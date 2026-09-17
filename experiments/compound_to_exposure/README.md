# Compound-to-exposure: frozen-source forensic audit

## Scope and authority

EXPECTED_FROM_MEMO: [DATASET_SELECTION_MEMO.md](docs/DATASET_SELECTION_MEMO.md), frozen in commit `9724c17`, is the scientific source of truth. Dataset selection is unchanged: direct ChEMBL is primary; TDC is for benchmark reproduction; its hepatocyte dataset is excluded; Biogen is for within-dataset replication. Rat hepatocytes are audit/exclusion evidence only.

OBSERVED: This checkpoint contains acquisition, identity/censoring/duplicate audits, cohort membership and descriptive chemical properties only. No predictive models, fitting, hyperparameters, target transformations, censor removal, outlier removal, modelling preprocessing or splits were run. No HLM/HH ratio, difference, physiological scaling or correlation was calculated.

## Review entry points

- [Concise findings and unresolved discrepancies](reports/REVIEW_SUMMARY.md)
- [Preserved independent review](reports/AUDIT_REVIEW.md) and [correction archive](reports/revisions/independent-review/amendment.json)
- [Complete audit](reports/DATA_AUDIT.md) and [machine-readable evidence](reports/DATA_AUDIT.json)
- [Provenance table](reports/PROVENANCE_TABLE.csv) and [raw manifest](manifests/source_manifest.json)
- [Microsome row reconciliation](reports/CHEMBL_TDC_MICROSOME_RECONCILIATION.csv)
- [Paired human membership](reports/PAIRED_HUMAN_COHORT_AUDIT.md)
- [Hepatocyte species audit](reports/TDC_HEPATOCYTE_SPECIES_AUDIT.md)
- [Biogen audit](reports/BIOGEN_AUDIT.md)

## Acquisition and identity

OBSERVED: ChEMBL 37 API metadata and every paginated activity response are retained verbatim. Biogen is pinned to author repository commit `b00df003de117ce9e5b381afd886095c5f2af2d5`. All URLs, UTC retrieval times, release information, schemas, byte sizes and SHA-256 hashes are recorded per downloaded file. Source assay organism/taxonomy determines species; a null target-organism field is not substituted for assay metadata.

OBSERVED: TDC acquisition uses the exact **PyTDC 1.1.15 source distribution**, checked against its PyPI SHA-256. The two Dataverse file IDs come from its `name2id` registry, read as literal source data. The package is **not installed or invoked**; this avoids unrelated modelling dependencies and loader filtering. The preserved source loader accepts raw X/Y/ID and drops missing targets; our raw-table audit retains all rows. PyTDC's raw CSV/tabular artifact is the source being audited, not a claimed PyTDC execution.

INFERRED: Structure identity is equality of RDKit 2025.03.6 sanitized isomeric canonical SMILES. Charge, isotopes, stereochemistry and all disconnected components are retained. No salt removal, parent selection or tautomer normalization occurs. Secondary molecule-ID and ChEMBL-declared parent-ID matches are evidence only and never replace the primary strict structure comparison. Missing/invalid structures never match one another.

INFERRED: Numeric label agreement uses exact Decimal equality, without a tolerance or rounding. Original qualifiers are retained separately, so agreement at a censored boundary is not proof of equal true clearance. Missing ChEMBL relations remain UNKNOWN; no implicit equals is assigned. Bare TDC/Biogen numbers have no encoded inequality, but this does not establish that measurements were uncensored. Missing tokens are None, blank/whitespace, NA, N/A, NaN, null and none, case-insensitively; zero is not missing.

INFERRED: Descriptors are only for characterisation: molecular weight, RDKit Crippen cLogP, TPSA, Lipinski HBD/HBA, strict rotatable bonds and fraction Csp3. Statistics are row-weighted (including duplicates), with linear quantiles, IQR and unscaled MAD. Censored numeric values describe supplied boundaries, not latent clearance. Undefined stereo counts use `FindPotentialStereo` elements marked `Unspecified`. All original rows remain in `data/interim/*_rows.csv`; they are evidence tables, not modelling-ready datasets.

