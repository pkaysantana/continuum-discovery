import os
import json
import hashlib
import pandas as pd
import numpy as np
import warnings
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors, Lipinski
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
                             f1_score, precision_score, recall_score, balanced_accuracy_score,
                             matthews_corrcoef, confusion_matrix)
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr
from collections import defaultdict

warnings.filterwarnings("ignore")

# --- 1. Load Data ---
folds_df = pd.read_csv('splits/HLM_OUTER_FOLDS_V1.csv')
raw_df = pd.read_csv('data/interim/CHEMBL3301370_rows.csv')
merged = pd.merge(folds_df, raw_df[['activity_id', 'standard_value']], on='activity_id', how='left')
assert len(merged) == 1102
assert merged['standard_value'].notnull().all()

# Log10 target for regression
merged['log10_CLint'] = np.log10(merged['standard_value'].astype(float))

# --- 2. Calculate Features ---
mw, clogp, tpsa, hbd, hba, rotb, csp3 = [], [], [], [], [], [], []
morgan_fps = []
for smi in merged['canonical_smiles_rdkit']:
    mol = Chem.MolFromSmiles(smi)
    assert mol is not None
    mw.append(Descriptors.MolWt(mol))
    clogp.append(Crippen.MolLogP(mol))
    tpsa.append(rdMolDescriptors.CalcTPSA(mol))
    hbd.append(Lipinski.NumHDonors(mol))
    hba.append(Lipinski.NumHAcceptors(mol))
    rotb.append(rdMolDescriptors.CalcNumRotatableBonds(mol, rdMolDescriptors.NumRotatableBondsOptions.Strict))
    csp3.append(rdMolDescriptors.CalcFractionCSP3(mol))
    
    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048, useChirality=True)
    arr = np.zeros((0,), dtype=np.int8)
    from rdkit import DataStructs
    DataStructs.ConvertToNumpyArray(fp, arr)
    morgan_fps.append(arr)

X_desc = np.column_stack([mw, clogp, tpsa, hbd, hba, rotb, csp3])
X_morg = np.array(morgan_fps)

# --- Inner Tuning Helper ---
def tune_hyperparams(X, y, groups, model_type, repr_type, is_classification):
    # Setup grid and ties
    if model_type == 'Ridge':
        grid = [{'alpha': a} for a in [0.1, 1.0, 10.0]]
        def tie_key(p): return p['alpha']
    elif model_type == 'LogisticRegression':
        grid = [{'C': c} for c in [0.1, 1.0, 10.0]]
        def tie_key(p): return -p['C'] # smaller C preferred
    elif model_type == 'RandomForestRegressor' or model_type == 'RandomForestClassifier':
        grid = [{'max_depth': d} for d in [10, None]]
        def tie_key(p): return 1 if p['max_depth'] == 10 else 0
    else:
        raise ValueError(f"Unknown {model_type}")

    inner_cv = GroupKFold(n_splits=3)
    best_score = -np.inf
    best_param = None
    
    for params in grid:
        scores = []
        for train_idx, val_idx in inner_cv.split(X, y, groups):
            X_tr, y_tr = X[train_idx], y[train_idx]
            X_val, y_val = X[val_idx], y[val_idx]
            
            # Preprocessing (scale descriptors only)
            if repr_type == 'descriptors':
                scaler = StandardScaler()
                X_tr = scaler.fit_transform(X_tr)
                X_val = scaler.transform(X_val)
                
            if model_type == 'Ridge':
                m = Ridge(solver="lsqr", tol=1e-4, max_iter=10000, fit_intercept=True, **params)
                m.fit(X_tr, y_tr)
                preds = m.predict(X_val)
                score = -mean_absolute_error(y_val, preds) # maximize neg MAE
            elif model_type == 'LogisticRegression':
                m = LogisticRegression(solver="lbfgs", max_iter=5000, tol=1e-4, class_weight="balanced", **params)
                m.fit(X_tr, y_tr)
                preds = m.predict(X_val)
                score = f1_score(y_val, preds, average='macro')
            elif model_type == 'RandomForestRegressor':
                m = RandomForestRegressor(criterion="squared_error", max_features=1.0, bootstrap=True, min_samples_split=2, min_samples_leaf=1, random_state=42, n_estimators=100, n_jobs=1, **params)
                m.fit(X_tr, y_tr)
                preds = m.predict(X_val)
                score = -mean_absolute_error(y_val, preds)
            elif model_type == 'RandomForestClassifier':
                m = RandomForestClassifier(criterion="gini", max_features="sqrt", bootstrap=True, min_samples_split=2, min_samples_leaf=1, class_weight="balanced", random_state=42, n_estimators=100, n_jobs=1, **params)
                m.fit(X_tr, y_tr)
                preds = m.predict(X_val)
                score = f1_score(y_val, preds, average='macro')
                
            scores.append(score)
            
        mean_score = np.mean(scores)
        
        if best_param is None:
            best_score = mean_score
            best_param = params
        else:
            diff = mean_score - best_score
            if diff > 1e-6:
                best_score = mean_score
                best_param = params
            elif abs(diff) <= 1e-6:
                # tie breaker
                if tie_key(params) > tie_key(best_param):
                    best_score = mean_score
                    best_param = params

    return best_param

