"""Offline pre-freeze evidence only; outputs stay in reports/, never splits/.

No predictive representations, fitted estimators, metrics, or benchmark execution.
Run from the experiment: .venv/Scripts/python.exe src/prefreeze_evidence.py
"""
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from decimal import Decimal

from rdkit import Chem, rdBase
from rdkit.Chem.Scaffolds import MurckoScaffold

from chembl_pages import validate_pages
from provenance import ROOT, digest, verify

STATUSES = ("INTERIOR_OBSERVED", "BOUNDARY_AMBIGUOUS", "LEFT_CENSORED", "RIGHT_CENSORED")
SAP = ROOT / "docs/STATISTICAL_ANALYSIS_PREREGISTRATION.md"


def status(row):
    """Fail closed on discordant fields or an unclassified numeric observation."""
    raw, standard = row["relation"], row["standard_relation"]
    value = Decimal(str(row["standard_value"]))
    if not value.is_finite() or Decimal(str(row["value"])) != value or raw != standard:
        raise ValueError("Discordant relation/value fields")
    if raw is None:
        if Decimal(3) < value < Decimal(150):
            return STATUSES[0]
        if value in (Decimal(3), Decimal(150)):
            return STATUSES[1]
    elif raw == "<" and value == 3:
        return STATUSES[2]
    elif raw == ">" and value == 150:
        return STATUSES[3]
    raise ValueError("Record does not satisfy any frozen status definition")


def parse(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Unparseable deposited structure")
    return mol


def scaffold(smiles):
    # Fragment selection is solely for grouping; full-molecule identity is separate.
    fragments = Chem.GetMolFrags(parse(smiles), asMols=True)
    chosen = min(fragments, key=lambda m: (-m.GetNumHeavyAtoms(), Chem.MolToSmiles(m)))
    return MurckoScaffold.MurckoScaffoldSmiles(mol=chosen, includeChirality=False) or "__ACYCLIC__"


def hash_order(key):
    return int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:8], 16), key


def dry_run(all_counts, primary_counts, size_basis="primary"):
    """SAP B5: count cohort membership only; never optimize target magnitudes.

    Compare integers to the exact 1/5 budget to avoid rounding 146.2 down to 146.
    The alternative total-row oversized test is a textual-ambiguity diagnostic.
    """
    primary_n = sum(primary_counts.values())
    sizes = primary_counts if size_basis == "primary" else all_counts
    holdout_n, assignments, cv = 0, {}, []
    for key in sorted(all_counts, key=hash_order):
        if holdout_n * 5 < primary_n and sizes.get(key, 0) * 5 <= primary_n:
            assignments[key] = ("holdout", None)
            holdout_n += primary_counts.get(key, 0)
        else:
            cv.append(key)
    fold_ns = [0] * 5
    for key in cv:
        fold = min(range(5), key=lambda i: (fold_ns[i], i))
        assignments[key] = ("cv", fold)
        fold_ns[fold] += primary_counts.get(key, 0)
    return assignments, fold_ns


def read_assay(assay):
    paths = sorted((ROOT / "data/raw/chembl").glob(f"{assay}_activities_*.json"))
    pages = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    validate_pages(pages, assay)
    rows = []
    for path, page in zip(paths, pages):
        for i, row in enumerate(page["activities"], 1):
            rows.append({**row, "raw_filename": path.relative_to(ROOT).as_posix(),
                         "row_in_page_1based": i, "status": status(row),
                         "canonical_smiles_rdkit": Chem.MolToSmiles(parse(row["canonical_smiles"]))})
    return rows


def unique_index(rows, field):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row[field]].append(row)
    if any(len(v) != 1 for v in grouped.values()):
        raise ValueError(f"Nonunique assay {field}")
    return {k: v[0] for k, v in grouped.items()}


