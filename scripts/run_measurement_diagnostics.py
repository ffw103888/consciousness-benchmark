from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mind_lab.distributed import DistributedArchitecture
from mind_lab.thalamus import ThalamusInspiredArchitecture
from mind_lab.utils import ensure_dir, entropy, safe_corr, write_json
from mind_lab.validation import (
    action_vector,
    behavior_vector,
    evaluation_scores,
    make_system,
    run_independent_validation,
    run_steps,
)
from scripts.run_measurement_validation import distributed_conditions, thalamus_conditions


def numeric_measurements(system: Any) -> dict[str, float]:
    if not hasattr(system, "system_measurements"):
        return {}
    measurements = system.system_measurements()
    rows: dict[str, float] = {}
    for key, value in measurements.items():
        if np.isscalar(value):
            try:
                rows[f"m_{key}"] = float(value)
            except Exception:
                pass
    return rows


def thalamus_intermediates(system: ThalamusInspiredArchitecture) -> dict[str, float]:
    recent = system.history[-max(1, getattr(system, "measurement_window", 256)) :]
    if not recent:
        return {}
    gated = np.array([r["gated_count"] for r in recent], dtype=float)
    threshold = np.array([r["threshold"] for r in recent], dtype=float)
    workspace_size = np.array([r["workspace_size"] for r in recent], dtype=float)
    arousal = np.array([r["arousal"] for r in recent], dtype=float)
    cortical = np.array([r["cortical_norm"] for r in recent], dtype=float)
    action_norms = (
        np.array(system.action_loop.action_norms[-128:], dtype=float)
        if system.action_loop is not None and system.action_loop.action_norms
        else np.zeros(1)
    )
    prediction_errors = (
        np.array(system.action_loop.prediction_errors[-128:], dtype=float)
        if system.action_loop is not None and system.action_loop.prediction_errors
        else np.ones(1)
    )
    return {
        "i_arch_thalamus": 1.0,
        "i_arch_distributed": 0.0,
        "i_workspace_enabled": 1.0 if system.enable_workspace else 0.0,
        "i_action_loop_enabled": 1.0 if system.enable_action_loop else 0.0,
        "i_workspace_capacity": float(system.workspace.capacity),
        "i_workspace_load": float(system.workspace.load()),
        "i_mean_gated_count": float(np.mean(gated)),
        "i_std_gated_count": float(np.std(gated)),
        "i_gated_entropy": float(entropy(gated, bins=8)),
        "i_mean_threshold": float(np.mean(threshold)),
        "i_std_threshold": float(np.std(threshold)),
        "i_mean_workspace_size": float(np.mean(workspace_size)),
        "i_std_workspace_size": float(np.std(workspace_size)),
        "i_mean_arousal": float(np.mean(arousal)),
        "i_std_arousal": float(np.std(arousal)),
        "i_mean_cortical_norm": float(np.mean(cortical)),
        "i_action_frequency": float(np.mean(action_norms > 1e-6)),
        "i_action_norm_mean": float(np.mean(action_norms)),
        "i_action_norm_std": float(np.std(action_norms)),
        "i_internal_prediction_error": float(np.mean(prediction_errors)),
        "i_behavior_action_similarity": float(
            1.0
            - min(
                np.linalg.norm(behavior_vector(system)[: min(behavior_vector(system).size, action_vector(system).size)] - action_vector(system)[: min(behavior_vector(system).size, action_vector(system).size)])
                / (np.linalg.norm(behavior_vector(system)) + np.linalg.norm(action_vector(system)) + 1e-9),
                1.0,
            )
        ),
    }


