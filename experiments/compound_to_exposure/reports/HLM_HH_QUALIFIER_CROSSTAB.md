# HLM–HH qualifier cross-tabulation: final verification

OBSERVED, 2026-09-18. Independently regenerated from the immutable downloaded ChEMBL 37 activity pages for CHEMBL3301370 (HLM) and CHEMBL3301372 (human hepatocyte; HH). Pagination totals/unique activity IDs, raw SHA-256 and byte sizes pass validation. Both relation fields and both numerical value fields agree for every record in these assays; NULL remains NULL.

Classification uses exact decimal comparisons: INTERIOR_OBSERVED requires both relations NULL and 3 < standard_value < 150; BOUNDARY_AMBIGUOUS requires both NULL and standard_value exactly 3 or 150; LEFT_CENSORED requires both relations `<` and reported bound 3; RIGHT_CENSORED requires both `>` and reported bound 150. The latter two labels describe qualifiers, not exact continuous observations. No other status occurs.

| HLM \ HH | INTERIOR_OBSERVED | BOUNDARY_AMBIGUOUS | LEFT_CENSORED | RIGHT_CENSORED | Total |
|---|---:|---:|---:|---:|---:|
| INTERIOR_OBSERVED | 94 | 0 | 26 | 5 | 125 |
| BOUNDARY_AMBIGUOUS | 2 | 0 | 0 | 0 | 2 |
| LEFT_CENSORED | 20 | 0 | 31 | 0 | 51 |
| RIGHT_CENSORED | 8 | 0 | 0 | 1 | 9 |
| Total | 124 | 0 | 57 | 6 | 187 |

OBSERVED: the provisional 94 / 59 / 32 / 2 summary is confirmed. Of the 59 interior/censored pairs, 31 have interior HLM (26 HH-left, 5 HH-right), and 28 have interior HH (20 HLM-left, 8 HLM-right). The 32 doubly censored pairs comprise 31 left/left and one right/right; opposite-tail cells are zero.

## Every boundary-ambiguous pair

| Molecule | HLM activity | HLM value | HH activity | HH value |
|---|---:|---:|---:|---:|
| CHEMBL271012 | 14769803 | 3.0 | 14763401 | 30.12 |
| CHEMBL552512 | 14769805 | 3.0 | 14758940 | 3.4 |

All four records above have raw and standard relation NULL. Both HLM records are BOUNDARY_AMBIGUOUS at 3; both HH records are INTERIOR_OBSERVED. Values retain their native scales: HLM raw units microL/min/mg (standard units mL.min-1.g-1), HH raw units microL/min/1E6 cells (standard units uL.min-1.(10^6cells)-1). No conversion, difference or ratio was calculated. There are no paired NULL-at-150 records and no NULL-at-150 records in either full assay. The HH assay has no NULL-at-3 records either.

OBSERVED: **94 pairs** qualify for the primary ordinary quantitative Spearman calculation. **96 pairs** qualify only under the specified sensitivity that includes the two HLM NULL-at-3 values as exact 3. They remain boundary-ambiguous in the evidence table; sensitivity eligibility does not establish equality semantics. No correlation was computed.

OBSERVED: full-molecule canonicalization with RDKit 2025.03.6 produces no duplicate molecule IDs or canonical structures within either assay. The molecule-ID intersection and strict canonical-structure intersection each contain the **same 187 one-to-one activity pairs**, exactly matching the frozen PAIRED_HUMAN_COHORT.csv. No salt, tautomer, stereochemistry or fragment normalization was used for this identity comparison.

Machine-readable evidence: [4×4 matrix CSV](HLM_HH_QUALIFIER_CROSSTAB.csv), [JSON with all 187 pairs, activity IDs, source pages/row locators, fields and input hashes](HLM_HH_QUALIFIER_CROSSTAB.json). Reproduction: `src/prefreeze_evidence.py`. SAP snapshot SHA-256: `6a29097ace7b01f89dbe00eedfb7781c4dd515113f98e433fd19d5328d5cfaa9`. Raw files, frozen membership and SAP were not changed. These findings preserve the existing scientific audit conclusions.
