"""Synthetic preparation tests. No real CSV or real outcomes are opened.

The original 13 test intentions are retained with specific failure assertions.
Fixture manifests are independent of production constants and production paths.
"""
import copy
import csv
import io
import unittest
from unittest.mock import patch
from . import extractor as e, harness as h, provenance as p


def csv_bytes(rows):
    fh = io.StringIO(newline="")
    writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return fh.getvalue().encode()


def fixture():
    smiles = ["c1ccccc1", "Cc1ccccc1", "c1ccncc1", "Cc1ccncc1", "C1CCCCC1", "CC1CCCCC1",
              "c1occc1", "Cc1occc1", "c1sccc1", "Cc1sccc1"]
    partition, sources, members = [], [], []
    for i, s in enumerate(smiles):
        aid, cid, fold, scaffold = f"SYN_ACT_{i:02}", f"SYN_{i:02}", i//2, h.scaffold_key(s)
        members.append({"activity_id": aid, "id": cid, "smiles": s, "scaffold": scaffold, "fold": fold})
        partition.append({"activity_id": aid, "chembl_id": cid, "canonical_smiles": s,
                          "scaffold_key": scaffold, "partition": "cv", "status": "INTERIOR_OBSERVED", "cv_fold": str(float(fold))})
        sources.append({"activity_id": aid, "molecule_chembl_id": cid, "canonical_smiles_rdkit": s,
                        "assay_chembl_id": "SYN_ASSAY", "value": str(10+i*5), "standard_value": str(10+i*5),
                        "units": "microL/min/mg", "standard_units": "mL.min-1.g-1", "relation": "", "standard_relation": ""})
    partition.append({"activity_id": "SYN_HOLD_ACT", "chembl_id": "SYN_HOLD", "canonical_smiles": "C1CC1",
                      "scaffold_key": "C1CC1", "partition": "holdout", "status": "INTERIOR_OBSERVED", "cv_fold": ""})
    for aid, cid in [("SYN_HOLD_ACT", "SYN_HOLD"), ("SYN_CENS_ACT", "SYN_CENS")]:
        sources.append({**sources[0], "activity_id": aid, "molecule_chembl_id": cid,
                        "value": "EXCLUDED_OUTCOME_SENTINEL", "standard_value": "EXCLUDED_OUTCOME_SENTINEL"})
    manifest = {"kind": "synthetic", "assay": "SYN_ASSAY", "n": 10, "fold_counts": {str(f): 2 for f in range(5)},
                "members": members, "assignments_sha256": p.assignment_digest(members),
                "protected_activity_ids": ["SYN_HOLD_ACT"], "protected_compound_ids": ["SYN_HOLD"],
                "partition": {"sha256": p.sha256(csv_bytes(partition))},
                "sources": {"SYN_ASSAY": {"sha256": p.sha256(csv_bytes(sources))}},
                "endpoint": {"original_units": "microL/min/mg", "standard_units": "mL.min-1.g-1",
                             "original_relation": "", "standard_relation": "", "numerical_conversion_factor": 1,
                             "range_exclusive": [3, 150]}}
    return partition, sources, manifest


class ExtractorAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.part, self.source, self.manifest = fixture()

    def prepare(self, *, rehash=False):
        part, source = csv_bytes(self.part), csv_bytes(self.source)
        manifest = copy.deepcopy(self.manifest)
        # Parser-focused mutations get fixture hashes, never relaxed scientific rules.
        # Reviewed members remain unchanged. Separate tests cover stale hashes.
        if rehash:
            manifest["partition"]["sha256"] = p.sha256(part)
            manifest["sources"]["SYN_ASSAY"]["sha256"] = p.sha256(source)
        return e.prepare_bytes(part, source, manifest)

    def test_0_clean_synthetic_data_succeeds(self):
        bundle = self.prepare()
        h.validate_bundle(**bundle)
        self.assertEqual(len(bundle["records"]), 10)

    def test_1_holdout_id_in_source_rejected(self):
        with patch.object(e, "endpoint", wraps=e.endpoint) as convert:
            bundle = self.prepare()
        self.assertEqual(convert.call_count, 10)
        self.assertNotIn("EXCLUDED_OUTCOME_SENTINEL", p.encoded(bundle).decode())
        self.assertNotIn("SYN_HOLD", [r["id"] for r in bundle["records"]])

    def test_2_wrong_fold_assignment_rejected(self):
        # Swap individual rows so counts stay fixed but scaffold groups are split.
        self.part[1]["cv_fold"], self.part[2]["cv_fold"] = self.part[2]["cv_fold"], self.part[1]["cv_fold"]
        with self.assertRaisesRegex(ValueError, "scaffold leakage"):
            self.prepare(rehash=True)

    def test_3_tampered_partition_hash_rejected(self):
        self.part[0]["cv_fold"] = "4.0"
        with self.assertRaisesRegex(ValueError, "partition SHA-256"):
            self.prepare()

    def test_4_mismatched_source_checksum_rejected(self):
        self.source[0]["value"] = "11"
        with self.assertRaisesRegex(ValueError, "source SHA-256"):
            self.prepare()

    def test_5_duplicate_molecular_ids_rejected(self):
        self.part[1]["chembl_id"] = self.part[0]["chembl_id"]
        with self.assertRaisesRegex(ValueError, "duplicate or empty compound ID"):
            self.prepare(rehash=True)

    def test_6_wrong_scaffold_assignment_rejected(self):
        self.part[0]["scaffold_key"] = "WRONG"
        with self.assertRaisesRegex(ValueError, "scaffold mismatch"):
            self.prepare(rehash=True)

    def test_7_censored_relation_in_source_rejected(self):
        self.source[0]["relation"] = "<"
        with self.assertRaisesRegex(ValueError, "qualifier mismatch"):
            self.prepare(rehash=True)

    def test_8_missing_assay_value_rejected(self):
        self.source[0]["value"] = ""
        with self.assertRaisesRegex(ValueError, "missing or nonnumeric"):
            self.prepare(rehash=True)

    def test_9_invalid_smiles_rejected(self):
        self.source[0]["canonical_smiles_rdkit"] = "INVALID_SMILES"
        with self.assertRaisesRegex(ValueError, "invalid SMILES"):
            self.prepare(rehash=True)

    def test_10_incomplete_allowlist_rejected(self):
        self.source.pop(0)
        with self.assertRaisesRegex(ValueError, "missing source observations"):
            self.prepare(rehash=True)

    def test_11_holdout_access_attempt_via_allowlist_poisoning(self):
        for field, value in [("activity_id", "SYN_HOLD_ACT"), ("chembl_id", "SYN_HOLD")]:
            with self.subTest(field=field):
                self.part, self.source, self.manifest = fixture()
                self.part[0][field] = value
                with patch.object(e, "source_records", side_effect=AssertionError("must not parse source")):
                    with self.assertRaisesRegex(PermissionError, "holdout.*collision before outcomes"):
                        self.prepare(rehash=True)

    def test_12_wrong_units_in_source_rejected(self):
        self.source[0]["units"] = "mL/min/mg"
        with self.assertRaisesRegex(ValueError, "units mismatch"):
            self.prepare(rehash=True)

    def test_wrong_compound_before_conversion(self):
        self.source[0]["molecule_chembl_id"] = "SYN_WRONG"
        with patch.object(e, "endpoint", side_effect=AssertionError("must not convert")):
            with self.assertRaisesRegex(ValueError, "compound ID mismatch"):
                self.prepare(rehash=True)

    def test_same_scaffold_different_molecule_before_conversion(self):
        self.source[0]["canonical_smiles_rdkit"] = "CCc1ccccc1"
        with patch.object(e, "endpoint", side_effect=AssertionError("must not convert")):
            with self.assertRaisesRegex(ValueError, "full molecular identity mismatch"):
                self.prepare(rehash=True)

    def test_count_preserving_whole_scaffold_swap(self):
        for r in self.part[:4]:
            r["cv_fold"] = str(1-int(float(r["cv_fold"])))
        with self.assertRaisesRegex(ValueError, "exact frozen membership or assignment"):
            self.prepare(rehash=True)

    def test_source_holdout_collisions_before_conversion(self):
        for field, value in [("activity_id", "SYN_HOLD_ACT"), ("molecule_chembl_id", "SYN_HOLD")]:
            with self.subTest(field=field):
                self.part, self.source, self.manifest = fixture()
                self.source[0][field] = value
                with patch.object(e, "endpoint", side_effect=AssertionError("must not convert")):
                    with self.assertRaisesRegex(PermissionError, "holdout.*collision before outcomes"):
                        self.prepare(rehash=True)

    def test_endpoint_and_standard_qualifier_disagreement(self):
        for field, value, message in [("standard_value", "12", "endpoint mismatch"),
                                      ("standard_relation", "=", "qualifier mismatch"),
                                      ("assay_chembl_id", "SYN_WRONG", "assay identity")]:
            with self.subTest(field=field):
                self.part, self.source, self.manifest = fixture()
                self.source[0][field] = value
                with self.assertRaisesRegex(ValueError, message):
                    self.prepare(rehash=True)

    def test_duplicate_observation(self):
        self.source.insert(1, dict(self.source[0]))
        with self.assertRaisesRegex(ValueError, "duplicate source observation"):
            self.prepare(rehash=True)

    def test_duplicate_full_identity(self):
        self.part[1]["canonical_smiles"] = self.part[0]["canonical_smiles"]
        with self.assertRaisesRegex(ValueError, "duplicate molecular identity"):
            self.prepare(rehash=True)

    def test_strict_boundaries_and_nonfinite(self):
        for value in ("3", "150", "NaN", "Infinity"):
            with self.subTest(value=value):
                self.source[0]["value"] = self.source[0]["standard_value"] = value
                with self.assertRaisesRegex(ValueError, "strict interior|nonfinite"):
                    self.prepare(rehash=True)

    def test_fractional_fold_rejected(self):
        self.part[0]["cv_fold"] = "0.5"
        with self.assertRaisesRegex(ValueError, "integral frozen fold"):
            self.prepare(rehash=True)

    def test_csv_materialises_excluded_strings(self):
        # Explicit evidence for the documented limitation, using a synthetic sentinel.
        parsed = list(e.csv_rows(csv_bytes(self.source), {"activity_id", "value"}))
        self.assertEqual(parsed[-1]["value"], "EXCLUDED_OUTCOME_SENTINEL")

    def test_skip_and_missing_preparation_approval_before_files(self):
        with patch.object(p, "input_manifest", side_effect=AssertionError("must not open")):
            with self.assertRaisesRegex(PermissionError, "skipped verification"):
                e.extract("unused", skip_hash_verification=True)
            with self.assertRaisesRegex(PermissionError, "separate preparation approval"):
                e.extract("unused")


if __name__ == "__main__":
    unittest.main()
