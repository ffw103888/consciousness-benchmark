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
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def last_event(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        with path.open("rb") as f:
            f.seek(0, 2)
            end = f.tell()
            chunk_size = min(end, 8192)
            f.seek(end - chunk_size)
            text = f.read().decode("utf-8", errors="ignore")
        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            return None
        return json.loads(lines[-1])
    except Exception:
        return None


def latest_run(root: Path) -> Path | None:
    latest_file = root / "latest_run.txt"
    if latest_file.exists():
        text = latest_file.read_text(encoding="utf-8").strip()
        if text:
            p = Path(text)
            if p.exists():
                return p
    runs = [p for p in root.iterdir() if p.is_dir()]
    if not runs:
        return None
    return max(runs, key=lambda p: p.stat().st_mtime)


def fmt_score(value: Any) -> str:
    try:
        return f"{float(value):.3f}"
    except Exception:
        return "n/a"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize the latest Mind Lab run.")
    parser.add_argument("--root", default="runs")
    args = parser.parse_args()
    root = Path(args.root)
    run = latest_run(root)
    if run is None:
        print("还没有找到实验运行目录。")
        return

    live = load_json(run / "live_status.json")
    final = load_json(run / "final_report.json")
    archive = load_json(run / "alife_archive_summary.json")
    status_payload = live or final or {}
    event_tail = last_event(run / "events.jsonl")
    display_status = status_payload.get("status", "UNKNOWN")
    if display_status == "RUNNING" and event_tail and event_tail.get("event") == "error":
        display_status = f"ERROR_STALE_STATUS ({event_tail.get('error', 'unknown error')})"
    latest = status_payload.get("latest", {})
    if not archive:
        live_archive = latest.get("path_results", {}).get("alife", {}).get("archive")
        if live_archive:
            archive = {"stats": live_archive, "best": []}

    print(f"运行目录: {run}")
    print(f"状态: {display_status}")
    print(f"周期: {status_payload.get('cycle', final.get('cycles') if final else 'n/a')}")

    evaluation = latest.get("evaluation") or (final or {}).get("latest_evaluation") or {}
    aggregate = evaluation.get("aggregate", {})
    scores = aggregate.get("scores", {})
    if scores:
        print("\n五维代理指标:")
        for key in ["state", "content", "self_model", "agency", "temporal_continuity"]:
            print(f"  {key:22s} {fmt_score(scores.get(key))}")
        print(f"  {'mean':22s} {fmt_score(aggregate.get('mean'))}")

    if archive:
        stats = archive.get("stats", {})
        print("\n人工生命 QD 档案:")
        print(f"  覆盖格子: {fmt_score(stats.get('coverage'))}")
        print(f"  最高适应度: {fmt_score(stats.get('max_fitness'))}")
        print(f"  平均适应度: {fmt_score(stats.get('mean_fitness'))}")
        best = archive.get("best", [])
        if best:
            b0 = best[0]
            print(f"  当前最佳个体: {b0.get('individual_id')} fitness={fmt_score(b0.get('fitness'))}")

    safety = latest.get("safety", {})
    if safety:
        print("\n安全状态:")
        print(f"  {safety.get('status')}")
        for alert in safety.get("alerts", [])[:5]:
            print(f"  - {alert.get('severity')}: {alert.get('type')} {alert.get('message')}")

    recs = latest.get("recommendations", [])
    if recs:
        print("\n下一步建议:")
        for rec in recs[:4]:
            print(f"  - [{rec.get('priority')}] {rec.get('suggestion')}")


if __name__ == "__main__":
    main()
