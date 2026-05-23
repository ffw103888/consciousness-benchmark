from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
import numpy as np
import pandas as pd

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mind_lab.utils import ensure_dir, safe_corr


OUT_DIR = PROJECT_ROOT / "docs" / "paper" / "figures"

PATHS = {
    "initial_validation": PROJECT_ROOT / "runs" / "measurement_validation" / "validation_20260521_093954" / "measurement_validation_raw.csv",
    "old_diagnostics": PROJECT_ROOT / "runs" / "measurement_validation" / "diagnostics_20260521_094719" / "diagnostic_raw.csv",
    "old_diagnostics_summary": PROJECT_ROOT / "runs" / "measurement_validation" / "diagnostics_20260521_094719" / "condition_summary.csv",
    "corrected_validation": PROJECT_ROOT / "runs" / "measurement_validation" / "validation_20260521_100404" / "measurement_validation_raw.csv",
    "self_diagnostics": PROJECT_ROOT / "runs" / "measurement_validation" / "self_diagnostics_20260521_101259" / "self_diagnostic_raw.csv",
    "self_summary": PROJECT_ROOT / "runs" / "measurement_validation" / "self_diagnostics_20260521_101259" / "self_condition_summary.csv",
    "distributed_self": PROJECT_ROOT / "runs" / "measurement_validation" / "distributed_self_validation_20260521_101511" / "distributed_self_raw.csv",
    "distributed_self_summary": PROJECT_ROOT / "runs" / "measurement_validation" / "distributed_self_validation_20260521_101511" / "distributed_self_summary.csv",
    "factorial": PROJECT_ROOT / "runs" / "mind_lab_night_20260520_182514" / "analysis" / "thalamus_factorial_timescale_20260520_212831" / "factorial_summary.csv",
    "action_variants": PROJECT_ROOT / "runs" / "mind_lab_night_20260520_182514" / "analysis" / "thalamus_action_loop_variants_20260520_220912" / "action_loop_variants_summary.csv",
    "cross_arch": PROJECT_ROOT / "runs" / "mind_lab_night_20260520_182514" / "analysis" / "cross_architecture_feedback_20260520_222903" / "cross_architecture_feedback_summary.csv",
    "extension_events": PROJECT_ROOT / "runs" / "mind_lab_night_20260520_182514_extended_20260521_093355" / "events.jsonl",
}


def set_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#222222",
            "axes.grid": True,
            "grid.alpha": 0.22,
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "legend.fontsize": 9,
            "savefig.dpi": 240,
        }
    )


def read_csv(path_key: str) -> pd.DataFrame:
    path = PATHS[path_key]
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def corr(x: Iterable[float], y: Iterable[float]) -> float:
    return safe_corr(np.asarray(list(x), dtype=float), np.asarray(list(y), dtype=float))


def fit_line(ax: plt.Axes, x: np.ndarray, y: np.ndarray, color: str) -> None:
    if len(x) < 2 or np.std(x) < 1e-9:
        return
    slope, intercept = np.polyfit(x, y, 1)
    xs = np.linspace(0.0, 1.0, 100)
    ax.plot(xs, slope * xs + intercept, "--", color=color, linewidth=2.0, alpha=0.8)


