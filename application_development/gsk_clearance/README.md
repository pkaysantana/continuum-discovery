# GSK development-only recovery checkpoint

Status: VALIDATED; scientific execution NOT AUTHORISED in this sprint. All 24
synthetic tests passed (11 harness + 13 extractor tests, exit code 0). Original
harness committed and pushed at commit `1aa7f6e557b9c0d8f28653f5ef34092d1d9f10e3`.
No real-data modelling executed; no new predictive finding.

Starting checkpoint: `49e94153a78224eb274ace540085d7a4d483605f` on
`wip/v3a-ticket5-pass2fa-codex-quota-handoff-2026-10-01`.
Harness commit: `1aa7f6e557b9c0d8f28653f5ef34092d1d9f10e3`.
Working branch: `dev/gsk-development-validation-2026-10-13`.

## Boundaries

Everything under `experiments/compound_to_exposure/` remains untouched, including
`data/`, `splits/`, `manifests/`, `results/`, `reports/`, `docs/`, `src/`, and `state/`.
In particular, the protected run
`manifests/runs/2026-09-18T215009395468_0000-4c110e67/`, both execution-state JSONs,
V1 outputs, and all V3A freeze artifacts remain strictly unmodified. Neither historical
runner is imported. No protected outcomes were loaded.

`harness.py` takes only an explicit in-memory input bundle. Development execution
defaults to blocked and requires explicit approval via `approve_development=True`.
This flag is a workflow guard, not a security sandbox: the caller is trusted to
supply an independently reviewed bundle.

### Data access boundary and limitation
The extractor (`extractor.py`) reads:
- Master partition: `splits/master_partition.csv` (SHA-256: `971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a`)
- ChEMBL interim sources: `data/interim/CHEMBL3301370_rows.csv` (`fc1ea6fa15736449a75f578b2ff3e97661b8079d087aae000ed3ed508223ab37`),
  `CHEMBL3301371_rows.csv` (`2c7578045d930d287de37f9da74d38cd978f5f7228b781e4bf2dc4c726bbe924`),
  `CHEMBL3301372_rows.csv` (`b3164bb3efb7a4c270dcbc2308e54573e728044a516eff1121d0522a3e1066d4`).

Protected holdout prediction files are never accessed:
`experiments/compound_to_exposure/manifests/runs/2026-09-18T215009395468_0000-4c110e67/primary_holdout_predictions.csv`.
Holdout exclusion is derived entirely from the master partition (all 250 holdout
partition rows, covering the 149 evaluated in V2), which is the authoritative,
pre-execution boundary.

**Explicit limitation:** The interim CSV files contain CLint outcome values for
all activity IDs in the partition, including censored and holdout rows. The extractor
enforces the boundary by building the allowlist strictly from the 582 `partition=cv`,
`status=INTERIOR_OBSERVED` rows *before* opening the interim files, and parsing outcome
fields only for allowlisted IDs. Holdout CLint values are never parsed into memory.
However, because holdout values physically reside in the interim files on disk,
this boundary is a Python-level data-access control, not OS-level filesystem isolation.

## Scientific choices

We adopt V2's 12-descriptor R1 definitions by importing only
`experiments.compound_to_exposure.src.representations`. Morgan is radius 2,
2048 binary bits, chirality disabled. V1 used seven descriptors and chirality
enabled; this is therefore NOT a reproduction of V1. Full supplied structures
are retained for features: no desalting, neutralisation or tautomer normalisation.
Scaffolds follow V2's largest-heavy-fragment rule, canonical-SMILES tie break,
nonchiral atomic Murcko scaffold, and shared `__ACYCLIC__` group. Invalid molecules
fail explicitly instead of being silently mapped to the acyclic group.

Input CLint must be in uL/min/mg (numerically equal to mL/min/g), unqualified,
strictly between 3 and 150. Transform once using log10. Descriptors are imputed
using training-fold medians; Ridge alone drops training-constant descriptors and
scales using training statistics. An entirely missing training descriptor fails
explicitly rather than silently changing the descriptor panel. Morgan is neither
scaled nor imputed. Duplicate molecular identities fail rather than being merged.

