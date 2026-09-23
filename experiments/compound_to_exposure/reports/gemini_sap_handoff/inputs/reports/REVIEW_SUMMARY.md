# Audit review summary

## Source counts

| Source | OBSERVED rows | OBSERVED unique IDs / strict structures |
|---|---:|---:|
| CHEMBL3301370 human HLM | 1,102 | 1,102 / 1,102 |
| CHEMBL3301371 rat hepatocyte | 837 | 837 / 837 |
| CHEMBL3301372 human hepatocyte | 408 | 408 / 408 |
| TDC Clearance_Microsome_AZ | 1,102 | 1,102 / 1,102 |
| TDC Clearance_Hepatocyte_AZ | 1,213 | 1,020 / 1,020 |
| Biogen ADME_public_set_3521.csv | 3,521 | 3,521 / 3,521 |

EXPECTED_FROM_MEMO: The task supplied ChEMBL expectations of 1,102 / 837 / 408; these match ChEMBL 37 observations. The frozen memo itself contains no numeric expectations.

OBSERVED: ChEMBL completeness is verified against the downloaded **ChEMBL 37 API state**, not a historical release. Stored pagination metadata, acquired row counts and unique activity IDs must agree for each assay. This does not establish completeness against the historical ChEMBL release used to construct TDC.

## Relations and boundaries

| Assay | OBSERVED `<` | OBSERVED `>` | OBSERVED explicit `=` | OBSERVED null/UNKNOWN |
|---|---:|---:|---:|---:|
| CHEMBL3301370 | 274 | 84 | 0 | 744 |
| CHEMBL3301371 | 115 | 127 | 0 | 595 |
| CHEMBL3301372 | 104 | 15 | 0 | 289 |

OBSERVED: All `<` boundaries are 3; all `>` boundaries are 150. Original and standard relation counts agree. Null is not recoded to equals. Units and every reported value by relation are preserved in DATA_AUDIT.json.

| Assay | OBSERVED null relation at 3 | OBSERVED null relation at 150 |
|---|---:|---:|
| CHEMBL3301370 | 13 | 0 |
| CHEMBL3301371 | 2 | 0 |
| CHEMBL3301372 | 0 | 0 |

OBSERVED: The two rat-assay records are activity 14768823 (CHEMBL589973) and activity 14768825 (CHEMBL364714), each with standard value 3.0 and null relation. Both remain UNKNOWN.

OBSERVED: TDC microsome has 287 values exactly 3 and 84 exactly 150; TDC hepatocyte has 195 exactly 3 and 137 exactly 150. Neither has inequality strings or missing targets. The 287 microsome values at 3 include 274 matches to `<3` records; the remaining 13 match records with null relations. A numeric boundary alone does not define censor status.

## Species claim

INFERRED: **REPRODUCED locally** from explicit rat-only and human-only structure/value matches; historical data lineage remains an inference.

OBSERVED: TDC hepatocyte strict structure classes, as **rows / distinct valid structures**, are rat only **609 / 609**, human only **183 / 183**, both **405 / 218**, neither **16 / 10**, ambiguous/unparseable **0 / 0**. All 193 duplicated structure groups have different labels. Of these, 187 pairs each contain exactly two TDC rows: one uniquely matches a rat source record and the other uniquely matches a human source record by strict structure and exact numeric value, with no opposite-species value match. Six groups have no strict structural match to either source assay under the frozen identity rule (all twelve rows are neither): CHEMBL115, CHEMBL173706, CHEMBL1513, CHEMBL1483, CHEMBL190 and CHEMBL82663. Secondary exact-ID evidence supports 190 such pairs, leaving three unresolved; it does not change the strict structural counts. Thirty-one individual rows have a value compatible with both species.

UNRESOLVED: Ten TDC structures (16 rows) have no strict current ChEMBL hepatocyte match. Eight rows remain unmatched even by exact molecule ID plus numeric value. Shared-structure/shared-label provenance cannot identify species uniquely. Rat assay strain metadata is inconsistent-looking; organism, taxonomy and description explicitly say rat, but the strain annotation requires source review.

