# V3A HLM Apparent CLint Assay-Uncertainty Literature Audit

## Metadata

**SOURCE:** ScienceBuddy targeted DMPK evidence audit

**DATE:** 2026-09-24

**ROLE:** Interpretation context only

**PROTOCOL STATUS:** NO V3A PROTOCOL CHANGE

## Evidence classes

### DATASET-SPECIFIC TO CHEMBL3301370

- Endpoint: apparent HLM intrinsic clearance.
- Range: 3–150 mL/min/g.
- `<3` is left-censored.
- `>150` is right-censored.
- Unqualified numeric values are exact reported measurements.
- Exact 3 is quantitative.
- Present exact quantitative cohort: `N=744`.

No examined external paper supplies row-level replicate variance, analytical validation, microsomal lot, protein concentration, incubation schedule, temperature, or aggregation metadata specifically for CHEMBL3301370.

### ASSAY-FAMILY EVIDENCE

Evidence concerning related microsomal or DMPK assay families; it is not dataset-specific observation-error evidence for CHEMBL3301370.

### OTHER HLM PROTOCOL EVIDENCE

Evidence from other HLM or microsomal protocols; protocol-specific quantities are not transferable to CHEMBL3301370 without direct evidence.

### REVIEW/INTERPRETATION

Interpretive implications of the accessed evidence, not additional dataset-specific measurements.

> **EVIDENCE BOUNDARY:** External SDs, limits, class boundaries, analytical precision estimates, donor effects, binding estimates, or protocol-specific LLOQs MUST NOT be transferred as the observation-error distribution of CHEMBL3301370.

> **ACCESS NOTE:** “Project-local evidence may contain stronger or full-text evidence for some sources than was available to this ScienceBuddy run. This memo records the ScienceBuddy access state and does not supersede separately preserved primary-paper provenance.”

No reconciliation with separately preserved project-local source provenance is attempted here.

## Authoritative source transcription

