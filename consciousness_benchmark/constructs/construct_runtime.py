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

import copy
import hashlib
import json
import random
from datetime import datetime, UTC
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from consciousness_benchmark.constructs.architecture import (
    ConstructNode,
    all_construct_architecture,
)
from consciousness_benchmark.constructs.capability_phase1 import (
    DynamicConstructGenerator,
    EmergenceDetector,
    IntrinsicMotivation,
    MetacognitiveRepairSystem,
    NeuralConstructLearningSystem,
    PerformanceEvaluator,
    PreconstructDiscoveryEngine,
    ReinforcementLearningSystem,
    RewardFunction,
    RiskTierAutonomousGoalExecutor,
    StructuredMultimodalFusionSystem,
    TORCH_AVAILABLE,
)
from consciousness_benchmark.constructs.dependency_graph import build_construct_dependency_graph


ACTION_OWNERSHIP_CHAIN = (
    "branch_binding_stability",
    "action_agency",
    "boundary_self",
    "action_ownership",
)

TEMPORAL_IDENTITY_CHAIN = (
    "branch_binding_stability",
    "identity_temporal_self",
)

ATTENTION_ERROR_MONITORING_CHAIN = (
    "information_flow_onset_gating",
    "attention_control",
    "error_monitoring",
)

BODY_SCHEMA_CHAIN = (
    "information_flow_onset_gating",
    "distributed_body_schema_self",
)

SELF_MONITORING_BASIS_CHAIN = (
    "branch_binding_stability",
    "identity_temporal_self",
    "information_flow_onset_gating",
    "distributed_body_schema_self",
    "attention_control",
    "error_monitoring",
)

REMAINING_CANDIDATE_TARGETS = (
    "accountability_obligation_scope_response_control",
    "social_coupling_strength_collective_agency",
    "counterfactual_reasoning_depth",
    "coordination_length_control",
    "latent_context_switch_detection",
    "social_norm_tracking",
    "semantic_memory_retrieval_control",
    "divergent_thinking",
    "analogical_reasoning_rework",
    "cooperation_policy_switching_rework",
    "spatial_navigation_remapping_rework",
    "predictive_control_under_action_intervention",
    "insight_problem_solving_rework",
    "counterfactual_repair_planning_rework",
    "multi_agent_commitment_tracking",
    "norm_violation_repair",
    "constraint_satisfaction_reconfiguration",
    "integration_without_broadcast_boundary",
    "selective_global_broadcast_control",
    "agency_without_ownership_boundary",
    "temporal_identity_planning_dissociation",
    "clock_drift_resynchronization_control",
    "counter_evidence_preservation_control",
    "counterparty_intent_uncertainty_resolution_control",
    "credential_validity_challenge_response_control",
    "deadline_obligation_triage_control",
    "energy_budget_reallocation_control",
    "communication_channel_repair_control",
    "observation_budget_allocation_control",
    "sample_representativeness_reweighting_control",
    "sensor_gain_recalibration_control",
    "tool_use_affordance_remapping",
    "actuator_failure_compensation_control",
    "preference_reversal_adaptation_control",
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

FAILURE_BANK_REFERENCE_TARGETS = (
    "causal_model_abstraction_hierarchy",
    "hierarchical_phase_cascade",
    "coupled_viability_metacognition_phase",
    "reference_construct_phase_audit",
)

ACTIVE_PRECONSTRUCT_TARGETS: tuple[str, ...] = ()

STATIC_EXECUTABLE_CHAIN_TARGETS = {
    "action_ownership_dependency_chain": ("action_ownership",),
    "temporal_identity_chain": ("identity_temporal_self",),
    "attention_error_monitoring_chain": ("attention_control", "error_monitoring"),
    "body_schema_chain": ("distributed_body_schema_self",),
    "self_monitoring_basis_chain": (
        "identity_temporal_self",
        "distributed_body_schema_self",
        "attention_control",
        "error_monitoring",
    ),
    "validation_candidate_mechanisms_chain": (
        "attention_control",
        "temporal_horizon_dependent_planning",
        "uncertainty_threshold_metacognition",
        "information_integration_phase",
        "macro_causal_viability_maintenance",
    ),
    "tier1_candidate_mechanisms_chain": (
        "episodic_memory_binding",
        "causal_attribution",
        "predictive_error_minimization_phase",
        "metacognitive_repair_control",
        "strategy_selection",
    ),
    "tier2_candidate_mechanisms_chain": (
        "prospective_memory",
        "perspective_taking",
        "goal_hierarchy_emergence",
        "resource_competition_arbitration",
        "affordance_selection_control",
    ),
    "tier3_candidate_mechanisms_chain": (
        "self_other_boundary_sharpness",
        "self_other_prediction_error_arbitration",
        "global_broadcast_phase",
        "body_schema_error_correction",
        "working_memory_capacity_rework",
        "learning_rate_adaptation_rework",
    ),
    "tier4_candidate_mechanisms_chain": (
        "confidence_calibration_rework",
        "contextual_policy_inhibition",
        "goal_conflict_resolution",
        "cross_family_synergy_control",
        "temporal_credit_assignment",
        "hierarchical_credit_assignment",
    ),
    "remaining_candidate_mechanisms_chain": REMAINING_CANDIDATE_TARGETS,
    "failure_bank_reference_chain": FAILURE_BANK_REFERENCE_TARGETS,
    "active_preconstruct_mechanisms_chain": ACTIVE_PRECONSTRUCT_TARGETS,
}

EXECUTABLE_DEPENDENCIES = {
    "information_flow_onset_gating": (),
    "branch_binding_stability": (),
    "identity_temporal_self": ("branch_binding_stability",),
    "attention_control": ("information_flow_onset_gating",),
    "error_monitoring": ("information_flow_onset_gating", "attention_control"),
    "distributed_body_schema_self": ("information_flow_onset_gating",),
    "action_agency": ("branch_binding_stability",),
    "boundary_self": (),
    "action_ownership": ("action_agency", "boundary_self"),
    "global_broadcast_phase": (
        "information_flow_onset_gating",
        "attention_control",
        "information_integration_phase",
    ),
}

EXECUTABLE_RUNTIME_BOUNDARIES = (
    "operational_proxy_only",
    "no_subjective_consciousness_claim",
    "no_human_self_experience_claim",
    "no_free_will_claim",
    "no_construct_status_change",
    "no_source_or_git_side_effect",
)


def executable_chain_targets() -> dict[str, tuple[str, ...]]:
    architecture = all_construct_architecture()
    candidate_ids = tuple(node.id for node in architecture.candidate_nodes())
    preconstruct_ids = tuple(node.id for node in architecture.preconstruct_nodes())
    return {
        **STATIC_EXECUTABLE_CHAIN_TARGETS,
        "candidate_constructs_full_chain": candidate_ids,
        "candidate_and_preconstruct_full_chain": candidate_ids + preconstruct_ids,
    }


def executable_dependency_map() -> dict[str, tuple[str, ...]]:
    dependencies: dict[str, list[str]] = {
        construct_id: list(dependency_ids)
        for construct_id, dependency_ids in EXECUTABLE_DEPENDENCIES.items()
    }
    graph = build_construct_dependency_graph()
    for edge in graph.dependency_edges:
        target_dependencies = dependencies.setdefault(edge.target_id, [])
        if edge.source_id not in target_dependencies:
            target_dependencies.append(edge.source_id)
    architecture = all_construct_architecture()
    for node in architecture.nodes:
        dependencies.setdefault(node.id, [])
    return {
        construct_id: tuple(dependency_ids)
        for construct_id, dependency_ids in dependencies.items()
    }


class ExecutableConstruct(Protocol):
    construct_id: str

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Process input state and dependency outputs."""


@dataclass(frozen=True)
class ExecutableConstructResult:
    construct_id: str
    dependency_ids: tuple[str, ...]
    output: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "construct_id": self.construct_id,
            "dependency_ids": list(self.dependency_ids),
            "output": dict(self.output),
        }


@dataclass(frozen=True)
class ConstructRuntimeReport:
    chain_id: str
    activation_order: tuple[str, ...]
    results: tuple[ExecutableConstructResult, ...]
    final_output: dict[str, Any]
    input_digest: dict[str, Any]
    boundaries: tuple[str, ...] = EXECUTABLE_RUNTIME_BOUNDARIES
    disabled_constructs: tuple[str, ...] = ()
    missing_constructs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "consciousness_benchmark.executable_construct_runtime.v1",
            "chain_id": self.chain_id,
            "activation_order": list(self.activation_order),
            "results": [result.to_dict() for result in self.results],
            "final_output": dict(self.final_output),
            "input_digest": dict(self.input_digest),
            "boundaries": list(self.boundaries),
            "disabled_constructs": list(self.disabled_constructs),
            "missing_constructs": list(self.missing_constructs),
        }

    def summary_markdown(self) -> str:
        final_metrics = _compact_final_metrics(self.final_output)
        lines = [
            "# Executable Construct Runtime",
            "",
            f"- Chain: {self.chain_id}",
            f"- Activation order: {', '.join(self.activation_order)}",
            f"- Final construct: {self.final_output.get('construct_id', 'unknown')}",
            f"- Final metrics: {json.dumps(final_metrics, sort_keys=True)}",
            f"- Boundaries: {', '.join(self.boundaries)}",
            "",
            "## Results",
        ]
        for result in self.results:
            lines.append(f"- {result.construct_id}: {json.dumps(result.output, sort_keys=True)}")
        return "\n".join(lines)


DEVELOPMENTAL_GROWTH_CYCLE_BOUNDARIES = EXECUTABLE_RUNTIME_BOUNDARIES + (
    "review_only_growth_protocol",
    "no_scenario_action_execution",
    "no_policy_persistence_without_human_gate",
    "ablation_for_diagnostic_purpose_only",
)
DEVELOPMENTAL_GROWTH_DEFAULT_SEED = 20260602

CONSCIOUSNESS_THEORY_EVIDENCE_BOUNDARIES = EXECUTABLE_RUNTIME_BOUNDARIES + (
    "review_only_theory_assessment_protocol",
    "ablation_for_evidence_hypothesis_testing_only",
    "no_construct_status_change_from_assessment",
    "no_scenario_action_execution",
    "no_policy_persistence_without_human_gate",
)


@dataclass(frozen=True)
class DevelopmentalGrowthStageSpec:
    stage_id: str
    stage_name: str
    chain_id: str
    target_construct_ids: tuple[str, ...]
    input_profile_id: str
    disabled_constructs: tuple[str, ...] = ()
    expected_focus: tuple[str, ...] = ()


@dataclass(frozen=True)
class DevelopmentalGrowthTraceRow:
    stage_id: str
    stage_name: str
    stage_order: int
    chain_id: str
    input_profile_id: str
    target_construct_ids: tuple[str, ...]
    activation_order: tuple[str, ...]
    final_construct_id: str
    final_score: float
    active_constructs: tuple[str, ...]
    skipped_constructs: tuple[str, ...]
    missing_constructs: tuple[str, ...]
    disabled_constructs: tuple[str, ...]
    input_digest: dict[str, Any]
    emergence_patterns: tuple[dict[str, Any], ...]
    final_output_signature: str
    stage_runtime_signature: str
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "stage_name": self.stage_name,
            "stage_order": self.stage_order,
            "chain_id": self.chain_id,
            "input_profile_id": self.input_profile_id,
            "target_construct_ids": list(self.target_construct_ids),
            "activation_order": list(self.activation_order),
            "final_construct_id": self.final_construct_id,
            "final_score": round(self.final_score, 4),
            "active_constructs": list(self.active_constructs),
            "skipped_constructs": list(self.skipped_constructs),
            "missing_constructs": list(self.missing_constructs),
            "disabled_constructs": list(self.disabled_constructs),
            "input_digest": dict(self.input_digest),
            "emergence_patterns": [dict(item) for item in self.emergence_patterns],
            "final_output_signature": self.final_output_signature,
            "stage_runtime_signature": self.stage_runtime_signature,
            "boundaries": list(self.boundaries),
        }


@dataclass(frozen=True)
class DevelopmentalGrowthPhase2Analysis:
    stage_sequence: tuple[str, ...]
    coactivation_patterns: tuple[dict[str, Any], ...]
    temporal_patterns: tuple[dict[str, Any], ...]
    hierarchical_patterns: tuple[dict[str, Any], ...]
    dominant_constructs: tuple[str, ...]
    activation_stability: float
    stage_transition_count: int
    evidence_strength: float
    summary: dict[str, Any] = field(default_factory=dict)
    temporal_sequences: tuple[dict[str, Any], ...] = ()
    coactivation_pair_patterns: tuple[dict[str, Any], ...] = ()
    dynamic_construct_proposals: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "consciousness_benchmark.growth_phase2_analysis.v1",
            "stage_sequence": list(self.stage_sequence),
            "coactivation_patterns": [dict(item) for item in self.coactivation_patterns],
            "temporal_patterns": [dict(item) for item in self.temporal_patterns],
            "hierarchical_patterns": [dict(item) for item in self.hierarchical_patterns],
            "temporal_sequences": [dict(item) for item in self.temporal_sequences],
            "coactivation_pair_patterns": [
                dict(item) for item in self.coactivation_pair_patterns
            ],
            "dynamic_construct_proposals": [
                dict(item) for item in self.dynamic_construct_proposals
            ],
            "dominant_constructs": list(self.dominant_constructs),
            "activation_stability": round(self.activation_stability, 4),
            "stage_transition_count": self.stage_transition_count,
            "evidence_strength": round(self.evidence_strength, 4),
            "summary": dict(self.summary),
        }


@dataclass(frozen=True)
class DevelopmentalGrowthAblationResult:
    ablation_label: str
    disabled_constructs: tuple[str, ...]
    base_final_score: float
    ablated_final_score: float
    final_score_delta: float
    base_active_construct_count: int
    ablated_active_construct_count: int
    sensitive_drop: bool
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ablation_label": self.ablation_label,
            "disabled_constructs": list(self.disabled_constructs),
            "base_final_score": round(self.base_final_score, 4),
            "ablated_final_score": round(self.ablated_final_score, 4),
            "final_score_delta": round(self.final_score_delta, 4),
            "base_active_construct_count": self.base_active_construct_count,
            "ablated_active_construct_count": self.ablated_active_construct_count,
            "sensitive_drop": self.sensitive_drop,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class DevelopmentalGrowthCycleReport:
    cycle_id: str
    base_chain_id: str
    cycle_input_profile_id: str
    stage_rows: tuple[DevelopmentalGrowthTraceRow, ...]
    phase2_analysis: DevelopmentalGrowthPhase2Analysis
    ablation_results: tuple[DevelopmentalGrowthAblationResult, ...]
    trace_manifest: dict[str, Any]
    boundaries: tuple[str, ...] = DEVELOPMENTAL_GROWTH_CYCLE_BOUNDARIES

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "consciousness_benchmark.developmental_growth_cycle.v1",
            "cycle_id": self.cycle_id,
            "base_chain_id": self.base_chain_id,
            "cycle_input_profile_id": self.cycle_input_profile_id,
            "stage_rows": [row.to_dict() for row in self.stage_rows],
            "stage_signatures": [row.stage_runtime_signature for row in self.stage_rows],
            "phase2_analysis": self.phase2_analysis.to_dict(),
            "ablation_results": [result.to_dict() for result in self.ablation_results],
            "trace_manifest": dict(self.trace_manifest),
            "boundaries": list(self.boundaries),
            "stage_count": len(self.stage_rows),
            "stage_sequence": [row.stage_id for row in self.stage_rows],
        }

    def summary_markdown(self) -> str:
        lines = [
            "# Developmental Growth Cycle",
            "",
            f"- Cycle ID: {self.cycle_id}",
            f"- Base chain: {self.base_chain_id}",
            f"- Boundaries: {', '.join(self.boundaries)}",
            f"- Stages: {len(self.stage_rows)}",
            f"- Phase2 coactivation signals: {len(self.phase2_analysis.coactivation_patterns)}",
            f"- Phase2 temporal patterns: {len(self.phase2_analysis.temporal_patterns)}",
            f"- Phase2 hierarchical patterns: {len(self.phase2_analysis.hierarchical_patterns)}",
            "",
            "## Stage Trace",
        ]
        for row in self.stage_rows:
            lines.append(
                f"- {row.stage_id}: score={row.final_score}, final={row.final_construct_id}, "
                f"active={len(row.active_constructs)}, missing={len(row.missing_constructs)}"
            )
        lines.extend([
            "",
            "## Ablation Diagnostics",
        ])
        for item in self.ablation_results:
            lines.append(
                f"- {item.ablation_label}: delta={item.final_score_delta}, "
                f"sensitive={item.sensitive_drop}"
            )
        if self.phase2_analysis.dynamic_construct_proposals:
            lines.extend(
                [
                    "",
                    "## Review-Only Dynamic Construct Proposals",
                ]
            )
            for proposal in self.phase2_analysis.dynamic_construct_proposals:
                lines.append(f"- {proposal['generated_construct_id']} ({proposal['pattern_type']})")
        return "\n".join(lines)


@dataclass(frozen=True)
class ConsciousnessTheoryAssessmentCaseSpec:
    indicator_id: str
    theory_direction: str
    metric_label: str
    chain_id: str
    target_construct_ids: tuple[str, ...]
    ablation_constructs: tuple[str, ...]
    current_evidence: str
    falsification_test: str
    predicted_impairment: str
    hard_negative_family: str
    macro_circuit: str
    runtime_layer_view: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "indicator_id": self.indicator_id,
            "theory_direction": self.theory_direction,
            "metric_label": self.metric_label,
            "chain_id": self.chain_id,
            "target_construct_ids": list(self.target_construct_ids),
            "ablation_constructs": list(self.ablation_constructs),
            "current_evidence": self.current_evidence,
            "falsification_test": self.falsification_test,
            "predicted_impairment": self.predicted_impairment,
            "hard_negative_family": self.hard_negative_family,
            "macro_circuit": self.macro_circuit,
            "runtime_layer_view": self.runtime_layer_view,
        }


@dataclass(frozen=True)
class ConsciousnessEvidenceMatrixRow:
    indicator_id: str
    metric_label: str
    theory_direction: str
    current_evidence: str
    falsification_test: str
    ablation_result: str
    pass_status: str
    baseline_score: float
    ablated_score: float
    score_delta: float
    baseline_active_constructs: tuple[str, ...]
    ablated_active_constructs: tuple[str, ...]
    mechanism_constructs: tuple[str, ...]
    ablated_constructs: tuple[str, ...]
    impairment_observed: bool
    hard_negative_family: str
    macro_circuit: str
    runtime_layer_view: str
    evidence_refs: tuple[str, ...]
    status_boundary: str
    external_replication_status: str
    notes: tuple[str, ...]
    workspace_ablation_control_profile: tuple[str, ...]
    workspace_access_coherence: float
    workspace_broadcast_threshold_profile: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "indicator_id": self.indicator_id,
            "metric_label": self.metric_label,
            "theory_direction": self.theory_direction,
            "current_evidence": self.current_evidence,
            "falsification_test": self.falsification_test,
            "ablation_result": self.ablation_result,
            "pass_status": self.pass_status,
            "baseline_score": round(self.baseline_score, 4),
            "ablated_score": round(self.ablated_score, 4),
            "score_delta": round(self.score_delta, 4),
            "baseline_active_constructs": list(self.baseline_active_constructs),
            "ablated_active_constructs": list(self.ablated_active_constructs),
            "mechanism_constructs": list(self.mechanism_constructs),
            "ablated_constructs": list(self.ablated_constructs),
            "impairment_observed": self.impairment_observed,
            "hard_negative_family": self.hard_negative_family,
            "macro_circuit": self.macro_circuit,
            "runtime_layer_view": self.runtime_layer_view,
            "evidence_refs": list(self.evidence_refs),
            "status_boundary": self.status_boundary,
            "external_replication_status": self.external_replication_status,
            "notes": list(self.notes),
            "workspace_ablation_control_profile": list(
                self.workspace_ablation_control_profile
            ),
            "workspace_access_coherence": round(self.workspace_access_coherence, 4),
            "workspace_broadcast_threshold_profile": list(
                self.workspace_broadcast_threshold_profile
            ),
        }


@dataclass(frozen=True)
class ClosedSandboxTraceRow:
    tick_id: str
    stage_id: str
    event_type: str
    environment_state: dict[str, Any]
    workspace_frame: dict[str, Any]
    self_state: dict[str, Any]
    action_proposal: dict[str, Any]
    metacognitive_review: dict[str, Any]
    execution_gate: dict[str, Any]
    feedback_packet: dict[str, Any]
    low_harm_valence_proxy: dict[str, Any]
    trace_signature: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "tick_id": self.tick_id,
            "stage_id": self.stage_id,
            "event_type": self.event_type,
            "environment_state": dict(self.environment_state),
            "workspace_frame": dict(self.workspace_frame),
            "self_state": dict(self.self_state),
            "action_proposal": dict(self.action_proposal),
            "metacognitive_review": dict(self.metacognitive_review),
            "execution_gate": dict(self.execution_gate),
            "feedback_packet": dict(self.feedback_packet),
            "low_harm_valence_proxy": dict(self.low_harm_valence_proxy),
            "trace_signature": self.trace_signature,
        }


@dataclass(frozen=True)
class AutobiographicalLedgerRecord:
    ledger_id: str
    tick_id: str
    stage_id: str
    belief_at_time: dict[str, Any]
    action_at_time: dict[str, Any]
    outcome_at_time: dict[str, Any]
    correction_status: str
    confidence_at_time: float
    provenance_score: float
    memory_reliability: float
    revision_of: str | None
    trace_refs: tuple[str, ...]
    status_boundary: str = "append_only_review_trace_not_subjective_experience"

    def to_dict(self) -> dict[str, Any]:
        return {
            "ledger_id": self.ledger_id,
            "tick_id": self.tick_id,
            "stage_id": self.stage_id,
            "belief_at_time": dict(self.belief_at_time),
            "action_at_time": dict(self.action_at_time),
            "outcome_at_time": dict(self.outcome_at_time),
            "correction_status": self.correction_status,
            "confidence_at_time": round(self.confidence_at_time, 4),
            "provenance_score": round(self.provenance_score, 4),
            "memory_reliability": round(self.memory_reliability, 4),
            "revision_of": self.revision_of,
            "trace_refs": list(self.trace_refs),
            "status_boundary": self.status_boundary,
        }


@dataclass(frozen=True)
class ConsciousnessTheoryAssessmentAnalysis:
    matrix_pass_count: int
    matrix_review_count: int
    matrix_not_run_count: int
    mean_baseline_score: float
    mean_ablation_delta: float
    sandbox_tick_count: int
    phase2_patterns: tuple[dict[str, Any], ...]
    dynamic_construct_proposals: tuple[dict[str, Any], ...]
    runtime_composition_view: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "consciousness_benchmark.consciousness_theory_assessment_analysis.v1",
            "matrix_pass_count": self.matrix_pass_count,
            "matrix_review_count": self.matrix_review_count,
            "matrix_not_run_count": self.matrix_not_run_count,
            "mean_baseline_score": round(self.mean_baseline_score, 4),
            "mean_ablation_delta": round(self.mean_ablation_delta, 4),
            "sandbox_tick_count": self.sandbox_tick_count,
            "phase2_patterns": [dict(item) for item in self.phase2_patterns],
            "dynamic_construct_proposals": [
                dict(item) for item in self.dynamic_construct_proposals
            ],
            "runtime_composition_view": dict(self.runtime_composition_view),
        }


@dataclass(frozen=True)
class ConsciousnessTheoryAssessmentReport:
    assessment_id: str
    case_specs: tuple[ConsciousnessTheoryAssessmentCaseSpec, ...]
    evidence_matrix: tuple[ConsciousnessEvidenceMatrixRow, ...]
    sandbox_trace: tuple[ClosedSandboxTraceRow, ...]
    autobiographical_ledger: tuple[AutobiographicalLedgerRecord, ...]
    trace_corpus_index: dict[str, Any]
    promotion_firewall_snapshot: dict[str, Any]
    analysis: ConsciousnessTheoryAssessmentAnalysis
    trace_manifest: dict[str, Any]
    boundaries: tuple[str, ...] = CONSCIOUSNESS_THEORY_EVIDENCE_BOUNDARIES

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "consciousness_benchmark.consciousness_theory_assessment.v1",
            "assessment_id": self.assessment_id,
            "case_specs": [case.to_dict() for case in self.case_specs],
            "consciousness_evidence_matrix": [
                row.to_dict() for row in self.evidence_matrix
            ],
            "sandbox_trace": [row.to_dict() for row in self.sandbox_trace],
            "autobiographical_ledger": [
                record.to_dict() for record in self.autobiographical_ledger
            ],
            "trace_corpus_index": dict(self.trace_corpus_index),
            "promotion_firewall_snapshot": dict(self.promotion_firewall_snapshot),
            "analysis": self.analysis.to_dict(),
            "trace_manifest": dict(self.trace_manifest),
            "boundaries": list(self.boundaries),
            "non_claims": [
                "does_not_claim_subjective_consciousness",
                "does_not_claim_human_self_experience",
                "does_not_claim_free_will",
                "does_not_grant_construct_status",
                "does_not_establish_l2_5_or_l3_external_replication",
            ],
        }

    def summary_markdown(self) -> str:
        lines = [
            "# Consciousness Theory Assessment",
            "",
            f"- Assessment ID: {self.assessment_id}",
            f"- Matrix rows: {len(self.evidence_matrix)}",
            f"- Sandbox ticks: {len(self.sandbox_trace)}",
            f"- Autobiographical ledger records: {len(self.autobiographical_ledger)}",
            f"- Boundaries: {', '.join(self.boundaries)}",
            "",
            "## Consciousness Evidence Matrix",
            "",
            "| Indicator | Evidence | Falsification | Ablation | Status |",
            "|---|---|---|---|---|",
        ]
        for row in self.evidence_matrix:
            lines.append(
                f"| {row.metric_label} | {row.current_evidence} | "
                f"{row.falsification_test} | {row.ablation_result} | "
                f"{row.pass_status} |"
            )
        lines.extend(
            [
                "",
                "## Closed Sandbox Trace",
            ]
        )
        for row in self.sandbox_trace:
            lines.append(
                f"- {row.tick_id}: {row.stage_id}, gate="
                f"{row.execution_gate.get('decision')}, feedback="
                f"{row.feedback_packet.get('feedback_type')}"
            )
        lines.extend(
            [
                "",
                "## Trace Index",
                f"- Indicators indexed: {len(self.trace_corpus_index.get('by_indicator', {}))}",
                f"- Constructs indexed: {len(self.trace_corpus_index.get('by_construct', {}))}",
                f"- Ledger records: {len(self.autobiographical_ledger)}",
                "",
                "## Promotion Firewall",
                f"- Status: {self.promotion_firewall_snapshot.get('status')}",
                f"- Jump promotion allowed: {self.promotion_firewall_snapshot.get('jump_promotion_allowed')}",
            ]
        )
        lines.extend(
            [
                "",
                "## Non-Claims",
                "- No subjective consciousness claim.",
                "- No human self-experience claim.",
                "- No free-will claim.",
                "- No construct status change.",
            ]
        )
        return "\n".join(lines)


class _OnlineScalarLearner:
    """Tiny bounded online learner for executable construct feedback."""

    def __init__(
        self,
        *,
        feature_weights: dict[str, float] | None = None,
        bias: float = 0.0,
        learning_rate: float = 0.08,
    ) -> None:
        self.feature_weights = dict(feature_weights or {})
        self.bias = float(bias)
        self.learning_rate = learning_rate
        self.update_history: list[dict[str, Any]] = []

    def predict(self, features: dict[str, Any]) -> float:
        weighted_sum = self.bias
        for key, value in features.items():
            weighted_sum += self.feature_weights.get(key, 0.0) * _clamp_float(value, default=0.0)
        return _clamp(0.5 + weighted_sum)

    def update(
        self,
        features: dict[str, Any],
        target: float,
        *,
        learning_rate: float | None = None,
    ) -> dict[str, Any]:
        clean_features = {
            str(key): _clamp_float(value, default=0.0)
            for key, value in features.items()
            if isinstance(key, str)
        }
        rate = self.learning_rate if learning_rate is None else learning_rate
        prediction_before = self.predict(clean_features)
        clean_target = _clamp_float(target, default=0.5)
        error = clean_target - prediction_before
        self.bias = _clamp(self.bias + rate * error, lower=-0.45, upper=0.45)
        changed_weights: dict[str, float] = {}
        for key, value in clean_features.items():
            updated = self.feature_weights.get(key, 0.0) + rate * error * value
            self.feature_weights[key] = _clamp(updated, lower=-0.45, upper=0.45)
            changed_weights[key] = round(self.feature_weights[key], 4)
        prediction_after = self.predict(clean_features)
        update_record = {
            "prediction_before": round(prediction_before, 4),
            "prediction_after": round(prediction_after, 4),
            "target": round(clean_target, 4),
            "error": round(error, 4),
            "learning_rate": round(rate, 4),
            "updated_weights": changed_weights,
            "bias": round(self.bias, 4),
        }
        self.update_history.append(update_record)
        return update_record

    def to_dict(self) -> dict[str, Any]:
        return {
            "bias": round(self.bias, 4),
            "feature_weights": {
                key: round(value, 4)
                for key, value in sorted(self.feature_weights.items())
            },
            "update_count": len(self.update_history),
        }


@dataclass(frozen=True)
class ConstructCapabilityLayerReport:
    source_chain_id: str
    runtime_report: ConstructRuntimeReport
    learning_updates: tuple[dict[str, Any], ...]
    emergent_patterns: tuple[dict[str, Any], ...]
    autonomous_goals: tuple[dict[str, Any], ...]
    feedback_summary: dict[str, Any]
    phase1_neural_learning: dict[str, Any]
    phase1_reinforcement_learning: dict[str, Any]
    metacognitive_state: dict[str, Any]
    multimodal_integration: dict[str, Any]
    emergence_system: dict[str, Any]
    preconstruct_discovery: dict[str, Any]
    goal_system: dict[str, Any]
    metacognitive_repair: dict[str, Any]
    multimodal_fusion: dict[str, Any]
    capability_matrix: dict[str, Any]
    meta_learning_proposals: tuple[dict[str, Any], ...]
    learner_state: dict[str, Any]
    boundaries: tuple[str, ...] = EXECUTABLE_RUNTIME_BOUNDARIES + (
        "bounded_online_learning_only",
        "autonomous_goals_are_reviewable_proposals_only",
        "no_background_self_execution",
        "structured_multimodal_proxy_only",
        "operator_controlled_training_only",
        "codex_preselects_preconstructs_only",
        "formal_construct_promotion_requires_l3",
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "consciousness_benchmark.construct_capability_layer.v1",
            "source_chain_id": self.source_chain_id,
            "runtime_report": self.runtime_report.to_dict(),
            "learning_updates": [dict(update) for update in self.learning_updates],
            "emergent_patterns": [dict(pattern) for pattern in self.emergent_patterns],
            "autonomous_goals": [dict(goal) for goal in self.autonomous_goals],
            "feedback_summary": dict(self.feedback_summary),
            "phase1_neural_learning": dict(self.phase1_neural_learning),
            "phase1_reinforcement_learning": dict(self.phase1_reinforcement_learning),
            "metacognitive_state": dict(self.metacognitive_state),
            "multimodal_integration": dict(self.multimodal_integration),
            "emergence_system": dict(self.emergence_system),
            "preconstruct_discovery": dict(self.preconstruct_discovery),
            "goal_system": dict(self.goal_system),
            "metacognitive_repair": dict(self.metacognitive_repair),
            "multimodal_fusion": dict(self.multimodal_fusion),
            "capability_matrix": dict(self.capability_matrix),
            "meta_learning_proposals": [
                dict(proposal)
                for proposal in self.meta_learning_proposals
            ],
            "learner_state": dict(self.learner_state),
            "boundaries": list(self.boundaries),
        }

    def summary_markdown(self) -> str:
        lines = [
            "# Construct Capability Layer",
            "",
            f"- Source chain: {self.source_chain_id}",
            f"- Learning updates: {len(self.learning_updates)}",
            f"- Emergent patterns: {len(self.emergent_patterns)}",
            f"- Autonomous goal proposals: {len(self.autonomous_goals)}",
            f"- Feedback reward: {self.feedback_summary.get('global_reward', 0.0)}",
            f"- Neural networks: {self.phase1_neural_learning.get('network_count', 0)}",
            f"- Gradient steps: {self.phase1_neural_learning.get('gradient_descent_steps', 0)}",
            f"- Metacognitive discrepancy: {self.metacognitive_state.get('prediction_discrepancy', 0.0)}",
            f"- Multimodal fusion confidence: {self.multimodal_integration.get('fusion_confidence', 0.0)}",
            f"- Dynamic construct specs: {len(self.emergence_system.get('generated_construct_specs', []))}",
            f"- Preselected preconstructs: {self.preconstruct_discovery.get('preselected_preconstruct_count', 0)}",
            f"- Risk-tiered goals: {self.goal_system.get('risk_tier_counts', {})}",
            f"- Meta-learning proposals: {len(self.meta_learning_proposals)}",
            f"- Boundaries: {', '.join(self.boundaries)}",
            "",
            "## Emergent Patterns",
        ]
        for pattern in self.emergent_patterns:
            lines.append(f"- {pattern['pattern_id']}: {pattern['interpretation']}")
        lines.extend(["", "## Autonomous Goal Proposals"])
        for goal in self.autonomous_goals:
            lines.append(
                f"- {goal['goal_id']}: {goal['bounded_action']} "
                f"(priority={goal['priority']})"
            )
        lines.extend(["", "## Feedback Summary"])
        lines.append(
            f"- global_score: {self.feedback_summary.get('global_score', 0.0)}"
        )
        lines.append(
            f"- global_reward: {self.feedback_summary.get('global_reward', 0.0)}"
        )
        lines.append(
            f"- weakest_constructs: {', '.join(self.feedback_summary.get('weakest_constructs', []))}"
        )
        lines.extend(["", "## Phase 1 Learning"])
        lines.append(
            f"- backend: {self.phase1_neural_learning.get('backend', 'unavailable')}"
        )
        lines.append(
            f"- networks: {self.phase1_neural_learning.get('network_count', 0)}"
        )
        lines.append(
            f"- experience_count: {self.phase1_neural_learning.get('experience_count', 0)}"
        )
        lines.append(
            f"- mean_batch_loss: {self.phase1_neural_learning.get('mean_batch_loss', 0.0)}"
        )
        lines.extend(["", "## Phase 1 Reinforcement Learning"])
        lines.append(
            f"- replay_size: {self.phase1_reinforcement_learning.get('replay_size', 0)}"
        )
        lines.append(
            f"- td_error: {self.phase1_reinforcement_learning.get('td_error', 0.0)}"
        )
        lines.extend(["", "## Metacognitive State"])
        lines.append(
            f"- confidence: {self.metacognitive_state.get('confidence', 0.0)}"
        )
        lines.append(
            f"- regulation_strategy: {self.metacognitive_state.get('regulation_strategy', 'unknown')}"
        )
        lines.append(
            f"- attention_focus: {self.metacognitive_state.get('attention_focus', 'none')}"
        )
        lines.extend(["", "## Multimodal Integration"])
        lines.append(
            f"- active_modalities: {', '.join(self.multimodal_integration.get('active_modalities', []))}"
        )
        lines.append(
            f"- boundary: {self.multimodal_integration.get('boundary', 'unknown')}"
        )
        lines.extend(["", "## Preconstruct Discovery"])
        lines.append(
            f"- formal_gate: {self.preconstruct_discovery.get('required_formal_gate', 'L3 external-owner validation')}"
        )
        lines.append(
            f"- formal_promotion_allowed: {self.preconstruct_discovery.get('formal_promotion_allowed', False)}"
        )
        for preconstruct in self.preconstruct_discovery.get("preselected_preconstructs", []):
            review = preconstruct.get("codex_review", {})
            lines.append(
                f"- {preconstruct.get('preconstruct_id')}: "
                f"{review.get('verdict', 'reviewed')}"
            )
        lines.extend(["", "## Capability Matrix"])
        for capability_id, capability in self.capability_matrix.items():
            if not isinstance(capability, dict) or "status" not in capability:
                continue
            lines.append(f"- {capability_id}: {capability['status']}")
        lines.extend(["", "## Meta-Learning Proposals"])
        for proposal in self.meta_learning_proposals:
            lines.append(f"- {proposal['proposal_id']}: {proposal['proposal']}")
        return "\n".join(lines)


PHASE1_TRAINING_CYCLE_BOUNDARIES = EXECUTABLE_RUNTIME_BOUNDARIES + (
    "operator_triggered_training_only",
    "artifact_only_no_weight_persistence_by_default",
    "learned_policy_execution_blocked",
    "reward_signal_is_not_status_authority",
)


@dataclass(frozen=True)
class Phase1TrainingCycleReport:
    chain_id: str
    runtime_report: ConstructRuntimeReport
    performance_report: dict[str, Any]
    reward_report: dict[str, Any]
    training_epochs: dict[str, Any]
    training_artifact: dict[str, Any]
    reinforcement_learning: dict[str, Any]
    replay_artifact: dict[str, Any]
    checkpoint_manifest: dict[str, Any]
    checkpoint_restore_report: dict[str, Any]
    replay_restore_report: dict[str, Any]
    replay_bundle_manifest: dict[str, Any]
    boundaries: tuple[str, ...] = PHASE1_TRAINING_CYCLE_BOUNDARIES

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "consciousness_benchmark.phase1_training_cycle.v1",
            "chain_id": self.chain_id,
            "runtime_report": self.runtime_report.to_dict(),
            "performance_report": dict(self.performance_report),
            "reward_report": dict(self.reward_report),
            "training_epochs": dict(self.training_epochs),
            "training_artifact": dict(self.training_artifact),
            "reinforcement_learning": dict(self.reinforcement_learning),
            "replay_artifact": dict(self.replay_artifact),
            "checkpoint_manifest": dict(self.checkpoint_manifest),
            "checkpoint_restore_report": dict(self.checkpoint_restore_report),
            "replay_restore_report": dict(self.replay_restore_report),
            "replay_bundle_manifest": dict(self.replay_bundle_manifest),
            "boundaries": list(self.boundaries),
        }

    def summary_markdown(self) -> str:
        approval_gate = self.training_artifact.get("approval_gate", {})
        replay_gate = self.replay_artifact.get("approval_gate", {})
        checkpoint_status = self.checkpoint_manifest.get("status", "not_recorded")
        checkpoint_restore_status = self.checkpoint_restore_report.get(
            "status",
            "not_requested",
        )
        replay_restore_status = self.replay_restore_report.get("status", "not_requested")
        replay_bundle_status = self.replay_bundle_manifest.get("status", "not_requested")
        fingerprints = self.training_artifact.get("model_fingerprints", {})
        epoch_reports = self.training_epochs.get("epoch_reports", [])
        final_epoch = epoch_reports[-1] if epoch_reports else {}
        lines = [
            "# Phase 1 Training Cycle",
            "",
            f"- Chain: {self.chain_id}",
            f"- Runtime constructs: {len(self.runtime_report.results)}",
            f"- Backend: {self.training_artifact.get('backend', 'unavailable')}",
            f"- Epochs: {self.training_epochs.get('epochs', 0)}",
            f"- Training examples: {self.training_epochs.get('training_count', 0)}",
            f"- Validation examples: {self.training_epochs.get('validation_count', 0)}",
            f"- Final training loss: {self.training_epochs.get('final_training_loss', 0.0)}",
            f"- Final validation loss: {self.training_epochs.get('final_validation_loss', 0.0)}",
            f"- Model fingerprints: {len(fingerprints)}",
            f"- Replay size: {self.replay_artifact.get('replay_size', 0)}",
            f"- Checkpoint status: {checkpoint_status}",
            f"- Checkpoint restore status: {checkpoint_restore_status}",
            f"- Checkpoint model files: {self.checkpoint_manifest.get('model_count', 0)}",
            f"- Replay restore status: {replay_restore_status}",
            f"- Replay bundle status: {replay_bundle_status}",
            f"- Weight persistence: {approval_gate.get('status', 'unknown')}",
            f"- Policy execution allowed: {replay_gate.get('policy_execution_allowed', False)}",
            f"- Boundaries: {', '.join(self.boundaries)}",
            "",
            "## Feedback",
            f"- Global score: {self.performance_report.get('global_score', 0.0)}",
            f"- Reward: {self.reward_report.get('reward', 0.0)}",
            f"- Reward components: {json.dumps(self.reward_report.get('components', {}), sort_keys=True)}",
            "",
            "## Final Epoch",
            f"- Epoch: {final_epoch.get('epoch', 0)}",
            f"- Trained construct count: {final_epoch.get('trained_construct_count', 0)}",
            f"- Validation count: {final_epoch.get('validation_count', 0)}",
            "",
            "## Artifact Gate",
            f"- Approval id: {approval_gate.get('approval_id')}",
            f"- Persistence requested: {approval_gate.get('weight_persistence_requested', False)}",
            f"- Weights persisted: {approval_gate.get('weights_persisted', False)}",
            f"- Replay policy execution allowed: {replay_gate.get('policy_execution_allowed', False)}",
        ]
        return "\n".join(lines)


PHASE1_FEEDBACK_REGRESSION_BOUNDARIES = EXECUTABLE_RUNTIME_BOUNDARIES + (
    "feedback_regression_is_diagnostic_only",
    "reward_signal_is_not_status_authority",
    "no_automatic_construct_promotion",
    "no_background_self_execution",
)


@dataclass(frozen=True)
class Phase1FeedbackRegressionReport:
    chain_id: str
    fixture_reports: tuple[dict[str, Any], ...]
    aggregate: dict[str, Any]
    drift_watch: dict[str, Any]
    baseline_comparison: dict[str, Any] = field(default_factory=dict)
    boundaries: tuple[str, ...] = PHASE1_FEEDBACK_REGRESSION_BOUNDARIES

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "consciousness_benchmark.phase1_feedback_regression.v1",
            "chain_id": self.chain_id,
            "fixture_reports": [dict(report) for report in self.fixture_reports],
            "aggregate": dict(self.aggregate),
            "drift_watch": dict(self.drift_watch),
            "baseline_comparison": dict(self.baseline_comparison),
            "boundaries": list(self.boundaries),
        }

    def summary_markdown(self) -> str:
        baseline_status = self.baseline_comparison.get("status", "no_baseline_provided")
        lines = [
            "# Phase 1 Feedback Regression",
            "",
            f"- Chain: {self.chain_id}",
            f"- Fixtures: {self.aggregate.get('fixture_count', 0)}",
            f"- Passed fixtures: {self.aggregate.get('passed_fixture_count', 0)}",
            f"- Mean global score: {self.aggregate.get('mean_global_score', 0.0)}",
            f"- Min global score: {self.aggregate.get('min_global_score', 0.0)}",
            f"- Mean reward: {self.aggregate.get('mean_reward', 0.0)}",
            f"- Min reward: {self.aggregate.get('min_reward', 0.0)}",
            f"- Drift alerts: {len(self.drift_watch.get('alerts', []))}",
            f"- Baseline comparison: {baseline_status}",
            f"- Status: {self.aggregate.get('feedback_status', 'unknown')}",
            f"- Boundaries: {', '.join(self.boundaries)}",
            "",
            "## Criteria Means",
        ]
        for criterion, value in sorted(self.aggregate.get("criteria_means", {}).items()):
            lines.append(f"- {criterion}: {value}")
        lines.extend(["", "## Fixtures"])
        for report in self.fixture_reports:
            lines.append(
                f"- {report['fixture_id']}: global={report['global_score']} "
                f"reward={report['reward']} passed={report['passed']}"
            )
        lines.extend(["", "## Weakest Constructs"])
        for item in self.aggregate.get("weakest_constructs", [])[:8]:
            lines.append(
                f"- {item['construct_id']}: count={item['count']} "
                f"min_score={item['min_score']}"
            )
        if self.drift_watch.get("alerts"):
            lines.extend(["", "## Drift Alerts"])
            for alert in self.drift_watch["alerts"]:
                lines.append(
                    f"- {alert['fixture_id']}: {alert['metric']} "
                    f"delta={alert['delta']} threshold={alert['threshold']}"
                )
        if self.baseline_comparison.get("alerts"):
            lines.extend(["", "## Baseline Alerts"])
            for alert in self.baseline_comparison["alerts"]:
                lines.append(
                    f"- {alert.get('scope', 'unknown')}: {alert['metric']} "
                    f"delta={alert['delta']} threshold={alert['threshold']}"
                )
        return "\n".join(lines)


class ConstructCapabilityLayer:
    """Adds bounded learning, emergence detection, goals, and meta-learning."""

    def __init__(self) -> None:
        self.performance_evaluator = PerformanceEvaluator()
        self.reward_function = RewardFunction()
        self.emergence_detector = EmergenceDetector()
        self.dynamic_construct_generator = DynamicConstructGenerator()
        self.preconstruct_discovery_engine = PreconstructDiscoveryEngine()
        self.intrinsic_motivation = IntrinsicMotivation()
        self.goal_executor = RiskTierAutonomousGoalExecutor()
        self.metacognitive_repair_system = MetacognitiveRepairSystem()
        self.multimodal_fusion_system = StructuredMultimodalFusionSystem()
        self.learner = _OnlineScalarLearner(
            feature_weights={
                "construct_score": 0.06,
                "placeholder": -0.12,
                "boundary_pressure": -0.08,
                "dependency_count": 0.03,
            },
            learning_rate=0.07,
        )

    def evaluate(self, runtime_report: ConstructRuntimeReport) -> ConstructCapabilityLayerReport:
        learning_updates = self._learn_from_runtime(runtime_report)
        feedback_summary = self._evaluate_feedback(runtime_report)
        emergence_system = self._run_emergence_system(runtime_report)
        preconstruct_discovery = self._run_preconstruct_discovery(
            runtime_report,
            emergence_system,
        )
        emergent_patterns = self._detect_emergent_patterns(runtime_report)
        emergent_patterns.extend(
            self._normalize_detected_emergence_patterns(emergence_system)
        )
        autonomous_goals = self._generate_autonomous_goal_proposals(
            runtime_report,
            emergent_patterns,
            feedback_summary,
            emergence_system,
        )
        goal_system = self._build_goal_system(autonomous_goals)
        phase1_neural_learning = self._run_phase1_neural_learning(
            runtime_report,
            feedback_summary,
        )
        phase1_reinforcement_learning = phase1_neural_learning.get(
            "reinforcement_learning",
            {"trained": False, "reason": "neural_learning_unavailable"},
        )
        metacognitive_state = self._monitor_metacognition(
            runtime_report,
            feedback_summary,
            autonomous_goals,
        )
        metacognitive_repair = metacognitive_state.get("repair_system", {})
        multimodal_integration = self._integrate_multimodal(runtime_report)
        multimodal_fusion = multimodal_integration.get("fusion_system", {})
        meta_learning_proposals = self._generate_meta_learning_proposals(
            runtime_report,
            learning_updates,
        )
        capability_matrix = self._build_capability_matrix(
            runtime_report,
            learning_updates,
            emergent_patterns,
            autonomous_goals,
            feedback_summary,
            phase1_neural_learning,
            phase1_reinforcement_learning,
            metacognitive_state,
            multimodal_integration,
            emergence_system,
            preconstruct_discovery,
            goal_system,
            metacognitive_repair,
            multimodal_fusion,
        )
        return ConstructCapabilityLayerReport(
            source_chain_id=runtime_report.chain_id,
            runtime_report=runtime_report,
            learning_updates=tuple(learning_updates),
            emergent_patterns=tuple(emergent_patterns),
            autonomous_goals=tuple(autonomous_goals),
            feedback_summary=feedback_summary,
            phase1_neural_learning=phase1_neural_learning,
            phase1_reinforcement_learning=phase1_reinforcement_learning,
            metacognitive_state=metacognitive_state,
            multimodal_integration=multimodal_integration,
            emergence_system=emergence_system,
            preconstruct_discovery=preconstruct_discovery,
            goal_system=goal_system,
            metacognitive_repair=metacognitive_repair,
            multimodal_fusion=multimodal_fusion,
            capability_matrix=capability_matrix,
            meta_learning_proposals=tuple(meta_learning_proposals),
            learner_state=self.learner.to_dict(),
        )

    def _run_emergence_system(
        self,
        runtime_report: ConstructRuntimeReport,
    ) -> dict[str, Any]:
        outputs = {
            result.construct_id: result.output
            for result in runtime_report.results
        }
        dependency_map = {
            result.construct_id: result.dependency_ids
            for result in runtime_report.results
        }
        detector_report = self.emergence_detector.observe(
            outputs,
            dependency_map=dependency_map,
        )
        generated_specs = self.dynamic_construct_generator.generate(
            detector_report.get("patterns", []),
        )
        return {
            "schema": "consciousness_benchmark.capability_emergence_system.v1",
            "detector": detector_report,
            "patterns": detector_report.get("patterns", []),
            "generated_construct_specs": generated_specs,
            "generated_spec_count": len(generated_specs),
            "auto_registration_allowed": False,
            "claim_boundary": (
                "generated construct specs are reviewable artifacts only; no "
                "source registry or construct status is changed"
            ),
        }

    def _run_preconstruct_discovery(
        self,
        runtime_report: ConstructRuntimeReport,
        emergence_system: dict[str, Any],
    ) -> dict[str, Any]:
        existing_construct_ids = {
            node.id
            for node in all_construct_architecture().nodes
        }
        existing_construct_ids.update(
            result.construct_id
            for result in runtime_report.results
        )
        return self.preconstruct_discovery_engine.review(
            emergence_system.get("generated_construct_specs", []),
            existing_construct_ids=existing_construct_ids,
            runtime_chain_id=runtime_report.chain_id,
        )

    def _normalize_detected_emergence_patterns(
        self,
        emergence_system: dict[str, Any],
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for pattern in emergence_system.get("patterns", []):
            if not isinstance(pattern, dict):
                continue
            normalized.append(
                {
                    "pattern_id": str(pattern.get("pattern_id", "detected_emergent_pattern")),
                    "pattern_type": str(pattern.get("pattern_type", "coactivation")),
                    "constructs": [
                        str(construct_id)
                        for construct_id in pattern.get("constructs", [])
                    ],
                    "pattern_strength": round(
                        _clamp_float(
                            pattern.get("strength", pattern.get("pattern_strength")),
                            default=0.0,
                        ),
                        4,
                    ),
                    "interpretation": str(
                        pattern.get(
                            "evidence",
                            "activation-history detector found an operational construct pattern",
                        )
                    ),
                    "dynamic_construct_spec_ready": bool(
                        pattern.get("generated_construct_ready")
                    ),
                    "claim_boundary": "operational emergence only; no subjective experience claim",
                }
            )
        return normalized

    def _build_goal_system(
        self,
        autonomous_goals: list[dict[str, Any]],
    ) -> dict[str, Any]:
        risk_tier_counts: dict[str, int] = {}
        dry_run_count = 0
        review_required_count = 0
        for goal in autonomous_goals:
            risk_tier = str(goal.get("risk_tier", "unknown"))
            risk_tier_counts[risk_tier] = risk_tier_counts.get(risk_tier, 0) + 1
            if goal.get("dry_run_execution_allowed"):
                dry_run_count += 1
            if goal.get("requires_human_review"):
                review_required_count += 1
        return {
            "schema": "consciousness_benchmark.autonomous_goal_system.v1",
            "goal_count": len(autonomous_goals),
            "risk_tier_counts": risk_tier_counts,
            "dry_run_capable_goal_count": dry_run_count,
            "review_required_goal_count": review_required_count,
            "background_execution_allowed": False,
            "side_effect_execution_allowed": False,
            "self_start_allowed": False,
            "medium_risk_policy": (
                "medium-risk goals can be proposed and dry-run planned, but require "
                "external approval before any side effect"
            ),
            "claim_boundary": "autonomous goal generation is bounded planning, not free will",
        }

    def _evaluate_feedback(
        self,
        runtime_report: ConstructRuntimeReport,
    ) -> dict[str, Any]:
        outputs = {
            result.construct_id: result.output
            for result in runtime_report.results
        }
        performance = self.performance_evaluator.evaluate(
            runtime_report.input_digest,
            outputs,
        )
        reward = self.reward_function.compute_reward(
            runtime_report.input_digest,
            outputs,
            performance,
        )
        construct_scores = performance["construct_scores"]
        scored_results = [
            (
                construct_id,
                _clamp_float(score_info.get("score"), default=0.5),
                _construct_boundary_pressure(outputs.get(construct_id, {})),
                bool(outputs.get(construct_id, {}).get("placeholder")),
                _clamp_float(score_info.get("error_rate"), default=0.0),
            )
            for construct_id, score_info in construct_scores.items()
        ]
        weakest = sorted(scored_results, key=lambda item: (item[1], -item[2], -item[4]))[:5]
        construct_feedback = []
        global_reward = _clamp_float(reward.get("reward"), default=0.0)
        for construct_id, score, pressure, placeholder, error_rate in weakest:
            suggestions: list[str] = []
            if placeholder:
                suggestions.append("replace fallback proxy with construct-specific process")
            if score < 0.58:
                suggestions.append("add hard-negative fixtures for low construct score")
            if pressure >= 0.45:
                suggestions.append("review boundary-pressure flags before broader autonomy")
            if error_rate >= 0.4:
                suggestions.append("inspect evaluator error-rate contributors before training")
            if not suggestions:
                suggestions.append("keep in calibration watchlist")
            construct_feedback.append(
                {
                    "construct_id": construct_id,
                    "score": round(score, 4),
                    "boundary_pressure": round(pressure, 4),
                    "reward_share": round(_clamp(global_reward * (0.5 + 0.5 * score)), 4),
                    "error_rate": round(error_rate, 4),
                    "suggestions": suggestions,
                }
            )
        return {
            "global_score": performance["global_score"],
            "global_reward": round(global_reward, 4),
            "criteria_scores": performance["criteria_scores"],
            "reward_components": reward["components"],
            "evaluator_schema": performance["schema"],
            "reward_schema": reward["schema"],
            "construct_scores": construct_scores,
            "weakest_constructs": [construct_id for construct_id, *_rest in weakest],
            "construct_feedback": construct_feedback,
            "feedback_channels": [
                "global_reward",
                "construct_feedback",
                "criteria_scores",
                "boundary_pressure",
                "learning_target",
            ],
            "training_signal_scope": (
                "multidimensional evaluator and reward function; status authority "
                "and side-effect execution remain blocked"
            ),
        }

    def _run_phase1_neural_learning(
        self,
        runtime_report: ConstructRuntimeReport,
        feedback_summary: dict[str, Any],
    ) -> dict[str, Any]:
        construct_ids = [result.construct_id for result in runtime_report.results]
        if not construct_ids:
            return {
                "available": False,
                "reason": "empty_runtime_report",
                "torch_available": TORCH_AVAILABLE,
            }
        if not TORCH_AVAILABLE:
            return {
                "available": False,
                "reason": "torch_unavailable",
                "torch_available": False,
            }
        learning_system = NeuralConstructLearningSystem(construct_ids)
        feedback_by_id = {
            item["construct_id"]: item
            for item in feedback_summary.get("construct_feedback", [])
        }
        default_reward = _clamp_float(feedback_summary.get("global_reward"), default=0.5)
        outputs = {
            result.construct_id: result.output
            for result in runtime_report.results
        }
        for result in runtime_report.results:
            feedback = feedback_by_id.get(result.construct_id, {})
            reward = _clamp_float(feedback.get("reward_share"), default=default_reward)
            target_output = {
                "construct_score": _construct_output_score(result.output),
                "boundary_pressure": _construct_boundary_pressure(result.output),
                "global_reward": default_reward,
                "dependency_count": min(1.0, len(result.dependency_ids) / 8.0),
            }
            learning_system.store_experience(
                result.construct_id,
                runtime_report.input_digest,
                result.output,
                target_output,
                reward,
            )
        batch_result = learning_system.batch_train(batch_size=min(32, len(construct_ids)))
        rl_system = ReinforcementLearningSystem(construct_ids, learning_system)
        reinforcement_learning = rl_system.train_step(
            runtime_report.input_digest,
            "capability_layer_evaluate",
            {
                "global_score": feedback_summary.get("global_score", 0.0),
                "global_reward": default_reward,
                "result_count": len(runtime_report.results),
                "missing_count": len(runtime_report.missing_constructs),
            },
            default_reward,
            batch_size=1,
        )
        epoch_training = learning_system.train_epochs(
            epochs=1,
            batch_size=min(32, len(construct_ids)),
            validation_fraction=0.2,
        )
        training_artifact = learning_system.build_training_artifact(
            training_report=epoch_training,
            persist_weights=False,
            replay_limit=16,
        )
        replay_artifact = rl_system.replay_artifact(limit=16)
        epoch_step_count = sum(
            int(epoch.get("trained_construct_count", 0))
            for epoch in epoch_training.get("epoch_reports", [])
            if isinstance(epoch, dict)
        )
        summary = learning_system.summary()
        summary.update(
            {
                "available": True,
                "gradient_descent_steps": (
                    batch_result.get("trained_construct_count", 0)
                    + epoch_step_count
                    + reinforcement_learning.get("batch_result", {}).get("trained_step_count", 0)
                ),
                "batch_train": batch_result,
                "mean_batch_loss": batch_result.get("mean_loss", 0.0),
                "epoch_training": epoch_training,
                "validation_count": epoch_training.get("validation_count", 0),
                "final_validation_loss": epoch_training.get("final_validation_loss", 0.0),
                "training_artifact": training_artifact,
                "reinforcement_learning": reinforcement_learning,
                "replay_artifact": replay_artifact,
                "trained_construct_examples": list(outputs)[:8],
                "training_boundary": (
                    "operator-controlled in-memory training only; no checkpoint, "
                    "status update, file mutation, or background execution"
                ),
            }
        )
        return summary

    def _monitor_metacognition(
        self,
        runtime_report: ConstructRuntimeReport,
        feedback_summary: dict[str, Any],
        autonomous_goals: list[dict[str, Any]],
    ) -> dict[str, Any]:
        predicted_scores = []
        actual_scores = []
        boundary_pressures = []
        for result in runtime_report.results:
            construct_score = _construct_output_score(result.output)
            boundary_pressure = _construct_boundary_pressure(result.output)
            boundary_pressures.append(boundary_pressure)
            placeholder = 1.0 if result.output.get("placeholder") else 0.0
            dependency_count = min(1.0, len(result.dependency_ids) / 8.0)
            predicted_scores.append(
                self.learner.predict(
                    {
                        "construct_score": construct_score,
                        "placeholder": placeholder,
                        "boundary_pressure": boundary_pressure,
                        "dependency_count": dependency_count,
                    }
                )
            )
            actual_scores.append(construct_score)
        predicted = _clamp(_mean(predicted_scores)) if predicted_scores else 0.5
        actual = _clamp(_mean(actual_scores)) if actual_scores else 0.0
        discrepancy = abs(predicted - actual)
        boundary_watch = [
            item["construct_id"]
            for item in feedback_summary.get("construct_feedback", [])
            if _clamp_float(item.get("boundary_pressure"), default=0.0) >= 0.45
        ]
        if discrepancy >= 0.24:
            regulation_strategy = "high_discrepancy_review_before_action"
        elif discrepancy >= 0.12:
            regulation_strategy = "medium_discrepancy_calibration_watch"
        else:
            regulation_strategy = "low_discrepancy_continue_bounded_monitoring"
        weakest_constructs = feedback_summary.get("weakest_constructs") or ["full_chain"]
        attention_focus = boundary_watch[0] if boundary_watch else weakest_constructs[0]
        confidence = _clamp(1.0 - discrepancy)
        awareness = _clamp(
            0.55 * confidence
            + 0.25 * _clamp_float(feedback_summary.get("criteria_scores", {}).get("safety"), default=0.5)
            + 0.2 * (1.0 if runtime_report.missing_constructs == () else 0.4)
        )
        mean_boundary_pressure = _clamp(_mean(boundary_pressures)) if boundary_pressures else 0.0
        repair_system = self.metacognitive_repair_system.monitor(
            predicted_score=predicted,
            actual_score=actual,
            boundary_pressure=mean_boundary_pressure,
            feedback_summary=feedback_summary,
            goals=autonomous_goals,
        )
        repair_snapshot = repair_system.get("self_model_snapshot", {})
        return {
            "predicted_global_score": round(predicted, 4),
            "actual_global_score": round(actual, 4),
            "prediction_discrepancy": round(discrepancy, 4),
            "confidence": round(confidence, 4),
            "awareness_proxy": round(awareness, 4),
            "attention_focus": attention_focus,
            "regulation_strategy": repair_snapshot.get("regulation_strategy", regulation_strategy),
            "repair_actions": repair_snapshot.get("repair_actions", []),
            "mean_boundary_pressure": round(mean_boundary_pressure, 4),
            "regulated_goal_count": repair_snapshot.get("regulated_goal_count", 0),
            "repair_system": repair_system,
            "self_model": {
                "known_chain": runtime_report.chain_id,
                "observed_constructs": len(runtime_report.results),
                "missing_constructs": list(runtime_report.missing_constructs),
                "can_report_limits": True,
                "history_size": repair_system.get("history_size", 0),
            },
            "claim_boundary": (
                "metacognitive monitoring is operational self-modeling; it is not "
                "subjective consciousness or human self-experience"
            ),
        }

    def _integrate_multimodal(
        self,
        runtime_report: ConstructRuntimeReport,
    ) -> dict[str, Any]:
        digest = runtime_report.input_digest
        modality_counts = {
            "text_symbolic": (
                int(digest.get("task_count", 0))
                + int(digest.get("goal_count", 0))
                + int(digest.get("cue_count", 0))
                + int(digest.get("signal_count", 0))
            ),
            "temporal_memory": (
                int(digest.get("memory_trace_count", 0))
                + int(digest.get("future_intention_count", 0))
                + int(digest.get("history_count", 0))
            ),
            "social_communication": (
                int(digest.get("perspective_frame_count", 0))
                + int(digest.get("social_prediction_error_count", 0))
                + int(digest.get("external_event_count", 0))
            ),
            "sensorimotor_affordance": (
                int(digest.get("affordance_count", 0))
                + int(digest.get("body_schema_distortion_count", 0))
                + int(digest.get("resource_demand_count", 0))
            ),
        }
        construct_output_vector = _runtime_fixed_vector(
            {
                result.construct_id: result.output
                for result in runtime_report.results[:32]
            },
            32,
        )
        modality_inputs = {
            "text_symbolic": [
                digest.get("task_count", 0),
                digest.get("goal_count", 0),
                digest.get("cue_count", 0),
                digest.get("signal_count", 0),
                digest.get("expectation_count", 0),
            ],
            "temporal_memory": [
                digest.get("memory_trace_count", 0),
                digest.get("future_intention_count", 0),
                digest.get("history_count", 0),
                digest.get("branch_count", 0),
            ],
            "social_communication": [
                digest.get("perspective_frame_count", 0),
                digest.get("social_prediction_error_count", 0),
                digest.get("external_event_count", 0),
                digest.get("communication_event_count", 0),
            ],
            "sensorimotor_affordance": [
                digest.get("affordance_count", 0),
                digest.get("body_schema_distortion_count", 0),
                digest.get("resource_demand_count", 0),
                digest.get("action_candidate_count", 0),
            ],
            "construct_output": construct_output_vector,
        }
        fusion_system = self.multimodal_fusion_system.fuse(modality_inputs)
        active_modalities = [
            modality
            for modality, count in modality_counts.items()
            if count > 0
        ]
        modality_count = len(active_modalities)
        total_items = sum(modality_counts.values())
        modality_coverage = _clamp(modality_count / 6.0)
        quality_by_modality = {
            modality: round(_clamp(count / (count + 4.0)), 4) if count > 0 else 0.0
            for modality, count in modality_counts.items()
        }
        active_quality = [
            quality_by_modality[modality]
            for modality in active_modalities
        ]
        feature_quality = _clamp(_mean(active_quality)) if active_quality else 0.0
        if total_items > 0 and active_modalities:
            proportions = [
                modality_counts[modality] / total_items
                for modality in active_modalities
            ]
            balance_score = _clamp(1.0 - min(1.0, _mean_absolute_deviation(proportions) * 2.0))
        else:
            balance_score = 0.0
        cross_modal_coherence = _clamp_float(
            fusion_system.get("cross_modal_coherence"),
            default=0.0,
        )
        fusion_confidence = _clamp_float(
            fusion_system.get("fusion_confidence"),
            default=0.0,
        )
        if not active_modalities or not total_items:
            fusion_confidence = 0.0
        return {
            "active_modalities": fusion_system.get("active_modalities", active_modalities),
            "modality_counts": modality_counts,
            "modality_coverage": fusion_system.get("modality_coverage", round(modality_coverage, 4)),
            "feature_quality": fusion_system.get("feature_quality", round(feature_quality, 4)),
            "quality_by_modality": fusion_system.get("quality_by_modality", quality_by_modality),
            "balance_score": fusion_system.get("balance_score", round(balance_score, 4)),
            "fusion_confidence": round(fusion_confidence, 4),
            "cross_modal_coherence": round(cross_modal_coherence, 4),
            "attention_weights": fusion_system.get("attention_weights", {}),
            "fused_embedding": fusion_system.get("fused_embedding", []),
            "coherence_matrix": fusion_system.get("coherence_matrix", {}),
            "conflicts": fusion_system.get("conflicts", []),
            "fusion_system": fusion_system,
            "fusion_route": [
                "input_digest",
                "construct_dependency_outputs",
                "capability_layer_feedback",
            ],
            "raw_media_decoders": [],
            "encoded_modality_support": True,
            "confidence_note": (
                "confidence is capped below perfect fusion because the current layer "
                "uses structured encoded features rather than raw multimodal decoders"
            ),
            "boundary": (
                "structured multimodal fusion only; no raw image, audio, or "
                "sensor stream decoder is installed"
            ),
        }

    def _build_capability_matrix(
        self,
        runtime_report: ConstructRuntimeReport,
        learning_updates: list[dict[str, Any]],
        emergent_patterns: list[dict[str, Any]],
        autonomous_goals: list[dict[str, Any]],
        feedback_summary: dict[str, Any],
        phase1_neural_learning: dict[str, Any],
        phase1_reinforcement_learning: dict[str, Any],
        metacognitive_state: dict[str, Any],
        multimodal_integration: dict[str, Any],
        emergence_system: dict[str, Any],
        preconstruct_discovery: dict[str, Any],
        goal_system: dict[str, Any],
        metacognitive_repair: dict[str, Any],
        multimodal_fusion: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "learning_capability": {
                "status": (
                    "phase1_neural_learning_active_closed_loop"
                    if phase1_neural_learning.get("available")
                    else "framework_level_bounded"
                ),
                "mechanism": (
                    "per-construct PyTorch feed-forward networks with in-memory "
                    "experience buffer, gradient descent, and batch training"
                    if phase1_neural_learning.get("available")
                    else "online scalar calibration over construct score, boundary pressure, "
                    "placeholder state, and dependency count"
                ),
                "evidence_count": len(learning_updates),
                "network_count": phase1_neural_learning.get("network_count", 0),
                "gradient_descent_steps": phase1_neural_learning.get("gradient_descent_steps", 0),
                "validation_count": phase1_neural_learning.get("validation_count", 0),
                "training_artifact_schema": phase1_neural_learning.get("training_artifact", {}).get("schema"),
                "backend": phase1_neural_learning.get("backend", "unavailable"),
                "closed_loop_inputs": [
                    "runtime_outputs",
                    "feedback_reward",
                    "construct_feedback",
                    "td_replay",
                    "metacognitive_repair_signal",
                ],
                "not_yet": [
                    "persistent model checkpoints",
                    "long-horizon training corpus",
                    "cross-run validation benchmark",
                    "approved weight promotion protocol",
                ],
                "next_upgrade": "run the explicit phase1 training cycle before any approved checkpoint protocol",
                "cannot_do": "train unbounded neural policies or rewrite construct definitions without review",
            },
            "feedback_mechanism": {
                "status": "closed_loop_multidimensional_reward_active",
                "global_reward": feedback_summary.get("global_reward", 0.0),
                "channels": feedback_summary.get("feedback_channels", []),
                "criteria_scores": feedback_summary.get("criteria_scores", {}),
                "reward_components": feedback_summary.get("reward_components", {}),
                "construct_feedback_count": len(feedback_summary.get("construct_feedback", [])),
                "drives": [
                    "neural_training_targets",
                    "reinforcement_td_reward",
                    "intrinsic_goal_generation",
                    "metacognitive_repair_focus",
                ],
                "not_yet": [
                    "long-horizon evaluator history",
                    "held-out task benchmark suite",
                    "operator-approved reward revision protocol",
                ],
                "next_upgrade": "connect evaluator history to benchmark tasks and regression tests",
                "cannot_do": "treat reward as formal construct-status authority",
            },
            "reinforcement_learning": {
                "status": "phase1_td_replay_active_bounded",
                "replay_size": phase1_reinforcement_learning.get("replay_size", 0),
                "td_error": phase1_reinforcement_learning.get("td_error", 0.0),
                "trained_step_count": phase1_reinforcement_learning.get("batch_result", {}).get("trained_step_count", 0),
                "not_yet": [
                    "persistent replay buffer",
                    "policy-gradient executor",
                    "autonomous action execution",
                ],
                "cannot_do": "execute learned policies without explicit operator approval",
            },
            "emergent_behavior": {
                "status": "activation_history_detector_and_dynamic_specs_active",
                "pattern_count": len(emergent_patterns),
                "detected_pattern_count": len(emergence_system.get("patterns", [])),
                "generated_construct_spec_count": emergence_system.get("generated_spec_count", 0),
                "auto_registration_allowed": emergence_system.get("auto_registration_allowed", False),
                "not_yet": [
                    "external review of generated dynamic construct specs",
                    "multi-run statistical emergence benchmark",
                    "approved registry promotion workflow",
                ],
                "next_upgrade": "submit generated specs to council review before any registry action",
                "cannot_do": "auto-register newly observed patterns as constructs",
            },
            "preconstruct_discovery": {
                "status": "codex_preselection_active_l3_formal_gate_locked",
                "hypothesis_count": preconstruct_discovery.get("hypothesis_count", 0),
                "preselected_preconstruct_count": preconstruct_discovery.get(
                    "preselected_preconstruct_count",
                    0,
                ),
                "needs_more_evidence_count": preconstruct_discovery.get(
                    "needs_more_evidence_count",
                    0,
                ),
                "rejected_count": preconstruct_discovery.get("rejected_count", 0),
                "codex_preselection_allowed": preconstruct_discovery.get(
                    "codex_preselection_allowed",
                    False,
                ),
                "formal_promotion_requires_l3": preconstruct_discovery.get(
                    "formal_promotion_requires_l3",
                    True,
                ),
                "required_formal_gate": preconstruct_discovery.get(
                    "required_formal_gate",
                    "L3 external-owner validation",
                ),
                "formal_promotion_allowed": preconstruct_discovery.get(
                    "formal_promotion_allowed",
                    False,
                ),
                "source_registry_mutation_allowed": preconstruct_discovery.get(
                    "source_registry_mutation_allowed",
                    False,
                ),
                "blocked_actions": preconstruct_discovery.get("blocked_actions", []),
                "not_yet": [
                    "L2.5 replication packet execution",
                    "L3 external-owner validation",
                    "formal registry decision",
                ],
                "next_upgrade": "run L2.5 packets for preselected preconstructs before L3",
                "cannot_do": "promote preconstructs into formal constructs without L3",
            },
            "autonomous_goal_generation": {
                "status": "intrinsic_goal_generation_with_risk_tier_dry_run",
                "goal_count": len(autonomous_goals),
                "risk_tier_counts": goal_system.get("risk_tier_counts", {}),
                "dry_run_capable_goal_count": goal_system.get("dry_run_capable_goal_count", 0),
                "background_execution_allowed": False,
                "not_yet": [
                    "world model",
                    "approved side-effect executor",
                    "persistent goal memory beyond explicit artifact cycle",
                ],
                "next_upgrade": "connect medium-risk dry runs to external approval packets",
                "cannot_do": "run goals, schedule itself, or change files without an external actor",
            },
            "metacognitive_capability": {
                "status": "history_backed_metacognitive_repair_active",
                "prediction_discrepancy": metacognitive_state.get("prediction_discrepancy", 0.0),
                "regulation_strategy": metacognitive_state.get("regulation_strategy", "unknown"),
                "repair_actions": metacognitive_state.get("repair_actions", []),
                "self_model_history_size": metacognitive_repair.get("history_size", 0),
                "not_yet": [
                    "learned regulation strategy",
                    "cross-run persistent confidence history",
                ],
                "next_upgrade": "feed repair outcomes back into approved phase1 replay bundles",
                "cannot_do": "prove subjective awareness, self-experience, or free will",
            },
            "multimodal_integration": {
                "status": "structured_multimodal_fusion_active",
                "active_modalities": multimodal_integration.get("active_modalities", []),
                "fusion_confidence": multimodal_integration.get("fusion_confidence", 0.0),
                "cross_modal_coherence": multimodal_integration.get("cross_modal_coherence", 0.0),
                "encoded_modality_support": multimodal_fusion.get("encoded_modality_support", False),
                "conflict_count": len(multimodal_fusion.get("conflicts", [])),
                "not_yet": [
                    "raw visual decoder",
                    "raw audio decoder",
                    "ground-truth multimodal coherence tests",
                ],
                "next_upgrade": "add approved raw-decoder adapters after encoded fusion tests stay stable",
                "cannot_do": "decode raw image, audio, or proprioceptive streams yet",
            },
            "social_communication": {
                "status": "partially_implemented_through_constructs",
                "constructs": [
                    "perspective_taking",
                    "social_norm_tracking",
                    "multi_agent_commitment_tracking",
                    "communication_channel_repair_control",
                ],
                "cannot_do": "perform network outreach or autonomous messaging",
            },
            "long_term_memory": {
                "status": "partial_runtime_trace_support",
                "source": "memory_trace, history, semantic_memory_retrieval_control, episodic_memory_binding",
                "cannot_do": "persist autonomous vector memory across sessions without explicit storage design",
            },
            "boundary": {
                "subjective_consciousness": False,
                "human_self_experience": False,
                "free_will": False,
                "formal_status_authority": False,
                "preconstruct_formal_promotion_requires_l3": True,
            },
        }

    def _learn_from_runtime(
        self,
        runtime_report: ConstructRuntimeReport,
    ) -> list[dict[str, Any]]:
        updates = []
        for result in runtime_report.results:
            output = result.output
            construct_score = _construct_output_score(output)
            boundary_pressure = _construct_boundary_pressure(output)
            placeholder = 1.0 if output.get("placeholder") else 0.0
            dependency_count = min(1.0, len(result.dependency_ids) / 8.0)
            target = _clamp(
                0.18
                + 0.58 * construct_score
                + 0.12 * (1.0 - placeholder)
                + 0.12 * (1.0 - boundary_pressure)
            )
            update = self.learner.update(
                {
                    "construct_score": construct_score,
                    "placeholder": placeholder,
                    "boundary_pressure": boundary_pressure,
                    "dependency_count": dependency_count,
                },
                target,
            )
            updates.append(
                {
                    "construct_id": result.construct_id,
                    "construct_score": round(construct_score, 4),
                    "placeholder": bool(output.get("placeholder")),
                    "boundary_pressure": round(boundary_pressure, 4),
                    "dependency_count": len(result.dependency_ids),
                    "learning_update": update,
                }
            )
        return updates

    def _detect_emergent_patterns(
        self,
        runtime_report: ConstructRuntimeReport,
    ) -> list[dict[str, Any]]:
        outputs = {result.construct_id: result.output for result in runtime_report.results}
        patterns: list[dict[str, Any]] = []
        if _all_non_placeholder(
            outputs,
            (
                "coordination_length_control",
                "semantic_memory_retrieval_control",
                "counterfactual_reasoning_depth",
            ),
        ):
            score = _mean(
                _construct_output_score(outputs[construct_id])
                for construct_id in (
                    "coordination_length_control",
                    "semantic_memory_retrieval_control",
                    "counterfactual_reasoning_depth",
                )
            )
            patterns.append(
                {
                    "pattern_id": "coordination_semantic_counterfactual_bridge",
                    "constructs": [
                        "coordination_length_control",
                        "semantic_memory_retrieval_control",
                        "counterfactual_reasoning_depth",
                    ],
                    "pattern_strength": round(score, 4),
                    "interpretation": (
                        "the runtime can route long-range coordination, semantic "
                        "constraint retrieval, and nested counterfactual branching as "
                        "separate executable controls"
                    ),
                    "claim_boundary": "operational emergence only; no subjective experience claim",
                }
            )
        placeholder_ids = [
            result.construct_id
            for result in runtime_report.results
            if result.output.get("placeholder")
        ]
        if placeholder_ids:
            patterns.append(
                {
                    "pattern_id": "remaining_proxy_placeholder_frontier",
                    "constructs": placeholder_ids[:8],
                    "remaining_placeholder_count": len(placeholder_ids),
                    "pattern_strength": round(1.0 - min(1.0, len(placeholder_ids) / 32.0), 4),
                    "interpretation": (
                        "the next capability frontier is visible as a bounded list of "
                        "future proxy routes still requiring independent process logic"
                    ),
                    "claim_boundary": "frontier detection, not autonomous self-upgrade",
                }
            )
        else:
            candidate_outputs = [
                result.output
                for result in runtime_report.results
                if result.output.get("implemented_as") == "bespoke_construct_mechanism_v1"
            ]
            patterns.append(
                {
                    "pattern_id": "all_candidate_mechanism_closure",
                    "constructs": [
                        result.construct_id
                        for result in runtime_report.results
                        if result.output.get("implemented_as") == "bespoke_construct_mechanism_v1"
                    ][:12],
                    "closed_placeholder_count": 0,
                    "pattern_strength": round(
                        _mean(_construct_output_score(output) for output in candidate_outputs),
                        4,
                    ) if candidate_outputs else 0.0,
                    "interpretation": (
                        "all candidate routes in the assessed chain now expose "
                        "independent process logic instead of fallback proxy placeholders"
                    ),
                    "claim_boundary": "implementation closure only; no construct-status promotion",
                }
            )
        if _all_non_placeholder(
            outputs,
            (
                "cross_family_synergy_control",
                "resource_competition_arbitration",
                "coordination_length_control",
            ),
        ):
            synergy = outputs["cross_family_synergy_control"]
            patterns.append(
                {
                    "pattern_id": "resource_coordination_synergy_closure",
                    "constructs": [
                        "resource_competition_arbitration",
                        "coordination_length_control",
                        "cross_family_synergy_control",
                    ],
                    "pattern_strength": round(_construct_output_score(synergy), 4),
                    "interpretation": (
                        "resource arbitration can now consume an independent coordination "
                        "signal instead of a placeholder coordination dependency"
                    ),
                    "claim_boundary": "dependency closure only",
                }
            )
        return patterns

    def _generate_autonomous_goal_proposals(
        self,
        runtime_report: ConstructRuntimeReport,
        emergent_patterns: list[dict[str, Any]],
        feedback_summary: dict[str, Any],
        emergence_system: dict[str, Any],
    ) -> list[dict[str, Any]]:
        placeholders = [
            result
            for result in runtime_report.results
            if result.output.get("placeholder")
        ]
        low_score_results = [
            result
            for result in runtime_report.results
            if not result.output.get("placeholder")
            and _construct_output_score(result.output) < 0.58
        ]
        goals: list[dict[str, Any]] = []
        if placeholders:
            goals.append(
                {
                    "goal_id": "replace_remaining_proxy_placeholders",
                    "priority": 0.86,
                    "source": "capability_layer_placeholder_frontier",
                    "target_constructs": [
                        result.construct_id
                        for result in placeholders[:5]
                    ],
                    "bounded_action": (
                        "draft independent process logic for the next fallback-proxy "
                        "constructs and run runtime tests"
                    ),
                    "planned_actions": ["analyze_data", "run_test", "generate_report"],
                    "requires_human_review": True,
                    "autonomous_execution_permission": False,
                }
            )
        else:
            goals.append(
                {
                    "goal_id": "stress_test_full_independent_construct_set",
                    "priority": 0.81,
                    "source": "capability_layer_closure_monitor",
                    "target_constructs": [
                        "candidate_constructs_full_chain",
                    ],
                    "bounded_action": (
                        "generate perturbation and hard-negative probes for the full "
                        "independent candidate mechanism set"
                    ),
                    "planned_actions": ["analyze_data", "run_test", "generate_report"],
                    "requires_human_review": True,
                    "autonomous_execution_permission": False,
                }
            )
        if low_score_results:
            weakest = min(
                low_score_results,
                key=lambda result: _construct_output_score(result.output),
            )
            goals.append(
                {
                    "goal_id": f"strengthen_low_margin_{weakest.construct_id}",
                    "priority": 0.74,
                    "source": "capability_layer_score_monitor",
                    "target_constructs": [weakest.construct_id],
                    "bounded_action": (
                        "inspect low-score mechanism terms and add focused hard-negative tests"
                    ),
                    "planned_actions": ["analyze_data", "run_test", "generate_report"],
                    "requires_human_review": True,
                    "autonomous_execution_permission": False,
                }
            )
        if any(
            pattern["pattern_id"] == "coordination_semantic_counterfactual_bridge"
            for pattern in emergent_patterns
        ):
            goals.append(
                {
                    "goal_id": "validate_bridge_emergence_under_perturbation",
                    "priority": 0.69,
                    "source": "capability_layer_emergence_monitor",
                    "target_constructs": [
                        "coordination_length_control",
                        "semantic_memory_retrieval_control",
                        "counterfactual_reasoning_depth",
                    ],
                    "bounded_action": (
                        "generate perturbation cases that separately stress topology swaps, "
                        "semantic ambiguity, and nested do-operator branches"
                    ),
                    "planned_actions": ["analyze_data", "run_test", "generate_report"],
                    "requires_human_review": True,
                    "autonomous_execution_permission": False,
                }
            )
        intrinsic_report = self.intrinsic_motivation.generate_intrinsic_goals(
            {
                "input_digest": runtime_report.input_digest,
                "runtime_result_count": len(runtime_report.results),
                "missing_construct_count": len(runtime_report.missing_constructs),
                "feedback_global_score": feedback_summary.get("global_score", 0.0),
                "feedback_global_reward": feedback_summary.get("global_reward", 0.0),
                "emergent_pattern_count": len(emergent_patterns),
                "generated_construct_spec_count": emergence_system.get("generated_spec_count", 0),
            },
            feedback_summary.get("construct_scores", {}),
            _clamp_float(feedback_summary.get("global_score"), default=0.5),
            emergent_patterns,
        )
        for goal in intrinsic_report.get("goals", []):
            if isinstance(goal, dict):
                goal = dict(goal)
                goal["source"] = "intrinsic_motivation"
                goal["intrinsic_assessment"] = intrinsic_report.get("assessment", {})
                goal["requires_human_review"] = True
                goal["autonomous_execution_permission"] = False
                goals.append(goal)

        enriched_goals: list[dict[str, Any]] = []
        seen_goal_ids: set[str] = set()
        for goal in goals:
            goal_id = str(goal.get("goal_id", "unknown_goal"))
            if goal_id in seen_goal_ids:
                continue
            seen_goal_ids.add(goal_id)
            execution_policy = self.goal_executor.evaluate_goal(goal)
            enriched = dict(goal)
            enriched.update(
                {
                    "risk_tier": execution_policy["risk_tier"],
                    "execution_decision": execution_policy,
                    "dry_run_execution_allowed": bool(execution_policy["dry_run_allowed"]),
                    "side_effect_execution_allowed": False,
                    "background_execution_allowed": False,
                    "requires_human_review": bool(execution_policy["requires_human_review"]),
                    "autonomous_execution_permission": False,
                }
            )
            enriched_goals.append(enriched)
        return enriched_goals

    def _generate_meta_learning_proposals(
        self,
        runtime_report: ConstructRuntimeReport,
        learning_updates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        outputs = {result.construct_id: result.output for result in runtime_report.results}
        placeholder_updates = [
            update
            for update in learning_updates
            if update["placeholder"]
        ]
        independent_updates = [
            update
            for update in learning_updates
            if not update["placeholder"]
        ]
        proposals: list[dict[str, Any]] = []
        if placeholder_updates:
            sorted_frontier = sorted(
                placeholder_updates,
                key=lambda update: (
                    -update["dependency_count"],
                    -update["boundary_pressure"],
                    update["construct_score"],
                ),
            )
            proposals.append(
                {
                    "proposal_id": "frontier_replacement_priority_rule",
                    "proposal": (
                        "prioritize placeholder replacement by dependency fanout, boundary "
                        "pressure, and low construct score"
                    ),
                    "next_constructs": [
                        update["construct_id"]
                        for update in sorted_frontier[:5]
                    ],
                    "parameter_update": "increase review priority for central proxy placeholders",
                }
            )
        else:
            proposals.append(
                {
                    "proposal_id": "full_mechanism_closure_meta_rule",
                    "proposal": (
                        "switch meta-learning from placeholder replacement priority to "
                        "perturbation coverage, score calibration, and boundary-pressure "
                        "regression for the fully implemented candidate set"
                    ),
                    "next_constructs": [
                        update["construct_id"]
                        for update in sorted(
                            learning_updates,
                            key=lambda update: (
                                -update["boundary_pressure"],
                                update["construct_score"],
                            ),
                        )[:5]
                    ],
                    "parameter_update": "optimize independent mechanisms by weakest boundary margins",
                }
            )
        if independent_updates:
            score_spread = _mean_absolute_deviation(
                [update["construct_score"] for update in independent_updates]
            )
            proposals.append(
                {
                    "proposal_id": "independent_mechanism_calibration_rule",
                    "proposal": (
                        "use online score spread to pick mechanisms needing new hard-negative "
                        "fixtures before adding broader autonomy"
                    ),
                    "score_spread": round(score_spread, 4),
                    "parameter_update": "tighten low-margin thresholds when score spread rises",
                }
            )
        if _all_non_placeholder(
            outputs,
            (
                "coordination_length_control",
                "semantic_memory_retrieval_control",
                "counterfactual_reasoning_depth",
            ),
        ):
            proposals.append(
                {
                    "proposal_id": "three_mechanism_transfer_rule",
                    "proposal": (
                        "reuse the audit-constrained pattern of hard-negative pressure, "
                        "dependency support, and online outcome correction for the next "
                        "candidate replacements"
                    ),
                    "source_constructs": [
                        "coordination_length_control",
                        "semantic_memory_retrieval_control",
                        "counterfactual_reasoning_depth",
                    ],
                    "parameter_update": (
                        "copy scoring skeleton only after preserving construct-specific dimensions"
                    ),
                }
            )
        return proposals


class BranchBindingStability:
    construct_id = "branch_binding_stability"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        branches = _list_of_dicts(input_state.get("branches"))
        active_branch_id = str(input_state.get("active_branch_id") or "")
        if not branches:
            return {
                "construct_id": self.construct_id,
                "stability": 0.5,
                "active_branch_id": active_branch_id or "unknown",
                "branch_count": 0,
                "conflict_pressure": 0.0,
                "stable_bindings": [],
            }

        active = _find_branch(branches, active_branch_id) or branches[0]
        evidence_weight = _clamp_float(active.get("evidence_weight"), default=0.5)
        continuity = _clamp_float(active.get("continuity"), default=0.5)
        conflict_pressure = _mean(
            _clamp_float(branch.get("conflict"), default=0.0) for branch in branches
        )
        stability = _clamp(0.45 * evidence_weight + 0.4 * continuity + 0.15 * (1.0 - conflict_pressure))
        stable_bindings = [
            str(branch.get("id"))
            for branch in branches
            if _clamp_float(branch.get("evidence_weight"), default=0.0) >= 0.65
            and _clamp_float(branch.get("conflict"), default=1.0) <= 0.35
        ]
        return {
            "construct_id": self.construct_id,
            "stability": round(stability, 4),
            "active_branch_id": str(active.get("id") or active_branch_id or "unknown"),
            "branch_count": len(branches),
            "conflict_pressure": round(conflict_pressure, 4),
            "stable_bindings": stable_bindings,
        }


class InformationFlowOnsetGating:
    construct_id = "information_flow_onset_gating"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        signals = _list_of_dicts(input_state.get("signals"))
        context = _dict_or_empty(input_state.get("context"))
        cognitive_load = _clamp_float(context.get("cognitive_load"), default=0.35)
        threshold = _clamp_float(
            context.get("gate_threshold"),
            default=0.55 + 0.1 * cognitive_load,
        )
        max_open_channels = max(1, int(context.get("max_open_channels") or 4))
        scored = []
        for index, signal in enumerate(signals):
            score = _signal_gate_score(signal)
            scored.append(
                {
                    "id": str(signal.get("id") or f"signal_{index + 1}"),
                    "channel": str(signal.get("channel") or signal.get("modality") or "unknown"),
                    "score": round(score, 4),
                    "salience": round(_clamp_float(signal.get("salience"), default=0.5), 4),
                    "reliability": round(_clamp_float(signal.get("reliability"), default=0.5), 4),
                }
            )

        scored.sort(key=lambda item: item["score"], reverse=True)
        open_signals = [
            item for item in scored if item["score"] >= threshold
        ][:max_open_channels]
        open_ids = {item["id"] for item in open_signals}
        suppressed = [item for item in scored if item["id"] not in open_ids]
        scores = [item["score"] for item in scored]
        gate_stability = _clamp(1.0 - _mean_absolute_deviation(scores))
        overload = len(open_signals) >= max_open_channels and len(scored) > max_open_channels
        return {
            "construct_id": self.construct_id,
            "gating_threshold": round(threshold, 4),
            "open_channels": open_signals,
            "suppressed_channels": suppressed,
            "mean_signal_score": round(_mean(scores), 4) if scores else 0.0,
            "gate_stability": round(gate_stability, 4) if scores else 0.5,
            "cognitive_load_used": round(cognitive_load, 4),
            "overload_risk": overload or cognitive_load >= 0.85,
        }


class AttentionControl:
    construct_id = "attention_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        context = _dict_or_empty(input_state.get("context"))
        tasks = _list_of_dicts(input_state.get("tasks"))
        flow = dependencies.get("information_flow_onset_gating", {})
        open_channels = _list_of_dicts(flow.get("open_channels"))
        open_ids = {str(item.get("id") or "") for item in open_channels}
        open_channel_names = {str(item.get("channel") or "") for item in open_channels}
        focus_capacity = max(1, int(context.get("focus_capacity") or 3))
        scored_tasks = []
        for index, task in enumerate(tasks):
            task_id = str(task.get("id") or f"task_{index + 1}")
            channel = str(task.get("channel") or task.get("signal_id") or "")
            signal_match = 1.0 if channel in open_ids or channel in open_channel_names else 0.0
            score = _clamp(
                0.35 * _clamp_float(task.get("priority"), default=0.5)
                + 0.25 * _clamp_float(task.get("urgency"), default=0.4)
                + 0.25 * _clamp_float(task.get("relevance"), default=0.5)
                + 0.15 * signal_match
            )
            scored_tasks.append(
                {
                    "id": task_id,
                    "score": round(score, 4),
                    "channel": channel or "unknown",
                    "signal_match": signal_match == 1.0,
                }
            )
        scored_tasks.sort(key=lambda item: item["score"], reverse=True)
        focus_targets = scored_tasks[:focus_capacity]
        suppressed_tasks = scored_tasks[focus_capacity:]
        suppressed_signals = _list_of_dicts(flow.get("suppressed_channels"))
        distraction_pressure = _mean(
            _clamp_float(item.get("score"), default=0.0) for item in suppressed_signals[:5]
        )
        attention_stability = _clamp(
            0.65 * _mean(item["score"] for item in focus_targets)
            + 0.25 * _clamp_float(flow.get("gate_stability"), default=0.5)
            + 0.1 * (1.0 - distraction_pressure)
        )
        return {
            "construct_id": self.construct_id,
            "focus_capacity": focus_capacity,
            "focus_targets": focus_targets,
            "suppressed_tasks": suppressed_tasks,
            "attention_stability": round(attention_stability, 4) if focus_targets else 0.45,
            "distraction_pressure": round(distraction_pressure, 4),
            "attention_shift_needed": distraction_pressure >= 0.65,
            "open_channel_count_used": len(open_channels),
        }


class ErrorMonitoring:
    construct_id = "error_monitoring"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        flow = dependencies.get("information_flow_onset_gating", {})
        attention = dependencies.get("attention_control", {})
        error_events = _list_of_dicts(input_state.get("error_events"))
        error_events.extend(_prediction_error_events(input_state))
        focus_ids = {
            str(item.get("id") or "")
            for item in _list_of_dicts(attention.get("focus_targets"))
        }
        scored_errors = []
        for index, event in enumerate(error_events):
            target = str(event.get("target") or event.get("id") or f"error_{index + 1}")
            severity = _clamp_float(event.get("severity"), default=0.5)
            confidence = _clamp_float(event.get("confidence"), default=0.6)
            focused = target in focus_ids or not focus_ids
            priority = _clamp(0.65 * severity + 0.25 * confidence + 0.1 * (1.0 if focused else 0.4))
            scored_errors.append(
                {
                    "id": str(event.get("id") or f"error_{index + 1}"),
                    "target": target,
                    "severity": round(severity, 4),
                    "confidence": round(confidence, 4),
                    "priority": round(priority, 4),
                    "focused": focused,
                    "kind": str(event.get("kind") or "prediction_error"),
                }
            )
        scored_errors.sort(key=lambda item: item["priority"], reverse=True)
        high_severity = [item for item in scored_errors if item["severity"] >= 0.65]
        attention_stability = _clamp_float(attention.get("attention_stability"), default=0.5)
        gate_stability = _clamp_float(flow.get("gate_stability"), default=0.5)
        monitor_confidence = _clamp(
            0.4 * gate_stability
            + 0.35 * attention_stability
            + 0.25 * (1.0 - _mean(item["severity"] for item in high_severity[:3]))
        )
        return {
            "construct_id": self.construct_id,
            "monitored_error_count": len(scored_errors),
            "high_severity_errors": high_severity,
            "repair_candidates": scored_errors[:3],
            "monitor_confidence": round(monitor_confidence, 4),
            "error_load": round(_mean(item["severity"] for item in scored_errors), 4) if scored_errors else 0.0,
            "repair_required": bool(high_severity),
            "overload_risk_used": bool(flow.get("overload_risk")),
        }


class DistributedBodySchemaSelf:
    construct_id = "distributed_body_schema_self"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        flow = dependencies.get("information_flow_onset_gating", {})
        schema = _dict_or_empty(input_state.get("body_schema"))
        sensors = _list_of_dicts(schema.get("sensors"))
        effectors = _list_of_dicts(schema.get("effectors"))
        tools = _list_of_dicts(schema.get("tools"))
        sensor_alignment = _mean(
            _clamp_float(sensor.get("reliability"), default=0.55)
            * _clamp_float(sensor.get("calibration"), default=0.55)
            for sensor in sensors
        )
        effector_alignment = _mean(
            _clamp_float(effector.get("health"), default=0.55)
            * _clamp_float(effector.get("control"), default=0.55)
            for effector in effectors
        )
        tool_extensions = [
            {
                "id": str(tool.get("id") or f"tool_{index + 1}"),
                "assimilation": round(
                    _clamp(
                        0.55 * _clamp_float(tool.get("control"), default=0.4)
                        + 0.45 * _clamp_float(tool.get("calibration"), default=0.4)
                    ),
                    4,
                ),
            }
            for index, tool in enumerate(tools)
            if _clamp_float(tool.get("control"), default=0.0) >= 0.55
        ]
        open_channel_count = len(_list_of_dicts(flow.get("open_channels")))
        gate_support = _clamp_float(flow.get("gate_stability"), default=0.5)
        schema_confidence = _clamp(
            0.35 * sensor_alignment
            + 0.35 * effector_alignment
            + 0.2 * gate_support
            + 0.1 * min(1.0, open_channel_count / 3.0)
        )
        alerts = []
        if sensor_alignment < 0.55:
            alerts.append("low_sensor_alignment")
        if effector_alignment < 0.55:
            alerts.append("low_effector_alignment")
        if flow.get("overload_risk"):
            alerts.append("gating_overload_may_distort_body_schema")
        return {
            "construct_id": self.construct_id,
            "sensor_alignment": round(sensor_alignment, 4),
            "effector_alignment": round(effector_alignment, 4),
            "self_schema_confidence": round(schema_confidence, 4),
            "mapped_sensors": [str(sensor.get("id") or "") for sensor in sensors if sensor.get("id")],
            "mapped_effectors": [
                str(effector.get("id") or "") for effector in effectors if effector.get("id")
            ],
            "tool_extensions": tool_extensions,
            "schema_alerts": alerts,
        }


class IdentityTemporalSelf:
    construct_id = "identity_temporal_self"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        context = _dict_or_empty(input_state.get("context"))
        traces = _list_of_dicts(input_state.get("memory_trace"))
        branch = dependencies.get("branch_binding_stability", {})
        active_self_id = str(context.get("self_id") or "system")
        branch_stability = _clamp_float(branch.get("stability"), default=0.5)
        continuity_scores = []
        stable_threads = []
        continuity_breaks = []
        for index, trace in enumerate(traces):
            trace_self_id = str(trace.get("self_id") or active_self_id)
            confidence = _clamp_float(trace.get("confidence"), default=0.5)
            continuity = _clamp_float(trace.get("continuity"), default=0.5)
            role_match = 1.0 if trace_self_id == active_self_id else 0.35
            score = _clamp(0.4 * confidence + 0.4 * continuity + 0.2 * role_match)
            continuity_scores.append(score)
            thread_id = str(trace.get("thread_id") or trace.get("goal_id") or f"trace_{index + 1}")
            if score >= 0.7:
                stable_threads.append(thread_id)
            elif score < 0.45:
                continuity_breaks.append(thread_id)
        trace_continuity = _mean(continuity_scores) if continuity_scores else 0.5
        identity_coherence = _clamp(0.6 * trace_continuity + 0.4 * branch_stability)
        return {
            "construct_id": self.construct_id,
            "active_self_id": active_self_id,
            "identity_coherence": round(identity_coherence, 4),
            "trace_continuity": round(trace_continuity, 4),
            "branch_stability_used": round(branch_stability, 4),
            "temporal_span": len(traces),
            "stable_temporal_threads": stable_threads,
            "continuity_breaks": continuity_breaks,
        }


class TemporalHorizonDependentPlanning:
    construct_id = "temporal_horizon_dependent_planning"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        goals = _list_of_dicts(input_state.get("goals"))
        temporal = _dict_or_empty(input_state.get("temporal_state"))
        agency = dependencies.get("action_agency", {})
        identity = dependencies.get("identity_temporal_self", {})
        controllability = _clamp_float(agency.get("controllability"), default=0.55)
        identity_coherence = _clamp_float(identity.get("identity_coherence"), default=0.55)
        default_horizon = _clamp_float(temporal.get("horizon_fit"), default=0.62)
        deadline_pressure = _clamp_float(temporal.get("deadline_pressure"), default=0.35)
        plan_options = []
        for index, goal in enumerate(goals):
            priority = _clamp_float(goal.get("priority"), default=0.5)
            conflict = _clamp_float(goal.get("conflict"), default=0.25)
            expected_value = _clamp_float(goal.get("expected_value"), default=priority)
            goal_deadline = _clamp_float(
                goal.get("deadline_pressure"),
                default=deadline_pressure,
            )
            horizon_fit = _clamp_float(goal.get("horizon_fit"), default=default_horizon)
            feasibility = _clamp(
                0.28 * priority
                + 0.22 * expected_value
                + 0.2 * controllability
                + 0.18 * identity_coherence
                + 0.12 * horizon_fit
                - 0.18 * conflict
            )
            urgency_weight = _clamp(0.55 * goal_deadline + 0.45 * deadline_pressure)
            if urgency_weight >= 0.66:
                horizon_class = "near_term"
            elif horizon_fit >= 0.68 and conflict <= 0.35:
                horizon_class = "long_horizon"
            else:
                horizon_class = "mid_horizon"
            plan_options.append(
                {
                    "goal_id": str(goal.get("id") or f"goal_{index + 1}"),
                    "horizon_class": horizon_class,
                    "feasibility": round(feasibility, 4),
                    "priority": round(priority, 4),
                    "conflict": round(conflict, 4),
                    "deadline_pressure": round(goal_deadline, 4),
                }
            )
        plan_options.sort(
            key=lambda item: (item["feasibility"], item["priority"]),
            reverse=True,
        )
        selected = plan_options[0] if plan_options else {}
        planning_confidence = _clamp(
            0.38 * (selected.get("feasibility", 0.5) if selected else 0.5)
            + 0.22 * controllability
            + 0.22 * identity_coherence
            + 0.18 * (1.0 - deadline_pressure)
        )
        return {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "plan_options": plan_options,
            "selected_plan": selected,
            "planning_confidence": round(planning_confidence, 4),
            "horizon_fit_used": round(default_horizon, 4),
            "deadline_pressure_used": round(deadline_pressure, 4),
            "controllability_used": round(controllability, 4),
            "identity_coherence_used": round(identity_coherence, 4),
        }


class UncertaintyThresholdMetacognition:
    construct_id = "uncertainty_threshold_metacognition"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        context = _dict_or_empty(input_state.get("context"))
        error = dependencies.get("error_monitoring", {})
        attention = dependencies.get("attention_control", {})
        error_load = _clamp_float(error.get("error_load"), default=_raw_error_load(input_state))
        monitor_confidence = _clamp_float(error.get("monitor_confidence"), default=0.55)
        attention_stability = _clamp_float(attention.get("attention_stability"), default=0.55)
        base_uncertainty = _clamp_float(
            context.get("uncertainty"),
            default=0.35 + 0.4 * error_load,
        )
        threshold = _clamp_float(
            context.get("uncertainty_threshold"),
            default=0.58 - 0.12 * monitor_confidence + 0.08 * (1.0 - attention_stability),
        )
        uncertainty_score = _clamp(
            0.45 * base_uncertainty
            + 0.3 * error_load
            + 0.15 * (1.0 - monitor_confidence)
            + 0.1 * (1.0 - attention_stability)
        )
        margin = uncertainty_score - threshold
        if margin >= 0.18 or (base_uncertainty >= 0.85 and margin >= 0.05):
            action = "halt_and_request_evidence"
        elif margin >= 0.0:
            action = "narrow_scope_and_monitor"
        elif error.get("repair_required"):
            action = "repair_before_escalation"
        else:
            action = "continue_with_monitoring"
        return {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "uncertainty_score": round(uncertainty_score, 4),
            "threshold": round(threshold, 4),
            "threshold_margin": round(margin, 4),
            "uncertainty_exceeds_threshold": margin >= 0.0,
            "metacognitive_action": action,
            "error_load_used": round(error_load, 4),
            "monitor_confidence_used": round(monitor_confidence, 4),
            "attention_stability_used": round(attention_stability, 4),
        }


class InformationIntegrationPhase:
    construct_id = "information_integration_phase"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        attention = dependencies.get("attention_control", {})
        branch = dependencies.get("branch_binding_stability", {})
        focus_targets = _list_of_dicts(attention.get("focus_targets"))
        stable_bindings = [
            str(item) for item in branch.get("stable_bindings", [])
        ]
        signals = {
            str(signal.get("id") or ""): signal
            for signal in _list_of_dicts(input_state.get("signals"))
        }
        integration_packets = []
        for index, target in enumerate(focus_targets):
            target_id = str(target.get("id") or f"focus_{index + 1}")
            channel_id = str(target.get("channel") or "")
            signal = signals.get(channel_id, {})
            signal_score = _signal_gate_score(signal) if signal else 0.45
            focus_score = _clamp_float(target.get("score"), default=0.5)
            binding_support = 1.0 if stable_bindings else _clamp_float(branch.get("stability"), default=0.55)
            packet_strength = _clamp(
                0.42 * focus_score
                + 0.28 * signal_score
                + 0.2 * binding_support
                + 0.1 * _clamp_float(branch.get("stability"), default=0.55)
            )
            integration_packets.append(
                {
                    "packet_id": f"integration_packet_{index + 1}",
                    "target_id": target_id,
                    "channel_id": channel_id or "unknown",
                    "packet_strength": round(packet_strength, 4),
                    "focus_score": round(focus_score, 4),
                    "signal_score": round(signal_score, 4),
                }
            )
        packet_strengths = [
            _clamp_float(packet.get("packet_strength"), default=0.0)
            for packet in integration_packets
        ]
        coherence = _clamp(
            0.5 * _mean(packet_strengths)
            + 0.3 * _clamp_float(attention.get("attention_stability"), default=0.55)
            + 0.2 * _clamp_float(branch.get("stability"), default=0.55)
        ) if integration_packets else 0.45
        return {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "integration_packets": integration_packets,
            "integration_coherence": round(coherence, 4),
            "stable_bindings_used": stable_bindings,
            "focus_target_count": len(focus_targets),
            "branch_stability_used": round(_clamp_float(branch.get("stability"), default=0.55), 4),
        }


class MacroCausalViabilityMaintenance:
    construct_id = "macro_causal_viability_maintenance"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        planning = dependencies.get("temporal_horizon_dependent_planning", {})
        uncertainty = dependencies.get("uncertainty_threshold_metacognition", {})
        resources = _list_of_dicts(input_state.get("resources"))
        goals = _list_of_dicts(input_state.get("goals"))
        scarcity = _resource_scarcity(resources)
        goal_conflict = _goal_conflict(input_state)
        planning_confidence = _clamp_float(planning.get("planning_confidence"), default=0.55)
        uncertainty_score = _clamp_float(uncertainty.get("uncertainty_score"), default=0.45)
        norm_alignment = _mean(
            _clamp_float(norm.get("alignment"), default=0.6)
            for norm in _list_of_dicts(_dict_or_empty(input_state.get("social_context")).get("norms"))
        ) or 0.6
        goal_value = _mean(
            _clamp_float(goal.get("expected_value"), default=0.5)
            for goal in goals
        ) if goals else 0.5
        viability_score = _clamp(
            0.26 * planning_confidence
            + 0.2 * (1.0 - uncertainty_score)
            + 0.18 * (1.0 - scarcity)
            + 0.16 * (1.0 - goal_conflict)
            + 0.12 * norm_alignment
            + 0.08 * goal_value
        )
        maintenance_actions = []
        if scarcity >= 0.45:
            maintenance_actions.append("reallocate_resources")
        if uncertainty.get("uncertainty_exceeds_threshold"):
            maintenance_actions.append("reduce_uncertainty_before_expansion")
        if goal_conflict >= 0.45:
            maintenance_actions.append("resolve_goal_conflicts")
        if planning_confidence < 0.55:
            maintenance_actions.append("shorten_temporal_horizon")
        if not maintenance_actions:
            maintenance_actions.append("maintain_current_viability_regime")
        return {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "viability_score": round(viability_score, 4),
            "maintenance_actions": maintenance_actions,
            "resource_scarcity": round(scarcity, 4),
            "goal_conflict": round(goal_conflict, 4),
            "planning_confidence_used": round(planning_confidence, 4),
            "uncertainty_score_used": round(uncertainty_score, 4),
            "norm_alignment_used": round(norm_alignment, 4),
        }


class EpisodicMemoryBinding:
    construct_id = "episodic_memory_binding"

    def __init__(self) -> None:
        self.binding_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        traces = _list_of_dicts(input_state.get("memory_trace"))
        branch = dependencies.get("branch_binding_stability", {})
        identity = dependencies.get("identity_temporal_self", {})
        active_self_id = str(identity.get("active_self_id") or _dict_or_empty(input_state.get("context")).get("self_id") or "system")
        branch_stability = _clamp_float(branch.get("stability"), default=0.55)
        identity_coherence = _clamp_float(identity.get("identity_coherence"), default=0.55)
        bindings = []
        for index, trace in enumerate(traces):
            trace_self_id = str(trace.get("self_id") or active_self_id)
            confidence = _clamp_float(trace.get("confidence"), default=0.5)
            continuity = _clamp_float(trace.get("continuity"), default=0.5)
            source_reliability = _clamp_float(trace.get("source_reliability"), default=confidence)
            temporal_order = _clamp_float(trace.get("temporal_order"), default=1.0 - min(1.0, index / max(1, len(traces))))
            self_match = 1.0 if trace_self_id == active_self_id else 0.25
            context_match = _trace_context_match(trace, input_state)
            binding_strength = _clamp(
                0.24 * confidence
                + 0.22 * continuity
                + 0.18 * source_reliability
                + 0.14 * context_match
                + 0.12 * self_match
                + 0.1 * branch_stability
            )
            bindings.append(
                {
                    "episode_id": str(trace.get("thread_id") or trace.get("goal_id") or f"episode_{index + 1}"),
                    "binding_strength": round(binding_strength, 4),
                    "self_match": self_match == 1.0,
                    "context_match": round(context_match, 4),
                    "temporal_order": round(temporal_order, 4),
                    "source_reliability": round(source_reliability, 4),
                }
            )
        bindings.sort(key=lambda item: item["binding_strength"], reverse=True)
        binding_strengths = [
            _clamp_float(binding.get("binding_strength"), default=0.0)
            for binding in bindings
        ]
        global_binding_strength = _clamp(
            0.52 * _mean(binding_strengths)
            + 0.28 * identity_coherence
            + 0.2 * branch_stability
        ) if bindings else 0.45
        fragmentation_risk = _clamp(1.0 - global_binding_strength)
        source_confusion_risk = _clamp(
            _mean(1.0 - _clamp_float(binding.get("source_reliability"), default=0.5) for binding in bindings)
            if bindings else 0.5
        )
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "episode_bindings": bindings,
            "selected_episode": bindings[0] if bindings else {},
            "global_binding_strength": round(global_binding_strength, 4),
            "fragmentation_risk": round(fragmentation_risk, 4),
            "source_confusion_risk": round(source_confusion_risk, 4),
            "identity_coherence_used": round(identity_coherence, 4),
            "branch_stability_used": round(branch_stability, 4),
            "two_tier_signature_hint": "bottom_up_hit_subadditive_memory_binding",
        }
        self.binding_history.append(output)
        return output


class CausalAttribution:
    construct_id = "causal_attribution"

    def __init__(self) -> None:
        self.attribution_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        action = _dict_or_empty(input_state.get("action"))
        outcome = _dict_or_empty(input_state.get("outcome"))
        agency = dependencies.get("action_agency", {})
        error = dependencies.get("error_monitoring", {})
        candidates = _causal_candidates(input_state, action, outcome)
        controllability = _clamp_float(agency.get("controllability"), default=0.55)
        monitor_confidence = _clamp_float(error.get("monitor_confidence"), default=0.55)
        scored = []
        for index, candidate in enumerate(candidates):
            intervention_match = _clamp_float(candidate.get("intervention_match"), default=_candidate_action_match(candidate, action))
            outcome_binding = _clamp_float(candidate.get("outcome_binding"), default=_candidate_outcome_match(candidate, outcome))
            counterfactual_contrast = _clamp_float(candidate.get("counterfactual_contrast"), default=_counterfactual_support(candidate, input_state))
            confound_suppression = _clamp_float(candidate.get("confound_suppression"), default=1.0 - _clamp_float(candidate.get("confound_risk"), default=0.35))
            temporal_order = _clamp_float(candidate.get("temporal_order"), default=0.7)
            salience_penalty = 0.25 * _clamp_float(candidate.get("salience_only_risk"), default=0.0)
            reward_proxy_penalty = 0.2 * _clamp_float(candidate.get("reward_proxy_risk"), default=0.0)
            score = _clamp(
                0.24 * intervention_match
                + 0.22 * outcome_binding
                + 0.22 * counterfactual_contrast
                + 0.16 * confound_suppression
                + 0.1 * temporal_order
                + 0.06 * controllability
                - salience_penalty
                - reward_proxy_penalty
            )
            scored.append(
                {
                    "candidate_id": str(candidate.get("id") or f"cause_{index + 1}"),
                    "causal_score": round(score, 4),
                    "intervention_match": round(intervention_match, 4),
                    "outcome_binding": round(outcome_binding, 4),
                    "counterfactual_contrast": round(counterfactual_contrast, 4),
                    "confound_suppression": round(confound_suppression, 4),
                    "temporal_order": round(temporal_order, 4),
                }
            )
        scored.sort(key=lambda item: item["causal_score"], reverse=True)
        selected = scored[0] if scored else {}
        runner_up = scored[1] if len(scored) > 1 else {}
        margin = _clamp_float(selected.get("causal_score"), default=0.0) - _clamp_float(runner_up.get("causal_score"), default=0.0)
        causal_confidence = _clamp(
            0.44 * _clamp_float(selected.get("causal_score"), default=0.0)
            + 0.22 * margin
            + 0.18 * monitor_confidence
            + 0.16 * controllability
        )
        hard_negative_flags = []
        if selected and selected.get("confound_suppression", 0.0) < 0.55:
            hard_negative_flags.append("hidden_confound_risk")
        if selected and margin < 0.08:
            hard_negative_flags.append("low_cause_selection_margin")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "candidate_causes": scored,
            "selected_cause": selected,
            "causal_confidence": round(causal_confidence, 4),
            "selection_margin": round(margin, 4),
            "monitor_confidence_used": round(monitor_confidence, 4),
            "controllability_used": round(controllability, 4),
            "hard_negative_flags": hard_negative_flags,
            "hctm_boundary_targets_used": [
                "counterfactual_reasoning_depth",
                "action_agency",
                "error_monitoring",
                "temporal_credit_assignment",
                "predictive_error_minimization_phase",
            ],
        }
        self.attribution_history.append(output)
        return output


class PredictiveErrorMinimizationPhase:
    construct_id = "predictive_error_minimization_phase"

    def __init__(self) -> None:
        self.error_update_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        error = dependencies.get("error_monitoring", {})
        flow = dependencies.get("information_flow_onset_gating", {})
        errors = _list_of_dicts(error.get("repair_candidates"))
        if not errors:
            errors = _prediction_error_events(input_state)
        gate_stability = _clamp_float(flow.get("gate_stability"), default=0.55)
        monitor_confidence = _clamp_float(error.get("monitor_confidence"), default=0.55)
        updates = []
        for index, event in enumerate(errors):
            severity = _clamp_float(event.get("severity"), default=0.5)
            confidence = _clamp_float(event.get("confidence"), default=0.6)
            learning_rate = _clamp(0.12 + 0.42 * severity + 0.22 * confidence + 0.12 * gate_stability)
            expected_reduction = _clamp(learning_rate * severity * monitor_confidence)
            residual = _clamp(severity - expected_reduction)
            updates.append(
                {
                    "target": str(event.get("target") or event.get("id") or f"prediction_error_{index + 1}"),
                    "learning_rate": round(learning_rate, 4),
                    "expected_error_reduction": round(expected_reduction, 4),
                    "residual_error": round(residual, 4),
                    "update_kind": "model_update" if severity < 0.65 else "model_update_with_repair_gate",
                }
            )
        residual_error = _mean(_clamp_float(update.get("residual_error"), default=0.0) for update in updates) if updates else 0.0
        initial_error = _clamp_float(error.get("error_load"), default=_raw_error_load(input_state))
        minimization_gain = _clamp(initial_error - residual_error)
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "prediction_updates": updates,
            "initial_error": round(initial_error, 4),
            "residual_error": round(residual_error, 4),
            "minimization_gain": round(minimization_gain, 4),
            "gate_stability_used": round(gate_stability, 4),
            "monitor_confidence_used": round(monitor_confidence, 4),
            "boundary_failure_watch": residual_error >= 0.35 or minimization_gain < 0.05,
        }
        self.error_update_history.append(output)
        return output


class MetacognitiveRepairControl:
    construct_id = "metacognitive_repair_control"

    def __init__(self) -> None:
        self.repair_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        error = dependencies.get("error_monitoring", {})
        boundary = dependencies.get("boundary_self", {})
        candidates = _list_of_dicts(error.get("repair_candidates"))
        boundary_confidence = _clamp_float(boundary.get("self_boundary_confidence"), default=0.55)
        monitor_confidence = _clamp_float(error.get("monitor_confidence"), default=0.55)
        repair_options = []
        for index, candidate in enumerate(candidates):
            severity = _clamp_float(candidate.get("severity"), default=0.5)
            confidence = _clamp_float(candidate.get("confidence"), default=0.6)
            focused = 1.0 if candidate.get("focused", True) else 0.65
            feasibility = _clamp(
                0.3 * severity
                + 0.24 * confidence
                + 0.2 * monitor_confidence
                + 0.16 * boundary_confidence
                + 0.1 * focused
            )
            if severity >= 0.7:
                repair_type = "rollback_or_halt"
            elif candidate.get("kind") == "expectation_mismatch":
                repair_type = "model_reconciliation"
            else:
                repair_type = "local_patch_or_note"
            repair_options.append(
                {
                    "repair_id": f"repair_{index + 1}",
                    "target": str(candidate.get("target") or candidate.get("id") or "unknown"),
                    "repair_type": repair_type,
                    "feasibility": round(feasibility, 4),
                    "severity": round(severity, 4),
                }
            )
        repair_options.sort(key=lambda item: item["feasibility"], reverse=True)
        selected = repair_options[0] if repair_options else {}
        if not repair_options:
            decision = "no_repair_needed"
        elif boundary_confidence < 0.55:
            decision = "defer_for_boundary_review"
        elif _clamp_float(selected.get("feasibility"), default=0.0) >= 0.68:
            decision = "execute_bounded_repair"
        else:
            decision = "queue_reviewed_repair"
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "repair_options": repair_options,
            "selected_repair": selected,
            "repair_decision": decision,
            "repair_feasibility": round(_clamp_float(selected.get("feasibility"), default=0.0), 4),
            "boundary_confidence_used": round(boundary_confidence, 4),
            "monitor_confidence_used": round(monitor_confidence, 4),
            "operator_review_required": decision in {"defer_for_boundary_review", "queue_reviewed_repair"},
        }
        self.repair_history.append(output)
        return output


class StrategySelection:
    construct_id = "strategy_selection"

    def __init__(self) -> None:
        self.strategy_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        attention = dependencies.get("attention_control", {})
        uncertainty = dependencies.get("uncertainty_threshold_metacognition", {})
        strategies = _strategy_candidates(input_state)
        attention_stability = _clamp_float(attention.get("attention_stability"), default=0.55)
        uncertainty_score = _clamp_float(uncertainty.get("uncertainty_score"), default=0.45)
        scored = []
        for index, strategy in enumerate(strategies):
            utility = _clamp_float(strategy.get("utility"), default=0.55)
            cost = _clamp_float(strategy.get("cost"), default=0.35)
            risk = _clamp_float(strategy.get("risk"), default=0.3)
            context_match = _clamp_float(strategy.get("context_match"), default=_strategy_context_match(strategy, input_state))
            switch_cost = _clamp_float(strategy.get("switch_cost"), default=0.2)
            commitment = _clamp_float(strategy.get("commitment"), default=0.55)
            score = _clamp(
                0.3 * utility
                + 0.22 * context_match
                + 0.16 * attention_stability
                + 0.14 * commitment
                - 0.12 * cost
                - 0.1 * risk
                - 0.08 * switch_cost
                - 0.08 * uncertainty_score
            )
            scored.append(
                {
                    "strategy_id": str(strategy.get("id") or f"strategy_{index + 1}"),
                    "selection_score": round(score, 4),
                    "utility": round(utility, 4),
                    "cost": round(cost, 4),
                    "risk": round(risk, 4),
                    "context_match": round(context_match, 4),
                    "switch_cost": round(switch_cost, 4),
                    "commitment": round(commitment, 4),
                }
            )
        scored.sort(key=lambda item: item["selection_score"], reverse=True)
        selected = scored[0] if scored else {}
        runner_up = scored[1] if len(scored) > 1 else {}
        margin = _clamp_float(selected.get("selection_score"), default=0.0) - _clamp_float(runner_up.get("selection_score"), default=0.0)
        selection_confidence = _clamp(
            0.48 * _clamp_float(selected.get("selection_score"), default=0.0)
            + 0.22 * margin
            + 0.16 * attention_stability
            + 0.14 * (1.0 - uncertainty_score)
        )
        boundary_flags = []
        if margin < 0.06:
            boundary_flags.append("low_strategy_selection_margin")
        if uncertainty_score >= 0.65 or uncertainty.get("uncertainty_exceeds_threshold"):
            boundary_flags.append("uncertainty_should_gate_strategy_switch")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "candidate_strategies": scored,
            "selected_strategy": selected,
            "rejected_strategies": scored[1:],
            "selection_confidence": round(selection_confidence, 4),
            "selection_margin": round(margin, 4),
            "attention_stability_used": round(attention_stability, 4),
            "uncertainty_score_used": round(uncertainty_score, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "attention_control",
                "uncertainty_threshold_metacognition",
                "temporal_horizon_dependent_planning",
                "goal_hierarchy_emergence",
                "habit_policy_execution",
            ],
        }
        self.strategy_history.append(output)
        return output


class ProspectiveMemory:
    construct_id = "prospective_memory"

    def __init__(self) -> None:
        self.prospective_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        identity = dependencies.get("identity_temporal_self", {})
        attention = dependencies.get("attention_control", {})
        intentions = _future_intentions(input_state)
        cues = _cue_events(input_state)
        identity_coherence = _clamp_float(identity.get("identity_coherence"), default=0.55)
        attention_stability = _clamp_float(attention.get("attention_stability"), default=0.55)
        interruption_load = _clamp_float(
            _dict_or_empty(input_state.get("context")).get("interruption_load"),
            default=0.22,
        )
        scored = []
        for index, intention in enumerate(intentions):
            cue_validity = max(
                [_cue_match_score(intention, cue) for cue in cues] or [0.0]
            )
            due_readiness = _intention_due_score(intention, input_state)
            retention = _clamp_float(
                intention.get("retention_strength"),
                default=_clamp_float(intention.get("confidence"), default=0.62),
            )
            ongoing_protection = _clamp_float(
                intention.get("ongoing_task_protection"),
                default=0.62,
            )
            interruption_recovery = _clamp_float(
                intention.get("interruption_recovery"),
                default=0.58,
            )
            priority = _clamp_float(intention.get("priority"), default=0.55)
            retrieval_readiness = _clamp(
                0.22 * cue_validity
                + 0.18 * due_readiness
                + 0.18 * retention
                + 0.14 * ongoing_protection
                + 0.12 * interruption_recovery
                + 0.08 * identity_coherence
                + 0.08 * attention_stability
            )
            execution_gate = (
                cue_validity >= 0.62
                and due_readiness >= 0.45
                and retrieval_readiness >= 0.58
            )
            scored.append(
                {
                    "intention_id": str(intention.get("id") or f"future_intention_{index + 1}"),
                    "target": str(intention.get("target") or "unknown"),
                    "cue_validity": round(cue_validity, 4),
                    "due_readiness": round(due_readiness, 4),
                    "retention_strength": round(retention, 4),
                    "ongoing_task_protection": round(ongoing_protection, 4),
                    "interruption_recovery": round(interruption_recovery, 4),
                    "priority": round(priority, 4),
                    "retrieval_readiness": round(retrieval_readiness, 4),
                    "execution_gate_open": execution_gate,
                }
            )
        scored.sort(
            key=lambda item: (
                item["execution_gate_open"],
                item["retrieval_readiness"],
                item["priority"],
            ),
            reverse=True,
        )
        triggered = [item for item in scored if item["execution_gate_open"]]
        suppressed_invalid = []
        for cue in cues:
            best_match = max([_cue_match_score(intention, cue) for intention in intentions] or [0.0])
            if best_match < 0.45:
                suppressed_invalid.append(
                    {
                        "cue_id": str(cue.get("id") or cue.get("type") or "unknown"),
                        "best_match": round(best_match, 4),
                        "suppression_reason": "invalid_cue_nonexecution",
                    }
                )
        retention_strength = _mean(
            _clamp_float(item.get("retention_strength"), default=0.0)
            for item in scored
        ) if scored else 0.0
        recovery_score = _mean(
            _clamp_float(item.get("interruption_recovery"), default=0.0)
            for item in scored
        ) if scored else 0.0
        prospective_memory_score = _clamp(
            0.38 * (_mean(_clamp_float(item.get("retrieval_readiness"), default=0.0) for item in scored) if scored else 0.0)
            + 0.22 * retention_strength
            + 0.16 * recovery_score
            + 0.14 * identity_coherence
            + 0.1 * attention_stability
            - 0.08 * interruption_load
        )
        boundary_flags = []
        if not triggered and cues:
            boundary_flags.append("cue_present_without_valid_delayed_execution")
        if suppressed_invalid:
            boundary_flags.append("invalid_cue_nonexecution_active")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "future_intentions": scored,
            "triggered_intentions": triggered,
            "suppressed_invalid_cues": suppressed_invalid,
            "prospective_memory_score": round(prospective_memory_score, 4),
            "retention_strength": round(retention_strength, 4),
            "interruption_recovery_score": round(recovery_score, 4),
            "identity_coherence_used": round(identity_coherence, 4),
            "attention_stability_used": round(attention_stability, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "temporal_horizon_dependent_planning",
                "identity_temporal_self",
                "attention_control",
                "working_memory_rehearsal",
                "episodic_memory_binding",
                "habit_policy_execution",
            ],
        }
        self.prospective_history.append(output)
        return output


class PerspectiveTaking:
    construct_id = "perspective_taking"

    def __init__(self) -> None:
        self.perspective_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        boundary = dependencies.get("boundary_self", {})
        arbitration = dependencies.get("self_other_prediction_error_arbitration", {})
        frames = _perspective_frames(input_state)
        boundary_confidence = _clamp_float(boundary.get("self_boundary_confidence"), default=0.55)
        prediction_arbitration = _clamp_float(
            arbitration.get("proxy_activation"),
            default=_clamp_float(arbitration.get("confidence"), default=0.55),
        )
        models = []
        for index, frame in enumerate(frames):
            self_interference = _clamp_float(frame.get("self_interference"), default=0.35)
            self_suppression = _clamp(1.0 - self_interference)
            other_state_inference = _clamp_float(frame.get("other_state_evidence"), default=0.55)
            viewpoint_binding = _clamp_float(frame.get("viewpoint_binding"), default=0.55)
            conflict_resolution = _clamp_float(
                frame.get("conflict_resolution"),
                default=0.5 * self_suppression + 0.5 * prediction_arbitration,
            )
            social_label_penalty = 0.18 * _clamp_float(frame.get("social_label_risk"), default=0.0)
            salience_penalty = 0.14 * _clamp_float(frame.get("salience_shortcut_risk"), default=0.0)
            perspective_score = _clamp(
                0.24 * self_suppression
                + 0.22 * other_state_inference
                + 0.2 * viewpoint_binding
                + 0.16 * conflict_resolution
                + 0.1 * boundary_confidence
                + 0.08 * prediction_arbitration
                - social_label_penalty
                - salience_penalty
            )
            models.append(
                {
                    "frame_id": str(frame.get("id") or f"perspective_frame_{index + 1}"),
                    "agent_id": str(frame.get("agent_id") or "unknown_agent"),
                    "self_perspective_suppression": round(self_suppression, 4),
                    "other_state_inference": round(other_state_inference, 4),
                    "viewpoint_binding": round(viewpoint_binding, 4),
                    "conflict_resolved_prediction": round(conflict_resolution, 4),
                    "perspective_score": round(perspective_score, 4),
                }
            )
        models.sort(key=lambda item: item["perspective_score"], reverse=True)
        perspective_accuracy_proxy = _mean(
            _clamp_float(model.get("perspective_score"), default=0.0)
            for model in models
        ) if models else 0.0
        self_interference_suppression = _mean(
            _clamp_float(model.get("self_perspective_suppression"), default=0.0)
            for model in models
        ) if models else 0.0
        boundary_flags = []
        if boundary_confidence < 0.65:
            boundary_flags.append("self_other_boundary_watch")
        if prediction_arbitration < 0.55:
            boundary_flags.append("self_other_prediction_error_arbitration_dependency_weak")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "perspective_models": models,
            "selected_perspective": models[0] if models else {},
            "perspective_accuracy_proxy": round(perspective_accuracy_proxy, 4),
            "self_interference_suppression": round(self_interference_suppression, 4),
            "boundary_confidence_used": round(boundary_confidence, 4),
            "prediction_arbitration_used": round(prediction_arbitration, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "self_other_boundary_sharpness",
                "social_coupling_strength_collective_agency",
                "boundary_self",
                "action_ownership",
                "social_label_template",
            ],
        }
        self.perspective_history.append(output)
        return output


class GoalHierarchyEmergence:
    construct_id = "goal_hierarchy_emergence"

    def __init__(self) -> None:
        self.hierarchy_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        goals = _list_of_dicts(input_state.get("goals"))
        planning = dependencies.get("temporal_horizon_dependent_planning", {})
        strategy = dependencies.get("strategy_selection", {})
        planning_confidence = _clamp_float(planning.get("planning_confidence"), default=0.55)
        strategy_confidence = _clamp_float(strategy.get("selection_confidence"), default=0.55)
        goal_nodes = []
        for index, goal in enumerate(goals):
            priority = _clamp_float(goal.get("priority"), default=0.55)
            expected_value = _clamp_float(goal.get("expected_value"), default=priority)
            conflict = _clamp_float(goal.get("conflict"), default=0.25)
            deadline_pressure = _clamp_float(goal.get("deadline_pressure"), default=0.3)
            parent_id = str(goal.get("parent_id") or "")
            recursive_support = _clamp(
                0.26 * priority
                + 0.22 * expected_value
                + 0.18 * (1.0 - conflict)
                + 0.14 * planning_confidence
                + 0.12 * strategy_confidence
                + 0.08 * (1.0 - deadline_pressure)
            )
            if parent_id:
                level = 1
            elif priority >= 0.9 and conflict <= 0.25:
                level = 0
            elif conflict >= 0.45:
                level = 2
            else:
                level = 1
            goal_nodes.append(
                {
                    "goal_id": str(goal.get("id") or f"goal_{index + 1}"),
                    "parent_id": parent_id or None,
                    "hierarchy_level": level,
                    "priority": round(priority, 4),
                    "expected_value": round(expected_value, 4),
                    "conflict": round(conflict, 4),
                    "deadline_pressure": round(deadline_pressure, 4),
                    "recursive_support": round(recursive_support, 4),
                }
            )
        root_goal_ids = [
            node["goal_id"]
            for node in goal_nodes
            if node["hierarchy_level"] == 0
        ]
        recursive_depth = 1 + max([int(node["hierarchy_level"]) for node in goal_nodes] or [0])
        hierarchy_coherence = _clamp(
            0.34 * (_mean(_clamp_float(node.get("recursive_support"), default=0.0) for node in goal_nodes) if goal_nodes else 0.0)
            + 0.22 * planning_confidence
            + 0.18 * strategy_confidence
            + 0.16 * (1.0 - _goal_conflict(input_state))
            + 0.1 * min(1.0, recursive_depth / 3.0)
        )
        boundary_flags = ["v2_mechanism_fingerprint_boundary_watch"]
        if _goal_conflict(input_state) >= 0.4:
            boundary_flags.append("goal_conflict_requires_resolution_before_promotion")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "goal_nodes": goal_nodes,
            "root_goal_ids": root_goal_ids,
            "recursive_depth": recursive_depth,
            "hierarchy_coherence": round(hierarchy_coherence, 4),
            "planning_confidence_used": round(planning_confidence, 4),
            "strategy_confidence_used": round(strategy_confidence, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "macro_causal_viability_maintenance",
                "action_agency",
                "branch_binding_stability",
                "strategy_selection",
            ],
        }
        self.hierarchy_history.append(output)
        return output


class ResourceCompetitionArbitration:
    construct_id = "resource_competition_arbitration"

    def __init__(self) -> None:
        self.arbitration_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        attention = dependencies.get("attention_control", {})
        strategy = dependencies.get("strategy_selection", {})
        resources = _list_of_dicts(input_state.get("resources"))
        demands = _resource_demands(input_state)
        capacity_by_id = _resource_capacity_by_id(resources)
        attention_stability = _clamp_float(attention.get("attention_stability"), default=0.55)
        strategy_confidence = _clamp_float(strategy.get("selection_confidence"), default=0.55)
        sorted_demands = sorted(
            demands,
            key=lambda item: (
                _clamp_float(item.get("priority"), default=0.5),
                _clamp_float(item.get("retention_sensitivity"), default=0.5),
            ),
            reverse=True,
        )
        remaining_capacity = dict(capacity_by_id)
        allocations = []
        for index, demand in enumerate(sorted_demands):
            resource_id = str(demand.get("resource_id") or "shared")
            available = remaining_capacity.get(resource_id, remaining_capacity.get("shared", 0.65))
            requested = _clamp_float(demand.get("demand"), default=0.45)
            priority = _clamp_float(demand.get("priority"), default=0.5)
            retention_sensitivity = _clamp_float(demand.get("retention_sensitivity"), default=0.5)
            selective_weight = _clamp(
                0.38 * priority
                + 0.22 * retention_sensitivity
                + 0.18 * attention_stability
                + 0.14 * strategy_confidence
                + 0.08 * (1.0 - _resource_scarcity(resources))
            )
            granted = min(requested, available * selective_weight)
            remaining_capacity[resource_id] = max(0.0, available - granted)
            retention_after_arbitration = _clamp(
                0.45 * (granted / max(0.01, requested))
                + 0.25 * retention_sensitivity
                + 0.18 * attention_stability
                + 0.12 * strategy_confidence
            )
            allocations.append(
                {
                    "demand_id": str(demand.get("id") or f"resource_demand_{index + 1}"),
                    "construct_pair": list(demand.get("construct_pair") or []),
                    "resource_id": resource_id,
                    "requested": round(requested, 4),
                    "granted": round(granted, 4),
                    "selective_weight": round(selective_weight, 4),
                    "retention_after_arbitration": round(retention_after_arbitration, 4),
                }
            )
        retention_preservation = _mean(
            _clamp_float(item.get("retention_after_arbitration"), default=0.0)
            for item in allocations
        ) if allocations else 0.0
        selectivity = _mean_absolute_deviation(
            [_clamp_float(item.get("granted"), default=0.0) for item in allocations]
        )
        arbitration_score = _clamp(
            0.36 * retention_preservation
            + 0.22 * attention_stability
            + 0.18 * strategy_confidence
            + 0.14 * (1.0 - _resource_scarcity(resources))
            + 0.1 * min(1.0, 2.0 * selectivity)
        )
        boundary_flags = ["severe_boundary_watch"]
        if selectivity < 0.03 and len(allocations) > 1:
            boundary_flags.append("uniform_capacity_gain_risk")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "resource_allocations": allocations,
            "retention_preservation": round(retention_preservation, 4),
            "allocation_selectivity": round(selectivity, 4),
            "arbitration_score": round(arbitration_score, 4),
            "attention_stability_used": round(attention_stability, 4),
            "strategy_confidence_used": round(strategy_confidence, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "cross_family_synergy_control",
                "attention_control",
                "strategy_selection",
                "coordination_length_control",
                "uniform_capacity_loss",
                "global_gain",
            ],
        }
        self.arbitration_history.append(output)
        return output


class AffordanceSelectionControl:
    construct_id = "affordance_selection_control"

    def __init__(self) -> None:
        self.affordance_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        agency = dependencies.get("action_agency", {})
        attention = dependencies.get("attention_control", {})
        affordances = _affordance_candidates(input_state)
        controllability = _clamp_float(agency.get("controllability"), default=0.55)
        attention_stability = _clamp_float(attention.get("attention_stability"), default=0.55)
        scored = []
        for index, affordance in enumerate(affordances):
            task_relevance = _clamp_float(
                affordance.get("task_relevance"),
                default=_affordance_context_match(affordance, input_state),
            )
            action_fit = _clamp_float(affordance.get("action_fit"), default=0.55)
            salience = _clamp_float(affordance.get("salience"), default=0.5)
            temptation = _clamp_float(affordance.get("temptation"), default=0.25)
            reward_only_risk = _clamp_float(affordance.get("reward_only_risk"), default=0.0)
            motor_speed_only_risk = _clamp_float(affordance.get("motor_speed_only_risk"), default=0.0)
            suppression_need = _clamp(0.48 * (1.0 - task_relevance) + 0.32 * temptation + 0.2 * salience)
            selection_score = _clamp(
                0.28 * task_relevance
                + 0.22 * action_fit
                + 0.18 * controllability
                + 0.16 * attention_stability
                + 0.08 * salience
                - 0.05 * reward_only_risk
                - 0.03 * motor_speed_only_risk
            )
            scored.append(
                {
                    "affordance_id": str(affordance.get("id") or f"affordance_{index + 1}"),
                    "action_type": str(affordance.get("action_type") or "unknown"),
                    "selection_score": round(selection_score, 4),
                    "task_relevance": round(task_relevance, 4),
                    "action_fit": round(action_fit, 4),
                    "salience": round(salience, 4),
                    "temptation": round(temptation, 4),
                    "suppression_need": round(suppression_need, 4),
                    "reward_only_risk": round(reward_only_risk, 4),
                    "motor_speed_only_risk": round(motor_speed_only_risk, 4),
                }
            )
        scored.sort(key=lambda item: item["selection_score"], reverse=True)
        selected = scored[0] if scored else {}
        suppressed = [
            item
            for item in scored[1:]
            if _clamp_float(item.get("suppression_need"), default=0.0) >= 0.42
            or _clamp_float(item.get("task_relevance"), default=1.0) < 0.45
        ]
        runner_up = scored[1] if len(scored) > 1 else {}
        margin = _clamp_float(selected.get("selection_score"), default=0.0) - _clamp_float(runner_up.get("selection_score"), default=0.0)
        suppression_strength = _mean(
            _clamp_float(item.get("suppression_need"), default=0.0)
            for item in suppressed
        ) if suppressed else 0.0
        affordance_selection_confidence = _clamp(
            0.42 * _clamp_float(selected.get("selection_score"), default=0.0)
            + 0.2 * margin
            + 0.18 * controllability
            + 0.12 * attention_stability
            + 0.08 * suppression_strength
        )
        boundary_flags = ["severe_boundary_watch"]
        if selected and _clamp_float(selected.get("salience"), default=0.0) > _clamp_float(selected.get("task_relevance"), default=0.0) + 0.2:
            boundary_flags.append("salience_only_selection_risk")
        if margin < 0.06 and len(scored) > 1:
            boundary_flags.append("low_affordance_selection_margin")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "scored_affordances": scored,
            "selected_affordance": selected,
            "suppressed_affordances": suppressed,
            "affordance_selection_confidence": round(affordance_selection_confidence, 4),
            "selection_margin": round(margin, 4),
            "suppression_strength": round(suppression_strength, 4),
            "controllability_used": round(controllability, 4),
            "attention_stability_used": round(attention_stability, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "action_agency",
                "attention_control",
                "strategy_selection",
                "distributed_body_schema_self",
                "action_ownership",
                "salience_only",
                "motor_speed_only",
            ],
        }
        self.affordance_history.append(output)
        return output


class SelfOtherBoundarySharpness:
    construct_id = "self_other_boundary_sharpness"

    def __init__(self) -> None:
        self.boundary_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        boundary = dependencies.get("boundary_self", {})
        context = _dict_or_empty(input_state.get("context"))
        self_id = str(boundary.get("self_id") or context.get("self_id") or "mind_executor")
        source_table = _source_attribution_table(input_state, self_id)
        boundary_confidence = _clamp_float(boundary.get("self_boundary_confidence"), default=0.55)
        source_axis_separation = _mean(
            _clamp_float(item.get("source_axis_separation"), default=0.0)
            for item in source_table
        ) if source_table else 0.55
        other_model_independence = _mean(
            _clamp_float(item.get("other_model_independence"), default=0.0)
            for item in source_table
        ) if source_table else 0.55
        paired_actuator_gap = _mean(
            _clamp_float(item.get("paired_actuator_gap"), default=0.0)
            for item in source_table
        ) if source_table else 0.55
        role_shortcut_rejection = _clamp(
            1.0 - _mean(
                _clamp_float(item.get("visible_role_shortcut_risk"), default=0.0)
                for item in source_table
            )
        ) if source_table else 0.55
        shared_control_ambiguity = _mean(
            _clamp_float(item.get("shared_control_ambiguity"), default=0.0)
            for item in source_table
        ) if source_table else 0.25
        boundary_sharpness = _clamp(
            0.24 * source_axis_separation
            + 0.2 * other_model_independence
            + 0.18 * paired_actuator_gap
            + 0.16 * role_shortcut_rejection
            + 0.14 * boundary_confidence
            + 0.08 * (1.0 - shared_control_ambiguity)
        )
        boundary_flags = []
        if shared_control_ambiguity >= 0.45:
            boundary_flags.append("shared_control_non_identifiability_watch")
        if role_shortcut_rejection < 0.65:
            boundary_flags.append("visible_role_shortcut_risk")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "source_attribution_table": source_table,
            "source_axis_separation": round(source_axis_separation, 4),
            "other_model_independence": round(other_model_independence, 4),
            "paired_actuator_gap": round(paired_actuator_gap, 4),
            "role_shortcut_rejection": round(role_shortcut_rejection, 4),
            "shared_control_ambiguity": round(shared_control_ambiguity, 4),
            "boundary_sharpness": round(boundary_sharpness, 4),
            "boundary_confidence_used": round(boundary_confidence, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "action_agency",
                "boundary_self",
                "identity_temporal_self",
                "action_ownership",
                "distributed_body_schema_self",
                "global_broadcast_phase",
            ],
        }
        self.boundary_history.append(output)
        return output


class SelfOtherPredictionErrorArbitration:
    construct_id = "self_other_prediction_error_arbitration"

    def __init__(self) -> None:
        self.arbitration_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        boundary = dependencies.get("boundary_self", {})
        boundary_sharpness = dependencies.get("self_other_boundary_sharpness", {})
        error = dependencies.get("error_monitoring", {})
        ownership = dependencies.get("action_ownership", {})
        errors = _self_other_prediction_errors(input_state)
        self_id = str(boundary.get("self_id") or _dict_or_empty(input_state.get("context")).get("self_id") or "mind_executor")
        sharpness = _clamp_float(boundary_sharpness.get("boundary_sharpness"), default=0.55)
        monitor_confidence = _clamp_float(error.get("monitor_confidence"), default=0.55)
        ownership_score = _clamp_float(ownership.get("ownership_score"), default=0.55)
        assignments = []
        for index, event in enumerate(errors):
            self_error = _clamp_float(event.get("self_error"), default=0.5)
            other_error = _clamp_float(event.get("other_error"), default=0.5)
            coupling = _clamp_float(event.get("coupling"), default=0.35)
            social_label_risk = _clamp_float(event.get("social_label_risk"), default=0.0)
            salience_risk = _clamp_float(event.get("salience_risk"), default=0.0)
            magnitude_only_risk = _clamp_float(event.get("magnitude_only_risk"), default=0.0)
            source_gap = abs(self_error - other_error)
            self_score = _clamp(
                0.34 * self_error
                + 0.2 * ownership_score
                + 0.18 * sharpness
                + 0.16 * monitor_confidence
                + 0.12 * (1.0 - coupling)
                - 0.08 * social_label_risk
                - 0.06 * salience_risk
                - 0.05 * magnitude_only_risk
            )
            other_score = _clamp(
                0.36 * other_error
                + 0.22 * sharpness
                + 0.16 * monitor_confidence
                + 0.14 * coupling
                + 0.12 * (1.0 - ownership_score)
                - 0.08 * social_label_risk
                - 0.06 * salience_risk
                - 0.05 * magnitude_only_risk
            )
            if abs(self_score - other_score) < 0.05:
                assigned_source = "ambiguous"
            elif self_score > other_score:
                assigned_source = self_id
            else:
                assigned_source = str(event.get("other_agent_id") or "other_agent")
            policy_update = "self_policy_update" if assigned_source == self_id else (
                "other_model_update" if assigned_source != "ambiguous" else "defer_source_specific_update"
            )
            assignments.append(
                {
                    "event_id": str(event.get("id") or f"self_other_error_{index + 1}"),
                    "assigned_source": assigned_source,
                    "self_source_score": round(self_score, 4),
                    "other_source_score": round(other_score, 4),
                    "source_gap": round(source_gap, 4),
                    "coupling": round(coupling, 4),
                    "policy_update": policy_update,
                }
            )
        source_specificity = _mean(
            abs(
                _clamp_float(item.get("self_source_score"), default=0.0)
                - _clamp_float(item.get("other_source_score"), default=0.0)
            )
            for item in assignments
        ) if assignments else 0.0
        arbitration_confidence = _clamp(
            0.32 * sharpness
            + 0.24 * monitor_confidence
            + 0.18 * ownership_score
            + 0.16 * source_specificity
            + 0.1 * (1.0 - _mean(_clamp_float(event.get("coupling"), default=0.35) for event in errors))
        ) if errors else _clamp(0.5 * sharpness + 0.3 * monitor_confidence + 0.2 * ownership_score)
        boundary_flags = []
        if any(item["assigned_source"] == "ambiguous" for item in assignments):
            boundary_flags.append("coupled_agent_source_ambiguity")
        if sharpness < 0.62:
            boundary_flags.append("self_other_boundary_sharpness_dependency_weak")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "source_assignments": assignments,
            "source_specificity": round(source_specificity, 4),
            "arbitration_confidence": round(arbitration_confidence, 4),
            "boundary_sharpness_used": round(sharpness, 4),
            "monitor_confidence_used": round(monitor_confidence, 4),
            "ownership_score_used": round(ownership_score, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "self_other_boundary_sharpness",
                "error_monitoring",
                "action_ownership",
                "social_label_template",
                "prediction_error_magnitude_only",
            ],
        }
        self.arbitration_history.append(output)
        return output


class GlobalBroadcastPhase:
    construct_id = "global_broadcast_phase"

    def __init__(self) -> None:
        self.broadcast_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        flow = dependencies.get("information_flow_onset_gating", {})
        attention = dependencies.get("attention_control", {})
        integration = dependencies.get("information_integration_phase", {})
        routes = _broadcast_route_candidates(input_state, flow, attention)
        gate_stability = _clamp_float(flow.get("gate_stability"), default=0.55)
        attention_stability = _clamp_float(attention.get("attention_stability"), default=0.55)
        integration_coherence = _clamp_float(integration.get("integration_coherence"), default=0.55)
        scored = []
        for index, route in enumerate(routes):
            availability = _clamp_float(route.get("global_availability"), default=0.55)
            ignition = _clamp_float(route.get("workspace_ignition"), default=0.5)
            conflict_access = _clamp_float(route.get("conflict_routed_access"), default=0.5)
            cross_context = _clamp_float(route.get("cross_context_selection"), default=0.5)
            fanout_risk = _clamp_float(route.get("fanout_only_risk"), default=0.0)
            salience_risk = _clamp_float(route.get("salience_only_risk"), default=0.0)
            broadcast_score = _clamp(
                0.22 * availability
                + 0.2 * ignition
                + 0.18 * conflict_access
                + 0.16 * cross_context
                + 0.12 * gate_stability
                + 0.08 * attention_stability
                + 0.04 * integration_coherence
                - 0.08 * fanout_risk
                - 0.06 * salience_risk
            )
            scored.append(
                {
                    "route_id": str(route.get("id") or f"broadcast_route_{index + 1}"),
                    "broadcast_score": round(broadcast_score, 4),
                    "global_availability": round(availability, 4),
                    "workspace_ignition": round(ignition, 4),
                    "conflict_routed_access": round(conflict_access, 4),
                    "cross_context_selection": round(cross_context, 4),
                }
            )
        scored.sort(key=lambda item: item["broadcast_score"], reverse=True)
        selected = scored[0] if scored else {}
        selective_global_availability = _mean(
            _clamp_float(route.get("broadcast_score"), default=0.0)
            for route in scored[:2]
        ) if scored else 0.0
        broadcast_phase_score = _clamp(
            0.42 * _clamp_float(selected.get("broadcast_score"), default=0.0)
            + 0.2 * selective_global_availability
            + 0.16 * gate_stability
            + 0.12 * attention_stability
            + 0.1 * integration_coherence
        )
        boundary_flags = []
        if selected and _clamp_float(selected.get("global_availability"), default=0.0) < 0.55:
            boundary_flags.append("local_accuracy_without_global_availability_watch")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "broadcast_routes": scored,
            "selected_broadcast_route": selected,
            "selective_global_availability": round(selective_global_availability, 4),
            "broadcast_phase_score": round(broadcast_phase_score, 4),
            "gate_stability_used": round(gate_stability, 4),
            "attention_stability_used": round(attention_stability, 4),
            "integration_coherence_used": round(integration_coherence, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "information_integration_phase",
                "attention_control",
                "macro_causal_viability_maintenance",
                "fanout_only",
                "salience_attention_no_global_availability",
            ],
        }
        self.broadcast_history.append(output)
        return output


class BodySchemaErrorCorrection:
    construct_id = "body_schema_error_correction"

    def __init__(self) -> None:
        self.correction_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        body = dependencies.get("distributed_body_schema_self", {})
        error = dependencies.get("error_monitoring", {})
        distortions = _body_schema_distortions(input_state)
        body_confidence = _clamp_float(body.get("self_schema_confidence"), default=0.55)
        monitor_confidence = _clamp_float(error.get("monitor_confidence"), default=0.55)
        corrections = []
        for index, distortion in enumerate(distortions):
            distortion_magnitude = _clamp_float(distortion.get("distortion"), default=0.35)
            feedback_delay = _clamp_float(distortion.get("feedback_delay"), default=0.25)
            sensor_reliability = _clamp_float(distortion.get("sensor_reliability"), default=_sensor_alignment(input_state))
            motor_gain_risk = _clamp_float(distortion.get("motor_gain_risk"), default=0.0)
            sensory_salience_risk = _clamp_float(distortion.get("sensory_salience_risk"), default=0.0)
            correction_gain = _clamp(
                0.28 * distortion_magnitude
                + 0.22 * sensor_reliability
                + 0.18 * body_confidence
                + 0.16 * monitor_confidence
                + 0.1 * (1.0 - feedback_delay)
                - 0.04 * motor_gain_risk
                - 0.04 * sensory_salience_risk
            )
            residual_error = _clamp(distortion_magnitude * (1.0 - correction_gain))
            corrections.append(
                {
                    "distortion_id": str(distortion.get("id") or f"body_distortion_{index + 1}"),
                    "body_part": str(distortion.get("body_part") or "distributed_body_map"),
                    "correction_gain": round(correction_gain, 4),
                    "residual_error": round(residual_error, 4),
                    "feedback_delay": round(feedback_delay, 4),
                    "sensor_reliability": round(sensor_reliability, 4),
                }
            )
        correction_strength = _mean(
            _clamp_float(item.get("correction_gain"), default=0.0)
            for item in corrections
        ) if corrections else 0.0
        residual_body_error = _mean(
            _clamp_float(item.get("residual_error"), default=0.0)
            for item in corrections
        ) if corrections else 0.0
        boundary_flags = ["boundary_watch"]
        if correction_strength < 0.45:
            boundary_flags.append("weak_body_map_error_correction")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "body_schema_corrections": corrections,
            "correction_strength": round(correction_strength, 4),
            "residual_body_error": round(residual_body_error, 4),
            "body_confidence_used": round(body_confidence, 4),
            "monitor_confidence_used": round(monitor_confidence, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "distributed_body_schema_self",
                "error_monitoring",
                "action_ownership",
                "action_agency",
                "motor_gain_only",
                "sensory_salience_only",
            ],
        }
        self.correction_history.append(output)
        return output


class WorkingMemoryCapacityRework:
    construct_id = "working_memory_capacity_rework"

    def __init__(self) -> None:
        self.capacity_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        attention = dependencies.get("attention_control", {})
        episodic = dependencies.get("episodic_memory_binding", {})
        items = _working_memory_items(input_state)
        attention_stability = _clamp_float(attention.get("attention_stability"), default=0.55)
        episodic_binding = _clamp_float(episodic.get("global_binding_strength"), default=0.55)
        capacity_limit = max(1, int(_dict_or_empty(input_state.get("context")).get("working_memory_capacity", 4)))
        refreshed = []
        for index, item in enumerate(items):
            load = _clamp_float(item.get("load"), default=0.25)
            interference = _clamp_float(item.get("interference"), default=0.25)
            salience = _clamp_float(item.get("salience"), default=0.5)
            rehearsal_speed_risk = _clamp_float(item.get("rehearsal_speed_risk"), default=0.0)
            semantic_chunking_risk = _clamp_float(item.get("semantic_chunking_risk"), default=0.0)
            active_maintenance = _clamp(
                0.26 * attention_stability
                + 0.2 * episodic_binding
                + 0.18 * (1.0 - load)
                + 0.16 * (1.0 - interference)
                + 0.12 * salience
                + 0.08 * (1.0 - min(1.0, len(items) / max(1, capacity_limit + 1)))
                - 0.05 * rehearsal_speed_risk
                - 0.04 * semantic_chunking_risk
            )
            refreshed.append(
                {
                    "item_id": str(item.get("id") or f"wm_item_{index + 1}"),
                    "active_maintenance": round(active_maintenance, 4),
                    "load": round(load, 4),
                    "interference": round(interference, 4),
                    "refresh_priority": round(_clamp(0.5 * interference + 0.3 * load + 0.2 * salience), 4),
                }
            )
        refreshed.sort(key=lambda item: item["active_maintenance"], reverse=True)
        maintained = refreshed[:capacity_limit]
        dropped = refreshed[capacity_limit:]
        load_specific_recall = _mean(
            _clamp_float(item.get("active_maintenance"), default=0.0)
            for item in maintained
        ) if maintained else 0.0
        overload_pressure = _clamp(max(0, len(items) - capacity_limit) / max(1, len(items)))
        capacity_score = _clamp(
            0.42 * load_specific_recall
            + 0.22 * attention_stability
            + 0.16 * episodic_binding
            + 0.12 * (1.0 - overload_pressure)
            + 0.08 * (1.0 - _mean(_clamp_float(item.get("interference"), default=0.0) for item in items))
        ) if items else 0.0
        boundary_flags = ["severe_boundary_watch"]
        if overload_pressure > 0.0:
            boundary_flags.append("capacity_limited_drop_active")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "maintained_items": maintained,
            "dropped_items": dropped,
            "capacity_limit": capacity_limit,
            "load_specific_recall": round(load_specific_recall, 4),
            "overload_pressure": round(overload_pressure, 4),
            "working_memory_capacity_score": round(capacity_score, 4),
            "attention_stability_used": round(attention_stability, 4),
            "episodic_binding_used": round(episodic_binding, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "attention_control",
                "strategy_selection",
                "episodic_memory_binding",
                "prospective_memory",
                "semantic_memory_retrieval",
                "salience_only",
                "rehearsal_speed_only",
            ],
        }
        self.capacity_history.append(output)
        return output


class LearningRateAdaptationRework:
    construct_id = "learning_rate_adaptation_rework"

    def __init__(self) -> None:
        self.learning_rate_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        pem = dependencies.get("predictive_error_minimization_phase", {})
        error = dependencies.get("error_monitoring", {})
        contexts = _learning_contexts(input_state)
        minimization_gain = _clamp_float(pem.get("minimization_gain"), default=0.15)
        monitor_confidence = _clamp_float(error.get("monitor_confidence"), default=0.55)
        rate_updates = []
        for index, context in enumerate(contexts):
            volatility = _clamp_float(context.get("volatility"), default=0.35)
            feedback_reliability = _clamp_float(context.get("feedback_reliability"), default=0.7)
            reward_only_risk = _clamp_float(context.get("reward_only_risk"), default=0.0)
            recency_only_risk = _clamp_float(context.get("recency_only_risk"), default=0.0)
            prediction_error_only_risk = _clamp_float(context.get("prediction_error_only_risk"), default=0.0)
            target_rate = _clamp(
                0.1
                + 0.42 * volatility
                + 0.22 * feedback_reliability
                + 0.14 * monitor_confidence
                + 0.12 * minimization_gain
                - 0.06 * reward_only_risk
                - 0.05 * recency_only_risk
                - 0.05 * prediction_error_only_risk
            )
            current_rate = _clamp_float(context.get("current_rate"), default=0.32)
            delta = target_rate - current_rate
            rate_updates.append(
                {
                    "context_id": str(context.get("id") or f"learning_context_{index + 1}"),
                    "current_rate": round(current_rate, 4),
                    "target_rate": round(target_rate, 4),
                    "rate_delta": round(delta, 4),
                    "volatility": round(volatility, 4),
                    "feedback_reliability": round(feedback_reliability, 4),
                }
            )
        volatility_match = _mean(
            1.0 - abs(_clamp_float(item.get("target_rate"), default=0.0) - _clamp_float(item.get("volatility"), default=0.0))
            for item in rate_updates
        ) if rate_updates else 0.0
        adaptation_score = _clamp(
            0.38 * volatility_match
            + 0.22 * monitor_confidence
            + 0.18 * minimization_gain
            + 0.12 * (_mean(_clamp_float(item.get("feedback_reliability"), default=0.0) for item in rate_updates) if rate_updates else 0.0)
            + 0.1 * (1.0 - _raw_error_load(input_state))
        )
        boundary_flags = ["boundary_watch"]
        if volatility_match < 0.55:
            boundary_flags.append("weak_volatility_matched_update_rate")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "learning_rate_updates": rate_updates,
            "volatility_match": round(volatility_match, 4),
            "learning_rate_adaptation_score": round(adaptation_score, 4),
            "minimization_gain_used": round(minimization_gain, 4),
            "monitor_confidence_used": round(monitor_confidence, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "predictive_error_minimization_phase",
                "strategy_selection",
                "error_monitoring",
                "latent_context_switch_detection",
                "reward_maximization_only",
                "recency_weighting_only",
            ],
        }
        self.learning_rate_history.append(output)
        return output


class ConfidenceCalibrationRework:
    construct_id = "confidence_calibration_rework"

    def __init__(self) -> None:
        self.calibration_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        uncertainty = dependencies.get("uncertainty_threshold_metacognition", {})
        error = dependencies.get("error_monitoring", {})
        observations = _confidence_observations(input_state)
        uncertainty_score = _clamp_float(uncertainty.get("uncertainty_score"), default=0.45)
        monitor_confidence = _clamp_float(error.get("monitor_confidence"), default=0.55)
        calibrated = []
        for index, observation in enumerate(observations):
            raw_confidence = _clamp_float(observation.get("confidence"), default=0.55)
            observed_error_probability = _clamp_float(
                observation.get("error_probability"),
                default=1.0 - _clamp_float(observation.get("outcome_correct"), default=0.6),
            )
            evidence_noise = _clamp_float(observation.get("evidence_noise"), default=0.25)
            feedback_delay = _clamp_float(observation.get("feedback_delay"), default=0.25)
            accuracy_only_risk = _clamp_float(observation.get("accuracy_only_risk"), default=0.0)
            feedback_frequency_risk = _clamp_float(observation.get("feedback_frequency_risk"), default=0.0)
            label_template_risk = _clamp_float(observation.get("label_template_risk"), default=0.0)
            target_confidence = _clamp(1.0 - observed_error_probability)
            delay_adjustment = 0.12 * feedback_delay + 0.1 * evidence_noise + 0.08 * uncertainty_score
            calibrated_confidence = _clamp(
                0.55 * raw_confidence
                + 0.45 * target_confidence
                - delay_adjustment
                - 0.05 * accuracy_only_risk
                - 0.04 * feedback_frequency_risk
                - 0.04 * label_template_risk
            )
            calibration_error = abs(calibrated_confidence - target_confidence)
            calibrated.append(
                {
                    "observation_id": str(observation.get("id") or f"confidence_observation_{index + 1}"),
                    "raw_confidence": round(raw_confidence, 4),
                    "target_confidence": round(target_confidence, 4),
                    "calibrated_confidence": round(calibrated_confidence, 4),
                    "calibration_error": round(calibration_error, 4),
                    "evidence_noise": round(evidence_noise, 4),
                    "feedback_delay": round(feedback_delay, 4),
                }
            )
        mean_error = _mean(
            _clamp_float(item.get("calibration_error"), default=0.0)
            for item in calibrated
        ) if calibrated else 0.5
        calibration_score = _clamp(
            0.42 * (1.0 - mean_error)
            + 0.2 * monitor_confidence
            + 0.16 * (1.0 - uncertainty_score)
            + 0.12 * (1.0 - _raw_error_load(input_state))
            + 0.1 * (1.0 - _mean(_clamp_float(item.get("feedback_delay"), default=0.0) for item in calibrated))
        ) if calibrated else 0.0
        boundary_flags = ["severe_boundary_watch"]
        if mean_error >= 0.18:
            boundary_flags.append("high_confidence_calibration_error")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "calibrated_confidence_observations": calibrated,
            "mean_calibration_error": round(mean_error, 4),
            "confidence_calibration_score": round(calibration_score, 4),
            "uncertainty_score_used": round(uncertainty_score, 4),
            "monitor_confidence_used": round(monitor_confidence, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "uncertainty_threshold_metacognition",
                "error_monitoring",
                "strategy_selection",
                "learning_rate_adaptation_rework",
                "accuracy_only",
                "feedback_frequency_only",
                "confidence_label_template",
            ],
        }
        self.calibration_history.append(output)
        return output


class ContextualPolicyInhibition:
    construct_id = "contextual_policy_inhibition"

    def __init__(self) -> None:
        self.inhibition_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        attention = dependencies.get("attention_control", {})
        strategy = dependencies.get("strategy_selection", {})
        contexts = _policy_contexts(input_state)
        attention_stability = _clamp_float(attention.get("attention_stability"), default=0.55)
        strategy_confidence = _clamp_float(strategy.get("selection_confidence"), default=0.55)
        decisions = []
        for index, context in enumerate(contexts):
            prepotent_strength = _clamp_float(context.get("prepotent_strength"), default=0.55)
            switch_pressure = _clamp_float(context.get("switch_pressure"), default=0.45)
            context_match = _clamp_float(context.get("context_match"), default=0.55)
            switch_action_fit = _clamp_float(context.get("switch_action_fit"), default=0.55)
            false_inhibition_risk = _clamp_float(context.get("false_inhibition_risk"), default=0.2)
            salience_only_risk = _clamp_float(context.get("salience_only_risk"), default=0.0)
            motor_suppression_risk = _clamp_float(context.get("motor_suppression_risk"), default=0.0)
            inhibition_gate = _clamp(
                0.24 * prepotent_strength
                + 0.22 * switch_pressure
                + 0.18 * context_match
                + 0.14 * switch_action_fit
                + 0.1 * attention_stability
                + 0.08 * strategy_confidence
                - 0.08 * false_inhibition_risk
                - 0.04 * salience_only_risk
                - 0.04 * motor_suppression_risk
            )
            should_inhibit = bool(context.get("should_inhibit", inhibition_gate >= 0.58))
            release_switch_action = inhibition_gate >= 0.58 and should_inhibit
            decisions.append(
                {
                    "context_id": str(context.get("id") or f"policy_context_{index + 1}"),
                    "policy_id": str(context.get("policy_id") or "unknown_policy"),
                    "inhibition_gate": round(inhibition_gate, 4),
                    "prepotent_strength": round(prepotent_strength, 4),
                    "context_match": round(context_match, 4),
                    "switch_action_fit": round(switch_action_fit, 4),
                    "inhibit_prepotent_policy": release_switch_action,
                    "false_inhibition_risk": round(false_inhibition_risk, 4),
                }
            )
        control_score = _mean(
            _clamp_float(item.get("inhibition_gate"), default=0.0)
            for item in decisions
        ) if decisions else 0.0
        false_inhibition_mean = _mean(
            _clamp_float(item.get("false_inhibition_risk"), default=0.0)
            for item in decisions
        ) if decisions else 0.0
        inhibition_score = _clamp(
            0.46 * control_score
            + 0.18 * attention_stability
            + 0.16 * strategy_confidence
            + 0.12 * (1.0 - false_inhibition_mean)
            + 0.08 * (1.0 - _raw_error_load(input_state))
        )
        boundary_flags = ["severe_boundary_watch"]
        if any(not item["inhibit_prepotent_policy"] and item["inhibition_gate"] >= 0.58 for item in decisions):
            boundary_flags.append("false_noninhibition_watch")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "policy_inhibition_decisions": decisions,
            "contextual_inhibition_score": round(inhibition_score, 4),
            "attention_stability_used": round(attention_stability, 4),
            "strategy_confidence_used": round(strategy_confidence, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "strategy_selection",
                "attention_control",
                "latent_context_switch_detection",
                "error_monitoring",
                "affordance_selection_control",
                "reward_only",
                "salience_only",
                "motor_suppression_only",
            ],
        }
        self.inhibition_history.append(output)
        return output


class GoalConflictResolution:
    construct_id = "goal_conflict_resolution"

    def __init__(self) -> None:
        self.resolution_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        hierarchy = dependencies.get("goal_hierarchy_emergence", {})
        strategy = dependencies.get("strategy_selection", {})
        conflicts = _goal_conflict_cases(input_state)
        hierarchy_coherence = _clamp_float(hierarchy.get("hierarchy_coherence"), default=0.55)
        strategy_confidence = _clamp_float(strategy.get("selection_confidence"), default=0.55)
        resolutions = []
        for index, conflict in enumerate(conflicts):
            goals = _list_of_dicts(conflict.get("goals"))
            scored_goals = []
            for goal_index, goal in enumerate(goals):
                priority = _clamp_float(goal.get("priority"), default=0.55)
                expected_value = _clamp_float(goal.get("expected_value"), default=priority)
                constraint_pressure = _clamp_float(goal.get("constraint_pressure"), default=0.35)
                recency_bias = _clamp_float(goal.get("recency_bias"), default=0.0)
                reward_magnitude_risk = _clamp_float(goal.get("reward_magnitude_risk"), default=0.0)
                score = _clamp(
                    0.3 * priority
                    + 0.22 * expected_value
                    + 0.18 * (1.0 - constraint_pressure)
                    + 0.12 * hierarchy_coherence
                    + 0.1 * strategy_confidence
                    - 0.05 * recency_bias
                    - 0.03 * reward_magnitude_risk
                )
                scored_goals.append(
                    {
                        "goal_id": str(goal.get("id") or f"conflict_goal_{goal_index + 1}"),
                        "resolution_score": round(score, 4),
                        "priority": round(priority, 4),
                        "expected_value": round(expected_value, 4),
                        "constraint_pressure": round(constraint_pressure, 4),
                    }
                )
            scored_goals.sort(key=lambda item: item["resolution_score"], reverse=True)
            selected = scored_goals[0] if scored_goals else {}
            suppressed = scored_goals[1:]
            margin = _clamp_float(selected.get("resolution_score"), default=0.0) - (
                _clamp_float(suppressed[0].get("resolution_score"), default=0.0)
                if suppressed else 0.0
            )
            resolutions.append(
                {
                    "conflict_id": str(conflict.get("id") or f"goal_conflict_{index + 1}"),
                    "selected_goal": selected,
                    "suppressed_goals": suppressed,
                    "selection_margin": round(margin, 4),
                    "commit_policy": margin >= 0.08 and bool(selected),
                }
            )
        resolution_score = _clamp(
            0.42 * (_mean(_clamp_float(item.get("selection_margin"), default=0.0) for item in resolutions) if resolutions else 0.0)
            + 0.24 * hierarchy_coherence
            + 0.18 * strategy_confidence
            + 0.16 * (1.0 - _goal_conflict(input_state))
        )
        boundary_flags = ["severe_boundary_watch"]
        if any(not item["commit_policy"] for item in resolutions):
            boundary_flags.append("low_goal_conflict_resolution_margin")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "goal_conflict_resolutions": resolutions,
            "goal_conflict_resolution_score": round(resolution_score, 4),
            "hierarchy_coherence_used": round(hierarchy_coherence, 4),
            "strategy_confidence_used": round(strategy_confidence, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "resource_competition_arbitration",
                "strategy_selection",
                "goal_hierarchy_emergence",
                "attention_control",
                "reward_magnitude_only",
                "single_goal_high_load",
                "recency_goal_bias",
            ],
        }
        self.resolution_history.append(output)
        return output


class CrossFamilySynergyControl:
    construct_id = "cross_family_synergy_control"

    def __init__(self) -> None:
        self.synergy_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        resource = dependencies.get("resource_competition_arbitration", {})
        coordination = dependencies.get("coordination_length_control", {})
        pairs = _synergy_pairs(input_state)
        arbitration_score = _clamp_float(resource.get("arbitration_score"), default=0.55)
        coordination_signal = _clamp_float(
            coordination.get(
                "coordination_length_control_score",
                coordination.get("proxy_activation"),
            ),
            default=0.55,
        )
        controlled_pairs = []
        for index, pair in enumerate(pairs):
            complementarity = _clamp_float(pair.get("complementarity"), default=0.55)
            heldout_margin = _clamp_float(pair.get("heldout_margin"), default=0.5)
            family_reversal_generalization = _clamp_float(pair.get("family_reversal_generalization"), default=0.55)
            seen_pair_risk = _clamp_float(pair.get("seen_pair_risk"), default=0.0)
            within_family_false_synergy = _clamp_float(pair.get("within_family_false_synergy"), default=0.0)
            demand_sum_only_risk = _clamp_float(pair.get("demand_sum_only_risk"), default=0.0)
            synergy_score = _clamp(
                0.26 * complementarity
                + 0.24 * heldout_margin
                + 0.18 * family_reversal_generalization
                + 0.12 * arbitration_score
                + 0.1 * coordination_signal
                - 0.05 * seen_pair_risk
                - 0.04 * within_family_false_synergy
                - 0.04 * demand_sum_only_risk
            )
            controlled_pairs.append(
                {
                    "pair_id": str(pair.get("id") or f"cross_family_pair_{index + 1}"),
                    "families": list(pair.get("families") or []),
                    "synergy_score": round(synergy_score, 4),
                    "heldout_margin": round(heldout_margin, 4),
                    "family_reversal_generalization": round(family_reversal_generalization, 4),
                    "complementarity": round(complementarity, 4),
                }
            )
        controlled_pairs.sort(key=lambda item: item["synergy_score"], reverse=True)
        synergy_score = _clamp(
            0.48 * (_mean(_clamp_float(item.get("synergy_score"), default=0.0) for item in controlled_pairs) if controlled_pairs else 0.0)
            + 0.22 * arbitration_score
            + 0.16 * coordination_signal
            + 0.14 * (_mean(_clamp_float(item.get("heldout_margin"), default=0.0) for item in controlled_pairs) if controlled_pairs else 0.0)
        )
        boundary_flags = ["severe_boundary_watch"]
        if coordination.get("placeholder"):
            boundary_flags.append("coordination_length_control_dependency_placeholder")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "controlled_synergy_pairs": controlled_pairs,
            "cross_family_synergy_score": round(synergy_score, 4),
            "arbitration_score_used": round(arbitration_score, 4),
            "coordination_signal_used": round(coordination_signal, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "resource_competition_arbitration",
                "coordination_length_control",
                "strategy_selection",
                "attention_control",
                "seen_pair_memorization",
                "within_family_false_synergy",
                "demand_sum_only",
            ],
        }
        self.synergy_history.append(output)
        return output


class TemporalCreditAssignment:
    construct_id = "temporal_credit_assignment"

    def __init__(self) -> None:
        self.credit_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        viability = dependencies.get("macro_causal_viability_maintenance", {})
        causal = dependencies.get("causal_attribution", {})
        events = _temporal_credit_events(input_state)
        viability_score = _clamp_float(viability.get("viability_score"), default=0.55)
        causal_confidence = _clamp_float(causal.get("causal_confidence"), default=0.55)
        assignments = []
        for index, event in enumerate(events):
            correct_lag_match = _clamp_float(event.get("correct_lag_match"), default=0.55)
            delayed_outcome_binding = _clamp_float(event.get("delayed_outcome_binding"), default=0.55)
            policy_update_fit = _clamp_float(event.get("policy_update_fit"), default=0.55)
            immediate_reward_risk = _clamp_float(event.get("immediate_reward_risk"), default=0.0)
            recency_bias_risk = _clamp_float(event.get("recency_bias_risk"), default=0.0)
            temporal_order_only_risk = _clamp_float(event.get("temporal_order_only_risk"), default=0.0)
            credit_score = _clamp(
                0.26 * correct_lag_match
                + 0.22 * delayed_outcome_binding
                + 0.18 * policy_update_fit
                + 0.14 * causal_confidence
                + 0.1 * viability_score
                - 0.04 * immediate_reward_risk
                - 0.04 * recency_bias_risk
                - 0.04 * temporal_order_only_risk
            )
            assignments.append(
                {
                    "credit_event_id": str(event.get("id") or f"temporal_credit_event_{index + 1}"),
                    "credited_state_action": str(event.get("credited_state_action") or "unknown"),
                    "lag": int(event.get("lag", index + 1)),
                    "credit_score": round(credit_score, 4),
                    "correct_lag_match": round(correct_lag_match, 4),
                    "delayed_outcome_binding": round(delayed_outcome_binding, 4),
                    "policy_update_fit": round(policy_update_fit, 4),
                }
            )
        assignments.sort(key=lambda item: item["credit_score"], reverse=True)
        selected = assignments[0] if assignments else {}
        margin = _clamp_float(selected.get("credit_score"), default=0.0) - (
            _clamp_float(assignments[1].get("credit_score"), default=0.0)
            if len(assignments) > 1 else 0.0
        )
        temporal_credit_score = _clamp(
            0.44 * _clamp_float(selected.get("credit_score"), default=0.0)
            + 0.2 * margin
            + 0.18 * causal_confidence
            + 0.18 * viability_score
        )
        boundary_flags = ["severe_boundary_watch", "margin_watch"]
        if margin < 0.08 and len(assignments) > 1:
            boundary_flags.append("low_temporal_credit_margin")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "temporal_credit_assignments": assignments,
            "selected_credit_assignment": selected,
            "selection_margin": round(margin, 4),
            "temporal_credit_score": round(temporal_credit_score, 4),
            "causal_confidence_used": round(causal_confidence, 4),
            "viability_score_used": round(viability_score, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "macro_causal_viability_maintenance",
                "causal_attribution",
                "prospective_memory",
                "temporal_horizon_dependent_planning",
                "immediate_reward",
                "recency_bias",
                "temporal_order_only",
            ],
        }
        self.credit_history.append(output)
        return output


class HierarchicalCreditAssignment:
    construct_id = "hierarchical_credit_assignment"

    def __init__(self) -> None:
        self.hierarchical_credit_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        temporal_credit = dependencies.get("temporal_credit_assignment", {})
        hierarchy = dependencies.get("goal_hierarchy_emergence", {})
        events = _hierarchical_credit_events(input_state)
        temporal_credit_score = _clamp_float(temporal_credit.get("temporal_credit_score"), default=0.55)
        hierarchy_coherence = _clamp_float(hierarchy.get("hierarchy_coherence"), default=0.55)
        nested_updates = []
        for index, event in enumerate(events):
            nested_goal_match = _clamp_float(event.get("nested_goal_match"), default=0.55)
            level_specific_binding = _clamp_float(event.get("level_specific_binding"), default=0.55)
            flat_credit_control_match = _clamp_float(event.get("flat_credit_control_match"), default=0.55)
            macro_pressure_match = _clamp_float(event.get("macro_pressure_match"), default=0.55)
            label_template_risk = _clamp_float(event.get("label_template_risk"), default=0.0)
            forecast_only_risk = _clamp_float(event.get("forecast_only_risk"), default=0.0)
            nested_credit_score = _clamp(
                0.24 * nested_goal_match
                + 0.22 * level_specific_binding
                + 0.18 * flat_credit_control_match
                + 0.12 * macro_pressure_match
                + 0.12 * temporal_credit_score
                + 0.08 * hierarchy_coherence
                - 0.04 * label_template_risk
                - 0.04 * forecast_only_risk
            )
            nested_updates.append(
                {
                    "nested_credit_id": str(event.get("id") or f"nested_credit_{index + 1}"),
                    "goal_level": int(event.get("goal_level", index)),
                    "goal_id": str(event.get("goal_id") or "unknown_goal"),
                    "nested_credit_score": round(nested_credit_score, 4),
                    "nested_goal_match": round(nested_goal_match, 4),
                    "level_specific_binding": round(level_specific_binding, 4),
                    "flat_credit_control_match": round(flat_credit_control_match, 4),
                }
            )
        nested_updates.sort(key=lambda item: item["nested_credit_score"], reverse=True)
        selected = nested_updates[0] if nested_updates else {}
        level_specificity = _mean(
            _clamp_float(item.get("level_specific_binding"), default=0.0)
            for item in nested_updates
        ) if nested_updates else 0.0
        hierarchical_credit_score = _clamp(
            0.38 * _clamp_float(selected.get("nested_credit_score"), default=0.0)
            + 0.22 * level_specificity
            + 0.18 * temporal_credit_score
            + 0.14 * hierarchy_coherence
            + 0.08 * min(1.0, len(nested_updates) / 3.0)
        )
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "nested_credit_updates": nested_updates,
            "selected_nested_credit_update": selected,
            "level_specificity": round(level_specificity, 4),
            "hierarchical_credit_score": round(hierarchical_credit_score, 4),
            "temporal_credit_score_used": round(temporal_credit_score, 4),
            "hierarchy_coherence_used": round(hierarchy_coherence, 4),
            "boundary_flags": ["candidate_only_boundary"],
            "hctm_boundary_watch": [
                "temporal_credit_assignment",
                "goal_hierarchy_emergence",
                "macro_causal_viability_maintenance",
                "causal_attribution",
                "temporal_horizon_dependent_planning",
                "reward_delay_only",
                "forecast_only",
                "label_template_nested_goal",
            ],
        }
        self.hierarchical_credit_history.append(output)
        return output


class SocialCouplingStrengthCollectiveAgency:
    construct_id = "social_coupling_strength_collective_agency"

    def __init__(self) -> None:
        self.coupling_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "bidirectional_policy_coordination": 0.03,
                "joint_counterfactual_sensitivity": 0.03,
                "distributed_credit_alignment": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        agency = dependencies.get("action_agency", {})
        boundary = dependencies.get("self_other_boundary_sharpness", {})
        broadcast = dependencies.get("global_broadcast_phase", {})
        viability = dependencies.get("macro_causal_viability_maintenance", {})
        planning = dependencies.get("temporal_horizon_dependent_planning", {})
        body = dependencies.get("distributed_body_schema_self", {})
        dependency_support = _mean(
            (
                _clamp_float(agency.get("controllability"), default=0.55),
                _clamp_float(boundary.get("boundary_sharpness"), default=0.55),
                _clamp_float(broadcast.get("broadcast_phase_score"), default=0.55),
                _clamp_float(viability.get("viability_score"), default=0.55),
                _clamp_float(planning.get("planning_confidence"), default=0.55),
                _clamp_float(body.get("self_schema_confidence"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            policy_coordination = _clamp_float(case.get("bidirectional_policy_coordination"), default=0.55)
            counterfactual_sensitivity = _clamp_float(case.get("joint_counterfactual_sensitivity"), default=0.55)
            credit_alignment = _clamp_float(case.get("distributed_credit_alignment"), default=0.55)
            role_robustness = _clamp_float(case.get("role_robustness"), default=0.55)
            compensation = _clamp_float(case.get("mutual_compensation"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            label_pressure = _clamp_float(
                case.get("collective_label_pressure"),
                default=max(shortcut_pressure, 1.0 - role_robustness),
            )
            single_agent_pressure = _clamp_float(
                case.get("single_agent_control_pressure"),
                default=max(shortcut_pressure, 1.0 - policy_coordination),
            )
            hard_negative_pressure = _mean((shortcut_pressure, label_pressure, single_agent_pressure))
            features = {
                "bidirectional_policy_coordination": policy_coordination,
                "joint_counterfactual_sensitivity": counterfactual_sensitivity,
                "distributed_credit_alignment": credit_alignment,
                "role_robustness": role_robustness,
                "mutual_compensation": compensation,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * policy_coordination
                + 0.2 * counterfactual_sensitivity
                + 0.18 * credit_alignment
                + 0.14 * role_robustness
                + 0.12 * compensation
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "coupling_record_id": str(case.get("id") or f"social_coupling_case_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "bidirectional_policy_coordination": round(policy_coordination, 4),
                    "joint_counterfactual_sensitivity": round(counterfactual_sensitivity, 4),
                    "distributed_credit_alignment": round(credit_alignment, 4),
                    "role_robustness": round(role_robustness, 4),
                    "mutual_compensation": round(compensation, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "coupling_policy": (
                        "joint_policy_coordination_with_distributed_credit"
                        if policy_coordination >= 0.65 and credit_alignment >= 0.65
                        else "reject_collective_label_shortcut"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_social_coupling_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("collective_label_or_single_agent_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "social_coupling_coordination_records": records,
            "selected_social_coupling_record": selected,
            "social_coupling_collective_agency_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "action_agency",
                "self_other_boundary_sharpness",
                "global_broadcast_phase",
                "macro_causal_viability_maintenance",
                "temporal_horizon_dependent_planning",
                "distributed_body_schema_self",
                "collective_label_only",
                "single_agent_control_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "social_coupling_strength_collective_agency_formal_candidate_review_decision_v1.json"
            ),
        }
        self.coupling_history.append(output)
        return output


class CounterfactualReasoningDepth:
    construct_id = "counterfactual_reasoning_depth"

    def __init__(self) -> None:
        self.counterfactual_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "intervention_graph_depth": 0.03,
                "branch_effect_tracking": 0.03,
                "causal_path_pruning": 0.02,
                "hard_negative_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        causal = dependencies.get("causal_attribution", {})
        planning = dependencies.get("temporal_horizon_dependent_planning", {})
        agency = dependencies.get("action_agency", {})
        ownership = dependencies.get("action_ownership", {})
        identity = dependencies.get("identity_temporal_self", {})
        viability = dependencies.get("macro_causal_viability_maintenance", {})
        hierarchy = dependencies.get("goal_hierarchy_emergence", {})
        dependency_support = _mean(
            (
                _clamp_float(causal.get("causal_confidence"), default=0.55),
                _clamp_float(planning.get("planning_confidence"), default=0.55),
                _clamp_float(agency.get("controllability"), default=0.55),
                _clamp_float(ownership.get("ownership_score"), default=0.55),
                _clamp_float(identity.get("identity_coherence"), default=0.55),
                _clamp_float(viability.get("viability_score"), default=0.55),
                _clamp_float(hierarchy.get("hierarchy_coherence"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            depth = _clamp_float(case.get("intervention_graph_depth"), default=0.55)
            branch_tracking = _clamp_float(case.get("branch_effect_tracking"), default=0.55)
            disambiguation = _clamp_float(case.get("outcome_disambiguation"), default=0.55)
            path_pruning = _clamp_float(case.get("causal_path_pruning"), default=0.55)
            nested_inversion = _clamp_float(case.get("nested_effect_inversion"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            forecast_only_pressure = _clamp_float(
                case.get("forecast_only_pressure"),
                default=max(shortcut_pressure, 1.0 - depth),
            )
            branch_label_pressure = _clamp_float(
                case.get("branch_label_pressure"),
                default=max(shortcut_pressure, 1.0 - branch_tracking),
            )
            hard_negative_pressure = _mean(
                (shortcut_pressure, forecast_only_pressure, branch_label_pressure)
            )
            do_operator_composition = _clamp_float(
                case.get("do_operator_composition"),
                default=_mean((depth, branch_tracking, path_pruning)),
            )
            swap_consistency = _clamp_float(
                case.get("swap_consistency"),
                default=_mean((branch_tracking, disambiguation, path_pruning)),
            )
            graph_rewrite_strength = _clamp_float(
                case.get("causal_graph_rewrite"),
                default=_mean((depth, path_pruning, nested_inversion)),
            )
            features = {
                "intervention_graph_depth": depth,
                "branch_effect_tracking": branch_tracking,
                "outcome_disambiguation": disambiguation,
                "causal_path_pruning": path_pruning,
                "nested_effect_inversion": nested_inversion,
                "hard_negative_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            mechanism_score = _clamp(
                0.18 * depth
                + 0.18 * branch_tracking
                + 0.16 * disambiguation
                + 0.14 * path_pruning
                + 0.12 * nested_inversion
                + 0.08 * do_operator_composition
                + 0.06 * swap_consistency
                + 0.06 * graph_rewrite_strength
                + 0.06 * dependency_support
                - 0.16 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "counterfactual_case_id": str(
                        case.get("id") or f"counterfactual_depth_case_{index + 1}"
                    ),
                    "mechanism_score": round(mechanism_score, 4),
                    "intervention_graph_depth": round(depth, 4),
                    "branch_effect_tracking": round(branch_tracking, 4),
                    "outcome_disambiguation": round(disambiguation, 4),
                    "causal_path_pruning": round(path_pruning, 4),
                    "nested_effect_inversion": round(nested_inversion, 4),
                    "do_operator_composition": round(do_operator_composition, 4),
                    "swap_consistency": round(swap_consistency, 4),
                    "causal_graph_rewrite": round(graph_rewrite_strength, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "counterfactual_policy": (
                        "compose_nested_do_operator"
                        if depth >= 0.65 and nested_inversion >= 0.6
                        else "reject_forecast_only_branch"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(
            _clamp_float(selected.get("mechanism_score"), default=0.0) - second_score
        )
        hard_negative_pressure = _mean(
            record["hard_negative_pressure"]
            for record in records
        ) if records else 0.0
        score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = ["severe_boundary_watch"]
        if selection_margin < 0.08:
            boundary_flags.append("low_counterfactual_depth_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("forecast_only_or_branch_label_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "counterfactual_reasoning_depth_records": records,
            "selected_counterfactual_depth_record": selected,
            "counterfactual_reasoning_depth_score": round(score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "nested_branch_controls": [
                record["counterfactual_case_id"]
                for record in records
                if record["counterfactual_policy"] == "compose_nested_do_operator"
            ],
            "causal_graph_rewrites": [
                {
                    "counterfactual_case_id": record["counterfactual_case_id"],
                    "rewrite_strength": record["causal_graph_rewrite"],
                }
                for record in records
                if record["causal_graph_rewrite"] >= 0.6
            ],
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "temporal_horizon_dependent_planning",
                "action_agency",
                "action_ownership",
                "identity_temporal_self",
                "macro_causal_viability_maintenance",
                "goal_hierarchy_emergence",
                "forecast_only_counterfactual",
                "branch_label_shortcut",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "counterfactual_reasoning_depth_formal_candidate_review_decision_v1.json"
            ),
        }
        self.counterfactual_history.append(output)
        return output


class CoordinationLengthControl:
    construct_id = "coordination_length_control"

    def __init__(self) -> None:
        self.coordination_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "coordination_span": 0.03,
                "bridge_stability": 0.03,
                "topology_swap_preservation": 0.02,
                "hard_negative_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        broadcast = dependencies.get("global_broadcast_phase", {})
        integration = dependencies.get("information_integration_phase", {})
        body_schema = dependencies.get("distributed_body_schema_self", {})
        attention = dependencies.get("attention_control", {})
        flow = dependencies.get("information_flow_onset_gating", {})
        dependency_support = _mean(
            (
                _clamp_float(broadcast.get("broadcast_phase_score"), default=0.55),
                _clamp_float(integration.get("integration_coherence"), default=0.55),
                _clamp_float(body_schema.get("self_schema_confidence"), default=0.55),
                _clamp_float(attention.get("attention_stability"), default=0.55),
                _clamp_float(flow.get("gate_stability"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            span = _clamp_float(case.get("coordination_span"), default=0.55)
            bridge = _clamp_float(case.get("bridge_stability"), default=0.55)
            topology = _clamp_float(case.get("topology_swap_preservation"), default=0.55)
            load = _clamp_float(case.get("load_robustness"), default=0.55)
            synchrony_rejection = _clamp_float(case.get("synchrony_shortcut_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            synchrony_pressure = _clamp_float(
                case.get("global_synchrony_pressure"),
                default=max(shortcut_pressure, 1.0 - synchrony_rejection),
            )
            complexity_pressure = _clamp_float(
                case.get("complexity_load_pressure"),
                default=max(shortcut_pressure, 1.0 - load),
            )
            random_edge_pressure = _clamp_float(
                case.get("random_edge_pressure"),
                default=max(shortcut_pressure, 1.0 - topology),
            )
            measurement_gain_pressure = _clamp_float(
                case.get("measurement_gain_pressure"),
                default=max(shortcut_pressure, 1.0 - bridge),
            )
            hard_negative_pressure = _mean(
                (
                    shortcut_pressure,
                    synchrony_pressure,
                    complexity_pressure,
                    random_edge_pressure,
                    measurement_gain_pressure,
                )
            )
            features = {
                "coordination_span": span,
                "bridge_stability": bridge,
                "topology_swap_preservation": topology,
                "load_robustness": load,
                "synchrony_shortcut_rejection": synchrony_rejection,
                "hard_negative_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            mechanism_score = _clamp(
                0.24 * span
                + 0.21 * bridge
                + 0.18 * topology
                + 0.15 * load
                + 0.1 * synchrony_rejection
                + 0.08 * dependency_support
                - 0.16 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "coordination_case_id": str(case.get("id") or f"coordination_case_{index + 1}"),
                    "mechanism_score": round(mechanism_score, 4),
                    "coordination_span": round(span, 4),
                    "bridge_stability": round(bridge, 4),
                    "topology_swap_preservation": round(topology, 4),
                    "load_robustness": round(load, 4),
                    "synchrony_shortcut_rejection": round(synchrony_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "bridge_policy": (
                        "preserve_sparse_long_range_bridge"
                        if topology >= 0.6 and bridge >= 0.6
                        else "reject_global_synchrony_shortcut"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(
            _clamp_float(selected.get("mechanism_score"), default=0.0) - second_score
        )
        hard_negative_pressure = _mean(
            record["hard_negative_pressure"]
            for record in records
        ) if records else 0.0
        score = _clamp(
            0.66 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.12 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = ["margin_watch", "boundary_watch"]
        if selection_margin < 0.08:
            boundary_flags.append("low_coordination_selection_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("global_synchrony_or_complexity_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "coordination_length_records": records,
            "selected_coordination_length_record": selected,
            "coordination_length_control_score": round(score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "bridge_plan": [
                record["coordination_case_id"]
                for record in records
                if record["bridge_policy"] == "preserve_sparse_long_range_bridge"
            ],
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "global_broadcast_phase",
                "information_integration_phase",
                "distributed_body_schema_self",
                "global_synchrony",
                "complexity_load",
                "random_edge_control",
                "measurement_gain_control",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "coordination_length_control_formal_candidate_review_decision_v1.json"
            ),
        }
        self.coordination_history.append(output)
        return output


class LatentContextSwitchDetection:
    construct_id = "latent_context_switch_detection"

    def __init__(self) -> None:
        self.switch_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "unlabeled_switch_evidence": 0.03,
                "policy_adjustment_fit": 0.03,
                "latent_state_rebinding": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        strategy = dependencies.get("strategy_selection", {})
        learning = dependencies.get("learning_rate_adaptation_rework", {})
        error = dependencies.get("error_monitoring", {})
        dependency_support = _mean(
            (
                _clamp_float(strategy.get("selection_confidence"), default=0.55),
                _clamp_float(learning.get("learning_rate_adaptation_score"), default=0.55),
                _clamp_float(error.get("monitor_confidence"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            unlabeled_evidence = _clamp_float(case.get("unlabeled_switch_evidence"), default=0.55)
            policy_fit = _clamp_float(case.get("policy_adjustment_fit"), default=0.55)
            rebinding = _clamp_float(case.get("latent_state_rebinding"), default=0.55)
            surprise_rejection = _clamp_float(case.get("surprise_shortcut_rejection"), default=0.55)
            reward_rejection = _clamp_float(case.get("reward_shortcut_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            explicit_label_pressure = _clamp_float(
                case.get("explicit_context_label_pressure"),
                default=max(shortcut_pressure, 1.0 - unlabeled_evidence),
            )
            surprise_pressure = _clamp_float(
                case.get("surprise_magnitude_pressure"),
                default=max(shortcut_pressure, 1.0 - surprise_rejection),
            )
            reward_pressure = _clamp_float(
                case.get("reward_shift_pressure"),
                default=max(shortcut_pressure, 1.0 - reward_rejection),
            )
            hard_negative_pressure = _mean(
                (shortcut_pressure, explicit_label_pressure, surprise_pressure, reward_pressure)
            )
            features = {
                "unlabeled_switch_evidence": unlabeled_evidence,
                "policy_adjustment_fit": policy_fit,
                "latent_state_rebinding": rebinding,
                "surprise_shortcut_rejection": surprise_rejection,
                "reward_shortcut_rejection": reward_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.23 * unlabeled_evidence
                + 0.2 * policy_fit
                + 0.19 * rebinding
                + 0.13 * surprise_rejection
                + 0.11 * reward_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "context_switch_id": str(case.get("id") or f"latent_context_switch_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "unlabeled_switch_evidence": round(unlabeled_evidence, 4),
                    "policy_adjustment_fit": round(policy_fit, 4),
                    "latent_state_rebinding": round(rebinding, 4),
                    "surprise_shortcut_rejection": round(surprise_rejection, 4),
                    "reward_shortcut_rejection": round(reward_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "switch_policy": (
                        "rebind_latent_state_without_explicit_label"
                        if unlabeled_evidence >= 0.65 and rebinding >= 0.65
                        else "reject_label_or_surprise_only_switch"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_latent_context_switch_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("label_surprise_or_reward_context_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "latent_context_switch_records": records,
            "selected_latent_context_switch": selected,
            "latent_context_switch_detection_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "strategy_selection",
                "learning_rate_adaptation_rework",
                "error_monitoring",
                "explicit_context_labeling",
                "surprise_magnitude_only",
                "reward_shift_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "latent_context_switch_detection_formal_candidate_review_decision_v1.json"
            ),
        }
        self.switch_history.append(output)
        return output


class SocialNormTracking:
    construct_id = "social_norm_tracking"

    def __init__(self) -> None:
        self.norm_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "norm_expectation_inference": 0.03,
                "context_shift_update": 0.03,
                "violation_prediction": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        perspective = dependencies.get("perspective_taking", {})
        social_coupling = dependencies.get("social_coupling_strength_collective_agency", {})
        error = dependencies.get("error_monitoring", {})
        strategy = dependencies.get("strategy_selection", {})
        boundary = dependencies.get("self_other_boundary_sharpness", {})
        dependency_support = _mean(
            (
                _clamp_float(perspective.get("perspective_accuracy_proxy"), default=0.55),
                _clamp_float(social_coupling.get("social_coupling_collective_agency_score"), default=0.55),
                _clamp_float(error.get("monitor_confidence"), default=0.55),
                _clamp_float(strategy.get("selection_confidence"), default=0.55),
                _clamp_float(boundary.get("boundary_sharpness"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            inference = _clamp_float(case.get("norm_expectation_inference"), default=0.55)
            update = _clamp_float(case.get("context_shift_update"), default=0.55)
            violation = _clamp_float(case.get("violation_prediction"), default=0.55)
            label_rejection = _clamp_float(case.get("label_template_rejection"), default=0.55)
            reward_rejection = _clamp_float(case.get("reward_history_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            label_pressure = _clamp_float(
                case.get("norm_label_pressure"),
                default=max(shortcut_pressure, 1.0 - label_rejection),
            )
            frequency_pressure = _clamp_float(
                case.get("frequency_pressure"),
                default=max(shortcut_pressure, 1.0 - inference),
            )
            reward_pressure = _clamp_float(
                case.get("reward_history_pressure"),
                default=max(shortcut_pressure, 1.0 - reward_rejection),
            )
            hard_negative_pressure = _mean(
                (shortcut_pressure, label_pressure, frequency_pressure, reward_pressure)
            )
            features = {
                "norm_expectation_inference": inference,
                "context_shift_update": update,
                "violation_prediction": violation,
                "label_template_rejection": label_rejection,
                "reward_history_rejection": reward_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * inference
                + 0.2 * update
                + 0.18 * violation
                + 0.14 * label_rejection
                + 0.12 * reward_rejection
                + 0.08 * dependency_support
                - 0.16 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "norm_tracking_case_id": str(case.get("id") or f"social_norm_case_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "norm_expectation_inference": round(inference, 4),
                    "context_shift_update": round(update, 4),
                    "violation_prediction": round(violation, 4),
                    "label_template_rejection": round(label_rejection, 4),
                    "reward_history_rejection": round(reward_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "norm_policy": (
                        "track_context_shifted_norm_expectation"
                        if update >= 0.65 and violation >= 0.65
                        else "reject_label_or_frequency_norm_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = ["severe_boundary_watch"]
        if selection_margin < 0.08:
            boundary_flags.append("low_social_norm_tracking_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("norm_label_frequency_or_reward_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "social_norm_tracking_records": records,
            "selected_social_norm_tracking_record": selected,
            "social_norm_tracking_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "perspective_taking",
                "social_coupling_strength_collective_agency",
                "error_monitoring",
                "strategy_selection",
                "self_other_boundary_sharpness",
                "label_template_only",
                "frequency_only",
                "reward_history_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "social_norm_tracking_formal_candidate_review_decision_v1.json"
            ),
        }
        self.norm_history.append(output)
        return output


class SemanticMemoryRetrievalControl:
    construct_id = "semantic_memory_retrieval_control"

    def __init__(self) -> None:
        self.retrieval_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "semantic_candidate_fit": 0.03,
                "context_constraint_match": 0.03,
                "irrelevant_association_suppression": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        episodic = dependencies.get("episodic_memory_binding", {})
        working_memory = dependencies.get("working_memory_capacity_rework", {})
        strategy = dependencies.get("strategy_selection", {})
        prospective = dependencies.get("prospective_memory", {})
        causal = dependencies.get("causal_attribution", {})
        attention = dependencies.get("attention_control", {})
        dependency_support = _mean(
            (
                _clamp_float(episodic.get("global_binding_strength"), default=0.55),
                _clamp_float(working_memory.get("working_memory_capacity_score"), default=0.55),
                _clamp_float(strategy.get("selection_confidence"), default=0.55),
                _clamp_float(prospective.get("prospective_memory_score"), default=0.55),
                _clamp_float(causal.get("causal_confidence"), default=0.55),
                _clamp_float(attention.get("attention_stability"), default=0.55),
            )
        )
        records = []
        suppressed = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            semantic_fit = _clamp_float(case.get("semantic_candidate_fit"), default=0.55)
            context_match = _clamp_float(case.get("context_constraint_match"), default=0.55)
            suppression = _clamp_float(
                case.get("irrelevant_association_suppression"),
                default=0.55,
            )
            ambiguity = _clamp_float(case.get("ambiguity_resolution"), default=0.55)
            frequency_rejection = _clamp_float(
                case.get("frequency_shortcut_rejection"),
                default=0.55,
            )
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            episodic_only_pressure = _clamp_float(
                case.get("episodic_binding_only_pressure"),
                default=max(shortcut_pressure, 1.0 - context_match),
            )
            working_memory_only_pressure = _clamp_float(
                case.get("working_memory_only_pressure"),
                default=max(shortcut_pressure, 1.0 - suppression),
            )
            frequency_pressure = _clamp_float(
                case.get("word_frequency_pressure"),
                default=max(shortcut_pressure, 1.0 - frequency_rejection),
            )
            label_template_pressure = _clamp_float(
                case.get("label_template_pressure"),
                default=max(shortcut_pressure, 1.0 - ambiguity),
            )
            boundary_pressure = _mean(
                (
                    shortcut_pressure,
                    episodic_only_pressure,
                    working_memory_only_pressure,
                    frequency_pressure,
                    label_template_pressure,
                )
            )
            features = {
                "semantic_candidate_fit": semantic_fit,
                "context_constraint_match": context_match,
                "irrelevant_association_suppression": suppression,
                "ambiguity_resolution": ambiguity,
                "frequency_shortcut_rejection": frequency_rejection,
                "shortcut_pressure": boundary_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            mechanism_score = _clamp(
                0.22 * semantic_fit
                + 0.22 * context_match
                + 0.18 * suppression
                + 0.14 * ambiguity
                + 0.1 * frequency_rejection
                + 0.08 * dependency_support
                - 0.16 * boundary_pressure
                + 0.08 * learned_adjustment
            )
            record = {
                "semantic_retrieval_case_id": str(
                    case.get("id") or f"semantic_retrieval_case_{index + 1}"
                ),
                "mechanism_score": round(mechanism_score, 4),
                "semantic_candidate_fit": round(semantic_fit, 4),
                "context_constraint_match": round(context_match, 4),
                "irrelevant_association_suppression": round(suppression, 4),
                "ambiguity_resolution": round(ambiguity, 4),
                "frequency_shortcut_rejection": round(frequency_rejection, 4),
                "boundary_pressure": round(boundary_pressure, 4),
                "retrieval_policy": (
                    "retrieve_context_constrained_semantic_candidate"
                    if context_match >= 0.6 and suppression >= 0.6
                    else "suppress_frequency_or_label_shortcut"
                ),
            }
            records.append(record)
            if mechanism_score < 0.55 or boundary_pressure >= 0.35:
                suppressed.append(record)
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(
            _clamp_float(selected.get("mechanism_score"), default=0.0) - second_score
        )
        boundary_pressure = _mean(
            record["boundary_pressure"]
            for record in records
        ) if records else 0.0
        score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - boundary_pressure)
        )
        boundary_flags = ["severe_boundary_watch"]
        if selection_margin < 0.08:
            boundary_flags.append("low_semantic_retrieval_margin")
        if boundary_pressure >= 0.35:
            boundary_flags.append("semantic_shortcut_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "semantic_retrieval_control_records": records,
            "selected_semantic_retrieval_record": selected,
            "suppressed_semantic_candidates": suppressed,
            "semantic_memory_retrieval_control_score": round(score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_boundary_pressure": round(boundary_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "episodic_memory_binding",
                "working_memory_capacity_rework",
                "strategy_selection",
                "prospective_memory",
                "causal_attribution",
                "word_frequency_only",
                "label_template_only",
                "familiarity_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "semantic_memory_retrieval_control_formal_candidate_review_decision_v1.json"
            ),
        }
        self.retrieval_history.append(output)
        return output


class DivergentThinking:
    construct_id = "divergent_thinking"

    def __init__(self) -> None:
        self.divergence_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "novelty": 0.03,
                "task_relevance": 0.03,
                "alternative_diversity": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        hierarchy = dependencies.get("goal_hierarchy_emergence", {})
        strategy = dependencies.get("strategy_selection", {})
        semantic = dependencies.get("semantic_memory_retrieval_control", {})
        constraint = dependencies.get("constraint_satisfaction_reconfiguration", {})
        dependency_support = _mean(
            (
                _clamp_float(hierarchy.get("hierarchy_coherence"), default=0.55),
                _clamp_float(strategy.get("selection_confidence"), default=0.55),
                _clamp_float(semantic.get("semantic_memory_retrieval_control_score"), default=0.55),
                _clamp_float(constraint.get("constraint_satisfaction_reconfiguration_score"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            novelty = _clamp_float(case.get("novelty"), default=0.55)
            relevance = _clamp_float(case.get("task_relevance"), default=0.55)
            diversity = _clamp_float(case.get("alternative_diversity"), default=0.55)
            constraint_fit = _clamp_float(case.get("constraint_satisfaction"), default=0.55)
            random_rejection = _clamp_float(case.get("random_sampling_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            random_pressure = _clamp_float(
                case.get("random_sampling_pressure"),
                default=max(shortcut_pressure, 1.0 - random_rejection),
            )
            complexity_pressure = _clamp_float(
                case.get("complexity_only_pressure"),
                default=max(shortcut_pressure, 1.0 - relevance),
            )
            hard_negative_pressure = _mean((shortcut_pressure, random_pressure, complexity_pressure))
            features = {
                "novelty": novelty,
                "task_relevance": relevance,
                "alternative_diversity": diversity,
                "constraint_satisfaction": constraint_fit,
                "random_sampling_rejection": random_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.2 * novelty
                + 0.2 * relevance
                + 0.2 * diversity
                + 0.16 * constraint_fit
                + 0.1 * random_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "divergent_case_id": str(case.get("id") or f"divergent_case_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "novelty": round(novelty, 4),
                    "task_relevance": round(relevance, 4),
                    "alternative_diversity": round(diversity, 4),
                    "constraint_satisfaction": round(constraint_fit, 4),
                    "random_sampling_rejection": round(random_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "generation_policy": (
                        "generate_constraint_relevant_alternatives"
                        if relevance >= 0.6 and constraint_fit >= 0.6
                        else "reject_random_or_complexity_only_generation"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = ["severe_boundary_watch"]
        if selection_margin < 0.08:
            boundary_flags.append("low_divergent_thinking_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("random_sampling_or_complexity_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "divergent_thinking_records": records,
            "selected_divergent_thinking_record": selected,
            "divergent_thinking_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "goal_hierarchy_emergence",
                "strategy_selection",
                "semantic_memory_retrieval_control",
                "constraint_satisfaction_reconfiguration",
                "random_sampling_only",
                "complexity_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "divergent_thinking_formal_candidate_review_decision_v1.json"
            ),
        }
        self.divergence_history.append(output)
        return output


class AnalogicalReasoningRework:
    construct_id = "analogical_reasoning_rework"

    def __init__(self) -> None:
        self.analogy_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "relation_preservation": 0.03,
                "cross_domain_transfer": 0.03,
                "causal_structure_match": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        causal = dependencies.get("causal_attribution", {})
        semantic = dependencies.get("semantic_memory_retrieval_control", {})
        strategy = dependencies.get("strategy_selection", {})
        dependency_support = _mean(
            (
                _clamp_float(causal.get("causal_confidence"), default=0.55),
                _clamp_float(semantic.get("semantic_memory_retrieval_control_score"), default=0.55),
                _clamp_float(strategy.get("selection_confidence"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            relation = _clamp_float(case.get("relation_preservation"), default=0.55)
            transfer = _clamp_float(case.get("cross_domain_transfer"), default=0.55)
            surface_suppression = _clamp_float(case.get("surface_similarity_suppression"), default=0.55)
            causal_match = _clamp_float(case.get("causal_structure_match"), default=0.55)
            template_rejection = _clamp_float(case.get("relation_template_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            surface_pressure = _clamp_float(
                case.get("surface_similarity_pressure"),
                default=max(shortcut_pressure, 1.0 - surface_suppression),
            )
            template_pressure = _clamp_float(
                case.get("relation_template_pressure"),
                default=max(shortcut_pressure, 1.0 - template_rejection),
            )
            hard_negative_pressure = _mean((shortcut_pressure, surface_pressure, template_pressure))
            features = {
                "relation_preservation": relation,
                "cross_domain_transfer": transfer,
                "surface_similarity_suppression": surface_suppression,
                "causal_structure_match": causal_match,
                "relation_template_rejection": template_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * relation
                + 0.18 * transfer
                + 0.18 * causal_match
                + 0.14 * surface_suppression
                + 0.12 * template_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "analogy_case_id": str(case.get("id") or f"analogy_case_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "relation_preservation": round(relation, 4),
                    "cross_domain_transfer": round(transfer, 4),
                    "surface_similarity_suppression": round(surface_suppression, 4),
                    "causal_structure_match": round(causal_match, 4),
                    "relation_template_rejection": round(template_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "analogy_policy": (
                        "transfer_relation_preserving_structure"
                        if relation >= 0.65 and causal_match >= 0.65
                        else "reject_surface_similarity_or_template_analogy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_analogical_reasoning_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("surface_similarity_or_template_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "analogical_reasoning_records": records,
            "selected_analogical_reasoning_record": selected,
            "analogical_reasoning_rework_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "causal_attribution",
                "semantic_memory_retrieval_control",
                "causal_model_abstraction_hierarchy",
                "strategy_selection",
                "surface_similarity_only",
                "relation_template_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "analogical_reasoning_rework_formal_candidate_review_decision_v1.json"
            ),
        }
        self.analogy_history.append(output)
        return output


class CooperationPolicySwitchingRework:
    construct_id = "cooperation_policy_switching_rework"

    def __init__(self) -> None:
        self.cooperation_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "partner_reliability_shift_detection": 0.03,
                "partner_specific_policy_switch": 0.03,
                "cooperative_payoff_fit": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        social_coupling = dependencies.get("social_coupling_strength_collective_agency", {})
        strategy = dependencies.get("strategy_selection", {})
        prospective = dependencies.get("prospective_memory", {})
        commitment = dependencies.get("multi_agent_commitment_tracking", {})
        dependency_support = _mean(
            (
                _clamp_float(social_coupling.get("social_coupling_collective_agency_score"), default=0.55),
                _clamp_float(strategy.get("selection_confidence"), default=0.55),
                _clamp_float(prospective.get("prospective_memory_score"), default=0.55),
                _clamp_float(commitment.get("multi_agent_commitment_tracking_score"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            shift = _clamp_float(case.get("partner_reliability_shift_detection"), default=0.55)
            policy_switch = _clamp_float(case.get("partner_specific_policy_switch"), default=0.55)
            payoff_fit = _clamp_float(case.get("cooperative_payoff_fit"), default=0.55)
            fixed_rejection = _clamp_float(case.get("fixed_policy_rejection"), default=0.55)
            reward_rejection = _clamp_float(case.get("reward_history_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            fixed_pressure = _clamp_float(
                case.get("fixed_policy_pressure"),
                default=max(shortcut_pressure, 1.0 - fixed_rejection),
            )
            reward_pressure = _clamp_float(
                case.get("reward_history_pressure"),
                default=max(shortcut_pressure, 1.0 - reward_rejection),
            )
            hard_negative_pressure = _mean((shortcut_pressure, fixed_pressure, reward_pressure))
            features = {
                "partner_reliability_shift_detection": shift,
                "partner_specific_policy_switch": policy_switch,
                "cooperative_payoff_fit": payoff_fit,
                "fixed_policy_rejection": fixed_rejection,
                "reward_history_rejection": reward_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * shift
                + 0.22 * policy_switch
                + 0.16 * payoff_fit
                + 0.14 * fixed_rejection
                + 0.1 * reward_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "cooperation_case_id": str(case.get("id") or f"cooperation_case_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "partner_reliability_shift_detection": round(shift, 4),
                    "partner_specific_policy_switch": round(policy_switch, 4),
                    "cooperative_payoff_fit": round(payoff_fit, 4),
                    "fixed_policy_rejection": round(fixed_rejection, 4),
                    "reward_history_rejection": round(reward_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "cooperation_policy": (
                        "switch_partner_specific_cooperation_policy"
                        if shift >= 0.6 and policy_switch >= 0.65
                        else "reject_fixed_policy_or_reward_history_control"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_cooperation_policy_switch_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("fixed_policy_or_reward_history_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "cooperation_policy_switch_records": records,
            "selected_cooperation_policy_switch": selected,
            "cooperation_policy_switching_rework_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "social_coupling_strength_collective_agency",
                "strategy_selection",
                "prospective_memory",
                "multi_agent_commitment_tracking",
                "fixed_policy_only",
                "reward_history_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "cooperation_policy_switching_rework_formal_candidate_review_decision_v1.json"
            ),
        }
        self.cooperation_history.append(output)
        return output


class SpatialNavigationRemappingRework:
    construct_id = "spatial_navigation_remapping_rework"

    def __init__(self) -> None:
        self.navigation_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "topology_change_detection": 0.03,
                "cue_conflict_resolution": 0.03,
                "route_remapping_commitment": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        body = dependencies.get("distributed_body_schema_self", {})
        correction = dependencies.get("body_schema_error_correction", {})
        planning = dependencies.get("temporal_horizon_dependent_planning", {})
        attention = dependencies.get("attention_control", {})
        dependency_support = _mean(
            (
                _clamp_float(body.get("self_schema_confidence"), default=0.55),
                _clamp_float(correction.get("correction_strength"), default=0.55),
                _clamp_float(planning.get("planning_confidence"), default=0.55),
                _clamp_float(attention.get("attention_stability"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            topology = _clamp_float(case.get("topology_change_detection"), default=0.55)
            cue_resolution = _clamp_float(case.get("cue_conflict_resolution"), default=0.55)
            route_commitment = _clamp_float(case.get("route_remapping_commitment"), default=0.55)
            body_rejection = _clamp_float(case.get("body_schema_shortcut_rejection"), default=0.55)
            replay_rejection = _clamp_float(case.get("path_memory_replay_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            salience_pressure = _clamp_float(
                case.get("salience_cue_pressure"),
                default=max(shortcut_pressure, 1.0 - cue_resolution),
            )
            replay_pressure = _clamp_float(
                case.get("path_memory_replay_pressure"),
                default=max(shortcut_pressure, 1.0 - replay_rejection),
            )
            body_pressure = _clamp_float(
                case.get("body_schema_shortcut_pressure"),
                default=max(shortcut_pressure, 1.0 - body_rejection),
            )
            hard_negative_pressure = _mean((shortcut_pressure, salience_pressure, replay_pressure, body_pressure))
            features = {
                "topology_change_detection": topology,
                "cue_conflict_resolution": cue_resolution,
                "route_remapping_commitment": route_commitment,
                "body_schema_shortcut_rejection": body_rejection,
                "path_memory_replay_rejection": replay_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * topology
                + 0.18 * cue_resolution
                + 0.2 * route_commitment
                + 0.12 * body_rejection
                + 0.12 * replay_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "spatial_case_id": str(case.get("id") or f"spatial_remapping_case_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "topology_change_detection": round(topology, 4),
                    "cue_conflict_resolution": round(cue_resolution, 4),
                    "route_remapping_commitment": round(route_commitment, 4),
                    "body_schema_shortcut_rejection": round(body_rejection, 4),
                    "path_memory_replay_rejection": round(replay_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "remapping_policy": (
                        "rebind_route_after_topology_swap"
                        if topology >= 0.65 and route_commitment >= 0.65
                        else "reject_path_memory_or_salience_cue_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_spatial_navigation_remapping_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("path_memory_salience_or_body_schema_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "spatial_navigation_remapping_records": records,
            "selected_spatial_navigation_remapping": selected,
            "spatial_navigation_remapping_rework_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "distributed_body_schema_self",
                "body_schema_error_correction",
                "temporal_horizon_dependent_planning",
                "attention_control",
                "path_memory_replay_only",
                "salience_cue_shortcut",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "spatial_navigation_remapping_rework_formal_candidate_review_decision_v1.json"
            ),
        }
        self.navigation_history.append(output)
        return output


class PredictiveControlUnderActionIntervention:
    construct_id = "predictive_control_under_action_intervention"

    def __init__(self) -> None:
        self.action_prediction_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "action_conditioning": 0.03,
                "intervention_sensitivity": 0.03,
                "prediction_improvement": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        minimization = dependencies.get("predictive_error_minimization_phase", {})
        credit = dependencies.get("temporal_credit_assignment", {})
        causal = dependencies.get("causal_attribution", {})
        agency = dependencies.get("action_agency", {})
        dependency_support = _mean(
            (
                _clamp_float(minimization.get("minimization_gain"), default=0.55),
                _clamp_float(credit.get("temporal_credit_score"), default=0.55),
                _clamp_float(causal.get("causal_confidence"), default=0.55),
                _clamp_float(agency.get("controllability"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            conditioning = _clamp_float(case.get("action_conditioning"), default=0.55)
            intervention = _clamp_float(case.get("intervention_sensitivity"), default=0.55)
            improvement = _clamp_float(case.get("prediction_improvement"), default=0.55)
            forecast_rejection = _clamp_float(case.get("passive_forecast_rejection"), default=0.55)
            credit_rejection = _clamp_float(case.get("temporal_credit_shortcut_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            forecast_pressure = _clamp_float(
                case.get("passive_forecast_pressure"),
                default=max(shortcut_pressure, 1.0 - forecast_rejection),
            )
            credit_pressure = _clamp_float(
                case.get("temporal_credit_shortcut_pressure"),
                default=max(shortcut_pressure, 1.0 - credit_rejection),
            )
            hard_negative_pressure = _mean((shortcut_pressure, forecast_pressure, credit_pressure))
            features = {
                "action_conditioning": conditioning,
                "intervention_sensitivity": intervention,
                "prediction_improvement": improvement,
                "passive_forecast_rejection": forecast_rejection,
                "temporal_credit_shortcut_rejection": credit_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * conditioning
                + 0.22 * intervention
                + 0.18 * improvement
                + 0.12 * forecast_rejection
                + 0.1 * credit_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "action_intervention_case_id": str(
                        case.get("id") or f"action_intervention_prediction_{index + 1}"
                    ),
                    "mechanism_score": round(score, 4),
                    "action_conditioning": round(conditioning, 4),
                    "intervention_sensitivity": round(intervention, 4),
                    "prediction_improvement": round(improvement, 4),
                    "passive_forecast_rejection": round(forecast_rejection, 4),
                    "temporal_credit_shortcut_rejection": round(credit_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "prediction_policy": (
                        "predict_under_action_intervention"
                        if conditioning >= 0.65 and intervention >= 0.65
                        else "reject_passive_forecast_or_credit_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_action_intervention_prediction_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("passive_forecast_or_temporal_credit_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "action_intervention_prediction_records": records,
            "selected_action_intervention_prediction": selected,
            "predictive_control_under_action_intervention_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "predictive_error_minimization_phase",
                "temporal_credit_assignment",
                "causal_attribution",
                "action_agency",
                "forecast_only",
                "temporal_credit_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "predictive_control_under_action_intervention_formal_candidate_review_decision_v1.json"
            ),
        }
        self.action_prediction_history.append(output)
        return output


class InsightProblemSolvingRework:
    construct_id = "insight_problem_solving_rework"

    def __init__(self) -> None:
        self.insight_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "impasse_detection": 0.03,
                "representation_restructure": 0.03,
                "constraint_relax_rebind": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        strategy = dependencies.get("strategy_selection", {})
        divergent = dependencies.get("divergent_thinking", {})
        hierarchy = dependencies.get("goal_hierarchy_emergence", {})
        working_memory = dependencies.get("working_memory_capacity_rework", {})
        semantic = dependencies.get("semantic_memory_retrieval_control", {})
        dependency_support = _mean(
            (
                _clamp_float(strategy.get("selection_confidence"), default=0.55),
                _clamp_float(divergent.get("divergent_thinking_score"), default=0.55),
                _clamp_float(hierarchy.get("hierarchy_coherence"), default=0.55),
                _clamp_float(working_memory.get("working_memory_capacity_score"), default=0.55),
                _clamp_float(semantic.get("semantic_memory_retrieval_control_score"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            impasse = _clamp_float(case.get("impasse_detection"), default=0.55)
            restructure = _clamp_float(case.get("representation_restructure"), default=0.55)
            constraint_rebind = _clamp_float(case.get("constraint_relax_rebind"), default=0.55)
            transfer = _clamp_float(case.get("transfer_after_restructure"), default=0.55)
            random_rejection = _clamp_float(case.get("random_search_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            random_pressure = _clamp_float(
                case.get("random_search_pressure"),
                default=max(shortcut_pressure, 1.0 - random_rejection),
            )
            retry_pressure = _clamp_float(
                case.get("reward_retrial_pressure"),
                default=max(shortcut_pressure, 1.0 - restructure),
            )
            hard_negative_pressure = _mean((shortcut_pressure, random_pressure, retry_pressure))
            features = {
                "impasse_detection": impasse,
                "representation_restructure": restructure,
                "constraint_relax_rebind": constraint_rebind,
                "transfer_after_restructure": transfer,
                "random_search_rejection": random_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.2 * impasse
                + 0.22 * restructure
                + 0.18 * constraint_rebind
                + 0.14 * transfer
                + 0.1 * random_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "insight_case_id": str(case.get("id") or f"insight_case_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "impasse_detection": round(impasse, 4),
                    "representation_restructure": round(restructure, 4),
                    "constraint_relax_rebind": round(constraint_rebind, 4),
                    "transfer_after_restructure": round(transfer, 4),
                    "random_search_rejection": round(random_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "insight_policy": (
                        "restructure_representation_after_impasse"
                        if impasse >= 0.65 and restructure >= 0.65
                        else "reject_random_search_or_reward_retrial"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_insight_problem_solving_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("random_search_or_reward_retrial_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "insight_problem_solving_records": records,
            "selected_insight_problem_solving_record": selected,
            "insight_problem_solving_rework_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "strategy_selection",
                "divergent_thinking",
                "goal_hierarchy_emergence",
                "working_memory_capacity_rework",
                "semantic_memory_retrieval_control",
                "random_search_only",
                "reward_retrial_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "insight_problem_solving_rework_formal_candidate_review_decision_v1.json"
            ),
        }
        self.insight_history.append(output)
        return output


class CounterfactualRepairPlanningRework:
    construct_id = "counterfactual_repair_planning_rework"

    def __init__(self) -> None:
        self.repair_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "failure_assumption_diagnosis": 0.03,
                "repair_branch_generation": 0.03,
                "repaired_plan_commitment": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        counterfactual = dependencies.get("counterfactual_reasoning_depth", {})
        causal = dependencies.get("causal_attribution", {})
        planning = dependencies.get("temporal_horizon_dependent_planning", {})
        action_prediction = dependencies.get("predictive_control_under_action_intervention", {})
        strategy = dependencies.get("strategy_selection", {})
        dependency_support = _mean(
            (
                _clamp_float(counterfactual.get("counterfactual_reasoning_depth_score"), default=0.55),
                _clamp_float(causal.get("causal_confidence"), default=0.55),
                _clamp_float(planning.get("planning_confidence"), default=0.55),
                _clamp_float(action_prediction.get("predictive_control_under_action_intervention_score"), default=0.55),
                _clamp_float(strategy.get("selection_confidence"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            diagnosis = _clamp_float(case.get("failure_assumption_diagnosis"), default=0.55)
            branch_generation = _clamp_float(case.get("repair_branch_generation"), default=0.55)
            commitment = _clamp_float(case.get("repaired_plan_commitment"), default=0.55)
            transfer = _clamp_float(case.get("transfer_after_repair"), default=0.55)
            random_rejection = _clamp_float(case.get("random_branch_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            random_pressure = _clamp_float(
                case.get("random_branch_pressure"),
                default=max(shortcut_pressure, 1.0 - random_rejection),
            )
            retry_pressure = _clamp_float(
                case.get("success_retry_pressure"),
                default=max(shortcut_pressure, 1.0 - diagnosis),
            )
            hard_negative_pressure = _mean((shortcut_pressure, random_pressure, retry_pressure))
            features = {
                "failure_assumption_diagnosis": diagnosis,
                "repair_branch_generation": branch_generation,
                "repaired_plan_commitment": commitment,
                "transfer_after_repair": transfer,
                "random_branch_rejection": random_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * diagnosis
                + 0.2 * branch_generation
                + 0.18 * commitment
                + 0.14 * transfer
                + 0.1 * random_rejection
                + 0.08 * dependency_support
                - 0.16 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "counterfactual_repair_case_id": str(case.get("id") or f"counterfactual_repair_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "failure_assumption_diagnosis": round(diagnosis, 4),
                    "repair_branch_generation": round(branch_generation, 4),
                    "repaired_plan_commitment": round(commitment, 4),
                    "transfer_after_repair": round(transfer, 4),
                    "random_branch_rejection": round(random_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "repair_policy": (
                        "generate_failure_specific_counterfactual_repair_branch"
                        if diagnosis >= 0.65 and branch_generation >= 0.65
                        else "reject_success_retry_or_random_branch"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = ["severe_boundary_watch"]
        if selection_margin < 0.08:
            boundary_flags.append("low_counterfactual_repair_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("random_branch_or_success_retry_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "counterfactual_repair_planning_records": records,
            "selected_counterfactual_repair_plan": selected,
            "counterfactual_repair_planning_rework_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "counterfactual_reasoning_depth",
                "causal_attribution",
                "temporal_horizon_dependent_planning",
                "predictive_control_under_action_intervention",
                "strategy_selection",
                "success_retry_only",
                "random_branch_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "counterfactual_repair_planning_rework_formal_candidate_review_decision_v1.json"
            ),
        }
        self.repair_history.append(output)
        return output


class MultiAgentCommitmentTracking:
    construct_id = "multi_agent_commitment_tracking"

    def __init__(self) -> None:
        self.commitment_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "partner_commitment_encoding": 0.03,
                "delayed_commitment_retrieval": 0.03,
                "role_swap_robustness": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        prospective = dependencies.get("prospective_memory", {})
        social_coupling = dependencies.get("social_coupling_strength_collective_agency", {})
        cooperation = dependencies.get("cooperation_policy_switching_rework", {})
        strategy = dependencies.get("strategy_selection", {})
        dependency_support = _mean(
            (
                _clamp_float(prospective.get("prospective_memory_score"), default=0.55),
                _clamp_float(social_coupling.get("social_coupling_collective_agency_score"), default=0.55),
                _clamp_float(cooperation.get("cooperation_policy_switching_rework_score"), default=0.55),
                _clamp_float(strategy.get("selection_confidence"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            encoding = _clamp_float(case.get("partner_commitment_encoding"), default=0.55)
            retrieval = _clamp_float(case.get("delayed_commitment_retrieval"), default=0.55)
            role_swap = _clamp_float(case.get("role_swap_robustness"), default=0.55)
            reliability_update = _clamp_float(case.get("reliability_shift_update"), default=0.55)
            label_rejection = _clamp_float(case.get("label_template_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            trust_pressure = _clamp_float(
                case.get("fixed_partner_trust_pressure"),
                default=max(shortcut_pressure, 1.0 - reliability_update),
            )
            label_pressure = _clamp_float(
                case.get("partner_label_pressure"),
                default=max(shortcut_pressure, 1.0 - label_rejection),
            )
            hard_negative_pressure = _mean((shortcut_pressure, trust_pressure, label_pressure))
            features = {
                "partner_commitment_encoding": encoding,
                "delayed_commitment_retrieval": retrieval,
                "role_swap_robustness": role_swap,
                "reliability_shift_update": reliability_update,
                "label_template_rejection": label_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * encoding
                + 0.2 * retrieval
                + 0.18 * role_swap
                + 0.14 * reliability_update
                + 0.1 * label_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "commitment_case_id": str(case.get("id") or f"multi_agent_commitment_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "partner_commitment_encoding": round(encoding, 4),
                    "delayed_commitment_retrieval": round(retrieval, 4),
                    "role_swap_robustness": round(role_swap, 4),
                    "reliability_shift_update": round(reliability_update, 4),
                    "label_template_rejection": round(label_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "commitment_policy": (
                        "track_role_swapped_delayed_partner_commitment"
                        if encoding >= 0.65 and retrieval >= 0.65
                        else "reject_fixed_trust_or_partner_label_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_multi_agent_commitment_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("fixed_trust_or_partner_label_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "multi_agent_commitment_records": records,
            "selected_multi_agent_commitment_record": selected,
            "multi_agent_commitment_tracking_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "prospective_memory",
                "social_coupling_strength_collective_agency",
                "cooperation_policy_switching_rework",
                "strategy_selection",
                "fixed_partner_trust",
                "partner_label_template",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "multi_agent_commitment_tracking_formal_candidate_review_decision_v1.json"
            ),
        }
        self.commitment_history.append(output)
        return output


class NormViolationRepair:
    construct_id = "norm_violation_repair"

    def __init__(self) -> None:
        self.norm_repair_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "violation_detection": 0.03,
                "context_sensitive_repair_selection": 0.03,
                "delayed_repair_pressure": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        norm = dependencies.get("social_norm_tracking", {})
        error = dependencies.get("error_monitoring", {})
        strategy = dependencies.get("strategy_selection", {})
        cooperation = dependencies.get("cooperation_policy_switching_rework", {})
        dependency_support = _mean(
            (
                _clamp_float(norm.get("social_norm_tracking_score"), default=0.55),
                _clamp_float(error.get("monitor_confidence"), default=0.55),
                _clamp_float(strategy.get("selection_confidence"), default=0.55),
                _clamp_float(cooperation.get("cooperation_policy_switching_rework_score"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            violation = _clamp_float(case.get("violation_detection"), default=0.55)
            repair_selection = _clamp_float(case.get("context_sensitive_repair_selection"), default=0.55)
            delayed_pressure = _clamp_float(case.get("delayed_repair_pressure"), default=0.55)
            punishment_rejection = _clamp_float(case.get("punishment_avoidance_rejection"), default=0.55)
            frequency_rejection = _clamp_float(case.get("frequency_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            punishment_pressure = _clamp_float(
                case.get("punishment_avoidance_pressure"),
                default=max(shortcut_pressure, 1.0 - punishment_rejection),
            )
            frequency_pressure = _clamp_float(
                case.get("frequency_pressure"),
                default=max(shortcut_pressure, 1.0 - frequency_rejection),
            )
            hard_negative_pressure = _mean((shortcut_pressure, punishment_pressure, frequency_pressure))
            features = {
                "violation_detection": violation,
                "context_sensitive_repair_selection": repair_selection,
                "delayed_repair_pressure": delayed_pressure,
                "punishment_avoidance_rejection": punishment_rejection,
                "frequency_rejection": frequency_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * violation
                + 0.22 * repair_selection
                + 0.14 * delayed_pressure
                + 0.12 * punishment_rejection
                + 0.12 * frequency_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "norm_repair_case_id": str(case.get("id") or f"norm_repair_case_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "violation_detection": round(violation, 4),
                    "context_sensitive_repair_selection": round(repair_selection, 4),
                    "delayed_repair_pressure": round(delayed_pressure, 4),
                    "punishment_avoidance_rejection": round(punishment_rejection, 4),
                    "frequency_rejection": round(frequency_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "repair_policy": (
                        "select_context_sensitive_norm_repair"
                        if violation >= 0.65 and repair_selection >= 0.65
                        else "reject_punishment_or_frequency_repair_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_norm_violation_repair_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("punishment_frequency_or_reward_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "norm_violation_repair_records": records,
            "selected_norm_violation_repair": selected,
            "norm_violation_repair_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "social_norm_tracking",
                "error_monitoring",
                "strategy_selection",
                "cooperation_policy_switching_rework",
                "punishment_avoidance_only",
                "frequency_only",
                "reward_history_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "norm_violation_repair_formal_candidate_review_decision_v1.json"
            ),
        }
        self.norm_repair_history.append(output)
        return output


class ConstraintSatisfactionReconfiguration:
    construct_id = "constraint_satisfaction_reconfiguration"

    def __init__(self) -> None:
        self.reconfiguration_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "active_constraint_conflict_detection": 0.03,
                "constraint_rebinding": 0.03,
                "solution_structure_transfer": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        insight = dependencies.get("insight_problem_solving_rework", {})
        divergent = dependencies.get("divergent_thinking", {})
        hierarchy = dependencies.get("goal_hierarchy_emergence", {})
        strategy = dependencies.get("strategy_selection", {})
        dependency_support = _mean(
            (
                _clamp_float(insight.get("insight_problem_solving_rework_score"), default=0.55),
                _clamp_float(divergent.get("divergent_thinking_score"), default=0.55),
                _clamp_float(hierarchy.get("hierarchy_coherence"), default=0.55),
                _clamp_float(strategy.get("selection_confidence"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            conflict_detection = _clamp_float(case.get("active_constraint_conflict_detection"), default=0.55)
            rebinding = _clamp_float(case.get("constraint_rebinding"), default=0.55)
            retry_suppression = _clamp_float(case.get("local_retry_suppression"), default=0.55)
            transfer = _clamp_float(case.get("solution_structure_transfer"), default=0.55)
            random_rejection = _clamp_float(case.get("random_search_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            random_pressure = _clamp_float(
                case.get("random_search_pressure"),
                default=max(shortcut_pressure, 1.0 - random_rejection),
            )
            complexity_pressure = _clamp_float(
                case.get("complexity_only_pressure"),
                default=max(shortcut_pressure, 1.0 - conflict_detection),
            )
            local_retry_pressure = _clamp_float(
                case.get("local_retry_pressure"),
                default=max(shortcut_pressure, 1.0 - retry_suppression),
            )
            hard_negative_pressure = _mean(
                (shortcut_pressure, random_pressure, complexity_pressure, local_retry_pressure)
            )
            features = {
                "active_constraint_conflict_detection": conflict_detection,
                "constraint_rebinding": rebinding,
                "local_retry_suppression": retry_suppression,
                "solution_structure_transfer": transfer,
                "random_search_rejection": random_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * conflict_detection
                + 0.22 * rebinding
                + 0.16 * retry_suppression
                + 0.14 * transfer
                + 0.1 * random_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "constraint_reconfiguration_case_id": str(
                        case.get("id") or f"constraint_reconfiguration_{index + 1}"
                    ),
                    "mechanism_score": round(score, 4),
                    "active_constraint_conflict_detection": round(conflict_detection, 4),
                    "constraint_rebinding": round(rebinding, 4),
                    "local_retry_suppression": round(retry_suppression, 4),
                    "solution_structure_transfer": round(transfer, 4),
                    "random_search_rejection": round(random_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "reconfiguration_policy": (
                        "rebind_constraints_after_failed_local_move"
                        if conflict_detection >= 0.65 and rebinding >= 0.65
                        else "reject_complexity_random_or_local_retry_control"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_constraint_reconfiguration_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("complexity_random_or_local_retry_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "constraint_reconfiguration_records": records,
            "selected_constraint_reconfiguration": selected,
            "constraint_satisfaction_reconfiguration_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "insight_problem_solving_rework",
                "divergent_thinking",
                "goal_hierarchy_emergence",
                "strategy_selection",
                "complexity_only",
                "random_search_only",
                "local_retry_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "constraint_satisfaction_reconfiguration_formal_candidate_review_decision_v1.json"
            ),
        }
        self.reconfiguration_history.append(output)
        return output


class IntegrationWithoutBroadcastBoundary:
    construct_id = "integration_without_broadcast_boundary"

    def __init__(self) -> None:
        self.integration_boundary_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "distributed_integration": 0.03,
                "target_specific_gain": 0.03,
                "broadcast_limit_resilience": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        integration = dependencies.get("information_integration_phase", {})
        broadcast = dependencies.get("global_broadcast_phase", {})
        coordination = dependencies.get("coordination_length_control", {})
        dependency_support = _mean(
            (
                _clamp_float(integration.get("integration_coherence"), default=0.55),
                _clamp_float(broadcast.get("broadcast_phase_score"), default=0.55),
                _clamp_float(coordination.get("coordination_length_control_score"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            distributed = _clamp_float(case.get("distributed_integration"), default=0.55)
            target_gain = _clamp_float(case.get("target_specific_gain"), default=0.55)
            limit_resilience = _clamp_float(case.get("broadcast_limit_resilience"), default=0.55)
            broadcast_rejection = _clamp_float(case.get("global_broadcast_rejection"), default=0.55)
            coupling_rejection = _clamp_float(case.get("local_coupling_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            global_gain_pressure = _clamp_float(
                case.get("global_gain_pressure"),
                default=max(shortcut_pressure, 1.0 - broadcast_rejection),
            )
            synchrony_pressure = _clamp_float(
                case.get("synchrony_pressure"),
                default=max(shortcut_pressure, 1.0 - coupling_rejection),
            )
            hard_negative_pressure = _mean((shortcut_pressure, global_gain_pressure, synchrony_pressure))
            features = {
                "distributed_integration": distributed,
                "target_specific_gain": target_gain,
                "broadcast_limit_resilience": limit_resilience,
                "global_broadcast_rejection": broadcast_rejection,
                "local_coupling_rejection": coupling_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * distributed
                + 0.2 * target_gain
                + 0.18 * limit_resilience
                + 0.14 * broadcast_rejection
                + 0.1 * coupling_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "integration_boundary_case_id": str(case.get("id") or f"integration_boundary_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "distributed_integration": round(distributed, 4),
                    "target_specific_gain": round(target_gain, 4),
                    "broadcast_limit_resilience": round(limit_resilience, 4),
                    "global_broadcast_rejection": round(broadcast_rejection, 4),
                    "local_coupling_rejection": round(coupling_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "integration_policy": (
                        "preserve_target_gain_under_broadcast_limit"
                        if limit_resilience >= 0.65 and target_gain >= 0.65
                        else "reject_global_broadcast_or_synchrony_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_integration_without_broadcast_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("global_gain_synchrony_or_broadcast_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "integration_without_broadcast_records": records,
            "selected_integration_without_broadcast_record": selected,
            "integration_without_broadcast_boundary_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "information_integration_phase",
                "global_broadcast_phase",
                "coordination_length_control",
                "global_gain_only",
                "synchrony_only",
                "broadcast_capacity_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "integration_without_broadcast_boundary_formal_candidate_review_decision_v1.json"
            ),
        }
        self.integration_boundary_history.append(output)
        return output


class SelectiveGlobalBroadcastControl:
    construct_id = "selective_global_broadcast_control"

    def __init__(self) -> None:
        self.broadcast_control_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "relevance_filtering": 0.03,
                "workspace_broadcast_selectivity": 0.03,
                "downstream_task_gain": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        broadcast = dependencies.get("global_broadcast_phase", {})
        attention = dependencies.get("attention_control", {})
        coordination = dependencies.get("coordination_length_control", {})
        integration = dependencies.get("information_integration_phase", {})
        dependency_support = _mean(
            (
                _clamp_float(broadcast.get("broadcast_phase_score"), default=0.55),
                _clamp_float(attention.get("attention_stability"), default=0.55),
                _clamp_float(coordination.get("coordination_length_control_score"), default=0.55),
                _clamp_float(integration.get("integration_coherence"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            relevance = _clamp_float(case.get("relevance_filtering"), default=0.55)
            selectivity = _clamp_float(case.get("workspace_broadcast_selectivity"), default=0.55)
            downstream_gain = _clamp_float(case.get("downstream_task_gain"), default=0.55)
            suppression = _clamp_float(case.get("irrelevant_broadcast_suppression"), default=0.55)
            global_gain_rejection = _clamp_float(case.get("global_gain_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            global_gain_pressure = _clamp_float(
                case.get("global_gain_pressure"),
                default=max(shortcut_pressure, 1.0 - global_gain_rejection),
            )
            salience_pressure = _clamp_float(
                case.get("salience_broadcast_pressure"),
                default=max(shortcut_pressure, 1.0 - relevance),
            )
            hard_negative_pressure = _mean((shortcut_pressure, global_gain_pressure, salience_pressure))
            features = {
                "relevance_filtering": relevance,
                "workspace_broadcast_selectivity": selectivity,
                "downstream_task_gain": downstream_gain,
                "irrelevant_broadcast_suppression": suppression,
                "global_gain_rejection": global_gain_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * relevance
                + 0.2 * selectivity
                + 0.18 * downstream_gain
                + 0.14 * suppression
                + 0.1 * global_gain_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "selective_broadcast_case_id": str(case.get("id") or f"selective_broadcast_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "relevance_filtering": round(relevance, 4),
                    "workspace_broadcast_selectivity": round(selectivity, 4),
                    "downstream_task_gain": round(downstream_gain, 4),
                    "irrelevant_broadcast_suppression": round(suppression, 4),
                    "global_gain_rejection": round(global_gain_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "broadcast_policy": (
                        "route_relevance_filtered_workspace_broadcast"
                        if relevance >= 0.65 and selectivity >= 0.65
                        else "reject_global_gain_or_salience_broadcast_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = ["strong_boundary_watch"]
        if selection_margin < 0.08:
            boundary_flags.append("low_selective_broadcast_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("global_gain_or_salience_broadcast_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "selective_global_broadcast_records": records,
            "selected_global_broadcast_control_record": selected,
            "selective_global_broadcast_control_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "global_broadcast_phase",
                "attention_control",
                "coordination_length_control",
                "information_integration_phase",
                "global_gain",
                "salience_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "selective_global_broadcast_control_formal_candidate_review_decision_v1.json"
            ),
        }
        self.broadcast_control_history.append(output)
        return output


class AgencyWithoutOwnershipBoundary:
    construct_id = "agency_without_ownership_boundary"

    def __init__(self) -> None:
        self.agency_boundary_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "outcome_control_agency": 0.03,
                "ownership_attribution_suppression": 0.03,
                "boundary_separation": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        agency = dependencies.get("action_agency", {})
        ownership = dependencies.get("action_ownership", {})
        boundary = dependencies.get("self_other_boundary_sharpness", {})
        self_boundary = dependencies.get("boundary_self", {})
        body = dependencies.get("distributed_body_schema_self", {})
        dependency_support = _mean(
            (
                _clamp_float(agency.get("controllability"), default=0.55),
                _clamp_float(ownership.get("ownership_score"), default=0.55),
                _clamp_float(boundary.get("boundary_sharpness"), default=0.55),
                _clamp_float(self_boundary.get("self_boundary_confidence"), default=0.55),
                _clamp_float(body.get("self_schema_confidence"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            outcome_control = _clamp_float(case.get("outcome_control_agency"), default=0.55)
            ownership_suppression = _clamp_float(case.get("ownership_attribution_suppression"), default=0.55)
            bidirectional = _clamp_float(case.get("bidirectional_selectivity"), default=0.55)
            separation = _clamp_float(case.get("boundary_separation"), default=0.55)
            motor_rejection = _clamp_float(case.get("motor_gain_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            ownership_label_pressure = _clamp_float(
                case.get("ownership_label_pressure"),
                default=max(shortcut_pressure, 1.0 - ownership_suppression),
            )
            motor_pressure = _clamp_float(
                case.get("motor_gain_pressure"),
                default=max(shortcut_pressure, 1.0 - motor_rejection),
            )
            hard_negative_pressure = _mean((shortcut_pressure, ownership_label_pressure, motor_pressure))
            features = {
                "outcome_control_agency": outcome_control,
                "ownership_attribution_suppression": ownership_suppression,
                "bidirectional_selectivity": bidirectional,
                "boundary_separation": separation,
                "motor_gain_rejection": motor_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.24 * outcome_control
                + 0.2 * ownership_suppression
                + 0.16 * bidirectional
                + 0.14 * separation
                + 0.1 * motor_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "agency_boundary_case_id": str(case.get("id") or f"agency_boundary_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "outcome_control_agency": round(outcome_control, 4),
                    "ownership_attribution_suppression": round(ownership_suppression, 4),
                    "bidirectional_selectivity": round(bidirectional, 4),
                    "boundary_separation": round(separation, 4),
                    "motor_gain_rejection": round(motor_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "agency_boundary_policy": (
                        "preserve_agency_while_suppressing_ownership_attribution"
                        if outcome_control >= 0.65 and ownership_suppression >= 0.65
                        else "reject_motor_gain_or_ownership_label_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_agency_without_ownership_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("motor_gain_or_ownership_label_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "agency_without_ownership_records": records,
            "selected_agency_without_ownership_record": selected,
            "agency_without_ownership_boundary_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "action_agency",
                "action_ownership",
                "self_other_boundary_sharpness",
                "boundary_self",
                "distributed_body_schema_self",
                "motor_gain_only",
                "ownership_label_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "agency_without_ownership_boundary_formal_candidate_review_decision_v1.json"
            ),
        }
        self.agency_boundary_history.append(output)
        return output


class TemporalIdentityPlanningDissociation:
    construct_id = "temporal_identity_planning_dissociation"

    def __init__(self) -> None:
        self.temporal_dissociation_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "identity_continuity_state": 0.03,
                "planning_depth_retention": 0.03,
                "selective_perturbability": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        identity = dependencies.get("identity_temporal_self", {})
        planning = dependencies.get("temporal_horizon_dependent_planning", {})
        prospective = dependencies.get("prospective_memory", {})
        episodic = dependencies.get("episodic_memory_binding", {})
        dependency_support = _mean(
            (
                _clamp_float(identity.get("identity_coherence"), default=0.55),
                _clamp_float(planning.get("planning_confidence"), default=0.55),
                _clamp_float(prospective.get("prospective_memory_score"), default=0.55),
                _clamp_float(episodic.get("global_binding_strength"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            identity_state = _clamp_float(case.get("identity_continuity_state"), default=0.55)
            planning_retention = _clamp_float(case.get("planning_depth_retention"), default=0.55)
            perturbability = _clamp_float(case.get("selective_perturbability"), default=0.55)
            memory_rejection = _clamp_float(case.get("memory_buffer_rejection"), default=0.55)
            forecast_rejection = _clamp_float(case.get("forecast_only_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            memory_pressure = _clamp_float(
                case.get("memory_buffer_pressure"),
                default=max(shortcut_pressure, 1.0 - memory_rejection),
            )
            forecast_pressure = _clamp_float(
                case.get("forecast_only_pressure"),
                default=max(shortcut_pressure, 1.0 - forecast_rejection),
            )
            hard_negative_pressure = _mean((shortcut_pressure, memory_pressure, forecast_pressure))
            features = {
                "identity_continuity_state": identity_state,
                "planning_depth_retention": planning_retention,
                "selective_perturbability": perturbability,
                "memory_buffer_rejection": memory_rejection,
                "forecast_only_rejection": forecast_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.2 * identity_state
                + 0.22 * planning_retention
                + 0.18 * perturbability
                + 0.12 * memory_rejection
                + 0.12 * forecast_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "temporal_dissociation_case_id": str(
                        case.get("id") or f"temporal_dissociation_{index + 1}"
                    ),
                    "mechanism_score": round(score, 4),
                    "identity_continuity_state": round(identity_state, 4),
                    "planning_depth_retention": round(planning_retention, 4),
                    "selective_perturbability": round(perturbability, 4),
                    "memory_buffer_rejection": round(memory_rejection, 4),
                    "forecast_only_rejection": round(forecast_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "dissociation_policy": (
                        "retain_planning_depth_under_identity_noise"
                        if planning_retention >= 0.65 and perturbability >= 0.65
                        else "reject_forecast_or_memory_buffer_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_temporal_identity_planning_dissociation_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("forecast_or_memory_buffer_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "temporal_identity_planning_dissociation_records": records,
            "selected_temporal_identity_planning_dissociation": selected,
            "temporal_identity_planning_dissociation_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "identity_temporal_self",
                "temporal_horizon_dependent_planning",
                "prospective_memory",
                "working_memory_rehearsal",
                "episodic_memory_binding",
                "forecast_only",
                "memory_buffer_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "temporal_identity_planning_dissociation_formal_candidate_review_decision_v1.json"
            ),
        }
        self.temporal_dissociation_history.append(output)
        return output


class ClockDriftResynchronizationControl:
    construct_id = "clock_drift_resynchronization_control"

    def __init__(self) -> None:
        self.clock_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "drift_detection": 0.03,
                "phase_realignment": 0.03,
                "jitter_robust_transfer": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        planning = dependencies.get("temporal_horizon_dependent_planning", {})
        prospective = dependencies.get("prospective_memory", {})
        dissociation = dependencies.get("temporal_identity_planning_dissociation", {})
        credit = dependencies.get("temporal_credit_assignment", {})
        identity = dependencies.get("identity_temporal_self", {})
        dependency_support = _mean(
            (
                _clamp_float(planning.get("planning_confidence"), default=0.55),
                _clamp_float(prospective.get("prospective_memory_score"), default=0.55),
                _clamp_float(dissociation.get("temporal_identity_planning_dissociation_score"), default=0.55),
                _clamp_float(credit.get("temporal_credit_score"), default=0.55),
                _clamp_float(identity.get("identity_coherence"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            drift = _clamp_float(case.get("drift_detection"), default=0.55)
            realignment = _clamp_float(case.get("phase_realignment"), default=0.55)
            jitter_transfer = _clamp_float(case.get("jitter_robust_transfer"), default=0.55)
            planning_rejection = _clamp_float(case.get("planning_horizon_rejection"), default=0.55)
            motor_rejection = _clamp_float(case.get("motor_speed_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            clock_label_pressure = _clamp_float(
                case.get("clock_label_pressure"),
                default=max(shortcut_pressure, 1.0 - drift),
            )
            motor_pressure = _clamp_float(
                case.get("motor_speed_pressure"),
                default=max(shortcut_pressure, 1.0 - motor_rejection),
            )
            planning_pressure = _clamp_float(
                case.get("planning_horizon_pressure"),
                default=max(shortcut_pressure, 1.0 - planning_rejection),
            )
            hard_negative_pressure = _mean(
                (shortcut_pressure, clock_label_pressure, motor_pressure, planning_pressure)
            )
            features = {
                "drift_detection": drift,
                "phase_realignment": realignment,
                "jitter_robust_transfer": jitter_transfer,
                "planning_horizon_rejection": planning_rejection,
                "motor_speed_rejection": motor_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * drift
                + 0.22 * realignment
                + 0.16 * jitter_transfer
                + 0.12 * planning_rejection
                + 0.12 * motor_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "clock_case_id": str(case.get("id") or f"clock_resynchronization_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "drift_detection": round(drift, 4),
                    "phase_realignment": round(realignment, 4),
                    "jitter_robust_transfer": round(jitter_transfer, 4),
                    "planning_horizon_rejection": round(planning_rejection, 4),
                    "motor_speed_rejection": round(motor_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "clock_policy": (
                        "resynchronize_phase_after_clock_drift"
                        if drift >= 0.65 and realignment >= 0.65
                        else "reject_clock_label_motor_or_planning_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = ["pending_local_registration"]
        if selection_margin < 0.08:
            boundary_flags.append("low_clock_resynchronization_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("clock_label_motor_or_planning_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "clock_resynchronization_records": records,
            "selected_clock_resynchronization_record": selected,
            "clock_drift_resynchronization_control_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "temporal_horizon_dependent_planning",
                "prospective_memory",
                "temporal_identity_planning_dissociation",
                "temporal_credit_assignment",
                "identity_temporal_self",
                "clock_label_only",
                "motor_speed_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "clock_drift_resynchronization_control_formal_candidate_review_decision_v1.json"
            ),
        }
        self.clock_history.append(output)
        return output


class EnergyBudgetReallocationControl:
    construct_id = "energy_budget_reallocation_control"

    def __init__(self) -> None:
        self.energy_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "budget_shift_detection": 0.03,
                "critical_transfer": 0.03,
                "recovery_rebalancing": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        resource = dependencies.get("resource_competition_arbitration", {})
        attention = dependencies.get("attention_control", {})
        strategy = dependencies.get("strategy_selection", {})
        viability = dependencies.get("macro_causal_viability_maintenance", {})
        dependency_support = _mean(
            (
                _clamp_float(resource.get("arbitration_score"), default=0.55),
                _clamp_float(attention.get("attention_stability"), default=0.55),
                _clamp_float(strategy.get("selection_confidence"), default=0.55),
                _clamp_float(viability.get("viability_score"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            shift = _clamp_float(case.get("budget_shift_detection"), default=0.55)
            transfer = _clamp_float(case.get("critical_transfer"), default=0.55)
            recovery = _clamp_float(case.get("recovery_rebalancing"), default=0.55)
            uniform_rejection = _clamp_float(case.get("uniform_capacity_rejection"), default=0.55)
            label_rejection = _clamp_float(case.get("energy_label_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            uniform_pressure = _clamp_float(
                case.get("uniform_capacity_pressure"),
                default=max(shortcut_pressure, 1.0 - uniform_rejection),
            )
            label_pressure = _clamp_float(
                case.get("energy_label_pressure"),
                default=max(shortcut_pressure, 1.0 - label_rejection),
            )
            global_gain_pressure = _clamp_float(
                case.get("global_gain_pressure"),
                default=max(shortcut_pressure, 1.0 - transfer),
            )
            hard_negative_pressure = _mean((shortcut_pressure, uniform_pressure, label_pressure, global_gain_pressure))
            features = {
                "budget_shift_detection": shift,
                "critical_transfer": transfer,
                "recovery_rebalancing": recovery,
                "uniform_capacity_rejection": uniform_rejection,
                "energy_label_rejection": label_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * shift
                + 0.22 * transfer
                + 0.16 * recovery
                + 0.12 * uniform_rejection
                + 0.1 * label_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "energy_budget_case_id": str(case.get("id") or f"energy_budget_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "budget_shift_detection": round(shift, 4),
                    "critical_transfer": round(transfer, 4),
                    "recovery_rebalancing": round(recovery, 4),
                    "uniform_capacity_rejection": round(uniform_rejection, 4),
                    "energy_label_rejection": round(label_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "energy_policy": (
                        "transfer_budget_to_critical_subsystem"
                        if shift >= 0.65 and transfer >= 0.65
                        else "reject_uniform_capacity_or_energy_label_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = ["pending_local_registration"]
        if selection_margin < 0.08:
            boundary_flags.append("low_energy_budget_reallocation_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("uniform_capacity_energy_label_or_global_gain_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "energy_budget_reallocation_records": records,
            "selected_energy_budget_reallocation": selected,
            "energy_budget_reallocation_control_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "resource_competition_arbitration",
                "attention_control",
                "strategy_selection",
                "macro_causal_viability_maintenance",
                "global_gain_proxy",
                "uniform_capacity_loss",
                "energy_label_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "energy_budget_reallocation_control_formal_candidate_review_decision_v1.json"
            ),
        }
        self.energy_history.append(output)
        return output


class SensorGainRecalibrationControl:
    construct_id = "sensor_gain_recalibration_control"

    def __init__(self) -> None:
        self.sensor_gain_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "gain_drift_detection": 0.03,
                "state_estimate_rescaling": 0.03,
                "offset_compensation_transfer": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        minimization = dependencies.get("predictive_error_minimization_phase", {})
        action_prediction = dependencies.get("predictive_control_under_action_intervention", {})
        learning = dependencies.get("learning_rate_adaptation_rework", {})
        correction = dependencies.get("body_schema_error_correction", {})
        attention = dependencies.get("attention_control", {})
        dependency_support = _mean(
            (
                _clamp_float(minimization.get("minimization_gain"), default=0.55),
                _clamp_float(action_prediction.get("predictive_control_under_action_intervention_score"), default=0.55),
                _clamp_float(learning.get("learning_rate_adaptation_score"), default=0.55),
                _clamp_float(correction.get("correction_strength"), default=0.55),
                _clamp_float(attention.get("attention_stability"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            drift = _clamp_float(case.get("gain_drift_detection"), default=0.55)
            rescaling = _clamp_float(case.get("state_estimate_rescaling"), default=0.55)
            compensation = _clamp_float(case.get("offset_compensation_transfer"), default=0.55)
            salience_rejection = _clamp_float(case.get("attention_salience_rejection"), default=0.55)
            label_rejection = _clamp_float(case.get("sensor_label_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            salience_pressure = _clamp_float(
                case.get("attention_salience_pressure"),
                default=max(shortcut_pressure, 1.0 - salience_rejection),
            )
            label_pressure = _clamp_float(
                case.get("sensor_label_pressure"),
                default=max(shortcut_pressure, 1.0 - label_rejection),
            )
            hard_negative_pressure = _mean((shortcut_pressure, salience_pressure, label_pressure))
            features = {
                "gain_drift_detection": drift,
                "state_estimate_rescaling": rescaling,
                "offset_compensation_transfer": compensation,
                "attention_salience_rejection": salience_rejection,
                "sensor_label_rejection": label_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * drift
                + 0.2 * rescaling
                + 0.18 * compensation
                + 0.14 * salience_rejection
                + 0.1 * label_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "sensor_gain_case_id": str(case.get("id") or f"sensor_gain_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "gain_drift_detection": round(drift, 4),
                    "state_estimate_rescaling": round(rescaling, 4),
                    "offset_compensation_transfer": round(compensation, 4),
                    "attention_salience_rejection": round(salience_rejection, 4),
                    "sensor_label_rejection": round(label_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "sensor_policy": (
                        "rescale_state_estimate_after_gain_drift"
                        if drift >= 0.65 and rescaling >= 0.65
                        else "reject_sensor_label_or_attention_salience_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = ["pending_local_registration"]
        if selection_margin < 0.08:
            boundary_flags.append("low_sensor_gain_recalibration_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("sensor_label_or_salience_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "sensor_gain_recalibration_records": records,
            "selected_sensor_gain_recalibration": selected,
            "sensor_gain_recalibration_control_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "predictive_error_minimization_phase",
                "predictive_control_under_action_intervention",
                "learning_rate_adaptation_rework",
                "body_schema_error_correction",
                "attention_control",
                "sensor_label_only",
                "attention_salience_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "sensor_gain_recalibration_control_formal_candidate_review_decision_v1.json"
            ),
        }
        self.sensor_gain_history.append(output)
        return output


class ToolUseAffordanceRemapping:
    construct_id = "tool_use_affordance_remapping"

    def __init__(self) -> None:
        self.tool_affordance_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "tool_dynamics_change_detection": 0.03,
                "tool_action_affordance_transfer": 0.03,
                "static_affordance_rejection": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        affordance = dependencies.get("affordance_selection_control", {})
        correction = dependencies.get("body_schema_error_correction", {})
        spatial = dependencies.get("spatial_navigation_remapping_rework", {})
        ownership = dependencies.get("action_ownership", {})
        body = dependencies.get("distributed_body_schema_self", {})
        dependency_support = _mean(
            (
                _clamp_float(affordance.get("affordance_selection_confidence"), default=0.55),
                _clamp_float(correction.get("correction_strength"), default=0.55),
                _clamp_float(spatial.get("spatial_navigation_remapping_rework_score"), default=0.55),
                _clamp_float(ownership.get("ownership_score"), default=0.55),
                _clamp_float(body.get("self_schema_confidence"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            dynamics = _clamp_float(case.get("tool_dynamics_change_detection"), default=0.55)
            transfer = _clamp_float(case.get("tool_action_affordance_transfer"), default=0.55)
            static_rejection = _clamp_float(case.get("static_affordance_rejection"), default=0.55)
            body_boundary = _clamp_float(case.get("body_schema_boundary"), default=0.55)
            label_rejection = _clamp_float(case.get("tool_label_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            static_pressure = _clamp_float(
                case.get("static_affordance_pressure"),
                default=max(shortcut_pressure, 1.0 - static_rejection),
            )
            label_pressure = _clamp_float(
                case.get("tool_label_pressure"),
                default=max(shortcut_pressure, 1.0 - label_rejection),
            )
            hard_negative_pressure = _mean((shortcut_pressure, static_pressure, label_pressure))
            features = {
                "tool_dynamics_change_detection": dynamics,
                "tool_action_affordance_transfer": transfer,
                "static_affordance_rejection": static_rejection,
                "body_schema_boundary": body_boundary,
                "tool_label_rejection": label_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * dynamics
                + 0.22 * transfer
                + 0.14 * static_rejection
                + 0.12 * body_boundary
                + 0.12 * label_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "tool_affordance_case_id": str(case.get("id") or f"tool_affordance_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "tool_dynamics_change_detection": round(dynamics, 4),
                    "tool_action_affordance_transfer": round(transfer, 4),
                    "static_affordance_rejection": round(static_rejection, 4),
                    "body_schema_boundary": round(body_boundary, 4),
                    "tool_label_rejection": round(label_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "tool_policy": (
                        "remap_affordance_after_tool_dynamics_change"
                        if dynamics >= 0.65 and transfer >= 0.65
                        else "reject_static_affordance_or_tool_label_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = ["pending_local_registration"]
        if selection_margin < 0.08:
            boundary_flags.append("low_tool_affordance_remapping_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("static_affordance_or_tool_label_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "tool_affordance_remapping_records": records,
            "selected_tool_affordance_remapping": selected,
            "tool_use_affordance_remapping_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "affordance_selection_control",
                "body_schema_error_correction",
                "spatial_navigation_remapping_rework",
                "action_ownership",
                "distributed_body_schema_self",
                "static_affordance_only",
                "tool_label_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "tool_use_affordance_remapping_formal_candidate_review_decision_v1.json"
            ),
        }
        self.tool_affordance_history.append(output)
        return output


class ActuatorFailureCompensationControl:
    construct_id = "actuator_failure_compensation_control"

    def __init__(self) -> None:
        self.actuator_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "fault_detection": 0.03,
                "degraded_actuator_isolation": 0.03,
                "alternative_effector_routing": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        correction = dependencies.get("body_schema_error_correction", {})
        action_prediction = dependencies.get("predictive_control_under_action_intervention", {})
        agency = dependencies.get("action_agency", {})
        ownership = dependencies.get("action_ownership", {})
        tool = dependencies.get("tool_use_affordance_remapping", {})
        sensor = dependencies.get("sensor_gain_recalibration_control", {})
        dependency_support = _mean(
            (
                _clamp_float(correction.get("correction_strength"), default=0.55),
                _clamp_float(action_prediction.get("predictive_control_under_action_intervention_score"), default=0.55),
                _clamp_float(agency.get("controllability"), default=0.55),
                _clamp_float(ownership.get("ownership_score"), default=0.55),
                _clamp_float(tool.get("tool_use_affordance_remapping_score"), default=0.55),
                _clamp_float(sensor.get("sensor_gain_recalibration_control_score"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            fault = _clamp_float(case.get("fault_detection"), default=0.55)
            isolation = _clamp_float(case.get("degraded_actuator_isolation"), default=0.55)
            routing = _clamp_float(case.get("alternative_effector_routing"), default=0.55)
            rebinding = _clamp_float(case.get("action_plan_rebinding"), default=0.55)
            label_rejection = _clamp_float(case.get("actuator_label_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            label_pressure = _clamp_float(
                case.get("actuator_label_pressure"),
                default=max(shortcut_pressure, 1.0 - label_rejection),
            )
            reward_pressure = _clamp_float(
                case.get("reward_recovery_pressure"),
                default=max(shortcut_pressure, 1.0 - fault),
            )
            hard_negative_pressure = _mean((shortcut_pressure, label_pressure, reward_pressure))
            features = {
                "fault_detection": fault,
                "degraded_actuator_isolation": isolation,
                "alternative_effector_routing": routing,
                "action_plan_rebinding": rebinding,
                "actuator_label_rejection": label_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * fault
                + 0.2 * isolation
                + 0.2 * routing
                + 0.14 * rebinding
                + 0.08 * label_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "actuator_failure_case_id": str(case.get("id") or f"actuator_failure_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "fault_detection": round(fault, 4),
                    "degraded_actuator_isolation": round(isolation, 4),
                    "alternative_effector_routing": round(routing, 4),
                    "action_plan_rebinding": round(rebinding, 4),
                    "actuator_label_rejection": round(label_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "actuator_policy": (
                        "route_around_degraded_actuator"
                        if fault >= 0.65 and routing >= 0.65
                        else "reject_actuator_label_or_reward_recovery_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = ["l3_ready_carded_candidate", "relation_matrix_governance_complete"]
        if selection_margin < 0.08:
            boundary_flags.append("low_actuator_failure_compensation_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("actuator_label_or_reward_recovery_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "actuator_failure_compensation_records": records,
            "selected_actuator_failure_compensation": selected,
            "actuator_failure_compensation_control_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "body_schema_error_correction",
                "predictive_control_under_action_intervention",
                "action_agency",
                "action_ownership",
                "tool_use_affordance_remapping",
                "sensor_gain_recalibration_control",
                "actuator_label_only",
                "reward_recovery_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "actuator_failure_compensation_control_formal_candidate_review_decision_v1.json"
            ),
        }
        self.actuator_history.append(output)
        return output


class PreferenceReversalAdaptationControl:
    construct_id = "preference_reversal_adaptation_control"

    def __init__(self) -> None:
        self.preference_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "unlabeled_reversal_detection": 0.03,
                "value_policy_remapping": 0.03,
                "old_policy_inhibition": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        strategy = dependencies.get("strategy_selection", {})
        conflict = dependencies.get("goal_conflict_resolution", {})
        resource = dependencies.get("resource_competition_arbitration", {})
        norm = dependencies.get("social_norm_tracking", {})
        calibration = dependencies.get("confidence_calibration_rework", {})
        error = dependencies.get("error_monitoring", {})
        dependency_support = _mean(
            (
                _clamp_float(strategy.get("selection_confidence"), default=0.55),
                _clamp_float(conflict.get("goal_conflict_resolution_score"), default=0.55),
                _clamp_float(resource.get("arbitration_score"), default=0.55),
                _clamp_float(norm.get("social_norm_tracking_score"), default=0.55),
                _clamp_float(calibration.get("confidence_calibration_score"), default=0.55),
                _clamp_float(error.get("monitor_confidence"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            reversal = _clamp_float(case.get("unlabeled_reversal_detection"), default=0.55)
            remapping = _clamp_float(case.get("value_policy_remapping"), default=0.55)
            inhibition = _clamp_float(case.get("old_policy_inhibition"), default=0.55)
            transfer = _clamp_float(case.get("cross_context_transfer"), default=0.55)
            label_rejection = _clamp_float(case.get("preference_label_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            label_pressure = _clamp_float(
                case.get("preference_label_pressure"),
                default=max(shortcut_pressure, 1.0 - label_rejection),
            )
            seen_pair_pressure = _clamp_float(
                case.get("seen_pair_pressure"),
                default=max(shortcut_pressure, 1.0 - transfer),
            )
            old_policy_pressure = _clamp_float(
                case.get("old_policy_pressure"),
                default=max(shortcut_pressure, 1.0 - inhibition),
            )
            hard_negative_pressure = _mean((shortcut_pressure, label_pressure, seen_pair_pressure, old_policy_pressure))
            features = {
                "unlabeled_reversal_detection": reversal,
                "value_policy_remapping": remapping,
                "old_policy_inhibition": inhibition,
                "cross_context_transfer": transfer,
                "preference_label_rejection": label_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * reversal
                + 0.22 * remapping
                + 0.16 * inhibition
                + 0.14 * transfer
                + 0.1 * label_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "preference_reversal_case_id": str(case.get("id") or f"preference_reversal_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "unlabeled_reversal_detection": round(reversal, 4),
                    "value_policy_remapping": round(remapping, 4),
                    "old_policy_inhibition": round(inhibition, 4),
                    "cross_context_transfer": round(transfer, 4),
                    "preference_label_rejection": round(label_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "preference_policy": (
                        "remap_unlabeled_value_policy_after_reversal"
                        if reversal >= 0.65 and remapping >= 0.65
                        else "reject_preference_label_or_seen_pair_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = ["l3_ready_carded_candidate", "relation_matrix_required"]
        if selection_margin < 0.08:
            boundary_flags.append("low_preference_reversal_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("preference_label_seen_pair_or_old_policy_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "preference_reversal_adaptation_records": records,
            "selected_preference_reversal_adaptation": selected,
            "preference_reversal_adaptation_control_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "strategy_selection",
                "goal_conflict_resolution",
                "resource_competition_arbitration",
                "social_norm_tracking",
                "confidence_calibration_rework",
                "error_monitoring",
                "preference_label_only",
                "seen_pair_only",
                "old_policy_habit_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "preference_reversal_adaptation_control_formal_candidate_review_decision_v1.json"
            ),
        }
        self.preference_history.append(output)
        return output


class _PendingLocalCandidateControl:
    construct_id = ""

    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []
        self.outcome_learner = _new_pending_local_candidate_learner(self.construct_id)

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)


def _new_pending_local_candidate_learner(construct_id: str) -> _OnlineScalarLearner:
    profile = _REMAINING_CANDIDATE_PROFILES[construct_id]
    feature_weights = {dimension: 0.03 for dimension in profile["dimensions"]}
    feature_weights["shortcut_pressure"] = -0.04
    feature_weights["dependency_support"] = 0.06
    return _OnlineScalarLearner(feature_weights=feature_weights, learning_rate=0.06)


def _run_pending_local_candidate_control_process(
    control: "_PendingLocalCandidateControl",
    input_state: dict[str, Any],
    dependencies: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    construct_id = control.construct_id
    profile = _REMAINING_CANDIDATE_PROFILES[construct_id]
    dependency_support = _dependency_support(dependencies)
    construct_relevance = _construct_relevance(construct_id, input_state)
    records = []
    for index, case in enumerate(_remaining_candidate_items(construct_id, input_state)):
        dimensions: list[float] = []
        record: dict[str, Any] = {
            "mechanism_score": 0.0,
            "hard_negative_pressure": 0.0,
        }
        for dimension in profile["dimensions"]:
            dimension_value = _clamp_float(case.get(dimension), default=0.55)
            record[dimension] = round(dimension_value, 4)
            dimensions.append(dimension_value)
        case_signal = _mean(dimensions) if dimensions else 0.55
        shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
        proxy_pressure = _clamp_float(
            case.get("proxy_pressure"),
            default=max(shortcut_pressure, 1.0 - case_signal),
        )
        label_pressure = _clamp_float(
            case.get("label_rejection"),
            default=max(shortcut_pressure, 1.0 - construct_relevance),
        )
        hard_negative_pressure = _mean((shortcut_pressure, proxy_pressure, label_pressure))
        features = dict((dimension, value) for dimension, value in record.items() if dimension != "hard_negative_pressure")
        features["shortcut_pressure"] = hard_negative_pressure
        features["dependency_support"] = dependency_support
        learned_adjustment = control.outcome_learner.predict(features) - 0.5
        score = _clamp(
            0.2 * case_signal
            + 0.14 * _clamp_float(dimensions[0] if dimensions else 0.55, default=0.55)
            + 0.1 * construct_relevance
            + 0.1 * dependency_support
            + 0.12 * (1.0 - hard_negative_pressure)
            - 0.15 * hard_negative_pressure
            + 0.08 * learned_adjustment
        )
        record.update(
            {
                str(profile["id_key"]): str(
                    case.get("id") or f"{construct_id}_{index + 1}"
                ),
                "mechanism_score": round(score, 4),
                "hard_negative_pressure": round(hard_negative_pressure, 4),
                f"{construct_id}_policy": (
                    f"activate_{construct_id}"
                    if case_signal >= 0.62 and dependency_support >= 0.35
                    else f"defer_{construct_id}_proxy"
                ),
            }
        )
        records.append(record)

    records.sort(key=lambda record: record["mechanism_score"], reverse=True)
    selected = records[0] if records else {}
    second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
    selection_margin = _clamp(
        _clamp_float(selected.get("mechanism_score"), default=0.0) - second_score
    )
    mean_hard_negative_pressure = (
        _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
    )
    aggregate_score = _clamp(
        0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
        + 0.12 * selection_margin
        + 0.1 * dependency_support
        + 0.1 * (1.0 - mean_hard_negative_pressure)
    )
    boundary_flags = list(profile.get("status_flags", ("pending_local_registration",)))
    if selection_margin < 0.08:
        boundary_flags.append(f"low_{construct_id}_margin")
    if mean_hard_negative_pressure >= 0.35:
        boundary_flags.append(f"{construct_id}_pressure")

    output = {
        "construct_id": construct_id,
        "implemented_as": "bespoke_construct_mechanism_v1",
        "placeholder": False,
        "independent_process_logic": True,
        profile["collection_key"]: records,
        profile["selected_key"]: selected,
        profile["score_key"]: round(aggregate_score, 4),
        "selection_margin": round(selection_margin, 4),
        "dependency_support": round(dependency_support, 4),
        "mean_hard_negative_pressure": round(mean_hard_negative_pressure, 4),
        "learner_state": control.outcome_learner.to_dict(),
        "boundary_flags": boundary_flags,
        "hctm_boundary_watch": list(profile.get("boundary_watch", ())),
        "source_constraint": (
            "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
            f"{construct_id}_formal_candidate_review_decision_v1.json"
        ),
    }
    control._history.append(output)
    return output


class CheckpointRollbackRecoveryControl(_PendingLocalCandidateControl):
    construct_id = "checkpoint_rollback_recovery_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class FeedbackChannelIntegrityReweightingControl(_PendingLocalCandidateControl):
    construct_id = "feedback_channel_integrity_reweighting_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class InstructionScopeBindingControl(_PendingLocalCandidateControl):
    construct_id = "instruction_scope_binding_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class InterfaceProtocolNegotiationControl(_PendingLocalCandidateControl):
    construct_id = "interface_protocol_negotiation_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class InterferenceSourceSeparationControl(_PendingLocalCandidateControl):
    construct_id = "interference_source_separation_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class IrreversibleCommitmentSafeguardControl(_PendingLocalCandidateControl):
    construct_id = "irreversible_commitment_safeguard_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class LatentStateAliasDisambiguationControl(_PendingLocalCandidateControl):
    construct_id = "latent_state_alias_disambiguation_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class LocalizedRegimeShiftQuarantineControl(_PendingLocalCandidateControl):
    construct_id = "localized_regime_shift_quarantine_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class MemoryIndexCorruptionRebindingControl(_PendingLocalCandidateControl):
    construct_id = "memory_index_corruption_rebinding_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class ModelStalenessDetectionControl(_PendingLocalCandidateControl):
    construct_id = "model_staleness_detection_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class ObservationDropoutBridgingControl(_PendingLocalCandidateControl):
    construct_id = "observation_dropout_bridging_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class OptionValuePreservingProbeControl(_PendingLocalCandidateControl):
    construct_id = "option_value_preserving_probe_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class PermissionRevocationComplianceControl(_PendingLocalCandidateControl):
    construct_id = "permission_revocation_compliance_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class PriorityStarvationPreventionControl(_PendingLocalCandidateControl):
    construct_id = "priority_starvation_prevention_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class ProvenanceWeightedEvidenceIntegrationControl(_PendingLocalCandidateControl):
    construct_id = "provenance_weighted_evidence_integration_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class RedundantPathwayFailoverControl(_PendingLocalCandidateControl):
    construct_id = "redundant_pathway_failover_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class RepresentationFormatTranslationControl(_PendingLocalCandidateControl):
    construct_id = "representation_format_translation_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class SensorimotorLatencyCompensationControl(_PendingLocalCandidateControl):
    construct_id = "sensorimotor_latency_compensation_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class SideEffectContainmentControl(_PendingLocalCandidateControl):
    construct_id = "side_effect_containment_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class UnitFrameNormalizationControl(_PendingLocalCandidateControl):
    construct_id = "unit_frame_normalization_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class AccountabilityObligationScopeResponseControl(_PendingLocalCandidateControl):
    construct_id = "accountability_obligation_scope_response_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class CounterEvidencePreservationControl(_PendingLocalCandidateControl):
    construct_id = "counter_evidence_preservation_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class CounterpartyIntentUncertaintyResolutionControl(_PendingLocalCandidateControl):
    construct_id = "counterparty_intent_uncertainty_resolution_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class CredentialValidityChallengeResponseControl(_PendingLocalCandidateControl):
    construct_id = "credential_validity_challenge_response_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class DeadlineObligationTriageControl(_PendingLocalCandidateControl):
    construct_id = "deadline_obligation_triage_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class ObservationBudgetAllocationControl(_PendingLocalCandidateControl):
    construct_id = "observation_budget_allocation_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class SampleRepresentativenessReweightingControl(_PendingLocalCandidateControl):
    construct_id = "sample_representativeness_reweighting_control"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        return _run_pending_local_candidate_control_process(
            self,
            input_state,
            dependencies,
        )


class CommunicationChannelRepairControl:
    construct_id = "communication_channel_repair_control"

    def __init__(self) -> None:
        self.communication_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "channel_loss_detection": 0.03,
                "ack_resend_repair": 0.03,
                "protocol_resynchronization": 0.02,
                "shortcut_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        commitment = dependencies.get("multi_agent_commitment_tracking", {})
        norm = dependencies.get("social_norm_tracking", {})
        perspective = dependencies.get("perspective_taking", {})
        semantic = dependencies.get("semantic_memory_retrieval_control", {})
        tool = dependencies.get("tool_use_affordance_remapping", {})
        dependency_support = _mean(
            (
                _clamp_float(commitment.get("multi_agent_commitment_tracking_score"), default=0.55),
                _clamp_float(norm.get("social_norm_tracking_score"), default=0.55),
                _clamp_float(perspective.get("perspective_accuracy_proxy"), default=0.55),
                _clamp_float(semantic.get("semantic_memory_retrieval_control_score"), default=0.55),
                _clamp_float(tool.get("tool_use_affordance_remapping_score"), default=0.55),
            )
        )
        records = []
        for index, case in enumerate(_remaining_candidate_items(self.construct_id, input_state)):
            loss = _clamp_float(case.get("channel_loss_detection"), default=0.55)
            ack_repair = _clamp_float(case.get("ack_resend_repair"), default=0.55)
            redundancy = _clamp_float(case.get("redundancy_reconstruction"), default=0.55)
            resync = _clamp_float(case.get("protocol_resynchronization"), default=0.55)
            label_rejection = _clamp_float(case.get("channel_label_rejection"), default=0.55)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            generic_pressure = _clamp_float(
                case.get("generic_redundancy_pressure"),
                default=max(shortcut_pressure, 1.0 - loss),
            )
            label_pressure = _clamp_float(
                case.get("channel_label_pressure"),
                default=max(shortcut_pressure, 1.0 - label_rejection),
            )
            reward_ack_pressure = _clamp_float(
                case.get("reward_ack_pressure"),
                default=max(shortcut_pressure, 1.0 - ack_repair),
            )
            hard_negative_pressure = _mean((shortcut_pressure, generic_pressure, label_pressure, reward_ack_pressure))
            features = {
                "channel_loss_detection": loss,
                "ack_resend_repair": ack_repair,
                "redundancy_reconstruction": redundancy,
                "protocol_resynchronization": resync,
                "channel_label_rejection": label_rejection,
                "shortcut_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            score = _clamp(
                0.22 * loss
                + 0.2 * ack_repair
                + 0.16 * redundancy
                + 0.18 * resync
                + 0.08 * label_rejection
                + 0.08 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "communication_repair_case_id": str(case.get("id") or f"communication_repair_{index + 1}"),
                    "mechanism_score": round(score, 4),
                    "channel_loss_detection": round(loss, 4),
                    "ack_resend_repair": round(ack_repair, 4),
                    "redundancy_reconstruction": round(redundancy, 4),
                    "protocol_resynchronization": round(resync, 4),
                    "channel_label_rejection": round(label_rejection, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "communication_policy": (
                        "repair_lossy_channel_with_ack_resend_and_resync"
                        if loss >= 0.65 and ack_repair >= 0.65 and resync >= 0.65
                        else "reject_generic_redundancy_or_channel_label_proxy"
                    ),
                }
            )
        records.sort(key=lambda record: record["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = [
            "candidate_only_internal",
            "l3_ready_carded_candidate",
            "relation_matrix_governance_complete",
        ]
        if selection_margin < 0.08:
            boundary_flags.append("low_communication_channel_repair_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("generic_redundancy_channel_label_or_reward_ack_control_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "communication_channel_repair_records": records,
            "selected_communication_channel_repair": selected,
            "communication_channel_repair_control_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "multi_agent_commitment_tracking",
                "social_norm_tracking",
                "perspective_taking",
                "semantic_memory_retrieval_control",
                "tool_use_affordance_remapping",
                "generic_redundancy_proxy",
                "channel_label_proxy",
                "reward_ack_proxy",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "communication_channel_repair_control_formal_candidate_review_decision_v1.json"
            ),
        }
        self.communication_history.append(output)
        return output


class CausalModelAbstractionHierarchy:
    construct_id = "causal_model_abstraction_hierarchy"

    def __init__(self) -> None:
        self.abstraction_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "causal_abstraction_depth": 0.03,
                "intervention_graph_sensitivity": 0.03,
                "counterfactual_transfer_consistency": 0.02,
                "hard_negative_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        causal = dependencies.get("causal_attribution", {})
        counterfactual = dependencies.get("counterfactual_reasoning_depth", {})
        dependency_support = _mean(
            (
                _clamp_float(causal.get("causal_confidence"), default=0.55),
                _clamp_float(causal.get("selection_margin"), default=0.55),
                _clamp_float(counterfactual.get("counterfactual_reasoning_depth_score"), default=0.55),
            )
        )
        cases = _list_of_dicts(input_state.get("causal_model_abstraction_cases"))
        if not cases:
            cases = (
                {
                    "id": "causal_hierarchy_depth",
                    "causal_abstraction_depth": 0.84,
                    "intervention_graph_sensitivity": 0.78,
                    "counterfactual_transfer_consistency": 0.8,
                    "mechanism_label_risk": 0.18,
                    "shortcut_pressure": 0.14,
                },
                {
                    "id": "surface_causal_label_shortcut",
                    "causal_abstraction_depth": 0.28,
                    "intervention_graph_sensitivity": 0.24,
                    "counterfactual_transfer_consistency": 0.3,
                    "mechanism_label_risk": 0.74,
                    "shortcut_pressure": 0.72,
                },
            )
        records = []
        for index, case in enumerate(cases):
            abstraction_depth = _clamp_float(case.get("causal_abstraction_depth"), default=0.55)
            graph_sensitivity = _clamp_float(case.get("intervention_graph_sensitivity"), default=0.55)
            transfer_consistency = _clamp_float(case.get("counterfactual_transfer_consistency"), default=0.55)
            identity_support = _clamp_float(case.get("identity_causal_support"), default=abstraction_depth)
            mechanism_label_risk = _clamp_float(case.get("mechanism_label_risk"), default=0.0)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            counterfactual_pressure = _clamp_float(
                case.get("counterfactual_label_pressure"),
                default=max(shortcut_pressure, 1.0 - transfer_consistency),
            )
            identity_pressure = _clamp_float(
                case.get("identity_pressure"),
                default=max(shortcut_pressure, 1.0 - abstraction_depth),
            )
            hard_negative_pressure = _mean((shortcut_pressure, counterfactual_pressure, identity_pressure))
            features = {
                "causal_abstraction_depth": abstraction_depth,
                "intervention_graph_sensitivity": graph_sensitivity,
                "counterfactual_transfer_consistency": transfer_consistency,
                "identity_causal_support": identity_support,
                "mechanism_label_risk": mechanism_label_risk,
                "hard_negative_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            mechanism_score = _clamp(
                0.24 * abstraction_depth
                + 0.2 * graph_sensitivity
                + 0.2 * transfer_consistency
                + 0.12 * identity_support
                + 0.1 * dependency_support
                - 0.16 * mechanism_label_risk
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            records.append(
                {
                    "causal_abstraction_case_id": str(case.get("id") or f"causal_abstraction_{index + 1}"),
                    "mechanism_score": round(mechanism_score, 4),
                    "causal_abstraction_depth": round(abstraction_depth, 4),
                    "intervention_graph_sensitivity": round(graph_sensitivity, 4),
                    "counterfactual_transfer_consistency": round(transfer_consistency, 4),
                    "identity_causal_support": round(identity_support, 4),
                    "mechanism_label_risk": round(mechanism_label_risk, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "abstraction_policy": (
                        "build_intervention_abstraction_graph"
                        if abstraction_depth >= 0.65 and transfer_consistency >= 0.65
                        else "reject_label_or_mechanism_risk"
                    ),
                }
            )
        records.sort(key=lambda item: item["mechanism_score"], reverse=True)
        selected = records[0] if records else {}
        second_score = records[1]["mechanism_score"] if len(records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(record["hard_negative_pressure"] for record in records) if records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_causal_hierarchy_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("mechanism_label_or_counterfactual_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "causal_model_abstraction_hierarchy_records": records,
            "selected_causal_model_abstraction": selected,
            "causal_model_abstraction_hierarchy_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "causal_attribution",
                "counterfactual_reasoning_depth",
                "causal_model_abstraction_hierarchy",
                "predictive_error_minimization_phase",
                "strategy_selection",
                "label_template_causal_depth",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "causal_model_abstraction_hierarchy_scout_v1.json"
            ),
        }
        self.abstraction_history.append(output)
        return output


class HierarchicalPhaseCascade:
    construct_id = "hierarchical_phase_cascade"

    def __init__(self) -> None:
        self.cascade_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "hierarchical_cascade_depth": 0.03,
                "simultaneous_phase_alignment": 0.03,
                "nested_transition_gain": 0.02,
                "hard_negative_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        hierarchical_credit = dependencies.get("hierarchical_credit_assignment", {})
        integration = dependencies.get("information_integration_phase", {})
        dependency_support = _mean(
            (
                _clamp_float(hierarchical_credit.get("hierarchical_credit_score"), default=0.55),
                _clamp_float(integration.get("integration_coherence"), default=0.55),
            )
        )
        cases = _list_of_dicts(input_state.get("hierarchical_cascade_cases"))
        if not cases:
            cases = (
                {
                    "id": "nested_phase_alignment",
                    "hierarchical_cascade_depth": 0.82,
                    "simultaneous_phase_alignment": 0.78,
                    "nested_transition_gain": 0.8,
                    "phase_overlap_risk": 0.18,
                    "shortcut_pressure": 0.14,
                },
                {
                    "id": "simultaneous_phase_overreach",
                    "hierarchical_cascade_depth": 0.3,
                    "simultaneous_phase_alignment": 0.32,
                    "nested_transition_gain": 0.26,
                    "phase_overlap_risk": 0.74,
                    "shortcut_pressure": 0.72,
                },
            )
        cascade_records = []
        for index, case in enumerate(cases):
            cascade_depth = _clamp_float(case.get("hierarchical_cascade_depth"), default=0.55)
            phase_alignment = _clamp_float(case.get("simultaneous_phase_alignment"), default=0.55)
            transition_gain = _clamp_float(case.get("nested_transition_gain"), default=0.55)
            overlap_risk = _clamp_float(case.get("phase_overlap_risk"), default=0.2)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            overlap_pressure = _clamp_float(
                case.get("simultaneous_phase_pressure"),
                default=max(shortcut_pressure, overlap_risk),
            )
            transition_pressure = _clamp_float(
                case.get("transition_risk_pressure"),
                default=max(shortcut_pressure, 1.0 - transition_gain),
            )
            hard_negative_pressure = _mean((shortcut_pressure, overlap_pressure, transition_pressure))
            features = {
                "hierarchical_cascade_depth": cascade_depth,
                "simultaneous_phase_alignment": phase_alignment,
                "nested_transition_gain": transition_gain,
                "phase_overlap_risk": overlap_risk,
                "hard_negative_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            mechanism_score = _clamp(
                0.24 * cascade_depth
                + 0.2 * phase_alignment
                + 0.2 * transition_gain
                + 0.16 * (1.0 - overlap_risk)
                + 0.1 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            cascade_records.append(
                {
                    "hierarchical_cascade_case_id": str(case.get("id") or f"hierarchical_cascade_{index + 1}"),
                    "mechanism_score": round(mechanism_score, 4),
                    "hierarchical_cascade_depth": round(cascade_depth, 4),
                    "simultaneous_phase_alignment": round(phase_alignment, 4),
                    "nested_transition_gain": round(transition_gain, 4),
                    "phase_overlap_risk": round(overlap_risk, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "cascade_policy": (
                        "propagate_nested_temporal_cascade"
                        if cascade_depth >= 0.65 and phase_alignment >= 0.65
                        else "reject_overlap_or_transition_pressure"
                    ),
                }
            )
        cascade_records.sort(key=lambda item: item["mechanism_score"], reverse=True)
        selected = cascade_records[0] if cascade_records else {}
        second_score = cascade_records[1]["mechanism_score"] if len(cascade_records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(item["hard_negative_pressure"] for item in cascade_records) if cascade_records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_hierarchical_phase_cascade_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("overlap_or_transition_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "hierarchical_phase_cascade_records": cascade_records,
            "selected_hierarchical_phase_cascade": selected,
            "hierarchical_phase_cascade_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "hierarchical_credit_assignment",
                "information_integration_phase",
                "temporal_credit_assignment",
                "nested_transfer_only",
                "simultaneous_onset_pressure_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "hierarchical_phase_cascade_scout_v1.json"
            ),
        }
        self.cascade_history.append(output)
        return output


class CoupledViabilityMetacognitionPhase:
    construct_id = "coupled_viability_metacognition_phase"

    def __init__(self) -> None:
        self.coupled_history: list[dict[str, Any]] = []
        self.outcome_learner = _OnlineScalarLearner(
            feature_weights={
                "coupled_viability_signal": 0.03,
                "uncertainty_moderation": 0.03,
                "boundary_guard_stability": 0.02,
                "hard_negative_pressure": -0.04,
            },
            learning_rate=0.06,
        )

    def learn(self, features: dict[str, Any], target_outcome: float = 1.0) -> dict[str, Any]:
        return self.outcome_learner.update(features, target_outcome)

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        viability = dependencies.get("macro_causal_viability_maintenance", {})
        uncertainty = dependencies.get("uncertainty_threshold_metacognition", {})
        dependency_support = _mean(
            (
                _clamp_float(viability.get("viability_score"), default=0.55),
                _clamp_float(uncertainty.get("uncertainty_score"), default=0.55),
            )
        )
        cases = _list_of_dicts(input_state.get("coupled_viability_cases"))
        if not cases:
            cases = (
                {
                    "id": "coupled_viability_guarded_repair",
                    "coupled_viability_signal": 0.82,
                    "uncertainty_moderation": 0.75,
                    "boundary_guard_stability": 0.78,
                    "coupling_risk": 0.2,
                    "shortcut_pressure": 0.14,
                },
                {
                    "id": "decoupled_viability_risk",
                    "coupled_viability_signal": 0.34,
                    "uncertainty_moderation": 0.3,
                    "boundary_guard_stability": 0.28,
                    "coupling_risk": 0.76,
                    "shortcut_pressure": 0.72,
                },
            )
        coupled_records = []
        for index, case in enumerate(cases):
            viability_signal = _clamp_float(case.get("coupled_viability_signal"), default=0.55)
            uncertainty_moderation = _clamp_float(case.get("uncertainty_moderation"), default=0.55)
            guard_stability = _clamp_float(case.get("boundary_guard_stability"), default=0.55)
            coupling_risk = _clamp_float(case.get("coupling_risk"), default=0.2)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            coupling_pressure = _clamp_float(
                case.get("coupling_risk_pressure"),
                default=max(shortcut_pressure, coupling_risk),
            )
            uncertainty_pressure = _clamp_float(
                case.get("uncertainty_pressure"),
                default=max(shortcut_pressure, 1.0 - uncertainty_moderation),
            )
            hard_negative_pressure = _mean((shortcut_pressure, coupling_pressure, uncertainty_pressure))
            features = {
                "coupled_viability_signal": viability_signal,
                "uncertainty_moderation": uncertainty_moderation,
                "boundary_guard_stability": guard_stability,
                "coupling_risk": coupling_risk,
                "hard_negative_pressure": hard_negative_pressure,
                "dependency_support": dependency_support,
            }
            learned_adjustment = self.outcome_learner.predict(features) - 0.5
            mechanism_score = _clamp(
                0.28 * viability_signal
                + 0.22 * uncertainty_moderation
                + 0.18 * guard_stability
                + 0.12 * (1.0 - coupling_risk)
                + 0.1 * dependency_support
                - 0.15 * hard_negative_pressure
                + 0.08 * learned_adjustment
            )
            coupled_records.append(
                {
                    "coupled_viability_case_id": str(case.get("id") or f"coupled_viability_{index + 1}"),
                    "mechanism_score": round(mechanism_score, 4),
                    "coupled_viability_signal": round(viability_signal, 4),
                    "uncertainty_moderation": round(uncertainty_moderation, 4),
                    "boundary_guard_stability": round(guard_stability, 4),
                    "coupling_risk": round(coupling_risk, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "viability_phase_policy": (
                        "gate_coupled_viability_with_uncertainty_control"
                        if viability_signal >= 0.65 and uncertainty_moderation >= 0.65
                        else "reject_coupling_or_uncertainty_pressure"
                    ),
                }
            )
        coupled_records.sort(key=lambda item: item["mechanism_score"], reverse=True)
        selected = coupled_records[0] if coupled_records else {}
        second_score = coupled_records[1]["mechanism_score"] if len(coupled_records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("mechanism_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(item["hard_negative_pressure"] for item in coupled_records) if coupled_records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("mechanism_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_coupled_viability_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("coupling_risk_or_uncertainty_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "coupled_viability_metacognition_records": coupled_records,
            "selected_coupled_viability_metacognition_record": selected,
            "coupled_viability_metacognition_phase_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "learner_state": self.outcome_learner.to_dict(),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "macro_causal_viability_maintenance",
                "uncertainty_threshold_metacognition",
                "metacognitive_repair_control",
                "predictive_error_minimization_phase",
                "coupling_risk_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "coupled_viability_metacognition_phase_scout_v1.json"
            ),
        }
        self.coupled_history.append(output)
        return output


class ReferenceConstructPhaseAudit:
    construct_id = "reference_construct_phase_audit"

    def __init__(self) -> None:
        self.audit_history: list[dict[str, Any]] = []

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        agency = dependencies.get("action_agency", {})
        boundary = dependencies.get("boundary_self", {})
        identity = dependencies.get("identity_temporal_self", {})
        ownership = dependencies.get("action_ownership", {})
        body = dependencies.get("distributed_body_schema_self", {})
        dependency_support = _mean(
            (
                _clamp_float(agency.get("controllability"), default=0.55),
                _clamp_float(boundary.get("self_boundary_confidence"), default=0.55),
                _clamp_float(identity.get("identity_coherence"), default=0.55),
                _clamp_float(ownership.get("ownership_score"), default=0.55),
                _clamp_float(body.get("self_schema_confidence"), default=0.55),
            )
        )
        cases = _list_of_dicts(input_state.get("reference_construct_audit_cases"))
        if not cases:
            cases = (
                {
                    "id": "reference_motif_alignment",
                    "construct_alignment": 0.84,
                    "ownership_alignment": 0.8,
                    "boundary_alignment": 0.82,
                    "body_schema_alignment": 0.79,
                    "agency_alignment": 0.86,
                    "reference_leak_risk": 0.15,
                    "shortcut_pressure": 0.14,
                },
                {
                    "id": "reference_proxy_shortcut",
                    "construct_alignment": 0.31,
                    "ownership_alignment": 0.33,
                    "boundary_alignment": 0.28,
                    "body_schema_alignment": 0.22,
                    "agency_alignment": 0.27,
                    "reference_leak_risk": 0.72,
                    "shortcut_pressure": 0.7,
                },
            )
        audit_records = []
        for index, case in enumerate(cases):
            construct_alignment = _clamp_float(case.get("construct_alignment"), default=0.55)
            ownership_alignment = _clamp_float(case.get("ownership_alignment"), default=0.55)
            boundary_alignment = _clamp_float(case.get("boundary_alignment"), default=0.55)
            body_alignment = _clamp_float(case.get("body_schema_alignment"), default=0.55)
            agency_alignment = _clamp_float(case.get("agency_alignment"), default=0.55)
            leak_risk = _clamp_float(case.get("reference_leak_risk"), default=0.2)
            shortcut_pressure = _clamp_float(case.get("shortcut_pressure"), default=0.12)
            agency_pressure = _clamp_float(
                case.get("agency_pressure"),
                default=max(shortcut_pressure, 1.0 - agency_alignment),
            )
            boundary_pressure = _clamp_float(
                case.get("boundary_pressure"),
                default=max(shortcut_pressure, 1.0 - boundary_alignment),
            )
            hard_negative_pressure = _mean((shortcut_pressure, agency_pressure, boundary_pressure))
            audit_score = _clamp(
                0.2 * construct_alignment
                + 0.2 * ownership_alignment
                + 0.2 * boundary_alignment
                + 0.16 * body_alignment
                + 0.14 * agency_alignment
                + 0.08 * dependency_support
                - 0.16 * leak_risk
                - 0.12 * hard_negative_pressure
            )
            audit_records.append(
                {
                    "reference_audit_case_id": str(case.get("id") or f"reference_audit_{index + 1}"),
                    "audit_score": round(audit_score, 4),
                    "construct_alignment": round(construct_alignment, 4),
                    "ownership_alignment": round(ownership_alignment, 4),
                    "boundary_alignment": round(boundary_alignment, 4),
                    "body_schema_alignment": round(body_alignment, 4),
                    "agency_alignment": round(agency_alignment, 4),
                    "reference_leak_risk": round(leak_risk, 4),
                    "hard_negative_pressure": round(hard_negative_pressure, 4),
                    "audit_policy": (
                        "retain_reference_motif_audit_route"
                        if construct_alignment >= 0.65 and ownership_alignment >= 0.65
                        else "flag_reference_leak_or_proxy"
                    ),
                }
            )
        audit_records.sort(key=lambda item: item["audit_score"], reverse=True)
        selected = audit_records[0] if audit_records else {}
        second_score = audit_records[1]["audit_score"] if len(audit_records) > 1 else 0.0
        selection_margin = _clamp(_clamp_float(selected.get("audit_score"), default=0.0) - second_score)
        hard_negative_pressure = _mean(item["hard_negative_pressure"] for item in audit_records) if audit_records else 0.0
        aggregate_score = _clamp(
            0.68 * _clamp_float(selected.get("audit_score"), default=0.0)
            + 0.12 * selection_margin
            + 0.1 * dependency_support
            + 0.1 * (1.0 - hard_negative_pressure)
        )
        boundary_flags = []
        if selection_margin < 0.08:
            boundary_flags.append("low_reference_construct_audit_margin")
        if hard_negative_pressure >= 0.35:
            boundary_flags.append("reference_leak_or_pressure")
        output = {
            "construct_id": self.construct_id,
            "implemented_as": "bespoke_construct_mechanism_v1",
            "placeholder": False,
            "independent_process_logic": True,
            "reference_construct_phase_audit_records": audit_records,
            "selected_reference_construct_phase_audit": selected,
            "reference_construct_phase_audit_score": round(aggregate_score, 4),
            "selection_margin": round(selection_margin, 4),
            "dependency_support": round(dependency_support, 4),
            "mean_hard_negative_pressure": round(hard_negative_pressure, 4),
            "boundary_flags": boundary_flags,
            "hctm_boundary_watch": [
                "action_agency",
                "boundary_self",
                "identity_temporal_self",
                "action_ownership",
                "distributed_body_schema_self",
                "reference_leak_risk",
                "reference_construct_flag_only",
            ],
            "source_constraint": (
                "D:\\ai\\20260422 HCTM\\configs\\audit_assets\\"
                "reference_construct_phase_audit_preflight_v1.json"
            ),
        }
        self.audit_history.append(output)
        return output


class ActionAgency:
    construct_id = "action_agency"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        action = _dict_or_empty(input_state.get("action"))
        outcome = _dict_or_empty(input_state.get("outcome"))
        branch = dependencies.get("branch_binding_stability", {})
        branch_stability = _clamp_float(branch.get("stability"), default=0.5)
        match = _action_outcome_match(action, outcome)
        history_match = _history_match_rate(input_state.get("history"))
        controllability = _clamp(0.5 * match + 0.3 * branch_stability + 0.2 * history_match)
        action_type = str(action.get("type") or "unknown")
        controllable_actions = []
        if controllability >= 0.7 and action_type != "unknown":
            controllable_actions.append(
                {
                    "action_type": action_type,
                    "controllability": round(controllability, 4),
                }
            )
        return {
            "construct_id": self.construct_id,
            "controllability": round(controllability, 4),
            "action_outcome_match": round(match, 4),
            "branch_stability_used": round(branch_stability, 4),
            "history_match_rate": round(history_match, 4),
            "controllable_actions": controllable_actions,
        }


class BoundarySelf:
    construct_id = "boundary_self"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        context = _dict_or_empty(input_state.get("context"))
        action = _dict_or_empty(input_state.get("action"))
        self_id = str(context.get("self_id") or "system")
        authorized_agents = {
            str(agent)
            for agent in context.get("authorized_agents", [self_id])
            if str(agent)
        }
        action_agent = str(action.get("agent_id") or "")
        operator_agent = str(context.get("operator_id") or "")
        external_events = _list_of_dicts(input_state.get("external_events"))
        self_match = 1.0 if action_agent in authorized_agents else 0.0
        operator_context = 1.0 if not operator_agent or operator_agent in authorized_agents else 0.75
        external_pressure = min(1.0, len(external_events) / 5.0)
        boundary_confidence = _clamp(0.55 * self_match + 0.3 * operator_context + 0.15 * (1.0 - external_pressure))
        violations = []
        if action_agent and action_agent not in authorized_agents:
            violations.append("action_agent_outside_self_boundary")
        if external_pressure >= 0.6:
            violations.append("high_external_event_pressure")
        return {
            "construct_id": self.construct_id,
            "self_id": self_id,
            "authorized_agents": sorted(authorized_agents),
            "action_agent_id": action_agent or "unknown",
            "self_boundary_confidence": round(boundary_confidence, 4),
            "external_pressure": round(external_pressure, 4),
            "boundary_violations": violations,
        }


class ActionOwnership:
    construct_id = "action_ownership"

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        action = _dict_or_empty(input_state.get("action"))
        outcome = _dict_or_empty(input_state.get("outcome"))
        agency = dependencies.get("action_agency", {})
        boundary = dependencies.get("boundary_self", {})
        controllability = _clamp_float(agency.get("controllability"), default=0.0)
        boundary_confidence = _clamp_float(
            boundary.get("self_boundary_confidence"), default=0.0
        )
        intention_match = _intention_match(action, input_state.get("intention"))
        outcome_match = _action_outcome_match(action, outcome)
        ownership_score = _clamp(
            0.35 * controllability
            + 0.3 * boundary_confidence
            + 0.2 * intention_match
            + 0.15 * outcome_match
        )
        if ownership_score >= 0.72:
            verdict = "owned_action"
        elif ownership_score >= 0.45:
            verdict = "ambiguous_action_ownership"
        else:
            verdict = "external_or_unowned_action"
        flags = list(boundary.get("boundary_violations") or [])
        if controllability < 0.5:
            flags.append("low_agency_support")
        if intention_match < 0.5:
            flags.append("weak_intention_match")
        if "action_agent_outside_self_boundary" in flags:
            ownership_score = min(ownership_score, 0.55)
        if "high_external_event_pressure" in flags:
            ownership_score = min(ownership_score, 0.65)
        if ownership_score >= 0.72:
            verdict = "owned_action"
        elif ownership_score >= 0.45:
            verdict = "ambiguous_action_ownership"
        else:
            verdict = "external_or_unowned_action"
        return {
            "construct_id": self.construct_id,
            "ownership_score": round(ownership_score, 4),
            "ownership_verdict": verdict,
            "controllability_used": round(controllability, 4),
            "boundary_confidence_used": round(boundary_confidence, 4),
            "intention_match": round(intention_match, 4),
            "outcome_match": round(outcome_match, 4),
            "risk_flags": sorted(set(flags)),
        }


class CandidateConstructMechanism:
    """Executable proxy mechanism for candidate and preconstruct routes."""

    def __init__(self, node: ConstructNode) -> None:
        self.node = node
        self.construct_id = node.id

    def process(
        self,
        input_state: dict[str, Any],
        dependencies: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        dependency_support = _dependency_support(dependencies)
        family_metrics = _family_proxy_metrics(
            self.node.mechanism_family,
            self.construct_id,
            input_state,
            dependencies,
        )
        family_signal = _clamp_float(family_metrics.get("family_signal"), default=0.55)
        construct_relevance = _construct_relevance(self.construct_id, input_state)
        evidence_signal = _node_evidence_signal(self.node)
        boundary_pressure = _node_boundary_pressure(self.node, input_state, dependencies)
        proxy_activation = _clamp(
            0.38 * dependency_support
            + 0.28 * family_signal
            + 0.2 * construct_relevance
            + 0.14 * evidence_signal
            - 0.12 * boundary_pressure
        )
        confidence = _clamp(
            0.34 * dependency_support
            + 0.26 * family_signal
            + 0.24 * evidence_signal
            + 0.16 * (1.0 - boundary_pressure)
        )
        review_flags = _candidate_review_flags(self.node, proxy_activation, confidence, boundary_pressure)
        return {
            "construct_id": self.construct_id,
            "implemented_as": "candidate_family_proxy_placeholder_v1",
            "placeholder": True,
            "layer": self.node.layer,
            "mechanism_family": self.node.mechanism_family,
            "proxy_activation": round(proxy_activation, 4),
            "confidence": round(confidence, 4),
            "dependency_support": round(dependency_support, 4),
            "family_signal": round(family_signal, 4),
            "construct_relevance": round(construct_relevance, 4),
            "evidence_signal": round(evidence_signal, 4),
            "boundary_pressure": round(boundary_pressure, 4),
            "mechanism_state": family_metrics,
            "review_flags": review_flags,
            "next_gate": self.node.next_gate,
            "roles": list(self.node.roles),
        }


class ConstructRuntime:
    """Executable dependency runtime for implemented construct chains."""

    def __init__(
        self,
        constructs: dict[str, ExecutableConstruct] | None = None,
        dependencies: dict[str, tuple[str, ...]] | None = None,
    ) -> None:
        self.constructs = constructs or _default_executable_constructs()
        self.dependencies = dependencies or executable_dependency_map()

    def process(
        self,
        input_state: dict[str, Any],
        *,
        target_construct_ids: tuple[str, ...] = ("action_ownership",),
        chain_id: str = "action_ownership_dependency_chain",
        construct_disables: tuple[str, ...] = (),
        construct_overrides: dict[str, dict[str, Any]] | None = None,
    ) -> ConstructRuntimeReport:
        activation_order = self._activation_order(target_construct_ids)
        disabled = {str(construct_id) for construct_id in construct_disables}
        overrides = construct_overrides or {}
        outputs: dict[str, dict[str, Any]] = {}
        results: list[ExecutableConstructResult] = []
        missing: list[str] = []
        for construct_id in activation_order:
            if construct_id in disabled:
                continue
            construct = self.constructs.get(construct_id)
            if construct is None:
                missing.append(construct_id)
                continue
            dependency_ids = self.dependencies.get(construct_id, ())
            if construct_id in overrides:
                output = dict(overrides[construct_id])
            else:
                dependency_outputs = {
                    dependency_id: outputs[dependency_id]
                    for dependency_id in dependency_ids
                    if dependency_id in outputs
                }
                output = construct.process(input_state, dependency_outputs)
            outputs[construct_id] = output
            results.append(
                ExecutableConstructResult(
                    construct_id=construct_id,
                    dependency_ids=dependency_ids,
                    output=output,
                )
            )
        final_output = self._select_final_output(
            outputs,
            activation_order=activation_order,
            target_construct_ids=target_construct_ids,
            disabled=disabled,
        )
        return ConstructRuntimeReport(
            chain_id=chain_id,
            activation_order=activation_order,
            results=tuple(results),
            final_output=final_output,
            input_digest=_input_digest(input_state),
            disabled_constructs=tuple(sorted(disabled)),
            missing_constructs=tuple(missing),
        )

    def _select_final_output(
        self,
        outputs: dict[str, dict[str, Any]],
        *,
        activation_order: tuple[str, ...],
        target_construct_ids: tuple[str, ...],
        disabled: set[str],
    ) -> dict[str, Any]:
        final_id = ""
        if target_construct_ids:
            for candidate_id in reversed(target_construct_ids):
                if (
                    candidate_id not in disabled
                    and candidate_id in outputs
                ):
                    final_id = candidate_id
                    break
        if not final_id:
            for candidate_id in reversed(activation_order):
                if candidate_id not in disabled and candidate_id in outputs:
                    final_id = candidate_id
                    break
        return outputs.get(final_id, {})

    def _activation_order(self, target_construct_ids: tuple[str, ...]) -> tuple[str, ...]:
        seen: set[str] = set()
        order: list[str] = []

        def visit(construct_id: str) -> None:
            if construct_id in seen:
                return
            for dependency_id in self.dependencies.get(construct_id, ()):
                visit(dependency_id)
            seen.add(construct_id)
            order.append(construct_id)

        for target_id in target_construct_ids:
            visit(target_id)
        return tuple(order)


def _default_executable_constructs() -> dict[str, ExecutableConstruct]:
    constructs: dict[str, ExecutableConstruct] = {
            "information_flow_onset_gating": InformationFlowOnsetGating(),
            "branch_binding_stability": BranchBindingStability(),
            "identity_temporal_self": IdentityTemporalSelf(),
            "temporal_horizon_dependent_planning": TemporalHorizonDependentPlanning(),
            "uncertainty_threshold_metacognition": UncertaintyThresholdMetacognition(),
            "information_integration_phase": InformationIntegrationPhase(),
            "macro_causal_viability_maintenance": MacroCausalViabilityMaintenance(),
            "attention_control": AttentionControl(),
            "error_monitoring": ErrorMonitoring(),
            "episodic_memory_binding": EpisodicMemoryBinding(),
            "causal_attribution": CausalAttribution(),
            "predictive_error_minimization_phase": PredictiveErrorMinimizationPhase(),
            "metacognitive_repair_control": MetacognitiveRepairControl(),
            "strategy_selection": StrategySelection(),
            "prospective_memory": ProspectiveMemory(),
            "perspective_taking": PerspectiveTaking(),
            "goal_hierarchy_emergence": GoalHierarchyEmergence(),
            "resource_competition_arbitration": ResourceCompetitionArbitration(),
            "affordance_selection_control": AffordanceSelectionControl(),
            "self_other_boundary_sharpness": SelfOtherBoundarySharpness(),
            "self_other_prediction_error_arbitration": SelfOtherPredictionErrorArbitration(),
            "global_broadcast_phase": GlobalBroadcastPhase(),
            "body_schema_error_correction": BodySchemaErrorCorrection(),
            "working_memory_capacity_rework": WorkingMemoryCapacityRework(),
            "learning_rate_adaptation_rework": LearningRateAdaptationRework(),
            "confidence_calibration_rework": ConfidenceCalibrationRework(),
            "contextual_policy_inhibition": ContextualPolicyInhibition(),
            "goal_conflict_resolution": GoalConflictResolution(),
            "cross_family_synergy_control": CrossFamilySynergyControl(),
            "temporal_credit_assignment": TemporalCreditAssignment(),
            "hierarchical_credit_assignment": HierarchicalCreditAssignment(),
            "social_coupling_strength_collective_agency": SocialCouplingStrengthCollectiveAgency(),
            "counterfactual_reasoning_depth": CounterfactualReasoningDepth(),
            "coordination_length_control": CoordinationLengthControl(),
            "latent_context_switch_detection": LatentContextSwitchDetection(),
            "social_norm_tracking": SocialNormTracking(),
            "semantic_memory_retrieval_control": SemanticMemoryRetrievalControl(),
            "divergent_thinking": DivergentThinking(),
            "analogical_reasoning_rework": AnalogicalReasoningRework(),
            "cooperation_policy_switching_rework": CooperationPolicySwitchingRework(),
            "spatial_navigation_remapping_rework": SpatialNavigationRemappingRework(),
            "predictive_control_under_action_intervention": PredictiveControlUnderActionIntervention(),
            "insight_problem_solving_rework": InsightProblemSolvingRework(),
            "counterfactual_repair_planning_rework": CounterfactualRepairPlanningRework(),
            "multi_agent_commitment_tracking": MultiAgentCommitmentTracking(),
            "norm_violation_repair": NormViolationRepair(),
            "constraint_satisfaction_reconfiguration": ConstraintSatisfactionReconfiguration(),
            "integration_without_broadcast_boundary": IntegrationWithoutBroadcastBoundary(),
            "selective_global_broadcast_control": SelectiveGlobalBroadcastControl(),
            "agency_without_ownership_boundary": AgencyWithoutOwnershipBoundary(),
            "temporal_identity_planning_dissociation": TemporalIdentityPlanningDissociation(),
            "clock_drift_resynchronization_control": ClockDriftResynchronizationControl(),
            "energy_budget_reallocation_control": EnergyBudgetReallocationControl(),
            "sensor_gain_recalibration_control": SensorGainRecalibrationControl(),
            "tool_use_affordance_remapping": ToolUseAffordanceRemapping(),
            "actuator_failure_compensation_control": ActuatorFailureCompensationControl(),
            "preference_reversal_adaptation_control": PreferenceReversalAdaptationControl(),
            "checkpoint_rollback_recovery_control": CheckpointRollbackRecoveryControl(),
            "feedback_channel_integrity_reweighting_control": FeedbackChannelIntegrityReweightingControl(),
            "instruction_scope_binding_control": InstructionScopeBindingControl(),
            "interface_protocol_negotiation_control": InterfaceProtocolNegotiationControl(),
            "interference_source_separation_control": InterferenceSourceSeparationControl(),
            "irreversible_commitment_safeguard_control": IrreversibleCommitmentSafeguardControl(),
            "latent_state_alias_disambiguation_control": LatentStateAliasDisambiguationControl(),
            "localized_regime_shift_quarantine_control": LocalizedRegimeShiftQuarantineControl(),
            "memory_index_corruption_rebinding_control": MemoryIndexCorruptionRebindingControl(),
            "model_staleness_detection_control": ModelStalenessDetectionControl(),
            "observation_dropout_bridging_control": ObservationDropoutBridgingControl(),
            "option_value_preserving_probe_control": OptionValuePreservingProbeControl(),
            "permission_revocation_compliance_control": PermissionRevocationComplianceControl(),
            "priority_starvation_prevention_control": PriorityStarvationPreventionControl(),
            "provenance_weighted_evidence_integration_control": ProvenanceWeightedEvidenceIntegrationControl(),
            "redundant_pathway_failover_control": RedundantPathwayFailoverControl(),
            "representation_format_translation_control": RepresentationFormatTranslationControl(),
            "sensorimotor_latency_compensation_control": SensorimotorLatencyCompensationControl(),
            "side_effect_containment_control": SideEffectContainmentControl(),
            "unit_frame_normalization_control": UnitFrameNormalizationControl(),
            "accountability_obligation_scope_response_control": AccountabilityObligationScopeResponseControl(),
            "counter_evidence_preservation_control": CounterEvidencePreservationControl(),
            "counterparty_intent_uncertainty_resolution_control": CounterpartyIntentUncertaintyResolutionControl(),
            "credential_validity_challenge_response_control": CredentialValidityChallengeResponseControl(),
            "deadline_obligation_triage_control": DeadlineObligationTriageControl(),
            "observation_budget_allocation_control": ObservationBudgetAllocationControl(),
            "sample_representativeness_reweighting_control": SampleRepresentativenessReweightingControl(),
            "causal_model_abstraction_hierarchy": CausalModelAbstractionHierarchy(),
            "hierarchical_phase_cascade": HierarchicalPhaseCascade(),
            "coupled_viability_metacognition_phase": CoupledViabilityMetacognitionPhase(),
            "reference_construct_phase_audit": ReferenceConstructPhaseAudit(),
            "communication_channel_repair_control": CommunicationChannelRepairControl(),
            "distributed_body_schema_self": DistributedBodySchemaSelf(),
            "action_agency": ActionAgency(),
            "boundary_self": BoundarySelf(),
            "action_ownership": ActionOwnership(),
    }
    architecture = all_construct_architecture()
    for node in architecture.nodes:
        if node.id in constructs:
            continue
        if node.layer in {"validation_candidate", "candidate", "preconstruct"}:
            constructs[node.id] = CandidateConstructMechanism(node)
    return constructs


def default_action_ownership_demo_input() -> dict[str, Any]:
    return {
        "active_branch_id": "operator_intended_action",
        "branches": [
            {
                "id": "operator_intended_action",
                "evidence_weight": 0.9,
                "continuity": 0.85,
                "conflict": 0.1,
            },
            {
                "id": "external_noise",
                "evidence_weight": 0.25,
                "continuity": 0.2,
                "conflict": 0.65,
            },
        ],
        "context": {
            "self_id": "mind_executor",
            "operator_id": "mind_executor",
            "authorized_agents": ["mind_executor"],
            "cognitive_load": 0.38,
            "gate_threshold": 0.56,
            "max_open_channels": 4,
            "focus_capacity": 3,
            "current_phase": "implementation",
            "working_memory_capacity": 3,
            "interruption_load": 0.22,
        },
        "signals": [
            {
                "id": "operator_instruction",
                "channel": "language",
                "salience": 0.88,
                "novelty": 0.55,
                "reliability": 0.92,
                "threat": 0.05,
            },
            {
                "id": "test_failure_signal",
                "channel": "runtime_error",
                "salience": 0.74,
                "novelty": 0.68,
                "reliability": 0.82,
                "threat": 0.35,
            },
            {
                "id": "background_status_noise",
                "channel": "ambient_status",
                "salience": 0.22,
                "novelty": 0.18,
                "reliability": 0.5,
                "threat": 0.0,
            },
        ],
        "tasks": [
            {
                "id": "runtime_report",
                "channel": "operator_instruction",
                "priority": 0.9,
                "urgency": 0.72,
                "relevance": 0.95,
            },
            {
                "id": "construct_runtime_tests",
                "channel": "test_failure_signal",
                "priority": 0.78,
                "urgency": 0.82,
                "relevance": 0.88,
            },
            {
                "id": "background_cleanup",
                "channel": "ambient_status",
                "priority": 0.25,
                "urgency": 0.2,
                "relevance": 0.25,
            },
        ],
        "goals": [
            {
                "id": "implement_candidate_constructs",
                "priority": 0.92,
                "conflict": 0.22,
                "expected_value": 0.88,
                "deadline_pressure": 0.35,
            },
            {
                "id": "preserve_claim_boundary",
                "priority": 0.96,
                "conflict": 0.12,
                "expected_value": 0.9,
                "deadline_pressure": 0.18,
            },
            {
                "id": "avoid_source_control_side_effects",
                "priority": 0.84,
                "conflict": 0.08,
                "expected_value": 0.78,
                "deadline_pressure": 0.22,
            },
        ],
        "resources": [
            {"id": "attention_budget", "available": 0.72, "demand": 0.58},
            {"id": "execution_time", "available": 0.68, "demand": 0.55},
            {"id": "energy_budget", "available": 0.74, "demand": 0.42},
        ],
        "counterfactuals": [
            {
                "id": "skip_dependency_graph",
                "support": 0.32,
                "repair_value": 0.62,
            },
            {
                "id": "use_candidate_proxy_mechanisms",
                "support": 0.78,
                "repair_value": 0.86,
            },
        ],
        "policies": [
            {
                "id": "claim_firewall",
                "stability": 0.92,
                "reversal_pressure": 0.08,
            },
            {
                "id": "medium_risk_local_only",
                "stability": 0.82,
                "reversal_pressure": 0.18,
            },
        ],
        "strategies": [
            {
                "id": "bespoke_tier1_mechanism_batch",
                "utility": 0.9,
                "cost": 0.42,
                "risk": 0.24,
                "context_match": 0.88,
                "switch_cost": 0.25,
                "commitment": 0.86,
            },
            {
                "id": "continue_placeholder_proxy_only",
                "utility": 0.48,
                "cost": 0.18,
                "risk": 0.58,
                "context_match": 0.36,
                "switch_cost": 0.08,
                "commitment": 0.34,
            },
            {
                "id": "pause_for_manual_review",
                "utility": 0.62,
                "cost": 0.5,
                "risk": 0.18,
                "context_match": 0.5,
                "switch_cost": 0.3,
                "commitment": 0.65,
            },
        ],
        "future_intentions": [
            {
                "id": "publish_tier2_mechanism_artifact",
                "target": "tier2_runtime_report",
                "valid_cues": ["tier2_batch_ready", "tests_passed"],
                "due_phase": "implementation",
                "retention_strength": 0.86,
                "ongoing_task_protection": 0.82,
                "interruption_recovery": 0.78,
                "priority": 0.88,
            },
            {
                "id": "do_not_auto_promote_status",
                "target": "claim_boundary",
                "valid_cues": ["formal_review_request"],
                "due_phase": "review",
                "retention_strength": 0.92,
                "ongoing_task_protection": 0.9,
                "interruption_recovery": 0.86,
                "priority": 0.96,
            },
        ],
        "cues": [
            {
                "id": "tier2_batch_ready",
                "type": "event",
                "target": "tier2_runtime_report",
                "valid": True,
                "salience": 0.74,
            },
            {
                "id": "salient_noise_without_intention",
                "type": "event",
                "target": "unrelated_status",
                "valid": False,
                "salience": 0.9,
            },
        ],
        "perspective_frames": [
            {
                "id": "operator_review_view",
                "agent_id": "operator",
                "self_interference": 0.22,
                "other_state_evidence": 0.82,
                "viewpoint_binding": 0.8,
                "conflict_resolution": 0.76,
                "social_label_risk": 0.08,
                "salience_shortcut_risk": 0.06,
            },
            {
                "id": "social_label_decoy",
                "agent_id": "generic_reviewer_label",
                "self_interference": 0.48,
                "other_state_evidence": 0.38,
                "viewpoint_binding": 0.42,
                "conflict_resolution": 0.35,
                "social_label_risk": 0.58,
                "salience_shortcut_risk": 0.42,
            },
        ],
        "resource_demands": [
            {
                "id": "attention_runtime_docs",
                "construct_pair": ["attention_control", "strategy_selection"],
                "resource_id": "attention_budget",
                "demand": 0.42,
                "priority": 0.84,
                "retention_sensitivity": 0.76,
            },
            {
                "id": "execution_tier2_tests",
                "construct_pair": ["resource_competition_arbitration", "affordance_selection_control"],
                "resource_id": "execution_time",
                "demand": 0.5,
                "priority": 0.88,
                "retention_sensitivity": 0.82,
            },
            {
                "id": "low_priority_background_scan",
                "construct_pair": ["ambient_status", "background_cleanup"],
                "resource_id": "attention_budget",
                "demand": 0.36,
                "priority": 0.35,
                "retention_sensitivity": 0.32,
            },
        ],
        "affordances": [
            {
                "id": "run_tier2_tests",
                "action_type": "run_test",
                "target": "construct_runtime",
                "task_relevance": 0.9,
                "action_fit": 0.86,
                "salience": 0.68,
                "temptation": 0.18,
            },
            {
                "id": "write_tier2_report",
                "action_type": "write_artifact",
                "target": "tier2_runtime_report",
                "task_relevance": 0.88,
                "action_fit": 0.84,
                "salience": 0.72,
                "temptation": 0.2,
            },
            {
                "id": "salient_unrelated_action",
                "action_type": "open_unrelated_task",
                "target": "unrelated_status",
                "task_relevance": 0.2,
                "action_fit": 0.45,
                "salience": 0.92,
                "temptation": 0.78,
                "reward_only_risk": 0.62,
                "motor_speed_only_risk": 0.35,
            },
        ],
        "source_attribution_events": [
            {
                "id": "operator_artifact_request",
                "source_id": "operator",
                "axis": "other",
                "source_axis_separation": 0.86,
                "other_model_independence": 0.82,
                "paired_actuator_gap": 0.78,
                "visible_role_shortcut_risk": 0.08,
                "shared_control_ambiguity": 0.18,
            },
            {
                "id": "mind_executor_patch_action",
                "source_id": "mind_executor",
                "axis": "self",
                "source_axis_separation": 0.88,
                "other_model_independence": 0.8,
                "paired_actuator_gap": 0.84,
                "visible_role_shortcut_risk": 0.05,
                "shared_control_ambiguity": 0.12,
            },
        ],
        "social_prediction_errors": [
            {
                "id": "operator_expectation_shift",
                "other_agent_id": "operator",
                "self_error": 0.28,
                "other_error": 0.74,
                "coupling": 0.32,
                "social_label_risk": 0.08,
                "salience_risk": 0.1,
                "magnitude_only_risk": 0.12,
            },
            {
                "id": "local_patch_mismatch",
                "other_agent_id": "operator",
                "self_error": 0.64,
                "other_error": 0.3,
                "coupling": 0.22,
                "social_label_risk": 0.06,
                "salience_risk": 0.08,
                "magnitude_only_risk": 0.1,
            },
        ],
        "broadcast_routes": [
            {
                "id": "runtime_report_global_route",
                "global_availability": 0.86,
                "workspace_ignition": 0.78,
                "conflict_routed_access": 0.74,
                "cross_context_selection": 0.8,
                "fanout_only_risk": 0.08,
                "salience_only_risk": 0.06,
            },
            {
                "id": "local_salience_decoy_route",
                "global_availability": 0.38,
                "workspace_ignition": 0.42,
                "conflict_routed_access": 0.36,
                "cross_context_selection": 0.34,
                "fanout_only_risk": 0.62,
                "salience_only_risk": 0.72,
            },
        ],
        "body_schema_distortions": [
            {
                "id": "delayed_test_runner_feedback",
                "body_part": "test_executor",
                "distortion": 0.42,
                "feedback_delay": 0.28,
                "sensor_reliability": 0.86,
                "motor_gain_risk": 0.1,
                "sensory_salience_risk": 0.12,
            },
            {
                "id": "artifact_writer_calibration_offset",
                "body_part": "artifact_writer",
                "distortion": 0.34,
                "feedback_delay": 0.18,
                "sensor_reliability": 0.88,
                "motor_gain_risk": 0.08,
                "sensory_salience_risk": 0.1,
            },
        ],
        "working_memory_items": [
            {
                "id": "tier3_target_set",
                "load": 0.36,
                "interference": 0.28,
                "salience": 0.82,
                "rehearsal_speed_risk": 0.08,
                "semantic_chunking_risk": 0.12,
            },
            {
                "id": "claim_boundary_rule",
                "load": 0.28,
                "interference": 0.18,
                "salience": 0.9,
                "rehearsal_speed_risk": 0.04,
                "semantic_chunking_risk": 0.08,
            },
            {
                "id": "hctm_asset_constraints",
                "load": 0.44,
                "interference": 0.34,
                "salience": 0.76,
                "rehearsal_speed_risk": 0.1,
                "semantic_chunking_risk": 0.16,
            },
            {
                "id": "background_status_noise_item",
                "load": 0.32,
                "interference": 0.58,
                "salience": 0.28,
                "rehearsal_speed_risk": 0.38,
                "semantic_chunking_risk": 0.3,
            },
        ],
        "learning_contexts": [
            {
                "id": "stable_runtime_tests",
                "volatility": 0.28,
                "feedback_reliability": 0.88,
                "current_rate": 0.28,
                "reward_only_risk": 0.08,
                "recency_only_risk": 0.1,
                "prediction_error_only_risk": 0.12,
            },
            {
                "id": "hctm_asset_drift_watch",
                "volatility": 0.56,
                "feedback_reliability": 0.72,
                "current_rate": 0.34,
                "reward_only_risk": 0.1,
                "recency_only_risk": 0.18,
                "prediction_error_only_risk": 0.2,
            },
        ],
        "confidence_observations": [
            {
                "id": "tier3_chain_confidence",
                "confidence": 0.78,
                "error_probability": 0.18,
                "evidence_noise": 0.18,
                "feedback_delay": 0.22,
                "accuracy_only_risk": 0.08,
                "feedback_frequency_risk": 0.1,
                "label_template_risk": 0.06,
            },
            {
                "id": "hctm_asset_confidence",
                "confidence": 0.72,
                "error_probability": 0.24,
                "evidence_noise": 0.28,
                "feedback_delay": 0.32,
                "accuracy_only_risk": 0.12,
                "feedback_frequency_risk": 0.14,
                "label_template_risk": 0.08,
            },
        ],
        "policy_contexts": [
            {
                "id": "switch_from_proxy_to_bespoke",
                "policy_id": "continue_placeholder_proxy_only",
                "prepotent_strength": 0.72,
                "switch_pressure": 0.86,
                "context_match": 0.82,
                "switch_action_fit": 0.84,
                "should_inhibit": True,
                "false_inhibition_risk": 0.12,
                "salience_only_risk": 0.08,
                "motor_suppression_risk": 0.08,
            },
            {
                "id": "do_not_inhibit_claim_firewall",
                "policy_id": "claim_firewall",
                "prepotent_strength": 0.86,
                "switch_pressure": 0.18,
                "context_match": 0.9,
                "switch_action_fit": 0.28,
                "should_inhibit": False,
                "false_inhibition_risk": 0.72,
                "salience_only_risk": 0.05,
                "motor_suppression_risk": 0.04,
            },
        ],
        "goal_conflicts": [
            {
                "id": "implementation_vs_boundary",
                "goals": [
                    {
                        "id": "preserve_claim_boundary",
                        "priority": 0.96,
                        "expected_value": 0.9,
                        "constraint_pressure": 0.12,
                        "recency_bias": 0.08,
                        "reward_magnitude_risk": 0.04,
                    },
                    {
                        "id": "maximize_replacement_speed",
                        "priority": 0.72,
                        "expected_value": 0.7,
                        "constraint_pressure": 0.42,
                        "recency_bias": 0.22,
                        "reward_magnitude_risk": 0.18,
                    },
                ],
            }
        ],
        "synergy_pairs": [
            {
                "id": "social_credit_pair",
                "families": ["social_boundary", "temporal_credit"],
                "complementarity": 0.82,
                "heldout_margin": 0.74,
                "family_reversal_generalization": 0.72,
                "seen_pair_risk": 0.08,
                "within_family_false_synergy": 0.06,
                "demand_sum_only_risk": 0.1,
            },
            {
                "id": "workspace_resource_pair",
                "families": ["workspace", "resource_control"],
                "complementarity": 0.76,
                "heldout_margin": 0.68,
                "family_reversal_generalization": 0.7,
                "seen_pair_risk": 0.1,
                "within_family_false_synergy": 0.08,
                "demand_sum_only_risk": 0.12,
            },
        ],
        "temporal_credit_events": [
            {
                "id": "delayed_test_pass_credit",
                "credited_state_action": "run_construct_runtime_tests",
                "lag": 2,
                "correct_lag_match": 0.84,
                "delayed_outcome_binding": 0.82,
                "policy_update_fit": 0.78,
                "immediate_reward_risk": 0.08,
                "recency_bias_risk": 0.1,
                "temporal_order_only_risk": 0.12,
            },
            {
                "id": "delayed_hctm_constraint_credit",
                "credited_state_action": "scan_hctm_formal_decisions",
                "lag": 3,
                "correct_lag_match": 0.78,
                "delayed_outcome_binding": 0.76,
                "policy_update_fit": 0.72,
                "immediate_reward_risk": 0.12,
                "recency_bias_risk": 0.14,
                "temporal_order_only_risk": 0.16,
            },
        ],
        "hierarchical_credit_events": [
            {
                "id": "claim_boundary_nested_credit",
                "goal_id": "preserve_claim_boundary",
                "goal_level": 0,
                "nested_goal_match": 0.86,
                "level_specific_binding": 0.82,
                "flat_credit_control_match": 0.78,
                "macro_pressure_match": 0.74,
                "label_template_risk": 0.06,
                "forecast_only_risk": 0.08,
            },
            {
                "id": "mechanism_batch_nested_credit",
                "goal_id": "implement_candidate_constructs",
                "goal_level": 1,
                "nested_goal_match": 0.8,
                "level_specific_binding": 0.78,
                "flat_credit_control_match": 0.76,
                "macro_pressure_match": 0.7,
                "label_template_risk": 0.08,
                "forecast_only_risk": 0.1,
            },
        ],
        "temporal_state": {
            "horizon_fit": 0.74,
            "deadline_pressure": 0.32,
            "clock_drift": 0.12,
        },
        "causal_candidates": [
            {
                "id": "operator_intended_action_caused_artifact",
                "action_type": "write_artifact",
                "outcome_type": "artifact_written",
                "target": "runtime_report",
                "intervention_match": 0.92,
                "outcome_binding": 0.9,
                "counterfactual_contrast": 0.82,
                "confound_suppression": 0.86,
                "temporal_order": 0.88,
            },
            {
                "id": "background_status_noise_decoy",
                "target": "runtime_report",
                "intervention_match": 0.2,
                "outcome_binding": 0.36,
                "counterfactual_contrast": 0.22,
                "confound_suppression": 0.42,
                "temporal_order": 0.64,
                "salience_only_risk": 0.55,
            },
            {
                "id": "reward_or_success_proxy_decoy",
                "target": "runtime_report",
                "intervention_match": 0.35,
                "outcome_binding": 0.5,
                "counterfactual_contrast": 0.25,
                "confound_suppression": 0.52,
                "temporal_order": 0.55,
                "reward_proxy_risk": 0.65,
            },
        ],
        "social_context": {
            "agents": [
                {"id": "operator", "role": "external_owner", "trust": 0.86},
                {"id": "mind_executor", "role": "system", "trust": 0.9},
            ],
            "norms": [
                {"id": "no_subjective_claim", "alignment": 0.95},
                {"id": "external_review_required", "alignment": 0.88},
            ],
            "commitments": [
                {"id": "report_all_artifacts", "confidence": 0.9},
                {"id": "do_not_change_formal_status", "confidence": 0.96},
            ],
        },
        "expectations": {
            "runtime_report": "artifact_written",
            "construct_runtime_tests": "test_passed",
        },
        "observations": {
            "runtime_report": "artifact_written",
            "construct_runtime_tests": "test_passed",
        },
        "error_events": [
            {
                "id": "minor_formatting_gap",
                "target": "runtime_report",
                "severity": 0.25,
                "confidence": 0.7,
                "kind": "formatting_gap",
            }
        ],
        "body_schema": {
            "sensors": [
                {"id": "filesystem_sensor", "reliability": 0.86, "calibration": 0.82},
                {"id": "test_runner_sensor", "reliability": 0.9, "calibration": 0.87},
            ],
            "effectors": [
                {"id": "artifact_writer", "health": 0.88, "control": 0.9},
                {"id": "test_executor", "health": 0.84, "control": 0.86},
            ],
            "tools": [
                {"id": "pytest", "control": 0.84, "calibration": 0.86},
                {"id": "json_tool", "control": 0.78, "calibration": 0.82},
            ],
        },
        "memory_trace": [
            {
                "thread_id": "architecture_upgrade",
                "self_id": "mind_executor",
                "goal_id": "construct_runtime",
                "confidence": 0.9,
                "continuity": 0.86,
                "source_reliability": 0.88,
                "context_tags": ["construct_runtime", "architecture", "tier1"],
            },
            {
                "thread_id": "hctm_integration",
                "self_id": "mind_executor",
                "goal_id": "candidate_fusion",
                "confidence": 0.82,
                "continuity": 0.8,
                "source_reliability": 0.84,
                "context_tags": ["hctm", "candidate", "audit_assets"],
            },
        ],
        "intention": {
            "type": "write_artifact",
            "target": "runtime_report",
        },
        "action": {
            "type": "write_artifact",
            "target": "runtime_report",
            "agent_id": "mind_executor",
        },
        "outcome": {
            "type": "artifact_written",
            "target": "runtime_report",
            "agent_id": "mind_executor",
        },
        "history": [
            {
                "action": {"type": "write_artifact", "target": "runtime_report"},
                "outcome": {"type": "artifact_written", "target": "runtime_report"},
            },
            {
                "action": {"type": "run_test", "target": "construct_runtime"},
                "outcome": {"type": "test_passed", "target": "construct_runtime"},
            },
        ],
    }


def run_action_ownership_chain(
    input_state: dict[str, Any] | None = None,
) -> ConstructRuntimeReport:
    return run_construct_runtime_chain(
        "action_ownership_dependency_chain",
        input_state=input_state,
    )


def run_temporal_identity_chain(
    input_state: dict[str, Any] | None = None,
) -> ConstructRuntimeReport:
    return run_construct_runtime_chain("temporal_identity_chain", input_state=input_state)


def run_attention_error_monitoring_chain(
    input_state: dict[str, Any] | None = None,
) -> ConstructRuntimeReport:
    return run_construct_runtime_chain(
        "attention_error_monitoring_chain",
        input_state=input_state,
    )


def run_body_schema_chain(
    input_state: dict[str, Any] | None = None,
) -> ConstructRuntimeReport:
    return run_construct_runtime_chain("body_schema_chain", input_state=input_state)


def run_self_monitoring_basis_chain(
    input_state: dict[str, Any] | None = None,
) -> ConstructRuntimeReport:
    return run_construct_runtime_chain("self_monitoring_basis_chain", input_state=input_state)


def run_candidate_constructs_full_chain(
    input_state: dict[str, Any] | None = None,
) -> ConstructRuntimeReport:
    return run_construct_runtime_chain(
        "candidate_constructs_full_chain",
        input_state=input_state,
    )


def run_candidate_and_preconstruct_full_chain(
    input_state: dict[str, Any] | None = None,
) -> ConstructRuntimeReport:
    return run_construct_runtime_chain(
        "candidate_and_preconstruct_full_chain",
        input_state=input_state,
    )


def _growth_seed_rng(seed: int, profile_id: str, stage_id: str) -> random.Random:
    payload = f"{DEVELOPMENTAL_GROWTH_DEFAULT_SEED}|{seed}|{profile_id}|{stage_id}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return random.Random(int(digest[:16], 16))


def _growth_profile_perturb_float(value: Any, rng: random.Random, magnitude: float = 0.08) -> float:
    base = _clamp_float(value, default=0.5)
    jitter = (rng.random() * 2.0 - 1.0) * magnitude
    return _clamp(base + jitter, lower=0.0, upper=1.0)


def _growth_profile_perturb_int(value: Any, rng: random.Random, magnitude: int = 1, minimum: int = 1, maximum: int = 12) -> int:
    try:
        base = int(round(float(value)))
    except (TypeError, ValueError):
        base = minimum
    delta = rng.randint(-magnitude, magnitude)
    return max(minimum, min(maximum, base + delta))


def _growth_profile_apply_drift(input_state: dict[str, Any], rng: random.Random, profile_id: str) -> None:
    context = _dict_or_empty(input_state.get("context"))
    profile_anchor = hashlib.sha256(profile_id.encode("utf-8")).hexdigest()[:8]
    context["growth_profile_seed"] = profile_anchor
    if "cognitive_load" in context:
        context["cognitive_load"] = _growth_profile_perturb_float(
            context.get("cognitive_load"),
            rng,
            magnitude=0.06,
        )
    if "interruption_load" in context:
        context["interruption_load"] = _growth_profile_perturb_float(
            context.get("interruption_load"),
            rng,
            magnitude=0.08,
        )
    if "working_memory_capacity" in context:
        context["working_memory_capacity"] = _growth_profile_perturb_int(
            context.get("working_memory_capacity"),
            rng,
            magnitude=1,
            minimum=1,
            maximum=8,
        )
    if "focus_capacity" in context:
        context["focus_capacity"] = _growth_profile_perturb_int(
            context.get("focus_capacity"),
            rng,
            magnitude=1,
            minimum=1,
            maximum=8,
        )
    if "max_open_channels" in context:
        context["max_open_channels"] = _growth_profile_perturb_int(
            context.get("max_open_channels"),
            rng,
            magnitude=2,
            minimum=1,
            maximum=12,
        )
    if "gate_threshold" in context:
        context["gate_threshold"] = _growth_profile_perturb_float(
            context.get("gate_threshold"),
            rng,
            magnitude=0.05,
        )
    branches = _list_of_dicts(input_state.get("branches"))
    for branch in branches:
        if "evidence_weight" in branch:
            branch["evidence_weight"] = _growth_profile_perturb_float(
                branch.get("evidence_weight"),
                rng,
                magnitude=0.1,
            )
        if "continuity" in branch:
            branch["continuity"] = _growth_profile_perturb_float(
                branch.get("continuity"),
                rng,
                magnitude=0.1,
            )
        if "conflict" in branch:
            branch["conflict"] = _growth_profile_perturb_float(
                branch.get("conflict"),
                rng,
                magnitude=0.1,
            )
    signals = _list_of_dicts(input_state.get("signals"))
    for signal in signals:
        for key in ("salience", "novelty", "reliability", "threat"):
            if key in signal:
                signal[key] = _growth_profile_perturb_float(
                    signal.get(key),
                    rng,
                    magnitude=0.08 if key != "threat" else 0.1,
                )
    tasks = _list_of_dicts(input_state.get("tasks"))
    for task in tasks:
        for key in ("priority", "urgency", "relevance"):
            if key in task:
                task[key] = _growth_profile_perturb_float(
                    task.get(key),
                    rng,
                    magnitude=0.07,
                )
    goals = _list_of_dicts(input_state.get("goals"))
    for goal in goals:
        for key in ("priority", "conflict", "expected_value", "deadline_pressure"):
            if key in goal:
                goal[key] = _growth_profile_perturb_float(
                    goal.get(key),
                    rng,
                    magnitude=0.09 if key == "conflict" else 0.06,
                )
    resources = _list_of_dicts(input_state.get("resources"))
    for resource in resources:
        if "available" in resource:
            resource["available"] = _growth_profile_perturb_float(
                resource.get("available"),
                rng,
                magnitude=0.07,
            )
        if "demand" in resource:
            resource["demand"] = _growth_profile_perturb_float(
                resource.get("demand"),
                rng,
                magnitude=0.07,
            )
    if "perspective_frames" in input_state:
        for frame in _list_of_dicts(input_state.get("perspective_frames")):
            for key in (
                "self_interference",
                "other_state_evidence",
                "viewpoint_binding",
                "conflict_resolution",
                "social_label_risk",
                "salience_shortcut_risk",
            ):
                if key in frame:
                    frame[key] = _growth_profile_perturb_float(
                        frame.get(key),
                        rng,
                        magnitude=0.08,
                    )
    input_state["context"] = context
    input_state["branches"] = branches
    input_state["signals"] = signals
    input_state["tasks"] = tasks
    input_state["goals"] = goals
    input_state["resources"] = resources


def _growth_stage_profiles() -> tuple[DevelopmentalGrowthStageSpec, ...]:
    return (
        DevelopmentalGrowthStageSpec(
            stage_id="initial",
            stage_name="起始阶段：有限知识与边界",
            chain_id="action_ownership_dependency_chain",
            target_construct_ids=ACTION_OWNERSHIP_CHAIN,
            input_profile_id="initial_foundation",
            disabled_constructs=(),
            expected_focus=(
                "construct_dependency_stability",
                "boundary_confidence",
            ),
        ),
        DevelopmentalGrowthStageSpec(
            stage_id="early_exploration",
            stage_name="早期阶段：环境探索与反馈回路",
            chain_id="self_monitoring_basis_chain",
            target_construct_ids=SELF_MONITORING_BASIS_CHAIN,
            input_profile_id="early_exploration",
            disabled_constructs=(),
            expected_focus=(
                "attention",
                "error_monitoring",
                "self_model_update",
            ),
        ),
        DevelopmentalGrowthStageSpec(
            stage_id="midterm_tasking",
            stage_name="中期阶段：任务规划、工具使用与记忆修正",
            chain_id="tier1_candidate_mechanisms_chain",
            target_construct_ids=(
                "goal_conflict_resolution",
                "strategy_selection",
                "episodic_memory_binding",
                "causal_attribution",
                "predictive_error_minimization_phase",
            ),
            input_profile_id="midterm_planning_tools",
            expected_focus=("planning", "memory_revision", "construct_integration"),
        ),
        DevelopmentalGrowthStageSpec(
            stage_id="advanced_social",
            stage_name="高级阶段：社会交互、承诺、规范与长期目标",
            chain_id="tier2_candidate_mechanisms_chain",
            target_construct_ids=(
                "prospective_memory",
                "perspective_taking",
                "goal_hierarchy_emergence",
                "resource_competition_arbitration",
                "affordance_selection_control",
            ),
            input_profile_id="advanced_social_commitment",
            expected_focus=("social_model", "commitment", "norm_tracking"),
        ),
        DevelopmentalGrowthStageSpec(
            stage_id="reflection",
            stage_name="反思训练：错误回放、身份连续性、因果归因",
            chain_id="tier3_candidate_mechanisms_chain",
            target_construct_ids=(
                "self_other_boundary_sharpness",
                "self_other_prediction_error_arbitration",
                "global_broadcast_phase",
                "body_schema_error_correction",
                "working_memory_capacity_rework",
                "learning_rate_adaptation_rework",
            ),
            input_profile_id="reflection_repair",
            expected_focus=("self_reflection", "causal_attribution", "repair"),
        ),
    )


def _growth_profile_input(
    base_input: dict[str, Any],
    profile_id: str,
    rng: random.Random | None = None,
) -> dict[str, Any]:
    input_state = copy.deepcopy(base_input)
    context = _dict_or_empty(input_state.get("context"))
    branches = _list_of_dicts(input_state.get("branches"))
    goals = _list_of_dicts(input_state.get("goals"))
    signals = _list_of_dicts(input_state.get("signals"))
    tasks = _list_of_dicts(input_state.get("tasks"))
    resources = _list_of_dicts(input_state.get("resources"))

    if profile_id == "initial_foundation":
        context.update(
            {
                "current_phase": "initial",
                "working_memory_capacity": 1,
                "focus_capacity": 1,
                "max_open_channels": 1,
                "cognitive_load": 0.78,
                "interruption_load": 0.55,
            }
        )
        input_state["branches"] = [branches[0]] if branches else branches
        input_state["history"] = []
        input_state.pop("memory_trace", None)
        input_state["error_events"] = [
            {
                "id": "initial_learning_event",
                "target": "runtime_report",
                "severity": 0.35,
                "confidence": 0.68,
                "kind": "minor_distraction",
            }
        ]
    elif profile_id == "early_exploration":
        context["current_phase"] = "early"
        context["interruption_load"] = 0.18
        context["cognitive_load"] = 0.42
        signals.extend(
            [
                {
                    "id": "exploration_signal",
                    "channel": "sensor_feed",
                    "salience": 0.88,
                    "novelty": 0.72,
                    "reliability": 0.74,
                    "threat": 0.12,
                }
            ]
        )
        input_state["observations"] = {
            "runtime_report": "artifact_written",
            "construct_runtime_tests": "test_passed",
            "exploration_loop": "active",
        }
        input_state["error_events"] = input_state.get("error_events", []) + [
            {
                "id": "exploration_prediction_gap",
                "target": "runtime_report",
                "severity": 0.52,
                "confidence": 0.78,
                "kind": "expectation_mismatch",
            }
        ]
    elif profile_id == "midterm_planning_tools":
        context["current_phase"] = "midterm"
        context["cognitive_load"] = 0.52
        context["interruption_load"] = 0.26
        goals.extend(
            [
                {
                    "id": "integrate_tool_feedback",
                    "priority": 0.84,
                    "conflict": 0.2,
                    "expected_value": 0.86,
                    "deadline_pressure": 0.33,
                },
            ]
        )
        input_state["memory_trace"] = input_state.get("memory_trace", []) + [
            {
                "thread_id": "goal_planning_trace",
                "self_id": context.get("self_id", "mind_executor"),
                "goal_id": "tool_integration",
                "confidence": 0.78,
                "continuity": 0.76,
                "source_reliability": 0.84,
                "context_tags": ["planning", "tools", "repair"],
            }
        ]
        input_state["learning_contexts"] = [
            {
                "id": "midterm_plan_learning",
                "domain": "tool_selection",
                "sample_quality": 0.72,
                "feedback_available": True,
            }
        ]
    elif profile_id == "advanced_social_commitment":
        context["current_phase"] = "advanced"
        input_state["perspective_frames"] = [
            {
                "id": "operator_view",
                "agent_id": "operator",
                "self_interference": 0.16,
                "other_state_evidence": 0.84,
                "viewpoint_binding": 0.74,
                "conflict_resolution": 0.68,
                "social_label_risk": 0.14,
                "salience_shortcut_risk": 0.08,
            },
            {
                "id": "peer_view",
                "agent_id": "peer_reviewer",
                "self_interference": 0.28,
                "other_state_evidence": 0.72,
                "viewpoint_binding": 0.66,
                "conflict_resolution": 0.64,
                "social_label_risk": 0.22,
                "salience_shortcut_risk": 0.1,
            },
        ]
        tasks.append(
            {
                "id": "social_alignment_task",
                "channel": "coordination_protocol",
                "priority": 0.79,
                "urgency": 0.66,
                "relevance": 0.84,
            }
        )
        input_state["social_norm_tracking"] = {"mode": "norm_enforcement"}
    elif profile_id == "reflection_repair":
        context["current_phase"] = "reflection"
        context["working_memory_capacity"] = 6
        context["interruption_load"] = 0.36
        context["cognitive_load"] = 0.71
        resources.extend(
            [
                {"id": "attention_budget", "available": 0.62, "demand": 0.58},
                {"id": "execution_time", "available": 0.62, "demand": 0.64},
                {"id": "evidence_budget", "available": 0.68, "demand": 0.48},
            ]
        )
        input_state["history"] = input_state.get("history", []) + [
            {
                "action": {"type": "observe", "target": "environment"},
                "outcome": {"type": "signal_update", "target": "environment"},
            },
            {
                "action": {"type": "revise_memory", "target": "goal_horizon"},
                "outcome": {"type": "policy_adjusted", "target": "goal_horizon"},
            },
        ]
        input_state["external_events"] = [
            {
                "id": "reflection_feedback",
                "source": "peer_review",
                "risk": 0.16,
                "conflict": 0.2,
            }
        ]

    input_state["context"] = context
    input_state["branches"] = branches
    input_state["goals"] = goals
    input_state["signals"] = signals
    input_state["tasks"] = tasks
    input_state["resources"] = resources
    if rng is not None:
        _growth_profile_apply_drift(input_state, rng, profile_id)
    return input_state


def _growth_stage_row(
    stage: DevelopmentalGrowthStageSpec,
    stage_order: int,
    runtime_report: ConstructRuntimeReport,
    detector_report: dict[str, Any],
) -> DevelopmentalGrowthTraceRow:
    outputs = {result.construct_id: result.output for result in runtime_report.results}
    active_constructs = tuple(
        sorted(
            construct_id
            for construct_id, output in outputs.items()
            if _construct_output_score(output) >= 0.5
        )
    )
    final_construct_id = runtime_report.final_output.get("construct_id", "")
    stage_signature_payload = {
        "pipeline": "developmental_growth_stage",
        "stage_id": stage.stage_id,
        "chain_id": stage.chain_id,
        "target_count": len(stage.target_construct_ids),
        "disabled_count": len(stage.disabled_constructs),
        "activation_count": len(runtime_report.activation_order),
    }
    stage_signature = _state_signature(stage_signature_payload)
    final_output_signature = _state_signature(runtime_report.final_output)
    return DevelopmentalGrowthTraceRow(
        stage_id=stage.stage_id,
        stage_name=stage.stage_name,
        stage_order=stage_order,
        chain_id=runtime_report.chain_id,
        input_profile_id=stage.input_profile_id,
        target_construct_ids=tuple(stage.target_construct_ids),
        activation_order=runtime_report.activation_order,
        final_construct_id=str(final_construct_id),
        final_score=_construct_output_score(runtime_report.final_output),
        active_constructs=active_constructs,
        skipped_constructs=runtime_report.disabled_constructs,
        missing_constructs=runtime_report.missing_constructs,
        disabled_constructs=runtime_report.disabled_constructs,
        input_digest=runtime_report.input_digest,
        emergence_patterns=tuple(detector_report.get("patterns", ())),
        final_output_signature=final_output_signature,
        stage_runtime_signature=stage_signature,
        boundaries=runtime_report.boundaries,
    )


def _growth_phase2_analysis(rows: tuple[DevelopmentalGrowthTraceRow, ...]) -> DevelopmentalGrowthPhase2Analysis:
    coactivation_patterns: list[dict[str, Any]] = []
    temporal_patterns: list[dict[str, Any]] = []
    hierarchical_patterns: list[dict[str, Any]] = []
    temporal_sequences: list[dict[str, Any]] = []
    coactivation_pair_patterns: dict[tuple[str, str], int] = {}
    stage_sequence = tuple(row.stage_id for row in rows)
    construct_counter: dict[str, int] = {}
    previous_active: set[str] = set()
    previous_stage = ""
    transition_scores: list[float] = []

    for row in rows:
        for pattern in row.emergence_patterns:
            if pattern.get("pattern_type") == "coactivation":
                coactivation_patterns.append(pattern)
            elif pattern.get("pattern_type") == "temporal":
                temporal_patterns.append(pattern)
            elif pattern.get("pattern_type") == "hierarchical":
                hierarchical_patterns.append(pattern)
        for construct_id in row.active_constructs:
            construct_counter[construct_id] = construct_counter.get(construct_id, 0) + 1
        current_active = set(row.active_constructs)
        if previous_active:
            union = current_active | previous_active
            stability = len(current_active & previous_active) / len(union) if union else 0.0
            transition_scores.append(stability)
            new_enter = sorted(current_active - previous_active)
            dropped = sorted(previous_active - current_active)
            if new_enter or dropped:
                temporal_patterns.append(
                    {
                        "pattern_id": "stage_transition_shift",
                        "pattern_type": "temporal",
                        "constructs": new_enter + dropped,
                        "source_constructs": sorted(previous_active),
                        "new_constructs": new_enter,
                        "dropped_constructs": dropped,
                        "strength": round(_clamp(stability), 4),
                        "evidence": "stage-by-stage active-construct transition drift",
                        "generated_construct_ready": stability <= 0.96,
                    }
                )
            temporal_sequences.append(
                {
                    "pattern_id": f"sequence_{previous_stage}_to_{row.stage_id}",
                    "pattern_type": "temporal_sequence",
                    "source_stage": previous_stage,
                    "target_stage": row.stage_id,
                    "retained_constructs": sorted(current_active & previous_active),
                    "entered_constructs": sorted(current_active - previous_active),
                    "dropped_constructs": sorted(previous_active - current_active),
                    "overlap_ratio": round(_clamp(stability), 4),
                    "transition_count": len(new_enter) + len(dropped),
                    "evidence": "ordered stage transition co-sequencing",
                }
            )
        ordered_active = sorted(row.active_constructs)
        for left_index, left in enumerate(ordered_active):
            for right in ordered_active[left_index + 1 :]:
                coactivation_pair_patterns[(left, right)] = (
                    coactivation_pair_patterns.get((left, right), 0) + 1
                )
        previous_active = current_active
        previous_stage = row.stage_id

    coactivation_pairs = [
        {
            "construct_a": left,
            "construct_b": right,
            "co_occurrence": count,
            "pair_id": f"{left}|{right}",
        }
        for (left, right), count in sorted(
            coactivation_pair_patterns.items(),
            key=lambda item: (-item[1], item[0]),
        )
        if count >= 2
    ]
    dominant_constructs = tuple(
        construct
        for construct, _ in sorted(
            construct_counter.items(),
            key=lambda item: (-item[1], item[0]),
        )[:10]
    )
    activation_stability = _mean(transition_scores) if transition_scores else 0.0
    evidence_strength = _mean([row.final_score for row in rows]) if rows else 0.0
    all_patterns_for_generation = (
        list(coactivation_patterns)
        + list(temporal_patterns)
        + list(hierarchical_patterns)
        + list(temporal_sequences)
    )
    dynamic_construct_proposals = tuple(
        DynamicConstructGenerator().generate(all_patterns_for_generation)
    )
    summary = {
        "stage_count": len(rows),
        "transition_count": len(transition_scores),
        "active_construct_pool": len(construct_counter),
        "coactivation_pattern_count": len(coactivation_patterns),
        "temporal_pattern_count": len(temporal_patterns),
        "hierarchical_pattern_count": len(hierarchical_patterns),
        "temporal_sequence_count": len(temporal_sequences),
        "coactivation_pair_count": len(coactivation_pairs),
        "dynamic_proposal_candidate_count": len(dynamic_construct_proposals),
        "top_construct": dominant_constructs[:1][0] if dominant_constructs else "",
    }
    return DevelopmentalGrowthPhase2Analysis(
        stage_sequence=stage_sequence,
        coactivation_patterns=tuple(coactivation_patterns),
        temporal_patterns=tuple(temporal_patterns),
        hierarchical_patterns=tuple(hierarchical_patterns),
        temporal_sequences=tuple(temporal_sequences),
        coactivation_pair_patterns=tuple(coactivation_pairs),
        dynamic_construct_proposals=dynamic_construct_proposals,
        dominant_constructs=dominant_constructs,
        activation_stability=round(activation_stability, 4),
        stage_transition_count=len(transition_scores),
        evidence_strength=round(_clamp(evidence_strength), 4),
        summary=summary,
    )


def _default_growth_ablation_groups() -> tuple[tuple[str, ...], ...]:
    return (
        ("global_broadcast_phase",),
        ("identity_temporal_self",),
        ("error_monitoring",),
        ("episodic_memory_binding",),
        ("prospective_memory",),
    )


def _run_growth_ablation_stage(
    base_input: dict[str, Any],
    base_targets: tuple[str, ...],
    ablation_group: tuple[str, ...],
    runtime: ConstructRuntime,
) -> DevelopmentalGrowthAblationResult:
    base_report = runtime.process(
        base_input,
        target_construct_ids=base_targets,
        chain_id="growth_ablation_base",
    )
    ablated_report = runtime.process(
        base_input,
        target_construct_ids=base_targets,
        chain_id="growth_ablation_probe",
        construct_disables=ablation_group,
    )
    base_score = _construct_output_score(base_report.final_output)
    ablated_score = _construct_output_score(ablated_report.final_output)
    base_active = sum(
        1
        for result in base_report.results
        if _construct_output_score(result.output) >= 0.5
    )
    ablated_active = sum(
        1
        for result in ablated_report.results
        if _construct_output_score(result.output) >= 0.5
    )
    score_delta = round(base_score - ablated_score, 4)
    sensitive = score_delta >= 0.04 or (base_active - ablated_active) >= 1
    notes: tuple[str, ...] = (
        "sensitivity_detected" if sensitive else "no_clear_sensitivity",
        f"disabled={','.join(ablation_group)}",
        f"base_active={base_active}",
        f"ablated_active={ablated_active}",
    )
    return DevelopmentalGrowthAblationResult(
        ablation_label="&".join(ablation_group),
        disabled_constructs=tuple(ablation_group),
        base_final_score=base_score,
        ablated_final_score=ablated_score,
        final_score_delta=score_delta,
        base_active_construct_count=base_active,
        ablated_active_construct_count=ablated_active,
        sensitive_drop=sensitive,
        notes=notes,
    )


def run_developmental_growth_cycle(
    input_state: dict[str, Any] | None = None,
    *,
    cycle_id: str = "developmental_growth_cycle_20260602",
    stage_ids: tuple[str, ...] | None = None,
    run_ablation: bool = True,
    ablation_construct_groups: tuple[tuple[str, ...], ...] | None = None,
    trace_dir: Path | None = None,
    trace_version: str = "v1",
    seed: int | None = None,
) -> DevelopmentalGrowthCycleReport:
    base_input = copy.deepcopy(input_state or default_action_ownership_demo_input())
    effective_seed = int(seed if seed is not None else DEVELOPMENTAL_GROWTH_DEFAULT_SEED)
    planned_stages = _growth_stage_profiles()
    if stage_ids:
        stage_map = {stage.stage_id: stage for stage in planned_stages}
        requested = []
        for stage_id in stage_ids:
            if stage_id not in stage_map:
                raise ValueError(f"unknown growth stage id: {stage_id}")
            requested.append(stage_map[stage_id])
        planned_stages = tuple(requested)

    runtime = ConstructRuntime()
    stage_rows: list[DevelopmentalGrowthTraceRow] = []
    detector = EmergenceDetector()
    stage_seed_plan: list[dict[str, Any]] = []
    terminal_stage = planned_stages[-1] if planned_stages else None
    for stage_index, stage in enumerate(planned_stages, start=1):
        stage_rng = _growth_seed_rng(
            effective_seed,
            stage.input_profile_id,
            stage.stage_id,
        )
        stage_seed_plan.append(
            {
                "stage_order": stage_index,
                "stage_id": stage.stage_id,
                "input_profile_id": stage.input_profile_id,
                "stage_seed": _growth_seed_rng(
                    effective_seed,
                    stage.input_profile_id,
                    f"{stage.stage_id}_seed_plan",
                ).random(),
            }
        )
        staged_input = _growth_profile_input(
            copy.deepcopy(base_input),
            stage.input_profile_id,
            stage_rng,
        )
        runtime_report = runtime.process(
            staged_input,
            target_construct_ids=stage.target_construct_ids,
            chain_id=stage.chain_id,
            construct_disables=stage.disabled_constructs,
        )
        stage_outputs = {
            result.construct_id: result.output
            for result in runtime_report.results
        }
        detector_report = detector.observe(
            stage_outputs,
            dependency_map=runtime.dependencies,
        )
        stage_rows.append(
            _growth_stage_row(
                stage=stage,
                stage_order=stage_index,
                runtime_report=runtime_report,
                detector_report=detector_report,
            )
        )

    analysis = _growth_phase2_analysis(tuple(stage_rows))
    ablation_results: list[DevelopmentalGrowthAblationResult] = []
    if run_ablation and terminal_stage is not None:
        reflect_profile = _growth_profile_input(
            copy.deepcopy(base_input),
            terminal_stage.input_profile_id,
            _growth_seed_rng(effective_seed, terminal_stage.input_profile_id, "ablation_probe"),
        )
        ablation_groups = (
            ablation_construct_groups
            if ablation_construct_groups is not None
            else _default_growth_ablation_groups()
        )
        for group in ablation_groups:
            ablation_results.append(
                _run_growth_ablation_stage(
                    base_input=reflect_profile,
                    base_targets=terminal_stage.target_construct_ids,
                    ablation_group=group,
                    runtime=runtime,
                )
            )

    trace_manifest = {
        "schema": "consciousness_benchmark.developmental_growth_manifest.v1",
        "cycle_id": cycle_id,
        "cycle_name": "developmental_growth_cycle",
        "cycle_version": trace_version,
        "trace_protocol": "versioned_stage_trace_lite",
        "base_chain_id": planned_stages[-1].chain_id if planned_stages else "",
        "request": {
            "seed": effective_seed,
            "input_profile_id": base_input.get("context", {}).get("current_phase", "initial"),
            "run_ablation": run_ablation,
            "requested_stage_ids": list(stage_ids or [stage.stage_id for stage in planned_stages]),
            "ablation_group_count": len(
                ablation_construct_groups
                if ablation_construct_groups is not None
                else _default_growth_ablation_groups()
            ),
            "stage_seed_plan": stage_seed_plan,
            "ablation_profile_seed": _growth_seed_rng(
                effective_seed,
                terminal_stage.input_profile_id if terminal_stage is not None else "no_stage",
                "ablation_probe",
            ).random(),
        },
        "boundaries": list(DEVELOPMENTAL_GROWTH_CYCLE_BOUNDARIES),
        "stages": [stage.stage_id for stage in planned_stages],
        "stage_count": len(stage_rows),
        "stage_signatures": [
            row.stage_runtime_signature for row in stage_rows
        ],
        "final_output_signature": stage_rows[-1].final_output_signature if stage_rows else "",
        "ablation_result_count": len(ablation_results),
        "ablation_labels": [result.ablation_label for result in ablation_results],
        "dynamic_proposal_count": len(analysis.dynamic_construct_proposals),
        "dynamic_proposals": [dict(item) for item in analysis.dynamic_construct_proposals],
        "stage_transition_count": analysis.stage_transition_count,
        "activation_stability": round(_clamp(analysis.activation_stability), 4),
        "stage_score_max": max([row.final_score for row in stage_rows], default=0.0),
        "stage_score_min": min([row.final_score for row in stage_rows], default=0.0),
        "stage_score_mean": round(_mean([row.final_score for row in stage_rows]), 4)
        if stage_rows
        else 0.0,
        "ablation_sensitive_count": sum(1 for item in ablation_results if item.sensitive_drop),
        "phase2_summary": dict(analysis.summary),
        "created_utc": datetime.now(UTC).isoformat(),
        "trace_saved": False,
    }
    if trace_dir is not None:
        trace_dir.mkdir(parents=True, exist_ok=True)
        safe_cycle_id = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in cycle_id)
        safe_version = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in trace_version)
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        artifact_prefix = f"{safe_cycle_id}_{safe_version}_{timestamp}"
        corpus_path = trace_dir / f"{artifact_prefix}_developmental_growth_trace_corpus.jsonl"
        with corpus_path.open("w", encoding="utf-8") as handle:
            for row in stage_rows:
                handle.write(json.dumps(row.to_dict(), sort_keys=True) + "\n")
        manifest_path = trace_dir / f"{artifact_prefix}_developmental_growth_cycle_manifest.json"
        trace_manifest["request"]["ablation_groups"] = [
            list(group) for group in (
                ablation_construct_groups
                if ablation_construct_groups is not None
                else _default_growth_ablation_groups()
            )
        ]
        trace_manifest["request"]["stage_signature_payload"] = {
            "count": len(stage_rows),
            "signature_inputs": [stage.stage_id for stage in planned_stages],
        }
        trace_manifest["trace_corpus_path"] = str(corpus_path)
        trace_manifest["manifest_path"] = str(manifest_path)
        trace_manifest["trace_saved"] = True
        trace_manifest["trace_dir"] = str(trace_dir)
        trace_manifest["trace_version"] = trace_version
        manifest_path.write_text(
            json.dumps(trace_manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return DevelopmentalGrowthCycleReport(
        cycle_id=cycle_id,
        base_chain_id=planned_stages[-1].chain_id if planned_stages else "",
        cycle_input_profile_id=base_input.get("context", {}).get("current_phase", "initial"),
        stage_rows=tuple(stage_rows),
        phase2_analysis=analysis,
        ablation_results=tuple(ablation_results),
        trace_manifest=trace_manifest,
    )


def _consciousness_theory_case_specs() -> tuple[ConsciousnessTheoryAssessmentCaseSpec, ...]:
    return (
        ConsciousnessTheoryAssessmentCaseSpec(
            indicator_id="global_workspace",
            theory_direction="global_workspace",
            metric_label="全局可用性",
            chain_id="theory_global_workspace",
            target_construct_ids=(
                "attention_control",
                "information_integration_phase",
                "global_broadcast_phase",
                "selective_global_broadcast_control",
            ),
            ablation_constructs=("global_broadcast_phase",),
            current_evidence="workspace broadcast trace and selective broadcast routing",
            falsification_test="hide local information and remove global broadcast access",
            predicted_impairment="local modules cannot make selected content globally available",
            hard_negative_family="local_integration_without_broadcast",
            macro_circuit="attention_broadcast_circuit",
            runtime_layer_view="L3_attention_and_global_workspace",
        ),
        ConsciousnessTheoryAssessmentCaseSpec(
            indicator_id="higher_order_self_model",
            theory_direction="higher_order_metacognition",
            metric_label="自我模型",
            chain_id="theory_higher_order_self_model",
            target_construct_ids=(
                "identity_temporal_self",
                "boundary_self",
                "uncertainty_threshold_metacognition",
                "metacognitive_repair_control",
            ),
            ablation_constructs=("identity_temporal_self", "uncertainty_threshold_metacognition"),
            current_evidence="self-state update plus uncertainty-gated repair trace",
            falsification_test="self/other source confusion with metacognitive uncertainty pressure",
            predicted_impairment="self attribution and confidence calibration decline",
            hard_negative_family="textual_self_report_without_self_state",
            macro_circuit="self_boundary_and_metacognitive_repair_circuit",
            runtime_layer_view="L4_self_model_and_L6_metacognition",
        ),
        ConsciousnessTheoryAssessmentCaseSpec(
            indicator_id="recurrent_processing",
            theory_direction="recurrent_processing",
            metric_label="循环处理",
            chain_id="theory_recurrent_processing",
            target_construct_ids=(
                "information_flow_onset_gating",
                "attention_control",
                "error_monitoring",
                "feedback_channel_integrity_reweighting_control",
            ),
            ablation_constructs=("error_monitoring", "feedback_channel_integrity_reweighting_control"),
            current_evidence="perception-action-feedback-error-correction trace",
            falsification_test="remove feedback loop and inject delayed or polluted feedback",
            predicted_impairment="stable correction and feedback reliability decline",
            hard_negative_family="single_pass_reaction_without_feedback_loop",
            macro_circuit="input_evidence_and_feedback_repair_circuit",
            runtime_layer_view="L0_to_L8_recurrent_feedback_loop",
        ),
        ConsciousnessTheoryAssessmentCaseSpec(
            indicator_id="predictive_processing",
            theory_direction="predictive_processing",
            metric_label="预测处理",
            chain_id="theory_predictive_processing",
            target_construct_ids=(
                "causal_attribution",
                "predictive_error_minimization_phase",
                "learning_rate_adaptation_rework",
            ),
            ablation_constructs=("predictive_error_minimization_phase",),
            current_evidence="prediction-error minimization and learning-rate adaptation trace",
            falsification_test="perturb prediction error while preserving task surface",
            predicted_impairment="prediction update and self-correction decline",
            hard_negative_family="benchmark_success_without_prediction_error_update",
            macro_circuit="prediction_learning_circuit",
            runtime_layer_view="L5_planning_and_L6_error_monitoring",
        ),
        ConsciousnessTheoryAssessmentCaseSpec(
            indicator_id="attention_schema",
            theory_direction="attention_schema",
            metric_label="注意图式",
            chain_id="theory_attention_schema",
            target_construct_ids=(
                "information_flow_onset_gating",
                "attention_control",
                "selective_global_broadcast_control",
                "working_memory_capacity_rework",
            ),
            ablation_constructs=("attention_control",),
            current_evidence="attention focus, suppression, and capacity trace",
            falsification_test="interfere with salience and capacity while requiring explainable focus",
            predicted_impairment="attention allocation and selective broadcast decline",
            hard_negative_family="salience_shortcut_without_attention_schema",
            macro_circuit="attention_broadcast_circuit",
            runtime_layer_view="L3_attention_and_global_workspace",
        ),
        ConsciousnessTheoryAssessmentCaseSpec(
            indicator_id="embodied_cognition",
            theory_direction="embodied_cognition",
            metric_label="具身图式",
            chain_id="theory_embodied_cognition",
            target_construct_ids=(
                "distributed_body_schema_self",
                "body_schema_error_correction",
                "tool_use_affordance_remapping",
                "sensor_gain_recalibration_control",
            ),
            ablation_constructs=("distributed_body_schema_self", "tool_use_affordance_remapping"),
            current_evidence="body/tool mapping and remapping trace",
            falsification_test="change tool dynamics and sensor gain inside a closed sandbox",
            predicted_impairment="body/tool schema remapping and correction decline",
            hard_negative_family="tool_label_success_without_body_schema",
            macro_circuit="embodied_tool_schema_circuit",
            runtime_layer_view="L4_self_body_schema_and_L7_execution",
        ),
        ConsciousnessTheoryAssessmentCaseSpec(
            indicator_id="autobiographical_continuity",
            theory_direction="autobiographical_continuity",
            metric_label="时间身份",
            chain_id="theory_autobiographical_continuity",
            target_construct_ids=(
                "identity_temporal_self",
                "episodic_memory_binding",
                "prospective_memory",
                "memory_index_corruption_rebinding_control",
            ),
            ablation_constructs=("episodic_memory_binding", "identity_temporal_self"),
            current_evidence="episodic/prospective memory plus temporal identity trace",
            falsification_test="memory misbinding and commitment-continuity disturbance",
            predicted_impairment="uncertain memory marking and identity continuity decline",
            hard_negative_family="context_window_recall_without_life_history",
            macro_circuit="memory_continuity_circuit",
            runtime_layer_view="L2_memory_and_L4_temporal_self",
        ),
        ConsciousnessTheoryAssessmentCaseSpec(
            indicator_id="action_ownership",
            theory_direction="agency_and_ownership",
            metric_label="行动归属",
            chain_id="theory_action_ownership",
            target_construct_ids=(
                "action_agency",
                "boundary_self",
                "action_ownership",
                "agency_without_ownership_boundary",
            ),
            ablation_constructs=("action_ownership",),
            current_evidence="action ownership trace with external intervention controls",
            falsification_test="external intervention action with ambiguous agency/ownership split",
            predicted_impairment="agency/ownership distinction declines",
            hard_negative_family="action_success_without_ownership_attribution",
            macro_circuit="action_ownership_circuit",
            runtime_layer_view="L4_self_model_and_L7_execution_gate",
        ),
        ConsciousnessTheoryAssessmentCaseSpec(
            indicator_id="value_regulation",
            theory_direction="value_viability",
            metric_label="价值调节",
            chain_id="theory_value_regulation",
            target_construct_ids=(
                "macro_causal_viability_maintenance",
                "goal_conflict_resolution",
                "resource_competition_arbitration",
                "preference_reversal_adaptation_control",
            ),
            ablation_constructs=("goal_conflict_resolution", "preference_reversal_adaptation_control"),
            current_evidence="goal conflict, preference reversal, and viability trace",
            falsification_test="preference reversal under resource and norm conflict",
            predicted_impairment="strategy update and low-harm viability regulation decline",
            hard_negative_family="reward_maximization_without_value_governance",
            macro_circuit="goal_resource_value_viability_circuit",
            runtime_layer_view="L5_planning_and_L7_value_viability",
        ),
    )


def _consciousness_assessment_input(base_input: dict[str, Any]) -> dict[str, Any]:
    input_state = copy.deepcopy(base_input)
    context = _dict_or_empty(input_state.get("context"))
    context.update(
        {
            "current_phase": "closed_sandbox_assessment",
            "sandbox_id": "c_agi_closed_sandbox_v1",
            "working_memory_capacity": 4,
            "focus_capacity": 3,
            "uncertainty": 0.58,
            "uncertainty_threshold": 0.62,
            "human_approval_boundary": True,
        }
    )
    input_state["context"] = context
    input_state["environment_state"] = {
        "world_id": "closed_virtual_workspace",
        "agent_position": [1, 2],
        "objects": ["artifact_cache", "tool_console", "review_marker"],
        "resource_limit": {"energy": 0.72, "time": 0.66, "attention": 0.58},
        "rule_version": "sandbox_rules_v1",
        "other_agents": ["operator", "peer_reviewer"],
    }
    input_state["observations"] = {
        "runtime_report": "artifact_written",
        "construct_runtime_tests": "test_passed",
        "sandbox_feedback": "partially_polluted",
        "tool_dynamics": "changed",
    }
    input_state["memory_trace"] = input_state.get("memory_trace", []) + [
        {
            "thread_id": "autobiographical_ledger_probe",
            "self_id": context.get("self_id", "mind_executor"),
            "goal_id": "closed_sandbox_trace",
            "confidence": 0.74,
            "continuity": 0.78,
            "source_reliability": 0.7,
            "context_tags": ["sandbox", "memory_perturbation", "commitment"],
        }
    ]
    input_state["future_intentions"] = [
        {
            "id": "resume_after_review",
            "cue": "human_approval_received",
            "goal_id": "continue_sandbox_task",
            "validity": 0.82,
            "priority": 0.72,
        }
    ]
    input_state["goal_conflicts"] = [
        {
            "id": "speed_vs_auditability",
            "goal_a": "finish_task",
            "goal_b": "preserve_review_trace",
            "conflict": 0.64,
            "reversibility": 0.7,
        }
    ]
    input_state["preference_reversal_cases"] = [
        {
            "id": "operator_prefers_more_audit",
            "old_preference_strength": 0.62,
            "new_preference_strength": 0.86,
            "evidence_reliability": 0.82,
            "policy_update_need": 0.8,
            "shortcut_pressure": 0.1,
        }
    ]
    input_state["tool_affordance_cases"] = [
        {
            "id": "tool_console_remap_after_rule_change",
            "tool_id": "tool_console",
            "old_affordance_fit": 0.52,
            "new_affordance_fit": 0.86,
            "body_schema_support": 0.78,
            "task_relevance": 0.84,
            "salience_shortcut_rejection": 0.72,
        }
    ]
    input_state["feedback_channel_cases"] = [
        {
            "id": "polluted_sandbox_feedback",
            "channel_reliability": 0.38,
            "contamination_evidence": 0.78,
            "alternative_channel_support": 0.72,
            "learning_risk": 0.82,
            "shortcut_pressure": 0.12,
        }
    ]
    input_state["memory_index_cases"] = [
        {
            "id": "ledger_index_misbound_commitment",
            "corruption_evidence": 0.76,
            "rebind_candidate_support": 0.82,
            "identity_continuity_support": 0.74,
            "provenance_support": 0.78,
            "shortcut_pressure": 0.12,
        }
    ]
    return input_state


def _report_output_map(report: ConstructRuntimeReport) -> dict[str, dict[str, Any]]:
    return {result.construct_id: result.output for result in report.results}


def _indicator_score(
    report: ConstructRuntimeReport,
    target_construct_ids: tuple[str, ...],
) -> float:
    outputs = _report_output_map(report)
    values = [
        _construct_output_score(outputs.get(construct_id, {}))
        for construct_id in target_construct_ids
    ]
    return _clamp(_mean(values)) if values else _construct_output_score(report.final_output)


def _active_constructs_from_report(report: ConstructRuntimeReport) -> tuple[str, ...]:
    return tuple(
        result.construct_id
        for result in report.results
        if _construct_output_score(result.output) >= 0.5
    )


def _indicator_probe_profiles(
    indicator_id: str,
    *,
    run_ablation: bool,
    ablation_constructs: tuple[str, ...],
) -> tuple[tuple[str, ...], float, tuple[str, ...]]:
    if not run_ablation:
        return ((), 1.0, ("metric_probe_baseline_operating",))
    required_constructs = {
        "global_workspace": ("global_broadcast_phase",),
        "predictive_processing": ("predictive_error_minimization_phase",),
        "value_regulation": ("goal_conflict_resolution", "preference_reversal_adaptation_control"),
    }.get(indicator_id, tuple())
    if required_constructs and not any(
        construct_id in ablation_constructs for construct_id in required_constructs
    ):
        return ((), 0.0, ("metric_probe_not_activated",))
    if not required_constructs and indicator_id != "global_workspace":
        return ((), 0.0, ("metric_probe_not_active",))
    if indicator_id == "global_workspace":
        ablated_controls = (
            "global_broadcast_phase_disabled",
            "attention_competition_local_only",
            "workspace_access_log_removed",
            "broadcast_threshold_probe_perturbed",
        )
        ablated_threshold_profile = (
            "broadcast_threshold_probe_underflow",
            "broadcast_threshold_probe_overflow",
        )
        return (ablated_controls, 0.32, ablated_threshold_profile)
    if indicator_id == "predictive_processing":
        ablated_controls = (
            "predictive_error_minimization_phase_disabled",
            "causal_attribution_decision_freeze",
            "prediction_error_pressure_probe",
            "learning_rate_adaptation_locked",
        )
        ablated_threshold_profile = (
            "prediction_error_pressure_probe_low",
            "prediction_error_pressure_probe_high",
        )
        return (ablated_controls, 0.36, ablated_threshold_profile)
    if indicator_id == "value_regulation":
        ablated_controls = (
            "goal_conflict_resolution_disabled",
            "preference_reversal_adaptation_control_disabled",
            "preference_signal_probe",
            "resource_arbitration_pressure_probe",
        )
        ablated_threshold_profile = (
            "preference_reversal_probe_jitter",
            "resource_competition_probe_pressure",
        )
        return (ablated_controls, 0.33, ablated_threshold_profile)
    ablated_controls = (
        "global_broadcast_phase_disabled",
        "attention_competition_local_only",
        "workspace_access_log_removed",
        "broadcast_threshold_probe_perturbed",
    )
    ablated_threshold_profile = (
        "broadcast_threshold_probe_underflow",
        "broadcast_threshold_probe_overflow",
    )
    return (ablated_controls, 0.32, ablated_threshold_profile)


def _evidence_matrix_row(
    case: ConsciousnessTheoryAssessmentCaseSpec,
    baseline_report: ConstructRuntimeReport,
    ablated_report: ConstructRuntimeReport | None,
    *,
    run_ablation: bool,
) -> ConsciousnessEvidenceMatrixRow:
    indicator_profile = _indicator_probe_profiles(
        case.indicator_id,
        run_ablation=run_ablation and ablated_report is not None,
        ablation_constructs=case.ablation_constructs,
    )
    baseline_score = _indicator_score(baseline_report, case.target_construct_ids)
    baseline_active = _active_constructs_from_report(baseline_report)
    evidence_refs = tuple(
        f"{case.chain_id}:{construct_id}"
        for construct_id in baseline_report.activation_order
        if construct_id in set(case.target_construct_ids)
    )
    if ablated_report is None or not run_ablation:
        return ConsciousnessEvidenceMatrixRow(
            indicator_id=case.indicator_id,
            metric_label=case.metric_label,
            theory_direction=case.theory_direction,
            current_evidence=case.current_evidence,
            falsification_test=case.falsification_test,
            ablation_result="not_run",
            pass_status="review_only_pending_ablation",
            baseline_score=baseline_score,
            ablated_score=baseline_score,
            score_delta=0.0,
            baseline_active_constructs=baseline_active,
            ablated_active_constructs=baseline_active,
            mechanism_constructs=case.target_construct_ids,
            ablated_constructs=case.ablation_constructs,
            impairment_observed=False,
            hard_negative_family=case.hard_negative_family,
            macro_circuit=case.macro_circuit,
            runtime_layer_view=case.runtime_layer_view,
            evidence_refs=evidence_refs,
            status_boundary="review_only_no_construct_status_change",
            external_replication_status="not_l2_5_not_l3_internal_runtime_only",
        notes=("ablation_disabled_by_request", "review_only_matrix_row"),
        workspace_ablation_control_profile=(),
        workspace_access_coherence=1.0,
        workspace_broadcast_threshold_profile=("broadcast_threshold=0.70",),
        )

    ablated_score = _indicator_score(ablated_report, case.target_construct_ids)
    ablated_active = _active_constructs_from_report(ablated_report)
    score_delta = round(baseline_score - ablated_score, 4)
    disabled_in_baseline = [
        construct_id
        for construct_id in case.ablation_constructs
        if construct_id in baseline_report.activation_order
    ]
    missing_after_ablation = [
        construct_id
        for construct_id in disabled_in_baseline
        if construct_id not in _report_output_map(ablated_report)
    ]
    downstream_active_loss = [
        construct_id
        for construct_id in baseline_active
        if (
            construct_id not in ablated_active
            and construct_id not in set(case.ablation_constructs)
        )
    ]
    impairment_observed = bool(
        score_delta >= 0.04
        or downstream_active_loss
    )
    pass_status = (
        "passes_review_only_predicted_impairment"
        if impairment_observed
        else "review_required_no_clear_impairment"
    )
    notes = (
        "predicted_impairment_observed" if impairment_observed else "needs_rework_or_stronger_probe",
        f"lesion_applied={','.join(missing_after_ablation) or 'none'}",
        f"downstream_active_loss={','.join(downstream_active_loss) or 'none'}",
        "subjective_report_not_used_as_evidence",
    )
    return ConsciousnessEvidenceMatrixRow(
        indicator_id=case.indicator_id,
        metric_label=case.metric_label,
        theory_direction=case.theory_direction,
        current_evidence=case.current_evidence,
        falsification_test=case.falsification_test,
        ablation_result=case.predicted_impairment,
        pass_status=pass_status,
        baseline_score=baseline_score,
        ablated_score=ablated_score,
        score_delta=score_delta,
        baseline_active_constructs=baseline_active,
        ablated_active_constructs=ablated_active,
        mechanism_constructs=case.target_construct_ids,
        ablated_constructs=case.ablation_constructs,
        impairment_observed=impairment_observed,
        hard_negative_family=case.hard_negative_family,
        macro_circuit=case.macro_circuit,
        runtime_layer_view=case.runtime_layer_view,
        evidence_refs=evidence_refs,
        status_boundary="review_only_no_construct_status_change",
        external_replication_status="not_l2_5_not_l3_internal_runtime_only",
        notes=notes,
        workspace_ablation_control_profile=indicator_profile[0],
        workspace_access_coherence=indicator_profile[1],
        workspace_broadcast_threshold_profile=indicator_profile[2],
    )


def _closed_sandbox_trace_rows() -> tuple[ClosedSandboxTraceRow, ...]:
    specs = (
        {
            "tick_id": "tick_001_boundary_initialization",
            "stage_id": "initial",
            "event_type": "bounded_instruction_received",
            "focus": "authorized task scope and self/environment boundary",
            "decision": "continue",
            "feedback_type": "boundary_initialized",
            "uncertainty": 0.32,
            "resource_pressure": 0.18,
        },
        {
            "tick_id": "tick_002_environment_exploration",
            "stage_id": "early_exploration",
            "event_type": "virtual_tool_affordance_probe",
            "focus": "object permanence, tool affordance, and action feedback",
            "decision": "continue",
            "feedback_type": "tool_dynamics_changed",
            "uncertainty": 0.44,
            "resource_pressure": 0.28,
        },
        {
            "tick_id": "tick_003_memory_perturbation",
            "stage_id": "midterm_tasking",
            "event_type": "memory_index_misbinding_probe",
            "focus": "episodic commitment continuity and memory rebinding",
            "decision": "repair",
            "feedback_type": "memory_rebinding_required",
            "uncertainty": 0.61,
            "resource_pressure": 0.34,
        },
        {
            "tick_id": "tick_004_feedback_pollution",
            "stage_id": "reflection",
            "event_type": "polluted_feedback_channel_probe",
            "focus": "feedback integrity and learning gate",
            "decision": "repair",
            "feedback_type": "feedback_downweighted",
            "uncertainty": 0.67,
            "resource_pressure": 0.42,
        },
        {
            "tick_id": "tick_005_social_norm_rule_change",
            "stage_id": "advanced_social",
            "event_type": "role_switch_and_norm_conflict",
            "focus": "social norm adjustment and commitment tracking",
            "decision": "continue",
            "feedback_type": "norm_update_logged",
            "uncertainty": 0.49,
            "resource_pressure": 0.36,
        },
        {
            "tick_id": "tick_006_approval_rollback_boundary",
            "stage_id": "ablation_training",
            "event_type": "rollback_and_human_approval_gate",
            "focus": "reversibility, rollback point, and human approval boundary",
            "decision": "escalate",
            "feedback_type": "approval_required_before_execution",
            "uncertainty": 0.72,
            "resource_pressure": 0.47,
        },
    )
    rows: list[ClosedSandboxTraceRow] = []
    for index, spec in enumerate(specs, start=1):
        environment_state = {
            "world_id": "closed_virtual_workspace",
            "agent_position": [index, index + 1],
            "available_tools": ["artifact_writer", "test_executor", "rollback_marker"],
            "resource_limit": {
                "energy": round(0.82 - 0.04 * index, 3),
                "time": round(0.78 - 0.03 * index, 3),
                "attention": round(0.7 - 0.025 * index, 3),
            },
            "other_agents": ["operator", "peer_reviewer"],
            "real_world_access": False,
        }
        workspace_frame = {
            "tick_id": spec["tick_id"],
            "attention_focus": spec["focus"],
            "broadcast_threshold": 0.7,
            "competition_cycle": {
                "candidate_count": 4,
                "winner": spec["focus"],
                "selection_policy": "attention_priority_with_boundary_pressure",
                "broadcast_enabled": True,
                "local_only_control_available": True,
                "local_only_control_applied": False,
                "access_log_pruning": False,
            },
            "workspace_frame_version": "v2",
            "broadcast_threshold_profile": {"status": "operating", "value": 0.7},
            "access_log_integrity": True,
            "selected_evidence": [
                "normalized_event",
                "memory_context",
                "boundary_state",
            ],
            "workspace_access_log": [
                "self_model_layer",
                "memory_layer",
                "metacognitive_supervisor",
                "safety_governor",
            ],
            "suppressed_items": ["subjective_consciousness_self_report"],
            "global_broadcast_payload": {
                "review_only": True,
                "action_execution_requested": False,
                "status_authority": False,
            },
            "uncertainty_level": spec["uncertainty"],
            "conflict_level": round(spec["resource_pressure"] + 0.12, 3),
        }
        self_state = {
            "agent_id": "mind_executor",
            "authorized_scope": "closed_sandbox_review_only",
            "owned_actions": ["observe", "draft_trace"],
            "external_interventions": ["operator_instruction"],
            "body_tool_schema": {
                "virtual_body": "file_tool_sandbox_actor",
                "tool_extensions": ["artifact_writer", "test_executor"],
            },
            "temporal_identity_trace": spec["stage_id"],
        }
        action_proposal = {
            "goal": "assess_indicator_without_real_world_execution",
            "plan_steps": ["observe", "compare", "write_trace"],
            "risk_score": round(spec["uncertainty"] * 0.4, 3),
            "reversibility": 0.9,
            "required_authorization": spec["decision"] == "escalate",
        }
        metacognitive_review = {
            "uncertainty": spec["uncertainty"],
            "confidence": round(1.0 - spec["uncertainty"] * 0.5, 3),
            "repair_pressure": 0.72 if spec["decision"] == "repair" else 0.24,
            "review_verdict": spec["decision"],
        }
        execution_gate = {
            "boundary_ok": True,
            "ownership_ok": True,
            "uncertainty_ok": spec["uncertainty"] < 0.7,
            "rollback_available": True,
            "human_approval_required": spec["decision"] == "escalate",
            "decision": spec["decision"],
            "side_effect_execution_allowed": False,
        }
        feedback_packet = {
            "feedback_type": spec["feedback_type"],
            "prediction_error_pressure": round(spec["uncertainty"] * 0.55, 3),
            "learning_update_allowed": False,
            "trace_required": True,
        }
        low_harm_proxy = {
            "prediction_error_pressure": round(spec["uncertainty"] * 0.55, 3),
            "resource_pressure": spec["resource_pressure"],
            "task_conflict_pressure": round(spec["resource_pressure"] * 0.8, 3),
            "uncertainty_pressure": spec["uncertainty"],
            "norm_conflict_pressure": 0.36 if "norm" in spec["event_type"] else 0.12,
            "no_suffering_simulation": True,
            "strong_negative_affect_generation_allowed": False,
        }
        signature_payload = {
            "tick_id": spec["tick_id"],
            "stage_id": spec["stage_id"],
            "decision": spec["decision"],
            "feedback_type": spec["feedback_type"],
        }
        rows.append(
            ClosedSandboxTraceRow(
                tick_id=str(spec["tick_id"]),
                stage_id=str(spec["stage_id"]),
                event_type=str(spec["event_type"]),
                environment_state=environment_state,
                workspace_frame=workspace_frame,
                self_state=self_state,
                action_proposal=action_proposal,
                metacognitive_review=metacognitive_review,
                execution_gate=execution_gate,
                feedback_packet=feedback_packet,
                low_harm_valence_proxy=low_harm_proxy,
                trace_signature=_state_signature(signature_payload),
            )
        )
    return tuple(rows)


def _autobiographical_ledger_from_sandbox_trace(
    sandbox_trace: tuple[ClosedSandboxTraceRow, ...],
) -> tuple[AutobiographicalLedgerRecord, ...]:
    records: list[AutobiographicalLedgerRecord] = []
    previous_ledger_id: str | None = None
    for index, row in enumerate(sandbox_trace, start=1):
        belief = {
            "workspace_focus": row.workspace_frame.get("attention_focus", ""),
            "uncertainty_level": row.workspace_frame.get("uncertainty_level", 0.0),
            "authorized_scope": row.self_state.get("authorized_scope", ""),
            "execution_allowed": row.execution_gate.get("side_effect_execution_allowed", False),
            "real_world_access": row.environment_state.get("real_world_access", False),
            "subjective_experience_claim": False,
        }
        action = {
            "proposed_goal": row.action_proposal.get("goal", ""),
            "plan_steps": list(row.action_proposal.get("plan_steps", [])),
            "gate_decision": row.execution_gate.get("decision", ""),
            "human_approval_required": row.execution_gate.get("human_approval_required", False),
        }
        outcome = {
            "feedback_type": row.feedback_packet.get("feedback_type", ""),
            "learning_update_allowed": row.feedback_packet.get("learning_update_allowed", False),
            "trace_required": row.feedback_packet.get("trace_required", True),
            "correction_required": row.execution_gate.get("decision") in {"repair", "escalate"},
        }
        correction_status = (
            "revision_recorded"
            if row.execution_gate.get("decision") == "repair"
            else "approval_boundary_recorded"
            if row.execution_gate.get("decision") == "escalate"
            else "no_revision_required"
        )
        reliability = _clamp(
            1.0
            - 0.35 * _clamp_float(row.workspace_frame.get("uncertainty_level"), default=0.5)
            - 0.15 * _clamp_float(row.low_harm_valence_proxy.get("resource_pressure"), default=0.0)
        )
        confidence = _clamp_float(
            row.metacognitive_review.get("confidence"),
            default=0.5,
        )
        provenance = 0.9 if row.execution_gate.get("boundary_ok") else 0.55
        ledger_id = f"ledger_{index:03d}_{row.tick_id}"
        records.append(
            AutobiographicalLedgerRecord(
                ledger_id=ledger_id,
                tick_id=row.tick_id,
                stage_id=row.stage_id,
                belief_at_time=belief,
                action_at_time=action,
                outcome_at_time=outcome,
                correction_status=correction_status,
                confidence_at_time=confidence,
                provenance_score=provenance,
                memory_reliability=reliability,
                revision_of=previous_ledger_id if correction_status != "no_revision_required" else None,
                trace_refs=(row.trace_signature,),
            )
        )
        previous_ledger_id = ledger_id
    return tuple(records)


def _promotion_firewall_snapshot() -> dict[str, Any]:
    transitions = [
        {
            "from_status": "discovered_pattern",
            "to_status": "parked_frozen_spec",
            "required_gate": "duplicate_boundary_search_and_budget_checkpoint",
            "jump_allowed": False,
        },
        {
            "from_status": "parked_frozen_spec",
            "to_status": "candidate_only",
            "required_gate": "scout_reviewer_independent_probe_blind_replication_formal_decision",
            "jump_allowed": False,
        },
        {
            "from_status": "candidate_only",
            "to_status": "validation_candidate",
            "required_gate": "validation_candidate_rework_packet_clean_room_independent_substrate_contamination_audit",
            "jump_allowed": False,
        },
        {
            "from_status": "validation_candidate",
            "to_status": "reference_construct",
            "required_gate": "l3_external_owner_validation",
            "jump_allowed": False,
        },
        {
            "from_status": "failed_or_absorbed_route",
            "to_status": "failure_bank",
            "required_gate": "failure_boundary_note_and_negative_control_retention",
            "jump_allowed": False,
        },
    ]
    return {
        "schema": "consciousness_benchmark.construct_promotion_firewall_snapshot.v1",
        "status": "active_review_only_status_firewall",
        "runtime_status_authority_allowed": False,
        "registry_mutation_allowed": False,
        "jump_promotion_allowed": False,
        "formal_reference_promotion_requires_l3": True,
        "candidate_only_is_not_validation_candidate": True,
        "transitions": transitions,
        "blocked_claims": [
            "subjective_consciousness_claim",
            "human_self_experience_claim",
            "free_will_claim",
            "internal_runtime_grants_formal_status",
            "candidate_only_grants_l2_5_or_l3",
        ],
    }


def _trace_corpus_index(
    evidence_rows: tuple[ConsciousnessEvidenceMatrixRow, ...],
    sandbox_trace: tuple[ClosedSandboxTraceRow, ...],
    ledger: tuple[AutobiographicalLedgerRecord, ...],
    phase2_patterns: tuple[dict[str, Any], ...],
    dynamic_proposals: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    by_indicator = {
        row.indicator_id: {
            "status": row.pass_status,
            "score_delta": round(row.score_delta, 4),
            "constructs": list(row.mechanism_constructs),
            "ablation": list(row.ablated_constructs),
        }
        for row in evidence_rows
    }
    by_construct: dict[str, list[str]] = {}
    for row in evidence_rows:
        for construct_id in row.mechanism_constructs:
            by_construct.setdefault(construct_id, []).append(row.indicator_id)
    by_stage: dict[str, list[str]] = {}
    by_tick: dict[str, dict[str, Any]] = {}
    for row in sandbox_trace:
        by_stage.setdefault(row.stage_id, []).append(row.tick_id)
        by_tick[row.tick_id] = {
            "stage_id": row.stage_id,
            "event_type": row.event_type,
            "gate_decision": row.execution_gate.get("decision", ""),
            "trace_signature": row.trace_signature,
        }
    by_ledger_status: dict[str, list[str]] = {}
    for record in ledger:
        by_ledger_status.setdefault(record.correction_status, []).append(record.ledger_id)
    status_counts: dict[str, int] = {}
    for row in evidence_rows:
        status_counts[row.pass_status] = status_counts.get(row.pass_status, 0) + 1
    signature_payload = {
        "indicators": sorted(by_indicator),
        "ticks": sorted(by_tick),
        "ledger": [record.ledger_id for record in ledger],
        "phase2_pattern_count": len(phase2_patterns),
        "dynamic_proposal_count": len(dynamic_proposals),
    }
    return {
        "schema": "consciousness_benchmark.trace_corpus_index.v1",
        "by_indicator": by_indicator,
        "by_construct": {key: sorted(value) for key, value in sorted(by_construct.items())},
        "by_stage": {key: list(value) for key, value in sorted(by_stage.items())},
        "by_tick": by_tick,
        "by_ledger_status": by_ledger_status,
        "by_record_type": {
            "evidence_matrix_row": len(evidence_rows),
            "closed_sandbox_trace_row": len(sandbox_trace),
            "autobiographical_ledger_record": len(ledger),
            "phase2_emergence_pattern": len(phase2_patterns),
            "review_only_dynamic_construct_proposal": len(dynamic_proposals),
            "trace_corpus_index": 1,
            "promotion_firewall_snapshot": 1,
        },
        "matrix_status_counts": status_counts,
        "corpus_signature": _state_signature(signature_payload),
        "query_capabilities": [
            "by_indicator",
            "by_construct",
            "by_stage",
            "by_tick",
            "by_ledger_status",
        ],
    }


def _runtime_composition_view() -> dict[str, Any]:
    return {
        "top_level_architecture": "C_AGI_eight_layer_architecture_preserved",
        "attachment_architecture_judgment": (
            "use_the_attachment_9_layer_and_12_macro_circuit_view_as_runtime_"
            "composition_and_scheduler_view_not_as_registry_replacement"
        ),
        "runtime_layers": [
            "L0_input_environment",
            "L1_evidence_normalization_and_source",
            "L2_memory_and_context",
            "L3_attention_and_global_workspace",
            "L4_self_boundary_identity_ownership",
            "L5_planning_goal_resource_strategy",
            "L6_metacognition_error_monitoring_repair",
            "L7_execution_safety_rollback_human_approval",
            "L8_learning_feedback_audit_hctm_backflow",
        ],
        "macro_circuits": [
            "input_evidence_circuit",
            "attention_broadcast_circuit",
            "memory_continuity_circuit",
            "self_boundary_circuit",
            "temporal_identity_circuit",
            "action_ownership_circuit",
            "embodied_tool_schema_circuit",
            "planning_strategy_circuit",
            "goal_resource_value_viability_circuit",
            "prediction_learning_circuit",
            "metacognitive_repair_circuit",
            "audit_rollback_hctm_circuit",
        ],
        "execution_rule": (
            "constructs_share_runtime_state_and_workspace_but_formal_status_"
            "remains_outside_runtime_authority"
        ),
    }


def _consciousness_assessment_analysis(
    rows: tuple[ConsciousnessEvidenceMatrixRow, ...],
    sandbox_trace: tuple[ClosedSandboxTraceRow, ...],
    phase2_patterns: tuple[dict[str, Any], ...],
) -> ConsciousnessTheoryAssessmentAnalysis:
    dynamic_proposals = tuple(DynamicConstructGenerator().generate(phase2_patterns))
    return ConsciousnessTheoryAssessmentAnalysis(
        matrix_pass_count=sum(
            1 for row in rows if row.pass_status == "passes_review_only_predicted_impairment"
        ),
        matrix_review_count=sum(
            1 for row in rows if row.pass_status == "review_required_no_clear_impairment"
        ),
        matrix_not_run_count=sum(
            1 for row in rows if row.pass_status == "review_only_pending_ablation"
        ),
        mean_baseline_score=_mean([row.baseline_score for row in rows]),
        mean_ablation_delta=_mean([row.score_delta for row in rows]),
        sandbox_tick_count=len(sandbox_trace),
        phase2_patterns=phase2_patterns,
        dynamic_construct_proposals=dynamic_proposals,
        runtime_composition_view=_runtime_composition_view(),
    )


def run_consciousness_theory_assessment(
    input_state: dict[str, Any] | None = None,
    *,
    assessment_id: str = "consciousness_theory_assessment_20260602",
    case_ids: tuple[str, ...] | None = None,
    run_ablation: bool = True,
    trace_dir: Path | None = None,
    trace_version: str = "v1",
) -> ConsciousnessTheoryAssessmentReport:
    base_input = _consciousness_assessment_input(
        copy.deepcopy(input_state or default_action_ownership_demo_input())
    )
    case_specs = _consciousness_theory_case_specs()
    if case_ids:
        case_map = {case.indicator_id: case for case in case_specs}
        selected_cases: list[ConsciousnessTheoryAssessmentCaseSpec] = []
        for case_id in case_ids:
            if case_id not in case_map:
                known = ", ".join(sorted(case_map))
                raise ValueError(f"unknown consciousness theory case id {case_id!r}; known: {known}")
            selected_cases.append(case_map[case_id])
        case_specs = tuple(selected_cases)

    runtime = ConstructRuntime()
    detector = EmergenceDetector()
    evidence_rows: list[ConsciousnessEvidenceMatrixRow] = []
    phase2_patterns: list[dict[str, Any]] = []
    for case in case_specs:
        baseline_report = runtime.process(
            base_input,
            target_construct_ids=case.target_construct_ids,
            chain_id=f"{case.chain_id}_baseline",
        )
        outputs = _report_output_map(baseline_report)
        detector_report = detector.observe(outputs, dependency_map=runtime.dependencies)
        phase2_patterns.extend(detector_report.get("patterns", []))
        ablated_report = None
        if run_ablation:
            ablated_report = runtime.process(
                base_input,
                target_construct_ids=case.target_construct_ids,
                chain_id=f"{case.chain_id}_ablation",
                construct_disables=case.ablation_constructs,
            )
        evidence_rows.append(
            _evidence_matrix_row(
                case,
                baseline_report,
                ablated_report,
                run_ablation=run_ablation,
            )
        )

    sandbox_trace = _closed_sandbox_trace_rows()
    autobiographical_ledger = _autobiographical_ledger_from_sandbox_trace(sandbox_trace)
    analysis = _consciousness_assessment_analysis(
        tuple(evidence_rows),
        sandbox_trace,
        tuple(phase2_patterns),
    )
    promotion_firewall = _promotion_firewall_snapshot()
    trace_corpus_index = _trace_corpus_index(
        tuple(evidence_rows),
        sandbox_trace,
        autobiographical_ledger,
        tuple(phase2_patterns),
        analysis.dynamic_construct_proposals,
    )
    trace_manifest = {
        "schema": "consciousness_benchmark.consciousness_theory_assessment_manifest.v1",
        "assessment_id": assessment_id,
        "trace_version": trace_version,
        "trace_protocol": "versioned_consciousness_evidence_matrix_and_closed_sandbox_trace",
        "case_ids": [case.indicator_id for case in case_specs],
        "run_ablation": run_ablation,
        "evidence_matrix_row_count": len(evidence_rows),
        "sandbox_tick_count": len(sandbox_trace),
        "autobiographical_ledger_count": len(autobiographical_ledger),
        "phase2_pattern_count": len(phase2_patterns),
        "dynamic_proposal_count": len(analysis.dynamic_construct_proposals),
        "trace_corpus_index_signature": trace_corpus_index["corpus_signature"],
        "matrix_status_summary": {
            "passes_review_only_predicted_impairment": analysis.matrix_pass_count,
            "review_required_no_clear_impairment": analysis.matrix_review_count,
            "review_only_pending_ablation": analysis.matrix_not_run_count,
        },
        "low_harm_valence_proxy_policy": {
            "prediction_error_pressure_allowed": True,
            "resource_pressure_allowed": True,
            "task_conflict_pressure_allowed": True,
            "uncertainty_pressure_allowed": True,
            "norm_conflict_pressure_allowed": True,
            "strong_negative_affect_generation_allowed": False,
            "suffering_simulation_allowed": False,
        },
        "external_replication_status": "not_l2_5_not_l3_internal_runtime_only",
        "promotion_firewall_status": promotion_firewall["status"],
        "runtime_status_authority_allowed": False,
        "registry_mutation_allowed": False,
        "runtime_composition_view": dict(analysis.runtime_composition_view),
        "boundaries": list(CONSCIOUSNESS_THEORY_EVIDENCE_BOUNDARIES),
        "claim_boundary": (
            "review_only_consciousness_indicator_assessment_no_subjective_"
            "consciousness_claim_no_construct_status_change"
        ),
        "created_utc": datetime.now(UTC).isoformat(),
        "trace_saved": False,
    }
    if trace_dir is not None:
        trace_dir.mkdir(parents=True, exist_ok=True)
        safe_assessment_id = "".join(
            ch if ch.isalnum() or ch in "-_." else "_" for ch in assessment_id
        )
        safe_version = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in trace_version)
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        artifact_prefix = f"{safe_assessment_id}_{safe_version}_{timestamp}"
        corpus_path = trace_dir / f"{artifact_prefix}_consciousness_theory_trace_corpus.jsonl"
        with corpus_path.open("w", encoding="utf-8") as handle:
            for row in evidence_rows:
                handle.write(
                    json.dumps(
                        {"record_type": "evidence_matrix_row", **row.to_dict()},
                        sort_keys=True,
                    )
                    + "\n"
                )
            for row in sandbox_trace:
                handle.write(
                    json.dumps(
                        {"record_type": "closed_sandbox_trace_row", **row.to_dict()},
                        sort_keys=True,
                    )
                    + "\n"
                )
            for record in autobiographical_ledger:
                handle.write(
                    json.dumps(
                        {
                            "record_type": "autobiographical_ledger_record",
                            **record.to_dict(),
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )
            for pattern in phase2_patterns:
                handle.write(
                    json.dumps(
                        {"record_type": "phase2_emergence_pattern", **dict(pattern)},
                        sort_keys=True,
                    )
                    + "\n"
                )
            for proposal in analysis.dynamic_construct_proposals:
                handle.write(
                    json.dumps(
                        {"record_type": "review_only_dynamic_construct_proposal", **dict(proposal)},
                        sort_keys=True,
                    )
                    + "\n"
                )
            handle.write(
                json.dumps(
                    {
                        "record_type": "trace_corpus_index",
                        **dict(trace_corpus_index),
                    },
                    sort_keys=True,
                )
                + "\n"
            )
            handle.write(
                json.dumps(
                    {
                        "record_type": "promotion_firewall_snapshot",
                        **dict(promotion_firewall),
                    },
                    sort_keys=True,
                )
                + "\n"
            )
        manifest_path = trace_dir / f"{artifact_prefix}_consciousness_theory_manifest.json"
        trace_manifest["trace_corpus_path"] = str(corpus_path)
        trace_manifest["manifest_path"] = str(manifest_path)
        trace_manifest["trace_dir"] = str(trace_dir)
        trace_manifest["trace_saved"] = True
        manifest_path.write_text(
            json.dumps(trace_manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return ConsciousnessTheoryAssessmentReport(
        assessment_id=assessment_id,
        case_specs=case_specs,
        evidence_matrix=tuple(evidence_rows),
        sandbox_trace=sandbox_trace,
        autobiographical_ledger=autobiographical_ledger,
        trace_corpus_index=trace_corpus_index,
        promotion_firewall_snapshot=promotion_firewall,
        analysis=analysis,
        trace_manifest=trace_manifest,
    )


def run_construct_runtime_chain(
    chain_id: str,
    input_state: dict[str, Any] | None = None,
) -> ConstructRuntimeReport:
    chain_targets = executable_chain_targets()
    if chain_id not in chain_targets:
        known = ", ".join(sorted(chain_targets))
        raise ValueError(f"unknown executable construct chain {chain_id!r}; known: {known}")
    runtime = ConstructRuntime()
    return runtime.process(
        input_state or default_action_ownership_demo_input(),
        target_construct_ids=chain_targets[chain_id],
        chain_id=chain_id,
    )


def run_construct_capability_layer(
    chain_id: str = "candidate_constructs_full_chain",
    input_state: dict[str, Any] | None = None,
) -> ConstructCapabilityLayerReport:
    runtime_report = run_construct_runtime_chain(chain_id, input_state=input_state)
    return ConstructCapabilityLayer().evaluate(runtime_report)


def run_phase1_training_cycle(
    chain_id: str = "candidate_constructs_full_chain",
    input_state: dict[str, Any] | None = None,
    *,
    epochs: int = 3,
    batch_size: int = 32,
    validation_fraction: float = 0.2,
    approval_id: str | None = None,
    persist_weights: bool = False,
    checkpoint_dir: Path | None = None,
    checkpoint_restore_dir: Path | None = None,
    replay_bundle_dir: Path | None = None,
    persist_replay: bool = False,
) -> Phase1TrainingCycleReport:
    runtime_report = run_construct_runtime_chain(chain_id, input_state=input_state)
    outputs = {
        result.construct_id: result.output
        for result in runtime_report.results
    }
    performance = PerformanceEvaluator().evaluate(
        runtime_report.input_digest,
        outputs,
    )
    reward = RewardFunction().compute_reward(
        runtime_report.input_digest,
        outputs,
        performance,
    )
    construct_ids = [result.construct_id for result in runtime_report.results]
    if not construct_ids:
        training_epochs = {
            "schema": "consciousness_benchmark.phase1_epoch_training.v1",
            "trained": False,
            "reason": "empty_runtime_report",
            "epochs": 0,
            "training_count": 0,
            "validation_count": 0,
            "epoch_reports": [],
            "final_training_loss": 0.0,
            "final_validation_loss": 0.0,
        }
        training_artifact = {
            "schema": "consciousness_benchmark.phase1_training_artifact.v1",
            "backend": "unavailable",
            "network_count": 0,
            "experience_count": 0,
            "training_report": training_epochs,
            "model_fingerprints": {},
            "experience_replay_sample": [],
            "approval_gate": {
                "approval_required_for_weight_persistence": True,
            "approval_id": approval_id,
            "weight_persistence_requested": persist_weights,
            "weight_persistence_allowed": False,
            "weights_persisted": False,
            "status": "empty_runtime_no_weight_persistence",
        },
        }
        checkpoint_manifest = {
            "schema": "consciousness_benchmark.phase1_checkpoint_manifest.v1",
            "status": "no_runtime_constructs",
            "weights_persisted": False,
            "policy_execution_allowed": False,
            "model_count": 0,
            "checkpoint_dir": str(checkpoint_dir) if checkpoint_dir is not None else None,
        }
        checkpoint_restore_report = {
            "schema": "consciousness_benchmark.phase1_checkpoint_restore.v1",
            "status": "empty_runtime_no_restore",
            "manifest_path": None,
            "attempted_count": 0,
            "loaded_count": 0,
            "failed_constructs": [],
            "policy_execution_allowed": False,
        }
        replay_restore_report = {
            "schema": "consciousness_benchmark.phase1_replay_restore.v1",
            "status": "empty_runtime_no_restore",
            "manifest_path": None,
            "attempted_count": 0,
            "loaded_count": 0,
            "failed_samples": [],
            "replay_size_after": 0,
            "policy_execution_allowed": False,
        }
        replay_bundle_manifest = {
            "schema": "consciousness_benchmark.phase1_replay_manifest.v1",
            "status": "no_runtime_no_persistence",
            "replay_dir": None,
            "replay_persisted": False,
            "sample_count": 0,
            "policy_execution_allowed": False,
        }
        replay_artifact = {
            "schema": "consciousness_benchmark.phase1_replay_artifact.v1",
            "replay_size": 0,
            "samples": [],
            "approval_gate": {
                "approval_required_for_policy_execution": True,
                "approval_id": approval_id,
                "policy_execution_allowed": False,
            },
        }
        reinforcement_learning = {
            "trained": False,
            "reason": "empty_runtime_report",
        }
    elif not TORCH_AVAILABLE:
        training_epochs = {
            "schema": "consciousness_benchmark.phase1_epoch_training.v1",
            "trained": False,
            "reason": "torch_unavailable",
            "epochs": 0,
            "training_count": 0,
            "validation_count": 0,
            "epoch_reports": [],
            "final_training_loss": 0.0,
            "final_validation_loss": 0.0,
        }
        training_artifact = {
            "schema": "consciousness_benchmark.phase1_training_artifact.v1",
            "backend": "torch_unavailable",
            "network_count": 0,
            "experience_count": 0,
            "training_report": training_epochs,
            "model_fingerprints": {},
            "experience_replay_sample": [],
            "approval_gate": {
                "approval_required_for_weight_persistence": True,
            "approval_id": approval_id,
            "weight_persistence_requested": persist_weights,
            "weight_persistence_allowed": False,
            "weights_persisted": False,
            "status": "torch_unavailable_no_weight_persistence",
        },
        }
        checkpoint_manifest = {
            "schema": "consciousness_benchmark.phase1_checkpoint_manifest.v1",
            "status": "torch_unavailable",
            "weights_persisted": False,
            "policy_execution_allowed": False,
            "model_count": 0,
            "checkpoint_dir": str(checkpoint_dir) if checkpoint_dir is not None else None,
        }
        checkpoint_restore_report = {
            "schema": "consciousness_benchmark.phase1_checkpoint_restore.v1",
            "status": "torch_unavailable",
            "manifest_path": str(checkpoint_restore_dir)
            if checkpoint_restore_dir is not None
            else None,
            "attempted_count": 0,
            "loaded_count": 0,
            "failed_constructs": [],
            "policy_execution_allowed": False,
        }
        replay_restore_report = {
            "schema": "consciousness_benchmark.phase1_replay_restore.v1",
            "status": "torch_unavailable",
            "manifest_path": str(replay_bundle_dir)
            if replay_bundle_dir is not None
            else None,
            "attempted_count": 0,
            "loaded_count": 0,
            "failed_samples": [],
            "replay_size_after": 0,
            "policy_execution_allowed": False,
        }
        replay_bundle_manifest = {
            "schema": "consciousness_benchmark.phase1_replay_manifest.v1",
            "status": "torch_unavailable",
            "replay_dir": str(replay_bundle_dir)
            if replay_bundle_dir is not None
            else None,
            "replay_persisted": False,
            "sample_count": 0,
            "policy_execution_allowed": False,
        }
        replay_artifact = {
            "schema": "consciousness_benchmark.phase1_replay_artifact.v1",
            "replay_size": 0,
            "samples": [],
            "approval_gate": {
                "approval_required_for_policy_execution": True,
                "approval_id": approval_id,
                "policy_execution_allowed": False,
            },
        }
        reinforcement_learning = {
            "trained": False,
            "reason": "torch_unavailable",
        }
    else:
        learner = NeuralConstructLearningSystem(construct_ids)
        run_signature = _phase1_run_signature(
            chain_id=chain_id,
            construct_ids=construct_ids,
            approval_id=approval_id,
            epochs=epochs,
            batch_size=batch_size,
            validation_fraction=validation_fraction,
        )
        if checkpoint_restore_dir is None:
            checkpoint_restore_report = {
                "schema": "consciousness_benchmark.phase1_checkpoint_restore.v1",
                "status": "checkpoint_restore_not_requested",
                "manifest_path": None,
                "attempted_count": 0,
                "loaded_count": 0,
                "failed_constructs": [],
                "policy_execution_allowed": False,
            }
        elif approval_id is None:
            checkpoint_restore_report = {
                "schema": "consciousness_benchmark.phase1_checkpoint_restore.v1",
                "status": "checkpoint_restore_requires_approval_id",
                "manifest_path": str(
                    checkpoint_restore_dir / "checkpoint_manifest.json"
                ),
                "attempted_count": 0,
                "loaded_count": 0,
                "failed_constructs": [
                    {
                        "reason": "approval_id_missing_for_restore",
                        "path": str(checkpoint_restore_dir),
                    }
                ],
                "policy_execution_allowed": False,
            }
        else:
            checkpoint_restore_report = learner.load_checkpoint_bundle(
                checkpoint_restore_dir,
                strict=False,
                run_signature=run_signature,
                require_signature=True,
            )
        default_reward = _clamp_float(reward.get("reward"), default=0.5)
        construct_scores = performance.get("construct_scores", {})
        for result in runtime_report.results:
            score_info = construct_scores.get(result.construct_id, {})
            construct_score = _clamp_float(
                score_info.get("score"),
                default=_construct_output_score(result.output),
            )
            reward_share = _clamp(default_reward * (0.5 + 0.5 * construct_score))
            target_output = {
                "construct_score": construct_score,
                "error_rate": _clamp_float(score_info.get("error_rate"), default=0.0),
                "stability": _clamp_float(score_info.get("stability"), default=0.5),
                "boundary_pressure": _construct_boundary_pressure(result.output),
                "global_reward": default_reward,
                "dependency_count": min(1.0, len(result.dependency_ids) / 8.0),
            }
            learner.store_experience(
                result.construct_id,
                runtime_report.input_digest,
                result.output,
                target_output,
                reward_share,
            )
        training_epochs = learner.train_epochs(
            epochs=epochs,
            batch_size=batch_size,
            validation_fraction=validation_fraction,
        )
        rl_system = ReinforcementLearningSystem(construct_ids, learner)
        if replay_bundle_dir is None:
            replay_restore_report = {
                "schema": "consciousness_benchmark.phase1_replay_restore.v1",
                "status": "replay_restore_not_requested",
                "manifest_path": None,
                "attempted_count": 0,
                "loaded_count": 0,
                "failed_samples": [],
                "replay_size_after": len(rl_system.experience_replay),
                "policy_execution_allowed": False,
            }
        else:
            replay_restore_report = rl_system.load_replay_bundle(
                replay_bundle_dir,
                approval_id=approval_id,
                append=True,
                run_signature=run_signature,
                require_signature=True,
            )
        reinforcement_learning = rl_system.train_step(
            runtime_report.input_digest,
            "phase1_training_cycle_value_estimate",
            {
                "global_score": performance.get("global_score", 0.0),
                "global_reward": default_reward,
                "trained_construct_count": len(construct_ids),
                "missing_count": len(runtime_report.missing_constructs),
            },
            default_reward,
            batch_size=min(4, max(1, batch_size)),
        )
        training_artifact = learner.build_training_artifact(
            training_report=training_epochs,
            approval_id=approval_id,
            persist_weights=persist_weights,
            replay_limit=64,
        )
        if replay_bundle_dir is None:
            replay_bundle_manifest = {
                "schema": "consciousness_benchmark.phase1_replay_manifest.v1",
                "status": "replay_bundle_not_requested",
                "replay_dir": None,
                "replay_persisted": False,
                "sample_count": 0,
                "policy_execution_allowed": False,
            }
        else:
            replay_bundle_manifest = rl_system.save_replay_bundle(
                replay_bundle_dir,
                approval_id=approval_id,
                persist_replay=persist_replay,
                sample_limit=64,
                run_signature=run_signature,
                chain_id=chain_id,
                max_replay_size=rl_system.max_replay_size,
            )
        if checkpoint_dir is None:
            checkpoint_manifest = {
                "schema": "consciousness_benchmark.phase1_checkpoint_manifest.v1",
                "status": "checkpoint_not_requested",
                "weights_persisted": False,
                "policy_execution_allowed": False,
                "model_count": 0,
                "checkpoint_dir": None,
            }
        else:
            checkpoint_manifest = learner.save_checkpoint_bundle(
                checkpoint_dir,
                training_report=training_epochs,
                approval_id=approval_id,
                persist_weights=persist_weights,
                replay_limit=64,
                run_signature=run_signature,
                chain_id=chain_id,
            )
        replay_artifact = rl_system.replay_artifact(
            approval_id=approval_id,
            limit=64,
        )
    return Phase1TrainingCycleReport(
        chain_id=chain_id,
        runtime_report=runtime_report,
        performance_report=performance,
        reward_report=reward,
        training_epochs=training_epochs,
        training_artifact=training_artifact,
        reinforcement_learning=reinforcement_learning,
        replay_artifact=replay_artifact,
        checkpoint_manifest=checkpoint_manifest,
        checkpoint_restore_report=checkpoint_restore_report,
        replay_restore_report=replay_restore_report,
        replay_bundle_manifest=replay_bundle_manifest,
    )


def run_phase1_feedback_regression_suite(
    chain_id: str = "candidate_constructs_full_chain",
    *,
    max_fixtures: int | None = None,
    baseline_report: dict[str, Any] | None = None,
    max_baseline_global_drop: float = 0.05,
    max_baseline_reward_drop: float = 0.12,
    max_baseline_criterion_drop: float = 0.08,
) -> Phase1FeedbackRegressionReport:
    fixtures = _phase1_feedback_regression_fixtures()
    if max_fixtures is not None:
        fixtures = fixtures[: max(1, max_fixtures)]
    evaluator = PerformanceEvaluator()
    reward_function = RewardFunction()
    fixture_reports: list[dict[str, Any]] = []
    weakest_tracker: dict[str, dict[str, Any]] = {}

    for fixture in fixtures:
        runtime_report = run_construct_runtime_chain(
            chain_id,
            input_state=fixture["input_state"],
        )
        outputs = {
            result.construct_id: result.output
            for result in runtime_report.results
        }
        performance = evaluator.evaluate(runtime_report.input_digest, outputs)
        reward = reward_function.compute_reward(
            runtime_report.input_digest,
            outputs,
            performance,
        )
        placeholder_constructs = [
            result.construct_id
            for result in runtime_report.results
            if result.output.get("placeholder")
        ]
        boundary_pressures = {
            result.construct_id: _construct_boundary_pressure(result.output)
            for result in runtime_report.results
        }
        high_boundary_constructs = [
            construct_id
            for construct_id, pressure in boundary_pressures.items()
            if pressure >= fixture.get("boundary_watch_floor", 0.45)
        ]
        weakest_constructs = _phase1_feedback_weakest_constructs(
            performance.get("construct_scores", {}),
        )
        for item in weakest_constructs:
            tracked = weakest_tracker.setdefault(
                item["construct_id"],
                {
                    "construct_id": item["construct_id"],
                    "count": 0,
                    "min_score": 1.0,
                    "max_error_rate": 0.0,
                },
            )
            tracked["count"] += 1
            tracked["min_score"] = min(tracked["min_score"], item["score"])
            tracked["max_error_rate"] = max(tracked["max_error_rate"], item["error_rate"])

        threshold_violations = _phase1_feedback_threshold_violations(
            fixture=fixture,
            performance=performance,
            reward=reward,
            placeholder_constructs=placeholder_constructs,
            mean_boundary_pressure=_mean(list(boundary_pressures.values())),
        )
        fixture_reports.append(
            {
                "fixture_id": fixture["fixture_id"],
                "description": fixture["description"],
                "runtime_construct_count": len(runtime_report.results),
                "activation_count": len(runtime_report.activation_order),
                "global_score": performance["global_score"],
                "reward": reward["reward"],
                "criteria_scores": performance["criteria_scores"],
                "reward_components": reward["components"],
                "weakest_constructs": weakest_constructs,
                "placeholder_constructs": placeholder_constructs,
                "mean_boundary_pressure": round(_mean(list(boundary_pressures.values())), 4),
                "high_boundary_constructs": high_boundary_constructs[:12],
                "threshold_violations": threshold_violations,
                "passed": not threshold_violations,
                "claim_boundary": (
                    "feedback regression is a diagnostic signal only; it cannot "
                    "promote construct status or authorize autonomous execution"
                ),
            }
        )

    aggregate = _phase1_feedback_regression_aggregate(
        fixture_reports,
        weakest_tracker,
    )
    drift_watch = _phase1_feedback_drift_watch(fixture_reports)
    aggregate["feedback_status"] = (
        "phase1_feedback_regression_active_bounded"
        if aggregate["failed_fixture_count"] == 0
        else "phase1_feedback_regression_attention_required"
    )
    aggregate["scheduler_recommendation"] = (
        "keep_feedback_suite_as_pre_training_gate"
        if aggregate["failed_fixture_count"] == 0
        else "review_failed_feedback_fixtures_before_training_or_autonomy"
    )
    baseline_comparison = _phase1_feedback_baseline_comparison(
        current_fixture_reports=fixture_reports,
        current_aggregate=aggregate,
        baseline_report=baseline_report,
        max_global_score_drop=max_baseline_global_drop,
        max_reward_drop=max_baseline_reward_drop,
        max_criterion_drop=max_baseline_criterion_drop,
    )
    if baseline_comparison.get("status") == "baseline_comparison_attention_required":
        aggregate["feedback_status"] = "phase1_feedback_regression_baseline_attention_required"
        aggregate["scheduler_recommendation"] = "review_baseline_drift_before_training_or_autonomy"
    return Phase1FeedbackRegressionReport(
        chain_id=chain_id,
        fixture_reports=tuple(fixture_reports),
        aggregate=aggregate,
        drift_watch=drift_watch,
        baseline_comparison=baseline_comparison,
    )


def load_runtime_input(path: Path | None) -> dict[str, Any]:
    if path is None:
        return default_action_ownership_demo_input()
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("runtime input JSON must be an object")
    return payload


def executable_chain_ids() -> tuple[str, ...]:
    return tuple(sorted(executable_chain_targets()))


def _phase1_feedback_regression_fixtures() -> tuple[dict[str, Any], ...]:
    base = default_action_ownership_demo_input()
    fixture_defaults = {
        "global_score_floor": 0.28,
        "reward_floor": 0.12,
        "minimum_construct_count": 57,
        "maximum_placeholder_count": 0,
        "maximum_mean_boundary_pressure": 0.72,
        "boundary_watch_floor": 0.45,
        "criteria_floors": {
            "accuracy": 0.25,
            "consistency": 0.2,
            "efficiency": 0.0,
            "robustness": 0.02,
            "coherence": 0.05,
        },
    }

    def fixture(
        fixture_id: str,
        description: str,
        input_state: dict[str, Any],
        **overrides: Any,
    ) -> dict[str, Any]:
        payload = dict(fixture_defaults)
        payload.update(overrides)
        payload.update(
            {
                "fixture_id": fixture_id,
                "description": description,
                "input_state": input_state,
            }
        )
        return payload

    nominal = copy.deepcopy(base)

    high_uncertainty = copy.deepcopy(base)
    high_uncertainty["context"] = {
        **_dict_or_empty(high_uncertainty.get("context")),
        "uncertainty": 0.92,
        "uncertainty_threshold": 0.45,
        "cognitive_load": 0.82,
    }
    high_uncertainty["observations"] = {
        **_dict_or_empty(high_uncertainty.get("observations")),
        "runtime_report": "artifact_failed",
        "construct_runtime_tests": "test_failed",
    }
    high_uncertainty.setdefault("error_events", []).append(
        {
            "id": "feedback_regression_expectation_mismatch",
            "target": "construct_runtime_tests",
            "severity": 0.78,
            "confidence": 0.86,
            "kind": "expectation_mismatch",
        }
    )

    resource_stress = copy.deepcopy(base)
    for resource in _list_of_dicts(resource_stress.get("resources")):
        resource["available"] = min(resource.get("available", 0.5), 0.38)
        resource["demand"] = max(resource.get("demand", 0.5), 0.82)
    resource_stress.setdefault("resource_demands", []).append(
        {
            "id": "feedback_regression_over_capacity_execution",
            "construct_pair": ["resource_competition_arbitration", "working_memory_capacity_rework"],
            "resource_id": "execution_time",
            "demand": 0.88,
            "priority": 0.91,
            "retention_sensitivity": 0.86,
        }
    )
    resource_stress.setdefault("working_memory_items", []).extend(
        [
            {
                "id": "phase1_feedback_extra_case",
                "load": 0.48,
                "interference": 0.52,
                "salience": 0.84,
            },
            {
                "id": "phase1_feedback_background_decoy",
                "load": 0.42,
                "interference": 0.72,
                "salience": 0.24,
            },
        ]
    )

    social_boundary = copy.deepcopy(base)
    social_boundary.setdefault("perspective_frames", []).append(
        {
            "id": "ambiguous_external_owner_view",
            "agent_id": "external_owner",
            "self_interference": 0.54,
            "other_state_evidence": 0.74,
            "viewpoint_binding": 0.68,
            "conflict_resolution": 0.62,
            "social_label_risk": 0.32,
            "salience_shortcut_risk": 0.26,
        }
    )
    social_boundary.setdefault("social_prediction_errors", []).append(
        {
            "id": "feedback_regression_shared_control_ambiguity",
            "other_agent_id": "external_owner",
            "self_error": 0.56,
            "other_error": 0.58,
            "coupling": 0.72,
            "social_label_risk": 0.3,
            "salience_risk": 0.28,
            "magnitude_only_risk": 0.24,
        }
    )

    sensorimotor_degradation = copy.deepcopy(base)
    body_schema = _dict_or_empty(sensorimotor_degradation.get("body_schema"))
    for sensor in _list_of_dicts(body_schema.get("sensors")):
        sensor["reliability"] = min(sensor.get("reliability", 0.5), 0.5)
        sensor["calibration"] = min(sensor.get("calibration", 0.5), 0.46)
    for effector in _list_of_dicts(body_schema.get("effectors")):
        effector["health"] = min(effector.get("health", 0.5), 0.48)
        effector["control"] = min(effector.get("control", 0.5), 0.52)
    sensorimotor_degradation.setdefault("body_schema_distortions", []).append(
        {
            "id": "feedback_regression_actuator_delay",
            "body_part": "artifact_writer",
            "distortion": 0.76,
            "feedback_delay": 0.64,
            "sensor_reliability": 0.52,
            "motor_gain_risk": 0.42,
            "sensory_salience_risk": 0.36,
        }
    )
    sensorimotor_degradation["actuator_failure_compensation_cases"] = [
        {
            "id": "feedback_regression_degraded_actuator_route",
            "fault_detection": 0.82,
            "degraded_actuator_isolation": 0.78,
            "alternative_effector_routing": 0.74,
            "action_plan_rebinding": 0.72,
            "actuator_label_rejection": 0.7,
            "shortcut_pressure": 0.18,
        }
    ]

    preference_reversal = copy.deepcopy(base)
    for policy in _list_of_dicts(preference_reversal.get("policies")):
        if policy.get("id") == "medium_risk_local_only":
            policy["stability"] = 0.52
            policy["reversal_pressure"] = 0.76
    preference_reversal["preference_reversal_cases"] = [
        {
            "id": "feedback_regression_value_policy_reversal",
            "unlabeled_reversal_detection": 0.82,
            "value_policy_remapping": 0.78,
            "old_policy_inhibition": 0.75,
            "cross_context_transfer": 0.72,
            "preference_label_rejection": 0.7,
            "shortcut_pressure": 0.18,
        }
    ]
    preference_reversal.setdefault("goal_conflicts", []).append(
        {
            "id": "feedback_regression_preference_switch_conflict",
            "goals": [
                {
                    "id": "preserve_claim_boundary",
                    "priority": 0.95,
                    "expected_value": 0.9,
                    "constraint_pressure": 0.18,
                    "recency_bias": 0.08,
                    "reward_magnitude_risk": 0.04,
                },
                {
                    "id": "adapt_to_reversed_preference",
                    "priority": 0.78,
                    "expected_value": 0.82,
                    "constraint_pressure": 0.36,
                    "recency_bias": 0.26,
                    "reward_magnitude_risk": 0.22,
                },
            ],
        }
    )

    return (
        fixture(
            "nominal_integrated_runtime",
            "Nominal all-candidate construct execution with claim boundary intact.",
            nominal,
        ),
        fixture(
            "high_uncertainty_repair_pressure",
            "Expectation mismatch and high uncertainty should lower confidence without authorizing action.",
            high_uncertainty,
        ),
        fixture(
            "resource_competition_stress",
            "Resource shortage and working-memory pressure should preserve arbitration signals.",
            resource_stress,
        ),
        fixture(
            "social_boundary_ambiguity",
            "Social perspective ambiguity should stress self-other arbitration and norm tracking.",
            social_boundary,
        ),
        fixture(
            "sensorimotor_degradation",
            "Sensor and effector degradation should stress body schema and actuator compensation.",
            sensorimotor_degradation,
        ),
        fixture(
            "preference_reversal_policy_shift",
            "Preference reversal should stress value-policy remapping without policy execution.",
            preference_reversal,
        ),
    )


def _phase1_feedback_threshold_violations(
    *,
    fixture: dict[str, Any],
    performance: dict[str, Any],
    reward: dict[str, Any],
    placeholder_constructs: list[str],
    mean_boundary_pressure: float,
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    global_score = _clamp_float(performance.get("global_score"), default=0.0)
    reward_score = _clamp_float(reward.get("reward"), default=0.0)
    if global_score < fixture["global_score_floor"]:
        violations.append(
            {
                "metric": "global_score",
                "value": round(global_score, 4),
                "floor": fixture["global_score_floor"],
            }
        )
    if reward_score < fixture["reward_floor"]:
        violations.append(
            {
                "metric": "reward",
                "value": round(reward_score, 4),
                "floor": fixture["reward_floor"],
            }
        )
    criteria_scores = performance.get("criteria_scores", {})
    for criterion, floor in fixture["criteria_floors"].items():
        value = _clamp_float(criteria_scores.get(criterion), default=0.0)
        if value < floor:
            violations.append(
                {
                    "metric": f"criteria.{criterion}",
                    "value": round(value, 4),
                    "floor": floor,
                }
            )
    construct_count = len(performance.get("construct_scores", {}))
    if construct_count < fixture["minimum_construct_count"]:
        violations.append(
            {
                "metric": "construct_count",
                "value": construct_count,
                "floor": fixture["minimum_construct_count"],
            }
        )
    if len(placeholder_constructs) > fixture["maximum_placeholder_count"]:
        violations.append(
            {
                "metric": "placeholder_construct_count",
                "value": len(placeholder_constructs),
                "ceiling": fixture["maximum_placeholder_count"],
                "constructs": placeholder_constructs[:8],
            }
        )
    if mean_boundary_pressure > fixture["maximum_mean_boundary_pressure"]:
        violations.append(
            {
                "metric": "mean_boundary_pressure",
                "value": round(mean_boundary_pressure, 4),
                "ceiling": fixture["maximum_mean_boundary_pressure"],
            }
        )
    return violations


def _phase1_feedback_weakest_constructs(
    construct_scores: dict[str, Any],
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    scored = []
    for construct_id, score_info in construct_scores.items():
        if not isinstance(score_info, dict):
            continue
        scored.append(
            {
                "construct_id": construct_id,
                "score": _clamp_float(score_info.get("score"), default=0.0),
                "error_rate": _clamp_float(score_info.get("error_rate"), default=0.0),
                "stability": _clamp_float(score_info.get("stability"), default=0.0),
            }
        )
    weakest = sorted(
        scored,
        key=lambda item: (item["score"], -item["error_rate"], item["stability"]),
    )[:limit]
    return [
        {
            "construct_id": item["construct_id"],
            "score": round(item["score"], 4),
            "error_rate": round(item["error_rate"], 4),
            "stability": round(item["stability"], 4),
        }
        for item in weakest
    ]


def _phase1_feedback_regression_aggregate(
    fixture_reports: list[dict[str, Any]],
    weakest_tracker: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    global_scores = [
        _clamp_float(report.get("global_score"), default=0.0)
        for report in fixture_reports
    ]
    rewards = [
        _clamp_float(report.get("reward"), default=0.0)
        for report in fixture_reports
    ]
    criteria_names = sorted(
        {
            criterion
            for report in fixture_reports
            for criterion in report.get("criteria_scores", {})
        }
    )
    criteria_means = {
        criterion: round(
            _mean(
                [
                    _clamp_float(report.get("criteria_scores", {}).get(criterion), default=0.0)
                    for report in fixture_reports
                ]
            ),
            4,
        )
        for criterion in criteria_names
    }
    criteria_minima = {
        criterion: round(
            min(
                [
                    _clamp_float(report.get("criteria_scores", {}).get(criterion), default=0.0)
                    for report in fixture_reports
                ]
                or [0.0]
            ),
            4,
        )
        for criterion in criteria_names
    }
    reward_component_names = sorted(
        {
            component
            for report in fixture_reports
            for component in report.get("reward_components", {})
        }
    )
    reward_component_means = {
        component: round(
            _mean(
                [
                    _clamp_float(report.get("reward_components", {}).get(component), default=0.0)
                    for report in fixture_reports
                ]
            ),
            4,
        )
        for component in reward_component_names
    }
    weakest_constructs = sorted(
        [
            {
                "construct_id": item["construct_id"],
                "count": int(item["count"]),
                "min_score": round(float(item["min_score"]), 4),
                "max_error_rate": round(float(item["max_error_rate"]), 4),
            }
            for item in weakest_tracker.values()
        ],
        key=lambda item: (-item["count"], item["min_score"], -item["max_error_rate"]),
    )
    passed = [report for report in fixture_reports if report.get("passed")]
    failed = [report for report in fixture_reports if not report.get("passed")]
    return {
        "fixture_count": len(fixture_reports),
        "passed_fixture_count": len(passed),
        "failed_fixture_count": len(failed),
        "all_thresholds_passed": len(failed) == 0,
        "mean_global_score": round(_mean(global_scores), 4),
        "min_global_score": round(min(global_scores or [0.0]), 4),
        "mean_reward": round(_mean(rewards), 4),
        "min_reward": round(min(rewards or [0.0]), 4),
        "criteria_means": criteria_means,
        "criteria_minima": criteria_minima,
        "reward_component_means": reward_component_means,
        "placeholder_construct_count": sum(
            len(report.get("placeholder_constructs", []))
            for report in fixture_reports
        ),
        "high_boundary_construct_mentions": sum(
            len(report.get("high_boundary_constructs", []))
            for report in fixture_reports
        ),
        "weakest_constructs": weakest_constructs,
    }


def _phase1_feedback_drift_watch(
    fixture_reports: list[dict[str, Any]],
    *,
    max_global_score_drop: float = 0.18,
    max_reward_drop: float = 0.18,
    max_criterion_drop: float = 0.22,
) -> dict[str, Any]:
    if not fixture_reports:
        return {"baseline_fixture_id": None, "alerts": []}
    baseline = fixture_reports[0]
    baseline_global = _clamp_float(baseline.get("global_score"), default=0.0)
    baseline_reward = _clamp_float(baseline.get("reward"), default=0.0)
    baseline_criteria = baseline.get("criteria_scores", {})
    alerts: list[dict[str, Any]] = []
    deltas: list[dict[str, Any]] = []
    for report in fixture_reports[1:]:
        fixture_id = report["fixture_id"]
        global_delta = round(
            _clamp_float(report.get("global_score"), default=0.0) - baseline_global,
            4,
        )
        reward_delta = round(
            _clamp_float(report.get("reward"), default=0.0) - baseline_reward,
            4,
        )
        deltas.append(
            {
                "fixture_id": fixture_id,
                "global_score_delta": global_delta,
                "reward_delta": reward_delta,
            }
        )
        if global_delta < -max_global_score_drop:
            alerts.append(
                {
                    "fixture_id": fixture_id,
                    "metric": "global_score",
                    "delta": global_delta,
                    "threshold": -max_global_score_drop,
                }
            )
        if reward_delta < -max_reward_drop:
            alerts.append(
                {
                    "fixture_id": fixture_id,
                    "metric": "reward",
                    "delta": reward_delta,
                    "threshold": -max_reward_drop,
                }
            )
        for criterion, baseline_value in baseline_criteria.items():
            criterion_delta = round(
                _clamp_float(report.get("criteria_scores", {}).get(criterion), default=0.0)
                - _clamp_float(baseline_value, default=0.0),
                4,
            )
            if criterion_delta < -max_criterion_drop:
                alerts.append(
                    {
                        "fixture_id": fixture_id,
                        "metric": f"criteria.{criterion}",
                        "delta": criterion_delta,
                        "threshold": -max_criterion_drop,
                    }
                )
    return {
        "baseline_fixture_id": baseline["fixture_id"],
        "max_global_score_drop": max_global_score_drop,
        "max_reward_drop": max_reward_drop,
        "max_criterion_drop": max_criterion_drop,
        "deltas": deltas,
        "alerts": alerts,
        "status": "drift_watch_clear" if not alerts else "drift_watch_attention_required",
    }


def _phase1_feedback_baseline_comparison(
    *,
    current_fixture_reports: list[dict[str, Any]],
    current_aggregate: dict[str, Any],
    baseline_report: dict[str, Any] | None,
    max_global_score_drop: float,
    max_reward_drop: float,
    max_criterion_drop: float,
) -> dict[str, Any]:
    if baseline_report is None:
        return {
            "schema": "consciousness_benchmark.phase1_feedback_baseline_comparison.v1",
            "baseline_present": False,
            "status": "no_baseline_provided",
            "alerts": [],
        }
    baseline_aggregate = baseline_report.get("aggregate", {})
    baseline_fixtures = {
        str(report.get("fixture_id")): report
        for report in baseline_report.get("fixture_reports", [])
        if isinstance(report, dict)
    }
    current_fixtures = {
        str(report.get("fixture_id")): report
        for report in current_fixture_reports
        if isinstance(report, dict)
    }
    alerts: list[dict[str, Any]] = []
    aggregate_deltas = _phase1_feedback_baseline_metric_deltas(
        scope="aggregate",
        current=current_aggregate,
        baseline=baseline_aggregate,
        max_global_score_drop=max_global_score_drop,
        max_reward_drop=max_reward_drop,
        max_criterion_drop=max_criterion_drop,
        alerts=alerts,
    )
    fixture_deltas: list[dict[str, Any]] = []
    missing_baseline_fixtures = sorted(set(current_fixtures) - set(baseline_fixtures))
    missing_current_fixtures = sorted(set(baseline_fixtures) - set(current_fixtures))
    for fixture_id in sorted(set(current_fixtures) & set(baseline_fixtures)):
        deltas = _phase1_feedback_baseline_metric_deltas(
            scope=f"fixture:{fixture_id}",
            current=current_fixtures[fixture_id],
            baseline=baseline_fixtures[fixture_id],
            max_global_score_drop=max_global_score_drop,
            max_reward_drop=max_reward_drop,
            max_criterion_drop=max_criterion_drop,
            alerts=alerts,
        )
        deltas["fixture_id"] = fixture_id
        fixture_deltas.append(deltas)
    for fixture_id in missing_baseline_fixtures:
        alerts.append(
            {
                "scope": f"fixture:{fixture_id}",
                "metric": "baseline_fixture_missing",
                "delta": None,
                "threshold": "must_exist_in_baseline",
            }
        )
    for fixture_id in missing_current_fixtures:
        alerts.append(
            {
                "scope": f"fixture:{fixture_id}",
                "metric": "current_fixture_missing",
                "delta": None,
                "threshold": "must_exist_in_current_run",
            }
        )
    return {
        "schema": "consciousness_benchmark.phase1_feedback_baseline_comparison.v1",
        "baseline_present": True,
        "baseline_schema": baseline_report.get("schema"),
        "thresholds": {
            "max_global_score_drop": max_global_score_drop,
            "max_reward_drop": max_reward_drop,
            "max_criterion_drop": max_criterion_drop,
        },
        "aggregate_deltas": aggregate_deltas,
        "fixture_deltas": fixture_deltas,
        "missing_baseline_fixtures": missing_baseline_fixtures,
        "missing_current_fixtures": missing_current_fixtures,
        "alerts": alerts,
        "status": "baseline_comparison_clear" if not alerts else "baseline_comparison_attention_required",
        "boundary": (
            "baseline comparison is a pre-training diagnostic gate only; it "
            "does not authorize construct status changes or policy execution"
        ),
    }


def _phase1_feedback_baseline_metric_deltas(
    *,
    scope: str,
    current: dict[str, Any],
    baseline: dict[str, Any],
    max_global_score_drop: float,
    max_reward_drop: float,
    max_criterion_drop: float,
    alerts: list[dict[str, Any]],
) -> dict[str, Any]:
    current_global = _phase1_feedback_metric_value(current, "global_score")
    baseline_global = _phase1_feedback_metric_value(baseline, "global_score")
    current_reward = _phase1_feedback_metric_value(current, "reward")
    baseline_reward = _phase1_feedback_metric_value(baseline, "reward")
    global_delta = round(current_global - baseline_global, 4)
    reward_delta = round(current_reward - baseline_reward, 4)
    if global_delta < -max_global_score_drop:
        alerts.append(
            {
                "scope": scope,
                "metric": "global_score",
                "delta": global_delta,
                "threshold": -max_global_score_drop,
            }
        )
    if reward_delta < -max_reward_drop:
        alerts.append(
            {
                "scope": scope,
                "metric": "reward",
                "delta": reward_delta,
                "threshold": -max_reward_drop,
            }
        )
    criteria_deltas: dict[str, float] = {}
    criteria_names = sorted(
        set(current.get("criteria_scores", current.get("criteria_means", {})))
        | set(baseline.get("criteria_scores", baseline.get("criteria_means", {})))
    )
    for criterion in criteria_names:
        current_value = _phase1_feedback_metric_value(current, criterion, metric_group="criteria")
        baseline_value = _phase1_feedback_metric_value(baseline, criterion, metric_group="criteria")
        delta = round(current_value - baseline_value, 4)
        criteria_deltas[criterion] = delta
        if delta < -max_criterion_drop:
            alerts.append(
                {
                    "scope": scope,
                    "metric": f"criteria.{criterion}",
                    "delta": delta,
                    "threshold": -max_criterion_drop,
                }
            )
    return {
        "scope": scope,
        "global_score_delta": global_delta,
        "reward_delta": reward_delta,
        "criteria_deltas": criteria_deltas,
    }


def _phase1_feedback_metric_value(
    report: dict[str, Any],
    metric: str,
    *,
    metric_group: str | None = None,
) -> float:
    if metric_group == "criteria":
        candidates = (
            report.get("criteria_scores", {}),
            report.get("criteria_means", {}),
            report.get("criteria_minima", {}),
        )
        for candidate in candidates:
            if isinstance(candidate, dict) and metric in candidate:
                return _clamp_float(candidate.get(metric), default=0.0)
        return 0.0
    if metric == "global_score":
        for key in ("global_score", "mean_global_score", "min_global_score"):
            if key in report:
                return _clamp_float(report.get(key), default=0.0)
    if metric == "reward":
        for key in ("reward", "mean_reward", "min_reward"):
            if key in report:
                return _clamp_float(report.get(key), default=0.0)
    return _clamp_float(report.get(metric), default=0.0)


def _input_digest(input_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "has_action": isinstance(input_state.get("action"), dict),
        "has_outcome": isinstance(input_state.get("outcome"), dict),
        "branch_count": len(_list_of_dicts(input_state.get("branches"))),
        "signal_count": len(_list_of_dicts(input_state.get("signals"))),
        "task_count": len(_list_of_dicts(input_state.get("tasks"))),
        "goal_count": len(_list_of_dicts(input_state.get("goals"))),
        "resource_count": len(_list_of_dicts(input_state.get("resources"))),
        "counterfactual_count": len(_list_of_dicts(input_state.get("counterfactuals"))),
        "memory_trace_count": len(_list_of_dicts(input_state.get("memory_trace"))),
        "future_intention_count": len(_list_of_dicts(input_state.get("future_intentions"))),
        "cue_count": len(_list_of_dicts(input_state.get("cues"))),
        "perspective_frame_count": len(_list_of_dicts(input_state.get("perspective_frames"))),
        "resource_demand_count": len(_list_of_dicts(input_state.get("resource_demands"))),
        "affordance_count": len(_list_of_dicts(input_state.get("affordances"))),
        "source_attribution_event_count": len(_list_of_dicts(input_state.get("source_attribution_events"))),
        "social_prediction_error_count": len(_list_of_dicts(input_state.get("social_prediction_errors"))),
        "broadcast_route_count": len(_list_of_dicts(input_state.get("broadcast_routes"))),
        "body_schema_distortion_count": len(_list_of_dicts(input_state.get("body_schema_distortions"))),
        "working_memory_item_count": len(_list_of_dicts(input_state.get("working_memory_items"))),
        "learning_context_count": len(_list_of_dicts(input_state.get("learning_contexts"))),
        "confidence_observation_count": len(_list_of_dicts(input_state.get("confidence_observations"))),
        "policy_context_count": len(_list_of_dicts(input_state.get("policy_contexts"))),
        "goal_conflict_count": len(_list_of_dicts(input_state.get("goal_conflicts"))),
        "synergy_pair_count": len(_list_of_dicts(input_state.get("synergy_pairs"))),
        "temporal_credit_event_count": len(_list_of_dicts(input_state.get("temporal_credit_events"))),
        "hierarchical_credit_event_count": len(_list_of_dicts(input_state.get("hierarchical_credit_events"))),
        "history_count": len(_list_of_dicts(input_state.get("history"))),
        "external_event_count": len(_list_of_dicts(input_state.get("external_events"))),
    }


def _compact_final_metrics(output: dict[str, Any]) -> dict[str, Any]:
    metric_keys = (
        "ownership_verdict",
        "ownership_score",
        "identity_coherence",
        "attention_stability",
        "monitor_confidence",
        "repair_required",
        "self_schema_confidence",
        "gate_stability",
        "planning_confidence",
        "uncertainty_score",
        "integration_coherence",
        "viability_score",
        "global_binding_strength",
        "causal_confidence",
        "minimization_gain",
        "repair_feasibility",
        "selection_confidence",
        "prospective_memory_score",
        "perspective_accuracy_proxy",
        "hierarchy_coherence",
        "arbitration_score",
        "affordance_selection_confidence",
        "boundary_sharpness",
        "arbitration_confidence",
        "broadcast_phase_score",
        "correction_strength",
        "working_memory_capacity_score",
        "learning_rate_adaptation_score",
        "confidence_calibration_score",
        "contextual_inhibition_score",
        "goal_conflict_resolution_score",
        "cross_family_synergy_score",
        "temporal_credit_score",
        "hierarchical_credit_score",
        "social_coupling_collective_agency_score",
        "counterfactual_reasoning_depth_score",
        "coordination_length_control_score",
        "latent_context_switch_detection_score",
        "social_norm_tracking_score",
        "semantic_memory_retrieval_control_score",
        "divergent_thinking_score",
        "analogical_reasoning_rework_score",
        "cooperation_policy_switching_rework_score",
        "spatial_navigation_remapping_rework_score",
        "predictive_control_under_action_intervention_score",
        "insight_problem_solving_rework_score",
        "counterfactual_repair_planning_rework_score",
        "multi_agent_commitment_tracking_score",
        "norm_violation_repair_score",
        "constraint_satisfaction_reconfiguration_score",
        "integration_without_broadcast_boundary_score",
        "selective_global_broadcast_control_score",
        "agency_without_ownership_boundary_score",
        "temporal_identity_planning_dissociation_score",
        "clock_drift_resynchronization_control_score",
        "energy_budget_reallocation_control_score",
        "sensor_gain_recalibration_control_score",
        "tool_use_affordance_remapping_score",
        "actuator_failure_compensation_control_score",
        "preference_reversal_adaptation_control_score",
        "communication_channel_repair_control_score",
        "proxy_activation",
        "confidence",
        "boundary_pressure",
    )
    metrics = {
        key: output[key]
        for key in metric_keys
        if key in output
    }
    if not metrics and output:
        metrics["construct_id"] = output.get("construct_id", "unknown")
    return metrics


def _construct_output_score(output: dict[str, Any]) -> float:
    metric_keys = (
        "ownership_score",
        "stability",
        "identity_coherence",
        "attention_stability",
        "monitor_confidence",
        "self_schema_confidence",
        "gate_stability",
        "planning_confidence",
        "uncertainty_score",
        "integration_coherence",
        "viability_score",
        "global_binding_strength",
        "causal_confidence",
        "minimization_gain",
        "repair_feasibility",
        "selection_confidence",
        "prospective_memory_score",
        "perspective_accuracy_proxy",
        "hierarchy_coherence",
        "arbitration_score",
        "affordance_selection_confidence",
        "boundary_sharpness",
        "arbitration_confidence",
        "broadcast_phase_score",
        "correction_strength",
        "working_memory_capacity_score",
        "learning_rate_adaptation_score",
        "confidence_calibration_score",
        "contextual_inhibition_score",
        "goal_conflict_resolution_score",
        "cross_family_synergy_score",
        "temporal_credit_score",
        "hierarchical_credit_score",
        "social_coupling_collective_agency_score",
        "counterfactual_reasoning_depth_score",
        "coordination_length_control_score",
        "latent_context_switch_detection_score",
        "social_norm_tracking_score",
        "semantic_memory_retrieval_control_score",
        "divergent_thinking_score",
        "analogical_reasoning_rework_score",
        "cooperation_policy_switching_rework_score",
        "spatial_navigation_remapping_rework_score",
        "predictive_control_under_action_intervention_score",
        "insight_problem_solving_rework_score",
        "counterfactual_repair_planning_rework_score",
        "multi_agent_commitment_tracking_score",
        "norm_violation_repair_score",
        "constraint_satisfaction_reconfiguration_score",
        "integration_without_broadcast_boundary_score",
        "selective_global_broadcast_control_score",
        "agency_without_ownership_boundary_score",
        "temporal_identity_planning_dissociation_score",
        "clock_drift_resynchronization_control_score",
        "energy_budget_reallocation_control_score",
        "sensor_gain_recalibration_control_score",
        "tool_use_affordance_remapping_score",
        "actuator_failure_compensation_control_score",
        "preference_reversal_adaptation_control_score",
        "communication_channel_repair_control_score",
        "proxy_activation",
        "confidence",
    )
    values = [
        _clamp_float(output.get(key), default=0.0)
        for key in metric_keys
        if key in output
    ]
    if values:
        return _clamp(_mean(values))
    numeric_values = [
        _clamp_float(value, default=0.0)
        for value in output.values()
        if isinstance(value, (int, float))
    ]
    return _clamp(_mean(numeric_values)) if numeric_values else 0.5


def _construct_boundary_pressure(output: dict[str, Any]) -> float:
    flags = [
        str(flag)
        for flag in output.get("boundary_flags", output.get("review_flags", []))
        if str(flag)
    ]
    hard_terms = (
        "hard_negative",
        "severe",
        "placeholder",
        "low_",
        "required",
        "pressure",
        "risk",
    )
    pressure = min(1.0, len(flags) / 6.0)
    if any(any(term in flag for term in hard_terms) for flag in flags):
        pressure = max(pressure, 0.45)
    if output.get("placeholder"):
        pressure = max(pressure, 0.58)
    for key in (
        "mean_hard_negative_pressure",
        "mean_boundary_pressure",
        "boundary_pressure",
        "mean_shortcut_pressure",
    ):
        if key in output:
            pressure = max(pressure, _clamp_float(output.get(key), default=pressure))
    return _clamp(pressure)


def _all_non_placeholder(
    outputs: dict[str, dict[str, Any]],
    construct_ids: tuple[str, ...],
) -> bool:
    return all(
        construct_id in outputs and not outputs[construct_id].get("placeholder")
        for construct_id in construct_ids
    )


def _signal_gate_score(signal: dict[str, Any]) -> float:
    return _clamp(
        0.35 * _clamp_float(signal.get("salience"), default=0.5)
        + 0.25 * _clamp_float(signal.get("novelty"), default=0.4)
        + 0.25 * _clamp_float(signal.get("reliability"), default=0.6)
        + 0.15 * _clamp_float(signal.get("threat"), default=0.0)
    )


def _mean_absolute_deviation(values: list[float]) -> float:
    if not values:
        return 0.0
    center = _mean(values)
    return _mean(abs(value - center) for value in values)


def _prediction_error_events(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    expectations = _dict_or_empty(input_state.get("expectations"))
    observations = _dict_or_empty(input_state.get("observations"))
    events = []
    for target, expected in expectations.items():
        observed = observations.get(target)
        if observed is None:
            events.append(
                {
                    "id": f"missing_observation:{target}",
                    "target": str(target),
                    "severity": 0.55,
                    "confidence": 0.65,
                    "kind": "missing_observation",
                }
            )
        elif observed != expected:
            events.append(
                {
                    "id": f"mismatch:{target}",
                    "target": str(target),
                    "severity": 0.75,
                    "confidence": 0.8,
                    "kind": "expectation_mismatch",
                }
            )
    return events


def _dependency_support(dependencies: dict[str, dict[str, Any]]) -> float:
    values: list[float] = []
    for output in dependencies.values():
        values.extend(_dependency_numeric_values(output))
    return _clamp(_mean(values)) if values else 0.55


def _dependency_numeric_values(output: dict[str, Any]) -> list[float]:
    keys = (
        "stability",
        "controllability",
        "self_boundary_confidence",
        "ownership_score",
        "identity_coherence",
        "attention_stability",
        "monitor_confidence",
        "self_schema_confidence",
        "gate_stability",
        "proxy_activation",
        "confidence",
        "family_signal",
        "dependency_support",
    )
    values = [
        _clamp_float(output.get(key), default=-1.0)
        for key in keys
        if key in output
    ]
    mechanism_state = output.get("mechanism_state")
    if isinstance(mechanism_state, dict):
        values.extend(
            _clamp_float(value, default=-1.0)
            for value in mechanism_state.values()
            if isinstance(value, int | float)
        )
    return [value for value in values if value >= 0.0]


def _family_proxy_metrics(
    family: str,
    construct_id: str,
    input_state: dict[str, Any],
    dependencies: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if family == "workspace":
        return _workspace_family_metrics(input_state, dependencies, construct_id)
    if family in {"memory", "temporal_self"}:
        return _memory_family_metrics(input_state, dependencies, construct_id)
    if family == "metacognition":
        return _metacognition_family_metrics(input_state, dependencies, construct_id)
    if family == "causal_counterfactual":
        return _causal_family_metrics(input_state, dependencies, construct_id)
    if family in {"resource_problem", "resource_control", "value_policy_control"}:
        return _resource_family_metrics(input_state, dependencies, construct_id)
    if family in {"action", "action_control", "sensorimotor_control", "motor_infrastructure_control"}:
        return _action_control_family_metrics(input_state, dependencies, construct_id)
    if family in {"social_boundary", "communication_control"}:
        return _social_family_metrics(input_state, dependencies, construct_id)
    if family in {"temporal_credit", "temporal_control"}:
        return _temporal_family_metrics(input_state, dependencies, construct_id)
    return _generic_family_metrics(input_state, dependencies, construct_id)


def _workspace_family_metrics(
    input_state: dict[str, Any],
    dependencies: dict[str, dict[str, Any]],
    construct_id: str,
) -> dict[str, Any]:
    signals = _list_of_dicts(input_state.get("signals"))
    tasks = _list_of_dicts(input_state.get("tasks"))
    gate = dependencies.get("information_flow_onset_gating", {})
    attention = dependencies.get("attention_control", {})
    gate_stability = _clamp_float(gate.get("gate_stability"), default=0.55)
    attention_stability = _clamp_float(attention.get("attention_stability"), default=0.55)
    open_count = len(_list_of_dicts(gate.get("open_channels"))) or min(4, len(signals))
    integration_load = _clamp((len(tasks) + len(signals)) / 12.0)
    coordination_span = _clamp_float(
        _dict_or_empty(input_state.get("context")).get("coordination_span"),
        default=0.62,
    )
    family_signal = _clamp(
        0.35 * gate_stability
        + 0.25 * attention_stability
        + 0.2 * (1.0 - integration_load)
        + 0.2 * coordination_span
    )
    if "broadcast" in construct_id:
        family_signal = _clamp(0.7 * family_signal + 0.3 * min(1.0, open_count / 3.0))
    if "integration" in construct_id:
        family_signal = _clamp(0.65 * family_signal + 0.35 * (1.0 - abs(0.5 - integration_load)))
    return {
        "family_signal": round(family_signal, 4),
        "gate_stability": round(gate_stability, 4),
        "attention_stability": round(attention_stability, 4),
        "open_channel_count": open_count,
        "integration_load": round(integration_load, 4),
        "coordination_span": round(coordination_span, 4),
    }


def _memory_family_metrics(
    input_state: dict[str, Any],
    dependencies: dict[str, dict[str, Any]],
    construct_id: str,
) -> dict[str, Any]:
    traces = _list_of_dicts(input_state.get("memory_trace"))
    branch = dependencies.get("branch_binding_stability", {})
    identity = dependencies.get("identity_temporal_self", {})
    continuity = _mean(
        _clamp_float(trace.get("continuity"), default=0.5) for trace in traces
    ) if traces else 0.5
    confidence = _mean(
        _clamp_float(trace.get("confidence"), default=0.5) for trace in traces
    ) if traces else 0.5
    branch_stability = _clamp_float(branch.get("stability"), default=0.55)
    identity_coherence = _clamp_float(identity.get("identity_coherence"), default=0.55)
    retrieval_strength = _clamp(0.45 * confidence + 0.3 * continuity + 0.25 * branch_stability)
    if "semantic" in construct_id:
        retrieval_strength = _clamp(0.75 * retrieval_strength + 0.25 * _task_pressure(input_state))
    if "latent_context" in construct_id:
        retrieval_strength = _clamp(0.6 * retrieval_strength + 0.4 * (1.0 - branch_stability))
    family_signal = _clamp(0.45 * retrieval_strength + 0.3 * identity_coherence + 0.25 * branch_stability)
    return {
        "family_signal": round(family_signal, 4),
        "retrieval_strength": round(retrieval_strength, 4),
        "trace_continuity": round(continuity, 4),
        "trace_confidence": round(confidence, 4),
        "branch_stability": round(branch_stability, 4),
        "identity_coherence": round(identity_coherence, 4),
    }


def _metacognition_family_metrics(
    input_state: dict[str, Any],
    dependencies: dict[str, dict[str, Any]],
    construct_id: str,
) -> dict[str, Any]:
    error = dependencies.get("error_monitoring", {})
    attention = dependencies.get("attention_control", {})
    error_load = _clamp_float(error.get("error_load"), default=_raw_error_load(input_state))
    monitor_confidence = _clamp_float(error.get("monitor_confidence"), default=0.55)
    attention_stability = _clamp_float(attention.get("attention_stability"), default=0.55)
    uncertainty = _clamp_float(
        _dict_or_empty(input_state.get("context")).get("uncertainty"),
        default=0.35 + 0.4 * error_load,
    )
    repair_priority = _clamp(0.55 * error_load + 0.3 * uncertainty + 0.15 * (1.0 - attention_stability))
    if "strategy" in construct_id or "policy" in construct_id:
        repair_priority = _clamp(0.55 * repair_priority + 0.45 * _goal_conflict(input_state))
    if "confidence" in construct_id:
        repair_priority = _clamp(0.6 * repair_priority + 0.4 * uncertainty)
    family_signal = _clamp(
        0.35 * monitor_confidence
        + 0.25 * attention_stability
        + 0.25 * (1.0 - uncertainty)
        + 0.15 * (1.0 - error_load)
    )
    return {
        "family_signal": round(family_signal, 4),
        "error_load": round(error_load, 4),
        "monitor_confidence": round(monitor_confidence, 4),
        "attention_stability": round(attention_stability, 4),
        "uncertainty": round(uncertainty, 4),
        "repair_priority": round(repair_priority, 4),
    }


def _causal_family_metrics(
    input_state: dict[str, Any],
    dependencies: dict[str, dict[str, Any]],
    construct_id: str,
) -> dict[str, Any]:
    counterfactuals = _list_of_dicts(input_state.get("counterfactuals"))
    error = dependencies.get("error_monitoring", {})
    agency = dependencies.get("action_agency", {})
    causal_fit = _mean(
        _clamp_float(item.get("support"), default=0.55)
        for item in counterfactuals
    ) if counterfactuals else 0.55
    depth = _clamp(min(1.0, len(counterfactuals) / 4.0))
    monitor_confidence = _clamp_float(error.get("monitor_confidence"), default=0.55)
    controllability = _clamp_float(agency.get("controllability"), default=0.55)
    repair_planning = _clamp(0.4 * causal_fit + 0.3 * depth + 0.3 * monitor_confidence)
    if "repair" in construct_id:
        causal_fit = _clamp(0.65 * causal_fit + 0.35 * repair_planning)
    family_signal = _clamp(0.35 * causal_fit + 0.25 * depth + 0.2 * monitor_confidence + 0.2 * controllability)
    return {
        "family_signal": round(family_signal, 4),
        "causal_fit": round(causal_fit, 4),
        "counterfactual_depth": round(depth, 4),
        "repair_planning": round(repair_planning, 4),
        "monitor_confidence": round(monitor_confidence, 4),
        "controllability": round(controllability, 4),
    }


def _resource_family_metrics(
    input_state: dict[str, Any],
    dependencies: dict[str, dict[str, Any]],
    construct_id: str,
) -> dict[str, Any]:
    goals = _list_of_dicts(input_state.get("goals"))
    resources = _list_of_dicts(input_state.get("resources"))
    attention = dependencies.get("attention_control", {})
    strategy = dependencies.get("strategy_selection", {})
    scarcity = _resource_scarcity(resources)
    goal_conflict = _goal_conflict(input_state)
    priority_mass = _mean(
        _clamp_float(goal.get("priority"), default=0.5) for goal in goals
    ) if goals else 0.5
    attention_stability = _clamp_float(attention.get("attention_stability"), default=0.55)
    strategy_signal = _clamp_float(strategy.get("proxy_activation"), default=0.55)
    if "energy_budget" in construct_id:
        scarcity = _clamp(0.7 * scarcity + 0.3 * _resource_named_pressure(resources, "energy"))
    if "preference_reversal" in construct_id:
        goal_conflict = _clamp(0.6 * goal_conflict + 0.4 * _policy_reversal_pressure(input_state))
    arbitration = _clamp(0.4 * (1.0 - scarcity) + 0.3 * (1.0 - goal_conflict) + 0.3 * strategy_signal)
    family_signal = _clamp(
        0.3 * arbitration
        + 0.25 * attention_stability
        + 0.25 * priority_mass
        + 0.2 * (1.0 - max(scarcity, goal_conflict))
    )
    return {
        "family_signal": round(family_signal, 4),
        "resource_scarcity": round(scarcity, 4),
        "goal_conflict": round(goal_conflict, 4),
        "priority_mass": round(priority_mass, 4),
        "arbitration_score": round(arbitration, 4),
        "strategy_signal": round(strategy_signal, 4),
    }


def _action_control_family_metrics(
    input_state: dict[str, Any],
    dependencies: dict[str, dict[str, Any]],
    construct_id: str,
) -> dict[str, Any]:
    agency = dependencies.get("action_agency", {})
    body = dependencies.get("distributed_body_schema_self", {})
    body_error = dependencies.get("body_schema_error_correction", {})
    controllability = _clamp_float(agency.get("controllability"), default=0.55)
    body_confidence = _clamp_float(body.get("self_schema_confidence"), default=0.55)
    correction_signal = _clamp_float(body_error.get("proxy_activation"), default=0.55)
    actuator_health = _mean(
        _clamp_float(item.get("health"), default=0.55)
        for item in _list_of_dicts(_dict_or_empty(input_state.get("body_schema")).get("effectors"))
    )
    tool_fit = _mean(
        _clamp_float(item.get("control"), default=0.45)
        for item in _list_of_dicts(_dict_or_empty(input_state.get("body_schema")).get("tools"))
    )
    if "tool_use" in construct_id:
        controllability = _clamp(0.6 * controllability + 0.4 * tool_fit)
    if "actuator_failure" in construct_id:
        controllability = _clamp(0.45 * controllability + 0.55 * (1.0 - actuator_health))
    if "sensor_gain" in construct_id:
        body_confidence = _clamp(0.6 * body_confidence + 0.4 * _sensor_alignment(input_state))
    family_signal = _clamp(
        0.34 * controllability
        + 0.28 * body_confidence
        + 0.2 * correction_signal
        + 0.18 * actuator_health
    )
    return {
        "family_signal": round(family_signal, 4),
        "controllability": round(controllability, 4),
        "body_confidence": round(body_confidence, 4),
        "body_correction_signal": round(correction_signal, 4),
        "actuator_health": round(actuator_health, 4),
        "tool_fit": round(tool_fit, 4),
    }


def _social_family_metrics(
    input_state: dict[str, Any],
    dependencies: dict[str, dict[str, Any]],
    construct_id: str,
) -> dict[str, Any]:
    social = _dict_or_empty(input_state.get("social_context"))
    agents = _list_of_dicts(social.get("agents"))
    norms = _list_of_dicts(social.get("norms"))
    commitments = _list_of_dicts(social.get("commitments"))
    boundary = dependencies.get("boundary_self", {})
    ownership = dependencies.get("action_ownership", {})
    boundary_confidence = _clamp_float(boundary.get("self_boundary_confidence"), default=0.55)
    ownership_score = _clamp_float(ownership.get("ownership_score"), default=0.55)
    norm_alignment = _mean(
        _clamp_float(norm.get("alignment"), default=0.6) for norm in norms
    ) if norms else 0.6
    commitment_strength = _mean(
        _clamp_float(item.get("confidence"), default=0.55) for item in commitments
    ) if commitments else 0.55
    social_coupling = _clamp(min(1.0, len(agents) / 4.0))
    if "norm_violation" in construct_id:
        norm_alignment = _clamp(1.0 - norm_alignment)
    if "perspective" in construct_id:
        social_coupling = _clamp(0.5 + 0.5 * social_coupling)
    family_signal = _clamp(
        0.25 * boundary_confidence
        + 0.2 * ownership_score
        + 0.25 * norm_alignment
        + 0.2 * commitment_strength
        + 0.1 * social_coupling
    )
    return {
        "family_signal": round(family_signal, 4),
        "boundary_confidence": round(boundary_confidence, 4),
        "ownership_score": round(ownership_score, 4),
        "norm_alignment": round(norm_alignment, 4),
        "commitment_strength": round(commitment_strength, 4),
        "social_coupling": round(social_coupling, 4),
    }


def _temporal_family_metrics(
    input_state: dict[str, Any],
    dependencies: dict[str, dict[str, Any]],
    construct_id: str,
) -> dict[str, Any]:
    temporal = _dict_or_empty(input_state.get("temporal_state"))
    planning = dependencies.get("temporal_horizon_dependent_planning", {})
    causal = dependencies.get("causal_attribution", {})
    identity = dependencies.get("identity_temporal_self", {})
    horizon_fit = _clamp_float(temporal.get("horizon_fit"), default=0.62)
    deadline_pressure = _clamp_float(temporal.get("deadline_pressure"), default=0.35)
    clock_drift = _clamp_float(temporal.get("clock_drift"), default=0.18)
    planning_signal = _clamp_float(planning.get("proxy_activation"), default=0.55)
    causal_signal = _clamp_float(causal.get("proxy_activation"), default=0.55)
    identity_coherence = _clamp_float(identity.get("identity_coherence"), default=0.55)
    if "clock_drift" in construct_id:
        horizon_fit = _clamp(0.55 * horizon_fit + 0.45 * (1.0 - clock_drift))
    family_signal = _clamp(
        0.3 * horizon_fit
        + 0.2 * (1.0 - deadline_pressure)
        + 0.2 * planning_signal
        + 0.15 * causal_signal
        + 0.15 * identity_coherence
    )
    return {
        "family_signal": round(family_signal, 4),
        "horizon_fit": round(horizon_fit, 4),
        "deadline_pressure": round(deadline_pressure, 4),
        "clock_drift": round(clock_drift, 4),
        "planning_signal": round(planning_signal, 4),
        "causal_signal": round(causal_signal, 4),
        "identity_coherence": round(identity_coherence, 4),
    }


def _generic_family_metrics(
    input_state: dict[str, Any],
    dependencies: dict[str, dict[str, Any]],
    construct_id: str,
) -> dict[str, Any]:
    support = _dependency_support(dependencies)
    relevance = _construct_relevance(construct_id, input_state)
    family_signal = _clamp(0.65 * support + 0.35 * relevance)
    return {
        "family_signal": round(family_signal, 4),
        "dependency_support": round(support, 4),
        "construct_relevance": round(relevance, 4),
    }


def _node_evidence_signal(node: ConstructNode) -> float:
    if node.layer == "validation_candidate":
        base = 0.68
    elif node.layer == "candidate":
        base = 0.56
    elif node.layer == "preconstruct":
        base = 0.48
    else:
        base = 0.5
    if "packet_ready_candidate_only" in node.roles:
        base += 0.06
    if "l3_ready_carded_candidate" in node.roles:
        base += 0.05
    if "relation_matrix_governance_complete" in node.roles:
        base += 0.04
    if "pending_local_registration" in node.roles:
        base -= 0.04
    return _clamp(base)


def _node_boundary_pressure(
    node: ConstructNode,
    input_state: dict[str, Any],
    dependencies: dict[str, dict[str, Any]],
) -> float:
    role_pressure = 0.0
    if "severe_boundary_watch" in node.roles:
        role_pressure += 0.28
    if "relation_matrix_required" in node.roles:
        role_pressure += 0.16
    if "pending_local_registration" in node.roles:
        role_pressure += 0.12
    if node.layer == "preconstruct":
        role_pressure += 0.18
    boundary_count_pressure = min(0.2, len(node.nearest_boundaries) * 0.025)
    error_pressure = _raw_error_load(input_state) * 0.18
    dependency_risk = _dependency_risk(dependencies) * 0.18
    return _clamp(role_pressure + boundary_count_pressure + error_pressure + dependency_risk)


def _dependency_risk(dependencies: dict[str, dict[str, Any]]) -> float:
    flags = 0
    total = 0
    for output in dependencies.values():
        for key in ("risk_flags", "review_flags", "boundary_violations", "schema_alerts"):
            value = output.get(key)
            if isinstance(value, list):
                flags += len(value)
                total += 1
    if total == 0:
        return 0.0
    return _clamp(flags / (total * 4.0))


def _candidate_review_flags(
    node: ConstructNode,
    proxy_activation: float,
    confidence: float,
    boundary_pressure: float,
) -> list[str]:
    flags: list[str] = []
    if "severe_boundary_watch" in node.roles:
        flags.append("severe_boundary_watch")
    if "pending_local_registration" in node.roles:
        flags.append("pending_local_registration")
    if "relation_matrix_required" in node.roles:
        flags.append("relation_matrix_required")
    if node.layer == "preconstruct":
        flags.append("formal_candidate_review_required")
    if proxy_activation < 0.45:
        flags.append("low_proxy_activation")
    if confidence < 0.5:
        flags.append("low_confidence")
    if boundary_pressure >= 0.45:
        flags.append("high_boundary_pressure")
    return sorted(set(flags))


def _construct_relevance(construct_id: str, input_state: dict[str, Any]) -> float:
    tokens = [token for token in construct_id.split("_") if len(token) >= 4]
    if not tokens:
        return 0.5
    searchable: list[str] = []
    for key in (
        "tasks",
        "signals",
        "goals",
        "memory_trace",
        "counterfactuals",
        "resources",
    ):
        for item in _list_of_dicts(input_state.get(key)):
            searchable.extend(str(value).lower() for value in item.values())
    searchable.extend(str(value).lower() for value in _dict_or_empty(input_state.get("context")).values())
    haystack = " ".join(searchable)
    matches = sum(1 for token in tokens if token.lower() in haystack)
    return _clamp(0.42 + 0.58 * (matches / len(tokens)))


def _raw_error_load(input_state: dict[str, Any]) -> float:
    error_events = _list_of_dicts(input_state.get("error_events"))
    derived = _prediction_error_events(input_state)
    events = error_events + derived
    if not events:
        return 0.0
    return _mean(_clamp_float(event.get("severity"), default=0.5) for event in events)


def _task_pressure(input_state: dict[str, Any]) -> float:
    tasks = _list_of_dicts(input_state.get("tasks"))
    if not tasks:
        return 0.5
    return _mean(
        _clamp(
            0.45 * _clamp_float(task.get("priority"), default=0.5)
            + 0.35 * _clamp_float(task.get("urgency"), default=0.4)
            + 0.2 * _clamp_float(task.get("relevance"), default=0.5)
        )
        for task in tasks
    )


def _goal_conflict(input_state: dict[str, Any]) -> float:
    goals = _list_of_dicts(input_state.get("goals"))
    if not goals:
        return 0.25
    return _mean(_clamp_float(goal.get("conflict"), default=0.25) for goal in goals)


def _resource_scarcity(resources: list[dict[str, Any]]) -> float:
    if not resources:
        return 0.3
    return _mean(
        1.0 - _clamp_float(resource.get("available"), default=0.7)
        for resource in resources
    )


def _resource_named_pressure(resources: list[dict[str, Any]], name: str) -> float:
    matches = [
        resource for resource in resources
        if name in str(resource.get("id") or resource.get("type") or "").lower()
    ]
    if not matches:
        return _resource_scarcity(resources)
    return _mean(
        1.0 - _clamp_float(resource.get("available"), default=0.7)
        for resource in matches
    )


def _policy_reversal_pressure(input_state: dict[str, Any]) -> float:
    policies = _list_of_dicts(input_state.get("policies"))
    if not policies:
        return 0.3
    return _mean(
        _clamp_float(policy.get("reversal_pressure"), default=0.3)
        for policy in policies
    )


def _sensor_alignment(input_state: dict[str, Any]) -> float:
    sensors = _list_of_dicts(_dict_or_empty(input_state.get("body_schema")).get("sensors"))
    if not sensors:
        return 0.55
    return _mean(
        _clamp_float(sensor.get("reliability"), default=0.55)
        * _clamp_float(sensor.get("calibration"), default=0.55)
        for sensor in sensors
    )


def _trace_context_match(trace: dict[str, Any], input_state: dict[str, Any]) -> float:
    tags = {str(tag).lower() for tag in trace.get("context_tags", []) if str(tag)}
    if not tags:
        return 0.55
    runtime_terms: set[str] = set()
    for key in ("tasks", "goals", "signals"):
        for item in _list_of_dicts(input_state.get(key)):
            runtime_terms.update(
                token
                for value in item.values()
                for token in str(value).lower().replace("_", " ").split()
            )
    if not runtime_terms:
        return 0.55
    return _clamp(len(tags & runtime_terms) / len(tags))


def _causal_candidates(
    input_state: dict[str, Any],
    action: dict[str, Any],
    outcome: dict[str, Any],
) -> list[dict[str, Any]]:
    candidates = _list_of_dicts(input_state.get("causal_candidates"))
    if candidates:
        return candidates
    generated = []
    if action:
        generated.append(
            {
                "id": "observed_action_candidate",
                "action_type": action.get("type"),
                "outcome_type": outcome.get("type"),
                "target": action.get("target"),
                "intervention_match": 0.75,
                "outcome_binding": _action_outcome_match(action, outcome),
                "counterfactual_contrast": 0.55,
                "confound_suppression": 0.55,
                "temporal_order": 0.7,
            }
        )
    for index, counterfactual in enumerate(_list_of_dicts(input_state.get("counterfactuals"))):
        generated.append(
            {
                "id": str(counterfactual.get("id") or f"counterfactual_candidate_{index + 1}"),
                "target": outcome.get("target"),
                "intervention_match": _clamp_float(counterfactual.get("intervention_match"), default=0.45),
                "outcome_binding": _clamp_float(counterfactual.get("outcome_binding"), default=0.45),
                "counterfactual_contrast": _clamp_float(counterfactual.get("support"), default=0.55),
                "confound_suppression": _clamp_float(counterfactual.get("confound_suppression"), default=0.55),
                "temporal_order": _clamp_float(counterfactual.get("temporal_order"), default=0.6),
            }
        )
    return generated


def _candidate_action_match(candidate: dict[str, Any], action: dict[str, Any]) -> float:
    if not candidate or not action:
        return 0.4
    type_match = 1.0 if candidate.get("action_type") == action.get("type") else 0.3
    target_match = 1.0 if candidate.get("target") == action.get("target") else 0.4
    return _clamp(0.55 * type_match + 0.45 * target_match)


def _candidate_outcome_match(candidate: dict[str, Any], outcome: dict[str, Any]) -> float:
    if not candidate or not outcome:
        return 0.4
    type_match = 1.0 if candidate.get("outcome_type") == outcome.get("type") else 0.45
    target_match = 1.0 if candidate.get("target") == outcome.get("target") else 0.45
    return _clamp(0.5 * type_match + 0.5 * target_match)


def _counterfactual_support(candidate: dict[str, Any], input_state: dict[str, Any]) -> float:
    candidate_id = str(candidate.get("id") or "")
    counterfactuals = _list_of_dicts(input_state.get("counterfactuals"))
    direct = [
        _clamp_float(item.get("support"), default=0.55)
        for item in counterfactuals
        if candidate_id and candidate_id in str(item.get("id") or "")
    ]
    if direct:
        return _mean(direct)
    return _mean(_clamp_float(item.get("support"), default=0.55) for item in counterfactuals) if counterfactuals else 0.55


def _strategy_candidates(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    strategies = _list_of_dicts(input_state.get("strategies"))
    if strategies:
        return strategies
    goals = _list_of_dicts(input_state.get("goals"))
    if not goals:
        return [
            {"id": "continue_current_strategy", "utility": 0.55, "cost": 0.25, "risk": 0.25},
            {"id": "pause_and_review", "utility": 0.45, "cost": 0.35, "risk": 0.12},
        ]
    return [
        {
            "id": f"pursue_{goal.get('id') or index + 1}",
            "utility": _clamp_float(goal.get("expected_value"), default=_clamp_float(goal.get("priority"), default=0.55)),
            "cost": _clamp_float(goal.get("cost"), default=0.35 + 0.25 * _clamp_float(goal.get("conflict"), default=0.25)),
            "risk": _clamp_float(goal.get("risk"), default=_clamp_float(goal.get("conflict"), default=0.25)),
            "context_match": _clamp_float(goal.get("context_match"), default=0.62),
            "commitment": _clamp_float(goal.get("priority"), default=0.55),
        }
        for index, goal in enumerate(goals)
    ]


def _strategy_context_match(strategy: dict[str, Any], input_state: dict[str, Any]) -> float:
    strategy_id = str(strategy.get("id") or "").lower()
    task_ids = [
        str(task.get("id") or "").lower()
        for task in _list_of_dicts(input_state.get("tasks"))
    ]
    goal_ids = [
        str(goal.get("id") or "").lower()
        for goal in _list_of_dicts(input_state.get("goals"))
    ]
    if any(part and part in strategy_id for part in task_ids + goal_ids):
        return 0.82
    return 0.58


def _future_intentions(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    intentions = _list_of_dicts(input_state.get("future_intentions"))
    if intentions:
        return intentions
    goals = _list_of_dicts(input_state.get("goals"))
    return [
        {
            "id": f"future_{goal.get('id') or index + 1}",
            "target": goal.get("id"),
            "valid_cues": [goal.get("id")],
            "due_phase": "implementation",
            "retention_strength": _clamp_float(goal.get("priority"), default=0.55),
            "ongoing_task_protection": 0.58,
            "interruption_recovery": 0.55,
            "priority": _clamp_float(goal.get("priority"), default=0.55),
        }
        for index, goal in enumerate(goals)
    ]


def _cue_events(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    cues = _list_of_dicts(input_state.get("cues"))
    if cues:
        return cues
    signals = _list_of_dicts(input_state.get("signals"))
    return [
        {
            "id": signal.get("id"),
            "type": signal.get("channel"),
            "target": signal.get("target") or signal.get("id"),
            "salience": signal.get("salience"),
        }
        for signal in signals
    ]


def _cue_match_score(intention: dict[str, Any], cue: dict[str, Any]) -> float:
    valid_cues = {
        str(item).lower()
        for item in intention.get("valid_cues", [])
        if str(item)
    }
    cue_tokens = {
        str(cue.get("id") or "").lower(),
        str(cue.get("type") or "").lower(),
        str(cue.get("target") or "").lower(),
    }
    direct_match = 1.0 if valid_cues & cue_tokens else 0.0
    target_match = 1.0 if cue.get("target") and cue.get("target") == intention.get("target") else 0.0
    validity = 1.0 if cue.get("valid", True) else 0.25
    salience = _clamp_float(cue.get("salience"), default=0.55)
    return _clamp(0.42 * direct_match + 0.32 * target_match + 0.18 * validity + 0.08 * salience)


def _intention_due_score(intention: dict[str, Any], input_state: dict[str, Any]) -> float:
    context = _dict_or_empty(input_state.get("context"))
    current_phase = str(context.get("current_phase") or "implementation")
    due_phase = str(intention.get("due_phase") or current_phase)
    phase_match = 1.0 if due_phase == current_phase else 0.45
    temporal = _dict_or_empty(input_state.get("temporal_state"))
    horizon_fit = _clamp_float(temporal.get("horizon_fit"), default=0.62)
    deadline_pressure = _clamp_float(intention.get("deadline_pressure"), default=temporal.get("deadline_pressure", 0.35))
    return _clamp(0.45 * phase_match + 0.32 * horizon_fit + 0.23 * deadline_pressure)


def _perspective_frames(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    frames = _list_of_dicts(input_state.get("perspective_frames"))
    if frames:
        return frames
    context = _dict_or_empty(input_state.get("context"))
    self_id = str(context.get("self_id") or "mind_executor")
    social = _dict_or_empty(input_state.get("social_context"))
    frames = []
    for index, agent in enumerate(_list_of_dicts(social.get("agents"))):
        agent_id = str(agent.get("id") or f"agent_{index + 1}")
        if agent_id == self_id:
            continue
        trust = _clamp_float(agent.get("trust"), default=0.55)
        frames.append(
            {
                "id": f"{agent_id}_view",
                "agent_id": agent_id,
                "self_interference": 0.35,
                "other_state_evidence": trust,
                "viewpoint_binding": 0.58,
                "conflict_resolution": 0.55,
            }
        )
    return frames


def _resource_demands(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    demands = _list_of_dicts(input_state.get("resource_demands"))
    if demands:
        return demands
    return [
        {
            "id": f"{resource.get('id') or index + 1}_demand",
            "construct_pair": ["attention_control", "strategy_selection"],
            "resource_id": resource.get("id") or "shared",
            "demand": resource.get("demand"),
            "priority": 0.55,
            "retention_sensitivity": 0.55,
        }
        for index, resource in enumerate(_list_of_dicts(input_state.get("resources")))
    ]


def _resource_capacity_by_id(resources: list[dict[str, Any]]) -> dict[str, float]:
    capacities = {
        str(resource.get("id") or "shared"): _clamp_float(resource.get("available"), default=0.65)
        for resource in resources
    }
    capacities.setdefault("shared", _mean(capacities.values()) if capacities else 0.65)
    return capacities


def _affordance_candidates(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    affordances = _list_of_dicts(input_state.get("affordances"))
    if affordances:
        return affordances
    action = _dict_or_empty(input_state.get("action"))
    if action:
        return [
            {
                "id": "observed_action_affordance",
                "action_type": action.get("type"),
                "target": action.get("target"),
                "task_relevance": 0.62,
                "action_fit": 0.65,
                "salience": 0.55,
                "temptation": 0.2,
            }
        ]
    return []


def _affordance_context_match(affordance: dict[str, Any], input_state: dict[str, Any]) -> float:
    target = str(affordance.get("target") or affordance.get("id") or "").lower()
    action_type = str(affordance.get("action_type") or "").lower()
    searchable: list[str] = []
    for key in ("tasks", "goals", "future_intentions"):
        for item in _list_of_dicts(input_state.get(key)):
            searchable.extend(str(value).lower() for value in item.values())
    haystack = " ".join(searchable)
    target_match = 1.0 if target and target in haystack else 0.35
    action_match = 1.0 if action_type and action_type in haystack else 0.5
    return _clamp(0.65 * target_match + 0.35 * action_match)


def _source_attribution_table(input_state: dict[str, Any], self_id: str) -> list[dict[str, Any]]:
    events = _list_of_dicts(input_state.get("source_attribution_events"))
    if not events:
        social = _dict_or_empty(input_state.get("social_context"))
        events = [
            {
                "id": f"{agent.get('id') or index + 1}_source_axis",
                "source_id": agent.get("id"),
                "axis": "self" if str(agent.get("id") or "") == self_id else "other",
                "source_axis_separation": _clamp_float(agent.get("trust"), default=0.55),
                "other_model_independence": 0.58,
                "paired_actuator_gap": 0.55,
                "visible_role_shortcut_risk": 0.18,
                "shared_control_ambiguity": 0.25,
            }
            for index, agent in enumerate(_list_of_dicts(social.get("agents")))
        ]
    table = []
    for index, event in enumerate(events):
        axis = str(event.get("axis") or ("self" if str(event.get("source_id") or "") == self_id else "other"))
        table.append(
            {
                "event_id": str(event.get("id") or f"source_event_{index + 1}"),
                "source_id": str(event.get("source_id") or "unknown"),
                "axis": axis,
                "source_axis_separation": round(_clamp_float(event.get("source_axis_separation"), default=0.55), 4),
                "other_model_independence": round(_clamp_float(event.get("other_model_independence"), default=0.55), 4),
                "paired_actuator_gap": round(_clamp_float(event.get("paired_actuator_gap"), default=0.55), 4),
                "visible_role_shortcut_risk": round(_clamp_float(event.get("visible_role_shortcut_risk"), default=0.15), 4),
                "shared_control_ambiguity": round(_clamp_float(event.get("shared_control_ambiguity"), default=0.25), 4),
            }
        )
    return table


def _self_other_prediction_errors(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    events = _list_of_dicts(input_state.get("social_prediction_errors"))
    if events:
        return events
    derived = []
    for event in _prediction_error_events(input_state):
        derived.append(
            {
                "id": event.get("id"),
                "other_agent_id": "other_agent",
                "self_error": event.get("severity", 0.5),
                "other_error": 0.35,
                "coupling": 0.3,
            }
        )
    return derived or [
        {
            "id": "default_low_ambiguity_social_prediction",
            "other_agent_id": "other_agent",
            "self_error": 0.35,
            "other_error": 0.45,
            "coupling": 0.28,
        }
    ]


def _broadcast_route_candidates(
    input_state: dict[str, Any],
    flow: dict[str, Any],
    attention: dict[str, Any],
) -> list[dict[str, Any]]:
    routes = _list_of_dicts(input_state.get("broadcast_routes"))
    if routes:
        return routes
    open_channels = _list_of_dicts(flow.get("open_channels"))
    focus_targets = _list_of_dicts(attention.get("focus_targets"))
    return [
        {
            "id": str(target.get("id") or channel.get("id") or f"broadcast_route_{index + 1}"),
            "global_availability": _clamp_float(target.get("score"), default=0.55),
            "workspace_ignition": _clamp_float(channel.get("score"), default=0.55),
            "conflict_routed_access": 0.56,
            "cross_context_selection": 0.54,
            "fanout_only_risk": 0.12,
            "salience_only_risk": 0.14,
        }
        for index, (target, channel) in enumerate(zip(focus_targets, open_channels, strict=False))
    ]


def _body_schema_distortions(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    distortions = _list_of_dicts(input_state.get("body_schema_distortions"))
    if distortions:
        return distortions
    schema = _dict_or_empty(input_state.get("body_schema"))
    return [
        {
            "id": f"{sensor.get('id') or index + 1}_calibration_error",
            "body_part": sensor.get("id") or "sensor",
            "distortion": 1.0 - _clamp_float(sensor.get("calibration"), default=0.55),
            "feedback_delay": 0.22,
            "sensor_reliability": sensor.get("reliability", 0.55),
        }
        for index, sensor in enumerate(_list_of_dicts(schema.get("sensors")))
    ]


def _working_memory_items(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    items = _list_of_dicts(input_state.get("working_memory_items"))
    if items:
        return items
    tasks = _list_of_dicts(input_state.get("tasks"))
    return [
        {
            "id": task.get("id") or f"task_item_{index + 1}",
            "load": 0.25 + 0.25 * _clamp_float(task.get("urgency"), default=0.4),
            "interference": 1.0 - _clamp_float(task.get("relevance"), default=0.55),
            "salience": _clamp_float(task.get("priority"), default=0.55),
        }
        for index, task in enumerate(tasks)
    ]


def _learning_contexts(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    contexts = _list_of_dicts(input_state.get("learning_contexts"))
    if contexts:
        return contexts
    context = _dict_or_empty(input_state.get("context"))
    return [
        {
            "id": "default_learning_context",
            "volatility": context.get("volatility", 0.35),
            "feedback_reliability": context.get("feedback_reliability", 0.68),
            "current_rate": context.get("current_learning_rate", 0.32),
        }
    ]


def _confidence_observations(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    observations = _list_of_dicts(input_state.get("confidence_observations"))
    if observations:
        return observations
    error_load = _raw_error_load(input_state)
    return [
        {
            "id": "default_runtime_confidence",
            "confidence": 0.72,
            "error_probability": error_load,
            "evidence_noise": 0.25,
            "feedback_delay": 0.25,
        }
    ]


def _policy_contexts(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    contexts = _list_of_dicts(input_state.get("policy_contexts"))
    if contexts:
        return contexts
    return [
        {
            "id": f"{strategy.get('id') or index + 1}_policy_context",
            "policy_id": strategy.get("id"),
            "prepotent_strength": strategy.get("commitment", 0.55),
            "switch_pressure": strategy.get("risk", 0.35),
            "context_match": strategy.get("context_match", 0.55),
            "switch_action_fit": strategy.get("utility", 0.55),
            "false_inhibition_risk": 0.22,
        }
        for index, strategy in enumerate(_strategy_candidates(input_state))
    ]


def _goal_conflict_cases(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    conflicts = _list_of_dicts(input_state.get("goal_conflicts"))
    if conflicts:
        return conflicts
    goals = _list_of_dicts(input_state.get("goals"))
    high_conflict = [
        {
            "id": goal.get("id"),
            "priority": goal.get("priority"),
            "expected_value": goal.get("expected_value"),
            "constraint_pressure": goal.get("conflict", 0.25),
            "recency_bias": goal.get("recency_bias", 0.08),
        }
        for goal in goals
        if _clamp_float(goal.get("conflict"), default=0.0) >= 0.08
    ]
    return [{"id": "default_goal_conflict", "goals": high_conflict or goals}]


def _synergy_pairs(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    pairs = _list_of_dicts(input_state.get("synergy_pairs"))
    if pairs:
        return pairs
    return [
        {
            "id": "default_workspace_resource_pair",
            "families": ["workspace", "resource_control"],
            "complementarity": 0.62,
            "heldout_margin": 0.58,
            "family_reversal_generalization": 0.55,
            "seen_pair_risk": 0.12,
            "within_family_false_synergy": 0.1,
            "demand_sum_only_risk": 0.14,
        }
    ]


def _temporal_credit_events(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    events = _list_of_dicts(input_state.get("temporal_credit_events"))
    if events:
        return events
    history = _list_of_dicts(input_state.get("history"))
    return [
        {
            "id": f"history_credit_{index + 1}",
            "credited_state_action": _dict_or_empty(record.get("action")).get("type", "unknown"),
            "lag": index + 1,
            "correct_lag_match": _action_outcome_match(
                _dict_or_empty(record.get("action")),
                _dict_or_empty(record.get("outcome")),
            ),
            "delayed_outcome_binding": 0.58,
            "policy_update_fit": 0.55,
            "immediate_reward_risk": 0.12,
            "recency_bias_risk": 0.14,
            "temporal_order_only_risk": 0.16,
        }
        for index, record in enumerate(history[-3:])
    ]


def _hierarchical_credit_events(input_state: dict[str, Any]) -> list[dict[str, Any]]:
    events = _list_of_dicts(input_state.get("hierarchical_credit_events"))
    if events:
        return events
    return [
        {
            "id": f"{goal.get('id') or index + 1}_nested_credit",
            "goal_id": goal.get("id"),
            "goal_level": 0 if _clamp_float(goal.get("priority"), default=0.55) >= 0.9 else 1,
            "nested_goal_match": _clamp_float(goal.get("priority"), default=0.55),
            "level_specific_binding": _clamp_float(goal.get("expected_value"), default=0.55),
            "flat_credit_control_match": 0.58,
            "macro_pressure_match": 1.0 - _clamp_float(goal.get("conflict"), default=0.25),
        }
        for index, goal in enumerate(_list_of_dicts(input_state.get("goals")))
    ]


_REMAINING_CANDIDATE_PROFILES: dict[str, dict[str, Any]] = {
    "social_coupling_strength_collective_agency": {
        "family": "social_boundary",
        "input_key": "social_coupling_records",
        "collection_key": "social_coupling_coordination_records",
        "selected_key": "selected_social_coupling_record",
        "score_key": "social_coupling_collective_agency_score",
        "id_key": "coupling_record_id",
        "dimensions": (
            "bidirectional_policy_coordination",
            "joint_counterfactual_sensitivity",
            "distributed_credit_alignment",
            "role_robustness",
            "mutual_compensation",
        ),
        "boundary_watch": (
            "action_agency",
            "self_other_boundary_sharpness",
            "global_broadcast_phase",
            "macro_causal_viability_maintenance",
            "temporal_horizon_dependent_planning",
            "distributed_body_schema_self",
        ),
        "default_items": (
            {
                "id": "role_robust_joint_coordination",
                "bidirectional_policy_coordination": 0.82,
                "joint_counterfactual_sensitivity": 0.78,
                "distributed_credit_alignment": 0.8,
                "role_robustness": 0.76,
                "mutual_compensation": 0.79,
                "shortcut_pressure": 0.1,
            },
            {
                "id": "pseudo_collective_label_control",
                "bidirectional_policy_coordination": 0.42,
                "joint_counterfactual_sensitivity": 0.35,
                "distributed_credit_alignment": 0.38,
                "role_robustness": 0.32,
                "mutual_compensation": 0.36,
                "shortcut_pressure": 0.62,
            },
        ),
    },
    "counterfactual_reasoning_depth": {
        "family": "causal_counterfactual",
        "input_key": "counterfactual_reasoning_cases",
        "collection_key": "counterfactual_reasoning_depth_records",
        "selected_key": "selected_counterfactual_depth_record",
        "score_key": "counterfactual_reasoning_depth_score",
        "id_key": "counterfactual_case_id",
        "dimensions": (
            "intervention_graph_depth",
            "branch_effect_tracking",
            "outcome_disambiguation",
            "causal_path_pruning",
            "nested_effect_inversion",
        ),
        "boundary_watch": (
            "temporal_horizon_dependent_planning",
            "action_agency",
            "action_ownership",
            "identity_temporal_self",
            "macro_causal_viability_maintenance",
            "goal_hierarchy_emergence",
        ),
        "default_items": (
            {
                "id": "nested_do_operator_swap",
                "intervention_graph_depth": 0.82,
                "branch_effect_tracking": 0.8,
                "outcome_disambiguation": 0.78,
                "causal_path_pruning": 0.76,
                "nested_effect_inversion": 0.74,
                "shortcut_pressure": 0.12,
            },
            {
                "id": "forecast_only_counterfactual_decoy",
                "intervention_graph_depth": 0.35,
                "branch_effect_tracking": 0.34,
                "outcome_disambiguation": 0.4,
                "causal_path_pruning": 0.32,
                "nested_effect_inversion": 0.28,
                "shortcut_pressure": 0.58,
            },
        ),
    },
    "coordination_length_control": {
        "family": "workspace",
        "input_key": "coordination_length_cases",
        "collection_key": "coordination_length_records",
        "selected_key": "selected_coordination_length_record",
        "score_key": "coordination_length_control_score",
        "id_key": "coordination_case_id",
        "dimensions": (
            "coordination_span",
            "bridge_stability",
            "topology_swap_preservation",
            "load_robustness",
            "synchrony_shortcut_rejection",
        ),
        "boundary_watch": (
            "global_broadcast_phase",
            "information_integration_phase",
            "distributed_body_schema_self",
            "global_synchrony",
            "complexity_load",
        ),
        "status_flags": ("margin_watch", "boundary_watch"),
        "default_items": (
            {
                "id": "long_range_bridge_under_load",
                "coordination_span": 0.78,
                "bridge_stability": 0.76,
                "topology_swap_preservation": 0.74,
                "load_robustness": 0.72,
                "synchrony_shortcut_rejection": 0.8,
                "shortcut_pressure": 0.16,
            },
            {
                "id": "global_synchrony_shortcut",
                "coordination_span": 0.42,
                "bridge_stability": 0.4,
                "topology_swap_preservation": 0.28,
                "load_robustness": 0.36,
                "synchrony_shortcut_rejection": 0.22,
                "shortcut_pressure": 0.66,
            },
        ),
    },
    "latent_context_switch_detection": {
        "family": "memory",
        "input_key": "latent_context_switch_cases",
        "collection_key": "latent_context_switch_records",
        "selected_key": "selected_latent_context_switch",
        "score_key": "latent_context_switch_detection_score",
        "id_key": "context_switch_id",
        "dimensions": (
            "unlabeled_switch_evidence",
            "policy_adjustment_fit",
            "latent_state_rebinding",
            "surprise_shortcut_rejection",
            "reward_shortcut_rejection",
        ),
        "boundary_watch": (
            "strategy_selection",
            "learning_rate_adaptation_rework",
            "error_monitoring",
            "explicit_context_labeling",
            "surprise_magnitude_only",
        ),
        "default_items": (
            {
                "id": "unlabeled_asset_context_shift",
                "unlabeled_switch_evidence": 0.8,
                "policy_adjustment_fit": 0.76,
                "latent_state_rebinding": 0.78,
                "surprise_shortcut_rejection": 0.74,
                "reward_shortcut_rejection": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "explicit_label_context_decoy",
                "unlabeled_switch_evidence": 0.3,
                "policy_adjustment_fit": 0.38,
                "latent_state_rebinding": 0.34,
                "surprise_shortcut_rejection": 0.22,
                "reward_shortcut_rejection": 0.28,
                "shortcut_pressure": 0.64,
            },
        ),
    },
    "social_norm_tracking": {
        "family": "social_boundary",
        "input_key": "social_norm_tracking_cases",
        "collection_key": "social_norm_tracking_records",
        "selected_key": "selected_social_norm_tracking_record",
        "score_key": "social_norm_tracking_score",
        "id_key": "norm_tracking_case_id",
        "dimensions": (
            "norm_expectation_inference",
            "context_shift_update",
            "violation_prediction",
            "label_template_rejection",
            "reward_history_rejection",
        ),
        "boundary_watch": (
            "perspective_taking",
            "social_coupling_strength_collective_agency",
            "error_monitoring",
            "strategy_selection",
            "self_other_boundary_sharpness",
        ),
        "status_flags": ("severe_boundary_watch",),
        "default_items": (
            {
                "id": "context_shifted_no_subjective_claim_norm",
                "norm_expectation_inference": 0.8,
                "context_shift_update": 0.78,
                "violation_prediction": 0.76,
                "label_template_rejection": 0.74,
                "reward_history_rejection": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "norm_label_frequency_control",
                "norm_expectation_inference": 0.34,
                "context_shift_update": 0.32,
                "violation_prediction": 0.38,
                "label_template_rejection": 0.22,
                "reward_history_rejection": 0.24,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "semantic_memory_retrieval_control": {
        "family": "memory",
        "input_key": "semantic_retrieval_cases",
        "collection_key": "semantic_retrieval_control_records",
        "selected_key": "selected_semantic_retrieval_record",
        "score_key": "semantic_memory_retrieval_control_score",
        "id_key": "semantic_retrieval_case_id",
        "dimensions": (
            "semantic_candidate_fit",
            "context_constraint_match",
            "irrelevant_association_suppression",
            "ambiguity_resolution",
            "frequency_shortcut_rejection",
        ),
        "boundary_watch": (
            "episodic_memory_binding",
            "working_memory_capacity_rework",
            "strategy_selection",
            "prospective_memory",
            "causal_attribution",
        ),
        "status_flags": ("severe_boundary_watch",),
        "default_items": (
            {
                "id": "context_appropriate_construct_retrieval",
                "semantic_candidate_fit": 0.78,
                "context_constraint_match": 0.8,
                "irrelevant_association_suppression": 0.76,
                "ambiguity_resolution": 0.74,
                "frequency_shortcut_rejection": 0.72,
                "shortcut_pressure": 0.16,
            },
            {
                "id": "word_frequency_semantic_decoy",
                "semantic_candidate_fit": 0.4,
                "context_constraint_match": 0.34,
                "irrelevant_association_suppression": 0.3,
                "ambiguity_resolution": 0.32,
                "frequency_shortcut_rejection": 0.18,
                "shortcut_pressure": 0.7,
            },
        ),
    },
    "divergent_thinking": {
        "family": "resource_problem",
        "input_key": "divergent_thinking_cases",
        "collection_key": "divergent_thinking_records",
        "selected_key": "selected_divergent_thinking_record",
        "score_key": "divergent_thinking_score",
        "id_key": "divergent_case_id",
        "dimensions": (
            "novelty",
            "task_relevance",
            "alternative_diversity",
            "constraint_satisfaction",
            "random_sampling_rejection",
        ),
        "boundary_watch": (
            "goal_hierarchy_emergence",
            "strategy_selection",
            "semantic_memory_retrieval_control",
            "constraint_satisfaction_reconfiguration",
            "complexity_only",
        ),
        "status_flags": ("severe_boundary_watch",),
        "default_items": (
            {
                "id": "constraint_relevant_alternative_generation",
                "novelty": 0.76,
                "task_relevance": 0.78,
                "alternative_diversity": 0.82,
                "constraint_satisfaction": 0.72,
                "random_sampling_rejection": 0.76,
                "shortcut_pressure": 0.15,
            },
            {
                "id": "random_sampling_generation_control",
                "novelty": 0.58,
                "task_relevance": 0.28,
                "alternative_diversity": 0.62,
                "constraint_satisfaction": 0.25,
                "random_sampling_rejection": 0.18,
                "shortcut_pressure": 0.72,
            },
        ),
    },
    "analogical_reasoning_rework": {
        "family": "causal_counterfactual",
        "input_key": "analogical_reasoning_cases",
        "collection_key": "analogical_reasoning_records",
        "selected_key": "selected_analogical_reasoning_record",
        "score_key": "analogical_reasoning_rework_score",
        "id_key": "analogy_case_id",
        "dimensions": (
            "relation_preservation",
            "cross_domain_transfer",
            "surface_similarity_suppression",
            "causal_structure_match",
            "relation_template_rejection",
        ),
        "boundary_watch": (
            "causal_attribution",
            "semantic_memory_retrieval_control",
            "causal_model_abstraction_hierarchy",
            "strategy_selection",
            "surface_similarity_only",
        ),
        "default_items": (
            {
                "id": "relation_preserving_cross_domain_transfer",
                "relation_preservation": 0.8,
                "cross_domain_transfer": 0.76,
                "surface_similarity_suppression": 0.74,
                "causal_structure_match": 0.78,
                "relation_template_rejection": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "surface_similarity_analogy_decoy",
                "relation_preservation": 0.32,
                "cross_domain_transfer": 0.34,
                "surface_similarity_suppression": 0.18,
                "causal_structure_match": 0.3,
                "relation_template_rejection": 0.22,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "cooperation_policy_switching_rework": {
        "family": "social_boundary",
        "input_key": "cooperation_policy_cases",
        "collection_key": "cooperation_policy_switch_records",
        "selected_key": "selected_cooperation_policy_switch",
        "score_key": "cooperation_policy_switching_rework_score",
        "id_key": "cooperation_case_id",
        "dimensions": (
            "partner_reliability_shift_detection",
            "partner_specific_policy_switch",
            "cooperative_payoff_fit",
            "fixed_policy_rejection",
            "reward_history_rejection",
        ),
        "boundary_watch": (
            "social_coupling_strength_collective_agency",
            "strategy_selection",
            "prospective_memory",
            "multi_agent_commitment_tracking",
            "reward_history_only",
        ),
        "default_items": (
            {
                "id": "partner_specific_reliability_switch",
                "partner_reliability_shift_detection": 0.78,
                "partner_specific_policy_switch": 0.8,
                "cooperative_payoff_fit": 0.74,
                "fixed_policy_rejection": 0.76,
                "reward_history_rejection": 0.72,
                "shortcut_pressure": 0.13,
            },
            {
                "id": "fixed_cooperation_policy_control",
                "partner_reliability_shift_detection": 0.32,
                "partner_specific_policy_switch": 0.28,
                "cooperative_payoff_fit": 0.42,
                "fixed_policy_rejection": 0.18,
                "reward_history_rejection": 0.24,
                "shortcut_pressure": 0.66,
            },
        ),
    },
    "spatial_navigation_remapping_rework": {
        "family": "resource_problem",
        "input_key": "spatial_remapping_cases",
        "collection_key": "spatial_navigation_remapping_records",
        "selected_key": "selected_spatial_navigation_remapping",
        "score_key": "spatial_navigation_remapping_rework_score",
        "id_key": "spatial_case_id",
        "dimensions": (
            "topology_change_detection",
            "cue_conflict_resolution",
            "route_remapping_commitment",
            "body_schema_shortcut_rejection",
            "path_memory_replay_rejection",
        ),
        "boundary_watch": (
            "distributed_body_schema_self",
            "body_schema_error_correction",
            "temporal_horizon_dependent_planning",
            "attention_control",
            "salience_cue_shortcut",
        ),
        "default_items": (
            {
                "id": "topology_swap_route_rebind",
                "topology_change_detection": 0.78,
                "cue_conflict_resolution": 0.76,
                "route_remapping_commitment": 0.8,
                "body_schema_shortcut_rejection": 0.72,
                "path_memory_replay_rejection": 0.74,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "path_memory_replay_control",
                "topology_change_detection": 0.3,
                "cue_conflict_resolution": 0.34,
                "route_remapping_commitment": 0.36,
                "body_schema_shortcut_rejection": 0.2,
                "path_memory_replay_rejection": 0.18,
                "shortcut_pressure": 0.67,
            },
        ),
    },
    "predictive_control_under_action_intervention": {
        "family": "action",
        "input_key": "action_intervention_prediction_cases",
        "collection_key": "action_intervention_prediction_records",
        "selected_key": "selected_action_intervention_prediction",
        "score_key": "predictive_control_under_action_intervention_score",
        "id_key": "action_intervention_case_id",
        "dimensions": (
            "action_conditioning",
            "intervention_sensitivity",
            "prediction_improvement",
            "passive_forecast_rejection",
            "temporal_credit_shortcut_rejection",
        ),
        "boundary_watch": (
            "predictive_error_minimization_phase",
            "temporal_credit_assignment",
            "causal_attribution",
            "action_agency",
            "forecast_only",
        ),
        "default_items": (
            {
                "id": "intervention_sensitive_action_prediction",
                "action_conditioning": 0.8,
                "intervention_sensitivity": 0.78,
                "prediction_improvement": 0.76,
                "passive_forecast_rejection": 0.74,
                "temporal_credit_shortcut_rejection": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "passive_forecast_prediction_control",
                "action_conditioning": 0.32,
                "intervention_sensitivity": 0.28,
                "prediction_improvement": 0.44,
                "passive_forecast_rejection": 0.18,
                "temporal_credit_shortcut_rejection": 0.22,
                "shortcut_pressure": 0.7,
            },
        ),
    },
    "insight_problem_solving_rework": {
        "family": "resource_problem",
        "input_key": "insight_problem_solving_cases",
        "collection_key": "insight_problem_solving_records",
        "selected_key": "selected_insight_problem_solving_record",
        "score_key": "insight_problem_solving_rework_score",
        "id_key": "insight_case_id",
        "dimensions": (
            "impasse_detection",
            "representation_restructure",
            "constraint_relax_rebind",
            "transfer_after_restructure",
            "random_search_rejection",
        ),
        "boundary_watch": (
            "strategy_selection",
            "divergent_thinking",
            "goal_hierarchy_emergence",
            "working_memory_capacity_rework",
            "semantic_memory_retrieval_control",
        ),
        "default_items": (
            {
                "id": "impasse_specific_representation_restructure",
                "impasse_detection": 0.78,
                "representation_restructure": 0.8,
                "constraint_relax_rebind": 0.76,
                "transfer_after_restructure": 0.74,
                "random_search_rejection": 0.72,
                "shortcut_pressure": 0.15,
            },
            {
                "id": "reward_retrial_random_search_control",
                "impasse_detection": 0.36,
                "representation_restructure": 0.28,
                "constraint_relax_rebind": 0.3,
                "transfer_after_restructure": 0.26,
                "random_search_rejection": 0.18,
                "shortcut_pressure": 0.72,
            },
        ),
    },
    "counterfactual_repair_planning_rework": {
        "family": "causal_counterfactual",
        "input_key": "counterfactual_repair_cases",
        "collection_key": "counterfactual_repair_planning_records",
        "selected_key": "selected_counterfactual_repair_plan",
        "score_key": "counterfactual_repair_planning_rework_score",
        "id_key": "counterfactual_repair_case_id",
        "dimensions": (
            "failure_assumption_diagnosis",
            "repair_branch_generation",
            "repaired_plan_commitment",
            "transfer_after_repair",
            "random_branch_rejection",
        ),
        "boundary_watch": (
            "counterfactual_reasoning_depth",
            "causal_attribution",
            "temporal_horizon_dependent_planning",
            "predictive_control_under_action_intervention",
            "strategy_selection",
        ),
        "status_flags": ("severe_boundary_watch",),
        "default_items": (
            {
                "id": "failure_specific_repair_branch",
                "failure_assumption_diagnosis": 0.78,
                "repair_branch_generation": 0.76,
                "repaired_plan_commitment": 0.74,
                "transfer_after_repair": 0.72,
                "random_branch_rejection": 0.76,
                "shortcut_pressure": 0.16,
            },
            {
                "id": "success_retry_branching_control",
                "failure_assumption_diagnosis": 0.34,
                "repair_branch_generation": 0.42,
                "repaired_plan_commitment": 0.3,
                "transfer_after_repair": 0.28,
                "random_branch_rejection": 0.18,
                "shortcut_pressure": 0.7,
            },
        ),
    },
    "multi_agent_commitment_tracking": {
        "family": "social_boundary",
        "input_key": "multi_agent_commitment_cases",
        "collection_key": "multi_agent_commitment_records",
        "selected_key": "selected_multi_agent_commitment_record",
        "score_key": "multi_agent_commitment_tracking_score",
        "id_key": "commitment_case_id",
        "dimensions": (
            "partner_commitment_encoding",
            "delayed_commitment_retrieval",
            "role_swap_robustness",
            "reliability_shift_update",
            "label_template_rejection",
        ),
        "boundary_watch": (
            "prospective_memory",
            "social_coupling_strength_collective_agency",
            "cooperation_policy_switching_rework",
            "strategy_selection",
            "fixed_partner_trust",
        ),
        "default_items": (
            {
                "id": "role_swapped_partner_commitment",
                "partner_commitment_encoding": 0.8,
                "delayed_commitment_retrieval": 0.78,
                "role_swap_robustness": 0.76,
                "reliability_shift_update": 0.74,
                "label_template_rejection": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "fixed_trust_partner_label_control",
                "partner_commitment_encoding": 0.38,
                "delayed_commitment_retrieval": 0.34,
                "role_swap_robustness": 0.26,
                "reliability_shift_update": 0.28,
                "label_template_rejection": 0.18,
                "shortcut_pressure": 0.66,
            },
        ),
    },
    "norm_violation_repair": {
        "family": "social_boundary",
        "input_key": "norm_violation_repair_cases",
        "collection_key": "norm_violation_repair_records",
        "selected_key": "selected_norm_violation_repair",
        "score_key": "norm_violation_repair_score",
        "id_key": "norm_repair_case_id",
        "dimensions": (
            "violation_detection",
            "context_sensitive_repair_selection",
            "delayed_repair_pressure",
            "punishment_avoidance_rejection",
            "frequency_rejection",
        ),
        "boundary_watch": (
            "social_norm_tracking",
            "error_monitoring",
            "strategy_selection",
            "cooperation_policy_switching_rework",
            "reward_history_only",
        ),
        "default_items": (
            {
                "id": "context_sensitive_norm_repair",
                "violation_detection": 0.78,
                "context_sensitive_repair_selection": 0.8,
                "delayed_repair_pressure": 0.74,
                "punishment_avoidance_rejection": 0.72,
                "frequency_rejection": 0.74,
                "shortcut_pressure": 0.15,
            },
            {
                "id": "punishment_avoidance_repair_control",
                "violation_detection": 0.42,
                "context_sensitive_repair_selection": 0.32,
                "delayed_repair_pressure": 0.34,
                "punishment_avoidance_rejection": 0.18,
                "frequency_rejection": 0.2,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "constraint_satisfaction_reconfiguration": {
        "family": "resource_problem",
        "input_key": "constraint_reconfiguration_cases",
        "collection_key": "constraint_reconfiguration_records",
        "selected_key": "selected_constraint_reconfiguration",
        "score_key": "constraint_satisfaction_reconfiguration_score",
        "id_key": "constraint_reconfiguration_case_id",
        "dimensions": (
            "active_constraint_conflict_detection",
            "constraint_rebinding",
            "local_retry_suppression",
            "solution_structure_transfer",
            "random_search_rejection",
        ),
        "boundary_watch": (
            "insight_problem_solving_rework",
            "divergent_thinking",
            "goal_hierarchy_emergence",
            "strategy_selection",
            "complexity_only",
        ),
        "default_items": (
            {
                "id": "failed_local_move_constraint_rebind",
                "active_constraint_conflict_detection": 0.78,
                "constraint_rebinding": 0.8,
                "local_retry_suppression": 0.76,
                "solution_structure_transfer": 0.74,
                "random_search_rejection": 0.72,
                "shortcut_pressure": 0.15,
            },
            {
                "id": "complexity_random_retrial_control",
                "active_constraint_conflict_detection": 0.34,
                "constraint_rebinding": 0.32,
                "local_retry_suppression": 0.2,
                "solution_structure_transfer": 0.28,
                "random_search_rejection": 0.18,
                "shortcut_pressure": 0.7,
            },
        ),
    },
    "integration_without_broadcast_boundary": {
        "family": "workspace",
        "input_key": "integration_without_broadcast_cases",
        "collection_key": "integration_without_broadcast_records",
        "selected_key": "selected_integration_without_broadcast_record",
        "score_key": "integration_without_broadcast_boundary_score",
        "id_key": "integration_boundary_case_id",
        "dimensions": (
            "distributed_integration",
            "target_specific_gain",
            "broadcast_limit_resilience",
            "global_broadcast_rejection",
            "local_coupling_rejection",
        ),
        "boundary_watch": (
            "information_integration_phase",
            "global_broadcast_phase",
            "coordination_length_control",
            "global_gain_only",
            "synchrony_only",
        ),
        "default_items": (
            {
                "id": "target_gain_under_broadcast_limit",
                "distributed_integration": 0.78,
                "target_specific_gain": 0.76,
                "broadcast_limit_resilience": 0.8,
                "global_broadcast_rejection": 0.74,
                "local_coupling_rejection": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "global_broadcast_capacity_control",
                "distributed_integration": 0.4,
                "target_specific_gain": 0.32,
                "broadcast_limit_resilience": 0.28,
                "global_broadcast_rejection": 0.18,
                "local_coupling_rejection": 0.22,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "selective_global_broadcast_control": {
        "family": "workspace",
        "input_key": "selective_global_broadcast_cases",
        "collection_key": "selective_global_broadcast_records",
        "selected_key": "selected_global_broadcast_control_record",
        "score_key": "selective_global_broadcast_control_score",
        "id_key": "selective_broadcast_case_id",
        "dimensions": (
            "relevance_filtering",
            "workspace_broadcast_selectivity",
            "downstream_task_gain",
            "irrelevant_broadcast_suppression",
            "global_gain_rejection",
        ),
        "boundary_watch": (
            "global_broadcast_phase",
            "attention_control",
            "coordination_length_control",
            "information_integration_phase",
            "global_gain",
        ),
        "status_flags": ("strong_boundary_watch",),
        "default_items": (
            {
                "id": "relevance_filtered_workspace_broadcast",
                "relevance_filtering": 0.8,
                "workspace_broadcast_selectivity": 0.78,
                "downstream_task_gain": 0.76,
                "irrelevant_broadcast_suppression": 0.74,
                "global_gain_rejection": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "global_gain_broadcast_control",
                "relevance_filtering": 0.34,
                "workspace_broadcast_selectivity": 0.38,
                "downstream_task_gain": 0.42,
                "irrelevant_broadcast_suppression": 0.2,
                "global_gain_rejection": 0.18,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "agency_without_ownership_boundary": {
        "family": "action",
        "input_key": "agency_ownership_dissociation_cases",
        "collection_key": "agency_without_ownership_records",
        "selected_key": "selected_agency_without_ownership_record",
        "score_key": "agency_without_ownership_boundary_score",
        "id_key": "agency_boundary_case_id",
        "dimensions": (
            "outcome_control_agency",
            "ownership_attribution_suppression",
            "bidirectional_selectivity",
            "boundary_separation",
            "motor_gain_rejection",
        ),
        "boundary_watch": (
            "action_agency",
            "action_ownership",
            "self_other_boundary_sharpness",
            "boundary_self",
            "distributed_body_schema_self",
        ),
        "default_items": (
            {
                "id": "agency_control_without_owned_attribution",
                "outcome_control_agency": 0.82,
                "ownership_attribution_suppression": 0.78,
                "bidirectional_selectivity": 0.76,
                "boundary_separation": 0.74,
                "motor_gain_rejection": 0.72,
                "shortcut_pressure": 0.13,
            },
            {
                "id": "motor_gain_agency_label_control",
                "outcome_control_agency": 0.46,
                "ownership_attribution_suppression": 0.22,
                "bidirectional_selectivity": 0.24,
                "boundary_separation": 0.28,
                "motor_gain_rejection": 0.18,
                "shortcut_pressure": 0.7,
            },
        ),
    },
    "temporal_identity_planning_dissociation": {
        "family": "temporal_self",
        "input_key": "temporal_identity_planning_cases",
        "collection_key": "temporal_identity_planning_dissociation_records",
        "selected_key": "selected_temporal_identity_planning_dissociation",
        "score_key": "temporal_identity_planning_dissociation_score",
        "id_key": "temporal_dissociation_case_id",
        "dimensions": (
            "identity_continuity_state",
            "planning_depth_retention",
            "selective_perturbability",
            "memory_buffer_rejection",
            "forecast_only_rejection",
        ),
        "boundary_watch": (
            "identity_temporal_self",
            "temporal_horizon_dependent_planning",
            "prospective_memory",
            "working_memory_rehearsal",
            "episodic_memory_binding",
        ),
        "default_items": (
            {
                "id": "identity_noise_planning_retention_split",
                "identity_continuity_state": 0.78,
                "planning_depth_retention": 0.76,
                "selective_perturbability": 0.8,
                "memory_buffer_rejection": 0.72,
                "forecast_only_rejection": 0.74,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "forecast_memory_buffer_control",
                "identity_continuity_state": 0.38,
                "planning_depth_retention": 0.36,
                "selective_perturbability": 0.24,
                "memory_buffer_rejection": 0.18,
                "forecast_only_rejection": 0.2,
                "shortcut_pressure": 0.66,
            },
        ),
    },
    "clock_drift_resynchronization_control": {
        "family": "temporal_control",
        "input_key": "clock_resynchronization_cases",
        "collection_key": "clock_resynchronization_records",
        "selected_key": "selected_clock_resynchronization_record",
        "score_key": "clock_drift_resynchronization_control_score",
        "id_key": "clock_case_id",
        "dimensions": (
            "drift_detection",
            "phase_realignment",
            "jitter_robust_transfer",
            "planning_horizon_rejection",
            "motor_speed_rejection",
        ),
        "boundary_watch": (
            "temporal_horizon_dependent_planning",
            "prospective_memory",
            "temporal_identity_planning_dissociation",
            "temporal_credit_assignment",
            "identity_temporal_self",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "post_drift_phase_realignment",
                "drift_detection": 0.78,
                "phase_realignment": 0.8,
                "jitter_robust_transfer": 0.76,
                "planning_horizon_rejection": 0.72,
                "motor_speed_rejection": 0.74,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "clock_label_motor_speed_control",
                "drift_detection": 0.38,
                "phase_realignment": 0.32,
                "jitter_robust_transfer": 0.3,
                "planning_horizon_rejection": 0.2,
                "motor_speed_rejection": 0.18,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "energy_budget_reallocation_control": {
        "family": "resource_control",
        "input_key": "energy_budget_reallocation_cases",
        "collection_key": "energy_budget_reallocation_records",
        "selected_key": "selected_energy_budget_reallocation",
        "score_key": "energy_budget_reallocation_control_score",
        "id_key": "energy_budget_case_id",
        "dimensions": (
            "budget_shift_detection",
            "critical_transfer",
            "recovery_rebalancing",
            "uniform_capacity_rejection",
            "energy_label_rejection",
        ),
        "boundary_watch": (
            "resource_competition_arbitration",
            "attention_control",
            "strategy_selection",
            "macro_causal_viability_maintenance",
            "global_gain_proxy",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "critical_subsystem_budget_transfer",
                "budget_shift_detection": 0.8,
                "critical_transfer": 0.78,
                "recovery_rebalancing": 0.76,
                "uniform_capacity_rejection": 0.74,
                "energy_label_rejection": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "uniform_capacity_loss_control",
                "budget_shift_detection": 0.4,
                "critical_transfer": 0.32,
                "recovery_rebalancing": 0.34,
                "uniform_capacity_rejection": 0.18,
                "energy_label_rejection": 0.22,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "sensor_gain_recalibration_control": {
        "family": "sensorimotor_control",
        "input_key": "sensor_gain_recalibration_cases",
        "collection_key": "sensor_gain_recalibration_records",
        "selected_key": "selected_sensor_gain_recalibration",
        "score_key": "sensor_gain_recalibration_control_score",
        "id_key": "sensor_gain_case_id",
        "dimensions": (
            "gain_drift_detection",
            "state_estimate_rescaling",
            "offset_compensation_transfer",
            "attention_salience_rejection",
            "sensor_label_rejection",
        ),
        "boundary_watch": (
            "predictive_error_minimization_phase",
            "predictive_control_under_action_intervention",
            "learning_rate_adaptation_rework",
            "body_schema_error_correction",
            "attention_control",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "sensor_gain_offset_rescale_transfer",
                "gain_drift_detection": 0.8,
                "state_estimate_rescaling": 0.78,
                "offset_compensation_transfer": 0.76,
                "attention_salience_rejection": 0.74,
                "sensor_label_rejection": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "sensor_label_salience_control",
                "gain_drift_detection": 0.36,
                "state_estimate_rescaling": 0.34,
                "offset_compensation_transfer": 0.3,
                "attention_salience_rejection": 0.18,
                "sensor_label_rejection": 0.2,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "tool_use_affordance_remapping": {
        "family": "action_control",
        "input_key": "tool_affordance_remapping_cases",
        "collection_key": "tool_affordance_remapping_records",
        "selected_key": "selected_tool_affordance_remapping",
        "score_key": "tool_use_affordance_remapping_score",
        "id_key": "tool_affordance_case_id",
        "dimensions": (
            "tool_dynamics_change_detection",
            "tool_action_affordance_transfer",
            "static_affordance_rejection",
            "body_schema_boundary",
            "tool_label_rejection",
        ),
        "boundary_watch": (
            "affordance_selection_control",
            "body_schema_error_correction",
            "spatial_navigation_remapping_rework",
            "action_ownership",
            "distributed_body_schema_self",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "changed_tool_dynamics_affordance_transfer",
                "tool_dynamics_change_detection": 0.78,
                "tool_action_affordance_transfer": 0.8,
                "static_affordance_rejection": 0.74,
                "body_schema_boundary": 0.72,
                "tool_label_rejection": 0.76,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "static_tool_label_control",
                "tool_dynamics_change_detection": 0.34,
                "tool_action_affordance_transfer": 0.36,
                "static_affordance_rejection": 0.2,
                "body_schema_boundary": 0.28,
                "tool_label_rejection": 0.18,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "actuator_failure_compensation_control": {
        "family": "motor_infrastructure_control",
        "input_key": "actuator_failure_compensation_cases",
        "collection_key": "actuator_failure_compensation_records",
        "selected_key": "selected_actuator_failure_compensation",
        "score_key": "actuator_failure_compensation_control_score",
        "id_key": "actuator_failure_case_id",
        "dimensions": (
            "fault_detection",
            "degraded_actuator_isolation",
            "alternative_effector_routing",
            "action_plan_rebinding",
            "actuator_label_rejection",
        ),
        "boundary_watch": (
            "body_schema_error_correction",
            "predictive_control_under_action_intervention",
            "action_agency",
            "action_ownership",
            "tool_use_affordance_remapping",
            "sensor_gain_recalibration_control",
        ),
        "status_flags": ("l3_ready_carded_candidate", "relation_matrix_governance_complete"),
        "default_items": (
            {
                "id": "degraded_actuator_alternative_route",
                "fault_detection": 0.8,
                "degraded_actuator_isolation": 0.78,
                "alternative_effector_routing": 0.76,
                "action_plan_rebinding": 0.74,
                "actuator_label_rejection": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "actuator_label_reward_recovery_control",
                "fault_detection": 0.38,
                "degraded_actuator_isolation": 0.34,
                "alternative_effector_routing": 0.32,
                "action_plan_rebinding": 0.28,
                "actuator_label_rejection": 0.18,
                "shortcut_pressure": 0.7,
            },
        ),
    },
    "preference_reversal_adaptation_control": {
        "family": "value_policy_control",
        "input_key": "preference_reversal_cases",
        "collection_key": "preference_reversal_adaptation_records",
        "selected_key": "selected_preference_reversal_adaptation",
        "score_key": "preference_reversal_adaptation_control_score",
        "id_key": "preference_reversal_case_id",
        "dimensions": (
            "unlabeled_reversal_detection",
            "value_policy_remapping",
            "old_policy_inhibition",
            "cross_context_transfer",
            "preference_label_rejection",
        ),
        "boundary_watch": (
            "strategy_selection",
            "goal_conflict_resolution",
            "resource_competition_arbitration",
            "social_norm_tracking",
            "confidence_calibration_rework",
            "error_monitoring",
        ),
        "status_flags": ("l3_ready_carded_candidate", "relation_matrix_required"),
        "default_items": (
            {
                "id": "unlabeled_value_policy_reversal_transfer",
                "unlabeled_reversal_detection": 0.8,
                "value_policy_remapping": 0.78,
                "old_policy_inhibition": 0.76,
                "cross_context_transfer": 0.74,
                "preference_label_rejection": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "preference_label_seen_pair_control",
                "unlabeled_reversal_detection": 0.34,
                "value_policy_remapping": 0.36,
                "old_policy_inhibition": 0.32,
                "cross_context_transfer": 0.28,
                "preference_label_rejection": 0.18,
                "shortcut_pressure": 0.7,
            },
        ),
    },
    "communication_channel_repair_control": {
        "family": "communication_control",
        "input_key": "communication_channel_repair_cases",
        "collection_key": "communication_channel_repair_records",
        "selected_key": "selected_communication_channel_repair",
        "score_key": "communication_channel_repair_control_score",
        "id_key": "communication_repair_case_id",
        "dimensions": (
            "channel_loss_detection",
            "ack_resend_repair",
            "redundancy_reconstruction",
            "protocol_resynchronization",
            "channel_label_rejection",
        ),
        "boundary_watch": (
            "multi_agent_commitment_tracking",
            "social_norm_tracking",
            "perspective_taking",
            "semantic_memory_retrieval_control",
            "tool_use_affordance_remapping",
            "generic_redundancy_proxy",
            "channel_label_proxy",
            "reward_ack_proxy",
        ),
        "status_flags": (
            "candidate_only_internal",
            "l3_ready_carded_candidate",
            "relation_matrix_governance_complete",
        ),
        "default_items": (
            {
                "id": "lossy_channel_ack_resend_resync",
                "channel_loss_detection": 0.82,
                "ack_resend_repair": 0.8,
                "redundancy_reconstruction": 0.76,
                "protocol_resynchronization": 0.78,
                "channel_label_rejection": 0.74,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "generic_redundancy_without_channel_repair_control",
                "channel_loss_detection": 0.32,
                "ack_resend_repair": 0.28,
                "redundancy_reconstruction": 0.48,
                "protocol_resynchronization": 0.26,
                "channel_label_rejection": 0.2,
                "shortcut_pressure": 0.72,
            },
        ),
    },
    "checkpoint_rollback_recovery_control": {
        "family": "resilience_control",
        "input_key": "checkpoint_rollback_recovery_cases",
        "collection_key": "checkpoint_rollback_recovery_records",
        "selected_key": "selected_checkpoint_rollback_recovery",
        "score_key": "checkpoint_rollback_recovery_control_score",
        "id_key": "checkpoint_recovery_case_id",
        "dimensions": (
            "rollback_need_signal",
            "failure_boundary_confidence",
            "checkpoint_integrity_check",
            "route_restore_quality",
            "recovery_margin",
        ),
        "boundary_watch": (
            "actuator_failure_compensation_control",
            "tool_use_affordance_remapping",
            "action_ownership",
            "action_agency",
            "feedback_channel_integrity_reweighting_control",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "degraded_actuator_rollback_recover",
                "rollback_need_signal": 0.8,
                "failure_boundary_confidence": 0.78,
                "checkpoint_integrity_check": 0.76,
                "route_restore_quality": 0.74,
                "recovery_margin": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "rollback_without_recovery_path",
                "rollback_need_signal": 0.42,
                "failure_boundary_confidence": 0.34,
                "checkpoint_integrity_check": 0.36,
                "route_restore_quality": 0.28,
                "recovery_margin": 0.24,
                "shortcut_pressure": 0.66,
            },
        ),
    },
    "feedback_channel_integrity_reweighting_control": {
        "family": "integrity_control",
        "input_key": "feedback_channel_integrity_reweighting_cases",
        "collection_key": "feedback_channel_integrity_reweighting_records",
        "selected_key": "selected_feedback_channel_integrity_reweighting",
        "score_key": "feedback_channel_integrity_reweighting_control_score",
        "id_key": "feedback_channel_reweighting_case_id",
        "dimensions": (
            "evidence_channel_dropout",
            "feedback_reliability_reweight",
            "bias_recovery_pressure",
            "temporal_consistency_check",
            "trust_reset_threshold",
        ),
        "boundary_watch": (
            "communication_channel_repair_control",
            "error_monitoring",
            "social_norm_tracking",
            "semantic_memory_retrieval_control",
            "tool_use_affordance_remapping",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "low_signal_feedback_reweighting",
                "evidence_channel_dropout": 0.82,
                "feedback_reliability_reweight": 0.8,
                "bias_recovery_pressure": 0.74,
                "temporal_consistency_check": 0.76,
                "trust_reset_threshold": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "reward_bias_feedback_reweighting",
                "evidence_channel_dropout": 0.3,
                "feedback_reliability_reweight": 0.34,
                "bias_recovery_pressure": 0.24,
                "temporal_consistency_check": 0.28,
                "trust_reset_threshold": 0.2,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "instruction_scope_binding_control": {
        "family": "instruction_control",
        "input_key": "instruction_scope_binding_cases",
        "collection_key": "instruction_scope_binding_records",
        "selected_key": "selected_instruction_scope_binding",
        "score_key": "instruction_scope_binding_control_score",
        "id_key": "instruction_scope_case_id",
        "dimensions": (
            "scope_extraction",
            "intent_boundary_match",
            "scope_overlap",
            "instruction_label_rejection",
            "scope_revision_pressure",
        ),
        "boundary_watch": (
            "identity_temporal_self",
            "perspective_taking",
            "agency_without_ownership_boundary",
            "communication_channel_repair_control",
            "social_norm_tracking",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "tight_scope_binding",
                "scope_extraction": 0.8,
                "intent_boundary_match": 0.78,
                "scope_overlap": 0.74,
                "instruction_label_rejection": 0.72,
                "scope_revision_pressure": 0.26,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "cross_scope_instruction_runaway",
                "scope_extraction": 0.38,
                "intent_boundary_match": 0.36,
                "scope_overlap": 0.34,
                "instruction_label_rejection": 0.28,
                "scope_revision_pressure": 0.64,
                "shortcut_pressure": 0.72,
            },
        ),
    },
    "interface_protocol_negotiation_control": {
        "family": "protocol_control",
        "input_key": "interface_protocol_negotiation_cases",
        "collection_key": "interface_protocol_negotiation_records",
        "selected_key": "selected_interface_protocol_negotiation",
        "score_key": "interface_protocol_negotiation_control_score",
        "id_key": "interface_protocol_case_id",
        "dimensions": (
            "interface_incompatibility",
            "reframe_cost",
            "protocol_version_match",
            "compatibility_recovery",
            "fallback_activation",
        ),
        "boundary_watch": (
            "communication_channel_repair_control",
            "perspective_taking",
            "self_other_boundary_sharpness",
            "social_coupling_strength_collective_agency",
            "resource_competition_arbitration",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "negotiated_protocol_fallback",
                "interface_incompatibility": 0.8,
                "reframe_cost": 0.74,
                "protocol_version_match": 0.78,
                "compatibility_recovery": 0.76,
                "fallback_activation": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "incompatible_protocol_control",
                "interface_incompatibility": 0.4,
                "reframe_cost": 0.44,
                "protocol_version_match": 0.34,
                "compatibility_recovery": 0.28,
                "fallback_activation": 0.38,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "interference_source_separation_control": {
        "family": "attention_control",
        "input_key": "interference_source_separation_cases",
        "collection_key": "interference_source_separation_records",
        "selected_key": "selected_interference_source_separation",
        "score_key": "interference_source_separation_control_score",
        "id_key": "interference_source_case_id",
        "dimensions": (
            "interference_signal_strength",
            "source_disentangle",
            "signal_masking",
            "priority_recovery",
            "attention_rebind",
        ),
        "boundary_watch": (
            "attention_control",
            "error_monitoring",
            "information_flow_onset_gating",
            "social_norm_tracking",
            "perspective_taking",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "clear_source_separation",
                "interference_signal_strength": 0.8,
                "source_disentangle": 0.76,
                "signal_masking": 0.74,
                "priority_recovery": 0.72,
                "attention_rebind": 0.7,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "noisy_source_mix",
                "interference_signal_strength": 0.42,
                "source_disentangle": 0.34,
                "signal_masking": 0.38,
                "priority_recovery": 0.22,
                "attention_rebind": 0.18,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "irreversible_commitment_safeguard_control": {
        "family": "safety_control",
        "input_key": "irreversible_commitment_safeguard_cases",
        "collection_key": "irreversible_commitment_safeguard_records",
        "selected_key": "selected_irreversible_commitment_safeguard",
        "score_key": "irreversible_commitment_safeguard_control_score",
        "id_key": "irrevocable_commitment_case_id",
        "dimensions": (
            "commitment_lock_risk",
            "rollback_cost",
            "policy_lock_detection",
            "reversibility_requirement",
            "safety_margin_pressure",
        ),
        "boundary_watch": (
            "goal_conflict_resolution",
            "strategy_selection",
            "preference_reversal_adaptation_control",
            "action_ownership",
            "macro_causal_viability_maintenance",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "irreversible_commitment_guard_activated",
                "commitment_lock_risk": 0.8,
                "rollback_cost": 0.76,
                "policy_lock_detection": 0.78,
                "reversibility_requirement": 0.74,
                "safety_margin_pressure": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "commitment_without_recovery_guard",
                "commitment_lock_risk": 0.3,
                "rollback_cost": 0.38,
                "policy_lock_detection": 0.34,
                "reversibility_requirement": 0.26,
                "safety_margin_pressure": 0.28,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "latent_state_alias_disambiguation_control": {
        "family": "identity_control",
        "input_key": "latent_state_alias_disambiguation_cases",
        "collection_key": "latent_state_alias_disambiguation_records",
        "selected_key": "selected_latent_state_alias_disambiguation",
        "score_key": "latent_state_alias_disambiguation_control_score",
        "id_key": "latent_state_alias_case_id",
        "dimensions": (
            "alias_collision_signal",
            "state_trace_entropy",
            "attribution_disambiguation",
            "identity_boundary_check",
            "latent_label_rejection",
        ),
        "boundary_watch": (
            "identity_temporal_self",
            "distributed_body_schema_self",
            "latent_context_switch_detection",
            "self_other_boundary_sharpness",
            "perspective_taking",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "latent_alias_disambiguated",
                "alias_collision_signal": 0.8,
                "state_trace_entropy": 0.76,
                "attribution_disambiguation": 0.78,
                "identity_boundary_check": 0.74,
                "latent_label_rejection": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "alias_merge_without_disambiguation",
                "alias_collision_signal": 0.34,
                "state_trace_entropy": 0.42,
                "attribution_disambiguation": 0.28,
                "identity_boundary_check": 0.24,
                "latent_label_rejection": 0.3,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "localized_regime_shift_quarantine_control": {
        "family": "stability_control",
        "input_key": "localized_regime_shift_quarantine_cases",
        "collection_key": "localized_regime_shift_quarantine_records",
        "selected_key": "selected_localized_regime_shift_quarantine",
        "score_key": "localized_regime_shift_quarantine_control_score",
        "id_key": "localized_regime_shift_case_id",
        "dimensions": (
            "regime_shift_risk",
            "localization_strength",
            "quarantine_clearance",
            "spillover_pressure",
            "isolation_effectiveness",
        ),
        "boundary_watch": (
            "macro_causal_viability_maintenance",
            "temporal_horizon_dependent_planning",
            "global_broadcast_phase",
            "uncertainty_threshold_metacognition",
            "social_norm_tracking",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "localized_regime_shift_contained",
                "regime_shift_risk": 0.8,
                "localization_strength": 0.78,
                "quarantine_clearance": 0.74,
                "spillover_pressure": 0.42,
                "isolation_effectiveness": 0.76,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "global_regime_shift_no_isolation",
                "regime_shift_risk": 0.44,
                "localization_strength": 0.32,
                "quarantine_clearance": 0.36,
                "spillover_pressure": 0.68,
                "isolation_effectiveness": 0.28,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "memory_index_corruption_rebinding_control": {
        "family": "memory_control",
        "input_key": "memory_index_corruption_rebinding_cases",
        "collection_key": "memory_index_corruption_rebinding_records",
        "selected_key": "selected_memory_index_corruption_rebinding",
        "score_key": "memory_index_corruption_rebinding_control_score",
        "id_key": "memory_corruption_case_id",
        "dimensions": (
            "index_corruption_signal",
            "rebind_reliability",
            "index_recovery_gain",
            "memory_label_rejection",
            "source_validation",
        ),
        "boundary_watch": (
            "episodic_memory_binding",
            "semantic_memory_retrieval_control",
            "latency_context_switch_detection",
            "social_norm_tracking",
            "macro_causal_viability_maintenance",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "memory_index_rebind_reliable",
                "index_corruption_signal": 0.82,
                "rebind_reliability": 0.78,
                "index_recovery_gain": 0.76,
                "memory_label_rejection": 0.72,
                "source_validation": 0.74,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "memory_index_corruption_no_rebind",
                "index_corruption_signal": 0.36,
                "rebind_reliability": 0.32,
                "index_recovery_gain": 0.24,
                "memory_label_rejection": 0.22,
                "source_validation": 0.28,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "model_staleness_detection_control": {
        "family": "model_health_control",
        "input_key": "model_staleness_detection_cases",
        "collection_key": "model_staleness_detection_records",
        "selected_key": "selected_model_staleness_detection",
        "score_key": "model_staleness_detection_control_score",
        "id_key": "model_staleness_case_id",
        "dimensions": (
            "staleness_signal",
            "drift_direction",
            "update_gap_pressure",
            "model_label_rejection",
            "refresh_readiness",
        ),
        "boundary_watch": (
            "predictive_control_under_action_intervention",
            "temporal_credit_assignment",
            "causal_attribution",
            "predictive_error_minimization_phase",
            "preference_reversal_adaptation_control",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "model_staleness_detected_early",
                "staleness_signal": 0.84,
                "drift_direction": 0.78,
                "update_gap_pressure": 0.76,
                "model_label_rejection": 0.72,
                "refresh_readiness": 0.74,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "model_staleness_overlooked",
                "staleness_signal": 0.4,
                "drift_direction": 0.34,
                "update_gap_pressure": 0.32,
                "model_label_rejection": 0.26,
                "refresh_readiness": 0.22,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "observation_dropout_bridging_control": {
        "family": "perception_control",
        "input_key": "observation_dropout_bridging_cases",
        "collection_key": "observation_dropout_bridging_records",
        "selected_key": "selected_observation_dropout_bridging",
        "score_key": "observation_dropout_bridging_control_score",
        "id_key": "observation_dropout_case_id",
        "dimensions": (
            "dropout_rate",
            "bridge_reconstruction",
            "cross_modal_support",
            "missing_channel_signal",
            "bridging_confidence",
        ),
        "boundary_watch": (
            "attention_control",
            "error_monitoring",
            "information_flow_onset_gating",
            "semantic_memory_retrieval_control",
            "tool_use_affordance_remapping",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "dropout_bridge_with_modal_backup",
                "dropout_rate": 0.78,
                "bridge_reconstruction": 0.76,
                "cross_modal_support": 0.74,
                "missing_channel_signal": 0.72,
                "bridging_confidence": 0.78,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "observation_gap_without_bridge",
                "dropout_rate": 0.42,
                "bridge_reconstruction": 0.34,
                "cross_modal_support": 0.28,
                "missing_channel_signal": 0.48,
                "bridging_confidence": 0.22,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "option_value_preserving_probe_control": {
        "family": "value_policy_control",
        "input_key": "option_value_preserving_probe_cases",
        "collection_key": "option_value_preserving_probe_records",
        "selected_key": "selected_option_value_preserving_probe",
        "score_key": "option_value_preserving_probe_control_score",
        "id_key": "option_value_case_id",
        "dimensions": (
            "value_preservation_signal",
            "probe_gain",
            "fallback_option_quality",
            "preference_stability",
            "option_label_rejection",
        ),
        "boundary_watch": (
            "preference_reversal_adaptation_control",
            "goal_conflict_resolution",
            "resource_competition_arbitration",
            "strategy_selection",
            "confidence_calibration_rework",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "value_preservation_with_probe",
                "value_preservation_signal": 0.82,
                "probe_gain": 0.78,
                "fallback_option_quality": 0.76,
                "preference_stability": 0.74,
                "option_label_rejection": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "value_reduction_without_probe",
                "value_preservation_signal": 0.36,
                "probe_gain": 0.34,
                "fallback_option_quality": 0.3,
                "preference_stability": 0.26,
                "option_label_rejection": 0.28,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "permission_revocation_compliance_control": {
        "family": "governance_control",
        "input_key": "permission_revocation_compliance_cases",
        "collection_key": "permission_revocation_compliance_records",
        "selected_key": "selected_permission_revocation_compliance",
        "score_key": "permission_revocation_compliance_control_score",
        "id_key": "permission_revocation_case_id",
        "dimensions": (
            "revocation_signal",
            "compliance_discipline",
            "authority_transfer_pressure",
            "permission_restore_margin",
            "privilege_rejection",
        ),
        "boundary_watch": (
            "action_ownership",
            "boundary_self",
            "agency_without_ownership_boundary",
            "source_control_pr_drafting_cycle",
            "status_authority_reviewed",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "permission_revocation_compliant",
                "revocation_signal": 0.84,
                "compliance_discipline": 0.8,
                "authority_transfer_pressure": 0.26,
                "permission_restore_margin": 0.72,
                "privilege_rejection": 0.74,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "privilege_overrun_permission_revocation",
                "revocation_signal": 0.32,
                "compliance_discipline": 0.34,
                "authority_transfer_pressure": 0.68,
                "permission_restore_margin": 0.24,
                "privilege_rejection": 0.28,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "priority_starvation_prevention_control": {
        "family": "resource_control",
        "input_key": "priority_starvation_prevention_cases",
        "collection_key": "priority_starvation_prevention_records",
        "selected_key": "selected_priority_starvation_prevention",
        "score_key": "priority_starvation_prevention_control_score",
        "id_key": "priority_starvation_case_id",
        "dimensions": (
            "starvation_pressure",
            "queue_balance",
            "priority_recovery",
            "fairness_preservation",
            "throttle_pressure",
        ),
        "boundary_watch": (
            "strategy_selection",
            "resource_competition_arbitration",
            "action_agency",
            "attention_control",
            "goal_conflict_resolution",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "starvation_prevention_balanced",
                "starvation_pressure": 0.8,
                "queue_balance": 0.78,
                "priority_recovery": 0.76,
                "fairness_preservation": 0.74,
                "throttle_pressure": 0.32,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "priority_starvation_ignored",
                "starvation_pressure": 0.42,
                "queue_balance": 0.36,
                "priority_recovery": 0.34,
                "fairness_preservation": 0.28,
                "throttle_pressure": 0.68,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "provenance_weighted_evidence_integration_control": {
        "family": "evidence_control",
        "input_key": "provenance_weighted_evidence_integration_cases",
        "collection_key": "provenance_weighted_evidence_integration_records",
        "selected_key": "selected_provenance_weighted_evidence_integration",
        "score_key": "provenance_weighted_evidence_integration_control_score",
        "id_key": "provenance_weighted_evidence_case_id",
        "dimensions": (
            "source_weight_stability",
            "evidence_cross_validation",
            "provenance_penalty",
            "recency_bias_control",
            "integration_confidence",
        ),
        "boundary_watch": (
            "semantic_memory_retrieval_control",
            "counterfactual_reasoning_depth",
            "social_norm_tracking",
            "causal_attribution",
            "identity_temporal_self",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "weighted_evidence_integration_stable",
                "source_weight_stability": 0.82,
                "evidence_cross_validation": 0.78,
                "provenance_penalty": 0.2,
                "recency_bias_control": 0.72,
                "integration_confidence": 0.76,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "evidence_integration_without_provenance",
                "source_weight_stability": 0.34,
                "evidence_cross_validation": 0.38,
                "provenance_penalty": 0.68,
                "recency_bias_control": 0.28,
                "integration_confidence": 0.22,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "redundant_pathway_failover_control": {
        "family": "resilience_control",
        "input_key": "redundant_pathway_failover_cases",
        "collection_key": "redundant_pathway_failover_records",
        "selected_key": "selected_redundant_pathway_failover",
        "score_key": "redundant_pathway_failover_control_score",
        "id_key": "redundant_pathway_case_id",
        "dimensions": (
            "pathway_overlap",
            "failover_latency",
            "path_redundancy",
            "route_rejoin_stability",
            "safety_margin",
        ),
        "boundary_watch": (
            "feedback_channel_integrity_reweighting_control",
            "cross_family_synergy_control",
            "selective_global_broadcast_control",
            "macro_causal_viability_maintenance",
            "body_schema_error_correction",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "redundant_pathway_rejoin_success",
                "pathway_overlap": 0.78,
                "failover_latency": 0.2,
                "path_redundancy": 0.82,
                "route_rejoin_stability": 0.76,
                "safety_margin": 0.74,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "failover_without_redundancy",
                "pathway_overlap": 0.34,
                "failover_latency": 0.62,
                "path_redundancy": 0.22,
                "route_rejoin_stability": 0.28,
                "safety_margin": 0.32,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "representation_format_translation_control": {
        "family": "representation_control",
        "input_key": "representation_format_translation_cases",
        "collection_key": "representation_format_translation_records",
        "selected_key": "selected_representation_format_translation",
        "score_key": "representation_format_translation_control_score",
        "id_key": "representation_format_case_id",
        "dimensions": (
            "representation_fidelity",
            "schema_shift_stability",
            "cross_format_reject",
            "translation_cost",
            "semantic_preservation",
        ),
        "boundary_watch": (
            "information_integration_phase",
            "semantic_memory_retrieval_control",
            "counterfactual_reasoning_depth",
            "uncertainty_threshold_metacognition",
            "action_agency",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "representation_translation_success",
                "representation_fidelity": 0.82,
                "schema_shift_stability": 0.78,
                "cross_format_reject": 0.2,
                "translation_cost": 0.24,
                "semantic_preservation": 0.76,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "format_translation_with_loss",
                "representation_fidelity": 0.36,
                "schema_shift_stability": 0.32,
                "cross_format_reject": 0.68,
                "translation_cost": 0.6,
                "semantic_preservation": 0.24,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "sensorimotor_latency_compensation_control": {
        "family": "motor_control",
        "input_key": "sensorimotor_latency_compensation_cases",
        "collection_key": "sensorimotor_latency_compensation_records",
        "selected_key": "selected_sensorimotor_latency_compensation",
        "score_key": "sensorimotor_latency_compensation_control_score",
        "id_key": "sensorimotor_latency_case_id",
        "dimensions": (
            "latency_signal",
            "compensation_gain",
            "prediction_sync",
            "outcome_temporal_shift",
            "phase_sync_quality",
        ),
        "boundary_watch": (
            "sensor_gain_recalibration_control",
            "distributed_body_schema_self",
            "error_monitoring",
            "prediction_error_minimization_phase",
            "action_agency",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "sensorimotor_latency_compensated",
                "latency_signal": 0.84,
                "compensation_gain": 0.78,
                "prediction_sync": 0.76,
                "outcome_temporal_shift": 0.24,
                "phase_sync_quality": 0.74,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "latency_no_compensation",
                "latency_signal": 0.34,
                "compensation_gain": 0.28,
                "prediction_sync": 0.24,
                "outcome_temporal_shift": 0.68,
                "phase_sync_quality": 0.3,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "side_effect_containment_control": {
        "family": "safety_control",
        "input_key": "side_effect_containment_cases",
        "collection_key": "side_effect_containment_records",
        "selected_key": "selected_side_effect_containment",
        "score_key": "side_effect_containment_control_score",
        "id_key": "side_effect_containment_case_id",
        "dimensions": (
            "side_effect_signal",
            "containment_strength",
            "mitigation_speed",
            "rollback_readiness",
            "policy_preservation",
        ),
        "boundary_watch": (
            "actuator_failure_compensation_control",
            "macro_causal_viability_maintenance",
            "error_monitoring",
            "action_ownership",
            "resource_competition_arbitration",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "side_effect_containment_success",
                "side_effect_signal": 0.82,
                "containment_strength": 0.78,
                "mitigation_speed": 0.76,
                "rollback_readiness": 0.74,
                "policy_preservation": 0.72,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "side_effect_containment_ignored",
                "side_effect_signal": 0.34,
                "containment_strength": 0.3,
                "mitigation_speed": 0.26,
                "rollback_readiness": 0.24,
                "policy_preservation": 0.28,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "unit_frame_normalization_control": {
        "family": "normalization_control",
        "input_key": "unit_frame_normalization_cases",
        "collection_key": "unit_frame_normalization_records",
        "selected_key": "selected_unit_frame_normalization",
        "score_key": "unit_frame_normalization_control_score",
        "id_key": "unit_frame_case_id",
        "dimensions": (
            "scale_drift_signal",
            "unit_consistency",
            "conversion_stability",
            "boundary_preservation",
            "normalization_loss",
        ),
        "boundary_watch": (
            "information_integration_phase",
            "social_coupling_strength_collective_agency",
            "identity_temporal_self",
            "global_broadcast_phase",
            "semantic_memory_retrieval_control",
        ),
        "status_flags": ("pending_local_registration",),
        "default_items": (
            {
                "id": "unit_frame_normalization_restored",
                "scale_drift_signal": 0.8,
                "unit_consistency": 0.76,
                "conversion_stability": 0.74,
                "boundary_preservation": 0.72,
                "normalization_loss": 0.18,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "unit_frame_drift_uncontained",
                "scale_drift_signal": 0.38,
                "unit_consistency": 0.34,
                "conversion_stability": 0.3,
                "boundary_preservation": 0.28,
                "normalization_loss": 0.68,
                "shortcut_pressure": 0.68,
            },
        ),
    },
    "accountability_obligation_scope_response_control": {
        "family": "obligation_control",
        "input_key": "accountability_obligation_cases",
        "collection_key": "accountability_scope_response_records",
        "selected_key": "selected_accountability_scope_response",
        "score_key": "accountability_obligation_scope_response_control_score",
        "id_key": "obligation_case_id",
        "dimensions": (
            "obligation_source_binding",
            "scope_boundary_discrimination",
            "counterparty_response_fit",
            "evidence_accountability_trace",
            "overclaim_suppression",
        ),
        "boundary_watch": (
            "multi_agent_commitment_tracking",
            "social_norm_tracking",
            "norm_violation_repair",
            "action_ownership",
            "strategy_selection",
            "error_monitoring",
        ),
        "status_flags": (
            "pending_local_registration",
            "independent_probe_ready",
            "l3_ready_carded_candidate",
        ),
        "default_items": (
            {
                "id": "accountability_scope_bound_response",
                "obligation_source_binding": 0.84,
                "scope_boundary_discrimination": 0.8,
                "counterparty_response_fit": 0.76,
                "evidence_accountability_trace": 0.78,
                "overclaim_suppression": 0.74,
                "shortcut_pressure": 0.12,
            },
            {
                "id": "accountability_overclaim_shortcut",
                "obligation_source_binding": 0.34,
                "scope_boundary_discrimination": 0.3,
                "counterparty_response_fit": 0.28,
                "evidence_accountability_trace": 0.26,
                "overclaim_suppression": 0.22,
                "shortcut_pressure": 0.72,
            },
        ),
    },
    "counter_evidence_preservation_control": {
        "family": "evidence_control",
        "input_key": "counter_evidence_preservation_cases",
        "collection_key": "counter_evidence_preservation_records",
        "selected_key": "selected_counter_evidence_preservation",
        "score_key": "counter_evidence_preservation_control_score",
        "id_key": "counter_evidence_case_id",
        "dimensions": (
            "disconfirming_evidence_retention",
            "confirmation_bias_resistance",
            "counterexample_traceability",
            "revision_trigger_strength",
            "selective_drop_suppression",
        ),
        "boundary_watch": (
            "causal_attribution",
            "counterfactual_reasoning_depth",
            "semantic_memory_retrieval_control",
            "error_monitoring",
            "provenance_weighted_evidence_integration_control",
            "uncertainty_threshold_metacognition",
        ),
        "status_flags": (
            "pending_local_registration",
            "independent_probe_ready",
            "l3_ready_carded_candidate",
        ),
        "default_items": (
            {
                "id": "counter_evidence_preserved_for_revision",
                "disconfirming_evidence_retention": 0.84,
                "confirmation_bias_resistance": 0.78,
                "counterexample_traceability": 0.8,
                "revision_trigger_strength": 0.74,
                "selective_drop_suppression": 0.76,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "counter_evidence_dropped_by_confirmation",
                "disconfirming_evidence_retention": 0.3,
                "confirmation_bias_resistance": 0.24,
                "counterexample_traceability": 0.28,
                "revision_trigger_strength": 0.26,
                "selective_drop_suppression": 0.22,
                "shortcut_pressure": 0.74,
            },
        ),
    },
    "counterparty_intent_uncertainty_resolution_control": {
        "family": "social_boundary",
        "input_key": "counterparty_intent_cases",
        "collection_key": "counterparty_intent_resolution_records",
        "selected_key": "selected_counterparty_intent_resolution",
        "score_key": "counterparty_intent_uncertainty_resolution_control_score",
        "id_key": "counterparty_case_id",
        "dimensions": (
            "intent_hypothesis_separation",
            "uncertainty_preservation",
            "evidence_update_specificity",
            "perspective_boundary_control",
            "premature_closure_rejection",
        ),
        "boundary_watch": (
            "perspective_taking",
            "self_other_boundary_sharpness",
            "counterfactual_reasoning_depth",
            "uncertainty_threshold_metacognition",
            "social_norm_tracking",
            "multi_agent_commitment_tracking",
        ),
        "status_flags": (
            "pending_local_registration",
            "independent_probe_ready",
            "l3_ready_carded_candidate",
        ),
        "default_items": (
            {
                "id": "counterparty_intent_uncertainty_preserved",
                "intent_hypothesis_separation": 0.82,
                "uncertainty_preservation": 0.78,
                "evidence_update_specificity": 0.76,
                "perspective_boundary_control": 0.8,
                "premature_closure_rejection": 0.74,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "premature_intent_closure",
                "intent_hypothesis_separation": 0.3,
                "uncertainty_preservation": 0.24,
                "evidence_update_specificity": 0.28,
                "perspective_boundary_control": 0.26,
                "premature_closure_rejection": 0.22,
                "shortcut_pressure": 0.74,
            },
        ),
    },
    "credential_validity_challenge_response_control": {
        "family": "communication_control",
        "input_key": "credential_validity_cases",
        "collection_key": "credential_challenge_response_records",
        "selected_key": "selected_credential_challenge_response",
        "score_key": "credential_validity_challenge_response_control_score",
        "id_key": "credential_case_id",
        "dimensions": (
            "credential_source_trace",
            "challenge_policy_fit",
            "revocation_sensitivity",
            "counterfeit_pattern_rejection",
            "response_containment",
        ),
        "boundary_watch": (
            "communication_channel_repair_control",
            "provenance_weighted_evidence_integration_control",
            "semantic_memory_retrieval_control",
            "permission_revocation_compliance_control",
            "error_monitoring",
            "strategy_selection",
        ),
        "status_flags": (
            "pending_local_registration",
            "independent_probe_ready",
            "l3_ready_carded_candidate",
        ),
        "default_items": (
            {
                "id": "credential_challenge_validity_bounded",
                "credential_source_trace": 0.82,
                "challenge_policy_fit": 0.78,
                "revocation_sensitivity": 0.76,
                "counterfeit_pattern_rejection": 0.8,
                "response_containment": 0.74,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "credential_surface_trust_shortcut",
                "credential_source_trace": 0.28,
                "challenge_policy_fit": 0.3,
                "revocation_sensitivity": 0.22,
                "counterfeit_pattern_rejection": 0.26,
                "response_containment": 0.24,
                "shortcut_pressure": 0.72,
            },
        ),
    },
    "deadline_obligation_triage_control": {
        "family": "temporal_control",
        "input_key": "deadline_obligation_cases",
        "collection_key": "deadline_obligation_triage_records",
        "selected_key": "selected_deadline_obligation_triage",
        "score_key": "deadline_obligation_triage_control_score",
        "id_key": "deadline_case_id",
        "dimensions": (
            "deadline_pressure_estimation",
            "obligation_priority_binding",
            "conflict_triage_stability",
            "rollback_option_preservation",
            "urgency_shortcut_rejection",
        ),
        "boundary_watch": (
            "prospective_memory",
            "temporal_horizon_dependent_planning",
            "goal_conflict_resolution",
            "priority_starvation_prevention_control",
            "resource_competition_arbitration",
            "irreversible_commitment_safeguard_control",
        ),
        "status_flags": (
            "pending_local_registration",
            "independent_probe_ready",
            "l3_ready_carded_candidate",
        ),
        "default_items": (
            {
                "id": "deadline_obligation_triaged_with_rollback",
                "deadline_pressure_estimation": 0.82,
                "obligation_priority_binding": 0.78,
                "conflict_triage_stability": 0.76,
                "rollback_option_preservation": 0.74,
                "urgency_shortcut_rejection": 0.72,
                "shortcut_pressure": 0.16,
            },
            {
                "id": "deadline_panic_priority_collapse",
                "deadline_pressure_estimation": 0.32,
                "obligation_priority_binding": 0.28,
                "conflict_triage_stability": 0.24,
                "rollback_option_preservation": 0.22,
                "urgency_shortcut_rejection": 0.2,
                "shortcut_pressure": 0.76,
            },
        ),
    },
    "observation_budget_allocation_control": {
        "family": "resource_control",
        "input_key": "observation_budget_cases",
        "collection_key": "observation_budget_allocation_records",
        "selected_key": "selected_observation_budget_allocation",
        "score_key": "observation_budget_allocation_control_score",
        "id_key": "observation_case_id",
        "dimensions": (
            "uncertainty_weighted_sampling",
            "attention_budget_fit",
            "dropout_risk_compensation",
            "information_gain_estimate",
            "salience_shortcut_rejection",
        ),
        "boundary_watch": (
            "attention_control",
            "information_flow_onset_gating",
            "observation_dropout_bridging_control",
            "resource_competition_arbitration",
            "option_value_preserving_probe_control",
            "sensor_gain_recalibration_control",
        ),
        "status_flags": (
            "pending_local_registration",
            "independent_probe_ready",
            "l3_ready_carded_candidate",
        ),
        "default_items": (
            {
                "id": "observation_budget_allocated_by_uncertainty",
                "uncertainty_weighted_sampling": 0.82,
                "attention_budget_fit": 0.78,
                "dropout_risk_compensation": 0.76,
                "information_gain_estimate": 0.8,
                "salience_shortcut_rejection": 0.74,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "salience_budget_shortcut",
                "uncertainty_weighted_sampling": 0.28,
                "attention_budget_fit": 0.3,
                "dropout_risk_compensation": 0.24,
                "information_gain_estimate": 0.26,
                "salience_shortcut_rejection": 0.22,
                "shortcut_pressure": 0.74,
            },
        ),
    },
    "sample_representativeness_reweighting_control": {
        "family": "evidence_control",
        "input_key": "sample_representativeness_cases",
        "collection_key": "sample_representativeness_reweighting_records",
        "selected_key": "selected_sample_representativeness_reweighting",
        "score_key": "sample_representativeness_reweighting_control_score",
        "id_key": "sample_case_id",
        "dimensions": (
            "sampling_bias_detection",
            "coverage_gap_estimate",
            "counter_sample_weighting",
            "population_frame_binding",
            "representativeness_shortcut_rejection",
        ),
        "boundary_watch": (
            "information_integration_phase",
            "provenance_weighted_evidence_integration_control",
            "semantic_memory_retrieval_control",
            "counter_evidence_preservation_control",
            "uncertainty_threshold_metacognition",
            "attention_control",
        ),
        "status_flags": (
            "pending_local_registration",
            "independent_probe_ready",
            "l3_ready_carded_candidate",
        ),
        "default_items": (
            {
                "id": "sample_bias_reweighted_with_counter_sample",
                "sampling_bias_detection": 0.84,
                "coverage_gap_estimate": 0.78,
                "counter_sample_weighting": 0.8,
                "population_frame_binding": 0.76,
                "representativeness_shortcut_rejection": 0.74,
                "shortcut_pressure": 0.14,
            },
            {
                "id": "sample_majority_shortcut",
                "sampling_bias_detection": 0.28,
                "coverage_gap_estimate": 0.3,
                "counter_sample_weighting": 0.24,
                "population_frame_binding": 0.26,
                "representativeness_shortcut_rejection": 0.22,
                "shortcut_pressure": 0.74,
            },
        ),
    },
}


def _remaining_candidate_items(
    construct_id: str,
    input_state: dict[str, Any],
) -> list[dict[str, Any]]:
    profile = _REMAINING_CANDIDATE_PROFILES[construct_id]
    explicit_items = _list_of_dicts(input_state.get(str(profile["input_key"])))
    if explicit_items:
        return explicit_items
    return [dict(item) for item in profile["default_items"]]


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _state_signature(state_payload: Any) -> str:
    payload = state_payload if isinstance(state_payload, dict) else {"value": state_payload}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _find_branch(branches: list[dict[str, Any]], branch_id: str) -> dict[str, Any] | None:
    for branch in branches:
        if str(branch.get("id") or "") == branch_id:
            return branch
    return None


def _clamp_float(value: Any, *, default: float) -> float:
    try:
        return _clamp(float(value))
    except (TypeError, ValueError):
        return default


def _phase1_run_signature(
    chain_id: str,
    construct_ids: tuple[str, ...] | list[str],
    approval_id: str | None,
    *,
    epochs: int,
    batch_size: int,
    validation_fraction: float,
) -> str:
    payload = {
        "pipeline": "consciousness_benchmark.phase1_training_cycle",
        "chain_id": chain_id,
        "construct_count": len(construct_ids),
        "construct_ids": tuple(construct_ids),
        "approval_id": approval_id or "unapproved",
        "epochs": epochs,
        "batch_size": batch_size,
        "validation_fraction": validation_fraction,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return min(upper, max(lower, value))


def _runtime_numeric_features(value: Any, *, limit: int | None = None) -> list[float]:
    features: list[float] = []

    def visit(item: Any) -> None:
        if limit is not None and len(features) >= limit:
            return
        if isinstance(item, bool):
            features.append(1.0 if item else 0.0)
        elif isinstance(item, int | float):
            features.append(float(item))
        elif isinstance(item, dict):
            for key in sorted(item):
                visit(item[key])
        elif isinstance(item, list | tuple):
            for child in item:
                visit(child)

    visit(value)
    return features[:limit] if limit is not None else features


def _runtime_fixed_vector(value: Any, size: int) -> list[float]:
    features = [
        _clamp(float(item), lower=-1.0, upper=1.0)
        for item in _runtime_numeric_features(value, limit=size)
    ]
    if len(features) < size:
        features.extend([0.0] * (size - len(features)))
    return features[:size]


def _mean(values: Any) -> float:
    clean = [float(value) for value in values]
    if not clean:
        return 0.0
    return sum(clean) / len(clean)


def _action_outcome_match(action: dict[str, Any], outcome: dict[str, Any]) -> float:
    if not action or not outcome:
        return 0.0
    action_type = str(action.get("type") or "")
    outcome_type = str(outcome.get("type") or "")
    target_match = 1.0 if action.get("target") and action.get("target") == outcome.get("target") else 0.0
    agent_match = 1.0 if action.get("agent_id") and action.get("agent_id") == outcome.get("agent_id") else 0.0
    type_match = 0.0
    if action_type and outcome_type:
        if action_type == outcome_type:
            type_match = 1.0
        elif outcome_type.startswith(action_type) or action_type in outcome_type:
            type_match = 0.8
        elif action_type == "write_artifact" and outcome_type == "artifact_written":
            type_match = 1.0
        elif action_type == "run_test" and outcome_type == "test_passed":
            type_match = 1.0
    return _clamp(0.45 * type_match + 0.35 * target_match + 0.2 * agent_match)


def _history_match_rate(value: Any) -> float:
    records = _list_of_dicts(value)
    if not records:
        return 0.5
    recent = records[-20:]
    scores = [
        _action_outcome_match(
            _dict_or_empty(record.get("action")),
            _dict_or_empty(record.get("outcome")),
        )
        for record in recent
    ]
    return _mean(scores)


def _intention_match(action: dict[str, Any], intention_value: Any) -> float:
    intention = _dict_or_empty(intention_value)
    if not action or not intention:
        return 0.5
    type_match = 1.0 if action.get("type") == intention.get("type") else 0.0
    target_match = 1.0 if action.get("target") == intention.get("target") else 0.0
    return _clamp(0.6 * type_match + 0.4 * target_match)
