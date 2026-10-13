# Evidence status key: what is verified, what is reported-only, what never ran

Documentation-only index. It adds no result and changes no frozen record. Where
this file and a frozen report disagree about *status*, this file is authoritative
about status and the frozen report remains authoritative about its own values.
No frozen report was edited to produce this index.

## Classes

| Class | Meaning | How a reader can check it |
| --- | --- | --- |
| **VERIFIED-ARTEFACT** | Executed, and the outputs are committed here | Open the artefact and recompute from it |
| **REPORTED-ONLY** | Executed on a local workstation; the numbers survive only as transcriptions into committed reports, because the run outputs were never committed | Cannot be recomputed from this repository. Treat as credible but unverifiable here |
| **NOT-EXECUTED** | Implemented and tested against synthetic data only; gate closed | Check the gate/state file named below |
| **DEFECT-AFFECTED** | Executed, but a code defect changes what the number means | Read the defect note before quoting the number |

## Regression and classification results

| Result | Class | Evidence |
| --- | --- | --- |
| Dataset counts: 1,102 source rows; 731 interior; 274 left-censored; 84 right-censored; 13 boundary-ambiguous; 582 CV / 149 holdout interior; 250-record protected holdout block | **VERIFIED-ARTEFACT** | Recountable from `data/interim/CHEMBL3301370_rows.csv` (1,102 data rows) and `splits/master_partition.csv` (1,102 rows; `status` and `partition` columns) |
| V1 frozen primary models, N=744 grouped scaffold CV: RF/Morgan MAE 0.3255, RMSE 0.3982, R2 0.1838, Spearman 0.4172; median baseline MAE 0.3759 | **VERIFIED-ARTEFACT** | `results/primary_v1/METRICS.json` plus `REGRESSION_PREDICTIONS.csv` (6,612 prediction rows), commit `98e43be` |
| V1 three-class classification macro-F1 0.481 vs 0.269 majority baseline | **VERIFIED-ARTEFACT** | `results/primary_v1/` |
| TDC `Clearance_Microsome_AZ` test split N=221, Ridge/Morgan Spearman 0.499 | **VERIFIED-ARTEFACT**, but *not* independent external validation (shares the AZ source) | `results/tdc_benchmark_v1/`, `splits/TDC_OFFICIAL_SPLIT.csv` |
| HLM vs human hepatocyte pairing: N=187 category agreement 68.45%; N=96 Spearman 0.486 | **VERIFIED-ARTEFACT** | `results/hlm_hh_pairing_v1/` |
| Biogen replication N=3,087 Spearman ~0.55 | **VERIFIED-ARTEFACT** with unresolved caveats (958-value minimum pile-up; undefined native log base) | `results/biogen_replication_v1/`, caveats in `README.md` and `FINAL_SCIENTIFIC_SUMMARY.md` |
| 20-seed GroupShuffleSplit medians: regression R2 ECFP4 0.2105 / R1 0.1388 / R1+2 0.1667; classification ROC-AUC 0.7616 / 0.7685 / 0.7860; paired ECFP4 - R1 +0.0542, p=0.0016 | **VERIFIED-ARTEFACT** | `reports/FROZEN_RESULTS.md` section 4, commit `925e71e` |
| Inter-laboratory reproducibility, 34 overlapping compounds: mean absolute difference 0.1601 log10, SD 0.4907 | **VERIFIED-ARTEFACT** | `reports/FROZEN_RESULTS.md` |
| **V2 protected holdout, 149 records: MAE 0.29558, RMSE 0.36924, R2 0.20050, Spearman 0.43683, Pearson 0.4612, within-twofold 57.05%, training-median baseline MAE 0.35135 (delta 0.0558)** | **REPORTED-ONLY** and **DEFECT-AFFECTED** | See both notes below |
| V2 scaffold-bootstrap CI for delta, [0.02275, 0.09453] | **REPORTED-ONLY**, provenance explicitly unresolved | `reports/V2_EXECUTION_001_POST_ACCESS_FORENSICS.md` records the interval as NOT RECOVERED, since recovery would require forbidden re-execution |