def run_models(df, X_desc, X_morg, is_s1=False):
    reg_results = []
    clf_results = []
    hyperparams = []
    
    # Regression
    for fold in range(5):
        train_mask = (df['outer_fold'] != fold) & (df['censoring_class'] == 'IN-RANGE')
        test_mask = (df['outer_fold'] == fold) # all compounds in fold for evaluation (including ABOVE/BELOW for tail ordering)
        
        y_train = df.loc[train_mask, 'log10_CLint'].values
        groups_train = df.loc[train_mask, 'scaffold_group_key'].values
        
        # Baselines
        train_mean = np.mean(y_train)
        train_median = np.median(y_train)
        for idx in df[test_mask].index:
            obs = df.loc[idx, 'log10_CLint'] if df.loc[idx, 'censoring_class'] == 'IN-RANGE' else np.nan
            reg_results.append({'activity_id': df.loc[idx, 'activity_id'], 'outer_fold': fold, 'censoring_class': df.loc[idx, 'censoring_class'], 'model': 'mean_baseline', 'representation': 'none', 'prediction': train_mean, 'observed': obs})
            reg_results.append({'activity_id': df.loc[idx, 'activity_id'], 'outer_fold': fold, 'censoring_class': df.loc[idx, 'censoring_class'], 'model': 'median_baseline', 'representation': 'none', 'prediction': train_median, 'observed': obs})

        for repr_type, X_full in [('descriptors', X_desc), ('Morgan', X_morg)]:
            X_train = X_full[train_mask]
            X_test = X_full[test_mask]
            
            for model_type in ['Ridge', 'RandomForestRegressor']:
                best_p = tune_hyperparams(X_train, y_train, groups_train, model_type, repr_type, False)
                hyperparams.append({'model': model_type, 'representation': repr_type, 'fold': fold, **best_p})
                
                # Fit outer model
                X_tr, X_te = X_train, X_test
                if repr_type == 'descriptors':
                    scaler = StandardScaler()
                    X_tr = scaler.fit_transform(X_tr)
                    X_te = scaler.transform(X_te)
                
                if model_type == 'Ridge':
                    m = Ridge(solver="lsqr", tol=1e-4, max_iter=10000, fit_intercept=True, **best_p)
                else:
                    m = RandomForestRegressor(criterion="squared_error", max_features=1.0, bootstrap=True, min_samples_split=2, min_samples_leaf=1, random_state=42, n_estimators=100, n_jobs=1, **best_p)
                    
                m.fit(X_tr, y_train)
                preds = m.predict(X_te)
                
                for i, idx in enumerate(df[test_mask].index):
                    obs = df.loc[idx, 'log10_CLint'] if df.loc[idx, 'censoring_class'] == 'IN-RANGE' else np.nan
                    reg_results.append({'activity_id': df.loc[idx, 'activity_id'], 'outer_fold': fold, 'censoring_class': df.loc[idx, 'censoring_class'], 'model': model_type, 'representation': repr_type, 'prediction': preds[i], 'observed': obs})
                    
    # Classifier
    label_map = {'BELOW': 0, 'IN-RANGE': 1, 'ABOVE': 2}
    # To use macro-f1, we need all classes.
    for fold in range(5):
        train_mask = (df['outer_fold'] != fold)
        test_mask = (df['outer_fold'] == fold)
        
        y_train_clf = df.loc[train_mask, 'censoring_class'].map(label_map).values
        groups_train = df.loc[train_mask, 'scaffold_group_key'].values
        
        # Majority baseline
        majority_class = df.loc[train_mask, 'censoring_class'].mode()[0]
        for idx in df[test_mask].index:
            clf_results.append({'activity_id': df.loc[idx, 'activity_id'], 'outer_fold': fold, 'true_class': df.loc[idx, 'censoring_class'], 'model': 'majority_baseline', 'representation': 'none', 'pred_class': majority_class, 'prob_BELOW': np.nan, 'prob_IN-RANGE': np.nan, 'prob_ABOVE': np.nan})

        for repr_type, X_full in [('descriptors', X_desc), ('Morgan', X_morg)]:
            X_train = X_full[train_mask]
            X_test = X_full[test_mask]
            
            for model_type in ['LogisticRegression', 'RandomForestClassifier']:
                best_p = tune_hyperparams(X_train, y_train_clf, groups_train, model_type, repr_type, True)
                hyperparams.append({'model': model_type, 'representation': repr_type, 'fold': fold, **best_p})
                
                X_tr, X_te = X_train, X_test
                if repr_type == 'descriptors':
                    scaler = StandardScaler()
                    X_tr = scaler.fit_transform(X_tr)
                    X_te = scaler.transform(X_te)
                
                if model_type == 'LogisticRegression':
                    m = LogisticRegression(solver="lbfgs", max_iter=5000, tol=1e-4, class_weight="balanced", **best_p)
                else:
                    m = RandomForestClassifier(criterion="gini", max_features="sqrt", bootstrap=True, min_samples_split=2, min_samples_leaf=1, class_weight="balanced", random_state=42, n_estimators=100, n_jobs=1, **best_p)
                
                m.fit(X_tr, y_train_clf)
                preds = m.predict(X_te)
                probs = m.predict_proba(X_te)
                
                # Check class order in proba (should be 0,1,2 since all are present in train)
                rev_map = {0: 'BELOW', 1: 'IN-RANGE', 2: 'ABOVE'}
                for i, idx in enumerate(df[test_mask].index):
                    clf_results.append({'activity_id': df.loc[idx, 'activity_id'], 'outer_fold': fold, 'true_class': df.loc[idx, 'censoring_class'], 'model': model_type, 'representation': repr_type, 'pred_class': rev_map[preds[i]], 'prob_BELOW': probs[i, list(m.classes_).index(0)], 'prob_IN-RANGE': probs[i, list(m.classes_).index(1)], 'prob_ABOVE': probs[i, list(m.classes_).index(2)]})
                    
    return pd.DataFrame(reg_results), pd.DataFrame(clf_results), hyperparams

