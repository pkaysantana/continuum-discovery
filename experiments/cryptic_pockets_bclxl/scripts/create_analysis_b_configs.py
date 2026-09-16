import json
import os
from pathlib import Path

def write_config(filename, config_dict):
    out_dir = Path("results/analysis_b/config")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / filename, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2)

apo_hash = "b0d20bfd4907b92929161c78790051471de261a917371b40da3aa418a3d64693"
holo_hash = "8162ea71785ea6e6ecc75d3be07bca42852cd9eacbcbe75f4039f7423a255ea4"

# P2Rank apo
p2rank_apo = {
    "analysis_condition": "apo",
    "method": "p2rank",
    "input_path": "data/processed/apo_matched_core.pdb",
    "input_sha256": apo_hash,
    "tool_path": "p2rank_2.5.1/prank.sh",
    "tool_version": "2.5.1",
    "java_version": "21.0.2",
    "command_template": "prank predict -f {INPUT} -o {OUTPUT} -threads 1 -seed 42 -visualizations 0",
    "parameters": {
        "threads": 1,
        "seed": 42,
        "visualizations": 0,
        "model": "default"
    },
    "ranking_configuration": "default",
    "candidate_budget": "all",
    "environment_identifier": "java-21-pinned",
    "expected_output_directory": "results/analysis_b/raw/p2rank_apo"
}

# P2Rank holo
p2rank_holo = p2rank_apo.copy()
p2rank_holo["analysis_condition"] = "holo_control"
p2rank_holo["input_path"] = "data/processed/holo_matched_core_no_ligand.pdb"
p2rank_holo["input_sha256"] = holo_hash
p2rank_holo["expected_output_directory"] = "results/analysis_b/raw/p2rank_holo"

# Lacuna apo
lacuna_apo = {
    "analysis_condition": "apo",
    "method": "lacuna",
    "input_path": "data/processed/apo_matched_core.pdb",
    "input_sha256": apo_hash,
    "tool_path": "lacuna CLI",
    "tool_version": "1.2.0",
    "command_template": "lacuna discover {INPUT} --conformers 20 --detector alpha --rank-by learned --no-sequence -o {OUTPUT}",
    "parameters": {
        "backend": "nma",
        "cutoff": 8.0,
        "n_modes": 10,
        "max_rmsd": 2.0,
        "seed": 42,
        "conformers": 20,
        "detector": "alpha",
        "rank-by": "learned",
        "no_sequence": True,
        "seed_from_sequence": False
    },
    "ranking_configuration": "learned",
    "candidate_budget": 10,
    "environment_identifier": "python-3.11-lacuna",
    "expected_output_directory": "results/analysis_b/raw/lacuna_apo"
}

# Lacuna holo
lacuna_holo = lacuna_apo.copy()
lacuna_holo["analysis_condition"] = "holo_control"
lacuna_holo["input_path"] = "data/processed/holo_matched_core_no_ligand.pdb"
lacuna_holo["input_sha256"] = holo_hash
lacuna_holo["expected_output_directory"] = "results/analysis_b/raw/lacuna_holo"

write_config("p2rank_apo.json", p2rank_apo)
write_config("p2rank_holo.json", p2rank_holo)
write_config("lacuna_apo.json", lacuna_apo)
write_config("lacuna_holo.json", lacuna_holo)

print("Configurations created.")
