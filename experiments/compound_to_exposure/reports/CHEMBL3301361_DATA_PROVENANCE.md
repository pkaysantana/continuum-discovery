# CHEMBL3301361 Dataset Provenance & Depositor Semantics

This document records the provenance, historical curation background, and archival resolution status for ChEMBL document `CHEMBL3301361` (assays `CHEMBL3301370`, `CHEMBL3301371`, `CHEMBL3301372`).

---

## 1. ChEMBL Helpdesk Resolution (chembl-help #890728)

The inquiry regarding the semantics of `standard_relation = NULL` records deposited under document `CHEMBL3301361` was initially addressed via ChEMBL support ticket **chembl-help #890728**.

ChEMBL support stated:
- The dataset was added in 2015 as part of ChEMBL 20.
- Nobody on the current ChEMBL team was involved in the original deposition, so they cannot provide 100% archival confirmation.
- They are nevertheless "fairly confident" that ordinary numeric records in `CHEMBL3301361` with `relation = NULL` were intended to represent exact/in-range measurements, effectively semantic `=`.
- Their reasoning is that the linked AstraZeneca publication (*Rapid Communications in Mass Spectrometry* 2010, 24, 1730–1736) reports values below the lower range as `<3` and the other reported $\text{CL}_{\text{int}}$ values as exact measurements.
- The paper publishes only 28 $\text{CL}_{\text{int}}$ values from approximately 1,140 compounds, so it is uncertain whether the full ChEMBL deposition is exactly the published dataset or separately generated data using the same method.
- ChEMBL support explicitly agreed that unqualified values exactly equal to 3 should remain semantically unknown because the publication reports `<3` at the lower end and does not establish genuine exact-3 measurements.
- ChEMBL found no indication that the deposited values are replicate-derived or aggregated and considered individual measurements the most plausible interpretation, but could not confirm this.
- ChEMBL identified Mark Wenlock and Nicholas Tomkinson as the original depositors who may be able to provide additional archival clarification.

---

## 2. Historical Scientific Interpretation Preservation (Pre-23 September 2026)

Under the prior helpdesk-only evidence, the project maintained the following conservative stance:
- Raw `standard_relation = NULL` remains preserved as raw database provenance.
- Source records are **not** rewritten to `=`.
- Records with `NULL` relation and $3 < \text{CL}_{\text{int}} < 150$ were described as:
  > **"likely exact in-range measurements based on ChEMBL support guidance"**
- The 13 `NULL`-at-3 records were provisionally designated as **`BOUNDARY_AMBIGUOUS`**.
- The 274 `<3` records were designated **left-censored**.
- The 84 `>150` records were designated **right-censored**.
- Existing frozen v2 cohorts ($N=731$ strict interior) were defined conservatively under this policy.

---

## 3. First-Hand Depositor Resolution (23 September 2026)

### Status: RESOLVED_BY_DEPOSITOR_CLARIFICATION (Mark Wenlock, 23 Sep 2026)

On 23 September 2026, Mark Wenlock, one of the original compilers/depositors of `CHEMBL3301361`, provided direct, first-hand archival clarification concerning the ChEMBL HLM clearance record:

> “With respect to the dynamic range of the microsomal clearance assay in this CHEMBL data record, it ranged from 3 to 150 mL/min/g. Measurements without a qualifier (i.e., ‘<’ or ‘>’) would be the exact number – there may be instances where a compound had an exact measurement of 3 or 150 and these will be distinct from instances where a compound had a measurement of <3 or >150.
> 
> When Nick and I compiled this data record, we would have used inter-assay replicate-derived/aggregated results where available – I don’t think we shared the associated standard deviation, although experimental errors were talked about in the publication: J. Chem. Inf. Model. 2015, 55, 125−134. Relatedly, I can’t recall whether the assay in question was derived from multiple intra-assay replicates, but this information would be mentioned in the associated publication: Rapid Commun. Mass Spectrom. 2010, 24, 1730-1736.”

This statement serves as **Level A primary archival evidence** for dataset `CHEMBL3301370`.

