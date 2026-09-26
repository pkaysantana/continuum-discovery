# V3A Sensitivity B Pre-Execution Protocol Amendment

**Date:** 2026-09-25  
**Status:** PRE-EXECUTION PROTOCOL AMENDMENT

## 1. Purpose and scope

The original frozen V3A Statistical Analysis Plan (SAP) correctly specifies Sensitivity B as an analysis of compounds with observed experimental $CL_{\mathrm{int}} \ge 25.0$, inclusive of exactly 25.0. It correctly establishes this sensitivity as outcome-defined, exploratory, diagnostic, and nondeployable.

The original frozen SAP does not, however, completely specify Sensitivity B's retention handling, matched-random handling, metrics, bootstrap treatment, or operational classification treatment. A read-only protocol audit identified this genuine specification gap. This amendment resolves only those implementation ambiguities.

This amendment was created before Ticket 4 implementation, before any real V3A scientific execution, and before inspection of any real V3A scientific result. No real CHEMBL3301370 $N=744$ result has been generated or was available when this amendment was written. It does not modify the primary V3A analysis, primary estimand, primary cohort, primary prediction freeze, or primary classification rule. The original frozen SAP, Gate 11 specification, and freeze checklist remain unchanged.

## 2. Authoritative unchanged constraints

Sensitivity B starts from the primary exact quantitative $N=744$ study machinery. The following primary artifacts remain immutable:

- the original $N=744$ cohort definition;
- the original five scaffold-grouped outer folds;
- the Random Forest (RF) model specification;
- the ECFP4 representation;
- the out-of-fold (OOF) point predictions;
- the Quantile Regression Forest (QRF) uncertainty values;
- the comparator uncertainty values; and
- the prediction-freeze bytes and hash.

Observed experimental $CL_{\mathrm{int}} \ge 25.0$ must not influence model fitting, fold construction, feature construction, prediction, uncertainty estimation, or prediction-freeze construction. No Sensitivity-B-specific upstream model may be fit.

## 3. Frozen Sensitivity B procedure

### A. Source population

Start from the $N=744$ exact quantitative primary cohort after the immutable prediction/uncertainty freeze exists.

### B. Outcome-defined filter

Define Sensitivity B as compounds satisfying:

$$
\text{observed experimental } CL_{\mathrm{int}} \ge 25.0
$$

on the original experimental $CL_{\mathrm{int}}$ scale, in $\mu\mathrm{L}/\mathrm{min}/\mathrm{mg}$. Exactly 25.0 is included.

The equivalent log-scale statement is:

$$
\log_{10}(CL_{\mathrm{int}}) \ge \log_{10}(25),
$$

but the canonical definition is on the original experimental $CL_{\mathrm{int}}$ scale.

### C. Upstream artifact reuse

Reuse unchanged:

- the original activity IDs;
- the original outer-fold assignments;
- the original OOF RF predictions; and
- the original frozen uncertainty scores.

There is no refitting, resplitting, hyperparameter change, new prediction freeze, or uncertainty recomputation.

### D. Filter timing

Apply the $\ge 25.0$ filter only after the primary immutable prediction/uncertainty freeze. This is an outcome-defined downstream diagnostic.

### E. Within-fold diagnostic ranking

After applying the $\ge 25.0$ filter, operate separately within each original outer fold. For every frozen coverage

$$
\kappa \in \{1.00, 0.90, 0.80, 0.70, 0.60, 0.50\},
$$

rank qualifying compounds using their already-frozen uncertainty score. In original outer fold $f$, let $n_{B,f}$ be the number of qualifying compounds and retain the lowest-uncertainty

$$
k_{B,f}(\kappa)=\left\lceil \kappa n_{B,f}\right\rceil
$$

qualifying compounds. Use the existing canonical configured activity-ID tie-break rule. Do not rank globally across folds.

### F. Primary diagnostic score

QRF width remains the focal uncertainty measure. At diagnostic coverage 0.80, define $\mathrm{RMSE\_QRF80\_B}$ as the pooled RMSE over the fold-local retained $\ge 25.0$ compounds. This is a descriptive diagnostic quantity, not a deployable policy result and not a primary protocol result.

