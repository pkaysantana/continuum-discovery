# CENSORING_POLICY_MEMO

Prospective policy for the treatment of censored and unqualified clearance observations in the DMPK
compound-to-exposure study. Written **before** any model is fitted, any representation is chosen, any
hyperparameter is selected and any performance number is seen.

Authority: [DATASET_SELECTION_MEMO.md](DATASET_SELECTION_MEMO.md) remains the frozen scientific source
of truth for dataset selection. This memo supplies the censor-handling rules that memo item 5 requires
("Explicit censoring and UNKNOWN handling rules must be applied rigorously across all datasets") and
that the audit's stop condition defers to review. It does not reopen dataset selection.

Evidence labels follow the audit convention: **OBSERVED** (read from frozen data), **INFERRED**
(reasoned from observations, stated as reasoning), **UNKNOWN / UNRESOLVED** (not established).
No inference is promoted to OBSERVED in this memo.

**Amendment, 2026-09-17 — frozen-metadata audit.** This revision incorporates the completed audit of the
remaining activity metadata fields for the 13 HLM null-relation records at value 3 (the check formerly
named U2). The audit adds OBSERVED facts about what those fields contain, and it **does not** resolve the
records' censoring status: that question is now recorded as **UNRESOLVED AFTER FROZEN-METADATA AUDIT**
(§2(d), §12 U4, frozen policy item 13). The consequential changes are terminological and
prespecification-hardening — the 744 null-relation HLM observations are named the **inferred
quantifiable-range cohort**, the cohort is decomposed as 731 + 13, S1 is expanded into a full-workflow
rerun, and the three-class classifier's IN-RANGE label carries an explicit boundary-ambiguity flag. **No
scientific conclusion of the previous version is reversed**, and dataset selection, the audit reports and
the raw data are untouched.

---

## 1. Meaning of censoring in this assay

OBSERVED: CHEMBL3301370 is human liver microsomal apparent intrinsic clearance, native units
`microL/min/mg` microsomal protein (1,102 rows), standardised by ChEMBL to `mL.min-1.g-1` (1,102 rows);
the two are dimensionally and numerically equivalent, and original and standard values agree for all
1,102 rows ([DATA_AUDIT.md](../reports/DATA_AUDIT.md) units section).

OBSERVED: qualifier structure of the three source assays
([REVIEW_SUMMARY.md](../reports/REVIEW_SUMMARY.md)):

| Assay | `<` | `>` | explicit `=` | null relation | total |
|---|---:|---:|---:|---:|---:|
| CHEMBL3301370 human HLM | 274 | 84 | **0** | 744 | 1,102 |
| CHEMBL3301371 rat hepatocyte (exclusion evidence only) | 115 | 127 | **0** | 595 | 837 |
| CHEMBL3301372 human hepatocyte | 104 | 15 | **0** | 289 | 408 |

OBSERVED: every `<` record has value exactly 3 and every `>` record has value exactly 150.

OBSERVED: across the complete per-relation value enumerations for all three assays, **no reported value
is below 3 and none is above 150**. The observed support of the HLM label is exactly the closed
interval [3, 150].

A `<3` record therefore carries one fact: the true CLint lies somewhere in (0, 3). A `>150` record
carries one fact: the true CLint lies somewhere in (150, ∞). Neither carries a point value. Recording
them as 3 and 150 converts a one-sided bound into a fabricated exact measurement, and does so for
**358 of 1,102 HLM records (32.5%)** — concentrated as two spikes at the extremes of the target
distribution, which is the worst possible place for fabricated precision to sit.

INFERRED: the numbers 3 and 150 function as the lower and upper limits of the assay's quantifiable
range. This is inferred from the qualifier/value structure above, not from a captured assay-description
statement of the limits — see UNKNOWN U3.

---

## 2. Null-relation interpretation

The question is whether the 744 HLM records with `standard_relation = null` may be treated as
uncensored measurements. The three evidence classes the task distinguishes resolve as follows.

**(a) Explicit documentary evidence that null means exact / equality — NOT ESTABLISHED.**

UNKNOWN: the ChEMBL schema describes `ACTIVITIES.standard_relation` as the symbol constraining
`standard_value`. No ChEMBL documentation known to this memo states that a null qualifier *means*
equality; the ChEMBL web interface and API simply render no qualifier. Absence of a qualifier and an
asserted `=` are different statements, and ChEMBL supplies an explicit `=` value for other datasets,
which it does **not** do anywhere in these three assays. The documentary question could not be checked
against ChEMBL's own schema/FAQ pages during the preparation of this memo (network retrieval was
unavailable in that session); it is carried as UNKNOWN U1 with a named check, and the policy below is
deliberately designed not to depend on its outcome.

**(b) The deposited original relation does NOT resolve it.**

OBSERVED: original and standard relation counts agree in all three assays, at 100% agreement of both
relation and value ([AUDIT_REVIEW.md](../reports/AUDIT_REVIEW.md)). The deposited qualifier field is
null wherever the standardised one is null. This closes the most obvious route: the depositor did not
supply a qualifier that ChEMBL's standardisation then dropped. There is no hidden `=` to recover.

**(c) Assay-level internal evidence — strong, and the basis of the ruling.**

INFERRED: three OBSERVED facts, taken together, support a working inference about the depositor's
convention across these three assays:

1. qualifiers appear at exactly two values, 3 and 150, and nowhere else;
2. there is no explicit `=` anywhere in 2,347 records across the three assays;
3. no value in any of the three assays lies outside [3, 150].

