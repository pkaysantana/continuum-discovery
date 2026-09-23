import urllib.request
import json
import sys

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
    ('EGFR L858R', '4I22', '5D41'),
    ('IDH1 R132H', '4KZO', '5CGJ'),
    ('AKT1 (Allosteric)', '1UNP', '3O96'),
    ('Menin', '3U85', '4X5Z'),
    ('BRAF V600E', '4MNE', '4MNF') # Just a guess for apo/holo
]

for name, apo, holo in candidates:
    a = fetch_pdb_metadata(apo)
    h = fetch_pdb_metadata(holo)
    if a and h:
        apo_title = a.get('struct',{}).get('title', '')[:60]
        holo_title = h.get('struct',{}).get('title', '')[:60]
        
        apo_res = a.get('rcsb_entry_info',{}).get('resolution_combined', [None])[0]
        holo_res = h.get('rcsb_entry_info',{}).get('resolution_combined', [None])[0]
        
        h_ligands = h.get('rcsb_binding_affinity', [])
        # We can also get non-polymer entities
        
        print(f"--- {name} ---")
        print(f"Apo:  {apo} (Res: {apo_res}A) - {apo_title}")
        print(f"Holo: {holo} (Res: {holo_res}A) - {holo_title}")
        
        a_poly = fetch_polymer_entity(apo)
        h_poly = fetch_polymer_entity(holo)
        
        if a_poly:
            print(f"  Apo chain length: {len(a_poly.get('entity_poly',{}).get('pdbx_seq_one_letter_code', ''))}, details: {a_poly.get('rcsb_polymer_entity',{}).get('pdbx_description')}")
        if h_poly:
            print(f"  Holo chain length: {len(h_poly.get('entity_poly',{}).get('pdbx_seq_one_letter_code', ''))}, details: {h_poly.get('rcsb_polymer_entity',{}).get('pdbx_description')}")
        print()
    else:
        print(f"Failed to fetch {name}")
