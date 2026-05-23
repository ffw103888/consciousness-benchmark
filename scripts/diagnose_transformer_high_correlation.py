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

from consciousness_benchmark.core.stats import bootstrap_corr_ci, format_p, pearson
from mind_lab.transformer import TransformerInspiredArchitecture, transformer_agency_probe, transformer_ownership_probe
from mind_lab.utils import ensure_dir, safe_corr, write_json


def difficulty_conditions() -> list[dict[str, Any]]:
    conditions: list[dict[str, Any]] = []
    for noise in [0.02, 0.06, 0.12, 0.24, 0.42, 0.72]:
        conditions.append(
            {
                "condition": f"noise_{noise:.2f}",
                "effect_noise_scale": noise,
                "action_learning_rate": 0.040,
                "workspace": True,
                "action_loop": True,
            }
        )
    for learning in [0.000, 0.008, 0.020, 0.040, 0.080]:
        conditions.append(
            {
                "condition": f"learning_{learning:.3f}",
                "effect_noise_scale": 0.12,
                "action_learning_rate": learning,
                "workspace": True,
                "action_loop": True,
            }
        )
    conditions.extend(
        [
            {
                "condition": "action_loop_off",
                "effect_noise_scale": 0.12,
                "action_learning_rate": 0.040,
                "workspace": True,
                "action_loop": False,
            },
            {
                "condition": "workspace_off_action_on",
                "effect_noise_scale": 0.12,
                "action_learning_rate": 0.040,
                "workspace": False,
                "action_loop": True,
            },
        ]
    )
    return conditions


def run_one(condition: dict[str, Any], seed: int, warmup: int, probe_steps: int, d_model: int, n_tokens: int) -> dict[str, Any]:
    config = {
        "d_model": d_model,
        "n_tokens": n_tokens,
        "workspace_capacity": 4,
        **condition,
    }
    system = TransformerInspiredArchitecture(config, seed=seed)
    system.run_steps(warmup)
    profile = system.evaluation_profile()
    details = profile["details"]
    rng = np.random.default_rng(seed + 8_100_000)
    agency = transformer_agency_probe(system, rng, steps=probe_steps)
    ownership = transformer_ownership_probe(system, rng, steps=probe_steps)
    prediction_accuracy = 1.0 - float(details["prediction_error"])

    return {
        "condition": condition["condition"],
        "seed": seed,
        "workspace": bool(condition["workspace"]),
        "action_loop": bool(condition["action_loop"]),
        "effect_noise_scale": float(condition["effect_noise_scale"]),
        "action_learning_rate": float(condition["action_learning_rate"]),
        "proxy_agency": float(details["proxy_agency"]),
        "proxy_action_attribution": float(details["proxy_action_attribution"]),
        "independent_agency": agency.score,
        "independent_action_ownership": ownership.score,
        "prediction_error": float(details["prediction_error"]),
        "prediction_accuracy": prediction_accuracy,
        "action_presence": float(details["action_presence"]),
        "agency_true_causality": agency.details["true_causality"],
        "agency_decoy_causality": agency.details["decoy_causality"],
        "ownership_accuracy": ownership.details["accuracy"],
        "ownership_margin": ownership.details["margin"],
    }


def compute_stats(raw: pd.DataFrame, bootstrap: int, seed: int) -> pd.DataFrame:
    pairs = [
        ("proxy_agency_vs_independent", "proxy_agency", "independent_agency"),
        ("proxy_ownership_vs_independent", "proxy_action_attribution", "independent_action_ownership"),
        ("prediction_accuracy_vs_independent_agency", "prediction_accuracy", "independent_agency"),
        ("prediction_accuracy_vs_true_causality", "prediction_accuracy", "agency_true_causality"),
        ("proxy_agency_vs_true_causality", "proxy_agency", "agency_true_causality"),
        ("action_presence_vs_independent_agency", "action_presence", "independent_agency"),
    ]
    rows = []
    subsets = {
        "all": raw,
        "action_loop_on": raw[raw["action_loop"]],
        "noise_sweep": raw[raw["condition"].str.startswith("noise_")],
        "learning_sweep": raw[raw["condition"].str.startswith("learning_")],
    }
    for subset_name, subset in subsets.items():
        for key, x_col, y_col in pairs:
            r, p, n = pearson(subset[x_col], subset[y_col])
            ci_low, ci_high = bootstrap_corr_ci(subset[x_col], subset[y_col], seed=seed, n_bootstrap=bootstrap)
            rows.append(
                {
                    "subset": subset_name,
                    "diagnostic": key,
                    "x": x_col,
                    "y": y_col,
                    "n": n,
                    "r": r,
                    "r_ci_low": ci_low,
                    "r_ci_high": ci_high,
                    "p": p,
                    "p_formatted": format_p(p),
                }
            )
    return pd.DataFrame(rows)


