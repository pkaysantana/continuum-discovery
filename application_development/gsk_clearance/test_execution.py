"""Synthetic export, receipt, process and result lifecycle tests."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from . import extractor as e, export as x, provenance as p, harness as h, execution as run
from .test_extractor import fixture, csv_bytes


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        part, source, self.manifest = fixture()
        self.bundle = e.prepare_bytes(csv_bytes(part), csv_bytes(source), self.manifest)
        self.export_dir = self.root / "export"
        self.receipt = e.write_export(self.export_dir, self.bundle, self.manifest, "synthetic-test-only")
        run.write_json(self.export_dir / "manifest.json", self.manifest)
        self.export_hash = p.sha256((self.export_dir / "export.json").read_bytes())
        self.receipt_hash = p.sha256((self.export_dir / "receipt.json").read_bytes())

    def tearDown(self):
        self.tmp.cleanup()

    def load(self, **kw):
        return x.verify_export(self.export_dir / "export.json", self.export_dir / "receipt.json", self.manifest,
                               export_sha256=kw.get("export_hash", self.export_hash),
                               receipt_sha256=kw.get("receipt_hash", self.receipt_hash))

    def command(self):
        return [sys.executable, "-B", "-m", "application_development.gsk_clearance.worker",
                "--synthetic-directory", str(self.export_dir), "--export-sha256", self.export_hash,
                "--receipt-sha256", self.receipt_hash]

    def test_verified_export_roundtrip(self):
        bundle, receipt = self.load()
        self.assertEqual(bundle, self.bundle)
        self.assertEqual(receipt["hash_verification"], "VERIFIED")
        self.assertNotIn("EXCLUDED_OUTCOME_SENTINEL", (self.export_dir / "export.json").read_text())

    def test_second_export_rejected(self):
        with self.assertRaises(FileExistsError):
            e.write_export(self.export_dir, self.bundle, self.manifest, "synthetic")

    def test_writers_refuse_historical_destinations(self):
        destination = p.REPO / p.HISTORICAL / "forbidden_synthetic_test_output"
        with self.assertRaisesRegex(PermissionError, "historical scientific subtree"):
            e.write_export(destination, self.bundle, self.manifest, "synthetic")
        with self.assertRaisesRegex(PermissionError, "historical scientific subtree"):
            run.run_supervised(self.command(), destination, self.manifest, self.receipt)
        self.assertFalse(destination.exists())

    def test_forged_receipt_rejected(self):
        forged = dict(self.receipt, source_file_sha256={"SYN_ASSAY": "a"*64})
        (self.export_dir / "receipt.json").write_bytes(p.encoded(forged))
        with patch.object(h, "feature_matrices", side_effect=AssertionError("must not fit")):
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                self.load()

    def test_skipped_receipt_rejected_before_fitting(self):
        forged = dict(self.receipt, hash_verification="SKIPPED")
        data = p.encoded(forged)
        (self.export_dir / "receipt.json").write_bytes(data)
        with patch.object(h, "feature_matrices", side_effect=AssertionError("must not fit")):
            with self.assertRaisesRegex(PermissionError, "skipped or missing"):
                self.load(receipt_hash=p.sha256(data))

    def test_missing_receipt_rejected(self):
        (self.export_dir / "receipt.json").unlink()
        with self.assertRaises(FileNotFoundError):
            self.load()

    def test_missing_verification_status_rejected(self):
        changed = dict(self.receipt)
        del changed["hash_verification"]
        data = p.encoded(changed)
        (self.export_dir / "receipt.json").write_bytes(data)
        with self.assertRaisesRegex(PermissionError, "skipped or missing"):
            self.load(receipt_hash=p.sha256(data))

    def test_committed_authority_mismatch_rejected(self):
        evidence = self.root / p.HISTORICAL / "synthetic_authority.json"
        evidence.parent.mkdir(parents=True)
        evidence.write_bytes(b'{}')
        manifest = {"evidence_revision": "synthetic-revision", "authorities": {
            "execution": {"path": "synthetic_authority.json", "sha256": p.sha256(b'{}')}}}
        with patch.object(subprocess, "check_output", return_value=b'{"different":true}'):
            with self.assertRaisesRegex(ValueError, "committed evidence"):
                p.verify_authorities(self.root, manifest)

    def test_synthetic_id_prefix_is_required(self):
        changed = copy.deepcopy(self.bundle)
        changed["records"][0]["id"] = "CHEMBL_NOT_A_FIXTURE"
        changed["provenance"]["records_sha256"] = p.digest(changed["records"])
        with self.assertRaisesRegex(ValueError, "SYN_ IDs"):
            h.evaluate(**changed)

    def test_self_consistent_modified_export_cannot_change_reviewed_hash(self):
        changed = copy.deepcopy(self.bundle)
        changed["records"][0]["clint"] += 1
        changed["provenance"]["records_sha256"] = p.digest(changed["records"])
        data = p.encoded(changed)
        (self.export_dir / "export.json").write_bytes(data)
        forged = dict(self.receipt, export_sha256=p.sha256(data))
        (self.export_dir / "receipt.json").write_bytes(p.encoded(forged))
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            self.load()

    def test_receipt_source_partition_checks_independent_of_receipt_hash(self):
        for field in ("source_file_sha256", "partition_file_sha256"):
            with self.subTest(field=field):
                receipt = dict(self.receipt, **{field: "a"*64})
                data = p.encoded(receipt)
                (self.export_dir / "receipt.json").write_bytes(data)
                with self.assertRaisesRegex(ValueError, "file hash receipt mismatch"):
                    self.load(receipt_hash=p.sha256(data))

    def test_reassigned_export_rejected_even_with_fixture_hashes(self):
        changed = copy.deepcopy(self.bundle)
        for r in changed["records"][:4]:
            r["fold"] = 1-r["fold"]
        changed["provenance"]["records_sha256"] = p.digest(changed["records"])
        data = p.encoded(changed)
        (self.export_dir / "export.json").write_bytes(data)
        receipt_data = p.encoded(dict(self.receipt, export_sha256=p.sha256(data)))
        (self.export_dir / "receipt.json").write_bytes(receipt_data)
        with self.assertRaisesRegex(ValueError, "exact frozen membership or assignment"):
            self.load(export_hash=p.sha256(data), receipt_hash=p.sha256(receipt_data))

    def test_direct_development_call_cannot_supply_own_approval(self):
        provenance = dict(self.bundle["provenance"], kind="development")
        with patch.object(h, "feature_matrices", side_effect=AssertionError("must not featurize")):
            with self.assertRaisesRegex(PermissionError, "NOT_READY"):
                h.evaluate(self.bundle["records"], provenance, approve_development=True)

    def test_real_runner_blocked_before_launch(self):
        with patch.object(subprocess, "Popen", side_effect=AssertionError("must not launch")):
            with self.assertRaisesRegex(PermissionError, "NOT_READY"):
                run.run_development(self.root / "real")
        self.assertFalse((self.root / "real").exists())

    def test_approval_cannot_relax_resource_contract(self):
        gate = json.loads((p.HERE / "execution_gate.json").read_bytes())
        gate["status"] = "APPROVED"
        gate["memory_limit"]["required_bytes"] = 2147483648
        run.write_json(self.root / "execution_gate.json", gate)
        with patch.object(p, "HERE", self.root):
            with self.assertRaisesRegex(PermissionError, "resource contract"):
                p.require_execution_gate()

    def test_synthetic_separate_process_result_and_no_overwrite(self):
        dest = run.run_supervised(self.command(), self.root / "run", self.manifest, self.receipt, wall_seconds=60)
        result = json.loads((dest / "result.json").read_bytes())
        self.assertEqual(len(result["fitted_configurations"]), 20)
        self.assertEqual(len(result["per_fold_metrics"]), 5)
        self.assertEqual(len(result["descriptor_quality"]["nonfinite_per_column"]), 12)
        ridge = next(r for r in result["fitted_configurations"] if r["pipeline"] == "descriptor_ridge")
        self.assertIn("retained_mask", ridge["preprocessing_state"]["variance"])
        self.assertIn("statistics_", ridge["preprocessing_state"]["impute"])
        self.assertTrue((dest / "COMPLETE.json").exists())
        for name, expected in json.loads((dest / "artifacts.json").read_bytes()).items():
            self.assertEqual(p.sha256((dest / name).read_bytes()), expected)
        with self.assertRaises(FileExistsError):
            run.run_supervised(self.command(), dest, self.manifest, self.receipt)

    def test_worker_failure_has_no_success_marker(self):
        dest = self.root / "fail"
        with self.assertRaisesRegex(RuntimeError, "worker failed"):
            run.run_supervised([sys.executable, "-B", "-c", "raise RuntimeError('synthetic failure')"],
                               dest, self.manifest, self.receipt)
        self.assertFalse((dest / "COMPLETE.json").exists())
        self.assertEqual(json.loads((dest / "FAILED.json").read_bytes())["status"], "FAILED")

    def test_watchdog_terminates_slow_worker(self):
        dest = self.root / "timeout"
        with self.assertRaisesRegex(TimeoutError, "watchdog"):
            run.run_supervised([sys.executable, "-B", "-c", "import time; time.sleep(60)"],
                               dest, self.manifest, self.receipt, wall_seconds=0.3)
        self.assertFalse((dest / "COMPLETE.json").exists())
        self.assertEqual(json.loads((dest / "FAILED.json").read_bytes())["error_type"], "TimeoutError")

    def test_interruption_cannot_publish_success(self):
        dest = self.root / "interrupt"
        with patch.object(subprocess, "Popen", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                run.run_supervised(self.command(), dest, self.manifest, self.receipt)
        self.assertFalse((dest / "COMPLETE.json").exists())
        self.assertTrue((dest / "FAILED.json").exists())

    def test_success_exit_with_invalid_results_has_no_success_marker(self):
        dest = self.root / "invalid"
        command = [sys.executable, "-B", "-c", "import os,pathlib; pathlib.Path(os.environ['GSK_CANDIDATE_RESULT']).write_text('{}')"]
        with self.assertRaises(KeyError):
            run.run_supervised(command, dest, self.manifest, self.receipt)
        self.assertFalse((dest / "COMPLETE.json").exists())

    def test_cwd_is_not_filesystem_isolation(self):
        # Negative capability evidence, synthetic sentinel only. Never probe real outcomes.
        mixed = self.root / "synthetic_mixed_source.txt"
        mixed.write_text("synthetic protected sentinel")
        script = self.root / "probe.py"
        script.write_text("import pathlib,sys\nassert pathlib.Path(sys.argv[1]).read_text() == 'synthetic protected sentinel'\n")
        completed = subprocess.run([sys.executable, "-B", str(script), str(mixed)], cwd=self.export_dir,
                                   capture_output=True)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(json.loads((p.HERE / "execution_gate.json").read_bytes())["filesystem_isolation"]["status"], "NOT_VERIFIED")

    def test_model_worker_does_not_open_preparation_sources(self):
        # Demonstrates logical stage separation, explicitly not OS isolation.
        with patch.object(e, "extract", side_effect=AssertionError("no preparation")), \
             patch.object(e, "source_records", side_effect=AssertionError("no source parsing")):
            bundle, _ = self.load()
            result = h.evaluate(**bundle, config=h.Configuration(trees=2))
        self.assertEqual(len(result["row_order"]), 10)


if __name__ == "__main__":
    unittest.main()
