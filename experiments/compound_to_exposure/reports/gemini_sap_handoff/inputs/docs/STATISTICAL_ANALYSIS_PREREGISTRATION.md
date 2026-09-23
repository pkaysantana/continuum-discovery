# v2 Reanalysis Protocol: QSAR/DMPK HLM Intrinsic Clearance

## Scientific Question
Can the structural representation and baseline physicochemical properties of a compound reliably predict its intrinsic clearance in human liver microsomes (HLM) within a continuous, finite observable range, and to what extent does structural similarity govern prediction error?

## Primary Estimand
The **expected absolute prediction error, on the $\log_{10}$ scale, of a frozen modelling pipeline applied to compounds whose Bemis–Murcko scaffold group is absent from its training data**, where both the training data and the evaluation compounds are drawn from the primary point-regression cohort of CHEMBL3301370 (`standard_relation IS NULL AND 3 < CLint < 150`, N = 731, units µL/min/mg).

Formally, for pipeline $f$ trained on a scaffold-disjoint training set $\mathcal{T}$:
$$\theta(f) \;=\; \mathbb{E}\big[\,\lvert f(X) - \log_{10}\mathrm{CL_{int}} \rvert \;\big|\; X \in \text{cohort},\; g(X) \notin g(\mathcal{T})\,\big]$$
where $g(\cdot)$ is the frozen scaffold-group assignment. It is estimated by the MAE of the frozen selected pipeline on the scaffold holdout reserved from v2 tuning.

**Conditioning that may not be dropped when this estimand is quoted:**
*   It is conditional on **membership of the quantifiable-range cohort**, which is defined by a filter on the outcome. It is therefore *not* an estimate of error on an unscreened compound population, and must never be quoted as one. A compound's range membership is unknown before assay; this preregistration does not supply a model that predicts it (see the descoping note under *Relationship to the superseded three-class classifier*).
*   It is conditional on the frozen representation set, model set, hyperparameter grid and split design defined in this document. It is a property of **this pipeline under this evaluation design**, not of structural predictability in general.
*   It concerns **reported** HLM CLint. No claim is made about latent true clearance for censored compounds, and none about in-vivo clearance.

**Secondary estimands**, reported alongside and subject to the same conditioning: RMSE under the mean-constant baseline; the tail concordance statistics $C_L$ and $C_U$; and the decay of absolute error with nearest-neighbour structural similarity.

## Source-of-Truth / Superseded Documents
*   **Source of Truth Hierarchy:**
    1.  The explicit frozen decisions in the authoritative statistical planning prompt.
    2.  Verified audit reports and independently reproduced numerical findings.
    3.  Commit `fefaf21` (the historical v1 preregistration).
    4.  `docs/ADVERSARIAL_PREREGISTRATION_REVIEW.md`.
    5.  `docs/DATASET_SELECTION_MEMO.md`.
    6.  `docs/CENSORING_POLICY_MEMO.md`.

*   **Disclosure regarding v1 analysis:** The underlying dataset was previously analyzed in the v1 track. Model performance for v1 was already generated and observed before this v2 protocol was drafted. This protocol governs a prospective v2 reanalysis wherein the holdout is reserved from v2 tuning, but it is not strictly "untouched" as it was analyzed in v1.

*   **Superseded Decisions.** This document supersedes `docs/CENSORING_POLICY_MEMO.md` in exactly one respect: the composition of the primary point-regression cohort.
    *   The memo froze the primary regression cohort as the **inferred quantifiable-range cohort of all 744 null-relation records** (731 interior + 13 boundary-ambiguous at exactly 3), with the 731-record analysis defined as sensitivity analysis **S1**, and with a binding clause that S1 may never be promoted to primary.
    *   This document **reverses that assignment**: the primary point-regression cohort is the **731 interior records**, and the 13 boundary-ambiguous records are excluded from it and handled by the sensitivity analyses in this document.
    *   This reversal is a **prespecified analytical decision taken before any model was fitted and before any performance number was seen**. It is not, and may not be reported as, a response to any result. The memo's prohibition on performance-based selection between the 744- and 731-record cohorts is preserved in substance: no metric from either cohort was available when this decision was made.