```text
SOURCE B — SCIENCEBUDDY DMPK-SPECIFIC HLM ASSAY-UNCERTAINTY AUDIT

DMPK-specific evidence audit

Scope and evidentiary boundary

DATASET-SPECIFIC TO CHEMBL3301370: The endpoint is apparent HLM intrinsic clearance. The established range is 3–150 mL/min/g; values below 3 and above 150 are censored; unqualified numeric values—including 3—are exact reported measurements; the present cohort contains 744 exact quantitative values.

DATASET-SPECIFIC TO CHEMBL3301370: No examined external paper provides replicate-level variance, analytical validation, microsomal lot, protein concentration, incubation schedule, temperature, or aggregation metadata specifically for CHEMBL3301370.

REVIEW/INTERPRETATION: Therefore, external numerical SDs, limits, or class boundaries must not be treated as the observation-error distribution of CHEMBL3301370.

Quantitative external evidence

ASSAY-FAMILY EVIDENCE — Wenlock & Carlsson evaluated how gross, systematic, and random experimental error affected QSAR/QSPR models built from internal DMPK data.
Numerical result and conditions: Models trained on fewer, repeatedly measured observations with an uncertainty threshold improved external-test prediction by 3.3%–23.0%; using lower-uncertainty data improved prediction by 3.3%–27.5%. The publisher abstract does not expose endpoint-specific sample sizes, replicate schedules, or an HLM-specific SD.
Relevance and limitation: Demonstrates that repeat measurement and label quality can materially affect DMPK modeling. It does not supply row-level noise or a transferable SD for CHEMBL3301370.

OTHER HLM PROTOCOL EVIDENCE — Di & Obach reviewed low-clearance measurement limits in standard microsomal depletion assays.
Numerical result and conditions: An illustrative lower measurable CLint was approximately 12 µL/min/mg protein, calculated using a maximum measurable in-vitro half-life of 120 min, 0.5 mg/mL microsomal protein, and a 1-hour incubation. They noted that protein is commonly kept below 2 mg/mL and incubation below approximately 1 hour because nonspecific binding increases with protein and enzyme activity declines with time.
Relevance and limitation: The value is a protocol-derived example, not a universal HLM LLOQ and not the CHEMBL3301370 threshold.

OTHER HLM PROTOCOL EVIDENCE — Austin et al. measured apparent clearance and microsomal binding for 13 drugs at three microsomal-protein concentrations; binding for another 25 drugs was measured at 1 mg/mL.
Numerical result and conditions: Rat liver microsomes; half-life depletion assay and equilibrium dialysis. Apparent CLint depended on protein concentration, while correction for microsomal binding made values approximately concentration-independent. Binding correlated with lipophilicity, with different behavior for bases versus acidic/neutral compounds.
Relevance and limitation: Strong mechanistic evidence that apparent CLint error or bias can be structure dependent. It is rat-microsome evidence, not direct HLM repeatability evidence.

OTHER HLM PROTOCOL EVIDENCE — Obach examined HLM half-life measurements and microsomal binding for 29 structurally diverse drugs.
Numerical result and conditions: Scaled intrinsic clearance ranged from <0.5 to 189 mL/min/kg; microsomal unbound fractions ranged from 0.11 to 1.0 at the protein concentrations used. Basic compounds generally showed more binding.
Relevance and limitation: Human-microsome evidence for compound-dependent binding and IVIVE bias, but not a replicate-error study and not in CHEMBL3301370 units.

ASSAY-FAMILY EVIDENCE — Williamson et al. compared a harmonized high-throughput microsomal assay with traditional formats differing in buffer, microsomal concentration, human lot, and animal strain.
Numerical result and conditions: Human-lot CLint results were reported as well correlated with no significant format difference. Using classes <50, 50–100, and >150 µL/min/mg protein, agreement across evaluated conditions exceeded 80%. The accessible abstract does not state the compound count or continuous-value SD.
Relevance and limitation: Protocol harmonization can preserve broad classes while still allowing continuous-value disagreement. These class thresholds must not be transferred to CHEMBL3301370.

OTHER HLM PROTOCOL EVIDENCE — Temesi et al. compared MRM triple-quadrupole detection with OATOF/ADC detection.
Numerical result and conditions: More than 1,000 compounds were screened in rat and/or cryopreserved human hepatocytes over 3 months. A structurally diverse subset showed good agreement; OATOF had a higher success rate and approximately 20% shorter acquisition time. Subset size and continuous error statistics were not stated in the abstract.
Relevance and limitation: Relevant to analytical-platform heterogeneity, but it is not an HLM replicate-precision study.

OTHER HLM PROTOCOL EVIDENCE — A validated single-compound HLM LC–MS/MS study quantified rociletinib.
Numerical result and conditions: Calibration range 5–500 ng/mL; LOQ 4.6 ng/mL; reported intra/inter-day accuracy and precision were below 4.63%; estimated CLint was 20.15 µL/min/mg and half-life 34.39 min.
Relevance and limitation: Shows that analytical error can be small in a validated compound-specific method. It cannot characterize generic-screen or CHEMBL3301370 analytical error.

OTHER HLM PROTOCOL EVIDENCE — Donor-matched HLM/hepatocyte work evaluated five CYP probe substrates across 15 donors.
Numerical result and conditions: Protein-expression differences, intracellular unbound exposure, enrichment during microsome preparation, and potentially different proportions of active/inactive CYP only partly explained system-level CLint disagreement.
Relevance and limitation: Supports lot/donor and preparation effects as enzyme- and substrate-dependent rather than a single common variance term.

Audit of the 15 requested uncertainty mechanisms

Lower limit and low-clearance resolution — OTHER HLM PROTOCOL EVIDENCE: Parent-depletion resolution is determined by how much disappearance can be distinguished from analytical and sampling variation over the permitted incubation. Di & Obach’s approximately 12 µL/min/mg example is conditional on a 120-min resolvable half-life, 0.5 mg/mL protein, and a 1-hour experiment.

REVIEW/INTERPRETATION: Near a lower reporting boundary, small slope errors can produce large relative CLint errors. Stable compounds may become indistinguishable even when their true clearances differ. This plausibly produces heteroscedasticity and compression, but the external 12 µL/min/mg value cannot redefine CHEMBL3301370’s established 3 mL/min/g boundary.

High-clearance ceiling effects — ASSAY-FAMILY EVIDENCE: Substrate-depletion CLint is estimated from the decline in parent concentration across sampled times.

REVIEW/INTERPRETATION: Very rapid depletion can leave few informative post-zero samples, making slope estimation sensitive to the earliest sampling time, mixing delay, quench timing, and the analytical LLOQ. Right-censoring at 150 additionally removes ordering among faster compounds and can make uncertainty depend mechanically on proximity to the ceiling.

Parent-depletion assay kinetics — OTHER HLM PROTOCOL EVIDENCE: The usual estimator fits a first-order slope to log parent remaining versus time and converts that slope using incubation volume and microsomal-protein amount. Parent depletion measures all disappearance pathways collectively and does not require quantification of every metabolite.

REVIEW/INTERPRETATION: Bias arises if depletion is not mono-exponential because of saturation, time-dependent inhibition, metabolite inhibition, cofactor depletion, nonenzymatic loss, precipitation, or declining enzyme activity. Such behavior can be compound-specific and structurally patterned.

Microsomal protein concentration — OTHER HLM PROTOCOL EVIDENCE: Austin et al. showed protein-concentration dependence of apparent CLint for strongly binding compounds; binding correction substantially removed that dependence in rat microsomes.

REVIEW/INTERPRETATION: If CHEMBL3301370 combines protocols or batches with different protein concentrations, lipophilic/basic compounds could shift systematically rather than acquire purely random noise.

Incubation duration — OTHER HLM PROTOCOL EVIDENCE: Di & Obach noted that standard microsomal incubations are generally shorter than approximately one hour because activity declines over longer periods.

REVIEW/INTERPRETATION: Short assays poorly resolve low clearance, whereas longer assays increase exposure to enzyme decay, instability, binding, evaporation, and nonenzymatic loss. The resulting error can change direction across the response range.

Nonspecific microsomal binding — OTHER HLM PROTOCOL EVIDENCE: Austin et al. found binding related to lipophilicity and ionization; Obach found microsomal unbound fractions of 0.11–1.0 among 29 HLM-tested drugs, with basic compounds generally binding more.

REVIEW/INTERPRETATION: Because lipophilicity, charge, and ionization are encoded by structure, uncorrected binding is one of the clearest mechanisms through which apparent measurement bias can itself be structure-predictable.

CYP activity loss during incubation — REVIEW/INTERPRETATION: Time-dependent loss of enzyme activity makes the later depletion curve shallower, biasing low-turnover compounds downward because their estimate depends most heavily on late samples.

OTHER HLM PROTOCOL EVIDENCE: Di & Obach explicitly identified declining microsomal enzyme activity as a reason not simply to extend incubation indefinitely.

Microsome lot/donor variability — OTHER HLM PROTOCOL EVIDENCE: Human donor-matched studies show that CYP abundance/activity and microsomal preparation can differ between donors and affect substrates according to their enzyme pathways. Williamson et al. nevertheless found over 80% agreement at broad clearance-class level across tested assay conditions and lots.

REVIEW/INTERPRETATION: Lot effects are partly compound-by-lot interactions: two compounds can respond differently if they depend on different CYPs. Unknown lot assignment is not predictable from structure alone, although enzyme-substrate preference is partly predictable.

Analytical quantification error — OTHER HLM PROTOCOL EVIDENCE: LC–MS/MS precision depends on the compound, calibration range, internal standard, matrix effect, recovery, signal intensity, and LLOQ. The rociletinib example achieved <4.63% reported intra/inter-day error under a dedicated validated method; Temesi showed broad agreement between two detection technologies but did not publish a transferable HLM variance estimate in its abstract.

REVIEW/INTERPRETATION: Generic high-throughput methods can have structure-dependent ionization, adduct formation, interference, carryover, and extraction recovery. Analytical precision from a dedicated one-compound assay should not be assigned to a generic screen.

Intra-assay versus inter-assay replication — ASSAY-FAMILY EVIDENCE: Wenlock & Carlsson treated repeated measurements as informative about experimental uncertainty and found that lower-uncertainty/repeated data could improve external model performance.

REVIEW/INTERPRETATION: Same-plate duplicates mainly expose pipetting and analytical repeatability; independent-day, analyst, instrument, reagent, and microsome-lot repeats include much more variance. A replicate count without its hierarchy is insufficient to define measurement uncertainty.

Aggregation of repeat measurements — ASSAY-FAMILY EVIDENCE: Wenlock & Carlsson compared modeling strategies involving repeated observations and uncertainty filtering, but their reported gains are dataset/model outcomes rather than a universal HLM SD.

REVIEW/INTERPRETATION: Means or medians suppress visible within-compound scatter; cherry-picking, “best run,” censor-aware substitution, or merging measurements across protocols can instead introduce bias. If CHEMBL3301370 exposes only an aggregate, QRF width cannot recover the discarded replicate variance.

Temperature and protocol differences — ASSAY-FAMILY EVIDENCE: Williamson et al. directly evaluated harmonization across protocols differing in buffer and microsomal concentration; broad clearance-class agreement exceeded 80%.

REVIEW/INTERPRETATION: Temperature, pre-incubation, NADPH concentration, solvent fraction, shaking, sampling times, and quench procedure can affect kinetic rate or stability. No retrieved study supplies a temperature-effect magnitude that is transferable to CHEMBL3301370.

Assay harmonization across laboratories — ASSAY-FAMILY EVIDENCE: Williamson et al. showed that consolidating divergent formats could yield consistent class assignments under head-to-head testing.

REVIEW/INTERPRETATION: More than 80% class agreement is weaker than continuous-value interchangeability and does not establish equal precision, equal calibration, or absence of compound-by-protocol interactions.

Compound-specific heteroscedasticity — ASSAY-FAMILY EVIDENCE: Wenlock & Carlsson distinguished gross, systematic, and random errors and found model gains when higher-uncertainty observations were excluded or repeatedly measured.

REVIEW/INTERPRETATION: HLM measurement variance is plausibly nonconstant: low-clearance compounds have small depletion slopes; high-clearance compounds may disappear before informative sampling; intermediate compounds may have the best-resolved slopes. Binding, solubility, ionization, and pathway complexity add compound-specific variation.

Physicochemical dependence of measurement error — OTHER HLM PROTOCOL EVIDENCE: Austin and Obach provide direct evidence that microsomal binding depends on lipophilicity and acid/base character.

REVIEW/INTERPRETATION: Poor solubility, adsorption, matrix recovery, LC ionization, microsomal binding, saturation, and CYP substrate preference can all covary with molecular descriptors. A structure model may therefore predict assay susceptibility as well as—or instead of—biological CLint uncertainty.

Answers to A–F

A. Error sources potentially predictable from molecular structure
REVIEW/INTERPRETATION: Nonspecific microsomal binding, especially through lipophilicity and ionization.
REVIEW/INTERPRETATION: Solubility, precipitation, adsorption, extraction recovery, LC–MS ionization, and matrix effects.
REVIEW/INTERPRETATION: CYP pathway preference, saturation, substrate inhibition, time-dependent inhibition, metabolite inhibition, and chemical instability.
REVIEW/INTERPRETATION: Susceptibility to the low- and high-clearance limits, because true turnover and assay artifacts both correlate with structural features.

B. Error sources essentially unpredictable from structure alone
REVIEW/INTERPRETATION: Analyst, pipetting, plate-position, timing, instrument-drift, and sample-handling errors.
REVIEW/INTERPRETATION: Unrecorded laboratory, day, protocol, or microsome-lot assignment.
REVIEW/INTERPRETATION: Random LC–MS noise conditional on a fixed signal level.
REVIEW/INTERPRETATION: Donor composition itself, although a molecule’s sensitivity to donor composition may be structure-dependent.
REVIEW/INTERPRETATION: Undocumented rules used to select or aggregate repeat results.

C. Sources capable of response-range confounding
REVIEW/INTERPRETATION: The 3 and 150 boundaries; limited depletion at the low end; near-complete early depletion at the high end; response-dependent slope precision; enzyme decay during long incubations; and protein-binding effects that compress apparent clearance.
REVIEW/INTERPRETATION: Consequently, prediction-interval width can correlate with observed CLint simply because measurement resolution varies across the response range.

D. Sources that could make QRF width appear useful without measuring epistemic uncertainty
REVIEW/INTERPRETATION: Learning distance to the censoring boundaries or regions with intrinsically poorer assay resolution.
REVIEW/INTERPRETATION: Learning structure-linked binding, solubility, LC–MS response, or saturation artifacts.
REVIEW/INTERPRETATION: Learning historical batch, scaffold, or protocol clusters.
REVIEW/INTERPRETATION: Reflecting irreducible assay variability or mixed measurement regimes rather than lack of training knowledge.
REVIEW/INTERPRETATION: Correlating with absolute residuals because both increase at response extremes.

E. Causes of a negative v3A result despite a real structure→clearance relationship
REVIEW/INTERPRETATION: Predominantly structure-independent run/lot/analytical noise.
REVIEW/INTERPRETATION: Aggregation that removes replicate dispersion from the labels.
REVIEW/INTERPRETATION: Floor or ceiling compression that makes different latent clearances observationally indistinguishable.
REVIEW/INTERPRETATION: Compound-by-protocol interactions absent from molecular descriptors.
REVIEW/INTERPRETATION: A mismatch between QRF ensemble dispersion and the actual sources of label uncertainty.
REVIEW/INTERPRETATION: Limited statistical power from 744 exact observations when heteroscedasticity is modest or localized.

F. Causes of a positive v3A result without deployable prospective uncertainty
REVIEW/INTERPRETATION: QRF width may detect retrospective response-range artifacts rather than epistemic uncertainty.
REVIEW/INTERPRETATION: It may learn assay-specific structure biases that disappear under another laboratory, lot, instrument, or protocol.
REVIEW/INTERPRETATION: It may exploit scaffold density in the historical cohort without extrapolating to new chemistry.
REVIEW/INTERPRETATION: It may correlate with residual magnitude while remaining miscalibrated as a prospective interval.
REVIEW/INTERPRETATION: A positive association within CHEMBL3301370 therefore supports retrospective risk ranking, but does not by itself establish prospective coverage or transportability.

Sources consulted

Wenlock MC, Carlsson LA. How Experimental Errors Influence Drug Metabolism and Pharmacokinetic QSAR/QSPR Models. J Chem Inf Model. PMID 25406036; DOI 10.1021/ci500535s.
Evidence accessed: Abstract/publisher metadata; full text was not available.

Di L, Obach RS. Addressing the Challenges of Low Clearance in Drug Research. AAPS J. PMID 25567366; DOI 10.1208/s12248-014-9691-7.
Evidence accessed: Abstract plus indexed full-text excerpts.

Austin RP et al. The Influence of Nonspecific Microsomal Binding on Apparent Intrinsic Clearance, and Its Prediction from Physicochemical Properties. Drug Metab Dispos. PMID 12433825; DOI 10.1124/dmd.30.12.1497.
Evidence accessed: Abstract/official metadata.

Williamson B et al. Harmonised high throughput microsomal stability assay. J Pharmacol Toxicol Methods. PMID 27773845; DOI 10.1016/j.vascn.2016.10.006.
Evidence accessed: Abstract/official metadata.

Temesi DG et al. High-throughput metabolic stability studies in drug discovery by orthogonal acceleration time-of-flight (OATOF) with analogue-to-digital signal capture (ADC). Rapid Commun Mass Spectrom. PMID 20499316; DOI 10.1002/rcm.4546.
Evidence accessed: Abstract/official metadata.

Obach RS. Prediction of Human Clearance of Twenty-Nine Drugs from Hepatic Microsomal Intrinsic Clearance Data: An Examination of In Vitro Half-Life Approach and Nonspecific Binding to Microsomes. Drug Metab Dispos. PMID 10534321.
Evidence accessed: Abstract/official metadata.

Vildhede A et al. Influence of Proteome Profiles and Intracellular Drug Exposure on Differences in CYP Activity in Donor-Matched Human Liver Microsomes and Hepatocytes. Mol Pharm. PMID 33739838; DOI 10.1021/acs.molpharmaceut.1c00053.
Evidence accessed: Abstract and PMC-indexed full-text excerpts.

Mechanism → Implication for interpreting v3A

Low-clearance slope resolution → Width may identify weak depletion signals or proximity to the lower boundary, not epistemic uncertainty.
High-clearance ceiling and early depletion → Width or residuals may reflect truncation and sampling cadence; ordering above the ceiling is unavailable.
First-order kinetic-model failure → Structure-dependent curvature can look like predictable uncertainty.
Microsomal protein concentration → Unrecorded concentration differences can interact with compound binding and shift apparent CLint.
Incubation duration → Short runs limit low-clearance resolution; long runs introduce enzyme-decay and stability bias.
Nonspecific microsomal binding → A major structure-predictable source of systematic apparent-CLint distortion.
CYP activity loss → Can selectively underestimate slowly depleted compounds and generate range-dependent bias.
Lot/donor variability → Adds largely unobserved biological variation with compound-specific enzyme-pathway interactions.
Analytical quantification → Contains both structure-linked matrix/ionization effects and structure-independent run noise.
Intra-assay replication → Usually characterizes only narrow technical repeatability.
Inter-assay replication → Better captures day, analyst, instrument, reagent, and microsome-lot variation.
Repeat aggregation → Can hide label variance and prevent QRF width from learning actual measurement uncertainty.
Protocol and temperature heterogeneity → Can produce batch shifts or compound-by-protocol interactions that are not molecular epistemic uncertainty.
Harmonization → Broad class agreement does not establish continuous-value interchangeability or transferable SD.
Compound-specific heteroscedasticity → Makes a single global noise benchmark inappropriate and can create apparently informative widths.
Physicochemical error dependence → Allows QRF width to predict assay susceptibility, which may be useful retrospectively but nonportable prospectively.
Negative v3A → Does not refute a real structure→clearance relationship; relevant uncertainty may be hidden, censored, averaged away, or driven by unobserved experimental factors.
Positive v3A → Supports retrospective association only; it does not establish calibrated, deployable prospective epistemic uncertainty.
```
