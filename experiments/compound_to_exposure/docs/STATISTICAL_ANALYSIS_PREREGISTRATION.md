# v2 Reanalysis Protocol: QSAR/DMPK HLM Intrinsic Clearance

## Scientific Question
Can the structural representation and baseline physicochemical properties of a compound reliably predict its intrinsic clearance in human liver microsomes (HLM) within a continuous, finite observable range, and to what extent does structural similarity govern prediction error?

## Primary Estimand
The primary estimand is the out-of-scaffold predictive absolute error for $\log_{10}$ reported apparent HLM CLint, conditional on membership of the primary interior cohort and the frozen pipeline/design. 

Formally, for pipeline $f$ trained on a scaffold-disjoint training set $\mathcal{T}$:
$$\theta(f) \;=\; \mathbb{E}\big[\,\lvert f(X) - \log_{10}\mathrm{CL_{int}} \rvert \;\big|\; X \in \text{cohort},\; g(X) \notin g(\mathcal{T})\,\big]$$
where $g(\cdot)$ is the frozen scaffold-group assignment. It is estimated by the MAE of the frozen selected pipeline on the scaffold holdout reserved from v2 tuning.

**Conditioning that may not be dropped when this estimand is quoted:**
*   It is conditional on **membership of the quantifiable-range cohort**, which is defined by a filter on the outcome. It is therefore *not* an estimate of error on an unscreened compound population, and must never be quoted as one. A compound's range membership is unknown before assay.
*   It is conditional on the frozen representation set, model set, hyperparameter grid and split design defined in this document. It is a property of **this pipeline under this evaluation design**, not of structural predictability in general.
*   It concerns **reported** HLM CLint. No claim is made about latent true clearance for censored compounds, and none about in-vivo clearance.

**Secondary estimands**, reported alongside and subject to the same conditioning: RMSE under the mean-constant baseline; the tail concordance statistics $C_L$ and $C_U$; and the decay of absolute error with nearest-neighbour structural similarity.

## Source-of-Truth / Superseded Documents
*   **Source of Truth Hierarchy:**
    1.  The explicit frozen decisions in the authoritative statistical planning prompt.
    2.  Verified audit reports, including the HLM-HH qualifier cross-tabulation.
    3.  `docs/ADVERSARIAL_PREREGISTRATION_REVIEW.md`.
    4.  `docs/DATASET_SELECTION_MEMO.md`.
    5.  `docs/CENSORING_POLICY_MEMO.md`.

*   **Disclosure regarding v1 analysis:** The historical v1 pre-performance preregistration is commit `fefaf21` (`fefaf215a1a0361470d039238bdf0178e3789410`). V1 modelling occurred afterward, and the underlying CHEMBL3301370 dataset was already analysed and v1 results existed before this v2 protocol was developed. This protocol defines the **primary prospective v2 reanalysis evaluation, reserved from v2 tuning**. The v2 holdout is not historically untouched and does not provide independent validation of v1. All v2 methodological decisions are frozen before any v2 model execution; no v2 model execution occurred during protocol preparation or this documentation freeze. The required pre-freeze evidence checks are complete.

*   **Superseded Decisions.** This document supersedes `docs/CENSORING_POLICY_MEMO.md` in the following respects:
    *   **Primary Cohort Reversal:** The memo explicitly rejected the assumption that `NULL` semantically meant equality, froze the inferred quantifiable-range cohort as all 744 null-relation records (731 interior + 13 boundary-ambiguous at exactly 3), defined the 731-record analysis as sensitivity analysis S1, and prohibited S1's promotion to primary. This SAP **reverses that assignment** for the new analysis: the primary point-regression cohort is now the 731 interior records, and the 13 boundary-ambiguous records are excluded from it and handled by sensitivity analyses.
    *   **Prospective nature:** This reversal is a prospective decision for the v2 reanalysis, drafted after v1 modelling had already occurred. However, the prohibition on choosing cohorts by performance remains preserved.
    *   **Classifier descoping (Review I3):** The memo froze a three-class assay-range classifier (BELOW / IN-RANGE / ABOVE, N=1,102) as Component 2. This preregistration descopes that component from v2 and records the descoping here explicitly.

