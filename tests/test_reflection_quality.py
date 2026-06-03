from __future__ import annotations

from pathlib import Path

from consciousness_benchmark.constructs.local_llm import (
    calculate_reflection_narrative_quality,
    extract_reflection_narrative_smart,
    reflection_narrative_is_usable,
)
from consciousness_benchmark.simple_persistent_agent import SimplePersistentAgent


def test_calculate_reflection_narrative_quality_scores_good_text() -> None:
    text = (
        "I explored the workspace, discovered a hidden file, and read its secret. "
        "I noticed the weather changed from sunny to raining and want to write notes next."
    )
    assert calculate_reflection_narrative_quality(text) >= 0.7
    assert reflection_narrative_is_usable(text)


def test_calculate_reflection_narrative_quality_rejects_meta_fragments() -> None:
    text = "*Check content:* I processed files. Step 1: read weather.txt"
    assert calculate_reflection_narrative_quality(text) < 0.6
    assert not reflection_narrative_is_usable(text)


def test_extract_reflection_narrative_smart_prefers_clean_response() -> None:
    raw = "Thinking Process:\n*Wait*\nDrafting - Attempt 1:\nI read weather.txt and noticed rain."
    final = "I read weather.txt and noticed it changed from sunny to raining."
    extracted = extract_reflection_narrative_smart(raw, final_response=final)
    assert "weather" in extracted.lower()
    assert "*Check" not in extracted


def test_reflect_action_uses_structured_fallback(tmp_path: Path) -> None:
    workspace = tmp_path / "reflect_quality"
    workspace.mkdir()
    (workspace / "weather.txt").write_text("Day 6: Raining\n", encoding="utf-8")

    agent = SimplePersistentAgent(workspace, verbose=False, dry_run=True)
    read_outcome = agent.execute_action("read weather.txt")
    agent.record_memory({"intention": "read weather.txt", "outcome": read_outcome})
    outcome = agent.execute_action("reflect")

    reflection = outcome.get("reflection", "")
    assert len(reflection) >= 50
    assert reflection_narrative_is_usable(reflection)
    assert "weather" in reflection.lower() or "read" in reflection.lower()


def test_build_reflection_prompt_mentions_content_changes(tmp_path: Path) -> None:
    agent = SimplePersistentAgent(tmp_path, verbose=False, dry_run=True)
    recent = [
        {
            "intention": "read weather.txt",
            "outcome": {
                "action": "read",
                "filename": "weather.txt",
                "content": "Day 6: Raining",
                "content_changed": True,
            },
        }
    ]
    _system, user = agent.build_reflection_prompt(recent)
    assert "Content changes detected" in user
    assert "weather.txt" in user
