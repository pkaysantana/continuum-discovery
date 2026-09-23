"""v3A.1-RC bootstrap-aware QRF weight recovery and uncertainty primitives.

Implements SAP §10: for each tree t, the weight of training observation i
for query x is:

    w_it(x) = m_it * I(i shares leaf with x) / sum_j[m_jt * I(j shares leaf with x)]

where m_it is the bootstrap multiplicity of observation i in tree t.

The ensemble weight is:

    w_i(x) = mean_t w_it(x)

A naive shared-leaf indicator ignoring bootstrap multiplicity is prohibited.
"""
import hashlib
from math import ceil

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble._forest import _generate_sample_indices, _get_n_samples_bootstrap
from sklearn.preprocessing import StandardScaler
from rdkit import Chem
from rdkit.Chem import Descriptors

from src import v3a_config as C


# --------------------------------------------------------------------------- QRF weights
class QRFWeightRecoveryError(RuntimeError):
    """Raised when exact bootstrap-aware RF weight recovery cannot be guaranteed."""


def _bootstrap_multiplicities(tree_estimator, n_train: int,
                              n_samples_bootstrap: int) -> np.ndarray:
    """Reconstruct the exact in-bag multiplicity used by scikit-learn.

    The private helpers are deliberately used because they are the implementation
    that created the fitted tree. The locked scikit-learn version is recorded in
    the freeze manifest. Reimplementing this with an approximately equivalent RNG
    call risks silent drift when ``max_samples`` or sklearn internals change.
    """
    sample_indices = _generate_sample_indices(
        tree_estimator.random_state, n_train, n_samples_bootstrap, None
    )
    counts = np.bincount(sample_indices, minlength=n_train)
    return counts


def _validate_sklearn_private_helpers(n_train: int) -> None:
    """Prove the installed sklearn private helper contract used by this module."""
    try:
        n_bootstrap = _get_n_samples_bootstrap(n_train, None, None)
        probe = _generate_sample_indices(0, n_train, n_bootstrap, None)
    except (TypeError, ValueError, AttributeError) as exc:
        raise QRFWeightRecoveryError(
            "QRF_WEIGHT_RECOVERY_FAILED: incompatible scikit-learn forest helpers"
        ) from exc
    if n_bootstrap != n_train or np.asarray(probe).shape != (n_train,):
        raise QRFWeightRecoveryError(
            "QRF_WEIGHT_RECOVERY_FAILED: incompatible scikit-learn bootstrap semantics"
        )


def _validate_frozen_forest(rf: RandomForestRegressor,
                            sample_weight_used: bool | None) -> None:
    """Reject any fitted forest outside the explicitly supported frozen mode."""
    if not isinstance(rf, RandomForestRegressor) or not hasattr(rf, "estimators_"):
        raise QRFWeightRecoveryError(
            "QRF_WEIGHT_RECOVERY_FAILED: fitted RandomForestRegressor required"
        )
    if not rf.bootstrap:
        raise QRFWeightRecoveryError(
            "QRF_WEIGHT_RECOVERY_FAILED: bootstrap=True is required"
        )
    if rf.max_samples is not None:
        raise QRFWeightRecoveryError(
            "QRF_WEIGHT_RECOVERY_FAILED: max_samples=None is required"
        )
    if sample_weight_used is not False:
        raise QRFWeightRecoveryError(
            "QRF_WEIGHT_RECOVERY_FAILED: explicit unweighted-fit attestation required; "
            "sample_weight fitting is unsupported"
        )

    expected = dict(C.FROZEN_RF_PARAMS)
    for parameter, value in expected.items():
        if getattr(rf, parameter, object()) != value:
            raise QRFWeightRecoveryError(
                f"QRF_WEIGHT_RECOVERY_FAILED: non-frozen RF parameter {parameter}"
            )
    if len(rf.estimators_) != expected["n_estimators"]:
        raise QRFWeightRecoveryError(
            "QRF_WEIGHT_RECOVERY_FAILED: fitted estimator count differs from frozen factory"
        )
    if not hasattr(rf, "n_features_in_"):
        raise QRFWeightRecoveryError(
            "QRF_WEIGHT_RECOVERY_FAILED: fitted forest metadata missing"
        )
    for tree in rf.estimators_:
        if (getattr(tree, "random_state", None) is None
                or not hasattr(tree, "tree_")
                or not hasattr(tree, "n_features_in_")):
            raise QRFWeightRecoveryError(
                "QRF_WEIGHT_RECOVERY_FAILED: fitted per-tree metadata missing"
            )


