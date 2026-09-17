# Paired HLM vs HH Secondary Analysis Results

## 1. Overview
This document summarizes the paired assay-comparison analysis between Human Liver Microsome (HLM) clearance and Human Hepatocyte (HH) clearance. 
- **Total Exact Overlap N:** 187 paired molecules
- **HLM Source:** `CHEMBL3301370`
- **HH Source:** `CHEMBL3301372`

**Important Intepretation Constraints:**
*RESULT vs. BIOLOGICAL INTERPRETATION*
- **Result:** We observe a moderate rank correlation (~0.49) and a 68% exact-category censoring agreement between the two assays. There are no extreme (BELOW vs ABOVE) disagreements.
- **Biological Interpretation:** The data suggests that compounds generally preserve their relative clearance ranking between HLM and HH systems, and censoring classes correspond fairly consistently. However, these results DO NOT imply that HLM and HH are numerically interchangeable, nor do they establish that either assay perfectly predicts in-vivo human clearance. HLM and intact hepatocytes capture overlapping but distinct aspects of hepatic disposition.

## 2. Paired Censoring-Class Cross-Tab (N = 187)

| HLM \ HH | BELOW | IN-RANGE | ABOVE |
| :--- | :--- | :--- | :--- |
| **BELOW** | 31 | 20 | 0 |
| **IN-RANGE** | 26 | 96 | 5 |
| **ABOVE** | 0 | 8 | 1 |

### Descriptive Agreement Stats:
- **Exact-category agreement:** 128 (68.45%)
- **Adjacent-category disagreement:** 59 (31.55%)
- **Non-adjacent disagreement (BELOW ↔ ABOVE):** 0 (0.0%)

## 3. Primary Paired Continuous Analysis
This analysis compares the doubly IN-RANGE continuous values.

- **Doubly IN-RANGE N:** 96
- **Spearman Rho:** 0.4864
- **Descriptive p-value:** 5.04e-07

*Note: The raw ratio, fold-change, and Bland-Altman statistics are deliberately omitted to avoid presenting the assays as numerically interchangeable.*

## 4. Sensitivity Analysis (S1): Ambiguous HLM Null-at-3 Records
We assessed the impact of the 13 previously identified HLM observations that lacked a relation but recorded exactly "3.0".
- **Ambiguous records found in this paired cohort:** 2
- **Doubly IN-RANGE N (S1):** 94
- **Spearman Rho (S1):** 0.5045
- **Descriptive p-value (S1):** 2.16e-07

The removal of these 2 ambiguous records caused only a nominal increase in rank correlation, confirming the primary finding is robust to this specific historical data artifact.
