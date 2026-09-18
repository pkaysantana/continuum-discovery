# V2 Failed Execution 002 Forensics

## 1. Preserve Failed Execution 002

**Run Directory/Log Identified:**
- The invocation is associated with run ID `2026-09-18T180525342345_0000-b3b5d39d`.
- Run JSON log path: `manifests/runs/2026-09-18T180525342345_0000-b3b5d39d.json`
- Log path: `reports/execute-2026-09-18T180525342345_0000-b3b5d39d.log`

**Verification Checklist:**
- **Number of real-mode invocations under `dmpk-v2-execution-ready-v2`**: 1 (the single `action: "execute"` log matching this period).
- **Furthest line/stage reached**: Execution failed at `src/execute_v2.py` line 204 (`KeyError: 'smiles'`) before any stage ledger was even begun.
- **No real `.fit()`**: Confirmed. Data preparation failed prior to any model fitting.
- **No `.predict()`**: Confirmed.
- **No selection manifest**: Confirmed. The script crashed before `manifests/runs/.../selection_manifest.json` could be generated.
- **No primary holdout target access**: Confirmed. Execution halted well before holdout masks were applied.
- **No predictive metric**: Confirmed.
- **No authoritative-state transition**: Confirmed. The `state/v2_execution_state.json` file remained absent as `ExecutionLedger.begin_stage` was never reached.

**Classification:**
`PRE_ACCESS_EXECUTION_FAILURE_CONFIRMED`

## 2. Establish the actual real-data schema

Using `from src.dataset import get_cohorts`, we examined the dataset schemas exactly as returned.

**Exact Columns for all major subsets (`full_df`, `interior_731`, `below_274`, `above_84`, `ambiguous_13`):**
`'action_type', 'activity_comment', 'activity_id', 'activity_properties', 'assay_cell_type', 'assay_chembl_id', 'assay_description', 'assay_organism', 'assay_strain', 'assay_subcellular_fraction', 'assay_tax_id', 'assay_tissue', 'assay_type', 'assay_variant_accession', 'assay_variant_mutation', 'bao_endpoint', 'bao_format', 'bao_label', 'canonical_smiles', 'canonical_smiles_rdkit', 'cell_chembl_id', 'clogp', 'data_validity_comment', 'data_validity_description', 'document_chembl_id', 'document_journal', 'document_year', 'dummy_atom_count', 'fraction_csp3', 'fragment_count', 'hba', 'hbd', 'ligand_efficiency', 'measurement_audit', 'modality', 'molecular_weight', 'chembl_id', 'molecule_pref_name', 'parent_molecule_chembl_id', 'pchembl_value', 'potential_duplicate', 'qudt_units', 'raw_filename', 'raw_identifier', 'raw_smiles', 'raw_target', 'record_id', 'relation', 'rotatable_bonds', 'source', 'source_row_1based', 'src_id', 'standard_flag', 'standard_relation', 'standard_text_value', 'standard_type', 'standard_units', 'standard_upper_value', 'standard_value', 'structure_error', 'structure_status', 'target_chembl_id', 'target_organism', 'target_pref_name', 'target_tax_id', 'text_value', 'tissue_chembl_id', 'toid', 'tpsa', 'type', 'undefined_stereo_elements', 'units', 'uo_units', 'upper_value', 'value', 'is_null_rel', 'is_left_rel', 'is_right_rel', 'val_close_to_3', 'val_close_to_150'`
*(Note: `interior_731` also has `log10_CLint`)*

**Canonical molecular-structure field:**
- Field name: `canonical_smiles_rdkit` (and `canonical_smiles` as identical backup).
- Non-null count: `731` (for `interior_731`).
- Uniqueness: `731` unique entries.
- The `smiles` column does not exist in the frozen dataframe.

## 3. Trace every structure-column reference

Tracing the execution code in `src/execute_v2.py`:

- **R1 descriptors:** Expects `['smiles']` (`np.array([get_r1_descriptors(s) for s in df_p['smiles']])`).
- **R2 Morgan fingerprints:** Expects `['smiles']` (`np.array([get_r2_morgan(s) for s in df_p['smiles']])`).
- **Scaffold/Tanimoto operations:** Does not reference structure columns directly here; relies on precomputed indices in `SCAFFOLD_PREFREEZE_DRY_RUN_ASSIGNMENTS.csv`.
- **Tail Evaluation:** Expects `['smiles']` (`df_tail[tail_fold_mask]['smiles']` & `df_tail[tail_h_mask]['smiles']`).
- **Sensitivity A/B:** Expects `['smiles']` implicitly via `X_r1_ambig` / `X_r2_ambig` pre-constructed using `df_ambig['smiles']`.
- **HLM-HH matching:** Does not expect a structure column; matches directly on `activity_id` using secondary static datasets.
- **Biogen modelling:** Does not expect a structure column; implementation currently hardcodes mock representations (`X_mock = np.zeros(...)`) rather than computing from structures.

**Problem Determination:**
The failure stems from **inconsistent aliases throughout the runner**. The execution runner consistently expects the alias `'smiles'`, whereas the upstream frozen dataset (schema-normalisation) canonically emits `'canonical_smiles_rdkit'` and `'canonical_smiles'`, omitting `'smiles'` entirely.

## 4. Explain why preflight missed it

Tracing `run.py preflight` logic to `execute_v2(..., preflight=True)`:
```python
    if preflight:
        return "V2_REAL_DATA_PREFLIGHT_PASS"

    if synthetic_data:
        pass
    else:
        X_r1 = np.array([get_r1_descriptors(s) for s in df_p['smiles']])
```
- **Preflight returns at line 198**.
- **Real R1/R2 descriptor construction** occurs on lines 204-207, which is **after** the preflight return statement.
- The required production-schema structure check (`df_p['smiles']`) is only evaluated during the real execution phase that constructs these representations.

This perfectly explains why `V2_REAL_DATA_PREFLIGHT_PASS` could comfortably coexist with a subsequent `KeyError: 'smiles'` during the actual run. Preflight tested only partition/hash constraints, bypassing descriptor generation.

## 5. No-real-execution verification

I have strictly verified that this execution incident resulted in an immediate crash during feature preprocessing (Line 204). Absolutely no model training occurred, no holdout records were accessed, and no true predictive results or metrics were derived.

FAILED_EXECUTION_002_SCHEMA_ROOT_CAUSE_CONFIRMED
