# Final Historical Status

## Historically demonstrated
- Generated 6 RFdiffusion primary design backbones
- Generated 10 ProteinMPNN sequence designs from 5 target templates
- Forward-folded 10 structures using ESMFold

## Deterministically reverified now
- Boltz-2 structural output was a mocked fallback (deterministic hash check confirms distinct from 3nft_original.pdb; fallback provenance confirmed via pipeline failure logs and code)
- The FASTA sequences explicitly contain temperature and sampling metadata indicating ProteinMPNN generation.

## Historical but not independently reproduced
- The actual RFdiffusion, ProteinMPNN, and ESMFold computations were not rerun locally. Their historical execution is established via format/metadata integrity and repository chronology.

## Simulated/fallback
- Boltz-2 outputs
- PeSTo confidence metrics

## Unresolved
- The 0.688 Å RMSD claim: Could not be unambiguously identified or reproduced via deterministic global alignment.
