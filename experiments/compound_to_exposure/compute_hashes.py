import hashlib
from pathlib import Path

files_to_hash = [
    "src/execute_v2.py",
    "src/run.py",
    "tests/test_execute_v2.py",
    "tests/test_validation_preflight.py",
    "splits/master_partition.csv",
    "docs/STATISTICAL_ANALYSIS_PREREGISTRATION.md",
    "docs/V2_PROTOCOL_AMENDMENT_001_BIOGEN_SELECTION.md"
]

for f in files_to_hash:
    path = Path(f)
    if path.exists():
        with open(path, "rb") as file:
            h = hashlib.sha256(file.read()).hexdigest()
            print(f"{f}: {h}")
    else:
        print(f"{f}: NOT FOUND")
