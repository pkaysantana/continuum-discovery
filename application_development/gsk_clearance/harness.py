"""Exploratory, in-memory scaffold CV. No CLI, data discovery, or file writes.

Dependencies are imported only when this module is explicitly imported. Importing
the historical representation helpers does not import either scientific runner.
"""
from dataclasses import asdict, dataclass
import hashlib
import importlib.metadata
import json
import platform
import re

import numpy as np
from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold
from scipy.stats import pearsonr, spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import VarianceThreshold
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from experiments.compound_to_exposure.src.representations import (
    R1_PROPERTIES, get_r1_vector, get_r2_morgan,
)

REPRESENTATIONS = {
    "descriptor_ridge": "R1", "morgan_ridge": "R2",
    "descriptor_rf": "R1", "morgan_rf": "R2",
}
TARGET = "log10(CLint expressed in uL/min/mg)"
RECORD_FIELDS = {"id", "smiles", "scaffold", "fold", "partition", "relation", "clint"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class Configuration:
    seed: int = 20261013
    ridge_alpha: float = 1.0
    trees: int = 100
    max_features: str | float = "sqrt"
    min_samples_leaf: int = 3
    max_depth: int | None = None

    def validate(self):
        if type(self.seed) is not int or not 0 <= self.seed < 2**32:
            raise ValueError("invalid seed")
        if not np.isfinite(self.ridge_alpha) or self.ridge_alpha <= 0:
            raise ValueError("ridge alpha must be positive")
        if type(self.trees) is not int or not 1 <= self.trees <= 100:
            raise ValueError("development budget permits 1..100 trees")
        if type(self.min_samples_leaf) is not int or self.min_samples_leaf < 1:
            raise ValueError("invalid leaf size")
        if self.max_depth is not None and (type(self.max_depth) is not int or self.max_depth < 1):
            raise ValueError("invalid depth")
        if not (self.max_features == "sqrt" or
                type(self.max_features) is float and 0 < self.max_features <= 1):
            raise ValueError("max_features must be sqrt or a fraction")


def scaffold_key(smiles):
    """V2 grouping policy, with explicit failure instead of fallback on errors.

    Only grouping selects the largest fragment; features retain all fragments.
    No tautomer, charge, stereochemistry, or parent-structure normalisation.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("invalid SMILES")
    fragments = Chem.GetMolFrags(mol, asMols=True)
    mol = sorted(fragments, key=lambda m: (-m.GetNumHeavyAtoms(),
                 Chem.MolToSmiles(m, canonical=True)))[0]
    return MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False) or "__ACYCLIC__"


def transform_target(clint):
    values = np.asarray(clint, dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("CLint must be a finite positive vector in uL/min/mg")
    return np.log10(values)


def validate_bundle(records, provenance, *, approve_development=False):
    required = {"kind", "source_commit", "source_sha256", "partition_sha256",
                "records_sha256", "assignments", "target", "representation_policy"}
    if set(provenance) != required:
        raise ValueError("missing or unexpected provenance fields")
    if provenance["kind"] not in {"synthetic", "development"}:
        raise ValueError("unknown data provenance kind")
    if provenance["kind"] == "development" and approve_development is not True:
        raise PermissionError("real development execution needs separate explicit approval")
    if not re.fullmatch(r"[0-9a-f]{40}", provenance["source_commit"]):
        raise ValueError("source commit is required")
    for field in ("source_sha256", "partition_sha256", "records_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", provenance[field]):
            raise ValueError("invalid provenance hash")
    if provenance["target"] != TARGET or provenance["representation_policy"] != "V2_R1_12_R2_2048_NOCHIRAL":
        raise ValueError("target or representation policy mismatch")
    if not records or digest(records) != provenance["records_sha256"]:
        raise ValueError("input records do not match provenance")
    assignments = provenance["assignments"]
    if not isinstance(assignments, dict) or len(assignments) != len(records):
        raise ValueError("incomplete frozen assignments")
    ids, identities, group_folds = set(), set(), {}
    for row in records:
        if set(row) != RECORD_FIELDS:
            raise ValueError("unexpected record schema")
        if not isinstance(row["id"], str) or not row["id"] or row["id"] in ids:
            raise ValueError("duplicate or invalid ID")
        ids.add(row["id"])
        if provenance["kind"] == "synthetic" and not row["id"].startswith("SYN_"):
            raise ValueError("synthetic fixtures must use SYN_ IDs")
        if row["partition"] != "cv" or row["relation"] not in (None, ""):
            raise ValueError("only uncensored development CV records are eligible")
        if type(row["fold"]) is not int or row["fold"] < 0:
            raise ValueError("invalid frozen fold")
        if not np.isfinite(row["clint"]) or not 3 < row["clint"] < 150:
            raise ValueError("strict-interior development cohort required")
        key = scaffold_key(row["smiles"])
        identity = Chem.MolToSmiles(Chem.MolFromSmiles(row["smiles"]), isomericSmiles=True)
        if identity in identities:
            raise ValueError("duplicate molecular identity; no silent deduplication")
        identities.add(identity)
        if row["scaffold"] != key or assignments.get(row["id"]) != [key, row["fold"]]:
            raise ValueError("scaffold or frozen assignment mismatch")
        if group_folds.setdefault(key, row["fold"]) != row["fold"]:
            raise ValueError("scaffold leakage across folds")
    folds = {row["fold"] for row in records}
    if len(folds) < 2 or len(folds) > 5:
        raise ValueError("require 2..5 frozen folds")
    if provenance["kind"] == "development":
        counts = [sum(r["fold"] == f for r in records) for f in range(5)]
        if len(records) != 582 or folds != set(range(5)) or counts != [115, 120, 115, 117, 115]:
            raise ValueError("development universe differs from frozen V2 CV cohort")


def feature_matrices(records):
    matrices = {
        "R1": np.asarray([get_r1_vector(r["smiles"]) for r in records], dtype=float),
        "R2": np.asarray([get_r2_morgan(r["smiles"]) for r in records], dtype=float),
    }
    if matrices["R1"].shape != (len(records), 12) or matrices["R2"].shape != (len(records), 2048):
        raise ValueError("incorrect feature dimensions")
    matrices["R1"][~np.isfinite(matrices["R1"])] = np.nan
    if not np.isin(matrices["R2"], [0, 1]).all():
        raise ValueError("Morgan fingerprints must be binary and finite")
    return matrices


def model_spec(name, representation, config):
    if name not in REPRESENTATIONS or REPRESENTATIONS[name] != representation:
        raise ValueError("incorrect pipeline representation mapping")
    # Also check against an independent semantic definition, not a mutable registry alone.
    expected = "R1" if name.startswith("descriptor_") else "R2"
    if representation != expected:
        raise ValueError("incorrect pipeline representation mapping")
    config.validate()
    if name.endswith("ridge"):
        estimator = Ridge(alpha=config.ridge_alpha, solver="lsqr", tol=1e-4,
                          max_iter=10000, fit_intercept=True)
    else:
        estimator = RandomForestRegressor(
            n_estimators=config.trees, max_features=config.max_features,
            min_samples_leaf=config.min_samples_leaf, max_depth=config.max_depth,
            random_state=config.seed, n_jobs=1, bootstrap=True,
            criterion="squared_error", min_samples_split=2,
        )
    steps = []
    if representation == "R1":
        steps.append(("impute", SimpleImputer(strategy="median")))
        if name.endswith("ridge"):
            steps += [("variance", VarianceThreshold()), ("scale", StandardScaler())]
    return Pipeline(steps + [("estimator", estimator)])


def metrics(y, predicted):
    y, p = np.asarray(y, dtype=float), np.asarray(predicted, dtype=float)
    if y.ndim != 1 or y.shape != p.shape or len(y) < 2 or not np.isfinite([y, p]).all():
        raise ValueError("metrics need aligned finite vectors of length >=2")
    variable = np.ptp(y) > 0 and np.ptp(p) > 0
    return {"mae_log10": float(np.mean(np.abs(y-p))),
            "rmse_log10": float(np.sqrt(np.mean((y-p)**2))),
            "pearson_r": float(pearsonr(y, p).statistic) if variable else None,
            "spearman_rho": float(spearmanr(y, p).statistic) if variable else None,
            "r_squared": float(1-np.sum((y-p)**2)/np.sum((y-y.mean())**2)) if np.ptp(y) else None}


def evaluate(records, provenance, config=Configuration(), *, approve_development=False):
    """No selection or holdout evaluation. Return all four models and two baselines.

    Caller must supply an independently reviewed development-only bundle; its
    declared source hashes are recorded, not authenticated against on-disk data.
    """
    validate_bundle(records, provenance, approve_development=approve_development)
    config.validate()
    x = feature_matrices(records)
    y = transform_target([r["clint"] for r in records])
    folds = np.asarray([r["fold"] for r in records])
    predictions = {name: np.full(len(y), np.nan) for name in
                   [*REPRESENTATIONS, "mean_baseline", "median_baseline"]}
    fitted = []
    for fold in sorted(set(folds)):
        train, valid = folds != fold, folds == fold
        if np.isnan(x["R1"][train]).all(axis=0).any():
            raise ValueError("training fold has an entirely missing descriptor")
        for name, representation in REPRESENTATIONS.items():
            model = model_spec(name, representation, config)
            model.fit(x[representation][train], y[train])
            predictions[name][valid] = model.predict(x[representation][valid])
            fitted.append({"fold": int(fold), "pipeline": name, "representation": representation,
                           "input_columns": int(x[representation].shape[1]),
                           "estimator_params": model.named_steps["estimator"].get_params(deep=False),
                           "preprocessing": [step for step, _ in model.steps[:-1]]})
        predictions["mean_baseline"][valid] = y[train].mean()
        predictions["median_baseline"][valid] = np.median(y[train])
    return {"status": "EXPLORATORY_DEVELOPMENT_ONLY", "data_provenance": provenance,
            "requested_configuration": asdict(config), "fitted_configurations": fitted,
            "runtime": {"python": platform.python_version(), **{
                name: importlib.metadata.version(name) for name in ["numpy", "scipy", "scikit-learn", "rdkit"]}},
            "representation": {"R1": list(R1_PROPERTIES), "R2": {
                "radius": 2, "bits": 2048, "binary": True, "useChirality": False}},
            "row_order": [r["id"] for r in records], "folds": folds.tolist(),
            "observed_log10": y.tolist(),
            "predictions": {k: v.tolist() for k, v in predictions.items()},
            "pooled_oof_metrics": {k: metrics(y, v) for k, v in predictions.items()}}
