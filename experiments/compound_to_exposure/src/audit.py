"""Forensic audit of six frozen sources. All source rows remain in evidence tables."""
from collections import Counter, defaultdict
import csv
import io
import json
import platform
import sys
import numpy as np
from rdkit import rdBase
from chemistry import chemical, distribution, duplicate_summary, measurement, missing, number, numeric_equal, PROPERTIES
from provenance import ROOT, immutable, json_bytes, record, verify
from chembl_pages import validate_pages

HLM, RAT, HH = 'CHEMBL3301370', 'CHEMBL3301371', 'CHEMBL3301372'
TM, TH, BIO = 'Clearance_Microsome_AZ', 'Clearance_Hepatocyte_AZ', 'Biogen'
HLM_COLUMN = 'LOG HLM_CLint (mL/min/kg)'
EXPECTED = {HLM: 1102, RAT: 837, HH: 408}
IDENTITY = ('RDKit 2025.03.6 sanitized isomeric canonical SMILES; stereochemistry, isotopes, charge and all '
            'disconnected fragments retained. No parent selection, desalting, neutralization, tautomer normalization '
            'or stereo removal. RDKit ordinary explicit-H handling applies. Equality is string equality of valid keys; '
            'missing/invalid structures never match. Identity is representation-specific, not proof of sample identity.')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def csv_bytes(rows, fields=None):
    if fields is None:
        fields = sorted(set().union(*(r.keys() for r in rows))) if rows else ['status']
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow({k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v for k, v in row.items()})
    return stream.getvalue().encode('utf-8')


def enrich(row, source, index, raw_path, smiles, value, identifier, relation=None):
    parsed = measurement(value, relation)
    if source.startswith('CHEMBL') and missing(relation):
        parsed['relation'] = 'UNKNOWN'
        if parsed['status'] == 'VALID':
            parsed['status'] = 'UNKNOWN_RELATION'
    return {**row, 'source': source, 'source_row_1based': index, 'raw_filename': raw_path.relative_to(ROOT).as_posix(),
            'raw_identifier': identifier, 'raw_smiles': smiles, 'raw_target': value,
            'measurement_audit': parsed, **chemical(smiles)}


def load_sources():
    datasets, assays = {}, {}
    for assay in (HLM, RAT, HH):
        meta = read_json(ROOT / f'data/raw/chembl/{assay}_assay.json')
        assays[assay] = meta
        rows = []
        pages = [(path, read_json(path)) for path in sorted((ROOT / 'data/raw/chembl').glob(f'{assay}_activities_*.json'))]
        observed = validate_pages((page for _, page in pages), assay)
        if observed != EXPECTED[assay]:
            raise ValueError(f'Frozen ChEMBL count differs from expectation: {assay}')
        for path, page in pages:
            for i, row in enumerate(page['activities'], 1):
                enriched = enrich(row, assay, i, path, row.get('canonical_smiles'), row.get('standard_value'), row['molecule_chembl_id'], row.get('standard_relation'))
                for field in ('assay_organism', 'assay_tax_id', 'assay_tissue', 'assay_cell_type', 'assay_subcellular_fraction', 'assay_strain', 'cell_chembl_id', 'tissue_chembl_id'):
                    enriched[field] = meta.get(field)
                rows.append(enriched)
        stored_total = pages[0][1]['page_meta']['total_count']
        if not (len(rows) == len({r['activity_id'] for r in rows}) == observed == stored_total):
            raise ValueError(f'ChEMBL page total, observed rows and unique activity IDs differ: {assay}')
        datasets[assay] = rows
    for source in (TM, TH):
        path = ROOT / f'data/raw/tdc/{source.lower()}.tab'
        with path.open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle, delimiter='\t')
            if reader.fieldnames != ['ID', 'X', 'Y']:
                raise ValueError(f'Unexpected TDC schema: {reader.fieldnames}')
            datasets[source] = [enrich(r, source, i, path, r['X'], r['Y'], r['ID']) for i, r in enumerate(reader, 1)]
    path = ROOT / 'data/raw/biogen/ADME_public_set_3521.csv'
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if HLM_COLUMN not in reader.fieldnames or 'SMILES' not in reader.fieldnames:
            raise ValueError('Biogen HLM/SMILES column absent; no substitute endpoint')
        datasets[BIO] = [enrich(r, BIO, i, path, r['SMILES'], r[HLM_COLUMN], r['Internal ID']) for i, r in enumerate(reader, 1)]
    return datasets, assays


def index_by(rows, key='canonical_smiles_rdkit'):
    out = defaultdict(list)
    for r in rows:
        if not missing(r.get(key)):
            out[r[key]].append(r)
    return out


