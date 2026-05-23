from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mind_lab.distributed import DistributedArchitecture
from mind_lab.thalamus import ThalamusInspiredArchitecture
from mind_lab.utils import ensure_dir, safe_corr, write_json
from mind_lab.validation import make_system, run_independent_validation, run_steps
from scripts.run_measurement_diagnostics import collect_intermediates, finite_corr, markdown_table
from scripts.run_measurement_validation import distributed_conditions, thalamus_conditions


SELF_TESTS = {
    "boundary_perturbation",
    "computational_mirror",
    "ownership_attribution",
    "architecture_self_probe",
}


def flatten_details(prefix: str, value: Any) -> dict[str, float]:
    rows: dict[str, float] = {}
    if isinstance(value, dict):
        for key, item in value.items():
            rows.update(flatten_details(f"{prefix}_{key}", item))
    elif isinstance(value, bool):
        rows[prefix] = float(value)
    elif isinstance(value, (int, float, np.integer, np.floating)):
        rows[prefix] = float(value)
    return rows


def build_conditions(architectures: list[str]) -> list[dict[str, Any]]:
    conditions: list[dict[str, Any]] = []
    if "thalamus" in architectures:
        conditions.extend(thalamus_conditions())
    if "distributed" in architectures:
        conditions.extend(distributed_conditions())
    return conditions


def self_specific_intermediates(system: Any) -> dict[str, float]:
    rows: dict[str, float] = {}
    if hasattr(system, "system_measurements"):
        for key, value in system.system_measurements().items():
            if isinstance(value, (int, float, np.integer, np.floating)):
                rows[f"self_m_{key}"] = float(value)
    if isinstance(system, ThalamusInspiredArchitecture):
        history = system.history[-max(1, getattr(system, "measurement_window", 128)) :]
        workspace_sizes = np.array([h["workspace_size"] for h in history], dtype=float) if history else np.zeros(1)
        source_counts = np.array([h.get("source_count", 0.0) for h in history], dtype=float) if history else np.zeros(1)
        gated = np.array([h.get("gated_count", 0.0) for h in history], dtype=float) if history else np.zeros(1)
        rows.update(
            {
                "self_i_arch_thalamus": 1.0,
                "self_i_arch_distributed": 0.0,
                "self_i_workspace_enabled": 1.0 if system.enable_workspace else 0.0,
                "self_i_reticular_enabled": 1.0 if system.enable_reticular else 0.0,
                "self_i_workspace_capacity": float(system.workspace.capacity),
                "self_i_workspace_load": float(system.workspace.load()),
                "self_i_mean_workspace_size": float(np.mean(workspace_sizes)),
                "self_i_std_workspace_size": float(np.std(workspace_sizes)),
                "self_i_workspace_cv": float(np.std(workspace_sizes) / (np.mean(workspace_sizes) + 1e-6)),
                "self_i_mean_source_count": float(np.mean(source_counts)),
                "self_i_mean_gated_count": float(np.mean(gated)),
                "self_i_std_gated_count": float(np.std(gated)),
            }
        )
    elif isinstance(system, DistributedArchitecture):
        history = system.history[-max(1, getattr(system, "measurement_window", 128)) :]
        if history:
            active = np.array([h["meta"]["active_agents"] for h in history], dtype=float)
            spread = np.array([h["meta"]["spread"] for h in history], dtype=float)
            align = np.array([h["meta"]["goal_alignment"] for h in history], dtype=float)
            energy = np.array([h["mean_energy"] for h in history], dtype=float)
        else:
            active = spread = align = energy = np.zeros(1)
        positions = np.stack([agent.position for agent in system.agents]).astype(float)
        centroid = positions.mean(axis=0)
        rows.update(
            {
                "self_i_arch_thalamus": 0.0,
                "self_i_arch_distributed": 1.0,
                "self_i_num_agents": float(system.num_agents),
                "self_i_active_agents_mean": float(np.mean(active)),
                "self_i_active_agents_std": float(np.std(active)),
                "self_i_spread_mean": float(np.mean(spread)),
                "self_i_spread_std": float(np.std(spread)),
                "self_i_goal_alignment_mean": float(np.mean(align)),
                "self_i_goal_alignment_std": float(np.std(align)),
                "self_i_energy_mean": float(np.mean(energy)),
                "self_i_energy_std": float(np.std(energy)),
                "self_i_centroid_x": float(centroid[0] / max(float(system.env.size), 1.0)),
                "self_i_centroid_y": float(centroid[1] / max(float(system.env.size), 1.0)),
            }
        )
    rows.update(collect_intermediates(system))
    return rows


