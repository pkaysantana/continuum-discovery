# CHEMBL3301370 Depositor Provenance Resolution & Experimental-Error Context

**Document Type**: Provenance Resolution Memo  
**Date**: 2026-09-23  
**Target Assays**: `CHEMBL3301370` (Human Liver Microsomes, HLM $CL_{\text{int}}$), `CHEMBL3301371` (Rat Liver Microsomes), `CHEMBL3301372` (Human Hepatocytes)  
**Parent Document**: `CHEMBL3301361`  
**Status**: ARCHIVAL PROVENANCE RESOLVED — NO MODEL RE-EXECUTION  

---

## 1. Executive Summary & Chronology of the Unresolved Question

For historical analyses within the `compound_to_exposure` project, the semantic meaning of records in dataset `CHEMBL3301370` deposited with `standard_relation = NULL` presented an open curation question:
1. **Initial Curation State (2015 Deposition in ChEMBL 20)**:
   The dataset was deposited with 1,102 total activity records: 274 records with `standard_relation == '<'`, 84 records with `standard_relation == '>'`, and 744 records with `standard_relation = NULL`. Of the 744 `NULL` records, 731 had reported clearance values strictly between 3.0 and 150.0 $\mu\text{L/min/mg}$, and 13 records had reported clearance values of exactly 3.0 $\mu\text{L/min/mg}$. Zero records had an unqualified value of exactly 150.0 $\mu\text{L/min/mg}$.
2. **Prior Curation Uncertainty & Conservative Stance**:
   Because ChEMBL data guidelines do not enforce that `standard_relation = NULL` strictly equals `=`, previous project protocols (`docs/CENSORING_POLICY_MEMO.md`, `reports/DATA_AUDIT.md`) conservatively treated the 731 strict interior records ($3.0 < CL_{\text{int}} < 150.0$) as an inferred quantitative cohort, while flagging the 13 unqualified records at exactly 3.0 as **`BOUNDARY_AMBIGUOUS`**. This conservative separation was maintained because the linked 2010 method publication (*Rapid Commun. Mass Spectrom.* 2010, 24, 1730–1736) noted $<3$ as below the measurable range, creating ambiguity as to whether an unqualified 3 was an exact observation or an unflagged boundary qualifier.
3. **ChEMBL Helpdesk Inquiry (`chembl-help #890728`)**:
   In September 2026, ChEMBL support confirmed they were "fairly confident" that ordinary numeric records with `relation = NULL` represented exact in-range measurements. However, they lacked original deposition logs to verify exact-3 semantics, agreed that the 13 `NULL`-at-3 records should remain semantically unknown, and referred the project to the original AstraZeneca depositors, Mark Wenlock and Nicholas Tomkinson.
4. **First-Hand Depositor Resolution (23 September 2026)**:
   On 23 September 2026, original compiler and depositor Mark Wenlock provided direct, definitive clarification resolving the dynamic range, boundary semantics, and replicate-aggregation context of `CHEMBL3301370`.

---

## 2. New First-Hand Depositor Evidence

On 23 September 2026, Mark Wenlock provided the following written clarification regarding the ChEMBL HLM clearance record:

> “With respect to the dynamic range of the microsomal clearance assay in this CHEMBL data record, it ranged from 3 to 150 mL/min/g. Measurements without a qualifier (i.e., ‘<’ or ‘>’) would be the exact number – there may be instances where a compound had an exact measurement of 3 or 150 and these will be distinct from instances where a compound had a measurement of <3 or >150.
> 
> When Nick and I compiled this data record, we would have used inter-assay replicate-derived/aggregated results where available – I don’t think we shared the associated standard deviation, although experimental errors were talked about in the publication: J. Chem. Inf. Model. 2015, 55, 125−134. Relatedly, I can’t recall whether the assay in question was derived from multiple intra-assay replicates, but this information would be mentioned in the associated publication: Rapid Commun. Mass Spectrom. 2010, 24, 1730-1736.”

