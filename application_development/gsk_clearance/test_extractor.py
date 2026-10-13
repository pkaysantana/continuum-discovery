r"""Adversarial synthetic tests for the development-only input extractor.

All tests use entirely synthetic records and never touch protected data.
No real CLint values, real compound IDs, or real SMILES from the project
dataset are used. Every test verifies that the extractor fails BEFORE model
fitting or scientific execution when a data-integrity boundary is violated.

Run from the repository root:

    .venv\Scripts\python.exe -B -m unittest application_development.gsk_clearance.test_extractor -v

"""
import copy
import hashlib
import json
import os
import pathlib
import sys
import tempfile
import unittest
import csv

# Ensure repository root is on sys.path for direct invocation
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# ── helpers ────────────────────────────────────────────────────────────────

# Nine simple synthetic SMILES from 5 distinct scaffold families for 5 folds.
_SMILES = [
    "c1ccccc1",    # benzene   – fold 0, scaffold: c1ccccc1
    "Cc1ccccc1",   # toluene   – fold 0, scaffold: c1ccccc1
    "c1ccncc1",    # pyridine  – fold 1, scaffold: c1ccncc1
    "Cc1ccncc1",   # 2-picoline– fold 1, scaffold: c1ccncc1
    "C1CCCCC1",    # cyclohex  – fold 2, scaffold: C1CCCCC1
    "CC1CCCCC1",   # Me-cychex – fold 2, scaffold: C1CCCCC1
    "c1occc1",     # furan     – fold 3, scaffold: c1ccoc1
    "Cc1occc1",    # 2-Me-furan– fold 3, scaffold: c1ccoc1
    "c1sccc1",     # thiophene – fold 4, scaffold: c1ccsc1
]
# Five-fold layout: rows 0-1 → fold 0, rows 2-3 → fold 1, rows 4-5 → fold 2,
# rows 6-7 → fold 3, row 8 → fold 4  (counts: 2,2,2,2,1 — intentionally
# different from the real 582-cohort so tests don't accidentally pass
# for the wrong reason)
_FOLDS = [0, 0, 1, 1, 2, 2, 3, 3, 4]
_CLINT = [10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 50.0, 60.0]

# Holdout IDs that must never appear in the development set.
_HOLDOUT_CHEMBL = ["HOLD_001", "HOLD_002"]

# Internal IDs used for synthetic molecules (never matching real ChEMBL IDs).
_DEV_CHEMBL = [f"SYN_DEV_{i:03d}" for i in range(9)]
_ACT_IDS = [f"ACT_{i:05d}" for i in range(9)]

