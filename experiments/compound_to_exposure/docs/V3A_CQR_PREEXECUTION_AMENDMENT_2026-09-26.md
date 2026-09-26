# V3A CQR Pre-Execution Protocol Amendment

**Date:** 2026-09-26  
**Status:** PRE-EXECUTION PROTOCOL AMENDMENT

## 1. Audit trail

**Trigger:** Independent read-only audit identified mathematically material CQR details not uniquely specified by the frozen SAP.

**Result knowledge at amendment:** No real V3A CQR result available.

| Item | Modified? |
|---|---|
| Primary V3A analysis | NO |
| Primary uncertainty ranking | NO |
| CQR role | NO |
| CQR mathematical implementation clarified | YES |

The original SAP froze CQR as a **SECONDARY marginal-calibration analysis**, but it did not fully freeze the calibration nonconformity score, signed-score handling, finite-sample conformal rank, order-statistic semantics, excessive-rank behavior, clipping behavior, or the exact deterministic proper-training/calibration scaffold split. This amendment freezes those choices before Ticket 4 implementation and before any real V3A scientific execution or CQR result inspection. It does not imply that these details were already specified by the original SAP.

### Focused remediation audit trail

The first draft of this amendment accidentally omitted the leading underscore from the existing helper's salt. Independent read-only audit detected that transcription error before execution. This focused remediation adopts the already-existing deterministic, outcome-blind helper salt exactly as `_V3A_CQR_20260923`. No real CQR result existed or was inspected when this correction was made. The helper and configuration are not modified by this documentation-only remediation.

## 2. Unchanged CQR role

- CQR is **SECONDARY**.
- CQR is calibration-focused.
- CQR is **NOT** a primary triage ranking.
- QRF width remains the primary uncertainty score.
- CQR cannot replace QRF width.
- Nominal coverages are exactly 80%, 90%, and 95%.
- Coverage claims are **MARGINAL**, not conditional.
- Outer-test outcomes are unavailable until final interval evaluation.
- One scalar `qhat` is constant within each outer fold and nominal coverage.

## 3. Base QRF intervals

The unconformalized QRF intervals are frozen as:

| Nominal coverage | Base QRF interval |
|---|---|
| 80% | $[Q_{0.10}(x), Q_{0.90}(x)]$ |
| 90% | $[Q_{0.05}(x), Q_{0.95}(x)]$ |
| 95% | $[Q_{0.025}(x), Q_{0.975}(x)]$ |

All quantiles use the already-frozen QRF weighted empirical inverse-CDF definition from the SAP:

$$
Q_{\tau}(x)=\inf\{y:\hat F(y\mid x)\ge\tau\}.
$$

No interpolation between observed response values is permitted.

## 4. Signed nonconformity score

For calibration observation $i$, with base interval $[L_i,U_i]$ and observed outcome $y_i$, define exactly:

$$
s_i=\max(L_i-y_i,\;y_i-U_i).
$$

The score is **SIGNED**:

- $s_i>0$ when $y_i$ lies outside the base interval;
- $s_i=0$ when $y_i$ lies exactly on an interval boundary; and
- $s_i<0$ when $y_i$ lies strictly inside the base interval.

Do not append a zero term. In particular, the following nonnegative score is prohibited:

```text
max(L_i - y_i, y_i - U_i, 0)
```

## 5. No nonnegative clipping

Do not clip `qhat` to zero. Negative `qhat` values are permitted and are not errors.

Consequently, CQR may:

- widen an under-covering base interval when `qhat > 0`;
- leave a base interval unchanged when `qhat = 0`; or
- shrink an over-wide base interval when `qhat < 0`.

This behavior is intentional and is part of the frozen signed-score CQR procedure.

## 6. Exact finite-sample conformal rank

For nominal miscoverage $\alpha$ and calibration size $n_{\mathrm{cal}}$, define:

