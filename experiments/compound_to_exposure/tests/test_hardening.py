"""Deterministic acquisition, provenance and output failure-path regressions."""
from copy import deepcopy
from http.client import IncompleteRead
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import acquire
import audit
import provenance
from chembl_pages import validate_pages
from test_audit import fixture


def page(ids, offset=0, total=3, terminal=False):
    return {'page_meta': {'total_count': total, 'offset': offset, 'limit': 2,
                         'next': None if terminal else f'/activity.json?offset={offset + len(ids)}&assay_chembl_id={audit.HLM}'},
            'activities': [{'activity_id': i, 'assay_chembl_id': audit.HLM} for i in ids]}


class PaginationTests(unittest.TestCase):
    def setUp(self):
        self.pages = [page([1, 2]), page([3], offset=2, terminal=True)]

    def test_complete_pagination_with_short_final_page(self):
        self.assertEqual(validate_pages(self.pages, audit.HLM), 3)

    def test_changing_total_count(self):
        self.pages[1]['page_meta']['total_count'] = 4
        with self.assertRaisesRegex(ValueError, 'count changed'):
            validate_pages(self.pages, audit.HLM)

    def test_empty_page(self):
        self.pages[1]['activities'] = []
        with self.assertRaisesRegex(ValueError, 'empty'):
            validate_pages(self.pages, audit.HLM)

    def test_early_terminal_page(self):
        self.pages[0]['page_meta']['next'] = None
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            validate_pages(self.pages[:1], audit.HLM)

    def test_missing_final_page(self):
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            validate_pages(self.pages[:1], audit.HLM)

    def test_interrupted_page_iterator_propagates_failure(self):
        def interrupted():
            yield self.pages[0]
            raise IncompleteRead(b'partial page')
        with self.assertRaises(IncompleteRead):
            validate_pages(interrupted(), audit.HLM)

    def test_incomplete_total_on_short_final_page(self):
        for p in self.pages:
            p['page_meta']['total_count'] = 4
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            validate_pages(self.pages, audit.HLM)

    def test_overfull_total(self):
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            validate_pages([page([1, 2], total=1, terminal=True)], audit.HLM)

    def test_repeated_activity_ids_within_and_across_pages(self):
        for pages in ([page([1, 1], total=2, terminal=True)],
                      [self.pages[0], page([2], offset=2, terminal=True)]):
            with self.subTest(pages=pages), self.assertRaisesRegex(ValueError, 'Repeated activity ID'):
                validate_pages(pages, audit.HLM)

    def test_wrong_assay(self):
        self.pages[1]['activities'][0]['assay_chembl_id'] = audit.RAT
        with self.assertRaisesRegex(ValueError, 'Wrong assay'):
            validate_pages(self.pages, audit.HLM)

    def test_noncontiguous_offset(self):
        self.pages[1]['page_meta']['offset'] = 3
        with self.assertRaisesRegex(ValueError, 'Noncontiguous'):
            validate_pages(self.pages, audit.HLM)

    def test_bad_next_link(self):
        self.pages[0]['page_meta']['next'] = '/activity.json?offset=1'
        with self.assertRaisesRegex(ValueError, 'next-page'):
            validate_pages(self.pages, audit.HLM)

    def test_nonterminal_final_page(self):
        self.pages[1]['page_meta']['next'] = '/activity.json?offset=3'
        with self.assertRaisesRegex(ValueError, 'nonterminal final'):
            validate_pages(self.pages, audit.HLM)

    def test_no_pages(self):
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            validate_pages([], audit.HLM)

    def test_page_after_terminal(self):
        with self.assertRaisesRegex(ValueError, 'follows terminal'):
            validate_pages([*self.pages, self.pages[1]], audit.HLM)

    def test_acquisition_requests_each_offset_and_uses_validator(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for i, content in enumerate([{}, {}, *self.pages]):
                path = Path(tmp) / f'{i}.json'
                path.write_text(json.dumps(content), encoding='utf-8')
                paths.append(path)
            with patch.object(acquire, 'ASSAYS', [audit.HLM]), patch.object(acquire, 'download', side_effect=paths) as download:
                acquire.chembl()
            self.assertEqual(download.call_count, 4)
            for call, offset in zip(download.call_args_list[2:], (0, 2)):
                self.assertIn(f'&offset={offset}&order_by=activity_id', call.args[0])
                self.assertEqual(call.args[1], f'chembl/{audit.HLM}_activities_{offset:05d}.json')
            bad = deepcopy(self.pages[0])
            bad['page_meta']['next'] = None
            paths[2].write_text(json.dumps(bad), encoding='utf-8')
            with patch.object(acquire, 'ASSAYS', [audit.HLM]), patch.object(acquire, 'download', side_effect=paths):
                with self.assertRaisesRegex(ValueError, 'incomplete'):
                    acquire.chembl()

    def test_audit_rejects_incomplete_stored_pages(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(audit, 'ROOT', Path(tmp)):
            folder = Path(tmp) / 'data/raw/chembl'
            folder.mkdir(parents=True)
            (folder / f'{audit.HLM}_assay.json').write_text('{}')
            (folder / f'{audit.HLM}_activities_00000.json').write_text(json.dumps(self.pages[0]))
            with self.assertRaisesRegex(ValueError, 'incomplete'):
                audit.load_sources()

    def test_audit_enforces_frozen_expected_count(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(audit, 'ROOT', Path(tmp)):
            folder = Path(tmp) / 'data/raw/chembl'
            folder.mkdir(parents=True)
            (folder / f'{audit.HLM}_assay.json').write_text('{}')
            (folder / f'{audit.HLM}_activities_00000.json').write_text(json.dumps(page([1], total=1, terminal=True)))
            with self.assertRaisesRegex(ValueError, 'Frozen ChEMBL count'):
                audit.load_sources()

    def test_audit_rejects_changed_totals_empty_and_repeated_stored_rows(self):
        cases = []
        changed = deepcopy(self.pages)
        changed[1]['page_meta']['total_count'] = 4
        cases.append((changed, 'count changed'))
        empty = deepcopy(self.pages)
        empty[1]['activities'] = []
        cases.append((empty, 'empty'))
        repeated = deepcopy(self.pages)
        repeated[1]['activities'][0]['activity_id'] = 2
        cases.append((repeated, 'Repeated activity ID'))
        for pages, message in cases:
            with self.subTest(message=message), tempfile.TemporaryDirectory() as tmp, patch.object(audit, 'ROOT', Path(tmp)):
                folder = Path(tmp) / 'data/raw/chembl'
                folder.mkdir(parents=True)
                (folder / f'{audit.HLM}_assay.json').write_text('{}')
                for p in pages:
                    offset = p['page_meta']['offset']
                    (folder / f'{audit.HLM}_activities_{offset:05d}.json').write_text(json.dumps(p))
                with self.assertRaisesRegex(ValueError, message):
                    audit.load_sources()

    def test_audit_rejects_loaded_ids_inconsistent_with_pagination_total(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(audit, 'ROOT', Path(tmp)), patch.dict(audit.EXPECTED, {audit.HLM: 3}):
            folder = Path(tmp) / 'data/raw/chembl'
            folder.mkdir(parents=True)
            (folder / f'{audit.HLM}_assay.json').write_text('{}')
            for p in deepcopy(self.pages):
                for row in p['activities']:
                    row['molecule_chembl_id'] = 'fixture'
                offset = p['page_meta']['offset']
                (folder / f'{audit.HLM}_activities_{offset:05d}.json').write_text(json.dumps(p))
            # Simulate a future loader regression collapsing distinct source IDs.
            with patch.object(audit, 'enrich', side_effect=lambda *args: {'activity_id': 1}):
                with self.assertRaisesRegex(ValueError, 'page total, observed rows and unique activity IDs differ'):
                    audit.load_sources()


class ProvenanceFailureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for module in (acquire, provenance):
            patcher = patch.object(module, 'ROOT', self.root)
            patcher.start()
            self.addCleanup(patcher.stop)
        network = patch.object(acquire.urllib.request, 'urlopen', side_effect=AssertionError('Offline test attempted network'))
        self.network = network.start()
        self.addCleanup(network.stop)
        self.raw = self.root / 'data/raw/chembl/input.json'
        self.raw.parent.mkdir(parents=True)
        self.raw.write_bytes(b'abc')
        self.url = 'https://example.invalid/frozen'
        self.receipt = self.root / 'manifests/downloads/chembl__input.json.json'
        self.saved = {**provenance.record(self.raw), 'source_url': self.url}
        provenance.save_json(self.receipt, self.saved)

    def download(self, url=None):
        return acquire.download(url or self.url, 'chembl/input.json', 'fixture')

    def test_valid_receipt_reused_offline(self):
        self.assertEqual(self.download(), self.raw)
        self.network.assert_not_called()

    def test_wrong_sha256_rejected(self):
        self.raw.write_bytes(b'abd')  # Same byte size, different hash.
        with self.assertRaisesRegex(ValueError, 'hash/size mismatch'):
            provenance.verify(self.saved)
        with self.assertRaisesRegex(ValueError, 'hash/size mismatch'):
            self.download()

    def test_wrong_file_size_rejected(self):
        self.saved['byte_size'] += 1  # Correct hash isolates the size check.
        self.receipt.write_text(json.dumps(self.saved))
        with self.assertRaisesRegex(ValueError, 'hash/size mismatch'):
            provenance.verify(self.saved)
        with self.assertRaisesRegex(ValueError, 'hash/size mismatch'):
            self.download()

    def test_missing_receipt_rejected(self):
        self.receipt.unlink()
        with self.assertRaisesRegex(ValueError, 'without receipt'):
            self.download()
        self.assertEqual(self.raw.read_bytes(), b'abc')
        self.network.assert_not_called()

    def test_changed_source_url_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Source URL changed'):
            self.download(self.url + '?revision=2')
        self.assertEqual(self.raw.read_bytes(), b'abc')
        self.assertEqual(json.loads(self.receipt.read_text()), self.saved)
        self.network.assert_not_called()

    def test_interrupted_download_creates_neither_raw_file_nor_receipt(self):
        response = self.network.return_value.__enter__.return_value
        response.read.side_effect = IncompleteRead(b'partial JSON')
        self.network.side_effect = None
        with self.assertRaises(IncompleteRead):
            acquire.download(self.url, 'chembl/interrupted.json', 'fixture')
        self.assertFalse((self.root / 'data/raw/chembl/interrupted.json').exists())
        self.assertFalse((self.root / 'manifests/downloads/chembl__interrupted.json.json').exists())
        self.assertEqual(self.raw.read_bytes(), b'abc')
        self.assertEqual(json.loads(self.receipt.read_text()), self.saved)


class OutputProtectionTests(unittest.TestCase):
    def test_audit_refuses_changed_output_before_any_writes(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(audit, 'ROOT', Path(tmp)):
            existing = Path(tmp) / 'reports/existing.json'
            existing.parent.mkdir()
            existing.write_bytes(b'changed result')
            outputs = {'reports/new.json': b'new', 'reports/existing.json': b'expected result'}
            with self.assertRaisesRegex(ValueError, 'Audit output changed'):
                audit.write_outputs(outputs)
            self.assertEqual(existing.read_bytes(), b'changed result')
            self.assertFalse((Path(tmp) / 'reports/new.json').exists())

    def test_audit_allows_identical_output_rerun(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(audit, 'ROOT', Path(tmp)):
            outputs = {'reports/result.json': b'unchanged result'}
            audit.write_outputs(outputs)
            audit.write_outputs(outputs)
            self.assertEqual((Path(tmp) / 'reports/result.json').read_bytes(), b'unchanged result')


class StrictPairTests(unittest.TestCase):
    def classify(self, labels=('7', '9'), rat_labels=('7',), human_labels=('9',)):
        tdc = [fixture(audit.TH, 't', 'CCC', v, i) for i, v in enumerate(labels, 1)]
        rat = [fixture(audit.RAT, 'r', 'CCC', v, i) for i, v in enumerate(rat_labels, 10)]
        human = [fixture(audit.HH, 'h', 'CCC', v, i) for i, v in enumerate(human_labels, 20)]
        return audit.species_audit(tdc, rat, human)[2][0]['trace_class']

    def test_exactly_two_unique_numeric_matches(self):
        self.assertEqual(self.classify(('9.0', '7.00')), 'distinct_labels_match_rat_and_human')

    def test_three_rows_are_not_a_strict_pair(self):
        self.assertEqual(self.classify(('7', '9', '7')), 'partial_or_unresolved')

    def test_extra_unmatched_row_is_not_a_strict_pair(self):
        self.assertEqual(self.classify(('7', '9', '11')), 'partial_or_unresolved')

    def test_missing_or_invalid_label_is_not_a_strict_pair(self):
        for value in (None, '', 'invalid', 'NaN'):
            with self.subTest(value=value):
                self.assertEqual(self.classify(('7', value)), 'partial_or_unresolved')

    def test_identical_labels_matching_both_species_are_ambiguous(self):
        self.assertEqual(self.classify(('7', '7.0'), human_labels=('7',)),
                         'all_labels_match_both_species')

    def test_multiple_matching_rat_records_are_not_unique(self):
        self.assertEqual(self.classify(rat_labels=('7', '7.0')), 'partial_or_unresolved')

    def test_multiple_matching_human_records_are_not_unique(self):
        self.assertEqual(self.classify(human_labels=('9', '9.0')), 'partial_or_unresolved')

    def test_structure_alone_does_not_establish_numeric_agreement(self):
        self.assertEqual(self.classify(('7', '9.00000001')), 'partial_or_unresolved')

    def test_both_species_numeric_match_is_not_unique(self):
        self.assertEqual(self.classify(human_labels=('7', '9')), 'partial_or_unresolved')

    def test_two_rat_only_rows_are_not_a_pair(self):
        self.assertEqual(self.classify(('7', '8'), rat_labels=('7', '8')), 'partial_or_unresolved')

    def test_no_structural_candidates_is_explicit(self):
        tdc = [fixture(audit.TH, 't', 'CCC', v, i) for i, v in enumerate(('7', '9'), 1)]
        rat = [fixture(audit.RAT, 't', 'CCC.O', '7', 3)]
        human = [fixture(audit.HH, 't', 'CCC.O', '9', 4)]
        summary, _, repeats = audit.species_audit(tdc, rat, human)
        self.assertEqual(repeats[0]['trace_class'], 'no_strict_structural_match_to_either_assay')
        self.assertEqual(summary['OBSERVED']['secondary_id_duplicate_trace_groups'], {'distinct_labels_match_rat_and_human': 1})