# Run primary
reg_df, clf_df, hp = run_models(merged, X_desc, X_morg, is_s1=False)

os.makedirs('results/primary_v1', exist_ok=True)
reg_df.to_csv('results/primary_v1/REGRESSION_PREDICTIONS.csv', index=False)
clf_df.to_csv('results/primary_v1/CLASSIFIER_PREDICTIONS.csv', index=False)
with open('results/primary_v1/HYPERPARAMETERS.json', 'w') as f:
    json.dump(hp, f, indent=2)

# --- S1 Sensitivity ---
s1_mask = ~( (merged['censoring_class'] == 'IN-RANGE') & (merged['standard_value'] == 3.0) & (raw_df['standard_relation'].isna() | (raw_df['standard_relation'] == '')) )
merged_s1 = merged[s1_mask].reset_index(drop=True)
# Also apply to X
X_desc_s1 = X_desc[s1_mask]
X_morg_s1 = X_morg[s1_mask]

reg_s1_df, clf_s1_df, hp_s1 = run_models(merged_s1, X_desc_s1, X_morg_s1, is_s1=True)
reg_s1_df.to_csv('results/primary_v1/S1_REGRESSION_PREDICTIONS.csv', index=False)
clf_s1_df.to_csv('results/primary_v1/S1_CLASSIFIER_PREDICTIONS.csv', index=False)

print("Models fitted. S1 counts: reg N =", len(merged_s1[merged_s1['censoring_class'] == 'IN-RANGE']), "clf N =", len(merged_s1))