OBSERVED, and refining fact 1: within the HLM assay the explicit `<` records sit at the **lower**
boundary of the observed support and the explicit `>` records at the **upper** boundary; of the 744
null-relation records, **731 lie strictly inside the interval (3 < value < 150)**, **13 sit exactly on
the lower boundary at 3**, and **none sits at 150**. The null-relation mass is therefore overwhelmingly
interior, with a single small boundary-coincident group at one end only.

Across these three assays, the observed pattern is consistent with the dataset-specific working
inference that null-relation records represent reported values within the assay's quantifiable range.
This is an inference from the deposited data pattern, not a documented general ChEMBL rule and not
proof that every null-relation record is uncensored.

**(d) Frozen-metadata audit of the remaining activity fields — completed, and it does not resolve the
13.**

The check named as U2 in the previous version of this memo has now been carried out against the frozen
raw bytes (`data/raw/chembl/CHEMBL3301370_activities_*.json`), read-only and with no new acquisition.

*Provenance note:* the field-level tabulation below is the result reported by that audit. It is recorded
here because this memo is where it bears on policy; it is **not** yet written into
[REVIEW_SUMMARY.md](../reports/REVIEW_SUMMARY.md) or
[AUDIT_REVIEW.md](../reports/AUDIT_REVIEW.md), which this amendment does not modify. Landing it in the
audit record is a separate, tracked task, and until then the numeric counts it depends on (744 null, 13
at 3, 0 at 150) are the ones those reports already carry.

OBSERVED, for each of the 13 HLM null-relation records at value 3:

- `value` and `standard_value` are both **3.0** — the original and standardised numbers agree;
- `relation` and `standard_relation` are both **null** — there is no deposited qualifier to recover, and
  none was dropped in standardisation;
- `activity_comment`, `data_validity_comment`, `text_value` and `standard_text_value` are all **null** —
  no free-text annotation marks them as limit values, and none marks them as quantified either;
- `standard_flag = 1` — but this flag is **also 1 for the explicitly censored observations**, so it
  carries no discriminating information about censor status;
- no other inspected field distinguishes them as quantified versus censored.

CONCLUSION: the per-record censor status of these 13 observations is **UNRESOLVED AFTER FROZEN-METADATA
AUDIT**. This is a closed question, not an open task: the frozen metadata has been inspected and does
not contain the answer. This memo does **not** propose further searching through the existing raw
metadata for it. Any future resolution would require information the frozen sources do not carry (e.g. a
depositor-side statement of the assay's reporting convention), and none is assumed.

**Ruling.** Null is recorded as **absence of a deposited qualifier**. It is never recoded to `=`, and
nothing in this memo states or implies that a ChEMBL NULL `standard_relation` means `=` in general. For
modelling purposes the 744 HLM null-relation records are designated the **inferred quantifiable-range
cohort**. That name is exact and deliberate: membership rests on a *dataset-specific working inference*
about this depositor's convention across these three assays — supported by the boundary structure of the
explicit qualifiers, the complete absence of an explicit `=` in 2,347 records, the absence of any value
outside [3, 150], the interior concentration of the null-relation values, and the fact that **no
inspected field contradicts it**. The cohort is *not* described anywhere in this project as a set of
documented exact or equality observations, and its designation is not an assertion that each value is an
exact measurement free of experimental error.

**The irreducibly ambiguous subset.** The cohort decomposes as **731 interior records + 13
boundary-ambiguous records at exactly 3** (OBSERVED; 13 confirmed in
[REVIEW_SUMMARY.md](../reports/REVIEW_SUMMARY.md) and
[AUDIT_REVIEW.md](../reports/AUDIT_REVIEW.md) MINOR-4). The 13 are either genuine measurements that
landed on the lower limit, or censored records whose qualifier was never deposited. They are **not**
reclassified on the strength of their numeric value — doing so would commit exactly the error the audit
warns against ("a numeric boundary alone does not define censor status") — and they are **not** claimed
to be resolved by their inclusion in the primary cohort. Their inclusion is a **prespecified working
inference**; their influence is measured by prespecified sensitivity analysis **S1** (§10), fixed before
any model is fitted.

---

## 3. Candidate approaches

### A. Complete-case regression (in-range only)

- **Statistical validity.** Valid as an estimator of a *conditional* quantity, and only that. Range
  membership is a deterministic function of the outcome y, so this is outcome-dependent selection, i.e.
  **truncation**, not missing-at-random. It cannot be repaired by inverse-probability weighting on X,
  because the selection does not depend on X.
- **Information loss.** 358/1,102 HLM records (32.5%) contribute nothing. Their one-sided bounds are
  real information and are discarded.
- **Selection bias.** Both tails are removed, symmetrically in direction but not in size (24.9% below,
  7.6% above). See §5.
- **Interpretability.** High, and honestly so — provided the claim is stated conditionally.

### B. Boundary substitution (`<3` → 3, `>150` → 150)

- Creates 358 artificial exact targets, 274 of them identical, at the extremes of the distribution.
- Biases the fitted relationship toward the interior: true values below 3 are pulled up, true values
  above 150 pulled down, so the model systematically under-predicts stability and under-predicts
  instability, at the two ends where a DMPK decision actually gets made.
- Corrupts every error metric in an unfalsifiable direction. A model can appear accurate by learning to
  emit 3 and 150 — 24.9% of the target mass sits on a single value — and no amount of held-out
  evaluation detects this, because the held-out data carry the same fabrication.
- **Prohibited throughout the direct-ChEMBL science track, including sensitivity analyses.** Censored
  records retain their one-sided meaning; `<3` is never replaced with exact 3 and `>150` is never
  replaced with exact 150 for continuous regression.
- **Legitimate in exactly one place:** the TDC benchmark reproduction, where the substitution is a
  property of the benchmark as historically shipped and must be preserved for comparability (§6). Its
  use there is a statement about the benchmark, never about experimental measurement.

### C. Censor-aware regression (Tobit / censored-normal, interval-censored likelihood, survival-style)

- **Assumptions.** Tobit assumes a correctly specified latent linear predictor and homoscedastic
  Gaussian errors on the modelled scale (here log10). Both are strong for fingerprint regression on
  1,102 compounds; violated heteroscedasticity biases the censored contributions specifically.
  Interval-censored likelihood is the most honest formulation — (-∞, log10 3] and [log10 150, ∞) are
  exactly the observations' information content — and needs the same distributional commitment.
  Survival framing (AFT) fits mechanically but imports a hazard vocabulary that has no DMPK meaning
  here and would confuse rather than clarify.
- **Compatibility with molecular descriptors/fingerprints.** Fine for a *linear* predictor: any
  descriptor or fingerprint matrix can drive a censored-normal likelihood.
- **Can Random Forest / Ridge incorporate censoring directly? No.** Ridge minimises squared error
  against point targets and has no censored likelihood; scikit-learn's RandomForestRegressor has no
  censored-target support. Bounds could only enter through a custom likelihood, a gradient-boosting
  objective written by hand, or a survival forest — each of which replaces the baseline with a
  different model, so the "simple baseline" comparison would no longer be measuring representations.
- **Implementation burden.** Moderate and, crucially, *unshared*: it applies to one model family and
  leaves the RF/Ridge baselines unable to participate, so the headline comparison would be
  apples-to-oranges.
- **Interpretability.** Coefficients are interpretable; the *predictions* are of a latent value that is
  unobservable for a third of the data, which is harder to communicate honestly, not easier.
- **Appropriate for a student v1? No, not as the primary analysis.** It is the statistically strongest
  option and it is the right answer to "how would you do this properly at scale" in an interview — but
  the v1 question is *how well do simple representations predict measured HLM clearance, and where do
  they fail*. Censor-aware machinery does not help answer that and costs the comparability of the
  baselines. It is retained as an **optional** robustness check (S3), which is the correct use of it.

### D. Two-part / hybrid formulation

Separate the two questions the data actually answer:

- **assay-range classification** — BELOW and ABOVE are directly observed from explicit `<3` and
  `>150` qualifiers; IN-RANGE is assigned to null-relation records under the dataset-specific working
  inference. All 1,102 records receive an assignment, but 13 IN-RANGE assignments are specifically
  boundary-ambiguous; range membership is not completely observable for all records;
- **regression within the inferred quantifiable-range cohort** — supplied numeric values, with the
  13 boundary-ambiguous records retained under the working inference and assessed through S1.

This preserves the censored records' information (they are full training examples for the classifier,
where their label is *exactly* what was observed) while keeping the regression target free of invented
values. It needs no custom likelihood, works identically for Ridge, RF or anything else, and maps
directly onto how a DMPK scientist reads the assay: *is this compound too stable to measure, measurable,
or too unstable to measure — and if measurable, what is the value?* **This is the recommended spine.**

