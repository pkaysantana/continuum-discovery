"""Small external watchdog and exclusive result writer; no memory sandbox."""
import csv
import json
import math
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from . import provenance as p


def write_json(path, value):
    with Path(path).open("xb") as fh:
        fh.write(p.encoded(value))


def validate_result(result, manifest):
    from .harness import REPRESENTATIONS, metrics, Configuration
    from dataclasses import asdict
    expected = sorted(manifest["members"], key=lambda r: r["id"])
    if result["status"] != "EXPLORATORY_DEVELOPMENT_ONLY":
        raise ValueError("invalid result status")
    for name, key in (("row_order", "id"), ("activity_ids", "activity_id"), ("folds", "fold")):
        if result[name] != [r[key] for r in expected]:
            raise ValueError("result alignment mismatch")
    if manifest["kind"] == "development" and result["requested_configuration"] != asdict(Configuration()):
        raise ValueError("result configuration differs from frozen experiment")
    observed = result["observed_log10"]
    if len(observed) != len(expected) or not all(math.isfinite(v) for v in observed):
        raise ValueError("invalid observed vector")
    names = {*REPRESENTATIONS, "mean_baseline", "median_baseline"}
    if set(result["predictions"]) != names or set(result["pooled_oof_metrics"]) != names:
        raise ValueError("incomplete result models")
    folds = sorted({r["fold"] for r in expected})
    if set(result["per_fold_metrics"]) != {str(f) for f in folds}:
        raise ValueError("incomplete fold metrics")
    actual_fits = [(r["fold"], r["pipeline"]) for r in result["fitted_configurations"]]
    if sorted(actual_fits) != sorted((f, name) for f in folds for name in REPRESENTATIONS):
        raise ValueError("incomplete or duplicate fitted configurations")
    for name, predicted in result["predictions"].items():
        if metrics(observed, predicted) != result["pooled_oof_metrics"][name]:
            raise ValueError("pooled metric mismatch")
        for fold in folds:
            ix = [i for i, r in enumerate(expected) if r["fold"] == fold]
            if metrics([observed[i] for i in ix], [predicted[i] for i in ix]) != result["per_fold_metrics"][str(fold)][name]:
                raise ValueError("fold metric mismatch")


def _terminate_tree(process):
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       creationflags=subprocess.CREATE_NO_WINDOW, check=False)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if process.poll() is None:
        process.kill()
    process.wait()


def run_supervised(command, destination, manifest, input_receipt, *, wall_seconds=900):
    """Trusted orchestration helper; worker writes candidate_result.json only.

    The supervisor exclusively creates the run directory and alone publishes
    COMPLETE.json after successful worker exit and result validation. A killed
    supervisor leaves STARTED without COMPLETE: never interpret that as success.
    """
    if not 0 < wall_seconds <= 900:
        raise ValueError("wall limit must be positive and at most 900 seconds")
    dest = Path(destination).resolve()
    if dest.is_relative_to(p.REPO / p.HISTORICAL):
        raise PermissionError("cannot write historical scientific subtree")
    dest.mkdir(parents=True, exist_ok=False)
    receipt = {"run_id": str(uuid4()), "started_utc": datetime.now(timezone.utc).isoformat(),
               "wall_seconds": wall_seconds, "memory_limit_enforced": False,
               "threads": {k: "1" for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
               "command": list(command), "status": "STARTED"}
    process = None
    started = time.monotonic()
    try:
        receipt.update(code=p.code_state(), runtime=p.runtime())
        write_json(dest / "STARTED.json", receipt)
        write_json(dest / "input_manifest.json", manifest)
        write_json(dest / "input_receipt.json", input_receipt)
        env = dict(os.environ, **receipt["threads"], PYTHONDONTWRITEBYTECODE="1",
                   GSK_CANDIDATE_RESULT=str(dest / "candidate_result.json"))
        kwargs = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {"start_new_session": True}
        with (dest / "stdout.log").open("xb") as stdout, (dest / "stderr.log").open("xb") as stderr:
            process = subprocess.Popen(command, env=env, stdout=stdout, stderr=stderr, **kwargs)
            receipt["worker_pid"] = process.pid
            try:
                code = process.wait(timeout=wall_seconds)
            except subprocess.TimeoutExpired:
                _terminate_tree(process)
                raise TimeoutError("external wall-clock watchdog expired") from None
        receipt["worker_exit_code"] = code
        if code != 0:
            raise RuntimeError("worker failed; see stderr.log")
        result = json.loads((dest / "candidate_result.json").read_bytes())
        validate_result(result, manifest)
        write_json(dest / "result.json", result)
        names = list(result["predictions"])
        with (dest / "oof_predictions.csv").open("x", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["activity_id", "compound_id", "fold", "observed_log10", *names])
            for i, cid in enumerate(result["row_order"]):
                writer.writerow([result["activity_ids"][i], cid, result["folds"][i], result["observed_log10"][i],
                                 *[result["predictions"][name][i] for name in names]])
        receipt.update(status="COMPLETED", elapsed_seconds=time.monotonic()-started,
                       ended_utc=datetime.now(timezone.utc).isoformat())
        write_json(dest / "execution_receipt.json", receipt)
        artifacts = {f.name: p.sha256(f.read_bytes()) for f in sorted(dest.iterdir()) if f.is_file()}
        write_json(dest / "artifacts.json", artifacts)
        # Verify bytes on disk before the sole success marker is written.
        for name, expected in artifacts.items():
            p.checked_bytes(dest / name, expected)
        write_json(dest / "COMPLETE.json", {"status": "COMPLETED", "artifacts_sha256": p.sha256((dest / "artifacts.json").read_bytes())})
        return dest
    except BaseException as exc:
        if process is not None and process.poll() is None:
            _terminate_tree(process)
        receipt.update(status="FAILED", error_type=type(exc).__name__,
                       elapsed_seconds=time.monotonic()-started,
                       ended_utc=datetime.now(timezone.utc).isoformat())
        write_json(dest / "FAILED.json", receipt)
        write_json(dest / "failure_artifacts.json", {
            f.name: p.sha256(f.read_bytes()) for f in sorted(dest.iterdir()) if f.is_file()})
        raise


def run_development(destination):
    # No caller override for approval, export hashes, configuration or limits.
    gate = p.require_execution_gate()
    from .export import approved_export
    _, receipt = approved_export()
    receipt = {**receipt, "execution_gate": gate}
    if gate["wall_seconds"] != 900:
        raise PermissionError("frozen wall-clock limit required")
    return run_supervised([sys.executable, "-B", "-m", "application_development.gsk_clearance.worker", "--development"],
                          destination, p.input_manifest(), receipt)
