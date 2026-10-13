# GSK development-only recovery checkpoint

Status: IMPLEMENTED; scientific execution NOT AUTHORISED. Synthetic tests NOT RUN
on this laptop because scikit-learn is unavailable. No new predictive finding.

Sprint checks (2026-10-13): dependency-free AST parsing passed for all three Python
files; 11 synthetic test methods counted statically. Git comparison against the
starting checkpoint showed no changes under `experiments/compound_to_exposure/`.
The four new files remain uncommitted; neither branch's commit pointer advanced.
Syntax validation is not a substitute for executing the synthetic tests.

Starting checkpoint: `49e94153a78224eb274ace540085d7a4d483605f` on
`wip/v3a-ticket5-pass2fa-codex-quota-handoff-2026-10-01`.
Working branch: `dev/gsk-development-validation-2026-10-13`.

## Boundaries

Everything under `experiments/compound_to_exposure/` remains unchanged, including
`data/`, `splits/`, `manifests/`, `results/`, `reports/`, `docs/`, `src/`, and `state/`.
In particular preserve the protected run
`manifests/runs/2026-09-18T215009395468_0000-4c110e67/`, both execution-state JSONs,
V1 outputs, and all V3A freeze artifacts. Neither historical runner is imported.
No protected outcomes were loaded in this sprint. No installs or model execution.

`harness.py` has no file loader, CLI, data discovery or result writer. It takes
only an explicit in-memory input bundle. Development execution defaults to
blocked and requires separate user approval before passing
`approve_development=True`. This flag is a workflow guard, not a security sandbox:
the caller is trusted to supply an independently reviewed bundle. Source hash
syntax and record consistency do not authenticate arbitrary caller-supplied data.
A reviewed development-only extraction step remains a prerequisite to real use.

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
| This sprint | Isolated harness and 11 synthetic test methods | IMPLEMENTED, execution blocked by missing dependency; no scientific results | this directory |

Important: 0.2005 is R-squared, not Pearson R. V2 holdout was reserved from V2
tuning, but the underlying dataset had prior V1 analyses (V2 SAP line 28).
The source audit reports 1102 unique structures, 274 left-censored, 84 right-
censored, and 13 historically boundary-ambiguous rows. Thus 1089 = 1102 - 13,
whereas 731 is the strict-interior regression cohort. These are not interchangeable.
The retained V2 result does not establish in-vivo PK, clinical exposure or efficacy.

## Synthetic checks and environment

Run from the repository root in an already approved compatible environment:

```powershell
python -B -m unittest application_development.gsk_clearance.test_harness -v
```

No pytest dependency is required. Required imports: NumPy, RDKit, SciPy and
scikit-learn. Current laptop: Python 3.12.10; NumPy, SciPy and RDKit discoverable;
scikit-learn absent. This sprint does not install dependencies. Historical package
pins are documented in the existing project; do not claim the laptop reproduces
that environment. Select and record a compatible isolated environment before
running the tests, and retain actual versions from `runtime` in any future result.

The tests cover exact feature matrices reaching every fit; 12/2048 dimensions;
the adversarial `'r1' in 'P3'` defect; applied and fitted hyperparameters;
scaffold isolation; training-only imputation/scaling and baselines; fold outcome
perturbations; log transformation, MAE, RMSE, Pearson R, Spearman, R-squared and
undefined cases; provenance failures; holdout rejection; bounded trees and repeatability.

Dependency-free syntax check (does not execute imports or tests):

```powershell
python -B -c "import ast,pathlib; paths=list(pathlib.Path('application_development/gsk_clearance').glob('*.py')); [ast.parse(p.read_text(encoding='utf-8')) for p in paths]; print('Syntax OK:',len(paths),'files')"
```

## Next-session experiment plan: approval required

1. First obtain a compatible environment and pass all synthetic tests. Any failure
   stops preparation; do not modify frozen code to make tests pass.
2. Request separate explicit execution approval for the following fixed experiment.
   Prepare an independently reviewed bundle of ONLY the 582 V2 strict-interior CV
   IDs, with original folds 0..4 of sizes 115/120/115/117/115. Inspect only identity,
   partition, scaffold and fold columns of the master partition to form an allowlist.
   An approved streaming extractor must filter IDs BEFORE parsing outcome fields;
   never use `get_cohorts()` or load the full source into a modelling dataframe.
   No feature or outcome extraction for the 149 protected IDs is permitted.
3. Preserve the source SMILES, null qualifier, units and frozen assignments.
   A second reviewer/check must reconcile the allowlist to the authoritative split,
   verify source/split hashes and exclude every protected ID. The extractor is NOT
   implemented or run in this sprint. Without it, real evaluation stays blocked.
4. Evaluate exactly four combinations on identical frozen CV folds: R1/R2 x
   Ridge/RF. Ridge alpha=1, solver=lsqr, tol=1e-4, max_iter=10000. RF: 100 trees,
   max_features=sqrt, min_samples_leaf=3, max_depth=None, bootstrap=True,
   criterion=squared_error, min_samples_split=2, seed=20261013, n_jobs=1.
   These are prospective development settings, NOT retrospectively repaired V2.
   Include fold-training mean/median baselines. No grid search or model selection.
5. Bound work to 20 learned fits (10 RF fits = 1000 trees), single-thread BLAS and
   estimator execution, no GPU or cloud, no nested CV, bootstrap or repeated seeds.
   Set OMP_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1 and MKL_NUM_THREADS=1 BEFORE Python.
   Use a supervised 15-minute wall-clock / 2-GB process budget. Stop on any limit,
   dependency mismatch, provenance failure, leakage, nonfinite output or incomplete
   folds. The external watchdog is a prerequisite, not provided by this in-memory API.
   Do not relax settings or cherry-pick completed folds after seeing performance.
6. Keep outputs only under a new, nonexisting application-development run directory:
   `inputs_manifest.json`, `configuration.json`, `oof_predictions.csv`,
   `metrics.json`, and `receipt.json` with code/file hashes, commit AND dirty-source
   hashes, runtime versions, seeds, complete row/fold identities, fitted settings,
   elapsed resources and input digests. A no-overwrite writer must be reviewed
   before real execution; the present harness returns an in-memory result only.
7. Label every result EXPLORATORY_DEVELOPMENT_ONLY. All 582 observations serve as
   validation once and training four times. No protected claim, tuned final refit,
   V2 result replacement, V3A execution or persisted-state update is allowed.

## Application description

Independent, AI-assisted DMPK research examining how molecular structure informs
human liver microsomal intrinsic-clearance prediction. The project combines
chemical data curation, scaffold-aware evaluation and critical analysis of model
limitations. Historical results show modest predictive signal; provenance audits
identified feature-routing and parameter-recording defects that restrict the
conclusions. This development sprint adds an isolated validation harness and
synthetic correctness tests to make future exploratory comparisons reviewable.
It does not claim experimental validation or independently authored implementation.
