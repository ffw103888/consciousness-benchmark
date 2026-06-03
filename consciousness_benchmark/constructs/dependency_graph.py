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

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from typing import Any

from consciousness_benchmark.constructs.architecture import (
    ConstructArchitecture,
    ConstructNode,
    all_construct_architecture,
)


LAYER_NAMES = {
    0: "infrastructure",
    1: "basic_perception_action",
    2: "self_model",
    3: "advanced_control",
    4: "integration_coordination",
    5: "social_and_advanced_cognition",
    6: "governance_fallback_and_negative_control",
}

EXPLICIT_LAYERS = {
    "information_flow_onset_gating": 0,
    "branch_binding_stability": 0,
    "coordination_length_control": 0,
    "global_broadcast_phase": 0,
    "action_agency": 1,
    "attention_control": 1,
    "error_monitoring": 1,
    "causal_attribution": 1,
    "predictive_error_minimization_phase": 1,
    "boundary_self": 2,
    "distributed_body_schema_self": 2,
    "identity_temporal_self": 2,
    "self_other_boundary_sharpness": 2,
    "episodic_memory_binding": 2,
    "body_schema_error_correction": 2,
    "action_ownership": 3,
    "temporal_horizon_dependent_planning": 3,
    "uncertainty_threshold_metacognition": 3,
    "metacognitive_repair_control": 3,
    "strategy_selection": 3,
    "prospective_memory": 3,
    "working_memory_capacity_rework": 3,
    "learning_rate_adaptation_rework": 3,
    "confidence_calibration_rework": 3,
    "contextual_policy_inhibition": 3,
    "affordance_selection_control": 3,
    "information_integration_phase": 4,
    "integration_without_broadcast_boundary": 4,
    "constraint_satisfaction_reconfiguration": 4,
    "macro_causal_viability_maintenance": 4,
    "goal_hierarchy_emergence": 4,
    "goal_conflict_resolution": 4,
    "resource_competition_arbitration": 4,
    "cross_family_synergy_control": 4,
    "temporal_credit_assignment": 4,
    "hierarchical_credit_assignment": 4,
    "semantic_memory_retrieval_control": 4,
    "counterfactual_reasoning_depth": 4,
    "counterfactual_repair_planning_rework": 4,
    "analogical_reasoning_rework": 4,
    "divergent_thinking": 4,
    "insight_problem_solving_rework": 4,
    "predictive_control_under_action_intervention": 4,
    "selective_global_broadcast_control": 4,
    "agency_without_ownership_boundary": 4,
    "temporal_identity_planning_dissociation": 4,
    "clock_drift_resynchronization_control": 4,
    "energy_budget_reallocation_control": 4,
    "sensor_gain_recalibration_control": 4,
    "tool_use_affordance_remapping": 4,
    "actuator_failure_compensation_control": 4,
    "latent_context_switch_detection": 4,
    "preference_reversal_adaptation_control": 5,
    "social_coupling_strength_collective_agency": 5,
    "perspective_taking": 5,
    "social_norm_tracking": 5,
    "cooperation_policy_switching_rework": 5,
    "multi_agent_commitment_tracking": 5,
    "norm_violation_repair": 5,
    "self_other_prediction_error_arbitration": 5,
    "spatial_navigation_remapping_rework": 5,
    "communication_channel_repair_control": 6,
    "coupled_viability_metacognition_phase": 6,
    "hierarchical_phase_cascade": 6,
    "causal_model_abstraction_hierarchy": 6,
    "reference_construct_phase_audit": 6,
}

