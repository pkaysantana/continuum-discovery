# Compound-to-Exposure: In Vitro HLM Clearance Prediction

## Scientific Question
How well can simple 2D molecular representations predict experimentally reported human liver microsomal intrinsic clearance under chemically held-out validation, and where do those predictions fail?

## Why HLM Clearance?
In the DMPK context, a critical progression is:
*chemistry → metabolic stability/intrinsic clearance → systemic PK/exposure*

Human Liver Microsomes (HLM) provide a simplified *in vitro* system to assess Phase I metabolic stability (primarily cytochrome P450-mediated metabolism). This project explicitly **stops at the in-vitro HLM level**. It does not attempt to predict *in vivo* clearance or model patient exposure, as those require substantial additional physiological and compartmental inputs.

## Data

### Direct AZ/ChEMBL HLM
The primary dataset is derived from ChEMBL3301370, representing a direct AstraZeneca assay for human liver microsome apparent intrinsic clearance.
*   **Total Source N:** 1102
*   **Primary Continuous N:** 744 (IN-RANGE subset)
*   **Censoring:** 274 BELOW limit, 84 ABOVE limit.

### TDC Historical Benchmark
The historical `Clearance_Microsome_AZ` dataset from PyTDC 1.1.15. This dataset heavily overlaps with the direct AZ source. It is used strictly for historical benchmark comparability and **is NOT an independent external validation**.
*   **Train:** 771
*   **Valid:** 110 (Used exclusively for hyperparameter selection)
*   **Test:** 221 (Used for the single final evaluation)

### Human Hepatocyte Paired Dataset
A secondary paired dataset matching overlapping compounds in Human Hepatocytes (HH, ChEMBL3301372). Hepatocytes are intact whole cells. 
*   **Paired N:** 187 exact overlapping structures
*   **Doubly-in-range continuous N:** 96

### Independent Biogen HLM Dataset
An independent historical public HLM dataset used to assess methodology reproducibility.
*   **Total Source N:** 3521
*   **Populated N:** 3087
*   **Missing Target N:** 434
*   **Caveat:** The Biogen dataset contains an unresolved accumulation of 958 observations at a single minimum value, and the explicit log base convention is undefined. 

## Censoring and Data-Quality Policy
*   **<3 and >150 Limits:** Historical values explicitly qualified with inequalities were treated strictly as censored categories (BELOW/ABOVE) rather than invented continuous numerical values.
*   **Ambiguous Records:** 13 HLM records containing the exact scalar value 3.0 with no relation qualifier were flagged. Sensitivity analyses confirmed the major conclusions were robust to these observations.
*   **Biogen Minimum Pile-up:** The 958 records piled at 0.675686709 were retained in the primary track because they are not proven to be censored limits. Sensitivity analysis assessed their impact.

## Modelling
*   **Representations:** 7 fundamental RDKit physicochemical descriptors versus high-dimensional Morgan fingerprints.
*   **Algorithms:** Ridge (regularized linear) and Random Forest (non-linear tree ensemble) for both regression and classification.
*   **Validation:** 5-fold StratifiedGroupKFold on explicit Bemis-Murcko scaffolds to prevent chemically inflated metrics.
*   **Baselines:** Trivial mean/median and majority class baselines to explicitly benchmark useful predictive lift.
*   **Tuning:** Nested inner cross-validation strictly held within the training folds.

## Results

### AZ Primary
*   **Regression (N=744):** Random Forest with Morgan fingerprints achieved the best absolute error (MAE ≈ 0.326, Spearman $\rho \approx 0.417$). Ridge Morgan achieved MAE ≈ 0.334 and Spearman $\rho \approx 0.391$. Descriptors provided substantially lower rank correlation for Ridge ($\rho \approx 0.120$). All learned cells beat the trivial baseline (MAE ≈ 0.376).
*   **Classification (N=1102):** RF Morgan achieved the highest Macro-F1 (0.481), heavily outperforming the majority baseline (0.269).
*   **Tail Ordering:** Models successfully discriminated both lower (stable) and upper (unstable) extremes (Tail scores 0.645–0.716).
*   **Sensitivity (S1):** Removing the 13 ambiguous null-at-3 observations left metrics virtually unchanged (RF Morgan MAE ≈ 0.322).

