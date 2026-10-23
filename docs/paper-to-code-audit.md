# Published Paper-to-Code Audit

**Paper:** Venkata Velavarthipati (2026), *Proactive Cloud Elasticity via XGBoost Predictive Scaling*  
**Journal:** East African Journal of Information Technology, 9(2), pp. 418–427  
**DOI:** https://doi.org/10.37284/eajit.9.2.5931  
**Audit status:** Initial repository review; no reproduction run has been performed yet.

This checklist maps the published paper's stated experimental design to the current repository. It is an implementation plan, not a claim that the paper's results have already been reproduced.

## Current repository baseline

The current `simulate.py`:
- Generates a deterministic synthetic demand trace or loads `demand_units` from CSV.
- Compares a reactive capacity calculation with a simple moving-average calculation.
- Reports sample count, under-capacity demand proxies, and provisioned-capacity proxies.
- Makes no cloud API calls.

The new `paper_repro/` package now contains an initial implementation of four synthetic workload generators, time-ordered features, an XGBoost ensemble, confidence/OOD gating with reactive fallback, controller simulation, metrics, CSV export, and plotting. Automated tests and a GitHub Actions workflow have been added. These changes have been committed on the research branch, but the experiment and tests have **not yet been executed in a verified runtime**. Exact numerical reproduction remains unverified. The existing sample CSV is still an illustrative 120-row workload and is not the paper's seven-day experimental dataset.

## Paper-to-code checklist

Status meanings: **Missing** = not present in the reviewed current implementation; **Verify** = requires specification or validation during implementation.

| Requirement from the paper | Paper specification | Current status | Planned evidence |
|---|---|---|---|
| Simulation time step | Five-minute telemetry interval | Missing | Configurable, documented simulation clock |
| Forecast horizon | 15 minutes | Missing | Explicit horizon and tests for correct time alignment |
| Duration | Seven days | Missing | 7-day workload per experimental run |
| Target utilization | 90% | Missing | Named configuration parameter and unit tests |
| Random seeds | 11, 22, 33 | Missing | Each seed recorded in machine-readable output |
| Workload: predictable | Recurring daily demand with moderate noise | Missing | Deterministic generator and scenario test |
| Workload: bimodal | Two recurring daily demand peaks | Missing | Deterministic generator and scenario test |
| Workload: rapid spike | Short bursts over a daily pattern | Missing | Deterministic generator and scenario test |
| Workload: distribution shift | Test period shifts/amplifies demand relative to training/calibration | Missing | Explicit train/calibration/test boundaries and test |
| Reactive controller | Observed demand with 15-minute actuation delay | Missing | Controller implementation and timing tests |
| Ungated XGBoost | Forecast-driven scaling with five-minute predictive actuation delay | Missing | Trained forecast model, configuration, timing tests |
| Confidence-gated XGBoost | Use predictive path only when gate passes; otherwise reactive fallback | Missing | Gate and fallback tests, including distribution shift |
| Forecast features | Current telemetry, lag values including 24-hour lag, rolling statistics, calendar features | Missing | Feature definitions and feature-generation tests |
| Forecast uncertainty | Ensemble disagreement | Missing | Reproducible uncertainty calculation |
| Distribution-shift signal | Feature-distance OOD proxy | Missing | Documented distance method and tests |
| Gate calibration | Thresholds calibrated on pre-test data only | Missing | Explicit data split; tests preventing test-data leakage |
| SLO violation | Percentage of test intervals where provisioned capacity is below actual demand | Missing | Metric definition, tests, and per-run results |
| Capacity excess | Excess provision above actual demand | Missing | Metric definition and tests |
| Forecast metrics | R², MAE, RMSE retained in machine-readable results | Missing | Per-workload/per-seed metrics output |
| Repeated runs | Three independent seeds; report mean and approximate 95% interval for SLO violation | Missing | Aggregation script with documented interval calculation |
| Figures and tables | Regenerate results from experiment outputs | Missing | Plot/table generation from saved results, not hard-coded values |
| Reproducible environment | Dependencies, model settings, seeds, delays, and commands documented | Partial | Pinned or bounded dependencies, configuration, run instructions |
| Automated tests | Unit tests for model, gate, timing, metrics, and reproducibility | Partial | Expanded tests while retaining existing baseline tests |

## Published reference results to compare against

The paper's Table 2 reports the following mean SLO violation percentages across three seeds for the 90% target-utilization sensitivity run:

| Workload | Reactive | Ungated XGBoost | Confidence-gated XGBoost |
|---|---:|---:|---:|
| Predictable | 2.28% | 0.19% | 1.74% |
| Bimodal | 6.56% | 0.81% | 1.12% |
| Rapid spike | 5.98% | 1.16% | 1.00% |
| Distribution shift | 2.39% | 24.11% | 2.31% |

These values are **reference targets for investigation**, not values to hard-code or force the implementation to match. The current repository has not reproduced them. Any difference must be reported and investigated.

## Implementation sequence

1. Preserve the existing `simulate.py` starter behavior and its tests as the baseline.
2. Add a separate experiment package for configuration, workload generation, features, controllers, confidence gating, and metrics.
3. Define and test time-step, forecast-horizon, and actuation-delay semantics before comparing controllers.
4. Train and evaluate XGBoost using a time-aware split; calibrate the gate without using test-period outcomes.
5. Run every workload with seeds 11, 22, and 33 and save raw per-run results.
6. Aggregate metrics and generate figures from those saved results.
7. Document discrepancies, limitations, and exact commands needed to reproduce the outputs.

## Research-integrity rules

- Label workloads as synthetic unless a public or production trace is actually used.
- Do not describe simulation outcomes as production measurements.
- Do not hard-code the paper's published percentages into experiment outputs.
- Keep training, calibration, and test data boundaries explicit to avoid leakage.
- Preserve the current baseline and make the paper-reproduction implementation separately testable.
- If the reported values cannot be reproduced, document the implementation details and likely causes rather than silently tuning to the desired answer.

## Source

Velavarthipati, V. (2026). Proactive Cloud Elasticity via XGBoost Predictive Scaling. *East African Journal of Information Technology, 9*(2), 418–427. https://doi.org/10.37284/eajit.9.2.5931