EXPLICIT_DEPENDENCIES = {
    "attention_control": ("information_flow_onset_gating",),
    "action_agency": ("branch_binding_stability",),
    "error_monitoring": ("information_flow_onset_gating",),
    "causal_attribution": ("action_agency", "error_monitoring"),
    "predictive_error_minimization_phase": ("error_monitoring", "information_flow_onset_gating"),
    "boundary_self": ("attention_control",),
    "distributed_body_schema_self": ("information_flow_onset_gating",),
    "identity_temporal_self": ("branch_binding_stability",),
    "self_other_boundary_sharpness": ("boundary_self",),
    "episodic_memory_binding": ("identity_temporal_self", "branch_binding_stability"),
    "body_schema_error_correction": ("distributed_body_schema_self", "error_monitoring"),
    "action_ownership": ("action_agency", "boundary_self"),
    "metacognitive_repair_control": ("error_monitoring", "boundary_self"),
    "temporal_horizon_dependent_planning": ("action_agency", "identity_temporal_self"),
    "uncertainty_threshold_metacognition": ("error_monitoring", "attention_control"),
    "strategy_selection": ("uncertainty_threshold_metacognition", "attention_control"),
    "prospective_memory": ("identity_temporal_self", "attention_control"),
    "working_memory_capacity_rework": ("attention_control", "episodic_memory_binding"),
    "learning_rate_adaptation_rework": (
        "predictive_error_minimization_phase",
        "error_monitoring",
    ),
    "confidence_calibration_rework": (
        "uncertainty_threshold_metacognition",
        "error_monitoring",
    ),
    "contextual_policy_inhibition": ("attention_control", "strategy_selection"),
    "affordance_selection_control": ("action_agency", "attention_control"),
    "information_integration_phase": ("attention_control", "branch_binding_stability"),
    "integration_without_broadcast_boundary": (
        "information_integration_phase",
        "distributed_body_schema_self",
    ),
    "constraint_satisfaction_reconfiguration": (
        "metacognitive_repair_control",
        "goal_hierarchy_emergence",
    ),
    "macro_causal_viability_maintenance": (
        "temporal_horizon_dependent_planning",
        "uncertainty_threshold_metacognition",
    ),
    "goal_hierarchy_emergence": ("temporal_horizon_dependent_planning", "strategy_selection"),
    "goal_conflict_resolution": ("goal_hierarchy_emergence", "strategy_selection"),
    "resource_competition_arbitration": ("attention_control", "strategy_selection"),
    "cross_family_synergy_control": (
        "resource_competition_arbitration",
        "coordination_length_control",
    ),
    "temporal_credit_assignment": (
        "macro_causal_viability_maintenance",
        "causal_attribution",
    ),
    "hierarchical_credit_assignment": (
        "temporal_credit_assignment",
        "goal_hierarchy_emergence",
    ),
    "semantic_memory_retrieval_control": (
        "episodic_memory_binding",
        "working_memory_capacity_rework",
    ),
    "counterfactual_reasoning_depth": ("causal_attribution", "working_memory_capacity_rework"),
    "counterfactual_repair_planning_rework": (
        "counterfactual_reasoning_depth",
        "temporal_horizon_dependent_planning",
    ),
    "analogical_reasoning_rework": (
        "causal_attribution",
        "semantic_memory_retrieval_control",
    ),
    "divergent_thinking": ("strategy_selection", "semantic_memory_retrieval_control"),
    "insight_problem_solving_rework": (
        "strategy_selection",
        "divergent_thinking",
        "goal_hierarchy_emergence",
    ),
    "predictive_control_under_action_intervention": (
        "predictive_error_minimization_phase",
        "temporal_credit_assignment",
    ),
    "selective_global_broadcast_control": (
        "global_broadcast_phase",
        "attention_control",
        "coordination_length_control",
    ),
    "agency_without_ownership_boundary": ("action_agency", "action_ownership"),
    "temporal_identity_planning_dissociation": (
        "identity_temporal_self",
        "temporal_horizon_dependent_planning",
    ),
    "clock_drift_resynchronization_control": (
        "temporal_horizon_dependent_planning",
        "prospective_memory",
    ),
    "energy_budget_reallocation_control": (
        "resource_competition_arbitration",
        "strategy_selection",
    ),
    "sensor_gain_recalibration_control": (
        "predictive_error_minimization_phase",
        "body_schema_error_correction",
    ),
    "tool_use_affordance_remapping": (
        "affordance_selection_control",
        "body_schema_error_correction",
    ),
    "actuator_failure_compensation_control": (
        "body_schema_error_correction",
        "predictive_control_under_action_intervention",
        "action_agency",
    ),
    "latent_context_switch_detection": (
        "learning_rate_adaptation_rework",
        "strategy_selection",
        "error_monitoring",
    ),
    "social_coupling_strength_collective_agency": (
        "boundary_self",
        "action_agency",
    ),
    "self_other_prediction_error_arbitration": (
        "boundary_self",
        "error_monitoring",
        "action_ownership",
    ),
    "perspective_taking": (
        "boundary_self",
        "self_other_prediction_error_arbitration",
    ),
    "social_norm_tracking": (
        "perspective_taking",
        "social_coupling_strength_collective_agency",
        "error_monitoring",
    ),
    "cooperation_policy_switching_rework": (
        "social_coupling_strength_collective_agency",
        "strategy_selection",
        "perspective_taking",
    ),
    "multi_agent_commitment_tracking": (
        "prospective_memory",
        "social_coupling_strength_collective_agency",
        "cooperation_policy_switching_rework",
    ),
    "norm_violation_repair": (
        "social_norm_tracking",
        "metacognitive_repair_control",
    ),
    "preference_reversal_adaptation_control": (
        "strategy_selection",
        "goal_conflict_resolution",
        "resource_competition_arbitration",
        "social_norm_tracking",
    ),
    "spatial_navigation_remapping_rework": (
        "distributed_body_schema_self",
        "temporal_horizon_dependent_planning",
        "attention_control",
    ),
    "communication_channel_repair_control": (
        "multi_agent_commitment_tracking",
        "social_norm_tracking",
        "semantic_memory_retrieval_control",
    ),
    "coupled_viability_metacognition_phase": (
        "macro_causal_viability_maintenance",
        "uncertainty_threshold_metacognition",
    ),
    "hierarchical_phase_cascade": (
        "hierarchical_credit_assignment",
        "information_integration_phase",
    ),
    "causal_model_abstraction_hierarchy": (
        "causal_attribution",
        "counterfactual_reasoning_depth",
    ),
    "reference_construct_phase_audit": (
        "action_agency",
        "boundary_self",
        "identity_temporal_self",
        "action_ownership",
        "distributed_body_schema_self",
    ),
}