def distributed_intermediates(system: DistributedArchitecture) -> dict[str, float]:
    recent = system.history[-max(1, getattr(system, "measurement_window", 256)) :]
    if not recent:
        return {}
    success = np.array([r["meta"]["success_rate"] for r in recent], dtype=float)
    controllability = np.array([r["meta"]["controllability"] for r in recent], dtype=float)
    alignment = np.array([r["meta"]["goal_alignment"] for r in recent], dtype=float)
    conflicts = np.array([r["coordination"]["conflicts"] for r in recent], dtype=float)
    energy = np.array([r["mean_energy"] for r in recent], dtype=float)
    positions = np.stack([agent.position for agent in system.agents]).astype(float)
    centroid = positions.mean(axis=0)
    spread = float(np.mean(np.linalg.norm(positions - centroid, axis=1)) / max(float(system.env.size), 1.0))
    action_vectors = []
    for agent in system.agents:
        if agent.last_request is None:
            continue
        target = np.asarray(agent.last_request.get("target", agent.position), dtype=float)
        action_vectors.append((target - agent.position.astype(float)) / max(float(system.env.size), 1.0))
    if action_vectors:
        action_matrix = np.stack(action_vectors)
        action_norms = np.linalg.norm(action_matrix, axis=1)
    else:
        action_norms = np.zeros(1)
    return {
        "i_arch_thalamus": 0.0,
        "i_arch_distributed": 1.0,
        "i_action_feedback_enabled": 1.0 if system.enable_action_feedback else 0.0,
        "i_num_agents": float(system.num_agents),
        "i_mean_success": float(np.mean(success)),
        "i_std_success": float(np.std(success)),
        "i_mean_controllability": float(np.mean(controllability)),
        "i_std_controllability": float(np.std(controllability)),
        "i_mean_goal_alignment": float(np.mean(alignment)),
        "i_std_goal_alignment": float(np.std(alignment)),
        "i_mean_conflicts": float(np.mean(conflicts)),
        "i_std_conflicts": float(np.std(conflicts)),
        "i_mean_energy": float(np.mean(energy)),
        "i_std_energy": float(np.std(energy)),
        "i_spread": spread,
        "i_action_frequency": float(np.mean(action_norms > 1e-6)),
        "i_action_norm_mean": float(np.mean(action_norms)),
        "i_action_norm_std": float(np.std(action_norms)),
        "i_behavior_action_similarity": float(
            1.0
            - min(
                np.linalg.norm(behavior_vector(system)[: min(behavior_vector(system).size, action_vector(system).size)] - action_vector(system)[: min(behavior_vector(system).size, action_vector(system).size)])
                / (np.linalg.norm(behavior_vector(system)) + np.linalg.norm(action_vector(system)) + 1e-9),
                1.0,
            )
        ),
    }


def collect_intermediates(system: Any) -> dict[str, float]:
    rows = numeric_measurements(system)
    if isinstance(system, ThalamusInspiredArchitecture):
        rows.update(thalamus_intermediates(system))
    elif isinstance(system, DistributedArchitecture):
        rows.update(distributed_intermediates(system))
    return rows


def finite_corr(x: pd.Series, y: pd.Series) -> float:
    data = pd.concat([x, y], axis=1).dropna()
    if len(data) < 3:
        return 0.0
    if data.iloc[:, 0].nunique() < 2 or data.iloc[:, 1].nunique() < 2:
        return 0.0
    return safe_corr(data.iloc[:, 0].to_numpy(dtype=float), data.iloc[:, 1].to_numpy(dtype=float))


