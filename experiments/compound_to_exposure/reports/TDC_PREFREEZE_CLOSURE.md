# TDC pre-freeze closure: defer execution

2026-09-18. Branch: `dmpk-compound-to-exposure`.

**Disposition B — TDC_PROTOCOL_NOT_FULLY_SPECIFIED.** PyTDC 1.1.15 supplies a documented retrieval/split/evaluation framework, but it does not fully specify this project's benchmark experiment. Required benchmark-group files are not present in the inspected local locations; the experiment environment is not a compatible installed PyTDC environment; and consequential run settings remain caller choices. Defer TDC execution from the frozen v2 protocol to a separately preregistered exploratory benchmark. No missing setting has been invented to retain TDC in v2.

This is a source, dependency-metadata and file-presence inspection. No package installation, acquisition, TDC import, split generation, benchmark execution, model fitting, performance calculation or v1 performance inspection occurred. The SAP and primary v2 science analysis are unchanged.

## Evidence basis

The source was reread directly from [pytdc-1.1.15.tar.gz](../data/raw/tdc/pytdc-1.1.15.tar.gz), whose SHA-256 agrees with the acquisition manifest and retained PyPI metadata. Source references below are archive-relative paths under `pytdc-1.1.15/`, with original line numbers. The earlier [harness specification](TDC_HARNESS_SPECIFICATION.md) remains unchanged.

OBSERVED denotes local file/runtime evidence; DOCUMENTED denotes explicit package code or documentation; UNRESOLVED denotes facts/settings not established by those sources. The signed metric's direction is a mathematical interpretation, not an automatic optimization rule supplied by the harness.

## API and required files

DOCUMENTED: `clearance_microsome_az` is **both a standalone ADME dataset and an ADMET benchmark-group member** (`tdc/metadata.py:103,443`). The canonical registry name is lowercase; case-insensitive lookup accepts `Clearance_Microsome_AZ` (`tdc/utils/misc.py:11–38`).

The benchmark-group retrieval calls, shown for specification only and **not executed**, are:

```python
from tdc.benchmark_group import admet_group
group = admet_group(path="./data")
benchmark = group.get("clearance_microsome_az")
```

`admet_group` fixes group name `ADMET_Group` and CSV format (`tdc/benchmark_group/admet_group.py:8–17`). `get()` returns `name`, `train_val` and `test` (`tdc/benchmark_group/base_group.py:137–155`). It needs:

- `<path>/admet_group/clearance_microsome_az/train_val.csv`
- `<path>/admet_group/clearance_microsome_az/test.csv`

On a cold cache, construction downloads `admet_group.zip` from the Dataverse access endpoint for file ID **4426004**, then extracts it. An existing group directory is accepted as a local copy; this wrapper does not verify its contents by hash (`tdc/utils/load.py:249–276`; `metadata.py:1199,1206`). Once extracted, the two CSVs are the task's required runtime data; the archive is needed to document their acquisition, not reread by every evaluation.

The separate standalone call is `from tdc.single_pred import ADME`, followed by `ADME(name="clearance_microsome_az", path="./data").get_data()`. It loads `clearance_microsome_az.tab`, Dataverse ID **4266186**, rather than the benchmark group's preassigned test data (`tdc/single_pred/adme.py:15–48`; `tdc/metadata.py:850,1059`). The root import `from tdc import BenchmarkGroup` used in the bundled README points to the deprecated class; its own warning recommends the group-specific API (`tdc/__init__.py:3`; `tdc/benchmark_deprecated.py:93–95`).

OBSERVED: filename searches, including ignored/hidden files in the experiment, found no group archive, `train_val.csv` or `test.csv`. Additional workspace filename checks and recursive checks of `C:/Users/Don/Downloads` and workspace `data/` found none; `C:/Users/Don/data` and `C:/Users/Don/admet_group` do not exist. This is a statement about the inspected locations, not proof of absence from every disk or opaque external cache. No registered, hashable group-data inputs are available to this project.

The following local inputs **do** exist and were hashed. Paths are relative to `experiments/compound_to_exposure/`:

| File | Bytes | SHA-256 |
|---|---:|---|
| `data/raw/tdc/pytdc-1.1.15.tar.gz` | 154168 | `cd6164859af7b9b6f60e0c6d6e50679eacaffd09cfdea1acfc8bb7360e8e2205` |
| `data/raw/tdc/PyTDC-1.1.15-pypi.json` | 23967 | `7ac902ba3b4e22423b070057c72b85958c2053e79f4ef56f661119916985860a` |
| `data/raw/tdc/clearance_microsome_az.tab` | 81661 | `4c9047dc1860cc05d5bdc09aa9cfef86a40740605c2ff06990b1fceb6085db9d` |
| `data/raw/tdc/clearance_microsome_az_metadata.json` | 71 | `29ff99f182fc1d47c5a2d9dad6806ef19671d013ab64d4f1157077bbdb5120a5` |

