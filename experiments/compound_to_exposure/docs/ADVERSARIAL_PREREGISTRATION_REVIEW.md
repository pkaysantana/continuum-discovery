# ADVERSARIAL_PREREGISTRATION_REVIEW

**Subject:** `STATISTICAL_ANALYSIS_PREREGISTRATION.md` (QSAR/DMPK HLM intrinsic clearance), at status
`READY_FOR_ADVERSARIAL_REVIEW`.
**Date:** 2026-09-18.
**Verdict:** REVISE_BEFORE_FREEZE.

**Reviewed-version note.** The preregistration under review was supplied to the reviewer as text and
is **not yet committed to this repository**. Section and quotation references below are to that
supplied text. When it is committed, the amendments in this review are applied to it directly; until
then this document stands alone as the record of what was challenged before freeze.

## Context

`STATISTICAL_ANALYSIS_PREREGISTRATION.md` is to be frozen before any modelling. It was reviewed
adversarially from a statistical/QSAR methodology standpoint. No models were run, no code was
written, and no performance number was inspected.

I did read two repository documents, because the review brief explicitly asks whether the
preregistration accurately describes the document it claims to supersede:

- `experiments/compound_to_exposure/docs/CENSORING_POLICY_MEMO.md` (744 lines)
- `experiments/compound_to_exposure/docs/DATASET_SELECTION_MEMO.md` (26 lines)

That check changed the review materially. The preregistration is not merely underspecified; its
supersession clause misstates the record, and it silently reverses three decisions the older memo
had already frozen with better justification.

**Verdict: REVISE_BEFORE_FREEZE.**

Findings are categorised BLOCKER / IMPORTANT / MINOR / NO ISSUE. Every BLOCKER and IMPORTANT
carries replacement wording or an exact methodological decision.

The scientific decisions the brief fixed are treated as fixed throughout: primary dataset
CHEMBL3301370; primary point-regression cohort N=731 (`standard_relation IS NULL AND 3 < CLint <
150`); 274 left-censored; 84 right-censored; 13 NULL-at-3 boundary-ambiguous and excluded from
the primary cohort; 3 and 150 are working boundaries with LLOQ/ULOQ unresolved; NULL is not
asserted to mean `=`; no IVIVE, no raw HLM/HH ratio, no in-vivo PK inference. Nothing below
reopens these.

---

# BLOCKERS

## B1 — The supersession clause misstates what CENSORING_POLICY_MEMO.md decided

**BLOCKER.**

The preregistration states:

> Specifically, the assumption that `NULL` standard relations mean exact equality ("=") in ChEMBL
> is **not established** and is hereby superseded by the dataset rules defined below.

The memo never made that assumption. It repeatedly and bindingly forbids it:

- §2: "nothing in this memo states or implies that a ChEMBL NULL `standard_relation` means `=` in
  general" (line 143).
- Frozen policy §12: "no output of this project may state or imply that a ChEMBL NULL
  `standard_relation` means `=` in general" (line 582).
- Frozen policy item 1: "never recoded to `=`" (line 614).
- It designates the null-relation records the **inferred quantifiable-range cohort**, explicitly
  labelled INFERRED rather than OBSERVED, under a dataset-specific working inference.
- It keeps the question open as **U1** (ChEMBL documentary semantics of NULL), unresolved at freeze.

So the preregistration supersedes a position the memo explicitly refused to hold. Worse, by
attacking a straw position it **fails to record the decision it actually overturns**.

The real supersession is the cohort definition. The memo's frozen Component 1 is:

> the **inferred quantifiable-range cohort of all 744 null-relation records** of CHEMBL3301370.
> This comprises **731 interior records (3 < value < 150) plus 13 ambiguous lower-boundary
> records** ... **N = 744.** (lines 413–416)

and it frozen-specifies that the 731-record analysis is **S1, a sensitivity analysis only**, with
an explicit anti-selection clause: "The 744-record analysis is **primary** and remains primary ...
no result of S1 promotes the 731-record analysis to primary" (lines 533–535).

The brief now fixes N=731 as primary. That is a legitimate decision, but it is a **direct
reversal** of a frozen clause, and the preregistration must say so in those terms.

### Replacement wording

Replace the entire "Superseded Decisions" bullet with:

> **Superseded Decisions.** This document supersedes `docs/CENSORING_POLICY_MEMO.md` in exactly
> one respect: the composition of the primary point-regression cohort.
>
> *   The memo froze the primary regression cohort as the **inferred quantifiable-range cohort of
>     all 744 null-relation records** (731 interior + 13 boundary-ambiguous at exactly 3), with the
>     731-record analysis defined as sensitivity analysis **S1**, and with a binding clause that S1
>     may never be promoted to primary.
> *   This document **reverses that assignment**: the primary point-regression cohort is the **731
>     interior records**, and the 13 boundary-ambiguous records are excluded from it and handled by
>     the sensitivity analyses in this document.
> *   This reversal is a **prespecified analytical decision taken before any model was fitted and
>     before any performance number was seen**. It is not, and may not be reported as, a response
>     to any result. The memo's prohibition on performance-based selection between the 744- and
>     731-record cohorts is preserved in substance: no metric from either cohort was available when
>     this decision was made.
>
> **Correction of the record.** An earlier draft of this document stated that the memo assumed a
> ChEMBL `NULL` `standard_relation` means exact equality (`=`). It did not. The memo explicitly and
> bindingly refuses that reading (memo §2, §12, frozen policy item 1) and designates the
> null-relation records an *inferred* quantifiable-range cohort under a dataset-specific working
> inference, with the documentary semantics of NULL left open as unresolved item U1. This document
> adopts the same position without change: **NULL is not asserted to mean `=` in ChEMBL generally,
> here or anywhere in this project.**
>
> **Not superseded.** All other frozen clauses of the memo remain in force, including: the
> prohibition on substituting 3 or 150 as exact targets anywhere in the science track; the
> benchmark/science separation; the shared-split constraint; and the restriction of the HLM–HH rank
> correlation to pairs in-range in both assays.

**Why this is a BLOCKER:** a preregistration whose provenance section misdescribes the prior
frozen decision is unusable as an audit trail. It is precisely the section an external reviewer
checks first, and the error is the kind that reads as retroactive justification.

---

## B2 — Primary metric and baseline are mutually incoherent, and silently reverse a frozen decision

**BLOCKER.**

The document specifies **RMSE as primary** against a **constant/median baseline**. These minimise
different functionals:

- RMSE (squared error) is minimised by the **conditional mean**; the optimal constant predictor
  under RMSE is the **mean** of the training target.
- MAE (absolute error) is minimised by the **conditional median**; the optimal constant predictor
  under MAE is the **median**.

