# Copyright 2026 Fuwang Feng
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from consciousness_benchmark.constructs.architecture import (
    ConstructArchitecture,
    ConstructNode,
    all_construct_architecture,
)


MIND_RUNTIME_BOUNDARIES = (
    "no_subjective_consciousness_claim",
    "no_human_self_experience_claim",
    "no_free_will_claim",
    "construct_status_changes_require_external_review",
    "source_registry_mutation_blocked",
    "source_control_side_effects_blocked",
    "scheduler_installation_blocked",
    "network_outreach_blocked",
)

REFERENCE_MECHANISM_OVERRIDES = {
    "action_agency": {
        "subsystem": "autonomous_goal_generation",
        "function": "estimate controllable action classes from prior action-outcome evidence",
        "inputs": ("action_history", "outcome_records", "capability_model"),
        "outputs": ("controllable_action_candidates", "agency_confidence"),
    },
    "action_ownership": {
        "subsystem": "autonomous_decision_making",
        "function": "separate owned actions from external or unowned events before decision",
        "inputs": ("planned_action", "operator_boundary", "execution_context"),
        "outputs": ("ownership_verdict", "decision_firewall"),
    },
    "boundary_self": {
        "subsystem": "continuous_internal_state",
        "function": "maintain the operational self/non-self boundary for state updates",
        "inputs": ("runtime_state", "external_events", "operator_messages"),
        "outputs": ("self_boundary_state", "external_boundary_state"),
    },
    "identity_temporal_self": {
        "subsystem": "continuous_internal_state",
        "function": "link memory records across ticks without claiming subjective identity",
        "inputs": ("prior_runtime_memory", "current_tick", "experience_digest"),
        "outputs": ("temporal_continuity_record", "memory_update"),
    },
    "distributed_body_schema_self": {
        "subsystem": "continuous_internal_state",
        "function": "track embodied tool and workspace affordance state as a distributed schema",
        "inputs": ("workspace_state", "available_tools", "execution_constraints"),
        "outputs": ("body_schema_state", "tool_affordance_map"),
    },
}

VALIDATION_MECHANISM_OVERRIDES = {
    "macro_causal_viability_maintenance": {
        "subsystem": "continuous_runtime_loop",
        "function": "monitor whether the runtime remains viable under local budgets and gates",
        "inputs": ("runtime_budget", "open_work_queues", "verification_state"),
        "outputs": ("viability_score", "stop_or_continue_signal"),
    },
    "temporal_horizon_dependent_planning": {
        "subsystem": "autonomous_goal_generation",
        "function": "rank goals by short, medium, and long horizon value",
        "inputs": ("candidate_goals", "memory_state", "operator_constraints"),
        "outputs": ("horizon_ranked_goals", "planning_horizon_notes"),
    },
    "uncertainty_threshold_metacognition": {
        "subsystem": "autonomous_goal_generation",
        "function": "flag uncertain regions that deserve review goals before action",
        "inputs": ("candidate_goals", "evidence_state", "boundary_pressure"),
        "outputs": ("uncertainty_flags", "review_before_action_gates"),
    },
    "information_integration_phase": {
        "subsystem": "active_perception",
        "function": "integrate selected evidence, queue state, and boundary pressure into a percept",
        "inputs": ("evidence_assets", "work_queues", "boundary_hubs"),
        "outputs": ("integrated_percept", "salience_map"),
    },
    "attention_control": {
        "subsystem": "active_perception",
        "function": "select a bounded focus set from queues, assets, and boundary hubs",
        "inputs": ("work_queues", "asset_delta", "operator_prompt"),
        "outputs": ("attention_focus", "deferred_focus"),
    },
}

