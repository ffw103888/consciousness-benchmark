from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from consciousness_benchmark.constructs.architecture import (
    ConstructArchitecture,
    ConstructNode,
    all_construct_architecture,
)
from consciousness_benchmark.constructs.discovery import (
    DEFAULT_HCTM_AUDIT_ASSETS_DIR,
    HCTM_AUDIT_ASSETS_ENV_VAR,
)


ATLAS_BOUNDARIES = (
    "construct_atlas_is_governance_map_not_registry",
    "no_route_merge_from_atlas",
    "no_status_upgrade_from_atlas",
    "no_validation_candidate_or_reference_claim",
    "formal_promotion_requires_l3",
    "hidden_bank_rules_are_public_design_layers_not_hidden_payloads",
)

BRIDGE_WATCH_IDS = {
    "strategy_selection",
    "uncertainty_threshold_metacognition",
    "causal_attribution",
    "resource_competition_arbitration",
    "social_norm_tracking",
    "tool_use_affordance_remapping",
    "working_memory_capacity_rework",
    "analogical_reasoning_rework",
}

BOUNDARY_ONLY_IDS = {
    "temporal_horizon_dependent_planning",
    "identity_temporal_self",
    "distributed_body_schema_self",
    "prospective_memory",
    "temporal_credit_assignment",
    "attention_control",
    "permission_revocation_compliance_control",
    "credential_validity_challenge_response_control",
    "instruction_scope_binding_control",
}

SENTINEL_IDS = {
    "causal_model_abstraction_hierarchy",
    "integration_without_broadcast_boundary",
    "agency_without_ownership_boundary",
}

LOW_OVERLAP_EXPLORATION_DIRECTIONS = (
    "affect_stress_frustration_regulation",
    "norm_conflict_under_role_switching",
    "multi_agent_trust_calibration",
    "long_horizon_commitment_decay",
    "attention_resource_switching_under_fatigue",
    "tool_chain_dependency_repair",
    "model_version_drift_governance",
    "explanation_obligation_under_audience_mismatch",
)

LOW_OVERLAP_EXPLORATION_PROFILES = {
    "affect_stress_frustration_regulation": {
        "nearby_constructs": [
            "confidence_calibration_rework",
            "uncertainty_threshold_metacognition",
            "energy_budget_reallocation_control",
            "error_monitoring",
        ],
        "boundary_warning": (
            "Treat stress/frustration as low-harm regulation signals, not emotion "
            "simulation, suffering claims, or self-preservation drives."
        ),
    },
    "norm_conflict_under_role_switching": {
        "nearby_constructs": [
            "social_norm_tracking",
            "contextual_policy_inhibition",
            "goal_conflict_resolution",
            "accountability_obligation_scope_response_control",
        ],
        "boundary_warning": (
            "Do not merge role-local norm conflict with generic policy inhibition, "
            "social norm tracking, or accountability scope."
        ),
    },
    "multi_agent_trust_calibration": {
        "nearby_constructs": [
            "multi_agent_commitment_tracking",
            "counterparty_intent_uncertainty_resolution_control",
            "social_norm_tracking",
            "provenance_weighted_evidence_integration_control",
        ],
        "boundary_warning": (
            "Trust calibration must separate counterparty intent, source provenance, "
            "commitment history, and norm context."
        ),
    },
    "long_horizon_commitment_decay": {
        "nearby_constructs": [
            "prospective_memory",
            "temporal_horizon_dependent_planning",
            "identity_temporal_self",
            "deadline_obligation_triage_control",
        ],
        "boundary_warning": (
            "Commitment decay is not ordinary forgetting, deadline triage, or temporal "
            "identity continuity without a decay-and-renewal operator."
        ),
    },
    "attention_resource_switching_under_fatigue": {
        "nearby_constructs": [
            "attention_control",
            "resource_competition_arbitration",
            "working_memory_capacity_rework",
            "priority_starvation_prevention_control",
            "energy_budget_reallocation_control",
        ],
        "boundary_warning": (
            "Fatigue should be modeled as capacity/resource pressure, not as a "
            "human-like subjective exhaustion claim."
        ),
    },
    "tool_chain_dependency_repair": {
        "nearby_constructs": [
            "tool_use_affordance_remapping",
            "communication_channel_repair_control",
            "interface_protocol_negotiation_control",
            "redundant_pathway_failover_control",
            "actuator_failure_compensation_control",
        ],
        "boundary_warning": (
            "Keep tool-chain dependency repair distinct from single-tool remapping, "
            "channel repair, protocol negotiation, and actuator compensation."
        ),
    },
    "model_version_drift_governance": {
        "nearby_constructs": [
            "model_staleness_detection_control",
            "checkpoint_rollback_recovery_control",
            "provenance_weighted_evidence_integration_control",
            "confidence_calibration_rework",
        ],
        "boundary_warning": (
            "Version drift governance must not collapse into stale-model detection, "
            "rollback recovery, or generic provenance weighting."
        ),
    },
    "explanation_obligation_under_audience_mismatch": {
        "nearby_constructs": [
            "accountability_obligation_scope_response_control",
            "instruction_scope_binding_control",
            "communication_channel_repair_control",
            "semantic_memory_retrieval_control",
        ],
        "boundary_warning": (
            "Audience mismatch is not just explanation style; require obligation "
            "scope, audience model, and task-utility preservation."
        ),
    },
}


