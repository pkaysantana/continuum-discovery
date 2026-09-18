# V2 Execution Ready V2 Provenance

## Execution-Critical File Hashes (SHA-256)
* `src/execute_v2.py`: `355b38ed94a8e4d52b731916641200c102d146d721689a88ad6119e43b743614`
* `src/run.py`: `f62dbbb5c58f66b46625d65ab03703798d54900809b4e8870356dad7a621dcbf`
* `tests/test_execute_v2.py`: `d5a975ab942661162b0eb615427bb4a9d34c256ce57013932299b330ede4c275`
* `tests/test_validation_preflight.py`: `14c535838b87e9f9f0837426f546a81369d916a951e353e1eb5401487828c478`
* `splits/master_partition.csv`: `971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a`
* `docs/STATISTICAL_ANALYSIS_PREREGISTRATION.md` (Frozen SAP): `cbb86e329fc889dbbf1832d3c83eaa3a909d9846a8b88e85a6ee341d6b572bba`
* `docs/V2_PROTOCOL_AMENDMENT_001_BIOGEN_SELECTION.md` (Amendment 001): `8b0dd8bb9d97409db53a14981777f086ef74a7eabd7d44757b9152f62c5a4df5`

## Provenance Tracking
* **Correction Commit**: `0e4248ff779d74b4a54abbea608c80b6897f33ff`
* **Historical Failed Execution-Ready Tag**: `dmpk-v2-execution-ready` pointing to `2f8ce1b6eb88cb9df941d915b2435f755c845ebe`
* **Failed Startup Invocations**:
  * `execute_ade01ceb`
  * `execute_10475810`
  * `execute_cc2f418b`
* **Failure Classification**: PRE_ACCESS_EXECUTION_FAILURE_CONFIRMED
* **Master-Partition Hash**: `971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a`
* **Preflight Result**: `V2_REAL_DATA_PREFLIGHT_PASS`
* **Canonical Test-Harness Result**: PASS (133 tests collected, 133 passed, 0 failed, 0 skipped, 0 warnings). The four unittests discover errors generated previously were strictly due to discovery framework path execution failures, rather than real code failures.
* **Authoritative State Status**: `state/v2_execution_state.json` is completely absent (`PRIMARY_HOLDOUT` stage is `NOT_STARTED`), meaning absolutely no predictive modeling or target observation has yet occurred on the holdout sets.
