import unittest
import os
import sys
import tempfile
import hashlib
import json
import csv
import re
from pathlib import Path

# Add scripts directory to path to import verify_historical_artifacts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts/audit')))
import verify_historical_artifacts

class TestVerifyHistoricalArtifacts(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent.parent
        self.ledger_json_path = self.repo_root / "audit/historical/f2495d8/verification/final_evidence_ledger.json"
        self.ledger_csv_path = self.repo_root / "audit/historical/f2495d8/verification/final_evidence_ledger.csv"
        self.status_md_path = self.repo_root / "audit/historical/f2495d8/verification/FINAL_HISTORICAL_STATUS.md"

    def test_compute_sha256(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(b"test data")
            tf_path = tf.name
            
        try:
            expected = hashlib.sha256(b"test data").hexdigest()
            actual = verify_historical_artifacts.compute_sha256(tf_path)
            self.assertEqual(actual, expected)
        finally:
            os.remove(tf_path)
            
    def test_compute_sha256_missing(self):
        self.assertEqual(verify_historical_artifacts.compute_sha256("nonexistent.pdb"), "N/A")
        
    def test_get_originating_commit_missing(self):
        self.assertEqual(verify_historical_artifacts.get_originating_commit("repo", "nonexistent.pdb"), "N/A")
        
    def test_build_ledger_row(self):
        row = verify_historical_artifacts.build_ledger_row(
            claim_id="TEST_1", claim="Test claim", path="test/path", sha="hash", commit="abcd",
            tool="RFD", origin_status="REAL_MODEL_OUTPUT", historical_execution_evidence="STRONG",
            reproduction_status="NOT_RERUN", legacy_classification="DOCUMENTED_NOT_RECOMPUTED"
        )
        self.assertEqual(row["origin_status"], "REAL_MODEL_OUTPUT")
        self.assertEqual(row["historical_execution_evidence"], "STRONG")
        self.assertEqual(row["reproduction_status"], "NOT_RERUN")
        self.assertEqual(row["classification"], "DOCUMENTED_NOT_RECOMPUTED")

    def test_invariant_real_model_output_cannot_have_none_evidence(self):
        """REAL_MODEL_OUTPUT must not coexist with historical_execution_evidence = NONE."""
        # 1. Unit level test: build_ledger_row must reject this invalid state
        with self.assertRaises(ValueError):
            verify_historical_artifacts.build_ledger_row(
                claim_id="INVALID_ROW", claim="Invalid claim", path="test/path", sha="hash", commit="abcd",
                tool="Model", origin_status="REAL_MODEL_OUTPUT", historical_execution_evidence="NONE",
                reproduction_status="UNRESOLVED", legacy_classification="DOCUMENTED_NOT_RECOMPUTED"
            )

        # 2. Validation level test: validate_ledger_invariants must reject it
        bad_ledger = [{
            "claim_id": "ROW_BAD", "claim": "Bad claim", "artefact_path": "path", "artefact_sha256": "sha",
            "originating_commit": "c", "tool": "T", "origin_status": "REAL_MODEL_OUTPUT",
            "historical_execution_evidence": "NONE", "reproduction_status": "NOT_RERUN",
            "classification": "DOCUMENTED_NOT_RECOMPUTED", "notes": ""
        }]
        with self.assertRaises(ValueError):
            verify_historical_artifacts.validate_ledger_invariants(bad_ledger)

        # 3. Integration level test on generated ledger
        if self.ledger_json_path.exists():
            with open(self.ledger_json_path, "r", encoding="utf-8") as f:
                ledger = json.load(f)
            for row in ledger:
                self.assertFalse(
                    row["origin_status"] == "REAL_MODEL_OUTPUT" and row["historical_execution_evidence"] == "NONE",
                    f"Row {row['claim_id']} violates invariant: REAL_MODEL_OUTPUT cannot have historical_execution_evidence = NONE"
                )

    def test_invariant_mock_or_fallback_cannot_be_real_model_output(self):
        """A byte-identical copied/mock output with proven fallback provenance must not be REAL_MODEL_OUTPUT."""
        # 1. Validation function check
        bad_ledger = [{
            "claim_id": "MOCK_ROW", "claim": "Mock claim", "artefact_path": "path", "artefact_sha256": "sha",
            "originating_commit": "c", "tool": "T", "origin_status": "REAL_MODEL_OUTPUT",
            "historical_execution_evidence": "STRONG", "reproduction_status": "NOT_RERUN",
            "classification": "DOCUMENTED_NOT_RECOMPUTED", "notes": "proven fallback mock output"
        }]
        with self.assertRaises(ValueError):
            verify_historical_artifacts.validate_ledger_invariants(bad_ledger)

        # 2. Verify ledger content for Boltz and PeSTo
        if self.ledger_json_path.exists():
            with open(self.ledger_json_path, "r", encoding="utf-8") as f:
                ledger = json.load(f)

            boltz_rows = [r for r in ledger if r.get("claim_id") == "BOLTZ_OUTPUT"]
            self.assertEqual(len(boltz_rows), 1, "Expected exactly 1 BOLTZ_OUTPUT row")
            boltz = boltz_rows[0]
            self.assertNotEqual(boltz["origin_status"], "REAL_MODEL_OUTPUT")
            self.assertEqual(boltz["origin_status"], "FALLBACK_OR_SIMULATED")
            self.assertEqual(boltz["classification"], "FALLBACK_OR_SIMULATED")
            self.assertEqual(boltz["historical_execution_evidence"], "CONFIRMED")
            self.assertEqual(boltz["reproduction_status"], "DETERMINISTICALLY_VERIFIED")

            pesto_rows = [r for r in ledger if r.get("claim_id") == "PESTO_VALIDATION"]
            self.assertEqual(len(pesto_rows), 1, "Expected exactly 1 PESTO_VALIDATION row")
            pesto = pesto_rows[0]
            self.assertNotEqual(pesto["origin_status"], "REAL_MODEL_OUTPUT")
            self.assertEqual(pesto["origin_status"], "FALLBACK_OR_SIMULATED")
            self.assertEqual(pesto["classification"], "FALLBACK_OR_SIMULATED")
            self.assertEqual(pesto["historical_execution_evidence"], "CONFIRMED")
            self.assertEqual(pesto["reproduction_status"], "DETERMINISTICALLY_VERIFIED")

    def test_invariant_every_simulated_fallback_item_exists_in_ledger(self):
        """Every item mentioned under 'Simulated/fallback' in FINAL_HISTORICAL_STATUS.md must exist in the final ledger."""
        self.assertTrue(self.status_md_path.exists(), f"Missing {self.status_md_path}")
        self.assertTrue(self.ledger_json_path.exists(), f"Missing {self.ledger_json_path}")
        self.assertTrue(self.ledger_csv_path.exists(), f"Missing {self.ledger_csv_path}")

        with open(self.status_md_path, "r", encoding="utf-8") as f:
            status_text = f.read()

        self.assertIn("## Simulated/fallback", status_text)
        sim_section = status_text.split("## Simulated/fallback")[1].split("##")[0]
        items = [line.strip("- ").strip() for line in sim_section.strip().splitlines() if line.strip().startswith("-")]
        self.assertTrue(len(items) >= 2, f"Expected at least Boltz and PeSTo under Simulated/fallback, found: {items}")

        with open(self.ledger_json_path, "r", encoding="utf-8") as f:
            json_ledger = json.load(f)

        with open(self.ledger_csv_path, "r", encoding="utf-8") as f:
            csv_reader = csv.DictReader(f)
            csv_ledger = list(csv_reader)

        # Check in both JSON and CSV
        for item in items:
            item_lower = item.lower()
            matched_json = any(
                (row["tool"].lower() in item_lower or any(k in row["claim_id"].lower() for k in ["boltz", "pesto"]))
                and row["origin_status"] == "FALLBACK_OR_SIMULATED"
                for row in json_ledger
            )
            self.assertTrue(matched_json, f"Item '{item}' from Simulated/fallback missing in JSON ledger")

            matched_csv = any(
                (row["tool"].lower() in item_lower or any(k in row["claim_id"].lower() for k in ["boltz", "pesto"]))
                and row["origin_status"] == "FALLBACK_OR_SIMULATED"
                for row in csv_ledger
            )
            self.assertTrue(matched_csv, f"Item '{item}' from Simulated/fallback missing in CSV ledger")

    def test_invariant_summary_counts_and_ledger_counts_reconcile(self):
        """Summary counts and ledger counts must reconcile."""
        self.assertTrue(self.status_md_path.exists())
        self.assertTrue(self.ledger_json_path.exists())
        self.assertTrue(self.ledger_csv_path.exists())

        with open(self.status_md_path, "r", encoding="utf-8") as f:
            status_text = f.read()

        with open(self.ledger_json_path, "r", encoding="utf-8") as f:
            ledger = json.load(f)

        with open(self.ledger_csv_path, "r", encoding="utf-8") as f:
            csv_rows = list(csv.DictReader(f))

        # CSV and JSON lengths must match
        self.assertEqual(len(ledger), len(csv_rows))

        # 1. RFdiffusion primary backbones
        rfd_match = re.search(r'Generated (\d+) RFdiffusion primary design backbones', status_text)
        self.assertIsNotNone(rfd_match)
        expected_rfd_backbones = int(rfd_match.group(1))
        actual_rfd_backbones = sum(1 for r in ledger if r["tool"] == "RFdiffusion" and r["claim"] == "Primary design backbone")
        self.assertEqual(expected_rfd_backbones, actual_rfd_backbones)

        # 2. ProteinMPNN sequence designs
        mpnn_match = re.search(r'Generated (\d+) ProteinMPNN sequence designs from (\d+) target templates', status_text)
        self.assertIsNotNone(mpnn_match)
        expected_mpnn_seqs = int(mpnn_match.group(1))
        expected_mpnn_templates = int(mpnn_match.group(2))
        
        mpnn_rows = [r for r in ledger if r["tool"] == "ProteinMPNN"]
        self.assertEqual(len(mpnn_rows), expected_mpnn_templates)
        
        actual_gen_seqs = 0
        for r in mpnn_rows:
            gen_match = re.search(r'Generated: (\d+)', r.get("notes", ""))
            if gen_match:
                actual_gen_seqs += int(gen_match.group(1))
        self.assertEqual(expected_mpnn_seqs, actual_gen_seqs)

        # 3. ESMFold structures
        esm_match = re.search(r'Forward-folded (\d+) structures using ESMFold', status_text)
        self.assertIsNotNone(esm_match)
        expected_esm_structures = int(esm_match.group(1))
        actual_esm_structures = sum(1 for r in ledger if r["tool"] == "ESMFold")
        self.assertEqual(expected_esm_structures, actual_esm_structures)

        # 4. Fallback items
        fallback_rows = [r for r in ledger if r["origin_status"] == "FALLBACK_OR_SIMULATED"]
        self.assertEqual(len(fallback_rows), 2)
        fallback_tools = {r["tool"] for r in fallback_rows}
        self.assertEqual(fallback_tools, {"Boltz", "PeSTo"})

        # 5. Unresolved items
        unresolved_rows = [r for r in ledger if r["reproduction_status"] == "UNRESOLVED"]
        self.assertEqual(len(unresolved_rows), 1)
        self.assertEqual(unresolved_rows[0]["claim_id"], "RMSD_0.688")

        # 6. Overall validation runs clean
        self.assertTrue(verify_historical_artifacts.validate_ledger_invariants(ledger, self.status_md_path))

if __name__ == "__main__":
    unittest.main()
