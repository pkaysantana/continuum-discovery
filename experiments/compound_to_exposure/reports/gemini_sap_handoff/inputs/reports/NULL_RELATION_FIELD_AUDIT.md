# NULL relation field audit

**INFERRED verdict: REMAINS_AMBIGUOUS**, specifically for CHEMBL3301370, CHEMBL3301371 and CHEMBL3301372.

## Scope and retained fields

OBSERVED: Primary evidence is the immutable downloaded ChEMBL 37 activity pages at `4640ea721204771979e5637e81217f59c65318e6`. All 18 acquired raw files passed the frozen manifest hash/size checks before and after this audit; receipts and manifest match that commit. The four activity pages contain 2,347 records. Completeness concerns this downloaded API state, not a historical ChEMBL release.

OBSERVED: Every requested activity field is retained in every record. The companion [JSON](NULL_RELATION_FIELD_AUDIT.json) extracts every record with its exact strings/nulls, source filename and 1-based position within the page. It includes all source/document IDs supplied by the API: document_chembl_id, src_id, record_id and toid, plus assay-level aidx/src_assay_id. No requested activity field was silently substituted or fetched.

OBSERVED: All activities identify document CHEMBL3301361 and src_id 27. document_journal, document_year and toid are NULL. The separate document record, original depositor activity table, compound-record source IDs and document DOI/PubMed identifiers were not acquired; their absence limits historical interpretation.

Method: standard-library JSON/Decimal field inspection only. No audit.py/chemistry imports, descriptors, preprocessing, splits or modelling. NULL is an explicit category, distinct from an absent field, empty string and `=`. Numeric equality is exact Decimal equality; source value strings are preserved.

## Raw relation versus standard_relation

OBSERVED: Rows are raw `relation`; columns are `standard_relation`. Zero cells are shown, including `=`. No other relation category occurs.

### CHEMBL3301370

| raw / standard | < | > | = | NULL |
| --- | --- | --- | --- | --- |
| < | 274 | 0 | 0 | 0 |
| > | 0 | 84 | 0 | 0 |
| = | 0 | 0 | 0 | 0 |
| NULL | 0 | 0 | 0 | 744 |

### CHEMBL3301371

| raw / standard | < | > | = | NULL |
| --- | --- | --- | --- | --- |
| < | 115 | 0 | 0 | 0 |
| > | 0 | 127 | 0 | 0 |
| = | 0 | 0 | 0 | 0 |
| NULL | 0 | 0 | 0 | 595 |

### CHEMBL3301372

| raw / standard | < | > | = | NULL |
| --- | --- | --- | --- | --- |
| < | 104 | 0 | 0 | 0 |
| > | 0 | 15 | 0 | 0 |
| = | 0 | 0 | 0 | 0 |
| NULL | 0 | 0 | 0 | 289 |

OBSERVED: All NULL standard_relation rows also have NULL relation. Raw `=` to standard NULL: **0**. Raw NULL to standard `=`: **0**. Explicit `<` and `>` agree in all records. There are no raw or standard explicit equals records in any assay.

## standard_flag

OBSERVED: Counts below use standard_relation classes; the raw-relation counts are identical.

| Assay | Relation | flag 1 | flag 0 | flag NULL / other |
| --- | --- | --- | --- | --- |
| CHEMBL3301370 | < | 274 | 0 | 0 |
| CHEMBL3301370 | > | 84 | 0 | 0 |
| CHEMBL3301370 | NULL | 744 | 0 | 0 |
| CHEMBL3301371 | < | 115 | 0 | 0 |
| CHEMBL3301371 | > | 127 | 0 | 0 |
| CHEMBL3301371 | NULL | 595 | 0 | 0 |
| CHEMBL3301372 | < | 104 | 0 | 0 |
| CHEMBL3301372 | > | 15 | 0 | 0 |
| CHEMBL3301372 | NULL | 289 | 0 | 0 |

DOCUMENTED: In the [ChEMBL 37 schema](https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/schema_documentation.txt), standard_flag distinguishes curated/set standard columns (1) from columns defaulting to published data (0). Relation columns store constraint symbols and permit NULL. The definition does not make flag 1 an assertion of exactness, reliability or lack of censoring.

INFERRED: Because flag 1 occurs in every relation class, it cannot distinguish censored from uncensored rows here.

## Hidden qualification and qualitative results

OBSERVED: Each of activity_comment, data_validity_comment, text_value and standard_text_value is JSON NULL in every row, including all explicitly qualified comparison rows. For each field separately:

| Assay | Relation | NULL count per field | Non-empty distinct values / frequencies |
| --- | --- | --- | --- |
| CHEMBL3301370 | < | 274 | None (0) |
| CHEMBL3301370 | > | 84 | None (0) |
| CHEMBL3301370 | NULL | 744 | None (0) |
| CHEMBL3301371 | < | 115 | None (0) |
| CHEMBL3301371 | > | 127 | None (0) |
| CHEMBL3301371 | NULL | 595 | None (0) |
| CHEMBL3301372 | < | 104 | None (0) |
| CHEMBL3301372 | > | 15 | None (0) |
| CHEMBL3301372 | NULL | 289 | None (0) |

OBSERVED: Exhaustive distinct-value enumeration therefore yields no `<`, `>`, lower/upper-bound, below/above-range, failure, unreliable, not-determined/NA or qualitative-outcome text in these fields. No keyword-only filter was used: every distinct non-empty value would have been retained. The JSON reports full field frequencies separately by assay and class. data_validity_description, upper_value and standard_upper_value are also NULL throughout; activity_properties is an empty list and potential_duplicate is 0 throughout.

DOCUMENTED: The [ChEMBL FAQ](https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/chembl-data-questions) explains validity flags and depositor qualitative comments. Their absence here is not a documented guarantee of reliability or uncensored measurement.

## Boundary-value enumeration

OBSERVED: The following counts apply **independently to both value and standard_value**; their complete enumerations agree. Cells count stored numerical values, not unknown true clearance. The JSON enumerates activity IDs for every bucket crossed with both raw and standard relations, including all zero combinations.

| Assay | Raw relation | Standard relation | Below 3 | Exactly 3 | 3 < value < 150 | Exactly 150 | Above 150 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CHEMBL3301370 | < | < | 0 | 274 | 0 | 0 | 0 |
| CHEMBL3301370 | > | > | 0 | 0 | 0 | 84 | 0 |
| CHEMBL3301370 | NULL | NULL | 0 | 13 | 731 | 0 | 0 |
| CHEMBL3301371 | < | < | 0 | 115 | 0 | 0 | 0 |
| CHEMBL3301371 | > | > | 0 | 0 | 0 | 127 | 0 |
| CHEMBL3301371 | NULL | NULL | 0 | 2 | 593 | 0 | 0 |
| CHEMBL3301372 | < | < | 0 | 104 | 0 | 0 | 0 |
| CHEMBL3301372 | > | > | 0 | 0 | 0 | 15 | 0 |
| CHEMBL3301372 | NULL | NULL | 0 | 0 | 289 | 0 | 0 |

OBSERVED: All values are numeric. NULL-at-3 counts reproduce **13 / 2 / 0** for human microsome / rat hepatocyte / human hepatocyte. NULL-at-150 counts are **0 / 0 / 0**. No stored numeric value is below 3 or above 150 in either field. Explicit `<3` and `>150` records still represent inequalities; these checks do not erase them.

### Individual NULL-at-3 records

| Assay | activity_id | molecule_chembl_id | value | standard_value | raw / standard relation | flag |
| --- | --- | --- | --- | --- | --- | --- |
| CHEMBL3301370 | 14769802 | CHEMBL70972 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769803 | CHEMBL271012 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769804 | CHEMBL383322 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769805 | CHEMBL552512 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769806 | CHEMBL2171047 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769807 | CHEMBL2208431 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769808 | CHEMBL1917448 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769809 | CHEMBL119385 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769810 | CHEMBL2031229 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769811 | CHEMBL1917445 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769812 | CHEMBL452273 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769813 | CHEMBL390191 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301370 | 14769814 | CHEMBL1529362 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301371 | 14768823 | CHEMBL589973 | 3.0 | 3.0 | NULL / NULL | 1 |
| CHEMBL3301371 | 14768825 | CHEMBL364714 | 3.0 | 3.0 | NULL / NULL | 1 |

OBSERVED: Each of these 15 records was inspected individually: all four requested comment/text fields and both upper-value fields are NULL; potential_duplicate is 0; document is CHEMBL3301361; src_id is 27. Their exact record_id, file location, units and additional retained fields are listed per record in the JSON. HLM uses microL/min/mg -> mL.min-1.g-1; rat uses microL/min/1E6 cells -> uL.min-1.(10^6cells)-1.

UNRESOLVED: A stored value of 3.0 with NULL relation cannot distinguish an exact observation from rounding, a reporting floor or an omitted qualifier. No censor category is assigned from value alone.

