# V2 Execution 001 Post-Access Forensics

## 1. Authoritative Protected Run
* **Run ID:** `2026-09-18T215009395468_0000-4c110e67` (UUID: `220bc125-141f-41ca-964c-525d9e3e075e`)
* **Run Directory:** `manifests/runs/2026-09-18T215009395468_0000-4c110e67`
* **Execution Commit:** `31693d204420fa547a96079ff11988058d133406`
* **Start Timestamp:** `2026-09-18T21:50:09.395468+00:00`
* **End/Interruption Timestamp:** The last completed deterministic stage (HLM_HH) finished at `2026-09-18T22:00:42.848215+00:00` before BIOGEN began. No files were modified for the run after this time window.
* **State File:** `state/v2_execution_state.json`
* **Selection Manifest:** Persisted correctly (`selection_manifest.json` in run directory).
* **Primary Prediction File:** Persisted correctly (`primary_holdout_predictions.csv` in run directory).
* **Metrics Files:** Not fully persisted (the global `results/` was not updated). The manifest only stored `mean_mae` and `mae`.
* **Tail Outputs:** Incomplete/Not Persisted (no files written).
* **Sensitivity Outputs:** Incomplete/Not Persisted (no files written for Sensitivity A or B).
* **HLM-HH Outputs:** Partially preserved in `v2_execution_state.json`, but qualifier contingency not persisted.
* **Biogen Partial Artifacts:** None. Biogen started but did not persist any artifacts.
* **Logs/Traceback:** No dedicated log output file was captured for the run execution other than standard console logs and the `.started.json` file.

## 2. Task 126 Verification
* **Task 126 Run ID:** `2026-09-18T221459876805_0000-12e19f8d`
Task 126 started at `2026-09-18T22:14:59.876805+00:00` and created a `.started.json` file and an empty run directory.
* **Reached PRIMARY_HOLDOUT:** No.
* **.fit() occurred:** No evidence of it completing.
* **.predict() occurred:** No.
* **Selection Manifest Generated:** No.
* **Prediction/Metric Artifact Written:** No.
* **Changed Authoritative Stage:** No. The `v2_execution_state.json` was not modified after `22:00:42`.
**Conclusion:** Task 126 did not create a second protected evaluation. No provenance violation occurred.

## 3. Primary Result Validation
* **`selection_manifest.json` exists:** Yes.
* **Selected pipeline/configuration was persisted before protected access:** Yes, P3 was selected with specified hyperparameters.
* **Primary prediction artifact exists:** Yes.
* **Exactly 149 holdout observations are present:** Yes (149 rows of data + header).
* **Each holdout ID appears once:** Yes.
* **Selected-model predictions are present:** Yes, the `predicted` column exists.
* **Baseline predictions are present:** No, baseline predictions were not persisted.
* **No nonselected P1–P4 holdout predictions exist:** Yes, only the single prediction column is present.

### Recomputed Summary Metrics (Deterministically from Persisted Artifacts):
* **MAE:** 0.2956
* **Median-baseline MAE:** 0.3514
* **Δ:** -0.0558
* **RMSE:** 0.3692
* **Spearman:** 0.4368
* **R²:** 0.2005
* **Within ±log10(2):** 0.5705 (57.05%)
* **Scaffold-bootstrap interval for Δ:** NOT RECOVERED (Requires exact re-execution which was forbidden).

## 4. Completed Secondary Stages
* **Tail:** INCOMPLETE (No C_L, C_U, boundary-violation summaries, or uncertainty outputs persisted).
* **Sensitivity A:** INCOMPLETE (No outputs persisted).
* **Sensitivity B:** INCOMPLETE (No outputs persisted).
* **HLM–HH:** INCOMPLETE (State file lists N=94 primary, N=96 sensitivity, but the qualifier contingency output is missing/not persisted).

## 5. Biogen Interruption
* **Progress:** Biogen execution `STARTED` according to `v2_execution_state.json` but no artifacts were written.
* **B1 model selection completed:** No.
* **B1 predictions/metrics persisted:** No.
* **B2 started:** No.
* **B2 predictions/metrics persisted:** No.
* **Exact last completed deterministic step:** HLM_HH.
* **Any partial Biogen artifact complete enough:** No partial artifacts exist.
**Classification:** `INCOMPLETE_AFTER_PROTECTED_EXECUTION`

## 6. Analysis Classification
* **Primary:** `VALID_COMPLETED_WITH_RECOVERED_METRICS_FROM_PERSISTED_PREDICTIONS`
* **Tails:** `INCOMPLETE`
* **Sensitivity A:** `INCOMPLETE`
* **Sensitivity B:** `INCOMPLETE`
* **Applicability-domain analysis:** `INCOMPLETE`
* **HLM–HH:** `INCOMPLETE` (Missing contingency tables)
* **Biogen B1:** `INCOMPLETE`
* **Biogen B2:** `INCOMPLETE`

## 7. Provenance Preservation
Hashes of all protected-run artifacts:
* `manifests/runs/2026-09-18T215009395468_0000-4c110e67.started.json`: `2e30562c0d04434eb7e29ee5668f810533a894231be03f96b72d3ca00b492289`
* `manifests/runs/2026-09-18T215009395468_0000-4c110e67/selection_manifest.json`: `fea8a4c9c4d78b963669d8ee467a1276cabc9affd3efecb62716e9dcf4fe9efb`
* `manifests/runs/2026-09-18T215009395468_0000-4c110e67/primary_holdout_predictions.csv`: `af427726da8f0c65741e32b0020d13141a3f4566f40e9c313adc88c88f7fa821`
* `state/v2_execution_state.json`: `adaf8c5cd7d7aa2e2c3ac9409df93f96ed3910a206335c58afd80c515c99d53a`
