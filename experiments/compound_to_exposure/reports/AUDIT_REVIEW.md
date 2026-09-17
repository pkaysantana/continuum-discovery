# Independent audit review — commit 13715550

Reviewer scope: numerical re-verification of the frozen-source DMPK audit from `data/raw/` only. No project code, reports or data were modified; no preprocessing or modelling was run.

## Method

- Independent script (kept outside the repository, in a session scratch directory) using only stdlib `csv`/`json`/`hashlib`/`decimal` and RDKit 2025.03.6 from the experiment `.venv`. No project module (`audit.py`, `chemistry.py`, `provenance.py`) was imported.
- Identity: `Chem.MolFromSmiles` (default sanitisation) → `MolToSmiles(isomericSmiles=True, canonical=True)`; string equality; no salt stripping, tautomer or stereo normalisation. This is an independent implementation of the same strict rule, not a call of the audited one.
- Labels: exact `Decimal` equality of ChEMBL `standard_value` and TDC `Y`. Null `standard_relation` counted as NULL, never `=`.
- Working tree confirmed byte-identical to commit 13715550 for `data/`, `manifests/`, `reports/`, `src/`, `tests/` (`git diff` empty).

## Recomputed values vs. published audit

| Check | Recomputed | Published | Status |
|---|---|---|---|
| Raw-file receipts / manifest entries / raw files on disk | 18 / 18 / 18; 0 hash or size mismatches; 0 raw files without receipt; receipt ≡ manifest hashes | 18 verified | NO ISSUE |
| PyTDC 1.1.15 sdist SHA-256 vs PyPI metadata | match | match | NO ISSUE |
| CHEMBL3301370 rows / unique activity IDs / molecule IDs / structures | 1,102 / 1,102 / 1,102 / 1,102 | 1,102 | NO ISSUE |
| CHEMBL3301371 | 837 / 837 / 837 / 837 | 837 | NO ISSUE |
| CHEMBL3301372 | 408 / 408 / 408 / 408 | 408 | NO ISSUE |
| Pagination | 3301370: pages at offset 0 (1,000) and 1000 (102), contiguous, `next` null on last page, `total_count` constant 1,102; 3301371/72 single page with `next` null. All rows carry the requested assay ID; activity IDs sorted and unique. | complete | NO ISSUE |
| Standard relations `<` / `>` / NULL (3301370) | 274 / 84 / 744; boundaries all 3.0 / 150.0 | same | NO ISSUE |
| (3301371) | 115 / 127 / 595 | same | NO ISSUE |
| (3301372) | 104 / 15 / 289 | same | NO ISSUE |
| Explicit `=` in any assay | 0 | 0 | NO ISSUE |
| Original vs standard relation and value agreement | 100% in all three assays | same | NO ISSUE |
| TDC microsome rows / IDs / structures / dup groups | 1,102 / 1,102 / 1,102 / 0 | same | NO ISSUE |
| TDC hepatocyte rows / IDs / structures | 1,213 / 1,020 / 1,020 | same | NO ISSUE |
| TDC `Y` containing `<`, `>`, `≤`, `≥`, `~` | 0 (microsome), 0 (hepatocyte); no missing targets | 0 | NO ISSUE — qualifiers absent from TDC |
| TDC values exactly 3 / 150 | microsome 287 / 84; hepatocyte 195 / 137 | same | NO ISSUE |
| Hepatocyte duplicate groups | 193, all of size exactly 2; each group is a single TDC ID; no ID maps to >1 structure | 193 | NO ISSUE |
| Groups with differing labels | 193 / 193 (no identical-label group) | 193 | NO ISSUE |
| Strict rat/human pairs (exactly 2 rows; one row value-matches rat only, other value-matches human only) | 187; in all 187 each row matches exactly one source record | 187 | NO ISSUE |
| Non-strict groups | 6 (see below) | 6 unresolved | NO ISSUE (see MINOR-1) |
| Structure class rows (rat-only / human-only / both / neither) | 609 / 183 / 405 / 16 | same | NO ISSUE |
| Structure class distinct structures | 609 / 183 / 218 / 10 | same | NO ISSUE |
| Row value-match classes (rat / human / both / neither) | 796 / 370 / 31 / 16 | — (31 "both" published) | NO ISSUE |
| Rat-only or human-only structure rows lacking a value match | 0 / 0 | — | NO ISSUE |
| TDC microsome ↔ ChEMBL strict structure overlap | 1,097; 5 TDC-only; 5 ChEMBL-only; ≤1 candidate per row | 1,097 / 5 / 5 | NO ISSUE |
| Matched pairs with exact numeric equality / same molecule ID | 1,097 / 1,097 | 1,097 | NO ISSUE |
| Exact molecule-ID overlap | 1,101 | 1,101 | NO ISSUE |
| Matched ChEMBL `<3` → TDC 3; `>150` → TDC 150 | 274 / 274; 84 / 84 | same | NO ISSUE |
| TDC 3 matched to NULL-relation ChEMBL records | 13 | 13 | NO ISSUE |
| Human HLM ∩ HH by molecule ID / by structure | 187 / 187; the two sets map one-to-one | 187 / 187 | NO ISSUE |
| Biogen rows / unique Internal IDs / structures | 3,521 / 3,521 / 3,521 | same | NO ISSUE |
| Biogen HLM non-null / missing | 3,087 / 434; 0 unparseable | same | NO ISSUE |
| Biogen HLM min / count at min / next value | 0.675686709 / 958 / 0.678154038 | 0.675686709 / 958 | NO ISSUE |
| Biogen HLM max / median | 3.372714293 / 1.205312653 | same | NO ISSUE |

