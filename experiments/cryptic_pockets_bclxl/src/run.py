"""Logged entry point. Allowed actions are exclusively benchmark Steps 1–5."""
from __future__ import annotations

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
import urllib.request
import uuid

from provenance import ROOT, canonical_bytes, file_record, now, sha256, verify_record, write_json, write_once

CONFIG = ROOT / 'configs/reference_site.json'
MANIFEST = ROOT / 'manifests/input_manifest.json'


def versions():
    packages = {}
    for p in ('biopython', 'numpy', 'scipy', 'click', 'rich', 'lacuna-pockets'):
        try:
            packages[p] = importlib.metadata.version(p)
        except importlib.metadata.PackageNotFoundError:
            packages[p] = 'NOT_INSTALLED'
    
    java_version = 'NOT_MEASURED'
    try:
        import subprocess, os
        java_exe = Path(os.getcwd()) / 'jdk-21.0.2' / 'bin' / 'java.exe'
        java_res = subprocess.run([str(java_exe), '-version'], capture_output=True, text=True, check=False)
        java_version = java_res.stderr.splitlines()[0] if java_res.stderr else 'NOT_FOUND'
    except Exception:
        pass
        
    return {'python': platform.python_version(),
            'java': java_version,
            'packages': packages}


def inputs():
    paths = list(ROOT.glob('*.md'))
    for directory, pattern in [('src', '*'), ('tests', '*.py'), ('configs', '*'),
                               ('data/raw', '*'), ('data/processed', '*')]:
        paths.extend(p for p in (ROOT / directory).glob(pattern) if p.is_file())
    paths.extend(p for p in (ROOT / 'manifests').glob('*.json') if p.is_file())
    paths.extend(p for p in (ROOT / 'manifests/source_review').rglob('*') if p.is_file())
    return [file_record(p) for p in sorted(set(paths)) if p.exists()]


def config():
    return json.loads(CONFIG.read_text(encoding='utf-8'))


