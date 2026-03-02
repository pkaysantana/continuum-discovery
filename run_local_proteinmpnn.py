#!/usr/bin/env python3
"""
Local ProteinMPNN Execution Script
Generate sequences for BipD binder design backbones
"""

import os
import subprocess
import glob
from pathlib import Path

def run_proteinmpnn():
    """Execute ProteinMPNN on all RFdiffusion backbones"""

    # Paths
    backbone_dir = "./rfdiffusion_test_results"
    output_dir = "./amina_results/bipd_sequences"
    proteinmpnn_script = "./ProteinMPNN_local/protein_mpnn_run.py"

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Find all PDB backbone files (exclude trajectory files)
    pdb_files = glob.glob(f"{backbone_dir}/*design_*.pdb")
    pdb_files = [f for f in pdb_files if "traj" not in f]

    print(f"Found {len(pdb_files)} backbone structures:")
    for pdb in pdb_files:
        print(f"   - {os.path.basename(pdb)}")

    # Parameters for high-precision sequence generation
    model_weights_path = os.path.abspath("./ProteinMPNN_local/vanilla_model_weights")
    params = {
        "--num_seq_per_target": "2",           # 2 sequences per backbone
        "--sampling_temp": "0.1",              # High precision (low temperature)
        "--seed": "42",                        # Reproducible results
        "--batch_size": "1",                   # Conservative for CPU
        "--save_score": "1",                   # Save confidence scores
        "--save_probs": "0",                   # Skip probability matrices (save space)
        "--path_to_model_weights": model_weights_path,  # Explicit model path
        "--out_folder": output_dir             # Output directory
    }

    # Process each backbone
    for i, pdb_file in enumerate(pdb_files, 1):
        backbone_name = Path(pdb_file).stem
        print(f"\nProcessing {i}/{len(pdb_files)}: {backbone_name}")

        # Build ProteinMPNN command using absolute paths
        python_exe = os.path.abspath("./.venv/Scripts/python.exe")
        script_path = "./protein_mpnn_run.py"  # Relative to ProteinMPNN_local
        pdb_absolute = os.path.abspath(pdb_file)
        output_absolute = os.path.abspath(output_dir)

        cmd = [python_exe, script_path]
        cmd.extend(["--pdb_path", pdb_absolute])

        # Add parameters with absolute paths
        for param, value in params.items():
            if param == "--out_folder":
                cmd.extend([param, output_absolute])
            elif param == "--path_to_model_weights":
                cmd.extend([param, value])  # Already absolute
            else:
                cmd.extend([param, value])

        print(f"   Command: {' '.join(cmd[2:])}")  # Skip python script path for display

        try:
            # Execute ProteinMPNN
            result = subprocess.run(cmd,
                                  capture_output=True,
                                  text=True,
                                  timeout=300,  # 5 minute timeout per backbone
                                  cwd="./ProteinMPNN_local")

            if result.returncode == 0:
                print(f"   SUCCESS! Generated sequences for {backbone_name}")
                if result.stdout:
                    # Show key output lines
                    for line in result.stdout.split('\n')[-10:]:
                        if line.strip():
                            print(f"      {line}")
            else:
                print(f"   ERROR processing {backbone_name}")
                if result.stderr:
                    print(f"      Error: {result.stderr}")

        except subprocess.TimeoutExpired:
            print(f"   TIMEOUT processing {backbone_name}")
        except Exception as e:
            print(f"   EXCEPTION: {e}")

    # Summary
    print(f"\nProteinMPNN execution complete!")
    print(f"Check results in: {output_dir}")

    # List generated files
    generated_files = glob.glob(f"{output_dir}/*.fa")
    if generated_files:
        print(f"Generated {len(generated_files)} FASTA files:")
        for fasta in generated_files:
            print(f"   - {os.path.basename(fasta)}")
    else:
        print("WARNING: No FASTA files found - check for errors above")

if __name__ == "__main__":
    print("Local ProteinMPNN Sequence Generation")
    print("=" * 50)
    run_proteinmpnn()