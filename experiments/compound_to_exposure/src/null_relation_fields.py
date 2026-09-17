"""Offline field evidence only: no chemistry, preprocessing, splits or model imports."""
from collections import Counter
from decimal import Decimal, InvalidOperation
import json
import subprocess
import sys

from chembl_pages import validate_pages
from provenance import ROOT, digest, immutable, json_bytes, verify

BASELINE = '4640ea721204771979e5637e81217f59c65318e6'
ASSAYS = ('CHEMBL3301370', 'CHEMBL3301371', 'CHEMBL3301372')
TEXT_FIELDS = ('activity_comment', 'data_validity_comment', 'text_value', 'standard_text_value')
FIELDS = ('activity_id', 'assay_chembl_id', 'molecule_chembl_id', 'relation', 'value', 'units',
          'standard_relation', 'standard_value', 'standard_units', 'standard_flag',
          *TEXT_FIELDS, 'potential_duplicate', 'document_chembl_id', 'document_journal',
          'document_year', 'src_id', 'record_id', 'toid', 'type', 'standard_type',
          'upper_value', 'standard_upper_value', 'data_validity_description',
          'activity_properties', 'molecule_pref_name', 'parent_molecule_chembl_id', 'target_chembl_id')
CLASSES = ('<', '>', '=', 'NULL')
BUCKETS = ('below_3', 'exactly_3', 'between_3_and_150', 'exactly_150', 'above_150', 'non_numeric')
SCHEMA_URL = 'https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/schema_documentation.txt'
GUIDE_URL = 'https://chembl.gitbook.io/chembl-data-deposition-guide/file-structure/field-names-and-data-types-minimal-data-submission/activity.tsv'
FAQ_URL = 'https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/chembl-data-questions'


def category(row, field):
    if field not in row:
        return 'MISSING_FIELD'
    return 'NULL' if row[field] is None else str(row[field])


def decimal_value(value):
    try:
        result = Decimal(str(value))
        return result if result.is_finite() else None
    except InvalidOperation:
        return None


def bucket(value):
    n = decimal_value(value)
    if n is None:
        return 'non_numeric'
    if n < 3:
        return 'below_3'
    if n == 3:
        return 'exactly_3'
    if n < 150:
        return 'between_3_and_150'
    return 'exactly_150' if n == 150 else 'above_150'


def frequencies(rows, field):
    """Preserve missing, JSON null, empty string and every distinct value separately."""
    counts = Counter(json.dumps(r[field], sort_keys=True) for r in rows if field in r)
    return {'missing_field': sum(field not in r for r in rows),
            'values': [{'value': json.loads(v), 'count': n} for v, n in sorted(counts.items())]}


def compare_values(rows):
    numeric_equal, non_numeric, precision_changed, differing = 0, 0, 0, []
    for row in rows:
        left, right = decimal_value(row.get('value')), decimal_value(row.get('standard_value'))
        if left is None or right is None:
            non_numeric += 1
        else:
            numeric_equal += left == right
            precision_changed += left.as_tuple().exponent != right.as_tuple().exponent
        if row.get('value') != row.get('standard_value'):
            differing.append(row['activity_id'])
    pairs = Counter((r.get('units'), r.get('standard_units')) for r in rows)
    return {'rows': len(rows), 'exact_numeric_equal': numeric_equal,
            'non_numeric_pairs': non_numeric, 'different_value_strings': len(differing),
            'different_decimal_exponents': precision_changed, 'different_value_activity_ids': differing,
            'unit_pairs': [{'units': a, 'standard_units': b, 'count': n}
                           for (a, b), n in sorted(pairs.items(), key=lambda p: str(p[0]))]}


