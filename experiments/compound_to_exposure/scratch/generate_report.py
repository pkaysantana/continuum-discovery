import json

with open('results/primary_v1/METRICS.json', 'r') as f:
    metrics = json.load(f)

with open('results/primary_v1/AD_METRICS.json', 'r') as f:
    ad = json.load(f)
    
with open('results/primary_v1/HYPERPARAMETERS.json', 'r') as f:
    hp = json.load(f)

md = "# Primary Modelling Results\n\n"
md += "**Direct Observation & Calculated Metrics Only. See limitations for caveats.**\n\n"

# Hyperparameters
md += "## Selected Hyperparameters by Fold\n"
for h in hp:
    md += f"- **{h['model']} ({h['representation']}) Fold {h['fold']}**: "
    for k, v in h.items():
        if k not in ['model', 'representation', 'fold']:
            md += f"{k}={v} "
    md += "\n"

# Regression
md += "\n## Regression Metrics (Primary N=744)\n"
md += "| Model | Rep | MAE | RMSE | Spearman ρ | R² | Frac <= log10(2) |\n"
md += "|---|---|---|---|---|---|---|\n"
for name, m in metrics['primary']['regression'].items():
    s = name.split('_')
    model, rep = s[0], s[1]
    md += f"| {model} | {rep} | {m['MAE']:.3f} | {m['RMSE']:.3f} | {m['Spearman_rho']:.3f} | {m['R2']:.3f} | {m['Fraction_within_2fold']:.3f} |\n"

# Classifier
md += "\n## Classifier Metrics (N=1102)\n"
md += "| Model | Rep | Macro-F1 | Balanced Acc | MCC | Precision (B/I/A) | Recall (B/I/A) |\n"
md += "|---|---|---|---|---|---|---|\n"
for name, m in metrics['primary']['classifier'].items():
    s = name.split('_')
    model, rep = s[0], s[1]
    md += f"| {model} | {rep} | {m['Macro_F1']:.3f} | {m['Balanced_Accuracy']:.3f} | {m['MCC']:.3f} | {m['Precision_BELOW']:.3f}/{m['Precision_IN-RANGE']:.3f}/{m['Precision_ABOVE']:.3f} | {m['Recall_BELOW']:.3f}/{m['Recall_IN-RANGE']:.3f}/{m['Recall_ABOVE']:.3f} |\n"

# Tail
md += "\n## Tail Ordering Scores\n"
md += "| Model | Rep | Tail | N Eligible | Score |\n"
md += "|---|---|---|---|---|\n"
for name, m in metrics['primary']['tail'].items():
    s = name.split('_')
    model, rep, tail = s[0], s[1], s[2]
    md += f"| {model} | {rep} | {tail} | {m['eligible_pairs']} | {m['final_score']:.3f} |\n"

# AD
md += "\n## Applicability Domain (Spearman ρ: Error vs Max Train Tanimoto)\n"
for name, m in ad.items():
    s = name.split('_')
    model, rep = s[0], s[1]
    md += f"- **{model} ({rep})**: {m['Spearman_rho']:.3f}\n"

# S1
md += "\n## Sensitivity S1 (Regression N=731, Classifier N=1089)\n"
md += "| Model | Rep | MAE (S1) | Macro-F1 (S1) |\n"
md += "|---|---|---|---|\n"
for name in metrics['s1']['regression'].keys():
    s = name.split('_')
    model, rep = s[0], s[1]
    if model == 'Ridge': clf_model = 'LogisticRegression'
    elif model == 'RandomForestRegressor': clf_model = 'RandomForestClassifier'
    else: clf_model = model
    clf_name = f"{clf_model}_{rep}"
    if clf_name in metrics['s1']['classifier']:
        clf_f1 = metrics['s1']['classifier'][clf_name]['Macro_F1']
    else:
        clf_f1 = float('nan')
    md += f"| {model} | {rep} | {metrics['s1']['regression'][name]['MAE']:.3f} | {clf_f1:.3f} |\n"

md += """
## Limitations & Interpretation
* **Calculated Metric vs Clinical PK**: These metrics evaluate strictly 2D mathematical ranking on in vitro microsomal stability (CLint). They do NOT make any clinical human clearance prediction or patient exposure prediction.
* **Exact Latent Values**: We do not infer or claim exact latent values for explicit censored observations.
"""

with open('results/primary_v1/PRIMARY_MODELLING_RESULTS.md', 'w', encoding='utf-8') as f:
    f.write(md)

print("Markdown report generated.")
