from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "docs" / "paper" / "figures" / "paper_v2_20260521"
SNAPSHOT_DIR = PROJECT_ROOT / "docs" / "paper" / "figure_snapshots" / "20260521_paper_v2"

TRANSFORMER_STATS_DIR = PROJECT_ROOT / "docs" / "paper" / "statistics" / "transformer_20260522"


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
            "legend.fontsize": 8.2,
            "savefig.dpi": 240,
        }
    )


def load_stats() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    high = pd.read_csv(TRANSFORMER_STATS_DIR / "transformer_high_corr_stats.csv")
    boundary = pd.read_csv(TRANSFORMER_STATS_DIR / "transformer_specific_boundary_stats.csv")
    variants = pd.read_csv(TRANSFORMER_STATS_DIR / "transformer_construct_variants_stats.csv")
    raw = pd.read_csv(TRANSFORMER_STATS_DIR / "transformer_construct_variants_raw.csv")
    return high, boundary, variants, raw


def stat_value(df: pd.DataFrame, **query: str) -> float:
    mask = np.ones(len(df), dtype=bool)
    for key, value in query.items():
        mask &= df[key].astype(str).to_numpy() == value
    sub = df.loc[mask]
    if sub.empty:
        raise KeyError(query)
    return float(sub.iloc[0]["r"])


def panel_bar(ax: plt.Axes, labels: list[str], values: list[float], title: str, ylabel: str = "r") -> None:
    colors = ["#4477AA" if v >= 0.7 else "#EE7733" if v >= 0.4 else "#CC6677" for v in values]
    ax.bar(np.arange(len(values)), values, color=colors, edgecolor="#222222", linewidth=0.8)
    ax.axhline(0.7, color="#222222", linestyle="--", linewidth=1.0, alpha=0.65)
    ax.axhline(0.0, color="#222222", linewidth=0.8, alpha=0.55)
    ax.set_xticks(np.arange(len(values)))
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylim(-0.25, 1.05)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontweight="bold")
    for i, value in enumerate(values):
        ax.text(i, value + (0.035 if value >= 0 else -0.075), f"{value:.2f}", ha="center", va="bottom" if value >= 0 else "top", fontsize=8.2)


def make_figure() -> Path:
    set_style()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    high, boundary, variants, raw = load_stats()
    fig, axes = plt.subplots(2, 2, figsize=(12.4, 9.0))

    clean_agency = 0.9998
    clean_ownership = 0.99999
    stress_agency = stat_value(high, subset="all", diagnostic="proxy_agency_vs_independent")
    stress_ownership = stat_value(high, subset="all", diagnostic="proxy_ownership_vs_independent")
    learning_agency = stat_value(high, subset="learning_sweep", diagnostic="proxy_agency_vs_independent")
    learning_ownership = stat_value(high, subset="learning_sweep", diagnostic="proxy_ownership_vs_independent")
    panel_bar(
        axes[0, 0],
        ["clean\nagency", "clean\nownership", "stress\nagency", "stress\nownership", "learning\nagency", "learning\nownership"],
        [clean_agency, clean_ownership, stress_agency, stress_ownership, learning_agency, learning_ownership],
        "A. Near-perfect Transformer validation is stress-sensitive",
    )

    boundary_values = [
        stat_value(boundary, diagnostic="dose_vs_proxy_boundary"),
        stat_value(boundary, diagnostic="proxy_vs_generic_boundary"),
        stat_value(boundary, diagnostic="proxy_vs_hard_attention_boundary"),
        stat_value(boundary, diagnostic="dose_vs_hard_attention_boundary"),
    ]
    panel_bar(
        axes[0, 1],
        ["dose ->\nproxy", "proxy ->\ngeneric", "proxy ->\nhard attention", "dose ->\nhard attention"],
        boundary_values,
        "B. Workspace proxy moves, boundary validation does not",
    )

    pred = raw[raw["study"] == "predictive_agency_without_boundary"].copy()
    pred = pred.dropna(subset=["independent_agency", "independent_boundary_self"])
    high_low = (pred["independent_agency"] >= 0.70) & (pred["independent_boundary_self"] < 0.50)
    colors = np.where(high_low, "#228833", "#BBBBBB")
    axes[1, 0].scatter(
        pred["independent_boundary_self"],
        pred["independent_agency"],
        c=colors,
        s=48,
        alpha=0.78,
        edgecolor="white",
        linewidth=0.35,
    )
    axes[1, 0].axhline(0.70, color="#222222", linestyle="--", linewidth=1.0)
    axes[1, 0].axvline(0.50, color="#222222", linestyle="--", linewidth=1.0)
    axes[1, 0].set_xlim(0.35, 0.62)
    axes[1, 0].set_ylim(0.50, 1.00)
    axes[1, 0].set_xlabel("independent boundary")
    axes[1, 0].set_ylabel("independent agency")
    axes[1, 0].set_title("C. High-agency / low-boundary region", fontweight="bold")
    axes[1, 0].text(0.355, 0.965, f"{int(high_low.sum())}/{len(pred)} rows = {high_low.mean() * 100:.1f}%", fontsize=9.2, va="top")

    candidate_values = [
        stat_value(variants, study="attention_focus_self", x="proxy_attention_focus_self"),
        stat_value(variants, study="context_window_self", x="proxy_context_window_self"),
        stat_value(variants, study="context_window_self", x="dose"),
        stat_value(variants, study="predictive_agency_without_boundary", x="independent_agency"),
    ]
    panel_bar(
        axes[1, 1],
        ["attention\nfocus", "context\nwindow", "context\ndose", "agency vs\nboundary"],
        candidate_values,
        "D. Candidate variants remain exploratory",
    )
    axes[1, 1].set_ylim(-0.05, 0.55)
    axes[1, 1].axhline(0.7, color="#222222", linestyle="--", linewidth=1.0, alpha=0.65)

    fig.suptitle("Figure 6. Transformer Diagnostics: Mechanism Generalization, Measurement Limits, and Construct Variation", fontsize=13.0, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.965))

    out = OUT_DIR / "figure6_transformer_diagnostics.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)

    snap = SNAPSHOT_DIR / out.name
    snap.write_bytes(out.read_bytes())

    manifest_path = OUT_DIR / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"out_dir": str(OUT_DIR.relative_to(PROJECT_ROOT)), "figures": []}
    figures = list(manifest.get("figures", []))
    if out.name not in figures:
        figures.append(out.name)
    manifest["figures"] = figures
    manifest["transformer_diagnostic_metrics"] = {
        "stress_agency_r": stress_agency,
        "stress_ownership_r": stress_ownership,
        "learning_agency_r": learning_agency,
        "learning_ownership_r": learning_ownership,
        "boundary_dose_proxy_r": boundary_values[0],
        "boundary_proxy_hard_r": boundary_values[2],
        "high_agency_low_boundary_rows": int(high_low.sum()),
        "high_agency_low_boundary_total": int(len(pred)),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (SNAPSHOT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return out


def main() -> None:
    out = make_figure()
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
