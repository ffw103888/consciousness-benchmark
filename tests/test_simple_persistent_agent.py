from __future__ import annotations

import json
from pathlib import Path

import pytest

from consciousness_benchmark.constructs.local_llm import (
    extract_visible_llm_response,
    parse_agent_intention,
)
from consciousness_benchmark.simple_persistent_agent import (
    MEMORY_FILENAME,
    SimplePersistentAgent,
    setup_demo_workspace,
)


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "agent_test"
    workspace.mkdir()
    return workspace


def test_agent_initialization(temp_workspace: Path) -> None:
    agent = SimplePersistentAgent(temp_workspace, verbose=False, dry_run=True)
    assert agent.step_count == 0
    assert agent.running
    assert agent.memory_file.name == MEMORY_FILENAME


def test_perception(temp_workspace: Path) -> None:
    agent = SimplePersistentAgent(temp_workspace, verbose=False, dry_run=True)
    (temp_workspace / "test1.txt").write_text("content1", encoding="utf-8")
    (temp_workspace / "test2.txt").write_text("content2", encoding="utf-8")

    perception = agent.perceive()

    assert "test1.txt" in perception["workspace_files"]
    assert "test2.txt" in perception["workspace_files"]


def test_action_explore(temp_workspace: Path) -> None:
    agent = SimplePersistentAgent(temp_workspace, verbose=False, dry_run=True)
    (temp_workspace / "file1.txt").write_text("test", encoding="utf-8")

    outcome = agent.execute_action("explore")

    assert outcome["success"]
    assert "file1.txt" in outcome["result"]


def test_action_read(temp_workspace: Path) -> None:
    agent = SimplePersistentAgent(temp_workspace, verbose=False, dry_run=True)
    (temp_workspace / "test.txt").write_text("Hello World", encoding="utf-8")

    outcome = agent.execute_action("read test.txt")

    assert outcome["success"]
    assert "Hello World" in outcome["content"]
    assert "test.txt" in agent.explored_files


def test_action_write(temp_workspace: Path) -> None:
    agent = SimplePersistentAgent(temp_workspace, verbose=False, dry_run=True)

    outcome = agent.execute_action("write notes.txt This is a test")

    assert outcome["success"]
    assert (temp_workspace / "notes.txt").read_text(encoding="utf-8") == "This is a test"


def test_memory_recording(temp_workspace: Path) -> None:
    agent = SimplePersistentAgent(temp_workspace, verbose=False, dry_run=True)
    agent.record_memory({"intention": "explore", "outcome": {"success": True}})

    lines = agent.memory_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    recorded = json.loads(lines[0])
    assert recorded["intention"] == "explore"
    assert "timestamp" in recorded


def test_read_recent_memory(temp_workspace: Path) -> None:
    agent = SimplePersistentAgent(temp_workspace, verbose=False, dry_run=True)
    for index in range(10):
        agent.record_memory({"data": f"entry_{index}"})
        agent.step_count += 1

    recent = agent.read_recent_memory(n=3)

    assert len(recent) == 3
    assert recent[-1]["data"] == "entry_9"


def test_dry_run_live_cycle(temp_workspace: Path) -> None:
    setup_demo_workspace(temp_workspace)
    agent = SimplePersistentAgent(temp_workspace, verbose=False, dry_run=True)
    agent.live(max_steps=5, step_interval=0)

    assert agent.step_count == 5
    assert agent.memory_file.exists()
    assert len(agent.read_recent_memory(n=10)) == 5


def test_extract_visible_llm_response_strips_thinking_block() -> None:
    open_tag = "<" + "redacted_reasoning" + ">"
    close_tag = "</" + "redacted_reasoning" + ">"
    raw = f"{open_tag}\nI should read welcome.txt first.\n{close_tag}\nread welcome.txt"
    assert extract_visible_llm_response(raw) == "read welcome.txt"


def test_parse_agent_intention_from_thinking_model() -> None:
    raw = (
        "planning\n\n"
        "Some explanation.\n"
        "reflect"
    )
    assert parse_agent_intention(raw) == "reflect"
