"""Controller implementations and confidence-gate calibration.

The gate is a transparent experimental operationalization: ensemble relative
standard deviation and standardized feature distance are calibrated using only
pre-test calibration data. This is not asserted to be the paper's exact code.
"""

import math
import statistics
from collections import deque

from .features import feature_row, make_supervised


def _xgb_regressor(seed, config):
    try:
        from xgboost import XGBRegressor
    except ImportError as exc:
        raise RuntimeError("Install dependencies with: pip install -r requirements.txt") from exc
    return XGBRegressor(
        n_estimators=config.xgboost_estimators,
        max_depth=config.xgboost_max_depth,
        learning_rate=config.xgboost_learning_rate,
        objective="reg:squarederror",
        random_state=seed,
        n_jobs=1,
        verbosity=0,
    )


def _relative_disagreement(predictions):
    center = statistics.fmean(predictions)
    if abs(center) < 1e-9:
        return 0.0
    return statistics.pstdev(predictions) / abs(center)


def _standardized_distance(row, means, scales):
    return math.sqrt(sum(((x - mu) / scale) ** 2 for x, mu, scale in zip(row, means, scales)) / len(row))


class PredictiveEnsemble:
    def __init__(self, models, means, scales, uncertainty_threshold, ood_threshold):
        self.models = models
        self.means = means
        self.scales = scales
        self.uncertainty_threshold = uncertainty_threshold
        self.ood_threshold = ood_threshold

    def predict(self, row):
        predictions = [float(model.predict([row])[0]) for model in self.models]
        center = statistics.fmean(predictions)
        uncertainty = _relative_disagreement(predictions)
        distance = _standardized_distance(row, self.means, self.scales)
        accepted = uncertainty <= self.uncertainty_threshold and distance <= self.ood_threshold
        return max(0.0, center), uncertainty, distance, accepted


def train_predictive_ensemble(demand, samples_per_day, config, seed):
    """Fit only on the training partition; calibrate gate on the next partition."""
    _, X_all, y_all = make_supervised(demand, samples_per_day, config.horizon_steps)
    target_indices = list(range(samples_per_day, len(demand) - config.horizon_steps))
    if len(X_all) != len(target_indices):
        raise RuntimeError("feature/target alignment failure")

    train_end = int(len(demand) * config.train_fraction)
    cal_end = int(len(demand) * (config.train_fraction + config.calibration_fraction))
    train_pairs = [(x, y) for i, x, y in zip(target_indices, X_all, y_all)
                   if i + config.horizon_steps < train_end]
    cal_pairs = [(i, x, y) for i, x, y in zip(target_indices, X_all, y_all)
                 if train_end <= i + config.horizon_steps < cal_end]
    if len(train_pairs) < 20 or len(cal_pairs) < 10:
        raise ValueError("not enough training or calibration samples for the configured split")

    X_train = [pair[0] for pair in train_pairs]
    y_train = [pair[1] for pair in train_pairs]
    models = []
    for offset in range(5):
        model = _xgb_regressor(seed + offset, config)
        model.fit(X_train, y_train)
        models.append(model)

    means = [statistics.fmean(row[j] for row in X_train) for j in range(len(X_train[0]))]
    scales = []
    for j, mu in enumerate(means):
        sd = statistics.pstdev(row[j] for row in X_train)
        scales.append(sd if sd > 1e-9 else 1.0)

    raw_uncertainties = []
    raw_distances = []
    for _, row, _ in cal_pairs:
        preds = [float(model.predict([row])[0]) for model in models]
        raw_uncertainties.append(_relative_disagreement(preds))
        raw_distances.append(_standardized_distance(row, means, scales))
    # Quantile thresholds are derived from calibration features only, never test outcomes.
    uncertainty_threshold = _quantile(raw_uncertainties, 0.90)
    ood_threshold = max(_quantile(raw_distances, 0.99), 1e-9)
    return PredictiveEnsemble(models, means, scales, uncertainty_threshold, ood_threshold), cal_end


def _quantile(values, q):
    ordered = sorted(float(x) for x in values)
    if not ordered:
        raise ValueError("cannot calculate quantile of empty data")
    position = (len(ordered) - 1) * q
    lo = int(position)
    hi = min(lo + 1, len(ordered) - 1)
    fraction = position - lo
    return ordered[lo] * (1 - fraction) + ordered[hi] * fraction


def _capacity(demand, target_utilization):
    return max(1.0, float(math.ceil(max(0.0, demand) / target_utilization)))


def simulate_controller(demand, config, controller, ensemble=None, start_index=0):
    """Simulate delayed capacity actions over the test period.

    The reactive controller schedules observed-demand capacity after its delay.
    Predictive controllers schedule forecast-demand capacity after their shorter
    delay. Pending changes are applied only at their configured arrival step.
    """
    if controller not in ("reactive", "xgboost", "confidence_gated"):
        raise ValueError("unknown controller")
    if controller != "reactive" and ensemble is None:
        raise ValueError("predictive controllers require a trained ensemble")
    delay = config.reactive_delay_steps if controller == "reactive" else config.predictive_delay_steps
    capacity = _capacity(demand[start_index], config.target_utilization)
    pending = {}
    rows = []
    used_predictive = 0
    fallbacks = 0
    for t in range(start_index, len(demand)):
        if t in pending:
            capacity = pending.pop(t)
        observed = float(demand[t])
        forecast = None
        uncertainty = None
        distance = None
        accepted = False
        if controller == "reactive":
            desired = _capacity(observed, config.target_utilization)
        else:
            row = feature_row(demand[:t + 1], t, config.samples_per_day)
            forecast, uncertainty, distance, accepted = ensemble.predict(row)
            if controller == "xgboost" or accepted:
                desired = _capacity(forecast, config.target_utilization)
                used_predictive += 1
            else:
                desired = _capacity(observed, config.target_utilization)
                fallbacks += 1
        apply_at = t + delay
        if apply_at < len(demand):
            pending[apply_at] = desired
        unmet = max(0.0, observed - capacity * config.target_utilization)
        excess = max(0.0, capacity * config.target_utilization - observed)
        rows.append({
            "index": t, "demand": observed, "capacity_units": capacity,
            "capacity_available": capacity * config.target_utilization,
            "slo_violation": unmet > 1e-9, "unmet_demand": unmet,
            "excess_capacity": excess, "forecast": forecast,
            "uncertainty": uncertainty, "ood_distance": distance,
            "gate_accepted": accepted if controller != "reactive" else None,
        })
    return {
        "controller": controller,
        "rows": rows,
        "predictive_decisions": used_predictive,
        "fallback_decisions": fallbacks,
    }