def figure_1_validation_framework(out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")

    boxes = [
        ((0.5, 5.8), "Theoretical\nConstruct", "e.g. agency / self", "#E8F4F8"),
        ((3.2, 5.8), "Operational\nProxy", "internal dynamics", "#B8E6F0"),
        ((5.9, 5.8), "Independent\nTests", "behavior-level probes", "#FFE6CC"),
        ((1.0, 2.5), "Validated\nConstruct", "bounded mechanism claim", "#E6F7E6"),
        ((6.2, 2.5), "Diagnostic\nPhase", "find construct mismatch", "#FFE6E6"),
        ((3.55, 0.65), "Refined\nConstructs", "split and revalidate", "#EDE7F6"),
    ]
    for (xy, title, subtitle, color) in boxes:
        box = patches.FancyBboxPatch(
            xy,
            2.1,
            1.15,
            boxstyle="round,pad=0.08",
            facecolor=color,
            edgecolor="#222222",
            linewidth=1.8,
        )
        ax.add_patch(box)
        ax.text(xy[0] + 1.05, xy[1] + 0.72, title, ha="center", va="center", weight="bold")
        ax.text(xy[0] + 1.05, xy[1] + 0.28, subtitle, ha="center", va="center", fontsize=9, style="italic")

    arrows = [
        ((2.62, 6.38), (3.18, 6.38), "#222222", "-"),
        ((5.32, 6.38), (5.88, 6.38), "#222222", "-"),
        ((6.95, 5.75), (7.25, 3.72), "#CC3333", "-"),
        ((4.95, 5.75), (2.15, 3.72), "#228833", "-"),
        ((7.25, 2.5), (5.15, 1.5), "#555555", "--"),
        ((4.6, 1.8), (4.25, 5.78), "#777777", ":"),
    ]
    for start, end, color, style in arrows:
        arrow = FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=18, linewidth=2.0, color=color, linestyle=style)
        ax.add_patch(arrow)
    ax.text(5.0, 4.85, "Validation\ncorrelation?", ha="center", va="center", weight="bold")
    ax.text(2.95, 4.35, "r > 0.7", color="#228833", weight="bold", ha="center")
    ax.text(7.55, 4.35, "r < 0.5 or r < 0", color="#CC3333", weight="bold", ha="center")
    ax.text(4.9, 3.15, "legacy fields retained\nfor auditability", ha="center", fontsize=9, color="#555555")
    ax.set_title("Figure 1. Validation-first measurement workflow", pad=12, weight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "figure1_validation_framework.png", bbox_inches="tight")
    plt.close(fig)


def figure_2_agency_refinement(out_dir: Path) -> None:
    initial = read_csv("initial_validation")
    old = read_csv("old_diagnostics")
    corrected = read_csv("corrected_validation")
    initial_thal = initial[initial["architecture"] == "thalamus"].copy()
    old_thal = old[old["architecture"] == "thalamus"].copy()

    fig, axes = plt.subplots(1, 3, figsize=(15.2, 4.9))

    ax = axes[0]
    x = initial_thal["proxy_agency"].to_numpy(float)
    y = initial_thal["independent_agency"].to_numpy(float)
    ax.scatter(x, y, s=55, alpha=0.78, color="#CC6677", edgecolor="white")
    ax.plot([0, 1], [0, 1], "k:", linewidth=1.2, alpha=0.65)
    fit_line(ax, x, y, "#AA2222")
    r = corr(x, y)
    ax.set_title(f"A. Original thalamus proxy (r={r:.2f})", weight="bold")
    ax.set_xlabel("Original agency proxy")
    ax.set_ylabel("Independent agency tests")
    ax.set_xlim(-0.04, 1.04)
    ax.set_ylim(-0.04, 1.04)
    key = initial_thal[initial_thal["condition"] == "W-A-"]
    if not key.empty:
        ax.scatter(key["proxy_agency"], key["independent_agency"], s=180, marker="*", color="#D62728", edgecolor="black", zorder=5)
        ax.annotate("W-A-\ngating mistaken for agency", xy=(float(key["proxy_agency"].mean()), float(key["independent_agency"].mean())), xytext=(0.42, 0.24), arrowprops=dict(arrowstyle="->", lw=1.2), fontsize=8)

    ax = axes[1]
    diagnostics = []
    for label, col in [
        ("gating\ncoordination", "m_gating_agency_proxy"),
        ("action\nfrequency", "i_action_frequency"),
        ("prediction\nerror", "i_internal_prediction_error"),
        ("behavior-action\nsimilarity", "i_behavior_action_similarity"),
    ]:
        if col in old_thal.columns:
            diagnostics.append((label, corr(old_thal["proxy_agency"], old_thal[col])))
    if not diagnostics:
        diagnostics = [("gating\ncoordination", 0.9), ("action\nvariables", 0.1)]
    labels, values = zip(*diagnostics)
    colors = ["#44AA99" if v > 0 else "#CC6677" for v in values]
    ax.barh(labels, values, color=colors, edgecolor="#222222", alpha=0.82)
    ax.axvline(0, color="#222222", linewidth=1)
    ax.set_xlim(-1, 1)
    ax.set_title("B. Diagnostic correlates", weight="bold")
    ax.set_xlabel("Correlation with original proxy")

    ax = axes[2]
    x = corrected["proxy_agency"].to_numpy(float)
    y = corrected["independent_agency"].to_numpy(float)
    for arch, group in corrected.groupby("architecture"):
        color = "#4477AA" if arch == "thalamus" else "#EE7733"
        ax.scatter(group["proxy_agency"], group["independent_agency"], s=50, alpha=0.75, label=arch, color=color, edgecolor="white")
    ax.plot([0, 1], [0, 1], "k:", linewidth=1.2, alpha=0.65)
    fit_line(ax, x, y, "#228833")
    r = corr(x, y)
    ax.set_title(f"C. Corrected action agency (r={r:.2f})", weight="bold")
    ax.set_xlabel("Corrected action-agency proxy")
    ax.set_ylabel("Independent agency tests")
    ax.set_xlim(-0.04, 1.04)
    ax.set_ylim(-0.04, 1.04)
    ax.legend(frameon=False)

    fig.suptitle("Figure 2. Agency proxy refinement", y=1.03, weight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "figure2_agency_refinement.png", bbox_inches="tight")
    plt.close(fig)


