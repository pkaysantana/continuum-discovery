# Pre-execution review: BCL-XL cryptic-pocket benchmark (Steps 1–5)

Independent scientific-methods and code review, performed 2026-09-16 before any
detector execution. No files were modified. No P2Rank, Lacuna, docking, or design
was run. Findings below are separated into VERIFIED (with source) and UNRESOLVED.

Reviewed: `PROTOCOL.md`, `README.md`, `configs/reference_site.json`,
`src/reference_site.py`, `src/provenance.py`, `src/run.py`,
`tests/test_reference_site.py`, `data/processed/reference_site.json`,
`data/processed/structure_inspection.json`, `data/raw/1LXL.cif`,
`data/raw/2YXJ.cif`, manifests and run receipts.

General assessment: the geometric core is careful, deterministic, and honestly
caveated. It is better than most work of this kind. The problems that matter are
not in the contact arithmetic. They are in benchmark independence, in a large and
unmitigated apo/holo input asymmetry, in a metric that penalises pocket size, and
in the absence of any durable anchor for the preregistration claim.

---

## 1. Benchmark independence — CHANGE BEFORE EXECUTION

**VERIFIED.** BCL-XL with this exact structure pair is Lacuna's own showcase
example, and the developer has already published quantitative results on it using
the same metric family this protocol preregisters.

From the Lacuna repository README (https://github.com/mooreneural/lacuna):

> "Apo BCL-XL (1LXL): a Lacuna-detected pocket (blue) opening onto the groove
> where ABT-737 (orange, from the holo structure 2YXJ) binds, a site never shown
> to the detector. With `--detector surface-fusion` this site is recovered at
> rank 2, Jaccard 0.36, centroid 5.6 Å."

1LXL, 2YXJ, and ABT-737 therefore appear in Lacuna's **documentation and headline
figure**, and in a **published benchmark result** reporting rank, Jaccard, and
centroid distance. These are three of the five primary metrics in `PROTOCOL.md`.
This is decisive: as configured, the BCL-XL system cannot function as an
independent generalisation test. It is a reproduction case.

**Recommendation.** Relabel the BCL-XL system throughout `PROTOCOL.md` and
`README.md` as a **reproduction / pipeline-validation case**, not an independent
test of generalisation. State the developer's published values as the
pre-existing expectation, and frame the endpoint as "does our independent
pipeline reproduce the published result", which is a legitimate and useful thing
to establish before testing generalisation elsewhere.

**Second, separate problem: configuration mismatch.** The published result was
obtained with `--detector surface-fusion`. `PROTOCOL.md` preregisters the
"default CPU elastic-network normal-mode (nma) backend". Detector and ensemble
backend are different axes, but the net configuration is not the published one.
A run under the preregistered configuration therefore **cannot** be reported as a
failed or successful reproduction of "rank 2, Jaccard 0.36, centroid 5.6 Å".
Either add a reproduction arm matching the published configuration exactly, or
state plainly in the protocol that the configuration differs and that the
published numbers are not the comparator.

### Fitting/training data — UNRESOLVED (no leakage claim made)

Lacuna does contain learned components, so the question is real rather than
rhetorical:

- **VERIFIED.** Ranking uses "a fitted linear model over 23 geometric and
  ensemble-derived features", with an optional PLM-assisted ranker (`[plm]`
  extra, PyTorch/ESM-2). `tests/test_ranker_integrity.py` confirms "weights"
  "fitted on the conformer-invariant features" (23 geometry features, optionally
  4 PLM features).
