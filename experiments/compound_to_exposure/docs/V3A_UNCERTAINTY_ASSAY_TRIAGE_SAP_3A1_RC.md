# Statistical Analysis Plan (SAP) — v3A.1-RC
## Uncertainty-Aware Human Liver Microsomal (HLM) Assay Triage

**Document Status**: `RELEASE CANDIDATE — FROZEN SPECIFICATION — STRICTLY NO EXECUTION`  
**Protocol Version**: `v3A.1-RC`  
**Study Type / Terminology**: Prospectively specified retrospective reanalysis using scaffold-grouped out-of-fold evaluation  
**Date**: `2026-09-23`  
**Target Endpoint**: Human Liver Microsomal (HLM) Intrinsic Clearance ($CL_{\text{int}}$, $\mu\text{L/min/mg}$)  
**Target Variable**: $y = \log_{10}(CL_{\text{int}})$  
**Dataset**: ChEMBL Assay `CHEMBL3301370` (Parent Document `CHEMBL3301361`)  
**Primary Cohort**: $N = 744$ exact quantitative observations (`standard_relation IS NULL`, $3.0 \le CL_{\text{int}} < 150.0$)  
**Branch / Base Tree**: `audit/whole-cohort-structure-integrity`  

---

## 1. Study Framing, Status, and Terminology

### 1.1 Formal Study Classification
This study is classified as a **prospectively specified retrospective reanalysis using scaffold-grouped out-of-fold evaluation**.
- **Prospective Methodological Specification**: The scientific question, primary cohort eligibility, model architecture, representation schema, uncertainty metrics, evaluation operators, estimands, practical-utility criteria, and inference rules are frozen *prior* to executing analysis scripts or generating out-of-fold residuals.
- **Retrospective Data Context**: All chemical structures and assay clearance determinations were generated historically and deposited into public databases (ChEMBL 20 in 2015). Portions of this dataset have been previously inspected, cleaned, and modelled during historical project phases (v1 exploratory, v2 sealed reanalysis, and data integrity audits). Under no circumstances may this study be characterized as "prospective compound collection" or "novel experimental validation."

### 1.2 Non-Confirmatory Status of Historical v2 Holdout
The historical 149-compound v2 holdout cohort was extensively unblinded, audited, and analyzed during post-hoc forensics. 
- It possesses **no special confirmatory status** in v3A.
- It is recombined into the unified exact quantitative cohort ($N = 744$) to maximize statistical power and structural diversity across 5 outer scaffold folds.
- Any secondary reporting of performance on those 149 compounds must be designated as a post-hoc descriptive appendix (`HISTORICAL_V2_HOLDOUT_POST_HOC_DESCRIPTIVE`) and cannot serve as prospective validation.

---

## 2. Primary Scientific Question & Decision Architecture

### 2.1 The Decision Problem: Selective Prediction for Assay Triage
In standard QSAR benchmarking, models are evaluated across all test instances regardless of confidence. In operational drug discovery, computational ADME models function as **triage filters**: the objective is to deploy in silico predictions when confident, while **deferring** low-confidence compounds to wet-lab experimental HLM clearance assays.

The **primary scientific question** of study v3A is:

> **Can pre-prediction uncertainty from a fixed HLM clearance model identify compounds whose computational predictions should be deferred to experimental measurement?**

This is an operational selective-prediction and assay-triage question. It is **NOT**:
1. A QSAR leaderboard tournament across multiple learning algorithms;
2. A representation tournament comparing topological vs descriptor spaces;
3. A test of whether uncertainty monotonically correlates with test residuals;
4. A censoring correction study.

### 2.2 Operational Conceptual Workflow
```
                      [ Chemical Structure x ]
                                 │
                   ┌─────────────┴─────────────┐
                   ▼                           ▼
        [ Fixed Point Model f(x) ]    [ Primary Uncertainty Score u(x) ]
                   │                           │
          Point Prediction ŷ                   ▼
                   │                  Within-Fold Rank u(x)
                   │                  Is u(x) ≤ τ_κ(fold)?
                   │                 ┌────────┴────────┐
                   │               YES                NO
                   │                │                  │
                   ▼                │                  ▼
             [ Retained Set ] ◄─────┘           [ Deferred Set ]
        Autonomous In Silico Call            Route to Prospective Wet-Lab
          (Assessed at Risk R_κ)                 HLM Clearance Assay
```

### 2.3 Strict Retrospective Interpretation
Study v3A evaluates whether an uncertainty-guided deferral strategy *could* support future assay triage. It does **not** establish that experimental assays can already be safely bypassed for newly synthesized chemical series in an active project pipeline.

---

## 3. Primary Cohort Definition & Population Limitations

### 3.1 Primary Cohort Eligibility ($N = 744$) — HUMAN DECISION FROZEN
Following first-hand depositor clarification from Mark Wenlock (23 September 2026), the primary cohort for study v3A is frozen at:
$$\mathbf{N = 744\text{ Exact Quantitative Observations}}$$

