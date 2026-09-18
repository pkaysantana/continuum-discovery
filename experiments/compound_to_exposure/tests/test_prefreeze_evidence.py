"""Narrow evidence checks only: no models, descriptors, fingerprints or performance."""
import csv
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from prefreeze_evidence import (ROOT, STATUSES, dry_run, hash_order, pair_evidence,
                                read_assay, scaffold, scaffold_evidence, status)


class QualifierTests(unittest.TestCase):
    def row(self, relation, value):
        return dict(relation=relation, standard_relation=relation, value=value, standard_value=value)

    def test_exact_boundaries_and_strict_interior(self):
        for relation, value, expected in [(None, "3", 1), (None, "150", 1),
                                         (None, "3.0000000000000001", 0),
                                         (None, "149.9999999999999999", 0),
                                         ("<", "3.0", 2), (">", "150.0", 3)]:
            self.assertEqual(status(self.row(relation, value)), STATUSES[expected])

    def test_no_null_imputation_or_value_only_censoring(self):
        invalid = [self.row(None, "2.9"), self.row(None, "150.1"), self.row("=", "5"),
                   self.row("<", "5"), self.row(">", "151"), self.row(None, "NaN")]
        invalid += [{**self.row(None, "5"), "relation": "="},
                    {**self.row(None, "5"), "value": "6"}]
        for row in invalid:
            with self.assertRaises(ValueError):
                status(row)


class ScaffoldTests(unittest.TestCase):
    def test_atomic_not_generic_and_empty_rule(self):
        self.assertEqual(scaffold("CC(O)CC"), "__ACYCLIC__")
        self.assertEqual(scaffold("Cc1ccncc1"), "c1ccncc1")
        self.assertNotEqual(scaffold("Cc1ccncc1"), scaffold("Cc1ccccc1"))

    def test_largest_fragment_and_lexicographic_tie(self):
        self.assertEqual(scaffold("c1ccccc1.CCCCCCC"), "__ACYCLIC__")
        # Both six heavy atoms: canonical 'C...' sorts before 'c...'.
        self.assertEqual(scaffold("c1ccccc1.C1CCCCC1"), "C1CCCCC1")
        self.assertEqual(scaffold("C1CCCCC1.c1ccccc1"), "C1CCCCC1")

    def test_chirality_ignored_for_scaffold(self):
        self.assertEqual(scaffold("C[C@H]1CCCCN1"), scaffold("C[C@@H]1CCCCN1"))

    def test_oversized_skip_and_full_budget_not_remaining_budget(self):
        keys = sorted([f"synthetic_{i}" for i in range(4)], key=hash_order)
        counts = dict(zip(keys, [70, 11, 11, 8]))  # budget20; first oversized
        assignments, folds = dry_run(counts, counts)
        self.assertEqual(assignments[keys[0]][0], "cv")
        self.assertEqual(assignments[keys[1]], ("holdout", None))
        self.assertEqual(assignments[keys[2]], ("holdout", None))  # 22, no remaining-budget skip
        self.assertEqual(sum(folds), 78)
        self.assertEqual(assignments[keys[0]][1], 0)
        self.assertEqual(assignments[keys[3]][1], 1)

    def test_zero_primary_groups_and_input_order_invariance(self):
        keys = sorted([f"zero_{i}" for i in range(6)], key=hash_order)
        total = dict(zip(keys, [2, 1, 1, 1, 1, 1]))
        primary = dict(zip(keys, [0, 1, 1, 1, 1, 1]))
        actual, folds = dry_run(total, primary)
        self.assertEqual(actual[keys[0]], ("holdout", None))
        self.assertEqual(actual[keys[1]], ("holdout", None))
        self.assertEqual(folds, [1, 1, 1, 1, 0])
        self.assertEqual(dry_run(dict(reversed(list(total.items()))), primary), (actual, folds))


class FrozenEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hlm, cls.hh = read_assay("CHEMBL3301370"), read_assay("CHEMBL3301372")

    def test_pair_id_structure_agreement_and_matrix(self):
        evidence = pair_evidence(self.hlm, self.hh)
        self.assertEqual(evidence["matrix_hlm_rows_hh_columns"],
                         [[94, 0, 26, 5], [2, 0, 0, 0], [20, 0, 31, 0], [8, 0, 0, 1]])
        self.assertEqual(evidence["counts"]["exact_boundary_sensitivity_spearman_eligible_n"], 96)
        self.assertEqual({p["molecule_chembl_id"] for p in evidence["boundary_ambiguous_pairs"]},
                         {"CHEMBL271012", "CHEMBL552512"})

    def test_frozen_scaffold_counts_and_assignment_integrity(self):
        evidence = scaffold_evidence(self.hlm)
        self.assertEqual(evidence["all_1102"]["unique_groups"], 712)
        self.assertEqual(evidence["primary_731"]["unique_groups"], 532)
        self.assertEqual(evidence["primary_731"]["acyclic_n"], 1)
        self.assertEqual(evidence["dry_run"]["primary_holdout_n"], 149)
        self.assertEqual(evidence["dry_run"]["inner_fold_primary_ns"], [115, 120, 115, 117, 115])
        self.assertEqual(evidence["dry_run"]["groups_crossing_partitions_or_folds"], 0)
        self.assertTrue(evidence["dry_run"]["size_basis_alternative_assignments_identical"])

    def test_saved_reports_reconcile_to_independent_raw_field_counts(self):
        report = json.loads((ROOT / "reports/HLM_HH_QUALIFIER_CROSSTAB.json").read_text())
        h = {r["molecule_chembl_id"]: r for r in self.hlm}
        c = {r["molecule_chembl_id"]: r for r in self.hh}
        # A separate count using the raw qualifiers and exact values, not report statuses.
        n = sum(h[k]["relation"] is None and c[k]["relation"] is None
                and 3 < float(h[k]["value"]) < 150 and 3 < float(c[k]["value"]) < 150
                for k in h.keys() & c.keys())
        self.assertEqual(report["counts"]["primary_spearman_eligible_n"], n)
        with (ROOT / "reports/HLM_HH_QUALIFIER_CROSSTAB.csv").open(newline="") as handle:
            cells = list(csv.DictReader(handle))
        self.assertEqual(sum(int(row[s]) for row in cells for s in STATUSES), 187)
        self.assertEqual(Counter(r["relation"] for r in self.hlm), {None: 744, "<": 274, ">": 84})


if __name__ == "__main__":
    unittest.main()
