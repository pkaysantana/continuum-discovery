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
