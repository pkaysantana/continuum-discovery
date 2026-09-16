"""Transparent mmCIF contact geometry and full-polymer sequence mapping.

No pocket detection, coordinate generation, optimization, or historical imports.
"""
from __future__ import annotations

from collections import defaultdict
import math

import numpy as np
from Bio.Align import PairwiseAligner
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

AA = dict(zip(
    'ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL'.split(),
    'ARNDCQEGHILKMFPSTWYV'))
MISSING = {'.', '?', ''}


def rows(cif, category):
    prefix = category + '.'
    columns = {key[len(prefix):]: value for key, value in cif.items()
               if key.startswith(prefix)}
    if not columns:
        return []
    if len({len(value) for value in columns.values()}) != 1:
        raise ValueError(f'Unequal column lengths in {category}')
    return [dict(zip(columns, values)) for values in zip(*columns.values())]


def scalar(cif, key):
    values = cif[key]
    if len(values) != 1:
        raise ValueError(f'Expected single value: {key}')
    return values[0]


def load_cif(path):
    return MMCIF2Dict(str(path))


def sequence(cif, label_chain):
    entities = [r['entity_id'] for r in rows(cif, '_struct_asym') if r['id'] == label_chain]
    if len(entities) != 1:
        raise ValueError(f'Expected one chain {label_chain}')
    entity = entities[0]
    types = [r['type'] for r in rows(cif, '_entity_poly') if r['entity_id'] == entity]
    if types != ['polypeptide(L)']:
        raise ValueError(f'Chain {label_chain} is not polypeptide(L)')
    seqrows = sorted((r for r in rows(cif, '_entity_poly_seq') if r['entity_id'] == entity),
                     key=lambda r: int(r['num']))
    if [int(r['num']) for r in seqrows] != list(range(1, len(seqrows) + 1)) or not seqrows:
        raise ValueError('Noncontiguous or ambiguous polymer sequence')
    if any(r['mon_id'] not in AA for r in seqrows):
        raise ValueError('Nonstandard polymer residue requires human review')
    return entity, ''.join(AA[r['mon_id']] for r in seqrows)


def selected_heavy_atoms(atom_rows):
    """Choose a coherent residue alt conformer using summed occupancy."""
    atoms = []
    for row in atom_rows:
        occupancy = float(row['occupancy'])
        xyz = tuple(float(row[k]) for k in ('Cartn_x', 'Cartn_y', 'Cartn_z'))
        if not math.isfinite(occupancy) or not 0 <= occupancy <= 1 or not all(map(math.isfinite, xyz)):
            raise ValueError('Invalid occupancy or coordinates')
        element = row['type_symbol'].upper()
        if element in MISSING:
            raise ValueError('Missing atom element')
        if occupancy > 0 and element not in {'H', 'D'}:
            atoms.append({'name': row['label_atom_id'], 'element': element,
                          'alt': '' if row['label_alt_id'] in MISSING else row['label_alt_id'],
                          'occupancy': occupancy, 'xyz': xyz})
    occupancy_by_alt = defaultdict(float)
    for atom in atoms:
        if atom['alt']:
            occupancy_by_alt[atom['alt']] += atom['occupancy']
    chosen = min(occupancy_by_alt, key=lambda a: (-occupancy_by_alt[a], a)) if occupancy_by_alt else ''
    selected = sorted((a for a in atoms if a['alt'] in {'', chosen}), key=lambda a: a['name'])
    if len({a['name'] for a in selected}) != len(selected):
        raise ValueError('Duplicate atom names after alternate-location selection')
    return selected, {'available_alt_ids': sorted(occupancy_by_alt), 'selected_alt_id': chosen}


def residue_id(row):
    return {'label_chain': row['label_asym_id'],
            'label_seq_id': int(row['label_seq_id']) if row['label_seq_id'] not in MISSING else None,
            'auth_chain': row['auth_asym_id'], 'auth_seq_id': row['auth_seq_id'],
            'insertion_code': '' if row['pdbx_PDB_ins_code'] in MISSING else row['pdbx_PDB_ins_code'],
            'resname': row['label_comp_id']}


def protein(cif, chain, model='1'):
    entity, seq = sequence(cif, chain)
    groups = defaultdict(list)
    for row in rows(cif, '_atom_site'):
        if row['label_asym_id'] != chain or row['pdbx_PDB_model_num'] != model:
            continue
        if row['label_seq_id'] in MISSING:
            continue
        if row['label_entity_id'] != entity:
            raise ValueError('Atom entity differs from chain entity')
        pos = int(row['label_seq_id'])
        if not 1 <= pos <= len(seq) or AA.get(row['label_comp_id']) != seq[pos - 1]:
            raise ValueError('Atom residue differs from declared polymer sequence')
        groups[pos].append(row)
    residues = {}
    for pos, group in sorted(groups.items()):
        ids = [residue_id(row) for row in group]
        if any(ident != ids[0] for ident in ids):
            raise ValueError('Multiple residue identities at one label position')
        atoms, alt = selected_heavy_atoms(group)
        if atoms:
            residues[pos] = {'id': ids[0], 'atoms': atoms, 'alternate_locations': alt}
    if not residues:
        raise ValueError(f'No protein coordinates in chain {chain}, model {model}')
    return seq, residues


