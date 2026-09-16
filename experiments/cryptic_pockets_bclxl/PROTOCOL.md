# BCL-XL reproduction and pipeline-validation benchmark

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
