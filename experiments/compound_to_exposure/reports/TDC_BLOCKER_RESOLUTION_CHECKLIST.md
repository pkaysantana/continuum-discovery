# TDC benchmark blocker-resolution checklist

2026-09-18; branch `dmpk-compound-to-exposure`. Read-only inspection of the PyTDC 1.1.15 archive, installed distribution metadata, the repository benchmark runner and [TDC_PREFREEZE_CLOSURE.md](TDC_PREFREEZE_CLOSURE.md). No modelling, benchmark, split generation, acquisition or installation was performed. No v1 performance outputs were opened. This checklist selects no analytical defaults and changes neither the SAP nor previous closure statuses.

**Current status: TDC_PROTOCOL_NOT_FULLY_SPECIFIED.** The intended five split seeds are **1, 2, 3, 4, 5**. They appear in the shipped README; they are not automatically enforced by PyTDC. Their relationship to estimator and tuning seeds still needs an explicit decision.

## 1. Missing files and the artifacts that already exist

`<path>` means the directory supplied to `admet_group(path=...)`; its package default is `./data`, relative to the process working directory. A future configuration must resolve it to one recorded location. No new location is selected here.

| Check | Missing file / expected path | Supplier or generator | Completion evidence |
|---|---|---|---|
| [ ] | `<path>/admet_group.zip` | PyTDC's cold-cache constructor downloads Dataverse file **4426004** through `https://dataverse.harvard.edu/api/access/datafile/4426004`. | Preserve the acquired bytes, source identifier, receipt, byte size and SHA-256. The archive is acquisition evidence; it is not required at each runtime once the CSVs exist. |
| [ ] | `<path>/admet_group/clearance_microsome_az/train_val.csv` | Extract unchanged from that group archive. **Do not generate it by splitting the existing standalone `.tab` or ChEMBL data.** | File hash, exact row order, schema, identifiers, row count, duplicates and missing/invalid fields recorded. |
| [ ] | `<path>/admet_group/clearance_microsome_az/test.csv` | Extract unchanged from the same group archive. The train/validation splitter does not generate this file. | Same evidence, plus fixed test membership and its disjointness from train_val verified. Test labels are not used to choose protocol settings. |

No group archive or either CSV was found in the experiment, including ignored/hidden files. Earlier closure checks also searched workspace data and the user's Downloads directory. The package does **not** require separately downloaded `train.csv` and `valid.csv`: `get_train_valid_split()` returns those in memory for a supplied seed. Recording their row membership/hashes later is a reproducibility artifact, not a missing upstream download.

Already present, and **not replacements for the missing group files**:

- `data/raw/tdc/pytdc-1.1.15.tar.gz`: source SHA-256 `cd6164859af7b9b6f60e0c6d6e50679eacaffd09cfdea1acfc8bb7360e8e2205`.
- `data/raw/tdc/clearance_microsome_az.tab`: standalone dataset, Dataverse **4266186**, SHA-256 `4c9047dc1860cc05d5bdc09aa9cfef86a40740605c2ff06990b1fceb6085db9d`.
- `splits/TDC_OFFICIAL_SPLIT.csv`: existing local artifact, 125702 bytes, SHA-256 `b74626353c2b8d41c6d4da0823ace0f5ceee4f2681e5ac7d340b6a06c8945aff`. Its filename does not prove equality with the group harness's fixed test set or seed-specific train/validation partitions. Only its existence and bytes were checked here; no performance was inspected.

- [ ] Verify the group archive/CSV hashes before trusting a cache. `bm_download_wrapper()` trusts an existing `admet_group` directory without checking completeness or hashes; merely creating that directory can suppress downloading.
- [ ] Keep an input manifest tying the CSVs to their source archive. No such verified group-data manifest currently exists. Preserve the existing raw acquisition unchanged.

