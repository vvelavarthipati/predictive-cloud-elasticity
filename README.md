# Predictive Cloud Elasticity

A small Python research prototype for exploring predictive cloud autoscaling using synthetic workloads and simplified capacity metrics.

## Goals

- Generate a reproducible synthetic demand trace.
- Compare a reactive capacity baseline with a simple moving-average predictor.
- Measure simplified under-capacity and provisioned-capacity proxies.
- Establish a baseline for future experiments with XGBoost forecasting and confidence-gated scaling.

## Repository contents

- `simulate.py` — synthetic workload generator and baseline comparison.
- `tests/test_simulate.py` — unit tests for reproducibility and input validation.
- `requirements.txt` — no third-party dependencies required.

## Requirements

- Python 3.9+
- No external packages for the current starter implementation.

## Run

```bash
python simulate.py
python -m unittest discover -s tests -v
```

## Simulation methodology

1. Generate a deterministic demand trace with several demand regimes and random variation.
2. At each sample, calculate a reactive capacity level from current demand.
3. Calculate a second capacity level from the mean of up to five previous demand samples.
4. Accumulate simplified under-capacity and provisioned-capacity indicators for both policies.

### Metrics

- **Under-capacity proxy:** sum of demand above selected capacity at each sample.
- **Provisioned-capacity proxy:** sum of selected capacity across all samples.

These are deliberately simplified indicators. They are not direct measurements of latency, availability, infrastructure cost, or real cloud resource utilization.

## Interpretation and limitations

- All workload data is synthetic and generated locally.
- The moving-average method is a baseline, not a trained machine-learning model.
- The current model does not call AWS, Kubernetes, or any other cloud service.
- Results depend on the workload shape and assumptions; no production performance claim is made.
- The two policies use different information: the reactive baseline sees current demand, while the moving-average baseline uses past samples. Treat this as a teaching comparison, not a fair production benchmark.

## Research references

- Kubernetes, [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/).
- Chen and Guestrin, [XGBoost: A Scalable Tree Boosting System](https://doi.org/10.1145/2939672.2939785), KDD 2016.
- Mao et al., [Resource Management with Deep Reinforcement Learning](https://doi.org/10.1145/3005745.3005750), HotNets 2016.

These references provide background only; they do not validate this starter simulation.

## Roadmap

- [ ] Add steady, ramp, burst, and noisy workload profiles.
- [ ] Add a true next-step forecast and compare it with persistence and moving-average baselines.
- [ ] Add XGBoost as an optional model.
- [ ] Add confidence-gated scaling and configurable safety margins.
- [ ] Run repeated trials across documented seeds and report variability.
- [ ] Export results to CSV and create plots.
- [ ] Add continuous integration.

## Research integrity

Describe current outputs as synthetic simulation results. Do not present them as measured cloud results unless experiments are later run on real infrastructure and the methodology, configuration, and raw results are documented.
