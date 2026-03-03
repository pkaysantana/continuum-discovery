#!/usr/bin/env python3
"""
BioScientistAgent: OpenClaw Agent for Protein Synthesis and Validation
Wraps fold_binders.py and memory_layer.py for Animoca Multi-Agent Swarm
"""

import sys
import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List
import random

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from openclaw.base_agent import OpenClawAgent, Message
from scripts.memory_layer import BiodefenseMemory
from anyway_integration.traceloop_config import workflow, task

class BioScientistAgent(OpenClawAgent):
    """
    OpenClaw Agent for protein synthesis and scientific validation
    Manages ProteinMPNN synthesis, ESMFold validation, and Unibase memory
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
            "rmsd_scoring"
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

    @workflow(name="protein_synthesis_pipeline")
    async def run_primary_function(self) -> Dict[str, Any]:
        """
        Primary function: Synthesize and validate protein countermeasures
        """
        if not self.memory_active:
            return {'status': 'error', 'reason': 'memory_unavailable'}

        print(f"\n[BIO_SCIENTIST] Running protein synthesis and validation pipeline...")

        try:
            # Run synthesis pipeline (wrapping fold_binders.py logic)
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

    @task(name="proteinmpnn_generation")
    async def _run_synthesis_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete protein synthesis and validation pipeline
        """
        # Simulate ProteinMPNN synthesis (enhanced from fold_binders.py logic)
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        sequence_length = random.randint(80, 150)
        protein_sequence = ''.join(random.choice(amino_acids) for _ in range(sequence_length))

        # Check Unibase memory first (prevent wasted compute)
        cached_result = self.memory.check_sequence(protein_sequence)

        if cached_result:
            print(f"[BIO_SCIENTIST] Sequence found in Unibase Membase - 100% compute efficiency!")

            return {
                'synthesis_timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'cached',
                'from_memory': True,
                'sequence': protein_sequence[:50] + "...",
                'rmsd_score': cached_result['rmsd_score'],
                'validation_status': cached_result['status'],
                'compute_saved': True
            }

        # Run new synthesis
        print(f"[BIO_SCIENTIST] Generating new countermeasure via ProteinMPNN...")

        # Simulate ESMFold validation
        rmsd_score = random.uniform(0.8, 3.5)
        validation_status = 'SUCCESS' if rmsd_score < 2.0 else 'MODERATE'

        # Log to Unibase memory
        if self.memory_active:
            result_id = self.memory.log_folding_result(
                protein_sequence,
                rmsd_score,
                "B. pseudomallei BipD (Multi-agent synthesis)"
            )

        synthesis_result = {
            'synthesis_timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'completed',
            'from_memory': False,
            'sequence': protein_sequence,
            'sequence_length': sequence_length,
            'rmsd_score': rmsd_score,
            'validation_status': validation_status,
            'target_pathogen': 'B. pseudomallei BipD',
            'synthesis_method': 'ProteinMPNN + ESMFold',
            'memory_logged': self.memory_active,
            'result_id': result_id if self.memory_active else None
        }

        print(f"[BIO_SCIENTIST] Synthesis complete: RMSD {rmsd_score:.3f}Å ({validation_status})")

        return synthesis_result

    @task(name="emergency_countermeasure_synthesis")
    async def handle_flood_threat_detected(self, message: Message):
        """
        Handle flood threat from EarthWatcherAgent and synthesize countermeasures
        """
        threat_data = message.payload
        severity = threat_data.get('severity', 'UNKNOWN')
        water_percentage = threat_data.get('water_percentage', 0.0)

        print(f"[BIO_SCIENTIST] Flood threat received: {severity} ({water_percentage:.1f}% water)")
        print(f"[BIO_SCIENTIST] Initiating emergency countermeasure synthesis...")

        if threat_data.get('requires_countermeasures', False):
            self.synthesis_active = True

            # Run emergency synthesis
            synthesis_result = await self.run_primary_function()

            # Notify BiotechExecutiveAgent of new countermeasure
            await self.send_message(
                recipient="BiotechExecutiveAgent",
                message_type="countermeasure_ready",
                payload={
                    'synthesis_result': synthesis_result,
                    'threat_context': threat_data,
                    'emergency_priority': severity in ['HIGH', 'CRITICAL'],
                    'commercial_ready': synthesis_result.get('validation_status') == 'SUCCESS'
                },
                priority=1 if severity in ['HIGH', 'CRITICAL'] else 0
            )

            # Send FLock progress update
            await self.send_message(
                recipient="TelegramInterface",
                message_type="synthesis_progress",
                payload={
                    'stage': 'synthesis_complete',
                    'rmsd_score': synthesis_result.get('rmsd_score'),
                    'validation': synthesis_result.get('validation_status'),
                    'sequence_cached': synthesis_result.get('from_memory', False),
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

        # Run synthesis
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
        """Get detailed synthesis and memory status"""
        memory_summary = self.memory.get_memory_summary() if self.memory_active else {}

        return {
            'agent_name': self.agent_name,
            'synthesis_active': self.synthesis_active,
            'memory_status': self.state.get('memory_status'),
            'memory_summary': memory_summary,
            'current_targets': self.current_targets,
            'synthesis_history_count': len(self.synthesis_history),
            'last_synthesis': self.state.get('last_synthesis'),
            'capabilities': self.capabilities
        }

    async def run_continuous_monitoring(self):
        """
        Monitor for synthesis requests and memory optimization
        """
        print(f"[BIO_SCIENTIST] Starting synthesis monitoring...")

        while self.is_active:
            try:
                # Periodic memory optimization
                if self.memory_active:
                    # Update memory statistics
                    summary = self.memory.get_memory_summary()
                    self.state['cached_sequences'] = summary['total_sequences']

                await asyncio.sleep(60)  # Check every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[BIO_SCIENTIST] Monitoring error: {e}")
                await asyncio.sleep(30)

        print(f"[BIO_SCIENTIST] Monitoring stopped")