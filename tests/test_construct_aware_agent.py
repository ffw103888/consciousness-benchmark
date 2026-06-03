from __future__ import annotations

import json
from pathlib import Path

import pytest

from consciousness_benchmark.construct_aware_agent import (
    ConstructAwareAgent,
    compute_construct_state_delta,
    summarize_construct_state,
    talk_to_agent,
)
from consciousness_benchmark.constructs.mind_runtime import run_construct_grounded_mind_runtime_tick
from consciousness_benchmark.simple_persistent_agent import setup_demo_workspace


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    root = tmp_path / "construct_agent"
    setup_demo_workspace(root)
    return root


def test_construct_agent_perception_includes_runtime_state(workspace: Path) -> None:
    agent = ConstructAwareAgent(workspace, verbose=False, dry_run=True)
    perception = agent.perceive()

    assert "construct_state" in perception
    assert "uncertainty_level" in perception
    assert "active_goals" in perception
    assert perception["global_workspace_state"]["goal_count"] >= 0


def test_construct_agent_records_construct_ledger(workspace: Path) -> None:
    agent = ConstructAwareAgent(workspace, verbose=False, dry_run=True)
    agent.live(max_steps=3, step_interval=0)

    assert agent.construct_ledger_file.exists()
    lines = agent.construct_ledger_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    payload = json.loads(lines[0])
    assert "construct_summary" in payload


def test_construct_agent_execute_action_writes_state_delta(workspace: Path) -> None:
    agent = ConstructAwareAgent(workspace, verbose=False, dry_run=True)
    agent.perceive()
    outcome = agent.execute_action("read welcome.txt")

    assert outcome["success"]
    assert "construct_state_delta" in outcome
    assert "construct_state_after" in outcome


def test_summarize_construct_state_from_runtime_tick(workspace: Path) -> None:
    report = run_construct_grounded_mind_runtime_tick(asset_dirs=[workspace])
    summary = summarize_construct_state(report, uncertainty_level=0.42, tick_id="tick_test")

    assert summary.tick_id == "tick_test"
    assert summary.uncertainty_level == 0.42
    assert summary.reference_self_constructs


def test_compute_construct_state_delta_detects_goal_changes() -> None:
    report = run_construct_grounded_mind_runtime_tick(asset_dirs=[])
    before = summarize_construct_state(report, uncertainty_level=0.5, tick_id="a")
    after = summarize_construct_state(report, uncertainty_level=0.7, tick_id="b")
    delta = compute_construct_state_delta(before, after)

    assert delta["uncertainty_delta"] == pytest.approx(0.2)


def test_talk_to_agent_dry_run(workspace: Path) -> None:
    agent = ConstructAwareAgent(workspace, verbose=False, dry_run=True)
    agent.live(max_steps=2, step_interval=0)

    answer = talk_to_agent(workspace, question="What did you do?", dry_run=True)

    assert "dry-run" in answer.lower()
    assert "Question received" in answer