These hashes do not establish benchmark-group CSV hashes, membership or equality to the standalone dataset. Acquisition code explicitly pins the source archive version and downloads standalone data by registry ID without installing/invoking PyTDC (`src/acquire.py:59–89`).

## Splits, proportions, seeds and scoring

| Question | Verified specification and limit |
|---|---|
| Group split call | `group.get_train_valid_split(seed=seed, benchmark="clearance_microsome_az", split_type="default")`; seed is required, with no default. |
| Default split method | Metadata selects `scaffold`. The group calls `create_scaffold_split(train_val, seed, frac=[0.875,0.125,0.0], entity="Drug")`. |
| Exact proportions prescribed in code | Requested **87.5% training / 12.5% validation of the existing train_val file**, with no new test allocation. Whole-group packing determines realised sizes. The fixed test fraction is encoded in the absent data files, not established by this method. |
| Exact overall train/validation/test proportions | **UNRESOLVED locally.** Neither the group's test N nor the seed-dependent realised training/validation Ns can be established from these missing files. Do not assert an exact 70/10/20 group allocation. |
| Standalone loader default | `get_split(method="random", seed=42, frac=[0.7,0.1,0.2])`; these are requested standalone fractions, not the group benchmark's fixed test membership. Random test sampling uses the supplied seed; validation sampling uses `random_state=1`. |
| Metric | Registered `spearman`; `Evaluator` calls `scipy.stats.spearmanr(y_true, y_pred)[0]`, returning the signed coefficient, not its p-value or absolute value. |
| Direction | Higher signed Spearman is better rank agreement; +1 is perfect agreement. The group evaluator does not tune/select models or implement a maximize/minimize policy. |
| Automatic selection | Yes for group `evaluate(pred, testing=True)`: metric comes from metadata. No metric argument is required. The standalone dataset loader has no `evaluate()` method; a caller must choose a standalone evaluator. |
| Test-score precision | Group `evaluate()` rounds to three decimal places and assumes predictions follow `test.csv` row order. It does not align predictions by molecule ID. |
| Seeds prescribed by the callable API | No exact seed list. The split API requires a caller-supplied seed; it neither chooses estimator seeds nor restricts split seeds to a particular set. |
| Documented official seed example | The bundled README's generic ADMET leaderboard framework uses **[1,2,3,4,5]** as split seeds and calls `evaluate_many()`. That is documentary support for a five-seed convention, not an enforced clearance-specific seed configuration. |
| Multiple runs required? | A single `evaluate()` call has no multiple-run requirement. Choosing `evaluate_many()` requires **at least five** supplied prediction dictionaries; it does not require exactly five, record/verify seed identities or execute runs itself. |
| Aggregation | `evaluate_many()` defaults to evaluating each supplied run, then calculates `np.mean` and `np.std` (**ddof=0**) of the already three-decimal run scores, rounding the returned mean and SD to three decimals. It returns `{dataset: [mean, std]}`. |

Sources: `tdc/metadata.py:535,580`; `tdc/benchmark_group/base_group.py:90–135,157–188,218–257`; `tdc/single_pred/single_pred_dataset.py:146–171`; `tdc/utils/split.py:10–33`; `tdc/evaluator.py:413–418,471–488`; `README.md:223–247`.

The exact scaffold procedure is specified in `tdc/utils/split.py:104–192`: compute atomic Murcko scaffold SMILES directly on each supplied molecule with `includeChirality=False`; group equal strings, including empty strings; omit RDKit-error rows; set training capacity to `int(N_valid * 0.875)` and nominal validation capacity to `int(N_valid * 0.125)`. Construct groups in input encounter order, separate big/small groups using `len(group) > val_size/2 or len(group) > test_size/2`, shuffle each list using Python `random.Random(seed)`, then concatenate big before small. With `frac[2] == 0`, put each whole group into training if it fits; otherwise put it into validation. Returned row order follows those operations. This does not use the v2 science SHA-256 partition or its largest-fragment rule.

The API provides no automatic label-log transformation or censor-aware handling for this task. Its standalone loader defaults to target `Y`, drops missing-target rows and leaves format conversion off unless requested (`tdc/utils/load.py:378–403`; `tdc/single_pred/single_pred_dataset.py:97–121`). Group scoring inherits SciPy defaults for ties, missing values and constant inputs. `evaluate(testing=False)` references undefined `true` in this release and cannot be assumed to supply validation scoring (`base_group.py:206–216`). These behaviours were inspected, not executed or repaired.

