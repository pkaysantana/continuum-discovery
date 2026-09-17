# CENSORING_POLICY_MEMO

Prospective policy for the treatment of censored and unqualified clearance observations in the DMPK
compound-to-exposure study. Written **before** any model is fitted, any representation is chosen, any
hyperparameter is selected and any performance number is seen.

Authority: [DATASET_SELECTION_MEMO.md](DATASET_SELECTION_MEMO.md) remains the frozen scientific source
of truth for dataset selection. This memo supplies the censor-handling rules that memo item 5 requires
("Explicit censoring and UNKNOWN handling rules must be applied rigorously across all datasets") and
that the audit's stop condition defers to review. It does not reopen dataset selection.

Where explanatory narrative and the PROPOSED FROZEN CENSORING POLICY differ, the numbered frozen-policy
clauses govern. This precedence applies within this memo and does not override the higher-level
authority of DATASET_SELECTION_MEMO.md. Analysis choices are fixed before predictive modelling; results
cannot be used to add, omit or substitute a v1 analysis. The U6 completion-or-omission deadline is also
before the first predictive model is fitted.

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

INFERRED: the observed assay pattern and assay description are consistent with working lower and upper
quantifiable-range boundaries of 3 and 150, respectively; their interpretation as formal quantification
limits remains inferred rather than independently documented. The frozen descriptions state an
experimental range of `<3` to `>150`, which does not independently establish formal quantification
limits. UNKNOWN U3 retains that distinction.

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

*Provenance note:* [CENSORING_METADATA_CHECK.md](../reports/CENSORING_METADATA_CHECK.md) records the
already-observed field-level results, input filenames and hashes, frozen audit checkpoint, and raw-hash
verification. It is a new post-audit record; [REVIEW_SUMMARY.md](../reports/REVIEW_SUMMARY.md),
[AUDIT_REVIEW.md](../reports/AUDIT_REVIEW.md) and the other frozen audit outputs remain unchanged.

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
landed on the working lower boundary, or censored records whose qualifier was never deposited. They are **not**
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

### C. Censor-aware likelihood methods — OUT OF SCOPE FOR V1

Censor-aware likelihood methods exist to use a censored record's one-sided information without
inventing an exact target. For example, a censored-normal likelihood assigns probability to the
reported interval under assumptions about a latent continuous outcome and its errors. Such methods
require additional distributional and model-family commitments; they do not reveal the unknown
clearance of an individual censored compound.

**Censored-normal/Tobit modelling is a plausible future extension but is outside the frozen v1
analysis. It will not be introduced after primary results are seen.** No censor-aware model replaces it
in v1. There is no run/omit decision remaining after freeze.

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

One primary policy plus the single prespecified censoring-policy sensitivity analysis S1 is preferable
to attempting a perfect censoring solution in the main model. The stratified tail diagnostic is a
separate descriptive diagnostic, not another sensitivity analysis. Censoring is a
property of the measurement that no analysis choice can remove. The scientific requirement is that the
primary conclusions be shown not to hinge on the arbitrary parts of the choice. Prespecification before
any model is fitted is what prevents this from becoming a search over analyses — hence §10, fixed now.

---

## 4. The actual prediction target

Four distinct quantities, routinely conflated, must be kept apart:

| Quantity | Symbol | Observable? | Which strategy predicts it |
|---|---|---|---|
| Latent true intrinsic clearance | CLint | Never directly; only bounded for censored records | Not estimated in frozen v1; C is out of scope |
| Reported HLM clearance, conditional on prespecified cohort assignment | log10 CLint_reported \| assigned to the inferred quantifiable-range cohort | Reported values for 744 records (731 interior + 13 boundary-ambiguous); cohort membership is inferred | **Primary regression (A/D)** |
| Assay-range category | below / in / above | BELOW and ABOVE directly observed from explicit qualifiers; IN-RANGE inferred for 744 null-relation records, including 13 boundary-ambiguous assignments | **Range classifier (D)** |
| Boundary-substituted benchmark label | TDC `Y` | Yes, but partly fabricated | Benchmark track only (B) |

The primary regression estimates
**E[log10 CLint_reported | assigned to the inferred quantifiable-range cohort]**. It predicts reported
HLM clearance conditional on this prespecified cohort assignment. It does **not** estimate latent
full-range clearance for all 1,102 compounds. For censored compounds the exact clearance is not known
from these data; the tail ordering scores assess relative prediction order only.

