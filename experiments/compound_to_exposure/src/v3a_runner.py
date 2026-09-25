"""Fail-closed v3A scientific-runner shell.

Ticket 1 deliberately stops before model fitting, prediction, uncertainty scoring,
or outcome evaluation.  It binds execution authorization to the persisted frozen
inputs and provides only a collision-safe internal run ledger.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from src import v3a_config as C
from src.v3a_preflight import (
    COHORT_RELATIVE,
    FEATURE_RELATIVE,
    MANIFEST_RELATIVE,
    SAP_RELATIVE,
    SPLIT_RELATIVE,
    STATE_RELATIVE,
)
from src.v3a_qrf_weights import ExecutionGuardError, check_execution_guard


SCIENTIFIC_RUNS_RELATIVE = Path("scientific_runs/v3a")
LEDGER_FILENAME = "execution_ledger.json"
LEDGER_SCHEMA_VERSION = 1
_RUN_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


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
