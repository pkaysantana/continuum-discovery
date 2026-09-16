# Independent Oncology Benchmark: Selection Outcome

## Prospectively Defined Purpose
The purpose of the independent oncology benchmark was to conduct "Analysis C" for the cryptic-pocket project. This required identifying a novel oncology-relevant therapeutic target with a defensible, unliganded apo structure and a matching ligand-bound holo structure displaying a meaningful cryptic or allosteric pocket. The goal was to provide a completely independent evaluation system, strictly isolated from any training or evaluation data used by the Lacuna or P2Rank pocket detectors.

## Frozen Eligibility Criteria
A candidate system was required to have:
- An oncology-relevant therapeutic target.
- A genuinely defensible ligand-free/unliganded apo structure.
- A ligand-bound holo reference structure showing a meaningful pocket opening.
- Objective ligand-defined reference-site construction.
- Sufficiently comparable constructs, sequence identity, and mutation background between apo and holo pairs to support attribution of pocket recovery to conformational opening.
- No second/confounding ligand (e.g., ATP-site binders) whose binding plausibly drives the relevant conformational change.
- No known example, benchmark, or training overlap with Lacuna or P2Rank datasets (with `UNKNOWN` applied when complete training provenance is unavailable).
- No candidate selection based on expected detector performance.

## Candidates Screened
A wide range of high-value oncology targets were screened across multiple rounds of review:
- EGFR (Various mutants)
- CDK2
- PTP1B (PTPN1)
- KRAS (G12C)
- MEK1
- PIK3CA (PI3K alpha)
- IDH1 (R132H)
- SHP2
- MDM2
- Abl Kinase
- Menin
- AKT1

## Major Rejection Reasons
Candidates were broadly rejected due to three overriding factors:
1. **Overlap and Independence Violations**: High-quality benchmark pairs (like PTP1B `1A5Y`, SHP2 `2SHP`/`5EHR`, Abl Kinase, MDM2) frequently suffered from explicit inclusion in Lacuna's benchmark datasets or P2Rank's evaluation datasets (e.g., `holo4k` or `coach420`).
2. **Confounding Ligands (Not Genuinely Apo)**: Kinases and GTPases (e.g., MEK1, CDK2, PI3K, KRAS, IDH1) are almost universally crystallized with their orthosteric ligands (ATP/ADP/GTP/GDP analogues) or other small molecules. This breaks the requirement for a genuinely ligand-free baseline or introduces secondary ligands that structurally drive the pocket conformation, confounding attribution.
3. **Mutation and Construct Mismatches**: Candidates featuring allosteric inhibitors often utilize carefully engineered or heavily mutated constructs to stabilize specific states or aid crystallization, preventing exact sequence/construct parity between apo and holo pairs.

## Resolution of EGFR Selection Errors
During the screening process, EGFR L858R was initially selected but subsequently rejected after rigorous factual correction:
- **Error 1**: `4I22` was mistakenly classified as apo. Metadata verification confirmed it is a triple mutant co-crystallized with Gefitinib, an ATP-site inhibitor that physically drives the active (alpha-C helix IN) state, closing the allosteric pocket. 
- **Error 2**: A revised pair (`5EDP` / `5D41`) suffered from severe mutation confounding. The `5EDP` apo construct lacked the `V948R` inactive-state stabilizing mutation and contained `E865A/E866A/K867A`, while `5D41` (bound to an ATP analogue and EAI001) notably lacked the primary `L858R` deposited mutation.
- **Resolution**: Both errors were caught and corrected *before* any detector execution occurred. The selection record was amended strictly on the basis of frozen structural-quality criteria, preserving the flawed initial reports as an audit trail.

## Final Status
**NO_VALID_CANDIDATE_YET**

No screened candidate satisfied all prespecified structural-comparability, independence and confounder-control criteria.

## Conclusion and Future Outlook
No benchmark target was forced into selection because relaxing the criteria would compromise the scientific validity and strict independence required for this phase of the study. 

Explicitly, **no candidate detector performance was inspected or calculated prior to or during candidate selection.**

To reopen the search in the future, explicit evidence of a new, high-resolution oncology target pair must be provided. This pair must definitively establish a completely ligand-free apo state, an allosteric/cryptic holo state free from structural confounders, exact sequence/mutation parity, and guaranteed absence from Lacuna and P2Rank datasets.
