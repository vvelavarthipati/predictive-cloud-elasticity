"""Time-ordered feature construction for demand forecasting."""

import math
import statistics


def feature_row(history, index, samples_per_day, window=12):
    """Features for forecasting demand at index + horizon from history up to index.

    No values after index are read. Missing early lags use the earliest observed
    value, which keeps the feature matrix defined at the start of a trace.
    """
    if not history:
        raise ValueError("history cannot be empty")
    current = float(history[index])
    def lag(k):
        return float(history[max(0, index - k)])
    start = max(0, index - window + 1)
    recent = [float(x) for x in history[start:index + 1]]
    mean = statistics.fmean(recent)
    variance = statistics.pvariance(recent) if len(recent) > 1 else 0.0
    previous = float(history[index - 1]) if index > 0 else current
    daily_lag = lag(samples_per_day)
    phase = 2 * math.pi * (index % samples_per_day) / samples_per_day
    return [
        current, lag(1), lag(2), lag(3), lag(6), lag(12),
        daily_lag, mean, variance, current - previous,
        math.sin(phase), math.cos(phase),
    ]


def make_supervised(demand, samples_per_day, horizon_steps, window=12):
    """Return time-ordered feature rows and target values."""
    last = len(demand) - horizon_steps
    indices = list(range(max(0, samples_per_day), last))
    X = [feature_row(demand, i, samples_per_day, window) for i in indices]
    y = [float(demand[i + horizon_steps]) for i in indices]
    return indices, X, y
