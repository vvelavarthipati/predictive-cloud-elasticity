"""Metrics and aggregation for controller evaluation."""

import math
import statistics


def evaluate_run(simulation, demand, horizon_steps):
    rows = simulation["rows"]
    if not rows:
        raise ValueError("simulation produced no test rows")
    violations = [1.0 if row["slo_violation"] else 0.0 for row in rows]
    result = {
        "controller": simulation["controller"],
        "test_samples": len(rows),
        "slo_violation_pct": 100.0 * statistics.fmean(violations),
        "capacity_excess_pct": 100.0 * sum(r["excess_capacity"] for r in rows) /
                               max(sum(r["demand"] for r in rows), 1e-9),
        "mean_unmet_demand": statistics.fmean(r["unmet_demand"] for r in rows),
        "predictive_decisions": simulation["predictive_decisions"],
        "fallback_decisions": simulation["fallback_decisions"],
        "fallback_pct": 100.0 * simulation["fallback_decisions"] / len(rows),
    }
    pairs = [(row["forecast"], float(demand[row["index"] + horizon_steps]))
             for row in rows if row["forecast"] is not None
             and row["index"] + horizon_steps < len(demand)]
    if pairs:
        errors = [pred - actual for pred, actual in pairs]
        actuals = [actual for _, actual in pairs]
        mae = statistics.fmean(abs(e) for e in errors)
        rmse = math.sqrt(statistics.fmean(e * e for e in errors))
        mean_actual = statistics.fmean(actuals)
        ss_tot = sum((actual - mean_actual) ** 2 for actual in actuals)
        ss_res = sum(e * e for e in errors)
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 0.0
        result.update({"forecast_mae": mae, "forecast_rmse": rmse, "forecast_r2": r2})
    else:
        result.update({"forecast_mae": None, "forecast_rmse": None, "forecast_r2": None})
    return result


def aggregate_runs(rows):
    """Aggregate metrics across seeds with an approximate normal 95% CI."""
    grouped = {}
    for row in rows:
        grouped.setdefault((row["scenario"], row["controller"]), []).append(row)
    output = []
    for (scenario, controller), group in sorted(grouped.items()):
        values = [float(item["slo_violation_pct"]) for item in group]
        mean_value = statistics.fmean(values)
        if len(values) > 1:
            half_width = 1.96 * statistics.stdev(values) / math.sqrt(len(values))
        else:
            half_width = 0.0
        output.append({
            "scenario": scenario, "controller": controller, "runs": len(values),
            "slo_violation_pct_mean": mean_value,
            "slo_violation_pct_ci95_half_width": half_width,
            "capacity_excess_pct_mean": statistics.fmean(float(x["capacity_excess_pct"]) for x in group),
            "fallback_pct_mean": statistics.fmean(float(x["fallback_pct"]) for x in group),
            "forecast_mae_mean": _mean_non_null(group, "forecast_mae"),
            "forecast_rmse_mean": _mean_non_null(group, "forecast_rmse"),
            "forecast_r2_mean": _mean_non_null(group, "forecast_r2"),
        })
    return output


def _mean_non_null(rows, key):
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    return statistics.fmean(values) if values else None