def ref(row):
    return {'source': row['source'], 'source_row_1based': row['source_row_1based'], 'raw_filename': row['raw_filename'],
            'identifier': row['raw_identifier'], 'activity_id': row.get('activity_id'), 'target': row['raw_target'],
            'standard_relation': row.get('standard_relation'), 'standard_units': row.get('standard_units')}


def source_summary(rows):
    states = Counter(r['structure_status'] for r in rows)
    return {'row_count': len(rows), 'unique_identifiers': len({r['raw_identifier'] for r in rows if not missing(r['raw_identifier'])}),
            'missing_identifiers': sum(missing(r['raw_identifier']) for r in rows),
            'unique_raw_smiles': len({r['raw_smiles'] for r in rows if not missing(r['raw_smiles'])}),
            'valid_structure_rows': states['VALID'], 'invalid_structure_rows': states['INVALID'], 'missing_structure_rows': states['MISSING'],
            **duplicate_summary([r['canonical_smiles_rdkit'] for r in rows]),
            'target_distribution': distribution([r['raw_target'] for r in rows]),
            'molecules_with_undefined_stereo': sum((r['undefined_stereo_elements'] or 0) > 0 for r in rows),
            'multicomponent_rows': sum((r['fragment_count'] or 0) > 1 for r in rows),
            'dummy_atom_rows': sum((r['dummy_atom_count'] or 0) > 0 for r in rows),
            'chemical_space': {p: distribution([r[p] for r in rows]) for p in PROPERTIES}}


def relations(rows, field, value_field):
    counts = Counter('UNKNOWN' if missing(r.get(field)) else str(r[field]) for r in rows)
    boundaries = {}
    for relation in sorted(counts):
        vals = Counter(str(r.get(value_field)) for r in rows if ('UNKNOWN' if missing(r.get(field)) else str(r[field])) == relation)
        boundaries[relation] = [{'reported_value': v, 'count': n} for v, n in sorted(vals.items())]
    return {'counts': {'<': counts['<'], '>': counts['>'], '=': counts['='], 'anything_else': sum(n for k, n in counts.items() if k not in ('<', '>', '='))},
            'all_relation_counts': dict(sorted(counts.items())), 'reported_values_by_relation': boundaries}


