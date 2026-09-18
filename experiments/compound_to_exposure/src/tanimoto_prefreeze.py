"""Structural-only check of saved candidate assignments; never read target files.

Outputs are report artifacts, not a changed partition or modelling feature cache.
"""
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from rdkit import Chem, DataStructs, rdBase
from rdkit.Chem import rdMolDescriptors

ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENTS = ROOT / "reports/SCAFFOLD_PREFREEZE_DRY_RUN_ASSIGNMENTS.csv"
EXPECTED_ASSIGNMENT_SHA256 = "96bf97e5500b108c40883c13e3fc4b87c49b49c61b22357ec89cbfcec41d7a2e"
SAP = ROOT / "docs/STATISTICAL_ANALYSIS_PREREGISTRATION.md"
BIN_EDGES = (0.0, 0.2, 0.3, 0.4, 0.6, 1.0)
BIN_LABELS = ("[0,0.2)", "[0.2,0.3)", "[0.3,0.4)", "[0.4,0.6)", "[0.6,1.0]")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bin_index(value):
    if not np.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("Invalid similarity")
    for i in range(5):
        if value < BIN_EDGES[i + 1] or (i == 4 and value == 1):
            return i
    raise AssertionError("Unclassified similarity")


def summarize(values):
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        raise ValueError("Empty query set")
    bins = Counter(bin_index(float(v)) for v in values)
    q1, median, q3 = np.quantile(values, [0.25, 0.5, 0.75], method="linear")
    return {"n": len(values), "min": float(values.min()), "q1": float(q1),
            "median": float(median), "q3": float(q3), "max": float(values.max()),
            "mean": float(values.mean()), "exactly_one_n": int(np.sum(values == 1.0)),
            "bins": [{"bin": label, "count": bins[i], "fraction": bins[i] / len(values)}
                     for i, label in enumerate(BIN_LABELS)]}


def load_membership():
    if sha(ASSIGNMENTS) != EXPECTED_ASSIGNMENT_SHA256:
        raise ValueError("Candidate partition differs from the inspected evidence artifact")
    with ASSIGNMENTS.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert set(reader.fieldnames) == {"activity_id", "molecule_chembl_id", "canonical_smiles_rdkit",
                                          "scaffold_key", "status", "dry_run_partition", "dry_run_cv_fold"}
        all_rows = list(reader)
    assert len(all_rows) == 1102
    # Consume saved cohort membership only. No relation/value fields are loaded.
    rows = [r for r in all_rows if r["status"] == "INTERIOR_OBSERVED"]
    assert len(rows) == 731
    for field in ("activity_id", "molecule_chembl_id", "canonical_smiles_rdkit"):
        assert len({r[field] for r in rows}) == len(rows), field
    holdout = [r for r in rows if r["dry_run_partition"] == "holdout"]
    cv = [r for r in rows if r["dry_run_partition"] == "cv"]
    assert len(holdout) == 149 and len(cv) == 582
    assert all(r["dry_run_cv_fold"] == "" for r in holdout)
    assert Counter(r["dry_run_cv_fold"] for r in cv) == dict(zip(map(str, range(5)), [115, 120, 115, 117, 115]))
    groups = defaultdict(set)
    for r in all_rows:
        groups[r["scaffold_key"]].add((r["dry_run_partition"], r["dry_run_cv_fold"]))
    assert all(len(partitions) == 1 for partitions in groups.values())
    assert not ({r["scaffold_key"] for r in holdout} & {r["scaffold_key"] for r in cv})
    return sorted(holdout, key=lambda r: int(r["activity_id"])), sorted(cv, key=lambda r: int(r["activity_id"]))


def fingerprints(rows):
    result = {}
    for row in rows:
        mol = Chem.MolFromSmiles(row["canonical_smiles_rdkit"])
        if mol is None:
            raise ValueError(f"Unparseable structure: {row['activity_id']}")
        # Use the SAP's exact legacy entry point. Suppress its deprecation log only
        # during fingerprint construction; failed parsing above remains fatal.
        with rdBase.BlockLogs():
            fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(
                mol, radius=2, nBits=2048, useChirality=False,
                useBondTypes=True, useFeatures=False, includeRedundantEnvironments=False)
        assert fp.GetNumBits() == 2048 and fp.GetNumOnBits() > 0
        result[row["activity_id"]] = fp
    return result


def reference_pool(query, cv):
    if query["dry_run_partition"] == "holdout":
        return cv
    if query["dry_run_partition"] != "cv":
        raise ValueError("Unexpected partition")
    return [r for r in cv if r["dry_run_cv_fold"] != query["dry_run_cv_fold"]]


