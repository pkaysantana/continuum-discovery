"""Synthetic Gate 11 acceptance coverage for the v3A Ticket 1 runner shell.

No model is fitted and no scientific result is calculated in this module.
"""
from __future__ import annotations

import ast
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import v3a_config as C
from src.v3a_preflight import (
    COHORT_RELATIVE,
    FEATURE_RELATIVE,
    MANIFEST_RELATIVE,
    SAP_RELATIVE,
    SPLIT_RELATIVE,
    STATE_RELATIVE,
)
from src.v3a_runner import (
    LEDGER_FILENAME,
    SCIENTIFIC_RUNS_RELATIVE,
    FrozenArtifactError,
    InternalRunStatus,
    LifecycleTransitionError,
    ProtectedRunPathError,
    RunAuthorizationError,
    RunCollisionError,
    abort_run,
    authorize_run,
    initialize_run_ledger,
    load_frozen_artifacts,
    reject_existing_run_directory,
    start_run,
    validate_internal_transition,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FROZEN_RELATIVES = (
    SAP_RELATIVE,
    COHORT_RELATIVE,
    SPLIT_RELATIVE,
    FEATURE_RELATIVE,
    MANIFEST_RELATIVE,
    STATE_RELATIVE,
)
FIXED_TIME = "2026-09-24T12:00:00Z"
FIXED_COMMIT = "1" * 40


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


@pytest.fixture
def ready_project(tmp_path):
    """Temporary future-authorized fixture using copies of frozen byte artifacts."""

    root = tmp_path / "synthetic_project"
    for relative in FROZEN_RELATIVES:
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PROJECT_ROOT / relative, destination)

    manifest_path = root / MANIFEST_RELATIVE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["execution_state"] = C.STATE_FROZEN
    manifest["independent_audit_recorded"] = True
    _write_json(manifest_path, manifest)

    state_path = root / STATE_RELATIVE
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["state"] = C.STATE_FROZEN
    state["scientific_execution_allowed"] = True
    state["independent_audit_recorded"] = True
    _write_json(state_path, state)
    return root


def _mutate_json(path: Path, mutator) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutator(payload)
    _write_json(path, payload)


def _ledger(ready_project: Path, tmp_path: Path, run_id: str = "synthetic-run"):
    artifacts = load_frozen_artifacts(ready_project)
    return initialize_run_ledger(
        ready_project / SCIENTIFIC_RUNS_RELATIVE,
        run_id,
        artifacts=artifacts,
        git_commit=FIXED_COMMIT,
        start_timestamp=FIXED_TIME,
        authorization_requested=True,
        environment_summary={"source": "synthetic-test"},
    )


