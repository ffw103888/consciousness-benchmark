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

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mind_lab.utils import ensure_dir, safe_corr, write_json
from mind_lab.validation import (
    computational_mirror_test,
    delayed_identity_recognition_test,
    identity_marker_persistence_probe,
    make_system,
    run_steps,
    temporal_binding_test,
    trajectory_consistency_probe,
    transformed_mirror_test,
)
from scripts.run_measurement_diagnostics import markdown_table
from scripts.run_measurement_validation import distributed_conditions, thalamus_conditions


def build_conditions(architectures: list[str]) -> list[dict[str, Any]]:
    conditions: list[dict[str, Any]] = []
    if "thalamus" in architectures:
        conditions.extend(thalamus_conditions())
    if "distributed" in architectures:
        conditions.extend(distributed_conditions())
    return conditions


def run_one(condition: dict[str, Any], seed: int, warmup: int, quick: bool) -> dict[str, Any]:
    system = make_system(condition["architecture"], condition["config"], seed)
    run_steps(system, warmup)
    rng = np.random.default_rng(seed + 2_100_000)
    profile = system.evaluation_profile()
    details = profile.get("details", {})

    trajectory = trajectory_consistency_probe(system, rng, trials=3 if quick else 6, steps=36 if quick else 72)
    marker = identity_marker_persistence_probe(system, rng, steps=48 if quick else 96)
    old_mirror = computational_mirror_test(system, rng, steps=64 if quick else 160)
    transformed = transformed_mirror_test(system, rng, steps=64 if quick else 120)
    binding = temporal_binding_test(system, rng, steps=56 if quick else 96)
    delayed_identity = delayed_identity_recognition_test(system, rng, steps=48 if quick else 96)

    proxy_existing = float(details.get("temporal_self_proxy", profile.get("temporal_continuity", 0.0)))
    proxy_candidate = float(np.mean([trajectory.score, marker.score]))
    independent_composite = float(np.mean([old_mirror.score, transformed.score, binding.score, delayed_identity.score]))
    independent_refined = float(np.mean([binding.score, delayed_identity.score]))

    return {
        "architecture": condition["architecture"],
        "condition": condition["condition"],
        "seed": seed,
        "proxy_temporal_existing": proxy_existing,
        "proxy_trajectory_consistency": trajectory.score,
        "proxy_identity_marker_persistence": marker.score,
        "proxy_temporal_candidate": proxy_candidate,
        "test_computational_mirror": old_mirror.score,
        "test_transformed_mirror": transformed.score,
        "test_temporal_binding": binding.score,
        "test_delayed_identity_recognition": delayed_identity.score,
        "independent_temporal_composite": independent_composite,
        "independent_temporal_refined": independent_refined,
        "detail_trajectory_behavior_consistency": trajectory.details.get("behavior_trajectory_consistency", 0.0),
        "detail_trajectory_action_consistency": trajectory.details.get("action_trajectory_consistency", 0.0),
        "detail_marker_architecture": marker.details.get("architecture", condition["architecture"]),
        "detail_marker_vector_trace": marker.details.get("vector_trace", np.nan),
        "detail_marker_source_trace": marker.details.get("source_trace", np.nan),
        "detail_marker_position_persistence": marker.details.get("position_persistence", np.nan),
        "detail_marker_memory_persistence": marker.details.get("memory_persistence", np.nan),
        "detail_transformed_accuracy": transformed.details.get("accuracy", 0.0),
        "detail_binding_ordering_accuracy": binding.details.get("ordering_accuracy", 0.0),
        "detail_binding_local_edge_rate": binding.details.get("local_edge_rate", 0.0),
        "detail_delayed_identity_discrimination": delayed_identity.details.get("discrimination", np.nan),
        "detail_delayed_identity_own_memory": delayed_identity.details.get("own_memory", np.nan),
    }


def correlations(df: pd.DataFrame) -> dict[str, float]:
    pairs = {
        "existing_proxy_vs_old_mirror": ("proxy_temporal_existing", "test_computational_mirror"),
        "existing_proxy_vs_refined_independent": ("proxy_temporal_existing", "independent_temporal_refined"),
        "trajectory_proxy_vs_transformed_mirror": ("proxy_trajectory_consistency", "test_transformed_mirror"),
        "marker_proxy_vs_temporal_binding": ("proxy_identity_marker_persistence", "test_temporal_binding"),
        "marker_proxy_vs_delayed_identity": ("proxy_identity_marker_persistence", "test_delayed_identity_recognition"),
        "candidate_proxy_vs_refined_independent": ("proxy_temporal_candidate", "independent_temporal_refined"),
        "candidate_proxy_vs_composite_independent": ("proxy_temporal_candidate", "independent_temporal_composite"),
    }
    out = {name: safe_corr(df[x].to_numpy(float), df[y].to_numpy(float)) for name, (x, y) in pairs.items()}
    for arch, group in df.groupby("architecture"):
        for name, (x, y) in pairs.items():
            out[f"{arch}_{name}"] = safe_corr(group[x].to_numpy(float), group[y].to_numpy(float))
    return out