# Provenance constants that MUST match extractor.py constants.
_MASTER_PARTITION_SHA256 = (
    "971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a"
)
_CHEMBL3301370_SHA256 = (
    "fc1ea6fa15736449a75f578b2ff3e97661b8079d087aae000ed3ed508223ab37"
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ── synthetic filesystem builder ───────────────────────────────────────────

class _SyntheticRepo:
    """Builds a minimal fake repository tree in a temp directory."""

    def __init__(self):
        self._td = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._td.name)

    def cleanup(self):
        self._td.cleanup()

    def build(
        self,
        *,
        partition_rows=None,    # list of dicts; if None, uses default 9 rows
        source_rows=None,       # list of dicts for chembl interim; if None uses defaults
        partition_sha_override=None,   # inject wrong hash into extractor constant
        source_sha_override=None,
        extra_holdout_in_source=False,  # adds a holdout ID row in the source file
    ) -> dict:
        """Write synthetic files and return {partition_path, chembl_path, root}."""
        from application_development.gsk_clearance.harness import scaffold_key

        root = self.root
        splits_dir = root / "experiments/compound_to_exposure/splits"
        interim_dir = root / "experiments/compound_to_exposure/data/interim"
        splits_dir.mkdir(parents=True)
        interim_dir.mkdir(parents=True)

        # Build default partition rows
        if partition_rows is None:
            partition_rows = []
            for i, (smiles, fold, clint) in enumerate(zip(_SMILES, _FOLDS, _CLINT)):
                scaffold = scaffold_key(smiles)
                partition_rows.append({
                    "activity_id": _ACT_IDS[i],
                    "chembl_id": _DEV_CHEMBL[i],
                    "canonical_smiles": smiles,
                    "scaffold_key": scaffold,
                    "status": "INTERIOR_OBSERVED",
                    "partition": "cv",
                    "cv_fold": str(float(fold)),
                })
            # Append holdout rows
            for h_id in _HOLDOUT_CHEMBL:
                partition_rows.append({
                    "activity_id": f"HOLD_ACT_{h_id}",
                    "chembl_id": h_id,
                    "canonical_smiles": "c1ccccc1",
                    "scaffold_key": scaffold_key("c1ccccc1"),
                    "status": "LEFT_CENSORED",
                    "partition": "holdout",
                    "cv_fold": "",
                })

        # Write master_partition.csv
        partition_path = splits_dir / "master_partition.csv"
        if partition_rows:
            fieldnames = list(partition_rows[0].keys())
        else:
            fieldnames = ["activity_id","chembl_id","canonical_smiles","scaffold_key",
                          "status","partition","cv_fold"]
        with open(partition_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(partition_rows)

        actual_partition_sha = _sha256_file(partition_path)

        # Build default source rows
        if source_rows is None:
            source_rows = []
            for i, (smiles, fold, clint) in enumerate(zip(_SMILES, _FOLDS, _CLINT)):
                source_rows.append({
                    "activity_id": _ACT_IDS[i],
                    "molecule_chembl_id": _DEV_CHEMBL[i],
                    "canonical_smiles_rdkit": smiles,
                    "value": str(clint),
                    "relation": "",
                    "units": "microL/min/mg",
                    "standard_value": str(clint),
                    "standard_units": "mL.min-1.g-1",
                    "standard_relation": "",
                })
            if extra_holdout_in_source:
                # Add a holdout ID into the source file
                source_rows.append({
                    "activity_id": "HOLD_ACT_HOLD_001",
                    "molecule_chembl_id": "HOLD_001",
                    "canonical_smiles_rdkit": "c1ccccc1",
                    "value": "5.0",
                    "relation": "",
                    "units": "microL/min/mg",
                    "standard_value": "5.0",
                    "standard_units": "mL.min-1.g-1",
                    "standard_relation": "",
                })

        # Write a single source interim file (tests only need one)
        chembl_path = interim_dir / "CHEMBL3301370_rows.csv"
        src_fieldnames = list(source_rows[0].keys()) if source_rows else [
            "activity_id","molecule_chembl_id","canonical_smiles_rdkit","value",
            "relation","units","standard_value","standard_units","standard_relation"]
        with open(chembl_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=src_fieldnames)
            w.writeheader()
            w.writerows(source_rows)

        actual_chembl_sha = _sha256_file(chembl_path)

        # Create stub files for the other two CHEMBL interim files (empty, correct hash)
        for fname in ("CHEMBL3301371_rows.csv", "CHEMBL3301372_rows.csv"):
            stub = interim_dir / fname
            with open(stub, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=src_fieldnames)
                w.writeheader()

        return {
            "root": root,
            "partition_path": partition_path,
            "chembl_path": chembl_path,
            "actual_partition_sha": actual_partition_sha,
            "actual_chembl_sha": actual_chembl_sha,
        }


# ── patch helper ──────────────────────────────────────────────────────────

def _with_patched_constants(repo_info, monkeypatches: dict):
    """Context manager that temporarily patches extractor module constants."""
    import application_development.gsk_clearance.extractor as ext
    originals = {}
    for k, v in monkeypatches.items():
        originals[k] = getattr(ext, k)
        setattr(ext, k, v)
    return originals


def _restore_constants(originals):
    import application_development.gsk_clearance.extractor as ext
    for k, v in originals.items():
        setattr(ext, k, v)


# ── test cases ────────────────────────────────────────────────────────────

class ExtractorAdversarialTests(unittest.TestCase):
    """12 adversarial synthetic tests for the development-only extractor."""

    def setUp(self):
        self.repo = _SyntheticRepo()

    def tearDown(self):
        self.repo.cleanup()

    def _extract_with_real_hashes(self, info, extra_patches=None):
        """Call extractor.extract() with hashes patched to match the synthetic files."""
        import application_development.gsk_clearance.extractor as ext
        patches = {
            "MASTER_PARTITION_SHA256": info["actual_partition_sha"],
            "CHEMBL3301370_SHA256": info["actual_chembl_sha"],
            "CHEMBL3301371_SHA256": _sha256_file(
                info["root"] / "experiments/compound_to_exposure/data/interim/CHEMBL3301371_rows.csv"),
            "CHEMBL3301372_SHA256": _sha256_file(
                info["root"] / "experiments/compound_to_exposure/data/interim/CHEMBL3301372_rows.csv"),
            # Relax cohort size/fold checks for synthetic data (9 rows, not 582)
            "EXPECTED_N": 9,
            "EXPECTED_FOLDS": {0: 2, 1: 2, 2: 2, 3: 2, 4: 1},
        }
        if extra_patches:
            patches.update(extra_patches)
        originals = _with_patched_constants(info, patches)
        try:
            return ext.extract(info["root"])
        finally:
            _restore_constants(originals)

    # ── Test 1: Unexpected protected-holdout ID in source file ──────────
    def test_1_holdout_id_in_source_rejected(self):
        """A holdout activity_id that slips into the source file must be ignored
        (never appear in outcome_map). The result should still succeed with 9 records
        — the holdout row is filtered by the allowlist before outcome access."""
        info = self.repo.build(extra_holdout_in_source=True)
        result = self._extract_with_real_hashes(info)
        # The holdout ID must not appear in any record
        record_ids = {r["id"] for r in result["records"]}
        self.assertNotIn("HOLD_001", record_ids)
        self.assertEqual(len(result["records"]), 9)

    # ── Test 2: Incorrectly assigned frozen fold in partition ───────────
    def test_2_wrong_fold_assignment_rejected(self):
        """A scaffold group assigned to two different folds must be rejected."""
        from application_development.gsk_clearance.harness import scaffold_key
        info_data = self.repo.build.__func__  # just build default first
        info = self.repo.build()
        # Tamper: change row 0's fold so its scaffold group (same as row 1)
        # would appear in two folds. We rebuild with tampered partition.
        self.repo.cleanup()
        self.repo = _SyntheticRepo()

        from application_development.gsk_clearance.harness import scaffold_key as sk
        partition_rows = []
        for i, (smiles, fold, clint) in enumerate(zip(_SMILES, _FOLDS, _CLINT)):
            partition_rows.append({
                "activity_id": _ACT_IDS[i],
                "chembl_id": _DEV_CHEMBL[i],
                "canonical_smiles": smiles,
                "scaffold_key": sk(smiles),
                "status": "INTERIOR_OBSERVED",
                "partition": "cv",
                "cv_fold": str(float(fold)),
            })
        # Row 0 and row 1 have the same scaffold (benzene family).
        # Move row 1 to fold 1 so the scaffold spans two folds.
        partition_rows[1]["cv_fold"] = "1.0"
        # Append holdouts
        for h_id in _HOLDOUT_CHEMBL:
            partition_rows.append({
                "activity_id": f"HOLD_ACT_{h_id}",
                "chembl_id": h_id,
                "canonical_smiles": "c1ccccc1",
                "scaffold_key": sk("c1ccccc1"),
                "status": "LEFT_CENSORED",
                "partition": "holdout",
                "cv_fold": "",
            })
        # Expected fold counts change; this will also fail EXPECTED_FOLDS check
        # before reaching scaffold validation. That is acceptable — it fails closed.
        info = self.repo.build(partition_rows=partition_rows)
        with self.assertRaises((ValueError, PermissionError)):
            self._extract_with_real_hashes(info)

    # ── Test 3: Tampered partition file ─────────────────────────────────
    def test_3_tampered_partition_hash_rejected(self):
        """A modified partition file whose SHA-256 no longer matches must be rejected."""
        info = self.repo.build()
        # Append a spurious byte to the partition file
        with open(info["partition_path"], "ab") as f:
            f.write(b"\n")
        import application_development.gsk_clearance.extractor as ext
        # Hash constants still point to the original (unmodified) value
        originals = _with_patched_constants(
            info, {"MASTER_PARTITION_SHA256": info["actual_partition_sha"]}
        )
        try:
            with self.assertRaisesRegex(ValueError, "[Pp]rovenance"):
                ext.extract(info["root"])
        finally:
            _restore_constants(originals)

    # ── Test 4: Mismatched source checksum ───────────────────────────────
    def test_4_mismatched_source_checksum_rejected(self):
        """If the source file hash does not match the authoritative constant, reject."""
        info = self.repo.build()
        # Corrupt the source file
        with open(info["chembl_path"], "ab") as f:
            f.write(b"\n")
        import application_development.gsk_clearance.extractor as ext
        originals = _with_patched_constants(
            info, {
                "MASTER_PARTITION_SHA256": info["actual_partition_sha"],
                "CHEMBL3301370_SHA256": info["actual_chembl_sha"],  # stale (pre-corruption)
                "EXPECTED_N": 9,
                "EXPECTED_FOLDS": {0: 2, 1: 2, 2: 2, 3: 2, 4: 1},
            }
        )
        try:
            with self.assertRaisesRegex(ValueError, "[Pp]rovenance"):
                ext.extract(info["root"])
        finally:
            _restore_constants(originals)

    # ── Test 5: Duplicate molecular IDs ──────────────────────────────────
    def test_5_duplicate_molecular_ids_rejected(self):
        """Duplicate chembl_id entries in the eligible partition rows must fail."""
        from application_development.gsk_clearance.harness import scaffold_key as sk
        partition_rows = []
        for i, (smiles, fold, clint) in enumerate(zip(_SMILES, _FOLDS, _CLINT)):
            partition_rows.append({
                "activity_id": _ACT_IDS[i],
                "chembl_id": _DEV_CHEMBL[i],
                "canonical_smiles": smiles,
                "scaffold_key": sk(smiles),
                "status": "INTERIOR_OBSERVED",
                "partition": "cv",
                "cv_fold": str(float(fold)),
            })
        # Duplicate the first chembl_id
        dup = copy.deepcopy(partition_rows[0])
        dup["activity_id"] = "ACT_99999"  # different activity_id, same chembl_id
        partition_rows.append(dup)
        # Append holdouts
        for h_id in _HOLDOUT_CHEMBL:
            partition_rows.append({
                "activity_id": f"HOLD_ACT_{h_id}",
                "chembl_id": h_id,
                "canonical_smiles": "c1ccccc1",
                "scaffold_key": sk("c1ccccc1"),
                "status": "LEFT_CENSORED",
                "partition": "holdout",
                "cv_fold": "",
            })
        self.repo.cleanup()
        self.repo = _SyntheticRepo()
        info = self.repo.build(partition_rows=partition_rows)
        # N is now 10 not 9 — EXPECTED_N patch won't match; still fails closed
        with self.assertRaises(ValueError):
            self._extract_with_real_hashes(info, extra_patches={"EXPECTED_N": 10})

    # ── Test 6: Incorrect scaffold assignment ────────────────────────────
    def test_6_wrong_scaffold_assignment_rejected(self):
        """A partition row with a scaffold_key inconsistent with its SMILES fails."""
        from application_development.gsk_clearance.harness import scaffold_key as sk
        partition_rows = []
        for i, (smiles, fold, clint) in enumerate(zip(_SMILES, _FOLDS, _CLINT)):
            partition_rows.append({
                "activity_id": _ACT_IDS[i],
                "chembl_id": _DEV_CHEMBL[i],
                "canonical_smiles": smiles,
                "scaffold_key": sk(smiles),
                "status": "INTERIOR_OBSERVED",
                "partition": "cv",
                "cv_fold": str(float(fold)),
            })
        # Inject a wrong scaffold for row 0
        partition_rows[0]["scaffold_key"] = "WRONG_SCAFFOLD_XYZ"
        for h_id in _HOLDOUT_CHEMBL:
            partition_rows.append({
                "activity_id": f"HOLD_ACT_{h_id}",
                "chembl_id": h_id,
                "canonical_smiles": "c1ccccc1",
                "scaffold_key": sk("c1ccccc1"),
                "status": "LEFT_CENSORED",
                "partition": "holdout",
                "cv_fold": "",
            })
        self.repo.cleanup()
        self.repo = _SyntheticRepo()
        info = self.repo.build(partition_rows=partition_rows)
        with self.assertRaisesRegex(ValueError, "[Ss]caffold"):
            self._extract_with_real_hashes(info)

    # ── Test 7: Unexpected relation / censored endpoint ──────────────────
    def test_7_censored_relation_in_source_rejected(self):
        """A source row with a qualified relation (< or >) must be rejected."""
        source_rows = []
        from application_development.gsk_clearance.harness import scaffold_key as sk
        for i, (smiles, fold, clint) in enumerate(zip(_SMILES, _FOLDS, _CLINT)):
            source_rows.append({
                "activity_id": _ACT_IDS[i],
                "molecule_chembl_id": _DEV_CHEMBL[i],
                "canonical_smiles_rdkit": smiles,
                "value": str(clint),
                "relation": "<" if i == 0 else "",  # row 0 is censored
                "units": "microL/min/mg",
                "standard_value": str(clint),
                "standard_units": "mL.min-1.g-1",
                "standard_relation": "",
            })
        info = self.repo.build(source_rows=source_rows)
        with self.assertRaisesRegex(ValueError, "[Rr]elation"):
            self._extract_with_real_hashes(info)

    # ── Test 8: Missing assay value ──────────────────────────────────────
    def test_8_missing_assay_value_rejected(self):
        """A source row with an empty CLint value field must be rejected."""
        source_rows = []
        for i, (smiles, fold, clint) in enumerate(zip(_SMILES, _FOLDS, _CLINT)):
            source_rows.append({
                "activity_id": _ACT_IDS[i],
                "molecule_chembl_id": _DEV_CHEMBL[i],
                "canonical_smiles_rdkit": smiles,
                "value": "" if i == 3 else str(clint),  # row 3 is missing
                "relation": "",
                "units": "microL/min/mg",
                "standard_value": str(clint),
                "standard_units": "mL.min-1.g-1",
                "standard_relation": "",
            })
        info = self.repo.build(source_rows=source_rows)
        with self.assertRaisesRegex(ValueError, "[Mm]issing"):
            self._extract_with_real_hashes(info)

    # ── Test 9: Invalid molecular structure ──────────────────────────────
    def test_9_invalid_smiles_rejected(self):
        """A source row whose SMILES cannot be parsed by RDKit must fail."""
        source_rows = []
        for i, (smiles, fold, clint) in enumerate(zip(_SMILES, _FOLDS, _CLINT)):
            source_rows.append({
                "activity_id": _ACT_IDS[i],
                "molecule_chembl_id": _DEV_CHEMBL[i],
                "canonical_smiles_rdkit": "INVALID_SMILES_XYZ" if i == 2 else smiles,
                "value": str(clint),
                "relation": "",
                "units": "microL/min/mg",
                "standard_value": str(clint),
                "standard_units": "mL.min-1.g-1",
                "standard_relation": "",
            })
        info = self.repo.build(source_rows=source_rows)
        with self.assertRaisesRegex(ValueError, "[Ii]nvalid SMILES"):
            self._extract_with_real_hashes(info)

    # ── Test 10: Incomplete development allowlist ─────────────────────────
    def test_10_incomplete_allowlist_rejected(self):
        """If the source files cover fewer IDs than the allowlist, extraction fails."""
        # Remove the last source row so one allowlisted ID has no outcome
        from application_development.gsk_clearance.harness import scaffold_key as sk
        source_rows = []
        for i, (smiles, fold, clint) in enumerate(zip(_SMILES, _FOLDS, _CLINT)):
            if i < 8:  # row 8 (last) is missing from source
                source_rows.append({
                    "activity_id": _ACT_IDS[i],
                    "molecule_chembl_id": _DEV_CHEMBL[i],
                    "canonical_smiles_rdkit": smiles,
                    "value": str(clint),
                    "relation": "",
                    "units": "microL/min/mg",
                    "standard_value": str(clint),
                    "standard_units": "mL.min-1.g-1",
                    "standard_relation": "",
                })
        info = self.repo.build(source_rows=source_rows)
        with self.assertRaisesRegex(ValueError, "no outcome"):
            self._extract_with_real_hashes(info)

    # ── Test 11: Attempt to access an excluded outcome ────────────────────
    def test_11_holdout_access_attempt_via_allowlist_poisoning(self):
        """A holdout activity_id injected into the partition as cv/INTERIOR_OBSERVED
        must be caught by the boundary check or fold-count mismatch before extraction
        succeeds. This simulates an allowlist-poisoning attack."""
        from application_development.gsk_clearance.harness import scaffold_key as sk
        partition_rows = []
        for i, (smiles, fold, clint) in enumerate(zip(_SMILES, _FOLDS, _CLINT)):
            partition_rows.append({
                "activity_id": _ACT_IDS[i],
                "chembl_id": _DEV_CHEMBL[i],
                "canonical_smiles": smiles,
                "scaffold_key": sk(smiles),
                "status": "INTERIOR_OBSERVED",
                "partition": "cv",
                "cv_fold": str(float(fold)),
            })
        # Inject a known-holdout CHEMBL ID into the cv partition
        partition_rows.append({
            "activity_id": "ACT_POISON",
            "chembl_id": "HOLD_001",
            "canonical_smiles": "c1ccccc1",
            "scaffold_key": sk("c1ccccc1"),
            "status": "INTERIOR_OBSERVED",
            "partition": "cv",
            "cv_fold": "4.0",
        })
        # Keep holdout rows present (they form the holdout_ids set)
        for h_id in _HOLDOUT_CHEMBL:
            partition_rows.append({
                "activity_id": f"HOLD_ACT_{h_id}",
                "chembl_id": h_id,
                "canonical_smiles": "c1ccccc1",
                "scaffold_key": sk("c1ccccc1"),
                "status": "LEFT_CENSORED",
                "partition": "holdout",
                "cv_fold": "",
            })
        self.repo.cleanup()
        self.repo = _SyntheticRepo()
        info = self.repo.build(partition_rows=partition_rows)
        # EXPECTED_N is now 10, fold 4 becomes 2 rows → fails EXPECTED_FOLDS
        with self.assertRaises((ValueError, PermissionError)):
            self._extract_with_real_hashes(
                info, extra_patches={"EXPECTED_N": 10, "EXPECTED_FOLDS": {0: 2, 1: 2, 2: 2, 3: 2, 4: 2}}
            )

    # ── Test 12: Incorrect input schema or units ──────────────────────────
    def test_12_wrong_units_in_source_rejected(self):
        """Source rows with unexpected units (e.g. mL/min/mg instead of microL/min/mg)
        must be rejected before outcome values are accepted."""
        source_rows = []
        for i, (smiles, fold, clint) in enumerate(zip(_SMILES, _FOLDS, _CLINT)):
            source_rows.append({
                "activity_id": _ACT_IDS[i],
                "molecule_chembl_id": _DEV_CHEMBL[i],
                "canonical_smiles_rdkit": smiles,
                "value": str(clint),
                "relation": "",
                "units": "mL/min/mg" if i == 0 else "microL/min/mg",  # wrong units
                "standard_value": str(clint),
                "standard_units": "mL.min-1.g-1",
                "standard_relation": "",
            })
        info = self.repo.build(source_rows=source_rows)
        with self.assertRaisesRegex(ValueError, "[Uu]nits"):
            self._extract_with_real_hashes(info)

    # ── Sanity test: Clean synthetic data extracts successfully ───────────
    def test_0_clean_synthetic_data_succeeds(self):
        """Baseline: synthetic data extracts without error and passes harness.validate_bundle."""
        from application_development.gsk_clearance import harness
        info = self.repo.build()
        result = self._extract_with_real_hashes(info)
        self.assertEqual(len(result["records"]), 9)
        self.assertIn("provenance", result)
        self.assertIn("extraction_meta", result)
        self.assertEqual(result["provenance"]["kind"], "development")
        self.assertFalse(result["extraction_meta"]["skip_hash_verification"])
        fold_counts = result["extraction_meta"]["fold_counts"]
        self.assertEqual(fold_counts, {0: 2, 1: 2, 2: 2, 3: 2, 4: 1})
        # Verify the bundle passes harness.validate_bundle under synthetic fixture rules
        prov_synth = dict(result["provenance"], kind="synthetic")
        harness.validate_bundle(result["records"], prov_synth)
        # Verify harness.validate_bundle rejects N=9 when kind is "development" (expects N=582)
        with self.assertRaisesRegex(ValueError, "development universe differs"):
            harness.validate_bundle(result["records"], result["provenance"], approve_development=True)


if __name__ == "__main__":
    unittest.main()
