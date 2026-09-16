"""Apply the explicitly requested pre-execution amendment, preserving version 1."""
import json
from provenance import ROOT, canonical_bytes, now

PROTOCOL = '''# BCL-XL reproduction and pipeline-validation benchmark

Protocol version 2, pre-execution review amendment, 2026-09-16. Version 1 is
preserved under manifests/pre_review/. No local detector results exist.

## Classification and question

This is a BCL-XL reproduction and pipeline-validation benchmark. It is not an
independent generalisation benchmark or blinded external validation: Lacuna's
README and curated benchmark already document BCL-XL / 1LXL / 2YXJ, and prior
results are known to us. Appearance in examples or benchmarks does not establish
training leakage. Purposes: validate experiment/provenance/evaluation infrastructure;
recover a known cryptic-pocket case with independently implemented evaluation;
compare a static detector and Lacuna under a common preregistered evaluator;
understand sensitivity to construct processing and metric definition.

Can an ensemble method recover a ligand-defined BCL-XL site from apo coordinates,
and how does it compare with a static detector? An ensemble method may recover
geometry less apparent to a static detector; we do not assume Lacuna wins.
Site recovery is not experimental evidence of binding, affinity or clinical utility.

## Public structures

[RCSB 1LXL](https://www.rcsb.org/structure/1LXL): ligand-free human BCL-XL,
single minimized-average solution NMR model. [RCSB 2YXJ](https://www.rcsb.org/structure/2YXJ):
human BCL-XL with ABT-737, X-ray diffraction at 2.20 A. [N3C](https://www.rcsb.org/ligand/N3C)
identifies ABT-737. Use model 1, protein label/auth chain A in both; holo ligand
label chain D, author chain A, author residue 1001. Chain B is excluded by the
original identifier rule. No symmetry expansion. Original RCSB mmCIF files and
retrieval receipts remain immutable; exact metadata/hashes are in input_manifest.json.

## Configuration dimensions and source evidence

Ensemble backend and pocket detector are separate dimensions. NMA is an ensemble
backend; alpha, surface, surface-fusion, p2rank and fusion are detector choices.
NMA can be combined with surface-fusion. Ranking is a third dimension.
The current audited Lacuna source identifies itself as 1.2.0 at commit
960523caa75c86f04111970da47c3c06ceeda8b4; use that exact revision for later work,
not a moving branch or an assumed equivalence with the superseded 1.1.0 plan.

| Configuration | Backend | Detector | Ranking / sampling | Interpretation |
| --- | --- | --- | --- | --- |
| A. Package defaults at audited revision | CLI auto: Boltz, OpenMM, NMA, random priority; plain base installation resolves to NMA | alpha | learned; 20 generated conformers plus input; top 10 output | Defaults are environment-dependent, so our runs explicitly select NMA |
| B. Documented BCL-XL showcase | Exact generating backend UNKNOWN beside the result | surface-fusion (alpha also discussed) | Exact conformer count, seed, sequence features and preparation UNKNOWN | README reports rank 2, Jaccard 0.36, center distance 5.6 A for surface-fusion; these are external prior results |
| C1. Our Analysis A approximation | NMA, CPU | surface-fusion, explicit no-sequence | learned request becomes learned-fused; 20 conformers plus input | Closest documented detector choice with explicit CPU-only assumptions; not an exact reconstruction of the undocumented showcase invocation |
| C2. Our Analysis B comparison | NMA, CPU | alpha | learned; 20 conformers plus input | Compare against P2Rank 2.5.1 default model on identical matched-core input bytes |

Audited source: [CLI](https://github.com/mooreneural/lacuna/blob/960523caa75c86f04111970da47c3c06ceeda8b4/lacuna/cli.py),
[showcase](https://github.com/mooreneural/lacuna/blob/960523caa75c86f04111970da47c3c06ceeda8b4/README.md),
[benchmark](https://github.com/mooreneural/lacuna/blob/960523caa75c86f04111970da47c3c06ceeda8b4/benchmarks/cryptic_benchmark.py).
Saved text and hashes are under manifests/source_review/ and benchmark_overlap_audit.json.

Exact planned parameters are in configs/methods.json. All Lacuna NMA runs use
NMABackend(cutoff=8.0, n_modes=10, max_rmsd=2.0, seed=42), 20 generated conformers
plus the original input. The source samples each conformer with seed=i. Freeze
Python/NumPy/SciPy and BLAS versions and use one numerical-library thread. No
optional Boltz/OpenMM/PLM backends, ESM model inference or sequence seeding.
Use a later audited API wrapper to emit every ranked cluster without CLI top-10
truncation; preserve native order and native centers. No detector code runs now.
P2Rank uses 2.5.1 (9808a7723be9a94e2ffc21ab5f724cb6ae4ba01e), Java 17,
default model/profile, seed 42, threads 1, visualizations disabled; no rescoring
or conservation/AlphaFold profile switching. Planned command template:
`prank predict -f INPUT -o OUTPUT -threads 1 -seed 42 -visualizations 0`.
Hash installed artifacts and lock transitive dependencies before authorized execution.

## Analyses and controls

Analysis A: Lacuna reproduction/sanity case. Later use the full selected apo
chain A from 1LXL, preserving all occupied standard-protein heavy atoms under the
same alternate-location rule; generate that derived input with its own manifest
before running it. Evaluate against our mapped reference. Compare approximately
with documented BCL-XL behaviour, explaining configuration and metric differences.
This analysis is not independent validation and is not part of the fair head-to-head.
Its full-chain derived input and execution wrapper are deferred until approval.

Analysis B: controlled method comparison. Both methods receive exactly
data/processed/apo_matched_core.pdb; both positive-control runs receive exactly
data/processed/holo_matched_core_no_ligand.pdb. The latter preserves the observed
ligand-associated protein conformation without ligand/solvent. It separates site
identification in an open geometry from limitations in sampling from apo; removal
does not relax holo into apo. No method is tuned after observing another's outputs.
Report A and B separately; any difference combines preparation and configuration
effects and must not be attributed solely to trimming. No extra factorial run is
implicitly authorized. Neither analysis is run in this task.

## Matched structural core

Reuse the unique global affine-gap alignment of complete deposited sequences
(match +2, mismatch -1, gap open -10, extension -0.5, including terminal gaps).
Keep a residue pair iff it is identical, both residues have selected occupied
N/CA/C/O atoms, and neither position is archive-annotated as an expression tag.
Exclude alignment gaps, substitutions, missing coordinates, incomplete backbones
and tags with explicit reasons. Fail ambiguous alignment or output numbering.
No pocket proximity, manual residue choices, or detector output enters selection.

There are 137 retained residues per state; 84/221 apo and 44/181 holo positions
are excluded. All 24 primary reference residues remain. Both PDB outputs use
chain A and the original holo author residue numbers, with complete reverse maps.
Sequence gaps and TER records are retained. Coordinates, selected occupancy and
original B factors are preserved; no coordinate fitting, atom rebuilding, caps,
relaxation or optimization. Remove other chains and all nonprotein content.
Raw and output hashes, every retained/excluded position, and reasons are in
matched_core_manifest.json. A core that loses reference residues fails; do not
silently shrink the reference. Discontinuous chains may still affect NMA.

## Reference-site definition and cutoff sensitivity

Protein membership is the selected polypeptide(L) entity with integer label_seq_id
and one of the 20 standard amino acids; modified residues require review. ATOM vs
HETATM alone does not define protein. Exclude waters, other nonpolymers, H/D by
element, and zero-occupancy atoms. Invalid values fail. Choose a coherent nonblank
alternate conformer by greatest summed heavy-atom occupancy, lexical tie-break,
plus shared blank-alt atoms; duplicate atom names fail. N3C is selected by explicit
component/chain/model metadata and verified ABT-737 synonym, not ligand size.

PRIMARY contact shell: at least one selected protein heavy atom within <=5.0 A
of a selected N3C heavy atom. Keep 5.0 because it predates local detector results.
Preregister 4.5 A as sensitivity; 4.0 A is a pre-run diagnostic count, not a
candidate for selecting the best future performance. Counts independently
reconfirmed before execution: 5.0 -> 24, 4.5 -> 22, 4.0 -> 19. Never choose
whichever cutoff favors a method. Recompute each reference centroid from that
cutoff's complete reference set; same method candidates, no reranking for sensitivity.

## Primary geometric recovery and comparable centroids

PRIMARY: a candidate's native pocket centroid is within **<=4.0 A** of the
preregistered reference centroid in the evaluated input coordinate frame.
Top-five recovery is yes if any of the first five ranked candidates qualifies.
First recovered rank is the smallest one-based native rank satisfying the same
rule, null if none; also report all-emitted-candidate coverage separately.

Reference center: arithmetic mean of one CA per reference residue in the evaluated
input (apo CA coordinates for apo; holo CA coordinates for positive control).
This pre-execution amendment replaces the former all-heavy-atom center for primary
recovery to match the reference-center definition in Lacuna's benchmark source.
Legacy heavy-atom centers remain secondary and are never interchanged silently.
comparison_reference.json freezes both CA and heavy-atom centers by cutoff/state.

Lacuna candidate center: `PocketCluster.centroid`, serialized as `pockets[].centroid`
in pocket_report.json, the unweighted mean of member-pocket native centers in the
audited clusterer. NMA adds displacements in the input Cartesian frame without a
global recentering/rotation. Use those centers directly; do not substitute the
mean of lining-residue coordinates. Save backend/frame provenance. Any backend
or coordinate-frame change invalidates this adapter and requires amendment.

P2Rank candidate center: the native `center_x`, `center_y`, `center_z` columns of
`*_predictions.csv`, in the supplied input Cartesian frame. Strip header whitespace,
require finite coordinates and valid native ranks. No re-centering or replacement
by residue means. The schema is also documented by Lacuna's P2Rank adapter source.
Both methods therefore compare cavity-center coordinates with the exact same
CA reference center for the same input. No cross-frame apo/holo subtraction or
alignment of different inputs is performed.

Source compatibility: Lacuna cryptic_benchmark.py uses a 4.5 A contact shell,
CA reference centroid and 4.0 A center-distance threshold. Its current combined
headline accepts centroid distance <=4 OR Jaccard >=0.25. Our primary endpoint
deliberately uses its geometric component alone and our original 5.0 A shell;
it is not numerically identical to the source headline. At the 4.5 A sensitivity
shell, optionally report the source-style OR result as a labelled SECONDARY
reproduction diagnostic, never replacing primary recovery. The published 5.6 A
showcase center would not pass a <=4 A geometric rule by itself.

## Secondary metrics and runtime

Let R be the complete reference set at the stated cutoff, P the unique predicted
lining-residue set in the supplied chain. Normalize P2Rank `residue_ids` (A_93)
and Lacuna `lining_residues` (ALA93:A) through the frozen processed numbering map;
unknown IDs or conflicting names fail, never disappear. Native lining sets may
have different size/definitions, which is why overlap is secondary.

- Reference-site recall = |P intersection R| / |R|.
- Predicted-site precision = |P intersection R| / |P|.
- Jaccard = |P intersection R| / |P union R|.
- Also report intersection count, |P|, |R|, native center distance and native rank.
- Minimum geometric distance = minimum heavy-atom distance between P and R in
  the original evaluated input; zero if atoms overlap. For holo also report
  minimum P-to-archived-N3C heavy-atom distance in the original holo frame.

Empty P gives precision/recall/Jaccard zero and minimum distance null; a valid
native center can still satisfy primary geometry. Empty R is invalid. No
predictions after a successful complete run gives recovery false and rank null.
Tie scores preserve native rank/file order; malformed or duplicate ranks fail.
Runtime is wall time from method start through ensemble generation, detection,
ranking and output completion; exclude installation, downloads, preprocessing
and evaluation. Record hardware, CPU time if available, threads, seeds and status.

## Confounders and overlap audit

Apo includes a 40-residue region absent from the holo construct and additional
expressed/tagged or unresolved-in-holo regions. These may affect NMA even when
remote from the groove; no distance-based trimming is used. NMR minimized average
versus X-ray, crystal packing, missing sidechain atoms, conformational differences,
numbering, insertion/deletion handling, alternate locations and ligand names
remain confounders. Holo SER A23 has alternate IDs A/B; A is selected. Missing
holo residues cannot contribute to the contact shell. Whole-protein sequence
alignment is unique, but global biological equivalence is not proven by alignment.

Audit: Lacuna EXAMPLE_OVERLAP and BENCHMARK_OVERLAP confirmed. Neither exact PDB
ID occurs in downloaded CryptoBench fold lists; learned-ranker and surface-fit
code use training folds. Finding: NO_EVIDENCE_OF_TRAINING_OVERLAP within the audit;
target/homolog/artifact-level training overlap remains UNKNOWN. P2Rank's searched
42 root membership lists (including CHEN11 and JOINED) contain neither exact ID;
same-target/homology and exact shipped-model lineage remain UNKNOWN. No training
leakage is inferred from showcase/benchmark appearance. See benchmark_overlap_audit.json.

## Independent second-system eligibility, before candidate discovery

Experiment 1B/2 must use an independent therapeutically meaningful oncology target
with defensible public apo/ligand-bound structures, a meaningful pocket/conformational
change, and objective ligand-defined validation. It must not appear in Lacuna's
examples/benchmarks and must have no identified fitting/training overlap for learned
components. Audit structures, alternate IDs and homologs before accepting it;
unresolved overlap cannot support a clean independent-validation claim. Do not
select candidates by favorable Lacuna performance. No second system is selected
or searched in this task; these requirements precede candidate discovery.

## Failures, provenance and stop

A failed run includes nonzero exit, missing/malformed outputs, invalid coordinates
or ranks, hash mismatch, unexpected preprocessing/backend/model/sequence-feature
change, ambiguity or incomplete execution. Mark FAILED and retain actual errors;
performance is null, not a scientific miss or mock substitute. Lacuna source has
fallback branches (surface model -> alpha, NMA -> random for too few CA atoms,
degenerate eigenmodes, optional sequence/ranker fallbacks). Later wrappers must
detect and reject these routes, not rely solely on exit code zero. No silent fallback.

Use only experiment-local outputs and environments. Never alter audit/historical/
or ../ep4-original. No historic sequences/outputs are inputs. Run the complete
experiment tests and preflight, commit all material and create the preregistration
tag. Subsequent methodological changes require a new dated amendment and commit,
never an amended anchor. Stop now: no P2Rank, Lacuna, docking, Boltz, RFdiffusion,
ProteinMPNN, ESMFold or molecular-design execution is authorized.
'''

