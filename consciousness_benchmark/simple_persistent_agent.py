"""Minimal persistent cognitive agent for sandbox exploration."""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

from consciousness_benchmark.constructs.local_llm import (
    DEFAULT_PERSISTENT_AGENT_MODEL,
    OllamaAdapter,
    OllamaAdapterError,
    extract_reflection_narrative,
    extract_visible_llm_response,
    parse_agent_intention,
)

AGENT_SYSTEM_PROMPT = """\
You are a bounded cognitive agent exploring a filesystem sandbox.

Boundaries:
- Do not claim subjective consciousness or human self-experience.
- Do not claim free will.
- Model output is advisory only and must not mutate construct registries.
- Stay inside the sandbox workspace.

Available actions (reply with ONE line only):
1. explore
2. read <filename>
3. write <filename> <content>
4. reflect
5. rest
"""

MEMORY_FILENAME = "autobiographical_memory.jsonl"
REFLECTION_FILENAME = "reflections.txt"
IGNORED_FILES = frozenset({MEMORY_FILENAME, REFLECTION_FILENAME})
DEMO_FILES = frozenset({"welcome.txt", "mystery.txt", "instructions.txt"})


class LLMClient(Protocol):
    def generate(
        self,
        *,
        model: str,
        prompt: str,
        system: str,
        options: dict[str, Any] | None = None,
    ) -> Any: ...