Source: archive `tdc/utils/load.py:249–276`, `tdc/metadata.py:1199,1206`, `tdc/benchmark_group/base_group.py:90–155`.

## 2. Environment incompatibilities and unresolved runtime support

Observed experiment runtime: **CPython 3.11.16, MSC v.1944, AMD64, Windows build 26200**. PyTDC is not installed. The source archive pin is **1.1.15**. The project requirements pin RDKit 2025.3.6, NumPy 2.2.6 and Pillow 12.3.0; they do not define a benchmark environment.

All 19 direct distribution requirements in the pinned PyTDC archive were compared with installed package metadata:

| Package | PyTDC 1.1.15 requirement | Current state | Blocker/action |
|---|---|---|---|
| PyTDC | `1.1.15` source under review | Not installed | [ ] Provision the chosen compatible benchmark environment using this exact artifact/version. |
| numpy | `>=1.26.4,<2.0.0` | **2.2.6** | [ ] Resolve incompatible version. |
| pandas | `>=2.1.4,<3.0.0` | **3.0.5** | [ ] Resolve incompatible version. |
| rdkit | `>=2023.9.5,<2024.3.1` | **2025.3.6** | [ ] Resolve incompatible version; scaffold membership can depend on it. |
| accelerate | `==0.33.0` | Missing | [ ] Resolve declared dependency. |
| dataclasses | `>=0.6,<1.0` | Distribution missing | [ ] Resolve the package declaration against the chosen Python version; Python 3.11 already includes the standard-library module. This is not evidence that the module itself is unavailable. |
| datasets | `<2.20.0` | Missing | [ ] Resolve declared dependency. |
| evaluate | `==0.4.2` | Missing | [ ] Resolve declared dependency. |
| fuzzywuzzy | `>=0.18.0,<1.0` | Missing | [ ] Resolve declared dependency; used in name lookup. |
| huggingface_hub | `>=0.20.3,<1.0` | Missing | [ ] Resolve declared dependency. |
| openpyxl | `>=3.0.10,<4.0.0` | Missing | [ ] Resolve declared dependency. |
| requests | `>=2.31.0,<3.0.0` | Missing | [ ] Resolve declared dependency; used for acquisition. |
| scikit-learn | `>=1.2.2` | **1.9.1**, satisfies range | [ ] Freeze an exact compatible version; satisfying a range is not a lock. |
| seaborn | `>=0.12.2,<1.0.0` | **0.13.2**, satisfies range | [ ] Include the resolved version in the lock. |
| tqdm | `>=4.65.0,<5.0.0` | Missing | [ ] Resolve declared dependency; used by the scaffold splitter. |
| transformers | `>=4.43.0,<4.51.0` | Missing | [ ] Resolve declared dependency. |
| cellxgene-census | `==1.15.0` | Missing | [ ] Resolve declared dependency and platform availability. |
| gget | `>=0.28.4,<1.0.0` | Missing | [ ] Resolve declared dependency. |
| pydantic | `>=2.6.3,<3.0.0` | Missing | [ ] Resolve declared dependency. |
| tiledbsoma | `>=1.7.2,<2.0.0` | Missing | [ ] Resolve declared dependency and platform availability. |

Additional runtime items:

- [ ] Freeze **SciPy** exactly. Installed **1.17.1** supplies the inspected Spearman implementation; PyTDC has no exact direct SciPy pin. This is an unresolved version choice, not a demonstrated incompatibility.
- [ ] Freeze Python version/build, OS/architecture, the complete resolved transitive dependency set and package artifact hashes. Setuptools is currently **79.0.1**, satisfying the source's `>=38.6.0` setup requirement; the build environment is not locked.
- [ ] Verify that the chosen Python/platform supports the full pinned distribution and imports. No Windows or Python-version incompatibility beyond the package version conflicts above has been demonstrated. Conversely, compatibility has not been established: installation/import checks were not run. Potential missing wheels or transitive conflicts must be reported if encountered, not assumed now.
- [ ] Record thread/parallelism configuration and numerical backends for the selected estimator; decide the required reproducibility tolerance. Python's seeded scaffold shuffling, RDKit parsing, pandas CSV interpretation and SciPy ranking all depend on the frozen runtime.
- [ ] Keep this resolution separate from the primary science environment. A separate environment can address TDC constraints without changing its existing RDKit/NumPy pins. No replacement versions or operating system are selected by this checklist.