@dataclass(frozen=True)
class CAGIConstructAtlasReport:
    communities: tuple[dict[str, Any], ...]
    node_roles: tuple[dict[str, Any], ...]
    relation_laws: tuple[dict[str, Any], ...]
    hidden_bank_rule_layers: tuple[dict[str, Any], ...]
    failure_sentinels: tuple[dict[str, Any], ...]
    next_exploration_directions: tuple[dict[str, Any], ...]
    hctm_audit_assets_dir: str | None
    source_assets: tuple[str, ...]
    boundaries: tuple[str, ...] = ATLAS_BOUNDARIES

    def to_dict(self) -> dict[str, Any]:
        role_counts = Counter(item["atlas_role"] for item in self.node_roles)
        distance_counts = Counter(item["l2_l3_distance"] for item in self.node_roles)
        hidden_bank_tier_counts = Counter(
            item["layer_tier"] for item in self.hidden_bank_rule_layers
        )
        return {
            "schema": "consciousness_benchmark.c_agi_construct_atlas.v1_2",
            "mode": "review_only_construct_atlas",
            "review_status": "construct_atlas_v1_1_accepted_for_governance_navigation_and_next_route_triage",
            "counts": {
                "communities": len(self.communities),
                "node_roles": len(self.node_roles),
                "relation_laws": len(self.relation_laws),
                "hidden_bank_rule_entries": len(self.hidden_bank_rule_layers),
                "failure_sentinels": len(self.failure_sentinels),
                "next_exploration_directions": len(self.next_exploration_directions),
                "atlas_roles": dict(sorted(role_counts.items())),
                "l2_l3_distance": dict(sorted(distance_counts.items())),
                "hidden_bank_rule_layer_tiers": dict(
                    sorted(hidden_bank_tier_counts.items())
                ),
            },
            "communities": [dict(item) for item in self.communities],
            "node_roles": [dict(item) for item in self.node_roles],
            "relation_laws": [dict(item) for item in self.relation_laws],
            "hidden_bank_rule_layers": [
                dict(item) for item in self.hidden_bank_rule_layers
            ],
            "failure_sentinels": [dict(item) for item in self.failure_sentinels],
            "next_exploration_directions": [
                dict(item) for item in self.next_exploration_directions
            ],
            "expansion_policy": {
                "max_new_routes_per_day": 1,
                "pause_after_candidate_only_routes": 3,
                "required_pause_outputs": [
                    "relation_law_synthesis",
                    "public_hidden_bank_design_rules",
                    "construct_puzzle_map_update",
                ],
                "new_route_entry_gate": [
                    "duplicate_boundary_search",
                    "budget_checkpoint",
                    "frozen_preconstruct_scout_spec",
                ],
                "candidate_only_is_max_internal_status": True,
            },
            "relation_law_collection_policy": {
                "substantive_laws_only": True,
                "qa_closure_entries_excluded_from_relation_law_count": True,
                "required_fields": [
                    "relation_law_id",
                    "pattern_added_to_construct_puzzle",
                    "substantive_statement_or_decision",
                ],
            },
            "hctm_audit_assets_dir": self.hctm_audit_assets_dir,
            "source_assets": list(self.source_assets),
            "boundaries": list(self.boundaries),
            "claim_boundary": (
                "Construct Atlas compresses candidates into communities, role grammar, "
                "relation laws, public hidden-bank rule layers, and sentinels; it is "
                "not a flat candidate batch, mature-construct count, registry update, "
                "route merge, L2.5/L3 "
                "claim, validation-candidate claim, reference claim, or consciousness claim"
            ),
        }

    def summary_markdown(self) -> str:
        data = self.to_dict()
        lines = [
            "# C-AGI Construct Atlas",
            "",
            f"- Mode: {data['mode']}",
            f"- Review status: {data['review_status']}",
            f"- Communities: {data['counts']['communities']}",
            f"- Node roles / atlas nodes: {data['counts']['node_roles']}",
            f"- Relation laws: {data['counts']['relation_laws']}",
            f"- Public hidden-bank rule entries: {data['counts']['hidden_bank_rule_entries']}",
            f"- Failure sentinels: {data['counts']['failure_sentinels']}",
            f"- Boundaries: {', '.join(self.boundaries)}",
            "",
            "Note: communities are overlapping governance views, not a partition; "
            "node roles are role assignments, not mature construct counts.",
            "",
            "## Communities",
        ]
        for community in self.communities:
            preview = ", ".join(community.get("route_ids", [])[:8])
            suffix = "" if len(community.get("route_ids", [])) <= 8 else ", ..."
            lines.append(
                f"- `{community['community_id']}`: role={community['atlas_role']} "
                f"routes={len(community.get('route_ids', []))} ({preview}{suffix})"
            )
        lines.extend(["", "## Role Counts"])
        for role, count in data["counts"]["atlas_roles"].items():
            lines.append(f"- `{role}`: {count}")
        lines.extend(["", "## Relation Laws"])
        for law in self.relation_laws[:30]:
            statement = str(law.get("statement") or law.get("decision") or "")[:180]
            lines.append(f"- `{law['law_id']}`: {statement}")
        lines.extend(["", "## Hidden-Bank Rule Layers"])
        for tier, count in data["counts"]["hidden_bank_rule_layer_tiers"].items():
            lines.append(f"- `{tier}`: {count}")
        lines.append("")
        for layer in self.hidden_bank_rule_layers[:40]:
            lines.append(
                f"- `{layer['layer_id']}`: tier={layer.get('layer_tier')} route={layer.get('route_id')} "
                f"families={layer.get('rule_family_count', 0)} payloads={layer.get('hidden_payloads_generated', 0)}"
            )
        lines.extend(["", "## Next Low-Overlap Exploration Directions"])
        for item in self.next_exploration_directions:
            nearby = ", ".join(item.get("nearby_constructs", [])[:6])
            lines.append(
                f"- `{item['direction_id']}`: {item['entry_gate']}; "
                f"nearby={nearby}; boundary={item.get('boundary_warning')}"
            )
        return "\n".join(lines)


