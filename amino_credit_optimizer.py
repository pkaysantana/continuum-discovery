#!/usr/bin/env python3
"""
Amino Analytica Credit Optimization Engine
Maximize "credits earned" per "compute spent" for Continuum Discovery platform

Target: H5N1 Hemagglutinin head domain (PDB: 2IBX) high-affinity binder discovery
Strategy: Optimized batch processing + UniBase failure avoidance + OpenClaw biosecurity
Hardware: RTX 5070 Ti (16GB VRAM) + 64GB RAM optimized batching
"""

import sys
import os
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@dataclass
class CreditOptimizationConfig:
    """Credit optimization configuration for amino analytica"""
    target_pdb: str = "2IBX"  # H5N1 Hemagglutinin head domain
    target_hotspots: List[int] = None  # H5N1 HA binding hotspots
    batch_size: int = 4  # Optimized for RTX 5070 Ti 16GB VRAM
    max_concurrent_jobs: int = 2  # Memory-efficient for 64GB RAM
    credit_efficiency_threshold: float = 0.75  # Minimum credits/compute ratio
    high_affinity_threshold: float = 0.85  # ipTM threshold for credit earning
    biosecurity_required: bool = True  # OpenClaw mandatory

    def __post_init__(self):
        if self.target_hotspots is None:
            # H5N1 HA receptor binding domain hotspots (key residues for human infection)
            self.target_hotspots = [138, 153, 155, 183, 190, 194, 225, 226, 228]

