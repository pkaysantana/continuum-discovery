# BCL-XL reproduction and pipeline-validation benchmark

Status: Analyses A and B are COMPLETE (executed 2026-09-16); independent
second-system selection is CLOSED with no eligible candidate; the structural-pocket
project is paused/closed. **The preregistered primary endpoint was not met in any
executed arm.** All preregistered definitions, endpoints, configs, run receipts and
results below are unchanged by this status correction; see AMENDMENTS.md item 10.
Earlier revisions of this file stated that no detector had been run: that text was
written at the preregistration commit `ff685f1` and was never updated after
execution. It is corrected here, and no result file was altered.
This is not independent generalisation or blinded external validation: Lacuna
already documents BCL-XL / 1LXL / 2YXJ and prior results are known. Documentation
or benchmark overlap is not evidence of training leakage.

The experiment validates our provenance/evaluation infrastructure, attempts to
recover a known cryptic-pocket case with independently implemented evaluation,
compares static detection and Lacuna using a common evaluator, and investigates
construct/metric sensitivity. [PROTOCOL.md](PROTOCOL.md) is authoritative;
[PREREGISTRATION.md](PREREGISTRATION.md) records the freeze and execution boundary.

Analysis A is an approximate Lacuna reproduction/sanity case with explicit CPU
NMA plus surface-fusion/no-sequence assumptions; the exact showcase backend is
not documented beside its result. Analysis B compares P2Rank and Lacuna NMA/alpha
on identical matched-core apo inputs and identical holo-minus-ligand controls.
Both analyses have been executed; see "Executed results" below. Backend, detector
and ranker are distinct configuration dimensions; the detailed table and
parameters are preregistered.

RCSB 1LXL is ligand-free BCL-XL (one minimized-average NMR model); 2YXJ is the
ABT-737/N3C complex (2.20 A X-ray). Both raw mmCIF files remain unchanged.
The deterministic matched core contains **137 residues in each state**; exclusions
are 84 apo and 44 holo deposited positions. Selection uses identical mapped,
observed native residues with complete backbones, without any pocket-proximity rule.
Coordinates, occupancies and B factors are preserved. Both processed files remain
discontinuous; truncation does not remove all NMR/crystal or sampling confounders.

Primary ligand-contact cutoff remains **5.0 A: 24 reference residues**, all retained
and mapped. **4.5 A: 22** is sensitivity; **4.0 A: 19** is a pre-run diagnostic only.
Primary recovery is native pocket center within **4.0 A of the reference-residue
CA centroid** in the same input frame, top five. Recall, precision and Jaccard
are separate secondary measures, not primary gates. This geometric-only endpoint
differs from Lacuna's published centroid-OR-Jaccard combined headline.

## Executed results

Both analyses ran on 2026-09-16 with timestamped receipts in `manifests/runs/`
(55 receipt files) and per-analysis run manifests beside each result set. The
preregistered primary endpoint throughout is: native pocket centre within 4.0 A
of the reference-residue CA centroid, within the top five ranks.

### Analysis A: Lacuna reproduction (commit `3a33dd2`)

Lacuna 1.2.0, CPU NMA backend, surface-fusion ranking, 20 conformers.
Artefacts: `results/analysis_a/` (`evaluation.json`, `configuration.json`,
`interpretation.md`, `ANALYSIS_A_RECONCILIATION.md`, two run manifests, `raw/`).

| Quantity | This reproduction | Published value |
| --- | --- | --- |
| Jaccard at rank 2 | 0.366 | 0.36 |
| Centroid distance at rank 2 | 5.34 A | 5.6 A |

- Under the preregistered primary endpoint, rank 2 **fails** (5.34 A > 4.0 A).
  The site is formally recovered only at **rank 10** (centroid 3.33 A), outside
  the top-five window.
- The NMA backend is deterministic (`seed=i`), so the residual difference from
  the published values is **not** stochastic variance.
- Classification: pipeline-validation reproduction on processed matched-core
  input. This is **not** an exact reproduction of the published result.

### Analysis B: P2Rank vs Lacuna, identical inputs (commit `20a24af`)

P2Rank 2.5.1 against Lacuna 1.2.0 (NMA/alpha/learned), seed 42, identical
matched-core apo inputs and identical holo-minus-ligand positive controls.
Artefacts: `results/analysis_b/` (`summary.json`, `candidate_metrics.csv`,
`ANALYSIS_B_RESULTS.md`, four run manifests, `config/`, `normalized/`, `raw/`).

| Condition | Method | Candidates | First primary hit | Best centroid (A) | Best Jaccard | Runtime (s) |
| --- | --- | --- | --- | --- | --- | --- |
| apo | P2Rank | 4 | none | 4.973 | 0.360 | 10.9 |
| apo | Lacuna | 10 | none | 4.962 | 0.433 | 5.6 |
| holo control | P2Rank | 3 | none | 6.849 | 0.500 | 8.6 |
| holo control | Lacuna | 10 | none | 4.481 | 0.560 | 4.8 |

- **Primary endpoint: zero hits in all four arms.** This is the headline finding
  and it is negative.
- The two methods differ by ~0.01 A in best apo centroid distance, so these data
  show no detectable advantage for ensemble-based over static detection on this
  single target.
- Both methods satisfy only the weaker upstream secondary criterion
  (Jaccard >= 0.25) and do so at rank 1.
- The 4.5 A sensitivity definition also yields exactly zero primary hits, so the
  qualitative primary conclusion is unchanged by that cutoff.

### Independent second system: CLOSED, no candidate

