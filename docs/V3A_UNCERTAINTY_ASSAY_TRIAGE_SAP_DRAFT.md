# Statistical Analysis Plan (SAP) — v3A Prospective Study Design: Uncertainty-Aware HLM Assay Triage

**Document Status**: `PREREGISTRATION DRAFT — STRICTLY NO EXECUTION`  
**Protocol Version**: `3A.0-draft`  
**Date**: `2026-09-23`  
**Dataset**: `CHEMBL3301370` Human Liver Microsomal (HLM) Clearance ($CL_{\text{int}}$, $\mu\text{L/min/mg}$)  
**Cohort Scope**: $N = 731$ strict quantitative interior observations ($3.0 < CL_{\text{int}} < 150.0$, `standard_relation IS NULL`)  
**Target Variable**: $\log_{10}(CL_{\text{int}})$  
**Branch / Base Commit**: `audit/whole-cohort-structure-integrity` / `ba6242e`  

---

## 1. Decision Framing (The Decision Problem)

### 1.1 The Operational Shift: Assay Triage vs QSAR Benchmarking
Traditional QSAR evaluations treat model assessment as an unconstrained regression benchmark evaluated uniformly across all test compounds. In practical drug discovery, however, in silico ADME models serve as **assay triage filters**: the primary operational goal is to identify a subset of high-confidence predictions that can reliably bypass experimental screening, while **deferring** low-confidence or high-uncertainty compounds to prospective wet-lab Human Liver Microsomal (HLM) clearance assays.

Therefore, the central scientific question of v3A is:

> **Can pre-prediction uncertainty information identify human liver microsomal clearance predictions that should be deferred to experimental measurement?**

The primary scientific object is **not**:
* *“Which uncertainty score correlates most strongly with the absolute residual?”* (A ranking/correlation objective that does not guarantee decision utility).

The primary scientific object **is**:
* *“Does abstaining on predictions judged least reliable improve predictive performance on the retained compounds enough to be operationally useful?”*

### 1.2 Mathematical Formulation of Triage
For a chemical structure $x$, a frozen regression model issues a point prediction $\hat{y} = f(x) \in \mathbb{R}$ for $\log_{10}(CL_{\text{int}})$, accompanied by an uncertainty score $u(x) \in \mathbb{R}$.

1. **Prediction**: $\hat{y}(x) = f(x)$, estimated conditional expectation of $\log_{10}(CL_{\text{int}})$.
2. **Uncertainty Score ($u(x)$)**: A scalar metric standardized such that **higher values denote higher expected error / lower reliability**.
3. **Coverage ($\kappa \in [0.5, 1.0]$)**: The proportion of test compounds retained for autonomous in silico prediction. At a chosen coverage level $\kappa$, an uncertainty threshold $\tau_\kappa$ is determined such that:
   $$S_\kappa = \{i \in \mathcal{D}_{\text{test}} \mid u(x_i) \le \tau_\kappa\}, \quad \frac{|S_\kappa|}{|\mathcal{D}_{\text{test}}|} = \kappa$$
4. **Risk ($\mathcal{R}(\kappa)$)**: The prediction error on the retained compound subset $S_\kappa$:
   $$\mathcal{R}(\kappa) = \text{RMSE}(S_\kappa) = \sqrt{\frac{1}{|S_\kappa|} \sum_{i \in S_\kappa} \big(y_i - \hat{y}(x_i)\big)^2}$$
5. **Abstention / Deferral Decision**: Compounds with $u(x_i) > \tau_\kappa$ are designated **DEFERRED_TO_EXPERIMENT**. The model issues no autonomous point clearance call for these compounds, routing them to prospective experimental HLM assay measurement.

```
                      [ Chemical Structure x ]
                                 │
                   ┌─────────────┴─────────────┐
                   ▼                           ▼
        [ Frozen Model f(x) ]        [ Uncertainty Metric u(x) ]
                   │                           │
            Prediction ŷ                       │
                   │                           ▼
                   │                  Is u(x) ≤ τ_κ?
                   │                 ┌────────┴────────┐
                   │               YES                NO
                   ▼                 │                 │
             [ Retained Set ] ◄──────┘                 ▼
       Autonomous In Silico Call              [ Defer to Experiment ]
         (Evaluated at Risk R(κ))            Wet-Lab HLM Measurement
```

---

## 2. Dataset Population & Methodological Boundaries

### 2.1 The 731 Strict Quantitative Interior Cohort
Study v3A is strictly restricted to the **$N = 731$ strict quantitative interior observations** of dataset `CHEMBL3301370`:
* Inclusion Criterion: `standard_relation IS NULL AND 3.0 < standard_value < 150.0`.
* Target Definition: $y_i = \log_{10}(\text{standard\_value}_i)$, where $\text{standard\_value}$ is recorded in $\mu\text{L/min/mg}$.

### 2.2 Explicit Exclusions
The following subsets of `CHEMBL3301370` are **strictly excluded** from v3A:
1. **Left-Censored Cohort ($N = 274$)**: `standard_relation == '<'` and $CL_{\text{int}} \le 3.0$.
2. **Right-Censored Cohort ($N = 84$)**: `standard_relation == '>'` and $CL_{\text{int}} \ge 150.0$.
3. **Boundary-Ambiguous Records ($N = 13$)**: `standard_relation IS NULL` with $CL_{\text{int}} \in \{3.0, 150.0\}$.

