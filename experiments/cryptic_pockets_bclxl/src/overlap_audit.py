"""Audit identifiers in saved public source text and dataset lists; no detectors."""
import json
import re
from provenance import ROOT, file_record, now, write_json


def audit():
    base = ROOT / 'manifests/source_review'
    pattern = re.compile(r'1lxl|2yxj|bcl[-_ ]?xl|bcl-x\b|q07817', re.I)
    lacuna_hits, p2rank_hits = [], []
    evidence = []
    for directory, output in [('lacuna', lacuna_hits), ('p2rank-datasets', p2rank_hits), ('p2rank', p2rank_hits)]:
        for path in sorted((base / directory).rglob('*')):
            if not path.is_file() or path.name.endswith('tree.json'):
                continue
            evidence.append(file_record(path))
            for line_no, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
                if pattern.search(line):
                    output.append({'file': path.relative_to(ROOT).as_posix(), 'line': line_no, 'text': line})
    folds_path = base / 'cryptobench/folds.json'
    folds = json.loads(folds_path.read_text())
    fold_matches = {pdb: [fold for fold, ids in folds.items() if pdb.lower() in {p.lower() for p in ids}]
                    for pdb in ('1LXL', '2YXJ')}
    evidence.append(file_record(folds_path))
    ds_files = sorted((base / 'p2rank-datasets').glob('*.ds'))
    result = {
        'schema_version': 1, 'audited_at': now(), 'query_identifiers': ['1LXL', '2YXJ', 'BCL-XL', 'BCLXL', 'Q07817'],
        'definitions': {
            'EXAMPLE_OVERLAP': 'Explicit same system/identifiers in documentation/showcase.',
            'BENCHMARK_OVERLAP': 'Explicit same system/identifiers in evaluation target definitions.',
            'TRAINING_OVERLAP': 'Direct evidence of inclusion in fitting data; never inferred from examples.',
            'NO_EVIDENCE_OF_TRAINING_OVERLAP': 'No positive evidence within the stated audited scope; not proof of absence.',
            'UNKNOWN': 'Insufficient coverage to resolve target-level/homology or exact artifact provenance.'},
        'lacuna': {
            'source_commit': '960523caa75c86f04111970da47c3c06ceeda8b4', 'source_package_version': '1.2.0',
            'example_status': 'EXAMPLE_OVERLAP', 'benchmark_status': 'BENCHMARK_OVERLAP',
            'training_evidence_status': 'NO_EVIDENCE_OF_TRAINING_OVERLAP', 'training_overlap_status': 'UNKNOWN',
            'matches': lacuna_hits, 'cryptobench_exact_id_fold_membership': fold_matches,
            'fit_evidence': [
                {'file': 'benchmarks/train_ranker.py', 'finding': 'Uses CryptoBench train-0..train-3 folds for learned ranker; designated test fold evaluated separately.'},
                {'file': 'analysis/moores_pocket_law/train_surface_detector.py', 'finding': 'Selects only CryptoBench train folds for fitted surface models.'}],
            'limitations': ['Neither identifier occurs in downloaded CryptoBench fold lists; alternate structures of BCL-XL or homologs were not sequence-audited.',
                            'Exact row-to-shipped-artifact membership for all learned/fused models not independently reconstructed.',
                            'Documentation and benchmark appearance establish prior exposure, not training leakage.',
                            'Published showcase backend, seed, preprocessing and sequence-feature availability are not specified beside the result.']},
        'p2rank': {
            'source_version': '2.5.1', 'source_commit': '9808a7723be9a94e2ffc21ab5f724cb6ae4ba01e',
            'dataset_source_commit': json.loads((base / 'supplementary_manifest.json').read_text())['dataset_repository_commit'],
            'example_status': 'UNKNOWN', 'benchmark_status': 'UNKNOWN',
            'training_evidence_status': 'NO_EVIDENCE_OF_TRAINING_OVERLAP', 'training_overlap_status': 'UNKNOWN',
            'matches': p2rank_hits, 'dataset_lists_searched': [p.name for p in ds_files],
            'documented_training': 'CHEN11 training, JOINED development; exact identifiers absent from downloaded root membership lists, including chen11.ds and joined.ds.',
            'publications': ['https://pmc.ncbi.nlm.nih.gov/articles/PMC6091426/',
                             'https://academic.oup.com/nar/article/50/W1/W593/6591527'],
            'limitations': ['No accession/homology audit of every training structure, so same-target overlap remains UNKNOWN.',
                            'Source recursive dataset-tree query was truncated and FAILED; successful follow-up audited root .ds membership lists, not every structure file.',
                            'No claim that absence of exact PDB identifiers guarantees independent generalisation.']},
        'evidence_files': evidence,
        'conclusion': 'Reproduction/pipeline validation only. No demonstrated training overlap, and no clean external-validation claim.'}
    if any(fold_matches.values()):
        raise ValueError('Unexpected exact-ID fold overlap; revise evidence classification before preregistration')
    if p2rank_hits:
        raise ValueError('P2Rank exact/system match requires manual evidence classification before preregistration')
    path = ROOT / 'manifests/benchmark_overlap_audit.json'
    if path.exists():
        result['audited_at'] = json.loads(path.read_text())['audited_at']
    write_json(path, result)
    print('Lacuna: EXAMPLE_OVERLAP, BENCHMARK_OVERLAP; training UNKNOWN (no positive evidence).')
    print('P2Rank: no exact/system matches in', len(ds_files), 'root dataset lists; target-level training UNKNOWN.')
    return [path]
