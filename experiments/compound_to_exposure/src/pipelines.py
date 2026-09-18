from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor

def get_p0a_baseline():
    """Median baseline (MAE optimal)"""
    return DummyRegressor(strategy='median')

def get_p0b_baseline():
    """Mean baseline (RMSE optimal)"""
    return DummyRegressor(strategy='mean')

def get_p1_pipeline():
    """R1 descriptors -> imputer -> scaler -> ridge"""
    return Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('estimator', Ridge(fit_intercept=True))
    ])

def get_p2_pipeline():
    """R2 Morgan -> ridge"""
    return Pipeline([
        ('estimator', Ridge(fit_intercept=True))
    ])

def get_p3_pipeline():
    """R1 descriptors -> imputer -> random forest"""
    return Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('estimator', RandomForestRegressor(n_estimators=500, max_depth=None, random_state=0))
    ])

def get_p4_pipeline():
    """R2 Morgan -> random forest"""
    return Pipeline([
        ('estimator', RandomForestRegressor(n_estimators=500, max_depth=None, random_state=0))
    ])

RIDGE_GRID = {
    'estimator__alpha': [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]
}

RF_GRID = {
    'estimator__max_features': ['sqrt', 0.3, 1.0],
    'estimator__min_samples_leaf': [1, 3, 5]
}

def get_pipeline_grids():
    return {
        'P1': (get_p1_pipeline(), RIDGE_GRID),
        'P2': (get_p2_pipeline(), RIDGE_GRID),
        'P3': (get_p3_pipeline(), RF_GRID),
        'P4': (get_p4_pipeline(), RF_GRID)
    }

def tie_break_candidates(candidate_a, candidate_b):
    """
    Candidate format: dict with keys:
    - 'pipeline_id': str ('P1', 'P2', 'P3', 'P4')
    - 'mae': float
    - 'alpha': float (optional)
    - 'min_samples_leaf': int (optional)
    - 'max_features': str/float (optional)
    
    Returns True if candidate_a is preferred over candidate_b.
    """
    # 1. Lowest MAE
    diff = candidate_b['mae'] - candidate_a['mae']
    if diff > 0.001:
        return True
    elif diff < -0.001:
        return False
        
    # Within 0.001 -> 2. simpler model family (Ridge < Random Forest)
    family_a = 'Ridge' if candidate_a['pipeline_id'] in ['P1', 'P2'] else 'RF'
    family_b = 'Ridge' if candidate_b['pipeline_id'] in ['P1', 'P2'] else 'RF'
    if family_a != family_b:
        return family_a == 'Ridge'
        
    # 3. R1 descriptors > R2 Morgan
    rep_a = 'R1' if candidate_a['pipeline_id'] in ['P1', 'P3'] else 'R2'
    rep_b = 'R1' if candidate_b['pipeline_id'] in ['P1', 'P3'] else 'R2'
    if rep_a != rep_b:
        return rep_a == 'R1'
        
    # 4. More regularised
    if family_a == 'Ridge':
        # larger alpha
        if candidate_a['alpha'] != candidate_b['alpha']:
            return candidate_a['alpha'] > candidate_b['alpha']
    else:
        # larger min_samples_leaf
        if candidate_a['min_samples_leaf'] != candidate_b['min_samples_leaf']:
            return candidate_a['min_samples_leaf'] > candidate_b['min_samples_leaf']
        # smaller max_features
        def mf_val(x):
            return 0.0 if x == 'sqrt' else float(x)
        if candidate_a['max_features'] != candidate_b['max_features']:
            return mf_val(candidate_a['max_features']) < mf_val(candidate_b['max_features'])
            
    # 5. Lowest pipeline ID P1 < P2 < P3 < P4
    return candidate_a['pipeline_id'] < candidate_b['pipeline_id']

