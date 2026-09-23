# Whole-Cohort Structure Integrity Audit Report

| Layer | N audited | N mismatched | N unresolved | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Raw → interim** | 1,102 | 0 | 0 | **PASS** |
| **Interim → get_cohorts** | 1,102 | 0 | 0 | **PASS** |
| **ID → structure** | 1,102 | 0 | 0 | **PASS** |
| **Structure → descriptors** | 1,102 | 0 | 0 | **PASS** |
| **Structure → ECFP4** | 1,102 | 0 | 0 | **PASS** |
| **Structure → scaffold** | 1,102 | 0 | 0 | **PASS** |
| **Interior 731** | 731 | 0 | 0 | **PASS** |
| **CV 582** | 582 | 0 | 0 | **PASS** |
| **Holdout 149** | 149 | 0 | 0 | **PASS** |

**Date**: 2026-09-23  
**Dataset**: ChEMBL Target CHEMBL3301370 (AstraZeneca Human Liver Microsomal $CL_{int}$)  
**Cohort Size**: 1,102 total records (731 interior, 274 left-censored, 84 right-censored, 13 boundary-ambiguous)  
**Branch**: `audit/whole-cohort-structure-integrity`  

---

## Executive Summary

This scientific data-integrity audit was conducted to investigate potential structure misalignment across the entire modelled cohort of dataset `CHEMBL3301370`. The audit was initiated following an independent review that raised concerns regarding two specific case-study compounds:
1. **`CHEMBL1778622`**: Descriptors appeared associated with one structure while a printed SMILES differed by approximately one methylene unit ($\approx 14\text{ Da}$, 1 $\text{CH}_2$);
2. **`CHEMBL1807823`**: A molecular weight corresponding to Raloxifene (473.64 Da) appeared in a case-study printout against an actual target structure of MW 447.63 Da.

An exhaustive, deterministic audit was performed across **all 1,102 records** from the historical raw source files through interim preprocessing, scientific cohort subsetting, Murcko scaffold partitioning, feature generation (RDKit 1D/2D descriptors and 2048-bit Morgan ECFP4 fingerprints), target array indexing, and model matrix alignment.

### Key Conclusions
1. **Zero Pipeline Corruption**: Across all 1,102 records and all pipeline layers, there is **zero evidence of data corruption, row shifting, or misaligned features**. Every row in the training, CV, and holdout feature matrices ($X$) is strictly and deterministically aligned with its corresponding target ($y$), compound identifier, and scaffold partition key.
2. **Root Cause of Review Discrepancies**: The anomalies noted in the review were strictly isolated to an exploratory post-hoc reporting script (`scratch/orig_extract_case_studies.py`) that performed unkeyed/offset array lookups during text table rendering. These errors never touched the source data, the pipeline data structures, or the model training/evaluation arrays.
3. **Descriptor Precision**: All 1,102 compounds exhibit 100.0% exact numerical agreement between recomputed RDKit descriptors and the stored interim dataset columns.
4. **Scaffold & Partition Invariance**: All 1,102 Bemis-Murcko scaffolds match `splits/master_partition.csv` exactly, confirming zero leakage across the 5-fold CV splits (582 compounds) and protected holdout split (149 compounds).

---

---

## Detailed Audit Findings (Parts A through L)

### Part A: Historical ChEMBL 20 Source Data Audit
- **Files Audited**:
  - `data/raw/chembl/CHEMBL3301370_activities_00000.json` (1,000 records)
  - `data/raw/chembl/CHEMBL3301370_activities_01000.json` (102 records)
- **Record Counts**:
  - Total activity records: **1,102**
  - Distinct `activity_id` values: **1,102**
  - Distinct `molecule_chembl_id` values: **1,102**
  - Distinct `canonical_smiles` strings: **1,102**
  - Missing molecule IDs: **0**
  - Missing or blank SMILES strings: **0**
