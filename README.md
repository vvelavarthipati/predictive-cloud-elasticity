# Predictive Cloud Elasticity

A small Python research prototype for exploring predictive cloud autoscaling using synthetic workloads and simplified capacity metrics.

## Existing starter simulation

The original starter remains available:
- `simulate.py` — synthetic workload generator, CSV loader, and reactive-vs-moving-average comparison.
- `data/sample_workload.csv` — 120 illustrative synthetic samples.
- `tests/test_simulate.py` — starter unit tests.

Run it with:

```bash
python simulate.py
python simulate.py data/sample_workload.csv
python -m unittest discover -s tests -v
```

The starter's moving-average method is not the XGBoost method described in the published paper. Its simplified capacity proxies are not direct measurements of latency, availability, cloud cost, or production utilization.

## Published-paper reproduction experiment

The `paper_repro/` package is being developed as a separate experiment implementation for:

Velavarthipati, V. (2026). *Proactive Cloud Elasticity via XGBoost Predictive Scaling*. East African Journal of Information Technology, 9(2), 418–427. https://doi.org/10.37284/eajit.9.2.5931

Read the implementation audit in [docs/paper-to-code-audit.md](docs/paper-to-code-audit.md) and the run guide in [docs/paper-reproduction.md](docs/paper-reproduction.md).

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

Run the full synthetic experiment:

```bash
python -m paper_repro.run_experiment --output-dir results
```

Generate a figure from the experiment summary:

```bash
python -m paper_repro.plot_results --summary results/summary_results.csv --output-dir results/figures
```

The experiment is configured for a five-minute telemetry interval, seven simulated days, a 15-minute forecast horizon, a 90% target-utilization setting, and seeds 11, 22, and 33. It includes predictable, bimodal, rapid-spike, and distribution-shift scenarios, and compares reactive, ungated XGBoost, and confidence-gated XGBoost controllers.

## Reproducibility and limitations

- Workloads are synthetic; no AWS, Kubernetes, or production APIs are called.
- The confidence gate uses an explicit implementation choice: relative ensemble disagreement and standardized feature-distance thresholds calibrated on pre-test data. The paper does not provide enough implementation detail to claim this is an exact reproduction of its original code.
- The paper's published numerical results are reference values for comparison, not hard-coded outputs.
- Any mismatch must be investigated and reported transparently.
- Three seeds provide limited statistical power. The reported normal-approximation confidence interval is descriptive, not a strong inferential guarantee.
- Generated CSVs and figures must come from actual experiment runs; do not claim the paper's values were reproduced until the run has been executed and checked.

The research implementation has been merged into `main`. The `research/paper-reproducibility-audit` branch is retained as a development/reference branch.