### E. Sensitivity-analysis strategy

One primary policy plus a small, prespecified set of sensitivity analyses is preferable to attempting a
perfect censoring solution in the main model. Censoring here is not a nuisance to be eliminated; it is a
property of the measurement that no analysis choice can remove. The scientific requirement is that the
primary conclusions be shown not to hinge on the arbitrary parts of the choice. Prespecification before
any model is fitted is what prevents this from becoming a search over analyses — hence §10, fixed now.

---

## 4. The actual prediction target

Four distinct quantities, routinely conflated, must be kept apart:

| Quantity | Symbol | Observable? | Which strategy predicts it |
|---|---|---|---|
| Latent true intrinsic clearance | CLint | Never directly; only bounded for censored records | Target of C only, and only under its distributional assumptions |
| Observed assay CLint, conditional on falling in the quantifiable range | log10 CLint \| in-range | Reported for the 744 records of the inferred quantifiable-range cohort (731 interior + 13 boundary-ambiguous) | **Primary regression (A/D)** |
| Assay-range category | below / in / above | BELOW and ABOVE directly observed from explicit qualifiers; IN-RANGE inferred for 744 null-relation records, including 13 boundary-ambiguous assignments | **Range classifier (D)** |
| Boundary-substituted benchmark label | TDC `Y` | Yes, but partly fabricated | Benchmark track only (B) |

The primary regression estimates **E[log10 CLint_observed | quantifiable range]**. It does not estimate
the unconditional latent CLint, and the project will not describe it as doing so. For censored compounds
the exact value is **unknowable from this data**, and no component of this study will emit a point
prediction claiming otherwise.

**Deployment semantics — two stages, in this order.** For a new compound: (1) predict the assay-range
class; (2) predict log10 CLint only if the predicted class is *quantifiable*. If the predicted class is
below- or above-range, the reported output is the range statement plus the corresponding bound, not a
number. This is the only formulation in which every number the pipeline emits corresponds to something
the assay could have measured.

---

## 5. Statistical consequences of dropping censored observations

Censored compounds are **not** a random sample of chemical space. Censoring status is determined by the
outcome itself, so the excluded set is chemically structured by construction:

- compounds below `<3` are the metabolically stable ones — characteristically low lipophilicity, few
  soft spots, blocked or sterically shielded metabolic positions;
- compounds above `>150` are the unstable ones — characteristically lipophilic, with exposed,
  readily-oxidised motifs.

Excluding both tails therefore removes the two chemically most coherent, and most
pharmaceutically consequential, regions of the target distribution. Consequences, stated in advance:

1. **Compressed target range.** The retained target spans log10 3 = 0.477 to log10 150 = 2.176, i.e.
   **1.70 log10 units**. The full distribution is open-ended at both ends. A two-fold error (0.301
   log10 units) is **~18% of the entire retained span** — so the headline metric is being measured
   against a deliberately narrow target, and this must be stated wherever the metric is.
2. **Deflated R² and Spearman.** Both depend on target variance, which truncation reduces. Values will
   look worse than a study that kept the substituted boundaries — and will be *more* honest. The
   converse trap matters more: a boundary-substituted study inflates R² by adding variance that is
   partly fabricated. The two numbers are not comparable and will never be compared.
3. **Unrepairable by reweighting.** Selection is on y, not X.
4. **Changed meaning.** The model predicts *"CLint within the quantifiable assay range"*, not the
   chemical-space clearance distribution.

**Is that acceptable for v1? Yes — conditionally, and only because it is paired with the range
classifier.** Complete-case regression *alone* would be a genuine weakness: it would silently drop a
third of the data and quietly redefine the scientific question. Complete-case regression *plus* a
classifier trained on all 1,102 records answers both halves — which range, and what value if
measurable — with every censored record still doing work and no fabricated target anywhere. That is
defensible for v1 and is straightforwardly explainable in a DMPK interview.

---

## 6. Benchmark / science separation

**Benchmark track — TDC `Clearance_Microsome_AZ`.** Used exactly as shipped. Official split and official
metric preserved. OBSERVED: TDC contains no `<` or `>` qualifiers; all 274 ChEMBL `<3` records appear as
bare 3 and all 84 `>150` records as bare 150; TDC has 287 values exactly 3, of which 274 match `<3`
source records and 13 match null-relation records
([REVIEW_SUMMARY.md](../reports/REVIEW_SUMMARY.md)). Boundary substitution stays in place here because it
is part of the benchmark's historical representation and removing it would destroy the comparability
that is the benchmark's only purpose. Results are reported **solely as benchmark comparability** —
never as accuracy on experimental measurements.

**Science track — direct ChEMBL CHEMBL3301370.** Retains qualifier information per record and applies
the policy in §9. For continuous regression, **never replace `<3` with exact 3 or `>150` with exact
150**, in either the primary analysis or any sensitivity analysis. Censored records retain their
one-sided meaning. Boundary substitution is allowed only in the separate TDC benchmark-reproduction
track, which is reproduced as distributed.

**Why the separation must remain.** The two tracks have different targets (§4): the benchmark label is
partly fabricated, the science label is not. Reporting them together would let benchmark numbers borrow
the credibility of experimental measurement, and would let the science track be judged against metrics
computed on invented values. Additionally, the datasets are OBSERVED not to be strictly identical
despite equal row counts — 1,097 strict structure matches, five unmatched on each side, four tautomer
spellings and one hydrate representation — so they are not interchangeable even before censoring is
considered. Neither track's numbers may be quoted as the other's.

---

## 7. Hepatocyte secondary (CHEMBL3301372)

**Recommendation: the same policy structure, with one deviation and reduced status.**

The same qualifier pattern is observed (104 `<3`, 15 `>150`, 0 explicit `=`, 289 null, all boundaries at
3/150), so the §2 ruling and the §9 policy transfer unchanged in *kind*: the 289 null-relation HH records
are likewise the assay's **inferred quantifiable-range cohort**, on the same dataset-specific working
inference and with the same refusal to read NULL as documented equality.

OBSERVED, and materially simpler than HLM: CHEMBL3301372 has **0 null-relation records at 3 and 0 at
150** ([REVIEW_SUMMARY.md](../reports/REVIEW_SUMMARY.md)). The HH cohort carries **no boundary-ambiguous
members**; all 289 lie strictly inside the interval. The ambiguity of §2(d) is therefore confined to the
HLM assay, and no HH-side analogue of S1 is required or defined.

Two adjustments:

1. **Collapse the range classifier to two classes** — below-range (104) vs quantifiable (289) — or keep
   the range component descriptive only. 15 above-range records out of 408 (3.7%) cannot support a third
   class: at any reasonable split there would be a handful per fold, and any per-class metric on them
   would be noise. The 15 are reported as a count and not modelled as a class.
2. **Regression on the 289 in-range records is secondary and descriptive.** 289 compounds is a small
   training set; it is reported for comparison of failure modes with HLM, not as a headline result.

Paired analysis stays as the frozen memo specifies: 187 shared compounds (OBSERVED: 187 shared molecule
IDs **and** 187 shared strict canonical structures, with no disagreement between the two identity
definitions), rank-based agreement only, no raw HLM:HH ratio, no physiological scaling. Censoring adds a
constraint the frozen memo does not yet state, and this memo preserves it unchanged: **the primary rank
correlation is restricted to pairs whose members are inferred to be in-range in both assays** — i.e.
both members must belong to their own assay's inferred quantifiable-range cohort. A rank correlation
computed across substituted boundaries would be measuring tied fabricated values, not concordance. Pairs
censored in one or both assays are reported as a cross-tabulation of range categories — which is itself
informative (does a compound below range in HLM also fall below range in HH?) and needs no ratio and no
shared unit.

**Handling of boundary ambiguity within the pair.** Because HH contributes no boundary-coincident
null-relation records, the only ambiguity a pair can inherit is on its HLM side: a paired compound may be
one of the 13 HLM null-at-3 records. Such pairs are **included** in the primary rank correlation under
the same working inference as the primary regression. Their status remains UNRESOLVED; exclusion in S1
does not reclassify them as censored. How many of the 13 fall inside the 187-compound paired cohort is
**reported explicitly** alongside the correlation, and the
primary rank correlation is **recomputed with them excluded** as the paired-analysis limb of S1. As in
the regression, the choice between the two paired estimates is not made on which is the stronger
correlation: the inclusive estimate is primary and the exclusive one is reported beside it.