Eligibility criteria:
- **Assay Record**: Target assay `CHEMBL3301370`.
- **Database Qualifier**: `standard_relation IS NULL`. The raw database column is preserved strictly as `NULL`; it is **never rewritten to `"="`**.
- **Numerical Range**: $3.0 \le CL_{\text{int}} < 150.0\text{ }\mu\text{L/min/mg}$.
- **Target Transformation**: $y_i = \log_{10}(CL_{\text{int}})$.

Cohort Composition:
- **Strict Interior ($3.0 < CL_{\text{int}} < 150.0$)**: $N = 731$ exact quantitative records.
- **Exact Lower Boundary ($CL_{\text{int}} == 3.0$)**: $N = 13$ exact quantitative records (`EXACT_QUANTITATIVE_BOUNDARY_LOW`).
- **Exact Upper Boundary ($CL_{\text{int}} == 150.0$)**: $N = 0$ records.

### 3.2 Explicit Exclusions
The following subsets of `CHEMBL3301370` are strictly excluded from v3A:
1. **Left-Censored Records ($N = 274$)**: `standard_relation == '<'` and reported value $3.0\text{ }\mu\text{L/min/mg}$.
2. **Right-Censored Records ($N = 84$)**: `standard_relation == '>'` and reported value $150.0\text{ }\mu\text{L/min/mg}$.
3. **Ambiguous Records ($N = 0$)**: There are zero unresolved relation records remaining in the repository.

### 3.3 Methodological Rationale & "Exact $\ne$ Error-Free"
- **Evaluation Necessity**: Selective prediction evaluation metrics (RMSE on retained sets, risk-coverage integrals, quantile widths) require continuous, uncensored numeric ground-truth labels. Including censored records would conflate predictive uncertainty with arbitrary boundary imputation.
- **Precision Decoupling**: Demonstrating that an observation is uncensored (`standard_relation IS NULL`) establishes **exact measurement semantics**, but does **not** imply zero experimental measurement error. As shown in AstraZeneca historical literature, clearance determinations near the lower dynamic boundary exhibit substantial experimental variability.

### 3.4 Population Limitations
v3A evaluates uncertainty performance **only among observed exact quantitative outcomes within the assay dynamic range**. It does **not** establish uncertainty behavior for:
1. Low-turnover compounds below assay detection ($CL_{\text{int}} < 3.0$);
2. High-clearance compounds above assay saturation ($CL_{\text{int}} > 150.0$);
3. The broader medicinal-chemistry discovery population (which is subject to substantial survival and design truncation).

The primary population is selected by observed endpoint status; it is free from ambiguous censored residuals, but **not free from endpoint-based selection effects**.

---

## 4. Fixed Point Predictor Architecture — HUMAN DECISION FROZEN

### 4.1 Single Primary Predictor
v3A deploys **one point predictor only**:
$$\mathbf{ECFP4\ Random\ Forest\ Regressor}$$

- **Feature Representation**: Morgan Fingerprint, radius = 2 (ECFP4 equivalent), 2,048 bits, binary bit presence, `useChirality=False`.
- **Engineering Rationale**: 
  1. Isolates uncertainty estimation without confounding from representation selection;
  2. ECFP4 was the exact topology representation executed in historical v2 Random Forest models;
  3. Prohibiting multi-representation tuning prevents v3A from collapsing into another representation contest.
- **Prohibition**: The 2,060-dimensional ECFP4 + R1 descriptor union is **strictly prohibited** as the primary predictor in v3A. It remains reserved for separate future exploratory representation work.

### 4.2 Frozen Random Forest Hyperparameters
The underlying regressor is instantiated with explicit, immutable parameters:
```python
RandomForestRegressor(
    n_estimators=500,
    criterion="squared_error",
    max_features="sqrt",
    min_samples_split=2,
    min_samples_leaf=2,
    max_depth=None,
    bootstrap=True,
    random_state=20260923
)
```
- All other parameters take explicit scikit-learn defaults that cannot alter scientific output (`n_jobs=-1`, `verbose=0`, `warm_start=False`, `ccp_alpha=0.0`).
- **No hyperparameter tuning is permitted.** This specification is a frozen engineering choice, not a retrospectively optimized configuration.
- Every uncertainty metric derived from trees, leaves, or kernel weights must use this exact forest instance.

---

## 5. Mandatory Representation-Routing & Pipeline Safeguards

To prevent recurrence of the representation-routing defect identified during historical audits, any script implementing v3A must execute the following automated validation assertions prior to fitting:

1. **Representation Enum Assertion**:
   The active representation name must strictly equal the immutable string:
   ```
   "ECFP4_2048_R2_BINARY_NOCHIRAL"
   ```
2. **Matrix Dimensionality Assertion**:
   The feature matrix $X$ must possess exact shape $(744, 2048)$ and dtype `uint8` or `float32`.
3. **Row-Key Alignment Assertion**:
   For every index $i \in \{0, \dots, 743\}$, assert exact 1:1 alignment between:
   $$X[i] \longleftrightarrow y[i] \longleftrightarrow \text{activity\_id}[i] \longleftrightarrow \text{chembl\_id}[i] \longleftrightarrow \text{scaffold\_key}[i]$$