COMPLEMENT_EDGES = (
    ("attention_control", "information_integration_phase", "attention selects what integration binds"),
    ("boundary_self", "distributed_body_schema_self", "self boundary and tool/body schema jointly form operational self-model"),
    ("action_agency", "action_ownership", "controllability and ownership jointly form action system"),
    ("error_monitoring", "metacognitive_repair_control", "monitoring enables repair"),
    ("strategy_selection", "goal_conflict_resolution", "strategy choice and conflict resolution co-regulate goals"),
    ("actuator_failure_compensation_control", "body_schema_error_correction", "actuator failure compensation uses body-schema correction"),
    ("preference_reversal_adaptation_control", "goal_conflict_resolution", "preference reversal is mediated by goal conflict handling"),
)

COMPETITION_EDGES = (
    ("integration_without_broadcast_boundary", "global_broadcast_phase", "distributed integration versus broadcast-style consolidation"),
    ("agency_without_ownership_boundary", "action_ownership", "agency can dissociate from ownership"),
    ("selective_global_broadcast_control", "integration_without_broadcast_boundary", "selective broadcast and no-broadcast integration are alternative routing regimes"),
)


@dataclass(frozen=True)
class ConstructDependencyNode:
    node_id: str
    layer_index: int
    layer_name: str
    architecture_layer: str
    mechanism_family: str
    roles: tuple[str, ...]
    review_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "layer_index": self.layer_index,
            "layer_name": self.layer_name,
            "architecture_layer": self.architecture_layer,
            "mechanism_family": self.mechanism_family,
            "roles": list(self.roles),
            "review_status": self.review_status,
        }


@dataclass(frozen=True)
class ConstructDependencyEdge:
    source_id: str
    target_id: str
    relation_type: str
    rationale: str
    confidence: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "rationale": self.rationale,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class LayeredActivationStep:
    layer_index: int
    layer_name: str
    construct_ids: tuple[str, ...]
    dependency_inputs: dict[str, list[str]]
    parallelizable: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer_index": self.layer_index,
            "layer_name": self.layer_name,
            "construct_ids": list(self.construct_ids),
            "dependency_inputs": {
                key: list(values) for key, values in sorted(self.dependency_inputs.items())
            },
            "parallelizable": self.parallelizable,
        }


