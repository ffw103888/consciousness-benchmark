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
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from consciousness_benchmark.core.stats import bootstrap_corr_ci, format_p, pearson
from mind_lab.transformer import (
    TransformerInspiredArchitecture,
    transformer_agency_probe,
    transformer_boundary_probe,
    transformer_identity_probe,
    transformer_ownership_probe,
)
from mind_lab.utils import ensure_dir, write_json


CONSTRUCTS = {
    "action_agency": {
        "label": "Action agency",
        "proxy": "proxy_agency",
        "independent": "independent_agency",
        "mechanism": "action_loop",
    },
    "boundary_self": {
        "label": "Boundary self",
        "proxy": "proxy_boundary_self",
        "independent": "independent_boundary_self",
        "mechanism": "workspace",
    },
    "identity_temporal_self": {
        "label": "Identity-temporal self",
        "proxy": "proxy_identity_marker_persistence",
        "independent": "independent_identity_temporal_self",
        "mechanism": "workspace",
    },
    "action_ownership": {
        "label": "Action ownership",
        "proxy": "proxy_action_attribution",
        "independent": "independent_action_ownership",
        "mechanism": "action_loop",
    },
}


def transformer_conditions() -> list[dict[str, Any]]:
    return [
        {"condition": "W-A-", "workspace": False, "action_loop": False},
        {"condition": "W+A-", "workspace": True, "action_loop": False},
        {"condition": "W-A+", "workspace": False, "action_loop": True},
        {"condition": "W+A+", "workspace": True, "action_loop": True},
    ]


def run_one(condition: dict[str, Any], seed: int, warmup: int, probe_steps: int, config: dict[str, Any]) -> dict[str, Any]:
    system_config = {
        **config,
        "workspace": condition["workspace"],
        "action_loop": condition["action_loop"],
    }
    system = TransformerInspiredArchitecture(system_config, seed=seed)
    system.run_steps(warmup)
    rng = np.random.default_rng(seed + 7_300_000)

    profile = system.evaluation_profile()
    details = profile["details"]
    boundary = transformer_boundary_probe(system, rng, steps=probe_steps)
    identity = transformer_identity_probe(system, rng, steps=probe_steps)
    agency = transformer_agency_probe(system, rng, steps=probe_steps)
    ownership = transformer_ownership_probe(system, rng, steps=probe_steps)

    return {
        "architecture": "transformer",
        "condition": condition["condition"],
        "workspace": bool(condition["workspace"]),
        "action_loop": bool(condition["action_loop"]),
        "seed": seed,
        "proxy_boundary_self": details["proxy_boundary_self"],
        "independent_boundary_self": boundary.score,
        "boundary_recovery_similarity": boundary.details["recovery_similarity"],
        "boundary_marker_recovery": boundary.details["marker_recovery"],
        "proxy_identity_marker_persistence": details["proxy_identity_marker_persistence"],
        "independent_identity_temporal_self": identity.score,
        "identity_own_marker": identity.details["own_marker"],
        "identity_decoy_marker": identity.details["decoy_marker"],
        "identity_stability": identity.details["stability"],
        "proxy_agency": details["proxy_agency"],
        "independent_agency": agency.score,
        "agency_true_causality": agency.details["true_causality"],
        "agency_decoy_causality": agency.details["decoy_causality"],
        "proxy_action_attribution": details["proxy_action_attribution"],
        "independent_action_ownership": ownership.score,
        "ownership_accuracy": ownership.details["accuracy"],
        "ownership_margin": ownership.details["margin"],
        "workspace_occupancy": details["workspace_occupancy"],
        "workspace_coherence": details["workspace_coherence"],
        "prediction_error": details["prediction_error"],
        "action_presence": details["action_presence"],
    }


def bootstrap_mean_ci(values: Iterable[float], rng: np.random.Generator, n_bootstrap: int) -> tuple[float, float]:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) == 0:
        return float("nan"), float("nan")
    means = []
    for _ in range(n_bootstrap):
        sample = arr[rng.integers(0, len(arr), len(arr))]
        means.append(float(np.mean(sample)))
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def cohen_d(a: Iterable[float], b: Iterable[float]) -> float:
    aa = np.asarray(list(a), dtype=float)
    bb = np.asarray(list(b), dtype=float)
    aa = aa[np.isfinite(aa)]
    bb = bb[np.isfinite(bb)]
    if len(aa) < 2 or len(bb) < 2:
        return float("nan")
    pooled = np.sqrt(((len(aa) - 1) * np.var(aa, ddof=1) + (len(bb) - 1) * np.var(bb, ddof=1)) / (len(aa) + len(bb) - 2))
    if pooled < 1e-12:
        return float("nan")
    return float((np.mean(a) - np.mean(b)) / pooled)