---

## 8. Biogen treatment

OBSERVED ([BIOGEN_AUDIT.md](../reports/BIOGEN_AUDIT.md)): the endpoint column is
`LOG HLM_CLint (mL/min/kg)`; 3,087 numeric values, 434 missing, of 3,521 rows. Minimum **0.675686709**
occurs **958 times (31.0% of populated values)**; q05 and q25 both equal the minimum; median 1.205312653;
maximum 3.372714293. Next distinct values upward include 0.80140371 and 0.881384657. The labels are
source-provided logs; no transformation was applied by the audit.

**This is not assumed to be censoring.** A 31% pile-up on the exact minimum is consistent with at least
four distinct mechanisms, which have different consequences:

| Candidate mechanism | Evidence that would establish it |
|---|---|
| **Assay floor / LLOQ substitution** | An upstream statement (paper, SI, repository README) of a lower limit of quantification for the HLM assay, and agreement between that limit and the pile-up value after the correct back-transformation. |
| **Clipping / winsorisation in preprocessing** | A documented clipping rule; **or** a distributional signature: a *gap* immediately above the minimum with no values in between. A genuine floor shows a continuum approaching it; clipping shows an empty interval then a spike. This is checkable from the frozen CSV with no new acquisition. |
| **Preprocessing artefact** | The identical value appearing as the minimum of *other* endpoints in the same file, or a value that is exactly log(round number) — 10^0.675686709 ≈ **4.74 mL/min/kg** if base 10, e^0.675686709 ≈ **1.97** if natural log. A round native limit (e.g. exactly 2, or a defined value) recovered under one base and not the other would simultaneously resolve the log base, which is itself UNRESOLVED. |
| **Genuine value distribution** | A plausible mechanism for 958 distinct compounds sharing a clearance value to nine decimal places. Implausible on its face, but it is the null that the others must displace, and it is not excluded by the audit. |

Also required before Biogen carries any weight: whether the authors' source repository or SI ships a
per-row qualifier or censor column (the downloaded CSV does not — OBSERVED/UNRESOLVED), and the
derivation of the bodyweight-normalised `mL/min/kg` labels, which is UNRESOLVED from the CSV and README.

**Interim treatment.** Biogen stays a **within-dataset replication set**, per the frozen selection memo
— never a naive transfer set, and specifically:

- it is **not** used to fit, tune or select the primary HLM model, and not used to choose this policy;
- any Biogen result is reported **twice**, with and without the 958-record floor stratum, both labelled,
  so the reader can see the pile-up's influence directly;
- no numeric comparison, back-transformation or scaling against the AstraZeneca labels until the log
  base *and* the pile-up mechanism are resolved. The units differ (`mL/min/kg` bodyweight-normalised vs
  `microL/min/mg` protein) and the transformation is undocumented; comparing them now would produce a
  number with no defined meaning.

---

## 9. Recommended v1 policy

**Two-part formulation (D) with complete-case regression (A) on the in-range stratum, plus prespecified
sensitivity analyses (E). Boundary substitution (B) confined to the benchmark track. Censor-aware
regression (C) as an optional robustness check only.**

**Component 1 — Primary regression.**
Target: log10 of HLM CLint. Training and evaluation set: the **inferred quantifiable-range cohort of all
744 null-relation records** of CHEMBL3301370. This comprises **731 interior records (3 < value < 150)
plus 13 ambiguous lower-boundary records (value exactly 3, relation and standard_relation both null)**.
**N = 744.**

Inclusion of the 13 is a **prespecified working inference, not a claim that their exact censoring status
is known** — that status is UNRESOLVED AFTER FROZEN-METADATA AUDIT (§2(d)). Their influence is measured
in **S1** by excluding them without reclassifying them as censored. The cohort is not described as a set
of documented exact measurements.

**Component 2 — Three-class assay-range classifier.**
Three classes on **all 1,102 records**:

| Class | Definition | n | % |
|---|---|---:|---:|
| **BELOW** | explicit `<` at 3 | 274 | 24.9 |
| **IN-RANGE** | null relation, under the dataset-specific working inference of §2 | 744 | 67.5 |
| **ABOVE** | explicit `>` at 150 | 84 | 7.6 |

The BELOW and ABOVE labels are OBSERVED — they are read directly from the deposited qualifier. The
IN-RANGE label is **INFERRED**, not observed: it is the dataset-specific working inference, and the memo
labels it as such wherever the classifier is reported.

**Boundary-ambiguity flag (binding).** **13 of the 744 IN-RANGE labels are boundary-ambiguous** — the
null-at-3 records, whose true class could be BELOW. This must be stated wherever the class definitions or
per-class metrics are reported, not relegated to a footnote. The same 13-record exclusion is prespecified
as a **complete classifier sensitivity analysis** (S1, classifier limb): refit each classifier after
excluding the ambiguous records from training, and evaluate on the remaining held-out records using the
unchanged prespecified fold assignments. Evaluate **all prespecified classifier metrics and all three
classes wherever the metric permits**, including ABOVE. Refitting can alter predictions for any class;
unchanged ABOVE-class membership is not grounds for an exemption. S1 excludes the 13 from whichever
training or evaluation folds they occupy: its regression cohort has N = 731, while its three-class
classifier cohort has N = 1,089 (274 BELOW + 731 IN-RANGE + 84 ABOVE).

Every explicitly censored record is a full classifier training example whose BELOW or ABOVE label comes
from its deposited qualifier. IN-RANGE assignments remain inferred, including the flagged 13 in the
primary analysis. No boundary value is substituted.

