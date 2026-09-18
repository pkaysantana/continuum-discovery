# ECFP4/Tanimoto pre-freeze split characterisation

Completed 2026-09-18T11:44:10.482590+00:00. This is a structural similarity calculation, not model performance. The existing candidate partition and SAP are unchanged. No numerical target values, raw activity records, model predictions, residuals or v1 performance files were opened.

## Input and method

The sole molecular-data input is `SCAFFOLD_PREFREEZE_DRY_RUN_ASSIGNMENTS.csv`. It contains identities, canonical SMILES, frozen scaffold keys, previously assigned cohort statuses and candidate partition/fold membership, but no numerical target fields. The saved INTERIOR_OBSERVED membership selects 731 compounds without re-deriving the cohort or partition.

RDKit **2025.03.6**; NumPy **2.2.6**. Fingerprints use the SAP's `GetMorganFingerprintAsBitVect`: Morgan/ECFP4, **radius 2, 2048 bits, binary, useChirality=False**. Other legacy defaults are preserved explicitly: `useBondTypes=True`, `useFeatures=False`, `includeRedundantEnvironments=False`; default atom invariants, all atoms, no atom filtering. Fingerprints are computed on the supplied complete canonical structures without new standardisation, fragment selection or chirality-aware encoding. Frozen scaffold keys are consumed as saved, not regenerated.

For each of the **149 primary holdout compounds**, the reference pool is all **582 primary CV compounds**. For each CV observation, the reference pool contains only primary CV observations in the other four frozen folds; the holdout and its own fold are excluded. Every candidate-pair RDKit similarity was independently checked by intersection/union of the on-bit sets, including maximum values and all nearest-neighbour ties.

Quartiles use NumPy `quantile(method="linear")`: linear interpolation at sorted index (N−1)p for p=0.25,0.5,0.75. Fractions use each section's query N. Bins have inclusive lower/exclusive upper edges, except the final upper edge 1.0 is inclusive. Summaries below are descriptive, not decision thresholds.

## Holdout nearest-CV distribution

| Statistic | Value |
|---|---:|
| N | 149 |
| Minimum | 0.17346938775510204 |
| Q1 | 0.32051282051282054 |
| Median | 0.52 |
| Q3 | 0.6896551724137931 |
| Maximum | 1.0 |
| Mean | 0.5228198769703273 |
| Maximum similarity exactly 1.0: query count | 2 |

| Preregistered bin | Count | Fraction |
|---|---:|---:|
| [0,0.2) | 1 | 0.006711409395973154 |
| [0.2,0.3) | 28 | 0.18791946308724833 |
| [0.3,0.4) | 24 | 0.1610738255033557 |
| [0.4,0.6) | 37 | 0.2483221476510067 |
| [0.6,1.0] | 59 | 0.3959731543624161 |

Bins with fewer than 20 observations remain descriptive counts under the SAP's existing rule. No residual, accuracy comparison or inference is performed.

## Exact-1.0 pairs

Holdout: **2 queries**, **2 query/reference pairs** at exactly 1.0. CV: **0 queries** at exactly 1.0 against an eligible other-fold reference. CV pairs are directed because each CV observation is a query.

| Scope | Query molecule / activity | Query frozen scaffold | Reference molecule / activity | Reference frozen scaffold |
|---|---|---|---|---|
| holdout_to_cv | CHEMBL1807827 / 14760031 | `O=c1[nH]c2cccc(CCNCCSCCCNCCc3ccccc3)c2s1` | CHEMBL1807869 / 14762426 | `O=c1[nH]c2cccc(CCNCCCSCCNCCc3ccccc3)c2s1` |
| holdout_to_cv | CHEMBL1807829 / 14761251 | `O=c1[nH]c2cccc(CCNCCSCCCNCCc3ccccc3)c2s1` | CHEMBL1807871 / 14763472 | `O=c1[nH]c2cccc(CCNCCCSCCNCCc3ccccc3)c2s1` |

