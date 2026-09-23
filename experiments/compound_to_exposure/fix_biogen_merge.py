with open('src/execute_v2.py', 'r') as f:
    c = f.read()

c = c.replace(
    "df_bio1_pf['canonical_smiles'] = df_bio1_pf[BIOGEN_STRUCTURE_COLUMN]\n        part_b1_pf = compute_master_partition(df_bio1_pf, set(df_bio1_pf['chembl_id']))\n        df_bio1_pf = df_bio1_pf.merge(part_b1_pf, on='chembl_id', how='left')",
    "df_bio1_pf['canonical_smiles'] = df_bio1_pf[BIOGEN_STRUCTURE_COLUMN]\n        df_bio1_pf = compute_master_partition(df_bio1_pf, set(df_bio1_pf['chembl_id']))"
)

c = c.replace(
    "df_bio1['canonical_smiles'] = df_bio1[BIOGEN_STRUCTURE_COLUMN]\n            part_b1 = compute_master_partition(df_bio1, set(df_bio1['chembl_id']))\n            df_bio1 = df_bio1.merge(part_b1, on='chembl_id', how='left')",
    "df_bio1['canonical_smiles'] = df_bio1[BIOGEN_STRUCTURE_COLUMN]\n            df_bio1 = compute_master_partition(df_bio1, set(df_bio1['chembl_id']))"
)

with open('src/execute_v2.py', 'w') as f:
    f.write(c)