**Correction of the record.** An earlier draft of this document stated that the memo assumed a ChEMBL `NULL` `standard_relation` means exact equality (`=`). It did not. The memo explicitly and bindingly refuses that reading (memo §2, §12, frozen policy item 1) and designates the null-relation records an *inferred* quantifiable-range cohort under a dataset-specific working inference, with the documentary semantics of NULL left open as unresolved item U1. This document adopts the same position without change: **NULL is not asserted to mean `=` in ChEMBL generally, here or anywhere in this project.**

**Not superseded.** All other frozen clauses of the memo remain in force, including: the prohibition on substituting 3 or 150 as exact targets anywhere in the science track; the benchmark/science separation; the shared-split constraint; and the restriction of the HLM–HH rank correlation to pairs in-range in both assays.

## Dataset Populations
*   **Primary Science Dataset:** CHEMBL3301370 (AstraZeneca HLM apparent intrinsic clearance). Units: µL/min/mg. Total N = 1,102.
*   **Primary Point-Regression Cohort:** N = 731.
    *   *Inclusion Rule:* `standard_relation IS NULL AND 3 < CLint < 150`.
*   **Censored / Boundary Populations:**
    *   N = 274 `<3`: Left-censored at working boundary 3.
    *   N = 84 `>150`: Right-censored at working boundary 150.
    *   N = 13 `NULL` exactly at 3: Boundary-ambiguous, excluded from primary point-regression, retained for sensitivity analyses.
*   **Secondary Human Assay:** CHEMBL3301372 (Human hepatocyte apparent intrinsic clearance). N = 408.
*   **External Replication:** Biogen public HLM dataset. N = 3,521 total rows (3,087 populated values and 434 missing).
*   **Benchmark Track:** TDC Clearance_Microsome_AZ. N = 1,102.

## Target Definition
The target is the base-10 logarithm of apparent intrinsic clearance, $\log_{10}(\text{CL}_{\text{int}})$.
The filter `3 < CLint < 150` is applied to the reported `standard_value` in µL/min/mg **before** the $\log_{10}$ transform, and the comparison is strict at both ends.

## Censoring Policy
*   The N = 731 observations with `NULL` standard relations strictly inside (3, 150) are treated as observed quantitative measurements under an assay-specific preregistered modelling assumption.
*   The values 3 and 150 are treated strictly as **working censoring boundaries**. Formal analytical LLOQ/ULOQ status remains UNRESOLVED. The modelling plan does not depend on resolving that terminology.

## Molecular Identity Policy
*   Identity relies on verified canonical SMILES. Zero unparseable SMILES exist across the audited sources.
*   CHEMBL3301370/71/72 have one row per unique structure with no within-assay duplicates.
*   **Rule:** We will not silently standardize salts, tautomers, stereochemistry, or multicomponent structures. Any handling of the 223 molecules with unspecified potential stereochemistry or the four multicomponent structures in the Biogen dataset must be explicitly preregistered if altered.

## Representations
Exactly **two** representations. No third is added in v2.

### R1 — Physicochemical descriptors (frozen list, 12)
As exposed by `rdkit.Chem.Descriptors` at the pinned RDKit version, computed on the unmodified deposited structure:
`MolWt`, `MolLogP`, `MolMR`, `TPSA`, `NumHDonors`, `NumHAcceptors`, `NumRotatableBonds`, `RingCount`, `NumAromaticRings`, `NumAliphaticRings`, `FractionCSP3`, `HeavyAtomCount`.
Chosen as the standard interpretable drivers of microsomal metabolic stability. **No descriptor may be added, removed or substituted after any performance number is seen.**
*   **Scaling:** `StandardScaler` **for Ridge only**, fitted inside each training fold. Random Forest receives raw descriptors.
*   **Non-finite handling:** descriptors are computed for all 1,102 records and the count of non-finite cells is reported. Any non-finite value is replaced by the **median of that descriptor within the training fold**, via a `SimpleImputer(strategy="median")` fitted inside the fold. No compound is dropped for a non-finite descriptor.
*   **Zero-variance:** a descriptor constant within a training fold is dropped **within that fold** for Ridge. Deterministic; reported.

