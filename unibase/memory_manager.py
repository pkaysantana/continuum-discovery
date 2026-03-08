#!/usr/bin/env python3
"""
UniBase Persistent Memory Layer
Prevents redundant compute on failed design trajectories
"""

import json
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from datetime import datetime

class UniBaseMemoryManager:
    """
    Persistent memory system to track failed designs and prevent redundant compute
    """

    def __init__(self, db_path: str = "unibase/memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for persistent memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Failed designs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS failed_designs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence_hash TEXT UNIQUE NOT NULL,
                sequence TEXT NOT NULL,
                failure_reason TEXT,
                iptm_score REAL,
                coverage_percent REAL,
                timestamp TEXT,
                topological_fingerprint TEXT
            )
        """)

        # Design trajectories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS design_trajectories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trajectory_hash TEXT UNIQUE NOT NULL,
                scaffold_hash TEXT,
                sequence_hashes TEXT,  -- JSON array
                final_outcome TEXT,    -- 'success', 'failure', 'abandoned'
                trajectory_score REAL,
                timestamp TEXT
            )
        """)

        # Successful designs for comparison
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS successful_designs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence_hash TEXT UNIQUE NOT NULL,
                sequence TEXT NOT NULL,
                iptm_score REAL,
                coverage_percent REAL,
                binding_affinity REAL,
                pdb_path TEXT,
                timestamp TEXT
            )
        """)

        conn.commit()
        conn.close()

    def compute_sequence_hash(self, sequence: str) -> str:
        """Compute unique hash for protein sequence"""
        return hashlib.sha256(sequence.encode()).hexdigest()[:16]

    def compute_topological_fingerprint(self, sequence: str) -> str:
        """
        Compute topological fingerprint based on sequence properties
        This helps identify structurally similar sequences that might fail similarly
        """
        # Simple topological features
        hydrophobic = sum(1 for aa in sequence if aa in 'AILMFWYV')
        charged = sum(1 for aa in sequence if aa in 'DEKR')
        polar = sum(1 for aa in sequence if aa in 'NQST')
        aromatic = sum(1 for aa in sequence if aa in 'FWY')

        # Normalize by length
        length = len(sequence)
        if length == 0:
            return "empty"

        fingerprint = f"{hydrophobic/length:.2f}_{charged/length:.2f}_{polar/length:.2f}_{aromatic/length:.2f}"
        return fingerprint

    def is_sequence_known_failure(self, sequence: str, threshold_similarity: float = 0.1) -> bool:
        """
        Check if sequence or similar sequences have failed before
        """
        seq_hash = self.compute_sequence_hash(sequence)
        topo_print = self.compute_topological_fingerprint(sequence)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check exact sequence match
        cursor.execute("SELECT COUNT(*) FROM failed_designs WHERE sequence_hash = ?", (seq_hash,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return True

        # Check topologically similar sequences
        cursor.execute("SELECT topological_fingerprint FROM failed_designs")
        failed_fingerprints = cursor.fetchall()

        conn.close()

        # Compare topological similarity
        current_features = [float(x) for x in topo_print.split('_')]

        for (failed_print,) in failed_fingerprints:
            if failed_print == "empty":
                continue
            try:
                failed_features = [float(x) for x in failed_print.split('_')]
                # Compute euclidean distance
                distance = sum((a - b) ** 2 for a, b in zip(current_features, failed_features)) ** 0.5
                if distance < threshold_similarity:
                    return True
            except:
                continue

        return False

    def record_failure(self, sequence: str, failure_reason: str, iptm_score: float, coverage_percent: float):
        """Record a failed design attempt"""
        seq_hash = self.compute_sequence_hash(sequence)
        topo_print = self.compute_topological_fingerprint(sequence)
        timestamp = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO failed_designs
                (sequence_hash, sequence, failure_reason, iptm_score, coverage_percent, timestamp, topological_fingerprint)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (seq_hash, sequence, failure_reason, iptm_score, coverage_percent, timestamp, topo_print))

            conn.commit()
            print(f"[UNIBASE] Recorded failure: {failure_reason} (ipTM: {iptm_score:.3f}, coverage: {coverage_percent:.1f}%)")

        except sqlite3.IntegrityError:
            print(f"[UNIBASE] Failure already recorded for sequence {seq_hash}")

        conn.close()

    def record_success(self, sequence: str, iptm_score: float, coverage_percent: float, binding_affinity: float, pdb_path: str):
        """Record a successful design"""
        seq_hash = self.compute_sequence_hash(sequence)
        timestamp = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO successful_designs
                (sequence_hash, sequence, iptm_score, coverage_percent, binding_affinity, pdb_path, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (seq_hash, sequence, iptm_score, coverage_percent, binding_affinity, pdb_path, timestamp))

            conn.commit()
            print(f"[UNIBASE] Recorded SUCCESS: ipTM={iptm_score:.3f}, coverage={coverage_percent:.1f}%")

        except sqlite3.IntegrityError:
            print(f"[UNIBASE] Success already recorded for sequence {seq_hash}")

        conn.close()

    def get_memory_stats(self) -> Dict[str, int]:
        """Get statistics about stored memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM failed_designs")
        failed_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM successful_designs")
        success_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM design_trajectories")
        trajectory_count = cursor.fetchone()[0]

        conn.close()

        return {
            'failed_designs': failed_count,
            'successful_designs': success_count,
            'trajectories': trajectory_count,
            'total_memory_entries': failed_count + success_count + trajectory_count
        }

    def cleanup_old_entries(self, days_old: int = 30):
        """Remove entries older than specified days"""
        cutoff_date = datetime.now().replace(day=datetime.now().day - days_old).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM failed_designs WHERE timestamp < ?", (cutoff_date,))
        cursor.execute("DELETE FROM successful_designs WHERE timestamp < ?", (cutoff_date,))
        cursor.execute("DELETE FROM design_trajectories WHERE timestamp < ?", (cutoff_date,))

        conn.commit()
        conn.close()

        print(f"[UNIBASE] Cleaned up entries older than {days_old} days")

if __name__ == "__main__":
    # Test the memory system
    memory = UniBaseMemoryManager()

    # Test sequence
    test_seq = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWUAKCLVUQKMNHQFGKWLDFGMWVPPGATMSQRPLESVVEKLHGLPLDHQLHEVCDGTGTGKSKWSQRGSKQPFLNKRQKL"

    # Test failure recording
    memory.record_failure(test_seq, "Low ipTM", 0.45, 33.3)

    # Test if it's detected as known failure
    print(f"Is known failure: {memory.is_sequence_known_failure(test_seq)}")

    # Show stats
    stats = memory.get_memory_stats()
    print(f"Memory stats: {stats}")