**Deployment semantics — two stages, in this order.** For a new compound: (1) predict the assay-range
class; (2) predict log10 reported HLM clearance only if the predicted class is IN-RANGE, under the
working inference used for that cohort. Otherwise report the predicted BELOW or ABOVE category relative
to the working boundaries, not a numerical clearance estimate. A predicted category is not proof that
the compound's unknown true clearance satisfies the corresponding bound.

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

1. **Compressed target range.** The working interval spans log10 3 = 0.477 to log10 150 = 2.176, i.e.
   **1.70 log10 units**. The full distribution is open-ended at both ends. A two-fold error (0.301
   log10 units) is **~18% of this working interval** — so the headline metric is being measured
   against a deliberately narrow target, and this must be stated wherever the metric is.
2. **Deflated R² and Spearman.** Both depend on target variance, which truncation reduces. Values will
   look worse than a study that kept the substituted boundaries — and will be *more* honest. The
   converse trap matters more: a boundary-substituted study inflates R² by adding variance that is
   partly fabricated. The two numbers are not comparable and will never be compared.
3. **Unrepairable by reweighting.** Selection is on y, not X.
4. **Changed meaning.** The model predicts reported HLM clearance conditional on assignment to the
   inferred quantifiable-range cohort, not latent full-range clearance for all 1,102 compounds.

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

1. **Collapse the range classifier to two classes** — BELOW (104 explicit `<3` records) vs IN-RANGE
   (289 null-relation records assigned under the working inference). This two-class classifier is the
   binding v1 treatment. 15 above-range records out of 408 (3.7%) cannot support a third
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

**Interim treatment.** Biogen stays a **within-dataset external replication/robustness set**, per the
frozen selection memo. It is not direct held-out testing of an AstraZeneca-trained model, and specifically:

- it is **not** used to fit, tune or select the primary HLM model, and not used to choose this policy;
- any Biogen result is reported **twice**, with and without the 958-record floor stratum, both labelled,
  so the reader can see the pile-up's influence directly;
- no numeric comparison, back-transformation or scaling against the AstraZeneca labels until the log
  base *and* the pile-up mechanism are resolved. The units differ (`mL/min/kg` bodyweight-normalised vs
  `microL/min/mg` protein) and the transformation is undocumented; comparing them now would produce a
  number with no defined meaning.

---

## 9. Recommended v1 policy

**Two-part formulation (D) with complete-case regression (A) on the inferred quantifiable-range
cohort, the single censoring-policy sensitivity analysis S1, and the prespecified stratified tail
diagnostic. Boundary substitution (B) is confined to the benchmark track. Censor-aware regression (C)
is OUT OF SCOPE FOR V1.**

**Component 1 — Primary regression.**
Target: log10 of reported HLM CLint conditional on the prespecified cohort assignment. Training and
evaluation set: the **inferred quantifiable-range cohort of all
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

**Component 3 — Prediction-ordering diagnostic for the censored tails.**
The 274 explicit `<3` and 84 explicit `>150` compounds retain their one-sided information and are never
assigned exact continuous targets. For each fitted regressor, compare its held-out tail predictions
with its held-out predictions for compounds assigned to the inferred quantifiable-range evaluation
cohort. Predictions are on the model's log10-clearance scale; the diagnostic uses only their ordering.

Let L, U and Q denote the lower-censored, upper-censored and inferred in-range evaluation groups,
respectively, and let p denote a prediction. The prespecified scores are:

- **Lower-tail ordering score:** P(p_L < p_Q) + 0.5 P(p_L = p_Q).
- **Upper-tail ordering score:** P(p_U > p_Q) + 0.5 P(p_U = p_Q).

Empirically, average over every eligible tail–Q pair: a correctly ordered pair scores 1, a tie scores
0.5, and a reversed pair scores 0. The denominator is the number of eligible pairs. Use only pairs
whose two predictions come from the same fitted model and the same held-out fold or evaluation split;
neither member may have trained that fitted model. For a prespecified multi-fold evaluation, pool the
pair scores and pair counts across folds (pair-count weighting); do not compare scores from different
fitted models as if they were paired predictions. Report the tail and Q sample sizes and pair count.
A fold without eligible pairs contributes no pairs; if none are eligible overall, report undefined,
not an imputed score.

