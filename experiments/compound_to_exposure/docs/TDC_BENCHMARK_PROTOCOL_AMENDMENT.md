# TDC Benchmark Protocol Amendment

**Context:** This protocol amendment was written and frozen **BEFORE** any TDC predictive fitting or performance inspection had occurred.

## Motivation and Scope
The original `MODELLING_PREREGISTRATION.md` specified that hyperparameter selection should be performed using a 3-fold scaffold-aware inner CV within the training data.

However, an inspection of the frozen PyTDC 1.1.15 source logic revealed a direct conflict with this rule for the historical TDC benchmark track. PyTDC explicitly defines a benchmark split containing a distinct `Valid` subset, and preserving inner CV on the `Train` subset would abandon the official PyTDC validation semantics. 

To maximize benchmark reproduction fidelity, the TDC tuning rule is amended prospectively here.

**IMPORTANT:** This amendment changes **NOTHING** about the primary HLM science track, primary N=744, classifier N=1102, primary scaffold OOF folds, S1 sensitivity analysis, U6 characterisation, censoring policy, primary results, HLM-HH, or Biogen replication. It applies **only** to the separate TDC historical benchmark track.

## 1. PyTDC-Explicit Facts
The following details are explicitly defined by the PyTDC 1.1.15 distribution:
- **Split algorithm:** Deterministic scaffold grouping based on `MurckoScaffold`, ordered by scaffold sizes and randomly shuffled.
- **Random seed:** `42`
- **Subset sizes:** `Train N = 771`, `Valid N = 110`, `Test N = 221`.
- **Test evaluation:** The benchmark expects predictions on the `Test` subset.
- **Metric:** `Spearman` correlation coefficient.

PyTDC **does not** explicitly prescribe whether the final model scored on the test set should be fitted on `Train` only, or refitted on `Train + Valid` after hyperparameter tuning.

## 2. Project-Specific Prospective Convention
To resolve the ambiguity without inventing an official PyTDC rule, we prospectively freeze the following **project-specific convention** for TDC modelling:

**Train-only final fitting**
- `Train` is the **only** subset used to fit model parameters and preprocessing statistics (scaling, variance filtering).
- `Valid` is used **solely** to calculate validation MAE for hyperparameter selection. Valid must never enter preprocessing, feature selection, or final model fitting.
- `Test` remains untouched until the single final benchmark evaluation. 
- There will be **no** `Train + Valid` refitting.

**Rationale for this choice:**
1. PyTDC source does not resolve final-refit semantics.
2. The choice is deliberately frozen before any performance observation.
3. Train-only is a conservative interpretation that strictly preserves the distinct semantic roles of each partition.
4. It avoids introducing an extra Train+Valid refitting convention that PyTDC itself does not mandate.

## 3. Revised Hyperparameter Selection (TDC ONLY)

The previous TDC-specific requirement for 3-fold inner CV is **superseded**.

For each benchmark cell, the candidate hyperparameter yielding the lowest MAE on the `Valid` subset will be selected. 

The hyperparameter candidates and grids remain completely unchanged from the original preregistration. The already-frozen numerical tie tolerance and Ridge tie-break rule still apply.

### Ridge
Candidates: `alpha ∈ {0.1, 1.0, 10.0}`
For each `alpha`:
- Fit preprocessing on `Train` only.
- Fit Ridge on `Train` only.
- Transform `Valid` using `Train`-fitted preprocessing only.
- Calculate MAE on `Valid`.

After selecting the best `alpha`, instantiate a fresh model using the selected `alpha` and fit it on the full 771-row `Train` subset **only**.

### Random Forest
Candidates: `max_depth ∈ {10, None}`
For each `max_depth`:
- Fit Random Forest on `Train` only.
- Evaluate MAE on `Valid`.

After selecting the best `max_depth`, instantiate a fresh estimator with the selected `max_depth` and fit it on the full 771-row `Train` subset **only**.

### Baselines
Mean and median baselines must also obey the Train-only semantics:
- Calculate the mean/median from the 771-row `Train` subset **only**.
- Use those fixed Train statistics to predict `Test`.
- The `Valid` subset must **not** be folded into the baseline statistic.