- **VERIFIED.** Lacuna is evaluated on CryptoBench's "designated test fold"
  (55.6% top-5 default, 66.1% with the PLM ranker), and ships a CryptoBench
  fold-ID mapping: `tests/test_fold_ids.py` tests a `pdb_id_of()` function that
  resolves structure identifiers to four-character PDB IDs used as "fold keys".
  A PR from the CryptoBench author (skrhakv, PR #1) corrected Lacuna's citation
  of the dataset.
- **VERIFIED.** CryptoBench comprises 1107 structures grouped by UniProt ID,
  clustered by sequence identity, with predefined cross-validation splits.
- **UNRESOLVED.** Whether BCL-XL (UniProt Q07817) is in CryptoBench at all and,
  if so, whether it falls in a **training** fold used to fit the 23-feature
  ranker, or in the held-out test fold. A web search summary asserted Q07817 is
  present, but I could not retrieve a primary quotation; repeated fetches of the
  CryptoBench paper were blocked in this environment. **I am explicitly not
  calling this training leakage.** There is no evidence of it.

**This is directly checkable locally and must be resolved before any performance
claim.** Lacuna ships the fold map with the package. After installing
`lacuna-pockets` 1.1.0, look up `1lxl`, `2yxj`, and Q07817 in the shipped fold
map and record the fold assignment in the manifests. If either structure or the
UniProt cluster sits in a fitting fold, the case is additionally compromised and
must be reported as such. If it sits in the test fold, say so, and note that the
developer's published 55.6%/66.1% headline figures then already include it.

**P2Rank — UNRESOLVED.** VERIFIED: P2Rank's prediction model is trained on
CHEN11 (251 proteins, 476 ligands); COACH420 and HOLO4K are disjoint evaluation
sets. Whether 1LXL or 2YXJ appears in `chen11.ds` or the JOINED set could not be
verified (fetch of the dataset list was blocked). Check `chen11.ds` and
`joined.ds` in https://github.com/rdk/p2rank-datasets before reporting P2Rank
performance, and record the result either way.

---

## 2. Reference-site definition — PASS WITH CAVEAT

The 5.0 Å inclusive protein-heavy-atom to ligand-heavy-atom criterion is
preregistered, operationally precise, and correctly implemented. Hydrogen and
deuterium are excluded by the `type_symbol` element field rather than by atom
name; chlorine is correctly retained as a heavy atom; zero-occupancy atoms are
excluded; comparison uses squared distances with an inclusive `<=`. The protocol
explicitly disclaims any energetic interpretation and forbids cutoff tuning
against detector results. All of that is correct practice.

**The reference set is robustly insensitive to the cutoff choice.** This can be
computed now from the already-archived per-residue minimum ligand distances in
`data/processed/reference_site.json`, with no detector output involved and
therefore no tuning risk:

| Cutoff | Reference residues | Change from 5.0 Å |
| --- | --- | --- |
| 5.0 Å (preregistered) | 24 | — |
| 4.5 Å | 22 | loses auth 149 (4.614 Å), 194 (4.698 Å) |
| 4.0 Å | 19 | additionally loses 145 (4.007 Å), 108 (4.141 Å), 197 (4.180 Å) |

**Recommendation.** Keep 5.0 Å as the **primary** definition and add 4.5 Å as a
**preregistered sensitivity analysis**. It is not unnecessary, because 4.5 Å is a
common convention and a reader will ask; but it should not become primary,
because switching now — after the 24-residue set is known and before any
performance is observed — has no scientific justification and only invites the
suspicion the protocol is designed to avoid. A 4.5 Å arm retains 22 of 24
residues, so conclusions are very unlikely to hinge on it, and saying so with the
number attached is stronger than choosing between the two.

**CAVEAT — UNRESOLVED.** How Lacuna's published benchmark (i.e. CryptoBench)
defines ligand-contact reference residues, and at what cutoff, could not be
verified; paper fetches were blocked. This matters specifically because item 1
makes this a reproduction case: comparing our Jaccard against the published
Jaccard 0.36 is only meaningful if the reference-residue definitions match.
Resolve the CryptoBench definition and record it before making any comparison to
published numbers.

**Sanity check on the residue identities.** The 24 residues (holo author
numbering) are 93, 96, 97, 100, 101, 104, 105, 108, 126, 129, 130, 136, 137, 138,
139, 141, 142, 145, 146, 149, 191, 194, 195, 197. These fall in the α4, α5, and
α8 regions and correspond to the canonical BH3-binding groove that ABT-737
occupies. The purely geometric, name-blind procedure recovered the biologically
correct site. Minimum distance 3.07 Å, maximum 4.70 Å; no borderline cluster at
the cutoff.

---

## 3. Apo/holo comparability — CHANGE BEFORE EXECUTION

This is the most consequential finding in the review. The mapping procedure is
sound; the **inputs are not comparable**, and the asymmetry is large, systematic,
and currently unmitigated.

### The mapping procedure itself is defensible, and 24/24 is genuine

**VERIFIED by reading the source, not the README.** Mapping globally aligns the
full deposited `_entity_poly_seq` polymer sequences, including residues without
coordinates, requires a **unique** optimal alignment (a second optimal alignment
raises `Ambiguous optimal sequence alignment`), maps only aligned positions with
**identical** amino acids, joins sequence positions to coordinates by
`label_seq_id`, and treats author numbers and insertion codes as annotations
only. Mismatch, apo alignment gap, and missing apo coordinates are recorded as
three distinct unmapped reasons. `protein()` additionally cross-checks every atom
row against the declared polymer sequence and raises if they disagree.

**The 24/24 mapping does not conceal ambiguity from duplicated or repeated
regions.** The two sequences are identical apart from one clean 40-residue
internal deletion:

- apo: `...RTEAPEGTESE` **`METPSAINGNPSWHLADSPAVNGATGHSSSLDAREVIPMA`** `AVKQALREAGDEF...`
- holo: `...RTEAPEGTESE` `AVKQALREAGDEF...`

There is no repeat, no tandem duplication, and no alternative equally scoring
placement of that gap, so the unique-alignment requirement is satisfied for a
real reason rather than by luck. The mapping is trustworthy.

One honest limitation, already stated in the README and worth keeping prominent:
44 deposited holo residues have no coordinates and therefore could not
contribute contacts. The 24-residue reference is a **lower bound** on the
biological site, and 24/24 coverage is not evidence of a complete site.

### The inputs differ far more than the protocol mitigates

**VERIFIED from the raw files:**

| Property | apo 1LXL | holo 2YXJ chain A |
| --- | --- | --- |
| Method | SOLUTION NMR, **minimized average**, 1 conformer submitted | X-ray, 2.20 Å |
| Deposited polymer | 221 residues | 181 residues |
| Residues with coordinates | 221 | 137 |
| 40-residue flexible loop | present and fully modelled | deleted from the construct |
| C-terminal `LEHHHHHH` tag | present and fully modelled | no coordinates (label 162–181 unobserved) |

So the apo input carries **~84 more residues bearing coordinates than the holo
input** — roughly 60% more structure — and ~52 of those residues are appendages
that simply do not exist as coordinates on the holo side.

**Those appendages are poorly determined and fully extended.** 1LXL's per-atom
uncertainty column separates them sharply from the core:

| Region (apo label IDs) | CA x-coordinate range | Uncertainty column |
| --- | --- | --- |
| Core (e.g. 10–19, 95–105) | ~ −3 to +22 | 0.28 – 2.16 |
| 40-residue loop (50–65) | ~ −38 to −49 | 17.2 – 18.5 |
| C-terminal tag (214–221) | ~ +35 to +44 | 12.1 – 17.9 |

The apo reference-site centroid is (14.87, −2.20, 1.07). The loop tail is
therefore roughly 55–65 Å from the binding groove.

**What follows, and what does not.** The loop does **not** occlude the BH3
groove; it projects away from it. So the naive worry — that the apo site is
artificially buried — is not supported, and I am not claiming it. The real
consequences are different and still serious:

1. **The NMA backend is the wrong tool for this input.** An elastic-network
   normal-mode ensemble is driven by the softest modes of the structure it is
   given. Two long, essentially undetermined, fully extended tails will dominate
   those modes. The ensemble will largely explore tail motion rather than groove
   opening. This is a specific and predictable failure mode of the preregistered
   configuration on this specific input.
2. **Top-5 ranking is diluted.** Two extended tails present a large amount of
   spurious convex surface. Any detector will emit candidate pockets along them.
   Since the primary endpoint is recovery within the first five ranked pockets,
   spurious tail pockets can displace the true site from the top five without any
   failure of site detection.
3. **Runtime and pocket counts are not comparable** between the apo challenge
   (221 residues) and the holo positive control (137 residues). Any runtime or
   pocket-count contrast between the two conditions is confounded by size.
4. **A minimized average is not a physical conformer.** `_struct.title` is
   literally "NMR STRUCTURE OF BCL-XL ... MINIMIZED AVERAGE STRUCTURE" with
   `conformers_submitted_total_number = 1`. Averaging Cartesian coordinates over
   an NMR ensemble and minimising produces side-chain packing and cavity geometry
   that are averaging artifacts. For pocket **detection** specifically — which is
   a question about cavity geometry — this is a weak input. The protocol notes it
   is "not a trajectory or ensemble", which is correct but understates it: it is
   also not a conformer.

**Recommendation (leakage-free and preregisterable).**

- **Equalise the evaluated region before running.** Preregister an
  input-preparation rule that restricts both inputs to residues that are (a)
  present in both constructs and (b) modelled in both: exclude the apo-only
  40-residue loop (apo label 49–88) and the C-terminal tag/linker region that is
  unobserved in holo (holo label 162–181 and its apo counterparts). Crucially,
  justify this **solely on construct parity and observability**, fix it in the
  protocol before any detector runs, and record the excluded ranges and the
  residue counts of both prepared inputs. Nothing about this rule depends on
  detector output, so it introduces no tuning and no leakage. Preserve the
  immutable raw files and write derived inputs, exactly as the protocol already
  requires for the holo control.
- **If the unequalised inputs are kept instead**, then state explicitly in the
  protocol that the apo condition carries ~52 extra poorly determined residues
  absent from holo, that the NMA ensemble is expected to be dominated by them,
  and that a negative apo result is therefore uninterpretable as evidence about
  groove opening. That is a defensible choice only if written down in advance.
- **Consider a preregistered alternative apo.** 1MAZ is the X-ray apo BCL-XL from
  the same 1996 work, in which the ~60-residue α1–α2 loop was shown to be
  flexible and dispensable. An X-ray apo would remove both the minimized-average
  artifact and, if the construct matches, the loop asymmetry. **Suitability
  unverified**: the construct boundaries, resolution, chain content, and any
  non-water ligands in 1MAZ must be checked, and it must be screened against
  items 6 and 7 of the independence requirements below. Do not swap the apo
  structure on the basis of which one performs better.

---

## 4. Reference geometry — PASS WITH CAVEAT

No hidden inconsistency of the kind asked about. I specifically checked for
residue-centroid versus atom-centroid mixing and did not find it.

- **Contacts** use the minimum heavy-atom-to-heavy-atom distance, computed with
  squared distances and an inclusive comparison. Correct, and tested at the
  boundary (5.000001 Å excluded, 5.0 Å included).
- **Centroids are atom centroids throughout**, consistently. The reference
  centroid is the unweighted mean of *all* selected heavy atoms of the reference
  residues — 206 atoms in the holo frame, and 206 atoms in the apo frame for the
  mapped counterparts. The matching counts confirm no side-chain atoms are
  missing from any of the 24 holo reference residues, which is a genuinely
  favourable property of this particular pair.
- **Frames are handled correctly.** Apo, holo, and ligand centroids are stored
  separately with explicit frame labels, and the protocol forbids subtracting
  coordinates across the two original frames. `math.fsum` is used to reduce
  accumulation error. Good.
- **Alternate conformers** are resolved per residue by greatest summed occupancy
  with a lexical tie-break, blank-alt atoms are shared into the selected
  conformer, and duplicate atom names after selection are a hard failure. This is
  deterministic and avoids mixing conformers. Holo Ser A23 has altlocs; alt A is
  selected by the occupancy rule; the ligand has none.

**CAVEAT, definitional not erroneous.** Because the reference centroid averages
*all* heavy atoms of contacting residues, including atoms pointing away from the
ligand, it is displaced from the ligand itself: reference centroid
(−8.680, −16.173, 8.146) versus ligand centroid (−9.874, −14.522, 10.799), an
offset of **≈ 3.3 Å**. That is a legitimate choice, and the protocol is right
that a predicted pocket should be compared to the protein-residue centroid rather
than the ligand centroid. But it means centroid-distance results carry a built-in
~3.3 Å offset relative to the ligand centre, and any threshold-style reading of
centroid distance (including comparison against the developer's published
"centroid 5.6 Å", whose definition is unknown) must account for it. State the
offset in the protocol.

---

## 5. Metrics — CHANGE BEFORE EXECUTION

Rank semantics, tie handling (native file order), null-with-reason for empty
predictions, retention of all scores and ranks, and FAILED status with null
performance rather than substituted output are all correctly specified. The
insistence that adapters document the exact lining-residue field and numbering
interpretation *before* execution is exactly right.

**The recovery criterion systematically penalises one representation.** This is
the substantive problem. The conjunction requires reference coverage ≥ 0.50 **and**
Jaccard ≥ 0.25. With |R| = 24, Jaccard = i / (|P| + 24 − i) where i = |P ∩ R|.
The Jaccard floor therefore imposes a hard cap on predicted pocket size:

| Intersection i | Coverage | Max |P| passing Jaccard ≥ 0.25 |
| --- | --- | --- |
| 12 (minimum passing coverage) | 0.50 | 36 |
| 18 | 0.75 | 60 |
| 24 (complete coverage) | 1.00 | 96 |

So a detector that localises the site perfectly but reports a lining set larger
than ~36 residues at threshold coverage **fails the criterion despite being
right**. That is a statement about output representation, not about detection
ability.

This is not hypothetical across these two detectors. P2Rank derives lining
residues from residues adjacent to the alpha-spheres of a single predicted
pocket. Lacuna detects grid alpha-point clusters **per conformer** and then
merges corresponding pockets **across an ensemble** by greedy centroid merging.
Union-style merging across many conformers can systematically enlarge |P|
relative to a single-structure detector. Whichever detector's native |P| happens
to sit nearer |R| = 24 is advantaged by the conjunction, independent of accuracy.

**Minimum changes.**

1. Preregister a **size-independent co-primary** criterion alongside the existing
   conjunction — centroid distance to the reference protein centroid, and/or a
   DCC/DCA-style pocket-centre-to-site criterion — and report recovery under
   both. Fix the thresholds now, before results.
2. Commit to reporting the **full |P| distribution per detector and per
   condition**, so a size-driven failure is visible rather than silently scored
   as non-recovery.
3. Keep the Jaccard conjunction as a secondary stringency measure. Do not adjust
   either threshold after seeing results; the protocol already forbids this and
   should continue to.

**Runtime.** Two separate confounds, both worth stating in the protocol rather
than fixing. First, apo and holo inputs currently differ by ~84 residues (item 3),
so cross-condition runtime is not comparable until the inputs are equalised.
Second, the protocol correctly includes Lacuna's ensemble generation in its wall
clock — but that means the comparison measures "ensemble generation plus
detection" against "single-structure detection". Report both honestly and do not
frame it as a like-for-like speed comparison.

---

## 6. Controls — PASS WITH CAVEAT

The two specified conditions are the right ones, and the reasoning is correct:
apo as the opening challenge, ligand-removed holo as a positive control that
separates "cannot identify this geometry" from "cannot sample it from apo". The
protocol's explicit warning that removing a ligand does **not** relax holo into
an apo state is the key caveat and is correctly stated. Retaining the immutable
raw file while writing a derived ligand-free file is the right mechanic.

Two additions that materially improve interpretability. I am deliberately not
proposing more.

1. **A specificity / decoy control.** As specified, every metric asks only
   whether the true site was found. Nothing penalises a detector that ranks many
   pockets highly across the whole surface — which is precisely the failure mode
   that two extended tails (item 3) will provoke. Preregister: report the total
   number of emitted pockets per run, and evaluate the same metrics against a
   decoy reference — an equally sized surface-residue patch elsewhere on the same
   chain, selected by a fixed geometric rule. Without this, "recovered at rank 2"
   cannot be distinguished from "blankets the surface".
2. **Chain B as a free internal replicate.** 2YXJ contains a second protein copy
   with its own N3C (label asym F, author chain B), currently excluded by the
   preregistered chain rule. Running the identical reference construction on
   chain B costs nothing, involves no detector, and independently checks whether
   the reference definition is stable across crystallographically independent
   copies. Report it as a preregistered secondary reference, separately from the
   primary.

---

## 7. Tests and implementation — PASS WITH CAVEAT

Reviewed against the source and the test file, not the README claims.

### Verified strengths

- **Determinism is real, not asserted.** There is no RNG anywhere in the Steps
  1–5 code. `test_real_evaluation_repeatable_and_matches_saved_output` re-runs
  `evaluate()` with every `_atom_site` column reversed and requires byte-identical
  canonical JSON, which genuinely tests independence from parser iteration order.
  Residue and atom iteration are explicitly sorted.
- **No silent fallbacks.** Every abnormal condition raises: empty contact set,
  ambiguous alignment, duplicate or absent ligand instance, ligand that is not a
  non-polymer entity, nonstandard polymer residue, missing element field, NaN or
  out-of-range occupancy and coordinates, unequal mmCIF column lengths, atom
  identity disagreeing with the declared polymer sequence. I found no
  `except: pass`, no default-on-failure, and no substituted value anywhere.
- **Create-only writes behave as claimed.** `write_once` permits byte-identical
  replay and raises on differing bytes; tested directly, including that the
  original bytes survive the refusal.
- **Input integrity is enforced.** `verify_record` checks SHA-256 and byte size,
  and rejects manifest paths that escape the experiment root. Acquisition refuses
  a raw file without a receipt, a receipt without a raw file, an identity
  mismatch, an unexpected redirect, and a body that is not the expected mmCIF
  entry.
- **No holo → apo information leakage in Steps 1–5.** I checked this specifically.
  Contacts are computed only from holo protein coordinates and the holo ligand.
  Apo coordinates enter only as a membership test during mapping
  (`ap not in apo_residues`) and to compute the separately labelled apo centroid.
  No apo-side geometry is derived from the ligand, and the apo structure is never
  superposed onto holo. The protocol's prohibition on comparing the two frames is
  respected in code.
- **Failure provenance is honest.** The first acquisition attempt, blocked by
  sandbox network permissions, is retained as FAILED with its real traceback
  rather than deleted.

### Weaknesses

a) **The headline integration test is a reproduction lock, not a validation.**
   `test_real_evaluation_repeatable_and_matches_saved_output` asserts
   `first == saved`, where `saved` is the implementation's own earlier output. If
   the contact geometry were subtly wrong, this test would pass. Of the 28 tests,
   the synthetic ones do validate behaviour independently, but nothing validates
   the *real* 24-residue result against anything external.
   **Add one independent check**: recompute the reference set from `2YXJ.cif` via
   a different code path (for example `Bio.PDB` `NeighborSearch` at 5.0 Å) and
   assert set equality, or assert against the RCSB/PDBe-reported ligand
   interaction residues for N3C in 2YXJ. This is not name-based cherry-picking —
   it is an external cross-check of a geometric computation, and it is the one
   test that would actually catch a systematic error.

