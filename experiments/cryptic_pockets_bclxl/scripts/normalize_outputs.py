import json
import csv
from pathlib import Path

def parse_pdb_residues(pdb_path):
    mapping = {}
    with open(pdb_path, 'r') as f:
        for line in f:
            if line.startswith("ATOM  ") or line.startswith("HETATM"):
                res_name = line[17:20].strip()
                chain = line[21]
                res_num = int(line[22:26].strip())
                # P2Rank format: A_93
                p2_key = f"{chain}_{res_num}"
                # Normalized format: ALA93:A
                norm_val = f"{res_name}{res_num}:{chain}"
                mapping[p2_key] = norm_val
    return mapping

def normalize_p2rank(csv_path, condition, pdb_path):
    mapping = parse_pdb_residues(pdb_path)
    candidates = []
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            # Clean keys
            row = {k.strip(): v.strip() for k, v in row.items()}
            rank = int(row['rank'])
            
            p2_res = row.get('residue_ids', '').split()
            norm_res = []
            for r in p2_res:
                if r in mapping:
                    norm_res.append(mapping[r])
                else:
                    raise ValueError(f"Unknown residue ID {r}")
            
            centroid = [float(row['center_x']), float(row['center_y']), float(row['center_z'])]
            
            cand = {
                "method": "p2rank",
                "condition": condition,
                "candidate_id": f"p2rank_{condition}_{rank}",
                "rank": rank,
                "residues": norm_res,
                "centroid": centroid,
                "method_specific_scores": {
                    "score": float(row['score']),
                    "probability": float(row['probability']),
                    "sas_points": int(row['sas_points']),
                    "surf_atoms": int(row['surf_atoms'])
                }
            }
            candidates.append(cand)
    return candidates

def normalize_lacuna(json_path, condition):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    candidates = []
    for pocket in data.get('pockets', []):
        rank = pocket['rank']
        
        cand = {
            "method": "lacuna",
            "condition": condition,
            "candidate_id": f"lacuna_{condition}_{rank}",
            "rank": rank,
            "residues": pocket['lining_residues'],
            "centroid": pocket['centroid'],
            "method_specific_scores": {
                "druggability": pocket.get('druggability'),
                "volume_A3": pocket.get('volume_A3'),
                "persistence": pocket.get('persistence'),
                "crypticity": pocket.get('crypticity')
            }
        }
        candidates.append(cand)
    return candidates

def main():
    import glob
    
    out_dir = Path("results/analysis_b/normalized")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # We have run IDs. Let's find the files.
    apo_pdb = Path("data/processed/apo_matched_core.pdb")
    holo_pdb = Path("data/processed/holo_matched_core_no_ligand.pdb")
    
    all_candidates = []
    
    # p2rank apo
    p2_apo_dir = list(Path("results/analysis_b/raw/p2rank_apo").glob("run_*"))[0]
    all_candidates.extend(normalize_p2rank(p2_apo_dir / "apo_matched_core.pdb_predictions.csv", "apo", apo_pdb))
    
    # p2rank holo
    p2_holo_dir = list(Path("results/analysis_b/raw/p2rank_holo").glob("run_*"))[0]
    all_candidates.extend(normalize_p2rank(p2_holo_dir / "holo_matched_core_no_ligand.pdb_predictions.csv", "holo_control", holo_pdb))
    
    # lacuna apo
    lac_apo_dir = list(Path("results/analysis_b/raw/lacuna_apo").glob("run_*"))[0]
    all_candidates.extend(normalize_lacuna(lac_apo_dir / "pocket_report.json", "apo"))
    
    # lacuna holo
    lac_holo_dir = list(Path("results/analysis_b/raw/lacuna_holo").glob("run_*"))[0]
    all_candidates.extend(normalize_lacuna(lac_holo_dir / "pocket_report.json", "holo_control"))
    
    with open(out_dir / "all_candidates.json", 'w') as f:
        json.dump(all_candidates, f, indent=2)

if __name__ == '__main__':
    main()