### R2 — Morgan fingerprints (frozen geometry)
`GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048, useChirality=False)` — ECFP4-equivalent.
*   **Binary bit vectors, not counts.**
*   `useChirality=False`, for the same reason as the scaffold rule: 223 molecules carry unspecified potential stereochemistry, and chirality-aware bits would encode annotation completeness.
*   **No scaling and no imputation.** Bits are already on a common scale and are always defined.

### Concatenation
**Descriptors and fingerprints are never concatenated in this reanalysis.** A concatenated block would be a third, unpreregistered representation mixing standardised continuous features with sparse binary ones under a single Ridge penalty, and would raise the pipeline count without a stated hypothesis.

## Model Pipelines and Final Selection Rule

### Frozen pipelines (four predictive pipelines plus two baselines; no model is added without a stated pre-performance justification)

| ID | Representation | Estimator |
|---|---|---|
| P0a | none | constant = training-fold **median** (MAE baseline) |
| P0b | none | constant = training-fold **mean** (RMSE baseline) |
| P1 | R1 descriptors | `Ridge` (imputer → scaler → ridge) |
| P2 | R2 Morgan | `Ridge` (no imputer, no scaler) |
| P3 | R1 descriptors | `RandomForestRegressor` (imputer → RF) |
| P4 | R2 Morgan | `RandomForestRegressor` |

### Selection rule (deterministic, fixed before any number is seen)
Selection uses **inner grouped-CV mean $\log_{10}$-MAE only** strictly among candidates P1 through P4 (P0a and P0b are strictly non-selected baselines). Applied in order, stopping at the first criterion that discriminates:
1. Lowest mean inner-CV $\log_{10}$-MAE.
2. If two candidates are within **0.001 $\log_{10}$ units**, prefer the simpler model family in the fixed order **Ridge < Random Forest**.
3. Still tied: prefer **R1 descriptors** over R2 Morgan.
4. Still tied: prefer the **more strongly regularised** setting — larger `alpha`; larger `min_samples_leaf`; then smaller `max_features`.
5. Still tied: lowest pipeline ID in the fixed lexicographic order P1 < P2 < P3 < P4.

### Holdout access rule (binding)
**Exactly one selected pipeline (from P1-P4), plus baselines P0a and P0b, are evaluated on the final holdout.** The non-selected pipelines are **never** evaluated on it. Their inner-CV results are reported in full; their holdout results do not exist. The holdout is touched **once**.

The holdout result is reported **whatever it shows**. Re-selection, metric substitution, grid extension, representation change and re-partitioning are all prohibited after the holdout is read.

## Split and Validation Strategy

### Scaffold definition (frozen)
*   Scaffold key = the **atomic Bemis–Murcko scaffold** as returned by `rdkit.Chem.Scaffolds.MurckoScaffold.MurckoScaffoldSmiles(mol=m, includeChirality=False)`.
*   `includeChirality=False` is deliberate.
*   **Multicomponent structures:** the scaffold is computed on the **largest fragment by heavy-atom count**; ties are broken by lexicographically smallest canonical SMILES.
*   **Acyclic molecules** are **pooled into one group** with the reserved key `__ACYCLIC__`.

### Deterministic assignment (frozen, no RNG)
The partition uses **no random number generator at all**.
1. Compute the scaffold key for **all 1,102 CHEMBL3301370 records**.
2. Order groups by `int(sha256(scaffold_key.encode("utf-8")).hexdigest()[:8], 16)`, ties broken by lexicographic scaffold key.
3. Walk that order assigning whole groups to the **final holdout** until the holdout first contains **≥ 20% of the 731-cohort compounds**; all remaining groups form the **CV pool**.
4. If any single group is itself larger than the holdout budget, it is assigned to the **CV pool** and skipped for the holdout; the walk continues.
5. Assign CV-pool groups to **5 inner folds** by walking the same order and placing each group into the fold with the fewest 731-cohort compounds so far, ties broken by lowest fold index.