b) **Hard-coded identifiers in the runner.** `acquisition()` iterates the literal
   tuple `('1LXL', '2YXJ')`, and `verify_inputs()` raises unless the manifest is
   exactly `['1LXL', '2YXJ']`. Reasonable as a guard for this experiment, but it
   means the second independent case (item 8) cannot be added without editing the
   runner. Drive these from `configs/reference_site.json`.

c) **`environment()` preserves the original `captured_at`** when the plan file
   already exists, so a replay on different hardware reports a stale timestamp
   beside freshly probed values. Minor, but it weakens the "records current
   hardware" claim exactly where the protocol relies on it.

d) **`inputs()` is a glob snapshot, not a declared set.** It globs `src/*`,
   `tests/*.py`, `configs/*`, `data/raw/*`, `data/processed/*`. A file that
   disappears is silently absent from the hash list rather than an error.
   Acceptable, but it is weaker provenance than the README implies.

e) **Test runs mutate the results tree.** `tests()` sets the module-global
   `tempfile.tempdir` and the provenance tests create directories under
   `results/tmp`. Harmless and gitignored, but it means running tests is not a
   read-only operation.

f) **Inadequate provenance anchor — the most important item in this section.**
   **VERIFIED: zero files under `experiments/cryptic_pockets_bclxl` are tracked in
   git** (`git ls-files` returns nothing). The run records faithfully store a
   `repository_base_commit`, but that commit contains none of the protocol, the
   configuration, the code, the inputs, or the outputs. Consequently the entire
   preregistration claim — "Preregistered on 2026-09-16 before acquisition and
   before any detector execution" — rests on SHA-256 values recorded in JSON
   files that live inside the same mutable, uncommitted directory they describe.
   Anyone, including the agent that produced them, could regenerate the whole
   tree with a different protocol and consistent hashes. The hashes establish
   internal consistency; nothing establishes **time order**, which is the only
   thing a preregistration is for.
   **Commit the Steps 1–5 tree to git before any detector runs.** This is the
   cheapest change in this review and the one that does the most work: it fixes
   the protocol hash in a dated, externally verifiable object.