Pairing a median baseline with an RMSE metric compares the model against a constant that is *not*
RMSE-optimal. On any skewed target — and log10 CLint truncated to (3, 150) is bounded but not
symmetric — the median constant has strictly higher RMSE than the mean constant. The comparison
therefore **handicaps the baseline and inflates the apparent improvement of every candidate
model**, by an amount fixed by the skew of the target rather than by anything the model learned.
This is a structural bias in the headline comparison, present before a single fit.

Independently: the memo's frozen policy item 6 already reads "Regression: **MAE on log10
primary**; RMSE, Spearman and fraction within two-fold" (line 661), and its S1 specification
repeats "MAE on log10 primary, with RMSE, Spearman and fraction-within-two-fold alongside" (line
528). The preregistration reverses this without acknowledging it, which compounds B1.

### The statistical trade-off (assessed without reference to outcomes)

**In favour of MAE as primary at this N:**

1. **Estimator stability.** The sampling variance of a squared-error mean depends on the fourth
   moment of the residual distribution. With a confirmatory holdout of ~150 compounds drawn by
   scaffold group, a single badly extrapolated series can move RMSE materially while barely moving
   MAE. Model *ranking* under RMSE is correspondingly unstable across grouped folds. MAE has
   bounded influence per compound.
2. **Coherence with the frozen reporting band.** ±0.301 log10 is already frozen as the two-fold
   agreement band. MAE lives on the same scale and is directly readable against it ("typical
   error, in fold-units"); RMSE is not, because it is inflated by the tail.
3. **Assay error structure.** DMPK microsomal error is approximately multiplicative, hence roughly
   symmetric on log10 but heavy-tailed in practice. L1 is the domain-standard choice, and the one
   that does not let a handful of assay outliers set the headline.
4. **Baseline coherence.** The median baseline the document already specifies is the L1-optimal
   constant. Making MAE primary fixes the incoherence without changing the baseline.

**In favour of retaining RMSE (as secondary, always reported):**

1. Large errors genuinely matter more in DMPK triage: one 10-fold miss is worse than two 2-fold
   misses, and MAE alone hides that.
2. RMSE is the more common reporting convention in the QSAR literature, so omitting it hampers
   external comparison.

The trade-off is decisively in favour of MAE at N≈731 with a scaffold holdout, and MAE is also
what the prior frozen document specified. Both metrics are reported in every table regardless.

### Replacement wording

Replace the **Metrics** section with:

> ## Metrics
>
> *   **Primary metric:** Mean Absolute Error (MAE) on the $\log_{10}$ scale.
> *   **Primary baseline:** a constant predictor equal to the **median** of the training-fold
>     $\log_{10}$ target. The median is the MAE-optimal constant, so baseline and primary metric are
>     matched.
> *   **Secondary metrics**, reported in every results table alongside the primary:
>     *   RMSE on the $\log_{10}$ scale. **Where RMSE is reported, it is compared against a constant
>         predictor equal to the training-fold *mean***, which is the RMSE-optimal constant. Each
>         metric is compared only against its own optimal constant; a median baseline is never
>         quoted under RMSE, and a mean baseline is never quoted under MAE.
>     *   Spearman rank correlation.
>     *   Coefficient of determination ($R^2$), reported with the caveat that $R^2$ is deflated by
>         the range restriction of the (3, 150) cohort and is not comparable to studies using
>         boundary-substituted targets.
> *   **Fold-error metric:** proportion of predictions within the two-fold agreement band
>     ($\pm\log_{10}(2) \approx \pm 0.301$), reported with a 95% interval computed by the same
>     scaffold-cluster bootstrap used for the primary comparison.
> *   *Constraint (unchanged):* $\pm 0.301$ is a two-fold agreement band only. It is **not** an
>     irreducible noise floor, a Bayes-error estimate, or a significance threshold.
> *   **Metric switching is prohibited.** MAE is primary whatever any metric shows.

---

## B3 — The censored-evaluation rule is degenerate by construction for Random Forest

**BLOCKER.** This is the single most serious *methodological* defect (B1 is the most serious
*documentary* one).

The document states a `<3` prediction is correct iff the model predicts ≤ 3, and a `>150`
prediction is correct iff the model predicts ≥ 150. But every candidate model is trained
exclusively on the N=731 cohort, whose targets lie strictly inside (3, 150).

A Random Forest prediction is a convex combination of training leaf means. Its output is therefore
bounded below by the minimum training target and above by the maximum. **A Random Forest trained on
(3, 150) can never produce a prediction ≤ 3 or ≥ 150.** Its score under this rule is **identically
zero for both tails, for every hyperparameter setting, before any data is seen.** Ridge, being
unbounded, can cross the boundaries — so the metric would report Ridge beating RF on the censored
tails as a mathematical property of the two estimator classes, with no information about which
model orders compounds better.

The metric measures model class, not model quality. It cannot appear in a frozen preregistration.

This is not a novel objection: the memo already identified and resolved it, and the
preregistration has reintroduced exactly the rule the memo excluded (emphasis added) —

> Range-bounded models such as Random Forests cannot extrapolate beyond their training-target
> range; absolute-bound satisfaction and violation magnitude are therefore **excluded from v1 tail
> metrics and from cross-model comparisons.** (memo lines 477–479)

### Replacement wording

Replace the **Censor-Aware Evaluation** section in full:

> ## Censor-Aware Evaluation
>
> The 274 `<3` and 84 `>150` records are never assigned exact continuous targets and never enter
> any continuous residual, in the primary analysis or any sensitivity analysis. They are evaluated
> **by the ordering of held-out predictions only**, which is invariant to the bounded output range
> of tree ensembles and therefore comparable across all model families.
>
> ### Primary censor-aware metrics — tail concordance
>
> Let $L$, $U$ and $Q$ denote the held-out left-censored, right-censored and interior (N=731
> cohort) evaluation groups, and $p$ a model prediction on the $\log_{10}$ scale.
>
> *   **Lower-tail concordance:** $C_L = P(p_L < p_Q) + \tfrac{1}{2}P(p_L = p_Q)$
> *   **Upper-tail concordance:** $C_U = P(p_U > p_Q) + \tfrac{1}{2}P(p_U = p_Q)$
>
> These are Mann–Whitney/AUC statistics: 0.5 is no discrimination, 1.0 is perfect separation.
> Computation rules, fixed now:
>
> *   Average over every eligible tail–$Q$ pair; correctly ordered pair scores 1, tie 0.5, reversal 0.
> *   **Both members of a pair must come from the same fitted model and the same held-out fold, and
>     neither may have been used to train that model.**
> *   Pool pair scores across folds weighted by eligible pair count. Never compare predictions from
>     different fitted models as if paired.
> *   Report the $L$, $U$ and $Q$ evaluation sizes and the eligible pair count for every reported
>     score. A fold with no eligible pairs contributes none; if none exist overall, report
>     **undefined** — never an imputed 0.5.
> *   Confidence intervals resample **scaffold clusters**, not pairs: tail–$Q$ pairs are strongly
>     dependent and pair counts must never be treated as independent observations.
> *   $N=274$ and $N=84$ carry materially different precision; that caveat is retained wherever
>     $C_L$ and $C_U$ are discussed, and no lower-versus-upper difference is interpreted
>     mechanistically.
>
> ### Secondary, descriptive — one-sided boundary-violation loss
>
> *   Lower: $\frac{1}{|L|}\sum_{i \in L} \max\!\big(0,\; p_i - \log_{10} 3\big)$
> *   Upper: $\frac{1}{|U|}\sum_{i \in U} \max\!\big(0,\; \log_{10} 150 - p_i\big)$
>
> **Binding constraint:** this loss is **reported within a model family only and is never used for
> model selection or cross-family comparison.** A range-bounded model incurs a guaranteed positive
> penalty because its output floor exceeds $\log_{10}3$ and its ceiling falls below
> $\log_{10}150$, while an unbounded linear model can reach zero trivially. Any cross-family
> reading of this quantity is a comparison of estimator classes, not of accuracy. It is reported to
> characterise *how far* a given model sits from the boundary, nothing more.
>
> ### Stratification by scaffold novelty
>
> $C_L$ and $C_U$ are additionally reported split by whether the censored compound's Murcko
> scaffold group appears in the training pool of its fold (**seen-scaffold**) or not
> (**unseen-scaffold**). Prespecified now, before any count is known: **any stratum containing
> fewer than 20 censored compounds is reported as a raw count with its score marked
> "under-powered — descriptive only", and is not compared against another stratum.** This threshold
> is fixed here and may not be adjusted after the strata sizes are seen.
>
> ### Prohibited
>
> *   Treating 3 or 150 as exact observations, anywhere in the science track.
> *   Any accuracy-style "percent correct" on censored records based on absolute bound satisfaction.
> *   Claiming that a concordance score establishes a numerical clearance value for a censored
>     compound, or that it verifies the unknown true clearance.

---

## B4 — The primary estimand is mis-specified for the analysis actually planned

**BLOCKER.**

The current estimand is "the expected value of $\log_{10}(\mathrm{CL_{int}})$ ... conditional on the
molecule's structural representation". Three problems:

1. **Nothing in the plan estimates or tests a conditional expectation.** A conditional-mean
   estimand implies an identifiable regression function and invites claims of unbiasedness and
   correct specification. The plan estimates *held-out predictive error under scaffold-based
   extrapolation* — a different quantity, with a different interpretation and different failure
   modes. As written, the document promises inference it never performs.
2. **It conflicts with the primary metric.** Once MAE is primary (B2), the loss-optimal functional
   is the conditional **median**, not the mean. Declaring a conditional-expectation estimand while
   optimising and reporting L1 loss is internally contradictory.
3. **It hides the selection on the outcome.** The N=731 cohort is defined by a filter on the
   target itself (`3 < CLint < 150`). This is selection on the dependent variable. Error estimated
   on this cohort does **not** transfer to an unscreened compound population, and the estimand must
   say so on its face rather than leave it to the phrase "strictly evaluated within the observable
   range". The memo states the conditioning correctly: "conditional on assignment to the inferred
   quantifiable-range cohort" (line 243).

The estimand should be framed as out-of-scaffold predictive error. It is what is computed, it is
what the decision rule acts on, and it is honest about the conditioning.

### Replacement wording

> ## Primary Estimand
>
> The **expected absolute prediction error, on the $\log_{10}$ scale, of a frozen modelling
> pipeline applied to compounds whose Bemis–Murcko scaffold group is absent from its training
> data**, where both the training data and the evaluation compounds are drawn from the primary
> point-regression cohort of CHEMBL3301370 (`standard_relation IS NULL AND 3 < CLint < 150`,
> N = 731, units µL/min/mg).
>
> Formally, for pipeline $f$ trained on a scaffold-disjoint training set $\mathcal{T}$:
> $$\theta(f) \;=\; \mathbb{E}\big[\,\lvert f(X) - \log_{10}\mathrm{CL_{int}} \rvert \;\big|\; X \in \text{cohort},\; g(X) \notin g(\mathcal{T})\,\big]$$
> where $g(\cdot)$ is the frozen scaffold-group assignment. It is estimated by the MAE of the
> frozen selected pipeline on the untouched scaffold holdout.
>
> **Conditioning that may not be dropped when this estimand is quoted:**
>
> *   It is conditional on **membership of the quantifiable-range cohort**, which is defined by a
>     filter on the outcome. It is therefore *not* an estimate of error on an unscreened compound
>     population, and must never be quoted as one. A compound's range membership is unknown before
>     assay; this preregistration does not supply a model that predicts it (see the descoping note
>     under *Relationship to the superseded three-class classifier*).
> *   It is conditional on the frozen representation set, model set, hyperparameter grid and split
>     design defined in this document. It is a property of **this pipeline under this evaluation
>     design**, not of structural predictability in general.
> *   It concerns **reported** HLM CLint. No claim is made about latent true clearance for censored
>     compounds, and none about in-vivo clearance.
>
> **Secondary estimands**, reported alongside and subject to the same conditioning: RMSE under the
> mean-constant baseline; the tail concordance statistics $C_L$ and $C_U$; and the decay of
> absolute error with nearest-neighbour structural similarity.

---

## B5 — The validation design is named, not specified

**BLOCKER.** "Scaffold-grouped cross-validation plus one untouched final scaffold holdout" names a
family of designs. It fixes no holdout proportion, no scaffold definition, no rule for acyclic
molecules, no assignment mechanism, and no fold count. Two analysts would produce different
partitions from this text, so it does not constrain anything.

### Replacement wording — the complete design

> ## Split and Validation Strategy
>
> ### Scaffold definition (frozen)
>
> *   Scaffold key = the **atomic Bemis–Murcko scaffold** as returned by
>     `rdkit.Chem.Scaffolds.MurckoScaffold.MurckoScaffoldSmiles(mol=m, includeChirality=False)`.
> *   `includeChirality=False` is deliberate: 223 audited molecules carry unspecified potential
>     stereochemistry, so a chirality-aware scaffold would split compounds by annotation
>     completeness rather than by structure.
> *   **Multicomponent structures:** the scaffold is computed on the **largest fragment by heavy-atom
>     count**; ties are broken by lexicographically smallest canonical SMILES. This rule affects
>     **scaffold-group assignment only**. The modelled structure is never altered, no salt is
>     stripped, and no tautomer or stereocentre is standardised — the Molecular Identity Policy is
>     unchanged.
> *   **Acyclic molecules** (`MurckoScaffoldSmiles` returns the empty string) are **pooled into one
>     group** with the reserved key `__ACYCLIC__`. Rationale: assigning each acyclic molecule its own
>     singleton group would let close acyclic analogues fall on both sides of the split, which is the
>     exact leakage the design exists to prevent.
>
> ### Deterministic assignment (frozen, no RNG)
>
> The partition uses **no random number generator at all**, which is a stronger guarantee than a
> fixed seed: it cannot drift with library version, platform or row order.
>
> 1.  Compute the scaffold key for **all 1,102 CHEMBL3301370 records** — not only the 731. Cohort
>     membership never influences fold assignment (see B6).
> 2.  Order groups by `int(sha256(scaffold_key.encode("utf-8")).hexdigest()[:8], 16)`, ties broken by
>     lexicographic scaffold key.
> 3.  Walk that order assigning whole groups to the **final holdout** until the holdout first
>     contains **≥ 20% of the 731-cohort compounds**; all remaining groups form the **CV pool**.
> 4.  If any single group is itself larger than the holdout budget, it is assigned to the **CV pool**
>     and skipped for the holdout; the walk continues.
> 5.  Assign CV-pool groups to **5 inner folds** by walking the same order and placing each group
>     into the fold with the fewest 731-cohort compounds so far, ties broken by lowest fold index.
>
> **Target values are read at no point in this procedure.** Target-informed split optimisation —
> balancing folds on the target, reshuffling to improve a metric, or regenerating the partition
> after any model is fitted — is **prohibited**. The partition is generated once and committed
> before the first fit.
>
> ### Holdout proportion (frozen)
>
> **20%** of the 731-cohort, ≈ 146 compounds, assigned by whole scaffold groups (the realised count
> will differ slightly from 146 because groups are indivisible; the realised count is reported). At
> 10–15% the holdout interval is too wide to support a confirmatory claim; at 30% too much training
> data is lost at a sample size where the learning curve is still steep. 20% is the standard
> compromise and is fixed here.
>
> ### Inner cross-validation (frozen)
>
> **5-fold grouped CV over the CV pool** (≈ 585 compounds), using the persisted fold column — not a
> runtime `GroupKFold` call, whose internal group ordering is an implementation detail. All
> hyperparameter selection, representation selection and pipeline selection occur **entirely within
> this inner CV**.
>
> ### Seeds
>
> The split needs none. Elsewhere `random_state = 0` is fixed for every stochastic estimator
> (`RandomForestRegressor`). Hyperparameter search is exhaustive grid search (B8), so it needs no
> seed. The bootstrap seed is fixed at 0.
>
> ### One holdout plus grouped CV, not repeated scaffold splits
>
> This is preferred for the **confirmatory** claim, for two reasons:
>
> 1.  Under repeated scaffold splits every compound is eventually a test compound, so once the
>     repeats inform any selection decision no compound remains untouched and no unbiased
>     confirmatory estimate survives. Repeated splits estimate *expected* generalisation; they
>     cannot support a single clean confirmatory number.
> 2.  Repeated Murcko resampling reshuffles scaffold groups between iterations, so near-analogues
>     from the same chemical series — frequently distinct Murcko scaffolds with high Tanimoto
>     similarity — land together in some iterations, optimistically biasing the average.
>
> The cost is acknowledged rather than hidden: a ~146-compound holdout gives a wide interval. This
> is handled by reporting the interval explicitly (B10), and by reporting the grouped-CV estimate
> beside it as the more precise but selection-contaminated figure. **The confirmatory claim rests on
> the holdout; the CV estimate is never quoted as the headline generalisation number.**
>
> Any random (non-scaffold) split may appear **only** as explicitly labelled exploratory comparison.
>
> ### Split characterisation, reported before modelling
>
> Computed from structures alone, therefore legitimate to compute pre-freeze: number of scaffold
> groups, **fraction of groups that are singletons**, largest group size, the size of `__ACYCLIC__`,
> and the distribution of nearest-neighbour Tanimoto similarity from each holdout compound to the CV
> pool. See I4 — if scaffold groups are mostly singletons, "scaffold split" is a weaker structural
> separation than the name implies, and the nearest-neighbour similarity distribution is the honest
> measure of split severity.

---

## B6 — No master structural partition is persisted

**BLOCKER.** The document requires "deterministic, persisted split assignments" in Reproducibility
but never states that **one** partition governs every analysis. Without that, Sensitivity Analysis
A (13 records added as exact 3s) and Analysis B (13 treated as left-censored) would each regenerate
a partition, changing the fold membership of unrelated compounds. The A-vs-B comparison would then
confound the 13 records with a reshuffle of the other 731 — and since the document forbids choosing
between A and B on performance, an un-comparable A/B contrast makes that clause unenforceable.
Likewise the censored evaluation is only genuinely held out if the 274 and 84 sit in the same fold
structure as the interior compounds. The memo's shared-split constraint (lines 490–493) covers
exactly this and was dropped.

### Replacement wording

Add as a new section immediately after Split and Validation Strategy:

> ## Master Structural Partition
>
> Exactly **one** partition governs every analysis on CHEMBL3301370. It is computed once by the
> procedure in *Split and Validation Strategy* over **all 1,102 records**, using structure only, and
> is persisted to `splits/master_partition.csv` with a recorded SHA-256 before the first model fit.
>
> Columns: `chembl_id`, `canonical_smiles`, `scaffold_key`, `scaffold_group_id`, `partition`
> (`holdout` | `cv`), `cv_fold` (0–4, null for holdout), `cohort` (`interior_731` | `below_274` |
> `above_84` | `ambiguous_13`).
>
> **Binding rules:**
>
> *   Fold membership is a function of **structure only**. `cohort` determines which records a given
>     analysis *uses*; it never determines which fold a record is *in*.
> *   The primary regression, Sensitivity Analysis A, Sensitivity Analysis B, the censor-aware
>     evaluation, the applicability-domain analysis and the HLM–HH paired analysis all read this
>     file. None regenerates a partition.
> *   Because the 13 boundary-ambiguous records already hold fold assignments, Analysis A and
>     Analysis B differ **only** in the treatment of those 13 records. No other compound changes fold
>     between them, making the contrast attributable to the 13 alone.
> *   The censored 274 and 84 receive fold assignments from the same partition, so their held-out
>     predictions in the censor-aware evaluation come from models that never saw them.
> *   The partition file is **immutable after first fit**. Any change voids the confirmatory result
>     and requires a versioned amendment recorded before refitting.
> *   The Biogen cohort uses a **separate** partition file, `splits/biogen_partition.csv`, built by
>     the identical algorithm. The two are never merged.

---

## B7 — The representations are named, not frozen

**BLOCKER.** "Preregistered RDKit physicochemical descriptors" is self-referential: the
preregistration does not contain the list. Descriptor choice, fingerprint geometry, scaling and
non-finite handling are all degrees of freedom that can be exercised after seeing results.

### Replacement wording

> ## Representations
>
> Exactly **two** representations. No third is added in v1.
>
> ### R1 — Physicochemical descriptors (frozen list, 12)
>
> As exposed by `rdkit.Chem.Descriptors` at the pinned RDKit version, computed on the unmodified
> deposited structure:
>
> `MolWt`, `MolLogP`, `MolMR`, `TPSA`, `NumHDonors`, `NumHAcceptors`, `NumRotatableBonds`,
> `RingCount`, `NumAromaticRings`, `NumAliphaticRings`, `FractionCSP3`, `HeavyAtomCount`.
>
> Chosen as the standard interpretable drivers of microsomal metabolic stability — lipophilicity,
> size, polarity, aromaticity and sp³ character. **No descriptor may be added, removed or
> substituted after any performance number is seen.**
>
> *   **Scaling:** `StandardScaler` **for Ridge only**, fitted inside each training fold. Random
>     Forest receives raw descriptors: tree splits are invariant to monotone rescaling, so a scaler
>     would be a no-op carrying a fitted object. This asymmetry is prespecified, not tuned.
> *   **Non-finite handling:** descriptors are computed for all 1,102 records and the count of
>     non-finite cells is reported. Any non-finite value is replaced by the **median of that
>     descriptor within the training fold**, via a `SimpleImputer(strategy="median")` fitted inside
>     the fold. No compound is dropped for a non-finite descriptor.
> *   **Zero-variance:** a descriptor constant within a training fold is dropped **within that fold**
>     for Ridge (it carries no information and destabilises scaling). Deterministic; reported.
>
> ### R2 — Morgan fingerprints (frozen geometry)
>
> `GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048, useChirality=False)` — ECFP4-equivalent.
>
> *   **Binary bit vectors, not counts.** At N≈731 count vectors add variance without interpretive
>     gain, and binary ECFP4 is the domain-standard baseline this project exists to establish.
> *   `useChirality=False`, for the same reason as the scaffold rule: 223 molecules carry unspecified
>     potential stereochemistry, and chirality-aware bits would encode annotation completeness.
> *   **No scaling and no imputation.** Bits are already on a common scale and are always defined.
>
> ### Concatenation
>
> **Descriptors and fingerprints are never concatenated in v1.** A concatenated block would be a
> third, unpreregistered representation mixing standardised continuous features with sparse binary
> ones under a single Ridge penalty, and would raise the pipeline count without a stated hypothesis.
> The estimand's phrase "and/or" is corrected to "either ... or" accordingly (see I7).

---

## B8 — The hyperparameter procedure is not preregistered

**BLOCKER.** "Grid or random search over predefined grids" fixes neither the procedure nor the
grids nor the selection criterion. Random search additionally introduces an unspecified seed and
budget.

### Replacement wording

> ## Hyperparameter Selection
>
> **Exhaustive grid search only.** Random search is not used, so no search seed exists.
>
> *   **Selection criterion:** lowest **mean $\log_{10}$-MAE across the five inner grouped CV
>     folds**, matching the primary metric.
> *   **Search spaces, frozen:**
>     *   Ridge: `alpha ∈ {0.01, 0.1, 1, 10, 100, 1000}` (6 settings; `fit_intercept=True`).
>     *   Random Forest: `max_features ∈ {"sqrt", 0.3, 1.0}` × `min_samples_leaf ∈ {1, 3, 5}`
>         (9 settings), with `n_estimators = 500`, `max_depth = None`, `random_state = 0` fixed.
> *   **All preprocessing is fitted inside training folds.** Every pipeline is a single
>     `sklearn.pipeline.Pipeline`, so the imputer and scaler are fitted on the training portion of
>     each fold only. No statistic — mean, median, variance, or fingerprint frequency — is computed
>     over the CV pool as a whole or over the holdout at any point.
> *   Grids may not be extended, recentred or refined after any performance number is seen. If a
>     selected value sits at a grid edge, that fact is **reported as a limitation**, not fixed by
>     widening the grid.

---

## B9 — No deterministic selection or tie-breaking rule across pipelines

**BLOCKER.** Four model×representation pipelines plus a baseline are compared, and the document
gives no rule for picking one, no tie-break, and no constraint on how many pipelines touch the
holdout. Left open, the confirmatory holdout could be evaluated for all four and the best reported
— which destroys the single-confirmatory-test property the Split section claims.

### Replacement wording

> ## Model Pipelines and Final Selection Rule
>
> ### Frozen pipelines (five; no model is added without a stated pre-performance justification)
>
> | ID | Representation | Estimator |
> |---|---|---|
> | P0a | none | constant = training-fold **median** (MAE baseline) |
> | P0b | none | constant = training-fold **mean** (RMSE baseline) |
> | P1 | R1 descriptors | `Ridge` (imputer → scaler → ridge) |
> | P2 | R2 Morgan | `Ridge` (no imputer, no scaler) |
> | P3 | R1 descriptors | `RandomForestRegressor` (imputer → RF) |
> | P4 | R2 Morgan | `RandomForestRegressor` |
>
> ### Selection rule (deterministic, fixed before any number is seen)
>
> Selection uses **inner grouped-CV mean $\log_{10}$-MAE only**. Applied in order, stopping at the
> first criterion that discriminates:
>
> 1.  Lowest mean inner-CV $\log_{10}$-MAE.
> 2.  If two candidates are within **0.001 $\log_{10}$ units**, prefer the simpler model family in
>     the fixed order **constant < Ridge < Random Forest**.
> 3.  Still tied: prefer **R1 descriptors** over R2 Morgan (lower dimension, directly interpretable).
> 4.  Still tied: prefer the **more strongly regularised** setting — larger `alpha`; larger
>     `min_samples_leaf`; then smaller `max_features`.
> 5.  Still tied: lowest pipeline ID in the fixed lexicographic order P1 < P2 < P3 < P4.
>
> ### Holdout access rule (binding)
>
> **Exactly one selected pipeline, plus P0a and P0b, are evaluated on the final holdout.** The
> non-selected pipelines are **never** evaluated on it — not as a check, not as a footnote, not as
> exploratory context. Their inner-CV results are reported in full; their holdout results do not
> exist. The holdout is touched **once**.
>
> The holdout result is reported **whatever it shows**. Re-selection, metric substitution, grid
> extension, representation change and re-partitioning are all prohibited after the holdout is read.

---

## B10 — "Statistically significant improvement" is undefined

**BLOCKER.** No test, no estimator, no resampling unit, no interval, and no separation of
statistical from scientific conclusions. As written the success criterion cannot be evaluated
without post-hoc choices.

### Replacement wording

> ## Decision Criteria
>
> ### Primary comparison
>
> $$\Delta \;=\; \mathrm{MAE}_{\log_{10}}(\text{P0a median baseline}) \;-\; \mathrm{MAE}_{\log_{10}}(\text{selected pipeline})$$
>
> computed on the untouched scaffold holdout. $\Delta > 0$ favours the model.
>
> ### Interval (frozen)
>
> **Paired scaffold-cluster bootstrap.** Resample **scaffold groups** in the holdout with
> replacement — never individual compounds, which are dependent within a group — to $B = 10{,}000$
> replicates, `seed = 0`. Both predictors are evaluated on the identical resample (paired). Report
> the **95% percentile interval** for $\Delta$, alongside both absolute MAEs and the realised
> holdout compound and group counts.
>
> ### Pre-specified conclusions
>
> *   **Improvement demonstrated** iff the lower bound of the 95% interval for $\Delta$ exceeds 0.
> *   **Improvement not demonstrated** otherwise. $\Delta$ and its interval are reported either way,
>     with the same prominence.
> *   **Practical utility marker (separate, and separately labelled):** the selected pipeline's
>     holdout MAE is additionally compared against 0.301 $\log_{10}$. This is a **prespecified
>     project-level reporting convention, deliberately conventional**, and is **not** a noise floor,
>     a Bayes-error estimate or a significance threshold — consistent with the frozen constraint on
>     ±0.301. It never affects model selection.
> *   **Statistical significance is not scientific usefulness.** A $\Delta$ whose interval excludes
>     zero but whose magnitude is small relative to two-fold assay agreement is reported as
>     *detectable but not decision-relevant*. The two judgements are reported as separate sentences
>     and never merged.
> *   The same bootstrap procedure produces intervals for RMSE (against P0b), $C_L$, $C_U$ and the
>     two-fold band proportion. No multiplicity adjustment is applied because **only $\Delta$ is
>     confirmatory**; all other intervals are descriptive and are labelled as such.

---

## B11 — The falsification language is invalid

**BLOCKER.** The document states that if Ridge or RF fail to beat the baseline, "the hypothesis
that these structural representations predict intrinsic clearance within the observable continuous
range is falsified for this dataset." A null result from two specific estimators, on 12 descriptors
or one fingerprint geometry, at N≈731, under one scaffold split, with a fixed grid, against a
target carrying assay noise and cohort truncation, cannot falsify structural predictability. The
outcome is confounded with sample size, representation choice, grid coverage, split severity, and
label noise simultaneously. Publishing that sentence would be the document's most attackable claim.

### Replacement wording

> ## Failure Criteria
>
> If $\Delta$'s 95% interval includes or lies below zero, the finding is stated exactly as:
>
> > **Under this preregistration** — the 12 frozen RDKit descriptors and binary ECFP4
> > (r=2, 2048 bits, no chirality); Ridge and Random Forest with the frozen grids; the N=731
> > CHEMBL3301370 quantifiable-range cohort; and a single 20% Bemis–Murcko scaffold holdout with
> > 5-fold grouped inner CV — **the selected pipeline did not demonstrate a detectable reduction in
> > $\log_{10}$-MAE relative to a median-constant baseline on structurally novel compounds.**
>
> Permitted accompanying statements: that the result is confounded with sample size, representation
> choice, grid coverage, scaffold-split severity and assay noise, which this design cannot separate;
> and that the scaffold holdout deliberately measures extrapolation to novel chemistry, which is a
> harder task than interpolation within a series.
>
> **Prohibited:** that structural representations do not predict intrinsic clearance; that QSAR
> fails on this endpoint; that the endpoint is unpredictable; any use of the word *falsified* for a
> hypothesis broader than the frozen pipeline, cohort and split named above; and any post-hoc
> addition of models or representations to rescue a null result.

---

## B12 — The HLM–HH analysis has no deterministic qualifier policy

**BLOCKER.** The section says "ranking and correlation" over 187 overlapping compounds without
saying which are quantitatively usable. A Spearman computed over all 187 would silently rank
censored records at their substituted boundary values, creating large tied blocks of fabricated
numbers at both extremes — the exact substitution the science track prohibits. The memo already
supplied the rule (§7, lines 346–363) and the preregistration dropped it.

### Replacement wording

> ## HLM–HH Secondary Analysis
>
> Units differ (HLM µL/min/mg; HH µL/min/10⁶ cells). No raw ratio, no subtraction, no physiological
> scaling, no IVIVE. Microsomal CLint is never described as clinical clearance. Rank agreement only.
>
> ### Deterministic qualifier policy (frozen)
>
> *   **Eligible paired set:** those of the 187 structural overlaps whose **HLM record belongs to the
>     N=731 primary interior cohort** *and* whose **HH record belongs to the 289 null-relation HH
>     records**. CHEMBL3301372 has zero null-relation records at 3 and zero at 150, so all 289 are
>     interior and the HH side contributes no boundary ambiguity.
> *   **The eligible count is reported explicitly and is not 187.** No figure, table or sentence may
>     imply that the correlation is computed over 187 compounds.
> *   **Censored members are never ranked.** Pairs censored in either assay are reported **only** as
>     a 3×3 contingency table of HLM range category (BELOW / IN-RANGE / ABOVE) × HH range category,
>     with counts. This is informative in its own right — whether a compound below range in HLM is
>     also below range in HH — and requires no shared unit and no ratio.
> *   **Boundary-ambiguous 13:** report how many fall inside the 187 overlaps. The **primary**
>     Spearman **excludes** them, consistent with the frozen N=731 primary cohort. A sensitivity
>     Spearman including them as interior is reported beside it, mirroring Sensitivity Analysis A.
>     **The choice between the two is not made on which correlation is stronger; the exclusive
>     estimate is primary by prespecification and both are reported.**
> *   Report Spearman $\rho$ with a 95% scaffold-cluster bootstrap interval and the eligible N.
> *   **Mandatory caveat:** restricting to in-range-in-both truncates variance in both variables, so
>     $\rho$ is attenuated and is a conservative, downward-biased estimate of the underlying
>     association. It is never quoted as an assay-agreement coefficient.

---

# IMPORTANT

## I1 — Biogen: the floor decision must be made now, and unit non-comparability stated

**IMPORTANT.** The document notes the 958 values at 0.675686709 are unresolved and "will not be
unilaterally declared as censored" — correct, but it then specifies no analysis, leaving the choice
to be made after the primary results are seen. That is the gap that most often becomes post-hoc
selection.

**Decision: preregister the explicitly exploratory as-shipped analysis plus a floor-excluded
sensitivity.** Deferring entirely discards a cheap robustness signal; declaring it confirmatory is
unsupportable with 31% of populated values at an unexplained floor. Running both, with neither
confirmatory, is the only option that cannot be gamed.

> ## Biogen Replication
>
> Within-dataset replication of the **modelling procedure**, never a pooled external test set.
> Both analyses below are **exploratory**; neither is confirmatory, and neither can change any
> conclusion of the primary track.
>
> *   **B1 — as-shipped:** all 3,087 populated `LOG HLM_CLint (mL/min/kg)` values, used exactly as
>     distributed.
> *   **B2 — floor-excluded sensitivity:** the 2,129 values strictly greater than 0.675686709.
> *   Both are **always reported**, side by side. The choice between them is not made on which
>     performs better, and the floor is described as **unresolved** in both — never as censored,
>     never as exact.
> *   **Labels are source-provided logs.** No re-logging, no unit conversion, no transformation to
>     imitate the AstraZeneca assay.
> *   **Units differ from HLM** (mL/min/kg vs µL/min/mg) and the label is already logged by the
>     source. **Biogen MAE/RMSE values are therefore not numerically comparable to HLM MAE/RMSE and
>     may never be placed in the same table or compared as magnitudes.** What replicates is the
>     *procedure and the qualitative pattern* — whether scaffold-split error exceeds random-split
>     error, and whether error grows with structural distance — not the error size.
> *   Biogen uses `splits/biogen_partition.csv`, built by the identical scaffold algorithm. The four
>     multicomponent structures are handled by the largest-fragment rule for **grouping only**;
>     harmonisation of multicomponent structures and unspecified stereochemistry remains deferred.

## I2 — TDC: official split and metric unspecified

**IMPORTANT.** The section describes the shipped data but not how it is evaluated, so "reproduce"
is unverifiable. The memo required "Official split and official metric preserved" (line 296).

> ## TDC Benchmark Reproduction
>
> Reproduced **exactly as shipped**, via the official harness: `Clearance_Microsome_AZ` retrieved
> through the TDC ADMET benchmark group API, using the **harness's own split** (its `get_split` /
> `get_train_valid_split` seeds as documented for the group) and **the metric the harness itself
> returns from `evaluate()`** — expected to be Spearman for this dataset, but the binding rule is
> that the metric is **taken from the harness and not chosen by us**. Reported with the harness's
> mean and standard deviation across its prescribed seeds.
>
> **Separation (binding):**
>
> *   TDC uses **its own split**, never the master structural partition.
> *   TDC results never appear in the same table or figure as science-track results.
> *   No TDC-derived choice — hyperparameter, representation or threshold — informs the science
>     track, and no science-track result is quoted as a benchmark number or vice versa.
> *   Boundary substitution (274 `<3` → 3, 84 `>150` → 150, giving 287 values at exactly 3) is part
>     of the benchmark's historical representation and stays **only** here. Results are reported
>     **solely as benchmark comparability**, never as accuracy on experimental measurements.
> *   The five structural-representation mismatches are reported, so the two sources are not
>     described as interchangeable.