def species_audit(tdc, rat, human):
    ri, hi = index_by(rat), index_by(human)
    rid, hid = index_by(rat, 'raw_identifier'), index_by(human, 'raw_identifier')
    evidence = []
    for r in tdc:
        key = r['canonical_smiles_rdkit']
        rr, hr = ri.get(key, []), hi.get(key, [])
        group = 'ambiguous_unparseable' if key is None else 'both' if rr and hr else 'rat_only' if rr else 'human_only' if hr else 'neither'
        rv = [x for x in rr if numeric_equal(r['raw_target'], x['raw_target'])]
        hv = [x for x in hr if numeric_equal(r['raw_target'], x['raw_target'])]
        value_group = 'both' if rv and hv else 'rat_only' if rv else 'human_only' if hv else 'unresolved'
        riv = [x for x in rid.get(r['raw_identifier'], []) if numeric_equal(r['raw_target'], x['raw_target'])]
        hiv = [x for x in hid.get(r['raw_identifier'], []) if numeric_equal(r['raw_target'], x['raw_target'])]
        id_value_group = 'both' if riv and hiv else 'rat_only' if riv else 'human_only' if hiv else 'unresolved'
        evidence.append({**ref(r), 'canonical_smiles_rdkit': key, 'structure_species_class': group,
                         'numeric_label_matches_species': value_group, 'rat_candidates': [ref(x) for x in rr],
                         'human_candidates': [ref(x) for x in hr], 'rat_numeric_matches': [ref(x) for x in rv], 'human_numeric_matches': [ref(x) for x in hv],
                         'secondary_id_numeric_matches_species': id_value_group,
                         'secondary_rat_id_numeric_matches': [{**ref(x), 'canonical_smiles_rdkit': x['canonical_smiles_rdkit']} for x in riv],
                         'secondary_human_id_numeric_matches': [{**ref(x), 'canonical_smiles_rdkit': x['canonical_smiles_rdkit']} for x in hiv]})
    labels = ('rat_only', 'human_only', 'both', 'neither', 'ambiguous_unparseable')
    row_counts = {k: sum(r['structure_species_class'] == k for r in evidence) for k in labels}
    structure_counts = {k: len({r['canonical_smiles_rdkit'] for r in evidence if r['structure_species_class'] == k and r['canonical_smiles_rdkit'] is not None}) for k in labels}
    repeated = []
    for key, rows in sorted(index_by(evidence).items()):
        if len(rows) < 2:
            continue
        numbers = [number(r['target']) for r in rows]
        label_state = 'unresolved' if any(n is None for n in numbers) else 'identical' if len(set(numbers)) == 1 else 'different'
        rat_only = [r for r in rows if r['numeric_label_matches_species'] == 'rat_only']
        human_only = [r for r in rows if r['numeric_label_matches_species'] == 'human_only']
        strict_pair = (len(rows) == 2 and label_state == 'different'
                       and len(rat_only) == len(human_only) == 1
                       and len(rat_only[0]['rat_numeric_matches']) == 1
                       and len(human_only[0]['human_numeric_matches']) == 1)
        trace = ('distinct_labels_match_rat_and_human' if strict_pair else
                 'no_strict_structural_match_to_either_assay' if all(r['structure_species_class'] == 'neither' for r in rows) else
                 'all_labels_match_both_species' if all(r['numeric_label_matches_species'] == 'both' for r in rows) else
                 'partial_or_unresolved')
        id_classes = {r['secondary_id_numeric_matches_species'] for r in rows}
        id_trace = 'distinct_labels_match_rat_and_human' if label_state == 'different' and {'rat_only','human_only'} <= id_classes else 'partial_or_unresolved'
        repeated.append({'canonical_smiles_rdkit': key, 'rows': rows, 'label_state': label_state, 'trace_class': trace, 'secondary_id_trace_class': id_trace})
    matched = Counter(r['numeric_label_matches_species'] for r in evidence)
    positive_rat = any(r['structure_species_class'] == 'rat_only' and r['numeric_label_matches_species'] == 'rat_only' for r in evidence)
    positive_human = any(r['structure_species_class'] == 'human_only' and r['numeric_label_matches_species'] == 'human_only' for r in evidence)
    status = 'REPRODUCED' if positive_rat and positive_human else 'PARTIALLY_REPRODUCED' if matched['rat_only'] and matched['human_only'] else 'NOT_REPRODUCED'
    return {'OBSERVED': {'row_counts': row_counts, 'unique_valid_structure_counts': structure_counts,
                         'numeric_label_match_row_counts': dict(sorted(matched.items())),
                         'secondary_id_numeric_label_match_row_counts': dict(sorted(Counter(r['secondary_id_numeric_matches_species'] for r in evidence).items())),
                         'duplicate_label_groups': dict(sorted(Counter(r['label_state'] for r in repeated).items())),
                         'duplicate_trace_groups': dict(sorted(Counter(r['trace_class'] for r in repeated).items())),
                         'secondary_id_duplicate_trace_groups': dict(sorted(Counter(r['secondary_id_trace_class'] for r in repeated).items()))},
            'INFERRED': {'claim_status': status, 'decision_rule': 'REPRODUCED requires both rat-only and human-only structure matches with exactly matching numeric source labels. PARTIALLY_REPRODUCED requires label-specific matches to both species without both exclusive structural witnesses; otherwise NOT_REPRODUCED. Censored matches identify numeric boundaries only.',
                         'strict_duplicate_pair_rule': 'Exactly two TDC rows with different numeric labels: one has exactly one strict structure/value-matching rat record and no human value match; the other has exactly one strict structure/value-matching human record and no rat value match. Numeric agreement uses exact Decimal equality.'},
            'UNRESOLVED': 'Historical lineage cannot be proven by equality alone. A shared structure/label can map to both species; retain ambiguity. Species uses ChEMBL assay organism/taxonomy, never target magnitude. Secondary exact molecule-ID plus numeric-value matching is explicitly separate and never upgrades the strict structural matches.'}, evidence, repeated