4. **Pre-Fit Cryptographic Hashing**:
   Compute and assert SHA-256 hashes for:
   - Cohort manifest file (`CHEMBL3301370_exact744_manifest.csv`);
   - Computed feature matrix binary array;
   - Outer scaffold fold split assignment file (`V3A_OUTER_SCAFFOLD_FOLDS.csv`).
5. **Absolute Prohibition of Substring Routing**:
   Substring matching (such as `'r1' in pipeline_id` or `'morgan' in name`) is **strictly prohibited**. Feature generation and model passing must occur via explicit, statically typed pipeline objects. Any dimensionality or name mismatch must instantly abort execution.

---

## 6. Uncertainty Scoring Methodology

### 6.1 Primary Uncertainty Method — HUMAN DECISION FROZEN
The **single primary uncertainty score** is:
$$\mathbf{u_{\text{primary}}(x) = u_{\text{QRF80}}(x) = \hat{Q}_{0.90}(x) - \hat{Q}_{0.10}(x)}$$
The central 80% predictive-distribution width computed from the bootstrap-aware Random Forest kernel-weighted training outcomes:
- $\hat{F}(y \mid x) = \sum_{i \in \mathcal{D}_{\text{train}}} w_i(x) \cdot \mathbb{I}(y_i \le y)$
- $\hat{Q}_\tau(x) = \inf \{y \mid \hat{F}(y \mid x) \ge \tau\}$
- Direction: **Higher width denotes higher uncertainty / lower predicted reliability**.
- This is the sole primary method. v3A is not an open tournament among primary scores.

### 6.2 Prespecified Secondary Comparator Uncertainty Scores
Five secondary comparators are prespecified to evaluate distinct uncertainty hypotheses:

#### A. Chemical Familiarity (Topological Distance)
$$u_{\text{tanimoto}}(x) = 1.0 - \max_{j \in \mathcal{D}_{\text{train}}} \text{Tanimoto}(x, x_j)$$
Comparison molecules $x_j$ are strictly restricted to the corresponding outer training fold. (Mean distance to 5-NN may be reported descriptively, but does not form a primary test).

#### B. Physicochemical Familiarity (Property-Space Distance)
$$u_{\text{physchem}}(x) = \frac{1}{5} \sum_{j \in \text{kNN}_5(x)} \|z(x) - z(x_j)\|_2$$
Mean Euclidean distance to the 5 nearest outer-training compounds in standardized 12-descriptor space:
- Panel: `MolWt`, `MolLogP`, `MolMR`, `TPSA`, `HBD`, `HBA`, `NumRotatableBonds`, `RingCount`, `NumAromaticRings`, `NumAliphaticRings`, `FractionCSP3`, `HeavyAtomCount`.
- Standardization: `StandardScaler` fit strictly on outer-training descriptors only.
- *Clarification*: Scaling is applied solely to calculate this distance metric; the Random Forest point predictor itself does not use or require scaled descriptors.

#### C. Model Familiarity (Effective Sample Size)
$$N_{\text{eff}}(x) = \frac{1}{\sum_{i \in \mathcal{D}_{\text{train}}} w_i(x)^2}, \quad u_{\text{neff}}(x) = \frac{1}{N_{\text{eff}}(x)}$$
Inverted so that higher $u_{\text{neff}}$ denotes fewer effective training points and higher uncertainty.

#### D. Local Outcome Heterogeneity (Neighborhood Variance)
$$u_{\text{local}}(x) = \sqrt{\sum_{i \in \mathcal{D}_{\text{train}}} w_i(x) \big(y_i - \mu_w(x)\big)^2}, \quad \mu_w(x) = \sum_{i \in \mathcal{D}_{\text{train}}} w_i(x) y_i$$
Proximity-weighted standard deviation of training labels sharing leaf paths with $x$.

#### E. Simple Tree-Variance Baseline
$$u_{\text{tree\_sd}}(x) = \sqrt{\frac{1}{T} \sum_{t=1}^T \big(\hat{y}_t(x) - \bar{y}_{\text{tree}}(x)\big)^2}$$
Standard deviation across the 500 individual tree point predictions.

### 6.3 Explicit Method Exclusions
- Raw unweighted "leaf support" (count of unique training compounds sharing leaves) is **excluded**.
- Learned meta-models (logistic regression or gradient boosting fit on error labels) are **strictly excluded** from v3A.

### 6.4 Shared Mathematical Ancestry
> **CRITICAL STATISTICAL DISCLOSURE**:  
> Measures $u_{\text{neff}}$, $u_{\text{local}}$, and $u_{\text{QRF80}}$ are derived from the **identical Random Forest kernel weight vector $w(x)$**. They represent different mathematical functionals of the same local empirical data distribution, not independent biological or chemical lines of evidence. Their comparison is purely methodological.

---

## 7. QRF Bootstrap-Aware Weight-Recovery Validity Gate