**Component 3 — Censored records as one-sided evaluation data, never as primary regression point targets.**
The in-range regression is applied to the 358 censored compounds and scored on *directional
correctness*: for a `<3` compound the prediction should be ≤ log10 3; for a `>150` compound, ≥ log10 150.
Reported as the fraction satisfying the bound, plus the magnitude of violation for those that do not.
This extracts precisely the information a censored likelihood uses, requires no distributional
assumption, no custom objective and no change of model family, and works identically for every baseline.

**Why this and not the alternatives.** B is rejected for the science track because it fabricates 358
exact targets at two spikes and makes its own failure undetectable. C is rejected as primary because it
cannot be carried by the Ridge and Random Forest baselines without replacing them, which would break the
one comparison v1 exists to make, and because its predictions concern a latent quantity that is
unobservable for a third of the data — sophistication bought at the cost of the project's
interpretability, for a question it does not help answer. A alone is rejected because discarding a third
of the data and both tails, with nothing in its place, silently narrows the science. The recommended
combination keeps the regression target honest, keeps every record in use, keeps all baselines
comparable, and is explainable in two sentences to a DMPK scientist.

**Shared-split constraint.** One prespecified split/fold assignment is used for the regression, the
classifier and every sensitivity analysis. A compound's fold must be identical across all components, so
that Component 3's evaluation set is genuinely held out from Component 1 and the two components can be
composed into the two-stage pipeline of §4 without leakage.

---

## 10. Prespecified sensitivity analyses

Fixed now, before any model is fitted. Deliberately three, to keep researcher degrees of freedom
bounded. All reuse the single prespecified split. Each is reported whatever it shows.

| ID | Analysis | Question it answers |
|---|---|---|
| **S1** | **Rerun the complete primary modelling workflow with the 13 null-at-3 records excluded (HLM regression N = 731).** The same representations, model families, prespecified fold assignments and evaluation are re-executed end to end. Scope: Component 1 regression and its Component 3 directional evaluation; full refitting of the Component 2 three-class classifier (N = 1,089), with all prespecified classifier metrics and all three classes evaluated wherever the metric permits; and the §7 paired rank correlation. No class is exempted. | Does the ambiguity that is UNRESOLVED AFTER FROZEN-METADATA AUDIT affect any conclusion? |
| **S2** | Score the lower-censored (274) and upper-censored (84) subsets **separately** under the Component 3 directional check, and report the classifier's per-class performance alongside. | Are the two tails equally predictable? Asymmetry here is a scientific finding about where the representations fail. |
| **S3** *(optional / stretch; secondary only)* | Censored-normal (Tobit) refit on all 1,102 with interval targets (-∞, log10 3], point, [log10 150, ∞), **linear predictor only**, compared on **model ranking only** — not used to claim absolute performance. | Did complete-case truncation drive the conclusions? The honest answer to the reviewer's obvious objection. Explicitly out of scope if time-constrained; its omission is reported, not hidden. |

**What S1 compares, fixed in advance.** Three things, and only these: (i) **model ranking** — the order
of the representation/model combinations; (ii) **the major effect and feature-level conclusions** where
the model family admits them (e.g. which descriptors or fingerprint regions carry the signal, and the
direction of the dominant effects) — where a model family admits no such reading, that is stated rather
than substituted with a proxy; (iii) the **headline evaluation metrics** (MAE on log10 primary, with
RMSE, Spearman and fraction-within-two-fold alongside), the prespecified directional evaluation, and
**all prespecified classifier metrics**: macro-F1, per-class precision and recall for BELOW, IN-RANGE
and ABOVE, balanced accuracy, MCC, the full confusion matrix, and the adjacent/non-adjacent error split.
All three classes are evaluated wherever the metric permits; ABOVE is not exempted.

**S1 is not a selection procedure.** The 744-record analysis is **primary** and remains primary. The
choice between the 744-record and 731-record analyses is **not** made on the basis of which performs
better, and no result of S1 promotes the 731-record analysis to primary. S1 exists to show whether the
conclusions depend on 13 records whose status is unresolved; a difference is a *reported finding about
the fragility of the conclusions*, never a reason to switch headline analyses.

**Decision rule, fixed in advance.** The primary policy (§9) is reported as the headline regardless of
what S1–S3 show. Sensitivity analyses are reported alongside it and inform the stated limitations. A
sensitivity result **never** silently replaces the primary analysis, and never replaces it on
performance grounds at all; if any of them materially changes the model ranking, that fact is reported as
the finding.

---

## 11. Claims the resulting model may and may not make

**May claim:**

- Predicts log10 human HLM intrinsic clearance for compounds whose clearance falls within the assay's
  quantifiable range of 3–150 µL·min⁻¹·mg⁻¹, with the stated error on held-out compounds.
- Classifies compounds into BELOW / IN-RANGE / ABOVE, with the stated per-class performance, using all
  1,102 records — stating that BELOW and ABOVE are read from deposited qualifiers, that IN-RANGE rests on
  the dataset-specific working inference, and that 13 IN-RANGE labels are boundary-ambiguous.
- Predicts, for compounds outside the range, the **direction** of censoring and a consistent bound.
- Identifies the chemical characteristics associated with large prediction error — the failure analysis
  that is the study's stated purpose.
- Reports a benchmark number on TDC `Clearance_Microsome_AZ` as comparability with prior published work
  on that benchmark.

**May not claim:**

- A point prediction of CLint for any compound whose measurement was censored. That value is not in the
  data.
- Prediction of latent true CLint across the full chemical-space distribution. The regression is
  conditional on assay-range membership (§4).