$$
k=\left\lceil(n_{\mathrm{cal}}+1)(1-\alpha)\right\rceil.
$$

The rank uses one-based order-statistic indexing. If $1\le k\le n_{\mathrm{cal}}$, `qhat` is exactly the $k$-th smallest calibration nonconformity score:

```text
qhat = sorted(scores)[k - 1]
```

An exact order-statistic operation with identical semantics is permitted. An interpolating quantile is prohibited. The protocol definition is the order statistic, not a NumPy probability-interpolation convention.

Do not use the following as a substitute unless it has been proved to return exactly the same $k$-th order statistic for every admissible $n_{\mathrm{cal}}$ and $k$:

```text
np.quantile(scores, k / n_cal, method="higher")
```

## 7. Small-calibration edge case

If $k>n_{\mathrm{cal}}$, define:

$$
\widehat q=+\infty.
$$

This preserves the finite-sample conformal guarantee when the calibration set is too small to support the requested nominal coverage using a finite order statistic. Do not replace this result with the sample maximum, clip $k$ to $n_{\mathrm{cal}}$, lower the confidence level, interpolate, or substitute an approximate finite value.

After conformal expansion, the resulting interval is:

$$
[-\infty,+\infty].
$$

This edge case must be represented explicitly in result metadata.

## 8. Final CQR interval

For an outer-test compound with base QRF interval $[L(x),U(x)]$, define the raw corrected endpoints exactly:

$$
A(x)=L(x)-\widehat q,
$$

$$
B(x)=U(x)+\widehat q.
$$

The raw algebraic corrected span is:

$$
D(x)=B(x)-A(x)=U(x)-L(x)+2\widehat q.
$$

For finite negative `qhat`, $D(x)$ may be negative. The same scalar `qhat` applies to every outer-test compound in the same outer fold and nominal coverage. A feature-dependent or local `qhat` is prohibited.

## 9. Finite negative-qhat / empty-set semantics

For finite corrected endpoints:

- If $A(x)\le B(x)$, the CQR prediction set is the ordinary closed interval

  $$
  C(x)=[A(x),B(x)].
  $$

- If $A(x)>B(x)$, define

  $$
  C(x)=\varnothing.
  $$

The empty-set result is an intentional prediction-set definition. Do not swap or reorder $A$ and $B$, clip `qhat`, set `qhat` to zero, expand the result to a point interval, replace `qhat` with another calibration score, drop the observation, or treat the prediction set as $[B(x),A(x)]$. The raw corrected endpoints $A(x)$ and $B(x)$ must remain in metadata so the inversion is auditable.

For a finite observed test outcome $y$:

```text
if A <= B:
    covered = (A <= y <= B)
if A > B:
    covered = FALSE
```

An empty prediction set contributes zero to the empirical coverage numerator and remains in the empirical marginal-coverage denominator. Empty sets must not be dropped.

Define the reported prediction-set width exactly as:

$$
\operatorname{WIDTH}(x)=\max(0,\;B(x)-A(x)).
$$

Thus an ordinary finite interval has width $B-A$, an empty prediction set has width zero, and a prediction set produced by `qhat = +infinity` has width `+infinity`. Negative interval widths must not be reported.

The raw corrected span may be retained separately as diagnostic provenance:

$$
\operatorname{RAW\_CORRECTED\_SPAN}(x)=B(x)-A(x).
$$

`RAW_CORRECTED_SPAN` may be negative. It is diagnostic metadata only and is not the reported prediction-set width.

Mean and median interval-width summaries must use `WIDTH(x)`, not the raw algebraic span. Empty prediction sets contribute zero width. Infinite prediction sets contribute `+infinity` under Section 16. Neither empty nor infinite sets may be excluded merely to obtain finite summaries.

## 10. Ranking invariance and canonical ranking

Within an outer fold and nominal coverage:

$$
D(x)=\operatorname{Width}_{\mathrm{QRF}}(x)+2\widehat q.
$$

