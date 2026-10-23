import unittest

from simulate import evaluate, workload


class SimulationTests(unittest.TestCase):
    def test_workload_is_reproducible(self):
        self.assertEqual(workload(), workload())

    def test_workload_length_matches_request(self):
        self.assertEqual(len(workload(n=12)), 12)

    def test_metrics_return_sample_count(self):
        result = evaluate([10, 20, 30])
        self.assertEqual(result["samples"], 3)
        self.assertIn("moving_average_under_capacity", result)

    def test_capacity_must_be_positive(self):
        with self.assertRaises(ValueError):
            evaluate([10], capacity_per_unit=0)

    def test_history_window_must_be_positive(self):
        with self.assertRaises(ValueError):
            evaluate([10], history_window=0)

    def test_negative_demand_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate([10, -1, 20])

    def test_empty_workload_returns_zero_samples(self):
        self.assertEqual(evaluate([])["samples"], 0)


if __name__ == "__main__":
    unittest.main()
