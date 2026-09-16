"""Synthetic geometry tests plus immutable-input integration checks. No detectors."""
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from Bio.PDB.MMCIF2Dict import MMCIF2Dict

from provenance import ROOT, canonical_bytes, file_record, sha256, verify_record, write_once
from reference_site import (align_sequences, centroid, contacts, evaluate, ligand, load_cif,
                            map_reference, missing_positions, protein, selected_heavy_atoms)

SCORES = {'match': 2.0, 'mismatch': -1.0, 'open_gap': -10.0, 'extend_gap': -0.5}
CFG = {'ligand_comp_id': 'N3C', 'ligand_label_chain': 'D', 'ligand_auth_chain': 'A',
       'ligand_synonym': 'ABT-737', 'model_number': '1'}


def atom(chain='A', seq='1', comp='ALA', name='CA', xyz=(0, 0, 0), element='C',
         entity='1', auth='101', ins='?', alt='.', occupancy='1.0', model='1'):
    return dict(label_asym_id=chain, label_seq_id=seq, label_comp_id=comp,
                label_atom_id=name, Cartn_x=str(xyz[0]), Cartn_y=str(xyz[1]), Cartn_z=str(xyz[2]),
                type_symbol=element, label_entity_id=entity, auth_seq_id=auth,
                auth_asym_id='A', pdbx_PDB_ins_code=ins, label_alt_id=alt,
                occupancy=occupancy, pdbx_PDB_model_num=model, group_PDB='ATOM' if entity == '1' else 'HETATM')


def category(cif, prefix, records):
    for key in records[0]:
        cif[prefix + '.' + key] = [r[key] for r in records]


def mock_cif(atoms=None):
    cif = {'data_': 'mock'}
    category(cif, '_struct_asym', [{'id': 'A', 'entity_id': '1'}])
    category(cif, '_entity_poly', [{'entity_id': '1', 'type': 'polypeptide(L)'}])
    category(cif, '_entity_poly_seq', [{'entity_id': '1', 'num': '1', 'mon_id': 'ALA'},
                                      {'entity_id': '1', 'num': '2', 'mon_id': 'GLY'}])
    category(cif, '_entity', [{'id': '1', 'type': 'polymer'}, {'id': '2', 'type': 'non-polymer'},
                              {'id': '3', 'type': 'water'}])
    category(cif, '_chem_comp', [{'id': 'N3C', 'pdbx_synonyms': 'ABT-737'}])
    if atoms is None:
        atoms = [atom(), atom(seq='2', comp='GLY', xyz=(10, 0, 0), auth='105', ins='A'),
                 atom(chain='D', seq='.', comp='N3C', xyz=(3, 0, 0), entity='2', auth='1001')]
    category(cif, '_atom_site', atoms)
    return cif


class LigandTests(unittest.TestCase):
    def test_exact_ligand_instance_selection(self):
        cif = mock_cif()
        selected = ligand(cif, CFG)
        self.assertEqual(selected['id']['label_chain'], 'D')
        self.assertEqual(selected['id']['auth_seq_id'], '1001')
        self.assertEqual(len(selected['atoms']), 1)

    def test_missing_ligand_fails_gracefully(self):
        with self.assertRaisesRegex(ValueError, 'absent'):
            ligand(mock_cif([atom()]), CFG)

    def test_wrong_ligand_synonym_fails(self):
        cif = mock_cif()
        cif['_chem_comp.pdbx_synonyms'] = ['OTHER']
        with self.assertRaisesRegex(ValueError, 'metadata'):
            ligand(cif, CFG)

    def test_duplicate_ligand_instances_fail(self):
        cif = mock_cif([atom(chain='D', seq='.', comp='N3C', entity='2', auth=str(i)) for i in (1001, 1002)])
        with self.assertRaisesRegex(ValueError, 'Multiple ligand'):
            ligand(cif, CFG)

    def test_other_ligand_chain_not_selected(self):
        cif = mock_cif([atom(chain='F', seq='.', comp='N3C', entity='2')])
        with self.assertRaisesRegex(ValueError, 'absent'):
            ligand(cif, CFG)

    def test_polymer_cannot_be_selected_as_ligand(self):
        cif = mock_cif([atom(chain='D', seq='.', comp='N3C', entity='1')])
        with self.assertRaisesRegex(ValueError, 'nonpolymer'):
            ligand(cif, CFG)


