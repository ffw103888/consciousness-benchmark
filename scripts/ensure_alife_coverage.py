"""Keep resuming ALife-only runs until a target QD coverage is reached."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import psutil
except Exception:  # pragma: no cover
    psutil = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def latest_run(root: Path) -> Path | None:
    latest_file = root / "latest_run.txt"
    if latest_file.exists():
        text = latest_file.read_text(encoding="utf-8").strip()
        if text:
            path = Path(text)
            if path.exists():
                return path
    runs = [p for p in root.iterdir() if p.is_dir()]
    return max(runs, key=lambda p: p.stat().st_mtime) if runs else None


def coverage_of(run: Path) -> float:
    archive = load_json(run / "alife_archive_summary.json")
    if archive:
        try:
            return float(archive.get("stats", {}).get("coverage", 0.0))
        except Exception:
            pass
    live = load_json(run / "live_status.json")
    if live:
        try:
            return float(live["latest"]["path_results"]["alife"]["archive"]["coverage"])
        except Exception:
            pass
    return 0.0


def active_alife_only_processes() -> list[int]:
    if psutil is None:
        return []
    pids: list[int] = []
    current = psutil.Process().pid
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            if proc.info["pid"] == current:
                continue
            cmdline = " ".join(proc.info.get("cmdline") or [])
            if "resume_alife_only.py" in cmdline:
                pids.append(int(proc.info["pid"]))
        except Exception:
            continue
    return pids


def valid_source_run(root: Path) -> Path:
    run = latest_run(root)
    if run is None:
        raise RuntimeError(f"No runs found under {root}")
    if not (run / "checkpoint.pkl").exists():
        # If latest_run points at a half-created failed attempt, walk backward to
        # the most recent run with a checkpoint and archive summary.
        candidates = sorted([p for p in root.iterdir() if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)
        for candidate in candidates:
            if (candidate / "checkpoint.pkl").exists() and (candidate / "alife_archive_summary.json").exists():
                return candidate
        raise RuntimeError(f"No checkpoint-bearing run found under {root}")
    return run


def start_resume(source_run: Path, args: argparse.Namespace) -> subprocess.Popen:
    command = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "resume_alife_only.py"),
        "--source-run",
        str(source_run),
        "--output-root",
        str(args.root),
        "--target-alife-coverage",
        str(args.target),
        "--workers",
        str(args.workers),
        "--chunk-generations",
        str(args.chunk_generations),
        "--checkpoint-every",
        str(args.checkpoint_every),
    ]
    if args.until:
        command.extend(["--until", args.until])
    return subprocess.Popen(command, cwd=PROJECT_ROOT)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("runs"))
    parser.add_argument("--target", type=float, default=16000)
    parser.add_argument("--until", type=str, default=None, help="Optional deadline passed to child resume runs.")
    parser.add_argument("--poll-seconds", type=int, default=60)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--chunk-generations", type=int, default=64)
    parser.add_argument("--checkpoint-every", type=int, default=4)
    args = parser.parse_args()

    root = args.root
    log_path = root / "alife_coverage_guard.jsonl"
    append_jsonl(log_path, {"time": datetime.now().isoformat(timespec="seconds"), "event": "guard_started", "target": args.target})

    while True:
        run = valid_source_run(root)
        coverage = coverage_of(run)
        append_jsonl(
            log_path,
            {
                "time": datetime.now().isoformat(timespec="seconds"),
                "event": "guard_poll",
                "run": str(run),
                "coverage": coverage,
                "active_alife_only_pids": active_alife_only_processes(),
            },
        )
        if coverage >= float(args.target):
            append_jsonl(log_path, {"time": datetime.now().isoformat(timespec="seconds"), "event": "target_reached", "coverage": coverage})
            return

        active = active_alife_only_processes()
        if active:
            time.sleep(max(5, int(args.poll_seconds)))
            continue

        child = start_resume(run, args)
        append_jsonl(
            log_path,
            {
                "time": datetime.now().isoformat(timespec="seconds"),
                "event": "started_child_resume",
                "source_run": str(run),
                "pid": child.pid,
                "coverage": coverage,
            },
        )
        time.sleep(max(5, int(args.poll_seconds)))


if __name__ == "__main__":
    main()
