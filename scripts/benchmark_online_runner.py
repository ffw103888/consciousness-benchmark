from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from consciousness_benchmark.adapters import MindLabAdapter, all_reference_condition_sets  # noqa: E402
from consciousness_benchmark.core.stats import bootstrap_corr_ci, finite_pair, format_p, pearson  # noqa: E402


CONSTRUCT_PAIRS = {
    "action_agency": {
        "label": "Action agency",
        "proxy": "proxy_agency",
        "independent": "independent_agency",
        "mechanism": "action-outcome loop",
    },
    "boundary_self": {
        "label": "Boundary self",
        "proxy": "proxy_boundary_self",
        "independent": "independent_self_core_boundary",
        "mechanism": "workspace",
    },
    "identity_temporal_self": {
        "label": "Identity-temporal self",
        "proxy": "proxy_identity_marker_persistence",
        "independent": "test_delayed_identity_recognition",
        "mechanism": "workspace",
    },
    "action_ownership": {
        "label": "Action ownership",
        "proxy": "proxy_action_attribution",
        "independent": "test_forced_choice_ownership",
        "mechanism": "action-outcome loop",
    },
    "distributed_body_schema_self": {
        "label": "Distributed body-schema self",
        "proxy": "proxy_distributed_body_schema_self",
        "independent": "hard_self_without_lesion",
        "mechanism": "meta-monitor",
    },
}


def bootstrap_mean_ci(values: Iterable[float], rng: np.random.Generator, n_bootstrap: int) -> tuple[float, float]:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) == 0:
        return float("nan"), float("nan")
    means = [float(np.mean(arr[rng.integers(0, len(arr), len(arr))])) for _ in range(n_bootstrap)]
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def bootstrap_factor_effect_ci(groups: list[tuple[np.ndarray, np.ndarray]], rng: np.random.Generator, n_bootstrap: int) -> tuple[float, float]:
    if not groups:
        return float("nan"), float("nan")
    effects = []
    for _ in range(n_bootstrap):
        pair_effects = []
        for off, on in groups:
            off_sample = off[rng.integers(0, len(off), len(off))]
            on_sample = on[rng.integers(0, len(on), len(on))]
            pair_effects.append(float(np.mean(on_sample) - np.mean(off_sample)))
        effects.append(float(np.mean(pair_effects)))
    return float(np.percentile(effects, 2.5)), float(np.percentile(effects, 97.5))


def cohen_d_independent(a: Iterable[float], b: Iterable[float]) -> float:
    aa = np.asarray(list(a), dtype=float)
    bb = np.asarray(list(b), dtype=float)
    aa = aa[np.isfinite(aa)]
    bb = bb[np.isfinite(bb)]
    if len(aa) < 2 or len(bb) < 2:
        return float("nan")
    pooled = np.sqrt(((len(aa) - 1) * np.var(aa, ddof=1) + (len(bb) - 1) * np.var(bb, ddof=1)) / (len(aa) + len(bb) - 2))
    if pooled < 1e-12:
        return float("nan")
    return float((np.mean(aa) - np.mean(bb)) / pooled)


def select_conditions(names: list[str]) -> list[dict[str, Any]]:
    registry = all_reference_condition_sets()
    if "all" in names:
        names = list(registry.keys())
    selected = []
    for name in names:
        if name not in registry:
            raise ValueError(f"Unknown condition set: {name}. Available: {sorted(registry)}")
        for condition in registry[name]:
            selected.append({"condition_set": name, "condition": condition})
    return selected


