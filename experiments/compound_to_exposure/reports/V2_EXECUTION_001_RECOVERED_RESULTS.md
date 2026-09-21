# V2 Execution 001 Recovered Results

This report documents the post-access artifact recovery for the protected primary run `2026-09-18T215009395468_0000-4c110e67`, performing deterministic recovery without model execution. 

## 1. Primary Model Performance

**Selected Pipeline/Configuration:**
`PERSISTED_DURING_PROTECTED_RUN`
- **Pipeline:** P3 (RandomForestRegressor)
- **Hyperparameters:** `max_features` = "sqrt", `min_samples_leaf` = 1, `n_estimators` = 500, `max_depth` = null, `random_state` = 0

**Primary Metrics:**
`DETERMINISTICALLY_RECOVERED_FROM_PERSISTED_PREDICTIONS`
- **CV Selection MAE:** 0.33228689634915415 (Persisted in selection manifest)
- **Primary Holdout MAE:** 0.2955808045870799
- **Median-Baseline MAE:** 0.3513546317442397
- **Correctly Signed Δ (Baseline - Model):** 0.05577382715715978
- **RMSE:** 0.36924301920763986
- **Spearman:** 0.43682578549670603
- **R²:** 0.20050067197777244
- **Within-Twofold Proportion:** 0.5704697986577181 (57.05%)

## 2. Scaffold-Bootstrap Interval
`DETERMINISTICALLY_RECOVERED_FROM_PERSISTED_PREDICTIONS`
- **95% Scaffold-Bootstrap CI for Δ:** [0.022749898278188855, 0.09452515112530031]
- **Frozen Improvement Conclusion:** Improvement demonstrated (lower bound > 0).

## 3. Applicability-Domain & Error Diagnostics
`DETERMINISTICALLY_RECOVERED_FROM_PERSISTED_PREDICTIONS`
- **Min Prediction:** 0.8331148184738654
- **Max Prediction:** 1.9098394713529616
- **Mean Residual:** 0.04536165635269869
- **Continuous Spearman (Abs Error vs Nearest Tanimoto):** -0.06340010067837754

**Absolute Error by Frozen Tanimoto Bins:**
*(Calculated using nearest-training similarity strictly against the 582 primary CV references)*
```
Bin          Count    Mean AE    Median AE
[0,0.2)          1   0.459766     0.459766
[0.2,0.3)       28   0.331983     0.291737
[0.3,0.4)       24   0.344038     0.298981
[0.4,0.6)       37   0.245387     0.220874
[0.6,1.0]       59   0.287288     0.246550
```

**Top 10 Absolute Error Compounds:**
1. CHEMBL1778622: 1.074075
2. CHEMBL574059: 0.887458
3. CHEMBL267744: 0.880394
4. CHEMBL1738761: 0.823241
5. CHEMBL2021706: 0.813134
6. CHEMBL2335901: 0.751997
7. CHEMBL100391: 0.739584
8. CHEMBL1807823: 0.715098
9. CHEMBL182682: 0.687303
10. CHEMBL20210: 0.674013

## 4. HLM-HH deterministic recovery
**Spearman Statistics:**
`PERSISTED_DURING_PROTECTED_RUN` (Recovered from `v2_execution_state.json`)
- **HLM-HH Primary N=94 Spearman:** 0.504526766825069
- **HLM-HH Sensitivity N=96 Spearman:** 0.4864353376748756

**Qualifier Contingency Table:**
`DETERMINISTICALLY_RECOVERED_FROM_FROZEN_SOURCE_DATA`
```
standard_relation_hh    <    unqualified/NULL  >  All
standard_relation_hlm                 
<                      31                  20  0   51
unqualified/NULL       26                  96  5  127
>                       0                   8  1    9
All                    57                 124  6  187
```

## 5. Incomplete Stages
`INCOMPLETE_AFTER_PROTECTED_EXECUTION`
- **Tail C_L/C_U evaluation:** Incomplete (out-of-fold predictions not persisted).
- **Sensitivity A:** Incomplete (predictions/results not persisted).
- **Sensitivity B:** Incomplete (predictions/results not persisted).
- **Biogen (B1 and B2):** Incomplete (interrupted before any model outputs were persisted).

## 6. Task 126 Verification
Task 126 (`2026-09-18T221459876805_0000-12e19f8d`) did not create a second protected evaluation. It generated an empty run directory and `.started.json` but never reached `.fit()`, `.predict()`, or generated any predictions or artifacts.

---
**Recovery Status:** PRIMARY_RESULT_RECOVERY_COMPLETE
