import os
import subprocess
import hashlib
import json
import csv
import argparse
from pathlib import Path

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()

def get_git_tracked_files(repo_path="."):
    """Returns a list of tracked files in the git repository."""
    output = run_cmd(["git", "ls-files"], cwd=repo_path)
    if not output:
        return []
    return [f for f in output.split('\n') if f]

def get_file_metadata(repo_path, relative_file_path):
    """Gets metadata for a specific tracked file."""
    absolute_path = os.path.join(repo_path, relative_file_path)
    
    # Check if it actually exists in the filesystem (might be removed or just not accessible)
    if not os.path.isfile(absolute_path):
        return None

    # Get extension
    _, ext = os.path.splitext(relative_file_path)
    
    # Get byte size
    byte_size = os.path.getsize(absolute_path)
    
    # Compute SHA-256 by treating file as opaque bytes
    sha256_hash = hashlib.sha256()
    with open(absolute_path, "rb") as f:
        # Read in chunks to avoid memory issues with large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            
    hash_hex = sha256_hash.hexdigest()
    
    # Git metadata
    # First commit containing the file
    first_commit = run_cmd(["git", "log", "--diff-filter=A", "--format=%H", "-1", "--", relative_file_path], cwd=repo_path)
    
    # Fallback to just the oldest commit if --diff-filter=A doesn't find it (e.g. if it was added in a different way or it's the root commit)
    if not first_commit:
        first_commit_out = run_cmd(["git", "log", "--format=%H", "--reverse", "--", relative_file_path], cwd=repo_path)
        first_commit = first_commit_out.split('\n')[0] if first_commit_out else ""

    # Last commit affecting the file
    last_commit = run_cmd(["git", "log", "-1", "--format=%H", "--", relative_file_path], cwd=repo_path)
    
    # Commit timestamp (ISO 8601 strict)
    commit_timestamp = run_cmd(["git", "log", "-1", "--format=%cI", "--", relative_file_path], cwd=repo_path)

    return {
        "relative_path": relative_file_path,
        "extension": ext,
        "byte_size": byte_size,
        "sha256": hash_hex,
        "first_commit": first_commit,
        "last_commit": last_commit,
        "commit_timestamp": commit_timestamp
    }

def build_manifest(repo_path=".", output_dir="."):
    repo_path = os.path.abspath(repo_path)
    output_dir = os.path.abspath(output_dir)
    
    files = get_git_tracked_files(repo_path)
    manifest = []
    
    for f in files:
        metadata = get_file_metadata(repo_path, f)
        if metadata:
            manifest.append(metadata)
            
    # Write JSON
    json_path = os.path.join(output_dir, "provenance_manifest.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(manifest, jf, indent=2)
        
    # Write CSV
    csv_path = os.path.join(output_dir, "provenance_manifest.csv")
    if manifest:
        keys = manifest[0].keys()
        with open(csv_path, "w", newline='', encoding="utf-8") as cf:
            writer = csv.DictWriter(cf, fieldnames=keys)
            writer.writeheader()
            writer.writerows(manifest)
    else:
        # Write empty CSV with headers if no files
        keys = ["relative_path", "extension", "byte_size", "sha256", "first_commit", "last_commit", "commit_timestamp"]
        with open(csv_path, "w", newline='', encoding="utf-8") as cf:
            writer = csv.DictWriter(cf, fieldnames=keys)
            writer.writeheader()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build deterministic provenance manifests (JSON/CSV) for a Git repository.")
    parser.add_argument("--repo-path", type=str, default=".", help="Path to the repository to audit.")
    parser.add_argument("--output-dir", type=str, default=".", help="Directory to save the manifests.")
    args = parser.parse_args()
    
    build_manifest(args.repo_path, args.output_dir)
    print(f"Manifests successfully built in {os.path.abspath(args.output_dir)}")