def pair_evidence(hlm, hh):
    hi, ci = [unique_index(rows, "molecule_chembl_id") for rows in (hlm, hh)]
    hs, cs = [unique_index(rows, "canonical_smiles_rdkit") for rows in (hlm, hh)]
    ids, structures = sorted(hi.keys() & ci.keys()), sorted(hs.keys() & cs.keys())
    by_id = {(hi[k]["activity_id"], ci[k]["activity_id"]) for k in ids}
    by_structure = {(hs[k]["activity_id"], cs[k]["activity_id"]) for k in structures}
    assert by_id == by_structure and len(by_id) == 187
    with (ROOT / "data/interim/PAIRED_HUMAN_COHORT.csv").open(encoding="utf-8", newline="") as handle:
        frozen = list(csv.DictReader(handle))
    frozen_triples = set()
    for row in frozen:
        hids, cids = json.loads(row["hlm_activity_ids"]), json.loads(row["hh_activity_ids"])
        assert len(hids) == len(cids) == 1
        frozen_triples.add((hids[0], cids[0], row["canonical_smiles_rdkit"]))
    assert len(frozen) == 187
    assert frozen_triples == {(hi[k]["activity_id"], ci[k]["activity_id"], hi[k]["canonical_smiles_rdkit"]) for k in ids}
    fields = ("activity_id", "assay_chembl_id", "molecule_chembl_id", "relation", "value", "units",
              "standard_relation", "standard_value", "standard_units", "status", "raw_filename", "row_in_page_1based")
    pairs = [{"molecule_chembl_id": k, "canonical_smiles_rdkit": hi[k]["canonical_smiles_rdkit"],
              "HLM": {f: hi[k][f] for f in fields}, "HH": {f: ci[k][f] for f in fields}} for k in ids]
    cells = Counter((p["HLM"]["status"], p["HH"]["status"]) for p in pairs)
    matrix = [[cells[a, b] for b in STATUSES] for a in STATUSES]
    interior, ambiguous, left, right = STATUSES
    counts = {"total_pairs": len(pairs), "both_interior": cells[interior, interior],
              "hlm_interior_hh_left": cells[interior, left], "hlm_interior_hh_right": cells[interior, right],
              "hlm_left_hh_interior": cells[left, interior], "hlm_right_hh_interior": cells[right, interior],
              "one_interior_one_censored": sum(cells[a, b] for a, b in cells if (a == interior and b in (left, right)) or (b == interior and a in (left, right))),
              "both_censored": sum(cells[a, b] for a in (left, right) for b in (left, right)),
              "any_boundary_ambiguous": sum(cells[a, b] for a, b in cells if ambiguous in (a, b)),
              "null_at_150_full_hlm": sum(r["relation"] is None and Decimal(r["standard_value"]) == 150 for r in hlm),
              "null_at_150_full_hh": sum(r["relation"] is None and Decimal(r["standard_value"]) == 150 for r in hh),
              "primary_spearman_eligible_n": cells[interior, interior],
              "exact_boundary_sensitivity_spearman_eligible_n": sum(cells[a, b] for a in (interior, ambiguous) for b in (interior, ambiguous))}
    assert matrix == [[94, 0, 26, 5], [2, 0, 0, 0], [20, 0, 31, 0], [8, 0, 0, 1]]
    assert counts["null_at_150_full_hlm"] == counts["null_at_150_full_hh"] == 0
    return {"status_order": STATUSES, "matrix_hlm_rows_hh_columns": matrix, "counts": counts,
            "matching": {"molecule_id_pairs": 187, "canonical_structure_pairs": 187,
                         "same_one_to_one_activity_pairs": True, "matches_frozen_membership": True},
            "boundary_ambiguous_pairs": [p for p in pairs if ambiguous in (p["HLM"]["status"], p["HH"]["status"])],
            "pairs": pairs}


def group_stats(counts):
    counts = {k: n for k, n in counts.items() if n}
    n, singletons = sum(counts.values()), sum(v == 1 for v in counts.values())
    return {"n": n, "unique_groups": len(counts), "singleton_groups": singletons,
            "singleton_group_fraction": singletons / len(counts), "compounds_in_singleton_groups": singletons,
            "acyclic_n": counts.get("__ACYCLIC__", 0), "acyclic_compound_fraction": counts.get("__ACYCLIC__", 0) / n,
            "largest_20": [{"scaffold_key": k, "n": v} for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:20]]}