def recover_weights_single_tree(tree, X_train: np.ndarray, x_query: np.ndarray,
                                 n_train: int, bootstrap_counts: np.ndarray) -> np.ndarray:
    """Per-tree weight vector w_t(x) of shape (n_train,).

    bootstrap_counts[i] = m_it = how many times observation i was drawn in tree t's bootstrap.
    """
    # Terminal leaf for query
    query_leaf = tree.apply(x_query.reshape(1, -1))[0]
    # Terminal leaves for all training rows
    train_leaves = tree.apply(X_train)
    # Indicator: which training rows share the query's leaf
    in_leaf = (train_leaves == query_leaf)
    # Weighted indicator: m_it * I(same leaf)
    weighted = bootstrap_counts.astype(np.float64) * in_leaf
    denom = weighted.sum()
    if denom == 0.0:
        raise QRFWeightRecoveryError(
            "QRF_WEIGHT_RECOVERY_FAILED: query leaf has no in-bag observations"
        )
    return weighted / denom


def recover_forest_weights(rf: RandomForestRegressor, X_train: np.ndarray,
                            x_query: np.ndarray,
                            *, sample_weight_used: bool | None = None) -> np.ndarray:
    """Ensemble weight vector w(x) of shape (n_train,), averaged across all trees.

    Each tree's contribution accounts for bootstrap multiplicity.
    """
    _validate_frozen_forest(rf, sample_weight_used)
    X_train = np.asarray(X_train)
    x_query = np.asarray(x_query)
    if X_train.ndim != 2 or x_query.size != X_train.shape[1]:
        raise QRFWeightRecoveryError(
            "QRF_WEIGHT_RECOVERY_FAILED: training/query feature dimensions differ"
        )
    x_query = x_query.reshape(-1)
    n_train = X_train.shape[0]
    n_trees = len(rf.estimators_)
    if n_train == 0 or n_trees == 0:
        raise QRFWeightRecoveryError(
            "QRF_WEIGHT_RECOVERY_FAILED: empty training set or forest"
        )
    _validate_sklearn_private_helpers(n_train)
    n_samples_bootstrap = _get_n_samples_bootstrap(n_train, rf.max_samples, None)
    weight_sum = np.zeros(n_train, dtype=np.float64)

    for tree in rf.estimators_:
        bootstrap_counts = _bootstrap_multiplicities(
            tree, n_train, n_samples_bootstrap
        )
        w_t = recover_weights_single_tree(tree, X_train, x_query, n_train, bootstrap_counts)
        weight_sum += w_t

    weights = weight_sum / n_trees
    if not np.isfinite(weights).all() or (weights < 0.0).any():
        raise QRFWeightRecoveryError(
            "QRF_WEIGHT_RECOVERY_FAILED: invalid recovered weights"
        )
    if abs(float(weights.sum()) - 1.0) >= C.WEIGHT_SUM_TOL:
        raise QRFWeightRecoveryError(
            "QRF_WEIGHT_RECOVERY_FAILED: recovered weights do not sum to one"
        )
    return weights


def recover_forest_weights_many(rf: RandomForestRegressor, X_train: np.ndarray,
                                X_query: np.ndarray,
                                *, sample_weight_used: bool | None = None) -> np.ndarray:
    """Recover one exact training-observation weight vector per query row."""
    X_query = np.asarray(X_query)
    if X_query.ndim != 2:
        raise QRFWeightRecoveryError(
            "QRF_WEIGHT_RECOVERY_FAILED: X_query must be two-dimensional"
        )
    return np.vstack([
        recover_forest_weights(
            rf, X_train, row, sample_weight_used=sample_weight_used
        )
        for row in X_query
    ])