**Interpretation, identical for every model family:** 0.5 corresponds to no ordering discrimination;
values nearer 1 indicate better directional ordering. This assesses ordering only. It does **not**
estimate latent clearance values for censored compounds and does **not** prove that predictions satisfy
the unknown true numerical clearance. It requires neither invented exact targets nor extrapolation
beyond the training-target range, so the same definition applies to bounded and unbounded regressors.
Range-bounded models such as Random Forests cannot extrapolate beyond their training-target range;
absolute-bound satisfaction and violation magnitude are therefore excluded from v1 tail metrics and
from cross-model comparisons. The reporting specification is the stratified tail diagnostic in §10.

**Why this and not the alternatives.** B is rejected for the science track because it fabricates 358
exact targets at two spikes and makes its own failure undetectable. C is outside frozen v1 because it
cannot be carried by the Ridge and Random Forest baselines without replacing them, which would break the
one comparison v1 exists to make, and because its predictions concern a latent quantity that is
unobservable for a third of the data — sophistication bought at the cost of the project's
interpretability, for a question it does not help answer. A alone is rejected because discarding a third
of the data and both tails, with nothing in its place, silently narrows the science. The recommended
combination keeps the regression target honest, keeps every record in use, keeps all baselines
comparable, and is explainable in two sentences to a DMPK scientist.

**Shared-split constraint.** One prespecified split/fold assignment is used for the regression, the
classifier, S1 and the tail diagnostic. A compound's fold must be identical across all components, so
that Component 3's evaluation set is genuinely held out from Component 1 and the two components can be
composed into the two-stage pipeline of §4 without leakage.

---

## 10. Prespecified sensitivity analysis and stratified tail diagnostic

Fixed now, before any model is fitted. **S1 is the only censoring-policy sensitivity analysis.** The
stratified tail diagnostic is a descriptive evaluation, not a sensitivity analysis of the censoring
policy. Both reuse the single prespecified split and are reported whatever they show.

| Analysis | Specification | Purpose |
|---|---|---|
| **S1** | **Rerun the complete primary modelling workflow with the 13 null-at-3 records excluded (HLM regression N = 731).** Fully refit the applicable models using the same representations, model families and prespecified fold assignments; recompute every prespecified applicable metric. Scope: Component 1 regression and its Component 3 lower- and upper-tail ordering scores; full refitting of the Component 2 three-class classifier (N = 1,089), with all prespecified classifier metrics and all three classes evaluated wherever the metric permits; and the §7 paired rank correlation. No class is exempted. | Assess whether unresolved boundary ambiguity affects the conclusions, without selecting the primary cohort by performance. |
| **Prespecified stratified tail diagnostic** | Report the lower-tail ordering score for the 274 explicit `<3` records and the upper-tail ordering score for the 84 explicit `>150` records separately, using Component 3's definitions. Report those cohort totals, the actual evaluated tail and Q sample sizes, eligible pair counts, BELOW and ABOVE precision and recall, and the BELOW and ABOVE true-class rows of the full confusion matrix (all predicted-class columns). | Describe tail performance separately; differences are descriptive and exploratory within this prespecified diagnostic. |

For S1, the tail cohorts retain their explicit qualifiers, while Q excludes the 13 ambiguous records
from whichever evaluation folds they occupy; the refitted regression uses the 731-record cohort. The
same ordering definitions and all reporting requirements apply. Primary regression N = 744 and
classifier N = 1,102; S1 regression N = 731 and classifier N = 1,089.

**Tail-asymmetry interpretation.** No hypothesis test or significance threshold for tail asymmetry is
defined. Any lower-versus-upper performance difference is descriptive and exploratory within a
prespecified diagnostic, not proof of a mechanistic difference. N = 274 and N = 84 have materially
different precision; report the actual evaluation sample sizes and retain that caveat when discussing
the scores. Pair counts do not turn dependent pairs into independent compound observations.

Censored-normal/Tobit modelling is outside frozen v1 (§3C); it is not a sensitivity analysis to run or
omit after freeze and will not be introduced after primary results are seen.