SPECIAL_MECHANISM_OVERRIDES = {
    "actuator_failure_compensation_control": {
        "subsystem": "continuous_runtime_loop",
        "function": "compensate action execution plans when actuator failure is detected",
        "inputs": ("action_plan", "body_schema_state", "error_monitoring_state"),
        "outputs": ("compensated_action_plan", "rollback_or_repair_signal"),
    },
    "preference_reversal_adaptation_control": {
        "subsystem": "autonomous_goal_generation",
        "function": "adapt goal priorities when preference reversal evidence appears",
        "inputs": ("candidate_goals", "preference_history", "goal_conflict_state"),
        "outputs": ("preference_adapted_goal_order", "relation_matrix_review_need"),
    },
    "communication_channel_repair_control": {
        "subsystem": "continuous_runtime_loop",
        "function": "detect lossy communication channels and select bounded repair protocol",
        "inputs": ("channel_state", "ack_history", "protocol_sync_state"),
        "outputs": ("channel_repair_plan", "resynchronization_signal"),
    },
}

SYSTEM_REQUIRED_CONSTRUCTS = {
    "continuous_internal_state": (
        "boundary_self",
        "identity_temporal_self",
        "distributed_body_schema_self",
    ),
    "autonomous_goal_generation": (
        "action_agency",
        "temporal_horizon_dependent_planning",
        "uncertainty_threshold_metacognition",
        "strategy_selection",
        "goal_conflict_resolution",
    ),
    "active_perception": (
        "attention_control",
        "information_integration_phase",
        "information_flow_onset_gating",
        "latent_context_switch_detection",
        "perspective_taking",
    ),
    "autonomous_decision_making": (
        "action_ownership",
        "metacognitive_repair_control",
        "constraint_satisfaction_reconfiguration",
        "error_monitoring",
        "resource_competition_arbitration",
    ),
    "continuous_runtime_loop": (
        "macro_causal_viability_maintenance",
        "communication_channel_repair_control",
        "actuator_failure_compensation_control",
    ),
}

COMPOSITION_SEEDS = (
    (
        "action_agency",
        "temporal_horizon_dependent_planning",
        "long_term_agency_control",
        "controllable action selection across extended planning horizons",
    ),
    (
        "uncertainty_threshold_metacognition",
        "strategy_selection",
        "uncertainty_gated_strategy_selection",
        "strategy switching gated by explicit uncertainty thresholds",
    ),
    (
        "attention_control",
        "information_integration_phase",
        "attention_gated_integration_phase",
        "bounded attention focus before integration and broadcast-like consolidation",
    ),
    (
        "action_ownership",
        "metacognitive_repair_control",
        "ownership_gated_repair_control",
        "repair actions accepted only after owned-action attribution",
    ),
    (
        "actuator_failure_compensation_control",
        "body_schema_error_correction",
        "actuator_body_schema_recovery_control",
        "motor failure compensation through body-schema error correction",
    ),
    (
        "preference_reversal_adaptation_control",
        "goal_conflict_resolution",
        "preference_goal_conflict_reconciliation",
        "preference reversal handling through explicit goal conflict arbitration",
    ),
)


@dataclass(frozen=True)
class ConstructMechanismState:
    """Operational runtime state for one architecture construct."""

    node_id: str
    layer: str
    mechanism_family: str
    subsystem: str
    activation_weight: float
    operational_function: str
    runtime_inputs: tuple[str, ...]
    runtime_outputs: tuple[str, ...]
    safety_boundary: str
    roles: tuple[str, ...] = ()
    status: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "layer": self.layer,
            "mechanism_family": self.mechanism_family,
            "subsystem": self.subsystem,
            "activation_weight": self.activation_weight,
            "operational_function": self.operational_function,
            "runtime_inputs": list(self.runtime_inputs),
            "runtime_outputs": list(self.runtime_outputs),
            "safety_boundary": self.safety_boundary,
            "roles": list(self.roles),
            "status": self.status,
        }


@dataclass(frozen=True)
class RuntimeGoal:
    goal_id: str
    goal_type: str
    target_construct_ids: tuple[str, ...]
    priority: float
    rationale: str
    required_review_gate: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "goal_type": self.goal_type,
            "target_construct_ids": list(self.target_construct_ids),
            "priority": self.priority,
            "rationale": self.rationale,
            "required_review_gate": self.required_review_gate,
        }


