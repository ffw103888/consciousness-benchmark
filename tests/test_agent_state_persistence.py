from __future__ import annotations

from pathlib import Path

from consciousness_benchmark.construct_aware_agent import ConstructAwareAgent
from consciousness_benchmark.showcase_scenarios import apply_surprise_change, setup_surprise_showcase
from consciousness_benchmark.simple_persistent_agent import AGENT_STATE_FILENAME


def test_agent_state_survives_process_restart(tmp_path: Path) -> None:
    """Two CLI-style invocations should keep file cache for content_surprises."""
    workspace = tmp_path / "surprise_resume"
    setup_surprise_showcase(workspace)

    agent1 = ConstructAwareAgent(workspace, verbose=False, dry_run=True)
    for _ in range(3):
        outcome = agent1.execute_action("read weather.txt")
        assert outcome["success"]
        agent1.record_memory({"intention": "read weather.txt", "outcome": outcome})
        agent1.step_count += 1
        agent1._save_agent_state()

    assert (workspace / AGENT_STATE_FILENAME).exists()
    assert agent1._file_content_cache.get("weather.txt") == "Day 1: Sunny\n"

    apply_surprise_change(workspace)

    agent2 = ConstructAwareAgent(workspace, verbose=False, dry_run=True)
    assert agent2.step_count == 3
    assert "weather.txt" in agent2.explored_files
    perception = agent2.perceive()

    assert "weather.txt" in perception["content_surprises"]
    assert agent2.generate_intention(perception) == "read weather.txt"


def test_live_runs_additional_steps_after_resume(tmp_path: Path) -> None:
    workspace = tmp_path / "resume_steps"
    setup_surprise_showcase(workspace)

    agent = ConstructAwareAgent(workspace, verbose=False, dry_run=True)
    agent.live(max_steps=3, step_interval=0)
    assert agent.step_count == 3

    agent.live(max_steps=2, step_interval=0)
    assert agent.step_count == 5