**Correction of the record.** An earlier draft of this document falsely claimed that the older censoring memo assumed a ChEMBL `NULL` `standard_relation` means exact equality (`=`). It did not. The memo explicitly and bindingly refused that reading and designated the null-relation records an *inferred* quantifiable-range cohort under a dataset-specific working inference. This document adopts the same position: **NULL is not asserted to mean `=` in ChEMBL generally, here or anywhere in this project.**

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
*   **Deferred Benchmark:** TDC Clearance_Microsome_AZ, acquired standalone dataset N = 1,102. Benchmark execution is excluded from required v2 execution; existing acquisition and audit evidence is retained.

## Target Definition
The target is the base-10 logarithm of apparent intrinsic clearance, $\log_{10}(\text{CL}_{\text{int}})$.
The filter `3 < CLint < 150` is applied to the reported `standard_value` in µL/min/mg **before** the $\log_{10}$ transform, and the comparison is strict at both ends.

## Censoring Policy
*   The N = 731 observations with `NULL` standard relations strictly inside (3, 150) are treated as observed quantitative measurements under an assay-specific preregistered modelling assumption.
*   The values 3 and 150 are treated strictly as **working censoring boundaries**. Formal analytical LLOQ/ULOQ status remains UNRESOLVED.
*   No accuracy rule requires predictions at or beyond 3/150. Boundary values are not exact continuous labels.

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
**Descriptors and fingerprints are never concatenated in this reanalysis.** A concatenated block would be a third, unpreregistered representation mixing standardised continuous features with sparse binary ones under a single Ridge penalty.

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

*Note: The mean constant (P0b) is a metric-specific reference for RMSE, not an added learned candidate.*

### Selection rule (deterministic, fixed before any v2 performance is generated)
Selection uses **inner grouped-CV mean $\log_{10}$-MAE only** strictly among candidates P1 through P4 (P0a and P0b are strictly non-selected baselines). Applied in order, stopping at the first criterion that discriminates:
1. Lowest mean inner-CV $\log_{10}$-MAE.
2. If two candidates are within **0.001 $\log_{10}$ units**, prefer the simpler model family in the fixed order **Ridge < Random Forest**.
3. Still tied: prefer **R1 descriptors** over R2 Morgan.
4. Still tied: prefer the **more strongly regularised** setting — larger `alpha`; larger `min_samples_leaf`; then smaller `max_features`.
5. Still tied: lowest pipeline ID in the fixed lexicographic order P1 < P2 < P3 < P4.

### Holdout access rule (binding)
**Exactly one selected pipeline (from P1-P4), plus baselines P0a and P0b, are evaluated on the final holdout.** The non-selected pipelines are **never** evaluated on it. Their inner-CV results are reported in full; their holdout results do not exist. The holdout is touched **once**.

The holdout result is reported **whatever it shows**. Re-selection, metric substitution, grid extension, representation change and re-partitioning are all prohibited after the holdout is read. Evaluating sensitivity refits (Analyses A and B) on the holdout is explicitly distinguished from comparing alternative learned candidates.

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

**Partition dependence:** Scaffold identity and hash order are structure-derived. Numerical CLint magnitudes are not used for partition optimisation. In the holdout allocation, frozen N=731 cohort membership, which is target-derived, is used only to determine when whole-group accumulation reaches the prespecified 20% primary-cohort size. Step 5 also uses those same frozen membership counts for its prespecified CV fold-size balancing. Thus the complete partition is not a function of structure alone. These statements describe the existing algorithm and verified candidate assignment; they do not change either.

### Holdout proportion (frozen)
The target is **at least 20%** of the 731-cohort, assigned by whole scaffold groups using the unchanged algorithm above. The verified dry-run yields **149 primary holdout compounds (149/731 = 20.3830369357%)** in **84 primary-populated scaffold groups**. Across all 1,102 records, the same holdout contains **250 records in 116 scaffold groups**.

### Inner cross-validation (frozen)
**5-fold grouped CV over the primary CV pool of 582 compounds**, using the persisted fold column. Verified primary fold Ns for indices 0–4 are **115 / 120 / 115 / 117 / 115**; the corresponding all-record Ns are **172 / 170 / 162 / 184 / 164** (852 total). No scaffold group appears across holdout/CV partitions or across inner folds. All hyperparameter selection, representation selection and pipeline selection occur **entirely within this inner CV**.