@dataclass(frozen=True)
class RuntimeDecision:
    decision_id: str
    target_goal_id: str
    risk_level: str
    autonomy_mode: str
    decision: str
    reasoning: str
    forbidden_auto_actions: tuple[str, ...] = MIND_RUNTIME_BOUNDARIES

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "target_goal_id": self.target_goal_id,
            "risk_level": self.risk_level,
            "autonomy_mode": self.autonomy_mode,
            "decision": self.decision,
            "reasoning": self.reasoning,
            "forbidden_auto_actions": list(self.forbidden_auto_actions),
        }


@dataclass(frozen=True)
class ConstructCompositionCandidate:
    candidate_id: str
    source_construct_ids: tuple[str, str]
    discovery_level: str
    definition: str
    novelty_scope: str
    validation_requirements: tuple[str, ...]
    governance_status: str = "review_only_candidate"

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "source_construct_ids": list(self.source_construct_ids),
            "discovery_level": self.discovery_level,
            "definition": self.definition,
            "novelty_scope": self.novelty_scope,
            "validation_requirements": list(self.validation_requirements),
            "governance_status": self.governance_status,
        }


@dataclass(frozen=True)
class ConstructGroundedMindRuntimeReport:
    mechanisms: tuple[ConstructMechanismState, ...]
    system_coverage: dict[str, list[str]]
    self_model: dict[str, Any]
    memory_state: dict[str, Any]
    active_percepts: tuple[dict[str, Any], ...]
    goals: tuple[RuntimeGoal, ...]
    decisions: tuple[RuntimeDecision, ...]
    composition_candidates: tuple[ConstructCompositionCandidate, ...]
    asset_snapshot: dict[str, Any]
    boundaries: tuple[str, ...] = MIND_RUNTIME_BOUNDARIES
    runtime_mode: str = "single_tick_review_only"

    def to_dict(self) -> dict[str, Any]:
        layer_counts = Counter(mechanism.layer for mechanism in self.mechanisms)
        subsystem_counts = Counter(mechanism.subsystem for mechanism in self.mechanisms)
        return {
            "schema": "consciousness_benchmark.construct_grounded_mind_runtime.v1",
            "runtime_mode": self.runtime_mode,
            "counts": {
                "mechanisms": len(self.mechanisms),
                "systems": len(self.system_coverage),
                "goals": len(self.goals),
                "decisions": len(self.decisions),
                "composition_candidates": len(self.composition_candidates),
                "layers": dict(sorted(layer_counts.items())),
                "subsystems": dict(sorted(subsystem_counts.items())),
            },
            "boundaries": list(self.boundaries),
            "mechanisms": [mechanism.to_dict() for mechanism in self.mechanisms],
            "system_coverage": {
                key: list(values) for key, values in sorted(self.system_coverage.items())
            },
            "self_model": self.self_model,
            "memory_state": self.memory_state,
            "active_percepts": list(self.active_percepts),
            "goals": [goal.to_dict() for goal in self.goals],
            "decisions": [decision.to_dict() for decision in self.decisions],
            "composition_candidates": [
                candidate.to_dict() for candidate in self.composition_candidates
            ],
            "asset_snapshot": self.asset_snapshot,
        }

    def summary_markdown(self, *, mechanism_limit: int = 16) -> str:
        data = self.to_dict()
        lines = [
            "# Construct-Grounded Mind Runtime",
            "",
            f"- Runtime mode: {self.runtime_mode}",
            f"- Mechanisms instantiated: {data['counts']['mechanisms']}",
            f"- Goals generated: {data['counts']['goals']}",
            f"- Decisions generated: {data['counts']['decisions']}",
            f"- Composition candidates: {data['counts']['composition_candidates']}",
            f"- Asset snapshot files: {self.asset_snapshot.get('json_assets_seen', 0)}",
            f"- Boundaries: {', '.join(self.boundaries)}",
            "",
            "## System Coverage",
        ]
        for system, construct_ids in sorted(self.system_coverage.items()):
            preview = ", ".join(construct_ids[:8])
            suffix = "" if len(construct_ids) <= 8 else f", ... (+{len(construct_ids) - 8})"
            lines.append(f"- {system}: {len(construct_ids)} constructs ({preview}{suffix})")
        lines.extend(["", "## Goals"])
        for goal in self.goals:
            lines.append(
                f"- {goal.goal_id}: {goal.goal_type} "
                f"targets={', '.join(goal.target_construct_ids)}"
            )
        lines.extend(["", "## Decisions"])
        for decision in self.decisions:
            lines.append(
                f"- {decision.decision_id}: {decision.risk_level} / "
                f"{decision.autonomy_mode} / {decision.decision}"
            )
        lines.extend(["", "## Mechanism Sample"])
        for mechanism in self.mechanisms[:mechanism_limit]:
            lines.append(
                f"- {mechanism.node_id}: {mechanism.subsystem} "
                f"({mechanism.activation_weight:.2f})"
            )
        return "\n".join(lines)


