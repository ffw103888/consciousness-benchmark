from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from consciousness_benchmark.adapters import (  # noqa: E402
    MindLabAdapter,
    distributed_reference_conditions,
    legacy_smoke_meta_monitor_strength_conditions,
    thalamus_reference_conditions,
)
from consciousness_benchmark.core.stats import pearson  # noqa: E402


def safe_corr_df(df: pd.DataFrame, x_col: str, y_col: str) -> float:
    subset = df[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(subset) < 3:
        return float("nan")
    r, _p, _n = pearson(subset[x_col], subset[y_col])
    return r


def summarize(df: pd.DataFrame) -> dict[str, Any]:
    pairs = {
        "action_agency_r": ("proxy_agency", "independent_agency"),
        "boundary_self_r": ("proxy_boundary_self", "independent_self_core_boundary"),
        "identity_temporal_self_r": ("proxy_identity_marker_persistence", "test_delayed_identity_recognition"),
        "action_ownership_r": ("proxy_action_attribution", "test_forced_choice_ownership"),
        "distributed_body_schema_self_r": ("proxy_distributed_body_schema_self", "hard_self_without_lesion"),
    }
    out: dict[str, Any] = {"n_rows": int(len(df))}
    for key, (x_col, y_col) in pairs.items():
        if x_col in df.columns and y_col in df.columns:
            out[key] = safe_corr_df(df, x_col, y_col)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a small online smoke test through the MindLab benchmark adapter.")
    parser.add_argument("--seeds", type=int, default=2)
    parser.add_argument("--warmup", type=int, default=96)
    parser.add_argument("--quick", action="store_true", default=True)
    parser.add_argument("--seed-base", type=int, default=20260521)
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "runs" / "benchmark_mvp")
    args = parser.parse_args()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.output_root / f"mind_lab_smoke_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    conditions = [
        *thalamus_reference_conditions(),
        *distributed_reference_conditions(),
        *legacy_smoke_meta_monitor_strength_conditions(),
    ]
    rows: list[dict[str, Any]] = []
    for condition_idx, condition in enumerate(conditions):
        for seed_idx in range(args.seeds):
            seed = args.seed_base + condition_idx * 1000 + seed_idx
            adapter = MindLabAdapter(condition, seed=seed)
            adapter.run(args.warmup)
            rows.append(adapter.refined_construct_row(seed=seed + 900_000, quick=args.quick))

    df = pd.DataFrame(rows)
    raw_path = out_dir / "mind_lab_adapter_smoke_raw.csv"
    df.to_csv(raw_path, index=False)
    summary = {
        "output_dir": str(out_dir),
        "raw": str(raw_path),
        "seeds": args.seeds,
        "warmup": args.warmup,
        "quick": args.quick,
        "correlations": summarize(df),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    report = [
        "# MindLab Adapter Smoke Report",
        "",
        f"Rows: `{len(df)}`",
        f"Warmup: `{args.warmup}`",
        "",
        "## Correlations",
        "",
        pd.DataFrame([summary["correlations"]]).T.rename(columns={0: "r"}).to_markdown(),
        "",
    ]
    (out_dir / "report.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
