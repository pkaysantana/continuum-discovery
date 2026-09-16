"""Deterministic identity and descriptive audit helpers; no scientific filtering."""
from collections import Counter
from decimal import Decimal, InvalidOperation
import math
import re
import numpy as np
from rdkit import Chem, rdBase
from rdkit.Chem import Crippen, Descriptors, Lipinski, rdMolDescriptors

MISSING = {'', 'na', 'n/a', 'nan', 'none', 'null'}
RELATIONS = {'<', '>', '=', '<=', '>=', '~'}
PATTERN = re.compile(r'^\s*(<=|>=|<|>|=|~|≤|≥)?\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*$')
PROPERTIES = ('molecular_weight', 'clogp', 'tpsa', 'hbd', 'hba', 'rotatable_bonds', 'fraction_csp3')


def missing(value):
    return value is None or str(value).strip().lower() in MISSING


def measurement(value, relation=None):
    """Keep absence/unknown distinct; Decimal equality never rounds source labels."""
    if missing(value):
        return {'status': 'MISSING', 'number': None, 'relation': 'UNKNOWN'}
    match = PATTERN.fullmatch(str(value))
    if not match:
        return {'status': 'UNPARSEABLE', 'number': None, 'relation': 'UNKNOWN'}
    inline, number = match.groups()
    inline = {'≤': '<=', '≥': '>='}.get(inline, inline)
    explicit = None if missing(relation) else {'≤': '<=', '≥': '>='}.get(str(relation).strip(), str(relation).strip())
    if explicit and inline and explicit != inline:
        return {'status': 'CONFLICT', 'number': number, 'relation': 'UNKNOWN'}
    effective = explicit or inline or '='
    return {'status': 'VALID' if effective in RELATIONS else 'UNKNOWN_RELATION',
            'number': number, 'relation': effective if effective in RELATIONS else 'UNKNOWN'}


def number(value):
    parsed = measurement(value)
    return Decimal(parsed['number']) if parsed['status'] == 'VALID' else None


def numeric_equal(a, b):
    aa, bb = number(a), number(b)
    return aa is not None and bb is not None and aa == bb


def chemical(smiles):
    base = {'canonical_smiles_rdkit': None, 'structure_status': 'MISSING' if missing(smiles) else 'INVALID',
            'structure_error': None, 'undefined_stereo_elements': None, 'fragment_count': None,
            'dummy_atom_count': None, **{p: None for p in PROPERTIES}}
    if missing(smiles):
        return base
    # Suppress RDKit's process-level parse messages; return an explicit row-level error.
    with rdBase.BlockLogs():
        mol = Chem.MolFromSmiles(str(smiles), sanitize=False)
        if mol is None:
            base['structure_error'] = 'RDKit MolFromSmiles returned None'
            return base
        try:
            Chem.SanitizeMol(mol)
            Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
        except Exception as exc:
            base['structure_error'] = type(exc).__name__ + ': ' + str(exc)
            return base
    base.update(structure_status='VALID', canonical_smiles_rdkit=Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True),
                undefined_stereo_elements=sum(s.specified == Chem.StereoSpecified.Unspecified for s in Chem.FindPotentialStereo(mol)),
                fragment_count=len(Chem.GetMolFrags(mol)), dummy_atom_count=sum(a.GetAtomicNum() == 0 for a in mol.GetAtoms()),
                molecular_weight=Descriptors.MolWt(mol), clogp=Crippen.MolLogP(mol),
                tpsa=rdMolDescriptors.CalcTPSA(mol), hbd=Lipinski.NumHDonors(mol), hba=Lipinski.NumHAcceptors(mol),
                rotatable_bonds=rdMolDescriptors.CalcNumRotatableBonds(mol, rdMolDescriptors.NumRotatableBondsOptions.Strict),
                fraction_csp3=rdMolDescriptors.CalcFractionCSP3(mol))
    if any(not math.isfinite(base[p]) for p in PROPERTIES):
        raise ValueError('Nonfinite descriptor; explicit review required')
    return base


def identity_match(left, right):
    a, b = chemical(left), chemical(right)
    return a['structure_status'] == b['structure_status'] == 'VALID' and a['canonical_smiles_rdkit'] == b['canonical_smiles_rdkit']


def duplicate_summary(keys):
    counts = Counter(k for k in keys if k is not None)
    repeated = {k: n for k, n in sorted(counts.items()) if n > 1}
    return {'unique_valid_structures': len(counts), 'duplicated_structure_groups': len(repeated),
            'rows_in_duplicate_groups': sum(repeated.values()), 'excess_duplicate_rows': sum(n-1 for n in repeated.values())}


def distribution(values):
    parsed = [measurement(v) for v in values]
    valid = [Decimal(p['number']) for p in parsed if p['status'] == 'VALID']
    counts = Counter(valid)
    result = {'total_rows': len(values), 'numeric_rows': len(valid),
              'missing_rows': sum(p['status'] == 'MISSING' for p in parsed),
              'unparseable_rows': sum(p['status'] not in ('VALID', 'MISSING') for p in parsed),
              'exactly_3': counts[Decimal(3)], 'exactly_150': counts[Decimal(150)],
              'inequality_strings': sum(p['relation'] in ('<', '>', '<=', '>=') for p in parsed),
              'top_value_frequencies': [{'value': str(k), 'count': n} for k, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]]}
    if valid:
        arr = np.array([float(v) for v in valid], dtype=float)
        quantiles = np.quantile(arr, [0, .05, .25, .5, .75, .95, 1], method='linear')
        result.update(dict(zip(('min', 'q05', 'q25', 'median', 'q75', 'q95', 'max'), map(float, quantiles))))
        result.update(iqr=float(quantiles[4]-quantiles[2]), mad=float(np.median(np.abs(arr-np.median(arr)))))
    return result
