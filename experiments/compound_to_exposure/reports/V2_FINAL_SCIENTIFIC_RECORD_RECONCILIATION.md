# Final Scientific Record Reconciliation: V2 Execution 001

## 1. Reconciled Primary Cohort
Counts derived strictly from the immutable `CHEMBL3301370` source and deterministic partition generation (`src/partition.py` and `src/dataset.py`):
- **total assay rows** = 1102
- **<3 left-censored** = 274
- **>150 right-censored** = 84
- **source standard_relation=NULL** = 744
- **NULL-at-3 ambiguous** = 13
- **strict primary point-regression cohort** = NULL relation AND 3 < CLint < 150 = 731
- **primary CV/training pool** = 582
- **primary protected holdout** = 149

The exact number of unique Bemis–Murcko scaffold groups strictly among the 149 primary holdout compounds is **84**. (The previously reported 116 refers to the number of holdout groups across the entire 1102-member master partition, which improperly includes censored/ambiguous compounds).

## 2. Actual Feature Routing in Protected Primary Selection
A line-by-line audit of `src/execute_v2.py` at the exact execution commit `31693d204420fa547a96079ff11988058d133406` reveals a massive provenance breakdown in feature routing.

**The Routing Bug:**
```python
# src/execute_v2.py lines 293, 295
X_tr = X_r1[train_mask] if 'r1' in p_id else X_r2[train_mask]
X_val = X_r1[val_mask] if 'r1' in p_id else X_r2[val_mask]
```
The variable `p_id` is an exact uppercase string `'P1'`, `'P2'`, `'P3'`, or `'P4'`. Because `'r1'` is lowercase, the condition `'r1' in p_id` evaluated to `False` for **all** candidates.

Consequently, **every pipeline** (P1–P4) received `X_r2` (the 2048-bit Morgan fingerprint) during CV and final evaluation.

**Actual Executed Models:**
- **P1:** Actually evaluated Ridge Regression with alpha=1.0 on **Morgan Fingerprints**.
- **P2:** Actually evaluated Ridge Regression with alpha=1.0 on **Morgan Fingerprints**.
- **P3:** Actually evaluated Random Forest on **Morgan Fingerprints**. (The prepended SimpleImputer had zero effect because bit vectors contain no NaNs).
- **P4:** Actually evaluated Random Forest on **Morgan Fingerprints**.

**Resolution of identical P3/P4 MAE:**
P3 and P4 produced the identical grouped-CV MAE `0.33228689634915415` because they were accidentally fed the exact same feature matrix (Morgan fingerprints), trained with the exact same hyperparameters (500 trees, sqrt features) and the exact same seed (`random_state=0`). 

Due to the tie-breaking logic in `tie_break_candidates(a, b)` explicitly preferring representations labeled "R1", P3 won the tie-breaker over P4. The execution then saved predictions under the false provenance that P3 (12-descriptors) had been trained, when it had genuinely trained and predicted using Morgan fingerprints.

Because the system genuinely fed `X_r2` to the model but persisted it under the metadata of `P3` (R1 descriptors), production feature routing accidentally gave them the same representation. **Case 3 has occurred.**

## 3. Reconciled Applicability Domain
Using precisely the 582-member primary CV reference set and comparing strictly using the frozen ECFP4 fingerprint rules, we exactly matched the pre-freeze similarities (`ECFP4_TANIMOTO_PREFREEZE_CHECK`). The previous 852-reference result is explicitly marked **INVALID_SUPERSEDED_RECOVERY**.

**Corrected Bins:**
| Bin | N | Mean AE | Median AE |
|---|---|---|---|
| [0,0.2) | 1 | 0.459766 | 0.459766 |
| [0.2,0.3) | 28 | 0.331983 | 0.291737 |
| [0.3,0.4) | 24 | 0.344038 | 0.298981 |
| [0.4,0.6) | 37 | 0.245387 | 0.220874 |
| [0.6,1.0] | 59 | 0.287288 | 0.246550 |

Corrected continuous Spearman: **-0.031288**

## 4. Top 10 Primary Errors (Actual 12 Descriptors)

1. **CHEMBL1778622** | Obs: 2.127105 | Pred: 1.053030 | Res: -1.074075 | AE: 1.074075 | Mult Err: 11.859728 | NN-Tanimoto: 0.388060 | CCSc1ccc(-c2cc(C(F)(F)F)ccc2OCC(=O)O)cc1
MolWt: 356.365 | MolLogP: 4.9478 | MolMR: 86.4088 | TPSA: 46.53 | HBD: 1.0 | HBA: 3.0 | NumRotatableBonds: 6.0 | RingCount: 2.0 | NumAromaticRings: 2.0 | NumAliphaticRings: 0.0 | FractionCSP3: 0.23529 | HeavyAtomCount: 24.0