def save_plots(raw: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    pairs = [
        ("proxy_agency", "independent_agency", "Proxy vs agency test"),
        ("prediction_accuracy", "independent_agency", "Prediction accuracy vs agency test"),
        ("effect_noise_scale", "independent_agency", "Noise difficulty curve"),
    ]
    for ax, (x_col, y_col, title) in zip(axes, pairs):
        for action_loop, group in raw.groupby("action_loop"):
            label = "action loop on" if action_loop else "action loop off"
            ax.scatter(group[x_col], group[y_col], s=42, alpha=0.75, label=label)
        r = safe_corr(raw[x_col].to_numpy(float), raw[y_col].to_numpy(float))
        ax.set_title(f"{title}\nr={r:.2f}")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_ylim(-0.03, 1.03)
        ax.grid(True, alpha=0.25)
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "transformer_high_correlation_diagnostics.png", dpi=180)
    plt.close(fig)

    noise = raw[raw["condition"].str.startswith("noise_")]
    if not noise.empty:
        summary = noise.groupby("effect_noise_scale", as_index=False).mean(numeric_only=True)
        fig, ax = plt.subplots(figsize=(7.2, 5.0))
        ax.plot(summary["effect_noise_scale"], summary["proxy_agency"], "o-", label="proxy agency")
        ax.plot(summary["effect_noise_scale"], summary["independent_agency"], "o-", label="independent agency")
        ax.plot(summary["effect_noise_scale"], summary["agency_true_causality"], "o-", label="true causality")
        ax.set_xlabel("Effect noise scale")
        ax.set_ylabel("Score")
        ax.set_ylim(0, 1.05)
        ax.set_title("Action-loop task difficulty sweep")
        ax.grid(True, alpha=0.25)
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_dir / "transformer_action_difficulty_sweep.png", dpi=180)
        plt.close(fig)


def write_report(out_dir: Path, raw: pd.DataFrame, stats_df: pd.DataFrame) -> None:
    variance = raw.groupby("condition", as_index=False).agg(
        proxy_agency_std=("proxy_agency", "std"),
        independent_agency_std=("independent_agency", "std"),
        proxy_agency_mean=("proxy_agency", "mean"),
        independent_agency_mean=("independent_agency", "mean"),
    )
    overlap_r = float(stats_df[stats_df["diagnostic"] == "prediction_accuracy_vs_independent_agency"]["r"].iloc[0])
    interpretation = (
        "High proxy-test convergence is substantially explained by shared action-outcome prediction accuracy. "
        "Treat Transformer agency/ownership validation as a mechanistic sanity check unless probes are redesigned to reduce signal overlap."
        if abs(overlap_r) >= 0.9
        else "High convergence is not fully explained by the prediction-accuracy diagnostic alone."
    )
    report = [
        "# Transformer High-Correlation Diagnostic",
        "",
        "## Correlation Diagnostics",
        "",
        stats_df.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Per-Condition Variance",
        "",
        variance.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Interpretation",
        "",
        interpretation,
    ]
    (out_dir / "diagnostic_report.md").write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose near-perfect Transformer agency/ownership correlations.")
    parser.add_argument("--output-root", type=Path, default=Path("runs") / "transformer_validation")
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--seed-base", type=int, default=20260522)
    parser.add_argument("--warmup", type=int, default=512)
    parser.add_argument("--probe-steps", type=int, default=128)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--d-model", type=int, default=32)
    parser.add_argument("--n-tokens", type=int, default=12)
    args = parser.parse_args()

    out_dir = ensure_dir(args.output_root / f"transformer_high_corr_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    rows = []
    conditions = difficulty_conditions()
    for condition_idx, condition in enumerate(conditions):
        for seed_idx in range(args.seeds):
            seed = args.seed_base + condition_idx * 1000 + seed_idx
            rows.append(run_one(condition, seed, args.warmup, args.probe_steps, args.d_model, args.n_tokens))
    raw = pd.DataFrame(rows)
    stats_df = compute_stats(raw, args.bootstrap, args.seed_base)
    summary = raw.groupby("condition", as_index=False).mean(numeric_only=True)

    raw.to_csv(out_dir / "transformer_high_corr_raw.csv", index=False)
    summary.to_csv(out_dir / "transformer_high_corr_summary.csv", index=False)
    stats_df.to_csv(out_dir / "transformer_high_corr_stats.csv", index=False)
    save_plots(raw, out_dir)
    write_report(out_dir, raw, stats_df)
    write_json(
        out_dir / "manifest.json",
        {
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "args": vars(args),
            "conditions": conditions,
            "files": {
                "raw": str(out_dir / "transformer_high_corr_raw.csv"),
                "summary": str(out_dir / "transformer_high_corr_summary.csv"),
                "stats": str(out_dir / "transformer_high_corr_stats.csv"),
                "report": str(out_dir / "diagnostic_report.md"),
            },
        },
    )
    print(
        json.dumps(
            {
                "output_dir": str(out_dir),
                "stats": stats_df[["subset", "diagnostic", "r", "r_ci_low", "r_ci_high", "p_formatted"]].to_dict(orient="records"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