An exact 1.0 here means identical finite binary fingerprints. It does not imply identical molecular structures or frozen Murcko scaffolds. All listed pairs have distinct frozen scaffold keys.

## CV nearest-other-fold executability check

| Query fold | Query N | Eligible reference N per query | Queries with a defined maximum |
|---:|---:|---:|---:|
| 0 | 115 | 467 | 115 |
| 1 | 120 | 462 | 120 |
| 2 | 115 | 467 | 115 |
| 3 | 117 | 465 | 117 |
| 4 | 115 | 467 | 115 |

All **582** CV observations have a finite maximum using only the other four CV folds. There is no self-match, same-fold reference or holdout reference. Aggregate CV minimum/Q1/median/Q3/maximum/mean are **0.1111111111111111 / 0.28169014084507044 / 0.4306623931623932 / 0.6578046142754146 / 0.9814814814814815 / 0.47390398442410037**.

| Preregistered bin | CV count | CV fraction |
|---|---:|---:|
| [0,0.2) | 11 | 0.018900343642611683 |
| [0.2,0.3) | 165 | 0.28350515463917525 |
| [0.3,0.4) | 92 | 0.15807560137457044 |
| [0.4,0.6) | 123 | 0.211340206185567 |
| [0.6,1.0] | 191 | 0.3281786941580756 |

## Scaffold separation and SAP consistency

**No holdout/CV pair shares a frozen Bemis–Murcko scaffold.** The primary holdout and CV scaffold-key sets have an empty intersection, and every scored pair has different keys. No frozen scaffold crosses CV folds either. All 1,102 saved assignments also retain one partition/fold per scaffold group. Primary membership remains 149 holdout and 582 CV, with CV fold Ns 115/120/115/117/115.

**Factual contradiction with the SAP's split/fingerprint specification: none detected.** Scaffold-key separation does not promise uniformly low fingerprint similarity; the distribution is reported without changing the partition, introducing a cutoff or choosing methods. The requested nearest-training calculation is executable for all 731 primary observations with the frozen reference-pool rules.

The two holdout queries with exact-1.0 matches are indistinguishable from their respective CV neighbours in this frozen binary fingerprint, despite distinct molecular structures and scaffold keys. Thus this check does not support a stronger claim that every holdout observation is novel in the fingerprint representation. Identical bits alone do not distinguish finite-radius representation equivalence from bit-folding collisions; no alternative fingerprint was computed to investigate that mechanism. This is a structural-separation limitation, not a changed partition or a performance result.

The SAP's statement that this characterisation has not yet been performed is now superseded by this completion evidence. The SAP itself remains unchanged, including its pending status. This report does not freeze the protocol, create a tag or authorize model execution.

## Reproduction and artifacts

- Assignment CSV SHA-256: `96bf97e5500b108c40883c13e3fc4b87c49b49c61b22357ec89cbfcec41d7a2e`.
- SAP snapshot SHA-256: `5564fd304cbacb7324fddd678306feb16de67187963b85aebe0df6675c34814e`.
- Audit script SHA-256: `a159b2c6ee22e84397b18b57a496c376d1fa32aed0ae564d65bbb8f5138e3fd4`.
- Input hashes before/after: identical. No partition, SAP or raw file was written.
- [Machine-readable JSON](ECFP4_TANIMOTO_PREFREEZE_CHECK.json): both distributions, all 731 per-query results, all nearest-neighbour ties, exact-1.0 pair identities/scaffolds, fold reference counts and verification flags.
- [Per-query CSV](ECFP4_TANIMOTO_PREFREEZE_CHECK.csv): 149 holdout rows plus 582 CV rows, distinguished by `scope`; array-valued nearest-neighbour fields use JSON encoding.
- Reproduce with `.venv/Scripts/python.exe src/tanimoto_prefreeze.py` from the experiment directory. This script reads only the saved structural assignment CSV and the SAP text; it does not import the raw-data audit or modelling runners. It hashes the saved group CSV without parsing its contents.

TANIMOTO_PREFREEZE_CHECK_COMPLETE
