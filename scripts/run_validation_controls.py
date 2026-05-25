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
import copy
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mind_lab.thalamus import ThalamusInspiredArchitecture
from mind_lab.utils import ensure_dir, write_json
from mind_lab.validation import evaluation_scores, run_independent_validation, run_steps


def thalamus_base() -> dict[str, Any]:
    return {
        "workspace_capacity": 96,
        "initial_threshold": 0.52,
        "inhibition_strength": 0.45,
        "threshold_adaptation_rate": 0.08,
        "dim": 32,
        "measurement_window": 128,
        "enable_reticular": True,
        "enable_core": True,
        "enable_matrix": True,
        "enable_cortical_feedback": True,
    }


def approx_complexity(config: dict[str, Any]) -> dict[str, float]:
    dim = int(config.get("dim", 32))
    workspace = int(config.get("workspace_capacity", 0)) if config.get("enable_workspace", True) else 0
    cortical_modules = 3 if config.get("enable_cortical_feedback", True) else 0
    action_loop = 1 if config.get("enable_action_loop", False) and config.get("action_loop_variant", "none") != "none" else 0
    return {
        "dim": float(dim),
        "workspace_capacity": float(workspace),
        "cortical_param_proxy": float(cortical_modules * dim * dim),
        "action_loop_param_proxy": float(action_loop * dim * dim),
        "total_param_proxy": float(cortical_modules * dim * dim + action_loop * dim * dim + workspace * dim),
    }


def condition_row(name: str, config: dict[str, Any], seed: int, warmup: int, quick: bool) -> dict[str, Any]:
    system = ThalamusInspiredArchitecture(config, seed=seed)
    run_steps(system, warmup)
    validation = run_independent_validation(system, seed=seed + 900_000, quick=quick)
    scores = evaluation_scores(system)
    return {
        "condition": name,
        "seed": seed,
        **{f"proxy_{k}": v for k, v in scores.items()},
        "independent_self_model": validation["independent_self_model"],
        "independent_agency": validation["independent_agency"],
        **approx_complexity(config),
    }


def dose_response(seed_base: int, warmup: int, quick: bool) -> pd.DataFrame:
    rows = []
    base = thalamus_base()
    capacities = [0, 32, 96, 192, 384]
    for idx, capacity in enumerate(capacities):
        config = {
            **base,
            "enable_workspace": capacity > 0,
            "workspace_capacity": max(capacity, 1),
            "enable_action_loop": False,
            "action_loop_variant": "none",
        }
        row = condition_row(f"workspace_capacity_{capacity}", config, seed_base + idx, warmup, quick)
        row["control_family"] = "workspace_dose"
        row["dose"] = capacity
        rows.append(row)

    variants = ["none", "minimal", "learning", "full"]
    for idx, variant in enumerate(variants):
        config = {
            **base,
            "enable_workspace": False,
            "workspace_capacity": 1,
            "enable_action_loop": variant != "none",
            "action_loop_variant": variant,
        }
        row = condition_row(f"action_loop_{variant}", config, seed_base + 100 + idx, warmup, quick)
        row["control_family"] = "action_loop_dose"
        row["dose"] = idx
        rows.append(row)
    return pd.DataFrame(rows)


def lesion_recovery(seed_base: int, warmup: int, quick: bool) -> pd.DataFrame:
    base = {
        **thalamus_base(),
        "enable_workspace": True,
        "enable_action_loop": True,
        "action_loop_variant": "learning",
    }
    system = ThalamusInspiredArchitecture(base, seed=seed_base)
    run_steps(system, warmup)
    rows = []

    baseline_validation = run_independent_validation(copy.deepcopy(system), seed=seed_base + 1, quick=quick)
    rows.append(
        {
            "phase": "baseline",
            **{f"proxy_{k}": v for k, v in evaluation_scores(system).items()},
            "independent_self_model": baseline_validation["independent_self_model"],
            "independent_agency": baseline_validation["independent_agency"],
        }
    )

    workspace_lesion = copy.deepcopy(system)
    workspace_lesion.enable_workspace = False
    workspace_lesion.workspace.contents = []
    run_steps(workspace_lesion, 80 if quick else 192)
    val = run_independent_validation(workspace_lesion, seed=seed_base + 2, quick=quick)
    rows.append(
        {
            "phase": "workspace_lesion",
            **{f"proxy_{k}": v for k, v in evaluation_scores(workspace_lesion).items()},
            "independent_self_model": val["independent_self_model"],
            "independent_agency": val["independent_agency"],
        }
    )

    workspace_recovery = copy.deepcopy(workspace_lesion)
    workspace_recovery.enable_workspace = True
    run_steps(workspace_recovery, 80 if quick else 192)
    val = run_independent_validation(workspace_recovery, seed=seed_base + 3, quick=quick)
    rows.append(
        {
            "phase": "workspace_recovery",
            **{f"proxy_{k}": v for k, v in evaluation_scores(workspace_recovery).items()},
            "independent_self_model": val["independent_self_model"],
            "independent_agency": val["independent_agency"],
        }
    )

    action_lesion = copy.deepcopy(system)
    action_lesion.enable_action_loop = False
    action_lesion.action_loop = None
    run_steps(action_lesion, 80 if quick else 192)
    val = run_independent_validation(action_lesion, seed=seed_base + 4, quick=quick)
    rows.append(
        {
            "phase": "action_loop_lesion",
            **{f"proxy_{k}": v for k, v in evaluation_scores(action_lesion).items()},
            "independent_self_model": val["independent_self_model"],
            "independent_agency": val["independent_agency"],
        }
    )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run alternative-explanation controls for measurement validation.")
    parser.add_argument("--output-root", type=Path, default=Path("runs") / "measurement_validation")
    parser.add_argument("--warmup", type=int, default=256)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed-base", type=int, default=20260521)
    args = parser.parse_args()

    out_dir = ensure_dir(args.output_root / f"controls_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    dose = dose_response(args.seed_base, args.warmup, args.quick)
    lesion = lesion_recovery(args.seed_base + 10_000, args.warmup, args.quick)
    dose.to_csv(out_dir / "dose_response_controls.csv", index=False)
    lesion.to_csv(out_dir / "lesion_recovery_controls.csv", index=False)
    summary = {
        "output_dir": str(out_dir),
        "dose_response_rows": len(dose),
        "lesion_recovery_rows": len(lesion),
        "files": {
            "dose_response": str(out_dir / "dose_response_controls.csv"),
            "lesion_recovery": str(out_dir / "lesion_recovery_controls.csv"),
        },
        "notes": [
            "Complexity values are approximate implementation proxies, not final parameter-matched controls.",
            "This script is the first executable control layer; stricter matching should follow if results depend on complexity.",
        ],
    }
    write_json(out_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
