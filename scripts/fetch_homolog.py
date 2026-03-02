#!/usr/bin/env python3
"""
Universal Biodefense Platform: Cross-Pathogen Target Fetcher
Downloads homologous Type III secretion system structures for pan-bacterial analysis
"""

import os
import requests
import time
from pathlib import Path

def fetch_pdb_structure(pdb_id: str, output_dir: str = "../amina_results/cross_pathogen_structures") -> str:
    """
    Fetch PDB structure from RCSB PDB database

    Args:
        pdb_id: 4-letter PDB identifier
        output_dir: Directory to save the structure

    Returns:
        Path to downloaded PDB file
    """

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # PDB download URL
    pdb_url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    output_file = os.path.join(output_dir, f"{pdb_id.upper()}.pdb")

    print(f"[TARGET] Universal Biodefense Platform: Cross-Pathogen Target Acquisition")
    print(f"=" * 65)
    print(f"Target: {pdb_id.upper()} - Yersinia pestis LcrV (Type III needle-tip)")
    print(f"Source: RCSB PDB Database")
    print(f"Resolution: 1.65 Å (sub-ångstrom validation ready)")
    print()

    try:
        print(f"Downloading PDB structure from: {pdb_url}")
        response = requests.get(pdb_url, timeout=30)

        if response.status_code == 200:
            with open(output_file, 'w') as f:
                f.write(response.text)

            print(f"[OK] SUCCESS: Downloaded {pdb_id.upper()}.pdb")
            print(f"[FILE] Location: {output_file}")

            # Validate the download
            file_size = os.path.getsize(output_file)
            print(f"[STATS] File size: {file_size:,} bytes")

            # Count atoms/residues for validation
            with open(output_file, 'r') as f:
                lines = f.readlines()
                atom_lines = [l for l in lines if l.startswith('ATOM')]
                hetatm_lines = [l for l in lines if l.startswith('HETATM')]

            print(f"[STRUCTURE] Structure content:")
            print(f"   ATOM records: {len(atom_lines):,}")
            print(f"   HETATM records: {len(hetatm_lines):,}")
            print(f"   Total lines: {len(lines):,}")

            return output_file

        else:
            print(f"[ERROR] ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"[ERROR] ERROR: Failed to download PDB structure: {e}")
        return None

def analyze_structure_info(pdb_file: str):
    """Analyze basic structure information"""
    if not os.path.exists(pdb_file):
        print("[ERROR] PDB file not found for analysis")
        return

    print(f"\n[ANALYSIS] Structure Analysis: {os.path.basename(pdb_file)}")
    print(f"-" * 50)

    chains = set()
    residues = set()
    resolution = None

    try:
        with open(pdb_file, 'r') as f:
            for line in f:
                if line.startswith('REMARK   2 RESOLUTION.'):
                    resolution_text = line.strip().split()
                    if len(resolution_text) > 3:
                        resolution = resolution_text[3]

                elif line.startswith('ATOM'):
                    chain_id = line[21:22].strip()
                    res_num = line[22:26].strip()
                    res_name = line[17:20].strip()

                    chains.add(chain_id)
                    residues.add(f"{chain_id}:{res_name}:{res_num}")

        print(f"[RESOLUTION] Resolution: {resolution} Å")
        print(f"[CHAINS] Chains: {sorted(chains)} ({len(chains)} total)")
        print(f"[RESIDUES] Unique residues: {len(residues)}")

        # Analyze chain composition
        chain_residue_counts = {}
        for res in residues:
            chain = res.split(':')[0]
            chain_residue_counts[chain] = chain_residue_counts.get(chain, 0) + 1

        for chain, count in sorted(chain_residue_counts.items()):
            print(f"   Chain {chain}: {count} residues")

    except Exception as e:
        print(f"[WARNING] Analysis error: {e}")

def main():
    """Fetch cross-pathogen targets for Universal Biodefense Platform"""

    # Cross-pathogen targets (Type III secretion system needle-tip proteins)
    targets = {
        "4JBU": {
            "organism": "Yersinia pestis",
            "protein": "LcrV (Low Calcium Response V antigen)",
            "description": "1.65Å Type III secretion needle-tip protein - Plague pathogen",
            "priority": "HIGH"
        },
        "1R6F": {
            "organism": "Yersinia pestis",
            "protein": "LcrV (V-antigen)",
            "description": "2.2Å resolution alternative structure",
            "priority": "MEDIUM"
        }
    }

    print("*** UNIVERSAL BIODEFENSE PLATFORM")
    print("Cross-Pathogen Homolog Acquisition for Pan-Bacterial Analysis")
    print("=" * 70)
    print("Goal: Validate if BipD binders work against multiple pathogen threats")
    print()

    downloaded_structures = []

    for pdb_id, info in targets.items():
        print(f"[TARGET] Target: {info['organism']} - {info['protein']}")
        print(f"   Priority: {info['priority']}")
        print(f"   Description: {info['description']}")
        print()

        pdb_file = fetch_pdb_structure(pdb_id)

        if pdb_file:
            downloaded_structures.append(pdb_file)
            analyze_structure_info(pdb_file)
            print()

        # Rate limiting
        time.sleep(2)

    # Summary
    print(f"[STATS] ACQUISITION SUMMARY:")
    print(f"=" * 30)
    print(f"Structures downloaded: {len(downloaded_structures)}")
    for structure in downloaded_structures:
        print(f"  [OK] {os.path.basename(structure)}")

    if downloaded_structures:
        print(f"\n[READY] Ready for cross-pathogen docking analysis!")
        print(f"Next: Test BipD binders against Y. pestis LcrV homolog")
    else:
        print(f"\n[ERROR] No structures downloaded - check network connectivity")

if __name__ == "__main__":
    main()