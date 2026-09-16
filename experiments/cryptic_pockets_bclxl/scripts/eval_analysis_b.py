import json
import csv
from pathlib import Path
import math

def distance(c1, c2):
    return math.sqrt(sum((a - b)**2 for a, b in zip(c1, c2)))

def candidate_metrics(candidate_center, reference_center, predicted_ids, reference_ids):
    dist = distance(candidate_center, reference_center)
    intersection = predicted_ids.intersection(reference_ids)
    
    metrics = {
        "centroid_distance_angstrom": dist,
        "recovered": dist <= 4.0,
        "intersection_count": len(intersection),
        "reference_site_recall": len(intersection) / len(reference_ids) if reference_ids else 0.0,
        "predicted_site_precision": len(intersection) / len(predicted_ids) if predicted_ids else 0.0,
        "predicted_size": len(predicted_ids),
        "reference_size": len(reference_ids)
    }
    
    # Jaccard
    union_size = len(predicted_ids.union(reference_ids))
    metrics["jaccard"] = len(intersection) / union_size if union_size > 0 else 0.0
    
    return metrics

def parse_res_id(norm_str):
    # e.g., 'ALA93:A' -> 93
    import re
    m = re.search(r'\d+', norm_str)
    return int(m.group(0))

def main():
    with open('data/processed/comparison_reference.json') as f:
        ref_data = json.load(f)
        
    ref_5_ids = set(ref_data['cutoffs']['5.0']['output_residue_ids'])
    ref_45_ids = set(ref_data['cutoffs']['4.5']['output_residue_ids'])
    
    with open('results/analysis_b/normalized/all_candidates.json') as f:
        candidates = json.load(f)
        
    summary_data = []
    
    for cand in candidates:
        cond = cand['condition'] # "apo" or "holo_control"
        
        if cond == "apo":
            ref_center = ref_data['cutoffs']['5.0']['apo_reference_centroid_CA']
            ref_center_45 = ref_data['cutoffs']['4.5']['apo_reference_centroid_CA']
        else:
            ref_center = ref_data['cutoffs']['5.0']['holo_reference_centroid_CA']
            ref_center_45 = ref_data['cutoffs']['4.5']['holo_reference_centroid_CA']
            
        pred_ids = set(parse_res_id(r) for r in cand['residues'])
        
        # Primary 5.0
        metrics_5 = candidate_metrics(cand['centroid'], ref_center, pred_ids, ref_5_ids)
        # Sensitivity 4.5
        metrics_45 = candidate_metrics(cand['centroid'], ref_center_45, pred_ids, ref_45_ids)
        
        row = {
            "method": cand['method'],
            "condition": cand['condition'],
            "candidate_id": cand['candidate_id'],
            "rank": cand['rank'],
            "primary_5_0_centroid_distance": metrics_5['centroid_distance_angstrom'],
            "primary_5_0_recovered": metrics_5['recovered'],
            "primary_5_0_jaccard": metrics_5['jaccard'],
            "primary_5_0_recall": metrics_5['reference_site_recall'],
            "primary_5_0_precision": metrics_5['predicted_site_precision'],
            "primary_5_0_intersection": metrics_5['intersection_count'],
            "primary_5_0_upstream_hit": metrics_5['jaccard'] >= 0.25 or metrics_5['centroid_distance_angstrom'] <= 4.0,
            
            "sensitivity_4_5_centroid_distance": metrics_45['centroid_distance_angstrom'],
            "sensitivity_4_5_recovered": metrics_45['recovered'],
            "sensitivity_4_5_jaccard": metrics_45['jaccard'],
            "sensitivity_4_5_recall": metrics_45['reference_site_recall'],
            "sensitivity_4_5_precision": metrics_45['predicted_site_precision'],
            "sensitivity_4_5_intersection": metrics_45['intersection_count'],
            "sensitivity_4_5_upstream_hit": metrics_45['jaccard'] >= 0.25 or metrics_45['centroid_distance_angstrom'] <= 4.0,
        }
        
        # Add method specific scores
        for k, v in cand['method_specific_scores'].items():
            row[f"method_score_{k}"] = v
            
        summary_data.append(row)
        
    # Write full candidate metrics CSV
    if summary_data:
        keys = []
        for row in summary_data:
            for k in row.keys():
                if k not in keys:
                    keys.append(k)
        with open('results/analysis_b/candidate_metrics.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(summary_data)
            
    # Now aggregate summary
    methods = ["p2rank", "lacuna"]
    conditions = ["apo", "holo_control"]
    
    aggregated = []
    
    for cond in conditions:
        for method in methods:
            cands = [c for c in summary_data if c['method'] == method and c['condition'] == cond]
            # Filter to top K budget: P2Rank = all, Lacuna = 10
            budget = 10 if method == "lacuna" else 1000
            cands = [c for c in cands if c['rank'] <= budget]
            
            # primary hit
            primary_hits = [c for c in cands if c['primary_5_0_recovered']]
            first_primary_hit = primary_hits[0] if primary_hits else None
            
            secondary_hits = [c for c in cands if c['primary_5_0_upstream_hit']]
            first_secondary_hit = secondary_hits[0] if secondary_hits else None
            
            best_centroid = min([c['primary_5_0_centroid_distance'] for c in cands]) if cands else None
            best_jaccard = max([c['primary_5_0_jaccard'] for c in cands]) if cands else None
            
            config_name = f"{method}_{'holo' if cond == 'holo_control' else cond}"
            run_dirs = list(Path(f"results/analysis_b/raw/{config_name}").glob("run_*"))
            runtime = None
            if run_dirs:
                manifest_path = Path("results/analysis_b") / f"{config_name}_{run_dirs[0].name}_manifest.json"
                if manifest_path.exists():
                    with open(manifest_path) as mf:
                        runtime = json.load(mf).get('runtime')
            
            row = {
                "condition": cond,
                "method": method,
                "candidate_count": len(cands),
                "first_primary_hit_rank": first_primary_hit['rank'] if first_primary_hit else None,
                "best_centroid_distance": best_centroid,
                "first_secondary_hit_rank": first_secondary_hit['rank'] if first_secondary_hit else None,
                "best_jaccard": best_jaccard,
                "reference_recall_at_first_primary_hit": first_primary_hit['primary_5_0_recall'] if first_primary_hit else None,
                "precision_at_first_primary_hit": first_primary_hit['primary_5_0_precision'] if first_primary_hit else None,
                "runtime": runtime,
                "status": "SUCCESS" if cands else "FAILED/NO_CANDIDATES"
            }
            aggregated.append(row)
            
    with open('results/analysis_b/summary.json', 'w', encoding='utf-8') as f:
        json.dump(aggregated, f, indent=2)

if __name__ == '__main__':
    main()