**What S1 compares, fixed in advance.** Three things, and only these: (i) **model ranking** — the order
of the representation/model combinations; (ii) **the major effect and feature-level conclusions** where
the model family admits them (e.g. which descriptors or fingerprint regions carry the signal, and the
direction of the dominant effects) — where a model family admits no such reading, that is stated rather
than substituted with a proxy; (iii) the **headline evaluation metrics** (MAE on log10 primary, with
RMSE, Spearman and fraction-within-two-fold alongside), both prespecified tail ordering scores, and
**all prespecified classifier metrics**: macro-F1, per-class precision and recall for BELOW, IN-RANGE
and ABOVE, balanced accuracy, MCC, the full confusion matrix, and the adjacent/non-adjacent error split.
All three classes are evaluated wherever the metric permits; ABOVE is not exempted.

**S1 is not a selection procedure.** The 744-record analysis is **primary** and remains primary. The
choice between the 744-record and 731-record analyses is **not** made on the basis of which performs
better, and no result of S1 promotes the 731-record analysis to primary. S1 exists to show whether the
conclusions depend on 13 records whose status is unresolved; a difference is a *reported finding about
the fragility of the conclusions*, never a reason to switch headline analyses.

**Decision rule, fixed in advance.** The primary policy (§9) is reported as the headline regardless of
what S1 or the stratified tail diagnostic shows. Their results are reported alongside it and inform the
stated limitations. S1 **never** replaces the primary analysis on performance grounds; if it materially
changes model ranking, that fact is reported as a finding about robustness. The tail diagnostic remains
descriptive and exploratory, with no significance-based selection rule.

---

## 11. Claims the resulting model may and may not make

**May claim:**

- Predicts log10 reported human HLM clearance conditional on assignment to the inferred
  quantifiable-range cohort, with the stated error on held-out cohort members. The working boundaries
  are 3 and 150 µL·min⁻¹·mg⁻¹; formal quantification-limit status remains inferred.
- Classifies compounds into BELOW / IN-RANGE / ABOVE, with the stated per-class performance, using all
  1,102 records — stating that BELOW and ABOVE are read from deposited qualifiers, that IN-RANGE rests on
  the dataset-specific working inference, and that 13 IN-RANGE labels are boundary-ambiguous.
- Reports how consistently held-out predictions for explicitly censored compounds are ordered below
  or above predictions for the inferred in-range evaluation cohort, using half-credit for ties.
- Identifies the chemical characteristics associated with large prediction error — the failure analysis
  that is the study's stated purpose.
- Reports a benchmark number on TDC `Clearance_Microsome_AZ` as comparability with prior published work
  on that benchmark.

**May not claim:**

- A point prediction of CLint for any compound whose measurement was censored. That value is not in the
  data.
- Prediction of latent full-range CLint for all 1,102 compounds. The regression is conditional on
  assignment to the inferred quantifiable-range cohort (§4).
- That a tail ordering score establishes numerical clearance for a censored compound or proves that
  its prediction satisfies the unknown true numerical clearance.