**Target values (numerical magnitudes) are never read for partitioning; however, frozen cohort membership is a function of the target filter, and that membership remains fixed.** Target-informed split optimisation is **prohibited**.

### Holdout proportion (frozen)
**20%** of the 731-cohort, ≈ 146 compounds, assigned by whole scaffold groups.

### Inner cross-validation (frozen)
**5-fold grouped CV over the CV pool** (≈ 585 compounds), using the persisted fold column. All hyperparameter selection, representation selection and pipeline selection occur **entirely within this inner CV**.

### Seeds
The split needs none. Elsewhere `random_state = 0` is fixed for every stochastic estimator (`RandomForestRegressor`). Hyperparameter search is exhaustive grid search, so it needs no seed. The bootstrap seed is fixed at 0.

### One holdout plus grouped CV, not repeated scaffold splits
This is preferred for the **confirmatory** claim. Any random (non-scaffold) split may appear **only** as explicitly labelled exploratory comparison.

### Split characterisation, reported before modelling
Report the number of scaffold groups, **fraction of groups that are singletons**, largest group size, the size of `__ACYCLIC__`, and the distribution of maximum Tanimoto similarity (frozen ECFP4) from each holdout compound to the CV pool. **If the singleton fraction is high, the scaffold split provides weaker structural separation than the term implies, and that is reported as a stated limitation on the confirmatory estimate.** This characterisation is a mandatory pre-freeze check before retaining the `__ACYCLIC__` pooling. No second partition is created in response to it.

## Master Structural Partition
Exactly **one** partition governs every analysis on CHEMBL3301370. It is computed once by the procedure in *Split and Validation Strategy* over **all 1,102 records**, using structure only, and is persisted to `splits/master_partition.csv` with a recorded SHA-256 before the first model fit.

Columns: `chembl_id`, `canonical_smiles`, `scaffold_key`, `scaffold_group_id`, `partition` (`holdout` | `cv`), `cv_fold` (0–4, null for holdout), `cohort` (`interior_731` | `below_274` | `above_84` | `ambiguous_13`).

**Binding rules:**
*   Fold membership is a function of **structure only**.
*   The primary regression, Sensitivity Analysis A, Sensitivity Analysis B, the censor-aware evaluation, the applicability-domain analysis and the HLM–HH paired analysis all read this file. None regenerates a partition.
*   Analysis A and Analysis B differ **only** in the treatment of the 13 boundary-ambiguous records.
*   The censored 274 and 84 receive fold assignments from the same partition.
*   The partition file is **immutable after first fit**.
*   The Biogen cohort uses a **separate** partition file, `splits/biogen_partition.csv`, built by the identical algorithm.

## Hyperparameter Selection
**Exhaustive grid search only.** Random search is not used, so no search seed exists.
*   **Selection criterion:** lowest **mean $\log_{10}$-MAE across the five inner grouped CV folds**, matching the primary metric.
*   **Search spaces, frozen:**
    *   Ridge: `alpha ∈ {0.01, 0.1, 1, 10, 100, 1000}` (6 settings; `fit_intercept=True`).
    *   Random Forest: `max_features ∈ {"sqrt", 0.3, 1.0}` × `min_samples_leaf ∈ {1, 3, 5}` (9 settings), with `n_estimators = 500`, `max_depth = None`, `random_state = 0` fixed.
*   **All preprocessing is fitted inside training folds.**
*   Grids may not be extended, recentred or refined after any performance number is seen. If a selected value sits at a grid edge, that fact is **reported as a limitation**, not fixed by widening the grid.

