#!/usr/bin/env python3
"""
Test the Macro-Alert Biodefense Watchdog with Simulated Flood Event
Demonstrates the complete trigger workflow
"""

import sys
import os
sys.path.append('./scripts')

from scripts.watchdog import BiodefenseWatchdog
from datetime import datetime
import numpy as np

def simulate_flood_event():
    """Simulate a flood detection scenario"""
    print("SIMULATING FLOOD EVENT FOR TESTING")
    print("="*50)

    # Initialize watchdog
    watchdog = BiodefenseWatchdog()

    # Simulate flood detection data
    simulated_flood_data = {
        'water_percentage': 12.5,  # Exceeds 5% threshold
        'ndwi_stats': {
            'mean': 0.45,
            'max': 0.78,
            'min': -0.23
        },
        'flood_detected': True,
        'region': watchdog.endemic_regions['northern_australia'],
        'timestamp': datetime.now()
    }

    print(f"Simulated water coverage: {simulated_flood_data['water_percentage']}%")
    print(f"NDWI mean value: {simulated_flood_data['ndwi_stats']['mean']}")
    print(f"Flood detection: {simulated_flood_data['flood_detected']}")
    print()

    # Trigger the biodefense pipeline
    print("TRIGGERING BIODEFENSE PIPELINE...")
    alert_file = watchdog.trigger_biodefense_pipeline(simulated_flood_data)

    print(f"\\nAlert logged to: {alert_file}")
    return alert_file

if __name__ == "__main__":
    simulate_flood_event()