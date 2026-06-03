from __future__ import annotations

from pathlib import Path

from consciousness_benchmark.gate_advisor import GateAdvisor


def test_advisor_phase2_rows_advice() -> None:
    gate_result = {
        "requirements": {"min_phase2_rows_with_phase2_data": 5},
        "observed": {"phase2_rows_with_phase2_data": 2},
        "violations": ["phase2_rows_with_phase2_data 2 < threshold 5."],
    }

    advice = GateAdvisor.generate_advice(gate_result)

    assert advice
    assert "Phase2 样本不足" in advice[0]
    assert "--rounds" in advice[0]


def test_advisor_temporal_ratio_advice() -> None:
    gate_result = {
        "requirements": {"min_phase2_temporal_sequence_ratio": 0.5},
        "observed": {"phase2_temporal_sequence_ratio": 0.3},
        "violations": [],
    }

    advice = GateAdvisor.generate_advice(gate_result)

    assert advice
    assert "Temporal sequence 比例不足" in advice[0]


def test_advisor_markdown_formatting() -> None:
    gate_result = {
        "requirements": {"min_phase2_rows_with_phase2_data": 5},
        "observed": {"phase2_rows_with_phase2_data": 2},
        "violations": [],
    }

    advice = GateAdvisor.generate_advice(gate_result)
    markdown = GateAdvisor.format_advice_as_markdown(advice)

    assert "## 门禁失败修复建议" in markdown
    assert "### 建议 1" in markdown
    assert "--profile exploration" in markdown


def test_write_gate_failure_advice(tmp_path: Path) -> None:
    gate_result = {
        "requirements": {"min_phase2_dynamic_ratio": 0.9},
        "observed": {"phase2_dynamic_ratio": 0.1},
        "violations": ["phase2_dynamic_ratio 0.1000 < threshold 0.9000."],
    }

    path = GateAdvisor.write_gate_failure_advice(tmp_path, gate_result)

    assert path.exists()
    assert "Dynamic construct 比例不足" in path.read_text(encoding="utf-8")
