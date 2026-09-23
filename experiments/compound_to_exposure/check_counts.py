import pandas as pd

df = pd.read_csv('splits/master_partition.csv')
df_p = df[df['status'] == 'INTERIOR_OBSERVED']

full_size = len(df)
interior_size = len(df_p)
holdout = len(df_p[df_p['partition'] == 'holdout'])
cv = len(df_p[df_p['partition'] == 'cv'])
full_holdout = len(df[df['partition'] == 'holdout'])

print(f"Full size: {full_size}")
print(f"Interior size: {interior_size}")
print(f"Holdout interior: {holdout}")
print(f"CV interior: {cv}")
print(f"Full holdout count: {full_holdout}")

cv_folds = df_p[df_p['partition'] == 'cv']['cv_fold'].value_counts().sort_index()
print("CV folds:")
print(cv_folds)
