# BCL-XL reproduction and pipeline-validation benchmark

Status: pre-execution review amendments complete; no detector has been run.
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
Neither analysis has been executed. Backend, detector and ranker are distinct
configuration dimensions; the detailed table and parameters are preregistered.

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

| Path | Purpose |
| --- | --- |
| PROTOCOL.md; PREREGISTRATION.md; AMENDMENTS.md | Definitions, freeze, reasons and chronology |
| configs/reference_site.json; configs/methods.json | Contact/mapping/recovery and exact planned method settings |
| configs/requirements-reference.txt | Current isolated parser environment |
| data/raw/1LXL.cif; data/raw/2YXJ.cif | Immutable RCSB inputs |
| manifests/input_manifest.json; manifests/acquisition_*.json | Raw metadata and acquisition hashes |
| manifests/environment_plan.json | Amended future software plan; neither detector installed |
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

Next stage needs human approval, artifact/dependency locking, tested strict method
wrappers that reject upstream fallback, and separate preparation for Analysis A.
No P2Rank, Lacuna, docking, Boltz, RFdiffusion, ProteinMPNN, ESMFold or design was run.
All findings so far are deterministic analyses of public structural coordinates,
not new experimental evidence.
