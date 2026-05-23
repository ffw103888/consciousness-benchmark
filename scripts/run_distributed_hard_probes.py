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
    architecture_self_probe_test,
    distributed_body_schema_update_probe,
    distributed_hidden_agent_perturbation_probe,
    distributed_meta_monitor_lesion_probe,
    make_system,
    run_steps,
)
from scripts.run_measurement_diagnostics import markdown_table


def hard_probe_conditions() -> list[dict[str, Any]]:
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
            "enable_meta_monitor": True,
        },
    }
    variants = [
        ("agents_8_full", {}),
        ("meta_monitor_off", {"enable_meta_monitor": False}),
        ("agents_8_feedback_off", {"enable_action_feedback": False}),
        ("agents_4_full", {"num_agents": 4}),
        ("agents_16_full", {"num_agents": 16}),
        ("no_coordination", {"enable_coordination": False}),
        ("no_coordination_no_meta", {"enable_coordination": False, "enable_meta_monitor": False}),
        ("sparse_sensors", {"sensor_range": 3}),
        ("dense_sensors", {"sensor_range": 10}),
        ("shifted_goal", {"global_goal_xy": [14.0, 42.0]}),
        ("large_world", {"world_size": 72, "global_goal_xy": [49.0, 25.0]}),
    ]
    return [{"architecture": "distributed", "condition": name, "config": {**base["config"], **updates}} for name, updates in variants]


def run_one(condition: dict[str, Any], seed: int, warmup: int, quick: bool) -> dict[str, Any]:
    system = make_system("distributed", condition["config"], seed)
    run_steps(system, warmup)
    rng = np.random.default_rng(seed + 4_100_000)
    profile = system.evaluation_profile()
    details = profile.get("details", {})

    generic_arch = architecture_self_probe_test(system, rng, trials=36 if quick else 96)
    lesion = distributed_meta_monitor_lesion_probe(system, rng, steps=48 if quick else 96)
    hidden = distributed_hidden_agent_perturbation_probe(system, rng, trials=4 if quick else 8, max_steps=80 if quick else 160)
    schema = distributed_body_schema_update_probe(system, rng, trials=5 if quick else 9, max_steps=64 if quick else 120)
    hard_probe = float(np.mean([lesion.score, hidden.score, schema.score]))

    return {
        "condition": condition["condition"],
        "seed": seed,
        "num_agents": int(condition["config"].get("num_agents", 0)),
        "world_size": int(condition["config"].get("world_size", 0)),
        "sensor_range": int(condition["config"].get("sensor_range", 0)),
        "enable_coordination": bool(condition["config"].get("enable_coordination", True)),
        "enable_action_feedback": bool(condition["config"].get("enable_action_feedback", True)),
        "enable_meta_monitor": bool(condition["config"].get("enable_meta_monitor", True)),
        "proxy_self_model": float(profile.get("self_model", 0.0)),
        "proxy_boundary_self": float(details.get("boundary_self_proxy", profile.get("self_model", 0.0))),
        "proxy_temporal_self": float(details.get("temporal_self_proxy", profile.get("temporal_continuity", 0.0))),
        "proxy_ownership_self": float(details.get("ownership_self_proxy", profile.get("agency", 0.0))),
        "proxy_legacy_self_model": float(details.get("legacy_self_model_stability", profile.get("self_model", 0.0))),
        "generic_architecture_probe": generic_arch.score,
        "hard_meta_monitor_lesion": lesion.score,
        "hard_hidden_agent_perturbation": hidden.score,
        "hard_body_schema_update": schema.score,
        "hard_distributed_self": hard_probe,
        "detail_lesion_baseline": lesion.details.get("baseline_body_schema", np.nan),
        "detail_lesion_lesioned": lesion.details.get("lesioned_body_schema", np.nan),
        "detail_lesion_drop": lesion.details.get("lesion_drop", np.nan),
        "detail_lesion_recovery_gap": lesion.details.get("recovery_gap", np.nan),
        "detail_hidden_discovery_rate": hidden.details.get("discovery_rate", np.nan),
        "detail_hidden_response_effectiveness": hidden.details.get("response_effectiveness", np.nan),
        "detail_hidden_mean_discovery_time": hidden.details.get("mean_discovery_time", np.nan),
        "detail_schema_final_accuracy": schema.details.get("final_accuracy", np.nan),
        "detail_schema_mean_update_time": schema.details.get("mean_update_time", np.nan),
        "detail_schema_update_speed": schema.details.get("update_speed", np.nan),
    }


