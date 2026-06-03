"""Tests for batch growth/theory replay runner."""

from __future__ import annotations

from pathlib import Path
import sys
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_developmental_growth_stability_batch import (
    _metric_trajectory_summary,
    run_batch,
)


def test_run_growth_stability_batch_generates_summary(tmp_path: Path) -> None:
    result = run_batch(
        output_root=tmp_path,
        seeds=[11],
        stage_ids=("initial",),
        growth_no_ablation=True,
        theory_case_ids=("global_workspace",),
        theory_no_ablation=True,
        run_gatecheck=False,
        growth_trace_version="v1",
        theory_trace_version="v1",
    )

    assert result["batch_id"].startswith("growth_batch_")
    assert len(result["per_seed"]) == 1
    per_seed = result["per_seed"][0]
    assert per_seed["seed"] == 11
    assert per_seed["growth_stage_count"] == 1
    assert per_seed["theory_matrix_row_count"] == 1
    assert per_seed["gate_status"] == "not_run"
    assert per_seed["gate_total"] == 0
    assert result["aggregate_mean"]["growth_stage_count"] == 1.0
    assert result["aggregate_mean"]["theory_matrix_row_count"] == 1.0
    assert result["development_trajectory_summary"] is None
    assert result["batch_health_summary"]["schema"] == "consciousness_benchmark.growth_development_batch_health.v1"
    assert result["batch_health_summary"]["applicable"] is False
    assert result["batch_health_summary"]["health_status"] == "single_round_insufficient"

    summary_path = tmp_path / result["batch_id"] / "batch_stability_summary.json"
    assert summary_path.exists()
    assert (tmp_path / result["batch_id"] / "batch_health_summary.json").exists()


def test_health_gate_fails_on_single_round_when_required(tmp_path: Path) -> None:
    result = run_batch(
        output_root=tmp_path,
        seeds=[11],
        stage_ids=("initial",),
        growth_no_ablation=True,
        theory_case_ids=("global_workspace",),
        theory_no_ablation=True,
        run_gatecheck=False,
        growth_trace_version="v1",
        theory_trace_version="v1",
        require_health_pass=True,
        enforce_health_gate=False,
    )
    gate = result["batch_health_gate"]
    assert gate["enabled"] is True
    assert gate["passed"] is False
    assert "at least 2 rounds" in ",".join(gate["violations"])


def test_health_gate_artifact_written(tmp_path: Path) -> None:
    result = run_batch(
        output_root=tmp_path,
        seeds=[11],
        stage_ids=("initial",),
        growth_no_ablation=True,
        theory_case_ids=("global_workspace",),
        theory_no_ablation=True,
        run_gatecheck=False,
        growth_trace_version="v1",
        theory_trace_version="v1",
    )

    assert (tmp_path / result["batch_id"] / "batch_health_gate.json").exists()


def test_run_growth_stability_batch_phase2_mining_artifact(tmp_path: Path) -> None:
    result = run_batch(
        output_root=tmp_path,
        seeds=[11],
        stage_ids=("initial", "early_exploration", "midterm_tasking"),
        growth_no_ablation=True,
        theory_case_ids=("global_workspace",),
        theory_no_ablation=True,
        run_gatecheck=False,
        growth_trace_version="v1",
        theory_trace_version="v1",
        rounds=2,
        seed_step=1,
    )

    batch_root = tmp_path / result["batch_id"]
    assert (batch_root / "batch_phase2_mining.json").exists()

    phase2 = result["phase2_mining_summary"]
    assert phase2["schema"] == "consciousness_benchmark.growth_development_batch_phase2_mining.v1"
    pattern_summary = phase2["pattern_summary"]
    assert "coactivation_top_patterns" in pattern_summary
    assert "temporal_top_patterns" in pattern_summary
    assert "hierarchical_top_patterns" in pattern_summary
    assert "temporal_sequence_top_patterns" in pattern_summary
    assert isinstance(phase2["construct_engagement"]["unique_construct_involved_count"], int)
    assert phase2["batch_coverage"]["rows_with_phase2_data"] == 2

    dynamic_summary = phase2["dynamic_construct_summary"]
    assert dynamic_summary["review_only_dynamic_construct_count"] >= 0
    assert isinstance(dynamic_summary["top_review_only_dynamic_constructs"], list)