def acquisition():
    from reference_site import load_cif, rows, scalar, sequence, ligand
    cfg = config()
    records, outputs = [], []
    for pdb_id in ('1LXL', '2YXJ'):
        target = ROOT / 'data/raw' / f'{pdb_id}.cif'
        receipt = ROOT / 'manifests' / f'acquisition_{pdb_id}.json'
        source = f'https://files.rcsb.org/download/{pdb_id}.cif'
        if target.exists():
            if not receipt.exists():
                raise ValueError(f'Raw input without acquisition receipt: {target}; manual review required')
            rec = json.loads(receipt.read_text(encoding='utf-8'))
            verify_record(rec)
            if rec['source_url'] != source or rec['pdb_id'] != pdb_id:
                raise ValueError('Acquisition receipt identity mismatch')
            print(f'Verified existing immutable input {pdb_id}')
        else:
            if receipt.exists():
                raise ValueError(f'Acquisition receipt exists but raw file is missing: {pdb_id}')
            request = urllib.request.Request(source, headers={'User-Agent': 'BCLXL-reference-benchmark/1.0'})
            with urllib.request.urlopen(request, timeout=60) as response:
                if response.status != 200 or response.geturl() != source:
                    raise ValueError('Unexpected source response or redirect; no fallback allowed')
                body = response.read()
                retrieved = now()
                headers = {key: response.headers.get(key) for key in ('ETag', 'Last-Modified', 'Content-Type')}
            if not body.lstrip().lower().startswith(f'data_{pdb_id.lower()}'.encode()):
                raise ValueError('Downloaded response is not expected mmCIF entry')
            write_once(target, body)
            rec = {'pdb_id': pdb_id, 'source_url': source, 'retrieved_at': retrieved,
                   'http_headers': headers, **file_record(target)}
            write_json(receipt, rec)
            print(f'Acquired {pdb_id}: {rec["byte_size"]} bytes, sha256 {rec["sha256"]}')
        outputs.extend([target, receipt])
        cif = load_cif(target)
        if scalar(cif, '_entry.id').upper() != pdb_id:
            raise ValueError('Archive entry ID mismatch')
        title = scalar(cif, '_struct.title')
        method = scalar(cif, '_exptl.method')
        entity, seq = sequence(cif, 'A')
        references = rows(cif, '_struct_ref')
        if not any(r.get('pdbx_db_accession') == 'Q07817' for r in references):
            raise ValueError(f'{pdb_id}: expected BCL-XL UniProt Q07817 annotation absent')
        if pdb_id == '1LXL':
            if method != 'SOLUTION NMR' or rows(cif, '_pdbx_entity_nonpoly'):
                raise ValueError('1LXL apo/NMR assignment not verified')
            ligand_identity = None
            caveats = ['Single minimized-average solution NMR model; not a trajectory or ensemble.',
                       'Ligand-free does not by itself establish a cryptic pocket.',
                       '221-residue construct differs from 2YXJ.']
        else:
            if method != 'X-RAY DIFFRACTION' or 'ABT-737' not in title:
                raise ValueError('2YXJ holo/ABT-737 assignment not verified')
            selected = ligand(cif, cfg)
            component = [r for r in rows(cif, '_chem_comp') if r['id'] == cfg['ligand_comp_id']]
            ligand_identity = {'common_name': 'ABT-737', 'component_id': 'N3C',
                               'component_metadata': component, 'selected_instance': selected['id'],
                               'heavy_atom_count': len(selected['atoms']),
                               'source_url': 'https://www.rcsb.org/ligand/N3C'}
            caveats = ['2.20 A crystal structure; method and packing differ from 1LXL.',
                       'Chains A and B with one N3C each; preregistered primary chain A / ligand D.',
                       '181-residue deposited construct with unresolved residues; numbering differs from label sequence IDs.',
                       'Glycerol, chloride and waters excluded; no symmetry mates added.']
        records.append({**rec, 'structure_title': title, 'experimental_method': method,
                        'selected_protein_chains': [{'label_chain': 'A', 'auth_chain': 'A', 'entity_id': entity}],
                        'model_number': cfg['model_number'], 'deposited_sequence_length_selected_chain': len(seq),
                        'polymer_entities': rows(cif, '_entity_poly'),
                        'nonpolymer_entities': rows(cif, '_pdbx_entity_nonpoly'),
                        'ligand_identity': ligand_identity, 'warnings': caveats,
                        'structure_page': f'https://www.rcsb.org/structure/{pdb_id}',
                        'database_references': references})
    write_json(MANIFEST, {'schema_version': 1, 'canonical_format': 'mmCIF',
                         'format_rationale': 'Retains polymer sequence, entities, label/auth numbering and missing-residue metadata.',
                         'structures': records})
    outputs.append(MANIFEST)
    return outputs


def environment():
    cpu, gpu = platform.processor(), {'status': 'unavailable', 'reason': 'Optional WMI query denied by sandbox (HRESULT 0x80041003). No GPU needed.'}
    if sys.platform == 'win32':
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
            cpu = winreg.QueryValueEx(key, 'ProcessorNameString')[0].strip()
    plan = {
        'schema_version': 1, 'captured_at': now(),
        'current': {'os': platform.platform(), 'python_executable': sys.executable,
                    **versions(), 'cpu': cpu, 'logical_cpu_count': os.cpu_count(), 'gpu': gpu},
        'planned': {
            'python': {'version': '3.11.16', 'requirement': '>=3.10 for Lacuna 1.1.0'},
            'biopython': {'version': '1.85', 'purpose': 'mmCIF dictionary parsing and sequence alignment'},
            'numpy': {'version': '2.2.6', 'purpose': 'deterministic geometric distances'},
            'pandas': {'requirement': '>=2.2,<3', 'status': 'optional later; exact lock required before installation'},
            'plotting': {'package': 'matplotlib', 'requirement': '>=3.9,<4', 'status': 'optional later; exact lock required before installation'},
            'lacuna': {'distribution': 'lacuna-pockets', 'version': '1.1.0',
                       'source_commit': '3ea5633137d53f80ac61120212b9228dfd246ce9',
                       'backend': 'nma', 'backend_selection': 'explicit CPU nma; no auto backend switching',
                       'requirements': ['numpy>=1.24', 'scipy>=1.10', 'biopython>=1.81', 'click>=8.1', 'rich>=13.0'],
                       'extras': [], 'status': 'PLANNED_ONLY_NOT_INSTALLED_OR_RUN',
                       'sources': ['https://pypi.org/project/lacuna-pockets/1.1.0/',
                                   'https://github.com/mooreneural/lacuna/blob/3ea5633137d53f80ac61120212b9228dfd246ce9/pyproject.toml']},
            'static_baseline': {'name': 'P2Rank', 'version': '2.5.1', 'java_major': 17,
                                'status': 'PLANNED_ONLY_NOT_INSTALLED_OR_RUN',
                                'sources': ['https://github.com/rdk/p2rank/releases/tag/2.5.1',
                                            'https://github.com/rdk/p2rank/blob/2.5.1/README.md']}},
        'isolation': 'Experiment-local .venv and .cache. No historical environment modifications.',
        'future_execution': 'Human approval required. Freeze a complete dependency lock, software hashes, seeds, threads and invocation first.',
        'excluded_backends': ['boltz', 'openmm', 'plm'],
        'current_minimum_dependencies': ['biopython==1.85', 'numpy==2.2.6'],
        'sources_checked_date': '2026-09-16'}
    path = ROOT / 'manifests/environment_plan.json'
    if path.exists():
        old = json.loads(path.read_text(encoding='utf-8'))
        plan['captured_at'] = old['captured_at']
        plan['planned'] = old['planned']
        if 'review_amendment' in old:
            plan['review_amendment'] = old['review_amendment']
        path.unlink()
    write_json(path, plan)
    print(json.dumps(plan['current'], indent=2))
    return [path]