These are package-metadata findings, not proof that every absent distribution is exercised by microsome scoring. Root `tdc` initialization imports additional modules (`tdc/__init__.py:1–5`), so assuming that only RDKit and SciPy are needed would not establish an as-shipped runnable package. Source: archive `requirements.txt:1–19`, `setup.py:21–23,38–39`.

## 3. What the current repository implementation does

Read-only inspection of `scratch/run_tdc_benchmark.py` found the following. These are **legacy implementation choices, not approved defaults for the new benchmark**:

| Existing implementation | Why it does not close the blocker |
|---|---|
| Reads `splits/TDC_OFFICIAL_SPLIT.csv`; asserts train/valid/test Ns **771/110/221** (lines 45–55). | No call to the group loader or five seeded group splits. Those assertions are not evidence of the group archive's allocation. |
| Uses `smiles` and `standard_value` columns (lines 57–67). | Requires a verified mapping to the group's `Drug` and `Y` fields and row identity before reuse. |
| Seven descriptors: MolWt, MolLogP, TPSA, H-donors, H-acceptors, strict rotatable bonds, FractionCSP3; Morgan radius 2, 2048 bits, **chirality enabled** (lines 18–41). | Representation and chirality choices come from repository code, not PyTDC. They cannot be silently inherited from this runner or from the primary v2 science protocol. |
| Mean and median constants; Ridge and Random Forest on each representation (lines 78–108). | PyTDC does not prescribe model families, baselines or which pipelines may access test data. |
| StandardScaler on descriptor inputs for both model families, fitted on train; no explicit imputer (lines 110–121). | Scaling, non-finite handling and fitting scope require an explicit benchmark policy. |
| Ridge alpha `{0.1,1,10}`; RF max_depth `{10,None}`, 100 trees; estimator `random_state=42` (lines 93–100,127–129,156–158). | No intended-seed loop; grids, fixed constructor settings and hidden library defaults need review and freezing. |
| Selects by validation **MAE**, tie tolerance `1e-12`, then refits on **train only** (lines 76,125–160). | The official test metric is Spearman; validation objective, tie-breaks and final refit population are caller choices. Different validation and test metrics are possible but must be deliberate. |
| Evaluates every retained pipeline directly with SciPy and computes other metrics (lines 170–194). | It does not call `group.evaluate()`/`evaluate_many()` or reproduce their rounding/aggregation. A direct coefficient calculation alone is not the entire harness protocol. |

Runner SHA-256: `983ae0453dd22d8e729aef989db8aa838d597008312313689fe71089b89da410`. It was neither imported nor executed. Its results directory was not read.

## 4. Consequential caller-controlled settings to freeze

“Supported options” below distinguishes package-supported calls from externally implemented analytical choices. PyTDC accepts supplied predictions and therefore does **not** define a closed menu of representations, models or tuning procedures. Options not prescribed by the package remain decisions for the benchmark owner.