### Seeds
The split needs none. Elsewhere `random_state = 0` is fixed for every stochastic estimator (`RandomForestRegressor`). Hyperparameter search is exhaustive grid search, so it needs no seed. The bootstrap seed is fixed at 0.

### One holdout plus grouped CV, not repeated scaffold splits
This is the design for the **primary prospective v2 reanalysis evaluation, reserved from v2 tuning**. Any random (non-scaffold) split may appear **only** as explicitly labelled exploratory comparison.

### Split characterisation, reported before modelling
The scaffold counts and deterministic dry-run are verified in `reports/SCAFFOLD_PREFREEZE_CHECK.md` and its JSON/CSV evidence, using RDKit 2025.03.6. The grouping and split algorithm above are unchanged.

| Verified statistic | All 1,102 HLM records | Primary 731 records |
|---|---:|---:|
| Unique scaffold groups | 712 | 532 |
| Singleton groups | 583 | 457 |
| Fraction of groups that are singletons | 0.8188202247191011 | 0.8590225563909775 |
| Compounds belonging to singleton groups | 583 | 457 |
| Largest scaffold-group size | 32 | 14 |
| `__ACYCLIC__` compounds | 1 | 1 |
| Fraction of compounds assigned to `__ACYCLIC__` | 0.0009074410163339383 | 0.0013679890560875513 |

The singleton fractions are **81.8820%** and **85.9023%** of groups, respectively, counted within each cohort. The largest full-data group is `c1ccc(-c2ccccc2)cc1` (32 records); the largest primary group is `O=C(Cc1ccccc1)NC1CCN(CCC(c2ccccc2)c2ccccc2)CC1` (14 records). The complete largest-20 lists are retained in the evidence report.

`__ACYCLIC__` contains exactly **one** compound, CHEMBL203125 (activity 14758924), an interior record. Its primary-cohort fraction is **0.136799%**, below 20%; it is **not a design blocker** and is not forced out of the holdout by the oversized-group rule. Hash ordering assigns it to CV fold 3. No group is oversized under either primary-record or all-record counting, and both interpretations yield the same verified assignment here. No scaffold group appears across holdout/CV partitions or across inner folds.

The high singleton fractions remain a limitation: scaffold-key disjointness alone does not establish fingerprint dissimilarity. Report that limitation for the primary prospective v2 reanalysis evaluation, reserved from v2 tuning.

### Completed ECFP4/Tanimoto pre-freeze characterisation
`reports/ECFP4_TANIMOTO_PREFREEZE_CHECK.md` and its JSON/CSV evidence complete the mandatory pre-freeze check using the unchanged candidate partition and frozen binary Morgan/ECFP4 fingerprint: radius 2, 2048 bits, `useChirality=False`. For each of the 149 primary holdout compounds, the reference pool contains all 582 primary CV compounds. The maximum Tanimoto per holdout compound has the following verified distribution (six decimal places):

| N | Minimum | Q1 | Median | Q3 | Maximum | Mean |
|---:|---:|---:|---:|---:|---:|---:|
| 149 | 0.173469 | 0.320513 | 0.520000 | 0.689655 | 1.000000 | 0.522820 |

| Frozen similarity bin | Count | Fraction |
|---|---:|---:|
| [0,0.2) | 1 | 0.006711409395973154 |
| [0.2,0.3) | 28 | 0.18791946308724833 |
| [0.3,0.4) | 24 | 0.1610738255033557 |
| [0.4,0.6) | 37 | 0.2483221476510067 |
| [0.6,1.0] | 59 | 0.3959731543624161 |

Exactly **two holdout compounds** have maximum Tanimoto **1.0**: CHEMBL1807827 against CV compound CHEMBL1807869, and CHEMBL1807829 against CV compound CHEMBL1807871. Each pair has distinct molecular structures and distinct frozen Bemis–Murcko scaffold keys. The frozen hashed fingerprint representation can coincide for structurally distinct molecules; **Tanimoto 1.0 does not establish molecular identity**. Pair activity IDs and scaffold keys are retained in the evidence report.

