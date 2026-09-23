# Independent adversarial review of whole-cohort structure integrity

**Review date:** 2026-09-23  
**Scope:** CHEMBL3301370 frozen repository snapshot; no model fitting or prediction, no protected-v2 access, and no data/protocol/artifact modification.  
**Central result:** the repository evidence independently confirms the activity-ID/molecule-ID/structure invariant and the per-row structure/target/scaffold alignment of the 731-row primary model cohort. Several broader statements in `WHOLE_COHORT_STRUCTURE_INTEGRITY_AUDIT.md` are nevertheless overstated or unsupported.

## Evidence and independent method

I used a minimal implementation that did not import or call either `whole_cohort_structure_integrity.py`. It loaded the two earliest repository raw pages, keyed every record by `activity_id`, parsed each SMILES independently with RDKit 2025.03.6, compared canonical isomeric graphs, independently calculated the 12 frozen descriptors, generated legacy 2048-bit radius-2 Morgan fingerprints, and independently reproduced the largest-fragment Bemis-Murcko rule.

The earliest repository versions of both raw pages and the interim table were introduced together by commit `13715550adad0a628e92da6cf34568000ddbc797`. The frozen partition was introduced by `0e4248ff779d74b4a54abbea608c80b6897f33ff`.

| Input | SHA-256 |
|---|---|
| `data/raw/chembl/CHEMBL3301370_activities_00000.json` | `657618e353b9795fd7fabb1a4086d7b936709059bbfdcbe689b0f87309e16d43` |
| `data/raw/chembl/CHEMBL3301370_activities_01000.json` | `df8720b582563b8d04c1029aedb5fc5ced7614d3c190e912ac4bab67140ac46e` |
| `data/interim/CHEMBL3301370_rows.csv` | `fc1ea6fa15736449a75f578b2ff3e97661b8079d087aae000ed3ed508223ab37` |
| `splits/master_partition.csv` | `971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a` |

Paths in this report are relative to `experiments/compound_to_exposure/` unless stated otherwise.

## Claim table

| Claim | Independently reproduced? | Evidence | Caveat |
|---|---|---|---|
| All 1,102 raw activity IDs map to the correct molecule ID and graph | Yes | 1,102 unique activity IDs and 1,102 unique molecule IDs; 0 ID mismatches, 0 graph mismatches, 0 missing/invalid structures, 0 unresolved records | This establishes the frozen repository snapshot, not present-day ChEMBL identity |
| Raw to interim mapping | Yes | Keyed by `activity_id`; molecule ID, parent ID, raw SMILES, relation, and value all have 0 mismatches | None for this snapshot |
| Interim to `get_cohorts()` and frozen split | Yes | Both contain all 1,102 keyed records; 0 ID/graph mismatches and 0 unresolved records | `get_cohorts()` reads the interim table rather than an independent source |
| 731-row X/y/ID/scaffold alignment | Yes | Per-key reconstruction of `X_r1[i]`, `X_r2[i]`, `y[i]`, `chembl_id[i]`, and `scaffold_key[i]`: 0 errors | `execute_v2.py` relies on a left merge preserving order; current inputs satisfy that assumption |
| 582 CV and 149 holdout alignment | Yes | 0 per-field or any-row errors in both subsets | None for current frozen inputs |
| All 14 named descriptors have independent stored comparators | No | Only seven have whole-cohort persisted columns | Seven others were only recomputed successfully |
| “100% exact numerical agreement” for stored descriptors | Partly | All seven persisted descriptors agree for 1,102 rows within `1e-12` | Four floating descriptors are not bit-for-bit equal after CSV round-trip; the prior script used `<1e-4` but called it “exact” |
| “Structure to ECFP4, N=1,102, PASS” as fingerprint matches | No | Fingerprints can be generated for all 1,102; model matrix rebuilt for 731 | No persisted fingerprint vectors exist for independent comparison |
| All 731 model fingerprints came from the correct structures | Yes | Every rebuilt `X_r2[i]` exactly equals an independent fingerprint of the raw structure keyed by that row's activity ID | Fingerprints ignore chirality by frozen design |
| 1,102 scaffold keys reproduce | Yes | 1,102/1,102 exact key agreement | Reproducibility alone is not a leakage test |
| No scaffold leakage | Yes | No scaffold crosses CV/holdout; no CV scaffold crosses folds; protected holdout has 84 scaffold groups | Tested independently from key reproducibility |
| Two suspicious compounds were absent from model corruption | Yes | Raw, interim, cohort, descriptor/fingerprint input, and scaffold all agree for both compounds | The claimed exact reporting-script mechanism is not fully reproduced |
| Security history was adequately scanned | No, prior scope corrected here | All 143 commits reachable from `origin/dmpk-v2-execution`, plus the current audit commit (144 total), were scanned | One bearer-token-shaped log value requires credential-owner review; value is not reproduced here |

