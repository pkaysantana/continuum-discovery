# Frozen Results Record

- **Git Commit Hash**: 925e71e99c91f03cd081104339cf6d19fda3f8ee
- **Scaffold-vs-Random Paired Bootstrap**: mean 0.0183, 95% CI [0.0006, 0.0348], fraction <=0 0.0190
- **Non-finite Descriptor Cells (across all 1,089)**: 0
- **Canonical SMILES Integrity**: verified against ChEMBL full_mwt for all 1,089 compounds, 0 rows differing by more than 0.1 Da. (Note: the check used canonical_smiles_rdkit from get_cohorts() and was not run separately against data/interim/CHEMBL3301370_rows.csv.)

## Pipeline selection defect
src/execute_v2.py selects the feature matrix with `'r1' in p_id` in BOTH the CV loop and the final fit. Pipeline ids are P1-P4; `'r1' in 'P3'` is False for all of them, so every candidate was evaluated and fitted on ECFP4 (X_r2). No candidate was ever evaluated on R1 descriptors. The stored holdout predictions are therefore ECFP4-based. Record that the bug is UNFIXED and that results predate any fix.

## Stored-prediction provenance
ECFP4 (Morgan r=2, 2048 bit) with max_features=1.0, because execute_v2.py uses the pipeline as constructed and does not apply selection_manifest.json params.

## 1. Dataset Counts
- Total Compounds: 1089
- Interior ($3 \le x \le 150$): 731
- Left-censored (< 3): 274
- Right-censored (> 150): 84
- Protected Holdout: 187 (classification), 149 (regression)

## 2. Baseline Variance (Interior 731)
- Total variance of log10 CLint: 0.1858
- Total SD of log10 CLint: 0.4310

## 3. Ceiling R² Estimates
*ASSUMPTION-DEPENDENT: These estimates assume true within-assay standard deviations of 0.25, 0.30, and 0.347 respectively.*
- Ceiling R² at 0.25 SD: 0.6635
- Ceiling R² at 0.30 SD: 0.5155
- Ceiling R² at 0.347 SD: 0.3518

## 4. Headline Performance Numbers (20 GroupShuffleSplit Seeds)
*(Holdout percentile within each 20-split distribution at max_features=1.0: ECFP4 45.0, R1 0.0, R1+2 5.0.)*

| Task | Metric | Median | Min | Max | SD | 5th-95th Percentile |
|------|--------|--------|-----|-----|----|---------------------|
| Classification RF/ECFP4 | ROC-AUC | 0.7616 | 0.6481 | 0.8210 | 0.0400 | 0.7115 - 0.8151 |
| Classification RF/descriptor panel | ROC-AUC | 0.7685 | 0.6605 | 0.8416 | 0.0470 | 0.6806 - 0.8326 |
| Classification RF/ECFP4+descriptors | ROC-AUC | 0.7860 | 0.6888 | 0.8550 | 0.0380 | 0.7451 - 0.8439 |
| Regression RF/ECFP4 | R² | 0.2105 | 0.0499 | 0.3017 | 0.0533 | 0.1336 - 0.2669 |
| Regression RF/R1 | R² | 0.1388 | 0.0422 | 0.2287 | 0.0539 | 0.0716 - 0.2255 |
| Regression RF/R1+2 | R² | 0.1667 | 0.0398 | 0.2653 | 0.0587 | 0.0677 - 0.2353 |

**Paired by split (n=20):**
ECFP4 - R1     mean +0.0542, SD 0.0659, t=3.68, p=0.0016, 15/20 seeds
ECFP4 - R1+2   mean +0.0428, SD 0.0726, t=2.64, p=0.016,  14/20 seeds
R1+2  - R1     mean +0.0114, SD 0.0223, t=2.29, p=0.034,  13/20 seeds
(Wilcoxon: 0.0020, 0.0215, 0.0673. Sign test: 0.041, 0.115, 0.263.)

## 5. Paired Bootstrap AUC Differences (2000 resamples)
**All 902 CV Compounds:**
- RF/ECFP4 minus RF/descriptors: Mean Difference = -0.0035, 95% CI [-0.0328, 0.0257], Fraction <= 0: 0.5905
- RF/ECFP4+descriptors minus RF/ECFP4: Mean Difference = 0.0294, 95% CI [0.0159, 0.0427], Fraction <= 0: 0.0000

**Interior Only (731 Compounds):**
- RF/ECFP4 minus RF/descriptors: Mean Difference = -0.0018, 95% CI [-0.0425, 0.0383], Fraction <= 0: 0.5315
- RF/ECFP4+descriptors minus RF/ECFP4: Mean Difference = 0.0180, 95% CI [-0.0001, 0.0362], Fraction <= 0: 0.0265

## Units note
standard_units in the extract is mL.min-1.g-1, which is numerically identical to uL/min/mg (1000 uL / 1000 mg). No rescaling is applied anywhere.

