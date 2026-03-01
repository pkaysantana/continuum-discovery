#!/usr/bin/env python3
"""
Molecular Topological Fingerprint (MTF) Generator for UniBase Logging
B. pseudomallei BipD Analysis
"""

import hashlib
import re
from collections import Counter
from pathlib import Path

def calculate_sequence_composition(sequence):
    """Calculate amino acid composition and derived properties"""
    aa_counts = Counter(sequence)
    total_length = len(sequence)

    # Hydrophobic residues
    hydrophobic = ['A', 'I', 'L', 'M', 'F', 'W', 'Y', 'V']
    hydrophobic_fraction = sum(aa_counts[aa] for aa in hydrophobic) / total_length

    # Charged residues
    positive = ['K', 'R', 'H']
    negative = ['D', 'E']
    positive_fraction = sum(aa_counts[aa] for aa in positive) / total_length
    negative_fraction = sum(aa_counts[aa] for aa in negative) / total_length

    # Polar residues
    polar = ['S', 'T', 'N', 'Q']
    polar_fraction = sum(aa_counts[aa] for aa in polar) / total_length

    return {
        'length': total_length,
        'hydrophobic_fraction': round(hydrophobic_fraction, 3),
        'positive_fraction': round(positive_fraction, 3),
        'negative_fraction': round(negative_fraction, 3),
        'polar_fraction': round(polar_fraction, 3),
        'net_charge': positive_fraction - negative_fraction
    }

def extract_structural_features(pdb_file):
    """Extract basic structural features from PDB file"""
    features = {
        'num_chains': 0,
        'resolution': None,
        'beta_sheets': 0,
        'alpha_helices': 0,
        'disulfide_bonds': 0
    }

    try:
        with open(pdb_file, 'r') as f:
            content = f.read()

            # Extract resolution
            resolution_match = re.search(r'RESOLUTION\.\s+(\d+\.\d+)', content)
            if resolution_match:
                features['resolution'] = float(resolution_match.group(1))

            # Count secondary structures (simplified)
            features['alpha_helices'] = content.count('HELIX')
            features['beta_sheets'] = content.count('SHEET')

            # Count disulfide bonds
            features['disulfide_bonds'] = content.count('SSBOND')

            # Count unique chains
            chain_ids = set(re.findall(r'ATOM\s+\d+\s+\w+\s+\w+\s+(\w)', content))
            features['num_chains'] = len(chain_ids)

    except Exception as e:
        print(f"Warning: Could not fully parse PDB file: {e}")

    return features

def generate_topological_hash(sequence, structural_features):
    """Generate a topological hash for UniBase deduplication"""
    # Combine sequence and structural information
    hash_input = f"{sequence}_{structural_features['num_chains']}_{structural_features['resolution']}"

    # Create SHA-256 hash (first 16 characters for MTF)
    return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

def create_mtf_log_entry(sequence, pdb_file, protein_id="3NFT_BipD"):
    """Create complete MTF log entry for UniBase"""

    # Calculate sequence properties
    seq_props = calculate_sequence_composition(sequence)

    # Extract structural features
    struct_features = extract_structural_features(pdb_file)

    # Generate topological fingerprint hash
    topo_hash = generate_topological_hash(sequence, struct_features)

    # Create MTF entry
    mtf_entry = {
        'protein_id': protein_id,
        'organism': 'Burkholderia_pseudomallei',
        'protein_type': 'Type_III_secretion_translocator',
        'topological_hash': topo_hash,
        'sequence_length': seq_props['length'],
        'hydrophobic_fraction': seq_props['hydrophobic_fraction'],
        'charge_balance': seq_props['net_charge'],
        'structural_complexity': struct_features['num_chains'] * (struct_features['alpha_helices'] + struct_features['beta_sheets']),
        'resolution_angstrom': struct_features['resolution'],
        'biosecurity_flag': 'PATHOGEN_DERIVED',
        'research_context': 'biodefense_hackathon_authorized'
    }

    return mtf_entry

def main():
    # BipD sequence from 3NFT
    bipd_sequence = "GSALTVRDWPALEALAKTMPADAGARAMTDDDLRAAGVDRRVPEQKLGAAIDEAFASLRLPRIDGRFVDGRRANLTVFDDARVAAVRGHAARAQRNLLERLETETLLGGTTLTAGNDEGGIQPDPILQGLVDVIGQGKSDIDAYATIVEGLTLKYFQSAVDVMKLQDYISAKDDKNMKIDDGGKIKALIQVILVDHLPTMQLPKGADIARWRKELGDAVSDSGVVTINPDKLIKMRRDSLPPDGTVWDTARYQAWNPTAFSGQKDNIQNDVQTLVEKYSHQNSNFDNLVKVLSGAISTLTDTAKSYLQI"

    # PDB file path
    pdb_file = "3nft_original.pdb"

    # Generate MTF
    mtf_entry = create_mtf_log_entry(bipd_sequence, pdb_file)

    # Output results
    print("=== MOLECULAR TOPOLOGICAL FINGERPRINT (MTF) ===")
    print("Generated for UniBase Deduplication System")
    print()
    for key, value in mtf_entry.items():
        print(f"{key.upper()}: {value}")

    print("\n=== TOPOLOGICAL HASH FOR DEDUPLICATION ===")
    print(f"MTF Hash: {mtf_entry['topological_hash']}")
    print("\nThis hash can be used to identify similar structural trajectories")
    print("in the UniBase system to prevent redundant computation.")

if __name__ == "__main__":
    main()