### 2.3 Methodological Rationale for Exclusion
In an uncertainty-evaluation protocol, every evaluation metric (residuals, RMSE, quantile calibration, nonconformity scores) requires an unambiguous, continuous, ground-truth label $y_i$. 
* Including censored observations introduces an intractable conflation between **predictive model uncertainty** and **censoring mechanics** (e.g., survival likelihood approximations, Tobit corrections, or arbitrary boundary imputation).
* If a model errs on a $<3.0$ compound, an uncalibrated residual could reflect true prediction failure or merely arbitrary distance from the artificial boundary.
* Restricting v3A strictly to verified continuous measurements ensures that the evaluation of predictive uncertainty is **mathematically interpretable and free from censoring artifacts**.
* Censored boundary handling is governed exclusively by the separate, two-stage censoring research programme.

---

## 3. Representation and Predictive Model Architecture

### 3.1 Frozen Model Selection
To ensure that v3A remains a clean investigation of uncertainty and assay triage rather than another iterative model-tuning or representation contest, the underlying predictive model architecture is **frozen before study execution**.

We evaluate three potential representation candidates based on methodological trade-offs:
1. **ECFP4 Alone (Morgan Radius 2, 2048 bits)**:
   * *Pros*: Cleanest benchmark for pure chemical topology and nearest-neighbor distance metrics; direct mapping to classic Tanimoto similarity.
   * *Cons*: Blind to scalar bulk properties (e.g., ionization, lipophilicity, polar surface area) that govern microsomal metabolic stability.
2. **Physicochemical Descriptors Alone (R1 Panel, 12 descriptors)**:
   * *Pros*: Highly interpretable, low-dimensional continuous manifold; straightforward Euclidean/Mahalanobis geometry.
   * *Cons*: Lacks specific functional group and sub-structural topological resolution.
3. **Union Representation (R1 Descriptors + 2048-bit Morgan ECFP4, 2060 dimensions)**:
   * *Pros*: Combines topological substructure with bulk physicochemical constraints. Exploratory scaffold-grouped evidence suggested complementary error patterns.
   * *Cons*: Requires feature scaling across heterogeneous feature types (binary bits vs continuous properties).

### 3.2 Recommended Frozen Model: `RF_R1_MORGAN2048`
* **Algorithm**: `RandomForestRegressor` (scikit-learn implementation).
* **Hyperparameters (Frozen)**:
  * `n_estimators`: 500
  * `max_features`: `"sqrt"` (or $\approx \sqrt{2060} \approx 45$)
  * `min_samples_leaf`: 2
  * `random_state`: 42
  * `bootstrap`: `True`
* **Representation**: `R1_MORGAN2048_UNION` (12 standardized R1 continuous descriptors + 2048 binary Morgan bits = 2,060 features).
  * Standardized scaling: Descriptors are scaled using `StandardScaler` fit strictly on the training fold; binary Morgan bits remain unscaled.

*(Note: Human decision must freeze whether the Union or ECFP4-alone representation is selected before execution; see Section 17).*

### 3.3 Mandatory Pre-Fit Implementation Assertions
Before fitting any model fold during v3A execution, the pipeline must programmatically verify:
1. `DECLARED_REPRESENTATION_NAME`: Must match an immutable configuration enum (`"R1_MORGAN2048_UNION"` or `"ECFP4_2048"`).
2. `FEATURE_DIMENSIONALITY`: Exactly matches the declared schema (2,060 or 2,048).
3. `MATRIX_SHA256`: Recomputed SHA-256 hash of the feature matrix matches the pre-computed hash manifest.
4. `ROW_KEY_ALIGNMENT`: Assert exact 1:1 row alignment: `X[i]`, `y[i]`, `chembl_id[i]`, and `scaffold_key[i]`.
5. `NO_SUBSTRING_ROUTING`: Feature extraction and routing must be executed via direct programmatic object passing; string pattern matching on pipeline names is strictly prohibited.

---

## 4. Candidate Uncertainty Families

