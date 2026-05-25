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


def config_for_variant(variant: str, eval_window: int) -> dict[str, Any]:
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
        "enable_workspace": True,
        "enable_action_loop": variant != "none",
        "action_loop_variant": variant,
        "action_learning_rate": 0.06,
    }


def run_one(variant: str, seed: int, warm_up: int, steps: int, eval_window: int) -> dict[str, Any]:
    system = ThalamusInspiredArchitecture(config_for_variant(variant, eval_window), seed=seed)
    if warm_up:
        system.run_steps(warm_up)
    system.run_steps(steps)
    profile = system.evaluation_profile()
    details = profile.get("details", {})
    row = {
        "variant": variant,
        "seed": seed,
        "warm_up": warm_up,
        "steps": steps,
        "eval_window": eval_window,
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
        "action_agency_proxy",
        "action_prediction_error",
        "action_predicted_gain",
        "action_intention_alignment",
        "action_presence",
        "gating_agency_proxy",
        "threshold_stability",
        "workspace_presence",
        "workspace_temporal",
        "source_diversity",
    ]:
        row[key] = float(details.get(key, 0.0))
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
        "action_agency_proxy",
        "action_prediction_error",
        "action_intention_alignment",
        "action_presence",
    ]
    grouped = df.groupby("variant", as_index=False)[metrics].agg(["mean", "std"])
    grouped.columns = ["_".join(col).strip("_") for col in grouped.columns.to_flat_index()]
    return grouped.reset_index(drop=True)


def plot_variant_bars(summary: pd.DataFrame, out_dir: Path) -> None:
    order = ["none", "minimal", "learning", "intention", "full"]
    summary = summary.copy()
    summary["order"] = summary["variant"].apply(lambda x: order.index(x))
    summary = summary.sort_values("order")
    x = np.arange(len(summary))
    width = 0.22
    plt.figure(figsize=(10, 5.6))
    plt.bar(x - width, summary["self_model_mean"], width, label="self_model")
    plt.bar(x, summary["agency_mean"], width, label="agency")
    plt.bar(x + width, summary["separation_mean"], width, label="separation")
    plt.xticks(x, summary["variant"])
    plt.ylim(-0.1, 1)
    plt.ylabel("Score")
    plt.title("Action-loop variants with workspace enabled")
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "action_loop_variant_scores.png", dpi=160)
    plt.close()


def plot_mechanism_bars(summary: pd.DataFrame, out_dir: Path) -> None:
    order = ["none", "minimal", "learning", "intention", "full"]
    summary = summary.copy()
    summary["order"] = summary["variant"].apply(lambda x: order.index(x))
    summary = summary.sort_values("order")
    x = np.arange(len(summary))
    width = 0.2
    plt.figure(figsize=(11, 5.6))
    plt.bar(x - 1.5 * width, summary["action_agency_proxy_mean"], width, label="action agency")
    plt.bar(x - 0.5 * width, 1.0 - summary["action_prediction_error_mean"], width, label="predictability")
    plt.bar(x + 0.5 * width, summary["action_intention_alignment_mean"], width, label="intention alignment")
    plt.bar(x + 1.5 * width, summary["action_presence_mean"], width, label="action presence")
    plt.xticks(x, summary["variant"])
    plt.ylim(0, 1)
    plt.ylabel("Mechanism proxy")
    plt.title("Action-loop internal mechanism diagnostics")
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "action_loop_mechanism_diagnostics.png", dpi=160)
    plt.close()


def plot_agency_vs_error(df: pd.DataFrame, out_dir: Path) -> None:
    plt.figure(figsize=(7, 5.6))
    for variant, sub in df.groupby("variant"):
        plt.scatter(sub["action_prediction_error"], sub["agency"], label=variant, s=45, alpha=0.75)
    plt.xlabel("Prediction error")
    plt.ylabel("Agency")
    plt.title("Agency vs action prediction error")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "agency_vs_prediction_error.png", dpi=160)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run action-loop variant experiments for thalamus architecture.")
    parser.add_argument("--root", default="runs")
    parser.add_argument("--run-dir", default=None)
    parser.add_argument("--variants", default="none,minimal,learning,intention,full")
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--seed-base", type=int, default=99001)
    parser.add_argument("--warm-up", type=int, default=500)
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--eval-window", type=int, default=100)
    args = parser.parse_args()

    root = Path(args.root)
    run_dir = Path(args.run_dir) if args.run_dir else latest_run(root)
    out_dir = ensure_dir(run_dir / "analysis" / f"thalamus_action_loop_variants_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    variants = [x.strip() for x in args.variants.split(",") if x.strip()]
    seeds = [args.seed_base + i for i in range(args.seeds)]

    rows: list[dict[str, Any]] = []
    for variant in variants:
        for seed in seeds:
            row = run_one(variant, seed, args.warm_up, args.steps, args.eval_window)
            rows.append(row)
            print(
                f"variant {variant:10s} seed={seed} self={row['self_model']:.3f} "
                f"agency={row['agency']:.3f} pred_err={row['action_prediction_error']:.3f}",
                flush=True,
            )
    df = pd.DataFrame(rows)
    summary = summarize(df)
    raw_path = out_dir / "action_loop_variants_raw.csv"
    summary_path = out_dir / "action_loop_variants_summary.csv"
    df.to_csv(raw_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    plot_variant_bars(summary, out_dir)
    plot_mechanism_bars(summary, out_dir)
    plot_agency_vs_error(df, out_dir)

    ordered = summary.copy()
    ordered["variant_order"] = ordered["variant"].apply(lambda x: variants.index(x))
    ordered = ordered.sort_values("variant_order")
    effects = {
        "agency_by_variant": {
            row["variant"]: float(row["agency_mean"])
            for _, row in ordered.iterrows()
        },
        "prediction_error_by_variant": {
            row["variant"]: float(row["action_prediction_error_mean"])
            for _, row in ordered.iterrows()
        },
    }
    if "none" in effects["agency_by_variant"] and "full" in effects["agency_by_variant"]:
        effects["full_minus_none_agency"] = effects["agency_by_variant"]["full"] - effects["agency_by_variant"]["none"]
    if "minimal" in effects["agency_by_variant"] and "learning" in effects["agency_by_variant"]:
        effects["learning_minus_minimal_agency"] = effects["agency_by_variant"]["learning"] - effects["agency_by_variant"]["minimal"]
    if "learning" in effects["agency_by_variant"] and "full" in effects["agency_by_variant"]:
        effects["full_minus_learning_agency"] = effects["agency_by_variant"]["full"] - effects["agency_by_variant"]["learning"]

    payload = {
        "run_dir": str(run_dir),
        "analysis_dir": str(out_dir),
        "variants": variants,
        "seeds": seeds,
        "warm_up": args.warm_up,
        "steps": args.steps,
        "eval_window": args.eval_window,
        "raw_csv": str(raw_path),
        "summary_csv": str(summary_path),
        "plots": [
            str(out_dir / "action_loop_variant_scores.png"),
            str(out_dir / "action_loop_mechanism_diagnostics.png"),
            str(out_dir / "agency_vs_prediction_error.png"),
        ],
        "effects": effects,
    }
    write_json(out_dir / "summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