# --------------------------------------------------------------------------- Weighted quantiles
def weighted_quantile(values: np.ndarray, weights: np.ndarray, quantile: float) -> float:
    """Deterministic weighted empirical quantile.

    Sorting: ascending by value.
    Cumulative-weight convention: interpolation-free step function.
        - Sort values, compute cumulative normalised weights.
        - q-th quantile = value at the first index where cumW >= q.
    Boundary: q=0 returns min, q=1 returns max.
    Ties in value: stable sort preserves original order.
    """
    values = np.asarray(values, dtype=np.float64).reshape(-1)
    weights = np.asarray(weights, dtype=np.float64).reshape(-1)
    if values.size == 0 or values.shape != weights.shape:
        raise ValueError("values and weights must be nonempty one-dimensional arrays of equal length")
    if not np.isfinite(values).all() or not np.isfinite(weights).all():
        raise ValueError("values and weights must be finite")
    if (weights < 0.0).any() or weights.sum() <= 0.0:
        raise ValueError("weights must be nonnegative with positive total weight")
    if not np.isfinite(quantile) or not 0.0 <= quantile <= 1.0:
        raise ValueError("quantile must lie in [0, 1]")

    if quantile == 0.0:
        mask = weights > 0
        return float(values[mask].min())
    if quantile == 1.0:
        mask = weights > 0
        return float(values[mask].max())

    order = np.argsort(values, kind="mergesort")
    sorted_vals = values[order]
    sorted_wts = weights[order]

    # Normalise
    total = sorted_wts.sum()
    cum_w = np.cumsum(sorted_wts) / total

    # First index where cumulative weight >= quantile
    idx = np.searchsorted(cum_w, quantile, side="left")
    idx = min(idx, len(sorted_vals) - 1)
    return float(sorted_vals[idx])


def qrf_prediction_quantiles(weights: np.ndarray, y_train: np.ndarray,
                              quantiles=(0.10, 0.25, 0.50, 0.75, 0.90)) -> dict:
    """Compute multiple weighted quantiles from QRF weights."""
    result = {}
    for q in quantiles:
        result[f"Q{int(q*100):02d}"] = weighted_quantile(y_train, weights, q)
    return result


# --------------------------------------------------------------------------- Uncertainty primitives
def qrf_width(weights: np.ndarray, y_train: np.ndarray,
              low_q: float = C.QRF_LOW_Q, high_q: float = C.QRF_HIGH_Q) -> float:
    """Primary uncertainty: Q90 - Q10."""
    q_low = weighted_quantile(y_train, weights, low_q)
    q_high = weighted_quantile(y_train, weights, high_q)
    return q_high - q_low


def tanimoto_unfamiliarity(query_fp: np.ndarray, train_fps: np.ndarray) -> float:
    """Comparator A: 1 - max Tanimoto(query, training)."""
    query_fp = np.asarray(query_fp)
    train_fps = np.asarray(train_fps)
    if query_fp.ndim != 1 or train_fps.ndim != 2 or train_fps.shape[0] == 0:
        raise ValueError("query_fp must be 1D and train_fps must be a nonempty 2D matrix")
    if train_fps.shape[1] != query_fp.shape[0]:
        raise ValueError("query and training fingerprints must have the same width")
    # Binary fingerprints: Tanimoto = intersection / union
    query = query_fp.astype(bool)
    train = train_fps.astype(bool)
    intersection = np.logical_and(query, train).sum(axis=1)
    union = np.logical_or(query, train).sum(axis=1)
    # Avoid division by zero
    tanimotos = np.where(union > 0, intersection / union, 0.0)
    return 1.0 - float(tanimotos.max())


