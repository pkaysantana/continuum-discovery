import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import shutil

os.makedirs('results/final_figures_v1', exist_ok=True)
sns.set_theme(style='whitegrid', context='paper', font_scale=1.2)

# 1. AZ observed-vs-predicted for a representative learned model (RF Morgan)
df_primary = pd.read_csv('results/primary_v1/REGRESSION_PREDICTIONS.csv')
df_rf = df_primary[(df_primary['model'] == 'RandomForestRegressor') & (df_primary['representation'] == 'Morgan')]
plt.figure(figsize=(6, 6))
sns.scatterplot(data=df_rf, x='observed', y='prediction', alpha=0.5, edgecolor='none')
plt.plot([-3, 4], [-3, 4], 'r--', zorder=3)
plt.title('AZ Primary HLM: Obs vs Pred (RF Morgan)')
plt.xlabel('Observed log(CLint)')
plt.ylabel('Predicted log(CLint)')
plt.xlim(-3, 4)
plt.ylim(-3, 4)
plt.tight_layout()
plt.savefig('results/final_figures_v1/fig1_az_obs_vs_pred_rf_morgan.png', dpi=300)
plt.close()

# 2. AZ model-comparison figure
az_perf = pd.DataFrame({
    'Model': ['Ridge desc', 'Ridge Morgan', 'RF desc', 'RF Morgan', 'Mean Baseline', 'Median Baseline'],
    'Spearman ρ': [0.120, 0.391, 0.362, 0.417, -0.089, -0.089]
})
plt.figure(figsize=(8, 5))
sns.barplot(data=az_perf, x='Spearman ρ', y='Model', color='steelblue')
plt.title('AZ Primary HLM: Rank Correlation by Model')
plt.xlabel('Spearman ρ')
plt.ylabel('')
plt.tight_layout()
plt.savefig('results/final_figures_v1/fig2_az_model_comparison.png', dpi=300)
plt.close()

# 3. AZ AD figure (RF Morgan)
shutil.copy(
    'results/primary_v1/plots/ad_RandomForestRegressor_Morgan.png', 
    'results/final_figures_v1/fig3_az_ad_rf_morgan.png'
)

# 4. HLM-vs-HH paired scatter
shutil.copy(
    'results/hlm_hh_pairing_v1/scatter_doubly_inrange.png',
    'results/final_figures_v1/fig4_hlm_vs_hh_scatter.png'
)

# 5. HLMxHH 3x3 category heatmap
categories = ['BELOW', 'IN-RANGE', 'ABOVE']
cat_matrix = np.array([
    [31, 20, 0],
    [26, 96, 5],
    [0, 8, 1]
])
plt.figure(figsize=(5, 4))
sns.heatmap(cat_matrix, annot=True, fmt='d', cmap='Blues', 
            xticklabels=categories, yticklabels=categories)
plt.title('HLM vs HH: Censoring Category Agreement')
plt.ylabel('HLM')
plt.xlabel('HH')
plt.tight_layout()
plt.savefig('results/final_figures_v1/fig5_hlm_vs_hh_heatmap.png', dpi=300)
plt.close()

# 6. Cross-dataset Spearman comparison
cross_study = pd.DataFrame({
    'Model': ['Ridge desc', 'Ridge Morgan', 'RF desc', 'RF Morgan'],
    'AZ Primary': [0.120, 0.391, 0.362, 0.417],
    'TDC Test': [0.146, 0.499, 0.266, 0.371],
    'Biogen Primary': [0.549, 0.541, 0.551, 0.485]
})
df_melt = cross_study.melt(id_vars='Model', var_name='Dataset', value_name='Spearman ρ')
plt.figure(figsize=(8, 5))
sns.barplot(data=df_melt, x='Dataset', y='Spearman ρ', hue='Model', palette='Set2')
plt.title('Cross-Dataset Model Performance')
plt.ylim(0, 0.6)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('results/final_figures_v1/fig6_cross_dataset_spearman.png', dpi=300)
plt.close()

# 7. Biogen primary vs sensitivity comparison
biogen_data = pd.DataFrame({
    'Model': ['Ridge desc', 'Ridge Morgan', 'RF desc', 'RF Morgan'],
    'Biogen Primary': [0.549, 0.541, 0.551, 0.485],
    'Biogen Sensitivity': [0.378, 0.384, 0.400, 0.343]
})
df_melt_bio = biogen_data.melt(id_vars='Model', var_name='Cohort', value_name='Spearman ρ')
plt.figure(figsize=(6, 5))
sns.barplot(data=df_melt_bio, x='Model', y='Spearman ρ', hue='Cohort', palette='Paired')
plt.title('Biogen: Primary vs Sensitivity Cohort')
plt.xticks(rotation=45)
plt.ylim(0, 0.6)
plt.tight_layout()
plt.savefig('results/final_figures_v1/fig7_biogen_primary_vs_sensitivity.png', dpi=300)
plt.close()

print("Figures successfully generated in results/final_figures_v1/")
