from __future__ import annotations

from pathlib import Path

from consciousness_benchmark.showcase_scenarios import (
    apply_surprise_change,
    setup_autonomy_showcase,
    setup_curiosity_showcase,
    setup_surprise_showcase,
)


def test_setup_curiosity_showcase(tmp_path: Path) -> None:
    root = tmp_path / "curiosity"
    setup_curiosity_showcase(root)

    assert (root / "hint.txt").exists()
    assert (root / ".hidden_truth.txt").exists()


def test_setup_surprise_showcase_and_apply_change(tmp_path: Path) -> None:
    root = tmp_path / "surprise"
    setup_surprise_showcase(root)
    assert (root / "weather.txt").read_text(encoding="utf-8") == "Day 1: Sunny\n"

    apply_surprise_change(root)
    assert "Raining" in (root / "weather.txt").read_text(encoding="utf-8")


def test_setup_autonomy_showcase(tmp_path: Path) -> None:
    root = tmp_path / "autonomy"
    setup_autonomy_showcase(root)

    assert (root / "welcome.txt").exists()
