"""Generate actionable advice when growth batch health gates fail."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class GateAdvisor:
    """Build human-readable remediation hints from health gate results."""

    @staticmethod
    def generate_advice(gate_result: dict[str, Any]) -> list[str]:
        advice: list[str] = []
        requirements = gate_result.get("requirements", {})
        observed = gate_result.get("observed", {})
        violations = list(gate_result.get("violations", []) or [])

        rows_required = requirements.get("min_phase2_rows_with_phase2_data")
        if rows_required is not None:
            actual = int(observed.get("phase2_rows_with_phase2_data", 0) or 0)
            if actual < int(rows_required):
                advice.append(
                    f"Phase2 样本不足 ({actual}/{rows_required}):\n"
                    "   建议 1: 增加 --rounds（当前轮次可能太少）\n"
                    "   建议 2: 增加 --stage-ids，覆盖更多发展阶段\n"
                    "   建议 3: 检查各 seed 的 growth_cycle 是否产出有效 phase2 数据"
                )

        temporal_required = requirements.get("min_phase2_temporal_sequence_ratio")
        if temporal_required is not None:
            actual = float(observed.get("phase2_temporal_sequence_ratio", 0.0) or 0.0)
            if actual < float(temporal_required):
                suggested = max(0.3, round(actual + 0.1, 2))
                advice.append(
                    f"Temporal sequence 比例不足 ({actual:.2%}/{float(temporal_required):.2%}):\n"
                    "   建议 1: 增加 --rounds，积累更多时间序列证据\n"
                    "   建议 2: 检查 coactivation / temporal mining 是否正常\n"
                    f"   建议 3: 探索阶段可尝试 --profile exploration 或降至约 {suggested:.2f}"
                )

        dynamic_required = requirements.get("min_phase2_dynamic_ratio")
        if dynamic_required is not None:
            actual = float(observed.get("phase2_dynamic_ratio", 0.0) or 0.0)
            if actual < float(dynamic_required):
                advice.append(
                    f"Dynamic construct 比例不足 ({actual:.2%}/{float(dynamic_required):.2%}):\n"
                    "   建议 1: 早期阶段动态提案偏少可能是正常现象\n"
                    "   建议 2: 高级阶段请检查 discovery 链路是否被调用\n"
                    "   建议 3: 使用 --profile exploration 降低比例门禁"
                )

        unique_required = requirements.get("min_phase2_unique_constructs")
        if unique_required is not None:
            actual = int(observed.get("phase2_unique_construct_count", 0) or 0)
            if actual < int(unique_required):
                advice.append(
                    f"Phase2 unique constructs 不足 ({actual}/{unique_required}):\n"
                    "   建议 1: 扩大 stage_ids 或增加 seeds\n"
                    "   建议 2: 确认 phase2 mining 聚合行数足够（见 batch_phase2_mining.json）"
                )

        dynamic_count_required = requirements.get("min_phase2_dynamic_construct_count")
        if dynamic_count_required is not None:
            actual = int(observed.get("phase2_dynamic_construct_count", 0) or 0)
            if actual < int(dynamic_count_required):
                advice.append(
                    f"Dynamic construct 计数不足 ({actual}/{dynamic_count_required}):\n"
                    "   建议 1: 在 midterm_tasking 及以上阶段再启用严格计数门禁\n"
                    "   建议 2: 使用 --profile quick_check 做 CI 冒烟"
                )

        if requirements.get("require_health_pass") and observed.get("health_status") != "pass":
            advice.append(
                f"Batch health_status 未通过（当前: {observed.get('health_status')}）:\n"
                "   建议 1: 查看 batch_health_summary.json 的 risk_level 与 trend\n"
                "   建议 2: 至少 2 轮 rounds 才适用 trajectory 健康评估\n"
                "   建议 3: 探索阶段使用 --profile exploration 并关闭 --require-health-pass"
            )

        min_score = requirements.get("min_health_score")
        if min_score is not None:
            score = float(observed.get("health_score", 0.0) or 0.0)
            if score < float(min_score):
                advice.append(
                    f"health_score 低于阈值 ({score:.4f} < {float(min_score):.4f}):\n"
                    "   建议: 检查 oscillatory_rate / regression_rate 与 theory 覆盖"
                )

        gatecheck = gate_result.get("gatecheck_result")
        if isinstance(gatecheck, dict) and not gatecheck.get("all_passed", True):
            failed = gatecheck.get("failed", [])
            advice.append(
                f"Layer gatecheck 失败 ({len(failed)} 项):\n"
                f"   失败项: {', '.join(str(item) for item in failed)}\n"
                "   建议: 运行 mind-c-agi-layer-gatecheck 查看逐层失败原因"
            )

        for violation in violations:
            if "oscillatory_rate" in violation:
                advice.append(
                    "振荡率超阈值:\n"
                    "   建议: 增加 rounds 或放宽 --health-oscillation-threshold（仅探索）"
                )
            elif "regression_rate" in violation:
                advice.append(
                    "回归率超阈值:\n"
                    "   建议: 对照 round_summaries 定位退化指标"
                )

        if not advice:
            violation_text = "; ".join(violations) if violations else "unknown"
            advice.append(
                f"门禁失败但未匹配到结构化建议（violations: {violation_text}）:\n"
                "   1. 阅读 batch_health_gate.json\n"
                "   2. 使用 --profile exploration 降低门禁\n"
                "   3. 增加 --rounds 与 --stage-ids"
            )

        return advice

    @staticmethod
    def format_advice_as_markdown(advice: list[str], *, profile_hint: str = "exploration") -> str:
        lines = ["## 门禁失败修复建议", ""]
        for index, item in enumerate(advice, start=1):
            lines.append(f"### 建议 {index}")
            lines.append("")
            lines.append(item)
            lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(
            f"提示：可使用 `--profile {profile_hint}` 进入较宽松模式快速迭代。"
        )
        return "\n".join(lines) + "\n"

    @staticmethod
    def write_gate_failure_advice(
        output_root: Path,
        gate_result: dict[str, Any],
        *,
        profile_hint: str = "exploration",
    ) -> Path:
        advisor = GateAdvisor()
        advice = advisor.generate_advice(gate_result)
        markdown = advisor.format_advice_as_markdown(advice, profile_hint=profile_hint)
        advice_path = output_root / "gate_failure_advice.md"
        advice_path.write_text(markdown, encoding="utf-8")
        return advice_path
