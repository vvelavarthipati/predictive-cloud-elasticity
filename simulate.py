"""Synthetic autoscaling comparison; makes no cloud API calls.

All workload values and metrics are illustrative. This is not a production
autoscaler or a benchmark of any cloud platform.
"""
import random
from statistics import mean


def workload(n=120, seed=7):
    """Return a deterministic synthetic demand trace."""
    if n < 0:
        raise ValueError("n must be non-negative")

    rng = random.Random(seed)
    values = []
    for t in range(n):
        if t < 30:
            base = 25
        elif t < 70:
            base = 55
        elif t < 95:
            base = 35
        else:
            base = 75
        values.append(max(1, base + rng.randint(-12, 12)))
    return values


def evaluate(load, capacity_per_unit=25, history_window=5):
    """Compare reactive capacity with a simple moving-average baseline.

    The reactive policy selects capacity from current demand. The moving-average
    baseline selects capacity from the previous samples, so it can lag sudden
    changes. Returned capacity totals are proxies, not cloud cost measurements.
    """
    if capacity_per_unit <= 0:
        raise ValueError("capacity_per_unit must be positive")
    if history_window <= 0:
        raise ValueError("history_window must be positive")
    if any(demand < 0 for demand in load):
        raise ValueError("demand values must be non-negative")

    reactive_under = predictive_under = 0
    reactive_capacity = predictive_capacity = 0
    history = []

    for demand in load:
        reactive_units = max(1, (demand + capacity_per_unit - 1) // capacity_per_unit)

        # Baseline prediction uses only earlier samples; on the first sample,
        # use current demand because there is no history available.
        prediction = mean(history[-history_window:]) if history else demand
        predictive_units = max(
            1, int((prediction + capacity_per_unit - 1) // capacity_per_unit)
        )

        reactive_under += max(0, demand - reactive_units * capacity_per_unit)
        predictive_under += max(0, demand - predictive_units * capacity_per_unit)
        reactive_capacity += reactive_units * capacity_per_unit
        predictive_capacity += predictive_units * capacity_per_unit
        history.append(demand)

    return {
        "samples": len(load),
        "reactive_under_capacity": reactive_under,
        "moving_average_under_capacity": predictive_under,
        "reactive_capacity_proxy": reactive_capacity,
        "moving_average_capacity_proxy": predictive_capacity,
    }


if __name__ == "__main__":
    print("Synthetic workload — illustrative metrics only")
    print(evaluate(workload()))
