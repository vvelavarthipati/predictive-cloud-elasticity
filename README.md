# Predictive Cloud Elasticity

A small Python research prototype for exploring predictive cloud autoscaling using synthetic workloads and simplified capacity metrics.

## Goals

- Generate reproducible synthetic demand traces.
- Compare a reactive capacity baseline with a simple moving-average predictor.
- Measure simplified under-capacity and provisioned-capacity proxies.
- Establish a foundation for future forecasting and confidence-gated scaling experiments.

## Repository contents

- `simulate.py` — synthetic workload generator, CSV loader, and baseline comparison.
- `data/sample_workload.csv` — 120 illustrative samples spanning quiet, ramp-up, high-load, cooldown, burst, and recovery scenarios.
- `tests/test_simulate.py` — unit tests.
- `requirements.txt` — no third-party dependencies required.

## Requirements

Python 3.9+; no external packages are required for the starter.

## Run with built-in synthetic data

```bash
python simulate.py
```

## Run with the sample CSV

```bash
python simulate.py data/sample_workload.csv
```

The CSV must contain a `demand_units` column. Additional columns such as `timestamp` and `scenario` describe the sample but are not used by the current model.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Simulation methodology

1. Generate or load a synthetic demand trace.
2. Calculate a reactive capacity level from current demand.
3. Calculate a second capacity level from the mean of up to five previous samples.
4. Accumulate simplified under-capacity and provisioned-capacity indicators for both policies.

### Metrics

- **Under-capacity proxy:** sum of demand above selected capacity at each sample.
- **Provisioned-capacity proxy:** sum of selected capacity across all samples.

These are simplified indicators, not direct measurements of latency, availability, infrastructure cost, or real cloud utilization.

## Limitations

- The included CSV is synthetic, not production telemetry.
- The moving-average method is a baseline, not a trained ML model.
- No cloud services are called.
- Results depend on the workload and assumptions; they are not evidence of real-world performance.
- The reactive baseline uses current demand while the moving-average baseline uses previous demand, so this is a teaching comparison rather than a fair production benchmark.

## Research references

- Kubernetes, [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/).
- Chen and Guestrin, [XGBoost: A Scalable Tree Boosting System](https://doi.org/10.1145/2939672.2939785), KDD 2016.
- Mao et al., [Resource Management with Deep Reinforcement Learning](https://doi.org/10.1145/3005745.3005750), HotNets 2016.

These references provide background only; they do not validate the current simulation.

## Roadmap

- [ ] Add multiple workload profiles and repeated random seeds.
- [ ] Add a true next-step forecast and compare with simple baselines.
- [ ] Add optional XGBoost and confidence-gated scaling.
- [ ] Export results to CSV and plot metrics.
- [ ] Add continuous integration.

## Research integrity

Describe current outputs as synthetic simulation results. Do not present them as measured cloud results unless real infrastructure experiments are performed and documented.