---

## 8. Independent oncology benchmark — CHANGE BEFORE EXECUTION

Because item 1 establishes that BCL-XL is a Lacuna example with published
results, a second, genuinely independent oncology case is required before any
generalisation claim. I have not run any detector and have not selected a case.

### Requirements a second case must satisfy

1. **Therapeutic relevance.** An oncology target with a real small-molecule
   programme, not merely a convenient structure.
2. **Defensible public structures.** Apo and ligand-bound entries both in the
   PDB, same species, preferably both X-ray at comparable resolution. Avoid
   minimized-average NMR entries as the apo input, for the reasons in item 3.
3. **Construct parity.** No large apo-only insertion or deletion, and no long
   modelled-but-undetermined tag or expression tag present on one side only. The
   evaluated region must be modelled in both. This requirement exists precisely
   because the current pair fails it.
4. **Genuine conformational change at the site.** A measurable apo-versus-holo
   opening (side-chain or backbone) at the ligand site, so the case tests cryptic
   pocket detection rather than static pocket detection. Quantify it before
   committing — for example by apo/holo side-chain RMSD and site SASA change over
   the ligand-defined residues.
5. **Objective ligand-defined validation.** One unambiguous, drug-like ligand
   with enough heavy atoms to define a site; not a cryoprotectant, buffer
   component, ion, or fragment-sized additive. A single copy, or a preregistered
   copy-selection rule.