- That its R² or Spearman is comparable to a study using boundary-substituted targets.
- That the two-fold band is an **irreducible noise floor**. It is an **experimental repeatability
  reference**: a scale for judging whether an error is large relative to the measurement itself.
  Sub-two-fold performance is neither impossible nor a validity ceiling.
- Any statement about hepatocyte clearance, or about HLM:HH relationships, beyond the secondary
  descriptive rank-based analysis of §7. No physiological scaling, no IVIVE.
- Any transfer claim to the Biogen data, or any numeric comparison with it, while §8 is unresolved.
- That null-relation ChEMBL records are documented exact or equality measurements (§2). In particular, no
  output of this project may state or imply that a ChEMBL NULL `standard_relation` means `=` in general.
  The inferred quantifiable-range cohort is named as an inference about this depositor's convention
  across these three assays.
- That the censoring status of the 13 HLM null-at-3 records is known. It is **UNRESOLVED AFTER
  FROZEN-METADATA AUDIT**, and their inclusion in the primary cohort does not resolve it.
- That S1 selects between the 744- and 731-record analyses, or that the better-performing of the two is
  the preferred one. The 744-record analysis is primary by prespecification (§10).

---

## 12. Remaining UNKNOWNs

| ID | UNKNOWN | Named check | Effect on this policy |
|---|---|---|---|
| **U1** | What, if anything, ChEMBL documents about the semantics of a NULL `standard_relation`. | Read the ChEMBL schema documentation and data FAQ for `ACTIVITIES.standard_relation`. Documentary, external to the frozen data — distinct from U2, which was internal and is closed. | None. The policy rests on assay-internal evidence and never asserts documented equality. No outcome of this check would license the general claim that NULL means `=`; at most it would constrain how the field should be read, and the memo would be amended to say exactly what was found. |
| **U2** — **CLOSED** | Whether other activity fields disambiguate the 744 — `activity_comment`, `data_validity_comment`, `text_value`, `standard_text_value`, `standard_flag`. | **Check performed.** Tabulated from the already-frozen raw bytes. Result: all four text/comment fields null for the 13; `standard_flag = 1` for them **and** for the explicitly censored records, so it does not discriminate; original and standard values both 3.0; original and standard relations both null (§2(d)). | None to the policy. The check did **not** resolve the 13 and does **not** retire S1 — S1 is now load-bearing rather than provisional. No further search through the existing raw metadata is proposed. |
| **U3** | Whether 3 and 150 are the *documented* assay limits, rather than inferred ones. | Extract the assay description / `assay_parameters` text from the frozen ChEMBL assay metadata. | None. Strengthens §1 from INFERRED to OBSERVED. |
| **U4** — **UNRESOLVED AFTER FROZEN-METADATA AUDIT** | Per-record censor status of the 13 HLM null-relation records at exactly 3. | **No further check is proposed against the frozen metadata.** U2 was the named check; it was executed and returned no discriminating field. Resolution would require information the frozen sources do not carry, and none is assumed. | Handled by S1, and by the boundary-ambiguity flag on the IN-RANGE class (§9). The 13 are included in the primary analysis as a prespecified working inference, not as a resolved classification. |
| **U5** | Biogen: mechanism of the 958-record pile-up; log base; derivation of bodyweight-normalised labels; existence of an upstream qualifier column. | §8 table. | Biogen quarantined from the primary track until resolved. |
| **U6** | Whether censoring correlates with chemical class in ways that make the in-range stratum unrepresentative in a *specific*, nameable way, beyond the general argument of §5. | Descriptive comparison of frozen descriptor distributions across the three range classes — read-only, no modelling, and legitimately doable before fitting. | Does not change the policy; sharpens the limitation statement. |

---

## PROPOSED FROZEN CENSORING POLICY

*For direct insertion into the preregistration.*

1. **Qualifier semantics.** ChEMBL `standard_relation` is retained per record. `<` and `>` denote
   one-sided bounds at the assay's quantifiable limits of 3 and 150 µL·min⁻¹·mg⁻¹ — `<` occurring at the
   lower boundary and `>` at the upper. A null relation denotes *absence of a deposited qualifier*; it is
   never recoded to `=`, and **no output of this project states or implies that a ChEMBL NULL
   `standard_relation` means `=` in general.** On the assay-internal evidence that qualifiers occur only
   at 3 and 150, that no explicit `=` exists in these assays, that no observed value lies outside
   [3, 150], that the null-relation values lie overwhelmingly inside the experimental range, and that no
   inspected metadata field contradicts it, the null-relation records are designated the **inferred
   quantifiable-range cohort**. This is a dataset-specific working inference about the depositor's
   convention across these three assays — not a documented ChEMBL-wide semantics of NULL, not a claim that the
   records are documented exact or equality observations, and not a claim of exactness.

2. **Primary regression.** log10 HLM CLint, fitted and evaluated on the **inferred quantifiable-range
   cohort: all 744 null-relation records of CHEMBL3301370, comprising 731 interior records
   (3 < value < 150) plus the 13 ambiguous lower-boundary records at value exactly 3. Primary HLM
   N = 744.** Inclusion of the 13 is a prespecified working inference and **not** a claim that their
   exact censoring status is known (item 13). Censored records are never assigned point targets in this
   component.

3. **Three-class assay-range classifier.** Fitted on all 1,102 records, with classes defined as:
   **BELOW** = explicit `<` at 3 (274); **IN-RANGE** = null relation under the dataset-specific working
   inference of item 1 (744); **ABOVE** = explicit `>` at 150 (84). BELOW and ABOVE are read from
   deposited qualifiers; IN-RANGE is inferred, and is reported as inferred. **13 of the 744 IN-RANGE
   labels are boundary-ambiguous and this is flagged wherever the classes or their metrics are
   reported.** Observed qualifiers are retained; IN-RANGE assignment is explicitly inferred. No boundary
   value is substituted. S1 excludes the 13 ambiguous records from their assigned training and
   evaluation folds, refits each classifier on the remaining training records, and evaluates **all
   prespecified classifier metrics and all three classes wherever the metric permits**. The S1
   classifier cohort is N = 1,089. ABOVE is not exempted: refitting can alter predictions for any class.

