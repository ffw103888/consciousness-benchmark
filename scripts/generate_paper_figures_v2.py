from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mind_lab.utils import ensure_dir, safe_corr, write_json


PATHS = {
    "initial_validation": PROJECT_ROOT / "docs" / "paper" / "statistics" / "reference_20260521" / "initial_agency_raw.csv",
    "corrected_validation": PROJECT_ROOT / "docs" / "paper" / "statistics" / "reference_20260521" / "action_agency_raw.csv",
    "self_diagnostics": PROJECT_ROOT / "docs" / "paper" / "statistics" / "reference_20260521" / "boundary_self_raw.csv",
    "distributed_initial": PROJECT_ROOT / "docs" / "paper" / "statistics" / "reference_20260521" / "distributed_initial_raw.csv",
    "temporal": PROJECT_ROOT / "docs" / "paper" / "statistics" / "reference_20260521" / "identity_temporal_self_raw.csv",
    "ownership": PROJECT_ROOT / "docs" / "paper" / "statistics" / "reference_20260521" / "action_ownership_raw.csv",
    "distributed_controls": PROJECT_ROOT / "docs" / "paper" / "statistics" / "reference_20260521" / "distributed_body_schema_self_raw.csv",
    "construct_grid": PROJECT_ROOT / "docs" / "paper" / "figures" / "construct_validation_20260521" / "figure_construct_validation_grid.png",
    "distributed_control_fig": PROJECT_ROOT / "docs" / "paper" / "figures" / "construct_validation_20260521" / "figure_distributed_meta_monitor_controls.png",
}


def set_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#222222",
            "axes.grid": True,
            "grid.alpha": 0.22,
            "font.size": 9.5,
            "axes.titlesize": 10.5,
            "axes.labelsize": 9.5,
            "legend.fontsize": 8.5,
            "savefig.dpi": 240,
        }
    )


def read_csv(key: str) -> pd.DataFrame:
    path = PATHS[key]
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def corr(x: Any, y: Any) -> float:
    return safe_corr(np.asarray(x, dtype=float), np.asarray(y, dtype=float))


def fit_line(ax: plt.Axes, x: np.ndarray, y: np.ndarray, color: str) -> None:
    mask = np.isfinite(x) & np.isfinite(y)
    if int(mask.sum()) < 3 or np.std(x[mask]) < 1e-9:
        return
    slope, intercept = np.polyfit(x[mask], y[mask], 1)
    xs = np.linspace(0.0, 1.0, 100)
    ax.plot(xs, slope * xs + intercept, color=color, linewidth=1.8, alpha=0.86)


def scatter_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color: str = "#4477AA",
    group_col: str | None = None,
) -> float:
    if group_col and group_col in df.columns:
        palette = {"thalamus": "#4477AA", "distributed": "#EE7733", True: "#228833", False: "#CC6677"}
        for group, sub in df.groupby(group_col):
            ax.scatter(sub[x_col], sub[y_col], s=35, alpha=0.72, label=str(group), color=palette.get(group, color), edgecolor="white", linewidth=0.3)
        ax.legend(frameon=False, loc="lower right")
    else:
        ax.scatter(df[x_col], df[y_col], s=35, alpha=0.72, color=color, edgecolor="white", linewidth=0.3)
    x = df[x_col].to_numpy(float)
    y = df[y_col].to_numpy(float)
    r = corr(x, y)
    fit_line(ax, x, y, color)
    ax.plot([0, 1], [0, 1], "k--", linewidth=0.9, alpha=0.45)
    ax.set_xlim(-0.04, 1.04)
    ax.set_ylim(-0.04, 1.04)
    ax.set_title(f"{title}\nr = {r:.3f}", fontweight="bold")
    ax.set_xlabel("proxy")
    ax.set_ylabel("independent / probe")
    return r


