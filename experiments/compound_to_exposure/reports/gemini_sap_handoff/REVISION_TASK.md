# Gemini Pro / Deep Think SAP revision handoff

Use Gemini Pro / Deep Think with the highest reasoning setting available. This is a document-revision task only. Read all attached sources before drafting. Produce the complete replacement text for `docs/STATISTICAL_ANALYSIS_PREREGISTRATION.md`; do not implement code.

Do not run models, calculate descriptors or fingerprints, create splits, search hyperparameters, inspect performance, modify raw data, or alter the scientific audit. Procedures described below are future implementation specifications, not permission to execute them now.

## Confirmed scope: prospective new-analysis amendment

The original request described this as a final pre-performance SAP and asked for a statement that no modelling had occurred. That statement conflicts with the actual history of the requested branch, `dmpk-compound-to-exposure`.

The branch contains these earlier commits (commit metadata only; no performance files are included or need to be inspected):

- `98e43be`: run frozen primary HLM models, 2026-09-17T18:26:43+01:00.
- `65eac85`: reproduce TDC microsome benchmark, 2026-09-17T19:36:57+01:00.
- `486a0ff`: analyse paired HLM and hepatocyte clearance, 2026-09-17T19:44:09+01:00.
- `df8291f`: replicate HLM modelling in Biogen dataset, 2026-09-17T21:40:32+01:00.
- `4640ea7`: audit correction checkpoint, later on 2026-09-17.

Claude's adversarial review was committed separately as `33f7e5aedabfb5ef0aa3d56a930cb5f82a5a4052` on `worktree-censoring-memo-metadata-audit` on 2026-09-18. Its prospective statements are part of the review's original text, not independent proof of this branch's chronology. The working SAP draft remains uncommitted.

The user has now explicitly chosen: **"New analysis amendment with prior modelling disclosed."** Produce a prospective SAP amendment for that new analysis. The chronology scope is resolved; prior modelling must be disclosed, not erased.

Do not assert that no model was ever fitted, that no performance had been generated, that the cohort reversal predates all modelling, or that a future holdout is historically untouched. A current revision cannot retrospectively establish preregistration for existing results. You may state that this evidence-resolution and document-preparation work ran no models and inspected no performance. Freeze the new analysis before its new fits, selection and evaluation, while clearly separating that prospective commitment from the existing modelling history. A holdout untouched by the new pipeline-selection process is not necessarily data never previously evaluated; disclose this limitation on confirmatory interpretation. Do not copy the review's pre-performance assertions as statements about the entire project.

## Source hierarchy

