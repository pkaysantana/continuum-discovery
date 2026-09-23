with open('src/execute_v2.py', 'r') as f:
    c = f.read()

# Fix Compound ID -> Internal ID
c = c.replace("'Compound ID': 'chembl_id'", "'Internal ID': 'chembl_id'")

# Fix partition calls
old_part_pf = "part_b1_pf = compute_master_partition(df_bio1_pf, n_folds=5)"
new_part_pf = "df_bio1_pf['canonical_smiles'] = df_bio1_pf[BIOGEN_STRUCTURE_COLUMN]\n        part_b1_pf = compute_master_partition(df_bio1_pf, set(df_bio1_pf['chembl_id']))"
c = c.replace(old_part_pf, new_part_pf)

old_part = "part_b1 = compute_master_partition(df_bio1, n_folds=5)"
new_part = "df_bio1['canonical_smiles'] = df_bio1[BIOGEN_STRUCTURE_COLUMN]\n            part_b1 = compute_master_partition(df_bio1, set(df_bio1['chembl_id']))"
c = c.replace(old_part, new_part)

with open('src/execute_v2.py', 'w') as f:
    f.write(c)
