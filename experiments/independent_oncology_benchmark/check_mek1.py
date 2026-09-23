import urllib.request, json
for pdb in ['1S9J', '1S9I']:
    print(f'\n--- {pdb} ---')
    try:
        url = f'https://data.rcsb.org/rest/v1/core/entry/{pdb}'
        with urllib.request.urlopen(url) as response:
            meta = json.loads(response.read().decode())
        url_poly = f'https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb}/1'
        with urllib.request.urlopen(url_poly) as response:
            poly = json.loads(response.read().decode())
        print(f"Title: {meta.get('struct', {}).get('title')}")
        muts = poly.get('rcsb_entity_host_organism', [{}])[0].get('pdbx_mutation', '')
        if not muts:
            muts = poly.get('entity_poly', {}).get('rcsb_mutation_mutation_details', 'None')
        print(f"Mutations: {muts}")
        print(f"Length: {len(poly.get('entity_poly',{}).get('pdbx_seq_one_letter_code', ''))}")
        print("Ligands:")
        npe_ids = meta.get('rcsb_entry_container_identifiers', {}).get('non_polymer_entity_ids', [])
        for npe_id in npe_ids:
            try:
                url_npe = f'https://data.rcsb.org/rest/v1/core/nonpolymer_entity/{pdb}/{npe_id}'
                with urllib.request.urlopen(url_npe) as r2:
                    npe = json.loads(r2.read().decode())
                    print(f"  - {npe.get('pdbx_entity_nonpoly', {}).get('comp_id', '')}: {npe.get('pdbx_entity_nonpoly', {}).get('name', '')}")
            except: pass
    except: pass
