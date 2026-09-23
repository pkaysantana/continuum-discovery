# HLM-HH qualifier cross-tabulation

OBSERVED: 187 compounds shared by CHEMBL3301370 (human HLM) and CHEMBL3301372 (human hepatocyte), using the frozen audit at `4640ea7`. Qualifiers and values were read from the immutable ChEMBL 37 raw pages; SHA-256 and sizes match the source manifest. Existing canonical keys and pair membership were verified against the frozen commit. No new structural calculation was performed.

## Status definitions

| Status | Operational rule |
| --- | --- |
| INTERIOR_OBSERVED | Both raw and standard relation NULL; 3 < standard_value < 150 |
| BOUNDARY_AMBIGUOUS | Both raw and standard relation NULL; standard_value equals 3 or 150 |
| LEFT_CENSORED | Both relations <; standard_value equals 3 |
| RIGHT_CENSORED | Both relations >; standard_value equals 150 |

UNRESOLVED: `INTERIOR_OBSERVED` is the requested operational status name. It does not assert that NULL means equals or resolve uncensored semantics. Existing scientific audit conclusions are unchanged. Raw and standardised qualifiers and numeric values agree for every paired record.

## Full 4 x 4 matrix

OBSERVED: Rows are HLM status; columns are HH status. Every zero cell is retained.

| HLM / HH | INTERIOR_OBSERVED | BOUNDARY_AMBIGUOUS | LEFT_CENSORED | RIGHT_CENSORED |
| --- | --- | --- | --- | --- |
| INTERIOR_OBSERVED | 94 | 0 | 26 | 5 |
| BOUNDARY_AMBIGUOUS | 2 | 0 | 0 | 0 |
| LEFT_CENSORED | 20 | 0 | 31 | 0 |
| RIGHT_CENSORED | 8 | 0 | 0 | 1 |

| Pair class | N |
| --- | --- |
| Both INTERIOR_OBSERVED | 94 |
| One INTERIOR_OBSERVED and the other LEFT/RIGHT_CENSORED | 59 |
| Both LEFT/RIGHT_CENSORED | 32 |
| At least one BOUNDARY_AMBIGUOUS | 2 |
| Total | 187 |

OBSERVED: Of the 59 mixed interior/censored pairs, 31 have interior HLM and censored HH (26 left, 5 right), and 28 have censored HLM and interior HH (20 left, 8 right). Of the 32 both-censored pairs, 31 are left/left and 1 is right/right; none is left/right or right/left.

## Every boundary-ambiguous paired case

| Molecule ID | HLM activity ID | HLM value | HLM raw / standard relation | HH activity ID | HH value | HH raw / standard relation | HH status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CHEMBL271012 | 14769803 | 3.0 | NULL / NULL | 14763401 | 30.12 | NULL / NULL | INTERIOR_OBSERVED |
| CHEMBL552512 | 14769805 | 3.0 | NULL / NULL | 14758940 | 3.4 | NULL / NULL | INTERIOR_OBSERVED |

OBSERVED: Both ambiguous HLM records are exactly 3; there are no ambiguous HH records and no NULL-at-150 paired records. Native units are microL/min/mg for HLM and microL/min/1E6 cells for HH. Values are listed separately without subtracting, dividing or physiologically scaling them.

## Identity and quantitative eligibility

OBSERVED: The raw molecule-ID intersection and frozen strict canonical-structure intersection both contain exactly **187** members and identify the same compound pairs. Each assay contributes exactly one activity per matched ID and per matched structure. All 187 pairs match the frozen `PAIRED_HUMAN_COHORT.csv`; there are no extra, duplicate or ambiguous mappings.

OBSERVED: **94 pairs** have both assays strictly interior with NULL qualifiers. This is the eligible N for the proposed ordinary quantitative correlation under the requested interior-only policy; no correlation was calculated. Including the two HLM NULL-at-3 cases as exact 3 in the separately specified sensitivity would give 96 pairs, but they remain boundary-ambiguous in this cross-tab.

Machine-readable evidence: [HLM_HH_QUALIFIER_CROSSTAB.json](HLM_HH_QUALIFIER_CROSSTAB.json), including all 187 paired records, source locations, native units, the complete matrix and both boundary-ambiguous cases.
