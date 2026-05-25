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
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy import stats


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PATHS = {
    "corrected_validation": PROJECT_ROOT
    / "docs"
    / "paper"
    / "statistics"
    / "reference_20260521"
    / "action_agency_raw.csv",
    "self_diagnostics": PROJECT_ROOT
    / "docs"
    / "paper"
    / "statistics"
    / "reference_20260521"
    / "boundary_self_raw.csv",
    "temporal": PROJECT_ROOT
    / "docs"
    / "paper"
    / "statistics"
    / "reference_20260521"
    / "identity_temporal_self_raw.csv",
    "ownership": PROJECT_ROOT
    / "docs"
    / "paper"
    / "statistics"
    / "reference_20260521"
    / "action_ownership_raw.csv",
    "distributed_controls": PROJECT_ROOT
    / "docs"
    / "paper"
    / "statistics"
    / "reference_20260521"
    / "distributed_body_schema_self_raw.csv",
    "figure_manifest": PROJECT_ROOT
    / "docs"
    / "paper"
    / "figures"
    / "paper_v2_20260521"
    / "manifest.json",
}


@dataclass(frozen=True)
class ConstructSpec:
    key: str
    label: str
    source: str
    proxy_col: str
    independent_col: str
    mechanism: str
    status: str = "validated"


CONSTRUCTS = [
    ConstructSpec(
        "action_agency",
        "Action agency",
        "corrected_validation",
        "proxy_agency",
        "independent_agency",
        "action-outcome loop",
    ),
    ConstructSpec(
        "boundary_self",
        "Boundary self",
        "self_diagnostics",
        "proxy_boundary_self",
        "independent_self_core_boundary",
        "workspace",
    ),
    ConstructSpec(
        "identity_temporal_self",
        "Identity-temporal self",
        "temporal",
        "proxy_identity_marker_persistence",
        "test_delayed_identity_recognition",
        "workspace",
    ),
    ConstructSpec(
        "action_ownership",
        "Action ownership",
        "ownership",
        "proxy_action_attribution",
        "test_forced_choice_ownership",
        "action-outcome loop",
    ),
    ConstructSpec(
        "distributed_body_schema_self",
        "Distributed body-schema self",
        "distributed_controls",
        "proxy_self_model",
        "hard_self_without_lesion",
        "meta-monitor",
    ),
]


EXPECTED_NUMBERS = {
    "action_agency_r": 0.873878,
    "boundary_self_r": 0.939760,
    "identity_temporal_self_r": 0.850324,
    "action_ownership_r": 0.995879,
    "distributed_body_schema_self_r": 0.923722,
    "workspace_effect_boundary_self": 0.467892,
    "workspace_effect_identity_temporal_self": 0.253548,
    "workspace_effect_action_agency": -0.001056,
    "workspace_effect_action_ownership": 0.000070,
    "action_effect_boundary_self": -0.045256,
    "action_effect_identity_temporal_self": 0.013087,
    "action_effect_action_agency": 0.711341,
    "action_effect_action_ownership": 0.968047,
    "meta_monitor_strength_r": 0.886760,
    "meta_monitor_noise_r": -0.973999,
}


def read_csv(key: str) -> pd.DataFrame:
    path = PATHS[key]
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def finite_pair(x: Iterable[float], y: Iterable[float]) -> tuple[np.ndarray, np.ndarray]:
    x_arr = np.asarray(list(x), dtype=float)
    y_arr = np.asarray(list(y), dtype=float)
    mask = np.isfinite(x_arr) & np.isfinite(y_arr)
    return x_arr[mask], y_arr[mask]


def pearson_r(x: Iterable[float], y: Iterable[float]) -> float:
    x_arr, y_arr = finite_pair(x, y)
    if len(x_arr) < 3 or np.std(x_arr) < 1e-12 or np.std(y_arr) < 1e-12:
        return float("nan")
    return float(stats.pearsonr(x_arr, y_arr).statistic)


def pearson_p(x: Iterable[float], y: Iterable[float]) -> float:
    x_arr, y_arr = finite_pair(x, y)
    if len(x_arr) < 3 or np.std(x_arr) < 1e-12 or np.std(y_arr) < 1e-12:
        return float("nan")
    return float(stats.pearsonr(x_arr, y_arr).pvalue)