All **582 CV observations** have valid nearest-neighbour similarities calculated using only the other four frozen CV folds. No holdout/CV scaffold overlap or scaffold overlap between CV folds was found. The split is scaffold-disjoint, while fingerprint-space novelty varies substantially across holdout compounds; therefore the preregistered applicability-domain analysis remains necessary. The check reveals no factual contradiction with the frozen split/fingerprint specification. Neither the partition nor the methodology was altered in response to this distribution.

## Master Structural Partition
Exactly **one** partition governs every analysis on CHEMBL3301370. The procedure in *Split and Validation Strategy* operates over **all 1,102 records**, with structure-derived scaffold keys/order and the frozen cohort-membership counts described above. The verified candidate assignments are retained in `reports/SCAFFOLD_PREFREEZE_DRY_RUN_ASSIGNMENTS.csv` (SHA-256 `96bf97e5500b108c40883c13e3fc4b87c49b49c61b22357ec89cbfcec41d7a2e`). Those same assignments must be persisted to `splits/master_partition.csv` with a recorded SHA-256 before the first model fit; this is an implementation artifact, not permission to select or alter the candidate partition.

Columns: `chembl_id`, `canonical_smiles`, `scaffold_key`, `scaffold_group_id`, `partition` (`holdout` | `cv`), `cv_fold` (0–4, null for holdout), `cohort` (`interior_731` | `below_274` | `above_84` | `ambiguous_13`).

**Binding rules:**
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
    *   RMSE on the $\log_{10}$ scale. **Where RMSE is reported, it is compared against a constant predictor equal to the training-fold *mean*** (P0b), which is the RMSE-optimal constant.
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

### Stratification by scaffold novelty (Rigorously Resolved)
Under the strict grouped out-of-fold prediction (scaffold split), held-out censored compounds will *never* share a Bemis-Murcko scaffold with the training pool. Therefore, the "seen-scaffold" stratum is structurally impossible and must be empty by definition. Consequently, we report only the overall "unseen-scaffold" (out-of-scaffold) tail concordance. The seen/unseen stratification is structurally degenerate under this split design and is therefore omitted.

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
*   **No applicability-domain cutoff is declared in v2**, and no bin edge is moved after residuals are seen. The analysis describes how reliability decays; it does not certify a domain.

## Residual Diagnostics
Aimed at predictive failure and heteroscedasticity, not at distributional inference. No normality test is performed; **no test statistic or p-value is computed for residual distribution shape.** A QQ plot may be shown as a purely descriptive display and is not interpreted inferentially.

1.  Predicted vs observed, with the $y=x$ line.
2.  Residual vs predicted. (Residual defined as $y_{true} - y_{pred}$, signed).
3.  **Absolute** residual vs predicted, with prespecified tercile summaries — the heteroscedasticity check.
4.  **Boundary-compression check (prespecified, expected failure mode):** mean signed residual in the lowest and highest prediction terciles. A model trained on a target truncated to (3, 150) is expected to compress toward the centre, producing systematically positive residuals at the low end and negative at the high end. This is reported explicitly whether or not it appears.
5.  Residual vs nearest-neighbour Tanimoto (shared with the AD analysis).
6.  The **10 largest absolute residuals** listed with structures and scaffold groups, supporting the failure analysis that is this project's stated purpose.

## HLM–HH Secondary Analysis
Units differ (HLM µL/min/mg; HH µL/min/10⁶ cells). No raw ratio, no subtraction, no physiological scaling, no IVIVE. Microsomal CLint is never described as clinical clearance. Rank agreement only.

### Deterministic qualifier policy (frozen)
*   **Eligible paired set:** those of the 187 structural overlaps whose **HLM record belongs to the N=731 primary interior cohort** *and* whose **HH record belongs to the 289 null-relation HH records**. CHEMBL3301372 has zero null-relation records at 3 and zero at 150, so all 289 are interior and the HH side contributes no boundary ambiguity.
*   **Machine-verified cross-tab evidence**, from `reports/HLM_HH_QUALIFIER_CROSSTAB.md` and its CSV/JSON:
    *   187 total matched compounds
    *   94 interior-observed in both HLM and HH
    *   59 interior-observed in one assay and censored in the other
    *   32 censored in both assays
    *   2 boundary-ambiguous pairs
