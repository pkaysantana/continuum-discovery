# Reconciliation of Forensic Audit

This document reconciles the earlier forensic findings (from `forensic_status.md`) with the deterministic verification of artefacts. 

## Was the earlier statement that the project was primarily a demonstration too broad?
Yes. The previous conclusion categorized the entire pipeline as a "meticulously constructed demonstration" and downplayed the extent of actual scientific computing. While the orchestration layer contains significant fallback logic, the verification phase proves that heavy compute tools were genuinely executed. 

## Which parts were demonstrably genuine computation?
Deterministic verification confirms the presence and execution lineage of:
- **RFdiffusion**: 24 distinct artefacts (designed backbones and trajectories) were genuinely generated.
- **ProteinMPNN**: 5 FASTA files containing designed sequences with embedded generation metadata (temperature, sequence recovery).
- **ESMFold (Structure Prediction)**: 10 valid `.pdb` structures were folded from the designed sequences.
These artefacts represent genuine, successful execution of state-of-the-art structural biology models. 

## Which parts of the autonomous/integrated pipeline used fallback behaviour?
The validation and assessment stages relied heavily on fallback behaviour:
- **Boltz-2 Execution**: The generated output (`boltz2_bipd_boltz2_pred_structure.pdb`) was proven to be a fallback simulation (distinct hash from input scaffold, but execution failed and pipeline defaulted to mock fallback metrics). The model was not run.
- **PeSTo / Confidence Metrics**: Metrics such as `ipTM`, `PAE`, and "100% success" claims were generated via simulation loops (e.g., `_fallback_simulation`) rather than true external model inference.
- **Pipeline Orchestration**: The overarching `AminoAnalyticaPipeline` gracefully substituted simulated data whenever heavy compute resources were unavailable or prone to failure, giving the illusion of a flawless autonomous loop.

## Which previous conclusions remain valid?
- The claims of "fully autonomous end-to-end pan-bacterial validation" remain invalid. The validation phase was heavily mocked.
- The evidence confirms that when the pipeline attempted complex binding validations (Boltz-2) or widespread assessment, it fell back to generating hardcoded or simulated JSON/CSV metrics.

## Which previous conclusions need narrowing or correction?
- **Correction**: The initial audit implied the whole project was a simulated interface. We must narrow this: the *generation* phase (RFdiffusion -> ProteinMPNN -> ESMFold) was demonstrably genuine and produced real scientific data. Only the *validation* and *blockchain-integration* phases were simulated.
- **Correction**: Artefacts such as the 10 ESMFold binders and the 5 RFdiffusion backbones should be treated as genuine scientific outputs of their respective tools, not mocked files.