## I3 — The three-class range classifier was dropped without comment

**IMPORTANT.** The memo froze a three-class BELOW / IN-RANGE / ABOVE classifier over all 1,102
records (Component 2) with a full metric set. The preregistration omits it entirely and never
records the omission. Two consequences:

1. It is a second undocumented supersession, compounding B1.
2. It leaves a scientific hole. The primary estimand is conditional on in-range membership (B4),
   and the classifier was the only component that predicted that membership. Without it, the
   regression cannot be applied to a new compound, because nothing says whether the compound falls
   in the quantifiable range.

I am not reopening the scope — the brief fixes what is in the primary track. But the document must
make an explicit, recorded choice rather than lose the component silently.

> **Relationship to the superseded three-class classifier.** `CENSORING_POLICY_MEMO.md` froze a
> three-class assay-range classifier (BELOW / IN-RANGE / ABOVE, N=1,102) as Component 2. This
> preregistration **descopes that component from v1** and records the descoping here explicitly. The
> consequence is stated as a limitation wherever the regression is reported: **the primary model is
> conditional on a compound already being known to fall in the quantifiable range, and this version
> supplies no model that predicts range membership.** The censored records are retained and used, but
> only through the ordering-based censor-aware evaluation. Reinstating a range classifier is deferred
> to a separately preregistered analysis.

