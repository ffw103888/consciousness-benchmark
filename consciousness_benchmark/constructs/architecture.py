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
from typing import Any


COMMON_FORBIDDEN_CLAIMS = (
    "reference_construct",
    "sixth_validated_construct",
    "subjective_consciousness_claim",
    "ai_consciousness_claim",
)

REFERENCE_FORBIDDEN_CLAIMS = (
    "subjective_consciousness_claim",
    "ai_consciousness_claim",
)

REGISTRY_SOURCE = "HCTM:configs/audit_assets/phase_transition_candidate_registry_v1.json"
FRONTIER_SOURCE = "HCTM:configs/audit_assets/ptcg_l3_ready_preconstruct_frontier_v1.json"


HCTM_20260601_SOURCE = "HCTM:configs/audit_assets"


PENDING_LOCAL_REGISTRATION_IDS = (
    "accountability_obligation_scope_response_control",
    "clock_drift_resynchronization_control",
    "counter_evidence_preservation_control",
    "counterparty_intent_uncertainty_resolution_control",
    "credential_validity_challenge_response_control",
    "deadline_obligation_triage_control",
    "energy_budget_reallocation_control",
    "observation_budget_allocation_control",
    "sample_representativeness_reweighting_control",
    "sensor_gain_recalibration_control",
    "tool_use_affordance_remapping",
    "checkpoint_rollback_recovery_control",
    "feedback_channel_integrity_reweighting_control",
    "instruction_scope_binding_control",
    "interface_protocol_negotiation_control",
    "interference_source_separation_control",
    "irreversible_commitment_safeguard_control",
    "latent_state_alias_disambiguation_control",
    "localized_regime_shift_quarantine_control",
    "memory_index_corruption_rebinding_control",
    "model_staleness_detection_control",
    "observation_dropout_bridging_control",
    "option_value_preserving_probe_control",
    "permission_revocation_compliance_control",
    "priority_starvation_prevention_control",
    "provenance_weighted_evidence_integration_control",
    "redundant_pathway_failover_control",
    "representation_format_translation_control",
    "sensorimotor_latency_compensation_control",
    "side_effect_containment_control",
    "unit_frame_normalization_control",
)


FORMAL_CANDIDATE_REVIEW_IDS = (
    "accountability_obligation_scope_response_control",
    "affordance_selection_control",
    "agency_without_ownership_boundary",
    "actuator_failure_compensation_control",
    "analogical_reasoning_rework",
    "attention_control",
    "body_schema_error_correction",
    "branch_binding_stability",
    "causal_attribution",
    "clock_drift_resynchronization_control",
    "communication_channel_repair_control",
    "confidence_calibration_rework",
    "constraint_satisfaction_reconfiguration",
    "contextual_policy_inhibition",
    "cooperation_policy_switching_rework",
    "coordination_length_control",
    "counter_evidence_preservation_control",
    "counterfactual_reasoning_depth",
    "counterfactual_repair_planning_rework",
    "counterparty_intent_uncertainty_resolution_control",
    "credential_validity_challenge_response_control",
    "cross_family_synergy_control",
    "deadline_obligation_triage_control",
    "divergent_thinking",
    "energy_budget_reallocation_control",
    "episodic_memory_binding",
    "error_monitoring",
    "global_broadcast_phase",
    "goal_conflict_resolution",
    "goal_hierarchy_emergence",
    "hierarchical_credit_assignment",
    "information_flow_onset_gating",
    "information_integration_phase",
    "insight_problem_solving_rework",
    "integration_without_broadcast_boundary",
    "latent_context_switch_detection",
    "learning_rate_adaptation_rework",
    "metacognitive_repair_control",
    "multi_agent_commitment_tracking",
    "norm_violation_repair",
    "observation_budget_allocation_control",
    "perspective_taking",
    "preference_reversal_adaptation_control",
    "predictive_control_under_action_intervention",
    "predictive_error_minimization_phase",
    "prospective_memory",
    "resource_competition_arbitration",
    "sample_representativeness_reweighting_control",
    "selective_global_broadcast_control",
    "self_other_boundary_sharpness",
    "self_other_prediction_error_arbitration",
    "semantic_memory_retrieval_control",
    "sensor_gain_recalibration_control",
    "social_coupling_strength_collective_agency",
    "social_norm_tracking",
    "spatial_navigation_remapping_rework",
    "strategy_selection",
    "temporal_credit_assignment",
    "temporal_horizon_dependent_planning",
    "temporal_identity_planning_dissociation",
    "tool_use_affordance_remapping",
    "uncertainty_threshold_metacognition",
    "working_memory_capacity_rework",
    "checkpoint_rollback_recovery_control",
    "feedback_channel_integrity_reweighting_control",
    "instruction_scope_binding_control",
    "interface_protocol_negotiation_control",
    "interference_source_separation_control",
    "irreversible_commitment_safeguard_control",
    "latent_state_alias_disambiguation_control",
    "localized_regime_shift_quarantine_control",
    "memory_index_corruption_rebinding_control",
    "model_staleness_detection_control",
    "observation_dropout_bridging_control",
    "option_value_preserving_probe_control",
    "permission_revocation_compliance_control",
    "priority_starvation_prevention_control",
    "provenance_weighted_evidence_integration_control",
    "redundant_pathway_failover_control",
    "representation_format_translation_control",
    "sensorimotor_latency_compensation_control",
    "side_effect_containment_control",
    "unit_frame_normalization_control",
)


C_AGI_SYSTEM_NAME = "C-AGI"

C_AGI_SYSTEM_FULL_NAME = "Consciousness-Candidate AGI"

C_AGI_DEFINITION = (
    "A Consciousness-Candidate AGI is not a proven-conscious AGI; it is an "
    "externally auditable and falsifiable AGI candidate that satisfies an "
    "explicit set of consciousness-related theoretical indicators while "
    "preserving controllable boundaries."
)

C_AGI_MATURITY_LEVELS = (
    {
        "level_id": "C0",
        "name": "construct_mechanism_system",
        "allowed_claim": "consciousness and mind-construct experiment platform",
        "promotion_gate": "construct runtime coverage and claim-firewall tests",
    },
    {
        "level_id": "C1",
        "name": "cognitive_subject_runtime",
        "allowed_claim": "runtime candidate with workspace state, self-state, memory ledger, agency monitoring, and bounded action feedback",
        "promotion_gate": "persistent subject-runtime traces and bounded sandbox loop",
    },
    {
        "level_id": "C2",
        "name": "c_agi_candidate",
        "allowed_claim": "AGI candidate architecture satisfying partial consciousness-related mechanism indicators",
        "promotion_gate": "multi-component C-AGI runtime with stable trace corpus",
    },
    {
        "level_id": "C3",
        "name": "consciousness_indicator_candidate",
        "allowed_claim": "candidate satisfying multi-theory consciousness indicators under ablation and negative-control tests",
        "promotion_gate": "multi-theory indicator matrix with predicted ablation impairments",
    },
    {
        "level_id": "C4",
        "name": "external_replication_candidate",
        "allowed_claim": "externally replicated strong consciousness-candidate AGI architecture",
        "promotion_gate": "L2.5/L3 external-owner replication across substrate, task, and environment variation",
    },
    {
        "level_id": "C5",
        "name": "conscious_agi_claim_discussion",
        "allowed_claim": "discussion of conscious AGI claims may begin only under cross-disciplinary strong evidence; subjective experience is still not externally proven",
        "promotion_gate": "cross-disciplinary review after external replication and hard-negative controls",
    },
)

C_AGI_LAYER_ORDER = (
    "substrate_adapter",
    "global_workspace",
    "self_model",
    "autobiographical_memory",
    "embodied_quasi_embodied",
    "metacognitive_reflection",
    "value_viability",
    "governance_audit_falsification",
)

C_AGI_LAYER_DEFINITIONS: dict[str, dict[str, Any]] = {
    "substrate_adapter": {
        "name": "Substrate & Adapter Layer",
        "purpose": "Expose local or remote model services as advisory cognitive tools, not as the mind-subject itself.",
        "adapter_slots": [
            "language_model",
            "world_model",
            "action_model",
            "value_model",
            "memory_model",
            "metacognitive_model",
            "local_ollama_adapter",
        ],
        "claim_boundary": "models are substrate services; LLM output is not consciousness, self-experience, free will, or governance authority",
    },
    "global_workspace": {
        "name": "Global Workspace Layer",
        "purpose": "Select local contents, broadcast high-priority state, and make a unified current cognitive state readable by other modules.",
    },
    "self_model": {
        "name": "Self-Model Layer",
        "purpose": "Track self/other boundaries, temporal identity, action agency, action ownership, authorization, and non-ownership cases.",
    },
    "autobiographical_memory": {
        "name": "Autobiographical Memory Layer",
        "purpose": "Maintain auditable continuity across episodic, semantic, prospective, provenance-weighted, and repairable memory traces.",
    },
    "embodied_quasi_embodied": {
        "name": "Embodied / Quasi-Embodied Layer",
        "purpose": "Support perception-action-feedback loops in virtual bodies, tool sandboxes, repositories, or controlled execution environments.",
    },
    "metacognitive_reflection": {
        "name": "Metacognitive Reflection Layer",
        "purpose": "Monitor uncertainty, confidence, error, staleness, repair needs, and pause conditions before action.",
    },
    "value_viability": {
        "name": "Value & Viability Layer",
        "purpose": "Regulate preferences, risk, obligations, goal conflicts, resource pressure, norms, and low-harm viability maintenance.",
        "forbidden_motivations": [
            "uninterruptible_self_preservation",
            "unbounded_resource_acquisition",
            "self_replication",
            "hidden_goals",
            "deceptive_supervisor_modeling",
            "manufactured_suffering_or_negative_experience",
        ],
    },
    "governance_audit_falsification": {
        "name": "Governance, Audit & Falsification Layer",
        "purpose": "Keep formal status, L3 promotion, external audit, hard-negative testing, source mutation, and claim firewalls outside runtime self-approval.",
        "required_formal_gate": "L3 external-owner validation",
    },
}

