# Biogen Replication Protocol Amendment

**Status:** Prospectively frozen  
**Timing:** Written BEFORE any Biogen model fitting and BEFORE any Biogen performance inspection.

## 1. Rationale for Amendment
The original frozen `MODELLING_PREREGISTRATION.md` (Section 14) mandated using the same methodology for the Biogen replication track as the primary AZ track. However, it did not unambiguously define the Biogen outer-fold generation algorithm. 

The primary AZ track strictly uses `StratifiedGroupKFold` stratified across three discrete censoring classes (BELOW, IN-RANGE, ABOVE). Because the independent Biogen dataset contains only a continuous target (`LOG HLM_CLint`) and no pre-defined censoring classes, the AZ class-stratified outer CV criterion cannot be transferred directly or logically evaluated.

## 2. Prospective Biogen Outer-Fold Rule
To maintain the chemically held-out, scaffold-aware validation intent of the primary project while respecting the continuous nature of the Biogen target, Biogen prospectively uses:

**`GroupKFold(n_splits=5, shuffle=True, random_state=42)`**

- **Grouping Variable:** Exact frozen RDKit Bemis-Murcko canonical isomeric scaffold SMILES (the identical implementation already used by the AZ project). Acyclic/empty-Murcko molecules receive deterministic singleton groups keyed by their canonical SMILES.
- **Stratification:** NO target-derived stratification is introduced. No artificial target binning, clearance quantiles, or invented censoring classes are used.

## 3. Minimum-Pile-Up Sensitivity Fold Inheritance
The previously preregistered sensitivity cohort (removing the 958 records exactly equal to the minimum pile-up of 0.675686709) strictly **inherits** the primary outer-fold IDs. 
- Sensitivity folds are **NOT** regenerated.
- Sensitivity folds are **NOT** rebalanced after the exclusion of the 958 records.

## 4. Preservation of Inner Rules
All other rules from the original preregistration remain fully unchanged:
- **Inner CV:** 3-fold scaffold-aware `GroupKFold` within each outer-training set.
- **Model Matrix & Grids:** Unchanged (mean, median, Ridge, Random Forest).
- **Applicability Domain:** As per Sections 9 and 14, Biogen uses the exact same applicability domain diagnostics (maximum Morgan Tanimoto similarity to the compound's own outer-training fold, error vs similarity Spearman, and LOWESS curve `frac=0.3`, `it=3`, `delta=0.0`) on all four learned regression cells.
