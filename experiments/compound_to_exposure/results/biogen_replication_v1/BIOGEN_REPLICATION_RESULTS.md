# Biogen Independent Replication Results

## RESULT

### Primary Cohort (N=3087)
The primary independent replication on the full Biogen dataset evaluated the predictive performance of models trained entirely on Biogen data using the exact frozen methodology from the AZ primary track. The metric outcomes are in native log units:

| Cell | MAE | RMSE | Spearman $\rho$ |
| :--- | :--- | :--- | :--- |
| **Mean Baseline** | 0.5368 | 0.6241 | -0.0320 |
| **Median Baseline** | 0.5316 | 0.6349 | -0.0234 |
| **Ridge — Descriptors** | 0.4384 | 0.5385 | 0.5492 |
| **Ridge — Morgan** | 0.4266 | 0.5350 | 0.5413 |
| **RF — Descriptors** | 0.4173 | 0.5227 | 0.5512 |
| **RF — Morgan** | 0.4497 | 0.5464 | 0.4853 |

*Applicability Domain (Spearman correlation between absolute OOF error and maximum Tanimoto similarity to outer training fold):*
- Ridge Descriptors: $\rho = -0.0013$
- Ridge Morgan: $\rho = -0.0631$
- RF Descriptors: $\rho = -0.0456$
- RF Morgan: $\rho = -0.0719$

### Sensitivity Cohort (N=2129)
The sensitivity analysis removed exactly 958 records possessing a target value of 0.675686709. Outer-folds were strictly inherited.

| Cell | MAE | RMSE | Spearman $\rho$ |
| :--- | :--- | :--- | :--- |
| **Mean Baseline** | 0.4519 | 0.5421 | -0.0390 |
| **Median Baseline** | 0.4504 | 0.5442 | -0.0383 |
| **Ridge — Descriptors** | 0.4135 | 0.5050 | 0.3785 |
| **Ridge — Morgan** | 0.4154 | 0.5167 | 0.3845 |
| **RF — Descriptors** | 0.4012 | 0.4922 | 0.4002 |
| **RF — Morgan** | 0.4154 | 0.5019 | 0.3439 |

*Applicability Domain:*
- Ridge Descriptors: $\rho = -0.0063$
- Ridge Morgan: $\rho = -0.0710$
- RF Descriptors: $\rho = -0.0260$
- RF Morgan: $\rho = -0.0631$

## INTERPRETATION

### Scientific Sanity Checks & AZ Primary Comparison
The Biogen independent replication demonstrates that the structural feature extraction and model matrix perform comparably on a different dataset. 
- **Outperforming baselines**: All four learned regression cells outperformed the trivial mean and median baselines in terms of absolute and squared log errors in both the primary and sensitivity cohorts.
- **Morgan vs Descriptors**: In the AZ primary track, Morgan fingerprints consistently provided an edge in signal over the 7 physicochemical descriptors. In this Biogen dataset, however, descriptors slightly outperformed Morgan fingerprints (e.g. Ridge Descriptors $\rho \approx 0.55$ vs Ridge Morgan $\rho \approx 0.54$; RF Descriptors $\rho \approx 0.55$ vs RF Morgan $\rho \approx 0.49$). This inversion is interesting and indicates that the 7 descriptors provide highly robust baseline predictive value, capturing substantial clearance mechanisms across datasets.
- **Ridge vs RF**: Ridge and Random Forest showed relatively similar signal magnitude when using descriptors (Spearman ~0.55 for both). Random Forest paired with Morgan dropped off significantly ($\rho \approx 0.49$), whereas Ridge handled the Morgan fingerprint sparsity more robustly, replicating the qualitative pattern observed in the primary AZ track.
- **Sensitivity vs Primary**: The exclusion of the 958 pileup records systematically reduced absolute errors (MAE, RMSE) simply by shrinking the target variance, but correspondingly restricted the dynamic range over which ranking could be evaluated, resulting in lower Spearman correlations (dropping from ~0.55 to ~0.40). The broad pattern (models beat baselines, Ridge handles Morgan better than RF) holds across both cohorts. 
- **Applicability Domain**: Higher training-set chemical similarity is descriptively associated with lower absolute error, although the correlations are extremely weak ($\rho$ between -0.04 and -0.07 for Morgan and RF models). This correctly tracks in the negative direction (higher similarity -> smaller absolute error).

## LIMITATIONS

- **Log Base**: The Biogen recorded log base remains UNRESOLVED. MAE and RMSE are evaluated strictly as native-log-unit metrics within the dataset and cannot be mathematically converted into a fold-error metric or compared directly to AZ MAE/RMSE magnitude.
- **Independent Validation Only**: This tracks represents an independent-dataset replication of the *modelling pattern*, it is **NOT** an external validation of an AZ-trained model. No AZ data entered the Biogen workflow.
- **Censoring**: The 958 records piled at 0.675686709 are retained in the primary track because they are NOT proven to be censored limits. The sensitivity analysis is purely an artificial exclusion experiment, not an endorsement of censoring.
