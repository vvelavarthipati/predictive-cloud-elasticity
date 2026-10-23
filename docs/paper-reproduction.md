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
- SLO violation, capacity excess, fallback, MAE, RMSE, and R² metrics.

## Important implementation assumptions

The paper describes ensemble disagreement and a feature-distance OOD proxy but does not fully specify every implementation detail needed to reproduce them exactly. This implementation uses relative ensemble standard deviation for uncertainty, standardized Euclidean feature distance for OOD, and calibration-set quantiles for thresholds. These choices are transparent operationalizations and may produce results different from the published table.

Capacity is an abstract simulation unit. The simulator is not connected to AWS, Kubernetes, or any production environment. Workloads are synthetic and do not represent production telemetry.

The approximate 95% interval uses a normal multiplier (1.96) across the configured seed results. With only three seeds, this interval is imprecise; expand repeated runs for stronger statistical conclusions.

Do not hard-code the paper's reported percentages into outputs. Compare actual results to the article's Table 2, investigate discrepancies, and document them.