- That a lower-versus-upper tail performance difference proves a mechanistic difference. Such
  differences are descriptive and exploratory, with materially different precision at N = 274 and 84.
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
| **U1** | What, if anything, ChEMBL documents about the semantics of a NULL `standard_relation`. | Read the ChEMBL schema documentation and data FAQ for `ACTIVITIES.standard_relation`. Documentary, external to the frozen data — distinct from U2, which was internal and is closed. | The policy rests on assay-internal evidence and never asserts documented equality. Evidence received before modelling requires a versioned amendment if it changes interpretation; evidence received after results may inform interpretation but cannot retroactively change the frozen analytical policy. |
| **U2** — **CLOSED** | Whether other activity fields disambiguate the 744 — `activity_comment`, `data_validity_comment`, `text_value`, `standard_text_value`, `standard_flag`. | **Check performed.** Recorded in [CENSORING_METADATA_CHECK.md](../reports/CENSORING_METADATA_CHECK.md), with frozen input and hash provenance. All four text/comment fields are null for the 13; `standard_flag = 1` for them **and** explicitly censored records; original and standard values are both 3.0 and both relations are null (§2(d)). | The check did **not** resolve the 13 and does **not** retire S1. No further search through the existing raw metadata is proposed. |
| **U3** | Whether the working boundaries of 3 and 150 are formal quantification limits. Their formal interpretation remains inferred. | The frozen assay descriptions state an experimental range of `<3` to `>150`; independent external assay documentation would be needed to establish formal quantification-limit status. | External assay documentation could confirm, refine or contradict the current interpretation. Any such evidence obtained before modelling would require a versioned amendment; evidence obtained after results are available may inform interpretation but cannot retroactively change the frozen analytical policy. |
| **U4** — **UNRESOLVED AFTER FROZEN-METADATA AUDIT** | Per-record censor status of the 13 HLM null-relation records at exactly 3. | **No further check is proposed against the frozen metadata.** U2 was the named check; it was executed and returned no discriminating field. Resolution would require information the frozen sources do not carry, and none is assumed. | Handled by S1, and by the boundary-ambiguity flag on the IN-RANGE class (§9). The 13 are included in the primary analysis as a prespecified working inference, not as a resolved classification. |
| **U5** | Biogen: mechanism of the 958-record pile-up; log base; derivation of bodyweight-normalised labels; existence of an upstream qualifier column. | §8 table. | Biogen quarantined from the primary track until resolved. |
| **U6** | Whether censoring correlates with chemical class in ways that make the inferred in-range stratum unrepresentative in a specific, nameable way. | Any descriptor-distribution comparison for this limitation must be completed and frozen BEFORE the first predictive model is fitted, or omitted from v1 entirely. Completion or omission must be recorded by that deadline. | It may not be added after model results are seen. If it is not completed and frozen before fitting, omission from v1 is binding; the limitation remains unresolved. |

---

## PROPOSED FROZEN CENSORING POLICY

*For direct insertion into the preregistration.*

1. **Qualifier semantics.** ChEMBL `standard_relation` is retained per record. `<` at 3 and `>` at 150
   carry one-sided information. The observed assay pattern and assay description are consistent with
   working lower and upper quantifiable-range boundaries of 3 and 150 µL·min⁻¹·mg⁻¹, respectively;
   their interpretation as formal quantification limits remains inferred rather than independently
   documented. A null relation denotes *absence of a deposited qualifier*; it is
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

4. **Censored-tail ordering diagnostic.** The 358 explicitly censored records retain their one-sided
   information and are never continuous point targets. For held-out predictions p_L (explicit `<3`),
   p_U (explicit `>150`) and p_Q (assigned inferred in-range evaluation cohort), report
   **lower-tail score = P(p_L < p_Q) + 0.5 P(p_L = p_Q)** and
   **upper-tail score = P(p_U > p_Q) + 0.5 P(p_U = p_Q)**. Use the same definition for every model
   family. Each correctly ordered pair scores 1, a tie 0.5, and a reversed pair 0. Pairs must come
   from the same fitted model and held-out fold/split; pool eligible pair scores and counts across
   prespecified folds as in §9. A score of 0.5 means no ordering discrimination; values nearer 1 mean
   better directional ordering. This assesses ordering only, neither estimating latent censored
   clearance nor proving that predictions satisfy unknown true numerical clearance. It requires no
   extrapolation beyond the training-target range. Absolute-bound satisfaction and violation magnitude
   are not v1 tail metrics or cross-model comparisons.

5. **Reported quantity.** The primary regression estimates
   E[log10 CLint_reported | assigned to the inferred quantifiable-range cohort]. It predicts reported
   HLM clearance conditional on this prespecified cohort assignment, not latent full-range clearance
   for all 1,102 compounds. Deployment is two-stage: predicted range assignment first, reported-value
   prediction only for predicted IN-RANGE assignments. Neither a class prediction nor an ordering score
   establishes an unknown true numerical clearance or a formally documented quantification limit.

6. **Metrics.** Regression: MAE on log10 primary; RMSE, Spearman and fraction within two-fold
   (|Δlog10| ≤ 0.301) secondary; R² reported only with the truncated-variance caveat and against a
   mean-predictor baseline. The two-fold band is the **experimental repeatability reference** and is
   never described as an irreducible noise floor. Classifier: macro-F1, per-class precision and recall,
   balanced accuracy, MCC, full confusion matrix, and the split between adjacent and non-adjacent
   (below↔above) errors. **Accuracy alone is not reported** — the majority class is 67.5%.

7. **Splits.** A single prespecified split/fold assignment is shared by the regression, the classifier,
   S1 and the stratified tail diagnostic. A compound's fold is identical across components.

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

