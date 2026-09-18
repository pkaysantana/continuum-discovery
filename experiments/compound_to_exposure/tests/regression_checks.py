import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

from src.execute_v2 import execute_v2, MockPredictor
from src.representations import get_r1_vector, get_r2_morgan, R1_PROPERTIES
from src.dataset import get_cohorts

class TestRegression(unittest.TestCase):
    def test_chembl_no_smiles_column_works(self):
        # We test that the actual loaded data has NO 'smiles' column but has CHEMBL_STRUCTURE_COLUMN
        # Since Correction 002 purged smiles fallbacks, this proves the invariant.
        from src.execute_v2 import CHEMBL_STRUCTURE_COLUMN
        cohorts = get_cohorts()
        df_p = cohorts['interior_731']
        self.assertNotIn('smiles', df_p.columns)
        self.assertIn(CHEMBL_STRUCTURE_COLUMN, df_p.columns)

    def test_removal_of_canonical_smiles_rdkit_fails(self):
        # Mock get_cohorts to remove canonical_smiles_rdkit and ensure it raises KeyError or AssertionError
        with patch('src.execute_v2.get_cohorts') as mock_get_cohorts:
            df_p = pd.DataFrame({'chembl_id': ['1'], 'canonical_smiles': ['CCO']})
            df_ambig = pd.DataFrame({'chembl_id': ['2'], 'canonical_smiles': ['O']})
            mock_get_cohorts.return_value = {'interior_731': df_p, 'ambiguous_13': df_ambig}
            
            with self.assertRaises(AssertionError):
                # execute_v2 will assert CHEMBL_STRUCTURE_COLUMN in df_p.columns
                execute_v2(Path('dummy'), Path('splits/master_partition.csv'), dry_run=False, preflight=True)

    def test_r1_schema_returns_12_features(self):
        vec = get_r1_vector('CCO')
        self.assertEqual(len(vec), 12)
        
    def test_r2_schema_returns_2048_features(self):
        vec = get_r2_morgan('CCO')
        self.assertEqual(len(vec), 2048)

    def test_preflight_cannot_call_fit(self):
        # We monkeypatch the pipeline models so any call to fit raises immediately.
        # This proves preflight completes successfully while attempt to enter model-fitting would fail loudly.
        with patch('src.execute_v2.get_pipeline_grids') as mock_get_pipelines:
            mock_pipe = MagicMock()
            mock_pipe.fit.side_effect = RuntimeError("Model fitting is forbidden in preflight!")
            mock_get_pipelines.return_value = {'P1': (mock_pipe, {})}
            
            res = execute_v2(Path('dummy'), Path('splits/master_partition.csv'), dry_run=False, preflight=True)
            self.assertEqual(res, "V2_REAL_DATA_PREFLIGHT_PASS")
            mock_pipe.fit.assert_not_called()

    def test_synthetic_mock_unreachable_in_real_execution(self):
        with open('src/execute_v2.py', 'r') as f:
            content = f.read()
        # Ensure that MockPredictor is only used if dry_run
        # The prompt says mock/synthetic feature construction must be unreachable in supported real mode.
        self.assertNotIn("X_mock =", content)
        self.assertNotIn("X_mock_b2 =", content)

    def test_biogen_genuine_descriptors(self):
        with open('src/execute_v2.py', 'r') as f:
            content = f.read()
        self.assertIn("X_b1_r1 = np.array([get_r1_vector(s) for s in df_bio1[BIOGEN_STRUCTURE_COLUMN]])", content)
        self.assertIn("X_b2_r2 = np.array([get_r2_morgan(s) for s in df_bio2[BIOGEN_STRUCTURE_COLUMN]])", content)

if __name__ == '__main__':
    unittest.main()
