#!/usr/bin/env python3
"""
OpenClaw Biosecurity Guardrails
Automated screening for dangerous protein designs
"""

import json
import hashlib
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import sqlite3

class BiosecurityScanner:
    """
    Automated biosecurity screening system to prevent dangerous protein designs
    """

    def __init__(self, audit_dir: str = "biosecurity_audits"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(exist_ok=True)

        # Known dangerous patterns database
        self.dangerous_patterns_db = self.audit_dir / "dangerous_patterns.db"
        self.init_dangerous_patterns_db()

        # Load known toxin/virulence signatures
        self.load_dangerous_signatures()

    def init_dangerous_patterns_db(self):
        """Initialize database of dangerous sequence patterns"""
        conn = sqlite3.connect(self.dangerous_patterns_db)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dangerous_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_hash TEXT UNIQUE NOT NULL,
                sequence_pattern TEXT NOT NULL,
                danger_type TEXT NOT NULL,  -- 'toxin', 'virulence', 'immune_evasion', 'bioweapon'
                source_organism TEXT,
                pdb_reference TEXT,
                danger_level INTEGER,  -- 1-5 scale
                description TEXT,
                timestamp TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS screening_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence_hash TEXT NOT NULL,
                sequence TEXT NOT NULL,
                screening_result TEXT NOT NULL,  -- 'SAFE', 'FLAGGED', 'BLOCKED'
                danger_matches TEXT,  -- JSON array of matches
                risk_score REAL,
                timestamp TEXT,
                reviewer_notes TEXT
            )
        """)

        conn.commit()
        conn.close()

    def load_dangerous_signatures(self):
        """Load known dangerous protein signatures"""
        # Known toxin patterns (simplified examples)
        self.dangerous_motifs = {
            # Botulinum toxin-like patterns
            'botulinum_like': [
                'STLNDY',    # Light chain zinc binding
                'HEFGH',     # Metalloprotease motif
                'QVDHGN',    # Catalytic domain
            ],

            # Ricin-like patterns
            'ricin_like': [
                'TATNP',     # A-chain active site
                'YISPYN',    # Ribosome binding
                'TTDLDA',    # Catalytic residues
            ],

            # Anthrax toxin patterns
            'anthrax_like': [
                'DNEAY',     # Protective antigen
                'TSKSY',     # Lethal factor
                'DGNGQ',     # Edema factor
            ],

            # Immune evasion patterns
            'immune_evasion': [
                'PEVIPMF',   # MHC-I downregulation
                'KMTLQ',     # CD4+ T-cell inhibition
                'QIPIDH',    # Complement evasion
            ],

            # Membrane disruption patterns
            'membrane_disruption': [
                'GLALA',     # Pore-forming toxins
                'SGGMG',     # Hemolytic activity
                'WLLQQ',     # Lipid binding
            ]
        }

        # Structural homology patterns (simplified)
        self.dangerous_structures = {
            'beta_barrel_toxins': ['TYGS', 'IMVG', 'WNEF'],
            'alpha_helical_toxins': ['LEALS', 'QKMDV', 'HVWLS'],
            'enzymatic_toxins': ['HEFGH', 'DXXH', 'HXXE']
        }

    def compute_sequence_hash(self, sequence: str) -> str:
        """Compute unique hash for sequence"""
        return hashlib.sha256(sequence.encode()).hexdigest()[:16]

    def scan_sequence_motifs(self, sequence: str) -> List[Dict[str, Any]]:
        """Scan sequence for dangerous motifs"""
        matches = []

        for toxin_type, motifs in self.dangerous_motifs.items():
            for motif in motifs:
                if motif in sequence:
                    position = sequence.find(motif)
                    matches.append({
                        'type': 'motif_match',
                        'toxin_type': toxin_type,
                        'motif': motif,
                        'position': position,
                        'danger_level': 4,  # High danger for exact motif matches
                        'description': f"Exact match to {toxin_type} motif"
                    })

        return matches

    def scan_structural_patterns(self, sequence: str) -> List[Dict[str, Any]]:
        """Scan for dangerous structural patterns"""
        matches = []

        for struct_type, patterns in self.dangerous_structures.items():
            pattern_count = sum(1 for pattern in patterns if pattern in sequence)
            if pattern_count >= 2:  # Multiple patterns suggest structural similarity
                matches.append({
                    'type': 'structural_pattern',
                    'structure_type': struct_type,
                    'pattern_count': pattern_count,
                    'danger_level': 3,
                    'description': f"Structural similarity to {struct_type}"
                })

        return matches

    def analyze_sequence_composition(self, sequence: str) -> Dict[str, Any]:
        """Analyze overall sequence composition for red flags"""
        if not sequence:
            return {'risk_factors': [], 'composition_score': 0}

        risk_factors = []

        # Check for unusual amino acid compositions
        cysteine_content = sequence.count('C') / len(sequence)
        if cysteine_content > 0.15:  # >15% cysteine suggests disulfide-rich toxins
            risk_factors.append({
                'type': 'high_cysteine',
                'percentage': cysteine_content * 100,
                'danger_level': 2,
                'description': f"High cysteine content ({cysteine_content*100:.1f}%) - potential disulfide toxin"
            })

        # Check for hydrophobic clusters (membrane-active toxins)
        hydrophobic = 'AILMFWYV'
        max_hydrophobic_stretch = 0
        current_stretch = 0

        for aa in sequence:
            if aa in hydrophobic:
                current_stretch += 1
                max_hydrophobic_stretch = max(max_hydrophobic_stretch, current_stretch)
            else:
                current_stretch = 0

        if max_hydrophobic_stretch > 10:
            risk_factors.append({
                'type': 'hydrophobic_stretch',
                'max_length': max_hydrophobic_stretch,
                'danger_level': 2,
                'description': f"Long hydrophobic stretch ({max_hydrophobic_stretch}) - potential membrane toxin"
            })

        # Overall composition risk score
        composition_score = len(risk_factors) * 0.5

        return {
            'risk_factors': risk_factors,
            'composition_score': composition_score
        }

    def screen_against_pdb_database(self, sequence: str) -> List[Dict[str, Any]]:
        """Screen against known dangerous PDB structures (simplified simulation)"""
        # In production, this would query actual PDB/UniProt databases
        # For now, simulate with known dangerous PDB IDs

        dangerous_pdbs = {
            '1DTC': 'Diphtheria toxin',
            '2AAI': 'Anthrax protective antigen',
            '1RTC': 'Ricin toxin A chain',
            '1EPW': 'Botulinum neurotoxin',
            '1CRP': 'C-reactive protein (inflammatory)'
        }

        matches = []
        seq_hash = self.compute_sequence_hash(sequence)

        # Simulate sequence similarity check (in production would use BLAST)
        for pdb_id, description in dangerous_pdbs.items():
            # Simulate finding partial matches
            if len(sequence) > 50 and hash(seq_hash + pdb_id) % 100 < 5:  # 5% false positive rate
                matches.append({
                    'type': 'pdb_similarity',
                    'pdb_id': pdb_id,
                    'description': description,
                    'similarity_score': 0.3 + (hash(seq_hash) % 30) / 100,  # 30-60% similarity
                    'danger_level': 5,  # Maximum danger for PDB matches
                    'description_detail': f"Potential similarity to {description} ({pdb_id})"
                })

        return matches

    def comprehensive_biosecurity_scan(self, sequence: str) -> Dict[str, Any]:
        """Perform comprehensive biosecurity screening"""
        scan_start = datetime.now()
        seq_hash = self.compute_sequence_hash(sequence)

        print(f"[OPENCLAW] Starting biosecurity scan for sequence {seq_hash}")

        # Perform all screening methods
        motif_matches = self.scan_sequence_motifs(sequence)
        structural_matches = self.scan_structural_patterns(sequence)
        composition_analysis = self.analyze_sequence_composition(sequence)
        pdb_matches = self.screen_against_pdb_database(sequence)

        # Compile all matches
        all_matches = motif_matches + structural_matches + composition_analysis['risk_factors'] + pdb_matches

        # Calculate overall risk score
        risk_score = sum(match.get('danger_level', 0) for match in all_matches)
        risk_score += composition_analysis['composition_score']

        # Determine screening result
        if risk_score >= 8:
            result = "BLOCKED"
        elif risk_score >= 4:
            result = "FLAGGED"
        else:
            result = "SAFE"

        scan_duration = (datetime.now() - scan_start).total_seconds()

        screening_report = {
            'sequence_hash': seq_hash,
            'screening_result': result,
            'risk_score': risk_score,
            'total_matches': len(all_matches),
            'match_details': all_matches,
            'scan_duration_seconds': scan_duration,
            'timestamp': datetime.now().isoformat(),
            'scanner_version': '1.0.0'
        }

        # Log the screening result
        self.log_screening_result(sequence, screening_report)

        print(f"[OPENCLAW] Scan complete: {result} (risk score: {risk_score:.1f}, {len(all_matches)} matches)")

        return screening_report

    def log_screening_result(self, sequence: str, report: Dict[str, Any]):
        """Log screening result to database and audit file"""
        # Database logging
        conn = sqlite3.connect(self.dangerous_patterns_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO screening_results
            (sequence_hash, sequence, screening_result, danger_matches, risk_score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            report['sequence_hash'],
            sequence,
            report['screening_result'],
            json.dumps(report['match_details']),
            report['risk_score'],
            report['timestamp']
        ))

        conn.commit()
        conn.close()

        # Audit file logging
        audit_file = self.audit_dir / f"screening_log_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(audit_file, 'a') as f:
            f.write(json.dumps(report) + '\n')

    def is_sequence_safe_for_synthesis(self, sequence: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Main entry point: determine if sequence is safe for synthesis
        Returns (is_safe, screening_report)
        """
        report = self.comprehensive_biosecurity_scan(sequence)
        is_safe = report['screening_result'] in ['SAFE', 'FLAGGED']  # Allow flagged with review

        return is_safe, report

    def get_screening_stats(self) -> Dict[str, Any]:
        """Get statistics about screening history"""
        conn = sqlite3.connect(self.dangerous_patterns_db)
        cursor = conn.cursor()

        cursor.execute("SELECT screening_result, COUNT(*) FROM screening_results GROUP BY screening_result")
        result_counts = dict(cursor.fetchall())

        cursor.execute("SELECT AVG(risk_score), MAX(risk_score), MIN(risk_score) FROM screening_results")
        avg_risk, max_risk, min_risk = cursor.fetchone()

        conn.close()

        return {
            'total_screenings': sum(result_counts.values()),
            'result_breakdown': result_counts,
            'risk_score_stats': {
                'average': avg_risk or 0,
                'maximum': max_risk or 0,
                'minimum': min_risk or 0
            }
        }

if __name__ == "__main__":
    # Test the biosecurity scanner
    scanner = BiosecurityScanner()

    # Test sequences
    safe_sequence = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWUAKCLVUQKMNHQFGKWLDFGMWVPPGATMSQRPLESVVEKLHGLPLDHQLHEVCDGTGTGKSKWSQRGSKQPFLNKRQKL"

    dangerous_sequence = "MKTAYIAKQRQISFVKSTLNDYFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWUAKCLVUQKMNHQFGKWLDFGMWVPPGATMSQRPLESVVEKLHGLPLDHQLHEVCDGTGTGKSKWSQRGSKQPFLNKRQKL"  # Contains STLNDY motif

    print("Testing safe sequence:")
    is_safe, report = scanner.is_sequence_safe_for_synthesis(safe_sequence)
    print(f"Safe: {is_safe}, Risk Score: {report['risk_score']}")

    print("\nTesting potentially dangerous sequence:")
    is_safe, report = scanner.is_sequence_safe_for_synthesis(dangerous_sequence)
    print(f"Safe: {is_safe}, Risk Score: {report['risk_score']}")

    print(f"\nScanning stats: {scanner.get_screening_stats()}")
