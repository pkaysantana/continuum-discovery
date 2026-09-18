import unittest
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.execute_v2 import execute_v2, ExecutionLedger, MockPredictor, EXPERIMENT_ROOT

class TestPreflightAndValidation(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.test_dir.name) / "run_01"
        self.run_dir.mkdir(parents=True)
        self.state_file = Path(self.test_dir.name) / "state" / "v2_execution_state.json"
        self.partition_path = self.run_dir / "master_partition.csv"
        
        # We'll use the real master_partition.csv for the base valid case
        self.real_master_path = EXPERIMENT_ROOT / "splits" / "master_partition.csv"
        if self.real_master_path.exists():
            self.valid_df = pd.read_csv(self.real_master_path)
            self.valid_df.to_csv(self.partition_path, index=False)
        else:
            self.valid_df = pd.DataFrame()

    def tearDown(self):
        self.test_dir.cleanup()

    def test_preflight_valid_partition(self):
        if self.valid_df.empty:
            self.skipTest("Real master_partition.csv not available")
        
        # Preflight should pass
        res = execute_v2(self.run_dir, self.partition_path, dry_run=False, preflight=True)
        self.assertEqual(res, "V2_REAL_DATA_PREFLIGHT_PASS")
        
        # Verify no ledger was created/transitioned
        self.assertFalse(self.state_file.exists())
        
        # Verify no real prediction artifacts written
        self.assertFalse((self.run_dir / "primary_holdout_predictions.csv").exists())

    @patch('src.execute_v2._sha256')
    def test_preflight_invalid_primary_holdout_count(self, mock_sha):
        if self.valid_df.empty:
            self.skipTest("Real master_partition.csv not available")
        mock_sha.return_value = "971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a"
        
        from src.dataset import get_cohorts
        cohorts = get_cohorts()
        df_p = cohorts['interior_731']
        
        df = self.valid_df.copy()
        # Find a holdout that is in interior_731
        holdout_mask = (df['partition'] == 'holdout') & (df['chembl_id'].isin(df_p['chembl_id']))
        holdout_idx = df[holdout_mask].index[0]
        df.loc[holdout_idx, 'partition'] = 'cv'
        df.to_csv(self.partition_path, index=False)
        
        with self.assertRaises(AssertionError):
            execute_v2(self.run_dir, self.partition_path, dry_run=False, preflight=True)

    @patch('src.execute_v2._sha256')
    def test_preflight_invalid_primary_cv_count(self, mock_sha):
        if self.valid_df.empty:
            self.skipTest("Real master_partition.csv not available")
        mock_sha.return_value = "971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a"
        
        from src.dataset import get_cohorts
        cohorts = get_cohorts()
        df_p = cohorts['interior_731']
        
        df = self.valid_df.copy()
        cv_mask = (df['partition'] == 'cv') & (df['chembl_id'].isin(df_p['chembl_id']))
        cv_idx = df[cv_mask].index[0]
        df.loc[cv_idx, 'partition'] = 'holdout'
        df.to_csv(self.partition_path, index=False)
        
        with self.assertRaises(AssertionError):
            execute_v2(self.run_dir, self.partition_path, dry_run=False, preflight=True)

    @patch('src.execute_v2._sha256')
    def test_preflight_invalid_fold_count(self, mock_sha):
        if self.valid_df.empty:
            self.skipTest("Real master_partition.csv not available")
        mock_sha.return_value = "971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a"
        
        from src.dataset import get_cohorts
        cohorts = get_cohorts()
        df_p = cohorts['interior_731']
        
        df = self.valid_df.copy()
        mask0 = (df['cv_fold'] == 0.0) & (df['chembl_id'].isin(df_p['chembl_id']))
        cv_idx0 = df[mask0].index[0]
        df.loc[cv_idx0, 'cv_fold'] = 1.0 
        df.to_csv(self.partition_path, index=False)
        
        with self.assertRaises(AssertionError):
            execute_v2(self.run_dir, self.partition_path, dry_run=False, preflight=True)

    @patch('src.execute_v2._sha256')
    def test_preflight_duplicate_id(self, mock_sha):
        if self.valid_df.empty:
            self.skipTest("Real master_partition.csv not available")
        mock_sha.return_value = "971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a"
        
        df = self.valid_df.copy()
        df.iloc[0] = df.iloc[1] # create duplicate
        df.to_csv(self.partition_path, index=False)
        
        with self.assertRaises(AssertionError):
            execute_v2(self.run_dir, self.partition_path, dry_run=False, preflight=True)

    def test_preflight_hash_mismatch(self):
        if self.valid_df.empty:
            self.skipTest("Real master_partition.csv not available")
            
        df = self.valid_df.copy()
        # Modifying the file without patching sha256
        df.loc[0, 'chembl_id'] = 'CHEMBL_INVALID_DUMMY'
        df.to_csv(self.partition_path, index=False)
        
        with self.assertRaises(AssertionError):
            execute_v2(self.run_dir, self.partition_path, dry_run=False, preflight=True)

    @patch('src.execute_v2.get_pipeline_grids')
    def test_preflight_cannot_invoke_fit_predict(self, mock_pipelines):
        if self.valid_df.empty:
            self.skipTest("Real master_partition.csv not available")
            
        # If preflight accidentally continues, it would call fit or predict
        # Let's ensure pipelines aren't even used.
        mock_pipe = MagicMock()
        mock_pipelines.return_value = {'P1': (mock_pipe, {})}
        
        execute_v2(self.run_dir, self.partition_path, dry_run=False, preflight=True)
        
        mock_pipe.fit.assert_not_called()
        mock_pipe.predict.assert_not_called()

if __name__ == '__main__':
    unittest.main()
