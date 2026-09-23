# NULL relation range check

Date: 2026-09-18. Evidence resolution only.

OBSERVED: Recomputed directly from the four existing ChEMBL 37 activity JSON pages under `../data/raw/chembl/`, with SHA-256 and byte sizes verified against the frozen source manifest. Selection requires both `relation` and `standard_relation` to be JSON NULL. Values are compared using exact Decimal arithmetic; no rounding, binning or data transformation was applied.

## NULL-relation ranges

OBSERVED: All counts below refer to stored `standard_value`, not an inferred true clearance. HLM standard units are `mL.min-1.g-1`; both hepatocyte assays use `uL.min-1.(10^6cells)-1`.

| Assay | N | Minimum | Maximum | <3 | =3 | Strictly >3 and <150 | =150 | >150 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CHEMBL3301370 | 744 | 3.0 | 146.0 | 0 | 13 | 731 | 0 | 0 |
| CHEMBL3301371 | 595 | 3.0 | 149.0 | 0 | 2 | 593 | 0 | 0 |
| CHEMBL3301372 | 289 | 3.2 | 134.9 | 0 | 0 | 289 | 0 | 0 |

OBSERVED: **No NULL-relation records occur outside [3,150] in any of the three assays**, so there are no out-of-range activity IDs, molecule IDs or values to enumerate. **There are no NULL-at-150 records in any assay.**

## Exact frequencies from 3 through 10 inclusive

OBSERVED: Each assay column pair is independently sorted by numeric value; adjacent assay entries do not denote matched records. Only observed unique values are listed, with their exact row counts. A dash marks the end of a list, not a missing source value. No bins are used.

| Assay | Rows in [3,10] | Distinct numeric values |
| --- | --- | --- |
| CHEMBL3301370 | 224 | 60 |
| CHEMBL3301371 | 126 | 55 |
| CHEMBL3301372 | 112 | 65 |