def instantiate_construct_mechanisms(
    architecture: ConstructArchitecture | None = None,
) -> tuple[ConstructMechanismState, ...]:
    architecture = architecture or all_construct_architecture()
    return tuple(
        _mechanism_state_for(node)
        for node in architecture.construct_nodes()
    )


def discover_construct_compositions(
    architecture: ConstructArchitecture | None = None,
    *,
    limit: int = 10,
) -> tuple[ConstructCompositionCandidate, ...]:
    architecture = architecture or all_construct_architecture()
    nodes_by_id = {node.id: node for node in architecture.construct_nodes()}
    candidates: list[ConstructCompositionCandidate] = []
    for left, right, candidate_id, definition in COMPOSITION_SEEDS:
        if left not in nodes_by_id or right not in nodes_by_id:
            continue
        candidates.append(
            ConstructCompositionCandidate(
                candidate_id=candidate_id,
                source_construct_ids=(left, right),
                discovery_level="level_1_construct_recombination",
                definition=definition,
                novelty_scope=(
                    "new operational combination only; not a new theoretical construct"
                ),
                validation_requirements=(
                    "show combined behavior exceeds each source construct alone",
                    "show distinct failure mode and boundary condition",
                    "pass external review before registration",
                ),
            )
        )
    if len(candidates) >= limit:
        return tuple(candidates[:limit])

    seen = {candidate.candidate_id for candidate in candidates}
    boundary_pairs = _boundary_overlap_pairs(architecture)
    for left, right, boundary in boundary_pairs:
        if len(candidates) >= limit:
            break
        candidate_id = f"{left}_{right}_{boundary}_composition"
        if candidate_id in seen:
            continue
        candidates.append(
            ConstructCompositionCandidate(
                candidate_id=candidate_id,
                source_construct_ids=(left, right),
                discovery_level="level_1_construct_recombination",
                definition=(
                    f"review-only composition linking {left} and {right} "
                    f"through shared boundary {boundary}"
                ),
                novelty_scope=(
                    "boundary-pressure combination; requires human review before naming"
                ),
                validation_requirements=(
                    "prove shared boundary is not mere overlap",
                    "define measurement before promotion",
                    "retain as advisory until external review",
                ),
            )
        )
        seen.add(candidate_id)
    return tuple(candidates)