## 1. Central invariant

The two raw JSON pages contain 1,000 and 102 records. Across the combined 1,102 records, `activity_id`, `molecule_chembl_id`, and raw structure are each one-to-one in this dataset.

| Compared layer, keyed by activity ID | N | ID mismatches | Graph mismatches | Missing/invalid structures | Unresolved records |
|---|---:|---:|---:|---:|---:|
| Raw to interim | 1,102 | 0 | 0 | 0 | 0 |
| Raw to `get_cohorts()['full_df']` | 1,102 | 0 | 0 | 0 | 0 |
| Raw to `master_partition.csv` | 1,102 | 0 | 0 | 0 | 0 |

The raw-to-interim exact-string checks also found 0 mismatches for `parent_molecule_chembl_id`, `canonical_smiles`, `standard_relation`, and `standard_value`. Thus the central `activity_id -> molecule_chembl_id -> molecular graph` invariant is independently reproduced.

## 2. Model-input alignment

The actual path in `src/execute_v2.py` is potentially delicate:

1. `df_p = cohorts['interior_731']`.
2. `X_r1` and `X_r2` are generated from `df_p['canonical_smiles_rdkit']` before partition attachment.
3. A second reference to `cohorts['interior_731']` is left-merged with a partition table indexed by `chembl_id`.
4. `y`, CV/holdout masks, IDs, and scaffold columns are taken from the post-merge dataframe, while the pre-merge X arrays are sliced with those masks.

I did not accept dataframe order as proof. For every post-merge row I used its `activity_id` to retrieve the raw record, then independently regenerated both representations and target and compared them to the actual array position.

| Cohort | N | X_r1 errors | X_r2 errors | y errors | ID errors | Scaffold errors | Any-row errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| Interior | 731 | 0 | 0 | 0 | 0 | 0 | 0 |
| Primary CV | 582 | 0 | 0 | 0 | 0 | 0 | 0 |
| Protected holdout | 149 | 0 | 0 | 0 | 0 | 0 | 0 |

The matrices were `(731, 12)` and `(731, 2048)`. The merge was one-to-one in fact: both sides had unique `chembl_id`, all 731 keys resolved, cardinality remained 731, and the pre-/post-merge activity-ID sequence was identical. The 149-row persisted protected prediction artifact also contains exactly the expected 149 unique holdout IDs, with no missing or extra ID.

**Could a structure/target/scaffold row shift have occurred between cohort construction and model-input creation?** Not for the frozen inputs examined. The implementation creates X before and y/scaffold metadata after a merge, so an explicit order assertion or keyed reindex would be safer, but the independent per-key reconstruction rules out an actual shift in all 731 current rows.

The protected run manifest identifies execution commit `31693d204420fa547a96079ff11988058d133406`. Between that commit and HEAD, the four relevant source files differ only by changing a bare `except` to `except Exception` in `representations.py`; the data, partition, cohort logic, feature logic, and model alignment path are unchanged.

### Representation-routing defect, not a row shift

Gemini missed a separate implementation defect. `execute_v2.py` selects a matrix with expressions such as:

```python
X_tr = X_r1[train_mask] if 'r1' in p_id else X_r2[train_mask]
```

For uppercase IDs `P1`, `P2`, `P3`, and `P4`, `'r1' in p_id` is always false. Consequently all four completed primary candidates, including nominal descriptor pipelines P1 and P3, were routed to the correctly aligned 731-row fingerprint matrix. This does **not** attach any row to the wrong molecule, target, or scaffold, but it means existing v2 outputs labelled P1/P3 as descriptor models did not use `X_r1` as intended. This review does not fit or predict a model and does not assess downstream performance consequences.

