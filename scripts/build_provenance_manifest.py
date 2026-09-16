import os
import subprocess
import hashlib
import json
import csv
import argparse
from datetime import datetime, timezone
from pathlib import Path


class GitCommandError(RuntimeError):
    """Raised when a Git command exits with a non-zero status."""
    def __init__(self, cmd, returncode, stdout, stderr):
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
        message = (
            f"Git command failed: {cmd_str}\n"
            f"Exit code: {returncode}\n"
            f"Stderr: {stderr.strip()}\n"
            f"Stdout: {stdout.strip()}"
        )
        super().__init__(message)
        self.cmd = cmd
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class DirtyRepositoryError(RuntimeError):
    """Raised when auditing a dirty repository without --allow-dirty."""
    pass


def run_cmd(cmd, cwd=None):
    """Runs a command and fails loudly if the return code is non-zero."""
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd
    )
    if result.returncode != 0:
        raise GitCommandError(cmd, result.returncode, result.stdout, result.stderr)
    return result.stdout.strip()


def check_is_lfs_pointer(absolute_path):
    """
    Detects if a file is a Git LFS pointer without downloading or interpreting biological content.
    LFS pointer files are small text files starting with 'version https://git-lfs.github.com/spec/v1'.
    """
    try:
        # LFS pointers are tiny text files, typically ~130-200 bytes.
        if os.path.getsize(absolute_path) > 1024:
            return False
        with open(absolute_path, "rb") as f:
            header = f.read(100)
            return header.startswith(b"version https://git-lfs.github.com/spec/v1")
    except Exception:
        return False


def get_audit_metadata(repo_path=".", allow_dirty=False):
    """
    Collects repository-level audit metadata before running file audits.
    Fails loudly if the repository is dirty unless allow_dirty is True.
    """
    abs_repo_path = os.path.abspath(repo_path)

    # HEAD commit SHA
    head_commit = run_cmd(["git", "rev-parse", "HEAD"], cwd=abs_repo_path)

    # HEAD commit timestamp (strict ISO 8601)
    head_commit_timestamp = run_cmd(["git", "log", "-1", "--format=%cI", "HEAD"], cwd=abs_repo_path)

    # Current branch or DETACHED_HEAD
    branch_output = run_cmd(["git", "branch", "--show-current"], cwd=abs_repo_path)
    branch = branch_output if branch_output else "DETACHED_HEAD"

    # Clean status check
    status_output = run_cmd(["git", "status", "--porcelain"], cwd=abs_repo_path)
    is_clean = (len(status_output) == 0)

    if not is_clean and not allow_dirty:
        raise DirtyRepositoryError(
            f"Repository at '{abs_repo_path}' has uncommitted changes. "
            f"Refusing to audit without --allow-dirty.\n"
            f"Status output:\n{status_output}"
        )

    audit_timestamp = datetime.now(timezone.utc).isoformat()

    return {
        "repo_path": abs_repo_path,
        "absolute_repository_path": abs_repo_path,
        "head_commit": head_commit,
        "audited_head_sha": head_commit,
        "head_commit_timestamp": head_commit_timestamp,
        "branch": branch,
        "is_clean": is_clean,
        "is_worktree_clean": is_clean,
        "audit_timestamp": audit_timestamp
    }


def get_git_tracked_files(repo_path="."):
    """Returns a list of tracked files in the git repository."""
    output = run_cmd(["git", "ls-files"], cwd=repo_path)
    if not output:
        return []
    return [f for f in output.split('\n') if f]


