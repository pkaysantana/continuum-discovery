# BCL-XL cryptic-pocket benchmark foundation

Status: **Steps 1–5 complete; stopped for human review.**

Question: can an ensemble method recover a known ligand-defined BCL-XL site
from an apo structure, compared with a static pocket detector? Apo coordinates
provide the opening challenge; ligand-removed holo coordinates will provide a
positive control with the ligand-associated protein geometry already present.
Neither an apo assignment nor successful site recovery alone proves crypticity.

RCSB independently verifies [1LXL](https://www.rcsb.org/structure/1LXL) as
ligand-free human BCL-XL (one minimized-average solution NMR model), and
[2YXJ](https://www.rcsb.org/structure/2YXJ) as its ABT-737 complex (2.20 A X-ray
structure). [N3C](https://www.rcsb.org/ligand/N3C) is ABT-737. Both unmodified
mmCIF files were retrieved from files.rcsb.org on 2026-09-16 UTC.

The preregistered rule uses protein chain A, model 1, and holo ligand N3C label
chain D / author chain A, residue 1001. A protein residue qualifies if any
occupied selected heavy atom is within **5.0 A inclusive** of a ligand heavy
atom. This defines a local contact shell before future detector performance is
observed. Protein membership, alternate conformers, waters, mapping, centroids,
future metrics and recovery thresholds are fixed in [PROTOCOL.md](PROTOCOL.md).

The deterministic evaluator found **24 holo reference residues; 24 mapped to
apo coordinates; 0 unmapped**. Mapping uses a unique global affine-gap alignment
of full deposited polymer sequences, with an explicit 40-residue deletion in the
holo construct. Author residue numbers are annotations, not mapping keys.
The holo protein reference centroid is (-8.680000, -16.172529, 8.146350) A,
averaged over 206 heavy atoms in the original holo frame. Apo and ligand centroids
are separately labelled in the JSON; the original apo/holo frames are not aligned.

Selected holo chain A has **137 observed / 181 deposited residues**, with 44
missing coordinate positions (label IDs 1–7, 30–46, 162–181; PDB sequence-scheme
numbers -3–3, 26–42, 198–217). Apo has 221/221 observed deposited residues.
Missing holo residues cannot contribute contacts, so complete mapping of the
24 observed contact residues is not proof of a complete biological site.
Both constructs contain expression tags and lack the native membrane anchor;
the holo construct additionally deletes native positions 45–84. Holo SER A23
has alternate locations; the preregistered occupancy rule selects A. The ligand
has no alternate locations. Full records are in the inspection JSON.

The complete experiment suite passed **28 tests, 0 failures, 0 errors, 0 skipped**.
Tests cover synthetic contacts, inclusive cutoff, atom and water exclusions,
ligand selection and absence, alternate locations, sequence gaps/mismatches,
missing coordinates, insertion codes, centroids, hashing, immutable writes,
mmCIF parsing, and repeatability including reversed atom-row order.

Completed files and outputs:

| Path | Contents |
| --- | --- |
| [PROTOCOL.md](PROTOCOL.md) | Preregistered scientific definitions and future controls/metrics |
| [configs/reference_site.json](configs/reference_site.json) | Fixed selection, geometry and alignment settings |
| [configs/requirements-reference.txt](configs/requirements-reference.txt) | Exact current parser/numerical dependencies |
| [data/raw/1LXL.cif](data/raw/1LXL.cif), [data/raw/2YXJ.cif](data/raw/2YXJ.cif) | Immutable public structures |
| [manifests/input_manifest.json](manifests/input_manifest.json) | URLs, retrieval timestamps, titles, methods, chains, ligands, sizes and hashes |
| manifests/acquisition_1LXL.json, manifests/acquisition_2YXJ.json | Create-only acquisition receipts and HTTP metadata |
| [manifests/environment_plan.json](manifests/environment_plan.json) | Current hardware/software and planned later environment |
| [data/processed/reference_site.json](data/processed/reference_site.json) | Contact residues, distances, complete alignment, mapped/unmapped residues, centroids and warnings |
| [data/processed/structure_inspection.json](data/processed/structure_inspection.json) | Archive missing-residue, construct, ligand and model metadata |
| [src/reference_site.py](src/reference_site.py) | Deterministic evaluator functions |
| [src/provenance.py](src/provenance.py), [src/run.py](src/run.py) | Hashing, immutable writes and logged commands |
| [src/bootstrap.ps1](src/bootstrap.ps1) | Isolated environment setup with execution receipt |
| [tests/test_reference_site.py](tests/test_reference_site.py) | Complete experiment test suite |
| manifests/runs/ | Timestamped start/completion receipts, commands, hashes and SUCCESS/FAILED status |
| results/tests-*.json, results/test-*.log | Exact test counts and per-test results |
| results/*.log | Acquisition, environment, inspection, evaluator, verification and setup logs |
| [manifests/setup_notes.json](manifests/setup_notes.json) | Pre-bootstrap probe failures and provenance limitations |

Reproduce from the repository root in PowerShell. Use a separate Python 3.11.16
installation; the example path is this workstation's existing uv-managed Python.
The bootstrap installs **only Biopython 1.85 and NumPy 2.2.6** into this experiment.
On another workstation pass its Python path via `-Python`. Installation and initial
download need network access. Existing raw inputs are verified locally and reused.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ./experiments/cryptic_pockets_bclxl/src/bootstrap.ps1 -Python C:/Users/Don/AppData/Roaming/uv/python/cpython-3.11.16-windows-x86_64-none/python.exe
& ./experiments/cryptic_pockets_bclxl/.venv/Scripts/python.exe -B ./experiments/cryptic_pockets_bclxl/src/run.py environment
& ./experiments/cryptic_pockets_bclxl/.venv/Scripts/python.exe -B ./experiments/cryptic_pockets_bclxl/src/run.py acquire
& ./experiments/cryptic_pockets_bclxl/.venv/Scripts/python.exe -B ./experiments/cryptic_pockets_bclxl/src/run.py inspect
& ./experiments/cryptic_pockets_bclxl/.venv/Scripts/python.exe -B ./experiments/cryptic_pockets_bclxl/src/run.py evaluate
& ./experiments/cryptic_pockets_bclxl/.venv/Scripts/python.exe -B ./experiments/cryptic_pockets_bclxl/src/run.py test
& ./experiments/cryptic_pockets_bclxl/.venv/Scripts/python.exe -B ./experiments/cryptic_pockets_bclxl/src/run.py verify
```

Use `run.py` for all experiment execution. The runner hashes inputs, source,
configuration, protocol and outputs, records the repository base commit and
installed versions, and writes create-only run records. An orphan `.started.json`
means interruption, never success. An expected exception inside a passing unit
test is reported as a passed negative test; actual command failures are FAILED.
The first acquisition attempt was blocked by sandbox network permissions and is
preserved as FAILED with its actual traceback; the authorized retry succeeded.
No scientific computation failed and no mock data replaced real inputs.

Raw files are never overwritten. Replays must have matching SHA-256 and sizes.
Derived files are also create-only: identical replays succeed, different results
fail for explicit versioning/review. On a different machine, `environment` will
report a mismatch with the recorded workstation plan; retain this plan and use
a separate experiment copy with a deliberately versioned environment record.
The scientific JSON omits timestamps to permit byte-identical replay; timestamps
live in run receipts. `.gitattributes` disables line-ending conversion so Git
preserves artifact hashes. `.venv`, caches, bytecode and temporary test files are
local ignored runtime artifacts. Never install into the historical environment.

**Not run:** P2Rank, Lacuna, docking, Boltz, RFdiffusion, ProteinMPNN, ESMFold,
protein/ligand design or optimization. No detector performance is reported.
The holo-minus-ligand control is specified but has not yet been prepared or run.

The planned next stage, only after approval, is P2Rank 2.5.1 versus Lacuna-pockets
1.1.0 with explicit CPU `nma`, after freezing adapters, dependencies, seeds and
thread settings and preparing matched inputs. No Boltz/MD/PLM extras are planned.
Human review should assess whether this NMR/crystal pair is an appropriate
cryptic-pocket challenge, missing-region/construct effects, chain-copy selection,
and possible overlap with detector training data. These outputs are geometric
analyses of public structures, not new experimental evidence.
