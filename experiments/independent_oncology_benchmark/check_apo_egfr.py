import urllib.request
import json

def fetch_pdb_metadata(pdb_id):
    url = f'https://data.rcsb.org/rest/v1/core/entry/{pdb_id}'
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except:
        return None

def fetch_polymer_entity(pdb_id):
    url = f'https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb_id}/1'
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except:
        return None

ids = ["5EDP", "2EB2", "2GS2", "2JIT", "4R3P", "4R3R", "4TKS", "5CZH", "5CZI", "2N5S", "5LV6", "4I20", "2M20", "4I21", "2M0B", "2RF9", "2RFE", "3OB2", "4ZJV", "7TVD", "4I1Z", "7SYD", "7SYE", "7SZ0", "7SZ1", "7SZ5", "7SZ7", "8JFQ"]

for pdb in ids[:10]:
    meta = fetch_pdb_metadata(pdb)
    poly = fetch_polymer_entity(pdb)
    if meta and poly:
        title = meta.get('struct', {}).get('title', '')
        muts = poly.get('rcsb_entity_host_organism', [{}])[0].get('pdbx_mutation', '')
        if not muts:
            muts = poly.get('entity_poly', {}).get('rcsb_mutation_mutation_details', 'None')
        print(f"{pdb}: {title} | Muts: {muts}")