def bootstrap_corr_ci(
    x: Iterable[float],
    y: Iterable[float],
    rng: np.random.Generator,
    n_bootstrap: int,
    alpha: float = 0.05,
) -> tuple[float, float]:
    x_arr, y_arr = finite_pair(x, y)
    if len(x_arr) < 3:
        return float("nan"), float("nan")
    rs: list[float] = []
    n = len(x_arr)
    attempts = 0
    max_attempts = n_bootstrap * 4
    while len(rs) < n_bootstrap and attempts < max_attempts:
        attempts += 1
        idx = rng.integers(0, n, n)
        x_sample = x_arr[idx]
        y_sample = y_arr[idx]
        if np.std(x_sample) < 1e-12 or np.std(y_sample) < 1e-12:
            continue
        rs.append(float(stats.pearsonr(x_sample, y_sample).statistic))
    if not rs:
        return float("nan"), float("nan")
    return (
        float(np.percentile(rs, 100 * alpha / 2)),
        float(np.percentile(rs, 100 * (1 - alpha / 2))),
    )


def bootstrap_mean_ci(
    values: Iterable[float],
    rng: np.random.Generator,
    n_bootstrap: int,
    alpha: float = 0.05,
) -> tuple[float, float]:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) == 0:
        return float("nan"), float("nan")
    means = [float(np.mean(arr[rng.integers(0, len(arr), len(arr))])) for _ in range(n_bootstrap)]
    return (
        float(np.percentile(means, 100 * alpha / 2)),
        float(np.percentile(means, 100 * (1 - alpha / 2))),
    )