README = '''# BCL-XL reproduction and pipeline-validation benchmark

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
'''

PREREG = '''# BCL-XL preregistration

- Classification: **reproduction and pipeline validation**, not independent or blinded validation.
- Prior exposure: Lacuna README showcase and curated BCLXL benchmark use 1LXL/2YXJ;
  prior results are known. Example/benchmark appearance does not establish training leakage.
- Raw structures: RCSB 1LXL chain A/model 1, 2YXJ chain A/model 1 and N3C ligand D
  (author A1001); unchanged mmCIF hashes in manifests/input_manifest.json.
- Matched core: identical unique sequence-aligned pairs with occupied N/CA/C/O
  in both structures, excluding archive-annotated expression tags in either;
  **137 residues per state**, no pocket-proximity trimming. Coordinates, occupancy
  and B factors retained; gaps retained; no reconstruction. Full manifest under data/processed/.
- Primary reference contact cutoff: **5.0 A, 24 residues**. Sensitivity: **4.5 A,
  22 residues**. Diagnostic only: 4.0 A, 19 residues. Never select by detector performance.
- Primary recovery: native candidate center **<=4.0 A** from the reference-residue
  **CA centroid in the same input frame**, top five; first recovered rank also reported.
  This uses the geometric component of Lacuna's benchmark, not its combined OR headline.
- Secondary: reference recall, predicted-site precision, Jaccard, intersection
  count/site sizes, minimum distances, heavy-atom-center sensitivity and runtime.
- Positive control: identical matched-core holo-minus-ligand file for both methods.
- Analysis A: Lacuna source 960523caa75c86f04111970da47c3c06ceeda8b4 (1.2.0), NMA,
  surface-fusion/no-sequence, learned-fused, 20 conformers plus input on full apo A.
  Approximate reproduction: showcase backend/seed/sequence features not established.
- Analysis B: same Lacuna revision, NMA/alpha/learned versus P2Rank 2.5.1 default
  (9808a7723be9a94e2ffc21ab5f724cb6ae4ba01e), Java 17, one thread, seed 42.
  NMA cutoff 8 A, 10 modes, maximum RMSD 2 A, seed 42; no optional sequence/MD/Boltz.
  Exact settings and future wrapper requirements are in configs/methods.json and PROTOCOL.md.
- Frozen Git SHA: **ANCHOR_SHA_PENDING**.
- Anchor tag: **cryptic-pocket-bclxl-preregistered-v1**. A commit cannot contain its
  own literal SHA; a subsequent receipt-only commit records the anchor SHA here.
  That receipt changes no scientific definitions. Never amend or move the anchor.
- Overlap: Lacuna EXAMPLE_OVERLAP/BENCHMARK_OVERLAP confirmed. Both methods have
  NO_EVIDENCE_OF_TRAINING_OVERLAP in the bounded exact-ID audit; full target/homolog
  and shipped-model fitting membership remains UNKNOWN. See benchmark_overlap_audit.json.
- Failed run: nonzero exit, missing/malformed/incomplete output, invalid center/rank,
  hash mismatch, unapproved configuration, or backend/model/feature fallback. Preserve
  FAILED and actual errors; failed performance is null. Valid zero candidates is a miss.
- **No silent fallback.** Upstream fallback branches must be rejected by tested
  wrappers before later execution; dependencies and model artifacts must be locked.
- **STOP AFTER PREREGISTRATION.** No detector, docking, structure-generation or
  molecular-design execution is authorized. No second-system search or selection yet.

Every later methodological change requires a new reasoned, timestamped amendment
and new commit. PROTOCOL.md is the detailed specification; AMENDMENTS.md explains
the pre-execution changes. The anchor contains raw/processed hashes, tests and preflight.
'''


