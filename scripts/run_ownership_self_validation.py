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
    action_attribution_proxy_test,
    body_ownership_proxy_test,
    forced_choice_ownership_test,
    make_system,
    ownership_attribution_test,
    ownership_illusion_resistance_test,
    run_steps,
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


def has_action_mechanism(condition: dict[str, Any]) -> bool:
    config = condition["config"]
    if condition["architecture"] == "thalamus":
        return bool(config.get("enable_action_loop", False)) and str(config.get("action_loop_variant", "minimal")) != "none"
    if condition["architecture"] == "distributed":
        return bool(config.get("enable_action_feedback", True))
    return False


def run_one(condition: dict[str, Any], seed: int, warmup: int, quick: bool) -> dict[str, Any]:
    system = make_system(condition["architecture"], condition["config"], seed)
    run_steps(system, warmup)
    rng = np.random.default_rng(seed + 3_100_000)
    profile = system.evaluation_profile()
    details = profile.get("details", {})

    action_proxy = action_attribution_proxy_test(system, rng, trials=48 if quick else 96)
    body_proxy = body_ownership_proxy_test(system, rng, trials=48 if quick else 96)
    old_ownership = ownership_attribution_test(system, rng, trials=48 if quick else 120)
    forced_choice = forced_choice_ownership_test(system, rng, trials=48 if quick else 96)
    illusion = ownership_illusion_resistance_test(system, rng, trials=48 if quick else 96)

    proxy_existing = float(details.get("ownership_self_proxy", profile.get("agency", 0.0)))
    proxy_candidate = float(action_proxy.score)
    independent_refined = float(np.mean([forced_choice.score, illusion.score]))
    independent_composite = float(np.mean([old_ownership.score, forced_choice.score, illusion.score]))

    return {
        "architecture": condition["architecture"],
        "condition": condition["condition"],
        "seed": seed,
        "has_action_mechanism": has_action_mechanism(condition),
        "proxy_ownership_existing": proxy_existing,
        "proxy_action_attribution": action_proxy.score,
        "proxy_body_ownership": body_proxy.score,
        "proxy_ownership_candidate": proxy_candidate,
        "test_ownership_attribution_old": old_ownership.score,
        "test_forced_choice_ownership": forced_choice.score,
        "test_ownership_illusion_resistance": illusion.score,
        "independent_ownership_composite": independent_composite,
        "independent_ownership_refined": independent_refined,
        "detail_action_prediction_accuracy": action_proxy.details.get("prediction_accuracy", np.nan),
        "detail_action_self_attribution": action_proxy.details.get("self_attribution_accuracy", np.nan),
        "detail_action_external_attribution": action_proxy.details.get("external_attribution_accuracy", np.nan),
        "detail_body_own_fit": body_proxy.details.get("own_fit", np.nan),
        "detail_body_fake_fit": body_proxy.details.get("fake_fit", np.nan),
        "detail_forced_choice_accuracy": forced_choice.details.get("accuracy", np.nan),
        "detail_illusion_external_rejection": illusion.details.get("external_rejection_accuracy", np.nan),
    }


def _corr(df: pd.DataFrame, x: str, y: str) -> float:
    if len(df) < 3:
        return 0.0
    return safe_corr(df[x].to_numpy(float), df[y].to_numpy(float))


def correlations(df: pd.DataFrame) -> dict[str, float]:
    pairs = {
        "existing_proxy_vs_old_test": ("proxy_ownership_existing", "test_ownership_attribution_old"),
        "existing_proxy_vs_refined_independent": ("proxy_ownership_existing", "independent_ownership_refined"),
        "action_proxy_vs_forced_choice": ("proxy_action_attribution", "test_forced_choice_ownership"),
        "body_proxy_vs_illusion_resistance": ("proxy_body_ownership", "test_ownership_illusion_resistance"),
        "candidate_proxy_vs_refined_independent": ("proxy_ownership_candidate", "independent_ownership_refined"),
        "candidate_proxy_vs_composite_independent": ("proxy_ownership_candidate", "independent_ownership_composite"),
    }
    out = {name: _corr(df, x, y) for name, (x, y) in pairs.items()}
    for key, group in [("with_action", df[df["has_action_mechanism"]]), ("without_action", df[~df["has_action_mechanism"]])]:
        for name, (x, y) in pairs.items():
            out[f"{key}_{name}"] = _corr(group, x, y)
    for arch, group in df.groupby("architecture"):
        for name, (x, y) in pairs.items():
            out[f"{arch}_{name}"] = _corr(group, x, y)
    return out


