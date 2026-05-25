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
    architecture_self_probe_test,
    distributed_body_schema_update_probe,
    distributed_hidden_agent_perturbation_probe,
    distributed_meta_monitor_lesion_probe,
    make_system,
    run_steps,
)
from scripts.run_measurement_diagnostics import markdown_table


def meta_monitor_conditions() -> list[dict[str, Any]]:
    base = {
        "num_agents": 8,
        "world_size": 52,
        "sensor_range": 6,
        "memory_capacity": 512,
        "measurement_window": 128,
        "enable_coordination": True,
        "enable_action_feedback": True,
        "enable_meta_monitor": True,
        "meta_monitor_strength": 1.0,
        "meta_monitor_noise": 0.0,
        "meta_monitor_delay": 0,
    }
    conditions: list[dict[str, Any]] = []
    for strength in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        config = {**base, "meta_monitor_strength": strength}
        conditions.append(
            {
                "condition": f"strength_{strength:.1f}",
                "control_type": "strength",
                "dose": strength,
                "config": config,
            }
        )
    for noise in [0.08, 0.18, 0.32]:
        config = {**base, "meta_monitor_noise": noise}
        conditions.append(
            {
                "condition": f"noise_{noise:.2f}",
                "control_type": "noise",
                "dose": noise,
                "config": config,
            }
        )
    for delay in [4, 16, 32]:
        config = {**base, "meta_monitor_delay": delay}
        conditions.append(
            {
                "condition": f"delay_{delay}",
                "control_type": "delay",
                "dose": float(delay),
                "config": config,
            }
        )
    conditions.append(
        {
            "condition": "meta_monitor_off",
            "control_type": "off",
            "dose": 0.0,
            "config": {**base, "enable_meta_monitor": False, "meta_monitor_strength": 0.0},
        }
    )
    return conditions


def run_one(condition: dict[str, Any], seed: int, warmup: int, quick: bool) -> dict[str, Any]:
    system = make_system("distributed", condition["config"], seed)
    run_steps(system, warmup)
    rng = np.random.default_rng(seed + 5_100_000)
    profile = system.evaluation_profile()
    details = profile.get("details", {})
    generic = architecture_self_probe_test(system, rng, trials=36 if quick else 96)
    hidden = distributed_hidden_agent_perturbation_probe(system, rng, trials=4 if quick else 8, max_steps=80 if quick else 160)
    schema = distributed_body_schema_update_probe(system, rng, trials=5 if quick else 9, max_steps=64 if quick else 120)
    lesion = distributed_meta_monitor_lesion_probe(system, rng, steps=48 if quick else 96)
    hard_without_lesion = float(np.mean([generic.score, hidden.score, schema.score]))
    hard_with_lesion = float(np.mean([generic.score, hidden.score, schema.score, lesion.score]))
    config = condition["config"]
    return {
        "condition": condition["condition"],
        "control_type": condition["control_type"],
        "dose": float(condition["dose"]),
        "seed": seed,
        "enable_meta_monitor": bool(config.get("enable_meta_monitor", True)),
        "meta_monitor_strength": float(config.get("meta_monitor_strength", 1.0)),
        "meta_monitor_noise": float(config.get("meta_monitor_noise", 0.0)),
        "meta_monitor_delay": int(config.get("meta_monitor_delay", 0)),
        "proxy_self_model": float(profile.get("self_model", 0.0)),
        "proxy_boundary_self": float(details.get("boundary_self_proxy", profile.get("self_model", 0.0))),
        "proxy_legacy_self_model": float(details.get("legacy_self_model_stability", profile.get("self_model", 0.0))),
        "generic_architecture_probe": generic.score,
        "hard_hidden_agent_perturbation": hidden.score,
        "hard_body_schema_update": schema.score,
        "hard_meta_monitor_lesion": lesion.score,
        "hard_self_without_lesion": hard_without_lesion,
        "hard_self_with_lesion": hard_with_lesion,
        "detail_hidden_discovery_rate": hidden.details.get("discovery_rate", np.nan),
        "detail_hidden_response_effectiveness": hidden.details.get("response_effectiveness", np.nan),
        "detail_schema_final_accuracy": schema.details.get("final_accuracy", np.nan),
        "detail_schema_update_speed": schema.details.get("update_speed", np.nan),
        "detail_lesion_drop": lesion.details.get("lesion_drop", np.nan),
    }


def correlations(raw: pd.DataFrame) -> dict[str, float]:
    out = {
        "proxy_self_vs_hard_without_lesion": safe_corr(raw["proxy_self_model"].to_numpy(float), raw["hard_self_without_lesion"].to_numpy(float)),
        "boundary_proxy_vs_hard_without_lesion": safe_corr(raw["proxy_boundary_self"].to_numpy(float), raw["hard_self_without_lesion"].to_numpy(float)),
        "generic_probe_vs_hard_without_lesion": safe_corr(raw["generic_architecture_probe"].to_numpy(float), raw["hard_self_without_lesion"].to_numpy(float)),
    }
    strength = raw[raw["control_type"] == "strength"]
    if len(strength) >= 3:
        out.update(
            {
                "strength_vs_proxy_self": safe_corr(strength["meta_monitor_strength"].to_numpy(float), strength["proxy_self_model"].to_numpy(float)),
                "strength_vs_hard_without_lesion": safe_corr(strength["meta_monitor_strength"].to_numpy(float), strength["hard_self_without_lesion"].to_numpy(float)),
                "strength_vs_hidden_agent": safe_corr(strength["meta_monitor_strength"].to_numpy(float), strength["hard_hidden_agent_perturbation"].to_numpy(float)),
                "strength_vs_schema_update": safe_corr(strength["meta_monitor_strength"].to_numpy(float), strength["hard_body_schema_update"].to_numpy(float)),
            }
        )
    noise = raw[raw["control_type"] == "noise"]
    if len(noise) >= 3:
        out["noise_vs_hard_without_lesion"] = safe_corr(noise["meta_monitor_noise"].to_numpy(float), noise["hard_self_without_lesion"].to_numpy(float))
    delay = raw[raw["control_type"] == "delay"]
    if len(delay) >= 3:
        out["delay_vs_hard_without_lesion"] = safe_corr(delay["meta_monitor_delay"].to_numpy(float), delay["hard_self_without_lesion"].to_numpy(float))
    return out


