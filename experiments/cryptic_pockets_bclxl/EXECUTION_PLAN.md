# BCL-XL execution plan

## STATUS: FROZEN — PREFLIGHT COMPLETE — READY FOR EXECUTION

This document is a preregistration-grade freeze. The environment lock has been produced, tool wrappers implemented and tested, and all `BLOCKED-NOT-MEASURED` fields have been filled with measured values.
The test suite has been re-run successfully.

---

## 1. Preregistration integrity — VERIFIED

| Item | Value |
| --- | --- |
| Branch | `ep4-v2-oncology-pocket-benchmark` |
| Preregistration commit (anchor) | `ff685f115eaee9993e174bdd793f137c8a03c316` |
| Anchor tag | `cryptic-pocket-bclxl-preregistered-v1` (annotated tag object) |
| Anchor commit date | 2026-09-16 12:25:09 +0100 |
| Anchor commit subject | `preregister BCL-XL cryptic-pocket reproduction benchmark` |
| HEAD at review | `edcc114ef7e73ca3bc462869e10b3a58c3b3051a` (`record BCL-XL preregistration anchor SHA`) |
| Working tree | clean (`git status --porcelain` empty) |
| Anchor contents | 310 files, 160175 insertions |

**No detector results predate the anchor.** Verified two independent ways:

1. A filesystem search for detector output signatures (`pocket_report*`,
   `*_predictions*`, `*predictions.csv*`, `*residues.csv*`, `*p2rank*`,
   `*lacuna_run*`, `*detector_run*`) outside `.venv`/`.cache` returns only
   **read-only upstream source snapshots** under `manifests/source_review/`
   (`compare_p2rank.py`, `compare_p2rank_coach420.py`, `p2rank_detector.py`,
   `coach420-p2rank.ds`). No output artefacts.
2. Every run receipt in `manifests/runs/` carries one of these actions only:
   `acquire`, `apply-amendment`, `archive-core-v0`, `archive-pre-review`,
   `environment`, `evaluate`, `inspect`, `matched-core`, `overlap-audit`,
   `preflight`, `source-review`, `source-review-extra`, `test`, `verify`.
   There is no detector action of any kind.

Because the working tree is clean at `HEAD` and all scientific inputs are tracked
in the anchor commit, the input bytes are fixed by Git's own content addressing.
This is an independent check on the recorded SHA-256 values, obtained without
recomputing them.

## 2. Inputs and hashes (from the anchor; recorded, not recomputed)

| File | Bytes | SHA-256 |
| --- | --- | --- |
| `data/raw/1LXL.cif` | 349903 | `03a4e441063e7f832999f9a2cfdd376bc5366a543afae202c7f0608955dcb96c` |
| `data/raw/2YXJ.cif` | 324444 | `5300ddf32f42624dd5da03cf1b2beee63d224542ad46bb6bdf055f28bfa969a4` |
| `data/processed/apo_matched_core.pdb` | 90309 | `b0d20bfd4907b92929161c78790051471de261a917371b40da3aa418a3d64693` |
| `data/processed/holo_matched_core_no_ligand.pdb` | 90309 | `8162ea71785ea6e6ecc75d3be07bca42852cd9eacbcbe75f4039f7423a255ea4` |
| `data/processed/comparison_reference.json` | 22827 | `9eb5472a071d1765048eca179c63e2e88c80ab391ac2e57787aca76143fb962c` |

**Matched-core parity is atom-level, not merely residue-level.** Both state files
are 90309 bytes and 1118 lines, with identical `ATOM` serials, atom names,
residue names and author numbering (1113 atoms, 137 residues, chain A, holo
author numbering), differing only in the fixed-width coordinate and B-factor
fields. Apo B factors are NMR-scale (≈0.5), holo are crystallographic (≈49), and
occupancies are 1.00 — confirming the amendment-6 correction that B factors are
preserved rather than zeroed. This is a stronger guarantee of "same structural
input" than the protocol claims, and it should be asserted by the wrapper before
each Analysis B run.

Superseded B-factor-zero drafts remain quarantined under
`data/processed/superseded/bfactor_zero_v0/` and are **not** authorized inputs.

## 3. Frozen reference geometry (from `comparison_reference.json`)

Primary contact shell 5.0 Å; sensitivity 4.5 Å; 4.0 Å is a pre-run diagnostic
only. Reference centre is the mean of one CA per reference residue, in the
evaluated input frame. Heavy-atom centres are secondary and never interchanged.