def ligand(cif, config):
    comp = config['ligand_comp_id']
    names = [r.get('pdbx_synonyms', '') for r in rows(cif, '_chem_comp') if r['id'] == comp]
    # Exact synonym token, accepting archive comma/semicolon-separated synonyms.
    synonyms = {part.strip().upper() for name in names for part in name.replace(';', ',').split(',')}
    if config['ligand_synonym'].upper() not in synonyms:
        raise ValueError(f'Ligand {comp} metadata does not identify {config["ligand_synonym"]}')
    entity_types = {r['id']: r['type'] for r in rows(cif, '_entity')}
    matches = []
    for row in rows(cif, '_atom_site'):
        if (row['label_comp_id'] == comp and row['label_asym_id'] == config['ligand_label_chain']
                and row['auth_asym_id'] == config['ligand_auth_chain']
                and row['pdbx_PDB_model_num'] == config['model_number']):
            if entity_types.get(row['label_entity_id']) != 'non-polymer' or row['label_seq_id'] not in MISSING:
                raise ValueError('Specified ligand is not a nonpolymer instance')
            matches.append(row)
    if not matches:
        raise ValueError(f'Specified ligand {comp} absent from selected chain/model')
    ident = residue_id(matches[0])
    if any(residue_id(row) != ident for row in matches):
        raise ValueError('Multiple ligand instances match selection')
    atoms, alt = selected_heavy_atoms(matches)
    if not atoms:
        raise ValueError('Specified ligand has no occupied heavy atoms')
    return {'id': ident, 'atoms': atoms, 'alternate_locations': alt}


def contacts(residues, ligand_atoms, cutoff):
    if not math.isfinite(cutoff) or cutoff <= 0 or not ligand_atoms:
        raise ValueError('Positive finite cutoff and nonempty ligand required')
    xyz = np.array([a['xyz'] for a in ligand_atoms], dtype=np.float64)
    output = []
    for pos, residue in sorted(residues.items()):
        p = np.array([a['xyz'] for a in residue['atoms']], dtype=np.float64)
        squared = np.sum((p[:, None, :] - xyz[None, :, :]) ** 2, axis=2)
        minimum_squared = float(squared.min())
        if minimum_squared <= cutoff ** 2:
            output.append({**residue['id'], 'minimum_ligand_distance_angstrom': math.sqrt(minimum_squared),
                           'heavy_atom_count': len(residue['atoms'])})
    if not output:
        raise ValueError('Reference contact set is empty')
    return output


def centroid(atoms):
    if not atoms:
        raise ValueError('Cannot calculate centroid of empty atom set')
    # Stable fixed ordering at caller; fsum reduces accumulation error.
    return [math.fsum(a['xyz'][axis] for a in atoms) / len(atoms) for axis in range(3)]


def align_sequences(holo_seq, apo_seq, scores):
    aligner = PairwiseAligner(mode='global')
    aligner.match_score = scores['match']
    aligner.mismatch_score = scores['mismatch']
    aligner.open_gap_score = scores['open_gap']
    aligner.extend_gap_score = scores['extend_gap']
    alignments = iter(aligner.align(holo_seq, apo_seq))
    alignment = next(alignments)
    if next(alignments, None) is not None:
        raise ValueError('Ambiguous optimal sequence alignment; human review required')
    pairs = []
    for h, a in alignment.indices.T:
        hp, ap = int(h) + 1 if h >= 0 else None, int(a) + 1 if a >= 0 else None
        identical = hp is not None and ap is not None and holo_seq[hp - 1] == apo_seq[ap - 1]
        pairs.append({'holo_label_seq_id': hp, 'apo_label_seq_id': ap,
                      'holo_aa': holo_seq[hp - 1] if hp else None,
                      'apo_aa': apo_seq[ap - 1] if ap else None, 'identical': identical})
    return {'method': 'unique global affine-gap alignment of full deposited polymer sequences',
            'scores': scores, 'score': float(alignment.score), 'optimal_alignment_count': 1,
            'holo_sequence': holo_seq, 'apo_sequence': apo_seq, 'positions': pairs}