- **Parent Molecule Alignment**: Every record maps 1:1 to a corresponding parent molecule ID with 0 unresolved relationships.

### Part B: Ingestion Pipeline Audit (Raw $\to$ Interim)
- **Interim File**: `data/interim/CHEMBL3301370_rows.csv`
- Total rows loaded: **1,102**
- Sequential row-by-row correspondence between the raw activity JSONs and interim CSV:
  - `activity_id` mismatches: **0**
  - `molecule_chembl_id` mismatches: **0**
  - `canonical_smiles` mismatches: **0**
  - `parent_molecule_chembl_id` mismatches: **0**
- Deterministic 1:1 mapping verified across the entire table.

### Part C: DataFrame Operation & Pipeline Trace Audit
An exhaustive code inspection and programmatic trace of all DataFrame operations (`merge`, `join`, `concat`, `sort_values`, `reset_index`, `groupby`, `.iloc`, `.values`) was executed across `src/dataset.py`, `src/partition.py`, and `src/execute_v2.py`:

| Component / Function | Operation | Alignment Key | Order Preserved? | Off-by-one Risk |
| :--- | :--- | :--- | :---: | :---: |
| `src/dataset.py` (`load_chembl3301370_raw`) | `pd.read_csv + rename` | Sequential index | YES | NONE |
| `src/dataset.py` (`get_cohorts`) | Boolean indexing masks | Positional boolean slice | YES | NONE |
| `src/partition.py` (`compute_master_partition`) | `apply(get_scaffold_key)` | Per-row apply | YES | NONE |
| `src/partition.py` (`compute_master_partition`) | `groupby('scaffold_key')` | `scaffold_key` | N/A (Holdout set budget) | NONE |
| `src/partition.py` (`compute_master_partition`) | `map(group_folds)` to original `df` | `scaffold_key` | YES (Direct column write) | NONE |
| `src/execute_v2.py` (Preflight check) | `df_p.merge(partition_df)` | `chembl_id` (Unique 1:1) | YES | NONE |
| `src/execute_v2.py` (Model execution) | `df_primary.merge(part_map, how='left')` | `chembl_id` (Unique 1:1 index) | YES | NONE |
| `src/execute_v2.py` (Feature construction) | `[get_r2_morgan(s) for s in df_p[...]]` | Direct iteration over `df_p` | YES | NONE |
| `src/execute_v2.py` (Target construction) | `y = df_primary['log10_CLint'].values` | Direct Series values | YES | NONE |

**Findings**:
- In `execute_v2.py`, `df_primary` is merged with `part_map` on `chembl_id` using `how='left'`. Because `chembl_id` is unique across all rows, pandas guarantees that the original row sequence is perfectly preserved.
- Slicing using `cv_mask = df_primary['partition'] == 'cv'` and `holdout_mask = df_primary['partition'] == 'holdout'` operates simultaneously on feature arrays $X$ and target vectors $y$, preventing any positional desynchronization.

### Part D: Deterministic Internal Alignment
- Re-evaluated all 1,102 SMILES through RDKit 2024.03.5:
  - Canonical isomeric SMILES generated via `Chem.MolToSmiles(Chem.MolFromSmiles(s), canonical=True, isomericSmiles=True)`.
  - Compared against `canonical_smiles_rdkit` stored in `CHEMBL3301370_rows.csv` and used throughout modelling.
  - Result: **0 mismatches** (1,102 / 1,102 exact string matches).
  - Graph mismatches: **0**
  - Salt / fragment differences: **0**
  - Stereochemical differences: **0**
  - Tautomeric discrepancies: **0**

