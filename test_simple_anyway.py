#!/usr/bin/env python3
"""
Simple Anyway SDK Test (without emojis)
"""
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Import Anyway configuration
sys.path.append('.')
from anyway_integration.traceloop_config import initialize_anyway_sdk, TRACELOOP_AVAILABLE

def test_config():
    """Test environment configuration"""
    print("\nTesting environment configuration...")

    required_vars = {
        "TRACELOOP_HEADERS": os.getenv("TRACELOOP_HEADERS"),
        "TRACELOOP_BASE_URL": os.getenv("TRACELOOP_BASE_URL"),
        "TRACELOOP_APP_NAME": os.getenv("TRACELOOP_APP_NAME")
    }

    all_good = True
    for var_name, var_value in required_vars.items():
        if var_value:
            print(f"  OK {var_name}: {var_value}")
        else:
            print(f"  ERROR {var_name}: Missing")
            all_good = False

    # Check API key format
    headers = required_vars["TRACELOOP_HEADERS"]
    if headers:
        if "sk_test_" in headers:
            print("  INFO API Key format: sk_test_ (provided by user)")
        elif "ami_sandbox_" in headers:
            print("  INFO API Key format: ami_sandbox_ (expected format)")
        else:
            print("  WARNING Unknown API key format")

    return all_good

def test_connectivity():
    """Test basic connectivity"""
    print("\nTesting connectivity...")
    try:
        import requests
        url = os.getenv("TRACELOOP_BASE_URL", "https://sandbox-collector.anyway.sh")
        response = requests.get(url, timeout=10)
        print(f"  Endpoint: {url}")
        print(f"  Status: {response.status_code}")
        return response.status_code in [200, 404, 405]
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    """Main test function"""
    print("Anyway SDK Simple Test")
    print("=" * 50)

    # Test 1: Environment
    config_ok = test_config()

    # Test 2: Connectivity
    connection_ok = test_connectivity()

    # Test 3: SDK Initialization
    print("\nTesting SDK initialization...")
    if TRACELOOP_AVAILABLE:
        sdk_ok = initialize_anyway_sdk()
        print(f"  SDK Init: {'OK' if sdk_ok else 'FAILED'}")
    else:
        print("  ERROR: Traceloop SDK not available")
        sdk_ok = False

    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"  Environment Config: {'PASS' if config_ok else 'FAIL'}")
    print(f"  Network Connectivity: {'PASS' if connection_ok else 'FAIL'}")
    print(f"  SDK Initialization: {'PASS' if sdk_ok else 'FAIL'}")

    all_passed = config_ok and connection_ok and sdk_ok
    print(f"\nOVERALL: {'SUCCESS' if all_passed else 'FAILED'}")

    if all_passed:
        print("\nYour Anyway SDK integration is working!")
        print("Visit: https://sandbox.anyway.sh/agent-traces")
    else:
        print("\nPlease check the failed components above.")

if __name__ == "__main__":
    main()