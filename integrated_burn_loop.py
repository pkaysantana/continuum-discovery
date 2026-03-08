#!/usr/bin/env python3
"""
Integrated Continuum Discovery Burn Loop
Combines UniBase memory, OpenClaw biosecurity, and Anyways economy
"""

import os
import json
import time
import requests
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import our new systems
import sys
sys.path.append('.')
from unibase.memory_manager import UniBaseMemoryManager
from openclaw.biosecurity_scanner import BiosecurityScanner
from anyways.agent_economy import AnyWaysAgentEconomy

# Configuration
AMINA_API_BASE = "https://api.aminoanalytica.com/v1"
API_KEY = os.getenv("AMINA_API_KEY", "your_api_key_here")
OUTPUT_DIR = Path("output/winning_binders")
LOGS_DIR = Path("logs/integrated_burn")

# Target: BipD (2IXR) hotspots
TARGET_PDB = "2IXR"
HOTSPOTS = [128, 135, 142, 156, 166, 243, 256, 289, 301]

class IntegratedContinuumDiscovery:
    """
    Fully integrated Continuum Discovery system with all components
    """

    def __init__(self, initial_credits: float = 17.82):
        print("=== INITIALIZING CONTINUUM DISCOVERY PLATFORM ===")

        # Core systems
        self.memory_manager = UniBaseMemoryManager()
        self.biosecurity_scanner = BiosecurityScanner()
        self.agent_economy = AnyWaysAgentEconomy(initial_credits)

        # API session
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        })

        # Counters
        self.iteration_count = 0
        self.winning_count = 0
        self.blocked_count = 0
        self.memory_skipped = 0

        # Ensure output directories exist
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

        print(f"✓ Memory system initialized: {self.memory_manager.get_memory_stats()}")
        print(f"✓ Biosecurity scanner ready: {self.biosecurity_scanner.get_screening_stats()}")
        print(f"✓ Agent economy initialized: ${self.agent_economy.current_credits:.4f} credits")

    def log(self, message: str):
        """Enhanced logging with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)

        # Write to log file
        with open(LOGS_DIR / "integrated_burn_log.txt", "a") as f:
            f.write(log_entry + "\n")

    def call_amina_api(self, endpoint: str, payload: Dict, timeout: int = 300) -> Optional[Dict]:
        """Make API call with retry logic and cost tracking"""
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
                time.sleep(2 ** attempt)

    def generate_rfdiffusion_batch(self) -> List[Dict]:
        """Generate scaffold structures with economy optimization"""
        # Get optimal batch size from economy
        optimal_batch, efficiency = self.agent_economy.optimize_batch_size('rfdiffusion', self.agent_economy.current_credits)

        self.log(f"Running RFDiffusion (optimal batch: {optimal_batch}, expected efficiency: {efficiency:.3f})")

        # Randomize hotspot selection for diversity
        selected_hotspots = random.sample(HOTSPOTS, min(5, len(HOTSPOTS)))

        payload = {
            "target_pdb": TARGET_PDB,
            "hotspots": selected_hotspots,
            "num_designs": optimal_batch,
            "diffusion_steps": 50,
            "scaffold_length": random.randint(80, 150),
            "temperature": random.uniform(0.8, 1.2)
        }

        try:
            result = self.call_amina_api("rfdiffusion/generate", payload)
            designs = result.get('designs', [])

            # Record operation in economy
            self.agent_economy.record_operation('rfdiffusion', optimal_batch, designs)

            self.log(f"RFDiffusion generated {len(designs)} scaffolds")
            return designs
        except Exception as e:
            self.log(f"RFDiffusion batch failed: {e}")
            return []

    def design_sequences_batch(self, scaffolds: List[Dict]) -> List[Dict]:
        """Design sequences with memory checking and economy optimization"""
        if not scaffolds:
            return []

        # Get optimal batch size
        optimal_batch, _ = self.agent_economy.optimize_batch_size('proteinmpnn', self.agent_economy.current_credits)

        self.log(f"Running ProteinMPNN (batch: {optimal_batch})")

        all_sequences = []
        for i in range(0, len(scaffolds), optimal_batch):
            batch_scaffolds = scaffolds[i:i + optimal_batch]

            payload = {
                "scaffolds": batch_scaffolds,
                "num_sequences_per_scaffold": 4,
                "temperature": random.uniform(0.1, 0.3),
                "top_k": 50
            }

            try:
                result = self.call_amina_api("proteinmpnn/design", payload)
                sequences = result.get('sequences', [])

                # Check sequences against memory before proceeding
                filtered_sequences = []
                for seq_data in sequences:
                    sequence = seq_data.get('sequence', '')
                    if self.memory_manager.is_sequence_known_failure(sequence):
                        self.memory_skipped += 1
                        self.log(f"MEMORY: Skipped known failure pattern")
                    else:
                        filtered_sequences.append(seq_data)

                # Record operation in economy
                self.agent_economy.record_operation('proteinmpnn', len(batch_scaffolds), filtered_sequences)

                all_sequences.extend(filtered_sequences)
                self.log(f"ProteinMPNN: {len(sequences)} designed, {len(filtered_sequences)} after memory filtering")

            except Exception as e:
                self.log(f"ProteinMPNN batch failed: {e}")

        return all_sequences

    def validate_structures_batch(self, sequences: List[Dict]) -> List[Dict]:
        """Validate structures with Boltz-2 and biosecurity screening"""
        if not sequences:
            return []

        # Get optimal batch size
        optimal_batch, _ = self.agent_economy.optimize_batch_size('boltz2', self.agent_economy.current_credits)

        self.log(f"Running Boltz-2 validation (batch: {optimal_batch})")

        validated = []
        for i in range(0, len(sequences), optimal_batch):
            batch_sequences = sequences[i:i + optimal_batch]

            payload = {
                "sequences": batch_sequences,
                "target_pdb": TARGET_PDB,
                "return_confidence": True,
                "return_coordinates": True
            }

            try:
                result = self.call_amina_api("boltz2/fold", payload)
                predictions = result.get('predictions', [])

                # Biosecurity screening for each prediction
                biosecurity_passed = []
                for pred in predictions:
                    sequence = pred.get('sequence', '')
                    if sequence:
                        is_safe, security_report = self.biosecurity_scanner.is_sequence_safe_for_synthesis(sequence)

                        if not is_safe:
                            self.blocked_count += 1
                            self.log(f"BIOSECURITY: BLOCKED sequence (risk score: {security_report['risk_score']:.1f})")
                            continue

                        # Add biosecurity info to prediction
                        pred['biosecurity_report'] = security_report
                        biosecurity_passed.append(pred)

                # Check winning criteria for sequences that passed biosecurity
                for pred in biosecurity_passed:
                    iptm = pred.get('iptm', 0.0)
                    coverage = pred.get('coverage', 0.0)

                    # Check if this is a failure to record in memory
                    if iptm < 0.70 and coverage < 70.0:
                        sequence = pred.get('sequence', '')
                        if sequence:
                            self.memory_manager.record_failure(
                                sequence,
                                f"Low confidence: ipTM={iptm:.3f}, coverage={coverage:.1f}%",
                                iptm,
                                coverage
                            )

                    # Check winning criteria
                    elif iptm >= 0.70 or coverage >= 70.0:
                        validated.append(pred)
                        self.log(f"WINNER: ipTM={iptm:.3f}, coverage={coverage:.1f}%")

                # Record operation in economy
                self.agent_economy.record_operation('boltz2', len(batch_sequences), biosecurity_passed)

                self.log(f"Boltz-2: {len(predictions)} validated, {len(biosecurity_passed)} passed security, {len([p for p in biosecurity_passed if p.get('iptm', 0) >= 0.70 or p.get('coverage', 0) >= 70.0])} winners")

            except Exception as e:
                self.log(f"Boltz-2 batch failed: {e}")

        return validated

    def analyze_pesto_batch(self, structures: List[Dict]) -> List[Dict]:
        """Analyze binding with PeSTo"""
        if not structures:
            return []

        # Get optimal batch size
        optimal_batch, _ = self.agent_economy.optimize_batch_size('pesto', self.agent_economy.current_credits)

        self.log(f"Running PeSTo analysis (batch: {optimal_batch})")

        analyzed = []
        for i in range(0, len(structures), optimal_batch):
            batch_structures = structures[i:i + optimal_batch]

            payload = {
                "structures": batch_structures,
                "target_pdb": TARGET_PDB,
                "analysis_type": "binding_affinity",
                "include_interface_analysis": True
            }

            try:
                result = self.call_amina_api("pesto/analyze", payload)
                analyses = result.get('analyses', [])

                # Record successes in memory
                for analysis in analyses:
                    sequence = analysis.get('sequence', '')
                    iptm = analysis.get('iptm', 0.0)
                    coverage = analysis.get('coverage', 0.0)
                    binding_affinity = analysis.get('binding_affinity', 0.0)

                    if sequence and (iptm >= 0.70 or coverage >= 70.0):
                        pdb_path = f"output/winning_binders/{self.compute_sequence_hash(sequence)}.pdb"
                        self.memory_manager.record_success(sequence, iptm, coverage, binding_affinity, pdb_path)

                # Record operation in economy
                self.agent_economy.record_operation('pesto', len(batch_structures), analyses)

                analyzed.extend(analyses)
                self.log(f"PeSTo analyzed {len(analyses)} binding interfaces")

            except Exception as e:
                self.log(f"PeSTo batch failed: {e}")

        return analyzed

    def compute_sequence_hash(self, sequence: str) -> str:
        """Compute hash for sequence"""
        import hashlib
        return hashlib.sha256(sequence.encode()).hexdigest()[:16]

    def save_winning_binders(self, structures: List[Dict]):
        """Save winning binders with full metadata"""
        for i, structure in enumerate(structures):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sequence_hash = self.compute_sequence_hash(structure.get('sequence', ''))
            base_name = f"integrated_binder_{timestamp}_{sequence_hash}_{i:03d}"

            # Save PDB structure
            pdb_path = OUTPUT_DIR / f"{base_name}.pdb"
            with open(pdb_path, "w") as f:
                f.write(structure.get('pdb_content', '# No structure data available\n'))

            # Save comprehensive JSON metadata
            json_path = OUTPUT_DIR / f"{base_name}.json"
            metadata = {
                'iteration': self.iteration_count,
                'timestamp': timestamp,
                'target_pdb': TARGET_PDB,
                'hotspots': HOTSPOTS,
                'sequence_hash': sequence_hash,
                'iptm': structure.get('iptm', 0.0),
                'coverage': structure.get('coverage', 0.0),
                'sequence': structure.get('sequence', ''),
                'binding_analysis': structure.get('pesto_analysis', {}),
                'biosecurity_report': structure.get('biosecurity_report', {}),
                'economy_efficiency': self.agent_economy.get_economy_stats()['overall_efficiency'],
                'full_data': structure
            }

            with open(json_path, "w") as f:
                json.dump(metadata, f, indent=2)

            self.winning_count += 1
            self.log(f"Saved winning binder: {base_name}")

    def run_integrated_discovery_iteration(self):
        """Run one complete iteration with all systems integrated"""
        self.iteration_count += 1
        self.log(f"=== INTEGRATED ITERATION {self.iteration_count} ===")

        try:
            # Step 1: Generate scaffolds with RFDiffusion
            scaffolds = self.generate_rfdiffusion_batch()

            # Step 2: Design sequences with ProteinMPNN (with memory filtering)
            sequences = self.design_sequences_batch(scaffolds)

            # Step 3: Validate with Boltz-2 (with biosecurity screening)
            validated = self.validate_structures_batch(sequences)

            # Step 4: Analyze with PeSTo
            analyzed = self.analyze_pesto_batch(validated)

            # Step 5: Save winners
            if analyzed:
                self.save_winning_binders(analyzed)

            # Show comprehensive stats
            self.log(f"Iteration {self.iteration_count} complete:")
            self.log(f"  Pipeline: {len(scaffolds)} scaffolds → {len(sequences)} sequences → {len(validated)} validated → {len(analyzed)} analyzed")
            self.log(f"  Memory skipped: {self.memory_skipped} duplicates")
            self.log(f"  Biosecurity blocked: {self.blocked_count} dangerous")
            self.log(f"  Total winners: {self.winning_count}")

            # Economic status
            economy_stats = self.agent_economy.get_economy_stats()
            self.log(f"  Credits: ${economy_stats['current_credits']:.4f} remaining, efficiency: {economy_stats['overall_efficiency']:.3f}")

        except Exception as e:
            self.log(f"Iteration {self.iteration_count} failed: {e}")

    def run_continuous_discovery(self):
        """Main continuous discovery loop"""
        self.log("=== STARTING INTEGRATED CONTINUUM DISCOVERY ===")
        self.log(f"Target: BipD ({TARGET_PDB}) hotspots: {HOTSPOTS}")
        self.log(f"Initial credits: ${self.agent_economy.current_credits:.4f}")
        self.log(f"Output directory: {OUTPUT_DIR}")

        start_time = time.time()

        try:
            while self.agent_economy.current_credits > 1.0:  # Keep $1 buffer
                iteration_start = time.time()

                self.run_integrated_discovery_iteration()

                iteration_time = time.time() - iteration_start
                self.log(f"Iteration {self.iteration_count} took {iteration_time:.1f}s")

                # Brief pause to prevent overwhelming APIs
                time.sleep(2)

        except KeyboardInterrupt:
            self.log("=== DISCOVERY INTERRUPTED BY USER ===")
        except Exception as e:
            self.log(f"=== DISCOVERY CRASHED: {e} ===")
        finally:
            self.print_final_summary(start_time)

    def print_final_summary(self, start_time: float):
        """Print comprehensive final summary"""
        runtime = time.time() - start_time

        self.log("\n" + "="*80)
        self.log("🧬 CONTINUUM DISCOVERY PLATFORM - FINAL SUMMARY 🧬")
        self.log("="*80)

        # Discovery stats
        self.log(f"DISCOVERY RESULTS:")
        self.log(f"  Total iterations: {self.iteration_count}")
        self.log(f"  Winning binders: {self.winning_count}")
        self.log(f"  Success rate: {self.winning_count/max(1,self.iteration_count)*100:.1f}%")
        self.log(f"  Runtime: {runtime:.0f} seconds")

        # Memory system stats
        memory_stats = self.memory_manager.get_memory_stats()
        self.log(f"\nUNIBASE MEMORY SYSTEM:")
        self.log(f"  Failed designs tracked: {memory_stats['failed_designs']}")
        self.log(f"  Successful designs: {memory_stats['successful_designs']}")
        self.log(f"  Duplicates skipped: {self.memory_skipped}")

        # Biosecurity stats
        security_stats = self.biosecurity_scanner.get_screening_stats()
        self.log(f"\nOPENCLAW BIOSECURITY:")
        self.log(f"  Sequences screened: {security_stats['total_screenings']}")
        self.log(f"  Dangerous sequences blocked: {self.blocked_count}")

        # Economic stats
        economy_stats = self.agent_economy.get_economy_stats()
        self.log(f"\nANYWAYS AGENT ECONOMY:")
        self.log(f"  Credits spent: ${economy_stats['total_spent']:.4f}")
        self.log(f"  Credits earned: ${economy_stats['total_earned']:.4f}")
        self.log(f"  Net profit: ${economy_stats['net_profit']:.4f}")
        self.log(f"  Overall efficiency: {economy_stats['overall_efficiency']:.3f}")

        self.log(f"\nOUTPUT: {self.winning_count} validated binders saved to {OUTPUT_DIR}")
        self.log("="*80)

if __name__ == "__main__":
    print("🧬 CONTINUUM DISCOVERY PLATFORM - INTEGRATED VERSION 🧬")
    print("Press Ctrl+C to stop the discovery loop")
    print()

    # Verify API key
    if API_KEY == "your_api_key_here":
        print("ERROR: Please set AMINA_API_KEY environment variable")
        exit(1)

    # Initialize and run
    discovery_engine = IntegratedContinuumDiscovery(initial_credits=17.82)
    discovery_engine.run_continuous_discovery()
