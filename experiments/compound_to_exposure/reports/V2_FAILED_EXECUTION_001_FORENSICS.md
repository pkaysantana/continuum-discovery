# V2 Failed Execution 001 Forensics

## 1. Inventory of Attempts

Three real-mode invocations were launched after the `dmpk-v2-execution-ready` tag.

**Attempt 1**
* **Run ID/Directory**: `manifests/runs/execute_ade01ceb`
* **Timestamp**: `2026-09-18T15:43:35.339740`
* **Command/Path**: `python run_exec.py` (Invokes `src/execute_v2.py`)
* **Furthest execution stage reached**: Failed during initial data loading, before any logged stage transition could begin.
* **Exception/Failure**: `AssertionError` at `src/execute_v2.py` line 166.
* **Model `.fit()` occurred**: No
* **Model `.predict()` occurred**: No
* **Primary holdout target values accessed**: No
* **Primary holdout predictions generated**: No
* **Authoritative ledger state before/after**: Did not exist before or after (equivalent to `NOT_STARTED`).
* **Artifacts written**: Directory `execute_ade01ceb` created but left completely empty. No manifest or prediction files were materialized.

**Attempt 2**
* **Run ID/Directory**: `manifests/runs/execute_10475810`
* **Timestamp**: `2026-09-18T15:44:10.400196`
* **Command/Path**: `python run_exec.py` (Invokes `src/execute_v2.py`)
* **Furthest execution stage reached**: Failed during initial data loading.
* **Exception/Failure**: `AssertionError` at `src/execute_v2.py` line 166.
* **Model `.fit()` occurred**: No
* **Model `.predict()` occurred**: No
* **Primary holdout target values accessed**: No
* **Primary holdout predictions generated**: No
* **Authoritative ledger state before/after**: Did not exist before or after (equivalent to `NOT_STARTED`).
* **Artifacts written**: Directory `execute_10475810` created but left completely empty. No manifest or prediction files were materialized.

**Attempt 3**
* **Run ID/Directory**: `manifests/runs/execute_cc2f418b`
* **Timestamp**: `2026-09-18T15:46:16.468378`
* **Command/Path**: `python run_exec.py` (Invokes `src/execute_v2.py`)
* **Furthest execution stage reached**: Failed during initial data loading.
* **Exception/Failure**: `AssertionError` at `src/execute_v2.py` line 166.
* **Model `.fit()` occurred**: No
* **Model `.predict()` occurred**: No
* **Primary holdout target values accessed**: No
* **Primary holdout predictions generated**: No
* **Authoritative ledger state before/after**: Did not exist before or after (equivalent to `NOT_STARTED`).
* **Artifacts written**: Directory `execute_cc2f418b` created but left completely empty. No manifest or prediction files were materialized.

## 2. Trace Assertion relative to Protected Access

The failing line in `src/execute_v2.py` is:
`assert len(partition_df[partition_df['partition']=='holdout']) == 149` (Line 166)

Based on the execution path in `execute_v2.py`, this assertion executes:
* **Before** P1–P4 model fitting (which begins at line 190).
* **Before** selection (which occurs at line 214).
* **Before** the serialization of `selection_manifest.json` (which occurs at line 227).
* **Before** the `PRIMARY_HOLDOUT` stage is marked as `STARTED` in the ledger (which occurs at line 237).
* **Before** any primary holdout target access or predictive metric calculation (target subsetting and `predict()` occur starting at line 242).

## 3. Inspect Authoritative Execution State

The authoritative execution state file `state/v2_execution_state.json` and its corresponding lock file **do not exist**.

Because the script crashed at line 166 before `ledger.begin_stage('PRIMARY_HOLDOUT', ...)` (line 237) was ever called, no attempted invocation transitioned the `PRIMARY_HOLDOUT` stage away from `NOT_STARTED`.

## 4. Establish Whether Real Predictive Execution Occurred

There is **zero evidence** of any real predictive execution:
* No actual AstraZeneca `.fit()` occurred.
* No actual Biogen `.fit()` occurred.
* No primary holdout `.predict()` occurred.
* No actual primary MAE, RMSE, or tail concordance metrics were generated.
* No real Biogen performance metrics were calculated.
* No fitted estimator serialization or selection manifests were generated.

All remaining artifacts in `manifests/runs/` correspond to synthetic/dry-run test executions (e.g., `test` or `dry_run` operations), which are securely mocked and do not involve real model fitting or target observation.

## 5. Audit the Master-Partition Provenance

* **Existence at commit**: `splits/master_partition.csv` **did not exist** at the execution-ready commit `2f8ce1b6eb88cb9df941d915b2435f755c845ebe`. It was generated dynamically by `run_exec.py` directly referencing the static prefreeze file.
* **Current SHA-256**: `971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a`.

We merged and mapped `splits/master_partition.csv` directly against `reports/SCAFFOLD_PREFREEZE_DRY_RUN_ASSIGNMENTS.csv`. The validation yielded exactly 0 mismatches across the assignments. 
* All expected compounds match.
* Partition assignments match.
* CV-fold assignments match.
* There are no missing, duplicate, or unexpected IDs.

**Count Verifications:**
* **Full partition**: 1,102 rows total.
* **Primary interior cohort (N=731)**:
  * Holdout = 149
  * CV = 582
  * Folds = 115 / 120 / 115 / 117 / 115
  * Zero scaffold overlap enforced identically to the freeze.

**Explanation for Holdout Size Mismatch**:
The full partition dataset contains 1,102 rows, which encompasses the 731 interior observed records, but also includes ambiguous observations, left-censored records, and right-censored records. When partitioned during the dry run, holdout assignments were computed across this broader population resulting in 250 total holdout labels. However, the assertion strictly expected 149 holdout labels because it incorrectly checked the full `partition_df` rather than the subsetted `df_p` interior cohort.

The intermediate file generated by `run_exec.py` and the prefreeze-assignment-derived file possess mathematically identical assignments.

## 6. Git/Provenance State

* **Current HEAD**: `2f8ce1b6eb88cb9df941d915b2435f755c845ebe`
* **Execution-Ready Tag Target**: `2f8ce1b6eb88cb9df941d915b2435f755c845ebe`
* **Tracked Modifications**: Clean (No tracked changes)
* **Untracked Files**:
  * Various mock/test artifacts in `manifests/runs/` and `reports/` created during testing or execution crash initialization.
  * `run_exec.py` (Script used to launch execution)
  * `splits/master_partition.csv` (Materialized safely from prefreeze)

## 7. Classification

PRE_ACCESS_EXECUTION_FAILURE_CONFIRMED
