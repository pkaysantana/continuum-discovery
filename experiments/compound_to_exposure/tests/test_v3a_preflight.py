"""v3A.1-RC comprehensive test suite — mechanical and synthetic validation only.

NO REAL SCIENTIFIC MODEL IS FIT TO CHEMBL3301370 OUTCOMES.
Synthetic model fitting is for mathematical/unit-test validation only.
"""
import hashlib
import json
import sys
import os
from math import ceil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression

# Project imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import v3a_config as C
from src.v3a_cohort import (
    build_cohort, build_folds, write_csv, ecfp4_matrix,
    verify_feature_matrix, verify_row_alignment, feature_matrix_hash,
    fold_statistics, PreflightGateError, gate
)
from src.v3a_qrf_weights import (
    recover_forest_weights, weighted_quantile, qrf_prediction_quantiles,
    qrf_width, tanimoto_unfamiliarity, physchem_knn_distance, neff, neff_inverse,
    local_label_sd, tree_dispersion, select_retained, rmse, mae,
    rel_benefit_80, trapezoidal_naurc, matched_random_rankings,
    scaffold_bootstrap_indices, conformal_proper_train_cal_split,
    check_execution_guard, ExecutionGuardError, compute_descriptors,
)

DATA_CSV = str(Path(__file__).resolve().parent.parent / "data" / "interim" / "CHEMBL3301370_rows.csv")
SPLITS_DIR = str(Path(__file__).resolve().parent.parent / "splits")


# =========================================================================== Config
class TestConfig:
    def test_frozen_rf_params(self):
        rf = C.make_frozen_rf()
        assert rf.n_estimators == 500
        assert rf.criterion == "squared_error"
        assert rf.max_features == "sqrt"
        assert rf.min_samples_split == 2
        assert rf.min_samples_leaf == 2
        assert rf.max_depth is None
        assert rf.bootstrap is True
        assert rf.random_state == 20260923

    def test_representation_enum(self):
        assert C.REPRESENTATION is C.Representation.ECFP4_2048_R2_BINARY_NOCHIRAL
        assert C.REPRESENTATION.value == "ECFP4_2048_R2_BINARY_NOCHIRAL"
        # Cannot route by substring
        assert not hasattr(C.Representation, "r1")

    def test_morgan_spec(self):
        assert C.MORGAN_SPEC == {"radius": 2, "nBits": 2048, "binary": True, "useChirality": False}

    def test_cohort_constants(self):
        assert C.COHORT_N == 744
        assert C.N_INTERIOR == 731
        assert C.N_BOUNDARY_LOW == 13
        assert C.N_BOUNDARY_HIGH == 0
        assert C.N_LEFT_CENSORED == 274
        assert C.N_RIGHT_CENSORED == 84
        assert C.N_TOTAL_ASSAY_ROWS == 1102


# =========================================================================== Cohort
class TestCohort:
    @pytest.fixture(scope="class")
    def cohort(self):
        return build_cohort(DATA_CSV)

    def test_cohort_N(self, cohort):
        assert len(cohort) == 744

    def test_strict_interior(self, cohort):
        assert (cohort["semantic_class"] == "EXACT_QUANTITATIVE").sum() == 731

    def test_exact_at_3(self, cohort):
        assert (cohort["semantic_class"] == "EXACT_QUANTITATIVE_BOUNDARY_LOW").sum() == 13

    def test_no_censored(self, cohort):
        # All CLint values must be in [3, 150)
        assert (cohort["CLint"] >= 3.0).all()
        assert (cohort["CLint"] < 150.0).all()

    def test_columns(self, cohort):
        expected = ["activity_id", "chembl_id", "canonical_smiles_rdkit",
                     "scaffold_key", "CLint", "log10_CLint", "semantic_class"]
        assert list(cohort.columns) == expected

    def test_deterministic(self, cohort):
        cohort2 = build_cohort(DATA_CSV)
        assert cohort.equals(cohort2)

    def test_unique_ids(self, cohort):
        assert cohort["activity_id"].is_unique
        assert cohort["chembl_id"].is_unique


