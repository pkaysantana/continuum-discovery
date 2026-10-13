"""Development-only input extractor for the frozen V2 development cohort.

This module reads the master partition and ChEMBL interim data files that
already exist in the repository. It never re-downloads, regenerates splits,
or accesses protected holdout outcomes. Outcomes (CLint values) are loaded
ONLY for the 582 INTERIOR_OBSERVED CV records after the holdout allowlist
check is confirmed. If any boundary condition cannot be verified the function
raises and stops rather than returning partial data.

Data access boundary
--------------------
- Master partition file:  splits/master_partition.csv
- ChEMBL interim sources: data/interim/CHEMBL330137{0,1,2}_rows.csv
- Protected files never accessed: manifests/runs/.../primary_holdout_predictions.csv
  (holdout exclusion is derived entirely from the master partition, not from
  the predictions CSV which was written after V2 execution. The partition is
  the authoritative, pre-execution boundary.)

Limitation explicitly documented
---------------------------------
The interim CSV files (CHEMBL3301370/1/2_rows.csv) contain outcome values for
every activity_id in the master partition, including censored and holdout rows.
This extractor enforces the boundary by (a) building the allowlist from only
the INTERIOR_OBSERVED cv rows of the master partition *before* opening the
interim files, and (b) reading outcome values only for allowlisted IDs. It
does NOT load outcome fields for holdout IDs at any point.

However, the full CLint values for holdout compounds are technically present in
the interim files on disk. The boundary enforced here is a Python-level access
control, not a file-system isolation. If a caller bypasses this function and
reads the interim files directly, the boundary is not maintained. A reviewer
should be aware of this limitation before approving real execution.

No model is fitted and no results are written by this module.
"""
import csv
import hashlib
import json
import re
from pathlib import Path

from rdkit import Chem

# ---------------------------------------------------------------------------
# Authoritative frozen provenance constants
# Computed from the actual on-disk files by this sprint's exploration.
# These are checked at runtime; a mismatch stops extraction.
# ---------------------------------------------------------------------------

# SHA-256 of splits/master_partition.csv  (binary read, all platforms)
MASTER_PARTITION_SHA256 = "971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a"

# SHA-256 of data/interim/CHEMBL3301370_rows.csv
CHEMBL3301370_SHA256 = "fc1ea6fa15736449a75f578b2ff3e97661b8079d087aae000ed3ed508223ab37"

# SHA-256 of data/interim/CHEMBL3301371_rows.csv
CHEMBL3301371_SHA256 = "2c7578045d930d287de37f9da74d38cd978f5f7228b781e4bf2dc4c726bbe924"

# SHA-256 of data/interim/CHEMBL3301372_rows.csv
CHEMBL3301372_SHA256 = "b3164bb3efb7a4c270dcbc2308e54573e728044a516eff1121d0522a3e1066d4"

# V3A freeze manifest records this same CHEMBL3301370 hash as raw_rows_sha256.
# That cross-reference provides independent confirmation that the file is
# unchanged since the V3A checkpoint.
V3A_MANIFEST_RAW_ROWS_SHA256 = "fc1ea6fa15736449a75f578b2ff3e97661b8079d087aae000ed3ed508223ab37"

# V2 selection manifest records the master partition hash.
V2_SELECTION_MASTER_PARTITION_SHA256 = "971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a"

# Expected development cohort definition (V2 SAP)
EXPECTED_N = 582
EXPECTED_FOLDS = {0: 115, 1: 120, 2: 115, 3: 117, 4: 115}

# Partition and status filters
ELIGIBLE_PARTITION = "cv"
ELIGIBLE_STATUS = "INTERIOR_OBSERVED"
ELIGIBLE_RELATION = ""          # empty string = unqualified (no < or > qualifier)

# Assay boundary (uL/min/mg, numerically equal to mL/min/g)
CLINT_LOW = 3.0
CLINT_HIGH = 150.0

# Authoritative representation policy tag (matches harness.py)
REPRESENTATION_POLICY = "V2_R1_12_R2_2048_NOCHIRAL"
TARGET_LABEL = "log10(CLint expressed in uL/min/mg)"

# Source commit used as placeholder (the master partition has no embedded commit)
# This is the V3A checkpoint commit recorded in the README.
SOURCE_COMMIT_PLACEHOLDER = "49e94153a78224eb274ace540085d7a4d483605f"