def scaffold_evidence(rows):
    all_counts, primary = Counter(), Counter()
    keyed = [(r, scaffold(r["canonical_smiles"])) for r in rows]
    for row, key in keyed:
        all_counts[key] += 1
        if row["status"] == STATUSES[0]:
            primary[key] += 1
    assert sum(all_counts.values()) == 1102 and sum(primary.values()) == 731
    assignments, folds = dry_run(all_counts, primary)
    alternative, _ = dry_run(all_counts, primary, "all")
    details = [{"activity_id": r["activity_id"], "molecule_chembl_id": r["molecule_chembl_id"],
                "canonical_smiles_rdkit": r["canonical_smiles_rdkit"], "scaffold_key": k,
                "status": r["status"], "dry_run_partition": assignments[k][0], "dry_run_cv_fold": assignments[k][1]}
               for r, k in sorted(keyed, key=lambda x: x[0]["activity_id"])]
    group_rows = [{"scaffold_key": k, "hash_prefix_32bit": hash_order(k)[0], "hash_order_1based": i,
                   "all_n": all_counts[k], "primary_n": primary[k],
                   "dry_run_partition": assignments[k][0], "dry_run_cv_fold": assignments[k][1]}
                  for i, k in enumerate(sorted(all_counts, key=hash_order), 1)]
    holdout = [k for k in assignments if assignments[k][0] == "holdout"]
    per_group = defaultdict(set)
    for row in details:
        per_group[row["scaffold_key"]].add((row["dry_run_partition"], row["dry_run_cv_fold"]))
    n_holdout = sum(primary[k] for k in holdout)
    return {"all_1102": group_stats(all_counts), "primary_731": group_stats(primary),
            "multicomponent_hlm_records": sum(len(Chem.GetMolFrags(parse(r["canonical_smiles"]))) > 1 for r in rows),
            "dry_run": {"primary_holdout_n": n_holdout, "primary_holdout_fraction": n_holdout / 731,
                        "all_holdout_n": sum(all_counts[k] for k in holdout), "holdout_groups_all": len(holdout),
                        "holdout_groups_with_primary_records": sum(primary[k] > 0 for k in holdout),
                        "primary_cv_pool_n": 731 - n_holdout, "all_cv_pool_n": 1102 - sum(all_counts[k] for k in holdout),
                        "inner_fold_primary_ns": folds,
                        "inner_fold_all_ns": [sum(all_counts[k] for k in assignments if assignments[k] == ("cv", j)) for j in range(5)],
                        "groups_crossing_partitions_or_folds": sum(len(v) > 1 for v in per_group.values()),
                        "oversized_groups_primary_basis": sum(n * 5 > 731 for n in primary.values()),
                        "oversized_groups_all_basis": sum(n * 5 > 731 for n in all_counts.values()),
                        "size_basis_alternative_assignments_identical": assignments == alternative,
                        "acyclic_exceeds_20_percent_primary": primary["__ACYCLIC__"] * 5 > 731,
                        "acyclic_necessarily_excluded_by_oversized_rule": primary["__ACYCLIC__"] * 5 > 731,
                        "acyclic_assignment": assignments["__ACYCLIC__"], "sap_procedural_steps_reproduced": True},
            "groups": group_rows, "assignments_evidence_only": details}


def csv_text(rows, columns=None):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=columns or list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def write_report(name, text):
    # Deliberately no configurable output directory and no modelling split artifact.
    (ROOT / "reports" / name).write_bytes(text.encode("utf-8"))