def run_one(condition: dict[str, Any], seed: int, warmup: int, quick: bool) -> dict[str, Any]:
    system = make_system(condition["architecture"], condition["config"], seed)
    run_steps(system, warmup)
    validation = run_independent_validation(system, seed=seed + 900_000, quick=quick)
    proxy = validation["proxy_scores"]
    measurements = system.system_measurements() if hasattr(system, "system_measurements") else {}
    row: dict[str, Any] = {
        "architecture": condition["architecture"],
        "condition": condition["condition"],
        "seed": seed,
        "proxy_self_model": proxy["self_model"],
        "proxy_boundary_self": float(measurements.get("boundary_self_proxy", proxy["self_model"])),
        "proxy_temporal_self": float(measurements.get("temporal_self_proxy", proxy.get("temporal_continuity", 0.0))),
        "proxy_ownership_self": float(measurements.get("ownership_self_proxy", proxy["agency"])),
        "proxy_legacy_self_model": float(measurements.get("legacy_self_model_stability", proxy["self_model"])),
        "proxy_agency": proxy["agency"],
        "independent_self_model": validation["independent_self_model"],
        "independent_agency": validation["independent_agency"],
        "self_discrepancy": proxy["self_model"] - validation["independent_self_model"],
    }
    test_scores: dict[str, float] = {}
    for item in validation["tests"]:
        test_name = item["test"]
        test_scores[test_name] = float(item["score"])
        row[f"test_{test_name}"] = test_scores[test_name]
        row[f"pass_{test_name}"] = bool(item["passed"])
        if test_name in SELF_TESTS:
            row.update(flatten_details(f"detail_{test_name}", item.get("details", {})))
    row["independent_self_core_boundary"] = float(
        np.mean(
            [
                test_scores.get("boundary_perturbation", 0.0),
                test_scores.get("architecture_self_probe", 0.0),
            ]
        )
    )
    row["independent_self_identity_ownership"] = float(
        np.mean(
            [
                test_scores.get("computational_mirror", 0.0),
                test_scores.get("ownership_attribution", 0.0),
            ]
        )
    )
    row["self_core_discrepancy"] = row["proxy_self_model"] - row["independent_self_core_boundary"]
    row["self_identity_discrepancy"] = row["proxy_self_model"] - row["independent_self_identity_ownership"]
    row["boundary_proxy_discrepancy"] = row["proxy_boundary_self"] - row["independent_self_core_boundary"]
    row["temporal_proxy_discrepancy"] = row["proxy_temporal_self"] - test_scores.get("computational_mirror", 0.0)
    row["ownership_proxy_discrepancy"] = row["proxy_ownership_self"] - test_scores.get("ownership_attribution", 0.0)
    row.update(self_specific_intermediates(system))
    return row


def corr_summary(df: pd.DataFrame) -> dict[str, float]:
    summary: dict[str, float] = {
        "overall_self_model_r": safe_corr(df["proxy_self_model"].to_numpy(dtype=float), df["independent_self_model"].to_numpy(dtype=float)),
        "overall_core_boundary_self_r": safe_corr(
            df["proxy_self_model"].to_numpy(dtype=float),
            df["independent_self_core_boundary"].to_numpy(dtype=float),
        ),
        "overall_identity_ownership_self_r": safe_corr(
            df["proxy_self_model"].to_numpy(dtype=float),
            df["independent_self_identity_ownership"].to_numpy(dtype=float),
        ),
        "boundary_proxy_to_core_boundary_r": safe_corr(
            df["proxy_boundary_self"].to_numpy(dtype=float),
            df["independent_self_core_boundary"].to_numpy(dtype=float),
        ),
        "temporal_proxy_to_mirror_r": safe_corr(
            df["proxy_temporal_self"].to_numpy(dtype=float),
            df["test_computational_mirror"].to_numpy(dtype=float),
        ),
        "ownership_proxy_to_ownership_test_r": safe_corr(
            df["proxy_ownership_self"].to_numpy(dtype=float),
            df["test_ownership_attribution"].to_numpy(dtype=float),
        ),
    }
    for architecture, group in df.groupby("architecture"):
        summary[f"{architecture}_self_model_r"] = safe_corr(
            group["proxy_self_model"].to_numpy(dtype=float),
            group["independent_self_model"].to_numpy(dtype=float),
        )
        summary[f"{architecture}_core_boundary_self_r"] = safe_corr(
            group["proxy_self_model"].to_numpy(dtype=float),
            group["independent_self_core_boundary"].to_numpy(dtype=float),
        )
        summary[f"{architecture}_identity_ownership_self_r"] = safe_corr(
            group["proxy_self_model"].to_numpy(dtype=float),
            group["independent_self_identity_ownership"].to_numpy(dtype=float),
        )
        summary[f"{architecture}_boundary_proxy_to_core_boundary_r"] = safe_corr(
            group["proxy_boundary_self"].to_numpy(dtype=float),
            group["independent_self_core_boundary"].to_numpy(dtype=float),
        )
        summary[f"{architecture}_temporal_proxy_to_mirror_r"] = safe_corr(
            group["proxy_temporal_self"].to_numpy(dtype=float),
            group["test_computational_mirror"].to_numpy(dtype=float),
        )
        summary[f"{architecture}_ownership_proxy_to_ownership_test_r"] = safe_corr(
            group["proxy_ownership_self"].to_numpy(dtype=float),
            group["test_ownership_attribution"].to_numpy(dtype=float),
        )
    return summary


