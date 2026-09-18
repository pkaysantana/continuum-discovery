# V2 Protocol Amendment 001 — Biogen B1/B2 Selection Relationship

## Timing and provenance

This amendment is made after the original v2 protocol freeze but before any real AstraZeneca or Biogen v2 model fitting, prediction, holdout evaluation or predictive-performance calculation.

The original frozen protocol did not explicitly specify whether Biogen B2 should independently rerun P1–P4 model selection or reuse the model specification selected by B1.

This amendment resolves that ambiguity prospectively.

It does not modify the AstraZeneca primary analysis, censored-tail analysis, sensitivities, HLM–HH analysis or TDC disposition.

## Frozen clarification

### B1

B1 is the primary exploratory Biogen variant using all 3,087 populated observations as shipped.

B1 performs the full frozen P1–P4 model-selection procedure using its own Biogen CV pool and inherited frozen modelling rules.

The B1 selection produces one fixed:
* pipeline ID;
* representation;
* model family;
* hyperparameter configuration.

### B2

B2 is a predetermined floor-exclusion sensitivity containing the 2,129 observations remaining after removal of the 958 observations at the observed minimum.

B2 must not independently rerun P1–P4 model selection.

Instead:
* B2 inherits every retained molecule's B1 structural partition and fold assignment;
* B2 does not regenerate, rebalance or optimise a partition;
* B2 reuses the pipeline family, representation and hyperparameters selected by B1;
* that fixed configuration is refitted using only eligible B2 training observations;
* B2 final evaluation uses only retained B2 observations that were already assigned to the B1 holdout;
* if fold-level B2 diagnostics are produced, the fixed B1-selected configuration is refitted within each inherited B2 training fold without model reselection.

B2 must not:
* trigger P1–P4 reselection;
* change representation;
* change hyperparameters;
* alter the B1 result;
* influence AstraZeneca model selection;
* be preferred or discarded based on comparative performance.

## Rationale

B2 is intended as a sensitivity analysis to the removal of the 958 floor-valued observations.

Fixing the model specification to the one selected by B1 isolates the effect of the data-exclusion rule more cleanly than allowing B2 to introduce an additional model-selection decision.

Both B1 and B2 remain exploratory and must be reported regardless of performance.

## Status

AMENDMENT_STATUS: FROZEN_BEFORE_V2_EXECUTION