## Five unmatched microsome structures (strict rule not relaxed)

| TDC ID | TDC canonical | ChEMBL record (same ID or declared parent) | Value | Relation | Standard InChIKey equal |
|---|---|---|---|---|---|
| CHEMBL82663 | `…c2nc(O)sc12` (hydroxythiazole) | CHEMBL82663 `O=c1[nH]c2…s1` (thiazolone) | 111.0 = 111.0 | NULL | yes |
| CHEMBL1483 | `…c2nc(…)[nH]c2c1` | CHEMBL1483 `…c2[nH]c(…)nc2c1` | 34.67 = 34.67 | NULL | yes |
| CHEMBL412142 | `Cc1c[nH]c(…)n1` | CHEMBL412142 `Cc1cnc(…)[nH]1` | 96.0 = 96.0 | NULL | yes |
| CHEMBL1513 | tetrazole `nn[nH]n` | CHEMBL1513 tetrazole `nnn[nH]` | 17.78 = 17.78 | NULL | yes |
| CHEMBL190 | theophylline | CHEMBL1355736 (parent CHEMBL190) `….O` hydrate | 4.79 = 4.79 | NULL | no (extra water component) |

Four are tautomer/representation differences (confirmed by identical standard InChIKey, used here as supporting evidence only); one is a parent/hydrate difference. All values agree exactly. These remain strict mismatches, as the audit states.

## Six non-strict hepatocyte duplicate groups

All six are two-row groups whose structure has **no strict match in either rat or human ChEMBL** (both rows "neither"): CHEMBL115 (10.23, 53.7), CHEMBL173706 (150.0, 4.57), CHEMBL1513 (9.01, 10.47), CHEMBL1483 (83.18, 12.59), CHEMBL190 (5.75, 3.0), CHEMBL82663 (91.0, 42.5). Four of these IDs are the same tautomer/hydrate cases as the microsome mismatches. These 12 rows plus 4 singleton rows make up the 16 "neither" rows / 10 structures. No group has 3+ rows, a both-species row, or a single-species pair.

## Findings

### BLOCKER

None.

### IMPORTANT

