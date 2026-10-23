"""Synthetic autoscaling comparison; makes no cloud API calls."""
import random
from statistics import mean

def workload(n=120, seed=7):
    rng = random.Random(seed)
    values = []
    for t in range(n):
        base = 25 if t < 30 else 55 if t < 70 else 35 if t < 95 else 75
        values.append(max(1, base + rng.randint(-12, 12)))
    return values

def evaluate(load, capacity_per_unit=25):
    threshold_under = predictive_under = 0
    threshold_capacity = predictive_capacity = 0
    history = []
    for demand in load:
        reactive_units = max(1, (demand + capacity_per_unit - 1) // capacity_per_unit)
        predicted = mean(history[-5:]) if history else demand
        predictive_units = max(1, int((predicted + capacity_per_unit - 1) // capacity_per_unit))
        threshold_under += max(0, demand - reactive_units * capacity_per_unit)
        predictive_under += max(0, demand - predictive_units * capacity_per_unit)
        threshold_capacity += reactive_units * capacity_per_unit
        predictive_capacity += predictive_units * capacity_per_unit
        history.append(demand)
    return {"samples": len(load), "reactive_under_capacity": threshold_under,
            "predictive_under_capacity": predictive_under,
            "reactive_capacity_proxy": threshold_capacity,
            "predictive_capacity_proxy": predictive_capacity}

if __name__ == "__main__":
    print("Synthetic workload — illustrative metrics only")
    print(evaluate(workload()))