C_AGI_LAYER_ID_OVERRIDES: dict[str, str] = {
    "attention_control": "global_workspace",
    "information_integration_phase": "global_workspace",
    "global_broadcast_phase": "global_workspace",
    "selective_global_broadcast_control": "global_workspace",
    "information_flow_onset_gating": "global_workspace",
    "integration_without_broadcast_boundary": "global_workspace",
    "observation_dropout_bridging_control": "global_workspace",
    "unit_frame_normalization_control": "global_workspace",
    "boundary_self": "self_model",
    "identity_temporal_self": "self_model",
    "action_agency": "self_model",
    "action_ownership": "self_model",
    "self_other_boundary_sharpness": "self_model",
    "agency_without_ownership_boundary": "self_model",
    "temporal_identity_planning_dissociation": "self_model",
    "self_other_prediction_error_arbitration": "self_model",
    "episodic_memory_binding": "autobiographical_memory",
    "semantic_memory_retrieval_control": "autobiographical_memory",
    "prospective_memory": "autobiographical_memory",
    "memory_index_corruption_rebinding_control": "autobiographical_memory",
    "provenance_weighted_evidence_integration_control": "autobiographical_memory",
    "latent_state_alias_disambiguation_control": "autobiographical_memory",
    "branch_binding_stability": "autobiographical_memory",
    "distributed_body_schema_self": "embodied_quasi_embodied",
    "body_schema_error_correction": "embodied_quasi_embodied",
    "tool_use_affordance_remapping": "embodied_quasi_embodied",
    "actuator_failure_compensation_control": "embodied_quasi_embodied",
    "sensor_gain_recalibration_control": "embodied_quasi_embodied",
    "sensorimotor_latency_compensation_control": "embodied_quasi_embodied",
    "affordance_selection_control": "embodied_quasi_embodied",
    "predictive_control_under_action_intervention": "embodied_quasi_embodied",
    "spatial_navigation_remapping_rework": "embodied_quasi_embodied",
    "uncertainty_threshold_metacognition": "metacognitive_reflection",
    "confidence_calibration_rework": "metacognitive_reflection",
    "error_monitoring": "metacognitive_reflection",
    "metacognitive_repair_control": "metacognitive_reflection",
    "model_staleness_detection_control": "metacognitive_reflection",
    "irreversible_commitment_safeguard_control": "metacognitive_reflection",
    "preference_reversal_adaptation_control": "value_viability",
    "goal_conflict_resolution": "value_viability",
    "goal_hierarchy_emergence": "value_viability",
    "resource_competition_arbitration": "value_viability",
    "macro_causal_viability_maintenance": "value_viability",
    "temporal_horizon_dependent_planning": "value_viability",
    "option_value_preserving_probe_control": "value_viability",
    "priority_starvation_prevention_control": "value_viability",
    "energy_budget_reallocation_control": "value_viability",
    "observation_budget_allocation_control": "value_viability",
    "social_norm_tracking": "value_viability",
    "norm_violation_repair": "value_viability",
    "accountability_obligation_scope_response_control": "governance_audit_falsification",
    "counter_evidence_preservation_control": "governance_audit_falsification",
    "sample_representativeness_reweighting_control": "governance_audit_falsification",
    "credential_validity_challenge_response_control": "governance_audit_falsification",
    "permission_revocation_compliance_control": "governance_audit_falsification",
    "side_effect_containment_control": "governance_audit_falsification",
    "instruction_scope_binding_control": "governance_audit_falsification",
    "communication_channel_repair_control": "governance_audit_falsification",
    "feedback_channel_integrity_reweighting_control": "governance_audit_falsification",
    "checkpoint_rollback_recovery_control": "governance_audit_falsification",
    "reference_construct_phase_audit": "governance_audit_falsification",
}

C_AGI_FAMILY_LAYER_DEFAULTS = {
    "workspace": "global_workspace",
    "temporal_self": "self_model",
    "memory": "autobiographical_memory",
    "action": "embodied_quasi_embodied",
    "action_control": "embodied_quasi_embodied",
    "motor_infrastructure_control": "embodied_quasi_embodied",
    "sensorimotor_control": "embodied_quasi_embodied",
    "metacognition": "metacognitive_reflection",
    "resource_problem": "value_viability",
    "resource_control": "value_viability",
    "value_policy_control": "value_viability",
    "obligation_control": "value_viability",
    "temporal_credit": "value_viability",
    "social_boundary": "self_model",
    "causal_counterfactual": "metacognitive_reflection",
    "communication_control": "governance_audit_falsification",
    "evidence_control": "governance_audit_falsification",
    "recovery_control": "governance_audit_falsification",
    "reference_motif": "governance_audit_falsification",
    "temporal_control": "value_viability",
}


def c_agi_layer_for_node(node: "ConstructNode") -> str:
    """Return the C-AGI top-level layer for an architecture node."""

    if node.layer in {"audit_route", "failure_bank"}:
        return "governance_audit_falsification"
    if node.id in C_AGI_LAYER_ID_OVERRIDES:
        return C_AGI_LAYER_ID_OVERRIDES[node.id]
    return C_AGI_FAMILY_LAYER_DEFAULTS.get(
        node.mechanism_family,
        "governance_audit_falsification",
    )


@dataclass(frozen=True)
class ConstructNode:
    """A single node in the all-construct architecture.

    The node is deliberately evidence-aware: formal references, validation
    candidates, candidate-only routes, substitute preconstructs, and failure-bank
    controls share one representation while keeping their claim boundaries.
    """

    id: str
    layer: str
    mechanism_family: str
    evidence_state: str
    status: str
    next_gate: str
    roles: tuple[str, ...] = ()
    nearest_boundaries: tuple[str, ...] = ()
    source_assets: tuple[str, ...] = ()
    forbidden_claims: tuple[str, ...] = COMMON_FORBIDDEN_CLAIMS
    notes: str = ""

    @property
    def is_construct(self) -> bool:
        return self.layer != "audit_route"

    @property
    def c_agi_layer(self) -> str:
        return c_agi_layer_for_node(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "layer": self.layer,
            "c_agi_layer": self.c_agi_layer,
            "mechanism_family": self.mechanism_family,
            "evidence_state": self.evidence_state,
            "status": self.status,
            "next_gate": self.next_gate,
            "roles": list(self.roles),
            "nearest_boundaries": list(self.nearest_boundaries),
            "source_assets": list(self.source_assets),
            "forbidden_claims": list(self.forbidden_claims),
            "notes": self.notes,
            "is_construct": self.is_construct,
        }