### G. Matched-random diagnostic baseline

Generate a Sensitivity-B-specific matched-random baseline after defining the subgroup, using:

- exactly 10,000 draws;
- seed `20260923`;
- random selection independently within each original outer fold; and
- in every fold, exactly the same number of $\ge 25.0$ compounds as QRF80 retains in that fold, namely $k_{B,f}(0.80)$.

For each draw, sample without replacement from the already-defined $\ge 25.0$ subgroup within each fold, pool the fold-local retained samples, and calculate retained RMSE. The random generator must operate only on the already-defined subgroup and must not use prediction error or residual magnitude for selection.

Define:

$$
\mathrm{RMSE\_RANDOM80\_B}
=
\text{mean pooled retained RMSE across the 10,000 matched subgroup random draws}.
$$

### H. Diagnostic relative benefit

Define descriptively:

$$
\mathrm{REL\_BENEFIT\_80\_B}
=
\frac{\mathrm{RMSE\_RANDOM80\_B}-\mathrm{RMSE\_QRF80\_B}}
{\mathrm{RMSE\_RANDOM80\_B}}.
$$

Higher is better. This diagnostic estimand does not inherit the primary operational decision classification.

### I. Coverage curves

For every frozen uncertainty method and every frozen coverage level, calculate within the $\ge 25.0$ subgroup:

- retained $n$;
- deferred $n$;
- pooled RMSE; and
- pooled MAE.

The same secondary normalized area under the risk-coverage curve (nAURC) definition may be applied over coverage 0.50-1.00. All coverage-curve and nAURC quantities are diagnostic.

### J. Bootstrap

Apply the same general primary inference architecture to quantify uncertainty descriptively:

- scaffold-clustered bootstrap;
- stratification by original outer fold;
- scaffold as the resampling unit;
- exactly 10,000 bootstrap replicates;
- the existing bootstrap-resampling seed `20260923` and existing bootstrap-resampling procedure; and
- paired evaluation of the QRF-versus-matched-random diagnostic estimand.

Each scaffold-bootstrap replicate preserves fold stratification and bootstrap multiplicity: scaffold clusters are resampled with replacement within each original outer fold, and all observations belonging to each sampled scaffold occurrence enter the replicate with that occurrence's multiplicity. Nothing in this amendment replaces or modifies the existing bootstrap-resampling seed or procedure.

For each bootstrap replicate $b \in \{1,\ldots,10000\}$:

1. Reuse the frozen $N=744$ predictions and uncertainty values. Do not refit a model, re-estimate uncertainty, or reassign any fold.
2. After scaffold resampling, reapply the observed experimental $CL_{\mathrm{int}} \ge 25.0$ eligibility filter to the resampled observations, preserving bootstrap multiplicity.
3. Separately within each original outer fold, recompute the QRF ranking over that replicate's eligible observations using the frozen QRF uncertainty values. Reapply the already-frozen fold-local retention-count rule $k_{B,f}(0.80)=\lceil 0.80n_{B,f}\rceil$ to the replicate-specific eligible count and use the existing canonical configured activity-ID tie-break rule. Pool the retained observations across folds and calculate that replicate's QRF retained-subgroup RMSE.
4. Recompute the matched-random comparator inside that same bootstrap replicate. Do not reuse the original non-bootstrap 10,000-draw matched-random baseline and do not substitute a single random draw. Use exactly 10,000 matched-random draws for the replicate. In every draw, sample independently within each original outer fold, without replacement from that replicate's eligible observation multiset, retaining exactly the same replicate-specific fold-local count as QRF in that fold. Each draw therefore uses the same replicate-specific eligible observations and fold-local retention counts as the replicate's QRF subgroup. Pool the selected observations across folds, calculate retained RMSE, and define the replicate's matched-random component as the arithmetic mean of pooled retained RMSE across its 10,000 draws.
5. Calculate replicate $b$'s $\mathrm{REL\_BENEFIT\_80\_B}$ from that replicate's recomputed QRF retained-subgroup RMSE and that same replicate's mean matched-random RMSE, using the already-frozen $\mathrm{REL\_BENEFIT\_80\_B}$ definition unchanged. The QRF and matched-random quantities are thus paired within the same scaffold-bootstrap replicate.