def calculate(queries, cv, fps):
    records, exact_pairs = [], []
    bitsets = {key: frozenset(fp.GetOnBits()) for key, fp in fps.items()}
    for query in queries:
        refs = reference_pool(query, cv)
        assert refs and all(r["activity_id"] != query["activity_id"] for r in refs)
        assert all(r["scaffold_key"] != query["scaffold_key"] for r in refs)
        values = DataStructs.BulkTanimotoSimilarity(fps[query["activity_id"]], [fps[r["activity_id"]] for r in refs])
        # Independently verify every candidate score by binary set intersection/union.
        query_bits = bitsets[query["activity_id"]]
        manual = [len(query_bits & bitsets[r["activity_id"]]) / len(query_bits | bitsets[r["activity_id"]]) for r in refs]
        assert np.allclose(values, manual, rtol=0, atol=1e-15)
        maximum = max(values)
        neighbours = [r for r, v in zip(refs, values) if v == maximum]
        assert {r["activity_id"] for r in neighbours} == {r["activity_id"] for r, v in zip(refs, manual) if v == max(manual)}
        scope = "holdout_to_cv" if query["dry_run_partition"] == "holdout" else "cv_to_other_cv_folds"
        record = {"scope": scope, "activity_id": query["activity_id"],
                  "molecule_chembl_id": query["molecule_chembl_id"], "scaffold_key": query["scaffold_key"],
                  "cv_fold": int(query["dry_run_cv_fold"]) if query["dry_run_cv_fold"] else None,
                  "reference_n": len(refs), "maximum_tanimoto": maximum, "bin": BIN_LABELS[bin_index(maximum)],
                  "nearest_tie_count": len(neighbours),
                  "nearest_activity_ids": [r["activity_id"] for r in neighbours],
                  "nearest_molecule_ids": [r["molecule_chembl_id"] for r in neighbours],
                  "nearest_scaffold_keys": [r["scaffold_key"] for r in neighbours]}
        records.append(record)
        if maximum == 1:
            for ref in neighbours:
                assert bitsets[ref["activity_id"]] == query_bits
                exact_pairs.append({"scope": scope, "query_activity_id": query["activity_id"],
                                    "query_molecule_id": query["molecule_chembl_id"], "query_scaffold_key": query["scaffold_key"],
                                    "query_smiles": query["canonical_smiles_rdkit"],
                                    "reference_activity_id": ref["activity_id"], "reference_molecule_id": ref["molecule_chembl_id"],
                                    "reference_scaffold_key": ref["scaffold_key"], "reference_smiles": ref["canonical_smiles_rdkit"],
                                    "same_frozen_scaffold": False, "identical_bit_vectors": True,
                                    "on_bits": len(query_bits)})
    return records, exact_pairs


def csv_bytes(records):
    out = io.StringIO(newline="")
    fields = list(records[0])
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in records:
        writer.writerow({k: json.dumps(v, separators=(",", ":")) if isinstance(v, list) else v for k, v in row.items()})
    return out.getvalue().encode("utf-8")


