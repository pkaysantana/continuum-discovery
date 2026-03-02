#!/usr/bin/env python3
"""Test different ESMFold API formats"""

import requests
import json

test_sequence = "MKQLEDKVEELLSKNYHLENEVARLKKLVGER"

# Try different API endpoints and formats
endpoints = [
    "https://api.esmatlas.com/foldSequence/v1/pdb/",
    "https://api.esmatlas.com/fold",
    "https://api.esmatlas.com/v1/fold",
]

formats = [
    # Format 1: form data
    {
        'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
        'data': {'sequence': test_sequence},
        'json': None
    },
    # Format 2: JSON
    {
        'headers': {'Content-Type': 'application/json'},
        'data': None,
        'json': {'sequence': test_sequence}
    },
    # Format 3: plain text
    {
        'headers': {'Content-Type': 'text/plain'},
        'data': test_sequence,
        'json': None
    }
]

for i, url in enumerate(endpoints):
    print(f"\\n=== Testing endpoint {i+1}: {url} ===")

    for j, fmt in enumerate(formats):
        print(f"\\nFormat {j+1}:")
        try:
            if fmt['json']:
                response = requests.post(url,
                                       headers=fmt['headers'],
                                       json=fmt['json'],
                                       timeout=10)
            else:
                response = requests.post(url,
                                       headers=fmt['headers'],
                                       data=fmt['data'],
                                       timeout=10)

            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  SUCCESS! Response length: {len(response.text)}")
                break
            else:
                print(f"  Response: {response.text[:200]}")

        except Exception as e:
            print(f"  Exception: {e}")

    # If we found a working format, stop testing other endpoints
    if response.status_code == 200:
        print(f"\\n*** FOUND WORKING ENDPOINT ***")
        print(f"URL: {url}")
        print(f"Format: {j+1}")
        break