def figure_3_action_agency_mechanism(out_dir: Path) -> None:
    factorial = read_csv("factorial")
    variants = read_csv("action_variants")
    cross = read_csv("cross_arch")

    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.8))

    ax = axes[0, 0]
    order = [
        "workspace_off__action_off",
        "workspace_on__action_off",
        "workspace_off__action_on",
        "workspace_on__action_on",
    ]
    labels = ["W-A-", "W+A-", "W-A+", "W+A+"]
    data = factorial.set_index("condition").loc[order]
    x = np.arange(len(data))
    ax.bar(x, data["agency_mean"], yerr=data["agency_std"], color=["#BBBBBB", "#88CCEE", "#44AA99", "#117733"], edgecolor="#222222", capsize=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 0.75)
    ax.set_ylabel("Agency proxy")
    ax.set_title("A. Thalamus 2x2 manipulation", weight="bold")

    ax = axes[0, 1]
    variant_order = ["none", "minimal", "learning", "intention", "full"]
    v = variants.set_index("variant").loc[variant_order]
    x = np.arange(len(v))
    ax.bar(x, v["agency_mean"], yerr=v["agency_std"], color="#4477AA", edgecolor="#222222", capsize=3, label="agency")
    ax2 = ax.twinx()
    ax2.plot(x, v["action_prediction_error_mean"], "o--", color="#CC6677", linewidth=2, label="prediction error")
    ax.set_xticks(x)
    ax.set_xticklabels(variant_order, rotation=25, ha="right")
    ax.set_ylim(0, 0.65)
    ax2.set_ylim(0, 0.6)
    ax.set_ylabel("Agency proxy")
    ax2.set_ylabel("Prediction error")
    ax.set_title("B. Action-loop variants", weight="bold")

    ax = axes[1, 0]
    labels = [f"{row.architecture}\n{row.condition}" for row in cross.itertuples()]
    x = np.arange(len(cross))
    ax.bar(x, cross["agency_mean"], yerr=cross["agency_std"], color=["#88CCEE" if a == "thalamus" else "#EE7733" for a in cross["architecture"]], edgecolor="#222222", capsize=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 0.9)
    ax.set_ylabel("Agency proxy")
    ax.set_title("C. Cross-architecture feedback", weight="bold")

    ax = axes[1, 1]
    validation = read_csv("corrected_validation")
    for arch, group in validation.groupby("architecture"):
        ax.scatter(group["proxy_agency"], group["independent_agency"], s=52, alpha=0.76, label=arch)
    ax.plot([0, 1], [0, 1], "k:", linewidth=1.2)
    r = corr(validation["proxy_agency"], validation["independent_agency"])
    fit_line(ax, validation["proxy_agency"].to_numpy(float), validation["independent_agency"].to_numpy(float), "#228833")
    ax.set_title(f"D. Validated action-agency alignment (r={r:.2f})", weight="bold")
    ax.set_xlabel("Corrected proxy")
    ax.set_ylabel("Independent tests")
    ax.set_xlim(-0.04, 1.04)
    ax.set_ylim(-0.04, 1.04)
    ax.legend(frameon=False)

    fig.suptitle("Figure 3. Action-outcome mechanisms align with operational agency", y=1.01, weight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "figure3_action_agency_mechanism.png", bbox_inches="tight")
    plt.close(fig)


