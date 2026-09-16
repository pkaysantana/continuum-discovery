"""Experiment-local immutable files and provenance."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def record(path):
    path = Path(path)
    return {'filename': path.relative_to(ROOT).as_posix(), 'sha256': digest(path), 'byte_size': path.stat().st_size}


def immutable(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError(f'Refusing to overwrite immutable file: {path}')
        return
    with path.open('xb') as handle:
        handle.write(content)


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf-8')


def save_json(path, value):
    immutable(path, json_bytes(value))


def verify(item):
    path = (ROOT / item['filename']).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError('Path escapes experiment')
    if digest(path) != item['sha256'] or path.stat().st_size != item['byte_size']:
        raise ValueError(f'Raw hash/size mismatch: {path}')
    return path