Uncertainty candidates are organized into six distinct conceptual families. Each family formalizes a different hypothesis about what drives prediction failure.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CANDIDATE UNCERTAINTY FAMILIES                        │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ Family A: Chemical            │ 1. Maximum ECFP4 Tanimoto to training set   │
│ Familiarity                   │ 2. Mean similarity to k-NN (k = 5)          │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ Family B: Physicochemical     │ 3. Scaled descriptor 1-NN Euclidean dist.   │
│ Familiarity                   │ 4. Scaled descriptor k-NN distance (k = 5)  │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ Family C: Model               │ 5. Random Forest leaf proximity support     │
│ Familiarity                   │ 6. Effective sample size N_eff              │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ Family D: Local Outcome       │ 7. RF proximity-weighted label variance     │
│ Heterogeneity                 │    (σ²_local)                               │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ Family E: Predictive          │ 8. Quantile Regression Forest (QRF) width   │
│ Distribution Uncertainty      │    (q0.90 - q0.10)                          │
│                               │ 9. QRF conditional IQR (q0.75 - q0.25)      │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ Family F: Calibrated          │ 10. Conformalized Quantile Regression (CQR) │
│ Predictive Uncertainty        │     interval width                          │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ Historical Negative           │ • Max ECFP4 Tanimoto similarity             │
│ Comparators                   │ • Unweighted RF tree-to-tree variance       │
└───────────────────────────────┴─────────────────────────────────────────────┘
```

### 4.1 Detailed Method Definitions

#### Family A: Chemical Familiarity (Topological Space)
* **$u_{\text{A1}}(x) = 1.0 - \max_{j \in \mathcal{D}_{\text{train}}} \text{Tanimoto}(x, x_j)$**: Topological distance to the nearest training analog.
* **$u_{\text{A2}}(x) = 1.0 - \frac{1}{k} \sum_{j \in \text{kNN}(x)} \text{Tanimoto}(x, x_j)$**: Average topological distance to the $k=5$ nearest training analogs.

#### Family B: Physicochemical Familiarity (Property Space)
Let $z(x)$ denote the 12-dimensional R1 descriptor vector standardized by the training set mean and standard deviation.
* **$u_{\text{B1}}(x) = \min_{j \in \mathcal{D}_{\text{train}}} \|z(x) - z(x_j)\|_2$**: Distance to the nearest training compound in standardized property space.
* **$u_{\text{B2}}(x) = \frac{1}{k} \sum_{j \in \text{kNN}(x)} \|z(x) - z(x_j)\|_2$**: Mean distance to the $k=5$ nearest property-space neighbors.
* *Note on Mahalanobis Distance*: Inversion of the $12 \times 12$ covariance matrix is permitted only if heavily regularized (Ledoit-Wolf shrinkage), as strong collinearities between molecular weight, heavy atom count, and ring counts make unregularized Mahalanobis metrics numerically volatile.

#### Family C: Model Familiarity (Tree-Kernel Space)
For a query compound $x$, the Random Forest induces a data-dependent kernel weight vector $w(x) = [w_1(x), \dots, w_N(x)]^T$ across all training points (see Section 5 for bootstrap-aware recovery):
* **$u_{\text{C1}}(x) = -\sum_{i=1}^N \mathbb{I}(w_i(x) > 0)$**: Leaf support (negative count of unique training observations sharing terminal leaves with $x$).
* **$u_{\text{C2}}(x) = -N_{\text{eff}}(x) = -\frac{1}{\sum_{i=1}^N w_i(x)^2}$**: Negative Effective Sample Size ($N_{\text{eff}}$). When $x$ falls into leaves populated by very few, highly repetitive training points, $\sum w_i^2$ is large and $N_{\text{eff}}$ is small, signaling low model familiarity.

#### Family D: Local Outcome Heterogeneity (Neighborhood Variance)
* **$u_{\text{D1}}(x) = \sigma_{\text{local}}^2(x) = \sum_{i=1}^N w_i(x) \big(y_i - \hat{y}(x)\big)^2$**: The proximity-weighted variance of the training labels in the leaf neighborhood of $x$. This measures whether nearby training molecules exhibit consistent or discordant microsomal clearance values.

#### Family E: Predictive Distribution Uncertainty (QRF Quantiles)
Using the cumulative distribution function $\hat{F}(y \mid x) = \sum_{i=1}^N w_i(x) \mathbb{I}(y_i \le y)$:
* **$u_{\text{E1}}(x) = \hat{q}_{0.90}(x) - \hat{q}_{0.10}(x)$**: 80% central prediction interval width.
* **$u_{\text{E2}}(x) = \hat{q}_{0.75}(x) - \hat{q}_{0.25}(x)$**: Conditional interquartile range (IQR).

#### Family F: Calibrated Predictive Uncertainty (Conformal Interval Width)
* **$u_{\text{F1}}(x) = \hat{W}_{\text{CQR}}(x)$**: Width of the Conformalized Quantile Regression (CQR) prediction interval calibrated on an independent inner calibration split (see Section 10).

### 4.2 Non-Independence Warning
> **CRITICAL STATISTICAL NOTICE**:  
> Candidates $u_{\text{C2}}$ ($N_{\text{eff}}$), $u_{\text{D1}}$ ($\sigma_{\text{local}}^2$), $u_{\text{E1}}$ (QRF width), and $u_{\text{F1}}$ (CQR width) all derive mathematically from the **identical Random Forest weight vector $w(x)$**. They represent different functional summaries of the same local empirical distribution. They **must not** be described as independent lines of biological or chemical evidence.

---

## 5. QRF Correctness & Weight-Recovery Requirement

Before Quantile Regression Forest (QRF) quantiles or weights are admitted into the scientific evaluation, the implementation must be verified using a **bootstrap-aware weight recovery algorithm**.

### 5.1 Formulation of Forest Kernel Weights
In a Random Forest consisting of $T$ trees, each tree $t$ is trained on an in-bag bootstrap sample $B_t$ of the training indices. Let $m_{t, i} \ge 0$ denote the multiplicity of training point $i$ in tree $t$'s bootstrap sample (i.e., the number of times observation $i$ was drawn). Let $L_t(x)$ denote the set of training indices residing in the terminal leaf where query point $x$ lands in tree $t$.

The bootstrap-aware kernel weight assigned to training observation $i$ by query $x$ is:
$$w_i(x) = \frac{1}{T} \sum_{t=1}^T \frac{m_{t, i} \cdot \mathbb{I}(i \in L_t(x))}{\sum_{j \in L_t(x)} m_{t, j}}$$

Properties:
1. $w_i(x) \ge 0$ for all $i \in \{1, \dots, N_{\text{train}}\}$.
2. $\sum_{i=1}^{N_{\text{train}}} w_i(x) = 1.0$.

### 5.2 Mandatory Mathematical Invariant
Because the Random Forest point prediction is defined as the average of tree predictions, and each tree prediction is the weighted mean of its in-bag leaf points, the reconstructed weights must reproduce the exact point prediction of the base model:

$$\hat{y}_{\text{reconstructed}}(x) = \sum_{i=1}^{N_{\text{train}}} w_i(x) \cdot y_i \quad \equiv \quad \text{RandomForestRegressor.predict}(x)$$

**Verification Assertion**:
Across every test compound $x$ in every evaluation fold:
$$\max_{x \in \mathcal{D}_{\text{test}}} \left| \sum_{i=1}^{N_{\text{train}}} w_i(x) y_i - f_{\text{RF}}(x) \right| < 10^{-6}$$

**Failure Protocol**:
If this invariant fails to hold to numerical precision ($< 10^{-6}$), the script must immediately raise:
```
QRF_WEIGHT_RECOVERY_FAILED
```
and execution must abort. QRF measures may not enter the study under an unverified weight approximation.

---

## 6. Nested Scaffold Validation Architecture

### 6.1 Split Architecture: Mutually Exclusive Outer Scaffold Folds
To prevent data leakage and provide clean, uncompromised statistical inference, v3A employs a **nested, scaffold-clustered cross-validation architecture**:
* **Outer Level**: 5 mutually exclusive outer test folds ($K_{\text{outer}} = 5$) grouped by Bemis–Murcko scaffold key (`scaffold_key`).
  * Every scaffold cluster appears in exactly **one** outer test fold.
  * No compound in outer test fold $k$ shares a Bemis–Murcko scaffold with any compound in outer training fold $k$.
* **Rejection of Repeated Random Group Splits**: We explicitly reject repeated `GroupShuffleSplit` across multiple random seeds for primary hypothesis testing. Reusing compounds across multiple test sets introduces **pseudo-replication**, which invalidates standard confidence intervals and artificially inflates effective sample sizes.

### 6.2 Nested Inner Partitioning (Within Each Outer Training Fold)
Within each outer training fold ($\approx 80\%$ of data, $N \approx 585$):
* **Inner Scaffold CV**: A nested 4-fold scaffold-grouped split is constructed exclusively within the outer training set.
* **Role of Inner Split**:
  1. Fit and calibrate conformal nonconformity scores (see Section 10).
  2. Compute out-of-fold predictions to train combined meta-models (see Section 11).
  3. Estimate scaling parameters.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          OUTER SCAFFOLD FOLD k                              │
├─────────────────────────────────────────────┬───────────────────────────────┤
│           OUTER TRAINING SET (80%)          │      OUTER TEST FOLD (20%)    │
│            (Scaffolds A, B, C, D)           │          (Scaffold E)         │
├──────────────────────┬──────────────────────┤                               │
│ Proper Training (80%)│ Inner Calibration    │ • Strictly untouched during   │
│ • Fit Base RF Model  │ Split (20%)          │   model training, scaling,    │
│ • Fit QRF Weights    │ • Calibrate Conformal│   and calibration.            │
│ • Fit Scalers        │   Scores             │ • Evaluated ONCE at test time.│
│                      │ • Train Meta-Model   │                               │
└──────────────────────┴──────────────────────┴───────────────────────────────┘
```