## I4 — Scaffold-group degeneracy is not characterised

**IMPORTANT.** In a 731-compound set assembled from diverse medicinal-chemistry series, a large
fraction of Bemis–Murcko scaffolds are typically unique to a single compound. If most groups are
singletons, a "scaffold split" is only marginally more separated than a random split, and the
document's claim of a "structurally distinct" holdout is overstated. This is computable from
structure alone, so it must be settled before freeze rather than discovered afterwards.

> **Split-severity reporting (added to Split and Validation Strategy).** Before the first model fit,
> report the number of scaffold groups, the singleton fraction, the largest group size, the
> `__ACYCLIC__` group size, and the distribution of maximum Tanimoto similarity (frozen ECFP4) from
> each holdout compound to the CV pool. **If the singleton fraction is high, the scaffold split
> provides weaker structural separation than the term implies, and that is reported as a stated
> limitation on the confirmatory estimate.** The nearest-neighbour similarity distribution — not the
> word "scaffold" — is the quantitative characterisation of split severity, and it is reported
> whatever it shows. No second partition is created in response to it.

## I5 — The applicability-domain plan invites post-hoc thresholds

**IMPORTANT.** "Structural distance (e.g. Tanimoto similarity)" leaves the fingerprint, the
aggregation and the bins open, and an AD threshold chosen after seeing residuals is a post-hoc
model-scope claim.