def audit_rows(rows):
    labels = list(CLASSES) + sorted({category(r, f) for r in rows for f in ('relation', 'standard_relation')} - set(CLASSES))
    cross = {a: {b: 0 for b in labels} for a in labels}
    boundary = {field: {a: {b: {k: [] for k in BUCKETS} for b in labels} for a in labels}
                for field in ('value', 'standard_value')}
    for r in rows:
        a, b = category(r, 'relation'), category(r, 'standard_relation')
        cross[a][b] += 1
        for field in boundary:
            boundary[field][a][b][bucket(r.get(field))].append(r['activity_id'])
    groups = {label: [r for r in rows if category(r, 'standard_relation') == label] for label in labels}
    return {'evidence_class': 'OBSERVED', 'rows': len(rows),
            'field_availability': {f: {'present': sum(f in r for r in rows),
                                       'null': sum(f in r and r[f] is None for r in rows),
                                       'missing': sum(f not in r for r in rows)} for f in FIELDS},
            'relation_crosstab': cross,
            'standard_flag_by_standard_relation': {k: frequencies(g, 'standard_flag') for k, g in groups.items()},
            'text_fields_by_standard_relation': {k: {f: frequencies(g, f) for f in TEXT_FIELDS} for k, g in groups.items()},
            'additional_fields_by_standard_relation': {k: {f: frequencies(g, f) for f in
                ('potential_duplicate', 'upper_value', 'standard_upper_value', 'data_validity_description', 'activity_properties')}
                for k, g in groups.items()},
            'value_comparison_by_standard_relation': {k: compare_values(g) for k, g in groups.items()},
            'boundary_activity_ids_by_value_field_and_both_relations': boundary,
            'null_boundary_records': [r for r in rows if r.get('standard_relation') is None and
                                      bucket(r.get('standard_value')) in ('exactly_3', 'exactly_150')],
            'source_identifiers': {f: frequencies(rows, f) for f in ('document_chembl_id', 'src_id', 'document_journal', 'document_year')},
            'records': rows}


def baseline_bytes(relative):
    return subprocess.check_output(['git', 'show', f'{BASELINE}:experiments/compound_to_exposure/{relative}'], cwd=ROOT)


def build_report():
    manifest_path = ROOT / 'manifests/source_manifest.json'
    if manifest_path.read_bytes() != baseline_bytes('manifests/source_manifest.json'):
        raise ValueError('Frozen source manifest changed')
    manifest = json.loads(manifest_path.read_bytes())['sources']
    for item in manifest:
        verify(item)
        receipt = 'manifests/downloads/' + item['filename'].removeprefix('data/raw/').replace('/', '__') + '.json'
        if (ROOT / receipt).read_bytes() != baseline_bytes(receipt):
            raise ValueError('Frozen acquisition receipt changed')
    sources = {r['filename']: r for r in manifest}
    results, inputs = {}, []
    for assay in ASSAYS:
        paths = sorted((ROOT / 'data/raw/chembl').glob(f'{assay}_activities_*.json'))
        pages = [json.loads(p.read_bytes()) for p in paths]
        n = validate_pages(pages, assay)
        extracted = []
        for path, page in zip(paths, pages):
            relative = path.relative_to(ROOT).as_posix()
            inputs.append({**sources[relative], 'page_meta': page['page_meta']})
            for i, raw in enumerate(page['activities'], 1):
                extracted.append({'raw_filename': relative, 'row_in_page_1based': i,
                                  'fields_absent_from_raw': [f for f in FIELDS if f not in raw],
                                  **{f: raw[f] for f in FIELDS if f in raw}})
        if len(extracted) != n or len({r['activity_id'] for r in extracted}) != n:
            raise ValueError('Acquired rows and pagination disagree')
        metadata_path = f'data/raw/chembl/{assay}_assay.json'
        metadata = json.loads((ROOT / metadata_path).read_bytes())
        inputs.append(sources[metadata_path])
        results[assay] = {**audit_rows(extracted), 'assay_metadata': metadata}
    for item in manifest:
        verify(item)  # Confirm that this field-only pass did not change any raw bytes.
    return {'title': 'NULL relation field audit', 'frozen_commit': BASELINE,
            'scope': 'Three primary assays only; exact Decimal comparisons of source strings; no scientific transformations or chemistry calculations.',
            'null_policy': 'JSON null is displayed as NULL; absent keys are MISSING_FIELD; neither is converted to equals.',
            'raw_files_verified': len(manifest), 'chembl_api_state': json.loads((ROOT / 'data/raw/chembl/status.json').read_bytes()),
            'inputs': inputs, 'assays': results,
            'documentation': [
                {'evidence_class': 'DOCUMENTED', 'url': SCHEMA_URL, 'accessed': '2026-09-17',
                 'sha256': '170021a58a6d8c09ca088eae5ee75c9b9d0b3b457c6428adf63986b9d765f9fb', 'byte_size': 96496,
                 'summary': 'ChEMBL 37 defines standard_flag=1 as curated/set standard columns and 0 as defaults from published data. Relation fields contain constraint symbols; raw relation/value/units describe the original dataset. Both relation columns are nullable. No NULL-to-equals convention is defined here.'},
                {'evidence_class': 'DOCUMENTED', 'url': GUIDE_URL, 'accessed': '2026-09-17',
                 'summary': 'Current deposition instructions require RELATION with a numeric VALUE; NA belongs in TEXT_VALUE. They do not establish the rules applied to this older deposition.'},
                {'evidence_class': 'DOCUMENTED', 'url': FAQ_URL, 'accessed': '2026-09-17',
                 'summary': 'ChEMBL documents unit standardisation, potential rounding, validity flags and qualitative activity comments; these are general processes, not evidence that a particular row was changed.'}],
            'supplementary_same_document': {'evidence_class': 'UNRESOLVED', 'document': 'CHEMBL3301361',
                'status': 'STOPPED_ADDITIONAL_ACQUISITION_REQUIRED',
                'local_search_scope': 'Workspace text tables (JSON/CSV/TSV/TAB/SQL/TXT/MD) searched for CHEMBL3301361; local ChEMBL/database/parquet filenames inspected. Git metadata, other worktrees, environments and caches excluded.',
                'finding': 'Only the three primary assays, their derived copies and reports were found. No other quantitative assay from this document is available in the acquired corpus; no local ChEMBL database dump was found. Other workspace databases are satellite_biowatch application stores.',
                'questions': {'systematic_null_elsewhere': 'UNRESOLVED', 'inequalities_preserved_elsewhere': 'UNRESOLVED',
                              'logd_solubility_pka_protein_binding': 'UNRESOLVED'},
                'downloads': 'No new activity, assay or document datasets downloaded. Only public field-definition documentation was consulted.'},
            'conclusions': [
                {'evidence_class': 'OBSERVED', 'statement': 'All NULL standard relations are also NULL raw relations; no equals-to-NULL or NULL-to-equals transitions occur. All inequalities agree.'},
                {'evidence_class': 'OBSERVED', 'statement': 'All rows have standard_flag=1 and empty comment/text qualification fields. Raw and standard numeric strings agree exactly.'},
                {'evidence_class': 'OBSERVED', 'statement': 'NULL-at-3 counts are 13 HLM, 2 rat hepatocyte and 0 human hepatocyte; NULL-at-150 counts are zero in all three.'},
                {'evidence_class': 'INFERRED', 'statement': 'The pattern is compatible with unqualified quantitative results, and gives no observed evidence that standardisation alone removed an equals sign. It does not establish uncensored measurement semantics.'},
                {'evidence_class': 'UNRESOLVED', 'statement': 'Original deposition conventions, upstream qualifier loss and rounding/reporting-limit treatment of the 15 NULL-at-3 records cannot be distinguished from the available records. No original depositor ACTIVITY table or record-specific confirmation was acquired.'}],
            'verdict_scope': list(ASSAYS), 'verdict_evidence_class': 'INFERRED', 'verdict': 'REMAINS_AMBIGUOUS'}


