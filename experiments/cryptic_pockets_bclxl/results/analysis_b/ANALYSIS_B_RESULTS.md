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

### 3.1 Apo Structure (Cryptic State)
| Metric | P2Rank | Lacuna |
| :--- | :--- | :--- |
| **First Primary Hit (Centroid $\le 4.0$ Å)** | None | None |
| **First Upstream Hit (Rank)** | 1 | 1 |
| **Best Centroid Distance** | $4.97$ Å | $4.96$ Å |
| **Best Jaccard Index** | $0.36$ | $0.43$ |
| **Candidate Count** | $4$ | $10$ |

### 3.2 Holo Structure (Control)
| Metric | P2Rank | Lacuna |
| :--- | :--- | :--- |
| **First Primary Hit (Centroid $\le 4.0$ Å)** | None | None |
| **First Upstream Hit (Rank)** | 1 | 1 |
| **Best Centroid Distance** | $6.85$ Å | $4.48$ Å |
| **Best Jaccard Index** | $0.50$ | $0.56$ |
| **Candidate Count** | $3$ | $10$ |

## 4. Benchmark-Bounded Conclusions
1.  **Primary Endpoint Failure:** Neither P2Rank nor Lacuna recovered the BCL-XL cryptic pocket on the matched-core structures under the strict primary preregistered endpoint (centroid distance $\le 4.0$ Å), for either the apo or holo control conditions.
2.  **Upstream Metric Recovery:** Under the more permissive secondary upstream metrics (Jaccard $\ge 0.25$), both P2Rank and Lacuna successfully recovered the pocket at Rank 1 in both the apo and holo control structures.
3.  **Methodological Performance:** Within the boundaries of this benchmark, Lacuna yielded moderately tighter centroid distances ($4.96$ Å vs $4.97$ Å in apo, $4.48$ Å vs $6.85$ Å in holo) and higher Jaccard overlaps ($0.43$ vs $0.36$ in apo, $0.56$ vs $0.50$ in holo) than P2Rank, though these improvements did not bridge the gap required to satisfy the primary endpoint.
4.  **Ensemble vs Static Detection:** The ensemble-based NMA approach of Lacuna did not lead to a binary difference in the preregistered primary recovery status compared to the static detection of P2Rank on the apo state of BCL-XL.

## 5. File Manifest
*   `candidate_metrics.csv`: Raw metrics for all candidates within the top-K budget.
*   `summary.json`: Aggregated endpoints and metadata for all execution runs.
