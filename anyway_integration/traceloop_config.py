#!/usr/bin/env python3
"""
Anyway SDK (Traceloop) Configuration for Sandbox Environment
Initializes SDK with sandbox endpoint and proper authentication
"""

import os
from typing import Optional

try:
    from traceloop.sdk import Traceloop
    from traceloop.sdk.decorators import workflow, task
    TRACELOOP_AVAILABLE = True
    print("[ANYWAY] Traceloop SDK available")
except ImportError:
    print("[ANYWAY] ERROR: Traceloop SDK not installed")
    print("[ANYWAY] Install with: pip install traceloop-sdk")
    TRACELOOP_AVAILABLE = False

    # Mock decorators to prevent crashes
    def workflow(name: Optional[str] = None):
        def decorator(func):
            return func
        return decorator

    def task(name: Optional[str] = None):
        def decorator(func):
            return func
        return decorator

def initialize_anyway_sdk():
    """
    Initialize Anyway SDK with Sandbox Environment configuration
    """
    if not TRACELOOP_AVAILABLE:
        print("[ANYWAY] WARNING: Using mock decorators - install traceloop-sdk for real tracing")
        return False

    try:
        # Load environment variables
        api_endpoint = os.getenv('TRACELOOP_BASE_URL', 'https://sandbox-collector.anyway.sh')
        app_name = os.getenv('TRACELOOP_APP_NAME', 'continuum-discovery')
        disable_batch = os.getenv('TRACELOOP_DISABLE_BATCH', 'true').lower() == 'true'

        # Initialize Traceloop SDK with sandbox configuration
        Traceloop.init(
            api_endpoint=api_endpoint,
            app_name=app_name,
            disable_batch=disable_batch,
            api_key=None,  # Will use TRACELOOP_HEADERS from environment
            generate_logs=True,  # Enable logging for debugging
            exporter='otlp_http'  # Use HTTP exporter for sandbox
        )

        print(f"[ANYWAY] ✅ SDK initialized successfully")
        print(f"[ANYWAY] API Endpoint: {api_endpoint}")
        print(f"[ANYWAY] App Name: {app_name}")
        print(f"[ANYWAY] Disable Batch: {disable_batch}")

        return True

    except Exception as e:
        print(f"[ANYWAY] ERROR: Failed to initialize SDK: {e}")
        return False

# Export decorators for easy import
__all__ = ['workflow', 'task', 'initialize_anyway_sdk', 'TRACELOOP_AVAILABLE']