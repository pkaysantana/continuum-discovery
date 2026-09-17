# TDC Benchmark Results (Clearance_Microsome_AZ)

## Overview
This document contains the fully deterministic execution results of the historical `Clearance_Microsome_AZ` benchmark from PyTDC 1.1.15. 

**IMPORTANT NOTICES:**
1. **Data Provenance:** TDC benchmark labels are used **exactly as distributed** for historical benchmark comparability. Bare values at `3` and `150` do not establish that the corresponding source observations were exact uncensored equality measurements.
2. **Not External Validation:** TDC substantially overlaps the direct AstraZeneca HLM source and is **not independent external validation**. The results here should only be used to calibrate historical literature comparisons.

## Evaluation Methodology
- **Train (N=771):** Used exclusively for calculating preprocessing statistics and final estimator fitting.
- **Valid (N=110):** Used exclusively to calculate MAE for hyperparameter selection.
- **Test (N=221):** Used exclusively for the single final benchmark evaluation.
- **Train+Valid Refit:** `NO`. Final fit was on Train only.
- **Test Used for Model Selection:** `NO`.

## Selected Hyperparameters
*   **Ridge (Descriptors):** `alpha = 0.1`
*   **Ridge (Morgan):** `alpha = 10.0`
*   **RandomForestRegressor (Descriptors):** `max_depth = 10`
*   **RandomForestRegressor (Morgan):** `max_depth = None`

## Benchmark Results (Test N=221)
*Headline metric: Spearman rho*

| Cell | Spearman | MAE | RMSE | R² |
| :--- | :--- | :--- | :--- | :--- |
| Mean Baseline | `NaN` | 35.352 | 43.774 | -0.032 |
| Median Baseline | `NaN` | 26.167 | 45.251 | -0.103 |
| Ridge (Descriptors) | 0.146 | 34.697 | 43.173 | -0.004 |
| Ridge (Morgan) | 0.499 | 28.881 | 38.852 | 0.187 |
| Random Forest (Descriptors) | 0.266 | 31.729 | 42.199 | 0.041 |
| Random Forest (Morgan) | 0.371 | 29.553 | 40.535 | 0.115 |

*(Note: Baseline Spearman is formally undefined/NaN because the baseline predictions have zero variance).*

## Descriptive Comparison with Primary HLM
*Note: Numerical performance differences are NOT directly attributable to model quality because the split design differs, TDC strips censor qualifiers, TDC includes the full distributed label range, the evaluation metric differs (Spearman vs 2-fold regression accuracy), and the datasets heavily overlap.*

**Broad Qualitative Patterns:**
- **Morgan vs Descriptors:** Just like in the primary HLM track, Morgan fingerprints systematically outperform the 7 RDKit physicochemical descriptors across both model families.
- **Ridge vs Random Forest:** For Morgan representations, Ridge heavily outperforms Random Forest, which was also the pattern observed in the primary HLM predictions. For descriptors, Random Forest achieves better rank-ordering (Spearman) than Ridge, which struggled on the non-linear descriptor distributions.
- **Predictive Signal:** The maximum Spearman achieved here is ~0.5 (Ridge_Morgan), which aligns with the modest-but-real predictive signal observed in the primary track's quantitative assessments.

## Integrity Checks
- Deterministic rerun yielded exactly identical hyperparameters, predictions, and metrics (tolerance < 1e-12).
- PyTDC Spearman identically matched the independent SciPy recomputation.
- Primary HLM files were absolutely unmodified.