def markdown(result):
    h, c = result["holdout_summary"], result["cv_oof_summary"]
    text = f"""# ECFP4/Tanimoto pre-freeze split characterisation

Completed {result['completed_utc']}. This is a structural similarity calculation, not model performance. The existing candidate partition and SAP are unchanged. No numerical target values, raw activity records, model predictions, residuals or v1 performance files were opened.

## Input and method

The sole molecular-data input is `SCAFFOLD_PREFREEZE_DRY_RUN_ASSIGNMENTS.csv`. It contains identities, canonical SMILES, frozen scaffold keys, previously assigned cohort statuses and candidate partition/fold membership, but no numerical target fields. The saved INTERIOR_OBSERVED membership selects 731 compounds without re-deriving the cohort or partition.

RDKit **{result['rdkit_version']}**; NumPy **{result['numpy_version']}**. Fingerprints use the SAP's `GetMorganFingerprintAsBitVect`: Morgan/ECFP4, **radius 2, 2048 bits, binary, useChirality=False**. Other legacy defaults are preserved explicitly: `useBondTypes=True`, `useFeatures=False`, `includeRedundantEnvironments=False`; default atom invariants, all atoms, no atom filtering. Fingerprints are computed on the supplied complete canonical structures without new standardisation, fragment selection or chirality-aware encoding. Frozen scaffold keys are consumed as saved, not regenerated.

For each of the **149 primary holdout compounds**, the reference pool is all **582 primary CV compounds**. For each CV observation, the reference pool contains only primary CV observations in the other four frozen folds; the holdout and its own fold are excluded. Every candidate-pair RDKit similarity was independently checked by intersection/union of the on-bit sets, including maximum values and all nearest-neighbour ties.

Quartiles use NumPy `quantile(method="linear")`: linear interpolation at sorted index (N−1)p for p=0.25,0.5,0.75. Fractions use each section's query N. Bins have inclusive lower/exclusive upper edges, except the final upper edge 1.0 is inclusive. Summaries below are descriptive, not decision thresholds.

## Holdout nearest-CV distribution

| Statistic | Value |
|---|---:|
"""
    for label, key in [("N", "n"), ("Minimum", "min"), ("Q1", "q1"), ("Median", "median"), ("Q3", "q3"), ("Maximum", "max"), ("Mean", "mean"), ("Maximum similarity exactly 1.0: query count", "exactly_one_n")]:
        text += f"| {label} | {h[key]} |\n"
    text += "\n| Preregistered bin | Count | Fraction |\n|---|---:|---:|\n"
    for b in h["bins"]:
        text += f"| {b['bin']} | {b['count']} | {b['fraction']} |\n"
    text += "\nBins with fewer than 20 observations remain descriptive counts under the SAP's existing rule. No residual, accuracy comparison or inference is performed.\n"
    text += "\n## Exact-1.0 pairs\n\n"
    exact = result["exact_one_pairs"]
    holdout_pairs = [p for p in exact if p["scope"] == "holdout_to_cv"]
    text += f"Holdout: **{h['exactly_one_n']} queries**, **{len(holdout_pairs)} query/reference pairs** at exactly 1.0. CV: **{c['exactly_one_n']} queries** at exactly 1.0 against an eligible other-fold reference. CV pairs are directed because each CV observation is a query.\n\n"
    if exact:
        text += "| Scope | Query molecule / activity | Query frozen scaffold | Reference molecule / activity | Reference frozen scaffold |\n|---|---|---|---|---|\n"
        for p in exact:
            text += f"| {p['scope']} | {p['query_molecule_id']} / {p['query_activity_id']} | `{p['query_scaffold_key']}` | {p['reference_molecule_id']} / {p['reference_activity_id']} | `{p['reference_scaffold_key']}` |\n"
        text += "\nAn exact 1.0 here means identical finite binary fingerprints. It does not imply identical molecular structures or frozen Murcko scaffolds. All listed pairs have distinct frozen scaffold keys.\n"
    else:
        text += "There are no exact-1.0 pairs to enumerate in either eligible comparison scope.\n"
    text += "\n## CV nearest-other-fold executability check\n\n| Query fold | Query N | Eligible reference N per query | Queries with a defined maximum |\n|---:|---:|---:|---:|\n"
    for row in result["cv_folds"]:
        text += f"| {row['fold']} | {row['n']} | {row['reference_n']} | {row['n']} |\n"
    text += f"\nAll **{c['n']}** CV observations have a finite maximum using only the other four CV folds. There is no self-match, same-fold reference or holdout reference. Aggregate CV minimum/Q1/median/Q3/maximum/mean are **{c['min']} / {c['q1']} / {c['median']} / {c['q3']} / {c['max']} / {c['mean']}**.\n"
    text += "\n| Preregistered bin | CV count | CV fraction |\n|---|---:|---:|\n"
    for b in c["bins"]:
        text += f"| {b['bin']} | {b['count']} | {b['fraction']} |\n"
    text += f"""
## Scaffold separation and SAP consistency

**No holdout/CV pair shares a frozen Bemis–Murcko scaffold.** The primary holdout and CV scaffold-key sets have an empty intersection, and every scored pair has different keys. No frozen scaffold crosses CV folds either. All 1,102 saved assignments also retain one partition/fold per scaffold group. Primary membership remains 149 holdout and 582 CV, with CV fold Ns 115/120/115/117/115.

**Factual contradiction with the SAP's split/fingerprint specification: none detected.** Scaffold-key separation does not promise uniformly low fingerprint similarity; the distribution is reported without changing the partition, introducing a cutoff or choosing methods. The requested nearest-training calculation is executable for all 731 primary observations with the frozen reference-pool rules.

The two holdout queries with exact-1.0 matches are indistinguishable from their respective CV neighbours in this frozen binary fingerprint, despite distinct molecular structures and scaffold keys. Thus this check does not support a stronger claim that every holdout observation is novel in the fingerprint representation. Identical bits alone do not distinguish finite-radius representation equivalence from bit-folding collisions; no alternative fingerprint was computed to investigate that mechanism. This is a structural-separation limitation, not a changed partition or a performance result.

The SAP's statement that this characterisation has not yet been performed is now superseded by this completion evidence. The SAP itself remains unchanged, including its pending status. This report does not freeze the protocol, create a tag or authorize model execution.

## Reproduction and artifacts

- Assignment CSV SHA-256: `{result['input_sha256']['assignment_csv']}`.
- SAP snapshot SHA-256: `{result['input_sha256']['sap']}`.
- Audit script SHA-256: `{result['code_sha256']}`.
- Input hashes before/after: identical. No partition, SAP or raw file was written.
- [Machine-readable JSON](ECFP4_TANIMOTO_PREFREEZE_CHECK.json): both distributions, all 731 per-query results, all nearest-neighbour ties, exact-1.0 pair identities/scaffolds, fold reference counts and verification flags.
- [Per-query CSV](ECFP4_TANIMOTO_PREFREEZE_CHECK.csv): 149 holdout rows plus 582 CV rows, distinguished by `scope`; array-valued nearest-neighbour fields use JSON encoding.
- Reproduce with `.venv/Scripts/python.exe src/tanimoto_prefreeze.py` from the experiment directory. This script reads only the saved structural assignment CSV and the SAP text; it does not import the raw-data audit or modelling runners. It hashes the saved group CSV without parsing its contents.

TANIMOTO_PREFREEZE_CHECK_COMPLETE
"""
    return text