def apply():
    outputs = []
    for name, text in [('PROTOCOL.md', PROTOCOL), ('README.md', README), ('PREREGISTRATION.md', PREREG)]:
        path = ROOT / name
        if path.exists() and name != 'PREREGISTRATION.md':
            archive = ROOT / 'manifests/pre_review' / name
            if path.read_bytes() not in (archive.read_bytes(), text.encode()):
                raise ValueError(f'Unexpected prior document version: {name}')
        path.write_bytes(text.encode('utf-8'))
        outputs.append(path)
    cfg_path = ROOT / 'configs/reference_site.json'
    cfg = json.loads(cfg_path.read_text())
    cfg['protocol_version'] = 2
    cfg['sensitivity_contact_cutoff_angstrom'] = 4.5
    cfg['diagnostic_contact_cutoff_angstrom'] = 4.0
    cfg['future_recovery'] = {'criterion': 'native_candidate_center_to_reference_CA_centroid',
                              'maximum_distance_angstrom_inclusive': 4.0, 'primary_top_k': 5,
                              'jaccard_role': 'SECONDARY_ONLY'}
    cfg_path.write_bytes(canonical_bytes(cfg)); outputs.append(cfg_path)
    env_path = ROOT / 'manifests/environment_plan.json'
    env = json.loads(env_path.read_text())
    env['planned']['lacuna'].update({'version': '1.2.0', 'source_commit': '960523caa75c86f04111970da47c3c06ceeda8b4',
                                    'detectors': {'analysis_A': 'surface-fusion (no-sequence)', 'analysis_B': 'alpha'},
                                    'sources': ['https://github.com/mooreneural/lacuna/tree/960523caa75c86f04111970da47c3c06ceeda8b4'],
                                    'rankers': {'analysis_A': 'learned-fused', 'analysis_B': 'learned'}})
    env['review_amendment'] = 'Pre-execution review 2026-09-16; original plan retained in manifests/pre_review/manifests/environment_plan.json.'
    env_path.write_bytes(canonical_bytes(env)); outputs.append(env_path)
    print('Applied explicit pre-execution protocol/configuration amendment; original documents retained.')
    return outputs