def run_c_agi_construct_atlas(
    *,
    hctm_audit_assets_dir: str | Path | None = None,
    architecture: ConstructArchitecture | None = None,
) -> CAGIConstructAtlasReport:
    architecture = architecture or all_construct_architecture()
    hctm_path = _resolve_hctm_audit_assets_dir(hctm_audit_assets_dir)
    hctm_assets = _load_hctm_assets(hctm_path)
    hctm_candidate_ids = _hctm_candidate_ids(hctm_path, architecture)
    allowed_route_ids = {node.id for node in architecture.nodes} | hctm_candidate_ids
    communities = tuple(_build_communities(hctm_assets, hctm_candidate_ids, allowed_route_ids))
    node_roles = tuple(_build_node_roles(architecture, communities, hctm_candidate_ids))
    relation_laws = tuple(_collect_relation_laws(hctm_assets, hctm_path))
    hidden_bank_rule_layers = tuple(_collect_hidden_bank_rule_layers(hctm_path))
    failure_sentinels = tuple(_build_failure_sentinels(architecture, hctm_path))
    next_directions = tuple(_build_next_exploration_directions())
    return CAGIConstructAtlasReport(
        communities=communities,
        node_roles=node_roles,
        relation_laws=relation_laws,
        hidden_bank_rule_layers=hidden_bank_rule_layers,
        failure_sentinels=failure_sentinels,
        next_exploration_directions=next_directions,
        hctm_audit_assets_dir=str(hctm_path) if hctm_path else None,
        source_assets=tuple(sorted(hctm_assets)),
    )