def microsome_audit(tdc, chembl):
    ci, ti = index_by(chembl), index_by(tdc)
    cid, cparent = index_by(chembl, 'raw_identifier'), index_by(chembl, 'parent_molecule_chembl_id')
    secondary = []
    evidence, matched_activity_ids = [], set()
    tdc_agree = tdc_disagree = tdc_unmatched = 0
    censor_counts = defaultdict(Counter)
    for t in tdc:
        candidates = ci.get(t['canonical_smiles_rdkit'], [])
        id_candidates = cid.get(t['raw_identifier'], [])
        parent_candidates = cparent.get(t['raw_identifier'], [])
        if not candidates:
            secondary.append({'tdc_id': t['raw_identifier'], 'tdc_canonical_smiles_rdkit': t['canonical_smiles_rdkit'], 'tdc_value': t['raw_target'],
                              'exact_id_candidates': [{**ref(c), 'canonical_smiles_rdkit': c['canonical_smiles_rdkit'], 'numeric_equal': numeric_equal(t['raw_target'], c['raw_target'])} for c in id_candidates],
                              'chembl_declared_parent_id_candidates': [{**ref(c), 'parent_molecule_chembl_id': c.get('parent_molecule_chembl_id'), 'canonical_smiles_rdkit': c['canonical_smiles_rdkit'], 'numeric_equal': numeric_equal(t['raw_target'], c['raw_target'])} for c in parent_candidates]})
        if not candidates:
            tdc_unmatched += 1
        elif any(numeric_equal(t['raw_target'], c['raw_target']) for c in candidates):
            tdc_agree += 1
        else:
            tdc_disagree += 1
        for c in candidates or [None]:
            equal = numeric_equal(t['raw_target'], c['raw_target']) if c else False
            if c:
                matched_activity_ids.add(c['activity_id'])
                relation = 'UNKNOWN' if missing(c['standard_relation']) else str(c['standard_relation'])
                censor_counts[relation]['candidate_pairs'] += 1
                censor_counts[relation]['numeric_equal_pairs'] += equal
                censor_counts[relation]['tdc_inequality_present_pairs'] += t['measurement_audit']['relation'] in ('<', '>', '<=', '>=')
            evidence.append({'evidence_label': 'OBSERVED', 'tdc_row': t['source_row_1based'], 'tdc_id': t['raw_identifier'],
                             'tdc_raw_smiles': t['raw_smiles'], 'tdc_y': t['raw_target'], 'canonical_smiles_rdkit': t['canonical_smiles_rdkit'],
                             'chembl_activity_id': c['activity_id'] if c else None, 'chembl_molecule_id': c['raw_identifier'] if c else None,
                             'chembl_standard_value': c['raw_target'] if c else None, 'chembl_standard_relation': c['standard_relation'] if c else None,
                             'chembl_standard_units': c['standard_units'] if c else None, 'chembl_original_value': c['value'] if c else None,
                             'chembl_original_relation': c['relation'] if c else None, 'chembl_original_units': c['units'] if c else None,
                             'numeric_equal': equal if c else None, 'id_equal': t['raw_identifier'] == c['raw_identifier'] if c else None,
                             'candidate_count': len(candidates), 'match_status': 'MATCHED' if c else 'TDC_UNMATCHED',
                             'secondary_exact_id_candidates': [{**ref(x), 'canonical_smiles_rdkit': x['canonical_smiles_rdkit']} for x in id_candidates],
                             'secondary_parent_id_candidates': [{**ref(x), 'canonical_smiles_rdkit': x['canonical_smiles_rdkit']} for x in parent_candidates]})
    for c in chembl:
        if c['activity_id'] not in matched_activity_ids:
            evidence.append({'evidence_label': 'OBSERVED', 'match_status': 'CHEMBL_UNMATCHED', 'canonical_smiles_rdkit': c['canonical_smiles_rdkit'],
                             'chembl_activity_id': c['activity_id'], 'chembl_molecule_id': c['raw_identifier'], 'chembl_standard_value': c['raw_target'],
                             'chembl_standard_relation': c['standard_relation'], 'chembl_standard_units': c['standard_units'],
                             'chembl_original_value': c['value'], 'chembl_original_relation': c['relation'], 'chembl_original_units': c['units']})
    return {'OBSERVED': {'structure_overlap': len(set(ci) & set(ti)), 'tdc_only_structures': len(set(ti)-set(ci)),
                         'chembl_only_structures': len(set(ci)-set(ti)), 'tdc_rows_with_exact_numeric_match': tdc_agree,
                         'tdc_rows_structure_matched_without_numeric_match': tdc_disagree, 'tdc_unmatched_rows': tdc_unmatched,
                         'chembl_unmatched_rows': len(chembl)-len(matched_activity_ids), 'tdc_rows_with_multiple_candidates': sum(len(ci.get(t['canonical_smiles_rdkit'], [])) > 1 for t in tdc),
                         'qualifier_reconciliation_candidate_pairs': {k: dict(v) for k, v in sorted(censor_counts.items())},
                         'original_to_standard_numeric_equal_rows': sum(numeric_equal(c['value'], c['standard_value']) for c in chembl),
                         'chembl_standard_units': dict(Counter(c['standard_units'] for c in chembl)), 'chembl_original_units': dict(Counter(c['units'] for c in chembl)),
                         'tdc_raw_unit_column': None},
            'INFERRED': 'mL/min/g and microL/min/mg are dimensionally and numerically equivalent (unit conversion in numerator and denominator cancels). Exact numeric matches require no target transformation; retained boundary numbers without inequality strings indicate censor information is absent from the TDC table. This is not physiological scaling.',
            'secondary_id_audit': {'OBSERVED': {'exact_id_overlap': len(set(cid) & {t['raw_identifier'] for t in tdc}),
                                   'tdc_rows_with_exact_id_and_numeric_match': sum(any(numeric_equal(t['raw_target'], c['raw_target']) for c in cid.get(t['raw_identifier'], [])) for t in tdc),
                                   'strict_structure_unmatched_details': secondary},
                                  'INFERRED': 'ID and declared parent-ID evidence can explain representation discrepancies but does not establish strict structure equality. No fragments or tautomers were transformed.'},
            'UNRESOLVED': 'The TDC table has no units or censoring field. Numeric agreement supports, but cannot independently establish, source lineage or unit annotation. No claim about undocumented historical processing is made.'}, evidence


