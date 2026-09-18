# Pre-Access Correction 002 Closure

## 1. Context and Audit Findings
- **Correction Commit**: 645e05a2cc75975b2559d1241db6c90e2d546b09
- **Targeted Audit Verdict**: PRE_ACCESS_CORRECTION_002_AUDIT_PASS_WITH_CORRECTIONS
- **Orphan-Test Discrepancy**: The file `test_synthetic_holdout.py` existed in the repository root and was not discovered by the canonical test harness. It contained purely synthetic partition assertions mapping fold/holdout counts.
- **Resolution**: The intended behavior of `test_synthetic_holdout.py` (validating deterministic splits and interior subset sizes) is already meaningfully and comprehensively covered by `tests/test_validation_preflight.py` (which modifies the master partition file and expects the real implementation to raise `AssertionError` for identical invalid partition logic). Therefore, to preserve the artifact without cluttering the canonical test discovery or adding a duplicate, it was moved to `scratch/test_synthetic_holdout.py` as an untracked development artifact.
- **Canonical Test Count After Resolution**: 133

## 2. Canonical Test Execution
- **Collected**: 133
- **Passed**: 133
- **Failed**: 0
- **Skipped**: 0
- **Errors**: 0
- **Warnings**: Hundreds of `DEPRECATION WARNING: please use MorganGenerator` emitted by RDKit, unchanged.

## 3. Preflight Execution
- **Result**: `V2_REAL_DATA_PREFLIGHT_PASS`
- **Authoritative State**: `state/v2_execution_state.json` remains absent, so `PRIMARY_HOLDOUT` remains `NOT_STARTED`.
- **Artifacts**: No real predictive metrics or model artifacts were created.

## 4. Production Hashes Before/After
- `src/execute_v2.py`: `0843d836c360a9553c73690b34aca7c4ab765c9832b5ec8381ae8943a25ec619`
- `src/run.py`: `f62dbbb5c58f66b46625d65ab03703798d54900809b4e8870356dad7a621dcbf`
- `splits/master_partition.csv`: `971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a`
- `reports/V2_PROTOCOL_FREEZE_RECORD.md`: `089a7aa75b85816483e05905c786eab4eb982078b0993f9e0dc8915ea6b539de`
- `reports/V2_PROTOCOL_AMENDMENT_001_FREEZE_RECORD.md`: `531a24cd4b456df771606400baac93ad5a40a83c2444edc46610e2073570c71a`
Production hashes are confirmed identical to the targeted audit record.

## 5. Historical Record
- **Total historical real-mode invocations**: 4 (all pre-access).
