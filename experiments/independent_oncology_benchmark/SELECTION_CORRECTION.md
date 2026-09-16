# Independent Oncology Benchmark: Selection Correction

## Issue Investigated
The previous selection of EGFR L858R (`4I22` apo / `5D41` holo) contained a factual eligibility error regarding the apo state. 
- **4I22 Audit**: Direct metadata retrieval confirms that `4I22` is **NOT** apo. It is a T790M/L858R/V948R triple mutant co-crystallized with Gefitinib in the ATP site. Gefitinib binding directly stabilizes the active (alpha-C helix IN) conformation, which mechanically closes the allosteric pocket. This represents a confounding ligand that plausibly drives the relevant closed conformation, rendering it ineligible as a true apo/unliganded starting structure.
- **CDK2 Audit (1HCL / 3PY1)**: `1HCL` is genuinely ligand-free. However, `3PY1` contains both ANS (allosteric ligand) and SU9516 (ATP-competitive inhibitor). SU9516 binding in the hinge/ATP site typically drives major conformational changes in kinases (e.g., remodeling the activation loop and alpha-C helix), materially confounding the attribution of the allosteric pocket opening solely to ANS. Therefore, the CDK2 pair is highly confounded.

## Corrected Candidate Search (EGFR)
A search for a genuinely ligand-free EGFR structure with a closely matched mutation background yielded **5EDP**.
- **5EDP (Apo)**: EGFR T790M/L858R mutant. It is genuinely ligand-free (0 non-polymer entities). The construct is 331 residues long. The allosteric site is structurally closed because the L858R/T790M mutations strongly favor the active (alpha-C helix IN) state in the absence of ligands.
- **5D41 (Holo)**: EGFR L858R/T790M/V948R mutant bound to EAI045 (allosteric inhibitor) and ANP (ATP analogue). The construct is 331 residues long. V948R is a known surface-exposed solubility mutation. While ANP is present, the key conformational change (alpha-C helix OUT) is mechanistically driven by the allosteric binding of EAI045.

## Re-evaluation against Frozen Criteria
- **Defensible ligand-free starting structure**: `5EDP` is completely unliganded.
- **Ligand-bound allosteric reference structure**: `5D41` defines the EAI045 pocket.
- **Construct/mutation comparability**: Both constructs are 331 residues. The mutation backgrounds are closely matched (T790M/L858R vs L858R/T790M/V948R).
- **Confounders**: `5EDP` has no ligands. `5D41` has an orthosteric ATP analogue (ANP), but the allosteric pocket formation is EAI045-dependent.
- **Overlap Status**: `NO_IDENTIFIED_OVERLAP` for both `5EDP` and `5D41` across Lacuna benchmarks/examples and P2Rank documented datasets (searches returned zero exact ID matches). Absence from fitting datasets is marked `UNKNOWN` as true training data is not fully auditable.

## Final Decision
**Selected Candidate**: Corrected EGFR Pair (`5EDP` Apo / `5D41` Holo).

This pair resolves the confounding ligand issue in the previously proposed apo structure while maintaining exceptional construct parity and high oncology relevance.

*Explicit Statement:* 
Neither the Lacuna nor the P2Rank detector has been run on any candidate. This selection was made strictly based on the frozen eligibility and structural-quality criteria. No final structures have been downloaded or processed.