Before QRF quantiles can enter scientific evaluation, the weight-recovery implementation must satisfy a formal mathematical validity gate accounting for bootstrap sampling mechanics.

### 7.1 Mathematical Invariant
For a forest of $T$ trees, let $m_{t, i}$ be the integer in-bag bootstrap multiplicity of training instance $i$ in tree $t$, and let $L_t(x)$ denote the set of training instances in the terminal leaf of tree $t$ reached by query $x$. The exact kernel weight is:
$$w_i(x) = \frac{1}{T} \sum_{t=1}^T \frac{m_{t, i} \cdot \mathbb{I}(i \in L_t(x))}{\sum_{j \in L_t(x)} m_{t, j}}$$

For every query compound $x$, the reconstructed weights must reproduce the exact scikit-learn point prediction and sum to unity:
$$\left| \sum_{i=1}^{N_{\text{train}}} w_i(x) \cdot y_i - \hat{f}_{\text{RF}}(x) \right| < 10^{-6}$$
$$\left| \sum_{i=1}^{N_{\text{train}}} w_i(x) - 1.0 \right| < 10^{-12}$$

### 7.2 Pre-Flight Validation Protocol
- Test weight reconstruction on synthetic data ($N=100, P=20$);
- Test on 50 training instances and 50 held-out instances from the actual dataset;
- If weight recovery fails:
  ```
  QRF_WEIGHT_RECOVERY_FAILED
  ```
  Execution must immediately halt. A naive implementation that ignores bootstrap multiplicity (e.g. `forest.apply(X)` with equal observation weighting) is strictly prohibited.

---

## 8. Outer Validation Architecture

### 8.1 5 Mutually Exclusive Outer Scaffold Folds
To evaluate out-of-fold generalisation under scaffold shift:
- The cohort ($N = 744$) is partitioned into **5 mutually exclusive outer folds** based on Bemis–Murcko scaffold keys (`scaffold_key`).
- Every compound appears as an evaluation instance in exactly **one** outer test fold.
- No scaffold cluster crosses between outer training and test sets.
- Repeated random splitting (e.g. repeated `GroupShuffleSplit`) is **prohibited** to prevent pseudo-replication.

### 8.2 Deterministic Allocation Algorithm
Scaffold fold generation must follow a deterministic greedy balancing procedure:
1. Identify all unique Bemis–Murcko scaffold groups and compute their compound counts;
2. Sort scaffold groups in descending order of compound count;
3. Break ties in group size using a deterministic SHA-256 hash of `scaffold_key + "_V3A_20260923"`;
4. Initialize 5 empty folds;
5. Greedily assign each scaffold group to the fold currently containing the fewest total compounds;
6. Break ties in current fold size by lowest fold index ($1 \dots 5$).

### 8.3 Invariant Split Persistence
- Folds are generated and persisted to `splits/V3A_OUTER_SCAFFOLD_FOLDS.csv` prior to model fitting.
- The split manifest is cryptographically hashed (SHA-256).
- Only fold sizes and scaffold counts may be reviewed during preflight. Inspecting fold outcome distributions to manually rebalance folds is strictly prohibited.

---

## 9. Within-Fold Risk–Coverage Construction (Cross-Fold Comparability Fix)

### 9.1 Prohibition of Global Cross-Fold Pooling
Raw uncertainty magnitudes generated by separately trained outer Random Forests are **not guaranteed to be numerically interchangeable**.
- **PROHIBITED**: Pooling all 744 raw out-of-fold uncertainty values into a single global vector and applying one global quantile threshold.
- **MANDATED**: **Within-fold independent ranking at every coverage level**.

### 9.2 Within-Fold Retention Protocol
For each outer test fold $f \in \{1, \dots, 5\}$ containing $n_f$ compounds (where $\sum_{f=1}^5 n_f = 744$):
1. Specify target coverage $\kappa \in \{1.00, 0.90, 0.80, 0.70, 0.60, 0.50\}$;
2. Determine the exact number of compounds to retain in fold $f$:
   $$k_f(\kappa) = \lceil \kappa \cdot n_f \rceil$$
3. Sort compounds in fold $f$ in ascending order of their within-fold uncertainty score $u(x)$;
4. Retain the lowest $k_f(\kappa)$ compounds to form retained fold subset $S_{f, \kappa}$;
5. Combine retained compounds across all 5 folds:
   $$S_\kappa = \bigcup_{f=1}^5 S_{f, \kappa}, \quad |S_\kappa| = \sum_{f=1}^5 k_f(\kappa)$$
6. Compute the pooled retained-set Root Mean Squared Error:
   $$\text{RMSE}(\kappa) = \sqrt{\frac{1}{|S_\kappa|} \sum_{i \in S_\kappa} (y_i - \hat{y}_i)^2}$$

### 9.3 Deterministic Tie-Breaking Rule
If two or more compounds in fold $f$ possess identical uncertainty scores at the retention boundary:
- Outcome values $y_i$ or residuals must **never** be used to break ties;
- Break ties by ascending order of SHA-256 hash:
  $$\text{Hash}(\text{activity\_id}_i + \text{"\_V3A\_TIE\_20260923"})$$

