import unittest
import numpy as np
from src.metrics import (
    log10_mae, log10_rmse, spearman_corr, r_squared,
    two_fold_proportion, tail_concordance, boundary_violation_loss
)
from src.pipelines import get_pipeline_grids, tie_break_candidates
from src.dataset import get_cohorts
from src.representations import get_r1_descriptors, R1_PROPERTIES
from src.biogen import load_biogen_data

class TestV2Implementation(unittest.TestCase):
    
    def test_metrics(self):
        y_t = [1.0, 2.0, 3.0]
        y_p = [1.1, 2.1, 3.1]
        
        # log10_mae = 0.1
        self.assertAlmostEqual(log10_mae(y_t, y_p), 0.1)
        
        # RMSE
        self.assertAlmostEqual(log10_rmse(y_t, y_p), 0.1)
        
        # Spearman (perfect correlation)
        self.assertAlmostEqual(spearman_corr(y_t, y_p), 1.0)
        
        # two fold (log10(2) ~ 0.301, all diffs are 0.1, so 1.0 proportion)
        self.assertEqual(two_fold_proportion(y_t, y_p), 1.0)
        
    def test_tail_concordance(self):
        # lower tail
        p_tail_lower = [0.5, 1.5]
        p_q = [1.0, 2.0, 3.0]
        
        # pairs: (0.5,1)->1, (0.5,2)->1, (0.5,3)->1
        # (1.5,1)->0, (1.5,2)->1, (1.5,3)->1
        # total 6 pairs. sum = 3 + 2 = 5.
        score, pairs = tail_concordance(p_tail_lower, p_q, 'lower')
        self.assertEqual(pairs, 6)
        self.assertAlmostEqual(score, 5/6)
        
    def test_tie_breaking(self):
        # 1. MAE diff > 0.001
        c1 = {'pipeline_id': 'P1', 'mae': 0.500, 'alpha': 1.0}
        c2 = {'pipeline_id': 'P2', 'mae': 0.510, 'alpha': 1.0}
        self.assertTrue(tie_break_candidates(c1, c2))
        
        # 2. MAE tie -> simpler (Ridge P1 over RF P3)
        c3 = {'pipeline_id': 'P1', 'mae': 0.500, 'alpha': 1.0}
        c4 = {'pipeline_id': 'P3', 'mae': 0.500, 'min_samples_leaf': 1, 'max_features': 1.0}
        self.assertTrue(tie_break_candidates(c3, c4))
        
        # 3. Same family -> R1 (P1) over R2 (P2)
        c5 = {'pipeline_id': 'P1', 'mae': 0.500, 'alpha': 1.0}
        c6 = {'pipeline_id': 'P2', 'mae': 0.500, 'alpha': 1.0}
        self.assertTrue(tie_break_candidates(c5, c6))
        
        # 4. Same family, same rep -> more regularised (alpha)
        c7 = {'pipeline_id': 'P1', 'mae': 0.500, 'alpha': 10.0}
        c8 = {'pipeline_id': 'P1', 'mae': 0.500, 'alpha': 1.0}
        self.assertTrue(tie_break_candidates(c7, c8))

    def test_cohorts_counts(self):
        # Ensure that running data loader fails or succeeds exactly matching SAP counts
        cohorts = get_cohorts()
        self.assertEqual(len(cohorts['interior_731']), 731)
        self.assertEqual(len(cohorts['below_274']), 274)
        self.assertEqual(len(cohorts['above_84']), 84)
        self.assertEqual(len(cohorts['ambiguous_13']), 13)
        
    def test_r1_ordering(self):
        # Ensure R1 properties are exactly the 12 frozen ones in exact order
        expected = (
            'MolWt', 'MolLogP', 'MolMR', 'TPSA', 'NumHDonors', 'NumHAcceptors',
            'NumRotatableBonds', 'RingCount', 'NumAromaticRings', 'NumAliphaticRings',
            'FractionCSP3', 'HeavyAtomCount'
        )
        self.assertEqual(R1_PROPERTIES, expected)
        res = get_r1_descriptors("CCO")
        self.assertEqual(tuple(res.keys()), expected)
        
    def test_biogen_counts(self):
        b1, b2 = load_biogen_data()
        self.assertEqual(len(b1), 3087)
        self.assertEqual(len(b2), 2129)

if __name__ == '__main__':
    unittest.main()