6. **Absent from Lacuna's example and benchmark suite.** Verified by searching
   the repository, documentation, figures, README, release notes, and tests — not
   assumed. This is the check that the current case fails.
7. **Absent from the fitting data of every learned component.** Not in a
   CryptoBench training fold used to fit Lacuna's 23-feature ranker (checked
   against the fold map Lacuna ships), and not in P2Rank's CHEN11 or JOINED
   training sets (checked against `p2rank-datasets`). If the PLM ranker is used,
   note that ESM-2 pretraining coverage cannot be excluded and say so.
8. **Not a near-duplicate of BCL-XL.** A different fold and a different UniProt
   sequence cluster, so the two cases are genuinely two cases.

### Candidate systems — all suitability UNVERIFIED

Offered as a shortlist to screen, not as a selection. None has been checked
against requirements 6 or 7, and I have run nothing.

- **KRAS G12C switch-II pocket** (apo versus covalent-inhibitor-bound). Strongly
  cryptic and therapeutically central, so it is the obvious first thought — but
  Lacuna's quickstart command uses a `kras.pdb` input, so overlap with the
  example suite is likely and must be checked first. Unverified.
- **ABL1 myristoyl pocket** (apo versus an asciminib- or GNF-2-class allosteric
  binder). A genuine allosteric opening, oncology-relevant, distinct fold from
  BCL-XL. Unverified.
