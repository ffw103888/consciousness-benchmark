"""Resume a long experiment from a saved checkpoint.

This is meant for extending a run that has a fixed in-memory deadline.  It can
wait for the original process to exit, copy a stable checkpoint, and continue in
a fresh run directory with a new wall-clock deadline and/or coverage target.
"""

from __future__ import annotations

import argparse
import json
import pickle
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mind_lab.manager import ExperimentManager
from mind_lab.utils import ensure_dir, write_json


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


def pid_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f"$p = Get-Process -Id {pid} -ErrorAction SilentlyContinue; if ($p) {{ '1' }} else {{ '0' }}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() == "1"


def live_status(source_run: Path) -> str | None:
    path = source_run / "live_status.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("status")
    except Exception:
        return None


def wait_for_source_to_finish(source_run: Path, watch_pid: int | None, poll_seconds: int) -> None:
    while True:
        status = live_status(source_run)
        process_alive = pid_exists(watch_pid) if watch_pid else False
        if status and status != "RUNNING":
            return
        if watch_pid and not process_alive:
            return
        time.sleep(poll_seconds)


def copy_stable_checkpoint(source_run: Path, target_dir: Path, retries: int = 20, delay: float = 3.0) -> dict:
    source = source_run / "checkpoint.pkl"
    snapshot = target_dir / "source_checkpoint_snapshot.pkl"
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            if not source.exists() or source.stat().st_size <= 0:
                raise RuntimeError("checkpoint missing or empty")
            size_before = source.stat().st_size
            time.sleep(0.5)
            size_after = source.stat().st_size
            if size_before != size_after:
                raise RuntimeError("checkpoint size is still changing")
            shutil.copy2(source, snapshot)
            with snapshot.open("rb") as f:
                return pickle.load(f)
        except Exception as exc:  # pragma: no cover - operational retry path
            last_error = exc
            time.sleep(delay)
    raise RuntimeError(f"Could not load a stable checkpoint from {source}: {last_error}")


def resume_checkpoint(
    checkpoint: dict,
    output_root: Path,
    source_run: Path,
    until: str | None,
    target_alife_coverage: float | None,
) -> dict:
    config = checkpoint["config"]
    source_id = str(config.get("id", source_run.name))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    config = dict(config)
    config["id"] = f"{source_id}_extended_{stamp}"
    config["resumed_from"] = str(source_run)
    config.setdefault("termination_conditions", {})
    if until:
        config["termination_conditions"]["wall_clock_deadline"] = until
    if target_alife_coverage is not None:
        config["termination_conditions"]["target_alife_coverage"] = float(target_alife_coverage)

    run_dir = ensure_dir(output_root / config["id"])
    write_json(run_dir / "config.json", config)
    manager = ExperimentManager(config, run_dir)
    manager.systems = checkpoint["systems"]
    manager.evaluation_history = checkpoint.get("evaluation_history", [])
    manager.cycle = int(checkpoint.get("cycle", 0))
    manager.status = "RUNNING"
    manager.config = config
    manager.logger.event(
        "resumed_from_checkpoint",
        source_run=str(source_run),
        source_cycle=manager.cycle,
        target_alife_coverage=target_alife_coverage,
        until=until,
    )
    deadline_epoch = parse_deadline(until)
    latest_path = output_root / "latest_run.txt"
    latest_path.write_text(str(run_dir), encoding="utf-8")
    report = manager.run(deadline_epoch=deadline_epoch)
    latest_path.write_text(str(report.get("run_dir", run_dir)), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("runs"))
    parser.add_argument("--until", type=str, default=None)
    parser.add_argument("--target-alife-coverage", type=float, default=None)
    parser.add_argument("--watch-pid", type=int, default=None)
    parser.add_argument("--poll-seconds", type=int, default=30)
    parser.add_argument("--no-wait", action="store_true")
    args = parser.parse_args()

    source_run = args.source_run
    output_root = ensure_dir(args.output_root)
    if not args.no_wait:
        wait_for_source_to_finish(source_run, args.watch_pid, args.poll_seconds)
    checkpoint = copy_stable_checkpoint(source_run, output_root)
    resume_checkpoint(
        checkpoint=checkpoint,
        output_root=output_root,
        source_run=source_run,
        until=args.until,
        target_alife_coverage=args.target_alife_coverage,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"resume_from_checkpoint failed: {exc!r}", file=sys.stderr)
        raise
