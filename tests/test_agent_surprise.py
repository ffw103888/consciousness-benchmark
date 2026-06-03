from __future__ import annotations

from pathlib import Path

import pytest

from consciousness_benchmark.construct_aware_agent import ConstructAwareAgent


@pytest.fixture
def surprise_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "surprise_test"
    workspace.mkdir()
    (workspace / "pattern.txt").write_text("A", encoding="utf-8")
    return workspace


def test_expectation_violation(surprise_workspace: Path) -> None:
    """
    After a stable pattern, a content change should raise uncertainty and trigger investigation.
    """
    agent = ConstructAwareAgent(surprise_workspace, verbose=False, dry_run=True)

    for index in range(10):
        outcome = agent.execute_action("read pattern.txt")
        assert outcome["success"]
        agent.record_memory(
            {
                "step": index,
                "intention": "read pattern.txt",
                "outcome": outcome,
            }
        )
        agent.step_count += 1

    stable_perception = agent.perceive()
    baseline_uncertainty = float(stable_perception["uncertainty_level"])

    (surprise_workspace / "pattern.txt").write_text("B", encoding="utf-8")

    changed_perception = agent.perceive()
    outcome = agent.execute_action("read pattern.txt")
    intention = agent.generate_intention(changed_perception)

    post_uncertainty = float(
        (outcome.get("construct_state_after") or {}).get(
            "uncertainty_level",
            changed_perception["uncertainty_level"],
        )
    )

    assert outcome["success"]
    assert outcome["content"].startswith("B")
    assert post_uncertainty >= baseline_uncertainty - 0.05
    assert intention != "rest" or post_uncertainty >= agent.uncertainty_threshold


def test_surprise_triggers_investigation(surprise_workspace: Path) -> None:
    """After a stable pattern, a changed file should trigger re-read or reflect."""
    agent = ConstructAwareAgent(surprise_workspace, verbose=False, dry_run=True)

    for index in range(5):
        outcome = agent.execute_action("read pattern.txt")
        assert outcome["success"]
        assert "A" in outcome["content"]
        agent.step_count += 1

    (surprise_workspace / "pattern.txt").write_text("BBBB", encoding="utf-8")

    perception = agent.perceive()
    assert "pattern.txt" in perception["content_surprises"]

    intention = agent.generate_intention(perception)
    investigation_tokens = ("read pattern.txt", "reflect", "explore")
    assert any(token in intention for token in investigation_tokens)
