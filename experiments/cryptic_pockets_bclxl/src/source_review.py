"""Download public source text for inspection only; never import or execute it."""
import json
import urllib.request
from provenance import ROOT, file_record, now, write_json, write_once


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'BCLXL-preregistration-review'})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()


def snapshot():
    base = ROOT / 'manifests/source_review'
    outputs, receipts = [], []
    for name, repo, ref in [('lacuna', 'mooreneural/lacuna', 'main'),
                            ('p2rank', 'rdk/p2rank', '2.5.1'),
                            ('p2rank-datasets', 'rdk/p2rank-datasets', 'master')]:
        commit_url = f'https://api.github.com/repos/{repo}/commits/{ref}'
        commit = json.loads(fetch(commit_url))['sha']
        tree_url = f'https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1'
        tree = json.loads(fetch(tree_url))
        if tree.get('truncated'):
            raise ValueError('Source tree truncated; audit cannot claim completeness')
        path = base / name / 'tree.json'
        write_json(path, tree)
        outputs.append(path)
        selected = []
        for item in tree['tree']:
            p = item['path']
            if item['type'] != 'blob':
                continue
            if name == 'lacuna':
                keep = p.endswith(('.py', '.md', '.toml')) and not p.startswith(('paper/', 'tests/'))
                keep = keep or (p.endswith(('.csv', '.json', '.tsv')) and any(s in p.lower() for s in ('train', 'split', 'dataset', 'target')))
            elif name == 'p2rank':
                keep = p.endswith(('.md', '.groovy')) and (p.count('/') < 2 or 'config' in p)
            else:
                keep = p.endswith(('.ds', '.md', '.txt', '.csv')) and item.get('size', 0) < 2000000
            if keep:
                selected.append(p)
        for p in selected:
            url = f'https://raw.githubusercontent.com/{repo}/{commit}/{p}'
            target = base / name / p
            # Source snapshots are immutable; replays still check upstream ref identity below.
            data = fetch(url)
            write_once(target, data)
            receipts.append({'repository': repo, 'commit': commit, 'source_url': url,
                             'retrieved_at': now(), **file_record(target)})
            outputs.append(target)
        print(name, commit, len(selected), 'source text files; no code executed')
    receipt = base / 'source_manifest.json'
    write_json(receipt, {'purpose': 'Read-only source audit. No detector imports or execution.', 'files': receipts})
    return outputs + [receipt]


def supplementary():
    """Bounded follow-up after recursive dataset tree was explicitly truncated."""
    base = ROOT / 'manifests/source_review'
    receipts, outputs = [], []
    repo = 'rdk/p2rank-datasets'
    commit = json.loads(fetch(f'https://api.github.com/repos/{repo}/commits/master'))['sha']
    tree = json.loads(fetch(f'https://api.github.com/repos/{repo}/git/trees/{commit}'))
    path = base / 'p2rank-datasets/root_tree.json'
    write_json(path, tree)
    outputs.append(path)
    requests = []
    for item in tree['tree']:
        if item['type'] == 'blob' and item['path'].endswith(('.ds', '.md')):
            requests.append((f'https://raw.githubusercontent.com/{repo}/{commit}/{item["path"]}',
                             base / 'p2rank-datasets' / item['path']))
    requests.extend([
        ('https://raw.githubusercontent.com/rdk/p2rank/9808a7723be9a94e2ffc21ab5f724cb6ae4ba01e/misc/tutorials/training-tutorial.md', base / 'p2rank/training-tutorial.md'),
        ('https://osf.io/download/5s93p/', base / 'cryptobench/folds.json')])
    for url, target in requests:
        try:
            data = fetch(url)
            write_once(target, data)
            receipts.append({'source_url': url, 'retrieved_at': now(), 'status': 'SUCCESS', **file_record(target)})
            outputs.append(target)
        except Exception as error:
            # Audit can report UNKNOWN when a public source is unavailable; never substitute data.
            receipts.append({'source_url': url, 'retrieved_at': now(), 'status': 'FAILED',
                             'error': f'{type(error).__name__}: {error}'})
            print('FAILED source retrieval:', url, str(error))
    path = base / 'supplementary_manifest.json'
    write_json(path, {'dataset_repository_commit': commit, 'scope': 'Root .ds membership lists only; no structures or predictions downloaded.', 'sources': receipts})
    print('Supplementary sources:', len(receipts), 'attempted;', sum(r['status'] == 'FAILED' for r in receipts), 'failed')
    return outputs + [path]