## Metrics
*   **Primary metric:** Mean Absolute Error (MAE) on the $\log_{10}$ scale.
*   **Primary baseline:** a constant predictor equal to the **median** of the training-fold $\log_{10}$ target. The median is the MAE-optimal constant, so baseline and primary metric are matched.
*   **Secondary metrics**, reported in every results table alongside the primary:
    *   RMSE on the $\log_{10}$ scale. **Where RMSE is reported, it is compared against a constant predictor equal to the training-fold *mean***, which is the RMSE-optimal constant.
    *   Spearman rank correlation.
    *   Coefficient of determination ($R^2$), reported with the caveat that $R^2$ is deflated by the range restriction of the (3, 150) cohort and is not comparable to studies using boundary-substituted targets.
*   **Fold-error metric:** proportion of predictions within the two-fold agreement band ($\pm\log_{10}(2) \approx \pm 0.301$), reported with a 95% interval computed by the same scaffold-cluster bootstrap used for the primary comparison.
*   *Constraint (unchanged):* $\pm 0.301$ is a two-fold agreement band only. It is **not** an irreducible noise floor, a Bayes-error estimate, a significance threshold, or a practical-utility threshold.
*   **Metric switching is prohibited.** MAE is primary whatever any metric shows.

## Censor-Aware Evaluation
The 274 `<3` and 84 `>150` records are never assigned exact continuous targets and never enter any continuous residual, in the primary analysis or any sensitivity analysis. They are evaluated **by the ordering of held-out predictions only**, which is invariant to the bounded output range of tree ensembles and therefore comparable across all model families.

### Primary censor-aware metrics — tail concordance
Let $L$, $U$ and $Q$ denote the held-out left-censored, right-censored and interior (N=731 cohort) evaluation groups, and $p$ a model prediction on the $\log_{10}$ scale.
*   **Lower-tail concordance:** $C_L = P(p_L < p_Q) + \tfrac{1}{2}P(p_L = p_Q)$
*   **Upper-tail concordance:** $C_U = P(p_U > p_Q) + \tfrac{1}{2}P(p_U = p_Q)$

These are Mann–Whitney/AUC statistics: 0.5 is no discrimination, 1.0 is perfect separation.
Computation rules, fixed now:
*   Average over every eligible tail–$Q$ pair; correctly ordered pair scores 1, tie 0.5, reversal 0.
*   **Both members of a pair must come from the same fitted model and the same held-out fold, and neither may have been used to train that model.**
*   Pool pair scores across folds weighted by eligible pair count. Never compare predictions from different fitted models as if paired.
*   Report the $L$, $U$ and $Q$ evaluation sizes and the eligible pair count for every reported score. A fold with no eligible pairs contributes none; if none exist overall, report **undefined** — never an imputed 0.5.
*   Confidence intervals resample **scaffold clusters**, not pairs: tail–$Q$ pairs are strongly dependent and pair counts must never be treated as independent observations.
*   $N=274$ and $N=84$ carry materially different precision; that caveat is retained wherever $C_L$ and $C_U$ are discussed, and no lower-versus-upper difference is interpreted mechanistically.

### Secondary, descriptive — one-sided boundary-violation loss
*   Lower: $\frac{1}{|L|}\sum_{i \in L} \max\!\big(0,\; p_i - \log_{10} 3\big)$
*   Upper: $\frac{1}{|U|}\sum_{i \in U} \max\!\big(0,\; \log_{10} 150 - p_i\big)$

**Binding constraint:** this loss is **reported within a model family only and is never used for model selection or cross-family comparison.**

### Prohibited
*   Treating 3 or 150 as exact observations, anywhere in the science track.
*   Any accuracy-style "percent correct" on censored records based on absolute bound satisfaction.
*   Claiming that a concordance score establishes a numerical clearance value for a censored compound, or that it verifies the unknown true clearance.

