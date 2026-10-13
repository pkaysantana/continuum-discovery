# GSK clearance development: Sprint 3B

**Execution readiness: NO-GO for real-data modelling. Implementation and synthetic
validation only.** `execution_gate.json` remains `NOT_READY`; no real development
export or approved receipt exists. This sprint did not run real preparation,
inspect/convert protected outcomes, fit real-data models, or execute V2/V3A.

Branch: `dev/gsk-provenance-hardening-2026-10-13`.
Starting/Sprint 2 checkpoint: `773ef309c882f15de462cfa6d35032ef407b85e5`.
Sprint 1 harness checkpoint: `1aa7f6e557b9c0d8f28653f5ef34092d1d9f10e3`.
Changes are uncommitted pending separate approval. The previous branch and
checkpoint are preserved. No historical scientific file is modified.

## Frozen prospective experiment

- Exactly 582 `cv / INTERIOR_OBSERVED` compounds from the immutable V2 partition.
- Five predetermined scaffold folds: 115 / 120 / 115 / 117 / 115; 448 scaffolds.
- R1: MolWt, MolLogP, MolMR, TPSA, NumHDonors, NumHAcceptors,
  NumRotatableBonds (Strict), RingCount, NumAromaticRings, NumAliphaticRings,
  FractionCSP3, HeavyAtomCount. Definitions remain imported from the unchanged
  historical `src/representations.py`; its byte hash is recorded with code hashes.
- R2: binary Morgan radius 2, 2,048 bits, `useChirality=False`.
- Full supplied molecules retained for features, without desalting, neutralisation
  or tautomer normalisation. Grouping uses largest-heavy-fragment/nonchiral Murcko,
  canonical-SMILES tie-break and shared `__ACYCLIC__` group.
- Four learned models: each representation with Ridge and Random Forest.
  Ridge: alpha 1, lsqr, tolerance 1e-4, maximum 10,000 iterations, intercept.
  RF: 100 trees, sqrt features, minimum leaf 3, unlimited depth, bootstrap,
  squared-error criterion, minimum split 2, seed 20261013, n_jobs 1.
- 20 learned fits / 1,000 RF trees; no optimisation, selection or refit on all data.
- Descriptor medians fitted inside training folds; Ridge additionally drops
  training-constant columns and standardises. Morgan is not imputed/scaled.
- Original and standard endpoint values must agree exactly as Decimal values
  after the explicit unit factor: microL/min/mg and mL/min/g are numerically equal.
  The recognised standard unit string is `mL.min-1.g-1`. Both qualifiers must be
  empty. Unknown units/qualifiers are rejected, never inferred as equivalent.
  Standard CLint must be finite and strictly between 3 and 150; log10 once.
- Mean/median training-only log10 baselines. Pooled and per-fold MAE, RMSE,
  Pearson R, Spearman rho and R-squared. Undefined correlations are null.

## Provenance and independent evidence

`input_manifest.json` contains **outcome-free partition metadata only**: exact
activity ID, compound ID, deposited full SMILES, scaffold and fold for 582 members,
plus the 250 protected activity/compound IDs (covering the 149 regression holdout
records). It was constructed from the unchanged partition, not from outcome CSVs.
Only the HLM CSV header was inspected for schema during implementation.

The manifest records each role separately:

| Role | Revision |
|---|---|
| Source acquisition recorded in Git | `13715550adad0a628e92da6cf34568000ddbc797` |
| Partition revision | `0e4248ff779d74b4a54abbea608c80b6897f33ff` |
| Historical V2 execution | `31693d204420fa547a96079ff11988058d133406` |
| Historical evidence snapshot | `773ef309c882f15de462cfa6d35032ef407b85e5` |
| Later V3A starting checkpoint, not data-generation evidence | `49e94153a78224eb274ace540085d7a4d483605f` |

Acquisition commit means the commit recording data; it does not prove the exact
generating process. Current execution revision, dirty state and actual code bytes
are separately captured at runtime, not replaced with a historical placeholder.

Stage A verifies authority-manifest byte hashes and compares their bytes to Git
objects at the fixed evidence revision. The original V2 `.started.json` manifest
supports all three interim source hashes; `selection_manifest.json` supports the
partition hash. The secondary assay hashes are retained as historical evidence,
but only CHEMBL3301370 is consumed for preparation. Secondary outcome CSVs are no
longer scanned for matching activities.

Digest semantics are explicit:

- `partition_file_sha256`, `source_file_sha256`, `export_sha256`, `receipt_sha256`:
  SHA-256 of exact file bytes, including line endings.
- `assignments_sha256` in the input manifest/receipt: canonical JSON of the full
  member metadata list sorted by activity ID, including identity and folds.
- `id_scaffold_fold_sha256` in bundle provenance: canonical JSON of the compound-ID
  to scaffold/fold mapping. Checked independently, not treated as a file hash.