class TestFrozenAuthorization:
    def test_current_real_persisted_state_fails_closed(self):
        with pytest.raises(RunAuthorizationError, match="persisted state"):
            authorize_run(PROJECT_ROOT, execute_scientific_analysis=True)

    def test_missing_explicit_authorization_fails_closed(self, ready_project):
        with pytest.raises(RunAuthorizationError, match="flag"):
            authorize_run(ready_project, execute_scientific_analysis=False)

    @pytest.mark.parametrize("audit_value", [False, None])
    def test_missing_or_false_persisted_audit_fails_closed(self, ready_project, audit_value):
        state_path = ready_project / STATE_RELATIVE

        def alter(state):
            if audit_value is None:
                state.pop("independent_audit_recorded")
            else:
                state["independent_audit_recorded"] = audit_value

        _mutate_json(state_path, alter)
        with pytest.raises(RunAuthorizationError, match="audit"):
            authorize_run(ready_project, execute_scientific_analysis=True)

    @pytest.mark.parametrize("allowed_value", [False, None])
    def test_scientific_execution_allowed_must_be_explicit_true(self, ready_project, allowed_value):
        state_path = ready_project / STATE_RELATIVE

        def alter(state):
            if allowed_value is None:
                state.pop("scientific_execution_allowed")
            else:
                state["scientific_execution_allowed"] = allowed_value

        _mutate_json(state_path, alter)
        with pytest.raises(RunAuthorizationError, match="scientific_execution_allowed"):
            authorize_run(ready_project, execute_scientific_analysis=True)

    @pytest.mark.parametrize(
        "relative",
        [SAP_RELATIVE, COHORT_RELATIVE, SPLIT_RELATIVE],
        ids=["sap", "cohort", "split"],
    )
    def test_altered_text_frozen_artifact_rejected(self, ready_project, relative):
        artifact = ready_project / relative
        artifact.write_bytes(artifact.read_bytes() + b"\nTAMPERED\n")
        with pytest.raises(RunAuthorizationError, match="artifact verification"):
            authorize_run(ready_project, execute_scientific_analysis=True)

    def test_altered_feature_artifact_rejected(self, ready_project):
        feature_path = ready_project / FEATURE_RELATIVE
        matrix = np.load(feature_path, allow_pickle=False)
        matrix[0, 0] = 1 - matrix[0, 0]
        np.save(feature_path, matrix, allow_pickle=False)
        with pytest.raises(RunAuthorizationError, match="artifact verification"):
            authorize_run(ready_project, execute_scientific_analysis=True)

    @pytest.mark.parametrize("relative", [SAP_RELATIVE, COHORT_RELATIVE, SPLIT_RELATIVE, FEATURE_RELATIVE])
    def test_missing_frozen_artifact_rejected(self, ready_project, relative):
        (ready_project / relative).unlink()
        with pytest.raises(RunAuthorizationError, match="missing"):
            authorize_run(ready_project, execute_scientific_analysis=True)

    @pytest.mark.parametrize(
        ("field", "bad_value"),
        [
            ("representation", "DESCRIPTORS"),
            ("morgan_fingerprint", {"radius": 1, "nBits": 2048, "binary": True, "useChirality": False}),
        ],
    )
    def test_altered_representation_metadata_rejected(self, ready_project, field, bad_value):
        _mutate_json(
            ready_project / MANIFEST_RELATIVE,
            lambda manifest: manifest.__setitem__(field, bad_value),
        )
        with pytest.raises(RunAuthorizationError, match="representation|Morgan"):
            authorize_run(ready_project, execute_scientific_analysis=True)

    @pytest.mark.parametrize("parameter", sorted(C.FROZEN_RF_PARAMS))
    def test_each_nonfrozen_rf_configuration_rejected(self, ready_project, parameter):
        def alter(manifest):
            current = manifest["rf_params"][parameter]
            manifest["rf_params"][parameter] = "DRIFT" if current is None else object_value(current)

        def object_value(current):
            if isinstance(current, bool):
                return not current
            if isinstance(current, int):
                return current + 1
            return f"{current}_DRIFT"

        _mutate_json(ready_project / MANIFEST_RELATIVE, alter)
        with pytest.raises(RunAuthorizationError, match="RF configuration"):
            authorize_run(ready_project, execute_scientific_analysis=True)

    def test_wrong_cohort_count_rejected(self, ready_project):
        _mutate_json(
            ready_project / MANIFEST_RELATIVE,
            lambda manifest: manifest.__setitem__("cohort_N", C.COHORT_N - 1),
        )
        with pytest.raises(RunAuthorizationError, match="cohort count"):
            authorize_run(ready_project, execute_scientific_analysis=True)

    def test_feature_file_byte_hash_is_enforced(self, ready_project):
        feature_path = ready_project / FEATURE_RELATIVE
        matrix = np.load(feature_path, allow_pickle=False)
        np.save(feature_path, matrix.astype(np.float32), allow_pickle=False)
        # Logical uint8 matrix hash is unchanged; exact persisted file hash is not.
        with pytest.raises(RunAuthorizationError, match="feature_file_sha256"):
            authorize_run(ready_project, execute_scientific_analysis=True)

    def test_valid_synthetic_future_state_authorizes(self, ready_project):
        artifacts = authorize_run(ready_project, execute_scientific_analysis=True)
        assert artifacts.state["state"] == C.STATE_FROZEN
        assert artifacts.manifest["cohort_N"] == C.COHORT_N
        assert not hasattr(artifacts, "outcomes")