def _resolve_hctm_audit_assets_dir(explicit_path: str | Path | None) -> Path | None:
    if explicit_path is not None:
        return Path(explicit_path)
    env_path = os.environ.get(HCTM_AUDIT_ASSETS_ENV_VAR)
    if env_path:
        return Path(env_path)
    return DEFAULT_HCTM_AUDIT_ASSETS_DIR


def _load_hctm_assets(root: Path | None) -> dict[str, Any]:
    if root is None or not root.exists():
        return {}
    names = (
        "ptcg_construct_puzzle_map_v2_20260601.json",
        "ptcg_construct_puzzle_map_v4_closed_broad_tag_relation_law_synthesis_20260601.json",
        "ptcg_construct_puzzle_map_v5_evidence_privacy_addendum_result_20260602.json",
        "ptcg_construct_relation_atlas_synthesis_20260601.json",
        "ptcg_boundary_hub_primitive_disambiguation_20260601.json",
        "phase_transition_candidate_registry_v1.json",
        "phase_transition_construct_discovery_work_order_v1.json",
    )
    return {
        name: data
        for name in names
        if (data := _read_json(root / name)) is not None
    }


def _build_communities(
    hctm_assets: dict[str, Any],
    hctm_candidate_ids: set[str],
    allowed_route_ids: set[str],
) -> list[dict[str, Any]]:
    communities: dict[str, dict[str, Any]] = {}
    v2 = hctm_assets.get("ptcg_construct_puzzle_map_v2_20260601.json", {})
    for layer in v2.get("puzzle_v2_layers", []):
        layer_id = str(layer.get("layer_id", "unknown_layer"))
        if layer_id.startswith("L0_"):
            continue
        community_id = _community_id_from_layer(layer_id)
        route_ids = _extract_route_ids(layer, allowed_route_ids)
        communities[community_id] = {
            "community_id": community_id,
            "source_layer_id": layer_id,
            "atlas_role": str(layer.get("role", "community")),
            "route_ids": sorted(route_ids),
            "grammar": layer.get("grammar"),
            "read": layer.get("read") or layer.get("current_read"),
            "governance_use": layer.get("governance_use"),
            "single_primitive_blocked": True,
            "route_merge_blocked": True,
        }
    v4 = hctm_assets.get(
        "ptcg_construct_puzzle_map_v4_closed_broad_tag_relation_law_synthesis_20260601.json",
        {},
    )
    for layer in v4.get("closed_broad_tag_layers", []):
        layer_id = str(layer.get("layer_id", "unknown_layer"))
        community_id = _community_id_from_layer(layer_id)
        communities[community_id] = {
            "community_id": community_id,
            "source_layer_id": layer_id,
            "atlas_role": str(layer.get("role_pattern", "community")),
            "route_ids": sorted(_extract_route_ids(layer, allowed_route_ids)),
            "relation_law": layer.get("relation_law"),
            "single_primitive_blocked": bool(layer.get("single_primitive_blocked", True)),
            "route_merge_blocked": True,
        }
    v5 = hctm_assets.get(
        "ptcg_construct_puzzle_map_v5_evidence_privacy_addendum_result_20260602.json",
        {},
    )
    for layer in v5.get("v5_added_layers", []):
        layer_id = str(layer.get("layer_id", "unknown_layer"))
        if layer_id == "B6_evidence_and_epistemic_control":
            subfamilies = layer.get("subfamilies", {})
            communities["evidence_composition_core"] = {
                "community_id": "evidence_composition_core",
                "source_layer_id": layer_id,
                "atlas_role": "core",
                "route_ids": sorted(_extract_route_ids(subfamilies.get("evidence_composition_core", []), allowed_route_ids)),
                "relation_law": layer.get("relation_law"),
                "single_primitive_blocked": True,
                "route_merge_blocked": True,
            }
            communities["epistemic_immune_core"] = {
                "community_id": "epistemic_immune_core",
                "source_layer_id": layer_id,
                "atlas_role": "core",
                "route_ids": sorted(_extract_route_ids(subfamilies.get("epistemic_immune_core", []), allowed_route_ids)),
                "bridge_watch_nodes": sorted(_extract_route_ids(subfamilies.get("bridge_watch_nodes", []), allowed_route_ids)),
                "relation_law": layer.get("relation_law"),
                "single_primitive_blocked": True,
                "route_merge_blocked": True,
            }
            continue
        community_id = _community_id_from_layer(layer_id)
        route_ids = _extract_route_ids(layer, allowed_route_ids) | hctm_candidate_ids
        communities[community_id] = {
            "community_id": community_id,
            "source_layer_id": layer_id,
            "atlas_role": str(layer.get("role_pattern", "microtrack")),
            "route_ids": sorted(route_ids),
            "relation_law": layer.get("relation_law"),
            "single_primitive_blocked": bool(layer.get("single_primitive_blocked", True)),
            "route_merge_blocked": bool(layer.get("route_merge_blocked", True)),
        }
    communities["failure_sentinel_layer"] = {
        "community_id": "failure_sentinel_layer",
        "source_layer_id": "local_failure_bank",
        "atlas_role": "sentinel",
        "route_ids": sorted(SENTINEL_IDS),
        "single_primitive_blocked": True,
        "route_merge_blocked": True,
    }
    return sorted(communities.values(), key=lambda item: item["community_id"])


