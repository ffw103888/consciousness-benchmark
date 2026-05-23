from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from mind_lab.manager import default_config, run_from_config
from mind_lab.utils import ensure_dir, read_json, write_json


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the unfamiliar-mind experiment platform.")
    parser.add_argument("--config", type=str, default=None, help="Path to a JSON config file.")
    parser.add_argument("--mode", type=str, default="night", choices=["smoke", "quick", "night"], help="Default config mode.")
    parser.add_argument("--output-root", type=str, default="runs", help="Directory for run outputs.")
    parser.add_argument("--until", type=str, default=None, help="Deadline as ISO datetime, or seconds from now.")
    parser.add_argument("--seed", type=int, default=20260520)
    args = parser.parse_args()

    if args.config:
        config = read_json(args.config)
    else:
        config = default_config(args.mode, seed=args.seed)

    if args.mode and not args.config:
        config["mode"] = args.mode
    deadline_epoch = parse_deadline(args.until)
    if deadline_epoch is not None:
        config.setdefault("termination_conditions", {})["wall_clock_deadline"] = args.until

    output_root = ensure_dir(args.output_root)
    write_json(output_root / "latest_config.json", config)
    latest_path = output_root / "latest_run.txt"
    latest_path.write_text(str(output_root / str(config.get("id", "pending_run"))), encoding="utf-8")
    report = run_from_config(config, output_root, deadline_epoch=deadline_epoch)
    latest_path.write_text(str(report.get("run_dir", "")), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