---

## 10. Primary Estimand, Baseline Comparator, & Practical Criterion

### 10.1 Primary Operating Point
$$\mathbf{\kappa = 0.80\text{ (80\% Retained / 20\% Deferred to Wet-Lab Assay)}}$$

### 10.2 Primary Estimand: $\text{REL\_BENEFIT\_80}$
Let $\text{RMSE}_{\text{QRF80}}$ denote the pooled retained RMSE achieved by QRF 80% predictive width under within-fold ranking at $\kappa = 0.80$.

Let $\text{RMSE}_{\text{RANDOM80}}$ denote the expected pooled retained RMSE achieved by a matched within-fold random deferral strategy retaining the identical count $k_f(0.80)$ in every outer fold.

The **single primary estimand** is:
$$\mathbf{\text{REL\_BENEFIT\_80} = \frac{\text{RMSE}_{\text{RANDOM80}} - \text{RMSE}_{\text{QRF80}}}{\text{RMSE}_{\text{RANDOM80}}}}$$
- Direction: **Higher is better**.
- Interpretation: The percentage reduction in retained prediction error obtained by QRF-guided triage compared with an unguided random assay allocation at the same 20% experimental budget.

### 10.3 Empirical Random Deferral Comparator
- **Non-Linearity Correction**: Because RMSE involves a non-linear square root, expected RMSE under random subset removal is **not analytically constant**.
- **Empirical Baseline**: $\text{RMSE}_{\text{RANDOM80}}$ is estimated via **10,000 matched random within-fold simulations** (random seed `20260923`).
  - In each simulation $m$, draw $k_f(0.80)$ compounds uniformly at random without replacement from test fold $f$;
  - Pool across folds and compute $\text{RMSE}^{(m)}$;
  - $\text{RMSE}_{\text{RANDOM80}} = \frac{1}{10000} \sum_{m=1}^{10000} \text{RMSE}^{(m)}$.
  - Report Monte Carlo standard error to confirm convergence.

### 10.4 Practical Operational Threshold
The operational success criterion is frozen at:
$$\mathbf{\text{REL\_BENEFIT\_80} \;\ge\; 10.0\%}$$
- **Binding Statement**:
  > “The 10% threshold is a prospectively chosen operational criterion for this study; it is not claimed to be a validated biological or regulatory threshold.”
- *Removal of Unsupported Wording*: The previous draft rationale stating that 0.08 log10 corresponds to a 20% variance reduction is completely excised as unsupported.

---

## 11. Scaffold-Clustered Bootstrap Inference & Three-State Interpretation

### 11.1 Inferential Bootstrap Architecture
Because compounds sharing a Bemis–Murcko scaffold key exhibit correlated properties, statistical inference is performed via **scaffold-clustered bootstrap stratified by outer fold**:
- **Resampling Unit**: Unique Bemis–Murcko scaffold key;
- **Strata**: Outer test fold (resampling preserves outer-fold scaffold architecture);
- **Replicates**: $B = 10,000$ paired bootstrap draws;
- **Random Seed**: `20260923`;
- **Paired Resampling**: In each bootstrap draw $b$, resample scaffold clusters with replacement within each fold, pull all corresponding compounds, and evaluate both QRF and Random triage on the identical resampled cohort.
- **Confidence Interval**: 95% empirical percentile interval $[Q_{0.025}^*, Q_{0.975}^*]$.

### 11.2 Three-State Primary Conclusion Framework
To avoid conflating imprecise null findings with proof of inefficacy, the primary outcome is classified into one of three binding states:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   THREE-STATE PRIMARY INFERENCE FRAMEWORK                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ State 1: SUPPORTED_OPERATIONAL_SIGNAL                                       │
│ Criteria:                                                                   │
│   1. Point Estimate REL_BENEFIT_80 ≥ 10.0%                                  │
│   2. 95% Bootstrap CI Lower Bound > 0.0%                                    │
│ Conclusion: Uncertainty triage provides a statistically robust, practically │
│ meaningful error reduction over random deferral.                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ State 2: EVIDENCE_BELOW_PRACTICAL_THRESHOLD                                 │
│ Criterion:                                                                  │
│   1. 95% Bootstrap CI Upper Bound < 10.0%                                   │
│ Conclusion: Data provide statistically confident evidence that triage       │
│ utility falls below the operational practical utility threshold.            │
├─────────────────────────────────────────────────────────────────────────────┤
│ State 3: INCONCLUSIVE                                                       │
│ Criterion:                                                                  │
│   All other outcomes (CI spans across 10.0% with lower bound ≤ 0.0%, or     │
│   point estimate ≥ 10.0% but CI lower bound crosses 0.0%).                  │
│ Conclusion: Data lack statistical precision to accept or reject triage      │
│ utility under scaffold shift.                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