Because `qhat` is constant, the raw algebraic corrected span is a constant shift of base QRF width and exactly preserves its ordering within the fold and coverage.

The reported set width applies the monotone transformation $\max(0,D(x))$. This transformation cannot reverse the base-width order, but multiple inverted prediction sets may collapse to tied zero widths. It therefore does not necessarily preserve a strict total ordering.

CQR does not create a scientifically separate triage ranking. The canonical assay-triage ranking remains the original frozen QRF-width ranking. CQR reported widths must never replace or re-rank the primary triage procedure. CQR remains calibration-only.

## 11. Exact proper-training/calibration scaffold split

The committed repository helper `src/v3a_qrf_weights.py::conformal_proper_train_cal_split` was inspected before this amendment was written. It provides a coherent, deterministic, outcome-blind, scaffold-grouped approximately-80/20 split. This amendment freezes its exact assignment algorithm:

1. For the designated outer fold $f$, define outer training as every row whose `outer_fold != f`. No outer-test row may enter either proper training or calibration.
2. Group outer-training rows by the same canonical Bemis–Murcko `scaffold_key` used elsewhere in V3A. Each scaffold group is indivisible.
3. Use calibration fraction `0.20` and salt exactly:

   ```text
   _V3A_CQR_20260923
   ```

4. For each scaffold key `key`, compute the lowercase hexadecimal SHA-256 digest of the UTF-8 bytes of the direct string concatenation:

   ```text
   key + "_V3A_CQR_20260923"
   ```

   There is no inserted separator.
5. Sort scaffold groups in ascending lexicographic order of that hexadecimal digest. The committed helper obtains groups through pandas `groupby("scaffold_key")` with its default ascending key ordering before applying the stable digest sort; therefore, in the theoretical event of identical digests, ascending scaffold-key order is the deterministic secondary order.
6. Let $n_{\mathrm{outer\ train}}$ be the number of outer-training compounds and set:

   $$
   n_{\mathrm{cal,target}}=\lceil0.20\,n_{\mathrm{outer\ train}}\rceil.
   $$

7. Traverse scaffold groups in the sorted order. While the calibration compound count before the current group is less than $n_{\mathrm{cal,target}}$, assign the entire current scaffold group to calibration and add its full size to the calibration count. Once the count has reached or exceeded the target, assign every remaining scaffold group to proper training.
8. Overshoot caused by the indivisible scaffold that crosses the target is retained. No scaffold is split to hit the target exactly.
9. Return the activity IDs in the two disjoint groups. Their union must equal the outer-training activity IDs.

This split targets approximately 80% of outer-training compounds for proper training and 20% for calibration while preserving scaffold integrity. It uses scaffold identities and group sizes only. Outcome balancing, residual balancing, uncertainty balancing, and random unseeded assignment are prohibited.

## 12. Proper-training role

For each outer fold, fit the **SECONDARY** CQR QRF using proper-training observations only. Calibration outcomes and outer-test outcomes must not enter model fitting.

The CQR model uses the frozen QRF representation and model architecture specified in the SAP. No retuning is permitted.

## 13. Calibration role

For each nominal coverage:

1. Construct base QRF intervals on calibration compounds using the proper-training fit.
2. Obtain calibration outcomes.
3. Compute the signed nonconformity scores specified in Section 4.
4. Calculate `qhat` using the exact finite-sample order-statistic rule in Sections 6 and 7.

Calibration rows may influence `qhat` only. They must not be added back into the proper-training fit after `qhat` is calculated.

## 14. Outer-test role and leakage boundary

For each outer-test compound:

1. Construct its base QRF interval from the proper-training model.
2. Apply the outer-fold/coverage-specific `qhat`.
3. Only after final interval construction may the outer-test outcome be accessed.
4. Use that outcome only to compute final empirical marginal coverage and width summaries.

