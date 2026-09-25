"""Fail-closed v3A scientific runner and outcome-blind prediction freeze.

Ticket 1 binds execution authorization to the persisted frozen inputs and provides
a collision-safe internal run ledger.  Ticket 2 adds only the five-fold model and
uncertainty orchestration up to an immutable prediction freeze.  This module does
not expose an outer-test outcome argument and contains no outcome-evaluation code.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from src import v3a_config as C
from src.v3a_preflight import (
    COHORT_RELATIVE,
    FEATURE_RELATIVE,
    MANIFEST_RELATIVE,
    SAP_RELATIVE,
    SPLIT_RELATIVE,
    STATE_RELATIVE,
)
from src.v3a_qrf_weights import (
    ExecutionGuardError,
    QRFWeightRecoveryError,
    check_execution_guard,
    compute_descriptor_matrix,
    fit_physchem_space,
    local_label_sd,
    neff_inverse,
    physchem_knn_distance,
    qrf_prediction_quantiles,
    recover_forest_weights_many,
    tanimoto_unfamiliarity,
    tree_dispersion,
)


SCIENTIFIC_RUNS_RELATIVE = Path("scientific_runs/v3a")
LEDGER_FILENAME = "execution_ledger.json"
LEDGER_SCHEMA_VERSION = 1
PREDICTION_FREEZE_SCHEMA_VERSION = 1
_RUN_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")

_UNCERTAINTY_FIELDS = (
    "qrf_width",
    "tanimoto_unfamiliarity",
    "physchem_knn5_distance",
    "neff_inverse",
    "local_label_sd",
    "tree_sd",
)
_BASE_PREDICTION_FIELDS = (
    "activity_id",
    "outer_fold",
    "rf_prediction",
    "qrf_q10",
    "qrf_q90",
    "qrf_width",
    "tanimoto_unfamiliarity",
    "physchem_knn5_distance",
    "neff_inverse",
    "local_label_sd",
    "tree_sd",
)
_RANKING_FIELDS = (
    "tie_break_sha256",
    "within_fold_ranks",
    "retained_coverages",
)
_PREDICTION_RECORD_FIELDS = frozenset(_BASE_PREDICTION_FIELDS + _RANKING_FIELDS)
_PROVENANCE_FIELDS = frozenset(
    {
        "protocol_version",
        "protocol_path",
        "manifest_sha256",
        "sap_sha256",
        "cohort_sha256",
        "split_sha256",
        "feature_sha256",
        "feature_file_sha256",
    }
)
_HASH_PROVENANCE_FIELDS = _PROVENANCE_FIELDS - {"protocol_version", "protocol_path"}
_FORBIDDEN_OUTCOME_TOKENS = (
    "observed",
    "residual",
    "absolute_error",
    "squared_error",
    "rmse",
    "mae",
    "error_class",
    "error_enrichment",
    "sensitivity",
    "y_test",
)


class RunnerError(RuntimeError):
    """Base class for Ticket 1 runner failures."""


class FrozenArtifactError(RunnerError):
    """A required persisted input is absent or malformed."""


class RunAuthorizationError(ExecutionGuardError, RunnerError):
    """The persisted authorization contract is not fully satisfied."""


class RunCollisionError(RunnerError):
    """A requested run ID already has a filesystem entry."""


class ProtectedRunPathError(RunnerError):
    """A requested output path is not a separate scientific-run namespace."""


class LifecycleTransitionError(RunnerError):
    """An internal ledger transition is not permitted in Ticket 1."""


class PredictionOrchestrationError(RunnerError):
    """The outcome-blind fold orchestration contract was violated."""


class PredictionFreezeError(RunnerError):
    """A complete deterministic prediction freeze could not be built or sealed."""


class PredictionFreezeCollisionError(PredictionFreezeError):
    """A prediction-freeze path already exists and may not be overwritten."""


class InternalRunStatus(str, Enum):
    """Internal-only lifecycle vocabulary; never written to frozen state."""

    RUNNER_IMPLEMENTED_NOT_AUDITED = "RUNNER_IMPLEMENTED_NOT_AUDITED"
    EXECUTION_RUNNING = "EXECUTION_RUNNING"
    EXECUTION_ABORTED = "EXECUTION_ABORTED"


@dataclass(frozen=True)
class FrozenArtifacts:
    """Read-only references and metadata for the persisted frozen inputs."""

    project_root: Path
    manifest: Mapping[str, Any]
    state: Mapping[str, Any]
    manifest_path: Path
    state_path: Path
    sap_path: Path
    cohort_path: Path
    split_path: Path
    feature_path: Path
    manifest_sha256: str


@dataclass(frozen=True)
class RunLedger:
    """Handle to a single collision-protected internal execution ledger."""

    run_id: str
    run_directory: Path
    ledger_path: Path

    def read(self) -> dict[str, Any]:
        return _read_json_object(self.ledger_path, "execution ledger")


@dataclass(frozen=True)
class OutcomeBlindInputs:
    """Outcome-free rows aligned to the frozen IDs, folds, fingerprints, and descriptors."""

    activity_ids: tuple[Any, ...]
    outer_folds: tuple[int, ...]
    scaffold_keys: tuple[str, ...]
    features: np.ndarray
    descriptors: np.ndarray
    provenance: Mapping[str, Any]


@dataclass(frozen=True)
class PredictionFreeze:
    """Canonical immutable bytes produced only after all five folds complete."""

    canonical_bytes: bytes
    sha256: str
    row_count: int
    fold_counts: tuple[tuple[int, int], ...]

    def read_payload(self) -> dict[str, Any]:
        """Return a detached mutable view; changing it cannot alter frozen bytes."""

        return json.loads(self.canonical_bytes.decode("utf-8"))


@dataclass(frozen=True)
class SealedPredictionFreeze:
    """Filesystem seal for a prediction freeze written with exclusive creation."""

    path: Path
    canonical_bytes: bytes
    sha256: str
    row_count: int
    fold_counts: tuple[tuple[int, int], ...]

    def verify(self) -> bool:
        try:
            persisted = self.path.read_bytes()
        except OSError:
            return False
        return (
            persisted == self.canonical_bytes
            and hashlib.sha256(persisted).hexdigest() == self.sha256
        )


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FrozenArtifactError(f"{label} is missing or invalid: {path}") from exc
    if not isinstance(payload, dict):
        raise FrozenArtifactError(f"{label} must be a JSON object: {path}")
    return payload


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    try:
        serialized = json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise RunnerError("execution ledger is not canonical-JSON serializable") from exc
    return (serialized + "\n").encode("utf-8")


def _atomic_write_json(payload: Mapping[str, Any], path: Path) -> None:
    data = _canonical_json_bytes(payload)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass


def _required_regular_file(project_root: Path, relative: Path) -> Path:
    path = project_root / relative
    if not path.is_file():
        raise FrozenArtifactError(f"required frozen artifact is missing: {relative.as_posix()}")
    return path


def load_frozen_artifacts(project_root: Path) -> FrozenArtifacts:
    """Load frozen manifest/state metadata and bind canonical artifact paths.

    Cohort outcomes are not parsed or exposed by this Ticket 1 loader.
    Cryptographic content verification remains centralized in the existing
    execution guard and is invoked by :func:`authorize_run`.
    """

    root = Path(project_root).resolve()
    if not root.is_dir():
        raise FrozenArtifactError(f"project root does not exist: {root}")

    manifest_path = _required_regular_file(root, MANIFEST_RELATIVE)
    state_path = _required_regular_file(root, STATE_RELATIVE)
    sap_path = _required_regular_file(root, SAP_RELATIVE)
    cohort_path = _required_regular_file(root, COHORT_RELATIVE)
    split_path = _required_regular_file(root, SPLIT_RELATIVE)
    feature_path = _required_regular_file(root, FEATURE_RELATIVE)

    manifest = _read_json_object(manifest_path, "freeze manifest")
    state = _read_json_object(state_path, "persisted execution state")
    return FrozenArtifacts(
        project_root=root,
        manifest=manifest,
        state=state,
        manifest_path=manifest_path,
        state_path=state_path,
        sap_path=sap_path,
        cohort_path=cohort_path,
        split_path=split_path,
        feature_path=feature_path,
        manifest_sha256=C.sha256_file(manifest_path),
    )


def _require_exact(value: Any, expected: Any, label: str) -> None:
    if value != expected:
        raise RunAuthorizationError(
            f"Execution blocked: {label} mismatch; expected {expected!r}"
        )


def _validate_authorization_metadata(artifacts: FrozenArtifacts) -> None:
    manifest = artifacts.manifest
    state = artifacts.state

    _require_exact(state.get("protocol_version"), C.PROTOCOL_VERSION, "state protocol_version")
    _require_exact(manifest.get("protocol_version"), C.PROTOCOL_VERSION, "manifest protocol_version")
    _require_exact(manifest.get("protocol_path"), SAP_RELATIVE.as_posix(), "protocol path")
    _require_exact(state.get("state"), C.STATE_FROZEN, "persisted state")
    _require_exact(
        state.get("required_state_for_scientific_execution"),
        C.STATE_FROZEN,
        "state required execution state",
    )
    _require_exact(manifest.get("required_execution_state"), C.STATE_FROZEN, "manifest required state")
    _require_exact(
        state.get("required_explicit_flag"),
        "--execute-scientific-analysis",
        "state explicit flag contract",
    )
    _require_exact(
        manifest.get("required_explicit_flag"),
        "--execute-scientific-analysis",
        "manifest explicit flag contract",
    )

    if state.get("scientific_execution_allowed") is not True:
        raise RunAuthorizationError(
            "Execution blocked: persisted scientific_execution_allowed is not true"
        )
    if state.get("independent_audit_recorded") is not True:
        raise RunAuthorizationError(
            "Execution blocked: persisted independent audit is not recorded"
        )
    if manifest.get("independent_audit_recorded") is not True:
        raise RunAuthorizationError(
            "Execution blocked: manifest independent audit is not recorded"
        )
    if state.get("production_model_fit_to_real_outcomes") is not False:
        raise RunAuthorizationError(
            "Execution blocked: persisted production-model status is not fail-closed"
        )

    _require_exact(manifest.get("cohort_N"), C.COHORT_N, "cohort count")
    cohort_records = manifest.get("cohort_records")
    if not isinstance(cohort_records, list) or len(cohort_records) != C.COHORT_N:
        raise RunAuthorizationError("Execution blocked: frozen cohort record count mismatch")
    activity_ids = [record.get("activity_id") for record in cohort_records if isinstance(record, dict)]
    if len(activity_ids) != C.COHORT_N or len(set(activity_ids)) != C.COHORT_N:
        raise RunAuthorizationError("Execution blocked: frozen cohort activity IDs are incomplete")

    _require_exact(manifest.get("representation"), C.REPRESENTATION.value, "representation")
    _require_exact(manifest.get("morgan_fingerprint"), dict(C.MORGAN_SPEC), "Morgan configuration")
    _require_exact(manifest.get("rf_params"), dict(C.FROZEN_RF_PARAMS), "RF configuration")
    _require_exact(
        manifest.get("feature_shape"),
        [C.COHORT_N, C.MORGAN_SPEC["nBits"]],
        "feature shape metadata",
    )
    if manifest.get("feature_dtype") not in ("uint8", "float32"):
        raise RunAuthorizationError("Execution blocked: feature dtype metadata mismatch")

    for key in (
        "sap_sha256",
        "cohort_sha256",
        "split_sha256",
        "feature_sha256",
        "feature_file_sha256",
    ):
        value = manifest.get(key)
        if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
            raise RunAuthorizationError(f"Execution blocked: invalid or missing {key}")


def authorize_run(
    project_root: Path,
    *,
    execute_scientific_analysis: bool,
    ledger: RunLedger | None = None,
) -> FrozenArtifacts:
    """Authorize only an explicitly requested, audited, fully frozen execution.

    The current repository state is expected to fail this function.  A ledger is
    optional so pure preflight authorization checks remain side-effect free; when
    supplied, success or failure is recorded in that already-initialized ledger.
    """

    if execute_scientific_analysis is not True and execute_scientific_analysis is not False:
        raise RunAuthorizationError(
            "Execution blocked: explicit scientific-execution authorization must be boolean"
        )
    try:
        artifacts = load_frozen_artifacts(project_root)
        _validate_authorization_metadata(artifacts)
        check_execution_guard(
            dict(artifacts.manifest),
            require_flag=execute_scientific_analysis,
            project_root=artifacts.project_root,
        )
        expected_feature_file_hash = artifacts.manifest["feature_file_sha256"]
        if C.sha256_file(artifacts.feature_path) != expected_feature_file_hash:
            raise RunAuthorizationError("Execution blocked: feature_file_sha256 mismatch")
    except (FrozenArtifactError, ExecutionGuardError, OSError, ValueError) as exc:
        error = exc if isinstance(exc, RunAuthorizationError) else RunAuthorizationError(
            f"Execution blocked: runner authorization failed: {exc}"
        )
        if ledger is not None:
            _record_authorization(ledger, execute_scientific_analysis, False, str(error))
        if error is exc:
            raise
        raise error from exc

    if ledger is not None:
        payload = ledger.read()
        if payload.get("manifest_sha256") != artifacts.manifest_sha256:
            error = RunAuthorizationError(
                "Execution blocked: ledger manifest hash differs from authorized manifest"
            )
            _record_authorization(ledger, execute_scientific_analysis, False, str(error))
            raise error
        ledger_state_fields = {
            "preflight_state": artifacts.state.get("state"),
            "scientific_execution_allowed": artifacts.state.get("scientific_execution_allowed"),
            "independent_audit_recorded": artifacts.state.get("independent_audit_recorded"),
        }
        if any(payload.get(key) != value for key, value in ledger_state_fields.items()):
            error = RunAuthorizationError(
                "Execution blocked: persisted state changed after ledger initialization"
            )
            _record_authorization(ledger, execute_scientific_analysis, False, str(error))
            raise error
        _record_authorization(ledger, execute_scientific_analysis, True, None)
    return artifacts


def _normalise_status(value: InternalRunStatus | str) -> InternalRunStatus:
    try:
        return value if isinstance(value, InternalRunStatus) else InternalRunStatus(value)
    except ValueError as exc:
        raise LifecycleTransitionError(f"unknown internal runner status: {value!r}") from exc


def validate_internal_transition(
    current: InternalRunStatus | str,
    target: InternalRunStatus | str,
) -> InternalRunStatus:
    """Validate only the lifecycle edges reachable in Ticket 1."""

    current_status = _normalise_status(current)
    target_status = _normalise_status(target)
    allowed = {
        InternalRunStatus.RUNNER_IMPLEMENTED_NOT_AUDITED: {
            InternalRunStatus.EXECUTION_RUNNING,
            InternalRunStatus.EXECUTION_ABORTED,
        },
        InternalRunStatus.EXECUTION_RUNNING: {InternalRunStatus.EXECUTION_ABORTED},
        InternalRunStatus.EXECUTION_ABORTED: set(),
    }
    if target_status not in allowed[current_status]:
        raise LifecycleTransitionError(
            f"internal transition {current_status.value} -> {target_status.value} is not allowed"
        )
    return target_status


def _validate_run_id(run_id: str) -> None:
    if not isinstance(run_id, str) or _RUN_ID_RE.fullmatch(run_id) is None or run_id in {".", ".."}:
        raise ProtectedRunPathError("run_id must be one safe filesystem component")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _validate_run_root(run_root: Path, project_root: Path) -> None:
    root = run_root.resolve()
    project = project_root.resolve()
    canonical_scientific_root = (project / SCIENTIFIC_RUNS_RELATIVE).resolve()
    if root != canonical_scientific_root:
        raise ProtectedRunPathError(
            "run_root must be the canonical scientific_runs/v3a namespace"
        )


def reject_existing_run_directory(
    run_root: Path,
    run_id: str,
    *,
    project_root: Path | None = None,
) -> Path:
    """Return the intended path only when it is safe and does not exist."""

    _validate_run_id(run_id)
    root = Path(run_root).resolve()
    if project_root is None:
        raise ProtectedRunPathError("canonical project_root is required")
    _validate_run_root(root, Path(project_root))
    candidate = (root / run_id).resolve()
    if candidate.parent != root or not _is_relative_to(candidate, root):
        raise ProtectedRunPathError("run directory escaped its namespace")
    if os.path.lexists(candidate):
        raise RunCollisionError(f"run directory already exists: {candidate}")
    return candidate


def initialize_run_ledger(
    run_root: Path,
    run_id: str,
    *,
    artifacts: FrozenArtifacts,
    git_commit: str,
    start_timestamp: str,
    authorization_requested: bool,
    environment_summary: Mapping[str, Any] | None = None,
) -> RunLedger:
    """Atomically claim a new run ID and write its minimal canonical JSON ledger."""

    if not isinstance(git_commit, str) or not git_commit.strip():
        raise RunnerError("git_commit is required")
    if not isinstance(start_timestamp, str) or not start_timestamp.strip():
        raise RunnerError("start_timestamp is required")
    if authorization_requested is not True and authorization_requested is not False:
        raise RunnerError("authorization_requested must be a boolean")

    run_directory = reject_existing_run_directory(
        run_root, run_id, project_root=artifacts.project_root
    )
    environment = (
        dict(environment_summary)
        if environment_summary is not None
        else {
            "metadata_source": "freeze_manifest.software_versions",
            "software_versions": artifacts.manifest.get("software_versions", {}),
        }
    )
    payload = {
        "abort_reason": None,
        "authorization_passed": False,
        "authorization_requested": authorization_requested,
        "environment_summary": environment,
        "git_commit": git_commit,
        "independent_audit_recorded": artifacts.state.get("independent_audit_recorded"),
        "manifest_reference": MANIFEST_RELATIVE.as_posix(),
        "manifest_sha256": artifacts.manifest_sha256,
        "preflight_state": artifacts.state.get("state"),
        "run_id": run_id,
        "schema_version": LEDGER_SCHEMA_VERSION,
        "scientific_execution_allowed": artifacts.state.get("scientific_execution_allowed"),
        "start_timestamp": start_timestamp,
        "status": InternalRunStatus.RUNNER_IMPLEMENTED_NOT_AUDITED.value,
    }
    _canonical_json_bytes(payload)

    Path(run_root).resolve().mkdir(parents=True, exist_ok=True)
    try:
        run_directory.mkdir()
    except FileExistsError as exc:
        raise RunCollisionError(f"run directory already exists: {run_directory}") from exc

    ledger_path = run_directory / LEDGER_FILENAME
    try:
        _atomic_write_json(payload, ledger_path)
    except Exception as exc:
        # The exclusively claimed directory is intentionally retained so a
        # failed/partial initialization can never be silently reused.
        raise RunnerError(
            f"run directory was claimed but ledger initialization failed: {run_directory}"
        ) from exc
    return RunLedger(run_id=run_id, run_directory=run_directory, ledger_path=ledger_path)


def _validated_ledger_payload(ledger: RunLedger) -> dict[str, Any]:
    payload = ledger.read()
    if payload.get("schema_version") != LEDGER_SCHEMA_VERSION:
        raise RunnerError("execution ledger schema mismatch")
    if payload.get("run_id") != ledger.run_id:
        raise RunnerError("execution ledger run_id mismatch")
    if ledger.ledger_path.parent.resolve() != ledger.run_directory.resolve():
        raise RunnerError("execution ledger path escaped its run directory")
    return payload


def _record_authorization(
    ledger: RunLedger,
    requested: bool,
    passed: bool,
    abort_reason: str | None,
) -> None:
    payload = _validated_ledger_payload(ledger)
    payload["authorization_requested"] = requested
    payload["authorization_passed"] = passed
    if passed:
        payload["abort_reason"] = None
    else:
        payload["status"] = validate_internal_transition(
            payload["status"], InternalRunStatus.EXECUTION_ABORTED
        ).value
        payload["abort_reason"] = abort_reason or "authorization failed"
    _atomic_write_json(payload, ledger.ledger_path)


def start_run(ledger: RunLedger) -> None:
    """Mark an authorized Ticket 1 ledger as running; perform no scientific work."""

    payload = _validated_ledger_payload(ledger)
    target_status = validate_internal_transition(
        payload["status"], InternalRunStatus.EXECUTION_RUNNING
    )
    if payload.get("authorization_requested") is not True or payload.get("authorization_passed") is not True:
        raise RunAuthorizationError("Execution blocked: ledger is not authorized")
    payload["status"] = target_status.value
    _atomic_write_json(payload, ledger.ledger_path)


def abort_run(ledger: RunLedger, reason: str) -> None:
    """Record a terminal Ticket 1 abort without producing result artifacts."""

    if not isinstance(reason, str) or not reason.strip():
        raise RunnerError("abort reason is required")
    payload = _validated_ledger_payload(ledger)
    payload["status"] = validate_internal_transition(
        payload["status"], InternalRunStatus.EXECUTION_ABORTED
    ).value
    payload["abort_reason"] = reason
    _atomic_write_json(payload, ledger.ledger_path)


# --------------------------------------------------------------------------- Ticket 2 inputs
def _immutable_array(values: np.ndarray) -> np.ndarray:
    """Return a C-contiguous array backed by immutable bytes."""

    contiguous = np.ascontiguousarray(values)
    return np.frombuffer(contiguous.tobytes(), dtype=contiguous.dtype).reshape(contiguous.shape)


def _prediction_provenance(artifacts: FrozenArtifacts) -> dict[str, str]:
    manifest = artifacts.manifest
    provenance = {
        "protocol_version": manifest.get("protocol_version"),
        "protocol_path": manifest.get("protocol_path"),
        "manifest_sha256": artifacts.manifest_sha256,
        "sap_sha256": manifest.get("sap_sha256"),
        "cohort_sha256": manifest.get("cohort_sha256"),
        "split_sha256": manifest.get("split_sha256"),
        "feature_sha256": manifest.get("feature_sha256"),
        "feature_file_sha256": manifest.get("feature_file_sha256"),
    }
    _validate_prediction_provenance(provenance)
    return provenance


def load_outcome_blind_inputs(artifacts: FrozenArtifacts) -> OutcomeBlindInputs:
    """Load only the frozen fields permitted upstream of the prediction freeze.

    The cohort parser explicitly selects identifier, structure, and scaffold columns;
    neither ``CLint`` nor ``log10_CLint`` is loaded.  The caller must have obtained
    ``artifacts`` through the existing authorization path before production use.
    """

    manifest = artifacts.manifest
    exact_hashes = (
        (artifacts.sap_path, "sap_sha256"),
        (artifacts.cohort_path, "cohort_sha256"),
        (artifacts.split_path, "split_sha256"),
        (artifacts.feature_path, "feature_file_sha256"),
    )
    for path, field in exact_hashes:
        expected = manifest.get(field)
        if not isinstance(expected, str) or C.sha256_file(path) != expected:
            raise FrozenArtifactError(f"frozen {field} verification failed")

    try:
        cohort = pd.read_csv(
            artifacts.cohort_path,
            usecols=["activity_id", "canonical_smiles_rdkit", "scaffold_key"],
        )
        folds = pd.read_csv(
            artifacts.split_path,
            usecols=["activity_id", "scaffold_key", "outer_fold"],
        )
        features = np.load(artifacts.feature_path, allow_pickle=False)
    except (OSError, ValueError, KeyError) as exc:
        raise FrozenArtifactError("outcome-blind frozen inputs are missing or malformed") from exc

    if not cohort["activity_id"].is_unique or not folds["activity_id"].is_unique:
        raise FrozenArtifactError("frozen input activity IDs must be unique")
    if cohort["activity_id"].tolist() != folds["activity_id"].tolist():
        raise FrozenArtifactError("cohort, split, and feature row order is not aligned")
    if cohort["scaffold_key"].astype(str).tolist() != folds["scaffold_key"].astype(str).tolist():
        raise FrozenArtifactError("cohort and split scaffold keys are not aligned")
    if features.ndim != 2 or features.shape[0] != len(cohort):
        raise FrozenArtifactError("feature rows are not aligned to frozen cohort IDs")
    if features.shape != tuple(manifest.get("feature_shape", ())):
        raise FrozenArtifactError("feature shape differs from frozen manifest")
    logical_feature_hash = hashlib.sha256(
        np.ascontiguousarray(features, dtype=np.uint8).tobytes()
    ).hexdigest()
    if logical_feature_hash != manifest.get("feature_sha256"):
        raise FrozenArtifactError("logical feature matrix hash verification failed")

    descriptors = compute_descriptor_matrix(cohort["canonical_smiles_rdkit"].tolist())
    inputs = OutcomeBlindInputs(
        activity_ids=tuple(cohort["activity_id"].tolist()),
        outer_folds=tuple(int(value) for value in folds["outer_fold"]),
        scaffold_keys=tuple(folds["scaffold_key"].astype(str).tolist()),
        features=_immutable_array(features),
        descriptors=_immutable_array(descriptors),
        provenance=_prediction_provenance(artifacts),
    )
    _validate_outcome_blind_inputs(inputs)
    return inputs


def _validate_prediction_provenance(provenance: Mapping[str, Any]) -> None:
    if not isinstance(provenance, Mapping) or set(provenance) != _PROVENANCE_FIELDS:
        raise PredictionFreezeError("prediction provenance fields are incomplete or unexpected")
    if provenance.get("protocol_version") != C.PROTOCOL_VERSION:
        raise PredictionFreezeError("prediction provenance protocol version mismatch")
    if provenance.get("protocol_path") != SAP_RELATIVE.as_posix():
        raise PredictionFreezeError("prediction provenance protocol path mismatch")
    for field in _HASH_PROVENANCE_FIELDS:
        value = provenance.get(field)
        if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
            raise PredictionFreezeError(f"prediction provenance {field} is not SHA-256")


def _validate_outcome_blind_inputs(inputs: OutcomeBlindInputs) -> None:
    n_rows = len(inputs.activity_ids)
    if n_rows == 0 or len(set(inputs.activity_ids)) != n_rows:
        raise PredictionOrchestrationError("activity IDs must be nonempty and unique")
    if not (
        len(inputs.outer_folds)
        == len(inputs.scaffold_keys)
        == inputs.features.shape[0]
        == inputs.descriptors.shape[0]
        == n_rows
    ):
        raise PredictionOrchestrationError("outcome-blind input rows are not aligned")
    if inputs.features.ndim != 2 or inputs.descriptors.ndim != 2:
        raise PredictionOrchestrationError("feature and descriptor matrices must be two-dimensional")
    if inputs.features.shape[1] != C.MORGAN_SPEC["nBits"]:
        raise PredictionOrchestrationError("point-predictor matrix is not frozen ECFP4/2048")
    if inputs.descriptors.shape[1] != len(C.DESCRIPTOR_PANEL):
        raise PredictionOrchestrationError("descriptor comparator matrix is not the frozen panel")
    if not np.isin(inputs.features, (0, 1)).all():
        raise PredictionOrchestrationError("point-predictor fingerprints must be binary")
    if not np.isfinite(inputs.descriptors).all():
        raise PredictionOrchestrationError("descriptor comparator matrix must be finite")
    if set(inputs.outer_folds) != set(range(1, C.N_FOLDS + 1)):
        raise PredictionOrchestrationError("exactly the five frozen outer folds are required")
    scaffold_fold: dict[str, int] = {}
    for scaffold, fold in zip(inputs.scaffold_keys, inputs.outer_folds):
        previous = scaffold_fold.setdefault(str(scaffold), int(fold))
        if previous != int(fold):
            raise PredictionOrchestrationError("outer train/test scaffold leakage detected")
    _validate_prediction_provenance(inputs.provenance)


def _validate_frozen_rf_configuration(rf: Any) -> None:
    try:
        parameters = rf.get_params(deep=False)
    except (AttributeError, TypeError, ValueError) as exc:
        raise PredictionOrchestrationError("frozen RF factory returned an invalid estimator") from exc
    for name, expected in C.FROZEN_RF_PARAMS.items():
        if parameters.get(name, object()) != expected:
            raise PredictionOrchestrationError(f"non-frozen RF parameter: {name}")


def _fold_training_labels(
    provider: Callable[[int, tuple[Any, ...]], Sequence[float] | Mapping[Any, float]],
    outer_fold: int,
    train_ids: tuple[Any, ...],
) -> np.ndarray:
    """Request only this fold's training labels from a fold-aware provider."""

    if not callable(provider):
        raise PredictionOrchestrationError("a fold-scoped training outcome provider is required")
    supplied = provider(outer_fold, train_ids)
    if isinstance(supplied, Mapping):
        if set(supplied) != set(train_ids):
            raise PredictionOrchestrationError("training outcome mapping must contain training IDs only")
        values = [supplied[activity_id] for activity_id in train_ids]
    else:
        values = supplied
    labels = np.asarray(values, dtype=np.float64).reshape(-1)
    if labels.shape != (len(train_ids),) or not np.isfinite(labels).all():
        raise PredictionOrchestrationError("training outcomes must be finite and align to training IDs")
    return labels