## Reproduction

OBSERVED: The checkpoint was produced on Windows with CPython 3.11.16, RDKit 2025.03.6 and NumPy 2.2.6. The installed Pillow dependency is 12.3.0. The installation receipt includes exact wheel URLs and hashes. The environment is isolated inside this experiment; no historical environment is changed.

From the repository root, use a Python 3.11.16 interpreter to create the experiment environment **only when `.venv` does not exist**:

```powershell
python -B experiments/compound_to_exposure/src/run.py bootstrap
```

Then:

```powershell
& experiments/compound_to_exposure/.venv/Scripts/python.exe -B experiments/compound_to_exposure/src/run.py acquire
& experiments/compound_to_exposure/.venv/Scripts/python.exe -B experiments/compound_to_exposure/src/run.py test
& experiments/compound_to_exposure/.venv/Scripts/python.exe -B experiments/compound_to_exposure/src/run.py audit
& experiments/compound_to_exposure/.venv/Scripts/python.exe -B experiments/compound_to_exposure/src/run.py verify
```

OBSERVED: With the committed raw files, acquisition verifies and reuses local bytes without requesting replacement data. A changed URL, missing receipt or mismatched raw hash fails. A fresh acquisition against future live ChEMBL may differ; it is a new acquisition, not a recreation of this snapshot. Use the committed raw inputs for exact reproduction. Reports are also compared byte-for-byte on rerun; environment differences recorded inside reports can cause an explicit mismatch requiring a documented new output location/amendment.

OBSERVED: `src/run.py` records commands, source/input hashes, timestamps, code commit, outputs/hashes and SUCCESS/FAILED status. Tests include offline synthetic failure fixtures and read-only frozen-data regressions against commit `13715550adad0a628e92da6cf34568000ddbc797`, which must remain available in Git history. They compare the complete original machine-readable report (allowing only the documented classification wording and added rule explanation), unchanged evidence tables, raw hashes and receipts. No test supplies replacement scientific results. An initial manifest type error is retained as FAILED with its traceback. The first successful derived audit was explicitly archived before adding ID/parent-ID forensic follow-up; its report hashes and code snapshot are under `reports/revisions/initial-audit/`. The one-time archive action is historical and should not be rerun.

OBSERVED: Independent-review hardening adds shared acquisition/audit checks for constant page totals, contiguous offsets, terminal page metadata, requested assay IDs and unique activity IDs. The frozen audit also enforces the expected 1,102 / 837 / 408 counts. Failure tests cover missing/early-ending pages, repeated IDs, hash and size mismatches, missing receipts, changed download URLs and refusal to overwrite non-identical outputs. Strict hepatocyte duplicate pairs require exactly two rows with one unique structure/value-matching source record per species and no opposite-species value match; the frozen result remains 187. The six other groups have no strict structural match to either source assay. Four microsome tautomer spellings and one hydrate representation remain strict mismatches; the strict overlap remains 1,097.

OBSERVED: The four regenerated audit artifacts were explicitly archived with their original hashes under `reports/revisions/independent-review/` before the documentation/classification amendment. `AUDIT_REVIEW.md` is preserved byte-for-byte as the independent review record. Raw inputs, source receipts, scientific numbers, identity and null-relation handling are unchanged.

INFERRED: Raw immutability is enforced by create-only writes and hash verification. `.gitattributes` disables newline conversion for this experiment so Git preserves the acquired bytes. `.venv`, caches, Python bytecode and temporary files are excluded from Git and kept inside the experiment.

## Stop condition

EXPECTED_FROM_MEMO: Independent review precedes preprocessing or modelling. This audit does not redesign the frozen source selection. Censor handling, unresolved representations and source metadata must receive explicit review before any later scientific processing.
