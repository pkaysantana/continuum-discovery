# DMPK Compound-to-Exposure Modelling Preregistration

This document outlines the frozen prospective modelling design for predicting human liver microsomal (HLM) apparent intrinsic clearance. The design strictly adheres to the frozen science requirements: NO neural networks, NO science-track boundary substitution, and fixed dataset sizes.

## Software Environment
The following environment packages are frozen:
*   **Python**: 3.11.16
*   **RDKit**: 2025.3.6
*   **NumPy**: 2.2.6
*   **scikit-learn**: 1.9.1
*   **SciPy**: 1.17.1
*   **statsmodels**: 0.15.0

*(Note: The original modelling environment was frozen before the U6 analysis. `matplotlib` was subsequently added solely as a plotting/reporting dependency before any predictive model was fitted. None of the frozen modelling-core package versions changed).*

## 1. Primary Validation Design
*   **Design Choice**: Stratified grouped 5-fold cross-validation generated ONCE on the full N=1,102 classifier cohort and subsequently frozen. The regression N=744 and S1 sub-cohorts inherit these exact fold assignments by subsetting.
*   **Scaffold Group Definition**: 
    *   Scaffolds are computed via exact RDKit Bemis-Murcko framework (`MurckoScaffold.GetScaffoldForMol`).
    *   For molecules with a non-empty scaffold, the group key is the canonical isomeric scaffold SMILES.
    *   For acyclic molecules whose Murcko scaffold is empty, each molecule receives its own deterministic singleton group keyed by its full frozen provenance canonical SMILES.
*   **Algorithm & Seed**: `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=Seed)` from scikit-learn.
*   **Fallback Procedure**: We search a prespecified, finite sequence of seeds: `[42, 43, 44, ..., 141]`. We stop at the first seed that yields a valid fold assignment.
    *   *Validity criterion*: No scaffold group crosses folds; every outer fold contains at least one BELOW, at least one IN-RANGE, and at least one ABOVE observation.
    *   *Failure*: If no seed in the sequence yields a valid assignment, the split generation fails explicitly. The methodology must be fundamentally reconsidered before continuing.
*   **Fold Artifact**: When outer folds are generated, the selected seed, exact compound-to-fold assignment, and scaffold keys will be written to a versioned artifact. This artifact must be hash-verified and committed *before* any predictive model fitting. The split may not subsequently be regenerated to improve performance.
*   **Locked Test Set**: No separate locked test set. Validation metrics are computed using the concatenated Out-Of-Fold (OOF) predictions across the 5 outer folds.

## 2. Molecular Identity and Leakage
*   **Modelling Structure Input**: The frozen provenance identity SMILES (RDKit 2025.3.6 sanitised isomeric canonical SMILES) containing all original stereochemistry, isotopes, and disconnected components.
*   **Salt/Multicomponent Policy**: All disconnected components are PRESERVED exactly as in the provenance identity for feature generation.
*   **Tautomers**: No tautomer normalisation.
*   **Cross-track Independence**: 
    *   HH is a paired/descriptive secondary analysis.
    *   Biogen is an independently fit/evaluated within-dataset replication.
    *   TDC is a separate historical benchmark reproduction.

## 3. Primary Continuous Target and Boundary-Ambiguous Records
*   **Primary Target**: `log10(reported HLM CLint)`.
*   **Invalid Value Handling**: The 13 unresolved null-at-3 records in the IN-RANGE set ($N=744$) are assigned the numerical value 3.0 (log10 = 0.477) for modelling, exclusively under the frozen dataset-specific working inference. This assignment is NOT evidence that the values are proven exact uncensored equalities.

## 4. Molecular Representations & Model Matrix
*   **Seven Descriptor Representation**: 
    The seven descriptors previously used for dataset characterisation are prospectively adopted as the frozen modelling representation (before any predictive model is fitted). The exact RDKit implementations are:
    1.  Molecular weight: `Descriptors.MolWt(mol)`
    2.  cLogP: `Crippen.MolLogP(mol)`
    3.  TPSA: `rdMolDescriptors.CalcTPSA(mol)`
    4.  H-bond donors: `Lipinski.NumHDonors(mol)`
    5.  H-bond acceptors: `Lipinski.NumHAcceptors(mol)`
    6.  Strict rotatable bonds: `rdMolDescriptors.CalcNumRotatableBonds(mol, rdMolDescriptors.NumRotatableBondsOptions.Strict)`
    7.  Fraction Csp3: `rdMolDescriptors.CalcFractionCSP3(mol)`