10. **Biogen.** Within-dataset external replication/robustness only, not direct held-out testing of an
    AstraZeneca-trained model. Not used to fit, tune or select the primary model. The
    958-record pile-up at the minimum is **not** assumed to be censoring; every Biogen result is
    reported with and without that stratum, labelled. No numeric comparison or back-transformation
    against the AstraZeneca labels until the log base and the pile-up mechanism are documented.

11. **Sole censoring-policy sensitivity analysis.** **S1 — rerun the complete primary modelling workflow with the
    13 null-at-3 records excluded (S1 HLM regression N = 731)**, comparing model ranking, the major effect and
    feature-level conclusions where the model family admits them, and the headline evaluation metrics,
    across the regression and both tail ordering scores, the fully refitted three-class classifier
    and the paired rank correlation. S1 evaluates all prespecified classifier metrics and all three
    classes wherever the metric permits, with no ABOVE-class exemption. Primary regression N = 744 and
    classifier N = 1,102; S1 regression N = 731 and classifier N = 1,089. Recompute every prespecified
    applicable metric after refitting, including the stratified tail diagnostic with Q excluding the 13.
    No additional censoring-policy sensitivity analysis is included in frozen v1.

12. **S1 is not a selection rule.** The 744-record analysis is primary and stays primary. The choice
    between the 744-record and 731-record analyses is **not** made on the basis of which performs better,
    and no S1 outcome promotes the 731-record analysis to headline status. The primary policy remains the
    headline regardless of what S1 or the stratified tail diagnostic shows; a material change in model
    ranking under S1 is reported as a finding about the fragility of the conclusions.

13. **Status of the 13 null-at-3 records: UNRESOLVED AFTER FROZEN-METADATA AUDIT.** The frozen metadata
    has been inspected (original and standard values both 3.0; original and standard relations both null;
    `activity_comment`, `data_validity_comment`, `text_value` and `standard_text_value` all null;
    `standard_flag = 1`, which is also 1 for explicitly censored records) and contains no field that
    distinguishes them as quantified versus censored. Provenance and results are recorded in
    [CENSORING_METADATA_CHECK.md](../reports/CENSORING_METADATA_CHECK.md). **No further searching of the existing raw metadata
    for this answer is proposed.** The records are carried in the primary analysis as a prespecified
    working inference, flagged in the classifier, and excluded in S1.

14. **Open UNKNOWNs at freeze.** U1 ChEMBL documentary semantics of NULL (external, documentary); U2
    **closed** — the frozen activity fields were examined and do not discriminate; U3 formal quantification
    limits; U4 per-record status of the 13 null-at-3 records, **unresolved after the frozen-metadata audit
    with no further frozen-data check proposed**; U5 Biogen pile-up mechanism and log base; U6 chemical
    non-randomness of the censored strata. U3 evidence could confirm, refine or contradict the working
    interpretation: evidence received before modelling requires a versioned amendment; evidence received
    after results may inform interpretation but cannot retroactively change the frozen analytical
    policy. U6's descriptor-distribution comparison must be completed and frozen before the first
    predictive model is fitted or omitted from v1 entirely; it cannot be added after results are seen.
    None of these unknowns is resolved by assumption.

15. **Prespecified stratified tail diagnostic.** Separately report the lower-tail ordering score for
    the 274 explicit `<3` records and the upper-tail ordering score for the 84 explicit `>150` records,
    with cohort totals, actual evaluated tail and Q sample sizes and eligible pair counts. Report BELOW
    and ABOVE precision and recall and their true-class confusion-matrix rows with all predicted-class
    columns. This is a descriptive diagnostic, not a censoring-policy sensitivity analysis. There is
    no hypothesis test or significance threshold for tail asymmetry. Differences are descriptive and
    exploratory within this prespecified diagnostic; N = 274 and N = 84 have materially different
    precision. A difference is not proof of a mechanistic difference. The same diagnostic is recomputed
    under S1 with the refitted models and the reduced Q evaluation cohort.

16. **Excluded future extension.** Censored-normal/Tobit modelling is a plausible future extension
    but is outside the frozen v1 analysis. It will not be introduced after primary results are seen.
    No censor-aware model replaces it in v1 and no run/omit decision remains after freeze.