Recorded in `experiments/independent_oncology_benchmark/` (commits `2607ba8`,
`ad68841`, `eea8354`, `11edeae`). Eight candidates were screened against the
frozen eligibility criteria (EGFR, CDK2, KRAS, PTP1B, PI3K, MEK1, IDH1 and
related pairs). An initial EGFR selection (`4I22`/`5D41`) and a revised pair
(`5EDP`/`5D41`) were both withdrawn on structural-quality grounds -- `4I22` is
not apo but a triple mutant co-crystallised with gefitinib, and the revised pair
had severe mutation/construct mismatch (missing `V948R`; `5D41` lacking the
deposited `L858R`). Both errors were caught **before** any detector execution.
Final status: **NO_VALID_CANDIDATE_YET**; no detector performance was inspected
at any point during candidate selection, and no candidate was forced into
selection. See `SELECTION_OUTCOME.md` for the reopening criteria.

### What these results do and do not support

- Supported: a preregistered, independently implemented evaluator reproduces
  published Lacuna numbers closely on processed input; under a stricter,
  prespecified geometric endpoint neither detector recovers the BCL-XL site.
- Not supported, and not claimed: independent generalisation, blinded or external
  validation, superiority of either detector, or a validated cryptic pocket.
  n = 1 target, single workstation, no replication.

## Repository map

| Path | Purpose |
| --- | --- |
| PROTOCOL.md; PREREGISTRATION.md; AMENDMENTS.md | Definitions, freeze, reasons and chronology |
| configs/reference_site.json; configs/methods.json | Contact/mapping/recovery and exact planned method settings |
| configs/requirements-reference.txt | Current isolated parser environment |
| data/raw/1LXL.cif; data/raw/2YXJ.cif | Immutable RCSB inputs |
| manifests/input_manifest.json; manifests/acquisition_*.json | Raw metadata and acquisition hashes |
| manifests/environment_plan.json | Amended software plan written before execution; both detectors were subsequently installed and used, as recorded in manifests/runs/ and the per-analysis run manifests |
| manifests/benchmark_overlap_audit.json; manifests/source_review/ | Bounded overlap findings and source evidence |
| data/processed/apo_matched_core.pdb | Identical apo input for both methods in Analysis B |
| data/processed/holo_matched_core_no_ligand.pdb | Identical ligand-free holo positive control |
| data/processed/matched_core_manifest.json | Retention, exclusions/reasons, raw/output hashes |
| data/processed/comparison_reference.json | Frozen CA and heavy-atom centers at all three cutoffs |
| data/processed/reference_site.json; reference_site_v2.json | Original reference output and amendment-provenance replay |
| data/processed/structure_inspection.json | Archive construct, missing-coordinate and ligand metadata |
| src/; tests/ | Deterministic evaluator, preprocessing, synthetic tests and logged entry point |
| manifests/runs/; results/ | Timestamped command receipts, hashes, failures and test results |
| manifests/pre_review/; data/processed/superseded/ | Superseded material retained for audit; never method inputs |

Reproduce deterministic work from the repository root, using the existing
experiment .venv (Python 3.11.16, Biopython 1.85, NumPy 2.2.6). For a new local
environment use src/bootstrap.ps1 with an explicit Python interpreter. It installs
only parser dependencies, not detectors. Keep logs/caches inside this experiment.

```powershell
& ./experiments/cryptic_pockets_bclxl/.venv/Scripts/python.exe -B ./experiments/cryptic_pockets_bclxl/src/run.py verify
& ./experiments/cryptic_pockets_bclxl/.venv/Scripts/python.exe -B ./experiments/cryptic_pockets_bclxl/src/run.py evaluate
& ./experiments/cryptic_pockets_bclxl/.venv/Scripts/python.exe -B ./experiments/cryptic_pockets_bclxl/src/run.py matched-core
& ./experiments/cryptic_pockets_bclxl/.venv/Scripts/python.exe -B ./experiments/cryptic_pockets_bclxl/src/run.py overlap-audit
& ./experiments/cryptic_pockets_bclxl/.venv/Scripts/python.exe -B ./experiments/cryptic_pockets_bclxl/src/run.py test
& ./experiments/cryptic_pockets_bclxl/.venv/Scripts/python.exe -B ./experiments/cryptic_pockets_bclxl/src/run.py preflight
```

Saved source evidence permits offline audit. Do not rerun network snapshot or
one-time archive/amendment actions against frozen outputs. Identical derived-file
replay succeeds; differing bytes require an explicit new version. Earlier FAILED
network/source-tree attempts remain in receipts. Initial environment probes lacked
individual timestamps, as documented in setup_notes.json. Source snapshots are
read-only evidence and must never be imported or executed.

Lacuna has EXAMPLE_OVERLAP and BENCHMARK_OVERLAP. No direct fitting inclusion was
identified for either method in this bounded audit; target/homology-level training
overlap remains UNKNOWN. Criteria for a genuinely independent second oncology
system are frozen before candidate discovery; no second system was selected.

Analyses A and B were executed through method wrappers in `src/wrappers.py`
that refuse to run rather than fall back (e.g. the Lacuna surface model raises
instead of silently degrading to alpha). P2Rank 2.5.1 and Lacuna 1.2.0 were run,
on the processed matched-core inputs only. No docking, Boltz, RFdiffusion, ProteinMPNN,
ESMFold or protein design was run at any point in this experiment. All findings
are deterministic analyses of public structural coordinates plus the two pocket
detectors above, executed locally on one workstation; they are not new
experimental evidence, and they are neither blinded nor independently replicated.