### 6.3 Strict Leakage-Prevention Invariants
1. **Scaler Isolation**: Standard scalers for descriptors are fit strictly on outer training data; test features are transformed using frozen training parameters.
2. **Weight Isolation**: QRF and kernel proximity weights $w_i(x)$ are computed using outer training observations only.
3. **Calibration Isolation**: Conformal correction terms $Q_{1-\alpha}$ are computed strictly on inner calibration folds. Outer test residuals are never accessed during calibration.
4. **Residual Barrier**: Outer test residuals are used solely to compute the final risk–coverage curves and performance metrics. They are never fed back into any uncertainty scoring function.

---

## 7. Primary Endpoint: Risk–Coverage Curve

### 7.1 Risk–Coverage Curve Definition
Let predictions on the combined outer test sets be denoted $\{(\hat{y}_i, y_i, u_i)\}_{i=1}^{N}$.
Predictions are ranked in ascending order of uncertainty score $u_i$ (from most confident to least confident).

For coverage $\kappa \in [0.5, 1.0]$, let $S_\kappa$ denote the top $\lfloor \kappa \cdot N \rfloor$ compounds with the lowest uncertainty scores.
The risk at coverage $\kappa$ is defined as the Root Mean Squared Error on the retained set:
$$\mathcal{R}(\kappa) = \text{RMSE}(\kappa) = \sqrt{\frac{1}{|S_\kappa|} \sum_{i \in S_\kappa} (y_i - \hat{y}_i)^2}$$

### 7.2 Discrete Grid Evaluation
Risk is evaluated at six prospectively frozen coverage benchmarks:
$$\kappa \in \{1.00, 0.90, 0.80, 0.70, 0.60, 0.50\}$$
* $\kappa = 1.00$: Full cohort baseline (0% deferred, all 731 compounds predicted).
* $\kappa = 0.80$: **Primary Operational Benchmark** (20% deferred to wet-lab HLM assay).
* $\kappa = 0.50$: Extreme triage benchmark (50% deferred).

