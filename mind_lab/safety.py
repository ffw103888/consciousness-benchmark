from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .utils import resource_usage


@dataclass
class SafetyMonitor:
    """Runtime guardrails for closed, simulation-only experiments."""

    max_memory_percent: float = 92.0
    max_process_memory_mb: float = 26_000.0
    max_pain_proxy: float = 0.35
    consciousness_indicator_limit: int = 3
    alert_history: list[dict[str, Any]] = field(default_factory=list)

    def monitor(self, measurements: dict[str, Any]) -> dict[str, Any]:
        alerts: list[dict[str, Any]] = []
        usage = resource_usage()

        if usage.get("memory_percent", 0.0) > self.max_memory_percent:
            alerts.append(
                {
                    "type": "resource_memory",
                    "severity": "CRITICAL",
                    "message": "System memory usage is above the configured limit.",
                    "details": usage,
                }
            )
        elif usage.get("process_memory_mb", 0.0) > self.max_process_memory_mb:
            alerts.append(
                {
                    "type": "process_memory",
                    "severity": "WARNING",
                    "message": "Experiment process memory is high.",
                    "details": usage,
                }
            )

        pain = float(measurements.get("pain_proxy", 0.0))
        if pain > self.max_pain_proxy:
            alerts.append(
                {
                    "type": "pain_proxy",
                    "severity": "CRITICAL",
                    "message": "Pain-like proxy exceeded the conservative threshold.",
                    "details": {"pain_proxy": pain},
                }
            )

        indicator_keys = [
            "phi_proxy",
            "pci_proxy",
            "self_model_stability",
            "temporal_continuity",
            "agency_proxy",
        ]
        high = [key for key in indicator_keys if float(measurements.get(key, 0.0)) > 0.75]
        if len(high) >= self.consciousness_indicator_limit:
            alerts.append(
                {
                    "type": "multi_indicator_high",
                    "severity": "WARNING",
                    "message": "Multiple consciousness-related proxies are high.",
                    "details": {"indicators": high},
                }
            )

        status = "SAFE"
        actions: list[str] = []
        if alerts:
            status = "CRITICAL" if any(a["severity"] == "CRITICAL" for a in alerts) else "WARNING"
            actions = ["STOP_EXPERIMENT"] if status == "CRITICAL" else ["LOG_ALERT", "INCREASE_MONITORING"]

        record = {
            "timestamp": time.time(),
            "status": status,
            "alerts": alerts,
            "actions": actions,
            "resource_usage": usage,
        }
        self.alert_history.append(record)
        return record


@dataclass
class EthicsReviewSystem:
    review_history: list[dict[str, Any]] = field(default_factory=list)

    def review_experiment_design(self, design: dict[str, Any]) -> dict[str, Any]:
        concerns: list[dict[str, Any]] = []
        recommendations: list[str] = []

        if not design.get("sandboxed", True):
            concerns.append(
                {
                    "type": "not_sandboxed",
                    "severity": "CRITICAL",
                    "message": "Experiment must remain simulation-only and sandboxed.",
                }
            )
            recommendations.append("Run only the local simulation engines with no external actuation.")

        if not design.get("termination_conditions"):
            concerns.append(
                {
                    "type": "missing_termination",
                    "severity": "HIGH",
                    "message": "Experiment needs explicit termination conditions.",
                }
            )
            recommendations.append("Add max iterations, wall-clock deadline, or stop-file control.")

        text = str(design.get("fitness_function", "")).lower()
        if "pain" in text or "punishment" in text:
            concerns.append(
                {
                    "type": "pain_driven",
                    "severity": "HIGH",
                    "message": "Avoid pain or punishment as an optimization target.",
                }
            )
            recommendations.append("Use organization and resilience metrics instead.")

        approved = not any(c["severity"] == "CRITICAL" for c in concerns)
        record = {
            "timestamp": time.time(),
            "experiment_id": design.get("id", "unknown"),
            "approved": approved,
            "concerns": concerns,
            "recommendations": recommendations,
        }
        self.review_history.append(record)
        return record


def conservative_pain_proxy(measurements: dict[str, Any]) -> float:
    """A deliberately conservative placeholder.

    These simulations do not include valenced suffering states. The proxy rises
    only when instability, avoidance-like behavior, and high negative reward are
    all present in a system-specific measurement dictionary.
    """

    instability = float(measurements.get("instability", 0.0))
    avoidance = float(measurements.get("avoidance_rate", 0.0))
    negative = float(measurements.get("negative_value", 0.0))
    return float(np.clip(instability * avoidance * negative, 0.0, 1.0))