def get_file_metadata(repo_path, relative_file_path, head_ref="HEAD"):
    """
    Gets metadata for a specific tracked file.
    Treats biological artefacts as opaque bytes without parsing them.
    """
    abs_repo_path = os.path.abspath(repo_path)
    absolute_path = os.path.join(abs_repo_path, relative_file_path)

    # Check if the file exists on the filesystem
    if not os.path.isfile(absolute_path):
        return None

    # Extension
    _, ext = os.path.splitext(relative_file_path)

    # Byte size
    byte_size = os.path.getsize(absolute_path)

    # Filesystem SHA-256 (streaming binary chunks; treats scientific files as opaque bytes)
    sha256_hash = hashlib.sha256()
    with open(absolute_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256_hash.update(chunk)
    fs_sha256 = sha256_hash.hexdigest()

    # Normalize relative path with forward slashes for Git operations
    git_file_path = relative_file_path.replace(os.sep, "/").replace("\\", "/")

    # Git blob SHA as of audited HEAD
    blob_sha = run_cmd(["git", "rev-parse", f"{head_ref}:{git_file_path}"], cwd=abs_repo_path)

    # First commit containing the file
    first_commit_out = run_cmd(
        ["git", "log", head_ref, "--diff-filter=A", "--root", "--format=%H|%cI", "-1", "--", git_file_path],
        cwd=abs_repo_path
    )
    if not first_commit_out:
        # Fallback to reverse log if diff-filter=A didn't match
        first_commit_out = run_cmd(
            ["git", "log", head_ref, "--format=%H|%cI", "--reverse", "--", git_file_path],
            cwd=abs_repo_path
        )
        first_commit_out = first_commit_out.split('\n')[0] if first_commit_out else ""

    if "|" in first_commit_out:
        first_commit_sha, first_commit_ts = first_commit_out.split("|", 1)
    else:
        first_commit_sha, first_commit_ts = first_commit_out, ""

    # Last commit affecting the file as of audited HEAD
    last_commit_out = run_cmd(
        ["git", "log", head_ref, "-1", "--format=%H|%cI", "--", git_file_path],
        cwd=abs_repo_path
    )
    if "|" in last_commit_out:
        last_commit_sha, last_commit_ts = last_commit_out.split("|", 1)
    else:
        last_commit_sha, last_commit_ts = last_commit_out, ""

    # LFS pointer detection (no download, opaque check)
    is_lfs = check_is_lfs_pointer(absolute_path)

    return {
        "relative_path": git_file_path,
        "extension": ext,
        "byte_size": byte_size,
        "filesystem_sha256": fs_sha256,
        "git_blob_sha": blob_sha,
        "first_commit_sha": first_commit_sha,
        "first_commit_timestamp": first_commit_ts,
        "last_commit_sha": last_commit_sha,
        "last_commit_timestamp": last_commit_ts,
        "is_lfs_pointer": is_lfs,
        # Backward compatibility aliases
        "sha256": fs_sha256,
        "first_commit": first_commit_sha,
        "last_commit": last_commit_sha,
        "commit_timestamp": last_commit_ts
    }


def build_manifest(repo_path=".", output_dir=".", allow_dirty=False):
    """
    Audits the repository and writes provenance_manifest.json and provenance_manifest.csv.
    """
    abs_repo_path = os.path.abspath(repo_path)
    abs_output_dir = os.path.abspath(output_dir)
    os.makedirs(abs_output_dir, exist_ok=True)

    # 1. Collect repository-level audit metadata (fails loudly if dirty unless allow_dirty=True)
    audit_meta = get_audit_metadata(abs_repo_path, allow_dirty=allow_dirty)

    # 2. Collect file-level records
    tracked_files = get_git_tracked_files(abs_repo_path)
    manifest_files = []

    for f in tracked_files:
        metadata = get_file_metadata(abs_repo_path, f, head_ref=audit_meta["head_commit"])
        if metadata:
            manifest_files.append(metadata)

    # 3. Top-level manifest object
    manifest_doc = {
        "audit": audit_meta,
        "files": manifest_files
    }

    # 4. Write JSON
    json_path = os.path.join(abs_output_dir, "provenance_manifest.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(manifest_doc, jf, indent=2)

    # 5. Write CSV (preserving file-level records)
    csv_path = os.path.join(abs_output_dir, "provenance_manifest.csv")
    fieldnames = [
        "relative_path",
        "extension",
        "byte_size",
        "filesystem_sha256",
        "git_blob_sha",
        "first_commit_sha",
        "first_commit_timestamp",
        "last_commit_sha",
        "last_commit_timestamp",
        "is_lfs_pointer",
        "sha256",
        "first_commit",
        "last_commit",
        "commit_timestamp"
    ]
    with open(csv_path, "w", newline='', encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(manifest_files)

    return manifest_doc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build deterministic provenance manifests (JSON/CSV) for a Git repository."
    )
    parser.add_argument("--repo-path", type=str, default=".", help="Path to the repository to audit.")
    parser.add_argument("--output-dir", type=str, default=".", help="Directory to save the manifests.")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow auditing when the repository has uncommitted changes."
    )
    args = parser.parse_args()

    build_manifest(args.repo_path, args.output_dir, allow_dirty=args.allow_dirty)
    print(f"Manifests successfully built in {os.path.abspath(args.output_dir)}")
