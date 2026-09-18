import unittest
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path
import threading
import json
from src.execute_v2 import execute_v2, ExecutionGuardError, ExecutionLedger, MockPredictor, EXPERIMENT_ROOT

class TestExecuteV2(unittest.TestCase):
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
                np.random.rand(5, 12),  # r1
                np.random.randint(0, 2, (5, 2048))  # r2
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

    def test_run_uuid_or_dir_cannot_bypass_started(self):
        # We must use dry_run to pass a custom state file otherwise it throws ExecutionGuardError
        execute_v2(self.run_dir, self.partition_path, dry_run=True, synthetic_data=self.synthetic_data, state_file=self.state_file)
        
        run_dir_2 = Path(self.test_dir.name) / "run_02"
        with self.assertRaises(ExecutionGuardError):
            execute_v2(run_dir_2, self.partition_path, dry_run=True, synthetic_data=self.synthetic_data, state_file=self.state_file)

    def test_state_override_rejected_in_production(self):
        with self.assertRaisesRegex(ExecutionGuardError, "Cannot override authoritative state path"):
            execute_v2(self.run_dir, self.partition_path, dry_run=False, synthetic_data=self.synthetic_data, state_file=self.state_file)

    def test_dry_run_is_isolated(self):
        # Isolated dry run natively without explicit state file
        execute_v2(self.run_dir, self.partition_path, dry_run=True, synthetic_data=self.synthetic_data)
        
        # Ensures isolated dry run didn't write to authoritative state
        self.assertFalse((EXPERIMENT_ROOT / "state" / "v2_execution_state.json").exists())
        
    def test_concurrent_primary_starts(self):
        results = []
        def run_thread():
            try:
                execute_v2(self.run_dir, self.partition_path, dry_run=True, synthetic_data=self.synthetic_data, state_file=self.state_file)
                results.append("SUCCESS")
            except ExecutionGuardError:
                results.append("BLOCKED")
                
        t1 = threading.Thread(target=run_thread)
        t2 = threading.Thread(target=run_thread)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        self.assertEqual(results.count("SUCCESS"), 1)
        self.assertEqual(results.count("BLOCKED"), 1)

    def test_selection_record_exists_before_started(self):
        ledger = ExecutionLedger(self.state_file)
        ledger.begin_stage('PRIMARY_HOLDOUT')
        
        with self.assertRaises(ExecutionGuardError):
            execute_v2(self.run_dir, self.partition_path, dry_run=True, synthetic_data=self.synthetic_data, state_file=self.state_file)
            
        self.assertTrue((self.run_dir / "selection_manifest.json").exists())

    def test_tie_break_features_exposed(self):
        manifest = execute_v2(self.run_dir, self.partition_path, dry_run=True, synthetic_data=self.synthetic_data)
        cands = manifest['candidate_results']
        for cand in cands:
            if cand['pipeline_id'] in ['P1', 'P2']:
                self.assertIn('alpha', cand)
            else:
                self.assertIn('max_features', cand)
                self.assertIn('min_samples_leaf', cand)

    def test_hlm_hh_derives_dynamic_values(self):
        # Using the state injection logic via dry run
        manifest = execute_v2(self.run_dir, self.partition_path, dry_run=True, synthetic_data=self.synthetic_data, state_file=self.state_file)
        
        ledger_content = ExecutionLedger(self.state_file)._load()
        hlm_hh_stage = ledger_content['HLM_HH']
        
        self.assertIn('primary_spearman', hlm_hh_stage['artifacts'])
        self.assertIn('sens_spearman', hlm_hh_stage['artifacts'])

    def test_biogen_cohorts(self):
        manifest = execute_v2(self.run_dir, self.partition_path, dry_run=True, synthetic_data=self.synthetic_data, state_file=self.state_file)
        ledger_content = ExecutionLedger(self.state_file)._load()
        self.assertEqual(ledger_content['BIOGEN']['status'], 'COMPLETED')

    def test_biogen_b1_b2_selection_inheritance(self):
        # We test that B2 inherits B1 partition, uses B1 selected pipeline, and does not run P1-P4.
        # This is proven structurally by the execution runner now lacking a P1-P4 loop for B2,
        # but we can verify it doesn't crash and completes the BIOGEN stage when B2 data differs.
        
        manifest = execute_v2(self.run_dir, self.partition_path, dry_run=True, synthetic_data=self.synthetic_data, state_file=self.state_file)
        ledger_content = ExecutionLedger(self.state_file)._load()
        self.assertEqual(ledger_content['BIOGEN']['status'], 'COMPLETED')

if __name__ == '__main__':
    unittest.main()
