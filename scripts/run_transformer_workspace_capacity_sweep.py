from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

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
from mind_lab.transformer import TransformerInspiredArchitecture, transformer_boundary_probe
from mind_lab.utils import ensure_dir, safe_corr, write_json
from scripts.run_transformer_specific_tests import (
    attention_boundary_perturbation_probe,
    attention_self_other_probe,
    workspace_lesion_probe,
)


def parse_capacities(text: str) -> list[int]:
    capacities = [int(x.strip()) for x in text.split(",") if x.strip()]
    if not capacities:
        raise ValueError("At least one workspace capacity is required.")
    return capacities


def capacity_config(capacity: int, d_model: int, n_tokens: int, action_loop: bool) -> dict[str, object]:
    workspace_on = int(capacity) > 0
    return {
        "d_model": int(d_model),
        "n_tokens": int(n_tokens),
        "workspace": workspace_on,
        "action_loop": bool(action_loop),
        "workspace_capacity": max(1, int(capacity)),
        "workspace_strength": 0.78 if workspace_on else 0.0,
    }


def run_one(capacity: int, seed: int, args: argparse.Namespace) -> dict[str, object]:
    system = TransformerInspiredArchitecture(
        capacity_config(capacity, args.d_model, args.n_tokens, args.action_loop),
        seed=seed,
    )
    system.run_steps(args.warmup)
    rng = np.random.default_rng(seed + 9_400_000)
    profile = system.evaluation_profile()
    details = profile["details"]

    generic = transformer_boundary_probe(system, rng, steps=args.probe_steps)
    self_other = attention_self_other_probe(system, rng, args.probe_steps)
    perturb = attention_boundary_perturbation_probe(system, rng, args.probe_steps)
    lesion = workspace_lesion_probe(system, rng, args.probe_steps)
    hard_attention_boundary = float(
        np.mean(
            [
                self_other["attention_self_other_score"],
                perturb["attention_boundary_perturbation_score"],
                lesion["workspace_lesion_score"],
            ]
        )
    )

    return {
        "architecture": "transformer",
        "condition": f"capacity_{capacity}",
        "capacity": int(capacity),
        "workspace": bool(capacity > 0),
        "action_loop": bool(args.action_loop),
        "seed": int(seed),
        "proxy_boundary_self": float(details["proxy_boundary_self"]),
        "generic_boundary_probe": float(generic.score),
        "hard_attention_boundary": hard_attention_boundary,
        "workspace_occupancy": float(details["workspace_occupancy"]),
        "workspace_coherence": float(details["workspace_coherence"]),
        "marker_alignment": float(details["marker_alignment"]),
        **self_other,
        **perturb,
        **lesion,
    }


def spearman(x: Iterable[float], y: Iterable[float]) -> tuple[float, float]:
    xx = np.asarray(list(x), dtype=float)
    yy = np.asarray(list(y), dtype=float)
    mask = np.isfinite(xx) & np.isfinite(yy)
    if int(mask.sum()) < 3:
        return float("nan"), float("nan")
    result = stats.spearmanr(xx[mask], yy[mask])
    return float(result.correlation), float(result.pvalue)


def compute_stats(raw: pd.DataFrame, bootstrap: int, seed: int) -> pd.DataFrame:
    pairs = [
        ("capacity_vs_boundary_proxy", "capacity", "proxy_boundary_self"),
        ("capacity_vs_generic_boundary", "capacity", "generic_boundary_probe"),
        ("capacity_vs_hard_attention_boundary", "capacity", "hard_attention_boundary"),
        ("proxy_vs_generic_boundary", "proxy_boundary_self", "generic_boundary_probe"),
        ("proxy_vs_hard_attention_boundary", "proxy_boundary_self", "hard_attention_boundary"),
    ]
    rows = []
    for key, x_col, y_col in pairs:
        r, p, n = pearson(raw[x_col], raw[y_col])
        ci_low, ci_high = bootstrap_corr_ci(raw[x_col], raw[y_col], seed=seed, n_bootstrap=bootstrap)
        rho, rho_p = spearman(raw[x_col], raw[y_col])
        rows.append(
            {
                "diagnostic": key,
                "x": x_col,
                "y": y_col,
                "n": n,
                "pearson_r": r,
                "pearson_ci_low": ci_low,
                "pearson_ci_high": ci_high,
                "pearson_p": p,
                "pearson_p_formatted": format_p(p),
                "spearman_rho": rho,
                "spearman_p": rho_p,
                "spearman_p_formatted": format_p(rho_p),
            }
        )
    return pd.DataFrame(rows)