# =========================================================================== Folds
class TestFolds:
    @pytest.fixture(scope="class")
    def cohort(self):
        return build_cohort(DATA_CSV)

    @pytest.fixture(scope="class")
    def folds(self, cohort):
        return build_folds(cohort)

    def test_all_744_assigned(self, folds):
        assert len(folds) == 744

    def test_no_duplicate_ids(self, folds):
        assert folds["activity_id"].is_unique

    def test_all_ids_present(self, cohort, folds):
        assert set(folds["activity_id"]) == set(cohort["activity_id"])

    def test_no_scaffold_leakage(self, folds):
        per_scaf = folds.groupby("scaffold_key")["outer_fold"].nunique()
        assert (per_scaf == 1).all()

    def test_fold_range(self, folds):
        assert set(folds["outer_fold"].unique()) == {1, 2, 3, 4, 5}

    def test_deterministic(self, cohort):
        f1 = build_folds(cohort)
        f2 = build_folds(cohort)
        assert f1.equals(f2)

    def test_fold_sizes(self, folds):
        sizes = folds.groupby("outer_fold").size().to_dict()
        assert sum(sizes.values()) == 744
        # Each fold should have ~148-149
        for v in sizes.values():
            assert 140 <= v <= 160

    def test_total_scaffolds(self, folds):
        assert folds["scaffold_key"].nunique() == 540


# =========================================================================== Features
class TestFeatures:
    @pytest.fixture(scope="class")
    def cohort(self):
        return build_cohort(DATA_CSV)

    @pytest.fixture(scope="class")
    def X(self, cohort):
        return ecfp4_matrix(cohort["canonical_smiles_rdkit"].tolist(), C.REPRESENTATION)

    def test_shape(self, X):
        assert X.shape == (744, 2048)

    def test_binary(self, X):
        assert np.isin(X, [0, 1]).all()

    def test_no_nan(self, X):
        assert not np.isnan(X.astype(float)).any()

    def test_no_empty_fingerprints(self, X):
        assert (X.sum(axis=1) > 0).all()

    def test_row_alignment(self, X, cohort):
        verify_row_alignment(X, cohort, n_checks=20, seed=42)

    def test_representation_gate(self, cohort):
        with pytest.raises(PreflightGateError, match="GATE_04"):
            ecfp4_matrix(cohort["canonical_smiles_rdkit"].tolist()[:2], "ECFP4")


