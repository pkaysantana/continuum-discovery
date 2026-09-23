#!/usr/bin/env python3
"""
Root wrapper for Whole-Cohort Structure Integrity Audit.
Executes experiments/compound_to_exposure/audit/whole_cohort_structure_integrity.py.
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET_SCRIPT = ROOT / "experiments" / "compound_to_exposure" / "audit" / "whole_cohort_structure_integrity.py"
PYTHON_EXE = ROOT / "experiments" / "compound_to_exposure" / ".venv" / "Scripts" / "python.exe"

if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)

res = subprocess.run([str(PYTHON_EXE), str(TARGET_SCRIPT)], cwd=str(ROOT))
sys.exit(res.returncode)
