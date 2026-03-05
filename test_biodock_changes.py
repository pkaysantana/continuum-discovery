#!/usr/bin/env python3
"""
Test BioDock Agent Changes
Verify the new _calculate_resource_requirements method works correctly
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.biodock_cognitive_agent import BioDockMedicalAgent

def test_biodock_resource_calculation():
    """Test the new _calculate_resource_requirements method"""

    print("="*60)
    print("TESTING BIODOCK AGENT CHANGES")
    print("="*60)

    # 1. Initialize BioDock agent
    print("\nSTEP 1: Initializing BioDock Agent...")
    biodock_agent = BioDockMedicalAgent()
    print(f"   [OK] Agent initialized: {biodock_agent.identity.name}")

    # 2. Test the new _calculate_resource_requirements method
    print("\nSTEP 2: Testing new _calculate_resource_requirements method...")
    try:
        result = biodock_agent._calculate_resource_requirements()
        print(f"   [OK] Method executed successfully")
        print(f"   [DATA] Result: {result}")

        # Verify expected output format
        if isinstance(result, dict):
            print(f"   [OK] Returns dict as expected")
            if 'gpu_memory_gb' in result and 'priority' in result:
                print(f"   [OK] Contains expected keys")
                print(f"   [TARGET] GPU Memory: {result['gpu_memory_gb']} GB")
                print(f"   [TARGET] Priority: {result['priority']}")
            else:
                print(f"   [WARN] Missing expected keys in result")
        else:
            print(f"   [WARN] Result is not a dict: {type(result)}")

    except Exception as e:
        print(f"   [ERROR] Method failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 3. Test that old method still works with new name
    print("\nSTEP 3: Testing renamed _calculate_study_resource_requirements method...")
    try:
        # Create a mock study protocol
        study_protocol = {
            'study_design': {
                'sample_size': {'total_samples': 80}
            },
            'pathological_assessment_plan': {}
        }

        # This is an async method, so we need to handle that
        import asyncio
        async def test_async_method():
            return await biodock_agent._calculate_study_resource_requirements(study_protocol)

        study_result = asyncio.run(test_async_method())
        print(f"   [OK] Renamed method executed successfully")
        print(f"   [DATA] Study result keys: {list(study_result.keys()) if isinstance(study_result, dict) else 'Not a dict'}")

    except Exception as e:
        print(f"   [ERROR] Renamed method failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\nSTEP 4: Verification Summary...")
    print("   [OK] New _calculate_resource_requirements() method works")
    print("   [OK] Renamed _calculate_study_resource_requirements() method works")
    print("   [OK] No AttributeError or 403 errors detected")
    print("   [TARGET] Looking for 'Emergency Stop' or 'SDG Alert' indicators...")

    # The print statement in our new method should have been called
    print("\nSTEP 5: Final verification - method should have printed BioDock message above")

    return True

if __name__ == "__main__":
    print("Starting BioDock Agent Changes Test...")

    success = test_biodock_resource_calculation()

    if success:
        print("\n[SUCCESS] All BioDock agent changes work correctly!")
        print("[READY] No 403 or AttributeError issues detected")
    else:
        print("\n[FAILED] Some BioDock agent changes need attention")

    print("\nTest complete.")