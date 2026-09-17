import os
import json
import hashlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors, Lipinski

def get_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

# Ensure directories exist
os.makedirs('reports/u6', exist_ok=True)

# 1. Reconstruct frozen cohort
# We can load the exact generated outer folds artifact since it contains the exact N=1102 cohort.
df = pd.read_csv('splits/HLM_OUTER_FOLDS_V1.csv')
assert len(df) == 1102

class_counts = df['censoring_class'].value_counts()
assert class_counts['BELOW'] == 274
assert class_counts['IN-RANGE'] == 744
assert class_counts['ABOVE'] == 84

# 2. Calculate descriptors
mw, clogp, tpsa, hbd, hba, rotb, csp3 = [], [], [], [], [], [], []

for smi in df['canonical_smiles_rdkit']:
    mol = Chem.MolFromSmiles(smi)
    assert mol is not None, f"Failed to parse SMILES: {smi}"
    
    mw.append(Descriptors.MolWt(mol))
    clogp.append(Crippen.MolLogP(mol))
    tpsa.append(rdMolDescriptors.CalcTPSA(mol))
    hbd.append(Lipinski.NumHDonors(mol))
    hba.append(Lipinski.NumHAcceptors(mol))
    rotb.append(rdMolDescriptors.CalcNumRotatableBonds(mol, rdMolDescriptors.NumRotatableBondsOptions.Strict))
    csp3.append(rdMolDescriptors.CalcFractionCSP3(mol))

df['MolecularWeight'] = mw
df['cLogP'] = clogp
df['TPSA'] = tpsa
df['HBD'] = hbd
df['HBA'] = hba
df['RotatableBonds'] = rotb
df['FractionCsp3'] = csp3

descriptors = ['MolecularWeight', 'cLogP', 'TPSA', 'HBD', 'HBA', 'RotatableBonds', 'FractionCsp3']

# Check for missing/non-finite
for desc in descriptors:
    assert df[desc].notnull().all(), f"Missing value in {desc}"
    assert np.isfinite(df[desc]).all(), f"Non-finite value in {desc}"

# 3. Descriptive Statistics
classes = ['BELOW', 'IN-RANGE', 'ABOVE'] # Enforce exact order

stats_rows = []
for desc in descriptors:
    for cls in classes:
        sub = df[df['censoring_class'] == cls][desc]
        stats_rows.append({
            'class': cls,
            'descriptor': desc,
            'N': len(sub),
            'median': sub.median(),
            'Q1': sub.quantile(0.25),
            'Q3': sub.quantile(0.75),
            'IQR': sub.quantile(0.75) - sub.quantile(0.25),
            'min': sub.min(),
            'max': sub.max(),
            'mean': sub.mean(), # supplementary
            'std': sub.std()    # supplementary
        })

stats_df = pd.DataFrame(stats_rows)
out_csv = 'reports/u6/U6_DESCRIPTOR_SUMMARY.csv'
stats_df.to_csv(out_csv, index=False)

# 4. Visualisation (deterministic boxplots)
for desc in descriptors:
    fig, ax = plt.subplots(figsize=(6, 5))
    data_to_plot = [df[df['censoring_class'] == cls][desc].values for cls in classes]
    
    ax.boxplot(data_to_plot, tick_labels=[f"{cls}\n(N={len(d)})" for cls, d in zip(classes, data_to_plot)])
    ax.set_ylabel(desc)
    ax.set_title(f"Distribution of {desc}")
    
    # Save figure
    fig.tight_layout()
    fig.savefig(f'reports/u6/boxplot_{desc}.png', dpi=150)
    plt.close(fig)

# 5. Markdown Report
md_content = f"""# U6 Descriptor Analysis

**Purpose**: Descriptive molecular-property analysis of the DMPK compound-to-exposure project cohort before any predictive modelling.
**Cohort**: Primary HLM classifier cohort (N=1,102).
**Class Counts**: BELOW (N=274), IN-RANGE (N=744), ABOVE (N=84).
**Exact Descriptors**: 
- Molecular Weight
- Crippen cLogP
- TPSA
- H-bond donors
- H-bond acceptors
- Strict rotatable-bond count
- Fraction Csp3
**Exact Structural Handling**: Provenance canonical structure; all disconnected components retained; stereochemistry retained; no salt stripping; no parent selection; no tautomer normalisation.

## Descriptive Statistics
See `U6_DESCRIPTOR_SUMMARY.csv` for exact quantiles (Median, Q1, Q3, Min, Max).

## Visualisations
"""
for desc in descriptors:
    md_content += f"\n### {desc}\n![{desc} distribution](boxplot_{desc}.png)\n"

md_content += """
## Declarations
* **NO inferential testing was performed.** (No p-values, ANOVA, Kruskal-Wallis, etc.)
* **These results CANNOT modify any modelling choice.** They are strictly descriptive.
"""

out_md = 'reports/u6/U6_DESCRIPTOR_ANALYSIS.md'
with open(out_md, 'w') as f:
    f.write(md_content)

print(f"All 1,102 structures successfully parsed and descriptors computed.")
print(f"CSV SHA-256: {get_hash(out_csv)}")
print(f"Report SHA-256: {get_hash(out_md)}")