The frozen allowed model/representation combinations are:
*   **Regression (trained on N=744 inferred quantifiable-range cohort)**:
    1.  Training-Fold Mean Predictor — no molecular representation
    2.  Training-Fold Median Predictor — no molecular representation
    3.  Ridge Regression — physicochemical descriptors (the 7 frozen descriptors)
    4.  Ridge Regression — Morgan fingerprints (Radius 2, 2048-bit, binary, useChirality=True)
    5.  Random Forest Regressor — physicochemical descriptors
    6.  Random Forest Regressor — Morgan fingerprints
*   **Classifier (trained on N=1102 full cohort)**:
    1.  Majority Baseline — no molecular representation
    2.  Multinomial Logistic Regression (L2) — physicochemical descriptors
    3.  Multinomial Logistic Regression (L2) — Morgan fingerprints
    4.  Random Forest Classifier — physicochemical descriptors
    5.  Random Forest Classifier — Morgan fingerprints

## 5. Preprocessing
*   **Missing Descriptors**: Median imputation (learned exclusively on the respective inner/outer training fold).
*   **Scaling**: StandardScaler applied to the 7 descriptors (learned exclusively on the respective inner/outer training fold).
*   **Variance Filtering**: Drop zero-variance Morgan bits (learned exclusively on the respective inner/outer training fold).

## 6. Estimator Randomness & Hyperparameters
*   **Inner Validation Method**: 
    *   Regression: Grouped 3-fold CV (`GroupKFold`, avoiding cross-fold scaffold leakage).
    *   Classifier: Stratified Grouped 3-fold CV (`StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=42)`).
    *   Outer-test scaffolds NEVER enter inner training/validation.
*   **Selection Metric**: 
    *   Regression: Mean inner-validation **MAE** (log10).
    *   Classifier: Mean inner-validation **Macro-F1**.
*   **Frozen Estimator Settings, Grids & Exact Tie-Breakers**: (Ties defined by equality of aggregated score to numerical tolerance 1e-6)
    *   **Ridge**: `solver="lsqr"`, `tol=1e-4`, `max_iter=10000`, `fit_intercept=True` (explicit deterministic solver compatible with dense/sparse descriptors). Grid: `alpha` $\in \{0.1, 1.0, 10.0\}$. Tie-break: larger `alpha` preferred.
    *   **LogisticRegression**: `solver="lbfgs"`, `max_iter=5000`, `tol=1e-4`, `class_weight="balanced"`. (Note: `penalty="l2"` is default but deprecated as of 1.8 so it is omitted; `multi_class` is removed in 1.9.1, and 3-class multinomial behaviour is inferred natively with `lbfgs`). Grid: `C` $\in \{0.1, 1.0, 10.0\}$. Tie-break: smaller `C` preferred.
    *   **RandomForestRegressor**: `criterion="squared_error"`, `max_features=1.0`, `bootstrap=True`, `min_samples_split=2`, `min_samples_leaf=1`, `random_state=42`, `n_estimators=100`, `n_jobs=1`. Grid: `max_depth` $\in \{10, \text{None}\}$. Tie-break: `max_depth=10` preferred.
    *   **RandomForestClassifier**: `criterion="gini"`, `max_features="sqrt"`, `bootstrap=True`, `min_samples_split=2`, `min_samples_leaf=1`, `class_weight="balanced"`, `random_state=42`, `n_estimators=100`, `n_jobs=1`. Grid: `max_depth` $\in \{10, \text{None}\}$. Tie-break: `max_depth=10` preferred.
    *   All other consequential parameters not enumerated are explicitly frozen to their scikit-learn defaults.

