# Predictive Cloud Elasticity

A minimal Python starter for comparing simple scaling policies against a synthetic workload.

## What is included
- `simulate.py`: deterministic synthetic demand generator and basic capacity metrics.
- `tests/`: smoke tests.
- `requirements.txt`: no third-party dependencies.

## Run locally
```bash
python simulate.py
python -m unittest discover -s tests -v
```

## Simulation plan
1. Generate a synthetic load trace with quiet, ramp-up, and burst periods.
2. Compare a reactive threshold policy with a simple moving-average predictor.
3. Report under-capacity and provisioned-capacity proxies.
4. Later extend to XGBoost, confidence gating, repeated seeds, and confidence intervals.

## Important limitations
This is illustrative starter code, not a production autoscaler. The workload is synthetic, the capacity metric is a simplified proxy, and no claim of real-world performance is made.

## References
- Kubernetes, [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/).
- Chen and Guestrin, [XGBoost: A Scalable Tree Boosting System](https://doi.org/10.1145/2939672.2939785), KDD 2016.
- Mao et al., [Resource Management with Deep Reinforcement Learning](https://doi.org/10.1145/3005745.3005750), HotNets 2016.

## Roadmap
- [ ] Add multiple workload profiles and random seeds
- [ ] Add a trained forecasting model
- [ ] Export CSV metrics and plots
- [ ] Add CI tests