def residualize(y: np.ndarray, z: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    z = np.asarray(z, dtype=float).reshape(-1, 1)
    x = np.column_stack([np.ones(len(z)), z])
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    return y - x @ beta


def partial_corr(df: pd.DataFrame, x_col: str, y_col: str, z_col: str) -> float:
    data = df[[x_col, y_col, z_col]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(data) < 4:
        return 0.0
    if any(data[col].nunique() < 2 for col in [x_col, y_col, z_col]):
        return 0.0
    x_res = residualize(data[x_col].to_numpy(dtype=float), data[z_col].to_numpy(dtype=float))
    y_res = residualize(data[y_col].to_numpy(dtype=float), data[z_col].to_numpy(dtype=float))
    return safe_corr(x_res, y_res)


def build_conditions(architectures: list[str]) -> list[dict[str, Any]]:
    conditions: list[dict[str, Any]] = []
    if "thalamus" in architectures:
        conditions.extend(thalamus_conditions())
    if "distributed" in architectures:
        conditions.extend(distributed_conditions())
    return conditions


def run_one(condition: dict[str, Any], seed: int, warmup: int, quick: bool) -> dict[str, Any]:
    system = make_system(condition["architecture"], condition["config"], seed)
    run_steps(system, warmup)
    validation = run_independent_validation(system, seed=seed + 700_000, quick=quick)
    proxy = evaluation_scores(system)
    test_scores = {f"test_{item['test']}": item["score"] for item in validation["tests"]}
    row = {
        "architecture": condition["architecture"],
        "condition": condition["condition"],
        "seed": seed,
        "proxy_self_model": proxy["self_model"],
        "proxy_agency": proxy["agency"],
        "independent_self_model": validation["independent_self_model"],
        "independent_agency": validation["independent_agency"],
        "self_discrepancy": proxy["self_model"] - validation["independent_self_model"],
        "agency_discrepancy": proxy["agency"] - validation["independent_agency"],
        **test_scores,
        **collect_intermediates(system),
    }
    return row


def correlation_tables(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    numeric_cols = [
        col
        for col in df.columns
        if (col.startswith("m_") or col.startswith("i_") or col.startswith("test_"))
        and pd.api.types.is_numeric_dtype(df[col])
    ]
    targets = ["proxy_self_model", "independent_self_model", "self_discrepancy", "proxy_agency", "independent_agency", "agency_discrepancy"]
    corr_rows = []
    partial_rows = []
    for col in numeric_cols:
        for target in targets:
            corr_rows.append({"variable": col, "target": target, "r": finite_corr(df[col], df[target])})
        partial_rows.append(
            {
                "variable": col,
                "partial_proxy_independent_self_controlling_variable": partial_corr(df, "proxy_self_model", "independent_self_model", col),
                "partial_proxy_independent_agency_controlling_variable": partial_corr(df, "proxy_agency", "independent_agency", col),
            }
        )
    corr = pd.DataFrame(corr_rows).sort_values("r", key=lambda s: s.abs(), ascending=False)
    partial = pd.DataFrame(partial_rows)
    return corr, partial


def markdown_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_No rows._"
    data = df.head(max_rows).copy()
    for col in data.columns:
        if pd.api.types.is_float_dtype(data[col]):
            data[col] = data[col].map(lambda x: f"{x:.4g}" if pd.notna(x) else "")
    cols = list(data.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in data.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def save_proxy_scatter(raw: pd.DataFrame, out_dir: Path) -> None:
    colors = {"thalamus": "tab:blue", "distributed": "tab:orange"}
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.0))
    for architecture, group in raw.groupby("architecture"):
        axes[0].scatter(
            group["proxy_self_model"],
            group["independent_self_model"],
            s=55,
            alpha=0.75,
            label=architecture,
            color=colors.get(architecture),
        )
        axes[1].scatter(
            group["proxy_agency"],
            group["independent_agency"],
            s=55,
            alpha=0.75,
            label=architecture,
            color=colors.get(architecture),
        )
    for ax in axes:
        ax.plot([0, 1], [0, 1], "k--", linewidth=1.0, alpha=0.6)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.25)
    r_self = safe_corr(raw["proxy_self_model"].to_numpy(dtype=float), raw["independent_self_model"].to_numpy(dtype=float))
    r_agency = safe_corr(raw["proxy_agency"].to_numpy(dtype=float), raw["independent_agency"].to_numpy(dtype=float))
    axes[0].set_title(f"Self-model proxy vs independent tests (r={r_self:.2f})")
    axes[0].set_xlabel("Proxy self-model")
    axes[0].set_ylabel("Independent self-model")
    axes[1].set_title(f"Agency proxy vs independent tests (r={r_agency:.2f})")
    axes[1].set_xlabel("Proxy agency")
    axes[1].set_ylabel("Independent agency")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(out_dir / "proxy_vs_independent_scatter.png", dpi=180)
    plt.close(fig)


def save_agency_condition_bars(summary: pd.DataFrame, out_dir: Path) -> None:
    labels = [f"{r.architecture}\n{r.condition}" for r in summary.itertuples()]
    x = np.arange(len(summary))
    width = 0.36
    fig, ax = plt.subplots(figsize=(11.5, 5.2))
    ax.bar(x - width / 2, summary["proxy_agency"], width, label="proxy agency", color="tab:red", alpha=0.78)
    ax.bar(x + width / 2, summary["independent_agency"], width, label="independent agency", color="tab:green", alpha=0.78)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=0)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Agency: proxy vs independent behavioral tests")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "agency_proxy_vs_independent_by_condition.png", dpi=180)
    plt.close(fig)