This statement provides **first-hand depositor evidence** directly from the author of the deposition. It is treated as primary archival evidence, adhering strictly to what was stated without extrapolation.

---

## 3. Evidence Hierarchy

To ground all future interpretations, the documentary evidence is structured in the following explicit hierarchy:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             EVIDENCE HIERARCHY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ Level A: Direct Depositor Clarification (Mark Wenlock, 23 Sep 2026)         │
│ • Primary archival evidence for CHEMBL3301370.                             │
│ • Dynamic range: 3 to 150 µL/min/mg.                                        │
│ • Unqualified records ('NULL') are exact quantitative measurements.          │
│ • Exact values of 3 or 150 are distinct from '<3' or '>150'.               │
│ • Inter-assay replicate-derived/aggregated results were used where available.│
│ • Deposited record does not include individual SDs or replicate counts.     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Level B: ChEMBL Helpdesk Support Resolution (Ticket #890728)                │
│ • Confirmed database curation history (added in ChEMBL 20, 2015).           │
│ • Stated high confidence that ordinary numeric NULL records mean exact (=). │
│ • Could not confirm exact-3 boundary semantics or replicate structure.      │
│ • Retained in full as archival history; superseded on exact-3 by Level A.   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Level C: 2015 Wenlock & Carlsson Publication (JCIM 2015, 55, 125–134)        │
│ • Broader AstraZeneca human microsomal assay family & QSAR context.         │
│ • Evaluated 5 pooled assays (dynamic range 3–300 µL/min/mg).                │
│ • 74% of compounds had single measurements; repeats used mean aggregation.  │
│ • For repeats (N ≥ 3), estimated typical SD ≈ 0.12 (95% CI 0.08–0.16).      │
│ • Heteroscedastic: argued stable above ~25 µL/min/mg (typical SD ≈ 0.11).   │
│ • Contextual reference only; strictly NOT row-level metadata for            │
│   CHEMBL3301370.                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ Level D: 2010 Temesi et al. Publication (RCM 2010, 24, 1730–1736)           │
│ • Analytical platform context (parent depletion kinetics, OATOF / MRM).     │
│ • Method comparison performed on cryopreserved human hepatocytes.           │
│ • Aliquots removed at 0, 5, 10, 15, 20, and 30 min.                         │
│ • Demonstrates instrument replication, not independent incubation repeats.  │
│ • Does not define the HLM 3–150 boundary (Level A governs this).            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Evaluation of Literature Context

#### Level C: J. Chem. Inf. Model. 2015, 55, 125–134 (Wenlock & Carlsson)
* **Broader Assay Context**: This publication analyzed human microsomal intrinsic clearance data pooled across five historical AstraZeneca assays.
* **Assay Range**: The assays reported values over $3 \text{ to } 300\text{ }\mu\text{L/min/mg}$. Measurements outside the dynamic range were excluded from that study's QSAR models.
* **Repeat Structure**: Where acceptable repeat measurements were available, the arithmetic mean was calculated.
* **Replication Distribution**: In that broader dataset, **74% of the human microsomal compounds had only a single measurement**, while 26% had two or more repeat determinations.
* **Experimental Error**: Among human microsomal $CL_{\text{int}}$ compounds with $\ge 3$ repeat measurements, the estimated typical repeat-measurement standard deviation was approximately **$0.12\text{ }\log_{10}\text{ units}$**, with **$0.08 \text{ to } 0.16$** reported as the 95% confidence interval for that estimate of typical SD. Observed molecule-level standard deviations ranged from approximately $0.01\text{ to } 0.67\text{ }\log_{10}\text{ units}$.
* **Heteroscedasticity & ~25 µL/min/mg Region**: The authors argued that, in the broader pooled AstraZeneca human microsomal dataset, variability was relatively stable above approximately $25\text{ }\mu\text{L/min/mg}$, with typical SD around $0.11$, whereas variability increased substantially toward the low-clearance end ($<25\text{ }\mu\text{L/min/mg}$). This $\ge 25\text{ }\mu\text{L/min/mg}$ threshold represents an externally motivated assay-family sensitivity threshold candidate for future v3A reconciliation, and is strictly not a validated CHEMBL3301370-specific reliability boundary.
* **QSAR Association**: Lower experimental uncertainty was demonstrably associated with superior QSAR predictive accuracy.
* **Scientific Boundary Constraint**:
  * **DO NOT** claim that `CHEMBL3301370` itself has a blanket row-level $\text{SD} = 0.12$ or imply that exact-3 records individually have $\text{SD} \ge 0.12$.
  * **DO NOT** assign $0.12$ to individual compounds in this project.
  * **DO NOT** assume every aggregate was specifically an arithmetic mean unless directly documented.
  * The 2015 paper serves as **assay-family and institutional context**, not row-level metadata for `CHEMBL3301370`.

#### Level D: Rapid Commun. Mass Spectrom. 2010, 24, 1730–1736 (Temesi et al.)
* **Analytical Architecture**: Describes an automated 96-well metabolic stability assay quantifying parent compound depletion over incubation timepoints (aliquots removed at $0, 5, 10, 15, 20,\text{ and } 30\text{ min}$), with intrinsic clearance calculated from the first-order elimination rate constant ($k_{\text{dep}}$).
* **Assay Tested**: The method comparison evaluated in the paper was conducted using **cryopreserved human hepatocytes** (corresponding to assay `CHEMBL3301372`), where values $<3$ were considered below the measurable range.
* **Instrument Comparison**: The paper evaluated sample analysis across Orthogonal Acceleration Time-of-Flight (OATOF) and Multiple Reaction Monitoring (MRM) triple-quadrupole mass spectrometers. Repeated analytical runs across different mass spectrometers reflect **instrumental/analytical precision**, not independent biological or metabolic incubation replicates.
* **Scientific Boundary Constraint**: This paper provides analytical workflow context, but does not establish independent intra-assay incubation replicates, nor does it define the HLM microsomal boundaries (which are established by Mark Wenlock's direct clarification).

---

## 4. Revised CHEMBL3301370 Measurement Semantics

### 4.1 Raw Database Invariance
The raw ChEMBL database field remains strictly untouched:
* **Raw Database Field**: `standard_relation = NULL`.
* **Prohibition**: We strictly **refuse** to mutate or rewrite the raw data column from `NULL` to `=`.

### 4.2 Updated Derived Scientific Semantics
Based on Level A depositor evidence, the derived scientific semantics across the 1,102 activity records of `CHEMBL3301370` are resolved as follows:

| Database Condition | Numeric Value ($CL_{\text{int}}$, $\mu\text{L/min/mg}$) | Previous Working Label | Revised Scientific Semantic Label | Semantic Status |
| :--- | :--- | :--- | :--- | :--- |
| `standard_relation == '<'` | $3.0$ | `LEFT_CENSORED` | **`LEFT_CENSORED`** | Left-censored at dynamic lower bound |
| `standard_relation == '>'` | $150.0$ | `RIGHT_CENSORED` | **`RIGHT_CENSORED`** | Right-censored at dynamic upper bound |
| `standard_relation IS NULL` | $3.0 < \text{value} < 150.0$ | `INFERRED_QUANTITATIVE` / `STRICT_INTERIOR` | **`EXACT_QUANTITATIVE`** | Exact uncensored quantitative measurement |
| `standard_relation IS NULL` | $\text{value} == 3.0$ | `BOUNDARY_AMBIGUOUS` | **`EXACT_QUANTITATIVE_BOUNDARY_LOW`** | Exact uncensored quantitative measurement at lower bound |
| `standard_relation IS NULL` | $\text{value} == 150.0$ | `BOUNDARY_AMBIGUOUS` | **`EXACT_QUANTITATIVE_BOUNDARY_HIGH`** | Exact uncensored quantitative measurement at upper bound |

### 4.3 Verified Repository Cohort Counts
Automated verification against `experiments/compound_to_exposure/data/interim/CHEMBL3301370_rows.csv` confirms exact alignment with deposited counts:

$$\begin{aligned}
\text{Total Activity Records} &= 1,102 \\
\text{Left-Censored } (<3.0) &= 274 \\
\text{Right-Censored } (>150.0) &= 84 \\
\text{Unqualified Strict Interior } (3.0 < CL_{\text{int}} < 150.0) &= 731 \\
\text{Unqualified Exact Boundary Value } (CL_{\text{int}} == 3.0) &= 13 \\
\text{Unqualified Exact Boundary Value } (CL_{\text{int}} == 150.0) &= 0 \\
\hline
\mathbf{Total\ Exact\ Quantitative\ Observations\ (731 + 13 + 0)} &= \mathbf{744} \\
\mathbf{Unresolved\ /\ Ambiguous\ Relation\ Records} &= \mathbf{0}
\end{aligned}$$

**Superseding Notice**: The previous provisional label `BOUNDARY_AMBIGUOUS` applied to the 13 unqualified value-3 observations is **formally superseded** by first-hand depositor clarification. These 13 records represent true uncensored measurements that yielded an exact clearance of 3.0 $\mu\text{L/min/mg}$.

---

## 5. Replicate Provenance & Measurement Precision

### 5.1 Canonical Formulation of Record Provenance
To ensure rigorous documentary integrity across all manuscripts and reports, any historical statement characterizing ChEMBL rows as "individual single-run measurements" is superseded by the following canonical wording:

> **“Each deposited row represents a compound-level HLM $CL_{\text{int}}$ result. According to original depositor Mark Wenlock, inter-assay replicate-derived/aggregated results were used where available. The deposited record does not provide row-level replicate counts or associated standard deviations, so individual records cannot be classified as single measurements versus replicate-derived aggregates from the public data alone.”**

### 5.2 Decoupling Exact Semantics from Measurement Precision
It is essential to maintain a strict scientific distinction between **exact measurement semantics** and **measurement precision**:
1. **Exact Semantics**: An unqualified record with `standard_relation IS NULL` and `standard_value = 3.0` is now proven to be **uncensored** (an exact observation of 3.0, distinct from a run truncated at $<3.0$).
2. **Measurement Precision**: Establishing that an observation is uncensored does **not** imply that it possesses zero or negligible experimental error:
   > “Exact boundary observations remain subject to experimental uncertainty. In the broader AstraZeneca human microsomal CLint dataset, the estimated typical repeat-measurement SD was approximately 0.12 log10 units (95% CI for that estimate: 0.08–0.16), with variability increasing toward the low-clearance end. These values provide assay-family context and must not be assigned as row-specific SDs to CHEMBL3301370.”
   
   None of these quantities are row-specific uncertainty estimates for `CHEMBL3301370`, and exact-3 records must not be stated or implied to individually have $\text{SD} \ge 0.12$.

---

## 6. Consequences for Historical Analytical Programs

### 6.1 The Sealed v2 Reanalysis Protocol
* **Status**: **v2 REMAINS SEALED. ZERO RE-EXECUTION.**
* **Scientific Validity**: The v2 primary regression cohort ($N = 731$) was defined strictly by the continuous filter `3.0 < CLint < 150.0 AND standard_relation IS NULL`. Every compound in the v2 cohort was a verified exact measurement.
* **Impact of Clarification**: The exclusion of the 13 exact boundary records from v2 was a conservative, prospective decision made when their semantics were unconfirmed. This conservative posture protected v2 from boundary artifacts. The new clarification reinforces the validity of v2's interior cohort; it does **not** invalidate v2, nor does it justify re-opening or re-running v2 models.

### 6.2 Historical Censored-Modelling Exploratory Study
* **Status**: Historical exploratory artifact preserved as executed.
* **Prospective Guidance**: Any future censored-modelling protocol must incorporate the resolved semantic ground truth:
  $$\text{Exact Quantitative} = 744, \quad \text{Left-Censored} = 274, \quad \text{Right-Censored} = 84$$
  The 13 unqualified value-3 observations must **never** be treated as left-censored in future work.

### 6.3 HLM–Hepatocyte (HH) Pairing Cohorts
* **Status**: No recomputation of correlation coefficients.
* **Impact**: In `results/hlm_hh_pairing_v1/`, the paired cohort contains two compounds whose HLM values are unqualified exact 3.0 measurements. 
  * The $N = 94$ doubly in-range cohort remains the valid **strict-interior paired cohort**.
  * The $N = 96$ sensitivity cohort (which included the boundary records) is now formally recognized as the **maximal exact quantitative paired cohort**.

---

## 7. Consequences for v3A Prospective Study Design

> **PROVENANCE NOTICE: V3A_COHORT_DECISION_REOPENED_BY_NEW_PROVENANCE**

1. **Protocol Text Invariance**:
   The draft SAP (`docs/V3A_UNCERTAINTY_ASSAY_TRIAGE_SAP_DRAFT.md`) is **NOT modified or executed** in this provenance update.
2. **Re-Opening of Cohort Decision**:
   The prospective v3A study was drafted under the assumption that the quantifiable interior was $N = 731$, with the 13 boundary records excluded due to unresolved ambiguity. Because these 13 records are now proven to be exact quantitative observations ($N_{\text{exact}} = 744$), the prospective study design committee must formally decide during SAP reconciliation:
   * **Option A**: Retain the strict interior cohort ($N = 731$, $3.0 < CL_{\text{int}} < 150.0$) as the primary triage population, treating the 13 boundary points as a secondary sensitivity cohort.
   * **Option B**: Expand the primary triage population to all $N = 744$ exact quantitative observations ($3.0 \le CL_{\text{int}} < 150.0$).
3. **External Assay-Reliability Sensitivity Context**:
   Wenlock & Carlsson (2015) argued that, in the broader pooled AstraZeneca human microsomal dataset, variability was relatively stable above approximately $25\text{ }\mu\text{L/min/mg}$ ($\approx 1.40\text{ }\log_{10}\text{ units}$), with typical SD around $0.11$. During v3A SAP reconciliation, the committee may consider $\ge 25\text{ }\mu\text{L/min/mg}$ as an externally motivated assay-family sensitivity threshold candidate. It is strictly not a validated CHEMBL3301370-specific reliability boundary.

---

## 8. Explicit Inventory of What Remains Unknown

To prevent over-claiming, the following parameters remain **strictly unknown from public data and depositor records**:
1. **Individual Row Aggregate Status**: It remains unknown which specific rows among the 1,102 records represent single experimental determinations versus multi-run aggregates.
2. **Row-Specific Replicate Counts**: No row-level sample sizes ($n$) were deposited in ChEMBL or retained in public records.
3. **Row-Specific Standard Deviations**: No compound-level standard deviations or confidence intervals exist in the deposited database.
4. **Exact Mathematical Aggregation Function**: It is unconfirmed whether replicate aggregation was conducted via arithmetic mean, geometric mean, median, or robust M-estimation for each individual compound.
5. **Intra-Assay Replication Protocol**: It remains unconfirmed whether individual 96-well incubation runs routinely utilized duplicate/triplicate incubation wells or single-well incubations for this specific HLM assay deposition.
6. **Compound Overlap with 2015 Publication**: It is unconfirmed whether the 1,102 compounds in `CHEMBL3301370` represent a direct subset of the pooled human microsomal dataset analyzed in Wenlock & Carlsson (2015).

---

## 9. Archival Sign-Off & Verification

This update completes the documentary reconciliation for `CHEMBL3301370` depositor semantics.

* No models have been fit or evaluated.
* No datasets have been altered.
* Historical records and reports retain their execution-time context.
* All semantic labels, counts, and uncertainties are verified.

```
DEPOSITOR_PROVENANCE_RESOLVED_744_EXACT_NO_MODEL_RERUN
```