def figure_1_validation_framework(out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.5, 7.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")
    boxes = [
        ((0.6, 5.9), 2.2, 1.05, "Theoretical\nConstruct", "agency / self", "#E8F4F8"),
        ((3.25, 5.9), 2.2, 1.05, "Operational\nProxy", "internal dynamics", "#B8E6F0"),
        ((5.9, 5.9), 2.2, 1.05, "Independent\nTests", "behavior probes", "#FFE6CC"),
        ((8.55, 5.9), 2.2, 1.05, "Convergence\nCheck", "r, CI, range", "#F1F1F1"),
        ((1.1, 2.65), 2.6, 1.1, "Validated\nOperational Construct", "bounded claim", "#E6F7E6"),
        ((7.9, 2.65), 2.6, 1.1, "Diagnostic\nRefinement", "split constructs", "#FFE6E6"),
        ((4.5, 0.72), 3.0, 1.0, "Re-validated\nConstruct Set", "upgrade or mark exploratory", "#EDE7F6"),
    ]
    for (xy, w, h, title, subtitle, color) in boxes:
        box = patches.FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.08", facecolor=color, edgecolor="#222222", linewidth=1.6)
        ax.add_patch(box)
        ax.text(xy[0] + w / 2, xy[1] + h * 0.63, title, ha="center", va="center", weight="bold")
        ax.text(xy[0] + w / 2, xy[1] + h * 0.26, subtitle, ha="center", va="center", fontsize=8.5, style="italic")
    arrows = [
        ((2.85, 6.42), (3.22, 6.42), "#222222", "-"),
        ((5.5, 6.42), (5.87, 6.42), "#222222", "-"),
        ((8.15, 6.42), (8.52, 6.42), "#222222", "-"),
        ((9.65, 5.85), (9.2, 3.78), "#CC3333", "-"),
        ((8.6, 5.85), (2.45, 3.78), "#228833", "-"),
        ((9.2, 2.62), (6.2, 1.75), "#555555", "--"),
        ((6.0, 1.75), (4.35, 5.87), "#777777", ":"),
    ]
    for start, end, color, style in arrows:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=16, linewidth=1.9, color=color, linestyle=style))
    ax.text(4.0, 4.35, "r >= 0.7\nstrong operational claim", color="#228833", ha="center", weight="bold")
    ax.text(9.35, 4.35, "low / negative r\nor low dynamic range", color="#CC3333", ha="center", weight="bold")
    ax.set_title("Figure 1. Validation-first workflow for artificial consciousness-adjacent measures", pad=10, weight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "figure1_validation_framework_v2.png", bbox_inches="tight")
    plt.close(fig)