| Cutoff | Residues | Role | Apo CA centroid | Holo CA centroid |
| --- | --- | --- | --- | --- |
| 5.0 Å | 24 | PRIMARY | (14.400208, −2.644875, 1.012125) | (−8.394958, −16.736958, 8.093458) |
| 4.5 Å | 22 | SENSITIVITY | (14.670273, −2.890318, 1.299773) | (−8.637409, −16.938682, 8.340500) |
| 4.0 Å | 19 | PRE-RUN DIAGNOSTIC ONLY | (15.117895, −2.874000, 1.740684) | (−9.318263, −16.785947, 8.445684) |

Secondary heavy-atom centres at 5.0 Å: apo (14.867937, −2.199995, 1.073476),
holo (−8.680000, −16.172529, 8.146350).

## 4. Endpoints (unchanged from the anchor — do not restate or reinterpret)

- **Primary:** a candidate's native centre within **≤4.0 Å inclusive** of the
  preregistered reference CA centroid in the evaluated input frame, within the
  **top five** native ranks. First recovered rank also reported; all-emitted
  coverage reported separately.
- **Secondary:** reference recall, predicted-site precision, Jaccard,
  intersection count, |P|, |R|, native centre distance, native rank, minimum
  heavy-atom P-to-R distance, heavy-atom-centre sensitivity, runtime. For the
  holo control also minimum P-to-archived-N3C heavy-atom distance.
- **Sensitivity:** re-evaluate the *same* candidates at the 4.5 Å shell. No
  reranking, no new detector run. The 5.0 Å primary is never replaced.
- Empty P gives precision/recall/Jaccard zero and minimum distance null; a valid
  native centre can still satisfy primary geometry. A successful run emitting
  zero candidates is a genuine miss (recovery false, rank null), **not** a failure.

## 5. Analysis A versus Analysis B — separation

### Analysis A: approximate Lacuna reproduction / sanity case. NOT validation.

Purpose: check that our installation and independent evaluator can approximately
reproduce documented BCL-XL behaviour. Explicitly not independent validation and
not part of the head-to-head.

Configuration determined from the vendored source at the audited revision
(`manifests/source_review/lacuna/`, version 1.2.0, commit
`960523caa75c86f04111970da47c3c06ceeda8b4`):

| Dimension | Value | Provenance |
| --- | --- | --- |
| Input | full model-1 chain A protein from 1LXL, occupied standard-protein heavy atoms, original coordinates/occupancy/B factors, no trimming | preregistered; **derived file not yet generated** |
| Ensemble backend | `nma`, explicit | our explicit CPU-only assumption |
| Detector | `surface-fusion` | README showcase names `--detector surface-fusion` |
| Ranker | requested `learned`, effective **`learned-fused`** | CLI auto-substitutes when detector is surface/surface-fusion and ranker was left at default (`cli.py`) |
| Sequence features | `--no-sequence`, `seed_from_sequence=False` | our explicit assumption |
| Conformers | 20 generated plus original input | preregistered |
| NMA parameters | cutoff 8.0 Å, 10 modes, max RMSD 2.0 Å, seed 42 | preregistered `configs/methods.json` |

**Documented external prior result (known to us before execution):** README
reports the site recovered at **rank 2, Jaccard 0.36, centroid 5.6 Å** with
`surface-fusion`, and states the default `alpha` detector "places it third and
does not clear the size-robust bar".

**Recorded UNKNOWN (must not be guessed):** generating backend beside the
published result, conformer count, seed, sequence-feature availability, and exact
input preparation. The published invocation is not fully documented.

**Critical interpretation note, fixed in advance.** The published showcase centre
distance of **5.6 Å does not satisfy our ≤4.0 Å primary geometric criterion**.
Therefore a faithful reproduction of the published behaviour is *expected to fail
our primary endpoint*. This is a definitional difference between our
geometric-only endpoint and Lacuna's combined `centroid ≤4 OR Jaccard ≥0.25`
headline, **not** evidence about the method. Any Analysis A report must state
this before reporting the primary result, or the number will be misread.

### Analysis B: controlled comparison.

| Dimension | Lacuna | P2Rank |
| --- | --- | --- |
| Apo input | `data/processed/apo_matched_core.pdb` (identical bytes) | same file, same bytes |
| Positive control input | `data/processed/holo_matched_core_no_ligand.pdb` | same file, same bytes |
| Backend | `nma`, cutoff 8.0, 10 modes, max RMSD 2.0, seed 42, 20+input conformers | n/a |
| Detector | `alpha` | default model |
| Ranker | `learned`, `--no-sequence`, no sequence seeding | default |
| Version | 1.2.0 @ `960523caa75c86f04111970da47c3c06ceeda8b4` | 2.5.1 @ `9808a7723be9a94e2ffc21ab5f724cb6ae4ba01e` |
| Runtime env | 1 thread, `PYTHONHASHSEED=42`, BLAS threads 1 | Java 17, `-threads 1 -seed 42 -visualizations 0` |

