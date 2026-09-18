import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def log10_mae(y_true, y_pred):
    return mean_absolute_error(y_true, y_pred)

def log10_rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))

def spearman_corr(y_true, y_pred):
    if len(y_true) < 2:
        return np.nan
    corr, _ = spearmanr(y_true, y_pred)
    return corr

def r_squared(y_true, y_pred):
    if len(y_true) < 2:
        return np.nan
    return r2_score(y_true, y_pred)

def two_fold_proportion(y_true, y_pred):
    if len(y_true) == 0:
        return np.nan
    diff = np.abs(np.array(y_true) - np.array(y_pred))
    return np.mean(diff <= np.log10(2))

def tail_concordance(p_tail, p_q, tail_type):
    """
    Computes tail concordance.
    p_tail: predictions for the censored group (left or right)
    p_q: predictions for the interior group (Q)
    tail_type: 'lower' or 'upper'
    
    Returns (concordance_score, eligible_pairs)
    """
    if len(p_tail) == 0 or len(p_q) == 0:
        return np.nan, 0
        
    pairs = 0
    score_sum = 0.0
    for pt in p_tail:
        for pq in p_q:
            pairs += 1
            if tail_type == 'lower':
                if pt < pq:
                    score_sum += 1.0
                elif pt == pq:
                    score_sum += 0.5
            elif tail_type == 'upper':
                if pt > pq:
                    score_sum += 1.0
                elif pt == pq:
                    score_sum += 0.5
                    
    return score_sum / pairs, pairs

def boundary_violation_loss(p_tail, bound_val, tail_type):
    if len(p_tail) == 0:
        return np.nan
    p_tail = np.array(p_tail)
    if tail_type == 'lower':
        # bound_val is log10(3)
        loss = np.maximum(0, p_tail - bound_val)
    elif tail_type == 'upper':
        # bound_val is log10(150)
        loss = np.maximum(0, bound_val - p_tail)
    return np.mean(loss)

def paired_scaffold_cluster_bootstrap(scaffold_groups_true, scaffold_groups_pred1, scaffold_groups_pred2, metric_fn, B=10000, seed=0):
    """
    scaffold_groups_true: dict of scaffold_key -> list of true values
    scaffold_groups_pred1: dict of scaffold_key -> list of pred1 values (e.g. median baseline)
    scaffold_groups_pred2: dict of scaffold_key -> list of pred2 values (e.g. selected pipeline)
    
    Returns 95% interval for the difference (metric_fn(pred1) - metric_fn(pred2))
    Wait, the SAP says "Delta = MAE(median baseline) - MAE(selected pipeline)". Positive favours model.
    """
    rng = np.random.RandomState(seed)
    keys = list(scaffold_groups_true.keys())
    n_keys = len(keys)
    
    deltas = []
    for _ in range(B):
        sample_keys = rng.choice(keys, size=n_keys, replace=True)
        y_t = []
        y_p1 = []
        y_p2 = []
        for k in sample_keys:
            y_t.extend(scaffold_groups_true[k])
            y_p1.extend(scaffold_groups_pred1[k])
            y_p2.extend(scaffold_groups_pred2[k])
            
        val1 = metric_fn(y_t, y_p1)
        val2 = metric_fn(y_t, y_p2)
        deltas.append(val1 - val2)
        
    return np.percentile(deltas, [2.5, 97.5])

def single_scaffold_cluster_bootstrap(scaffold_groups_true, scaffold_groups_pred, metric_fn, B=10000, seed=0):
    rng = np.random.RandomState(seed)
    keys = list(scaffold_groups_true.keys())
    n_keys = len(keys)
    
    vals = []
    for _ in range(B):
        sample_keys = rng.choice(keys, size=n_keys, replace=True)
        y_t = []
        y_p = []
        for k in sample_keys:
            y_t.extend(scaffold_groups_true[k])
            y_p.extend(scaffold_groups_pred[k])
        vals.append(metric_fn(y_t, y_p))
        
    return np.percentile(vals, [2.5, 97.5])

def nearest_training_tanimoto(holdout_fps, train_fps):
    """
    Given binary vectors, computes maximum Tanimoto to any compound in the training pool.
    fps are expected to be boolean or 0/1 numpy arrays.
    """
    # Dice distance is related, but let's do exact Tanimoto
    # T(a,b) = (a AND b) / (a OR b)
    max_sims = []
    for h in holdout_fps:
        # intersection over union
        intersection = np.logical_and(h, train_fps).sum(axis=1)
        union = np.logical_or(h, train_fps).sum(axis=1)
        sims = intersection / np.maximum(union, 1) # avoid div by zero
        max_sims.append(np.max(sims))
    return np.array(max_sims)
