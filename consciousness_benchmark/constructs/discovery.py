from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from consciousness_benchmark.constructs.architecture import all_construct_architecture
from consciousness_benchmark.constructs.construct_runtime import (
    executable_chain_ids,
    run_construct_capability_layer,
)
from consciousness_benchmark.constructs.mind_runtime import discover_construct_compositions


DEFAULT_HCTM_AUDIT_ASSETS_DIR = Path("D:/ai/20260422 HCTM/configs/audit_assets")
HCTM_AUDIT_ASSETS_ENV_VAR = "C_AGI_HCTM_AUDIT_ASSETS_DIR"
RECOMMENDED_REWORK_PRECONSTRUCT_ID = (
    "preconstruct_self_monitoring_repair_bridge_"
    "identity_temporal_self_attention_control_metacognitive_repair_control"
)
COMPOSITION_SUMMARY_LIMIT = 20

DISCOVERY_BOUNDARIES = (
    "review_only_discovery",
    "no_auto_registration",
    "no_formal_construct_promotion",
    "formal_promotion_requires_l3",
    "no_background_self_execution",
    "no_source_registry_mutation",
)


@dataclass(frozen=True)
class CAGIConstructDiscoveryReport:
    chain_reports: tuple[dict[str, Any], ...]
    dynamic_preconstructs: tuple[dict[str, Any], ...]
    composition_candidates: tuple[dict[str, Any], ...]
    hctm_candidate_discoveries: tuple[dict[str, Any], ...]
    failed_chains: tuple[dict[str, Any], ...]
    hctm_audit_assets_dir: str | None
    boundaries: tuple[str, ...] = DISCOVERY_BOUNDARIES

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "consciousness_benchmark.c_agi_construct_discovery.v1",
            "mode": "bounded_full_speed_local_discovery",
            "counts": {
                "chains_run": len(self.chain_reports),
                "productive_chains": len(
                    [
                        item
                        for item in self.chain_reports
                        if item.get("chain_productivity") == "productive_nonempty"
                    ]
                ),
                "expected_empty_noop_chains": len(
                    [
                        item
                        for item in self.chain_reports
                        if item.get("chain_productivity") == "expected_empty_safe_noop"
                    ]
                ),
                "failed_chains": len(self.failed_chains),
                "dynamic_preconstructs": len(self.dynamic_preconstructs),
                "dynamic_preconstruct_families": len(self.dynamic_preconstruct_families()),
                "composition_candidates": len(self.composition_candidates),
                "hctm_candidate_discoveries": len(self.hctm_candidate_discoveries),
            },
            "chain_reports": [dict(item) for item in self.chain_reports],
            "dynamic_preconstructs": [
                dict(item) for item in self.dynamic_preconstructs
            ],
            "dynamic_preconstruct_families": self.dynamic_preconstruct_families(),
            "recommended_rework": self.recommended_rework(),
            "composition_candidates": [
                dict(item) for item in self.composition_candidates
            ],
            "hctm_candidate_discoveries": [
                dict(item) for item in self.hctm_candidate_discoveries
            ],
            "failed_chains": [dict(item) for item in self.failed_chains],
            "hctm_audit_assets_dir": self.hctm_audit_assets_dir,
            "boundaries": list(self.boundaries),
            "governance": {
                "codex_preselection_allowed": True,
                "formal_promotion_allowed": False,
                "can_self_register": False,
                "source_registry_mutation_allowed": False,
                "required_formal_gate": "L3 external-owner validation",
            },
            "claim_boundary": (
                "full-speed discovery means maximum local review-only coverage; "
                "it does not auto-register constructs, mutate registries, or claim "
                "subjective consciousness"
            ),
        }

    def summary_markdown(self) -> str:
        data = self.to_dict()
        lines = [
            "# C-AGI Construct Discovery",
            "",
            f"- Mode: {data['mode']}",
            f"- Chains run: {data['counts']['chains_run']}",
            f"- Productive/nonempty chains: {data['counts']['productive_chains']}",
            f"- Expected empty safe no-op chains: {data['counts']['expected_empty_noop_chains']}",
            f"- Failed chains: {data['counts']['failed_chains']}",
            f"- Dynamic preconstructs: {data['counts']['dynamic_preconstructs']}",
            f"- Dynamic preconstruct families: {data['counts']['dynamic_preconstruct_families']}",
            f"- Composition candidates: {data['counts']['composition_candidates']}",
            f"- HCTM candidate discoveries: {data['counts']['hctm_candidate_discoveries']}",
            "- Interpretation: review-only autonomous discovery scan, not a formal candidate registration batch",
            f"- Boundaries: {', '.join(self.boundaries)}",
            "",
            "## Recommended Rework",
        ]
        recommendation = data["recommended_rework"]
        if recommendation:
            lines.append(
                f"- `{recommendation['preconstruct_id']}`: {recommendation['rationale']}"
            )
        else:
            lines.append("- No dynamic preconstruct met the rework recommendation rule.")
        lines.extend(
            [
                "",
                "## Dynamic Preconstruct Families",
            ]
        )
        for family in data["dynamic_preconstruct_families"]:
            lines.append(
                f"- `{family['family_id']}`: members={family['member_count']} "
                f"max_strength={family['max_strength']} recommended={family['recommended_for_rework']}"
            )
        lines.extend(
            [
                "",
            "## Dynamic Preconstructs",
            ]
        )
        for item in self.dynamic_preconstructs:
            lines.append(
                f"- `{item['preconstruct_id']}`: strength={item['max_strength']} "
                f"chains={', '.join(item['observed_chains'])}"
            )
        lines.extend(["", "## HCTM Candidate Discoveries"])
        for item in self.hctm_candidate_discoveries:
            lines.append(
                f"- `{item['route_id']}`: {item.get('status_granted', 'candidate')} "
                f"assets={len(item.get('asset_files', []))}"
            )
        lines.extend(
            [
                "",
                "## Composition Candidates",
                (
                    f"Showing first {min(COMPOSITION_SUMMARY_LIMIT, len(self.composition_candidates))}; "
                    f"full {len(self.composition_candidates)} in JSON. Treat as idea bank / near-miss raw material."
                ),
            ]
        )
        for item in self.composition_candidates[:COMPOSITION_SUMMARY_LIMIT]:
            lines.append(
                f"- `{item['candidate_id']}`: {item['discovery_level']}"
            )
        if self.failed_chains:
            lines.extend(["", "## Failed Chains"])
            for item in self.failed_chains:
                lines.append(
                    f"- `{item['chain_id']}`: {item['error_type']} {item['error']}"
                )
        return "\n".join(lines)

    def dynamic_preconstruct_families(self) -> list[dict[str, Any]]:
        families: dict[str, dict[str, Any]] = {}
        for item in self.dynamic_preconstructs:
            family_id = _dynamic_family_id(item)
            record = families.setdefault(
                family_id,
                {
                    "family_id": family_id,
                    "member_count": 0,
                    "member_preconstruct_ids": [],
                    "max_strength": 0.0,
                    "source_constructs": [],
                    "recommended_for_rework": False,
                    "governance_status": "family_review_required_before_route_opening",
                },
            )
            record["member_count"] += 1
            record["member_preconstruct_ids"].append(item["preconstruct_id"])
            record["max_strength"] = round(
                max(record["max_strength"], float(item.get("max_strength", 0.0))),
                4,
            )
            for construct_id in item.get("source_constructs", []):
                if construct_id not in record["source_constructs"]:
                    record["source_constructs"].append(construct_id)
            if item["preconstruct_id"] == RECOMMENDED_REWORK_PRECONSTRUCT_ID:
                record["recommended_for_rework"] = True
        return sorted(
            families.values(),
            key=lambda item: (-item["max_strength"], item["family_id"]),
        )

    def recommended_rework(self) -> dict[str, Any] | None:
        for item in self.dynamic_preconstructs:
            if item["preconstruct_id"] != RECOMMENDED_REWORK_PRECONSTRUCT_ID:
                continue
            return {
                "preconstruct_id": item["preconstruct_id"],
                "family_id": _dynamic_family_id(item),
                "rationale": (
                    "best first rework because it bridges identity_temporal_self, "
                    "attention_control, and metacognitive_repair_control; related "
                    "to repair/core-periphery grammar and not merely a duplicate "
                    "hierarchical dependency closure"
                ),
                "next_step": "manual rework review with duplicate and boundary matrix",
                "formal_promotion_allowed": False,
                "required_formal_gate": "L3 external-owner validation",
            }
        return None


