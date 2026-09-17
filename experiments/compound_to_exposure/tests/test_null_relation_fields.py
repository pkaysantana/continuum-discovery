"""Field-only tests. Run separately: the old chemistry suite calculates descriptors."""
from copy import deepcopy
import json
import unittest

import null_relation_fields as fields


def row(activity_id=1, relation=None, standard_relation=None, value='3.0', standard_value='3.0'):
    return {'activity_id': activity_id, 'relation': relation, 'standard_relation': standard_relation,
            'value': value, 'standard_value': standard_value, 'standard_flag': 1,
            'units': 'microL/min/mg', 'standard_units': 'mL.min-1.g-1'}


class FieldLogicTests(unittest.TestCase):
    def test_null_missing_and_empty_remain_distinct(self):
        self.assertEqual(fields.category({}, 'relation'), 'MISSING_FIELD')
        self.assertEqual(fields.category({'relation': None}, 'relation'), 'NULL')
        self.assertEqual(fields.category({'relation': ''}, 'relation'), '')
        self.assertEqual(fields.category({'relation': '='}, 'relation'), '=')

    def test_crosstab_detects_both_directions_of_qualifier_change(self):
        records = [row(1, '=', None), row(2, None, '='), row(3, '<', '>'), row(4)]
        result = fields.audit_rows(records)
        self.assertEqual(result['relation_crosstab']['=']['NULL'], 1)
        self.assertEqual(result['relation_crosstab']['NULL']['='], 1)
        self.assertEqual(result['relation_crosstab']['<']['>'], 1)
        self.assertEqual(result['relation_crosstab']['NULL']['NULL'], 1)

    def test_boundaries_are_exact_and_independent_of_relation(self):
        expected = {'2.999999999999': 'below_3', '3.00': 'exactly_3', '3.000000000001': 'between_3_and_150',
                    '150': 'exactly_150', '150.000000000001': 'above_150', 'NaN': 'non_numeric',
                    'Infinity': 'non_numeric', None: 'non_numeric', '<3': 'non_numeric'}
        for value, category in expected.items():
            with self.subTest(value=value):
                self.assertEqual(fields.bucket(value), category)
        records = [row(1, '<', None, '3', '150')]
        result = fields.audit_rows(records)['boundary_activity_ids_by_value_field_and_both_relations']
        self.assertEqual(result['value']['<']['NULL']['exactly_3'], [1])
        self.assertEqual(result['standard_value']['<']['NULL']['exactly_150'], [1])

    def test_precision_changes_are_not_hidden_by_numeric_equality(self):
        result = fields.compare_values([row(value='3.000', standard_value='3.0')])
        self.assertEqual(result['exact_numeric_equal'], 1)
        self.assertEqual(result['different_value_strings'], 1)
        self.assertEqual(result['different_decimal_exponents'], 1)
        self.assertEqual(fields.compare_values([row(standard_value='3.00000001')])['exact_numeric_equal'], 0)

    def test_comments_include_every_distinct_value_and_frequency(self):
        values = [None, '', 'NA', 'NA', '<3 below range', 'assay failed', 'inactive', 'unexpected text']
        result = fields.frequencies([{'text_value': v} for v in values] + [{}], 'text_value')
        self.assertEqual(result['missing_field'], 1)
        actual = {p['value']: p['count'] for p in result['values']}
        self.assertEqual(actual, {None: 1, '': 1, 'NA': 2, '<3 below range': 1, 'assay failed': 1,
                                  'inactive': 1, 'unexpected text': 1})

    def test_field_analysis_never_mutates_records(self):
        records = [row(), row(2, '<', '<')]
        original = deepcopy(records)
        fields.audit_rows(records)
        self.assertEqual(records, original)


class FrozenFieldEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = fields.build_report()

    def test_every_requested_field_and_raw_record_is_preserved(self):
        self.assertEqual(self.report['raw_files_verified'], 18)
        self.assertEqual(self.report['chembl_api_state']['chembl_db_version'], 'ChEMBL_37')
        pages = {}
        for assay, result in self.report['assays'].items():
            for extracted in result['records']:
                path = fields.ROOT / extracted['raw_filename']
                if path not in pages:
                    pages[path] = json.loads(path.read_bytes())['activities']
                raw = pages[path][extracted['row_in_page_1based'] - 1]
                self.assertEqual(extracted['fields_absent_from_raw'], [])
                self.assertEqual({f: extracted[f] for f in fields.FIELDS}, {f: raw[f] for f in fields.FIELDS})
            self.assertTrue(all(v['missing'] == 0 for v in result['field_availability'].values()))

    def test_all_relation_classes_and_flags(self):
        for assay, expected in zip(fields.ASSAYS, ((274, 84, 744), (115, 127, 595), (104, 15, 289))):
            result = self.report['assays'][assay]
            counts = dict(zip(('<', '>', 'NULL'), expected))
            for raw in fields.CLASSES:
                for standard in fields.CLASSES:
                    self.assertEqual(result['relation_crosstab'][raw][standard], counts.get(raw, 0) if raw == standard else 0)
            for r in result['records']:
                self.assertEqual(r['standard_flag'], 1)
                self.assertEqual(r['potential_duplicate'], 0)
                for f in (*fields.TEXT_FIELDS, 'data_validity_description', 'upper_value', 'standard_upper_value',
                          'toid', 'document_journal', 'document_year'):
                    self.assertIsNone(r[f])
                self.assertEqual(r['activity_properties'], [])
                self.assertEqual((r['document_chembl_id'], r['src_id'], r['type'], r['standard_type']),
                                 ('CHEMBL3301361', 27, 'CLint', 'CL'))

    def test_boundaries_and_individual_null_records(self):
        expected_ids = (set(range(14769802, 14769815)), {14768823, 14768825}, set())
        for assay, ids in zip(fields.ASSAYS, expected_ids):
            result = self.report['assays'][assay]
            self.assertEqual({r['activity_id'] for r in result['null_boundary_records']}, ids)
            boundaries = result['boundary_activity_ids_by_value_field_and_both_relations']
            self.assertEqual(boundaries['value'], boundaries['standard_value'])
            self.assertEqual(set(boundaries['value']['NULL']['NULL']['exactly_3']), ids)
            for raw in fields.CLASSES:
                for standard in fields.CLASSES:
                    buckets = boundaries['value'][raw][standard]
                    for k in ('below_3', 'above_150', 'non_numeric'):
                        self.assertEqual(buckets[k], [])
            self.assertEqual(boundaries['value']['NULL']['NULL']['exactly_150'], [])
            all_ids = [i for cell in boundaries['value'].values() for buckets in cell.values()
                       for values in buckets.values() for i in values]
            self.assertEqual(len(all_ids), result['rows'])
            self.assertEqual(len(set(all_ids)), result['rows'])

    def test_values_and_units_match_report_claims(self):
        for assay, result in self.report['assays'].items():
            for r in result['records']:
                self.assertEqual(r['value'], r['standard_value'])
                self.assertIsNotNone(fields.decimal_value(r['value']))
                expected_units = ('microL/min/mg', 'mL.min-1.g-1') if assay == fields.ASSAYS[0] else (
                    'microL/min/1E6 cells', 'uL.min-1.(10^6cells)-1')
                self.assertEqual((r['units'], r['standard_units']), expected_units)

    def test_report_files_reproduce_exactly(self):
        self.assertEqual((fields.ROOT / 'reports/NULL_RELATION_FIELD_AUDIT.json').read_bytes(), fields.json_bytes(self.report))
        self.assertEqual((fields.ROOT / 'reports/NULL_RELATION_FIELD_AUDIT.md').read_text(encoding='utf-8'), fields.render(self.report))


if __name__ == '__main__':
    unittest.main()