*   **The machine-verified eligible count for primary ordinary quantitative Spearman correlation is precisely the 94 interior/interior pairs.** No figure, table or sentence may imply that the correlation is computed over 187 compounds.
*   **Censored members are never ranked.** Report the complete verified 4×4 HLM-by-HH status table below; boundary-ambiguous records retain their own evidence category. The 59 interior/censored pairs comprise 26 HLM-interior/HH-left, 5 HLM-interior/HH-right, 20 HLM-left/HH-interior and 8 HLM-right/HH-interior pairs. The 32 censored/censored pairs comprise 31 left/left and one right/right pair; opposite-tail cells are zero.
*   **Boundary-ambiguous pairs:** The **primary** Spearman **excludes** them, consistent with the frozen N=731 primary cohort. A sensitivity Spearman including them as interior is reported beside it (N=96), mirroring Sensitivity Analysis A. **The choice between the two is not made on which correlation is stronger; the exclusive estimate is primary by prespecification and both are reported.**
*   Report Spearman $\rho$ with a 95% scaffold-cluster bootstrap interval and the eligible N.
*   **Mandatory caveat:** Restricting to in-range-in-both truncates variance in both variables. Review B12 asserted this makes $\rho$ a "conservative, downward-biased estimate". We identify this as an unsupported mathematical claim: range restriction attenuates correlation under specific bivariate normality assumptions, but does not guarantee a downward bias for Spearman rank correlation on arbitrary skewed subsets. We report the range restriction as a caveat, but do not present the downward-bias claim as established fact. It is never quoted as a general assay-agreement coefficient.

| HLM / HH | INTERIOR_OBSERVED | BOUNDARY_AMBIGUOUS | LEFT_CENSORED | RIGHT_CENSORED | Total |
|---|---:|---:|---:|---:|---:|
| INTERIOR_OBSERVED | 94 | 0 | 26 | 5 | 125 |
| BOUNDARY_AMBIGUOUS | 2 | 0 | 0 | 0 | 2 |
| LEFT_CENSORED | 20 | 0 | 31 | 0 | 51 |
| RIGHT_CENSORED | 8 | 0 | 0 | 1 | 9 |
| Total | 124 | 0 | 57 | 6 | 187 |

The classifications require agreement of raw and standard relation fields: INTERIOR_OBSERVED has both NULL and a value strictly inside (3,150); BOUNDARY_AMBIGUOUS has both NULL and a value exactly 3 or 150; LEFT_CENSORED has both `<` with reported bound 3; RIGHT_CENSORED has both `>` with reported bound 150. Raw and standard numeric values agree in these assays. The evidence labels do not assert that NULL semantically means equality.

The two boundary-ambiguous pairs are CHEMBL271012 (HLM activity 14769803, NULL 3.0; HH activity 14763401, NULL 30.12) and CHEMBL552512 (HLM activity 14769805, NULL 3.0; HH activity 14758940, NULL 3.4). Both HH records are interior. Including these two HLM values as exact 3 only for the prespecified sensitivity gives **Spearman N=96**; the primary remains **N=94**. Neither assay contains NULL-at-150 records. Molecule-ID matching and full canonical-structure matching identify the same **187 one-to-one pairs**, matching the frozen membership evidence.

## TDC Benchmark Reproduction — Deferred
**TDC_PROTOCOL_NOT_FULLY_SPECIFIED.** As established by `reports/TDC_PREFREEZE_CLOSURE.md`, the required benchmark-group `train_val.csv` and `test.csv` files are not currently available locally, the present execution environment is not compatible with a binding PyTDC 1.1.15 reproduction, and consequential caller settings remain unfrozen. TDC benchmark execution is therefore **deferred from the frozen v2 protocol**. **No TDC result is required for completion of the primary v2 science analysis.**

If TDC reproduction is later performed, it requires its own documented exploratory benchmark protocol frozen before that execution. That protocol must establish the exact package/runtime environment, group-data source and file hashes, API, supplied test membership, split procedure, split and estimator seeds, run count, representations, label handling, training/tuning/selection rules, metric implementation and aggregation/rounding rules. The package's documented five-seed example and aggregation facility do not supply these missing decisions. No execution is promised under an official harness in v2.