No outer-test outcome may influence the proper/calibration split, model fit, base interval, or `qhat`.

## 15. Reporting

For each nominal level of 80%, 90%, and 95%, report at minimum:

- nominal coverage;
- empirical **MARGINAL** coverage;
- number of evaluated outer-test compounds;
- mean final interval width; and
- median final interval width.

Compute pooled summaries over all valid outer-test compounds after fold-specific interval construction.

Mean and median summaries use the nonnegative reported prediction-set width `WIDTH(x) = max(0, B(x) - A(x))`. Empty prediction sets remain in the summaries with width zero. Infinite prediction sets remain in the summaries with width `+infinity`.

Fold-level calibration metadata must retain:

- outer fold;
- `n_proper`;
- `n_cal`;
- nominal coverage;
- finite-sample $k$;
- `qhat`;
- whether `qhat` is finite; and
- proper/calibration split provenance, including helper name, salt, calibration fraction, and assignment algorithm identifier;
- number evaluated;
- number of finite ordinary intervals;
- number of empty prediction sets;
- number of infinite prediction sets;
- empirical marginal coverage;
- mean prediction-set width; and
- median prediction-set width.

Where row-level interval records are retained, they must preserve:

- raw lower endpoint $A(x)$;
- raw upper endpoint $B(x)$;
- empty-set boolean;
- finite/infinite status; and
- reported set width.

The raw corrected span may also be retained as diagnostic metadata. These fields are reporting and provenance only; they introduce no new scientific endpoint or hypothesis test.

Conditional coverage claims are prohibited.

## 16. Infinite-interval reporting

If `qhat = +infinity` for any fold and coverage:

- mark that fold/coverage as having insufficient calibration size for a finite conformal interval;
- record interval width as `+infinity`;
- record coverage for those intervals as mechanically 1 for finite outcomes; and
- preserve the fold and this fact explicitly rather than silently dropping it.

Infinity must not be replaced by an arbitrary large finite number.

## 17. Relation to the current helper

The pre-existing helper was inspected during the audit but was **not** protocol authority.

The following current behavior is compliant with this amendment:

- uses the same signed score form;
- uses the deterministic `conformal_proper_train_cal_split` helper and literal salt `_V3A_CQR_20260923` documented in Section 11.

Ticket 4 correction remains required because the current helper:

- uses a NumPy `"higher"` probability-quantile construction rather than the protocol-defined exact order statistic;
- clips `qhat` to nonnegative values;
- maps an excessive finite-sample rank to the sample maximum; and
- rejects negative corrections and does not implement the empty-set semantics and reporting frozen in Section 9.

Ticket 4 must correct behavior inconsistent with the newly frozen exact order-statistic, signed-`qhat`, infinite-edge-case, and empty-set rules. No helper or other code is edited by this documentation-only amendment task.

## 18. Scientific interpretation

CQR assesses marginal interval calibration. It does **NOT** establish:

- conditional coverage;
- a compound-specific calibrated error probability;
- epistemic uncertainty;
- a regulatory prediction interval; or
- a superior assay-triage ranking.

The CQR ranking remains the underlying frozen QRF ranking.

The signed-score construction permits a negative conformal correction because calibration observations already well inside their base intervals can have negative nonconformity scores. An empty prediction set is an output of this finite-sample calibration construction; it is not interpreted as physical impossibility or biological certainty. It is handled transparently as uncovered, zero set width, and retained in evaluation. No conditional-coverage claim is introduced.

## 19. No other changes

This amendment does not modify:

- the primary QRF point predictor;
- the primary QRF uncertainty score;
- the primary bootstrap;
- the primary classification;
- Sensitivity A;
- Sensitivity B;
- V3B; or
- any coverage level.

---

**Protocol amendment status:** PRE-EXECUTION  
**Real V3A CQR result available:** NO  
**Original CQR specification gap acknowledged:** YES  
**CQR mathematical implementation clarified:** YES
