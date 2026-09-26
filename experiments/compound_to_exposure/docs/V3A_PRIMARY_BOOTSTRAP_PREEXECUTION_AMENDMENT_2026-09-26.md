# V3A Primary Bootstrap Pre-Execution Amendment

**Date:** 2026-09-26  
**Status:** PRE-EXECUTION PROTOCOL AMENDMENT

## 1. Audit trail

**Trigger:** An independent read-only protocol audit found that the frozen SAP does not specify whether primary bootstrap replicates use fixed original retention/random selections or recompute those selections inside each resampled cohort.

**Result knowledge at amendment:** No real V3A scientific result is available.

The primary bootstrap execution semantics were not fully specified by the original SAP. This amendment resolves that pre-execution ambiguity; it does not rewrite the original SAP or imply that the original text already specified the procedure below.

| Item | Modified? |
|---|---|
| Primary point-estimate formula | NO |
| Primary model | NO |
| Primary cohort | NO |
| Primary folds | NO |
| Primary predictions/uncertainties | NO |
| Primary bootstrap execution semantics | YES |

## 2. Unchanged primary estimand and point estimate

The primary point estimand remains exactly:

```text
REL_BENEFIT_80 =
(RMSE_RANDOM80 - RMSE_QRF80) / RMSE_RANDOM80
```

The primary point-estimate machinery remains the N744 exact quantitative cohort, original five outer scaffold folds, frozen ECFP4 Random Forest, frozen out-of-fold RF predictions, frozen QRF-width uncertainty, fold-local 80% QRF retention, and 10,000 matched-random primary draws with seed `20260923`.

This amendment does not change the primary point estimate. It clarifies only how bootstrap replicates are constructed and evaluated.

## 3. Bootstrap resampling unit and strata

For each bootstrap replicate \(b\), resample independently within each **original outer fold** \(f\):

1. Identify the unique Bemis–Murcko scaffold clusters represented in that fold.
2. Sample scaffold clusters with replacement, drawing exactly as many scaffolds as the number of unique scaffold clusters originally present in that fold.
3. Include all compounds belonging to each sampled scaffold occurrence.
4. If a scaffold is drawn \(m\) times, include every compound from that scaffold \(m\) times in the bootstrap row-occurrence multiset.

Bootstrap multiplicity is real multiplicity in the evaluation sample. Repeated scaffold draws must not be collapsed to unique compounds.

## 4. Frozen upstream predictions and uncertainty

Bootstrap resampling occurs strictly downstream of the immutable prediction/uncertainty freeze. Every bootstrap row-occurrence reuses the original `activity_id`, outer-fold assignment, frozen RF prediction, frozen QRF width, frozen comparator uncertainty values, and observed outcome for downstream evaluation.

Do not refit RF models, reconstruct outer folds, recompute fingerprints, recompute QRF weights or uncertainty values, or alter prediction-freeze bytes or hash.

## 5. Reapply QRF80 retention within each replicate

The primary bootstrap reapplies the frozen triage procedure inside every resampled cohort. For replicate \(b\) and original fold \(f\), let \(n^*_{b,f}\) be the number of bootstrap **row-occurrences** in that fold, including multiplicity. Define:

```text
k*_(b,f) = ceil(0.80 * n*_(b,f))
```

Rank the fold's bootstrap row-occurrences by their already-frozen QRF-width uncertainty, lowest first, and retain exactly \(k^*_{b,f}\) occurrences. Retention membership and counts are thus recomputed from the replicate cohort, not inherited from the original cohort's fixed retained-ID mask. Outcomes and residuals must not participate in ranking.

## 6. Duplicate scaffold and compound occurrences

Repeated scaffold draws contribute repeated row-occurrences. Copies of a compound retain identical activity ID, prediction, uncertainty, and observed outcome, but each occurrence counts separately in ranking and RMSE. Do not deduplicate repeated occurrences before either operation.

For deterministic ranking where occurrences have identical uncertainty and activity ID, order by:

1. uncertainty score;
2. the canonical configured activity-ID tie hash; and
3. deterministic bootstrap occurrence index.

The occurrence index is an implementation/reproducibility key only and carries no scientific information. Partial selection of repeated occurrences at the retention boundary is permitted because bootstrap occurrences are the resampled observational units.

## 7. Matched-random comparator within each replicate

For each bootstrap replicate, construct the matched-random comparator from that same resampled cohort. Within each original fold, the candidate pool is its bootstrap row-occurrences and the retained count for every random draw is exactly \(k^*_{b,f}\), matching QRF80. Random selection is without replacement from the row-occurrence multiset and is outcome-blind.

Use exactly 10,000 matched-random draws within each bootstrap replicate, following the frozen matched-random procedure's arithmetic-mean-of-draw-RMSE definition. Do not reuse the original cohort's random retained-ID masks. Selection must not use outcomes, residuals, absolute errors, or squared errors.

