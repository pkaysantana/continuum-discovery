"""v3A.1-RC cohort construction, outcome-blind scaffold folds, and ECFP4 feature matrix (mechanical preflight only)."""
import hashlib
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, rdBase
from rdkit.Chem import rdFingerprintGenerator

from src import v3a_config as C
from src.partition import get_scaffold_key

COHORT_COLUMNS = ["activity_id", "chembl_id", "canonical_smiles_rdkit", "scaffold_key",
                  "CLint", "log10_CLint", "semantic_class"]
FOLD_COLUMNS = ["activity_id", "chembl_id", "scaffold_key", "outer_fold"]
CLASS_EXACT = "EXACT_QUANTITATIVE"
CLASS_BOUNDARY_LOW = "EXACT_QUANTITATIVE_BOUNDARY_LOW"


class PreflightGateError(AssertionError):
    """A named SAP §19 gate tripped."""


def gate(condition, name, detail=""):
    if not condition:
        raise PreflightGateError(f"{name} FAILED {detail}".strip())


# --------------------------------------------------------------------------- cohort
def build_cohort(rows_csv) -> pd.DataFrame:
    """Cohort = standard_relation IS NULL and 3 <= CLint < 150, from the canonical interim rows."""
    raw = pd.read_csv(rows_csv, low_memory=False)
    gate(len(raw) == C.N_TOTAL_ASSAY_ROWS, "GATE_01a_FULL_DATASET_CONSERVATION", f"raw rows={len(raw)}")
    gate((raw["assay_chembl_id"] == "CHEMBL3301370").all(), "GATE_01_ASSAY_ID")
    gate(raw["activity_id"].is_unique, "GATE_01_ACTIVITY_ID_UNIQUE")
    rel = raw["standard_relation"]
    n_null = int(rel.isna().sum())
    n_lt = int((rel == "<").sum())
    n_gt = int((rel == ">").sum())
    gate(n_null + n_lt + n_gt == len(raw), "GATE_01a_FULL_DATASET_CONSERVATION", "unexpected relation values")
    gate((n_null, n_lt, n_gt) == (C.COHORT_N, C.N_LEFT_CENSORED, C.N_RIGHT_CENSORED),
         "GATE_01a_FULL_DATASET_CONSERVATION", f"null/<//>={n_null}/{n_lt}/{n_gt}")

    mask = rel.isna() & (raw["standard_value"] >= C.CLINT_LOW) & (raw["standard_value"] < C.CLINT_HIGH)
    cohort = raw.loc[mask].copy()
    gate(len(cohort) == C.COHORT_N, "GATE_01_COHORT_COUNT", f"N={len(cohort)}")
    gate(cohort["standard_relation"].isna().all(), "GATE_01c_RAW_FIELD_PRESERVATION")
    # No censored row can be present (explicit, not merely implied by the mask).
    censored_ids = set(raw.loc[rel.isin(["<", ">"]), "activity_id"])
    gate(not censored_ids & set(cohort["activity_id"]), "GATE_01_CENSORED_IN_COHORT")
    gate((cohort["standard_value"] == cohort["value"]).all(), "GATE_01_VALUE_COLUMNS_AGREE")
    gate(cohort["structure_status"].eq("VALID").all() and cohort["canonical_smiles_rdkit"].notna().all(),
         "GATE_02_STRUCTURE_STATUS")

    clint = cohort["standard_value"].astype(float)
    n_boundary_low = int((clint == C.CLINT_LOW).sum())
    n_boundary_high = int((clint == C.CLINT_HIGH).sum())
    n_interior = int(((clint > C.CLINT_LOW) & (clint < C.CLINT_HIGH)).sum())
    gate((n_interior, n_boundary_low, n_boundary_high) == (C.N_INTERIOR, C.N_BOUNDARY_LOW, C.N_BOUNDARY_HIGH),
         "GATE_01b_EXACT_BOUNDARY_BREAKDOWN", f"{n_interior}/{n_boundary_low}/{n_boundary_high}")

    out = pd.DataFrame({
        "activity_id": cohort["activity_id"].astype("int64").to_numpy(),
        "chembl_id": cohort["molecule_chembl_id"].to_numpy(),
        "canonical_smiles_rdkit": cohort["canonical_smiles_rdkit"].to_numpy(),
        "CLint": clint.to_numpy(),
    })
    out["scaffold_key"] = [get_scaffold_key(s) for s in out["canonical_smiles_rdkit"]]
    gate(out["scaffold_key"].notna().all(), "GATE_02_SCAFFOLD_KEY_MISSING")
    out["log10_CLint"] = np.log10(out["CLint"].to_numpy())
    out["semantic_class"] = np.where(out["CLint"] == C.CLINT_LOW, CLASS_BOUNDARY_LOW, CLASS_EXACT)
    out = out.sort_values("activity_id", kind="mergesort").reset_index(drop=True)
    gate(out["chembl_id"].is_unique, "GATE_01_CHEMBL_ID_UNIQUE")
    return out[COHORT_COLUMNS]