> ## Applicability-Domain Analysis
>
> *   **Similarity definition, fixed and model-independent:** Tanimoto on the frozen ECFP4
>     fingerprint (radius 2, 2048 bits, `useChirality=False`) — **used even when the selected
>     pipeline is the descriptor pipeline**, so the AD axis never changes with the selected model.
> *   **Statistic:** for each evaluation compound, the **maximum Tanimoto to any compound in the
>     training pool of its own fold**.
> *   **Bins, fixed now, before any residual is seen:** [0, 0.2), [0.2, 0.3), [0.3, 0.4), [0.4, 0.6),
>     [0.6, 1.0]. Report per-bin N, MAE and a bootstrap interval. **A bin with fewer than 20
>     compounds is reported as a count and marked under-powered, and is not compared.**
> *   Also report the continuous relationship: absolute residual vs nearest-neighbour similarity as a
>     scatter, summarised by a single prespecified Spearman correlation between the two.
> *   **No applicability-domain cutoff is declared in v1**, and no bin edge is moved after residuals
>     are seen. The analysis describes how reliability decays; it does not certify a domain.

## I6 — Residual normality testing should be removed

**IMPORTANT.** No procedure in the plan assumes Gaussian residuals: the primary metric is MAE, the
interval is a distribution-free bootstrap, and there is no OLS t- or F-test anywhere. A normality
test on ~146 holdout compounds therefore either rejects on an irrelevant deviation or lacks power,
and changes no decision either way. It is a diagnostic in search of an inference.

