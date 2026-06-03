"""Launch the simple persistent agent with optional demo workspace setup."""

from __future__ import annotations

from pathlib import Path

from consciousness_benchmark.constructs.local_llm import DEFAULT_PERSISTENT_AGENT_MODEL
from consciousness_benchmark.simple_persistent_agent import (
    SimplePersistentAgent,
    setup_demo_workspace,
)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run persistent agent with demo setup")
    parser.add_argument("--workspace", type=Path, default=Path("sandbox/demo_agent"))
    parser.add_argument("--steps", type=int, default=15)
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--llm", default=DEFAULT_PERSISTENT_AGENT_MODEL)
    parser.add_argument("--setup-demo", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.setup_demo or not args.workspace.exists():
        setup_demo_workspace(args.workspace)
        print(f"Demo workspace ready: {args.workspace.resolve()}")

    agent = SimplePersistentAgent(
        workspace=args.workspace,
        llm_model=args.llm,
        dry_run=args.dry_run,
        verbose=True,
    )
    agent.live(max_steps=args.steps, step_interval=args.interval)

    print("\nSUMMARY")
    print(f"- steps: {agent.step_count}")
    print(f"- explored: {sorted(agent.explored_files)}")
    print(f"- curiosity: {agent.curiosity_level:.2f}")
    print(f"- memory: {agent.memory_file}")
    if agent.reflection_file.exists():
        print(f"- reflections: {agent.reflection_file}")


if __name__ == "__main__":
    main()