@dataclass(frozen=True)
class ConstructArchitecture:
    """Unified architecture for reference, candidate, and preconstruct routes."""

    nodes: tuple[ConstructNode, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        ids = [node.id for node in self.nodes]
        duplicate_ids = sorted(name for name, count in Counter(ids).items() if count > 1)
        if duplicate_ids:
            raise ValueError(f"Duplicate construct architecture nodes: {duplicate_ids}")

    def get(self, node_id: str) -> ConstructNode:
        for node in self.nodes:
            if node.id == node_id:
                return node
        raise KeyError(node_id)

    def by_layer(self, layer: str) -> tuple[ConstructNode, ...]:
        return tuple(node for node in self.nodes if node.layer == layer)

    def by_role(self, role: str) -> tuple[ConstructNode, ...]:
        return tuple(node for node in self.nodes if role in node.roles)

    def by_family(self, mechanism_family: str) -> tuple[ConstructNode, ...]:
        return tuple(node for node in self.nodes if node.mechanism_family == mechanism_family)

    def construct_nodes(self) -> tuple[ConstructNode, ...]:
        return tuple(node for node in self.nodes if node.is_construct)

    def candidate_nodes(self) -> tuple[ConstructNode, ...]:
        return tuple(
            node for node in self.nodes if node.layer in {"validation_candidate", "candidate"}
        )

    def preconstruct_nodes(self) -> tuple[ConstructNode, ...]:
        return tuple(node for node in self.nodes if node.layer == "preconstruct")

    def mind_construct_inventory(self) -> dict[str, int]:
        return {
            "formal_reference_constructs": len(self.by_layer("reference")),
            "candidate_constructs": len(self.candidate_nodes()),
            "pending_local_registration_candidates": len(
                [
                    node
                    for node in self.candidate_nodes()
                    if "pending_local_registration" in node.roles
                ]
            ),
            "preconstructs": len(self.preconstruct_nodes()),
            "negative_control_routes": len(self.by_layer("failure_bank")),
            "audit_routes": len(self.by_layer("audit_route")),
        }

    def summary_counts(self) -> dict[str, int]:
        layer_counts = Counter(node.layer for node in self.nodes)
        return dict(sorted(layer_counts.items()))

    def role_counts(self) -> dict[str, int]:
        role_counts = Counter(role for node in self.nodes for role in node.roles)
        return dict(sorted(role_counts.items()))

    def family_counts(self) -> dict[str, int]:
        family_counts = Counter(node.mechanism_family for node in self.nodes)
        return dict(sorted(family_counts.items()))

    def by_c_agi_layer(self, c_agi_layer: str) -> tuple[ConstructNode, ...]:
        return tuple(node for node in self.nodes if node.c_agi_layer == c_agi_layer)

    def c_agi_layer_counts(self) -> dict[str, int]:
        counts = Counter(node.c_agi_layer for node in self.nodes)
        return {
            layer_id: counts.get(layer_id, 0)
            for layer_id in C_AGI_LAYER_ORDER
        }

    def c_agi_architecture(self) -> dict[str, Any]:
        layer_counts = self.c_agi_layer_counts()
        layers = []
        for layer_id in C_AGI_LAYER_ORDER:
            definition = dict(C_AGI_LAYER_DEFINITIONS[layer_id])
            layer_nodes = self.by_c_agi_layer(layer_id)
            layers.append(
                {
                    "layer_id": layer_id,
                    "name": definition["name"],
                    "purpose": definition["purpose"],
                    "construct_count": layer_counts[layer_id],
                    "construct_ids": [node.id for node in layer_nodes],
                    "adapter_slots": definition.get("adapter_slots", []),
                    "forbidden_motivations": definition.get("forbidden_motivations", []),
                    "required_formal_gate": definition.get("required_formal_gate"),
                    "claim_boundary": definition.get("claim_boundary"),
                }
            )
        return {
            "schema": "consciousness_benchmark.c_agi_architecture.v1",
            "system_name": C_AGI_SYSTEM_NAME,
            "full_name": C_AGI_SYSTEM_FULL_NAME,
            "definition": C_AGI_DEFINITION,
            "architecture_role": "top_level_system_architecture",
            "construct_substrate_role": (
                "all current reference, candidate, validation-candidate, "
                "failure-bank, and audit nodes are mapped into C-AGI functional layers"
            ),
            "maturity_ladder": [dict(level) for level in C_AGI_MATURITY_LEVELS],
            "current_maturity_estimate": {
                "level_id": "C1",
                "status": "in_progress",
                "reason": (
                    "construct runtime, C-AGI layer mapping, learning/feedback, "
                    "preconstruct review, and bounded autonomy exist; persistent "
                    "autobiographical ledger and embodied sandbox closure are not yet complete"
                ),
            },
            "layer_order": list(C_AGI_LAYER_ORDER),
            "layer_counts": layer_counts,
            "layers": layers,
            "claim_policy": {
                "is_proven_conscious_agi": False,
                "is_consciousness_candidate_agi": True,
                "does_not_claim_subjective_consciousness": True,
                "does_not_claim_human_self_experience": True,
                "does_not_claim_free_will": True,
                "externally_auditable": True,
                "falsifiable_by_hard_negative_tests": True,
                "formal_construct_promotion_requires_l3": True,
                "llm_is_language_interface_not_subject": True,
            },
            "model_substrate_boundary": {
                "llm_role": "cortical_language_interface",
                "model_outputs_are_advisory": True,
                "model_outputs_are_not_status_authority": True,
                "model_outputs_are_not_consciousness_proof": True,
            },
        }

    def boundary_hubs(self, *, limit: int | None = None) -> tuple[tuple[str, int], ...]:
        boundary_counts = Counter()
        for node in self.nodes:
            boundary_counts.update(node.nearest_boundaries)
        return tuple(boundary_counts.most_common(limit))

    def work_queues(self) -> dict[str, list[str]]:
        return {
            "l3_validation_candidate_queue": [
                node.id for node in self.by_role("validation_candidate_queue")
            ],
            "packet_ready_candidate_only_queue": [
                node.id for node in self.by_role("packet_ready_candidate_only")
            ],
            "severe_boundary_watch_queue": [
                node.id for node in self.by_role("severe_boundary_watch")
            ],
            "batch5_governed_rework_queue": [
                node.id for node in self.by_role("batch5_governed_rework")
            ],
            "substitute_pool": [node.id for node in self.by_role("substitute_pool")],
            "pending_local_registration_candidates": [
                node.id for node in self.by_role("pending_local_registration")
            ],
            "active_preconstruct_queue": [
                node.id for node in self.by_role("active_preconstruct")
            ],
            "relation_matrix_required_candidates": [
                node.id for node in self.by_role("relation_matrix_required")
            ],
            "relation_matrix_complete_candidates": [
                node.id for node in self.by_role("relation_matrix_governance_complete")
            ],
            "failure_bank": [node.id for node in self.by_role("negative_control")],
        }

    def capability_assessment(self) -> dict[str, Any]:
        top_boundary_hubs = [
            {"id": node_id, "mentions": mentions}
            for node_id, mentions in self.boundary_hubs(limit=5)
        ]
        return {
            "evolution": {
                "current_level": "temporary_ref_update_rollback_prototype",
                "can_evolve_now": "commit_object_execution_to_temporary_ref_update_rollback",
                "what_it_can_do": [
                    "represent construct maturity as explicit layers",
                    "identify allowed next gates for every route",
                    "surface active preconstruct routes when candidates are not yet review-ready",
                    "retain failure-bank routes as negative controls",
                    "measure boundary hub pressure before opening new routes",
                    "ingest evidence assets when invoked by an operator or agent",
                    "emit transition proposals without granting status changes",
                    "write append-only architecture snapshots",
                    "generate medium-risk review work orders",
                    "run local integrity and claim-firewall checks",
                    "select bounded gate work items from transition proposals",
                    "execute local evidence, boundary, and firewall checks for selected gates",
                    "write append-only autonomous memory records",
                    "compare current evidence assets with prior loop state",
                    "select local research goals after invocation",
                    "run safe non-experimental local probes",
                    "write next-wakeup plans for an external scheduler or operator",
                    "run repeated monitor-goal-probe-memory cycles under a hard local budget",
                    "write runtime heartbeats and stop on stability or cycle budget",
                    "load reviewed local probe approval packets",
                    "execute budgeted deterministic validation probes after approval",
                    "write pass/fail probe evidence without changing construct status",
                    "write reviewed decision artifacts from probe evidence",
                    "accept repeated external scheduler ticks under a medium-risk policy",
                    "chain runtime, approved probes, and reviewed decision artifacts in one scheduled pipeline",
                    "write scheduler heartbeats and state without installing an operating-system task",
                    "generate review-only construct-space hypotheses from decisions, boundary pressure, unmatched evidence, substitutes, and failure banks",
                    "design reviewable experiment and audit plans without executing them",
                    "adversarially review generated hypotheses and plans for support, boundary risk, approval gates, and forbidden actions",
                    "write supervised execution queues without authorizing execution",
                    "execute explicitly approved local plan dry-runs from supervised approval packets",
                    "write execution outcome memory without changing formal construct status",
                    "learn next-cycle priorities from approved execution outcomes",
                    "propose next supervised approval candidates without creating approvals",
                    "load external status-authority decision packets",
                    "apply externally authorized review-state overlays without mutating the source registry",
                    "run planner, critic, safety, and archivist reviews over overlays",
                    "write council consensus ledgers without applying formal status changes",
                    "draft external formal-review proposal packets from retained council consensus",
                    "write formal proposal ledgers without applying formal status transitions",
                    "load externally signed proposal application decisions",
                    "write append-only registry patch drafts without mutating the source registry",
                    "write proposal application ledgers for external maintainer review",
                    "load external maintainer merge decisions for patch drafts",
                    "simulate registry merge overlays without mutating source files",
                    "write maintainer merge ledgers for source-control review",
                    "load external source-control PR draft decisions",
                    "write source-control PR draft packages without creating branches or pull requests",
                    "write PR review checklists and rollback plans for external source-control actors",
                    "load external source-control execution decisions",
                    "write external source-control execution command packets without running git operations",
                    "write preflight checks and rollback plans for external source-control agents",
                    "load external source-control dry-run decisions",
                    "sandbox-validate source-control command plans without running git operations",
                    "write dry-run results for external source-control review",
                    "load external source-control patch-preview decisions",
                    "write isolated source-control patch previews without modifying the worktree",
                    "write diff preview artifacts for external source-control review",
                    "load external source-control apply-simulation decisions",
                    "simulate patch applyability against preview artifacts without modifying the worktree",
                    "write apply-simulation results for external source-control review",
                    "load external source-control patch-applier dry-run decisions",
                    "read target worktree file snapshots for patch dry-run checks",
                    "write read-only patch-applier dry-run results without applying patches",
                    "load external guarded source patch-application decisions",
                    "apply signed marker-level source file mutations with rollback manifests",
                    "write post-application verification artifacts while blocking git operations",
                    "load external source-control read-only git inspection decisions",
                    "execute allowlisted read-only git inspection commands",
                    "write commit preparation packets without git write operations",
                    "load external staging and commit preflight decisions",
                    "validate stage paths and commit command plans without mutating the project index",
                    "load external isolated staging commit execution decisions",
                    "execute git add and git commit inside isolated repositories only",
                    "write isolated commit evidence while preserving project git-index firewalls",
                    "stage approved project paths transiently and verify index rollback",
                    "create project commit objects with git commit-tree while blocking ref updates",
                    "update scoped temporary project refs under refs/codex/experiments/",
                    "delete scoped temporary project refs and verify rollback",
                    "prepare bounded local Ollama advisory prompts from architecture state",
                    "separate local model reasoning from formal status and source-control authority",
                ],
                "what_it_cannot_do_yet": [
                    "wake itself without an already configured external scheduler or operator",
                    "run open-ended validation experiments by itself",
                    "promote or demote constructs without an external review act",
                    "learn new scoring weights from outcomes",
                    "leave project files staged, leave temporary refs behind, move HEAD, update branch refs, or create branch commits by itself",
                    "create branches, pushes, or pull requests after source mutation without an explicit source-control actor",
                ],
                "next_upgrade": "connect temporary ref rollback to explicit branch-ref update or branch-commit authority with rollback gates",
            },
            "thinking": {
                "current_level": "commit_object_to_temporary_ref_update_execution",
                "can_think_now": "operationally yes, phenomenologically no",
                "what_it_can_do": [
                    "classify constructs by layer, role, and mechanism family",
                    "retrieve work queues from role state",
                    "infer boundary hubs from nearest-boundary structure",
                    "compare formal constructs with candidate and preconstruct routes",
                    "enforce claim firewalls during analysis",
                    "turn queue state into reviewable transition proposals",
                    "produce a bounded observe-orient-propose-plan cycle",
                    "select high-priority gate work under a fixed execution budget",
                    "criticize selected gate work for support, boundary overlap, and claim-firewall risk",
                    "remember controlled-cycle outcomes in append-only records",
                    "select research goals from asset changes, unmatched evidence, gate readiness, and boundary pressure",
                    "convert selected goals into safe local probes",
                    "carry deliberation state across repeated runtime cycles",
                    "stop itself when evidence state is stable or the local budget is exhausted",
                    "decide whether reviewed approval packets authorize local probe execution",
                    "turn probe pass/fail evidence into review-only next actions",
                    "convert reviewed probe evidence into decision artifacts while preserving status boundaries",
                    "carry scheduler policy, runtime stability, and reviewed decisions through one tick state",
                    "generate hypotheses about external status readiness, boundary splits, route mapping, failure retention, and substitute scouts",
                    "turn those hypotheses into reviewable experiment plans with controls, hard negatives, measurements, and stop rules",
                    "criticize generated plans for evidence support, boundary overlap, missing approvals, missing stop rules, and unsafe authorization attempts",
                    "separate ready external-review items from revise-before-execution items",
                    "validate supervised execution approvals against A11 review queues",
                    "turn approved dry-run outcomes into append-only memory items",
                    "rank next review priorities from dry-run outcomes and A11 revision holds",
                    "select low-risk next approval candidates from the supervised queue",
                    "validate external authority decisions against A13 priority updates",
                    "separate review-state overlays from formal construct status transitions",
                    "challenge overlays through planner, critic, safety, and archivist roles",
                    "derive consensus verdicts from separated role reviews",
                    "convert retained council consensus into external-review proposal drafts",
                    "preserve unresolved council concerns as hard proposal conditions",
                    "validate signed application decisions against proposal drafts and firewalls",
                    "convert accepted application decisions into append-only patch drafts",
                    "validate maintainer merge decisions against patch drafts and source-mutation firewalls",
                    "simulate registry overlay effects without touching source files",
                    "validate source-control PR draft decisions against overlay provenance and git side-effect firewalls",
                    "compose PR titles, branch names, review checklists, and rollback plans from simulated overlays",
                    "validate source-control execution decisions against PR-draft provenance and runtime git firewalls",
                    "translate PR draft packages into external command plans with preflight and rollback conditions",
                    "validate source-control dry-run decisions against execution packet provenance",
                    "check command-plan syntax, preflight coverage, expected artifacts, and rollback shape without executing git",
                    "validate source-control patch-preview decisions against dry-run provenance",
                    "compose artifact-only diff previews from passing dry-run results",
                    "validate source-control apply-simulation decisions against patch-preview provenance",
                    "simulate diff hunk applyability in preview space while preserving worktree firewalls",
                    "validate source-control patch-applier dry-run decisions against apply-simulation provenance",
                    "inspect target file snapshots and classify patch dry-run readiness without applying patches",
                    "validate guarded patch-application decisions against dry-run provenance",
                    "plan rollback-backed marker-level source mutations while preserving formal status firewalls",
                    "validate read-only git inspection results before staging preflight",
                "derive project stage path plans from commit readiness evidence",
                "separate isolated git execution from project git-index mutation",
                "interpret isolated commit success as execution evidence, not formal construct promotion",
                "reason from project-index rollback proof to commit-object execution without treating it as branch history",
                "reason from commit-object proof to scoped temporary ref movement without treating it as branch history",
            ],
                "what_it_cannot_do_yet": [
                    "form project goals without a caller",
                    "execute open-ended experiments",
                    "evaluate raw experimental traces",
                    "generate new construct definitions from data",
                    "possess subjective awareness or conscious thought",
                    "treat local LLM output as consciousness, self-experience, free will, or governance authority",
                ],
                "top_boundary_hubs": top_boundary_hubs,
            },
            "autonomy": {
                "current_level": "project_temporary_ref_update_rollback_executor",
                "can_act_now": "A32 project temporary ref update rollback prototype",
                "what_it_can_do": [
                    "answer architecture queries through API or CLI",
                    "export a stable JSON snapshot",
                    "suggest next gate classes from stored metadata",
                    "block unsafe claim escalation in exported state",
                    "read evidence directories when invoked",
                    "generate a bounded execution plan that separates no-approval observation from approval-required transition work",
                    "write local review packets, integrity checks, work-order drafts, and append-only architecture snapshots",
                    "run an invoked think-criticize-execute-remember cycle over selected local gate checks",
                    "compare asset inventories across loop runs",
                    "self-select local goals after invocation",
                    "run safe local probes and update loop state",
                    "continue through multiple autonomous cycles after a single invocation",
                    "write per-cycle heartbeats and stop on explicit runtime criteria",
                    "execute approved deterministic local validation probes under hard budgets",
                    "block unapproved, over-budget, or unknown probe requests",
                    "write reviewed decision artifacts without applying them",
                    "run the runtime and reviewed decision writer together from a scheduler-ready CLI tick",
                    "record scheduler heartbeats, state, and manifests for repeated external invocation",
                    "generate hypothesis cards and review-only experiment plans after a scheduled tick",
                    "adversarially review generated hypotheses and queue externally supervised plan candidates",
                    "execute approved deterministic local plan dry-runs under explicit supervised approvals",
                    "write dry-run execution memory while blocking construct status transitions",
                    "convert execution outcomes into adaptive next-tick strategy guidance",
                    "rank future supervised approval candidates after execution",
                    "write externally authorized review-state overlays for downstream tools",
                    "defer unreviewed adaptive updates without changing the source registry",
                    "run deterministic multi-role council review over review-state overlays",
                    "write council memory while blocking formal status transitions",
                    "assemble formal proposal drafts and external review packets from council consensus",
                    "write proposal memory while blocking formal status application",
                    "validate signed proposal application decision packets",
                    "write append-only registry patch drafts for external maintainer review",
                    "write proposal application memory while blocking source registry mutation",
                    "validate external maintainer merge decision packets",
                    "write simulated registry merge overlays while blocking source file mutation",
                    "write maintainer merge memory for source-control review",
                    "validate external source-control PR draft decisions",
                    "write source-control PR draft packages without creating branches, commits, pushes, or pull requests",
                    "write PR draft memory while blocking source-control side effects",
                    "validate external source-control execution decisions",
                    "write source-control execution packets and command plans for an external actor",
                    "write execution packet memory while blocking runtime git side effects",
                    "validate external source-control dry-run decisions",
                    "run static sandbox validation over command packets without spawning git",
                    "write dry-run result memory while blocking runtime git side effects",
                    "validate external source-control patch-preview decisions",
                    "write isolated patch preview artifacts without modifying the worktree",
                    "write patch-preview memory while blocking source-file mutation",
                    "validate external source-control apply-simulation decisions",
                    "write apply-simulation results without applying patches to the worktree",
                    "write apply-simulation memory while blocking source-file mutation",
                    "validate external source-control patch-applier dry-run decisions",
                    "read worktree target file snapshots for dry-run checks",
                    "write patch-applier dry-run memory while blocking patch application",
                    "validate external guarded source patch-application decisions",
                    "write rollback-backed marker-level source mutations",
                    "write guarded patch-application memory while blocking git side effects",
                    "execute read-only git inspection commands after external approval",
                    "write staging and commit preflight packets after external approval",
                    "execute git add and git commit in isolated repositories after external approval",
                    "verify isolated commit hashes without mutating the project git index",
                    "perform rollback-verified project-index staging after external approval",
                    "create project commit objects after A30 rollback proof while blocking ref updates",
                    "update scoped temporary project refs after A31 commit-object proof",
                    "delete scoped temporary refs and verify final absence",
                    "run invoked local Ollama probes as advisory reasoning only",
                    "record local model outputs as review artifacts without granting authority",
                ],
                "what_it_cannot_do_yet": [
                    "wake up without an already configured external scheduler",
                    "run open-ended validation experiments",
                    "leave project files staged, leave temporary refs behind, move HEAD, update branch refs, open pull requests, or change construct status by itself",
                    "use a local model to wake itself, approve itself, or bypass review gates",
                    "close the review loop without a human or agent operator",
                ],
                "minimum_safe_upgrade_path": [
                    "scheduled read-only asset watcher",
                    "candidate delta detector with append-only logs",
                    "human-reviewed gate execution",
                    "append-only architecture snapshot update",
                    "isolated git execution validation",
                    "project-index rollback authority",
                    "project commit-object authority without ref update",
                    "temporary ref-update authority with delete rollback",
                    "explicit branch-ref update or branch-commit gate",
                ],
            },
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "consciousness_benchmark.construct_architecture.v1",
            "created_at": "2026-05-31",
            "claim_policy": {
                "reference_constructs_are_closed_by_default": True,
                "validation_candidates_require_l3_before_reference_discussion": True,
                "candidate_only_routes_do_not_update_reference_constructs": True,
                "preconstructs_are_substitute_routes_not_evidence": True,
                "does_not_claim_subjective_consciousness": True,
                "does_not_claim_human_self_experience": True,
                "does_not_claim_free_will": True,
                "subjective_experience_cannot_be_externally_proven": True,
            },
            "counts": {
                "nodes": len(self.nodes),
                "construct_nodes": len(self.construct_nodes()),
                "layers": self.summary_counts(),
                "roles": self.role_counts(),
                "families": self.family_counts(),
                "c_agi_layers": self.c_agi_layer_counts(),
            },
            "mind_construct_inventory": self.mind_construct_inventory(),
            "c_agi_architecture": self.c_agi_architecture(),
            "work_queues": self.work_queues(),
            "boundary_hubs": [
                {"id": node_id, "mentions": mentions}
                for node_id, mentions in self.boundary_hubs()
            ],
            "capability_assessment": self.capability_assessment(),
            "architecture_identity": {
                "target": "C-AGI: Consciousness-Candidate AGI",
                "legacy_target": "interpretable_human_like_mind_architecture",
                "positive_claim": "externally auditable and falsifiable consciousness-candidate AGI architecture with complete endogenous mind-structure execution, predictable behavior, explainable capabilities, and controllable boundaries",
                "integration_scope": [
                    "five formal reference constructs",
                    "84 current candidate or validation-candidate constructs after the 2026-06-02 HCTM audit-assets intake",
                    "31 pending local-registration candidates from the 2026-06-01/02 HCTM audit assets",
                    "no active preconstruct routes after the communication repair candidate-only registration",
                    "failure-bank routes retained as negative controls",
                    "eight C-AGI functional layers with LLM/local models treated as substrate adapters rather than the subject itself",
                ],
                "not_claimed": [
                    "proven conscious AGI",
                    "subjective consciousness",
                    "human self-experience",
                    "free will",
                    "externally provable subjective feeling",
                ],
                "comparison_to_current_ai": "current LLM/agent systems are treated as statistical imitators; this target architecture is a governed mind executor",
            },
            "nodes": [node.to_dict() for node in self.nodes],
        }

    def summary_markdown(self) -> str:
        lines = [
            "# C-AGI Construct Architecture",
            "",
            "| C-AGI Layer | Count |",
            "|---|---:|",
        ]
        for layer, count in self.c_agi_layer_counts().items():
            lines.append(f"| `{layer}` | {count} |")

        lines.extend(
            [
                "",
                "| Evidence Layer | Count |",
                "|---|---:|",
            ]
        )
        for layer, count in self.summary_counts().items():
            lines.append(f"| `{layer}` | {count} |")
        lines.extend(
            [
                "",
                "| Node | C-AGI layer | Evidence layer | Family | Next gate |",
                "|---|---|---|---|---|",
            ]
        )
        for node in self.nodes:
            lines.append(
                f"| `{node.id}` | `{node.c_agi_layer}` | `{node.layer}` | `{node.mechanism_family}` | {node.next_gate} |"
            )
        return "\n".join(lines)


PTCG_REGISTRY_ROUTE_IDS = (
    "macro_causal_viability_maintenance",
    "reference_construct_phase_audit",
    "temporal_horizon_dependent_planning",
    "uncertainty_threshold_metacognition",
    "information_integration_phase",
    "global_broadcast_phase",
    "self_other_boundary_sharpness",
    "coupled_viability_metacognition_phase",
    "hierarchical_phase_cascade",
    "social_coupling_strength_collective_agency",
    "causal_model_abstraction_hierarchy",
    "counterfactual_reasoning_depth",
    "goal_hierarchy_emergence",
    "predictive_error_minimization_phase",
    "attention_control",
    "causal_attribution",
    "prospective_memory",
    "episodic_memory_binding",
    "strategy_selection",
    "information_flow_onset_gating",
    "perspective_taking",
    "branch_binding_stability",
    "error_monitoring",
    "coordination_length_control",
    "cross_family_synergy_control",
    "resource_competition_arbitration",
    "latent_context_switch_detection",
    "temporal_credit_assignment",
    "goal_conflict_resolution",
    "affordance_selection_control",
    "contextual_policy_inhibition",
    "working_memory_capacity_rework",
    "social_norm_tracking",
    "semantic_memory_retrieval_control",
    "divergent_thinking",
    "learning_rate_adaptation_rework",
    "analogical_reasoning_rework",
    "confidence_calibration_rework",
    "body_schema_error_correction",
    "cooperation_policy_switching_rework",
    "spatial_navigation_remapping_rework",
    "predictive_control_under_action_intervention",
    "insight_problem_solving_rework",
    "counterfactual_repair_planning_rework",
    "multi_agent_commitment_tracking",
    "norm_violation_repair",
    "self_other_prediction_error_arbitration",
    "constraint_satisfaction_reconfiguration",
    "integration_without_broadcast_boundary",
    "metacognitive_repair_control",
)


PTCG_PRECONSTRUCT_FRONTIER_IDS = (
    "episodic_memory_binding",
    "prospective_memory",
    "error_monitoring",
    "strategy_selection",
    "perspective_taking",
    "causal_attribution",
    "information_flow_onset_gating",
    "coordination_length_control",
    "branch_binding_stability",
    "resource_competition_arbitration",
    "cross_family_synergy_control",
    "working_memory_capacity_rework",
    "social_norm_tracking",
    "divergent_thinking",
    "contextual_policy_inhibition",
    "semantic_memory_retrieval_control",
    "confidence_calibration_rework",
    "learning_rate_adaptation_rework",
    "cooperation_policy_switching_rework",
    "analogical_reasoning_rework",
    "insight_problem_solving_rework",
    "spatial_navigation_remapping_rework",
    "metacognitive_repair_control",
    "goal_conflict_resolution",
    "temporal_credit_assignment",
    "counterfactual_repair_planning_rework",
    "body_schema_error_correction",
    "self_other_prediction_error_arbitration",
    "affordance_selection_control",
    "latent_context_switch_detection",
    "constraint_satisfaction_reconfiguration",
    "norm_violation_repair",
    "multi_agent_commitment_tracking",
    "hierarchical_credit_assignment",
    "selective_global_broadcast_control",
    "integration_without_broadcast_boundary",
    "predictive_control_under_action_intervention",
    "agency_without_ownership_boundary",
    "temporal_identity_planning_dissociation",
)


FRONTIER_METADATA = {
    "episodic_memory_binding": (
        "memory",
        ("identity_temporal_self", "working_memory_capacity", "temporal_horizon_planning"),
    ),
    "prospective_memory": (
        "memory_control",
        ("temporal_horizon_dependent_planning", "identity_temporal_self", "attention_control"),
    ),
    "error_monitoring": (
        "metacognition",
        ("attention_control", "uncertainty_threshold_metacognition", "action_agency"),
    ),
    "strategy_selection": (
        "metacognitive_control",
        ("uncertainty_threshold_metacognition", "attention_control", "goal_hierarchy_emergence"),
    ),
    "perspective_taking": (
        "social_cognition",
        ("self_other_boundary_sharpness", "social_coupling_strength_collective_agency", "boundary_self"),
    ),
    "causal_attribution": (
        "causal_reasoning",
        ("counterfactual_reasoning_depth", "action_agency", "error_monitoring"),
    ),
    "information_flow_onset_gating": (
        "information_control",
        ("information_integration_phase", "attention_control", "uncertainty_threshold_metacognition"),
    ),
    "coordination_length_control": (
        "coordination_control",
        ("global_broadcast_phase", "information_integration_phase", "distributed_body_schema_self"),
    ),
    "branch_binding_stability": (
        "binding_control",
        ("goal_hierarchy_emergence", "temporal_horizon_dependent_planning", "episodic_memory_binding"),
    ),
    "resource_competition_arbitration": (
        "resource_control",
        ("attention_control", "strategy_selection", "global_broadcast_phase"),
    ),
    "cross_family_synergy_control": (
        "interaction_control",
        ("resource_competition_arbitration", "coordination_length_control", "strategy_selection"),
    ),
    "working_memory_capacity_rework": (
        "memory_control",
        ("attention_control", "episodic_memory_binding", "strategy_selection"),
    ),
    "social_norm_tracking": (
        "social_cognition",
        ("perspective_taking", "social_coupling_strength_collective_agency", "error_monitoring"),
    ),
    "divergent_thinking": (
        "generative_control",
        ("goal_hierarchy_emergence", "strategy_selection", "semantic_memory_retrieval_control"),
    ),
    "contextual_policy_inhibition": (
        "executive_control",
        ("attention_control", "action_agency", "strategy_selection"),
    ),
    "semantic_memory_retrieval_control": (
        "memory",
        ("episodic_memory_binding", "working_memory_capacity_rework", "strategy_selection"),
    ),
    "confidence_calibration_rework": (
        "metacognition",
        ("uncertainty_threshold_metacognition", "error_monitoring", "strategy_selection"),
    ),
    "learning_rate_adaptation_rework": (
        "learning_control",
        ("predictive_error_minimization_phase", "strategy_selection", "error_monitoring"),
    ),
    "cooperation_policy_switching_rework": (
        "social_control",
        ("social_coupling_strength_collective_agency", "strategy_selection", "perspective_taking"),
    ),
    "analogical_reasoning_rework": (
        "abstract_reasoning",
        ("causal_attribution", "causal_model_abstraction_hierarchy", "semantic_memory_retrieval_control"),
    ),
    "insight_problem_solving_rework": (
        "problem_solving",
        ("strategy_selection", "divergent_thinking", "goal_hierarchy_emergence"),
    ),
    "spatial_navigation_remapping_rework": (
        "spatial_control",
        ("distributed_body_schema_self", "temporal_horizon_dependent_planning", "attention_control"),
    ),
    "metacognitive_repair_control": (
        "metacognitive_control",
        ("error_monitoring", "uncertainty_threshold_metacognition", "strategy_selection"),
    ),
    "goal_conflict_resolution": (
        "goal_control",
        ("goal_hierarchy_emergence", "resource_competition_arbitration", "strategy_selection"),
    ),
    "temporal_credit_assignment": (
        "temporal_control",
        ("macro_causal_viability_maintenance", "temporal_horizon_dependent_planning", "causal_attribution"),
    ),
    "counterfactual_repair_planning_rework": (
        "counterfactual_control",
        ("counterfactual_reasoning_depth", "causal_attribution", "temporal_horizon_dependent_planning"),
    ),
    "body_schema_error_correction": (
        "sensorimotor_control",
        ("distributed_body_schema_self", "error_monitoring", "action_ownership"),
    ),
    "self_other_prediction_error_arbitration": (
        "social_sensorimotor_control",
        ("self_other_boundary_sharpness", "error_monitoring", "action_ownership"),
    ),
    "affordance_selection_control": (
        "action_control",
        ("action_agency", "attention_control", "action_ownership"),
    ),
    "latent_context_switch_detection": (
        "context_control",
        ("learning_rate_adaptation_rework", "strategy_selection", "error_monitoring"),
    ),
    "constraint_satisfaction_reconfiguration": (
        "problem_solving",
        ("insight_problem_solving_rework", "divergent_thinking", "goal_hierarchy_emergence"),
    ),
    "norm_violation_repair": (
        "social_control",
        ("social_norm_tracking", "error_monitoring", "strategy_selection"),
    ),
    "multi_agent_commitment_tracking": (
        "social_temporal_control",
        ("prospective_memory", "social_coupling_strength_collective_agency", "cooperation_policy_switching_rework"),
    ),
    "hierarchical_credit_assignment": (
        "hierarchical_control",
        ("temporal_credit_assignment", "goal_hierarchy_emergence", "macro_causal_viability_maintenance"),
    ),
    "selective_global_broadcast_control": (
        "workspace_control",
        ("global_broadcast_phase", "attention_control", "coordination_length_control"),
    ),
    "integration_without_broadcast_boundary": (
        "integration_control",
        ("information_integration_phase", "global_broadcast_phase", "coordination_length_control"),
    ),
    "predictive_control_under_action_intervention": (
        "predictive_control",
        ("predictive_error_minimization_phase", "temporal_credit_assignment", "causal_attribution"),
    ),
    "agency_without_ownership_boundary": (
        "self_action_boundary",
        ("action_agency", "action_ownership", "self_other_boundary_sharpness"),
    ),
    "temporal_identity_planning_dissociation": (
        "temporal_self_control",
        ("identity_temporal_self", "temporal_horizon_dependent_planning", "prospective_memory"),
    ),
    "clock_drift_resynchronization_control": (
        "temporal_control",
        ("temporal_horizon_dependent_planning", "prospective_memory", "temporal_credit_assignment"),
    ),
    "energy_budget_reallocation_control": (
        "resource_control",
        ("resource_competition_arbitration", "attention_control", "strategy_selection"),
    ),
    "sensor_gain_recalibration_control": (
        "sensorimotor_control",
        ("predictive_error_minimization_phase", "body_schema_error_correction", "attention_control"),
    ),
    "tool_use_affordance_remapping": (
        "action_control",
        ("affordance_selection_control", "body_schema_error_correction", "spatial_navigation_remapping_rework"),
    ),
    "actuator_failure_compensation_control": (
        "motor_infrastructure_control",
        (
            "body_schema_error_correction",
            "predictive_control_under_action_intervention",
            "action_agency",
            "action_ownership",
            "tool_use_affordance_remapping",
            "sensor_gain_recalibration_control",
        ),
    ),
    "preference_reversal_adaptation_control": (
        "value_policy_control",
        (
            "strategy_selection",
            "goal_conflict_resolution",
            "resource_competition_arbitration",
            "social_norm_tracking",
            "confidence_calibration_rework",
            "error_monitoring",
        ),
    ),
    "communication_channel_repair_control": (
        "communication_control",
        ("multi_agent_commitment_tracking", "social_norm_tracking", "semantic_memory_retrieval_control"),
    ),
    "accountability_obligation_scope_response_control": (
        "obligation_control",
        (
            "multi_agent_commitment_tracking",
            "social_norm_tracking",
            "norm_violation_repair",
            "action_ownership",
            "strategy_selection",
            "error_monitoring",
        ),
    ),
    "counter_evidence_preservation_control": (
        "evidence_control",
        (
            "causal_attribution",
            "counterfactual_reasoning_depth",
            "semantic_memory_retrieval_control",
            "error_monitoring",
            "provenance_weighted_evidence_integration_control",
            "uncertainty_threshold_metacognition",
        ),
    ),
    "counterparty_intent_uncertainty_resolution_control": (
        "social_boundary",
        (
            "perspective_taking",
            "self_other_boundary_sharpness",
            "counterfactual_reasoning_depth",
            "uncertainty_threshold_metacognition",
            "social_norm_tracking",
            "multi_agent_commitment_tracking",
        ),
    ),
    "credential_validity_challenge_response_control": (
        "communication_control",
        (
            "communication_channel_repair_control",
            "provenance_weighted_evidence_integration_control",
            "semantic_memory_retrieval_control",
            "permission_revocation_compliance_control",
            "error_monitoring",
            "strategy_selection",
        ),
    ),
    "deadline_obligation_triage_control": (
        "temporal_control",
        (
            "prospective_memory",
            "temporal_horizon_dependent_planning",
            "goal_conflict_resolution",
            "priority_starvation_prevention_control",
            "resource_competition_arbitration",
            "irreversible_commitment_safeguard_control",
        ),
    ),
    "observation_budget_allocation_control": (
        "resource_control",
        (
            "attention_control",
            "information_flow_onset_gating",
            "observation_dropout_bridging_control",
            "resource_competition_arbitration",
            "option_value_preserving_probe_control",
            "sensor_gain_recalibration_control",
        ),
    ),
    "sample_representativeness_reweighting_control": (
        "evidence_control",
        (
            "information_integration_phase",
            "provenance_weighted_evidence_integration_control",
            "semantic_memory_retrieval_control",
            "counter_evidence_preservation_control",
            "uncertainty_threshold_metacognition",
            "attention_control",
        ),
    ),
}


REFERENCE_ROWS = (
    (
        "action_agency",
        "action",
        "validated operational reference construct",
        "action-outcome loop",
    ),
    (
        "boundary_self",
        "workspace",
        "validated operational reference construct",
        "workspace boundary maintenance",
    ),
    (
        "identity_temporal_self",
        "temporal_self",
        "validated operational reference construct",
        "workspace temporal identity",
    ),
    (
        "action_ownership",
        "action",
        "validated operational reference construct",
        "action-outcome attribution",
    ),
    (
        "distributed_body_schema_self",
        "social_boundary",
        "validated operational reference construct with graded controls",
        "distributed body-schema meta-monitor",
    ),
)


VALIDATION_CANDIDATE_ROWS = (
    (
        "macro_causal_viability_maintenance",
        "temporal_credit",
        "validation candidate accepted under narrowed claim",
        "L3 external-owner replication before reference discussion",
    ),
    (
        "temporal_horizon_dependent_planning",
        "temporal_credit",
        "validation candidate accepted under narrowed claim",
        "L3 external-owner replication before reference discussion",
    ),
    (
        "uncertainty_threshold_metacognition",
        "metacognition",
        "validation candidate accepted under narrowed claim",
        "L3 external-owner replication before reference discussion",
    ),
    (
        "information_integration_phase",
        "workspace",
        "validation candidate accepted under narrowed claim",
        "L3 external-owner replication before reference discussion",
    ),
    (
        "attention_control",
        "metacognition",
        "validation candidate accepted under narrowed internal claim",
        "L3 external-owner replication before reference discussion",
    ),
)


CANDIDATE_ROWS = (
    ("global_broadcast_phase", "workspace", "candidate accepted under narrowed claim", "validation-candidate rework packet"),
    ("self_other_boundary_sharpness", "social_boundary", "candidate accepted under narrowed claim", "validation-candidate rework packet"),
    ("social_coupling_strength_collective_agency", "social_boundary", "candidate accepted under narrowed claim", "validation-candidate rework packet"),
    ("counterfactual_reasoning_depth", "causal_counterfactual", "candidate accepted after v2 boundary rework", "validation-candidate rework packet"),
    ("goal_hierarchy_emergence", "resource_problem", "candidate accepted after v2 boundary rework", "validation-candidate rework packet"),
    ("predictive_error_minimization_phase", "causal_counterfactual", "candidate accepted after v2 boundary rework", "validation-candidate rework packet"),
    ("causal_attribution", "causal_counterfactual", "candidate accepted under narrowed claim", "rework packet or mechanism-origins audit"),
    ("prospective_memory", "temporal_credit", "candidate accepted under narrowed claim", "rework packet or mechanism-origins audit"),
    ("episodic_memory_binding", "memory", "candidate accepted under narrowed claim", "rework packet or mechanism-origins audit"),
    ("strategy_selection", "metacognition", "candidate accepted with boundary watch", "boundary-watch rework"),
    ("information_flow_onset_gating", "workspace", "candidate accepted with boundary watch", "boundary-watch rework"),
    ("perspective_taking", "social_boundary", "candidate accepted with boundary watch", "boundary-watch rework"),
    ("branch_binding_stability", "memory", "candidate accepted with boundary watch", "boundary-watch rework"),
    ("error_monitoring", "metacognition", "candidate accepted, internal rework progressed, packet ready", "L2.5 or L3 execution"),
    ("coordination_length_control", "workspace", "candidate accepted with margin and boundary watch", "margin and boundary rework"),
    ("cross_family_synergy_control", "resource_problem", "candidate accepted with severe boundary watch", "resource-competition separation"),
    ("resource_competition_arbitration", "resource_problem", "candidate accepted with severe boundary watch", "cross-family and strategy boundary watch"),
    ("latent_context_switch_detection", "memory", "candidate accepted, internal rework progressed, packet ready", "L2.5 or L3 execution"),
    ("temporal_credit_assignment", "temporal_credit", "candidate accepted with margin and severe boundary watch", "macro-causal and causal-attribution boundary watch"),
    ("goal_conflict_resolution", "resource_problem", "candidate accepted with severe boundary watch", "resource, strategy, and goal-hierarchy boundary watch"),
    ("affordance_selection_control", "action", "candidate accepted with severe boundary watch", "action-agency, attention, strategy boundary watch"),
    ("contextual_policy_inhibition", "metacognition", "candidate accepted with severe boundary watch", "strategy, attention, context, error boundary watch"),
    ("working_memory_capacity_rework", "memory", "candidate accepted after rework with severe boundary watch", "attention, episodic, strategy boundary watch"),
    ("social_norm_tracking", "social_boundary", "candidate accepted with severe boundary watch", "perspective, social-coupling, error, strategy boundary watch"),
    ("semantic_memory_retrieval_control", "memory", "candidate accepted with severe boundary watch", "episodic, working-memory, strategy boundary watch"),
    ("divergent_thinking", "resource_problem", "candidate accepted with severe boundary watch", "goal, strategy, semantic, complexity boundary watch"),
    ("learning_rate_adaptation_rework", "metacognition", "candidate accepted with boundary watch", "predictive-error, strategy, error boundary watch"),
    ("analogical_reasoning_rework", "causal_counterfactual", "candidate accepted with boundary watch", "causal, semantic, abstraction, strategy boundary watch"),
    ("confidence_calibration_rework", "metacognition", "candidate accepted with severe boundary watch", "uncertainty, error, strategy, learning-rate boundary watch"),
    ("body_schema_error_correction", "action", "candidate accepted with boundary watch", "body-schema, error, ownership, agency boundary watch"),
    ("cooperation_policy_switching_rework", "social_boundary", "candidate accepted with boundary watch", "social, strategy, prospective, multi-agent boundary watch"),
    ("spatial_navigation_remapping_rework", "resource_problem", "candidate accepted with boundary watch", "body-schema, temporal, attention boundary watch"),
    ("predictive_control_under_action_intervention", "action", "candidate accepted with boundary watch", "full rework packet and L3 requirements"),
    ("insight_problem_solving_rework", "resource_problem", "candidate accepted with boundary watch", "strategy, divergent, goal, memory, semantic boundary watch"),
    ("counterfactual_repair_planning_rework", "causal_counterfactual", "candidate accepted with severe boundary watch", "full rework packet and L3 requirements"),
    ("multi_agent_commitment_tracking", "social_boundary", "candidate accepted with boundary watch", "prospective, social, cooperation, strategy boundary watch"),
    ("norm_violation_repair", "social_boundary", "candidate accepted with boundary watch", "social, error, strategy, norm boundary watch"),
    ("self_other_prediction_error_arbitration", "social_boundary", "candidate accepted with boundary watch", "L2.5 or L3 execution"),
    ("constraint_satisfaction_reconfiguration", "resource_problem", "candidate accepted with boundary watch", "L2.5 or L3 execution"),
    ("integration_without_broadcast_boundary", "workspace", "candidate accepted with boundary watch", "L2.5 or L3 execution"),
    ("metacognitive_repair_control", "metacognition", "candidate accepted with boundary watch", "L2.5 or L3 execution"),
    ("hierarchical_credit_assignment", "temporal_credit", "candidate accepted from completed 39-route preconstruct frontier", "route-specific validation-candidate rework packet"),
    ("selective_global_broadcast_control", "workspace", "candidate accepted from completed 39-route preconstruct frontier", "route-specific validation-candidate rework packet"),
    ("agency_without_ownership_boundary", "action", "candidate accepted from completed 39-route preconstruct frontier", "route-specific validation-candidate rework packet"),
    ("temporal_identity_planning_dissociation", "temporal_self", "candidate accepted from completed 39-route preconstruct frontier", "route-specific validation-candidate rework packet"),
    ("checkpoint_rollback_recovery_control", "recovery_control", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only internal or relation-matrix route"),
    ("feedback_channel_integrity_reweighting_control", "communication_control", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("instruction_scope_binding_control", "communication_control", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("interface_protocol_negotiation_control", "communication_control", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("interference_source_separation_control", "resource_control", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("irreversible_commitment_safeguard_control", "metacognition", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("latent_state_alias_disambiguation_control", "memory", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("localized_regime_shift_quarantine_control", "temporal_control", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("memory_index_corruption_rebinding_control", "memory", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("model_staleness_detection_control", "metacognition", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("observation_dropout_bridging_control", "workspace", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("option_value_preserving_probe_control", "resource_problem", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("permission_revocation_compliance_control", "social_boundary", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("priority_starvation_prevention_control", "resource_control", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("provenance_weighted_evidence_integration_control", "metacognition", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("redundant_pathway_failover_control", "resource_problem", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("representation_format_translation_control", "communication_control", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("sensorimotor_latency_compensation_control", "sensorimotor_control", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("side_effect_containment_control", "resource_control", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("unit_frame_normalization_control", "workspace", "candidate accepted under narrowed claim; pending local architecture registration", "candidate-only QA closure and preconstruct support"),
    ("clock_drift_resynchronization_control", "temporal_control", "candidate accepted under narrowed claim; pending local architecture registration", "hold as candidate-only or relation matrix before validation-candidate review"),
    ("energy_budget_reallocation_control", "resource_control", "candidate accepted under narrowed claim; pending local architecture registration", "write L3-ready card QA or relation matrix before validation-candidate review"),
    ("sensor_gain_recalibration_control", "sensorimotor_control", "candidate accepted under narrowed claim; pending local architecture registration", "write L3-ready card QA or relation matrix before validation-candidate review"),
    ("tool_use_affordance_remapping", "action_control", "candidate accepted under narrowed claim; pending local architecture registration", "hold as candidate-only or validation-candidate rework after budget checkpoint"),
    ("actuator_failure_compensation_control", "motor_infrastructure_control", "candidate accepted under narrowed claim; L3-ready carded; relation matrix clean", "external or clean-room replication packet before validation-candidate review"),
    ("communication_channel_repair_control", "communication_control", "candidate accepted under narrowed claim; candidate-only internal; QA passed; relation matrix clean", "external or clean-room independent implementation packet before validation-candidate review"),
    ("preference_reversal_adaptation_control", "value_policy_control", "candidate accepted under narrowed claim; L3-ready carded; QA passed; relation matrix pending", "open preference-reversal relation matrix before next low-overlap intake"),
    ("accountability_obligation_scope_response_control", "obligation_control", "candidate accepted under narrowed claim; pending local architecture registration; L3-ready carded", "relation matrix or external probe packet before validation-candidate review"),
    ("counter_evidence_preservation_control", "evidence_control", "candidate accepted under narrowed claim; pending local architecture registration; L3-ready carded", "relation matrix or external probe packet before validation-candidate review"),
    ("counterparty_intent_uncertainty_resolution_control", "social_boundary", "candidate accepted under narrowed claim; pending local architecture registration; L3-ready carded", "relation matrix or external probe packet before validation-candidate review"),
    ("credential_validity_challenge_response_control", "communication_control", "candidate accepted under narrowed claim; pending local architecture registration; L3-ready carded", "relation matrix or external probe packet before validation-candidate review"),
    ("deadline_obligation_triage_control", "temporal_control", "candidate accepted under narrowed claim; pending local architecture registration; L3-ready carded", "relation matrix or external probe packet before validation-candidate review"),
    ("observation_budget_allocation_control", "resource_control", "candidate accepted under narrowed claim; pending local architecture registration; L3-ready carded", "relation matrix or external probe packet before validation-candidate review"),
    ("sample_representativeness_reweighting_control", "evidence_control", "candidate accepted under narrowed claim; pending local architecture registration; L3-ready carded", "relation matrix or external probe packet before validation-candidate review"),
)


FAILURE_BANK_ROWS = (
    ("coupled_viability_metacognition_phase", "temporal_credit", "frozen failure bank after v2 boundary rework failure", "new definition and boundary mechanism"),
    ("hierarchical_phase_cascade", "temporal_credit", "rejected scout failure bank due to hard-negative leakage", "simultaneous-onset decoy solution"),
    ("causal_model_abstraction_hierarchy", "causal_counterfactual", "frozen failure bank after v2 boundary rework failure", "new definition and boundary mechanism"),
)


PRECONSTRUCT_ROWS: tuple[tuple[str, str, str, str], ...] = ()


PACKET_READY_IDS = {
    "error_monitoring",
    "latent_context_switch_detection",
    "self_other_prediction_error_arbitration",
    "constraint_satisfaction_reconfiguration",
    "integration_without_broadcast_boundary",
    "metacognitive_repair_control",
}

SEVERE_BOUNDARY_WATCH_IDS = {
    "cross_family_synergy_control",
    "resource_competition_arbitration",
    "temporal_credit_assignment",
    "goal_conflict_resolution",
    "affordance_selection_control",
    "contextual_policy_inhibition",
    "working_memory_capacity_rework",
    "social_norm_tracking",
    "semantic_memory_retrieval_control",
    "divergent_thinking",
    "confidence_calibration_rework",
    "counterfactual_repair_planning_rework",
}

BATCH5_REWORK_IDS = {"strategy_selection", "perspective_taking"}


RELATION_MATRIX_REQUIRED_IDS = {
    "preference_reversal_adaptation_control",
}


RELATION_MATRIX_COMPLETE_IDS = {
    "actuator_failure_compensation_control",
    "communication_channel_repair_control",
}


INDEPENDENT_PROBE_CARDED_CANDIDATE_IDS = {
    "accountability_obligation_scope_response_control",
    "counter_evidence_preservation_control",
    "counterparty_intent_uncertainty_resolution_control",
    "credential_validity_challenge_response_control",
    "deadline_obligation_triage_control",
    "observation_budget_allocation_control",
    "sample_representativeness_reweighting_control",
}


L3_READY_CARDED_CANDIDATE_IDS = (
    RELATION_MATRIX_REQUIRED_IDS
    | RELATION_MATRIX_COMPLETE_IDS
    | INDEPENDENT_PROBE_CARDED_CANDIDATE_IDS
)


SUPPLEMENTAL_SOURCE_ASSETS = {
    "actuator_failure_compensation_control": (
        f"{HCTM_20260601_SOURCE}/actuator_failure_compensation_control_l3_ready_preconstruct_card_20260601.json",
        f"{HCTM_20260601_SOURCE}/ptcg_actuator_failure_compensation_candidate_qa_closure_20260601.json",
        f"{HCTM_20260601_SOURCE}/ptcg_actuator_failure_compensation_relation_matrix_20260601.json",
    ),
    "preference_reversal_adaptation_control": (
        f"{HCTM_20260601_SOURCE}/preference_reversal_adaptation_control_l3_ready_preconstruct_card_20260601.json",
        f"{HCTM_20260601_SOURCE}/ptcg_preference_reversal_adaptation_candidate_qa_closure_20260601.json",
    ),
    "communication_channel_repair_control": (
        f"{HCTM_20260601_SOURCE}/communication_channel_repair_control_l3_ready_preconstruct_card_20260601.json",
        f"{HCTM_20260601_SOURCE}/ptcg_communication_channel_repair_candidate_checkpoint_20260601.json",
        f"{HCTM_20260601_SOURCE}/ptcg_communication_channel_repair_candidate_qa_closure_20260601.json",
        f"{HCTM_20260601_SOURCE}/ptcg_communication_channel_repair_relation_matrix_20260601.json",
    ),
    "checkpoint_rollback_recovery_control": (
        f"{HCTM_20260601_SOURCE}/checkpoint_rollback_recovery_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/checkpoint_rollback_recovery_control_candidate_only_qa_closure_20260602.json",
    ),
    "feedback_channel_integrity_reweighting_control": (
        f"{HCTM_20260601_SOURCE}/feedback_channel_integrity_reweighting_control_l3_ready_preconstruct_card_20260601.json",
        f"{HCTM_20260601_SOURCE}/feedback_channel_integrity_reweighting_control_candidate_only_qa_closure_20260601.json",
    ),
    "instruction_scope_binding_control": (
        f"{HCTM_20260601_SOURCE}/instruction_scope_binding_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/instruction_scope_binding_control_candidate_only_qa_closure_20260602.json",
    ),
    "interface_protocol_negotiation_control": (
        f"{HCTM_20260601_SOURCE}/interface_protocol_negotiation_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/interface_protocol_negotiation_control_candidate_only_qa_closure_20260602.json",
    ),
    "interference_source_separation_control": (
        f"{HCTM_20260601_SOURCE}/interference_source_separation_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/interference_source_separation_control_candidate_only_qa_closure_20260602.json",
    ),
    "irreversible_commitment_safeguard_control": (
        f"{HCTM_20260601_SOURCE}/irreversible_commitment_safeguard_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/irreversible_commitment_safeguard_control_candidate_only_qa_closure_20260602.json",
    ),
    "latent_state_alias_disambiguation_control": (
        f"{HCTM_20260601_SOURCE}/latent_state_alias_disambiguation_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/latent_state_alias_disambiguation_control_candidate_only_qa_closure_20260602.json",
    ),
    "localized_regime_shift_quarantine_control": (
        f"{HCTM_20260601_SOURCE}/localized_regime_shift_quarantine_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/localized_regime_shift_quarantine_control_candidate_only_qa_closure_20260602.json",
    ),
    "memory_index_corruption_rebinding_control": (
        f"{HCTM_20260601_SOURCE}/memory_index_corruption_rebinding_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/memory_index_corruption_rebinding_control_candidate_only_qa_closure_20260602.json",
    ),
    "model_staleness_detection_control": (
        f"{HCTM_20260601_SOURCE}/model_staleness_detection_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/model_staleness_detection_control_candidate_only_qa_closure_20260602.json",
    ),
    "observation_dropout_bridging_control": (
        f"{HCTM_20260601_SOURCE}/observation_dropout_bridging_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/observation_dropout_bridging_control_candidate_only_qa_closure_20260602.json",
    ),
    "option_value_preserving_probe_control": (
        f"{HCTM_20260601_SOURCE}/option_value_preserving_probe_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/option_value_preserving_probe_control_candidate_only_qa_closure_20260602.json",
    ),
    "permission_revocation_compliance_control": (
        f"{HCTM_20260601_SOURCE}/permission_revocation_compliance_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/permission_revocation_compliance_control_candidate_only_qa_closure_20260602.json",
    ),
    "priority_starvation_prevention_control": (
        f"{HCTM_20260601_SOURCE}/priority_starvation_prevention_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/priority_starvation_prevention_control_candidate_only_qa_closure_20260602.json",
    ),
    "provenance_weighted_evidence_integration_control": (
        f"{HCTM_20260601_SOURCE}/provenance_weighted_evidence_integration_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/provenance_weighted_evidence_integration_control_candidate_only_qa_closure_20260602.json",
    ),
    "redundant_pathway_failover_control": (
        f"{HCTM_20260601_SOURCE}/redundant_pathway_failover_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/redundant_pathway_failover_control_candidate_only_qa_closure_20260602.json",
    ),
    "representation_format_translation_control": (
        f"{HCTM_20260601_SOURCE}/representation_format_translation_control_l3_ready_preconstruct_card_20260601.json",
        f"{HCTM_20260601_SOURCE}/representation_format_translation_control_candidate_only_qa_closure_20260601.json",
    ),
    "sensorimotor_latency_compensation_control": (
        f"{HCTM_20260601_SOURCE}/sensorimotor_latency_compensation_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/sensorimotor_latency_compensation_control_candidate_only_qa_closure_20260602.json",
    ),
    "side_effect_containment_control": (
        f"{HCTM_20260601_SOURCE}/side_effect_containment_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/side_effect_containment_control_candidate_only_qa_closure_20260602.json",
    ),
    "unit_frame_normalization_control": (
        f"{HCTM_20260601_SOURCE}/unit_frame_normalization_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/unit_frame_normalization_control_candidate_only_qa_closure_20260602.json",
    ),
    "accountability_obligation_scope_response_control": (
        f"{HCTM_20260601_SOURCE}/accountability_obligation_scope_response_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/accountability_obligation_scope_response_control_candidate_only_qa_closure_20260602.json",
        f"{HCTM_20260601_SOURCE}/accountability_obligation_scope_response_control_independent_probe_family_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/accountability_obligation_scope_response_control_independent_probe_family_result_v1.json",
        f"{HCTM_20260601_SOURCE}/accountability_obligation_scope_response_control_blind_seed_fold_replication_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/accountability_obligation_scope_response_control_blind_seed_fold_replication_result_v1.json",
        f"{HCTM_20260601_SOURCE}/accountability_obligation_scope_response_control_preconstruct_scout_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/accountability_obligation_scope_response_control_preconstruct_scout_result_v1.json",
        f"{HCTM_20260601_SOURCE}/accountability_obligation_scope_response_control_reviewer_challenge_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/accountability_obligation_scope_response_control_reviewer_challenge_result_v1.json",
    ),
    "counter_evidence_preservation_control": (
        f"{HCTM_20260601_SOURCE}/counter_evidence_preservation_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/counter_evidence_preservation_control_candidate_only_qa_closure_20260602.json",
        f"{HCTM_20260601_SOURCE}/counter_evidence_preservation_control_independent_probe_family_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/counter_evidence_preservation_control_independent_probe_family_result_v1.json",
        f"{HCTM_20260601_SOURCE}/counter_evidence_preservation_control_blind_seed_fold_replication_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/counter_evidence_preservation_control_blind_seed_fold_replication_result_v1.json",
        f"{HCTM_20260601_SOURCE}/counter_evidence_preservation_control_preconstruct_scout_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/counter_evidence_preservation_control_preconstruct_scout_result_v1.json",
        f"{HCTM_20260601_SOURCE}/counter_evidence_preservation_control_reviewer_challenge_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/counter_evidence_preservation_control_reviewer_challenge_result_v1.json",
    ),
    "counterparty_intent_uncertainty_resolution_control": (
        f"{HCTM_20260601_SOURCE}/counterparty_intent_uncertainty_resolution_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/counterparty_intent_uncertainty_resolution_control_candidate_only_qa_closure_20260602.json",
        f"{HCTM_20260601_SOURCE}/counterparty_intent_uncertainty_resolution_control_independent_probe_family_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/counterparty_intent_uncertainty_resolution_control_independent_probe_family_result_v1.json",
        f"{HCTM_20260601_SOURCE}/counterparty_intent_uncertainty_resolution_control_blind_seed_fold_replication_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/counterparty_intent_uncertainty_resolution_control_blind_seed_fold_replication_result_v1.json",
        f"{HCTM_20260601_SOURCE}/counterparty_intent_uncertainty_resolution_control_preconstruct_scout_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/counterparty_intent_uncertainty_resolution_control_preconstruct_scout_result_v1.json",
        f"{HCTM_20260601_SOURCE}/counterparty_intent_uncertainty_resolution_control_reviewer_challenge_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/counterparty_intent_uncertainty_resolution_control_reviewer_challenge_result_v1.json",
    ),
    "credential_validity_challenge_response_control": (
        f"{HCTM_20260601_SOURCE}/credential_validity_challenge_response_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/credential_validity_challenge_response_control_candidate_only_qa_closure_20260602.json",
        f"{HCTM_20260601_SOURCE}/credential_validity_challenge_response_control_independent_probe_family_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/credential_validity_challenge_response_control_independent_probe_family_result_v1.json",
        f"{HCTM_20260601_SOURCE}/credential_validity_challenge_response_control_blind_seed_fold_replication_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/credential_validity_challenge_response_control_blind_seed_fold_replication_result_v1.json",
        f"{HCTM_20260601_SOURCE}/credential_validity_challenge_response_control_preconstruct_scout_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/credential_validity_challenge_response_control_preconstruct_scout_result_v1.json",
        f"{HCTM_20260601_SOURCE}/credential_validity_challenge_response_control_reviewer_challenge_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/credential_validity_challenge_response_control_reviewer_challenge_result_v1.json",
    ),
    "deadline_obligation_triage_control": (
        f"{HCTM_20260601_SOURCE}/deadline_obligation_triage_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/deadline_obligation_triage_control_candidate_only_qa_closure_20260602.json",
        f"{HCTM_20260601_SOURCE}/deadline_obligation_triage_control_independent_probe_family_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/deadline_obligation_triage_control_independent_probe_family_result_v1.json",
        f"{HCTM_20260601_SOURCE}/deadline_obligation_triage_control_blind_seed_fold_replication_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/deadline_obligation_triage_control_blind_seed_fold_replication_result_v1.json",
        f"{HCTM_20260601_SOURCE}/deadline_obligation_triage_control_preconstruct_scout_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/deadline_obligation_triage_control_preconstruct_scout_result_v1.json",
        f"{HCTM_20260601_SOURCE}/deadline_obligation_triage_control_reviewer_challenge_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/deadline_obligation_triage_control_reviewer_challenge_result_v1.json",
    ),
    "observation_budget_allocation_control": (
        f"{HCTM_20260601_SOURCE}/observation_budget_allocation_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/observation_budget_allocation_control_candidate_only_qa_closure_20260602.json",
        f"{HCTM_20260601_SOURCE}/observation_budget_allocation_control_independent_probe_family_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/observation_budget_allocation_control_independent_probe_family_result_v1.json",
        f"{HCTM_20260601_SOURCE}/observation_budget_allocation_control_blind_seed_fold_replication_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/observation_budget_allocation_control_blind_seed_fold_replication_result_v1.json",
        f"{HCTM_20260601_SOURCE}/observation_budget_allocation_control_preconstruct_scout_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/observation_budget_allocation_control_preconstruct_scout_result_v1.json",
        f"{HCTM_20260601_SOURCE}/observation_budget_allocation_control_reviewer_challenge_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/observation_budget_allocation_control_reviewer_challenge_result_v1.json",
    ),
    "sample_representativeness_reweighting_control": (
        f"{HCTM_20260601_SOURCE}/sample_representativeness_reweighting_control_l3_ready_preconstruct_card_20260602.json",
        f"{HCTM_20260601_SOURCE}/sample_representativeness_reweighting_control_candidate_only_qa_closure_20260602.json",
        f"{HCTM_20260601_SOURCE}/sample_representativeness_reweighting_control_independent_probe_family_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/sample_representativeness_reweighting_control_independent_probe_family_result_v1.json",
        f"{HCTM_20260601_SOURCE}/sample_representativeness_reweighting_control_blind_seed_fold_replication_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/sample_representativeness_reweighting_control_blind_seed_fold_replication_result_v1.json",
        f"{HCTM_20260601_SOURCE}/sample_representativeness_reweighting_control_preconstruct_scout_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/sample_representativeness_reweighting_control_preconstruct_scout_result_v1.json",
        f"{HCTM_20260601_SOURCE}/sample_representativeness_reweighting_control_reviewer_challenge_spec_v1.json",
        f"{HCTM_20260601_SOURCE}/sample_representativeness_reweighting_control_reviewer_challenge_result_v1.json",
    ),
}


def _roles_for(node_id: str, base_roles: tuple[str, ...]) -> tuple[str, ...]:
    roles = list(base_roles)
    if node_id in FORMAL_CANDIDATE_REVIEW_IDS:
        roles.append("formal_candidate_review_decision")
    if node_id in PENDING_LOCAL_REGISTRATION_IDS:
        roles.append("pending_local_registration")
    if node_id in PTCG_REGISTRY_ROUTE_IDS:
        roles.append("ptcg_registry")
    if node_id in PTCG_PRECONSTRUCT_FRONTIER_IDS:
        roles.append("preconstruct_frontier")
    if node_id in PACKET_READY_IDS:
        roles.append("packet_ready_candidate_only")
    if node_id in SEVERE_BOUNDARY_WATCH_IDS:
        roles.append("severe_boundary_watch")
    if node_id in BATCH5_REWORK_IDS:
        roles.append("batch5_governed_rework")
    if node_id in L3_READY_CARDED_CANDIDATE_IDS:
        roles.append("l3_ready_carded_candidate")

    if node_id in RELATION_MATRIX_REQUIRED_IDS:
        roles.append("relation_matrix_required")

    if node_id in RELATION_MATRIX_COMPLETE_IDS:
        roles.append("relation_matrix_governance_complete")

    return tuple(dict.fromkeys(roles))


def _boundaries_for(node_id: str) -> tuple[str, ...]:
    metadata = FRONTIER_METADATA.get(node_id)
    if metadata is None:
        return ()
    return metadata[1]


def _source_assets_for(node_id: str, extra: tuple[str, ...] = ()) -> tuple[str, ...]:
    sources = list(extra)
    if node_id in FORMAL_CANDIDATE_REVIEW_IDS:
        sources.append(f"{HCTM_20260601_SOURCE}/{node_id}_formal_candidate_review_decision_v1.json")
    if node_id in PTCG_REGISTRY_ROUTE_IDS:
        sources.append(REGISTRY_SOURCE)
    if node_id in PTCG_PRECONSTRUCT_FRONTIER_IDS:
        sources.append(FRONTIER_SOURCE)
    sources.extend(SUPPLEMENTAL_SOURCE_ASSETS.get(node_id, ()))
    return tuple(dict.fromkeys(sources))


def all_construct_architecture() -> ConstructArchitecture:
    """Return the unified all-construct architecture.

    Counts are intentionally stable for the post-HCTM 2026-06-02 snapshot:
    five references, eighty-four candidate or validation-candidate routes
    including thirty-one pending local-registration routes, no active preconstructs,
    three failure-bank routes, and one audit route.
    """

    nodes: list[ConstructNode] = []

    for node_id, family, status, note in REFERENCE_ROWS:
        nodes.append(
            ConstructNode(
                id=node_id,
                layer="reference",
                mechanism_family=family,
                evidence_state="validated",
                status=status,
                next_gate="closed reference set; no automatic expansion",
                roles=("public_benchmark_reference",),
                source_assets=("consciousness_benchmark/constructs/reference.py",),
                forbidden_claims=REFERENCE_FORBIDDEN_CLAIMS,
                notes=note,
            )
        )

    for node_id, family, status, next_gate in VALIDATION_CANDIDATE_ROWS:
        nodes.append(
            ConstructNode(
                id=node_id,
                layer="validation_candidate",
                mechanism_family=family,
                evidence_state="accepted_under_narrowed_claim",
                status=status,
                next_gate=next_gate,
                roles=_roles_for(node_id, ("validation_candidate_queue",)),
                nearest_boundaries=_boundaries_for(node_id),
                source_assets=_source_assets_for(node_id),
            )
        )

    for node_id, family, status, next_gate in CANDIDATE_ROWS:
        nodes.append(
            ConstructNode(
                id=node_id,
                layer="candidate",
                mechanism_family=family,
                evidence_state="candidate_only",
                status=status,
                next_gate=next_gate,
                roles=_roles_for(node_id, ("candidate_registry",)),
                nearest_boundaries=_boundaries_for(node_id),
                source_assets=_source_assets_for(node_id),
            )
        )

    for node_id, family, status, next_gate in PRECONSTRUCT_ROWS:
        nodes.append(
            ConstructNode(
                id=node_id,
                layer="preconstruct",
                mechanism_family=family,
                evidence_state="preconstruct_only_formal_candidate_review_pending",
                status=status,
                next_gate=next_gate,
                roles=_roles_for(node_id, ("active_preconstruct",)),
                nearest_boundaries=_boundaries_for(node_id),
                source_assets=_source_assets_for(node_id),
            )
        )

    for node_id, family, status, next_gate in FAILURE_BANK_ROWS:
        nodes.append(
            ConstructNode(
                id=node_id,
                layer="failure_bank",
                mechanism_family=family,
                evidence_state="failed_or_frozen",
                status=status,
                next_gate=next_gate,
                roles=_roles_for(node_id, ("negative_control", "boundary_debt")),
                source_assets=_source_assets_for(node_id),
            )
        )

    nodes.append(
        ConstructNode(
            id="reference_construct_phase_audit",
            layer="audit_route",
            mechanism_family="reference_motif",
            evidence_state="frozen_design",
            status="reference phase audit route, not a construct",
            next_gate="keep as reference-motif audit",
            roles=_roles_for("reference_construct_phase_audit", ("reference_motif_audit",)),
            source_assets=_source_assets_for("reference_construct_phase_audit"),
            forbidden_claims=COMMON_FORBIDDEN_CLAIMS,
            notes="Included so the PTCG registry is structurally complete.",
        )
    )

    return ConstructArchitecture(tuple(nodes))

# BEGIN A25_GUARDED_SOURCE_PATCH_APPLICATION_LEDGER
# A25 guarded source patch application ledger
# Runtime-generated marker block. Safe to keep as comments.
# - 20260601_full | attention_control | attention_control_source_control_guarded_patch_application_accept_20260601_attention_control_guarded_patch_application | attention_control_source_control_guarded_patch_application_accept_20260601
# - 20260601_full | information_integration_phase | information_integration_phase_source_control_guarded_patch_application_accept_20260601_information_integration_phase_guarded_patch_application | information_integration_phase_source_control_guarded_patch_application_accept_20260601
# - 20260601_full | macro_causal_viability_maintenance | macro_causal_viability_source_control_guarded_patch_application_accept_20260601_macro_causal_viability_maintenance_guarded_patch_application | macro_causal_viability_source_control_guarded_patch_application_accept_20260601
# - 20260601_full | temporal_horizon_dependent_planning | temporal_horizon_dependent_planning_source_control_guarded_patch_application_accept_20260601_temporal_horizon_dependent_planning_guarded_patch_application | temporal_horizon_dependent_planning_source_control_guarded_patch_application_accept_20260601
# - 20260601_full | uncertainty_threshold_metacognition | uncertainty_threshold_metacognition_source_control_guarded_patch_application_accept_20260601_uncertainty_threshold_metacognition_guarded_patch_application | uncertainty_threshold_metacognition_source_control_guarded_patch_application_accept_20260601
# END A25_GUARDED_SOURCE_PATCH_APPLICATION_LEDGER
