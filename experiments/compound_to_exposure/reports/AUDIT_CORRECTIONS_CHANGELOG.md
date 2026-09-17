# Audit correction changelog

The branch already contained the review corrections in `1b93269`. This follow-up closes interruption-test gaps and makes the audit-time pagination assertion explicit. No preprocessing or modelling was run; raw files, acquisition receipts and existing numeric audit artifacts were unchanged.

## Files changed

- `src/audit.py`: explicitly require acquired row count, unique activity-ID count, validated pagination count and stored `total_count` to agree; identify the failing assay.
- `tests/test_hardening.py`: seven new tests covering interrupted page iteration/download (no partial raw file or receipt), corrupt stored pagination, loaded-ID inconsistency, extra unmatched duplicate rows, missing/invalid labels and shared-label ambiguity.
- `tests/test_frozen_audit.py`: three new regressions for row/structure species denominators, all three assays' censor counts and unknown relations, and bare TDC microsome boundary values without qualifiers.
- `reports/REVIEW_SUMMARY.md`: explicitly scope completeness to the downloaded ChEMBL 37 API state, not a historical release.
- `reports/AUDIT_CORRECTIONS_CHANGELOG.md`: this changelog.
- Test evidence: `reports/test-2026-09-17T213518374541_0000-92cab7a9.log`, `reports/tests-2026-09-17T213518374541_0000-92cab7a9.json`, and the corresponding `.json` / `.started.json` receipts under `manifests/runs/`.

## Validation

Full compound-to-exposure suite: **79 passed, 0 failures, 0 errors, 0 skipped**, including **10 new tests**. Command from the experiment directory: `.venv/Scripts/python.exe -B src/run.py test`.

Existing tests also passed for changing ChEMBL totals, incomplete/empty pagination, repeated activity IDs within/across pages, wrong SHA-256, wrong size, missing receipt, changed source URL and refusal to overwrite changed audit outputs. The strict classification already requires exactly two rows, one unique rat structure/value match and one unique human structure/value match, with exact numeric agreement and no opposite-species value match; extra or ambiguous rows do not qualify.

**Every independently verified headline audit number remains unchanged.** The full report matches reviewed commit `13715550adad0a628e92da6cf34568000ddbc797` after accounting only for the previously approved explanatory field and six-group classification rename. All 18 raw hashes/sizes and acquisition receipts match that baseline.

| Verified finding | Preserved result |
|---|---|
| ChEMBL HLM / rat hepatocyte / human hepatocyte rows | 1,102 / 837 / 408 |
| Strict rat/human duplicate pairs | 187 |
| Species classes, rows: rat-only / human-only / both / neither | 609 / 183 / 405 / 16 |
| Same classes, distinct structures | 609 / 183 / 218 / 10 |
| Remaining duplicate groups | 6 strict structural non-matches; all 12 rows are neither, not unexplained mixed-species cases |
| Microsome strict matches / mismatches | 1,097 / 5; four representation/tautomer cases with matching ID/value/InChIKey evidence, one hydrate/parent representation case |
| CHEMBL3301370: `<3` / `>150` / null | 274 / 84 / 744 |
| CHEMBL3301371: `<` / `>` / null | 115 / 127 / 595 |
| CHEMBL3301372: `<` / `>` / null | 104 / 15 / 289 |
| Null standard_relation | Remains UNKNOWN; never converted to `=` |
| TDC microsome censor boundaries | All 274 lower and 84 upper source boundaries have matching bare numeric labels; no `<`/`>` qualifiers |

Correction scope ends with this commit. Existing later modelling work on the branch was not rerun or modified.
