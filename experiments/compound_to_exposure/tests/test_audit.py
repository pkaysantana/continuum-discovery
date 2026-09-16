"""Small offline fixtures only; never model outputs or live APIs."""
import json
from pathlib import Path
import tempfile
import unittest
from chemistry import chemical, distribution, duplicate_summary, identity_match, measurement, missing, numeric_equal
from provenance import digest, immutable, json_bytes
from audit import species_audit, microsome_audit, paired_audit, enrich, ROOT, HLM, RAT, HH, TH, TM


def fixture(source, ident, smiles, target, activity, relation='='):
    return enrich({'activity_id': activity, 'standard_value': target, 'standard_relation': relation,
                   'standard_units': 'mL.min-1.g-1', 'value': target, 'relation': relation, 'units': 'microL/min/mg'},
                  source, activity, ROOT / 'data/raw/fixture.json', smiles, target, ident, relation)


class HashTests(unittest.TestCase):
    def test_sha256_known_vector(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'input'
            path.write_bytes(b'abc')
            self.assertEqual(digest(path), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')

    def test_immutable_reuse_and_refuse_replacement(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'raw'
            immutable(p, b'abc'); immutable(p, b'abc')
            with self.assertRaises(ValueError):
                immutable(p, b'xyz')
            self.assertEqual(p.read_bytes(), b'abc')

    def test_deterministic_serialization(self):
        self.assertEqual(json_bytes({'b': 2, 'a': 1}), json_bytes({'a': 1, 'b': 2}))


class ChemistryTests(unittest.TestCase):
    def test_valid_parse(self):
        self.assertEqual(chemical('CCO')['structure_status'], 'VALID')

    def test_invalid_parse(self):
        result = chemical('not_a_smiles')
        self.assertEqual(result['structure_status'], 'INVALID')
        self.assertIsNotNone(result['structure_error'])

    def test_invalid_valence(self):
        self.assertEqual(chemical('C(C)(C)(C)(C)C')['structure_status'], 'INVALID')

    def test_missing_parse(self):
        for v in (None, '', '  ', 'NaN'):
            self.assertEqual(chemical(v)['structure_status'], 'MISSING')

    def test_canonical_equivalence(self):
        self.assertTrue(identity_match('OCC', 'CCO'))

    def test_preserve_stereo(self):
        self.assertFalse(identity_match('F[C@H](Cl)Br', 'F[C@@H](Cl)Br'))
        self.assertFalse(identity_match('F[C@H](Cl)Br', 'FC(Cl)Br'))

    def test_preserve_salts_charges_isotopes(self):
        for a,b in [('CC(=O)O','CC(=O)[O-]'), ('CCO.[Na+]','CCO'), ('[13CH3]CO','CCO')]:
            self.assertFalse(identity_match(a,b))

    def test_invalid_does_not_match_invalid(self):
        self.assertFalse(identity_match('bad', 'bad'))
        self.assertFalse(identity_match(None, None))

    def test_duplicate_counts(self):
        keys = [chemical(s)['canonical_smiles_rdkit'] for s in ('CCO','OCC','CCC','CCCO','OCCC','bad')]
        self.assertEqual(duplicate_summary(keys), {'unique_valid_structures':3,'duplicated_structure_groups':2,'rows_in_duplicate_groups':4,'excess_duplicate_rows':2})

    def test_undefined_stereo(self):
        self.assertEqual(chemical('FC(Cl)Br')['undefined_stereo_elements'], 1)
        self.assertEqual(chemical('F[C@H](Cl)Br')['undefined_stereo_elements'], 0)

    def test_descriptors_reference(self):
        c = chemical('CCO')
        self.assertAlmostEqual(c['molecular_weight'], 46.069, places=3)
        self.assertAlmostEqual(c['tpsa'], 20.23, places=2)
        self.assertEqual((c['hbd'], c['hba'], c['fraction_csp3']), (1,1,1.0))

    def test_repeatability(self):
        self.assertEqual(json_bytes(chemical('CC(O)C')), json_bytes(chemical('CC(O)C')))


class ValueTests(unittest.TestCase):
    def test_relation_parsing(self):
        for v, rel in [('<3','<'), ('>150','>'), ('=3.0','='), ('<= 3','<='), ('≥150','>='), ('1e2','=')]:
            self.assertEqual(measurement(v)['relation'], rel)

    def test_explicit_relation(self):
        self.assertEqual(measurement('3.0','<')['relation'], '<')

    def test_conflicting_relation(self):
        self.assertEqual(measurement('<3','>')['status'], 'CONFLICT')

    def test_unknown_relation(self):
        self.assertEqual(measurement('3','?')['status'], 'UNKNOWN_RELATION')

    def test_missing_chembl_relation_stays_unknown(self):
        self.assertEqual(fixture(HLM,'id','CCO','3',1,None)['measurement_audit']['relation'], 'UNKNOWN')

    def test_missing_values_not_zero(self):
        for v in (None,'','NA','n/a','NaN','null','None'):
            self.assertTrue(missing(v))
        self.assertFalse(missing('0'))
        self.assertEqual(distribution(['0',None,'NA','bad'])['numeric_rows'],1)
        self.assertEqual(distribution(['0',None,'NA','bad'])['missing_rows'],2)
        self.assertEqual(distribution(['0',None,'NA','bad'])['unparseable_rows'],1)

    def test_exact_decimal_no_tolerance(self):
        self.assertTrue(numeric_equal('3', '3.000'))
        self.assertFalse(numeric_equal('3', '3.00000001'))
        self.assertFalse(numeric_equal(None, None))

    def test_boundary_summaries(self):
        d=distribution(['<3','3','150','>150','4',None])
        self.assertEqual((d['exactly_3'],d['exactly_150'],d['inequality_strings']), (2,2,2))
        self.assertEqual(d['median'],4)


class ReconciliationTests(unittest.TestCase):
    def test_id_evidence_does_not_override_structure_mismatch(self):
        c=fixture(HLM,'same','CCO.O','4',1,None)
        c['parent_molecule_chembl_id']='parent'
        t=fixture(TM,'parent','CCO','4',2)
        summary, rows=microsome_audit([t],[c])
        self.assertEqual(summary['OBSERVED']['structure_overlap'],0)
        secondary=summary['secondary_id_audit']['OBSERVED']['strict_structure_unmatched_details'][0]
        self.assertEqual(secondary['exact_id_candidates'],[])
        self.assertTrue(secondary['chembl_declared_parent_id_candidates'][0]['numeric_equal'])

    def test_unknown_relation_not_equals(self):
        from audit import relations
        r=fixture(HLM,'a','CCO','3',1,None)
        self.assertEqual(relations([r],'standard_relation','standard_value')['counts'], {'<':0,'>':0,'=':0,'anything_else':1})

    def test_species_id_match_keeps_structure_unmatched(self):
        t=fixture(TH,'same','CCO','3',1)
        r=fixture(RAT,'same','CCO.O','3',2)
        summary, rows, _=species_audit([t],[r],[])
        self.assertEqual(rows[0]['structure_species_class'],'neither')
        self.assertEqual(rows[0]['secondary_id_numeric_matches_species'],'rat_only')
        self.assertEqual(summary['INFERRED']['claim_status'],'NOT_REPRODUCED')

    def test_species_evidence_and_repeated_labels(self):
        rat=[fixture(RAT,'r1','CCO','3',1),fixture(RAT,'r2','CCC','7',2)]
        human=[fixture(HH,'h1','CCN','3',3),fixture(HH,'h2','CCC','9',4)]
        tdc=[fixture(TH,'t1','OCC','3',5),fixture(TH,'t2','NCC','3',6),fixture(TH,'t3','CCC','7',7),fixture(TH,'t4','CCC','9',8),fixture(TH,'t5','bad','3',9)]
        summary, rows, dup=species_audit(tdc,rat,human)
        self.assertEqual(summary['INFERRED']['claim_status'],'REPRODUCED')
        self.assertEqual(summary['OBSERVED']['row_counts'], {'rat_only':1,'human_only':1,'both':2,'neither':0,'ambiguous_unparseable':1})
        self.assertEqual(dup[0]['trace_class'],'distinct_labels_match_rat_and_human')

    def test_species_shared_label_ambiguous(self):
        summary, rows, dup=species_audit([fixture(TH,'t','CCO','3',3)], [fixture(RAT,'r','CCO','3',1)], [fixture(HH,'h','CCO','3',2)])
        self.assertEqual(rows[0]['numeric_label_matches_species'],'both')
        self.assertEqual(summary['INFERRED']['claim_status'],'NOT_REPRODUCED')

    def test_microsome_outer_reconciliation(self):
        chem=[fixture(HLM,'a','CCO','3',1,'<'),fixture(HLM,'b','CCC','7',2),fixture(HLM,'c','CCCl','12',3)]
        tdc=[fixture(TM,'a','OCC','3',4),fixture(TM,'b','CCC','8',5),fixture(TM,'d','CCN','9',6)]
        summary,rows=microsome_audit(tdc,chem)
        obs=summary['OBSERVED']
        self.assertEqual((obs['structure_overlap'],obs['tdc_rows_with_exact_numeric_match'],obs['tdc_rows_structure_matched_without_numeric_match'],obs['tdc_unmatched_rows'],obs['chembl_unmatched_rows']), (2,1,1,1,1))
        self.assertEqual(len(rows),4)
        self.assertEqual(obs['qualifier_reconciliation_candidate_pairs']['<']['tdc_inequality_present_pairs'],0)

    def test_paired_two_identity_definitions(self):
        a=[fixture(HLM,'same','CCO','3',1),fixture(HLM,'x','CCC','5',2),fixture(HLM,'bad','CCN','2',3)]
        b=[fixture(HH,'same','OCC','9',4),fixture(HH,'y','CCC','8',5),fixture(HH,'bad','CCCl','7',6)]
        result,rows=paired_audit(a,b)
        obs=result['OBSERVED']
        self.assertEqual((obs['id_overlap_n'],obs['canonical_structure_overlap_n'],obs['shared_structures_without_shared_id']), (2,2,1))
        self.assertEqual(len(obs['id_structure_disagreement_or_ambiguity']),1)
        self.assertTrue(all('raw_target' not in r for r in rows))


if __name__ == '__main__':
    unittest.main()
