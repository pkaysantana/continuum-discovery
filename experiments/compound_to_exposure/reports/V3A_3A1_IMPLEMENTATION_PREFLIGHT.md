# v3A.1-RC Implementation Preflight

**Protocol:** `v3A.1-RC`

**Date:** `2026-09-23`

**Branch:** `v3a-3a1-preflight`

**Recovery status:** `RECOVERED_AND_REPAIRED`

**Execution state:** `PREEXECUTION_IMPLEMENTED_NOT_RUN`

**Scientific execution:** blocked pending an explicit future execution flag, state transition to `FROZEN_READY_FOR_EXECUTION`, and recorded independent audit.

## Recovery disposition

- **KEEP:** the frozen canonical SAP; the N=744 cohort CSV, scaffold-fold CSV, and ECFP4 matrix after deterministic regeneration reproduced their existing hashes exactly.
- **REPAIR:** `src/v3a_config.py`, `src/v3a_cohort.py`, `src/v3a_qrf_weights.py`, `src/v3a_preflight.py`, `tests/test_v3a_preflight.py`, `requirements.txt`, and the mechanical checklist. Repairs made constants immutable, isolated fail-closed Bemis–Murcko generation, made bootstrap multiplicity recovery exact for the locked scikit-learn version, added validation/statistical/conformal helpers, generated the freeze manifest/state record, and expanded synthetic/mechanical tests.
- **REPLACE:** none.
- **DELETE_AS_PARTIAL:** none in canonical V3A scope. Unrelated checkpoint, v2, historical report, run-log, scratch, and other project changes already present in the branch baseline were preserved and were not edited by this increment.

## Frozen artifacts and hashes

| Artifact | SHA-256 |
|---|---|
| Canonical SAP file | `eb4c09ceb8ff6ab4bafea2dfa86fcc01adccaa822b85c3d0707840ff65a1e4fb` |
| Exact-744 cohort CSV | `75c52910c611ab791ff5b193637baeff9d33f71f28848a44e023fba0a251b7dd` |
| Outer scaffold-fold CSV | `1fbd977633a1327e9c1cf4921dbaa3a25f4cced6bf9a2cf6010f2688191488de` |
| ECFP4 contiguous `uint8` array | `27c158c6b5967f44a0134f530b297794c6477543f61b40615bfc0f35ecba9ecb` |
| Persisted ECFP4 `.npy` file | `975fe7a2548d1081858e9fad8c976134cfe35cf7d693c300856a52a8b6b5252f` |
| Canonical raw assay rows | `fc1ea6fa15736449a75f578b2ff3e97661b8079d087aae000ed3ed508223ab37` |

## Cohort, split, and representation verification

- Cohort N: **744** exact quantitative observations.
- Strict interior (`3 < CLint < 150`): **731**.
- Exact lower boundary (`CLint == 3`): **13**.
- Exact upper boundary (`CLint == 150`): **0**.
- Censored observations in cohort: **0**.
- Representation: `ECFP4_2048_R2_BINARY_NOCHIRAL`.
- Matrix: **744 × 2048**, `uint8`, binary, no empty fingerprints.
- Unique Bemis–Murcko scaffold groups: **540**.
- Fold sizes: fold 1 **149**, fold 2 **149**, fold 3 **149**, fold 4 **149**, fold 5 **148**.
- Scaffold counts: **108 per fold**.
- Scaffold leakage: **none**.
- Activity assignment: every one of 744 activity IDs is unique and assigned exactly once.

## Environment

| Package | Version |
|---|---:|
| Python | `3.11.16` |
| RDKit | `2025.03.6` |
| scikit-learn | `1.9.1` |
| NumPy | `2.2.6` |
| pandas | `3.0.5` |
| SciPy | `1.17.1` |
| pytest | `9.1.1` |

## Frozen Random Forest configuration

```python
RandomForestRegressor(
    n_estimators=500,
    criterion="squared_error",
    max_features="sqrt",
    min_samples_split=2,
    min_samples_leaf=2,
    max_depth=None,
    bootstrap=True,
    random_state=20260923,
)
```

No hyperparameter search or tuning was performed.

## Test evidence

- Command: `python -m pytest experiments/compound_to_exposure/tests/test_v3a_preflight.py -p no:cacheprovider -v --tb=short -s`
- Passed: **78**.
- Failed: **0**.
- Skipped: **0**.
- Warnings: **0**.
- Maximum synthetic RF-weight prediction reconstruction error: **1.14e-13** (required `< 1e-6`).
- Maximum synthetic RF weight-sum error: **2.22e-16** (required `< 1e-12`).
- Tested on multiple synthetic datasets using both training and held-out queries.
- Additional QRF gates passed: nonnegative weights, nonempty support, `N_eff >= 1`, and monotone q10/q25/q50/q75/q90.
- The current manifest is tested to fail closed because its state is `PREEXECUTION_IMPLEMENTED_NOT_RUN`.

## Execution-boundary attestation

- Was any production model fit to real CHEMBL3301370 outcomes? **NO**
- Were any real model predictions, residuals, uncertainty scores, risk–coverage values, `REL_BENEFIT_80`, 10,000-run random-retention results, 10,000-run scaffold-bootstrap results, or conformal-calibration results produced? **NO**
- Were v2 code/results or historical result artifacts modified by this implementation increment? **NO**
- Scientific result artifacts created: **NONE**. The cohort, split, fingerprints, hashes, manifest, state record, tests, checklist, and this report are pre-execution mechanical artifacts only.
- Raw-data tree digest before/after implementation: `8c1d151fb2ca235ccafe596fadf757c60d7c81d0c1c062bb8ed8d532844d1e91` / identical.
- Historical-results tree digest before/after implementation: `3badfb31b359b57244d3ecae0506bda3c320c395bc441d79e1c70e853c1e20b2` / identical.

## Independent-audit handoff

Independent audit should re-run the mechanical generator and 78-test suite, inspect the use of scikit-learn bootstrap sample-index reconstruction, compare all four primary hashes, verify the fail-closed state/flag gate, and confirm that the final commit contains no scientific result artifact. Scientific execution remains prohibited until that audit is recorded and the required future state transition is made explicitly.

`V3A_3A1_PREFLIGHT_IMPLEMENTED_NOT_RUN`