### Part E: Descriptor Integrity
- Recomputed all R1 physicochemical descriptors and compared against stored values in `CHEMBL3301370_rows.csv`:
  - `molecular_weight` vs `MolWt`: 1,102 / 1,102 exact matches ($\Delta_{\max} = 0.00$)
  - `clogp` vs `MolLogP`: 1,102 / 1,102 exact matches ($\Delta_{\max} = 0.00$)
  - `tpsa` vs `TPSA`: 1,102 / 1,102 exact matches ($\Delta_{\max} = 0.00$)
  - `hbd` vs `NumHDonors`: 1,102 / 1,102 exact matches ($\Delta_{\max} = 0.00$)
  - `hba` vs `NumHAcceptors`: 1,102 / 1,102 exact matches ($\Delta_{\max} = 0.00$)
  - `rotatable_bonds` vs `NumRotatableBonds`: 1,102 / 1,102 exact matches ($\Delta_{\max} = 0.00$)
  - `fraction_csp3` vs `FractionCSP3`: 1,102 / 1,102 exact matches ($\Delta_{\max} = 0.00$)
- Computed R1+2 additional ionisable descriptors (AcidicCentres, BasicCentres):
  - AcidicCentres: Range [0, 2], mean = 0.20
  - BasicCentres: Range [0, 8], mean = 1.43
  - 100% computed with 0 failures.

### Part F: Fingerprint Integrity & Model Input Row Alignment
- Reconstructed 2048-bit ECFP4 fingerprint matrix ($X_{r2}$) on all 731 interior compounds:
  - Shape: $(731, 2048)$
  - Sequence equality tests between `df_p` and `df_primary_merged`:
    - `chembl_id` sequence identical: **True**
    - `canonical_smiles_rdkit` sequence identical: **True**
    - `log10_CLint` sequence identical: **True**
- Row alignment test: For every index $i \in [0, 730]$, row $i$ of $X$, row $i$ of $y$, `chembl_id[i]`, and `scaffold_key[i]` belong to the exact same molecule.
- Total alignment errors: **0**.

### Part G: Scaffold Integrity
- Recalculated Murcko scaffold keys across all 1,102 compounds using `get_scaffold_key(canonical_smiles)`:
  - Exact matches against `splits/master_partition.csv`: **1,102 / 1,102 (100.0%)**
  - Scaffold mismatches: **0**
  - Cross-partition scaffold leakage: **0** (verified in preflight check: no scaffold crosses between CV and holdout).

### Part H: Scientific Cohorts Audit
Every scientific cohort was audited for ID-structure consistency and unresolved rows:

| Cohort | Definition / Filter | N | Mismatches | Unresolved | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **All Records** | Complete dataset | 1,102 | 0 | 0 | **VERIFIED** |
| **Left-Censored** | `relation == '<'` and $CL_{int} \le 3.0$ | 274 | 0 | 0 | **VERIFIED** |
| **Right-Censored** | `relation == '>'` and $CL_{int} \ge 150.0$ | 84 | 0 | 0 | **VERIFIED** |
| **Boundary-Ambiguous** | `relation IS NULL` and $CL_{int} \in \{3.0, 150.0\}$ | 13 | 0 | 0 | **VERIFIED** |
| **Strict Interior** | `relation IS NULL` and $3.0 < CL_{int} < 150.0$ | 731 | 0 | 0 | **VERIFIED** |
| **Primary CV** | Interior cohort, `partition == 'cv'` | 582 | 0 | 0 | **VERIFIED** |
| **Protected Holdout** | Interior cohort, `partition == 'holdout'` | 149 | 0 | 0 | **VERIFIED** |

### Part I: Forensic Case Studies (The Four Compounds)
A targeted forensic analysis was performed on the four compounds cited in the independent review:

1. **`CHEMBL1778622`**:
   - Raw Activity ID: `14765536` (Row 923 in `CHEMBL3301370_rows.csv`)
   - Canonical SMILES: `CCSc1ccc(-c2cc(C(F)(F)F)ccc2OCC(=O)O)cc1`
   - Formula: $\text{C}_{17}\text{H}_{15}\text{F}_3\text{O}_3\text{S}$
   - RDKit MolWt: **356.3650** | Stored Interim MW: **356.3650**
   - Murcko Scaffold: `c1ccc(-c2ccccc2)cc1`
   - Forensic Status: **Model input was 100% correct**. The reported discrepancy (MW 342.34, differing by $14\text{ Da}$ / 1 $\text{CH}_2$) was traced to an off-by-one indexing offset in `scratch/orig_extract_case_studies.py`.
