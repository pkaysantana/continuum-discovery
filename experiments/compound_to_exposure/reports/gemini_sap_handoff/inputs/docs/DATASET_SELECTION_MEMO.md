# DMPK Clearance Dataset Selection & Scientific Specification

This document defines the scientific specification and dataset selection rules for the first phase of the DMPK compound-to-exposure project, focusing on prediction and failure analysis.

## Dataset Selection & Processing
1. **Primary Science Data**: We will use direct ChEMBL data for the primary scientific analysis.
2. **Benchmark Reproduction**: The TDC (Therapeutics Data Commons) datasets will be used strictly for benchmark reproduction. 
3. **Exclusions**: The mixed-species TDC hepatocyte set is explicitly excluded from the analysis.
4. **Replication Strategy**: The Biogen dataset will be utilized as a within-dataset replication rather than treated as a naive transfer set.
5. **Data Handling**: Explicit censoring and UNKNOWN handling rules must be applied rigorously across all datasets.
6. **Performance Interpretation**: The interpretation of the two-fold repeatability band has been corrected and will serve as the realistic baseline for model performance expectations.

## HLM–HH Paired Analysis (v1 Rule)
For the v1 analysis, the paired Human Liver Microsome (HLM) and Human Hepatocyte (HH) analysis will remain secondary and descriptive, employing no physiological scaling.

On compounds measured in both assays, we will examine:
- Rank-order agreement between HLM and HH using Spearman correlation.
- Whether compounds ranked as high/low clearance in one assay behave similarly in the other.
- Assay-specific model residuals on the shared compounds.
- Whether molecular characteristics associated with large prediction errors differ between HLM and HH.

### Exclusions & Future Work
- **No Raw Ratios**: We will not compute a raw HLM:HH clearance ratio because the native units differ.
- **Deferred Physiological Scaling**: Physiologically scaled HLM:HH ratios (IVIVE) are deferred to a later, separately preregistered analysis that will require explicit scaling-factor sources and sensitivity analysis. 

This approach ensures the initial project remains sharply focused on prediction and failure analysis without letting IVIVE/scaling conflate the scope.
