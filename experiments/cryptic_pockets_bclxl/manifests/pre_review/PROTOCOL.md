# BCL-XL reference-site protocol, version 1

Preregistered on 2026-09-16 before acquisition/contact calculation and before any
detector execution. Scope: Steps 1–5 only. Changes to site definitions or recovery
thresholds after future method results must be labelled exploratory and versioned.

## Question

Can an ensemble-based cryptic-pocket method recover a ligand-defined BCL-XL binding site from an apo structure, and how does this compare with a static pocket detector?

## Hypothesis

An ensemble-based method may recover a known ligand-defined site from the apo structure that is less apparent to a static detector.

There is no assumption that Lacuna will outperform P2Rank. Ligand-free does not
establish that the site is cryptic; this is a candidate benchmark of site recovery.

## Methods to compare later

A. Static pocket detection: P2Rank 2.5.1, default model, as a reproducible baseline.

B. Ensemble-based detection: Lacuna (lacuna-pockets 1.1.0), default CPU
elastic-network normal-mode (nma) backend, explicitly selected to avoid automatic
backend changes. Freeze all later parameters, seeds, thread counts and software
artifacts before execution. Neither method is run in Steps 1–5.

## Verified public structures

Checked 2026-09-16 against [RCSB 1LXL](https://www.rcsb.org/structure/1LXL),
[RCSB 2YXJ](https://www.rcsb.org/structure/2YXJ), and
[RCSB component N3C](https://www.rcsb.org/ligand/N3C).

- 1LXL: BCL-XL minimized-average NMR structure; SOLUTION NMR, one submitted model,
  chain A, 221 deposited residues, no nonpolymer ligand listed.
- 2YXJ: Bcl-xL complex with ABT-737; X-RAY DIFFRACTION, 2.20 A, protein chains
  A and B (181 deposited residues each). N3C copies have label asym IDs D and F
  (author chains A and B). Glycerol and chloride also occur.
- Both are assigned human BCL-XL / UniProt Q07817. Different constructs and
  experimental methods limit comparability. No substitute structure is permitted.

Exact archive titles, timestamps and hashes are captured in input_manifest.json.

## Reference-site definition

Canonical inputs are unmodified RCSB mmCIF files: this format retains polymer
sequence, label/auth identifiers, ligand entities and missing-residue metadata.
Use deposited model number 1 and protein label chain A in each structure.
Chain A is selected by identifier before contact calculation, not by site size.
In 2YXJ select exactly one nonpolymer N3C in label chain D / author chain A;
verify the component synonym is ABT-737. Absent or duplicate selections fail.
The second protein/ligand copy is excluded from the primary reference by this
preregistered chain rule; no symmetry mates are added.

A reference residue contains at least one selected heavy atom at Euclidean
distance **<= 5.0 A** from any selected heavy atom of the specified N3C instance.
This inclusive cutoff captures a local contact shell including close packing
contacts while avoiding a large arbitrary neighborhood. It is an operational
geometric definition, not an energetic interaction claim. No residues are chosen
by name or historical knowledge. No cutoff tuning against detector results.

A protein residue belongs to the selected `polypeptide(L)` entity, has an integer
`label_seq_id` in its declared polymer sequence, and is one of the 20 standard
amino acids. ATOM/HETATM alone does not determine protein membership. Modified
or nonstandard polymer residues fail explicitly pending review. Nonpolymer
amino acids, waters, ions, glycerol and other ligands do not count as protein.
Hydrogen and deuterium are excluded using the element field, not atom names;
chlorine is a heavy atom. Exclude zero-occupancy atoms; invalid coordinates or
occupancy fail. Missing atoms are not rebuilt.

Alternate conformers: for each residue choose the nonblank alt ID with greatest
summed occupancy (tie: lexical ID). Include shared blank-alt atoms and that
conformer only; fail duplicate atom names. Apply the same rule to the ligand.
This avoids mixing alternate conformers; report their presence.

Mapping: globally align the full deposited polymer sequences from
`_entity_poly_seq`, including residues without coordinates, using Biopython's
PairwiseAligner with match +2, mismatch -1, gap open -10, extension -0.5,
including terminal gaps. Require a unique optimal alignment; ambiguity fails
for human review. Map identical aligned amino acids only. Record mismatches,
gaps and absent apo coordinates as unmapped with distinct reasons. Join sequence
positions to coordinates by label sequence ID, retaining author numbering and
insertion codes as annotations. Do not equate author numbers between files.
Record every aligned position and both full sequences, plus all unobserved
sequence positions. No structural prediction or missing-residue reconstruction.

Reference centroid: unweighted arithmetic mean of all selected heavy-atom
coordinates in all reference protein residues (including atoms beyond the contact
cutoff). Store this in the original holo Cartesian frame. Also store the centroid
of all heavy atoms of mapped apo residues in the original apo frame, and the
holo ligand heavy-atom centroid as a separately named quantity. Never compare
coordinates from the two original frames directly.

## Primary future metrics

Let R be the reference set in the evaluated structure: all holo reference
residues for holo-minus-ligand, and their successfully mapped coordinate-bearing
apo counterparts for apo. Publish |R| and mapping coverage; missing mappings
must never be silently dropped from coverage reporting. Let P be one predicted
pocket's unique lining-residue set, resolved to label sequence IDs in the same
input chain. Use native reported lining residues; adapters must document the
exact field and numbering interpretation before detector execution. If an output
does not supply lining residues, amend and preregister a common geometric adapter
before running either method. Unresolvable residue IDs invalidate evaluation.

- Residue overlap: intersection count |P intersect R|, reference coverage
  |P intersect R| / |R|, and precision |P intersect R| / |P|. Empty P has zero
  precision/coverage; empty R makes evaluation invalid.
- Jaccard similarity: |P intersect R| / |P union R|.
- Centroid distance: Euclidean distance in A between the centroid of all heavy
  atoms of P in the original input structure and the corresponding reference
  protein centroid defined above. Empty P gives null with an explicit reason.
  For ensemble predictions use residue identities in the original apo frame,
  not an unaligned ensemble centroid. Method-native centers can be exploratory.
- Minimum geometric distance: minimum heavy-atom distance between residues in
  P and R in that same frame (zero if they share an atom). For holo control also
  report minimum distance between P heavy atoms and archived N3C heavy atoms.
  No direct apo-to-holo ligand distance without a separately documented alignment.
- Reference-site recovery: whether any of the first five ranked pockets meets
  the criterion below. Also report recovery over all emitted pockets separately.
- Rank of first recovered site: smallest one-based native rank meeting the
  criterion, null if none; ties in score preserve native file order. Retain scores
  and all ranks. No predictions is recovery false, first rank null.
- Runtime: wall-clock elapsed seconds from detector subprocess launch to exit,
  including its ensemble generation and output writing; exclude acquisition,
  reference construction and environment installation. Record CPU time if
  available, hardware, threads, seeds and exit status. Failed methods have null
  performance with FAILED status, never substituted outputs.

## Recovery criterion

A pocket recovers R when reference coverage is >= 0.50 **and** Jaccard similarity
is >= 0.25. The conjunction requires recovery of at least half the reference
while penalizing very broad pockets. Top-five success is the primary yes/no
endpoint. Distances are complementary descriptive metrics, not adjustable
success thresholds. These are operational preregistered thresholds; they do not
establish binding affinity, druggability or clinical utility.

## Controls

1. Apo 1LXL chain A is the proposed cryptic/opening challenge.
2. Ligand-removed holo 2YXJ chain A is a positive-control structural state.

Later prepare the holo control by retaining selected protein coordinates and
removing all nonprotein molecules in a derived file, preserving the immutable
raw file. This checks whether a method recovers the site when the experimentally
observed ligand-associated protein conformation is provided, separating failures
to identify this geometry from limitations in sampling it from apo. Removing a
ligand does not relax the holo conformation into an apo state. Control files and
method executions are deferred beyond this task.

## Potential confounders

Differing full sequences, chain numbering, insertion codes, deletions, engineered
construct boundaries and unresolved coordinates can alter mapping and pockets.
Aligning deposited sequences prevents unresolved loops from being mistaken for
construct deletions; report both independently. Standard-residue substitutions
are reported and not silently mapped. Poor or ambiguous alignments require review.
Missing sidechain atoms can shrink the reference shell or shift centroids.

The NMR minimized average is not a measured trajectory or conformational
ensemble. Crystallographic resolution, crystal packing, the second protein copy,
and flexible regions may affect geometry. Neither ligand absence nor apo/holo
differences alone establish crypticity or ligand-induced causality. Alternative
locations and ligand aliases require explicit choices. A single chain/copy is
not evidence of robustness across structures. Learned detector training-set
overlap with these old public structures needs checking before future claims.

## Execution and provenance boundary

Use only this experiment directory for new data, code, environments and logs.
Never modify audit/historical/ or ../ep4-original or use historical targets,
sequences or outputs. Raw acquisition is create-only with SHA-256 receipts;
existing inputs must verify or fail, never be replaced. Every provided command
records timestamps, command, input/code/output hashes, versions and status.
Failures retain actual exceptions. Synthetic structures are tests only.

Stop after the deterministic evaluator and its complete tests. No P2Rank,
Lacuna, docking, Boltz, RFdiffusion, ProteinMPNN, ESMFold or molecular design.