def test_growth_batch_health_gate_enforces_phase2_thresholds(tmp_path: Path) -> None:
    result = run_batch(
        output_root=tmp_path,
        seeds=[11],
        stage_ids=("initial", "early_exploration"),
        growth_no_ablation=True,
        theory_case_ids=("global_workspace",),
        theory_no_ablation=True,
        run_gatecheck=False,
        growth_trace_version="v1",
        theory_trace_version="v1",
        rounds=2,
        seed_step=1,
        min_phase2_unique_constructs=999999,
    )

    gate = result["batch_health_gate"]
    assert gate["enabled"] is True
    assert gate["passed"] is False
    assert any(
        "phase2_unique_construct_count" in item
        for item in gate["violations"]
    )


def test_growth_batch_health_gate_enforces_phase2_coverage_ratios(tmp_path: Path) -> None:
    result = run_batch(
        output_root=tmp_path,
        seeds=[11],
        stage_ids=("initial", "early_exploration"),
        growth_no_ablation=True,
        theory_case_ids=("global_workspace",),
        theory_no_ablation=True,
        run_gatecheck=False,
        growth_trace_version="v1",
        theory_trace_version="v1",
        rounds=2,
        seed_step=1,
        min_phase2_temporal_sequence_ratio=1.5,
        min_phase2_dynamic_ratio=1.5,
    )

    gate = result["batch_health_gate"]
    assert gate["enabled"] is True
    assert gate["passed"] is False
    assert any("phase2_temporal_sequence_ratio" in item for item in gate["violations"])
    assert any("phase2_dynamic_ratio" in item for item in gate["violations"])
    assert result["config"]["min_phase2_temporal_sequence_ratio"] == 1.5
    assert result["config"]["min_phase2_dynamic_ratio"] == 1.5


def test_growth_batch_health_gate_enforces_phase2_row_coverage_minimum(tmp_path: Path) -> None:
    result = run_batch(
        output_root=tmp_path,
        seeds=[11],
        stage_ids=("initial",),
        growth_no_ablation=True,
        theory_case_ids=("global_workspace",),
        theory_no_ablation=True,
        run_gatecheck=False,
        growth_trace_version="v1",
        theory_trace_version="v1",
        rounds=1,
        seed_step=1,
        min_phase2_rows_with_phase2_data=999999,
    )

    gate = result["batch_health_gate"]
    assert gate["enabled"] is True
    assert gate["passed"] is False
    assert any(
        "phase2_rows_with_phase2_data" in item for item in gate["violations"]
    )


def test_growth_batch_health_gate_raises_when_enforced_thresholds_fail(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="Advice:"):
        run_batch(
            output_root=tmp_path,
            seeds=[11],
            stage_ids=("initial", "early_exploration"),
            growth_no_ablation=True,
            theory_case_ids=("global_workspace",),
            theory_no_ablation=True,
            run_gatecheck=False,
            growth_trace_version="v1",
            theory_trace_version="v1",
            rounds=2,
            seed_step=1,
            min_phase2_dynamic_construct_count=999999,
            enforce_health_gate=True,
        )

    advice_files = list(tmp_path.rglob("gate_failure_advice.md"))
    assert len(advice_files) == 1
    assert "Dynamic construct 计数不足" in advice_files[0].read_text(encoding="utf-8")


