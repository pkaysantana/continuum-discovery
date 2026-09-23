import urllib.request
import json
import traceback

def fetch(pdb):
    print(f"\n================ {pdb} ================")
    try:
        url = f'https://data.rcsb.org/rest/v1/core/entry/{pdb}'
        with urllib.request.urlopen(url) as response:
            meta = json.loads(response.read().decode())
        
        title = meta.get('struct', {}).get('title', '')
        print(f"Title: {title}")
        
        url_poly = f'https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb}/1'
        with urllib.request.urlopen(url_poly) as response:
            poly = json.loads(response.read().decode())
        
        muts = poly.get('rcsb_entity_host_organism', [{}])[0].get('pdbx_mutation', '')
        if not muts:
            muts = poly.get('entity_poly', {}).get('rcsb_mutation_mutation_details', 'None')
        print(f"Mutations/Construct: {muts}")
        
        seq = poly.get('entity_poly', {}).get('pdbx_seq_one_letter_code', '')
        print(f"Sequence Length: {len(seq)}")
        
        print("Ligands:")
        npe_ids = meta.get('rcsb_entry_container_identifiers', {}).get('non_polymer_entity_ids', [])
        for npe_id in npe_ids:
            url_npe = f'https://data.rcsb.org/rest/v1/core/nonpolymer_entity/{pdb}/{npe_id}'
            try:
                with urllib.request.urlopen(url_npe) as response:
                    npe = json.loads(response.read().decode())
                    comp_id = npe.get('pdbx_entity_nonpoly', {}).get('comp_id', '')
                    name = npe.get('pdbx_entity_nonpoly', {}).get('name', '')
                    print(f"  - {comp_id}: {name}")
            except Exception as e:
                print(f"  - {npe_id}: Error fetching ligand info")
    except Exception as e:
        print(f"Error fetching {pdb}")

for pdb in ['5EDP', '5D41', '1II6', '1X88', '1Q0B', '1A5Y', '1T49', '1MQ4', '5L8J']:
    fetch(pdb)
