# Test Documentation

## 1. Canonical Suite
To run the canonical test suite:
```bash
.venv\Scripts\python.exe src/run.py test
```
**Expected canonical count**: 133 tests.

## 2. Supplementary Correction 002/003 Regression Suite
To run the supplementary regression checks:
```bash
.venv\Scripts\python.exe -m unittest tests/regression_checks.py
```

### Important Notes on the Regression Suite
- The `regression_checks.py` file is intentionally not named `test_*.py`.
- It contains supplementary forensic and regression coverage testing specific audit findings and implementation invariants from Corrections 002/003.
- It is deliberately kept outside the automatic discovery because it relies on source-string matches and behavioral side-channel checks rather than the primary scientific logic.
- It is **not** part of the historical canonical 133-test suite.
- It should be run independently before any V2 execution-ready freeze.
- The test count for this suite is exactly 7 substantive tests (all empty placeholder tests were implemented in Correction 004).

### Purpose of Supplementary Checks
The suite ensures that:
- Production code behaves safely when `smiles` is missing (relying strictly on `canonical_smiles_rdkit`).
- The `master_partition.csv` scoping strictly expects the internal `splits/` directory.
- `execute_v2.py` genuinely executes preflight schema validation without entering the model-fitting `.fit()` loops.
- `R1` and `R2` representations construct schemas of the correct dimension exactly.
- Real structures pass through identical vector generation.