2. **`CHEMBL1807823`**:
   - Raw Activity ID: `14759804` (Row 240 in `CHEMBL3301370_rows.csv`)
   - Canonical SMILES: `O=c1[nH]c2c(O)ccc([C@@H](O)CNCCSCCCNCCc3ccccc3)c2s1`
   - Formula: $\text{C}_{22}\text{H}_{29}\text{N}_3\text{O}_3\text{S}_2$
   - RDKit MolWt: **447.6260** | Stored Interim MW: **447.6260**
   - Murcko Scaffold: `O=c1[nH]c2cccc(CCNCCSCCCNCCc3ccccc3)c2s1`
   - Forensic Status: **Model input was 100% correct**. The reported MW 473.64 Da corresponds to Raloxifene (`CHEMBL81`), which was accidentally extracted by an unkeyed query in the exploratory script.
3. **`CHEMBL2335901`**:
   - Raw Activity ID: `14758997` (Row 231 in `CHEMBL3301370_rows.csv`)
   - Canonical SMILES: `C[C@@H](NC(=O)C1CCNCC1)c1ccc(Nc2ncc3cc(-c4ccncc4)ccc3n2)cc1`
   - Formula: $\text{C}_{27}\text{H}_{28}\text{N}_6\text{O}$
   - RDKit MolWt: **452.5620** | Stored Interim MW: **452.5620**
   - Murcko Scaffold: `O=C(NCc1ccc(Nc2ncc3cc(-c4ccncc4)ccc3n2)cc1)C1CCNCC1`
   - Forensic Status: **Model input was 100% correct**. Clean alignment across all layers.
4. **`CHEMBL20210`**:
   - Raw Activity ID: `14765461` (Row 888 in `CHEMBL3301370_rows.csv`)
   - Canonical SMILES: `CCOC(=O)/C=C/[C@H](C[C@@H]1CCNC1=O)NC(=O)[C@@H](CC(=O)[C@@H](NC(=O)c1cc(C)on1)C(C)C)Cc1ccc(F)cc1`
   - Formula: $\text{C}_{31}\text{H}_{39}\text{FN}_4\text{O}_7$
   - RDKit MolWt: **598.6720** | Stored Interim MW: **598.6720**
   - Murcko Scaffold: `O=C(CNC(=O)c1ccon1)CC(Cc1ccccc1)C(=O)NCCC1CCNC1=O`
   - Forensic Status: **Model input was 100% correct**. Clean alignment across all layers.

### Part J: Off-by-One Hypothesis Testing
To rule out any systematic row displacement, molecular weights recomputed from structure were shifted relative to stored molecular weights across offsets $k \in \{-3, -2, -1, 0, +1, +2, +3\}$:
- **Offset -3**: $2 / 1,099$ matches (0.2%)
- **Offset -2**: $1 / 1,100$ matches (0.1%)
- **Offset -1**: $6 / 1,101$ matches (0.5%)
- **Offset 0**: **1,102 / 1,102 matches (100.0%)**
- **Offset +1**: $6 / 1,101$ matches (0.5%)
- **Offset +2**: $1 / 1,100$ matches (0.1%)
- **Offset +3**: $2 / 1,099$ matches (0.2%)

**Conclusion**: The interim dataset has zero shift. The 100% match rate occurs uniquely at offset 0.

### Part K: Present-Day ChEMBL External API Check
- Queries attempted against `https://www.ebi.ac.uk/chembl/api/data/molecule/...`.
- Result: External EMBL-EBI ChEMBL API responded with HTTP 500 / gateway timeouts.
- Recorded as: **`CURRENT_CHEMBL_EXTERNAL_CHECK_UNAVAILABLE`**.
- As established in project governance, historical source data deposited in ChEMBL 20 remains the authoritative ground truth for this project.

