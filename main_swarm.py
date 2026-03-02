#!/usr/bin/env python3
"""
OpenClaw Multi-Agent Swarm Orchestrator
Coordinates biodefense intelligence across multiple hackathon tracks
"""

import sys
import os
import asyncio
import signal
from datetime import datetime, timezone
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from openclaw.base_agent import SwarmCoordinator
from agents.earth_watcher_agent import EarthWatcherAgent
from agents.bio_scientist_agent import BioScientistAgent
from agents.biotech_executive_agent import BiotechExecutiveAgent
from agents.telegram_interface import TelegramInterface

class BiodefenseSwarmOrchestrator:
    """
    OpenClaw Multi-Agent Swarm for Biodefense Intelligence
    Animoca Multi-Agent Swarm + FLock.io SDG 3 + Imperial 'Claw for Human'
    """

    def __init__(self, telegram_token: str = None):
        print("=" * 80)
        print("OPENCLAW MULTI-AGENT BIODEFENSE SWARM")
        print("Animoca | FLock.io SDG 3 | Imperial 'Claw for Human'")
        print("=" * 80)

        # Initialize swarm coordinator
        self.coordinator = SwarmCoordinator()
        self.shutdown_requested = False

        # Create agent instances
        print("\n[ORCHESTRATOR] Initializing agents...")

        self.earth_watcher = EarthWatcherAgent(self.coordinator.message_bus)
        print("[ORCHESTRATOR] EarthWatcherAgent: Satellite monitoring ready")

        self.bio_scientist = BioScientistAgent(self.coordinator.message_bus)
        print("[ORCHESTRATOR] BioScientistAgent: Protein synthesis ready")

        self.biotech_executive = BiotechExecutiveAgent(self.coordinator.message_bus)
        print("[ORCHESTRATOR] BiotechExecutiveAgent: Commercial operations ready")

        self.telegram_interface = TelegramInterface(self.coordinator.message_bus, telegram_token)
        print("[ORCHESTRATOR] TelegramInterface: FLock SDG 3 alerts ready")

        # Register all agents
        self.coordinator.register_agent(self.earth_watcher)
        self.coordinator.register_agent(self.bio_scientist)
        self.coordinator.register_agent(self.biotech_executive)
        self.coordinator.register_agent(self.telegram_interface)

        print(f"[ORCHESTRATOR] {len(self.coordinator.agents)} agents registered")

    async def start_swarm(self):
        """Start the complete multi-agent swarm"""
        print("\n[ORCHESTRATOR] Starting OpenClaw biodefense swarm...")

        try:
            # Start swarm coordinator
            await self.coordinator.start_swarm()

            # Start agent monitoring loops
            monitoring_tasks = [
                asyncio.create_task(self.earth_watcher.start_continuous_monitoring()),
                asyncio.create_task(self.bio_scientist.run_continuous_monitoring()),
                asyncio.create_task(self.biotech_executive.run_continuous_monitoring()),
                asyncio.create_task(self.telegram_interface.run_continuous_monitoring())
            ]

            print("\n[ORCHESTRATOR] All agent monitoring loops started")
            print("[ORCHESTRATOR] Swarm is operational - monitoring for threats...")

            # Demo sequence to show swarm capabilities
            await self._run_demo_sequence()

            # Keep swarm running until shutdown
            await self._monitor_swarm_health(monitoring_tasks)

        except KeyboardInterrupt:
            print("\n[ORCHESTRATOR] Shutdown signal received")
        finally:
            await self._shutdown_swarm(monitoring_tasks)

    async def _run_demo_sequence(self):
        """Run a demonstration of swarm capabilities"""
        print("\n" + "=" * 60)
        print("SWARM DEMONSTRATION: Multi-Agent Biodefense Pipeline")
        print("=" * 60)

        # Wait for agents to stabilize
        await asyncio.sleep(3)

        # Trigger manual scan to demonstrate workflow
        print("\n[ORCHESTRATOR] Triggering satellite scan for demonstration...")
        await self.earth_watcher.run_primary_function()

        # Allow message propagation
        await asyncio.sleep(2)

        # Show swarm status
        await self._display_swarm_status()

        print("\n[ORCHESTRATOR] Demo complete. Swarm entering continuous monitoring...")

    async def _monitor_swarm_health(self, monitoring_tasks):
        """Monitor swarm health and handle shutdown"""
        health_check_interval = 30  # 30 seconds

        while not self.shutdown_requested:
            try:
                # Check if any monitoring tasks have failed
                for i, task in enumerate(monitoring_tasks):
                    if task.done():
                        if task.exception():
                            agent_name = ['EarthWatcher', 'BioScientist', 'BiotechExecutive', 'TelegramInterface'][i]
                            print(f"[ORCHESTRATOR] WARNING: {agent_name} monitoring failed: {task.exception()}")

                # Periodic health display
                await self._display_swarm_status()

                await asyncio.sleep(health_check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[ORCHESTRATOR] Health monitoring error: {e}")
                await asyncio.sleep(10)

    async def _display_swarm_status(self):
        """Display current swarm status"""
        status = self.coordinator.get_swarm_status()

        print(f"\n[ORCHESTRATOR] === SWARM STATUS ===")
        print(f"Running: {status['is_running']}")
        print(f"Active Agents: {status['agent_count']}")
        print(f"Messages Processed: {status['message_history_count']}")

        for name, agent_status in status['agents'].items():
            activity = agent_status['state'].get('last_activity', 'Never')
            if activity != 'Never':
                activity = activity.split('T')[1][:8]  # Just show time
            print(f"  {name}: {agent_status['state']['status']} (last: {activity})")

        # Show individual agent details
        print(f"\n[EARTH_WATCHER] {self.earth_watcher.get_monitoring_status()['watchdog_status']}")
        print(f"[BIO_SCIENTIST] Memory: {self.bio_scientist.get_synthesis_status()['memory_status']}")
        print(f"[BIOTECH_EXEC] Revenue: ${self.biotech_executive.get_commercial_status()['total_revenue']:.2f}")
        print(f"[TELEGRAM] Status: {self.telegram_interface.get_interface_status()['telegram_status']}")

    async def _shutdown_swarm(self, monitoring_tasks):
        """Graceful swarm shutdown"""
        print("\n[ORCHESTRATOR] Initiating graceful shutdown...")

        # Cancel monitoring tasks
        for task in monitoring_tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to clean up
        await asyncio.gather(*monitoring_tasks, return_exceptions=True)

        # Stop swarm coordinator
        await self.coordinator.stop_swarm()

        print("[ORCHESTRATOR] Swarm shutdown complete")

    def request_shutdown(self):
        """Request swarm shutdown"""
        self.shutdown_requested = True

async def main():
    """Main entry point for OpenClaw biodefense swarm"""

    # Check for Telegram token (optional for demo)
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not telegram_token:
        print("[MAIN] No TELEGRAM_BOT_TOKEN found - using simulation mode")

    # Create and start orchestrator
    orchestrator = BiodefenseSwarmOrchestrator(telegram_token)

    # Handle shutdown signals
    def signal_handler(signum, frame):
        print(f"\n[MAIN] Signal {signum} received")
        orchestrator.request_shutdown()

    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)

    try:
        await orchestrator.start_swarm()
    except KeyboardInterrupt:
        print("\n[MAIN] Keyboard interrupt received")
    except Exception as e:
        print(f"[MAIN] Swarm error: {e}")
        import traceback
        traceback.print_exc()

    print("[MAIN] OpenClaw biodefense swarm terminated")

if __name__ == "__main__":
    print("Starting OpenClaw Multi-Agent Biodefense Swarm...")
    print("Press Ctrl+C to shutdown")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")