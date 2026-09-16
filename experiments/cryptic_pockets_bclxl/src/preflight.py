"""Verify local preregistration artifacts and absence of method execution evidence."""
import importlib.metadata
import json
from provenance import ROOT, file_record, now, verify_record, write_json


def check():
    outputs = []
    for name, field in [('input_manifest.json', 'structures')]:
        for record in json.loads((ROOT / 'manifests' / name).read_text())[field]:
            verify_record(record)
    core = json.loads((ROOT / 'data/processed/matched_core_manifest.json').read_text())
    for record in core['raw_inputs'] + core['processed_outputs']:
        verify_record(record)
    runs = []
    allowed = {'acquire', 'environment', 'inspect', 'evaluate', 'test', 'verify', 'source-review',
               'source-review-extra', 'overlap-audit', 'matched-core', 'archive-pre-review',
               'archive-core-v0', 'apply-amendment', 'preflight'}
    for path in sorted((ROOT / 'manifests/runs').glob('*.json')):
        r = json.loads(path.read_text(encoding='utf-8-sig'))
        if path.name.endswith('.started.json') or path.name.startswith('bootstrap-'):
            continue
        if r['action'] not in allowed:
            raise ValueError(f'Unexpected execution action: {r["action"]}')
        runs.append({'file': path.relative_to(ROOT).as_posix(), 'action': r['action'], 'status': r['status']})
    # Source snapshots can mention outputs, but do not contain our scientific results.
    forbidden = []
    for directory in ('results', 'data/processed'):
        for path in (ROOT / directory).rglob('*'):
            if not path.is_file():
                continue
            if (path.name == 'pocket_report.json' or path.name.endswith(('_predictions.csv', '_residues.csv'))
                    or (path.name.startswith('pocket_') and path.suffix in ('.pdb', '.yaml', '.conf'))):
                forbidden.append(path.relative_to(ROOT).as_posix())
    if forbidden:
        raise ValueError(f'Detector output files found: {forbidden}')
    installed = {d.metadata['Name'].lower() for d in importlib.metadata.distributions()}
    if installed & {'lacuna-pockets', 'boltz', 'openmm', 'torch'}:
        raise ValueError('Unexpected method/backend installed in parser environment')
    reports = sorted((ROOT / 'results').glob('tests-*.json'))
    if not reports:
        raise ValueError('No complete test report')
    latest = json.loads(reports[-1].read_text())
    if latest['status'] != 'SUCCESS' or latest['failures'] or latest['errors'] or latest['skipped']:
        raise ValueError('Latest complete tests did not all pass')
    report = {'checked_at': now(), 'status': 'SUCCESS', 'raw_and_processed_hashes_verified': True,
              'detector_output_files_found': forbidden,
              'detector_execution_status': 'No detector invocation in experiment receipts; no invocation by this agent; user pre-review states none occurred.',
              'scope_limitation': 'This is an experiment-directory/log audit, not a forensic claim about arbitrary external processes.',
              'test_report': file_record(reports[-1]), 'test_counts': latest,
              'reviewed_execution_receipts': runs, 'matched_core_counts': core['counts'],
              'scientific_inputs': core['processed_outputs'],
              'git_anchor_policy': 'Stage only experiments/cryptic_pockets_bclxl after tests; no existing staged changes may be included.'}
    path = ROOT / 'manifests' / ('preflight-' + now().replace(':', '').replace('.', '').replace('+', '_') + '.json')
    write_json(path, report)
    print('PREFLIGHT SUCCESS:', latest['passed'], 'tests passed; no detector result files or recorded executions.')
    return [path]
