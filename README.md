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

## Frequently asked questions

### What problem does this research address?

Reactive autoscaling responds to observed demand and can be delayed while new capacity becomes available. This project explores whether forecasting future demand with XGBoost can support more proactive capacity decisions.

### Which controllers are compared?

The experiment compares a reactive controller, an ungated XGBoost predictive controller, and a confidence-gated XGBoost controller that falls back to reactive behavior when its prediction gate rejects a forecast.

### What does confidence-gated scaling mean?

The implementation checks forecast uncertainty and an out-of-distribution (OOD) score. If the checks pass, the predictive path can be used; otherwise, the controller follows the reactive fallback path. The exact formulas and threshold percentiles are implementation choices because the paper does not fully specify them.

### What workloads are tested?

Four synthetic scenarios are included: predictable demand, bimodal demand, rapid spikes, and distribution shift. They support controlled experiments but are not substitutes for validation on real production traces.

### What does SLO violation mean in this repository?

It is the percentage of test intervals in which provisioned capacity is below simulated demand. It is a capacity-based simulation metric, not a direct measurement of application latency, availability, or a production SLO.

### Does this code deploy to AWS or Kubernetes?

No. The current experiment runs locally with synthetic workloads and simulated capacity decisions. It does not call production AWS or Kubernetes APIs.

### Have the published numerical results been reproduced exactly?

No. The experiment has been run locally and the repository owner reported that all 24 tests passed, but the current numerical results do not exactly match the published paper. The implementation assumptions and differences are documented in [the paper-to-code audit](docs/paper-to-code-audit.md). Published values are not hard-coded into the simulator.

### How do I run the experiment?

Install dependencies with `python -m pip install -r requirements.txt`, run tests with `python -m unittest discover -s tests -v`, then execute `python -m paper_repro.run_experiment --output-dir results`. See [the reproduction guide](docs/paper-reproduction.md) for details.

### What are the main limitations?

The workloads are synthetic, some controller and gate details must be reconstructed from an incompletely specified paper, and only three random seeds are used. Results should therefore be treated as preliminary simulation evidence rather than proof of production performance.
