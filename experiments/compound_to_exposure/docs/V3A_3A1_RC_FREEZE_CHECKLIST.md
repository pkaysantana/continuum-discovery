# v3A.1-RC Pre-Execution Freeze Checklist
## Uncertainty-Aware Human Liver Microsomal (HLM) Assay Triage

**Document Status**: `PRE-EXECUTION AUDIT GATES — NO SCIENTIFIC DECISIONS REOPENED`  
**Protocol Version**: `v3A.1-RC`  
**Date**: `2026-09-23`  
**Scope**: Operational and mechanical pre-flight verification checklist for study v3A.1-RC.

---

## 1. Overview & Operational Scope

This checklist establishes the mandatory mechanical verification gates that must be satisfied prior to running model fitting or evaluation scripts for study `v3A.1-RC`. 

> **BINDING RULE**:  
> All human scientific and methodological decisions are **frozen**. This checklist provides mechanical quality-assurance gates only. It does **not** permit reopening, re-evaluating, or modifying frozen study decisions based on data exploration or preliminary results.

---

## 2. Inventory of Frozen Human Decisions (Immutable)

The following decisions are permanently locked in `docs/V3A_UNCERTAINTY_ASSAY_TRIAGE_SAP_3A1_RC.md` and must be verified as frozen:

- [x] **Study Terminology**: Formally classified as a *prospectively specified retrospective reanalysis using scaffold-grouped out-of-fold evaluation*. Not prospectively collected.
- [x] **Historical v2 Holdout Status**: Merged into unified exact cohort ($N=744$); possesses zero confirmatory status in v3A.
- [x] **Primary Scientific Question**: Selective prediction and assay triage: *“Can pre-prediction uncertainty from a fixed HLM clearance model identify compounds whose computational predictions should be deferred to experimental measurement?”*
- [x] **Primary Cohort Eligibility**: $N = 744$ exact quantitative observations (`standard_relation IS NULL`, $3.0 \le CL_{\text{int}} < 150.0\text{ }\mu\text{L/min/mg}$).
- [x] **Raw Database Invariance**: Raw `standard_relation = NULL` preserved in source/interim files; never rewritten to `"="`.
- [x] **Exclusions**: 274 left-censored ($<3$) and 84 right-censored ($>150$) strictly excluded from v3A; zero ambiguous records.
- [x] **Exact $\ne$ Error-Free**: Uncensored semantics established; zero individual row error-bar imputation.
- [x] **Primary Point Predictor**: ECFP4 Random Forest Regressor only (Morgan R2, 2048-bit, binary, unchiralled).
- [x] **RF Hyperparameter Specification**: `n_estimators=500`, `criterion="squared_error"`, `max_features="sqrt"`, `min_samples_split=2`, `min_samples_leaf=2`, `max_depth=None`, `bootstrap=True`, `random_state=20260923`. Zero tuning.
- [x] **Primary Uncertainty Metric**: QRF central 80% predictive width ($Q_{0.90}(x) - Q_{0.10}(x)$). Single primary method.
- [x] **Cross-Fold Comparability Fix**: Within-fold independent ranking at every coverage level; global pooling strictly prohibited.
- [x] **Primary Operating Point**: $\kappa = 0.80$ (80% retained / 20% deferred to experimental assay).
- [x] **Primary Estimand**: $\text{REL\_BENEFIT\_80} = (\text{RMSE}_{\text{RANDOM80}} - \text{RMSE}_{\text{QRF80}}) / \text{RMSE}_{\text{RANDOM80}}$.
- [x] **Random Deferral Baseline**: 10,000 matched within-fold random rankings (seed `20260923`); exact same $k_f(0.80)$ in every fold.
- [x] **Practical Operational Threshold**: 10.0% relative RMSE reduction over random deferral ($\text{REL\_BENEFIT\_80} \ge 10\%$).
- [x] **Primary Inference**: Scaffold-clustered bootstrap (10,000 resamples, stratified by fold, seed `20260923`), three-state interpretation (`SUPPORTED_OPERATIONAL_SIGNAL`, `EVIDENCE_BELOW_PRACTICAL_THRESHOLD`, `INCONCLUSIVE`).
- [x] **Conformal Prediction**: Secondary interval calibration analysis only; not a separate ranking method.
- [x] **Excised Components**: Learned meta-models removed; leaf-support metric removed; FDR/BH primary correction removed.
- [x] **Assay-Noise Context**: Wenlock & Carlsson (2015) context documented; zero residual modification/subtraction.
- [x] **Sensitivity A**: N = 731 historical strict interior ($3.0 < CL_{\text{int}} < 150.0$).
- [x] **Sensitivity B**: Observed $CL_{\text{int}} \ge 25.0\text{ }\mu\text{L/min/mg}$ diagnostic outcome-stratified sensitivity analysis.
- [x] **Negative-Result Wording**: Non-causal standardized reporting language frozen.
- [x] **Protocol Boundaries**: v2 permanently sealed; censoring track (1,102 rows) completely separated.

