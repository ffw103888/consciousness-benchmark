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


def base_config(eval_window: int) -> dict[str, Any]:
    return {
        "workspace_capacity": 96,
        "initial_threshold": 0.52,
        "inhibition_strength": 0.45,
        "threshold_adaptation_rate": 0.08,
        "dim": 32,
        "measurement_window": eval_window,
        "enable_reticular": True,
        "enable_core": True,
        "enable_matrix": True,
        "enable_cortical_feedback": True,
    }


def condition_config(condition: str, eval_window: int) -> dict[str, Any]:
    cfg = base_config(eval_window)
    if condition == "W-A-":
        cfg.update({"enable_workspace": False, "enable_action_loop": False})
    elif condition == "W+A-":
        cfg.update({"enable_workspace": True, "enable_action_loop": False})
    elif condition == "W-A+":
        cfg.update({"enable_workspace": False, "enable_action_loop": True})
    elif condition == "W+A+":
        cfg.update({"enable_workspace": True, "enable_action_loop": True})
    else:
        raise ValueError(condition)
    return cfg


def profile_row(system: ThalamusInspiredArchitecture, eval_window: int) -> dict[str, Any]:
    profile = system.evaluation_profile()
    window = system.history[-eval_window:]
    fields = ["workspace_size", "gated_count", "threshold", "cortical_norm", "action_agency"]
    stability = {
        f"{field}_std": float(np.std([record.get(field, 0.0) for record in window])) if window else 0.0
        for field in fields
    }
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
        **stability,
    }
    for key, value in profile.get("details", {}).items():
        if np.isscalar(value):
            row[key] = float(value)
    return row