**IMPORTANT-1 — Acquisition and integrity failure modes are claimed but not tested.**
- File/line: `tests/test_audit.py` (whole file); code paths `src/acquire.py:17-23` (missing receipt, changed URL), `src/acquire.py:43-61` (total-count drift, empty page, wrong assay, repeated activity ID, incomplete pagination), `src/provenance.py:46-47` (hash/size mismatch), `src/audit.py:355-358` (refuse changed outputs). README "Reproduction" asserts these fail.
- Tests actually cover: SHA-256 vector, create-only write refusal, parsing/identity/relation handling, and species/microsome/paired logic on synthetic fixtures. None of the listed acquisition/verification paths is exercised.
- Scientific consequence: none for the current snapshot (independently verified complete and hash-consistent above); but regressions in the completeness/immutability guards would go undetected in any future re-acquisition.
- Published number changes: no.
- Minimal correction: add offline tests with synthetic page JSON (total_count change, empty page, duplicate activity_id, short final page) by factoring the pagination check into a pure function, plus a `verify()` test with a tampered byte and a URL-change test for `download()` against a temp ROOT.

### MINOR

**MINOR-1 — Wording of the six "unresolved" groups understates why.** `reports/REVIEW_SUMMARY.md` ("six groups remain unresolved under that rule") and `src/audit.py:149` (`partial_or_unresolved`). All six have zero strict structural candidates in either species; they are not partially traced. Consequence: reader could assume ambiguous species evidence rather than representation mismatch. No number changes. Correction: state "six groups have no strict structural match to either ChEMBL hepatocyte assay (all rows 'neither')".

**MINOR-2 — Trace rule is looser than the strict pair definition.** `src/audit.py:149` accepts any group with differing labels containing ≥1 rat-only and ≥1 human-only row; it does not require group size 2 or single-record provenance. On this snapshot every group has size 2 and each matched row maps to exactly one record, so the count is identical (187). Correction: assert `len(rows) == 2` and single matching record, or report non-binary groups separately.

**MINOR-3 — Completeness is not re-checked at audit time.** `src/audit.py:49-63` does not compare loaded rows with `page_meta.total_count`, and `EXPECTED` (`src/audit.py:16`) is reported but not enforced. Relies on acquisition-time checks (untested, IMPORTANT-1). No number changes. Correction: assert `len(rows) == page_meta.total_count` and `next is None` on the last page inside `load_sources`.

**MINOR-4 — Null-relation values at censoring boundaries are not tabulated per assay in the summary.** Recomputed: 13 (3301370) and 2 (3301371) NULL-relation records have value exactly 3; none at 150. The summary mentions the 13 microsome cases only. No number changes; the audit correctly keeps them UNKNOWN. Correction: add the per-assay count to REVIEW_SUMMARY.

### NO ISSUE

Raw-file preservation and SHA-256 manifests; ChEMBL counts and pagination; relation counts and null handling (never recoded to `=`); TDC removal of `<`/`>` qualifiers (confirmed: 274 `<3` and 84 `>150` records appear as bare 3 / 150); hepatocyte duplicate groups and label differences; 187 strict pairs; 609/183/405/16 classification; 1,097/1,102 microsome matches and five unmatched identities; 187 paired human cohort under both identity definitions; Biogen N, missingness and 958-value minimum pile-up.

## Acquisition-completeness assessment

Stored page metadata is internally consistent with complete retrieval for all three assays (constant `total_count`, contiguous offsets, terminal `next: null`, rows = total, unique activity IDs = total). Completeness is relative to the live ChEMBL 37 API at retrieval time; it cannot be independently confirmed against a historical release, which the audit already flags as UNRESOLVED. No concern for this snapshot beyond the untested guards (IMPORTANT-1).

## Verdict

All headline numeric conclusions of the original audit survive independent recomputation with zero numeric discrepancies. Corrections are limited to test coverage and wording/robustness of rules that do not change any published figure.

**PASS_WITH_CORRECTIONS**