**Preserved provenance and separation (binding for any later benchmark):**
*   A later TDC benchmark uses its separately documented benchmark split, never the science master structural partition.
*   Any later TDC results remain separate from science-track results in tables and figures.
*   No TDC-derived choice — hyperparameter, representation or threshold — informs the science track, and no science-track result is quoted as a benchmark number or vice versa.
*   The acquired standalone TDC microsome artifact retains the corresponding boundary values as **bare numbers without `<`/`>` qualifiers**: 274 `<3` records correspond to 3 and 84 `>150` records correspond to 150, with the 13 NULL-at-3 records giving **287 values at exactly 3**. This qualifier stripping remains a provenance finding, not a science-track reinterpretation of censoring or NULL.
*   The five microsome structural mismatches remain documented: **four representation/tautomer cases with matching ID/value/InChIKey evidence and one hydrate/parent representation case**. The sources are not described as interchangeable. Findings about the acquired standalone artifact are not asserted for the unacquired group files.
*   Any later benchmark is reported solely for benchmark comparability, not as accuracy on uncensored experimental measurements or independent external validation of the overlapping AstraZeneca data.

## Biogen Replication
Within-dataset replication of the **modelling procedure**, never a pooled external test set. Both analyses below are **exploratory** and neither can change any conclusion of the primary prospective v2 reanalysis evaluation.

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
*   Both analyses strictly use the **master structural partition**, and describe what is refitted, evaluated and reported in each.
*   *Rule:* We will not choose between Analysis A and B based on downstream performance; both sets of metrics will be reported. We do not use sensitivity results to replace the primary result.

## Decision Criteria
### Primary comparison
$$\Delta \;=\; \mathrm{MAE}_{\log_{10}}(\text{P0a median baseline}) \;-\; \mathrm{MAE}_{\log_{10}}(\text{selected pipeline})$$
computed on the scaffold holdout reserved from v2 tuning. $\Delta > 0$ favours the model.

### Interval (frozen)
**Paired scaffold-cluster bootstrap.** Resample **scaffold groups** in the holdout with replacement — never individual compounds, which are dependent within a group — to $B = 10{,}000$ replicates, `seed = 0`. Both predictors are evaluated on the identical resample (paired). Report the **95% percentile interval** for $\Delta$, alongside both absolute MAEs and the realised holdout compound and group counts.

### Pre-specified conclusions
*   **Improvement demonstrated** iff the lower bound of the 95% interval for $\Delta$ exceeds 0.
*   **Improvement not demonstrated** otherwise. $\Delta$ and its interval are reported either way, with the same prominence.
*   **Statistical uncertainty, effect size and scientific usefulness are distinct.** Report $\Delta$ and its interval without assigning a utility classification. This v2 protocol contains **no validated utility threshold**. The two-fold band is used only to report agreement for individual predictions.
*   The same bootstrap procedure produces intervals for RMSE (against P0b), $C_L$, $C_U$ and the two-fold band proportion. No multiplicity adjustment is applied because **$\Delta$ is the sole primary inferential comparison in this prospective v2 reanalysis**; all other intervals are descriptive and are labelled as such.

## Failure Criteria
If $\Delta$'s 95% interval includes or lies below zero, the finding is stated exactly as:
> **Under this preregistration** — the 12 frozen RDKit descriptors and binary ECFP4 (r=2, 2048 bits, no chirality); Ridge and Random Forest with the frozen grids; the N=731 CHEMBL3301370 quantifiable-range cohort; and a single 20% Bemis–Murcko scaffold holdout with 5-fold grouped inner CV — **the selected pipeline did not demonstrate a detectable reduction in $\log_{10}$-MAE relative to a median-constant baseline on structurally novel compounds.**

Permitted accompanying statements: that the result is confounded with sample size, representation choice, grid coverage, scaffold-split severity and assay noise, which this design cannot separate. Structural novelty in the statement above means an unseen frozen scaffold key; it does not imply uniform novelty in fingerprint space. The pre-freeze similarity evidence establishes that this novelty varies substantially, including two holdout fingerprints with exact matches in the CV pool.

**Prohibited:** that structural representations do not predict intrinsic clearance; that QSAR fails on this endpoint; that the endpoint is unpredictable; any use of the word *falsified* for a hypothesis broader than the frozen pipeline, cohort and split named above; and any post-hoc addition of models or representations to rescue a null result.