1. Explicit frozen scientific decisions in this task.
2. Verified audit evidence, including the new HLM-HH qualifier cross-tabulation.
3. `docs/ADVERSARIAL_PREREGISTRATION_REVIEW.md` (Claude's exact review).
4. `docs/DATASET_SELECTION_MEMO.md`.
5. `docs/CENSORING_POLICY_MEMO.md`.

The earlier SAP is the text to revise, not an authority overriding these sources. `INPUT_MANIFEST.json` records the origin, SHA-256 and byte size of each supplied input. The exact review is supplied from its separate commit; no merge or cherry-pick was performed.

**Draft-version update during packaging:** the working SAP was independently updated to a document titled `v2 Reanalysis Protocol` while this handoff was being prepared. `inputs/docs/STATISTICAL_ANALYSIS_PREREGISTRATION.md` contains that latest snapshot and is the revision target. `inputs/docs/STATISTICAL_ANALYSIS_PREREGISTRATION_PRE_HANDOFF_SNAPSHOT.md` preserves the earlier draft used at the start of this task. Read both, apply the review to remaining defects in the latest target, and retain correct amendments already made. Do not mistake a finding about the earlier draft for a finding that necessarily still applies to the current version. Both versions are uncommitted source snapshots, not a newly frozen SAP.

## Frozen scientific decisions

- Primary assay: CHEMBL3301370.
- Primary point-regression cohort: N=731, NULL relation and strictly 3 < reported CLint < 150, before log transformation.
- 274 explicit `<3` records are left-censored; 84 explicit `>150` records are right-censored.
- 13 NULL-at-3 records are boundary-ambiguous and excluded from primary regression.
- 3 and 150 are working censoring boundaries. Formal LLOQ/ULOQ status remains unresolved.
- NULL is not asserted to mean equals in ChEMBL generally. The interior cohort is an operational analytical assumption, not a change to the frozen field-audit conclusion.
- No IVIVE, raw HLM/HH differences or ratios, physiological scaling, or in-vivo PK claims.

## Newly verified pairing evidence

Status order is INTERIOR_OBSERVED, BOUNDARY_AMBIGUOUS, LEFT_CENSORED, RIGHT_CENSORED. Rows are HLM; columns are HH:

| HLM / HH | INTERIOR_OBSERVED | BOUNDARY_AMBIGUOUS | LEFT_CENSORED | RIGHT_CENSORED |
|---|---:|---:|---:|---:|
| INTERIOR_OBSERVED | 94 | 0 | 26 | 5 |
| BOUNDARY_AMBIGUOUS | 2 | 0 | 0 | 0 |
| LEFT_CENSORED | 20 | 0 | 31 | 0 |
| RIGHT_CENSORED | 8 | 0 | 0 | 1 |

- Both interior: **94**. This is the ordinary quantitative correlation cohort under the primary policy; no correlation has been computed in this evidence task.
- One interior, one censored: **59** (31 interior HLM / censored HH; 28 censored HLM / interior HH).
- Both censored: **32** (31 left/left, 1 right/right).
- Boundary-ambiguous: **2**, both HLM NULL-at-3 with interior HH.
- `CHEMBL271012`: HLM activity 14769803, NULL, 3.0; HH activity 14763401, NULL, 30.12.
- `CHEMBL552512`: HLM activity 14769805, NULL, 3.0; HH activity 14758940, NULL, 3.4.
- Including these two as exact-3 solely for the specified sensitivity would give **96** pairs.
- The molecule-ID and frozen strict-structure matched sets are identical, each contains **187**, and both remain one-to-one. No ambiguous mapping exists.
- Values retain their different native units. No paired differences, ratios or scaling were calculated.

The full paired evidence is in `reports/HLM_HH_QUALIFIER_CROSSTAB.json`; its Markdown companion explains the definitions and verification.

## Mandatory revision requirements

1. **Supersession history.** Correct the false claim that the older censoring memo assumed NULL meant equals. It explicitly rejected semantic equality, froze N=744 primary, defined N=731 as sensitivity S1, and prohibited S1's promotion to primary. State that the present SAP reverses that assignment for the new analysis. Preserve the prohibition on choosing cohorts by performance. Disclose earlier modelling and describe this decision as prospective for the new analysis, not as predating all modelling. Also record other actual supersessions, including the classifier descoping required by review I3, rather than claiming only one clause changed if more did.

2. **Primary estimand.** Define out-of-scaffold predictive absolute error for log10 reported apparent HLM CLint, conditional on membership of the primary interior cohort and the frozen pipeline/design. Do not describe it merely as a conditional expected value or extend it to an unscreened population.

3. **Metrics and baselines.** Primary: MAE on log10(CL_int), with the training-fold median constant baseline. Secondary: RMSE, Spearman, coefficient of determination R-squared, and proportion within two-fold. Follow review B2: RMSE is compared with the training-fold mean constant, never the median constant. The mean constant is a metric-specific reference, not an added learned candidate. The two-fold band is exactly plus/minus log10(2), not an assay noise floor or a significance threshold.

4. **Scaffold validation.** Copy the exact review B5/B6 design, including the final 20% target for scaffold holdout, Bemis-Murcko implementation, largest-fragment rule for grouping only, `__ACYCLIC__` grouping, SHA-256 ordering, oversize-group handling, five persisted inner folds, tie rules, and single master partition shared across analyses. No target-informed optimisation. Do not replace precise rules with examples. If B5's use of 731-cohort group counts conflicts with B6's statement that assignment is purely structural, identify that conflict explicitly; do not silently claim the two statements are identical or invent a replacement algorithm.

5. **Censored observations.** Remove any accuracy rule requiring predictions at or beyond 3/150. Use review B3's lower/upper Mann-Whitney tail concordance, exact tie scores, same-model/same-held-out-fold eligibility, pair-count pooling, undefined-case handling, scaffold bootstrap, and fixed novelty-stratum reporting. Include the review's one-sided boundary-violation loss only as a within-model-family descriptive metric, never for model selection or cross-family comparison. Boundary values are not exact continuous labels.

6. **Representations.** Freeze exactly the 12 descriptors in review B7: MolWt, MolLogP, MolMR, TPSA, NumHDonors, NumHAcceptors, NumRotatableBonds, RingCount, NumAromaticRings, NumAliphaticRings, FractionCSP3, HeavyAtomCount. Copy the exact fold-local imputation, Ridge scaling and zero-variance rules; Random Forest receives unscaled descriptors. Copy the binary Morgan/ECFP4 definition and all parameters specified by the review. No extra representations or concatenation.

7. **Models.** Only the median constant primary baseline, Ridge regression and Random Forest regression, with the exact representation/model pairings in review B9. No neural networks. Retain the RMSE-specific mean reference required by B2 without turning it into a new pipeline-selection candidate.

8. **Hyperparameters.** Use the exact exhaustive search procedure, parameter grids and estimator settings in review B8. Replace all open-ended search language. Every fitted preprocessing step stays inside each training fold.

9. **Selection and final evaluation.** Copy review B9's deterministic selection and tie-breaking sequence exactly. Only the finally selected learned pipeline receives the primary untouched-holdout evaluation, together with the prespecified constant references. Explicitly distinguish prespecified sensitivity refits from comparing alternative learned candidates on the final holdout. Report the final result regardless of outcome.

10. **Statistical comparison.** Copy the scaffold-cluster bootstrap procedure and decision criterion in review B10, comparing held-out MAE against the median baseline. Keep statistical uncertainty, effect size and scientific usefulness separate. Do not invent an unfrozen practical-utility threshold.

11. **Failure language.** Limit any negative conclusion to these preregistered representations, models, dataset and out-of-scaffold design failing to demonstrate useful improvement. Do not claim to falsify structural predictability generally.

12. **Applicability domain.** Use nearest-training-compound Tanimoto on the frozen ECFP4 fingerprint for every model, including descriptor models. Copy the review's exact bins and small-stratum rule. No post-hoc threshold or altered bin edges.

13. **Residuals.** Follow review I6: signed residuals, absolute errors, prediction magnitude, structural similarity, heteroscedasticity, fixed tercile summaries, boundary compression and the ten largest failures. Specify residual sign consistently. No inferential normality testing. Do not create optional implementation choices where the final SAP must be determinate.

14. **HLM-HH secondary analysis.** Use the verified four-status cross-tab above and **N=94** for the primary ordinary quantitative/rank correlation. Exclude the two ambiguous HLM cases; the exact-3 sensitivity has N=96. Censored pairs are never ranked as exact boundary values. Any censored-pair analysis is separate, descriptive/exploratory, and uses the qualifier contingency counts. Preserve the boundary-ambiguous category rather than silently merging it into an observed or censored class. No raw difference, ratio or physiological scaling. Do not strengthen a range-restriction caveat into an unsupported guaranteed direction of correlation bias; identify any conflict in the review rather than presenting an unsupported mathematical claim as established.

15. **TDC.** Reproduce the official TDC benchmark harness's split and evaluation convention as shipped. Keep it entirely separate from censor-aware science, using its own split and metric/seed convention. No TDC-derived selection informs the science track. If the exact harness version or prescribed seeds cannot be established from the supplied sources, explicitly identify the missing freeze detail instead of guessing.

16. **Biogen.** Exploratory within-dataset replication: all 3,087 populated labels as shipped, plus the 2,129-value floor-excluded sensitivity, always reported together. The 958 values at 0.675686709 remain unresolved, neither declared exact nor censored. No re-logging or conversion to mimic AZ, no pooled external-test claim, and no comparison of native error magnitudes across incompatible units. Copy the review's separate-partition policy.

17. **Sensitivities.** Preserve primary N=731, NULL-at-3 exact-3 sensitivity, and NULL-at-3 left-censored sensitivity. All reuse the master structural partition. Never choose between them based on performance. Describe exactly what is refitted, evaluated and reported in each; do not use sensitivity results to replace the primary result.

Apply all remaining BLOCKER, IMPORTANT and MINOR corrections in Claude's review, including the explicit three-class-classifier descoping, split-severity reporting, version pins, and named/hash-identified audit evidence. Do not include existing modelling results or performance metrics in the SAP.

## Output requirements

Return a self-contained replacement `docs/STATISTICAL_ANALYSIS_PREREGISTRATION.md`, suitable for implementation without additional methodological discretion once all freeze blockers are resolved. Do not output code, execute an analysis, change supplied sources or produce a modelling result.

No phrases like `e.g.`, `such as`, `grid or random search` or `approximately` where an exact frozen decision is required. Copy review implementation details accurately. Flag any material contradiction or missing exact setting; do not disguise it with discretionary wording.

At the end include a table named **FROZEN_ANALYSIS_DECISIONS**, containing:

- population;
- target;
- representation;
- model;
- split;
- tuning;
- primary metric;
- baseline;
- censor-aware metric;
- model-selection rule;
- final evaluation rule;
- uncertainty procedure.

The user's requested final status is `PREREGISTRATION_STATUS: READY_TO_FREEZE`, scoped to the **new analysis amendment with prior modelling disclosed**. The user has resolved that scope. Do not falsely certify readiness if a consequential methodological contradiction or missing exact setting still prevents implementation; identify any such blocker explicitly. A handoff, a newly written document and a model's review cannot themselves establish that the historical project was pre-performance. The final status must never be presented as retroactive preregistration of existing results.

Finish the task after reporting the document and any unresolved freeze blockers. Do not proceed to implementation.
