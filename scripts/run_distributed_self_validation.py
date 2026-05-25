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
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mind_lab.utils import ensure_dir, safe_corr, write_json
from mind_lab.validation import make_system, run_independent_validation, run_steps
from scripts.run_self_model_diagnostics import markdown_table


def distributed_self_conditions() -> list[dict[str, Any]]:
    base = {
        "architecture": "distributed",
        "config": {
            "num_agents": 8,
            "world_size": 52,
            "sensor_range": 6,
            "memory_capacity": 512,
            "measurement_window": 128,
            "enable_coordination": True,
            "enable_action_feedback": True,
        },
    }
    variants = [
        ("agents_8_feedback_on", {}),
        ("agents_8_feedback_off", {"enable_action_feedback": False}),
        ("agents_4", {"num_agents": 4}),
        ("agents_16", {"num_agents": 16}),
        ("no_coordination_feedback_on", {"enable_coordination": False}),
        ("no_coordination_feedback_off", {"enable_coordination": False, "enable_action_feedback": False}),
        ("sparse_sensors", {"sensor_range": 3}),
        ("dense_sensors", {"sensor_range": 10}),
        ("shifted_goal", {"global_goal_xy": [14.0, 42.0]}),
        ("large_world", {"world_size": 72, "global_goal_xy": [49.0, 25.0]}),
    ]
    conditions = []
    for name, updates in variants:
        config = {**base["config"], **updates}
        conditions.append({"architecture": "distributed", "condition": name, "config": config})
    return conditions


def run_one(condition: dict[str, Any], seed: int, warmup: int, quick: bool) -> dict[str, Any]:
    system = make_system("distributed", condition["config"], seed)
    run_steps(system, warmup)
    validation = run_independent_validation(system, seed=seed + 1_100_000, quick=quick)
    profile = system.evaluation_profile()
    details = profile.get("details", {})
    test_scores = {item["test"]: float(item["score"]) for item in validation["tests"]}
    row = {
        "condition": condition["condition"],
        "seed": seed,
        "num_agents": int(condition["config"]["num_agents"]),
        "world_size": int(condition["config"]["world_size"]),
        "sensor_range": int(condition["config"]["sensor_range"]),
        "enable_coordination": bool(condition["config"].get("enable_coordination", True)),
        "enable_action_feedback": bool(condition["config"].get("enable_action_feedback", True)),
        "proxy_self_model": float(profile["self_model"]),
        "proxy_boundary_self": float(details.get("boundary_self_proxy", profile["self_model"])),
        "proxy_temporal_self": float(details.get("temporal_self_proxy", profile["temporal_continuity"])),
        "proxy_ownership_self": float(details.get("ownership_self_proxy", profile["agency"])),
        "proxy_legacy_self_model": float(details.get("legacy_self_model_stability", profile["self_model"])),
        "independent_self_model": float(validation["independent_self_model"]),
        "independent_core_boundary_self": float(
            np.mean(
                [
                    test_scores.get("boundary_perturbation", 0.0),
                    test_scores.get("architecture_self_probe", 0.0),
                ]
            )
        ),
        "independent_identity_ownership_self": float(
            np.mean(
                [
                    test_scores.get("computational_mirror", 0.0),
                    test_scores.get("ownership_attribution", 0.0),
                ]
            )
        ),
        "test_boundary_perturbation": test_scores.get("boundary_perturbation", 0.0),
        "test_computational_mirror": test_scores.get("computational_mirror", 0.0),
        "test_ownership_attribution": test_scores.get("ownership_attribution", 0.0),
        "test_architecture_self_probe": test_scores.get("architecture_self_probe", 0.0),
        "proxy_agency": float(profile["agency"]),
        "independent_agency": float(validation["independent_agency"]),
    }
    row["boundary_discrepancy"] = row["proxy_boundary_self"] - row["independent_core_boundary_self"]
    row["temporal_discrepancy"] = row["proxy_temporal_self"] - row["test_computational_mirror"]
    row["ownership_discrepancy"] = row["proxy_ownership_self"] - row["test_ownership_attribution"]
    return row


def correlations(df: pd.DataFrame) -> dict[str, float]:
    return {
        "self_proxy_vs_independent": safe_corr(df["proxy_self_model"].to_numpy(float), df["independent_self_model"].to_numpy(float)),
        "boundary_proxy_vs_core_boundary": safe_corr(df["proxy_boundary_self"].to_numpy(float), df["independent_core_boundary_self"].to_numpy(float)),
        "temporal_proxy_vs_mirror": safe_corr(df["proxy_temporal_self"].to_numpy(float), df["test_computational_mirror"].to_numpy(float)),
        "ownership_proxy_vs_ownership_test": safe_corr(df["proxy_ownership_self"].to_numpy(float), df["test_ownership_attribution"].to_numpy(float)),
        "agency_proxy_vs_independent": safe_corr(df["proxy_agency"].to_numpy(float), df["independent_agency"].to_numpy(float)),
    }


