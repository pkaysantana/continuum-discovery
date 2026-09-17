"""Offline completeness checks shared by acquisition and the frozen-source audit."""
from urllib.parse import parse_qs, urlsplit


def validate_pages(pages, assay):
    """Consume pages without repairing them; require complete, unique activities."""
    total, observed, ids, terminal = None, 0, set(), False
    for page in pages:
        if terminal:
            raise ValueError('ChEMBL page follows terminal page')
        meta, rows = page['page_meta'], page['activities']
        n = meta['total_count']
        if not isinstance(n, int) or n < 0:
            raise ValueError('Invalid ChEMBL total_count')
        if total is not None and n != total:
            raise ValueError('ChEMBL activity count changed during pagination')
        total = n
        if meta['offset'] != observed:
            raise ValueError('Noncontiguous ChEMBL page offset')
        if not rows:
            raise ValueError('Unexpected empty ChEMBL page')
        if not isinstance(meta['limit'], int) or meta['limit'] <= 0 or len(rows) > meta['limit']:
            raise ValueError('Invalid ChEMBL page size')
        for row in rows:
            if row['assay_chembl_id'] != assay:
                raise ValueError('Wrong assay during ChEMBL pagination')
            if row['activity_id'] in ids:
                raise ValueError('Repeated activity ID during ChEMBL pagination')
            ids.add(row['activity_id'])
        observed += len(rows)
        terminal = meta['next'] is None
        if observed > total or (terminal and observed != total):
            raise ValueError('ChEMBL pagination incomplete: observed rows differ from total_count')
        if not terminal:
            if observed >= total:
                raise ValueError('ChEMBL pagination incomplete: nonterminal final page')
            query = parse_qs(urlsplit(meta['next']).query)
            if query.get('offset') != [str(observed)] or query.get('assay_chembl_id') != [assay]:
                raise ValueError('Inconsistent ChEMBL next-page metadata')
    if total is None or not terminal or observed != total or len(ids) != total:
        raise ValueError('ChEMBL pagination incomplete: pages, rows and unique activity IDs must agree')
    return observed
