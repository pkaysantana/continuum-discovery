# Independent Oncology Benchmark: Selection Correction 2

## Correction of the Factual Record
The previous selection of EGFR (`5EDP` / `5D41`) contained significant factual errors regarding construct parity and mutation backgrounds, which are corrected here:
- **5EDP (Apo)**: This structure is genuinely ligand-free, but its deposited mutations include L858R, T790M, and additionally E865A, E866A, and K867A (surface entropy reduction mutations).
- **5D41 (Holo)**: This structure contains T790M and V948R. It explicitly **lacks** the L858R mutation deposited in the sequence. Furthermore, `5D41` contains the ATP-site ligand ANP (AMP-PNP) and the allosteric ligand `57N` (EAI001, not EAI045). Additionally, `V948R` is an inactive-state stabilizing/dimerization-deficient mutation that actively restricts conformational sampling, rather than just a solubility substitution.

*Correction*: The previous claims of "exceptional mutation/construct parity" and that `5D41` was L858R/T790M/V948R containing EAI045 were objectively false.

**Eligibility Decision for EGFR**: `REJECTED_MUTATION_CONSTRUCT_CONFOUNDING`. The severe mismatch in biologically relevant mutations (presence/absence of L858R and the E865A/E866A/K867A cluster) and the presence of `V948R` fundamentally confound attribution of pocket opening to apo→holo conformational dynamics.

## Candidate Discovery Resumption
To find a genuinely cleaner candidate, 6 additional independent oncology systems were thoroughly screened.

### 1. CDK2
- **Apo**: `1HCL` (Genuinely ligand-free, WT)
- **Holo**: `3PY1` (Bound to ANS and SU9516)
- **Confounders**: `3PY1` contains SU9516 in the ATP-binding hinge region. ATP-competitive inhibitors in kinases are mechanically known to drive massive structural remodeling (e.g., activation loop and alpha-C helix shifts), confounding the attribution of the allosteric pocket solely to ANS.
- **Overlap**: No exact PDB ID overlap identified.
- **Decision**: `REJECTED_MUTATION_CONSTRUCT_CONFOUNDING`

### 2. PTP1B (PTPN1)
- **Apo Candidates**: `1A5Y`, `2HNQ`
- **Holo Candidates**: `1T49`, `1T4J` (Allosteric inhibitor BB3/892)
- **Confounders/Parity**: `1A5Y` is in the Lacuna cryptic benchmark dataset. `2HNQ` contains a tungstate ion (`WO4`) in the active site, which acts as a transition state analogue (phosphate mimic), meaning it is not a truly unliganded/apo structure. `1T49` has a construct length of 298 vs `2HNQ` at 321 (missing 23 residues).
- **Overlap**: `1A5Y` is `BENCHMARK_OVERLAP` (Lacuna). `2HNQ`/`1T49` is `UNKNOWN`.
- **Decision**: `REJECTED (Overlap / Confounders)`

### 3. KRAS G12C
- **Apo Candidates**: `6OIM`, `4LUC`
- **Holo Candidates**: `6OQA` (Wait, 6OQA is CEP250, 6UT0 is Adagrasib KRAS G12C).
- **Confounders**: `6OIM` was investigated as apo but is actually covalently bound to AMG 510. `4LUC` is bound to a small molecule disulfide. Genuinely apo KRAS G12C structures without GDP/GTP or covalent ligands are exceedingly rare. `4OBE` (another apo candidate) is in the Lacuna training/benchmark set.
- **Overlap**: `4OBE` is `BENCHMARK_OVERLAP`. 
- **Decision**: `REJECTED (No Valid Apo)`

### 4. MEK1 
- **Apo Candidates**: `1S9J`
- **Holo Candidates**: `1S9I`
- **Confounders**: Neither structure is apo. Both are complexed with MgATP and allosteric inhibitors (BBM in `1S9J`, 5EA in `1S9I`).
- **Overlap**: `UNKNOWN`
- **Decision**: `REJECTED (No Valid Apo)`

### 5. PIK3CA (PI3K alpha)
- **Apo Candidates**: `4JPS`
- **Holo Candidates**: `4TV3`
- **Confounders**: `4JPS` is not apo; it contains the ligand `1LT`.
- **Overlap**: `UNKNOWN`
- **Decision**: `REJECTED (No Valid Apo)`

### 6. IDH1 R132H
- **Apo Candidates**: `3INM`, `4KZO`
- **Confounders**: All identified IDH1 mutant baseline structures contain NADP+ and/or alpha-ketoglutarate in the active site, confounding the "unoccupied" requirement for the reference state.
- **Overlap**: `UNKNOWN`
- **Decision**: `REJECTED (No Valid Apo)`

## Final Decision
**Selected Candidate**: NO VALID CANDIDATE YET.

**Reasoning**: After exhaustive screening across major oncology targets (EGFR, CDK2, PTP1B, KRAS, MEK1, PI3K, IDH1), no single pair perfectly satisfies the frozen eligibility criteria. Kinases and GTPases are almost universally crystallized with their orthosteric ligands (ATP/ADP/GTP/GDP analogues) or engineered with crystallization-enabling mutations (e.g., surface entropy reduction or dimerization mutants). Those rare pairs that do exist (e.g., specific PTP1B or Abl kinase structures) suffer from explicit presence in the Lacuna benchmark or P2Rank datasets. Rather than forcing a compromised selection that violates the strict independence, mutation parity, and confounder-free requirements, the process is halted here without an eligible candidate.

*Explicit Statement:* Neither the Lacuna nor the P2Rank detector has been run on any candidate. The selection was aborted based solely on structural-quality metadata and overlap auditing. No final structures have been downloaded or processed.
