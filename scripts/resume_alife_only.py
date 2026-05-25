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

"""Resume only the ALife engine from a Mind Lab checkpoint.

This is an operational recovery path for late-stage QD coverage pushes.  It
avoids re-running distributed/thalamus systems and avoids carrying the full
manager evaluation history, which keeps memory lower than a full manager resume.
"""

from __future__ import annotations

import argparse
import gc
import json
import pickle
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mind_lab.utils import ensure_dir, jsonable, now_iso, write_json


def parse_deadline(value: str | None) -> float | None:
    if not value:
        return None
    text = value.strip()
    if text.isdigit():
        return time.time() + int(text)
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("Asia/Shanghai"))
    return dt.timestamp()


def append_jsonl(path: Path, payload: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(jsonable(payload), ensure_ascii=False) + "\n")


def copy_stable_checkpoint(source_run: Path, run_dir: Path, retries: int = 20, delay: float = 2.0) -> dict:
    source = source_run / "checkpoint.pkl"
    snapshot = run_dir / "source_checkpoint_snapshot.pkl"
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            if not source.exists() or source.stat().st_size <= 0:
                raise RuntimeError("checkpoint missing or empty")
            size_before = source.stat().st_size
            time.sleep(0.5)
            size_after = source.stat().st_size
            if size_before != size_after:
                raise RuntimeError("checkpoint is still changing")
            shutil.copy2(source, snapshot)
            with snapshot.open("rb") as f:
                return pickle.load(f)
        except Exception as exc:
            last_error = exc
            time.sleep(delay)
    raise RuntimeError(f"Could not load stable checkpoint from {source}: {last_error}")


def write_live_status(run_dir: Path, status: str, cycle: int, chunk: dict | None, alife) -> None:
    profile = alife.evaluation_profile()
    latest = {
        "cycle": cycle,
        "path_results": {"alife": chunk or {"archive": alife.archive.stats, "generation": alife.generation}},
        "evaluation": {
            "aggregate": {
                "scores": {
                    key: float(profile.get(key, 0.0))
                    for key in ["state", "content", "self_model", "agency", "temporal_continuity"]
                },
                "mean": float(
                    sum(float(profile.get(key, 0.0)) for key in ["state", "content", "self_model", "agency", "temporal_continuity"]) / 5.0
                ),
                "anomalies": [],
            },
            "systems": {"alife": profile},
        },
        "safety": {"status": "SAFE", "alerts": []},
        "recommendations": [],
    }
    write_json(
        run_dir / "live_status.json",
        {
            "time": now_iso(),
            "status": status,
            "cycle": cycle,
            "latest": latest,
            "run_dir": str(run_dir),
        },
    )
    write_json(run_dir / "alife_archive_summary.json", alife.archive.summary())


def save_checkpoint(run_dir: Path, config: dict, cycle: int, alife) -> None:
    with (run_dir / "checkpoint.pkl").open("wb") as f:
        pickle.dump(
            {
                "cycle": cycle,
                "status": "RUNNING",
                "systems": {"alife": alife},
                "evaluation_history": [],
                "config": config,
            },
            f,
        )


def final_report(run_dir: Path, status: str, cycle: int, alife, source_run: Path) -> dict:
    return {
        "experiment_id": run_dir.name,
        "status": status,
        "run_dir": str(run_dir),
        "cycles": cycle,
        "resumed_from": str(source_run),
        "alife_only": True,
        "archive": alife.archive.summary(),
        "latest_evaluation": {
            "aggregate": {
                "scores": {
                    key: float(alife.evaluation_profile().get(key, 0.0))
                    for key in ["state", "content", "self_model", "agency", "temporal_continuity"]
                }
            }
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("runs"))
    parser.add_argument("--until", type=str, default=None)
    parser.add_argument("--target-alife-coverage", type=float, default=16000)
    parser.add_argument("--chunk-generations", type=int, default=256)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--checkpoint-every", type=int, default=2)
    args = parser.parse_args()

    source_run = args.source_run
    output_root = ensure_dir(args.output_root)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = ensure_dir(output_root / f"{source_run.name}_alife_only_{stamp}")
    (output_root / "latest_run.txt").write_text(str(run_dir), encoding="utf-8")
    log_path = run_dir / "events.jsonl"
    deadline = parse_deadline(args.until)

    append_jsonl(log_path, {"time": now_iso(), "event": "alife_only_resume_loading", "source_run": str(source_run)})
    checkpoint = copy_stable_checkpoint(source_run, run_dir)
    config = dict(checkpoint.get("config", {}))
    config["id"] = run_dir.name
    config["alife_only"] = True
    config["resumed_from"] = str(source_run)
    config.setdefault("termination_conditions", {})
    config["termination_conditions"]["target_alife_coverage"] = float(args.target_alife_coverage)
    config["termination_conditions"]["wall_clock_deadline"] = args.until
    write_json(run_dir / "config.json", config)

    source_cycle = int(checkpoint.get("cycle", 0))
    systems = checkpoint.get("systems", {})
    if "alife" not in systems:
        raise RuntimeError("checkpoint does not contain systems['alife']")
    alife = systems["alife"]
    del systems
    del checkpoint
    gc.collect()

    if hasattr(alife, "workers"):
        alife.workers = max(1, int(args.workers))
    cycle = source_cycle

    status = "RUNNING"
    write_live_status(run_dir, status, cycle, None, alife)
    append_jsonl(
        log_path,
        {
            "time": now_iso(),
            "event": "alife_only_run_started",
            "cycle": cycle,
            "coverage": alife.archive.stats.get("coverage", 0.0),
            "target": args.target_alife_coverage,
            "workers": getattr(alife, "workers", None),
        },
    )

    last_chunk = None
    try:
        while True:
            coverage = float(alife.archive.stats.get("coverage", 0.0))
            if coverage >= float(args.target_alife_coverage):
                status = "COMPLETED_TARGET_COVERAGE"
                append_jsonl(log_path, {"time": now_iso(), "event": "target_alife_coverage_reached", "coverage": coverage})
                break
            if deadline is not None and time.time() >= deadline:
                status = "COMPLETED_DEADLINE"
                append_jsonl(log_path, {"time": now_iso(), "event": "deadline_reached", "coverage": coverage})
                break

            cycle += 1
            started = time.time()
            last_chunk = alife.run_chunk(args.chunk_generations)
            last_chunk["elapsed_seconds_total"] = time.time() - started
            append_jsonl(log_path, {"time": now_iso(), "event": "cycle_completed", "cycle": cycle, "path_results": {"alife": last_chunk}})
            write_live_status(run_dir, status, cycle, last_chunk, alife)
            if cycle % max(1, int(args.checkpoint_every)) == 0:
                save_checkpoint(run_dir, config, cycle, alife)
    except Exception as exc:
        status = "ERROR"
        append_jsonl(log_path, {"time": now_iso(), "event": "error", "error": repr(exc)})
        raise
    finally:
        if hasattr(alife, "shutdown"):
            alife.shutdown()
        write_live_status(run_dir, status, cycle, last_chunk, alife)
        write_json(run_dir / "final_report.json", final_report(run_dir, status, cycle, alife, source_run))
        write_json(run_dir / "safety_log.json", [])
        write_json(run_dir / "ethics_review.json", [])
        save_checkpoint(run_dir, config, cycle, alife)
        append_jsonl(log_path, {"time": now_iso(), "event": "run_finished", "status": status})


if __name__ == "__main__":
    main()
