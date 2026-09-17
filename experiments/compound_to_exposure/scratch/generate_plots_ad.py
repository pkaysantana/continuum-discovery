import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import DataStructs
import statsmodels.api as sm

df_folds = pd.read_csv('splits/HLM_OUTER_FOLDS_V1.csv')
df_reg = pd.read_csv('results/primary_v1/REGRESSION_PREDICTIONS.csv')
# Only focus on the 4 learned cells for AD
learned_models = [
    ('Ridge', 'descriptors'), ('Ridge', 'Morgan'),
    ('RandomForestRegressor', 'descriptors'), ('RandomForestRegressor', 'Morgan')
]

# Compute Morgan FP once for all compounds for AD similarity
smi_map = dict(zip(df_folds['activity_id'], df_folds['canonical_smiles_rdkit']))
fps = {}
for act_id, smi in smi_map.items():
    mol = Chem.MolFromSmiles(smi)
    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048, useChirality=True)
    fps[act_id] = fp

ad_results = {}
os.makedirs('results/primary_v1/plots', exist_ok=True)

for model, repr_type in learned_models:
    cell_df = df_reg[(df_reg['model'] == model) & (df_reg['representation'] == repr_type)]
    
    max_sims = []
    abs_errors = []
    obs_all = []
    pred_all = []
    res_all = []
    top_errors = []
    
    for fold in range(5):
        train_act_ids = df_folds[(df_folds['outer_fold'] != fold) & (df_folds['censoring_class'] == 'IN-RANGE')]['activity_id'].values
        train_fps = [fps[a] for a in train_act_ids]
        
        test_inrange = cell_df[(cell_df['outer_fold'] == fold) & (cell_df['censoring_class'] == 'IN-RANGE')]
        for idx, row in test_inrange.iterrows():
            test_fp = fps[row['activity_id']]
            sims = DataStructs.BulkTanimotoSimilarity(test_fp, train_fps)
            max_sim = np.max(sims)
            error = row['prediction'] - row['observed']
            
            max_sims.append(max_sim)
            abs_errors.append(abs(error))
            obs_all.append(row['observed'])
            pred_all.append(row['prediction'])
            res_all.append(error)
            
            top_errors.append({
                'activity_id': row['activity_id'],
                'outer_fold': fold,
                'observed': row['observed'],
                'prediction': row['prediction'],
                'abs_error': abs(error),
                'max_train_similarity': max_sim
            })
            
    # Spearman rho between abs error and max sim
    rho, _ = spearmanr(abs_errors, max_sims)
    ad_results[f"{model}_{repr_type}"] = {'Spearman_rho': rho}
    
    top_errors_df = pd.DataFrame(top_errors).sort_values('abs_error', ascending=False).head(20)
    top_errors_df.to_csv(f'results/primary_v1/top20_errors_{model}_{repr_type}.csv', index=False)
    
    # 1. Applicability domain scatter + lowess
    fig, ax = plt.subplots()
    ax.scatter(max_sims, abs_errors, alpha=0.5, s=10)
    lowess = sm.nonparametric.lowess(abs_errors, max_sims, frac=0.3, it=3, delta=0.0)
    ax.plot(lowess[:, 0], lowess[:, 1], color='red')
    ax.set_xlabel('Max Tanimoto Similarity to Training Fold')
    ax.set_ylabel('Absolute Error (log10)')
    ax.set_title(f'AD: {model} ({repr_type})')
    fig.tight_layout()
    fig.savefig(f'results/primary_v1/plots/ad_{model}_{repr_type}.png')
    plt.close(fig)
    
    # 2. Predicted vs Observed
    fig, ax = plt.subplots()
    ax.scatter(obs_all, pred_all, alpha=0.5, s=10)
    ax.plot([min(obs_all), max(obs_all)], [min(obs_all), max(obs_all)], color='red', linestyle='--')
    ax.set_xlabel('Observed log10(CLint)')
    ax.set_ylabel('Predicted log10(CLint)')
    ax.set_title(f'Pred vs Obs: {model} ({repr_type})')
    fig.tight_layout()
    fig.savefig(f'results/primary_v1/plots/pred_vs_obs_{model}_{repr_type}.png')
    plt.close(fig)
    
    # 3. Residual Distribution
    fig, ax = plt.subplots()
    ax.hist(res_all, bins=30, edgecolor='black')
    ax.set_xlabel('Residual (Pred - Obs)')
    ax.set_ylabel('Count')
    ax.set_title(f'Residuals: {model} ({repr_type})')
    fig.tight_layout()
    fig.savefig(f'results/primary_v1/plots/residuals_{model}_{repr_type}.png')
    plt.close(fig)

with open('results/primary_v1/AD_METRICS.json', 'w') as f:
    json.dump(ad_results, f, indent=2)

print("AD and plotting completed.")
