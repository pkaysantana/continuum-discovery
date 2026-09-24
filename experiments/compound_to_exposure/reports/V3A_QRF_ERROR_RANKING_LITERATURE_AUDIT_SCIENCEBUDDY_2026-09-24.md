# V3A QRF Error-Ranking Literature Audit

## Metadata

**SOURCE:** ScienceBuddy targeted literature audit

**DATE:** 2026-09-24

**ROLE:** Methodological and interpretation context only

**PROTOCOL STATUS:** NO V3A PROTOCOL CHANGE

## Concise finding

### NO DIRECT PRECEDENT FOUND

No located study directly validates QRF Q90-Q10 as a compound-level ranking score for absolute errors of a separate frozen RF under molecular scaffold shift.

No direct precedent was located for that complete proposition specifically for hLM CLint.

### VALID V3A INTERPRETATION

> “Q90-Q10 is a prespecified empirical candidate uncertainty-ranking score whose operational utility is tested through scaffold-grouped out-of-fold retain/defer evaluation.”

### TERMINOLOGY BOUNDARIES

Do not describe QRF Q90-Q10 as:

- a calibrated prediction interval for the frozen RF;
- an estimator of RF epistemic uncertainty;
- an established estimator of frozen-RF absolute error;
- a universal applicability-domain measure;
- a central 90% interval.

Q90-Q10 is the central 80% QRF response width.

### Mathematical distinction

For a fixed predictor `f_hat(x)`, translating `Y` to residual `E = Y - f_hat(x)` preserves distribution width.

Therefore QRF response width may represent conditional residual spread if the conditional response distribution is estimated correctly.

However, width does not encode residual location or systematic model bias.

A narrow QRF width can therefore coexist with large frozen-RF error.

## Authoritative source transcription