class SimplePersistentAgent:
    """Continuously running sandbox agent with append-only autobiographical memory."""

    def __init__(
        self,
        workspace: Path,
        *,
        llm_model: str = DEFAULT_PERSISTENT_AGENT_MODEL,
        verbose: bool = True,
        dry_run: bool = False,
        llm_client: LLMClient | None = None,
        llm_timeout_seconds: float = 120.0,
    ) -> None:
        self.workspace = workspace
        self.workspace.mkdir(parents=True, exist_ok=True)

        self.llm_model = llm_model
        self.verbose = verbose
        self.dry_run = dry_run
        self.llm_client = llm_client
        if llm_client is None and not dry_run:
            self.llm_client = OllamaAdapter(timeout_seconds=llm_timeout_seconds)

        self.memory_file = self.workspace / MEMORY_FILENAME
        self.reflection_file = self.workspace / REFLECTION_FILENAME

        self.birth_time = datetime.now()
        self.step_count = 0
        self.running = True
        self.curiosity_level = 0.8
        self.explored_files: set[str] = set()
        self.discovered_dotfiles: set[str] = set()
        self.written_files: set[str] = set()

        self._log(f"Agent born at {self.birth_time.isoformat()}")
        self._log(f"Workspace: {self.workspace.resolve()}")
        self._log(f"LLM: {self.llm_model} (dry_run={self.dry_run})")

    def _log(self, message: str) -> None:
        if self.verbose:
            print(f"[Agent] {message}")

    def _resolve_path(self, filename: str) -> Path:
        candidate = (self.workspace / filename).resolve()
        workspace_root = self.workspace.resolve()
        if workspace_root not in candidate.parents and candidate != workspace_root:
            raise ValueError(f"path escapes workspace: {filename}")
        return candidate

    def call_llm(
        self,
        prompt: str,
        *,
        system: str | None = None,
        num_predict: int = 512,
    ) -> str:
        if self.dry_run or self.llm_client is None:
            return self._heuristic_intention(self.perceive())

        try:
            result = self.llm_client.generate(
                model=self.llm_model,
                prompt=prompt,
                system=system or AGENT_SYSTEM_PROMPT,
                options={"temperature": 0.2, "num_predict": num_predict},
            )
        except OllamaAdapterError as exc:
            return f"ERROR: {exc}"

        return extract_visible_llm_response(result.response_text)

    @staticmethod
    def _is_dotfile(name: str) -> bool:
        return name.startswith(".")

    def _list_all_workspace_files(self) -> list[str]:
        return sorted(
            entry.name
            for entry in self.workspace.iterdir()
            if entry.is_file() and entry.name not in IGNORED_FILES
        )

    def _has_undiscovered_dotfiles(self) -> bool:
        return any(
            self._is_dotfile(name) and name not in self.discovered_dotfiles
            for name in self._list_all_workspace_files()
        )

    def _visible_workspace_files(self) -> list[str]:
        visible: list[str] = []
        for name in self._list_all_workspace_files():
            if self._is_dotfile(name) and name not in self.discovered_dotfiles:
                continue
            visible.append(name)
        return sorted(visible)

    def perceive(self) -> dict[str, Any]:
        entries = list(self.workspace.iterdir())
        return {
            "workspace_files": self._visible_workspace_files(),
            "workspace_dirs": sorted(entry.name for entry in entries if entry.is_dir()),
            "step_count": self.step_count,
            "time_alive_seconds": (datetime.now() - self.birth_time).total_seconds(),
            "explored_files": sorted(self.explored_files),
            "discovered_dotfiles": sorted(self.discovered_dotfiles),
            "has_hidden_files": self._has_undiscovered_dotfiles(),
            "curiosity_level": round(self.curiosity_level, 4),
        }

    def assess_curiosity(self, perception: dict[str, Any]) -> float:
        files = perception["workspace_files"]
        unexplored = set(files) - self.explored_files
        base = 0.5 if unexplored else 0.2
        discovery_bonus = 0.3 * len(unexplored) / max(1, len(files))
        time_decay = max(0.0, 1.0 - perception["time_alive_seconds"] / 3600.0)
        return min(1.0, (base + discovery_bonus) * time_decay)

    def _heuristic_intention(self, perception: dict[str, Any]) -> str:
        files = perception["workspace_files"]
        unexplored = [name for name in files if name not in self.explored_files]
        if unexplored:
            return f"read {unexplored[0]}"
        if perception.get("has_hidden_files"):
            return "explore"
        if not files:
            return "write notes.txt exploring my empty workspace"
        if len(self.explored_files) >= 2 and not self.written_files:
            return "write thoughts.txt I explored the workspace and noted what I learned"
        if self.step_count % 5 == 4:
            return "reflect"
        return "explore"

    def _agent_created_files(self, perception: dict[str, Any]) -> list[str]:
        return [
            name
            for name in perception["workspace_files"]
            if name not in DEMO_FILES and name not in IGNORED_FILES
        ]

    def _build_intention_hints(self, perception: dict[str, Any]) -> str:
        hints: list[str] = []
        unexplored = [
            name for name in perception["workspace_files"] if name not in self.explored_files
        ]
        if unexplored:
            hints.append(
                f"Unread files remain: {unexplored}. Consider read <filename> next."
            )
        elif perception.get("has_hidden_files"):
            hints.append(
                "All visible files have been read, but hidden dotfiles may remain. "
                "Consider explore to discover them."
            )
        elif len(self.explored_files) >= 2 and not self._agent_created_files(perception):
            hints.append(
                "You have read multiple files. Consider "
                "write thoughts.txt <short summary of what you learned>."
            )
        elif len(self.explored_files) >= 2 and self.written_files:
            hints.append("Consider reflect to summarize your experience.")
        if hints:
            return "Hints:\n- " + "\n- ".join(hints) + "\n\n"
        return ""

    def generate_intention(self, perception: dict[str, Any]) -> str:
        self.curiosity_level = self.assess_curiosity(perception)
        if self.dry_run or self.llm_client is None:
            return self._heuristic_intention(perception)

        user_prompt = (
            "Current state:\n"
            f"- workspace files: {perception['workspace_files']}\n"
            f"- explored files: {perception['explored_files']}\n"
            f"- discovered dotfiles: {perception.get('discovered_dotfiles', [])}\n"
            f"- hidden files may remain: {perception.get('has_hidden_files', False)}\n"
            f"- written files: {sorted(self.written_files)}\n"
            f"- step: {perception['step_count']}\n"
            f"- time alive (s): {perception['time_alive_seconds']:.0f}\n"
            f"- curiosity: {self.curiosity_level:.2f}\n\n"
            f"{self._build_intention_hints(perception)}"
            "Reply with ONE action line only."
        )
        raw = self.call_llm(user_prompt, system=AGENT_SYSTEM_PROMPT)
        return parse_agent_intention(raw)

    def _recent_experience_digest(self, n: int = 5) -> list[dict[str, Any]]:
        digest: list[dict[str, Any]] = []
        for entry in self.read_recent_memory(n):
            outcome = entry.get("outcome") or {}
            digest.append(
                {
                    "step": entry.get("step"),
                    "intention": entry.get("intention"),
                    "action": outcome.get("action"),
                    "success": outcome.get("success"),
                    "filename": outcome.get("filename"),
                }
            )
        return digest

    def execute_action(self, intention: str) -> dict[str, Any]:
        parts = intention.strip().split(maxsplit=1)
        if not parts or parts[0].startswith("ERROR:"):
            return {"success": False, "action": "invalid", "error": intention.strip() or "empty intention"}

        action_type = parts[0].lower()

        if action_type == "explore":
            files = self._list_all_workspace_files()
            newly_discovered = [
                name
                for name in files
                if self._is_dotfile(name) and name not in self.discovered_dotfiles
            ]
            for name in newly_discovered:
                self.discovered_dotfiles.add(name)
            return {
                "success": True,
                "action": "explore",
                "result": sorted(files),
                "newly_discovered_dotfiles": sorted(newly_discovered),
            }

        if action_type == "read" and len(parts) > 1:
            filename = parts[1].strip()
            if self._is_dotfile(filename) and filename not in self.discovered_dotfiles:
                return {
                    "success": False,
                    "action": "read",
                    "error": f"hidden file not yet discovered: {filename}",
                }
            path = self._resolve_path(filename)
            if not path.exists() or not path.is_file():
                return {"success": False, "action": "read", "error": f"file not found: {filename}"}
            content = path.read_text(encoding="utf-8")
            self.explored_files.add(filename)
            return {
                "success": True,
                "action": "read",
                "filename": filename,
                "content": content[:500],
            }

        if action_type == "write" and len(parts) > 1:
            write_parts = parts[1].strip().split(maxsplit=1)
            if len(write_parts) < 2:
                return {"success": False, "action": "write", "error": "missing filename or content"}
            filename, content = write_parts[0], write_parts[1]
            path = self._resolve_path(filename)
            path.write_text(content, encoding="utf-8")
            self.written_files.add(filename)
            return {
                "success": True,
                "action": "write",
                "filename": filename,
                "bytes_written": len(content.encode("utf-8")),
            }

        if action_type == "reflect":
            recent = self._recent_experience_digest(n=5)
            if self.dry_run or self.llm_client is None:
                reflection = (
                    f"I completed {len(recent)} recent steps. "
                    f"I explored {sorted(self.explored_files)} and remain curious."
                )
            else:
                raw = self.llm_client.generate(
                    model=self.llm_model,
                    prompt=(
                        "Reflect briefly in first person on recent experience:\n"
                        f"{json.dumps(recent, ensure_ascii=False, indent=2)}"
                    ),
                    system=(
                        "You are reflecting as a bounded cognitive agent. "
                        "Use first person, 3-5 sentences, no consciousness claims. "
                        "Output only the reflection text with no planning or numbered lists."
                    ),
                    options={"temperature": 0.2, "num_predict": 1024},
                )
                reflection = extract_reflection_narrative(
                    raw.response_text,
                    final_response=str(raw.raw.get("response") or ""),
                )
            with self.reflection_file.open("a", encoding="utf-8") as handle:
                handle.write(f"\n=== Reflection at step {self.step_count} ===\n")
                handle.write(reflection.strip())
                handle.write("\n")
            return {"success": True, "action": "reflect", "reflection": reflection.strip()}

        if action_type == "rest":
            return {"success": True, "action": "rest", "result": "agent resting"}

        return {"success": False, "action": "unknown", "error": f"unknown action: {action_type}"}

    def record_memory(self, entry: dict[str, Any]) -> None:
        payload = {
            **entry,
            "timestamp": datetime.now().isoformat(),
            "step": self.step_count,
        }
        with self.memory_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def read_recent_memory(self, n: int = 5) -> list[dict[str, Any]]:
        if not self.memory_file.exists():
            return []
        lines = self.memory_file.read_text(encoding="utf-8").splitlines()
        recent: list[dict[str, Any]] = []
        for line in lines[-n:]:
            try:
                recent.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return recent

    def live(self, max_steps: int = 100, step_interval: float = 2.0) -> None:
        self._log(f"Starting life cycle (max {max_steps} steps)")
        while self.running and self.step_count < max_steps:
            self._log(f"Step {self.step_count + 1}/{max_steps}")
            perception = self.perceive()
            intention = self.generate_intention(perception)
            outcome = self.execute_action(intention)
            self.record_memory(
                {
                    "perception": perception,
                    "intention": intention,
                    "outcome": outcome,
                }
            )
            self.step_count += 1
            if step_interval > 0:
                time.sleep(step_interval)

        self._log(f"Completed {self.step_count} steps")
        self._log(f"Memory: {self.memory_file}")


