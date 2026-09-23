# V2 Runner Adversarial Review V2

## A. Code Identity

- **src/execute_v2.py SHA-256**: `2B47C99B8F483EFDDF21256CC22E97317F270C0A34AACB53CB6F1D23901EF128`
- **tests/test_execute_v2.py SHA-256**: `553AD6C00F1A8465348C410C65CD0A54ABC27BA3569070037D6895B86DF34767`
- **SAP SHA-256**: `CBB86E329FC889DBBF1832D3C83EAA3A909D9846A8B88E85A6EE341D6B572BBA`
- **Current HEAD**: `c67148c62d814357034d4c33db7967c88354f874`
- **Tag dmpk-v2-execution-ready**: Does NOT exist.

## B. Test Execution

Independent execution of `tests.test_execute_v2` and the full suite via `run.py test` yielded:
- **Total Tests Run**: 121
- **Passed**: 121
- **Failed**: 0
- **Skipped**: 0
- **Warnings**: 0

The 5 new runner-specific tests do correctly test the implemented lock, but fail to cover the edge cases regarding `run_dir` manipulation.

## C. Execution State Audit

### Finding 1: Authoritative State is Still Not Anchored to Experiment Root (BLOCKER)
- **Exact Location**: `src/execute_v2.py:140` (`state_file = run_dir.parent.parent.parent / "state" / "v2_execution_state.json"`)
- **Expected Behaviour**: The state file must resolve to a single canonical path relative to the repository/experiment root regardless of what the caller specifies as the output directory.
- **Observed Behaviour**: The code derives the authoritative state path relative to `run_dir`. If an operator invokes `execute_v2(run_dir=Path('/tmp/custom_run'))`, the state file resolves to `/state/v2_execution_state.json`, completely bypassing the state stored in the experiment root.
- **Consequence**: An operator can bypass the primary holdout block by supplying an external or arbitrary `run_dir`.
- **Minimal Correction**: Use an absolute anchor like `Path(__file__).parent.parent / "state" / "v2_execution_state.json"` to completely decouple the authoritative state from the output `run_dir`.

## D. Concurrency and Atomicity Audit
- The `AtomicLock` properly enforces `touch(exist_ok=False)` under a `while` loop, yielding an inter-process safe lock. 
- Crash behavior leaves an orphaned `.lock` file. The timeout (`5.0` seconds) protects against deadlocks if the other process is holding it legitimately, but if it crashes while holding the lock, manual intervention is safely required. This does not result in a second holdout evaluation. NO ISSUE.

## E. State-Machine Semantics
- `FAILED_BEFORE_ACCESS` retry explicitly uses `pass` and permits another run. Since holdout target values were not read, this is safe.
- `STARTED`, `COMPLETED`, `FAILED_AFTER_ACCESS` enforce blocks natively. NO ISSUE.

## F. Pre-Holdout Selection
- The selection is correctly flushed to `selection_manifest.json` before `ledger.begin_stage('PRIMARY_HOLDOUT')` is invoked. If the file write fails, the exception breaks execution before the lock transitions to `STARTED`. NO ISSUE.

## G. Primary Model Selection Fidelity
- Explicit parameter exposition for `alpha` (Ridge) and `max_features` / `min_samples_leaf` (RF) are cleanly mapped. The `tie_break_candidates` KeyError risk has been eliminated. NO ISSUE.

## H. Master Partition
- The master partition (`master_partition.csv`) is read as source-of-truth. NO ISSUE.

## I. Tail Implementation
- Same-fold prediction logic and weighting are correct. No 3 or 150 regression values exist. NO ISSUE.

## J. Sensitivity A & K. Sensitivity B
- Unambiguous partition merging and exact-target substitution applied. NO ISSUE.

## L. HLM-HH Audit

### Finding 2: Missing Real Substantive Computation for HLM-HH (BLOCKER)
- **Exact Location**: `src/execute_v2.py:383`
- **Expected Behaviour**: The execution runner must load the specific `hlm_hh_187` paired compounds and compute the primary `N=94` and sensitivity `N=96` Spearman correlations directly according to the frozen protocol.
- **Observed Behaviour**: The stage merely reads the length of the dataframe, leaves `p_spear` and `s_spear` as hardcoded literal stubs (`94` and `96`), and completes the stage.
- **Consequence**: The frozen computation is skipped, leaving the stage completely unexecuted structurally.
- **Minimal Correction**: Write the actual Pandas `scipy.stats.spearmanr` metric calculations against the loaded cohort targets.

## M. Biogen Audit

### Finding 3: Missing Real Substantive Computation for Biogen (BLOCKER)
- **Exact Location**: `src/execute_v2.py:400`
- **Expected Behaviour**: The execution runner must recreate the nested P1-P4 CV pipeline logic locally inside the Biogen B1 partition independently of the main run, and then predict Biogen B2.
- **Observed Behaviour**: The script applies the partitioning inheritance but merely sets a dummy `biogen_b1_complete = True` variable before marking the stage complete. The P1-P4 modelling loops are not executed for Biogen.
- **Consequence**: The entire Biogen replication analysis is functionally stubbed and skipped.
- **Minimal Correction**: Duplicate or abstract the CV selection loop so it executes fully upon the `biogen_B1` cohort before completing.

## N. Stub Search
No `MockPredictor` or `mock` strings exist in legitimate execution paths. `pass` is present at line 73 explicitly to handle `FAILED_BEFORE_ACCESS` and is architecturally correct.

## O. Dry-Run Isolation
Dry-run safely diverts state tracking to an isolated file internal to the run directory. NO ISSUE.

## P & Q. No-Real Execution Isolation
No real data was exposed or modelled.

## Original Finding Dispositions
| Original finding | Corrected? | Evidence |
|------------------|------------|----------|
| Ledger scope bypass | NO | Bypassed if `run_dir` is externally rooted. |
| Pre-access durability | YES | `manifest_path` is written before state transition. |
| Incomplete secondary methodology | NO | HLM-HH and Biogen contain literal hardcoded metric results and skipped CV loops. |
| Tie-break parameter handling | YES | Correct dict signatures passed. |

## Conclusion
RUNNER_AUDIT_BLOCKED