**Conclusion about the earlier assumption:** mean/SD aggregation is genuinely implemented, and seeds 1–5 appear in official shipped documentation. They were not invented. What is unsupported is treating “official harness” as a complete experimental configuration that automatically prescribes and executes exactly those five seeds, estimator randomness, training/selection procedures and a fully pinned environment.

## Package/runtime closure

OBSERVED: project [requirements.txt](../requirements.txt) pins only `rdkit==2025.3.6`, `numpy==2.2.6` and `Pillow==12.3.0`. Its SHA-256 is `3f5664c12d1ba27f185cf5a1b7862e92d393439bd2801f3109a770e2c40f402e`. No benchmark dependency lock was found in the experiment. The repository's root `anyway_requirements.txt` concerns tracing integration, not a PyTDC environment.

Package metadata was queried without importing PyTDC or numerical/model libraries:

| Component | Observed experiment environment | PyTDC 1.1.15 source requirement |
|---|---|---|
| Runtime | CPython **3.11.16**, MSC v.1944, 64-bit AMD64; Windows build **26200** | No exact runtime/platform lock established by the source archive |
| PyTDC | **Not installed**; acquired source is **1.1.15** | Version confirmed by `tdc/version.py:22` |
| RDKit | **2025.3.6** | `>=2023.9.5,<2024.3.1` — incompatible |
| NumPy | **2.2.6** | `>=1.26.4,<2.0.0` — incompatible |
| pandas | **3.0.5** | `>=2.1.4,<3.0.0` — incompatible |
| SciPy | **1.17.1** | No exact direct pin; supplies the metric implementation |
| scikit-learn | **1.9.1** | `>=1.2.2`; a lower bound is not a reproducibility lock |
| fuzzywuzzy | **Not installed** | `>=0.18.0,<1.0` |
| tqdm | **Not installed** | `>=4.65.0,<5.0.0` |
| requests | **Not installed** | `>=2.31.0,<3.0.0` |
| setuptools | **79.0.1** | Setup requirement `>=38.6.0`; not an exact build lock |

Declared requirements come from archive `requirements.txt:1–19`, consumed by `setup.py:21–23,38–39`. Some other direct dependencies are exact pins, but the complete transitive dependency set is not locked. Current installed versions are observations, **not** approved benchmark pins.

**UNRESOLVED:** there is no evidence-derived exact compatible runtime/dependency tuple to prescribe today. A future benchmark preregistration must identify the exact PyTDC artifact, Python version/build and platform, RDKit, NumPy, pandas and SciPy versions, all import/runtime dependencies, and any estimator libraries, using a resolved compatible lock with package artifact hashes. It must also fix data-file hashes/order, seeds and run configuration. Source version 1.1.15 and version ranges cannot stand in for that lock. This task neither selects alternative versions nor alters the science environment.

## SAP-ready replacement text — disposition B

> **TDC exploratory benchmark deferred.** Execution of `Clearance_Microsome_AZ` is excluded from the frozen prospective v2 reanalysis protocol. A future TDC benchmark will be documented and preregistered separately before any benchmark model fitting, tuning, prediction generation or performance evaluation. Static inspection of PyTDC 1.1.15 establishes its ADMET benchmark-group retrieval API, scaffold train/validation procedure, automatic Spearman test metric and mean/population-SD aggregation facility. It does not establish a complete reproducible experiment: the required benchmark-group train_val/test files have not been acquired and hash-verified locally, a compatible runtime/dependency lock has not been fixed, and the API leaves consequential run and modelling choices to the caller. The bundled split-seed example [1,2,3,4,5] is not adopted implicitly as a complete configuration. The separate preregistration must freeze the exact package/runtime environment, source and data hashes, group API, supplied test membership, train/validation procedure, split and estimator seeds, run count, representations, label handling, training/tuning/selection rules, metric implementation and aggregation/rounding rules. Until then, no TDC execution or claim of exact benchmark reproduction forms part of frozen v2. Existing standalone TDC acquisition/audit evidence remains unchanged. Any later benchmark is exploratory, is kept separate from the primary science track, does not inform its methodological choices, and is not independent external validation of the overlapping AstraZeneca data.

## Scope and verification

Only this report and a TDC-resolution-status note in [PREFREEZE_EVIDENCE_CLOSURE.md](PREFREEZE_EVIDENCE_CLOSURE.md) are changed by this task. The earlier source specification and other closure findings are preserved. All 18 raw manifest entries passed SHA-256 and byte-size verification. The SAP SHA-256 remains `6a29097ace7b01f89dbe00eedfb7781c4dd515113f98e433fd19d5328d5cfaa9`. This resolves the TDC blocker by deferral, not by asserting that the benchmark has become executable or fully specified. The SAP-ready wording above has not been inserted into the SAP.

TDC_PROTOCOL_NOT_FULLY_SPECIFIED
