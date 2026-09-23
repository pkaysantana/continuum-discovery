with open('src/execute_v2.py', 'r') as f:
    c = f.read()

c = c.replace("df_primary.join(part_map, on='chembl_id', how='left')", "df_primary.merge(part_map, on='chembl_id', how='left', suffixes=('', '_part'))")
c = c.replace("df_tail.join(part_map, on='chembl_id', how='left')", "df_tail.merge(part_map, on='chembl_id', how='left', suffixes=('', '_part'))")
c = c.replace("df_ambig.join(part_map, on='chembl_id', how='left')", "df_ambig.merge(part_map, on='chembl_id', how='left', suffixes=('', '_part'))")

with open('src/execute_v2.py', 'w') as f:
    f.write(c)