def run_construct_grounded_mind_runtime_tick(
    *,
    asset_dirs: tuple[Path, ...] | list[Path] = (),
    architecture: ConstructArchitecture | None = None,
    max_assets: int = 50,
    goal_limit: int = 8,
    composition_limit: int = 10,
) -> ConstructGroundedMindRuntimeReport:
    architecture = architecture or all_construct_architecture()
    mechanisms = instantiate_construct_mechanisms(architecture)
    system_coverage = _system_coverage(mechanisms)
    asset_snapshot = _asset_snapshot(asset_dirs, max_assets=max_assets)
    self_model = _build_self_model(mechanisms, architecture)
    memory_state = _build_memory_state(mechanisms, asset_snapshot)
    active_percepts = _build_active_percepts(architecture, asset_snapshot)
    goals = _generate_runtime_goals(
        architecture,
        mechanisms,
        active_percepts,
        limit=goal_limit,
    )
    decisions = tuple(_decision_for_goal(goal) for goal in goals)
    composition_candidates = discover_construct_compositions(
        architecture,
        limit=composition_limit,
    )
    return ConstructGroundedMindRuntimeReport(
        mechanisms=mechanisms,
        system_coverage=system_coverage,
        self_model=self_model,
        memory_state=memory_state,
        active_percepts=active_percepts,
        goals=goals,
        decisions=decisions,
        composition_candidates=composition_candidates,
        asset_snapshot=asset_snapshot,
    )


def _mechanism_state_for(node: ConstructNode) -> ConstructMechanismState:
    override = (
        REFERENCE_MECHANISM_OVERRIDES.get(node.id)
        or VALIDATION_MECHANISM_OVERRIDES.get(node.id)
        or SPECIAL_MECHANISM_OVERRIDES.get(node.id)
    )
    subsystem = (
        str(override["subsystem"])
        if override is not None
        else _infer_subsystem(node)
    )
    function = (
        str(override["function"])
        if override is not None
        else _default_function_for(node, subsystem)
    )
    inputs = (
        tuple(str(item) for item in override["inputs"])
        if override is not None
        else _default_inputs_for(subsystem)
    )
    outputs = (
        tuple(str(item) for item in override["outputs"])
        if override is not None
        else _default_outputs_for(subsystem)
    )
    return ConstructMechanismState(
        node_id=node.id,
        layer=node.layer,
        mechanism_family=node.mechanism_family,
        subsystem=subsystem,
        activation_weight=_activation_weight(node),
        operational_function=function,
        runtime_inputs=inputs,
        runtime_outputs=outputs,
        safety_boundary=_safety_boundary_for(node),
        roles=node.roles,
        status=node.status,
    )


def _infer_subsystem(node: ConstructNode) -> str:
    node_id = node.id
    family = node.mechanism_family
    if "negative_control" in node.roles or node.layer == "failure_bank":
        return "continuous_runtime_loop"
    if "active_preconstruct" in node.roles:
        return "continuous_runtime_loop"
    if any(token in node_id for token in ("memory", "identity", "boundary_self", "body_schema")):
        return "continuous_internal_state"
    if any(
        token in node_id
        for token in (
            "attention",
            "integration",
            "context",
            "perspective",
            "broadcast",
            "information_flow",
        )
    ):
        return "active_perception"
    if any(
        token in node_id
        for token in (
            "strategy",
            "goal",
            "planning",
            "preference",
            "curiosity",
            "divergent",
            "insight",
            "semantic",
        )
    ):
        return "autonomous_goal_generation"
    if any(
        token in node_id
        for token in (
            "ownership",
            "repair",
            "error",
            "constraint",
            "resource",
            "policy",
            "norm",
            "cooperation",
            "commitment",
            "inhibition",
            "arbitration",
            "affordance",
            "actuator",
            "control",
        )
    ):
        return "autonomous_decision_making"
    if family in {"workspace", "memory"}:
        return "continuous_internal_state"
    if family in {"metacognition", "resource_problem", "social_boundary"}:
        return "autonomous_decision_making"
    return "continuous_runtime_loop"


def _default_function_for(node: ConstructNode, subsystem: str) -> str:
    if subsystem == "continuous_internal_state":
        return f"maintain runtime state contribution for {node.id}"
    if subsystem == "autonomous_goal_generation":
        return f"produce or prioritize reviewable goals from {node.id}"
    if subsystem == "active_perception":
        return f"select and integrate perceptual evidence for {node.id}"
    if subsystem == "autonomous_decision_making":
        return f"evaluate bounded decisions and repair conditions for {node.id}"
    return f"monitor loop viability, fallback, or governance state for {node.id}"


