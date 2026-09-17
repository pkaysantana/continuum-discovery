import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
import hashlib

def classify_relation(row):
    rel = str(row).strip()
    if pd.isna(row) or rel == 'nan' or rel == '=' or rel == '~' or rel == '':
        return 'IN-RANGE'
    elif '<' in rel:
        return 'BELOW'
    elif '>' in rel:
        return 'ABOVE'
    else:
        return 'IN-RANGE'

def run_pipeline(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Load datasets
    df_hlm = pd.read_csv('data/interim/CHEMBL3301370_rows.csv')
    df_hh = pd.read_csv('data/interim/CHEMBL3301372_rows.csv')
    
    assert len(df_hlm) == 1102
    assert len(df_hh) == 408
    
    # 2. Reconstruct exact paired overlap
    # We join on canonical_smiles_rdkit
    paired = pd.merge(df_hlm, df_hh, on='canonical_smiles_rdkit', suffixes=('_hlm', '_hh'), how='inner')
    
    assert len(paired) == 187, f"Expected 187, got {len(paired)}"
    
    # Save the paired cohort
    cohort = paired[['molecule_chembl_id_hlm', 'canonical_smiles_rdkit', 
                     'standard_value_hlm', 'standard_relation_hlm',
                     'standard_value_hh', 'standard_relation_hh']].copy()
    cohort.rename(columns={'molecule_chembl_id_hlm': 'molecule_chembl_id'}, inplace=True)
    
    # 3. Preserve frozen class definitions
    cohort['class_hlm'] = paired['standard_relation_hlm'].apply(classify_relation)
    cohort['class_hh'] = paired['standard_relation_hh'].apply(classify_relation)
    
    # Find the ambiguous 13 records in HLM (null relation at value 3)
    # The original condition: standard_relation is null and standard_value == 3.0
    ambig_hlm_mask = cohort['standard_relation_hlm'].isna() & (cohort['standard_value_hlm'] == 3.0)
    cohort['is_hlm_ambiguous_at_3'] = ambig_hlm_mask
    n_ambiguous_paired = ambig_hlm_mask.sum()
    
    cohort.to_csv(f'{out_dir}/paired_cohort_187.csv', index=False)
    
    # 4. 3x3 paired censoring-class cross-tab
    categories = ['BELOW', 'IN-RANGE', 'ABOVE']
    cohort['class_hlm'] = pd.Categorical(cohort['class_hlm'], categories=categories)
    cohort['class_hh'] = pd.Categorical(cohort['class_hh'], categories=categories)
    
    xtab = pd.crosstab(cohort['class_hlm'], cohort['class_hh'], dropna=False)
    xtab_row_pct = pd.crosstab(cohort['class_hlm'], cohort['class_hh'], dropna=False, normalize='index')
    xtab_col_pct = pd.crosstab(cohort['class_hlm'], cohort['class_hh'], dropna=False, normalize='columns')
    
    xtab.to_csv(f'{out_dir}/crosstab_counts.csv')
    xtab_row_pct.to_csv(f'{out_dir}/crosstab_row_pct.csv')
    xtab_col_pct.to_csv(f'{out_dir}/crosstab_col_pct.csv')
    
    # Calculate agreement stats
    exact_agree = sum(cohort['class_hlm'] == cohort['class_hh'])
    non_adj_disagree = sum((cohort['class_hlm'] == 'BELOW') & (cohort['class_hh'] == 'ABOVE')) + \
                       sum((cohort['class_hlm'] == 'ABOVE') & (cohort['class_hh'] == 'BELOW'))
    adj_disagree = len(cohort) - exact_agree - non_adj_disagree
    
    agree_stats = {
        'exact_count': int(exact_agree),
        'exact_prop': float(exact_agree / len(cohort)),
        'adjacent_count': int(adj_disagree),
        'adjacent_prop': float(adj_disagree / len(cohort)),
        'non_adjacent_count': int(non_adj_disagree),
        'non_adjacent_prop': float(non_adj_disagree / len(cohort))
    }
    
    # 5. Primary paired continuous analysis
    # Double in-range
    double_in_mask = (cohort['class_hlm'] == 'IN-RANGE') & (cohort['class_hh'] == 'IN-RANGE')
    double_in = cohort[double_in_mask].copy()
    
    double_in['log10_hlm'] = np.log10(double_in['standard_value_hlm'].astype(float))
    double_in['log10_hh'] = np.log10(double_in['standard_value_hh'].astype(float))
    
    double_in.to_csv(f'{out_dir}/doubly_inrange_cohort.csv', index=False)
    
    n_primary = len(double_in)
    spearman_rho, spearman_p = spearmanr(double_in['log10_hlm'], double_in['log10_hh'])
    
    primary_metrics = {
        'n': int(n_primary),
        'spearman_rho': float(spearman_rho),
        'spearman_pvalue': float(spearman_p)
    }
    
    # 6. Visualisation
    plt.figure(figsize=(6,6))
    plt.scatter(double_in['log10_hlm'], double_in['log10_hh'], alpha=0.7)
    plt.xlabel('log10 HLM CLint (uL/min/mg)')
    plt.ylabel('log10 HH CLint (uL/min/1M cells)')
    plt.title(f'Paired IN-RANGE HLM vs HH (N={n_primary}, rho={spearman_rho:.3f})')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{out_dir}/scatter_doubly_inrange.png', dpi=300)
    plt.close()
    
    # 7. S1 Sensitivity
    # Remove ambiguous HLM
    s1_cohort = cohort[~cohort['is_hlm_ambiguous_at_3']].copy()
    s1_xtab = pd.crosstab(s1_cohort['class_hlm'], s1_cohort['class_hh'], dropna=False)
    s1_xtab.to_csv(f'{out_dir}/s1_crosstab_counts.csv')
    
    s1_double_in_mask = (s1_cohort['class_hlm'] == 'IN-RANGE') & (s1_cohort['class_hh'] == 'IN-RANGE')
    s1_double_in = s1_cohort[s1_double_in_mask].copy()
    
    s1_double_in['log10_hlm'] = np.log10(s1_double_in['standard_value_hlm'].astype(float))
    s1_double_in['log10_hh'] = np.log10(s1_double_in['standard_value_hh'].astype(float))
    s1_double_in.to_csv(f'{out_dir}/s1_doubly_inrange_cohort.csv', index=False)
    
    n_s1 = len(s1_double_in)
    s1_spearman_rho, s1_spearman_p = spearmanr(s1_double_in['log10_hlm'], s1_double_in['log10_hh'])
    
    s1_metrics = {
        'n': int(n_s1),
        'spearman_rho': float(s1_spearman_rho),
        'spearman_pvalue': float(s1_spearman_p)
    }
    
    with open(f'{out_dir}/provenance.json', 'w') as f:
        json.dump({
            'total_paired_n': 187,
            'n_ambiguous_hlm_in_paired': int(n_ambiguous_paired),
            'agree_stats': agree_stats,
            'primary_metrics': primary_metrics,
            's1_metrics': s1_metrics
        }, f, indent=2)
        
    return {
        'xtab': xtab,
        's1_xtab': s1_xtab,
        'cohort': cohort,
        'primary_metrics': primary_metrics,
        's1_metrics': s1_metrics,
        'agree_stats': agree_stats
    }

if __name__ == '__main__':
    run_pipeline('results/hlm_hh_pairing_v1')
