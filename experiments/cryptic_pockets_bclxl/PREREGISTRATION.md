# BCL-XL preregistration

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