## 6. 14-descriptor exploratory panel (NOT R1)
*Note: This comes from a CLASSIFICATION model on a 14-descriptor exploratory panel, not from the regression and not from R1.*
1. AcidicCentres: 0.081494
2. MolLogP: 0.038766
3. NumRotatableBonds: 0.009078
4. RingCount: 0.007076
5. NumAromaticRings: 0.005747
6. NumSaturatedRings: 0.005084
7. BasicCentres: 0.004422
8. NumHDonors: 0.003532
9. NumHAcceptors: 0.002630
10. FormalCharge: 0.000001
11. HeavyAtomCount: -0.002448
12. MolWt: -0.003818
13. TPSA: -0.004012
14. FractionCSP3: -0.010641

## 7. cLogP vs Fraction Stable
| cLogP Bin | Count | Fraction Stable |
|---|---|---|
| (-1.972, 2.027] | 91 | 0.659341 |
| (2.027, 2.69] | 90 | 0.411111 |
| (2.69, 3.07] | 90 | 0.433333 |
| (3.07, 3.438] | 90 | 0.477778 |
| (3.438, 3.706] | 90 | 0.300000 |
| (3.706, 4.045] | 90 | 0.433333 |
| (4.045, 4.405] | 90 | 0.377778 |
| (4.405, 4.84] | 91 | 0.439560 |
| (4.84, 5.383] | 89 | 0.528090 |
| (5.383, 10.343] | 91 | 0.472527 |

## 8. Inter-Lab Assay Reproducibility (ChEMBL 3301361/3301370-3301372)
computed 2026-09-18, script scratch/task_b.py, not re-verified this session
- Overlapping compounds: 34
- Mean difference (log10): +0.1601
- Standard Deviation: 0.4907
- Interquartile Range (IQR): 0.5487

## 9. Stored-Prediction Holdout Metrics
- R²: 0.2005
- Pearson r: 0.4612
- Spearman rho: 0.4368
- RMSE: 0.3692
- MAE: 0.2956
- Calibration slope: 0.9762
- sd ratio: 0.4724
- corr(obs, resid): -0.8814

*Corrected explanation of the 0.224 figure:* The identity `corr(obs, resid) = -sqrt(1 - R²)` is exact only when the calibration slope equals exactly 1. The calibration slope for the stored predictions was 0.9762, plus a small mean offset, which shifts the calculated `0.2231` (from `-0.8814`) to the true `0.2005`. Model class is irrelevant.

## 10. Environment Info
- rdkit: 2025.03.6
- scikit-learn: 1.9.1
- pandas: 3.0.5
- numpy: 2.2.6

## 11. R1 descriptor definition (NOT the representation actually used)

The fitted representation was ECFP4.

**R1 descriptors verbatim from `src/representations.py`:**
```python
# Frozen R1 descriptors
R1_PROPERTIES = (
    'MolWt', 'MolLogP', 'MolMR', 'TPSA', 'NumHDonors', 'NumHAcceptors',
    'NumRotatableBonds', 'RingCount', 'NumAromaticRings', 'NumAliphaticRings',
    'FractionCSP3', 'HeavyAtomCount'
)

def get_r1_descriptors(smiles):
    """
    Computes the 12 frozen RDKit descriptors for a given SMILES string.
    Returns a dictionary mapping descriptor name to its computed value.
    If the SMILES is unparseable or cannot be computed, returns None.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
        
    try:
        Chem.SanitizeMol(mol)
    except:
        pass # RDKit might fail on some molecules, let's see if descriptors still work
        
    desc_dict = {}
    
    try:
        desc_dict['MolWt'] = Descriptors.MolWt(mol)
        desc_dict['MolLogP'] = Crippen.MolLogP(mol)
        desc_dict['MolMR'] = Crippen.MolMR(mol)
        desc_dict['TPSA'] = rdMolDescriptors.CalcTPSA(mol)
        desc_dict['NumHDonors'] = Lipinski.NumHDonors(mol)
        desc_dict['NumHAcceptors'] = Lipinski.NumHAcceptors(mol)
        desc_dict['NumRotatableBonds'] = rdMolDescriptors.CalcNumRotatableBonds(mol, rdMolDescriptors.NumRotatableBondsOptions.Strict)
        desc_dict['RingCount'] = Lipinski.RingCount(mol)
        desc_dict['NumAromaticRings'] = Lipinski.NumAromaticRings(mol)
        desc_dict['NumAliphaticRings'] = Lipinski.NumAliphaticRings(mol)
        desc_dict['FractionCSP3'] = rdMolDescriptors.CalcFractionCSP3(mol)
        desc_dict['HeavyAtomCount'] = Lipinski.HeavyAtomCount(mol)
    except Exception as e:
        # If any descriptor fails, we could return NaNs, but the SAP says
        # "descriptors are computed for all 1,102 records and the count of non-finite cells is reported."
        # If a molecule totally fails, we might return NaNs for all
        return {p: np.nan for p in R1_PROPERTIES}
        
    # Ensure they are in exact order if we convert to list
    return desc_dict
```
