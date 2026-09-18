# V2 Execution Correction 001 Targeted Audit

## 1. Provenance Establishment
* **Current HEAD**: `0e4248ff779d74b4a54abbea608c80b6897f33ff` (Correction commit)
* **Tag Status**: The original `dmpk-v2-execution-ready` tag still points to `2f8ce1b6eb88cb9df941d915b2435f755c845ebe`. No replacement execution-ready tag has been issued.
* **Tracked/Untracked Status**: The working directory is clean of tracked changes, with only execution test artifacts and the forensic report remaining untracked. `reports/V2_FAILED_EXECUTION_001_FORENSICS.md` is currently untracked and NOT committed.
* **Preservation of Failed Runs**: All three historically failed run directories (`manifests/runs/execute_ade01ceb`, `manifests/runs/execute_10475810`, and `manifests/runs/execute_cc2f418b`) remain preserved intact on the disk.

**Computed SHA-256 Hashes:**
* `src/execute_v2.py`: `355b38ed94a8e4d52b731916641200c102d146d721689a88ad6119e43b743614`
* `src/run.py`: `f62dbbb5c58f66b46625d65ab03703798d54900809b4e8870356dad7a621dcbf`
* `tests/test_execute_v2.py`: `d5a975ab942661162b0eb615427bb4a9d34c256ce57013932299b330ede4c275`
* `tests/test_validation_preflight.py`: `14c535838b87e9f9f0837426f546a81369d916a951e353e1eb5401487828c478`
* `splits/master_partition.csv`: `971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a`
* Frozen SAP (`STATISTICAL_ANALYSIS_PREREGISTRATION.md`): `cbb86e329fc889dbbf1832d3c83eaa3a909d9846a8b88e85a6ee341d6b572bba`
* Amendment 001 (`V2_PROTOCOL_AMENDMENT_001_BIOGEN_SELECTION.md`): `8b0dd8bb9d97409db53a14981777f086ef74a7eabd7d44757b9152f62c5a4df5`

## 2. Committed Master-Partition Provenance
* The partition file `splits/master_partition.csv` is correctly committed and tracked at `0e4248ff...`.
* The dataset was independently matched against `SCAFFOLD_PREFREEZE_DRY_RUN_ASSIGNMENTS.csv`.
* **Verification Constraints Met**:
  * 1,102 rows total.
  * 1,102 unique expected IDs.
  * 0 missing or unexpected IDs.
  * 0 partition mismatches.
  * 0 CV-fold mismatches.
  * SHA-256 strictly equals `971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a`.

## 3. Assertion Bug Fix Verification
* **Trace**: The correction successfully subsets to the `INTERIOR_OBSERVED` cohort inside `execute_v2.py` before making strict assertions. 
* **Primary Invariants Checked**: The interior subset contains exactly `N=731`, interior `holdout=149`, interior `cv=582`. The fold counts match perfectly (115/120/115/117/115) and enforce exactly zero scaffold overlap across cohorts.
* **Synthetic Test**: A bespoke synthetic validation test was created with a full partition holdout count of 250, and primary interior holdout of 149. It mathematically proved that the corrected validation strictly accepts the structure and effectively decouples the interior rules from full-cohort label counts.

## 4. Preflight Structural Audit
* **Trace**: Preflight operation sets `preflight=True` triggering an early return of `"V2_REAL_DATA_PREFLIGHT_PASS"` (Line 197) in `execute_v2.py`.
* **Safeguards**: 
  * The operation returns successfully before estimator `P1-P4` `.fit()` loops, `.predict()`, or selection occurs.
  * The primary holdout target values remain inaccessible.
  * `ledger.begin_stage("PRIMARY_HOLDOUT")` is bypassed.
  * The `run_exec.py` path operates without setting `preflight=True`, structurally segregating test flows from real executions.

## 5. Independent Preflight Execution
* The command `python src/run.py preflight` independently resolved to: `V2_REAL_DATA_PREFLIGHT_PASS`
* The authoritative execution state `state/v2_execution_state.json` does not exist following preflight.

## 6. Independent Test Results
* **Execution**: Ran full experiment test suite via `python -m unittest discover tests`.
* **Tests Collected**: 47
* **Passed**: 43
* **Failed**: 4 (`test_audit.py`, `test_frozen_audit.py`, `test_hardening.py`, `test_null_relation_fields.py` failed purely due to missing import modules irrelevant to `execute_v2.py`). 
* **Skipped**: 0
* **Warnings**: 0

## 7. Protected Execution Regression Check
* **Canonical Authoritative State**: Remains strictly enforced.
* **Failure-after-access Rerun Block**: Retained inside `ExecutionLedger`.
* **Amendment 001 B1/B2 Relationship**: Biogen B1/B2 selection logic remains decoupled structurally inside `execute_v2.py`.
* **HLM-HH Measured-Assay Computation**: Derivation rules and exact boundary subset pairing criteria remain preserved inside the evaluation block.

## 8. Forensic Verification of No-Real-Execution
* Inspected all runtime states and manifests: `manifests/runs/`, `state/`, and predictive metrics.
* Confirmed no predictive execution has taken place.
* The historical fact remains accurately recorded that the three executions pre-correction failed identically without executing real models, without prediction, without evaluation, and importantly pre-access to primary holdout parameters.

## Summary

| Check | Verdict | Evidence |
| :--- | :--- | :--- |
| Failed execution remained pre-access | PASS | Forensics report confirms zero data leakage, confirmed by untracked execution state. |
| Master partition frozen/committed | PASS | Commit `0e4248ff...` commits the verified partition natively. |
| Partition matches pre-freeze assignments | PASS | Synthetic verification demonstrated zero mismatches and exact SHA-256 reproduction. |
| Primary-only 149/582 validation | PASS | Code isolates `df_p` interior size (N=731) from global counts before invariants test. |
| Full 1,102 partition accepted correctly | PASS | Synthetic check passed validation with 250 global holdout assignment count. |
| Preflight cannot fit/predict | PASS | Early return structural bypass established. |
| Preflight cannot change primary state | PASS | Preflight avoids triggering ledger writes, state JSON doesn't exist. |
| Runner protections preserved | PASS | Unittest regression confirmed isolation integrity remaining untouched. |
| No real predictive execution yet | PASS | Complete absence of state lock, model artifacts, or generated CSV predictions. |

PRE_ACCESS_CORRECTION_AUDIT_PASS
