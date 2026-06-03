"""Run bounded developmental growth/theory replay rounds and write stability summaries.

This runner executes growth-cycle and consciousness-theory assessment across a
list of seeds and round ids, then writes:

- per-seed growth/theory/gatecheck artifacts (trace manifests and full summaries)
- a combined batch stability summary (`batch_stability_summary.json`)

The workflow is review-only and does not alter construct registries or proposal
state.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any

from consciousness_benchmark import (
    run_consciousness_theory_assessment,
    run_developmental_growth_cycle,
)
from consciousness_benchmark.cli import _run_c_agi_layer_gatebook_check


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "runs" / "exec_20260602_growth_batch"
DEFAULT_GATEBOOK_PATH = ROOT / "docs" / "c_agi_layer_gatebook_20260602.json"
_HEALTH_SUMMARY_SCHEMA = "consciousness_benchmark.growth_development_batch_health.v1"
_HEALTH_GATE_SCHEMA = "consciousness_benchmark.growth_development_batch_health_gate.v1"
_PHASE2_MINING_SCHEMA = "consciousness_benchmark.growth_development_batch_phase2_mining.v1"
DEFAULT_CASE_IDS = (
    "global_workspace",
    "higher_order_self_model",
    "recurrent_processing",
    "predictive_processing",
    "attention_schema",
    "embodied_cognition",
    "autobiographical_continuity",
    "action_ownership",
    "value_regulation",
)
DEFAULT_STAGE_IDS = (
    "initial",
    "early_exploration",
    "midterm_tasking",
    "advanced_social",
    "reflection",
)


def _safe_mean(values: list[float]) -> float | None:
    return round(mean(values), 4) if values else None


def _to_float(value: object) -> float | None:
    if value is None:
        return None
    return float(value)


def _normalize_case_ids(raw_case_ids: list[str] | None) -> tuple[str, ...]:
    if not raw_case_ids:
        return DEFAULT_CASE_IDS
    return tuple(raw_case_ids)


def _normalize_stage_ids(raw_stage_ids: list[str] | None) -> tuple[str, ...]:
    if not raw_stage_ids:
        return DEFAULT_STAGE_IDS
    return tuple(raw_stage_ids)


def _normalize_seed_step(seed_step: int) -> int:
    value = int(seed_step)
    return value if value >= 0 else 0


def _growth_summary(growth: dict[str, Any]) -> dict[str, Any]:
    stage_rows = growth["stage_rows"]
    stage_scores = [float(row["final_score"]) for row in stage_rows if row.get("final_score") is not None]
    phase2 = growth["phase2_analysis"]
    ablation_rows = growth["ablation_results"]
    ablation_deltas = [float(item["final_score_delta"]) for item in ablation_rows]
    return {
        "growth_stage_mean": _safe_mean(stage_scores),
        "growth_stage_max": max(stage_scores) if stage_scores else None,
        "growth_stage_count": len(stage_rows),
        "coactivation_pair_count": len(phase2.get("coactivation_pair_patterns", [])),
        "coactivation_pattern_count": len(phase2.get("coactivation_patterns", [])),
        "temporal_pattern_count": len(phase2.get("temporal_patterns", [])),
        "hierarchical_pattern_count": len(phase2.get("hierarchical_patterns", [])),
        "temporal_sequence_count": len(phase2.get("temporal_sequences", [])),
        "dynamic_constructs": len(phase2.get("dynamic_construct_proposals", [])),
        "growth_ab_sensitive": sum(
            1 for item in ablation_rows if item.get("sensitive_drop")
        ),
        "growth_ab_mean_delta": _safe_mean(ablation_deltas) if ablation_deltas else None,
        "growth_ab_delta_max": max(ablation_deltas) if ablation_deltas else None,
    }


def _theory_summary(theory: dict[str, Any]) -> dict[str, Any]:
    analysis = theory["analysis"]
    rows = theory["consciousness_evidence_matrix"]
    return {
        "theory_pass_count": int(analysis["matrix_pass_count"]),
        "theory_review_required_count": int(analysis["matrix_review_count"]),
        "theory_not_run_count": int(analysis["matrix_not_run_count"]),
        "theory_phase2_patterns": len(analysis.get("phase2_patterns", [])),
        "theory_matrix_row_count": len(rows),
        "theory_mean_ablation_delta": _to_float(
            analysis["mean_ablation_delta"] if analysis["mean_ablation_delta"] != 0 else 0.0
        ),
    }


def _gate_summary(gate_result: dict[str, Any] | None) -> tuple[int, int, int]:
    if gate_result is None:
        return (0, 0, 0)
    counts = gate_result.get("check_counts", {})
    return (
        int(counts.get("passed", 0)),
        int(counts.get("failed", 0)),
        int(counts.get("total", 0)),
    )


def _float_or_none(value: float | None, fallback: float | None = None) -> float | None:
    if value is None:
        return fallback
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _aggregate_means(rows: list[dict[str, Any]], key: str) -> float | None:
    vals = [_to_float(row.get(key)) for row in rows]
    vals = [v for v in vals if v is not None]
    return _safe_mean(vals)


def _build_metric_trajectory(round_summaries: list[dict[str, Any]], key: str) -> list[float]:
    values: list[float] = []
    for summary in round_summaries:
        raw = summary["aggregate_mean"].get(key)
        if isinstance(raw, (int, float)):
            values.append(float(raw))
        elif raw is None:
            values.append(0.0)
        else:
            values.append(_float_or_none(raw, 0.0) or 0.0)
    return values


def _build_stability_summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {
            "sample_count": 0,
            "min": 0.0,
            "max": 0.0,
            "mean": 0.0,
            "first": 0.0,
            "last": 0.0,
            "last_minus_first": 0.0,
        }
    return {
        "sample_count": len(values),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "mean": round(sum(values) / len(values), 4),
        "first": round(values[0], 4),
        "last": round(values[-1], 4),
        "last_minus_first": round(values[-1] - values[0], 4),
    }


def _metric_sign(value: float, eps: float = 1e-9) -> int:
    if value > eps:
        return 1
    if value < -eps:
        return -1
    return 0


def _metric_trajectory_summary(values: list[float], *, eps: float = 1e-9) -> dict[str, Any]:
    if not values:
        return {
            "round_count": 0,
            "trajectory": [],
            "trend_direction": "not_applicable",
            "is_monotonic": False,
            "is_oscillatory": False,
            "regression_detected": False,
            "rebound_count": 0,
            "step_range": 0.0,
            "max_step": 0.0,
            "min_step": 0.0,
            "max_drop": 0.0,
            "first": 0.0,
            "last": 0.0,
            "delta": 0.0,
        }

    steps = [values[i] - values[i - 1] for i in range(1, len(values))]
    non_zero_steps = [step for step in steps if abs(step) > eps]
    signs = [_metric_sign(step, eps=eps) for step in non_zero_steps]
    rebound_count = 0
    for idx in range(1, len(signs)):
        if signs[idx] != 0 and signs[idx - 1] != 0 and signs[idx] != signs[idx - 1]:
            rebound_count += 1

    direction = "flat"
    if non_zero_steps:
        if all(step > eps for step in non_zero_steps):
            direction = "increasing"
        elif all(step < -eps for step in non_zero_steps):
            direction = "decreasing"
        else:
            direction = "non_monotonic"

    regression_detected = any(step < -eps for step in non_zero_steps)
    is_oscillatory = rebound_count > 0
    max_step = max(steps) if steps else 0.0
    min_step = min(steps) if steps else 0.0
    max_drop = abs(min_step) if min_step < 0 else 0.0
    first = float(values[0])
    last = float(values[-1])
    return {
        "round_count": len(values),
        "trajectory": [round(value, 4) for value in values],
        "trend_direction": direction,
        "is_monotonic": direction in {"increasing", "decreasing", "flat"},
        "is_oscillatory": is_oscillatory,
        "regression_detected": regression_detected,
        "rebound_count": rebound_count,
        "step_range": round(max(values) - min(values), 4),
        "max_step": round(max_step, 4),
        "min_step": round(min_step, 4),
        "max_drop": round(max_drop, 4),
        "first": round(first, 4),
        "last": round(last, 4),
        "delta": round(last - first, 4),
        "volatility_ratio": round(
            (max_step - min_step) / max(1.0, abs(first), abs(last)),
            4,
        )
        if len(values) > 1
        else 0.0,
    }


def _normalize_construct_set(values: Any) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple, set)):
        return ()
    cleaned = sorted({str(value) for value in values if isinstance(value, str) and value.strip()})
    return tuple(cleaned)


def _safe_pattern_rows(raw_patterns: object) -> tuple[dict[str, Any], ...]:
    """Normalize pattern-like rows into JSON-serializable tuple of dicts."""
    if not isinstance(raw_patterns, (list, tuple)):
        return ()
    normalized: list[dict[str, Any]] = []
    for entry in raw_patterns:
        if isinstance(entry, dict):
            normalized.append(entry)
    return tuple(normalized)


def _safe_signature(value: Any) -> str:
    """Create a deterministic fingerprint for a pattern-like mapping."""
    if not isinstance(value, dict):
        return str(value)
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def _aggregate_phase2_mining(
    growth_phase2_rows: list[dict[str, Any]],
    *,
    top_k_patterns: int = 20,
) -> dict[str, Any]:
    """Aggregate phase-2 pattern families across the full batch."""
    pattern_groups: dict[str, dict[str, Any]] = {
        "coactivation": {},
        "temporal": {},
        "hierarchical": {},
        "temporal_sequence": {},
    }
    proposal_counter: dict[str, int] = {}
    proposal_by_pattern: dict[str, set[str]] = {}
    construct_involvement: dict[str, int] = {}

    for row in growth_phase2_rows:
        if not isinstance(row, dict):
            continue
        for pattern_type in ("coactivation_patterns", "temporal_patterns", "hierarchical_patterns"):
            mapped_key = {
                "coactivation_patterns": "coactivation",
                "temporal_patterns": "temporal",
                "hierarchical_patterns": "hierarchical",
            }[pattern_type]
            raw_patterns = row.get(pattern_type, ())
            if not isinstance(raw_patterns, (list, tuple)):
                raw_patterns = ()
            for pattern in raw_patterns:
                if not isinstance(pattern, dict):
                    continue
                pattern_id = str(pattern.get("pattern_id") or f"unknown_{mapped_key}")
                construct_set = _normalize_construct_set(pattern.get("constructs", ()))
                source_key = f"{pattern_id}:{_safe_signature(pattern.get('evidence',''))}:{construct_set}"
                entry = pattern_groups[mapped_key].setdefault(
                    source_key,
                    {
                        "pattern_type": mapped_key,
                        "pattern_id": pattern_id,
                        "occurrence_count": 0,
                        "max_strength": 0.0,
                        "sum_strength": 0.0,
                        "constructs": [],
                    },
                )
                entry["occurrence_count"] += 1
                strength = _to_float(pattern.get("strength")) or 0.0
                entry["max_strength"] = max(entry["max_strength"], strength)
                entry["sum_strength"] += strength
                for construct in construct_set:
                    construct_involvement[construct] = construct_involvement.get(construct, 0) + 1
                if construct_set and construct_set[0] not in entry["constructs"]:
                    entry["constructs"] = list(construct_set)

        raw_temporal_sequences = row.get("temporal_sequences", ())
        if not isinstance(raw_temporal_sequences, (list, tuple)):
            raw_temporal_sequences = ()
        for pattern in raw_temporal_sequences:
            if not isinstance(pattern, dict):
                continue
            pattern_id = str(pattern.get("pattern_id") or "unknown_temporal_sequence")
            source_stage = str(pattern.get("source_stage") or "")
            target_stage = str(pattern.get("target_stage") or "")
            transition_key = f"{pattern_id}:{source_stage}->{target_stage}:{_safe_signature(pattern.get('entered_constructs', ())) }"
            entry = pattern_groups["temporal_sequence"].setdefault(
                transition_key,
                {
                    "pattern_type": "temporal_sequence",
                    "pattern_id": pattern_id,
                    "source_stage": source_stage,
                    "target_stage": target_stage,
                    "occurrence_count": 0,
                    "max_strength": 0.0,
                    "sum_strength": 0.0,
                },
            )
            entry["occurrence_count"] += 1
            strength = _to_float(pattern.get("overlap_ratio")) or 0.0
            entry["max_strength"] = max(entry["max_strength"], strength)
            entry["sum_strength"] += strength

        raw_proposals = row.get("dynamic_construct_proposals", ())
        if not isinstance(raw_proposals, (list, tuple)):
            raw_proposals = ()
        for proposal in raw_proposals:
            if not isinstance(proposal, dict):
                continue
            proposal_id = str(proposal.get("generated_construct_id") or "")
            if not proposal_id:
                continue
            proposal_counter[proposal_id] = proposal_counter.get(proposal_id, 0) + 1
            source_pattern_id = str(proposal.get("source_pattern_id") or "unknown")
            linked = proposal_by_pattern.setdefault(source_pattern_id, set())
            linked.add(proposal_id)

    def _summarize(pattern_dict: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        rows = []
        for entry in pattern_dict.values():
            total = entry["occurrence_count"]
            sum_strength = entry["sum_strength"]
            entry = dict(entry)
            entry["mean_strength"] = round(sum_strength / total, 4) if total > 0 else 0.0
            entry["sum_strength"] = round(sum_strength, 4)
            entry["max_strength"] = round(entry["max_strength"], 4)
            entry.pop("sum_strength")
            rows.append(entry)
        rows = sorted(
            rows,
            key=lambda item: (item["occurrence_count"], item.get("max_strength", 0.0)),
            reverse=True,
        )
        return [
            {
                "pattern_type": row["pattern_type"],
                "pattern_id": row["pattern_id"],
                "occurrence_count": int(row["occurrence_count"]),
                "mean_strength": float(row["mean_strength"]),
                "max_strength": float(row["max_strength"]),
                **(
                    {"source_stage": row["source_stage"], "target_stage": row["target_stage"]}
                    if row["pattern_type"] == "temporal_sequence"
                    else {"constructs": row.get("constructs", [])}
                ),
            }
            for row in rows[:top_k_patterns]
        ]

    proposals_sorted = sorted(
        proposal_counter.items(),
        key=lambda item: (item[1], item[0]),
        reverse=True,
    )
    top_dynamic_constructs = [
        {
            "generated_construct_id": construct_id,
            "occurrence_count": int(count),
        }
        for construct_id, count in proposals_sorted[:top_k_patterns]
    ]

    return {
        "schema": _PHASE2_MINING_SCHEMA,
        "pattern_summary": {
            "coactivation_top_patterns": _summarize(pattern_groups["coactivation"]),
            "temporal_top_patterns": _summarize(pattern_groups["temporal"]),
            "hierarchical_top_patterns": _summarize(pattern_groups["hierarchical"]),
            "temporal_sequence_top_patterns": _summarize(pattern_groups["temporal_sequence"]),
        },
        "dynamic_construct_summary": {
            "review_only_dynamic_construct_count": sum(proposal_counter.values()),
            "unique_review_only_dynamic_constructs": len(proposal_counter),
            "top_review_only_dynamic_constructs": top_dynamic_constructs,
            "source_pattern_coverage_count": len(proposal_by_pattern),
            "source_pattern_link_map": {
                pattern_id: sorted(construct_ids)
                for pattern_id, construct_ids in sorted(proposal_by_pattern.items())
            },
        },
        "construct_engagement": {
            "unique_construct_involved_count": len(construct_involvement),
            "construct_occurrence_top": [
                {"construct": construct, "occurrence_count": count}
                for construct, count in sorted(
                    construct_involvement.items(),
                    key=lambda item: (item[1], item[0]),
                    reverse=True,
                )[:top_k_patterns]
            ],
        },
        "batch_coverage": {
            "rows_with_phase2_data": len(growth_phase2_rows),
            "rows_with_temporal_sequence": sum(
                1
                for row in growth_phase2_rows
                for _ in [0]
                if isinstance(row.get("temporal_sequences"), (list, tuple))
                and row.get("temporal_sequences")
            ),
            "rows_with_dynamic_constructs": sum(
                1
                for row in growth_phase2_rows
                for _ in [0]
                if isinstance(row.get("dynamic_construct_proposals"), (list, tuple))
                and row.get("dynamic_construct_proposals")
            ),
        },
    }


def _top_trend_metrics(
    metric_summaries: dict[str, dict[str, Any]], *, top_n: int = 5
) -> list[str]:
    ranked = sorted(
        metric_summaries.items(),
        key=lambda item: abs(item[1]["delta"]),
        reverse=True,
    )
    return [name for name, _ in ranked[:top_n]]


def _build_health_summary(
    trajectory_summary: dict[str, Any] | None,
    aggregate_mean: dict[str, Any],
) -> dict[str, Any]:
    """Build a deterministic, review-oriented batch health digest."""
    if trajectory_summary is None:
        return {
            "schema": _HEALTH_SUMMARY_SCHEMA,
            "applicable": False,
            "health_status": "single_round_insufficient",
            "has_stable_growth": False,
            "has_evidence_regression": False,
            "dominant_trend_keys": [],
            "dominant_metric_count": 0,
            "health_score": 0.0,
            "risk_level": "high",
            "risk_reason": "trajectory analysis requires at least 2 rounds.",
            "theory_coverage": 0.0,
            "trajectory_rounds": 1,
            "oscillatory_rate": 0.0,
            "regression_rate": 0.0,
        }

    metric_summaries = trajectory_summary["metric_summaries"]
    round_count = int(trajectory_summary.get("round_count", 0))
    growth_summary = metric_summaries.get("growth_stage_mean", {})

    has_stable_growth = False
    if round_count >= 2 and growth_summary:
        trend_direction = growth_summary.get("trend_direction")
        has_stable_growth = (
            trend_direction in {"increasing", "flat"}
            and growth_summary.get("rebound_count", 0) <= 1
            and not growth_summary.get("regression_detected", False)
        )

    oscillatory_rate = float(trajectory_summary.get("summary", {}).get("oscillatory_rate", 0.0))
    regression_rate = float(trajectory_summary.get("summary", {}).get("regression_rate", 0.0))

    dominant_trend_keys = _top_trend_metrics(metric_summaries)
    dominant_metric_count = len(dominant_trend_keys)

    theory_pass_count = float(aggregate_mean.get("theory_pass_count", 0.0))
    theory_review_required = float(aggregate_mean.get("theory_review_required_count", 0.0))
    theory_not_run = float(aggregate_mean.get("theory_not_run_count", 0.0))
    theory_total = theory_pass_count + theory_review_required + theory_not_run
    theory_coverage = theory_pass_count / theory_total if theory_total > 0 else 0.0

    health_score = max(
        0.0,
        min(1.0, 1.0 - 0.65 * oscillatory_rate - 0.9 * regression_rate),
    )

    if health_score >= 0.85:
        risk_level = "low"
    elif health_score >= 0.65:
        risk_level = "medium"
    else:
        risk_level = "high"

    return {
        "schema": _HEALTH_SUMMARY_SCHEMA,
        "applicable": True,
        "health_status": "pass" if has_stable_growth and oscillatory_rate <= 0.35 else "monitor",
        "has_stable_growth": bool(has_stable_growth),
        "has_evidence_regression": bool(trajectory_summary.get("regression_metrics")),
        "dominant_trend_keys": dominant_trend_keys,
        "dominant_metric_count": dominant_metric_count,
        "health_score": round(health_score, 4),
        "risk_level": risk_level,
        "risk_reason": (
            "oscillatory or regression pressure exceeded thresholds"
            if oscillatory_rate > 0.35 or regression_rate > 0.35
            else "none"
        ),
        "theory_coverage": round(theory_coverage, 4),
        "trajectory_rounds": round_count,
        "oscillatory_rate": oscillatory_rate,
        "regression_rate": regression_rate,
    }


def _evaluate_health_gate(
    health_summary: dict[str, Any],
    phase2_mining_summary: dict[str, Any] | None = None,
    *,
    require_health_pass: bool = False,
    min_health_score: float | None = None,
    max_oscillation_rate: float | None = None,
    max_regression_rate: float | None = None,
    min_phase2_unique_constructs: int | None = None,
    min_phase2_dynamic_construct_count: int | None = None,
    min_phase2_rows_with_phase2_data: int | None = None,
    min_phase2_temporal_sequence_ratio: float | None = None,
    min_phase2_dynamic_ratio: float | None = None,
) -> dict[str, Any]:
    """Evaluate optional policy gates on the produced batch health summary."""
    health_score = _to_float(health_summary.get("health_score")) or 0.0
    oscillatory_rate = _to_float(health_summary.get("oscillatory_rate")) or 0.0
    regression_rate = _to_float(health_summary.get("regression_rate")) or 0.0
    health_status = str(health_summary.get("health_status") or "")
    applicable = bool(health_summary.get("applicable"))
    phase2_summary = phase2_mining_summary or {}
    phase2_coverage = phase2_summary.get("batch_coverage", {})
    phase2_constructs = phase2_summary.get("construct_engagement", {})
    phase2_dynamic = phase2_summary.get("dynamic_construct_summary", {})
    phase2_rows_with_phase2_data = int(phase2_coverage.get("rows_with_phase2_data", 0) or 0)
    phase2_rows_with_temporal_sequence = int(
        phase2_coverage.get("rows_with_temporal_sequence", 0) or 0
    )
    phase2_rows_with_dynamic_constructs = int(
        phase2_coverage.get("rows_with_dynamic_constructs", 0) or 0
    )
    phase2_unique_construct_count = int(
        phase2_constructs.get("unique_construct_involved_count", 0) or 0
    )
    phase2_dynamic_construct_count = int(
        phase2_dynamic.get("review_only_dynamic_construct_count", 0) or 0
    )
    phase2_temporal_sequence_ratio = (
        phase2_rows_with_temporal_sequence / phase2_rows_with_phase2_data
        if phase2_rows_with_phase2_data > 0
        else 0.0
    )
    phase2_dynamic_ratio = (
        phase2_rows_with_dynamic_constructs / phase2_rows_with_phase2_data
        if phase2_rows_with_phase2_data > 0
        else 0.0
    )

    gate_enabled = bool(
        require_health_pass
        or min_health_score is not None
        or max_oscillation_rate is not None
        or max_regression_rate is not None
        or min_phase2_unique_constructs is not None
        or min_phase2_dynamic_construct_count is not None
        or min_phase2_rows_with_phase2_data is not None
        or min_phase2_temporal_sequence_ratio is not None
        or min_phase2_dynamic_ratio is not None
    )
    violations: list[str] = []

    if not applicable:
        violations.append("health summary is not applicable; at least 2 rounds are required.")
    else:
        if require_health_pass and health_status != "pass":
            violations.append("health_status is not pass.")
        if min_health_score is not None and (health_score is None or health_score < min_health_score):
            violations.append(
                f"health_score {health_score} < threshold {min_health_score}."
            )
        if max_oscillation_rate is not None and (
            oscillatory_rate is None or oscillatory_rate > max_oscillation_rate
        ):
            violations.append(
                f"oscillatory_rate {oscillatory_rate} > threshold {max_oscillation_rate}."
            )
        if max_regression_rate is not None and (
            regression_rate is None or regression_rate > max_regression_rate
        ):
            violations.append(
                f"regression_rate {regression_rate} > threshold {max_regression_rate}."
            )
    if min_phase2_unique_constructs is not None and phase2_rows_with_phase2_data == 0:
        violations.append(
            "phase2 summary is not available; cannot enforce unique construct threshold."
        )
    elif min_phase2_unique_constructs is not None:
        if phase2_unique_construct_count < min_phase2_unique_constructs:
            violations.append(
                f"phase2_unique_construct_count {phase2_unique_construct_count} < threshold "
                f"{min_phase2_unique_constructs}."
            )
    if (
        min_phase2_dynamic_construct_count is not None
        and phase2_rows_with_dynamic_constructs is not None
    ):
        if phase2_dynamic_construct_count < min_phase2_dynamic_construct_count:
            violations.append(
                f"phase2_dynamic_construct_count {phase2_dynamic_construct_count} < threshold "
                f"{min_phase2_dynamic_construct_count}."
            )
    if min_phase2_rows_with_phase2_data is not None:
        if phase2_rows_with_phase2_data < min_phase2_rows_with_phase2_data:
            violations.append(
                "phase2_rows_with_phase2_data "
                f"{phase2_rows_with_phase2_data} < threshold {min_phase2_rows_with_phase2_data}."
            )
    if min_phase2_temporal_sequence_ratio is not None:
        if phase2_temporal_sequence_ratio < min_phase2_temporal_sequence_ratio:
            violations.append(
                f"phase2_temporal_sequence_ratio {phase2_temporal_sequence_ratio:.4f} "
                f"< threshold {min_phase2_temporal_sequence_ratio:.4f}."
            )
    if min_phase2_dynamic_ratio is not None:
        if phase2_dynamic_ratio < min_phase2_dynamic_ratio:
            violations.append(
                f"phase2_dynamic_ratio {phase2_dynamic_ratio:.4f} "
                f"< threshold {min_phase2_dynamic_ratio:.4f}."
            )

    return {
        "schema": _HEALTH_GATE_SCHEMA,
        "enabled": gate_enabled,
        "passed": len(violations) == 0,
        "applicable": applicable,
        "requirements": {
            "require_health_pass": require_health_pass,
            "min_health_score": min_health_score,
            "max_oscillation_rate": max_oscillation_rate,
            "max_regression_rate": max_regression_rate,
            "min_phase2_unique_constructs": min_phase2_unique_constructs,
            "min_phase2_dynamic_construct_count": min_phase2_dynamic_construct_count,
            "min_phase2_rows_with_phase2_data": min_phase2_rows_with_phase2_data,
            "min_phase2_temporal_sequence_ratio": min_phase2_temporal_sequence_ratio,
            "min_phase2_dynamic_ratio": min_phase2_dynamic_ratio,
        },
        "violations": violations,
        "observed": {
            "health_status": health_status,
            "health_score": health_score,
            "oscillatory_rate": oscillatory_rate,
            "regression_rate": regression_rate,
            "phase2_rows_with_phase2_data": phase2_rows_with_phase2_data,
            "phase2_rows_with_temporal_sequence": phase2_rows_with_temporal_sequence,
            "phase2_rows_with_dynamic_constructs": phase2_rows_with_dynamic_constructs,
            "phase2_unique_construct_count": phase2_unique_construct_count,
            "phase2_dynamic_construct_count": phase2_dynamic_construct_count,
            "phase2_temporal_sequence_ratio": round(phase2_temporal_sequence_ratio, 4),
            "phase2_dynamic_ratio": round(phase2_dynamic_ratio, 4),
            "min_required_phase2_rows_with_phase2_data": min_phase2_rows_with_phase2_data,
            "min_required_phase2_temporal_sequence_ratio": min_phase2_temporal_sequence_ratio,
            "min_required_phase2_dynamic_ratio": min_phase2_dynamic_ratio,
        },
    }


def _build_trajectory_summary(aggregate_trajectory: dict[str, list[float]]) -> dict[str, Any]:
    metric_summaries = {
        metric: _metric_trajectory_summary(values) for metric, values in aggregate_trajectory.items()
    }
    oscillatory_metrics = [
        metric for metric, details in metric_summaries.items() if details["is_oscillatory"]
    ]
    regressions = [
        metric for metric, details in metric_summaries.items() if details["regression_detected"]
    ]
    return {
        "schema": "consciousness_benchmark.growth_development_trajectory_summary.v1",
        "round_count": max(
            (summary["round_count"] for summary in metric_summaries.values()),
            default=0,
        ),
        "metric_count": len(metric_summaries),
        "monotonic_metrics": [
            metric for metric, details in metric_summaries.items() if details["is_monotonic"]
        ],
        "oscillatory_metrics": oscillatory_metrics,
        "regression_metrics": regressions,
        "metric_summaries": metric_summaries,
        "summary": {
            "oscillatory_rate": round(len(oscillatory_metrics) / max(1, len(metric_summaries)), 4),
            "regression_rate": round(len(regressions) / max(1, len(metric_summaries)), 4),
        },
    }


def run_batch(
    *,
    output_root: Path,
    seeds: list[int],
    stage_ids: tuple[str, ...],
    growth_no_ablation: bool,
    theory_case_ids: tuple[str, ...],
    theory_no_ablation: bool,
    run_gatecheck: bool,
    gatebook_path: Path | None = None,
    growth_trace_version: str = "v1",
    theory_trace_version: str = "v1",
    rounds: int = 1,
    seed_step: int = 0,
    require_health_pass: bool = False,
    health_min_score: float | None = None,
    health_oscillation_threshold: float | None = None,
    health_regression_threshold: float | None = None,
    min_phase2_unique_constructs: int | None = None,
    min_phase2_dynamic_construct_count: int | None = None,
    min_phase2_rows_with_phase2_data: int | None = None,
    min_phase2_temporal_sequence_ratio: float | None = None,
    min_phase2_dynamic_ratio: float | None = None,
    enforce_health_gate: bool = False,
    profile: str | None = None,
) -> dict[str, Any]:
    batch_run_id = f"growth_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_root = output_root / batch_run_id
    output_root.mkdir(parents=True, exist_ok=True)

    rounds = max(1, int(rounds))
    seed_step = _normalize_seed_step(seed_step)
    per_seed: list[dict[str, Any]] = []
    round_summaries: list[dict[str, Any]] = []
    growth_phase2_rows: list[dict[str, Any]] = []

    for round_index in range(rounds):
        round_id = f"round_{round_index}"
        round_output = output_root if rounds == 1 else output_root / round_id
        if round_output is not output_root:
            round_output.mkdir(parents=True, exist_ok=True)
        run_per_seed: list[dict[str, Any]] = []

        for base_seed in seeds:
            effective_seed = base_seed + (round_index * seed_step)
            seed_output = round_output / f"seed_{effective_seed}"
            seed_output.mkdir(parents=True, exist_ok=True)
            growth = run_developmental_growth_cycle(
                cycle_id=f"batch_growth_r{round_index}_s{base_seed}_{batch_run_id}",
                stage_ids=stage_ids,
                run_ablation=not growth_no_ablation,
                seed=effective_seed,
                trace_dir=seed_output / "growth",
                trace_version=growth_trace_version,
            )
            growth_payload = growth.to_dict()

            theory = run_consciousness_theory_assessment(
                case_ids=theory_case_ids,
                assessment_id=f"batch_theory_r{round_index}_s{base_seed}_{batch_run_id}",
                run_ablation=not theory_no_ablation,
                trace_dir=seed_output / "theory",
                trace_version=theory_trace_version,
            )
            theory_payload = theory.to_dict()

            gate = None
            if run_gatecheck:
                gate = _run_c_agi_layer_gatebook_check(
                    growth_stage_ids=stage_ids,
                    growth_seed=effective_seed,
                    growth_no_ablation=growth_no_ablation,
                    growth_trace_version=growth_trace_version,
                    theory_case_ids=theory_case_ids,
                    theory_no_ablation=theory_no_ablation,
                    check_gatebook_path=gatebook_path,
                )

            item = {
                "run_round": round_index,
                "base_seed": base_seed,
                "seed": effective_seed,
                "seed_output": str(seed_output),
                **_growth_summary(growth_payload),
                **_theory_summary(theory_payload),
                "gate_pass": 0,
                "gate_fail": 0,
                "gate_total": 0,
                "gate_status": gate.get("status") if isinstance(gate, dict) else "not_run",
            }
            phase2 = growth_payload.get("phase2_analysis", {})
            growth_phase2_rows.append(
                {
                    "run_round": round_index,
                    "seed": effective_seed,
                    "base_seed": base_seed,
                    "coactivation_patterns": tuple(
                        _safe_pattern_rows(
                            phase2.get("coactivation_patterns", ())
                        )
                    ),
                    "temporal_patterns": tuple(
                        _safe_pattern_rows(phase2.get("temporal_patterns", ()))
                    ),
                    "hierarchical_patterns": tuple(
                        _safe_pattern_rows(phase2.get("hierarchical_patterns", ()))
                    ),
                    "temporal_sequences": tuple(
                        _safe_pattern_rows(phase2.get("temporal_sequences", ()))
                    ),
                    "dynamic_construct_proposals": tuple(
                        _safe_pattern_rows(
                            phase2.get("dynamic_construct_proposals", ())
                        )
                    ),
                }
            )
            gate_pass, gate_fail, gate_total = _gate_summary(gate if isinstance(gate, dict) else None)
            item["gate_pass"] = gate_pass
            item["gate_fail"] = gate_fail
            item["gate_total"] = gate_total

            growth_payload["trace_manifest"]["request"].setdefault("batch_run_id", batch_run_id)
            growth_payload["trace_manifest"]["request"].setdefault(
                "seed_output", str(seed_output / "growth")
            )
            growth_payload["trace_manifest"]["request"]["batch_round"] = round_index
            growth_payload["trace_manifest"]["request"]["base_seed"] = base_seed
            growth_payload["trace_manifest"]["request"]["effective_seed"] = effective_seed
            (seed_output / "growth_cycle.json").write_text(
                json.dumps(growth_payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (seed_output / "theory_assessment.json").write_text(
                json.dumps(theory_payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            if isinstance(gate, dict):
                (seed_output / "gatecheck.json").write_text(
                    json.dumps(gate, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )

            run_per_seed.append(item)
            per_seed.append(item)

        round_aggregate_mean: dict[str, Any] = {}
        for key in (
            "growth_stage_mean",
            "growth_stage_max",
            "growth_stage_count",
            "coactivation_pair_count",
            "coactivation_pattern_count",
            "temporal_pattern_count",
            "hierarchical_pattern_count",
            "temporal_sequence_count",
            "dynamic_constructs",
            "growth_ab_sensitive",
            "growth_ab_mean_delta",
            "growth_ab_delta_max",
            "theory_pass_count",
            "theory_review_required_count",
            "theory_not_run_count",
            "theory_phase2_patterns",
            "theory_matrix_row_count",
            "theory_mean_ablation_delta",
            "gate_pass",
            "gate_fail",
            "gate_total",
        ):
            round_aggregate_mean[key] = _aggregate_means(run_per_seed, key) or 0.0

        round_summaries.append(
            {
                "round_index": round_index,
                "per_seed": run_per_seed,
                "aggregate_mean": round_aggregate_mean,
                "seed_list": [entry["seed"] for entry in run_per_seed],
                "seed_count": len(run_per_seed),
            }
        )

    # Keep compatibility key list used by downstream scripts/records.
    mean_aggregation_keys = (
        "growth_stage_mean",
        "growth_stage_max",
        "growth_stage_count",
        "coactivation_pair_count",
        "coactivation_pattern_count",
        "temporal_pattern_count",
        "hierarchical_pattern_count",
        "temporal_sequence_count",
        "dynamic_constructs",
        "growth_ab_sensitive",
        "growth_ab_mean_delta",
        "growth_ab_delta_max",
        "theory_pass_count",
        "theory_review_required_count",
        "theory_not_run_count",
        "theory_phase2_patterns",
        "theory_matrix_row_count",
        "theory_mean_ablation_delta",
        "gate_pass",
        "gate_fail",
        "gate_total",
    )
    aggregate_mean: dict[str, Any] = {}
    for key in mean_aggregation_keys:
        aggregate_mean[key] = _aggregate_means(per_seed, key) or 0.0

    aggregate_trajectory: dict[str, list[float]] = {}
    for key in mean_aggregation_keys:
        aggregate_trajectory[key] = _build_metric_trajectory(round_summaries, key)
    aggregate_stability: dict[str, dict[str, Any]] = {
        key: _build_stability_summary(values)
        for key, values in aggregate_trajectory.items()
    }

    trajectory_summary: dict[str, Any] | None = None
    if rounds > 1:
        trajectory_summary = _build_trajectory_summary(aggregate_trajectory)
        (output_root / "development_trajectory_summary.json").write_text(
            json.dumps(trajectory_summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    batch_health_summary = _build_health_summary(
        trajectory_summary=trajectory_summary, aggregate_mean=aggregate_mean
    )
    (output_root / "batch_health_summary.json").write_text(
        json.dumps(batch_health_summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    phase2_mining_summary = _aggregate_phase2_mining(growth_phase2_rows)
    (output_root / "batch_phase2_mining.json").write_text(
        json.dumps(phase2_mining_summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    batch_health_gate = _evaluate_health_gate(
        batch_health_summary,
        phase2_mining_summary=phase2_mining_summary,
        require_health_pass=require_health_pass,
        min_health_score=health_min_score,
        max_oscillation_rate=health_oscillation_threshold,
        max_regression_rate=health_regression_threshold,
        min_phase2_unique_constructs=min_phase2_unique_constructs,
        min_phase2_dynamic_construct_count=min_phase2_dynamic_construct_count,
        min_phase2_rows_with_phase2_data=min_phase2_rows_with_phase2_data,
        min_phase2_temporal_sequence_ratio=min_phase2_temporal_sequence_ratio,
        min_phase2_dynamic_ratio=min_phase2_dynamic_ratio,
    )
    (output_root / "batch_health_gate.json").write_text(
        json.dumps(batch_health_gate, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    summary = {
        "batch_id": batch_run_id,
        "created_utc": datetime.now().isoformat(),
        "config": {
            "profile": profile,
            "seeds": seeds,
            "stage_ids": list(stage_ids),
            "theory_case_ids": list(theory_case_ids),
            "growth_no_ablation": growth_no_ablation,
            "theory_no_ablation": theory_no_ablation,
            "run_gatecheck": run_gatecheck,
            "rounds": rounds,
            "seed_step": seed_step,
            "min_phase2_unique_constructs": min_phase2_unique_constructs,
            "min_phase2_dynamic_construct_count": min_phase2_dynamic_construct_count,
            "min_phase2_rows_with_phase2_data": min_phase2_rows_with_phase2_data,
            "min_phase2_temporal_sequence_ratio": min_phase2_temporal_sequence_ratio,
            "min_phase2_dynamic_ratio": min_phase2_dynamic_ratio,
        },
        "per_seed": per_seed,
        "aggregate_mean": aggregate_mean,
        "round_summaries": round_summaries,
        "aggregate_trajectory": aggregate_trajectory,
        "aggregate_stability": aggregate_stability,
        "development_trajectory_summary": trajectory_summary,
        "batch_health_summary": batch_health_summary,
        "batch_health_gate": batch_health_gate,
        "phase2_mining_summary": phase2_mining_summary,
    }

    if enforce_health_gate and not batch_health_gate["passed"]:
        from consciousness_benchmark.gate_advisor import GateAdvisor

        advice_path = GateAdvisor.write_gate_failure_advice(
            output_root,
            batch_health_gate,
        )
        advice = GateAdvisor.generate_advice(batch_health_gate)
        first_hint = advice[0].split("\n", maxsplit=1)[0] if advice else "see gate_failure_advice.md"
        raise RuntimeError(
            "Growth batch health gate failed: "
            + "; ".join(batch_health_gate["violations"] or ["unknown failure"])
            + f". Advice: {advice_path}. {first_hint}"
        )

    (output_root / "batch_stability_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run growth/theory batch with deterministic seeds and produce "
            "stability summary."
        )
    )
    parser.add_argument(
        "--profile",
        choices=["exploration", "validation", "production", "quick_check"],
        default=None,
        help="Apply a predefined run profile; explicit flags override profile values.",
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List available profiles and exit.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        action="append",
        default=[11, 23, 37],
        help="Seed values to run (repeatable).",
    )
    parser.add_argument(
        "--seed-csv",
        type=str,
        default=None,
        help="Optional comma-separated seed values; overrides --seed.",
    )
    parser.add_argument(
        "--stage-ids",
        nargs="*",
        default=[],
        help="Optional growth stage ids in order.",
    )
    parser.add_argument(
        "--theory-case-id",
        action="append",
        default=[],
        help="Optional case id for theory assessment. Can be repeated.",
    )
    parser.add_argument("--no-growth-ablation", action="store_true")
    parser.add_argument("--no-theory-ablation", action="store_true")
    parser.add_argument("--run-gatecheck", action="store_true")
    parser.add_argument(
        "--gatebook-path",
        type=Path,
        default=DEFAULT_GATEBOOK_PATH,
        help="Optional gatebook file when --run-gatecheck is used.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Root folder to write batch artifacts.",
    )
    parser.add_argument("--growth-trace-version", default="v1")
    parser.add_argument("--theory-trace-version", default="v1")
    parser.add_argument(
        "--rounds",
        type=int,
        default=1,
        help="Number of replay rounds to run.",
    )
    parser.add_argument(
        "--seed-step",
        type=int,
        default=0,
        help=(
            "Seed increment between replay rounds. "
            "0 keeps the same seeds for each round; >0 sweeps the seed lattice."
        ),
    )
    parser.add_argument(
        "--require-health-pass",
        action="store_true",
        help=(
            "Require strict health gate evaluation (health_status == pass). "
            "Without additional thresholds, this is the only required pass condition."
        ),
    )
    parser.add_argument(
        "--health-min-score",
        type=float,
        default=None,
        help="Optional minimum batch health_score required for pass.",
    )
    parser.add_argument(
        "--health-oscillation-threshold",
        type=float,
        default=None,
        help=(
            "Optional maximum oscillatory_rate threshold. If set and exceeded, gate fails."
        ),
    )
    parser.add_argument(
        "--health-regression-threshold",
        type=float,
        default=None,
        help=(
            "Optional maximum regression_rate threshold. If set and exceeded, gate fails."
        ),
    )
    parser.add_argument(
        "--min-phase2-unique-constructs",
        type=int,
        default=None,
        help=(
            "Optional minimum phase2 unique construct count required for batch pass."
        ),
    )
    parser.add_argument(
        "--min-phase2-dynamic-construct-count",
        type=int,
        default=None,
        help=(
            "Optional minimum phase2 dynamic construct proposal count required for batch pass."
        ),
    )
    parser.add_argument(
        "--min-phase2-rows-with-phase2-data",
        type=int,
        default=None,
        help=(
            "Optional minimum number of rows with phase2 data required for batch pass."
        ),
    )
    parser.add_argument(
        "--min-phase2-temporal-sequence-ratio",
        type=float,
        default=None,
        help=(
            "Optional minimum ratio of rows with temporal sequence evidence. "
            "Set in [0,1]."
        ),
    )
    parser.add_argument(
        "--min-phase2-dynamic-ratio",
        type=float,
        default=None,
        help=(
            "Optional minimum ratio of rows with dynamic construct proposals. "
            "Set in [0,1]."
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress JSON summary printout.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.list_profiles:
        from consciousness_benchmark.run_profiles import format_profiles_listing

        print(format_profiles_listing())
        return

    if args.profile:
        from consciousness_benchmark.run_profiles import apply_profile_to_namespace

        print(f"Using profile: {args.profile}")
        for line in apply_profile_to_namespace(args):
            print(f"  profile default: {line}")

    if args.seed_csv:
        seeds = [int(part.strip()) for part in args.seed_csv.split(",") if part.strip()]
    else:
        seeds = args.seed or []
    if not seeds:
        seeds = [11, 23, 37]

    stage_ids = _normalize_stage_ids(args.stage_ids)
    theory_case_ids = _normalize_case_ids(args.theory_case_id)

    result = run_batch(
        output_root=args.output_root,
        seeds=seeds,
        stage_ids=stage_ids,
        growth_no_ablation=args.no_growth_ablation,
        theory_case_ids=theory_case_ids,
        theory_no_ablation=args.no_theory_ablation,
        run_gatecheck=args.run_gatecheck,
        gatebook_path=args.gatebook_path if args.run_gatecheck else None,
        growth_trace_version=args.growth_trace_version,
        theory_trace_version=args.theory_trace_version,
        rounds=args.rounds,
        seed_step=args.seed_step,
        require_health_pass=args.require_health_pass,
        health_min_score=args.health_min_score,
        health_oscillation_threshold=args.health_oscillation_threshold,
        health_regression_threshold=args.health_regression_threshold,
        min_phase2_unique_constructs=args.min_phase2_unique_constructs,
        min_phase2_dynamic_construct_count=args.min_phase2_dynamic_construct_count,
        min_phase2_rows_with_phase2_data=args.min_phase2_rows_with_phase2_data,
        min_phase2_temporal_sequence_ratio=args.min_phase2_temporal_sequence_ratio,
        min_phase2_dynamic_ratio=args.min_phase2_dynamic_ratio,
        profile=args.profile,
        enforce_health_gate=args.require_health_pass
        or args.health_min_score is not None
        or args.health_oscillation_threshold is not None
        or args.health_regression_threshold is not None
        or args.min_phase2_unique_constructs is not None
        or args.min_phase2_dynamic_construct_count is not None
        or args.min_phase2_rows_with_phase2_data is not None
        or args.min_phase2_temporal_sequence_ratio is not None
        or args.min_phase2_dynamic_ratio is not None,
    )
    if not args.quiet:
        print(json.dumps(result["aggregate_mean"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
