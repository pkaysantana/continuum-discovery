# CHEMBL3301361 Dataset Provenance & Depositor Semantics

This document records the provenance, historical curation background, and archival resolution status for ChEMBL document `CHEMBL3301361` (assays `CHEMBL3301370`, `CHEMBL3301371`, `CHEMBL3301372`).

---

## 1. ChEMBL Helpdesk Resolution (chembl-help #890728)

The inquiry regarding the semantics of `standard_relation = NULL` records deposited under document `CHEMBL3301361` was resolved via ChEMBL support ticket **chembl-help #890728**.

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

## 2. Scientific Interpretation Preservation

The scientific interpretation across all analytical artifacts remains strictly preserved:
- Raw `standard_relation = NULL` remains preserved as raw database provenance.
- Source records are **not** rewritten to `=`.
- Records with `NULL` relation and $3 < \text{CL}_{\text{int}} < 150$ may now be described as:
  > **"likely exact in-range measurements based on ChEMBL support guidance"**
- The 13 `NULL`-at-3 records remain **`BOUNDARY_AMBIGUOUS`**.
- The 274 `<3` records remain **left-censored**.
- The 84 `>150` records remain **right-censored**.
- **No existing cohort membership changes.**
- **No existing numerical result changes.**
- This constitutes stronger provenance support for the already-used interpretation, not a retrospective analytical change.

---

## 3. Pending archival depositor follow-up

### Status: OUTREACH_PENDING — NOT EVIDENCE

The following outreach actions have been taken to seek original depositor clarification:
- Mark Wenlock has now been contacted by email regarding the historical deposition semantics.
- A LinkedIn connection request has also been sent to Mark Wenlock.
- A LinkedIn connection request has been sent to Nicholas Tomkinson.
- Nicholas Tomkinson is now retired from AstraZeneca.
- No response from either depositor has yet been incorporated into the scientific record.

**Constraints:**
- Do not infer what either depositor will say.
- Do not upgrade "likely exact" to "confirmed exact."
- Do not alter the treatment of the `NULL`-at-3 observations.

---

## 4. Provenance Summary Table

| Source | Status | Claim supported | Confidence/status | Analytic consequence |
| :--- | :--- | :--- | :--- | :--- |
| ChEMBL raw records | observed | NULL / < / > source qualifiers | direct source provenance | existing cohort definitions |
| AstraZeneca 2010 paper | published | <3 lower-end reporting; exact reported in-range values | partial dataset evidence | supports interpretation but does not resolve all deposited rows |
| ChEMBL helpdesk #890728 | received | NULL ordinary numeric records likely exact/in-range; exact-3 remains ambiguous | informed but not archival certainty | no analytic change |
| Mark Wenlock | contacted | awaiting archival clarification | pending | none |
| Nicholas Tomkinson | contacted | awaiting archival clarification | pending | none |

*Note for future updates: If a depositor later replies, the record can be appended below without rewriting prior provenance.*
