# V2 Runner Adversarial Review V3

## 1. Code Identity

- **src/execute_v2.py SHA-256**: `E829B94A408D04FE1CA85BF915604A34130600A7F85EF48521082B50BBB721AB`
- **tests/test_execute_v2.py SHA-256**: `312341C1FB41BA1B477566C3B9355255AF3C901A1E04D160954D125D701AB99C`
- **SAP SHA-256**: `CBB86E329FC889DBBF1832D3C83EAA3A909D9846A8B88E85A6EE341D6B572BBA`
- **Current HEAD**: `c67148c62d814357034d4c33db7967c88354f874`
- **Tag dmpk-v2-execution-ready**: Does NOT exist.

## 2. Test Execution

Independent re-execution via `run.py test`:
- **Total Tests Run**: 124
- **Passed**: 124
- **Failed**: 0
- **Skipped**: 0
- **Warnings**: 0

The official synthetic pathways are fully exercised and verified dynamically.

## 3. Regression-Check of Execution Protections

- **Canonical Authoritative State**: Fixed. `Path(__file__).resolve().parent.parent / "state" / "v2_execution_state.json"` anchors the path securely. Direct runner invocation, cwd, UUID, and `run_dir` overrides cannot bypass the root lock.
- **Concurrency**: Properly protected via `touch(exist_ok=False)`.
- **Pre-Access Durability**: The configuration `manifest` is generated and saved locally before holdout access commences.
- **State-Machine Logic**: Post-access failures permanently block reruns without manual intervention.

## 4. Synthetic/Mock Isolation Audit

The presence of `MockPredictor`, literal `94`/`96`, and `synthetic_data` variables are rigorously isolated from the official entry points.
- `MockPredictor` is conditionally instantiated exclusively if `dry_run = True`. 
- `synthetic_data` relies on explicit injection and defaults to `None`. No environment variables or exceptions expose it during production runs. 
- Real execution fetches the real data `get_cohorts()` dynamically, completely bypassing mock matrices.
- The `94` and `96` are only used for synthetic stubs or as `assert p_n == 94` to strictly validate correctly derived source data counts. They never populate real reporting unless the derivation matches structurally.

## 5 & 6. Primary / Secondary Regression Check

All prior validations remain valid:
- **Primary Holdout**: Partition 149/582 remains immutable.
- **Selection**: Follows pure fold-local mean log10-MAE with tiebreaker rules (0.001 -> Ridge -> R1 -> stronger reg -> P1-P4 list).
- **Tail / Sensitivity**: P1-P4 restricted, left/right C/U predictions pair inside fold. Ambiguous (N=13) handled perfectly as exact `3` (Sensitivity A) or censored (Sensitivity B) without triggering refits in Sens B. 

## 7. HLM–HH Source Implementation Audit

The `HLM_HH` logic reads `CHEMBL3301370_rows.csv` and `CHEMBL3301372_rows.csv` alongside the mapped IDs from `PAIRED_HUMAN_COHORT.csv`. 
- **Matching & Counts**: Calculates identical 1-to-1 relations checking null fields strictly. `INTERIOR_OBSERVED` pairs yield precisely `N=94`. `BOUNDARY_AMBIGUOUS` (exactly 3/150 in HLM) yields `N=2` pairs which are merged sequentially into the sensitivity logic yielding exactly `N=96`. 
- **Calculation Accuracy**: Uses `scipy.stats.spearmanr` dynamically across the quantitative matched values.
- **Rules Met**: No prediction, no ML fit, no ratio, no subtraction, no scaling, no IVIVE.

## 8. Biogen Source Implementation Audit

The runner constructs `B1` and `B2` counts from `Biogen_rows.csv` and structurally replicates the models independently. However, a rigorous textual review of the SAP reveals a severe documentation gap. 

### Finding 1: Unspecified B1/B2 Selection Relationship (BLOCKER)
- **Exact Location**: `src/execute_v2.py:464` and `STATISTICAL_ANALYSIS_PREREGISTRATION.md`
- **Expected Behaviour**: The SAP must explicitly state whether B2 performs independent hyperparameter and pipeline selection (an independent P1-P4 loop) or if B2 evaluates the specific model selected by B1. 
- **Observed Behaviour**: The implementation runs the P1-P4 loop independently for B2. The SAP says "Both are always reported... Implement the frozen P1-P4 procedure within Biogen". The SAP wording does *not* explicitly specify the selection relationship between B1 and B2 variants. 
- **Consequence**: The implementation assumes independent selection, which is scientifically material but lacks explicit SAP textual authorization. Deciding this retrospectively violates the freeze.
- **Minimal Correction**: The protocol must be explicitly amended/clarified before this execution runner can be considered faithful to a complete preregistration.

## 9. Authoritative-State Paths
Test fixtures explicitly demonstrate identical canonical path derivations across disjoint `cwd` combinations and root/uuid executions. 

## 10 & 11. Stubs and Forensic Search
- Strings like `Mock`, `TODO`, `pass`, etc. have been entirely neutralized or removed. No pseudo-metrics are fed into actual completion manifests. 
- `run_dir` traces prove no actual predictive runs or AstraZeneca/Biogen `.fit()` executions occurred.

## 12. Execution-Readiness Disposition

| Previously blocked issue | Current status | Evidence |
|--------------------------|----------------|----------|
| Ledger scope / canonical path | FIXED | Anchored dynamically via `Path(__file__)`. |
| Pre-access durability | FIXED | `selection_manifest.json` persists early. |
| Tail implementation | FIXED | Concordance correctly restricted by fold/pipeline. |
| Sensitivity implementation | FIXED | Sens A/B follow target handling rules cleanly. |
| Tie-break parameter handling | FIXED | Proper feature mapping applied (`alpha` vs `max_features`). |
| HLM–HH real computation | FIXED | Directly calculates `scipy.stats.spearmanr` off loaded fields. |
| Biogen real workflow | BLOCKED | SAP lacks specification for the B2 model-selection relationship. |

RUNNER_AUDIT_BLOCKED