## 7. Regression Metrics
*   **Headline**: MAE (log10).
*   **Secondary**: 
    *   RMSE
    *   Spearman $\rho$
    *   $R^2$: This is secondary and must be interpreted with an explicit restricted/truncated target-variance caveat. Learned models must be compared against the training-fold mean baseline when discussing $R^2$ / predictive value.
    *   Fraction within two-fold (absolute error $\le \log_{10}(2)$): Reported as an experimental-repeatability/reference agreement band. It is NOT an irreducible noise floor, Bayes error, or significance threshold.
*   Metrics pooled globally from OOF predictions.

## 8. Classifier Metrics
*   **Headline**: Macro-F1.
*   **Secondary**: Per-class precision, per-class recall, balanced accuracy, MCC, full $3 \times 3$ confusion matrix.
*   **Descriptive Error Partition**:
    *   *Adjacent errors*: BELOW $\leftrightarrow$ IN-RANGE, IN-RANGE $\leftrightarrow$ ABOVE.
    *   *Non-adjacent errors*: BELOW $\leftrightarrow$ ABOVE.
    *   Counts and proportions reported descriptively. No inferential hypothesis test.

## 9. Applicability Domain & Diagnostics
*   **No Post-Result Selection**: We do NOT designate a “best model” after results. All FOUR learned regression cells (Ridge-descriptors, Ridge-Morgan, RF-descriptors, RF-Morgan) receive the exact same diagnostic suite independently. Mean and median baselines appear in metric tables but do not require molecular applicability-domain plots.
*   **Diagnostic Suite**:
    1. Predicted-versus-observed plot.
    2. Residual distribution.
    3. Maximum Morgan Tanimoto similarity to that compound's outer-training fold versus absolute OOF error.
    4. Spearman correlation ($\rho$) between absolute OOF error and maximum training-set Tanimoto similarity (reported descriptively with no threshold-based decision).
    5. LOWESS curve of absolute OOF error against maximum Tanimoto similarity. LOWESS is frozen entirely via statsmodels: `frac=0.3`, `it=3`, `delta=0.0`.
    6. Top 20 absolute OOF errors.

## 10. S1 Sub-analysis
*   **Rule**: Exactly the 13 unresolved HLM null-at-3 records are removed.
*   **Fold Assignment**: Surviving compounds (Regression N=731, Classifier N=1089) exactly inherit their fold assignments from the primary frozen scaffold split.
*   **Process**: Within each surviving outer-training fold, S1 explicitly reruns:
    *   training-fold preprocessing
    *   descriptor imputation/scaling where applicable
    *   fingerprint variance filtering
    *   inner scaffold-aware hyperparameter selection
    *   regression model fitting
    *   classifier fitting
    *   all applicable regression metrics
    *   all applicable classifier metrics
    *   adjacent/non-adjacent error reporting
    *   applicability-domain analysis
    *   tail-ordering diagnostics
*   **Role**: Primary N=744 remains primary regardless of S1 performance. S1 reveals sensitivity/fragility but can NEVER replace the primary result.

## 11. Tail Ordering Diagnostic
*   **Scope**: Evaluated on continuous regression predictions only.
*   **Method**: Computed explicitly within each separate outer fold independently.
    *   Lower: Compare that fold's held-out BELOW predictions against that SAME fold's held-out IN-RANGE (Q) predictions.
    *   Upper: Compare that fold's held-out ABOVE predictions against that SAME fold's held-out IN-RANGE (Q) predictions.
    *   Ties: Evaluated exactly as $0.5$.
*   **Aggregation**: Sum all concordant-equivalent pair scores across the 5 outer folds, divided by the sum of all eligible within-fold pairs across the 5 outer folds. Cross-fold pairs are absolutely prohibited.
*   **Zero-eligibility Fallback**: If a fold has zero eligible pairs for a tail, it contributes zero to both the numerator and the denominator.
*   **Reporting**: For each tail (Lower, Upper), explicitly report: frozen source cohort total (274 BELOW, 84 ABOVE), actual held-out N evaluated, actual Q N participating, eligible within-fold pair count, concordant-equivalent numerator, and final ordering score. For classifiers, precision/recall and confusion-matrix rows for BELOW/ABOVE are reported instead. Lower and upper results are separate; unequal N implies unequal precision; no significance threshold; no mechanistic inference. Pooled pair counts do NOT make pairwise comparisons independent compound observations.

