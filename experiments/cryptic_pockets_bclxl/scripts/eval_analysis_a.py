import json
import sys
from pathlib import Path
sys.path.append("src")

from comparison_metrics import candidate_metrics
from reference_site import evaluate, load_cif
from run import config, verify_inputs

def get_ref(c, structures):
    return evaluate(load_cif(structures["2YXJ"]), load_cif(structures["1LXL"]), c)

def load_pockets(path):
    with open(path) as f:
        return json.load(f)["pockets"]

def eval_pockets(pockets, ref_site):
    ref_residues = set()
    for r in ref_site["apo_mapped_residues"]:
        res_name = r["apo"]["resname"]
        res_id = r["apo"]["auth_seq_id"]
        chain = r["apo"]["auth_chain"]
        ref_residues.add(f"{res_name}{res_id}:{chain}")
        
    results = []
    for p in pockets:
        pred_residues = set(p["lining_residues"])
        metrics = candidate_metrics(
            candidate_center=p["centroid"],
            reference_center=ref_site["apo_reference_centroid"],
            predicted=pred_residues,
            reference=ref_residues
        )
        results.append({
            "rank": p["rank"],
            "centroid_distance_angstrom": metrics["centroid_distance_angstrom"],
            "recovered": metrics["recovered"],
            "intersection_count": metrics["intersection_count"],
            "reference_site_recall": metrics["reference_site_recall"],
            "predicted_site_precision": metrics["predicted_site_precision"],
            "jaccard": metrics["jaccard"]
        })
    return results

def main():
    structures = verify_inputs()
    
    c = config()
    c["contact_cutoff_angstrom"] = 5.0
    ref_5 = get_ref(c, structures)
    
    c["contact_cutoff_angstrom"] = 4.5
    ref_4_5 = get_ref(c, structures)
    
    run_dir = Path("results/analysis_a/raw/run_1d6f4a82")
    pockets = load_pockets(run_dir / "pocket_report.json")
    
    eval_5 = eval_pockets(pockets, ref_5)
    eval_4_5 = eval_pockets(pockets, ref_4_5)
    
    out = {
        "primary_5_0A": eval_5,
        "sensitivity_4_5A": eval_4_5
    }
    
    with open("results/analysis_a/evaluation.json", "w") as f:
        json.dump(out, f, indent=2)
        
    print("Evaluation complete. Results saved to evaluation.json")

if __name__ == "__main__":
    main()

