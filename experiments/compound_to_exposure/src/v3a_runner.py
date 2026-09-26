"""Fail-closed v3A scientific runner and post-freeze analysis.

Ticket 1 binds execution authorization to the persisted frozen inputs and provides
a collision-safe internal run ledger.  Ticket 2 adds the five-fold model and
uncertainty orchestration up to an immutable prediction freeze.  Ticket 3 starts
strictly after that seal: retention and matched-random IDs are planned without
outcomes, then outcomes are aligned by activity ID for point evaluation only.
Ticket 4 adds pure in-memory bootstrap inference, secondary CQR, and the two
prespecified sensitivities; it adds no persistence or lifecycle transition.
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
from src.v3a_cohort import assign_scaffold_folds
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
    apply_conformal_correction,
    check_execution_guard,
    compute_descriptor_matrix,
    conformal_correction,
    conformal_proper_train_cal_split,
    cqr_nonconformity_scores,
    fit_physchem_space,
    interval_calibration_summary,
    local_label_sd,
    mae,
    matched_random_rankings,
    neff_inverse,
    physchem_knn_distance,
    qrf_prediction_quantiles,
    recover_forest_weights_many,
    rel_benefit_80,
    rmse,
    scaffold_bootstrap_indices,
    tanimoto_unfamiliarity,
    trapezoidal_naurc,
    tree_dispersion,
    weighted_quantile,
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


class OutcomeEvaluationError(RunnerError):
    """Post-freeze outcome access or evaluation violated the Ticket 3 contract."""


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


@dataclass(frozen=True)
class RetentionSet:
    """One outcome-blind retained-ID set from frozen within-fold ranks."""

    method: str
    coverage: float
    retained_ids: tuple[Any, ...]
    retained_counts_by_fold: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class PostFreezePlan:
    """Outcome-blind Ticket 3 plan derived from a verified prediction seal."""

    sealed_freeze: SealedPredictionFreeze
    freeze_sha256: str
    expected_id_to_fold: tuple[tuple[Any, int], ...]
    retention_sets: tuple[RetentionSet, ...]
    random_retained_ids_by_draw: tuple[tuple[Any, ...], ...]
    random_retained_counts_by_fold: tuple[tuple[int, int], ...]
    random_draw_count: int
    random_seed: int

    def retention(self, method: str, coverage: float) -> RetentionSet:
        for retention_set in self.retention_sets:
            if retention_set.method == method and retention_set.coverage == float(coverage):
                return retention_set
        raise KeyError((method, coverage))


@dataclass(frozen=True)
class CoveragePointResult:
    """Pooled retained-set metrics at one frozen coverage."""

    coverage: float
    retained_n: int
    deferred_n: int
    pooled_rmse: float
    pooled_mae: float
    retained_ids: tuple[Any, ...]
    retained_counts_by_fold: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class CoverageCurveResult:
    """Complete six-point risk-coverage curve for one uncertainty method."""

    method: str
    role: str
    points: tuple[CoveragePointResult, ...]
    naurc: float

    def at(self, coverage: float) -> CoveragePointResult:
        for point in self.points:
            if point.coverage == float(coverage):
                return point
        raise KeyError(coverage)


@dataclass(frozen=True)
class MatchedRandomResult:
    """Outcome-derived pooled RMSE distribution for the frozen random ID plan."""

    draw_count: int
    seed: int
    retained_counts_by_fold: tuple[tuple[int, int], ...]
    mean_rmse: float
    monte_carlo_se: float
    rmse_draws: np.ndarray


@dataclass(frozen=True)
class Ticket3EvaluationResult:
    """In-memory Ticket 3 point results; this is not a sealed scientific result."""

    freeze_sha256: str
    primary_method: str
    primary_coverage: float
    coverage_curves: tuple[CoverageCurveResult, ...]
    qrf80: CoveragePointResult
    matched_random80: MatchedRandomResult
    rel_benefit_80: float

    def curve(self, method: str) -> CoverageCurveResult:
        for curve in self.coverage_curves:
            if curve.method == method:
                return curve
        raise KeyError(method)


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
        record["tie_break_sha256"] = C.retention_tiebreak_hash(record["activity_id"])
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
    if tie_hash != C.retention_tiebreak_hash(activity_id):
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


# --------------------------------------------------------------------------- Ticket 3 post-freeze planning
def _validated_sealed_payload(
    sealed_freeze: SealedPredictionFreeze,
    expected_id_to_fold: Mapping[Any, int],
) -> tuple[dict[str, Any], dict[Any, int]]:
    """Verify the persisted seal and authoritative universe without reading outcomes."""

    if not isinstance(sealed_freeze, SealedPredictionFreeze):
        raise OutcomeEvaluationError("outcome evaluation requires a sealed prediction freeze")
    if not sealed_freeze.verify():
        raise OutcomeEvaluationError("prediction freeze seal or hash verification failed")
    if hashlib.sha256(sealed_freeze.canonical_bytes).hexdigest() != sealed_freeze.sha256:
        raise OutcomeEvaluationError("prediction freeze bytes no longer match their SHA-256")
    try:
        expected = _normalise_expected_id_to_fold(expected_id_to_fold)
        payload = json.loads(sealed_freeze.canonical_bytes.decode("utf-8"))
    except (PredictionFreezeError, UnicodeError, json.JSONDecodeError) as exc:
        raise OutcomeEvaluationError("sealed prediction freeze is invalid") from exc

    required_fields = {
        "fold_counts",
        "protocol_version",
        "provenance",
        "records",
        "row_count",
        "schema_version",
    }
    if not isinstance(payload, dict) or set(payload) != required_fields:
        raise OutcomeEvaluationError("sealed prediction freeze payload fields are invalid")
    records = payload.get("records")
    if not isinstance(records, list):
        raise OutcomeEvaluationError("sealed prediction freeze records are invalid")
    try:
        rebuilt = build_prediction_freeze(
            records,
            expected_activity_ids=tuple(expected),
            expected_outer_folds=tuple(expected.values()),
            provenance=payload.get("provenance"),
        )
    except PredictionFreezeError as exc:
        raise OutcomeEvaluationError("sealed prediction freeze failed downstream validation") from exc
    if (
        rebuilt.canonical_bytes != sealed_freeze.canonical_bytes
        or rebuilt.sha256 != sealed_freeze.sha256
        or rebuilt.row_count != sealed_freeze.row_count
        or rebuilt.fold_counts != sealed_freeze.fold_counts
    ):
        raise OutcomeEvaluationError("sealed prediction freeze metadata is inconsistent")
    if rebuilt.row_count != len(expected):
        raise OutcomeEvaluationError("sealed prediction freeze universe is incomplete")
    return payload, expected


def _retention_sets_from_records(records: Sequence[Mapping[str, Any]]) -> tuple[RetentionSet, ...]:
    retention_sets: list[RetentionSet] = []
    for method in _UNCERTAINTY_FIELDS:
        for coverage in C.COVERAGE_LEVELS:
            retained_ids = tuple(
                record["activity_id"]
                for record in records
                if float(coverage) in record["retained_coverages"][method]
            )
            counts = tuple(
                (
                    fold,
                    sum(
                        record["outer_fold"] == fold
                        and float(coverage) in record["retained_coverages"][method]
                        for record in records
                    ),
                )
                for fold in range(1, C.N_FOLDS + 1)
            )
            expected_counts = tuple(
                (
                    fold,
                    math.ceil(
                        float(coverage)
                        * sum(record["outer_fold"] == fold for record in records)
                    ),
                )
                for fold in range(1, C.N_FOLDS + 1)
            )
            if counts != expected_counts or len(retained_ids) != sum(count for _, count in counts):
                raise OutcomeEvaluationError("frozen retention metadata violates the ceil rule")
            retention_sets.append(
                RetentionSet(
                    method=method,
                    coverage=float(coverage),
                    retained_ids=retained_ids,
                    retained_counts_by_fold=counts,
                )
            )
    return tuple(retention_sets)


def _plan_random_retention(
    records: Sequence[Mapping[str, Any]],
    qrf80: RetentionSet,
) -> tuple[tuple[Any, ...], ...]:
    """Use the hardened random-ranking primitive on ID-independent integer tokens."""

    if C.N_RANDOM_DEFERRALS != 10_000 or C.MASTER_SEED != 20260923:
        raise OutcomeEvaluationError("matched-random draw count or seed differs from the SAP")
    fold_tokens: dict[int, list[int]] = {}
    id_by_token: dict[int, Any] = {}
    for token, record in enumerate(records):
        fold = int(record["outer_fold"])
        fold_tokens.setdefault(fold, []).append(token)
        id_by_token[token] = record["activity_id"]
    samples = matched_random_rankings(
        fold_tokens,
        n_random=10_000,
        seed=20260923,
        coverage=C.PRIMARY_COVERAGE,
    )
    expected_counts = dict(qrf80.retained_counts_by_fold)
    draws: list[tuple[Any, ...]] = []
    for draw_index in range(10_000):
        pooled: list[Any] = []
        for fold in range(1, C.N_FOLDS + 1):
            selected_tokens = sorted(int(token) for token in samples[fold][draw_index])
            if len(selected_tokens) != expected_counts[fold]:
                raise OutcomeEvaluationError("matched-random fold count differs from QRF80")
            pooled.extend(id_by_token[token] for token in selected_tokens)
        draws.append(tuple(pooled))
    return tuple(draws)


def prepare_postfreeze_plan(
    sealed_freeze: SealedPredictionFreeze,
    *,
    expected_id_to_fold: Mapping[Any, int],
) -> PostFreezePlan:
    """Freeze deterministic and matched-random retention IDs before outcome access."""

    payload, expected = _validated_sealed_payload(sealed_freeze, expected_id_to_fold)
    records = payload["records"]
    retention_sets = _retention_sets_from_records(records)
    qrf80 = next(
        item
        for item in retention_sets
        if item.method == "qrf_width" and item.coverage == C.PRIMARY_COVERAGE
    )
    random_draws = _plan_random_retention(records, qrf80)
    return PostFreezePlan(
        sealed_freeze=sealed_freeze,
        freeze_sha256=sealed_freeze.sha256,
        expected_id_to_fold=tuple(expected.items()),
        retention_sets=retention_sets,
        random_retained_ids_by_draw=random_draws,
        random_retained_counts_by_fold=qrf80.retained_counts_by_fold,
        random_draw_count=10_000,
        random_seed=20260923,
    )


def _validate_postfreeze_plan(plan: PostFreezePlan) -> tuple[dict[str, Any], dict[Any, int]]:
    if not isinstance(plan, PostFreezePlan):
        raise OutcomeEvaluationError("outcome evaluation requires an outcome-blind post-freeze plan")
    payload, expected = _validated_sealed_payload(
        plan.sealed_freeze, dict(plan.expected_id_to_fold)
    )
    if plan.freeze_sha256 != plan.sealed_freeze.sha256:
        raise OutcomeEvaluationError("post-freeze plan does not match the verified freeze hash")
    expected_retention = _retention_sets_from_records(payload["records"])
    if plan.retention_sets != expected_retention:
        raise OutcomeEvaluationError("post-freeze retention IDs differ from frozen metadata")
    if (
        plan.random_draw_count != 10_000
        or plan.random_seed != 20260923
        or len(plan.random_retained_ids_by_draw) != 10_000
    ):
        raise OutcomeEvaluationError("post-freeze random plan differs from the SAP")
    expected_qrf80 = next(
        item
        for item in expected_retention
        if item.method == "qrf_width" and item.coverage == C.PRIMARY_COVERAGE
    )
    expected_counts = dict(expected_qrf80.retained_counts_by_fold)
    if dict(plan.random_retained_counts_by_fold) != expected_counts:
        raise OutcomeEvaluationError("random plan counts do not match QRF80")
    expected_random_draws = _plan_random_retention(payload["records"], expected_qrf80)
    if plan.random_retained_ids_by_draw != expected_random_draws:
        raise OutcomeEvaluationError(
            "post-freeze random plan does not match the canonical seeded draw stream"
        )
    return payload, expected


# --------------------------------------------------------------------------- Ticket 3 outcome attachment/evaluation
def _outcome_rows(outcomes: Any) -> list[Mapping[str, Any]]:
    if isinstance(outcomes, pd.DataFrame):
        return outcomes.to_dict(orient="records")
    if isinstance(outcomes, Mapping):
        if "activity_id" in outcomes:
            return [outcomes]
        rows: list[Mapping[str, Any]] = []
        for activity_id, value in outcomes.items():
            if isinstance(value, Mapping):
                row = dict(value)
                supplied_id = row.setdefault("activity_id", activity_id)
                if supplied_id != activity_id:
                    raise OutcomeEvaluationError("outcome mapping key and activity_id disagree")
                rows.append(row)
            else:
                rows.append({"activity_id": activity_id, "observed_y": value})
        return rows
    if isinstance(outcomes, (str, bytes)):
        raise OutcomeEvaluationError("outcomes must be ID-keyed records")
    try:
        rows = list(outcomes)
    except TypeError as exc:
        raise OutcomeEvaluationError("outcomes must be ID-keyed records") from exc
    if any(not isinstance(row, Mapping) for row in rows):
        raise OutcomeEvaluationError("each outcome row must be a mapping")
    return rows


def _align_outcomes_by_activity_id(
    outcomes: Any,
    expected_id_to_fold: Mapping[Any, int],
) -> dict[Any, float]:
    rows = _outcome_rows(outcomes)
    observed_by_id: dict[Any, float] = {}
    for row in rows:
        if "activity_id" not in row:
            raise OutcomeEvaluationError("outcome row is missing activity_id")
        activity_id = row["activity_id"]
        if isinstance(activity_id, np.integer):
            activity_id = int(activity_id)
        if isinstance(activity_id, bool) or not isinstance(activity_id, (int, str)):
            raise OutcomeEvaluationError("outcome activity_id must be an integer or string")
        if activity_id in observed_by_id:
            raise OutcomeEvaluationError("duplicate outcome activity_id")
        outcome_fields = [field for field in ("observed_y", "y_test") if field in row]
        if len(outcome_fields) != 1:
            raise OutcomeEvaluationError("outcome row must contain exactly one observed value")
        if "outer_fold" in row:
            supplied_fold = row["outer_fold"]
            if (
                activity_id in expected_id_to_fold
                and (
                    isinstance(supplied_fold, bool)
                    or not isinstance(supplied_fold, (int, np.integer))
                    or int(supplied_fold) != expected_id_to_fold[activity_id]
                )
            ):
                raise OutcomeEvaluationError("outcome outer_fold differs from the sealed freeze")
        try:
            observed = float(row[outcome_fields[0]])
        except (TypeError, ValueError) as exc:
            raise OutcomeEvaluationError("outcome values must be numeric") from exc
        if not math.isfinite(observed):
            raise OutcomeEvaluationError("outcome values must be finite")
        observed_by_id[activity_id] = observed
    expected_ids = set(expected_id_to_fold)
    actual_ids = set(observed_by_id)
    if actual_ids != expected_ids:
        missing = expected_ids - actual_ids
        detail = "missing" if missing else "extra"
        raise OutcomeEvaluationError(f"outcome ID universe has {detail} activity IDs")
    return observed_by_id


def evaluate_postfreeze(
    plan: PostFreezePlan,
    outcomes: Any,
) -> Ticket3EvaluationResult:
    """Attach ID-keyed outcomes and compute only the frozen Ticket 3 point analyses."""

    # Full seal/plan validation deliberately precedes even iteration over outcomes.
    payload, expected = _validate_postfreeze_plan(plan)
    observed_by_id = _align_outcomes_by_activity_id(outcomes, expected)
    prediction_by_id = {
        record["activity_id"]: float(record["rf_prediction"])
        for record in payload["records"]
    }

    curves: list[CoverageCurveResult] = []
    for method in _UNCERTAINTY_FIELDS:
        points: list[CoveragePointResult] = []
        for coverage in C.COVERAGE_LEVELS:
            retention = plan.retention(method, coverage)
            retained_ids = retention.retained_ids
            y_true = np.asarray([observed_by_id[activity_id] for activity_id in retained_ids])
            y_pred = np.asarray([prediction_by_id[activity_id] for activity_id in retained_ids])
            points.append(
                CoveragePointResult(
                    coverage=float(coverage),
                    retained_n=len(retained_ids),
                    deferred_n=len(expected) - len(retained_ids),
                    pooled_rmse=rmse(y_true, y_pred),
                    pooled_mae=mae(y_true, y_pred),
                    retained_ids=retained_ids,
                    retained_counts_by_fold=retention.retained_counts_by_fold,
                )
            )
        curves.append(
            CoverageCurveResult(
                method=method,
                role="PRIMARY" if method == "qrf_width" else "SECONDARY",
                points=tuple(points),
                naurc=trapezoidal_naurc(
                    np.asarray([point.coverage for point in points]),
                    np.asarray([point.pooled_rmse for point in points]),
                ),
            )
        )

    random_draws = np.empty(plan.random_draw_count, dtype=np.float64)
    for draw_index, retained_ids in enumerate(plan.random_retained_ids_by_draw):
        y_true = np.asarray([observed_by_id[activity_id] for activity_id in retained_ids])
        y_pred = np.asarray([prediction_by_id[activity_id] for activity_id in retained_ids])
        random_draws[draw_index] = rmse(y_true, y_pred)
    random_mean = float(random_draws.mean())
    random_mcse = float(random_draws.std(ddof=1) / np.sqrt(plan.random_draw_count))
    random_result = MatchedRandomResult(
        draw_count=plan.random_draw_count,
        seed=plan.random_seed,
        retained_counts_by_fold=plan.random_retained_counts_by_fold,
        mean_rmse=random_mean,
        monte_carlo_se=random_mcse,
        rmse_draws=_immutable_array(random_draws),
    )
    qrf_curve = next(curve for curve in curves if curve.method == "qrf_width")
    qrf80 = qrf_curve.at(C.PRIMARY_COVERAGE)
    return Ticket3EvaluationResult(
        freeze_sha256=plan.freeze_sha256,
        primary_method="qrf_width",
        primary_coverage=C.PRIMARY_COVERAGE,
        coverage_curves=tuple(curves),
        qrf80=qrf80,
        matched_random80=random_result,
        rel_benefit_80=rel_benefit_80(random_mean, qrf80.pooled_rmse),
    )


def classify_rel_benefit_80(
    point_estimate: float,
    ci_lower: float,
    ci_upper: float,
) -> str:
    """Apply the frozen three-state rule to a future Ticket 4 bootstrap CI."""

    try:
        point = float(point_estimate)
        lower = float(ci_lower)
        upper = float(ci_upper)
    except (TypeError, ValueError) as exc:
        raise ValueError("point estimate and confidence bounds must be numeric") from exc
    if not all(math.isfinite(value) for value in (point, lower, upper)) or lower > upper:
        raise ValueError("point estimate and ordered confidence bounds must be finite")
    if point >= C.PRACTICAL_THRESHOLD and lower > 0.0:
        return "SUPPORTED_OPERATIONAL_SIGNAL"
    if upper < C.PRACTICAL_THRESHOLD:
        return "EVIDENCE_BELOW_PRACTICAL_THRESHOLD"
    return "INCONCLUSIVE"


# --------------------------------------------------------------------------- Ticket 4 inference
BOOTSTRAP_RNG_PROVENANCE = (
    "SeedSequence([20260923,b])->uint32->RandomState->permutation"
)
CQR_SPLIT_ALGORITHM = "conformal_proper_train_cal_split_v1_hash_group_overshoot"


@dataclass(frozen=True)
class BootstrapReplicateResult:
    """One downstream scaffold-bootstrap replicate with multiplicity retained."""

    replicate_index: int
    occurrence_ids: tuple[tuple[int, int, int, int], ...]
    qrf_retained_occurrence_ids: tuple[tuple[int, int, int, int], ...]
    fold_candidate_counts: tuple[tuple[int, int], ...]
    fold_retained_counts: tuple[tuple[int, int], ...]
    rmse_qrf80: float
    rmse_random80: float
    rel_benefit_80: float


@dataclass(frozen=True)
class BootstrapInferenceResult:
    """Percentile inference from the frozen downstream bootstrap procedure."""

    replicates: tuple[BootstrapReplicateResult, ...]
    ci_lower: float
    ci_upper: float
    confidence_level: float
    percentile_method: str
    bootstrap_replicates: int
    matched_random_draws_per_replicate: int
    base_seed: int
    nested_rng_provenance: str


@dataclass(frozen=True)
class PrimaryInferenceResult:
    """Primary point estimate, CI, and the frozen three-state classification."""

    point_estimate: float
    ci_lower: float
    ci_upper: float
    classification: str
    bootstrap: BootstrapInferenceResult


@dataclass(frozen=True)
class CQRRowResult:
    activity_id: Any
    outer_fold: int
    nominal_coverage: float
    raw_lower_endpoint: float
    raw_upper_endpoint: float
    raw_corrected_span: float
    empty_set: bool
    finite_set: bool
    infinite_set: bool
    covered: bool
    reported_width: float


@dataclass(frozen=True)
class CQRFoldMetadata:
    outer_fold: int
    n_proper: int
    n_cal: int
    nominal_coverage: float
    alpha: float
    k: int
    qhat: float
    qhat_is_finite: bool
    n_evaluated: int
    ordinary_finite_interval_count: int
    empty_set_count: int
    infinite_set_count: int
    empirical_marginal_coverage: float
    mean_prediction_set_width: float
    median_prediction_set_width: float
    split_helper: str
    split_salt: str
    calibration_fraction: float
    split_algorithm: str


@dataclass(frozen=True)
class CQRCoverageResult:
    nominal_coverage: float
    empirical_marginal_coverage: float
    n_evaluated: int
    mean_final_set_width: float
    median_final_set_width: float
    ordinary_finite_interval_count: int
    empty_set_count: int
    infinite_set_count: int
    rows: tuple[CQRRowResult, ...]


@dataclass(frozen=True)
class CQRResult:
    """Secondary marginal-calibration result; never a triage ranking."""

    role: str
    marginal_label: str
    canonical_triage_ranking: str
    base_intervals: tuple[tuple[float, float, float], ...]
    coverages: tuple[CQRCoverageResult, ...]
    fold_metadata: tuple[CQRFoldMetadata, ...]

    def at(self, nominal_coverage: float) -> CQRCoverageResult:
        for result in self.coverages:
            if result.nominal_coverage == float(nominal_coverage):
                return result
        raise KeyError(nominal_coverage)


@dataclass(frozen=True)
class SensitivityResult:
    """In-memory sensitivity result without lifecycle or persistence behavior."""

    name: str
    interpretation_labels: tuple[str, ...]
    cohort_n: int
    coverage_curves: tuple[CoverageCurveResult, ...]
    qrf80: CoveragePointResult
    matched_random80: MatchedRandomResult
    rel_benefit_80: float
    bootstrap: BootstrapInferenceResult
    oof_records: tuple[Mapping[str, Any], ...] = ()
    provenance: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class SensitivityAPredictionInputs:
    """Separate strict-interior five-fold inputs and training labels."""

    inputs: OutcomeBlindInputs
    outcomes_by_id: Mapping[Any, float]


def _ticket4_rows(
    records: Sequence[Mapping[str, Any]],
    *,
    require_outcome: bool,
) -> list[dict[str, Any]]:
    """Return canonical detached rows for downstream Ticket 4 calculations."""

    required = {"activity_id", "outer_fold", "scaffold_key", "qrf_width", "rf_prediction"}
    if require_outcome:
        required.add("observed_y")
    rows = [dict(record) for record in records]
    if not rows:
        raise OutcomeEvaluationError("Ticket 4 records are empty")
    seen: set[Any] = set()
    for row in rows:
        if not required.issubset(row):
            raise OutcomeEvaluationError("Ticket 4 record fields are incomplete")
        activity_id = row["activity_id"]
        if activity_id in seen:
            raise OutcomeEvaluationError("Ticket 4 activity IDs must be unique before resampling")
        seen.add(activity_id)
        fold = row["outer_fold"]
        if isinstance(fold, bool) or not isinstance(fold, (int, np.integer)):
            raise OutcomeEvaluationError("Ticket 4 outer folds must be integers")
        row["outer_fold"] = int(fold)
        if not isinstance(row["scaffold_key"], str) or not row["scaffold_key"]:
            raise OutcomeEvaluationError("Ticket 4 scaffold keys must be nonempty strings")
        for field in ("qrf_width", "rf_prediction"):
            row[field] = float(row[field])
            if not math.isfinite(row[field]):
                raise OutcomeEvaluationError(f"Ticket 4 {field} values must be finite")
        if require_outcome:
            row["observed_y"] = float(row["observed_y"])
            if not math.isfinite(row["observed_y"]):
                raise OutcomeEvaluationError("Ticket 4 outcomes must be finite")
    rows.sort(
        key=lambda row: (
            row["outer_fold"],
            row["scaffold_key"],
            C.retention_tiebreak_hash(row["activity_id"]),
            _activity_sort_key(row["activity_id"]),
        )
    )
    return rows


def _bootstrap_occurrences(
    rows: Sequence[Mapping[str, Any]],
    sample_positions: np.ndarray,
    replicate_index: int,
) -> list[dict[str, Any]]:
    """Attach the frozen deterministic identity to each sampled row occurrence."""

    group_sizes: dict[tuple[int, str], int] = {}
    for row in rows:
        key = (int(row["outer_fold"]), str(row["scaffold_key"]))
        group_sizes[key] = group_sizes.get(key, 0) + 1
    occurrences: list[dict[str, Any]] = []
    sample = [int(position) for position in np.asarray(sample_positions).reshape(-1)]
    cursor = 0
    draw_positions: dict[int, int] = {}
    while cursor < len(sample):
        row = rows[sample[cursor]]
        fold = int(row["outer_fold"])
        scaffold = str(row["scaffold_key"])
        size = group_sizes[(fold, scaffold)]
        chunk = sample[cursor:cursor + size]
        if len(chunk) != size or any(
            int(rows[position]["outer_fold"]) != fold
            or str(rows[position]["scaffold_key"]) != scaffold
            for position in chunk
        ):
            raise OutcomeEvaluationError("bootstrap scaffold occurrence is not contiguous")
        draw_position = draw_positions.get(fold, 0)
        for within_position, row_position in enumerate(chunk):
            source = rows[row_position]
            occurrence_id = (
                int(replicate_index), fold, draw_position, within_position
            )
            occurrences.append(
                {
                    "row_position": row_position,
                    "activity_id": source["activity_id"],
                    "outer_fold": fold,
                    "scaffold_key": scaffold,
                    "occurrence_id": occurrence_id,
                }
            )
        draw_positions[fold] = draw_position + 1
        cursor += size
    return occurrences


def _retention_for_occurrences(
    rows: Sequence[Mapping[str, Any]],
    occurrences: Sequence[Mapping[str, Any]],
    *,
    coverage: float = C.PRIMARY_COVERAGE,
) -> tuple[tuple[int, ...], tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]:
    if not 0.0 < coverage <= 1.0:
        raise ValueError("coverage must lie in (0, 1]")
    selected: list[int] = []
    candidates_by_fold: list[tuple[int, int]] = []
    retained_by_fold: list[tuple[int, int]] = []
    for fold in sorted({int(item["outer_fold"]) for item in occurrences}):
        candidates = [
            index for index, item in enumerate(occurrences)
            if int(item["outer_fold"]) == fold
        ]
        k = math.ceil(float(coverage) * len(candidates))
        ranked = sorted(
            candidates,
            key=lambda index: (
                float(rows[int(occurrences[index]["row_position"])]["qrf_width"]),
                C.retention_tiebreak_hash(occurrences[index]["activity_id"]),
                tuple(occurrences[index]["occurrence_id"]),
            ),
        )
        selected.extend(ranked[:k])
        candidates_by_fold.append((fold, len(candidates)))
        retained_by_fold.append((fold, k))
    return tuple(selected), tuple(candidates_by_fold), tuple(retained_by_fold)


def nested_bootstrap_seed(replicate_index: int, *, base_seed: int = C.MASTER_SEED) -> int:
    """Return the pinned uint32-derived nested seed for zero-based replicate ``b``."""

    if isinstance(replicate_index, bool) or int(replicate_index) != replicate_index:
        raise ValueError("replicate index must be an integer")
    if int(replicate_index) < 0:
        raise ValueError("replicate index must be nonnegative")
    sequence = np.random.SeedSequence([int(base_seed), int(replicate_index)])
    return int(sequence.generate_state(1, dtype=np.uint32)[0])


def _random_occurrence_draws(
    occurrences: Sequence[Mapping[str, Any]],
    retained_counts_by_fold: Sequence[tuple[int, int]],
    *,
    replicate_index: int,
    n_random: int,
    base_seed: int,
    sensitivity_b_one_based: bool = False,
) -> tuple[tuple[int, ...], ...]:
    """Literal nested matched-random reference path with one sequential RNG."""

    if n_random < 1:
        raise ValueError("matched-random draw count must be positive")
    seed_index = replicate_index + 1 if sensitivity_b_one_based else replicate_index
    rng = np.random.RandomState(nested_bootstrap_seed(seed_index, base_seed=base_seed))
    counts = dict(retained_counts_by_fold)
    candidates = {
        fold: tuple(
            sorted(
                (
                    index for index, occurrence in enumerate(occurrences)
                    if int(occurrence["outer_fold"]) == fold
                ),
                key=lambda index: tuple(occurrences[index]["occurrence_id"]),
            )
        )
        for fold in sorted(counts)
    }
    draws: list[tuple[int, ...]] = []
    for _ in range(n_random):
        pooled: list[int] = []
        for fold in sorted(candidates):
            fold_candidates = candidates[fold]
            k = counts[fold]
            if k > len(fold_candidates):
                raise OutcomeEvaluationError("random retained count exceeds fold candidates")
            permutation = rng.permutation(len(fold_candidates))[:k]
            pooled.extend(fold_candidates[int(position)] for position in permutation)
        draws.append(tuple(pooled))
    return tuple(draws)


def primary_bootstrap_plan(
    records: Sequence[Mapping[str, Any]],
    *,
    n_bootstrap: int = C.N_BOOTSTRAP,
    n_random: int = C.N_RANDOM_DEFERRALS,
    seed: int = C.MASTER_SEED,
) -> tuple[dict[str, Any], ...]:
    """Build a literal complete outcome-blind plan for reduced test fixtures.

    This reference path materialises every matched-random selection so tests can
    compare plans directly.  The production-facing ``run_primary_bootstrap``
    path below streams those draws and has bounded memory.
    """

    if n_bootstrap < 1 or n_random < 1:
        raise ValueError("bootstrap and matched-random counts must be positive")
    rows = _ticket4_rows(records, require_outcome=False)
    frame = pd.DataFrame(
        {
            "activity_id": [row["activity_id"] for row in rows],
            "outer_fold": [row["outer_fold"] for row in rows],
            "scaffold_key": [row["scaffold_key"] for row in rows],
        }
    )
    samples = scaffold_bootstrap_indices(frame, n_bootstrap=n_bootstrap, seed=seed)
    plans: list[dict[str, Any]] = []
    for replicate_index, sample in enumerate(samples):
        occurrences = _bootstrap_occurrences(rows, sample, replicate_index)
        selected, candidate_counts, retained_counts = _retention_for_occurrences(
            rows, occurrences
        )
        random_draws = _random_occurrence_draws(
            occurrences,
            retained_counts,
            replicate_index=replicate_index,
            n_random=n_random,
            base_seed=seed,
        )
        plans.append(
            {
                "replicate_index": replicate_index,
                "occurrences": tuple(occurrences),
                "qrf_selected": selected,
                "candidate_counts": candidate_counts,
                "retained_counts": retained_counts,
                "random_draws": random_draws,
                "nested_seed": nested_bootstrap_seed(replicate_index, base_seed=seed),
            }
        )
    return tuple(plans)


def evaluate_primary_bootstrap_plan(
    records: Sequence[Mapping[str, Any]],
    plan: Sequence[Mapping[str, Any]],
    *,
    n_random: int,
    seed: int = C.MASTER_SEED,
    percentile_method: str = "linear",
) -> BootstrapInferenceResult:
    """Attach outcomes after planning and evaluate bootstrap multiplicities literally."""

    rows = _ticket4_rows(records, require_outcome=True)
    by_id = {row["activity_id"]: row for row in rows}
    results: list[BootstrapReplicateResult] = []
    for expected_index, replicate in enumerate(plan):
        if int(replicate["replicate_index"]) != expected_index:
            raise OutcomeEvaluationError("bootstrap plan replicate order is invalid")
        occurrences = tuple(replicate["occurrences"])
        if any(occurrence["activity_id"] not in by_id for occurrence in occurrences):
            raise OutcomeEvaluationError("bootstrap plan differs from outcome activity IDs")

        def errors(indices: Sequence[int]) -> np.ndarray:
            values = []
            for occurrence_index in indices:
                activity_id = occurrences[int(occurrence_index)]["activity_id"]
                row = by_id[activity_id]
                values.append((row["observed_y"] - row["rf_prediction"]) ** 2)
            if not values:
                raise OutcomeEvaluationError("bootstrap selection is empty")
            return np.asarray(values, dtype=np.float64)

        qrf_rmse = float(np.sqrt(np.mean(errors(replicate["qrf_selected"]))))
        random_draws = tuple(replicate["random_draws"])
        if len(random_draws) != n_random:
            raise OutcomeEvaluationError("bootstrap random draw count is inconsistent")
        random_rmses = np.asarray(
            [float(np.sqrt(np.mean(errors(draw)))) for draw in random_draws],
            dtype=np.float64,
        )
        random_mean = float(random_rmses.mean())
        benefit = rel_benefit_80(random_mean, qrf_rmse)
        results.append(
            BootstrapReplicateResult(
                replicate_index=expected_index,
                occurrence_ids=tuple(
                    tuple(occurrence["occurrence_id"]) for occurrence in occurrences
                ),
                qrf_retained_occurrence_ids=tuple(
                    tuple(occurrences[index]["occurrence_id"])
                    for index in replicate["qrf_selected"]
                ),
                fold_candidate_counts=tuple(replicate["candidate_counts"]),
                fold_retained_counts=tuple(replicate["retained_counts"]),
                rmse_qrf80=qrf_rmse,
                rmse_random80=random_mean,
                rel_benefit_80=benefit,
            )
        )
    values = np.asarray([item.rel_benefit_80 for item in results], dtype=np.float64)
    lower, upper = np.percentile(values, [2.5, 97.5], method=percentile_method)
    return BootstrapInferenceResult(
        replicates=tuple(results),
        ci_lower=float(lower),
        ci_upper=float(upper),
        confidence_level=0.95,
        percentile_method=percentile_method,
        bootstrap_replicates=len(results),
        matched_random_draws_per_replicate=n_random,
        base_seed=int(seed),
        nested_rng_provenance=BOOTSTRAP_RNG_PROVENANCE,
    )


def run_primary_bootstrap(
    records: Sequence[Mapping[str, Any]],
    *,
    n_bootstrap: int = C.N_BOOTSTRAP,
    n_random: int = C.N_RANDOM_DEFERRALS,
    seed: int = C.MASTER_SEED,
    percentile_method: str = "linear",
) -> BootstrapInferenceResult:
    """Run the frozen bootstrap while streaming nested draws in bounded memory."""

    if n_bootstrap < 1 or n_random < 1:
        raise ValueError("bootstrap and matched-random counts must be positive")
    rows = _ticket4_rows(records, require_outcome=True)
    frame = pd.DataFrame(
        {
            "activity_id": [row["activity_id"] for row in rows],
            "outer_fold": [row["outer_fold"] for row in rows],
            "scaffold_key": [row["scaffold_key"] for row in rows],
        }
    )
    samples = scaffold_bootstrap_indices(frame, n_bootstrap=n_bootstrap, seed=seed)
    results: list[BootstrapReplicateResult] = []
    for replicate_index, sample in enumerate(samples):
        occurrences = _bootstrap_occurrences(rows, sample, replicate_index)
        selected, candidate_counts, retained_counts = _retention_for_occurrences(
            rows, occurrences
        )
        squared_errors = np.asarray(
            [
                (
                    rows[int(occurrence["row_position"])]["observed_y"]
                    - rows[int(occurrence["row_position"])]["rf_prediction"]
                ) ** 2
                for occurrence in occurrences
            ],
            dtype=np.float64,
        )
        qrf_rmse = float(np.sqrt(np.mean(squared_errors[list(selected)])))
        seed_value = nested_bootstrap_seed(replicate_index, base_seed=seed)
        rng = np.random.RandomState(seed_value)
        counts = dict(retained_counts)
        candidates = {
            fold: tuple(
                sorted(
                    (
                        index for index, occurrence in enumerate(occurrences)
                        if int(occurrence["outer_fold"]) == fold
                    ),
                    key=lambda index: tuple(occurrences[index]["occurrence_id"]),
                )
            )
            for fold in sorted(counts)
        }
        random_rmses = np.empty(n_random, dtype=np.float64)
        for draw_index in range(n_random):
            pooled: list[int] = []
            for fold in sorted(candidates):
                fold_candidates = candidates[fold]
                permutation = rng.permutation(len(fold_candidates))[:counts[fold]]
                pooled.extend(fold_candidates[int(position)] for position in permutation)
            random_rmses[draw_index] = float(np.sqrt(np.mean(squared_errors[pooled])))
        random_mean = float(random_rmses.mean())
        results.append(
            BootstrapReplicateResult(
                replicate_index=replicate_index,
                occurrence_ids=tuple(tuple(item["occurrence_id"]) for item in occurrences),
                qrf_retained_occurrence_ids=tuple(
                    tuple(occurrences[index]["occurrence_id"]) for index in selected
                ),
                fold_candidate_counts=candidate_counts,
                fold_retained_counts=retained_counts,
                rmse_qrf80=qrf_rmse,
                rmse_random80=random_mean,
                rel_benefit_80=rel_benefit_80(random_mean, qrf_rmse),
            )
        )
    values = np.asarray([item.rel_benefit_80 for item in results], dtype=np.float64)
    lower, upper = np.percentile(values, [2.5, 97.5], method=percentile_method)
    return BootstrapInferenceResult(
        replicates=tuple(results),
        ci_lower=float(lower),
        ci_upper=float(upper),
        confidence_level=0.95,
        percentile_method=percentile_method,
        bootstrap_replicates=n_bootstrap,
        matched_random_draws_per_replicate=n_random,
        base_seed=seed,
        nested_rng_provenance=BOOTSTRAP_RNG_PROVENANCE,
    )


def primary_inference(
    point_estimate: float,
    bootstrap: BootstrapInferenceResult,
) -> PrimaryInferenceResult:
    """Wire the existing pure classifier to the primary percentile interval."""

    if not isinstance(bootstrap, BootstrapInferenceResult):
        raise TypeError("bootstrap must be a BootstrapInferenceResult")
    return PrimaryInferenceResult(
        point_estimate=float(point_estimate),
        ci_lower=bootstrap.ci_lower,
        ci_upper=bootstrap.ci_upper,
        classification=classify_rel_benefit_80(
            point_estimate, bootstrap.ci_lower, bootstrap.ci_upper
        ),
        bootstrap=bootstrap,
    )


def _blind_query_rows(rows: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    forbidden = {"observed_y", "y_test", "observed_clint", "standard_value"}
    return tuple(
        {key: value for key, value in row.items() if key not in forbidden}
        for row in rows
    )


class ProperTrainingQRFIntervalModel:
    """Frozen QRF fit used by the production CQR path for one outer fold."""

    def __init__(self, proper_rows: tuple[Mapping[str, Any], ...]):
        if not proper_rows or any("features" not in row or "observed_y" not in row for row in proper_rows):
            raise OutcomeEvaluationError("CQR proper rows require features and training outcomes")
        self._features = np.asarray([row["features"] for row in proper_rows])
        self._outcomes = np.asarray([row["observed_y"] for row in proper_rows], dtype=np.float64)
        if (
            self._features.ndim != 2
            or self._features.shape[1] != C.MORGAN_SPEC["nBits"]
            or not np.isin(self._features, (0, 1)).all()
            or not np.isfinite(self._outcomes).all()
        ):
            raise OutcomeEvaluationError("CQR proper-training representation is not frozen ECFP4")
        self._rf = C.make_frozen_rf()
        _validate_frozen_rf_configuration(self._rf)
        self._rf.fit(self._features, self._outcomes)

    def predict_intervals(
        self,
        query_rows: Sequence[Mapping[str, Any]],
        quantile_pairs: Sequence[tuple[float, float, float]],
    ) -> dict[float, tuple[np.ndarray, np.ndarray]]:
        if any("features" not in row for row in query_rows):
            raise OutcomeEvaluationError("CQR query rows require frozen ECFP4 features")
        query = np.asarray([row["features"] for row in query_rows])
        if query.ndim != 2 or query.shape[1] != C.MORGAN_SPEC["nBits"] or not np.isin(query, (0, 1)).all():
            raise OutcomeEvaluationError("CQR query representation is not frozen ECFP4")
        weights = recover_forest_weights_many(
            self._rf, self._features, query, sample_weight_used=False
        )
        output: dict[float, tuple[np.ndarray, np.ndarray]] = {}
        for nominal, low_q, high_q in quantile_pairs:
            lower = np.asarray([
                weighted_quantile(self._outcomes, row_weights, low_q)
                for row_weights in weights
            ])
            upper = np.asarray([
                weighted_quantile(self._outcomes, row_weights, high_q)
                for row_weights in weights
            ])
            output[float(nominal)] = (lower, upper)
        return output


def evaluate_cqr(
    records: Sequence[Mapping[str, Any]],
    model_factory: Callable[[tuple[Mapping[str, Any], ...]], Any] = ProperTrainingQRFIntervalModel,
) -> CQRResult:
    """Run secondary CQR with proper-only fitting and delayed test-outcome access.

    ``model_factory`` receives only proper-training records.  Its returned object
    must expose ``predict_intervals(query_rows, quantile_pairs)`` and return a
    mapping from nominal coverage to aligned ``(lower, upper)`` arrays.  Query
    records are stripped of every outcome field before the call.
    """

    rows = _ticket4_rows(records, require_outcome=True)
    frame = pd.DataFrame(
        {
            "activity_id": [row["activity_id"] for row in rows],
            "outer_fold": [row["outer_fold"] for row in rows],
            "scaffold_key": [row["scaffold_key"] for row in rows],
        }
    )
    quantile_pairs = ((0.80, 0.10, 0.90), (0.90, 0.05, 0.95), (0.95, 0.025, 0.975))
    by_id = {row["activity_id"]: row for row in rows}
    all_row_results: list[CQRRowResult] = []
    metadata: list[CQRFoldMetadata] = []
    for fold in sorted({row["outer_fold"] for row in rows}):
        proper_ids, calibration_ids = conformal_proper_train_cal_split(
            frame,
            fold,
            cal_fraction=0.20,
            salt=C.CQR_SPLIT_SALT_SUFFIX,
        )
        test_ids = {
            row["activity_id"] for row in rows if row["outer_fold"] == fold
        }
        if proper_ids & calibration_ids or (proper_ids | calibration_ids) & test_ids:
            raise OutcomeEvaluationError("CQR proper/calibration/test sets overlap")
        outer_train_ids = {
            row["activity_id"] for row in rows if row["outer_fold"] != fold
        }
        if proper_ids | calibration_ids != outer_train_ids:
            raise OutcomeEvaluationError("CQR split does not cover outer training")
        canonical = lambda ids: sorted(
            ids,
            key=lambda activity_id: (
                C.retention_tiebreak_hash(activity_id), _activity_sort_key(activity_id)
            ),
        )
        proper_rows = tuple(dict(by_id[item]) for item in canonical(proper_ids))
        cal_rows = tuple(dict(by_id[item]) for item in canonical(calibration_ids))
        test_rows = tuple(dict(by_id[item]) for item in canonical(test_ids))
        model = model_factory(proper_rows)
        if not hasattr(model, "predict_intervals"):
            raise OutcomeEvaluationError("CQR model must provide predict_intervals")
        combined_blind = _blind_query_rows(cal_rows + test_rows)
        predicted = model.predict_intervals(combined_blind, quantile_pairs)
        for nominal, _, _ in quantile_pairs:
            if nominal not in predicted:
                raise OutcomeEvaluationError("CQR model omitted a frozen nominal level")
            lower_all, upper_all = predicted[nominal]
            lower_all = np.asarray(lower_all, dtype=np.float64).reshape(-1)
            upper_all = np.asarray(upper_all, dtype=np.float64).reshape(-1)
            if lower_all.shape != (len(combined_blind),) or upper_all.shape != lower_all.shape:
                raise OutcomeEvaluationError("CQR model interval output is misaligned")
            n_cal = len(cal_rows)
            lower_cal, lower_test = lower_all[:n_cal], lower_all[n_cal:]
            upper_cal, upper_test = upper_all[:n_cal], upper_all[n_cal:]
            y_cal = np.asarray([row["observed_y"] for row in cal_rows])
            scores = cqr_nonconformity_scores(y_cal, lower_cal, upper_cal)
            alpha = 1.0 - nominal
            k = math.ceil((n_cal + 1) * (1.0 - alpha))
            qhat = conformal_correction(scores, alpha)
            corrected_lower, corrected_upper = apply_conformal_correction(
                lower_test, upper_test, qhat
            )
            # Test outcomes are first touched here, after final endpoints exist.
            y_test = np.asarray([row["observed_y"] for row in test_rows])
            summary = interval_calibration_summary(
                y_test, corrected_lower, corrected_upper
            )
            for index, row in enumerate(test_rows):
                a = float(corrected_lower[index])
                b = float(corrected_upper[index])
                empty = bool(summary["empty_set"][index])
                infinite = bool(np.isneginf(a) and np.isposinf(b))
                all_row_results.append(
                    CQRRowResult(
                        activity_id=row["activity_id"],
                        outer_fold=fold,
                        nominal_coverage=nominal,
                        raw_lower_endpoint=a,
                        raw_upper_endpoint=b,
                        raw_corrected_span=float(summary["raw_corrected_span"][index]),
                        empty_set=empty,
                        finite_set=not infinite,
                        infinite_set=infinite,
                        covered=bool(summary["covered"][index]),
                        reported_width=float(summary["reported_width"][index]),
                    )
                )
            metadata.append(
                CQRFoldMetadata(
                    outer_fold=fold,
                    n_proper=len(proper_rows),
                    n_cal=n_cal,
                    nominal_coverage=nominal,
                    alpha=alpha,
                    k=k,
                    qhat=qhat,
                    qhat_is_finite=math.isfinite(qhat),
                    n_evaluated=summary["n_evaluated"],
                    ordinary_finite_interval_count=summary["ordinary_finite_interval_count"],
                    empty_set_count=summary["empty_set_count"],
                    infinite_set_count=summary["infinite_set_count"],
                    empirical_marginal_coverage=summary["empirical_marginal_coverage"],
                    mean_prediction_set_width=summary["mean_interval_width"],
                    median_prediction_set_width=summary["median_interval_width"],
                    split_helper="conformal_proper_train_cal_split",
                    split_salt=C.CQR_SPLIT_SALT_SUFFIX,
                    calibration_fraction=0.20,
                    split_algorithm=CQR_SPLIT_ALGORITHM,
                )
            )
    coverage_results: list[CQRCoverageResult] = []
    for nominal, _, _ in quantile_pairs:
        selected = tuple(row for row in all_row_results if row.nominal_coverage == nominal)
        widths = np.asarray([row.reported_width for row in selected])
        coverage_results.append(
            CQRCoverageResult(
                nominal_coverage=nominal,
                empirical_marginal_coverage=float(np.mean([row.covered for row in selected])),
                n_evaluated=len(selected),
                mean_final_set_width=float(np.mean(widths)),
                median_final_set_width=float(np.median(widths)),
                ordinary_finite_interval_count=sum(
                    row.finite_set and not row.empty_set for row in selected
                ),
                empty_set_count=sum(row.empty_set for row in selected),
                infinite_set_count=sum(row.infinite_set for row in selected),
                rows=selected,
            )
        )
    return CQRResult(
        role="SECONDARY_CALIBRATION_ONLY",
        marginal_label="EMPIRICAL_MARGINAL_COVERAGE",
        canonical_triage_ranking="ORIGINAL_FROZEN_QRF_WIDTH",
        base_intervals=quantile_pairs,
        coverages=tuple(coverage_results),
        fold_metadata=tuple(metadata),
    )


def strict_interior_sensitivity_rows(
    records: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    """Select exact quantitative ``3 < CLint < 150`` rows for Sensitivity A."""

    selected: list[dict[str, Any]] = []
    for record in records:
        row = dict(record)
        if "observed_clint" not in row:
            raise OutcomeEvaluationError("Sensitivity A requires original-scale CLint")
        relation = row.get("standard_relation")
        if relation is not None and not (isinstance(relation, float) and math.isnan(relation)):
            continue
        value = float(row["observed_clint"])
        if math.isfinite(value) and C.CLINT_LOW < value < C.CLINT_HIGH:
            selected.append(row)
    return tuple(selected)


def prepare_sensitivity_a_prediction_inputs(
    records: Sequence[Mapping[str, Any]],
    features: np.ndarray,
    descriptors: np.ndarray,
    *,
    provenance: Mapping[str, Any],
) -> SensitivityAPredictionInputs:
    """Build a separate strict-interior five-fold model input without touching N744."""

    source = [dict(row) for row in records]
    features = np.asarray(features)
    descriptors = np.asarray(descriptors, dtype=np.float64)
    if features.shape[0] != len(source) or descriptors.shape[0] != len(source):
        raise OutcomeEvaluationError("Sensitivity A source arrays are not row aligned")
    selected_positions: list[int] = []
    for position, row in enumerate(source):
        relation = row.get("standard_relation")
        exact = relation is None or (isinstance(relation, float) and math.isnan(relation))
        if "observed_clint" not in row or "observed_y" not in row:
            raise OutcomeEvaluationError("Sensitivity A requires CLint and log-scale outcome")
        clint = float(row["observed_clint"])
        if exact and math.isfinite(clint) and C.CLINT_LOW < clint < C.CLINT_HIGH:
            selected_positions.append(position)
    if not selected_positions:
        raise OutcomeEvaluationError("Sensitivity A strict-interior cohort is empty")
    # Canonicalise before fitting: sklearn bootstrap indices are positional, so
    # leaving rows in caller order would make equivalent shuffled inputs produce
    # different forests despite the same fixed seed.
    selected_positions.sort(
        key=lambda position: (
            C.retention_tiebreak_hash(source[position].get("activity_id")),
            _activity_sort_key(source[position].get("activity_id")),
        )
    )
    selected = [source[position] for position in selected_positions]
    if any("activity_id" not in row or "scaffold_key" not in row for row in selected):
        raise OutcomeEvaluationError("Sensitivity A keys are incomplete")
    assignment = assign_scaffold_folds(
        [str(row["scaffold_key"]) for row in selected], n_folds=C.N_FOLDS
    )
    inputs = OutcomeBlindInputs(
        activity_ids=tuple(row["activity_id"] for row in selected),
        outer_folds=tuple(assignment[str(row["scaffold_key"])] for row in selected),
        scaffold_keys=tuple(str(row["scaffold_key"]) for row in selected),
        features=_immutable_array(features[selected_positions]),
        descriptors=_immutable_array(descriptors[selected_positions]),
        provenance=dict(provenance),
    )
    _validate_outcome_blind_inputs(inputs)
    outcomes = {
        row["activity_id"]: float(row["observed_y"])
        for row in selected
    }
    if not all(math.isfinite(value) for value in outcomes.values()):
        raise OutcomeEvaluationError("Sensitivity A outcomes must be finite")
    return SensitivityAPredictionInputs(inputs=inputs, outcomes_by_id=outcomes)


def orchestrate_sensitivity_a_predictions(
    prepared: SensitivityAPredictionInputs,
    *,
    rf_factory: Callable[[], Any] = C.make_frozen_rf,
    audit_hook: Callable[[str, Mapping[str, Any]], None] | None = None,
) -> PredictionFreeze:
    """Fit the separate frozen-architecture Sensitivity-A five-fold analysis."""

    if not isinstance(prepared, SensitivityAPredictionInputs):
        raise TypeError("prepared must be SensitivityAPredictionInputs")

    def training_outcomes(_fold: int, train_ids: tuple[Any, ...]) -> list[float]:
        return [prepared.outcomes_by_id[activity_id] for activity_id in train_ids]

    return orchestrate_outcome_blind_predictions(
        prepared.inputs,
        training_outcomes,
        rf_factory=rf_factory,
        audit_hook=audit_hook,
    )


def _sensitivity_curves(
    records: Sequence[Mapping[str, Any]],
) -> tuple[CoverageCurveResult, ...]:
    rows = _ticket4_rows(records, require_outcome=True)
    methods = tuple(method for method in _UNCERTAINTY_FIELDS if all(method in row for row in rows))
    if "qrf_width" not in methods:
        raise OutcomeEvaluationError("sensitivity records require frozen QRF width")
    curves: list[CoverageCurveResult] = []
    for method in methods:
        points: list[CoveragePointResult] = []
        for coverage in C.COVERAGE_LEVELS:
            retained: list[dict[str, Any]] = []
            counts: list[tuple[int, int]] = []
            for fold in sorted({row["outer_fold"] for row in rows}):
                candidates = [row for row in rows if row["outer_fold"] == fold]
                k = math.ceil(float(coverage) * len(candidates))
                ranked = sorted(
                    candidates,
                    key=lambda row: (
                        float(row[method]),
                        C.retention_tiebreak_hash(row["activity_id"]),
                        _activity_sort_key(row["activity_id"]),
                    ),
                )
                retained.extend(ranked[:k])
                counts.append((fold, k))
            y_true = np.asarray([row["observed_y"] for row in retained])
            y_pred = np.asarray([row["rf_prediction"] for row in retained])
            points.append(
                CoveragePointResult(
                    coverage=float(coverage),
                    retained_n=len(retained),
                    deferred_n=len(rows) - len(retained),
                    pooled_rmse=rmse(y_true, y_pred),
                    pooled_mae=mae(y_true, y_pred),
                    retained_ids=tuple(row["activity_id"] for row in retained),
                    retained_counts_by_fold=tuple(counts),
                )
            )
        curves.append(
            CoverageCurveResult(
                method=method,
                role="FOCAL_DIAGNOSTIC" if method == "qrf_width" else "SECONDARY_DIAGNOSTIC",
                points=tuple(points),
                naurc=trapezoidal_naurc(
                    np.asarray([point.coverage for point in points]),
                    np.asarray([point.pooled_rmse for point in points]),
                ),
            )
        )
    return tuple(curves)


def _point_matched_random(
    records: Sequence[Mapping[str, Any]],
    qrf80: CoveragePointResult,
    *,
    n_random: int,
    seed: int,
) -> MatchedRandomResult:
    rows = _ticket4_rows(records, require_outcome=True)
    fold_ids = {
        fold: [row["activity_id"] for row in rows if row["outer_fold"] == fold]
        for fold in sorted({row["outer_fold"] for row in rows})
    }
    samples = matched_random_rankings(
        fold_ids, n_random=n_random, seed=seed, coverage=C.PRIMARY_COVERAGE
    )
    by_id = {row["activity_id"]: row for row in rows}
    draws = np.empty(n_random, dtype=np.float64)
    expected = dict(qrf80.retained_counts_by_fold)
    for draw_index in range(n_random):
        selected: list[Any] = []
        for fold in sorted(samples):
            fold_selected = samples[fold][draw_index]
            if len(fold_selected) != expected[fold]:
                raise OutcomeEvaluationError("sensitivity random count differs from QRF80")
            canonical_ids = [
                int(item) if isinstance(item, np.integer) else item
                for item in fold_selected
            ]
            selected.extend(sorted(canonical_ids, key=_activity_sort_key))
        draws[draw_index] = rmse(
            np.asarray([by_id[item]["observed_y"] for item in selected]),
            np.asarray([by_id[item]["rf_prediction"] for item in selected]),
        )
    return MatchedRandomResult(
        draw_count=n_random,
        seed=seed,
        retained_counts_by_fold=qrf80.retained_counts_by_fold,
        mean_rmse=float(draws.mean()),
        monte_carlo_se=0.0 if n_random == 1 else float(draws.std(ddof=1) / np.sqrt(n_random)),
        rmse_draws=_immutable_array(draws),
    )


def evaluate_sensitivity_a(
    exact_cohort_records: Sequence[Mapping[str, Any]],
    features: np.ndarray,
    descriptors: np.ndarray,
    *,
    provenance: Mapping[str, Any],
    n_bootstrap: int = C.N_BOOTSTRAP,
    n_random: int = C.N_RANDOM_DEFERRALS,
    seed: int = C.MASTER_SEED,
    rf_factory: Callable[[], Any] = C.make_frozen_rf,
) -> SensitivityResult:
    """Run the complete separate strict-interior five-fold sensitivity analysis.

    Primary N744 fold labels, OOF predictions, uncertainties, and retention
    metadata in ``exact_cohort_records`` are deliberately ignored.  The strict
    cohort is canonically rebuilt, assigned its own scaffold folds, and passed
    through the same frozen primary model/uncertainty orchestration before any
    downstream ranking or bootstrap evaluation.
    """

    source = [dict(row) for row in exact_cohort_records]
    prepared = prepare_sensitivity_a_prediction_inputs(
        source,
        features,
        descriptors,
        provenance=provenance,
    )
    fold_fits: list[dict[str, Any]] = []

    def audit(event: str, detail: Mapping[str, Any]) -> None:
        if event == "fold_completed":
            fold_fits.append(dict(detail))

    sensitivity_freeze = orchestrate_sensitivity_a_predictions(
        prepared,
        rf_factory=rf_factory,
        audit_hook=audit,
    )
    predicted_records = sensitivity_freeze.read_payload()["records"]
    strict_by_id = {
        row["activity_id"]: row
        for row in strict_interior_sensitivity_rows(source)
    }
    scaffold_by_id = dict(
        zip(prepared.inputs.activity_ids, prepared.inputs.scaffold_keys)
    )
    records: list[dict[str, Any]] = []
    for prediction in predicted_records:
        activity_id = prediction["activity_id"]
        source_row = strict_by_id[activity_id]
        records.append(
            {
                **prediction,
                "scaffold_key": scaffold_by_id[activity_id],
                "observed_y": float(source_row["observed_y"]),
                "observed_clint": float(source_row["observed_clint"]),
                "standard_relation": source_row.get("standard_relation"),
            }
        )
    if len(records) != len(prepared.inputs.activity_ids):
        raise OutcomeEvaluationError("Sensitivity A OOF prediction universe is incomplete")

    curves = _sensitivity_curves(records)
    qrf80 = next(curve for curve in curves if curve.method == "qrf_width").at(0.80)
    random_result = _point_matched_random(
        records, qrf80, n_random=n_random, seed=seed
    )
    bootstrap = run_primary_bootstrap(
        records, n_bootstrap=n_bootstrap, n_random=n_random, seed=seed
    )
    return SensitivityResult(
        name="SENSITIVITY_A_STRICT_INTERIOR",
        interpretation_labels=("SENSITIVITY", "STRICT_INTERIOR", "SEPARATE_FIVE_FOLD_ANALYSIS"),
        cohort_n=len(records),
        coverage_curves=curves,
        qrf80=qrf80,
        matched_random80=random_result,
        rel_benefit_80=rel_benefit_80(random_result.mean_rmse, qrf80.pooled_rmse),
        bootstrap=bootstrap,
        oof_records=tuple(dict(row) for row in records),
        provenance={
            "cohort_rule": "standard_relation IS NULL and 3 < observed_clint < 150",
            "cohort_n": len(records),
            "fold_assignment": tuple(
                sorted(
                    zip(prepared.inputs.activity_ids, prepared.inputs.outer_folds),
                    key=lambda item: _activity_sort_key(item[0]),
                )
            ),
            "model_specification": dict(C.FROZEN_RF_PARAMS),
            "representation": C.REPRESENTATION.value,
            "oof_origin": "SENSITIVITY_A_SEPARATE_STRICT_INTERIOR_FIVE_FOLD_REFIT",
            "ranking_source": "SENSITIVITY_A_RECOMPUTED_QRF_WIDTH_FOLD_LOCAL",
            "bootstrap_source": "SENSITIVITY_A_OWN_OOF_RECORDS_AND_FOLDS",
            "prediction_artifact_sha256": sensitivity_freeze.sha256,
            "fold_fits": tuple(fold_fits),
        },
    )


def _sensitivity_b_bootstrap(
    records: Sequence[Mapping[str, Any]],
    *,
    n_bootstrap: int,
    n_random: int,
    seed: int,
) -> BootstrapInferenceResult:
    """Sensitivity-B bootstrap with one-based nested substreams from its amendment."""

    all_rows = _ticket4_rows(records, require_outcome=True)
    plan_rows = [
        {key: value for key, value in row.items() if key != "observed_y"}
        for row in all_rows
    ]
    frame = pd.DataFrame(
        {
            "activity_id": [row["activity_id"] for row in all_rows],
            "outer_fold": [row["outer_fold"] for row in all_rows],
            "scaffold_key": [row["scaffold_key"] for row in all_rows],
        }
    )
    samples = scaffold_bootstrap_indices(frame, n_bootstrap=n_bootstrap, seed=seed)
    results: list[BootstrapReplicateResult] = []
    for replicate_index, sample in enumerate(samples):
        all_occurrences = _bootstrap_occurrences(plan_rows, sample, replicate_index)
        occurrences = tuple(
            occurrence for occurrence in all_occurrences
            if float(all_rows[int(occurrence["row_position"])]["observed_clint"]) >= 25.0
        )
        if not occurrences:
            raise OutcomeEvaluationError("Sensitivity B bootstrap replicate has no eligible rows")
        selected, candidate_counts, retained_counts = _retention_for_occurrences(
            plan_rows, occurrences
        )
        random_draws = _random_occurrence_draws(
            occurrences,
            retained_counts,
            replicate_index=replicate_index,
            n_random=n_random,
            base_seed=seed,
            sensitivity_b_one_based=True,
        )

        def squared(indices: Sequence[int]) -> np.ndarray:
            return np.asarray(
                [
                    (
                        all_rows[int(occurrences[index]["row_position"])]["observed_y"]
                        - all_rows[int(occurrences[index]["row_position"])]["rf_prediction"]
                    ) ** 2
                    for index in indices
                ]
            )

        qrf_rmse = float(np.sqrt(np.mean(squared(selected))))
        random_mean = float(np.mean([
            float(np.sqrt(np.mean(squared(draw)))) for draw in random_draws
        ]))
        results.append(
            BootstrapReplicateResult(
                replicate_index=replicate_index,
                occurrence_ids=tuple(tuple(item["occurrence_id"]) for item in occurrences),
                qrf_retained_occurrence_ids=tuple(
                    tuple(occurrences[index]["occurrence_id"]) for index in selected
                ),
                fold_candidate_counts=candidate_counts,
                fold_retained_counts=retained_counts,
                rmse_qrf80=qrf_rmse,
                rmse_random80=random_mean,
                rel_benefit_80=rel_benefit_80(random_mean, qrf_rmse),
            )
        )
    values = np.asarray([item.rel_benefit_80 for item in results])
    lower, upper = np.percentile(values, [2.5, 97.5], method="linear")
    return BootstrapInferenceResult(
        replicates=tuple(results),
        ci_lower=float(lower),
        ci_upper=float(upper),
        confidence_level=0.95,
        percentile_method="linear",
        bootstrap_replicates=n_bootstrap,
        matched_random_draws_per_replicate=n_random,
        base_seed=seed,
        nested_rng_provenance=(
            "SensitivityB:SeedSequence([20260923,b])->uint32->RandomState->permutation; b starts at 1"
        ),
    )


def evaluate_sensitivity_b(
    frozen_primary_records: Sequence[Mapping[str, Any]],
    *,
    n_bootstrap: int = C.N_BOOTSTRAP,
    n_random: int = C.N_RANDOM_DEFERRALS,
    seed: int = C.MASTER_SEED,
) -> SensitivityResult:
    """Run the post-freeze, outcome-defined, nondeployable CLint >= 25 diagnostic."""

    original = [dict(row) for row in frozen_primary_records]
    for row in original:
        if "observed_clint" not in row or not math.isfinite(float(row["observed_clint"])):
            raise OutcomeEvaluationError("Sensitivity B requires finite original-scale CLint")
    subgroup = tuple(row for row in original if float(row["observed_clint"]) >= 25.0)
    if not subgroup:
        raise OutcomeEvaluationError("Sensitivity B subgroup is empty")
    curves = _sensitivity_curves(subgroup)
    qrf80 = next(curve for curve in curves if curve.method == "qrf_width").at(0.80)
    random_result = _point_matched_random(
        subgroup, qrf80, n_random=n_random, seed=seed
    )
    bootstrap = _sensitivity_b_bootstrap(
        original, n_bootstrap=n_bootstrap, n_random=n_random, seed=seed
    )
    return SensitivityResult(
        name="SENSITIVITY_B_CLINT_GE_25",
        interpretation_labels=("EXPLORATORY", "OUTCOME_DEFINED", "DIAGNOSTIC", "NONDEPLOYABLE"),
        cohort_n=len(subgroup),
        coverage_curves=curves,
        qrf80=qrf80,
        matched_random80=random_result,
        rel_benefit_80=rel_benefit_80(random_result.mean_rmse, qrf80.pooled_rmse),
        bootstrap=bootstrap,
    )
