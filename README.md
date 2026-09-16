# Continuum Discovery: EP4 Structural-Pocket Reconstruction

*Note: The original hackathon-phase "Edge-to-Cloud Biodefense Swarm" code and documentation have been deprecated in this branch in favor of this strict scientific reconstruction.*

## Project Overview

This branch represents the **EP4 Structural-Pocket Reconstruction Project**. Its goal was to forensically audit, reconstruct, and execute the preregistered structural bioinformatics benchmarks originally scoped for the Continuum Discovery project, with a strict focus on cryptic pocket detection.

The project was executed in four distinct phases:

### Phase 1: Forensic Audit & Initialization
- **Action**: Investigated the historical `ep4-original` run.
- **Findings**: Established that the original Boltz and PeSTo generative biology components were simulated via fallback logic rather than active model executions. 
- **Outcome**: A historical evidence ledger was created, and the initial EP4 state was frozen to ensure scientific integrity moving forward.

### Phase 2: BCL-XL Analysis A (Pipeline Validation)
- **Action**: Verified the preregistered Lacuna cryptic pocket benchmark on BCL-XL.
- **Findings**: Resolved critical execution environment issues (e.g., locating missing `fused_ranker.npz` and package inconsistencies). Corrected interpretation of evaluation metrics by distinguishing the predefined primary centroid-based hits from secondary Jaccard hits.
- **Outcome**: The Lacuna pipeline was validated, and erroneous claims regarding NMA determinism and stochastic variance were scientifically reconciled.

### Phase 3: BCL-XL Analysis B (Static vs Ensemble-Based Detection)
- **Action**: Conducted a head-to-head evaluation of static pocket detection (P2Rank) versus ensemble-based detection (Lacuna) on identical matched-core BCL-XL inputs.
- **Findings**: Documented near-identical centroid differences (e.g., ~0.01 Å difference).
- **Outcome**: The results were rigorously reported without subjective inflation or scientifically ungrounded phrasing, completing the predefined Analysis B protocol.

### Phase 4: Independent Oncology Benchmark Selection
- **Action**: Initiated candidate discovery for an independent oncology target to serve as a structurally isolated benchmark (Analysis C).
- **Findings**: Screened multiple high-value targets including EGFR, CDK2, KRAS, PTP1B, PI3K, MEK1, and IDH1. The screening revealed widespread confounding issues such as:
  - Reliance on ATP-competitive inhibitors driving structural changes.
  - Irreconcilable mutation and construct mismatches between apo/holo pairs (e.g., EGFR L858R vs V948R).
  - Explicit overlap with Lacuna or P2Rank training/evaluation datasets.
- **Outcome**: Rejected all candidates based on the frozen structural-quality criteria. The selection phase was officially closed with the status **NO VALID CANDIDATE YET**, refusing to compromise the benchmark's independence.

## Current Status

The structural-pocket project is currently **paused/closed**. 

- **BCL-XL Analysis A**: Complete
- **BCL-XL Analysis B**: Complete
- **Independent Benchmark Selection**: Closed (no eligible candidate found)