The input bundle supplies frozen scaffold/fold assignments. CV never generates,
balances or searches splits. Models are freshly instantiated per fold; explicit
representation mapping replaces pipeline-ID substring routing. Parameters are
passed into constructors. Reports query each fitted estimator's actual settings.
Pooled OOF MAE/RMSE are log10 errors; `pearson_r`, `spearman_rho` and `r_squared`
are distinct. Undefined correlations/R-squared are `None`, not invented zeros.
Mean/median baselines use training-fold log outcomes only. No significance claims.

## Historical evidence versus prospective work

All source paths below are relative to `experiments/compound_to_exposure/`.

| Record | Finding | Evidence status / limitation | Source |
|---|---|---|---|
| V1 HLM | RF Morgan OOF MAE 0.3255, RMSE 0.3982, Spearman 0.4172, R-squared 0.1838; N744 | DOCUMENTED; five-fold scaffold OOF, not a protected test | `results/primary_v1/METRICS.json:1`, result commit `98e43be` |
| V2 selection | P3/P4 grouped-CV MAE 0.3322868963; development N582 | QUALIFIED; all candidates received Morgan; parameter dictionaries were recorded but not applied | `src/execute_v2.py:285`, `src/pipelines.py:28`, protected `selection_manifest.json:8` |
| V2 protected output | N149; recovered MAE 0.2955808, RMSE 0.3692430, Spearman 0.4368258, R-squared 0.2005007 | QUALIFIED; genuine executed Morgan RF; no claim of valid representation selection | `reports/V2_EXECUTION_001_RECOVERED_RESULTS.md:12` |
| V2 median baseline | Recovered MAE 0.3513546; reported difference 0.0557738 | DOCUMENTED recovery; baseline predictions absent from protected CSV | same report; `reports/V2_EXECUTION_001_POST_ACCESS_FORENSICS.md:37` |
| V2 bootstrap | Reported CI [0.0227499, 0.0945252] | UNRESOLVED provenance; do not claim significant improvement | `reports/V2_FINAL_INTERPRETATION.md:41` |
| Structural characterisation | Holdout nearest-training Tanimoto median 0.52; two similarities of 1.0 | DOCUMENTED; scaffold-disjoint does not imply unfamiliar fingerprints | `reports/ECFP4_TANIMOTO_PREFREEZE_CHECK.md:17` |
| V3A | QRF/CQR/inference implementation | NOT EXECUTED; state remains pre-execution | `state/v3a_execution_state.json:1` |
| Sprint 1 | Isolated harness and 11 synthetic tests | COMMITTED and PUSHED (`1aa7f6e5`); tests passed | `application_development/gsk_clearance/` |
| Sprint 2 | Input extractor and 13 adversarial tests | IMPLEMENTED and PASSED (13/13); prospective design verified | this directory |

Important: 0.2005 is R-squared, not Pearson R. V2 holdout was reserved from V2
tuning, but the underlying dataset had prior V1 analyses (V2 SAP line 28).
The source audit reports 1102 unique structures, 274 left-censored, 84 right-
censored, and 13 historically boundary-ambiguous rows. Thus 1089 = 1102 - 13,
whereas 731 is the strict-interior regression cohort. These are not interchangeable.
The retained V2 result does not establish in-vivo PK, clinical exposure or efficacy.

## Synthetic checks and runtime environment

A project-local virtual environment (`.venv`) was configured without administrator
privileges. scikit-learn 1.9.1 was installed to satisfy harness dependencies.

### Actual runtime versions vs historical locked environment

| Package | Historical lock (`requirements.txt`) | Current `.venv` runtime | Notes |
|---|---|---|---|
| Python | 3.12 (assumed) | 3.12.10 (AMD64) | Matches minor version |
| scikit-learn | 1.9.1 | 1.9.1 | Exact match |
| NumPy | 2.2.6 | 2.5.3 | Runtime is newer than lock |
| SciPy | 1.17.1 | 1.18.1 | Runtime is newer than lock |
| RDKit | 2025.3.6 | 2026.09.1 | Newer; emits deprecation warning on `GetMorganFingerprintAsBitVect` favoring `MorganGenerator` |

