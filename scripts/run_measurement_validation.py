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
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mind_lab.utils import ensure_dir, safe_corr, write_json
from mind_lab.validation import anonymized_id, correlation_summary, make_system, run_independent_validation, run_steps


def thalamus_conditions() -> list[dict[str, Any]]:
    base = {
        "workspace_capacity": 96,
        "initial_threshold": 0.52,
        "inhibition_strength": 0.45,
        "threshold_adaptation_rate": 0.08,
        "dim": 32,
        "measurement_window": 128,
    }
    return [
        {
            "architecture": "thalamus",
            "condition": "W-A-",
            "config": {**base, "enable_workspace": False, "enable_action_loop": False, "action_loop_variant": "none"},
        },
        {
            "architecture": "thalamus",
            "condition": "W+A-",
            "config": {**base, "enable_workspace": True, "enable_action_loop": False, "action_loop_variant": "none"},
        },
        {
            "architecture": "thalamus",
            "condition": "W-A+",
            "config": {**base, "enable_workspace": False, "enable_action_loop": True, "action_loop_variant": "learning"},
        },
        {
            "architecture": "thalamus",
            "condition": "W+A+",
            "config": {**base, "enable_workspace": True, "enable_action_loop": True, "action_loop_variant": "learning"},
        },
    ]


def distributed_conditions() -> list[dict[str, Any]]:
    base = {"num_agents": 12, "world_size": 52, "sensor_range": 6, "memory_capacity": 512, "measurement_window": 128}
    return [
        {
            "architecture": "distributed",
            "condition": "feedback_off",
            "config": {**base, "enable_action_feedback": False},
        },
        {
            "architecture": "distributed",
            "condition": "feedback_on",
            "config": {**base, "enable_action_feedback": True},
        },
    ]


def run_condition(condition: dict[str, Any], seed: int, warmup: int, quick: bool) -> dict[str, Any]:
    system = make_system(condition["architecture"], condition["config"], seed=seed)
    run_steps(system, warmup)
    validation = run_independent_validation(system, seed=seed + 100_000, quick=quick)
    proxy = validation["proxy_scores"]
    test_scores = {f"test_{item['test']}": item["score"] for item in validation["tests"]}
    test_passed = {f"pass_{item['test']}": item["passed"] for item in validation["tests"]}
    row = {
        "architecture": condition["architecture"],
        "condition": condition["condition"],
        "seed": seed,
        "proxy_state": proxy["state"],
        "proxy_content": proxy["content"],
        "proxy_self_model": proxy["self_model"],
        "proxy_agency": proxy["agency"],
        "proxy_temporal_continuity": proxy["temporal_continuity"],
        "independent_self_model": validation["independent_self_model"],
        "independent_agency": validation["independent_agency"],
        **test_scores,
        **test_passed,
    }
    return {"row": row, "validation": validation, "condition": condition}


def build_blind_exports(results: list[dict[str, Any]], out_dir: Path) -> None:
    blind_dir = ensure_dir(out_dir / "blind_exports")
    label_rows = []
    rating_rows = []
    for item in results:
        row = item["row"]
        condition = item["condition"]
        anon = anonymized_id(
            {
                "architecture": row["architecture"],
                "condition": row["condition"],
                "seed": row["seed"],
            }
        )
        payload = {
            "anonymous_id": anon,
            "behavioral_tests": [
                {
                    "test": test["test"],
                    "score": test["score"],
                    "passed": test["passed"],
                    "details": test["details"],
                }
                for test in item["validation"]["tests"]
            ],
            "rating_instructions": {
                "self_model_rating": "0-10 blind rating based only on behavior-level tests.",
                "agency_rating": "0-10 blind rating based only on behavior-level tests.",
                "do_not_use": "Do not inspect labels.csv before rating.",
            },
        }
        write_json(blind_dir / f"{anon}.json", payload)
        label_rows.append(
            {
                "anonymous_id": anon,
                "architecture": row["architecture"],
                "condition": row["condition"],
                "seed": row["seed"],
                "proxy_self_model": row["proxy_self_model"],
                "proxy_agency": row["proxy_agency"],
                "independent_self_model": row["independent_self_model"],
                "independent_agency": row["independent_agency"],
                "config": json.dumps(condition["config"], sort_keys=True),
            }
        )
        rating_rows.append({"anonymous_id": anon, "self_model_rating_0_10": "", "agency_rating_0_10": "", "notes": ""})
    pd.DataFrame(label_rows).to_csv(out_dir / "blind_labels_do_not_open_before_rating.csv", index=False)
    pd.DataFrame(rating_rows).to_csv(out_dir / "blind_rating_sheet.csv", index=False)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary = correlation_summary(rows)
    df = pd.DataFrame(rows)
    if not df.empty:
        for architecture, group in df.groupby("architecture"):
            summary[f"{architecture}_self_model_r"] = safe_corr(
                group["proxy_self_model"].to_numpy(dtype=float),
                group["independent_self_model"].to_numpy(dtype=float),
            )
            summary[f"{architecture}_agency_r"] = safe_corr(
                group["proxy_agency"].to_numpy(dtype=float),
                group["independent_agency"].to_numpy(dtype=float),
            )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run independent measurement validation and produce blind-analysis exports.")
    parser.add_argument("--output-root", type=Path, default=Path("runs") / "measurement_validation")
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--warmup", type=int, default=256)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed-base", type=int, default=20260521)
    parser.add_argument("--architectures", nargs="*", default=["thalamus", "distributed"], choices=["thalamus", "distributed"])
    args = parser.parse_args()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = ensure_dir(args.output_root / f"validation_{stamp}")
    conditions = []
    if "thalamus" in args.architectures:
        conditions.extend(thalamus_conditions())
    if "distributed" in args.architectures:
        conditions.extend(distributed_conditions())

    results = []
    rows = []
    for idx, condition in enumerate(conditions):
        for seed_idx in range(args.seeds):
            seed = args.seed_base + idx * 1000 + seed_idx
            item = run_condition(condition, seed=seed, warmup=args.warmup, quick=args.quick)
            results.append(item)
            rows.append(item["row"])

    raw_df = pd.DataFrame(rows)
    raw_df.to_csv(out_dir / "measurement_validation_raw.csv", index=False)
    grouped = raw_df.groupby(["architecture", "condition"], as_index=False).agg(
        proxy_self_model_mean=("proxy_self_model", "mean"),
        proxy_self_model_std=("proxy_self_model", "std"),
        independent_self_model_mean=("independent_self_model", "mean"),
        independent_self_model_std=("independent_self_model", "std"),
        proxy_agency_mean=("proxy_agency", "mean"),
        proxy_agency_std=("proxy_agency", "std"),
        independent_agency_mean=("independent_agency", "mean"),
        independent_agency_std=("independent_agency", "std"),
    )
    grouped.to_csv(out_dir / "measurement_validation_summary.csv", index=False)
    build_blind_exports(results, out_dir)
    summary = {
        "output_dir": str(out_dir),
        "n_rows": len(rows),
        "correlations": summarize(rows),
        "files": {
            "raw": str(out_dir / "measurement_validation_raw.csv"),
            "summary": str(out_dir / "measurement_validation_summary.csv"),
            "blind_exports": str(out_dir / "blind_exports"),
            "blind_rating_sheet": str(out_dir / "blind_rating_sheet.csv"),
            "blind_labels": str(out_dir / "blind_labels_do_not_open_before_rating.csv"),
        },
    }
    write_json(out_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
