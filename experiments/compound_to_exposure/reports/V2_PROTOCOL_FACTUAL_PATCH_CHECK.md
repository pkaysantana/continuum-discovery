# V2 protocol factual patch — freeze held

2026-09-18, branch `dmpk-compound-to-exposure`.

The requested factual corrections are saved in `docs/STATISTICAL_ANALYSIS_PREREGISTRATION.md`. The user explicitly retained the unperformed ECFP4/Tanimoto characterisation as a **mandatory pre-freeze requirement** and instructed **not to freeze yet**. Consequently, the SAP remains `PREREGISTRATION_STATUS: PENDING_FINAL_EVIDENCE_CHECKS`. No freeze commit, freeze tag or completed-freeze record was created. No modelling, prediction, performance calculation, TDC execution or v1 performance inspection occurred.

| Document snapshot | SHA-256 |
|---|---|
| SAP before this factual patch, inspected by the earlier evidence reports | `6a29097ace7b01f89dbe00eedfb7781c4dd515113f98e433fd19d5328d5cfaa9` |
| SAP after this factual patch, still pending freeze | `5564fd304cbacb7324fddd678306feb16de67187963b85aebe0df6675c34814e` |

## Corrections completed

- Replaced provisional HLM–HH wording with the verified complete 4×4 matrix, its 94/59/32/2 summary, directionality, two boundary cases and primary/sensitivity Spearman eligibility of 94/96. The same 187 one-to-one ID/structure matches remain explicit.
- Inserted scaffold counts: 712/532 groups, 583/457 singleton groups, exact singleton fractions, largest group sizes 32/14, and the single acyclic compound. Inserted holdout N=149, CV N=582, inner-fold Ns 115/120/115/117/115 and the absence of scaffold overlap. The grouping and deterministic assignment algorithm are unchanged.
- Deferred TDC execution under `TDC_PROTOCOL_NOT_FULLY_SPECIFIED`; no TDC result is required for primary v2 completion. Preserved qualifier stripping and the five structural-reconciliation findings. Any later TDC benchmark requires its own protocol frozen before execution.
- Removed use of two-fold agreement as a utility or decision-relevance threshold. Retained it only as an individual-prediction agreement band; no validated utility threshold is declared.
- Replaced active confirmatory terminology with primary prospective v2 reanalysis evaluation, reserved from v2 tuning. Preserved historical v1 preregistration `fefaf21` (`fefaf215a1a0361470d039238bdf0178e3789410`), subsequent v1 modelling and development of v2 after v1 results existed.
- Made the existing project RDKit/NumPy pins explicit without installing or changing packages.

## Text-only consistency checks

Exact text-block comparisons with the pre-patch SAP passed for representations, scaffold definition and deterministic split steps, master partition policy, hyperparameter selection, metrics, censor-aware evaluation, applicability-domain analysis, residual diagnostics, sensitivity analyses, primary comparison/bootstrap, and failure criteria. The selection-rule heading changed only to clarify that its chronology concerns v2 performance. No model-selection rule or candidate changed.

The preserved primary comparison is MAE(median baseline) minus MAE(selected pipeline), with paired scaffold-cluster bootstrap, B=10,000 and seed=0. The conclusion remains improvement demonstrated only when the lower 95% bootstrap bound exceeds zero; otherwise improvement not demonstrated.

The requested stale-string scan was reviewed manually:

| String/category | Active SAP disposition |
|---|---|
| `PENDING_` | One occurrence: final pending status, intentionally retained because the user kept the pre-freeze requirement. |
| `READY_TO_FREEZE` | Absent. |
| `confirmatory` | Absent. |
| `untouched` | Absent. |
| `decision-relevant` | Absent. |
| `NULL means =` | Absent; the historical correction and explicit rejection of semantic equality are preserved. |
| Provisional HLM–HH counts | Absent; machine-verified counts and table are present. |

All remaining mentions of 0.301/two-fold agreement were reviewed: they describe the individual-prediction band, its descriptive bootstrap interval, or expressly reject a utility interpretation. Historical evidence reports retain their original source-SAP hash and quoted pre-patch wording; they are snapshots, not active execution instructions.

## Remaining requirement and held actions

The pre-freeze distribution of maximum ECFP4/Tanimoto similarity from each holdout compound to the CV pool has not been calculated. Existing scaffold counts do not substitute for it. The requirement remains before freeze, with no permission to change partitions or methods in response to it. This patch adds no analysis and performs no feature calculation.

`PREREGISTRATION_STATUS: FROZEN_FOR_V2_EXECUTION`, the freeze commit, `dmpk-v2-reanalysis-protocol-frozen` tag, and `reports/V2_PROTOCOL_FREEZE_RECORD.md` must wait. The working SAP is saved but not committed by this task. The pending state is deliberate; it is not a completed freeze.

PRE_FREEZE_DECISION_REQUIRED