def verify_inputs():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if [r['pdb_id'] for r in manifest['structures']] != ['1LXL', '2YXJ']:
        raise ValueError('Unexpected benchmark input identifiers')
    return {r['pdb_id']: verify_record(r) for r in manifest['structures']}


def evaluation():
    from reference_site import evaluate, load_cif
    structures = verify_inputs()
    result = evaluate(load_cif(structures['2YXJ']), load_cif(structures['1LXL']), config())
    result['provenance'] = {'inputs': [file_record(p) for p in structures.values()],
                            'protocol_sha256': sha256(ROOT / 'PROTOCOL.md'),
                            'config_sha256': sha256(CONFIG),
                            'evaluator_sha256': sha256(ROOT / 'src/reference_site.py'),
                            'versions': versions()}
    path = ROOT / 'data/processed/reference_site_v2.json'
    write_json(path, result)
    print(json.dumps({'holo_reference_residues': len(result['holo_reference_residues']),
                      'mapped_to_apo': len(result['apo_mapped_residues']),
                      'unmapped': len(result['unmapped_residues']),
                      'missing_coordinates': {k: len(v) for k, v in result['missing_coordinate_residues'].items()},
                      'reference_centroid': result['reference_centroid']}, indent=2))
    return [path]


def inspection(run_id):
    from reference_site import load_cif, rows, scalar
    paths = verify_inputs()
    report = {}
    for pdb, path in paths.items():
        cif = load_cif(path)
        report[pdb] = {'title': scalar(cif, '_struct.title'), 'method': scalar(cif, '_exptl.method'),
                       'categories': {category: rows(cif, category) for category in (
                           '_entity_poly', '_pdbx_unobs_or_zero_occ_residues',
                           '_pdbx_unobs_or_zero_occ_atoms', '_struct_ref_seq', '_struct_ref_seq_dif',
                           '_pdbx_entity_nonpoly', '_pdbx_nonpoly_scheme', '_pdbx_nmr_ensemble')},
                       'model_numbers': sorted({r['pdbx_PDB_model_num'] for r in rows(cif, '_atom_site')})}
    path = ROOT / 'data/processed/structure_inspection.json'
    write_json(path, report)
    for pdb, r in report.items():
        print(pdb, r['title'], r['method'], 'models', r['model_numbers'])
        print('nonpolymer (excluding water):', [item for item in r['categories']['_pdbx_nonpoly_scheme']
                                               if item['mon_id'] != 'HOH'])
    return [path]


def tests(run_id):
    temporary = ROOT / 'results/tmp'
    temporary.mkdir(parents=True, exist_ok=True)
    tempfile.tempdir = str(temporary)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_*.py')
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    print(stream.getvalue())
    report = {'tests_run': result.testsRun, 'passed': result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
              'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
              'status': 'SUCCESS' if result.wasSuccessful() and result.testsRun else 'FAILED',
              'failure_details': [(str(t), error) for t, error in result.failures + result.errors]}
    path = ROOT / f'results/tests-{run_id}.json'
    write_json(path, report)
    if not result.wasSuccessful() or not result.testsRun:
        raise RuntimeError(f'Test suite FAILED: {report}')
    return [path]