```text
SOURCE A — SCIENCEBUDDY TARGETED QRF/RF UNCERTAINTY AUDIT

Targeted audit result

As of 23 September 2026, I found no study that directly validates Q90−Q10 from a QRF as a compound-level ranking score for the absolute errors of a separate, frozen RF under scaffold shift.

The literature supports each component separately—QRF response quantiles, RF uncertainty measures, molecular confidence curves, scaffold-shift evaluation—but not their conjunction.

No evidence makes frozen v3A technically invalid if Q90−Q10 is treated strictly as an empirical candidate ranking score. It would be technically misleading to call it:

a calibrated interval for the frozen RF;
an estimator of RF epistemic uncertainty;
an established estimator of the frozen RF’s absolute error;
a central 90% interval. Q90−Q10 spans the central 80% of the estimated response distribution.

Essential estimand distinction

QRF estimates conditional response quantiles:

W_Y(x)=Q_0.90(Y|X=x)−Q_0.10(Y|X=x).

For a fixed predictor f_hat(x), the prediction error is E=Y−f_hat(x). Translation leaves widths unchanged:

Q_0.90(E|x)−Q_0.10(E|x)=W_Y(x).

This gives QRF width a legitimate interpretation as a possible estimate of conditional error spread—if the conditional response distribution is estimated correctly. But it does not capture the error distribution’s location:

E(|Y−f_hat(x)||x)

depends on both spread and systematic bias. Consequently, a narrow QRF distribution can coexist with a large frozen-RF error, especially under scaffold shift.

Source audit

Foundational RF/QRF evidence

Meinshausen N. (2006), “Quantile Regression Forests.” JMLR 7:983–999. Full text. No DOI verified. FULL TEXT; no separate SI identified.
Endpoint, size, model and split: Five general regression benchmarks, including Ozone, Abalone, Boston Housing, Fuel and BigMac; exact per-dataset sizes were not recovered. QRF; ordinary benchmark evaluation, not chemistry or OOD.
Uncertainty quantity; same model?: Conditional response distribution F(Y|X=x); same forest weights used for response mean and quantiles.
Metric and recoverable result: Quantile loss and prediction-interval behavior; no absolute-error rank correlation, risk–coverage curve or separate-RF evaluation.
Reported limitation or relevance: Establishes QRF response quantiles and consistency under assumptions. It does not establish that width ranks RF error or detects lack of support. QRF cannot identify covariate outliers from response quantiles alone.

Lu B, Hardin J. (2021), “A Unified Framework for Random Forest Prediction Error Estimation.” JMLR 22(8):1–41. Full text; arXiv:1912.07435. FULL TEXT; appendices/package available, no separate SI identified.
Endpoint, size, model and split: Simulations with n=1000 or 3000 and 1,000 repetitions; Boston, Abalone and Servo benchmarks. RF; simulated or random train/test evaluation, no molecular shift.
Uncertainty quantity; same model?: Locally weighted OOB residual distribution F_E(e|x); belongs directly to the same RF whose prediction error is estimated.
Metric and recoverable result: Coverage and width, plus conditional MSPE/bias. In the clustered simulation, nominal 95% QRF coverage was 0.930 with mean width 15.15; competing methods were closer to 0.95, although widths varied substantially. No error-ranking curve.
Reported limitation or relevance: Practical estimator is less stringently constructed than the version receiving the consistency proof. No chemistry, scaffold shift or hLM validation.

Zhang H, Zimmerman J, Nettleton D, Nordman DJ. (2020; online 2019), “Random Forest Prediction Intervals.” DOI 10.1080/00031305.2019.1585288. FULL TEXT; supplementary analyses and code available.
Endpoint, size, model and split: Simulations and 60 general real datasets. RF point predictions; random/CV evaluations.
Uncertainty quantity; same model?: Global OOB prediction-error distribution, compared with QRF response intervals and split conformal intervals; same RF for the proposed OOB method.
Metric and recoverable result: Four coverage definitions and interval width—not absolute-error ranking. A reanalysis of five Meinshausen datasets gave 95% QRF coverage from 90.2% to 98.6%. Proposed OOB intervals generally remained near nominal marginal coverage while being narrower.
Reported limitation or relevance: Shows that QRF coverage and width need not match RF residual-based intervals. No chemistry or distribution shift.

Chemistry and QSAR evidence

Sheridan RP. (2012), “Three Useful Dimensions for Domain Applicability in QSAR Models Using Random Forest.” DOI 10.1021/ci300004n; PMID:22385389. ABSTRACT ONLY plus indexed excerpts; SI not located.
Endpoint, size, model and split: Proprietary QSAR endpoints; exact endpoints and sizes unavailable from accessed material. RF; CV plus compounds measured after model construction, but no verified scaffold split.
Uncertainty quantity; same model?: TREE_SD, predicted activity and nearest-training similarity: model disagreement, response-region difficulty and applicability distance. TREE_SD belongs to the activity RF.
Metric and recoverable result: Binned RMSE discrimination. Publisher excerpts report TREE_SD as the most discriminating single variable and the three-dimensional combination as more discriminating than any single variable.
Reported limitation or relevance: Detailed numerical tables and exact splitting could not be verified without full text. No QRF.

Sheridan RP. (2013), “Using Random Forest To Model the Domain Applicability of Another Random Forest Model.” DOI 10.1021/ci400482e; PMID:24152204. ABSTRACT ONLY/indexed excerpts; SI not located.
Endpoint, size, model and split: Ten QSAR datasets; exact endpoints and sizes inaccessible. RF activity model plus a second RF error model.
Uncertainty quantity; same model?: Learned unsigned-error model using seven AD variables; reduced model used TREE_SD and PREDICTED. The error model is separate, but its targets are errors from the activity RF.
Metric and recoverable result: Cross-validated ability to model unsigned error; exact ranking statistic and numerical performance not recoverable from the abstract.
Reported limitation or relevance: No QRF or verified scaffold split. Proper out-of-fold construction is central to avoiding optimistic error labels, but detailed nesting could not be checked.

Fang Y, Xu P, Yang J, Qin Y. (2018), “A quantile regression forest based method to predict drug response and assess prediction reliability.” DOI 10.1371/journal.pone.0205155; PMID:30289891. FULL TEXT; supporting data available.
Endpoint, size, model and split: CCLE activity area for 24 drugs, up to 479 cell lines; genomic information available for 947 lines. QRF with 15,000 trees; OOB evaluation.
Uncertainty quantity; same model?: Conditional drug-response distribution; QRF supplies both point and interval predictions. Not molecular-structure QSAR and not a separate frozen RF.
Metric and recoverable result: Pearson correlation for OOB point predictions, quantile loss and clinical examples of 95% intervals. No interval-width versus absolute-error ranking statistic was reported.
Reported limitation or relevance: “Shorter means more reliable” was largely interpretive; it was not established through risk–coverage or rank-correlation analysis.

Vasiloudis T, De Francisci Morales G, Boström H. (2019), “Quantifying Uncertainty in Online Regression Forests.” JMLR 20(155):1–35. Full text. No DOI verified. FULL TEXT; code/data repository available; no formal SI located.
Endpoint, size, model and split: Thirty streaming datasets, including a ChEMBL17 pseudo-pIC50 QSAR dataset; its exact size was not recovered. Online regression forests.
Uncertainty quantity; same model?: Online QRF conditional-response intervals and conformal residual intervals; same online forest.
Metric and recoverable result: Mean error rate, relative interval size and quantile loss; synthetic concept-drift experiments. No molecule-level absolute-error ranking.
Reported limitation or relevance: The chemical dataset was not evaluated with scaffold/temporal shift; concept-drift experiments were synthetic rather than chemical-series shifts.

Venkatraman V. (2021), “FP-ADMET: a compendium of fingerprint-based ADMET prediction models.” DOI 10.1186/s13321-021-00557-5; PMID:34583740. FULL TEXT; SI available.
Endpoint, size, model and split: More than 50 ADMET endpoints. Regression sets included human liver microsomal clearance n=5348, rat n=2166, mouse n=790, and a separate “intrinsic clearance” set n=244. RF, 500 trees; repeated random 80/20 splits and fivefold CV.
Uncertainty quantity; same model?: QRF 95% response intervals presented as stability/applicability information. The paper does not establish whether the QRF was exactly the same fitted forest as every point model.
Metric and recoverable result: Point-model R2, RMSE and MAE. For human liver microsomal clearance: calibration R2=0.51, RMSE 1.08, MAE 0.80; validation R2=0.56, RMSE 1.05, MAE 0.79. No interval coverage or width–error ranking result.
Reported limitation or relevance: Direct ADMET/QRF precedent, but not evidence for selection, scaffold shift or frozen-RF error ranking. The endpoint wording does not establish that every record corresponds exactly to your hLM CLint assay definition.

Dutschmann T-M, Baumann K. (2021), “Evaluating High-Variance Leaves as Uncertainty Measure for Random Forest Regression.” DOI 10.3390/molecules26216514; PMID:34770921. FULL TEXT; SI available.
Endpoint, size, model and split: 32 chemoinformatics regression datasets: mostly target activities plus TETRAH, Delaney solubility and FreeSolv; per-dataset molecule counts not recovered. RF; tenfold CV, not scaffold split.
Uncertainty quantity; same model?: Compared tree-prediction SD (SDEP) with high-variance leaves, a local training-response heterogeneity measure. Both belong to the point RF.
Metric and recoverable result: Confidence curves, error after removing uncertain predictions and AUCO50. Relative HVL/SDEP AUCO50: 97.4–136.9%, mean 114.9%, with RDKit descriptors; 80.1–129.0%, mean 108.7%, with ECFP. Lower is better, so HVL was not superior overall.
Reported limitation or relevance: Direct precedent for molecular retain/defer curves and local-response heterogeneity, but not QRF. MSE occasionally increased after removing supposedly uncertain predictions.

Xu Y, Liaw A, Sheridan RP, Svetnik V. (2024), “Development and Evaluation of Conformal Prediction Methods for Quantitative Structure–Activity Relationship.” DOI 10.1021/acsomega.4c02017; PMID:39005801. FULL TEXT; SI available.
Endpoint, size, model and split: 23 ChEMBL IC50 and 15 Merck/Kaggle QSAR datasets. RF, DNN and gradient boosting. Repeated random train/calibration/test splits; original Kaggle temporal test sets were explicitly excluded.
Uncertainty quantity; same model?: ACE conformal intervals scale residuals using ensemble/tree SD. For RF, the raw score belongs to the activity RF; conformal calibration estimates residual magnitude.
Metric and recoverable result: Marginal coverage error, mean width and conditional coverage by width quintile. No molecule-level Spearman correlation or scaffold-shift risk–coverage result was reported.
Reported limitation or relevance: Demonstrates RF interval calibration in random-split QSAR, not raw QRF width or covariate shift. Authors explicitly note exchangeability limits.

Parrondo-Pizarro R, Lanini J, Rodríguez-Pérez R. (2026), “Uncertainty Quantification in Molecular Machine Learning for Property Predictions under Data Shifts.” DOI 10.1021/acs.jcim.5c02381; PMID:41533656. FULL TEXT; SI identified and available.
Endpoint, size, model and split: hLM CLint: in-house 137,029/12,755/19,967 train/calibration/test; public 1544/925/616. GNN ensembles. In-house temporal split; public scaffold-grouped 50/30/20 split.
Uncertainty quantity; same model?: Latent 5-NN Manhattan distance, ensemble variance and RF error models using predicted response, distance and ensemble variance. No QRF.
Metric and recoverable result: Spearman correlation with absolute error, confidence curves, AUC difference and performance drop. Across endpoints, distance SRCC ranged −0.08–0.20 and ensemble variance −0.07–0.26. Public hLM error-model SRCC was 0.16. Ensemble variance exceeded distance for hLM in both sources.
Reported limitation or relevance: Direct hLM shifted-distribution ranking evidence, but correlations were modest and no method won universally. The accessible methods state that training and calibration errors were error-model labels, but I could not verify an explicit nested/out-of-fold generation procedure for every training error; leakage protection therefore cannot be certified from the text inspected.

von Borries K, Beckwith KV, Goodman JM, Chiu WA, Jolliet O, Fantke P. (2026), “Uncertainty-aware machine learning to predict non-cancer human toxicity for the global chemicals market.” DOI 10.1038/s41467-025-67374-4; PMID:41501044. FULL TEXT; SI/source data available.
Endpoint, size, model and split: Reproductive/developmental and general non-cancer points of departure; 2357 and approximately 1845 chemicals in the principal Results description. Tenfold CV, not scaffold shift.
Uncertainty quantity; same model?: QRF was the core learner inside uncertainty-aware conformalized quantile regression. This is conformalized uncertainty, not raw QRF width.
Metric and recoverable result: RMSE, coverage/calibration, ENCE and binned RMU–RMSE association. CP RMSE was 0.63/0.73; ENCE 16.6%/13.4%.
Reported limitation or relevance: Shows that a QRF-based conformal method can provide useful chemical intervals, but does not isolate raw Q90−Q10 or rank errors of a separate RF.

Answers to the six questions

1. Direct precedent for Q90−Q10 ranking error of a frozen RF in chemistry?

No located direct precedent.

FP-ADMET uses QRF intervals for ADMET—including human liver microsomal clearance—but reports point-prediction metrics and descriptive interval widths, not absolute-error ranking. Fang et al. similarly uses intervals from the same QRF, not a separate frozen RF.

2. Direct precedent under scaffold shift?

No.

Parrondo-Pizarro et al. provides direct scaffold-shift uncertainty-ranking evidence, but for GNN ensemble variance, distance and learned error models—not QRF. Other chemical QRF studies used OOB, random or ordinary CV evaluation.

3. Direct precedent for hLM CLint?

No direct ranking precedent.

There are two adjacent results:

FP-ADMET: QRF intervals for “human liver microsomal clearance,” but no error-ranking analysis and no scaffold shift.
Parrondo-Pizarro et al.: hLM CLint error ranking under temporal/scaffold shift, but no RF or QRF.

Neither validates your complete proposition.

4. Evidence that QRF response width is superior to tree-SD, distance or learned-error models?

None located.

No molecular study was found that compares raw QRF width against all—or even a well-controlled subset—of those methods using matched point predictions and scaffold-shift risk–coverage evaluation.

The available comparative evidence instead supports:

TREE_SD as useful in Sheridan’s QSAR studies;
tree-SD outperforming high-variance leaves on average in Dutschmann and Baumann;
weak, endpoint-dependent performance for distance and ensemble variance under hLM shift;
learned error models often improving rankings in Parrondo-Pizarro et al., although public hLM SRCC remained only 0.16.

These findings do not prove that those alternatives would outperform your particular QRF score.

5. Is Lu and Hardin conceptually closer to RF prediction error?

Yes.

Lu and Hardin explicitly estimate:

F_E(e|x), E=Y−f_hat_RF(X),

using locally weighted OOB residuals from the same RF. This can represent:

local residual scale;
systematic over- or underprediction;
conditional MSPE;
asymmetric residual quantiles.

Raw QRF instead estimates F_Y(y|x). Its width can describe residual spread because widths are invariant to translation, but it does not encode where the frozen RF prediction lies within that distribution. Therefore it cannot by itself capture local frozen-RF bias.

Lu and Hardin is consequently closer to prediction-error uncertainty, while raw QRF width is primarily response-distribution uncertainty.

6. Empirically known versus merely plausible

Empirically demonstrated

QRF can estimate conditional response quantiles under its stated assumptions.
QRF widths vary with local response heterogeneity.
QRF intervals can under-cover or become inefficient.
QRF has been used for QSAR/ADMET response intervals.
RF tree-SD, local leaf heterogeneity, distance and learned error models can provide useful error rankings in some molecular datasets.
Confidence/abstention-style curves have direct molecular precedent.
UQ rankings under hLM scaffold and temporal shift can be weak and endpoint-dependent.

Methodologically plausible, but not demonstrated for v3A

Q90−Q10 may rank frozen-RF error when conditional response spread is associated with residual magnitude.
Similar RF/QRF neighborhoods may allow width to transfer between models.
Wider response distributions may identify noisy assay regions where absolute error is larger.

Not established

That this association survives scaffold shift.
That it holds for hLM CLint.
That it captures RF model bias or unfamiliarity.
That it is better than tree-SD, similarity, effective support or learned error models.
That raw QRF intervals are calibrated for your frozen RF.

Consequence for frozen v3A

No protocol change is warranted from this audit if v3A states:

Q90−Q10 is a candidate uncertainty ranking score whose utility will be determined empirically through within-fold scaffold-grouped retain/defer evaluation.

The literature does require cautious terminology. A positive v3A result would support the dataset- and protocol-specific statement that QRF response width was associated with frozen-RF error and improved selective prediction retrospectively. It would not establish calibrated prediction intervals, causal assay-triage benefit, epistemic uncertainty estimation or generalization to new prospective chemistry.

FUTURE STUDY — NOT A V3A CHANGE

Lu–Hardin local OOB residual distributions, conformalized RF intervals and independently nested learned-error models are conceptually stronger estimators of prediction-error distributions. That is useful context for a future matched benchmark; it is not evidence requiring their addition to frozen v3A.

Final evidence classification

DIRECTLY SUPPORTED

QRF estimates conditional response quantiles and response spread.
Lu–Hardin targets the same RF’s conditional residual/error distribution.
RF tree-SD and confidence/abstention curves have QSAR precedent.
hLM CLint uncertainty ranking under temporal and scaffold shift has been studied with distance, ensemble variance and learned error models.

INDIRECTLY SUPPORTED

QRF width can serve as a conditional error-scale proxy.
Response heterogeneity may sometimes track absolute prediction error.
QRF-derived intervals have ADMET and human liver microsomal clearance precedent.
Retain/defer evaluation is methodologically precedented in molecular regression.

NOT YET DEMONSTRATED

Q90−Q10 ranks absolute error of a separate frozen RF in chemistry.
The same claim under scaffold shift.
The same claim for hLM CLint.
Superiority over tree-SD, similarity/distance, effective support or learned error models.
Calibration of raw QRF intervals for the frozen RF.
Prospective assay-triage benefit.

CONTRADICTED

Q90−Q10 is a central 90% interval—it is central 80%.
Raw QRF width necessarily measures epistemic uncertainty or chemical unfamiliarity.
Width alone captures local frozen-RF bias.
Raw QRF quantiles automatically provide finite-sample nominal coverage, particularly under scaffold shift.
```
