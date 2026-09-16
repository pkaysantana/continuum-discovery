"""Select a common observed native core without using any pocket geometry."""
import json
import math
from collections import Counter
from provenance import ROOT, file_record, sha256, verify_record, write_json, write_once
from reference_site import (align_sequences, centroid, contacts, ligand, load_cif, protein, rows)

BACKBONE = {'N', 'CA', 'C', 'O'}


def expression_tags(cif, chain):
    return {int(r['seq_num']) for r in rows(cif, '_struct_ref_seq_dif')
            if r.get('pdbx_pdb_strand_id') == chain and 'expression tag' in r.get('details', '').lower()}


def select_core(alignment, holo, apo, holo_tags=frozenset(), apo_tags=frozenset()):
    retained, excluded = [], {'holo': [], 'apo': []}
    for pair in alignment['positions']:
        h, a = pair['holo_label_seq_id'], pair['apo_label_seq_id']
        reasons = []
        if h is None or a is None:
            reasons.append('no_counterpart_in_deposited_sequence')
        elif not pair['identical']:
            reasons.append('amino_acid_mismatch')
        if h in holo_tags or a in apo_tags:
            reasons.append('expression_tag_annotation')
        if h is not None and h not in holo:
            reasons.append('holo_coordinates_missing')
        if a is not None and a not in apo:
            reasons.append('apo_coordinates_missing')
        for name, pos, residues in [('holo', h, holo), ('apo', a, apo)]:
            if pos in residues and not BACKBONE <= {x['name'] for x in residues[pos]['atoms']}:
                reasons.append(name + '_incomplete_backbone')
        if reasons:
            for name, pos, residues in [('holo', h, holo), ('apo', a, apo)]:
                if pos is not None:
                    excluded[name].append({'label_seq_id': pos, 'residue': residues[pos]['id'] if pos in residues else None,
                                           'amino_acid': pair[name + '_aa'], 'reasons': reasons})
        else:
            ident = holo[h]['id']
            if ident['insertion_code'] or not ident['auth_seq_id'].isdigit():
                raise ValueError('Matched output numbering requires positive integer holo author IDs without insertions; review needed')
            retained.append({'holo': holo[h]['id'], 'apo': apo[a]['id'],
                             'output_chain': 'A', 'output_resseq': int(ident['auth_seq_id'])})
    if not retained or len({r['output_resseq'] for r in retained}) != len(retained):
        raise ValueError('Empty or ambiguous matched structural core')
    return retained, excluded


def pdb_bytes(residues, retained, state):
    """PDB 3-decimal coordinates preserve the archive's 3-decimal atom positions.

    Both states use holo author residue numbering. Gaps and TER preserve breaks;
    no bonds, missing atoms, hydrogens, caps or reconstructed residues are added.
    """
    lines = ['REMARK 950 MATCHED COMMON OBSERVED CORE; NO COORDINATES GENERATED',
             'REMARK 950 NUMBERING: HOLO AUTHOR RESIDUE IDS; SEE MATCHED_CORE_MANIFEST.JSON']
    serial, previous = 1, None
    for match in retained:
        number = match['output_resseq']
        if previous is not None and number != previous + 1:
            lines.append('TER')
        residue = residues[match[state]['label_seq_id']]
        for atom in residue['atoms']:
            name = atom['name']
            atom_field = f' {name:<3}' if len(name) < 4 and len(atom['element']) == 1 else f'{name:<4}'
            x, y, z = atom['xyz']
            lines.append(f'ATOM  {serial:5d} {atom_field} {residue["id"]["resname"]:>3} A{number:4d}    '
                         f'{x:8.3f}{y:8.3f}{z:8.3f}{atom["occupancy"]:6.2f}{atom["bfactor"]:6.2f}          {atom["element"]:>2}  ')
            serial += 1
        previous = number
    return ('\n'.join(lines + ['TER', 'END']) + '\n').encode('ascii')


def retain_bfactors(cif, residues):
    atom_rows = {(int(r['label_seq_id']), r['label_atom_id'], '' if r['label_alt_id'] in ('.', '?') else r['label_alt_id']): r
                 for r in rows(cif, '_atom_site') if r['label_asym_id'] == 'A'
                 and r['label_seq_id'] not in ('.', '?') and r['pdbx_PDB_model_num'] == '1'}
    for position, residue in residues.items():
        for atom in residue['atoms']:
            bfactor = float(atom_rows[(position, atom['name'], atom['alt'])]['B_iso_or_equiv'])
            if not math.isfinite(bfactor):
                raise ValueError('Invalid B factor; do not substitute a value')
            atom['bfactor'] = bfactor


