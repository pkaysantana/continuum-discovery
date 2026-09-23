# V2 Recovered Secondary Provenance Check

## 1. Tanimoto Provenance Audit

**Discrepancy Analysis:**
The previously recovered holdout-bin counts (0/22/21/30/76) differed from the frozen pre-execution ECFP4 counts (1/28/24/37/59) due to the use of an incorrect reference population in the recovery code. 

**Exact Cause:**
The initial recovery script calculated the nearest-training similarity against all 852 cross-validation (CV) compounds present in `master_partition.csv` (which includes out-of-bounds "above/below" and "ambiguous" targets). However, the frozen pre-execution definition strictly required comparing each of the 149 primary holdout compounds against ONLY the 582 *primary* CV compounds (the `interior_731` subset). 

**Verification:**
When independently recalculating the nearest-training similarity using exactly the frozen definition (Morgan radius 2, 2048 binary bits, `useChirality=False`, restricted to the 582 primary CV references), the similarities match the `ECFP4_TANIMOTO_PREFREEZE_CHECK` evidence molecule-by-molecule perfectly.

*Correction Action:* The recovered report's Tanimoto bins should reflect the frozen pre-execution ECFP4 counts (1/28/24/37/59). No execution artifacts require revision.

## 2. HLM-HH Provenance Audit

**Analysis of `=` Labels:**
An audit of `PAIRED_HUMAN_COHORT.csv` against the immutable raw ChEMBL records (`CHEMBL3301370_activities_00000.json`) reveals that the `=` labels are an internal normalized representation. 

**Exact Cause:**
In the raw ChEMBL data, these exact-value measurements have a `NULL` (or `None`) `standard_relation`. The data pipeline mapped these `NULL` relations to `=` in the interim cohort file. Therefore, ChEMBL did not explicitly supply `=` for these records; they were simply unqualified values.

**Relabelling & Re-verification:**
The qualifier contingency labels should be described as `unqualified/NULL` rather than `=`.
The Spearman correlation calculations for N=94 primary and N=96 sensitivity remain numerically unchanged, as the calculation simply selects records with `NULL` relations in the source data.

### Corrected Qualifier Contingency Table (Provenance-Accurate)
```
standard_relation_hh    <    unqualified/NULL  >  All
standard_relation_hlm                 
<                      31                  20  0   51
unqualified/NULL       26                  96  5  127
>                       0                   8  1    9
All                    57                 124  6  187
```

---
**Status:** SECONDARY_RECOVERY_REQUIRES_CORRECTION
