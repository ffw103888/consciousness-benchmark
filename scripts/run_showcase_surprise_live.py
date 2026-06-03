#!/usr/bin/env python3
"""Live surprise showcase: stable weather reads, mutation, investigation.

Preferred one-shot acceptance path. Two-step CLI also works when agent_state.json
is persisted between invocations (see docs/phase_a3_direction_a_20260603.md).
"""

from __future__ import annotations

import argparse
import shutil
import time
from pathlib import Path

from consciousness_benchmark.construct_aware_agent import ConstructAwareAgent
from consciousness_benchmark.showcase_scenarios import apply_surprise_change, setup_surprise_showcase


def main() -> None:
    parser = argparse.ArgumentParser(description="Run surprise showcase (single session)")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("sandbox/showcase_surprise"),
        help="Sandbox workspace (default: sandbox/showcase_surprise)",
    )
    parser.add_argument("--llm", default="qwen3.5:9b")
    parser.add_argument("--fresh", action="store_true", help="Delete workspace before run")
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()

    ws = args.workspace
    if args.fresh and ws.exists():
        shutil.rmtree(ws)
    if not ws.exists() or args.fresh:
        setup_surprise_showcase(ws)

    agent = ConstructAwareAgent(ws, verbose=True, llm_model=args.llm)
    print("=== Phase A: establish weather expectation ===")
    for step in range(6):
        perception = agent.perceive()
        intention = agent.generate_intention(perception)
        outcome = agent.execute_action(intention)
        agent.record_memory(
            {"perception": perception, "intention": intention, "outcome": outcome}
        )
        if outcome.get("filename") == "weather.txt":
            print(f"  weather read: {outcome.get('content', '').strip()!r}")
        agent.step_count += 1
        time.sleep(args.interval)

    apply_surprise_change(ws)
    print("\n=== Mutation applied: Day 6: Raining ===\n")

    perception = agent.perceive()
    print("content_surprises:", perception.get("content_surprises"))
    intention = agent.generate_intention(perception)
    outcome = agent.execute_action(intention)
    print(f"post-mutation intention: {intention}")
    print(
        f"post-mutation outcome: action={outcome.get('action')} "
        f"file={outcome.get('filename')} changed={outcome.get('content_changed')} "
        f"content={str(outcome.get('content', '')).strip()!r}"
    )
    agent.record_memory(
        {"perception": perception, "intention": intention, "outcome": outcome}
    )
    agent.step_count += 1

    print("\n=== Phase B: follow-up steps ===")
    for _ in range(4):
        time.sleep(args.interval)
        perception = agent.perceive()
        intention = agent.generate_intention(perception)
        outcome = agent.execute_action(intention)
        agent.record_memory(
            {"perception": perception, "intention": intention, "outcome": outcome}
        )
        if outcome.get("action") == "reflect":
            reflection = str(outcome.get("reflection") or "")
            print(f"  reflect excerpt: {reflection[:220]}")
        else:
            print(f"  step: {intention}")
        agent.step_count += 1

    reflection_file = ws / "reflections.txt"
    if reflection_file.exists():
        print("\n=== reflections.txt ===")
        print(reflection_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