4. **Censored records in evaluation.** The 358 explicitly censored records are used as one-sided
   evaluation data for directional correctness (`<3` → prediction ≤ log10 3; `>150` → prediction ≥
   log10 150), never as point targets for the primary continuous regression. Their explicit qualifiers
   supply the classifier labels; optional S3 retains their one-sided bounds in its censored likelihood.

5. **Reported quantity.** The primary regression estimates E[log10 CLint_observed | quantifiable range]. No
   primary component predicts latent CLint for censored compounds, and no exact value is reported for any
   censored observation. Deployment is two-stage: range class first, value only if quantifiable.

6. **Metrics.** Regression: MAE on log10 primary; RMSE, Spearman and fraction within two-fold
   (|Δlog10| ≤ 0.301) secondary; R² reported only with the truncated-variance caveat and against a
   mean-predictor baseline. The two-fold band is the **experimental repeatability reference** and is
   never described as an irreducible noise floor. Classifier: macro-F1, per-class precision and recall,
   balanced accuracy, MCC, full confusion matrix, and the split between adjacent and non-adjacent
   (below↔above) errors. **Accuracy alone is not reported** — the majority class is 67.5%.

7. **Splits.** A single prespecified split/fold assignment is shared by the regression, the classifier
   and all sensitivity analyses. A compound's fold is identical across components.

8. **Benchmark separation.** TDC `Clearance_Microsome_AZ` is used as shipped, with its official split
   and metric, and reported solely as benchmark comparability, **unchanged by this amendment** — it
   remains the historical benchmark representation. Its boundary substitutions are a property of that
   historical representation. **Boundary substitution is prohibited throughout the direct-ChEMBL
   science track, including every sensitivity analysis**: never replace `<3` with exact 3 or `>150`
   with exact 150 for continuous regression. Censored records retain their one-sided meaning. Boundary
   substitution is allowed only in the separate TDC benchmark-reproduction track because that dataset
   is reproduced as distributed. Benchmark and science metrics are never compared to each other.

9. **Hepatocyte (CHEMBL3301372).** Same policy structure; its 289 null-relation records are that assay's
   inferred quantifiable-range cohort, and OBSERVED it contains **no** null-relation records at 3 or 150,
   so it carries no boundary-ambiguous members. The range component is collapsed to below-range vs
   quantifiable because 15 above-range records cannot support a third class. Regression on the 289
   in-range records is secondary and descriptive. The 187-compound paired analysis is rank-based only and
   **the primary rank correlation is restricted to compounds inferred to be in-range in both assays**,
   with censored pairs reported as a range-category cross-tabulation. Any pair inheriting HLM-side
   boundary ambiguity (one of the 13) is included, the count is reported, and the correlation is
   recomputed without them as the paired limb of S1. No ratios, no physiological scaling.

10. **Biogen.** Within-dataset replication only. Not used to fit, tune or select the primary model. The
    958-record pile-up at the minimum is **not** assumed to be censoring; every Biogen result is
    reported with and without that stratum, labelled. No numeric comparison or back-transformation
    against the AstraZeneca labels until the log base and the pile-up mechanism are documented.

11. **Prespecified sensitivity analyses.** **S1 — rerun the complete primary modelling workflow with the
    13 null-at-3 records excluded (S1 HLM regression N = 731)**, comparing model ranking, the major effect and
    feature-level conclusions where the model family admits them, and the headline evaluation metrics,
    across the regression and its directional evaluation, the fully refitted three-class classifier
    and the paired rank correlation. S1 evaluates all prespecified classifier metrics and all three
    classes wherever the metric permits, with no ABOVE-class exemption. S2 lower- and upper-censored
    subsets scored separately; S3 *(optional, secondary)* censored-normal/Tobit refit compared on model
    ranking only — never primary. No further analyses are added after results are seen.

12. **S1 is not a selection rule.** The 744-record analysis is primary and stays primary. The choice
    between the 744-record and 731-record analyses is **not** made on the basis of which performs better,
    and no S1 outcome promotes the 731-record analysis to headline status. The primary policy remains the
    headline regardless of what S1–S3 show; a material change in model ranking is reported as a finding
    about the fragility of the conclusions.

13. **Status of the 13 null-at-3 records: UNRESOLVED AFTER FROZEN-METADATA AUDIT.** The frozen metadata
    has been inspected (original and standard values both 3.0; original and standard relations both null;
    `activity_comment`, `data_validity_comment`, `text_value` and `standard_text_value` all null;
    `standard_flag = 1`, which is also 1 for explicitly censored records) and contains no field that
    distinguishes them as quantified versus censored. **No further searching of the existing raw metadata
    for this answer is proposed.** The records are carried in the primary analysis as a prespecified
    working inference, flagged in the classifier, and excluded in S1.

14. **Open UNKNOWNs at freeze.** U1 ChEMBL documentary semantics of NULL (external, documentary); U2
    **closed** — the frozen activity fields were examined and do not discriminate; U3 documented assay
    limits; U4 per-record status of the 13 null-at-3 records, **unresolved after the frozen-metadata audit
    with no further frozen-data check proposed**; U5 Biogen pile-up mechanism and log base; U6 chemical
    non-randomness of the censored strata. None blocks v1. None is resolved by assumption.
