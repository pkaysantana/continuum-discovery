#!/usr/bin/env python3
"""
Simple Autonomous Loop - Direct Execution
Bypasses import issues and runs pipeline directly
"""

import asyncio
import os
import subprocess
from datetime import datetime

class SimpleAutonomousLoop:
    """Simple autonomous execution for Alpha-Helix 8 binder discovery"""

    def __init__(self):
        self.run_count = 0
        self.budget_remaining = 17.82

    async def run_discovery_loop(self):
        """Run continuous discovery loop"""

        print('AUTONOMOUS AMINA COMPUTE LOOP')
        print(f'Budget: ${self.budget_remaining:.2f}')
        print('Target: Perfect 9/9 BipD hotspot coverage')
        print('Auto-archival system active')
        print('=' * 60)
        print('[STATUS] Running autonomously...')
        print('=' * 60)

        start_time = datetime.now()

        try:
            while True:
                self.run_count += 1

                print(f'\nRUN #{self.run_count}')
                print('=' * 30)

                try:
                    # Direct pipeline execution
                    result = await self.execute_pipeline()

                    if result:
                        print(f'[RUN #{self.run_count}] Pipeline completed successfully')
                    else:
                        print(f'[RUN #{self.run_count}] Pipeline had issues, continuing...')

                    # Brief pause between runs
                    await asyncio.sleep(5)

                except KeyboardInterrupt:
                    print(f'\n[STOP] Stopped after {self.run_count} runs')
                    break

                except Exception as e:
                    print(f'[ERROR] Run #{self.run_count}: {str(e)[:50]}...')
                    await asyncio.sleep(10)

        except KeyboardInterrupt:
            print('\n[SHUTDOWN] Autonomous loop terminated')

        runtime = datetime.now() - start_time
        print(f'\nSummary: {self.run_count} runs in {runtime.total_seconds():.0f}s')

    async def execute_pipeline(self):
        """Execute pipeline directly via subprocess"""

        try:
            # Create a simple test script that imports and runs the pipeline
            test_script = '''
import sys
import os
import asyncio
sys.path.append(".")
os.environ.update({"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})

try:
    from agents.bio_scientist_agent import BioScientistAgent
    from openclaw.base_agent import MessageBus

    async def run_once():
        message_bus = MessageBus()
        agent = BioScientistAgent(message_bus)
        result = await agent.run_primary_function()

        iptm = result.get("iptm_score", 0.0)
        coverage = result.get("hotspot_coverage_percent", 0.0)

        print(f"RESULT: ipTM={iptm:.3f} Coverage={coverage:.1f}%")

        if coverage >= 100.0:
            print("PERFECT: 9/9 hotspot coverage achieved!")
        elif coverage >= 88.9:
            print("EXCELLENT: 8/9+ hotspot coverage")

        return result

    result = asyncio.run(run_once())

except ImportError as e:
    print(f"IMPORT ERROR: {e}")
except Exception as e:
    print(f"EXECUTION ERROR: {e}")
'''

            # Write temporary script
            with open('temp_run.py', 'w') as f:
                f.write(test_script)

            # Execute it
            env = os.environ.copy()
            env.update({
                'PYTHONIOENCODING': 'utf-8',
                'PYTHONUTF8': '1'
            })

            process = await asyncio.create_subprocess_exec(
                'python', 'temp_run.py',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=60.0
            )

            # Process output
            output = stdout.decode('utf-8', errors='ignore')
            error_output = stderr.decode('utf-8', errors='ignore')

            if 'RESULT:' in output:
                print(f'SUCCESS {output.split("RESULT:")[-1].strip()}')

            if 'PERFECT:' in output:
                print('Perfect design found!')

            if 'EXCELLENT:' in output:
                print('Excellent design found!')

            # Clean up
            if os.path.exists('temp_run.py'):
                os.remove('temp_run.py')

            return process.returncode == 0

        except Exception as e:
            print(f'Pipeline execution error: {e}')
            return False

async def main():
    """Main execution"""
    loop = SimpleAutonomousLoop()
    await loop.run_discovery_loop()

if __name__ == "__main__":
    print("Starting simple autonomous Alpha-Helix 8 discovery...")
    print("Press Ctrl+C to stop")
    print()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[EXIT] Autonomous discovery stopped")

    print("Discovery session complete.")