## Applicability-Domain Analysis
*   **Similarity definition, fixed and model-independent:** Tanimoto on the frozen ECFP4 fingerprint (radius 2, 2048 bits, `useChirality=False`) — **used even when the selected pipeline is the descriptor pipeline**, so the AD axis never changes with the selected model.
*   **Statistic:** for each evaluation compound, the **maximum Tanimoto to any compound in the training pool of its own fold**.
*   **Bins, fixed now, before any residual is seen:** [0, 0.2), [0.2, 0.3), [0.3, 0.4), [0.4, 0.6), [0.6, 1.0]. Report per-bin N, MAE and a bootstrap interval. **A bin with fewer than 20 compounds is reported as a count and marked under-powered, and is not compared.**
*   Also report the continuous relationship: absolute residual vs nearest-neighbour similarity as a scatter, summarised by a single prespecified Spearman correlation between the two.
*   **No applicability-domain cutoff is declared in v1**, and no bin edge is moved after residuals are seen. The analysis describes how reliability decays; it does not certify a domain.

## Residual Diagnostics
Aimed at predictive failure and heteroscedasticity, not at distributional inference. No normality test is performed; **no test statistic or p-value is computed for residual distribution shape.** A QQ plot may be shown as a purely descriptive display and is not interpreted inferentially.

1.  Predicted vs observed, with the $y=x$ line.
2.  Residual vs predicted.
3.  **Absolute** residual vs predicted, with prespecified tercile summaries — the heteroscedasticity check.
4.  **Boundary-compression check (prespecified, expected failure mode):** mean signed residual in the lowest and highest prediction terciles. A model trained on a target truncated to (3, 150) is expected to compress toward the centre, producing systematically positive residuals at the low end and negative at the high end. This is reported explicitly whether or not it appears.
5.  Residual vs nearest-neighbour Tanimoto (shared with the AD analysis).
6.  The **10 largest absolute residuals** listed with structures and scaffold groups, supporting the failure analysis that is this project's stated purpose.

## HLM–HH Secondary Analysis
Units differ (HLM µL/min/mg; HH µL/min/10⁶ cells). No raw ratio, no subtraction, no physiological scaling, no IVIVE. Microsomal CLint is never described as clinical clearance. Rank agreement only.

### Deterministic qualifier policy (frozen)
*   **Eligible paired set:** those of the 187 structural overlaps whose **HLM record belongs to the N=731 primary interior cohort** *and* whose **HH record belongs to the 289 null-relation HH records**. CHEMBL3301372 has zero null-relation records at 3 and zero at 150, so all 289 are interior and the HH side contributes no boundary ambiguity.
*   **Provisional Cross-Tab Evidence (PENDING_FINAL_MACHINE_VERIFICATION)**: 
    *   187 total matched compounds
    *   94 interior-observed in both HLM and HH
    *   59 interior-observed in one assay and censored in the other
    *   32 censored in both assays
    *   2 boundary-ambiguous pairs
*   **The eligible count for ordinary quantitative Spearman correlation is precisely the 94 interior/interior pairs (PENDING_FINAL_MACHINE_VERIFICATION).** No figure, table or sentence may imply that the correlation is computed over 187 compounds.
*   **Censored members are never ranked.** Pairs censored in either assay are reported **only** as a 3×3 contingency table of HLM range category (BELOW / IN-RANGE / ABOVE) × HH range category, with counts.
*   **Boundary-ambiguous pairs:** The **primary** Spearman **excludes** them, consistent with the frozen N=731 primary cohort. A sensitivity Spearman including them as interior is reported beside it, mirroring Sensitivity Analysis A. **The choice between the two is not made on which correlation is stronger; the exclusive estimate is primary by prespecification and both are reported.**
*   Report Spearman $\rho$ with a 95% scaffold-cluster bootstrap interval and the eligible N.
*   **Mandatory caveat:** The correlation is computed strictly on the restricted in-range-in-both cohort. It is never quoted as a general assay-agreement coefficient.

## TDC Benchmark Reproduction
Reproduced **exactly as shipped**, via the official harness: `Clearance_Microsome_AZ` retrieved through the TDC ADMET benchmark group API, using the **harness's own split** and **the metric the harness itself returns from `evaluate()`** (Exact split, seeds, and metric are **PENDING_PRE_FREEZE_VERIFICATION**). Reported with the harness's mean and standard deviation across its prescribed seeds.