def run_experiment(
    conditions: list[str],
    seeds: list[int],
    warm_up_steps: int,
    eval_window: int,
    time_points: list[int],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for condition in conditions:
        for seed in seeds:
            system = ThalamusInspiredArchitecture(condition_config(condition, eval_window), seed=seed)
            elapsed = 0
            if warm_up_steps > 0:
                system.run_steps(warm_up_steps)
                elapsed = warm_up_steps
            for target in time_points:
                if target < warm_up_steps:
                    continue
                delta = target - elapsed
                if delta > 0:
                    system.run_steps(delta)
                    elapsed = target
                row = profile_row(system, eval_window)
                row.update(
                    {
                        "condition": condition,
                        "seed": seed,
                        "steps": elapsed,
                        "warm_up_steps": warm_up_steps,
                        "eval_window": eval_window,
                    }
                )
                rows.append(row)
            print(f"robust-timescale {condition:5s} seed={seed} done to {elapsed}", flush=True)
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    metrics = ["self_model", "agency", "separation", "state", "content", "temporal_continuity", "mean_score"]
    grouped = df.groupby(["condition", "steps"], as_index=False)[metrics].agg(["mean", "std"])
    grouped.columns = ["_".join(col).strip("_") for col in grouped.columns.to_flat_index()]
    return grouped.reset_index(drop=True)


def steady_state_summary(df: pd.DataFrame) -> pd.DataFrame:
    final_step = int(df["steps"].max())
    final = df[df["steps"] == final_step].copy()
    metrics = ["self_model", "agency", "separation", "workspace_size_std", "gated_count_std", "action_agency_std"]
    grouped = final.groupby("condition", as_index=False)[metrics].agg(["mean", "std"])
    grouped.columns = ["_".join(col).strip("_") for col in grouped.columns.to_flat_index()]
    return grouped.reset_index(drop=True)


def time_to_stability(df: pd.DataFrame, threshold: float, stability_epsilon: float) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (condition, seed), sub in df.groupby(["condition", "seed"]):
        sub = sub.sort_values("steps")
        row: dict[str, Any] = {"condition": condition, "seed": seed}
        for metric in ["self_model", "agency"]:
            crossed = sub[sub[metric] >= threshold]
            row[f"{metric}_time_to_{threshold}"] = int(crossed["steps"].iloc[0]) if not crossed.empty else np.nan
        for metric in ["self_model", "agency", "separation"]:
            values = sub[metric].to_numpy(dtype=float)
            steps = sub["steps"].to_numpy(dtype=int)
            stable_at = np.nan
            for idx in range(len(values)):
                tail = values[idx:]
                if len(tail) >= 2 and float(np.max(tail) - np.min(tail)) <= stability_epsilon:
                    stable_at = int(steps[idx])
                    break
            row[f"{metric}_stable_at_eps_{stability_epsilon}"] = stable_at
        rows.append(row)
    return pd.DataFrame(rows)


def plot_timescale(summary: pd.DataFrame, out_dir: Path) -> None:
    for metric in ["self_model", "agency", "separation"]:
        plt.figure(figsize=(9, 5.5))
        for condition, sub in summary.groupby("condition"):
            sub = sub.sort_values("steps")
            mean = sub[f"{metric}_mean"].to_numpy(dtype=float)
            std = sub[f"{metric}_std"].fillna(0.0).to_numpy(dtype=float)
            steps = sub["steps"].to_numpy(dtype=float)
            plt.plot(steps, mean, marker="o", linewidth=2, label=condition)
            plt.fill_between(steps, np.clip(mean - std, 0, 1), np.clip(mean + std, 0, 1), alpha=0.12)
        plt.xscale("log")
        plt.ylim(-0.25 if metric == "separation" else 0, 1)
        plt.xlabel("Steps after start (log scale)")
        plt.ylabel(metric)
        plt.title(f"Robust timescale with warm-up/window: {metric}")
        plt.grid(True, alpha=0.25)
        plt.legend()
        plt.tight_layout()
        plt.savefig(out_dir / f"robust_timescale_{metric}.png", dpi=160)
        plt.close()


def plot_final_bars(final_summary: pd.DataFrame, out_dir: Path) -> None:
    order = ["W-A-", "W+A-", "W-A+", "W+A+"]
    final_summary = final_summary.copy()
    final_summary["order"] = final_summary["condition"].apply(lambda x: order.index(x))
    final_summary = final_summary.sort_values("order")
    x = np.arange(len(final_summary))
    width = 0.28
    plt.figure(figsize=(8.5, 5.4))
    plt.bar(x - width, final_summary["self_model_mean"], width, label="self_model")
    plt.bar(x, final_summary["agency_mean"], width, label="agency")
    plt.bar(x + width, final_summary["separation_mean"], width, label="separation")
    plt.xticks(x, final_summary["condition"])
    plt.ylim(-0.25, 1)
    plt.ylabel("Final-window score")
    plt.title("Robust final scores by condition")
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "robust_final_condition_bars.png", dpi=160)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Robust thalamus timescale experiment with warm-up/window evaluation.")
    parser.add_argument("--root", default="runs")
    parser.add_argument("--run-dir", default=None)
    parser.add_argument("--warm-up-steps", type=int, default=500)
    parser.add_argument("--eval-window", type=int, default=100)
    parser.add_argument("--time-points", default="500,1000,2000,5000,10000")
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--seed-base", type=int, default=95001)
    parser.add_argument("--threshold", type=float, default=0.45)
    parser.add_argument("--stability-epsilon", type=float, default=0.05)
    args = parser.parse_args()

    root = Path(args.root)
    run_dir = Path(args.run_dir) if args.run_dir else latest_run(root)
    out_dir = ensure_dir(run_dir / "analysis" / f"thalamus_timescale_robust_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    conditions = ["W-A-", "W+A-", "W-A+", "W+A+"]
    seeds = [args.seed_base + idx for idx in range(args.seeds)]
    time_points = [int(x.strip()) for x in args.time_points.split(",") if x.strip()]
    df = run_experiment(conditions, seeds, args.warm_up_steps, args.eval_window, time_points)
    summary = summarize(df)
    final_summary = steady_state_summary(df)
    threshold_df = time_to_stability(df, args.threshold, args.stability_epsilon)

    raw_path = out_dir / "robust_timescale_raw.csv"
    summary_path = out_dir / "robust_timescale_summary.csv"
    final_path = out_dir / "robust_final_summary.csv"
    threshold_path = out_dir / "robust_time_to_threshold_stability.csv"
    df.to_csv(raw_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    final_summary.to_csv(final_path, index=False, encoding="utf-8-sig")
    threshold_df.to_csv(threshold_path, index=False, encoding="utf-8-sig")
    plot_timescale(summary, out_dir)
    plot_final_bars(final_summary, out_dir)

    payload = {
        "run_dir": str(run_dir),
        "analysis_dir": str(out_dir),
        "conditions": conditions,
        "seeds": seeds,
        "warm_up_steps": args.warm_up_steps,
        "eval_window": args.eval_window,
        "time_points": time_points,
        "raw_csv": str(raw_path),
        "summary_csv": str(summary_path),
        "final_summary_csv": str(final_path),
        "threshold_stability_csv": str(threshold_path),
        "plots": [
            str(out_dir / "robust_timescale_self_model.png"),
            str(out_dir / "robust_timescale_agency.png"),
            str(out_dir / "robust_timescale_separation.png"),
            str(out_dir / "robust_final_condition_bars.png"),
        ],
    }
    write_json(out_dir / "summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