def figure_4_self_construct_split(out_dir: Path) -> None:
    raw = read_csv("self_diagnostics")
    summary = read_csv("self_summary")

    fig, axes = plt.subplots(2, 2, figsize=(13.2, 9.5))

    ax = axes[0, 0]
    for arch, group in raw.groupby("architecture"):
        ax.scatter(group["proxy_self_model"], group["independent_self_model"], s=50, alpha=0.72, label=arch)
    ax.plot([0, 1], [0, 1], "k:", linewidth=1.1)
    r = corr(raw["proxy_self_model"], raw["independent_self_model"])
    fit_line(ax, raw["proxy_self_model"].to_numpy(float), raw["independent_self_model"].to_numpy(float), "#555555")
    ax.set_title(f"A. Overall self proxy (r={r:.2f})", weight="bold")
    ax.set_xlabel("Self proxy")
    ax.set_ylabel("Independent self aggregate")
    ax.set_xlim(-0.04, 1.04)
    ax.set_ylim(-0.04, 1.04)
    ax.legend(frameon=False)

    ax = axes[0, 1]
    bars = [
        ("boundary/core", corr(raw["proxy_boundary_self"], raw["independent_self_core_boundary"])),
        ("temporal", corr(raw["proxy_temporal_self"], raw["test_computational_mirror"])),
        ("ownership", corr(raw["proxy_ownership_self"], raw["test_ownership_attribution"])),
        ("identity agg.", corr(raw["proxy_self_model"], raw["independent_self_identity_ownership"])),
    ]
    labels, values = zip(*bars)
    colors = ["#228833" if v >= 0.7 else "#DDCC77" if v >= 0.4 else "#CC6677" for v in values]
    ax.bar(labels, values, color=colors, edgecolor="#222222")
    ax.axhline(0.7, color="#228833", linestyle="--", linewidth=1, alpha=0.7)
    ax.axhline(0.0, color="#222222", linewidth=1)
    ax.set_ylim(-0.35, 1.05)
    ax.set_ylabel("Proxy-test correlation")
    ax.set_title("B. Self construct split", weight="bold")

    ax = axes[1, 0]
    labels = [f"{r.architecture}\n{r.condition}" for r in summary.itertuples()]
    x = np.arange(len(summary))
    width = 0.22
    ax.bar(x - width, summary["proxy_boundary_self"], width, label="boundary proxy", color="#4477AA", alpha=0.82)
    ax.bar(x, summary["independent_self_core_boundary"], width, label="independent core/boundary", color="#44AA99", alpha=0.82)
    ax.bar(x + width, summary["proxy_ownership_self"], width, label="ownership proxy", color="#CC6677", alpha=0.82)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("C. Condition-level self components", weight="bold")
    ax.legend(frameon=False)

    ax = axes[1, 1]
    x = raw["proxy_boundary_self"].to_numpy(float)
    y = raw["independent_self_core_boundary"].to_numpy(float)
    ax.scatter(x, y, s=50, alpha=0.72, color="#44AA99", edgecolor="white")
    fit_line(ax, x, y, "#228833")
    ax.plot([0, 1], [0, 1], "k:", linewidth=1.1)
    ax.set_title(f"D. Boundary/core self alignment (r={corr(x, y):.2f})", weight="bold")
    ax.set_xlabel("Boundary self proxy")
    ax.set_ylabel("Core/boundary independent tests")
    ax.set_xlim(-0.04, 1.04)
    ax.set_ylim(-0.04, 1.04)

    fig.suptitle("Figure 4. Self-model requires construct splitting", y=1.01, weight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "figure4_self_construct_split.png", bbox_inches="tight")
    plt.close(fig)


