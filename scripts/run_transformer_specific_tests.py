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

from consciousness_benchmark.core.stats import bootstrap_corr_ci, format_p, pearson
from mind_lab.transformer import TransformerInspiredArchitecture, _cosine, transformer_boundary_probe
from mind_lab.utils import clamp01, ensure_dir, safe_corr, write_json


def workspace_conditions() -> list[dict[str, Any]]:
    return [
        {
            "condition": "workspace_off",
            "dose": 0.0,
            "workspace": False,
            "workspace_strength": 0.0,
            "workspace_capacity": 4,
        },
        {
            "condition": "workspace_weak",
            "dose": 0.25,
            "workspace": True,
            "workspace_strength": 0.35,
            "workspace_capacity": 2,
            "workspace_marker_injection": 0.06,
            "transient_marker_injection": 0.02,
            "external_filter_strength": 0.12,
            "workspace_self_anchor": 0.06,
            "broadcast_self_anchor": 0.05,
            "workspace_update_rate": 0.12,
        },
        {
            "condition": "workspace_mid",
            "dose": 0.55,
            "workspace": True,
            "workspace_strength": 0.62,
            "workspace_capacity": 4,
            "workspace_marker_injection": 0.12,
            "external_filter_strength": 0.38,
            "workspace_self_anchor": 0.12,
            "broadcast_self_anchor": 0.12,
            "workspace_update_rate": 0.22,
        },
        {
            "condition": "workspace_strong",
            "dose": 0.80,
            "workspace": True,
            "workspace_strength": 0.78,
            "workspace_capacity": 4,
            "workspace_marker_injection": 0.16,
            "external_filter_strength": 0.55,
            "workspace_self_anchor": 0.16,
            "broadcast_self_anchor": 0.18,
            "workspace_update_rate": 0.28,
        },
        {
            "condition": "workspace_very_strong",
            "dose": 1.0,
            "workspace": True,
            "workspace_strength": 0.90,
            "workspace_capacity": 6,
            "workspace_marker_injection": 0.22,
            "external_filter_strength": 0.90,
            "workspace_self_anchor": 0.24,
            "broadcast_self_anchor": 0.26,
            "workspace_update_rate": 0.36,
        },
    ]


def attention_self_other_probe(system: TransformerInspiredArchitecture, rng: np.random.Generator, steps: int) -> dict[str, float]:
    clone = system.clone()
    self_mass = []
    external_mass = []
    external_leak = []
    for _ in range(int(steps)):
        clone.tokens[0] += 0.55 * clone.self_marker
        clone.tokens[3] += 1.10 * clone.external_marker + rng.normal(0.0, 0.15, size=clone.dim)
        clone.step()
        att = clone.attention_history[-1]
        self_mass.append(float(np.mean(att[:, 0])))
        external_mass.append(float(np.mean(att[:, 3])))
        external_leak.append(0.5 + 0.5 * _cosine(clone.broadcast_history[-1], clone.external_marker))
    self_mean = float(np.mean(self_mass[-32:]))
    external_mean = float(np.mean(external_mass[-32:]))
    preference = self_mean / (self_mean + external_mean + 1e-12)
    rejection = 1.0 - float(np.mean(external_leak[-32:]))
    score = clamp01(0.60 * preference + 0.40 * rejection)
    return {
        "attention_self_other_score": score,
        "attention_self_mass": self_mean,
        "attention_external_mass": external_mean,
        "attention_external_rejection": rejection,
    }


def attention_boundary_perturbation_probe(system: TransformerInspiredArchitecture, rng: np.random.Generator, steps: int) -> dict[str, float]:
    baseline = system.clone()
    baseline.step()
    baseline_attention = baseline.attention_history[-1]

    protected = system.clone()
    protected.tokens[0] += rng.normal(0.0, 0.90, size=protected.dim)
    protected.workspace_memory += rng.normal(0.0, 0.45, size=protected.workspace_memory.shape)
    protected_recovery = []
    protected_self_mass = []
    for _ in range(int(steps)):
        protected.step()
        att = protected.attention_history[-1]
        protected_recovery.append(1.0 - np.linalg.norm(att - baseline_attention) / (np.linalg.norm(att) + np.linalg.norm(baseline_attention) + 1e-9))
        protected_self_mass.append(float(np.mean(att[:, 0])))

    external = system.clone()
    external_rejection = []
    for _ in range(int(steps)):
        external.tokens[3:] += 1.30 * external.external_marker + rng.normal(0.0, 0.22, size=external.tokens[3:].shape)
        external.step()
        external_rejection.append(1.0 - (0.5 + 0.5 * _cosine(external.broadcast_history[-1], external.external_marker)))

    recovery = clamp01(float(np.mean(protected_recovery[-32:])))
    self_mass = clamp01(8.0 * float(np.mean(protected_self_mass[-32:])))
    rejection = clamp01(float(np.mean(external_rejection[-32:])))
    score = clamp01(0.35 * recovery + 0.25 * self_mass + 0.40 * rejection)
    return {
        "attention_boundary_perturbation_score": score,
        "attention_pattern_recovery": recovery,
        "attention_protected_self_mass": self_mass,
        "attention_external_rejection": rejection,
    }