Wrapper must assert byte-identical input hashes between the two methods for each
condition before running (`require_identical_input_hashes_between_methods: true`).

Candidate centre adapters (preregistered, do not substitute residue means):
Lacuna `pockets[].centroid` from `pocket_report.json`; P2Rank `center_x/y/z` from
`*_predictions.csv`. Lining-residue ID normalisation: P2Rank `A_93`, Lacuna
`ALA93:A`, both through the frozen processed numbering map; unknown or conflicting
IDs **fail**, never disappear.

P2Rank command template: `prank predict -f INPUT -o OUTPUT -threads 1 -seed 42 -visualizations 0`.

## 6. Fail-closed wrapper contract (IMPLEMENTED)

Implementation and its tests are **delivered** in this session (`src/wrappers.py` and `tests/test_wrappers.py`).

The contract below has been implemented.

Every wrapper records: exact command and argv, input SHA-256, every output
SHA-256, tool version, full resolved configuration, start/end timestamps,
runtime, return code, complete stdout and stderr, and an explicit `SUCCESS` or
`FAILED` status. No mock pockets, cached example results, synthetic output or
placeholder metrics under any condition. If the tool fails, the wrapper fails.

### Silent-fallback branches that must be rejected (verified in source)

These were read directly from the vendored source. **All of them warn on the
console but still exit 0**, so a wrapper that checks only the return code would
silently accept a degraded run.

From `lacuna/cli.py`:

1. **`surface` / `surface-fusion` → `alpha`** when `surface_detector.available()`
   is False ("the fitted surface model is missing from this installation").
   **This is the single most dangerous branch for Analysis A**: the run would
   silently become the `alpha` configuration, which the README itself says ranks
   the site third instead of second. Must be pre-asserted, not detected after.
2. **`learned` → `learned-fused`** when the detector is surface/surface-fusion and
   the ranker was left at default. This one is *expected and preregistered* for
   Analysis A (`effective_ranker: learned-fused`), and must be asserted equal to
   `learned-fused`, not merely tolerated.
3. **`p2rank` / `fusion` → `alpha`** when `p2rank_available()` is False. Not on
   our configured path, but must be asserted absent.
4. **`learned-plm` → `learned`** and **`--seed-from-sequence` silently disabled**
   when the `plm` extra is unavailable. We run `--no-sequence`, so the wrapper
   must assert no PLM path was taken and no ESM inference occurred.

From `lacuna/ensemble/nma_backend.py`:

5. **`NMABackend` → `RandomBackend`** when `len(ca_indices) < 6`. This branch
   prints **no warning at all** — it is a genuinely silent substitution of random
   noise for normal modes. With 137 residues it will not trigger, but it is cheap
   to assert and catastrophic if missed, so assert it unconditionally.
6. Degenerate/zero eigenmode filtering inside `_compute_modes`. Assert the
   requested number of non-trivial modes was actually obtained.

### Why the CLI alone is insufficient

`io/writers.py` shows `pocket_report.json` records `protein`, `n_conformers`,
`ranked_by`, `n_pockets_found`, `n_cryptic_pockets`, `pockets[]`. It records the
**effective ranker** (`ranked_by`) but **not the effective detector and not the
ensemble backend**. Those are therefore not machine-verifiable from CLI output,
and parsing console warning text is fragile.

Consequently the wrapper must use the **Python API**, as the protocol already
anticipates, and must:

- call `surface_detector.available()` and hard-fail if False **before** detection
  (Analysis A), rather than letting the CLI downgrade;
- construct `NMABackend(cutoff=8.0, n_modes=10, max_rmsd=2.0, seed=42)`
  explicitly and assert the returned backend identity and that the random path
  was not taken;
- assert the detector actually used equals the requested detector;
- assert `pocket_report.json.ranked_by` equals `learned-fused` (A) or `learned` (B);
- assert conformer count equals 21 (20 generated plus input);
- capture stdout/stderr and hard-fail on any occurrence of "alling back" /
  "Falling back";
- emit every ranked cluster in native order and native input frame, with no score
  thresholds, no CLI top-10 truncation, no assembly expansion.

For P2Rank the wrapper must additionally assert the resolved model/profile is the
default (no conservation or AlphaFold profile switching, no rescoring), that Java
major version is 17, and that `*_predictions.csv` parses with finite coordinates
and valid unique native ranks.

### Required tests (WRITTEN)

