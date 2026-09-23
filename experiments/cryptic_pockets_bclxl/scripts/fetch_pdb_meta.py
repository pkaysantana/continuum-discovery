import urllib.request
import json

def fetch_pdb_metadata(pdb_id):
    url = f'https://data.rcsb.org/rest/v1/core/entry/{pdb_id}'
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {pdb_id}: {e}")
        return None

def fetch_polymer_entity(pdb_id):
    url = f'https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb_id}/1'
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return None

candidates = [
    ('KRAS G12C', '4OBE', '4L9S'), # 4OBE is apo, 4L9S is holo
    ('SHP2', '2SHP', '5EHR'), 
    ('EGFR L858R', '4I22', '5D41'), 
    ('Menin', '3U84', '4X5Z'), 
    ('MDM2', '1Z1M', '4HG7'),
    ('IDH1', '3INM', '5SVB'),
    ('N-myristoyltransferase 1', '3IU1', '5O45'),
    ('PI3K alpha', '4JPS', '4JPR'),
    ('CDK4', '2W96', '2W9Z')
]

for name, apo, holo in candidates:
    a = fetch_pdb_metadata(apo)
    h = fetch_pdb_metadata(holo)
    if a and h:
        apo_title = a.get('struct',{}).get('title', '')[:60]
        holo_title = h.get('struct',{}).get('title', '')[:60]
        
        # Check ligands
        h_ligands = h.get('rcsb_binding_affinity', [])
        
        print(f"--- {name} ---")
        print(f"Apo:  {apo} ({apo_title})")
        print(f"Holo: {holo} ({holo_title})")
        
        a_poly = fetch_polymer_entity(apo)
        h_poly = fetch_polymer_entity(holo)
        
        if a_poly:
            print(f"  Apo sequence length: {len(a_poly.get('entity_poly',{}).get('pdbx_seq_one_letter_code', ''))}")
        if h_poly:
            print(f"  Holo sequence length: {len(h_poly.get('entity_poly',{}).get('pdbx_seq_one_letter_code', ''))}")
        print()