def correlation_table(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [
        col
        for col in df.columns
        if (
            col.startswith("self_m_")
            or col.startswith("self_i_")
            or col.startswith("i_")
            or col.startswith("m_")
            or col.startswith("test_")
            or col.startswith("detail_architecture_self_probe")
            or col.startswith("detail_boundary_perturbation")
        )
        and pd.api.types.is_numeric_dtype(df[col])
    ]
    targets = [
        "proxy_self_model",
        "proxy_boundary_self",
        "proxy_temporal_self",
        "proxy_ownership_self",
        "proxy_legacy_self_model",
        "independent_self_model",
        "independent_self_core_boundary",
        "independent_self_identity_ownership",
        "self_discrepancy",
        "self_core_discrepancy",
        "self_identity_discrepancy",
        "boundary_proxy_discrepancy",
        "temporal_proxy_discrepancy",
        "ownership_proxy_discrepancy",
    ]
    rows = []
    for col in numeric_cols:
        for target in targets:
            rows.append({"variable": col, "target": target, "r": finite_corr(df[col], df[target])})
    return pd.DataFrame(rows).sort_values("r", key=lambda s: s.abs(), ascending=False)


def save_scatter(df: pd.DataFrame, out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.2, 5.4))
    colors = {"thalamus": "tab:blue", "distributed": "tab:orange"}
    for architecture, group in df.groupby("architecture"):
        ax.scatter(
            group["proxy_self_model"],
            group["independent_self_model"],
            s=58,
            alpha=0.78,
            label=architecture,
            color=colors.get(architecture),
        )
    ax.plot([0, 1], [0, 1], "k--", linewidth=1.0, alpha=0.6)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.25)
    r = safe_corr(df["proxy_self_model"].to_numpy(dtype=float), df["independent_self_model"].to_numpy(dtype=float))
    ax.set_title(f"Self-model proxy vs independent tests (r={r:.2f})")
    ax.set_xlabel("Proxy self-model")
    ax.set_ylabel("Independent self-model")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "self_proxy_vs_independent_scatter.png", dpi=180)
    plt.close(fig)


def save_condition_bars(summary: pd.DataFrame, out_dir: Path) -> None:
    labels = [f"{r.architecture}\n{r.condition}" for r in summary.itertuples()]
    x = np.arange(len(summary))
    width = 0.28
    fig, ax = plt.subplots(figsize=(11.5, 5.2))
    ax.bar(x - width, summary["proxy_self_model"], width, label="proxy self", color="tab:blue", alpha=0.75)
    ax.bar(x, summary["independent_self_model"], width, label="independent self", color="tab:green", alpha=0.75)
    if "test_architecture_self_probe" in summary.columns:
        ax.bar(x + width, summary["test_architecture_self_probe"], width, label="architecture probe", color="tab:purple", alpha=0.75)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Self-model: proxy vs independent and architecture-specific tests")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "self_proxy_independent_by_condition.png", dpi=180)
    plt.close(fig)


