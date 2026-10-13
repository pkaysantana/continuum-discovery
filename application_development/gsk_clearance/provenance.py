"""Local, reviewable provenance checks. Hash matching is not authentication.

Only preparation reads historical source files. Modelling verifies a separate
export against hashes pinned by a reviewer, not hashes supplied by its caller.
"""
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from importlib.metadata import version

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
HISTORICAL = "experiments/compound_to_exposure/"


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def digest(value):
    return sha256(encoded(value))


def checked_bytes(path, expected):
    data = Path(path).read_bytes()
    if sha256(data) != expected:
        raise ValueError("file SHA-256 mismatch: " + str(path))
    return data


def runtime():
    return {"python": platform.python_version(), "executable": sys.executable,
            "platform": platform.platform(), "machine": platform.machine(),
            "packages": {p: version(p) for p in ("numpy", "scipy", "scikit-learn", "rdkit")}}


def code_hashes():
    hashes = {f.name: sha256(f.read_bytes()) for f in sorted(HERE.glob("*.py"))}
    # The only historical import is pure feature code; include its actual bytes.
    hashes["experiments/compound_to_exposure/src/representations.py"] = sha256(
        (REPO / HISTORICAL / "src/representations.py").read_bytes())
    return hashes


def code_state(root=REPO):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE).strip()
    try:
        revision, state = git("rev-parse", "HEAD"), git("status", "--porcelain=v1")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # An isolated code-only deployment must not mount the full repository or
        # .git (which also contains historical outcomes). Never invent clean state.
        revision, state = None, "GIT_UNAVAILABLE_CODE_ONLY_DEPLOYMENT"
    return {"revision": revision, "working_tree": state,
            "code_sha256": code_hashes()}


def input_manifest():
    return json.loads((HERE / "input_manifest.json").read_bytes())


def assignment_digest(members):
    # Full identity and activity/compound IDs bind assignments, not fold order alone.
    return digest(sorted(members, key=lambda r: r["activity_id"]))


def verify_authorities(root, manifest):
    """Check local evidence against exact committed historical evidence bytes."""
    authorities = {}
    for name, spec in manifest["authorities"].items():
        data = checked_bytes(Path(root) / HISTORICAL / spec["path"], spec["sha256"])
        committed = subprocess.check_output([
            "git", "-C", str(root), "show",
            manifest["evidence_revision"] + ":" + HISTORICAL + spec["path"]])
        if data != committed:
            raise ValueError("historical authority differs from committed evidence")
        authorities[name] = json.loads(data)
    inputs = {r["filename"]: r["sha256"] for r in authorities["execution"]["inputs"]}
    for spec in manifest["sources"].values():
        if inputs.get(spec["path"]) != spec["sha256"]:
            raise ValueError("source hash lacks historical manifest support")
    if authorities["selection"]["master_partition_hash"] != manifest["partition"]["sha256"]:
        raise ValueError("partition hash lacks historical manifest support")
    if authorities["execution"]["repository_commit"] != manifest["revisions"]["historical_execution"]:
        raise ValueError("historical execution revision mismatch")


def require_execution_gate():
    gate = json.loads((HERE / "execution_gate.json").read_bytes())
    if gate.get("status") != "APPROVED":
        raise PermissionError("real modelling blocked: execution gate is NOT_READY")
    if gate.get("wall_seconds") != 900 or gate.get("memory_limit", {}).get("required_bytes") != 2000000000:
        raise PermissionError("resource contract differs from frozen limits")
    for name in ("filesystem_isolation", "memory_limit"):
        evidence = gate.get(name, {})
        if evidence.get("status") != "VERIFIED":
            raise PermissionError(name + " has not been verified")
        checked_bytes(evidence["evidence_path"], evidence["evidence_sha256"])
    if not gate.get("approval_reference"):
        raise PermissionError("missing separate execution approval")
    if gate.get("approved_code_sha256") != code_hashes() or not gate.get("approved_code_revision"):
        raise PermissionError("running code differs from reviewed code snapshot")
    return gate
