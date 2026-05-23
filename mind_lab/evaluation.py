from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .utils import clamp01


DIMENSIONS = ["state", "content", "self_model", "agency", "temporal_continuity"]


@dataclass
class ConsciousnessEvaluator:
    """Five independent operational measurements.

    The evaluator reports proxy dimensions. It does not collapse them into a
    single consciousness score and does not use them as evolutionary fitness.
    """

    history: list[dict[str, Any]] = field(default_factory=list)

    def evaluate(self, systems: dict[str, Any]) -> dict[str, Any]:
        by_system: dict[str, Any] = {}
        for name, system in systems.items():
            if hasattr(system, "evaluation_profile"):
                profile = system.evaluation_profile()
            else:
                profile = self._fallback_profile(system)
            scores = {dim: clamp01(float(profile.get(dim, 0.0))) for dim in DIMENSIONS}
            by_system[name] = {
                "scores": scores,
                "details": profile.get("details", {}),
                "anomalies": self.detect_anomalies(scores),
                "mean": float(np.mean(list(scores.values()))),
            }

        aggregate = self.aggregate(by_system)
        result = {"systems": by_system, "aggregate": aggregate}
        self.history.append(result)
        return result

    def _fallback_profile(self, system: Any) -> dict[str, Any]:
        measurements = system.system_measurements() if hasattr(system, "system_measurements") else {}
        return {
            "state": measurements.get("pci_proxy", 0.0),
            "content": measurements.get("phi_proxy", 0.0),
            "self_model": measurements.get("self_model_stability", 0.0),
            "agency": measurements.get("agency_proxy", 0.0),
            "temporal_continuity": measurements.get("temporal_continuity", 0.0),
            "details": measurements,
        }

    def aggregate(self, by_system: dict[str, Any]) -> dict[str, Any]:
        if not by_system:
            return {"scores": {dim: 0.0 for dim in DIMENSIONS}, "mean": 0.0, "anomalies": []}
        aggregate_scores = {}
        for dim in DIMENSIONS:
            aggregate_scores[dim] = float(np.mean([payload["scores"][dim] for payload in by_system.values()]))
        anomalies = []
        for name, payload in by_system.items():
            for anomaly in payload["anomalies"]:
                anomalies.append({"system": name, **anomaly})
        return {
            "scores": aggregate_scores,
            "mean": float(np.mean(list(aggregate_scores.values()))),
            "anomalies": anomalies,
        }

    def detect_anomalies(self, scores: dict[str, float]) -> list[dict[str, Any]]:
        anomalies: list[dict[str, Any]] = []
        if scores["self_model"] > 0.7 and scores["agency"] < 0.3:
            anomalies.append(
                {
                    "type": "high_self_low_agency",
                    "severity": "medium",
                    "description": "Self-model proxy is high while agency proxy is low.",
                }
            )
        if scores["content"] > 0.7 and scores["state"] < 0.3:
            anomalies.append(
                {
                    "type": "high_content_low_state",
                    "severity": "high",
                    "description": "Content richness proxy is high without a stable state proxy.",
                }
            )
        if scores["temporal_continuity"] > 0.7 and scores["self_model"] < 0.3:
            anomalies.append(
                {
                    "type": "high_continuity_low_self",
                    "severity": "medium",
                    "description": "Temporal continuity proxy is high while self-model proxy is low.",
                }
            )
        return anomalies

    def recommendations(self, result: dict[str, Any]) -> list[dict[str, str]]:
        recs: list[dict[str, str]] = []
        scores = result["aggregate"]["scores"]
        weakest = min(scores, key=scores.get)
        if scores[weakest] < 0.45:
            recs.append(
                {
                    "priority": "high",
                    "dimension": weakest,
                    "suggestion": f"Prioritize experiments that improve the {weakest} proxy.",
                }
            )
        for anomaly in result["aggregate"]["anomalies"][:4]:
            if anomaly["type"] == "high_self_low_agency":
                recs.append(
                    {
                        "priority": "medium",
                        "dimension": "agency",
                        "suggestion": "Run more action-result intervention probes for the affected system.",
                    }
                )
            elif anomaly["type"] == "high_content_low_state":
                recs.append(
                    {
                        "priority": "high",
                        "dimension": "state",
                        "suggestion": "Increase gating or homeostatic constraints before expanding content capacity.",
                    }
                )
        return recs

