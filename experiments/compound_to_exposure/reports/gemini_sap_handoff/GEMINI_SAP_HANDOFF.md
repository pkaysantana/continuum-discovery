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


---
# Supplied source documents

Read these as source material under the hierarchy in the revision task. Historical assertions in a source do not override the confirmed new-analysis scope and prior-modelling disclosure.


---
<!-- BEGIN INPUT inputs/docs/STATISTICAL_ANALYSIS_PREREGISTRATION.md -->

Source: `inputs/docs/STATISTICAL_ANALYSIS_PREREGISTRATION.md`  
SHA-256 of exact source bytes: `140b25430c346a484cf09a0f6fb8951bd66b595c1f53553e635d8db864e77940`  
Origin: latest working-tree v2 reanalysis draft snapshot after concurrent edit; uncommitted

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


<!-- END INPUT inputs/docs/STATISTICAL_ANALYSIS_PREREGISTRATION.md -->


---
<!-- BEGIN INPUT inputs/docs/STATISTICAL_ANALYSIS_PREREGISTRATION_PRE_HANDOFF_SNAPSHOT.md -->

Source: `inputs/docs/STATISTICAL_ANALYSIS_PREREGISTRATION_PRE_HANDOFF_SNAPSHOT.md`  
SHA-256 of exact source bytes: `442fe23ee0790fc097684e84d78033f479113c31035788fb180844f0fc3be42a`  
Origin: earlier working-tree snapshot preserved before concurrent v2 draft update; uncommitted

# Statistical Analysis Preregistration: QSAR/DMPK HLM Intrinsic Clearance

## Scientific Question
Can the structural representation and baseline physicochemical properties of a compound reliably predict its intrinsic clearance in human liver microsomes (HLM) within a continuous, finite observable range, and to what extent does structural similarity govern prediction error?

## Primary Estimand
The expected value of the log-transformed apparent intrinsic clearance ($\log_{10}(\text{CL}_{\text{int}})$) for small molecules in human liver microsomes (HLM), conditional on the molecule's structural representation (RDKit physicochemical descriptors and/or Morgan fingerprints), strictly evaluated within the observable range (3, 150) µL/min/mg.

## Source-of-Truth / Superseded Documents
*   **Source of Truth Hierarchy:**
    1.  The explicit frozen decisions in the authoritative statistical planning prompt.
    2.  Verified audit reports and independently reproduced numerical findings.
    3.  `docs/DATASET_SELECTION_MEMO.md`.
    4.  `docs/CENSORING_POLICY_MEMO.md`.
*   **Superseded Decisions:** This document formally supersedes `docs/CENSORING_POLICY_MEMO.md` where conflicts exist. Specifically, the assumption that `NULL` standard relations mean exact equality ("=") in ChEMBL is **not established** and is hereby superseded by the dataset rules defined below.

## Dataset Populations
*   **Primary Science Dataset:** CHEMBL3301370 (AstraZeneca HLM apparent intrinsic clearance). Units: µL/min/mg. Total N = 1,102.
*   **Primary Point-Regression Cohort:** N = 731.
    *   *Inclusion Rule:* `standard_relation IS NULL AND 3 < CLint < 150`.
*   **Censored / Boundary Populations:**
    *   N = 274 `<3`: Left-censored at working boundary 3.
    *   N = 84 `>150`: Right-censored at working boundary 150.
    *   N = 13 `NULL` exactly at 3: Boundary-ambiguous, excluded from primary point-regression, retained for sensitivity analyses.
*   **Secondary Human Assay:** CHEMBL3301372 (Human hepatocyte apparent intrinsic clearance). N = 408 (187 structural overlaps with HLM).
*   **External Replication:** Biogen public HLM dataset. N = 3,521 total structures; N = 3,087 populated HLM values.
*   **Benchmark Track:** TDC Clearance_Microsome_AZ. N = 1,102.

## Target Definition
The target is the base-10 logarithm of apparent intrinsic clearance, $\log_{10}(\text{CL}_{\text{int}})$.

## Censoring Policy
*   The N = 731 observations with `NULL` standard relations strictly inside (3, 150) are treated as observed quantitative measurements under an assay-specific preregistered modelling assumption.
*   **Boundary-status caveat U3:** The values 3 and 150 are treated strictly as **working censoring boundaries**. Formal analytical LLOQ/ULOQ status remains UNRESOLVED. The modelling plan does not depend on resolving that terminology, and they will not be called formally established LLOQ/ULOQ without a primary source.

## Molecular Identity Policy
*   Identity relies on verified canonical SMILES.
*   Zero unparseable SMILES exist across the audited sources.
*   CHEMBL3301370/71/72 have one row per unique structure with no within-assay duplicates.
*   **Rule:** We will not silently standardize salts, tautomers, stereochemistry, or multicomponent structures. Any handling of the 223 molecules with unspecified potential stereochemistry or the four multicomponent structures in the Biogen dataset must be explicitly preregistered if altered.

## Representations
Candidate representations are restricted to:
*   Preregistered RDKit physicochemical descriptors.
*   Morgan/ECFP fingerprints.

*Rationale:* Version 1 (v1) of this project favours interpretable conventional methods. These representations establish a well-understood, domain-standard baseline for chemical predictive modelling.

## Models and Baselines
Candidate models are restricted to:
*   Constant/median baseline predictor.
*   Ridge regression.
*   Random Forest regression.

*Constraints:* 
*   Deep neural networks will not be used in the primary v1 analysis due to a lack of unusually strong statistical justification at N≈731.
*   Models are not added merely to increase the comparison count. Any changes to this list must be statistically justified.

## Split and Validation Strategy
*   **Primary Strategy:** Scaffold-grouped cross-validation plus one untouched final scaffold holdout test set.
*   *Rationale:* For a dataset of N≈731, a single fixed split can yield high-variance performance estimates, while repeated scaffold splits risk analogue leakage across different iterations. A cross-validated inner loop (e.g., 5-fold Bemis-Murcko scaffold split) allows stable hyperparameter tuning and model evaluation, while reserving a single, structurally distinct holdout test set guarantees a strict, unbiased final confirmatory evaluation.
*   Any random split may only appear as an explicitly exploratory comparison, not as the primary result.
*   The final test set remains completely untouched until the single final confirmatory evaluation. It will not be used for model selection, feature selection, hyperparameter tuning, representation selection, threshold selection, or decisions about censoring.

## Hyperparameter Selection
Hyperparameter selection will be performed exclusively via grid or random search over predefined grids evaluated within the inner cross-validation folds. 

## Metrics
*   **Primary Metric:** Root Mean Square Error (RMSE) on the $\log_{10}$ scale.
*   **Secondary Metrics:** 
    *   Mean Absolute Error (MAE) on the $\log_{10}$ scale.
    *   Spearman Rank Correlation.
    *   Coefficient of Determination ($R^2$).
*   **Fold-Error Metrics:** Proportion of predictions within a 2-fold agreement band ($\pm \log_{10}(2) \approx \pm 0.301$).
*   *Constraint:* $\pm 0.301$ is treated *only* as a two-fold agreement band. It is NOT an irreducible noise floor, a Bayes-error estimate, or a significance threshold.

## Censor-Aware Evaluation
A separate evaluation will be conducted for the 274 `<3` and 84 `>150` observations.
*   This evaluation will use the continuous model's predictions **directionally**.
*   A prediction for a `<3` record is "correct" if the model predicts $\le 3$.
*   A prediction for a `>150` record is "correct" if the model predicts $\ge 150$.
*   We will **not** pretend 3 or 150 are exact ground-truth labels for calculating continuous residuals.

## Applicability-Domain Analysis
Model residuals will be analyzed as a function of structural distance (e.g., Tanimoto similarity) to the nearest training set neighbor.
*   *Rationale:* To determine how rapidly predictive reliability decays as a function of chemical extrapolation.

## Residual Analysis
Standard residual diagnostics (e.g., predicted vs. observed, residuals vs. predicted) will be generated for the N=731 cohort to inspect for systemic bias, heteroscedasticity, and normality of errors.

## HLM–HH Secondary Analysis
*   CHEMBL3301372 (HH) has different native units (µL/min/10^6 cells) than HLM (µL/min/mg).
*   *Constraints:* There will be no raw HLM/HH ratio calculated, no direct raw subtraction, no physiological scaling in v1, and no in vitro to in vivo extrapolation (IVIVE) claims. Claims that microsomal $\text{CL}_{\text{int}}$ is clinical clearance are strictly forbidden. The analysis will focus purely on ranking and correlation.

## TDC Benchmark Reproduction
*   TDC `Clearance_Microsome_AZ` will be reproduced preserving the dataset as shipped (where censored boundaries are stripped of `<`/`>` and represented as bare numerical 3 and 150, alongside 5 structural representation mismatches).
*   This benchmark reproduction is fundamentally separate from the censor-aware primary scientific analysis.

## Biogen Replication
*   The Biogen dataset is a within-dataset replication/robustness cohort, not a directly pooled external test set.
*   The labels will not be transformed to imitate the AstraZeneca assay without a separately justified and preregistered analysis.
*   The 958 values equal to the dataset minimum (0.675686709) have an unresolved boundary interpretation and will not be unilaterally declared as censored.

## Sensitivity Analyses
We will conduct two parallel sensitivity analyses for the 13 `NULL`-at-3 boundary-ambiguous records:
*   **Analysis A:** Include them in the primary point-regression cohort as exact 3 values.
*   **Analysis B:** Treat them as left-censored at 3 and evaluate them directionally alongside the 274 `<3` records.
*   *Rule:* We will not choose between Analysis A and B based on downstream performance; both sets of metrics will be reported.

## Decision/Failure Criteria
*   **Success:** A model is considered scientifically useful only if it demonstrates a statistically significant improvement in the primary metric (RMSE) over the constant/median baseline on the scaffold holdout set.
*   **Failure:** If the Ridge or Random Forest models fail to outperform the baseline, the hypothesis that these structural representations predict intrinsic clearance within the observable continuous range is falsified for this dataset.

## Confirmatory vs. Exploratory Analyses
*   **Confirmatory:** The evaluation of the frozen, cross-validation-selected primary model on the untouched scaffold holdout test set (N=731 point-regression cohort).
*   **Exploratory:** Any random-split evaluations, the Biogen within-dataset replication, the TDC benchmark reproduction, and post-hoc feature importance derivations.

## Reproducibility Requirements
*   Fixed random seeds where relevant.
*   Deterministic, persisted split assignments saved to disk.
*   Machine-readable configuration.
*   Hashes for derived datasets.
*   Saved model parameters.
*   Explicit logging of exact package versions.
*   No manual post-result changes to frozen analysis decisions.

## Frozen Decisions
*   The primary point-regression dataset is exclusively N=731.
*   The target is transformed via $\log_{10}$.
*   The working boundary values are 3 and 150.
*   Scaffold splitting is the primary data partitioning strategy.
*   The interpretation of $\pm 0.301$ is limited strictly to a two-fold agreement band.

## Explicitly Deferred Questions
*   The formal analytical LLOQ/ULOQ status of the boundaries.
*   Physiological scaling to in vivo clearance.
*   Harmonization of the Biogen multicomponent structures and unspecified stereochemistry.

---
PREREGISTRATION_STATUS: READY_FOR_ADVERSARIAL_REVIEW


<!-- END INPUT inputs/docs/STATISTICAL_ANALYSIS_PREREGISTRATION_PRE_HANDOFF_SNAPSHOT.md -->


---
<!-- BEGIN INPUT inputs/docs/ADVERSARIAL_PREREGISTRATION_REVIEW.md -->

Source: `inputs/docs/ADVERSARIAL_PREREGISTRATION_REVIEW.md`  
SHA-256 of exact source bytes: `103719d2ad3d87a12e20fa4e2b8dfe5d873e2c2baf605a406471a2a1536fde4a`  
Origin: 33f7e5aedabfb5ef0aa3d56a930cb5f82a5a4052

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


<!-- END INPUT inputs/docs/ADVERSARIAL_PREREGISTRATION_REVIEW.md -->


---
<!-- BEGIN INPUT inputs/docs/DATASET_SELECTION_MEMO.md -->

Source: `inputs/docs/DATASET_SELECTION_MEMO.md`  
SHA-256 of exact source bytes: `6fb903b926ec7a3fc3bf87fc9cbf8e18c90cb36ca940996338bea79a97cfb06b`  
Origin: 4640ea721204771979e5637e81217f59c65318e6

# DMPK Clearance Dataset Selection & Scientific Specification

This document defines the scientific specification and dataset selection rules for the first phase of the DMPK compound-to-exposure project, focusing on prediction and failure analysis.

## Dataset Selection & Processing
1. **Primary Science Data**: We will use direct ChEMBL data for the primary scientific analysis.
2. **Benchmark Reproduction**: The TDC (Therapeutics Data Commons) datasets will be used strictly for benchmark reproduction. 
3. **Exclusions**: The mixed-species TDC hepatocyte set is explicitly excluded from the analysis.
4. **Replication Strategy**: The Biogen dataset will be utilized as a within-dataset replication rather than treated as a naive transfer set.
5. **Data Handling**: Explicit censoring and UNKNOWN handling rules must be applied rigorously across all datasets.
6. **Performance Interpretation**: The interpretation of the two-fold repeatability band has been corrected and will serve as the realistic baseline for model performance expectations.

## HLM–HH Paired Analysis (v1 Rule)
For the v1 analysis, the paired Human Liver Microsome (HLM) and Human Hepatocyte (HH) analysis will remain secondary and descriptive, employing no physiological scaling.

On compounds measured in both assays, we will examine:
- Rank-order agreement between HLM and HH using Spearman correlation.
- Whether compounds ranked as high/low clearance in one assay behave similarly in the other.
- Assay-specific model residuals on the shared compounds.
- Whether molecular characteristics associated with large prediction errors differ between HLM and HH.

### Exclusions & Future Work
- **No Raw Ratios**: We will not compute a raw HLM:HH clearance ratio because the native units differ.
- **Deferred Physiological Scaling**: Physiologically scaled HLM:HH ratios (IVIVE) are deferred to a later, separately preregistered analysis that will require explicit scaling-factor sources and sensitivity analysis. 

This approach ensures the initial project remains sharply focused on prediction and failure analysis without letting IVIVE/scaling conflate the scope.


<!-- END INPUT inputs/docs/DATASET_SELECTION_MEMO.md -->


---
<!-- BEGIN INPUT inputs/docs/CENSORING_POLICY_MEMO.md -->

Source: `inputs/docs/CENSORING_POLICY_MEMO.md`  
SHA-256 of exact source bytes: `85184aff6d3976a7950c055bdf75e7723b68e8ed6c88aeb578f21e2a7520973f`  
Origin: 4640ea721204771979e5637e81217f59c65318e6

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


<!-- END INPUT inputs/docs/CENSORING_POLICY_MEMO.md -->


---
<!-- BEGIN INPUT inputs/reports/DATA_AUDIT.md -->

Source: `inputs/reports/DATA_AUDIT.md`  
SHA-256 of exact source bytes: `c09ddb308019034b61d8c1e1ec5ef2a6cb0f77ba59015375616ed24fa29097bd`  
Origin: 4640ea721204771979e5637e81217f59c65318e6

# Frozen-source data audit

OBSERVED: Acquisition and forensic characterisation only. No modelling or scientific preprocessing was executed.

## Counts

| Source | Rows | Unique IDs | Unique raw SMILES | Unique RDKit structures | Missing / invalid | Duplicate groups / excess rows |
|---|---:|---:|---:|---:|---:|---:|
| OBSERVED: CHEMBL3301370 | 1102 | 1102 | 1102 | 1102 | 0 / 0 | 0 / 0 |
| OBSERVED: CHEMBL3301371 | 837 | 837 | 837 | 837 | 0 / 0 | 0 / 0 |
| OBSERVED: CHEMBL3301372 | 408 | 408 | 408 | 408 | 0 / 0 | 0 / 0 |
| OBSERVED: Clearance_Microsome_AZ | 1102 | 1102 | 1102 | 1102 | 0 / 0 | 0 / 0 |
| OBSERVED: Clearance_Hepatocyte_AZ | 1213 | 1020 | 1020 | 1020 | 0 / 0 | 193 / 193 |
| OBSERVED: Biogen | 3521 | 3521 | 3521 | 3521 | 0 / 0 | 0 / 0 |

EXPECTED_FROM_MEMO: Task-supplied expected assay counts are 1102 (3301370), 837 (3301371), 408 (3301372). The memo freezes selection but contains no numeric counts.

## ChEMBL relations

| Assay | < | > | = | Anything else |
|---|---:|---:|---:|---:|
| OBSERVED: CHEMBL3301370 | 274 | 84 | 0 | 744 |
| OBSERVED: CHEMBL3301371 | 115 | 127 | 0 | 595 |
| OBSERVED: CHEMBL3301372 | 104 | 15 | 0 | 289 |

