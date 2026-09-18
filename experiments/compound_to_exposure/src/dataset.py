import numpy as np
import pandas as pd
from pathlib import Path

# Assuming ROOT is the project root containing 'data/'
ROOT = Path(__file__).resolve().parent.parent

def load_chembl3301370_raw():
    df = pd.read_csv(ROOT / "data" / "interim" / "CHEMBL3301370_rows.csv", dtype=str)
    
    # Clean the dataframe
    df['standard_value'] = pd.to_numeric(df['standard_value'], errors='coerce')
    df['molecule_chembl_id'] = df['molecule_chembl_id'].fillna('')
    df['standard_relation'] = df['standard_relation'].fillna('')
    
    # We rename molecule_chembl_id to chembl_id for consistency
    if 'molecule_chembl_id' in df.columns:
        df = df.rename(columns={'molecule_chembl_id': 'chembl_id'})
        
    return df

def get_cohorts():
    df = load_chembl3301370_raw()
    
    # Based on the HLM-HH cross-tab descriptions and SAP:
    # interior_731: standard_relation IS NULL AND 3 < CLint < 150
    # below_274: left-censored at 3 -> standard_relation == '<' and standard_value <= 3 (actually the data has < 3.0)
    # above_84: right-censored at 150 -> standard_relation == '>' and standard_value >= 150
    # ambiguous_13: standard_relation IS NULL AND standard_value exactly 3
    
    df['is_null_rel'] = df['standard_relation'].str.strip() == ''
    df['is_left_rel'] = df['standard_relation'].str.strip() == '<'
    df['is_right_rel'] = df['standard_relation'].str.strip() == '>'
    
    df['val_close_to_3'] = np.isclose(df['standard_value'], 3.0, atol=1e-5)
    df['val_close_to_150'] = np.isclose(df['standard_value'], 150.0, atol=1e-5)
    
    interior_mask = df['is_null_rel'] & (df['standard_value'] > 3.0) & (df['standard_value'] < 150.0) & ~df['val_close_to_3'] & ~df['val_close_to_150']
    ambiguous_mask = df['is_null_rel'] & (df['val_close_to_3'] | df['val_close_to_150'])
    left_mask = df['is_left_rel'] & df['val_close_to_3']
    right_mask = df['is_right_rel'] & df['val_close_to_150']
    
    # Assert counts to ensure we hit exactly the 731, 274, 84, 13
    assert interior_mask.sum() == 731, f"Expected 731, got {interior_mask.sum()}"
    assert left_mask.sum() == 274, f"Expected 274, got {left_mask.sum()}"
    assert right_mask.sum() == 84, f"Expected 84, got {right_mask.sum()}"
    assert ambiguous_mask.sum() == 13, f"Expected 13, got {ambiguous_mask.sum()}"
    
    total_assigned = interior_mask.sum() + left_mask.sum() + right_mask.sum() + ambiguous_mask.sum()
    assert total_assigned == 1102, f"Expected 1102, got {total_assigned}"
    assert len(df) == 1102, f"Total dataset rows should be 1102, got {len(df)}"
    
    interior_731 = df[interior_mask].copy()
    below_274 = df[left_mask].copy()
    above_84 = df[right_mask].copy()
    ambiguous_13 = df[ambiguous_mask].copy()
    
    # Target for primary regression is log10(CL_int) only for interior_731
    interior_731['log10_CLint'] = np.log10(interior_731['standard_value'])
    
    return {
        'interior_731': interior_731,
        'below_274': below_274,
        'above_84': above_84,
        'ambiguous_13': ambiguous_13,
        'full_df': df
    }