def _retention_tie_hash(activity_id: Any) -> str:
    """Ticket-2 frozen tie rule: SHA256('V3A_TIE_20260923' + activity_id)."""

    return hashlib.sha256(f"V3A_TIE_20260923{activity_id}".encode("utf-8")).hexdigest()


def _activity_sort_key(activity_id: Any) -> str:
    try:
        return json.dumps(activity_id, ensure_ascii=False, allow_nan=False, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise PredictionFreezeError("activity_id must be a canonical JSON scalar") from exc


# --------------------------------------------------------------------------- Ticket 2 ranking/orchestration
def rank_outcome_blind_records(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Attach deterministic per-fold ranks and retention metadata to raw score rows."""

    ranked_records = [dict(record) for record in records]
    if not ranked_records:
        raise PredictionFreezeError("prediction records are empty")
    for record in ranked_records:
        if set(record) != set(_BASE_PREDICTION_FIELDS):
            raise PredictionFreezeError("raw prediction record fields are incomplete or unexpected")
        record["tie_break_sha256"] = _retention_tie_hash(record["activity_id"])
        record["within_fold_ranks"] = {}
        record["retained_coverages"] = {}

    folds = sorted({int(record["outer_fold"]) for record in ranked_records})
    for fold in folds:
        positions = [
            position
            for position, record in enumerate(ranked_records)
            if int(record["outer_fold"]) == fold
        ]
        for method in _UNCERTAINTY_FIELDS:
            order = sorted(
                positions,
                key=lambda position: (
                    float(ranked_records[position][method]),
                    ranked_records[position]["tie_break_sha256"],
                    _activity_sort_key(ranked_records[position]["activity_id"]),
                ),
            )
            for rank, position in enumerate(order, start=1):
                ranked_records[position]["within_fold_ranks"][method] = rank
                n_fold = len(positions)
                ranked_records[position]["retained_coverages"][method] = [
                    float(coverage)
                    for coverage in C.COVERAGE_LEVELS
                    if rank <= math.ceil(float(coverage) * n_fold)
                ]
    return ranked_records


def orchestrate_outcome_blind_predictions(
    inputs: OutcomeBlindInputs,
    training_outcome_provider: Callable[
        [int, tuple[Any, ...]], Sequence[float] | Mapping[Any, float]
    ],
    *,
    rf_factory: Callable[[], Any] = C.make_frozen_rf,
    audit_hook: Callable[[str, Mapping[str, Any]], None] | None = None,
) -> PredictionFreeze:
    """Fit one frozen RF per fold and freeze all OOF predictions/uncertainties.

    Only fold-scoped outer-training labels can enter this API.  There is no
    ``y_test`` parameter, and every reference pool is constructed from the fold's
    training positions before any test row is scored.
    """

    _validate_outcome_blind_inputs(inputs)
    ids = np.asarray(inputs.activity_ids, dtype=object)
    folds = np.asarray(inputs.outer_folds, dtype=np.int64)
    scaffolds = np.asarray(inputs.scaffold_keys, dtype=object)
    features = np.asarray(inputs.features)
    descriptors = np.asarray(inputs.descriptors, dtype=np.float64)
    raw_records: list[dict[str, Any]] = []

    for fold in range(1, C.N_FOLDS + 1):
        test_positions = np.flatnonzero(folds == fold)
        train_positions = np.flatnonzero(folds != fold)
        train_ids = tuple(ids[train_positions].tolist())
        test_ids = tuple(ids[test_positions].tolist())
        if not test_ids or set(train_ids) & set(test_ids):
            raise PredictionOrchestrationError(f"outer fold {fold} train/test ID overlap")
        train_scaffolds = set(scaffolds[train_positions].tolist())
        test_scaffolds = set(scaffolds[test_positions].tolist())
        if train_scaffolds & test_scaffolds:
            raise PredictionOrchestrationError(f"outer fold {fold} scaffold leakage")

        X_train = features[train_positions]
        X_test = features[test_positions]
        descriptor_train = descriptors[train_positions]
        descriptor_test = descriptors[test_positions]

        rf = rf_factory()
        _validate_frozen_rf_configuration(rf)
        y_train = _fold_training_labels(training_outcome_provider, fold, train_ids)
        rf.fit(X_train, y_train)
        predictions = np.asarray(rf.predict(X_test), dtype=np.float64)
        try:
            weights = recover_forest_weights_many(
                rf, X_train, X_test, sample_weight_used=False
            )
        except QRFWeightRecoveryError as exc:
            raise PredictionOrchestrationError(str(exc)) from exc
        if weights.shape != (len(test_positions), len(train_positions)):
            raise PredictionOrchestrationError("QRF weights do not index outer-training rows only")
        weight_sum_error = float(np.max(np.abs(weights.sum(axis=1) - 1.0)))
        reconstruction_error = float(np.max(np.abs(weights @ y_train - predictions)))
        if weight_sum_error >= C.WEIGHT_SUM_TOL:
            raise PredictionOrchestrationError("GATE_08_QRF_WEIGHT_SUM failed")
        if reconstruction_error >= C.WEIGHT_MEAN_TOL:
            raise PredictionOrchestrationError("GATE_07_QRF_PREDICTION_INVARIANT failed")

        scaler, descriptor_train_scaled = fit_physchem_space(descriptor_train)
        for local_index, position in enumerate(test_positions):
            row_weights = weights[local_index]
            quantiles = qrf_prediction_quantiles(
                row_weights,
                y_train,
                quantiles=(C.QRF_LOW_Q, C.QRF_HIGH_Q),
            )
            q10 = float(quantiles["Q10"])
            q90 = float(quantiles["Q90"])
            raw_records.append(
                {
                    "activity_id": ids[position].item()
                    if isinstance(ids[position], np.generic)
                    else ids[position],
                    "outer_fold": fold,
                    "rf_prediction": float(predictions[local_index]),
                    "qrf_q10": q10,
                    "qrf_q90": q90,
                    "qrf_width": q90 - q10,
                    "tanimoto_unfamiliarity": tanimoto_unfamiliarity(
                        X_test[local_index], X_train
                    ),
                    "physchem_knn5_distance": physchem_knn_distance(
                        descriptor_test[local_index],
                        descriptor_train_scaled,
                        scaler.mean_,
                        scaler.scale_,
                    ),
                    "neff_inverse": neff_inverse(row_weights),
                    "local_label_sd": local_label_sd(row_weights, y_train),
                    "tree_sd": tree_dispersion(rf, X_test[local_index]),
                }
            )

        if audit_hook is not None:
            audit_hook(
                "fold_completed",
                {
                    "outer_fold": fold,
                    "train_ids": train_ids,
                    "test_ids": test_ids,
                    "tanimoto_reference_ids": train_ids,
                    "descriptor_scaler_fit_ids": train_ids,
                    "descriptor_knn_reference_ids": train_ids,
                    "qrf_weight_ids": train_ids,
                    "local_label_ids": train_ids,
                    "qrf_weight_sum_max_error": weight_sum_error,
                    "qrf_prediction_max_error": reconstruction_error,
                },
            )

    if len(raw_records) != len(inputs.activity_ids):
        raise PredictionOrchestrationError("OOF prediction output is incomplete")
    ranked_records = rank_outcome_blind_records(raw_records)
    return build_prediction_freeze(
        ranked_records,
        expected_activity_ids=inputs.activity_ids,
        expected_outer_folds=inputs.outer_folds,
        provenance=inputs.provenance,
    )


# --------------------------------------------------------------------------- Ticket 2 immutable freeze
def _normalise_prediction_record(record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping) or set(record) != _PREDICTION_RECORD_FIELDS:
        raise PredictionFreezeError("prediction record fields are incomplete or unexpected")
    lowered_fields = {str(field).lower() for field in record}
    if any(token in field for token in _FORBIDDEN_OUTCOME_TOKENS for field in lowered_fields):
        raise PredictionFreezeError("prediction freeze contains an outcome-derived field")

    activity_id = record["activity_id"]
    if isinstance(activity_id, bool) or not isinstance(activity_id, (int, str)):
        raise PredictionFreezeError("activity_id must be an integer or string")
    fold = record["outer_fold"]
    if isinstance(fold, bool) or not isinstance(fold, (int, np.integer)):
        raise PredictionFreezeError("outer_fold must be an integer")
    fold = int(fold)

    normalised: dict[str, Any] = {"activity_id": activity_id, "outer_fold": fold}
    for field in _BASE_PREDICTION_FIELDS[2:]:
        try:
            value = float(record[field])
        except (TypeError, ValueError) as exc:
            raise PredictionFreezeError(f"prediction field {field} must be numeric") from exc
        if not math.isfinite(value):
            raise PredictionFreezeError(f"prediction field {field} must be finite")
        normalised[field] = value
    if abs(normalised["qrf_width"] - (normalised["qrf_q90"] - normalised["qrf_q10"])) > 1e-12:
        raise PredictionFreezeError("qrf_width does not equal qrf_q90 - qrf_q10")
    if normalised["qrf_width"] < 0.0:
        raise PredictionFreezeError("qrf_width must be nonnegative")

    tie_hash = record["tie_break_sha256"]
    if tie_hash != _retention_tie_hash(activity_id):
        raise PredictionFreezeError("prediction record tie hash is not the frozen rule")
    normalised["tie_break_sha256"] = tie_hash

    ranks = record["within_fold_ranks"]
    retained = record["retained_coverages"]
    if not isinstance(ranks, Mapping) or set(ranks) != set(_UNCERTAINTY_FIELDS):
        raise PredictionFreezeError("within-fold uncertainty ranks are incomplete")
    if not isinstance(retained, Mapping) or set(retained) != set(_UNCERTAINTY_FIELDS):
        raise PredictionFreezeError("retention metadata is incomplete")
    normalised["within_fold_ranks"] = {}
    normalised["retained_coverages"] = {}
    for method in _UNCERTAINTY_FIELDS:
        rank = ranks[method]
        if isinstance(rank, bool) or not isinstance(rank, (int, np.integer)) or int(rank) < 1:
            raise PredictionFreezeError("within-fold ranks must be positive integers")
        normalised["within_fold_ranks"][method] = int(rank)
        coverage_values = retained[method]
        if not isinstance(coverage_values, (list, tuple)):
            raise PredictionFreezeError("retained coverages must be an ordered sequence")
        coverage_tuple = tuple(float(value) for value in coverage_values)
        if any(value not in C.COVERAGE_LEVELS for value in coverage_tuple):
            raise PredictionFreezeError("retention metadata uses a non-frozen coverage")
        normalised["retained_coverages"][method] = list(coverage_tuple)
    return normalised


def _validate_ranking_metadata(records: Sequence[Mapping[str, Any]]) -> None:
    for fold in range(1, C.N_FOLDS + 1):
        fold_records = [record for record in records if record["outer_fold"] == fold]
        n_fold = len(fold_records)
        if n_fold == 0:
            raise PredictionFreezeError("all five outer folds must be represented")
        for method in _UNCERTAINTY_FIELDS:
            ranks = sorted(record["within_fold_ranks"][method] for record in fold_records)
            if ranks != list(range(1, n_fold + 1)):
                raise PredictionFreezeError("within-fold ranks are not a complete permutation")
            expected_order = sorted(
                fold_records,
                key=lambda record: (
                    record[method],
                    record["tie_break_sha256"],
                    _activity_sort_key(record["activity_id"]),
                ),
            )
            for expected_rank, record in enumerate(expected_order, start=1):
                if record["within_fold_ranks"][method] != expected_rank:
                    raise PredictionFreezeError("uncertainty ranking is not independently within fold")
                expected_coverages = [
                    float(coverage)
                    for coverage in C.COVERAGE_LEVELS
                    if expected_rank <= math.ceil(float(coverage) * n_fold)
                ]
                if record["retained_coverages"][method] != expected_coverages:
                    raise PredictionFreezeError("retention metadata does not match frozen ranks")


def build_prediction_freeze(
    records: Sequence[Mapping[str, Any]],
    *,
    expected_activity_ids: Sequence[Any],
    expected_outer_folds: Sequence[int],
    provenance: Mapping[str, Any],
) -> PredictionFreeze:
    """Validate a complete five-fold OOF table and return canonical immutable bytes."""

    _validate_prediction_provenance(provenance)
    expected_ids = tuple(expected_activity_ids)
    if not expected_ids or len(set(expected_ids)) != len(expected_ids):
        raise PredictionFreezeError("expected primary activity IDs must be unique")
    expected_folds = tuple(int(fold) for fold in expected_outer_folds)
    if len(expected_folds) != len(expected_ids):
        raise PredictionFreezeError("expected fold assignments must align to primary IDs")
    if set(expected_folds) != set(range(1, C.N_FOLDS + 1)):
        raise PredictionFreezeError("expected partition must contain all five outer folds")
    expected_fold_by_id = dict(zip(expected_ids, expected_folds))
    normalised = [_normalise_prediction_record(record) for record in records]
    actual_ids = [record["activity_id"] for record in normalised]
    if len(actual_ids) != len(set(actual_ids)):
        raise PredictionFreezeError("duplicate activity_id in prediction freeze")
    if len(actual_ids) != len(expected_ids) or set(actual_ids) != set(expected_ids):
        raise PredictionFreezeError("prediction freeze has missing or unexpected activity IDs")
    if any(
        record["outer_fold"] != expected_fold_by_id[record["activity_id"]]
        for record in normalised
    ):
        raise PredictionFreezeError("prediction record differs from frozen outer-fold assignment")
    if {record["outer_fold"] for record in normalised} != set(range(1, C.N_FOLDS + 1)):
        raise PredictionFreezeError("partial prediction freeze: all five folds are required")
    _validate_ranking_metadata(normalised)

    ordered = sorted(
        normalised,
        key=lambda record: (record["outer_fold"], _activity_sort_key(record["activity_id"])),
    )
    fold_counts = tuple(
        (fold, sum(record["outer_fold"] == fold for record in ordered))
        for fold in range(1, C.N_FOLDS + 1)
    )
    payload = {
        "fold_counts": {str(fold): count for fold, count in fold_counts},
        "protocol_version": C.PROTOCOL_VERSION,
        "provenance": dict(provenance),
        "records": ordered,
        "row_count": len(ordered),
        "schema_version": PREDICTION_FREEZE_SCHEMA_VERSION,
    }
    canonical_bytes = _canonical_json_bytes(payload)
    digest = hashlib.sha256(canonical_bytes).hexdigest()
    return PredictionFreeze(
        canonical_bytes=canonical_bytes,
        sha256=digest,
        row_count=len(ordered),
        fold_counts=fold_counts,
    )


def _normalise_expected_id_to_fold(
    expected_id_to_fold: Mapping[Any, int],
) -> dict[Any, int]:
    """Validate the authoritative outer-test universe supplied at the seal boundary."""

    if not isinstance(expected_id_to_fold, Mapping) or not expected_id_to_fold:
        raise PredictionFreezeError("authoritative expected ID-to-fold mapping is required")
    normalised: dict[Any, int] = {}
    for activity_id, outer_fold in expected_id_to_fold.items():
        if isinstance(activity_id, bool) or not isinstance(activity_id, (int, str)):
            raise PredictionFreezeError("expected activity IDs must be integers or strings")
        if (
            isinstance(outer_fold, bool)
            or not isinstance(outer_fold, (int, np.integer))
            or int(outer_fold) not in range(1, C.N_FOLDS + 1)
        ):
            raise PredictionFreezeError("expected outer folds must be integers 1 through 5")
        normalised[activity_id] = int(outer_fold)
    if set(normalised.values()) != set(range(1, C.N_FOLDS + 1)):
        raise PredictionFreezeError("expected universe must represent exactly five outer folds")
    return normalised


def _write_prediction_freeze_temp(descriptor: int, canonical_bytes: bytes) -> None:
    """Write, flush, and fsync a uniquely claimed temporary file descriptor."""

    with os.fdopen(descriptor, "wb", closefd=False) as handle:
        handle.write(canonical_bytes)
        handle.flush()
        os.fsync(handle.fileno())


def _finalize_prediction_freeze_no_clobber(temporary_path: Path, destination: Path) -> None:
    """Atomically expose a complete same-filesystem file without replacing a peer.

    ``os.link`` is the commit point: creation of the destination directory entry is
    atomic and fails when that entry already exists on both Windows and POSIX.
    The caller removes the temporary link only after this operation succeeds.
    """

    os.link(temporary_path, destination)


def seal_prediction_freeze(
    freeze: PredictionFreeze,
    path: Path,
    *,
    expected_id_to_fold: Mapping[Any, int],
) -> SealedPredictionFreeze:
    """Validate the expected universe and atomically persist canonical bytes once."""

    if not isinstance(freeze, PredictionFreeze):
        raise PredictionFreezeError("a validated PredictionFreeze is required")
    if hashlib.sha256(freeze.canonical_bytes).hexdigest() != freeze.sha256:
        raise PredictionFreezeError("prediction freeze bytes no longer match their SHA-256")
    try:
        payload = freeze.read_payload()
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise PredictionFreezeError("prediction freeze bytes are not canonical JSON") from exc
    required_payload_fields = {
        "fold_counts",
        "protocol_version",
        "provenance",
        "records",
        "row_count",
        "schema_version",
    }
    if not isinstance(payload, dict) or set(payload) != required_payload_fields:
        raise PredictionFreezeError("prediction freeze payload fields are invalid")
    if (
        payload.get("schema_version") != PREDICTION_FREEZE_SCHEMA_VERSION
        or payload.get("protocol_version") != C.PROTOCOL_VERSION
        or not isinstance(payload.get("records"), list)
    ):
        raise PredictionFreezeError("prediction freeze schema or protocol is invalid")
    expected_universe = _normalise_expected_id_to_fold(expected_id_to_fold)
    records = payload["records"]
    record_ids = [record.get("activity_id") for record in records]
    record_folds = [record.get("outer_fold") for record in records]
    if len(record_ids) != len(set(record_ids)):
        raise PredictionFreezeError("duplicate activity_id at prediction seal boundary")
    if len(record_ids) != len(expected_universe):
        raise PredictionFreezeError("prediction seal row count differs from expected universe")
    if set(record_ids) != set(expected_universe):
        raise PredictionFreezeError("prediction seal activity-ID set differs from expected universe")
    if any(
        not isinstance(outer_fold, int)
        or expected_universe[activity_id] != outer_fold
        for activity_id, outer_fold in zip(record_ids, record_folds)
    ):
        raise PredictionFreezeError("prediction seal ID-to-fold mapping differs from expected universe")
    expected_fold_counts = {
        fold: sum(expected_fold == fold for expected_fold in expected_universe.values())
        for fold in range(1, C.N_FOLDS + 1)
    }
    actual_fold_counts = {
        fold: sum(actual_fold == fold for actual_fold in record_folds)
        for fold in range(1, C.N_FOLDS + 1)
    }
    if actual_fold_counts != expected_fold_counts:
        raise PredictionFreezeError("prediction seal fold counts differ from expected universe")
    rebuilt = build_prediction_freeze(
        records,
        expected_activity_ids=tuple(expected_universe),
        expected_outer_folds=tuple(expected_universe.values()),
        provenance=payload.get("provenance"),
    )
    if (
        rebuilt.canonical_bytes != freeze.canonical_bytes
        or rebuilt.sha256 != freeze.sha256
        or rebuilt.row_count != freeze.row_count
        or rebuilt.fold_counts != freeze.fold_counts
    ):
        raise PredictionFreezeError("prediction freeze object is inconsistent with validated bytes")
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(destination):
        raise PredictionFreezeCollisionError(
            f"prediction freeze already exists: {destination}"
        )

    descriptor: int | None = None
    temporary_path: Path | None = None
    temporary_cleanup_error: OSError | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
        )
        temporary_path = Path(temporary_name)
        _write_prediction_freeze_temp(descriptor, freeze.canonical_bytes)
        os.close(descriptor)
        descriptor = None
        _finalize_prediction_freeze_no_clobber(temporary_path, destination)
    except FileExistsError as exc:
        raise PredictionFreezeCollisionError(
            f"prediction freeze already exists: {destination}"
        ) from exc
    except OSError as exc:
        raise PredictionFreezeError(f"prediction freeze could not be sealed: {destination}") from exc
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
            except OSError as exc:
                temporary_cleanup_error = exc
    if temporary_cleanup_error is not None:
        raise PredictionFreezeError(
            f"prediction freeze temporary artifact could not be removed: {temporary_path}"
        ) from temporary_cleanup_error
    sealed = SealedPredictionFreeze(
        path=destination,
        canonical_bytes=freeze.canonical_bytes,
        sha256=freeze.sha256,
        row_count=freeze.row_count,
        fold_counts=freeze.fold_counts,
    )
    if not sealed.verify():
        raise PredictionFreezeError("persisted prediction freeze verification failed")
    return sealed