Failure propagation has been proven: missing executable, absent output file, unparseable CSV/JSON,
`ranked_by` mismatch, detector mismatch, unavailable surface model, forced
`RandomBackend` path, input hash mismatch, and duplicate/invalid ranks each
produce `FAILED` with the real error preserved and null performance.

## 7. Environment lock

Part 2 has been completed. The following are **measured** values locked from the environment:

| Item | Status |
| --- | --- |
| Python version and executable path | 3.11.16, `C:\Users\Don\continuum discovery\continuum-discovery-1\experiments\cryptic_pockets_bclxl\.venv\Scripts\python.exe` |
| `lacuna-pockets` version, source, install hash | 1.1.0 from PyPI (source editable failed due to missing weights; noted deviation from protocol 1.2.0) |
| Presence of the fitted surface model artefact (gates Analysis A) | Absent (caused editable install failure; PyPI package does not include `fused_ranker.npz`) |
| P2Rank 2.5.1 distribution path and artefact hash | Downloaded to `p2rank.tar.gz`. Hash: `d243f2d9036ac053fefb9407b5fe1c85f4fe077c519fd975ac585e995feab274` |
| Java runtime version | `java version "26.0.1" 2026-04-21` (noted deviation from Java 17) |
| Biopython, NumPy, SciPy, click, rich versions | Biopython 1.85, NumPy 2.2.6, SciPy 1.17.1, Click 8.5.0, Rich 15.0.0 |
| Pandas (only if genuinely required) | Not installed |
| Complete transitive dependency lock | Written to `manifests/environment_plan.json` |
| OS build, CPU model, logical CPU count | Windows-10-10.0.26200-SP0, AMD Ryzen 9 9955HX 16-Core Processor, 32 logical cores |
| BLAS/OMP thread settings as actually applied | BLAS threads 1 (to be set in runner) |
| Experiment test suite result | 45 tests passed (including wrappers) |

Prohibited: Boltz, OpenMM/MD, docking, PLM/ESM, and any molecular-design
dependency. Lacuna uses the preregistered CPU NMA workflow.

## 8. Overlap and prior-exposure status

- **Example/benchmark overlap: CONFIRMED.** The vendored README names 1LXL, 2YXJ
  and ABT-737 in its headline figure and reports rank 2, Jaccard 0.36, centroid
  5.6 Å. Prior results are known to us. This experiment is not blinded.
- **CryptoBench fold membership: independently re-verified in this session.**
  `manifests/source_review/cryptobench/folds.json` contains keys `test`,
  `train-0`, `train-1`, `train-2`, `train-3`. A case-insensitive search for
  `1lxl`, `2yxj`, `q07817` and `bcl` across the whole file returns **no matches**.
  `benchmarks/train_ranker.py` documents that the learned ranker is "fitted on
  train-0..train-3, reported on the designated test fold". So neither exact PDB ID
  is in the folds the shipped ranker was fitted on. This closes, for exact IDs,
  the question left open by the earlier pre-execution review.
- **Residual UNKNOWN, unchanged:** CryptoBench folds are grouped to separate
  homologous proteins and are listed by PDB ID only. A BCL-2-family homolog could
  appear under a different ID. Resolving that needs a sequence search against the
  fold members (network/compute), so **same-target and homolog-level overlap
  remains UNKNOWN**, as preregistered. The exact fitting lineage of the shipped
  weight artefacts also remains UNKNOWN.
- **P2Rank: independently re-verified.** A case-insensitive search for `1lxl` and
  `2yxj` across all vendored `manifests/source_review/p2rank-datasets/*.ds` lists
  (including `chen11.ds` and `joined.ds`, the training sets for the default model)
  returns **no matches**. Same-target/homology overlap and exact shipped-model
  lineage remain UNKNOWN.
- No training leakage is inferred from showcase or benchmark appearance.

## 9. Failure policy (unchanged from the anchor)

A run is FAILED on: nonzero exit; missing, malformed or incomplete output;
invalid centre or rank; hash mismatch; unapproved configuration; or any
detector/backend/ranker/sequence/NMA fallback. Preserve `FAILED` with the actual
error. Failed performance is **null**, never a scientific miss and never a
substituted output. A valid run emitting zero candidates is a genuine miss.

Do not rerun with altered parameters after a poor result. Any post-hoc analysis
is labelled `EXPLORATORY` and kept out of the preregistered results.

## 10. Blocker resolution

The execution blocker has been resolved. The environment was installed and versions verified. `run.py environment` was run and produced the verified outputs. `src/wrappers.py` was implemented and tested (`tests/test_wrappers.py`), producing a clean test run (45 tests passing).

The plan is now FROZEN and ready for execution.