OBSERVED: CHEMBL3301370 censored/other reported boundaries: `{"<": [{"count": 274, "reported_value": "3.0"}], ">": [{"count": 84, "reported_value": "150.0"}], "UNKNOWN": [{"count": 10, "reported_value": "10.0"}, {"count": 1, "reported_value": "10.23"}, {"count": 1, "reported_value": "10.47"}, {"count": 2, "reported_value": "10.5"}, {"count": 1, "reported_value": "10.67"}, {"count": 1, "reported_value": "10.72"}, {"count": 2, "reported_value": "10.96"}, {"count": 1, "reported_value": "100.0"}, {"count": 1, "reported_value": "101.0"}, {"count": 1, "reported_value": "102.0"}, {"count": 2, "reported_value": "103.0"}, {"count": 2, "reported_value": "104.0"}, {"count": 1, "reported_value": "104.5"}, {"count": 4, "reported_value": "104.71"}, {"count": 1, "reported_value": "105.0"}, {"count": 1, "reported_value": "107.0"}, {"count": 1, "reported_value": "107.15"}, {"count": 17, "reported_value": "11.0"}, {"count": 5, "reported_value": "11.22"}, {"count": 3, "reported_value": "11.48"}, {"count": 1, "reported_value": "11.75"}, {"count": 1, "reported_value": "111.0"}, {"count": 2, "reported_value": "112.0"}, {"count": 4, "reported_value": "112.2"}, {"count": 2, "reported_value": "114.82"}, {"count": 2, "reported_value": "116.0"}, {"count": 2, "reported_value": "117.49"}, {"count": 1, "reported_value": "119.0"}, {"count": 13, "reported_value": "12.0"}, {"count": 1, "reported_value": "12.02"}, {"count": 2, "reported_value": "12.3"}, {"count": 1, "reported_value": "12.5"}, {"count": 2, "reported_value": "12.59"}, {"count": 1, "reported_value": "12.88"}, {"count": 2, "reported_value": "120.0"}, {"count": 1, "reported_value": "120.23"}, {"count": 2, "reported_value": "123.03"}, {"count": 1, "reported_value": "124.0"}, {"count": 2, "reported_value": "125.89"}, {"count": 1, "reported_value": "126.0"}, {"count": 1, "reported_value": "127.0"}, {"count": 1, "reported_value": "127.7"}, {"count": 1, "reported_value": "128.82"}, {"count": 1, "reported_value": "129.0"}, {"count": 10, "reported_value": "13.0"}, {"count": 2, "reported_value": "13.49"}, {"count": 2, "reported_value": "13.5"}, {"count": 3, "reported_value": "13.8"}, {"count": 2, "reported_value": "131.83"}, {"count": 1, "reported_value": "134.0"}, {"count": 1, "reported_value": "137.0"}, {"count": 2, "reported_value": "138.04"}, {"count": 12, "reported_value": "14.0"}, {"count": 4, "reported_value": "14.13"}, {"count": 4, "reported_value": "14.45"}, {"count": 2, "reported_value": "14.79"}, {"count": 1, "reported_value": "140.0"}, {"count": 1, "reported_value": "141.0"}, {"count": 1, "reported_value": "144.54"}, {"count": 1, "reported_value": "145.0"}, {"count": 2, "reported_value": "146.0"}, {"count": 8, "reported_value": "15.0"}, {"count": 3, "reported_value": "15.14"}, {"count": 1, "reported_value": "15.49"}, {"count": 1, "reported_value": "15.67"}, {"count": 3, "reported_value": "15.85"}, {"count": 7, "reported_value": "16.0"}, {"count": 1, "reported_value": "16.6"}, {"count": 4, "reported_value": "17.0"}, {"count": 1, "reported_value": "17.03"}, {"count": 1, "reported_value": "17.25"}, {"count": 1, "reported_value": "17.33"}, {"count": 2, "reported_value": "17.38"}, {"count": 2, "reported_value": "17.5"}, {"count": 6, "reported_value": "17.78"}, {"count": 5, "reported_value": "18.0"}, {"count": 1, "reported_value": "18.2"}, {"count": 1, "reported_value": "18.33"}, {"count": 1, "reported_value": "18.5"}, {"count": 1, "reported_value": "18.62"}, {"count": 5, "reported_value": "19.0"}, {"count": 1, "reported_value": "19.05"}, {"count": 1, "reported_value": "19.25"}, {"count": 2, "reported_value": "19.5"}, {"count": 3, "reported_value": "19.95"}, {"count": 5, "reported_value": "20.0"}, {"count": 5, "reported_value": "20.42"}, {"count": 1, "reported_value": "20.5"}, {"count": 1, "reported_value": "20.89"}, {"count": 8, "reported_value": "21.0"}, {"count": 5, "reported_value": "21.38"}, {"count": 1, "reported_value": "21.5"}, {"count": 2, "reported_value": "21.88"}, {"count": 5, "reported_value": "22.0"}, {"count": 3, "reported_value": "23.0"}, {"count": 1, "reported_value": "23.44"}, {"count": 3, "reported_value": "23.5"}, {"count": 1, "reported_value": "23.6"}, {"count": 4, "reported_value": "24.0"}, {"count": 4, "reported_value": "24.55"}, {"count": 5, "reported_value": "25.0"}, {"count": 2, "reported_value": "25.12"}, {"count": 4, "reported_value": "26.0"}, {"count": 2, "reported_value": "26.33"}, {"count": 7, "reported_value": "27.0"}, {"count": 2, "reported_value": "27.5"}, {"count": 4, "reported_value": "27.54"}, {"count": 5, "reported_value": "28.0"}, {"count": 1, "reported_value": "28.18"}, {"count": 1, "reported_value": "28.67"}, {"count": 2, "reported_value": "29.0"}, {"count": 2, "reported_value": "29.51"}, {"count": 13, "reported_value": "3.0"}, {"count": 1, "reported_value": "3.02"}, {"count": 1, "reported_value": "3.31"}, {"count": 1, "reported_value": "3.6"}, {"count": 1, "reported_value": "3.9"}, {"count": 2, "reported_value": "3.98"}, {"count": 4, "reported_value": "30.0"}, {"count": 1, "reported_value": "30.13"}, {"count": 2, "reported_value": "30.2"}, {"count": 1, "reported_value": "30.33"}, {"count": 3, "reported_value": "30.5"}, {"count": 2, "reported_value": "30.9"}, {"count": 4, "reported_value": "31.0"}, {"count": 1, "reported_value": "31.62"}, {"count": 1, "reported_value": "32.0"}, {"count": 2, "reported_value": "32.36"}, {"count": 7, "reported_value": "33.0"}, {"count": 2, "reported_value": "33.11"}, {"count": 2, "reported_value": "33.88"}, {"count": 2, "reported_value": "34.0"}, {"count": 3, "reported_value": "34.67"}, {"count": 11, "reported_value": "35.0"}, {"count": 1, "reported_value": "35.48"}, {"count": 4, "reported_value": "36.0"}, {"count": 1, "reported_value": "36.31"}, {"count": 3, "reported_value": "37.0"}, {"count": 2, "reported_value": "37.15"}, {"count": 4, "reported_value": "38.0"}, {"count": 1, "reported_value": "38.02"}, {"count": 2, "reported_value": "38.9"}, {"count": 1, "reported_value": "39.0"}, {"count": 1, "reported_value": "39.25"}, {"count": 1, "reported_value": "39.81"}, {"count": 1, "reported_value": "39.83"}, {"count": 22, "reported_value": "4.0"}, {"count": 1, "reported_value": "4.07"}, {"count": 3, "reported_value": "4.17"}, {"count": 1, "reported_value": "4.2"}, {"count": 1, "reported_value": "4.47"}, {"count": 1, "reported_value": "4.57"}, {"count": 1, "reported_value": "4.7"}, {"count": 1, "reported_value": "4.79"}, {"count": 1, "reported_value": "4.9"}, {"count": 1, "reported_value": "40.0"}, {"count": 1, "reported_value": "40.4"}, {"count": 1, "reported_value": "40.5"}, {"count": 1, "reported_value": "40.74"}, {"count": 5, "reported_value": "41.0"}, {"count": 2, "reported_value": "41.69"}, {"count": 5, "reported_value": "42.0"}, {"count": 2, "reported_value": "42.66"}, {"count": 2, "reported_value": "43.0"}, {"count": 1, "reported_value": "43.5"}, {"count": 2, "reported_value": "43.65"}, {"count": 2, "reported_value": "44.0"}, {"count": 1, "reported_value": "44.67"}, {"count": 4, "reported_value": "45.0"}, {"count": 1, "reported_value": "45.71"}, {"count": 2, "reported_value": "46.0"}, {"count": 2, "reported_value": "46.77"}, {"count": 1, "reported_value": "47.0"}, {"count": 2, "reported_value": "48.0"}, {"count": 1, "reported_value": "48.67"}, {"count": 2, "reported_value": "48.98"}, {"count": 2, "reported_value": "49.0"}, {"count": 22, "reported_value": "5.0"}, {"count": 2, "reported_value": "5.13"}, {"count": 3, "reported_value": "5.25"}, {"count": 2, "reported_value": "5.37"}, {"count": 5, "reported_value": "5.5"}, {"count": 1, "reported_value": "5.6"}, {"count": 3, "reported_value": "5.75"}, {"count": 2, "reported_value": "50.0"}, {"count": 2, "reported_value": "50.12"}, {"count": 1, "reported_value": "50.5"}, {"count": 1, "reported_value": "51.0"}, {"count": 3, "reported_value": "51.29"}, {"count": 1, "reported_value": "52.48"}, {"count": 2, "reported_value": "53.0"}, {"count": 1, "reported_value": "53.7"}, {"count": 1, "reported_value": "54.0"}, {"count": 1, "reported_value": "54.5"}, {"count": 2, "reported_value": "54.95"}, {"count": 4, "reported_value": "56.0"}, {"count": 2, "reported_value": "56.23"}, {"count": 1, "reported_value": "57.54"}, {"count": 2, "reported_value": "58.0"}, {"count": 1, "reported_value": "58.5"}, {"count": 3, "reported_value": "59.0"}, {"count": 23, "reported_value": "6.0"}, {"count": 1, "reported_value": "6.03"}, {"count": 2, "reported_value": "6.17"}, {"count": 1, "reported_value": "6.18"}, {"count": 4, "reported_value": "6.31"}, {"count": 1, "reported_value": "6.33"}, {"count": 1, "reported_value": "6.46"}, {"count": 1, "reported_value": "6.5"}, {"count": 1, "reported_value": "6.61"}, {"count": 1, "reported_value": "6.67"}, {"count": 1, "reported_value": "6.76"}, {"count": 3, "reported_value": "6.92"}, {"count": 2, "reported_value": "60.0"}, {"count": 3, "reported_value": "60.26"}, {"count": 1, "reported_value": "61.0"}, {"count": 1, "reported_value": "61.66"}, {"count": 3, "reported_value": "62.0"}, {"count": 2, "reported_value": "63.0"}, {"count": 1, "reported_value": "63.1"}, {"count": 2, "reported_value": "64.0"}, {"count": 1, "reported_value": "64.57"}, {"count": 7, "reported_value": "66.0"}, {"count": 3, "reported_value": "66.07"}, {"count": 1, "reported_value": "66.5"}, {"count": 2, "reported_value": "67.61"}, {"count": 2, "reported_value": "68.0"}, {"count": 1, "reported_value": "69.0"}, {"count": 19, "reported_value": "7.0"}, {"count": 1, "reported_value": "7.08"}, {"count": 1, "reported_value": "7.24"}, {"count": 3, "reported_value": "7.41"}, {"count": 3, "reported_value": "7.5"}, {"count": 2, "reported_value": "7.59"}, {"count": 2, "reported_value": "7.76"}, {"count": 2, "reported_value": "7.94"}, {"count": 1, "reported_value": "70.0"}, {"count": 2, "reported_value": "70.79"}, {"count": 1, "reported_value": "71.0"}, {"count": 1, "reported_value": "71.25"}, {"count": 3, "reported_value": "72.0"}, {"count": 1, "reported_value": "73.0"}, {"count": 2, "reported_value": "74.0"}, {"count": 4, "reported_value": "75.0"}, {"count": 1, "reported_value": "75.86"}, {"count": 1, "reported_value": "76.0"}, {"count": 1, "reported_value": "77.62"}, {"count": 2, "reported_value": "79.0"}, {"count": 2, "reported_value": "79.43"}, {"count": 1, "reported_value": "79.5"}, {"count": 13, "reported_value": "8.0"}, {"count": 1, "reported_value": "8.13"}, {"count": 1, "reported_value": "8.28"}, {"count": 2, "reported_value": "8.32"}, {"count": 1, "reported_value": "8.33"}, {"count": 3, "reported_value": "8.5"}, {"count": 1, "reported_value": "8.51"}, {"count": 1, "reported_value": "8.67"}, {"count": 2, "reported_value": "8.71"}, {"count": 1, "reported_value": "8.86"}, {"count": 2, "reported_value": "8.91"}, {"count": 1, "reported_value": "81.0"}, {"count": 2, "reported_value": "82.0"}, {"count": 1, "reported_value": "83.0"}, {"count": 1, "reported_value": "83.18"}, {"count": 1, "reported_value": "83.83"}, {"count": 2, "reported_value": "85.0"}, {"count": 1, "reported_value": "85.11"}, {"count": 2, "reported_value": "86.0"}, {"count": 2, "reported_value": "87.1"}, {"count": 1, "reported_value": "88.0"}, {"count": 1, "reported_value": "89.0"}, {"count": 1, "reported_value": "89.13"}, {"count": 16, "reported_value": "9.0"}, {"count": 2, "reported_value": "9.12"}, {"count": 1, "reported_value": "9.33"}, {"count": 1, "reported_value": "9.5"}, {"count": 1, "reported_value": "9.55"}, {"count": 3, "reported_value": "9.77"}, {"count": 1, "reported_value": "93.33"}, {"count": 2, "reported_value": "94.0"}, {"count": 3, "reported_value": "95.5"}, {"count": 1, "reported_value": "96.0"}, {"count": 2, "reported_value": "97.72"}, {"count": 2, "reported_value": "99.0"}]}`.

OBSERVED: CHEMBL3301371 censored/other reported boundaries: `{"<": [{"count": 115, "reported_value": "3.0"}], ">": [{"count": 127, "reported_value": "150.0"}], "UNKNOWN": [{"count": 8, "reported_value": "10.0"}, {"count": 1, "reported_value": "10.2"}, {"count": 3, "reported_value": "10.23"}, {"count": 3, "reported_value": "10.47"}, {"count": 1, "reported_value": "10.63"}, {"count": 1, "reported_value": "10.72"}, {"count": 1, "reported_value": "10.8"}, {"count": 1, "reported_value": "10.96"}, {"count": 1, "reported_value": "100.0"}, {"count": 1, "reported_value": "101.0"}, {"count": 2, "reported_value": "102.33"}, {"count": 1, "reported_value": "103.2"}, {"count": 3, "reported_value": "104.71"}, {"count": 1, "reported_value": "105.0"}, {"count": 2, "reported_value": "107.0"}, {"count": 3, "reported_value": "107.15"}, {"count": 3, "reported_value": "108.0"}, {"count": 2, "reported_value": "109.65"}, {"count": 3, "reported_value": "11.0"}, {"count": 3, "reported_value": "11.48"}, {"count": 1, "reported_value": "11.75"}, {"count": 1, "reported_value": "110.0"}, {"count": 1, "reported_value": "111.0"}, {"count": 1, "reported_value": "112.2"}, {"count": 1, "reported_value": "113.0"}, {"count": 1, "reported_value": "114.0"}, {"count": 1, "reported_value": "114.82"}, {"count": 3, "reported_value": "117.49"}, {"count": 1, "reported_value": "118.0"}, {"count": 1, "reported_value": "119.0"}, {"count": 8, "reported_value": "12.0"}, {"count": 4, "reported_value": "12.02"}, {"count": 1, "reported_value": "12.15"}, {"count": 5, "reported_value": "12.3"}, {"count": 1, "reported_value": "12.5"}, {"count": 2, "reported_value": "12.59"}, {"count": 1, "reported_value": "12.73"}, {"count": 4, "reported_value": "12.88"}, {"count": 2, "reported_value": "120.23"}, {"count": 1, "reported_value": "121.0"}, {"count": 3, "reported_value": "123.03"}, {"count": 1, "reported_value": "125.89"}, {"count": 1, "reported_value": "128.0"}, {"count": 2, "reported_value": "128.82"}, {"count": 1, "reported_value": "129.0"}, {"count": 5, "reported_value": "13.0"}, {"count": 3, "reported_value": "13.18"}, {"count": 3, "reported_value": "13.49"}, {"count": 1, "reported_value": "13.78"}, {"count": 2, "reported_value": "13.8"}, {"count": 2, "reported_value": "130.0"}, {"count": 2, "reported_value": "135.0"}, {"count": 1, "reported_value": "136.0"}, {"count": 1, "reported_value": "137.0"}, {"count": 4, "reported_value": "138.04"}, {"count": 1, "reported_value": "139.0"}, {"count": 3, "reported_value": "14.0"}, {"count": 2, "reported_value": "14.13"}, {"count": 1, "reported_value": "14.24"}, {"count": 1, "reported_value": "14.3"}, {"count": 2, "reported_value": "14.45"}, {"count": 2, "reported_value": "14.79"}, {"count": 1, "reported_value": "140.0"}, {"count": 1, "reported_value": "141.0"}, {"count": 1, "reported_value": "141.25"}, {"count": 1, "reported_value": "142.0"}, {"count": 2, "reported_value": "144.0"}, {"count": 3, "reported_value": "144.54"}, {"count": 3, "reported_value": "147.91"}, {"count": 1, "reported_value": "149.0"}, {"count": 5, "reported_value": "15.0"}, {"count": 1, "reported_value": "15.14"}, {"count": 1, "reported_value": "15.3"}, {"count": 1, "reported_value": "15.85"}, {"count": 4, "reported_value": "16.0"}, {"count": 2, "reported_value": "16.22"}, {"count": 1, "reported_value": "16.25"}, {"count": 3, "reported_value": "16.6"}, {"count": 3, "reported_value": "16.98"}, {"count": 4, "reported_value": "17.0"}, {"count": 1, "reported_value": "17.16"}, {"count": 1, "reported_value": "17.32"}, {"count": 4, "reported_value": "17.38"}, {"count": 3, "reported_value": "18.0"}, {"count": 2, "reported_value": "18.2"}, {"count": 1, "reported_value": "18.62"}, {"count": 1, "reported_value": "18.84"}, {"count": 1, "reported_value": "18.89"}, {"count": 4, "reported_value": "19.0"}, {"count": 3, "reported_value": "19.05"}, {"count": 1, "reported_value": "19.44"}, {"count": 3, "reported_value": "19.5"}, {"count": 1, "reported_value": "19.6"}, {"count": 5, "reported_value": "19.95"}, {"count": 5, "reported_value": "20.0"}, {"count": 3, "reported_value": "20.42"}, {"count": 2, "reported_value": "20.89"}, {"count": 4, "reported_value": "21.0"}, {"count": 1, "reported_value": "21.3"}, {"count": 1, "reported_value": "21.38"}, {"count": 1, "reported_value": "21.47"}, {"count": 3, "reported_value": "21.88"}, {"count": 2, "reported_value": "22.0"}, {"count": 1, "reported_value": "22.39"}, {"count": 1, "reported_value": "22.77"}, {"count": 1, "reported_value": "22.91"}, {"count": 2, "reported_value": "23.0"}, {"count": 2, "reported_value": "23.44"}, {"count": 5, "reported_value": "23.99"}, {"count": 1, "reported_value": "24.0"}, {"count": 2, "reported_value": "24.55"}, {"count": 1, "reported_value": "25.0"}, {"count": 2, "reported_value": "25.12"}, {"count": 1, "reported_value": "25.33"}, {"count": 3, "reported_value": "25.7"}, {"count": 3, "reported_value": "26.0"}, {"count": 1, "reported_value": "26.3"}, {"count": 5, "reported_value": "26.92"}, {"count": 1, "reported_value": "26.98"}, {"count": 3, "reported_value": "27.0"}, {"count": 1, "reported_value": "27.54"}, {"count": 4, "reported_value": "28.0"}, {"count": 3, "reported_value": "28.18"}, {"count": 6, "reported_value": "29.0"}, {"count": 3, "reported_value": "29.51"}, {"count": 2, "reported_value": "3.0"}, {"count": 1, "reported_value": "3.09"}, {"count": 1, "reported_value": "3.16"}, {"count": 1, "reported_value": "3.24"}, {"count": 1, "reported_value": "3.31"}, {"count": 3, "reported_value": "3.39"}, {"count": 1, "reported_value": "3.63"}, {"count": 1, "reported_value": "3.8"}, {"count": 1, "reported_value": "3.87"}, {"count": 1, "reported_value": "30.0"}, {"count": 2, "reported_value": "30.2"}, {"count": 1, "reported_value": "30.51"}, {"count": 1, "reported_value": "30.72"}, {"count": 2, "reported_value": "30.9"}, {"count": 3, "reported_value": "31.0"}, {"count": 2, "reported_value": "31.62"}, {"count": 1, "reported_value": "32.36"}, {"count": 2, "reported_value": "33.0"}, {"count": 1, "reported_value": "33.11"}, {"count": 2, "reported_value": "33.88"}, {"count": 1, "reported_value": "34.0"}, {"count": 1, "reported_value": "34.5"}, {"count": 1, "reported_value": "35.0"}, {"count": 5, "reported_value": "35.48"}, {"count": 1, "reported_value": "36.08"}, {"count": 3, "reported_value": "36.31"}, {"count": 1, "reported_value": "37.0"}, {"count": 3, "reported_value": "38.0"}, {"count": 2, "reported_value": "38.02"}, {"count": 1, "reported_value": "38.9"}, {"count": 2, "reported_value": "39.0"}, {"count": 2, "reported_value": "39.81"}, {"count": 7, "reported_value": "4.0"}, {"count": 2, "reported_value": "4.17"}, {"count": 1, "reported_value": "4.24"}, {"count": 1, "reported_value": "4.37"}, {"count": 1, "reported_value": "4.68"}, {"count": 3, "reported_value": "4.79"}, {"count": 1, "reported_value": "40.0"}, {"count": 3, "reported_value": "40.74"}, {"count": 1, "reported_value": "41.0"}, {"count": 1, "reported_value": "41.35"}, {"count": 1, "reported_value": "41.41"}, {"count": 2, "reported_value": "42.0"}, {"count": 5, "reported_value": "42.66"}, {"count": 3, "reported_value": "43.0"}, {"count": 1, "reported_value": "43.36"}, {"count": 1, "reported_value": "43.43"}, {"count": 1, "reported_value": "43.65"}, {"count": 3, "reported_value": "44.67"}, {"count": 2, "reported_value": "45.71"}, {"count": 3, "reported_value": "46.0"}, {"count": 1, "reported_value": "46.28"}, {"count": 1, "reported_value": "46.77"}, {"count": 1, "reported_value": "47.0"}, {"count": 1, "reported_value": "47.91"}, {"count": 1, "reported_value": "48.44"}, {"count": 1, "reported_value": "48.98"}, {"count": 7, "reported_value": "5.0"}, {"count": 2, "reported_value": "5.01"}, {"count": 4, "reported_value": "5.13"}, {"count": 2, "reported_value": "5.25"}, {"count": 1, "reported_value": "5.29"}, {"count": 1, "reported_value": "5.37"}, {"count": 2, "reported_value": "5.5"}, {"count": 1, "reported_value": "5.75"}, {"count": 1, "reported_value": "5.79"}, {"count": 1, "reported_value": "50.0"}, {"count": 3, "reported_value": "50.12"}, {"count": 1, "reported_value": "50.96"}, {"count": 2, "reported_value": "51.0"}, {"count": 2, "reported_value": "51.29"}, {"count": 2, "reported_value": "52.0"}, {"count": 5, "reported_value": "52.48"}, {"count": 2, "reported_value": "53.0"}, {"count": 3, "reported_value": "53.7"}, {"count": 1, "reported_value": "54.0"}, {"count": 3, "reported_value": "54.95"}, {"count": 1, "reported_value": "55.0"}, {"count": 2, "reported_value": "56.0"}, {"count": 2, "reported_value": "56.23"}, {"count": 1, "reported_value": "57.0"}, {"count": 1, "reported_value": "57.54"}, {"count": 1, "reported_value": "58.0"}, {"count": 1, "reported_value": "58.88"}, {"count": 1, "reported_value": "59.0"}, {"count": 1, "reported_value": "59.87"}, {"count": 8, "reported_value": "6.0"}, {"count": 3, "reported_value": "6.17"}, {"count": 3, "reported_value": "6.31"}, {"count": 2, "reported_value": "6.61"}, {"count": 2, "reported_value": "6.76"}, {"count": 2, "reported_value": "6.92"}, {"count": 2, "reported_value": "60.0"}, {"count": 2, "reported_value": "61.0"}, {"count": 2, "reported_value": "61.66"}, {"count": 2, "reported_value": "63.1"}, {"count": 3, "reported_value": "64.0"}, {"count": 1, "reported_value": "64.34"}, {"count": 4, "reported_value": "64.57"}, {"count": 2, "reported_value": "65.0"}, {"count": 3, "reported_value": "66.0"}, {"count": 2, "reported_value": "66.07"}, {"count": 1, "reported_value": "67.0"}, {"count": 1, "reported_value": "67.61"}, {"count": 1, "reported_value": "69.0"}, {"count": 6, "reported_value": "69.18"}, {"count": 6, "reported_value": "7.0"}, {"count": 1, "reported_value": "7.08"}, {"count": 1, "reported_value": "7.11"}, {"count": 1, "reported_value": "7.2"}, {"count": 1, "reported_value": "7.24"}, {"count": 1, "reported_value": "7.33"}, {"count": 1, "reported_value": "7.48"}, {"count": 1, "reported_value": "7.59"}, {"count": 2, "reported_value": "7.94"}, {"count": 1, "reported_value": "70.0"}, {"count": 3, "reported_value": "70.79"}, {"count": 1, "reported_value": "71.99"}, {"count": 6, "reported_value": "72.44"}, {"count": 1, "reported_value": "73.0"}, {"count": 1, "reported_value": "74.0"}, {"count": 4, "reported_value": "74.13"}, {"count": 1, "reported_value": "75.0"}, {"count": 2, "reported_value": "75.86"}, {"count": 1, "reported_value": "75.93"}, {"count": 1, "reported_value": "76.0"}, {"count": 2, "reported_value": "77.0"}, {"count": 1, "reported_value": "78.0"}, {"count": 1, "reported_value": "79.43"}, {"count": 1, "reported_value": "79.99"}, {"count": 9, "reported_value": "8.0"}, {"count": 2, "reported_value": "8.13"}, {"count": 2, "reported_value": "8.51"}, {"count": 2, "reported_value": "8.71"}, {"count": 1, "reported_value": "8.91"}, {"count": 1, "reported_value": "80.0"}, {"count": 2, "reported_value": "81.0"}, {"count": 1, "reported_value": "82.0"}, {"count": 2, "reported_value": "83.18"}, {"count": 1, "reported_value": "84.0"}, {"count": 3, "reported_value": "85.0"}, {"count": 1, "reported_value": "85.11"}, {"count": 1, "reported_value": "87.0"}, {"count": 4, "reported_value": "87.1"}, {"count": 1, "reported_value": "88.0"}, {"count": 4, "reported_value": "89.13"}, {"count": 5, "reported_value": "9.0"}, {"count": 1, "reported_value": "9.01"}, {"count": 2, "reported_value": "9.12"}, {"count": 1, "reported_value": "9.33"}, {"count": 2, "reported_value": "9.55"}, {"count": 4, "reported_value": "9.77"}, {"count": 1, "reported_value": "9.8"}, {"count": 1, "reported_value": "9.88"}, {"count": 1, "reported_value": "9.9"}, {"count": 1, "reported_value": "9.95"}, {"count": 5, "reported_value": "91.0"}, {"count": 3, "reported_value": "91.2"}, {"count": 1, "reported_value": "93.03"}, {"count": 1, "reported_value": "93.33"}, {"count": 1, "reported_value": "95.5"}, {"count": 1, "reported_value": "97.72"}, {"count": 1, "reported_value": "98.0"}, {"count": 1, "reported_value": "99.0"}]}`.