@dataclass(frozen=True)
class ConstructDependencyGraphReport:
    nodes: tuple[ConstructDependencyNode, ...]
    dependency_edges: tuple[ConstructDependencyEdge, ...]
    complement_edges: tuple[ConstructDependencyEdge, ...]
    competition_edges: tuple[ConstructDependencyEdge, ...]
    activation_steps: tuple[LayeredActivationStep, ...]
    unresolved_dependencies: tuple[dict[str, str], ...]
    cycles: tuple[tuple[str, ...], ...]
    review_notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "consciousness_benchmark.construct_dependency_graph.v1",
            "counts": {
                "nodes": len(self.nodes),
                "dependency_edges": len(self.dependency_edges),
                "complement_edges": len(self.complement_edges),
                "competition_edges": len(self.competition_edges),
                "activation_layers": len(self.activation_steps),
                "unresolved_dependencies": len(self.unresolved_dependencies),
                "cycles": len(self.cycles),
                "layers": dict(
                    sorted(Counter(node.layer_name for node in self.nodes).items())
                ),
            },
            "acyclic": not self.cycles,
            "nodes": [node.to_dict() for node in self.nodes],
            "dependency_edges": [edge.to_dict() for edge in self.dependency_edges],
            "complement_edges": [edge.to_dict() for edge in self.complement_edges],
            "competition_edges": [edge.to_dict() for edge in self.competition_edges],
            "activation_steps": [step.to_dict() for step in self.activation_steps],
            "unresolved_dependencies": list(self.unresolved_dependencies),
            "cycles": [list(cycle) for cycle in self.cycles],
            "review_notes": list(self.review_notes),
            "claim_boundary": [
                "dependency graph is an inferred operational model",
                "edges require domain review before being treated as formal theory",
                "no subjective consciousness, human self-experience, or free will is claimed",
            ],
        }

    def summary_markdown(self) -> str:
        data = self.to_dict()
        lines = [
            "# Construct Dependency Graph",
            "",
            f"- Nodes: {data['counts']['nodes']}",
            f"- Dependency edges: {data['counts']['dependency_edges']}",
            f"- Complement edges: {data['counts']['complement_edges']}",
            f"- Competition edges: {data['counts']['competition_edges']}",
            f"- Acyclic: {data['acyclic']}",
            f"- Unresolved dependencies: {data['counts']['unresolved_dependencies']}",
            "",
            "## Activation Layers",
        ]
        for step in self.activation_steps:
            preview = ", ".join(step.construct_ids[:10])
            suffix = "" if len(step.construct_ids) <= 10 else f", ... (+{len(step.construct_ids) - 10})"
            lines.append(
                f"- L{step.layer_index} {step.layer_name}: "
                f"{len(step.construct_ids)} constructs ({preview}{suffix})"
            )
        lines.extend(["", "## Core Dependencies"])
        for edge in self.dependency_edges[:24]:
            lines.append(
                f"- {edge.source_id} -> {edge.target_id}: {edge.rationale}"
            )
        lines.extend(["", "## Competition / Tension"])
        for edge in self.competition_edges:
            lines.append(
                f"- {edge.source_id} <-> {edge.target_id}: {edge.rationale}"
            )
        if self.review_notes:
            lines.extend(["", "## Review Notes"])
            lines.extend(f"- {note}" for note in self.review_notes)
        return "\n".join(lines)


def build_construct_dependency_graph(
    architecture: ConstructArchitecture | None = None,
) -> ConstructDependencyGraphReport:
    architecture = architecture or all_construct_architecture()
    node_by_id = {node.id: node for node in architecture.nodes}
    dependency_nodes = tuple(
        _dependency_node_for(node)
        for node in architecture.nodes
    )
    node_layers = {node.node_id: node.layer_index for node in dependency_nodes}
    dependency_edges, unresolved = _dependency_edges(node_by_id, node_layers)
    complement_edges = _typed_edges(COMPLEMENT_EDGES, node_by_id, "complements")
    competition_edges = _typed_edges(COMPETITION_EDGES, node_by_id, "competes_with")
    cycles = _detect_cycles(dependency_edges)
    activation_steps = _activation_steps(dependency_nodes, dependency_edges)
    review_notes = _review_notes(dependency_edges, complement_edges, competition_edges, unresolved)
    return ConstructDependencyGraphReport(
        nodes=dependency_nodes,
        dependency_edges=dependency_edges,
        complement_edges=complement_edges,
        competition_edges=competition_edges,
        activation_steps=activation_steps,
        unresolved_dependencies=tuple(unresolved),
        cycles=cycles,
        review_notes=review_notes,
    )


def _dependency_node_for(node: ConstructNode) -> ConstructDependencyNode:
    layer_index = EXPLICIT_LAYERS.get(node.id, _infer_layer(node))
    return ConstructDependencyNode(
        node_id=node.id,
        layer_index=layer_index,
        layer_name=LAYER_NAMES[layer_index],
        architecture_layer=node.layer,
        mechanism_family=node.mechanism_family,
        roles=node.roles,
        review_status=_review_status_for(node),
    )