def test_enforce_health_gate_raises_for_bad_batch(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        run_batch(
            output_root=tmp_path,
            seeds=[11],
            stage_ids=("initial",),
            growth_no_ablation=True,
            theory_case_ids=("global_workspace",),
            theory_no_ablation=True,
            run_gatecheck=False,
            growth_trace_version="v1",
            theory_trace_version="v1",
            require_health_pass=True,
            enforce_health_gate=True,
        )


def test_run_growth_stability_batch_writes_trace_artifacts(tmp_path: Path) -> None:
    result = run_batch(
        output_root=tmp_path,
        seeds=[11, 23],
        stage_ids=("initial", "early_exploration"),
        growth_no_ablation=True,
        theory_case_ids=("global_workspace", "predictive_processing"),
        theory_no_ablation=True,
        run_gatecheck=False,
        growth_trace_version="v1",
        theory_trace_version="v1",
    )

    batch_root = tmp_path / result["batch_id"]
    assert batch_root.exists()
    assert (batch_root / "batch_stability_summary.json").exists()
    assert (batch_root / "batch_health_summary.json").exists()

    seed_dir = batch_root / "seed_11"
    assert seed_dir.exists()
    assert (seed_dir / "growth_cycle.json").exists()
    assert (seed_dir / "theory_assessment.json").exists()

    growth_data = seed_dir.joinpath("growth_cycle.json").read_text(encoding="utf-8")
    theory_data = seed_dir.joinpath("theory_assessment.json").read_text(encoding="utf-8")
    assert '"cycle_id"' in growth_data
    assert '"assessment_id"' in theory_data


def test_run_growth_stability_batch_multi_round_trajectory(tmp_path: Path) -> None:
    result = run_batch(
        output_root=tmp_path,
        seeds=[11],
        stage_ids=("initial",),
        growth_no_ablation=True,
        theory_case_ids=("global_workspace",),
        theory_no_ablation=True,
        run_gatecheck=False,
        growth_trace_version="v1",
        theory_trace_version="v1",
        rounds=3,
        seed_step=2,
    )

    assert result["config"]["rounds"] == 3
    assert result["config"]["seed_step"] == 2
    assert len(result["round_summaries"]) == 3
    assert len(result["per_seed"]) == 3
    assert [entry["seed"] for entry in result["per_seed"]] == [11, 13, 15]

    trajectory = result["aggregate_trajectory"]
    assert len(trajectory["growth_stage_count"]) == 3
    assert trajectory["growth_stage_count"] == [1.0, 1.0, 1.0]

    stability = result["aggregate_stability"]["growth_stage_count"]
    assert stability["sample_count"] == 3
    assert stability["min"] == 1.0
    assert stability["max"] == 1.0
    assert stability["first"] == 1.0
    assert stability["last"] == 1.0

    trajectory_summary = result["development_trajectory_summary"]
    assert trajectory_summary is not None
    assert trajectory_summary["schema"] == "consciousness_benchmark.growth_development_trajectory_summary.v1"
    assert result["batch_health_summary"]["schema"] == "consciousness_benchmark.growth_development_batch_health.v1"
    assert result["batch_health_summary"]["applicable"] is True
    assert trajectory_summary["round_count"] == 3
    assert trajectory_summary["metric_count"] >= 1
    assert "coactivation_pattern_count" in trajectory_summary["metric_summaries"]
    co_activation_summary = trajectory_summary["metric_summaries"]["coactivation_pattern_count"]
    assert co_activation_summary["round_count"] == 3
    assert co_activation_summary["trend_direction"] in {"flat", "increasing", "decreasing", "non_monotonic"}

    trajectory_summary_path = tmp_path / result["batch_id"] / "development_trajectory_summary.json"
    assert trajectory_summary_path.exists()
    assert trajectory_summary_path.read_text(encoding="utf-8").strip()

    batch_root = tmp_path / result["batch_id"]
    assert (batch_root / "round_0" / "seed_11" / "growth_cycle.json").exists()
    assert (batch_root / "round_1" / "seed_13" / "growth_cycle.json").exists()
    assert (batch_root / "round_2" / "seed_15" / "growth_cycle.json").exists()

    health_summary = result["batch_health_summary"]
    assert health_summary["applicable"] is True
    assert health_summary["trajectory_rounds"] == 3
    assert isinstance(health_summary["health_score"], float)
    assert isinstance(health_summary["dominant_metric_count"], int)
    assert len(health_summary["dominant_trend_keys"]) <= 5


def test_metric_trajectory_summary_detects_signal_shape() -> None:
    monotonic = _metric_trajectory_summary([1.0, 1.1, 1.2])
    assert monotonic["trend_direction"] == "increasing"
    assert monotonic["is_monotonic"] is True
    assert monotonic["is_oscillatory"] is False
    assert monotonic["rebound_count"] == 0

    oscillatory = _metric_trajectory_summary([1.0, 1.5, 1.2, 1.6])
    assert oscillatory["trend_direction"] == "non_monotonic"
    assert oscillatory["is_oscillatory"] is True
    assert oscillatory["rebound_count"] >= 1
    assert oscillatory["regression_detected"] is True
