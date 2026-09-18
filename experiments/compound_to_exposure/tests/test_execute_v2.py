import unittest
import tempfile
from pathlib import Path
import pandas as pd
import numpy as np

from src.execute_v2 import execute_v2, ExecutionGuardError

class TestExecuteV2(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.test_dir.name)
        
        # Synthetic master partition
        self.partition_path = self.run_dir / "master_partition.csv"
        part_df = pd.DataFrame({
            'chembl_id': ['CHEMBL1', 'CHEMBL2', 'CHEMBL3', 'CHEMBL4', 'CHEMBL5'],
            'partition': ['cv', 'cv', 'cv', 'holdout', 'holdout'],
            'cv_fold': [0, 1, 2, -1, -1]
        })
        part_df.to_csv(self.partition_path, index=False)
        
        self.synthetic_data = {
            'cohorts': {
                'interior_731': pd.DataFrame({
                    'chembl_id': ['CHEMBL1', 'CHEMBL2', 'CHEMBL3', 'CHEMBL4', 'CHEMBL5'],
                    'smiles': ['C', 'CC', 'CCC', 'CCCC', 'CCCCC'],
                    'log10_CLint': [1.0, 2.0, 3.0, 4.0, 5.0]
                })
            },
            'partition': part_df,
            'representations': (
                np.random.rand(5, 12),  # r1
                np.random.randint(0, 2, (5, 2048))  # r2
            )
        }

    def tearDown(self):
        self.test_dir.cleanup()

    def test_dry_run_completes_and_locks(self):
        # First run
        manifest = execute_v2(self.run_dir, self.partition_path, dry_run=True, synthetic_data=self.synthetic_data)
        self.assertTrue(manifest['holdout_accessed'])
        self.assertEqual(manifest['status'], 'V2_IMPLEMENTATION_READY_FOR_REVIEW')
        
        # Lock file should exist
        self.assertTrue((self.run_dir / ".holdout_lock").exists())
        
        # Predictions should be written
        preds = pd.read_csv(self.run_dir / "holdout_predictions.csv")
        self.assertEqual(len(preds), 2)
        
        # Attempt adaptive rerun, should fail
        with self.assertRaises(ExecutionGuardError):
            execute_v2(self.run_dir, self.partition_path, dry_run=True, synthetic_data=self.synthetic_data)

if __name__ == '__main__':
    unittest.main()
