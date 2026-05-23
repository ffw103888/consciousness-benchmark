from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mind_lab.thalamus import ThalamusInspiredArchitecture
from mind_lab.utils import ensure_dir, write_json


def latest_run(root: Path) -> Path:
    latest = root / "latest_run.txt"
    if latest.exists():
        text = latest.read_text(encoding="utf-8").strip()
        if text and Path(text).exists():
            return Path(text)
    runs = [p for p in root.iterdir() if p.is_dir()]
    if not runs:
        raise FileNotFoundError(f"No runs under {root}")
    return max(runs, key=lambda p: p.stat().st_mtime)


def base_config() -> dict[str, Any]:
    return {
        "workspace_capacity": 96,
        "initial_threshold": 0.52,
        "inhibition_strength": 0.45,
        "threshold_adaptation_rate": 0.08,
        "dim": 32,
        "enable_reticular": True,
        "enable_core": True,
        "enable_matrix": True,
        "enable_cortical_feedback": True,
    }


def profile_row(system: ThalamusInspiredArchitecture) -> dict[str, float]:
    profile = system.evaluation_profile()
    details = profile.get("details", {})
    row = {
        "state": float(profile["state"]),
        "content": float(profile["content"]),
        "self_model": float(profile["self_model"]),
        "agency": float(profile["agency"]),
        "temporal_continuity": float(profile["temporal_continuity"]),
        "separation": float(profile["self_model"] - profile["agency"]),
        "mean_score": float(
            np.mean(
                [
                    profile["state"],
                    profile["content"],
                    profile["self_model"],
                    profile["agency"],
                    profile["temporal_continuity"],
                ]
            )
        ),
    }
    for key in [
        "phi_proxy",
        "pci_proxy",
        "gating_agency_proxy",
        "action_agency_proxy",
        "threshold_stability",
        "workspace_presence",
        "workspace_temporal",
        "source_diversity",
        "cortical_presence",
        "instability",
    ]:
        row[key] = float(details.get(key, 0.0))
    return row


def condition_config(workspace: bool, action_loop: bool) -> dict[str, Any]:
    return {
        **base_config(),
        "enable_workspace": workspace,
        "enable_action_loop": action_loop,
    }


def condition_name(workspace: bool, action_loop: bool) -> str:
    return f"workspace_{'on' if workspace else 'off'}__action_{'on' if action_loop else 'off'}"