- **SHP2 (PTPN11) allosteric tunnel** (apo versus an SHP099-class binder). The
  site is formed by interdomain closure, which is a strong crypticity test.
  Unverified.
- **PDK1 PIF pocket** (apo versus an allosteric PIF-pocket ligand). Unverified.
- **MEK1 allosteric site.** Oncology-relevant, but the pocket is largely present
  in apo, so it is a weaker crypticity test. Unverified.
- **Hsp90α and BRD4 BD1.** Both are likely to fail requirement 7 (heavily
  represented in generic pocket-prediction benchmark sets) and requirement 4
  (well-formed static pockets). Mentioned to be screened out explicitly rather
  than silently. Unverified.

**Selection procedure.** Apply requirements 6 and 7 mechanically over the
shortlist, then requirement 4 quantitatively, and fix the chosen case in the
protocol **before** any detector output on it is observed. Do not select on
performance, and record the systems screened out and why, so the final choice is
auditable.

---

## Verdict summary

| Issue | Verdict |
| --- | --- |
| 1. Benchmark independence | **CHANGE BEFORE EXECUTION** (independence), **UNRESOLVED** (fitting-data lookups) |
| 2. Reference-site definition | **PASS WITH CAVEAT** (add 4.5 Å sensitivity; CryptoBench cutoff UNRESOLVED) |
| 3. Apo/holo comparability | **CHANGE BEFORE EXECUTION** (mapping itself PASS) |
| 4. Reference geometry | **PASS WITH CAVEAT** (state the ~3.3 Å centroid offset) |
| 5. Metrics | **CHANGE BEFORE EXECUTION** (size-dependent recovery criterion) |
| 6. Controls | **PASS WITH CAVEAT** (add specificity control and chain-B replicate) |
| 7. Tests and implementation | **PASS WITH CAVEAT** (provenance anchor; add one independent validation) |
| 8. Independent oncology benchmark | **CHANGE BEFORE EXECUTION** (requirements defined; candidates unverified) |

