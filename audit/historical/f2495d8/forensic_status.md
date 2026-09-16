# Final Forensic Status Report

**Snapshot SHA:** `f2495d813100f8f4860bb54e63b85da798220e32`
**Worktree Status:** Clean (Verified during manifest generation)
**Manifest File Count:** 1,239 tracked files
**Audit Timestamp:** 2026-09-16 (Current Session)

## Summary of Findings

A comprehensive forensic audit of the historical snapshot `f2495d8` reveals significant discrepancies between the claims made in the project's commit history and the actual computational evidence present in the codebase. While some intermediate artefacts (PDB structures and FASTA sequences) do exist, the orchestration and generative pipelines heavily rely on simulated metrics, fallback heuristics, and mocked tools rather than genuine API calls or local executions.

### Tools Identified in History
The following scientific models were referenced in the codebase and commit logs:
- **RFdiffusion** (Backbone generation)
- **ProteinMPNN** (Sequence design)
- **ESMFold** (3D Structure prediction)
- **Boltz-2** (Complex structure validation)
- **PeSTo** (Binding interface analysis)

### Evidence Chains & Lineage
An evidence chain was successfully traced for the target **BipD (B. pseudomallei translocator protein)**:
1. **Target Identification:** PDB `3NFT`.
2. **RFdiffusion:** 5 test backbones were committed in SHA `002eb66`.
3. **ProteinMPNN:** 10 binder sequences (2 per backbone) were committed in SHA `4f9c4ce`.
4. **ESMFold:** 10 forward-folded 3D structures were committed in SHA `2534ec9`.

The explicit artefact lineage has been documented in `artifact_lineage.csv` and `artifact_lineage.json`.

### Verification vs. Simulation (The "Mock" Problem)
Despite the presence of the files above, the actual Python orchestration scripts (`agents/aminoanalytica_pipeline.py`, `agents/bio_scientist_agent.py`, etc.) heavily utilized hardcoded mock responses and fallback simulations.

**Findings from Codebase Grep:**
- The `AminoAnalytica` generative pipeline uses a `_safe_amina_cli_call` function that defaults to returning `fallback_metrics` (e.g., hardcoded sequence confidence, hardcoded `iptm_score: 0.860`) whenever the CLI fails or times out.
- The `BioScientistAgent` contains a direct `_fallback_simulation()` method used to bypass the pipeline entirely, returning simulated workshop metrics.
- The `Animoca` blockchain agent explicitly uses simulated wallets (`simulated_private_key`, `simulate_balance_update`) and fakes blockchain transaction intents.
- `ESMFold` and `Boltz` validations frequently log failures and immediately pivot to local mock geometric filters.

**Conclusion on Claims:**
The project's claims of "successful autonomous compute loops" and "world-first biodefense platforms" cannot be verified as legitimate autonomous AI capabilities. The agents were configured to fail gracefully into hardcoded, simulated pathways that output pre-determined, successful-looking metrics. The metrics are untrustworthy.

## Audit Outputs Generated
All outputs have been safely written to the reconstruction repository without modifying the original historical snapshot.

- **Provenance Manifest (JSON):** `audit/historical/f2495d8/provenance_manifest.json`
- **Provenance Manifest (CSV):** `audit/historical/f2495d8/provenance_manifest.csv`
- **Audit Summary:** `audit/historical/f2495d8/audit_summary.md`
- **Historical Chronology:** `audit/historical/f2495d8/chronology.md`
- **Artefact Lineage (CSV):** `audit/historical/f2495d8/artifact_lineage.csv`
- **Artefact Lineage (JSON):** `audit/historical/f2495d8/artifact_lineage.json`
- **Evidence Classification:** `audit/historical/f2495d8/evidence_classification.md`
- **Final Forensic Status:** `audit/historical/f2495d8/forensic_status.md`

## Tests Run
1. `scripts/test_build_provenance_manifest.py`: Ran 11 tests to verify Git command error handling, repository clean/dirty logic, LFS pointer detection, and metadata extraction. **Result: 11/11 Passed.**
2. `scripts/generate_audit_summary.py`: Parsed the JSON manifest to aggregate statistics safely. **Result: Passed.**
3. `analyze_history2.py`: Parsed historical Git logs to construct chronology and trace artefact lineage. **Result: Passed.**

## Unresolved Claims
- **"Fully Decentralized Dynamic Biotech Economy"**: No real blockchain interactions exist; entirely simulated.
- **"Pan-bacterial validation achieved"**: Only the BipD target has any structural files, and the agent pipelines use fallback mocks. No evidence of pan-bacterial validation.
- **"Automatic archival system for high-quality protein designs"**: This system just moves mock files into an archive folder.

The historical snapshot is a meticulously constructed simulation rather than a fully functional, autonomous AI discovery pipeline.
