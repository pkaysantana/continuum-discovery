import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

import src.execute_v2 as execute_v2_module
from src.execute_v2 import ExecutionLedger, _select_representation, execute_v2
from src.pipelines import representation_for, tie_break_candidates


class RecordingEstimator:
    def __init__(self):
        self.fit_feature_counts = []

    def fit(self, X, y):
        self.fit_feature_counts.append(X.shape[1])
        return self

    def predict(self, X):
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

    def test_representation_for_maps_pipeline_ids_and_rejects_unknown_ids(self):
        self.assertEqual(representation_for('P1'), 'R1')
        self.assertEqual(representation_for('P2'), 'R2')
        self.assertEqual(representation_for('P3'), 'R1')
        self.assertEqual(representation_for('P4'), 'R2')
        for pipeline_id in ('p1', 'P5', ''):
            with self.subTest(pipeline_id=pipeline_id):
                with self.assertRaises(ValueError):
                    representation_for(pipeline_id)

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

    def test_select_representation_routes_expected_shapes_and_objects(self):
        X_r1 = np.zeros((3, 12))
        X_r2 = np.zeros((3, 2048))
        selected = {
            pipeline_id: _select_representation(pipeline_id, X_r1, X_r2)
            for pipeline_id in ('P1', 'P2', 'P3', 'P4')
        }

        self.assertEqual(selected['P1'].shape[1], 12)
        self.assertEqual(selected['P3'].shape[1], 12)
        self.assertEqual(selected['P2'].shape[1], 2048)
        self.assertEqual(selected['P4'].shape[1], 2048)
        self.assertIs(selected['P1'], X_r1)
        self.assertIs(selected['P2'], X_r2)
        self.assertIsNot(selected['P1'], selected['P2'])
        self.assertNotEqual(selected['P1'].shape, selected['P2'].shape)

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
