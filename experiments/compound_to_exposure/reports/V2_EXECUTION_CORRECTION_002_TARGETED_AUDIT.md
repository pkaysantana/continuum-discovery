# Pre-Access Correction 002 Targeted Audit

## 1. Exact Git / Provenance State

- **Current HEAD**: `645e05a2cc75975b2559d1241db6c90e2d546b09`
- **Is HEAD equal to 645e05a2...?**: Yes
- **reports/V2_FAILED_EXECUTION_002_FORENSICS.md tracked?**: Yes (exists and unmodified relative to HEAD).
- **tests/test_regression.py tracked?**: No (file not found). However, an untracked file `test_synthetic_holdout.py` exists in the repository root.
- **Historical execution-ready tags moved?**: No. They remain exactly where they were (`dmpk-v2-execution-ready` at `2f8ce1b6...` and `dmpk-v2-execution-ready-v2` at `3fb8894f...`).

### Tracked File Hashes (SHA-256)
- `src/execute_v2.py`: `0843d836c360a9553c73690b34aca7c4ab765c9832b5ec8381ae8943a25ec619`
- `src/run.py`: `f62dbbb5c58f66b46625d65ab03703798d54900809b4e8870356dad7a621dcbf`
- `tests/test_execute_v2.py`: `d5a975ab942661162b0eb615427bb4a9d34c256ce57013932299b330ede4c275`
- `tests/test_validation_preflight.py`: `14c535838b87e9f9f0837426f546a81369d916a951e353e1eb5401487828c478`
- `tests/test_regression.py`: NOT FOUND
- `splits/master_partition.csv`: `971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a`
- `reports/V2_PROTOCOL_FREEZE_RECORD.md`: `089a7aa75b85816483e05905c786eab4eb982078b0993f9e0dc8915ea6b539de`
- `reports/V2_PROTOCOL_AMENDMENT_001_FREEZE_RECORD.md`: `531a24cd4b456df771606400baac93ad5a40a83c2444edc46610e2073570c71a`
- `reports/V2_FAILED_EXECUTION_002_FORENSICS.md`: `c06d0d616412bf7074bf8340a99fb27af07d5e65210f3530fe462fab398d42ee`
- `reports/V2_EXECUTION_CORRECTION_002.md`: `4559f99e7fd7e248f40b87e2b7d77ec9289636623e2ed9cf2effb33c859fa3e2`

## 2. Test-Reporting Discrepancy
The canonical test run (`python src/run.py test`) executed 133 tests successfully (133 passed, 0 failures, 0 errors, 0 skipped).
However, `tests/test_regression.py` does not exist. An untracked file `test_synthetic_holdout.py` is present in the repository root, which means it is excluded from the canonical harness (which only discovers `tests/`). Running it independently executed 0 tests. 
This is classified as a provenance correction required before tagging, but not a scientific BLOCKER.

## 3. Findings

| Check | Verdict | Evidence |
|-------|---------|----------|
| Failed Execution 002 pre-access | PASS | State files remain untampered. Preflight run confirmed no fit/predict pathways were activated. Total historical count of real-mode invocations remains preserved (4 real-mode pre-access invocations). |
| ChEMBL structure schema | PASS | `CHEMBL_STRUCTURE_COLUMN` is defined as `canonical_smiles_rdkit` and used consistently. Searched `src/` for `['smiles']` and `["smiles"]` and found no remaining literal fallbacks to aliases. N=731 matrix built from this column cleanly. |
| R1 exact frozen representation | PASS | `get_r1_vector()` correctly builds a 12-dimensional vector in exact frozen sequence (MolWt to HeavyAtomCount) mapping to `(N, 12)` shape arrays, validated via preflight shape checks. |
| R2 exact frozen representation | PASS | `get_r2_morgan()` uses radius 2, 2048 bits, binary vectors, `useChirality=False`. Shape verified as `(N, 2048)` in preflight. |
| Biogen identifier/schema | PASS | Schema reads from `Internal ID` correctly mapped to `chembl_id`. Evaluated counts exactly match expected: 3521 total rows, 3087 HLM populated, 434 missing, 958 floor, 2129 B2 (floor excluded). |
| Genuine Biogen R1/R2 | PASS | R1/R2 matrices for Biogen cohorts correctly populated by looping over `get_r1_vector` and `get_r2_morgan` with the `canonical_smiles_rdkit` structure column. Verified via code inspection and preflight shape checks. |
| B1 partition algorithm | PASS | `compute_master_partition` successfully handles Biogen data using `Internal ID` to trace scaffolds and CV/holdout splits identically to the frozen protocol. |
| B2 inherits B1 partition | PASS | B2 performs a left merge on B1's `['chembl_id', 'partition', 'cv_fold']`, strictly preserving deterministic partitions. |
| B2 inherits B1 model specification | PASS | B1 selects optimal model pipeline; B2 subsequently extracts `p_id = b1_best_candidate['pipeline_id']` rather than running autonomous selection, conforming to Amendment 001. |
| Enhanced preflight exercises real preparation | PASS | `python src/run.py preflight` successfully executed data loading, column checks, vector generation, and master partitioning on full real cohorts before stopping. |
| Enhanced preflight cannot fit/predict | PASS | Execution is strictly hard-coded to return `"V2_REAL_DATA_PREFLIGHT_PASS"` immediately after preparing real representations and checking shapes, inherently protecting `.fit()` and `.predict()`. |
| Execution ledger protections preserved | PASS | `AtomicLock` and `ExecutionLedger` components operate normally. `preflight=False` requires unaltered `authoritative_state`, disallowing mock UUID bypasses. |
| No real predictive execution yet | PASS | Thorough search inside `src/` for `MockPredictor`, `np.zeros`, and other leakage stubs confirmed they only execute if explicitly launched with `synthetic_data` or `dry_run=True`, which is programmatically blocked from actual real execution. No actual `.predict()` calls have occurred in real-mode runs. |

## 4. Final Conclusion

PRE_ACCESS_CORRECTION_002_AUDIT_PASS_WITH_CORRECTIONS