| HLM 3301370 value | Count | Rat 3301371 value | Count | Human 3301372 value | Count |
| --- | --- | --- | --- | --- | --- |
| 3.0 | 13 | 3.0 | 2 | 3.2 | 1 |
| 3.02 | 1 | 3.09 | 1 | 3.24 | 1 |
| 3.31 | 1 | 3.16 | 1 | 3.3 | 1 |
| 3.6 | 1 | 3.24 | 1 | 3.31 | 3 |
| 3.9 | 1 | 3.31 | 1 | 3.39 | 1 |
| 3.98 | 2 | 3.39 | 3 | 3.4 | 1 |
| 4.0 | 22 | 3.63 | 1 | 3.46 | 1 |
| 4.07 | 1 | 3.8 | 1 | 3.47 | 2 |
| 4.17 | 3 | 3.87 | 1 | 3.55 | 1 |
| 4.2 | 1 | 4.0 | 7 | 3.72 | 3 |
| 4.47 | 1 | 4.17 | 2 | 3.8 | 1 |
| 4.57 | 1 | 4.24 | 1 | 3.81 | 1 |
| 4.7 | 1 | 4.37 | 1 | 3.89 | 1 |
| 4.79 | 1 | 4.68 | 1 | 3.91 | 1 |
| 4.9 | 1 | 4.79 | 3 | 3.98 | 3 |
| 5.0 | 22 | 5.0 | 7 | 4.04 | 1 |
| 5.13 | 2 | 5.01 | 2 | 4.17 | 1 |
| 5.25 | 3 | 5.13 | 4 | 4.27 | 2 |
| 5.37 | 2 | 5.25 | 2 | 4.46 | 1 |
| 5.5 | 5 | 5.29 | 1 | 4.47 | 2 |
| 5.6 | 1 | 5.37 | 1 | 4.57 | 3 |
| 5.75 | 3 | 5.5 | 2 | 4.68 | 2 |
| 6.0 | 23 | 5.75 | 1 | 4.7 | 1 |
| 6.03 | 1 | 5.79 | 1 | 4.76 | 1 |
| 6.17 | 2 | 6.0 | 8 | 4.79 | 3 |
| 6.18 | 1 | 6.17 | 3 | 4.88 | 1 |
| 6.31 | 4 | 6.31 | 3 | 4.9 | 2 |
| 6.33 | 1 | 6.61 | 2 | 4.92 | 1 |
| 6.46 | 1 | 6.76 | 2 | 5.01 | 1 |
| 6.5 | 1 | 6.92 | 2 | 5.05 | 1 |
| 6.61 | 1 | 7.0 | 6 | 5.13 | 1 |
| 6.67 | 1 | 7.08 | 1 | 5.16 | 1 |
| 6.76 | 1 | 7.11 | 1 | 5.17 | 1 |
| 6.92 | 3 | 7.2 | 1 | 5.25 | 3 |
| 7.0 | 19 | 7.24 | 1 | 5.37 | 2 |
| 7.08 | 1 | 7.33 | 1 | 5.5 | 1 |
| 7.24 | 1 | 7.48 | 1 | 5.62 | 2 |
| 7.41 | 3 | 7.59 | 1 | 5.75 | 3 |
| 7.5 | 3 | 7.94 | 2 | 5.88 | 1 |
| 7.59 | 2 | 8.0 | 9 | 6.0 | 3 |
| 7.76 | 2 | 8.13 | 2 | 6.17 | 2 |
| 7.94 | 2 | 8.51 | 2 | 6.31 | 3 |
| 8.0 | 13 | 8.71 | 2 | 6.46 | 2 |
| 8.13 | 1 | 8.91 | 1 | 6.61 | 2 |
| 8.28 | 1 | 9.0 | 5 | 6.76 | 2 |
| 8.32 | 2 | 9.01 | 1 | 6.92 | 2 |
| 8.33 | 1 | 9.12 | 2 | 6.99 | 1 |
| 8.5 | 3 | 9.33 | 1 | 7.0 | 1 |
| 8.51 | 1 | 9.55 | 2 | 7.08 | 2 |
| 8.67 | 1 | 9.77 | 4 | 7.24 | 1 |
| 8.71 | 2 | 9.8 | 1 | 7.41 | 2 |
| 8.86 | 1 | 9.88 | 1 | 7.59 | 3 |
| 8.91 | 2 | 9.9 | 1 | 7.76 | 3 |
| 9.0 | 16 | 9.95 | 1 | 7.9 | 1 |
| 9.12 | 2 | 10.0 | 8 | 7.94 | 2 |
| 9.33 | 1 | - | - | 8.13 | 1 |
| 9.5 | 1 | - | - | 8.51 | 3 |
| 9.55 | 1 | - | - | 8.7 | 1 |
| 9.77 | 3 | - | - | 8.71 | 2 |
| 10.0 | 10 | - | - | 8.91 | 1 |
| - | - | - | - | 9.12 | 4 |
| - | - | - | - | 9.33 | 2 |
| - | - | - | - | 9.5 | 1 |
| - | - | - | - | 9.77 | 2 |
| - | - | - | - | 10.0 | 3 |

## Primary human HLM: CHEMBL3301370

| Record class | Count |
| --- | --- |
| Both relations NULL; strictly inside (3,150) | 731 |
| Both relations NULL; exactly 3 | 13 |
| Both relations explicitly <; standard_value 3 | 274 |
| Both relations explicitly >; standard_value 150 | 84 |

OBSERVED: These four classes sum to all 1,102 HLM activity records. The explicitly qualified records represent `<3` and `>150`; they are separate from NULL-relation rows.

UNRESOLVED: These ranges and frequency distributions do not establish clipping, reporting-limit treatment or uncensored semantics. NULL is not reinterpreted as equals. The existing audit conclusions, including `REMAINS_AMBIGUOUS`, are unchanged. No raw data, preprocessing outputs, splits or models were modified.
