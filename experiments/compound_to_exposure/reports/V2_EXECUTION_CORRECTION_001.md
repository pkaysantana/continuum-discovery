# V2 Execution Correction 001

## Incident Context
- Failed Runs: Execution 001 (PRE_ACCESS_EXECUTION_FAILURE_CONFIRMED)
- Tag: `dmpk-v2-execution-ready`
- Tag Commit: `2f8ce1b6eb88cb9df941d915b2435f755c845ebe`

## Observation
The v2 execution initially failed during startup due to a structural validation bug in `src/execute_v2.py`. The code asserted `len(partition_df[partition_df['partition']=='holdout']) == 149` on the full partition dataset (N=1,102), failing because the full partition contains 250 holdouts. The intended N=149 holdouts applies exclusively to the `interior_731` primary modeling cohort.

The scientific splits, derived cleanly from the frozen assignments, were correct. The execution state lock correctly aborted without writing predictive artifacts or transitioning stage state.

## Corrections Applied
1. **Committed Frozen Splits**: The frozen splits previously generated were committed directly to the repo as `splits/master_partition.csv`. 
   - SHA256: `971f78aa2a86b0a45c79d52dcb3fca64895289dd7c72b547797b273b067cb90a`
2. **Cohort-Aware Validation**: `src/execute_v2.py` was updated to properly separate the full-population assertions (N=1,102) from the primary-cohort assertions (N=731). Explicit verification that no primary scaffolds cross partition boundaries was added.
3. **Preflight Mode**: Added `preflight=True` to the execution pipeline (exposed via `src/run.py preflight`), explicitly validating constraints against the real-data artifacts without allowing the generation of predictive models, stage transition logs, or predictions.
4. **Validation Test Coverage**: Added rigorous test cases (`tests/test_validation_preflight.py`) guaranteeing failure against compromised splits and ensuring the `preflight` routine cannot be bypassed.

## Validation Status
- Cohort assertions: Pass
- Scaffold integrity assertions: Pass 
- Hash verification: Pass
- Preflight integrity: Pass
- Test suite: Pass

The implementation restores the original preregistered scientific integrity of `dmpk-v2-execution-ready` without mutating the data inputs or the scientific plan.
