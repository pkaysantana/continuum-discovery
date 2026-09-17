import os
import json
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, f1_score, precision_score, recall_score, balanced_accuracy_score, matthews_corrcoef, confusion_matrix
from scipy.stats import spearmanr
from rdkit import Chem
from rdkit import DataStructs
from rdkit.Chem import rdMolDescriptors

def compute_regression_metrics(df):
    results = {}
    for (model, repr_type), group in df.groupby(['model', 'representation']):
        # Primary metrics only on IN-RANGE
        in_range = group[group['censoring_class'] == 'IN-RANGE']
        obs = in_range['observed'].values
        pred = in_range['prediction'].values
        mae = mean_absolute_error(obs, pred)
        rmse = np.sqrt(mean_squared_error(obs, pred))
        rho, _ = spearmanr(obs, pred)
        r2 = r2_score(obs, pred)
        frac = np.mean(np.abs(obs - pred) <= np.log10(2))
        results[f"{model}_{repr_type}"] = {
            'MAE': float(mae), 'RMSE': float(rmse), 'Spearman_rho': float(rho), 'R2': float(r2), 'Fraction_within_2fold': float(frac), 'N': int(len(obs))
        }
    return results

def compute_tail_ordering(df):
    results = []
    for (model, repr_type), group in df.groupby(['model', 'representation']):
        if model in ['mean_baseline', 'median_baseline']: continue
        for fold in range(5):
            f_group = group[group['outer_fold'] == fold]
            in_range = f_group[f_group['censoring_class'] == 'IN-RANGE']['prediction'].values
            below = f_group[f_group['censoring_class'] == 'BELOW']['prediction'].values
            above = f_group[f_group['censoring_class'] == 'ABOVE']['prediction'].values
            
            # Lower
            if len(below) > 0 and len(in_range) > 0:
                eligible = len(below) * len(in_range)
                score = 0
                for pl in below:
                    score += np.sum(pl < in_range) + 0.5 * np.sum(pl == in_range)
                results.append({'model': model, 'representation': repr_type, 'fold': fold, 'tail': 'Lower', 'eligible': eligible, 'score_num': score, 'q_n': len(in_range), 'tail_n': len(below)})
            else:
                results.append({'model': model, 'representation': repr_type, 'fold': fold, 'tail': 'Lower', 'eligible': 0, 'score_num': 0, 'q_n': len(in_range), 'tail_n': len(below)})

            # Upper
            if len(above) > 0 and len(in_range) > 0:
                eligible = len(above) * len(in_range)
                score = 0
                for pu in above:
                    score += np.sum(pu > in_range) + 0.5 * np.sum(pu == in_range)
                results.append({'model': model, 'representation': repr_type, 'fold': fold, 'tail': 'Upper', 'eligible': eligible, 'score_num': score, 'q_n': len(in_range), 'tail_n': len(above)})
            else:
                results.append({'model': model, 'representation': repr_type, 'fold': fold, 'tail': 'Upper', 'eligible': 0, 'score_num': 0, 'q_n': len(in_range), 'tail_n': len(above)})

    # Aggregate
    agg_res = {}
    tail_df = pd.DataFrame(results)
    for (model, repr_type, tail), g in tail_df.groupby(['model', 'representation', 'tail']):
        total_eligible = g['eligible'].sum()
        total_score = g['score_num'].sum()
        agg_res[f"{model}_{repr_type}_{tail}"] = {
            'eligible_pairs': int(total_eligible),
            'score_numerator': float(total_score),
            'final_score': float(total_score / total_eligible) if total_eligible > 0 else np.nan,
            'actual_tail_N': int(g['tail_n'].sum()),
            'actual_Q_N': int(g['q_n'].sum())
        }
    return agg_res

def compute_classifier_metrics(df):
    results = {}
    label_map = {'BELOW': 0, 'IN-RANGE': 1, 'ABOVE': 2}
    for (model, repr_type), group in df.groupby(['model', 'representation']):
        obs = group['true_class'].map(label_map).values
        pred = group['pred_class'].map(label_map).values
        
        macro_f1 = f1_score(obs, pred, average='macro')
        precision = precision_score(obs, pred, average=None, labels=[0,1,2]).tolist()
        recall = recall_score(obs, pred, average=None, labels=[0,1,2]).tolist()
        bal_acc = balanced_accuracy_score(obs, pred)
        mcc = matthews_corrcoef(obs, pred)
        cm = confusion_matrix(obs, pred, labels=[0,1,2]).tolist()
        
        # Adjacent/Non-adjacent errors
        cm_arr = np.array(cm)
        adj_b_i = cm_arr[0,1] + cm_arr[1,0]
        adj_i_a = cm_arr[1,2] + cm_arr[2,1]
        non_adj_b_a = cm_arr[0,2] + cm_arr[2,0]
        total = np.sum(cm_arr)
        
        results[f"{model}_{repr_type}"] = {
            'Macro_F1': float(macro_f1),
            'Balanced_Accuracy': float(bal_acc),
            'MCC': float(mcc),
            'Precision_BELOW': float(precision[0]), 'Precision_IN-RANGE': float(precision[1]), 'Precision_ABOVE': float(precision[2]),
            'Recall_BELOW': float(recall[0]), 'Recall_IN-RANGE': float(recall[1]), 'Recall_ABOVE': float(recall[2]),
            'CM': cm,
            'Adjacent_Errors_BELOW_IN-RANGE': int(adj_b_i),
            'Adjacent_Errors_IN-RANGE_ABOVE': int(adj_i_a),
            'NonAdjacent_Errors_BELOW_ABOVE': int(non_adj_b_a)
        }
    return results

reg_df = pd.read_csv('results/primary_v1/REGRESSION_PREDICTIONS.csv')
clf_df = pd.read_csv('results/primary_v1/CLASSIFIER_PREDICTIONS.csv')

primary_reg = compute_regression_metrics(reg_df)
primary_tail = compute_tail_ordering(reg_df)
primary_clf = compute_classifier_metrics(clf_df)

reg_s1_df = pd.read_csv('results/primary_v1/S1_REGRESSION_PREDICTIONS.csv')
clf_s1_df = pd.read_csv('results/primary_v1/S1_CLASSIFIER_PREDICTIONS.csv')

s1_reg = compute_regression_metrics(reg_s1_df)
s1_tail = compute_tail_ordering(reg_s1_df)
s1_clf = compute_classifier_metrics(clf_s1_df)

with open('results/primary_v1/METRICS.json', 'w') as f:
    json.dump({'primary': {'regression': primary_reg, 'tail': primary_tail, 'classifier': primary_clf},
               's1': {'regression': s1_reg, 'tail': s1_tail, 'classifier': s1_clf}}, f, indent=2)

print("Metrics computed successfully.")