## 3. Dangerous dataframe and array operations

| Location/operation | Risk | Independent result |
|---|---|---|
| `src/audit.py`: sorted raw pages, nested append, then CSV write | Accidental pagination or row loss | Page offsets are contiguous; IDs unique; interim exact fields match raw for all 1,102 |
| `src/dataset.py`: rename plus boolean masks | Positional filtering | Masks preserve source rows; independently derived memberships exactly equal all four project cohorts |
| `src/partition.py`: `groupby`, sorted group table, then scaffold-key `map`/`apply` to original dataframe | Group ordering could be mistaken for row ordering | Assignments return by key; 1,102 scaffold keys and every assignment reproduce |
| `src/execute_v2.py`: X built before `merge`, y built after `merge` | Principal row-shift risk | One-to-one merge and independent keyed X/y checks give 0 errors; no actual shift |
| `src/execute_v2.py`: CV/holdout boolean masks applied to arrays | Positional mask risk | Mask lengths and row keys agree; 582/149 independently verified |
| `src/execute_v2.py`: ambiguous X built before later merge | Same risk in sensitivity A/B | Current 13-row one-to-one merge preserves identical activity-ID order; completed primary result does not include those 13 |
| `src/execute_v2.py`: `if 'r1' in p_id` | Wrong representation selection | Confirmed defect; all P1-P4 route to R2, but R2 rows are correctly keyed |
| `src/prefreeze_evidence.py`: activity-ID sorting | Evidence ordering could be confused with model ordering | Used only for saved evidence; assignments are keyed by scaffold/activity |
| `src/tanimoto_prefreeze.py`: separately generated fingerprints | Positional recombination risk | Fingerprints are stored in an `activity_id` dictionary and reference pools retain keyed rows |

The committed whole-cohort audit implementation itself has a missed fatal indexing error: it creates `partition_map = df_partition.set_index('chembl_id')` and then accesses it with an `activity_id` at lines 366 and 444. It would raise `KeyError` before its advertised summary. It also hard-codes the final all-PASS table rather than deriving it, labels a `<1e-4` tolerance as exact, and never performs the reported 50-commit scan. The report's central numbers can be reproduced independently, but they cannot be treated as proven merely by that script's successful execution.

## 4. Four forensic compounds

All four occur once in the first raw page and are protected-holdout records.

| Compound | Activity ID / raw row | Formula; MolWt | Raw = interim = cohort graph? | Fingerprint input | Scaffold agreement |
|---|---|---|---|---|---|
| CHEMBL1778622 | `14765536` / 923 | C17H15F3O3S; 356.365 | Yes | Exact raw/interim structure; independent 2048-bit vector equals model row | `c1ccc(-c2ccccc2)cc1`, exact |
| CHEMBL1807823 | `14759804` / 240 | C22H29N3O3S2; 447.626 | Yes | Exact raw/interim structure; independent 2048-bit vector equals model row | `O=c1[nH]c2cccc(CCNCCSCCCNCCc3ccccc3)c2s1`, exact |
| CHEMBL2335901 | `14758997` / 231 | C27H28N6O; 452.562 | Yes | Exact raw/interim structure; independent 2048-bit vector equals model row | `O=C(NCc1ccc(Nc2ncc3cc(-c4ccncc4)ccc3n2)cc1)C1CCNCC1`, exact |
| CHEMBL20210 | `14765461` / 888 | C31H39FN4O7; 598.672 | Yes | Exact raw/interim structure; independent 2048-bit vector equals model row | `O=C(CNC(=O)c1ccon1)CC(Cc1ccccc1)C(=O)NCCC1CCNC1=O`, exact |

Descriptor vectors were independently calculated in the frozen order `MolWt, MolLogP, MolMR, TPSA, HBD, HBA, NumRotatableBonds, RingCount, NumAromaticRings, NumAliphaticRings, FractionCSP3, HeavyAtomCount`:

| Compound | Independent descriptor vector | Acidic / basic centres |
|---|---|---:|
| CHEMBL1778622 | `356.365, 4.9478, 86.4088, 46.53, 1, 3, 6, 2, 2, 0, 0.235294117647, 24` | 1 / 0 |
| CHEMBL1807823 | `447.626, 2.8738, 126.8977, 97.38, 5, 7, 13, 3, 3, 0, 0.409090909091, 30` | 0 / 2 |
| CHEMBL2335901 | `452.562, 4.6122, 134.6451, 91.83, 3, 6, 6, 5, 4, 1, 0.259259259259, 34` | 0 / 3 |
| CHEMBL20210 | `598.672, 2.82492, 153.9876, 156.7, 3, 8, 15, 3, 2, 1, 0.483870967742, 43` | 0 / 3 |

### What the reporting script actually establishes

`scratch/orig_extract_case_studies.py` is an untracked script later recovered from a Gemini transcript by `scratch/extract_orig.py`. Its API-properties block contains a real reporting bug:

- it calls `.only(['molecule_properties'])` even though `only` is variadic;
- the projected result omits `molecule_chembl_id`;
- it then accepts `chembl_data[0]` without verifying that result's identity.

That is an unverified positional extraction and can attach another response's ChEMBL property block during reporting. The corrected `scratch/extract_case_studies.py` requests the ID and searches the response for exact equality.

However, the preserved original source computes local R1 descriptors earlier from `smiles = df_full[df_full['chembl_id'] == cid].iloc[0]['canonical_smiles_rdkit']`, which is correctly keyed. It contains no off-by-one structure lookup. It is also not runnable against the current tree without correction: it references the nonexistent `data/processed/master_partition.csv`, expects prediction column `prediction` when the artifact uses `predicted`, and later references `canonical_smiles_rdkit` after merging only `chembl_id` and `standard_value`.

Therefore:

- the **model-pipeline** conclusion is firm: neither suspicious structure entered the model under the wrong ID;
- the wrong values exist only in post-hoc reporting/transcript artifacts, not raw/interim/model inputs;
- Gemini's specific statement that CHEMBL1778622 arose from an “off-by-one indexing offset” is not supported by the preserved script;
- the unverified API first-row bug explains how external property values could be attached incorrectly, but the repository does not preserve a coherent executable path that produces the wrong local R1 vectors in `step269_full.txt`;
- the wrong CHEMBL1807823 R1 vector is not the RDKit vector of the repository's CHEMBL81/raloxifene structure, so “corresponds to raloxifene” is not established for the complete vector merely because one reported molecular weight was 473.64.

The exact origin of those two bad rendered descriptor vectors is thus **reporting-layer but not fully forensically resolved to the claimed code mechanism**.

## 5. Descriptor claim

### A. Compared against persisted project values

Only seven named descriptors have whole-cohort comparator columns in `CHEMBL3301370_rows.csv`.

| Descriptor | Persisted column | N compared | Bit-for-bit float equality | Agreement within `1e-12` | Maximum absolute difference |
|---|---|---:|---:|---:|---:|
| MolWt | `molecular_weight` | 1,102 | 973 | 1,102 | `5.68e-14` |
| MolLogP | `clogp` | 1,102 | 954 | 1,102 | `1.78e-15` |
| TPSA | `tpsa` | 1,102 | 948 | 1,102 | `5.68e-14` |
| HBD | `hbd` | 1,102 | 1,102 | 1,102 | 0 |
| HBA | `hba` | 1,102 | 1,102 | 1,102 | 0 |
| NumRotatableBonds | `rotatable_bonds` | 1,102 | 1,102 | 1,102 | 0 |
| FractionCSP3 | `fraction_csp3` | 1,102 | 708 | 1,102 | `8.33e-17` |

These are persisted comparators, but they were originally generated from the same project structures and RDKit family, so they are not external chemical measurements. The tiny nonzero differences are CSV floating-point round-trip effects. “Numerically equal to tight tolerance” is accurate; “100% exact” is not if exact means binary equality.

### B. Recomputed successfully, without whole-cohort persisted comparators

`MolMR`, `RingCount`, `NumAromaticRings`, `NumAliphaticRings`, `HeavyAtomCount`, `AcidicCentres`, and `BasicCentres` have no independent whole-cohort columns or saved arrays against which to claim agreement. All were successfully recomputed for 1,102 valid structures, but that is a reproducibility check only.

All 13,224 cells in the independently recomputed 1,102 x 12 frozen R1 matrix were finite.

## 6. Fingerprint claim