class UniBaseFailureTracker:
    """Track failed designs to avoid wasted compute"""

    def __init__(self, log_dir: str = "unibase_logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.failure_db_path = os.path.join(log_dir, "failed_sequences.json")
        self.topology_cache_path = os.path.join(log_dir, "topology_fingerprints.json")
        self.failed_sequences = self._load_failure_db()
        self.topology_fingerprints = self._load_topology_cache()

        self.logger = logging.getLogger('unibase_tracker')

    def _load_failure_db(self) -> Set[str]:
        """Load previously failed sequences"""
        if os.path.exists(self.failure_db_path):
            with open(self.failure_db_path, 'r') as f:
                data = json.load(f)
                return set(data.get('failed_sequences', []))
        return set()

    def _load_topology_cache(self) -> Dict[str, str]:
        """Load topology fingerprint cache"""
        if os.path.exists(self.topology_cache_path):
            with open(self.topology_cache_path, 'r') as f:
                return json.load(f)
        return {}

    def generate_topology_fingerprint(self, sequence: str) -> str:
        """Generate topological fingerprint for sequence convergence detection"""
        # Simple topology fingerprint based on sequence properties
        aa_props = {
            'A': 'h', 'V': 'h', 'I': 'h', 'L': 'h', 'M': 'h', 'F': 'h', 'Y': 'h', 'W': 'h',  # Hydrophobic
            'S': 'p', 'T': 'p', 'N': 'p', 'Q': 'p', 'C': 'p',  # Polar
            'D': 'n', 'E': 'n',  # Negative
            'K': '+', 'R': '+', 'H': '+',  # Positive
            'G': 'g', 'P': 'p'  # Special
        }

        # Generate property sequence
        prop_seq = ''.join(aa_props.get(aa, 'x') for aa in sequence)

        # Generate fingerprint from property patterns
        fingerprint_data = {
            'length': len(sequence),
            'hydrophobic_clusters': self._find_clusters(prop_seq, 'h'),
            'charged_clusters': self._find_clusters(prop_seq, ['+', 'n']),
            'polar_distribution': prop_seq.count('p') / len(sequence),
            'charge_ratio': (prop_seq.count('+') - prop_seq.count('n')) / len(sequence)
        }

        # Hash fingerprint
        fingerprint = hashlib.sha256(json.dumps(fingerprint_data, sort_keys=True).encode()).hexdigest()[:16]
        return fingerprint

    def _find_clusters(self, prop_seq: str, target_props: str) -> List[int]:
        """Find clusters of target properties"""
        if isinstance(target_props, str):
            target_props = [target_props]

        clusters = []
        current_cluster = 0

        for prop in prop_seq:
            if prop in target_props:
                current_cluster += 1
            else:
                if current_cluster >= 3:  # Minimum cluster size
                    clusters.append(current_cluster)
                current_cluster = 0

        if current_cluster >= 3:
            clusters.append(current_cluster)

        return clusters

    def is_sequence_failed(self, sequence: str) -> bool:
        """Check if sequence has previously failed"""
        return sequence in self.failed_sequences

    def is_topology_explored(self, sequence: str) -> Tuple[bool, Optional[str]]:
        """Check if sequence topology has been explored"""
        fingerprint = self.generate_topology_fingerprint(sequence)

        if fingerprint in self.topology_fingerprints:
            previous_sequence = self.topology_fingerprints[fingerprint]
            return True, previous_sequence

        return False, None

    def log_failure(self, sequence: str, failure_type: str, metrics: Dict = None):
        """Log failed sequence to avoid future waste"""
        self.failed_sequences.add(sequence)
        fingerprint = self.generate_topology_fingerprint(sequence)
        self.topology_fingerprints[fingerprint] = sequence

        # Save to persistent storage
        failure_data = {
            'failed_sequences': list(self.failed_sequences),
            'last_updated': datetime.now(timezone.utc).isoformat()
        }

        with open(self.failure_db_path, 'w') as f:
            json.dump(failure_data, f, indent=2)

        with open(self.topology_cache_path, 'w') as f:
            json.dump(self.topology_fingerprints, f, indent=2)

        self.logger.info(f"Logged failure: {failure_type} for sequence length {len(sequence)}")

class OpenClawBiosecurity:
    """OpenClaw biosecurity guardrails for amino analytica"""

    def __init__(self):
        self.toxin_patterns = self._load_toxin_patterns()
        self.virulence_signatures = self._load_virulence_signatures()
        self.approved_targets = {"2IBX"}  # Only H5N1 HA approved for safety

    def _load_toxin_patterns(self) -> List[str]:
        """Load known toxin sequence patterns"""
        # Simplified toxin pattern database
        return [
            "CWTKSIPPKPCF",  # Conotoxin pattern
            "PYCC",  # Cytotoxin motif
            "KKYRYHLKPFCKK",  # Neurotoxin pattern
            "GGGCCWT"  # Membrane toxin
        ]

    def _load_virulence_signatures(self) -> List[str]:
        """Load virulence factor signatures"""
        return [
            "TTSS",  # Type III secretion
            "HEMOLYSIN",  # Hemolysin signatures
            "INVASIN",  # Invasion proteins
            "ADHERENCE"  # Adhesion factors
        ]

    def screen_sequence(self, sequence: str, target_pdb: str = "2IBX") -> Tuple[bool, float, str]:
        """
        Screen sequence for biosecurity compliance
        Returns: (is_safe, safety_score, safety_report)
        """

        safety_score = 1.0
        safety_issues = []

        # 1. Target validation
        if target_pdb not in self.approved_targets:
            safety_score = 0.0
            safety_issues.append(f"Unauthorized target: {target_pdb}")

        # 2. Toxin pattern screening
        for pattern in self.toxin_patterns:
            if pattern in sequence:
                safety_score *= 0.1  # Major penalty for toxin patterns
                safety_issues.append(f"Potential toxin pattern: {pattern}")

        # 3. Virulence signature screening
        for signature in self.virulence_signatures:
            if signature in sequence.upper():
                safety_score *= 0.3
                safety_issues.append(f"Virulence signature detected: {signature}")

        # 4. Structural homology screening (simplified)
        if self._has_dangerous_structural_motifs(sequence):
            safety_score *= 0.2
            safety_issues.append("Dangerous structural motif detected")

        # 5. Length-based risk assessment
        if len(sequence) > 500:  # Very large proteins can be risky
            safety_score *= 0.8
            safety_issues.append("Large protein size increases risk")

        is_safe = safety_score >= 0.7  # Threshold for approval

        safety_report = {
            'safety_score': safety_score,
            'is_approved': is_safe,
            'target_approved': target_pdb in self.approved_targets,
            'issues': safety_issues,
            'screening_timestamp': datetime.now(timezone.utc).isoformat()
        }

        return is_safe, safety_score, json.dumps(safety_report, indent=2)

    def _has_dangerous_structural_motifs(self, sequence: str) -> bool:
        """Check for dangerous structural motifs"""
        # Simplified check for membrane disruption patterns
        membrane_disruptors = ["WWWW", "FFFF", "CCCC"]  # Hydrophobic clusters

        for pattern in membrane_disruptors:
            if pattern in sequence:
                return True

        # Check for excessive positive charge (can be membrane-disrupting)
        positive_aa = sequence.count('K') + sequence.count('R')
        if positive_aa / len(sequence) > 0.3:  # >30% positive charge
            return True

        return False

class AminoAnalyticaCreditEngine:
    """Main credit optimization engine for amino analytica platform"""

    def __init__(self, config: CreditOptimizationConfig = None):
        self.config = config or CreditOptimizationConfig()
        self.failure_tracker = UniBaseFailureTracker()
        self.biosecurity = OpenClawBiosecurity()

        # Credit tracking
        self.credits_earned = 0
        self.compute_spent = 0
        self.successful_designs = []

        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('amino_credit_engine')

        # Create output directories
        os.makedirs("outputs/winning_binders", exist_ok=True)
        os.makedirs("outputs/credit_optimization", exist_ok=True)

        self.logger.info(f"Amino Analytica Credit Engine initialized")
        self.logger.info(f"Target: {self.config.target_pdb} (H5N1 Hemagglutinin)")
        self.logger.info(f"Batch size optimized for RTX 5070 Ti: {self.config.batch_size}")

    def pre_filter_sequence_batch(self, sequence_candidates: List[str]) -> List[str]:
        """Pre-filter sequences to avoid wasted compute"""

        filtered_sequences = []

        for sequence in sequence_candidates:
            # 1. Check failure history
            if self.failure_tracker.is_sequence_failed(sequence):
                self.logger.debug(f"Skipping previously failed sequence (length {len(sequence)})")
                continue

            # 2. Check topology convergence
            is_explored, previous_seq = self.failure_tracker.is_topology_explored(sequence)
            if is_explored:
                self.logger.debug(f"Skipping topologically similar sequence to {previous_seq[:20]}...")
                continue

            # 3. Biosecurity screening
            is_safe, safety_score, safety_report = self.biosecurity.screen_sequence(sequence, self.config.target_pdb)
            if not is_safe:
                self.logger.warning(f"Biosecurity failed for sequence: safety_score={safety_score:.3f}")
                continue

            filtered_sequences.append(sequence)

        self.logger.info(f"Pre-filtering: {len(sequence_candidates)} → {len(filtered_sequences)} sequences")
        return filtered_sequences

    def estimate_credit_potential(self, sequence: str, predicted_iptm: float = None) -> float:
        """Estimate credit earning potential for sequence"""

        base_credits = 10.0  # Base credits for high-affinity binder

        # Adjust based on predicted performance
        if predicted_iptm:
            if predicted_iptm >= self.config.high_affinity_threshold:
                credit_multiplier = 2.0 + (predicted_iptm - self.config.high_affinity_threshold) * 10
            else:
                credit_multiplier = predicted_iptm / self.config.high_affinity_threshold
        else:
            credit_multiplier = 1.0  # Default for unknown prediction

        # Bonus for H5N1 target (high priority)
        target_bonus = 1.5 if self.config.target_pdb == "2IBX" else 1.0

        # Novelty bonus (inverse of exploration level)
        novelty_bonus = 1.2  # Default for new sequences

        estimated_credits = base_credits * credit_multiplier * target_bonus * novelty_bonus
        return estimated_credits

    def optimize_batch_for_gpu(self, sequences: List[str]) -> List[List[str]]:
        """Optimize sequence batches for RTX 5070 Ti memory constraints"""

        # Sort by length for efficient memory usage
        sorted_sequences = sorted(sequences, key=len)

        batches = []
        current_batch = []
        current_memory_estimate = 0

        # Estimate: ~100MB per 150-residue protein for Boltz-2
        memory_per_residue = 0.67  # MB
        max_batch_memory = 12000  # 12GB of 16GB VRAM (leave buffer)

        for seq in sorted_sequences:
            seq_memory = len(seq) * memory_per_residue

            if current_memory_estimate + seq_memory <= max_batch_memory and len(current_batch) < self.config.batch_size:
                current_batch.append(seq)
                current_memory_estimate += seq_memory
            else:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [seq]
                current_memory_estimate = seq_memory

        if current_batch:
            batches.append(current_batch)

        self.logger.info(f"GPU batch optimization: {len(sequences)} sequences → {len(batches)} batches")
        return batches

    def calculate_credit_efficiency(self) -> float:
        """Calculate current credits earned per compute spent ratio"""
        if self.compute_spent == 0:
            return 0.0

        return self.credits_earned / self.compute_spent

    def log_successful_design(self, sequence: str, metrics: Dict):
        """Log successful design and calculate credits earned"""

        iptm_score = metrics.get('iptm_score', 0.0)

        if iptm_score >= self.config.high_affinity_threshold:
            # Calculate credits earned
            credits = self.estimate_credit_potential(sequence, iptm_score)
            self.credits_earned += credits

            design_record = {
                'sequence': sequence,
                'iptm_score': iptm_score,
                'credits_earned': credits,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'target': self.config.target_pdb,
                'hotspot_coverage': metrics.get('hotspot_coverage_percent', 0.0)
            }

            self.successful_designs.append(design_record)

            self.logger.info(f"CREDITS EARNED: +{credits:.1f} for ipTM {iptm_score:.3f} sequence")
            self.logger.info(f"Total credits: {self.credits_earned:.1f} | Efficiency: {self.calculate_credit_efficiency():.3f}")

            return credits

        return 0.0

    def log_compute_spent(self, compute_units: float):
        """Log compute units spent"""
        self.compute_spent += compute_units

    def should_continue_optimization(self) -> bool:
        """Determine if optimization should continue based on efficiency"""

        if len(self.successful_designs) < 5:  # Need minimum sample size
            return True

        efficiency = self.calculate_credit_efficiency()
        return efficiency >= self.config.credit_efficiency_threshold

    def generate_optimization_report(self) -> Dict:
        """Generate comprehensive optimization report"""

        report = {
            'optimization_summary': {
                'total_credits_earned': self.credits_earned,
                'total_compute_spent': self.compute_spent,
                'credit_efficiency': self.calculate_credit_efficiency(),
                'successful_designs': len(self.successful_designs),
                'target_pdb': self.config.target_pdb
            },
            'top_designs': sorted(
                self.successful_designs,
                key=lambda x: x['iptm_score'],
                reverse=True
            )[:10],
            'optimization_config': {
                'batch_size': self.config.batch_size,
                'high_affinity_threshold': self.config.high_affinity_threshold,
                'efficiency_threshold': self.config.credit_efficiency_threshold
            },
            'failure_avoidance': {
                'sequences_filtered': len(self.failure_tracker.failed_sequences),
                'topologies_tracked': len(self.failure_tracker.topology_fingerprints)
            }
        }

        # Save report
        report_path = f"outputs/credit_optimization/optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Optimization report saved: {report_path}")
        return report