def workspace_lesion_probe(system: TransformerInspiredArchitecture, rng: np.random.Generator, steps: int) -> dict[str, float]:
    baseline = system.evaluation_profile()["details"]["proxy_boundary_self"]
    clone = system.clone()
    clone.workspace_memory[:] = 0.0
    clone.workspace_strength = 0.0
    clone.external_filter_strength = 0.0
    clone.workspace_self_anchor = 0.0
    clone.broadcast_self_anchor = 0.0
    clone.workspace_marker_injection = clone.transient_marker_injection
    clone.run_steps(max(8, int(steps // 2)))
    lesioned = clone.evaluation_profile()["details"]["proxy_boundary_self"]
    drop = max(0.0, float(baseline - lesioned))
    score = clamp01(drop / 0.65)
    return {
        "workspace_lesion_score": score,
        "workspace_lesion_drop": drop,
        "workspace_baseline_boundary_proxy": float(baseline),
        "workspace_lesioned_boundary_proxy": float(lesioned),
    }


def run_one(condition: dict[str, Any], seed: int, warmup: int, probe_steps: int, d_model: int, n_tokens: int) -> dict[str, Any]:
    config = {
        "d_model": d_model,
        "n_tokens": n_tokens,
        "action_loop": False,
        **condition,
    }
    system = TransformerInspiredArchitecture(config, seed=seed)
    system.run_steps(warmup)
    rng = np.random.default_rng(seed + 9_100_000)
    profile = system.evaluation_profile()
    details = profile["details"]

    generic = transformer_boundary_probe(system, rng, steps=probe_steps)
    self_other = attention_self_other_probe(system, rng, probe_steps)
    perturb = attention_boundary_perturbation_probe(system, rng, probe_steps)
    lesion = workspace_lesion_probe(system, rng, probe_steps)
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
        "condition": condition["condition"],
        "dose": float(condition["dose"]),
        "seed": seed,
        "workspace": bool(condition["workspace"]),
        "proxy_boundary_self": float(details["proxy_boundary_self"]),
        "generic_boundary_probe": generic.score,
        "hard_attention_boundary": hard_attention_boundary,
        **self_other,
        **perturb,
        **lesion,
        "workspace_occupancy": float(details["workspace_occupancy"]),
        "workspace_coherence": float(details["workspace_coherence"]),
        "marker_alignment": float(details["marker_alignment"]),
    }


def compute_stats(raw: pd.DataFrame, bootstrap: int, seed: int) -> pd.DataFrame:
    pairs = [
        ("proxy_vs_generic_boundary", "proxy_boundary_self", "generic_boundary_probe"),
        ("proxy_vs_hard_attention_boundary", "proxy_boundary_self", "hard_attention_boundary"),
        ("dose_vs_hard_attention_boundary", "dose", "hard_attention_boundary"),
        ("dose_vs_proxy_boundary", "dose", "proxy_boundary_self"),
    ]
    rows = []
    for key, x_col, y_col in pairs:
        r, p, n = pearson(raw[x_col], raw[y_col])
        ci_low, ci_high = bootstrap_corr_ci(raw[x_col], raw[y_col], seed=seed, n_bootstrap=bootstrap)
        rows.append(
            {
                "diagnostic": key,
                "x": x_col,
                "y": y_col,
                "n": n,
                "r": r,
                "r_ci_low": ci_low,
                "r_ci_high": ci_high,
                "p": p,
                "p_formatted": format_p(p),
                "validated": bool(np.isfinite(r) and r >= 0.7),
            }
        )
    return pd.DataFrame(rows)


def save_plots(raw: pd.DataFrame, summary: pd.DataFrame, stats_df: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    pairs = [
        ("proxy_boundary_self", "generic_boundary_probe", "Generic boundary probe"),
        ("proxy_boundary_self", "hard_attention_boundary", "Attention-specific hard probe"),
        ("dose", "hard_attention_boundary", "Workspace dose response"),
    ]
    for ax, (x_col, y_col, title) in zip(axes, pairs):
        ax.scatter(raw[x_col], raw[y_col], s=42, alpha=0.75)
        if x_col != "dose":
            ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.55)
            ax.set_xlim(-0.03, 1.03)
        ax.set_ylim(-0.03, 1.03)
        r = safe_corr(raw[x_col].to_numpy(float), raw[y_col].to_numpy(float))
        ax.set_title(f"{title}\nr={r:.2f}")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "transformer_attention_boundary_scatter.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.2, 5.4))
    ordered = summary.sort_values("dose")
    ax.plot(ordered["dose"], ordered["proxy_boundary_self"], "o-", label="boundary proxy")
    ax.plot(ordered["dose"], ordered["generic_boundary_probe"], "o-", label="generic probe")
    ax.plot(ordered["dose"], ordered["hard_attention_boundary"], "o-", label="attention-specific hard probe")
    ax.plot(ordered["dose"], ordered["workspace_lesion_score"], "o-", label="workspace lesion")
    ax.set_xlabel("Workspace dose")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.set_title("Transformer attention-boundary dose response")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "transformer_attention_boundary_dose_response.png", dpi=180)
    plt.close(fig)


def write_report(out_dir: Path, stats_df: pd.DataFrame, summary: pd.DataFrame) -> None:
    hard_r = float(stats_df[stats_df["diagnostic"] == "proxy_vs_hard_attention_boundary"]["r"].iloc[0])
    interpretation = (
        "Attention-specific probes lift Transformer boundary validation above the 0.7 threshold, supporting an architecture-specific measurement interpretation."
        if hard_r >= 0.7
        else "Attention-specific probes improve diagnostics but do not yet validate boundary self above threshold; keep Transformer boundary self as a measurement-limited result."
    )
    report = [
        "# Transformer-Specific Boundary Tests",
        "",
        "## Correlations",
        "",
        stats_df.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Condition Summary",
        "",
        summary.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Interpretation",
        "",
        interpretation,
    ]
    (out_dir / "transformer_specific_boundary_report.md").write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Transformer-specific attention-boundary tests.")
    parser.add_argument("--output-root", type=Path, default=Path("runs") / "transformer_validation")
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--seed-base", type=int, default=20260522)
    parser.add_argument("--warmup", type=int, default=512)
    parser.add_argument("--probe-steps", type=int, default=128)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--d-model", type=int, default=32)
    parser.add_argument("--n-tokens", type=int, default=12)
    args = parser.parse_args()

    out_dir = ensure_dir(args.output_root / f"transformer_specific_boundary_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    rows = []
    conditions = workspace_conditions()
    for condition_idx, condition in enumerate(conditions):
        for seed_idx in range(args.seeds):
            seed = args.seed_base + condition_idx * 1000 + seed_idx
            rows.append(run_one(condition, seed, args.warmup, args.probe_steps, args.d_model, args.n_tokens))
    raw = pd.DataFrame(rows)
    summary = raw.groupby("condition", as_index=False).mean(numeric_only=True)
    stats_df = compute_stats(raw, args.bootstrap, args.seed_base)

    raw.to_csv(out_dir / "transformer_specific_boundary_raw.csv", index=False)
    summary.to_csv(out_dir / "transformer_specific_boundary_summary.csv", index=False)
    stats_df.to_csv(out_dir / "transformer_specific_boundary_stats.csv", index=False)
    save_plots(raw, summary, stats_df, out_dir)
    write_report(out_dir, stats_df, summary)
    write_json(
        out_dir / "manifest.json",
        {
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "args": vars(args),
            "conditions": conditions,
            "files": {
                "raw": str(out_dir / "transformer_specific_boundary_raw.csv"),
                "summary": str(out_dir / "transformer_specific_boundary_summary.csv"),
                "stats": str(out_dir / "transformer_specific_boundary_stats.csv"),
                "report": str(out_dir / "transformer_specific_boundary_report.md"),
            },
        },
    )
    print(
        json.dumps(
            {
                "output_dir": str(out_dir),
                "stats": stats_df[["diagnostic", "r", "r_ci_low", "r_ci_high", "p_formatted", "validated"]].to_dict(orient="records"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