| Quantity | N | Meaning |
|---|---:|---|
| Structures from which the frozen ECFP4-equivalent fingerprint can be deterministically generated | 1,102 | All parse; no generation failure |
| Fingerprints in the primary model matrix | 731 | `(731, 2048)`; all rows independently keyed to raw structures |
| Fingerprints actually used by the completed v2 primary modelling code | 731 | Because the representation-routing defect sends all P1-P4 through `X_r2` |
| Persisted fingerprint vectors independently comparable | 0 | No `.npy`, `.npz`, fingerprint table, or saved bit-vector artifact exists |

Persisted Tanimoto summaries and predictions are downstream results, not independent fingerprint objects. Accordingly, `Structure -> ECFP4, N=1,102, PASS` can mean only “generation succeeds for 1,102,” not “1,102 fingerprints match a separate persisted reference.” All 731 modelled fingerprints definitely came from the correct keyed structures.

## 7. Scaffold reproducibility and leakage

The independent largest-fragment rule (highest heavy-atom count, canonical-SMILES tie-break), non-chiral Murcko extraction, and `__ACYCLIC__` fallback produced exact agreement for all 1,102 frozen keys. There are 712 scaffold groups across the full cohort.

Leakage was tested separately:

- no scaffold group appears in both primary CV and protected holdout;
- no primary CV scaffold group appears in more than one CV fold;
- CV fold counts are 115, 120, 115, 117, and 115;
- the 582 primary CV compounds occupy 448 scaffold groups;
- the 149 protected compounds occupy exactly 84 holdout scaffold groups.

Thus both scaffold-key reproducibility and absence of scaffold leakage are independently confirmed.

## 8. Cohorts and censoring provenance

| Cohort | Independent definition from raw `standard_relation` and `standard_value` | N | ID/graph mismatches |
|---|---|---:|---:|
| Total | All raw records | 1,102 | 0 |
| `<3` | raw relation `<`, stored boundary value 3 | 274 | 0 |
| `>150` | raw relation `>`, stored boundary value 150 | 84 | 0 |
| NULL-at-3 ambiguous | raw relation is JSON null, value 3 | 13 | 0 |
| Strict interior | raw relation is JSON null, `3 < value < 150` | 731 | 0 |
| Primary CV | interior plus frozen `partition=cv` | 582 | 0 |
| Protected holdout | interior plus frozen `partition=holdout` | 149 | 0 |

All 1,102 records are assigned exactly once. The raw files contain 744 null `standard_relation` values: 13 at 3, 0 at 150, and 731 strict-interior values. The interim CSV represents those nulls as empty cells; `dataset.py` fills them with empty strings for filtering. This review preserved and checked the raw JSON-null provenance rather than treating null as a literal stored equals sign.

## 9. Current-ChEMBL limitation

No live comparison is required to determine what the model saw, and none is used in this verdict. Failure to compare with current ChEMBL:

- does **not** weaken internal alignment validity, which is fully determined by the frozen raw pages, interim data, split, and execution code;
- **does** weaken historical-versus-current provenance interpretation, including whether present-day ChEMBL has changed structures or property records associated with these IDs.

Therefore the limitation weakens the second issue only, not both.

## 10. Security scan with corrected scope

`origin/dmpk-v2-execution` has 143 reachable commits; the current audit branch adds one commit, for 144 reachable commits total. `origin/main` (86 commits) is an ancestor and is included in that traversal. I scanned all 144 commit trees, comprising 1,235 unique blobs, for provider-shaped API keys, bearer tokens, hard-coded credential/password assignments, `.env` secret files, private-key headers, personal-phone patterns, and private-address patterns. Values were never printed.

Findings are reported as path / introducing commit / category only:

| Path | Commit | Category |
|---|---|---|
| `FINAL_SWARM_RUN.log` | `7575fd27f1fc1a8c514a28333b8faa8d420537f7` | Bearer-token-shaped value in tracked log; active/placeholder status not established, so credential-owner review is required |
| `experiments/compound_to_exposure/manifests/downloads/tdc__clearance_hepatocyte_az.tab.json` | `13715550adad0a628e92da6cf34568000ddbc797` | Expired Harvard Dataverse/S3 pre-signed URL; AWS access-key identifier occurs only inside the signed URL |
| `experiments/compound_to_exposure/manifests/downloads/tdc__clearance_microsome_az.tab.json` | `13715550adad0a628e92da6cf34568000ddbc797` | Expired Harvard Dataverse/S3 pre-signed URL; AWS access-key identifier occurs only inside the signed URL |
| `experiments/compound_to_exposure/manifests/source_manifest.json` | `13715550adad0a628e92da6cf34568000ddbc797` | Same two expired pre-signed URLs |
| `experiments/compound_to_exposure/reports/PROVENANCE_TABLE.csv` | `13715550adad0a628e92da6cf34568000ddbc797` | Same two expired pre-signed URLs |

