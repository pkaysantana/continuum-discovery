# Continuum Discovery: EP4 Reconstruction & Cryptic Pocket Benchmark

This repository contains the reconstructed "EP4" structural biology pipeline, with a rigorous, preregistered benchmark of cryptic pocket detection methods (Lacuna vs. P2Rank). 

The repository has transitioned from its initial hackathon prototype ("Edge-to-Cloud Biodefense Swarm") to a strictly controlled scientific environment emphasising reproducible structural bioinformatics, forensic auditing, and robust benchmarking.

## Project Status
See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the latest high-level status.
- **BCL-XL Analysis A**: Complete
- **BCL-XL Analysis B**: Complete
- **Independent Benchmark Selection**: Completed with no eligible candidate
- **Structural-Pocket Project**: Paused/closed for the current application cycle.

## 1. EP4 Historical Forensic Audit
An exhaustive forensic audit was conducted on the original EP4 generative pipeline. 
Key findings:
- The historical pipeline contained a fallback mechanism where purported Boltz-2 structural outputs were actually byte-identical mock copies of the input scaffold.
- The original prose summaries contradicted the exact byte-level execution ledger.
- Invariant tests and a `build_provenance_manifest.py` script were implemented to mathematically ensure contradictory states and undocumented fallbacks cannot occur in future executions.

## 2. BCL-XL Cryptic Pocket Benchmark
We conducted a preregistered computational pocket benchmark using BCL-XL to compare static detection (P2Rank) against ensemble-based detection (Lacuna). No molecular or protein generation (e.g., Boltz, RFdiffusion, ESMFold) was used in this phase.
- **Analysis A (Reconciliation)**: Validated the Lacuna BCL-XL pipeline. Verified the determinism of the Lacuna Normal Mode Analysis (NMA) backend and corrected the interpretation of the primary vs. secondary hit thresholds.
- **Analysis B (Comparison)**: Executed a strict static vs. ensemble comparison on identical, matched-core BCL-XL apo inputs.

## 3. Independent Oncology Benchmark (Candidate Discovery)
A rigorous screening phase was initiated to find an independent oncology target with a genuinely unliganded (apo) structure and a paired holo structure to serve as a blind test set.
- Exhaustive screening was performed across high-value targets including EGFR, CDK2, PTP1B, KRAS G12C, MEK1, PI3K alpha, and IDH1.
- **Outcome**: The selection was halted with `NO_VALID_CANDIDATE_YET`. All candidates failed the strict eligibility criteria due to either dataset overlap (inclusion in P2Rank/Lacuna training datasets) or the presence of confounding active-site ligands (e.g., ATP-analogues, tungstate) that violated the strict "genuinely apo" requirement.
- See [SELECTION_OUTCOME.md](experiments/independent_oncology_benchmark/SELECTION_OUTCOME.md) for the full target-by-target breakdown and rationale.

## Repository Structure
- `experiments/cryptic_pockets_bclxl/`: The preregistered BCL-XL benchmark suite, environment locks, and results.
- `experiments/independent_oncology_benchmark/`: Candidate screening scripts, structural metadata checks, and outcome reports.
- `audit/`: Historical audit records, forensic status reports, and legacy data.
- `scripts/`: Provenance tracking, manifest building, and deterministic hashing utilities.
- `tests/`: Automated invariants to protect the audit ledger.

---
*Note: The original hackathon-phase "Edge-to-Cloud Biodefense Swarm" code and documentation have been deprecated in favor of this strict scientific reconstruction.*