| Check / setting | Supported behaviour or currently available options | Why a decision matters / acceptance condition |
|---|---|---|
| [ ] API and data identity | Group API `tdc.benchmark_group.admet_group(...).get("clearance_microsome_az")`; standalone `tdc.single_pred.ADME(...)` is a different retrieval/split route. | Record which claim is intended. Group-harness reproduction requires its CSVs and fixed test set; the standalone default cannot silently substitute. |
| [ ] Split method | Registered group `split_type="default"` resolves to `scaffold`; explicit `"scaffold"` reaches the same branch. The generic group class also has random/combination/group branches, but these are not the registered microsome convention and some require other schemas. | For an as-shipped microsome claim, preserve the registered scaffold path. Any override is a separately declared design change, not a missing default to guess. |
| [ ] Split seeds and run identity | Intended list **[1,2,3,4,5]**; API otherwise accepts caller seeds. | Freeze exactly five named runs and preserve one supplied test membership across them; record seed-specific train/validation memberships. |
| [ ] Estimator and tuning RNGs | Use the corresponding split seed, a fixed separate seed, or an explicitly enumerated mapping. The legacy runner uses 42. | These are different repeated-run experiments. Define seeds for every stochastic estimator, search, sampling and transform; do not assume the split seed controls them. |
| [ ] Structure policy | Package splitter parses supplied molecules directly. External feature code may use deposited structures or an explicitly specified transformation. | Specify salts/fragments, stereochemistry, tautomer handling and invalid structures. Feature choices must not silently change benchmark split membership or modify source files. |
| [ ] Representation | Current runner supports its seven descriptors and binary Morgan radius 2/2048/chiral. PyTDC itself supplies no feature set. Retain, replace or restrict only by explicit preregistration. | Freeze exact descriptors/order, fingerprint algorithm/version, radius, length, chirality, binary/count form and any concatenation. No primary-science representation is automatically inherited. |
| [ ] Label use and output scale | Harness reads numeric `Y` unchanged; an external training transform is technically possible. | Freeze raw versus transformed training target, inverse transform and prediction scale, handling of bare boundary numbers and population inclusion. Different scales alter fitting and tuning even when positive monotone transforms preserve rank. No restoration of missing qualifiers is supplied by TDC. |
| [ ] Feature preprocessing | No harness default. Current runner scales descriptors for both families; future code could explicitly specify scaling/imputation/feature filtering per pipeline. | Freeze exact operations, fitting population, zero-variance/non-finite policy and leakage controls. None may be fitted using validation/test labels or test-derived parameter estimates. |
| [ ] Models and baselines | Current runner offers Ridge, RF, mean and median baselines. Other models would require new implementation and explicit authorization. | Freeze candidates, representation/model pairings and all consequential constructor parameters, including solver, tolerance, iterations, intercept, RF tree/depth/feature/leaf/bootstrap settings and parallelism. Explicitly record library defaults that remain in use. |
| [ ] Tuning | No harness search. Current runner uses its small exhaustive grids; fixed settings or a separately specified search are possible external designs. | Freeze search space, procedure, budget, RNG, training/validation allocation and handling of convergence/failure. Do not infer a new search from “official harness.” |
| [ ] Validation objective and tie-breaks | Current runner minimizes MAE. Standalone `Evaluator(name="spearman")` or an explicitly verified direct metric implementation can score validation; broken `group.evaluate(testing=False)` cannot be relied upon. | Decide objective, direction, precision/tolerance and deterministic tie-break sequence. Choosing Spearman merely to match test scoring is still an analytical choice, not made here. |
| [ ] Selection scope | Select settings separately per seed or use one configuration chosen by a prespecified train/validation-only aggregation rule. | Specify whether selection is per representation/model/run or across them; do not use test scores to select winners. |
| [ ] Final fit population | Train only (legacy runner) versus refit a selected pipeline on train_val. PyTDC README permits training and/or validation data for fitting. | Freeze which records fit the final model and every fitted preprocessing step, and when validation ceases to be held out. |
| [ ] Test-access/reporting rule | One preselected pipeline or a fixed prespecified collection of benchmark pipelines. | Freeze which prediction arrays are scored and reported; prevent test-driven changes or reporting only the best test result. |
| [ ] Test metric | Official group metric is fixed: signed Spearman, higher is better; `evaluate()` auto-selects it and rounds to three decimals. | No official-metric choice is missing. Additional metrics, if wanted, require separate prespecification and do not replace the official score. |
| [ ] Aggregation route | Default `evaluate_many(preds)` versus its `results_individual` bypass; the latter can receive differently rounded numbers. Single-run `evaluate()` also exists but does not implement the intended five-run summary. | Freeze the route. Exact default-harness aggregation uses mean and population SD (`ddof=0`) of per-run rounded scores, then rounds both to three decimals. Raw-score aggregation/sample SD are different reporting conventions. |
| [ ] Invalid data, NaNs and constant predictions | Source behaviours are listed below; alternative omission, imputation or retry policies would be caller interventions. | State when execution stops, what is reported as undefined, and whether any repair is permitted. Do not silently reduce evaluation N or replace undefined Spearman with zero. |
| [ ] Failed runs and reproducibility | No harness retry/seed-replacement policy; `evaluate_many()` only checks input count. | Freeze failure reporting, deterministic same-run restart conditions, and whether all five valid runs are required. Do not replace failed seeds or use only successful runs without a prior rule. |