def markdown_reports(pairs, groups, evidence):
    matrix = pairs["matrix_hlm_rows_hh_columns"]
    table = "| HLM \\ HH | " + " | ".join(STATUSES) + " | Total |\n"
    table += "|---|---:|---:|---:|---:|---:|\n"
    for label, values in zip(STATUSES, matrix):
        table += "| " + label + " | " + " | ".join(map(str, values + [sum(values)])) + " |\n"
    table += "| Total | " + " | ".join(str(sum(row[j] for row in matrix)) for j in range(4)) + " | 187 |\n"
    boundary = "| Molecule | HLM activity | HLM value | HH activity | HH value |\n|---|---:|---:|---:|---:|\n"
    for p in pairs["boundary_ambiguous_pairs"]:
        boundary += f'| {p["molecule_chembl_id"]} | {p["HLM"]["activity_id"]} | {p["HLM"]["standard_value"]} | {p["HH"]["activity_id"]} | {p["HH"]["standard_value"]} |\n'
    write_report("HLM_HH_QUALIFIER_CROSSTAB.md", f"""# HLM–HH qualifier cross-tabulation: final verification

OBSERVED, 2026-09-18. Independently regenerated from the immutable downloaded ChEMBL 37 activity pages for CHEMBL3301370 (HLM) and CHEMBL3301372 (human hepatocyte; HH). Pagination totals/unique activity IDs, raw SHA-256 and byte sizes pass validation. Both relation fields and both numerical value fields agree for every record in these assays; NULL remains NULL.

Classification uses exact decimal comparisons: INTERIOR_OBSERVED requires both relations NULL and 3 < standard_value < 150; BOUNDARY_AMBIGUOUS requires both NULL and standard_value exactly 3 or 150; LEFT_CENSORED requires both relations `<` and reported bound 3; RIGHT_CENSORED requires both `>` and reported bound 150. The latter two labels describe qualifiers, not exact continuous observations. No other status occurs.

{table}
OBSERVED: the provisional 94 / 59 / 32 / 2 summary is confirmed. Of the 59 interior/censored pairs, 31 have interior HLM (26 HH-left, 5 HH-right), and 28 have interior HH (20 HLM-left, 8 HLM-right). The 32 doubly censored pairs comprise 31 left/left and one right/right; opposite-tail cells are zero.

## Every boundary-ambiguous pair

{boundary}
All four records above have raw and standard relation NULL. Both HLM records are BOUNDARY_AMBIGUOUS at 3; both HH records are INTERIOR_OBSERVED. Values retain their native scales: HLM raw units microL/min/mg (standard units mL.min-1.g-1), HH raw units microL/min/1E6 cells (standard units uL.min-1.(10^6cells)-1). No conversion, difference or ratio was calculated. There are no paired NULL-at-150 records and no NULL-at-150 records in either full assay. The HH assay has no NULL-at-3 records either.

OBSERVED: **94 pairs** qualify for the primary ordinary quantitative Spearman calculation. **96 pairs** qualify only under the specified sensitivity that includes the two HLM NULL-at-3 values as exact 3. They remain boundary-ambiguous in the evidence table; sensitivity eligibility does not establish equality semantics. No correlation was computed.

OBSERVED: full-molecule canonicalization with RDKit {evidence['rdkit_version']} produces no duplicate molecule IDs or canonical structures within either assay. The molecule-ID intersection and strict canonical-structure intersection each contain the **same 187 one-to-one activity pairs**, exactly matching the frozen PAIRED_HUMAN_COHORT.csv. No salt, tautomer, stereochemistry or fragment normalization was used for this identity comparison.

Machine-readable evidence: [4×4 matrix CSV](HLM_HH_QUALIFIER_CROSSTAB.csv), [JSON with all 187 pairs, activity IDs, source pages/row locators, fields and input hashes](HLM_HH_QUALIFIER_CROSSTAB.json). Reproduction: `src/prefreeze_evidence.py`. SAP snapshot SHA-256: `{evidence['sap_sha256']}`. Raw files, frozen membership and SAP were not changed. These findings preserve the existing scientific audit conclusions.
""")
    all_s, primary_s, dry = groups["all_1102"], groups["primary_731"], groups["dry_run"]
    stats = "| Statistic | All 1,102 | Primary 731 |\n|---|---:|---:|\n"
    for label, key in [("Unique scaffold groups", "unique_groups"), ("Singleton groups", "singleton_groups"),
                       ("Fraction of groups that are singletons", "singleton_group_fraction"),
                       ("Compounds in singleton groups", "compounds_in_singleton_groups"),
                       ("__ACYCLIC__ compounds", "acyclic_n"), ("Fraction of compounds in __ACYCLIC__", "acyclic_compound_fraction")]:
        stats += f"| {label} | {all_s[key]} | {primary_s[key]} |\n"
    top = ""
    for label, data in [("All 1,102 records", all_s), ("Primary 731 records", primary_s)]:
        top += f"\n## Largest 20 scaffold groups: {label}\n\n| Rank | Atomic scaffold key | N |\n|---:|---|---:|\n"
        for i, row in enumerate(data["largest_20"], 1):
            top += f"| {i} | `{row['scaffold_key']}` | {row['n']} |\n"
    write_report("SCAFFOLD_PREFREEZE_CHECK.md", f"""# Scaffold pre-freeze characterisation

OBSERVED, 2026-09-18. RDKit {evidence['rdkit_version']}; SAP SHA-256 `{evidence['sap_sha256']}`. Immutable CHEMBL3301370 raw pages pass manifest hash/size and pagination checks. The primary cohort consists of 731 records with both relation fields NULL and 3 < standard_value < 150. Both relation fields agree throughout. This is an evidence-only dry-run; no modelling partition or fitted representation was created.

## Exact grouping and cohort statistics

Atomic `MurckoScaffoldSmiles(mol=m, includeChirality=False)`; no generic-scaffold conversion. Multicomponent grouping chooses the fragment with most heavy atoms, then the lexicographically smallest canonical SMILES on a tie. Canonical SMILES uses RDKit's default isomeric form. Empty Murcko strings map to `__ACYCLIC__`. Identity and raw structures are unchanged. One HLM record is multicomponent: activity 14759791, CHEMBL1355736 (deposited hydrate); fragment selection is for its scaffold key only.

{stats}
Singleton fractions are 81.8820% of all groups and 85.9023% of primary groups. Cohort-specific singleton counts count only members of that cohort; a primary singleton may have non-primary companions in the full 1,102. Both assays have unique structures per row, so row and compound counts coincide here.

OBSERVED: `__ACYCLIC__` contains only CHEMBL203125, activity 14758924, an interior record. It is 0.136799% of the primary cohort, **does not exceed 20%**, and is **not excluded by the oversized-group rule**. Its actual hash position places it in CV fold 3. No scaffold exceeds the holdout budget: the largest primary group has 14 members; the largest full-data group has 32. No material oversized-group or acyclic-pooling problem is observed.

## Deterministic assignment dry-run

Groups are sorted by the integer value of the first eight SHA-256 hex digits of UTF-8 scaffold key, then lexicographic key. Whole groups, including groups with zero primary members, enter the holdout until its primary count first reaches at least 731/5 = 146.2. This requires at least 147, not 146, primary records. Whole-group accumulation yields **149 / 731 = 20.3830369357%**. The rule skips groups exceeding the full budget, not groups merely exceeding the remaining budget. CV groups follow the same hash order and are assigned to the fold with fewest primary members, ties to lowest index (0–4).

| Quantity | Result |
|---|---:|
| Primary holdout N | {dry['primary_holdout_n']} |
| Primary holdout scaffold groups | {dry['holdout_groups_with_primary_records']} |
| All-record holdout N | {dry['all_holdout_n']} |
| All-record holdout scaffold groups | {dry['holdout_groups_all']} |
| Primary CV-pool N | {dry['primary_cv_pool_n']} |
| All-record CV-pool N | {dry['all_cv_pool_n']} |
| Groups crossing holdout/CV or inner folds | {dry['groups_crossing_partitions_or_folds']} |

| CV fold | Primary N | All-record N |
|---:|---:|---:|
""" + "".join(f"| {j} | {dry['inner_fold_primary_ns'][j]} | {dry['inner_fold_all_ns'][j]} |\n" for j in range(5)) + f"""
OBSERVED: all five procedural assignment steps are reproduced, with no target-magnitude balancing, tuning, fitting or second selected partition. The SAP's phrase 'group larger than the holdout budget' does not specify whether group size means primary or all records. The diagnostic checked both interpretations; they give identical assignments because neither basis has an oversized group. This ambiguity has no effect on these HLM records. The assignment depends on outcome-defined cohort membership, as the SAP explicitly acknowledges; it is not a structure-only algorithm in the strict sense.

INFERRED limitation: abundant singleton scaffold keys do not establish that held-out compounds are chemically distant from training compounds. Scaffold disjointness is verified; fingerprint dissimilarity is not. The requested scope excludes representation generation, so the SAP's additional pre-freeze nearest-training ECFP4/Tanimoto characterisation was not performed. Accepting the limitation and closing that unperformed requirement need an explicit protocol decision, not a changed split. The numerical RDKit version is recorded here but has not been inserted into the unchanged SAP.
{top}
All ties in the largest-20 lists are ordered lexicographically by scaffold key. Complete evidence: [JSON](SCAFFOLD_PREFREEZE_CHECK.json), [712 group statistics and hash-order assignments](SCAFFOLD_PREFREEZE_GROUPS.csv), [1,102 per-record dry-run assignments](SCAFFOLD_PREFREEZE_DRY_RUN_ASSIGNMENTS.csv). These report artifacts are not `splits/master_partition.csv` and do not authorize fitting. Reproduce with `src/prefreeze_evidence.py`.

PRE_FREEZE_DECISION_REQUIRED
""")