## Raw versus standard value, units and precision

| Assay | Relation | Rows | Exact numeric matches | Different value strings | Different decimal precision | Raw units -> standard units |
| --- | --- | --- | --- | --- | --- | --- |
| CHEMBL3301370 | < | 274 | 274 | 0 | 0 | microL/min/mg -> mL.min-1.g-1 (274) |
| CHEMBL3301370 | > | 84 | 84 | 0 | 0 | microL/min/mg -> mL.min-1.g-1 (84) |
| CHEMBL3301370 | NULL | 744 | 744 | 0 | 0 | microL/min/mg -> mL.min-1.g-1 (744) |
| CHEMBL3301371 | < | 115 | 115 | 0 | 0 | microL/min/1E6 cells -> uL.min-1.(10^6cells)-1 (115) |
| CHEMBL3301371 | > | 127 | 127 | 0 | 0 | microL/min/1E6 cells -> uL.min-1.(10^6cells)-1 (127) |
| CHEMBL3301371 | NULL | 595 | 595 | 0 | 0 | microL/min/1E6 cells -> uL.min-1.(10^6cells)-1 (595) |
| CHEMBL3301372 | < | 104 | 104 | 0 | 0 | microL/min/1E6 cells -> uL.min-1.(10^6cells)-1 (104) |
| CHEMBL3301372 | > | 15 | 15 | 0 | 0 | microL/min/1E6 cells -> uL.min-1.(10^6cells)-1 (15) |
| CHEMBL3301372 | NULL | 289 | 289 | 0 | 0 | microL/min/1E6 cells -> uL.min-1.(10^6cells)-1 (289) |

OBSERVED: Raw value strings and standard value strings are identical for every row; no precision change is visible in the API fields. Type changes from CLint to CL for every row. Units have different strings in each assay, with the same change across NULL, `<` and `>` classes.

INFERRED (unit algebra): microL/min/mg and mL/min/g have the same numeric scale; the hepatocyte change is a spelling change for microlitres/minute per million cells. No numerical rescaling or rounding is apparent between these two API fields. This does not recover laboratory precision before deposition.

INFERRED: Nothing in the observed type/unit/value changes explains missing relations: raw relation is already NULL, and supplied inequalities survive the same standardisation. Upstream omission or ingestion history remains UNRESOLVED.

## Supplementary same-document check

OBSERVED: The acquired corpus and workspace search yielded only these three quantitative assays for CHEMBL3301361, their derived copies and audit reports. No local ChEMBL database dump or unrelated endpoint activity records were found. Search scope and exclusions are recorded in the JSON.

UNRESOLVED: Systematic NULL use elsewhere in the deposition, preservation of inequalities elsewhere, and patterns across LogD, solubility, pKa or protein binding cannot be assessed from the local evidence. **This supplementary check stops here because additional acquisition would be required.** No additional activity, assay or document dataset was downloaded.

## Documented definitions and limits

DOCUMENTED: [ChEMBL 37 schema](https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/schema_documentation.txt) defines raw relation/value/units as the source-dataset fields and standard fields as their standardised counterparts. The schema permits nullable relation columns but supplies no NULL-means-equals convention. The documentation was read on 2026-09-17 (96,496 bytes; SHA-256 `170021a58a6d8c09ca088eae5ee75c9b9d0b3b457c6428adf63986b9d765f9fb`); no raw dataset was replaced.

DOCUMENTED: The [current ChEMBL deposition guide](https://chembl.gitbook.io/chembl-data-deposition-guide/file-structure/field-names-and-data-types-minimal-data-submission/activity.tsv) requires a relation with numeric VALUE submissions and directs NA outcomes to TEXT_VALUE. That guidance does not define the meaning of NULL in this older AstraZeneca deposition. It cannot retrospectively establish an equals convention or prove that these rows are invalid.

## Evidence resolution

INFERRED: These three assays show a consistent distinction between explicit inequalities and numeric records without a recorded qualifier. This supports an unqualified-numeric interpretation and argues against loss of an equals sign specifically between the retained raw and standard fields.

UNRESOLVED: Unqualified numeric storage is not proof of an uncensored assay observation. Neither standard_flag=1, empty comments nor unchanged numeric strings establishes the missing historical convention. The 15 NULL-at-3 records remain individually unresolved, and unrelated same-document endpoints are unavailable. The evidence does not justify recoding NULL to equals.

Scope: This verdict concerns only these three assays in the frozen ChEMBL 37 API acquisition, not ChEMBL globally.

REMAINS_AMBIGUOUS