For full details, literature analysis, and procedural implications, see the standalone resolution memo:
[DEPOSITOR_PROVENANCE_RESOLUTION_2026-09-23.md](file:///c:/Users/Don/continuum%20discovery/continuum-discovery-1/experiments/compound_to_exposure/reports/DEPOSITOR_PROVENANCE_RESOLUTION_2026-09-23.md).

---

## 4. Revised Measurement Semantics & Superseding Status

### 4.1 Invariance of Raw Data
The raw ChEMBL database column remains untouched:
- `standard_relation = NULL` is preserved exactly as deposited.
- **Do NOT rewrite `NULL` to `"="`.**

### 4.2 Derived Semantic Classifications
The scientific interpretation is updated as follows:
- `standard_relation == '<'`, value 3 $\rightarrow$ **`LEFT_CENSORED`**
- `standard_relation == '>'`, value 150 $\rightarrow$ **`RIGHT_CENSORED`**
- `standard_relation IS NULL`, $3 < \text{value} < 150$ $\rightarrow$ **`EXACT_QUANTITATIVE`**
- `standard_relation IS NULL`, $\text{value} == 3$ $\rightarrow$ **`EXACT_QUANTITATIVE_BOUNDARY_LOW`**
- `standard_relation IS NULL`, $\text{value} == 150$ $\rightarrow$ **`EXACT_QUANTITATIVE_BOUNDARY_HIGH`**

### 4.3 Verified Repository Record Counts (`CHEMBL3301370`)
- **Total records**: 1,102
- **`<3` (Left-censored)**: 274
- **`>150` (Right-censored)**: 84
- **Unqualified strict interior ($3 < CL_{\text{int}} < 150$)**: 731
- **Unqualified exact boundary value 3**: 13
- **Unqualified exact boundary value 150**: 0
- **Total exact quantitative observations**: **744** (731 strict interior + 13 boundary low + 0 boundary high)
- **Unresolved / ambiguous relation records**: **0**

**Superseding Notice**: The previous provisional label `BOUNDARY_AMBIGUOUS` for the 13 unqualified value-3 observations is **formally superseded** by first-hand depositor clarification. These 13 records are confirmed uncensored exact measurements. Historical documents describing them as ambiguous reflect the scientific understanding prior to 23 September 2026 and are retained as valid historical artifacts.

---

## 5. Replicate Provenance & Measurement Precision

### 5.1 Replicate Provenance
Any prior description of each deposited row as an "individual single-run measurement" is replaced with the canonical formulation:

> **“Each deposited row represents a compound-level HLM CLint result. According to original depositor Mark Wenlock, inter-assay replicate-derived/aggregated results were used where available. The deposited record does not provide row-level replicate counts or associated standard deviations, so individual records cannot be classified as single measurements versus replicate-derived aggregates from the public data alone.”**

### 5.2 Decoupling Exact Semantics from Measurement Precision
- **Exact Measurement Semantics**: An unqualified value of 3 is now known to be an uncensored, exact observation (as distinct from $<3$).
- **Measurement Precision**: Exact boundary observations remain subject to experimental uncertainty. In the broader AstraZeneca human microsomal CLint dataset, the estimated typical repeat-measurement SD was approximately 0.12 log10 units (95% CI for that estimate: 0.08–0.16), with variability increasing toward the low-clearance end. These values provide assay-family context and must not be assigned as row-specific SDs to CHEMBL3301370. Do not imply that exact-3 records individually have $\text{SD} \ge 0.12$.

---

## 6. Analytical Program Consequences (Non-Execution Policy)

1. **v2 Protocol**:
   - **v2 remains sealed; no models are rerun.**
   - The v2 primary cohort ($N=731$ strict interior) consisted entirely of valid exact measurements.
   - The exclusion of the 13 exact boundary observations was a conservative, prospective choice given the information available at execution time. v2 is not retroactively invalidated.
2. **Historical Censored-Modelling Experiment**:
   - Preserved in its original executed state as exploratory work.
   - Prospective censoring studies must recognize: Exact Quantitative = 744, Left-Censored = 274, Right-Censored = 84.
   - The 13 value-3 observations must not be treated as left-censored.
3. **HLM–Hepatocyte Pairing**:
   - For the paired HLM–HH dataset, the previous $N=96$ sensitivity cohort now represents the maximal exact quantitative paired cohort, while $N=94$ remains the strict-interior cohort. No recomputation of correlation is performed.
4. **Prospective v3A Study**:
   - Notice: **`V3A_COHORT_DECISION_REOPENED_BY_NEW_PROVENANCE`**.
   - No edits or executions of the v3A SAP are made in this task.
   - During prospective SAP reconciliation, the committee must formally decide whether v3A targets the strict interior ($N=731$) or all exact quantitative observations ($N=744$).
   - Wenlock & Carlsson (2015) argued that, in the broader pooled AstraZeneca human microsomal dataset, variability was relatively stable above approximately $25\text{ }\mu\text{L/min/mg}$, with typical SD around $0.11$. This provides an externally motivated assay-family sensitivity threshold candidate for future v3A reconciliation, but is strictly not a validated CHEMBL3301370-specific reliability boundary.

---

## 7. What Remains Strictly Unknown

From public ChEMBL data and depositor communications, the following cannot be determined:
1. Which of the 1,102 individual rows are single measurements versus replicate-derived aggregates.
2. Row-specific replicate counts ($n$).
3. Row-specific standard deviations or standard errors.
4. Exact mathematical aggregation rule used for each individual compound (e.g., arithmetic vs geometric mean vs median).
5. Whether intra-assay technical/biological replication was routinely performed for the specific HLM assay record.
6. Whether the broader five-assay 2015 human-mic dataset contains exactly the same compounds as `CHEMBL3301370`.

---

## 8. Provenance Summary Table

| Source | Status | Claim Supported | Confidence / Evidence Level | Analytic Consequence |
| :--- | :--- | :--- | :--- | :--- |
| **ChEMBL raw records** | Observed | Raw qualifiers (`NULL`, `<`, `>`) | Direct source provenance (Invariable) | Ground-truth repository counts verified |
| **Mark Wenlock (23 Sep 2026)** | Received | Range 3–150; unqualified records are exact; boundary 3 is distinct from <3; inter-assay replicate-derived/aggregated results were used where available | **Level A: Primary archival evidence** | Supersedes `BOUNDARY_AMBIGUOUS` $\rightarrow$ 744 exact quantitative |
| **ChEMBL Helpdesk #890728** | Received | Added in ChEMBL 20; high confidence ordinary numeric `NULL` is `=`; boundary 3 unconfirmed | Level B: Database curation history | Preserved historically; superseded on boundary 3 by Level A |
| **Wenlock & Carlsson (2015)** | Published | 5 pooled assays; 74% single determinations; for repeats (N ≥ 3), estimated typical SD ≈ 0.12 log units (95% CI for estimate: 0.08–0.16); stable above ~25 (SD ≈ 0.11) | Level C: Broader assay-family / institutional context | Informs experimental error context; strictly NOT row-level metadata |
| **Temesi et al. (2010)** | Published | Parent depletion kinetics; OATOF vs MRM instrument comparison on human hepatocytes; <3 below measurable range | Level D: Analytical platform context | Contextual analytical workflow; does not define HLM boundary |
| **Nicholas Tomkinson** | Contacted | Co-depositor outreach | Retired; no response | Archival status resolved via Wenlock |
