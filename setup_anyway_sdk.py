#!/usr/bin/env python3
"""
Anyway SDK Setup Script
Automates the installation and configuration of Anyway SDK for Continuum Discovery
"""

import os
import subprocess
import sys
from pathlib import Path

def install_dependencies():
    """Install required dependencies for Anyway SDK"""
    print("📦 Installing Anyway SDK dependencies...")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "-r", "anyway_requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_env_configuration():
    """Check if .env file is properly configured"""
    print("\n🔧 Checking environment configuration...")

    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("🔧 Create .env file from .env.example first")
        return False

    # Read .env file
    with open(env_file, 'r') as f:
        env_content = f.read()

    required_vars = [
        "TRACELOOP_HEADERS",
        "TRACELOOP_BASE_URL"
    ]

    missing_vars = []
    for var in required_vars:
        if var not in env_content:
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False

    # Check for sandbox key format
    if "ami_sandbox_your_key" in env_content:
        print("⚠️  Replace 'ami_sandbox_your_key' with your actual Anyway sandbox API key")
        return False

    print("✅ Environment configuration looks good")
    return True

def test_connectivity():
    """Test connection to Anyway sandbox"""
    print("\n🧪 Testing Anyway SDK connectivity...")

    try:
        result = subprocess.run([
            sys.executable, "test_anyway_connection.py"
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ Connectivity test passed!")
            return True
        else:
            print("❌ Connectivity test failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("❌ Connectivity test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running connectivity test: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Anyway SDK Setup for Continuum Discovery")
    print("=" * 60)

    # Step 1: Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Step 2: Check environment
    if not check_env_configuration():
        print("\n🔧 Please fix environment configuration and run setup again")
        sys.exit(1)

    # Step 3: Test connectivity
    if not test_connectivity():
        print("\n🔧 Please check your API key and configuration")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("🎉 Anyway SDK Setup Complete!")
    print()
    print("✅ All dependencies installed")
    print("✅ Environment properly configured")
    print("✅ Sandbox connectivity verified")
    print()
    print("🚀 Your multi-agent swarm is ready for Anyway observability!")
    print("📊 Visit https://sandbox.anyway.sh/agent-traces to see your traces")
    print()
    print("▶️  Next: Run 'python main_swarm.py' to start your instrumented swarm")

if __name__ == "__main__":
    main()