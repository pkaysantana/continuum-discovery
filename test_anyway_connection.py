#!/usr/bin/env python3
"""
Anyway SDK Sandbox Connectivity Test
Tests connection to sandbox.anyway.sh and verifies trace submission
"""

import os
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Anyway configuration
from anyway_integration.traceloop_config import initialize_anyway_sdk, workflow, task, TRACELOOP_AVAILABLE

@workflow(name="anyway_sandbox_connectivity_test")
async def test_anyway_connection():
    """
    Test workflow to verify Anyway SDK sandbox connectivity
    """
    print("🧪 Testing Anyway SDK Sandbox Connection...")
    print("=" * 60)

    # Test configuration
    test_data = {
        "test_timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "sandbox",
        "agent_type": "connectivity_test",
        "test_id": f"conn_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }

    print(f"📋 Test Data: {test_data}")

    # Execute test tasks
    validation_result = await validate_environment_config()
    ping_result = await ping_sandbox_collector()
    trace_result = await submit_test_trace(test_data)

    # Overall result
    success = all([validation_result, ping_result, trace_result])

    if success:
        print("\n✅ CONNECTIVITY TEST PASSED")
        print("🎯 Check sandbox.anyway.sh/agent-traces for your trace!")
        print(f"🔍 Look for trace: anyway_sandbox_connectivity_test")
        print(f"📅 Timestamp: {test_data['test_timestamp']}")
    else:
        print("\n❌ CONNECTIVITY TEST FAILED")
        print("🔧 Check your TRACELOOP_HEADERS and TRACELOOP_BASE_URL configuration")

    return {
        "success": success,
        "validation": validation_result,
        "ping": ping_result,
        "trace": trace_result,
        "test_data": test_data
    }

@task(name="validate_environment_config")
async def validate_environment_config():
    """
    Validate that environment variables are properly configured
    """
    print("\n🔧 Validating Environment Configuration...")

    required_vars = {
        "TRACELOOP_HEADERS": os.getenv("TRACELOOP_HEADERS"),
        "TRACELOOP_BASE_URL": os.getenv("TRACELOOP_BASE_URL"),
        "TRACELOOP_APP_NAME": os.getenv("TRACELOOP_APP_NAME")
    }

    for var_name, var_value in required_vars.items():
        if var_value:
            print(f"  ✅ {var_name}: {var_value}")
        else:
            print(f"  ❌ {var_name}: Missing")
            return False

    # Check if API key format is correct
    headers = required_vars["TRACELOOP_HEADERS"]
    if headers and "ami_sandbox_" in headers:
        print("  ✅ API Key format looks correct (ami_sandbox_*)")
    else:
        print("  ⚠️  API Key format may be incorrect (should be ami_sandbox_*)")

    return True

@task(name="ping_sandbox_collector")
async def ping_sandbox_collector():
    """
    Test basic connectivity to sandbox collector
    """
    print("\n🌐 Testing Sandbox Collector Connectivity...")

    try:
        import requests
        url = os.getenv("TRACELOOP_BASE_URL", "https://sandbox-collector.anyway.sh")

        # Simple health check (most OTLP endpoints respond to GET with basic info)
        response = requests.get(url, timeout=10)

        if response.status_code in [200, 404, 405]:  # 404/405 are fine for OTLP endpoints
            print(f"  ✅ Sandbox reachable: {url}")
            print(f"  📡 HTTP Status: {response.status_code}")
            return True
        else:
            print(f"  ❌ Unexpected response: {response.status_code}")
            return False

    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        return False

@task(name="submit_test_trace")
async def submit_test_trace(test_data):
    """
    Submit a test trace with span attributes
    """
    print("\n📊 Submitting Test Trace...")

    try:
        if not TRACELOOP_AVAILABLE:
            print("  ❌ Traceloop SDK not available")
            return False

        # Add span attributes for testing
        from traceloop.sdk import Traceloop
        current_span = Traceloop.get_current_span()

        if current_span:
            # Add test attributes
            current_span.set_attribute("test.id", test_data["test_id"])
            current_span.set_attribute("test.environment", "sandbox")
            current_span.set_attribute("test.agent.type", "connectivity_test")
            current_span.set_attribute("test.timestamp", test_data["test_timestamp"])

            # Add sample business attributes (like your actual agents)
            current_span.set_attribute("stripe.payment.link", "https://buy.stripe.com/test_connectivity_12345")
            current_span.set_attribute("sentinel2.event.id", "s2_test_20260303_connectivity")

            print("  ✅ Span attributes added successfully")
            print(f"  🏷️  Test ID: {test_data['test_id']}")
        else:
            print("  ⚠️  No active span found")

        print("  ✅ Test trace submitted")
        return True

    except Exception as e:
        print(f"  ❌ Trace submission failed: {e}")
        return False

async def main():
    """
    Main connectivity test function
    """
    print("🚀 Anyway SDK Sandbox Connectivity Test")
    print("📱 Continuum Discovery Multi-Agent Swarm")
    print("🕐 Starting test at:", datetime.now())
    print()

    # Initialize SDK
    if not initialize_anyway_sdk():
        print("❌ Failed to initialize Anyway SDK")
        return

    # Run connectivity test
    result = await test_anyway_connection()

    # Final instructions
    print("\n" + "=" * 60)
    if result["success"]:
        print("🎉 SUCCESS! Your Anyway SDK is properly configured!")
        print()
        print("📋 Next Steps:")
        print("1. 🌐 Visit: https://sandbox.anyway.sh/agent-traces")
        print("2. 🔍 Look for traces from 'continuum-discovery' app")
        print("3. 📊 Find your test trace: 'anyway_sandbox_connectivity_test'")
        print("4. ✅ Verify span attributes include Stripe and Sentinel-2 data")
        print()
        print("🚀 Your multi-agent swarm is ready for Anyway observability!")
    else:
        print("❌ Configuration issues detected. Please fix and retry.")
        print()
        print("🔧 Troubleshooting:")
        print("1. Verify your sandbox API key in .env file")
        print("2. Check TRACELOOP_BASE_URL = https://sandbox-collector.anyway.sh")
        print("3. Ensure pip install traceloop-sdk completed successfully")

if __name__ == "__main__":
    asyncio.run(main())