### 7.3 Primary Summary Scalar: Area Under the Risk–Coverage Curve (AURC)
The primary summary scalar is the **Area Under the Risk–Coverage Curve** across the triage range $[0.50, 1.00]$:
$$\text{AURC} = \int_{0.50}^{1.00} \mathcal{R}(\kappa) \, d\kappa$$
Approximated via trapezoidal numerical quadrature over the discrete grid:
$$\text{AURC} \approx \sum_{j=1}^{5} \frac{\mathcal{R}(\kappa_j) + \mathcal{R}(\kappa_{j+1})}{2} \cdot (\kappa_j - \kappa_{j+1})$$

* **Directionality**: **LOWER IS BETTER**. A triage system that successfully identifies and removes high-error compounds causes $\mathcal{R}(\kappa)$ to decline sharply as coverage drops from 1.00 to 0.50, producing a low AURC.

### 7.4 Benchmarks
1. **Flat Random Baseline ($\text{AURC}_{\text{random}}$)**: Expected risk when compounds are deferred completely at random. Under random abstention, expected retained RMSE remains flat at $\text{RMSE}(1.00)$, yielding:
   $$\text{AURC}_{\text{random}} = 0.50 \cdot \text{RMSE}(1.00)$$
2. **Oracle Upper Bound ($\text{AURC}_{\text{oracle}}$)**: An outcome-informed theoretical benchmark where compounds are sorted in ascending order of their true absolute error $e_i = |y_i - \hat{y}_i|$.
   * *Status*: Labelled strictly as `ORACLE_UNATTAINABLE_BENCHMARK`. It represents the physical mathematical limit of triage performance for the given point predictor.

---

## 8. Practical Effect-Size Criteria (Pre-Specified Thresholds)

Statistical significance alone (e.g., $p < 0.05$) is insufficient to justify integrating an uncertainty method into an operational drug discovery pipeline. To be declared successful, an uncertainty metric must demonstrate **practical operational utility**.

We evaluate performance at the primary operational benchmark: **$\kappa = 0.80$ (20% deferral to assay)**.

### 8.1 Candidate Practical Effect-Size Thresholds (Select One to Freeze)
The study team must prospectively select and freeze exactly one of the following criteria prior to unblinding and execution:

* **Candidate Threshold A (Absolute RMSE Reduction)**:
  $$\Delta \text{RMSE}_{80} = \text{RMSE}(1.00) - \text{RMSE}(0.80) \;\ge\; 0.08 \text{ }\log_{10}\text{ units}$$
  *(Rationale: In HLM assays, 0.08 log units represents $\approx 20\%$ reduction in error variance, a meaningful shift above assay repeatability limits).*
* **Candidate Threshold B (Relative RMSE Reduction)**:
  $$\frac{\text{RMSE}(1.00) - \text{RMSE}(0.80)}{\text{RMSE}(1.00)} \;\ge\; 15.0\%$$
* **Candidate Threshold C (Multiplicative Geometric Fold-Error Reduction)**:
  Let $\text{GSD} = 10^{\text{RMSE}}$. The fold-error uncertainty must drop by at least 0.25 fold:
  $$10^{\text{RMSE}(1.00)} - 10^{\text{RMSE}(0.80)} \;\ge\; 0.25 \text{ fold}$$
* **Candidate Threshold D (Normalized Oracle Efficiency)**:
  The method must capture at least 25% of the total potential error reduction achievable by the theoretical oracle:
  $$\eta_{\text{oracle}} = \frac{\text{RMSE}(1.00) - \text{RMSE}(0.80)}{\text{RMSE}(1.00) - \text{RMSE}_{\text{oracle}}(0.80)} \;\ge\; 25.0\%$$

*(Recommendation: Candidate Threshold A is recommended for its direct physical interpretability in log clearance units).*

---

## 9. Secondary Endpoints

The following secondary metrics provide granular insight into the error mechanics and calibration of candidate uncertainty methods:

1. **ROC-AUC for High-Error Detection**:
   * Binary label: $Y_{\text{high\_error}} = \mathbb{I}\big(|y_i - \hat{y}_i| \ge Q_{0.75}(|y - \hat{y}|)\big)$ (top quartile of absolute prediction errors).
   * Metric: Area Under the ROC Curve discriminating top-quartile errors using uncertainty score $u(x)$.
2. **Spearman Rank Correlation ($\rho_s$)**:
   * $\rho_s\big(u(x), |y - \hat{y}|\big)$ across all test compounds.
   * *Status*: Secondary only. High monotonic rank correlation does not guarantee sharp separation at operational triage thresholds.
3. **Deferred Set Large-Error Enrichment Factor ($\text{EF}_{20}$)**:
   * Proportion of top-quartile errors concentrated in the 20% deferred subset:
     $$\text{EF}_{20} = \frac{P(\text{Top-Quartile Error} \mid \text{Deferred})}{P(\text{Top-Quartile Error})} = \frac{\sum_{i \in \text{Deferred}} Y_{\text{high\_error}, i}}{0.20 \cdot N \cdot 0.25}$$
