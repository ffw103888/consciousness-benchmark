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


def base_config() -> dict[str, Any]:
    return {
        "workspace_capacity": 96,
        "initial_threshold": 0.52,
        "inhibition_strength": 0.45,
        "threshold_adaptation_rate": 0.08,
        "dim": 32,
    }


def run_one(config: dict[str, Any], seed: int, steps: int) -> dict[str, Any]:
    system = ThalamusInspiredArchitecture(config, seed=seed)
    system.run_steps(steps)
    profile = system.evaluation_profile()
    scores = profile["scores"] if "scores" in profile else {k: profile[k] for k in ["state", "content", "self_model", "agency", "temporal_continuity"]}
    details = profile.get("details", {})
    row = {
        **{f"score_{k}": float(v) for k, v in scores.items()},
        "separation": float(scores["self_model"] - scores["agency"]),
        "mean_score": float(np.mean(list(scores.values()))),
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


def build_conditions() -> list[dict[str, Any]]:
    return [
        {"condition_type": "ablation", "condition": "full", "config": {}},
        {"condition_type": "ablation", "condition": "no_reticular", "config": {"enable_reticular": False}},
        {"condition_type": "ablation", "condition": "no_workspace", "config": {"enable_workspace": False}},
        {"condition_type": "ablation", "condition": "no_matrix", "config": {"enable_matrix": False}},
        {"condition_type": "ablation", "condition": "no_cortical_feedback", "config": {"enable_cortical_feedback": False}},
        {
            "condition_type": "ablation",
            "condition": "core_only",
            "config": {
                "enable_reticular": False,
                "enable_workspace": False,
                "enable_matrix": False,
                "enable_cortical_feedback": False,
            },
        },
        {"condition_type": "ablation", "condition": "with_action_loop", "config": {"enable_action_loop": True}},
    ]


def build_parameter_scans() -> list[dict[str, Any]]:
    conditions: list[dict[str, Any]] = []
    for value in [0.0, 0.2, 0.45, 0.6, 0.8, 1.0]:
        conditions.append(
            {
                "condition_type": "scan_inhibition",
                "condition": f"inhibition_{value:g}",
                "parameter": "inhibition_strength",
                "parameter_value": value,
                "config": {"inhibition_strength": value},
            }
        )
    for value in [0.01, 0.04, 0.08, 0.16, 0.32]:
        conditions.append(
            {
                "condition_type": "scan_threshold_adaptation",
                "condition": f"adaptation_{value:g}",
                "parameter": "threshold_adaptation_rate",
                "parameter_value": value,
                "config": {"threshold_adaptation_rate": value},
            }
        )
    for value in [16, 32, 64, 96, 160]:
        conditions.append(
            {
                "condition_type": "scan_workspace_capacity",
                "condition": f"capacity_{value}",
                "parameter": "workspace_capacity",
                "parameter_value": value,
                "config": {"workspace_capacity": value},
            }
        )
    return conditions


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    metrics = ["score_self_model", "score_agency", "separation", "score_state", "score_content", "score_temporal_continuity", "mean_score"]
    grouped = df.groupby(["condition_type", "condition"], as_index=False)[metrics].agg(["mean", "std"])
    grouped.columns = ["_".join(col).strip("_") for col in grouped.columns.to_flat_index()]
    return grouped.reset_index(drop=True)


def plot_ablation(summary: pd.DataFrame, out_dir: Path) -> None:
    ab = summary[summary["condition_type"] == "ablation"].copy()
    if ab.empty:
        return
    order = ["full", "no_reticular", "no_workspace", "no_matrix", "no_cortical_feedback", "core_only", "with_action_loop"]
    ab["order"] = ab["condition"].apply(lambda x: order.index(x) if x in order else len(order))
    ab = ab.sort_values("order")
    x = np.arange(len(ab))
    width = 0.28
    plt.figure(figsize=(11, 5.8))
    plt.bar(x - width, ab["score_self_model_mean"], width, label="self_model")
    plt.bar(x, ab["score_agency_mean"], width, label="agency")
    plt.bar(x + width, ab["separation_mean"], width, label="separation")
    plt.xticks(x, ab["condition"], rotation=25, ha="right")
    plt.ylim(0, 1)
    plt.ylabel("Score")
    plt.title("Thalamus ablations: self-model / agency separation")
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "ablation_self_agency_bar.png", dpi=160)
    plt.close()