---

## 3. Mechanical Pre-Execution Verification Checklist

Before execution, an automated preflight script must run and verify every item below:

### 3.1 Data & Cohort Alignment Gates
- [x] **Gate 01 — Cohort Count**:
  `len(cohort_df) == 744`
- [x] **Gate 01a — Full Dataset Conservation**:
  $744\text{ exact} + 274\text{ left-censored} + 84\text{ right-censored} == 1102\text{ total rows}$.
- [x] **Gate 01b — Exact Boundary Breakdown**:
  $731\text{ interior} (3 < y < 150) + 13\text{ boundary-low} (y == 3) + 0\text{ boundary-high} (y == 150) == 744$.
- [x] **Gate 01c — Raw Field Preservation**:
  All 744 rows have `standard_relation IS NULL` in raw data.
- [x] **Gate 02 — Structure & Key Alignment**:
  Row-by-row 1:1 check: `X[i]`, `y[i]`, `activity_id[i]`, `chembl_id[i]`, `scaffold_key[i]`. Zero misalignments.

### 3.2 Representation & Routing Safeguards
- [x] **Gate 03 — Feature Dimensionality**:
  $X$ is a 2D array of shape $(744, 2048)$ and dtype `uint8` or `float32`.
- [x] **Gate 04 — Declared Representation Enum**:
  Active representation name string strictly matches `"ECFP4_2048_R2_BINARY_NOCHIRAL"`.
- [x] **Gate 04a — Substring Routing Ban**:
  Code contains no substring checks on pipeline identifiers (`"r1" in name`, etc.).

### 3.3 Outer Scaffold Split Verification
- [x] **Gate 05 — Scaffold Leakage Check**:
  For all outer folds $f \in \{1, \dots, 5\}$:
  $$\text{scaffolds}(\mathcal{D}_{\text{train}, f}) \cap \text{scaffolds}(\mathcal{D}_{\text{test}, f}) = \emptyset$$
- [x] **Gate 06 — Unique Test Evaluation**:
  Every compound $\text{activity\_id}$ appears in exactly one outer test fold. $\sum_{f=1}^5 n_f = 744$.
- [x] **Gate 06a — Deterministic Split File**:
  `splits/V3A_OUTER_SCAFFOLD_FOLDS.csv` exists, contains columns `activity_id,chembl_id,scaffold_key,outer_fold`, and matches pre-computed SHA-256 hash.

### 3.4 QRF Weight Recovery Validity Gate
- [x] **Gate 07 — QRF Point Prediction Invariant**:
  Across 100% of validation queries (synthetic, training, held-out):
  $$\max_{x} \left| \sum_{i=1}^{N_{\text{train}}} w_i(x) \cdot y_i - \hat{f}_{\text{RF}}(x) \right| < 10^{-6}$$
