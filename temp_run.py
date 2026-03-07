
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