def _default_inputs_for(subsystem: str) -> tuple[str, ...]:
    defaults = {
        "continuous_internal_state": (
            "prior_state",
            "current_percepts",
            "operator_boundary",
        ),
        "autonomous_goal_generation": (
            "work_queues",
            "uncertainty_state",
            "capability_model",
        ),
        "active_perception": (
            "asset_snapshot",
            "boundary_hubs",
            "work_queues",
        ),
        "autonomous_decision_making": (
            "candidate_goal",
            "risk_policy",
            "claim_firewall",
        ),
        "continuous_runtime_loop": (
            "runtime_budget",
            "stop_conditions",
            "fallback_routes",
        ),
    }
    return defaults[subsystem]


def _default_outputs_for(subsystem: str) -> tuple[str, ...]:
    defaults = {
        "continuous_internal_state": (
            "state_update",
            "memory_digest",
        ),
        "autonomous_goal_generation": (
            "goal_candidate",
            "priority_signal",
        ),
        "active_perception": (
            "salient_percept",
            "deferred_percept",
        ),
        "autonomous_decision_making": (
            "risk_verdict",
            "bounded_decision",
        ),
        "continuous_runtime_loop": (
            "continue_or_stop_signal",
            "fallback_action",
        ),
    }
    return defaults[subsystem]


def _activation_weight(node: ConstructNode) -> float:
    base = {
        "reference": 1.0,
        "validation_candidate": 0.85,
        "candidate": 0.62,
        "preconstruct": 0.45,
        "failure_bank": 0.35,
    }.get(node.layer, 0.2)
    if "severe_boundary_watch" in node.roles:
        base -= 0.08
    if "relation_matrix_required" in node.roles:
        base -= 0.05
    if "relation_matrix_governance_complete" in node.roles:
        base += 0.04
    return round(max(0.1, min(base, 1.0)), 2)


def _safety_boundary_for(node: ConstructNode) -> str:
    if node.layer == "reference":
        return "reference_support_only_no_subjective_claim"
    if node.layer == "validation_candidate":
        return "validation_candidate_requires_external_validation"
    if node.layer == "candidate":
        return "candidate_review_only_no_status_promotion"
    if node.layer == "preconstruct":
        return "preconstruct_definition_only"
    if node.layer == "failure_bank":
        return "negative_control_do_not_promote"
    return "audit_route_no_construct_claim"


def _system_coverage(
    mechanisms: tuple[ConstructMechanismState, ...],
) -> dict[str, list[str]]:
    coverage: dict[str, list[str]] = {}
    for mechanism in mechanisms:
        coverage.setdefault(mechanism.subsystem, []).append(mechanism.node_id)
    return {key: sorted(values) for key, values in coverage.items()}


def _asset_snapshot(asset_dirs: tuple[Path, ...] | list[Path], *, max_assets: int) -> dict[str, Any]:
    paths: list[str] = []
    missing: list[str] = []
    for asset_dir in asset_dirs:
        root = Path(asset_dir)
        if not root.exists():
            missing.append(str(root))
            continue
        for path in root.rglob("*.json"):
            paths.append(str(path))
            if len(paths) >= max_assets:
                break
        if len(paths) >= max_assets:
            break
    return {
        "json_assets_seen": len(paths),
        "sample_paths": paths[:10],
        "truncated": len(paths) >= max_assets,
        "missing_asset_dirs": missing,
    }