Nested matched-random RNG handling is deterministic and reproducible. For bootstrap replicate $b$, numbered starting at $b=1$, initialize the nested matched-random RNG from:

```text
SeedSequence([20260923, b])
```

Use that replicate-specific RNG stream for its 10,000 matched-random draws. This seed rule applies only to the nested matched-random calculation; it does not replace, advance, or otherwise modify the existing bootstrap-resampling seed or procedure.

Recomputing fold-local QRF ranking and retention inside every bootstrap replicate is intentional. The bootstrap confidence interval targets uncertainty in the full QRF-retention procedure under scaffold resampling, rather than uncertainty conditional on one permanently frozen retained subset.

Report the percentile 95% confidence interval from the 10,000 replicate $\mathrm{REL\_BENEFIT\_80\_B}$ values.

The confidence interval remains descriptive diagnostic uncertainty for a nondeployable, outcome-defined sensitivity analysis. It must not be converted into the primary V3A three-state operational result.

### K. No three-state operational classification

Do not classify Sensitivity B as any of:

- `SUPPORTED_OPERATIONAL_SIGNAL`;
- `EVIDENCE_BELOW_PRACTICAL_THRESHOLD`; or
- `INCONCLUSIVE`.

Those labels belong to the prespecified primary operational analysis. Sensitivity B must instead be reported as an **"exploratory, outcome-defined, diagnostic assay-family sensitivity"**, together with its point estimate and descriptive uncertainty.

### L. Comparator status

The following remain secondary diagnostic comparators:

- Tanimoto unfamiliarity;
- physicochemical 5-nearest-neighbour distance;
- $1/N_{\mathrm{eff}}$;
- local weighted outcome standard deviation; and
- tree standard deviation.

No comparator may replace QRF width as the focal Sensitivity B score based on observed results.

## 4. Interpretation limitations

All reporting and interpretation must preserve the following limitations:

- The approximately 25 threshold comes from broader assay-family heteroscedasticity context. It is not a validated CHEMBL3301370 row-level observation-error threshold.
- The $\ge 25.0$ stratum must not be described as "noise-free."
- The $\ge 25.0$ threshold must not be described as a biologically privileged clearance boundary.
- The analysis cannot become a deployable pre-assay policy because subgroup membership requires observing the assay outcome.
- No row-level error subtraction or noise correction is permitted.
- A positive diagnostic result cannot prove that the primary result was caused by assay noise.
- A negative diagnostic result cannot prove that assay variability is irrelevant.

## 5. Rationale for subgroup re-ranking

The diagnostic question is conditional:

> "Within the observed $\ge 25$ assay stratum, does the already-frozen pre-assay uncertainty ranking discriminate prediction error?"

Accordingly, this amendment requires re-ranking within the outcome-defined subgroup using frozen uncertainty values rather than simply filtering the original $N=744$ retained IDs. Re-ranking uses no new model information and no recomputed uncertainty. Subset-specific ranking and matched-random counts keep the diagnostic coverage comparison internally matched.

Because subgroup membership is outcome-defined, this procedure remains explicitly nondeployable. It must not be portrayed as a primary protocol result.

## 6. Protocol boundaries

This amendment does not expand any other analysis or resolve any additional scientific question. It does not modify Sensitivity A or V3B censored-data work. Its sole function is to freeze the previously underspecified execution details for V3A Sensitivity B before implementation and before any real scientific execution or result inspection.

## 7. Audit trail

| Field | Frozen record |
|---|---|
| Date | 2026-09-25 |
| Status | PRE-EXECUTION PROTOCOL AMENDMENT |
| Trigger | Read-only audit identified an underspecified Sensitivity-B execution procedure. |
| Result knowledge at amendment | No real V3A scientific result available. |
| Primary SAP modified | NO |
| Primary estimand modified | NO |
| Primary cohort modified | NO |
| Primary prediction freeze modified | NO |
| Primary classification rule modified | NO |
| Sensitivity B implementation clarified | YES |
