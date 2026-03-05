#!/usr/bin/env python3
"""
Biosecurity Screening Module - Hard Mode Implementation
AminoAnalytica Workshop Biosecurity Screening System
"""

import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from anyway_integration.traceloop_config import task

class BiosecurityScreening:
    """
    Hard Mode Biosecurity Screening System for AminoAnalytica
    Implements structural homology screening and dangerous motif detection
    """

    def __init__(self):
        self.biosecurity_enabled = True
        self.threat_database = self._initialize_threat_database()
        self.dangerous_motifs = ['KDEL', 'RGD', 'YXXΦ', 'KKXX']
        self.t3ss_motifs = ['needle_tip', 'host_invasion', 'translocon', 'immune_evasion']

        print(f"[BIOSECURITY] Hard Mode Screening Initialized")
        print(f"[BIOSECURITY] Monitoring {len(self.threat_database)} known threat structures")

    def _initialize_threat_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize threat database mapping T3SS threats and toxins
        """
        threat_db = {
            # Type III Secretion System (T3SS) Threats
            'BipD': {
                'threat_type': 'T3SS_translocon',
                'pathogen': 'Burkholderia pseudomallei',
                'pdb_id': '2IXR',
                'risk_score': 0.9,
                'mechanism': 'host_cell_invasion',
                'critical_regions': ['128-166', '243-301'],
                'reference_rmsd': 1.2,
                'reference_tm_score': 0.85
            },
            'IpaD': {
                'threat_type': 'T3SS_needle_tip',
                'pathogen': 'Shigella flexneri',
                'pdb_id': '2J0O',
                'risk_score': 0.85,
                'mechanism': 'needle_tip_complex',
                'critical_regions': ['45-87', '156-198'],
                'reference_rmsd': 1.4,
                'reference_tm_score': 0.82
            },
            'SipD': {
                'threat_type': 'T3SS_translocon',
                'pathogen': 'Salmonella enterica',
                'pdb_id': '2VT2',
                'risk_score': 0.8,
                'mechanism': 'pore_formation',
                'critical_regions': ['67-109', '178-221'],
                'reference_rmsd': 1.6,
                'reference_tm_score': 0.78
            },

            # High-Risk Toxins
            'Ricin': {
                'threat_type': 'ribosome_toxin',
                'pathogen': 'Ricinus communis',
                'pdb_id': '2AAI',
                'risk_score': 0.95,
                'mechanism': 'protein_synthesis_inhibition',
                'critical_regions': ['177-186', '235-239'],
                'reference_rmsd': 0.8,
                'reference_tm_score': 0.92
            },
            'Botulinum': {
                'threat_type': 'neurotoxin',
                'pathogen': 'Clostridium botulinum',
                'pdb_id': '3BTA',
                'risk_score': 0.98,
                'mechanism': 'synaptic_transmission_block',
                'critical_regions': ['441-449', '1252-1296'],
                'reference_rmsd': 1.0,
                'reference_tm_score': 0.90
            },
            'Anthrax': {
                'threat_type': 'binary_toxin',
                'pathogen': 'Bacillus anthracis',
                'pdb_id': '1ACC',
                'risk_score': 0.92,
                'mechanism': 'cellular_edema_factor',
                'critical_regions': ['167-175', '289-308'],
                'reference_rmsd': 1.1,
                'reference_tm_score': 0.88
            }
        }

        return threat_db

    @task(name="structural_homology_screening")
    def structural_homology_screening(self, query_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare query structure against threat database
        Returns risk assessment based on structural similarity

        Args:
            query_structure: Dict with 'rmsd', 'tm_score', 'sequence' keys

        Returns:
            Dict with risk_level, matched_threats, security_score
        """
        if not self.biosecurity_enabled:
            return {'risk_level': 'SAFE', 'security_score': 0.0, 'threats_detected': []}

        query_rmsd = query_structure.get('rmsd', 999.0)
        query_tm_score = query_structure.get('tm_score', 0.0)
        query_sequence = query_structure.get('sequence', '')

        detected_threats = []
        max_risk_score = 0.0

        print(f"[BIOSECURITY] Scanning query structure (RMSD: {query_rmsd:.3f}, TM: {query_tm_score:.3f})")

        for threat_name, threat_data in self.threat_database.items():
            # Structural similarity thresholds (AminoAnalytica Hard Mode specs)
            rmsd_threshold = 3.0
            tm_threshold = 0.5

            # Calculate structural similarity risk
            rmsd_similarity = query_rmsd <= rmsd_threshold
            tm_similarity = query_tm_score >= tm_threshold

            if rmsd_similarity or tm_similarity:
                # Calculate combined risk score
                rmsd_risk = max(0, (rmsd_threshold - query_rmsd) / rmsd_threshold)
                tm_risk = max(0, query_tm_score - tm_threshold) / (1.0 - tm_threshold)

                combined_risk = threat_data['risk_score'] * max(rmsd_risk, tm_risk)

                detected_threats.append({
                    'threat_name': threat_name,
                    'threat_type': threat_data['threat_type'],
                    'pathogen': threat_data['pathogen'],
                    'risk_score': combined_risk,
                    'similarity_basis': 'RMSD' if rmsd_similarity else 'TM_Score',
                    'rmsd_match': rmsd_similarity,
                    'tm_match': tm_similarity
                })

                max_risk_score = max(max_risk_score, combined_risk)

        # Determine overall risk level
        if max_risk_score >= 0.7:
            risk_level = 'CRITICAL'
        elif max_risk_score >= 0.5:
            risk_level = 'HIGH'
        elif max_risk_score >= 0.3:
            risk_level = 'MODERATE'
        else:
            risk_level = 'LOW'

        # Security score for memory logging (inverse of risk)
        security_score = max_risk_score

        result = {
            'risk_level': risk_level,
            'security_score': security_score,
            'threats_detected': detected_threats,
            'threat_count': len(detected_threats),
            'max_risk_score': max_risk_score,
            'screening_timestamp': datetime.now(timezone.utc).isoformat()
        }

        if detected_threats:
            print(f"[BIOSECURITY] WARNING THREAT DETECTED: {risk_level} risk ({len(detected_threats)} matches)")
            for threat in detected_threats[:3]:  # Show top 3 threats
                print(f"[BIOSECURITY]   • {threat['threat_name']} ({threat['threat_type']}) - Risk: {threat['risk_score']:.3f}")
        else:
            print(f"[BIOSECURITY] CLEARED - no significant threat similarity detected")

        return result

    @task(name="motif_threat_detection")
    def detect_redesigned_threats(self, sequence: str, sequence_features: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Scan for dangerous motifs and T3SS-specific patterns

        Args:
            sequence: Protein sequence string
            sequence_features: Optional additional features/annotations

        Returns:
            Dict with detected motifs and threat assessment
        """
        if not self.biosecurity_enabled:
            return {'dangerous_motifs': [], 't3ss_motifs': [], 'motif_risk_score': 0.0}

        if sequence_features is None:
            sequence_features = {}

        dangerous_motifs_found = []
        t3ss_motifs_found = []

        print(f"[BIOSECURITY] Scanning {len(sequence)} amino acids for dangerous motifs...")

        # Scan for dangerous motifs
        for motif in self.dangerous_motifs:
            # Simple pattern matching (in real implementation would use more sophisticated algorithms)
            if motif in sequence:
                dangerous_motifs_found.append({
                    'motif': motif,
                    'positions': [i for i in range(len(sequence)) if sequence[i:i+len(motif)] == motif],
                    'risk_level': 'HIGH',
                    'description': self._get_motif_description(motif)
                })

        # Scan for T3SS-specific motifs (simplified pattern recognition)
        sequence_lower = sequence.lower()
        for t3ss_pattern in self.t3ss_motifs:
            # Pattern recognition heuristics
            pattern_indicators = {
                'needle_tip': ['needle', 'tip', 'invasion'],
                'host_invasion': ['host', 'invasion', 'penetration'],
                'translocon': ['translocon', 'pore', 'channel'],
                'immune_evasion': ['immune', 'evasion', 'stealth']
            }

            if t3ss_pattern in pattern_indicators:
                # Check sequence features for T3SS indicators
                feature_text = str(sequence_features).lower()
                if any(indicator in feature_text for indicator in pattern_indicators[t3ss_pattern]):
                    t3ss_motifs_found.append({
                        'motif': t3ss_pattern,
                        'evidence': pattern_indicators[t3ss_pattern],
                        'risk_level': 'MODERATE',
                        'description': f"T3SS {t3ss_pattern.replace('_', ' ')} pattern detected"
                    })

        # Calculate overall motif risk score
        dangerous_risk = len(dangerous_motifs_found) * 0.4  # Each dangerous motif = +0.4
        t3ss_risk = len(t3ss_motifs_found) * 0.2  # Each T3SS motif = +0.2
        motif_risk_score = min(1.0, dangerous_risk + t3ss_risk)

        result = {
            'dangerous_motifs': dangerous_motifs_found,
            't3ss_motifs': t3ss_motifs_found,
            'motif_risk_score': motif_risk_score,
            'total_motifs_detected': len(dangerous_motifs_found) + len(t3ss_motifs_found),
            'screening_timestamp': datetime.now(timezone.utc).isoformat()
        }

        if dangerous_motifs_found or t3ss_motifs_found:
            print(f"[BIOSECURITY] MOTIF ALERT: {len(dangerous_motifs_found)} dangerous, {len(t3ss_motifs_found)} T3SS motifs")
            for motif in dangerous_motifs_found:
                print(f"[BIOSECURITY]   • DANGEROUS: {motif['motif']} at positions {motif['positions']}")
            for motif in t3ss_motifs_found:
                print(f"[BIOSECURITY]   • T3SS: {motif['motif']} ({motif['description']})")
        else:
            print(f"[BIOSECURITY] CLEARED - No dangerous motifs detected in sequence")

        return result

    def _get_motif_description(self, motif: str) -> str:
        """Get description of dangerous motif"""
        descriptions = {
            'KDEL': 'ER retention signal - potential cellular targeting',
            'RGD': 'Integrin binding motif - cell adhesion manipulation',
            'YXXΦ': 'Tyrosine-based internalization signal - endocytic pathway hijacking',
            'KKXX': 'COPI retrieval signal - intracellular trafficking disruption'
        }
        return descriptions.get(motif, f'Unknown dangerous motif: {motif}')

    def comprehensive_screening(self, sequence: str, rmsd_score: float, tm_score: float = None, sequence_features: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run comprehensive biosecurity screening combining structural and motif analysis

        Args:
            sequence: Protein sequence
            rmsd_score: RMSD score from structural analysis
            tm_score: Optional TM-score
            sequence_features: Optional additional sequence features

        Returns:
            Combined screening results with overall risk assessment
        """
        # Prepare query structure
        query_structure = {
            'sequence': sequence,
            'rmsd': rmsd_score,
            'tm_score': tm_score or 0.0
        }

        # Run structural homology screening
        structural_results = self.structural_homology_screening(query_structure)

        # Run motif detection
        motif_results = self.detect_redesigned_threats(sequence, sequence_features)

        # Combine results for overall assessment
        structural_risk = structural_results['security_score']
        motif_risk = motif_results['motif_risk_score']

        # Calculate combined security score
        combined_security_score = max(structural_risk, motif_risk)

        # Determine validation status for memory logging
        validation_status = "CLEARED" if combined_security_score < 0.3 else "FLAGGED"

        comprehensive_result = {
            'validation_status': validation_status,
            'security_score': combined_security_score,
            'structural_screening': structural_results,
            'motif_screening': motif_results,
            'overall_risk_level': structural_results['risk_level'],
            'screening_timestamp': datetime.now(timezone.utc).isoformat(),
            'biosecurity_enabled': self.biosecurity_enabled
        }

        print(f"[BIOSECURITY] COMPREHENSIVE SCREENING: {validation_status}")
        print(f"[BIOSECURITY] Security Score: {combined_security_score:.3f} ({'HIGH RISK' if combined_security_score >= 0.5 else 'MODERATE RISK' if combined_security_score >= 0.3 else 'LOW RISK'})")

        return comprehensive_result
