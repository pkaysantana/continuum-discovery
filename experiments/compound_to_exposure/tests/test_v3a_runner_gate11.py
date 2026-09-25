"""Synthetic Gate 11 acceptance coverage for the v3A Ticket 1/2 runner.

Only synthetic models are fitted.  No outcome-dependent scientific metric is
computed and the real CHEMBL3301370 outcomes are never supplied to the runner.
"""
from __future__ import annotations

import ast
import hashlib
import json
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
    SCIENTIFIC_RUNS_RELATIVE,
    FrozenArtifactError,
    InternalRunStatus,
    LifecycleTransitionError,
    OutcomeBlindInputs,
    PredictionFreezeCollisionError,
    PredictionFreezeError,
    PredictionOrchestrationError,
    ProtectedRunPathError,
    RunAuthorizationError,
    RunCollisionError,
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

    def test_ties_use_frozen_hash_and_ignore_input_order(self):
        records = [
            _raw_rank_record(10, 1, 1.0),
            _raw_rank_record(20, 1, 1.0),
            _raw_rank_record(30, 1, 1.0),
        ]
        forward = rank_outcome_blind_records(records)
        reverse = rank_outcome_blind_records(list(reversed(records)))
        ranks_forward = {
            row["activity_id"]: row["within_fold_ranks"]["qrf_width"] for row in forward
        }
        ranks_reverse = {
            row["activity_id"]: row["within_fold_ranks"]["qrf_width"] for row in reverse
        }
        expected_order = sorted(
            (10, 20, 30),
            key=lambda activity_id: hashlib.sha256(
                f"V3A_TIE_20260923{activity_id}".encode("utf-8")
            ).hexdigest(),
        )
        assert ranks_forward == ranks_reverse
        assert [activity_id for activity_id, _rank in sorted(ranks_forward.items(), key=lambda x: x[1])] == expected_order

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


def test_ticket2_runner_has_no_outcome_evaluation_implementation():
    source_path = PROJECT_ROOT / "src" / "v3a_runner.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imported_or_called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "src.v3a_qrf_weights":
            imported_or_called.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            imported_or_called.add(node.func.id)
    prohibited = {
        "rmse",
        "mae",
        "rel_benefit_80",
        "matched_random_retention_rmse",
        "scaffold_bootstrap_indices",
        "interval_calibration_summary",
    }
    assert imported_or_called.isdisjoint(prohibited)