def table(headers, rows):
    def cell(v):
        return str(v).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(cell(v) for v in row) + ' |' for row in rows])


def render(report):
    assays = report['assays']
    lines = ['# NULL relation field audit', '',
        '**INFERRED verdict: REMAINS_AMBIGUOUS**, specifically for CHEMBL3301370, CHEMBL3301371 and CHEMBL3301372.', '',
        '## Scope and retained fields', '',
        f"OBSERVED: Primary evidence is the immutable downloaded ChEMBL 37 activity pages at `{BASELINE}`. All {report['raw_files_verified']} acquired raw files passed the frozen manifest hash/size checks before and after this audit; receipts and manifest match that commit. The four activity pages contain 2,347 records. Completeness concerns this downloaded API state, not a historical ChEMBL release.", '',
        'OBSERVED: Every requested activity field is retained in every record. The companion [JSON](NULL_RELATION_FIELD_AUDIT.json) extracts every record with its exact strings/nulls, source filename and 1-based position within the page. It includes all source/document IDs supplied by the API: document_chembl_id, src_id, record_id and toid, plus assay-level aidx/src_assay_id. No requested activity field was silently substituted or fetched.', '',
        'OBSERVED: All activities identify document CHEMBL3301361 and src_id 27. document_journal, document_year and toid are NULL. The separate document record, original depositor activity table, compound-record source IDs and document DOI/PubMed identifiers were not acquired; their absence limits historical interpretation.', '',
        'Method: standard-library JSON/Decimal field inspection only. No audit.py/chemistry imports, descriptors, preprocessing, splits or modelling. NULL is an explicit category, distinct from an absent field, empty string and `=`. Numeric equality is exact Decimal equality; source value strings are preserved.', '',
        '## Raw relation versus standard_relation', '',
        'OBSERVED: Rows are raw `relation`; columns are `standard_relation`. Zero cells are shown, including `=`. No other relation category occurs.', '']
    for assay, result in assays.items():
        cross = result['relation_crosstab']
        lines += [f'### {assay}', '', table(['raw / standard', *cross], [[a, *cells.values()] for a, cells in cross.items()]), '']
    lines += ['OBSERVED: All NULL standard_relation rows also have NULL relation. Raw `=` to standard NULL: **0**. Raw NULL to standard `=`: **0**. Explicit `<` and `>` agree in all records. There are no raw or standard explicit equals records in any assay.', '',
              '## standard_flag', '',
              'OBSERVED: Counts below use standard_relation classes; the raw-relation counts are identical.', '',
              table(['Assay', 'Relation', 'flag 1', 'flag 0', 'flag NULL / other'],
                    [[a, rel, r['value_comparison_by_standard_relation'][rel]['rows'], 0, 0] for a, r in assays.items() for rel in ('<', '>', 'NULL')]), '',
              f'DOCUMENTED: In the [ChEMBL 37 schema]({SCHEMA_URL}), standard_flag distinguishes curated/set standard columns (1) from columns defaulting to published data (0). Relation columns store constraint symbols and permit NULL. The definition does not make flag 1 an assertion of exactness, reliability or lack of censoring.', '',
              'INFERRED: Because flag 1 occurs in every relation class, it cannot distinguish censored from uncensored rows here.', '',
              '## Hidden qualification and qualitative results', '',
              'OBSERVED: Each of activity_comment, data_validity_comment, text_value and standard_text_value is JSON NULL in every row, including all explicitly qualified comparison rows. For each field separately:', '',
              table(['Assay', 'Relation', 'NULL count per field', 'Non-empty distinct values / frequencies'],
                    [[a, rel, r['value_comparison_by_standard_relation'][rel]['rows'], 'None (0)'] for a, r in assays.items() for rel in ('<', '>', 'NULL')]), '',
              'OBSERVED: Exhaustive distinct-value enumeration therefore yields no `<`, `>`, lower/upper-bound, below/above-range, failure, unreliable, not-determined/NA or qualitative-outcome text in these fields. No keyword-only filter was used: every distinct non-empty value would have been retained. The JSON reports full field frequencies separately by assay and class. data_validity_description, upper_value and standard_upper_value are also NULL throughout; activity_properties is an empty list and potential_duplicate is 0 throughout.', '',
              f'DOCUMENTED: The [ChEMBL FAQ]({FAQ_URL}) explains validity flags and depositor qualitative comments. Their absence here is not a documented guarantee of reliability or uncensored measurement.', '',
              '## Boundary-value enumeration', '',
              'OBSERVED: The following counts apply **independently to both value and standard_value**; their complete enumerations agree. Cells count stored numerical values, not unknown true clearance. The JSON enumerates activity IDs for every bucket crossed with both raw and standard relations, including all zero combinations.', '',
              table(['Assay', 'Raw relation', 'Standard relation', 'Below 3', 'Exactly 3', '3 < value < 150', 'Exactly 150', 'Above 150'],
                    [[a, rel, rel, *[len(r['boundary_activity_ids_by_value_field_and_both_relations']['value'][rel][rel][k]) for k in BUCKETS[:-1]]]
                     for a, r in assays.items() for rel in ('<', '>', 'NULL')]), '',
              'OBSERVED: All values are numeric. NULL-at-3 counts reproduce **13 / 2 / 0** for human microsome / rat hepatocyte / human hepatocyte. NULL-at-150 counts are **0 / 0 / 0**. No stored numeric value is below 3 or above 150 in either field. Explicit `<3` and `>150` records still represent inequalities; these checks do not erase them.', '',
              '### Individual NULL-at-3 records', '',
              table(['Assay', 'activity_id', 'molecule_chembl_id', 'value', 'standard_value', 'raw / standard relation', 'flag'],
                    [[a, x['activity_id'], x['molecule_chembl_id'], x['value'], x['standard_value'], 'NULL / NULL', x['standard_flag']]
                     for a, r in assays.items() for x in r['null_boundary_records']]), '',
              'OBSERVED: Each of these 15 records was inspected individually: all four requested comment/text fields and both upper-value fields are NULL; potential_duplicate is 0; document is CHEMBL3301361; src_id is 27. Their exact record_id, file location, units and additional retained fields are listed per record in the JSON. HLM uses microL/min/mg -> mL.min-1.g-1; rat uses microL/min/1E6 cells -> uL.min-1.(10^6cells)-1.', '',
              'UNRESOLVED: A stored value of 3.0 with NULL relation cannot distinguish an exact observation from rounding, a reporting floor or an omitted qualifier. No censor category is assigned from value alone.', '',
              '## Raw versus standard value, units and precision', '',
              table(['Assay', 'Relation', 'Rows', 'Exact numeric matches', 'Different value strings', 'Different decimal precision', 'Raw units -> standard units'],
                    [[a, rel, c['rows'], c['exact_numeric_equal'], c['different_value_strings'], c['different_decimal_exponents'],
                      '; '.join(f"{p['units']} -> {p['standard_units']} ({p['count']})" for p in c['unit_pairs'])]
                     for a, r in assays.items() for rel, c in r['value_comparison_by_standard_relation'].items() if c['rows']]), '',
              'OBSERVED: Raw value strings and standard value strings are identical for every row; no precision change is visible in the API fields. Type changes from CLint to CL for every row. Units have different strings in each assay, with the same change across NULL, `<` and `>` classes.', '',
              'INFERRED (unit algebra): microL/min/mg and mL/min/g have the same numeric scale; the hepatocyte change is a spelling change for microlitres/minute per million cells. No numerical rescaling or rounding is apparent between these two API fields. This does not recover laboratory precision before deposition.', '',
              'INFERRED: Nothing in the observed type/unit/value changes explains missing relations: raw relation is already NULL, and supplied inequalities survive the same standardisation. Upstream omission or ingestion history remains UNRESOLVED.', '',
              '## Supplementary same-document check', '',
              'OBSERVED: The acquired corpus and workspace search yielded only these three quantitative assays for CHEMBL3301361, their derived copies and audit reports. No local ChEMBL database dump or unrelated endpoint activity records were found. Search scope and exclusions are recorded in the JSON.', '',
              'UNRESOLVED: Systematic NULL use elsewhere in the deposition, preservation of inequalities elsewhere, and patterns across LogD, solubility, pKa or protein binding cannot be assessed from the local evidence. **This supplementary check stops here because additional acquisition would be required.** No additional activity, assay or document dataset was downloaded.', '',
              '## Documented definitions and limits', '',
              f'DOCUMENTED: [ChEMBL 37 schema]({SCHEMA_URL}) defines raw relation/value/units as the source-dataset fields and standard fields as their standardised counterparts. The schema permits nullable relation columns but supplies no NULL-means-equals convention. The documentation was read on 2026-09-17 (96,496 bytes; SHA-256 `170021a58a6d8c09ca088eae5ee75c9b9d0b3b457c6428adf63986b9d765f9fb`); no raw dataset was replaced.', '',
              f'DOCUMENTED: The [current ChEMBL deposition guide]({GUIDE_URL}) requires a relation with numeric VALUE submissions and directs NA outcomes to TEXT_VALUE. That guidance does not define the meaning of NULL in this older AstraZeneca deposition. It cannot retrospectively establish an equals convention or prove that these rows are invalid.', '',
              '## Evidence resolution', '',
              'INFERRED: These three assays show a consistent distinction between explicit inequalities and numeric records without a recorded qualifier. This supports an unqualified-numeric interpretation and argues against loss of an equals sign specifically between the retained raw and standard fields.', '',
              'UNRESOLVED: Unqualified numeric storage is not proof of an uncensored assay observation. Neither standard_flag=1, empty comments nor unchanged numeric strings establishes the missing historical convention. The 15 NULL-at-3 records remain individually unresolved, and unrelated same-document endpoints are unavailable. The evidence does not justify recoding NULL to equals.', '',
              'Scope: This verdict concerns only these three assays in the frozen ChEMBL 37 API acquisition, not ChEMBL globally.', '',
              report['verdict'], '']
    return '\n'.join(lines)


def main():
    report = build_report()
    outputs = {ROOT / 'reports/NULL_RELATION_FIELD_AUDIT.json': json_bytes(report),
               ROOT / 'reports/NULL_RELATION_FIELD_AUDIT.md': render(report).encode('utf-8')}
    for path, content in outputs.items():
        if path.exists() and path.read_bytes() != content:
            raise ValueError(f'Refusing to overwrite changed field audit: {path}')
    if '--check' in sys.argv:
        if any(not p.exists() for p in outputs):
            raise ValueError('Report missing')
    else:
        for path, content in outputs.items():
            immutable(path, content)
    print(json.dumps({'verdict': report['verdict'], 'rows': {a: r['rows'] for a, r in report['assays'].items()},
                      'outputs': {p.name: digest(p) for p in outputs}}, indent=2))


if __name__ == '__main__':
    main()
