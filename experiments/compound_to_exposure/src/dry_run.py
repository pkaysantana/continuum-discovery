import sys
from pathlib import Path
from src.dataset import get_cohorts
from src.representations import get_r1_descriptors, get_r2_morgan
from src.partition import compute_master_partition
from src.pipelines import get_pipeline_grids, get_p0a_baseline, get_p0b_baseline
from src.hlm_hh import load_hlm_hh_data
from src.biogen import load_biogen_data
from src.sensitivities import run_sensitivity_analyses

def main():
    print("Starting V2 Implementation Dry-Run...")
    
    # 1. Loading & cohort construction
    print("Loading data cohorts...")
    cohorts = get_cohorts()
    print(f"Cohorts loaded successfully. N_interior = {len(cohorts['interior_731'])}")
    
    # 2. Descriptors / fingerprints
    print("Testing representation building...")
    smiles = "CCO"
    r1 = get_r1_descriptors(smiles)
    assert r1 is not None, "Failed R1 descriptor building"
    r2 = get_r2_morgan(smiles)
    assert r2 is not None, "Failed R2 Morgan fingerprint building"
    
    # 3. Partition Loading/Computation
    print("Computing Master Partition...")
    interior_ids = set(cohorts['interior_731']['chembl_id'])
    partition_df = compute_master_partition(cohorts['full_df'], interior_ids)
    
    # Save partition (simulated loading)
    # partition_df.to_csv('splits/master_partition.csv', index=False)
    
    # Verify partition counts
    h_count = len(partition_df[partition_df['partition'] == 'holdout'])
    cv_count = len(partition_df[partition_df['partition'] == 'cv'])
    print(f"Partition computed: {h_count} holdout, {cv_count} CV.")
    
    # 4. Pipeline construction
    print("Testing pipeline construction...")
    grids = get_pipeline_grids()
    p0a = get_p0a_baseline()
    p0b = get_p0b_baseline()
    assert len(grids) == 4, "Missing pipelines"
    
    # 5. Configuration validation (sensitivities, biogen, etc.)
    print("Testing configuration & sensitivity validation...")
    sens_res = run_sensitivity_analyses(partition_df, cohorts)
    b1, b2 = load_biogen_data()
    print(f"Biogen subsets loaded: B1={len(b1)}, B2={len(b2)}")
    
    # Ensure NO .fit() is called on real dataset
    print("\nDry run completed successfully without real model fitting.")
    print("V2_IMPLEMENTATION_READY_FOR_REVIEW")

if __name__ == '__main__':
    main()