def save_discrepancy_correlates(corr: pd.DataFrame, out_dir: Path, target: str, filename: str) -> None:
    data = corr[corr["target"] == target].copy()
    data = data.reindex(data["r"].abs().sort_values(ascending=False).index).head(12)
    if data.empty:
        return
    data = data.iloc[::-1]
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    ax.barh(data["variable"], data["r"], color=["tab:red" if v > 0 else "tab:blue" for v in data["r"]], alpha=0.82)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Correlation with discrepancy")
    ax.set_title(target.replace("_", " ").title())
    fig.tight_layout()
    fig.savefig(out_dir / filename, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose discrepancies between operational proxies and independent behavioral tests.")
    parser.add_argument("--output-root", type=Path, default=Path("runs") / "measurement_validation")
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--warmup", type=int, default=160)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed-base", type=int, default=20260521)
    parser.add_argument("--architectures", nargs="*", default=["thalamus", "distributed"], choices=["thalamus", "distributed"])
    args = parser.parse_args()

    out_dir = ensure_dir(args.output_root / f"diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    conditions = build_conditions(args.architectures)
    rows = []
    for idx, condition in enumerate(conditions):
        for seed_idx in range(args.seeds):
            rows.append(run_one(condition, args.seed_base + idx * 1000 + seed_idx, args.warmup, args.quick))
    raw = pd.DataFrame(rows)
    raw.to_csv(out_dir / "diagnostic_raw.csv", index=False)
    condition_summary = raw.groupby(["architecture", "condition"], as_index=False).agg(
        proxy_self_model=("proxy_self_model", "mean"),
        independent_self_model=("independent_self_model", "mean"),
        self_discrepancy=("self_discrepancy", "mean"),
        proxy_agency=("proxy_agency", "mean"),
        independent_agency=("independent_agency", "mean"),
        agency_discrepancy=("agency_discrepancy", "mean"),
    )
    condition_summary.to_csv(out_dir / "condition_summary.csv", index=False)
    corr, partial = correlation_tables(raw)
    corr.to_csv(out_dir / "intermediate_correlations.csv", index=False)
    partial.to_csv(out_dir / "partial_correlations.csv", index=False)

    agency_drivers = corr[corr["target"] == "agency_discrepancy"].head(12)
    self_drivers = corr[corr["target"] == "self_discrepancy"].head(12)
    save_proxy_scatter(raw, out_dir)
    save_agency_condition_bars(condition_summary, out_dir)
    save_discrepancy_correlates(corr, out_dir, "agency_discrepancy", "agency_discrepancy_correlates.png")
    save_discrepancy_correlates(corr, out_dir, "self_discrepancy", "self_discrepancy_correlates.png")
    report = [
        "# Measurement Diagnostic Report",
        "",
        "## Condition Summary",
        "",
        markdown_table(condition_summary, max_rows=20),
        "",
        "## Strongest Correlates Of Agency Discrepancy",
        "",
        markdown_table(agency_drivers, max_rows=12),
        "",
        "## Strongest Correlates Of Self Discrepancy",
        "",
        markdown_table(self_drivers, max_rows=12),
        "",
        "## Interpretation Guardrail",
        "",
        "Large discrepancy correlations are diagnostic leads, not validated mechanisms. They tell us where proxy and behavior-level tests diverge.",
    ]
    (out_dir / "diagnostic_report.md").write_text("\n".join(report), encoding="utf-8")
    summary = {
        "output_dir": str(out_dir),
        "rows": len(raw),
        "files": {
            "raw": str(out_dir / "diagnostic_raw.csv"),
            "condition_summary": str(out_dir / "condition_summary.csv"),
            "intermediate_correlations": str(out_dir / "intermediate_correlations.csv"),
            "partial_correlations": str(out_dir / "partial_correlations.csv"),
            "report": str(out_dir / "diagnostic_report.md"),
            "proxy_scatter": str(out_dir / "proxy_vs_independent_scatter.png"),
            "agency_bars": str(out_dir / "agency_proxy_vs_independent_by_condition.png"),
            "agency_discrepancy_correlates": str(out_dir / "agency_discrepancy_correlates.png"),
            "self_discrepancy_correlates": str(out_dir / "self_discrepancy_correlates.png"),
        },
    }
    write_json(out_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
