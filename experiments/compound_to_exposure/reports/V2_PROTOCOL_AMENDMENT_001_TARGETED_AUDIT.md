# Protocol Amendment 001 Targeted Final Audit

| Check | Verdict | Evidence |
|---|---|---|
| **Amendment provenance** | PASS | Amendment hash `8B0DD8BB9D97409DB53A14981777F086EF74A7EABD7D44757B9152F62C5A4DF5`, commit `2b4fc365e258e55abdaa3db07d213b42f4cd70e5`, and tag `dmpk-v2-protocol-amendment-001-biogen-frozen` all match identically. Original SAP hash remains `cbb86e329fc889dbbf1832d3c83eaa3a909d9846a8b88e85a6ee341d6b572bba`. Original tag unchanged. Freeze record is accurate. `dmpk-v2-execution-ready` does not exist. |
| **Amendment prospective** | PASS | `manifests/runs/` and `state/` verified manually. Only `.started.json` and `.json` dry-run artifacts exist. No real `.fit()`, predictions, or performance files are present. |
| **B1 full selection** | PASS | `execute_v2.py` isolates B1 data, iterates its own `b1_cv_folds`, computes `b1_candidate_results` using `mean(fold_maes)` on frozen grids, and formally determines `b1_best_candidate` independently using standard P1-P4 implementations without AstraZeneca cross-contamination. |
| **B2 no reselection** | PASS | B2 does not initiate any hyperparameter search loop. The exact assignment `p_id = b1_best_candidate['pipeline_id']` and `base_pipe = pipelines[p_id][0]` retrieves B1's selection directly. |
| **B2 fixed-config refit** | PASS | B2 runs `.fit()` with `base_pipe` specifically using only `b2_cv_folds` (B2 training observations). |
| **B2 partition inheritance** | PASS | Proven structurally: `df_bio2.merge(df_bio1[['chembl_id', 'partition', 'cv_fold']], on='chembl_id', how='left')` is directly used with a rigorous `assert len(df_bio2[df_bio2['partition'].isna()]) == 0`. B2 cannot regenerate a split. |
| **B1 unaffected by B2** | PASS | B2 logic is strictly strictly downstream of B1 completion in `execute_v2.py`. |
| **Runner safety regression** | PASS | `ExecutionLedger` paths, `AtomicLock`, Tail constraints, and Sensitivity bounds are unchanged. The amendment uniquely isolated Biogen logic as specified. |
| **No real execution yet** | PASS | No real runs, predictions, metrics, or logs found. |

### Test Execution Proof
- Runner-specific and full experiment suite run manually: `Ran 125 tests in 42.043s`
- Passed: `125`
- Failed: `0`
- Skipped: `0`
- Warnings: `0`

AMENDMENT_TARGETED_AUDIT_PASS
