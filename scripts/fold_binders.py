#!/usr/bin/env python3
"""
Forward Folding Script for BipD Binder Sequences
Uses Meta's free ESMFold API to validate 3D structures of generated sequences
"""

import os
import time
import glob
import requests
from pathlib import Path

def parse_fasta_file(fasta_path):
    """Parse FASTA file and extract generated sequences only"""
    sequences = []
    current_seq = ""
    current_header = ""

    with open(fasta_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                # Save previous sequence if it exists
                if current_seq and current_header:
                    sequences.append({
                        'header': current_header,
                        'sequence': current_seq
                    })
                current_header = line[1:]  # Remove '>'
                current_seq = ""
            else:
                current_seq += line

        # Don't forget the last sequence
        if current_seq and current_header:
            sequences.append({
                'header': current_header,
                'sequence': current_seq
            })

    # Filter to get only generated sequences (skip original/reference)
    generated_sequences = []
    for seq_data in sequences:
        header = seq_data['header']
        # Look for sample sequences (T=0.1, sample=X)
        if 'T=0.1' in header and 'sample=' in header:
            generated_sequences.append(seq_data)

    return generated_sequences

def clean_sequence(sequence):
    """Clean sequence by removing unwanted characters and taking only the binder part"""
    # Split on '/' if present (some sequences have structure like binder/linker)
    if '/' in sequence:
        sequence = sequence.split('/')[0]  # Take first part (the binder)

    # Remove stretches of X characters (placeholders)
    import re
    sequence = re.sub(r'X+', '', sequence)

    # Remove any non-standard amino acids and keep only the 20 standard ones
    clean_seq = ''.join(c for c in sequence if c in 'ACDEFGHIKLMNPQRSTVWY')

    return clean_seq

def fold_sequence_with_esmfold(sequence, output_path, max_retries=3):
    """Send sequence to ESMFold API and save the folded PDB"""
    url = "https://api.esmatlas.com/foldSequence/v1/pdb/"

    headers = {
        'Content-Type': 'text/plain',
        'User-Agent': 'ContinuumDiscovery/1.0 (Research/Hackathon)'
    }

    data = sequence  # Send sequence as raw text

    for attempt in range(max_retries):
        try:
            print(f"    Attempt {attempt + 1}: Folding sequence (length: {len(sequence)})")
            response = requests.post(url, data=data, headers=headers, timeout=30)

            if response.status_code == 200:
                # Save PDB data
                with open(output_path, 'w') as f:
                    f.write(response.text)
                print(f"    SUCCESS: Saved folded structure to {os.path.basename(output_path)}")
                return True
            elif response.status_code == 429:
                print(f"    Rate limited, waiting 10 seconds...")
                time.sleep(10)
            else:
                print(f"    HTTP {response.status_code}: {response.text[:100]}...")
                time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"    Request failed: {e}")
            time.sleep(5)

    print(f"    FAILED: Could not fold sequence after {max_retries} attempts")
    return False

def main():
    """Main folding workflow"""
    print("BipD Binder Forward Folding with ESMFold")
    print("=" * 50)

    # Setup directories
    input_dir = "./amina_results/bipd_sequences"
    output_dir = "./amina_results/bipd_folded_binders"
    os.makedirs(output_dir, exist_ok=True)

    # Find all FASTA files
    fasta_files = glob.glob(f"{input_dir}/*.fa")
    print(f"Found {len(fasta_files)} FASTA files to process")

    total_sequences = 0
    successful_folds = 0

    # Process each FASTA file
    for i, fasta_path in enumerate(fasta_files, 1):
        basename = Path(fasta_path).stem
        print(f"\\nProcessing {i}/{len(fasta_files)}: {basename}")

        # Parse sequences
        generated_sequences = parse_fasta_file(fasta_path)
        print(f"  Found {len(generated_sequences)} generated sequences")

        # Fold each generated sequence
        for seq_idx, seq_data in enumerate(generated_sequences, 1):
            total_sequences += 1

            # Clean the sequence
            clean_seq = clean_sequence(seq_data['sequence'])

            # Skip if sequence is too short or too long
            if len(clean_seq) < 20:
                print(f"    Skipping sequence {seq_idx}: too short ({len(clean_seq)} aa)")
                continue
            elif len(clean_seq) > 1000:
                print(f"    Skipping sequence {seq_idx}: too long ({len(clean_seq)} aa)")
                continue

            # Create output filename
            design_num = basename.split('_')[-1]  # Extract design number (0, 1, 2, etc.)
            output_filename = f"folded_design_{design_num}_seq_{seq_idx}.pdb"
            output_path = os.path.join(output_dir, output_filename)

            # Skip if already exists
            if os.path.exists(output_path):
                print(f"    Skipping sequence {seq_idx}: {output_filename} already exists")
                successful_folds += 1
                continue

            print(f"  Folding sequence {seq_idx}/{len(generated_sequences)}")

            # Fold the sequence
            if fold_sequence_with_esmfold(clean_seq, output_path):
                successful_folds += 1

            # Rate limiting delay
            print(f"    Waiting 3 seconds (rate limiting)...")
            time.sleep(3)

    # Summary
    print(f"\\nFolding Summary:")
    print(f"=" * 30)
    print(f"Total sequences processed: {total_sequences}")
    print(f"Successful folds: {successful_folds}")
    print(f"Success rate: {(successful_folds/total_sequences*100):.1f}%")
    print(f"Output directory: {output_dir}")

    # List generated files
    pdb_files = glob.glob(f"{output_dir}/*.pdb")
    if pdb_files:
        print(f"\\nGenerated {len(pdb_files)} PDB files:")
        for pdb in sorted(pdb_files):
            print(f"  - {os.path.basename(pdb)}")
    else:
        print("\\nWARNING: No PDB files were generated!")

if __name__ == "__main__":
    main()