def plot_scans(df: pd.DataFrame, out_dir: Path) -> None:
    for condition_type, title in [
        ("scan_inhibition", "Inhibition strength scan"),
        ("scan_threshold_adaptation", "Threshold adaptation scan"),
        ("scan_workspace_capacity", "Workspace capacity scan"),
    ]:
        sub = df[df["condition_type"] == condition_type].copy()
        if sub.empty:
            continue
        grouped = sub.groupby("parameter_value", as_index=False)[["score_self_model", "score_agency", "separation"]].mean()
        plt.figure(figsize=(8, 5.2))
        plt.plot(grouped["parameter_value"], grouped["score_self_model"], marker="o", label="self_model")
        plt.plot(grouped["parameter_value"], grouped["score_agency"], marker="o", label="agency")
        plt.plot(grouped["parameter_value"], grouped["separation"], marker="o", label="separation")
        plt.ylim(0, 1)
        plt.xlabel(sub["parameter"].iloc[0])
        plt.ylabel("Score")
        plt.title(title)
        plt.grid(True, alpha=0.25)
        plt.legend()
        plt.tight_layout()
        plt.savefig(out_dir / f"{condition_type}.png", dpi=160)
        plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run thalamus ablations and parameter scans.")
    parser.add_argument("--root", default="runs")
    parser.add_argument("--run-dir", default=None)
    parser.add_argument("--steps", type=int, default=1200)
    parser.add_argument("--seeds", type=int, default=6)
    parser.add_argument("--seed-base", type=int, default=91001)
    parser.add_argument("--skip-scans", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    run_dir = Path(args.run_dir) if args.run_dir else latest_run(root)
    out_dir = ensure_dir(run_dir / "analysis" / f"thalamus_ablations_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    conditions = build_conditions()
    if not args.skip_scans:
        conditions.extend(build_parameter_scans())

    rows: list[dict[str, Any]] = []
    for condition in conditions:
        for seed_idx in range(args.seeds):
            seed = args.seed_base + seed_idx
            cfg = {**base_config(), **condition["config"]}
            row = run_one(cfg, seed=seed, steps=args.steps)
            row.update(
                {
                    "seed": seed,
                    "steps": args.steps,
                    "condition_type": condition["condition_type"],
                    "condition": condition["condition"],
                    "parameter": condition.get("parameter", ""),
                    "parameter_value": condition.get("parameter_value", np.nan),
                    "config": json.dumps(cfg, sort_keys=True),
                }
            )
            rows.append(row)
            print(
                f"{condition['condition_type']:24s} {condition['condition']:24s} seed={seed} "
                f"self={row['score_self_model']:.3f} agency={row['score_agency']:.3f} sep={row['separation']:.3f}",
                flush=True,
            )

    df = pd.DataFrame(rows)
    summary = summarize(df)
    raw_path = out_dir / "thalamus_ablation_raw.csv"
    summary_path = out_dir / "thalamus_ablation_summary.csv"
    df.to_csv(raw_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    plot_ablation(summary, out_dir)
    plot_scans(df, out_dir)

    full = summary[(summary["condition_type"] == "ablation") & (summary["condition"] == "full")]
    with_action = summary[(summary["condition_type"] == "ablation") & (summary["condition"] == "with_action_loop")]
    no_workspace = summary[(summary["condition_type"] == "ablation") & (summary["condition"] == "no_workspace")]
    conclusions = []
    if not full.empty:
        conclusions.append(
            f"Full architecture mean separation={full.iloc[0]['separation_mean']:.3f} "
            f"(self={full.iloc[0]['score_self_model_mean']:.3f}, agency={full.iloc[0]['score_agency_mean']:.3f})."
        )
    if not with_action.empty and not full.empty:
        delta = with_action.iloc[0]["score_agency_mean"] - full.iloc[0]["score_agency_mean"]
        conclusions.append(f"Adding an explicit action-outcome loop changes agency by {delta:+.3f}.")
    if not no_workspace.empty and not full.empty:
        delta_self = no_workspace.iloc[0]["score_self_model_mean"] - full.iloc[0]["score_self_model_mean"]
        conclusions.append(f"Removing the workspace changes self_model by {delta_self:+.3f}.")

    payload = {
        "run_dir": str(run_dir),
        "analysis_dir": str(out_dir),
        "steps": args.steps,
        "seeds": args.seeds,
        "raw_csv": str(raw_path),
        "summary_csv": str(summary_path),
        "plots": [
            str(out_dir / "ablation_self_agency_bar.png"),
            str(out_dir / "scan_inhibition.png"),
            str(out_dir / "scan_threshold_adaptation.png"),
            str(out_dir / "scan_workspace_capacity.png"),
        ],
        "conclusions": conclusions,
    }
    write_json(out_dir / "summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

