#!/usr/bin/env python3
"""
Biodefense Memory Layer: Unibase Membase Integration
Implements decentralized persistent memory for agent folding results
Follows Unibase patterns with client-side AES-256-GCM encryption
"""

import os
import json
import hashlib
import base64
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import logging

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("ERROR: Missing cryptography library for Unibase integration")
    print("Install with: pip install cryptography")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BiodefenseMemory:
    """
    Decentralized memory layer for biodefense pipeline results
    Implements Unibase Membase patterns with encrypted persistent storage
    """

    def __init__(self, memory_dir: str = "./amina_results/unibase_memory",
                 encryption_key: Optional[str] = None):
        """
        Initialize biodefense memory layer with Unibase-compatible storage

        Args:
            memory_dir: Directory for encrypted memory storage
            encryption_key: Optional encryption key (auto-generated if None)
        """
        self.memory_dir = memory_dir
        self.memory_file = os.path.join(memory_dir, "biodefense_memory.enc")
        self.index_file = os.path.join(memory_dir, "sequence_index.enc")
        self.backup_dir = os.path.join(memory_dir, "snapshots")

        # Create directories
        os.makedirs(memory_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)

        # Initialize encryption (AES-256-GCM with PBKDF2 key derivation)
        self.encryption_key = self._derive_key(encryption_key or "biodefense_membase_key")
        self.aesgcm = AESGCM(self.encryption_key)

        # Load existing memory
        self.memory_data = self._load_encrypted_memory()
        self.sequence_index = self._load_encrypted_index()

        logger.info(f"BiodefenseMemory initialized with {len(self.sequence_index)} cached sequences")

    def _derive_key(self, password: str) -> bytes:
        """
        Derive encryption key using PBKDF2 (100,000 iterations) - Unibase standard
        """
        salt = b"unibase_biodefense_salt"  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256 key length
            salt=salt,
            iterations=100000,  # Unibase standard
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using AES-256-GCM"""
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        encrypted = self.aesgcm.encrypt(nonce, data, None)
        return nonce + encrypted

    def _decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using AES-256-GCM"""
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, None)

    def _load_encrypted_memory(self) -> Dict:
        """Load encrypted memory data from disk"""
        if not os.path.exists(self.memory_file):
            return {"folding_results": [], "metadata": {"created": datetime.now(timezone.utc).isoformat()}}

        try:
            with open(self.memory_file, 'rb') as f:
                encrypted_data = f.read()

            decrypted_json = self._decrypt_data(encrypted_data).decode('utf-8')
            return json.loads(decrypted_json)
        except Exception as e:
            logger.warning(f"Failed to load encrypted memory: {e}")
            return {"folding_results": [], "metadata": {"created": datetime.now(timezone.utc).isoformat()}}

    def _save_encrypted_memory(self):
        """Save memory data to encrypted file"""
        try:
            json_data = json.dumps(self.memory_data, indent=2).encode('utf-8')
            encrypted_data = self._encrypt_data(json_data)

            with open(self.memory_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            logger.error(f"Failed to save encrypted memory: {e}")

    def _load_encrypted_index(self) -> Dict[str, str]:
        """Load sequence index for fast lookups"""
        if not os.path.exists(self.index_file):
            return {}

        try:
            with open(self.index_file, 'rb') as f:
                encrypted_data = f.read()

            decrypted_json = self._decrypt_data(encrypted_data).decode('utf-8')
            return json.loads(decrypted_json)
        except Exception as e:
            logger.warning(f"Failed to load sequence index: {e}")
            return {}

    def _save_encrypted_index(self):
        """Save sequence index to encrypted file"""
        try:
            json_data = json.dumps(self.sequence_index, indent=2).encode('utf-8')
            encrypted_data = self._encrypt_data(json_data)

            with open(self.index_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            logger.error(f"Failed to save sequence index: {e}")

    def _sequence_hash(self, sequence: str) -> str:
        """Generate deterministic hash for sequence lookup"""
        return hashlib.sha256(sequence.encode()).hexdigest()[:16]

    def log_folding_result(self, sequence: str, rmsd_score: float,
                          target_pathogen: str = "B. pseudomallei BipD") -> str:
        """
        Log folding result to decentralized memory layer

        Args:
            sequence: Protein sequence that was folded
            rmsd_score: RMSD validation score from folding
            target_pathogen: Target pathogen/protein

        Returns:
            Unique result ID for this folding attempt
        """
        # Determine success/failure based on RMSD threshold
        status = "SUCCESS" if rmsd_score < 2.0 else "FAILED"

        # Create unique result entry
        result_id = f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{self._sequence_hash(sequence)}"

        folding_result = {
            "result_id": result_id,
            "sequence": sequence,
            "sequence_hash": self._sequence_hash(sequence),
            "rmsd_score": rmsd_score,
            "target_pathogen": target_pathogen,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sequence_length": len(sequence)
        }

        # Add to memory data
        self.memory_data["folding_results"].append(folding_result)

        # Update index for fast lookups
        self.sequence_index[self._sequence_hash(sequence)] = {
            "result_id": result_id,
            "status": status,
            "rmsd_score": rmsd_score,
            "timestamp": folding_result["timestamp"]
        }

        # Save to encrypted storage
        self._save_encrypted_memory()
        self._save_encrypted_index()

        logger.info(f"Logged folding result: {result_id} | {status} | RMSD: {rmsd_score:.3f}")

        return result_id

    def check_sequence(self, sequence: str) -> Optional[Dict]:
        """
        Check if sequence has already been tested to prevent wasted compute

        Args:
            sequence: Protein sequence to check

        Returns:
            Dict with previous result info if found, None if not cached
        """
        sequence_hash = self._sequence_hash(sequence)

        if sequence_hash in self.sequence_index:
            cached_result = self.sequence_index[sequence_hash].copy()
            cached_result["sequence_hash"] = sequence_hash
            cached_result["found_in_cache"] = True

            logger.info(f"Sequence found in cache: {cached_result['status']} | RMSD: {cached_result['rmsd_score']:.3f}")
            return cached_result

        return None

    def get_success_rate(self) -> Dict:
        """Get folding success rate statistics"""
        if not self.memory_data["folding_results"]:
            return {"total": 0, "successes": 0, "failures": 0, "success_rate": 0.0}

        total = len(self.memory_data["folding_results"])
        successes = sum(1 for r in self.memory_data["folding_results"] if r["status"] == "SUCCESS")
        failures = total - successes
        success_rate = successes / total * 100

        return {
            "total": total,
            "successes": successes,
            "failures": failures,
            "success_rate": success_rate
        }

    def create_backup_snapshot(self) -> str:
        """
        Create backup snapshot following Unibase patterns

        Returns:
            Backup identifier for later restore
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_id = f"biodefense_backup_{timestamp}"

        backup_data = {
            "backup_id": backup_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "memory_data": self.memory_data,
            "sequence_index": self.sequence_index,
            "stats": self.get_success_rate()
        }

        backup_file = os.path.join(self.backup_dir, f"{backup_id}.enc")

        try:
            json_data = json.dumps(backup_data, indent=2).encode('utf-8')
            encrypted_data = self._encrypt_data(json_data)

            with open(backup_file, 'wb') as f:
                f.write(encrypted_data)

            logger.info(f"Created backup snapshot: {backup_id}")
            return backup_id

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return ""

    def list_backups(self) -> List[str]:
        """List available backup snapshots"""
        try:
            backups = [f[:-4] for f in os.listdir(self.backup_dir) if f.endswith('.enc')]
            return sorted(backups, reverse=True)  # Most recent first
        except Exception:
            return []

    def get_memory_summary(self) -> Dict:
        """Get summary of current memory state"""
        stats = self.get_success_rate()

        return {
            "total_sequences": len(self.sequence_index),
            "total_folding_attempts": stats["total"],
            "success_rate": f"{stats['success_rate']:.1f}%",
            "successful_folds": stats["successes"],
            "failed_folds": stats["failures"],
            "memory_file_size": os.path.getsize(self.memory_file) if os.path.exists(self.memory_file) else 0,
            "last_updated": self.memory_data.get("metadata", {}).get("last_updated", "Never")
        }

def main():
    """Test the biodefense memory layer"""
    print("Testing Unibase Membase Integration for Biodefense Pipeline")
    print("=" * 60)

    # Initialize memory layer
    memory = BiodefenseMemory()

    # Test sequence checking
    test_sequence = "MKQLEDKVEELLSKNYHLENEVARLKKLVGER"
    cached = memory.check_sequence(test_sequence)

    if cached:
        print(f"Sequence found in cache: {cached}")
    else:
        print("Sequence not in cache - would proceed with folding")

        # Simulate folding result
        import random
        rmsd_score = random.uniform(1.5, 3.5)
        result_id = memory.log_folding_result(test_sequence, rmsd_score)
        print(f"Logged folding result: {result_id}")

    # Display memory summary
    summary = memory.get_memory_summary()
    print(f"\nMemory Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Create backup
    backup_id = memory.create_backup_snapshot()
    if backup_id:
        print(f"\nCreated backup: {backup_id}")

if __name__ == "__main__":
    main()