> ## Residual Diagnostics
>
> Aimed at predictive failure and heteroscedasticity, not at distributional inference. No normality
> test is performed; **no test statistic or p-value is computed for residual distribution shape.** A
> QQ plot may be shown as a purely descriptive display and is not interpreted inferentially.
>
> 1.  Predicted vs observed, with the $y=x$ line.
> 2.  Residual vs predicted.
> 3.  **Absolute** residual vs predicted, with prespecified tercile summaries — the heteroscedasticity
>     check.
> 4.  **Boundary-compression check (prespecified, expected failure mode):** mean signed residual in
>     the lowest and highest prediction terciles. A model trained on a target truncated to (3, 150)
>     is expected to compress toward the centre, producing systematically positive residuals at the
>     low end and negative at the high end. This is reported explicitly whether or not it appears.
> 5.  Residual vs nearest-neighbour Tanimoto (shared with the AD analysis).
> 6.  The **10 largest absolute residuals** listed with structures and scaffold groups, supporting
>     the failure analysis that is this project's stated purpose.

## I7 — "and/or" in the estimand conflicts with the no-concatenation freeze

**IMPORTANT.** The estimand says "RDKit physicochemical descriptors and/or Morgan fingerprints",
which admits a concatenated representation that B7 prohibits. Change to "either the frozen RDKit
descriptor block **or** the frozen Morgan fingerprint, never their concatenation".