def construct_stats(df: pd.DataFrame, *, seed: int, n_bootstrap: int) -> pd.DataFrame:
    rows = []
    for key, spec in CONSTRUCT_PAIRS.items():
        if spec["proxy"] not in df.columns or spec["independent"] not in df.columns:
            continue
        x, y = finite_pair(df[spec["proxy"]], df[spec["independent"]])
        if len(x) < 3:
            r = p = ci_low = ci_high = float("nan")
            n = int(len(x))
        else:
            r, p, n = pearson(x, y)
            ci_low, ci_high = bootstrap_corr_ci(x, y, seed=seed, n_bootstrap=n_bootstrap)
        rows.append(
            {
                "construct_key": key,
                "construct": spec["label"],
                "n": n,
                "proxy_col": spec["proxy"],
                "independent_col": spec["independent"],
                "r": r,
                "r_ci_low": ci_low,
                "r_ci_high": ci_high,
                "p": p,
                "p_formatted": format_p(p),
                "validated": bool(np.isfinite(r) and r >= 0.7),
                "mechanism": spec["mechanism"],
            }
        )
    return pd.DataFrame(rows)


def thalamus_groups(df: pd.DataFrame, value_col: str, factor: str) -> list[tuple[np.ndarray, np.ndarray]]:
    thal = df[df["architecture"] == "thalamus"]
    if factor == "workspace":
        pairs = [("W-A-", "W+A-"), ("W-A+", "W+A+")]
    elif factor == "action_loop":
        pairs = [("W-A-", "W-A+"), ("W+A-", "W+A+")]
    else:
        raise ValueError(factor)
    groups = []
    for off_cond, on_cond in pairs:
        off = thal[thal["condition"] == off_cond][value_col].to_numpy(float)
        on = thal[thal["condition"] == on_cond][value_col].to_numpy(float)
        off = off[np.isfinite(off)]
        on = on[np.isfinite(on)]
        if len(off) and len(on):
            groups.append((off, on))
    return groups


def factor_effect(groups: list[tuple[np.ndarray, np.ndarray]]) -> float:
    if not groups:
        return float("nan")
    return float(np.mean([np.mean(on) - np.mean(off) for off, on in groups]))


def mechanism_effects(df: pd.DataFrame, *, rng: np.random.Generator, n_bootstrap: int) -> pd.DataFrame:
    specs = [
        ("boundary_self", "Boundary self", "proxy_boundary_self"),
        ("identity_temporal_self", "Identity-temporal self", "proxy_identity_marker_persistence"),
        ("action_agency", "Action agency", "proxy_agency"),
        ("action_ownership", "Action ownership", "proxy_action_attribution"),
    ]
    rows = []
    for key, label, col in specs:
        if col not in df.columns:
            continue
        for factor, mechanism in [("workspace", "workspace"), ("action_loop", "action_loop")]:
            groups = thalamus_groups(df, col, factor)
            if not groups:
                continue
            off_all = np.concatenate([off for off, _on in groups]) if groups else np.array([])
            on_all = np.concatenate([on for _off, on in groups]) if groups else np.array([])
            mean_diff = factor_effect(groups)
            ci_low, ci_high = bootstrap_factor_effect_ci(groups, rng, n_bootstrap)
            p = float(stats.ttest_ind(on_all, off_all, equal_var=False).pvalue) if len(on_all) >= 2 and len(off_all) >= 2 else float("nan")
            rows.append(
                {
                    "effect_key": f"{factor}_effect_{key}",
                    "mechanism": mechanism,
                    "target_construct": label,
                    "n_off": int(len(off_all)),
                    "n_on": int(len(on_all)),
                    "mean_diff": mean_diff,
                    "mean_diff_ci_low": ci_low,
                    "mean_diff_ci_high": ci_high,
                    "independent_cohens_d": cohen_d_independent(on_all, off_all),
                    "p": p,
                    "p_formatted": format_p(p),
                }
            )
    return pd.DataFrame(rows)


