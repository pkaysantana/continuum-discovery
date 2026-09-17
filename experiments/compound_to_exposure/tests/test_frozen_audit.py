"""Read-only regressions against the independently reviewed commit and raw bytes."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
import subprocess
import unittest
from unittest.mock import patch

from rdkit import Chem
import audit
import provenance

BASELINE = '13715550adad0a628e92da6cf34568000ddbc797'


def original(relative):
    return subprocess.check_output(
        ['git', 'show', f'{BASELINE}:experiments/compound_to_exposure/{relative}'], cwd=audit.ROOT)


class FrozenAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = {}
        with patch.object(audit, 'write_outputs', side_effect=cls.outputs.update), redirect_stdout(io.StringIO()):
            audit.audit()
        cls.report = json.loads(cls.outputs['reports/DATA_AUDIT.json'])

    def test_all_original_report_results_unchanged(self):
        current = deepcopy(self.report)
        species = current['tdc_hepatocyte_species_audit']
        species['INFERRED'].pop('strict_duplicate_pair_rule')
        counts = species['OBSERVED']['duplicate_trace_groups']
        counts['partial_or_unresolved'] = counts.pop('no_strict_structural_match_to_either_assay')
        self.assertEqual(current, json.loads(original('reports/DATA_AUDIT.json')))

    def test_strict_pair_and_microsome_counts(self):
        species = self.report['tdc_hepatocyte_species_audit']['OBSERVED']
        self.assertEqual(species['duplicate_trace_groups'], {
            'distinct_labels_match_rat_and_human': 187,
            'no_strict_structural_match_to_either_assay': 6})
        self.assertEqual(self.report['tdc_microsome_reconciliation']['OBSERVED']['structure_overlap'], 1097)

    def test_all_other_derived_outputs_byte_identical(self):
        amended = {'reports/DATA_AUDIT.json', 'reports/DATA_AUDIT.md',
                   'reports/TDC_HEPATOCYTE_SPECIES_AUDIT.md',
                   'data/interim/TDC_HEPATOCYTE_DUPLICATE_LABELS.json'}
        for relative, content in self.outputs.items():
            if relative not in amended:
                with self.subTest(relative=relative):
                    self.assertEqual(content, original(relative))

    def test_duplicate_evidence_changes_only_six_class_names(self):
        current = json.loads(self.outputs['data/interim/TDC_HEPATOCYTE_DUPLICATE_LABELS.json'])
        changed = 0
        for group in current['OBSERVED']:
            if group['trace_class'] == 'no_strict_structural_match_to_either_assay':
                self.assertEqual(len(group['rows']), 2)
                self.assertTrue(all(r['structure_species_class'] == 'neither' for r in group['rows']))
                group['trace_class'] = 'partial_or_unresolved'
                changed += 1
        self.assertEqual(changed, 6)
        self.assertEqual(current, json.loads(original('data/interim/TDC_HEPATOCYTE_DUPLICATE_LABELS.json')))

    def test_raw_hashes_sizes_and_receipts_unchanged(self):
        manifest = json.loads(original('manifests/source_manifest.json'))
        actual = {p.relative_to(audit.ROOT).as_posix() for p in (audit.ROOT / 'data/raw').rglob('*') if p.is_file()}
        self.assertEqual(actual, {r['filename'] for r in manifest['sources']})
        self.assertEqual(len(actual), 18)
        for item in manifest['sources']:
            with self.subTest(filename=item['filename']):
                provenance.verify(item)
                relative = item['filename'].removeprefix('data/raw/')
                receipt_name = 'manifests/downloads/' + relative.replace('/', '__') + '.json'
                self.assertEqual((audit.ROOT / receipt_name).read_bytes(), original(receipt_name))

    def test_microsome_tautomer_and_hydrate_evidence(self):
        details = self.report['tdc_microsome_reconciliation']['secondary_id_audit']['OBSERVED']['strict_structure_unmatched_details']
        expected = {'CHEMBL82663': '111.0', 'CHEMBL1483': '34.67',
                    'CHEMBL412142': '96.0', 'CHEMBL1513': '17.78', 'CHEMBL190': '4.79'}
        self.assertEqual({d['tdc_id'] for d in details}, set(expected))
        for detail in details:
            with self.subTest(molecule=detail['tdc_id']):
                hydrate = detail['tdc_id'] == 'CHEMBL190'
                candidates = detail['chembl_declared_parent_id_candidates'] if hydrate else detail['exact_id_candidates']
                self.assertEqual(len(candidates), 1)
                candidate = candidates[0]
                self.assertEqual(candidate['identifier'], 'CHEMBL1355736' if hydrate else detail['tdc_id'])
                self.assertTrue(audit.numeric_equal(detail['tdc_value'], expected[detail['tdc_id']]))
                self.assertTrue(audit.numeric_equal(detail['tdc_value'], candidate['target']))
                left, right = detail['tdc_canonical_smiles_rdkit'], candidate['canonical_smiles_rdkit']
                self.assertNotEqual(left, right)
                keys = [Chem.MolToInchiKey(Chem.MolFromSmiles(s)) for s in (left, right)]
                self.assertTrue(all(keys))
                self.assertEqual(keys[0] == keys[1], not hydrate)
                if hydrate:
                    self.assertEqual(candidate['parent_molecule_chembl_id'], 'CHEMBL190')
                    self.assertIn('O', right.split('.'))

    def test_null_relations_at_boundaries_and_rat_records(self):
        for assay, expected in ((audit.HLM, 13), (audit.RAT, 2), (audit.HH, 0)):
            rows = [r for p in (audit.ROOT / 'data/raw/chembl').glob(f'{assay}_activities_*.json')
                    for r in json.loads(p.read_text())['activities'] if r['standard_relation'] is None]
            lower = [r for r in rows if audit.numeric_equal(r['standard_value'], '3')]
            self.assertEqual(len(lower), expected)
            self.assertFalse(any(audit.numeric_equal(r['standard_value'], '150') for r in rows))
            if assay == audit.RAT:
                self.assertEqual({(r['activity_id'], r['molecule_chembl_id']) for r in lower},
                                 {(14768823, 'CHEMBL589973'), (14768825, 'CHEMBL364714')})