---

# NOT READY TO RUN

The geometric core is sound and I would not change the contact arithmetic. The
blockers are that the system is the tool's own showcase example, that the two
inputs are not comparable, that the success criterion depends on output
representation, and that the preregistration has no durable anchor.

## Minimum changes required before execution

1. **Relabel BCL-XL as a reproduction / pipeline-validation case**, not an
   independent generalisation test. Record the developer's published values and
   configuration (`--detector surface-fusion`, rank 2, Jaccard 0.36, centroid
   5.6 Å). Either add an arm matching that configuration, or state that the
   preregistered `nma` configuration differs and that the published numbers are
   not the comparator.
2. **Preregister an input-preparation rule that equalises the evaluated region**
   across apo and holo — excluding the apo-only 40-residue loop and the
   C-terminal tag region unobserved in holo — justified solely on construct
   parity and observability, with the excluded ranges and both prepared residue
   counts recorded. If the unequalised inputs are kept instead, state in advance
   that a negative apo result is uninterpretable.
3. **Add a size-independent co-primary recovery criterion** (centroid distance
   and/or a DCC/DCA-style criterion) with thresholds fixed now, and commit to
   reporting the |P| distribution per detector and condition.
4. **Resolve, or record explicitly as UNRESOLVED, the two fitting-data lookups**
   before any performance claim: 1LXL / 2YXJ / Q07817 against the CryptoBench
   fold map Lacuna ships, and 1LXL / 2YXJ against P2Rank's CHEN11 and JOINED
   training lists.
5. **Commit the Steps 1–5 tree to git**, so the protocol hash is anchored in a
   dated commit rather than only in files inside the directory it describes.
6. **Add one independent validation of the 24-residue reference set** via a
   different code path or an external interaction listing, rather than relying on
   a test that compares the implementation to its own saved output.

## Recommended, not blocking

- 4.5 Å reference-set sensitivity analysis, computable now from archived
  distances with no detector output (5.0 Å → 24 residues; 4.5 Å → 22).
- Specificity/decoy control and total emitted-pocket counts.
- Chain B of 2YXJ as a free secondary reference replicate.
- State the ~3.3 Å offset between the reference protein centroid and the ligand
  centroid.
- Consider an X-ray apo (for example 1MAZ, suitability unverified) as a
  preregistered alternative, chosen on construct and method grounds only.