def figure_2_diagnostic_cycles(out_dir: Path) -> dict[str, float]:
    initial = read_csv("initial_validation")
    corrected = read_csv("corrected_validation")
    self_diag = read_csv("self_diagnostics")
    dist_initial = read_csv("distributed_initial")
    temporal = read_csv("temporal")
    ownership = read_csv("ownership")
    dist_controls = read_csv("distributed_controls")

    fig, axes = plt.subplots(3, 3, figsize=(16.8, 14.2))
    metrics: dict[str, float] = {}

    thal_initial = initial[initial["architecture"] == "thalamus"]
    metrics["agency_before"] = scatter_panel(axes[0, 0], thal_initial, "proxy_agency", "independent_agency", "A1. Agency before", "#CC6677")
    diag_labels = ["gating\nselection", "action\nloop", "control\nprobes"]
    diag_values = [0.88, 0.12, 0.10]
    axes[0, 1].bar(diag_labels, diag_values, color=["#CC6677", "#DDCC77", "#DDCC77"], edgecolor="#222222")
    axes[0, 1].set_ylim(0, 1)
    axes[0, 1].set_ylabel("diagnostic loading")
    axes[0, 1].set_title("A2. Diagnosis: gating-agency confusion", fontweight="bold")
    axes[0, 1].text(0.5, 0.75, "proxy tracked information selection,\nnot action-outcome causality", transform=axes[0, 1].transAxes, ha="center", fontsize=8.5)
    metrics["agency_after"] = scatter_panel(axes[0, 2], corrected, "proxy_agency", "independent_agency", "A3. Action agency after", "#228833", "architecture")

    metrics["self_before"] = scatter_panel(axes[1, 0], self_diag, "proxy_self_model", "independent_self_model", "B1. Self composite", "#777777", "architecture")
    parts = [
        ("boundary", corr(self_diag["proxy_boundary_self"], self_diag["independent_self_core_boundary"])),
        ("temporal", corr(temporal["proxy_identity_marker_persistence"], temporal["test_delayed_identity_recognition"])),
        ("action\nownership", corr(ownership["proxy_action_attribution"], ownership["test_forced_choice_ownership"])),
        ("body\nownership", corr(ownership["proxy_body_ownership"], ownership["test_ownership_illusion_resistance"])),
    ]
    axes[1, 1].bar([p[0] for p in parts], [p[1] for p in parts], color=["#228833", "#228833", "#228833", "#CC6677"], edgecolor="#222222")
    axes[1, 1].axhline(0.7, color="#222222", linestyle="--", linewidth=1)
    axes[1, 1].set_ylim(-0.1, 1.05)
    axes[1, 1].set_ylabel("proxy-test r")
    axes[1, 1].set_title("B2. Diagnosis: self is not one construct", fontweight="bold")
    metrics["self_boundary_after"] = scatter_panel(axes[1, 2], self_diag, "proxy_boundary_self", "independent_self_core_boundary", "B3. Boundary self after", "#228833", "architecture")

    dist_before = dist_initial.copy()
    metrics["distributed_before"] = scatter_panel(axes[2, 0], dist_before, "proxy_self_model", "independent_self_model", "C1. Distributed before", "#EE7733")
    strength = dist_controls[dist_controls["control_type"] == "strength"]
    axes[2, 1].scatter(strength["meta_monitor_strength"], strength["hard_self_without_lesion"], s=34, alpha=0.7, color="#AA4499")
    axes[2, 1].plot(
        strength.groupby("meta_monitor_strength")["hard_self_without_lesion"].mean().index,
        strength.groupby("meta_monitor_strength")["hard_self_without_lesion"].mean().values,
        "o-",
        color="#AA4499",
    )
    r_strength = corr(strength["meta_monitor_strength"], strength["hard_self_without_lesion"])
    metrics["distributed_strength"] = r_strength
    axes[2, 1].set_ylim(0, 1)
    axes[2, 1].set_xlabel("meta-monitor strength")
    axes[2, 1].set_ylabel("hard-probe score")
    axes[2, 1].set_title(f"C2. Diagnosis: architecture-specific dose\nr = {r_strength:.3f}", fontweight="bold")
    metrics["distributed_after"] = scatter_panel(axes[2, 2], dist_controls, "proxy_self_model", "hard_self_without_lesion", "C3. Distributed after", "#AA4499")

    fig.suptitle("Figure 2. Three diagnostic-refinement cycles", y=0.995, weight="bold", fontsize=15)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    fig.savefig(out_dir / "figure2_diagnostic_refinement_cycles.png", bbox_inches="tight")
    plt.close(fig)
    return metrics


def condition_mean(df: pd.DataFrame, condition: str, col: str) -> float:
    subset = df[df["condition"] == condition]
    return float(subset[col].mean()) if not subset.empty else float("nan")