### TDC Benchmark
*   **Convention:** Train-only fit (Valid used solely for hyperparameter selection).
*   **Results (N=221 Test):** Ridge Morgan achieved the best rank-ordering (Spearman $\rho \approx 0.499$), substantially outperforming baseline predictions.

### HLM–HH Paired Analysis
*   **Category Agreement (N=187):** Majority censoring-category agreement was observed (68.45% exact agreement), with no observed non-adjacent BELOW↔ABOVE disagreements.
*   **Continuous Agreement (N=96):** Moderate rank correlation was preserved (Spearman $\rho \approx 0.486$).
*   **Sensitivity (S1):** N=94, Spearman $\rho \approx 0.505$.

### Biogen Replication
*   **Primary (N=3087):** RF Descriptors ($\rho \approx 0.551$), Ridge Descriptors ($\rho \approx 0.549$), and Ridge Morgan ($\rho \approx 0.541$) all achieved robust rank-ordering. 
*   **Sensitivity (N=2129):** After excluding the 958 unresolved minimum-valued records, MAE and RMSE decreased while Spearman rank correlation also decreased. Because the sensitivity cohort differs substantially in target distribution and composition, these changes are not attributed to a single cause.

## Cross-Study Findings
*   Molecular structure contains reproducible information about reported *in-vitro* HLM intrinsic-clearance behaviour beyond trivial baselines.
*   Representation/model superiority is dataset-dependent: Morgan is particularly useful in AZ/TDC, while seven simple physicochemical descriptors can retain substantial predictive signal, particularly in Biogen, but their usefulness relative to Morgan fingerprints is dataset- and model-dependent.
*   HLM and intact human hepatocytes preserve moderate relative clearance ranking but are not numerically interchangeable.
*   Maximum training-set Morgan similarity is at most a weak predictor of model error and does not provide a robust cross-dataset confidence rule.

### Cross-Study Spearman Comparison

| Model | AZ primary | TDC test | Biogen primary | Biogen sensitivity |
| :--- | :--- | :--- | :--- | :--- |
| **Ridge descriptors** | 0.120 | 0.146 | 0.549 | 0.378 |
| **Ridge Morgan** | 0.391 | 0.499 | 0.541 | 0.384 |
| **RF descriptors** | 0.362 | 0.266 | 0.551 | 0.400 |
| **RF Morgan** | 0.417 | 0.371 | 0.485 | 0.343 |

*(Note: MAE cannot be compared directly across AZ and Biogen due to the unresolved Biogen log base and native unit scaling differences.)*

## Limitations
1. **Public historical assay data:** These are retrospective agglomerations of legacy assay data spanning many years, carrying unmeasured experimental variance.
2. **Censoring constraints:** Exact continuous values for historically censored limits are impossible to recover.
3. **Biogen dataset ambiguity:** The precise mathematical log base and the origin of the 958-value pileup are unresolved.
4. **No prospective wet-lab validation:** The models have not been used to prospectively synthesize and assay novel compounds.
5. **No IVIVE / Exposure:** No *in vivo* clearance modeling, IVIVE scaling, or patient exposure prediction was performed.
6. **Independent replication limitation:** The Biogen track represents within-dataset replication of the methodology; it is NOT an external *AZ→Biogen transfer* validation.

## Reproducibility
*   **Preregistration:** Analytical constraints, censoring logic, and structural descriptors were prospectively frozen prior to modelling (see `dmpk-modelling-preregistration-v1`).
*   **Frozen Commits & Tags:** Major milestones are indelibly recorded by Git annotated tags (`dmpk-primary-models-v1`, `dmpk-tdc-benchmark-v1`, `dmpk-hlm-hh-v1`, `dmpk-biogen-replication-v1`).
*   **Deterministic Folds:** Outer folds were generated and cryptographic hashes committed *before* training.
*   **Deterministic Reruns:** Execution was subjected to independent deterministic reruns which passed exactly (numerical tolerance < 1e-12).