def create_optimized_h5n1_target_config() -> CreditOptimizationConfig:
    """Create optimized configuration for H5N1 Hemagglutinin targeting"""

    return CreditOptimizationConfig(
        target_pdb="2IBX",  # H5N1 Hemagglutinin head domain
        target_hotspots=[138, 153, 155, 183, 190, 194, 225, 226, 228],  # HA receptor binding sites
        batch_size=4,  # Optimized for RTX 5070 Ti
        max_concurrent_jobs=2,  # Memory management for 64GB RAM
        credit_efficiency_threshold=0.85,  # High efficiency target
        high_affinity_threshold=0.87,  # Stringent affinity requirement
        biosecurity_required=True
    )


# Main optimization execution
if __name__ == "__main__":
    print("🧬 Amino Analytica Credit Optimization Engine")
    print("=" * 60)

    # Initialize optimized configuration for H5N1
    config = create_optimized_h5n1_target_config()
    credit_engine = AminoAnalyticaCreditEngine(config)

    print(f"🎯 Target: H5N1 Hemagglutinin (PDB: {config.target_pdb})")
    print(f"⚡ GPU Optimization: RTX 5070 Ti (batch size: {config.batch_size})")
    print(f"🔒 Biosecurity: OpenClaw guardrails enabled")
    print(f"📊 Credit Threshold: ipTM ≥ {config.high_affinity_threshold}")
    print(f"💰 Efficiency Target: {config.credit_efficiency_threshold:.0%} credits/compute")

    print("\n🚀 Ready for amino analytica credit maximization!")
    print("Next: Run optimized pipeline with failure avoidance and batch processing")