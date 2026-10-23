"""Create publication-style plots from generated summary_results.csv."""

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


CONTROLLERS = ("reactive", "xgboost", "confidence_gated")
LABELS = {
    "reactive": "Reactive",
    "xgboost": "Ungated XGBoost",
    "confidence_gated": "Confidence-gated XGBoost",
}


def plot_summary(summary_csv, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(summary_csv, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    scenarios = list(dict.fromkeys(row["scenario"] for row in rows))
    values = {
        (row["scenario"], row["controller"]): float(row["slo_violation_pct_mean"])
        for row in rows
    }
    x = list(range(len(scenarios)))
    width = 0.25
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for i, controller in enumerate(CONTROLLERS):
        offsets = [position + (i - 1) * width for position in x]
        heights = [values.get((scenario, controller), 0.0) for scenario in scenarios]
        ax.bar(offsets, heights, width=width, label=LABELS[controller])
    ax.set_xticks(x, [s.replace("_", "\n") for s in scenarios])
    ax.set_ylabel("SLO violation (%)")
    ax.set_title("Simulated SLO violation by workload and controller")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    path = output_dir / "slo_violation_by_controller.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    print(f"Wrote {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", default="results/summary_results.csv")
    parser.add_argument("--output-dir", default="results/figures")
    args = parser.parse_args()
    plot_summary(args.summary, args.output_dir)


if __name__ == "__main__":
    main()