4. **Retained-Set MAE**:
   * Mean Absolute Error evaluated at each coverage level $\kappa \in \{1.00, 0.90, 0.80, 0.70, 0.60, 0.50\}$.
5. **Prediction Interval Empirical Coverage**:
   * Evaluated for nominal 80%, 90%, and 95% intervals produced by QRF and CQR:
     $$\text{Coverage}_{\alpha} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}\big(y_i \in [\hat{L}_\alpha(x_i), \hat{U}_\alpha(x_i)]\big)$$
6. **Interval Efficiency**:
   * Mean and median prediction interval width $\hat{U}_\alpha(x_i) - \hat{L}_\alpha(x_i)$.
7. **Effective Sample Size ($N_{\text{eff}}$) Distribution**:
   * Summary statistics (median, IQR, 5th percentile) of $N_{\text{eff}}(x)$ across test compounds.

---

## 10. Conformal Prediction Protocol

### 10.1 Conformalized Quantile Regression (CQR) Procedure
To evaluate rigorously calibrated prediction intervals, Conformalized Quantile Regression (CQR) is implemented using split-conformal inference within each outer fold:

1. **Inner Calibration Split**:
   Within outer training fold $k$, compounds are partitioned by scaffold into an Inner Proper Training set $\mathcal{D}_{\text{proper\_train}}$ (80% of scaffolds) and an Inner Calibration set $\mathcal{D}_{\text{cal}}$ (20% of scaffolds).
2. **Quantile Model Training**:
   The base QRF model is fit on $\mathcal{D}_{\text{proper\_train}}$ to estimate nominal conditional quantile functions $\hat{q}_{\alpha/2}(x)$ and $\hat{q}_{1 - \alpha/2}(x)$ (e.g., $\alpha = 0.20$ for an 80% interval).
3. **Nonconformity Score Computation**:
   For each observation $i \in \mathcal{D}_{\text{cal}}$, compute the signed nonconformity score:
   $$E_i = \max\Big(\hat{q}_{\alpha/2}(x_i) - y_i, \; y_i - \hat{q}_{1 - \alpha/2}(x_i)\Big)$$
4. **Conformal Correction Factor**:
   Compute the $(1 - \alpha)$-th empirical quantile of $\{E_i\}_{i \in \mathcal{D}_{\text{cal}}}$, with finite-sample correction:
   $$Q_{1-\alpha}(E; \mathcal{D}_{\text{cal}}) = \text{Quantile}\left(1 - \alpha; \; \frac{\lceil (1 - \alpha)(|\mathcal{D}_{\text{cal}}| + 1) \rceil}{|\mathcal{D}_{\text{cal}}|}\right)$$
5. **Outer Test Prediction Interval**:
   For each outer test compound $x_* \in \mathcal{D}_{\text{test}, k}$, the calibrated interval is:
   $$\hat{C}(x_*) = \Big[\hat{q}_{\alpha/2}(x_*) - Q_{1-\alpha}, \; \hat{q}_{1 - \alpha/2}(x_*) + Q_{1-\alpha}\Big]$$
   The calibrated uncertainty score is the interval width: $u_{\text{F1}}(x_*) = \text{Width}\big(\hat{C}(x_*)\big)$.

### 10.2 Exchangeability and Scaffold Covariate Shift
* **Theoretical Guarantee vs Practical Reality**:
  * Standard conformal prediction guarantees exact marginal coverage $P\big(y_* \in \hat{C}(x_*)\big) \ge 1 - \alpha$ under the assumption that calibration and test observations are **exchangeable** (i.e. independent and identically distributed).
  * In scaffold-split evaluations, test compounds belong to disjoint molecular scaffolds from training and calibration compounds. Scaffold shift constitutes a **covariate shift** ($P_{\text{test}}(X) \ne P_{\text{cal}}(X)$), formally violating strict exchangeability.
* **Interpretation**:
  * Marginal coverage under scaffold splits is an **empirical target**, not an absolute mathematical guarantee.
  * Conditional coverage across individual chemical sub-series is not guaranteed.
* **Descriptive Subgroup Diagnostics**:
  * Empirical coverage will be reported descriptively across:
    1. Singleton vs multi-compound scaffolds;
    2. High vs low chemical familiarity bins (Tanimoto $<0.35$, $0.35-0.50$, $>0.50$).
  * These subgroup diagnostics are descriptive only and will not be claimed as conditionally guaranteed.

---

## 11. Combined Confidence Model (Meta-Model Protocol)

### 11.1 Role: Secondary / Exploratory Endpoint
A meta-model combining multiple uncertainty metrics is included strictly as a **secondary exploratory analysis**. The primary scientific test rests on individual, transparent uncertainty measures.

### 11.2 Model Specification: Regularized Logistic Regression
* **Objective**: Predict whether a compound falls in the top error quartile:
  $$\pi(x) = P\big(|y - \hat{y}| \ge Q_{0.75} \;\big|\; u_{\text{features}}(x)\big)$$
* **Input Features ($u_{\text{features}}$)**: Standardized vector containing one representative metric from each family:
  1. Chemical distance: $u_{\text{A1}}$ ($1 - \max \text{Tanimoto}$)
  2. Physicochemical distance: $u_{\text{B1}}$ (1-NN descriptor distance)
  3. Model familiarity: $u_{\text{C2}}$ ($-N_{\text{eff}}$)
  4. Local outcome variance: $u_{\text{D1}}$ ($\sigma_{\text{local}}^2$)
  5. Predictive distribution width: $u_{\text{E1}}$ (QRF 80% width)