### Note 1: why the V2 holdout metrics are REPORTED-ONLY

The protected run is `2026-09-18T215009395468_0000-4c110e67` (execution commit
`31693d204420fa547a96079ff11988058d133406`). Its `.started.json` receipt, its
`selection_manifest.json` and its `primary_holdout_predictions.csv` are **not
tracked in this repository** on any branch: `manifests/runs/` contains 32 tracked
`*.json` receipt files and no run subdirectories at all. The metrics therefore
exist here only as values transcribed into four committed reports
(`V2_EXECUTION_001_RECOVERED_RESULTS.md`,
`V2_EXECUTION_001_POST_ACCESS_FORENSICS.md`,
`V2_FINAL_SCIENTIFIC_RECORD_RECONCILIATION.md`, `reports/FROZEN_RESULTS.md`),
where they agree to four decimal places. They cannot be recomputed from this
repository. Recovery and verification options are in
`reports/V2_ARTIFACT_RECOVERY_PLAN.md`.

### Note 2: why they are also DEFECT-AFFECTED

`src/execute_v2.py` selects the feature matrix with `'r1' in p_id` in both the CV
loop and the final fit, while pipeline IDs are `P1`-`P4`. The test is false for
every ID, so all four candidates were evaluated and fitted on ECFP4 (Morgan
radius 2, 2,048 bits) and no candidate was ever evaluated on the R1 descriptor
panel. The recorded selection of a descriptor pipeline is therefore mislabelled:
the stored holdout predictions are ECFP4-based. `selection_manifest.json`
hyperparameters were recorded but not applied. This is the same defect already
recorded in `reports/FROZEN_RESULTS.md` ("Pipeline selection defect") and tagged
`V2_PRIMARY_SELECTION_PROVENANCE_COMPROMISED` in
`reports/V2_FINAL_SCIENTIFIC_RECORD_RECONCILIATION.md`.

Consequence for any downstream use: these numbers may be described as a
single-shot scaffold-holdout result for an ECFP4 random forest. They may **not**
be attributed to a physicochemical-descriptor model, and they do not support a
descriptor-versus-fingerprint comparison. The artefact-backed comparison for that
question is the 20-seed table in `reports/FROZEN_RESULTS.md`.

## Stages that started but produced no artefacts

All **NOT-EXECUTED** / incomplete, per `reports/V2_EXECUTION_001_POST_ACCESS_FORENSICS.md`:
censored tail models C_L and C_U; Sensitivity A; Sensitivity B; applicability-domain
analysis; the HLM-HH qualifier contingency output; Biogen B1/B2 (started, no artefacts
persisted). Baseline predictions were not persisted. Task 126 created a `.started.json`
and an empty run directory and produced no second evaluation.

## V3A and GSK development work

| Item | Class | Gate evidence |
| --- | --- | --- |
| V3A quantile-regression / conformalised prediction (QRF, CQR, Gate 11) | **NOT-EXECUTED** | `state/v3a_execution_state.json`: `state: PREEXECUTION_IMPLEMENTED_NOT_RUN`, `scientific_execution_allowed: false`, `production_model_fit_to_real_outcomes: false`, `independent_audit_recorded: false`; requires `--execute-scientific-analysis` |
| `application_development/gsk_clearance/` extractor, harness, execution and provenance layers | **NOT-EXECUTED** | `application_development/gsk_clearance/execution_gate.json`: `status: NOT_READY`, `filesystem_isolation: NOT_VERIFIED`, `memory_limit: NOT_VERIFIED`, no approval reference and no receipt. Its README states NO-GO for real-data modelling |

No uncertainty-quantification result, conformal interval or GSK-development model
result exists in this repository. Tests covering these layers are synthetic-data
tests; passing them is evidence about the code, not about any compound.

Attribution note for V3A: commit `2a24fdf` (+1,798 / -32 lines across
`src/v3a_runner.py`, `src/v3a_qrf_weights.py` and two test files) is authored by
Copilot. The V3A uncertainty implementation is not single-author work.