## I8 — No pre-commitment to report the holdout result regardless of outcome

**IMPORTANT.** The document forbids "manual post-result changes to frozen analysis decisions" but
never commits to *publishing* the confirmatory result whatever it is. Covered by the closing
sentences of B9 and B10; state it once more under Reproducibility: **the holdout evaluation is
executed once and reported in full regardless of outcome; a null result is reported with the same
prominence as a positive one.**

## I9 — The source-of-truth hierarchy names a tier it does not identify

**IMPORTANT.** Tier 2 is "verified audit reports and independently reproduced numerical findings",
but no audit file is named, so the tier cannot be checked. The memo cites specific reports with
hash provenance (`DATA_AUDIT.md`, `REVIEW_SUMMARY.md`, `BIOGEN_AUDIT.md`,
`CENSORING_METADATA_CHECK.md`). Enumerate those paths with their recorded SHA-256 values at freeze
time, so tier 2 is a closed set rather than an open category.

---

# MINOR

- **M1.** State that `3 < CLint < 150` is applied to the reported `standard_value` in µL/min/mg
  **before** the $\log_{10}$ transform, and that the comparison is strict at both ends — this is what
  places the 13 NULL-at-3 records outside the cohort.
- **M2.** Record that the 187 HLM–HH overlaps agree under both identity definitions (187 shared
  molecule IDs *and* 187 shared strict canonical structures), citing the audit, rather than leaving
  "structural overlaps" undefined.