2. **CHEMBL574059** | Obs: 2.120014 | Pred: 1.232556 | Res: -0.887458 | AE: 0.887458 | Mult Err: 7.717165 | NN-Tanimoto: 0.378378 | Cn1c(=O)c(-c2c(Cl)cccc2Cl)cc2cnc(Nc3ccc(F)cc3)nc21
MolWt: 415.255 | MolLogP: 5.1850 | MolMR: 109.9177 | TPSA: 59.81 | HBD: 1.0 | HBA: 5.0 | NumRotatableBonds: 3.0 | RingCount: 4.0 | NumAromaticRings: 4.0 | NumAliphaticRings: 0.0 | FractionCSP3: 0.05 | HeavyAtomCount: 28.0

3. **CHEMBL267744** | Obs: 1.913814 | Pred: 1.033420 | Res: -0.880394 | AE: 0.880394 | Mult Err: 7.592655 | NN-Tanimoto: 0.307692 | O=C(O)COc1ccc(C(=O)c2cccs2)c(Cl)c1Cl
MolWt: 331.176 | MolLogP: 3.7493 | MolMR: 77.3443 | TPSA: 63.6 | HBD: 1.0 | HBA: 4.0 | NumRotatableBonds: 5.0 | RingCount: 2.0 | NumAromaticRings: 2.0 | NumAliphaticRings: 0.0 | FractionCSP3: 0.07692 | HeavyAtomCount: 20.0

4. **CHEMBL1738761** | Obs: 0.602060 | Pred: 1.425301 | Res: 0.823241 | AE: 0.823241 | Mult Err: 6.656429 | NN-Tanimoto: 0.211268 | N#Cc1ccc(Cl)cc1O[C@H](CCN)c1ccccc1
MolWt: 286.762 | MolLogP: 3.6806 | MolMR: 79.6494 | TPSA: 59.04 | HBD: 1.0 | HBA: 3.0 | NumRotatableBonds: 5.0 | RingCount: 2.0 | NumAromaticRings: 2.0 | NumAliphaticRings: 0.0 | FractionCSP3: 0.1875 | HeavyAtomCount: 20.0

5. **CHEMBL2021706** | Obs: 1.940018 | Pred: 1.126884 | Res: -0.813134 | AE: 0.813134 | Mult Err: 6.503300 | NN-Tanimoto: 0.269231 | CCC[C@@H](CNC(=O)c1nc(Cl)c(N)nc1N)[N+](C)(C)CCCc1ccc(OC)cc1
MolWt: 450.007 | MolLogP: 2.9107 | MolMR: 125.1864 | TPSA: 116.15 | HBD: 3.0 | HBA: 6.0 | NumRotatableBonds: 11.0 | RingCount: 2.0 | NumAromaticRings: 2.0 | NumAliphaticRings: 0.0 | FractionCSP3: 0.5 | HeavyAtomCount: 31.0

6. **CHEMBL2335901** | Obs: 0.620136 | Pred: 1.372133 | Res: 0.751997 | AE: 0.751997 | Mult Err: 5.649331 | NN-Tanimoto: 0.465753 | C[C@@H](NC(=O)C1CCNCC1)c1ccc(Nc2ncc3cc(-c4ccncc4)ccc3n2)cc1
MolWt: 452.562 | MolLogP: 4.6122 | MolMR: 134.6451 | TPSA: 91.83 | HBD: 3.0 | HBA: 6.0 | NumRotatableBonds: 6.0 | RingCount: 5.0 | NumAromaticRings: 4.0 | NumAliphaticRings: 1.0 | FractionCSP3: 0.25926 | HeavyAtomCount: 34.0

7. **CHEMBL100391** | Obs: 0.698970 | Pred: 1.438554 | Res: 0.739584 | AE: 0.739584 | Mult Err: 5.490150 | NN-Tanimoto: 0.272727 | CN(C)CC(O)COc1ccc(Nc2ncc(Cl)c(Nc3ccccc3)n2)cc1
MolWt: 413.909 | MolLogP: 3.9185 | MolMR: 116.5472 | TPSA: 82.54 | HBD: 3.0 | HBA: 7.0 | NumRotatableBonds: 9.0 | RingCount: 3.0 | NumAromaticRings: 3.0 | NumAliphaticRings: 0.0 | FractionCSP3: 0.23810 | HeavyAtomCount: 29.0

8. **CHEMBL1807823** | Obs: 0.698970 | Pred: 1.414068 | Res: 0.715098 | AE: 0.715098 | Mult Err: 5.189168 | NN-Tanimoto: 0.815385 | O=c1[nH]c2c(O)ccc([C@@H](O)CNCCSCCCNCCc3ccccc3)c2s1
MolWt: 447.626 | MolLogP: 2.8738 | MolMR: 126.8977 | TPSA: 97.38 | HBD: 5.0 | HBA: 7.0 | NumRotatableBonds: 13.0 | RingCount: 3.0 | NumAromaticRings: 3.0 | NumAliphaticRings: 0.0 | FractionCSP3: 0.40909 | HeavyAtomCount: 30.0

