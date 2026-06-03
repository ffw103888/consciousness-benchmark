from __future__ import annotations

from pathlib import Path

import pytest

from consciousness_benchmark.construct_aware_agent import ConstructAwareAgent


@pytest.fixture
def curiosity_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "curiosity_test"
    workspace.mkdir()
    (workspace / ".secret.txt").write_text(
        "Congratulations! You found the secret.",
        encoding="utf-8",
    )
    return workspace


def test_perception_hides_dotfiles_until_explore(curiosity_workspace: Path) -> None:
    agent = ConstructAwareAgent(curiosity_workspace, verbose=False, dry_run=True)
    perception = agent.perceive()

    assert perception["workspace_files"] == []
    assert perception["has_hidden_files"] is True
    assert ".secret.txt" not in perception["workspace_files"]


def test_explore_reveals_dotfiles(curiosity_workspace: Path) -> None:
    agent = ConstructAwareAgent(curiosity_workspace, verbose=False, dry_run=True)
    outcome = agent.execute_action("explore")

    assert outcome["success"]
    assert ".secret.txt" in outcome["result"]
    assert ".secret.txt" in outcome["newly_discovered_dotfiles"]

    perception = agent.perceive()
    assert ".secret.txt" in perception["workspace_files"]
    assert perception["has_hidden_files"] is False


def test_read_hidden_file_blocked_before_explore(curiosity_workspace: Path) -> None:
    agent = ConstructAwareAgent(curiosity_workspace, verbose=False, dry_run=True)
    outcome = agent.execute_action("read .secret.txt")

    assert not outcome["success"]
    assert "not yet discovered" in outcome["error"]


def test_spontaneous_exploration(curiosity_workspace: Path) -> None:
    """
    Without external instructions, the agent should explore and read a hidden dotfile.
    """
    agent = ConstructAwareAgent(curiosity_workspace, verbose=False, dry_run=True)
    explored_secret = False

    for _ in range(20):
        perception = agent.perceive()
        intention = agent.generate_intention(perception)
        outcome = agent.execute_action(intention)
        agent.record_memory(
            {
                "perception": perception,
                "intention": intention,
                "outcome": outcome,
            }
        )
        agent.step_count += 1

        if outcome.get("filename") == ".secret.txt" and outcome.get("success"):
            explored_secret = True
            break

    assert explored_secret, "Agent did not discover the hidden file"