def save_plots(raw: pd.DataFrame, summary: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    pairs = [
        ("proxy_boundary_self", "independent_core_boundary_self", "Boundary self"),
        ("proxy_temporal_self", "test_computational_mirror", "Temporal self"),
        ("proxy_ownership_self", "test_ownership_attribution", "Ownership self"),
    ]
    for ax, (x_col, y_col, title) in zip(axes, pairs):
        ax.scatter(raw[x_col], raw[y_col], s=45, alpha=0.75)
        ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.55)
        r = safe_corr(raw[x_col].to_numpy(float), raw[y_col].to_numpy(float))
        ax.set_title(f"{title} (r={r:.2f})")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "distributed_self_proxy_scatter.png", dpi=180)
    plt.close(fig)

    labels = list(summary["condition"])
    x = np.arange(len(summary))
    width = 0.22
    fig, ax = plt.subplots(figsize=(13, 5.2))
    ax.bar(x - width, summary["proxy_boundary_self"], width, label="boundary proxy", alpha=0.8)
    ax.bar(x, summary["independent_core_boundary_self"], width, label="core boundary independent", alpha=0.8)
    ax.bar(x + width, summary["proxy_ownership_self"], width, label="ownership proxy", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Distributed self validation across architecture conditions")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "distributed_self_conditions.png", dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run expanded distributed self-model validation conditions.")
    parser.add_argument("--output-root", type=Path, default=Path("runs") / "measurement_validation")
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--warmup", type=int, default=180)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed-base", type=int, default=20260521)
    args = parser.parse_args()

    out_dir = ensure_dir(args.output_root / f"distributed_self_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    rows = []
    conditions = distributed_self_conditions()
    for idx, condition in enumerate(conditions):
        for seed_idx in range(args.seeds):
            rows.append(run_one(condition, args.seed_base + idx * 1000 + seed_idx, args.warmup, args.quick))
    raw = pd.DataFrame(rows)
    raw.to_csv(out_dir / "distributed_self_raw.csv", index=False)
    summary = raw.groupby("condition", as_index=False).agg(
        proxy_self_model=("proxy_self_model", "mean"),
        proxy_boundary_self=("proxy_boundary_self", "mean"),
        proxy_temporal_self=("proxy_temporal_self", "mean"),
        proxy_ownership_self=("proxy_ownership_self", "mean"),
        proxy_legacy_self_model=("proxy_legacy_self_model", "mean"),
        independent_self_model=("independent_self_model", "mean"),
        independent_core_boundary_self=("independent_core_boundary_self", "mean"),
        independent_identity_ownership_self=("independent_identity_ownership_self", "mean"),
        test_boundary_perturbation=("test_boundary_perturbation", "mean"),
        test_computational_mirror=("test_computational_mirror", "mean"),
        test_ownership_attribution=("test_ownership_attribution", "mean"),
        test_architecture_self_probe=("test_architecture_self_probe", "mean"),
        proxy_agency=("proxy_agency", "mean"),
        independent_agency=("independent_agency", "mean"),
    )
    summary.to_csv(out_dir / "distributed_self_summary.csv", index=False)
    save_plots(raw, summary, out_dir)
    corr = correlations(raw)
    report = [
        "# Distributed Self Validation",
        "",
        "## Correlations",
        "",
        "```json",
        json.dumps(corr, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Condition Summary",
        "",
        markdown_table(summary, max_rows=30),
        "",
        "## Guardrail",
        "",
        "This expanded grid tests whether distributed self proxies remain valid beyond feedback_on/off. It is still operational validation, not a claim about subjective selfhood.",
    ]
    (out_dir / "distributed_self_report.md").write_text("\n".join(report), encoding="utf-8")
    payload = {
        "output_dir": str(out_dir),
        "rows": len(raw),
        "correlations": corr,
        "files": {
            "raw": str(out_dir / "distributed_self_raw.csv"),
            "summary": str(out_dir / "distributed_self_summary.csv"),
            "report": str(out_dir / "distributed_self_report.md"),
            "scatter": str(out_dir / "distributed_self_proxy_scatter.png"),
            "conditions": str(out_dir / "distributed_self_conditions.png"),
        },
    }
    write_json(out_dir / "summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
