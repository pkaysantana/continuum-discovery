#!/usr/bin/env python3
"""
Autonomous Amina Compute Loop
Continuously runs AminoAnalytica pipeline to hunt for perfect Alpha-Helix 8 binders
Auto-saves winning designs with archival system
"""

import asyncio
import os
import sys
from datetime import datetime
from agents.bio_scientist_agent import BioScientistAgent
from openclaw.base_agent import MessageBus

class AutonomousComputeLoop:
    """Autonomous pipeline execution for Alpha-Helix 8 binder discovery"""

    def __init__(self):
        self.remaining_budget = 17.82
        self.run_count = 0
        self.perfect_designs = 0
        self.excellent_designs = 0

        # Set environment for Windows compatibility
        os.environ.update({
            'PYTHONIOENCODING': 'utf-8',
            'PYTHONUTF8': '1'
        })

    async def run_continuous_discovery(self):
        """Run continuous discovery loop"""

        print('AUTONOMOUS AMINA COMPUTE LOOP STARTING')
        print(f'Budget: ${self.remaining_budget:.2f} - Live Alpha-Helix 8 Binder Hunt')
        print('Target: Perfect 9/9 BipD hotspot coverage')
        print('Auto-saving winners to outputs/winning_binders/')
        print('ESMFold hybrid filtering active')
        print('=' * 80)
        print('[STATUS] Pipeline running autonomously...')
        print('[STATUS] Stepping away - hunting for perfect binders!')
        print('=' * 80)

        # Initialize agent
        message_bus = MessageBus()
        agent = BioScientistAgent(message_bus)

        start_time = datetime.now()

        try:
            while True:
                self.run_count += 1

                print(f'\nAUTONOMOUS RUN #{self.run_count}')
                print('=' * 40)

                try:
                    # Execute pipeline
                    result = await agent.run_primary_function()

                    # Extract metrics
                    iptm = result.get('iptm_score', 0.0)
                    coverage = result.get('hotspot_coverage_percent', 0.0)
                    pae = result.get('interface_pae', 0.0)

                    print(f'[RUN #{self.run_count}] ipTM: {iptm:.3f} | Coverage: {coverage:.1f}% | PAE: {pae:.2f}A')

                    # Analyze results
                    if coverage >= 100.0:
                        self.perfect_designs += 1
                        print(f'PERFECT 9/9 COVERAGE ACHIEVED! Run #{self.run_count}')
                        print(f'WINNER ipTM: {iptm:.3f} | PAE: {pae:.2f}A')
                        print(f'Total perfect designs found: {self.perfect_designs}')

                    elif coverage >= 88.9:
                        self.excellent_designs += 1
                        print(f'EXCELLENT 8/9+ coverage! Run #{self.run_count}')
                        print(f'Total excellent designs: {self.excellent_designs}')

                    else:
                        print(f'Progress: {coverage:.1f}% coverage achieved')

                    # Brief status update
                    runtime = datetime.now() - start_time
                    print(f'[STATUS] Runtime: {runtime.total_seconds():.0f}s | Perfect: {self.perfect_designs} | Excellent: {self.excellent_designs}')

                    # Short pause between runs to avoid overwhelming the system
                    await asyncio.sleep(3)

                except KeyboardInterrupt:
                    print(f'\n[STOP] User interrupted after {self.run_count} runs')
                    break

                except Exception as e:
                    print(f'[ERROR] Run #{self.run_count}: {str(e)[:100]}...')
                    print('[RETRY] Continuing autonomous loop...')
                    await asyncio.sleep(5)

        except KeyboardInterrupt:
            print(f'\n[SHUTDOWN] Autonomous loop stopped')

        finally:
            await self.print_final_summary(start_time)

    async def print_final_summary(self, start_time):
        """Print final discovery summary"""

        runtime = datetime.now() - start_time

        print('\n' + '=' * 80)
        print('AUTONOMOUS DISCOVERY COMPLETE')
        print('=' * 80)
        print(f'Total Runs: {self.run_count}')
        print(f'Perfect Designs (9/9): {self.perfect_designs}')
        print(f'Excellent Designs (8/9+): {self.excellent_designs}')
        print(f'Total Runtime: {runtime.total_seconds():.0f} seconds')
        print(f'Winners auto-saved to: outputs/winning_binders/')

        # Check for saved files
        if os.path.exists('outputs/winning_binders'):
            saved_files = [f for f in os.listdir('outputs/winning_binders') if f.endswith('.json')]
            print(f'Designs Archived: {len(saved_files)} high-quality winners')

        print('\nAlpha-Helix 8 Binder Discovery Mission Complete!')

async def main():
    """Main entry point"""

    loop = AutonomousComputeLoop()
    await loop.run_continuous_discovery()

if __name__ == "__main__":
    print("Starting autonomous Alpha-Helix 8 binder discovery...")
    print("Press Ctrl+C to stop the autonomous loop")
    print()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[EXIT] Autonomous loop terminated by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")

    print("Autonomous discovery session ended.")
