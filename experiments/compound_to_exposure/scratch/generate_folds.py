import pandas as pd
import numpy as np
import json
import hashlib
from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.model_selection import StratifiedGroupKFold
import sklearn

def get_censoring_class(row):
    rel = row['standard_relation']
    val = float(row['standard_value']) if pd.notnull(row['standard_value']) else None
    
    if rel == '<' and val == 3.0:
        return 'BELOW'
    elif rel == '>' and val == 150.0:
        return 'ABOVE'
    else:
        # Any other valid record is IN-RANGE under the frozen working-inference cohort
        return 'IN-RANGE'

# 1. Load data
df = pd.read_csv('data/interim/CHEMBL3301370_rows.csv')
assert len(df) == 1102, f"Expected 1102 rows, got {len(df)}"

# 2. Check activity_id
assert df['activity_id'].notnull().all(), "Missing activity_id"
assert df['activity_id'].is_unique, "activity_id is not unique"

# 3. Apply class assignment
df['censoring_class'] = df.apply(get_censoring_class, axis=1)

# Verify counts
class_counts = df['censoring_class'].value_counts()
assert class_counts['BELOW'] == 274, f"Expected 274 BELOW, got {class_counts.get('BELOW', 0)}"
assert class_counts['IN-RANGE'] == 744, f"Expected 744 IN-RANGE, got {class_counts.get('IN-RANGE', 0)}"
assert class_counts['ABOVE'] == 84, f"Expected 84 ABOVE, got {class_counts.get('ABOVE', 0)}"

# 4. Deterministic ordering
df = df.sort_values('activity_id', ascending=True).reset_index(drop=True)

# 5. Scaffold groups
scaffold_keys = []
for idx, row in df.iterrows():
    smi = row['canonical_smiles_rdkit'] # frozen provenance canonical SMILES
    mol = Chem.MolFromSmiles(smi)
    assert mol is not None
    scaffold = MurckoScaffold.GetScaffoldForMol(mol)
    if scaffold.GetNumAtoms() > 0:
        scaffold_smi = Chem.MolToSmiles(scaffold, isomericSmiles=True, canonical=True)
        scaffold_keys.append(scaffold_smi)
    else:
        # Deterministic singleton keyed by its own full provenance SMILES
        scaffold_keys.append(smi)

df['scaffold_group_key'] = scaffold_keys

# Diagnostics
unique_groups = df['scaffold_group_key'].nunique()
group_sizes = df['scaffold_group_key'].value_counts()
singleton_count = (group_sizes == 1).sum()
# empty-Murcko singletons
empty_murcko = [1 for smi, key in zip(df['canonical_smiles_rdkit'], df['scaffold_group_key']) if smi == key]
empty_murcko_count = len(empty_murcko)

print(f"Unique scaffold groups: {unique_groups}")
print(f"Singleton groups: {singleton_count}")
print(f"Empty-Murcko singleton groups: {empty_murcko_count}")
print(f"Largest scaffold group size: {group_sizes.max()}")

# 6. Generate outer split
X = df['canonical_smiles_rdkit'].values
y = df['censoring_class'].values
groups = df['scaffold_group_key'].values

selected_seed = None
final_folds = np.zeros(len(df), dtype=int) - 1

for seed in range(42, 142):
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    valid = True
    temp_folds = np.zeros(len(df), dtype=int) - 1
    
    for fold, (train_idx, test_idx) in enumerate(cv.split(X, y, groups)):
        temp_folds[test_idx] = fold
        
    for fold in range(5):
        fold_y = y[temp_folds == fold]
        if 'BELOW' not in fold_y or 'IN-RANGE' not in fold_y or 'ABOVE' not in fold_y:
            valid = False
            break
            
    # Also verify no group crosses folds
    # StratifiedGroupKFold guarantees this, but we explicitly assert it
    for g in np.unique(groups):
        if len(np.unique(temp_folds[groups == g])) > 1:
            valid = False
            break
            
    if valid:
        selected_seed = seed
        final_folds = temp_folds
        break

assert selected_seed is not None, "Failed to find a valid seed"
print(f"Selected seed: {selected_seed}")

df['outer_fold'] = final_folds

# Create output dirs if not exist
import os
os.makedirs('splits', exist_ok=True)

# Save artifact
out_df = df[['activity_id', 'molecule_chembl_id', 'canonical_smiles_rdkit', 'censoring_class', 'scaffold_group_key', 'outer_fold']]
out_df = out_df.rename(columns={'molecule_chembl_id': 'molecule_id'})
out_csv = 'splits/HLM_OUTER_FOLDS_V1.csv'
out_df.to_csv(out_csv, index=False)

# Validation Phase 7
assert len(out_df) == 1102
assert out_df['activity_id'].nunique() == 1102
assert out_df['canonical_smiles_rdkit'].nunique() == 1102
assert (out_df['censoring_class'] == 'BELOW').sum() == 274
assert (out_df['censoring_class'] == 'IN-RANGE').sum() == 744
assert (out_df['censoring_class'] == 'ABOVE').sum() == 84
assert out_df['outer_fold'].isin([0,1,2,3,4]).all()
for fold in range(5):
    fold_df = out_df[out_df['outer_fold'] == fold]
    assert len(fold_df) > 0
    assert 'BELOW' in fold_df['censoring_class'].values
    assert 'IN-RANGE' in fold_df['censoring_class'].values
    assert 'ABOVE' in fold_df['censoring_class'].values

for g in out_df['scaffold_group_key'].unique():
    assert out_df[out_df['scaffold_group_key'] == g]['outer_fold'].nunique() == 1
    
print("Artifact validation passed.")

def get_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

# Metadata
metadata = {
    'source_dataset_assay_id': 'CHEMBL3301370',
    'total_N': 1102,
    'class_totals': {'BELOW': 274, 'IN-RANGE': 744, 'ABOVE': 84},
    'rdkit_version': '2025.3.6',
    'scikit_learn_version': sklearn.__version__,
    'split_algorithm': 'StratifiedGroupKFold',
    'n_splits': 5,
    'ordered_candidate_seed_range': [42, 141],
    'selected_seed': selected_seed,
    'deterministic_source_ordering_rule': 'activity_id ascending',
    'scaffold_definition_rule': 'MurckoScaffold.GetScaffoldForMol canonical isomeric smiles',
    'empty_scaffold_rule': 'singleton group keyed by provenance canonical SMILES',
    'fold_sizes': {int(k): int(v) for k, v in out_df['outer_fold'].value_counts().items()},
    'class_counts_per_fold': {int(fold): {cls: int((out_df[out_df['outer_fold'] == fold]['censoring_class'] == cls).sum()) for cls in ['BELOW', 'IN-RANGE', 'ABOVE']} for fold in range(5)},
    'unique_scaffold_count': int(unique_groups),
    'largest_scaffold_group': int(group_sizes.max()),
    'governing_preregistration_tag': 'dmpk-modelling-preregistration-v1',
    'governing_preregistration_sha': 'fefaf215a1a0361470d039238bdf0178e3789410'
}

import datetime
metadata['creation_timestamp'] = datetime.datetime.now(datetime.timezone.utc).isoformat()

out_json = 'splits/HLM_OUTER_FOLDS_V1_METADATA.json'
with open(out_json, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"CSV SHA-256: {get_hash(out_csv)}")
print(f"JSON SHA-256: {get_hash(out_json)}")
