from __future__ import annotations

import argparse
import json
import sys
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


DEFAULT_PATHS = {
    "agency": Path("docs/paper/statistics/reference_20260521/action_agency_raw.csv"),
    "boundary": Path("docs/paper/statistics/reference_20260521/boundary_self_raw.csv"),
    "temporal": Path("docs/paper/statistics/reference_20260521/identity_temporal_self_raw.csv"),
    "ownership": Path("docs/paper/statistics/reference_20260521/action_ownership_raw.csv"),
    "distributed": Path("docs/paper/statistics/reference_20260521/distributed_body_schema_self_raw.csv"),
}


def load_constructs(paths: dict[str, Path]) -> dict[str, dict[str, Any]]:
    constructs: dict[str, dict[str, Any]] = {}

    agency = pd.read_csv(paths["agency"])
    constructs["Action agency"] = {
        "df": agency,
        "x": "proxy_agency",
        "y": "independent_agency",
        "status": "validated",
        "mechanism": "action-outcome loop",
    }

    boundary = pd.read_csv(paths["boundary"])
    constructs["Boundary self"] = {
        "df": boundary,
        "x": "proxy_boundary_self",
        "y": "independent_self_core_boundary",
        "status": "validated",
        "mechanism": "workspace",
    }

    temporal = pd.read_csv(paths["temporal"])
    constructs["Identity-temporal self"] = {
        "df": temporal,
        "x": "proxy_identity_marker_persistence",
        "y": "test_delayed_identity_recognition",
        "status": "validated subconstruct",
        "mechanism": "workspace",
    }

    ownership = pd.read_csv(paths["ownership"])
    constructs["Action ownership"] = {
        "df": ownership,
        "x": "proxy_action_attribution",
        "y": "test_forced_choice_ownership",
        "status": "validated subconstruct",
        "mechanism": "action-outcome loop",
    }

    distributed = pd.read_csv(paths["distributed"])
    constructs["Distributed body-schema self"] = {
        "df": distributed,
        "x": "proxy_self_model",
        "y": "hard_self_without_lesion",
        "status": "validated with graded controls",
        "mechanism": "meta-monitor",
    }
    return constructs


def fit_line(ax: plt.Axes, x: np.ndarray, y: np.ndarray, color: str) -> None:
    mask = np.isfinite(x) & np.isfinite(y)
    if int(mask.sum()) < 3 or np.std(x[mask]) < 1e-9:
        return
    slope, intercept = np.polyfit(x[mask], y[mask], 1)
    xs = np.linspace(max(0.0, float(np.min(x[mask]))), min(1.0, float(np.max(x[mask]))), 100)
    ax.plot(xs, slope * xs + intercept, color=color, linewidth=2, alpha=0.85)