def _infer_layer(node: ConstructNode) -> int:
    if node.layer in {"failure_bank", "audit_route", "preconstruct"}:
        return 6
    family = node.mechanism_family
    node_id = node.id
    if family in {"workspace"} and "broadcast" in node_id:
        return 0
    if family in {"action", "causal_counterfactual"}:
        return 1
    if family in {"temporal_self", "memory"}:
        return 2
    if family in {"metacognition", "temporal_credit"}:
        return 3
    if family in {"resource_problem", "resource_control", "action_control", "sensorimotor_control"}:
        return 4
    if family in {"social_boundary", "communication_control"}:
        return 5
    return 4


def _review_status_for(node: ConstructNode) -> str:
    if node.layer == "reference":
        return "formal_reference_dependency_anchor"
    if node.layer == "validation_candidate":
        return "validation_candidate_dependency_requires_external_validation"
    if node.layer == "candidate":
        return "candidate_dependency_inferred_review_required"
    if node.layer == "preconstruct":
        return "preconstruct_dependency_hypothesis"
    if node.layer == "failure_bank":
        return "negative_control_dependency_do_not_promote"
    return "audit_dependency_route"


def _dependency_edges(
    node_by_id: dict[str, ConstructNode],
    node_layers: dict[str, int],
) -> tuple[tuple[ConstructDependencyEdge, ...], list[dict[str, str]]]:
    edges: list[ConstructDependencyEdge] = []
    unresolved: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    def add(source_id: str, target_id: str, rationale: str, confidence: str) -> None:
        key = (source_id, target_id, "requires")
        if source_id == target_id or key in seen:
            return
        if source_id not in node_by_id:
            unresolved.append({"source_id": source_id, "target_id": target_id})
            return
        if target_id not in node_by_id:
            unresolved.append({"source_id": source_id, "target_id": target_id})
            return
        if node_layers[source_id] > node_layers[target_id]:
            unresolved.append(
                {
                    "source_id": source_id,
                    "target_id": target_id,
                    "reason": "dependency would point from later layer to earlier layer",
                }
            )
            return
        seen.add(key)
        edges.append(
            ConstructDependencyEdge(
                source_id=source_id,
                target_id=target_id,
                relation_type="requires",
                rationale=rationale,
                confidence=confidence,
            )
        )

    for target_id, dependency_ids in EXPLICIT_DEPENDENCIES.items():
        for source_id in dependency_ids:
            add(
                source_id,
                target_id,
                "explicit mechanism dependency inferred from construct semantics",
                "reviewable_inference",
            )

    for node in node_by_id.values():
        for boundary_id in node.nearest_boundaries:
            if boundary_id not in node_by_id:
                continue
            if node_layers[boundary_id] < node_layers[node.id]:
                add(
                    boundary_id,
                    node.id,
                    "nearest-boundary dependency from architecture metadata",
                    "metadata_inferred",
                )
            elif node_layers[boundary_id] == node_layers[node.id]:
                continue
        if node_layers[node.id] > 0 and not any(edge.target_id == node.id for edge in edges):
            for source_id in _fallback_dependencies_for(node, node_by_id, node_layers):
                add(
                    source_id,
                    node.id,
                    "fallback dependency inferred from mechanism family",
                    "low_confidence_inference",
                )

    edges.sort(key=lambda edge: (node_layers[edge.target_id], edge.target_id, edge.source_id))
    return tuple(edges), unresolved


def _fallback_dependencies_for(
    node: ConstructNode,
    node_by_id: dict[str, ConstructNode],
    node_layers: dict[str, int],
) -> tuple[str, ...]:
    candidates_by_family = {
        "action": ("action_agency", "branch_binding_stability"),
        "action_control": ("action_agency", "body_schema_error_correction"),
        "sensorimotor_control": ("predictive_error_minimization_phase", "attention_control"),
        "motor_infrastructure_control": ("action_agency", "body_schema_error_correction"),
        "workspace": ("attention_control", "information_flow_onset_gating"),
        "metacognition": ("error_monitoring", "attention_control"),
        "memory": ("identity_temporal_self", "branch_binding_stability"),
        "temporal_self": ("identity_temporal_self", "branch_binding_stability"),
        "temporal_credit": ("temporal_horizon_dependent_planning", "causal_attribution"),
        "temporal_control": ("temporal_horizon_dependent_planning", "branch_binding_stability"),
        "resource_problem": ("strategy_selection", "attention_control"),
        "resource_control": ("resource_competition_arbitration", "strategy_selection"),
        "causal_counterfactual": ("causal_attribution", "error_monitoring"),
        "social_boundary": ("boundary_self", "error_monitoring"),
        "communication_control": ("social_norm_tracking", "semantic_memory_retrieval_control"),
        "reference_motif": ("boundary_self", "action_agency"),
    }
    candidates = candidates_by_family.get(
        node.mechanism_family,
        ("information_flow_onset_gating", "branch_binding_stability"),
    )
    return tuple(
        candidate
        for candidate in candidates
        if candidate in node_by_id and node_layers[candidate] < node_layers[node.id]
    )


