# V2 Final Interpretation

## 1. Intended Experiment vs. Protocol Deviation

The v2 execution intended to compare the performance of four specific configurations on the primary quantitative cohort:
- R1 descriptors + Ridge
- R2 Morgan + Ridge
- R1 descriptors + RF
- R2 Morgan + RF

However, due to the production routing expression in the execution script (`src/execute_v2.py`):
```python
X_tr = X_r1[train_mask] if 'r1' in p_id else X_r2[train_mask]
```
where `p_id` was defined strictly in uppercase (e.g., `'P1'`, `'P3'`), the expression `'r1' in p_id` always evaluated to `False`. 

Because of this logical flaw, all candidates actually received R2 Morgan fingerprints. Therefore, the intended representation-comparison/model-selection experiment is **PROTOCOL_COMPROMISED**.

## 2. Status of the Protected Artifact

Despite the routing failure, the protected 149-compound prediction artifact remains a genuine one-time scaffold-held-out evaluation of the actually executed Morgan Random Forest.

- Primary numerical performance may be reported only as performance of that executed Morgan RF, not as evidence that R1 descriptors won.
- Applicability-domain results refer to ECFP4 similarity against the correct 582-member CV pool.
- HLM–HH results are unaffected.
- No v2 rerun will be performed.
- Any future representation comparison will be a new prospective experiment.

## 3. Provenance Summary

We must explicitly distinguish:

**VALID_PROTECTED_MODEL_PERFORMANCE**
The numerical metrics and predictions themselves reflect a perfectly valid execution and evaluation of a Morgan + Random Forest model.

from 

**INVALID_INTENDED_MODEL_SELECTION_PROVENANCE**
The recorded metadata claiming that the winning representation used R1 descriptors is entirely false.

## 4. Bootstrap CI Provenance

An attempt was made to verify whether the originally reported scaffold-bootstrap CI `[0.022749898278188855, 0.09452515112530031]` matches the originally specified `B=10,000, seed=0` scaffold-cluster recovery on the true 84-scaffold holdout. Mathematical equivalence could not be provably established (due to superseded cohort extraction anomalies in earlier reports). 

As such, the CI provenance is marked **unresolved**.

V2_RECORD_SEALED_WITH_PROTOCOL_DEVIATION
