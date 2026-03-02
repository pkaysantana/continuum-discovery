#!/usr/bin/env python3
"""Test ESMFold API with a simple sequence"""

import requests

# Test with a simple, known-good sequence
test_sequence = "MKQLEDKVEELLSKNYHLENEVARLKKLVGER"
url = "https://api.esmatlas.com/foldSequence/v1/pdb/"

print(f"Testing ESMFold API with sequence: {test_sequence}")
print(f"Length: {len(test_sequence)}")

# Check characters
chars = set(test_sequence)
standard_aa = set('ACDEFGHIKLMNPQRSTVWY')
print(f"Characters in sequence: {sorted(chars)}")
print(f"All standard AAs: {chars.issubset(standard_aa)}")

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = {'sequence': test_sequence}

try:
    response = requests.post(url, data=data, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response length: {len(response.text)}")

    if response.status_code == 200:
        print("SUCCESS! ESMFold API is working")
        print("First 200 chars of response:")
        print(response.text[:200])
    else:
        print("FAILED!")
        print("Response text:")
        print(response.text[:500])

except Exception as e:
    print(f"Exception: {e}")