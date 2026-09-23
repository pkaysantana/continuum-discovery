import csv
with open('results/analysis_b/candidate_metrics.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        if r['rank'] == '1':
            print(f"{r['method']} {r['condition']} - Recall: {r['primary_5_0_recall']} Precision: {r['primary_5_0_precision']}")