## 8. Paired bootstrap meaning

"Paired" means that, within replicate \(b\), QRF triage and matched-random triage are evaluated on the same scaffold-resampled fold populations and the same scaffold/row-occurrence multiplicities. The methods differ in selection strategy, not in resampled cohort. Each random draw uses the replicate's same fold-specific candidate pools and QRF-matched retained counts.

## 9. Replicate metrics and interval

For each replicate:

1. Pool the fold-local QRF-retained row-occurrences and compute \(\mathrm{RMSE}^{(b)}_{\mathrm{QRF80}}\).
2. For each of the 10,000 matched-random draws, pool its fold-local selected occurrences and compute that draw's retained RMSE.
3. Define \(\mathrm{RMSE}^{(b)}_{\mathrm{RANDOM80}}\) as the arithmetic mean of the 10,000 draw-specific pooled RMSEs.
4. Calculate:

```text
REL_BENEFIT_80^(b) =
(RMSE_RANDOM80^(b) - RMSE_QRF80^(b)) / RMSE_RANDOM80^(b)
```

Every metric respects bootstrap multiplicity; repeated scaffold/compound occurrences count separately in every RMSE.

Use exactly 10,000 scaffold-bootstrap replicates, stratified by original outer fold, with seed `20260923`. The confidence interval is the empirical percentile 95% interval from the replicate `REL_BENEFIT_80` values. It quantifies sampling uncertainty in the full frozen downstream triage/evaluation procedure under scaffold-cluster resampling, including replicate-specific fold-local retention and matched-random selection. It is not conditional on one fixed original retained-ID set.

## 10. RNG and implementation reproducibility

The original SAP pins the bootstrap seed `20260923` and replicate count, but does not pin the RNG family, seed consumption, replicate substream construction, or sampling primitive. These are implementation-level reproducibility details and do not change the scientific estimand.

For scaffold-resampling draws, a deterministic implementation already exists in repository code/config. A complete RNG contract for the entire amended bootstrap does not yet exist because the nested matched-random draws have no defined per-replicate RNG/substream construction.

The current repository does contain a scaffold-resampling helper, `src/v3a_qrf_weights.py::scaffold_bootstrap_indices`, and frozen defaults in `src/v3a_config.py` (`MASTER_SEED = 20260923`, `N_BOOTSTRAP = 10_000`). The helper's present deterministic construction is:

- initialize one `numpy.random.RandomState(seed)` for the call (the legacy MT19937-based NumPy RNG);
- process outer folds in sorted order and scaffold keys in sorted order;
- for each fold and replicate, draw `n_groups` integer indices using `rng.randint(0, n_groups, n_groups)`, which samples scaffold indices uniformly with replacement; and
- append all original row indices for each selected scaffold in draw order, preserving repeated scaffold occurrences.

The original SAP did not specify these implementation details. This amendment records the existing scaffold-bootstrap helper's construction for Ticket 4 to use and test; it does not attribute that detail to the original SAP.

The existing `matched_random_rankings` helper is not a complete implementation of the amended within-replicate comparator: it requires unique activity IDs and cannot represent duplicated row-occurrences as distinct selectable entries. The Ticket 4 implementation must therefore pin a deterministic RNG/substream and sampling construction for the 10,000 nested matched-random draws before real execution. That implementation choice must preserve the specified uniform, fold-local, without-replacement sampling of row-occurrences and must not change the estimand.

## 11. Computational cost and equivalence

Replicate-specific matched-random evaluation may be computationally expensive. Cost must not be used to alter the frozen estimand. An optimization is permitted only if it is mathematically equivalent to the literal reference procedure and verified against that reference on synthetic fixtures.

Do not replace the matched-random procedure with an analytic expectation, fewer draws, median random RMSE, compound-level bootstrap, or global sampling.

## 12. Relation to Sensitivity B

The separate Sensitivity-B pre-execution amendment defines replicate-specific subgroup reranking and matched-random regeneration for B. This amendment independently clarifies the primary procedure. Sensitivity B did not retroactively define primary semantics. The two procedures are now deliberately aligned in their bootstrap logic, each under its own explicit pre-execution protocol record.

## 13. Interpretation and unchanged protocol boundaries

The bootstrap does not estimate model-training uncertainty: models, predictions, and uncertainty scores remain frozen. It estimates sampling uncertainty in downstream triage performance across scaffold-cluster resamples of the evaluated chemical space. Because triage retention is part of the frozen downstream procedure, the retention rule is reapplied inside each bootstrap replicate.

This amendment does not modify the primary practical threshold of 10%, three-state classification, primary coverage of 80%, random draw count, primary point-estimate definition, Sensitivity A, Sensitivity B, CQR, or V3B censored-data analysis.

---

**Protocol amendment status:** PRE-EXECUTION  
**Real V3A result available:** NO  
**Primary point-estimate formula changed:** NO  
**Primary bootstrap semantics clarified:** YES