def save_plots(raw: pd.DataFrame, summary: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    plot_pairs = [
        ("proxy_temporal_existing", "test_computational_mirror", "Existing vs old mirror"),
        ("proxy_trajectory_consistency", "test_transformed_mirror", "Trajectory vs transformed mirror"),
        ("proxy_identity_marker_persistence", "test_delayed_identity_recognition", "Marker vs delayed identity"),
    ]
    colors = {"thalamus": "tab:blue", "distributed": "tab:orange"}
    for ax, (x_col, y_col, title) in zip(axes, plot_pairs):
        for arch, group in raw.groupby("architecture"):
            ax.scatter(group[x_col], group[y_col], s=48, alpha=0.72, label=arch, color=colors.get(arch))
        ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.55)
        r = safe_corr(raw[x_col].to_numpy(float), raw[y_col].to_numpy(float))
        ax.set_title(f"{title}\nr={r:.2f}")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.25)
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(out_dir / "temporal_self_proxy_scatter.png", dpi=180)
    plt.close(fig)

    labels = [f"{r.architecture}\n{r.condition}" for r in summary.itertuples()]
    x = np.arange(len(summary))
    width = 0.2
    fig, ax = plt.subplots(figsize=(12.5, 5.4))
    ax.bar(x - 1.5 * width, summary["proxy_temporal_existing"], width, label="existing proxy")
    ax.bar(x - 0.5 * width, summary["proxy_temporal_candidate"], width, label="candidate proxy")
    ax.bar(x + 0.5 * width, summary["test_temporal_binding"], width, label="temporal binding")
    ax.bar(x + 1.5 * width, summary["test_delayed_identity_recognition"], width, label="delayed identity")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Temporal self validation by condition")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "temporal_self_conditions.png", dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run temporal-self measurement strengthening probes.")
    parser.add_argument("--output-root", type=Path, default=Path("runs") / "measurement_validation")
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--warmup", type=int, default=180)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed-base", type=int, default=20260521)
    parser.add_argument("--architectures", nargs="*", default=["thalamus", "distributed"], choices=["thalamus", "distributed"])
    args = parser.parse_args()

    out_dir = ensure_dir(args.output_root / f"temporal_self_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    rows = []
    conditions = build_conditions(args.architectures)
    for idx, condition in enumerate(conditions):
        for seed_idx in range(args.seeds):
            rows.append(run_one(condition, args.seed_base + idx * 1000 + seed_idx, args.warmup, args.quick))
    raw = pd.DataFrame(rows)
    raw.to_csv(out_dir / "temporal_self_raw.csv", index=False)
    summary = raw.groupby(["architecture", "condition"], as_index=False).mean(numeric_only=True)
    summary.to_csv(out_dir / "temporal_self_summary.csv", index=False)
    corr = correlations(raw)
    save_plots(raw, summary, out_dir)

    report = [
        "# Temporal Self Validation",
        "",
        "## Correlations",
        "",
        "```json",
        json.dumps(corr, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Condition Summary",
        "",
        markdown_table(summary, max_rows=20),
        "",
        "## Guardrail",
        "",
        "Temporal probes are construct-refinement candidates. A subconstruct should only be upgraded if proxy-test convergence is stable across architectures or clearly scoped to one architecture.",
    ]
    (out_dir / "temporal_self_report.md").write_text("\n".join(report), encoding="utf-8")
    payload = {
        "output_dir": str(out_dir),
        "rows": len(raw),
        "correlations": corr,
        "files": {
            "raw": str(out_dir / "temporal_self_raw.csv"),
            "summary": str(out_dir / "temporal_self_summary.csv"),
            "report": str(out_dir / "temporal_self_report.md"),
            "scatter": str(out_dir / "temporal_self_proxy_scatter.png"),
            "conditions": str(out_dir / "temporal_self_conditions.png"),
        },
    }
    write_json(out_dir / "summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