**Separation (binding):**
*   TDC uses **its own split**, never the master structural partition.
*   TDC results never appear in the same table or figure as science-track results.
*   No TDC-derived choice — hyperparameter, representation or threshold — informs the science track, and no science-track result is quoted as a benchmark number or vice versa.
*   Boundary substitution (274 `<3` → 3, 84 `>150` → 150, giving 287 values at exactly 3) is part of the benchmark's historical representation and stays **only** here. Results are reported **solely as benchmark comparability**, never as accuracy on experimental measurements.
*   The five structural-representation mismatches are reported, so the two sources are not described as interchangeable.

## Biogen Replication
Within-dataset replication of the **modelling procedure**, never a pooled external test set. Both analyses below are **exploratory**; neither is confirmatory, and neither can change any conclusion of the primary track.

*   **B1 — as-shipped:** all 3,087 populated `LOG HLM_CLint (mL/min/kg)` values, used exactly as distributed.
*   **B2 — floor-excluded sensitivity:** the 2,129 values strictly greater than 0.675686709.
*   Both are **always reported**, side by side. The choice between them is not made on which performs better, and the floor is described as **unresolved** in both — never as censored, never as exact.
*   **Labels are source-provided logs.** No re-logging, no unit conversion, no transformation to imitate the AstraZeneca assay.
*   **Units differ from HLM** (mL/min/kg vs µL/min/mg) and the label is already logged by the source. **Biogen MAE/RMSE values are therefore not numerically comparable to HLM MAE/RMSE and may never be placed in the same table or compared as magnitudes.**
*   Biogen uses `splits/biogen_partition.csv`, built by the identical scaffold algorithm. The four multicomponent structures are handled by the largest-fragment rule for **grouping only**; harmonisation of multicomponent structures and unspecified stereochemistry remains deferred.

## Sensitivity Analyses
We will conduct two parallel sensitivity analyses for the 13 `NULL`-at-3 boundary-ambiguous records:
*   **Analysis A:** Include them in the primary point-regression cohort as exact 3 values.
*   **Analysis B:** Treat them as left-censored at 3 and evaluate them directionally alongside the 274 `<3` records.
*   Both analyses strictly use the **master structural partition**.
*   *Rule:* We will not choose between Analysis A and B based on downstream performance; both sets of metrics will be reported.

## Decision Criteria
### Primary comparison
$$\Delta \;=\; \mathrm{MAE}_{\log_{10}}(\text{P0a median baseline}) \;-\; \mathrm{MAE}_{\log_{10}}(\text{selected pipeline})$$
computed on the scaffold holdout reserved from v2 tuning. $\Delta > 0$ favours the model.

### Interval (frozen)
**Paired scaffold-cluster bootstrap.** Resample **scaffold groups** in the holdout with replacement — never individual compounds, which are dependent within a group — to $B = 10{,}000$ replicates, `seed = 0`. Both predictors are evaluated on the identical resample (paired). Report the **95% percentile interval** for $\Delta$, alongside both absolute MAEs and the realised holdout compound and group counts.

### Pre-specified conclusions
*   **Improvement demonstrated** iff the lower bound of the 95% interval for $\Delta$ exceeds 0.
*   **Improvement not demonstrated** otherwise. $\Delta$ and its interval are reported either way, with the same prominence.
*   **Statistical significance is not scientific usefulness.** A $\Delta$ whose interval excludes zero but whose magnitude is small relative to two-fold assay agreement is reported as *detectable but not decision-relevant*. The two judgements are reported as separate sentences and never merged.
*   The same bootstrap procedure produces intervals for RMSE (against P0b), $C_L$, $C_U$ and the two-fold band proportion. No multiplicity adjustment is applied because **only $\Delta$ is confirmatory**; all other intervals are descriptive and are labelled as such.