def save_plots(raw: pd.DataFrame, summary: pd.DataFrame, out_dir: Path) -> None:
    ordered = summary.sort_values("capacity")
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    ax.plot(ordered["capacity"], ordered["proxy_boundary_self"], "o-", label="boundary proxy")
    ax.plot(ordered["capacity"], ordered["generic_boundary_probe"], "o-", label="generic boundary probe")
    ax.plot(ordered["capacity"], ordered["hard_attention_boundary"], "o-", label="attention-specific hard probe")
    ax.plot(ordered["capacity"], ordered["workspace_lesion_score"], "o-", label="workspace lesion")
    ax.set_xlabel("Workspace capacity")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.set_title("Transformer workspace capacity sweep")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "transformer_workspace_capacity_response.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.7))
    axes[0].scatter(raw["proxy_boundary_self"], raw["generic_boundary_probe"], s=42, alpha=0.72)
    axes[0].plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.55)
    axes[0].set_title(f"Proxy vs generic probe\nr={safe_corr(raw['proxy_boundary_self'], raw['generic_boundary_probe']):.2f}")
    axes[0].set_xlabel("proxy_boundary_self")
    axes[0].set_ylabel("generic_boundary_probe")
    axes[0].set_xlim(-0.03, 1.03)
    axes[0].set_ylim(-0.03, 1.03)
    axes[0].grid(True, alpha=0.25)

    axes[1].scatter(raw["proxy_boundary_self"], raw["hard_attention_boundary"], s=42, alpha=0.72)
    axes[1].plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.55)
    axes[1].set_title(f"Proxy vs hard probe\nr={safe_corr(raw['proxy_boundary_self'], raw['hard_attention_boundary']):.2f}")
    axes[1].set_xlabel("proxy_boundary_self")
    axes[1].set_ylabel("hard_attention_boundary")
    axes[1].set_xlim(-0.03, 1.03)
    axes[1].set_ylim(-0.03, 1.03)
    axes[1].grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "transformer_workspace_capacity_scatter.png", dpi=180)
    plt.close(fig)


def write_report(out_dir: Path, stats_df: pd.DataFrame, summary: pd.DataFrame, args: argparse.Namespace) -> None:
    lines = [
        "# Transformer Workspace Capacity Sweep",
        "",
        "## Run",
        "",
        f"- Capacities: `{args.capacities}`",
        f"- Seeds per capacity: `{args.seeds}`",
        f"- Action loop enabled: `{args.action_loop}`",
        f"- Warmup steps: `{args.warmup}`",
        f"- Probe steps: `{args.probe_steps}`",
        "",
        "## Correlations",
        "",
        stats_df.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Capacity Summary",
        "",
        summary.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Interpretation Guardrail",
        "",
        "This sweep tests whether Transformer workspace capacity drives internal boundary proxies and whether that effect transfers to independent boundary probes. It is supplementary evidence and does not alter the frozen primary results.",
    ]
    (out_dir / "transformer_workspace_capacity_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a Transformer workspace-capacity sweep for supplementary diagnostics.")
    parser.add_argument("--output-root", type=Path, default=Path("runs") / "supplementary")
    parser.add_argument("--capacities", default="0,1,2,4,8")
    parser.add_argument("--seeds", type=int, default=16)
    parser.add_argument("--seed-base", type=int, default=20260522)
    parser.add_argument("--warmup", type=int, default=512)
    parser.add_argument("--probe-steps", type=int, default=128)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--d-model", type=int, default=32)
    parser.add_argument("--n-tokens", type=int, default=12)
    parser.add_argument("--action-loop", action="store_true", help="Enable action loop while sweeping workspace capacity.")
    args = parser.parse_args()

    capacities = parse_capacities(args.capacities)
    out_dir = ensure_dir(args.output_root / f"transformer_workspace_capacity_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    rows = []
    total = len(capacities) * args.seeds
    completed = 0
    for condition_idx, capacity in enumerate(capacities):
        for seed_idx in range(args.seeds):
            seed = args.seed_base + condition_idx * 1000 + seed_idx
            rows.append(run_one(capacity, seed, args))
            completed += 1
            pd.DataFrame(rows).to_csv(out_dir / "transformer_workspace_capacity_raw.partial.csv", index=False)
            (out_dir / "progress.json").write_text(
                json.dumps({"completed": completed, "total": total, "updated_at": datetime.now().astimezone().isoformat(timespec="seconds")}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    raw = pd.DataFrame(rows)
    summary = raw.groupby("capacity", as_index=False).mean(numeric_only=True)
    stats_df = compute_stats(raw, args.bootstrap, args.seed_base)
    raw.to_csv(out_dir / "transformer_workspace_capacity_raw.csv", index=False)
    summary.to_csv(out_dir / "transformer_workspace_capacity_summary.csv", index=False)
    stats_df.to_csv(out_dir / "transformer_workspace_capacity_stats.csv", index=False)
    save_plots(raw, summary, out_dir)
    write_report(out_dir, stats_df, summary, args)

    manifest = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "args": vars(args),
        "capacities": capacities,
        "row_count": int(len(raw)),
        "files": {
            "raw": str(out_dir / "transformer_workspace_capacity_raw.csv"),
            "summary": str(out_dir / "transformer_workspace_capacity_summary.csv"),
            "stats": str(out_dir / "transformer_workspace_capacity_stats.csv"),
            "report": str(out_dir / "transformer_workspace_capacity_report.md"),
            "response_plot": str(out_dir / "transformer_workspace_capacity_response.png"),
            "scatter_plot": str(out_dir / "transformer_workspace_capacity_scatter.png"),
        },
        "claim_boundary": "Supplementary operational diagnostics only; primary manuscript statistics remain frozen.",
    }
    write_json(out_dir / "manifest.json", manifest)
    print(json.dumps({"output_dir": str(out_dir), "stats": stats_df.to_dict(orient="records")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