OBSERVED: CHEMBL3301372 censored/other reported boundaries: `{"<": [{"count": 104, "reported_value": "3.0"}], ">": [{"count": 15, "reported_value": "150.0"}], "UNKNOWN": [{"count": 3, "reported_value": "10.0"}, {"count": 2, "reported_value": "10.23"}, {"count": 2, "reported_value": "10.47"}, {"count": 5, "reported_value": "10.72"}, {"count": 2, "reported_value": "10.96"}, {"count": 1, "reported_value": "102.33"}, {"count": 1, "reported_value": "11.48"}, {"count": 2, "reported_value": "12.02"}, {"count": 2, "reported_value": "12.3"}, {"count": 2, "reported_value": "12.59"}, {"count": 2, "reported_value": "12.88"}, {"count": 1, "reported_value": "123.03"}, {"count": 1, "reported_value": "125.0"}, {"count": 1, "reported_value": "125.89"}, {"count": 1, "reported_value": "128.82"}, {"count": 2, "reported_value": "13.18"}, {"count": 3, "reported_value": "13.49"}, {"count": 1, "reported_value": "13.5"}, {"count": 5, "reported_value": "13.8"}, {"count": 1, "reported_value": "134.9"}, {"count": 1, "reported_value": "14.0"}, {"count": 3, "reported_value": "14.45"}, {"count": 1, "reported_value": "14.5"}, {"count": 1, "reported_value": "14.78"}, {"count": 3, "reported_value": "14.79"}, {"count": 2, "reported_value": "15.14"}, {"count": 6, "reported_value": "15.49"}, {"count": 1, "reported_value": "16.0"}, {"count": 2, "reported_value": "16.22"}, {"count": 2, "reported_value": "16.6"}, {"count": 1, "reported_value": "16.98"}, {"count": 4, "reported_value": "17.38"}, {"count": 3, "reported_value": "17.78"}, {"count": 3, "reported_value": "18.2"}, {"count": 2, "reported_value": "18.62"}, {"count": 3, "reported_value": "19.05"}, {"count": 1, "reported_value": "19.45"}, {"count": 2, "reported_value": "19.5"}, {"count": 1, "reported_value": "19.91"}, {"count": 2, "reported_value": "19.95"}, {"count": 1, "reported_value": "20.0"}, {"count": 1, "reported_value": "20.05"}, {"count": 1, "reported_value": "20.42"}, {"count": 2, "reported_value": "21.38"}, {"count": 1, "reported_value": "21.88"}, {"count": 1, "reported_value": "21.9"}, {"count": 2, "reported_value": "22.39"}, {"count": 1, "reported_value": "22.91"}, {"count": 1, "reported_value": "23.2"}, {"count": 1, "reported_value": "23.22"}, {"count": 1, "reported_value": "23.44"}, {"count": 1, "reported_value": "23.99"}, {"count": 3, "reported_value": "24.55"}, {"count": 3, "reported_value": "25.12"}, {"count": 2, "reported_value": "25.7"}, {"count": 1, "reported_value": "25.92"}, {"count": 2, "reported_value": "26.3"}, {"count": 1, "reported_value": "26.41"}, {"count": 2, "reported_value": "26.92"}, {"count": 1, "reported_value": "27.3"}, {"count": 3, "reported_value": "27.54"}, {"count": 2, "reported_value": "28.18"}, {"count": 1, "reported_value": "28.84"}, {"count": 2, "reported_value": "29.51"}, {"count": 1, "reported_value": "3.2"}, {"count": 1, "reported_value": "3.24"}, {"count": 1, "reported_value": "3.3"}, {"count": 3, "reported_value": "3.31"}, {"count": 1, "reported_value": "3.39"}, {"count": 1, "reported_value": "3.4"}, {"count": 1, "reported_value": "3.46"}, {"count": 2, "reported_value": "3.47"}, {"count": 1, "reported_value": "3.55"}, {"count": 3, "reported_value": "3.72"}, {"count": 1, "reported_value": "3.8"}, {"count": 1, "reported_value": "3.81"}, {"count": 1, "reported_value": "3.89"}, {"count": 1, "reported_value": "3.91"}, {"count": 3, "reported_value": "3.98"}, {"count": 1, "reported_value": "30.12"}, {"count": 2, "reported_value": "30.2"}, {"count": 2, "reported_value": "30.9"}, {"count": 1, "reported_value": "32.0"}, {"count": 3, "reported_value": "32.36"}, {"count": 1, "reported_value": "33.88"}, {"count": 2, "reported_value": "34.67"}, {"count": 2, "reported_value": "35.48"}, {"count": 1, "reported_value": "36.31"}, {"count": 1, "reported_value": "37.0"}, {"count": 3, "reported_value": "38.02"}, {"count": 3, "reported_value": "38.9"}, {"count": 2, "reported_value": "39.81"}, {"count": 1, "reported_value": "4.04"}, {"count": 1, "reported_value": "4.17"}, {"count": 2, "reported_value": "4.27"}, {"count": 1, "reported_value": "4.46"}, {"count": 2, "reported_value": "4.47"}, {"count": 3, "reported_value": "4.57"}, {"count": 2, "reported_value": "4.68"}, {"count": 1, "reported_value": "4.7"}, {"count": 1, "reported_value": "4.76"}, {"count": 3, "reported_value": "4.79"}, {"count": 1, "reported_value": "4.88"}, {"count": 2, "reported_value": "4.9"}, {"count": 1, "reported_value": "4.92"}, {"count": 1, "reported_value": "40.0"}, {"count": 1, "reported_value": "40.74"}, {"count": 1, "reported_value": "41.69"}, {"count": 1, "reported_value": "42.5"}, {"count": 2, "reported_value": "42.66"}, {"count": 1, "reported_value": "43.65"}, {"count": 1, "reported_value": "44.0"}, {"count": 1, "reported_value": "45.71"}, {"count": 1, "reported_value": "46.77"}, {"count": 1, "reported_value": "5.01"}, {"count": 1, "reported_value": "5.05"}, {"count": 1, "reported_value": "5.13"}, {"count": 1, "reported_value": "5.16"}, {"count": 1, "reported_value": "5.17"}, {"count": 3, "reported_value": "5.25"}, {"count": 2, "reported_value": "5.37"}, {"count": 1, "reported_value": "5.5"}, {"count": 2, "reported_value": "5.62"}, {"count": 3, "reported_value": "5.75"}, {"count": 1, "reported_value": "5.88"}, {"count": 2, "reported_value": "50.12"}, {"count": 2, "reported_value": "51.29"}, {"count": 1, "reported_value": "52.48"}, {"count": 4, "reported_value": "54.95"}, {"count": 1, "reported_value": "56.23"}, {"count": 1, "reported_value": "57.11"}, {"count": 3, "reported_value": "6.0"}, {"count": 2, "reported_value": "6.17"}, {"count": 3, "reported_value": "6.31"}, {"count": 2, "reported_value": "6.46"}, {"count": 2, "reported_value": "6.61"}, {"count": 2, "reported_value": "6.76"}, {"count": 2, "reported_value": "6.92"}, {"count": 1, "reported_value": "6.99"}, {"count": 2, "reported_value": "60.26"}, {"count": 1, "reported_value": "61.66"}, {"count": 1, "reported_value": "64.0"}, {"count": 1, "reported_value": "64.57"}, {"count": 1, "reported_value": "66.07"}, {"count": 1, "reported_value": "67.61"}, {"count": 1, "reported_value": "7.0"}, {"count": 2, "reported_value": "7.08"}, {"count": 1, "reported_value": "7.24"}, {"count": 2, "reported_value": "7.41"}, {"count": 3, "reported_value": "7.59"}, {"count": 3, "reported_value": "7.76"}, {"count": 1, "reported_value": "7.9"}, {"count": 2, "reported_value": "7.94"}, {"count": 1, "reported_value": "74.13"}, {"count": 1, "reported_value": "77.62"}, {"count": 1, "reported_value": "8.13"}, {"count": 3, "reported_value": "8.51"}, {"count": 1, "reported_value": "8.7"}, {"count": 2, "reported_value": "8.71"}, {"count": 1, "reported_value": "8.91"}, {"count": 1, "reported_value": "83.18"}, {"count": 2, "reported_value": "87.1"}, {"count": 4, "reported_value": "9.12"}, {"count": 2, "reported_value": "9.33"}, {"count": 1, "reported_value": "9.5"}, {"count": 2, "reported_value": "9.77"}, {"count": 2, "reported_value": "95.5"}]}`.

### Null-relation records at numeric boundaries

| Assay | Null relation at 3 | Null relation at 150 |
|---|---:|---:|
| CHEMBL3301370 | 13 | 0 |
| CHEMBL3301371 | 2 | 0 |
| CHEMBL3301372 | 0 | 0 |

OBSERVED: Rat-assay null-relation records at 3: activity 14768823, CHEMBL589973, value 3.0; activity 14768825, CHEMBL364714, value 3.0. These remain UNKNOWN; boundary equality does not assign a censor relation.


## TDC target audit

OBSERVED: Raw columns are ID, X, Y; Drug_ID in the requested audit means ID, raw SMILES means X. Both tables were downloaded directly using the verified PyTDC 1.1.15 source registry. PyTDC itself was not installed or invoked.