### Part L: Security & Repository Scan
- Scanned all tracked and working tree files across the repository, plus 50 reachable git commits in branch history, checking for API keys, secret tokens, private keys, database passwords, and unencrypted `.env` credentials.
- Result: **0 active secret keys or credentials**. Clean repository state.
- Provenance note: One historical commit (`1371555`) contained an ephemeral, public Harvard Dataverse pre-signed S3 download URL from 2026-09-16 (expired after 1 hour) in download receipt manifests. The only `.env` files detected were non-secret `.env.example` templates. Zero private keys or production credentials exist.

---

## Discrepancy Classification Table

| Compound | Classification | Model Input Correct? | Details |
| :--- | :--- | :---: | :--- |
| **`CHEMBL1778622`** | `CASE_STUDY_EXTRACTION_ERROR` | **YES** | Historical source, interim table, and model matrix used correct structure $\text{C}_{17}\text{H}_{15}\text{F}_3\text{O}_3\text{S}$ (MW 356.37). Discrepancy was isolated to exploratory script `scratch/orig_extract_case_studies.py`. |
| **`CHEMBL1807823`** | `CASE_STUDY_EXTRACTION_ERROR` | **YES** | Historical source, interim table, and model matrix used correct structure $\text{C}_{22}\text{H}_{29}\text{N}_3\text{O}_3\text{S}_2$ (MW 447.63). Discrepancy was isolated to exploratory script `scratch/orig_extract_case_studies.py`. |
| **`CHEMBL2335901`** | `NONE_CLEAN_ALIGNMENT` | **YES** | Clean alignment across raw, interim, cohort, partition, descriptor, fingerprint, and model layers (MW 452.56). |
| **`CHEMBL20210`** | `NONE_CLEAN_ALIGNMENT` | **YES** | Clean alignment across raw, interim, cohort, partition, descriptor, fingerprint, and model layers (MW 598.67). |

### Forensic Compound Status Statements
- **`CHEMBL1778622`**: Classification = **`CASE_STUDY_EXTRACTION_ERROR`**. Model input was **100% CORRECT**.
- **`CHEMBL1807823`**: Classification = **`CASE_STUDY_EXTRACTION_ERROR`**. Model input was **100% CORRECT**.
- **`CHEMBL2335901`**: Classification = **`NONE_CLEAN_ALIGNMENT`**. Model input was **100% CORRECT**.
- **`CHEMBL20210`**: Classification = **`NONE_CLEAN_ALIGNMENT`**. Model input was **100% CORRECT**.

---

## Mandatory Question Responses

### MODEL INPUT ALIGNMENT
**Were X, y, compound ID and scaffold key correctly aligned for every modelled row?**

> **YES.**  
> Every modelled row across all 731 interior compounds (582 CV and 149 holdout) maintains strict 1-to-1 deterministic alignment between feature representations ($X_{r1}, X_{r2}$), target clearance values ($y = \log_{10} CL_{int}$), ChEMBL molecule identifiers, and Murcko scaffold partition keys. Zero alignment errors exist anywhere in the pipeline.

### IMPACT ON EXISTING RESULTS
**State whether there is any evidence of model-input corruption or whether the issue was isolated to reporting/extraction.**

> **no evidence of model-input corruption**  
> All primary and secondary model evaluations, cross-validation runs, holdout predictions, censored-endpoint models, confidence assessments, and residual analyses were trained and evaluated on 100% correct, verified molecular structures and property matrices. The discrepancies raised in the external review were entirely confined to post-hoc reporting scripts and never affected the modelling pipeline.

---

## Final Audit Verdict

```
WHOLE_COHORT_STRUCTURE_INTEGRITY_VERIFIED
```
