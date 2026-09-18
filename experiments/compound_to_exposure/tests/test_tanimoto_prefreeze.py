"""Synthetic leakage/boundary checks, without target values or model execution."""
import sys
import unittest
from pathlib import Path

from rdkit import DataStructs

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tanimoto_prefreeze import bin_index, calculate, reference_pool, summarize


def row(identifier, fold=None, partition="cv"):
    return {"activity_id": identifier, "molecule_chembl_id": "MOLECULE_" + identifier,
            "scaffold_key": "SCAFFOLD_" + identifier, "canonical_smiles_rdkit": "CC",
            "dry_run_partition": partition, "dry_run_cv_fold": str(fold) if fold is not None else ""}


def bits(*positions):
    fp = DataStructs.ExplicitBitVect(2048)
    for position in positions:
        fp.SetBit(position)
    return fp


class TanimotoEvidenceTests(unittest.TestCase):
    def test_bin_edges_and_inclusive_one(self):
        self.assertEqual([bin_index(x) for x in [0, 0.1999999, 0.2, 0.3, 0.4, 0.6, 1]], [0, 0, 1, 2, 3, 4, 4])
        for invalid in [-0.1, 1.01, float("nan")]:
            with self.assertRaises(ValueError):
                bin_index(invalid)

    def test_declared_linear_quantiles_and_complete_bins(self):
        result = summarize([0.1, 0.2, 0.8, 0.9])
        self.assertAlmostEqual(result["q1"], 0.175)
        self.assertAlmostEqual(result["median"], 0.5)
        self.assertAlmostEqual(result["q3"], 0.825)
        self.assertEqual(sum(b["count"] for b in result["bins"]), 4)
        self.assertAlmostEqual(sum(b["fraction"] for b in result["bins"]), 1)

    def test_cv_excludes_self_and_same_fold_perfect_match(self):
        query, same_fold, outside_a, outside_b = row("1", 0), row("2", 0), row("3", 1), row("4", 2)
        cv = [query, same_fold, outside_a, outside_b]
        fps = {"1": bits(1, 2), "2": bits(1, 2), "3": bits(1), "4": bits(3)}
        self.assertEqual([r["activity_id"] for r in reference_pool(query, cv)], ["3", "4"])
        records, exact = calculate([query], cv, fps)
        self.assertEqual(records[0]["reference_n"], 2)
        self.assertEqual(records[0]["maximum_tanimoto"], 0.5)
        self.assertEqual(records[0]["nearest_activity_ids"], ["3"])
        self.assertEqual(exact, [])

    def test_holdout_uses_all_cv_and_retains_all_exact_ties(self):
        query, a, b = row("h", partition="holdout"), row("a", 0), row("b", 1)
        fps = {key: bits(1, 2) for key in ["h", "a", "b"]}
        records, exact = calculate([query], [a, b], fps)
        self.assertEqual(records[0]["maximum_tanimoto"], 1)
        self.assertEqual(records[0]["nearest_activity_ids"], ["a", "b"])
        self.assertEqual(len(exact), 2)
        self.assertTrue(all(not p["same_frozen_scaffold"] for p in exact))

    def test_shared_frozen_scaffold_is_rejected(self):
        query, ref = row("h", partition="holdout"), row("c", 0)
        ref["scaffold_key"] = query["scaffold_key"]
        with self.assertRaises(AssertionError):
            calculate([query], [ref], {"h": bits(1), "c": bits(2)})


if __name__ == "__main__":
    unittest.main()
