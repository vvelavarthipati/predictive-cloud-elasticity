"""Synthetic autoscaling comparison; makes no cloud API calls.

All workload values and metrics are illustrative. This is not a production
autoscaler or a benchmark of any cloud platform.
"""
import argparse
import csv
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


def load_csv(path):
    """Load demand_units from a CSV containing a demand_units column."""
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "demand_units" not in reader.fieldnames:
            raise ValueError("CSV must contain a 'demand_units' column")
        values = []
        for line_number, row in enumerate(reader, start=2):
            try:
                demand = int(row["demand_units"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid demand_units on CSV line {line_number}") from exc
            if demand < 0:
                raise ValueError(f"Negative demand_units on CSV line {line_number}")
            values.append(demand)
    return values


def evaluate(load, capacity_per_unit=25, history_window=5):
    """Compare reactive capacity with a simple moving-average baseline."""
    if capacity_per_unit <= 0:
        raise ValueError("capacity_per_unit must be positive")
    if history_window <= 0:
        raise ValueError("history_window must be positive")
    if any(demand < 0 for demand in load):
        raise ValueError("demand values must be non-negative")

    reactive_under = moving_under = 0
    reactive_capacity = moving_capacity = 0
    history = []
    for demand in load:
        reactive_units = max(1, (demand + capacity_per_unit - 1) // capacity_per_unit)
        prediction = mean(history[-history_window:]) if history else demand
        moving_units = max(1, int((prediction + capacity_per_unit - 1) // capacity_per_unit))
        reactive_under += max(0, demand - reactive_units * capacity_per_unit)
        moving_under += max(0, demand - moving_units * capacity_per_unit)
        reactive_capacity += reactive_units * capacity_per_unit
        moving_capacity += moving_units * capacity_per_unit
        history.append(demand)

    return {
        "samples": len(load),
        "reactive_under_capacity": reactive_under,
        "moving_average_under_capacity": moving_under,
        "reactive_capacity_proxy": reactive_capacity,
        "moving_average_capacity_proxy": moving_capacity,
    }


def main():
    parser = argparse.ArgumentParser(description="Run the synthetic cloud elasticity demo.")
    parser.add_argument("csv_path", nargs="?", help="Optional CSV with a demand_units column")
    args = parser.parse_args()
    load = load_csv(args.csv_path) if args.csv_path else workload()
    print("Synthetic workload — illustrative metrics only")
    if args.csv_path:
        print(f"Input CSV: {args.csv_path}")
    print(evaluate(load))


if __name__ == "__main__":
    main()