class GeometryTests(unittest.TestCase):
    def test_heavy_atom_contact_residue_extraction(self):
        cif = mock_cif()
        _, residues = protein(cif, 'A')
        result = contacts(residues, ligand(cif, CFG)['atoms'], 5.0)
        self.assertEqual([r['label_seq_id'] for r in result], [1])
        self.assertEqual(result[0]['minimum_ligand_distance_angstrom'], 3.0)

    def test_inclusive_cutoff_and_just_outside(self):
        cif = mock_cif([atom(xyz=(5, 0, 0)), atom(seq='2', comp='GLY', xyz=(5.000001, 0, 0))])
        _, residues = protein(cif, 'A')
        self.assertEqual([r['label_seq_id'] for r in contacts(residues, [{'xyz': (0, 0, 0)}], 5.0)], [1])

    def test_waters_ions_and_nonpolymer_amino_acids_excluded(self):
        cif = mock_cif([atom(), atom(chain='W', seq='.', comp='HOH', name='O', element='O', entity='3'),
                        atom(chain='I', seq='.', comp='CL', name='CL', element='CL', entity='2'),
                        atom(chain='X', seq='.', comp='GLY', entity='2')])
        seq, residues = protein(cif, 'A')
        self.assertEqual(seq, 'AG')
        self.assertEqual(list(residues), [1])

    def test_hydrogen_deuterium_and_zero_occupancy_excluded(self):
        selected, _ = selected_heavy_atoms([
            atom(name='H1', element='H'), atom(name='D1', element='D'),
            atom(name='CB', occupancy='0'), atom(name='CL', element='Cl')])
        self.assertEqual([a['element'] for a in selected], ['CL'])

    def test_hydrogen_alone_does_not_create_contact(self):
        cif = mock_cif([atom(xyz=(9, 0, 0)), atom(name='H', element='H', xyz=(0, 0, 0))])
        _, residues = protein(cif, 'A')
        with self.assertRaisesRegex(ValueError, 'empty'):
            contacts(residues, [{'xyz': (0, 0, 0)}], 5)

    def test_altloc_occupancy_selection_is_coherent(self):
        selected, details = selected_heavy_atoms([
            atom(name='N'), atom(name='CA', alt='A', occupancy='0.4', xyz=(1, 0, 0)),
            atom(name='CA', alt='B', occupancy='0.6', xyz=(9, 0, 0))])
        self.assertEqual(details['selected_alt_id'], 'B')
        self.assertEqual({a['name']: a['xyz'][0] for a in selected}, {'CA': 9.0, 'N': 0.0})

    def test_altloc_tie_is_lexical(self):
        selected, details = selected_heavy_atoms([
            atom(alt='B', occupancy='0.5'), atom(alt='A', occupancy='0.5')])
        self.assertEqual(details['selected_alt_id'], 'A')
        self.assertEqual(len(selected), 1)

    def test_nan_coordinates_fail(self):
        with self.assertRaisesRegex(ValueError, 'Invalid'):
            selected_heavy_atoms([atom(xyz=(float('nan'), 0, 0))])

    def test_centroid_is_atom_weighted_arithmetic_mean(self):
        self.assertEqual(centroid([{'xyz': (0, 0, 0)}, {'xyz': (3, 6, 9)}, {'xyz': (6, 0, 0)}]), [3, 2, 3])

    def test_empty_centroid_fails(self):
        with self.assertRaisesRegex(ValueError, 'empty'):
            centroid([])

    def test_model_selection(self):
        cif = mock_cif([atom(xyz=(1, 0, 0)), atom(xyz=(99, 0, 0), model='2')])
        _, residues = protein(cif, 'A')
        self.assertEqual(residues[1]['atoms'][0]['xyz'][0], 1)


