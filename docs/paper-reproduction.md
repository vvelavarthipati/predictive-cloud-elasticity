# Reproducing the EAJIT predictive-scaling experiment

This implementation is a new, explicit experiment implementation based on the paper's stated design. It is not yet verified to reproduce the exact published numerical results.

## Environment

Python 3.9+ is recommended. Install the model dependency:

```bash
python -m pip install -r requirements.txt
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Run the experiment

From the repository root:

```bash
python -m paper_repro.run_experiment --output-dir results
```

The experiment writes:
- `results/per_seed_results.csv`: one row per scenario, seed, and controller.
- `results/summary_results.csv`: mean metrics and approximate 95% normal intervals across seeds.
- `results/gate_diagnostics.csv`: per-scenario/seed gate thresholds, forecast MAE by calibration/test period, and counts/percentages rejected for uncertainty, OOD distance, both, or neither.
- `results/experiment_config.json`: configuration used for the run.

The generated `results/` files are experimental outputs and should be reviewed before committing or citing them.

## Implemented design

- Five-minute telemetry interval and seven-day synthetic traces.
- 15-minute forecasting horizon.
- Four deterministic, seed-controlled synthetic workload regimes.
- Reactive controller with a three-step actuation delay.
- XGBoost ensemble with one-step predictive actuation delay.
- Confidence-gated predictive controller with reactive fallback.
- Calibration thresholds derived from pre-test calibration samples only.
- SLO violation (provisioned capacity below actual demand), capacity excess, fallback, MAE, RMSE, and R² metrics.

## Important implementation assumptions

The paper describes ensemble disagreement and a feature-distance OOD proxy but does not fully specify every implementation detail needed to reproduce them exactly. This implementation uses relative ensemble standard deviation for uncertainty, standardized Euclidean feature distance for OOD, and calibration-set quantiles for thresholds. These choices are transparent operationalizations and may produce results different from the published table.

Capacity is an abstract simulation unit. The simulator is not connected to AWS, Kubernetes, or any production environment. Workloads are synthetic and do not represent production telemetry.

The controller starts test evaluation from capacity based on the last pre-test observation, rather than using the first test demand to initialize capacity. The gate diagnostic labels the calibration period before the test boundary and the test period after it; for the distribution-shift scenario, that boundary is also the synthetic shift point. Scaling decisions are queued and applied after their configured delay; gated fallback decisions use the reactive delay. SLO violation is evaluated as provisioned capacity below actual demand, matching the paper's stated definition. Target utilization affects the capacity requested by a controller, not the SLO comparison threshold.

The approximate 95% interval uses a normal multiplier (1.96) across the configured seed results. With only three seeds, this interval is imprecise; expand repeated runs for stronger statistical conclusions.

Do not hard-code the paper's reported percentages into outputs. Compare actual results to the article's Table 2, investigate discrepancies, and document them.