def main():
    manifest = ROOT / "manifests/source_manifest.json"
    sources = json.loads(manifest.read_text(encoding="utf-8"))["sources"]
    raw = [verify(s) for s in sources]
    protected = raw + [SAP, manifest, ROOT / "data/interim/PAIRED_HUMAN_COHORT.csv"]
    before = {p.relative_to(ROOT).as_posix(): digest(p) for p in protected}
    hlm, hh = read_assay("CHEMBL3301370"), read_assay("CHEMBL3301372")
    pairs, groups = pair_evidence(hlm, hh), scaffold_evidence(hlm)
    assert Counter(r["status"] for r in hlm) == dict(zip(STATUSES, [731, 13, 274, 84]))
    assert Counter(r["status"] for r in hh) == {STATUSES[0]: 289, STATUSES[2]: 104, STATUSES[3]: 15}
    assert before == {p.relative_to(ROOT).as_posix(): digest(p) for p in protected}
    evidence = {"scope": "Offline evidence only; no fitting, predictive representations, correlations or modelling split created.",
                "rdkit_version": rdBase.rdkitVersion, "sap_sha256": digest(SAP),
                "protected_input_sha256": before, "input_hashes_unchanged": True,
                "source_code_sha256": digest(__file__), "chembl_pagination_validation": "PASS"}
    for name, data in [("HLM_HH_QUALIFIER_CROSSTAB.json", pairs), ("SCAFFOLD_PREFREEZE_CHECK.json", groups)]:
        write_report(name, json.dumps({"evidence": evidence, **data}, indent=2, sort_keys=True, allow_nan=False) + "\n")
    matrix_rows = [{"HLM_status": a, **{b: pairs["matrix_hlm_rows_hh_columns"][i][j] for j, b in enumerate(STATUSES)}} for i, a in enumerate(STATUSES)]
    write_report("HLM_HH_QUALIFIER_CROSSTAB.csv", csv_text(matrix_rows))
    write_report("SCAFFOLD_PREFREEZE_GROUPS.csv", csv_text(groups["groups"]))
    write_report("SCAFFOLD_PREFREEZE_DRY_RUN_ASSIGNMENTS.csv", csv_text(groups["assignments_evidence_only"]))
    markdown_reports(pairs, groups, evidence)
    assert before == {p.relative_to(ROOT).as_posix(): digest(p) for p in protected}
    print(json.dumps({"pairs": pairs["counts"], "dry_run": groups["dry_run"],
                      "sap_sha256": evidence["sap_sha256"], "input_hashes_unchanged": True}, indent=2))


if __name__ == "__main__":
    main()
