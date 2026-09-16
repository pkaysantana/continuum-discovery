"""Fetch only frozen sources and their provenance, without dataset transformations."""
import ast
import csv
import io
import json
import tarfile
import urllib.request
from provenance import ROOT, immutable, record, save_json, utc, verify

API = 'https://www.ebi.ac.uk/chembl/api/data'
ASSAYS = ['CHEMBL3301370', 'CHEMBL3301371', 'CHEMBL3301372']


def download(url, relative, source, version=None, kind='support'):
    target = ROOT / 'data/raw' / relative
    receipt = ROOT / 'manifests/downloads' / (relative.replace('/', '__') + '.json')
    if target.exists():
        if not receipt.exists():
            raise ValueError(f'Raw file without receipt: {relative}')
        saved = json.loads(receipt.read_text())
        verify(saved)
        if saved['source_url'] != url:
            raise ValueError('Source URL changed; no silent replacement')
        return target
    req = urllib.request.Request(url, headers={'User-Agent': 'CompoundToExposure-forensic-audit/1.0'})
    with urllib.request.urlopen(req, timeout=120) as response:
        data = response.read()
        final_url = response.geturl()
        headers = {k: response.headers.get(k) for k in ['Content-Type', 'ETag', 'Last-Modified']}
    immutable(target, data)
    saved = {'source': source, 'source_url': url, 'final_url': final_url, 'retrieved_utc': utc(),
             'version': version, 'kind': kind, 'http_headers': headers, **record(target)}
    save_json(receipt, saved)
    print('Acquired', relative, saved['byte_size'], 'bytes', flush=True)
    return target


def chembl():
    status = download(API + '/status.json', 'chembl/status.json', 'ChEMBL')
    release = json.loads(status.read_text())
    for assay in ASSAYS:
        download(f'{API}/assay/{assay}.json', f'chembl/{assay}_assay.json', assay, release)
        offset, total, ids = 0, None, set()
        while total is None or offset < total:
            url = f'{API}/activity.json?assay_chembl_id={assay}&limit=1000&offset={offset}&order_by=activity_id'
            path = download(url, f'chembl/{assay}_activities_{offset:05d}.json', assay, release, 'dataset')
            page = json.loads(path.read_text())
            n = page['page_meta']['total_count']
            if total is not None and n != total:
                raise ValueError('ChEMBL activity count changed during pagination')
            total = n
            activities = page['activities']
            if not activities:
                raise ValueError('Unexpected empty ChEMBL page')
            for row in activities:
                if row['assay_chembl_id'] != assay or row['activity_id'] in ids:
                    raise ValueError('Wrong assay or repeated activity ID during pagination')
                ids.add(row['activity_id'])
            offset += len(activities)
        if len(ids) != total:
            raise ValueError('ChEMBL pagination incomplete')
        print(assay, 'OBSERVED activities:', total, flush=True)


def tdc():
    version = '1.1.15'
    meta = download(f'https://pypi.org/pypi/PyTDC/{version}/json', 'tdc/PyTDC-1.1.15-pypi.json', 'PyTDC', version)
    package = json.loads(meta.read_text())
    artifact = next(r for r in package['urls'] if r['packagetype'] == 'sdist')
    archive = download(artifact['url'], 'tdc/' + artifact['filename'], 'PyTDC', version)
    from provenance import digest
    if digest(archive) != artifact['digests']['sha256']:
        raise ValueError('PyTDC sdist hash differs from PyPI metadata')
    # Read selected source members as text only; no extraction/execution of package code.
    with tarfile.open(archive) as tar:
        for suffix in ('tdc/metadata.py', 'tdc/utils/load.py'):
            members = [m for m in tar.getmembers() if m.name.endswith('/' + suffix)]
            if len(members) != 1:
                raise ValueError('Ambiguous package source member')
            code = tar.extractfile(members[0]).read()
            immutable(ROOT / 'data/interim/tdc_source' / suffix, code)
            if suffix.endswith('metadata.py'):
                tree = ast.parse(code)
    assignments = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('name2id', 'name2type'):
                    assignments[target.id] = ast.literal_eval(node.value)
    for name in ('clearance_microsome_az', 'clearance_hepatocyte_az'):
        file_id = assignments['name2id'][name]
        extension = assignments['name2type'][name]
        if extension != 'tab':
            raise ValueError('Unexpected TDC format; review required')
        download(f'https://dataverse.harvard.edu/api/access/datafile/{file_id}', f'tdc/{name}.tab',
                 name, {'PyTDC': version, 'dataverse_file_id': file_id, 'method': 'Direct byte download using exact sdist name2id registry; PyTDC is not installed or invoked.'}, 'dataset')
        download(f'https://dataverse.harvard.edu/api/files/{file_id}/metadata', f'tdc/{name}_metadata.json', name, version)


def biogen():
    repo = 'molecularinformatics/Computational-ADME'
    info = download(f'https://api.github.com/repos/{repo}/commits/main', 'biogen/source_commit.json', 'Biogen')
    commit = json.loads(info.read_text())['sha']
    for name in ('ADME_public_set_3521.csv', 'README.md', 'LICENSE'):
        download(f'https://raw.githubusercontent.com/{repo}/{commit}/{name}', f'biogen/{name}', 'Biogen',
                 {'repository': repo, 'commit': commit}, 'dataset' if name.endswith('.csv') else 'support')


def manifest():
    records = []
    for path in sorted((ROOT / 'manifests/downloads').glob('*.json')):
        rec = json.loads(path.read_text())
        raw = verify(rec)
        if raw.suffix in ('.tab', '.csv'):
            reader = csv.DictReader(io.StringIO(raw.read_text(encoding='utf-8-sig')), delimiter='\t' if raw.suffix == '.tab' else ',')
            items = list(reader)
            rec.update(raw_row_count=len(items), schema=reader.fieldnames)
        elif raw.suffix == '.json':
            obj = json.loads(raw.read_text())
            items = obj.get('activities') if isinstance(obj, dict) else None
            if not isinstance(items, list):
                items = None
            rec.update(raw_row_count=len(items) if items is not None else 1,
                       schema=sorted(set().union(*(r.keys() for r in items))) if items else (sorted(obj) if isinstance(obj, dict) else 'JSON array'))
        else:
            rec.update(raw_row_count=None, schema='source documentation/archive; not a dataset table')
        records.append(rec)
    save_json(ROOT / 'manifests/source_manifest.json', {'sources': records})
    return records


def acquire_all():
    chembl(); tdc(); biogen(); manifest()