def physchem_knn_distance(query_descriptors: np.ndarray, train_descriptors_scaled: np.ndarray,
                           scaler_mean: np.ndarray, scaler_scale: np.ndarray,
                           k: int = C.PHYSCHEM_KNN) -> float:
    """Comparator B: mean Euclidean distance to k nearest training compounds
    after StandardScaler fitted on training descriptors only."""
    query_descriptors = np.asarray(query_descriptors, dtype=np.float64)
    train_descriptors_scaled = np.asarray(train_descriptors_scaled, dtype=np.float64)
    scaler_mean = np.asarray(scaler_mean, dtype=np.float64)
    scaler_scale = np.asarray(scaler_scale, dtype=np.float64)
    if train_descriptors_scaled.ndim != 2 or train_descriptors_scaled.shape[0] == 0:
        raise ValueError("training descriptor matrix must be nonempty and two-dimensional")
    if query_descriptors.shape != scaler_mean.shape or scaler_mean.shape != scaler_scale.shape:
        raise ValueError("query, scaler mean, and scaler scale must have matching shapes")
    if train_descriptors_scaled.shape[1] != query_descriptors.size:
        raise ValueError("query and training descriptor dimensions differ")
    if k < 1 or k > train_descriptors_scaled.shape[0]:
        raise ValueError("k must be between 1 and the number of training rows")
    if (scaler_scale <= 0.0).any():
        raise ValueError("scaler scales must be positive")
    query_scaled = (query_descriptors - scaler_mean) / scaler_scale
    dists = np.sqrt(((train_descriptors_scaled - query_scaled) ** 2).sum(axis=1))
    knn_dists = np.sort(dists)[:k]
    return float(knn_dists.mean())


def fit_physchem_space(train_descriptors: np.ndarray):
    """Fit the required StandardScaler on outer-training descriptors only.

    Returns the fitted scaler and its transformed training matrix. Test-fold
    descriptors are intentionally not accepted by this fitting helper.
    """
    train_descriptors = np.asarray(train_descriptors, dtype=np.float64)
    if train_descriptors.ndim != 2 or train_descriptors.shape[0] < C.PHYSCHEM_KNN:
        raise ValueError("outer-training descriptor matrix is too small")
    scaler = StandardScaler().fit(train_descriptors)
    return scaler, scaler.transform(train_descriptors)


def neff_inverse(weights: np.ndarray) -> float:
    """Comparator C: 1 / N_eff where N_eff = 1 / sum(w_i^2)."""
    w2 = (weights ** 2).sum()
    if w2 <= 0.0:
        raise ValueError("weights must have nonempty support")
    n_eff = 1.0 / w2
    return 1.0 / n_eff


def neff(weights: np.ndarray) -> float:
    """Effective sample size = 1 / sum(w_i^2)."""
    w2 = (weights ** 2).sum()
    if w2 <= 0.0:
        raise ValueError("weights must have nonempty support")
    return 1.0 / w2


def local_label_sd(weights: np.ndarray, y_train: np.ndarray) -> float:
    """Comparator D: weighted SD of training outcomes."""
    w_mean = np.dot(weights, y_train)
    w_var = np.dot(weights, (y_train - w_mean) ** 2)
    return float(np.sqrt(max(w_var, 0.0)))


def tree_dispersion(rf: RandomForestRegressor, x_query: np.ndarray) -> float:
    """Comparator E: SD of individual-tree point predictions."""
    preds = np.array([t.predict(x_query.reshape(1, -1))[0] for t in rf.estimators_])
    return float(preds.std(ddof=0))


# --------------------------------------------------------------------------- Descriptor panel
DESCRIPTOR_FUNCS = {
    "MolWt": Descriptors.MolWt,
    "MolLogP": Descriptors.MolLogP,
    "MolMR": Descriptors.MolMR,
    "TPSA": Descriptors.TPSA,
    "NumHDonors": Descriptors.NumHDonors,
    "NumHAcceptors": Descriptors.NumHAcceptors,
    "NumRotatableBonds": Descriptors.NumRotatableBonds,
    "RingCount": Descriptors.RingCount,
    "NumAromaticRings": Descriptors.NumAromaticRings,
    "NumAliphaticRings": Descriptors.NumAliphaticRings,
    "FractionCSP3": Descriptors.FractionCSP3,
    "HeavyAtomCount": Descriptors.HeavyAtomCount,
}


