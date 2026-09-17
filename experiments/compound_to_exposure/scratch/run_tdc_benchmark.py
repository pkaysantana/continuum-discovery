import os
import json
import hashlib
import pandas as pd
import numpy as np
import warnings
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors, Lipinski
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr
from collections import defaultdict

warnings.filterwarnings("ignore")

def compute_features(smiles_list):
    mw, clogp, tpsa, hbd, hba, rotb, csp3 = [], [], [], [], [], [], []
    morgan_fps = []
    
    from rdkit import DataStructs
    
    for smi in smiles_list:
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
        DataStructs.ConvertToNumpyArray(fp, arr)
        morgan_fps.append(arr)
        
    X_desc = np.column_stack([mw, clogp, tpsa, hbd, hba, rotb, csp3])
    X_morg = np.array(morgan_fps)
    return X_desc, X_morg

def main():
    split_file = 'splits/TDC_OFFICIAL_SPLIT.csv'
    df = pd.read_csv(split_file)
    assert len(df) == 1102
    
    df_train = df[df['split'] == 'train'].copy()
    df_valid = df[df['split'] == 'valid'].copy()
    df_test = df[df['split'] == 'test'].copy()
    
    assert len(df_train) == 771
    assert len(df_valid) == 110
    assert len(df_test) == 221
    
    # Extract labels EXACTLY as distributed in TDC
    y_train = df_train['standard_value'].values.astype(float)
    y_valid = df_valid['standard_value'].values.astype(float)
    y_test = df_test['standard_value'].values.astype(float)
    
    # Extract features
    X_desc_tr, X_morg_tr = compute_features(df_train['smiles'])
    X_desc_val, X_morg_val = compute_features(df_valid['smiles'])
    X_desc_ts, X_morg_ts = compute_features(df_test['smiles'])
    
    out_dir = 'results/tdc_benchmark_v1'
    os.makedirs(out_dir, exist_ok=True)
    
    test_preds = {}
    valid_metrics = []
    selected_hps = {}
    test_metrics = {}
    
    # Tie tolerance for selection
    TOL = 1e-12
    
    # ------------------
    # 1. Baseline: Mean
    # ------------------
    mean_val = np.mean(y_train)
    test_preds['mean_baseline'] = np.full(len(y_test), mean_val)
    
    # ------------------
    # 2. Baseline: Median
    # ------------------
    median_val = np.median(y_train)
    test_preds['median_baseline'] = np.full(len(y_test), median_val)
    
    # ------------------
    # ML Models Setup
    # ------------------
    models = {
        'Ridge': {
            'grid': [{'alpha': a} for a in [0.1, 1.0, 10.0]],
            'tie_key': lambda p: p['alpha']
        },
        'RandomForestRegressor': {
            'grid': [{'max_depth': d} for d in [10, None]],
            'tie_key': lambda p: 1 if p['max_depth'] == 10 else 0
        }
    }
    
    reprs = {
        'descriptors': (X_desc_tr, X_desc_val, X_desc_ts, True),
        'Morgan': (X_morg_tr, X_morg_val, X_morg_ts, False)
    }
    
    for model_name, model_info in models.items():
        for rep_name, (X_tr, X_val, X_ts, do_scale) in reprs.items():
            cell_name = f"{model_name}_{rep_name}"
            
            # Preprocessing is fitted on Train only
            if do_scale:
                scaler = StandardScaler()
                X_tr_proc = scaler.fit_transform(X_tr)
                X_val_proc = scaler.transform(X_val)
                X_ts_proc = scaler.transform(X_ts)
            else:
                X_tr_proc, X_val_proc, X_ts_proc = X_tr, X_val, X_ts
                
            best_mae = np.inf
            best_param = None
            
            for params in model_info['grid']:
                if model_name == 'Ridge':
                    m = Ridge(solver="lsqr", tol=1e-4, max_iter=10000, fit_intercept=True, random_state=42, **params)
                else:
                    m = RandomForestRegressor(criterion="squared_error", max_features=1.0, bootstrap=True, min_samples_split=2, min_samples_leaf=1, random_state=42, n_estimators=100, n_jobs=1, **params)
                
                # Fit Train only
                m.fit(X_tr_proc, y_train)
                # Predict Valid
                v_preds = m.predict(X_val_proc)
                v_mae = mean_absolute_error(y_valid, v_preds)
                
                valid_metrics.append({
                    'cell': cell_name,
                    'params': str(params),
                    'valid_mae': float(v_mae)
                })
                
                # Selection Logic
                if v_mae < best_mae - TOL:
                    best_mae = v_mae
                    best_param = params
                elif abs(v_mae - best_mae) <= TOL:
                    if model_info['tie_key'](params) > model_info['tie_key'](best_param):
                        best_mae = v_mae
                        best_param = params
            
            selected_hps[cell_name] = best_param
            
            # Final Fit on Train Only
            if model_name == 'Ridge':
                final_m = Ridge(solver="lsqr", tol=1e-4, max_iter=10000, fit_intercept=True, random_state=42, **best_param)
            else:
                final_m = RandomForestRegressor(criterion="squared_error", max_features=1.0, bootstrap=True, min_samples_split=2, min_samples_leaf=1, random_state=42, n_estimators=100, n_jobs=1, **best_param)
            
            final_m.fit(X_tr_proc, y_train)
            t_preds = final_m.predict(X_ts_proc)
            test_preds[cell_name] = t_preds

    # ------------------
    # Evaluation
    # ------------------
    # We independently compute Spearman using SciPy which exactly matches PyTDC's logic
    test_metrics_list = []
    
    for cell_name, t_preds in test_preds.items():
        # Independent recomputation
        rho, _ = spearmanr(y_test, t_preds)
        mae = mean_absolute_error(y_test, t_preds)
        rmse = np.sqrt(mean_squared_error(y_test, t_preds))
        r2 = r2_score(y_test, t_preds)
        
        # PyTDC evaluator recomputation is equivalent to scipy.stats.spearmanr
        
        test_metrics_list.append({
            'cell': cell_name,
            'spearman': float(rho),
            'mae': float(mae),
            'rmse': float(rmse),
            'r2': float(r2)
        })
        test_metrics[cell_name] = {'spearman': float(rho), 'mae': float(mae), 'rmse': float(rmse), 'r2': float(r2)}
        
    # ------------------
    # Save Results
    # ------------------
    with open(f'{out_dir}/valid_metrics.json', 'w') as f:
        json.dump(valid_metrics, f, indent=2)
        
    with open(f'{out_dir}/selected_hps.json', 'w') as f:
        json.dump(selected_hps, f, indent=2)
        
    with open(f'{out_dir}/test_metrics.json', 'w') as f:
        json.dump(test_metrics_list, f, indent=2)
        
    # Save predictions
    pred_df = df_test[['activity_id', 'smiles', 'standard_value']].copy()
    for cell_name, t_preds in test_preds.items():
        pred_df[cell_name] = t_preds
    pred_df.to_csv(f'{out_dir}/test_predictions.csv', index=False)
    
    # Hashes
    with open(split_file, 'rb') as f:
        split_hash = hashlib.sha256(f.read()).hexdigest()
        
    with open(f'{out_dir}/provenance.json', 'w') as f:
        json.dump({
            'split_file': split_file,
            'split_hash': split_hash,
            'train_n': len(df_train),
            'valid_n': len(df_valid),
            'test_n': len(df_test)
        }, f, indent=2)

if __name__ == '__main__':
    main()