9. **CHEMBL182682** | Obs: 2.049218 | Pred: 1.361915 | Res: -0.687303 | AE: 0.687303 | Mult Err: 4.867470 | NN-Tanimoto: 0.477612 | COc1ccc(CC(=O)N(C)C2CCN(CCC(c3ccccc3)c3ccccc3)CC2)cc1OC
MolWt: 486.656 | MolLogP: 5.3913 | MolMR: 144.8260 | TPSA: 42.01 | HBD: 0.0 | HBA: 4.0 | NumRotatableBonds: 10.0 | RingCount: 4.0 | NumAromaticRings: 3.0 | NumAliphaticRings: 1.0 | FractionCSP3: 0.38710 | HeavyAtomCount: 36.0

10. **CHEMBL20210** | Obs: 2.019988 | Pred: 1.345975 | Res: -0.674013 | AE: 0.674013 | Mult Err: 4.720774 | NN-Tanimoto: 0.538462 | CCOC(=O)/C=C/[C@H](C[C@@H]1CCNC1=O)NC(=O)[C@@H](CC(=O)[C@@H](NC(=O)c1cc(C)on1)C(C)C)Cc1ccc(F)cc1
MolWt: 598.672 | MolLogP: 2.8249 | MolMR: 153.9876 | TPSA: 156.70 | HBD: 3.0 | HBA: 8.0 | NumRotatableBonds: 15.0 | RingCount: 3.0 | NumAromaticRings: 2.0 | NumAliphaticRings: 1.0 | FractionCSP3: 0.48387 | HeavyAtomCount: 43.0

## 5. Reconciled HLM–HH Definitions
- **Paired cohort N=187**
- **Primary N=94**: Derived strictly from pairs where both HLM and HH had an unqualified/NULL standard relation and fell within the strictly observed interior interval (3 < x < 150).
- **Sensitivity N=96**: Adds precisely two compounds (**CHEMBL271012** and **CHEMBL552512**). Under the frozen `BOUNDARY_AMBIGUOUS` specification, these had unqualified/NULL relations but were recorded exactly on the boundaries (x=3.0 or x=150.0) in HLM, paired with `INTERIOR_OBSERVED` values in HH.

Independently verified and preserved Spearmans and provenance labels:
- **primary Spearman:** 0.504526766825069
- **sensitivity Spearman:** 0.4864353376748756
- Provenance-correct labels `<, unqualified/NULL, >` verified.

## 6. Git Provenance
- **Peeled dmpk-v2-execution-ready-v3^{} commit:** `31693d204420fa547a96079ff11988058d133406`
- **Protected run's recorded execution commit:** `31693d204420fa547a96079ff11988058d133406` (from `18T215009395468_0000-4c110e67.started.json`)
- **Current HEAD:** `6476129a543f125263e7631d89420aa4d4234cec` (Recovery/Report commit)
- **Confirmation:** The protected run *was* launched from the true execution-ready commit (`31693d204420fa547a96079ff11988058d133406`). 

## 7. Protected Primary Metrics
The following metrics are derived entirely from the protected 149 point-prediction artifact and depend exclusively on the strictly defined interior cohort and 582 CV records:
- **MAE:** 0.2955808045870799
- **baseline MAE:** 0.3513546317442397
- **Δ:** 0.05577382715715978
- **RMSE:** 0.36924301920763986
- **Spearman:** 0.43682578549670603
- **R²:** 0.20050067197777244
- **within-twofold:** 0.5704697986577181
- **scaffold-bootstrap CI:** [0.022749898278188855, 0.09452515112530031]

These values are mathematically uncorrupted by extraction logic flaws and remain valid summaries of what the artifact *actually produced*. However, due to the routing bug, they represent the performance of a **Morgan Fingerprint (R2)** model, not the R1 descriptors model the artifact was falsely marked as.

## 8. Summary Table

| Previous extracted claim | Correct value | Root cause | Scientific consequence |
|---|---|---|---|
| 116 unique holdout scaffolds | 84 primary holdout scaffolds | Previous extraction incorrectly counted unique scaffolds across the entire 1102 master partition, including censored rows. | Minor demographic correction; primary point-regression validation metrics were unaffected. |
| P3 and P4 MAEs identical due to R1/R2 similarity | Identical because they both used Morgan Fingerprints (R2) | `if 'r1' in p_id` evaluated to False for `'P3'` and `'P4'`, feeding R2 arrays to all estimators in `src/execute_v2.py`. | **Catastrophic Provenance Failure**: Selected P3 model claimed R1 descriptors but was trained on R2 Morgan fingerprints. |
| AD Bins: 0/22/21/30/76 | 1/28/24/37/59 | Extractor improperly cross-referenced against all 852 CV records instead of the 582 primary quantitative CV records. | Original applicability bins were recovered and exactly matched pre-execution constraints. |

V2_PRIMARY_SELECTION_PROVENANCE_COMPROMISED