def _sha256_file(path: Path) -> str:
    """Return the lowercase hex SHA-256 digest of a file (binary read)."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _verify_file_hash(path: Path, expected: str, label: str) -> None:
    """Raise ValueError if the file's SHA-256 does not match expected."""
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    actual = _sha256_file(path)
    if actual != expected:
        raise ValueError(
            f"Provenance failure: {label} hash mismatch.\n"
            f"  Expected: {expected}\n"
            f"  Actual:   {actual}\n"
            f"  Path:     {path}\n"
            "The file has been modified since the V2/V3A checkpoint. "
            "Do not proceed."
        )


def _canonical_identity(smiles: str):
    """Return RDKit canonical SMILES for identity deduplication, or None."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol, isomericSmiles=True)


def extract(repo_root: str | Path, *, skip_hash_verification: bool = False) -> dict:
    """Extract and validate the 582-compound V2 development bundle.

    Parameters
    ----------
    repo_root : str | Path
        Absolute path to the repository root
        (the directory containing ``experiments/``).
    skip_hash_verification : bool
        **For synthetic testing only.** When True, file hash checks are
        bypassed. Must never be True in real execution. The returned
        provenance dict records this flag so callers can detect it.

    Returns
    -------
    dict with keys:
        ``records``    – list of 582 dicts, each with harness.RECORD_FIELDS
        ``provenance`` – dict compatible with harness.validate_bundle

    Raises
    ------
    FileNotFoundError
        If any required source file is absent.
    ValueError
        On any provenance, schema, boundary, or integrity failure.
    PermissionError
        If a holdout ID is detected in the candidate set.
    """
    root = Path(repo_root)
    partition_path = root / "experiments/compound_to_exposure/splits/master_partition.csv"
    chembl_paths = {
        "CHEMBL3301370": root / "experiments/compound_to_exposure/data/interim/CHEMBL3301370_rows.csv",
        "CHEMBL3301371": root / "experiments/compound_to_exposure/data/interim/CHEMBL3301371_rows.csv",
        "CHEMBL3301372": root / "experiments/compound_to_exposure/data/interim/CHEMBL3301372_rows.csv",
    }
    expected_hashes = {
        "master_partition": (partition_path, MASTER_PARTITION_SHA256),
        "CHEMBL3301370":    (chembl_paths["CHEMBL3301370"], CHEMBL3301370_SHA256),
        "CHEMBL3301371":    (chembl_paths["CHEMBL3301371"], CHEMBL3301371_SHA256),
        "CHEMBL3301372":    (chembl_paths["CHEMBL3301372"], CHEMBL3301372_SHA256),
    }

    # ------------------------------------------------------------------
    # Step 1: Verify file hashes BEFORE reading any content.
    # This must happen before any row is parsed so that a tampered file
    # cannot inject data under a passing provenance check.
    # ------------------------------------------------------------------
    if skip_hash_verification:
        partition_sha256 = "SKIPPED_FOR_SYNTHETIC_TEST"
        chembl_sha256 = {k: "SKIPPED_FOR_SYNTHETIC_TEST" for k in chembl_paths}
    else:
        _verify_file_hash(partition_path, MASTER_PARTITION_SHA256, "master_partition.csv")
        chembl_sha256 = {}
        for label, (path, expected) in list(expected_hashes.items())[1:]:
            _verify_file_hash(path, expected, label)
            chembl_sha256[label] = expected
        partition_sha256 = MASTER_PARTITION_SHA256

    # ------------------------------------------------------------------
    # Step 2: Read the master partition.  Build the allowlist of eligible
    # IDs from partition=cv, status=INTERIOR_OBSERVED ONLY.  The holdout
    # set is also extracted here to allow the exclusion check in step 4.
    # No outcome values are read in this step.
    # ------------------------------------------------------------------
    if not partition_path.is_file():
        raise FileNotFoundError(f"Master partition not found: {partition_path}")

    with open(partition_path, encoding="utf-8") as fh:
        partition_rows = list(csv.DictReader(fh))

    required_partition_cols = {"activity_id", "chembl_id", "canonical_smiles", "scaffold_key",
                               "status", "partition", "cv_fold"}
    actual_cols = set(partition_rows[0].keys()) if partition_rows else set()
    missing_cols = required_partition_cols - actual_cols
    if missing_cols:
        raise ValueError(f"Master partition missing required columns: {missing_cols}")

    # Build holdout allowlist (authoritative exclusion set, derived from
    # the partition file before V2 or V3A execution).
    holdout_ids = {r["chembl_id"] for r in partition_rows if r["partition"] == "holdout"}
    if len(holdout_ids) < 1:
        raise ValueError("No holdout IDs found in master partition — file may be corrupt.")

    # Build development allowlist: only eligible CV rows.
    eligible_rows = [
        r for r in partition_rows
        if r["partition"] == ELIGIBLE_PARTITION and r["status"] == ELIGIBLE_STATUS
    ]

    if len(eligible_rows) != EXPECTED_N:
        raise ValueError(
            f"Expected {EXPECTED_N} eligible CV rows, found {len(eligible_rows)}. "
            "Master partition content differs from the frozen V2 cohort definition."
        )

    # Validate fold counts.
    from collections import Counter
    fold_counter = Counter(int(float(r["cv_fold"])) for r in eligible_rows)
    if dict(fold_counter) != EXPECTED_FOLDS:
        raise ValueError(
            f"Fold sizes do not match frozen V2 assignment.\n"
            f"  Expected: {EXPECTED_FOLDS}\n"
            f"  Actual:   {dict(fold_counter)}"
        )

    # Build allowlist: activity_id → partition row
    allowlist: dict[str, dict] = {}
    seen_chembl_ids: set[str] = set()
    for row in eligible_rows:
        aid = row["activity_id"]
        cid = row["chembl_id"]
        if not aid or not cid:
            raise ValueError(f"Empty activity_id or chembl_id in partition row: {row}")
        if aid in allowlist:
            raise ValueError(f"Duplicate activity_id in partition: {aid}")
        if cid in seen_chembl_ids:
            raise ValueError(f"Duplicate chembl_id in eligible partition rows: {cid}")
        seen_chembl_ids.add(cid)
        allowlist[aid] = row

    # ------------------------------------------------------------------
    # Step 3: Read outcome values from ChEMBL interim files.
    # Only activity_ids present in the allowlist are extracted.
    # Holdout IDs are never in the allowlist (enforced by partition status),
    # so their values are never parsed into any output variable.
    # ------------------------------------------------------------------
    outcome_map: dict[str, float] = {}
    smiles_map: dict[str, str] = {}  # activity_id -> raw SMILES from source

    for source_label, path in chembl_paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"ChEMBL interim file not found: {path}")
        with open(path, encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            required_src_cols = {"activity_id", "molecule_chembl_id", "value",
                                 "relation", "units", "canonical_smiles_rdkit"}
            if not required_src_cols.issubset(set(reader.fieldnames or [])):
                raise ValueError(
                    f"Source file {source_label} missing required columns. "
                    f"Expected: {required_src_cols}. "
                    f"Found: {set(reader.fieldnames or [])}"
                )
            for src_row in reader:
                aid = src_row["activity_id"]
                if aid not in allowlist:
                    # This ID is either holdout, censored, or not in our cohort.
                    # Do NOT parse its outcome value.
                    continue

                if aid in outcome_map:
                    raise ValueError(
                        f"Duplicate activity_id {aid} found across source files "
                        f"(second occurrence in {source_label}). "
                        "Cannot determine which outcome is authoritative."
                    )

                # Validate units — must be microL/min/mg (the assay standard)
                units = src_row.get("units", "").strip()
                if units not in ("microL/min/mg",):
                    raise ValueError(
                        f"activity_id {aid}: unexpected units '{units}'. "
                        "Expected 'microL/min/mg'."
                    )

                # Validate relation — must be unqualified (empty string)
                relation = src_row.get("relation", "").strip()
                if relation != ELIGIBLE_RELATION:
                    raise ValueError(
                        f"activity_id {aid}: qualified relation '{relation}' "
                        "found for an INTERIOR_OBSERVED record. "
                        "Only unqualified (empty relation) records are eligible."
                    )

                # Parse and range-check value
                raw_val = src_row.get("value", "").strip()
                if not raw_val:
                    raise ValueError(f"activity_id {aid}: missing CLint value.")
                try:
                    clint = float(raw_val)
                except ValueError:
                    raise ValueError(f"activity_id {aid}: non-numeric CLint value '{raw_val}'.")

                if not (CLINT_LOW < clint < CLINT_HIGH):
                    raise ValueError(
                        f"activity_id {aid}: CLint {clint} is not strictly "
                        f"interior ({CLINT_LOW} < value < {CLINT_HIGH})."
                    )

                outcome_map[aid] = clint
                smiles_map[aid] = src_row["canonical_smiles_rdkit"]

    # ------------------------------------------------------------------
    # Step 4: Confirm every allowlisted ID has an outcome and check for
    # holdout contamination.  This check is redundant by design.
    # ------------------------------------------------------------------
    missing_outcomes = set(allowlist) - set(outcome_map)
    if missing_outcomes:
        raise ValueError(
            f"{len(missing_outcomes)} eligible IDs have no outcome in source files: "
            f"{sorted(missing_outcomes)[:10]}{'...' if len(missing_outcomes) > 10 else ''}"
        )

    # Explicit holdout contamination check (belt-and-braces).
    holdout_overlap = set(outcome_map) & {r["activity_id"] for r in partition_rows
                                          if r["partition"] == "holdout"}
    if holdout_overlap:
        raise PermissionError(
            f"BOUNDARY VIOLATION: {len(holdout_overlap)} holdout activity_id(s) "
            f"present in outcome map: {sorted(holdout_overlap)[:5]}. "
            "Extraction aborted."
        )

    # ------------------------------------------------------------------
    # Step 5: Validate molecular structures and assemble records.
    # Structure validation uses RDKit. Duplicate canonical SMILES fail.
    # Scaffold assignments are re-derived and checked against the partition.
    # ------------------------------------------------------------------
    from application_development.gsk_clearance.harness import scaffold_key as compute_scaffold

    seen_identities: set[str] = set()
    records = []
    assignments: dict[str, list] = {}

    for aid, part_row in allowlist.items():
        smiles = smiles_map[aid]
        clint = outcome_map[aid]
        chembl_id = part_row["chembl_id"]
        fold = int(float(part_row["cv_fold"]))
        frozen_scaffold = part_row["scaffold_key"]

        # Validate structure
        identity = _canonical_identity(smiles)
        if identity is None:
            raise ValueError(f"activity_id {aid} (chembl_id {chembl_id}): invalid SMILES '{smiles}'.")
        if identity in seen_identities:
            raise ValueError(
                f"activity_id {aid} (chembl_id {chembl_id}): duplicate molecular "
                f"identity detected. Canonical SMILES already seen."
            )
        seen_identities.add(identity)

        # Re-derive scaffold and verify it matches the frozen partition value
        try:
            derived_scaffold = compute_scaffold(smiles)
        except ValueError as exc:
            raise ValueError(
                f"activity_id {aid}: scaffold derivation failed: {exc}"
            ) from exc

        if derived_scaffold != frozen_scaffold:
            raise ValueError(
                f"activity_id {aid}: derived scaffold '{derived_scaffold}' "
                f"does not match frozen partition value '{frozen_scaffold}'. "
                "Scaffold assignment is inconsistent."
            )

        record = {
            "id": chembl_id,
            "smiles": smiles,
            "scaffold": derived_scaffold,
            "fold": fold,
            "partition": "cv",
            "relation": None,
            "clint": clint,
        }
        records.append(record)
        assignments[chembl_id] = [derived_scaffold, fold]

    # Sort by chembl_id for deterministic ordering
    records.sort(key=lambda r: r["id"])
    assignments = {r["id"]: assignments[r["id"]] for r in records}

    # Explicitly check that no scaffold spans multiple folds
    scaffold_to_fold: dict[str, int] = {}
    for r in records:
        sc = r["scaffold"]
        f = r["fold"]
        if sc in scaffold_to_fold and scaffold_to_fold[sc] != f:
            raise ValueError(
                f"Scaffold leakage detected: scaffold '{sc}' assigned to multiple folds "
                f"({scaffold_to_fold[sc]} and {f})."
            )
        scaffold_to_fold[sc] = f

    # ------------------------------------------------------------------
    # Step 6: Build and return the provenance bundle.
    # The harness.digest() function is used for the records hash so that
    # the bundle is immediately compatible with harness.validate_bundle().
    # Only the exact 8 fields expected by harness.validate_bundle are
    # placed in provenance; extra extraction metadata is in extraction_meta.
    # ------------------------------------------------------------------
    from application_development.gsk_clearance.harness import digest

    records_sha256 = digest(records)
    fold_list = [r["fold"] for r in records]

    provenance = {
        "kind": "development",
        "source_commit": SOURCE_COMMIT_PLACEHOLDER,
        "source_sha256": CHEMBL3301370_SHA256,
        "partition_sha256": digest(fold_list),
        "records_sha256": records_sha256,
        "assignments": assignments,
        "target": TARGET_LABEL,
        "representation_policy": REPRESENTATION_POLICY,
    }

    extraction_meta = {
        "master_partition_sha256_verified": partition_sha256,
        "chembl_source_sha256_verified": {
            k: (v if not skip_hash_verification else "SKIPPED")
            for k, v in {
                "CHEMBL3301370": CHEMBL3301370_SHA256,
                "CHEMBL3301371": CHEMBL3301371_SHA256,
                "CHEMBL3301372": CHEMBL3301372_SHA256,
            }.items()
        },
        "skip_hash_verification": skip_hash_verification,
        "holdout_ids_excluded_count": len(holdout_ids),
        "records_n": len(records),
        "fold_counts": dict(
            sorted(Counter(r["fold"] for r in records).items())
        ),
    }

    return {
        "records": records,
        "provenance": provenance,
        "extraction_meta": extraction_meta,
    }
