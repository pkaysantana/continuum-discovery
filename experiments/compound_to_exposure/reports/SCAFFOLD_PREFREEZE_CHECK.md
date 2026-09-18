# Scaffold pre-freeze characterisation

OBSERVED, 2026-09-18. RDKit 2025.03.6; SAP SHA-256 `6a29097ace7b01f89dbe00eedfb7781c4dd515113f98e433fd19d5328d5cfaa9`. Immutable CHEMBL3301370 raw pages pass manifest hash/size and pagination checks. The primary cohort consists of 731 records with both relation fields NULL and 3 < standard_value < 150. Both relation fields agree throughout. This is an evidence-only dry-run; no modelling partition or fitted representation was created.

## Exact grouping and cohort statistics

Atomic `MurckoScaffoldSmiles(mol=m, includeChirality=False)`; no generic-scaffold conversion. Multicomponent grouping chooses the fragment with most heavy atoms, then the lexicographically smallest canonical SMILES on a tie. Canonical SMILES uses RDKit's default isomeric form. Empty Murcko strings map to `__ACYCLIC__`. Identity and raw structures are unchanged. One HLM record is multicomponent: activity 14759791, CHEMBL1355736 (deposited hydrate); fragment selection is for its scaffold key only.

| Statistic | All 1,102 | Primary 731 |
|---|---:|---:|
| Unique scaffold groups | 712 | 532 |
| Singleton groups | 583 | 457 |
| Fraction of groups that are singletons | 0.8188202247191011 | 0.8590225563909775 |
| Compounds in singleton groups | 583 | 457 |
| __ACYCLIC__ compounds | 1 | 1 |
| Fraction of compounds in __ACYCLIC__ | 0.0009074410163339383 | 0.0013679890560875513 |

Singleton fractions are 81.8820% of all groups and 85.9023% of primary groups. Cohort-specific singleton counts count only members of that cohort; a primary singleton may have non-primary companions in the full 1,102. Both assays have unique structures per row, so row and compound counts coincide here.

OBSERVED: `__ACYCLIC__` contains only CHEMBL203125, activity 14758924, an interior record. It is 0.136799% of the primary cohort, **does not exceed 20%**, and is **not excluded by the oversized-group rule**. Its actual hash position places it in CV fold 3. No scaffold exceeds the holdout budget: the largest primary group has 14 members; the largest full-data group has 32. No material oversized-group or acyclic-pooling problem is observed.

## Deterministic assignment dry-run

Groups are sorted by the integer value of the first eight SHA-256 hex digits of UTF-8 scaffold key, then lexicographic key. Whole groups, including groups with zero primary members, enter the holdout until its primary count first reaches at least 731/5 = 146.2. This requires at least 147, not 146, primary records. Whole-group accumulation yields **149 / 731 = 20.3830369357%**. The rule skips groups exceeding the full budget, not groups merely exceeding the remaining budget. CV groups follow the same hash order and are assigned to the fold with fewest primary members, ties to lowest index (0–4).

| Quantity | Result |
|---|---:|
| Primary holdout N | 149 |
| Primary holdout scaffold groups | 84 |
| All-record holdout N | 250 |
| All-record holdout scaffold groups | 116 |
| Primary CV-pool N | 582 |
| All-record CV-pool N | 852 |
| Groups crossing holdout/CV or inner folds | 0 |

| CV fold | Primary N | All-record N |
|---:|---:|---:|
| 0 | 115 | 172 |
| 1 | 120 | 170 |
| 2 | 115 | 162 |
| 3 | 117 | 184 |
| 4 | 115 | 164 |

OBSERVED: all five procedural assignment steps are reproduced, with no target-magnitude balancing, tuning, fitting or second selected partition. The SAP's phrase 'group larger than the holdout budget' does not specify whether group size means primary or all records. The diagnostic checked both interpretations; they give identical assignments because neither basis has an oversized group. This ambiguity has no effect on these HLM records. The assignment depends on outcome-defined cohort membership, as the SAP explicitly acknowledges; it is not a structure-only algorithm in the strict sense.

INFERRED limitation: abundant singleton scaffold keys do not establish that held-out compounds are chemically distant from training compounds. Scaffold disjointness is verified; fingerprint dissimilarity is not. The requested scope excludes representation generation, so the SAP's additional pre-freeze nearest-training ECFP4/Tanimoto characterisation was not performed. Accepting the limitation and closing that unperformed requirement need an explicit protocol decision, not a changed split. The numerical RDKit version is recorded here but has not been inserted into the unchanged SAP.

## Largest 20 scaffold groups: All 1,102 records