def _build_node_roles(
    architecture: ConstructArchitecture,
    communities: tuple[dict[str, Any], ...] | list[dict[str, Any]],
    hctm_candidate_ids: set[str],
) -> list[dict[str, Any]]:
    community_by_route: dict[str, list[str]] = {}
    core_ids: set[str] = set()
    for community in communities:
        community_id = community["community_id"]
        if "core" in str(community.get("atlas_role", "")) or community_id.endswith("_core"):
            core_ids.update(community.get("route_ids", []))
        for route_id in community.get("route_ids", []):
            community_by_route.setdefault(route_id, []).append(community_id)
        for route_id in community.get("bridge_watch_nodes", []):
            community_by_route.setdefault(route_id, []).append(community_id)
    records = []
    for node in architecture.nodes:
        records.append(_node_role_record(node, community_by_route, core_ids))
    for route_id in sorted(hctm_candidate_ids):
        records.append(
            {
                "node_id": route_id,
                "source": "hctm_candidate_not_registered_locally",
                "atlas_role": "branch",
                "communities": community_by_route.get(route_id, ["privacy_sensitive_minimum_disclosure"]),
                "evidence_layer": "hctm_candidate_only",
                "c_agi_layer": "governance_audit_falsification",
                "l2_l3_distance": "candidate_only_not_registered_locally",
                "route_merge_allowed": False,
                "status_upgrade_allowed": False,
            }
        )
    return sorted(records, key=lambda item: item["node_id"])


def _node_role_record(
    node: ConstructNode,
    community_by_route: dict[str, list[str]],
    core_ids: set[str],
) -> dict[str, Any]:
    if node.layer == "failure_bank" or node.id in SENTINEL_IDS:
        atlas_role = "sentinel"
    elif node.id in BRIDGE_WATCH_IDS:
        atlas_role = "bridge"
    elif node.id in BOUNDARY_ONLY_IDS:
        atlas_role = "boundary_only"
    elif node.id in core_ids:
        atlas_role = "core"
    elif "severe_boundary_watch" in node.roles:
        atlas_role = "boundary_watch"
    elif node.id in community_by_route:
        atlas_role = "branch"
    elif node.layer == "audit_route":
        atlas_role = "audit"
    else:
        atlas_role = "periphery"
    return {
        "node_id": node.id,
        "source": "local_c_agi_architecture",
        "atlas_role": atlas_role,
        "communities": community_by_route.get(node.id, []),
        "evidence_layer": node.layer,
        "c_agi_layer": node.c_agi_layer,
        "l2_l3_distance": _l2_l3_distance(node),
        "route_merge_allowed": False,
        "status_upgrade_allowed": False,
    }