- `records_sha256`: canonical JSON of the ordered export records.
- `input_manifest_canonical_sha256`: canonical JSON of the manifest object,
  explicitly distinct from the pretty-printed repository file's byte hash.
- Canonical JSON uses sorted object keys, compact separators, default ASCII
  escaping, UTF-8 encoding, no NaN/Infinity, and preserved array order.

The historical partition file hash remains
`971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a`.
The complete historical subtree remains Git tree
`d92568a6ff4dbbebe3f8ceb1f6f46bf9fba0e952` at the starting checkpoint.

## Stage A: preparation, separately authorised

`extractor.extract` requires `approve_preparation=True`, an approval reference and
a new destination. This is a procedural acknowledgement, not proof of permission.
`skip_hash_verification=True` is always rejected, including for tests.

Before opening outcome-bearing input, verify partition hashes, exact membership,
full identities/scaffolds/folds and activity-ID/compound-ID holdout collisions.
Within the source, verify matching activity/compound identity, assay and full
canonical molecular identity before endpoint conversion. Duplicate/missing
observations fail. Same-scaffold substitutions fail. Original/standard endpoint
equivalence is checked explicitly; it has **not yet been established on real
development outcomes in this sprint**. Any failure stops preparation and requires
review; it does not authorise changing scientific rules.

Hash verification and parsing use the same captured bytes. Preparation creates a
new directory containing `export.json` and `receipt.json`, without overwriting.
The receipt records source/partition hashes, endpoint checks, manifest digest,
revision roles, actual preparation code and environment. No receipt is an
independent attestation merely because a helper wrote it.

**Access limitation:** hashing reads all source bytes. `csv.DictReader` parses
excluded outcome strings into Python objects before filtering. Only permitted
development values are numerically converted and returned/exported. This does
not provide physical or memory isolation. Authorising Stage A must acknowledge
its mixed-source read/string-materialisation boundary. Stage A was not run here.

## Stage B: modelling, separately gated

`export.approved_export` reads the fixed, review-controlled `execution_gate.json`.
It requires separately approved export and receipt byte hashes, manifest digest,
configuration digest, exact running-code hashes/revision, and deployment evidence
for filesystem isolation and the memory limit. `harness.evaluate` checks any
development caller's bundle against that pinned export, so a caller cannot supply
a different internally consistent receipt or use approval=True alone to proceed.
Production accepts only the frozen Configuration defaults. The real runner is
`execution.run_development`; it uses the external supervisor and Stage B worker.

These checks establish **local provenance consistency against reviewed evidence**,
not cryptographic authentication. Code, Git objects, configuration and gate files
must be trusted and protected by ordinary review/permissions. A user able to edit
code/gate files or run arbitrary Python can bypass application controls.
Synthetic APIs intentionally accept fixture manifests and SYN_ IDs; prefixes
cannot prove synthetic origin. Keep those APIs in the trusted testing workflow.

Genuine Stage B isolation requires a separate account/OS policy or isolated
execution environment containing only the development export, reviewed code and
dependencies. Do not expose the full checkout, backups, historical result files,
or `.git`: Git objects can also recover protected outcomes. Mount/copy only the
unchanged representation helper under its import path, not its parent data tree.
A code-only deployment records unavailable Git state honestly and binds code
bytes to the separately reviewed revision via the gate.

Changing working directory is not isolation. The synthetic subprocess test
demonstrates that an absolute path outside its working directory remains readable.
No genuine filesystem isolation is installed or claimed here. Hash-pinned
deployment evidence is a review record, not a live enforcement mechanism.

## Outputs and actual resource controls

`execution.run_supervised` exclusively creates the requested run directory and
assigns a UUID. An existing destination fails before launch. The worker can write
only the candidate result under the intended lifecycle; the supervisor publishes
the successful result after worker exit and validation. This is orchestration,
not a defence against arbitrary malicious worker code with the same OS rights.

Artifacts: input-manifest/receipt snapshots; start/exit/runtime/code receipts;
stdout/stderr; requested configuration and actual fitted estimator parameters;
descriptor nonfinite counts; imputer statistics, variance masks and scaler
statistics; aligned activity/compound IDs, observed log10 values and all six OOF
prediction vectors; per-fold/pooled metrics and baseline constants; artifact hashes.
The result writer recomputes metrics and checks alignment and fit completeness.

Only the supervisor writes `COMPLETE.json`, after successful exit, validation,
serialization and artifact-hash verification. `FAILED.json` and failure artifact
hashes are written on handled errors/interruption/watchdog expiry. If the
supervisor itself is forcibly killed or storage fails, a receipt may be incomplete;
absence of COMPLETE always means incomplete/failed, never success. No auto-resume
or overwriting an earlier run is implemented.

