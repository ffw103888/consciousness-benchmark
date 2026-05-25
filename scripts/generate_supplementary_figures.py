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

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mind_lab.utils import ensure_dir, safe_corr


PAPER_DIR = PROJECT_ROOT / "docs" / "paper"
STATS_DIR = PAPER_DIR / "statistics" / "supplementary_20260522"
FIG_DIR = PAPER_DIR / "figures" / "supplementary_20260522"


def _finite_pair(df: pd.DataFrame, x_col: str, y_col: str) -> pd.DataFrame:
    sub = df[[x_col, y_col, "condition_set"]].replace([np.inf, -np.inf], np.nan).dropna()
    return sub


def figure_s1() -> Path:
    raw_path = STATS_DIR / "online_16seed_raw.csv"
    stats_path = STATS_DIR / "online_16seed_construct_validation_stats.csv"
    raw = pd.read_csv(raw_path)
    stats = pd.read_csv(stats_path).set_index("construct_key")
    pairs = [
        ("action_agency", "Action agency", "proxy_agency", "independent_agency"),
        ("boundary_self", "Boundary self", "proxy_boundary_self", "independent_self_core_boundary"),
        ("identity_temporal_self", "Identity-temporal", "proxy_identity_marker_persistence", "test_delayed_identity_recognition"),
        ("action_ownership", "Action ownership", "proxy_action_attribution", "test_forced_choice_ownership"),
        ("distributed_body_schema_self", "Distributed body-schema", "proxy_distributed_body_schema_self", "hard_self_without_lesion"),
    ]
    colors = {
        "thalamus": "#3B82F6",
        "distributed": "#059669",
        "meta-strength": "#D97706",
        "meta-noise": "#DC2626",
        "meta-delay": "#7C3AED",
    }
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 8.2))
    axes_flat = axes.ravel()
    for ax, (key, label, x_col, y_col) in zip(axes_flat, pairs):
        sub = _finite_pair(raw, x_col, y_col)
        for condition_set, group in sub.groupby("condition_set"):
            ax.scatter(
                group[x_col],
                group[y_col],
                s=22,
                alpha=0.58,
                color=colors.get(condition_set, "gray"),
                label=condition_set,
                edgecolors="none",
            )
        ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.5)
        r = float(stats.loc[key, "r"])
        lo = float(stats.loc[key, "r_ci_low"])
        hi = float(stats.loc[key, "r_ci_high"])
        n = int(stats.loc[key, "n"])
        ax.set_title(f"{label}\nn={n}, r={r:.3f} [{lo:.3f}, {hi:.3f}]")
        ax.set_xlabel("Proxy")
        ax.set_ylabel("Independent probe")
        ax.set_xlim(-0.03, 1.03)
        ax.set_ylim(-0.03, 1.03)
        ax.grid(True, alpha=0.25)
    axes_flat[-1].axis("off")
    handles, labels = axes_flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower right", bbox_to_anchor=(0.91, 0.11), frameon=False)
    fig.suptitle("Supplementary Figure S1. Extended 16-seed validation", fontsize=15, fontweight="bold")
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    out_path = FIG_DIR / "figureS1_extended_16seed_validation.png"
    fig.savefig(out_path, dpi=220)
    plt.close(fig)
    return out_path


def figure_s2() -> Path:
    thal = pd.read_csv(STATS_DIR / "thalamus_workspace_capacity_summary.csv").sort_values("capacity")
    trans = pd.read_csv(STATS_DIR / "transformer_workspace_capacity_summary.csv").sort_values("capacity")
    thal_stats = pd.read_csv(STATS_DIR / "thalamus_workspace_capacity_stats.csv").set_index("diagnostic")
    trans_stats = pd.read_csv(STATS_DIR / "transformer_workspace_capacity_stats.csv").set_index("diagnostic")
    fig, axes = plt.subplots(2, 2, figsize=(12.0, 8.2), sharex="col")

    axes[0, 0].plot(thal["capacity"], thal["proxy_boundary_self"], "o-", label="proxy", color="#2563EB")
    axes[0, 0].plot(thal["capacity"], thal["independent_self_core_boundary"], "o-", label="independent", color="#F97316")
    axes[0, 0].set_title("Thalamus boundary self")
    axes[0, 0].set_ylabel("Score")

    axes[1, 0].plot(thal["capacity"], thal["proxy_identity_marker_persistence"], "o-", label="proxy", color="#2563EB")
    axes[1, 0].plot(thal["capacity"], thal["test_delayed_identity_recognition"], "o-", label="independent", color="#F97316")
    axes[1, 0].set_title("Thalamus identity-temporal self")
    axes[1, 0].set_xlabel("Workspace capacity")
    axes[1, 0].set_ylabel("Score")

    axes[0, 1].plot(trans["capacity"], trans["proxy_boundary_self"], "o-", label="proxy", color="#2563EB")
    axes[0, 1].plot(trans["capacity"], trans["generic_boundary_probe"], "o-", label="generic independent", color="#F97316")
    axes[0, 1].plot(trans["capacity"], trans["hard_attention_boundary"], "o-", label="attention hard probe", color="#10B981")
    axes[0, 1].set_title("Transformer boundary self")

    axes[1, 1].plot(trans["capacity"], trans["workspace_occupancy"], "o-", label="occupancy", color="#64748B")
    axes[1, 1].plot(trans["capacity"], trans["workspace_coherence"], "o-", label="coherence", color="#A855F7")
    axes[1, 1].plot(trans["capacity"], trans["workspace_lesion_score"], "o-", label="lesion sensitivity", color="#EF4444")
    axes[1, 1].set_title("Transformer workspace diagnostics")
    axes[1, 1].set_xlabel("Workspace capacity")

    for ax in axes.ravel():
        ax.set_ylim(-0.03, 1.05)
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False, fontsize=9)

    thal_boundary_r = float(thal_stats.loc["boundary_proxy_vs_independent", "pearson_r"])
    thal_identity_r = float(thal_stats.loc["identity_proxy_vs_independent", "pearson_r"])
    trans_boundary_r = float(trans_stats.loc["proxy_vs_generic_boundary", "pearson_r"])
    fig.text(
        0.5,
        0.01,
        f"Raw-level convergence: thalamus boundary r={thal_boundary_r:.3f}; "
        f"thalamus identity-temporal r={thal_identity_r:.3f}; "
        f"Transformer boundary proxy-generic r={trans_boundary_r:.3f}.",
        ha="center",
        fontsize=9,
    )
    fig.suptitle("Supplementary Figure S2. Workspace capacity sweeps", fontsize=15, fontweight="bold")
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    out_path = FIG_DIR / "figureS2_workspace_capacity_sweeps.png"
    fig.savefig(out_path, dpi=220)
    plt.close(fig)
    return out_path


def main() -> None:
    ensure_dir(FIG_DIR)
    paths = [figure_s1(), figure_s2()]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