- **No Primary p-Value**: Hypothesis testing is governed by the 95% bootstrap interval relative to the 0% and 10% boundaries.
- **No Multiple Testing Adjustment on Primary**: There is exactly one primary uncertainty method (QRF 80% width) and one primary estimand ($\text{REL\_BENEFIT\_80}$). Secondary comparators are prespecified descriptive analyses.

---

## 12. Secondary Endpoints & Risk–Coverage Evaluation

### 12.1 Discrete Risk–Coverage Profile
All candidate uncertainty metrics (QRF and secondary comparators) are evaluated on the discrete coverage grid:
$$\kappa \in \{1.00, 0.90, 0.80, 0.70, 0.60, 0.50\}$$
At each coverage level $\kappa$, under within-fold independent ranking, the pipeline reports:
- Number of retained compounds ($|S_\kappa|$) and deferred compounds;
- Pooled Retained RMSE;
- Pooled Retained MAE.

### 12.2 Normalized Area Under the Risk–Coverage Curve (nAURC)
As a summary across the triage spectrum $[0.50, 1.00]$:
$$\text{nAURC} = \frac{1}{0.50} \int_{0.50}^{1.00} \text{RMSE}(\kappa) \, d\kappa \;\approx\; \frac{1}{0.50} \sum_{j=1}^5 \frac{\text{RMSE}(\kappa_j) + \text{RMSE}(\kappa_{j+1})}{2} (\kappa_j - \kappa_{j+1})$$
- Direction: **Lower is better**.
- Status: **Secondary scalar summary**. It does not supersede $\text{REL\_BENEFIT\_80}$.

### 12.3 Post-Outcome Oracle Benchmark
An oracle ranking by true absolute test error $|y_i - \hat{y}_i|$ will be plotted strictly as a theoretical upper bound. It must be visibly labelled:
```
POST_OUTCOME_ORACLE_NOT_DEPLOYABLE
```

### 12.4 Granular Error Mechanics Endpoints
1. **Spearman Rank Correlation**: $\rho_s(u(x), |y - \hat{y}|)$;
2. **Top-Quartile Error Discrimination (ROC-AUC)**: Discrimination of test compounds in the top 25% of absolute prediction errors ($|y - \hat{y}| \ge Q_{0.75}$);
3. **Deferred-Set Top-Quartile Enrichment Factor ($\text{EF}_{20}$)**:
   $$\text{EF}_{20} = \frac{\sum_{i \in \text{Deferred}} \mathbb{I}(|y_i - \hat{y}_i| \ge Q_{0.75})}{0.20 \cdot 744 \cdot 0.25}$$
4. **Geometric Standard Deviation (GSD)**: $10^{\text{RMSE}}$ multiplicative fold-error interpretation.

---

## 13. Conformal Prediction: Secondary Calibration Protocol

### 13.1 Exclusion of CQR from Primary Triage Ranking
Split-conformal Conformalized Quantile Regression (CQR) is **NOT a separate triage ranking method**.
- In standard split-conformal CQR, the calibrated prediction interval for query $x$ is:
  $$\hat{C}_{\text{CQR}}(x) = \big[\hat{q}_{\alpha/2}(x) - \hat{Q}_{1-\alpha}, \; \hat{q}_{1 - \alpha/2}(x) + \hat{Q}_{1-\alpha}\big]$$
- The resulting interval width is:
  $$\text{Width}_{\text{CQR}}(x) = \big(\hat{q}_{1 - \alpha/2}(x) - \hat{q}_{\alpha/2}(x)\big) + 2\hat{Q}_{1-\alpha} = \text{Width}_{\text{QRF}}(x) + \text{constant}$$
- Because $\hat{Q}_{1-\alpha}$ is constant across all query instances within an evaluation fold, $\text{Width}_{\text{CQR}}(x)$ has a **Pearson and Spearman rank correlation of exactly 1.0** with raw QRF width $\text{Width}_{\text{QRF}}(x)$. It produces an identical within-fold ranking.

### 13.2 Role of Conformal Prediction: Interval Calibration Assessment
Conformal prediction is utilized solely to assess the **empirical calibration of prediction intervals**:
- Nominal Confidence Levels: 80% ($\alpha = 0.20$), 90% ($\alpha = 0.10$), 95% ($\alpha = 0.05$);
- Within each outer fold:
  1. Split outer training scaffolds into Proper Training (approx 80% compounds) and Calibration (approx 20% compounds) using a deterministic hash;
  2. Fit QRF on Proper Training;
  3. Compute nonconformity scores on Calibration;
  4. Evaluate interval coverage and efficiency strictly on the untouched Outer Test Fold.
- Reported Metrics: Empirical Marginal Coverage ($\frac{1}{n_{\text{test}}} \sum \mathbb{I}(y_i \in \hat{C}_i)$), Mean Interval Width, Median Interval Width.
- **Exchangeability Constraint**: Conformal guarantees rely on exchangeability. Because outer test folds represent disjoint molecular scaffolds, exchangeability is challenged by scaffold covariate shift. Coverage is an **empirical target, not a guaranteed mathematical bound**. No conditional coverage claims may be made.

