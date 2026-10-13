"""Stage B input verification. This module never opens mixed-source files."""
import json
from . import provenance as p


def verify_export(export_path, receipt_path, manifest, *, export_sha256, receipt_sha256):
    """Shared verifier; expected hashes MUST come from an independent review.

    Production obtains them only from the fixed execution gate, below. Explicit
    arguments here support synthetic tests, not an alternative production gate.
    """
    receipt = json.loads(p.checked_bytes(receipt_path, receipt_sha256))
    if receipt.get("hash_verification") != "VERIFIED":
        raise PermissionError("skipped or missing hash verification receipt")
    if receipt.get("kind") != manifest["kind"]:
        raise ValueError("receipt kind mismatch")
    if receipt.get("input_manifest_canonical_sha256") != p.digest(manifest):
        raise ValueError("input manifest mismatch")
    if receipt.get("partition_file_sha256") != manifest["partition"]["sha256"]:
        raise ValueError("partition file hash receipt mismatch")
    expected_sources = {manifest["assay"]: manifest["sources"][manifest["assay"]]["sha256"]}
    if receipt.get("source_file_sha256") != expected_sources:
        raise ValueError("source file hash receipt mismatch")
    if receipt.get("assignments_sha256") != manifest["assignments_sha256"]:
        raise ValueError("assignment receipt mismatch")
    if receipt.get("export_sha256") != export_sha256:
        raise ValueError("export receipt mismatch")
    if receipt.get("endpoint_equivalence") != "CHECKED_EXACT_DECIMAL_AFTER_UNIT_CONVERSION":
        raise ValueError("missing endpoint equivalence receipt")
    bundle = json.loads(p.checked_bytes(export_path, export_sha256))
    if set(bundle) != {"records", "provenance"}:
        raise ValueError("unexpected export schema")
    rows = bundle["records"]
    metadata = [{k: r[k] for k in ("activity_id", "id", "smiles", "scaffold", "fold")} for r in rows]
    if sorted(metadata, key=lambda r: r["activity_id"]) != manifest["members"]:
        raise ValueError("export exact frozen membership or assignment mismatch")
    if p.assignment_digest(metadata) != manifest["assignments_sha256"]:
        raise ValueError("export assignment digest mismatch")
    if len(rows) != manifest["n"] or p.digest(rows) != bundle["provenance"]["records_sha256"]:
        raise ValueError("export records mismatch")
    if bundle["provenance"]["kind"] != manifest["kind"]:
        raise ValueError("export kind mismatch")
    return bundle, receipt


def approved_export():
    gate = p.require_execution_gate()
    manifest = p.input_manifest()
    if manifest["kind"] != "development" or gate["input_manifest_canonical_sha256"] != p.digest(manifest):
        raise PermissionError("reviewed development manifest required")
    from .harness import Configuration
    from dataclasses import asdict
    if gate["configuration_sha256"] != p.digest(asdict(Configuration())):
        raise PermissionError("fixed configuration not approved")
    bundle, receipt = verify_export(gate["export_path"], gate["receipt_path"], manifest,
                                   export_sha256=gate["export_sha256"], receipt_sha256=gate["receipt_sha256"])
    return bundle, receipt


def verify_development_bundle(records, provenance):
    bundle, _ = approved_export()
    if records != bundle["records"] or provenance != bundle["provenance"]:
        raise PermissionError("caller bundle differs from reviewed development export")