OBSERVED: The [TDC public documentation](https://tdcommons.ai/single_pred_tasks/adme/#clearance-astrazeneca), accessed 2026-09-16, reports 1,020 hepatocyte drugs. The downloaded table has 1,213 rows and 1,020 unique IDs/structures. These are distinct denominators; no raw deduplication was applied.

OBSERVED: The preserved PyTDC 1.1.15 loader source uses raw X/Y/ID and filters null targets. This audit reads the raw table directly, retaining even missing-target rows. Both acquired TDC tables have no missing targets.

### Clearance_Microsome_AZ

OBSERVED:
```json
{
  "total_rows": 1102,
  "numeric_rows": 1102,
  "missing_rows": 0,
  "unparseable_rows": 0,
  "exactly_3": 287,
  "exactly_150": 84,
  "inequality_strings": 0,
  "top_value_frequencies": [
    {
      "value": "3.0",
      "count": 287
    },
    {
      "value": "150.0",
      "count": 84
    },
    {
      "value": "6.0",
      "count": 23
    },
    {
      "value": "4.0",
      "count": 22
    },
    {
      "value": "5.0",
      "count": 22
    },
    {
      "value": "7.0",
      "count": 19
    },
    {
      "value": "11.0",
      "count": 17
    },
    {
      "value": "9.0",
      "count": 16
    },
    {
      "value": "8.0",
      "count": 13
    },
    {
      "value": "12.0",
      "count": 13
    }
  ],
  "min": 3.0,
  "q05": 3.0,
  "q25": 3.0,
  "median": 12.735,
  "q75": 42.66,
  "q95": 150.0,
  "max": 150.0,
  "iqr": 39.66,
  "mad": 9.735
}
```

### Clearance_Hepatocyte_AZ

OBSERVED:
```json
{
  "total_rows": 1213,
  "numeric_rows": 1213,
  "missing_rows": 0,
  "unparseable_rows": 0,
  "exactly_3": 195,
  "exactly_150": 137,
  "inequality_strings": 0,
  "top_value_frequencies": [
    {
      "value": "3.0",
      "count": 195
    },
    {
      "value": "150.0",
      "count": 137
    },
    {
      "value": "10.0",
      "count": 11
    },
    {
      "value": "6.0",
      "count": 10
    },
    {
      "value": "8.0",
      "count": 9
    },
    {
      "value": "12.0",
      "count": 8
    },
    {
      "value": "17.38",
      "count": 8
    },
    {
      "value": "4.0",
      "count": 7
    },
    {
      "value": "5.0",
      "count": 7
    },
    {
      "value": "7.0",
      "count": 7
    }
  ],
  "min": 3.0,
  "q05": 3.0,
  "q25": 6.0,
  "median": 19.0,
  "q75": 64.0,
  "q95": 150.0,
  "max": 150.0,
  "iqr": 58.0,
  "mad": 16.0
}
```

## Species and microsome reconciliation

# TDC hepatocyte summary

```json
{
  "INFERRED": {
    "claim_status": "REPRODUCED",
    "decision_rule": "REPRODUCED requires both rat-only and human-only structure matches with exactly matching numeric source labels. PARTIALLY_REPRODUCED requires label-specific matches to both species without both exclusive structural witnesses; otherwise NOT_REPRODUCED. Censored matches identify numeric boundaries only.",
    "strict_duplicate_pair_rule": "Exactly two TDC rows with different numeric labels: one has exactly one strict structure/value-matching rat record and no human value match; the other has exactly one strict structure/value-matching human record and no rat value match. Numeric agreement uses exact Decimal equality."
  },
  "OBSERVED": {
    "duplicate_label_groups": {
      "different": 193
    },
    "duplicate_trace_groups": {
      "distinct_labels_match_rat_and_human": 187,
      "no_strict_structural_match_to_either_assay": 6
    },
    "numeric_label_match_row_counts": {
      "both": 31,
      "human_only": 370,
      "rat_only": 796,
      "unresolved": 16
    },
    "row_counts": {
      "ambiguous_unparseable": 0,
      "both": 405,
      "human_only": 183,
      "neither": 16,
      "rat_only": 609
    },
    "secondary_id_duplicate_trace_groups": {
      "distinct_labels_match_rat_and_human": 190,
      "partial_or_unresolved": 3
    },
    "secondary_id_numeric_label_match_row_counts": {
      "both": 31,
      "human_only": 373,
      "rat_only": 801,
      "unresolved": 8
    },
    "unique_valid_structure_counts": {
      "ambiguous_unparseable": 0,
      "both": 218,
      "human_only": 183,
      "neither": 10,
      "rat_only": 609
    }
  },
  "UNRESOLVED": "Historical lineage cannot be proven by equality alone. A shared structure/label can map to both species; retain ambiguity. Species uses ChEMBL assay organism/taxonomy, never target magnitude. Secondary exact molecule-ID plus numeric-value matching is explicitly separate and never upgrades the strict structural matches."
}
```

OBSERVED: The six non-strict hepatocyte duplicate groups have no strict structural match to either source assay under the frozen identity rule; all twelve rows are classified as neither. They are not groups with ambiguous matching species evidence.

# TDC microsome summary

```json
{
  "INFERRED": "mL/min/g and microL/min/mg are dimensionally and numerically equivalent (unit conversion in numerator and denominator cancels). Exact numeric matches require no target transformation; retained boundary numbers without inequality strings indicate censor information is absent from the TDC table. This is not physiological scaling.",
  "OBSERVED": {
    "chembl_only_structures": 5,
    "chembl_original_units": {
      "microL/min/mg": 1102
    },
    "chembl_standard_units": {
      "mL.min-1.g-1": 1102
    },
    "chembl_unmatched_rows": 5,
    "original_to_standard_numeric_equal_rows": 1102,
    "qualifier_reconciliation_candidate_pairs": {
      "<": {
        "candidate_pairs": 274,
        "numeric_equal_pairs": 274,
        "tdc_inequality_present_pairs": 0
      },
      ">": {
        "candidate_pairs": 84,
        "numeric_equal_pairs": 84,
        "tdc_inequality_present_pairs": 0
      },
      "UNKNOWN": {
        "candidate_pairs": 739,
        "numeric_equal_pairs": 739,
        "tdc_inequality_present_pairs": 0
      }
    },
    "structure_overlap": 1097,
    "tdc_only_structures": 5,
    "tdc_raw_unit_column": null,
    "tdc_rows_structure_matched_without_numeric_match": 0,
    "tdc_rows_with_exact_numeric_match": 1097,
    "tdc_rows_with_multiple_candidates": 0,
    "tdc_unmatched_rows": 5
  },
  "UNRESOLVED": "The TDC table has no units or censoring field. Numeric agreement supports, but cannot independently establish, source lineage or unit annotation. No claim about undocumented historical processing is made.",
  "secondary_id_audit": {
    "INFERRED": "ID and declared parent-ID evidence can explain representation discrepancies but does not establish strict structure equality. No fragments or tautomers were transformed.",
    "OBSERVED": {
      "exact_id_overlap": 1101,
      "strict_structure_unmatched_details": [
        {
          "chembl_declared_parent_id_candidates": [
            {
              "activity_id": 14765481,
              "canonical_smiles_rdkit": "O=c1[nH]c2c(O)ccc(CCNCCS(=O)(=O)CCCOCCc3ccccc3)c2s1",
              "identifier": "CHEMBL82663",
              "numeric_equal": true,
              "parent_molecule_chembl_id": "CHEMBL82663",
              "raw_filename": "data/raw/chembl/CHEMBL3301370_activities_00000.json",
              "source": "CHEMBL3301370",
              "source_row_1based": 894,
              "standard_relation": null,
              "standard_units": "mL.min-1.g-1",
              "target": "111.0"
            }
          ],
          "exact_id_candidates": [
            {
              "activity_id": 14765481,
              "canonical_smiles_rdkit": "O=c1[nH]c2c(O)ccc(CCNCCS(=O)(=O)CCCOCCc3ccccc3)c2s1",
              "identifier": "CHEMBL82663",
              "numeric_equal": true,
              "raw_filename": "data/raw/chembl/CHEMBL3301370_activities_00000.json",
              "source": "CHEMBL3301370",
              "source_row_1based": 894,
              "standard_relation": null,
              "standard_units": "mL.min-1.g-1",
              "target": "111.0"
            }
          ],
          "tdc_canonical_smiles_rdkit": "O=S(=O)(CCCOCCc1ccccc1)CCNCCc1ccc(O)c2nc(O)sc12",
          "tdc_id": "CHEMBL82663",
          "tdc_value": "111.0"
        },
        {
          "chembl_declared_parent_id_candidates": [
            {
              "activity_id": 14763462,
              "canonical_smiles_rdkit": "CCCSc1ccc2[nH]c(NC(=O)OC)nc2c1",
              "identifier": "CHEMBL1483",
              "numeric_equal": true,
              "parent_molecule_chembl_id": "CHEMBL1483",
              "raw_filename": "data/raw/chembl/CHEMBL3301370_activities_00000.json",
              "source": "CHEMBL3301370",
              "source_row_1based": 688,
              "standard_relation": null,
              "standard_units": "mL.min-1.g-1",
              "target": "34.67"
            }
          ],
          "exact_id_candidates": [
            {
              "activity_id": 14763462,
              "canonical_smiles_rdkit": "CCCSc1ccc2[nH]c(NC(=O)OC)nc2c1",
              "identifier": "CHEMBL1483",
              "numeric_equal": true,
              "raw_filename": "data/raw/chembl/CHEMBL3301370_activities_00000.json",
              "source": "CHEMBL3301370",
              "source_row_1based": 688,
              "standard_relation": null,
              "standard_units": "mL.min-1.g-1",
              "target": "34.67"
            }
          ],
          "tdc_canonical_smiles_rdkit": "CCCSc1ccc2nc(NC(=O)OC)[nH]c2c1",
          "tdc_id": "CHEMBL1483",
          "tdc_value": "34.67"
        },
        {
          "chembl_declared_parent_id_candidates": [
            {
              "activity_id": 14765433,
              "canonical_smiles_rdkit": "Cc1cnc(-c2cnc(NCCNc3ccc(C#N)cn3)nc2-c2ccc(Cl)cc2Cl)[nH]1",
              "identifier": "CHEMBL412142",
              "numeric_equal": true,
              "parent_molecule_chembl_id": "CHEMBL412142",
              "raw_filename": "data/raw/chembl/CHEMBL3301370_activities_00000.json",
              "source": "CHEMBL3301370",
              "source_row_1based": 874,
              "standard_relation": null,
              "standard_units": "mL.min-1.g-1",
              "target": "96.0"
            }
          ],
          "exact_id_candidates": [
            {
              "activity_id": 14765433,
              "canonical_smiles_rdkit": "Cc1cnc(-c2cnc(NCCNc3ccc(C#N)cn3)nc2-c2ccc(Cl)cc2Cl)[nH]1",
              "identifier": "CHEMBL412142",
              "numeric_equal": true,
              "raw_filename": "data/raw/chembl/CHEMBL3301370_activities_00000.json",
              "source": "CHEMBL3301370",
              "source_row_1based": 874,
              "standard_relation": null,
              "standard_units": "mL.min-1.g-1",
              "target": "96.0"
            }
          ],
          "tdc_canonical_smiles_rdkit": "Cc1c[nH]c(-c2cnc(NCCNc3ccc(C#N)cn3)nc2-c2ccc(Cl)cc2Cl)n1",
          "tdc_id": "CHEMBL412142",
          "tdc_value": "96.0"
        },
        {
          "chembl_declared_parent_id_candidates": [
            {
              "activity_id": 14762352,
              "canonical_smiles_rdkit": "CCCCC1=NC2(CCCC2)C(=O)N1Cc1ccc(-c2ccccc2-c2nnn[nH]2)cc1",
              "identifier": "CHEMBL1513",
              "numeric_equal": true,
              "parent_molecule_chembl_id": "CHEMBL1513",
              "raw_filename": "data/raw/chembl/CHEMBL3301370_activities_00000.json",
              "source": "CHEMBL3301370",
              "source_row_1based": 541,
              "standard_relation": null,
              "standard_units": "mL.min-1.g-1",
              "target": "17.78"
            }
          ],
          "exact_id_candidates": [
            {
              "activity_id": 14762352,
              "canonical_smiles_rdkit": "CCCCC1=NC2(CCCC2)C(=O)N1Cc1ccc(-c2ccccc2-c2nnn[nH]2)cc1",
              "identifier": "CHEMBL1513",
              "numeric_equal": true,
              "raw_filename": "data/raw/chembl/CHEMBL3301370_activities_00000.json",
              "source": "CHEMBL3301370",
              "source_row_1based": 541,
              "standard_relation": null,
              "standard_units": "mL.min-1.g-1",
              "target": "17.78"
            }
          ],
          "tdc_canonical_smiles_rdkit": "CCCCC1=NC2(CCCC2)C(=O)N1Cc1ccc(-c2ccccc2-c2nn[nH]n2)cc1",
          "tdc_id": "CHEMBL1513",
          "tdc_value": "17.78"
        },
        {
          "chembl_declared_parent_id_candidates": [
            {
              "activity_id": 14759791,
              "canonical_smiles_rdkit": "Cn1c(=O)c2nc[nH]c2n(C)c1=O.O",
              "identifier": "CHEMBL1355736",
              "numeric_equal": true,
              "parent_molecule_chembl_id": "CHEMBL190",
              "raw_filename": "data/raw/chembl/CHEMBL3301370_activities_00000.json",
              "source": "CHEMBL3301370",
              "source_row_1based": 238,
              "standard_relation": null,
              "standard_units": "mL.min-1.g-1",
              "target": "4.79"
            }
          ],
          "exact_id_candidates": [],
          "tdc_canonical_smiles_rdkit": "Cn1c(=O)c2nc[nH]c2n(C)c1=O",
          "tdc_id": "CHEMBL190",
          "tdc_value": "4.79"
        }
      ],
      "tdc_rows_with_exact_id_and_numeric_match": 1101
    }
  }
}
```

### Five strict microsome structure discrepancies

| TDC molecule ID | ChEMBL molecule ID | Representation discrepancy | Matching numeric value | Standard InChIKeys |
|---|---|---|---:|---|
| CHEMBL82663 | CHEMBL82663 | Hydroxythiazole / thiazolone tautomer spellings | 111.0 | Equal |
| CHEMBL1483 | CHEMBL1483 | Heterocyclic N-H tautomer spellings | 34.67 | Equal |
| CHEMBL412142 | CHEMBL412142 | Imidazole N-H tautomer spellings | 96.0 | Equal |
| CHEMBL1513 | CHEMBL1513 | Tetrazole N-H tautomer spellings | 17.78 | Equal |
| CHEMBL190 | CHEMBL1355736 (declared parent CHEMBL190) | Theophylline / hydrate with a disconnected O component | 4.79 | Different |

OBSERVED: The independent review confirmed matching molecule IDs, values and standard InChIKeys for the four tautomer cases. Standard InChIKey agreement is supporting evidence only; it does not replace the frozen canonical-SMILES identity rule. The hydrate pair has a matching value. All five remain strict mismatches; the strict match count remains 1,097. Full canonical strings and activity references are retained above and in the reconciliation CSV. See AUDIT_REVIEW.md for the preserved independent review.

## Paired human cohort

# Membership summary

```json
{
  "INFERRED": "This establishes membership only under two identity definitions. It does not establish matched experimental conditions or independent biological replicates.",
  "OBSERVED": {
    "canonical_structure_overlap_n": 187,
    "id_overlap_n": 187,
    "id_structure_disagreement_or_ambiguity": [],
    "shared_ids": [
      "CHEMBL1017",
      "CHEMBL1020",
      "CHEMBL103667",
      "CHEMBL1071",
      "CHEMBL108",
      "CHEMBL1088752",
      "CHEMBL1089518",
      "CHEMBL1091137",
      "CHEMBL11",
      "CHEMBL112",
      "CHEMBL114",
      "CHEMBL1144",
      "CHEMBL1164729",
      "CHEMBL1194325",
      "CHEMBL12",
      "CHEMBL1201753",
      "CHEMBL1204759",
      "CHEMBL1213118",
      "CHEMBL1232461",
      "CHEMBL1256967",
      "CHEMBL12610",
      "CHEMBL1276308",
      "CHEMBL1346",
      "CHEMBL1355736",
      "CHEMBL1363",
      "CHEMBL1371",
      "CHEMBL139",
      "CHEMBL1405150",
      "CHEMBL141157",
      "CHEMBL1427959",
      "CHEMBL1463345",
      "CHEMBL1464",
      "CHEMBL1483",
      "CHEMBL1513",
      "CHEMBL1575409",
      "CHEMBL1614705",
      "CHEMBL1645392",
      "CHEMBL1688458",
      "CHEMBL1689109",
      "CHEMBL1689110",
      "CHEMBL1689111",
      "CHEMBL1689117",
      "CHEMBL1689119",
      "CHEMBL1689126",
      "CHEMBL1689127",
      "CHEMBL1689128",
      "CHEMBL1689133",
      "CHEMBL1689135",
      "CHEMBL1689137",
      "CHEMBL17157",
      "CHEMBL1734492",
      "CHEMBL1761322",
      "CHEMBL1773254",
      "CHEMBL1778628",
      "CHEMBL1778639",
      "CHEMBL1778644",
      "CHEMBL1779512",
      "CHEMBL1790041",
      "CHEMBL1800526",
      "CHEMBL1800528",
      "CHEMBL1800659",
      "CHEMBL1807820",
      "CHEMBL1807821",
      "CHEMBL1807823",
      "CHEMBL1807827",
      "CHEMBL1807829",
      "CHEMBL1829174",
      "CHEMBL1829763",
      "CHEMBL1834184",
      "CHEMBL1835918",
      "CHEMBL1852508",
      "CHEMBL1874317",
      "CHEMBL1900528",
      "CHEMBL1916271",
      "CHEMBL1916272",
      "CHEMBL1916282",
      "CHEMBL1916288",
      "CHEMBL1916289",
      "CHEMBL1917443",
      "CHEMBL1917450",
      "CHEMBL1917456",
      "CHEMBL1917458",
      "CHEMBL1917459",
      "CHEMBL192",
      "CHEMBL1929039",
      "CHEMBL193",
      "CHEMBL1934426",
      "CHEMBL1938400",
      "CHEMBL1939560",
      "CHEMBL1944691",
      "CHEMBL1945033",
      "CHEMBL1947157",
      "CHEMBL1951575",
      "CHEMBL196707",
      "CHEMBL2017291",
      "CHEMBL2018964",
      "CHEMBL2018969",
      "CHEMBL20210",
      "CHEMBL203059",
      "CHEMBL2036958",
      "CHEMBL205078",
      "CHEMBL2057371",
      "CHEMBL2057372",
      "CHEMBL2058529",
      "CHEMBL2062774",
      "CHEMBL2070950",
      "CHEMBL2137199",
      "CHEMBL2141746",
      "CHEMBL2147032",
      "CHEMBL2147033",
      "CHEMBL2147475",
      "CHEMBL2158771",
      "CHEMBL2158785",
      "CHEMBL2158792",
      "CHEMBL2158793",
      "CHEMBL2158826",
      "CHEMBL2158839",
      "CHEMBL217899",
      "CHEMBL2181753",
      "CHEMBL2181926",
      "CHEMBL2181927",
      "CHEMBL2207669",
      "CHEMBL2216859",
      "CHEMBL2216870",
      "CHEMBL23",
      "CHEMBL2326623",
      "CHEMBL2326624",
      "CHEMBL232846",
      "CHEMBL2349318",
      "CHEMBL235789",
      "CHEMBL2364624",
      "CHEMBL256668",
      "CHEMBL257025",
      "CHEMBL271012",
      "CHEMBL272705",
      "CHEMBL35",
      "CHEMBL360227",
      "CHEMBL361546",
      "CHEMBL361812",
      "CHEMBL370492",
      "CHEMBL380732",
      "CHEMBL380947",
      "CHEMBL38380",
      "CHEMBL402501",
      "CHEMBL402728",
      "CHEMBL402986",
      "CHEMBL403225",
      "CHEMBL403313",
      "CHEMBL408",
      "CHEMBL42",
      "CHEMBL423",
      "CHEMBL451",
      "CHEMBL457",
      "CHEMBL46",
      "CHEMBL46740",
      "CHEMBL472",
      "CHEMBL49",
      "CHEMBL5",
      "CHEMBL551170",
      "CHEMBL551813",
      "CHEMBL552512",
      "CHEMBL553",
      "CHEMBL560219",
      "CHEMBL560423",
      "CHEMBL560993",
      "CHEMBL565755",
      "CHEMBL570015",
      "CHEMBL578194",
      "CHEMBL580",
      "CHEMBL583042",
      "CHEMBL589973",
      "CHEMBL62136",
      "CHEMBL682",
      "CHEMBL6966",
      "CHEMBL71",
      "CHEMBL72",
      "CHEMBL723",
      "CHEMBL782",
      "CHEMBL787",
      "CHEMBL82663",
      "CHEMBL833",
      "CHEMBL841",
      "CHEMBL894",
      "CHEMBL945",
      "CHEMBL95",
      "CHEMBL956",
      "CHEMBL957"
    ],
    "shared_structures_with_multiple_rows_or_ids": 0,
    "shared_structures_without_shared_id": 0
  },
  "UNRESOLVED": "Any repeated activities remain unresolved replicates; no aggregation or label selection occurs. No clearance ratio, difference, scaling, correlation or model is calculated."
}
```

## Biogen

OBSERVED: 3521 rows; exact non-null HLM N = 3087; column `LOG HLM_CLint (mL/min/kg)`. See BIOGEN_AUDIT.md for independent descriptive results; no numerical cross-dataset comparison is made.

## Chemical-space audit

INFERRED: RDKit 2025.03.6 sanitized isomeric canonical SMILES; stereochemistry, isotopes, charge and all disconnected fragments retained. No parent selection, desalting, neutralization, tautomer normalization or stereo removal. RDKit ordinary explicit-H handling applies. Equality is string equality of valid keys; missing/invalid structures never match. Identity is representation-specific, not proof of sample identity.

INFERRED: Descriptors use RDKit MolWt (g/mol), Wildman-Crippen MolLogP, CalcTPSA (A^2), Lipinski NumHDonors/NumHAcceptors, strict CalcNumRotatableBonds, CalcFractionCSP3. Every valid source row is characterised, including duplicates and rows with missing targets. No outliers are removed.

| Source / property | Numeric N | Min | Q05 | Q25 | Median | Q75 | Q95 | Max | IQR | MAD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| OBSERVED: CHEMBL3301370 / molecular_weight | 1102 | 133.154 | 241.291 | 340.335 | 414.549 | 478.622 | 569.66 | 1065.7 | 138.288 | 67.044 |
| OBSERVED: CHEMBL3301370 / clogp | 1102 | -1.9714 | 1.39099 | 2.81585 | 3.64341 | 4.53905 | 5.64899 | 10.3425 | 1.7232 | 0.85982 |
| OBSERVED: CHEMBL3301370 / tpsa | 1102 | 3.24 | 38.3325 | 57.9025 | 79.54 | 96.4125 | 124.276 | 300.89 | 38.51 | 17.995 |
| OBSERVED: CHEMBL3301370 / hbd | 1102 | 0 | 0 | 1 | 1 | 2 | 4 | 11 | 1 | 1 |
| OBSERVED: CHEMBL3301370 / hba | 1102 | 1 | 2 | 4 | 5 | 6 | 8 | 14 | 2 | 1 |
| OBSERVED: CHEMBL3301370 / rotatable_bonds | 1102 | 0 | 2 | 4 | 6 | 8 | 11.95 | 23 | 4 | 2 |
| OBSERVED: CHEMBL3301370 / fraction_csp3 | 1102 | 0 | 0 | 0.1875 | 0.315789 | 0.43442 | 0.6 | 0.888889 | 0.24692 | 0.118993 |
| OBSERVED: CHEMBL3301371 / molecular_weight | 837 | 147.177 | 239.66 | 343.423 | 415.862 | 475.004 | 578.185 | 1160.43 | 131.581 | 64.732 |
| OBSERVED: CHEMBL3301371 / clogp | 837 | -7.8314 | 1.03734 | 2.64662 | 3.5376 | 4.41952 | 5.91242 | 10.3425 | 1.7729 | 0.88487 |
| OBSERVED: CHEMBL3301371 / tpsa | 837 | 3.24 | 35.128 | 60.45 | 82.59 | 101.79 | 132.2 | 490.66 | 41.34 | 20.23 |
| OBSERVED: CHEMBL3301371 / hbd | 837 | 0 | 0 | 1 | 2 | 2 | 5 | 18 | 1 | 1 |
| OBSERVED: CHEMBL3301371 / hba | 837 | 1 | 2 | 4 | 5 | 7 | 9 | 18 | 3 | 1 |
| OBSERVED: CHEMBL3301371 / rotatable_bonds | 837 | 0 | 2 | 4 | 6 | 8 | 12 | 28 | 4 | 2 |
| OBSERVED: CHEMBL3301371 / fraction_csp3 | 837 | 0 | 0.0549708 | 0.208333 | 0.315789 | 0.434783 | 0.622868 | 0.846154 | 0.226449 | 0.115789 |
| OBSERVED: CHEMBL3301372 / molecular_weight | 408 | 30.07 | 217.613 | 325.622 | 397.476 | 469.905 | 549.027 | 914.187 | 144.283 | 72.415 |
| OBSERVED: CHEMBL3301372 / clogp | 408 | -1.8644 | 0.91544 | 2.47 | 3.37795 | 4.34332 | 5.69199 | 8.948 | 1.87332 | 0.92795 |
| OBSERVED: CHEMBL3301372 / tpsa | 408 | 0 | 34.6 | 55.71 | 79.515 | 98.585 | 130.746 | 235.97 | 42.875 | 21.945 |
| OBSERVED: CHEMBL3301372 / hbd | 408 | 0 | 0 | 1 | 1 | 2 | 4 | 6 | 1 | 1 |
| OBSERVED: CHEMBL3301372 / hba | 408 | 0 | 2 | 3 | 5 | 7 | 9 | 14 | 4 | 2 |
| OBSERVED: CHEMBL3301372 / rotatable_bonds | 408 | 0 | 1 | 3 | 5 | 7 | 11 | 16 | 4 | 2 |
| OBSERVED: CHEMBL3301372 / fraction_csp3 | 408 | 0 | 0.0601103 | 0.181818 | 0.30602 | 0.428571 | 0.644588 | 1 | 0.246753 | 0.123377 |
| OBSERVED: Clearance_Microsome_AZ / molecular_weight | 1102 | 133.154 | 241.291 | 340.335 | 414.549 | 478.622 | 569.66 | 1065.7 | 138.288 | 67.044 |
| OBSERVED: Clearance_Microsome_AZ / clogp | 1102 | -1.9714 | 1.39099 | 2.81958 | 3.64341 | 4.53905 | 5.64899 | 10.3425 | 1.71948 | 0.85886 |
| OBSERVED: Clearance_Microsome_AZ / tpsa | 1102 | 3.24 | 38.3325 | 57.9025 | 79.46 | 96.33 | 124.276 | 300.89 | 38.4275 | 17.945 |
| OBSERVED: Clearance_Microsome_AZ / hbd | 1102 | 0 | 0 | 1 | 1 | 2 | 4 | 11 | 1 | 1 |
| OBSERVED: Clearance_Microsome_AZ / hba | 1102 | 1 | 2 | 4 | 5 | 6 | 8 | 14 | 2 | 1 |
| OBSERVED: Clearance_Microsome_AZ / rotatable_bonds | 1102 | 0 | 2 | 4 | 6 | 8 | 11.95 | 23 | 4 | 2 |
| OBSERVED: Clearance_Microsome_AZ / fraction_csp3 | 1102 | 0 | 0 | 0.1875 | 0.315789 | 0.43442 | 0.6 | 0.888889 | 0.24692 | 0.118993 |
| OBSERVED: Clearance_Hepatocyte_AZ / molecular_weight | 1213 | 30.07 | 232.543 | 336.432 | 410.4 | 472.387 | 566.887 | 1160.43 | 135.955 | 67.183 |
| OBSERVED: Clearance_Hepatocyte_AZ / clogp | 1213 | -7.8314 | 1.0349 | 2.6037 | 3.4871 | 4.38702 | 5.83048 | 10.3425 | 1.78332 | 0.8891 |
| OBSERVED: Clearance_Hepatocyte_AZ / tpsa | 1213 | 0 | 33.42 | 57.78 | 80.91 | 99.88 | 129.144 | 490.66 | 42.1 | 21.31 |
| OBSERVED: Clearance_Hepatocyte_AZ / hbd | 1213 | 0 | 0 | 1 | 2 | 2 | 4 | 18 | 1 | 1 |
| OBSERVED: Clearance_Hepatocyte_AZ / hba | 1213 | 0 | 2 | 4 | 5 | 7 | 9 | 18 | 3 | 1 |
| OBSERVED: Clearance_Hepatocyte_AZ / rotatable_bonds | 1213 | 0 | 1 | 4 | 6 | 7 | 12 | 28 | 3 | 2 |
| OBSERVED: Clearance_Hepatocyte_AZ / fraction_csp3 | 1213 | 0 | 0.0555556 | 0.2 | 0.3125 | 0.433333 | 0.641143 | 1 | 0.233333 | 0.120192 |
| OBSERVED: Biogen / molecular_weight | 3521 | 150.145 | 219.288 | 268.32 | 313.792 | 364.489 | 461.949 | 1097.4 | 96.169 | 47.581 |
| OBSERVED: Biogen / clogp | 3521 | -1.98 | 0.97814 | 2.0532 | 2.7828 | 3.5326 | 4.7748 | 9.0141 | 1.4794 | 0.7388 |
| OBSERVED: Biogen / tpsa | 3521 | 3.24 | 38.33 | 49.33 | 60.15 | 74.44 | 103.78 | 258.52 | 25.11 | 12.32 |
| OBSERVED: Biogen / hbd | 3521 | 0 | 0 | 1 | 1 | 1 | 3 | 8 | 0 | 0 |
| OBSERVED: Biogen / hba | 3521 | 1 | 2 | 3 | 4 | 5 | 7 | 16 | 2 | 1 |
| OBSERVED: Biogen / rotatable_bonds | 3521 | 0 | 2 | 3 | 4 | 5 | 7 | 35 | 2 | 1 |
| OBSERVED: Biogen / fraction_csp3 | 3521 | 0 | 0.0625 | 0.2 | 0.333333 | 0.466667 | 0.7 | 1 | 0.266667 | 0.133333 |

## Uncertainty and provenance

UNRESOLVED: ChEMBL live API release may differ from historical TDC release; no historical ChEMBL release asserted.

UNRESOLVED: Null ChEMBL standard/original relations remain UNKNOWN; none are recoded to explicit equals. Numeric source values without qualifiers are not asserted to be uncensored observations.

UNRESOLVED: Rat assay strain metadata contains CD1, BC, CD1, NMRI, SCID, or Nd. Species classification follows explicit assay organism Rattus norvegicus/taxonomy 10116 and description; the strain annotation requires source-level review.

UNRESOLVED: Identity matching does not resolve unspecified stereochemistry, tautomer differences or sample provenance.

UNRESOLVED: TDC has numeric targets without native unit/censor fields; absent qualifiers are not evidence of exact uncensored measurements.

OBSERVED: Full machine-readable results are DATA_AUDIT.json. All six complete enriched row tables, structure anomalies and duplicate groups are under data/interim. Raw files and receipt hashes are in manifests/source_manifest.json and PROVENANCE_TABLE.csv. Execution logs include failures with actual errors.

OBSERVED: Initial reports were explicitly archived under reports/revisions/initial-audit with original hashes and a code snapshot before adding secondary ID/parent-ID reconciliation. Strict structural identity and all raw inputs are unchanged.

INFERRED: Native ChEMBL source numeric boundary distributions are descriptive, not estimates of uncensored clearance. Raw TDC and Biogen numeric labels do not encode absent censor metadata. Missing metadata remains unknown.

OBSERVED: Acquisition initially failed only while generating the manifest because the ChEMBL status activities field is an integer. All raw downloads were retained; a list-type check fixed manifest generation and acquisition was rerun using the same bytes. No failed computation was replaced by a mock result.


<!-- END INPUT inputs/reports/DATA_AUDIT.md -->


---
<!-- BEGIN INPUT inputs/reports/REVIEW_SUMMARY.md -->

Source: `inputs/reports/REVIEW_SUMMARY.md`  
SHA-256 of exact source bytes: `b08e8b82f59d53ef09c82c9be80a1e627197d2ae9d8a57f0fe9bc8c61981a3be`  
Origin: 4640ea721204771979e5637e81217f59c65318e6

# Audit review summary

## Source counts

| Source | OBSERVED rows | OBSERVED unique IDs / strict structures |
|---|---:|---:|
| CHEMBL3301370 human HLM | 1,102 | 1,102 / 1,102 |
| CHEMBL3301371 rat hepatocyte | 837 | 837 / 837 |
| CHEMBL3301372 human hepatocyte | 408 | 408 / 408 |
| TDC Clearance_Microsome_AZ | 1,102 | 1,102 / 1,102 |
| TDC Clearance_Hepatocyte_AZ | 1,213 | 1,020 / 1,020 |
| Biogen ADME_public_set_3521.csv | 3,521 | 3,521 / 3,521 |

EXPECTED_FROM_MEMO: The task supplied ChEMBL expectations of 1,102 / 837 / 408; these match ChEMBL 37 observations. The frozen memo itself contains no numeric expectations.

OBSERVED: ChEMBL completeness is verified against the downloaded **ChEMBL 37 API state**, not a historical release. Stored pagination metadata, acquired row counts and unique activity IDs must agree for each assay. This does not establish completeness against the historical ChEMBL release used to construct TDC.

## Relations and boundaries

| Assay | OBSERVED `<` | OBSERVED `>` | OBSERVED explicit `=` | OBSERVED null/UNKNOWN |
|---|---:|---:|---:|---:|
| CHEMBL3301370 | 274 | 84 | 0 | 744 |
| CHEMBL3301371 | 115 | 127 | 0 | 595 |
| CHEMBL3301372 | 104 | 15 | 0 | 289 |

OBSERVED: All `<` boundaries are 3; all `>` boundaries are 150. Original and standard relation counts agree. Null is not recoded to equals. Units and every reported value by relation are preserved in DATA_AUDIT.json.

| Assay | OBSERVED null relation at 3 | OBSERVED null relation at 150 |
|---|---:|---:|
| CHEMBL3301370 | 13 | 0 |
| CHEMBL3301371 | 2 | 0 |
| CHEMBL3301372 | 0 | 0 |

OBSERVED: The two rat-assay records are activity 14768823 (CHEMBL589973) and activity 14768825 (CHEMBL364714), each with standard value 3.0 and null relation. Both remain UNKNOWN.

OBSERVED: TDC microsome has 287 values exactly 3 and 84 exactly 150; TDC hepatocyte has 195 exactly 3 and 137 exactly 150. Neither has inequality strings or missing targets. The 287 microsome values at 3 include 274 matches to `<3` records; the remaining 13 match records with null relations. A numeric boundary alone does not define censor status.

## Species claim

INFERRED: **REPRODUCED locally** from explicit rat-only and human-only structure/value matches; historical data lineage remains an inference.

OBSERVED: TDC hepatocyte strict structure classes, as **rows / distinct valid structures**, are rat only **609 / 609**, human only **183 / 183**, both **405 / 218**, neither **16 / 10**, ambiguous/unparseable **0 / 0**. All 193 duplicated structure groups have different labels. Of these, 187 pairs each contain exactly two TDC rows: one uniquely matches a rat source record and the other uniquely matches a human source record by strict structure and exact numeric value, with no opposite-species value match. Six groups have no strict structural match to either source assay under the frozen identity rule (all twelve rows are neither): CHEMBL115, CHEMBL173706, CHEMBL1513, CHEMBL1483, CHEMBL190 and CHEMBL82663. Secondary exact-ID evidence supports 190 such pairs, leaving three unresolved; it does not change the strict structural counts. Thirty-one individual rows have a value compatible with both species.

UNRESOLVED: Ten TDC structures (16 rows) have no strict current ChEMBL hepatocyte match. Eight rows remain unmatched even by exact molecule ID plus numeric value. Shared-structure/shared-label provenance cannot identify species uniquely. Rat assay strain metadata is inconsistent-looking; organism, taxonomy and description explicitly say rat, but the strain annotation requires source review.

## Microsome reconciliation

OBSERVED: **1,097 strict structure matches**, all with exactly equal numeric values; five unmatched structures on each side and no duplicates. Exact-ID overlap is **1,101**, with exact numeric agreement for all 1,101 IDs.

| TDC molecule ID | ChEMBL molecule ID | Discrepancy | Matching value | Standard InChIKeys |
|---|---|---|---:|---|
| CHEMBL82663 | CHEMBL82663 | Hydroxythiazole / thiazolone tautomer spellings | 111.0 | Equal |
| CHEMBL1483 | CHEMBL1483 | Heterocyclic N-H tautomer spellings | 34.67 | Equal |
| CHEMBL412142 | CHEMBL412142 | Imidazole N-H tautomer spellings | 96.0 | Equal |
| CHEMBL1513 | CHEMBL1513 | Tetrazole N-H tautomer spellings | 17.78 | Equal |
| CHEMBL190 | CHEMBL1355736 (declared parent CHEMBL190) | Theophylline / hydrate with disconnected `O` | 4.79 | Different |

OBSERVED: The four tautomer spellings have matching molecule IDs, values and standard InChIKeys, as independently confirmed in [AUDIT_REVIEW.md](AUDIT_REVIEW.md). The hydrate pair also has a matching value. Standard InChIKeys are supporting evidence only; all five remain mismatches under the frozen canonical-SMILES rule. Full strings, source activities and secondary ID evidence appear in the reconciliation CSV/JSON. This evidence does not establish when or why source representations changed. No tautomer or fragment transformation was applied.

OBSERVED: All 274 `<3` and 84 `>150` ChEMBL microsome records have strict TDC structure/value matches with numeric 3 or 150 and no inequality. All 1,102 ChEMBL original and standard numeric values agree.

INFERRED: ChEMBL's standard mL/min/g and original microL/min/mg are numerically equivalent units. No physiological scaling was performed.

UNRESOLVED: The raw TDC tables contain no unit/censor columns. Matched numbers support consistency with source units but cannot independently prove unit provenance or historical preprocessing. The datasets are not strictly identical despite equal row counts.

## Human paired cohort

OBSERVED: **187 shared molecule IDs and 187 shared strict canonical structures**, with no disagreement or duplicate-activity ambiguity between these identity definitions. Only cohort membership was established.

## Biogen and chemical anomalies

OBSERVED: Exact non-null HLM N is **3,087** in `LOG HLM_CLint (mL/min/kg)`; **434** values are missing. The supplied HLM target minimum is **0.675686709**, present **958** times; the maximum is **3.372714293**, median **1.205312653**. These are source-provided log labels; no new transformation was applied. No numerical comparison to AstraZeneca labels was performed.

INFERRED: The minimum pile-up is consistent with a reporting boundary; it does not alone prove censoring. Log base, source scaling derivation and per-row censor status remain UNRESOLVED from the downloaded CSV/README.

OBSERVED: All six sources have zero missing/invalid SMILES under the pinned parser. Only TDC hepatocyte has duplicate canonical structures. Biogen has **223** molecules with reproducibly detected unspecified potential stereochemistry and **4** multicomponent structures. Undefined stereo and fragment flags for every row, and descriptor ranges/quantiles/IQR/MAD for all six datasets, are retained in the full audit.

## Execution and review boundary

OBSERVED: The acquisition manifest initially failed on a metadata type check after all downloads succeeded; the actual FAILED traceback is retained. Raw inputs were unchanged during the fix. Initial derived reports were archived explicitly before the ID-evidence follow-up. Final unit-test receipts and integrity verification are under reports/ and manifests/.

OBSERVED: No modelling, model preprocessing, synthetic scientific results, HLM/HH arithmetic or physiological scaling was performed. The frozen memo and unrelated projects remain unchanged. This is the audit checkpoint for independent review.


<!-- END INPUT inputs/reports/REVIEW_SUMMARY.md -->


---
<!-- BEGIN INPUT inputs/reports/AUDIT_REVIEW.md -->

Source: `inputs/reports/AUDIT_REVIEW.md`  
SHA-256 of exact source bytes: `e2d7dfff97eb52c8ea1263485bb7f31638d7dda2f0d9b5d71717fa9dcc85fdfe`  
Origin: 4640ea721204771979e5637e81217f59c65318e6

# Independent audit review — commit 13715550

Reviewer scope: numerical re-verification of the frozen-source DMPK audit from `data/raw/` only. No project code, reports or data were modified; no preprocessing or modelling was run.

## Method

- Independent script (kept outside the repository, in a session scratch directory) using only stdlib `csv`/`json`/`hashlib`/`decimal` and RDKit 2025.03.6 from the experiment `.venv`. No project module (`audit.py`, `chemistry.py`, `provenance.py`) was imported.
- Identity: `Chem.MolFromSmiles` (default sanitisation) → `MolToSmiles(isomericSmiles=True, canonical=True)`; string equality; no salt stripping, tautomer or stereo normalisation. This is an independent implementation of the same strict rule, not a call of the audited one.
- Labels: exact `Decimal` equality of ChEMBL `standard_value` and TDC `Y`. Null `standard_relation` counted as NULL, never `=`.
- Working tree confirmed byte-identical to commit 13715550 for `data/`, `manifests/`, `reports/`, `src/`, `tests/` (`git diff` empty).

## Recomputed values vs. published audit

| Check | Recomputed | Published | Status |
|---|---|---|---|
| Raw-file receipts / manifest entries / raw files on disk | 18 / 18 / 18; 0 hash or size mismatches; 0 raw files without receipt; receipt ≡ manifest hashes | 18 verified | NO ISSUE |
| PyTDC 1.1.15 sdist SHA-256 vs PyPI metadata | match | match | NO ISSUE |
| CHEMBL3301370 rows / unique activity IDs / molecule IDs / structures | 1,102 / 1,102 / 1,102 / 1,102 | 1,102 | NO ISSUE |
| CHEMBL3301371 | 837 / 837 / 837 / 837 | 837 | NO ISSUE |
| CHEMBL3301372 | 408 / 408 / 408 / 408 | 408 | NO ISSUE |
| Pagination | 3301370: pages at offset 0 (1,000) and 1000 (102), contiguous, `next` null on last page, `total_count` constant 1,102; 3301371/72 single page with `next` null. All rows carry the requested assay ID; activity IDs sorted and unique. | complete | NO ISSUE |
| Standard relations `<` / `>` / NULL (3301370) | 274 / 84 / 744; boundaries all 3.0 / 150.0 | same | NO ISSUE |
| (3301371) | 115 / 127 / 595 | same | NO ISSUE |
| (3301372) | 104 / 15 / 289 | same | NO ISSUE |
| Explicit `=` in any assay | 0 | 0 | NO ISSUE |
| Original vs standard relation and value agreement | 100% in all three assays | same | NO ISSUE |
| TDC microsome rows / IDs / structures / dup groups | 1,102 / 1,102 / 1,102 / 0 | same | NO ISSUE |
| TDC hepatocyte rows / IDs / structures | 1,213 / 1,020 / 1,020 | same | NO ISSUE |
| TDC `Y` containing `<`, `>`, `≤`, `≥`, `~` | 0 (microsome), 0 (hepatocyte); no missing targets | 0 | NO ISSUE — qualifiers absent from TDC |
| TDC values exactly 3 / 150 | microsome 287 / 84; hepatocyte 195 / 137 | same | NO ISSUE |
| Hepatocyte duplicate groups | 193, all of size exactly 2; each group is a single TDC ID; no ID maps to >1 structure | 193 | NO ISSUE |
| Groups with differing labels | 193 / 193 (no identical-label group) | 193 | NO ISSUE |
| Strict rat/human pairs (exactly 2 rows; one row value-matches rat only, other value-matches human only) | 187; in all 187 each row matches exactly one source record | 187 | NO ISSUE |
| Non-strict groups | 6 (see below) | 6 unresolved | NO ISSUE (see MINOR-1) |
| Structure class rows (rat-only / human-only / both / neither) | 609 / 183 / 405 / 16 | same | NO ISSUE |
| Structure class distinct structures | 609 / 183 / 218 / 10 | same | NO ISSUE |
| Row value-match classes (rat / human / both / neither) | 796 / 370 / 31 / 16 | — (31 "both" published) | NO ISSUE |
| Rat-only or human-only structure rows lacking a value match | 0 / 0 | — | NO ISSUE |
| TDC microsome ↔ ChEMBL strict structure overlap | 1,097; 5 TDC-only; 5 ChEMBL-only; ≤1 candidate per row | 1,097 / 5 / 5 | NO ISSUE |
| Matched pairs with exact numeric equality / same molecule ID | 1,097 / 1,097 | 1,097 | NO ISSUE |
| Exact molecule-ID overlap | 1,101 | 1,101 | NO ISSUE |
| Matched ChEMBL `<3` → TDC 3; `>150` → TDC 150 | 274 / 274; 84 / 84 | same | NO ISSUE |
| TDC 3 matched to NULL-relation ChEMBL records | 13 | 13 | NO ISSUE |
| Human HLM ∩ HH by molecule ID / by structure | 187 / 187; the two sets map one-to-one | 187 / 187 | NO ISSUE |
| Biogen rows / unique Internal IDs / structures | 3,521 / 3,521 / 3,521 | same | NO ISSUE |
| Biogen HLM non-null / missing | 3,087 / 434; 0 unparseable | same | NO ISSUE |
| Biogen HLM min / count at min / next value | 0.675686709 / 958 / 0.678154038 | 0.675686709 / 958 | NO ISSUE |
| Biogen HLM max / median | 3.372714293 / 1.205312653 | same | NO ISSUE |

## Five unmatched microsome structures (strict rule not relaxed)

| TDC ID | TDC canonical | ChEMBL record (same ID or declared parent) | Value | Relation | Standard InChIKey equal |
|---|---|---|---|---|---|
| CHEMBL82663 | `…c2nc(O)sc12` (hydroxythiazole) | CHEMBL82663 `O=c1[nH]c2…s1` (thiazolone) | 111.0 = 111.0 | NULL | yes |
| CHEMBL1483 | `…c2nc(…)[nH]c2c1` | CHEMBL1483 `…c2[nH]c(…)nc2c1` | 34.67 = 34.67 | NULL | yes |
| CHEMBL412142 | `Cc1c[nH]c(…)n1` | CHEMBL412142 `Cc1cnc(…)[nH]1` | 96.0 = 96.0 | NULL | yes |
| CHEMBL1513 | tetrazole `nn[nH]n` | CHEMBL1513 tetrazole `nnn[nH]` | 17.78 = 17.78 | NULL | yes |
| CHEMBL190 | theophylline | CHEMBL1355736 (parent CHEMBL190) `….O` hydrate | 4.79 = 4.79 | NULL | no (extra water component) |

Four are tautomer/representation differences (confirmed by identical standard InChIKey, used here as supporting evidence only); one is a parent/hydrate difference. All values agree exactly. These remain strict mismatches, as the audit states.

## Six non-strict hepatocyte duplicate groups

All six are two-row groups whose structure has **no strict match in either rat or human ChEMBL** (both rows "neither"): CHEMBL115 (10.23, 53.7), CHEMBL173706 (150.0, 4.57), CHEMBL1513 (9.01, 10.47), CHEMBL1483 (83.18, 12.59), CHEMBL190 (5.75, 3.0), CHEMBL82663 (91.0, 42.5). Four of these IDs are the same tautomer/hydrate cases as the microsome mismatches. These 12 rows plus 4 singleton rows make up the 16 "neither" rows / 10 structures. No group has 3+ rows, a both-species row, or a single-species pair.

## Findings

### BLOCKER

None.

### IMPORTANT

**IMPORTANT-1 — Acquisition and integrity failure modes are claimed but not tested.**
- File/line: `tests/test_audit.py` (whole file); code paths `src/acquire.py:17-23` (missing receipt, changed URL), `src/acquire.py:43-61` (total-count drift, empty page, wrong assay, repeated activity ID, incomplete pagination), `src/provenance.py:46-47` (hash/size mismatch), `src/audit.py:355-358` (refuse changed outputs). README "Reproduction" asserts these fail.
- Tests actually cover: SHA-256 vector, create-only write refusal, parsing/identity/relation handling, and species/microsome/paired logic on synthetic fixtures. None of the listed acquisition/verification paths is exercised.
- Scientific consequence: none for the current snapshot (independently verified complete and hash-consistent above); but regressions in the completeness/immutability guards would go undetected in any future re-acquisition.
- Published number changes: no.
- Minimal correction: add offline tests with synthetic page JSON (total_count change, empty page, duplicate activity_id, short final page) by factoring the pagination check into a pure function, plus a `verify()` test with a tampered byte and a URL-change test for `download()` against a temp ROOT.

### MINOR

**MINOR-1 — Wording of the six "unresolved" groups understates why.** `reports/REVIEW_SUMMARY.md` ("six groups remain unresolved under that rule") and `src/audit.py:149` (`partial_or_unresolved`). All six have zero strict structural candidates in either species; they are not partially traced. Consequence: reader could assume ambiguous species evidence rather than representation mismatch. No number changes. Correction: state "six groups have no strict structural match to either ChEMBL hepatocyte assay (all rows 'neither')".

**MINOR-2 — Trace rule is looser than the strict pair definition.** `src/audit.py:149` accepts any group with differing labels containing ≥1 rat-only and ≥1 human-only row; it does not require group size 2 or single-record provenance. On this snapshot every group has size 2 and each matched row maps to exactly one record, so the count is identical (187). Correction: assert `len(rows) == 2` and single matching record, or report non-binary groups separately.

**MINOR-3 — Completeness is not re-checked at audit time.** `src/audit.py:49-63` does not compare loaded rows with `page_meta.total_count`, and `EXPECTED` (`src/audit.py:16`) is reported but not enforced. Relies on acquisition-time checks (untested, IMPORTANT-1). No number changes. Correction: assert `len(rows) == page_meta.total_count` and `next is None` on the last page inside `load_sources`.

**MINOR-4 — Null-relation values at censoring boundaries are not tabulated per assay in the summary.** Recomputed: 13 (3301370) and 2 (3301371) NULL-relation records have value exactly 3; none at 150. The summary mentions the 13 microsome cases only. No number changes; the audit correctly keeps them UNKNOWN. Correction: add the per-assay count to REVIEW_SUMMARY.

### NO ISSUE

Raw-file preservation and SHA-256 manifests; ChEMBL counts and pagination; relation counts and null handling (never recoded to `=`); TDC removal of `<`/`>` qualifiers (confirmed: 274 `<3` and 84 `>150` records appear as bare 3 / 150); hepatocyte duplicate groups and label differences; 187 strict pairs; 609/183/405/16 classification; 1,097/1,102 microsome matches and five unmatched identities; 187 paired human cohort under both identity definitions; Biogen N, missingness and 958-value minimum pile-up.

## Acquisition-completeness assessment

Stored page metadata is internally consistent with complete retrieval for all three assays (constant `total_count`, contiguous offsets, terminal `next: null`, rows = total, unique activity IDs = total). Completeness is relative to the live ChEMBL 37 API at retrieval time; it cannot be independently confirmed against a historical release, which the audit already flags as UNRESOLVED. No concern for this snapshot beyond the untested guards (IMPORTANT-1).

## Verdict

All headline numeric conclusions of the original audit survive independent recomputation with zero numeric discrepancies. Corrections are limited to test coverage and wording/robustness of rules that do not change any published figure.

**PASS_WITH_CORRECTIONS**


<!-- END INPUT inputs/reports/AUDIT_REVIEW.md -->


---
<!-- BEGIN INPUT inputs/reports/BIOGEN_AUDIT.md -->

Source: `inputs/reports/BIOGEN_AUDIT.md`  
SHA-256 of exact source bytes: `92fb5c0a8128f47ae4b91597e047b8a1dcee06d3f7aecc493ee5994a78afb217`  
Origin: 4640ea721204771979e5637e81217f59c65318e6

# Biogen HLM audit

```json
{
  "INFERRED": "Repeated exact values at distribution boundaries are pile-ups consistent with reporting/assay limits; they alone do not prove censoring. Undefined stereochemistry means RDKit-detectable potential stereo elements without specified configuration, not demonstrated sample composition.",
  "OBSERVED": {
    "exact_hlm_column": "LOG HLM_CLint (mL/min/kg)",
    "missing_hlm_n": 434,
    "non_null_hlm_n": 3087,
    "structure_and_target_audit": {
      "chemical_space": {
        "clogp": {
          "exactly_150": 0,
          "exactly_3": 0,
          "inequality_strings": 0,
          "iqr": 1.4794000000000023,
          "mad": 0.7388000000000008,
          "max": 9.0141,
          "median": 2.782800000000001,
          "min": -1.9800000000000006,
          "missing_rows": 0,
          "numeric_rows": 3521,
          "q05": 0.9781399999999999,
          "q25": 2.0532,
          "q75": 3.532600000000002,
          "q95": 4.7748000000000035,
          "top_value_frequencies": [
            {
              "count": 3,
              "value": "2.127"
            },
            {
              "count": 3,
              "value": "2.34412"
            },
            {
              "count": 3,
              "value": "4.068500000000003"
            },
            {
              "count": 2,
              "value": "0.0427199999999997"
            },
            {
              "count": 2,
              "value": "0.1988999999999993"
            },
            {
              "count": 2,
              "value": "0.91212"
            },
            {
              "count": 2,
              "value": "1.0446999999999993"
            },
            {
              "count": 2,
              "value": "1.4462"
            },
            {
              "count": 2,
              "value": "1.61432"
            },
            {
              "count": 2,
              "value": "1.6822"
            }
          ],
          "total_rows": 3521,
          "unparseable_rows": 0
        },
        "fraction_csp3": {
          "exactly_150": 0,
          "exactly_3": 0,
          "inequality_strings": 0,
          "iqr": 0.26666666666666666,
          "mad": 0.1333333333333333,
          "max": 1.0,
          "median": 0.3333333333333333,
          "min": 0.0,
          "missing_rows": 0,
          "numeric_rows": 3521,
          "q05": 0.0625,
          "q25": 0.2,
          "q75": 0.4666666666666667,
          "q95": 0.7,
          "top_value_frequencies": [
            {
              "count": 145,
              "value": "0.5"
            },
            {
              "count": 132,
              "value": "0.3333333333333333"
            },
            {
              "count": 97,
              "value": "0.25"
            },
            {
              "count": 84,
              "value": "0.0"
            },
            {
              "count": 75,
              "value": "0.2"
            },
            {
              "count": 75,
              "value": "0.4"
            },
            {
              "count": 68,
              "value": "0.2857142857142857"
            },
            {
              "count": 65,
              "value": "0.42857142857142855"
            },
            {
              "count": 57,
              "value": "0.2727272727272727"
            },
            {
              "count": 54,
              "value": "0.3"
            }
          ],
          "total_rows": 3521,
          "unparseable_rows": 0
        },
        "hba": {
          "exactly_150": 0,
          "exactly_3": 688,
          "inequality_strings": 0,
          "iqr": 2.0,
          "mad": 1.0,
          "max": 16.0,
          "median": 4.0,
          "min": 1.0,
          "missing_rows": 0,
          "numeric_rows": 3521,
          "q05": 2.0,
          "q25": 3.0,
          "q75": 5.0,
          "q95": 7.0,
          "top_value_frequencies": [
            {
              "count": 982,
              "value": "4"
            },
            {
              "count": 756,
              "value": "5"
            },
            {
              "count": 688,
              "value": "3"
            },
            {
              "count": 443,
              "value": "6"
            },
            {
              "count": 260,
              "value": "2"
            },
            {
              "count": 240,
              "value": "7"
            },
            {
              "count": 88,
              "value": "8"
            },
            {
              "count": 31,
              "value": "9"
            },
            {
              "count": 19,
              "value": "10"
            },
            {
              "count": 6,
              "value": "1"
            }
          ],
          "total_rows": 3521,
          "unparseable_rows": 0
        },
        "hbd": {
          "exactly_150": 0,
          "exactly_3": 133,
          "inequality_strings": 0,
          "iqr": 0.0,
          "mad": 0.0,
          "max": 8.0,
          "median": 1.0,
          "min": 0.0,
          "missing_rows": 0,
          "numeric_rows": 3521,
          "q05": 0.0,
          "q25": 1.0,
          "q75": 1.0,
          "q95": 3.0,
          "top_value_frequencies": [
            {
              "count": 2014,
              "value": "1"
            },
            {
              "count": 848,
              "value": "0"
            },
            {
              "count": 482,
              "value": "2"
            },
            {
              "count": 133,
              "value": "3"
            },
            {
              "count": 31,
              "value": "4"
            },
            {
              "count": 9,
              "value": "5"
            },
            {
              "count": 2,
              "value": "6"
            },
            {
              "count": 1,
              "value": "7"
            },
            {
              "count": 1,
              "value": "8"
            }
          ],
          "total_rows": 3521,
          "unparseable_rows": 0
        },
        "molecular_weight": {
          "exactly_150": 0,
          "exactly_3": 0,
          "inequality_strings": 0,
          "iqr": 96.16900000000015,
          "mad": 47.580999999999904,
          "max": 1097.3979999999992,
          "median": 313.79200000000014,
          "min": 150.145,
          "missing_rows": 0,
          "numeric_rows": 3521,
          "q05": 219.28799999999998,
          "q25": 268.32,
          "q75": 364.48900000000015,
          "q95": 461.94900000000024,
          "top_value_frequencies": [
            {
              "count": 6,
              "value": "258.32099999999997"
            },
            {
              "count": 5,
              "value": "202.213"
            },
            {
              "count": 5,
              "value": "203.245"
            },
            {
              "count": 5,
              "value": "259.30899999999997"
            },
            {
              "count": 5,
              "value": "262.353"
            },
            {
              "count": 4,
              "value": "214.268"
            },
            {
              "count": 4,
              "value": "228.295"
            },
            {
              "count": 4,
              "value": "257.33699999999993"
            },
            {
              "count": 4,
              "value": "287.36299999999994"
            },
            {
              "count": 4,
              "value": "296.33000000000004"
            }
          ],
          "total_rows": 3521,
          "unparseable_rows": 0
        },
        "rotatable_bonds": {
          "exactly_150": 0,
          "exactly_3": 796,
          "inequality_strings": 0,
          "iqr": 2.0,
          "mad": 1.0,
          "max": 35.0,
          "median": 4.0,
          "min": 0.0,
          "missing_rows": 0,
          "numeric_rows": 3521,
          "q05": 2.0,
          "q25": 3.0,
          "q75": 5.0,
          "q95": 7.0,
          "top_value_frequencies": [
            {
              "count": 1021,
              "value": "4"
            },
            {
              "count": 796,
              "value": "3"
            },
            {
              "count": 464,
              "value": "2"
            },
            {
              "count": 458,
              "value": "5"
            },
            {
              "count": 312,
              "value": "6"
            },
            {
              "count": 164,
              "value": "7"
            },
            {
              "count": 122,
              "value": "1"
            },
            {
              "count": 79,
              "value": "8"
            },
            {
              "count": 42,
              "value": "9"
            },
            {
              "count": 30,
              "value": "0"
            }
          ],
          "total_rows": 3521,
          "unparseable_rows": 0
        },
        "tpsa": {
          "exactly_150": 0,
          "exactly_3": 0,
          "inequality_strings": 0,
          "iqr": 25.109999999999992,
          "mad": 12.32,
          "max": 258.5199999999999,
          "median": 60.15,
          "min": 3.24,
          "missing_rows": 0,
          "numeric_rows": 3521,
          "q05": 38.33,
          "q25": 49.330000000000005,
          "q75": 74.44,
          "q95": 103.78000000000002,
          "top_value_frequencies": [
            {
              "count": 67,
              "value": "41.99"
            },
            {
              "count": 35,
              "value": "45.230000000000004"
            },
            {
              "count": 34,
              "value": "46.92"
            },
            {
              "count": 34,
              "value": "59.81"
            },
            {
              "count": 28,
              "value": "49.410000000000004"
            },
            {
              "count": 26,
              "value": "40.620000000000005"
            },
            {
              "count": 25,
              "value": "54.88"
            },
            {
              "count": 23,
              "value": "58.120000000000005"
            },
            {
              "count": 22,
              "value": "50.7"
            },
            {
              "count": 22,
              "value": "51.22"
            }
          ],
          "total_rows": 3521,
          "unparseable_rows": 0
        }
      },
      "dummy_atom_rows": 0,
      "duplicated_structure_groups": 0,
      "excess_duplicate_rows": 0,
      "invalid_structure_rows": 0,
      "missing_identifiers": 0,
      "missing_structure_rows": 0,
      "molecules_with_undefined_stereo": 223,
      "multicomponent_rows": 4,
      "row_count": 3521,
      "rows_in_duplicate_groups": 0,
      "target_distribution": {
        "exactly_150": 0,
        "exactly_3": 0,
        "inequality_strings": 0,
        "iqr": 1.1274287875,
        "mad": 0.529625944,
        "max": 3.372714293,
        "median": 1.205312653,
        "min": 0.675686709,
        "missing_rows": 434,
        "numeric_rows": 3087,
        "q05": 0.675686709,
        "q25": 0.675686709,
        "q75": 1.8031154965,
        "q95": 2.4395045188999993,
        "top_value_frequencies": [
          {
            "count": 958,
            "value": "0.675686709"
          },
          {
            "count": 6,
            "value": "0.881384657"
          },
          {
            "count": 2,
            "value": "0.80140371"
          },
          {
            "count": 2,
            "value": "0.82445127"
          },
          {
            "count": 2,
            "value": "0.837651558"
          },
          {
            "count": 2,
            "value": "0.845903839"
          },
          {
            "count": 2,
            "value": "0.870462432"
          },
          {
            "count": 2,
            "value": "0.880813592"
          },
          {
            "count": 2,
            "value": "1.005952287"
          },
          {
            "count": 2,
            "value": "1.006893708"
          }
        ],
        "total_rows": 3521,
        "unparseable_rows": 0
      },
      "unique_identifiers": 3521,
      "unique_raw_smiles": 3521,
      "unique_valid_structures": 3521,
      "valid_structure_rows": 3521
    },
    "total_rows": 3521,
    "unique_internal_ids": 3521,
    "upstream_readme": "data/raw/biogen/README.md explicitly describes experimental log(properties)."
  },
  "UNRESOLVED": "CSV supplies no per-row HLM censor relation. Log base and derivation of bodyweight-normalized source labels are not established by the downloaded CSV/README. No log/inverse-log, scaling or numerical comparison with AstraZeneca has been performed."
}
```


<!-- END INPUT inputs/reports/BIOGEN_AUDIT.md -->


---
<!-- BEGIN INPUT inputs/reports/CENSORING_METADATA_CHECK.md -->

Source: `inputs/reports/CENSORING_METADATA_CHECK.md`  
SHA-256 of exact source bytes: `dff0913237ea554bf0609bd456ebaed3c907bd96cee7ef2f6401ec1263540370`  
Origin: 4640ea721204771979e5637e81217f59c65318e6

# Censoring metadata check — post-audit record

Date: 2026-09-17. Status of the 13 HLM null-at-3 records: **UNRESOLVED**
(**UNRESOLVED AFTER FROZEN-METADATA AUDIT**).

This record preserves the already-observed results of the read-only frozen-metadata inspection.
It does not amend the frozen audit reports or reinterpret any record's censoring status. No raw files
were modified, no data were preprocessed, no models were fitted, and no model performance was inspected.

## Frozen inputs and provenance

- Acquisition commit: `13715550adad0a628e92da6cf34568000ddbc797`.
- Validated audit checkpoint: tag `dmpk-data-audit-v1`, resolving to commit
  `1b93269b167d7d1bea245f90b34761011613f2d8`.
- Documentation parent for this record: `653e0fa94065dd74fd28a12ff122bc096cadfc04`, on
  `worktree-censoring-memo-metadata-audit`.
- Frozen inventory: [source_manifest.json](../manifests/source_manifest.json), SHA-256
  `370df65f0a6c18ef936b49429778a96f18efa2360c67356959bfb95c7547610d`.
  Original per-file download receipts remain in `../manifests/downloads/`.

The activity pages below were inspected directly as JSON. All paths are relative to
`experiments/compound_to_exposure/data/raw/chembl/`.

| Frozen activity page | Bytes | SHA-256 |
|---|---:|---|
| `CHEMBL3301370_activities_00000.json` | 1,474,958 | `657618e353b9795fd7fabb1a4086d7b936709059bbfdcbe689b0f87309e16d43` |
| `CHEMBL3301370_activities_01000.json` | 150,154 | `df8720b582563b8d04c1029aedb5fc5ced7614d3c190e912ac4bab67140ac46e` |
| `CHEMBL3301371_activities_00000.json` | 1,251,418 | `c6a101aba9d6e9010cbab9dd26daf7523929b6ce3dd19ea2e6625e8bcaf40f24` |
| `CHEMBL3301372_activities_00000.json` | 610,243 | `a1d5c17f98a34e3f4c5d1816c67ff97bb37c1722b66cb9a5a0ec348b3877ff90` |

OBSERVED: all **18 raw-file SHA-256 hashes and byte sizes matched the frozen source manifest**, including
these four pages. Inputs remain unchanged from the validated checkpoint. The inspection used direct
field tabulation and exact decimal comparisons of supplied values, without changing stored data.

## Observed counts

Groups below use `standard_value` and `standard_relation`. Original relations and numerical values
agree with their standard counterparts for every activity: 1,102/1,102 HLM, 837/837 rat hepatocyte and
408/408 human hepatocyte, or 2,347/2,347 overall.

| Group | CHEMBL3301370 HLM | CHEMBL3301371 rat hepatocyte | CHEMBL3301372 human hepatocyte |
|---|---:|---:|---:|
| All activities | 1,102 | 837 | 408 |
| Value = 3, relation null | 13 | 2 | 0 |
| Value = 150, relation null | 0 | 0 | 0 |
| Explicit `<` at value 3 | 274 | 115 | 104 |
| Explicit `>` at value 150 | 84 | 127 | 15 |
| Null relation, strictly 3 < value < 150 | 731 | 593 | 289 |

The 13 HLM activities are **14769802–14769814 inclusive**, all in
`CHEMBL3301370_activities_01000.json`. Each has raw `value` and `standard_value` equal to the string
`"3.0"`, and both `relation` and `standard_relation` equal to JSON `null`.

The two analogous rat activities are **14768823 / CHEMBL589973** and
**14768825 / CHEMBL364714**, both in `CHEMBL3301371_activities_00000.json`; each has the same
`"3.0"`/null value-and-relation pattern. Human hepatocytes have no null-relation record at either
numeric boundary.

## Fields inspected and comparison

The relevant fields were `activity_comment`, `data_validity_comment`, `text_value`,
`standard_text_value` (present), `standard_flag`, `relation` and `standard_relation`, alongside the
original and standard numeric values.

| Metadata | Null-at-3 records | Explicit `<3` records | Interior null-relation records | Explicit `>150` records |
|---|---|---|---|---|
| `activity_comment` | `null` | `null` | `null` | `null` |
| `data_validity_comment` | `null` | `null` | `null` | `null` |
| `text_value` | `null` | `null` | `null` | `null` |
| `standard_text_value` | `null` | `null` | `null` | `null` |
| `standard_flag` | `1` | `1` | `1` | `1` |
| `relation` / `standard_relation` | `null` / `null` | `<` / `<` | `null` / `null` | `>` / `>` |

These patterns hold across all three assays wherever the group exists. The four comment/text fields
are null for all 2,347 activities, and `standard_flag` is 1 for all 2,347, including explicit censoring.
Additional inspected metadata provides no distinction: `data_validity_description`, `upper_value` and
`standard_upper_value` are null; `activity_properties` is empty; `potential_duplicate` is 0 throughout.

## Result

The metadata does not distinguish the 13 HLM records as quantified versus censored. In particular,
`standard_flag = 1` is shared with explicitly censored records; both original and standard relations
are null, with no original equality qualifier to recover. No inspected annotation resolves their
censoring status. No record is reclassified as proven censored or proven uncensored, and null is not
converted to equality.

**UNRESOLVED**


<!-- END INPUT inputs/reports/CENSORING_METADATA_CHECK.md -->


---
<!-- BEGIN INPUT inputs/reports/PAIRED_HUMAN_COHORT_AUDIT.md -->

Source: `inputs/reports/PAIRED_HUMAN_COHORT_AUDIT.md`  
SHA-256 of exact source bytes: `488f9bb1dfda32055322a984211fd71648f4e3eec3c1171da2717b12c6307d3e`  
Origin: 4640ea721204771979e5637e81217f59c65318e6

# Paired human cohort audit

```json
{
  "INFERRED": "This establishes membership only under two identity definitions. It does not establish matched experimental conditions or independent biological replicates.",
  "OBSERVED": {
    "canonical_structure_overlap_n": 187,
    "id_overlap_n": 187,
    "id_structure_disagreement_or_ambiguity": [],
    "shared_ids": [
      "CHEMBL1017",
      "CHEMBL1020",
      "CHEMBL103667",
      "CHEMBL1071",
      "CHEMBL108",
      "CHEMBL1088752",
      "CHEMBL1089518",
      "CHEMBL1091137",
      "CHEMBL11",
      "CHEMBL112",
      "CHEMBL114",
      "CHEMBL1144",
      "CHEMBL1164729",
      "CHEMBL1194325",
      "CHEMBL12",
      "CHEMBL1201753",
      "CHEMBL1204759",
      "CHEMBL1213118",
      "CHEMBL1232461",
      "CHEMBL1256967",
      "CHEMBL12610",
      "CHEMBL1276308",
      "CHEMBL1346",
      "CHEMBL1355736",
      "CHEMBL1363",
      "CHEMBL1371",
      "CHEMBL139",
      "CHEMBL1405150",
      "CHEMBL141157",
      "CHEMBL1427959",
      "CHEMBL1463345",
      "CHEMBL1464",
      "CHEMBL1483",
      "CHEMBL1513",
      "CHEMBL1575409",
      "CHEMBL1614705",
      "CHEMBL1645392",
      "CHEMBL1688458",
      "CHEMBL1689109",
      "CHEMBL1689110",
      "CHEMBL1689111",
      "CHEMBL1689117",
      "CHEMBL1689119",
      "CHEMBL1689126",
      "CHEMBL1689127",
      "CHEMBL1689128",
      "CHEMBL1689133",
      "CHEMBL1689135",
      "CHEMBL1689137",
      "CHEMBL17157",
      "CHEMBL1734492",
      "CHEMBL1761322",
      "CHEMBL1773254",
      "CHEMBL1778628",
      "CHEMBL1778639",
      "CHEMBL1778644",
      "CHEMBL1779512",
      "CHEMBL1790041",
      "CHEMBL1800526",
      "CHEMBL1800528",
      "CHEMBL1800659",
      "CHEMBL1807820",
      "CHEMBL1807821",
      "CHEMBL1807823",
      "CHEMBL1807827",
      "CHEMBL1807829",
      "CHEMBL1829174",
      "CHEMBL1829763",
      "CHEMBL1834184",
      "CHEMBL1835918",
      "CHEMBL1852508",
      "CHEMBL1874317",
      "CHEMBL1900528",
      "CHEMBL1916271",
      "CHEMBL1916272",
      "CHEMBL1916282",
      "CHEMBL1916288",
      "CHEMBL1916289",
      "CHEMBL1917443",
      "CHEMBL1917450",
      "CHEMBL1917456",
      "CHEMBL1917458",
      "CHEMBL1917459",
      "CHEMBL192",
      "CHEMBL1929039",
      "CHEMBL193",
      "CHEMBL1934426",
      "CHEMBL1938400",
      "CHEMBL1939560",
      "CHEMBL1944691",
      "CHEMBL1945033",
      "CHEMBL1947157",
      "CHEMBL1951575",
      "CHEMBL196707",
      "CHEMBL2017291",
      "CHEMBL2018964",
      "CHEMBL2018969",
      "CHEMBL20210",
      "CHEMBL203059",
      "CHEMBL2036958",
      "CHEMBL205078",
      "CHEMBL2057371",
      "CHEMBL2057372",
      "CHEMBL2058529",
      "CHEMBL2062774",
      "CHEMBL2070950",
      "CHEMBL2137199",
      "CHEMBL2141746",
      "CHEMBL2147032",
      "CHEMBL2147033",
      "CHEMBL2147475",
      "CHEMBL2158771",
      "CHEMBL2158785",
      "CHEMBL2158792",
      "CHEMBL2158793",
      "CHEMBL2158826",
      "CHEMBL2158839",
      "CHEMBL217899",
      "CHEMBL2181753",
      "CHEMBL2181926",
      "CHEMBL2181927",
      "CHEMBL2207669",
      "CHEMBL2216859",
      "CHEMBL2216870",
      "CHEMBL23",
      "CHEMBL2326623",
      "CHEMBL2326624",
      "CHEMBL232846",
      "CHEMBL2349318",
      "CHEMBL235789",
      "CHEMBL2364624",
      "CHEMBL256668",
      "CHEMBL257025",
      "CHEMBL271012",
      "CHEMBL272705",
      "CHEMBL35",
      "CHEMBL360227",
      "CHEMBL361546",
      "CHEMBL361812",
      "CHEMBL370492",
      "CHEMBL380732",
      "CHEMBL380947",
      "CHEMBL38380",
      "CHEMBL402501",
      "CHEMBL402728",
      "CHEMBL402986",
      "CHEMBL403225",
      "CHEMBL403313",
      "CHEMBL408",
      "CHEMBL42",
      "CHEMBL423",
      "CHEMBL451",
      "CHEMBL457",
      "CHEMBL46",
      "CHEMBL46740",
      "CHEMBL472",
      "CHEMBL49",
      "CHEMBL5",
      "CHEMBL551170",
      "CHEMBL551813",
      "CHEMBL552512",
      "CHEMBL553",
      "CHEMBL560219",
      "CHEMBL560423",
      "CHEMBL560993",
      "CHEMBL565755",
      "CHEMBL570015",
      "CHEMBL578194",
      "CHEMBL580",
      "CHEMBL583042",
      "CHEMBL589973",
      "CHEMBL62136",
      "CHEMBL682",
      "CHEMBL6966",
      "CHEMBL71",
      "CHEMBL72",
      "CHEMBL723",
      "CHEMBL782",
      "CHEMBL787",
      "CHEMBL82663",
      "CHEMBL833",
      "CHEMBL841",
      "CHEMBL894",
      "CHEMBL945",
      "CHEMBL95",
      "CHEMBL956",
      "CHEMBL957"
    ],
    "shared_structures_with_multiple_rows_or_ids": 0,
    "shared_structures_without_shared_id": 0
  },
  "UNRESOLVED": "Any repeated activities remain unresolved replicates; no aggregation or label selection occurs. No clearance ratio, difference, scaling, correlation or model is calculated."
}
```

OBSERVED: Complete membership evidence: `../data/interim/PAIRED_HUMAN_COHORT.csv`. No clearance labels are included in that membership table.


<!-- END INPUT inputs/reports/PAIRED_HUMAN_COHORT_AUDIT.md -->


---
<!-- BEGIN INPUT inputs/reports/TDC_HEPATOCYTE_SPECIES_AUDIT.md -->

Source: `inputs/reports/TDC_HEPATOCYTE_SPECIES_AUDIT.md`  
SHA-256 of exact source bytes: `7141f6d8dca86a093f34906b4ed016ab0451793eda1e2cf200fb14776e6f21db`  
Origin: 4640ea721204771979e5637e81217f59c65318e6

# TDC hepatocyte species audit

```json
{
  "INFERRED": {
    "claim_status": "REPRODUCED",
    "decision_rule": "REPRODUCED requires both rat-only and human-only structure matches with exactly matching numeric source labels. PARTIALLY_REPRODUCED requires label-specific matches to both species without both exclusive structural witnesses; otherwise NOT_REPRODUCED. Censored matches identify numeric boundaries only.",
    "strict_duplicate_pair_rule": "Exactly two TDC rows with different numeric labels: one has exactly one strict structure/value-matching rat record and no human value match; the other has exactly one strict structure/value-matching human record and no rat value match. Numeric agreement uses exact Decimal equality."
  },
  "OBSERVED": {
    "duplicate_label_groups": {
      "different": 193
    },
    "duplicate_trace_groups": {
      "distinct_labels_match_rat_and_human": 187,
      "no_strict_structural_match_to_either_assay": 6
    },
    "numeric_label_match_row_counts": {
      "both": 31,
      "human_only": 370,
      "rat_only": 796,
      "unresolved": 16
    },
    "row_counts": {
      "ambiguous_unparseable": 0,
      "both": 405,
      "human_only": 183,
      "neither": 16,
      "rat_only": 609
    },
    "secondary_id_duplicate_trace_groups": {
      "distinct_labels_match_rat_and_human": 190,
      "partial_or_unresolved": 3
    },
    "secondary_id_numeric_label_match_row_counts": {
      "both": 31,
      "human_only": 373,
      "rat_only": 801,
      "unresolved": 8
    },
    "unique_valid_structure_counts": {
      "ambiguous_unparseable": 0,
      "both": 218,
      "human_only": 183,
      "neither": 10,
      "rat_only": 609
    }
  },
  "UNRESOLVED": "Historical lineage cannot be proven by equality alone. A shared structure/label can map to both species; retain ambiguity. Species uses ChEMBL assay organism/taxonomy, never target magnitude. Secondary exact molecule-ID plus numeric-value matching is explicitly separate and never upgrades the strict structural matches."
}
```

INFERRED: Identity rule: RDKit 2025.03.6 sanitized isomeric canonical SMILES; stereochemistry, isotopes, charge and all disconnected fragments retained. No parent selection, desalting, neutralization, tautomer normalization or stereo removal. RDKit ordinary explicit-H handling applies. Equality is string equality of valid keys; missing/invalid structures never match. Identity is representation-specific, not proof of sample identity.

OBSERVED: Row evidence is in `../data/interim/TDC_HEPATOCYTE_SPECIES_ROWS.csv`; repeated-structure evidence is in `../data/interim/TDC_HEPATOCYTE_DUPLICATE_LABELS.json`. Numeric matching retains source censor relations and does not assign species from label magnitude.


<!-- END INPUT inputs/reports/TDC_HEPATOCYTE_SPECIES_AUDIT.md -->


---
<!-- BEGIN INPUT inputs/reports/NULL_RELATION_FIELD_AUDIT.md -->

Source: `inputs/reports/NULL_RELATION_FIELD_AUDIT.md`  
SHA-256 of exact source bytes: `884d36e6bf4ea070774168229648cf9ec55c642789017d6f877a5b7cf8e187b8`  
Origin: a5473ad0e9496d951712bbb24d5bfdb663002c5e

# NULL relation field audit

**INFERRED verdict: REMAINS_AMBIGUOUS**, specifically for CHEMBL3301370, CHEMBL3301371 and CHEMBL3301372.

## Scope and retained fields

OBSERVED: Primary evidence is the immutable downloaded ChEMBL 37 activity pages at `4640ea721204771979e5637e81217f59c65318e6`. All 18 acquired raw files passed the frozen manifest hash/size checks before and after this audit; receipts and manifest match that commit. The four activity pages contain 2,347 records. Completeness concerns this downloaded API state, not a historical ChEMBL release.

OBSERVED: Every requested activity field is retained in every record. The companion [JSON](NULL_RELATION_FIELD_AUDIT.json) extracts every record with its exact strings/nulls, source filename and 1-based position within the page. It includes all source/document IDs supplied by the API: document_chembl_id, src_id, record_id and toid, plus assay-level aidx/src_assay_id. No requested activity field was silently substituted or fetched.

OBSERVED: All activities identify document CHEMBL3301361 and src_id 27. document_journal, document_year and toid are NULL. The separate document record, original depositor activity table, compound-record source IDs and document DOI/PubMed identifiers were not acquired; their absence limits historical interpretation.

Method: standard-library JSON/Decimal field inspection only. No audit.py/chemistry imports, descriptors, preprocessing, splits or modelling. NULL is an explicit category, distinct from an absent field, empty string and `=`. Numeric equality is exact Decimal equality; source value strings are preserved.

## Raw relation versus standard_relation

OBSERVED: Rows are raw `relation`; columns are `standard_relation`. Zero cells are shown, including `=`. No other relation category occurs.

### CHEMBL3301370

| raw / standard | < | > | = | NULL |
| --- | --- | --- | --- | --- |
| < | 274 | 0 | 0 | 0 |
| > | 0 | 84 | 0 | 0 |
| = | 0 | 0 | 0 | 0 |
| NULL | 0 | 0 | 0 | 744 |

### CHEMBL3301371

| raw / standard | < | > | = | NULL |
| --- | --- | --- | --- | --- |
| < | 115 | 0 | 0 | 0 |
| > | 0 | 127 | 0 | 0 |
| = | 0 | 0 | 0 | 0 |
| NULL | 0 | 0 | 0 | 595 |

### CHEMBL3301372

| raw / standard | < | > | = | NULL |
| --- | --- | --- | --- | --- |
| < | 104 | 0 | 0 | 0 |
| > | 0 | 15 | 0 | 0 |
| = | 0 | 0 | 0 | 0 |
| NULL | 0 | 0 | 0 | 289 |

OBSERVED: All NULL standard_relation rows also have NULL relation. Raw `=` to standard NULL: **0**. Raw NULL to standard `=`: **0**. Explicit `<` and `>` agree in all records. There are no raw or standard explicit equals records in any assay.

## standard_flag

OBSERVED: Counts below use standard_relation classes; the raw-relation counts are identical.

| Assay | Relation | flag 1 | flag 0 | flag NULL / other |
| --- | --- | --- | --- | --- |
| CHEMBL3301370 | < | 274 | 0 | 0 |
| CHEMBL3301370 | > | 84 | 0 | 0 |
| CHEMBL3301370 | NULL | 744 | 0 | 0 |
| CHEMBL3301371 | < | 115 | 0 | 0 |
| CHEMBL3301371 | > | 127 | 0 | 0 |
| CHEMBL3301371 | NULL | 595 | 0 | 0 |
| CHEMBL3301372 | < | 104 | 0 | 0 |
| CHEMBL3301372 | > | 15 | 0 | 0 |
| CHEMBL3301372 | NULL | 289 | 0 | 0 |

DOCUMENTED: In the [ChEMBL 37 schema](https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/schema_documentation.txt), standard_flag distinguishes curated/set standard columns (1) from columns defaulting to published data (0). Relation columns store constraint symbols and permit NULL. The definition does not make flag 1 an assertion of exactness, reliability or lack of censoring.

INFERRED: Because flag 1 occurs in every relation class, it cannot distinguish censored from uncensored rows here.

## Hidden qualification and qualitative results

OBSERVED: Each of activity_comment, data_validity_comment, text_value and standard_text_value is JSON NULL in every row, including all explicitly qualified comparison rows. For each field separately:

| Assay | Relation | NULL count per field | Non-empty distinct values / frequencies |
| --- | --- | --- | --- |
| CHEMBL3301370 | < | 274 | None (0) |
| CHEMBL3301370 | > | 84 | None (0) |
| CHEMBL3301370 | NULL | 744 | None (0) |
| CHEMBL3301371 | < | 115 | None (0) |
| CHEMBL3301371 | > | 127 | None (0) |
| CHEMBL3301371 | NULL | 595 | None (0) |
| CHEMBL3301372 | < | 104 | None (0) |
| CHEMBL3301372 | > | 15 | None (0) |
| CHEMBL3301372 | NULL | 289 | None (0) |

OBSERVED: Exhaustive distinct-value enumeration therefore yields no `<`, `>`, lower/upper-bound, below/above-range, failure, unreliable, not-determined/NA or qualitative-outcome text in these fields. No keyword-only filter was used: every distinct non-empty value would have been retained. The JSON reports full field frequencies separately by assay and class. data_validity_description, upper_value and standard_upper_value are also NULL throughout; activity_properties is an empty list and potential_duplicate is 0 throughout.

DOCUMENTED: The [ChEMBL FAQ](https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/chembl-data-questions) explains validity flags and depositor qualitative comments. Their absence here is not a documented guarantee of reliability or uncensored measurement.

## Boundary-value enumeration

OBSERVED: The following counts apply **independently to both value and standard_value**; their complete enumerations agree. Cells count stored numerical values, not unknown true clearance. The JSON enumerates activity IDs for every bucket crossed with both raw and standard relations, including all zero combinations.

| Assay | Raw relation | Standard relation | Below 3 | Exactly 3 | 3 < value < 150 | Exactly 150 | Above 150 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CHEMBL3301370 | < | < | 0 | 274 | 0 | 0 | 0 |
| CHEMBL3301370 | > | > | 0 | 0 | 0 | 84 | 0 |
| CHEMBL3301370 | NULL | NULL | 0 | 13 | 731 | 0 | 0 |
| CHEMBL3301371 | < | < | 0 | 115 | 0 | 0 | 0 |
| CHEMBL3301371 | > | > | 0 | 0 | 0 | 127 | 0 |
| CHEMBL3301371 | NULL | NULL | 0 | 2 | 593 | 0 | 0 |
| CHEMBL3301372 | < | < | 0 | 104 | 0 | 0 | 0 |
| CHEMBL3301372 | > | > | 0 | 0 | 0 | 15 | 0 |
| CHEMBL3301372 | NULL | NULL | 0 | 0 | 289 | 0 | 0 |

OBSERVED: All values are numeric. NULL-at-3 counts reproduce **13 / 2 / 0** for human microsome / rat hepatocyte / human hepatocyte. NULL-at-150 counts are **0 / 0 / 0**. No stored numeric value is below 3 or above 150 in either field. Explicit `<3` and `>150` records still represent inequalities; these checks do not erase them.

### Individual NULL-at-3 records

| Assay | activity_id | molecule_chembl_id | value | standard_value | raw / standard relation | flag |
| --- | --- | --- | --- | --- | --- | --- |
| CHEMBL3301370 | 14769802 | CHEMBL70972 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769803 | CHEMBL271012 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769804 | CHEMBL383322 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769805 | CHEMBL552512 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769806 | CHEMBL2171047 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769807 | CHEMBL2208431 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769808 | CHEMBL1917448 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769809 | CHEMBL119385 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769810 | CHEMBL2031229 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769811 | CHEMBL1917445 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769812 | CHEMBL452273 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769813 | CHEMBL390191 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769814 | CHEMBL1529362 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301371 | 14768823 | CHEMBL589973 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301371 | 14768825 | CHEMBL364714 | 3.0 | 3.0 | NULL / NULL | 1 |

OBSERVED: Each of these 15 records was inspected individually: all four requested comment/text fields and both upper-value fields are NULL; potential_duplicate is 0; document is CHEMBL3301361; src_id is 27. Their exact record_id, file location, units and additional retained fields are listed per record in the JSON. HLM uses microL/min/mg -> mL.min-1.g-1; rat uses microL/min/1E6 cells -> uL.min-1.(10^6cells)-1.

UNRESOLVED: A stored value of 3.0 with NULL relation cannot distinguish an exact observation from rounding, a reporting floor or an omitted qualifier. No censor category is assigned from value alone.

## Raw versus standard value, units and precision

| Assay | Relation | Rows | Exact numeric matches | Different value strings | Different decimal precision | Raw units -> standard units |
| --- | --- | --- | --- | --- | --- | --- |
| CHEMBL3301370 | < | 274 | 274 | 0 | 0 | microL/min/mg -> mL.min-1.g-1 (274) |
| CHEMBL3301370 | > | 84 | 84 | 0 | 0 | microL/min/mg -> mL.min-1.g-1 (84) |
| CHEMBL3301370 | NULL | 744 | 744 | 0 | 0 | microL/min/mg -> mL.min-1.g-1 (744) |
| CHEMBL3301371 | < | 115 | 115 | 0 | 0 | microL/min/1E6 cells -> uL.min-1.(10^6cells)-1 (115) |
| CHEMBL3301371 | > | 127 | 127 | 0 | 0 | microL/min/1E6 cells -> uL.min-1.(10^6cells)-1 (127) |
| CHEMBL3301371 | NULL | 595 | 595 | 0 | 0 | microL/min/1E6 cells -> uL.min-1.(10^6cells)-1 (595) |
| CHEMBL3301372 | < | 104 | 104 | 0 | 0 | microL/min/1E6 cells -> uL.min-1.(10^6cells)-1 (104) |
| CHEMBL3301372 | > | 15 | 15 | 0 | 0 | microL/min/1E6 cells -> uL.min-1.(10^6cells)-1 (15) |
| CHEMBL3301372 | NULL | 289 | 289 | 0 | 0 | microL/min/1E6 cells -> uL.min-1.(10^6cells)-1 (289) |

OBSERVED: Raw value strings and standard value strings are identical for every row; no precision change is visible in the API fields. Type changes from CLint to CL for every row. Units have different strings in each assay, with the same change across NULL, `<` and `>` classes.

INFERRED (unit algebra): microL/min/mg and mL/min/g have the same numeric scale; the hepatocyte change is a spelling change for microlitres/minute per million cells. No numerical rescaling or rounding is apparent between these two API fields. This does not recover laboratory precision before deposition.

INFERRED: Nothing in the observed type/unit/value changes explains missing relations: raw relation is already NULL, and supplied inequalities survive the same standardisation. Upstream omission or ingestion history remains UNRESOLVED.

## Supplementary same-document check

OBSERVED: The acquired corpus and workspace search yielded only these three quantitative assays for CHEMBL3301361, their derived copies and audit reports. No local ChEMBL database dump or unrelated endpoint activity records were found. Search scope and exclusions are recorded in the JSON.

UNRESOLVED: Systematic NULL use elsewhere in the deposition, preservation of inequalities elsewhere, and patterns across LogD, solubility, pKa or protein binding cannot be assessed from the local evidence. **This supplementary check stops here because additional acquisition would be required.** No additional activity, assay or document dataset was downloaded.

## Documented definitions and limits

DOCUMENTED: [ChEMBL 37 schema](https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/schema_documentation.txt) defines raw relation/value/units as the source-dataset fields and standard fields as their standardised counterparts. The schema permits nullable relation columns but supplies no NULL-means-equals convention. The documentation was read on 2026-09-17 (96,496 bytes; SHA-256 `170021a58a6d8c09ca088eae5ee75c9b9d0b3b457c6428adf63986b9d765f9fb`); no raw dataset was replaced.

DOCUMENTED: The [current ChEMBL deposition guide](https://chembl.gitbook.io/chembl-data-deposition-guide/file-structure/field-names-and-data-types-minimal-data-submission/activity.tsv) requires a relation with numeric VALUE submissions and directs NA outcomes to TEXT_VALUE. That guidance does not define the meaning of NULL in this older AstraZeneca deposition. It cannot retrospectively establish an equals convention or prove that these rows are invalid.

## Evidence resolution

INFERRED: These three assays show a consistent distinction between explicit inequalities and numeric records without a recorded qualifier. This supports an unqualified-numeric interpretation and argues against loss of an equals sign specifically between the retained raw and standard fields.

UNRESOLVED: Unqualified numeric storage is not proof of an uncensored assay observation. Neither standard_flag=1, empty comments nor unchanged numeric strings establishes the missing historical convention. The 15 NULL-at-3 records remain individually unresolved, and unrelated same-document endpoints are unavailable. The evidence does not justify recoding NULL to equals.

Scope: This verdict concerns only these three assays in the frozen ChEMBL 37 API acquisition, not ChEMBL globally.

REMAINS_AMBIGUOUS


<!-- END INPUT inputs/reports/NULL_RELATION_FIELD_AUDIT.md -->


---
<!-- BEGIN INPUT inputs/reports/NULL_RELATION_RANGE_CHECK.md -->

Source: `inputs/reports/NULL_RELATION_RANGE_CHECK.md`  
SHA-256 of exact source bytes: `1857f140a3bed81822e43f034c61a4e83a022723035e344bfb07e7046d3ac4d8`  
Origin: working-tree snapshot; uncommitted

# NULL relation range check

Date: 2026-09-18. Evidence resolution only.

OBSERVED: Recomputed directly from the four existing ChEMBL 37 activity JSON pages under `../data/raw/chembl/`, with SHA-256 and byte sizes verified against the frozen source manifest. Selection requires both `relation` and `standard_relation` to be JSON NULL. Values are compared using exact Decimal arithmetic; no rounding, binning or data transformation was applied.

## NULL-relation ranges

OBSERVED: All counts below refer to stored `standard_value`, not an inferred true clearance. HLM standard units are `mL.min-1.g-1`; both hepatocyte assays use `uL.min-1.(10^6cells)-1`.

| Assay | N | Minimum | Maximum | <3 | =3 | Strictly >3 and <150 | =150 | >150 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CHEMBL3301370 | 744 | 3.0 | 146.0 | 0 | 13 | 731 | 0 | 0 |
| CHEMBL3301371 | 595 | 3.0 | 149.0 | 0 | 2 | 593 | 0 | 0 |
| CHEMBL3301372 | 289 | 3.2 | 134.9 | 0 | 0 | 289 | 0 | 0 |

OBSERVED: **No NULL-relation records occur outside [3,150] in any of the three assays**, so there are no out-of-range activity IDs, molecule IDs or values to enumerate. **There are no NULL-at-150 records in any assay.**

## Exact frequencies from 3 through 10 inclusive

OBSERVED: Each assay column pair is independently sorted by numeric value; adjacent assay entries do not denote matched records. Only observed unique values are listed, with their exact row counts. A dash marks the end of a list, not a missing source value. No bins are used.

| Assay | Rows in [3,10] | Distinct numeric values |
| --- | --- | --- |
| CHEMBL3301370 | 224 | 60 |
| CHEMBL3301371 | 126 | 55 |
| CHEMBL3301372 | 112 | 65 |

| HLM 3301370 value | Count | Rat 3301371 value | Count | Human 3301372 value | Count |
| --- | --- | --- | --- | --- | --- |
| 3.0 | 13 | 3.0 | 2 | 3.2 | 1 |
| 3.02 | 1 | 3.09 | 1 | 3.24 | 1 |
| 3.31 | 1 | 3.16 | 1 | 3.3 | 1 |
| 3.6 | 1 | 3.24 | 1 | 3.31 | 3 |
| 3.9 | 1 | 3.31 | 1 | 3.39 | 1 |
| 3.98 | 2 | 3.39 | 3 | 3.4 | 1 |
| 4.0 | 22 | 3.63 | 1 | 3.46 | 1 |
| 4.07 | 1 | 3.8 | 1 | 3.47 | 2 |
| 4.17 | 3 | 3.87 | 1 | 3.55 | 1 |
| 4.2 | 1 | 4.0 | 7 | 3.72 | 3 |
| 4.47 | 1 | 4.17 | 2 | 3.8 | 1 |
| 4.57 | 1 | 4.24 | 1 | 3.81 | 1 |
| 4.7 | 1 | 4.37 | 1 | 3.89 | 1 |
| 4.79 | 1 | 4.68 | 1 | 3.91 | 1 |
| 4.9 | 1 | 4.79 | 3 | 3.98 | 3 |
| 5.0 | 22 | 5.0 | 7 | 4.04 | 1 |
| 5.13 | 2 | 5.01 | 2 | 4.17 | 1 |
| 5.25 | 3 | 5.13 | 4 | 4.27 | 2 |
| 5.37 | 2 | 5.25 | 2 | 4.46 | 1 |
| 5.5 | 5 | 5.29 | 1 | 4.47 | 2 |
| 5.6 | 1 | 5.37 | 1 | 4.57 | 3 |
| 5.75 | 3 | 5.5 | 2 | 4.68 | 2 |
| 6.0 | 23 | 5.75 | 1 | 4.7 | 1 |
| 6.03 | 1 | 5.79 | 1 | 4.76 | 1 |
| 6.17 | 2 | 6.0 | 8 | 4.79 | 3 |
| 6.18 | 1 | 6.17 | 3 | 4.88 | 1 |
| 6.31 | 4 | 6.31 | 3 | 4.9 | 2 |
| 6.33 | 1 | 6.61 | 2 | 4.92 | 1 |
| 6.46 | 1 | 6.76 | 2 | 5.01 | 1 |
| 6.5 | 1 | 6.92 | 2 | 5.05 | 1 |
| 6.61 | 1 | 7.0 | 6 | 5.13 | 1 |
| 6.67 | 1 | 7.08 | 1 | 5.16 | 1 |
| 6.76 | 1 | 7.11 | 1 | 5.17 | 1 |
| 6.92 | 3 | 7.2 | 1 | 5.25 | 3 |
| 7.0 | 19 | 7.24 | 1 | 5.37 | 2 |
| 7.08 | 1 | 7.33 | 1 | 5.5 | 1 |
| 7.24 | 1 | 7.48 | 1 | 5.62 | 2 |
| 7.41 | 3 | 7.59 | 1 | 5.75 | 3 |
| 7.5 | 3 | 7.94 | 2 | 5.88 | 1 |
| 7.59 | 2 | 8.0 | 9 | 6.0 | 3 |
| 7.76 | 2 | 8.13 | 2 | 6.17 | 2 |
| 7.94 | 2 | 8.51 | 2 | 6.31 | 3 |
| 8.0 | 13 | 8.71 | 2 | 6.46 | 2 |
| 8.13 | 1 | 8.91 | 1 | 6.61 | 2 |
| 8.28 | 1 | 9.0 | 5 | 6.76 | 2 |
| 8.32 | 2 | 9.01 | 1 | 6.92 | 2 |
| 8.33 | 1 | 9.12 | 2 | 6.99 | 1 |
| 8.5 | 3 | 9.33 | 1 | 7.0 | 1 |
| 8.51 | 1 | 9.55 | 2 | 7.08 | 2 |
| 8.67 | 1 | 9.77 | 4 | 7.24 | 1 |
| 8.71 | 2 | 9.8 | 1 | 7.41 | 2 |
| 8.86 | 1 | 9.88 | 1 | 7.59 | 3 |
| 8.91 | 2 | 9.9 | 1 | 7.76 | 3 |
| 9.0 | 16 | 9.95 | 1 | 7.9 | 1 |
| 9.12 | 2 | 10.0 | 8 | 7.94 | 2 |
| 9.33 | 1 | - | - | 8.13 | 1 |
| 9.5 | 1 | - | - | 8.51 | 3 |
| 9.55 | 1 | - | - | 8.7 | 1 |
| 9.77 | 3 | - | - | 8.71 | 2 |
| 10.0 | 10 | - | - | 8.91 | 1 |
| - | - | - | - | 9.12 | 4 |
| - | - | - | - | 9.33 | 2 |
| - | - | - | - | 9.5 | 1 |
| - | - | - | - | 9.77 | 2 |
| - | - | - | - | 10.0 | 3 |

## Primary human HLM: CHEMBL3301370

| Record class | Count |
| --- | --- |
| Both relations NULL; strictly inside (3,150) | 731 |
| Both relations NULL; exactly 3 | 13 |
| Both relations explicitly <; standard_value 3 | 274 |
| Both relations explicitly >; standard_value 150 | 84 |

OBSERVED: These four classes sum to all 1,102 HLM activity records. The explicitly qualified records represent `<3` and `>150`; they are separate from NULL-relation rows.

UNRESOLVED: These ranges and frequency distributions do not establish clipping, reporting-limit treatment or uncensored semantics. NULL is not reinterpreted as equals. The existing audit conclusions, including `REMAINS_AMBIGUOUS`, are unchanged. No raw data, preprocessing outputs, splits or models were modified.


<!-- END INPUT inputs/reports/NULL_RELATION_RANGE_CHECK.md -->


---
<!-- BEGIN INPUT inputs/reports/HLM_HH_QUALIFIER_CROSSTAB.md -->

Source: `inputs/reports/HLM_HH_QUALIFIER_CROSSTAB.md`  
SHA-256 of exact source bytes: `be877677f147e220e3b8a6cb2785fc32c18c2664ff8dbcd5b6da5ad14b5c89fc`  
Origin: working-tree snapshot; uncommitted

# HLM-HH qualifier cross-tabulation

OBSERVED: 187 compounds shared by CHEMBL3301370 (human HLM) and CHEMBL3301372 (human hepatocyte), using the frozen audit at `4640ea7`. Qualifiers and values were read from the immutable ChEMBL 37 raw pages; SHA-256 and sizes match the source manifest. Existing canonical keys and pair membership were verified against the frozen commit. No new structural calculation was performed.

## Status definitions

| Status | Operational rule |
| --- | --- |
| INTERIOR_OBSERVED | Both raw and standard relation NULL; 3 < standard_value < 150 |
| BOUNDARY_AMBIGUOUS | Both raw and standard relation NULL; standard_value equals 3 or 150 |
| LEFT_CENSORED | Both relations <; standard_value equals 3 |
| RIGHT_CENSORED | Both relations >; standard_value equals 150 |

UNRESOLVED: `INTERIOR_OBSERVED` is the requested operational status name. It does not assert that NULL means equals or resolve uncensored semantics. Existing scientific audit conclusions are unchanged. Raw and standardised qualifiers and numeric values agree for every paired record.

## Full 4 x 4 matrix

OBSERVED: Rows are HLM status; columns are HH status. Every zero cell is retained.

| HLM / HH | INTERIOR_OBSERVED | BOUNDARY_AMBIGUOUS | LEFT_CENSORED | RIGHT_CENSORED |
| --- | --- | --- | --- | --- |
| INTERIOR_OBSERVED | 94 | 0 | 26 | 5 |
| BOUNDARY_AMBIGUOUS | 2 | 0 | 0 | 0 |
| LEFT_CENSORED | 20 | 0 | 31 | 0 |
| RIGHT_CENSORED | 8 | 0 | 0 | 1 |

| Pair class | N |
| --- | --- |
| Both INTERIOR_OBSERVED | 94 |
| One INTERIOR_OBSERVED and the other LEFT/RIGHT_CENSORED | 59 |
| Both LEFT/RIGHT_CENSORED | 32 |
| At least one BOUNDARY_AMBIGUOUS | 2 |
| Total | 187 |

OBSERVED: Of the 59 mixed interior/censored pairs, 31 have interior HLM and censored HH (26 left, 5 right), and 28 have censored HLM and interior HH (20 left, 8 right). Of the 32 both-censored pairs, 31 are left/left and 1 is right/right; none is left/right or right/left.

## Every boundary-ambiguous paired case

| Molecule ID | HLM activity ID | HLM value | HLM raw / standard relation | HH activity ID | HH value | HH raw / standard relation | HH status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CHEMBL271012 | 14769803 | 3.0 | NULL / NULL | 14763401 | 30.12 | NULL / NULL | INTERIOR_OBSERVED |
| CHEMBL552512 | 14769805 | 3.0 | NULL / NULL | 14758940 | 3.4 | NULL / NULL | INTERIOR_OBSERVED |

OBSERVED: Both ambiguous HLM records are exactly 3; there are no ambiguous HH records and no NULL-at-150 paired records. Native units are microL/min/mg for HLM and microL/min/1E6 cells for HH. Values are listed separately without subtracting, dividing or physiologically scaling them.

## Identity and quantitative eligibility

OBSERVED: The raw molecule-ID intersection and frozen strict canonical-structure intersection both contain exactly **187** members and identify the same compound pairs. Each assay contributes exactly one activity per matched ID and per matched structure. All 187 pairs match the frozen `PAIRED_HUMAN_COHORT.csv`; there are no extra, duplicate or ambiguous mappings.

OBSERVED: **94 pairs** have both assays strictly interior with NULL qualifiers. This is the eligible N for the proposed ordinary quantitative correlation under the requested interior-only policy; no correlation was calculated. Including the two HLM NULL-at-3 cases as exact 3 in the separately specified sensitivity would give 96 pairs, but they remain boundary-ambiguous in this cross-tab.

Machine-readable evidence: [HLM_HH_QUALIFIER_CROSSTAB.json](HLM_HH_QUALIFIER_CROSSTAB.json), including all 187 paired records, source locations, native units, the complete matrix and both boundary-ambiguous cases.


<!-- END INPUT inputs/reports/HLM_HH_QUALIFIER_CROSSTAB.md -->