def compute_descriptors(smiles: str) -> np.ndarray:
    """Compute the frozen 12-descriptor panel for a single molecule."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Cannot parse SMILES: {smiles!r}")
    return np.array([float(DESCRIPTOR_FUNCS[name](mol)) for name in C.DESCRIPTOR_PANEL])


def compute_descriptor_matrix(smiles_list) -> np.ndarray:
    """Compute the 12-descriptor matrix for a list of SMILES."""
    return np.vstack([compute_descriptors(s) for s in smiles_list])


# --------------------------------------------------------------------------- Within-fold retention
def select_retained(ids, uncertainty: np.ndarray, coverage: float,
                    salt: str = C.RETENTION_TIE_SUFFIX) -> set:
    """Select the k = ceil(coverage * n) compounds with lowest uncertainty.

    Ties broken deterministically by SHA-256(str(activity_id) + salt).
    Returns set of retained activity_ids.
    """
    ids = list(ids)
    uncertainty = np.asarray(uncertainty, dtype=np.float64).reshape(-1)
    n = len(ids)
    if n == 0 or len(set(ids)) != n or uncertainty.size != n:
        raise ValueError("ids must be nonempty and unique and align one-to-one with uncertainty")
    if not np.isfinite(uncertainty).all() or not 0.0 < coverage <= 1.0:
        raise ValueError("uncertainties must be finite and coverage must lie in (0, 1]")
    k = ceil(coverage * n)
    k = min(k, n)

    # Build (uncertainty, tiebreak_hash, id) tuples
    ranked = []
    for uid, u in zip(ids, uncertainty):
        tb = hashlib.sha256((str(uid) + salt).encode("utf-8")).hexdigest()
        ranked.append((u, tb, uid))
    ranked.sort()
    return set(item[2] for item in ranked[:k])


def within_fold_retention_mask(activity_ids, outer_folds, uncertainty: np.ndarray,
                               coverage: float) -> np.ndarray:
    """Return a pooled mask after independent deterministic ranking within each fold."""
    activity_ids = np.asarray(activity_ids)
    outer_folds = np.asarray(outer_folds)
    uncertainty = np.asarray(uncertainty, dtype=np.float64)
    if not (activity_ids.ndim == outer_folds.ndim == uncertainty.ndim == 1):
        raise ValueError("activity_ids, outer_folds, and uncertainty must be one-dimensional")
    if not (len(activity_ids) == len(outer_folds) == len(uncertainty)):
        raise ValueError("activity_ids, outer_folds, and uncertainty must align")
    retained = np.zeros(len(activity_ids), dtype=bool)
    for fold in sorted(np.unique(outer_folds)):
        positions = np.flatnonzero(outer_folds == fold)
        keep_ids = select_retained(activity_ids[positions], uncertainty[positions], coverage)
        retained[positions] = np.isin(activity_ids[positions], list(keep_ids))
    return retained


# --------------------------------------------------------------------------- Metric primitives
def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true, y_pred = _metric_arrays(y_true, y_pred)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true, y_pred = _metric_arrays(y_true, y_pred)
    return float(np.mean(np.abs(y_true - y_pred)))


def _metric_arrays(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=np.float64).reshape(-1)
    y_pred = np.asarray(y_pred, dtype=np.float64).reshape(-1)
    if y_true.size == 0 or y_true.shape != y_pred.shape:
        raise ValueError("metric inputs must be nonempty and aligned")
    if not np.isfinite(y_true).all() or not np.isfinite(y_pred).all():
        raise ValueError("metric inputs must be finite")
    return y_true, y_pred


def rel_benefit_80(rmse_random80: float, rmse_qrf80: float) -> float:
    """REL_BENEFIT_80 = (RMSE_RANDOM80 - RMSE_QRF80) / RMSE_RANDOM80."""
    if not np.isfinite(rmse_random80) or not np.isfinite(rmse_qrf80) or rmse_random80 <= 0.0:
        raise ValueError("RMSE inputs must be finite and random-baseline RMSE must be positive")
    return (rmse_random80 - rmse_qrf80) / rmse_random80


def trapezoidal_naurc(coverage_levels: np.ndarray, rmse_values: np.ndarray,
                      kappa_min: float = 0.50, kappa_max: float = 1.00) -> float:
    """Normalised AURC via trapezoidal rule over [kappa_min, kappa_max].

    nAURC = (1 / (kappa_max - kappa_min)) * integral RMSE(kappa) dkappa
    """
    coverage_levels = np.asarray(coverage_levels, dtype=np.float64)
    rmse_values = np.asarray(rmse_values, dtype=np.float64)
    if coverage_levels.ndim != 1 or coverage_levels.shape != rmse_values.shape:
        raise ValueError("coverage and RMSE arrays must be aligned and one-dimensional")
    if not np.isfinite(coverage_levels).all() or not np.isfinite(rmse_values).all():
        raise ValueError("coverage and RMSE arrays must be finite")
    mask = (coverage_levels >= kappa_min) & (coverage_levels <= kappa_max)
    kappas = coverage_levels[mask]
    rmses = rmse_values[mask]
    order = np.argsort(kappas)
    kappas = kappas[order]
    rmses = rmses[order]
    if len(kappas) < 2:
        return float("nan")
    integral = np.trapezoid(rmses, kappas)
    return float(integral / (kappa_max - kappa_min))


# --------------------------------------------------------------------------- Random deferral engine
def matched_random_rankings(n_per_fold: dict, n_random: int = C.N_RANDOM_DEFERRALS,
                            seed: int = C.MASTER_SEED,
                            coverage: float = C.PRIMARY_COVERAGE) -> dict:
    """Generate n_random matched random within-fold retention sets.

    Parameters
    ----------
    n_per_fold : dict mapping fold_id -> list of activity_ids in that fold
    n_random : number of random rankings to generate
    coverage : fraction to retain in each fold
    seed : master RNG seed

    Returns
    -------
    dict mapping fold_id -> list of n_random sets of retained activity_ids
    """
    if n_random < 1 or not 0.0 < coverage <= 1.0 or not n_per_fold:
        raise ValueError("nonempty folds, positive n_random, and coverage in (0, 1] are required")
    rng = np.random.RandomState(seed)
    result = {}
    for fold_id in sorted(n_per_fold.keys()):
        ids = np.array(n_per_fold[fold_id])
        n = len(ids)
        if n == 0 or len(set(ids.tolist())) != n:
            raise ValueError("each fold must contain unique activity IDs")
        k = ceil(coverage * n)
        k = min(k, n)
        fold_samples = []
        for _ in range(n_random):
            perm = rng.permutation(n)
            retained = set(ids[perm[:k]])
            fold_samples.append(retained)
        result[fold_id] = fold_samples
    return result


def matched_random_retention_rmse(activity_ids, outer_folds, y_true, y_pred,
                                  n_random: int = C.N_RANDOM_DEFERRALS,
                                  seed: int = C.MASTER_SEED,
                                  coverage: float = C.PRIMARY_COVERAGE) -> dict:
    """Compute matched within-fold random-retention RMSE draws and Monte Carlo SE.

    This is an outcome-accepting execution utility. Preflight tests call it only on
    synthetic arrays; the preflight artifact generator never imports or calls it.
    """
    activity_ids = np.asarray(activity_ids)
    outer_folds = np.asarray(outer_folds)
    y_true, y_pred = _metric_arrays(y_true, y_pred)
    if not (activity_ids.ndim == outer_folds.ndim == 1):
        raise ValueError("activity IDs and folds must be one-dimensional")
    if not (len(activity_ids) == len(outer_folds) == len(y_true)):
        raise ValueError("random-retention inputs must align")
    fold_ids = {
        fold: activity_ids[outer_folds == fold].tolist()
        for fold in sorted(np.unique(outer_folds))
    }
    samples = matched_random_rankings(
        fold_ids, n_random=n_random, seed=seed, coverage=coverage
    )
    position_by_id = {activity_id: pos for pos, activity_id in enumerate(activity_ids)}
    if len(position_by_id) != len(activity_ids):
        raise ValueError("activity IDs must be unique")
    draws = np.empty(n_random, dtype=np.float64)
    for draw in range(n_random):
        positions = [
            position_by_id[activity_id]
            for fold in sorted(samples)
            for activity_id in samples[fold][draw]
        ]
        draws[draw] = rmse(y_true[positions], y_pred[positions])
    mcse = 0.0 if n_random == 1 else float(draws.std(ddof=1) / np.sqrt(n_random))
    return {
        "mean_rmse": float(draws.mean()),
        "monte_carlo_se": mcse,
        "rmse_draws": draws,
    }


# --------------------------------------------------------------------------- Scaffold bootstrap engine
def scaffold_bootstrap_indices(folds_df, n_bootstrap: int = C.N_BOOTSTRAP,
                                seed: int = C.MASTER_SEED) -> list:
    """Generate scaffold-group bootstrap resamples stratified by outer fold.

    Returns list of n_bootstrap index arrays (into the original folds_df rows).
    Bootstrap unit = scaffold group. Fold strata remain separated.
    All compared methods receive identical bootstrap draws.
    """
    required = {"scaffold_key", "outer_fold"}
    if not required.issubset(folds_df.columns) or len(folds_df) == 0 or n_bootstrap < 1:
        raise ValueError("nonempty folds data and positive n_bootstrap are required")
    rng = np.random.RandomState(seed)
    positional = folds_df.reset_index(drop=True)
    # Pre-compute scaffold groups per fold
    fold_groups = {}
    for fold_id in sorted(positional["outer_fold"].unique()):
        fold_mask = positional["outer_fold"] == fold_id
        fold_data = positional[fold_mask]
        groups = fold_data.groupby("scaffold_key").groups
        # Each group: scaffold_key -> list of positional indices
        scaffold_keys = sorted(groups.keys())
        fold_groups[fold_id] = {
            "keys": scaffold_keys,
            "index_lists": [groups[k].tolist() for k in scaffold_keys],
        }

    resamples = []
    for _ in range(n_bootstrap):
        all_indices = []
        for fold_id in sorted(fold_groups.keys()):
            fg = fold_groups[fold_id]
            n_groups = len(fg["keys"])
            chosen = rng.randint(0, n_groups, n_groups)
            for g_idx in chosen:
                all_indices.extend(fg["index_lists"][g_idx])
        resamples.append(np.asarray(all_indices, dtype=np.int64))
    return resamples


# --------------------------------------------------------------------------- Conformal split
def conformal_proper_train_cal_split(folds_df, outer_fold: int,
                                      cal_fraction: float = 0.20,
                                      salt: str = C.CQR_SPLIT_SALT_SUFFIX):
    """Deterministic scaffold-group split of outer-training into proper-train and calibration.

    Groups are indivisible. Split uses group sizes only, never outcomes.
    Deterministic SHA-256 tie-breaking with the CQR salt.
    Approximately cal_fraction of compounds go to calibration.

    Returns (proper_train_ids, calibration_ids) as sets of activity_ids.
    """
    if not np.isfinite(cal_fraction) or not 0.0 < cal_fraction < 1.0:
        raise ValueError("cal_fraction must be finite and lie strictly between 0 and 1")

    # Outer training = everything NOT in outer_fold
    train_mask = folds_df["outer_fold"] != outer_fold
    train_data = folds_df[train_mask].copy()

    # Group by scaffold
    groups = train_data.groupby("scaffold_key")["activity_id"].apply(list).to_dict()
    scaffold_keys = sorted(
        groups,
        key=lambda key: hashlib.sha256((key + salt).encode("utf-8")).hexdigest(),
    )

    n_total = len(train_data)
    target_cal = ceil(cal_fraction * n_total)

    cal_ids = set()
    proper_ids = set()
    cal_count = 0

    for k in scaffold_keys:
        ids = groups[k]
        if cal_count < target_cal:
            cal_ids.update(ids)
            cal_count += len(ids)
        else:
            proper_ids.update(ids)

    return proper_ids, cal_ids


def cqr_nonconformity_scores(y_calibration: np.ndarray, lower_quantiles: np.ndarray,
                             upper_quantiles: np.ndarray) -> np.ndarray:
    """CQR calibration scores: max(lower - y, y - upper), calibration rows only."""
    y_calibration, lower_quantiles = _metric_arrays(y_calibration, lower_quantiles)
    _, upper_quantiles = _metric_arrays(y_calibration, upper_quantiles)
    if (lower_quantiles > upper_quantiles).any():
        raise ValueError("lower quantiles must not exceed upper quantiles")
    return np.maximum(lower_quantiles - y_calibration, y_calibration - upper_quantiles)


def conformal_correction(scores: np.ndarray, alpha: float) -> float:
    """Return a finite, nonnegative conservative split-conformal correction."""
    scores = np.asarray(scores, dtype=np.float64).reshape(-1)
    if scores.size == 0 or not np.isfinite(scores).all() or not 0.0 < alpha < 1.0:
        raise ValueError("finite nonempty scores and alpha in (0, 1) are required")
    level = min(1.0, ceil((scores.size + 1) * (1.0 - alpha)) / scores.size)
    return max(0.0, float(np.quantile(scores, level, method="higher")))


def apply_conformal_correction(lower_quantiles: np.ndarray, upper_quantiles: np.ndarray,
                               correction: float):
    """Apply a fold-constant CQR correction without changing within-fold ranking."""
    lower_quantiles = np.asarray(lower_quantiles, dtype=np.float64)
    upper_quantiles = np.asarray(upper_quantiles, dtype=np.float64)
    if lower_quantiles.shape != upper_quantiles.shape or lower_quantiles.ndim != 1:
        raise ValueError("lower and upper quantiles must be aligned one-dimensional arrays")
    if not np.isfinite(correction) or correction < 0.0:
        raise ValueError("conformal correction must be finite and nonnegative")
    calibrated_lower = lower_quantiles - correction
    calibrated_upper = upper_quantiles + correction
    if (calibrated_lower > calibrated_upper).any():
        raise ValueError("conformal correction produces inverted intervals")
    return calibrated_lower, calibrated_upper


def interval_calibration_summary(y_true: np.ndarray, lower: np.ndarray,
                                 upper: np.ndarray) -> dict:
    """Return empirical marginal coverage and mean/median interval width."""
    y_true, lower = _metric_arrays(y_true, lower)
    _, upper = _metric_arrays(y_true, upper)
    if (lower > upper).any():
        raise ValueError("lower interval bounds must not exceed upper bounds")
    widths = upper - lower
    return {
        "empirical_marginal_coverage": float(np.mean((y_true >= lower) & (y_true <= upper))),
        "mean_interval_width": float(np.mean(widths)),
        "median_interval_width": float(np.median(widths)),
    }


# --------------------------------------------------------------------------- Execution guard
class ExecutionGuardError(RuntimeError):
    """Raised when scientific execution is attempted without proper state."""


def check_execution_guard(manifest: dict, require_flag: bool = False,
                          *, project_root=None):
    """Fail-closed guard: scientific execution requires explicit flag and frozen state.

    Parameters
    ----------
    manifest : the pre-execution manifest dict
    require_flag : whether the --execute-scientific-analysis flag was provided
    project_root : canonical project root containing all frozen artifacts

    Raises ExecutionGuardError if any condition is not met.
    """
    state = manifest.get("execution_state", "")

    if state != C.STATE_FROZEN:
        raise ExecutionGuardError(
            f"Execution blocked: state is '{state}', required '{C.STATE_FROZEN}'")

    if require_flag is not True:
        raise ExecutionGuardError(
            "Execution blocked: --execute-scientific-analysis flag not provided")

    required_checks = [
        ("sap_sha256", "SAP hash missing"),
        ("cohort_sha256", "Cohort hash missing"),
        ("split_sha256", "Split hash missing"),
        ("feature_sha256", "Feature hash missing"),
    ]
    for key, msg in required_checks:
        if not manifest.get(key):
            raise ExecutionGuardError(f"Execution blocked: {msg}")

    if manifest.get("cohort_N") != C.COHORT_N:
        raise ExecutionGuardError(
            f"Execution blocked: cohort_N={manifest.get('cohort_N')}, expected {C.COHORT_N}")

    if not manifest.get("independent_audit_recorded"):
        raise ExecutionGuardError("Execution blocked: independent implementation audit not recorded")

    if manifest.get("representation") != C.REPRESENTATION.value:
        raise ExecutionGuardError("Execution blocked: frozen representation mismatch")

    if manifest.get("production_model_fit_to_real_outcomes") is not False:
        raise ExecutionGuardError("Execution blocked: invalid pre-fit production-model status")

    if project_root is None:
        raise ExecutionGuardError(
            "Execution blocked: canonical project root required for artifact verification"
        )
    try:
        # Local import avoids coupling mechanical preflight generation to the
        # outcome-accepting execution utility module at import time.
        from src.v3a_preflight import verify_persisted_artifacts
        verify_persisted_artifacts(project_root, manifest, expected_state=None)
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        raise ExecutionGuardError(
            f"Execution blocked: frozen artifact verification failed: {exc}"
        ) from exc