def prepare():
    cfg = json.loads((ROOT / 'configs/reference_site.json').read_text())
    raw_manifest = json.loads((ROOT / 'manifests/input_manifest.json').read_text())
    paths = {r['pdb_id']: verify_record(r) for r in raw_manifest['structures']}
    hc, ac = load_cif(paths['2YXJ']), load_cif(paths['1LXL'])
    hs, hr = protein(hc, 'A'); aps, ar = protein(ac, 'A')
    retain_bfactors(hc, hr); retain_bfactors(ac, ar)
    alignment = align_sequences(hs, aps, cfg['alignment'])
    original = json.loads((ROOT / 'data/processed/reference_site.json').read_text())
    if alignment != original['alignment']:
        raise ValueError('Sequence mapping differs from original evaluator; stop for review')
    kept, excluded = select_core(alignment, hr, ar, expression_tags(hc, 'A'), expression_tags(ac, 'A'))
    outputs = []
    for state, residues, filename in [('apo', ar, 'apo_matched_core.pdb'), ('holo', hr, 'holo_matched_core_no_ligand.pdb')]:
        path = ROOT / 'data/processed' / filename
        write_once(path, pdb_bytes(residues, kept, state))
        outputs.append(path)
    lig = ligand(hc, cfg)
    refs = {}
    by_holo = {m['holo']['label_seq_id']: m for m in kept}
    for cutoff, role in [(5.0, 'PRIMARY'), (4.5, 'SENSITIVITY'), (4.0, 'PRE_RUN_DIAGNOSTIC_ONLY')]:
        site = contacts(hr, lig['atoms'], cutoff)
        if any(r['label_seq_id'] not in by_holo for r in site):
            raise ValueError('Core excludes a reference residue; do not redefine reference silently')
        entry = {'role': role, 'residue_count': len(site), 'holo_residues': site,
                 'output_residue_ids': [by_holo[r['label_seq_id']]['output_resseq'] for r in site]}
        for state, residues in [('holo', hr), ('apo', ar)]:
            selected = [residues[by_holo[r['label_seq_id']][state]['label_seq_id']] for r in site]
            entry[state + '_reference_centroid_CA'] = centroid([a for r in selected for a in r['atoms'] if a['name'] == 'CA'])
            entry[state + '_reference_centroid_heavy_atoms_secondary'] = centroid([a for r in selected for a in r['atoms']])
        refs[str(cutoff)] = entry
    if [refs[str(c)]['residue_count'] for c in (5.0, 4.5, 4.0)] != [24, 22, 19]:
        raise ValueError('Pre-execution review contact counts do not reproduce')
    reference_path = ROOT / 'data/processed/comparison_reference.json'
    write_json(reference_path, {'primary_centroid_definition': 'Unweighted mean of reference-residue CA coordinates in evaluated input frame.',
                                'primary_recovery_distance_angstrom': 4.0, 'cutoffs': refs,
                                'original_reference_sha256': sha256(ROOT / 'data/processed/reference_site.json'),
                                'frame_rule': 'Apo original frame for apo inputs; holo original frame for holo control. Never subtract across frames.'})
    outputs.append(reference_path)
    manifest_path = ROOT / 'data/processed/matched_core_manifest.json'
    write_json(manifest_path, {
        'schema_version': 1, 'raw_inputs': [file_record(p) for p in paths.values()],
        'mapping_method': alignment['method'], 'alignment_sha256_source': sha256(ROOT / 'data/processed/reference_site.json'),
        'selection_rule': 'Unique identical sequence alignment pairs; observed N,CA,C,O in both states; exclude archive-annotated expression tags in either state. Independent of pocket location.',
        'retained_residues': kept, 'excluded_residues': excluded,
        'counts': {'retained_apo': len(kept), 'retained_holo': len(kept),
                   'excluded_apo': len(excluded['apo']), 'excluded_holo': len(excluded['holo'])},
        'output_numbering': 'Both states: chain A, original holo author residue numbers; mapping retained explicitly.',
        'atom_policy': 'Existing selected occupied heavy atoms only; coherent altloc rule unchanged; coordinates, occupancies and original B factors preserved. No replacement values.',
        'excluded_other_content': 'All other chains, models, nonprotein entities including N3C/water/ions/glycerol, hydrogens and unselected alternate atoms.',
        'processed_outputs': [file_record(p) for p in outputs],
        'warnings': ['Core is discontinuous; gaps/TER retained, no repair or caps. NMA may still connect spatial neighbors across sequence gaps.',
                     'Matched residues do not eliminate NMR versus crystal differences or missing sidechain-atom differences.',
                     'Same apo file bytes must be supplied to both detectors; same holo control bytes likewise.']})
    print('Matched core:', len(kept), 'residues in each state; exclusions', {k: len(v) for k, v in excluded.items()})
    print('Reference counts:', {k: v['residue_count'] for k, v in refs.items()})
    return outputs + [manifest_path]