| Constraint | Status |
|---|---|
| CPU-only estimators, RF n_jobs=1 | Implemented |
| OMP/OpenBLAS/MKL environment limits = 1 before worker import | Implemented by supervisor |
| 20 fits, 1,000 trees in real configuration | Frozen/validated |
| External 900-second worker wall-clock watchdog | Implemented; synthetic slow worker terminated |
| Entire preparation plus result-publication duration <=900 seconds | Not claimed; timeout covers worker execution |
| 2 GB memory ceiling (2,000,000,000 bytes; decimal, not a larger GiB allowance) | **Not enforced by this supervisor; NO-GO** |
| Protected-source filesystem isolation | **Not implemented in this checkout; NO-GO** |

No portable Windows memory sandbox was added. A separately demonstrated external
memory limit is required; evidence must match the exact deployment. Receipts state
`memory_limit_enforced=false` for the supervisor. Do not change the gate to APPROVED
based only on a self-written evidence file or an intended limit.

## Sprint 3A finding disposition

| Finding | Sprint 3B disposition |
|---|---|
| F01 | False memory-isolation claim removed; two stages implemented; genuine OS isolation still blocked |
| F02 | Skip prohibited; absent/skipped receipts rejected; receipt retained through execution |
| F03 | Fixed reviewed export/receipt pins required; caller self-consistency insufficient; local trust limits explicit |
| F04 | Activity/compound/full-identity checks and early exclusions implemented |
| F05 | File hashes separated from recomputed assignment digests |
| F06 | Historical evidence anchored to committed manifests; revision roles separated |
| F07 | Exact endpoint/qualifier/unit verification implemented; real-data equivalence pending authorised preparation |
| F08 | Exclusive writer, aligned OOF results and comprehensive receipts implemented |
| F09 | External worker watchdog implemented; memory enforcement and deployment isolation unresolved |
| F10 | Original 13 extractor test intentions retained with specific failures; additional adversarial coverage |
| F11 | Historical Python corrected to 3.11.16 from the V2 execution manifest |

## Synthetic validation and environment

No packages installed. Existing project-local `.venv` only.

| Component | Current runtime | Historical evidence |
|---|---|---|
| Python | 3.12.10 AMD64 | V2 execution manifest: 3.11.16 |
| NumPy | 2.5.3 | Historical pin: 2.2.6 |
| SciPy | 1.18.1 | Historical pin: 1.17.1 |
| scikit-learn | 1.9.1 | Historical pin: 1.9.1 |
| RDKit | 2026.9.1 | Historical pin: 2025.3.6 |

Runtime OS: Windows 11, build 26200. Numerical identity across environments is not
claimed. The existing Morgan API emits deprecation warnings; synthetic invalid-
SMILES tests intentionally emit RDKit parse diagnostics. Neither warrants changing
the frozen representation during this sprint.

Run the complete development-only suite (never repository-wide scientific runners):

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s application_development/gsk_clearance -t . -v
```

Validation history on 2026-10-13:

- Initial harness + rewritten/extended extractor run: 35 tests, exit 0.
- Initial execution tests: 17 tests, exit 1; an interruption during runtime
  metadata collection escaped failure-receipt creation. Moved metadata collection
  inside the failure handler; retained the regression test.
- Subsequent complete suite: 55 tests, exit 0 (8.612 seconds).
- Complete suite including writer-path protection: 56 tests, exit 0 (9.022 seconds).
- **Final complete suite: 57 tests, 0 failures, exit 0 (9.133 seconds).** This
  comprises 11 harness, 24 extractor and 22 execution tests, including rejection
  of a relaxed resource contract. All fitting used invented synthetic outcomes.
- Metadata-only check of the committed authority manifests and all 582 partition
  members/digests/fold counts: PASS, exit 0. No real outcome file was parsed.

## Scientific limitations and next safe action

This is exploratory development evaluation, not a V1 reproduction, V2 rerun or
independent validation. V1 used seven descriptors, chiral fingerprints, different
grouping, N744 and tuning. Intended V2 used grid search, 500 trees and seed 0.
Executed V2 routed all candidates to Morgan and did not apply recorded candidate
parameters as intended; representation-selection provenance is invalid. The
historical bootstrap CI provenance remains unresolved. Prior V1/V2 analysis must
remain disclosed. Do not reuse protected outcomes for a new comparison.

The 582-member cohort is selected by observed outcome range; it cannot estimate
performance on unscreened compounds. Range membership is unknown before assay;
blank qualifiers are a dataset-specific working inference, not universal equality.
Scaffold separation does not imply fingerprint novelty. No claim about in-vivo
clearance, exposure, clinical efficacy or statistically significant improvement.

**Next safe action:** independently review this uncommitted implementation and the
synthetic results. Then separately authorise an isolation/memory demonstration
using synthetic sentinels, and separately approve Stage A preparation with its
explicit access limitation. Inspect the resulting development-only receipt and
pin exact export/receipt/code/configuration hashes before any modelling approval.
Do not run preparation or open the real execution gate as part of Sprint 3B.
