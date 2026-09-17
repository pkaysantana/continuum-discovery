import pandas as pd
import numpy as np

# Load data
folds = pd.read_csv('splits/HLM_OUTER_FOLDS_V1.csv')
raw_df = pd.read_csv('data/interim/CHEMBL3301370_rows.csv')
reg = pd.read_csv('results/primary_v1/REGRESSION_PREDICTIONS.csv')
clf = pd.read_csv('results/primary_v1/CLASSIFIER_PREDICTIONS.csv')
s1_reg = pd.read_csv('results/primary_v1/S1_REGRESSION_PREDICTIONS.csv')
s1_clf = pd.read_csv('results/primary_v1/S1_CLASSIFIER_PREDICTIONS.csv')

# 1. 744 primary IN-RANGE exactly one OOF reg pred per model
in_range_counts = reg[reg['censoring_class'] == 'IN-RANGE'].groupby(['model', 'representation']).size()
assert (in_range_counts == 744).all(), f"Expected 744 regression predictions per model, got {in_range_counts}"

# 2. 1,102 compounds exactly one OOF clf pred per model
clf_counts = clf.groupby(['model', 'representation']).size()
assert (clf_counts == 1102).all(), f"Expected 1102 classifier predictions per model, got {clf_counts}"

# 3. S1 counts = 731 / 1089
s1_in_range = s1_reg[s1_reg['censoring_class'] == 'IN-RANGE'].groupby(['model', 'representation']).size()
assert (s1_in_range == 731).all(), f"Expected 731 S1 regression predictions per model, got {s1_in_range}"

s1_clf_counts = s1_clf.groupby(['model', 'representation']).size()
assert (s1_clf_counts == 1089).all(), f"Expected 1089 S1 classifier predictions per model, got {s1_clf_counts}"

# 4. No exact continuous target stored for explicit censored tail rows
tail_obs = reg[reg['censoring_class'] != 'IN-RANGE']['observed']
assert tail_obs.isnull().all(), "Continuous targets stored for censored observations!"

# 5. Classifier confusion matrices sum to their cohort N
import json
with open('results/primary_v1/METRICS.json', 'r') as f:
    metrics = json.load(f)

for m_name, m_data in metrics['primary']['classifier'].items():
    cm_sum = sum([sum(row) for row in m_data['CM']])
    assert cm_sum == 1102, f"Confusion matrix sums to {cm_sum} for {m_name}, expected 1102"

for m_name, m_data in metrics['s1']['classifier'].items():
    cm_sum = sum([sum(row) for row in m_data['CM']])
    assert cm_sum == 1089, f"Confusion matrix sums to {cm_sum} for {m_name}, expected 1089"

print("All scientific sanity checks passed.")
