# Primary Modelling Results

**Direct Observation & Calculated Metrics Only. See limitations for caveats.**

## Selected Hyperparameters by Fold
- **Ridge (descriptors) Fold 0**: alpha=0.1 
- **RandomForestRegressor (descriptors) Fold 0**: max_depth=None 
- **Ridge (Morgan) Fold 0**: alpha=10.0 
- **RandomForestRegressor (Morgan) Fold 0**: max_depth=None 
- **Ridge (descriptors) Fold 1**: alpha=0.1 
- **RandomForestRegressor (descriptors) Fold 1**: max_depth=None 
- **Ridge (Morgan) Fold 1**: alpha=10.0 
- **RandomForestRegressor (Morgan) Fold 1**: max_depth=None 
- **Ridge (descriptors) Fold 2**: alpha=0.1 
- **RandomForestRegressor (descriptors) Fold 2**: max_depth=None 
- **Ridge (Morgan) Fold 2**: alpha=10.0 
- **RandomForestRegressor (Morgan) Fold 2**: max_depth=None 
- **Ridge (descriptors) Fold 3**: alpha=10.0 
- **RandomForestRegressor (descriptors) Fold 3**: max_depth=None 
- **Ridge (Morgan) Fold 3**: alpha=10.0 
- **RandomForestRegressor (Morgan) Fold 3**: max_depth=None 
- **Ridge (descriptors) Fold 4**: alpha=10.0 
- **RandomForestRegressor (descriptors) Fold 4**: max_depth=10 
- **Ridge (Morgan) Fold 4**: alpha=10.0 
- **RandomForestRegressor (Morgan) Fold 4**: max_depth=None 
- **LogisticRegression (descriptors) Fold 0**: C=1.0 
- **RandomForestClassifier (descriptors) Fold 0**: max_depth=None 
- **LogisticRegression (Morgan) Fold 0**: C=0.1 
- **RandomForestClassifier (Morgan) Fold 0**: max_depth=10 
- **LogisticRegression (descriptors) Fold 1**: C=1.0 
- **RandomForestClassifier (descriptors) Fold 1**: max_depth=10 
- **LogisticRegression (Morgan) Fold 1**: C=1.0 
- **RandomForestClassifier (Morgan) Fold 1**: max_depth=None 
- **LogisticRegression (descriptors) Fold 2**: C=0.1 
- **RandomForestClassifier (descriptors) Fold 2**: max_depth=10 
- **LogisticRegression (Morgan) Fold 2**: C=0.1 
- **RandomForestClassifier (Morgan) Fold 2**: max_depth=None 
- **LogisticRegression (descriptors) Fold 3**: C=10.0 
- **RandomForestClassifier (descriptors) Fold 3**: max_depth=10 
- **LogisticRegression (Morgan) Fold 3**: C=0.1 
- **RandomForestClassifier (Morgan) Fold 3**: max_depth=10 
- **LogisticRegression (descriptors) Fold 4**: C=0.1 
- **RandomForestClassifier (descriptors) Fold 4**: max_depth=10 
- **LogisticRegression (Morgan) Fold 4**: C=0.1 
- **RandomForestClassifier (Morgan) Fold 4**: max_depth=10 

## Regression Metrics (Primary N=744)
| Model | Rep | MAE | RMSE | Spearman ρ | R² | Frac <= log10(2) |
|---|---|---|---|---|---|---|
| RandomForestRegressor | Morgan | 0.326 | 0.398 | 0.417 | 0.184 | 0.512 |
| RandomForestRegressor | descriptors | 0.339 | 0.413 | 0.362 | 0.124 | 0.481 |
| Ridge | Morgan | 0.334 | 0.412 | 0.391 | 0.128 | 0.507 |
| Ridge | descriptors | 0.371 | 0.440 | 0.120 | 0.002 | 0.437 |
| mean | baseline | 0.376 | 0.442 | -0.089 | -0.005 | 0.429 |
| median | baseline | 0.376 | 0.442 | -0.089 | -0.007 | 0.423 |

## Classifier Metrics (N=1102)
| Model | Rep | Macro-F1 | Balanced Acc | MCC | Precision (B/I/A) | Recall (B/I/A) |
|---|---|---|---|---|---|---|
| LogisticRegression | Morgan | 0.477 | 0.481 | 0.210 | 0.454/0.727/0.239 | 0.489/0.703/0.250 |
| LogisticRegression | descriptors | 0.340 | 0.445 | 0.077 | 0.304/0.685/0.137 | 0.474/0.313/0.548 |
| RandomForestClassifier | Morgan | 0.481 | 0.479 | 0.217 | 0.478/0.727/0.244 | 0.442/0.746/0.250 |
| RandomForestClassifier | descriptors | 0.404 | 0.404 | 0.135 | 0.394/0.715/0.101 | 0.398/0.707/0.107 |
| majority | baseline | 0.269 | 0.333 | 0.000 | 0.000/0.675/0.000 | 0.000/1.000/0.000 |

## Tail Ordering Scores
| Model | Rep | Tail | N Eligible | Score |
|---|---|---|---|---|
| RandomForestRegressor | Morgan | Lower | 40771 | 0.693 |
| RandomForestRegressor | Morgan | Upper | 12499 | 0.687 |
| RandomForestRegressor | descriptors | Lower | 40771 | 0.648 |
| RandomForestRegressor | descriptors | Upper | 12499 | 0.574 |
| Ridge | Morgan | Lower | 40771 | 0.716 |
| Ridge | Morgan | Upper | 12499 | 0.645 |
| Ridge | descriptors | Lower | 40771 | 0.564 |
| Ridge | descriptors | Upper | 12499 | 0.534 |

## Applicability Domain (Spearman ρ: Error vs Max Train Tanimoto)
- **Ridge (descriptors)**: -0.061
- **Ridge (Morgan)**: -0.230
- **RandomForestRegressor (descriptors)**: -0.127
- **RandomForestRegressor (Morgan)**: -0.166

## Sensitivity S1 (Regression N=731, Classifier N=1089)
| Model | Rep | MAE (S1) | Macro-F1 (S1) |
|---|---|---|---|
| RandomForestRegressor | Morgan | 0.322 | 0.489 |
| RandomForestRegressor | descriptors | 0.337 | 0.415 |
| Ridge | Morgan | 0.333 | 0.477 |
| Ridge | descriptors | 0.363 | 0.336 |
| mean | baseline | 0.368 | nan |
| median | baseline | 0.368 | nan |

## Limitations & Interpretation
* **Calculated Metric vs Clinical PK**: These metrics evaluate strictly 2D mathematical ranking on in vitro microsomal stability (CLint). They do NOT make any clinical human clearance prediction or patient exposure prediction.
* **Exact Latent Values**: We do not infer or claim exact latent values for explicit censored observations.