- [x] **Gate 08 — QRF Weight Normalization Invariant**:
  $$\max_{x} \left| \sum_{i=1}^{N_{\text{train}}} w_i(x) - 1.0 \right| < 10^{-12}$$
- [x] **Gate 08a — Bootstrap Multiplicity Accounting**:
  Confirmed that weight algorithm utilizes `tree.tree_.n_node_samples` or in-bag multiplicity array rather than unweighted leaf indexing.

### 3.5 Within-Fold Ranking & Metric Implementation
- [x] **Within-Fold Ranking Implementation**:
  Verified that retention subset selection operates on within-fold slices, with $k_f(\kappa) = \lceil \kappa \cdot n_f \rceil$.
- [x] **Deterministic Tie-Breaker**:
  Ties broken by SHA-256 hash of `activity_id + "_V3A_TIE_20260923"`.
- [x] **Random Baseline Monte Carlo Machinery**:
  Random baseline runner executes 10,000 within-fold draws with seed `20260923`.
- [x] **Bootstrap Resampling Engine Machinery**:
  10,000 paired scaffold-clustered draws stratified by fold, with seed `20260923`.

The two machinery checks above verify implementation defaults and synthetic behavior only. Neither real 10,000-run analysis has been executed.

### 3.6 Data Leakage & Outcome Blindness Gates
- [x] **Gate 09 — Split Hash Invariance**:
  SHA-256 of `splits/V3A_OUTER_SCAFFOLD_FOLDS.csv` verified.
- [x] **Gate 10 — Feature Matrix Hash Invariance**:
  SHA-256 of computed feature array matches manifest.
- [x] **Gate 11 — Test Outcome Blindness**:
  Verified that outer test outcomes $y_{\text{test}}$ are never passed to standardizers, leaf weight computers, or quantile functions, and are accessed only during final residual calculation.

---

## 4. Pre-Execution Freeze Manifest Generation Checklist

Prior to execution, the following manifest file must be written to `manifests/V3A_1_RC_FREEZE_MANIFEST.json` and hashed:

- [x] Cohort metadata ($N=744$, SHA-256 of input table)
- [x] Feature representation name and exact Morgan fingerprint settings
- [x] SHA-256 of feature matrix array
- [x] SHA-256 of outer scaffold fold assignments
- [x] Complete scikit-learn `RandomForestRegressor` parameter dictionary
- [x] Random seeds:
  - Model training: `20260923`
  - Split tie-breaking: `V3A_20260923`
  - Retention tie-breaking: `V3A_TIE_20260923`
  - Bootstrap resampling: `20260923`
  - Random deferral baseline: `20260923`
- [x] Software environment versions:
  - Python version
  - RDKit version
  - scikit-learn version
  - numpy / scipy versions
- [x] Primary estimand definition and practical criterion (10.0% relative benefit)

---

## 5. Verification Sign-Off

| Check Category | Verification Status | Auditor / Agent | Date |
| :--- | :---: | :---: | :---: |
| **Scientific Design Decisions** | **FROZEN** | Human Lead / Archival Record | 2026-09-23 |
| **Statistical Analysis Plan (v3A.1-RC)** | **COMPLETE** | Antigravity AI Assistant | 2026-09-23 |
| **Pre-Execution Failure Gates** | **SPECIFIED** | Antigravity AI Assistant | 2026-09-23 |
| **Split & Feature Generation** | **MECHANICALLY VERIFIED** | Codex implementation preflight | 2026-09-23 |
| **Cryptographic Manifest** | **GENERATED — PREEXECUTION STATE** | Codex implementation preflight | 2026-09-23 |
| **Model Fitting & Execution** | **BLOCKED — INDEPENDENT AUDIT REQUIRED** | Execution Runner | — |

---

```
V3A_3A1_RC_PREFLIGHT_IMPLEMENTED_NOT_RUN
```