---

## 14. Experimental Assay-Noise Context & Non-Imputation Policy

### 14.1 Grounding in Wenlock & Carlsson (2015) Literature
To contextualize residual errors, findings from AstraZeneca's broader human microsomal clearance dataset (Wenlock & Carlsson, *J. Chem. Inf. Model.* 2015, 55, 125–134) provide institutional context:
- 74% of human microsomal compounds in that broader study had only a single measurement;
- For compounds with $\ge 3$ repeat measurements, estimated typical repeat SD was $\approx 0.12\text{ }\log_{10}\text{ units}$ (95% CI: $0.08–0.16$);
- Observed molecule-level SDs ranged $0.01–0.67\text{ }\log_{10}\text{ units}$;
- Experimental error was heteroscedastic, increasing toward the lower dynamic boundary, and comparatively stable above $\approx 25\text{ }\mu\text{L/min/mg}$ (typical SD $\approx 0.11$).

### 14.2 Absolute Prohibitions on Modifying Residuals
For dataset `CHEMBL3301370`, row-specific replicate counts, row-specific standard deviations, and single vs aggregate statuses are **strictly unknown**. Therefore:
- **DO NOT** subtract 0.12 from prediction errors;
- **DO NOT** treat 0.12 as an irreducible noise floor;
- **DO NOT** assign row-level error bars to test observations;
- **DO NOT** "correct" or adjust test residuals for assumed assay noise.

---

## 15. Prespecified Sensitivity Analyses

Two sensitivity analyses are prespecified to evaluate the robustness of the primary triage finding:

### 15.1 Sensitivity A: Historical Strict-Interior Cohort ($N = 731$)
- **Cohort**: Restrict analysis to the $N = 731$ strict-interior observations ($3.0 < CL_{\text{int}} < 150.0$), excluding the 13 exact boundary-3 records.
- **Execution**: Apply identical model architecture, 5-fold scaffold split, within-fold ranking, and bootstrap estimation.
- **Purpose**: Verify whether inclusion of the 13 newly resolved exact lower-bound observations materially shifts the triage estimand $\text{REL\_BENEFIT\_80}$.

### 15.2 Sensitivity B: Assay-Family Higher-Reliability Subgroup ($CL_{\text{int}} \ge 25\text{ }\mu\text{L/min/mg}$)
- **Cohort**: Subgroup of exact quantitative test compounds with true observed $CL_{\text{int}} \ge 25.0\text{ }\mu\text{L/min/mg}$ ($\log_{10} \ge 1.398$).
- **Rationale**: Motivated externally by Wenlock & Carlsson (2015), where assay variability was observed to stabilize at typical SD $\approx 0.11$.
- **CRITICAL METHODOLOGICAL LIMITATION**: True clearance is unknown prior to assay measurement. Therefore, this is an **exploratory, diagnostic, outcome-stratified sensitivity analysis**, strictly **NOT a deployable pre-assay triage policy**.
- **Prohibition**: Do NOT present $\ge 25\text{ }\mu\text{L/min/mg}$ as a validated `CHEMBL3301370`-specific reliability boundary.

---

## 16. Binding Negative-Result Reporting Language

To protect against publication bias, wishful interpretation, and post-hoc rationalization, binding negative-result language is frozen:

### 16.1 Permitted Negative Finding Statement
If the primary analysis yields `EVIDENCE_BELOW_PRACTICAL_THRESHOLD` or `INCONCLUSIVE`:
> **“The prespecified QRF uncertainty measure did not meet the prespecified criterion for operational assay-triage utility within the exact quantitative CHEMBL3301370 cohort.”**

If appropriate:
> **“This result does not establish that prediction errors are intrinsically unpredictable, nor does it identify their mechanistic cause.”**

### 16.2 Prohibition of Causal Speculation
Speculative causal claims—such as asserting that errors are driven by "activity cliffs," "uncaptured structural discontinuities," or "assay noise"—are **strictly prohibited** in the primary report. An absence of triage utility demonstrates only that the candidate uncertainty score does not separate high- and low-error predictions under scaffold shift.

---

## 17. Protocol Separation Boundaries

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CONTINUUM DISCOVERY DMPK                           │
├──────────────────────────────────────┬──────────────────────────────────────┤
│               v3A                    │                 v3B                  │
│     UNCERTAINTY ASSAY TRIAGE         │      TWO-STAGE CENSORING ENSEMBLE    │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ • Cohort: 744 Exact Quantitative     │ • Cohort: All 1,102 Records          │
│ • Focus: Continuous Residual Error   │ • Focus: Range Classification        │
│ • Question: Does uncertainty-based   │   (<3 vs 3-150 vs >150) + Censored   │
│   abstention reduce retained RMSE?   │   Tobit / Survival Likelihoods       │
│ • Status: RELEASE CANDIDATE (v3A.1)  │ • Status: Separate Research Track    │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

