import unittest
from simulate import evaluate, workload

class SimulationTests(unittest.TestCase):
    def test_workload_is_reproducible(self):
        self.assertEqual(workload(), workload())

    def test_metrics_return_sample_count(self):
        self.assertEqual(evaluate([10, 20, 30])["samples"], 3)

if __name__ == "__main__":
    unittest.main()
