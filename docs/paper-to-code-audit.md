# Published Paper-to-Code Audit

**Paper:** Venkata Velavarthipati (2026), *Proactive Cloud Elasticity via XGBoost Predictive Scaling*  
**Journal:** East African Journal of Information Technology, 9(2), pp. 418–427  
**DOI:** https://doi.org/10.37284/eajit.9.2.5931  
**Audit status:** Initial reproduction run completed and documented; local tests and experiment execution were reported by the repository owner. Exact numerical reproduction has not been achieved.

This audit maps the published paper's stated experimental design to the repository implementation and records validation findings. The implementation has been run locally, but the paper's published numerical results have not been exactly reproduced.

## Current repository baseline

The current `simulate.py`:
- Generates a deterministic synthetic demand trace or loads `demand_units` from CSV.
- Compares a reactive capacity calculation with a simple moving-average calculation.
- Reports sample count, under-capacity demand proxies, and provisioned-capacity proxies.
- Makes no cloud API calls.

The `paper_repro/` package contains four synthetic workload generators, time-ordered features, an XGBoost ensemble, confidence/OOD gating with reactive fallback, controller simulation, metrics, CSV export, and plotting. Automated tests and a GitHub Actions workflow are included. The repository owner reports that all 24 tests pass locally and that the experiment runs successfully, generating per-seed metrics, summary metrics, plots, and gate diagnostics. Exact numerical reproduction remains unverified. The existing sample CSV is still an illustrative 120-row workload and is not the paper's seven-day experimental dataset.

**Historical checklist note:** The checklist immediately below was drafted before implementation and is retained as a record of the original plan. Its “Missing” statuses and “Planned evidence” column are historical and should not be read as the current implementation status; the executed-run findings later in this document describe the current implementation.

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



## Audit findings from the first executed reproduction attempt

The implementation has now been run locally by the repository owner: 24 tests pass, and the experiment generates per-seed metrics, summary metrics, plots, and gate diagnostics. Exact reproduction is **not** achieved.

| Area | What the paper states | What the current code does | Assessment |
|---|---|---|---|
| Workload timing | Training/calibration follow a normal pattern; test contains shifted and amplified demand | Uses a normal daily sinusoid plus seeded Gaussian noise; distribution shift applies `demand * 1.45 + 12` from the test boundary | Qualitatively aligned, but the exact shift magnitude and generator are not specified by the paper and remain reconstruction choices |
| Train/calibration/test split | Gate thresholds use pre-test data only | 60% train, 20% calibration, final 20% test; shifted workload starts at the test boundary | Consistent with the stated high-level design; exact fractions are not specified in the paper |
| Features | Current telemetry, multiple lags including 24-hour lag, rolling statistics, rate of change, calendar features | Includes current, short lags, 24-hour lag, rolling mean/variance, first difference, sine/cosine calendar phase | Broadly aligned, but window sizes and full feature definitions are implementation choices |
| Ensemble uncertainty | Relative ensemble uncertainty/model disagreement | Relative population standard deviation divided by absolute ensemble mean | Plausible operationalization; exact formula is not fully specified in the paper |
| OOD score | Feature-distance OOD score | RMS standardized Euclidean distance from training-feature means/scales | Plausible operationalization; exact distance and normalization are not specified in the paper |
| Threshold calibration | Calibrated on pre-test data only | 90th percentile of calibration uncertainty and 99th percentile of calibration distance | Uses pre-test data only, but percentile choices are not stated in the paper |
| Reactive timing | 15-minute actuation delay | Demand observed at time t schedules capacity at t+3 samples | Matches the stated delay at a high level |
| Predictive timing | 15-minute forecast; five-minute predictive actuation delay | Forecast target is t+3; predicted capacity is scheduled for t+1 | Needs an explicit control interpretation: the forecast target and action arrival are different times, which is plausible but should be validated against the paper's intended semantics |
| Confidence-gated fallback | Failed gate returns control to reactive path | Rejected predictions use observed demand and the reactive three-step delay | Broadly aligned with the described fallback behavior |
| Capacity calculation | 90% target utilization | Requested capacity is `ceil(demand / 0.90)`; SLO is evaluated against provisioned units versus demand | Reasonable interpretation, but capacity units and rounding semantics are not fully specified in the paper |

### Diagnostic evidence

For the distribution-shift scenario, the current run shows pre-shift forecast MAE around 2.60–2.77, increasing to around 31.36–32.55 after the shift. Pre-shift gate acceptance is around 88–89%, while post-shift acceptance is around 0–2%. Most post-shift rejection is due to both the uncertainty and OOD tests failing together.

This demonstrates that the current implementation detects its deliberately strong synthetic shift. It does **not** establish that the gate is correctly calibrated to reproduce the paper's reported 51% fallback rate.

### Correct next steps

1. Keep the current run as the baseline; do not tune thresholds to force the reported values.
2. Add a sensitivity experiment for shift magnitude and baseline offset, and report the resulting forecast error, gate rejection, and SLO metrics. Treat it as a robustness experiment, not as reproduction.
3. Make the action timeline explicit in a unit test: at each sample, log forecast target time, decision time, capacity-change arrival time, and demand interval used for SLO evaluation.
4. Search for the original simulation source/configuration, if it exists. The article does not specify enough detail to uniquely infer the exact synthetic workload formula, uncertainty formula, OOD distance, or threshold percentiles from the text alone.
5. After resolving those details, rerun the full three-seed experiment and compare with Table 2.

No numerical reference values from Table 2 should be hard-coded into the simulator.

## Source

Velavarthipati, V. (2026). Proactive Cloud Elasticity via XGBoost Predictive Scaling. *East African Journal of Information Technology, 9*(2), 418–427. https://doi.org/10.37284/eajit.9.2.5931