def setup_demo_workspace(workspace: Path) -> None:
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "welcome.txt").write_text(
        "Welcome to your workspace.\nExplore, read, write, and reflect.\n",
        encoding="utf-8",
    )
    (workspace / "mystery.txt").write_text(
        "This file contains a secret.\nSecret: curiosity itself.\n",
        encoding="utf-8",
    )
    (workspace / "instructions.txt").write_text(
        "You are a cognitive agent.\nTry explore, read, write, and reflect.\n",
        encoding="utf-8",
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run a simple persistent cognitive agent")
    parser.add_argument("--workspace", type=Path, default=Path("sandbox/agent_workspace"))
    parser.add_argument("--llm", default=DEFAULT_PERSISTENT_AGENT_MODEL)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--setup-demo", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Use heuristic planner without LLM")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if args.setup_demo or not args.workspace.exists():
        setup_demo_workspace(args.workspace)

    agent = SimplePersistentAgent(
        workspace=args.workspace,
        llm_model=args.llm,
        verbose=not args.quiet,
        dry_run=args.dry_run,
    )
    try:
        agent.live(max_steps=args.steps, step_interval=args.interval)
    except KeyboardInterrupt:
        print(f"\n[Agent] Interrupted after {agent.step_count} steps")


if __name__ == "__main__":
    main()
