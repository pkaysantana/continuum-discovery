"""Logged acquisition/audit entry point. No modelling or physiological scaling."""
import contextlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import traceback
import unittest
import uuid
from provenance import ROOT, immutable, record, save_json, utc


def inventory():
    files = []
    for directory in ('src', 'tests', 'docs', 'data/raw', 'data/interim', 'manifests'):
        for path in (ROOT / directory).rglob('*'):
            if path.is_file() and 'runs' not in path.parts and '__pycache__' not in path.parts:
                files.append(record(path))
    return files


def bootstrap():
    base = sys.executable
    venv = ROOT / '.venv'
    if venv.exists():
        raise ValueError('Experiment environment already exists; use it or explicitly archive before rebuilding')
    subprocess.run([base, '-B', '-m', 'venv', str(venv)], check=True)
    executable = venv / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    env = {**os.environ, 'PIP_CACHE_DIR': str(ROOT / '.cache/pip'), 'TEMP': str(ROOT / 'reports/tmp'), 'TMP': str(ROOT / 'reports/tmp')}
    args = [str(executable), '-B', '-m', 'pip', 'install', '--disable-pip-version-check', '--report', str(ROOT / 'manifests/pip_install_report.json'),
            'rdkit==2025.3.6', 'numpy==2.2.6', 'Pillow==12.3.0']
    completed = subprocess.run(args, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print('Subcommand:', subprocess.list2cmdline(args)); print(completed.stdout)
    completed.check_returncode()


def tests(run_id):
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT / 'tests')))
    print(stream.getvalue())
    summary = {'run': result.testsRun, 'passed': result.testsRun-len(result.errors)-len(result.failures)-len(result.skipped),
               'failed': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
               'status': 'SUCCESS' if result.wasSuccessful() and result.testsRun else 'FAILED'}
    save_json(ROOT / f'reports/tests-{run_id}.json', summary)
    if not result.wasSuccessful() or not result.testsRun:
        raise RuntimeError('Complete audit test suite FAILED')


def main():
    for folder in ('data/raw', 'data/interim', 'manifests/runs', 'reports/tmp', 'src', 'tests'):
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    tempfile.tempdir = str(ROOT / 'reports/tmp')
    run_id = utc().replace(':', '').replace('.', '').replace('+', '_') + '-' + uuid.uuid4().hex[:8]
    action = sys.argv[1] if len(sys.argv) == 2 else 'INVALID'
    rec = {'run_id': run_id, 'status': 'RUNNING', 'started_utc': utc(), 'action': action,
           'command': [sys.executable, '-B', str(Path(__file__).resolve()), *sys.argv[1:]], 'inputs': inventory(),
           'python': sys.version, 'platform': platform.platform(),
           'repository_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    save_json(ROOT / f'manifests/runs/{run_id}.started.json', rec)
    start = time.perf_counter()
    log = io.StringIO(); code = 0
    before = {p: record(p) for d in ('data', 'reports', 'manifests') for p in (ROOT / d).rglob('*') if p.is_file()}
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        try:
            if action == 'bootstrap':
                bootstrap()
            elif action == 'acquire':
                from acquire import acquire_all
                acquire_all()
            elif action == 'audit':
                from audit import audit
                audit()
            elif action == 'test':
                tests(run_id)
            elif action == 'verify':
                from verify_checkpoint import verify_checkpoint
                verify_checkpoint()
            elif action == 'archive_initial_reports':
                from provenance import digest
                names = ['reports/DATA_AUDIT.json', 'reports/DATA_AUDIT.md',
                         'reports/CHEMBL_TDC_MICROSOME_RECONCILIATION.csv', 'reports/TDC_HEPATOCYTE_SPECIES_AUDIT.md',
                         'data/interim/TDC_HEPATOCYTE_SPECIES_ROWS.csv', 'data/interim/TDC_HEPATOCYTE_DUPLICATE_LABELS.json']
                archive = ROOT / 'reports/revisions/initial-audit'
                if archive.exists():
                    raise ValueError('Initial audit already archived; no repeat mutation')
                receipts = []
                for name in names:
                    path = ROOT / name
                    target = archive / name
                    if not path.resolve().is_relative_to(ROOT.resolve()) or not target.resolve().is_relative_to(ROOT.resolve()):
                        raise ValueError('Archive path outside experiment')
                    receipts.append(record(path))
                    immutable(target, path.read_bytes())
                    if digest(target) != digest(path):
                        raise ValueError('Archive verification failed')
                    path.unlink()
                immutable(archive / 'src/audit.py.snapshot', (ROOT / 'src/audit.py').read_bytes())
                save_json(archive / 'amendment.json', {'reason': 'Forensic follow-up: add explicit molecule-ID and parent-ID evidence for strict structure mismatches; clarify null ChEMBL relations and raw TDC row-count discrepancy. Identity rule, raw data and scientific selection unchanged.', 'archived_utc': utc(), 'original_files': receipts})
                print('Archived initial derived reports with verified hashes; raw files unchanged.')
            else:
                raise ValueError('Allowed actions: bootstrap, acquire, audit, test')
            rec['status'] = 'SUCCESS'
        except BaseException as e:
            rec['status'] = 'FAILED'; code = 1
            rec['error'] = {'type': type(e).__name__, 'message': str(e), 'traceback': traceback.format_exc()}
            traceback.print_exc()
    rec['finished_utc'] = utc(); rec['elapsed_seconds'] = time.perf_counter()-start
    logfile = ROOT / f'reports/{action}-{run_id}.log'
    immutable(logfile, log.getvalue().encode('utf-8'))
    rec['outputs'] = []
    for directory in ('data', 'reports', 'manifests'):
        for path in (ROOT / directory).rglob('*'):
            if path.is_file():
                item = record(path)
                if before.get(path) != item:
                    rec['outputs'].append(item)
    save_json(ROOT / f'manifests/runs/{run_id}.json', rec)
    print(log.getvalue()); print(rec['status'], action, run_id)
    return code


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    raise SystemExit(main())
