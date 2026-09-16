import json
from copy import deepcopy
import io
import unittest
import numpy as np
from Bio.PDB import PDBParser
from provenance import ROOT, canonical_bytes, verify_record
from reference_site import align_sequences, load_cif, protein
from matched_core import expression_tags, pdb_bytes, retain_bfactors, select_core
from comparison_metrics import candidate_metrics
from test_reference_site import SCORES, atom, mock_cif


class MatchedCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hc, cls.ac = load_cif(ROOT / 'data/raw/2YXJ.cif'), load_cif(ROOT / 'data/raw/1LXL.cif')
        hs, cls.hr = protein(cls.hc, 'A'); aps, cls.ar = protein(cls.ac, 'A')
        retain_bfactors(cls.hc, cls.hr); retain_bfactors(cls.ac, cls.ar)
        cls.alignment = align_sequences(hs, aps, SCORES)
        cls.retained, cls.excluded = select_core(cls.alignment, cls.hr, cls.ar,
                                                expression_tags(cls.hc, 'A'), expression_tags(cls.ac, 'A'))

    def test_real_common_core_and_complete_accounting(self):
        self.assertEqual(len(self.retained), 137)
        self.assertEqual(len(self.retained) + len(self.excluded['apo']), 221)
        self.assertEqual(len(self.retained) + len(self.excluded['holo']), 181)
        for state, length in [('apo', 221), ('holo', 181)]:
            ids = [r[state]['label_seq_id'] for r in self.retained] + [r['label_seq_id'] for r in self.excluded[state]]
            self.assertEqual(sorted(ids), list(range(1, length + 1)))

    def test_manifest_and_output_hashes(self):
        manifest = json.loads((ROOT / 'data/processed/matched_core_manifest.json').read_text())
        self.assertEqual(manifest['retained_residues'], self.retained)
        self.assertEqual(manifest['excluded_residues'], self.excluded)
        for record in manifest['raw_inputs'] + manifest['processed_outputs']:
            verify_record(record)

    def test_pdb_round_trip_preserves_atoms_coordinates_occupancy_bfactor(self):
        for state, residues in [('holo', self.hr), ('apo', self.ar)]:
            text = pdb_bytes(residues, self.retained, state).decode()
            parsed = PDBParser(PERMISSIVE=False, QUIET=True).get_structure('core', io.StringIO(text))
            chain = parsed[0]['A']
            self.assertEqual(len(chain), 137)
            for match in self.retained:
                observed = chain[match['output_resseq']]
                source = residues[match[state]['label_seq_id']]
                self.assertEqual(len(observed), len(source['atoms']))
                for at in source['atoms']:
                    copied = observed[at['name']]
                    np.testing.assert_allclose(copied.coord, at['xyz'], atol=1e-5, rtol=0)
                    self.assertEqual(copied.occupancy, at['occupancy'])
                    self.assertEqual(copied.bfactor, at['bfactor'])

    def test_output_contains_only_core_protein(self):
        text = pdb_bytes(self.hr, self.retained, 'holo').decode()
        self.assertNotIn('HETATM', text)
        self.assertNotIn('N3C', text)
        self.assertNotIn('HOH', text)
        self.assertGreater(text.count('\nTER\n'), 1)
        self.assertTrue(all(line[76:78].strip() not in ('H', 'D') for line in text.splitlines() if line.startswith('ATOM')))

    def test_serialized_output_is_repeatable(self):
        for state, residues, filename in [('apo', self.ar, 'apo_matched_core.pdb'), ('holo', self.hr, 'holo_matched_core_no_ligand.pdb')]:
            content = pdb_bytes(residues, self.retained, state)
            self.assertEqual(content, pdb_bytes(deepcopy(residues), deepcopy(self.retained), state))
            self.assertEqual(content, (ROOT / 'data/processed' / filename).read_bytes())

    def test_tags_excluded_even_if_observed_in_both(self):
        kept, excluded = select_core(self.alignment, self.hr, self.ar, {self.retained[0]['holo']['label_seq_id']}, set())
        self.assertEqual(len(kept), 136)
        self.assertTrue(any('expression_tag_annotation' in r['reasons'] for r in excluded['holo']))

    def test_missing_backbone_excludes_both_counterparts(self):
        changed = deepcopy(self.hr)
        h = self.retained[0]['holo']['label_seq_id']
        changed[h]['atoms'] = [a for a in changed[h]['atoms'] if a['name'] != 'CA']
        kept, excluded = select_core(self.alignment, changed, self.ar)
        self.assertEqual(len(kept), 136)
        self.assertTrue(any('holo_incomplete_backbone' in r['reasons'] for r in excluded['apo']))

    def test_selection_independent_of_pocket_or_coordinate_location(self):
        moved = deepcopy(self.hr)
        for r in moved.values():
            for a in r['atoms']:
                a['xyz'] = (10000, 20000, 30000)
        kept, excluded = select_core(self.alignment, moved, self.ar,
                                     expression_tags(self.hc, 'A'), expression_tags(self.ac, 'A'))
        self.assertEqual(kept, self.retained)
        self.assertEqual(excluded, self.excluded)

    def test_all_reference_sets_retained_and_CA_centroids_correct(self):
        result = json.loads((ROOT / 'data/processed/comparison_reference.json').read_text())
        for cutoff, count in [('5.0', 24), ('4.5', 22), ('4.0', 19)]:
            ref = result['cutoffs'][cutoff]
            self.assertEqual(ref['residue_count'], count)
            self.assertTrue(set(ref['output_residue_ids']) <= {r['output_resseq'] for r in self.retained})
            for state, residues in [('apo', self.ar), ('holo', self.hr)]:
                coordinates = [a['xyz'] for r in self.retained if r['output_resseq'] in ref['output_residue_ids']
                               for a in residues[r[state]['label_seq_id']]['atoms'] if a['name'] == 'CA']
                np.testing.assert_allclose(ref[state + '_reference_centroid_CA'], np.mean(coordinates, axis=0))


class PrimaryMetricTests(unittest.TestCase):
    def test_four_angstrom_boundary_is_inclusive(self):
        self.assertTrue(candidate_metrics((4, 0, 0), (0, 0, 0), [], [1])['recovered'])
        self.assertFalse(candidate_metrics((4.000001, 0, 0), (0, 0, 0), [1], [1])['recovered'])

    def test_jaccard_is_not_a_success_gate(self):
        self.assertTrue(candidate_metrics((0, 0, 0), (0, 0, 0), [99], [1])['recovered'])
        self.assertFalse(candidate_metrics((9, 0, 0), (0, 0, 0), [1], [1])['recovered'])

    def test_recall_precision_and_jaccard_have_distinct_denominators(self):
        m = candidate_metrics((1, 0, 0), (0, 0, 0), [1, 2, 3, 4], [1, 2, 5])
        self.assertEqual(m['reference_site_recall'], 2/3)
        self.assertEqual(m['predicted_site_precision'], 2/4)
        self.assertEqual(m['jaccard'], 2/5)

    def test_invalid_center_fails_without_fallback(self):
        with self.assertRaisesRegex(ValueError, 'finite'):
            candidate_metrics((float('nan'), 0, 0), (0, 0, 0), [1], [1])

    def test_centroid_distance_translation_invariant(self):
        self.assertEqual(candidate_metrics((1, 2, 3), (4, 5, 6), [1], [1]),
                         candidate_metrics((101, 102, 103), (104, 105, 106), [1], [1]))