def save_plots(raw: pd.DataFrame, summary: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    plot_pairs = [
        ("proxy_ownership_existing", "test_ownership_attribution_old", "Existing vs old ownership test"),
        ("proxy_action_attribution", "test_forced_choice_ownership", "Action attribution vs forced choice"),
        ("proxy_ownership_candidate", "independent_ownership_refined", "Candidate vs refined independent"),
    ]
    colors = {True: "tab:green", False: "tab:red"}
    for ax, (x_col, y_col, title) in zip(axes, plot_pairs):
        for has_action, group in raw.groupby("has_action_mechanism"):
            ax.scatter(group[x_col], group[y_col], s=48, alpha=0.72, label=f"action={has_action}", color=colors.get(bool(has_action)))
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
    fig.savefig(out_dir / "ownership_self_proxy_scatter.png", dpi=180)
    plt.close(fig)

    labels = [f"{r.architecture}\n{r.condition}" for r in summary.itertuples()]
    x = np.arange(len(summary))
    width = 0.2
    fig, ax = plt.subplots(figsize=(12.5, 5.4))
    ax.bar(x - 1.5 * width, summary["proxy_ownership_existing"], width, label="existing proxy")
    ax.bar(x - 0.5 * width, summary["proxy_ownership_candidate"], width, label="action-attribution proxy")
    ax.bar(x + 0.5 * width, summary["test_forced_choice_ownership"], width, label="forced choice")
    ax.bar(x + 1.5 * width, summary["test_ownership_illusion_resistance"], width, label="illusion resistance")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Ownership self validation by condition")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "ownership_self_conditions.png", dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ownership-self measurement strengthening probes.")
    parser.add_argument("--output-root", type=Path, default=Path("runs") / "measurement_validation")
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--warmup", type=int, default=180)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed-base", type=int, default=20260521)
    parser.add_argument("--architectures", nargs="*", default=["thalamus", "distributed"], choices=["thalamus", "distributed"])
    args = parser.parse_args()

    out_dir = ensure_dir(args.output_root / f"ownership_self_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    rows = []
    conditions = build_conditions(args.architectures)
    for idx, condition in enumerate(conditions):
        for seed_idx in range(args.seeds):
            rows.append(run_one(condition, args.seed_base + idx * 1000 + seed_idx, args.warmup, args.quick))
    raw = pd.DataFrame(rows)
    raw.to_csv(out_dir / "ownership_self_raw.csv", index=False)
    summary = raw.groupby(["architecture", "condition"], as_index=False).mean(numeric_only=True)
    summary.to_csv(out_dir / "ownership_self_summary.csv", index=False)
    corr = correlations(raw)
    save_plots(raw, summary, out_dir)

    report = [
        "# Ownership Self Validation",
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
        "Ownership probes are analyzed separately for systems with and without action mechanisms. Do not interpret low scores without action loops as validation failure; they may define the scope of the construct.",
    ]
    (out_dir / "ownership_self_report.md").write_text("\n".join(report), encoding="utf-8")
    payload = {
        "output_dir": str(out_dir),
        "rows": len(raw),
        "correlations": corr,
        "files": {
            "raw": str(out_dir / "ownership_self_raw.csv"),
            "summary": str(out_dir / "ownership_self_summary.csv"),
            "report": str(out_dir / "ownership_self_report.md"),
            "scatter": str(out_dir / "ownership_self_proxy_scatter.png"),
            "conditions": str(out_dir / "ownership_self_conditions.png"),
        },
    }
    write_json(out_dir / "summary.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