def write_csv(df: pd.DataFrame, path) -> str:
    """LF line endings, shortest round-trip floats: byte-stable across platforms."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, lineterminator="\n")
    return C.sha256_file(path)


# --------------------------------------------------------------------------- folds
def assign_scaffold_folds(scaffold_keys, n_folds=C.N_FOLDS, tie_hash=C.split_tiebreak_hash) -> dict:
    """SAP §8.2. Depends only on the multiset of scaffold keys: no outcomes, no similarity.

    groups sorted by (-count, sha256(scaffold_key + suffix)); each goes to the currently smallest
    fold; equal-size folds resolved by ascending fold number (1..n_folds).
    """
    counts = defaultdict(int)
    for k in scaffold_keys:
        counts[k] += 1
    order = sorted(counts, key=lambda k: (-counts[k], tie_hash(k)))
    sizes = {f: 0 for f in range(1, n_folds + 1)}
    assignment = {}
    for k in order:
        f = min(sizes, key=lambda fold: (sizes[fold], fold))
        assignment[k] = f
        sizes[f] += counts[k]
    return assignment


def build_folds(cohort: pd.DataFrame, tie_hash=C.split_tiebreak_hash) -> pd.DataFrame:
    """Only ids and scaffold keys are read; outcome columns are never touched."""
    assign = assign_scaffold_folds(cohort["scaffold_key"].tolist(), tie_hash=tie_hash)
    folds = cohort[["activity_id", "chembl_id", "scaffold_key"]].copy()
    folds["outer_fold"] = folds["scaffold_key"].map(assign).astype("int64")
    verify_folds(cohort, folds)
    return folds[FOLD_COLUMNS]


def verify_folds(cohort: pd.DataFrame, folds: pd.DataFrame):
    ids = folds["activity_id"]
    gate(len(folds) == C.COHORT_N, "GATE_06_UNIQUE_TEST_INSTANCE", "row count")
    gate(ids.is_unique, "GATE_06_UNIQUE_TEST_INSTANCE", "duplicate activity_id")
    gate(set(ids) == set(cohort["activity_id"]), "GATE_06_UNIQUE_TEST_INSTANCE", "missing/extra ids")
    gate(folds["outer_fold"].isin(range(1, C.N_FOLDS + 1)).all(), "GATE_06_FOLD_RANGE")
    per_scaf = folds.groupby("scaffold_key")["outer_fold"].nunique()
    gate((per_scaf == 1).all(), "GATE_05_SCAFFOLD_LEAKAGE")
    merged = cohort[["activity_id", "chembl_id", "scaffold_key"]].merge(
        folds, on="activity_id", suffixes=("", "_f"))
    gate((merged["chembl_id"] == merged["chembl_id_f"]).all()
         and (merged["scaffold_key"] == merged["scaffold_key_f"]).all(), "GATE_02_STRUCTURE_ALIGNMENT")


def fold_statistics(folds: pd.DataFrame) -> dict:
    """Mechanical statistics only: no outcome information."""
    g = folds.groupby("outer_fold")
    return {
        "total_N": int(len(folds)),
        "compounds_per_fold": {int(k): int(v) for k, v in g.size().items()},
        "scaffold_groups_per_fold": {int(k): int(v) for k, v in g["scaffold_key"].nunique().items()},
        "total_unique_scaffolds": int(folds["scaffold_key"].nunique()),
    }


# --------------------------------------------------------------------------- features
_MORGAN_GEN = None


def _generator():
    global _MORGAN_GEN
    if _MORGAN_GEN is None:
        _MORGAN_GEN = rdFingerprintGenerator.GetMorganGenerator(
            radius=C.MORGAN_SPEC["radius"], fpSize=C.MORGAN_SPEC["nBits"])
    return _MORGAN_GEN


def ecfp4_row(smiles: str) -> np.ndarray:
    with rdBase.BlockLogs():
        mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise PreflightGateError(f"GATE_02_STRUCTURE_ALIGNMENT unparseable SMILES: {smiles!r}")
    # useChirality=False and includeChirality default False in generator; binary = GetFingerprintAsNumPy.
    return _generator().GetFingerprintAsNumPy(mol).astype(np.uint8)


def ecfp4_matrix(smiles_list, representation) -> np.ndarray:
    """Explicit enum routing. Anything but the frozen enum member aborts (GATE_04)."""
    gate(isinstance(representation, C.Representation)
         and representation is C.Representation.ECFP4_2048_R2_BINARY_NOCHIRAL,
         "GATE_04_REPRESENTATION_NAME", repr(representation))
    return np.vstack([ecfp4_row(s) for s in smiles_list]).astype(np.uint8)


def verify_feature_matrix(X: np.ndarray, cohort: pd.DataFrame):
    gate(X.shape == (C.COHORT_N, C.MORGAN_SPEC["nBits"]), "GATE_03_DIMENSIONALITY", str(X.shape))
    gate(X.dtype in (np.uint8, np.float32), "GATE_03_DIMENSIONALITY", str(X.dtype))
    gate(bool(np.isin(X, (0, 1)).all()), "GATE_03_BINARY")
    gate(bool(np.isfinite(X.astype(np.float64)).all()), "GATE_03_FINITE")
    gate(len(cohort) == X.shape[0], "GATE_02_STRUCTURE_ALIGNMENT")
    gate(bool((X.sum(axis=1) > 0).all()), "GATE_02_EMPTY_FINGERPRINT")


def verify_row_alignment(X: np.ndarray, cohort: pd.DataFrame, n_checks=None, seed=0):
    """Recompute each row's fingerprint independently and compare to the stored matrix.

    Parameters
    ----------
    X : ndarray of shape (N, 2048)
    cohort : DataFrame with canonical_smiles_rdkit aligned row-by-row to X
    n_checks : int or None – number of rows to spot-check (None = all)
    seed : int – RNG seed for row sampling when n_checks < N
    """
    n = len(cohort)
    if n_checks is None or n_checks >= n:
        indices = range(n)
    else:
        rng = np.random.RandomState(seed)
        indices = sorted(rng.choice(n, size=n_checks, replace=False))
    mismatches = []
    for i in indices:
        fp = ecfp4_row(cohort.iloc[i]["canonical_smiles_rdkit"])
        if not np.array_equal(fp, X[i]):
            mismatches.append(i)
    gate(len(mismatches) == 0, "GATE_02_STRUCTURE_ALIGNMENT",
         f"{len(mismatches)} row(s) mismatch: {mismatches[:5]}")


def feature_matrix_hash(X: np.ndarray) -> str:
    """SHA-256 of the contiguous C-order uint8 buffer."""
    return hashlib.sha256(np.ascontiguousarray(X, dtype=np.uint8).tobytes()).hexdigest()