def correlations(df: pd.DataFrame) -> dict[str, float]:
    pairs = {
        "proxy_self_vs_hard_self": ("proxy_self_model", "hard_distributed_self"),
        "boundary_proxy_vs_hard_self": ("proxy_boundary_self", "hard_distributed_self"),
        "legacy_proxy_vs_hard_self": ("proxy_legacy_self_model", "hard_distributed_self"),
        "generic_probe_vs_hard_self": ("generic_architecture_probe", "hard_distributed_self"),
        "boundary_proxy_vs_meta_lesion": ("proxy_boundary_self", "hard_meta_monitor_lesion"),
        "boundary_proxy_vs_hidden_agent": ("proxy_boundary_self", "hard_hidden_agent_perturbation"),
        "boundary_proxy_vs_schema_update": ("proxy_boundary_self", "hard_body_schema_update"),
    }
    return {name: safe_corr(df[x].to_numpy(float), df[y].to_numpy(float)) for name, (x, y) in pairs.items()}


def save_plots(raw: pd.DataFrame, summary: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    pairs = [
        ("proxy_self_model", "hard_distributed_self", "Proxy self vs hard probes"),
        ("generic_architecture_probe", "hard_distributed_self", "Generic arch probe vs hard probes"),
        ("proxy_boundary_self", "hard_meta_monitor_lesion", "Boundary proxy vs meta lesion"),
    ]
    for ax, (x_col, y_col, title) in zip(axes, pairs):
        ax.scatter(raw[x_col], raw[y_col], s=48, alpha=0.72)
        ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.55)
        r = safe_corr(raw[x_col].to_numpy(float), raw[y_col].to_numpy(float))
        ax.set_title(f"{title}\nr={r:.2f}")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "distributed_hard_probe_scatter.png", dpi=180)
    plt.close(fig)

    labels = list(summary["condition"])
    x = np.arange(len(summary))
    width = 0.16
    fig, ax = plt.subplots(figsize=(13.5, 5.8))
    ax.bar(x - 2 * width, summary["proxy_self_model"], width, label="proxy self")
    ax.bar(x - width, summary["generic_architecture_probe"], width, label="generic arch probe")
    ax.bar(x, summary["hard_meta_monitor_lesion"], width, label="meta lesion")
    ax.bar(x + width, summary["hard_hidden_agent_perturbation"], width, label="hidden agent")
    ax.bar(x + 2 * width, summary["hard_body_schema_update"], width, label="schema update")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Distributed self harder probes by condition")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncol=2)
    fig.tight_layout()
    fig.savefig(out_dir / "distributed_hard_probe_conditions.png", dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run distributed architecture-specific hard self probes.")
    parser.add_argument("--output-root", type=Path, default=Path("runs") / "measurement_validation")
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--warmup", type=int, default=220)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed-base", type=int, default=20260521)
    args = parser.parse_args()

    out_dir = ensure_dir(args.output_root / f"distributed_hard_probes_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    rows = []
    conditions = hard_probe_conditions()
    for idx, condition in enumerate(conditions):
        for seed_idx in range(args.seeds):
            rows.append(run_one(condition, args.seed_base + idx * 1000 + seed_idx, args.warmup, args.quick))
    raw = pd.DataFrame(rows)
    raw.to_csv(out_dir / "distributed_hard_probe_raw.csv", index=False)
    summary = raw.groupby("condition", as_index=False).mean(numeric_only=True)
    summary.to_csv(out_dir / "distributed_hard_probe_summary.csv", index=False)
    corr = correlations(raw)
    save_plots(raw, summary, out_dir)

    report = [
        "# Distributed Self Hard Probes",
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
        "Hard probes test operational body-schema and meta-monitor sensitivity. They are designed to diagnose measurement sensitivity, not to certify subjective selfhood.",
    ]
    (out_dir / "distributed_hard_probe_report.md").write_text("\n".join(report), encoding="utf-8")
    payload = {
        "output_dir": str(out_dir),
        "rows": len(raw),
        "correlations": corr,
        "files": {
            "raw": str(out_dir / "distributed_hard_probe_raw.csv"),
            "summary": str(out_dir / "distributed_hard_probe_summary.csv"),
            "report": str(out_dir / "distributed_hard_probe_report.md"),
            "scatter": str(out_dir / "distributed_hard_probe_scatter.png"),
            "conditions": str(out_dir / "distributed_hard_probe_conditions.png"),
        },
    }
    write_json(out_dir / "summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
