import json
from collections import Counter, defaultdict
from pathlib import Path


def generate_summary(manifest_json_path, output_md_path):
    with open(manifest_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    audit = data["audit"]
    files = data["files"]

    total_files = len(files)
    total_bytes = sum(f["byte_size"] for f in files)

    ext_counts = Counter(f["extension"] if f["extension"] else "(no extension)" for f in files)

    def get_top_level(path):
        parts = path.replace("\\", "/").split("/")
        if len(parts) > 1:
            return parts[0]
        return "(root)"

    top_dir_counts = Counter(get_top_level(f["relative_path"]) for f in files)

    first_commits = set(f["first_commit_sha"] for f in files if f.get("first_commit_sha"))
    last_commits = set(f["last_commit_sha"] for f in files if f.get("last_commit_sha"))

    all_timestamps = []
    for f in files:
        if f.get("first_commit_timestamp"):
            all_timestamps.append(f["first_commit_timestamp"])
        if f.get("last_commit_timestamp"):
            all_timestamps.append(f["last_commit_timestamp"])

    earliest_ts = min(all_timestamps) if all_timestamps else "N/A"
    latest_ts = max(all_timestamps) if all_timestamps else "N/A"

    lfs_count = sum(1 for f in files if f.get("is_lfs_pointer"))

    missing_meta_files = []
    for f in files:
        missing_fields = []
        for field in [
            "relative_path",
            "byte_size",
            "filesystem_sha256",
            "git_blob_sha",
            "first_commit_sha",
            "first_commit_timestamp",
            "last_commit_sha",
            "last_commit_timestamp",
        ]:
            if f.get(field) is None or f.get(field) == "":
                missing_fields.append(field)
        if missing_fields:
            missing_meta_files.append((f.get("relative_path"), missing_fields))

    sha_groups = defaultdict(list)
    for f in files:
        sha_groups[f["filesystem_sha256"]].append(f["relative_path"])

    dup_groups = {h: p for h, p in sha_groups.items() if len(p) > 1}

    lines = []
    lines.append("# Historical Provenance Audit Summary: Snapshot `f2495d8`\n")
    lines.append("## Repository Audit Metadata")
    lines.append(f"- **Audited Repository Path**: `{audit.get('repo_path')}`")
    lines.append(f"- **Audited HEAD Commit SHA**: `{audit.get('head_commit')}`")
    lines.append(f"- **Audited HEAD Timestamp**: `{audit.get('head_commit_timestamp')}`")
    lines.append(f"- **Branch / State**: `{audit.get('branch')}`")
    lines.append(f"- **Worktree Clean**: `{audit.get('is_clean')}`")
    lines.append(f"- **Audit Generation Timestamp**: `{audit.get('audit_timestamp')}`\n")

    lines.append("## High-Level Summary Metrics")
    lines.append(f"- **Total Tracked Files**: {total_files:,}")
    lines.append(f"- **Total Bytes**: {total_bytes:,} bytes ({total_bytes / (1024 * 1024):.2f} MB)")
    lines.append(f"- **Number of Unique First Commits**: {len(first_commits)}")
    lines.append(f"- **Number of Unique Last Commits**: {len(last_commits)}")
    lines.append(f"- **Earliest Commit Timestamp**: `{earliest_ts}`")
    lines.append(f"- **Latest Commit Timestamp**: `{latest_ts}`")
    lines.append(f"- **Number of LFS Pointers**: {lfs_count}")
    lines.append(f"- **Files with Missing Metadata**: {len(missing_meta_files)}")
    lines.append(f"- **Duplicate SHA-256 Groups**: {len(dup_groups)} groups\n")

    lines.append("## File Counts by Extension")
    lines.append("| Extension | Count | Total Bytes |")
    lines.append("| :--- | :--- | :--- |")
    ext_bytes = defaultdict(int)
    for f in files:
        ext_bytes[f["extension"] if f["extension"] else "(no extension)"] += f["byte_size"]

    for ext, count in ext_counts.most_common():
        b = ext_bytes[ext]
        lines.append(f"| `{ext}` | {count:,} | {b:,} bytes ({b / (1024 * 1024):.2f} MB) |")

    lines.append("\n## File Counts by Top-Level Directory")
    lines.append("| Top-Level Directory | Count | Total Bytes |")
    lines.append("| :--- | :--- | :--- |")
    dir_bytes = defaultdict(int)
    for f in files:
        d = get_top_level(f["relative_path"])
        dir_bytes[d] += f["byte_size"]

    for d, count in top_dir_counts.most_common():
        b = dir_bytes[d]
        lines.append(f"| `{d}` | {count:,} | {b:,} bytes ({b / (1024 * 1024):.2f} MB) |")

    lines.append("\n## Files with Missing Metadata")
    if not missing_meta_files:
        lines.append(
            "None. All tracked files have complete metadata records (relative path, extension, "
            "byte size, filesystem SHA-256, Git blob SHA, first commit SHA/timestamp, and "
            "last commit SHA/timestamp).\n"
        )
    else:
        lines.append(f"{len(missing_meta_files)} files have missing fields:\n")
        for path, fields in missing_meta_files:
            lines.append(f"- `{path}`: missing {fields}")

    lines.append("## Duplicate SHA-256 Groups")
    lines.append(
        f"There are **{len(dup_groups)}** groups of files sharing identical filesystem SHA-256 checksums:\n"
    )
    for idx, (h, group_files) in enumerate(
        sorted(dup_groups.items(), key=lambda x: len(x[1]), reverse=True), 1
    ):
        lines.append(f"### Group {idx}: `{h}` ({len(group_files)} files)")
        for gf in sorted(group_files):
            lines.append(f"- `{gf}`")
        lines.append("")

    summary_content = "\n".join(lines)
    Path(output_md_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_md_path, "w", encoding="utf-8") as sf:
        sf.write(summary_content)

    print(f"Wrote audit summary to {output_md_path} ({len(summary_content)} bytes)")


if __name__ == "__main__":
    generate_summary(
        "audit/historical/f2495d8/provenance_manifest.json",
        "audit/historical/f2495d8/audit_summary.md",
    )
