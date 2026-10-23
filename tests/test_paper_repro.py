import unittest

from paper_repro.config import ExperimentConfig
from paper_repro.controllers import simulate_controller
from paper_repro.features import feature_row, make_supervised
from paper_repro.metrics import aggregate_runs, evaluate_run
from paper_repro.workloads import SCENARIOS, generate_workload


class FakeRejectedEnsemble:
    def predict(self, row):
        return 100.0, 0.5, 5.0, False


class PaperReproductionTests(unittest.TestCase):
    def test_config_matches_paper_settings(self):
        config = ExperimentConfig().validate()
        self.assertEqual(config.samples_per_day, 288)
        self.assertEqual(config.samples, 2016)
        self.assertEqual(config.horizon_steps, 3)
        self.assertEqual(config.reactive_delay_steps, 3)
        self.assertEqual(config.predictive_delay_steps, 1)
        self.assertEqual(config.seeds, (11, 22, 33))

    def test_config_rejects_invalid_split(self):
        with self.assertRaises(ValueError):
            ExperimentConfig(train_fraction=0.8, calibration_fraction=0.2).validate()

    def test_all_workloads_are_reproducible_and_nonnegative(self):
        for scenario in SCENARIOS:
            first = generate_workload(scenario, 100, 24, seed=11, shift_start=80)
            second = generate_workload(scenario, 100, 24, seed=11, shift_start=80)
            self.assertEqual(first, second)
            self.assertEqual(len(first), 100)
            self.assertTrue(all(value >= 1 for value in first))

    def test_unknown_workload_rejected(self):
        with self.assertRaises(ValueError):
            generate_workload("not-a-scenario", 10, 5, 1)

    def test_distribution_shift_occurs_after_boundary(self):
        shifted = generate_workload("distribution_shift", 100, 24, seed=7, shift_start=80)
        baseline = generate_workload("predictable", 100, 24, seed=7, shift_start=80)
        self.assertEqual(shifted[:80], baseline[:80])
        self.assertTrue(sum(shifted[80:]) > sum(baseline[80:]))

    def test_feature_row_uses_only_prefix(self):
        prefix = [10.0, 11.0, 12.0, 13.0]
        row = feature_row(prefix, 3, samples_per_day=24)
        self.assertEqual(row[0], 13.0)
        self.assertEqual(row[1], 12.0)
        self.assertEqual(len(row), 12)

    def test_supervised_targets_are_horizon_aligned(self):
        demand = [float(i) for i in range(40)]
        indices, X, y = make_supervised(demand, samples_per_day=5, horizon_steps=3)
        self.assertEqual(len(indices), len(X))
        self.assertEqual(len(X), len(y))
        self.assertEqual(y[0], demand[indices[0] + 3])

    def test_gated_fallback_uses_reactive_delay(self):
        config = ExperimentConfig(days=1)
        demand = [10.0, 100.0, 100.0, 100.0, 100.0, 100.0]
        result = simulate_controller(
            demand, config, "confidence_gated",
            ensemble=FakeRejectedEnsemble(), start_index=0,
        )
        capacities = [row["capacity_units"] for row in result["rows"]]
        # Demand observed at step 1 is scheduled through the reactive 3-step delay,
        # so it must not be applied at steps 1, 2, or 3.
        self.assertEqual(capacities[1], capacities[0])
        self.assertEqual(capacities[2], capacities[0])
        self.assertEqual(capacities[3], capacities[0])
        self.assertGreater(capacities[4], capacities[3])
        self.assertEqual(result["fallback_decisions"], len(demand))

    def test_metrics_and_aggregation(self):
        simulation = {
            "controller": "reactive",
            "rows": [
                {"slo_violation": False, "demand": 10, "excess_capacity": 2,
                 "unmet_demand": 0, "forecast": None, "index": 0},
                {"slo_violation": True, "demand": 12, "excess_capacity": 0,
                 "unmet_demand": 1, "forecast": None, "index": 1},
            ],
            "predictive_decisions": 0,
            "fallback_decisions": 0,
        }
        row = evaluate_run(simulation, [10, 12, 13], horizon_steps=1)
        self.assertEqual(row["slo_violation_pct"], 50.0)
        self.assertEqual(row["fallback_pct"], 0.0)
        summary = aggregate_runs([
            {"scenario": "test", "controller": "reactive", "slo_violation_pct": 10,
             "capacity_excess_pct": 5, "fallback_pct": 0, "forecast_mae": None,
             "forecast_rmse": None, "forecast_r2": None},
            {"scenario": "test", "controller": "reactive", "slo_violation_pct": 20,
             "capacity_excess_pct": 7, "fallback_pct": 0, "forecast_mae": None,
             "forecast_rmse": None, "forecast_r2": None},
        ])
        self.assertEqual(summary[0]["slo_violation_pct_mean"], 15.0)
        self.assertGreater(summary[0]["slo_violation_pct_ci95_half_width"], 0)


if __name__ == "__main__":
    unittest.main()
