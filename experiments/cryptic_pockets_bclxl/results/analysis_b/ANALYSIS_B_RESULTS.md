# Analysis B: Static vs Ensemble-based Pocket Detection on BCL-XL

## 1. Overview
This report documents **Analysis B** of the preregistered BCL-XL cryptic-pocket benchmark. It compares a static pocket detector (P2Rank) with an ensemble-based detector (Lacuna) using identical, matched-core structures for both the apo and holo states of BCL-XL.

**Primary Endpoint:** Centroid distance $\le 4.0$ Å.
**Upstream Secondary Endpoint:** Jaccard index $\ge 0.25$ OR Centroid distance $\le 4.0$ Å.

## 2. Experimental Setup
*   **P2Rank Configuration:** Default parameters (version 2.5.1), `seed 42`.
*   **Lacuna Configuration:** `nma` backend, 20 conformers, `alpha` detector, `learned` ranker, `seed 42`, no sequence seeding.
*   **Inputs:** Byte-identical matched-core PDB structures (apo: `apo_matched_core.pdb`, holo: `holo_matched_core_no_ligand.pdb`).

## 3. Results Summary

### 3.1 Four-Run Execution Results
| Condition | Method | Candidates | Primary Hit Rank | Upstream Hit Rank | Best Centroid (Å) | Best Jaccard | Hit Recall | Hit Precision | Runtime (s) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Apo | P2Rank | 4 | None | 1 | 4.97 | 0.36 | 0.375 | 0.900 | ~10.9 | SUCCESS |
| Apo | Lacuna | 10 | None | 1 | 4.96 | 0.43 | 0.542 | 0.591 | ~5.6 | SUCCESS |
| Holo Control | P2Rank | 3 | None | 1 | 6.85 | 0.50 | 0.500 | 1.000 | ~8.6 | SUCCESS |
| Holo Control | Lacuna | 10 | None | 1 | 4.48 | 0.56 | 0.583 | 0.933 | ~4.8 | SUCCESS |

*(Note: "Hit Recall" and "Hit Precision" represent the metrics associated with the first upstream secondary hit at Rank 1. Best Centroid and Best Jaccard are the optimal values found within the top-K budget.)*

## 4. Benchmark-Bounded Conclusions

1.  **Primary Endpoint Failure:** Neither P2Rank nor Lacuna recovered the BCL-XL cryptic pocket on the matched-core structures under the strict primary preregistered endpoint (centroid distance $\le 4.0$ Å), for either the apo or the holo control conditions.
2.  **Positive-Control Conclusion:** In the matched-core ligand-removed holo positive-control analysis, both methods successfully identified the pocket region using the secondary upstream endpoint (Jaccard $\ge 0.25$ at Rank 1). However, neither method satisfied the strict primary centroid $\le 4.0$ Å distance metric (best centroid was 6.85 Å for P2Rank and 4.48 Å for Lacuna).
3.  **Upstream Metric Recovery:** Under the more permissive secondary upstream metrics (Jaccard $\ge 0.25$), both P2Rank and Lacuna successfully recovered the pocket at Rank 1 in both the apo and holo control structures.
4.  **Methodological Performance (Apo):** Within the boundaries of this benchmark, the centroid distance difference between Lacuna (4.96 Å) and P2Rank (4.97 Å) on the apo structure is ~0.01 Å and should be treated as essentially indistinguishable for interpretation. Lacuna did yield a higher residue-set overlap (Jaccard of 0.43 vs 0.36) on this single BCL-XL case.
5.  **Sensitivity Conclusion:** The 4.5 Å sensitivity analysis did not change the qualitative primary conclusion. There were exactly zero primary hits (0) across all methods and conditions under the 4.5 Å reference definition, identical to the 5.0 Å primary definition.
6.  **Ensemble vs Static Detection:** The ensemble-based NMA approach of Lacuna did not lead to a binary difference in the preregistered primary recovery status compared to the static detection of P2Rank on the apo state of BCL-XL.

## 5. File Manifest
*   `candidate_metrics.csv`: Raw metrics for all candidates within the top-K budget.
*   `summary.json`: Aggregated endpoints and metadata for all execution runs.
