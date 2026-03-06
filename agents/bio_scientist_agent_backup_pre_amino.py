#!/usr/bin/env python3
"""
BioScientistAgent: OpenClaw Agent for Protein Synthesis and Validation
Enhanced with AminoAnalytica 'Hard Mode' Biosecurity Screening System
"""

import sys
import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List
import random
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from openclaw.base_agent import OpenClawAgent, Message
from scripts.memory_layer import BiodefenseMemory
from anyway_integration.traceloop_config import workflow, task
from agents.biosecurity_screening import BiosecurityScreening

class BioScientistAgent(OpenClawAgent):
    """
    OpenClaw Agent for protein synthesis and scientific validation
    Enhanced with Hard Mode Biosecurity Screening System
    """

    def __init__(self, message_bus):
        super().__init__(
            agent_name="BioScientistAgent",
            agent_type="protein_scientist",
            message_bus=message_bus
        )

        # Initialize capabilities
        self.capabilities = [
            "protein_synthesis",
            "proteinmpnn_generation",
            "esmfold_validation",
            "unibase_memory_management",
            "cross_pathogen_analysis",
            "rmsd_scoring",
            "biosecurity_screening",  # Hard Mode capability
            "threat_detection",       # Threat database screening
            "motif_analysis"         # Dangerous motif detection
        ]

        # Initialize Unibase Membase
        try:
            self.memory = BiodefenseMemory()
            self.memory_active = True
            self.state['memory_status'] = 'operational'
            self.state['cached_sequences'] = self.memory.get_memory_summary()['total_sequences']
        except Exception as e:
            self.memory_active = False
            self.state['memory_status'] = f'error: {e}'
            print(f"[BIO_SCIENTIST] Warning: Could not initialize memory - {e}")

        # Synthesis parameters
        self.synthesis_active = False
        self.current_targets = []
        self.synthesis_history = []

        # Initialise Hard Mode Biosecurity Screening System
        try:
            self.biosecurity = BiosecurityScreening()
            self.biosecurity_enabled = True
            print(f"[BIO_SCIENTIST] Hard Mode Biosecurity Screening: ENABLED")
            print(f"[BIO_SCIENTIST] Monitoring {len(self.biosecurity.threat_database)} known threat structures")
        except Exception as e:
            self.biosecurity = None
            self.biosecurity_enabled = False
            print(f"[BIO_SCIENTIST] Warning: Biosecurity screening disabled - {e}")

    @workflow(name="protein_synthesis_pipeline")
    async def run_primary_function(self) -> Dict[str, Any]:
        """
        Primary function: Synthesize and validate protein countermeasures with biosecurity screening
        """
        if not self.memory_active:
            return {'status': 'error', 'reason': 'memory_unavailable'}

        print(f"\n[BIO_SCIENTIST] Running protein synthesis and validation pipeline with biosecurity...")

        try:
            # Run enhanced synthesis pipeline with biosecurity
            synthesis_result = await self._run_synthesis_pipeline()

            self.state['last_synthesis'] = datetime.now(timezone.utc).isoformat()
            self.synthesis_history.append(synthesis_result)

            return synthesis_result

        except Exception as e:
            error_result = {
                'synthesis_timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'error',
                'error': str(e)
            }
            print(f"[BIO_SCIENTIST] Synthesis error: {e}")
            return error_result

    @task(name="proteinmpnn_generation_with_screening")
    async def _run_synthesis_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete protein synthesis and validation pipeline with biosecurity screening
        """
        # Simulate ProteinMPNN synthesis (enhanced from fold_binders.py logic)
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        sequence_length = random.randint(80, 150)
        protein_sequence = ''.join(random.choice(amino_acids) for _ in range(sequence_length))

        # Check Unibase memory first (prevent wasted compute)
        cached_result = self.memory.check_sequence(protein_sequence)

        if cached_result:
            print(f"[BIO_SCIENTIST] Sequence found in Unibase Membase - 100% compute efficiency!")

            # Still run biosecurity screening on cached results
            biosecurity_result = None
            if self.biosecurity_enabled:
                cached_rmsd = cached_result.get('rmsd_score', 999.0)
                biosecurity_result = self.biosecurity.comprehensive_screening(
                    protein_sequence, cached_rmsd
                )

            return {
                'synthesis_timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'cached',
                'from_memory': True,
                'sequence': protein_sequence[:50] + "...",
                'rmsd_score': cached_result['rmsd_score'],
                'validation_status': cached_result['status'],
                'compute_saved': True,
                'biosecurity_screening': biosecurity_result
            }

        # Run new synthesis
        print(f"[BIO_SCIENTIST] Generating new countermeasure via ProteinMPNN...")

        # Simulate ESMFold validation
        rmsd_score = random.uniform(0.8, 3.5)
        tm_score = random.uniform(0.3, 0.9)  # Add TM-score for biosecurity screening
        validation_status = 'SUCCESS' if rmsd_score < 2.0 else 'MODERATE'

        # Run Hard Mode Biosecurity Screening
        biosecurity_result = None
        if self.biosecurity_enabled:
            print(f"[BIO_SCIENTIST] Running Hard Mode Biosecurity Screening...")
            biosecurity_result = self.biosecurity.comprehensive_screening(
                protein_sequence,
                rmsd_score,
                tm_score,
                {'target': 'B. pseudomallei BipD', 'method': 'ProteinMPNN'}
            )

            # Update validation status based on biosecurity screening
            if biosecurity_result['validation_status'] == 'FLAGGED':
                validation_status = 'BIOSECURITY_FLAGGED'
                print(f"[BIO_SCIENTIST] ⚠️  BIOSECURITY ALERT: Sequence flagged as potential threat")

        # Enhanced memory logging with biosecurity validation
        result_id = None
        if self.memory_active:
            # Prepare enhanced log data for memory
            log_data = {
                'protein_sequence': protein_sequence,
                'rmsd_score': rmsd_score,
                'tm_score': tm_score,
                'target': "B. pseudomallei BipD (Multi-agent synthesis)",
                'validation_status': biosecurity_result['validation_status'] if biosecurity_result else 'CLEARED',
                'security_score': biosecurity_result['security_score'] if biosecurity_result else 0.0,
                'biosecurity_screening': biosecurity_result is not None
            }

            result_id = self.log_binder_result(log_data)

        synthesis_result = {
            'synthesis_timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'completed',
            'from_memory': False,
            'sequence': protein_sequence,
            'sequence_length': sequence_length,
            'rmsd_score': rmsd_score,
            'tm_score': tm_score,
            'validation_status': validation_status,
            'target_pathogen': 'B. pseudomallei BipD',
            'synthesis_method': 'ProteinMPNN + ESMFold',
            'memory_logged': self.memory_active,
            'result_id': result_id,
            'biosecurity_screening': biosecurity_result,
            'biosecurity_enabled': self.biosecurity_enabled
        }

        # Enhanced logging with biosecurity context
        if biosecurity_result:
            security_score = biosecurity_result['security_score']
            risk_level = biosecurity_result['overall_risk_level']
            print(f"[BIO_SCIENTIST] Synthesis complete: RMSD {rmsd_score:.3f}Å, Security: {security_score:.3f} ({risk_level})")
        else:
            print(f"[BIO_SCIENTIST] Synthesis complete: RMSD {rmsd_score:.3f}Å ({validation_status})")

        return synthesis_result

    def log_binder_result(self, log_data: Dict[str, Any]) -> str:
        """
        Enhanced memory logging with biosecurity validation status
        """
        sequence = log_data['protein_sequence']
        rmsd_score = log_data['rmsd_score']
        target = log_data.get('target', 'Unknown target')

        # Set validation_status based on security_score (AminoAnalytica Hard Mode spec)
        security_score = log_data.get('security_score', 0.0)
        validation_status = "CLEARED" if security_score < 0.3 else "FLAGGED"

        # Use existing memory system with enhanced validation status
        if self.memory_active:
            result_id = self.memory.log_folding_result(sequence, rmsd_score, target)

            # Log biosecurity metadata if available
            if log_data.get('biosecurity_screening', False):
                print(f"[BIO_SCIENTIST] Memory logged with biosecurity validation: {validation_status}")
                print(f"[BIO_SCIENTIST] Security score: {security_score:.3f}")

            return result_id
        else:
            print(f"[BIO_SCIENTIST] Warning: Memory logging unavailable")
            return None

    @task(name="emergency_countermeasure_synthesis")
    async def handle_flood_threat_detected(self, message: Message):
        """
        Handle flood threat from EarthWatcherAgent and synthesise countermeasures with biosecurity
        """
        threat_data = message.payload
        severity = threat_data.get('severity', 'UNKNOWN')
        water_percentage = threat_data.get('water_percentage', 0.0)

        print(f"[BIO_SCIENTIST] Flood threat received: {severity} ({water_percentage:.1f}% water)")
        print(f"[BIO_SCIENTIST] Initiating emergency countermeasure synthesis with biosecurity screening...")

        if threat_data.get('requires_countermeasures', False):
            self.synthesis_active = True

            # Run emergency synthesis with enhanced biosecurity
            synthesis_result = await self.run_primary_function()

            # Check if biosecurity flagged the result
            biosecurity_flagged = (
                synthesis_result.get('validation_status') == 'BIOSECURITY_FLAGGED' or
                (synthesis_result.get('biosecurity_screening') and
                 synthesis_result['biosecurity_screening']['validation_status'] == 'FLAGGED')
            )

            if biosecurity_flagged:
                print(f"[BIO_SCIENTIST] ⚠️  Emergency synthesis flagged by biosecurity - manual review required")

            # Notify BiotechExecutiveAgent of new countermeasure
            await self.send_message(
                recipient="BiotechExecutiveAgent",
                message_type="countermeasure_ready",
                payload={
                    'synthesis_result': synthesis_result,
                    'threat_context': threat_data,
                    'emergency_priority': severity in ['HIGH', 'CRITICAL'],
                    'commercial_ready': synthesis_result.get('validation_status') == 'SUCCESS',
                    'biosecurity_cleared': not biosecurity_flagged
                },
                priority=1 if severity in ['HIGH', 'CRITICAL'] else 0
            )

            # Send FLock progress update with biosecurity status
            await self.send_message(
                recipient="TelegramInterface",
                message_type="synthesis_progress",
                payload={
                    'stage': 'synthesis_complete',
                    'rmsd_score': synthesis_result.get('rmsd_score'),
                    'validation': synthesis_result.get('validation_status'),
                    'sequence_cached': synthesis_result.get('from_memory', False),
                    'biosecurity_status': 'FLAGGED' if biosecurity_flagged else 'CLEARED',
                    'flock_api_status': 'synthesis_via_open_source'
                },
                priority=1
            )

    async def handle_synthesis_request(self, message: Message):
        """Handle direct synthesis requests from other agents"""
        request_data = message.payload
        target_pathogen = request_data.get('target_pathogen', 'B. pseudomallei BipD')

        print(f"[BIO_SCIENTIST] Synthesis request for: {target_pathogen}")

        # Add to synthesis queue
        self.current_targets.append(target_pathogen)

        # Run synthesis with biosecurity
        result = await self.run_primary_function()

        # Send results back
        await self.send_message(
            recipient=message.sender,
            message_type="synthesis_results",
            payload={'synthesis_result': result},
            priority=0
        )

    async def handle_memory_query(self, message: Message):
        """Handle memory queries from other agents"""
        query_data = message.payload
        sequence = query_data.get('sequence')

        if sequence and self.memory_active:
            cached_result = self.memory.check_sequence(sequence)

            await self.send_message(
                recipient=message.sender,
                message_type="memory_query_result",
                payload={
                    'sequence_found': cached_result is not None,
                    'cached_data': cached_result
                },
                priority=0
            )

    async def handle_emergency_stop(self, message: Message):
        """Handle emergency stop from swarm coordinator"""
        print(f"[BIO_SCIENTIST] Emergency stop received: {message.payload.get('reason')}")
        self.synthesis_active = False

        # Create memory backup before shutdown
        if self.memory_active:
            backup_id = self.memory.create_backup_snapshot()
            print(f"[BIO_SCIENTIST] Memory backup created: {backup_id}")

        await self.deactivate()

    async def handle_agent_activated(self, message: Message):
        """Handle agent activation notifications"""
        activated_agent = message.payload.get('agent_name')
        if activated_agent == "BiotechExecutiveAgent":
            print(f"[BIO_SCIENTIST] BiotechExecutiveAgent online - ready for commercialization")

    def get_synthesis_status(self) -> Dict[str, Any]:
        """Get detailed synthesis and memory status with biosecurity info"""
        memory_summary = self.memory.get_memory_summary() if self.memory_active else {}

        return {
            'agent_name': self.agent_name,
            'synthesis_active': self.synthesis_active,
            'memory_status': self.state.get('memory_status'),
            'memory_summary': memory_summary,
            'current_targets': self.current_targets,
            'synthesis_history_count': len(self.synthesis_history),
            'last_synthesis': self.state.get('last_synthesis'),
            'capabilities': self.capabilities,
            'biosecurity_enabled': self.biosecurity_enabled,
            'biosecurity_threats_monitored': len(self.biosecurity.threat_database) if self.biosecurity else 0
        }

    async def run_continuous_monitoring(self):
        """
        Monitor for synthesis requests and memory optimization with biosecurity alerts
        """
        print(f"[BIO_SCIENTIST] Starting synthesis monitoring with biosecurity screening...")

        while self.is_active:
            try:
                # Periodic memory optimization
                if self.memory_active:
                    # Update memory statistics
                    summary = self.memory.get_memory_summary()
                    self.state['cached_sequences'] = summary['total_sequences']

                # Periodic biosecurity system health check
                if self.biosecurity_enabled:
                    if hasattr(self.biosecurity, 'threat_database'):
                        threats_count = len(self.biosecurity.threat_database)
                        if threats_count != 6:  # Expected number of threats
                            print(f"[BIO_SCIENTIST] Biosecurity warning: Expected 6 threats, found {threats_count}")

                await asyncio.sleep(60)  # Check every min
                ute

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[BIO_SCIENTIST] Monitoring error: {e}")
                await asyncio.sleep(30)

        print(f"[BIO_SCIENTIST] Monitoring stopped")
