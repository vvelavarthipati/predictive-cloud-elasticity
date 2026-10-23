"""Run the synthetic paper-reproduction experiment and export CSV results."""

import argparse
import csv
import json
import statistics
from pathlib import Path

from .config import ExperimentConfig
from .controllers import simulate_controller, train_predictive_ensemble
from .features import feature_row
from .metrics import aggregate_runs, evaluate_run
from .workloads import SCENARIOS, generate_workload


def _gate_diagnostics(demand, ensemble, config, train_end, test_start):
    """Describe gate thresholds, rejection reasons, and forecast error by period."""
    result = {
        "uncertainty_threshold": ensemble.uncertainty_threshold,
        "ood_threshold": ensemble.ood_threshold,
    }
    period_errors = {"pre_shift": [], "post_shift": []}
    reason_counts = {
        "pre_shift_accepted": 0, "pre_shift_uncertainty": 0,
        "pre_shift_ood": 0, "pre_shift_both": 0,
        "post_shift_accepted": 0, "post_shift_uncertainty": 0,
        "post_shift_ood": 0, "post_shift_both": 0,
    }
    start = max(config.samples_per_day, train_end)
    for t in range(start, len(demand) - config.horizon_steps):
        row = feature_row(demand[:t + 1], t, config.samples_per_day)
        forecast, uncertainty, distance, accepted, reason = ensemble.predict(row)
        period = "pre_shift" if t < test_start else "post_shift"
        reason_counts[f"{period}_{reason}"] += 1
        actual = float(demand[t + config.horizon_steps])
        period_errors[period].append(abs(forecast - actual))
    for period, errors in period_errors.items():
        result[f"{period}_forecast_count"] = len(errors)
        result[f"{period}_forecast_mae"] = statistics.fmean(errors) if errors else None
        total = sum(reason_counts[f"{period}_{reason}"] for reason in
                    ("accepted", "uncertainty", "ood", "both"))
        result[f"{period}_gate_evaluations"] = total
        for reason in ("accepted", "uncertainty", "ood", "both"):
            count = reason_counts[f"{period}_{reason}"]
            result[f"{period}_{reason}_count"] = count
            result[f"{period}_{reason}_pct"] = 100.0 * count / total if total else 0.0
    return result


def run_experiment(config=None, output_dir="results"):
    config = (config or ExperimentConfig()).validate()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    raw_rows = []
    gate_rows = []
    for scenario in SCENARIOS:
        for seed in config.seeds:
            demand = generate_workload(
                scenario, config.samples, config.samples_per_day, seed,
                shift_start=int(config.samples * (config.train_fraction + config.calibration_fraction)),
            )
            ensemble, test_start = train_predictive_ensemble(
                demand, config.samples_per_day, config, seed
            )
            train_end = int(len(demand) * config.train_fraction)
            gate_rows.append({
                "scenario": scenario, "seed": seed, "test_start_index": test_start,
                **_gate_diagnostics(demand, ensemble, config, train_end, test_start),
            })
            for controller in ("reactive", "xgboost", "confidence_gated"):
                simulation = simulate_controller(
                    demand, config, controller,
                    ensemble=None if controller == "reactive" else ensemble,
                    start_index=test_start,
                )
                row = {
                    "scenario": scenario,
                    "seed": seed,
                    "test_start_index": test_start,
                    **evaluate_run(simulation, demand, config.horizon_steps),
                }
                if controller == "confidence_gated":
                    reasons = [item["gate_reason"] for item in simulation["rows"]]
                    for reason in ("accepted", "uncertainty", "ood", "both"):
                        row[f"test_gate_{reason}_count"] = reasons.count(reason)
                        row[f"test_gate_{reason}_pct"] = 100.0 * reasons.count(reason) / len(reasons)
                raw_rows.append(row)
                print(f"{scenario:20s} seed={seed:2d} {controller:17s} "
                      f"SLO={row['slo_violation_pct']:.2f}% "
                      f"excess={row['capacity_excess_pct']:.2f}% "
                      f"fallback={row['fallback_pct']:.1f}%")
    summary_rows = aggregate_runs(raw_rows)
    _write_csv(output / "per_seed_results.csv", raw_rows)
    _write_csv(output / "summary_results.csv", summary_rows)
    _write_csv(output / "gate_diagnostics.csv", gate_rows)
    with (output / "experiment_config.json").open("w", encoding="utf-8") as handle:
        json.dump(config.__dict__, handle, indent=2)
        handle.write("\n")
    print(f"\nWrote {output / 'per_seed_results.csv'}")
    print(f"Wrote {output / 'summary_results.csv'}")
    print(f"Wrote {output / 'gate_diagnostics.csv'}")
    return raw_rows, summary_rows


def _write_csv(path, rows):
    if not rows:
        return
    fields = list(dict.fromkeys(key for row in rows for key in row.keys()))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="results")
    args = parser.parse_args()
    run_experiment(output_dir=args.output_dir)


if __name__ == "__main__":
    main()