def control_correlations(df: pd.DataFrame, *, seed: int, n_bootstrap: int) -> pd.DataFrame:
    specs = [
        ("meta_monitor_strength", "meta-strength", "meta_monitor_strength", "hard_self_without_lesion"),
        ("meta_monitor_noise", "meta-noise", "meta_monitor_noise", "hard_self_without_lesion"),
        ("meta_monitor_delay", "meta-delay", "meta_monitor_delay", "hard_self_without_lesion"),
    ]
    rows = []
    for key, condition_set, x_col, y_col in specs:
        if x_col not in df.columns or y_col not in df.columns:
            continue
        subset = df[df["condition_set"] == condition_set][[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna()
        if len(subset) < 3 or subset[x_col].nunique() < 2:
            continue
        r, p, n = pearson(subset[x_col], subset[y_col])
        ci_low, ci_high = bootstrap_corr_ci(subset[x_col], subset[y_col], seed=seed, n_bootstrap=n_bootstrap)
        rows.append(
            {
                "control_key": key,
                "condition_set": condition_set,
                "x_col": x_col,
                "y_col": y_col,
                "n": n,
                "r": r,
                "r_ci_low": ci_low,
                "r_ci_high": ci_high,
                "p": p,
                "p_formatted": format_p(p),
            }
        )
    return pd.DataFrame(rows)


def condition_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [
        col
        for col in df.columns
        if col not in {"architecture", "condition", "condition_set"}
        and pd.api.types.is_numeric_dtype(df[col])
    ]
    agg = {col: ["mean", "std"] for col in numeric_cols if col != "seed"}
    if not agg:
        return pd.DataFrame()
    summary = df.groupby(["condition_set", "architecture", "condition"], as_index=False).agg(agg)
    summary.columns = ["_".join([part for part in col if part]).rstrip("_") if isinstance(col, tuple) else col for col in summary.columns]
    return summary


def write_progress(out_dir: Path, rows: list[dict[str, Any]], *, completed: int, total: int, status: str) -> None:
    partial_path = out_dir / "online_benchmark_raw.partial.csv"
    progress_path = out_dir / "progress.json"
    if rows:
        pd.DataFrame(rows).to_csv(partial_path, index=False)
    payload = {
        "status": status,
        "completed": completed,
        "total": total,
        "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "partial_raw": str(partial_path),
    }
    progress_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_report(out_dir: Path, manifest: dict[str, Any], construct_df: pd.DataFrame, effect_df: pd.DataFrame, control_df: pd.DataFrame) -> None:
    lines = [
        "# Online Benchmark Run Report",
        "",
        f"Run ID: `{manifest['run_id']}`",
        f"Rows: `{manifest['row_count']}`",
        f"Condition sets: `{', '.join(manifest['condition_sets'])}`",
        f"Seeds per condition: `{manifest['seeds_per_condition']}`",
        f"Warmup: `{manifest['warmup']}`",
        f"Quick probes: `{manifest['quick']}`",
        "",
        "## Construct Validation",
        "",
    ]
    if not construct_df.empty:
        table = construct_df.copy()
        table["r_95_ci"] = table.apply(lambda r: f"{r.r:.3f} [{r.r_ci_low:.3f}, {r.r_ci_high:.3f}]", axis=1)
        lines.append(table[["construct", "n", "r_95_ci", "p_formatted", "validated", "mechanism"]].to_markdown(index=False))
    lines.extend(["", "## Mechanism Effects", ""])
    if not effect_df.empty:
        table = effect_df.copy()
        table["mean_diff_95_ci"] = table.apply(lambda r: f"{r.mean_diff:.3f} [{r.mean_diff_ci_low:.3f}, {r.mean_diff_ci_high:.3f}]", axis=1)
        lines.append(table[["mechanism", "target_construct", "n_off", "n_on", "mean_diff_95_ci", "p_formatted"]].to_markdown(index=False))
    lines.extend(["", "## Control Correlations", ""])
    if not control_df.empty:
        table = control_df.copy()
        table["r_95_ci"] = table.apply(lambda r: f"{r.r:.3f} [{r.r_ci_low:.3f}, {r.r_ci_high:.3f}]", axis=1)
        lines.append(table[["control_key", "n", "r_95_ci", "p_formatted"]].to_markdown(index=False))
    lines.append("")
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a formal online benchmark batch with manifest and frozen statistics.")
    parser.add_argument("--condition-sets", nargs="*", default=["thalamus", "distributed", "meta-strength"], help="Condition sets: thalamus, distributed, meta-strength, meta-noise, meta-delay, all")
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--warmup", type=int, default=128)
    parser.add_argument("--quick", action="store_true", help="Use fast probes; omit for slower formal probes.")
    parser.add_argument("--seed-base", type=int, default=20260521)
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "runs" / "benchmark_online")
    parser.add_argument("--save-every", type=int, default=1, help="Write partial raw data and progress every N completed rows.")
    args = parser.parse_args()

    selected = select_conditions(args.condition_sets)
    run_id = datetime.now().strftime("online_%Y%m%d_%H%M%S")
    out_dir = args.output_root / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    total_rows = len(selected) * args.seeds
    completed = 0
    write_progress(out_dir, rows, completed=completed, total=total_rows, status="running")
    for condition_idx, item in enumerate(selected):
        condition_set = item["condition_set"]
        condition = item["condition"]
        for seed_idx in range(args.seeds):
            seed = args.seed_base + condition_idx * 1000 + seed_idx
            adapter = MindLabAdapter(condition, seed=seed)
            adapter.run(args.warmup)
            row = adapter.refined_construct_row(seed=seed + 900_000, quick=args.quick)
            row["condition_set"] = condition_set
            row["run_index"] = completed
            rows.append(row)
            completed += 1
            if args.save_every > 0 and (completed % args.save_every == 0 or completed == total_rows):
                write_progress(out_dir, rows, completed=completed, total=total_rows, status="running")

    raw = pd.DataFrame(rows)
    raw_path = out_dir / "online_benchmark_raw.csv"
    raw.to_csv(raw_path, index=False)
    summary_df = condition_summary(raw)
    summary_path = out_dir / "condition_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    rng = np.random.default_rng(args.seed_base)
    construct_df = construct_stats(raw, seed=args.seed_base, n_bootstrap=args.bootstrap)
    effect_df = mechanism_effects(raw, rng=rng, n_bootstrap=args.bootstrap)
    control_df = control_correlations(raw, seed=args.seed_base, n_bootstrap=args.bootstrap)
    construct_path = out_dir / "construct_validation_stats.csv"
    effect_path = out_dir / "mechanism_effects.csv"
    control_path = out_dir / "control_correlations.csv"
    construct_df.to_csv(construct_path, index=False)
    effect_df.to_csv(effect_path, index=False)
    control_df.to_csv(control_path, index=False)

    manifest = {
        "schema_version": "benchmark-online-v1",
        "run_id": run_id,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "condition_sets": args.condition_sets,
        "conditions": [
            {
                "condition_set": item["condition_set"],
                "architecture": item["condition"].architecture,
                "condition": item["condition"].condition,
                "config": item["condition"].config,
            }
            for item in selected
        ],
        "seeds_per_condition": args.seeds,
        "seed_base": args.seed_base,
        "warmup": args.warmup,
        "quick": args.quick,
        "bootstrap": args.bootstrap,
        "row_count": int(len(raw)),
        "files": {
            "raw": str(raw_path),
            "condition_summary": str(summary_path),
            "construct_validation_stats": str(construct_path),
            "mechanism_effects": str(effect_path),
            "control_correlations": str(control_path),
            "report": str(out_dir / "report.md"),
        },
        "claim_boundary": "Operational construct validation only; not a detector of subjective consciousness.",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(out_dir, manifest, construct_df, effect_df, control_df)
    write_progress(out_dir, rows, completed=completed, total=total_rows, status="completed")
    print(json.dumps({"run_dir": str(out_dir), "row_count": len(raw), "files": manifest["files"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
