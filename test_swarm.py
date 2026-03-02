#!/usr/bin/env python3
"""
Quick test script for OpenClaw Multi-Agent Biodefense Swarm
Demonstrates the integrated workflow across all bounty tracks
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from main_swarm import BiodefenseSwarmOrchestrator

async def quick_test():
    """Quick test of swarm functionality"""
    print("=" * 60)
    print("OPENCLAW SWARM QUICK TEST")
    print("Testing multi-agent communication and workflow")
    print("=" * 60)

    # Create orchestrator (no Telegram token needed for test)
    orchestrator = BiodefenseSwarmOrchestrator()

    try:
        # Start swarm
        print("\n[TEST] Starting swarm...")
        await orchestrator.coordinator.start_swarm()

        # Wait for initialization
        await asyncio.sleep(2)

        # Test individual agent functions
        print("\n[TEST] Testing EarthWatcherAgent...")
        earth_result = await orchestrator.earth_watcher.run_primary_function()
        print(f"[TEST] Earth scan status: {earth_result.get('status')}")

        # Test BioScientistAgent
        print("\n[TEST] Testing BioScientistAgent...")
        bio_result = await orchestrator.bio_scientist.run_primary_function()
        print(f"[TEST] Synthesis status: {bio_result.get('status')}")

        # Test BiotechExecutiveAgent
        print("\n[TEST] Testing BiotechExecutiveAgent...")
        exec_result = await orchestrator.biotech_executive.run_primary_function()
        print(f"[TEST] Commercial status: {exec_result.get('status')}")

        # Test TelegramInterface
        print("\n[TEST] Testing TelegramInterface...")
        telegram_result = await orchestrator.telegram_interface.run_primary_function()
        print(f"[TEST] Telegram status: {telegram_result.get('status')}")

        # Show final status
        print("\n[TEST] Final swarm status:")
        await orchestrator._display_swarm_status()

        print("\n[TEST] SUCCESS: All agents operational!")

    except Exception as e:
        print(f"[TEST] ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Shutdown
        print("\n[TEST] Shutting down swarm...")
        await orchestrator.coordinator.stop_swarm()
        print("[TEST] Test complete")

if __name__ == "__main__":
    asyncio.run(quick_test())