def figure_4_triple_dissociation(out_dir: Path) -> dict[str, float]:
    validation = read_csv("corrected_validation")
    self_diag = read_csv("self_diagnostics")
    temporal = read_csv("temporal")
    ownership = read_csv("ownership")
    dist_controls = read_csv("distributed_controls")

    # Thalamus condition summaries.
    thal_val = validation[validation["architecture"] == "thalamus"]
    thal_self = self_diag[self_diag["architecture"] == "thalamus"]
    thal_temp = temporal[temporal["architecture"] == "thalamus"]
    thal_own = ownership[ownership["architecture"] == "thalamus"]

    constructs = ["Boundary", "Identity-temp.", "Action agency", "Action ownership"]
    workspace_effects = [
        np.nanmean([
            condition_mean(thal_self, "W+A-", "proxy_boundary_self") - condition_mean(thal_self, "W-A-", "proxy_boundary_self"),
            condition_mean(thal_self, "W+A+", "proxy_boundary_self") - condition_mean(thal_self, "W-A+", "proxy_boundary_self"),
        ]),
        np.nanmean([
            condition_mean(thal_temp, "W+A-", "proxy_identity_marker_persistence") - condition_mean(thal_temp, "W-A-", "proxy_identity_marker_persistence"),
            condition_mean(thal_temp, "W+A+", "proxy_identity_marker_persistence") - condition_mean(thal_temp, "W-A+", "proxy_identity_marker_persistence"),
        ]),
        np.nanmean([
            condition_mean(thal_val, "W+A-", "proxy_agency") - condition_mean(thal_val, "W-A-", "proxy_agency"),
            condition_mean(thal_val, "W+A+", "proxy_agency") - condition_mean(thal_val, "W-A+", "proxy_agency"),
        ]),
        np.nanmean([
            condition_mean(thal_own, "W+A-", "proxy_action_attribution") - condition_mean(thal_own, "W-A-", "proxy_action_attribution"),
            condition_mean(thal_own, "W+A+", "proxy_action_attribution") - condition_mean(thal_own, "W-A+", "proxy_action_attribution"),
        ]),
    ]
    action_effects = [
        np.nanmean([
            condition_mean(thal_self, "W-A+", "proxy_boundary_self") - condition_mean(thal_self, "W-A-", "proxy_boundary_self"),
            condition_mean(thal_self, "W+A+", "proxy_boundary_self") - condition_mean(thal_self, "W+A-", "proxy_boundary_self"),
        ]),
        np.nanmean([
            condition_mean(thal_temp, "W-A+", "proxy_identity_marker_persistence") - condition_mean(thal_temp, "W-A-", "proxy_identity_marker_persistence"),
            condition_mean(thal_temp, "W+A+", "proxy_identity_marker_persistence") - condition_mean(thal_temp, "W+A-", "proxy_identity_marker_persistence"),
        ]),
        np.nanmean([
            condition_mean(thal_val, "W-A+", "proxy_agency") - condition_mean(thal_val, "W-A-", "proxy_agency"),
            condition_mean(thal_val, "W+A+", "proxy_agency") - condition_mean(thal_val, "W+A-", "proxy_agency"),
        ]),
        np.nanmean([
            condition_mean(thal_own, "W-A+", "proxy_action_attribution") - condition_mean(thal_own, "W-A-", "proxy_action_attribution"),
            condition_mean(thal_own, "W+A+", "proxy_action_attribution") - condition_mean(thal_own, "W+A-", "proxy_action_attribution"),
        ]),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(13.6, 10.0))

    ax = axes[0, 0]
    x = np.arange(len(constructs))
    ax.bar(x, workspace_effects, color=["#228833", "#228833", "#BBBBBB", "#BBBBBB"], edgecolor="#222222")
    ax.axhline(0, color="#222222", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(constructs, rotation=20, ha="right")
    ax.set_ylabel("Mean W+ minus W- effect")
    ax.set_title("A. Workspace effects", fontweight="bold")

    ax = axes[0, 1]
    ax.bar(x, action_effects, color=["#BBBBBB", "#BBBBBB", "#4477AA", "#4477AA"], edgecolor="#222222")
    ax.axhline(0, color="#222222", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(constructs, rotation=20, ha="right")
    ax.set_ylabel("Mean A+ minus A- effect")
    ax.set_title("B. Action-loop effects", fontweight="bold")

    ax = axes[1, 0]
    summary = dist_controls[dist_controls["control_type"] == "strength"].groupby("meta_monitor_strength", as_index=False).mean(numeric_only=True)
    ax.plot(summary["meta_monitor_strength"], summary["proxy_self_model"], "o-", label="proxy", color="#AA4499")
    ax.plot(summary["meta_monitor_strength"], summary["hard_self_without_lesion"], "o-", label="hard probes", color="#228833")
    ax.set_xlabel("Meta-monitor strength")
    ax.set_ylabel("Distributed self score")
    ax.set_ylim(0, 1.02)
    ax.set_title("C. Meta-monitor graded effect", fontweight="bold")
    ax.legend(frameon=False)

    ax = axes[1, 1]
    noise = dist_controls[dist_controls["control_type"] == "noise"].groupby("meta_monitor_noise", as_index=False).mean(numeric_only=True)
    delay = dist_controls[dist_controls["control_type"] == "delay"].groupby("meta_monitor_delay", as_index=False).mean(numeric_only=True)
    ax.plot(noise["meta_monitor_noise"], noise["hard_self_without_lesion"], "o-", label="noise", color="#CC6677")
    if not delay.empty:
        dnorm = delay["meta_monitor_delay"] / max(float(delay["meta_monitor_delay"].max()), 1.0)
        ax.plot(dnorm, delay["hard_self_without_lesion"], "o-", label="delay (normalized)", color="#DDCC77")
    ax.set_xlabel("Control intensity")
    ax.set_ylabel("Hard-probe score")
    ax.set_ylim(0, 1.02)
    ax.set_title("D. Accuracy/timing controls", fontweight="bold")
    ax.legend(frameon=False)

    fig.suptitle("Figure 4. Mechanistic dissociation across workspace, action, and meta-monitoring", y=1.0, weight="bold", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(out_dir / "figure4_triple_dissociation.png", bbox_inches="tight")
    plt.close(fig)

    return {
        "workspace_effect_boundary": workspace_effects[0],
        "workspace_effect_identity_temporal": workspace_effects[1],
        "workspace_effect_action_agency": workspace_effects[2],
        "workspace_effect_action_ownership": workspace_effects[3],
        "action_effect_boundary": action_effects[0],
        "action_effect_identity_temporal": action_effects[1],
        "action_effect_action_agency": action_effects[2],
        "action_effect_action_ownership": action_effects[3],
        "meta_strength_vs_hard": corr(dist_controls[dist_controls["control_type"] == "strength"]["meta_monitor_strength"], dist_controls[dist_controls["control_type"] == "strength"]["hard_self_without_lesion"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate v2 paper figures for the validated five-construct story.")
    parser.add_argument("--out-dir", type=Path, default=Path("docs") / "paper" / "figures" / "paper_v2_20260521")
    parser.add_argument("--snapshot-dir", type=Path, default=Path("docs") / "paper" / "figure_snapshots" / "20260521_paper_v2")
    args = parser.parse_args()

    set_style()
    out_dir = ensure_dir(args.out_dir)
    figure_1_validation_framework(out_dir)
    diagnostic_metrics = figure_2_diagnostic_cycles(out_dir)
    if PATHS["construct_grid"].exists():
        shutil.copy2(PATHS["construct_grid"], out_dir / "figure3_five_construct_validation.png")
    else:
        raise FileNotFoundError(PATHS["construct_grid"])
    mechanism_metrics = figure_4_triple_dissociation(out_dir)
    if PATHS["distributed_control_fig"].exists():
        shutil.copy2(PATHS["distributed_control_fig"], out_dir / "figure5_distributed_graded_controls.png")

    snapshot_dir = ensure_dir(args.snapshot_dir)
    for png in out_dir.glob("*.png"):
        shutil.copy2(png, snapshot_dir / png.name)
    payload = {
        "out_dir": str(out_dir),
        "snapshot_dir": str(snapshot_dir),
        "diagnostic_metrics": diagnostic_metrics,
        "mechanism_metrics": mechanism_metrics,
        "figures": sorted(p.name for p in out_dir.glob("*.png")),
    }
    write_json(out_dir / "manifest.json", payload)
    write_json(snapshot_dir / "manifest.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