## Primary Prospective V2 Reanalysis and Exploratory Analyses
*   **Primary prospective v2 reanalysis evaluation, reserved from v2 tuning:** The evaluation of the frozen, cross-validation-selected primary model on the scaffold holdout test set, with the underlying dataset's previous v1 analysis explicitly disclosed.
*   **Exploratory within the existing v2 scope:** Any random-split evaluations, the Biogen within-dataset replication, and post-hoc feature importance derivations. Their existing scope is unchanged.
*   **Deferred outside required v2 execution:** TDC benchmark reproduction requires a separate protocol frozen before its execution.

## Relationship to the Superseded Three-Class Classifier
`CENSORING_POLICY_MEMO.md` froze a three-class assay-range classifier (BELOW / IN-RANGE / ABOVE, N=1,102) as Component 2. This preregistration **descopes that component from v2** and records the descoping here explicitly. The consequence is stated as a limitation wherever the regression is reported: **the primary model is conditional on a compound already being known to fall in the quantifiable range, and this version supplies no model that predicts range membership.** The censored records are retained and used, but only through the ordering-based censor-aware evaluation. Reinstating a range classifier is deferred to a separately preregistered analysis.

## Reproducibility Requirements
*   Fixed random seeds where relevant.
*   Deterministic, persisted split assignments saved to disk via SHA-256 assignment.
*   Machine-readable configuration.
*   Hashes for derived datasets.
*   Saved model parameters.
*   Explicit logging of exact package versions. The existing science project pins are **RDKit 2025.03.6** (`rdkit==2025.3.6`) and **NumPy 2.2.6**; the scaffold evidence was generated with that RDKit version. Record scikit-learn and the complete execution environment before fitting. No package installation or environment change is part of this factual patch.
*   **The holdout evaluation is executed once and reported in full regardless of outcome; a null result is reported with the same prominence as a positive one.**

## Explicitly Deferred Questions
*   The formal analytical LLOQ/ULOQ status of the boundaries.
*   Physiological scaling to in vivo clearance.
*   Harmonization of the Biogen multicomponent structures and unspecified stereochemistry.
*   TDC benchmark reproduction, excluded from required v2 execution and subject to a separately frozen exploratory benchmark protocol.

---
## FROZEN_ANALYSIS_DECISIONS

| Parameter | Decision |
|---|---|
| Population | CHEMBL3301370 point-regression cohort, N=731 |
| Target | $\log_{10}$ apparent intrinsic clearance (µL/min/mg) |
| Representation | Frozen RDKit descriptors (12) OR frozen Morgan ECFP4 fingerprint (2048 bit, no chirality) |
| Model | Median baseline; Mean baseline; Ridge; Random Forest |
| Split | Unchanged whole-scaffold SHA-256 assignment with at least 20% target: realised holdout N=149 (20.3830369357%), reserved from v2 tuning; primary CV pool N=582 |
| Tuning | 5-fold grouped inner CV, primary fold Ns 115/120/115/117/115; exhaustive grid search over defined parameters |
| Primary Metric | Mean Absolute Error (MAE) on $\log_{10}$ scale |
| Baseline | Training-fold median |
| Censor-Aware Metric | Tail concordance ($C_L$, $C_U$) evaluated by ordering |
| Model-Selection Rule | Lowest inner-CV $\log_{10}$-MAE among P1-P4, with fixed hierarchy of tie-breakers (simpler -> descriptors -> regularised -> lexicographic) |
| Final Evaluation Rule | Exactly one selected pipeline plus median/mean baselines touch the holdout once |
| Uncertainty Procedure | Paired scaffold-cluster bootstrap (B=10,000) for 95% interval on difference |

The HLM–HH, scaffold and ECFP4/Tanimoto pre-freeze evidence requirements are complete. TDC reproduction is explicitly deferred outside required v2 execution. Formal LLOQ/ULOQ terminology remains unresolved without affecting the frozen working-boundary policy. No execution-blocking pre-freeze evidence item remains. This documentation freeze executes no v2 model or benchmark.

PREREGISTRATION_STATUS: FROZEN_FOR_V2_EXECUTION
