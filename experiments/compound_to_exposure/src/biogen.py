import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load_biogen_data():
    """
    Biogen replication data loader.
    """
    df = pd.read_csv(ROOT / "data" / "interim" / "Biogen_rows.csv", dtype=str)
    
    # Populated values only
    df = df.dropna(subset=['LOG HLM_CLint (mL/min/kg)'])
    df['LOG HLM_CLint (mL/min/kg)'] = pd.to_numeric(df['LOG HLM_CLint (mL/min/kg)'], errors='coerce')
    df = df.dropna(subset=['LOG HLM_CLint (mL/min/kg)'])
    
    # B1 as-shipped: N=3087
    b1_as_shipped = df.copy()
    
    # B2 floor-excluded sensitivity: strictly greater than 0.675686709
    b2_floor_excluded = df[df['LOG HLM_CLint (mL/min/kg)'] > 0.675686709].copy()
    
    assert len(b1_as_shipped) == 3087, f"Expected B1 N=3087, got {len(b1_as_shipped)}"
    assert len(b2_floor_excluded) == 2129, f"Expected B2 N=2129, got {len(b2_floor_excluded)}"
    
    return b1_as_shipped, b2_floor_excluded