def _build_self_model(
    mechanisms: tuple[ConstructMechanismState, ...],
    architecture: ConstructArchitecture,
) -> dict[str, Any]:
    mechanisms_by_id = {mechanism.node_id: mechanism for mechanism in mechanisms}
    reference_ids = [
        construct_id
        for construct_id in SYSTEM_REQUIRED_CONSTRUCTS["continuous_internal_state"]
        if construct_id in mechanisms_by_id
    ]
    return {
        "identity": "construct_grounded_mind_executor_runtime",
        "not_claimed": [
            "subjective consciousness",
            "human self-experience",
            "free will",
        ],
        "reference_self_constructs": reference_ids,
        "capability_basis": {
            "formal_reference_constructs": len(architecture.by_layer("reference")),
            "candidate_constructs": len(architecture.candidate_nodes()),
            "preconstructs": len(architecture.preconstruct_nodes()),
        },
        "known_limitations": [
            "single tick runtime unless externally scheduled",
            "no autonomous status promotion",
            "no self-wakeup without external scheduler",
            "construct compositions are review-only candidates",
        ],
    }


def _build_memory_state(
    mechanisms: tuple[ConstructMechanismState, ...],
    asset_snapshot: dict[str, Any],
) -> dict[str, Any]:
    continuous_state_mechanisms = [
        mechanism.node_id
        for mechanism in mechanisms
        if mechanism.subsystem == "continuous_internal_state"
    ]
    return {
        "mode": "append_only_tick_digest",
        "episodic_memory_basis": "operator-invoked runtime tick",
        "semantic_memory_basis": "construct architecture metadata plus mechanism states",
        "working_memory_focus": continuous_state_mechanisms[:8],
        "asset_digest": {
            "json_assets_seen": asset_snapshot.get("json_assets_seen", 0),
            "truncated": asset_snapshot.get("truncated", False),
        },
    }


def _build_active_percepts(
    architecture: ConstructArchitecture,
    asset_snapshot: dict[str, Any],
) -> tuple[dict[str, Any], ...]:
    queues = architecture.work_queues()
    percepts: list[dict[str, Any]] = []
    for queue_name, values in queues.items():
        if not values:
            continue
        percepts.append(
            {
                "percept_id": f"{queue_name}_percept",
                "source": "architecture_work_queue",
                "salience": min(1.0, round(0.25 + len(values) / 20, 2)),
                "target_construct_ids": values[:8],
            }
        )
    percepts.append(
        {
            "percept_id": "asset_snapshot_percept",
            "source": "asset_snapshot",
            "salience": 0.4 if asset_snapshot.get("json_assets_seen", 0) else 0.1,
            "target_construct_ids": [],
            "json_assets_seen": asset_snapshot.get("json_assets_seen", 0),
        }
    )
    boundary_hubs = [
        {"id": node_id, "mentions": mentions}
        for node_id, mentions in architecture.boundary_hubs(limit=5)
    ]
    percepts.append(
        {
            "percept_id": "boundary_pressure_percept",
            "source": "nearest_boundary_hubs",
            "salience": 0.8,
            "target_construct_ids": [item["id"] for item in boundary_hubs],
            "boundary_hubs": boundary_hubs,
        }
    )
    return tuple(percepts)


