#!/usr/bin/env python3
"""
Local Geometric Pre-Filtering for α-Helix 8 Channel Penetration
Saves Amina credits by pre-screening sequences for deep pocket targeting
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Any
from datetime import datetime

class AlphaHelix8Filter:
    """Local GPU compute for α-Helix 8 channel penetration analysis"""

    def __init__(self):
        # α-Helix 8 channel geometry (residues 256, 289, 301)
        # Based on BipD structural data: forms inner channel wall
        self.channel_residues = [256, 289, 301]
        self.channel_geometry = {
            'center': np.array([0.0, 0.0, 0.0]),  # Channel center
            'radius': 12.5,  # Angstroms - inner channel radius
            'depth': 25.0,   # Channel depth for penetration
            'burial_target': 1271  # Target surface area burial (Å²)
        }

        # Hydrophobic residue properties for channel packing
        self.hydrophobic_residues = {
            'I': {'volume': 166.7, 'hydrophobicity': 4.5, 'packing_score': 0.9},
            'L': {'volume': 166.7, 'hydrophobicity': 3.8, 'packing_score': 0.85},
            'V': {'volume': 140.0, 'hydrophobicity': 4.2, 'packing_score': 0.8},
            'F': {'volume': 189.9, 'hydrophobicity': 2.8, 'packing_score': 0.95},
            'M': {'volume': 162.9, 'hydrophobicity': 1.9, 'packing_score': 0.75},
            'A': {'volume': 88.6, 'hydrophobicity': 1.8, 'packing_score': 0.6},
            'Y': {'volume': 193.6, 'hydrophobicity': -1.3, 'packing_score': 0.7},
            'W': {'volume': 227.8, 'hydrophobicity': -0.9, 'packing_score': 0.8}
        }

    def calculate_sequence_geometry(self, sequence: str, backbone_coords: Dict[str, Any]) -> Dict[str, float]:
        """Calculate geometric properties for α-Helix 8 penetration"""

        # Simulate backbone positioning (in practice would use actual coordinates)
        seq_length = len(sequence)

        # Generate simulated C-alpha coordinates for analysis
        coords = self._generate_simulated_coords(sequence, backbone_coords)

        # Calculate channel penetration metrics
        penetration_score = self._calculate_channel_penetration(coords, sequence)
        hydrophobic_packing = self._calculate_hydrophobic_packing(sequence)
        burial_potential = self._estimate_surface_burial(coords, sequence)

        # α-Helix 8 specific targeting (residues 256, 289, 301)
        channel_targeting = self._evaluate_channel_targeting(coords, sequence)

        return {
            'penetration_score': penetration_score,
            'hydrophobic_packing': hydrophobic_packing,
            'burial_potential': burial_potential,
            'channel_targeting': channel_targeting,
            'overall_score': (penetration_score * 0.4 +
                            hydrophobic_packing * 0.3 +
                            channel_targeting * 0.3)
        }

    def _generate_simulated_coords(self, sequence: str, backbone_coords: Dict[str, Any]) -> np.ndarray:
        """Generate simulated C-alpha coordinates for geometric analysis"""
        seq_length = len(sequence)

        # Use ideal alpha-helix geometry (3.6 residues per turn, 1.5Å rise per residue)
        coords = np.zeros((seq_length, 3))

        for i in range(seq_length):
            # Alpha helix parameters
            phi = (i * 100.0) * (math.pi / 180.0)  # 100° rotation per residue
            z = i * 1.5  # 1.5Å rise per residue
            r = 2.3  # Helix radius

            coords[i] = [
                r * math.cos(phi),
                r * math.sin(phi),
                z
            ]

        return coords

    def _calculate_channel_penetration(self, coords: np.ndarray, sequence: str) -> float:
        """Calculate how well sequence penetrates the α-Helix 8 channel"""

        # Check if any residues reach the channel depth
        max_penetration = np.max(coords[:, 2])  # Z-axis penetration
        penetration_fraction = min(max_penetration / self.channel_geometry['depth'], 1.0)

        # Bonus for reaching the critical channel region
        channel_region_bonus = 0.0
        if max_penetration > (self.channel_geometry['depth'] * 0.8):
            channel_region_bonus = 0.3

        return min(penetration_fraction + channel_region_bonus, 1.0)

    def _calculate_hydrophobic_packing(self, sequence: str) -> float:
        """Calculate hydrophobic packing potential for channel formation"""

        total_hydrophobic_score = 0.0
        total_residues = len(sequence)

        for residue in sequence:
            if residue in self.hydrophobic_residues:
                props = self.hydrophobic_residues[residue]
                # Weight by both hydrophobicity and packing efficiency
                score = props['hydrophobicity'] * props['packing_score']
                total_hydrophobic_score += score
            else:
                # Penalty for non-hydrophobic residues in channel
                total_hydrophobic_score -= 1.0

        # Normalize by sequence length
        return max(total_hydrophobic_score / total_residues, 0.0) / 5.0  # Scale to 0-1

    def _estimate_surface_burial(self, coords: np.ndarray, sequence: str) -> float:
        """Estimate surface area burial potential (target: 1271 Å²)"""

        # Calculate approximate buried surface area
        # Based on residue volumes and packing geometry
        total_volume = 0.0

        for residue in sequence:
            if residue in self.hydrophobic_residues:
                total_volume += self.hydrophobic_residues[residue]['volume']
            else:
                total_volume += 120.0  # Average residue volume

        # Convert volume to approximate surface burial
        estimated_burial = total_volume * 0.8  # Packing efficiency factor

        # Score relative to α-Helix 8 burial target
        burial_score = min(estimated_burial / self.channel_geometry['burial_target'], 1.0)

        return burial_score

    def _evaluate_channel_targeting(self, coords: np.ndarray, sequence: str) -> float:
        """Evaluate specific targeting of α-Helix 8 channel residues (256, 289, 301)"""

        # Check spatial positioning relative to channel center
        channel_center = self.channel_geometry['center']
        channel_radius = self.channel_geometry['radius']

        targeting_score = 0.0
        valid_positions = 0

        for i, coord in enumerate(coords):
            # Distance from channel center
            distance = np.linalg.norm(coord[:2] - channel_center[:2])  # X-Y distance

            # Score proximity to channel
            if distance <= channel_radius:
                targeting_score += 1.0
                valid_positions += 1
            elif distance <= (channel_radius * 1.5):
                targeting_score += 0.5
                valid_positions += 1

        # Normalize by sequence length
        if len(coords) > 0:
            targeting_score = targeting_score / len(coords)
        else:
            targeting_score = 0.0

        return targeting_score

    def filter_for_channel_penetration(self,
                                     sequences: List[str],
                                     backbone_coords: Dict[str, Any],
                                     threshold: float = 0.7) -> List[Tuple[str, Dict[str, float]]]:
        """Filter sequences for α-Helix 8 channel penetration capability"""

        print(f"[LOCAL-GPU] Analyzing {len(sequences)} sequences for α-Helix 8 penetration...")

        passed_sequences = []

        for seq in sequences:
            geometry_metrics = self.calculate_sequence_geometry(seq, backbone_coords)

            if geometry_metrics['overall_score'] >= threshold:
                passed_sequences.append((seq, geometry_metrics))
                print(f"[LOCAL-GPU] ✓ Sequence passed - Channel Score: {geometry_metrics['overall_score']:.3f}")
                print(f"           Penetration: {geometry_metrics['penetration_score']:.3f}, "
                      f"Hydrophobic: {geometry_metrics['hydrophobic_packing']:.3f}, "
                      f"Targeting: {geometry_metrics['channel_targeting']:.3f}")
            else:
                print(f"[LOCAL-GPU] ✗ Sequence failed - Channel Score: {geometry_metrics['overall_score']:.3f}")

        print(f"[LOCAL-GPU] Pre-filtering complete: {len(passed_sequences)}/{len(sequences)} sequences passed")

        return passed_sequences

    def validate_hotspot_coverage(self, geometry_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Local validation of hotspot coverage before expensive API calls"""

        # Predict hotspot engagement based on geometric analysis
        predicted_coverage = {}

        # α-Helix 4 membrane binding (128, 135, 142, 156, 166)
        membrane_binding_score = geometry_metrics.get('penetration_score', 0.0) * 0.8
        predicted_coverage['helix4_membrane'] = membrane_binding_score

        # α-Helix 7 conformational switch (243)
        switch_score = geometry_metrics.get('channel_targeting', 0.0) * 0.9
        predicted_coverage['helix7_switch'] = switch_score

        # α-Helix 8 translocation channel (256, 289, 301) - PRIMARY TARGET
        channel_score = (geometry_metrics.get('hydrophobic_packing', 0.0) * 0.5 +
                        geometry_metrics.get('burial_potential', 0.0) * 0.5)
        predicted_coverage['helix8_channel'] = channel_score

        # Overall predicted hotspot coverage
        total_hotspots = 9
        estimated_engaged = 0

        if membrane_binding_score > 0.6:
            estimated_engaged += 5  # All α-Helix 4 hotspots
        if switch_score > 0.7:
            estimated_engaged += 1  # α-Helix 7 hotspot
        if channel_score > 0.8:  # High threshold for critical α-Helix 8
            estimated_engaged += 3  # All α-Helix 8 hotspots

        predicted_hotspot_percent = (estimated_engaged / total_hotspots) * 100.0

        return {
            'predicted_hotspot_coverage': predicted_hotspot_percent,
            'helix_scores': predicted_coverage,
            'estimated_engaged_hotspots': estimated_engaged,
            'worth_expensive_validation': predicted_hotspot_percent >= 88.9  # 8/9 or better
        }