def validation_stats(raw: pd.DataFrame, seed: int, n_bootstrap: int) -> pd.DataFrame:
    rows = []
    for key, spec in CONSTRUCTS.items():
        r, p, n = pearson(raw[spec["proxy"]], raw[spec["independent"]])
        ci_low, ci_high = bootstrap_corr_ci(raw[spec["proxy"]], raw[spec["independent"]], seed=seed, n_bootstrap=n_bootstrap)
        rows.append(
            {
                "construct_key": key,
                "construct": spec["label"],
                "proxy_col": spec["proxy"],
                "independent_col": spec["independent"],
                "n": n,
                "r": r,
                "r_ci_low": ci_low,
                "r_ci_high": ci_high,
                "p": p,
                "p_formatted": format_p(p),
                "validated": bool(np.isfinite(r) and r >= 0.7),
                "expected_mechanism": spec["mechanism"],
            }
        )
    return pd.DataFrame(rows)


def effect_rows(raw: pd.DataFrame, rng: np.random.Generator, n_bootstrap: int) -> pd.DataFrame:
    rows = []
    for key, spec in CONSTRUCTS.items():
        for factor in ["workspace", "action_loop"]:
            on = raw[raw[factor]][spec["proxy"]].to_numpy(float)
            off = raw[~raw[factor]][spec["proxy"]].to_numpy(float)
            if len(on) < 2 or len(off) < 2:
                continue
            diff = float(np.mean(on) - np.mean(off))
            boot = []
            for _ in range(n_bootstrap):
                on_sample = on[rng.integers(0, len(on), len(on))]
                off_sample = off[rng.integers(0, len(off), len(off))]
                boot.append(float(np.mean(on_sample) - np.mean(off_sample)))
            p = float(stats.ttest_ind(on, off, equal_var=False).pvalue)
            rows.append(
                {
                    "effect_key": f"{factor}_effect_{key}",
                    "factor": factor,
                    "target_construct": spec["label"],
                    "target_proxy": spec["proxy"],
                    "mean_diff": diff,
                    "mean_diff_ci_low": float(np.percentile(boot, 2.5)),
                    "mean_diff_ci_high": float(np.percentile(boot, 97.5)),
                    "cohens_d": cohen_d(on, off),
                    "p": p,
                    "p_formatted": format_p(p),
                    "predicted_target": factor == spec["mechanism"],
                }
            )
    return pd.DataFrame(rows)


def condition_summary(raw: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [c for c in raw.columns if c not in {"architecture", "condition"} and pd.api.types.is_numeric_dtype(raw[c])]
    summary = raw.groupby(["architecture", "condition"], as_index=False)[numeric_cols].agg(["mean", "std"])
    summary.columns = ["_".join([part for part in col if part]).rstrip("_") if isinstance(col, tuple) else col for col in summary.columns]
    return summary


def save_plots(raw: pd.DataFrame, stats_df: pd.DataFrame, effects: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 9.0))
    axes_flat = axes.ravel()
    for ax, (key, spec) in zip(axes_flat, CONSTRUCTS.items()):
        for cond, group in raw.groupby("condition"):
            ax.scatter(group[spec["proxy"]], group[spec["independent"]], label=cond, alpha=0.78, s=46)
        ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.55)
        row = stats_df[stats_df["construct_key"] == key].iloc[0]
        ax.set_title(f"{spec['label']}\nr={row.r:.2f}, p={row.p_formatted}")
        ax.set_xlabel("proxy")
        ax.set_ylabel("independent probe")
        ax.set_xlim(-0.03, 1.03)
        ax.set_ylim(-0.03, 1.03)
        ax.grid(True, alpha=0.25)
    axes_flat[0].legend(fontsize=8, loc="lower right")
    fig.suptitle("Transformer construct validation", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "transformer_construct_validation.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11.0, 5.2))
    plot = effects.copy()
    plot["label"] = plot["factor"] + " -> " + plot["target_construct"]
    colors = ["tab:green" if target else "tab:gray" for target in plot["predicted_target"]]
    ax.bar(np.arange(len(plot)), plot["mean_diff"], color=colors, alpha=0.78, edgecolor="black")
    ax.axhline(0, color="black", linewidth=1)
    ax.set_xticks(np.arange(len(plot)))
    ax.set_xticklabels(plot["label"], rotation=35, ha="right")
    ax.set_ylabel("Mean proxy difference")
    ax.set_title("Transformer mechanism effects")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "transformer_mechanism_effects.png", dpi=180)
    plt.close(fig)


