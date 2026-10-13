"""Small synthetic correctness tests. Never load any project dataset."""
import copy
import unittest
from unittest.mock import patch

import numpy as np

from application_development.gsk_clearance import harness as h


def fixture():
    smiles = ["c1ccccc1", "Cc1ccccc1", "Oc1ccccc1",
              "c1ccncc1", "Cc1ccncc1", "Oc1ccncc1",
              "C1CCCCC1", "CC1CCCCC1", "OC1CCCCC1"]
    rows = [{"activity_id": f"SYN_ACT_{i}", "id": f"SYN_{i}", "smiles": s, "scaffold": h.scaffold_key(s),
             "fold": i//3, "partition": "cv", "relation": None,
             "clint": float(10+8*i)} for i, s in enumerate(smiles)]
    provenance = {"kind": "synthetic",
                  "id_scaffold_fold_sha256": h.digest({r["id"]: [r["scaffold"], r["fold"]] for r in rows}),
                  "records_sha256": h.digest(rows),
                  "assignments": {r["id"]: [r["scaffold"], r["fold"]] for r in rows},
                  "target": h.TARGET, "representation_policy": "V2_R1_12_R2_2048_NOCHIRAL"}
    return rows, provenance


class HarnessTests(unittest.TestCase):
    def test_dimensions_and_descriptor_names(self):
        rows, _ = fixture()
        x = h.feature_matrices(rows)
        self.assertEqual(x["R1"].shape, (9, 12))
        self.assertEqual(x["R2"].shape, (9, 2048))
        self.assertTrue(np.isin(x["R2"], [0, 1]).all())
        self.assertEqual(tuple(h.R1_PROPERTIES), (
            "MolWt", "MolLogP", "MolMR", "TPSA", "NumHDonors", "NumHAcceptors",
            "NumRotatableBonds", "RingCount", "NumAromaticRings", "NumAliphaticRings",
            "FractionCSP3", "HeavyAtomCount"))

    def test_historical_p3_adversarial_route_is_rejected(self):
        historical_route = "R1" if "r1" in "P3" else "R2"
        self.assertEqual(historical_route, "R2")
        with self.assertRaisesRegex(ValueError, "mapping"):
            h.model_spec("descriptor_rf", historical_route, h.Configuration())
        with patch.dict(h.REPRESENTATIONS, {"descriptor_rf": "R2"}):
            with self.assertRaisesRegex(ValueError, "mapping"):
                h.model_spec("descriptor_rf", "R2", h.Configuration())

    def test_all_pipelines_receive_exact_intended_fold_matrix(self):
        rows, provenance = fixture()
        matrices = h.feature_matrices(rows)
        original = h.model_spec
        seen = []

        def spy(name, representation, config):
            model = original(name, representation, config)
            original_fit = model.fit

            def fit(x, y):
                fold = len(seen)//4
                expected_rep = "R1" if name.startswith("descriptor_") else "R2"
                mask = np.array([r["fold"] != fold for r in rows])
                np.testing.assert_array_equal(x, matrices[expected_rep][mask])
                seen.append((name, fold))
                return original_fit(x, y)

            model.fit = fit
            return model

        with patch.object(h, "model_spec", side_effect=spy):
            result = h.evaluate(rows, provenance, h.Configuration(trees=2))
        self.assertEqual(len(seen), 12)
        self.assertEqual(len(result["predictions"]), 6)

    def test_parameters_applied_and_reported_from_fitted_estimators(self):
        rows, provenance = fixture()
        config = h.Configuration(trees=3, ridge_alpha=7.0, max_features=0.3,
                                 min_samples_leaf=2, max_depth=2, seed=19)
        result = h.evaluate(rows, provenance, config)
        for record in result["fitted_configurations"]:
            p = record["estimator_params"]
            if record["pipeline"].endswith("ridge"):
                self.assertEqual(p["alpha"], 7.0)
            else:
                self.assertEqual([p[k] for k in ["n_estimators", "max_features",
                                  "min_samples_leaf", "max_depth", "random_state", "n_jobs"]],
                                 [3, 0.3, 2, 2, 19, 1])
        self.assertEqual(result["data_provenance"], provenance)
        self.assertIn("scikit-learn", result["runtime"])

    def test_scaffolds_disjoint_and_cross_fold_mutation_rejected(self):
        rows, p = fixture()
        h.validate_bundle(rows, p)
        for fold in range(3):
            train = {r["scaffold"] for r in rows if r["fold"] != fold}
            valid = {r["scaffold"] for r in rows if r["fold"] == fold}
            self.assertFalse(train & valid)
        rows[0]["fold"] = 1
        p["assignments"][rows[0]["id"]][1] = 1
        p["records_sha256"] = h.digest(rows)
        with self.assertRaisesRegex(ValueError, "leakage"):
            h.validate_bundle(rows, p)

    def test_imputer_and_scaler_use_training_only(self):
        model = h.model_spec("descriptor_ridge", "R1", h.Configuration())
        train = np.tile(np.array([1., 3., np.nan, 5.])[:, None], (1, 12))
        model.fit(train, [0., 1., 2., 3.])
        np.testing.assert_allclose(model.named_steps["impute"].statistics_, 3.)
        np.testing.assert_allclose(model.named_steps["scale"].mean_, 3.)
        before = model.named_steps["scale"].mean_.copy()
        model.predict(np.full((2, 12), 1e6))
        np.testing.assert_array_equal(model.named_steps["scale"].mean_, before)
        raw_rf = h.model_spec("descriptor_rf", "R1", h.Configuration(trees=2))
        self.assertEqual(list(raw_rf.named_steps), ["impute", "estimator"])
        for name in ("morgan_rf", "morgan_ridge"):
            self.assertEqual(list(h.model_spec(name, "R2", h.Configuration()).named_steps), ["estimator"])

    def test_baselines_and_predictions_exclude_validation_outcomes(self):
        rows, p = fixture()
        config = h.Configuration(trees=2)
        result = h.evaluate(rows, p, config)
        y = h.transform_target([r["clint"] for r in rows])
        for fold in range(3):
            train = np.array([r["fold"] != fold for r in rows])
            for name, value in [("mean_baseline", np.mean(y[train])),
                                ("median_baseline", np.median(y[train]))]:
                np.testing.assert_allclose(np.array(result["predictions"][name])[~train], value)
        changed = copy.deepcopy(rows)
        for r in changed[:3]:
            r["clint"] = 149.0
        p2 = copy.deepcopy(p)
        p2["records_sha256"] = h.digest(changed)
        again = h.evaluate(changed, p2, config)
        for name in result["predictions"]:
            np.testing.assert_array_equal(result["predictions"][name][:3], again["predictions"][name][:3])

    def test_metrics_and_transform(self):
        np.testing.assert_allclose(h.transform_target([1., 10., 100.]), [0., 1., 2.])
        m = h.metrics([0., 1., 2.], [0., 2., 4.])
        self.assertAlmostEqual(m["mae_log10"], 1.)
        self.assertAlmostEqual(m["rmse_log10"], np.sqrt(5/3))
        self.assertAlmostEqual(m["pearson_r"], 1.)
        self.assertAlmostEqual(m["spearman_rho"], 1.)
        self.assertAlmostEqual(m["r_squared"], -1.5)
        self.assertIsNone(h.metrics([1., 2., 3.], [2., 2., 2.])["pearson_r"])
        self.assertIsNone(h.metrics([1., 1., 1.], [1., 2., 3.])["r_squared"])
        self.assertAlmostEqual(h.metrics([1., 1., 2., 3.], [2., 2., 1., 0.])["spearman_rho"], -1.)
        for values in ([0., 1.], [np.nan, 1.], [-1., 1.]):
            with self.assertRaises(ValueError):
                h.transform_target(values)

    def test_provenance_and_holdout_fail_closed(self):
        rows, p = fixture()
        for field in p:
            broken = {k: v for k, v in p.items() if k != field}
            with self.assertRaises(ValueError):
                h.validate_bundle(rows, broken)
        altered = copy.deepcopy(rows)
        altered[0]["clint"] += 1
        with self.assertRaisesRegex(ValueError, "provenance"):
            h.validate_bundle(altered, p)
        altered = copy.deepcopy(rows)
        altered[0]["partition"] = "holdout"
        p2 = {**p, "records_sha256": h.digest(altered)}
        with self.assertRaisesRegex(ValueError, "development CV"):
            h.validate_bundle(altered, p2)
        with patch.object(h, "feature_matrices", side_effect=AssertionError("must not featurize")):
            with self.assertRaises(PermissionError):
                h.evaluate(rows, {**p, "kind": "development"})

    def test_unknown_model_budget_and_missing_descriptor_fail(self):
        with self.assertRaises(ValueError):
            h.model_spec("P3", "R1", h.Configuration())
        with self.assertRaises(ValueError):
            h.Configuration(trees=101).validate()
        rows, p = fixture()
        x = h.feature_matrices(rows)
        x["R1"][:, 0] = np.nan
        with patch.object(h, "feature_matrices", return_value=x):
            with self.assertRaisesRegex(ValueError, "entirely missing"):
                h.evaluate(rows, p)

    def test_repeatability(self):
        rows, p = fixture()
        config = h.Configuration(trees=2)
        self.assertEqual(h.evaluate(rows, p, config), h.evaluate(rows, p, config))


if __name__ == "__main__":
    unittest.main()