- **M3.** "Biogen ... N = 3,521 total structures" should read **rows**, not structures; 3,087 are
  populated and 434 missing.
- **M4.** The two-fold band is a proportion and should carry an interval from the same bootstrap;
  otherwise it will be read as exact.
- **M5.** Reproducibility should pin the **RDKit version explicitly** alongside scikit-learn and
  NumPy. Descriptor values and Murcko scaffold output are version-sensitive, so a floating RDKit
  version silently changes both the features and the master partition.

---

# NO ISSUE

- **N1.** The source-of-truth hierarchy correctly places `DATASET_SELECTION_MEMO.md` above
  `CENSORING_POLICY_MEMO.md`, matching the memo's own header ("DATASET_SELECTION_MEMO.md remains the
  frozen scientific source of truth ... It does not reopen dataset selection").
- **N2.** Cohort arithmetic is internally consistent: 731 + 274 + 84 + 13 = 1,102.
- **N3.** Biogen counts are consistent: 3,087 populated + 434 missing = 3,521.
- **N4.** The molecular identity policy — no silent standardisation of salts, tautomers,
  stereochemistry or multicomponent structures — is correct and worth keeping verbatim.
- **N5.** The no-IVIVE / no-raw-ratio / no-clinical-clearance constraints are correctly stated and
  correctly scoped.
- **N6.** The benchmark/science separation principle is correct in substance (its mechanics need I2).
- **N7.** The A/B sensitivity structure for the 13 records, with the explicit rule that the choice is
  not made on downstream performance, is correct and should be preserved verbatim — it needs only the
  shared partition of B6 to be enforceable.
- **N8.** Confining deep neural networks out of v1 at N≈731, and the "models are not added merely to
  increase the comparison count" clause, are both correct and should be kept.

---

# Summary

| Category | Count |
|---|---:|
| BLOCKER | 12 |
| IMPORTANT | 9 |
| MINOR | 5 |
| NO ISSUE | 8 |

The three defects that most threaten the document's credibility, in order:

1. **B1** — the supersession clause attacks a position the prior memo explicitly refused to hold,
   and omits the decision actually being reversed (primary cohort N=744 → N=731). This is a
   provenance error in the section an external reviewer reads first.
2. **B3** — the censored-evaluation rule returns a score of exactly zero for Random Forest as a
   mathematical property of the estimator class, and the memo had already identified and excluded
   precisely this rule.
3. **B2** — RMSE against a median baseline compares the model to a constant that is not
   RMSE-optimal, biasing the headline comparison in the model's favour before any fitting, and
   silently reversing the memo's frozen MAE-primary decision.

**REVISE_BEFORE_FREEZE**

---

# Applying this review

The preregistration is not yet in this repository, so this review is committed on its own and the
amendments below are applied when the preregistration lands.

1. **This document** — the permanent record of what was challenged before freeze. It is not
   superseded by the amended preregistration; it remains the evidence that the amendments were made
   before any model was fitted.
2. **`STATISTICAL_ANALYSIS_PREREGISTRATION.md`** — amended section by section. Sections replaced in
   full: Primary Estimand (B4), Source-of-Truth / Superseded Documents (B1), Representations (B7),
   Models and Baselines (B9), Split and Validation Strategy (B5, I4), Hyperparameter Selection (B8),
   Metrics (B2), Censor-Aware Evaluation (B3), Applicability-Domain Analysis (I5), Residual Analysis
   (I6), HLM–HH Secondary Analysis (B12), TDC Benchmark Reproduction (I2), Biogen Replication (I1),
   Decision/Failure Criteria (B10, B11). New sections added: Master Structural Partition (B6),
   Relationship to the superseded three-class classifier (I3).
3. Bump `PREREGISTRATION_STATUS` from `READY_FOR_ADVERSARIAL_REVIEW` to `AMENDED_PENDING_FREEZE`,
   with a dated amendment note in the same style the censoring memo uses for its 2026-09-17
   frozen-metadata amendment.

No code is written and no model is fitted as part of applying this review.

## Verification

This review is a document-level deliverable, so verification is documentary rather than executable:

- Re-read the amended preregistration against the five fixed decisions in the brief, confirming none
  was reopened (cohort N=731, censoring counts, boundary status, NULL semantics, no-IVIVE).
- Diff the amended Source-of-Truth section against `CENSORING_POLICY_MEMO.md` §2, §12 and frozen
  policy items 1, 6 and 12 to confirm every supersession claim is literally supported.
- Confirm every frozen clause in the memo that is **not** superseded still holds in the amended text
  (no boundary substitution in the science track; benchmark/science separation; shared-split
  constraint; in-range-both restriction on the HLM–HH correlation).
- Confirm the amended document contains no remaining metric, representation, grid, split parameter
  or decision threshold that is named without being fully specified.