def main():
    for folder in ('manifests/runs', 'results', 'results/tmp', 'data/raw', 'data/processed'):
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    run_id = now().replace(':', '').replace('.', '').replace('+', '_') + '-' + uuid.uuid4().hex[:8]
    action = sys.argv[1] if len(sys.argv) == 2 else 'INVALID'
    record = {'schema_version': 1, 'run_id': run_id, 'started_at': now(), 'status': 'RUNNING',
              'command_argv': [sys.executable, '-B', str(Path(__file__).resolve()), *sys.argv[1:]],
              'command': subprocess.list2cmdline([sys.executable, '-B', str(Path(__file__).resolve()), *sys.argv[1:]]),
              'cwd': os.getcwd(), 'inputs': inputs(), 'outputs': [], 'action': action}
    # Separate create-only start record means interruption is distinguishable from success.
    start_path = ROOT / f'manifests/runs/{run_id}.started.json'
    write_json(start_path, record)
    started = time.perf_counter()
    stream, exit_code, outputs = io.StringIO(), 0, []
    before = {p for folder in ('data', 'manifests', 'results') for p in (ROOT / folder).rglob('*') if p.is_file()}
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        try:
            record['versions'] = versions()
            git = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True, check=True)
            record['repository_base_commit'] = git.stdout.strip()
            record['code_version_note'] = 'Working source identified by individual SHA-256 hashes in inputs.'
            if action == 'acquire':
                outputs = acquisition()
            elif action == 'environment':
                outputs = environment()
            elif action == 'inspect':
                outputs = inspection(run_id)
            elif action == 'evaluate':
                outputs = evaluation()
            elif action == 'test':
                outputs = tests(run_id)
            elif action == 'source-review':
                from source_review import snapshot
                outputs = snapshot()
            elif action == 'source-review-extra':
                from source_review import supplementary
                outputs = supplementary()
            elif action == 'matched-core':
                from matched_core import prepare
                outputs = prepare()
            elif action == 'overlap-audit':
                from overlap_audit import audit
                outputs = audit()
            elif action == 'apply-amendment':
                from amendment import apply
                outputs = apply()
            elif action == 'preflight':
                from preflight import check
                outputs = check()
            elif action == 'archive-pre-review':
                outputs = []
                for relative in ('PROTOCOL.md', 'README.md', 'configs/reference_site.json', 'manifests/environment_plan.json'):
                    destination = ROOT / 'manifests/pre_review' / relative
                    write_once(destination, (ROOT / relative).read_bytes())
                    outputs.append(destination)
            elif action == 'archive-core-v0':
                outputs = []
                for filename in ('apo_matched_core.pdb', 'holo_matched_core_no_ligand.pdb', 'comparison_reference.json', 'matched_core_manifest.json'):
                    old = ROOT / 'data/processed' / filename
                    destination = ROOT / 'data/processed/superseded/bfactor_zero_v0' / filename
                    if not old.resolve().is_relative_to((ROOT / 'data/processed').resolve()):
                        raise ValueError('Archive path outside processed directory')
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    if destination.exists():
                        raise ValueError('Archive destination already exists')
                    old.rename(destination)
                    outputs.append(destination)
            elif action == 'verify':
                verify_inputs()
                print('All raw inputs match manifest SHA-256 and byte sizes.')
            else:
                raise ValueError('Allowed actions: acquire, environment, inspect, evaluate, test, verify')
            record['status'] = 'SUCCESS'
        except BaseException as error:
            record['status'], exit_code = 'FAILED', 1
            record['error'] = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
            traceback.print_exc()
    record['finished_at'] = now()
    record['wall_seconds'] = time.perf_counter() - started
    log_path = ROOT / f'results/{action}-{run_id}.log'
    write_once(log_path, stream.getvalue().encode('utf-8'))
    after = {p for folder in ('data', 'manifests', 'results') for p in (ROOT / folder).rglob('*') if p.is_file()}
    outputs = set(outputs) | (after - before) | {log_path}
    record['outputs'] = [file_record(p) for p in sorted(outputs)]
    write_json(ROOT / f'manifests/runs/{run_id}.json', record)
    print(stream.getvalue(), end='')
    print(f'{record["status"]}: {action}; run {run_id}')
    return exit_code


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    raise SystemExit(main())
