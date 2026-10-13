"""Stage A: separately authorised preparation; never model fitting.

Mixed CSV bytes and excluded outcome STRINGS are read/materialised by DictReader.
Only validated development outcomes are numerically converted or exported.
This is filtering, not filesystem or memory isolation. Do not run preparation
without separate approval acknowledging this access boundary.
"""
import csv
import io
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from rdkit import Chem
from . import provenance as p


def canonical_identity(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None or mol.GetNumAtoms() == 0:
        raise ValueError("invalid SMILES")
    return Chem.MolToSmiles(mol, isomericSmiles=True)


def csv_rows(data, required):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    fields = reader.fieldnames or []
    if len(fields) != len(set(fields)) or not required.issubset(fields):
        raise ValueError("missing or duplicate CSV columns")
    for row in reader:
        if None in row or any(v is None for v in row.values()):
            raise ValueError("malformed CSV row")
        yield row


def partition_members(rows, manifest):
    """Validate membership before opening outcome-bearing sources."""
    hold_a = set(manifest["protected_activity_ids"])
    hold_c = set(manifest["protected_compound_ids"])
    hold_a.update(r["activity_id"] for r in rows if r["partition"] == "holdout")
    hold_c.update(r["chembl_id"] for r in rows if r["partition"] == "holdout")
    candidates = [r for r in rows if r["partition"] == "cv" and r["status"] == "INTERIOR_OBSERVED"]
    members, aids, cids, identities, groups = [], set(), set(), set(), {}
    from .harness import scaffold_key
    for row in candidates:
        aid, cid = row["activity_id"], row["chembl_id"]
        if aid in hold_a or cid in hold_c:
            raise PermissionError("holdout activity or compound collision before outcomes")
        if not aid or aid in aids:
            raise ValueError("duplicate or empty activity ID")
        if not cid or cid in cids:
            raise ValueError("duplicate or empty compound ID")
        aids.add(aid)
        cids.add(cid)
        fold = Decimal(row["cv_fold"])
        if not fold.is_finite() or fold != fold.to_integral_value() or not 0 <= fold <= 4:
            raise ValueError("invalid integral frozen fold")
        identity = canonical_identity(row["canonical_smiles"])
        if identity in identities:
            raise ValueError("duplicate molecular identity")
        identities.add(identity)
        scaffold = scaffold_key(row["canonical_smiles"])
        if scaffold != row["scaffold_key"]:
            raise ValueError("scaffold mismatch")
        if groups.setdefault(scaffold, int(fold)) != int(fold):
            raise ValueError("scaffold leakage")
        members.append({"activity_id": aid, "id": cid, "smiles": row["canonical_smiles"],
                        "scaffold": scaffold, "fold": int(fold)})
    if len(members) != manifest["n"]:
        raise ValueError("incomplete development membership")
    if dict(Counter(str(r["fold"]) for r in members)) != manifest["fold_counts"]:
        raise ValueError("frozen fold counts mismatch")
    if sorted(members, key=lambda r: r["activity_id"]) != manifest["members"]:
        raise ValueError("exact frozen membership or assignment mismatch")
    if p.assignment_digest(members) != manifest["assignments_sha256"]:
        raise ValueError("assignment digest mismatch")
    return {r["activity_id"]: r for r in members}


def endpoint(row, policy):
    # Called only after all membership/identity checks. Never echo outcome strings.
    for field in ("relation", "standard_relation"):
        if row[field].strip() != policy["original_relation" if field == "relation" else field]:
            raise ValueError("endpoint qualifier mismatch or censored relation")
    if row["units"].strip() != policy["original_units"] or row["standard_units"].strip() != policy["standard_units"]:
        raise ValueError("endpoint units mismatch")
    try:
        original, standard = Decimal(row["value"].strip()), Decimal(row["standard_value"].strip())
    except InvalidOperation:
        raise ValueError("missing or nonnumeric endpoint") from None
    if not original.is_finite() or not standard.is_finite():
        raise ValueError("nonfinite endpoint")
    if original * Decimal(str(policy["numerical_conversion_factor"])) != standard:
        raise ValueError("original and standard endpoint mismatch")
    low, high = policy["range_exclusive"]
    if not Decimal(low) < standard < Decimal(high):
        raise ValueError("endpoint outside strict interior")
    return float(standard)


def source_records(data, members, manifest):
    required = {"activity_id", "molecule_chembl_id", "assay_chembl_id", "canonical_smiles_rdkit",
                "value", "standard_value", "relation", "standard_relation", "units", "standard_units"}
    hold_a, hold_c = set(manifest["protected_activity_ids"]), set(manifest["protected_compound_ids"])
    allowed_c = {r["id"] for r in members.values()}
    records, seen = [], set()
    from .harness import scaffold_key
    for row in csv_rows(data, required):
        aid, cid = row["activity_id"], row["molecule_chembl_id"]
        candidate = aid in members or cid in allowed_c
        if candidate and (aid in hold_a or cid in hold_c):
            raise PermissionError("holdout activity or compound collision before outcomes")
        if not candidate:
            continue
        if aid not in members or cid != members[aid]["id"]:
            raise ValueError("activity and compound ID mismatch")
        if aid in seen:
            raise ValueError("duplicate source observation")
        seen.add(aid)
        member = members[aid]
        if row["assay_chembl_id"] != manifest["assay"]:
            raise ValueError("source assay identity mismatch")
        if canonical_identity(row["canonical_smiles_rdkit"]) != canonical_identity(member["smiles"]):
            raise ValueError("full molecular identity mismatch")
        if scaffold_key(row["canonical_smiles_rdkit"]) != member["scaffold"]:
            raise ValueError("source scaffold mismatch")
        value = endpoint(row, manifest["endpoint"])
        records.append({**member, "partition": "cv", "relation": None, "clint": value})
    if seen != set(members):
        raise ValueError("missing source observations")
    return sorted(records, key=lambda r: r["id"])


def prepare_bytes(partition_data, source_data, manifest):
    """Shared parser. Not a production trust boundary; accepts fixture contracts."""
    if p.sha256(partition_data) != manifest["partition"]["sha256"]:
        raise ValueError("partition SHA-256 mismatch")
    source = manifest["sources"][manifest["assay"]]
    if p.sha256(source_data) != source["sha256"]:
        raise ValueError("source SHA-256 mismatch")
    required = {"activity_id", "chembl_id", "canonical_smiles", "scaffold_key", "status", "partition", "cv_fold"}
    members = partition_members(list(csv_rows(partition_data, required)), manifest)
    records = source_records(source_data, members, manifest)
    from .harness import TARGET
    assignments = {r["id"]: [r["scaffold"], r["fold"]] for r in records}
    return {"records": records, "provenance": {
        "kind": manifest["kind"], "records_sha256": p.digest(records),
        "assignments": assignments, "id_scaffold_fold_sha256": p.digest(assignments),
        "target": TARGET, "representation_policy": "V2_R1_12_R2_2048_NOCHIRAL"}}


def write_export(destination, bundle, manifest, approval_reference):
    """Exclusive preparation directory; no success receipt for partial writes."""
    dest = Path(destination).resolve()
    if dest.is_relative_to(p.REPO / p.HISTORICAL):
        raise PermissionError("cannot write historical scientific subtree")
    dest.mkdir(parents=True, exist_ok=False)
    data = p.encoded(bundle)
    with (dest / "export.json").open("xb") as fh:
        fh.write(data)
    receipt = {"schema_version": 1, "kind": manifest["kind"], "hash_verification": "VERIFIED",
               "export_sha256": p.sha256(data), "input_manifest_canonical_sha256": p.digest(manifest),
               "partition_file_sha256": manifest["partition"]["sha256"],
               "source_file_sha256": {manifest["assay"]: manifest["sources"][manifest["assay"]]["sha256"]},
               "assignments_sha256": manifest["assignments_sha256"],
               "revisions": manifest.get("revisions", {}), "preparation_code": p.code_state(),
               "runtime": p.runtime(), "approval_reference": approval_reference,
               "endpoint_equivalence": "CHECKED_EXACT_DECIMAL_AFTER_UNIT_CONVERSION",
               "boundary": "mixed CSV strings materialised in preparation; only development outcomes exported"}
    with (dest / "receipt.json").open("xb") as fh:
        fh.write(p.encoded(receipt))
    return receipt


def extract(repo_root, *, approve_preparation=False, approval_reference=None,
            destination=None, skip_hash_verification=False):
    """Real Stage A. Approval is procedural, never inferred from a hash match."""
    if skip_hash_verification:
        raise PermissionError("skipped verification prohibited")
    if approve_preparation is not True or not approval_reference or destination is None:
        raise PermissionError("separate preparation approval, reference and destination required")
    root = Path(repo_root).resolve()
    dest = Path(destination).resolve()
    if dest.is_relative_to(root / p.HISTORICAL):
        raise PermissionError("cannot write historical scientific subtree")
    manifest = p.input_manifest()
    p.verify_authorities(root, manifest)
    partition_data = p.checked_bytes(root / p.HISTORICAL / manifest["partition"]["path"], manifest["partition"]["sha256"])
    # Establish exclusion/membership before even opening the mixed outcome source.
    partition_members(list(csv_rows(partition_data, {"activity_id", "chembl_id", "canonical_smiles", "scaffold_key", "status", "partition", "cv_fold"})), manifest)
    source = manifest["sources"][manifest["assay"]]
    source_data = p.checked_bytes(root / p.HISTORICAL / source["path"], source["sha256"])
    bundle = prepare_bytes(partition_data, source_data, manifest)
    write_export(dest, bundle, manifest, approval_reference)
    return bundle