def paired_audit(hlm, hh):
    mi, hi = index_by(hlm), index_by(hh)
    mid, hid = index_by(hlm, 'raw_identifier'), index_by(hh, 'raw_identifier')
    keys, ids = sorted(set(mi)&set(hi)), sorted(set(mid)&set(hid))
    rows = []
    for key in keys:
        mids, hids = sorted({r['raw_identifier'] for r in mi[key]}), sorted({r['raw_identifier'] for r in hi[key]})
        rows.append({'evidence_label': 'OBSERVED', 'canonical_smiles_rdkit': key, 'hlm_molecule_ids': mids, 'hh_molecule_ids': hids,
                     'hlm_activity_ids': [r['activity_id'] for r in mi[key]], 'hh_activity_ids': [r['activity_id'] for r in hi[key]],
                     'shares_molecule_id': bool(set(mids)&set(hids)), 'multiple_rows_or_ids': len(mi[key]) > 1 or len(hi[key]) > 1})
    id_cases = []
    for ident in ids:
        a = {r['canonical_smiles_rdkit'] for r in mid[ident] if r['canonical_smiles_rdkit']}
        b = {r['canonical_smiles_rdkit'] for r in hid[ident] if r['canonical_smiles_rdkit']}
        if a != b or len(a) != 1 or len(b) != 1:
            id_cases.append({'molecule_id': ident, 'hlm_keys': sorted(a), 'hh_keys': sorted(b), 'shared_valid_key': bool(a&b)})
    summary = {'OBSERVED': {'id_overlap_n': len(ids), 'canonical_structure_overlap_n': len(keys),
                            'shared_ids': ids, 'id_structure_disagreement_or_ambiguity': id_cases,
                            'shared_structures_without_shared_id': sum(not r['shares_molecule_id'] for r in rows),
                            'shared_structures_with_multiple_rows_or_ids': sum(r['multiple_rows_or_ids'] for r in rows)},
               'INFERRED': 'This establishes membership only under two identity definitions. It does not establish matched experimental conditions or independent biological replicates.',
               'UNRESOLVED': 'Any repeated activities remain unresolved replicates; no aggregation or label selection occurs. No clearance ratio, difference, scaling, correlation or model is calculated.'}
    return summary, rows


def markdown_json(title, obj):
    return f'# {title}\n\n```json\n' + json.dumps(obj, indent=2, sort_keys=True) + '\n```\n'


def write_outputs(outputs):
    """Preflight every existing output before creating any audit artifact."""
    for relative, content in outputs.items():
        path = ROOT / relative
        if path.exists() and path.read_bytes() != content:
            raise ValueError(f'Audit output changed: {relative}; archive/amend explicitly before rerun')
    for relative, content in outputs.items():
        immutable(ROOT / relative, content)


