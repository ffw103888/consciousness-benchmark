# Copyright 2026 Fuwang Feng
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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


def base_config(capacity: int, inhibition: float, eval_window: int) -> dict[str, Any]:
    return {
        "workspace_capacity": int(capacity),
        "initial_threshold": 0.52,
        "inhibition_strength": float(inhibition),
        "threshold_adaptation_rate": 0.08,
        "dim": 32,
        "measurement_window": eval_window,
        "enable_reticular": True,
        "enable_core": True,
        "enable_matrix": True,
        "enable_cortical_feedback": True,
        "enable_workspace": True,
        "enable_action_loop": True,
    }


def run_one(config: dict[str, Any], seed: int, warm_up: int, steps: int) -> dict[str, float]:
    system = ThalamusInspiredArchitecture(config, seed=seed)
    if warm_up > 0:
        system.run_steps(warm_up)
    system.run_steps(steps)
    profile = system.evaluation_profile()
    details = profile.get("details", {})
    row = {
        "self_model": float(profile["self_model"]),
        "agency": float(profile["agency"]),
        "separation": float(profile["self_model"] - profile["agency"]),
        "state": float(profile["state"]),
        "content": float(profile["content"]),
        "temporal_continuity": float(profile["temporal_continuity"]),
        "mean_score": float(
            np.mean(
                [
                    profile["self_model"],
                    profile["agency"],
                    profile["state"],
                    profile["content"],
                    profile["temporal_continuity"],
                ]
            )
        ),
    }
    for key in [
        "threshold_stability",
        "workspace_presence",
        "workspace_temporal",
        "source_diversity",
        "cortical_presence",
        "gating_agency_proxy",
        "action_agency_proxy",
        "instability",
    ]:
        row[key] = float(details.get(key, 0.0))
    return row