## Microsome reconciliation

OBSERVED: **1,097 strict structure matches**, all with exactly equal numeric values; five unmatched structures on each side and no duplicates. Exact-ID overlap is **1,101**, with exact numeric agreement for all 1,101 IDs.

| TDC molecule ID | ChEMBL molecule ID | Discrepancy | Matching value | Standard InChIKeys |
|---|---|---|---:|---|
| CHEMBL82663 | CHEMBL82663 | Hydroxythiazole / thiazolone tautomer spellings | 111.0 | Equal |
| CHEMBL1483 | CHEMBL1483 | Heterocyclic N-H tautomer spellings | 34.67 | Equal |
| CHEMBL412142 | CHEMBL412142 | Imidazole N-H tautomer spellings | 96.0 | Equal |
| CHEMBL1513 | CHEMBL1513 | Tetrazole N-H tautomer spellings | 17.78 | Equal |
| CHEMBL190 | CHEMBL1355736 (declared parent CHEMBL190) | Theophylline / hydrate with disconnected `O` | 4.79 | Different |

OBSERVED: The four tautomer spellings have matching molecule IDs, values and standard InChIKeys, as independently confirmed in [AUDIT_REVIEW.md](AUDIT_REVIEW.md). The hydrate pair also has a matching value. Standard InChIKeys are supporting evidence only; all five remain mismatches under the frozen canonical-SMILES rule. Full strings, source activities and secondary ID evidence appear in the reconciliation CSV/JSON. This evidence does not establish when or why source representations changed. No tautomer or fragment transformation was applied.

OBSERVED: All 274 `<3` and 84 `>150` ChEMBL microsome records have strict TDC structure/value matches with numeric 3 or 150 and no inequality. All 1,102 ChEMBL original and standard numeric values agree.

INFERRED: ChEMBL's standard mL/min/g and original microL/min/mg are numerically equivalent units. No physiological scaling was performed.

UNRESOLVED: The raw TDC tables contain no unit/censor columns. Matched numbers support consistency with source units but cannot independently prove unit provenance or historical preprocessing. The datasets are not strictly identical despite equal row counts.

## Human paired cohort

OBSERVED: **187 shared molecule IDs and 187 shared strict canonical structures**, with no disagreement or duplicate-activity ambiguity between these identity definitions. Only cohort membership was established.

## Biogen and chemical anomalies

OBSERVED: Exact non-null HLM N is **3,087** in `LOG HLM_CLint (mL/min/kg)`; **434** values are missing. The supplied HLM target minimum is **0.675686709**, present **958** times; the maximum is **3.372714293**, median **1.205312653**. These are source-provided log labels; no new transformation was applied. No numerical comparison to AstraZeneca labels was performed.

INFERRED: The minimum pile-up is consistent with a reporting boundary; it does not alone prove censoring. Log base, source scaling derivation and per-row censor status remain UNRESOLVED from the downloaded CSV/README.

OBSERVED: All six sources have zero missing/invalid SMILES under the pinned parser. Only TDC hepatocyte has duplicate canonical structures. Biogen has **223** molecules with reproducibly detected unspecified potential stereochemistry and **4** multicomponent structures. Undefined stereo and fragment flags for every row, and descriptor ranges/quantiles/IQR/MAD for all six datasets, are retained in the full audit.

## Execution and review boundary

OBSERVED: The acquisition manifest initially failed on a metadata type check after all downloads succeeded; the actual FAILED traceback is retained. Raw inputs were unchanged during the fix. Initial derived reports were archived explicitly before the ID-evidence follow-up. Final unit-test receipts and integrity verification are under reports/ and manifests/.

OBSERVED: No modelling, model preprocessing, synthetic scientific results, HLM/HH arithmetic or physiological scaling was performed. The frozen memo and unrelated projects remain unchanged. This is the audit checkpoint for independent review.