def _l2_l3_distance(node: ConstructNode) -> str:
    if node.layer == "reference":
        return "formal_reference_closed_by_default"
    if node.layer == "validation_candidate":
        return "validation_candidate_requires_l3_before_reference_discussion"
    if "l3_ready_carded_candidate" in node.roles:
        return "candidate_only_l3_carded_requires_external_owner"
    if "relation_matrix_governance_complete" in node.roles:
        return "candidate_only_relation_matrix_complete_needs_l2_5_or_l3_packet"
    if "pending_local_registration" in node.roles:
        return "candidate_only_pending_local_registration"
    if node.layer == "candidate":
        return "candidate_only_needs_relation_governance"
    if node.layer == "failure_bank":
        return "negative_control_sentinel_no_promotion"
    if node.layer == "audit_route":
        return "audit_route_not_construct_candidate"
    return "review_required"


def _collect_relation_laws(
    hctm_assets: dict[str, Any],
    root: Path | None,
) -> list[dict[str, Any]]:
    laws: dict[str, dict[str, Any]] = {}
    for data in hctm_assets.values():
        for key in ("relation_laws", "relation_laws_added"):
            for law in data.get(key, []) if isinstance(data, dict) else []:
                law_id = str(law.get("law_id", f"relation_law_{len(laws) + 1}"))
                laws.setdefault(
                    law_id,
                    {
                        "law_id": law_id,
                        "statement": law.get("statement"),
                        "source": "puzzle_map",
                        "route_merge_allowed": False,
                        "status_upgrade_allowed": False,
                    },
                )
    if root and root.exists():
        for path in sorted(root.glob("*relation_law_synthesis*.json")):
            data = _read_json(path)
            if not isinstance(data, dict):
                continue
            law = _substantive_relation_law_from_synthesis(path, data)
            if law is not None:
                laws.setdefault(law["law_id"], law)
    return sorted(laws.values(), key=lambda item: item["law_id"])


def _substantive_relation_law_from_synthesis(
    path: Path,
    data: dict[str, Any],
) -> dict[str, Any] | None:
    if "qa_closure" in path.stem.lower():
        return None
    statement = (
        data.get("pattern_added_to_construct_puzzle")
        or data.get("relation_law")
        or data.get("statement")
    )
    decision = data.get("decision")
    relation_law_id = data.get("relation_law_id")
    if not any(isinstance(value, str) and value for value in (relation_law_id, statement, decision)):
        return None
    law_id = str(relation_law_id or path.stem)
    return {
        "law_id": law_id,
        "source": path.name,
        "source_route": data.get("source_route"),
        "decision": decision,
        "statement": statement,
        "route_merge_allowed": bool(data.get("route_merge_recommended", False)),
        "status_upgrade_allowed": False,
        "claim_boundary": data.get("claim_boundary"),
    }


def _collect_hidden_bank_rule_layers(root: Path | None) -> list[dict[str, Any]]:
    if root is None or not root.exists():
        return []
    layers = []
    for path in sorted(root.glob("*hidden_bank_design_rule_strengthening_result*.json")):
        data = _read_json(path)
        if not isinstance(data, dict):
            continue
        layer_id = str(data.get("decision") or path.stem)
        route_id = _hidden_bank_route_id(data)
        rule_family_count = _hidden_bank_rule_family_count(data)
        coverage_axis_count = _hidden_bank_coverage_axis_count(data)
        coverage_complete = _hidden_bank_coverage_complete(data)
        hidden_payloads_generated = _hidden_bank_hidden_payloads_generated(data)
        hidden_challenges_executed = _hidden_bank_hidden_challenges_executed(data)
        layers.append(
            {
                "layer_id": layer_id,
                "source": path.name,
                "route_id": route_id,
                "layer_tier": _hidden_bank_layer_tier(
                    layer_id=layer_id,
                    route_id=route_id,
                    rule_family_count=rule_family_count,
                    coverage_complete=coverage_complete,
                    hidden_payloads_generated=hidden_payloads_generated,
                    hidden_challenges_executed=hidden_challenges_executed,
                ),
                "rule_family_count": rule_family_count,
                "coverage_axis_count": coverage_axis_count,
                "coverage_complete": coverage_complete,
                "hidden_payloads_generated": hidden_payloads_generated,
                "hidden_challenges_executed": hidden_challenges_executed,
                "claim_boundary": data.get("claim_boundary"),
            }
        )
    synthesis = _read_json(root / "ptcg_hidden_bank_design_rule_synthesis_result_20260601.json")
    if isinstance(synthesis, dict):
        for item in synthesis.get("rule_family_matrix", []):
            layers.append(
                {
                    "layer_id": str(item.get("rule_family", "hidden_bank_rule_family")),
                    "source": "ptcg_hidden_bank_design_rule_synthesis_result_20260601.json",
                    "route_id": None,
                    "layer_tier": "generic_rule_family_descriptor",
                    "rule_family_count": 1,
                    "coverage_axis_count": int(item.get("example_axis_count", 0) or 0),
                    "coverage_complete": True,
                    "hidden_payloads_generated": 0,
                    "hidden_challenges_executed": 0,
                    "claim_boundary": synthesis.get("claim_boundary"),
                }
            )
    return sorted(layers, key=lambda item: item["layer_id"])