def run_c_agi_construct_discovery(
    *,
    chain_ids: tuple[str, ...] | list[str] | None = None,
    hctm_audit_assets_dir: str | Path | None = None,
    composition_limit: int = 50,
) -> CAGIConstructDiscoveryReport:
    selected_chain_ids = tuple(chain_ids) if chain_ids is not None else executable_chain_ids()
    chain_reports: list[dict[str, Any]] = []
    failed_chains: list[dict[str, Any]] = []
    dynamic_by_id: dict[str, dict[str, Any]] = {}
    for chain_id in selected_chain_ids:
        try:
            report = run_construct_capability_layer(chain_id).to_dict()
        except Exception as exc:  # pragma: no cover - retained for field diagnostics.
            failed_chains.append(
                {
                    "chain_id": chain_id,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            continue
        emergence = report.get("emergence_system", {})
        discovery = report.get("preconstruct_discovery", {})
        chain_reports.append(
            {
                "chain_id": chain_id,
                "runtime_result_count": len(report.get("runtime_report", {}).get("results", [])),
                "pattern_count": len(emergence.get("patterns", [])),
                "generated_spec_count": emergence.get("generated_spec_count", 0),
                "preselected_preconstruct_count": discovery.get(
                    "preselected_preconstruct_count",
                    0,
                ),
                "formal_promotion_allowed": discovery.get(
                    "formal_promotion_allowed",
                    False,
                ),
                "source_registry_mutation_allowed": discovery.get(
                    "source_registry_mutation_allowed",
                    False,
                ),
                "chain_productivity": _chain_productivity(report),
            }
        )
        for hypothesis in discovery.get("preconstruct_hypotheses", []):
            _merge_dynamic_hypothesis(dynamic_by_id, chain_id, hypothesis)

    dynamic_preconstructs = tuple(
        sorted(
            dynamic_by_id.values(),
            key=lambda item: (-item["max_strength"], item["preconstruct_id"]),
        )
    )
    composition_candidates = tuple(
        candidate.to_dict()
        for candidate in discover_construct_compositions(limit=composition_limit)
    )
    hctm_path = _resolve_hctm_audit_assets_dir(hctm_audit_assets_dir)
    hctm_candidates = tuple(_scan_hctm_candidate_discoveries(hctm_path))
    return CAGIConstructDiscoveryReport(
        chain_reports=tuple(chain_reports),
        dynamic_preconstructs=dynamic_preconstructs,
        composition_candidates=composition_candidates,
        hctm_candidate_discoveries=hctm_candidates,
        failed_chains=tuple(failed_chains),
        hctm_audit_assets_dir=str(hctm_path) if hctm_path else None,
    )


def _merge_dynamic_hypothesis(
    dynamic_by_id: dict[str, dict[str, Any]],
    chain_id: str,
    hypothesis: dict[str, Any],
) -> None:
    preconstruct_id = str(hypothesis.get("preconstruct_id", "unknown_preconstruct"))
    strength = float(hypothesis.get("strength", 0.0))
    record = dynamic_by_id.setdefault(
        preconstruct_id,
        {
            "preconstruct_id": preconstruct_id,
            "status": hypothesis.get("status", "unknown"),
            "source_constructs": list(hypothesis.get("source_constructs", [])),
            "source_pattern_ids": [],
            "observed_chains": [],
            "max_strength": strength,
            "max_novelty_score": float(hypothesis.get("novelty_score", 0.0)),
            "best_evidence_score": float(hypothesis.get("evidence_score", 0.0)),
            "codex_review": dict(hypothesis.get("codex_review", {})),
            "hard_negative_tests": list(hypothesis.get("hard_negative_tests", [])),
            "relation_matrix_draft": dict(hypothesis.get("relation_matrix_draft", {})),
            "formal_promotion_allowed": False,
            "source_registry_mutation_allowed": False,
            "required_formal_gate": "L3 external-owner validation",
        },
    )
    if chain_id not in record["observed_chains"]:
        record["observed_chains"].append(chain_id)
    source_pattern_id = hypothesis.get("source_pattern_id")
    if source_pattern_id and source_pattern_id not in record["source_pattern_ids"]:
        record["source_pattern_ids"].append(source_pattern_id)
    record["max_strength"] = round(max(record["max_strength"], strength), 4)
    record["max_novelty_score"] = round(
        max(record["max_novelty_score"], float(hypothesis.get("novelty_score", 0.0))),
        4,
    )
    record["best_evidence_score"] = round(
        max(record["best_evidence_score"], float(hypothesis.get("evidence_score", 0.0))),
        4,
    )


def _dynamic_family_id(item: dict[str, Any]) -> str:
    source_pattern_ids = item.get("source_pattern_ids", [])
    first_pattern = str(source_pattern_ids[0]) if source_pattern_ids else ""
    preconstruct_id = str(item.get("preconstruct_id", ""))
    if first_pattern == "hierarchical_dependency_closure" or "hierarchical_dependency_closure" in preconstruct_id:
        return "hierarchical_dependency_closure_family"
    if first_pattern == "self_monitoring_repair_bridge" or "self_monitoring_repair_bridge" in preconstruct_id:
        return "self_monitoring_repair_bridge_family"
    return first_pattern or "unclassified_dynamic_preconstruct_family"


def _chain_productivity(report: dict[str, Any]) -> str:
    runtime_result_count = len(report.get("runtime_report", {}).get("results", []))
    if runtime_result_count == 0:
        return "expected_empty_safe_noop"
    return "productive_nonempty"


def _resolve_hctm_audit_assets_dir(
    explicit_path: str | Path | None,
) -> Path | None:
    if explicit_path is not None:
        return Path(explicit_path)
    env_path = os.environ.get(HCTM_AUDIT_ASSETS_ENV_VAR)
    if env_path:
        return Path(env_path)
    return DEFAULT_HCTM_AUDIT_ASSETS_DIR


def _scan_hctm_candidate_discoveries(root: Path | None) -> list[dict[str, Any]]:
    if root is None or not root.exists():
        return []
    architecture_ids = {node.id for node in all_construct_architecture().nodes}
    discoveries: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob("*formal_candidate_review_decision*.json")):
        data = _read_json(path)
        if not isinstance(data, dict):
            continue
        route_id = data.get("route_id") or data.get("construct_id") or data.get("candidate_id")
        if not isinstance(route_id, str) or route_id in architecture_ids:
            continue
        if data.get("status_granted") != "candidate":
            continue
        discoveries[route_id] = {
            "route_id": route_id,
            "discovery_source": "hctm_audit_assets",
            "status": "hctm_candidate_not_registered_locally",
            "decision": data.get("decision"),
            "status_granted": data.get("status_granted"),
            "status_not_granted": list(data.get("status_not_granted", [])),
            "accepted_narrowed_claim": data.get("accepted_narrowed_claim"),
            "boundary_caveat": data.get("boundary_caveat"),
            "next_required_step": data.get("next_required_step"),
            "claim_boundary": data.get("claim_boundary"),
            "asset_files": [path.name],
            "formal_promotion_allowed": False,
            "source_registry_mutation_allowed": False,
            "required_formal_gate": "L3 external-owner validation",
        }
    for path in sorted(root.glob("*.json")):
        data = _read_json(path)
        if not isinstance(data, dict):
            continue
        route_id = data.get("route_id") or data.get("construct_id") or data.get("candidate_id")
        if route_id in discoveries and path.name not in discoveries[route_id]["asset_files"]:
            discoveries[route_id]["asset_files"].append(path.name)
    return sorted(discoveries.values(), key=lambda item: item["route_id"])


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


__all__ = [
    "CAGIConstructDiscoveryReport",
    "COMPOSITION_SUMMARY_LIMIT",
    "DEFAULT_HCTM_AUDIT_ASSETS_DIR",
    "DISCOVERY_BOUNDARIES",
    "HCTM_AUDIT_ASSETS_ENV_VAR",
    "RECOMMENDED_REWORK_PRECONSTRUCT_ID",
    "run_c_agi_construct_discovery",
]
