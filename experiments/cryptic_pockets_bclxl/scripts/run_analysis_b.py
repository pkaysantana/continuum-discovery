import os
import sys
import json
import uuid
import shutil
from pathlib import Path
sys.path.append('src')

from wrappers_analysis_b import run_lacuna_analysis_b, run_p2rank_analysis_b
from provenance import now, sha256

def execute_run(config_name, method, input_path):
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    
    # Check input
    if not input_path.exists():
        print(f"Missing input {input_path}")
        return
        
    out_dir = Path(f"results/analysis_b/raw/{config_name}/{run_id}")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if method == "lacuna":
        result = run_lacuna_analysis_b(input_path, out_dir)
    elif method == "p2rank":
        p2rank_sh = Path("p2rank_2.5.1/prank.sh") if os.name != 'nt' else Path("p2rank_2.5.1/prank.bat")
        result = run_p2rank_analysis_b(p2rank_sh, input_path, out_dir)
    else:
        raise ValueError(f"Unknown method {method}")
        
    result['run_id'] = run_id
    result['config_name'] = config_name
    
    manifest_path = Path(f"results/analysis_b/{config_name}_{run_id}_manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str)
        
    if result['status'] == 'SUCCESS':
        print(f"[{config_name}] SUCCESS. Run ID: {run_id}")
    else:
        print(f"[{config_name}] FAILED. Run ID: {run_id}")
        print(f"Error: {result.get('error')}")

def main():
    Path("results/analysis_b/raw").mkdir(parents=True, exist_ok=True)
    
    # 1. P2Rank apo
    execute_run("p2rank_apo", "p2rank", Path("data/processed/apo_matched_core.pdb"))
    
    # 2. Lacuna apo
    execute_run("lacuna_apo", "lacuna", Path("data/processed/apo_matched_core.pdb"))
    
    # 3. P2Rank holo
    execute_run("p2rank_holo", "p2rank", Path("data/processed/holo_matched_core_no_ligand.pdb"))
    
    # 4. Lacuna holo
    execute_run("lacuna_holo", "lacuna", Path("data/processed/holo_matched_core_no_ligand.pdb"))

if __name__ == '__main__':
    main()