## 5. The five seeds: enforcement points

The intended split seeds are **1, 2, 3, 4, 5**, from archive `README.md:230,236`. Their enforcement requires caller code; the package does not provide a full experiment runner.

- [ ] Store the exact ordered list in the benchmark configuration and assert that it has exactly these five distinct integers.
- [ ] For each run, pass that integer explicitly to `group.get_train_valid_split(seed=seed, benchmark="clearance_microsome_az", split_type="default")`. Use the same verified `test.csv` for all runs.
- [ ] Record run ID, split seed, input hashes and resulting train/validation/test row IDs. Check disjointness/completeness and that repeated construction under the frozen environment reproduces membership. Equal memberships for different seeds are not automatically an error if the algorithm happens to yield them.
- [ ] **User decision remains:** define the estimator/search seed mapping. Enforce it in every estimator's `random_state` and every separate generator used by training/search. Global NumPy/Python seeds alone do not seed all explicit RNG objects. Remove an unreviewed hardcoded 42 from any future runner; do not change the historical runner in place as part of this checklist.
- [ ] At aggregation, assert one completed result per intended run/seed and the same evaluated test-row order. The harness accepts any list of at least five dictionaries and cannot detect repeated seed identities. Do not infer run identity from list length alone.

No seed loop, RNG change or split was implemented here.

## 6. Remaining ambiguities and behaviours that are already fixed