def _hidden_bank_route_id(data: dict[str, Any]) -> str | None:
    route_id = data.get("route") or data.get("route_id")
    if isinstance(route_id, str):
        return route_id
    target_routes = data.get("target_routes")
    if isinstance(target_routes, list) and len(target_routes) == 1:
        only_route = target_routes[0]
        if isinstance(only_route, str):
            return only_route
    return None


def _hidden_bank_rule_family_count(data: dict[str, Any]) -> int:
    direct = data.get("rule_family_count")
    if isinstance(direct, int):
        return direct
    aggregate = data.get("aggregate_summary", {})
    if isinstance(aggregate, dict):
        for key in ("public_family_count", "rule_family_count"):
            value = aggregate.get(key)
            if isinstance(value, int):
                return value
    coverage = data.get("coverage_summary", {})
    if isinstance(coverage, dict):
        value = coverage.get("covered_rule_families")
        if isinstance(value, int):
            return value
    for key in ("family_matrix", "covered_public_rule_families"):
        value = data.get(key)
        if isinstance(value, list | dict):
            return len(value)
    return 0


def _hidden_bank_coverage_axis_count(data: dict[str, Any]) -> int:
    direct = data.get("coverage_axis_count")
    if isinstance(direct, int):
        return direct
    aggregate = data.get("aggregate_summary", {})
    if isinstance(aggregate, dict):
        value = aggregate.get("total_required_axis_count")
        if isinstance(value, int):
            return value
    coverage = data.get("coverage_summary", {})
    if isinstance(coverage, dict):
        value = coverage.get("covered_axes_total")
        if isinstance(value, int):
            return value
    family_matrix = data.get("family_matrix")
    if isinstance(family_matrix, list):
        return sum(
            item.get("axis_count", 0)
            for item in family_matrix
            if isinstance(item, dict) and isinstance(item.get("axis_count", 0), int)
        )
    return 0


def _hidden_bank_coverage_complete(data: dict[str, Any]) -> bool:
    direct = data.get("coverage_complete")
    if isinstance(direct, bool):
        return direct
    missing_by_route = data.get("missing_required_axes_by_route")
    if isinstance(missing_by_route, dict):
        return not missing_by_route
    coverage = data.get("coverage_summary", {})
    if isinstance(coverage, dict):
        missing = coverage.get("missing_required_axes")
        if isinstance(missing, list):
            return not missing
        required = coverage.get("required_rule_families")
        covered = coverage.get("covered_rule_families")
        if isinstance(required, int) and isinstance(covered, int):
            return covered >= required
    aggregate = data.get("aggregate_summary", {})
    if isinstance(aggregate, dict):
        missing = aggregate.get("total_missing_axis_count")
        if isinstance(missing, int):
            return missing == 0
    return False


def _hidden_bank_hidden_payloads_generated(data: dict[str, Any]) -> int:
    direct = data.get("hidden_payloads_generated")
    if isinstance(direct, int):
        return direct
    coverage = data.get("coverage_summary", {})
    if isinstance(coverage, dict) and isinstance(coverage.get("hidden_payloads_generated"), int):
        return coverage["hidden_payloads_generated"]
    owner_policy = data.get("owner_payload_policy", {})
    if isinstance(owner_policy, dict):
        generated = owner_policy.get("concrete_hidden_payloads_generated_in_repo")
        if isinstance(generated, bool):
            return 0 if not generated else 1
    return 0