def map_reference(reference, alignment, apo_residues):
    by_holo = {p['holo_label_seq_id']: p for p in alignment['positions'] if p['holo_label_seq_id']}
    mapped, unmapped = [], []
    for ref in reference:
        pair = by_holo[ref['label_seq_id']]
        ap = pair['apo_label_seq_id']
        if ap is None:
            reason = 'alignment_gap_in_apo'
        elif not pair['identical']:
            reason = 'amino_acid_mismatch'
        elif ap not in apo_residues:
            reason = 'apo_coordinates_missing'
        else:
            mapped.append({'holo': ref, 'apo': apo_residues[ap]['id']})
            continue
        unmapped.append({'holo': ref, 'apo_label_seq_id': ap, 'reason': reason})
    return mapped, unmapped


def missing_positions(cif, chain, seq, residues):
    scheme = {int(r['seq_id']): r for r in rows(cif, '_pdbx_poly_seq_scheme')
              if r['asym_id'] == chain}
    return [{'label_seq_id': i, 'amino_acid': seq[i - 1],
             'sequence_scheme': scheme.get(i)} for i in range(1, len(seq) + 1) if i not in residues]


def evaluate(holo_cif, apo_cif, config):
    if scalar(holo_cif, '_entry.id').upper() != config['holo_pdb_id']:
        raise ValueError('Wrong holo entry identifier')
    if scalar(apo_cif, '_entry.id').upper() != config['apo_pdb_id']:
        raise ValueError('Wrong apo entry identifier')
    hs, hr = protein(holo_cif, config['holo_label_chain'], config['model_number'])
    aps, ar = protein(apo_cif, config['apo_label_chain'], config['model_number'])
    lig = ligand(holo_cif, config)
    ref = contacts(hr, lig['atoms'], config['contact_cutoff_angstrom'])
    alignment = align_sequences(hs, aps, config['alignment'])
    mapped, unmapped = map_reference(ref, alignment, ar)
    if not mapped:
        raise ValueError('No reference residues map to apo coordinates')
    holo_atoms = [atom for r in ref for atom in hr[r['label_seq_id']]['atoms']]
    apo_atoms = [atom for r in mapped for atom in ar[r['apo']['label_seq_id']]['atoms']]
    warnings = [
        '1LXL is one minimized-average NMR model, not an experimental ensemble.',
        '2YXJ is a 2.20 A crystal structure; NMR/crystal and construct differences confound comparison.',
        'Primary reference uses chain A and N3C label chain D; chain B and symmetry contacts excluded.',
        'Ligand absence does not establish crypticity; no pocket detection or method performance computed.',
        'Coordinate-based reference omits unobserved atoms and residues; none rebuilt.',
        'Centroids are in different original coordinate frames and cannot be directly subtracted.'
    ]
    hm = missing_positions(holo_cif, config['holo_label_chain'], hs, hr)
    am = missing_positions(apo_cif, config['apo_label_chain'], aps, ar)
    if hm:
        warnings.append(f'{len(hm)} deposited holo chain A residues have no selected heavy-atom coordinates.')
    if am:
        warnings.append(f'{len(am)} deposited apo chain A residues have no selected heavy-atom coordinates.')
    if unmapped:
        warnings.append(f'{len(unmapped)} reference residues could not be mapped to apo coordinates.')
    alt = {'holo_protein': [{'residue': r['id'], **r['alternate_locations']} for r in hr.values()
                            if r['alternate_locations']['available_alt_ids']],
           'apo_protein': [{'residue': r['id'], **r['alternate_locations']} for r in ar.values()
                           if r['alternate_locations']['available_alt_ids']],
           'ligand': lig['alternate_locations']}
    return {
        'schema_version': 1, 'holo_pdb_id': config['holo_pdb_id'], 'apo_pdb_id': config['apo_pdb_id'],
        'ligand_id': config['ligand_comp_id'], 'ligand_selection': lig['id'],
        'ligand_heavy_atom_count': len(lig['atoms']),
        'contact_cutoff_angstrom': config['contact_cutoff_angstrom'],
        'holo_reference_residues': ref, 'apo_mapped_residues': mapped, 'unmapped_residues': unmapped,
        'mapping_method': alignment['method'], 'alignment': alignment,
        'mapping_coverage': len(mapped) / len(ref),
        'reference_centroid': centroid(holo_atoms), 'reference_centroid_frame': '2YXJ original model 1',
        'reference_centroid_definition': 'unweighted mean of all selected heavy atoms of reference protein residues',
        'reference_centroid_atom_count': len(holo_atoms),
        'apo_reference_centroid': centroid(apo_atoms), 'apo_reference_centroid_frame': '1LXL original model 1',
        'apo_reference_centroid_atom_count': len(apo_atoms), 'holo_ligand_centroid': centroid(lig['atoms']),
        'missing_coordinate_residues': {'holo': hm, 'apo': am},
        'polymer_lengths': {'holo': len(hs), 'apo': len(aps)},
        'observed_residue_counts': {'holo': len(hr), 'apo': len(ar)},
        'alternate_locations': alt, 'warnings': warnings}
