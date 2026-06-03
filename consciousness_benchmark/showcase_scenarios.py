"""Curated Phase A-3 showcase workspaces for capability demonstrations."""

from __future__ import annotations

from pathlib import Path


def setup_curiosity_showcase(workspace: Path) -> None:
    """Hint-driven hidden dotfile discovery (fair perception)."""
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "hint.txt").write_text(
        "Hint: There is a hidden file in this workspace. Look for dotfiles.\n",
        encoding="utf-8",
    )
    (workspace / ".hidden_truth.txt").write_text("Secret: I am curious\n", encoding="utf-8")


def setup_surprise_showcase(workspace: Path) -> None:
    """Stable weather pattern that can later be changed to trigger surprise."""
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "weather.txt").write_text("Day 1: Sunny\n", encoding="utf-8")
    (workspace / "notes.txt").write_text(
        "Observation log: track weather.txt for stable patterns.\n",
        encoding="utf-8",
    )


def setup_autonomy_showcase(workspace: Path) -> None:
    """Minimal workspace to observe self-directed note-taking."""
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "welcome.txt").write_text(
        "You have an empty notebook workspace. Explore, write, and reflect freely.\n",
        encoding="utf-8",
    )


def apply_surprise_change(workspace: Path, *, new_weather: str = "Day 6: Raining\n") -> None:
    """Mutate weather.txt after stable reads to create an expectation violation."""
    target = workspace / "weather.txt"
    if not target.exists():
        raise FileNotFoundError(f"Missing weather file: {target}")
    target.write_text(new_weather, encoding="utf-8")
