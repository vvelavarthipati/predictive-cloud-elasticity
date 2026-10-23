"""Deterministic synthetic workload generators for the four paper scenarios."""

import math
import random


SCENARIOS = ("predictable", "bimodal", "rapid_spike", "distribution_shift")


def generate_workload(scenario, samples, samples_per_day, seed, shift_start=None):
    """Generate non-negative demand samples; all scenarios are synthetic.

    For distribution_shift, the normal pattern is retained before shift_start;
    demand is amplified and its baseline raised after that boundary.
    """
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario: {scenario}")
    if samples < 1 or samples_per_day < 1:
        raise ValueError("samples and samples_per_day must be positive")
    rng = random.Random(seed)
    values = []
    shift_start = shift_start if shift_start is not None else int(samples * 0.8)
    for t in range(samples):
        phase = 2 * math.pi * (t % samples_per_day) / samples_per_day
        if scenario in ("predictable", "distribution_shift"):
            baseline = 55 + 20 * math.sin(phase - math.pi / 2)
        elif scenario == "bimodal":
            baseline = 42 + 16 * math.sin(phase - math.pi / 2) + 13 * math.sin(2 * phase - math.pi / 2)
        else:
            baseline = 50 + 18 * math.sin(phase - math.pi / 2)
        noise = rng.gauss(0, 3.0)
        demand = baseline + noise
        if scenario == "rapid_spike":
            # Short bursts recur irregularly; burst positions are seed-controlled.
            if (t % samples_per_day) in (int(samples_per_day * 0.28), int(samples_per_day * 0.29),
                                         int(samples_per_day * 0.62)):
                demand += rng.uniform(25, 40)
        if scenario == "distribution_shift" and t >= shift_start:
            demand = demand * 1.45 + 12
        values.append(max(1.0, float(demand)))
    return values