## Failure Criteria
If $\Delta$'s 95% interval includes or lies below zero, the finding is stated exactly as:
> **Under this preregistration** — the 12 frozen RDKit descriptors and binary ECFP4 (r=2, 2048 bits, no chirality); Ridge and Random Forest with the frozen grids; the N=731 CHEMBL3301370 quantifiable-range cohort; and a single 20% Bemis–Murcko scaffold holdout with 5-fold grouped inner CV — **the selected pipeline did not demonstrate a detectable reduction in $\log_{10}$-MAE relative to a median-constant baseline on structurally novel compounds.**

Permitted accompanying statements: that the result is confounded with sample size, representation choice, grid coverage, scaffold-split severity and assay noise, which this design cannot separate; and that the scaffold holdout deliberately measures extrapolation to novel chemistry, which is a harder task than interpolation within a series.

**Prohibited:** that structural representations do not predict intrinsic clearance; that QSAR fails on this endpoint; that the endpoint is unpredictable; any use of the word *falsified* for a hypothesis broader than the frozen pipeline, cohort and split named above; and any post-hoc addition of models or representations to rescue a null result.

## Confirmatory vs. Exploratory Analyses
*   **Confirmatory:** The evaluation of the frozen, cross-validation-selected primary model on the scaffold holdout test set (reserved from v2 tuning, though previously analyzed in v1).
*   **Exploratory:** Any random-split evaluations, the Biogen within-dataset replication, the TDC benchmark reproduction, and post-hoc feature importance derivations.

## Relationship to the Superseded Three-Class Classifier
`CENSORING_POLICY_MEMO.md` froze a three-class assay-range classifier (BELOW / IN-RANGE / ABOVE, N=1,102) as Component 2. This preregistration **descopes that component from v2** and records the descoping here explicitly. The consequence is stated as a limitation wherever the regression is reported: **the primary model is conditional on a compound already being known to fall in the quantifiable range, and this version supplies no model that predicts range membership.** The censored records are retained and used, but only through the ordering-based censor-aware evaluation. Reinstating a range classifier is deferred to a separately preregistered analysis.

## Reproducibility Requirements
*   Fixed random seeds where relevant.
*   Deterministic, persisted split assignments saved to disk via SHA-256 assignment.
*   Machine-readable configuration.
*   Hashes for derived datasets.
*   Saved model parameters.
*   Explicit logging of exact package versions, including fixing **RDKit version** alongside NumPy and scikit-learn.
*   **The holdout evaluation is executed once and reported in full regardless of outcome; a null result is reported with the same prominence as a positive one.**

## Explicitly Deferred Questions
*   The formal analytical LLOQ/ULOQ status of the boundaries.
*   Physiological scaling to in vivo clearance.
*   Harmonization of the Biogen multicomponent structures and unspecified stereochemistry.

---
## FROZEN_ANALYSIS_DECISIONS

| Parameter | Decision |
|---|---|
| Population | CHEMBL3301370 point-regression cohort, N=731 |
| Target | $\log_{10}$ apparent intrinsic clearance (µL/min/mg) |
| Representation | Frozen RDKit descriptors (12) OR frozen Morgan ECFP4 fingerprint (2048 bit, no chirality) |
| Model | Median baseline; Mean baseline; Ridge; Random Forest |
| Split | 20% Bemis-Murcko scaffold holdout (N≈146), reserved from v2 tuning |
| Tuning | 5-fold grouped inner CV (scaffold-aware), exhaustive grid search over defined parameters |
| Primary Metric | Mean Absolute Error (MAE) on $\log_{10}$ scale |
| Baseline | Training-fold median |
| Censor-Aware Metric | Tail concordance ($C_L$, $C_U$) evaluated by ordering |
| Model-Selection Rule | Lowest inner-CV $\log_{10}$-MAE among P1-P4, with fixed hierarchy of tie-breakers (simpler -> descriptors -> regularised -> lexicographic) |
| Final Evaluation Rule | Exactly one selected pipeline plus median/mean baselines touch the holdout once |
| Uncertainty Procedure | Paired scaffold-cluster bootstrap (B=10,000) for 95% interval on difference |

PREREGISTRATION_STATUS: PENDING_FINAL_EVIDENCE_CHECKS
