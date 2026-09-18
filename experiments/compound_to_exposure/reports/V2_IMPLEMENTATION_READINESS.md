# V2 Implementation Readiness Report

This report maps the frozen v2 SAP clauses to their implementation files, functions, and corresponding test coverage.

## 1. Immutable Dataset Construction
- **SAP Clause:** "Primary science dataset: CHEMBL3301370... exact cohorts: interior_731, below_274, above_84, ambiguous_13."
- **Implementation:** `src/dataset.py:get_cohorts`
- **Tests:** `tests/test_v2_implementation.py:TestV2Implementation.test_cohorts_counts`
- **Status:** **IMPLEMENTED** (Verified lengths map exactly)

## 2. Target Estimand
- **SAP Clause:** "Target for the primary regression: log10(CL_int) only for interior_731. Never substitute 3 or 150 as exact targets for censored records."
- **Implementation:** `src/dataset.py:get_cohorts` (creates `log10_CLint` only for `interior_731`)
- **Tests:** `tests/test_leakage_guards.py:TestLeakageGuards.test_censored_labels_exclusion`
- **Status:** **IMPLEMENTED**

## 3. Molecular Representations
- **SAP Clause:** "R1 exactly: MolWt, MolLogP, MolMR, TPSA, NumHDonors, NumHAcceptors, NumRotatableBonds, RingCount, NumAromaticRings, NumAliphaticRings, FractionCSP3, HeavyAtomCount. R2 exactly: Morgan radius 2, 2048 bits, binary, useChirality=False."
- **Implementation:** `src/representations.py:get_r1_descriptors` and `get_r2_morgan`
- **Tests:** `tests/test_v2_implementation.py:TestV2Implementation.test_r1_ordering`
- **Status:** **IMPLEMENTED**

## 4. Structural Partition Algorithm
- **SAP Clause:** "Bemis–Murcko scaffold... __ACYCLIC__... SHA-256 scaffold ordering... 20% primary-cohort holdout... five inner grouped folds."
- **Implementation:** `src/partition.py:compute_master_partition`
- **Tests:** `tests/test_leakage_guards.py:TestLeakageGuards.test_scaffold_overlap`
- **Status:** **IMPLEMENTED**

## 5. Preprocessing/Model Pipelines
- **SAP Clause:** "Implement exactly P0a, P0b, P1-P4. Tie-breaking logic."
- **Implementation:** `src/pipelines.py:get_pipeline_grids` and `tie_break_candidates`
- **Tests:** `tests/test_v2_implementation.py:TestV2Implementation.test_tie_breaking`
- **Status:** **IMPLEMENTED**

## 6. Metrics & Tails
- **SAP Clause:** "log10 MAE, RMSE, Spearman, R², proportion within ±log10(2), paired bootstrap, C_L, C_U, boundary violation."
- **Implementation:** `src/metrics.py` (various functions)
- **Tests:** `tests/test_v2_implementation.py:TestV2Implementation.test_metrics` and `test_tail_concordance`
- **Status:** **IMPLEMENTED**

## 7. Sensitivities
- **SAP Clause:** "Sensitivity A: 13 NULL-at-3 included as exact 3. Sensitivity B: 13 NULL-at-3 treated with censored group."
- **Implementation:** `src/sensitivities.py:run_sensitivity_analyses`
- **Tests:** `tests/test_leakage_guards.py:TestLeakageGuards.test_sensitivity_partition_reuse`
- **Status:** **IMPLEMENTED**

## 8. HLM-HH Qualifier
- **SAP Clause:** "total matched = 187, primary interior/interior N = 94. Implement qualifier filtering and contingency reporting."
- **Implementation:** `src/hlm_hh.py:qualify_hlm_hh_pairs`
- **Status:** **IMPLEMENTED**

## 9. Biogen
- **SAP Clause:** "Implement data preparation only for: B1 as-shipped N=3,087. B2 floor-excluded N=2,129."
- **Implementation:** `src/biogen.py:load_biogen_data`
- **Tests:** `tests/test_v2_implementation.py:TestV2Implementation.test_biogen_counts`
- **Status:** **IMPLEMENTED**

## 10. Leakage Guards
- **SAP Clause:** "Add tests that fail if holdout compounds enter fitting... scaffold groups cross... etc."
- **Implementation:** `tests/test_leakage_guards.py`
- **Status:** **IMPLEMENTED**

## Dry-Run Readiness
- **Implementation:** `src/dry_run.py` & `src/run.py`
- **Status:** **V2_IMPLEMENTATION_READY_FOR_REVIEW**
