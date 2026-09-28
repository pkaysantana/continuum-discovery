"""Synthetic Gate 11 acceptance coverage for the v3A Ticket 1/2/3/4/5 runner.

Only synthetic models and outcomes are used.  The real CHEMBL3301370 outcomes
are never supplied to the runner.
"""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import math
import shutil
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import v3a_config as C
from src import v3a_runner as runner
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
    FINAL_MANIFEST_FILENAME,
    FINAL_RESULT_FILENAME,
    PREDICTION_FREEZE_FILENAME,
    SCIENTIFIC_RUNS_RELATIVE,
    FrozenArtifactError,
    InternalRunStatus,
    LifecycleTransitionError,
    OutcomeEvaluationError,
    OutcomeBlindInputs,
    PredictionFreezeCollisionError,
    PredictionFreezeError,
    PredictionOrchestrationError,
    ProtectedRunPathError,
    RunAuthorizationError,
    RunCollisionError,
    FinalResultCollisionError,
    FinalResultError,
    abort_run,
    authorize_run,
    initialize_run_ledger,
    load_frozen_artifacts,
    load_outcome_blind_inputs,
    orchestrate_outcome_blind_predictions,
    rank_outcome_blind_records,
    reject_existing_run_directory,
    seal_prediction_freeze,
    start_run,
    validate_internal_transition,
    build_prediction_freeze,
    classify_rel_benefit_80,
    evaluate_postfreeze,
    prepare_postfreeze_plan,
    build_final_result_package,
    seal_final_result,
    validate_final_result_payload,
    verify_sealed_scientific_run,
)
from src.v3a_qrf_weights import (
    matched_random_rankings,
    rel_benefit_80,
    rmse,
    trapezoidal_naurc,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FROZEN_RELATIVES = tuple(dict.fromkeys((
    SAP_RELATIVE,
    COHORT_RELATIVE,
    SPLIT_RELATIVE,
    FEATURE_RELATIVE,
    MANIFEST_RELATIVE,
    STATE_RELATIVE,
    *runner.AUTHORITY_RELATIVES,
)))
FIXED_TIME = "2026-09-24T12:00:00Z"
FIXED_COMMIT = "2a24fdf83998e07b889b9046330c3d12a8858506"


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

    def test_hash_shaped_caller_commit_cannot_override_executing_checkout(
        self, ready_project
    ):
        artifacts = load_frozen_artifacts(ready_project)
        with pytest.raises(runner.RunnerError, match="executing checkout HEAD"):
            initialize_run_ledger(
                ready_project / SCIENTIFIC_RUNS_RELATIVE,
                "forged-code-identity",
                artifacts=artifacts,
                git_commit="f" * 40,
                start_timestamp=FIXED_TIME,
                authorization_requested=True,
            )
        assert not (
            ready_project / SCIENTIFIC_RUNS_RELATIVE / "forged-code-identity"
        ).exists()

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
            "artifact_hashes",
            "authorization_passed",
            "authorization_requested",
            "completion_timestamp",
            "environment_summary",
            "final_manifest_reference",
            "final_manifest_sha256",
            "git_commit",
            "independent_audit_recorded",
            "lifecycle_events",
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


# --------------------------------------------------------------------------- Ticket 2
def _synthetic_provenance():
    return {
        "protocol_version": C.PROTOCOL_VERSION,
        "protocol_path": SAP_RELATIVE.as_posix(),
        "manifest_sha256": "1" * 64,
        "sap_sha256": "2" * 64,
        "cohort_sha256": "3" * 64,
        "split_sha256": "4" * 64,
        "feature_sha256": "5" * 64,
        "feature_file_sha256": "6" * 64,
    }


def _synthetic_inputs():
    rng = np.random.RandomState(20260923)
    activity_ids = tuple(100 * fold + offset for fold in range(1, 6) for offset in range(3))
    outer_folds = tuple(fold for fold in range(1, 6) for _ in range(3))
    scaffold_keys = tuple(f"fold-{fold}-scaffold" for fold in range(1, 6) for _ in range(3))
    features = (rng.random_sample((15, C.MORGAN_SPEC["nBits"])) < 0.04).astype(np.uint8)
    features[:, 0] = 1
    descriptor_axis = np.arange(15, dtype=np.float64)[:, None]
    descriptor_scale = np.arange(1, len(C.DESCRIPTOR_PANEL) + 1, dtype=np.float64)[None, :]
    descriptors = descriptor_axis * descriptor_scale + descriptor_scale / 10.0
    return OutcomeBlindInputs(
        activity_ids=activity_ids,
        outer_folds=outer_folds,
        scaffold_keys=scaffold_keys,
        features=features,
        descriptors=descriptors,
        provenance=_synthetic_provenance(),
    )


class _ForbiddenOuterTestOutcomes:
    def __init__(self, token):
        self.token = token
        self.access_attempts = 0

    def _raise(self):
        self.access_attempts += 1
        raise AssertionError("outer-test outcome accessed before prediction freeze")

    def __getitem__(self, _key):
        self._raise()

    def __iter__(self):
        self._raise()

    def __array__(self, *_args, **_kwargs):
        self._raise()


class _TrainingOnlyProvider:
    def __init__(self, inputs, outer_test_token):
        self._fold_by_id = dict(zip(inputs.activity_ids, inputs.outer_folds))
        self._training_labels = {
            activity_id: np.log10(1.0 + position)
            for position, activity_id in enumerate(inputs.activity_ids, start=1)
        }
        self.outer_test_outcomes = _ForbiddenOuterTestOutcomes(outer_test_token)
        self.calls = []

    def __call__(self, fold, train_ids):
        assert set(train_ids) == {
            activity_id
            for activity_id, assigned_fold in self._fold_by_id.items()
            if assigned_fold != fold
        }
        assert all(self._fold_by_id[activity_id] != fold for activity_id in train_ids)
        self.calls.append((fold, train_ids))
        return {activity_id: self._training_labels[activity_id] for activity_id in train_ids}


def _counting_rf_factory(counter):
    def factory():
        counter["factory_calls"] += 1
        rf = C.make_frozen_rf()
        original_fit = rf.fit

        def counted_fit(X_train, y_train, *args, **kwargs):
            counter["fit_calls"] += 1
            counter["fit_shapes"].append((X_train.shape, y_train.shape))
            return original_fit(X_train, y_train, *args, **kwargs)

        rf.fit = counted_fit
        return rf

    return factory


def _run_synthetic_ticket2(inputs, token):
    provider = _TrainingOnlyProvider(inputs, token)
    counter = {"factory_calls": 0, "fit_calls": 0, "fit_shapes": []}
    audits = []
    freeze = orchestrate_outcome_blind_predictions(
        inputs,
        provider,
        rf_factory=_counting_rf_factory(counter),
        audit_hook=lambda event, payload: audits.append((event, dict(payload))),
    )
    return {"freeze": freeze, "provider": provider, "counter": counter, "audits": audits}


def _expected_id_to_fold(ticket2_synthetic_runs):
    inputs = ticket2_synthetic_runs["inputs"]
    return dict(zip(inputs.activity_ids, inputs.outer_folds))


@pytest.fixture(scope="module")
def ticket2_synthetic_runs():
    inputs = _synthetic_inputs()
    return {
        "inputs": inputs,
        "a": _run_synthetic_ticket2(inputs, "radically-low-test-y"),
        "b": _run_synthetic_ticket2(inputs, "radically-high-test-y"),
    }


class TestGate11NegativeControlsQ1ToQ4:
    def test_test_y_cannot_change_descriptor_scaling(self, ticket2_synthetic_runs):
        inputs = ticket2_synthetic_runs["inputs"]
        train_mask = np.asarray(inputs.outer_folds) != 1
        train_descriptors = inputs.descriptors[train_mask]
        test_descriptors = inputs.descriptors[~train_mask]
        test_y_candidates = (
            np.zeros((~train_mask).sum()),
            np.full((~train_mask).sum(), 1_000_000.0),
        )
        labels_seen = []

        def descriptor_stage(test_y):
            rows = [
                {"is_train": True, "descriptors": row, "y": float(index)}
                for index, row in enumerate(train_descriptors)
            ] + [
                {"is_train": False, "descriptors": row, "y": float(label)}
                for row, label in zip(test_descriptors, test_y)
            ]
            labels_seen.append(tuple(row["y"] for row in rows if not row["is_train"]))
            if not np.isfinite([row["y"] for row in rows]).all():
                raise AssertionError("synthetic labels must be finite")
            selected = np.asarray([row["descriptors"] for row in rows if row["is_train"]])
            scaler, scaled = runner.fit_physchem_space(selected)
            distances = tuple(
                runner.physchem_knn_distance(
                    row["descriptors"], scaled, scaler.mean_, scaler.scale_, k=C.PHYSCHEM_KNN
                )
                for row in rows if not row["is_train"]
            )
            return scaler.mean_.copy(), scaler.scale_.copy(), distances

        observed = [descriptor_stage(test_y) for test_y in test_y_candidates]
        assert labels_seen[0] != labels_seen[1]
        assert observed[0][0].tobytes() == observed[1][0].tobytes()
        assert observed[0][1].tobytes() == observed[1][1].tobytes()
        assert observed[0][2] == observed[1][2]

    def test_test_compound_cannot_improve_tanimoto(self, ticket2_synthetic_runs):
        query = np.asarray([1, 1, 0, 0], dtype=np.uint8)
        outer_training = np.asarray(
            [[1, 0, 1, 0], [0, 1, 0, 1]], dtype=np.uint8
        )
        training_only_score = runner.tanimoto_unfamiliarity(query, outer_training)
        leaked_score = runner.tanimoto_unfamiliarity(
            query, np.vstack([outer_training, query])
        )
        assert training_only_score > 0.0
        assert leaked_score == 0.0
        for _event, audit in ticket2_synthetic_runs["a"]["audits"]:
            assert set(audit["test_ids"]).isdisjoint(audit["tanimoto_reference_ids"])

    def test_test_y_cannot_change_local_sd(self):
        weights = np.asarray([0.2, 0.3, 0.5])
        y_train = np.asarray([1.0, 4.0, 9.0])
        test_y_candidates = (np.asarray([0.0, 0.0]), np.asarray([1000.0, 1000.0]))
        labels_seen = []

        def local_sd_stage(test_y):
            rows = [
                {"is_train": True, "weight": float(weight), "y": float(label)}
                for weight, label in zip(weights, y_train)
            ] + [
                {"is_train": False, "weight": None, "y": float(label)}
                for label in test_y
            ]
            labels_seen.append(tuple(row["y"] for row in rows if not row["is_train"]))
            if not np.isfinite([row["y"] for row in rows]).all():
                raise AssertionError("synthetic labels must be finite")
            training = [row for row in rows if row["is_train"]]
            return runner.local_label_sd(
                np.asarray([row["weight"] for row in training]),
                np.asarray([row["y"] for row in training]),
            )

        observed = [local_sd_stage(test_y) for test_y in test_y_candidates]
        assert labels_seen[0] != labels_seen[1]
        assert observed[0] == observed[1]
        assert observed[0] > 0.0

    def test_test_y_cannot_change_qrf_width(self):
        weights = np.asarray([0.1, 0.2, 0.3, 0.4])
        y_train = np.asarray([1.0, 2.0, 8.0, 16.0])
        test_y_candidates = (np.asarray([-1000.0]), np.asarray([1000.0]))
        labels_seen = []

        def qrf_stage(test_y):
            rows = [
                {"is_train": True, "weight": float(weight), "y": float(label)}
                for weight, label in zip(weights, y_train)
            ] + [
                {"is_train": False, "weight": None, "y": float(label)}
                for label in test_y
            ]
            labels_seen.append(tuple(row["y"] for row in rows if not row["is_train"]))
            if not np.isfinite([row["y"] for row in rows]).all():
                raise AssertionError("synthetic labels must be finite")
            training = [row for row in rows if row["is_train"]]
            return runner.qrf_prediction_quantiles(
                np.asarray([row["weight"] for row in training]),
                np.asarray([row["y"] for row in training]),
                quantiles=(0.10, 0.90),
            )

        quantiles = [qrf_stage(test_y) for test_y in test_y_candidates]
        assert labels_seen[0] != labels_seen[1]
        assert quantiles[0] == quantiles[1]
        assert quantiles[0]["Q90"] - quantiles[0]["Q10"] > 0.0


class TestTicket2OuterFoldOrchestration:
    def test_frozen_loader_exposes_no_outcomes_and_returns_immutable_arrays(self, ready_project):
        inputs = load_outcome_blind_inputs(load_frozen_artifacts(ready_project))
        assert len(inputs.activity_ids) == C.COHORT_N
        assert inputs.features.shape == (C.COHORT_N, C.MORGAN_SPEC["nBits"])
        assert inputs.descriptors.shape == (C.COHORT_N, len(C.DESCRIPTOR_PANEL))
        assert inputs.features.flags.writeable is False
        assert inputs.descriptors.flags.writeable is False
        assert not hasattr(inputs, "outcomes")
        assert not hasattr(inputs, "CLint")

    def test_five_folds_exactly_one_frozen_rf_fit_each(self, ticket2_synthetic_runs):
        for run in (ticket2_synthetic_runs["a"], ticket2_synthetic_runs["b"]):
            assert run["counter"]["factory_calls"] == C.N_FOLDS
            assert run["counter"]["fit_calls"] == C.N_FOLDS
            assert run["counter"]["fit_shapes"] == [((12, 2048), (12,))] * C.N_FOLDS
            assert [fold for fold, _ in run["provider"].calls] == list(range(1, 6))

    def test_train_test_ids_and_scaffolds_are_disjoint(self, ticket2_synthetic_runs):
        inputs = ticket2_synthetic_runs["inputs"]
        scaffold_by_id = dict(zip(inputs.activity_ids, inputs.scaffold_keys))
        for event, audit in ticket2_synthetic_runs["a"]["audits"]:
            assert event == "fold_completed"
            train_ids = set(audit["train_ids"])
            test_ids = set(audit["test_ids"])
            assert train_ids.isdisjoint(test_ids)
            assert {scaffold_by_id[i] for i in train_ids}.isdisjoint(
                {scaffold_by_id[i] for i in test_ids}
            )

    def test_every_reference_pool_is_outer_training_only(self, ticket2_synthetic_runs):
        for _event, audit in ticket2_synthetic_runs["a"]["audits"]:
            expected = audit["train_ids"]
            assert audit["tanimoto_reference_ids"] == expected
            assert audit["descriptor_scaler_fit_ids"] == expected
            assert audit["descriptor_knn_reference_ids"] == expected
            assert audit["qrf_weight_ids"] == expected
            assert audit["local_label_ids"] == expected
            assert set(expected).isdisjoint(audit["test_ids"])

    def test_qrf_weight_and_prediction_invariants_hold(self, ticket2_synthetic_runs):
        for _event, audit in ticket2_synthetic_runs["a"]["audits"]:
            assert audit["qrf_weight_sum_max_error"] < C.WEIGHT_SUM_TOL
            assert audit["qrf_prediction_max_error"] < C.WEIGHT_MEAN_TOL

    def test_outer_test_outcome_change_cannot_change_any_prefreeze_output(
        self, ticket2_synthetic_runs
    ):
        first = ticket2_synthetic_runs["a"]
        second = ticket2_synthetic_runs["b"]
        assert first["provider"].outer_test_outcomes.access_attempts == 0
        assert second["provider"].outer_test_outcomes.access_attempts == 0
        assert first["freeze"].canonical_bytes == second["freeze"].canonical_bytes
        assert first["freeze"].sha256 == second["freeze"].sha256
        assert first["freeze"].read_payload()["records"] == second["freeze"].read_payload()["records"]

    def test_complete_oof_provenance_exactly_once(self, ticket2_synthetic_runs):
        payload = ticket2_synthetic_runs["a"]["freeze"].read_payload()
        ids = [record["activity_id"] for record in payload["records"]]
        assert len(ids) == len(ticket2_synthetic_runs["inputs"].activity_ids)
        assert len(ids) == len(set(ids))
        assert set(ids) == set(ticket2_synthetic_runs["inputs"].activity_ids)
        assert payload["fold_counts"] == {str(fold): 3 for fold in range(1, 6)}

    def test_scaffold_leak_is_rejected_before_fit(self):
        inputs = _synthetic_inputs()
        leaked = list(inputs.scaffold_keys)
        leaked[3] = leaked[0]
        bad = replace(inputs, scaffold_keys=tuple(leaked))
        with pytest.raises(PredictionOrchestrationError, match="scaffold"):
            orchestrate_outcome_blind_predictions(bad, lambda *_: ())

    @pytest.mark.parametrize("replacement", [499, 501])
    def test_altered_rf_parameters_rejected_before_fit(self, replacement):
        inputs = _synthetic_inputs()

        def wrong_factory():
            rf = C.make_frozen_rf()
            rf.set_params(n_estimators=replacement)
            return rf

        with pytest.raises(PredictionOrchestrationError, match="n_estimators"):
            orchestrate_outcome_blind_predictions(
                inputs,
                _TrainingOnlyProvider(inputs, "unused"),
                rf_factory=wrong_factory,
            )

    def test_missing_fold_and_duplicate_id_fail_before_fit(self):
        inputs = _synthetic_inputs()
        missing_fold = replace(inputs, outer_folds=tuple(1 if f == 5 else f for f in inputs.outer_folds))
        with pytest.raises(PredictionOrchestrationError, match="five"):
            orchestrate_outcome_blind_predictions(missing_fold, lambda *_: ())
        duplicate_ids = list(inputs.activity_ids)
        duplicate_ids[-1] = duplicate_ids[0]
        duplicate = replace(inputs, activity_ids=tuple(duplicate_ids))
        with pytest.raises(PredictionOrchestrationError, match="unique"):
            orchestrate_outcome_blind_predictions(duplicate, lambda *_: ())


def _raw_rank_record(activity_id, fold, uncertainty):
    return {
        "activity_id": activity_id,
        "outer_fold": fold,
        "rf_prediction": 1.0,
        "qrf_q10": 0.0,
        "qrf_q90": uncertainty,
        "qrf_width": uncertainty,
        "tanimoto_unfamiliarity": uncertainty,
        "physchem_knn5_distance": uncertainty,
        "neff_inverse": uncertainty,
        "local_label_sd": uncertainty,
        "tree_sd": uncertainty,
    }


class TestTicket2WithinFoldRanking:
    def test_ranking_is_independent_within_each_outer_fold(self):
        records = [
            _raw_rank_record(1, 1, 100.0),
            _raw_rank_record(2, 1, 200.0),
            _raw_rank_record(3, 2, 1.0),
            _raw_rank_record(4, 2, 2.0),
        ]
        ranked = rank_outcome_blind_records(records)
        rank_by_id = {row["activity_id"]: row["within_fold_ranks"]["qrf_width"] for row in ranked}
        assert rank_by_id == {1: 1, 2: 2, 3: 1, 4: 2}

    def test_runner_tie_metadata_matches_configured_known_vector(self):
        activity_id = 10
        ranked = rank_outcome_blind_records([_raw_rank_record(activity_id, 1, 1.0)])
        assert ranked[0]["tie_break_sha256"] == C.retention_tiebreak_hash(activity_id)

    def test_equal_uncertainty_order_uses_configured_hash(self):
        records = [
            _raw_rank_record(10, 1, 1.0),
            _raw_rank_record(20, 1, 1.0),
            _raw_rank_record(30, 1, 1.0),
        ]
        ranked = rank_outcome_blind_records(records)
        ranks = {
            row["activity_id"]: row["within_fold_ranks"]["qrf_width"] for row in ranked
        }
        expected_order = sorted(
            (10, 20, 30),
            key=C.retention_tiebreak_hash,
        )
        actual_order = [
            activity_id for activity_id, _rank in sorted(ranks.items(), key=lambda item: item[1])
        ]
        assert actual_order == expected_order

    def test_equal_uncertainty_order_is_input_shuffle_invariant(self):
        records = [
            _raw_rank_record(10, 1, 1.0),
            _raw_rank_record(20, 1, 1.0),
            _raw_rank_record(30, 1, 1.0),
        ]
        forward = rank_outcome_blind_records(records)
        reverse = rank_outcome_blind_records(list(reversed(records)))
        order = lambda rows: [
            row["activity_id"]
            for row in sorted(rows, key=lambda row: row["within_fold_ranks"]["qrf_width"])
        ]
        assert order(forward) == order(reverse) == sorted(
            (10, 20, 30), key=C.retention_tiebreak_hash
        )

    def test_old_prefix_tie_rule_is_distinguished_and_not_used(self):
        activity_ids = (10, 20, 30)
        configured_order = sorted(activity_ids, key=C.retention_tiebreak_hash)
        old_prefix_hash = lambda activity_id: hashlib.sha256(
            f"V3A_TIE_20260923{activity_id}".encode("utf-8")
        ).hexdigest()
        old_order = sorted(activity_ids, key=old_prefix_hash)
        ranked = rank_outcome_blind_records(
            [_raw_rank_record(activity_id, 1, 1.0) for activity_id in activity_ids]
        )
        runner_order = [
            row["activity_id"]
            for row in sorted(ranked, key=lambda row: row["within_fold_ranks"]["qrf_width"])
        ]
        assert C.retention_tiebreak_hash(activity_ids[0]) != old_prefix_hash(activity_ids[0])
        assert configured_order != old_order
        assert runner_order == configured_order
        assert runner_order != old_order

    def test_retention_metadata_uses_ceil_per_fold(self):
        ranked = rank_outcome_blind_records(
            [_raw_rank_record(activity_id, 1, float(activity_id)) for activity_id in range(1, 4)]
        )
        retained_at_50 = {
            row["activity_id"]
            for row in ranked
            if 0.50 in row["retained_coverages"]["qrf_width"]
        }
        assert retained_at_50 == {1, 2}


class TestTicket2PredictionFreeze:
    def test_freeze_schema_is_outcome_blind_and_complete(self, ticket2_synthetic_runs):
        freeze = ticket2_synthetic_runs["a"]["freeze"]
        payload = freeze.read_payload()
        assert payload["schema_version"] == 1
        assert payload["row_count"] == 15
        assert payload["protocol_version"] == C.PROTOCOL_VERSION
        assert payload["provenance"] == _synthetic_provenance()
        forbidden = {
            "observed_y",
            "residual",
            "absolute_error",
            "squared_error",
            "rmse",
            "mae",
            "error_class",
            "error_enrichment",
        }
        assert all(forbidden.isdisjoint(record) for record in payload["records"])

    def test_partial_four_fold_freeze_is_rejected(self, ticket2_synthetic_runs):
        payload = ticket2_synthetic_runs["a"]["freeze"].read_payload()
        partial = [record for record in payload["records"] if record["outer_fold"] != 5]
        with pytest.raises(PredictionFreezeError, match="five|row count"):
            build_prediction_freeze(
                partial,
                expected_activity_ids=[record["activity_id"] for record in partial],
                expected_outer_folds=[record["outer_fold"] for record in partial],
                provenance=payload["provenance"],
            )

    def test_duplicate_missing_and_missing_field_are_rejected(self, ticket2_synthetic_runs):
        payload = ticket2_synthetic_runs["a"]["freeze"].read_payload()
        records = payload["records"]
        duplicate = records[:-1] + [dict(records[0])]
        with pytest.raises(PredictionFreezeError, match="duplicate"):
            build_prediction_freeze(
                duplicate,
                expected_activity_ids=[record["activity_id"] for record in records],
                expected_outer_folds=[record["outer_fold"] for record in records],
                provenance=payload["provenance"],
            )
        missing_field = [dict(record) for record in records]
        missing_field[0].pop("tree_sd")
        with pytest.raises(PredictionFreezeError, match="fields"):
            build_prediction_freeze(
                missing_field,
                expected_activity_ids=[record["activity_id"] for record in records],
                expected_outer_folds=[record["outer_fold"] for record in records],
                provenance=payload["provenance"],
            )

    def test_changed_frozen_fold_assignment_is_rejected(self, ticket2_synthetic_runs):
        payload = ticket2_synthetic_runs["a"]["freeze"].read_payload()
        records = [dict(record) for record in payload["records"]]
        records[0]["outer_fold"] = 2
        with pytest.raises(PredictionFreezeError, match="outer-fold assignment"):
            build_prediction_freeze(
                records,
                expected_activity_ids=ticket2_synthetic_runs["inputs"].activity_ids,
                expected_outer_folds=ticket2_synthetic_runs["inputs"].outer_folds,
                provenance=payload["provenance"],
            )

    def test_freeze_hash_and_bytes_are_deterministic(self, ticket2_synthetic_runs):
        original = ticket2_synthetic_runs["a"]["freeze"]
        payload = original.read_payload()
        rebuilt = build_prediction_freeze(
            list(reversed(payload["records"])),
            expected_activity_ids=list(reversed(ticket2_synthetic_runs["inputs"].activity_ids)),
            expected_outer_folds=list(reversed(ticket2_synthetic_runs["inputs"].outer_folds)),
            provenance=payload["provenance"],
        )
        assert rebuilt.canonical_bytes == original.canonical_bytes
        assert rebuilt.sha256 == original.sha256
        assert hashlib.sha256(original.canonical_bytes).hexdigest() == original.sha256

    def test_seal_is_exclusive_and_rejects_overwrite(self, ticket2_synthetic_runs, tmp_path):
        freeze = ticket2_synthetic_runs["a"]["freeze"]
        expected = _expected_id_to_fold(ticket2_synthetic_runs)
        path = tmp_path / "prediction_freeze.json"
        sealed = seal_prediction_freeze(freeze, path, expected_id_to_fold=expected)
        assert sealed.verify()
        assert path.read_bytes() == freeze.canonical_bytes
        with pytest.raises(PredictionFreezeCollisionError, match="already exists"):
            seal_prediction_freeze(freeze, path, expected_id_to_fold=expected)
        assert path.read_bytes() == freeze.canonical_bytes

    def test_forged_partial_freeze_object_cannot_be_sealed(self, ticket2_synthetic_runs, tmp_path):
        valid = ticket2_synthetic_runs["a"]["freeze"]
        payload = valid.read_payload()
        payload["records"] = [
            record for record in payload["records"] if record["outer_fold"] != 5
        ]
        payload["row_count"] = len(payload["records"])
        payload["fold_counts"].pop("5")
        partial_bytes = (
            json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("utf-8")
        forged = type(valid)(
            canonical_bytes=partial_bytes,
            sha256=hashlib.sha256(partial_bytes).hexdigest(),
            row_count=len(payload["records"]),
            fold_counts=tuple((fold, 3) for fold in range(1, 5)),
        )
        destination = tmp_path / "forged-partial.json"
        with pytest.raises(PredictionFreezeError, match="five|row count"):
            seal_prediction_freeze(
                forged,
                destination,
                expected_id_to_fold=_expected_id_to_fold(ticket2_synthetic_runs),
            )
        assert not destination.exists()

    def test_downstream_mutation_cannot_change_sealed_bytes(self, ticket2_synthetic_runs, tmp_path):
        freeze = ticket2_synthetic_runs["a"]["freeze"]
        sealed = seal_prediction_freeze(
            freeze,
            tmp_path / "immutable.json",
            expected_id_to_fold=_expected_id_to_fold(ticket2_synthetic_runs),
        )
        detached = freeze.read_payload()
        detached["records"][0]["rf_prediction"] = 999999.0
        detached["records"].clear()
        assert sealed.verify()
        assert sealed.canonical_bytes == freeze.canonical_bytes
        with pytest.raises(FrozenInstanceError):
            freeze.sha256 = "0" * 64


_TEST_BASE_PREDICTION_FIELDS = (
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


def _canonical_test_bytes(payload):
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _alternate_freeze(valid_freeze, mutator):
    payload = valid_freeze.read_payload()
    raw_records = [
        {field: record[field] for field in _TEST_BASE_PREDICTION_FIELDS}
        for record in payload["records"]
    ]
    mutator(raw_records)
    ranked = rank_outcome_blind_records(raw_records)
    alternate_universe = {
        record["activity_id"]: record["outer_fold"] for record in ranked
    }
    return build_prediction_freeze(
        ranked,
        expected_activity_ids=tuple(alternate_universe),
        expected_outer_folds=tuple(alternate_universe.values()),
        provenance=payload["provenance"],
    )


class TestTicket2AtomicFreezePersistence:
    def test_successful_atomic_seal_leaves_exactly_one_final_artifact(
        self, ticket2_synthetic_runs, tmp_path
    ):
        freeze = ticket2_synthetic_runs["a"]["freeze"]
        destination = tmp_path / "prediction_freeze.json"
        sealed = seal_prediction_freeze(
            freeze,
            destination,
            expected_id_to_fold=_expected_id_to_fold(ticket2_synthetic_runs),
        )
        assert list(tmp_path.iterdir()) == [destination]
        assert destination.read_bytes() == freeze.canonical_bytes
        assert sealed.sha256 == hashlib.sha256(destination.read_bytes()).hexdigest()
        assert sealed.verify()

    def test_partial_temporary_write_never_reaches_final_and_is_cleaned(
        self, ticket2_synthetic_runs, tmp_path, monkeypatch
    ):
        freeze = ticket2_synthetic_runs["a"]["freeze"]
        destination = tmp_path / "prediction_freeze.json"

        def fail_after_prefix(descriptor, canonical_bytes):
            os_written = runner.os.write(descriptor, canonical_bytes[:17])
            assert os_written == 17
            raise OSError("injected partial write")

        monkeypatch.setattr(runner, "_write_prediction_freeze_temp", fail_after_prefix)
        with pytest.raises(PredictionFreezeError, match="could not be sealed"):
            seal_prediction_freeze(
                freeze,
                destination,
                expected_id_to_fold=_expected_id_to_fold(ticket2_synthetic_runs),
            )
        assert not destination.exists()
        assert list(tmp_path.iterdir()) == []

    def test_fsync_failure_returns_no_seal_and_cleans_temporary_file(
        self, ticket2_synthetic_runs, tmp_path, monkeypatch
    ):
        freeze = ticket2_synthetic_runs["a"]["freeze"]
        destination = tmp_path / "prediction_freeze.json"

        def fail_fsync(_descriptor):
            raise OSError("injected fsync failure")

        monkeypatch.setattr(runner.os, "fsync", fail_fsync)
        with pytest.raises(PredictionFreezeError, match="could not be sealed"):
            seal_prediction_freeze(
                freeze,
                destination,
                expected_id_to_fold=_expected_id_to_fold(ticket2_synthetic_runs),
            )
        assert not destination.exists()
        assert list(tmp_path.iterdir()) == []

    def test_flush_failure_returns_no_seal_and_cleans_temporary_file(
        self, ticket2_synthetic_runs, tmp_path, monkeypatch
    ):
        freeze = ticket2_synthetic_runs["a"]["freeze"]
        destination = tmp_path / "prediction_freeze.json"
        real_fdopen = runner.os.fdopen

        class FlushFailingHandle:
            def __init__(self, handle):
                self.handle = handle

            def __enter__(self):
                return self

            def __exit__(self, _exc_type, _exc, _traceback):
                self.handle.close()
                return False

            def write(self, data):
                return self.handle.write(data)

            def flush(self):
                raise OSError("injected flush failure")

            def fileno(self):
                return self.handle.fileno()

        def failing_fdopen(*args, **kwargs):
            return FlushFailingHandle(real_fdopen(*args, **kwargs))

        monkeypatch.setattr(runner.os, "fdopen", failing_fdopen)
        with pytest.raises(PredictionFreezeError, match="could not be sealed"):
            seal_prediction_freeze(
                freeze,
                destination,
                expected_id_to_fold=_expected_id_to_fold(ticket2_synthetic_runs),
            )
        assert not destination.exists()
        assert list(tmp_path.iterdir()) == []

    def test_finalization_failure_never_exposes_final_and_cleans_temp(
        self, ticket2_synthetic_runs, tmp_path, monkeypatch
    ):
        freeze = ticket2_synthetic_runs["a"]["freeze"]
        destination = tmp_path / "prediction_freeze.json"

        def fail_finalization(temporary_path, final_path):
            assert temporary_path.parent == final_path.parent == tmp_path
            assert temporary_path.is_file()
            assert not final_path.exists()
            raise OSError("injected atomic-link failure")

        monkeypatch.setattr(
            runner, "_finalize_prediction_freeze_no_clobber", fail_finalization
        )
        with pytest.raises(PredictionFreezeError, match="could not be sealed"):
            seal_prediction_freeze(
                freeze,
                destination,
                expected_id_to_fold=_expected_id_to_fold(ticket2_synthetic_runs),
            )
        assert not destination.exists()
        assert list(tmp_path.iterdir()) == []

    def test_temporary_name_is_same_directory_and_never_treated_as_sealed(
        self, ticket2_synthetic_runs, tmp_path, monkeypatch
    ):
        freeze = ticket2_synthetic_runs["a"]["freeze"]
        destination = tmp_path / "prediction_freeze.json"
        observed = {}

        def inspect_then_fail(temporary_path, final_path):
            observed["temporary"] = temporary_path
            assert temporary_path.parent == final_path.parent
            assert temporary_path.name.startswith(f".{final_path.name}.")
            assert temporary_path.name.endswith(".tmp")
            assert temporary_path.read_bytes() == freeze.canonical_bytes
            assert not final_path.exists()
            raise OSError("stop before commit point")

        monkeypatch.setattr(
            runner, "_finalize_prediction_freeze_no_clobber", inspect_then_fail
        )
        with pytest.raises(PredictionFreezeError):
            seal_prediction_freeze(
                freeze,
                destination,
                expected_id_to_fold=_expected_id_to_fold(ticket2_synthetic_runs),
            )
        assert observed["temporary"] != destination
        assert not destination.exists()
        assert not observed["temporary"].exists()

    def test_racing_destination_creation_cannot_be_overwritten(
        self, ticket2_synthetic_runs, tmp_path, monkeypatch
    ):
        freeze = ticket2_synthetic_runs["a"]["freeze"]
        destination = tmp_path / "prediction_freeze.json"
        competitor_bytes = b"independent-existing-freeze"
        real_finalizer = runner._finalize_prediction_freeze_no_clobber

        def create_competitor_then_finalize(temporary_path, final_path):
            final_path.write_bytes(competitor_bytes)
            real_finalizer(temporary_path, final_path)

        monkeypatch.setattr(
            runner,
            "_finalize_prediction_freeze_no_clobber",
            create_competitor_then_finalize,
        )
        with pytest.raises(PredictionFreezeCollisionError, match="already exists"):
            seal_prediction_freeze(
                freeze,
                destination,
                expected_id_to_fold=_expected_id_to_fold(ticket2_synthetic_runs),
            )
        assert destination.read_bytes() == competitor_bytes
        assert list(tmp_path.iterdir()) == [destination]


class TestTicket2SealExpectedUniverse:
    def test_expected_universe_is_mandatory(self, ticket2_synthetic_runs, tmp_path):
        with pytest.raises(TypeError, match="expected_id_to_fold"):
            seal_prediction_freeze(
                ticket2_synthetic_runs["a"]["freeze"],
                tmp_path / "must-not-seal.json",
            )

    def test_expected_id_missing_is_rejected(self, ticket2_synthetic_runs, tmp_path):
        expected = _expected_id_to_fold(ticket2_synthetic_runs)
        expected.pop(next(iter(expected)))
        destination = tmp_path / "missing-expected.json"
        with pytest.raises(PredictionFreezeError, match="row count|activity-ID set"):
            seal_prediction_freeze(
                ticket2_synthetic_runs["a"]["freeze"],
                destination,
                expected_id_to_fold=expected,
            )
        assert not destination.exists()

    def test_substituted_id_with_same_row_count_and_five_folds_is_rejected(
        self, ticket2_synthetic_runs, tmp_path
    ):
        valid = ticket2_synthetic_runs["a"]["freeze"]

        def substitute(records):
            records[0]["activity_id"] = 999_001

        forged = _alternate_freeze(valid, substitute)
        forged_payload = forged.read_payload()
        assert forged.row_count == valid.row_count
        assert set(record["outer_fold"] for record in forged_payload["records"]) == set(range(1, 6))
        destination = tmp_path / "substituted.json"
        with pytest.raises(PredictionFreezeError, match="activity-ID set"):
            seal_prediction_freeze(
                forged,
                destination,
                expected_id_to_fold=_expected_id_to_fold(ticket2_synthetic_runs),
            )
        assert not destination.exists()

    def test_actual_missing_id_is_rejected(self, ticket2_synthetic_runs, tmp_path):
        valid = ticket2_synthetic_runs["a"]["freeze"]
        forged = _alternate_freeze(valid, lambda records: records.pop(0))
        destination = tmp_path / "actual-missing.json"
        with pytest.raises(PredictionFreezeError, match="row count"):
            seal_prediction_freeze(
                forged,
                destination,
                expected_id_to_fold=_expected_id_to_fold(ticket2_synthetic_runs),
            )
        assert not destination.exists()

    def test_actual_extra_id_is_rejected(self, ticket2_synthetic_runs, tmp_path):
        valid = ticket2_synthetic_runs["a"]["freeze"]

        def add_extra(records):
            extra = dict(records[0])
            extra["activity_id"] = 999_002
            records.append(extra)

        forged = _alternate_freeze(valid, add_extra)
        destination = tmp_path / "actual-extra.json"
        with pytest.raises(PredictionFreezeError, match="row count"):
            seal_prediction_freeze(
                forged,
                destination,
                expected_id_to_fold=_expected_id_to_fold(ticket2_synthetic_runs),
            )
        assert not destination.exists()

    def test_correct_ids_with_wrong_fold_and_fold_counts_are_rejected(
        self, ticket2_synthetic_runs, tmp_path
    ):
        valid = ticket2_synthetic_runs["a"]["freeze"]

        def move_fold(records):
            records[0]["outer_fold"] = 2

        forged = _alternate_freeze(valid, move_fold)
        destination = tmp_path / "wrong-fold.json"
        with pytest.raises(PredictionFreezeError, match="ID-to-fold mapping"):
            seal_prediction_freeze(
                forged,
                destination,
                expected_id_to_fold=_expected_id_to_fold(ticket2_synthetic_runs),
            )
        assert not destination.exists()

    def test_manually_constructed_duplicate_id_freeze_is_rejected(
        self, ticket2_synthetic_runs, tmp_path
    ):
        valid = ticket2_synthetic_runs["a"]["freeze"]
        payload = valid.read_payload()
        payload["records"][-1]["activity_id"] = payload["records"][0]["activity_id"]
        payload["records"][-1]["tie_break_sha256"] = payload["records"][0][
            "tie_break_sha256"
        ]
        forged_bytes = _canonical_test_bytes(payload)
        forged = type(valid)(
            canonical_bytes=forged_bytes,
            sha256=hashlib.sha256(forged_bytes).hexdigest(),
            row_count=valid.row_count,
            fold_counts=valid.fold_counts,
        )
        destination = tmp_path / "duplicate.json"
        with pytest.raises(PredictionFreezeError, match="duplicate"):
            seal_prediction_freeze(
                forged,
                destination,
                expected_id_to_fold=_expected_id_to_fold(ticket2_synthetic_runs),
            )
        assert not destination.exists()


def test_ticket3_scope_excludes_later_analysis_stages():
    imported_or_called = set()
    for function in (prepare_postfreeze_plan, evaluate_postfreeze):
        tree = ast.parse(inspect.getsource(function))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                imported_or_called.add(node.func.id)
    prohibited = {
        "matched_random_retention_rmse",
        "scaffold_bootstrap_indices",
        "interval_calibration_summary",
    }
    assert imported_or_called.isdisjoint(prohibited)


def _ticket3_raw_records():
    records = []
    fold_sizes = {1: 3, 2: 4, 3: 5, 4: 6, 5: 7}
    for fold, size in fold_sizes.items():
        for offset in range(size):
            activity_id = fold * 100 + offset
            uncertainty = float(fold * 100 + offset)
            record = _raw_rank_record(activity_id, fold, uncertainty)
            record["rf_prediction"] = fold / 10.0 + offset / 100.0
            records.append(record)
    return records


@pytest.fixture(scope="module")
def ticket3_bundle(tmp_path_factory):
    raw_records = _ticket3_raw_records()
    ranked = rank_outcome_blind_records(raw_records)
    expected = {record["activity_id"]: record["outer_fold"] for record in ranked}
    freeze = build_prediction_freeze(
        ranked,
        expected_activity_ids=tuple(expected),
        expected_outer_folds=tuple(expected.values()),
        provenance=_synthetic_provenance(),
    )
    seal_path = tmp_path_factory.mktemp("ticket3-seal") / "prediction_freeze.json"
    sealed = seal_prediction_freeze(freeze, seal_path, expected_id_to_fold=expected)
    plan = prepare_postfreeze_plan(sealed, expected_id_to_fold=expected)
    payload = freeze.read_payload()
    outcomes = []
    alternate_outcomes = []
    fold_sizes = {1: 3, 2: 4, 3: 5, 4: 6, 5: 7}
    for record in payload["records"]:
        fold = record["outer_fold"]
        offset = record["activity_id"] - fold * 100
        outcomes.append(
            {
                "activity_id": record["activity_id"],
                "outer_fold": fold,
                "observed_y": record["rf_prediction"] + fold * (offset + 1) / 10.0,
            }
        )
        alternate_outcomes.append(
            {
                "activity_id": record["activity_id"],
                "outer_fold": fold,
                "observed_y": record["rf_prediction"]
                + (fold_sizes[fold] - offset) * (6 - fold) / 8.0,
            }
        )
    return {
        "raw_records": raw_records,
        "freeze": freeze,
        "sealed": sealed,
        "expected": expected,
        "plan": plan,
        "payload": payload,
        "outcomes": outcomes,
        "alternate_outcomes": alternate_outcomes,
    }


@pytest.fixture(scope="module")
def ticket3_results(ticket3_bundle):
    return {
        "original": evaluate_postfreeze(ticket3_bundle["plan"], ticket3_bundle["outcomes"]),
        "shuffled": evaluate_postfreeze(
            ticket3_bundle["plan"], list(reversed(ticket3_bundle["outcomes"]))
        ),
        "alternate": evaluate_postfreeze(
            ticket3_bundle["plan"], ticket3_bundle["alternate_outcomes"]
        ),
    }


def _result_metric_signature(result):
    return tuple(
        (
            curve.method,
            curve.role,
            curve.naurc,
            tuple(
                (
                    point.coverage,
                    point.retained_n,
                    point.deferred_n,
                    point.pooled_rmse,
                    point.pooled_mae,
                    point.retained_ids,
                    point.retained_counts_by_fold,
                )
                for point in curve.points
            ),
        )
        for curve in result.coverage_curves
    )


def _draw_with_one_same_fold_substitution(draw, expected_id_to_fold):
    replacement = list(draw)
    retained = set(draw)
    for position, activity_id in enumerate(draw):
        fold = expected_id_to_fold[activity_id]
        candidates = [
            candidate
            for candidate, candidate_fold in expected_id_to_fold.items()
            if candidate_fold == fold and candidate not in retained
        ]
        if candidates:
            replacement[position] = sorted(candidates, key=str)[0]
            return tuple(replacement)
    raise AssertionError("synthetic fixture has no same-fold substitution candidate")


def _forged_plan_with_substituted_draws(plan, expected_id_to_fold, draw_indices):
    draws = list(plan.random_retained_ids_by_draw)
    for draw_index in draw_indices:
        draws[draw_index] = _draw_with_one_same_fold_substitution(
            draws[draw_index], expected_id_to_fold
        )
    return replace(plan, random_retained_ids_by_draw=tuple(draws))


def _canonical_random_stream_for_seed(records, qrf80, seed):
    fold_tokens = {}
    id_by_token = {}
    for token, record in enumerate(records):
        fold_tokens.setdefault(record["outer_fold"], []).append(token)
        id_by_token[token] = record["activity_id"]
    samples = matched_random_rankings(
        fold_tokens,
        n_random=C.N_RANDOM_DEFERRALS,
        seed=seed,
        coverage=C.PRIMARY_COVERAGE,
    )
    expected_counts = dict(qrf80.retained_counts_by_fold)
    draws = []
    for draw_index in range(C.N_RANDOM_DEFERRALS):
        assert all(
            len(samples[fold][draw_index]) == expected_counts[fold]
            for fold in range(1, C.N_FOLDS + 1)
        )
        draws.append(
            tuple(
                id_by_token[token]
                for fold in range(1, C.N_FOLDS + 1)
                for token in sorted(samples[fold][draw_index])
            )
        )
    return tuple(draws)


def _outcome_informed_forged_plan(ticket3_bundle):
    plan = ticket3_bundle["plan"]
    observed = {
        row["activity_id"]: row["observed_y"] for row in ticket3_bundle["outcomes"]
    }
    predicted = {
        row["activity_id"]: row["rf_prediction"]
        for row in ticket3_bundle["payload"]["records"]
    }
    outcome_informed_draw = tuple(
        activity_id
        for fold, count in plan.random_retained_counts_by_fold
        for activity_id in sorted(
            (
                activity_id
                for activity_id, assigned_fold in ticket3_bundle["expected"].items()
                if assigned_fold == fold
            ),
            key=lambda activity_id: abs(observed[activity_id] - predicted[activity_id]),
            reverse=True,
        )[:count]
    )
    return replace(
        plan,
        random_retained_ids_by_draw=(outcome_informed_draw,) * C.N_RANDOM_DEFERRALS,
    )


class TestTicket3OutcomeGateAndAlignment:
    def test_unsealed_freeze_is_rejected_before_outcome_access(self, ticket3_bundle):
        with pytest.raises(OutcomeEvaluationError, match="sealed"):
            prepare_postfreeze_plan(
                ticket3_bundle["freeze"],
                expected_id_to_fold=ticket3_bundle["expected"],
            )

    def test_invalid_seal_hash_is_rejected(self, ticket3_bundle):
        tampered = replace(ticket3_bundle["sealed"], sha256="0" * 64)
        with pytest.raises(OutcomeEvaluationError, match="seal|hash"):
            prepare_postfreeze_plan(
                tampered,
                expected_id_to_fold=ticket3_bundle["expected"],
            )

    def test_downstream_expected_universe_is_reverified(self, ticket3_bundle):
        incomplete = dict(ticket3_bundle["expected"])
        incomplete.pop(next(iter(incomplete)))
        with pytest.raises(OutcomeEvaluationError, match="invalid|validation|incomplete"):
            prepare_postfreeze_plan(
                ticket3_bundle["sealed"],
                expected_id_to_fold=incomplete,
            )

    def test_direct_evaluator_call_before_plan_fails_without_reading_outcomes(
        self, ticket3_bundle
    ):
        class OutcomeSentinel:
            accessed = False

            def __iter__(self):
                self.accessed = True
                raise AssertionError("outcomes accessed before valid freeze")

        sentinel = OutcomeSentinel()
        with pytest.raises(OutcomeEvaluationError, match="post-freeze plan"):
            evaluate_postfreeze(ticket3_bundle["freeze"], sentinel)
        assert sentinel.accessed is False

    def test_shuffled_outcomes_are_identical(self, ticket3_results):
        original = ticket3_results["original"]
        shuffled = ticket3_results["shuffled"]
        assert _result_metric_signature(original) == _result_metric_signature(shuffled)
        assert original.rel_benefit_80 == shuffled.rel_benefit_80
        assert np.array_equal(
            original.matched_random80.rmse_draws,
            shuffled.matched_random80.rmse_draws,
        )

    @pytest.mark.parametrize("mutation, message", [
        (lambda rows: rows.pop(), "missing"),
        (
            lambda rows: rows.append(
                {"activity_id": 999999, "outer_fold": 1, "observed_y": 1.0}
            ),
            "extra",
        ),
        (lambda rows: rows.append(dict(rows[0])), "duplicate"),
    ])
    def test_missing_extra_and_duplicate_outcomes_rejected(
        self, ticket3_bundle, mutation, message
    ):
        rows = [dict(row) for row in ticket3_bundle["outcomes"]]
        mutation(rows)
        with pytest.raises(OutcomeEvaluationError, match=message):
            evaluate_postfreeze(ticket3_bundle["plan"], rows)

    def test_wrong_supplied_fold_is_rejected(self, ticket3_bundle):
        rows = [dict(row) for row in ticket3_bundle["outcomes"]]
        rows[0]["outer_fold"] = 2 if rows[0]["outer_fold"] == 1 else 1
        with pytest.raises(OutcomeEvaluationError, match="outer_fold"):
            evaluate_postfreeze(ticket3_bundle["plan"], rows)

    @pytest.mark.parametrize("bad_value", [np.nan, np.inf, -np.inf])
    def test_nonfinite_outcome_is_rejected(self, ticket3_bundle, bad_value):
        rows = [dict(row) for row in ticket3_bundle["outcomes"]]
        rows[0]["observed_y"] = bad_value
        with pytest.raises(OutcomeEvaluationError, match="finite"):
            evaluate_postfreeze(ticket3_bundle["plan"], rows)


class TestTicket3RetentionAndCoverage:
    def test_global_ranking_differs_and_plan_uses_fold_local_ids(self, ticket3_bundle):
        plan = ticket3_bundle["plan"]
        local_ids = set(plan.retention("qrf_width", 0.50).retained_ids)
        globally_ranked = sorted(
            ticket3_bundle["raw_records"],
            key=lambda row: (row["qrf_width"], row["activity_id"]),
        )
        global_ids = {
            row["activity_id"]
            for row in globally_ranked[: math.ceil(0.50 * len(globally_ranked))]
        }
        assert local_ids != global_ids
        for fold in range(1, 6):
            fold_rows = [
                row for row in ticket3_bundle["raw_records"] if row["outer_fold"] == fold
            ]
            expected_local = {
                row["activity_id"]
                for row in sorted(fold_rows, key=lambda row: row["qrf_width"])[
                    : math.ceil(0.50 * len(fold_rows))
                ]
            }
            assert {activity_id for activity_id in local_ids if activity_id // 100 == fold} == expected_local

    def test_all_six_coverages_use_exact_ceil_counts(self, ticket3_bundle):
        plan = ticket3_bundle["plan"]
        fold_sizes = {1: 3, 2: 4, 3: 5, 4: 6, 5: 7}
        for method in runner._UNCERTAINTY_FIELDS:
            for coverage in C.COVERAGE_LEVELS:
                retention = plan.retention(method, coverage)
                assert dict(retention.retained_counts_by_fold) == {
                    fold: math.ceil(coverage * size) for fold, size in fold_sizes.items()
                }

    def test_qrf80_exact_per_fold_counts(self, ticket3_bundle):
        assert dict(
            ticket3_bundle["plan"].retention("qrf_width", 0.80).retained_counts_by_fold
        ) == {1: 3, 2: 4, 3: 4, 4: 5, 5: 6}

    def test_result_contains_six_points_and_both_metrics(self, ticket3_results):
        result = ticket3_results["original"]
        assert len(result.coverage_curves) == 6
        assert result.curve("qrf_width").role == "PRIMARY"
        assert all(curve.role == "SECONDARY" for curve in result.coverage_curves[1:])
        for curve in result.coverage_curves:
            assert tuple(point.coverage for point in curve.points) == C.COVERAGE_LEVELS
            assert all(np.isfinite(point.pooled_rmse) for point in curve.points)
            assert all(np.isfinite(point.pooled_mae) for point in curve.points)

    def test_pooled_rmse_is_not_mean_fold_rmse(self, ticket3_bundle, ticket3_results):
        point = ticket3_results["original"].qrf80
        outcome_by_id = {
            row["activity_id"]: row["observed_y"] for row in ticket3_bundle["outcomes"]
        }
        prediction_by_id = {
            row["activity_id"]: row["rf_prediction"]
            for row in ticket3_bundle["payload"]["records"]
        }
        pooled = rmse(
            [outcome_by_id[i] for i in point.retained_ids],
            [prediction_by_id[i] for i in point.retained_ids],
        )
        fold_rmses = []
        for fold in range(1, 6):
            ids = [i for i in point.retained_ids if ticket3_bundle["expected"][i] == fold]
            fold_rmses.append(
                rmse([outcome_by_id[i] for i in ids], [prediction_by_id[i] for i in ids])
            )
        assert point.pooled_rmse == pytest.approx(pooled)
        assert point.pooled_rmse != pytest.approx(np.mean(fold_rmses))


class TestTicket3MatchedRandomAndEstimand:
    def test_canonical_seeded_plan_is_accepted(self, ticket3_results):
        assert ticket3_results["original"].matched_random80.draw_count == 10_000

    def test_exact_production_draw_count_seed_and_per_fold_counts(self, ticket3_bundle):
        plan = ticket3_bundle["plan"]
        assert plan.random_draw_count == C.N_RANDOM_DEFERRALS == 10_000
        assert plan.random_seed == C.MASTER_SEED == 20260923
        expected_counts = dict(plan.retention("qrf_width", 0.80).retained_counts_by_fold)
        assert dict(plan.random_retained_counts_by_fold) == expected_counts
        for draw in plan.random_retained_ids_by_draw:
            actual = {
                fold: sum(ticket3_bundle["expected"][activity_id] == fold for activity_id in draw)
                for fold in range(1, 6)
            }
            assert actual == expected_counts

    def test_random_draw_stream_is_deterministic(self, ticket3_bundle):
        repeated = prepare_postfreeze_plan(
            ticket3_bundle["sealed"],
            expected_id_to_fold=ticket3_bundle["expected"],
        )
        assert repeated.random_retained_ids_by_draw == (
            ticket3_bundle["plan"].random_retained_ids_by_draw
        )

    def test_one_draw_one_same_fold_id_substitution_is_rejected(self, ticket3_bundle):
        forged = _forged_plan_with_substituted_draws(
            ticket3_bundle["plan"], ticket3_bundle["expected"], [0]
        )
        assert forged.random_draw_count == 10_000
        assert forged.random_seed == 20260923
        with pytest.raises(OutcomeEvaluationError, match="canonical seeded draw stream"):
            runner._validate_postfreeze_plan(forged)

    def test_many_same_count_draw_substitutions_are_rejected(self, ticket3_bundle):
        forged = _forged_plan_with_substituted_draws(
            ticket3_bundle["plan"], ticket3_bundle["expected"], range(0, 100, 7)
        )
        with pytest.raises(OutcomeEvaluationError, match="canonical seeded draw stream"):
            runner._validate_postfreeze_plan(forged)

    def test_draw_order_tampering_is_rejected(self, ticket3_bundle):
        plan = ticket3_bundle["plan"]
        draws = list(plan.random_retained_ids_by_draw)
        other_index = next(index for index, draw in enumerate(draws[1:], 1) if draw != draws[0])
        draws[0], draws[other_index] = draws[other_index], draws[0]
        forged = replace(plan, random_retained_ids_by_draw=tuple(draws))
        with pytest.raises(OutcomeEvaluationError, match="canonical seeded draw stream"):
            runner._validate_postfreeze_plan(forged)

    def test_other_seed_ids_disguised_with_frozen_seed_metadata_are_rejected(
        self, ticket3_bundle
    ):
        plan = ticket3_bundle["plan"]
        other_seed_draws = _canonical_random_stream_for_seed(
            ticket3_bundle["payload"]["records"],
            plan.retention("qrf_width", C.PRIMARY_COVERAGE),
            C.MASTER_SEED + 1,
        )
        assert len(other_seed_draws) == C.N_RANDOM_DEFERRALS
        assert other_seed_draws != plan.random_retained_ids_by_draw
        forged = replace(
            plan,
            random_retained_ids_by_draw=other_seed_draws,
            random_seed=C.MASTER_SEED,
        )
        with pytest.raises(OutcomeEvaluationError, match="canonical seeded draw stream"):
            runner._validate_postfreeze_plan(forged)

    def test_seed_metadata_value_tampering_is_rejected(self, ticket3_bundle):
        forged = replace(ticket3_bundle["plan"], random_seed=C.MASTER_SEED + 1)
        with pytest.raises(OutcomeEvaluationError, match="differs from the SAP"):
            runner._validate_postfreeze_plan(forged)

    def test_valid_seed_metadata_with_wrong_generated_ids_is_rejected(self, ticket3_bundle):
        forged = _forged_plan_with_substituted_draws(
            ticket3_bundle["plan"], ticket3_bundle["expected"], [9999]
        )
        assert forged.random_seed == C.MASTER_SEED
        with pytest.raises(OutcomeEvaluationError, match="canonical seeded draw stream"):
            runner._validate_postfreeze_plan(forged)

    def test_outcome_informed_same_count_plan_is_rejected(self, ticket3_bundle):
        forged = _outcome_informed_forged_plan(ticket3_bundle)
        with pytest.raises(OutcomeEvaluationError, match="canonical seeded draw stream"):
            evaluate_postfreeze(forged, ticket3_bundle["outcomes"])

    def test_forged_plan_is_rejected_before_outcome_provider_access(self, ticket3_bundle):
        class OutcomeSentinel:
            access_count = 0

            def __iter__(self):
                self.access_count += 1
                raise AssertionError("outcome provider must not be touched")

        forged = _outcome_informed_forged_plan(ticket3_bundle)
        sentinel = OutcomeSentinel()
        with pytest.raises(OutcomeEvaluationError, match="canonical seeded draw stream"):
            evaluate_postfreeze(forged, sentinel)
        assert sentinel.access_count == 0

    def test_canonical_stream_is_invariant_to_input_row_order(
        self, ticket3_bundle, tmp_path
    ):
        ranked = rank_outcome_blind_records(list(reversed(ticket3_bundle["raw_records"])))
        expected = {record["activity_id"]: record["outer_fold"] for record in ranked}
        freeze = build_prediction_freeze(
            ranked,
            expected_activity_ids=tuple(expected),
            expected_outer_folds=tuple(expected.values()),
            provenance=_synthetic_provenance(),
        )
        assert freeze.canonical_bytes == ticket3_bundle["freeze"].canonical_bytes
        sealed = seal_prediction_freeze(
            freeze,
            tmp_path / "shuffled_prediction_freeze.json",
            expected_id_to_fold=expected,
        )
        shuffled_plan = prepare_postfreeze_plan(sealed, expected_id_to_fold=expected)
        assert shuffled_plan.random_retained_ids_by_draw == (
            ticket3_bundle["plan"].random_retained_ids_by_draw
        )

    def test_test_y_cannot_change_retained_ids(
        self, ticket3_bundle, ticket3_results
    ):
        draws_before = ticket3_bundle["plan"].random_retained_ids_by_draw
        qrf_before = ticket3_bundle["plan"].retention("qrf_width", 0.80).retained_ids
        original = ticket3_results["original"]
        alternate = ticket3_results["alternate"]
        assert original.qrf80.retained_ids == alternate.qrf80.retained_ids
        assert ticket3_bundle["plan"].random_retained_ids_by_draw == draws_before
        assert ticket3_bundle["plan"].retention("qrf_width", 0.80).retained_ids == qrf_before
        assert tuple(inspect.signature(prepare_postfreeze_plan).parameters) == (
            "sealed_freeze",
            "expected_id_to_fold",
        )
        assert not np.array_equal(
            original.matched_random80.rmse_draws,
            alternate.matched_random80.rmse_draws,
        )

    def test_random_baseline_is_mean_of_all_pooled_rmse_draws(self, ticket3_results):
        random_result = ticket3_results["original"].matched_random80
        assert random_result.draw_count == 10_000
        assert random_result.rmse_draws.shape == (10_000,)
        assert random_result.rmse_draws.flags.writeable is False
        assert random_result.mean_rmse == pytest.approx(random_result.rmse_draws.mean())
        assert random_result.mean_rmse != pytest.approx(np.median(random_result.rmse_draws))

    def test_rel_benefit_formula_and_known_numeric_fixture(self, ticket3_results):
        result = ticket3_results["original"]
        expected = (
            result.matched_random80.mean_rmse - result.qrf80.pooled_rmse
        ) / result.matched_random80.mean_rmse
        assert result.rel_benefit_80 == pytest.approx(expected)
        assert rel_benefit_80(4.0, 3.0) == pytest.approx(0.25)

    def test_naurc_known_fixture_and_result_is_secondary(self, ticket3_results):
        assert trapezoidal_naurc(
            np.asarray([0.50, 0.60, 0.70, 0.80, 0.90, 1.00]),
            np.asarray([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]),
        ) == pytest.approx(3.5)
        result = ticket3_results["original"]
        curve = result.curve("qrf_width")
        assert curve.naurc == pytest.approx(
            trapezoidal_naurc(
                np.asarray([point.coverage for point in curve.points]),
                np.asarray([point.pooled_rmse for point in curve.points]),
            )
        )
        assert result.primary_method == "qrf_width"
        assert result.primary_coverage == 0.80
        assert not hasattr(result, "primary_naurc")


class TestTicket3Nonmutation:
    def test_outcomes_change_only_downstream_metrics(self, ticket3_bundle, ticket3_results):
        before_bytes = ticket3_bundle["freeze"].canonical_bytes
        before_hash = ticket3_bundle["freeze"].sha256
        before_file = ticket3_bundle["sealed"].path.read_bytes()
        original = ticket3_results["original"]
        alternate = ticket3_results["alternate"]
        assert _result_metric_signature(original) != _result_metric_signature(alternate)
        assert original.rel_benefit_80 != alternate.rel_benefit_80
        assert original.qrf80.retained_ids == alternate.qrf80.retained_ids
        assert ticket3_bundle["freeze"].canonical_bytes == before_bytes
        assert ticket3_bundle["freeze"].sha256 == before_hash
        assert ticket3_bundle["sealed"].path.read_bytes() == before_file
        assert ticket3_bundle["sealed"].verify()


class TestTicket3ThreeStateClassifier:
    @pytest.mark.parametrize(
        "point, lower, upper, expected",
        [
            (0.10, 0.001, 0.20, "SUPPORTED_OPERATIONAL_SIGNAL"),
            (0.099, 0.001, 0.20, "INCONCLUSIVE"),
            (0.10, 0.0, 0.20, "INCONCLUSIVE"),
            (0.05, -0.10, 0.099, "EVIDENCE_BELOW_PRACTICAL_THRESHOLD"),
            (0.05, -0.10, 0.10, "INCONCLUSIVE"),
            (0.20, -0.01, 0.30, "INCONCLUSIVE"),
        ],
    )
    def test_exact_three_state_boundaries(self, point, lower, upper, expected):
        assert classify_rel_benefit_80(point, lower, upper) == expected

    def test_classifier_has_no_p_value_input(self):
        assert tuple(inspect.signature(classify_rel_benefit_80).parameters) == (
            "point_estimate",
            "ci_lower",
            "ci_upper",
        )
        with pytest.raises(TypeError):
            classify_rel_benefit_80(0.10, 0.01, 0.20, p_value=0.001)


# =========================================================================== Ticket 4
def _ticket4_records():
    rows = []
    for fold in (1, 2):
        for scaffold_number in (1, 2):
            for within in (0, 1):
                activity_id = fold * 100 + scaffold_number * 10 + within
                rows.append(
                    {
                        "activity_id": activity_id,
                        "outer_fold": fold,
                        "scaffold_key": f"F{fold}S{scaffold_number}",
                        "rf_prediction": float(within),
                        "qrf_width": float(scaffold_number + within / 10),
                        "observed_y": float(within + scaffold_number),
                        "observed_clint": 25.0 if within == 0 else 30.0,
                        "standard_relation": None,
                    }
                )
    return rows


class TestTicket4PrimaryBootstrap:
    def test_scaffold_fold_multiplicity_and_exact_k_star(self):
        records = _ticket4_records()
        plans = runner.primary_bootstrap_plan(records, n_bootstrap=12, n_random=3, seed=20260923)
        assert len(plans) == 12
        saw_duplicate = False
        for plan in plans:
            occurrences = plan["occurrences"]
            for fold, n_candidates in plan["candidate_counts"]:
                assert dict(plan["retained_counts"])[fold] == math.ceil(0.8 * n_candidates)
                assert all(item["outer_fold"] == fold for item in occurrences if item["outer_fold"] == fold)
            ids = [item["activity_id"] for item in occurrences]
            saw_duplicate |= len(ids) != len(set(ids))
            for draw in plan["random_draws"]:
                assert len(draw) == sum(count for _, count in plan["retained_counts"])
                assert len(set(draw)) == len(draw)
        assert saw_duplicate

    def test_occurrence_identity_and_plan_are_shuffle_invariant(self):
        records = _ticket4_records()
        shuffled = list(reversed(records))
        first = runner.primary_bootstrap_plan(records, n_bootstrap=4, n_random=5)
        second = runner.primary_bootstrap_plan(shuffled, n_bootstrap=4, n_random=5)
        assert first == second
        identities = [
            item["occurrence_id"] for replicate in first for item in replicate["occurrences"]
        ]
        assert len(identities) == len(set(identities))

    def test_test_y_cannot_change_bootstrap_draws(self):
        records = _ticket4_records()
        altered = [dict(row, observed_y=10_000.0 - row["observed_y"]) for row in records]
        plan_a = runner.primary_bootstrap_plan(records, n_bootstrap=3, n_random=7)
        plan_b = runner.primary_bootstrap_plan(altered, n_bootstrap=3, n_random=7)
        assert plan_a == plan_b

    def test_reselection_uses_occurrences_not_original_mask(self):
        records = _ticket4_records()
        plan = runner.primary_bootstrap_plan(records, n_bootstrap=8, n_random=2)
        replicate = next(
            item for item in plan
            if len({occ["activity_id"] for occ in item["occurrences"]})
            < len(item["occurrences"])
        )
        retained_ids = [
            replicate["occurrences"][index]["activity_id"]
            for index in replicate["qrf_selected"]
        ]
        assert len(retained_ids) == sum(count for _, count in replicate["retained_counts"])
        assert len(retained_ids) > len(set(retained_ids)) or any(
            retained_ids.count(item) < [o["activity_id"] for o in replicate["occurrences"]].count(item)
            for item in set(retained_ids)
        )

    def test_nested_rng_provenance_and_literal_metrics(self):
        records = _ticket4_records()
        plan = runner.primary_bootstrap_plan(records, n_bootstrap=4, n_random=6)
        result = runner.evaluate_primary_bootstrap_plan(records, plan, n_random=6)
        repeat = runner.run_primary_bootstrap(records, n_bootstrap=4, n_random=6)
        assert result == repeat
        assert result.nested_rng_provenance == (
            "SeedSequence([20260923,b])->uint32->RandomState->permutation"
        )
        expected_seed = int(
            np.random.SeedSequence([20260923, 0]).generate_state(1, dtype=np.uint32)[0]
        )
        assert plan[0]["nested_seed"] == expected_seed
        for replicate in result.replicates:
            assert replicate.rel_benefit_80 == pytest.approx(
                (replicate.rmse_random80 - replicate.rmse_qrf80)
                / replicate.rmse_random80
            )
        values = np.array([replicate.rel_benefit_80 for replicate in result.replicates])
        assert (result.ci_lower, result.ci_upper) == pytest.approx(
            np.percentile(values, [2.5, 97.5], method="linear")
        )

    def test_duplicate_occurrences_contribute_to_rmse(self):
        records = _ticket4_records()
        plan = runner.primary_bootstrap_plan(records, n_bootstrap=10, n_random=2)
        result = runner.evaluate_primary_bootstrap_plan(records, plan, n_random=2)
        replicate_index = next(
            index for index, item in enumerate(plan)
            if len({occ["activity_id"] for occ in item["occurrences"]})
            < len(item["occurrences"])
        )
        replicate_plan = plan[replicate_index]
        by_id = {row["activity_id"]: row for row in records}
        errors = []
        for index in replicate_plan["qrf_selected"]:
            activity_id = replicate_plan["occurrences"][index]["activity_id"]
            row = by_id[activity_id]
            errors.append((row["observed_y"] - row["rf_prediction"]) ** 2)
        assert result.replicates[replicate_index].rmse_qrf80 == pytest.approx(
            np.sqrt(np.mean(errors))
        )

    def test_production_constants_and_classifier_wiring(self):
        assert C.N_BOOTSTRAP == 10_000
        assert C.N_RANDOM_DEFERRALS == 10_000
        assert C.MASTER_SEED == 20260923
        bootstrap = runner.run_primary_bootstrap(
            _ticket4_records(), n_bootstrap=4, n_random=3
        )
        inference = runner.primary_inference(0.11, bootstrap)
        assert inference.classification == classify_rel_benefit_80(
            0.11, bootstrap.ci_lower, bootstrap.ci_upper
        )
        source = inspect.getsource(runner.run_primary_bootstrap)
        assert ".fit(" not in source
        assert "qrf_prediction_quantiles" not in source


class _SyntheticCQRModel:
    def __init__(self, heldout_fold, calls):
        self.heldout_fold = heldout_fold
        self.calls = calls

    def predict_intervals(self, query_rows, quantile_pairs):
        assert all("observed_y" not in row and "observed_clint" not in row for row in query_rows)
        self.calls.append(tuple(row["activity_id"] for row in query_rows))
        output = {}
        for nominal, _, _ in quantile_pairs:
            lower = []
            upper = []
            for row in query_rows:
                half_width = 0.05 if row["outer_fold"] == self.heldout_fold else 0.20
                lower.append(-half_width)
                upper.append(half_width)
            output[nominal] = (np.asarray(lower), np.asarray(upper))
        return output


class _SyntheticCQRFactory:
    def __init__(self):
        self.fit_ids = []
        self.predict_calls = []

    def __call__(self, proper_rows):
        folds = {row["outer_fold"] for row in proper_rows}
        assert len(folds) == 1
        heldout_fold = ({1, 2} - folds).pop()
        self.fit_ids.append(tuple(row["activity_id"] for row in proper_rows))
        return _SyntheticCQRModel(heldout_fold, self.predict_calls)


def _cqr_records():
    return [
        {
            "activity_id": fold * 1000 + index,
            "outer_fold": fold,
            "scaffold_key": f"F{fold}_S{index:02d}",
            "rf_prediction": 0.0,
            "qrf_width": 0.1 + index / 1000,
            "observed_y": 0.0,
        }
        for fold in (1, 2)
        for index in range(25)
    ]


class TestTicket4CQR:
    def test_split_fit_leakage_levels_and_reporting(self):
        records = _cqr_records()
        factory = _SyntheticCQRFactory()
        result = runner.evaluate_cqr(records, factory)
        assert C.CQR_SPLIT_SALT_SUFFIX == "_V3A_CQR_20260923"
        assert tuple(item.nominal_coverage for item in result.coverages) == (0.80, 0.90, 0.95)
        assert result.base_intervals == (
            (0.80, 0.10, 0.90), (0.90, 0.05, 0.95), (0.95, 0.025, 0.975)
        )
        assert result.role == "SECONDARY_CALIBRATION_ONLY"
        assert result.marginal_label == "EMPIRICAL_MARGINAL_COVERAGE"
        assert result.canonical_triage_ranking == "ORIGINAL_FROZEN_QRF_WIDTH"
        assert len(factory.fit_ids) == 2
        for fold, fit_ids in zip((1, 2), factory.fit_ids):
            assert all(activity_id // 1000 != fold for activity_id in fit_ids)
        for metadata in result.fold_metadata:
            assert metadata.n_proper + metadata.n_cal == 25
            assert metadata.n_cal == 5
            assert metadata.split_salt.startswith("_")

    def test_negative_qhat_empty_sets_and_infinite_sets(self):
        result = runner.evaluate_cqr(_cqr_records(), _SyntheticCQRFactory())
        finite = [item for item in result.fold_metadata if item.nominal_coverage == 0.80]
        assert all(item.qhat == pytest.approx(-0.2) for item in finite)
        eighty = result.at(0.80)
        assert eighty.empty_set_count == eighty.n_evaluated
        assert eighty.empirical_marginal_coverage == 0.0
        assert eighty.mean_final_set_width == 0.0
        assert all(row.raw_lower_endpoint > row.raw_upper_endpoint for row in eighty.rows)
        assert all(row.raw_corrected_span < 0.0 and not row.covered for row in eighty.rows)
        for nominal in (0.90, 0.95):
            coverage = result.at(nominal)
            assert coverage.infinite_set_count == coverage.n_evaluated
            assert coverage.empirical_marginal_coverage == 1.0
            assert np.isposinf(coverage.mean_final_set_width)

    def test_qhat_is_fold_coverage_constant_and_primary_rank_unchanged(self):
        records = _cqr_records()
        original_order = {
            fold: [row["activity_id"] for row in sorted(
                (row for row in records if row["outer_fold"] == fold),
                key=lambda row: row["qrf_width"],
            )]
            for fold in (1, 2)
        }
        result = runner.evaluate_cqr(records, _SyntheticCQRFactory())
        assert result.canonical_triage_ranking == "ORIGINAL_FROZEN_QRF_WIDTH"
        assert original_order == {
            fold: [row["activity_id"] for row in sorted(
                (row for row in records if row["outer_fold"] == fold),
                key=lambda row: row["qrf_width"],
            )]
            for fold in (1, 2)
        }
        assert len({(m.outer_fold, m.nominal_coverage, m.qhat) for m in result.fold_metadata}) == 6


def _oracle_scaffold_folds(records):
    """Independent test oracle implementing the frozen SAP greedy allocator."""
    counts = {}
    for row in records:
        scaffold = row["scaffold_key"]
        counts[scaffold] = counts.get(scaffold, 0) + 1
    ordered = sorted(
        counts,
        key=lambda scaffold: (
            -counts[scaffold],
            hashlib.sha256((scaffold + "_V3A_20260923").encode("utf-8")).hexdigest(),
        ),
    )
    sizes = {fold: 0 for fold in range(1, 6)}
    assignment = {}
    for scaffold in ordered:
        fold = min(sizes, key=lambda candidate: (sizes[candidate], candidate))
        assignment[scaffold] = fold
        sizes[fold] += counts[scaffold]
    return assignment


def _sensitivity_a_synthetic_inputs():
    records = []
    for scaffold_index, scaffold in enumerate(("A", "B", "C", "D", "E")):
        for within in (0, 1):
            activity_id = 100 + scaffold_index * 10 + within
            clint = 5.0 + scaffold_index * 8 + within
            records.append(
                {
                    "activity_id": activity_id,
                    "scaffold_key": scaffold,
                    "observed_clint": clint,
                    "observed_y": float(np.log10(clint)),
                    "standard_relation": None,
                    # Deliberately impossible primary-N744 artifacts.  A correct
                    # Sensitivity A implementation must ignore all four fields.
                    "outer_fold": 99,
                    "rf_prediction": 900.0 + activity_id,
                    "qrf_width": 700.0 + activity_id,
                    "primary_retained": True,
                }
            )
    for offset in range(4):
        records.append(
            {
                "activity_id": 900 + offset,
                "scaffold_key": "BOUNDARY",
                "observed_clint": 3.0,
                "observed_y": float(np.log10(3.0)),
                "standard_relation": None,
                "outer_fold": 99,
                "rf_prediction": -999.0,
                "qrf_width": 999.0,
                "primary_retained": False,
            }
        )
    primary_assignment = _oracle_scaffold_folds(records)
    for row in records:
        row["outer_fold"] = primary_assignment[row["scaffold_key"]]

    features = np.zeros((len(records), C.MORGAN_SPEC["nBits"]), dtype=np.uint8)
    descriptors = np.empty((len(records), len(C.DESCRIPTOR_PANEL)), dtype=np.float64)
    for position, row in enumerate(records):
        features[position, (position * 17 + 3) % features.shape[1]] = 1
        features[position, (position * 29 + 11) % features.shape[1]] = 1
        descriptors[position] = np.arange(len(C.DESCRIPTOR_PANEL), dtype=float) + position / 10
    provenance = {
        "protocol_version": C.PROTOCOL_VERSION,
        "protocol_path": SAP_RELATIVE.as_posix(),
        **{field: "0" * 64 for field in runner._HASH_PROVENANCE_FIELDS},
    }
    return records, features, descriptors, provenance


@pytest.fixture(scope="module")
def sensitivity_a_end_to_end():
    records, features, descriptors, provenance = _sensitivity_a_synthetic_inputs()
    records_before = json.dumps(records, sort_keys=True)
    features_before = features.tobytes()
    descriptors_before = descriptors.tobytes()
    primary_freeze_like = {
        "sha256": hashlib.sha256(records_before.encode("utf-8")).hexdigest(),
        "plan": tuple((row["activity_id"], row["outer_fold"], row["qrf_width"]) for row in records),
    }
    result = runner.evaluate_sensitivity_a(
        records,
        features,
        descriptors,
        provenance=provenance,
        n_bootstrap=3,
        n_random=4,
    )
    permutation = list(reversed(range(len(records))))
    shuffled = runner.evaluate_sensitivity_a(
        [records[index] for index in permutation],
        features[permutation],
        descriptors[permutation],
        provenance=provenance,
        n_bootstrap=3,
        n_random=4,
    )
    return {
        "records": records,
        "features": features,
        "descriptors": descriptors,
        "provenance": provenance,
        "result": result,
        "shuffled": shuffled,
        "records_before": records_before,
        "features_before": features_before,
        "descriptors_before": descriptors_before,
        "primary_freeze_like": primary_freeze_like,
    }


class TestTicket4Sensitivities:
    def test_sensitivity_a_strict_boundaries_and_censoring(self):
        template = _ticket4_records()[0]
        rows = [
            dict(template, activity_id=1, observed_clint=2.9, standard_relation=None),
            dict(template, activity_id=2, observed_clint=3.0, standard_relation=None),
            dict(template, activity_id=3, observed_clint=3.0001, standard_relation=None),
            dict(template, activity_id=4, observed_clint=25.0, standard_relation=None),
            dict(template, activity_id=5, observed_clint=149.999, standard_relation=None),
            dict(template, activity_id=6, observed_clint=150.0, standard_relation=None),
            dict(template, activity_id=7, observed_clint=151.0, standard_relation=None),
            dict(template, activity_id=8, observed_clint=25.0, standard_relation="<"),
            dict(template, activity_id=9, observed_clint=25.0, standard_relation=">"),
        ]
        selected = runner.strict_interior_sensitivity_rows(rows)
        assert [row["activity_id"] for row in selected] == [3, 4, 5]

    def test_sensitivity_a_recomputes_own_folds_from_independent_oracle(
        self, sensitivity_a_end_to_end
    ):
        bundle = sensitivity_a_end_to_end
        strict = [row for row in bundle["records"] if 3.0 < row["observed_clint"] < 150.0]
        expected_scaffold_folds = _oracle_scaffold_folds(strict)
        result = bundle["result"]
        actual_by_id = dict(result.provenance["fold_assignment"])
        expected_by_id = {
            row["activity_id"]: expected_scaffold_folds[row["scaffold_key"]]
            for row in strict
        }
        primary_by_id = {row["activity_id"]: row["outer_fold"] for row in strict}
        assert actual_by_id == expected_by_id
        assert actual_by_id != primary_by_id
        for fit in result.provenance["fold_fits"]:
            assert set(fit["train_ids"]).isdisjoint(fit["test_ids"])
            train_scaffolds = {
                row["scaffold_key"] for row in strict if row["activity_id"] in fit["train_ids"]
            }
            test_scaffolds = {
                row["scaffold_key"] for row in strict if row["activity_id"] in fit["test_ids"]
            }
            assert train_scaffolds.isdisjoint(test_scaffolds)

    def test_sensitivity_a_new_fit_and_uncertainty_match_independent_fold_oracle(
        self, sensitivity_a_end_to_end
    ):
        bundle = sensitivity_a_end_to_end
        result = bundle["result"]
        records = bundle["records"]
        features = bundle["features"]
        strict = [row for row in records if 3.0 < row["observed_clint"] < 150.0]
        expected_assignment = _oracle_scaffold_folds(strict)
        canonical_ids = sorted(
            (row["activity_id"] for row in strict),
            key=lambda activity_id: (
                hashlib.sha256((str(activity_id) + C.RETENTION_TIE_SUFFIX).encode()).hexdigest(),
                json.dumps(activity_id, sort_keys=True),
            ),
        )
        row_by_id = {row["activity_id"]: row for row in records}
        feature_by_id = {
            row["activity_id"]: features[position]
            for position, row in enumerate(records)
        }
        heldout_fold = 1
        train_ids = [
            activity_id for activity_id in canonical_ids
            if expected_assignment[row_by_id[activity_id]["scaffold_key"]] != heldout_fold
        ]
        test_ids = [
            activity_id for activity_id in canonical_ids
            if expected_assignment[row_by_id[activity_id]["scaffold_key"]] == heldout_fold
        ]
        X_train = np.asarray([feature_by_id[item] for item in train_ids])
        X_test = np.asarray([feature_by_id[item] for item in test_ids])
        y_train = np.asarray([row_by_id[item]["observed_y"] for item in train_ids])
        independent_rf = C.make_frozen_rf()
        independent_rf.fit(X_train, y_train)
        expected_predictions = independent_rf.predict(X_test)
        weights = runner.recover_forest_weights_many(
            independent_rf, X_train, X_test, sample_weight_used=False
        )
        expected_widths = np.asarray([
            runner.weighted_quantile(y_train, row_weights, 0.90)
            - runner.weighted_quantile(y_train, row_weights, 0.10)
            for row_weights in weights
        ])
        actual = {row["activity_id"]: row for row in result.oof_records}
        assert np.asarray([actual[item]["rf_prediction"] for item in test_ids]) == pytest.approx(
            expected_predictions
        )
        assert np.asarray([actual[item]["qrf_width"] for item in test_ids]) == pytest.approx(
            expected_widths
        )
        assert all(actual[item]["rf_prediction"] != row_by_id[item]["rf_prediction"] for item in test_ids)
        assert all(actual[item]["qrf_width"] != row_by_id[item]["qrf_width"] for item in test_ids)

    def test_sensitivity_a_architecture_representation_order_and_primary_isolation(
        self, sensitivity_a_end_to_end
    ):
        bundle = sensitivity_a_end_to_end
        result = bundle["result"]
        assert result.name == "SENSITIVITY_A_STRICT_INTERIOR"
        assert result.cohort_n == 10
        assert "SEPARATE_FIVE_FOLD_ANALYSIS" in result.interpretation_labels
        assert result.provenance["model_specification"] == dict(C.FROZEN_RF_PARAMS)
        assert result.provenance["representation"] == "ECFP4_2048_R2_BINARY_NOCHIRAL"
        assert json.dumps(bundle["records"], sort_keys=True) == bundle["records_before"]
        assert bundle["features"].tobytes() == bundle["features_before"]
        assert bundle["descriptors"].tobytes() == bundle["descriptors_before"]
        assert bundle["primary_freeze_like"]["sha256"] == hashlib.sha256(
            bundle["records_before"].encode("utf-8")
        ).hexdigest()
        first = sorted(
            (row["activity_id"], row["outer_fold"], row["rf_prediction"], row["qrf_width"])
            for row in result.oof_records
        )
        shuffled = sorted(
            (row["activity_id"], row["outer_fold"], row["rf_prediction"], row["qrf_width"])
            for row in bundle["shuffled"].oof_records
        )
        assert first == shuffled

    def test_sensitivity_a_ranking_and_bootstrap_use_own_oof(self, sensitivity_a_end_to_end):
        result = sensitivity_a_end_to_end["result"]
        assert result.provenance["ranking_source"] == "SENSITIVITY_A_RECOMPUTED_QRF_WIDTH_FOLD_LOCAL"
        assert result.provenance["bootstrap_source"] == "SENSITIVITY_A_OWN_OOF_RECORDS_AND_FOLDS"
        independently_replayed = runner.run_primary_bootstrap(
            result.oof_records, n_bootstrap=3, n_random=4
        )
        assert independently_replayed == result.bootstrap
        fold_sizes = {}
        for row in result.oof_records:
            fold_sizes[row["outer_fold"]] = fold_sizes.get(row["outer_fold"], 0) + 1
        assert dict(result.qrf80.retained_counts_by_fold) == {
            fold: math.ceil(0.8 * count) for fold, count in fold_sizes.items()
        }

    def test_sensitivity_b_boundary_labels_reranking_and_no_classifier(self):
        records = _ticket4_records()
        records[0]["observed_clint"] = 24.999
        records[1]["observed_clint"] = 25.0
        before = json.dumps(records, sort_keys=True)
        result = runner.evaluate_sensitivity_b(records, n_bootstrap=3, n_random=4)
        assert result.cohort_n == 7
        assert set(result.interpretation_labels) == {
            "EXPLORATORY", "OUTCOME_DEFINED", "DIAGNOSTIC", "NONDEPLOYABLE"
        }
        assert 111 in result.qrf80.retained_ids
        assert 110 not in result.qrf80.retained_ids
        assert not hasattr(result, "classification")
        assert result.matched_random80.draw_count == 4
        assert result.bootstrap.nested_rng_provenance.endswith("b starts at 1")
        assert json.dumps(records, sort_keys=True) == before


# =========================================================================== Ticket 5
def _ticket5_primary_records(ticket3_bundle):
    outcomes = {row["activity_id"]: row["observed_y"] for row in ticket3_bundle["outcomes"]}
    return [
        {
            **record,
            "scaffold_key": f"F{record['outer_fold']}_S{record['activity_id']}",
            "observed_y": outcomes[record["activity_id"]],
            "observed_clint": float(25 + record["activity_id"] % 17),
            "standard_relation": None,
        }
        for record in ticket3_bundle["payload"]["records"]
    ]


@pytest.fixture(scope="module")
def ticket5_components(ticket3_bundle, sensitivity_a_end_to_end):
    primary_records = _ticket5_primary_records(ticket3_bundle)
    bootstrap = runner.run_primary_bootstrap(
        primary_records, n_bootstrap=3, n_random=4
    )
    return {
        "bootstrap": bootstrap,
        "cqr": runner.evaluate_cqr(_cqr_records(), _SyntheticCQRFactory()),
        "sensitivity_a": sensitivity_a_end_to_end["result"],
        "sensitivity_b": runner.evaluate_sensitivity_b(
            _ticket4_records(), n_bootstrap=3, n_random=4
        ),
    }


def _authorized_prediction_freeze(artifacts, ticket3_bundle):
    payload = ticket3_bundle["freeze"].read_payload()
    records = payload["records"]
    expected = {record["activity_id"]: record["outer_fold"] for record in records}
    freeze = build_prediction_freeze(
        records,
        expected_activity_ids=tuple(expected),
        expected_outer_folds=tuple(expected.values()),
        provenance=runner._prediction_provenance(artifacts),
    )
    return freeze, expected


@pytest.fixture
def ticket5_running_bundle(ready_project, tmp_path, ticket3_bundle, ticket5_components):
    artifacts = load_frozen_artifacts(ready_project)
    ledger = initialize_run_ledger(
        ready_project / SCIENTIFIC_RUNS_RELATIVE,
        "ticket5-synthetic-run",
        artifacts=artifacts,
        git_commit=FIXED_COMMIT,
        start_timestamp=FIXED_TIME,
        authorization_requested=True,
        environment_summary={"z": 2, "a": 1},
    )
    authorize_run(ready_project, execute_scientific_analysis=True, ledger=ledger)
    start_run(ledger)
    freeze, expected = _authorized_prediction_freeze(artifacts, ticket3_bundle)
    sealed_freeze = seal_prediction_freeze(
        freeze,
        ledger.run_directory / PREDICTION_FREEZE_FILENAME,
        expected_id_to_fold=expected,
    )
    plan = prepare_postfreeze_plan(sealed_freeze, expected_id_to_fold=expected)
    point = evaluate_postfreeze(plan, ticket3_bundle["outcomes"])
    primary = runner.primary_inference(point.rel_benefit_80, ticket5_components["bootstrap"])
    package = build_final_result_package(
        ledger=ledger,
        artifacts=artifacts,
        sealed_freeze=sealed_freeze,
        postfreeze_plan=plan,
        point_result=point,
        primary=primary,
        cqr=ticket5_components["cqr"],
        sensitivity_a=ticket5_components["sensitivity_a"],
        sensitivity_b=ticket5_components["sensitivity_b"],
    )
    return {
        "artifacts": artifacts,
        "ledger": ledger,
        "freeze": freeze,
        "sealed_freeze": sealed_freeze,
        "expected": expected,
        "plan": plan,
        "point": point,
        "primary": primary,
        "package": package,
        **ticket5_components,
    }


def _seal_ticket5_bundle(bundle):
    return seal_final_result(
        bundle["package"],
        ledger=bundle["ledger"],
        artifacts=bundle["artifacts"],
        sealed_freeze=bundle["sealed_freeze"],
        completion_timestamp="2026-09-27T12:00:00Z",
    )


class TestGate11Ticket5Serialization91To96:
    def test_gate11_91_prediction_freeze_schema_and_hash_deterministic(
        self, ticket5_running_bundle
    ):
        bundle = ticket5_running_bundle
        payload = bundle["freeze"].read_payload()
        rebuilt = build_prediction_freeze(
            list(reversed(payload["records"])),
            expected_activity_ids=tuple(reversed(tuple(bundle["expected"]))),
            expected_outer_folds=tuple(
                bundle["expected"][item] for item in reversed(tuple(bundle["expected"]))
            ),
            provenance=dict(reversed(list(payload["provenance"].items()))),
        )
        assert rebuilt.canonical_bytes == bundle["freeze"].canonical_bytes
        assert rebuilt.sha256 == hashlib.sha256(rebuilt.canonical_bytes).hexdigest()

    def test_gate11_92_outcome_results_separate_from_prediction_freeze(
        self, ticket5_running_bundle
    ):
        sealed = _seal_ticket5_bundle(ticket5_running_bundle)
        freeze_payload = json.loads(sealed.prediction_freeze_path.read_text(encoding="utf-8"))
        result_payload = json.loads(sealed.result_path.read_text(encoding="utf-8"))
        assert sealed.prediction_freeze_path != sealed.result_path
        assert sealed.prediction_freeze_sha256 != sealed.result_sha256
        assert all("observed_y" not in record for record in freeze_payload["records"])
        assert set(result_payload["scientific_content"]["outputs"]) == {
            "primary", "sensitivity_a", "sensitivity_b", "cqr"
        }

    def test_gate11_93_scientific_results_cannot_overwrite_preflight(
        self, ticket5_running_bundle, ready_project
    ):
        protected = {
            relative: (ready_project / relative).read_bytes()
            for relative in FROZEN_RELATIVES
        }
        sealed = _seal_ticket5_bundle(ticket5_running_bundle)
        assert sealed.result_path.parent == ticket5_running_bundle["ledger"].run_directory
        assert all((ready_project / relative).read_bytes() == data for relative, data in protected.items())

    def test_gate11_94_result_records_all_frozen_hashes(self, ticket5_running_bundle):
        payload = ticket5_running_bundle["package"].read_payload()
        context = payload["scientific_content"]["context"]
        assert context["git_commit"] == FIXED_COMMIT
        assert context["preflight_manifest_sha256"] == C.sha256_file(
            ticket5_running_bundle["artifacts"].manifest_path
        )
        assert context["prediction_freeze_sha256"] == ticket5_running_bundle["sealed_freeze"].sha256
        assert context["cohort_sha256"] == ticket5_running_bundle["artifacts"].manifest["cohort_sha256"]
        assert context["split_sha256"] == ticket5_running_bundle["artifacts"].manifest["split_sha256"]
        assert context["feature_sha256"] == ticket5_running_bundle["artifacts"].manifest["feature_sha256"]
        assert len(context["authority_documents"]) == len(runner.AUTHORITY_RELATIVES)
        for document in context["authority_documents"]:
            assert document["sha256"] == C.sha256_file(
                ticket5_running_bundle["artifacts"].project_root / document["path"]
            )

    def test_gate11_95_partial_run_not_marked_complete(
        self, ticket5_running_bundle, monkeypatch
    ):
        def fail_after_prefix(descriptor, data):
            assert runner.os.write(descriptor, data[:23]) == 23
            raise OSError("injected result interruption")

        monkeypatch.setattr(runner, "_write_final_temp", fail_after_prefix)
        with pytest.raises(FinalResultError, match="could not be staged"):
            _seal_ticket5_bundle(ticket5_running_bundle)
        ledger = ticket5_running_bundle["ledger"]
        assert ledger.read()["status"] == InternalRunStatus.EXECUTION_RUNNING.value
        assert not (ledger.run_directory / FINAL_RESULT_FILENAME).exists()
        assert not (ledger.run_directory / FINAL_MANIFEST_FILENAME).exists()
        assert not any(path.suffix == ".tmp" for path in ledger.run_directory.iterdir())

    def test_gate11_96_failed_fold_blocks_final_sealing(
        self, ready_project
    ):
        artifacts = load_frozen_artifacts(ready_project)
        inputs = replace(_synthetic_inputs(), provenance=runner._prediction_provenance(artifacts))
        ledger = initialize_run_ledger(
            ready_project / SCIENTIFIC_RUNS_RELATIVE,
            "failed-fold-run",
            artifacts=artifacts,
            git_commit=FIXED_COMMIT,
            start_timestamp=FIXED_TIME,
            authorization_requested=True,
        )
        accessed = {"outcomes": 0}

        def failing_training(fold, train_ids):
            if fold == 3:
                raise RuntimeError("synthetic fold 3 failure")
            return {item: float(item % 13) / 10 for item in train_ids}

        def forbidden_outcomes():
            accessed["outcomes"] += 1
            raise AssertionError("outcomes must not be accessed after a failed fold")

        with pytest.raises(RuntimeError, match="fold 3"):
            runner.orchestrate_full_scientific_run(
                project_root=ready_project,
                ledger=ledger,
                inputs=inputs,
                training_outcome_provider=failing_training,
                outcome_provider=forbidden_outcomes,
                completion_timestamp="2026-09-27T12:00:00Z",
                execute_scientific_analysis=True,
                n_bootstrap=2,
                n_random=3,
            )
        assert accessed["outcomes"] == 0
        assert ledger.read()["status"] == InternalRunStatus.EXECUTION_ABORTED.value
        assert not (ledger.run_directory / FINAL_RESULT_FILENAME).exists()
        assert not (ledger.run_directory / FINAL_MANIFEST_FILENAME).exists()

    def test_mismatched_frozen_input_provenance_blocks_all_model_and_outcome_access(
        self, ready_project
    ):
        artifacts = load_frozen_artifacts(ready_project)
        provenance = runner._prediction_provenance(artifacts)
        bad_inputs = replace(
            _synthetic_inputs(),
            provenance={**provenance, "feature_sha256": "f" * 64},
        )
        ledger = initialize_run_ledger(
            ready_project / SCIENTIFIC_RUNS_RELATIVE,
            "wrong-input-provenance",
            artifacts=artifacts,
            git_commit=FIXED_COMMIT,
            start_timestamp=FIXED_TIME,
            authorization_requested=True,
        )
        calls = {"training": 0, "outcomes": 0}

        def training_provider(_fold, _ids):
            calls["training"] += 1
            raise AssertionError("model fitting must not begin")

        def outcome_provider():
            calls["outcomes"] += 1
            raise AssertionError("outcomes must not be accessed")

        with pytest.raises(RunAuthorizationError, match="outcome-blind inputs"):
            runner.orchestrate_full_scientific_run(
                project_root=ready_project,
                ledger=ledger,
                inputs=bad_inputs,
                training_outcome_provider=training_provider,
                outcome_provider=outcome_provider,
                completion_timestamp="2026-09-27T12:00:00Z",
                execute_scientific_analysis=True,
                n_bootstrap=2,
                n_random=3,
            )
        assert calls == {"training": 0, "outcomes": 0}
        assert ledger.read()["status"] == InternalRunStatus.EXECUTION_ABORTED.value


class TestGate11Ticket5Lifecycle97To100:
    def test_gate11_97_completed_run_gets_immutable_run_id(self, ticket5_running_bundle):
        sealed = _seal_ticket5_bundle(ticket5_running_bundle)
        manifest = json.loads(sealed.manifest_path.read_text(encoding="utf-8"))
        assert sealed.run_id == manifest["run_id"] == sealed.run_directory.name
        assert sealed.verify()

    def test_gate11_98_completed_run_cannot_be_overwritten(self, ticket5_running_bundle):
        sealed = _seal_ticket5_bundle(ticket5_running_bundle)
        before = {
            path: path.read_bytes()
            for path in (sealed.result_path, sealed.manifest_path, sealed.prediction_freeze_path)
        }
        ledger_before = sealed.ledger_path.read_bytes()
        with pytest.raises((LifecycleTransitionError, FinalResultCollisionError)):
            _seal_ticket5_bundle(ticket5_running_bundle)
        with pytest.raises(LifecycleTransitionError, match="before execution starts"):
            authorize_run(
                ticket5_running_bundle["artifacts"].project_root,
                execute_scientific_analysis=True,
                ledger=ticket5_running_bundle["ledger"],
            )
        assert all(path.read_bytes() == data for path, data in before.items())
        assert sealed.ledger_path.read_bytes() == ledger_before

    def test_gate11_99_rerun_requires_new_provenance_record(
        self, ticket5_running_bundle
    ):
        sealed = _seal_ticket5_bundle(ticket5_running_bundle)
        artifacts = ticket5_running_bundle["artifacts"]
        with pytest.raises(RunCollisionError):
            initialize_run_ledger(
                artifacts.project_root / SCIENTIFIC_RUNS_RELATIVE,
                sealed.run_id,
                artifacts=artifacts,
                git_commit=FIXED_COMMIT,
                start_timestamp=FIXED_TIME,
                authorization_requested=True,
            )
        rerun = initialize_run_ledger(
            artifacts.project_root / SCIENTIFIC_RUNS_RELATIVE,
            "ticket5-synthetic-rerun",
            artifacts=artifacts,
            git_commit=FIXED_COMMIT,
            start_timestamp="2026-09-27T13:00:00Z",
            authorization_requested=True,
        )
        assert rerun.run_id != sealed.run_id
        assert rerun.ledger_path != sealed.ledger_path
        assert sealed.verify()

    def test_gate11_100_execution_ledger_is_complete(self, ticket5_running_bundle):
        sealed = _seal_ticket5_bundle(ticket5_running_bundle)
        payload = ticket5_running_bundle["ledger"].read()
        assert payload["status"] == InternalRunStatus.EXECUTION_COMPLETED.value
        assert payload["completion_timestamp"] == "2026-09-27T12:00:00Z"
        assert payload["git_commit"] == FIXED_COMMIT
        assert payload["manifest_sha256"]
        assert payload["final_manifest_sha256"] == sealed.manifest_sha256
        assert payload["environment_summary"] == {"a": 1, "z": 2}
        assert set(payload["artifact_hashes"]) == {"prediction_freeze", "scientific_result"}
        assert [event["event"] for event in payload["lifecycle_events"]] == [
            "RUN_INITIALIZED", "AUTHORIZATION_PASSED", "EXECUTION_STARTED", "EXECUTION_COMPLETED"
        ]


class TestTicket5DeterminismAndAdversarialFinalization:
    def test_canonical_special_float_bytes_and_sha_match_independent_known_oracle(self):
        value = {"z": -0.0, "nested": {"b": 2}, "a": float("inf")}
        expected = b'{"a":{"$v3a_float":"+infinity"},"nested":{"b":2},"z":0.0}\n'
        assert runner._canonical_value_bytes(value) == expected
        assert runner._value_sha256(value) == (
            "4a205c6f7f6da947a795e8ddfa5091d876949402efc6dbfbae728ce9e7e181a2"
        )

    def test_final_result_is_deterministic_strict_json_with_explicit_infinities(
        self, ticket5_running_bundle
    ):
        first = ticket5_running_bundle["package"]
        second = build_final_result_package(
            ledger=ticket5_running_bundle["ledger"],
            artifacts=ticket5_running_bundle["artifacts"],
            sealed_freeze=ticket5_running_bundle["sealed_freeze"],
            postfreeze_plan=ticket5_running_bundle["plan"],
            point_result=ticket5_running_bundle["point"],
            primary=ticket5_running_bundle["primary"],
            cqr=ticket5_running_bundle["cqr"],
            sensitivity_a=ticket5_running_bundle["sensitivity_a"],
            sensitivity_b=ticket5_running_bundle["sensitivity_b"],
        )
        assert first.canonical_bytes == second.canonical_bytes
        assert first.sha256 == hashlib.sha256(first.canonical_bytes).hexdigest()
        assert b"NaN" not in first.canonical_bytes
        assert b"Infinity" not in first.canonical_bytes
        assert b'"$v3a_float":"+infinity"' in first.canonical_bytes

    def test_changed_random_plan_is_rejected(self, ticket5_running_bundle):
        plan = ticket5_running_bundle["plan"]
        draws = list(plan.random_retained_ids_by_draw)
        draws[0] = tuple(reversed(draws[0]))
        forged = replace(plan, random_retained_ids_by_draw=tuple(draws))
        with pytest.raises(OutcomeEvaluationError, match="canonical seeded draw stream"):
            build_final_result_package(
                ledger=ticket5_running_bundle["ledger"],
                artifacts=ticket5_running_bundle["artifacts"],
                sealed_freeze=ticket5_running_bundle["sealed_freeze"],
                postfreeze_plan=forged,
                point_result=ticket5_running_bundle["point"],
                primary=ticket5_running_bundle["primary"],
                cqr=ticket5_running_bundle["cqr"],
                sensitivity_a=ticket5_running_bundle["sensitivity_a"],
                sensitivity_b=ticket5_running_bundle["sensitivity_b"],
            )

    def test_incomplete_result_wrong_run_id_and_bad_classification_rejected(
        self, ticket5_running_bundle
    ):
        payload = ticket5_running_bundle["package"].read_payload()
        incomplete = json.loads(json.dumps(payload))
        incomplete["scientific_content"]["outputs"].pop("cqr")
        incomplete["scientific_content_sha256"] = runner._value_sha256(
            incomplete["scientific_content"]
        )
        with pytest.raises(FinalResultError, match="namespaces"):
            validate_final_result_payload(incomplete)
        with pytest.raises(FinalResultError, match="run_id"):
            validate_final_result_payload(payload, expected_run_id="another-run")
        expected = classify_rel_benefit_80(
            payload["scientific_content"]["outputs"]["primary"]["point_estimate"],
            payload["scientific_content"]["outputs"]["primary"]["bootstrap"]["ci_lower"],
            payload["scientific_content"]["outputs"]["primary"]["bootstrap"]["ci_upper"],
        )
        inconsistent = json.loads(json.dumps(payload))
        inconsistent["scientific_content"]["outputs"]["primary"]["classification"] = (
            "INCONCLUSIVE"
            if expected != "INCONCLUSIVE"
            else "SUPPORTED_OPERATIONAL_SIGNAL"
        )
        inconsistent["scientific_content_sha256"] = runner._value_sha256(
            inconsistent["scientific_content"]
        )
        with pytest.raises(FinalResultError, match="classification"):
            validate_final_result_payload(inconsistent)
        forged_primary = replace(
            ticket5_running_bundle["primary"],
            ci_lower=ticket5_running_bundle["primary"].ci_lower - 0.5,
        )
        with pytest.raises(FinalResultError, match="confidence interval"):
            build_final_result_package(
                ledger=ticket5_running_bundle["ledger"],
                artifacts=ticket5_running_bundle["artifacts"],
                sealed_freeze=ticket5_running_bundle["sealed_freeze"],
                postfreeze_plan=ticket5_running_bundle["plan"],
                point_result=ticket5_running_bundle["point"],
                primary=forged_primary,
                cqr=ticket5_running_bundle["cqr"],
                sensitivity_a=ticket5_running_bundle["sensitivity_a"],
                sensitivity_b=ticket5_running_bundle["sensitivity_b"],
            )

    @pytest.mark.parametrize(
        "mutator,match",
        [
            (
                lambda payload: payload["scientific_content"]["outputs"]["primary"][
                    "bootstrap"
                ].pop("base_seed"),
                "bootstrap.*schema",
            ),
            (
                lambda payload: payload["scientific_content"]["outputs"]["primary"][
                    "qrf80"
                ].__setitem__(
                    "retained_n",
                    payload["scientific_content"]["outputs"]["primary"]["qrf80"][
                        "retained_n"
                    ] + 1,
                ),
                "cohort size|retained_ids length",
            ),
        ],
    )
    def test_nested_schema_and_consistency_tampering_is_rejected_before_sealing(
        self, ticket5_running_bundle, mutator, match
    ):
        original = ticket5_running_bundle["package"]
        payload = original.read_payload()
        mutator(payload)
        payload["scientific_content_sha256"] = runner._value_sha256(
            payload["scientific_content"]
        )
        malicious_bytes = runner._canonical_value_bytes(payload)
        malicious = replace(
            original,
            canonical_bytes=malicious_bytes,
            sha256=hashlib.sha256(malicious_bytes).hexdigest(),
            scientific_content_sha256=payload["scientific_content_sha256"],
        )
        ledger = ticket5_running_bundle["ledger"]
        with pytest.raises(FinalResultError, match=match):
            seal_final_result(
                malicious,
                ledger=ledger,
                artifacts=ticket5_running_bundle["artifacts"],
                sealed_freeze=ticket5_running_bundle["sealed_freeze"],
                completion_timestamp="2026-09-27T12:00:00Z",
            )
        assert not (ledger.run_directory / FINAL_RESULT_FILENAME).exists()
        assert not (ledger.run_directory / FINAL_MANIFEST_FILENAME).exists()

    def test_changed_prediction_freeze_after_final_sealing_is_rejected(
        self, ticket5_running_bundle
    ):
        sealed = _seal_ticket5_bundle(ticket5_running_bundle)
        sealed.prediction_freeze_path.write_bytes(
            sealed.prediction_freeze_path.read_bytes() + b" "
        )
        with pytest.raises(FinalResultError, match="prediction-freeze mutation"):
            verify_sealed_scientific_run(sealed)

    @pytest.mark.parametrize("filename", [FINAL_RESULT_FILENAME, FINAL_MANIFEST_FILENAME])
    def test_existing_final_destination_collision_is_directly_rejected(
        self, ticket5_running_bundle, filename
    ):
        ledger = ticket5_running_bundle["ledger"]
        destination = ledger.run_directory / filename
        sentinel = b"pre-existing-final-destination"
        destination.write_bytes(sentinel)
        with pytest.raises(FinalResultCollisionError, match="already exists"):
            _seal_ticket5_bundle(ticket5_running_bundle)
        assert destination.read_bytes() == sentinel
        assert ledger.read()["status"] == InternalRunStatus.EXECUTION_RUNNING.value
        counterpart = (
            FINAL_MANIFEST_FILENAME if filename == FINAL_RESULT_FILENAME else FINAL_RESULT_FILENAME
        )
        assert not (ledger.run_directory / counterpart).exists()

    def test_manifest_result_hash_mismatch_is_directly_rejected(
        self, ticket5_running_bundle
    ):
        sealed = _seal_ticket5_bundle(ticket5_running_bundle)
        manifest = json.loads(sealed.manifest_path.read_text(encoding="utf-8"))
        result_entry = next(
            entry for entry in manifest["artifacts"]
            if entry["logical_name"] == "scientific_result"
        )
        result_entry["sha256"] = sealed.prediction_freeze_sha256
        forged_bytes = runner._canonical_value_bytes(manifest)
        sealed.manifest_path.write_bytes(forged_bytes)
        forged_handle = replace(
            sealed,
            manifest_sha256=hashlib.sha256(forged_bytes).hexdigest(),
        )
        with pytest.raises(FinalResultError, match="artifact hash or size mismatch"):
            verify_sealed_scientific_run(forged_handle)

    def test_sibling_and_symlink_run_directory_substitution_rejected_before_writes(
        self, ticket5_running_bundle, monkeypatch
    ):
        bundle = ticket5_running_bundle
        sibling = bundle["artifacts"].project_root / "scientific_runs" / "v3a-sibling"
        sibling.mkdir(parents=True)
        forged_ledger_path = sibling / LEDGER_FILENAME
        shutil.copy2(bundle["ledger"].ledger_path, forged_ledger_path)
        forged_ledger = replace(
            bundle["ledger"], run_directory=sibling, ledger_path=forged_ledger_path
        )
        with pytest.raises(ProtectedRunPathError, match="canonical run-ID path"):
            seal_final_result(
                bundle["package"],
                ledger=forged_ledger,
                artifacts=bundle["artifacts"],
                sealed_freeze=bundle["sealed_freeze"],
                completion_timestamp="2026-09-27T12:00:00Z",
            )
        original_is_symlink = Path.is_symlink

        def report_run_as_symlink(path):
            if path == bundle["ledger"].run_directory:
                return True
            return original_is_symlink(path)

        monkeypatch.setattr(Path, "is_symlink", report_run_as_symlink)
        with pytest.raises(ProtectedRunPathError, match="symlink"):
            _seal_ticket5_bundle(bundle)
        assert not (bundle["ledger"].run_directory / FINAL_RESULT_FILENAME).exists()
        assert not (bundle["ledger"].run_directory / FINAL_MANIFEST_FILENAME).exists()

    def test_executing_checkout_identity_is_revalidated_before_publication(
        self, ticket5_running_bundle, monkeypatch
    ):
        monkeypatch.setattr(runner, "executing_checkout_commit", lambda: "f" * 40)
        with pytest.raises(FinalResultError, match="executing checkout HEAD"):
            _seal_ticket5_bundle(ticket5_running_bundle)
        ledger = ticket5_running_bundle["ledger"]
        assert ledger.read()["status"] == InternalRunStatus.EXECUTION_RUNNING.value
        assert not (ledger.run_directory / FINAL_RESULT_FILENAME).exists()
        assert not (ledger.run_directory / FINAL_MANIFEST_FILENAME).exists()

    def test_manifest_hash_mismatch_path_escape_and_sealed_mutation_rejected(
        self, ticket5_running_bundle
    ):
        sealed = _seal_ticket5_bundle(ticket5_running_bundle)
        original_manifest = sealed.manifest_path.read_bytes()
        manifest = json.loads(original_manifest)
        manifest["artifacts"][0]["relative_path"] = "../escape.json"
        sealed.manifest_path.write_bytes(runner._canonical_value_bytes(manifest))
        with pytest.raises((FinalResultError, ProtectedRunPathError)):
            verify_sealed_scientific_run(replace(
                sealed, manifest_sha256=C.sha256_file(sealed.manifest_path)
            ))
        sealed.manifest_path.write_bytes(original_manifest)
        sealed.result_path.write_bytes(sealed.result_path.read_bytes() + b" ")
        assert sealed.verify() is False

    def test_wrong_protocol_and_code_identity_in_manifest_are_rejected(
        self, ticket5_running_bundle
    ):
        sealed = _seal_ticket5_bundle(ticket5_running_bundle)
        original = json.loads(sealed.manifest_path.read_text(encoding="utf-8"))
        wrong_protocol = json.loads(json.dumps(original))
        wrong_protocol["protocol_version"] = "V3A-UNAUTHORIZED-PROTOCOL"
        with pytest.raises(FinalResultError, match="protocol version"):
            runner._verify_manifest_artifacts(
                wrong_protocol, sealed.run_directory, expected_run_id=sealed.run_id
            )
        wrong_commit = json.loads(json.dumps(original))
        wrong_commit["git_commit"] = "f" * 40
        with pytest.raises(FinalResultError, match="git_commit"):
            runner._verify_manifest_artifacts(
                wrong_commit, sealed.run_directory, expected_run_id=sealed.run_id
            )

    def test_interrupted_result_publication_rolls_back_manifest_and_completion(
        self, ticket5_running_bundle, monkeypatch
    ):
        def fail_publication(_staged, _destination, *, label):
            assert label == "scientific result"
            raise FinalResultError("injected result publication failure")

        monkeypatch.setattr(runner, "_publish_staged_no_clobber", fail_publication)
        with pytest.raises(FinalResultError, match="result publication"):
            _seal_ticket5_bundle(ticket5_running_bundle)
        ledger = ticket5_running_bundle["ledger"]
        assert ledger.read()["status"] == InternalRunStatus.EXECUTION_RUNNING.value
        assert not (ledger.run_directory / FINAL_RESULT_FILENAME).exists()
        assert not (ledger.run_directory / FINAL_MANIFEST_FILENAME).exists()
        assert not any(path.suffix == ".staged" for path in ledger.run_directory.iterdir())

    def test_interrupted_manifest_publication_never_exposes_final_result(
        self, ticket5_running_bundle, monkeypatch
    ):
        def fail_manifest(_data, _destination, *, label):
            assert label == "final manifest"
            raise FinalResultError("injected manifest publication failure")

        monkeypatch.setattr(runner, "_seal_bytes_no_clobber", fail_manifest)
        with pytest.raises(FinalResultError, match="manifest publication"):
            _seal_ticket5_bundle(ticket5_running_bundle)
        ledger = ticket5_running_bundle["ledger"]
        assert ledger.read()["status"] == InternalRunStatus.EXECUTION_RUNNING.value
        assert not (ledger.run_directory / FINAL_RESULT_FILENAME).exists()
        assert not (ledger.run_directory / FINAL_MANIFEST_FILENAME).exists()
        assert not any(path.suffix == ".staged" for path in ledger.run_directory.iterdir())


class _FiveFoldSyntheticCQRModel:
    def predict_intervals(self, query_rows, quantile_pairs):
        assert all("observed_y" not in row and "observed_clint" not in row for row in query_rows)
        centers = np.asarray([row["rf_prediction"] for row in query_rows], dtype=float)
        return {
            nominal: (centers - (1.0 + nominal), centers + (1.0 + nominal))
            for nominal, _low, _high in quantile_pairs
        }


def _five_fold_cqr_factory(proper_rows):
    assert proper_rows
    return _FiveFoldSyntheticCQRModel()


def test_ticket5_full_synthetic_end_to_end_and_q1_to_q6_orchestration(ready_project):
    artifacts = load_frozen_artifacts(ready_project)
    inputs = replace(_synthetic_inputs(), provenance=runner._prediction_provenance(artifacts))
    ledger = initialize_run_ledger(
        ready_project / SCIENTIFIC_RUNS_RELATIVE,
        "full-synthetic-ticket5",
        artifacts=artifacts,
        git_commit=FIXED_COMMIT,
        start_timestamp=FIXED_TIME,
        authorization_requested=True,
        environment_summary={"fixture": "synthetic-only"},
    )
    outcome_values = {
        activity_id: float(np.log10(25.0 + position))
        for position, activity_id in enumerate(inputs.activity_ids)
    }
    outcome_access = {"count": 0}
    events = []

    def training_provider(fold, train_ids):
        assert all(dict(zip(inputs.activity_ids, inputs.outer_folds))[item] != fold for item in train_ids)
        return {item: outcome_values[item] for item in train_ids}

    def outcome_provider():
        outcome_access["count"] += 1
        freeze_path = ledger.run_directory / PREDICTION_FREEZE_FILENAME
        assert freeze_path.is_file()
        assert "prediction_freeze_sealed" in events
        return [
            {
                "activity_id": activity_id,
                "outer_fold": fold,
                "observed_y": outcome_values[activity_id],
                "observed_clint": float(25.0 + position),
                "standard_relation": None,
            }
            for position, (activity_id, fold) in enumerate(
                zip(inputs.activity_ids, inputs.outer_folds)
            )
        ]

    result = runner.orchestrate_full_scientific_run(
        project_root=ready_project,
        ledger=ledger,
        inputs=inputs,
        training_outcome_provider=training_provider,
        outcome_provider=outcome_provider,
        completion_timestamp="2026-09-27T14:00:00Z",
        execute_scientific_analysis=True,
        cqr_model_factory=_five_fold_cqr_factory,
        n_bootstrap=2,
        n_random=3,
        audit_hook=lambda event, _detail: events.append(event),
    )
    assert outcome_access["count"] == 1
    assert events.index("prediction_freeze_sealed") < events.index("outcomes_accessed_after_freeze")
    assert events.index("primary_frozen") < events.index("sensitivities_completed")
    assert result.prediction_freeze.verify()
    assert result.sealed_run.verify()
    assert ledger.read()["status"] == InternalRunStatus.EXECUTION_COMPLETED.value
    final = json.loads(result.sealed_run.result_path.read_text(encoding="utf-8"))
    outputs = final["scientific_content"]["outputs"]
    assert set(outputs) == {"primary", "sensitivity_a", "sensitivity_b", "cqr"}
    assert "classification" in outputs["primary"]
    assert "classification" not in outputs["sensitivity_b"]
    assert outputs["cqr"]["canonical_triage_ranking"] == "ORIGINAL_FROZEN_QRF_WIDTH"
    serialized_bootstrap = outputs["primary"]["bootstrap"]
    assert serialized_bootstrap["base_seed"] == C.MASTER_SEED
    assert serialized_bootstrap["nested_rng_provenance"] == runner.BOOTSTRAP_RNG_PROVENANCE
    assert serialized_bootstrap["bootstrap_replicates"] == 2
    assert serialized_bootstrap["matched_random_draws_per_replicate"] == 3
    assert serialized_bootstrap["detailed_replicates_sha256"] == runner._value_sha256(
        result.primary_inference.bootstrap.replicates
    )