def figure_construct_grid(constructs: dict[str, dict[str, Any]], out_dir: Path) -> dict[str, float]:
    fig, axes = plt.subplots(2, 3, figsize=(15.5, 9.2))
    axes_flat = axes.ravel()
    colors = ["#4477AA", "#228833", "#AA3377", "#EE7733", "#66CCEE"]
    correlations: dict[str, float] = {}
    for ax, (idx, (name, spec)) in zip(axes_flat, enumerate(constructs.items())):
        df = spec["df"]
        x = df[spec["x"]].to_numpy(float)
        y = df[spec["y"]].to_numpy(float)
        r = safe_corr(x, y)
        correlations[name] = r
        ax.scatter(x, y, s=42, alpha=0.72, color=colors[idx], edgecolor="white", linewidth=0.3)
        fit_line(ax, x, y, colors[idx])
        ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.45)
        ax.set_xlim(-0.03, 1.03)
        ax.set_ylim(-0.03, 1.03)
        ax.grid(True, alpha=0.23)
        ax.set_title(f"{name}\nr = {r:.3f}", fontsize=12, fontweight="bold")
        ax.set_xlabel("Operational proxy")
        ax.set_ylabel("Independent / hard-probe measure")
        ax.text(
            0.03,
            0.97,
            spec["mechanism"],
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=8.5,
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#CCCCCC", "alpha": 0.85},
        )
    ax = axes_flat[-1]
    labels = list(correlations.keys())
    vals = [correlations[label] for label in labels]
    bar_colors = colors[: len(vals)]
    ax.barh(labels[::-1], vals[::-1], color=bar_colors[::-1], alpha=0.85)
    ax.axvline(0.7, color="#444444", linestyle="--", linewidth=1, label="validation threshold")
    ax.set_xlim(0, 1.02)
    ax.set_xlabel("Proxy-test correlation")
    ax.set_title("Validation summary", fontsize=12, fontweight="bold")
    ax.grid(axis="x", alpha=0.23)
    ax.legend(loc="lower right", fontsize=8)
    fig.suptitle("Five Operational Constructs After Measurement Refinement", fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_dir / "figure_construct_validation_grid.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    return correlations


def figure_distributed_controls(paths: dict[str, Path], out_dir: Path) -> dict[str, float]:
    raw = pd.read_csv(paths["distributed"])
    summary = raw.groupby(["condition", "control_type"], as_index=False).mean(numeric_only=True)
    strength = summary[summary["control_type"] == "strength"].sort_values("meta_monitor_strength")
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.2))
    ax = axes[0]
    ax.plot(strength["meta_monitor_strength"], strength["proxy_self_model"], "o-", label="proxy self", color="#4477AA")
    ax.plot(strength["meta_monitor_strength"], strength["hard_self_without_lesion"], "o-", label="hard probes", color="#228833")
    ax.plot(strength["meta_monitor_strength"], strength["hard_body_schema_update"], "o-", label="body-schema update", color="#EE7733")
    ax.set_xlabel("Meta-monitor strength")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.02)
    ax.set_title("Graded meta-monitor dose response", fontweight="bold")
    ax.grid(True, alpha=0.25)
    ax.legend()

    ax = axes[1]
    noise_delay = summary[summary["control_type"].isin(["noise", "delay"])].copy()
    labels = list(noise_delay["condition"])
    x = np.arange(len(labels))
    ax.bar(x - 0.2, noise_delay["proxy_self_model"], 0.4, label="proxy self", color="#4477AA", alpha=0.85)
    ax.bar(x + 0.2, noise_delay["hard_self_without_lesion"], 0.4, label="hard probes", color="#228833", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylim(0, 1.02)
    ax.set_ylabel("Score")
    ax.set_title("Accuracy and timing controls", fontweight="bold")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.suptitle("Distributed Self: Graded Meta-Monitor Controls", fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(out_dir / "figure_distributed_meta_monitor_controls.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    return {
        "strength_vs_proxy_self": safe_corr(raw[raw["control_type"] == "strength"]["meta_monitor_strength"].to_numpy(float), raw[raw["control_type"] == "strength"]["proxy_self_model"].to_numpy(float)),
        "strength_vs_hard_self": safe_corr(raw[raw["control_type"] == "strength"]["meta_monitor_strength"].to_numpy(float), raw[raw["control_type"] == "strength"]["hard_self_without_lesion"].to_numpy(float)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate construct validation summary figures from latest measurement runs.")
    parser.add_argument("--out-dir", type=Path, default=Path("docs") / "paper" / "figures" / "construct_validation_20260521")
    parser.add_argument("--agency", type=Path, default=DEFAULT_PATHS["agency"])
    parser.add_argument("--boundary", type=Path, default=DEFAULT_PATHS["boundary"])
    parser.add_argument("--temporal", type=Path, default=DEFAULT_PATHS["temporal"])
    parser.add_argument("--ownership", type=Path, default=DEFAULT_PATHS["ownership"])
    parser.add_argument("--distributed", type=Path, default=DEFAULT_PATHS["distributed"])
    args = parser.parse_args()

    out_dir = ensure_dir(args.out_dir)
    paths = {
        "agency": args.agency,
        "boundary": args.boundary,
        "temporal": args.temporal,
        "ownership": args.ownership,
        "distributed": args.distributed,
    }
    constructs = load_constructs(paths)
    construct_corr = figure_construct_grid(constructs, out_dir)
    distributed_corr = figure_distributed_controls(paths, out_dir)
    payload = {
        "out_dir": str(out_dir),
        "inputs": {key: str(value) for key, value in paths.items()},
        "construct_correlations": construct_corr,
        "distributed_control_correlations": distributed_corr,
        "files": {
            "construct_grid": str(out_dir / "figure_construct_validation_grid.png"),
            "distributed_controls": str(out_dir / "figure_distributed_meta_monitor_controls.png"),
        },
    }
    write_json(out_dir / "manifest.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