def save_correlates(corr: pd.DataFrame, out_dir: Path) -> None:
    data = corr[corr["target"] == "self_discrepancy"].copy()
    data = data.reindex(data["r"].abs().sort_values(ascending=False).index).head(14)
    if data.empty:
        return
    data = data.iloc[::-1]
    fig, ax = plt.subplots(figsize=(9.8, 5.8))
    ax.barh(data["variable"], data["r"], color=["tab:red" if v > 0 else "tab:blue" for v in data["r"]], alpha=0.82)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Correlation with proxy-independent self discrepancy")
    ax.set_title("Self-model discrepancy correlates")
    fig.tight_layout()
    fig.savefig(out_dir / "self_discrepancy_correlates.png", dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run self-model-focused proxy validation diagnostics.")
    parser.add_argument("--output-root", type=Path, default=Path("runs") / "measurement_validation")
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--warmup", type=int, default=160)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed-base", type=int, default=20260521)
    parser.add_argument("--architectures", nargs="*", default=["thalamus", "distributed"], choices=["thalamus", "distributed"])
    args = parser.parse_args()

    out_dir = ensure_dir(args.output_root / f"self_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    rows = []
    conditions = build_conditions(args.architectures)
    for idx, condition in enumerate(conditions):
        for seed_idx in range(args.seeds):
            rows.append(run_one(condition, args.seed_base + idx * 1000 + seed_idx, args.warmup, args.quick))

    raw = pd.DataFrame(rows)
    raw.to_csv(out_dir / "self_diagnostic_raw.csv", index=False)
    agg_spec = {
        "proxy_self_model": ("proxy_self_model", "mean"),
        "proxy_boundary_self": ("proxy_boundary_self", "mean"),
        "proxy_temporal_self": ("proxy_temporal_self", "mean"),
        "proxy_ownership_self": ("proxy_ownership_self", "mean"),
        "proxy_legacy_self_model": ("proxy_legacy_self_model", "mean"),
        "independent_self_model": ("independent_self_model", "mean"),
        "independent_self_core_boundary": ("independent_self_core_boundary", "mean"),
        "independent_self_identity_ownership": ("independent_self_identity_ownership", "mean"),
        "self_discrepancy": ("self_discrepancy", "mean"),
        "self_core_discrepancy": ("self_core_discrepancy", "mean"),
        "self_identity_discrepancy": ("self_identity_discrepancy", "mean"),
        "boundary_proxy_discrepancy": ("boundary_proxy_discrepancy", "mean"),
        "temporal_proxy_discrepancy": ("temporal_proxy_discrepancy", "mean"),
        "ownership_proxy_discrepancy": ("ownership_proxy_discrepancy", "mean"),
    }
    for col in raw.columns:
        if col.startswith("test_") and raw[col].dtype.kind in "if":
            agg_spec[col] = (col, "mean")
    condition_summary = raw.groupby(["architecture", "condition"], as_index=False).agg(**agg_spec)
    condition_summary.to_csv(out_dir / "self_condition_summary.csv", index=False)
    corr = correlation_table(raw)
    corr.to_csv(out_dir / "self_intermediate_correlations.csv", index=False)

    save_scatter(raw, out_dir)
    save_condition_bars(condition_summary, out_dir)
    save_correlates(corr, out_dir)

    correlations = corr_summary(raw)
    report = [
        "# Self-Model Diagnostic Report",
        "",
        "## Correlations",
        "",
        "```json",
        json.dumps(correlations, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Condition Summary",
        "",
        markdown_table(condition_summary, max_rows=20),
        "",
        "## Strongest Correlates Of Self Discrepancy",
        "",
        markdown_table(corr[corr["target"] == "self_discrepancy"].head(16), max_rows=16),
        "",
        "## Strongest Correlates Of Core/Boundary Self Discrepancy",
        "",
        markdown_table(corr[corr["target"] == "self_core_discrepancy"].head(16), max_rows=16),
        "",
        "## Strongest Correlates Of Identity/Ownership Self Discrepancy",
        "",
        markdown_table(corr[corr["target"] == "self_identity_discrepancy"].head(16), max_rows=16),
        "",
        "## Proxy-Specific Discrepancies",
        "",
        "Boundary, temporal, and ownership proxies are reported separately to prevent a single self-model average from hiding construct mismatch.",
        "",
        "## Guardrail",
        "",
        "Architecture-specific self probes are validation candidates, not final construct definitions. Treat improved agreement as evidence for better operational alignment, not as direct evidence of consciousness.",
    ]
    (out_dir / "self_diagnostic_report.md").write_text("\n".join(report), encoding="utf-8")
    summary = {
        "output_dir": str(out_dir),
        "rows": len(raw),
        "correlations": correlations,
        "files": {
            "raw": str(out_dir / "self_diagnostic_raw.csv"),
            "condition_summary": str(out_dir / "self_condition_summary.csv"),
            "correlations": str(out_dir / "self_intermediate_correlations.csv"),
            "report": str(out_dir / "self_diagnostic_report.md"),
            "scatter": str(out_dir / "self_proxy_vs_independent_scatter.png"),
            "condition_bars": str(out_dir / "self_proxy_independent_by_condition.png"),
            "discrepancy_correlates": str(out_dir / "self_discrepancy_correlates.png"),
        },
    }
    write_json(out_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