class MappingTests(unittest.TestCase):
    def test_mapping_uses_sequence_not_author_numbers(self):
        _, residues = protein(mock_cif(), 'A')
        alignment = align_sequences('AG', 'AG', SCORES)
        mapped, unmapped = map_reference([{'label_seq_id': 2, 'auth_seq_id': '999'}], alignment, residues)
        self.assertEqual(mapped[0]['apo']['auth_seq_id'], '105')
        self.assertEqual(mapped[0]['apo']['insertion_code'], 'A')
        self.assertEqual(unmapped, [])

    def test_construct_deletion_recorded(self):
        alignment = align_sequences('ACDEFGHIK', 'ACDGHIK', SCORES)
        _, unmapped = map_reference([{'label_seq_id': 4}], alignment, {})
        self.assertEqual(unmapped[0]['reason'], 'alignment_gap_in_apo')

    def test_missing_coordinates_do_not_change_alignment(self):
        alignment = align_sequences('AG', 'AG', SCORES)
        _, residues = protein(mock_cif([atom()]), 'A')
        _, unmapped = map_reference([{'label_seq_id': 2}], alignment, residues)
        self.assertEqual(unmapped[0]['reason'], 'apo_coordinates_missing')
        self.assertEqual(unmapped[0]['apo_label_seq_id'], 2)

    def test_mismatches_are_unmapped(self):
        alignment = align_sequences('ACD', 'AED', SCORES)
        _, unmapped = map_reference([{'label_seq_id': 2}], alignment, {})
        self.assertEqual(unmapped[0]['reason'], 'amino_acid_mismatch')

    def test_ambiguous_alignment_fails(self):
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            align_sequences('AA', 'A', SCORES)

    def test_missing_position_reporting(self):
        cif = mock_cif([atom()])
        seq, residues = protein(cif, 'A')
        missing = missing_positions(cif, 'A', seq, residues)
        self.assertEqual([r['label_seq_id'] for r in missing], [2])


class ProvenanceAndIntegrationTests(unittest.TestCase):
    def test_manifest_known_hash_and_tamper_detection(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'results/tmp') as directory:
            root = Path(directory)
            path = root / 'mock.cif'
            path.write_bytes(b'abc')
            self.assertEqual(sha256(path), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
            record = file_record(path, root)
            verify_record(record, root)
            path.write_bytes(b'abd')
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                verify_record(record, root)

    def test_raw_write_cannot_replace_existing_bytes(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'results/tmp') as directory:
            path = Path(directory) / 'mock.cif'
            write_once(path, b'first')
            write_once(path, b'first')
            with self.assertRaisesRegex(ValueError, 'Refusing'):
                write_once(path, b'second')
            self.assertEqual(path.read_bytes(), b'first')

    def test_mock_mmcif_text_round_trip(self):
        cif = mock_cif()
        text = 'data_mock\n'
        categories = sorted({k.split('.')[0] for k in cif if k != 'data_'})
        for prefix in categories:
            keys = [k for k in cif if k.startswith(prefix + '.')]
            text += 'loop_\n' + '\n'.join(keys) + '\n'
            for vals in zip(*(cif[k] for k in keys)):
                text += ' '.join(vals) + '\n'
            text += '#\n'
        parsed = MMCIF2Dict(io.StringIO(text))
        seq, residues = protein(parsed, 'A')
        self.assertEqual(seq, 'AG')
        self.assertEqual(len(residues), 2)
        self.assertEqual(ligand(parsed, CFG)['id']['auth_seq_id'], '1001')

    def test_real_inputs_match_manifests(self):
        manifest = json.loads((ROOT / 'manifests/input_manifest.json').read_text())
        self.assertEqual([r['pdb_id'] for r in manifest['structures']], ['1LXL', '2YXJ'])
        for record in manifest['structures']:
            verify_record(record)

    def test_real_evaluation_repeatable_and_matches_saved_output(self):
        cfg = json.loads((ROOT / 'configs/reference_site.json').read_text())
        holo, apo = load_cif(ROOT / 'data/raw/2YXJ.cif'), load_cif(ROOT / 'data/raw/1LXL.cif')
        first = evaluate(holo, apo, cfg)
        # Reverse atom-row order to check independence from parser iteration order.
        reordered = deepcopy(holo)
        for key in reordered:
            if key.startswith('_atom_site.'):
                reordered[key] = list(reversed(reordered[key]))
        second = evaluate(reordered, apo, cfg)
        self.assertEqual(canonical_bytes(first), canonical_bytes(second))
        saved = json.loads((ROOT / 'data/processed/reference_site.json').read_text())
        saved.pop('provenance')
        self.assertEqual(first, saved)
        self.assertGreater(len(first['holo_reference_residues']), 0)
        self.assertEqual(len(first['holo_reference_residues']),
                         len(first['apo_mapped_residues']) + len(first['unmapped_residues']))


if __name__ == '__main__':
    raise SystemExit('Run via src/run.py test to capture provenance.')