| Area | Known implementation | What must still be resolved |
|---|---|---|
| Overall split fractions | Group holds out the supplied test file. On train_val, requested fractions are **0.875/0.125/0.0**. Atomic Murcko (`includeChirality=False`) groups are shuffled with the supplied seed and packed whole into training up to `int(N_valid*0.875)`; overflow goes to validation. | Obtain files, record exact test fraction and each seed's realised train/validation counts. **771/110/221 and exact 70/10/20 are not established group facts.** |
| Scaffold handling | Empty scaffold strings pool naturally; source uses whole supplied molecules, not the science-track largest-fragment rule. RDKit exceptions are omitted before train/validation assignment. | Verify actual parse failures and record omitted IDs with reasons; decide whether any occurrence stops the benchmark or is accepted as documented package behaviour. Do not repair structures silently. |
| Row ordering and duplicates | pandas CSV loading and source encounter order feed group generation; test predictions are positional. No ID-based alignment or duplicate-resolution policy is supplied by `get()`/`evaluate()`. | Audit IDs, duplicate structures/rows, cross-partition overlap and schema. Preserve source order and explicitly verify prediction alignment. Define how an anomaly is escalated rather than silently deduplicating. |
| Missing target data | Standalone loader drops missing `Y`; group `get()` simply reads CSVs and does not apply that standalone filter. | Check missing/non-finite labels in both group files. Freeze a failure/reporting policy without assuming the standalone cleaning applies. Never impute test labels. |
| Missing/invalid features | Harness supplies no feature imputer; legacy runner asserts molecule parsing succeeds and lacks explicit feature-NaN handling. | Select and freeze pipeline-specific handling and fitting scope. Training feature imputation is a model choice, not package evidence. |
| Spearman definition | Calls SciPy's signed coefficient, default tie ranking, no supplied `nan_policy`; p-value discarded. In the inspected SciPy 1.17.1 source, NaNs propagate and constant input produces an undefined coefficient. | Freeze the actual compatible SciPy version and how undefined scores are reported. Mean/median constant baselines necessarily have undefined Spearman when predictions are constant; do not treat that as evidence of measured zero rank correlation. No baseline choice is made here. |
| Aggregation and missing runs | Default `evaluate_many()` uses `np.mean` and `np.std(ddof=0)`; no `nanmean`/`nanstd` or seed validation. Per-run score rounding occurs before aggregation. | Freeze undefined-score/run-failure treatment and selected API path. SD is run dispersion, not a confidence interval. No rounding or averaging of predictions may silently replace score aggregation. |
| Validation scoring | `evaluate(testing=False)` references undefined `true` (`base_group.py:216`). | Choose a documented validation scorer outside that broken branch or explicitly version/hash a reviewed patch. A direct scorer and a source patch are different implementation routes; neither is selected here. |
| Modelling/preprocessing | No harness-prescribed model, search, feature construction, target transform, train_val refit or selection objective. | Complete the caller-decision table before fitting; source inspection alone cannot close these choices. |

Source: archive `tdc/utils/split.py:104–192`, `tdc/benchmark_group/base_group.py:90–257`, `tdc/utils/load.py:378–403`, `tdc/evaluator.py:413–418,471–488`. SciPy 1.17.1 source inspected without invoking it: `scipy/stats/_stats_py.py:5169,5366–5397,5405`.

## 7. Minimum path to protocol-ready — no performance required

1. [ ] **Acquire and verify the actual group inputs.** Retain the archive and two unchanged task CSVs, their hashes, schema and row-order/membership evidence. This is an acquisition action, not something performed by this checklist.
2. [ ] **Create a compatible isolated benchmark environment and exact lock.** Resolve all package constraints, runtime/platform support and transitive dependencies; record artifact hashes. Run dependency/import checks without fitting or evaluating predictions. Do not alter the science environment.
3. [ ] **Obtain explicit decisions for every open caller setting above.** Write a separate benchmark protocol/configuration. Freeze the five split seeds and the independent estimator/search seed mapping; model and preprocessing choices cannot be supplied by PyTDC documentation.
4. [ ] **Implement or adapt a benchmark-specific runner after those decisions.** It must consume the verified group files, enforce seeds/row alignment, use the chosen validation path, reproduce official test metric/rounding/aggregation and report failures as specified. Do not carry forward the historical local split, seed 42, grids or MAE selection merely because code already exists.
5. [ ] **Perform only authorized non-performance checks before declaring readiness.** Check actual split construction/membership/counts for all five seeds under the locked environment, deterministic replay, scaffold separation and required exclusions. Use synthetic scorer tests to verify rounding, NaN/constant-input behaviour and aggregation. Keep fit/predict and real benchmark scoring unreachable during these checks. These are future checklist items, not actions executed now.
6. [ ] **Review and freeze the complete specification and artifacts before execution.** Record exact versions/hashes and confirm no unresolved analytical choices remain. Then the separately documented benchmark can be protocol-ready without having generated any predictive performance. This does not reinstate it into the frozen v2 SAP automatically; that document remains untouched.

A model run is **not** a prerequisite for protocol readiness. The missing requirements are verified inputs, a compatible frozen environment, explicit analytical decisions and a checked implementation—not a favourable result. Until these boxes are resolved, retain **TDC_PROTOCOL_NOT_FULLY_SPECIFIED**.