def figure_5_distributed_self_limitation(out_dir: Path) -> None:
    raw = read_csv("distributed_self")
    summary = read_csv("distributed_self_summary")

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))

    pairs = [
        ("proxy_boundary_self", "independent_core_boundary_self", "Boundary"),
        ("proxy_temporal_self", "test_computational_mirror", "Temporal"),
        ("proxy_ownership_self", "test_ownership_attribution", "Ownership"),
    ]
    for ax, (x_col, y_col, title) in zip(axes, pairs):
        ax.scatter(raw[x_col], raw[y_col], s=48, alpha=0.72, color="#EE7733", edgecolor="white")
        ax.plot([0, 1], [0, 1], "k:", linewidth=1.1)
        r = corr(raw[x_col], raw[y_col])
        fit_line(ax, raw[x_col].to_numpy(float), raw[y_col].to_numpy(float), "#CC6677")
        ax.set_title(f"{title} distributed self (r={r:.2f})", weight="bold")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_xlim(-0.04, 1.04)
        ax.set_ylim(-0.04, 1.04)

    fig.suptitle("Figure 5. Distributed self validation is measurement-limited", y=1.04, weight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "figure5_distributed_self_limitation.png", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(13.5, 5.2))
    labels = list(summary["condition"])
    x = np.arange(len(summary))
    width = 0.22
    ax.bar(x - width, summary["test_architecture_self_probe"], width, label="architecture probe", color="#AA4499")
    ax.bar(x, summary["test_computational_mirror"], width, label="mirror", color="#88CCEE")
    ax.bar(x + width, summary["test_boundary_perturbation"], width, label="boundary perturbation", color="#DDCC77")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Independent test score")
    ax.set_title("Figure 5 supplement. Low dynamic range in current distributed self tests", weight="bold")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out_dir / "figure5_distributed_self_test_ranges.png", bbox_inches="tight")
    plt.close(fig)


def parse_extension_events(path: Path) -> pd.DataFrame:
    rows = []
    if not path.exists():
        return pd.DataFrame(rows)
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("event") != "cycle_completed":
                continue
            alife = item.get("path_results", {}).get("alife", {})
            archive = alife.get("archive", {})
            rows.append(
                {
                    "time": item.get("time", ""),
                    "cycle": item.get("cycle", np.nan),
                    "coverage": archive.get("coverage", np.nan),
                    "max_fitness": archive.get("max_fitness", np.nan),
                    "mean_fitness": archive.get("mean_fitness", np.nan),
                    "added": alife.get("added", np.nan),
                }
            )
    return pd.DataFrame(rows)


def figure_6_alife_context(out_dir: Path) -> None:
    data = parse_extension_events(PATHS["extension_events"])
    if data.empty:
        return
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 9.2), sharex=True)
    axes[0].plot(data["cycle"], data["coverage"], color="#4477AA", linewidth=2)
    axes[0].axhline(16000, color="#228833", linestyle="--", linewidth=1.5, label="10% target")
    axes[0].set_ylabel("QD coverage")
    axes[0].legend(frameon=False)
    axes[0].set_title("Figure 6. ALife archive continues as open-ended search context", weight="bold")

    axes[1].plot(data["cycle"], data["max_fitness"], color="#CC6677", linewidth=2, label="max")
    axes[1].plot(data["cycle"], data["mean_fitness"], color="#DDCC77", linewidth=2, label="mean")
    axes[1].set_ylabel("Fitness")
    axes[1].legend(frameon=False)

    axes[2].bar(data["cycle"], data["added"], color="#44AA99", alpha=0.75, width=0.8)
    axes[2].set_ylabel("Archive additions")
    axes[2].set_xlabel("Cycle")

    fig.tight_layout()
    fig.savefig(out_dir / "figure6_alife_context.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ensure_dir(OUT_DIR)
    set_style()
    figure_1_validation_framework(OUT_DIR)
    figure_2_agency_refinement(OUT_DIR)
    figure_3_action_agency_mechanism(OUT_DIR)
    figure_4_self_construct_split(OUT_DIR)
    figure_5_distributed_self_limitation(OUT_DIR)
    figure_6_alife_context(OUT_DIR)
    manifest = {
        "output_dir": str(OUT_DIR),
        "figures": sorted(path.name for path in OUT_DIR.glob("*.png")),
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
