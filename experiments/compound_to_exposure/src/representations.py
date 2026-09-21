import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors, Lipinski

# Frozen R1 descriptors
R1_PROPERTIES = (
    'MolWt', 'MolLogP', 'MolMR', 'TPSA', 'NumHDonors', 'NumHAcceptors',
    'NumRotatableBonds', 'RingCount', 'NumAromaticRings', 'NumAliphaticRings',
    'FractionCSP3', 'HeavyAtomCount'
)

def get_r1_descriptors(smiles):
    """
    Computes the 12 frozen RDKit descriptors for a given SMILES string.
    Returns a dictionary mapping descriptor name to its computed value.
    If the SMILES is unparseable or cannot be computed, returns None.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
        
    try:
        Chem.SanitizeMol(mol)
    except Exception:
        pass # RDKit might fail on some molecules, let's see if descriptors still work
        
    desc_dict = {}
    
    try:
        desc_dict['MolWt'] = Descriptors.MolWt(mol)
        desc_dict['MolLogP'] = Crippen.MolLogP(mol)
        desc_dict['MolMR'] = Crippen.MolMR(mol)
        desc_dict['TPSA'] = rdMolDescriptors.CalcTPSA(mol)
        desc_dict['NumHDonors'] = Lipinski.NumHDonors(mol)
        desc_dict['NumHAcceptors'] = Lipinski.NumHAcceptors(mol)
        desc_dict['NumRotatableBonds'] = rdMolDescriptors.CalcNumRotatableBonds(mol, rdMolDescriptors.NumRotatableBondsOptions.Strict)
        desc_dict['RingCount'] = Lipinski.RingCount(mol)
        desc_dict['NumAromaticRings'] = Lipinski.NumAromaticRings(mol)
        desc_dict['NumAliphaticRings'] = Lipinski.NumAliphaticRings(mol)
        desc_dict['FractionCSP3'] = rdMolDescriptors.CalcFractionCSP3(mol)
        desc_dict['HeavyAtomCount'] = Lipinski.HeavyAtomCount(mol)
    except Exception as e:
        # If any descriptor fails, we could return NaNs, but the SAP says
        # "descriptors are computed for all 1,102 records and the count of non-finite cells is reported."
        # If a molecule totally fails, we might return NaNs for all
        return {p: np.nan for p in R1_PROPERTIES}
        
    # Ensure they are in exact order if we convert to list
    return desc_dict

def get_r1_vector(smiles):
    res = get_r1_descriptors(smiles)
    if res is None:
        return [np.nan] * len(R1_PROPERTIES)
    return [float(res[p]) for p in R1_PROPERTIES]

def get_r2_morgan(smiles):
    """
    Morgan radius 2, 2048 bits, binary, useChirality=False.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        # If parse fails, return a zero vector or NaN?
        # A fingerprint should generally be returnable or error.
        # We will return None and handle it in the caller.
        return None
    
    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048, useChirality=False)
    # Convert to a binary list or numpy array
    arr = np.zeros((0,), dtype=np.int8)
    from rdkit.DataStructs import ConvertToNumpyArray
    ConvertToNumpyArray(fp, arr)
    return arr
