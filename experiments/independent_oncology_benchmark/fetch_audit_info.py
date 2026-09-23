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
        traceback.print_exc()

for pdb in ['4I22', '5D41', '1HCL', '3PY1']:
    fetch(pdb)
