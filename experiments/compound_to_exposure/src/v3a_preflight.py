"""Mechanical v3A.1-RC preflight artifact generation; never fits a model.

This module is intentionally limited to the real-data operations authorized before
scientific execution: cohort validation, ID/structure alignment, scaffold assignment,
fingerprint generation, and hashing.
"""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import rdkit
import scipy
import sklearn

from src import v3a_config as C
from src.v3a_cohort import (
    build_cohort,
    build_folds,
    ecfp4_matrix,
    feature_matrix_hash,
    fold_statistics,
    verify_feature_matrix,
    verify_folds,
    verify_row_alignment,
    write_csv,
)

SAP_RELATIVE = Path("docs/V3A_UNCERTAINTY_ASSAY_TRIAGE_SAP_3A1_RC.md")
COHORT_RELATIVE = Path("splits/V3A_EXACT744_COHORT.csv")
SPLIT_RELATIVE = Path("splits/V3A_OUTER_SCAFFOLD_FOLDS.csv")
FEATURE_RELATIVE = Path("splits/V3A_ECFP4_MATRIX.npy")
MANIFEST_RELATIVE = Path("manifests/V3A_1_RC_FREEZE_MANIFEST.json")
STATE_RELATIVE = Path("state/v3a_execution_state.json")
RAW_ROWS_RELATIVE = Path("data/interim/CHEMBL3301370_rows.csv")


def _write_json(payload: dict, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(serialized)
    return C.sha256_file(path)


def software_versions() -> dict:
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "rdkit": rdkit.__version__,
        "scipy": scipy.__version__,
        "scikit_learn": sklearn.__version__,
    }


def construct_preflight_payload(project_root: Path, write_artifacts: bool = False):
    """Construct and optionally persist deterministic mechanical artifacts.

    No estimator is instantiated or fitted here. In particular, real outcomes are
    never passed to ``RandomForestRegressor.fit``.
    """
    project_root = Path(project_root).resolve()
    cohort = build_cohort(project_root / RAW_ROWS_RELATIVE)
    folds = build_folds(cohort)
    X = ecfp4_matrix(cohort["canonical_smiles_rdkit"].tolist(), C.REPRESENTATION)
    verify_feature_matrix(X, cohort)
    verify_row_alignment(X, cohort)
    verify_folds(cohort, folds)

    cohort_path = project_root / COHORT_RELATIVE
    split_path = project_root / SPLIT_RELATIVE
    feature_path = project_root / FEATURE_RELATIVE
    if write_artifacts:
        write_csv(cohort, cohort_path)
        write_csv(folds, split_path)
        feature_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(feature_path, np.ascontiguousarray(X, dtype=np.uint8), allow_pickle=False)
    elif not (cohort_path.is_file() and split_path.is_file() and feature_path.is_file()):
        raise FileNotFoundError("persisted preflight artifacts are missing")

    fold_by_id = folds.set_index("activity_id")["outer_fold"].to_dict()
    cohort_records = [
        {
            "activity_id": int(row.activity_id),
            "chembl_id": str(row.chembl_id),
            "scaffold_key": str(row.scaffold_key),
            "outer_fold": int(fold_by_id[row.activity_id]),
        }
        for row in cohort.itertuples(index=False)
    ]
    stats = fold_statistics(folds)
    payload = {
        "schema_version": 1,
        "protocol_version": C.PROTOCOL_VERSION,
        "protocol_path": SAP_RELATIVE.as_posix(),
        "execution_state": C.STATE_PREEXECUTION,
        "required_execution_state": C.STATE_FROZEN,
        "required_explicit_flag": "--execute-scientific-analysis",
        "independent_audit_recorded": False,
        "production_model_fit_to_real_outcomes": False,
        "cohort_definition": {
            "assay_chembl_id": "CHEMBL3301370",
            "standard_relation": "IS NULL",
            "standard_value_lower_inclusive": C.CLINT_LOW,
            "standard_value_upper_exclusive": C.CLINT_HIGH,
        },
        "cohort_N": C.COHORT_N,
        "cohort_composition": {
            "strict_interior": C.N_INTERIOR,
            "exact_boundary_low_3": C.N_BOUNDARY_LOW,
            "exact_boundary_high_150": C.N_BOUNDARY_HIGH,
            "censored_observations": 0,
        },
        "cohort_records": cohort_records,
        "representation": C.REPRESENTATION.value,
        "morgan_fingerprint": dict(C.MORGAN_SPEC),
        "feature_shape": list(X.shape),
        "feature_dtype": str(X.dtype),
        "fold_statistics": stats,
        "rf_params": dict(C.FROZEN_RF_PARAMS),
        "uncertainty_score_definitions": {
            "primary": "QRF80_WIDTH = weighted_Q90(y_train) - weighted_Q10(y_train)",
            "tanimoto": "1 - max_train Tanimoto(ECFP4_query, ECFP4_train)",
            "physchem_knn5": "mean Euclidean distance to 5 nearest standardized outer-training descriptors",
            "neff_inverse": "sum_i(w_i ** 2)",
            "local_label_sd": "sqrt(sum_i(w_i * (y_i - sum_j(w_j*y_j)) ** 2))",
            "tree_sd": "population standard deviation of per-tree predictions",
        },
        "random_seeds": {
            "model_training": C.MASTER_SEED,
            "split_tie_suffix": C.SPLIT_TIE_SUFFIX,
            "retention_tie_suffix": C.RETENTION_TIE_SUFFIX,
            "bootstrap": C.MASTER_SEED,
            "random_comparator": C.MASTER_SEED,
        },
        "primary_estimand": "REL_BENEFIT_80 = (RMSE_RANDOM80 - RMSE_QRF80) / RMSE_RANDOM80",
        "practical_threshold": C.PRACTICAL_THRESHOLD,
        "software_versions": software_versions(),
        "sap_sha256": C.sha256_file(project_root / SAP_RELATIVE),
        "raw_rows_sha256": C.sha256_file(project_root / RAW_ROWS_RELATIVE),
        "cohort_sha256": C.sha256_file(cohort_path),
        "split_sha256": C.sha256_file(split_path),
        "feature_sha256": feature_matrix_hash(X),
        "feature_file_sha256": C.sha256_file(feature_path),
    }
    return payload, cohort, folds, X


