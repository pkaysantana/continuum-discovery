"""Read-only integrity checks plus a new timestamped checkpoint receipt."""
import csv
import json
import subprocess
from pathlib import Path
from provenance import ROOT, digest, record, save_json, utc, verify


def verify_checkpoint():
    manifest = json.loads((ROOT / 'manifests/source_manifest.json').read_text())
    listed = {r['filename'] for r in manifest['sources']}
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'data/raw').rglob('*') if p.is_file()}
    if actual != listed:
        raise ValueError('Raw inventory differs from manifest')
    for item in manifest['sources']:
        verify(item)
    memo = ROOT / 'docs/DATASET_SELECTION_MEMO.md'
    frozen_bytes = subprocess.check_output(['git','show','9724c17:experiments/compound_to_exposure/docs/DATASET_SELECTION_MEMO.md'])
    if memo.read_bytes() != frozen_bytes:
        raise ValueError('Frozen memo changed')
    required = ['DATA_AUDIT.md','DATA_AUDIT.json','PROVENANCE_TABLE.csv','CHEMBL_TDC_MICROSOME_RECONCILIATION.csv',
                'PAIRED_HUMAN_COHORT_AUDIT.md','TDC_HEPATOCYTE_SPECIES_AUDIT.md','BIOGEN_AUDIT.md']
    for name in required:
        if not (ROOT / 'reports' / name).is_file():
            raise ValueError('Required report missing: ' + name)
    report = json.loads((ROOT / 'reports/DATA_AUDIT.json').read_text())
    for name, summary in report['OBSERVED']['datasets'].items():
        path = ROOT / f'data/interim/{name}_rows.csv'
        with path.open(encoding='utf-8', newline='') as f:
            count = sum(1 for _ in csv.DictReader(f))
        if count != summary['row_count']:
            raise ValueError('Row preservation failed: ' + name)
    audit_runs = []
    for path in (ROOT / 'manifests/runs').glob('*.json'):
        r = json.loads(path.read_text())
        if r.get('action') == 'audit' and r.get('status') == 'SUCCESS' and any(x['filename'] == 'reports/DATA_AUDIT.json' for x in r['outputs']):
            audit_runs.append(r)
    if not audit_runs:
        raise ValueError('No successful report-generating audit execution')
    latest = max(audit_runs, key=lambda r:r['finished_utc'])
    for item in latest['outputs']:
        verify(item)
    test_runs = [json.loads(p.read_text()) for p in (ROOT / 'reports').glob('tests-*.json')]
    if not test_runs or not all(r['status'] == 'SUCCESS' for r in test_runs):
        raise ValueError('Missing or failed test run requires explicit review')
    result = {'status': 'SUCCESS', 'verified_utc': utc(), 'raw_files_verified': len(actual), 'memo': record(memo),
              'reports': [record(ROOT / 'reports' / name) for name in required], 'report_generating_audit_run': latest['run_id'],
              'test_results': test_runs, 'scope': 'Integrity checks only; no scientific data transformations.'}
    save_json(ROOT / 'manifests' / ('checkpoint-verification-' + result['verified_utc'].replace(':','').replace('.','').replace('+','_') + '.json'), result)
    print(json.dumps(result, indent=2))