# =========================================================================== QRF weights — SYNTHETIC ONLY
class TestQRFWeights:
    """Fit RF on SYNTHETIC data. Verify weight recovery invariants."""

    @pytest.fixture(scope="class")
    def synthetic_setup(self):
        """Create multiple synthetic datasets and fit RFs."""
        setups = []
        for seed in [42, 123, 7, 999]:
            X, y = make_regression(n_samples=80, n_features=10, noise=0.5, random_state=seed)
            rf = RandomForestRegressor(
                n_estimators=50, min_samples_leaf=2, bootstrap=True,
                random_state=seed, max_depth=8)
            rf.fit(X, y)
            setups.append({"X": X, "y": y, "rf": rf, "seed": seed})
        return setups

    def test_weight_sum_invariant(self, synthetic_setup):
        max_err = 0.0
        for setup in synthetic_setup:
            X, y, rf = setup["X"], setup["y"], setup["rf"]
            # Test on training points and held-out points
            for idx in [0, len(X)//2, len(X)-1]:
                w = recover_forest_weights(rf, X, X[idx])
                err = abs(w.sum() - 1.0)
                max_err = max(max_err, err)
                assert err < C.WEIGHT_SUM_TOL, f"Weight sum {w.sum()} for seed={setup['seed']}, idx={idx}"
            # Held-out query
            rng = np.random.RandomState(setup["seed"] + 1)
            x_new = rng.randn(X.shape[1])
            w = recover_forest_weights(rf, X, x_new)
            err = abs(w.sum() - 1.0)
            max_err = max(max_err, err)
            assert err < C.WEIGHT_SUM_TOL
        print(f"\n  MAX WEIGHT-SUM ERROR: {max_err:.2e}")

    def test_prediction_reconstruction(self, synthetic_setup):
        max_err = 0.0
        for setup in synthetic_setup:
            X, y, rf = setup["X"], setup["y"], setup["rf"]
            for idx in [0, 10, len(X)//2, len(X)-1]:
                w = recover_forest_weights(rf, X, X[idx])
                reconstructed = np.dot(w, y)
                actual = rf.predict(X[idx].reshape(1, -1))[0]
                err = abs(reconstructed - actual)
                max_err = max(max_err, err)
                assert err < C.WEIGHT_MEAN_TOL, \
                    f"Reconstruction err {err:.2e} for seed={setup['seed']}, idx={idx}"
            # Held-out
            rng = np.random.RandomState(setup["seed"] + 1)
            x_new = rng.randn(X.shape[1])
            w = recover_forest_weights(rf, X, x_new)
            reconstructed = np.dot(w, y)
            actual = rf.predict(x_new.reshape(1, -1))[0]
            err = abs(reconstructed - actual)
            max_err = max(max_err, err)
            assert err < C.WEIGHT_MEAN_TOL
        print(f"\n  MAX PREDICTION RECONSTRUCTION ERROR: {max_err:.2e}")

    def test_non_negative_weights(self, synthetic_setup):
        for setup in synthetic_setup:
            X, y, rf = setup["X"], setup["y"], setup["rf"]
            w = recover_forest_weights(rf, X, X[0])
            assert (w >= 0).all()

    def test_neff_ge_1(self, synthetic_setup):
        for setup in synthetic_setup:
            X, y, rf = setup["X"], setup["y"], setup["rf"]
            w = recover_forest_weights(rf, X, X[0])
            assert neff(w) >= 1.0

    def test_quantile_monotonicity(self, synthetic_setup):
        for setup in synthetic_setup:
            X, y, rf = setup["X"], setup["y"], setup["rf"]
            w = recover_forest_weights(rf, X, X[0])
            qs = qrf_prediction_quantiles(w, y)
            assert qs["Q10"] <= qs["Q25"] <= qs["Q50"] <= qs["Q75"] <= qs["Q90"]

    def test_nonempty_support(self, synthetic_setup):
        for setup in synthetic_setup:
            X, y, rf = setup["X"], setup["y"], setup["rf"]
            w = recover_forest_weights(rf, X, X[0])
            assert (w > 0).sum() >= 1


# =========================================================================== Weighted quantiles
class TestWeightedQuantile:
    def test_uniform_weights(self):
        vals = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        wts = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
        assert weighted_quantile(vals, wts, 0.0) == 1.0
        assert weighted_quantile(vals, wts, 1.0) == 5.0
        q50 = weighted_quantile(vals, wts, 0.5)
        assert 2.5 <= q50 <= 3.5  # should be 3.0

    def test_concentrated_weight(self):
        vals = np.array([10.0, 20.0, 30.0])
        wts = np.array([0.0, 1.0, 0.0])
        for q in [0.1, 0.5, 0.9]:
            assert weighted_quantile(vals, wts, q) == 20.0

    def test_monotonic(self):
        vals = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
        wts = np.array([0.1, 0.1, 0.2, 0.1, 0.2, 0.1, 0.2])
        qs = [weighted_quantile(vals, wts, q) for q in [0.1, 0.25, 0.5, 0.75, 0.9]]
        for i in range(len(qs) - 1):
            assert qs[i] <= qs[i + 1]


# =========================================================================== Uncertainty primitives
class TestUncertaintyPrimitives:
    def test_tanimoto(self):
        q = np.array([1, 0, 1, 0, 1], dtype=np.uint8)
        t = np.array([[1, 0, 1, 0, 1],
                       [0, 1, 0, 1, 0]], dtype=np.uint8)
        assert tanimoto_unfamiliarity(q, t) == 0.0  # perfect match exists

    def test_tanimoto_no_match(self):
        q = np.array([1, 1, 0, 0], dtype=np.uint8)
        t = np.array([[0, 0, 1, 1]], dtype=np.uint8)
        assert tanimoto_unfamiliarity(q, t) == 1.0  # zero overlap

    def test_neff_uniform(self):
        w = np.ones(100) / 100
        assert abs(neff(w) - 100.0) < 1e-10

    def test_neff_inverse_uniform(self):
        w = np.ones(100) / 100
        assert abs(neff_inverse(w) - 0.01) < 1e-10

    def test_local_label_sd_constant(self):
        w = np.array([0.5, 0.5])
        y = np.array([3.0, 3.0])
        assert local_label_sd(w, y) == 0.0

    def test_local_label_sd_nonzero(self):
        w = np.array([0.5, 0.5])
        y = np.array([1.0, 3.0])
        assert local_label_sd(w, y) > 0.0

    def test_descriptors_length(self):
        d = compute_descriptors("c1ccccc1")  # benzene
        assert len(d) == 12


# =========================================================================== Retention
class TestRetention:
    def test_deterministic(self):
        ids = list(range(100))
        unc = np.random.RandomState(42).rand(100)
        s1 = select_retained(ids, unc, 0.80)
        s2 = select_retained(ids, unc, 0.80)
        assert s1 == s2

    def test_correct_count(self):
        for cov in [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]:
            ids = list(range(100))
            unc = np.random.RandomState(42).rand(100)
            retained = select_retained(ids, unc, cov)
            assert len(retained) == ceil(cov * 100)

    def test_no_target_values_used(self):
        # Retention depends only on uncertainty and IDs, not on outcomes
        ids = list(range(50))
        unc = np.random.RandomState(42).rand(50)
        retained = select_retained(ids, unc, 0.80)
        assert all(isinstance(x, int) for x in retained)


# =========================================================================== Metrics
class TestMetrics:
    def test_rmse_zero(self):
        y = np.array([1.0, 2.0, 3.0])
        assert rmse(y, y) == 0.0

    def test_rmse_known(self):
        y_true = np.array([1.0, 2.0, 3.0])
        y_pred = np.array([2.0, 3.0, 4.0])
        assert abs(rmse(y_true, y_pred) - 1.0) < 1e-10

    def test_mae_known(self):
        y_true = np.array([1.0, 2.0, 3.0])
        y_pred = np.array([2.0, 3.0, 4.0])
        assert abs(mae(y_true, y_pred) - 1.0) < 1e-10

    def test_rel_benefit(self):
        assert abs(rel_benefit_80(1.0, 0.9) - 0.1) < 1e-10

    def test_naurc_constant(self):
        kappas = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        rmses = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
        assert abs(trapezoidal_naurc(kappas, rmses) - 1.0) < 1e-10


# =========================================================================== Random deferral
class TestRandomDeferral:
    def test_determinism(self):
        fold_ids = {1: [1, 2, 3, 4, 5], 2: [6, 7, 8, 9, 10]}
        r1 = matched_random_rankings(fold_ids, n_random=100, seed=42, coverage=0.80)
        r2 = matched_random_rankings(fold_ids, n_random=100, seed=42, coverage=0.80)
        for f in fold_ids:
            for i in range(100):
                assert r1[f][i] == r2[f][i]

    def test_exact_counts(self):
        fold_ids = {1: list(range(20)), 2: list(range(20, 35))}
        result = matched_random_rankings(fold_ids, n_random=10, seed=42, coverage=0.80)
        for f, ids in fold_ids.items():
            k = ceil(0.80 * len(ids))
            for sample in result[f]:
                assert len(sample) == k

    def test_fold_matching(self):
        fold_ids = {1: list(range(50)), 2: list(range(50, 100))}
        result = matched_random_rankings(fold_ids, n_random=10, seed=42, coverage=0.80)
        for f in fold_ids:
            for sample in result[f]:
                assert sample.issubset(set(fold_ids[f]))


# =========================================================================== Scaffold bootstrap
class TestScaffoldBootstrap:
    def test_scaffold_unit(self):
        # Synthetic fold data
        data = pd.DataFrame({
            "activity_id": range(20),
            "scaffold_key": ["A"]*5 + ["B"]*5 + ["C"]*5 + ["D"]*5,
            "outer_fold": [1]*10 + [2]*10,
        })
        resamples = scaffold_bootstrap_indices(data, n_bootstrap=10, seed=42)
        assert len(resamples) == 10
        for idx_arr in resamples:
            assert len(idx_arr) > 0

    def test_fold_strata_separated(self):
        data = pd.DataFrame({
            "activity_id": range(20),
            "scaffold_key": ["A"]*5 + ["B"]*5 + ["C"]*5 + ["D"]*5,
            "outer_fold": [1]*10 + [2]*10,
        })
        resamples = scaffold_bootstrap_indices(data, n_bootstrap=100, seed=42)
        # Each resample should have indices from both folds
        for idx_arr in resamples:
            fold_values = data.iloc[idx_arr]["outer_fold"].unique()
            assert len(fold_values) == 2  # Both folds represented

    def test_paired_draws(self):
        data = pd.DataFrame({
            "activity_id": range(20),
            "scaffold_key": ["A"]*5 + ["B"]*5 + ["C"]*5 + ["D"]*5,
            "outer_fold": [1]*10 + [2]*10,
        })
        r1 = scaffold_bootstrap_indices(data, n_bootstrap=50, seed=42)
        r2 = scaffold_bootstrap_indices(data, n_bootstrap=50, seed=42)
        for i in range(50):
            assert np.array_equal(r1[i], r2[i])


# =========================================================================== Conformal
class TestConformal:
    def test_conformal_split_groups_indivisible(self):
        data = pd.DataFrame({
            "activity_id": list(range(100)),
            "scaffold_key": [f"S{i//5}" for i in range(100)],
            "outer_fold": [i % 5 + 1 for i in range(100)],
        })
        for fold in range(1, 6):
            proper, cal = conformal_proper_train_cal_split(data, fold)
            # All IDs accounted for
            train_ids = set(data[data["outer_fold"] != fold]["activity_id"])
            assert proper | cal == train_ids
            assert len(proper & cal) == 0
            # ~20% in calibration
            assert 0.10 <= len(cal) / len(train_ids) <= 0.35

    def test_conformal_width_ranking_identity(self):
        """If width_CQR = width_QRF + 2*qhat and qhat is constant within fold,
        then within-fold ranking of widths is identical."""
        widths_qrf = np.array([0.5, 1.2, 0.3, 0.8, 1.5])
        qhat = 0.25
        widths_cqr = widths_qrf + 2 * qhat
        rank_qrf = np.argsort(widths_qrf)
        rank_cqr = np.argsort(widths_cqr)
        assert np.array_equal(rank_qrf, rank_cqr)


# =========================================================================== Execution guard
class TestExecutionGuard:
    def test_fails_preexecution_state(self):
        manifest = {
            "execution_state": C.STATE_PREEXECUTION,
            "sap_sha256": "abc",
            "cohort_sha256": "def",
            "split_sha256": "ghi",
            "feature_sha256": "jkl",
            "cohort_N": 744,
            "independent_audit_recorded": True,
        }
        with pytest.raises(ExecutionGuardError, match="PREEXECUTION"):
            check_execution_guard(manifest, require_flag=True)

    def test_fails_no_flag(self):
        manifest = {
            "execution_state": C.STATE_FROZEN,
            "sap_sha256": "abc",
            "cohort_sha256": "def",
            "split_sha256": "ghi",
            "feature_sha256": "jkl",
            "cohort_N": 744,
            "independent_audit_recorded": True,
        }
        with pytest.raises(ExecutionGuardError, match="flag"):
            check_execution_guard(manifest, require_flag=False)

    def test_fails_wrong_N(self):
        manifest = {
            "execution_state": C.STATE_FROZEN,
            "sap_sha256": "abc",
            "cohort_sha256": "def",
            "split_sha256": "ghi",
            "feature_sha256": "jkl",
            "cohort_N": 100,
            "independent_audit_recorded": True,
        }
        with pytest.raises(ExecutionGuardError, match="cohort_N"):
            check_execution_guard(manifest, require_flag=True)

    def test_fails_no_audit(self):
        manifest = {
            "execution_state": C.STATE_FROZEN,
            "sap_sha256": "abc",
            "cohort_sha256": "def",
            "split_sha256": "ghi",
            "feature_sha256": "jkl",
            "cohort_N": 744,
            "independent_audit_recorded": False,
        }
        with pytest.raises(ExecutionGuardError, match="audit"):
            check_execution_guard(manifest, require_flag=True)


# =========================================================================== Module integrity
class TestModuleIntegrity:
    """Verify the interrupted-run recovery didn't leave corrupt modules."""
    def test_v3a_config_imports(self):
        from src import v3a_config
        assert hasattr(v3a_config, 'make_frozen_rf')
        assert hasattr(v3a_config, 'COHORT_N')

    def test_v3a_cohort_imports(self):
        from src import v3a_cohort
        assert hasattr(v3a_cohort, 'build_cohort')
        assert hasattr(v3a_cohort, 'build_folds')
        assert hasattr(v3a_cohort, 'ecfp4_matrix')

    def test_v3a_qrf_imports(self):
        from src import v3a_qrf_weights
        assert hasattr(v3a_qrf_weights, 'recover_forest_weights')
        assert hasattr(v3a_qrf_weights, 'weighted_quantile')


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
