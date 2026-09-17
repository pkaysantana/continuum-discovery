# Censoring metadata check — post-audit record

Date: 2026-09-17. Status of the 13 HLM null-at-3 records: **UNRESOLVED**
(**UNRESOLVED AFTER FROZEN-METADATA AUDIT**).

This record preserves the already-observed results of the read-only frozen-metadata inspection.
It does not amend the frozen audit reports or reinterpret any record's censoring status. No raw files
were modified, no data were preprocessed, no models were fitted, and no model performance was inspected.

## Frozen inputs and provenance

- Acquisition commit: `13715550adad0a628e92da6cf34568000ddbc797`.
- Validated audit checkpoint: tag `dmpk-data-audit-v1`, resolving to commit
  `1b93269b167d7d1bea245f90b34761011613f2d8`.
- Documentation parent for this record: `653e0fa94065dd74fd28a12ff122bc096cadfc04`, on
  `worktree-censoring-memo-metadata-audit`.
- Frozen inventory: [source_manifest.json](../manifests/source_manifest.json), SHA-256
  `370df65f0a6c18ef936b49429778a96f18efa2360c67356959bfb95c7547610d`.
  Original per-file download receipts remain in `../manifests/downloads/`.

The activity pages below were inspected directly as JSON. All paths are relative to
`experiments/compound_to_exposure/data/raw/chembl/`.

| Frozen activity page | Bytes | SHA-256 |
|---|---:|---|
| `CHEMBL3301370_activities_00000.json` | 1,474,958 | `657618e353b9795fd7fabb1a4086d7b936709059bbfdcbe689b0f87309e16d43` |
| `CHEMBL3301370_activities_01000.json` | 150,154 | `df8720b582563b8d04c1029aedb5fc5ced7614d3c190e912ac4bab67140ac46e` |
| `CHEMBL3301371_activities_00000.json` | 1,251,418 | `c6a101aba9d6e9010cbab9dd26daf7523929b6ce3dd19ea2e6625e8bcaf40f24` |
| `CHEMBL3301372_activities_00000.json` | 610,243 | `a1d5c17f98a34e3f4c5d1816c67ff97bb37c1722b66cb9a5a0ec348b3877ff90` |

OBSERVED: all **18 raw-file SHA-256 hashes and byte sizes matched the frozen source manifest**, including
these four pages. Inputs remain unchanged from the validated checkpoint. The inspection used direct
field tabulation and exact decimal comparisons of supplied values, without changing stored data.

## Observed counts

Groups below use `standard_value` and `standard_relation`. Original relations and numerical values
agree with their standard counterparts for every activity: 1,102/1,102 HLM, 837/837 rat hepatocyte and
408/408 human hepatocyte, or 2,347/2,347 overall.

| Group | CHEMBL3301370 HLM | CHEMBL3301371 rat hepatocyte | CHEMBL3301372 human hepatocyte |
|---|---:|---:|---:|
| All activities | 1,102 | 837 | 408 |
| Value = 3, relation null | 13 | 2 | 0 |
| Value = 150, relation null | 0 | 0 | 0 |
| Explicit `<` at value 3 | 274 | 115 | 104 |
| Explicit `>` at value 150 | 84 | 127 | 15 |
| Null relation, strictly 3 < value < 150 | 731 | 593 | 289 |

The 13 HLM activities are **14769802–14769814 inclusive**, all in
`CHEMBL3301370_activities_01000.json`. Each has raw `value` and `standard_value` equal to the string
`"3.0"`, and both `relation` and `standard_relation` equal to JSON `null`.

The two analogous rat activities are **14768823 / CHEMBL589973** and
**14768825 / CHEMBL364714**, both in `CHEMBL3301371_activities_00000.json`; each has the same
`"3.0"`/null value-and-relation pattern. Human hepatocytes have no null-relation record at either
numeric boundary.

## Fields inspected and comparison

The relevant fields were `activity_comment`, `data_validity_comment`, `text_value`,
`standard_text_value` (present), `standard_flag`, `relation` and `standard_relation`, alongside the
original and standard numeric values.

| Metadata | Null-at-3 records | Explicit `<3` records | Interior null-relation records | Explicit `>150` records |
|---|---|---|---|---|
| `activity_comment` | `null` | `null` | `null` | `null` |
| `data_validity_comment` | `null` | `null` | `null` | `null` |
| `text_value` | `null` | `null` | `null` | `null` |
| `standard_text_value` | `null` | `null` | `null` | `null` |
| `standard_flag` | `1` | `1` | `1` | `1` |
| `relation` / `standard_relation` | `null` / `null` | `<` / `<` | `null` / `null` | `>` / `>` |

These patterns hold across all three assays wherever the group exists. The four comment/text fields
are null for all 2,347 activities, and `standard_flag` is 1 for all 2,347, including explicit censoring.
Additional inspected metadata provides no distinction: `data_validity_description`, `upper_value` and
`standard_upper_value` are null; `activity_properties` is empty; `potential_duplicate` is 0 throughout.

## Result

The metadata does not distinguish the 13 HLM records as quantified versus censored. In particular,
`standard_flag = 1` is shared with explicitly censored records; both original and standard relations
are null, with no original equality qualifier to recover. No inspected annotation resolves their
censoring status. No record is reclassified as proven censored or proven uncensored, and null is not
converted to equality.

**UNRESOLVED**