def _typed_edges(
    specs: tuple[tuple[str, str, str], ...],
    node_by_id: dict[str, ConstructNode],
    relation_type: str,
) -> tuple[ConstructDependencyEdge, ...]:
    edges: list[ConstructDependencyEdge] = []
    for left, right, rationale in specs:
        if left not in node_by_id or right not in node_by_id:
            continue
        edges.append(
            ConstructDependencyEdge(
                source_id=left,
                target_id=right,
                relation_type=relation_type,
                rationale=rationale,
                confidence="reviewable_inference",
            )
        )
    return tuple(edges)


def _detect_cycles(
    edges: tuple[ConstructDependencyEdge, ...],
) -> tuple[tuple[str, ...], ...]:
    incoming: dict[str, int] = defaultdict(int)
    outgoing: dict[str, list[str]] = defaultdict(list)
    nodes: set[str] = set()
    for edge in edges:
        nodes.add(edge.source_id)
        nodes.add(edge.target_id)
        outgoing[edge.source_id].append(edge.target_id)
        incoming[edge.target_id] += 1
        incoming.setdefault(edge.source_id, incoming.get(edge.source_id, 0))

    queue = deque(sorted(node for node in nodes if incoming[node] == 0))
    visited: list[str] = []
    while queue:
        node = queue.popleft()
        visited.append(node)
        for target in outgoing[node]:
            incoming[target] -= 1
            if incoming[target] == 0:
                queue.append(target)
    if len(visited) == len(nodes):
        return ()
    residual = tuple(sorted(node for node in nodes if incoming[node] > 0))
    return (residual,)


def _activation_steps(
    nodes: tuple[ConstructDependencyNode, ...],
    edges: tuple[ConstructDependencyEdge, ...],
) -> tuple[LayeredActivationStep, ...]:
    dependencies_by_target: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        dependencies_by_target[edge.target_id].append(edge.source_id)
    nodes_by_layer: dict[int, list[ConstructDependencyNode]] = defaultdict(list)
    for node in nodes:
        nodes_by_layer[node.layer_index].append(node)

    steps: list[LayeredActivationStep] = []
    for layer_index in sorted(nodes_by_layer):
        layer_nodes = sorted(nodes_by_layer[layer_index], key=lambda item: item.node_id)
        construct_ids = tuple(node.node_id for node in layer_nodes)
        dependency_inputs = {
            node.node_id: sorted(dependencies_by_target.get(node.node_id, []))
            for node in layer_nodes
        }
        layer_set = set(construct_ids)
        has_internal_dependency = any(
            dependency in layer_set
            for dependencies in dependency_inputs.values()
            for dependency in dependencies
        )
        steps.append(
            LayeredActivationStep(
                layer_index=layer_index,
                layer_name=LAYER_NAMES[layer_index],
                construct_ids=construct_ids,
                dependency_inputs=dependency_inputs,
                parallelizable=not has_internal_dependency,
            )
        )
    return tuple(steps)


def _review_notes(
    dependency_edges: tuple[ConstructDependencyEdge, ...],
    complement_edges: tuple[ConstructDependencyEdge, ...],
    competition_edges: tuple[ConstructDependencyEdge, ...],
    unresolved: list[dict[str, str]],
) -> tuple[str, ...]:
    notes = [
        "The graph is a conservative operational dependency inference, not a formal theory claim.",
        "Edges inferred from nearest-boundary metadata should be reviewed before publication.",
        "Same-layer constructs are allowed to run in parallel and exchange state only through the next layer.",
    ]
    if unresolved:
        notes.append("Some requested dependencies were held out because they would violate the layer order.")
    if competition_edges:
        notes.append("Competition edges are modeled as route tension, not as mutual exclusion by default.")
    if complement_edges:
        notes.append("Complement edges indicate paired review focus for future council analysis.")
    if not dependency_edges:
        notes.append("No dependency edges were produced; this would indicate a broken graph build.")
    return tuple(notes)
