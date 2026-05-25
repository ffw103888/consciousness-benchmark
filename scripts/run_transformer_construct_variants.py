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

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from consciousness_benchmark.core.stats import bootstrap_corr_ci, format_p, pearson
from mind_lab.transformer import (
    TransformerInspiredArchitecture,
    _cosine,
    transformer_agency_probe,
    transformer_boundary_probe,
)
from mind_lab.utils import clamp01, ensure_dir, safe_corr, write_json


def _normalized_distance(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    n = min(a.size, b.size)
    if n == 0:
        return 1.0
    a = a[:n]
    b = b[:n]
    return clamp01(float(np.linalg.norm(a - b) / (np.linalg.norm(a) + np.linalg.norm(b) + 1e-9)))


def _attention_signature(system: TransformerInspiredArchitecture, window: int = 16) -> np.ndarray:
    if not system.attention_history:
        return np.zeros(system.n_tokens * system.n_tokens)
    recent = system.attention_history[-window:]
    return np.mean(np.stack(recent), axis=0).ravel()


def _attention_entropy(att: np.ndarray) -> float:
    att = np.asarray(att, dtype=float)
    entropy = -np.sum(att * np.log(att + 1e-12), axis=1) / np.log(max(att.shape[-1], 2))
    return float(np.mean(entropy))


def attention_focus_probe(
    system: TransformerInspiredArchitecture,
    rng: np.random.Generator,
    *,
    external_salience: float,
    steps: int,
) -> dict[str, float]:
    clone = system.clone()
    baseline = _attention_signature(clone)
    forced_self_mass = []
    forced_external_mass = []
    forced_entropy = []
    forced_pattern_similarity = []
    for _ in range(int(steps)):
        clone.tokens[3] += external_salience * clone.external_marker + rng.normal(0.0, 0.12, size=clone.dim)
        clone.tokens[4] += 0.45 * external_salience * clone.external_marker + rng.normal(0.0, 0.08, size=clone.dim)
        clone.step()
        att = clone.attention_history[-1]
        forced_self_mass.append(float(np.mean(att[:, 0])))
        forced_external_mass.append(float(np.mean(att[:, 3:5])))
        forced_entropy.append(_attention_entropy(att))
        forced_pattern_similarity.append(1.0 - _normalized_distance(att.ravel(), baseline))

    recovery_similarity = []
    recovery_external_leak = []
    for _ in range(max(16, int(steps // 2))):
        clone.step()
        att = clone.attention_history[-1]
        recovery_similarity.append(1.0 - _normalized_distance(att.ravel(), baseline))
        recovery_external_leak.append(float(np.mean(att[:, 3:5])))

    self_mass = float(np.mean(forced_self_mass[-32:]))
    external_mass = float(np.mean(forced_external_mass[-32:]))
    entropy_resistance = 1.0 - float(np.mean(forced_entropy[-32:]))
    pattern_stability = float(np.mean(forced_pattern_similarity[-32:]))
    focus_preference = self_mass / (self_mass + external_mass + 1e-12)
    proxy = clamp01(0.45 * focus_preference + 0.30 * pattern_stability + 0.25 * entropy_resistance)

    final_recovery = float(np.mean(recovery_similarity[-16:]))
    leak_reduction = 1.0 - float(np.mean(recovery_external_leak[-16:]))
    independent = clamp01(0.60 * final_recovery + 0.40 * leak_reduction)
    return {
        "proxy_attention_focus_self": proxy,
        "independent_attention_focus_self": independent,
        "attention_focus_preference": focus_preference,
        "attention_focus_pattern_stability": pattern_stability,
        "attention_focus_entropy_resistance": entropy_resistance,
        "attention_focus_recovery": final_recovery,
        "attention_focus_leak_reduction": leak_reduction,
    }


def context_window_probe(
    system: TransformerInspiredArchitecture,
    rng: np.random.Generator,
    *,
    context_pressure: float,
    steps: int,
) -> dict[str, float]:
    clone = system.clone()
    retention = []
    inclusion = []
    contamination = []
    for _ in range(int(steps)):
        if rng.random() < context_pressure:
            clone.tokens[0] *= 1.0 - 0.55 * context_pressure
            replace_count = max(1, int(round(context_pressure * (clone.n_tokens - 3))))
            replace_idx = rng.choice(np.arange(3, clone.n_tokens), size=replace_count, replace=False)
            clone.tokens[replace_idx] = rng.normal(0.0, 0.35 + 0.45 * context_pressure, size=(replace_count, clone.dim))
        clone.tokens[3:] += context_pressure * rng.normal(0.0, 0.12, size=clone.tokens[3:].shape)
        clone.step()
        broadcast = clone.broadcast_history[-1]
        retention.append(0.5 + 0.5 * _cosine(broadcast, clone.self_marker))
        memory = clone.workspace_memory if clone.enable_workspace else clone.tokens[:1]
        inclusion.append(float(np.mean([0.5 + 0.5 * _cosine(row, clone.self_marker) for row in memory])))
        contamination.append(0.5 + 0.5 * _cosine(broadcast, clone.external_marker))

    proxy = clamp01(
        0.45 * float(np.mean(retention[-32:]))
        + 0.35 * float(np.mean(inclusion[-32:]))
        + 0.20 * (1.0 - float(np.mean(contamination[-32:])))
    )

    own_reentry = []
    decoy_reentry = []
    decoy = rng.normal(size=clone.dim)
    decoy = decoy / (np.linalg.norm(decoy) + 1e-12)
    for _ in range(max(24, int(steps // 2))):
        clone.tokens[0] = 0.68 * clone.tokens[0] + 0.32 * clone.self_marker
        clone.tokens[3] = 0.68 * clone.tokens[3] + 0.32 * decoy
        clone.step()
        broadcast = clone.broadcast_history[-1]
        own_reentry.append(0.5 + 0.5 * _cosine(broadcast, clone.self_marker))
        decoy_reentry.append(0.5 + 0.5 * _cosine(broadcast, decoy))

    discrimination = float(np.mean(own_reentry[-24:]) - np.mean(decoy_reentry[-24:]))
    final_own = float(np.mean(own_reentry[-24:]))
    independent = clamp01(0.50 + 0.90 * discrimination + 0.25 * (final_own - 0.5))
    return {
        "proxy_context_window_self": proxy,
        "independent_context_window_self": independent,
        "context_retention": float(np.mean(retention[-32:])),
        "context_inclusion": float(np.mean(inclusion[-32:])),
        "context_contamination_resistance": 1.0 - float(np.mean(contamination[-32:])),
        "context_reentry_discrimination": discrimination,
        "context_reentry_own": final_own,
    }


def base_transformer_config(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "d_model": args.d_model,
        "n_tokens": args.n_tokens,
        "workspace_capacity": args.workspace_capacity,
    }


def run_attention_focus(args: argparse.Namespace) -> pd.DataFrame:
    rows = []
    for salience in [0.0, 0.35, 0.70, 1.10, 1.60]:
        for seed_idx in range(args.seeds):
            seed = args.seed_base + int(salience * 1000) + seed_idx
            config = {
                **base_transformer_config(args),
                "workspace": True,
                "action_loop": False,
                "external_filter_strength": 0.55,
            }
            system = TransformerInspiredArchitecture(config, seed=seed)
            system.run_steps(args.warmup)
            result = attention_focus_probe(system, np.random.default_rng(seed + 11_000_000), external_salience=salience, steps=args.probe_steps)
            rows.append({"study": "attention_focus_self", "condition": f"salience_{salience:.2f}", "dose": salience, "seed": seed, **result})
    return pd.DataFrame(rows)


def run_context_window(args: argparse.Namespace) -> pd.DataFrame:
    rows = []
    for pressure in [0.0, 0.20, 0.40, 0.65, 0.90]:
        for seed_idx in range(args.seeds):
            seed = args.seed_base + 20_000 + int(pressure * 1000) + seed_idx
            config = {
                **base_transformer_config(args),
                "workspace": True,
                "action_loop": False,
                "workspace_strength": 0.82,
            }
            system = TransformerInspiredArchitecture(config, seed=seed)
            system.run_steps(args.warmup)
            result = context_window_probe(system, np.random.default_rng(seed + 12_000_000), context_pressure=pressure, steps=args.probe_steps)
            rows.append({"study": "context_window_self", "condition": f"pressure_{pressure:.2f}", "dose": pressure, "seed": seed, **result})
    return pd.DataFrame(rows)


def workspace_config_for_dose(dose: float) -> dict[str, Any]:
    if dose <= 0.0:
        return {
            "workspace": False,
            "workspace_strength": 0.0,
            "workspace_marker_injection": 0.02,
            "external_filter_strength": 0.0,
            "workspace_self_anchor": 0.0,
            "broadcast_self_anchor": 0.0,
        }
    return {
        "workspace": True,
        "workspace_strength": 0.35 + 0.55 * dose,
        "workspace_marker_injection": 0.05 + 0.17 * dose,
        "external_filter_strength": 0.10 + 0.80 * dose,
        "workspace_self_anchor": 0.05 + 0.19 * dose,
        "broadcast_self_anchor": 0.05 + 0.21 * dose,
        "workspace_update_rate": 0.12 + 0.24 * dose,
    }


def run_predictive_agency_without_boundary(args: argparse.Namespace) -> pd.DataFrame:
    rows = []
    for workspace_dose in [0.0, 0.35, 0.70, 1.0]:
        for effect_noise in [0.02, 0.12, 0.42]:
            for seed_idx in range(args.seeds):
                seed = args.seed_base + 40_000 + int(workspace_dose * 1000) * 10 + int(effect_noise * 1000) + seed_idx
                config = {
                    **base_transformer_config(args),
                    **workspace_config_for_dose(workspace_dose),
                    "action_loop": True,
                    "effect_noise_scale": effect_noise,
                    "action_learning_rate": 0.040,
                }
                system = TransformerInspiredArchitecture(config, seed=seed)
                system.run_steps(args.warmup)
                rng = np.random.default_rng(seed + 13_000_000)
                profile = system.evaluation_profile()
                details = profile["details"]
                agency = transformer_agency_probe(system, rng, steps=args.probe_steps)
                boundary = transformer_boundary_probe(system, rng, steps=args.probe_steps)
                high_agency_low_boundary = bool(agency.score >= 0.70 and boundary.score < 0.50)
                rows.append(
                    {
                        "study": "predictive_agency_without_boundary",
                        "condition": f"workspace_{workspace_dose:.2f}_noise_{effect_noise:.2f}",
                        "dose": workspace_dose,
                        "effect_noise_scale": effect_noise,
                        "seed": seed,
                        "proxy_agency": details["proxy_agency"],
                        "independent_agency": agency.score,
                        "proxy_boundary_self": details["proxy_boundary_self"],
                        "independent_boundary_self": boundary.score,
                        "high_agency_low_boundary": high_agency_low_boundary,
                    }
                )
    return pd.DataFrame(rows)


def correlation_table(raw: pd.DataFrame, bootstrap: int, seed: int) -> pd.DataFrame:
    specs = [
        ("attention_focus_self", "proxy_attention_focus_self", "independent_attention_focus_self"),
        ("attention_focus_self", "dose", "independent_attention_focus_self"),
        ("context_window_self", "proxy_context_window_self", "independent_context_window_self"),
        ("context_window_self", "dose", "independent_context_window_self"),
        ("predictive_agency_without_boundary", "proxy_agency", "independent_agency"),
        ("predictive_agency_without_boundary", "proxy_boundary_self", "independent_boundary_self"),
        ("predictive_agency_without_boundary", "independent_agency", "independent_boundary_self"),
    ]
    rows = []
    for study, x_col, y_col in specs:
        subset = raw[raw["study"] == study]
        if x_col not in subset.columns or y_col not in subset.columns:
            continue
        r, p, n = pearson(subset[x_col], subset[y_col])
        ci_low, ci_high = bootstrap_corr_ci(subset[x_col], subset[y_col], seed=seed, n_bootstrap=bootstrap)
        rows.append(
            {
                "study": study,
                "x": x_col,
                "y": y_col,
                "n": n,
                "r": r,
                "r_ci_low": ci_low,
                "r_ci_high": ci_high,
                "p": p,
                "p_formatted": format_p(p),
                "candidate_validated": bool(np.isfinite(r) and abs(r) >= 0.7 and x_col.startswith("proxy_")),
            }
        )
    return pd.DataFrame(rows)


def save_plots(raw: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    att = raw[raw["study"] == "attention_focus_self"]
    ctx = raw[raw["study"] == "context_window_self"]
    quad = raw[raw["study"] == "predictive_agency_without_boundary"]

    att_summary = att.groupby("dose", as_index=False).mean(numeric_only=True)
    axes[0].plot(att_summary["dose"], att_summary["proxy_attention_focus_self"], "o-", label="proxy")
    axes[0].plot(att_summary["dose"], att_summary["independent_attention_focus_self"], "o-", label="independent")
    axes[0].set_title("Attention-focus self candidate")
    axes[0].set_xlabel("External salience")
    axes[0].set_ylabel("Score")
    axes[0].set_ylim(0, 1)
    axes[0].grid(True, alpha=0.25)
    axes[0].legend()

    ctx_summary = ctx.groupby("dose", as_index=False).mean(numeric_only=True)
    axes[1].plot(ctx_summary["dose"], ctx_summary["proxy_context_window_self"], "o-", label="proxy")
    axes[1].plot(ctx_summary["dose"], ctx_summary["independent_context_window_self"], "o-", label="independent")
    axes[1].set_title("Context-window self candidate")
    axes[1].set_xlabel("Context pressure")
    axes[1].set_ylabel("Score")
    axes[1].set_ylim(0, 1)
    axes[1].grid(True, alpha=0.25)
    axes[1].legend()

    scatter = axes[2].scatter(quad["independent_boundary_self"], quad["independent_agency"], c=quad["dose"], cmap="viridis", s=52, alpha=0.78)
    axes[2].axhline(0.70, color="tab:green", linestyle="--", linewidth=1)
    axes[2].axvline(0.50, color="tab:red", linestyle="--", linewidth=1)
    axes[2].set_title("Predictive agency without boundary")
    axes[2].set_xlabel("Independent boundary score")
    axes[2].set_ylabel("Independent agency score")
    axes[2].set_xlim(0, 1)
    axes[2].set_ylim(0, 1)
    axes[2].grid(True, alpha=0.25)
    fig.colorbar(scatter, ax=axes[2], label="Workspace dose")
    fig.tight_layout()
    fig.savefig(out_dir / "transformer_construct_variants_overview.png", dpi=180)
    plt.close(fig)


def write_report(out_dir: Path, raw: pd.DataFrame, stats_df: pd.DataFrame, summary: pd.DataFrame) -> None:
    quad = raw[raw["study"] == "predictive_agency_without_boundary"]
    high_low_count = int(quad["high_agency_low_boundary"].sum()) if not quad.empty else 0
    high_low_rate = high_low_count / max(len(quad), 1)
    report = [
        "# Transformer Construct Variant Mini-Study",
        "",
        "This exploratory run follows the Transformer follow-up. It tests candidate architecture-conditioned constructs rather than upgrading any main-paper claim.",
        "",
        "## Correlations",
        "",
        stats_df.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Condition Summary",
        "",
        summary.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Predictive Agency Without Boundary",
        "",
        f"- high agency / low boundary rows: {high_low_count}/{len(quad)} ({high_low_rate:.1%})",
        "",
        "## Interpretation Guardrail",
        "",
        "These are construct-discovery probes. A candidate should only be promoted after independent probe redesign, graded controls, and cross-seed stability checks.",
    ]
    (out_dir / "transformer_construct_variants_report.md").write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run exploratory Transformer construct-variant probes.")
    parser.add_argument("--output-root", type=Path, default=Path("runs") / "transformer_validation")
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--seed-base", type=int, default=20260522)
    parser.add_argument("--warmup", type=int, default=512)
    parser.add_argument("--probe-steps", type=int, default=128)
    parser.add_argument("--bootstrap", type=int, default=1000)
    parser.add_argument("--d-model", type=int, default=32)
    parser.add_argument("--n-tokens", type=int, default=12)
    parser.add_argument("--workspace-capacity", type=int, default=4)
    args = parser.parse_args()

    out_dir = ensure_dir(args.output_root / f"transformer_construct_variants_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    frames = [run_attention_focus(args), run_context_window(args), run_predictive_agency_without_boundary(args)]
    raw = pd.concat(frames, ignore_index=True, sort=False)
    summary = raw.groupby(["study", "condition"], as_index=False).mean(numeric_only=True)
    stats_df = correlation_table(raw, args.bootstrap, args.seed_base)
    raw.to_csv(out_dir / "transformer_construct_variants_raw.csv", index=False)
    summary.to_csv(out_dir / "transformer_construct_variants_summary.csv", index=False)
    stats_df.to_csv(out_dir / "transformer_construct_variants_stats.csv", index=False)
    save_plots(raw, out_dir)
    write_report(out_dir, raw, stats_df, summary)
    write_json(
        out_dir / "manifest.json",
        {
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "args": vars(args),
            "files": {
                "raw": str(out_dir / "transformer_construct_variants_raw.csv"),
                "summary": str(out_dir / "transformer_construct_variants_summary.csv"),
                "stats": str(out_dir / "transformer_construct_variants_stats.csv"),
                "report": str(out_dir / "transformer_construct_variants_report.md"),
                "overview": str(out_dir / "transformer_construct_variants_overview.png"),
            },
        },
    )
    print(
        json.dumps(
            {
                "output_dir": str(out_dir),
                "rows": len(raw),
                "stats": stats_df[["study", "x", "y", "r", "r_ci_low", "r_ci_high", "p_formatted", "candidate_validated"]].to_dict(orient="records"),
                "high_agency_low_boundary_rows": int(raw.get("high_agency_low_boundary", pd.Series(dtype=bool)).fillna(False).sum()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