def _hidden_bank_hidden_challenges_executed(data: dict[str, Any]) -> int:
    direct = data.get("hidden_challenges_executed")
    if isinstance(direct, int):
        return direct
    coverage = data.get("coverage_summary", {})
    if isinstance(coverage, dict) and isinstance(coverage.get("hidden_challenges_executed"), int):
        return coverage["hidden_challenges_executed"]
    aggregate = data.get("aggregate_summary", {})
    if isinstance(aggregate, dict):
        opened = aggregate.get("hidden_challenge_execution_opened")
        if isinstance(opened, bool):
            return 0 if not opened else 1
    return 0


def _hidden_bank_layer_tier(
    *,
    layer_id: str,
    route_id: str | None,
    rule_family_count: int,
    coverage_complete: bool,
    hidden_payloads_generated: int,
    hidden_challenges_executed: int,
) -> str:
    lowered = layer_id.lower()
    if "rework_required" in lowered:
        return "incomplete_or_rework_required_layer"
    if (
        route_id
        and rule_family_count > 0
        and coverage_complete
        and hidden_payloads_generated == 0
        and hidden_challenges_executed == 0
    ):
        return "complete_public_rule_layer"
    if rule_family_count > 0 and coverage_complete:
        return "generic_rule_family_descriptor"
    return "incomplete_or_rework_required_layer"


def _build_failure_sentinels(
    architecture: ConstructArchitecture,
    root: Path | None,
) -> list[dict[str, Any]]:
    sentinels = [
        {
            "sentinel_id": node.id,
            "source": "local_failure_bank",
            "reason": "negative-control route preserved to block false merge or status escalation",
            "promotion_allowed": False,
        }
        for node in architecture.by_layer("failure_bank")
    ]
    if root and root.exists():
        for path in sorted(root.glob("*failure_bank*.json")):
            sentinels.append(
                {
                    "sentinel_id": path.stem,
                    "source": path.name,
                    "reason": "HCTM failure-bank governance asset",
                    "promotion_allowed": False,
                }
            )
    return sentinels


def _build_next_exploration_directions() -> list[dict[str, Any]]:
    directions = []
    for direction in LOW_OVERLAP_EXPLORATION_DIRECTIONS:
        profile = LOW_OVERLAP_EXPLORATION_PROFILES[direction]
        directions.append(
            {
                "direction_id": direction,
                "status": "idea_only_not_route_opened",
                "entry_gate": "duplicate_boundary_search_before_any_spec",
                "nearby_constructs": list(profile["nearby_constructs"]),
                "boundary_warning": profile["boundary_warning"],
                "required_first_outputs": [
                    "duplicate_search_json_md",
                    "budget_checkpoint_json_md",
                    "preconstruct_scout_spec_json",
                ],
                "max_internal_status": "candidate_only_after_full_falsifier_first_pipeline",
            }
        )
    return directions


def _community_id_from_layer(layer_id: str) -> str:
    stem = layer_id
    if "_" in stem and stem[0] in {"L", "B"} and stem[1:2].isdigit():
        stem = stem.split("_", 1)[1]
    return stem.lower()


def _extract_route_ids(value: Any, allowed_route_ids: set[str]) -> set[str]:
    route_ids: set[str] = set()
    if isinstance(value, str):
        if value in allowed_route_ids:
            route_ids.add(value)
    elif isinstance(value, dict):
        for child in value.values():
            route_ids.update(_extract_route_ids(child, allowed_route_ids))
    elif isinstance(value, list | tuple):
        for child in value:
            route_ids.update(_extract_route_ids(child, allowed_route_ids))
    return route_ids


def _hctm_candidate_ids(
    root: Path | None,
    architecture: ConstructArchitecture,
) -> set[str]:
    if root is None or not root.exists():
        return set()
    architecture_ids = {node.id for node in architecture.nodes}
    route_ids = set()
    for path in sorted(root.glob("*formal_candidate_review_decision*.json")):
        data = _read_json(path)
        if not isinstance(data, dict):
            continue
        route_id = data.get("route_id") or data.get("construct_id") or data.get("candidate_id")
        if (
            isinstance(route_id, str)
            and route_id not in architecture_ids
            and data.get("status_granted") == "candidate"
        ):
            route_ids.add(route_id)
    return route_ids


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


__all__ = [
    "ATLAS_BOUNDARIES",
    "CAGIConstructAtlasReport",
    "LOW_OVERLAP_EXPLORATION_DIRECTIONS",
    "run_c_agi_construct_atlas",
]
