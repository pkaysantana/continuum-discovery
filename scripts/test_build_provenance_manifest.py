import unittest
import os
import sys
from pathlib import Path

# Ensure scripts directory is on sys.path regardless of execution CWD
sys.path.insert(0, str(Path(__file__).resolve().parent))

import tempfile
import shutil
import subprocess
import json
import csv
import time
import stat
import hashlib

from build_provenance_manifest import (
    build_manifest,
    get_file_metadata,
    get_git_tracked_files,
    get_audit_metadata,
    run_cmd,
    check_is_lfs_pointer,
    GitCommandError,
    DirtyRepositoryError
)


def remove_readonly(func, path, _):
    """Helper to delete read-only files on Windows."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


class TestBuildProvenanceManifest(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for our mock repository
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()

        # Initialize a git repository
        subprocess.run(["git", "init"], cwd=self.test_dir, check=True, stdout=subprocess.DEVNULL)

        # Configure local git user for commits
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.test_dir, check=True)

        # Create dummy file 1 (simulating text file)
        self.file1_path = os.path.join(self.test_dir, "dummy1.txt")
        with open(self.file1_path, "wb") as f:
            f.write(b"Initial content for dummy1.\n")

        # Create dummy file 2 (simulating opaque scientific file, like PDB)
        self.file2_path = os.path.join(self.test_dir, "structure.pdb")
        with open(self.file2_path, "wb") as f:
            f.write(b"HEADER    TEST STRUCTURE\nATOM      1  N   ALA A   1      11.104  10.231  12.012  1.00 10.00           N\n")

        # Create dummy file 3 (simulating Git LFS pointer)
        self.lfs_path = os.path.join(self.test_dir, "large_model.bin")
        with open(self.lfs_path, "wb") as f:
            f.write(
                b"version https://git-lfs.github.com/spec/v1\n"
                b"oid sha256:4d7a214614ab2935c943f9e0ff69d22ecd5421d0fbe8f66f883612b4ff9cdbfd\n"
                b"size 12345678\n"
            )

        # Commit initial batch
        subprocess.run(["git", "add", "dummy1.txt", "structure.pdb", "large_model.bin"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.test_dir, check=True, stdout=subprocess.DEVNULL)

        # Sleep to guarantee distinct timestamps between commits
        time.sleep(1)

        # Update file 1 and commit again to create commit history
        with open(self.file1_path, "ab") as f:
            f.write(b"Second line in dummy1.\n")

        subprocess.run(["git", "add", "dummy1.txt"], cwd=self.test_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Update dummy1"], cwd=self.test_dir, check=True, stdout=subprocess.DEVNULL)

    def tearDown(self):
        shutil.rmtree(self.test_dir, onerror=remove_readonly)
        shutil.rmtree(self.output_dir, onerror=remove_readonly)

    def test_clean_repo(self):
        """Auditing a clean repository succeeds and records clean status and audit timestamp."""
        manifest = build_manifest(self.test_dir, self.output_dir)
        self.assertTrue(manifest["audit"]["is_clean"])
        self.assertEqual(manifest["audit"]["repo_path"], os.path.abspath(self.test_dir))
        self.assertIn("head_commit", manifest["audit"])
        self.assertIn("head_commit_timestamp", manifest["audit"])
        self.assertIn("branch", manifest["audit"])
        self.assertIn("audit_timestamp", manifest["audit"])
        self.assertTrue(len(manifest["audit"]["audit_timestamp"]) > 0)
        self.assertEqual(len(manifest["files"]), 3)

    def test_dirty_repo_rejection(self):
        """Auditing a dirty repository without --allow-dirty raises DirtyRepositoryError."""
        # Make working directory dirty by modifying dummy1.txt
        with open(self.file1_path, "ab") as f:
            f.write(b"Uncommitted changes.\n")

        with self.assertRaises(DirtyRepositoryError):
            build_manifest(self.test_dir, self.output_dir, allow_dirty=False)

    def test_allow_dirty(self):
        """Auditing a dirty repository with --allow-dirty succeeds and flags is_clean as False."""
        with open(self.file1_path, "ab") as f:
            f.write(b"Uncommitted changes.\n")

        manifest = build_manifest(self.test_dir, self.output_dir, allow_dirty=True)
        self.assertFalse(manifest["audit"]["is_clean"])
        self.assertEqual(len(manifest["files"]), 3)

    def test_command_failure(self):
        """Failing Git commands raise GitCommandError with command, exit code, and stderr."""
        with self.assertRaises(GitCommandError) as ctx:
            run_cmd(["git", "rev-parse", "--verify", "nonexistent_ref_12345"], cwd=self.test_dir)

        err = ctx.exception
        self.assertNotEqual(err.returncode, 0)
        self.assertIn("rev-parse", err.cmd)
        self.assertTrue(len(err.stderr) > 0)
        self.assertIn("Git command failed", str(err))
        self.assertIn("Exit code:", str(err))
        self.assertIn("Stderr:", str(err))

    def test_correct_head_capture(self):
        """Audit accurately records the HEAD commit SHA and timestamp."""
        expected_head = run_cmd(["git", "rev-parse", "HEAD"], cwd=self.test_dir)
        expected_ts = run_cmd(["git", "log", "-1", "--format=%cI", "HEAD"], cwd=self.test_dir)

        audit_meta = get_audit_metadata(self.test_dir)
        self.assertEqual(audit_meta["head_commit"], expected_head)
        self.assertEqual(audit_meta["head_commit_timestamp"], expected_ts)

    def test_branch_and_detached_head_handling(self):
        """Audit accurately records the active branch name or DETACHED_HEAD when detached."""
        # 1. On active branch
        current_branch = run_cmd(["git", "branch", "--show-current"], cwd=self.test_dir)
        audit_meta_branch = get_audit_metadata(self.test_dir)
        self.assertEqual(audit_meta_branch["branch"], current_branch if current_branch else "DETACHED_HEAD")

        # 2. In detached HEAD state
        head_commit = run_cmd(["git", "rev-parse", "HEAD"], cwd=self.test_dir)
        subprocess.run(["git", "checkout", head_commit], cwd=self.test_dir, check=True, stderr=subprocess.DEVNULL)

        audit_meta_detached = get_audit_metadata(self.test_dir)
        self.assertEqual(audit_meta_detached["branch"], "DETACHED_HEAD")

    def test_first_vs_last_commit_timestamps(self):
        """Files with multiple commits have distinct first and last commit SHAs and ordered timestamps."""
        head_commit = run_cmd(["git", "rev-parse", "HEAD"], cwd=self.test_dir)
        meta = get_file_metadata(self.test_dir, "dummy1.txt", head_ref=head_commit)

        self.assertIsNotNone(meta)
        self.assertNotEqual(meta["first_commit_sha"], meta["last_commit_sha"])
        self.assertEqual(meta["last_commit_sha"], head_commit)
        self.assertTrue(len(meta["first_commit_timestamp"]) > 0)
        self.assertTrue(len(meta["last_commit_timestamp"]) > 0)
        self.assertLessEqual(meta["first_commit_timestamp"], meta["last_commit_timestamp"])

        # structure.pdb was only committed once
        pdb_meta = get_file_metadata(self.test_dir, "structure.pdb", head_ref=head_commit)
        self.assertEqual(pdb_meta["first_commit_sha"], pdb_meta["last_commit_sha"])
        self.assertEqual(pdb_meta["first_commit_timestamp"], pdb_meta["last_commit_timestamp"])

    def test_git_blob_sha(self):
        """Git blob SHA matches git rev-parse HEAD:<path> exactly."""
        head_commit = run_cmd(["git", "rev-parse", "HEAD"], cwd=self.test_dir)
        expected_blob = run_cmd(["git", "rev-parse", f"HEAD:dummy1.txt"], cwd=self.test_dir)

        meta = get_file_metadata(self.test_dir, "dummy1.txt", head_ref=head_commit)
        self.assertEqual(meta["git_blob_sha"], expected_blob)

    def test_filesystem_sha256(self):
        """Filesystem SHA-256 matches independent computation over raw bytes for all files."""
        head_commit = run_cmd(["git", "rev-parse", "HEAD"], cwd=self.test_dir)

        for filename in ["dummy1.txt", "structure.pdb", "large_model.bin"]:
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, "rb") as f:
                expected_sha256 = hashlib.sha256(f.read()).hexdigest()

            meta = get_file_metadata(self.test_dir, filename, head_ref=head_commit)
            self.assertIsNotNone(meta)
            self.assertEqual(meta["filesystem_sha256"], expected_sha256)
            self.assertEqual(meta["sha256"], expected_sha256)
            self.assertEqual(len(meta["filesystem_sha256"]), 64)

    def test_lfs_pointer_detection(self):
        """Git LFS pointer files are detected without downloading content."""
        head_commit = run_cmd(["git", "rev-parse", "HEAD"], cwd=self.test_dir)

        # LFS pointer file
        lfs_meta = get_file_metadata(self.test_dir, "large_model.bin", head_ref=head_commit)
        self.assertTrue(lfs_meta["is_lfs_pointer"])

        # Regular file
        txt_meta = get_file_metadata(self.test_dir, "dummy1.txt", head_ref=head_commit)
        self.assertFalse(txt_meta["is_lfs_pointer"])

        # PDB file
        pdb_meta = get_file_metadata(self.test_dir, "structure.pdb", head_ref=head_commit)
        self.assertFalse(pdb_meta["is_lfs_pointer"])

    def test_json_and_csv_output(self):
        """JSON output contains audit metadata and files list; CSV contains file rows."""
        build_manifest(self.test_dir, self.output_dir)

        json_path = os.path.join(self.output_dir, "provenance_manifest.json")
        csv_path = os.path.join(self.output_dir, "provenance_manifest.csv")

        self.assertTrue(os.path.isfile(json_path))
        self.assertTrue(os.path.isfile(csv_path))

        with open(json_path, "r", encoding="utf-8") as jf:
            doc = json.load(jf)

        self.assertIn("audit", doc)
        self.assertIn("files", doc)
        self.assertEqual(len(doc["files"]), 3)

        with open(csv_path, "r", encoding="utf-8", newline="") as cf:
            reader = csv.DictReader(cf)
            rows = list(reader)

        self.assertEqual(len(rows), 3)
        row_paths = [r["relative_path"] for r in rows]
        self.assertIn("dummy1.txt", row_paths)
        self.assertIn("structure.pdb", row_paths)
        self.assertIn("large_model.bin", row_paths)


if __name__ == "__main__":
    unittest.main()
