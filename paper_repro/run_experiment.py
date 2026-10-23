"""Run the synthetic paper-reproduction experiment and export CSV results."""

import argparse
import csv
import json
from pathlib import Path

from .config import ExperimentConfig
from .controllers import simulate_controller, train_predictive_ensemble
from .metrics import aggregate_runs, evaluate_run
from .workloads import SCENARIOS, generate_workload


def run_experiment(config=None, output_dir="results"):
    config = (config or ExperimentConfig()).validate()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    raw_rows = []
    for scenario in SCENARIOS:
        for seed in config.seeds:
            demand = generate_workload(
                scenario, config.samples, config.samples_per_day, seed,
                shift_start=int(config.samples * (config.train_fraction + config.calibration_fraction)),
            )
            ensemble, test_start = train_predictive_ensemble(
                demand, config.samples_per_day, config, seed
            )
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
                raw_rows.append(row)
                print(f"{scenario:20s} seed={seed:2d} {controller:17s} "
                      f"SLO={row['slo_violation_pct']:.2f}% "
                      f"excess={row['capacity_excess_pct']:.2f}% "
                      f"fallback={row['fallback_pct']:.1f}%")
    summary_rows = aggregate_runs(raw_rows)
    _write_csv(output / "per_seed_results.csv", raw_rows)
    _write_csv(output / "summary_results.csv", summary_rows)
    with (output / "experiment_config.json").open("w", encoding="utf-8") as handle:
        json.dump(config.__dict__, handle, indent=2)
        handle.write("\n")
    print(f"\nWrote {output / 'per_seed_results.csv'}")
    print(f"Wrote {output / 'summary_results.csv'}")
    return raw_rows, summary_rows


def _write_csv(path, rows):
    if not rows:
        return
    fields = list(rows[0].keys())
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