def audit():
    if rdBase.rdkitVersion != '2025.03.6' or np.__version__ != '2.2.6':
        raise ValueError('Audit identity/statistics dependency version changed; explicit amendment required')
    manifest = read_json(ROOT / 'manifests/source_manifest.json')
    for item in manifest['sources']:
        verify(item)
    datasets, assays = load_sources()
    summaries = {name: source_summary(rows) for name, rows in datasets.items()}
    assay_audits = {}
    for name in (HLM, RAT, HH):
        rows = datasets[name]
        assay_audits[name] = {'OBSERVED': {'metadata': assays[name], 'activities': len(rows),
                             'standard_relations': relations(rows, 'standard_relation', 'standard_value'),
                             'original_relations': relations(rows, 'relation', 'value'),
                             'standard_units': dict(Counter(r.get('standard_units') for r in rows)),
                             'original_units': dict(Counter(r.get('units') for r in rows)),
                             'missing_standard_relation_rows': sum(missing(r.get('standard_relation')) for r in rows),
                             'data_validity_comments': dict(Counter(str(r.get('data_validity_comment')) for r in rows)),
                             'potential_duplicate_flags': dict(Counter(str(r.get('potential_duplicate')) for r in rows))},
                             'EXPECTED_FROM_MEMO': {'activities': EXPECTED[name], 'provenance': 'Expected counts explicitly supplied in the task; the frozen memo itself contains no numeric counts.'}}
    species, species_rows, repeats = species_audit(datasets[TH], datasets[RAT], datasets[HH])
    microsome, micro_rows = microsome_audit(datasets[TM], datasets[HLM])
    paired, paired_rows = paired_audit(datasets[HLM], datasets[HH])
    b = summaries[BIO]
    biogen = {'OBSERVED': {'total_rows': b['row_count'], 'unique_internal_ids': b['unique_identifiers'],
                          'exact_hlm_column': HLM_COLUMN, 'non_null_hlm_n': sum(not missing(r['raw_target']) for r in datasets[BIO]),
                          'missing_hlm_n': b['target_distribution']['missing_rows'], 'structure_and_target_audit': b,
                          'upstream_readme': 'data/raw/biogen/README.md explicitly describes experimental log(properties).'},
              'INFERRED': 'Repeated exact values at distribution boundaries are pile-ups consistent with reporting/assay limits; they alone do not prove censoring. Undefined stereochemistry means RDKit-detectable potential stereo elements without specified configuration, not demonstrated sample composition.',
              'UNRESOLVED': 'CSV supplies no per-row HLM censor relation. Log base and derivation of bodyweight-normalized source labels are not established by the downloaded CSV/README. No log/inverse-log, scaling or numerical comparison with AstraZeneca has been performed.'}
    report = {'OBSERVED': {'datasets': summaries, 'chembl_release': read_json(ROOT / 'data/raw/chembl/status.json'),
                           'environment': {'python': sys.version, 'platform': platform.platform(), 'rdkit': rdBase.rdkitVersion, 'numpy': np.__version__, 'PyTDC_registry_version': '1.1.15', 'PyTDC_installed': False},
                           'frozen_memo': record(ROOT / 'docs/DATASET_SELECTION_MEMO.md'),
                           'raw_input_hashes_verified': len(manifest['sources'])},
              'EXPECTED_FROM_MEMO': {'frozen_selection': 'Direct ChEMBL primary; TDC benchmark only; TDC hepatocyte excluded; Biogen within-dataset replication; no HLM/HH physiological scaling.', 'activity_counts_from_user_task': EXPECTED},
              'INFERRED': {'identity_definition': IDENTITY, 'statistics': 'Row-weighted descriptive statistics; numpy linear quantiles, IQR Q75-Q25, MAD median absolute deviation. Source labels unchanged; numeric summaries of censored records describe reported boundaries, not latent true clearance. No outlier removal. Descriptor missingness preserves source rows.'},
              'UNRESOLVED': ['ChEMBL live API release may differ from historical TDC release; no historical ChEMBL release asserted.',
                             'Null ChEMBL standard/original relations remain UNKNOWN; none are recoded to explicit equals. Numeric source values without qualifiers are not asserted to be uncensored observations.',
                             'Rat assay strain metadata contains CD1, BC, CD1, NMRI, SCID, or Nd. Species classification follows explicit assay organism Rattus norvegicus/taxonomy 10116 and description; the strain annotation requires source-level review.',
                             'Identity matching does not resolve unspecified stereochemistry, tautomer differences or sample provenance.',
                             'TDC has numeric targets without native unit/censor fields; absent qualifiers are not evidence of exact uncensored measurements.'],
              'chembl_assay_audits': assay_audits, 'tdc_hepatocyte_species_audit': species,
              'tdc_microsome_reconciliation': microsome, 'paired_human_cohort': paired, 'biogen_audit': biogen}
    outputs = {}
    def put(path, value):
        outputs[path] = json_bytes(value) if isinstance(value, (dict, list)) else value.encode('utf-8') if isinstance(value, str) else value
    put('reports/DATA_AUDIT.json', report)
    put('reports/CHEMBL_TDC_MICROSOME_RECONCILIATION.csv', csv_bytes(micro_rows))
    put('reports/PROVENANCE_TABLE.csv', csv_bytes([{'evidence_label': 'OBSERVED', **r} for r in manifest['sources']]))
    put('data/interim/TDC_HEPATOCYTE_SPECIES_ROWS.csv', csv_bytes(species_rows))
    put('data/interim/TDC_HEPATOCYTE_DUPLICATE_LABELS.json', {'OBSERVED': repeats})
    put('data/interim/PAIRED_HUMAN_COHORT.csv', csv_bytes(paired_rows))
    for name, rows in datasets.items():
        put(f'data/interim/{name}_rows.csv', csv_bytes(rows))
    anomalies = [{'source': name, **ref(r), 'raw_smiles': r['raw_smiles'], 'structure_status': r['structure_status'], 'structure_error': r['structure_error']}
                 for name, rows in datasets.items() for r in rows if r['structure_status'] != 'VALID']
    put('data/interim/STRUCTURE_ANOMALIES.json', {'OBSERVED': anomalies})
    duplicate_rows = []
    for name, rows in datasets.items():
        for key, members in sorted(index_by(rows).items()):
            if len(members) > 1:
                duplicate_rows.append({'source': name, 'canonical_smiles_rdkit': key, 'members': [ref(r) for r in members]})
    put('data/interim/DUPLICATE_STRUCTURES.json', {'OBSERVED': duplicate_rows})
    put('reports/PAIRED_HUMAN_COHORT_AUDIT.md', markdown_json('Paired human cohort audit', paired) + '\nOBSERVED: Complete membership evidence: `../data/interim/PAIRED_HUMAN_COHORT.csv`. No clearance labels are included in that membership table.\n')
    put('reports/TDC_HEPATOCYTE_SPECIES_AUDIT.md', markdown_json('TDC hepatocyte species audit', species) + '\nINFERRED: Identity rule: ' + IDENTITY + '\n\nOBSERVED: Row evidence is in `../data/interim/TDC_HEPATOCYTE_SPECIES_ROWS.csv`; repeated-structure evidence is in `../data/interim/TDC_HEPATOCYTE_DUPLICATE_LABELS.json`. Numeric matching retains source censor relations and does not assign species from label magnitude.\n')
    put('reports/BIOGEN_AUDIT.md', markdown_json('Biogen HLM audit', biogen))
    lines = ['# Frozen-source data audit', '', 'OBSERVED: Acquisition and forensic characterisation only. No modelling or scientific preprocessing was executed.', '',
             '## Counts', '', '| Source | Rows | Unique IDs | Unique raw SMILES | Unique RDKit structures | Missing / invalid | Duplicate groups / excess rows |', '|---|---:|---:|---:|---:|---:|---:|']
    for name, s in summaries.items():
        lines.append(f"| OBSERVED: {name} | {s['row_count']} | {s['unique_identifiers']} | {s['unique_raw_smiles']} | {s['unique_valid_structures']} | {s['missing_structure_rows']} / {s['invalid_structure_rows']} | {s['duplicated_structure_groups']} / {s['excess_duplicate_rows']} |")
    lines += ['', 'EXPECTED_FROM_MEMO: Task-supplied expected assay counts are 1102 (3301370), 837 (3301371), 408 (3301372). The memo freezes selection but contains no numeric counts.', '', '## ChEMBL relations', '', '| Assay | < | > | = | Anything else |', '|---|---:|---:|---:|---:|']
    for name, a in assay_audits.items():
        c = a['OBSERVED']['standard_relations']['counts']
        lines.append(f"| OBSERVED: {name} | {c['<']} | {c['>']} | {c['=']} | {c['anything_else']} |")
    for name, a in assay_audits.items():
        bounds = {k:v for k,v in a['OBSERVED']['standard_relations']['reported_values_by_relation'].items() if k != '='}
        lines += ['', f'OBSERVED: {name} censored/other reported boundaries: `{json.dumps(bounds, sort_keys=True)}`.']
    lines += ['', '### Null-relation records at numeric boundaries', '',
              '| Assay | Null relation at 3 | Null relation at 150 |', '|---|---:|---:|']
    for name in (HLM, RAT, HH):
        null_rows = [r for r in datasets[name] if r.get('standard_relation') is None]
        counts = [sum(numeric_equal(r['raw_target'], value) for r in null_rows) for value in ('3', '150')]
        lines.append(f'| {name} | {counts[0]} | {counts[1]} |')
    lines += ['', 'OBSERVED: Rat-assay null-relation records at 3: ' + '; '.join(
        f"activity {r['activity_id']}, {r['raw_identifier']}, value {r['raw_target']}"
        for r in datasets[RAT] if r.get('standard_relation') is None and numeric_equal(r['raw_target'], '3')) +
        '. These remain UNKNOWN; boundary equality does not assign a censor relation.', '']
    lines += ['', '## TDC target audit', '', 'OBSERVED: Raw columns are ID, X, Y; Drug_ID in the requested audit means ID, raw SMILES means X. Both tables were downloaded directly using the verified PyTDC 1.1.15 source registry. PyTDC itself was not installed or invoked.', '']
    lines += ['OBSERVED: The [TDC public documentation](https://tdcommons.ai/single_pred_tasks/adme/#clearance-astrazeneca), accessed 2026-09-16, reports 1,020 hepatocyte drugs. The downloaded table has 1,213 rows and 1,020 unique IDs/structures. These are distinct denominators; no raw deduplication was applied.', '',
              'OBSERVED: The preserved PyTDC 1.1.15 loader source uses raw X/Y/ID and filters null targets. This audit reads the raw table directly, retaining even missing-target rows. Both acquired TDC tables have no missing targets.', '']
    for name in (TM, TH):
        lines += [f'### {name}', '', 'OBSERVED:', '```json', json.dumps(summaries[name]['target_distribution'], indent=2), '```', '']
    lines += ['## Species and microsome reconciliation', '', markdown_json('TDC hepatocyte summary', species),
              'OBSERVED: The six non-strict hepatocyte duplicate groups have no strict structural match to either source assay under the frozen identity rule; all twelve rows are classified as neither. They are not groups with ambiguous matching species evidence.', '',
              markdown_json('TDC microsome summary', microsome),
              '### Five strict microsome structure discrepancies', '',
              '| TDC molecule ID | ChEMBL molecule ID | Representation discrepancy | Matching numeric value | Standard InChIKeys |',
              '|---|---|---|---:|---|',
              '| CHEMBL82663 | CHEMBL82663 | Hydroxythiazole / thiazolone tautomer spellings | 111.0 | Equal |',
              '| CHEMBL1483 | CHEMBL1483 | Heterocyclic N-H tautomer spellings | 34.67 | Equal |',
              '| CHEMBL412142 | CHEMBL412142 | Imidazole N-H tautomer spellings | 96.0 | Equal |',
              '| CHEMBL1513 | CHEMBL1513 | Tetrazole N-H tautomer spellings | 17.78 | Equal |',
              '| CHEMBL190 | CHEMBL1355736 (declared parent CHEMBL190) | Theophylline / hydrate with a disconnected O component | 4.79 | Different |', '',
              'OBSERVED: The independent review confirmed matching molecule IDs, values and standard InChIKeys for the four tautomer cases. Standard InChIKey agreement is supporting evidence only; it does not replace the frozen canonical-SMILES identity rule. The hydrate pair has a matching value. All five remain strict mismatches; the strict match count remains 1,097. Full canonical strings and activity references are retained above and in the reconciliation CSV. See AUDIT_REVIEW.md for the preserved independent review.', '',
              '## Paired human cohort', '', markdown_json('Membership summary', paired), '## Biogen', '',
              f"OBSERVED: {b['row_count']} rows; exact non-null HLM N = {biogen['OBSERVED']['non_null_hlm_n']}; column `{HLM_COLUMN}`. See BIOGEN_AUDIT.md for independent descriptive results; no numerical cross-dataset comparison is made.", '',
              '## Chemical-space audit', '', 'INFERRED: ' + IDENTITY, '',
              'INFERRED: Descriptors use RDKit MolWt (g/mol), Wildman-Crippen MolLogP, CalcTPSA (A^2), Lipinski NumHDonors/NumHAcceptors, strict CalcNumRotatableBonds, CalcFractionCSP3. Every valid source row is characterised, including duplicates and rows with missing targets. No outliers are removed.', '',
              '| Source / property | Numeric N | Min | Q05 | Q25 | Median | Q75 | Q95 | Max | IQR | MAD |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name, summary in summaries.items():
        for prop, d in summary['chemical_space'].items():
            lines.append('| OBSERVED: ' + name + ' / ' + prop + ' | ' + str(d['numeric_rows']) + ' | ' + ' | '.join(f'{d[k]:.6g}' for k in ('min','q05','q25','median','q75','q95','max','iqr','mad')) + ' |')
    lines += ['', '## Uncertainty and provenance', ''] + ['UNRESOLVED: ' + s + '\n' for s in report['UNRESOLVED']]
    lines += ['OBSERVED: Full machine-readable results are DATA_AUDIT.json. All six complete enriched row tables, structure anomalies and duplicate groups are under data/interim. Raw files and receipt hashes are in manifests/source_manifest.json and PROVENANCE_TABLE.csv. Execution logs include failures with actual errors.', '',
              'OBSERVED: Initial reports were explicitly archived under reports/revisions/initial-audit with original hashes and a code snapshot before adding secondary ID/parent-ID reconciliation. Strict structural identity and all raw inputs are unchanged.', '',
              'INFERRED: Native ChEMBL source numeric boundary distributions are descriptive, not estimates of uncensored clearance. Raw TDC and Biogen numeric labels do not encode absent censor metadata. Missing metadata remains unknown.', '',
              'OBSERVED: Acquisition initially failed only while generating the manifest because the ChEMBL status activities field is an integer. All raw downloads were retained; a list-type check fixed manifest generation and acquisition was rerun using the same bytes. No failed computation was replaced by a mock result.', '']
    put('reports/DATA_AUDIT.md', '\n'.join(lines))
    write_outputs(outputs)
    print(json.dumps({'OBSERVED': {k: {p: v for p,v in s.items() if p in ('row_count','unique_identifiers','unique_valid_structures','invalid_structure_rows','duplicated_structure_groups','excess_duplicate_rows')} for k,s in summaries.items()}, 'species': species, 'microsome': microsome, 'paired': paired['OBSERVED'], 'biogen_non_null_hlm': biogen['OBSERVED']['non_null_hlm_n']}, indent=2))
