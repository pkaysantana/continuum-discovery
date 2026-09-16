"""Experiment-local, create-only provenance utilities (stdlib only)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')


def write_once(path, data):
    """Allow identical replay, never silently replace different bytes."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f'Refusing to replace existing file: {path}')
        return
    with path.open('xb') as handle:
        handle.write(data)


def write_json(path, value):
    write_once(path, canonical_bytes(value))


def file_record(path, root=ROOT):
    path = Path(path)
    return {'filename': path.relative_to(root).as_posix(),
            'sha256': sha256(path), 'byte_size': path.stat().st_size}


def verify_record(record, root=ROOT):
    path = (root / record['filename']).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Manifest path escapes experiment')
    actual = file_record(path, root)
    if any(actual[k] != record[k] for k in ('sha256', 'byte_size')):
        raise ValueError(f'Input hash/size mismatch: {record["filename"]}')
    return path