The two pre-signed URLs were signed at 2026-09-16 17:41:25/28 UTC with `X-Amz-Expires=3600`; they expired at 18:41:25/28 UTC that day. Their signatures are therefore no longer valid credentials. An AWS access-key ID is an identifier, not a secret by itself. No security token parameter is present.

No private-key material, known provider-shaped API key, hard-coded password/credential assignment, tracked `.env` file, confirmed personal phone number, or confirmed private physical address was found. A dummy phone value in `test_genuine_biodock.py` and simulated blockchain wallet-address labels in `agents/animoca/blockchain.py` and `test_animoca_spec.py` were false positives, not personal contact/address data. Gemini's blanket “0 active credentials” is too strong because the bearer-shaped log value was missed and was not tested for activity.

## 11. Repository hygiene

Commit `ba6242ee398063fd54fe307c1a24818c4f46461a` deliberately added both root-level and experiment-level audit/report paths.

- The two reports are byte-identical: SHA-256 `220045511b147556094e384698891f0473ef07a84a09fcc32c6d7df4b3502856`.
- The scripts are **not** byte-identical. The root script is an 18-line launcher wrapper (SHA-256 `aa77eb8b9932fdea736147e47627069f40a3b296615e65857e9a76dda3ee425c`); the experiment script is the 631-line implementation (SHA-256 `a931c43082b84960f212510fb62b5c548ac7e4f262bfcb353735f889e4bd8ace`). Calling them “equivalent copies” is inaccurate.

The experiment-specific paths should be canonical because the audit code, input data, frozen split, and related reports all belong to that experiment. A future cleanup could leave the root script as an explicit delegating launcher and replace the duplicate root report with a pointer. No cleanup is performed here.

## Explicit answers

**Are raw activity IDs correctly attached to molecular structures?** Yes. All 1,102 are correct; 0 ID mismatches, 0 graph mismatches, 0 missing/invalid structures, and 0 unresolved records.

**Are interim IDs correctly attached to structures?** Yes. All 1,102 match the raw keyed mapping.

**Are the 731 modelled structures correct?** Yes. Every R1 and R2 row independently matches the raw structure keyed by that model row's activity ID.

**Are X and y correctly aligned?** Yes, for all 731 rows, including 582 CV and 149 holdout. The nominal representation labels are affected by the separate `if 'r1' in p_id` routing defect, but there is no molecule/target row shift.

**Are scaffold keys correctly aligned?** Yes. All 1,102 keys reproduce, and every primary model row's key matches its raw structure.

**Are the two suspicious case-study structures only reporting-layer errors?** Yes with respect to scientific-data and model-input impact: the wrong structures/descriptors occur in post-hoc reporting artifacts only. However, Gemini's claimed exact causes are not fully supported: no preserved off-by-one lookup exists for CHEMBL1778622, and the demonstrable API first-result bug does not explain the wrong local R1 vectors by itself.

**Is there any evidence that existing model outputs were generated from the wrong molecular structure?** No. The completed protected prediction IDs, executed code snapshot, raw/interim structures, and independently rebuilt 731-row fingerprint matrix provide no evidence of wrong-structure model input. There is evidence that nominal P1/P3 representation labels are wrong because all candidates were routed to fingerprints.

**Are any claims in Gemini's report overstated even if the central integrity conclusion remains correct?** Yes: all-14 descriptor agreement, exact rather than tolerance-based agreement, 1,102 fingerprint “matches,” the case-study off-by-one/raloxifene narrative, successful provenance of the committed audit script, equivalence of the duplicate scripts, exhaustive dataframe coverage, and the security conclusion are overstated or unsupported.

INTEGRITY_AUDIT_INDEPENDENTLY_CONFIRMED
