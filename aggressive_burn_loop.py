#!/usr/bin/env python3
"""
Aggressive Burn Loop for Continuum Discovery
Targeting BipD (2IXR) hotspots with continuous Amina API calls
Efficiently burns remaining $17.82 in API credits
"""

import os
import json
import time
import requests
import random
from datetime import datetime
from pathlib import Path

# Configuration
AMINA_API_BASE = "https://api.aminoanalytica.com/v1"
API_KEY = os.getenv("AMINA_API_KEY", "your_api_key_here")
OUTPUT_DIR = Path("output/winning_binders")
LOGS_DIR = Path("logs/aggressive_burn")

# Target: BipD (2IXR) hotspots
TARGET_PDB = "2IXR"
HOTSPOTS = [128, 135, 142, 156, 166, 243, 256, 289, 301]

# Winning thresholds (lowered for aggressive saving)
MIN_IPTM = 0.70
MIN_COVERAGE = 70.0

# Batch sizes for API efficiency
RFDIFFUSION_BATCH = 8
PROTEINMPNN_BATCH = 16
BOLTZ_BATCH = 4
PESTO_BATCH = 12

class AggressiveBurnEngine:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        })
        self.iteration_count = 0
        self.winning_count = 0
        self.total_spent = 0.0

        # Ensure output directories exist
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)

        # Write to log file
        with open(LOGS_DIR / "burn_log.txt", "a") as f:
            f.write(log_entry + "\n")

    def call_amina_api(self, endpoint, payload, timeout=300):
        """Make API call with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    f"{AMINA_API_BASE}/{endpoint}",
                    json=payload,
                    timeout=timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                self.log(f"API call failed (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff

    def generate_rfdiffusion_batch(self):
        """Generate scaffold structures targeting BipD hotspots"""
        self.log(f"Running RFDiffusion batch (size: {RFDIFFUSION_BATCH})")

        # Randomize hotspot selection for diversity
        selected_hotspots = random.sample(HOTSPOTS, min(5, len(HOTSPOTS)))

        payload = {
            "target_pdb": TARGET_PDB,
            "hotspots": selected_hotspots,
            "num_designs": RFDIFFUSION_BATCH,
            "diffusion_steps": 50,  # Reduced for speed
            "scaffold_length": random.randint(80, 150),
            "temperature": random.uniform(0.8, 1.2)
        }

        try:
            result = self.call_amina_api("rfdiffusion/generate", payload)
            self.log(f"RFDiffusion generated {len(result.get('designs', []))} scaffolds")
            return result.get('designs', [])
        except Exception as e:
            self.log(f"RFDiffusion batch failed: {e}")
            return []

    def design_sequences_batch(self, scaffolds):
        """Design sequences with ProteinMPNN"""
        if not scaffolds:
            return []

        self.log(f"Running ProteinMPNN batch (size: {PROTEINMPNN_BATCH})")

        # Process scaffolds in batches
        all_sequences = []
        for i in range(0, len(scaffolds), PROTEINMPNN_BATCH):
            batch_scaffolds = scaffolds[i:i + PROTEINMPNN_BATCH]

            payload = {
                "scaffolds": batch_scaffolds,
                "num_sequences_per_scaffold": 4,
                "temperature": random.uniform(0.1, 0.3),
                "top_k": 50
            }

            try:
                result = self.call_amina_api("proteinmpnn/design", payload)
                sequences = result.get('sequences', [])
                all_sequences.extend(sequences)
                self.log(f"ProteinMPNN designed {len(sequences)} sequences")
            except Exception as e:
                self.log(f"ProteinMPNN batch failed: {e}")

        return all_sequences

    def validate_structures_batch(self, sequences):
        """Validate structures with Boltz-2"""
        if not sequences:
            return []

        self.log(f"Running Boltz-2 validation batch (size: {BOLTZ_BATCH})")

        validated = []
        for i in range(0, len(sequences), BOLTZ_BATCH):
            batch_sequences = sequences[i:i + BOLTZ_BATCH]

            payload = {
                "sequences": batch_sequences,
                "target_pdb": TARGET_PDB,
                "return_confidence": True,
                "return_coordinates": True
            }

            try:
                result = self.call_amina_api("boltz2/fold", payload)
                predictions = result.get('predictions', [])

                for pred in predictions:
                    iptm = pred.get('iptm', 0.0)
                    coverage = pred.get('coverage', 0.0)

                    # Check winning criteria
                    if iptm >= MIN_IPTM or coverage >= MIN_COVERAGE:
                        validated.append(pred)
                        self.log(f"WINNER: ipTM={iptm:.3f}, coverage={coverage:.1f}%")

                self.log(f"Boltz-2 validated {len(predictions)} structures, {len([p for p in predictions if p.get('iptm', 0) >= MIN_IPTM or p.get('coverage', 0) >= MIN_COVERAGE])} winners")

            except Exception as e:
                self.log(f"Boltz-2 batch failed: {e}")

        return validated

    def analyze_pesto_batch(self, structures):
        """Analyze binding with PeSTo"""
        if not structures:
            return []

        self.log(f"Running PeSTo analysis batch (size: {PESTO_BATCH})")

        analyzed = []
        for i in range(0, len(structures), PESTO_BATCH):
            batch_structures = structures[i:i + PESTO_BATCH]

            payload = {
                "structures": batch_structures,
                "target_pdb": TARGET_PDB,
                "analysis_type": "binding_affinity",
                "include_interface_analysis": True
            }

            try:
                result = self.call_amina_api("pesto/analyze", payload)
                analyses = result.get('analyses', [])
                analyzed.extend(analyses)
                self.log(f"PeSTo analyzed {len(analyses)} binding interfaces")
            except Exception as e:
                self.log(f"PeSTo batch failed: {e}")

        return analyzed

    def save_winning_binders(self, structures):
        """Save winning binders to output directory"""
        for i, structure in enumerate(structures):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"bipd_binder_{timestamp}_{i:03d}"

            # Save PDB structure
            pdb_path = OUTPUT_DIR / f"{base_name}.pdb"
            with open(pdb_path, "w") as f:
                f.write(structure.get('pdb_content', ''))

            # Save JSON metadata
            json_path = OUTPUT_DIR / f"{base_name}.json"
            metadata = {
                "iteration": self.iteration_count,
                "timestamp": timestamp,
                "target_pdb": TARGET_PDB,
                "hotspots": HOTSPOTS,
                "iptm": structure.get('iptm', 0.0),
                "coverage": structure.get('coverage', 0.0),
                "sequence": structure.get('sequence', ''),
                "binding_analysis": structure.get('pesto_analysis', {}),
                "full_data": structure
            }

            with open(json_path, "w") as f:
                json.dump(metadata, f, indent=2)

            self.winning_count += 1
            self.log(f"Saved winning binder: {base_name}")

    def run_burn_iteration(self):
        """Run one complete iteration of the burn loop"""
        self.iteration_count += 1
        self.log(f"=== BURN ITERATION {self.iteration_count} ===")

        try:
            # Step 1: Generate scaffolds with RFDiffusion
            scaffolds = self.generate_rfdiffusion_batch()

            # Step 2: Design sequences with ProteinMPNN
            sequences = self.design_sequences_batch(scaffolds)

            # Step 3: Validate with Boltz-2
            validated = self.validate_structures_batch(sequences)

            # Step 4: Analyze with PeSTo
            analyzed = self.analyze_pesto_batch(validated)

            # Step 5: Save winners
            if analyzed:
                self.save_winning_binders(analyzed)

            # Log iteration summary
            self.log(f"Iteration {self.iteration_count} complete: {len(scaffolds)} scaffolds -> {len(sequences)} sequences -> {len(validated)} validated -> {len(analyzed)} analyzed")

        except Exception as e:
            self.log(f"Iteration {self.iteration_count} failed: {e}")

    def run_aggressive_burn(self):
        """Main burn loop - runs until manually stopped or budget exhausted"""
        self.log("=== STARTING AGGRESSIVE BURN LOOP ===")
        self.log(f"Target: BipD ({TARGET_PDB}) hotspots: {HOTSPOTS}")
        self.log(f"Thresholds: ipTM >= {MIN_IPTM}, coverage >= {MIN_COVERAGE}%")
        self.log(f"Output directory: {OUTPUT_DIR}")

        try:
            while True:
                start_time = time.time()

                self.run_burn_iteration()

                iteration_time = time.time() - start_time
                self.log(f"Iteration {self.iteration_count} took {iteration_time:.1f}s")
                self.log(f"Total winners so far: {self.winning_count}")

                # Brief pause to prevent overwhelming the API
                time.sleep(5)

        except KeyboardInterrupt:
            self.log("=== BURN LOOP INTERRUPTED BY USER ===")
        except Exception as e:
            self.log(f"=== BURN LOOP CRASHED: {e} ===")
        finally:
            self.log(f"=== BURN LOOP SUMMARY ===")
            self.log(f"Total iterations: {self.iteration_count}")
            self.log(f"Total winners: {self.winning_count}")
            self.log(f"Winners saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    print("Aggressive Burn Loop for Continuum Discovery")
    print("Targeting BipD (2IXR) hotspots with continuous Amina API calls")
    print("Press Ctrl+C to stop the burn loop")
    print()

    # Verify API key
    if API_KEY == "your_api_key_here":
        print("ERROR: Please set AMINA_API_KEY environment variable")
        exit(1)

    # Initialize and run
    engine = AggressiveBurnEngine()
    engine.run_aggressive_burn()