def run_grid(
    capacities: list[int],
    inhibitions: list[float],
    seeds: list[int],
    warm_up: int,
    steps: int,
    eval_window: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for capacity in capacities:
        for inhibition in inhibitions:
            for seed in seeds:
                cfg = base_config(capacity, inhibition, eval_window)
                row = run_one(cfg, seed, warm_up, steps)
                row.update(
                    {
                        "capacity": capacity,
                        "inhibition": inhibition,
                        "seed": seed,
                        "warm_up": warm_up,
                        "steps": steps,
                        "eval_window": eval_window,
                    }
                )
                rows.append(row)
                print(
                    f"heatmap cap={capacity:4d} inh={inhibition:.2f} seed={seed} "
                    f"self={row['self_model']:.3f} agency={row['agency']:.3f} sep={row['separation']:.3f}",
                    flush=True,
                )
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    metrics = ["self_model", "agency", "separation", "state", "content", "temporal_continuity", "mean_score"]
    grouped = df.groupby(["capacity", "inhibition"], as_index=False)[metrics].agg(["mean", "std"])
    grouped.columns = ["_".join(col).strip("_") for col in grouped.columns.to_flat_index()]
    return grouped.reset_index(drop=True)


def heatmap_matrix(summary: pd.DataFrame, capacities: list[int], inhibitions: list[float], metric: str) -> np.ndarray:
    matrix = np.full((len(inhibitions), len(capacities)), np.nan)
    for i, inhibition in enumerate(inhibitions):
        for j, capacity in enumerate(capacities):
            row = summary[(summary["capacity"] == capacity) & (np.isclose(summary["inhibition"], inhibition))]
            if not row.empty:
                matrix[i, j] = float(row.iloc[0][f"{metric}_mean"])
    return matrix


def plot_heatmap(summary: pd.DataFrame, capacities: list[int], inhibitions: list[float], metric: str, out_dir: Path) -> None:
    matrix = heatmap_matrix(summary, capacities, inhibitions, metric)
    plt.figure(figsize=(8, 5.8))
    im = plt.imshow(matrix, origin="lower", aspect="auto", cmap="viridis", vmin=-0.25 if metric == "separation" else 0, vmax=1)
    plt.colorbar(im, label=metric)
    plt.xticks(np.arange(len(capacities)), [str(x) for x in capacities])
    plt.yticks(np.arange(len(inhibitions)), [f"{x:g}" for x in inhibitions])
    plt.xlabel("workspace_capacity")
    plt.ylabel("inhibition_strength")
    plt.title(f"Thalamus parameter heatmap: {metric}")
    for i in range(len(inhibitions)):
        for j in range(len(capacities)):
            value = matrix[i, j]
            if not np.isnan(value):
                plt.text(j, i, f"{value:.2f}", ha="center", va="center", color="white" if value < 0.55 else "black", fontsize=8)
    plt.tight_layout()
    plt.savefig(out_dir / f"heatmap_{metric}.png", dpi=160)
    plt.close()


def plot_tradeoff(summary: pd.DataFrame, out_dir: Path) -> None:
    plt.figure(figsize=(7, 6))
    sizes = 35 + 0.15 * summary["capacity"].to_numpy(dtype=float)
    scatter = plt.scatter(
        summary["self_model_mean"],
        summary["agency_mean"],
        c=summary["inhibition"].to_numpy(dtype=float),
        s=sizes,
        alpha=0.75,
        cmap="plasma",
    )
    plt.colorbar(scatter, label="inhibition_strength")
    plt.xlabel("self_model")
    plt.ylabel("agency")
    plt.title("Self/agency tradeoff by capacity and inhibition")
    plt.grid(True, alpha=0.25)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(out_dir / "self_agency_tradeoff.png", dpi=160)
    plt.close()


def best_regions(summary: pd.DataFrame) -> dict[str, Any]:
    data = summary.copy()
    data["balanced_score"] = np.minimum(data["self_model_mean"], data["agency_mean"])
    data["combined_score"] = 0.5 * data["self_model_mean"] + 0.5 * data["agency_mean"] - 0.25 * np.abs(data["separation_mean"])
    best_balanced = data.sort_values("balanced_score", ascending=False).head(5)
    best_combined = data.sort_values("combined_score", ascending=False).head(5)
    return {
        "best_balanced": best_balanced[
            ["capacity", "inhibition", "self_model_mean", "agency_mean", "separation_mean", "balanced_score"]
        ].to_dict(orient="records"),
        "best_combined": best_combined[
            ["capacity", "inhibition", "self_model_mean", "agency_mean", "separation_mean", "combined_score"]
        ].to_dict(orient="records"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Workspace capacity x inhibition heatmap for thalamus architecture.")
    parser.add_argument("--root", default="runs")
    parser.add_argument("--run-dir", default=None)
    parser.add_argument("--capacities", default="50,100,200,500,1000")
    parser.add_argument("--inhibitions", default="0,0.2,0.4,0.6,0.8,1.0")
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--seed-base", type=int, default=97001)
    parser.add_argument("--warm-up", type=int, default=500)
    parser.add_argument("--steps", type=int, default=1500)
    parser.add_argument("--eval-window", type=int, default=100)
    args = parser.parse_args()

    root = Path(args.root)
    run_dir = Path(args.run_dir) if args.run_dir else latest_run(root)
    out_dir = ensure_dir(run_dir / "analysis" / f"thalamus_parameter_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    capacities = [int(x.strip()) for x in args.capacities.split(",") if x.strip()]
    inhibitions = [float(x.strip()) for x in args.inhibitions.split(",") if x.strip()]
    seeds = [args.seed_base + i for i in range(args.seeds)]
    df = run_grid(capacities, inhibitions, seeds, args.warm_up, args.steps, args.eval_window)
    summary = summarize(df)
    raw_path = out_dir / "parameter_heatmap_raw.csv"
    summary_path = out_dir / "parameter_heatmap_summary.csv"
    df.to_csv(raw_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    for metric in ["self_model", "agency", "separation", "mean_score"]:
        plot_heatmap(summary, capacities, inhibitions, metric, out_dir)
    plot_tradeoff(summary, out_dir)
    regions = best_regions(summary)

    payload = {
        "run_dir": str(run_dir),
        "analysis_dir": str(out_dir),
        "capacities": capacities,
        "inhibitions": inhibitions,
        "seeds": seeds,
        "warm_up": args.warm_up,
        "steps": args.steps,
        "eval_window": args.eval_window,
        "raw_csv": str(raw_path),
        "summary_csv": str(summary_path),
        "plots": [
            str(out_dir / "heatmap_self_model.png"),
            str(out_dir / "heatmap_agency.png"),
            str(out_dir / "heatmap_separation.png"),
            str(out_dir / "heatmap_mean_score.png"),
            str(out_dir / "self_agency_tradeoff.png"),
        ],
        **regions,
    }
    write_json(out_dir / "summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