1. **v2 Remains Sealed**: v2 model files, predictions, and reports are permanent historical artifacts. v2 is not rerun or patched.
2. **Censoring Separation**: QRF does not solve censored likelihood mechanics. The 274 `<3` and 84 `>150` records remain outside v3A. Imputing values or substituting boundary constants is prohibited.

---

## 18. Pre-Execution Freeze Manifest Requirements

Prior to executing any model fitting or analysis script, an immutable cryptographic freeze manifest must be generated and committed:

Manifest Contents:
1. Canonical cohort specification and exact row count ($N = 744$);
2. Full lists of `activity_id`, `chembl_id`, and `scaffold_key`;
3. Exact outer-fold split assignments (1 to 5) for all 744 rows;
4. Feature representation specification (`ECFP4_2048_R2_BINARY_NOCHIRAL`);
5. SHA-256 hash of feature matrix binary array;
6. SHA-256 hash of split manifest file (`splits/V3A_OUTER_SCAFFOLD_FOLDS.csv`);
7. Exact Random Forest hyperparameter dictionary;
8. Exact code definitions of primary and secondary uncertainty scores;
9. Random seeds: model training (`20260923`), tie-breaking (`V3A_TIE_20260923`), bootstrap (`20260923`), random comparator (`20260923`);
10. Environment metadata: Python, RDKit, and scikit-learn exact version numbers.

---

## 19. Pre-Execution Execution Failure Gates

Scientific execution must immediately abort if any of the following failure gates trip during preflight checks:

1. `GATE_01_COHORT_COUNT`: Exact cohort size $\ne 744$;
2. `GATE_02_STRUCTURE_ALIGNMENT`: Any mismatch between $X[i]$, $y[i]$, `activity_id[i]`, or `scaffold_key[i]`;
3. `GATE_03_DIMENSIONALITY`: Feature matrix shape $\ne (744, 2048)$;
4. `GATE_04_REPRESENTATION_NAME`: Active representation $\ne$ `ECFP4_2048_R2_BINARY_NOCHIRAL`;
5. `GATE_05_SCAFFOLD_LEAKAGE`: Any scaffold key appears in more than one outer fold;
6. `GATE_06_UNIQUE_TEST_INSTANCE`: Any `activity_id` appears in more than one outer test fold;
7. `GATE_07_QRF_PREDICTION_INVARIANT`: $\max_i |\sum_j w_j(x_i) y_j - \hat{f}(x_i)| \ge 10^{-6}$;
8. `GATE_08_QRF_WEIGHT_SUM`: $\max_i |\sum_j w_j(x_i) - 1.0| \ge 10^{-12}$;
9. `GATE_09_SPLIT_HASH_MISMATCH`: SHA-256 of `splits/V3A_OUTER_SCAFFOLD_FOLDS.csv` differs from manifest;
10. `GATE_10_FEATURE_HASH_MISMATCH`: SHA-256 of feature matrix differs from manifest;
11. `GATE_11_TEST_OUTCOME_INSPECTION`: Any pipeline step accesses test labels $y_{\text{test}}$ to determine retention thresholds, feature transforms, or calibration terms.

---

## 20. Explicit Log of Closed Methodological Decisions

The following methodological questions are **permanently closed** in this release candidate:

| Area | Former Open Status | Frozen Resolution in v3A.1-RC |
| :--- | :--- | :--- |
| **Primary Cohort** | 731 vs 744 | **$N = 744$ Exact Quantitative** (includes 13 exact boundary-3 records) |
| **Point Predictor Representation** | ECFP4 vs Descriptors vs Union | **ECFP4 (Morgan R2, 2048-bit, binary) only** |
| **Point Model Architecture** | RF vs GBM vs Ridge | **Frozen RandomForestRegressor (500 trees, sqrt, leaf=2)** |
| **Hyperparameter Tuning** | Grid search vs Frozen | **Zero tuning; frozen engineering parameters** |
| **Primary Uncertainty Method** | 6-family tournament | **QRF central 80% predictive width ($Q_{0.90} - Q_{0.10}$) only** |
| **Primary Operating Point** | Variable vs Frozen | **$\kappa = 0.80$ (20% deferred to assay)** |
| **Cross-Fold Ranking** | Global pooling vs Within-fold | **Within-fold independent ranking strictly mandated** |
| **Role of Conformal Prediction** | Separate triage ranking vs Calibration | **Secondary interval calibration only; not a ranking method** |
| **Learned Uncertainty Meta-Model** | Logistic regression meta-model | **Completely excised from v3A** |
| **Primary Inferential Criterion** | FDR-corrected p-value | **Three-state bootstrap confidence interval relative to 10% benefit** |
| **Practical Utility Threshold** | 0.08 log10 vs Relative | **10% Relative RMSE Benefit over matched random deferral** |
| **Assay Error Handling** | Imputing noise floors | **Descriptive context only; zero residual modification** |
| **Sensitivity at $\ge 25$** | Triage policy vs Diagnostic | **Diagnostic outcome-stratified sensitivity analysis only** |

---

```
V3A_3A1_RC_SPECIFICATION_COMPLETE_NO_EXECUTION
```