def run_factorial(seeds: list[int], final_steps: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for workspace in [False, True]:
        for action_loop in [False, True]:
            name = condition_name(workspace, action_loop)
            for seed in seeds:
                system = ThalamusInspiredArchitecture(condition_config(workspace, action_loop), seed=seed)
                system.run_steps(final_steps)
                row = profile_row(system)
                row.update(
                    {
                        "seed": seed,
                        "steps": final_steps,
                        "condition": name,
                        "workspace": workspace,
                        "action_loop": action_loop,
                    }
                )
                rows.append(row)
                print(
                    f"factorial {name:32s} seed={seed} "
                    f"self={row['self_model']:.3f} agency={row['agency']:.3f} sep={row['separation']:.3f}",
                    flush=True,
                )
    return pd.DataFrame(rows)


def run_timescale(seeds: list[int], time_points: list[int]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for workspace in [False, True]:
        for action_loop in [False, True]:
            name = condition_name(workspace, action_loop)
            for seed in seeds:
                system = ThalamusInspiredArchitecture(condition_config(workspace, action_loop), seed=seed)
                elapsed = 0
                for target in time_points:
                    delta = int(target) - elapsed
                    if delta > 0:
                        system.run_steps(delta)
                        elapsed = int(target)
                    row = profile_row(system)
                    row.update(
                        {
                            "seed": seed,
                            "steps": elapsed,
                            "condition": name,
                            "workspace": workspace,
                            "action_loop": action_loop,
                        }
                    )
                    rows.append(row)
                print(f"timescale {name:32s} seed={seed} done to {elapsed}", flush=True)
    return pd.DataFrame(rows)


def summarize_factorial(df: pd.DataFrame) -> pd.DataFrame:
    metrics = ["self_model", "agency", "separation", "state", "content", "temporal_continuity", "mean_score"]
    grouped = df.groupby(["condition", "workspace", "action_loop"], as_index=False)[metrics].agg(["mean", "std"])
    grouped.columns = ["_".join(col).strip("_") for col in grouped.columns.to_flat_index()]
    return grouped.reset_index(drop=True)


def effect_summary(df: pd.DataFrame) -> dict[str, Any]:
    means = df.groupby(["workspace", "action_loop"])[["self_model", "agency", "separation"]].mean()

    def m(workspace: bool, action_loop: bool, metric: str) -> float:
        return float(means.loc[(workspace, action_loop), metric])

    effects = {
        "workspace_effect_on_self_without_action": m(True, False, "self_model") - m(False, False, "self_model"),
        "workspace_effect_on_self_with_action": m(True, True, "self_model") - m(False, True, "self_model"),
        "action_effect_on_agency_without_workspace": m(False, True, "agency") - m(False, False, "agency"),
        "action_effect_on_agency_with_workspace": m(True, True, "agency") - m(True, False, "agency"),
        "separation_workspace_on_action_off": m(True, False, "separation"),
        "separation_workspace_on_action_on": m(True, True, "separation"),
        "separation_reduction_with_action_when_workspace_on": m(True, False, "separation") - m(True, True, "separation"),
    }
    return effects


def plot_factorial(summary: pd.DataFrame, out_dir: Path) -> None:
    summary = summary.copy()
    order = [
        condition_name(False, False),
        condition_name(True, False),
        condition_name(False, True),
        condition_name(True, True),
    ]
    summary["order"] = summary["condition"].apply(order.index)
    summary = summary.sort_values("order")
    labels = ["W- A-", "W+ A-", "W- A+", "W+ A+"]
    x = np.arange(len(summary))
    width = 0.28
    plt.figure(figsize=(9, 5.6))
    plt.bar(x - width, summary["self_model_mean"], width, label="self_model")
    plt.bar(x, summary["agency_mean"], width, label="agency")
    plt.bar(x + width, summary["separation_mean"], width, label="separation")
    plt.xticks(x, labels)
    plt.ylim(0, 1)
    plt.xlabel("Workspace / Action-loop condition")
    plt.ylabel("Mean score")
    plt.title("2x2 factorial: workspace and action-outcome loop")
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "factorial_2x2_bar.png", dpi=160)
    plt.close()


def plot_interaction(df: pd.DataFrame, out_dir: Path) -> None:
    grouped = df.groupby(["workspace", "action_loop"], as_index=False)[["self_model", "agency", "separation"]].mean()
    labels = ["action off", "action on"]
    for metric in ["self_model", "agency", "separation"]:
        plt.figure(figsize=(7.5, 5.2))
        for workspace in [False, True]:
            sub = grouped[grouped["workspace"] == workspace].sort_values("action_loop")
            plt.plot([0, 1], sub[metric], marker="o", linewidth=2, label=f"workspace {'on' if workspace else 'off'}")
        plt.xticks([0, 1], labels)
        plt.ylim(0, 1)
        plt.ylabel(metric)
        plt.title(f"Interaction plot: {metric}")
        plt.grid(True, alpha=0.25)
        plt.legend()
        plt.tight_layout()
        plt.savefig(out_dir / f"interaction_{metric}.png", dpi=160)
        plt.close()


def plot_timescale(df: pd.DataFrame, out_dir: Path) -> None:
    grouped = df.groupby(["condition", "steps"], as_index=False)[["self_model", "agency", "separation"]].mean()
    for metric in ["self_model", "agency", "separation"]:
        plt.figure(figsize=(9, 5.4))
        for condition, sub in grouped.groupby("condition"):
            sub = sub.sort_values("steps")
            plt.plot(sub["steps"], sub[metric], marker="o", linewidth=1.8, label=condition.replace("__", "\n"))
        plt.xscale("log")
        plt.ylim(0, 1)
        plt.xlabel("Steps (log scale)")
        plt.ylabel(metric)
        plt.title(f"Development over time: {metric}")
        plt.grid(True, alpha=0.25)
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.savefig(out_dir / f"timescale_{metric}.png", dpi=160)
        plt.close()


def time_to_threshold(df: pd.DataFrame, threshold: float = 0.45) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (condition, seed), sub in df.groupby(["condition", "seed"]):
        sub = sub.sort_values("steps")
        row: dict[str, Any] = {"condition": condition, "seed": seed}
        for metric in ["self_model", "agency"]:
            crossed = sub[sub[metric] >= threshold]
            row[f"{metric}_time_to_{threshold}"] = int(crossed["steps"].iloc[0]) if not crossed.empty else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run 2x2 workspace/action-loop and timescale experiments.")
    parser.add_argument("--root", default="runs")
    parser.add_argument("--run-dir", default=None)
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--seed-base", type=int, default=93001)
    parser.add_argument("--final-steps", type=int, default=1800)
    parser.add_argument("--time-points", default="10,25,50,100,250,500,1000,1800,3200")
    args = parser.parse_args()

    root = Path(args.root)
    run_dir = Path(args.run_dir) if args.run_dir else latest_run(root)
    out_dir = ensure_dir(run_dir / "analysis" / f"thalamus_factorial_timescale_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    seeds = [args.seed_base + i for i in range(args.seeds)]
    time_points = [int(x.strip()) for x in args.time_points.split(",") if x.strip()]

    factorial = run_factorial(seeds, args.final_steps)
    timescale = run_timescale(seeds, time_points)
    factorial_summary = summarize_factorial(factorial)
    effects = effect_summary(factorial)
    threshold_df = time_to_threshold(timescale)

    factorial_path = out_dir / "factorial_raw.csv"
    factorial_summary_path = out_dir / "factorial_summary.csv"
    timescale_path = out_dir / "timescale_raw.csv"
    threshold_path = out_dir / "time_to_threshold.csv"
    factorial.to_csv(factorial_path, index=False, encoding="utf-8-sig")
    factorial_summary.to_csv(factorial_summary_path, index=False, encoding="utf-8-sig")
    timescale.to_csv(timescale_path, index=False, encoding="utf-8-sig")
    threshold_df.to_csv(threshold_path, index=False, encoding="utf-8-sig")

    plot_factorial(factorial_summary, out_dir)
    plot_interaction(factorial, out_dir)
    plot_timescale(timescale, out_dir)

    payload = {
        "run_dir": str(run_dir),
        "analysis_dir": str(out_dir),
        "seeds": seeds,
        "final_steps": args.final_steps,
        "time_points": time_points,
        "factorial_csv": str(factorial_path),
        "factorial_summary_csv": str(factorial_summary_path),
        "timescale_csv": str(timescale_path),
        "time_to_threshold_csv": str(threshold_path),
        "effects": effects,
        "plots": [
            str(out_dir / "factorial_2x2_bar.png"),
            str(out_dir / "interaction_self_model.png"),
            str(out_dir / "interaction_agency.png"),
            str(out_dir / "interaction_separation.png"),
            str(out_dir / "timescale_self_model.png"),
            str(out_dir / "timescale_agency.png"),
            str(out_dir / "timescale_separation.png"),
        ],
    }
    write_json(out_dir / "summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

