import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

import src.execute_v2 as execute_v2_module
from src.execute_v2 import (
    ExecutionLedger,
    _biogen_b1_candidates,
    _biogen_b2_fit,
    _select_representation,
    execute_v2,
)
from src.pipelines import representation_for, tie_break_candidates
from src.representations import get_r1_vector, get_r2_morgan


class RecordingEstimator:
    def __init__(self):
        self.fit_feature_counts = []
        self.fit_row_counts = []
        self.predict_row_counts = []

    def fit(self, X, y):
        self.fit_feature_counts.append(X.shape[1])
        self.fit_row_counts.append(X.shape[0])
        return self

    def predict(self, X):
        self.predict_row_counts.append(X.shape[0])
        return np.zeros(len(X))


class TestFeatureRouting(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.test_dir.name) / "run_01"
        self.run_dir.mkdir(parents=True)
        self.state_file = Path(self.test_dir.name) / "state" / "v2_execution_state.json"

        self.partition_path = self.run_dir / "master_partition.csv"
        part_df = pd.DataFrame({
            'chembl_id': ['CHEMBL1', 'CHEMBL2', 'CHEMBL3', 'CHEMBL4', 'CHEMBL5', 'CHEMBL_AMB1'],
            'partition': ['cv', 'cv', 'cv', 'holdout', 'holdout', 'cv'],
            'cv_fold': [0, 1, 2, -1, -1, 0]
        })
        part_df.to_csv(self.partition_path, index=False)

        self.synthetic_data = {
            'cohorts': {
                'interior_731': pd.DataFrame({
                    'chembl_id': ['CHEMBL1', 'CHEMBL2', 'CHEMBL3', 'CHEMBL4', 'CHEMBL5'],
                    'smiles': ['C', 'CC', 'CCC', 'CCCC', 'CCCCC'],
                    'log10_CLint': [1.0, 2.0, 3.0, 4.0, 5.0]
                }),
                'ambiguous_13': pd.DataFrame({
                    'chembl_id': ['CHEMBL_AMB1'],
                    'smiles': ['O'],
                    'log10_CLint': [np.nan]
                }),
                'all_censored': pd.DataFrame({
                    'chembl_id': ['CHEMBL_TAIL1'],
                    'smiles': ['F'],
                    'log10_CLint': [np.nan],
                    'partition': ['cv'],
                    'cv_fold': [0],
                    'qualifier': ['<']
                })
            },
            'partition': part_df,
            'representations': (
                np.random.rand(5, 12),
                np.random.randint(0, 2, (5, 2048))
            ),
            'representations_ambig': (
                np.random.rand(1, 12),
                np.random.randint(0, 2, (1, 2048))
            ),
            'representations_tail': (
                np.random.rand(1, 12),
                np.random.randint(0, 2, (1, 2048))
            )
        }

    def tearDown(self):
        self.test_dir.cleanup()

    def test_representation_for_maps_pipeline_ids(self):
        expected = {'P1': 'R1', 'P2': 'R2', 'P3': 'R1', 'P4': 'R2'}
        for pipeline_id, representation in expected.items():
            with self.subTest(pipeline_id=pipeline_id):
                self.assertEqual(representation_for(pipeline_id), representation)

    def test_representation_and_selection_reject_unknown_and_case_variant_ids(self):
        X_r1 = np.ones((2, 12))
        X_r2 = np.full((2, 2048), 2)
        for pipeline_id in (
            'p1', 'p2', 'p3', 'p4', 'r1', 'R1', 'R2', ' P1', 'P1 ',
            'P0A', 'P5', '', None
        ):
            with self.subTest(pipeline_id=pipeline_id):
                with self.assertRaises(ValueError):
                    representation_for(pipeline_id)
                with self.assertRaises(ValueError):
                    _select_representation(pipeline_id, X_r1, X_r2)

    def test_tie_break_candidates_prefers_r1_within_family_in_either_order(self):
        candidate_pairs = (
            ('P1', 'P2', {'alpha': 1.0}),
            ('P3', 'P4', {'max_features': 'sqrt', 'min_samples_leaf': 1})
        )
        for r1_id, r2_id, params in candidate_pairs:
            candidate_r1 = {'pipeline_id': r1_id, 'mae': 1.0, **params}
            candidate_r2 = {'pipeline_id': r2_id, 'mae': 1.0005, **params}
            with self.subTest(r1_id=r1_id, r2_id=r2_id):
                self.assertTrue(tie_break_candidates(candidate_r1, candidate_r2))
                self.assertFalse(tie_break_candidates(candidate_r2, candidate_r1))

    def test_execute_v2_source_has_no_lowercase_substring_routing(self):
        source = Path(execute_v2_module.__file__).read_text()
        self.assertNotIn("'r1' in", source)

    def test_representation_for_and_selection_agree_on_real_feature_widths(self):
        X_r1 = np.ones((3, 12))
        X_r2 = np.full((3, 2048), 2)
        expected_width = {'R1': 12, 'R2': 2048}
        for pipeline_id in ('P1', 'P2', 'P3', 'P4'):
            with self.subTest(pipeline_id=pipeline_id):
                representation = representation_for(pipeline_id)
                selected = _select_representation(pipeline_id, X_r1, X_r2)
                expected_matrix = X_r1 if representation == 'R1' else X_r2
                self.assertEqual(selected.shape[1], expected_width[representation])
                self.assertIs(selected, expected_matrix)
                self.assertNotEqual(selected[0, 0], (X_r2 if representation == 'R1' else X_r1)[0, 0])

    def _synthetic_biogen_inputs(self):
        n = 12
        cv_mask = pd.Series([True] * 9 + [False] * 3)
        fold_assignments = pd.Series([0] * 3 + [1] * 3 + [2] * 3 + [-1] * 3)
        cv_folds = [0, 1, 2]
        X_r1 = np.arange(n * 12, dtype=float).reshape(n, 12)
        X_r2 = (np.arange(n * 2048).reshape(n, 2048) % 2).astype(np.int8)
        y = np.arange(1, n + 1, dtype=float)
        return X_r1, X_r2, y, cv_mask, fold_assignments, cv_folds

    def _recording_pipelines(self):
        estimators = {pipeline_id: RecordingEstimator() for pipeline_id in ('P1', 'P2', 'P3', 'P4')}
        pipelines = {pipeline_id: (estimator, {}) for pipeline_id, estimator in estimators.items()}
        return estimators, pipelines

    def test_biogen_b1_candidates_route_features_and_preserve_series_fold_masks(self):
        X_r1, X_r2, y, cv_mask, fold_assignments, cv_folds = self._synthetic_biogen_inputs()
        estimators, pipelines = self._recording_pipelines()

        candidates = _biogen_b1_candidates(
            pipelines, X_r1, X_r2, y, cv_mask, fold_assignments, cv_folds, False
        )

        self.assertEqual(len(candidates), 4)
        self.assertEqual({candidate['pipeline_id'] for candidate in candidates}, {'P1', 'P2', 'P3', 'P4'})
        for pipeline_id, estimator in estimators.items():
            with self.subTest(pipeline_id=pipeline_id):
                expected_width = 12 if pipeline_id in ('P1', 'P3') else 2048
                self.assertEqual(estimator.fit_feature_counts, [expected_width] * len(cv_folds))
                expected_row_counts = [
                    (
                        int((cv_mask & (fold_assignments != fold)).sum()),
                        int((cv_mask & (fold_assignments == fold)).sum())
                    )
                    for fold in cv_folds
                ]
                self.assertEqual(list(zip(estimator.fit_row_counts, estimator.predict_row_counts)), expected_row_counts)

    def test_biogen_b1_dry_run_uses_mock_predictor_without_fitting_recorders(self):
        X_r1, X_r2, y, cv_mask, fold_assignments, cv_folds = self._synthetic_biogen_inputs()
        estimators, pipelines = self._recording_pipelines()

        with patch.object(execute_v2_module, 'MockPredictor', wraps=execute_v2_module.MockPredictor) as mock_predictor:
            candidates = _biogen_b1_candidates(
                pipelines, X_r1, X_r2, y, cv_mask, fold_assignments, cv_folds, True
            )

        self.assertEqual(len(candidates), 4)
        self.assertEqual(mock_predictor.call_count, 4 * len(cv_folds))
        self.assertTrue(all(not estimator.fit_feature_counts for estimator in estimators.values()))

    def test_biogen_b2_fits_only_selected_pipeline_with_expected_width(self):
        X_r1, X_r2, y, cv_mask, fold_assignments, cv_folds = self._synthetic_biogen_inputs()
        for pipeline_id in ('P1', 'P2', 'P3', 'P4'):
            estimators, pipelines = self._recording_pipelines()
            with self.subTest(pipeline_id=pipeline_id):
                _biogen_b2_fit(
                    pipelines, pipeline_id, X_r1, X_r2, y, cv_mask,
                    fold_assignments, cv_folds, False
                )

                expected_width = 12 if pipeline_id in ('P1', 'P3') else 2048
                self.assertEqual(estimators[pipeline_id].fit_feature_counts, [expected_width] * len(cv_folds))
                self.assertTrue(all(
                    not estimator.fit_feature_counts
                    for other_id, estimator in estimators.items()
                    if other_id != pipeline_id
                ))

                expected_row_counts = [
                    (
                        int((cv_mask & (fold_assignments != fold)).sum()),
                        int((cv_mask & (fold_assignments == fold)).sum())
                    )
                    for fold in cv_folds
                ]
                self.assertEqual(
                    list(zip(estimators[pipeline_id].fit_row_counts, estimators[pipeline_id].predict_row_counts)),
                    expected_row_counts
                )

    def test_rdkit_r1_vectors_are_finite_12_descriptors_and_distinct(self):
        smiles = ('CCO', 'Oc1ccccc1', 'CC(=O)Oc1ccccc1C(=O)O', 'Cn1cnc2c1c(=O)n(C)c(=O)n2C')
        vectors = [np.asarray(get_r1_vector(value), dtype=float) for value in smiles]
        self.assertTrue(all(vector.shape == (12,) for vector in vectors))
        self.assertTrue(all(np.isfinite(vector).all() for vector in vectors))
        self.assertEqual(np.unique(np.stack(vectors), axis=0).shape, (4, 12))

    def test_rdkit_r2_vectors_are_binary_2048_bit_fingerprints_and_distinct(self):
        smiles = ('CCO', 'Oc1ccccc1', 'CC(=O)Oc1ccccc1C(=O)O', 'Cn1cnc2c1c(=O)n(C)c(=O)n2C')
        vectors = [np.asarray(get_r2_morgan(value)) for value in smiles]
        self.assertTrue(all(vector.shape == (2048,) for vector in vectors))
        self.assertTrue(all(np.isin(vector, (0, 1)).all() for vector in vectors))
        self.assertTrue(all(vector.any() for vector in vectors))
        self.assertEqual(np.unique(np.stack(vectors), axis=0).shape, (4, 2048))

    def test_rdkit_stacked_feature_matrices_have_expected_shapes_and_distinct_rows(self):
        smiles = ('CCO', 'Oc1ccccc1', 'CC(=O)Oc1ccccc1C(=O)O', 'Cn1cnc2c1c(=O)n(C)c(=O)n2C')
        X_r1 = np.asarray([get_r1_vector(value) for value in smiles], dtype=float)
        X_r2 = np.asarray([get_r2_morgan(value) for value in smiles])
        self.assertEqual(X_r1.shape, (4, 12))
        self.assertEqual(X_r2.shape, (4, 2048))
        self.assertEqual(np.unique(X_r1, axis=0).shape[0], 4)
        self.assertEqual(np.unique(X_r2, axis=0).shape[0], 4)

    def test_invalid_smiles_returns_nan_r1_and_none_r2(self):
        self.assertTrue(np.isnan(np.asarray(get_r1_vector('not_a_smiles'), dtype=float)).all())
        self.assertIsNone(get_r2_morgan('not_a_smiles'))

    def test_execute_v2_synthetic_fitting_routes_all_four_pipeline_estimators(self):
        estimators = {pipeline_id: RecordingEstimator() for pipeline_id in ('P1', 'P2', 'P3', 'P4')}
        pipeline_grids = {
            pipeline_id: (estimator, {})
            for pipeline_id, estimator in estimators.items()
        }
        original_ledger = ExecutionLedger

        def temporary_ledger(_state_path):
            return original_ledger(self.state_file)

        # dry_run=True uses MockPredictor rather than the configured estimators;
        # this synthetic-only run exercises the fitting loop with isolated ledger state.
        with patch.object(execute_v2_module, 'get_pipeline_grids', return_value=pipeline_grids), \
                patch.object(execute_v2_module, 'ExecutionLedger', side_effect=temporary_ledger):
            execute_v2(
                self.run_dir,
                self.partition_path,
                dry_run=False,
                synthetic_data=self.synthetic_data
            )

        self.assertTrue(estimators['P1'].fit_feature_counts)
        self.assertTrue(estimators['P2'].fit_feature_counts)
        self.assertTrue(estimators['P3'].fit_feature_counts)
        self.assertTrue(estimators['P4'].fit_feature_counts)
        self.assertTrue(all(count == 12 for count in estimators['P1'].fit_feature_counts))
        self.assertTrue(all(count == 2048 for count in estimators['P2'].fit_feature_counts))
        self.assertTrue(all(count == 12 for count in estimators['P3'].fit_feature_counts))
        self.assertTrue(all(count == 2048 for count in estimators['P4'].fit_feature_counts))


if __name__ == '__main__':
    unittest.main()