def verify_persisted_artifacts(project_root: Path, manifest: dict) -> None:
    """Fail closed if persisted hashes, dimensions, keys, or state drift."""
    project_root = Path(project_root).resolve()
    required_hashes = {
        "sap_sha256": project_root / SAP_RELATIVE,
        "cohort_sha256": project_root / COHORT_RELATIVE,
        "split_sha256": project_root / SPLIT_RELATIVE,
    }
    for key, path in required_hashes.items():
        if manifest.get(key) != C.sha256_file(path):
            raise RuntimeError(f"{key} mismatch")
    X = np.load(project_root / FEATURE_RELATIVE, allow_pickle=False)
    if manifest.get("feature_sha256") != feature_matrix_hash(X):
        raise RuntimeError("feature_sha256 mismatch")
    if list(X.shape) != [C.COHORT_N, C.MORGAN_SPEC["nBits"]]:
        raise RuntimeError("feature dimensionality mismatch")
    if manifest.get("execution_state") != C.STATE_PREEXECUTION:
        raise RuntimeError("pre-execution state mismatch")
    if manifest.get("production_model_fit_to_real_outcomes") is not False:
        raise RuntimeError("production-model status is not fail-closed")


def write_preflight_manifest(project_root: Path) -> dict:
    payload, _, _, _ = construct_preflight_payload(project_root, write_artifacts=True)
    _write_json(payload, Path(project_root) / MANIFEST_RELATIVE)
    state = {
        "protocol_version": C.PROTOCOL_VERSION,
        "state": C.STATE_PREEXECUTION,
        "required_state_for_scientific_execution": C.STATE_FROZEN,
        "required_explicit_flag": "--execute-scientific-analysis",
        "independent_audit_recorded": False,
        "scientific_execution_allowed": False,
        "production_model_fit_to_real_outcomes": False,
    }
    _write_json(state, Path(project_root) / STATE_RELATIVE)
    verify_persisted_artifacts(project_root, payload)
    return payload


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--write", action="store_true", help="persist mechanical artifacts and manifest")
    args = parser.parse_args(argv)
    if args.write:
        payload = write_preflight_manifest(args.project_root)
    else:
        manifest_path = args.project_root / MANIFEST_RELATIVE
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        verify_persisted_artifacts(args.project_root, payload)
    print(json.dumps({key: payload[key] for key in (
        "execution_state", "sap_sha256", "cohort_sha256", "split_sha256", "feature_sha256"
    )}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