class TestRunNamespaceAndLedger:
    @pytest.mark.parametrize("protected_name", ["splits", "manifests", "state", "reports"])
    def test_preflight_namespaces_are_protected(self, ready_project, protected_name):
        protected = ready_project / protected_name
        protected.mkdir(exist_ok=True)
        before = {path: path.read_bytes() for path in protected.rglob("*") if path.is_file()}
        artifacts = load_frozen_artifacts(ready_project)
        with pytest.raises(ProtectedRunPathError, match="canonical"):
            initialize_run_ledger(
                protected,
                "forbidden-run",
                artifacts=artifacts,
                git_commit=FIXED_COMMIT,
                start_timestamp=FIXED_TIME,
                authorization_requested=False,
            )
        assert before == {path: path.read_bytes() for path in protected.rglob("*") if path.is_file()}

    @pytest.mark.parametrize("run_id", ["../escape", "nested/run", "nested\\run", ".", ""])
    def test_unsafe_run_id_rejected(self, tmp_path, run_id):
        with pytest.raises(ProtectedRunPathError):
            reject_existing_run_directory(
                tmp_path / SCIENTIFIC_RUNS_RELATIVE,
                run_id,
                project_root=tmp_path,
            )

    def test_canonical_scientific_namespace_succeeds(self, ready_project, tmp_path):
        ledger = _ledger(ready_project, tmp_path, run_id="canonical-run")
        canonical_root = (ready_project / SCIENTIFIC_RUNS_RELATIVE).resolve()
        assert ledger.run_directory == canonical_root / "canonical-run"
        assert ledger.ledger_path.is_file()

    def test_valid_child_run_directory_is_accepted(self, ready_project):
        canonical_root = ready_project / SCIENTIFIC_RUNS_RELATIVE
        candidate = reject_existing_run_directory(
            canonical_root,
            "valid-child",
            project_root=ready_project,
        )
        assert candidate == canonical_root.resolve() / "valid-child"
        assert not candidate.exists()

    @pytest.mark.parametrize(
        "run_root_factory",
        [
            pytest.param(lambda project, owner: owner / "absolute-external", id="absolute-external"),
            pytest.param(lambda project, owner: project / "repository-sibling", id="repository-sibling"),
            pytest.param(
                lambda project, owner: project / SCIENTIFIC_RUNS_RELATIVE / ".." / "escaped",
                id="parent-traversal",
            ),
            pytest.param(
                lambda project, owner: project / "scientific_runs" / "v3a-evil",
                id="prefix-confusion",
            ),
        ],
    )
    def test_noncanonical_run_roots_rejected_without_side_effect(
        self, ready_project, tmp_path, run_root_factory
    ):
        artifacts = load_frozen_artifacts(ready_project)
        run_root = run_root_factory(ready_project, tmp_path).absolute()
        resolved_run_root = run_root.resolve()
        candidate = resolved_run_root / "rejected-run"
        assert not resolved_run_root.exists()
        with pytest.raises(ProtectedRunPathError):
            initialize_run_ledger(
                run_root,
                "rejected-run",
                artifacts=artifacts,
                git_commit=FIXED_COMMIT,
                start_timestamp=FIXED_TIME,
                authorization_requested=False,
            )
        assert not resolved_run_root.exists()
        assert not candidate.exists()

    def test_existing_run_id_collision_is_rejected_without_overwrite(self, ready_project, tmp_path):
        ledger = _ledger(ready_project, tmp_path)
        original = ledger.ledger_path.read_bytes()
        with pytest.raises(RunCollisionError):
            _ledger(ready_project, tmp_path)
        assert ledger.ledger_path.read_bytes() == original

    def test_ledger_schema_is_complete_and_canonical(self, ready_project, tmp_path):
        second_project = tmp_path / "second-synthetic-project"
        shutil.copytree(ready_project, second_project)
        artifacts = load_frozen_artifacts(ready_project)
        second_artifacts = load_frozen_artifacts(second_project)
        kwargs = dict(
            artifacts=artifacts,
            git_commit=FIXED_COMMIT,
            start_timestamp=FIXED_TIME,
            authorization_requested=True,
            environment_summary={"z": 1, "a": 2},
        )
        first = initialize_run_ledger(
            ready_project / SCIENTIFIC_RUNS_RELATIVE, "same-id", **kwargs
        )
        kwargs["artifacts"] = second_artifacts
        second = initialize_run_ledger(
            second_project / SCIENTIFIC_RUNS_RELATIVE, "same-id", **kwargs
        )
        assert first.ledger_path.read_bytes() == second.ledger_path.read_bytes()
        raw = first.ledger_path.read_bytes()
        assert raw.endswith(b"\n")
        assert b": " not in raw
        payload = first.read()
        assert set(payload) == {
            "abort_reason",
            "authorization_passed",
            "authorization_requested",
            "environment_summary",
            "git_commit",
            "independent_audit_recorded",
            "manifest_reference",
            "manifest_sha256",
            "preflight_state",
            "run_id",
            "schema_version",
            "scientific_execution_allowed",
            "start_timestamp",
            "status",
        }
        assert payload["status"] == InternalRunStatus.RUNNER_IMPLEMENTED_NOT_AUDITED.value
        assert "complete" not in payload["status"].lower()
        assert list(json.loads(raw).keys()) == sorted(payload)

    def test_authorization_success_then_start_and_abort(self, ready_project, tmp_path):
        ledger = _ledger(ready_project, tmp_path)
        authorize_run(ready_project, execute_scientific_analysis=True, ledger=ledger)
        assert ledger.read()["authorization_passed"] is True
        start_run(ledger)
        assert ledger.read()["status"] == InternalRunStatus.EXECUTION_RUNNING.value
        abort_run(ledger, "synthetic stop")
        payload = ledger.read()
        assert payload["status"] == InternalRunStatus.EXECUTION_ABORTED.value
        assert payload["abort_reason"] == "synthetic stop"
        assert list(ledger.run_directory.iterdir()) == [ledger.run_directory / LEDGER_FILENAME]

    def test_failed_authorization_is_aborted_never_completed(self, ready_project, tmp_path):
        ledger = _ledger(ready_project, tmp_path)
        with pytest.raises(RunAuthorizationError):
            authorize_run(ready_project, execute_scientific_analysis=False, ledger=ledger)
        payload = ledger.read()
        assert payload["authorization_passed"] is False
        assert payload["status"] == InternalRunStatus.EXECUTION_ABORTED.value
        assert "complete" not in json.dumps(payload).lower()
        with pytest.raises(LifecycleTransitionError):
            start_run(ledger)

    def test_state_change_after_initialization_is_rejected(self, ready_project, tmp_path):
        state_path = ready_project / STATE_RELATIVE
        ready_state = json.loads(state_path.read_text(encoding="utf-8"))
        initial_state = dict(ready_state)
        initial_state["state"] = C.STATE_PREEXECUTION
        initial_state["scientific_execution_allowed"] = False
        initial_state["independent_audit_recorded"] = False
        _write_json(state_path, initial_state)
        ledger = _ledger(ready_project, tmp_path)
        _write_json(state_path, ready_state)
        with pytest.raises(RunAuthorizationError, match="changed after ledger"):
            authorize_run(ready_project, execute_scientific_analysis=True, ledger=ledger)
        assert ledger.read()["status"] == InternalRunStatus.EXECUTION_ABORTED.value

    def test_unrelated_filesystem_artifact_is_untouched(self, ready_project, tmp_path):
        sentinel = tmp_path / "unrelated.bin"
        sentinel.write_bytes(b"leave-me-alone")
        ledger = _ledger(ready_project, tmp_path)
        with pytest.raises(RunAuthorizationError):
            authorize_run(ready_project, execute_scientific_analysis=False, ledger=ledger)
        assert sentinel.read_bytes() == b"leave-me-alone"

    def test_only_ticket1_transitions_are_reachable(self):
        assert validate_internal_transition(
            InternalRunStatus.RUNNER_IMPLEMENTED_NOT_AUDITED,
            InternalRunStatus.EXECUTION_RUNNING,
        ) is InternalRunStatus.EXECUTION_RUNNING
        with pytest.raises(LifecycleTransitionError):
            validate_internal_transition(
                InternalRunStatus.EXECUTION_ABORTED,
                InternalRunStatus.EXECUTION_RUNNING,
            )
        for forbidden in (
            "PREDICTIONS_FROZEN",
            "OUTCOME_EVALUATION_COMPLETE",
            "INFERENCE_COMPLETE",
            "EXECUTION_COMPLETED",
        ):
            with pytest.raises(LifecycleTransitionError):
                validate_internal_transition(
                    InternalRunStatus.RUNNER_IMPLEMENTED_NOT_AUDITED,
                    forbidden,
                )


def test_runner_imports_no_v2_execution_module():
    source_path = PROJECT_ROOT / "src" / "v3a_runner.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    prohibited = {"execute_v2", "run", "pipelines"}
    assert not any(name.split(".")[-1] in prohibited for name in imported)


@pytest.mark.parametrize(
    "missing_relative",
    [STATE_RELATIVE, MANIFEST_RELATIVE],
    ids=["state", "manifest"],
)
def test_missing_manifest_or_state_is_fail_closed(ready_project, missing_relative):
    (ready_project / missing_relative).unlink()
    with pytest.raises((FrozenArtifactError, RunAuthorizationError), match="missing"):
        authorize_run(ready_project, execute_scientific_analysis=True)