| Rank | Atomic scaffold key | N |
|---:|---|---:|
| 1 | `c1ccc(-c2ccccc2)cc1` | 32 |
| 2 | `c1ccc(CCN2CCC(CN3CCC(Oc4ccccc4)CC3)CC2)cc1` | 23 |
| 3 | `O=C(Cc1ccccc1)NC1CCN(CCC(c2ccccc2)c2ccccc2)CC1` | 20 |
| 4 | `c1ccc(Sc2c[nH]c3ccccc23)cc1` | 20 |
| 5 | `c1ccccc1` | 18 |
| 6 | `O=C(NS(=O)(=O)c1ccccc1)N1CCC(N2CCC(Oc3ccccc3)CC2)CC1` | 17 |
| 7 | `O=C(NCCCN1CCC(Oc2ccccc2)CC1)c1c[nH]c(=O)c2ccccc12` | 15 |
| 8 | `O=S(=O)(Nc1ccnn1-c1ccccc1)c1ccccc1` | 13 |
| 9 | `c1ccc2c(-c3c[nH]c4ccccc34)ccnc2c1` | 12 |
| 10 | `O=S(=O)(c1ccccc1)N1CCN(Cc2ccccc2)CC1` | 10 |
| 11 | `O=C(Cc1ccccc1)N1CCN(Cc2ccccc2)CC1` | 9 |
| 12 | `O=S(=O)(Nc1ccn[nH]1)c1ccccc1` | 8 |
| 13 | `c1ccc(-c2cccs2)cc1` | 8 |
| 14 | `c1ccc(OC2CCN(CC3CCN(c4ccccc4)CC3)CC2)cc1` | 8 |
| 15 | `c1ccc(COc2ccccc2)cc1` | 7 |
| 16 | `c1ccc(CSc2ncc3scnc3n2)cc1` | 7 |
| 17 | `O=C(CCOCCc1ccccc1)NCCNCCc1cccc2[nH]c(=O)sc12` | 6 |
| 18 | `O=C(NC1CCCCC1)c1cnn(-c2ccccc2)c1NS(=O)(=O)c1ccccc1` | 6 |
| 19 | `O=c1[nH]c2cccc(CCNCCSCCCNCCc3ccccc3)c2s1` | 6 |
| 20 | `O=C(Cc1ccccc1)NC1CCN(CCC(c2ccccc2)C2CCNCC2)CC1` | 5 |

## Largest 20 scaffold groups: Primary 731 records

| Rank | Atomic scaffold key | N |
|---:|---|---:|
| 1 | `O=C(Cc1ccccc1)NC1CCN(CCC(c2ccccc2)c2ccccc2)CC1` | 14 |
| 2 | `O=S(=O)(Nc1ccnn1-c1ccccc1)c1ccccc1` | 13 |
| 3 | `O=C(NCCCN1CCC(Oc2ccccc2)CC1)c1c[nH]c(=O)c2ccccc12` | 12 |
| 4 | `c1ccc(-c2ccccc2)cc1` | 12 |
| 5 | `c1ccccc1` | 10 |
| 6 | `O=C(NS(=O)(=O)c1ccccc1)N1CCC(N2CCC(Oc3ccccc3)CC2)CC1` | 8 |
| 7 | `O=S(=O)(Nc1ccn[nH]1)c1ccccc1` | 8 |
| 8 | `O=S(=O)(c1ccccc1)N1CCN(Cc2ccccc2)CC1` | 8 |
| 9 | `c1ccc2c(-c3c[nH]c4ccccc34)ccnc2c1` | 7 |
| 10 | `O=C(NC1CCCCC1)c1cnn(-c2ccccc2)c1NS(=O)(=O)c1ccccc1` | 6 |
| 11 | `O=c1[nH]c2cccc(CCNCCSCCCNCCc3ccccc3)c2s1` | 6 |
| 12 | `c1ccc(-c2cccs2)cc1` | 6 |
| 13 | `c1ccc(CCN2CCC(CN3CCC(Oc4ccccc4)CC3)CC2)cc1` | 6 |
| 14 | `O=c1[nH]c2cccc(CCNCCc3cccc(CNCc4ccccc4)c3)c2s1` | 5 |
| 15 | `c1ccc(CSc2ncc3scnc3n2)cc1` | 5 |
| 16 | `c1ccc(Sc2c[nH]c3ccccc23)cc1` | 5 |
| 17 | `O=C(CCOCCc1ccccc1)NCCNCCc1cccc2[nH]c(=O)sc12` | 4 |
| 18 | `O=C(Cc1ccccc1)NC1CCN(CCC(c2ccccc2)C2CCNCC2)CC1` | 4 |
| 19 | `O=C(NCC12CC3CC(CC(C3)C1)C2)c1ccccc1` | 4 |
| 20 | `O=C(c1cc2ccccc2[nH]1)N1CCNCC1` | 4 |

All ties in the largest-20 lists are ordered lexicographically by scaffold key. Complete evidence: [JSON](SCAFFOLD_PREFREEZE_CHECK.json), [712 group statistics and hash-order assignments](SCAFFOLD_PREFREEZE_GROUPS.csv), [1,102 per-record dry-run assignments](SCAFFOLD_PREFREEZE_DRY_RUN_ASSIGNMENTS.csv). These report artifacts are not `splits/master_partition.csv` and do not authorize fitting. Reproduce with `src/prefreeze_evidence.py`.

PRE_FREEZE_DECISION_REQUIRED