def write_report(out_dir: Path, raw: pd.DataFrame, stats_df: pd.DataFrame, effects: pd.DataFrame, summary: pd.DataFrame, args: argparse.Namespace) -> None:
    validated = int(stats_df["validated"].sum())
    report = [
        "# Transformer Construct Validation",
        "",
        "## Run",
        "",
        f"- Seeds: {args.seeds}",
        f"- Warmup steps: {args.warmup}",
        f"- Probe steps: {args.probe_steps}",
        f"- Rows: {len(raw)}",
        "",
        "## Proxy-Independent Convergence",
        "",
        stats_df.to_markdown(index=False, floatfmt=".3f"),
        "",
        f"Validated constructs at r >= 0.7: **{validated}/{len(stats_df)}**.",
        "",
        "## Mechanism Effects",
        "",
        effects.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Condition Summary",
        "",
        summary.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Interpretation Guardrail",
        "",
        "This is a controlled Transformer-inspired reproduction, not a claim about production LLM phenomenology. Strong effects here mean the workspace/action-loop mechanisms survive a Transformer-like attention substrate under operational tests.",
    ]
    (out_dir / "report.md").write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Transformer-inspired construct validation.")
    parser.add_argument("--output-root", type=Path, default=Path("runs") / "transformer_validation")
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--seed-base", type=int, default=20260522)
    parser.add_argument("--warmup", type=int, default=512)
    parser.add_argument("--probe-steps", type=int, default=128)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--d-model", type=int, default=32)
    parser.add_argument("--n-tokens", type=int, default=12)
    parser.add_argument("--workspace-capacity", type=int, default=4)
    args = parser.parse_args()

    out_dir = ensure_dir(args.output_root / f"transformer_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    base_config = {
        "d_model": args.d_model,
        "n_tokens": args.n_tokens,
        "workspace_capacity": args.workspace_capacity,
    }
    rows = []
    conditions = transformer_conditions()
    total = len(conditions) * args.seeds
    completed = 0
    for condition_idx, condition in enumerate(conditions):
        for seed_idx in range(args.seeds):
            seed = args.seed_base + condition_idx * 1000 + seed_idx
            rows.append(run_one(condition, seed, args.warmup, args.probe_steps, base_config))
            completed += 1
            pd.DataFrame(rows).to_csv(out_dir / "transformer_validation_raw.partial.csv", index=False)
            (out_dir / "progress.json").write_text(
                json.dumps({"completed": completed, "total": total, "updated_at": datetime.now().astimezone().isoformat(timespec="seconds")}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    raw = pd.DataFrame(rows)
    rng = np.random.default_rng(args.seed_base)
    stats_df = validation_stats(raw, args.seed_base, args.bootstrap)
    effects = effect_rows(raw, rng, args.bootstrap)
    summary = condition_summary(raw)

    raw.to_csv(out_dir / "transformer_validation_raw.csv", index=False)
    stats_df.to_csv(out_dir / "construct_validation_stats.csv", index=False)
    effects.to_csv(out_dir / "mechanism_effects.csv", index=False)
    summary.to_csv(out_dir / "condition_summary.csv", index=False)
    save_plots(raw, stats_df, effects, out_dir)

    manifest = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "architecture": "transformer",
        "conditions": conditions,
        "args": vars(args),
        "files": {
            "raw": str(out_dir / "transformer_validation_raw.csv"),
            "stats": str(out_dir / "construct_validation_stats.csv"),
            "effects": str(out_dir / "mechanism_effects.csv"),
            "summary": str(out_dir / "condition_summary.csv"),
            "report": str(out_dir / "report.md"),
            "validation_plot": str(out_dir / "transformer_construct_validation.png"),
            "effects_plot": str(out_dir / "transformer_mechanism_effects.png"),
        },
    }
    write_json(out_dir / "manifest.json", manifest)
    write_report(out_dir, raw, stats_df, effects, summary, args)

    payload = {
        "output_dir": str(out_dir),
        "validated": int(stats_df["validated"].sum()),
        "constructs": len(stats_df),
        "stats": stats_df[["construct_key", "r", "r_ci_low", "r_ci_high", "p_formatted", "validated"]].to_dict(orient="records"),
        "effects": effects[["effect_key", "mean_diff", "cohens_d", "p_formatted", "predicted_target"]].to_dict(orient="records"),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