These version differences must be retained and reported in any execution receipt.
The current environment does not claim byte-for-byte numerical identity with the
historical execution environment.

### Running the synthetic tests

Run both test suites from the repository root:

```powershell
# 1. Harness synthetic unit tests (11 tests)
.\.venv\Scripts\python.exe -B -m unittest application_development.gsk_clearance.test_harness -v

# 2. Extractor adversarial tests (13 tests)
.\.venv\Scripts\python.exe -B -m unittest application_development.gsk_clearance.test_extractor -v
```

Both suites execute with exit code 0 and require no network access or real data.

The tests cover:
- Exact feature matrix dimensions (12 R1, 2048 R2) and descriptor names.
- Adversarial substring routing defect (`'r1' in 'P3'`).
- Applied and reported hyperparameters from fitted estimators.
- Cross-fold scaffold isolation and cross-fold mutation rejection.
- Training-only imputer/scaler fitting and training-only mean/median baselines.
- Target transformation log10 and metric definitions (MAE, RMSE, Pearson r, Spearman rho, R-squared).
- Repeatability across duplicate executions with identical seeds.
- Fail-closed behavior for tampered partitions, mismatched source checksums, duplicate molecular IDs, wrong scaffold assignments, qualified/censored relations, missing assay values, invalid SMILES, incomplete allowlists, allowlist poisoning / holdout access attempts, and unexpected units.

## Prospective experiment design (Task D)

The existing harness and extractor support the fixed design:
- **Cohort**: 582 strictly interior development compounds (`partition == 'cv'`, `status == 'INTERIOR_OBSERVED'`).
- **Folds**: 5 frozen scaffold-grouped folds (sizes: 115, 120, 115, 117, 115).
- **Representations**: 12 RDKit physicochemical descriptors (R1) and Morgan radius-2, 2048-bit binary fingerprints (R2).
- **Pipelines**: 4 combinations (R1 Ridge, R2 Ridge, R1 RF, R2 RF) plus 2 training-only baselines (mean, median).
- **Fits budget**: 20 learned fits total (4 pipelines x 5 folds; 10 RF fits = 1,000 trees total).
- **Hyperparameters**: Fixed; no hyperparameter grid/random search.
  - Ridge: `alpha=1.0`, solver=`lsqr`, `tol=1e-4`, `max_iter=10000`.
  - RF: `n_estimators=100`, `max_features='sqrt'`, `min_samples_leaf=3`, `max_depth=None`, `bootstrap=True`, `criterion='squared_error'`, `min_samples_split=2`, `random_state=20261013`, `n_jobs=1`.
- **Metrics**: Pooled OOF log10 MAE, RMSE, Pearson r, Spearman rho, R-squared.
- **Resource bounds**: CPU-only (`OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`), <2 GB RAM, 15-minute wall clock limit.

Execution command (requires explicit authorization; DO NOT run without approval):
```powershell
$env:OMP_NUM_THREADS="1"; $env:OPENBLAS_NUM_THREADS="1"; $env:MKL_NUM_THREADS="1"
.\.venv\Scripts\python.exe -c "from application_development.gsk_clearance.extractor import extract; from application_development.gsk_clearance.harness import evaluate, Configuration; bundle = extract('.'); result = evaluate(bundle['records'], bundle['provenance'], Configuration(), approve_development=True); print('Status:', result['status'], 'Fits:', len(result['fitted_configurations']))"
```

## Application description

Independent, AI-assisted DMPK research examining how molecular structure informs
human liver microsomal intrinsic-clearance prediction. The project combines
chemical data curation, scaffold-aware evaluation and critical analysis of model
limitations. Historical results show modest predictive signal; provenance audits
identified feature-routing and parameter-recording defects that restrict the
conclusions. This development sprint adds an isolated validation harness,
authoritative input extractor, and 24 synthetic correctness tests to make future
exploratory comparisons reviewable. It does not claim experimental validation or
independently authored implementation.