def main():
    assert rdBase.rdkitVersion == "2025.03.6"
    protected = {"assignment_csv": ASSIGNMENTS, "sap": SAP,
                 "group_csv": ROOT / "reports/SCAFFOLD_PREFREEZE_GROUPS.csv"}
    before = {k: sha(v) for k, v in protected.items()}
    # Reading protocol text is allowed; no target value records are loaded.
    sap_text = SAP.read_text(encoding="utf-8")
    assert "radius=2, nBits=2048, useChirality=False" in sap_text
    holdout, cv = load_membership()
    fps = fingerprints(holdout + cv)
    h_records, h_pairs = calculate(holdout, cv, fps)
    c_records, c_pairs = calculate(cv, cv, fps)
    result = {"completed_utc": datetime.now(timezone.utc).isoformat(),
              "rdkit_version": rdBase.rdkitVersion, "numpy_version": np.__version__,
              "input_sha256": before, "code_sha256": sha(__file__),
              "fingerprint": {"radius": 2, "n_bits": 2048, "binary": True, "useChirality": False,
                              "useBondTypes": True, "useFeatures": False, "includeRedundantEnvironments": False},
              "quantile_method": "linear, sorted index (N-1)*p", "bin_labels": BIN_LABELS,
              "holdout_summary": summarize([r["maximum_tanimoto"] for r in h_records]),
              "cv_oof_summary": summarize([r["maximum_tanimoto"] for r in c_records]),
              "cv_folds": [{"fold": f, "n": sum(r["cv_fold"] == f for r in c_records),
                            "reference_n": 582 - sum(r["cv_fold"] == f for r in c_records)} for f in range(5)],
              "verification": {"holdout_cv_shared_scaffolds": 0, "cross_fold_shared_scaffolds": 0,
                               "all_scores_checked_by_bitset_intersection_union": True,
                               "numerical_targets_read": False, "models_or_residuals_computed": False,
                               "partition_changed": False, "sap_changed": False,
                               "factual_split_or_fingerprint_contradiction": False},
              "exact_one_pairs": h_pairs + c_pairs, "observations": h_records + c_records}
    assert sum(r["reference_n"] for r in h_records) == 149 * 582
    assert all(r["reference_n"] == 582 for r in h_records)
    for row in c_records:
        assert row["reference_n"] == result["cv_folds"][row["cv_fold"]]["reference_n"]
    assert before == {k: sha(v) for k, v in protected.items()}
    outputs = {"ECFP4_TANIMOTO_PREFREEZE_CHECK.json": (json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(),
               "ECFP4_TANIMOTO_PREFREEZE_CHECK.csv": csv_bytes(result["observations"]),
               "ECFP4_TANIMOTO_PREFREEZE_CHECK.md": markdown(result).encode("utf-8")}
    for name, data in outputs.items():
        (ROOT / "reports" / name).write_bytes(data)
    assert before == {k: sha(v) for k, v in protected.items()}
    print(json.dumps({"holdout_summary": result["holdout_summary"], "cv_oof_summary": result["cv_oof_summary"],
                      "exact_one_pairs": result["exact_one_pairs"], "verification": result["verification"]}, indent=2))


if __name__ == "__main__":
    main()