* **Classifier**: Logistic Regression with L2 regularization ($C = 1.0$). Complex non-linear gradient-boosted meta-models are prohibited to prevent overfitting on $N=731$ and to ensure inspectable regression coefficients.

### 11.3 Nested Training Invariant
To prevent target leakage:
* The meta-model evaluated on outer test fold $k$ must be trained **strictly on out-of-fold predictions from the inner scaffold cross-validation** within outer training fold $k$.
* The meta-model never sees test set error labels.

---

## 12. Statistical Inference Plan

### 12.1 Unit of Inference: Scaffold-Clustered Bootstrap
Because compounds sharing a Bemis–Murcko scaffold key exhibit correlated physicochemical and clearance properties, individual observations are not statistically independent.
* **Inference Unit**: The Bemis–Murcko scaffold cluster ($g(x_i)$).
* **Resampling Procedure**: Clustered bootstrap over unique scaffold keys (1,000 resamples).
* **Procedure**:
  1. Sample unique scaffold identifiers with replacement from the complete set of scaffolds.
  2. Pull all test compounds belonging to the sampled scaffolds.
  3. Recompute the risk–coverage curve $\mathcal{R}^*(\kappa)$, AURC$^*$, and $\Delta \text{RMSE}_{80}^*$ on the resampled test set.
  4. Compute 95% empirical percentile confidence intervals $[Q_{0.025}^*, Q_{0.975}^*]$.

### 12.2 Primary Hypothesis Testing
* **Null Hypothesis ($H_0$)**: The candidate uncertainty measure provides no operational triage benefit over full-cohort prediction:
  $$H_0: \Delta \text{RMSE}_{80} \;\le\; 0.00$$
* **Alternative Hypothesis ($H_1$)**: The candidate uncertainty measure significantly reduces prediction error on the retained 80% subset:
  $$H_1: \Delta \text{RMSE}_{80} \;>\; 0.00$$

### 12.3 Paired Method Comparisons
To test whether a candidate metric (e.g. QRF width or $N_{\text{eff}}$) outperforms standard chemical familiarity ($1 - \max \text{Tanimoto}$):
* Compute paired bootstrap differences on identical resamples:
  $$\Delta \text{AURC}^* = \text{AURC}^*(\text{Candidate}) - \text{AURC}^*(\text{Tanimoto})$$
* Test whether the 95% confidence interval of the difference excludes zero.

### 12.4 Multiple Testing Correction
Across the primary candidate uncertainty families (6 primary representatives), false discovery rates will be controlled using the **Benjamini–Hochberg procedure** at $\alpha = 0.05$.

---

## 13. Pre-Specified Negative-Result Criterion

To preserve scientific objectivity, study v3A is explicitly structured such that **a definitive negative finding is a fully valid, successful scientific conclusion**.

### Binding Negative-Result Statement
If upon execution of the frozen protocol:
1. No candidate uncertainty method achieves the pre-specified practical effect-size threshold (e.g. $\Delta \text{RMSE}_{80} \ge 0.08$ with FDR-adjusted $p < 0.05$); **OR**
2. No candidate uncertainty method demonstrates statistically significant error reduction over random abstention;

The study will conclude and report:

> **“None of the evaluated pre-prediction uncertainty measures provides operationally useful assay-triage capability for human liver microsomal clearance in this dataset. Prediction errors under scaffold shift appear driven by uncaptured structural discontinuities rather than identifiable model or chemical familiarity boundaries.”**

**Prohibition on Post-Hoc Reframing**:
An absence of triage utility must **never** be retroactively re-framed as a positive finding (e.g., claiming success based on minor non-significant Spearman correlations or uncalibrated subgroup trends). A negative result directly informs the scientific community that simple in silico uncertainty triage cannot reliably substitute for experimental HLM profiling in this chemical space.

---

## 14. Assay-Noise Ceiling Analysis

### 14.1 Absence of Individual Replicate Variances
Dataset `CHEMBL3301370` reports single unreplicated summary intrinsic clearance values without individual experimental replicate logs or within-lab standard deviations. Consequently, the true experimental measurement noise floor cannot be directly computed from the data.

### 14.2 Assumption-Dependent Ceiling Scenarios
To contextualize model error relative to experimental assay noise, residual risk $\mathcal{R}(\kappa)$ will be compared against three published historical literature estimates for microsomal intrinsic clearance inter-day/inter-lab standard deviations:
* Scenario 1 (Optimistic Intralab SD): $\sigma_{\text{assay}} = 0.25 \text{ }\log_{10}\text{ units}$
* Scenario 2 (Standard Literature Benchmark): $\sigma_{\text{assay}} = 0.30 \text{ }\log_{10}\text{ units}$
* Scenario 3 (Conservative Interlab SD): $\sigma_{\text{assay}} = 0.347 \text{ }\log_{10}\text{ units}$

### 14.3 Mandatory Reporting Constraint
Any comparison of model RMSE to an assay-noise floor must be explicitly and visibly tagged:
```
ASSUMPTION_DEPENDENT_CEILING_ANALYSIS
```
This comparison is exploratory and descriptive only. It **cannot** determine the primary study outcome or override the empirical effect-size criteria.