## 12. TDC Benchmark
*   **Role**: Regression benchmark. Results are for historical comparability only and cannot select the science-track methodology.
*   **Artifact**: PyTDC 1.1.15 `Clearance_Microsome_AZ`.
*   **Split**: Official TDC scaffold split.
*   **Metric**: Official TDC Spearman metric.
*   **Models**: 
    1. Mean baseline
    2. Median baseline
    3. Ridge (descriptors)
    4. Ridge (Morgan)
    5. RF (descriptors)
    6. RF (Morgan)
*   **Hyperparameters**: Chosen using strictly training-data-only inner scaffold-aware CV (3 inner folds using the exact same scaffold-definition implementation) under the exact same fixed grids and tie-breakers.
*   **Caveat**: TDC's bare values at 3 and 150 are used as shipped for benchmark reproduction and are NOT evidence that the corresponding ChEMBL censored observations are exact experimental equality measurements.

## 13. HLM-HH Descriptive Track
*   **Scope**: 187 total strict structures overlap HLM and HH. The primary paired analysis restricts these strictly to compounds assigned to the inferred in-range cohort in BOTH assays. The resulting exact analysis $N$ is deterministically derived and reported prior to computing correlations.
*   **Analysis**: Primary paired Spearman rank correlation. Descriptive 3x3 HLM-class x HH-class cross-tabulation for all overlapping compounds. Count of overlapping compounds carrying the HLM-side 13-record boundary ambiguity.
*   **Paired S1 limb**: Recompute the applicable paired Spearman after removing HLM-side ambiguous null-at-3 records. S1 result is secondary/descriptive.
*   **Prohibited**: No Bland-Altman analysis. No raw HLM/HH ratio. No numerical agreement claim across unlike native units.

## 14. Biogen External Replication
*   **Role**: Independently fitted within-dataset replication.
*   **Methodology**: Uses the exact same continuous-regression representation/model matrix (mean, median, Ridge-descriptors, Ridge-Morgan, RF-descriptors, RF-Morgan). Uses the same seven descriptor definitions, Morgan specifications, preprocessing, estimator settings, inner CV logic, tuning rules, and applicability domain methods. Biogen models are trained only on Biogen.
*   **Sub-cohorts**:
    1.  **Primary**: N=3,087 populated values.
    2.  **Sensitivity**: N=2,129 remaining after removing the 958 minimum-pile-up records. The 2,129 sensitivity records inherit their primary Biogen outer-fold assignments. Preprocessing, inner tuning, and model fits are explicitly rerun on the reduced training folds.
*   **Log Base**: Remains UNKNOWN. No conversion is invented; no AZ two-fold threshold is applied. MAE and RMSE may be reported WITHIN Biogen in its native recorded LOG units; their numerical magnitudes are NOT compared directly with AZ MAE/RMSE. Spearman is the principal base-invariant cross-study qualitative comparison.

## 15. Descriptor Analysis / U6
*   **Role**: Strictly descriptive (boxplots, median, IQR across the 3 classes). Formal hypothesis tests are prohibited.
*   **Timing**: It MUST be completed and its outputs archived BEFORE the first predictive model is fitted. Its results may NOT change descriptors, representations, model families, folds, or hyperparameters. If not completed before first model fitting, it is omitted from v1 and cannot be reinstated after seeing model results.

## 16. Reporting
Frozen outputs explicitly include:
1. Primary and secondary metric tables
2. Predicted-versus-observed plot
3. Residual distribution plot
4. Error-versus-similarity correlation ($\rho$) and LOWESS scatter plot
5. Top 20 OOF absolute errors list
6. Classifier confusion matrix
7. Class precision and recall table
8. Tail-ordering pair counts and scores table
9. S1 comparative results
10. TDC benchmark table
11. HH paired-correlation result
12. Biogen qualitative replication results

Inspection of large errors is interpretive only and cannot trigger v1 model changes.

## 17. Claims Policy
*   **Can Claim**: Accuracy of simple 2D models in prospectively ranking/predicting HLM CLint within the inferred quantifiable-range cohort for this specific chemical space.
*   **Cannot Claim**: Clinical human clearance prediction, patient exposure prediction, causal metabolism, exact latent values for censored observations, unrestricted chemical-domain generalisation.
