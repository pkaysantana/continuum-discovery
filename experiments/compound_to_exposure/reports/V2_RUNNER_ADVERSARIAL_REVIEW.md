# V2 Runner Adversarial Review

## 1. Provenance and Code Identity

- **src/execute_v2.py SHA-256**: `10F27FF95CD523BF7C51D5CEE3673649D581D9BF881D570922A241B514808CAB`
- **tests/test_execute_v2.py SHA-256**: `C6C43482082161A0D1C98A94BD3753A1999991FD6E6E24AEC539F8883504DE40`
- **Frozen SAP Hash**: `cbb86e329fc889dbbf1832d3c83eaa3a909d9846a8b88e85a6ee341d6b572bba` (Unchanged)
- **Tag Verification**: `dmpk-v2-execution-ready` does NOT exist.
- **Git HEAD**: `c67148c62d814357034d4c33db7967c88354f874`

## 2. Test Execution
Tests ran on the dry-run/synthetic pathway. 
- **Passed**: 120
- **Failed**: 0
- **Skipped**: 0

However, adversarial code review reveals that the synthetic tests only verify the presence of the execution ledger on a superficial level without catching underlying architectural leakages.

## 3. Findings

### Finding 1: Execution Ledger Scope Bypass (BLOCKER)
- **Exact Location**: `src/execute_v2.py` in `ExecutionLedger.__init__`
- **Expected Behaviour**: The ledger must durably prohibit a second primary holdout evaluation across the entire project once access has begun.
- **Observed Behaviour**: `self.ledger_file = run_dir / "execution_ledger.json"`. The ledger is scoped strictly to the current ephemeral output directory (`run_dir`).
- **Consequence**: An operator can trivially bypass the entire holdout-access protection by simply invoking `execute_v2.py` with a new unique `run_dir` UUID. Each new run directory generates a fresh, empty ledger, allowing multiple silent adaptive primary evaluations.
- **Minimal Correction**: The `ExecutionLedger` file must be anchored to the project/experiment root (e.g., `experiments/compound_to_exposure/execution_ledger.json`), entirely independent of the specific `run_dir`.

### Finding 2: Lack of Pre-Access Durability (BLOCKER)
- **Exact Location**: `src/execute_v2.py` inside `execute_v2` around the `PRIMARY_HOLDOUT` stage start.
- **Expected Behaviour**: The selected configuration and candidate pipeline must be durably written to disk *before* any primary holdout target is read or evaluated.
- **Observed Behaviour**: The run manifest (containing the selected pipeline, hyperparameters, and CV tie-breaker results) is only kept in memory until the very end of the function, where `json.dump(manifest, ...)` writes it.
- **Consequence**: If the process crashes or an exception is thrown precisely after the `PRIMARY_HOLDOUT` stage starts but before the script exits naturally, the configuration that triggered the failure is lost from memory. The ledger will block reruns (`FAILED_AFTER_ACCESS`), leaving the experiment permanently locked with no record of *what* pipeline failed.
- **Minimal Correction**: Serialize and dump the `manifest` dict containing model-selection results to disk immediately prior to calling `ledger.begin_stage('PRIMARY_HOLDOUT')`.

### Finding 3: Incomplete SAP Secondary Methodology (BLOCKER)
- **Exact Location**: `src/execute_v2.py` Stages 5 (Tail), 6 (Sensitivity A), 7 (Sensitivity B), 8 (HLM_HH), and 9 (Biogen).
- **Expected Behaviour**: The execution runner must implement the exact fold-specific tail concordance pairings, Sensitivity A ambiguous training injection, Sensitivity B reclassification, and Biogen inheritance logic governed by the frozen SAP.
- **Observed Behaviour**: These sections contain literal `# (Mock implementation)` stubs followed immediately by `ledger.complete_stage()`.
- **Consequence**: Running the pipeline for real will bypass all secondary and sensitivity analyses entirely. The protocol is functionally missing from the implementation.
- **Minimal Correction**: Replace all mock stubs with the genuine dataset merging, out-of-sample matching, metric computation, and scaffold-cluster bootstrap execution specified by the frozen SAP.

### Finding 4: Incomplete Tie-Breaker Parameters (IMPORTANT)
- **Exact Location**: `src/execute_v2.py` in the `candidate_results` population block.
- **Expected Behaviour**: Ridge pipelines must supply `alpha` and Random Forest pipelines must supply `min_samples_leaf` and `max_features` to the `tie_break_candidates` function.
- **Observed Behaviour**: The mock parameter grid hardcodes a single dict that supplies dummy hyperparameters, but a genuine `GridSearchCV` object will unpack actual hyperparameters that vary depending on the pipeline family.
- **Consequence**: If real hyperparameter dictionaries do not explicitly contain exactly the keys expected by the tie-breaker, the logic will throw a `KeyError` during real execution before holdout access, requiring a script patch.
- **Minimal Correction**: Ensure the pipeline hyperparameters mapped into candidate dicts correctly handle the differing signature spaces of Ridge vs RF.

## 4. No-Real-Execution Verification
A thorough check confirms no actual models have been fitted using the full AstraZeneca DMPK dataset, and no intermediate or final test-set predictive performance has been calculated or surfaced.

## 5. Conclusion
Due to fundamental bypasses available in the holdout protection ledger and the omission of core secondary analyses from the implementation, the runner is formally rejected.

RUNNER_AUDIT_BLOCKED