---

## 15. Policy on Historical v2 Holdout

1. **Exclusion from Model Tuning & Calibration**:
   The historical 149-compound v2 holdout was extensively unblinded, audited, and analyzed during v2 forensics. It is **no longer pristine**.
2. **Prohibited Uses**:
   * It must **NOT** be used to select v3A representations or hyperparameters.
   * It must **NOT** be used to tune uncertainty thresholds $\tau_\kappa$.
   * It must **NOT** be used to calibrate conformal nonconformity scores.
   * It must **NOT** be presented as an untouched prospective confirmatory test set.
3. **v3A Primary Allocation**:
   The 149 historical holdout compounds are recombined with the 582 training compounds into the unified $N=731$ pool for fresh, nested 5-fold scaffold cross-validation.
4. **Post-Hoc Reporting**:
   Performance on the historical 149-compound subset may be reported in a secondary appendix table strictly for post-hoc longitudinal comparison with v2 results, clearly labelled:
   `HISTORICAL_V2_HOLDOUT_POST_HOC_COMPARISON`.

---

## 16. Relationship to Censoring Research Programme

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CONTINUUM DISCOVERY DMPK                           │
├──────────────────────────────────────┬──────────────────────────────────────┤
│               v3A                    │                 v3B                  │
│     UNCERTAINTY ASSAY TRIAGE         │      TWO-STAGE CENSORING ENSEMBLE    │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ • Cohort: 731 Strict Interior        │ • Cohort: All 1,102 Records          │
│ • Focus: Continuous Residual Error   │ • Focus: Range Classification        │
│ • Question: Does abstention reduce   │   (<3 vs 3-150 vs >150) + Censored   │
│   RMSE on retained interior points?  │   Regression Likelihoods             │
│ • Status: Quantitative Triage SAP    │ • Status: Separate Research Track    │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

* Quantile Regression Forests (QRF) and Conformalized Quantile Regression (CQR) **do not solve survival or censoring mechanics**.
* Study v3A investigates uncertainty strictly within observable continuous clearance space ($3.0 < CL_{\text{int}} < 150.0$).
* Boundary categorization ($CL_{\text{int}} \le 3.0$ and $CL_{\text{int}} \ge 150.0$) belongs to the separate, future two-stage censoring research programme.

---

## 17. Pre-Execution Human Freezing Checklist

Before executing any script or fitting any model under v3A, the study team must make and record the following binding decisions:

| Decision Item | Candidate Options | Recommended Selection | Status |
| :--- | :--- | :--- | :---: |
| **1. Frozen Feature Representation** | (A) `R1_MORGAN2048_UNION` (2060)<br>(B) `ECFP4_2048` (2048)<br>(C) `R1_DESCRIPTORS_12` (12) | **`R1_MORGAN2048_UNION`** | `PENDING_HUMAN_FREEZE` |
| **2. Primary Practical Effect-Size Criterion** | (A) $\Delta\text{RMSE}_{80} \ge 0.08$ log units<br>(B) Relative $\Delta\text{RMSE}_{80} \ge 15\%$<br>(C) Fold error drop $\ge 0.25$ fold<br>(D) Oracle efficiency $\ge 25\%$ | **Candidate A ($\Delta\text{RMSE}_{80} \ge 0.08$)** | `PENDING_HUMAN_FREEZE` |
| **3. Outer Split Architecture** | (A) 5-fold scaffold partition<br>(B) 10-fold scaffold partition | **5-fold scaffold partition** | `PENDING_HUMAN_FREEZE` |
| **4. QRF Nominal Confidence Level** | (A) 80% interval ($q_{0.10}$ to $q_{0.90}$)<br>(B) 90% interval ($q_{0.05}$ to $q_{0.95}$) | **80% central interval** | `PENDING_HUMAN_FREEZE` |
| **5. Pre-Computed Feature Matrix SHA-256** | Compute and freeze SHA-256 hash of $731 \times 2060$ feature matrix | *Hash manifest generation* | `PENDING_HUMAN_FREEZE` |

---

## 18. Pre-Flight Implementation Verification Invariants

Prior to running prospective analysis scripts, automated tests must verify:
- [ ] `ASSERT_DATASET_N`: Exact row count of interior cohort is 731.
- [ ] `ASSERT_EXCLUSIONS`: Left-censored (274), right-censored (84), and boundary-ambiguous (13) rows are excluded.
- [ ] `ASSERT_REPRESENTATION_NAME`: Matches frozen selection enum.
- [ ] `ASSERT_QRF_WEIGHT_INVARIANT`: $\max_i |\sum_j w_j(x_i) y_j - f(x_i)| < 10^{-6}$.
- [ ] `ASSERT_SCAFFOLD_DISJOINTNESS`: $\mathcal{S}(\text{Train}_k) \cap \mathcal{S}(\text{Test}_k) = \emptyset$ for all $k \in \{1, \dots, 5\}$.
- [ ] `ASSERT_SCALER_LEAK_FREE`: Test features are never passed to `fit` or `fit_transform`.
- [ ] `ASSERT_CALIBRATION_LEAK_FREE`: Conformal $Q_{1-\alpha}$ computed exclusively on inner calibration folds.

---

V3A_PROTOCOL_DRAFT_COMPLETE_NO_EXECUTION
