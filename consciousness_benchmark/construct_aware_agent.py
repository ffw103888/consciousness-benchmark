"""Persistent sandbox agent integrated with construct-grounded mind runtime."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from consciousness_benchmark.constructs.local_llm import parse_agent_intention
from consciousness_benchmark.constructs.mind_runtime import (
    ConstructGroundedMindRuntimeReport,
    run_construct_grounded_mind_runtime_tick,
)
from consciousness_benchmark.simple_persistent_agent import (
    REFLECTION_FILENAME,
    SimplePersistentAgent,
)


CONSTRUCT_LEDGER_FILENAME = "construct_state_ledger.jsonl"
UNCERTAINTY_PAUSE_THRESHOLD = 0.85
INTERNAL_AGENT_FILES = frozenset(
    {
        "autobiographical_memory.jsonl",
        REFLECTION_FILENAME,
        CONSTRUCT_LEDGER_FILENAME,
    }
)


@dataclass(frozen=True)
class ConstructStateSummary:
    """Compact construct-runtime snapshot for agent memory and ledgers."""

    tick_id: str
    uncertainty_level: float
    active_goal_ids: tuple[str, ...]
    top_goal_rationales: tuple[str, ...]
    active_percept_count: int
    max_percept_salience: float
    reference_self_constructs: tuple[str, ...]
    json_assets_seen: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "tick_id": self.tick_id,
            "uncertainty_level": round(self.uncertainty_level, 4),
            "active_goal_ids": list(self.active_goal_ids),
            "top_goal_rationales": list(self.top_goal_rationales),
            "active_percept_count": self.active_percept_count,
            "max_percept_salience": round(self.max_percept_salience, 4),
            "reference_self_constructs": list(self.reference_self_constructs),
            "json_assets_seen": self.json_assets_seen,
        }


def summarize_construct_state(
    report: ConstructGroundedMindRuntimeReport,
    *,
    uncertainty_level: float,
    tick_id: str,
) -> ConstructStateSummary:
    saliences = [float(item.get("salience", 0.0) or 0.0) for item in report.active_percepts]
    return ConstructStateSummary(
        tick_id=tick_id,
        uncertainty_level=uncertainty_level,
        active_goal_ids=tuple(goal.goal_id for goal in report.goals[:5]),
        top_goal_rationales=tuple(goal.rationale for goal in report.goals[:3]),
        active_percept_count=len(report.active_percepts),
        max_percept_salience=max(saliences) if saliences else 0.0,
        reference_self_constructs=tuple(
            report.self_model.get("reference_self_constructs", []) or []
        ),
        json_assets_seen=int(report.asset_snapshot.get("json_assets_seen", 0) or 0),
    )


def compute_construct_state_delta(
    before: ConstructStateSummary | None,
    after: ConstructStateSummary | None,
) -> dict[str, Any]:
    if before is None or after is None:
        return {}
    before_goals = set(before.active_goal_ids)
    after_goals = set(after.active_goal_ids)
    return {
        "uncertainty_delta": round(after.uncertainty_level - before.uncertainty_level, 4),
        "goal_ids_added": sorted(after_goals - before_goals),
        "goal_ids_removed": sorted(before_goals - after_goals),
        "max_percept_salience_delta": round(
            after.max_percept_salience - before.max_percept_salience,
            4,
        ),
        "json_assets_seen_delta": after.json_assets_seen - before.json_assets_seen,
    }


class ConstructAwareAgent(SimplePersistentAgent):
    """Sandbox agent whose loop is grounded in construct-runtime ticks."""

    def __init__(
        self,
        workspace: Path,
        *,
        llm_model: str | None = None,
        verbose: bool = True,
        dry_run: bool = False,
        llm_client: Any | None = None,
        llm_timeout_seconds: float = 120.0,
        uncertainty_threshold: float = UNCERTAINTY_PAUSE_THRESHOLD,
    ) -> None:
        super().__init__(
            workspace,
            llm_model=llm_model or "qwen3.5:9b",
            verbose=verbose,
            dry_run=dry_run,
            llm_client=llm_client,
            llm_timeout_seconds=llm_timeout_seconds,
        )
        self.uncertainty_threshold = uncertainty_threshold
        self.construct_ledger_file = self.workspace / CONSTRUCT_LEDGER_FILENAME
        self.last_runtime_report: ConstructGroundedMindRuntimeReport | None = None
        self.last_construct_summary: ConstructStateSummary | None = None
        self.construct_state_history: dict[int, dict[str, Any]] = {}
        self._reflect_steps = 0

    def _filter_workspace_files(self, files: list[str]) -> list[str]:
        return sorted(name for name in files if name not in INTERNAL_AGENT_FILES)

    def _slim_perception_for_memory(self, perception: dict[str, Any]) -> dict[str, Any]:
        slim = dict(perception)
        slim["workspace_files"] = self._filter_workspace_files(
            list(perception.get("workspace_files", []))
        )
        if "global_workspace_state" in slim:
            slim["global_workspace_state"] = {
                "goal_count": slim["global_workspace_state"].get("goal_count"),
                "active_percept_count": len(
                    slim["global_workspace_state"].get("active_percepts", [])
                ),
            }
        if "self_model_state" in slim:
            slim["self_model_state"] = {
                "reference_self_constructs": slim["self_model_state"].get(
                    "reference_self_constructs", []
                )
            }
        if "active_goals" in slim:
            slim["active_goals"] = [
                {"goal_id": goal.get("goal_id"), "goal_type": goal.get("goal_type")}
                for goal in slim.get("active_goals", [])[:3]
            ]
        return slim

    def _build_intention_hints(self, perception: dict[str, Any]) -> str:
        hints = super()._build_intention_hints(perception)
        if self._reflect_steps >= 1 and not self._agent_created_files(perception):
            extra = (
                "Hints:\n"
                "- You already reflected once; prefer write thoughts.txt <summary> next.\n\n"
            )
            return extra + hints
        return hints

    def run_mind_runtime_tick(self) -> ConstructGroundedMindRuntimeReport:
        report = run_construct_grounded_mind_runtime_tick(asset_dirs=[self.workspace])
        self.last_runtime_report = report
        return report

    def estimate_uncertainty(
        self,
        perception: dict[str, Any],
        report: ConstructGroundedMindRuntimeReport,
    ) -> float:
        files = perception["workspace_files"]
        unexplored = [name for name in files if name not in self.explored_files]
        curiosity_gap = 1.0 - float(perception.get("curiosity_level", 0.0) or 0.0)
        unexplored_ratio = len(unexplored) / max(1, len(files))
        goal_pressure = min(1.0, len(report.goals) / 8.0) * 0.25
        percept_pressure = min(1.0, len(report.active_percepts) / 10.0) * 0.15
        return min(1.0, curiosity_gap * 0.45 + unexplored_ratio * 0.35 + goal_pressure + percept_pressure)

    def _propose_construct_intentions(
        self,
        perception: dict[str, Any],
        report: ConstructGroundedMindRuntimeReport,
    ) -> list[str]:
        proposals: list[str] = []
        unexplored = [
            name for name in perception["workspace_files"] if name not in self.explored_files
        ]
        if unexplored:
            proposals.append(f"read {unexplored[0]}")
        if not self._agent_created_files(perception) and len(self.explored_files) >= 2:
            proposals.append(
                "write thoughts.txt I integrated construct-runtime goals with sandbox exploration"
            )
        elif self._reflect_steps == 0 and len(self.explored_files) >= 3:
            proposals.append("reflect")
        if not proposals:
            proposals.append("explore")
        return proposals

    def perceive(self) -> dict[str, Any]:
        basic = super().perceive()
        report = self.run_mind_runtime_tick()
        uncertainty = self.estimate_uncertainty(basic, report)
        summary = summarize_construct_state(
            report,
            uncertainty_level=uncertainty,
            tick_id=f"tick_{self.step_count}",
        )
        self.last_construct_summary = summary
        basic["workspace_files"] = self._filter_workspace_files(basic["workspace_files"])
        return {
            **basic,
            "construct_state": summary.to_dict(),
            "global_workspace_state": {
                "active_percepts": list(report.active_percepts[:5]),
                "goal_count": len(report.goals),
            },
            "self_model_state": report.self_model,
            "uncertainty_level": round(uncertainty, 4),
            "active_goals": [goal.to_dict() for goal in report.goals[:5]],
        }

    def generate_intention(self, perception: dict[str, Any]) -> str:
        uncertainty = float(perception.get("uncertainty_level", 0.0) or 0.0)
        if self._reflect_steps >= 2:
            return "rest"
        if uncertainty >= self.uncertainty_threshold:
            self._log(
                f"High uncertainty ({uncertainty:.2f}); preferring reflect before new action"
            )
            return "reflect"

        report = self.last_runtime_report
        if report is None:
            return super().generate_intention(perception)

        if self.dry_run or self.llm_client is None:
            return self._propose_construct_intentions(perception, report)[0]

        proposals = self._propose_construct_intentions(perception, report)
        user_prompt = (
            "Current state:\n"
            f"- workspace files: {perception['workspace_files']}\n"
            f"- explored files: {perception['explored_files']}\n"
            f"- written files: {sorted(self.written_files)}\n"
            f"- uncertainty: {uncertainty:.2f}\n"
            f"- active goals: {json.dumps(perception.get('active_goals', [])[:3], ensure_ascii=False)}\n"
            f"- reference self constructs: {perception.get('self_model_state', {}).get('reference_self_constructs', [])}\n\n"
            f"{self._build_intention_hints(perception)}"
            "Construct-runtime proposed intentions:\n"
            + "\n".join(f"- {item}" for item in proposals)
            + "\n\nReply with ONE action line only."
        )
        raw = self.call_llm(user_prompt)
        return parse_agent_intention(raw)

    def execute_action(self, intention: str) -> dict[str, Any]:
        parts = intention.strip().split(maxsplit=1)
        if parts and parts[0].lower() == "read" and len(parts) > 1:
            target = parts[1].strip()
            if target in INTERNAL_AGENT_FILES:
                intention = "write thoughts.txt summarizing construct-aware exploration so far"

        pre_summary = self.last_construct_summary
        outcome = super().execute_action(intention)
        if outcome.get("action") == "reflect":
            self._reflect_steps += 1
        basic = super().perceive()
        report = self.run_mind_runtime_tick()
        post_uncertainty = self.estimate_uncertainty(basic, report)
        post_summary = summarize_construct_state(
            report,
            uncertainty_level=post_uncertainty,
            tick_id=f"tick_{self.step_count}_post",
        )
        self.last_construct_summary = post_summary
        self.last_runtime_report = report
        outcome["construct_state_delta"] = compute_construct_state_delta(pre_summary, post_summary)
        outcome["construct_state_after"] = post_summary.to_dict()
        return outcome

    def record_memory(self, entry: dict[str, Any]) -> None:
        perception = entry.get("perception")
        if isinstance(perception, dict):
            entry = {**entry, "perception": self._slim_perception_for_memory(perception)}
        enriched = {
            **entry,
            "construct_summary": (
                self.last_construct_summary.to_dict() if self.last_construct_summary else None
            ),
        }
        super().record_memory(enriched)
        if self.last_construct_summary is not None:
            self.construct_state_history[self.step_count] = self.last_construct_summary.to_dict()
            ledger_entry = {
                "timestamp": datetime.now().isoformat(),
                "step": self.step_count,
                "intention": entry.get("intention"),
                "construct_summary": self.last_construct_summary.to_dict(),
                "construct_state_delta": (entry.get("outcome") or {}).get("construct_state_delta"),
            }
            with self.construct_ledger_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(ledger_entry, ensure_ascii=False) + "\n")


def talk_to_agent(
    workspace: Path,
    *,
    question: str,
    llm_model: str = "qwen3.5:9b",
    dry_run: bool = False,
) -> str:
    """Read-only dialogue against recent agent memory (no sandbox mutation)."""
    memory_file = workspace / "autobiographical_memory.jsonl"
    reflection_file = workspace / "reflections.txt"
    if not memory_file.exists():
        raise FileNotFoundError(f"Missing agent memory: {memory_file}")

    recent_lines = memory_file.read_text(encoding="utf-8").splitlines()[-8:]
    reflections = (
        reflection_file.read_text(encoding="utf-8") if reflection_file.exists() else ""
    )
    recent = [json.loads(line) for line in recent_lines if line.strip()]
    digest = [
        {
            "step": row.get("step"),
            "intention": row.get("intention"),
            "action": (row.get("outcome") or {}).get("action"),
            "filename": (row.get("outcome") or {}).get("filename"),
            "construct_summary": row.get("construct_summary"),
        }
        for row in recent
    ]
    context = {
        "recent_memory": digest,
        "reflections_excerpt": reflections[-1200:],
        "question": question,
    }

    if dry_run:
        last_intention = recent[-1].get("intention") if recent else "unknown"
        return (
            f"[dry-run] Based on recent memory, last intention was {last_intention}. "
            f"Question received: {question}"
        )

    from consciousness_benchmark.constructs.local_llm import (
        DEFAULT_PERSISTENT_AGENT_MODEL,
        OllamaAdapter,
        extract_reflection_narrative,
        extract_visible_llm_response,
    )

    adapter = OllamaAdapter(timeout_seconds=120.0)
    result = adapter.generate(
        model=llm_model or DEFAULT_PERSISTENT_AGENT_MODEL,
        prompt=(
            "Answer the operator question using only the agent memory excerpt. "
            "Do not claim consciousness. Be concise.\n\n"
            f"Context JSON:\n{json.dumps(context, ensure_ascii=False, indent=2)}"
        ),
        system=(
            "You are a read-only interpreter of a bounded cognitive agent ledger. "
            "Never mutate files or claim subjective consciousness."
        ),
        options={"temperature": 0.2, "num_predict": 1024},
    )
    final = str(result.raw.get("response") or "")
    if final.strip():
        return extract_visible_llm_response(final)
    return extract_reflection_narrative(result.response_text, final_response=final)


def main() -> None:
    import argparse

    from consciousness_benchmark.constructs.local_llm import DEFAULT_PERSISTENT_AGENT_MODEL

    parser = argparse.ArgumentParser(description="Run construct-aware persistent agent")
    parser.add_argument("--workspace", type=Path, default=Path("sandbox/construct_agent"))
    parser.add_argument("--llm", default=DEFAULT_PERSISTENT_AGENT_MODEL)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--setup-demo", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--talk", type=str, default=None, help="Ask a read-only question and exit")
    args = parser.parse_args()

    if args.setup_demo or not args.workspace.exists():
        from consciousness_benchmark.simple_persistent_agent import setup_demo_workspace

        setup_demo_workspace(args.workspace)

    if args.talk:
        answer = talk_to_agent(
            args.workspace,
            question=args.talk,
            llm_model=args.llm,
            dry_run=args.dry_run,
        )
        print(answer)
        return

    agent = ConstructAwareAgent(
        workspace=args.workspace,
        llm_model=args.llm,
        verbose=not args.quiet,
        dry_run=args.dry_run,
    )
    agent.live(max_steps=args.steps, step_interval=args.interval)


if __name__ == "__main__":
    main()
