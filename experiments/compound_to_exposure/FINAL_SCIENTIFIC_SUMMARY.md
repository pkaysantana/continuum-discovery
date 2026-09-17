# Final Scientific Summary: Compound-to-Exposure v1

## One-Sentence Contribution
Using public experimental clearance datasets, this project found that simple 2D molecular representations contain reproducible scaffold-held-out signal for ranking in-vitro human liver microsomal intrinsic clearance, while model/representation performance remains dataset-dependent and does not establish in-vivo clearance or patient exposure.

## Three Principal Findings
1. **Reproducible Predictive Signal:** 2D structural representations reproducibly yield predictive rank-ordering (Spearman $\rho$ ~ 0.40 - 0.55) over trivial baselines across independent datasets in strict scaffold-held-out validation.
2. **Representation Dataset-Dependence:** Seven simple physicochemical descriptors can retain substantial predictive signal, particularly in Biogen (Ridge Descriptors $\rho \approx 0.549$), but their usefulness relative to Morgan fingerprints is dataset- and model-dependent (e.g., Morgan strongly outperforms descriptors in the AZ primary cohort).
3. **Assay Concordance:** HLM and intact human hepatocytes share a moderate intrinsic clearance rank signal ($\rho \approx 0.486$) and majority censoring-category agreement (68.45% exact agreement), with no observed non-adjacent BELOW↔ABOVE disagreements, but they remain non-interchangeable assay systems.

## Three Most Important Limitations
1. **No In-Vivo Translation:** The target across all datasets is strictly *in vitro* intrinsic clearance; this work does not extend to clinical *in vivo* clearance or exposure, which require physiological scaling and additional biological inputs (e.g., volume of distribution).
2. **Censoring and Data Ambiguities:** Absolute numerical prediction accuracy (MAE/RMSE) is fundamentally limited by unrecoverable historical censoring limits, recording artifacts, and unresolved dataset conventions (such as the Biogen native log base and the 958-value pileup).
3. **Applicability Domain Weakness:** Maximum training-set Morgan Tanimoto similarity is at most a weak predictor of model error ($\rho$ typically > -0.20) and does not provide a robust cross-dataset confidence rule.

## Three Things Explicitly Not Claimed
1. **Prediction of Patient Exposure:** The models do not predict *in vivo* human clearance or patient exposure.
2. **Assay Interchangeability:** The models do not claim that Human Liver Microsomes and whole Human Hepatocytes are numerically interchangeable.
3. **Universal Model Superiority:** The models do not establish that Random Forest always outperforms Ridge, or that Morgan fingerprints always outperform simple descriptors.

## Experimental Next Steps
1. **Prospective HLM Measurements:** Synthesize and test a chemically diverse, held-out batch of novel molecules prospectively in a standardized HLM stability assay.
2. **Matched Hepatocyte Assays:** Conduct parallel LC-MS/MS bioanalysis in matched HLM and intact hepatocyte systems to rigorously profile specific non-P450 clearance mechanisms (e.g. active transport).
3. **Eventual IVIVE:** Perform *In Vitro-In Vivo* Extrapolation (IVIVE) only after securing appropriate additional physiological inputs, plasma protein binding (fu_p), and microsomal binding (fu_mic) measurements.