def save_plots(raw: pd.DataFrame, summary: pd.DataFrame, out_dir: Path) -> None:
    strength = summary[summary["control_type"] == "strength"].sort_values("meta_monitor_strength")
    if not strength.empty:
        fig, ax = plt.subplots(figsize=(7.2, 5.0))
        ax.plot(strength["meta_monitor_strength"], strength["proxy_self_model"], "o-", label="proxy self")
        ax.plot(strength["meta_monitor_strength"], strength["hard_self_without_lesion"], "o-", label="hard probes")
        ax.plot(strength["meta_monitor_strength"], strength["generic_architecture_probe"], "o-", label="generic arch probe")
        ax.set_xlabel("Meta-monitor strength")
        ax.set_ylabel("Score")
        ax.set_ylim(0, 1)
        ax.set_title("Graded meta-monitor dose response")
        ax.grid(True, alpha=0.25)
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_dir / "meta_monitor_strength_dose_response.png", dpi=180)
        plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    pairs = [
        ("proxy_self_model", "hard_self_without_lesion", "Proxy vs hard probes"),
        ("generic_architecture_probe", "hard_self_without_lesion", "Generic vs hard probes"),
        ("meta_monitor_strength", "hard_hidden_agent_perturbation", "Strength vs hidden-agent probe"),
    ]
    for ax, (x_col, y_col, title) in zip(axes, pairs):
        ax.scatter(raw[x_col], raw[y_col], s=42, alpha=0.72)
        if x_col != "meta_monitor_strength":
            ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.55)
            ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        r = safe_corr(raw[x_col].to_numpy(float), raw[y_col].to_numpy(float))
        ax.set_title(f"{title}\nr={r:.2f}")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "meta_monitor_control_scatter.png", dpi=180)
    plt.close(fig)

    labels = list(summary["condition"])
    x = np.arange(len(summary))
    width = 0.18
    fig, ax = plt.subplots(figsize=(13.5, 5.8))
    ax.bar(x - 1.5 * width, summary["proxy_self_model"], width, label="proxy self")
    ax.bar(x - 0.5 * width, summary["hard_self_without_lesion"], width, label="hard probes")
    ax.bar(x + 0.5 * width, summary["hard_hidden_agent_perturbation"], width, label="hidden agent")
    ax.bar(x + 1.5 * width, summary["hard_body_schema_update"], width, label="schema update")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Meta-monitor control conditions")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncol=2)
    fig.tight_layout()
    fig.savefig(out_dir / "meta_monitor_control_conditions.png", dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run graded meta-monitor controls for distributed self validation.")
    parser.add_argument("--output-root", type=Path, default=Path("runs") / "measurement_validation")
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--warmup", type=int, default=220)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed-base", type=int, default=20260521)
    args = parser.parse_args()

    out_dir = ensure_dir(args.output_root / f"distributed_meta_monitor_controls_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    rows = []
    conditions = meta_monitor_conditions()
    for idx, condition in enumerate(conditions):
        for seed_idx in range(args.seeds):
            rows.append(run_one(condition, args.seed_base + idx * 1000 + seed_idx, args.warmup, args.quick))
    raw = pd.DataFrame(rows)
    raw.to_csv(out_dir / "distributed_meta_monitor_controls_raw.csv", index=False)
    summary = raw.groupby(["condition", "control_type"], as_index=False).mean(numeric_only=True)
    summary.to_csv(out_dir / "distributed_meta_monitor_controls_summary.csv", index=False)
    corr = correlations(raw)
    save_plots(raw, summary, out_dir)

    report = [
        "# Distributed Meta-Monitor Controls",
        "",
        "## Correlations",
        "",
        "```json",
        json.dumps(corr, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Condition Summary",
        "",
        markdown_table(summary, max_rows=40),
        "",
        "## Interpretation Guardrail",
        "",
        "A smooth dose response supports the hard-probe result. A step-like response would suggest the probes mostly detect the meta-monitor switch. Noise and delay conditions test whether the construct depends on accurate and timely meta-monitoring rather than mere module presence.",
    ]
    (out_dir / "distributed_meta_monitor_controls_report.md").write_text("\n".join(report), encoding="utf-8")
    payload = {
        "output_dir": str(out_dir),
        "rows": len(raw),
        "correlations": corr,
        "files": {
            "raw": str(out_dir / "distributed_meta_monitor_controls_raw.csv"),
            "summary": str(out_dir / "distributed_meta_monitor_controls_summary.csv"),
            "report": str(out_dir / "distributed_meta_monitor_controls_report.md"),
            "dose_response": str(out_dir / "meta_monitor_strength_dose_response.png"),
            "scatter": str(out_dir / "meta_monitor_control_scatter.png"),
            "conditions": str(out_dir / "meta_monitor_control_conditions.png"),
        },
    }
    write_json(out_dir / "summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
