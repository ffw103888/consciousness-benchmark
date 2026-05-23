"""Generate paper-ready statistics from the completed mechanism experiments.

The script is intentionally dependency-light: pandas, numpy, and scipy only.
It discovers the latest analysis folders, computes descriptive statistics,
paired effects, simple 2x2 OLS ANOVA tables, correlations, and Markdown/CSV
outputs suitable for drafting the Results section.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy import stats


MEASURES = ["self_model", "agency", "separation", "state", "content", "temporal_continuity", "mean_score"]


@dataclass
class EffectResult:
    experiment: str
    contrast: str
    measure: str
    comparison: str
    n_a: int
    n_b: int
    mean_a: float
    mean_b: float
    delta: float
    test: str
    statistic: float
    p_value: float
    cohens_d: float
    hedges_g: float
    ci_low: float
    ci_high: float
    interpretation: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=None, help="Run directory. Defaults to runs/latest_run.txt.")
    parser.add_argument("--root", type=Path, default=Path("runs"), help="Root containing experiment runs.")
    parser.add_argument("--bootstrap", type=int, default=5000, help="Bootstrap iterations for confidence intervals.")
    parser.add_argument("--seed", type=int, default=20260520, help="RNG seed for bootstrap resampling.")
    return parser.parse_args()


def resolve_run_dir(root: Path, run_dir: Path | None) -> Path:
    if run_dir is not None:
        return run_dir
    latest = root / "latest_run.txt"
    if latest.exists():
        text = latest.read_text(encoding="utf-8").strip()
        candidate = Path(text)
        if not candidate.is_absolute():
            candidate = root.parent / candidate
        if candidate.exists():
            return candidate
    runs = sorted(root.glob("mind_lab_night_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not runs:
        raise FileNotFoundError(f"No mind_lab_night_* runs found under {root}")
    return runs[0]


def latest_dir(analysis_root: Path, prefix: str) -> Path:
    matches = sorted(analysis_root.glob(f"{prefix}*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not matches:
        raise FileNotFoundError(f"No analysis directory matching {prefix!r} in {analysis_root}")
    return matches[0]


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def to_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin(["true", "1", "yes", "on"])


def finite(values: Iterable[float]) -> np.ndarray:
    arr = np.asarray(list(values), dtype=float)
    return arr[np.isfinite(arr)]


def bootstrap_mean_ci(values: np.ndarray, rng: np.random.Generator, n_boot: int) -> tuple[float, float]:
    values = finite(values)
    if values.size == 0:
        return math.nan, math.nan
    if values.size == 1 or np.nanstd(values) == 0:
        mean = float(np.nanmean(values))
        return mean, mean
    samples = rng.choice(values, size=(n_boot, values.size), replace=True)
    means = np.nanmean(samples, axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def bootstrap_delta_ci(
    a: np.ndarray,
    b: np.ndarray,
    rng: np.random.Generator,
    n_boot: int,
    paired: bool,
) -> tuple[float, float]:
    a = finite(a)
    b = finite(b)
    if a.size == 0 or b.size == 0:
        return math.nan, math.nan
    if paired:
        n = min(a.size, b.size)
        diffs = a[:n] - b[:n]
        if n == 1 or np.nanstd(diffs) == 0:
            delta = float(np.nanmean(diffs))
            return delta, delta
        idx = rng.integers(0, n, size=(n_boot, n))
        boot = np.nanmean(diffs[idx], axis=1)
    else:
        idx_a = rng.integers(0, a.size, size=(n_boot, a.size))
        idx_b = rng.integers(0, b.size, size=(n_boot, b.size))
        boot = np.nanmean(a[idx_a], axis=1) - np.nanmean(b[idx_b], axis=1)
    return float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def cohens_d(a: np.ndarray, b: np.ndarray, paired: bool) -> float:
    a = finite(a)
    b = finite(b)
    if a.size == 0 or b.size == 0:
        return math.nan
    if paired:
        n = min(a.size, b.size)
        diff = a[:n] - b[:n]
        sd = np.std(diff, ddof=1)
        if sd == 0:
            return 0.0 if np.mean(diff) == 0 else math.copysign(math.inf, np.mean(diff))
        return float(np.mean(diff) / sd)
    pooled_num = (a.size - 1) * np.var(a, ddof=1) + (b.size - 1) * np.var(b, ddof=1)
    pooled_den = a.size + b.size - 2
    if pooled_den <= 0:
        return math.nan
    pooled = math.sqrt(max(pooled_num / pooled_den, 0.0))
    if pooled == 0:
        delta = float(np.mean(a) - np.mean(b))
        return 0.0 if delta == 0 else math.copysign(math.inf, delta)
    return float((np.mean(a) - np.mean(b)) / pooled)


def hedges_g_from_d(d: float, n_a: int, n_b: int) -> float:
    if not np.isfinite(d):
        return d
    df = n_a + n_b - 2
    if df <= 1:
        return d
    correction = 1.0 - (3.0 / (4.0 * df - 1.0))
    return float(d * correction)


def interpret_effect_size(d: float) -> str:
    d = abs(d)
    if not np.isfinite(d):
        return "undefined"
    if d < 0.2:
        return "negligible"
    if d < 0.5:
        return "small"
    if d < 0.8:
        return "medium"
    return "large"


def paired_arrays(
    df: pd.DataFrame,
    condition_col: str,
    a_value,
    b_value,
    measure: str,
    pair_col: str,
) -> tuple[np.ndarray, np.ndarray]:
    left = df[df[condition_col] == a_value][[pair_col, measure]].rename(columns={measure: "a"})
    right = df[df[condition_col] == b_value][[pair_col, measure]].rename(columns={measure: "b"})
    merged = left.merge(right, on=pair_col, how="inner").sort_values(pair_col)
    return merged["a"].to_numpy(dtype=float), merged["b"].to_numpy(dtype=float)


def effect_contrast(
    df: pd.DataFrame,
    experiment: str,
    contrast: str,
    condition_col: str,
    a_value,
    b_value,
    measure: str,
    rng: np.random.Generator,
    n_boot: int,
    pair_col: str | None = None,
) -> EffectResult:
    paired = pair_col is not None
    if paired:
        a, b = paired_arrays(df, condition_col, a_value, b_value, measure, pair_col)
    else:
        a = df[df[condition_col] == a_value][measure].to_numpy(dtype=float)
        b = df[df[condition_col] == b_value][measure].to_numpy(dtype=float)
    a = finite(a)
    b = finite(b)
    delta = float(np.mean(a) - np.mean(b)) if a.size and b.size else math.nan
    if paired:
        statistic, p_value = stats.ttest_rel(a, b, nan_policy="omit")
        test = "paired_t"
    else:
        statistic, p_value = stats.ttest_ind(a, b, equal_var=False, nan_policy="omit")
        test = "welch_t"
    if not np.isfinite(statistic):
        statistic = math.nan
    if not np.isfinite(p_value):
        p_value = math.nan
    d = cohens_d(a, b, paired=paired)
    g = hedges_g_from_d(d, len(a), len(b))
    ci_low, ci_high = bootstrap_delta_ci(a, b, rng, n_boot, paired=paired)
    return EffectResult(
        experiment=experiment,
        contrast=contrast,
        measure=measure,
        comparison=f"{a_value} - {b_value}",
        n_a=int(len(a)),
        n_b=int(len(b)),
        mean_a=float(np.mean(a)) if a.size else math.nan,
        mean_b=float(np.mean(b)) if b.size else math.nan,
        delta=delta,
        test=test,
        statistic=float(statistic),
        p_value=float(p_value),
        cohens_d=float(d),
        hedges_g=float(g),
        ci_low=ci_low,
        ci_high=ci_high,
        interpretation=interpret_effect_size(d),
    )


def descriptives(
    df: pd.DataFrame,
    experiment: str,
    group_cols: list[str],
    measures: list[str],
    rng: np.random.Generator,
    n_boot: int,
) -> pd.DataFrame:
    rows: list[dict] = []
    available = [m for m in measures if m in df.columns]
    for keys, group in df.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        group_info = dict(zip(group_cols, keys))
        for measure in available:
            values = finite(group[measure].to_numpy(dtype=float))
            ci_low, ci_high = bootstrap_mean_ci(values, rng, n_boot)
            rows.append(
                {
                    "experiment": experiment,
                    **group_info,
                    "measure": measure,
                    "n": int(values.size),
                    "mean": float(np.mean(values)) if values.size else math.nan,
                    "std": float(np.std(values, ddof=1)) if values.size > 1 else 0.0,
                    "sem": float(stats.sem(values)) if values.size > 1 else 0.0,
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                }
            )
    return pd.DataFrame(rows)


def ols_rss(y: np.ndarray, x: np.ndarray) -> tuple[float, int]:
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    residuals = y - x @ beta
    rank = np.linalg.matrix_rank(x)
    return float(np.sum(residuals**2)), int(len(y) - rank)


def anova_2x2(df: pd.DataFrame, measure: str) -> pd.DataFrame:
    work = df.copy()
    work["workspace_num"] = to_bool(work["workspace"]).astype(float)
    work["action_num"] = to_bool(work["action_loop"]).astype(float)
    y = work[measure].to_numpy(dtype=float)
    ones = np.ones(len(work))
    w = work["workspace_num"].to_numpy()
    a = work["action_num"].to_numpy()
    wa = w * a
    x_full = np.column_stack([ones, w, a, wa])
    x_add = np.column_stack([ones, w, a])
    x_no_w = np.column_stack([ones, a])
    x_no_a = np.column_stack([ones, w])
    rss_full, df_full = ols_rss(y, x_full)
    rss_add, _ = ols_rss(y, x_add)
    rss_no_w, _ = ols_rss(y, x_no_w)
    rss_no_a, _ = ols_rss(y, x_no_a)
    mse_full = rss_full / df_full if df_full > 0 else math.nan
    terms = [
        ("workspace", rss_no_w - rss_add, 1),
        ("action_loop", rss_no_a - rss_add, 1),
        ("workspace:action_loop", rss_add - rss_full, 1),
    ]
    rows = []
    for term, ss, df_term in terms:
        ms = ss / df_term
        f_value = ms / mse_full if mse_full and mse_full > 0 else math.nan
        p_value = float(stats.f.sf(f_value, df_term, df_full)) if np.isfinite(f_value) else math.nan
        partial_eta2 = ss / (ss + rss_full) if (ss + rss_full) > 0 else math.nan
        rows.append(
            {
                "measure": measure,
                "term": term,
                "ss": float(ss),
                "df": df_term,
                "ms": float(ms),
                "F": float(f_value),
                "p_value": p_value,
                "partial_eta2": float(partial_eta2),
                "residual_df": df_full,
            }
        )
    return pd.DataFrame(rows)


def correlation_row(experiment: str, name: str, df: pd.DataFrame, x_col: str, y_col: str) -> dict:
    data = df[[x_col, y_col]].dropna()
    data = data[np.isfinite(data[x_col]) & np.isfinite(data[y_col])]
    if len(data) < 3 or data[x_col].nunique() < 2 or data[y_col].nunique() < 2:
        return {
            "experiment": experiment,
            "correlation": name,
            "x": x_col,
            "y": y_col,
            "n": int(len(data)),
            "pearson_r": math.nan,
            "pearson_p": math.nan,
            "spearman_r": math.nan,
            "spearman_p": math.nan,
        }
    pearson_r, pearson_p = stats.pearsonr(data[x_col], data[y_col])
    spearman_r, spearman_p = stats.spearmanr(data[x_col], data[y_col])
    return {
        "experiment": experiment,
        "correlation": name,
        "x": x_col,
        "y": y_col,
        "n": int(len(data)),
        "pearson_r": float(pearson_r),
        "pearson_p": float(pearson_p),
        "spearman_r": float(spearman_r),
        "spearman_p": float(spearman_p),
    }


def markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    if df.empty:
        return "_No rows._"
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda x: "" if pd.isna(x) else f"{x:.4g}")
    columns = list(display.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in display.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return "\n".join(lines)


def write_json(path: Path, payload: dict) -> None:
    def default(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
        return str(obj)

    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=default), encoding="utf-8")


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)
    run_dir = resolve_run_dir(args.root, args.run_dir)
    analysis_root = run_dir / "analysis"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = analysis_root / f"paper_statistics_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    dirs = {
        "factorial": latest_dir(analysis_root, "thalamus_factorial_timescale_"),
        "timescale": latest_dir(analysis_root, "thalamus_timescale_robust_"),
        "parameter": latest_dir(analysis_root, "thalamus_parameter_heatmap_"),
        "variants": latest_dir(analysis_root, "thalamus_action_loop_variants_"),
        "cross_arch": latest_dir(analysis_root, "cross_architecture_feedback_"),
    }

    factorial = read_csv(dirs["factorial"] / "factorial_raw.csv")
    timescale = read_csv(dirs["timescale"] / "robust_timescale_raw.csv")
    parameter = read_csv(dirs["parameter"] / "parameter_heatmap_summary.csv")
    variants = read_csv(dirs["variants"] / "action_loop_variants_raw.csv")
    cross = read_csv(dirs["cross_arch"] / "cross_architecture_feedback_raw.csv")

    desc_frames = [
        descriptives(factorial, "factorial_2x2", ["condition", "workspace", "action_loop"], MEASURES, rng, args.bootstrap),
        descriptives(variants, "action_loop_variants", ["variant"], MEASURES, rng, args.bootstrap),
        descriptives(cross, "cross_architecture", ["architecture", "condition", "action_feedback"], MEASURES, rng, args.bootstrap),
    ]
    final_step = int(timescale["steps"].max())
    timescale_final = timescale[timescale["steps"] == final_step].copy()
    desc_frames.append(descriptives(timescale_final, "timescale_final", ["condition"], MEASURES, rng, args.bootstrap))
    descriptives_df = pd.concat(desc_frames, ignore_index=True)

    effect_rows: list[EffectResult] = []
    # 2x2 mechanism contrasts.
    effect_rows.append(
        effect_contrast(
            factorial[factorial["action_loop"].astype(str).str.lower() == "false"],
            "factorial_2x2",
            "workspace_effect_without_action",
            "workspace",
            True,
            False,
            "self_model",
            rng,
            args.bootstrap,
            pair_col="seed",
        )
    )
    effect_rows.append(
        effect_contrast(
            factorial[factorial["action_loop"].astype(str).str.lower() == "true"],
            "factorial_2x2",
            "workspace_effect_with_action",
            "workspace",
            True,
            False,
            "self_model",
            rng,
            args.bootstrap,
            pair_col="seed",
        )
    )
    effect_rows.append(
        effect_contrast(
            factorial[factorial["workspace"].astype(str).str.lower() == "false"],
            "factorial_2x2",
            "action_effect_without_workspace",
            "action_loop",
            True,
            False,
            "agency",
            rng,
            args.bootstrap,
            pair_col="seed",
        )
    )
    effect_rows.append(
        effect_contrast(
            factorial[factorial["workspace"].astype(str).str.lower() == "true"],
            "factorial_2x2",
            "action_effect_with_workspace",
            "action_loop",
            True,
            False,
            "agency",
            rng,
            args.bootstrap,
            pair_col="seed",
        )
    )
    effect_rows.append(
        effect_contrast(
            factorial[factorial["workspace"].astype(str).str.lower() == "true"],
            "factorial_2x2",
            "action_reduces_separation_with_workspace",
            "action_loop",
            True,
            False,
            "separation",
            rng,
            args.bootstrap,
            pair_col="seed",
        )
    )

    # Action loop component contrasts.
    for a_value, b_value, label in [
        ("minimal", "none", "minimal_minus_none"),
        ("learning", "minimal", "learning_minus_minimal"),
        ("full", "learning", "full_minus_learning"),
        ("full", "none", "full_minus_none"),
    ]:
        effect_rows.append(
            effect_contrast(
                variants,
                "action_loop_variants",
                label,
                "variant",
                a_value,
                b_value,
                "agency",
                rng,
                args.bootstrap,
                pair_col="seed",
            )
        )
    effect_rows.append(
        effect_contrast(
            variants,
            "action_loop_variants",
            "selectivity_full_minus_none",
            "variant",
            "full",
            "none",
            "self_model",
            rng,
            args.bootstrap,
            pair_col="seed",
        )
    )

    # Cross-architecture feedback contrasts.
    for architecture in sorted(cross["architecture"].dropna().unique()):
        arch_data = cross[cross["architecture"] == architecture]
        for measure in ["agency", "self_model", "separation"]:
            effect_rows.append(
                effect_contrast(
                    arch_data,
                    "cross_architecture",
                    f"{architecture}_feedback_on_minus_off",
                    "action_feedback",
                    True,
                    False,
                    measure,
                    rng,
                    args.bootstrap,
                    pair_col="seed",
                )
            )

    effects_df = pd.DataFrame([asdict(row) for row in effect_rows])

    anova_df = pd.concat(
        [anova_2x2(factorial, measure) for measure in ["self_model", "agency", "separation"]],
        ignore_index=True,
    )

    variant_means = variants[variants["variant"] != "none"].groupby("variant", as_index=False).agg(
        agency=("agency", "mean"),
        prediction_error=("action_prediction_error", "mean"),
    )
    variant_runs = variants[variants["variant"] != "none"].rename(columns={"action_prediction_error": "prediction_error"})
    correlations_df = pd.DataFrame(
        [
            correlation_row(
                "action_loop_variants",
                "variant_means_prediction_error_vs_agency",
                variant_means,
                "prediction_error",
                "agency",
            ),
            correlation_row(
                "action_loop_variants",
                "run_level_prediction_error_vs_agency",
                variant_runs,
                "prediction_error",
                "agency",
            ),
        ]
    )

    # Parameter scan rankings.
    parameter_rank = parameter.copy()
    parameter_rank["balance_score"] = (
        parameter_rank["self_model_mean"] + parameter_rank["agency_mean"] - parameter_rank["separation_mean"].abs()
    )
    top_mean = parameter_rank.sort_values("mean_score_mean", ascending=False).head(10)
    top_balance = parameter_rank.sort_values("balance_score", ascending=False).head(10)

    # Timescale threshold summaries.
    threshold_rows = []
    for condition, group in timescale.groupby("condition"):
        for seed, seed_group in group.sort_values("steps").groupby("seed"):
            for measure, threshold in [("self_model", 0.6), ("agency", 0.45)]:
                reached = seed_group[seed_group[measure] >= threshold]
                threshold_rows.append(
                    {
                        "condition": condition,
                        "seed": seed,
                        "measure": measure,
                        "threshold": threshold,
                        "first_step": int(reached["steps"].iloc[0]) if not reached.empty else math.nan,
                    }
                )
    thresholds_df = pd.DataFrame(threshold_rows)
    threshold_summary = (
        thresholds_df.dropna(subset=["first_step"])
        .groupby(["condition", "measure"], as_index=False)
        .agg(n_reached=("first_step", "count"), mean_first_step=("first_step", "mean"), min_first_step=("first_step", "min"))
    )

    descriptives_df.to_csv(output_dir / "descriptive_statistics.csv", index=False)
    effects_df.to_csv(output_dir / "effect_sizes.csv", index=False)
    anova_df.to_csv(output_dir / "anova_2x2.csv", index=False)
    correlations_df.to_csv(output_dir / "correlations.csv", index=False)
    top_mean.to_csv(output_dir / "top_parameter_regions_by_mean_score.csv", index=False)
    top_balance.to_csv(output_dir / "top_parameter_regions_by_balance.csv", index=False)
    thresholds_df.to_csv(output_dir / "timescale_thresholds_by_seed.csv", index=False)
    threshold_summary.to_csv(output_dir / "timescale_threshold_summary.csv", index=False)

    paper_numbers = {
        "run_dir": str(run_dir),
        "analysis_dirs": {k: str(v) for k, v in dirs.items()},
        "factorial_key_effects": effects_df[effects_df["experiment"] == "factorial_2x2"].to_dict(orient="records"),
        "action_loop_key_effects": effects_df[effects_df["experiment"] == "action_loop_variants"].to_dict(orient="records"),
        "cross_architecture_key_effects": effects_df[effects_df["experiment"] == "cross_architecture"].to_dict(orient="records"),
        "correlations": correlations_df.to_dict(orient="records"),
        "top_parameter_regions_by_mean_score": top_mean.to_dict(orient="records"),
        "top_parameter_regions_by_balance": top_balance.to_dict(orient="records"),
    }
    write_json(output_dir / "paper_numbers.json", paper_numbers)

    key_desc = descriptives_df[
        (descriptives_df["measure"].isin(["self_model", "agency", "separation"]))
        & (descriptives_df["experiment"].isin(["factorial_2x2", "action_loop_variants", "cross_architecture", "timescale_final"]))
    ].copy()

    report_lines = [
        "# Paper Statistics Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Run directory: `{run_dir}`",
        "",
        "## Source Analysis Folders",
        "",
        *[f"- `{name}`: `{path}`" for name, path in dirs.items()],
        "",
        "## Key Descriptive Statistics",
        "",
        markdown_table(key_desc[["experiment", "condition", "variant", "architecture", "action_feedback", "measure", "n", "mean", "std", "ci_low", "ci_high"]].fillna(""), max_rows=80),
        "",
        "## Key Effect Sizes",
        "",
        markdown_table(
            effects_df[
                [
                    "experiment",
                    "contrast",
                    "measure",
                    "comparison",
                    "delta",
                    "ci_low",
                    "ci_high",
                    "cohens_d",
                    "hedges_g",
                    "p_value",
                    "interpretation",
                ]
            ],
            max_rows=80,
        ),
        "",
        "## 2x2 OLS ANOVA",
        "",
        markdown_table(anova_df, max_rows=40),
        "",
        "## Prediction Error Correlations",
        "",
        markdown_table(correlations_df, max_rows=20),
        "",
        "## Top Parameter Regions",
        "",
        "### By Mean Five-Dimension Score",
        "",
        markdown_table(
            top_mean[
                [
                    "capacity",
                    "inhibition",
                    "self_model_mean",
                    "agency_mean",
                    "separation_mean",
                    "mean_score_mean",
                    "balance_score",
                ]
            ],
            max_rows=10,
        ),
        "",
        "### By Balanced Self + Agency - |Separation|",
        "",
        markdown_table(
            top_balance[
                [
                    "capacity",
                    "inhibition",
                    "self_model_mean",
                    "agency_mean",
                    "separation_mean",
                    "mean_score_mean",
                    "balance_score",
                ]
            ],
            max_rows=10,
        ),
        "",
        "## Timescale Thresholds",
        "",
        "Thresholds are operational: self_model >= 0.60, agency >= 0.45.",
        "",
        markdown_table(threshold_summary, max_rows=40),
        "",
        "## Notes For Drafting",
        "",
        "- Treat all metrics as operational proxies, not direct claims about phenomenology.",
        "- For prediction-error correlations, the `none` action-loop variant is excluded because prediction error is structurally undefined there.",
        "- Cross-architecture feedback effects are paired by seed, so the reported deltas isolate the feedback manipulation more cleanly.",
    ]
    (output_dir / "paper_statistics_report.md").write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Statistics written to: {output_dir}")
    print("Key files:")
    for name in [
        "paper_statistics_report.md",
        "paper_numbers.json",
        "descriptive_statistics.csv",
        "effect_sizes.csv",
        "anova_2x2.csv",
        "correlations.csv",
        "top_parameter_regions_by_mean_score.csv",
        "top_parameter_regions_by_balance.csv",
    ]:
        print(f"  - {output_dir / name}")


if __name__ == "__main__":
    main()
