#!/usr/bin/env python3
"""
Local ProteinMPNN Execution Script - Windows Path Fix
Generate sequences for BipD binder design backbones
"""

import os
import subprocess
import glob
import shutil
from pathlib import Path

def run_proteinmpnn():
    """Execute ProteinMPNN on all RFdiffusion backbones with Windows path fix"""

    # Paths
    backbone_dir = "./rfdiffusion_test_results"
    output_dir = "./amina_results/bipd_sequences"
    proteinmpnn_dir = "./ProteinMPNN_local"
    temp_input_dir = os.path.join(proteinmpnn_dir, "temp_inputs")

    # Create directories
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(temp_input_dir, exist_ok=True)

    # Find all PDB backbone files (exclude trajectory files)
    pdb_files = glob.glob(f"{backbone_dir}/*design_*.pdb")
    pdb_files = [f for f in pdb_files if "traj" not in f]

    print(f"Found {len(pdb_files)} backbone structures:")
    for pdb in pdb_files:
        print(f"   - {os.path.basename(pdb)}")

    # Copy PDB files to temp directory with simple names
    temp_pdb_files = []
    for pdb_file in pdb_files:
        basename = os.path.basename(pdb_file)
        temp_path = os.path.join(temp_input_dir, basename)
        shutil.copy2(pdb_file, temp_path)
        temp_pdb_files.append(basename)
        print(f"   Copied to temp: {basename}")

    # Parameters for high-precision sequence generation
    model_weights_path = "./vanilla_model_weights"  # Relative path from ProteinMPNN dir
    params = {
        "--num_seq_per_target": "2",           # 2 sequences per backbone
        "--sampling_temp": "0.1",              # High precision (low temperature)
        "--seed": "42",                        # Reproducible results
        "--batch_size": "1",                   # Conservative for CPU
        "--save_score": "1",                   # Save confidence scores
        "--save_probs": "0",                   # Skip probability matrices (save space)
        "--path_to_model_weights": model_weights_path,
        "--out_folder": "outputs"              # Relative to ProteinMPNN dir
    }

    # Process each backbone
    results_found = False
    for i, temp_basename in enumerate(temp_pdb_files, 1):
        backbone_name = Path(temp_basename).stem
        print(f"\\nProcessing {i}/{len(temp_pdb_files)}: {backbone_name}")

        # Build ProteinMPNN command
        python_exe = os.path.abspath("./.venv/Scripts/python.exe")
        script_path = "./protein_mpnn_run.py"  # Relative to ProteinMPNN_local
        temp_pdb_path = f"./temp_inputs/{temp_basename}"  # Relative path

        cmd = [python_exe, script_path]
        cmd.extend(["--pdb_path", temp_pdb_path])

        # Add parameters
        for param, value in params.items():
            cmd.extend([param, value])

        print(f"   Command: {' '.join(cmd[2:])}")  # Skip python script path for display

        try:
            # Execute ProteinMPNN from its directory
            result = subprocess.run(cmd,
                                  capture_output=True,
                                  text=True,
                                  timeout=300,  # 5 minute timeout per backbone
                                  cwd=proteinmpnn_dir)

            if result.returncode == 0:
                print(f"   SUCCESS! Generated sequences for {backbone_name}")
                results_found = True
                if result.stdout:
                    # Show last few lines of output
                    lines = result.stdout.split('\\n')
                    for line in lines[-5:]:
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

    # Copy results back to our output directory
    if results_found:
        proteinmpnn_outputs = os.path.join(proteinmpnn_dir, "outputs")
        if os.path.exists(proteinmpnn_outputs):
            # Copy all generated FASTA files
            for item in os.listdir(proteinmpnn_outputs):
                if item.endswith('.fa') or item.endswith('.fasta'):
                    src = os.path.join(proteinmpnn_outputs, item)
                    dst = os.path.join(output_dir, item)
                    shutil.copy2(src, dst)
                    print(f"   Copied result: {item}")

    # Clean up temp files
    if os.path.exists(temp_input_dir):
        shutil.rmtree(temp_input_dir)
        print("   Cleaned up temporary files")

    # Summary
    print(f"\\nProteinMPNN execution complete!")
    print(f"Check results in: {output_dir}")

    # List generated files
    generated_files = glob.glob(f"{output_dir}/*.fa*")
    if generated_files:
        print(f"Generated {len(generated_files)} FASTA files:")
        for fasta in generated_files:
            print(f"   - {os.path.basename(fasta)}")
    else:
        print("WARNING: No FASTA files found - check for errors above")

if __name__ == "__main__":
    print("Local ProteinMPNN Sequence Generation (Windows Path Fix)")
    print("=" * 60)
    run_proteinmpnn()