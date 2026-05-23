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

from mind_lab.distributed import DistributedArchitecture
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


def thalamus_config(action_feedback: bool, eval_window: int) -> dict[str, Any]:
    return {
        "workspace_capacity": 96,
        "initial_threshold": 0.52,
        "inhibition_strength": 0.45,
        "threshold_adaptation_rate": 0.08,
        "dim": 32,
        "measurement_window": eval_window,
        "enable_workspace": True,
        "enable_reticular": True,
        "enable_core": True,
        "enable_matrix": True,
        "enable_cortical_feedback": True,
        "enable_action_loop": action_feedback,
        "action_loop_variant": "full" if action_feedback else "none",
    }


def distributed_config(action_feedback: bool, eval_window: int) -> dict[str, Any]:
    return {
        "num_agents": 12,
        "world_size": 52,
        "sensor_range": 6,
        "memory_capacity": 512,
        "measurement_window": eval_window,
        "enable_action_feedback": action_feedback,
    }


def profile_row(profile: dict[str, Any]) -> dict[str, float]:
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
    for key, value in profile.get("details", {}).items():
        if np.isscalar(value):
            row[key] = float(value)
    return row


def run_one(architecture: str, action_feedback: bool, seed: int, warm_up: int, steps: int, eval_window: int) -> dict[str, Any]:
    if architecture == "thalamus":
        system = ThalamusInspiredArchitecture(thalamus_config(action_feedback, eval_window), seed=seed)
    elif architecture == "distributed":
        system = DistributedArchitecture(distributed_config(action_feedback, eval_window), seed=seed)
    else:
        raise ValueError(architecture)
    if warm_up:
        system.run_steps(warm_up)
    system.run_steps(steps)
    row = profile_row(system.evaluation_profile())
    row.update(
        {
            "architecture": architecture,
            "condition": "feedback_on" if action_feedback else "feedback_off",
            "action_feedback": action_feedback,
            "seed": seed,
            "warm_up": warm_up,
            "steps": steps,
            "eval_window": eval_window,
        }
    )
    return row


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "self_model",
        "agency",
        "separation",
        "state",
        "content",
        "temporal_continuity",
        "mean_score",
        "actual_success_rate",
        "action_agency_proxy",
        "action_prediction_error",
    ]
    available = [metric for metric in metrics if metric in df.columns]
    grouped = df.groupby(["architecture", "condition", "action_feedback"], as_index=False)[available].agg(["mean", "std"])
    grouped.columns = ["_".join(col).strip("_") for col in grouped.columns.to_flat_index()]
    return grouped.reset_index(drop=True)


def effect_summary(df: pd.DataFrame) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for architecture, sub in df.groupby("architecture"):
        means = sub.groupby("action_feedback")[["self_model", "agency", "separation"]].mean()
        if False in means.index and True in means.index:
            out[architecture] = {
                "self_model_delta_feedback_on_minus_off": float(means.loc[True, "self_model"] - means.loc[False, "self_model"]),
                "agency_delta_feedback_on_minus_off": float(means.loc[True, "agency"] - means.loc[False, "agency"]),
                "separation_delta_feedback_on_minus_off": float(means.loc[True, "separation"] - means.loc[False, "separation"]),
                "off": means.loc[False].to_dict(),
                "on": means.loc[True].to_dict(),
            }
    return out


def plot_bars(summary: pd.DataFrame, out_dir: Path) -> None:
    summary = summary.copy()
    summary["label"] = summary["architecture"] + "\n" + summary["condition"]
    summary = summary.sort_values(["architecture", "action_feedback"])
    x = np.arange(len(summary))
    width = 0.26
    plt.figure(figsize=(9.5, 5.6))
    plt.bar(x - width, summary["self_model_mean"], width, label="self_model")
    plt.bar(x, summary["agency_mean"], width, label="agency")
    plt.bar(x + width, summary["separation_mean"], width, label="separation")
    plt.xticks(x, summary["label"])
    plt.ylim(-0.1, 1)
    plt.ylabel("Score")
    plt.title("Cross-architecture action-feedback validation")
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "cross_architecture_feedback_bars.png", dpi=160)
    plt.close()


def plot_effects(effects: dict[str, Any], out_dir: Path) -> None:
    architectures = list(effects.keys())
    agency_delta = [effects[a]["agency_delta_feedback_on_minus_off"] for a in architectures]
    self_delta = [effects[a]["self_model_delta_feedback_on_minus_off"] for a in architectures]
    sep_delta = [effects[a]["separation_delta_feedback_on_minus_off"] for a in architectures]
    x = np.arange(len(architectures))
    width = 0.25
    plt.figure(figsize=(8, 5.4))
    plt.bar(x - width, self_delta, width, label="delta self_model")
    plt.bar(x, agency_delta, width, label="delta agency")
    plt.bar(x + width, sep_delta, width, label="delta separation")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.xticks(x, architectures)
    plt.ylabel("Feedback on - off")
    plt.title("Effect of action feedback by architecture")
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "cross_architecture_feedback_effects.png", dpi=160)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Cross-architecture validation of action feedback effects.")
    parser.add_argument("--root", default="runs")
    parser.add_argument("--run-dir", default=None)
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--seed-base", type=int, default=101001)
    parser.add_argument("--warm-up", type=int, default=500)
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--eval-window", type=int, default=100)
    args = parser.parse_args()

    root = Path(args.root)
    run_dir = Path(args.run_dir) if args.run_dir else latest_run(root)
    out_dir = ensure_dir(run_dir / "analysis" / f"cross_architecture_feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    seeds = [args.seed_base + i for i in range(args.seeds)]

    rows: list[dict[str, Any]] = []
    for architecture in ["distributed", "thalamus"]:
        for feedback in [False, True]:
            for seed in seeds:
                row = run_one(architecture, feedback, seed, args.warm_up, args.steps, args.eval_window)
                rows.append(row)
                print(
                    f"{architecture:12s} feedback={feedback!s:5s} seed={seed} "
                    f"self={row['self_model']:.3f} agency={row['agency']:.3f} sep={row['separation']:.3f}",
                    flush=True,
                )

    df = pd.DataFrame(rows)
    summary = summarize(df)
    effects = effect_summary(df)
    raw_path = out_dir / "cross_architecture_feedback_raw.csv"
    summary_path = out_dir / "cross_architecture_feedback_summary.csv"
    df.to_csv(raw_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    plot_bars(summary, out_dir)
    plot_effects(effects, out_dir)

    payload = {
        "run_dir": str(run_dir),
        "analysis_dir": str(out_dir),
        "seeds": seeds,
        "warm_up": args.warm_up,
        "steps": args.steps,
        "eval_window": args.eval_window,
        "raw_csv": str(raw_path),
        "summary_csv": str(summary_path),
        "plots": [
            str(out_dir / "cross_architecture_feedback_bars.png"),
            str(out_dir / "cross_architecture_feedback_effects.png"),
        ],
        "effects": effects,
    }
    write_json(out_dir / "summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