def cohen_d_independent(group_a: Iterable[float], group_b: Iterable[float]) -> float:
    a = np.asarray(list(group_a), dtype=float)
    b = np.asarray(list(group_b), dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    pooled = math.sqrt(((len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1)) / (len(a) + len(b) - 2))
    if pooled < 1e-12:
        return float("nan")
    return float((np.mean(a) - np.mean(b)) / pooled)


def cohen_d_paired(diffs: Iterable[float]) -> float:
    arr = np.asarray(list(diffs), dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) < 2 or np.std(arr, ddof=1) < 1e-12:
        return float("nan")
    return float(np.mean(arr) / np.std(arr, ddof=1))


def format_p(p: float) -> str:
    if not np.isfinite(p):
        return "NA"
    if p < 1e-9:
        return "<1e-9"
    if p < 1e-4:
        return f"{p:.1e}"
    return f"{p:.4f}"


def get_dataframes() -> dict[str, pd.DataFrame]:
    return {key: read_csv(key) for key in PATHS if key != "figure_manifest"}


def compute_construct_stats(
    data: dict[str, pd.DataFrame],
    rng: np.random.Generator,
    n_bootstrap: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for spec in CONSTRUCTS:
        df = data[spec.source]
        x = df[spec.proxy_col]
        y = df[spec.independent_col]
        r = pearson_r(x, y)
        p = pearson_p(x, y)
        ci_low, ci_high = bootstrap_corr_ci(x, y, rng, n_bootstrap)
        rows.append(
            {
                "construct_key": spec.key,
                "construct": spec.label,
                "n": int(np.isfinite(df[spec.proxy_col]).sum()),
                "proxy_col": spec.proxy_col,
                "independent_col": spec.independent_col,
                "r": r,
                "r_ci_low": ci_low,
                "r_ci_high": ci_high,
                "p": p,
                "p_formatted": format_p(p),
                "mechanism": spec.mechanism,
                "status": spec.status,
            }
        )
    return pd.DataFrame(rows)


def thalamus_condition_diffs(df: pd.DataFrame, value_col: str, factor: str) -> np.ndarray:
    thal = df[df["architecture"] == "thalamus"].copy()
    if thal.empty:
        return np.array([], dtype=float)
    pairs: list[tuple[str, str]]
    if factor == "workspace":
        pairs = [("W-A-", "W+A-"), ("W-A+", "W+A+")]
    elif factor == "action_loop":
        pairs = [("W-A-", "W-A+"), ("W+A-", "W+A+")]
    else:
        raise ValueError(f"unknown factor: {factor}")

    diffs: list[float] = []
    for seed in sorted(thal["seed"].dropna().unique()):
        seed_df = thal[thal["seed"] == seed]
        for off_cond, on_cond in pairs:
            off = seed_df[seed_df["condition"] == off_cond][value_col]
            on = seed_df[seed_df["condition"] == on_cond][value_col]
            if len(off) and len(on):
                diffs.append(float(on.mean() - off.mean()))
    return np.asarray(diffs, dtype=float)


def thalamus_condition_groups(df: pd.DataFrame, value_col: str, factor: str) -> list[tuple[np.ndarray, np.ndarray]]:
    thal = df[df["architecture"] == "thalamus"].copy()
    if thal.empty:
        return []
    if factor == "workspace":
        pairs = [("W-A-", "W+A-"), ("W-A+", "W+A+")]
    elif factor == "action_loop":
        pairs = [("W-A-", "W-A+"), ("W+A-", "W+A+")]
    else:
        raise ValueError(f"unknown factor: {factor}")

    groups: list[tuple[np.ndarray, np.ndarray]] = []
    for off_cond, on_cond in pairs:
        off = thal[thal["condition"] == off_cond][value_col].to_numpy(float)
        on = thal[thal["condition"] == on_cond][value_col].to_numpy(float)
        off = off[np.isfinite(off)]
        on = on[np.isfinite(on)]
        if len(off) and len(on):
            groups.append((off, on))
    return groups


def mean_factor_effect(groups: list[tuple[np.ndarray, np.ndarray]]) -> float:
    effects = [float(np.mean(on) - np.mean(off)) for off, on in groups if len(off) and len(on)]
    return float(np.mean(effects)) if effects else float("nan")


def bootstrap_factor_effect_ci(
    groups: list[tuple[np.ndarray, np.ndarray]],
    rng: np.random.Generator,
    n_bootstrap: int,
    alpha: float = 0.05,
) -> tuple[float, float]:
    if not groups:
        return float("nan"), float("nan")
    effects: list[float] = []
    for _ in range(n_bootstrap):
        pair_effects: list[float] = []
        for off, on in groups:
            off_sample = off[rng.integers(0, len(off), len(off))]
            on_sample = on[rng.integers(0, len(on), len(on))]
            pair_effects.append(float(np.mean(on_sample) - np.mean(off_sample)))
        effects.append(float(np.mean(pair_effects)))
    return (
        float(np.percentile(effects, 100 * alpha / 2)),
        float(np.percentile(effects, 100 * (1 - alpha / 2))),
    )


def condition_effect_row(
    mechanism: str,
    target: str,
    groups: list[tuple[np.ndarray, np.ndarray]],
    rng: np.random.Generator,
    n_bootstrap: int,
) -> dict[str, Any]:
    off_all = np.concatenate([off for off, _on in groups]) if groups else np.array([], dtype=float)
    on_all = np.concatenate([on for _off, on in groups]) if groups else np.array([], dtype=float)
    mean_diff = mean_factor_effect(groups)
    ci_low, ci_high = bootstrap_factor_effect_ci(groups, rng, n_bootstrap)
    d = cohen_d_independent(on_all, off_all)
    p = float(stats.ttest_ind(on_all, off_all, equal_var=False).pvalue) if len(off_all) >= 2 and len(on_all) >= 2 else float("nan")
    return {
        "mechanism": mechanism,
        "target_construct": target,
        "n_paired_diffs": int(0),
        "n_off": int(len(off_all)),
        "n_on": int(len(on_all)),
        "mean_diff": mean_diff,
        "mean_diff_ci_low": ci_low,
        "mean_diff_ci_high": ci_high,
        "paired_cohens_dz": float("nan"),
        "independent_cohens_d": d,
        "p": p,
        "p_formatted": format_p(p),
    }


def compute_mechanism_effects(
    data: dict[str, pd.DataFrame],
    rng: np.random.Generator,
    n_bootstrap: int,
) -> pd.DataFrame:
    specs = [
        ("boundary_self", "Boundary self", data["self_diagnostics"], "proxy_boundary_self"),
        ("identity_temporal_self", "Identity-temporal self", data["temporal"], "proxy_identity_marker_persistence"),
        ("action_agency", "Action agency", data["corrected_validation"], "proxy_agency"),
        ("action_ownership", "Action ownership", data["ownership"], "proxy_action_attribution"),
    ]
    rows: list[dict[str, Any]] = []
    for key, label, df, col in specs:
        rows.append(condition_effect_row("workspace", label, thalamus_condition_groups(df, col, "workspace"), rng, n_bootstrap))
        rows[-1]["effect_key"] = f"workspace_effect_{key}"
        rows.append(condition_effect_row("action_loop", label, thalamus_condition_groups(df, col, "action_loop"), rng, n_bootstrap))
        rows[-1]["effect_key"] = f"action_effect_{key}"

    dist = data["distributed_controls"]
    strength = dist[dist["control_type"] == "strength"]
    low = strength[strength["meta_monitor_strength"] == strength["meta_monitor_strength"].min()]["hard_self_without_lesion"]
    high = strength[strength["meta_monitor_strength"] == strength["meta_monitor_strength"].max()]["hard_self_without_lesion"]
    rows.append(
        {
            "effect_key": "meta_monitor_strength_high_minus_low",
            "mechanism": "meta_monitor_strength",
            "target_construct": "Distributed body-schema self",
            "n_paired_diffs": int(len(low) + len(high)),
            "n_off": int(len(low)),
            "n_on": int(len(high)),
            "mean_diff": float(high.mean() - low.mean()),
            "mean_diff_ci_low": float("nan"),
            "mean_diff_ci_high": float("nan"),
            "paired_cohens_dz": float("nan"),
            "independent_cohens_d": cohen_d_independent(high, low),
            "p": float(stats.ttest_ind(high, low, equal_var=False).pvalue) if len(low) >= 2 and len(high) >= 2 else float("nan"),
            "p_formatted": format_p(float(stats.ttest_ind(high, low, equal_var=False).pvalue)) if len(low) >= 2 and len(high) >= 2 else "NA",
        }
    )
    return pd.DataFrame(rows)


def compute_control_correlations(
    data: dict[str, pd.DataFrame],
    rng: np.random.Generator,
    n_bootstrap: int,
) -> pd.DataFrame:
    dist = data["distributed_controls"]
    specs = [
        ("meta_monitor_strength", "strength", "meta_monitor_strength", "hard_self_without_lesion"),
        ("meta_monitor_noise", "noise", "meta_monitor_noise", "hard_self_without_lesion"),
        ("meta_monitor_delay", "delay", "meta_monitor_delay", "hard_self_without_lesion"),
    ]
    rows: list[dict[str, Any]] = []
    for key, control_type, x_col, y_col in specs:
        subset = dist[dist["control_type"] == control_type]
        r = pearson_r(subset[x_col], subset[y_col])
        p = pearson_p(subset[x_col], subset[y_col])
        ci_low, ci_high = bootstrap_corr_ci(subset[x_col], subset[y_col], rng, n_bootstrap)
        rows.append(
            {
                "control_key": key,
                "control_type": control_type,
                "x_col": x_col,
                "y_col": y_col,
                "n": int(len(subset)),
                "r": r,
                "r_ci_low": ci_low,
                "r_ci_high": ci_high,
                "p": p,
                "p_formatted": format_p(p),
            }
        )
    return pd.DataFrame(rows)


def compute_number_consistency(
    construct_stats: pd.DataFrame,
    mechanism_effects: pd.DataFrame,
    control_stats: pd.DataFrame,
) -> pd.DataFrame:
    computed = {
        f"{row.construct_key}_r": float(row.r)
        for row in construct_stats.itertuples(index=False)
    }
    computed.update(
        {
            row.effect_key: float(row.mean_diff)
            for row in mechanism_effects.itertuples(index=False)
            if str(row.effect_key).startswith(("workspace_effect_", "action_effect_"))
        }
    )
    computed.update({f"{row.control_key}_r": float(row.r) for row in control_stats.itertuples(index=False)})

    rows = []
    for key, expected in EXPECTED_NUMBERS.items():
        actual = computed.get(key, float("nan"))
        diff = abs(actual - expected) if np.isfinite(actual) else float("nan")
        rows.append(
            {
                "number_key": key,
                "expected": expected,
                "computed": actual,
                "abs_diff": diff,
                "ok": bool(np.isfinite(diff) and diff <= 0.01),
            }
        )
    return pd.DataFrame(rows)


def as_markdown_table(df: pd.DataFrame, cols: list[str]) -> str:
    return df[cols].to_markdown(index=False)


def write_tables(
    out_dir: Path,
    construct_stats: pd.DataFrame,
    mechanism_effects: pd.DataFrame,
    control_stats: pd.DataFrame,
) -> None:
    table1 = construct_stats.copy()
    table1["r_95_ci"] = table1.apply(lambda r: f"{r.r:.3f} [{r.r_ci_low:.3f}, {r.r_ci_high:.3f}]", axis=1)
    table1_md = as_markdown_table(
        table1,
        ["construct", "n", "r_95_ci", "p_formatted", "mechanism", "status"],
    )
    (out_dir / "table1_validation_status.md").write_text(table1_md + "\n", encoding="utf-8")
    table1.to_latex(out_dir / "table1_validation_status.tex", index=False, float_format="%.3f")

    table2 = mechanism_effects.copy()
    table2["mean_diff_95_ci"] = table2.apply(
        lambda r: f"{r.mean_diff:.3f} [{r.mean_diff_ci_low:.3f}, {r.mean_diff_ci_high:.3f}]"
        if np.isfinite(r.mean_diff_ci_low)
        else f"{r.mean_diff:.3f}",
        axis=1,
    )
    table2_md = as_markdown_table(
        table2,
        ["mechanism", "target_construct", "n_off", "n_on", "mean_diff_95_ci", "independent_cohens_d", "p_formatted"],
    )
    (out_dir / "table2_mechanism_effects.md").write_text(table2_md + "\n", encoding="utf-8")
    table2.to_latex(out_dir / "table2_mechanism_effects.tex", index=False, float_format="%.3f")

    table3 = control_stats.copy()
    table3["r_95_ci"] = table3.apply(lambda r: f"{r.r:.3f} [{r.r_ci_low:.3f}, {r.r_ci_high:.3f}]", axis=1)
    table3_md = as_markdown_table(table3, ["control_type", "n", "r_95_ci", "p_formatted"])
    (out_dir / "table3_distributed_controls.md").write_text(table3_md + "\n", encoding="utf-8")
    table3.to_latex(out_dir / "table3_distributed_controls.tex", index=False, float_format="%.3f")


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze final paper statistics with bootstrap CIs and consistency checks.")
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260521)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "paper" / "statistics" / "final_20260521",
    )
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    data = get_dataframes()

    construct_stats = compute_construct_stats(data, rng, args.bootstrap)
    mechanism_effects = compute_mechanism_effects(data, rng, args.bootstrap)
    control_stats = compute_control_correlations(data, rng, args.bootstrap)
    consistency = compute_number_consistency(construct_stats, mechanism_effects, control_stats)

    construct_stats.to_csv(args.out_dir / "construct_validation_stats.csv", index=False)
    mechanism_effects.to_csv(args.out_dir / "mechanism_effects.csv", index=False)
    control_stats.to_csv(args.out_dir / "distributed_control_correlations.csv", index=False)
    consistency.to_csv(args.out_dir / "number_consistency.csv", index=False)
    write_tables(args.out_dir, construct_stats, mechanism_effects, control_stats)

    payload = {
        "bootstrap": args.bootstrap,
        "seed": args.seed,
        "paths": {key: str(path.relative_to(PROJECT_ROOT)) for key, path in PATHS.items()},
        "construct_validation": construct_stats.to_dict(orient="records"),
        "mechanism_effects": mechanism_effects.to_dict(orient="records"),
        "distributed_controls": control_stats.to_dict(orient="records"),
        "number_consistency": consistency.to_dict(orient="records"),
        "all_numbers_consistent": bool(consistency["ok"].all()),
    }
    (args.out_dir / "final_statistics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved final statistics to {args.out_dir}")
    print("\nConstruct validation:")
    print(construct_stats[["construct", "n", "r", "r_ci_low", "r_ci_high", "p_formatted"]].to_string(index=False))
    print("\nNumber consistency:")
    print(consistency[["number_key", "expected", "computed", "abs_diff", "ok"]].to_string(index=False))
    if not consistency["ok"].all():
        print("\nWARNING: Some expected numbers differ by more than 0.01.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
