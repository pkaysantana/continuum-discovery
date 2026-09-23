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

for apo, holo in [('1HCL', '3PY1'), ('5MO4', '5MO3')]:
    a = fetch_pdb_metadata(apo)
    h = fetch_pdb_metadata(holo)
    if a and h:
        print(f'Apo {apo} res: {a.get("rcsb_entry_info",{}).get("resolution_combined", [None])[0]}')
        print(f'Holo {holo} res: {h.get("rcsb_entry_info",{}).get("resolution_combined", [None])[0]}')
        a_poly = fetch_polymer_entity(apo)
        h_poly = fetch_polymer_entity(holo)
        if a_poly:
            print(f"  Apo chain length: {len(a_poly.get('entity_poly',{}).get('pdbx_seq_one_letter_code', ''))}")
        if h_poly:
            print(f"  Holo chain length: {len(h_poly.get('entity_poly',{}).get('pdbx_seq_one_letter_code', ''))}")