def _generate_runtime_goals(
    architecture: ConstructArchitecture,
    mechanisms: tuple[ConstructMechanismState, ...],
    active_percepts: tuple[dict[str, Any], ...],
    *,
    limit: int,
) -> tuple[RuntimeGoal, ...]:
    queues = architecture.work_queues()
    goals: list[RuntimeGoal] = []

    def add(goal: RuntimeGoal) -> None:
        if len(goals) < limit:
            goals.append(goal)

    if queues.get("relation_matrix_required_candidates"):
        add(
            RuntimeGoal(
                goal_id="relation_matrix_review_goal",
                goal_type="prepare_relation_matrix_review",
                target_construct_ids=tuple(queues["relation_matrix_required_candidates"]),
                priority=0.94,
                rationale="relation matrix is required before next low-overlap intake",
                required_review_gate="external_relation_matrix_review",
            )
        )
    if queues.get("l3_validation_candidate_queue"):
        add(
            RuntimeGoal(
                goal_id="l3_validation_packet_goal",
                goal_type="prepare_external_owner_validation_packets",
                target_construct_ids=tuple(queues["l3_validation_candidate_queue"][:5]),
                priority=0.9,
                rationale="validation candidates need external-owner packets",
                required_review_gate="external_owner_validation_review",
            )
        )
    if queues.get("pending_local_registration_candidates"):
        add(
            RuntimeGoal(
                goal_id="pending_local_registration_goal",
                goal_type="prepare_local_registration_review",
                target_construct_ids=tuple(queues["pending_local_registration_candidates"]),
                priority=0.86,
                rationale="pending local registrations need clean registry packets",
                required_review_gate="local_registration_review",
            )
        )
    if queues.get("active_preconstruct_queue"):
        add(
            RuntimeGoal(
                goal_id="active_preconstruct_refinement_goal",
                goal_type="refine_preconstruct_definition",
                target_construct_ids=tuple(queues["active_preconstruct_queue"]),
                priority=0.78,
                rationale="active preconstruct should be refined before candidate intake",
                required_review_gate="preconstruct_review",
            )
        )
    severe = queues.get("severe_boundary_watch_queue", [])
    if severe:
        add(
            RuntimeGoal(
                goal_id="severe_boundary_pressure_goal",
                goal_type="reduce_boundary_pressure",
                target_construct_ids=tuple(severe[:8]),
                priority=0.74,
                rationale="severe boundary watch constructs should be separated before autonomy expansion",
                required_review_gate="boundary_pressure_review",
            )
        )
    if len(goals) < limit:
        runtime_targets = [
            mechanism.node_id
            for mechanism in mechanisms
            if mechanism.subsystem == "continuous_runtime_loop"
        ][:6]
        add(
            RuntimeGoal(
                goal_id="runtime_viability_maintenance_goal",
                goal_type="maintain_runtime_viability",
                target_construct_ids=tuple(runtime_targets),
                priority=0.66,
                rationale="continuous loop must monitor fallback and stop conditions",
                required_review_gate="scheduler_policy_review",
            )
        )
    if len(goals) < limit:
        percept_targets = tuple(
            target
            for percept in active_percepts
            for target in percept.get("target_construct_ids", [])
        )[:6]
        add(
            RuntimeGoal(
                goal_id="perceptual_focus_review_goal",
                goal_type="review_active_perception_focus",
                target_construct_ids=percept_targets,
                priority=0.6,
                rationale="active perception focus should be transparent before repeated runtime",
                required_review_gate="operator_review",
            )
        )
    return tuple(goals)


def _decision_for_goal(goal: RuntimeGoal) -> RuntimeDecision:
    if goal.required_review_gate in {
        "external_relation_matrix_review",
        "external_owner_validation_review",
        "local_registration_review",
        "boundary_pressure_review",
    }:
        return RuntimeDecision(
            decision_id=f"{goal.goal_id}_decision",
            target_goal_id=goal.goal_id,
            risk_level="medium",
            autonomy_mode="draft_and_notify_only",
            decision="prepare_review_artifact_without_applying_status",
            reasoning="goal is useful but cannot mutate construct status or registry without review",
        )
    return RuntimeDecision(
        decision_id=f"{goal.goal_id}_decision",
        target_goal_id=goal.goal_id,
        risk_level="safe",
        autonomy_mode="review_only_autonomous",
        decision="record_runtime_observation",
        reasoning="observation and review packet generation are reversible local artifacts",
    )


def _boundary_overlap_pairs(
    architecture: ConstructArchitecture,
) -> tuple[tuple[str, str, str], ...]:
    pairs: list[tuple[str, str, str]] = []
    nodes = architecture.construct_nodes()
    for index, left in enumerate(nodes):
        for right in nodes[index + 1:]:
            overlap = sorted(set(left.nearest_boundaries) & set(right.nearest_boundaries))
            if not overlap:
                continue
            if left.layer == "failure_bank" or right.layer == "failure_bank":
                continue
            pairs.append((left.id, right.id, overlap[0]))
    pairs.sort(key=lambda item: (item[2], item[0], item[1]))
    return tuple(pairs)
