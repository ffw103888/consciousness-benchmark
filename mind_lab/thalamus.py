from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .utils import binary_lz_complexity, clamp01, entropy, safe_corr


@dataclass
class InformationItem:
    source: str
    vector: np.ndarray
    activation: float
    timestamp: float = field(default_factory=time.time)
    importance: float | None = None

    def __post_init__(self) -> None:
        self.vector = np.asarray(self.vector, dtype=float)
        if self.importance is None:
            self.importance = float(self.activation)


class RuleBasedGating:
    def evaluate(self, candidate: InformationItem, context: dict[str, Any]) -> float:
        recent = context.get("recent_vectors", [])
        if recent:
            similarities = [self.similarity(candidate.vector, vec) for vec in recent[-16:]]
            novelty = 1.0 - float(np.mean(similarities))
        else:
            novelty = 1.0
        goal = context.get("goal_vector")
        relevance = self.similarity(candidate.vector, goal) if goal is not None else 0.5
        intensity = clamp01(candidate.activation)
        attention_bias = float(context.get("attention_bias", {}).get(candidate.source, 0.5))
        return clamp01(0.34 * novelty + 0.3 * relevance + 0.22 * intensity + 0.14 * attention_bias)

    @staticmethod
    def similarity(a: np.ndarray, b: np.ndarray | None) -> float:
        if b is None:
            return 0.0
        denom = float(np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9
        return clamp01((float(np.dot(a, b)) / denom + 1.0) / 2.0)


class ReticularNucleus:
    def __init__(self, config: dict[str, Any]):
        self.policy = RuleBasedGating()
        self.threshold = float(config.get("initial_threshold", 0.52))
        self.inhibition_strength = float(config.get("inhibition_strength", 0.45))
        self.adaptation_rate = float(config.get("threshold_adaptation_rate", 0.08))
        self.history: list[dict[str, Any]] = []

    def gate(self, candidates: list[InformationItem], context: dict[str, Any]) -> dict[str, Any]:
        if not candidates:
            return {"gated": [], "inhibited": [], "threshold": self.threshold, "scores": []}
        scores = np.array([self.policy.evaluate(c, context) for c in candidates], dtype=float)
        base = float(np.percentile(scores, 78))
        arousal = float(context.get("arousal", 0.5))
        load = float(context.get("workspace_load", 0.0))
        inhibition_modulation = 0.18 * (self.inhibition_strength - 0.45)
        target = base - 0.14 * (arousal - 0.5) + 0.12 * load + inhibition_modulation
        self.threshold = float((1.0 - self.adaptation_rate) * self.threshold + self.adaptation_rate * target)
        gated: list[InformationItem] = []
        inhibited: list[InformationItem] = []
        for item, score in zip(candidates, scores):
            item.importance = float(score)
            if score >= self.threshold:
                gated.append(item)
            else:
                item.activation *= 1.0 - self.inhibition_strength
                inhibited.append(item)
        record = {
            "threshold": self.threshold,
            "candidate_count": len(candidates),
            "gated_count": len(gated),
            "mean_score": float(np.mean(scores)),
        }
        self.history.append(record)
        return {"gated": gated, "inhibited": inhibited, "threshold": self.threshold, "scores": scores.tolist()}


class GlobalWorkspace:
    def __init__(self, capacity: int = 96, decay_rate: float = 0.045):
        self.capacity = int(capacity)
        self.decay_rate = float(decay_rate)
        self.contents: list[InformationItem] = []
        self.broadcast_history: list[dict[str, Any]] = []

    def update(self, gated: list[InformationItem]) -> dict[str, Any]:
        for item in gated:
            if len(self.contents) < self.capacity:
                self.contents.append(item)
            else:
                weakest_idx, weakest = min(
                    enumerate(self.contents),
                    key=lambda pair: float(pair[1].importance or 0.0),
                )
                if float(item.importance or 0.0) > float(weakest.importance or 0.0):
                    del self.contents[weakest_idx]
                    self.contents.append(item)
        for item in self.contents:
            item.importance = float(item.importance or 0.0) * (1.0 - self.decay_rate)
        self.contents = [c for c in self.contents if float(c.importance or 0.0) > 0.06]
        if self.contents:
            matrix = np.stack([c.vector for c in self.contents])
            broadcast_vector = matrix.mean(axis=0)
            mean_importance = float(np.mean([float(c.importance or 0.0) for c in self.contents]))
        else:
            broadcast_vector = np.zeros(32)
            mean_importance = 0.0
        broadcast = {
            "vector": broadcast_vector,
            "size": len(self.contents),
            "mean_importance": mean_importance,
            "sources": [c.source for c in self.contents[-16:]],
        }
        self.broadcast_history.append(broadcast)
        if len(self.broadcast_history) > 5000:
            del self.broadcast_history[:1000]
        return broadcast

    def load(self) -> float:
        return len(self.contents) / max(self.capacity, 1)

    def recent_vectors(self, window: int = 16) -> list[np.ndarray]:
        return [b["vector"] for b in self.broadcast_history[-window:]]


class ThalamicLayer:
    def __init__(self, rng: np.random.Generator, dim: int = 32):
        self.rng = rng
        self.dim = int(dim)
        self.modality_basis = {
            "visual": self._unit(),
            "auditory": self._unit(),
            "proprioceptive": self._unit(),
            "interoceptive": self._unit(),
        }

    def _unit(self) -> np.ndarray:
        vec = self.rng.normal(size=self.dim)
        return vec / (np.linalg.norm(vec) + 1e-9)

    def synthetic_input(self, t: int) -> dict[str, np.ndarray]:
        phase = t / 24.0
        data = {}
        for idx, (name, basis) in enumerate(self.modality_basis.items()):
            intensity = 0.55 + 0.35 * np.sin(phase + idx * 1.7) + 0.08 * self.rng.normal()
            data[name] = basis * intensity + 0.16 * self.rng.normal(size=self.dim)
        if t % 97 == 0:
            data["visual"] = data["visual"] + 1.2 * self.modality_basis["visual"]
        return data

    def process(self, sensory_input: dict[str, np.ndarray]) -> tuple[list[InformationItem], dict[str, Any]]:
        candidates: list[InformationItem] = []
        intensities: dict[str, float] = {}
        for source, vector in sensory_input.items():
            intensity = float(np.linalg.norm(vector) / np.sqrt(self.dim))
            intensities[source] = clamp01(intensity)
            candidates.append(InformationItem(source=source, vector=vector, activation=clamp01(intensity)))
        arousal = clamp01(float(np.mean(list(intensities.values()))) if intensities else 0.0)
        attention_bias = {k: clamp01(v / (arousal + 1e-6) * 0.5) for k, v in intensities.items()}
        return candidates, {"arousal": arousal, "attention_bias": attention_bias}


class CorticalModule:
    def __init__(self, name: str, rng: np.random.Generator, dim: int):
        self.name = name
        self.rng = rng
        self.weights = rng.normal(scale=0.22, size=(dim, dim))
        self.state = np.zeros(dim)
        self.candidates: list[InformationItem] = []

    def process(self, broadcast: dict[str, Any]) -> np.ndarray:
        vec = np.asarray(broadcast["vector"], dtype=float)
        self.state = np.tanh(0.78 * self.state + self.weights @ vec / max(len(vec), 1))
        if np.linalg.norm(self.state) > 0.2:
            self.candidates = [
                InformationItem(
                    source=self.name,
                    vector=self.state + 0.05 * self.rng.normal(size=self.state.shape),
                    activation=clamp01(float(np.linalg.norm(self.state) / np.sqrt(self.state.size))),
                )
            ]
        else:
            self.candidates = []
        return self.state


class ActionOutcomeLoop:
    """Minimal explicit action-outcome loop for agency ablations."""

    def __init__(self, rng: np.random.Generator, dim: int, variant: str = "minimal", learning_rate: float = 0.06):
        self.rng = rng
        self.dim = int(dim)
        self.variant = variant
        self.learning_enabled = variant in {"learning", "full"}
        self.intention_enabled = variant in {"intention", "full"}
        self.learning_rate = float(learning_rate)
        self.policy = rng.normal(scale=0.18, size=(dim, dim))
        self.pending_action: np.ndarray | None = None
        self.last_action: np.ndarray | None = None
        self.actual_gain = 1.0
        self.predicted_gain = 0.32 if self.learning_enabled else 0.55
        self.action_noise = 0.006 if self.intention_enabled else 0.015
        self.prediction_errors: list[float] = []
        self.action_norms: list[float] = []
        self.intention_alignments: list[float] = []

    def apply_pending(self, sensory: dict[str, np.ndarray]) -> tuple[dict[str, np.ndarray], np.ndarray | None]:
        if self.pending_action is None:
            return sensory, None
        action = self.pending_action.copy()
        self.last_action = action
        predicted_effect = self.predicted_gain * action
        actual_effect = self.actual_gain * action + self.action_noise * self.rng.normal(size=self.dim)
        updated = {key: value.copy() for key, value in sensory.items()}
        updated["proprioceptive"] = updated.get("proprioceptive", np.zeros(self.dim)) + actual_effect
        return updated, predicted_effect

    def observe(self, expected_effect: np.ndarray | None, observed_delta: np.ndarray | None) -> None:
        if expected_effect is None or observed_delta is None:
            return
        denom = float(np.linalg.norm(expected_effect) + np.linalg.norm(observed_delta)) + 1e-9
        error = float(np.linalg.norm(expected_effect - observed_delta) / denom)
        self.prediction_errors.append(clamp01(error))
        if self.learning_enabled and self.last_action is not None:
            action_energy = float(np.dot(self.last_action, self.last_action)) + 1e-9
            observed_gain = float(np.dot(observed_delta, self.last_action) / action_energy)
            self.predicted_gain = float(
                (1.0 - self.learning_rate) * self.predicted_gain + self.learning_rate * observed_gain
            )
        if len(self.prediction_errors) > 2048:
            del self.prediction_errors[:512]

    def decide_next(self, broadcast_vector: np.ndarray, goal_vector: np.ndarray | None = None) -> None:
        policy_drive = self.policy @ broadcast_vector / max(len(broadcast_vector), 1)
        if self.intention_enabled and goal_vector is not None:
            goal = goal_vector / (np.linalg.norm(goal_vector) + 1e-9)
            policy_drive = 0.48 * policy_drive + 0.52 * goal
        else:
            policy_drive = policy_drive + 0.28 * self.rng.normal(size=self.dim)
        raw = np.tanh(policy_drive)
        norm = float(np.linalg.norm(raw))
        if norm <= 1e-9:
            self.pending_action = np.zeros(self.dim)
        else:
            scale = 0.72 if self.intention_enabled else 0.42
            self.pending_action = scale * raw / np.sqrt(self.dim)
        self.action_norms.append(float(np.linalg.norm(self.pending_action)))
        if goal_vector is not None and self.pending_action is not None and np.linalg.norm(self.pending_action) > 1e-9:
            goal = goal_vector / (np.linalg.norm(goal_vector) + 1e-9)
            alignment = (float(np.dot(self.pending_action, goal)) / (np.linalg.norm(self.pending_action) + 1e-9) + 1.0) / 2.0
            self.intention_alignments.append(clamp01(alignment))
        if len(self.action_norms) > 2048:
            del self.action_norms[:512]
        if len(self.intention_alignments) > 2048:
            del self.intention_alignments[:512]

    def score(self) -> float:
        if not self.prediction_errors:
            return 0.0
        predictability = 1.0 - float(np.mean(self.prediction_errors[-128:]))
        action_presence = clamp01(float(np.mean(self.action_norms[-128:])) * 8.0) if self.action_norms else 0.0
        if self.intention_enabled:
            intention = float(np.mean(self.intention_alignments[-128:])) if self.intention_alignments else 0.0
            return clamp01(0.58 * predictability + 0.2 * action_presence + 0.22 * intention)
        return clamp01(0.72 * predictability + 0.28 * action_presence)

    def diagnostics(self) -> dict[str, float]:
        return {
            "action_prediction_error": float(np.mean(self.prediction_errors[-128:])) if self.prediction_errors else 1.0,
            "action_predicted_gain": float(self.predicted_gain),
            "action_intention_alignment": float(np.mean(self.intention_alignments[-128:])) if self.intention_alignments else 0.0,
            "action_presence": clamp01(float(np.mean(self.action_norms[-128:])) * 8.0) if self.action_norms else 0.0,
        }


class ThalamusInspiredArchitecture:
    def __init__(self, config: dict[str, Any], seed: int = 3):
        self.config = config
        self.rng = np.random.default_rng(seed)
        self.dim = int(config.get("dim", 32))
        self.enable_reticular = bool(config.get("enable_reticular", True))
        self.enable_workspace = bool(config.get("enable_workspace", True))
        self.enable_core = bool(config.get("enable_core", True))
        self.enable_matrix = bool(config.get("enable_matrix", True))
        self.enable_cortical_feedback = bool(config.get("enable_cortical_feedback", True))
        self.action_loop_variant = str(config.get("action_loop_variant", "minimal"))
        self.enable_action_loop = bool(config.get("enable_action_loop", False)) and self.action_loop_variant != "none"
        self.measurement_window = int(config.get("measurement_window", 256))
        self.thalamus = ThalamicLayer(self.rng, self.dim)
        self.reticular = ReticularNucleus(config)
        self.workspace = GlobalWorkspace(capacity=int(config.get("workspace_capacity", 96)))
        self.cortical_modules = [
            CorticalModule("prefrontal", self.rng, self.dim),
            CorticalModule("parietal", self.rng, self.dim),
            CorticalModule("temporal", self.rng, self.dim),
        ]
        goal = self.rng.normal(size=self.dim)
        self.goal_vector = goal / (np.linalg.norm(goal) + 1e-9)
        self.action_loop = (
            ActionOutcomeLoop(
                self.rng,
                self.dim,
                variant=self.action_loop_variant,
                learning_rate=float(config.get("action_learning_rate", 0.06)),
            )
            if self.enable_action_loop
            else None
        )
        self.transient_broadcast_history: list[dict[str, Any]] = []
        self.step_count = 0
        self.history: list[dict[str, Any]] = []

    def step(self) -> dict[str, Any]:
        base_sensory = self.thalamus.synthetic_input(self.step_count)
        expected_effect = None
        if self.action_loop is not None:
            sensory, expected_effect = self.action_loop.apply_pending(base_sensory)
        else:
            sensory = base_sensory

        core_candidates, modulation = self.thalamus.process(sensory)
        if self.action_loop is not None and expected_effect is not None:
            observed_delta = sensory.get("proprioceptive", np.zeros(self.dim)) - base_sensory.get("proprioceptive", np.zeros(self.dim))
            self.action_loop.observe(expected_effect, observed_delta)
        if not self.enable_core:
            core_candidates = []
        if not self.enable_matrix:
            modulation = {
                "arousal": 0.5,
                "attention_bias": {key: 0.5 for key in sensory.keys()},
            }
        cortical_candidates: list[InformationItem] = []
        if self.enable_cortical_feedback:
            for module in self.cortical_modules:
                cortical_candidates.extend(module.candidates)
        candidates = core_candidates + cortical_candidates
        context = {
            "arousal": modulation["arousal"],
            "attention_bias": modulation["attention_bias"],
            "workspace_load": self.workspace.load(),
            "recent_vectors": self.workspace.recent_vectors(),
            "goal_vector": self.goal_vector,
        }
        if self.enable_reticular:
            gating = self.reticular.gate(candidates, context)
        else:
            for candidate in candidates:
                candidate.importance = float(candidate.activation)
            gating = {
                "gated": candidates,
                "inhibited": [],
                "threshold": 0.0,
                "scores": [float(c.activation) for c in candidates],
            }

        if self.enable_workspace:
            broadcast = self.workspace.update(gating["gated"])
        else:
            broadcast = self.transient_broadcast(gating["gated"])
            self.transient_broadcast_history.append(broadcast)
            if len(self.transient_broadcast_history) > 5000:
                del self.transient_broadcast_history[:1000]

        cortical_norms = []
        for module in self.cortical_modules:
            state = module.process(broadcast)
            cortical_norms.append(float(np.linalg.norm(state)))
        if self.action_loop is not None:
            self.action_loop.decide_next(np.asarray(broadcast["vector"], dtype=float), self.goal_vector)
        self.step_count += 1
        record = {
            "step": self.step_count,
            "arousal": modulation["arousal"],
            "threshold": gating["threshold"],
            "gated_count": len(gating["gated"]),
            "inhibited_count": len(gating["inhibited"]),
            "workspace_size": broadcast["size"],
            "workspace_importance": broadcast["mean_importance"],
            "source_count": len(set(broadcast.get("sources", []))),
            "cortical_norm": float(np.mean(cortical_norms)),
            "action_agency": self.action_loop.score() if self.action_loop is not None else 0.0,
        }
        self.history.append(record)
        if len(self.history) > 5000:
            del self.history[:1000]
        return record

    def transient_broadcast(self, items: list[InformationItem]) -> dict[str, Any]:
        if not items:
            vector = np.zeros(self.dim)
            mean_importance = 0.0
        else:
            matrix = np.stack([item.vector for item in items])
            vector = matrix.mean(axis=0)
            mean_importance = float(np.mean([float(item.importance or 0.0) for item in items]))
        return {
            "vector": vector,
            "size": len(items),
            "mean_importance": mean_importance,
            "sources": [item.source for item in items[-16:]],
        }

    def run_steps(self, steps: int) -> dict[str, Any]:
        records = [self.step() for _ in range(int(steps))]
        return {
            "step": self.step_count,
            "workspace_size": self.workspace.broadcast_history[-1]["size"] if self.workspace.broadcast_history else 0,
            "mean_gated": float(np.mean([r["gated_count"] for r in records])) if records else 0.0,
            "mean_threshold": float(np.mean([r["threshold"] for r in records])) if records else self.reticular.threshold,
            "mean_arousal": float(np.mean([r["arousal"] for r in records])) if records else 0.0,
        }

    def system_measurements(self) -> dict[str, float]:
        recent = self.history[-max(1, self.measurement_window) :]
        if not recent:
            return {
                "phi_proxy": 0.0,
                "pci_proxy": 0.0,
                "self_model_stability": 0.0,
                "boundary_self_proxy": 0.0,
                "temporal_self_proxy": 0.0,
                "ownership_self_proxy": 0.0,
                "legacy_self_model_stability": 0.0,
                "temporal_continuity": 0.0,
            }
        arousal = np.array([r["arousal"] for r in recent], dtype=float)
        threshold = np.array([r["threshold"] for r in recent], dtype=float)
        workspace_size = np.array([r["workspace_size"] for r in recent], dtype=float)
        gated = np.array([r["gated_count"] for r in recent], dtype=float)
        cortical = np.array([r["cortical_norm"] for r in recent], dtype=float)
        source_count = np.array([r.get("source_count", 0.0) for r in recent], dtype=float)
        binary = (gated > np.mean(gated)).astype(int)
        workspace_load = self.workspace.load() if self.enable_workspace else 0.0
        phi = clamp01(0.45 * abs(safe_corr(arousal, workspace_size)) + 0.35 * entropy(cortical, bins=12) + 0.2 * workspace_load)
        pci = clamp01(binary_lz_complexity(binary) / 1.2)
        threshold_stability = clamp01(1.0 - float(np.std(threshold)) * 4.0)
        workspace_presence = clamp01(float(np.mean(workspace_size)) / max(float(self.workspace.capacity) * 0.1, 1.0)) if self.enable_workspace else 0.0
        workspace_temporal = clamp01(1.0 - float(np.std(workspace_size) / (np.mean(workspace_size) + 1e-6))) if self.enable_workspace else 0.0
        source_diversity = clamp01(float(np.mean(source_count)) / 5.0)
        cortical_presence = clamp01(float(np.mean(cortical)) / 0.45)
        reticular_factor = threshold_stability if self.enable_reticular else 0.0
        legacy_self_model_stability = clamp01(
            0.3 * reticular_factor
            + 0.27 * workspace_temporal
            + 0.18 * workspace_presence
            + 0.15 * source_diversity
            + 0.1 * cortical_presence
        )
        temporal = clamp01(1.0 - float(np.std(workspace_size) / (np.mean(workspace_size) + 1e-6)))
        gating_coordination = clamp01(abs(safe_corr(threshold, gated))) if self.enable_reticular else 0.0
        action_agency = self.action_loop.score() if self.action_loop is not None else 0.0
        if self.enable_workspace:
            boundary_self = clamp01(
                0.28 * reticular_factor
                + 0.28 * workspace_presence
                + 0.24 * workspace_temporal
                + 0.14 * source_diversity
                + 0.06 * cortical_presence
            )
        else:
            boundary_self = clamp01(
                0.18 * reticular_factor
                + 0.12 * source_diversity
                + 0.08 * cortical_presence
            )
        temporal_self = clamp01(0.55 * temporal + 0.25 * reticular_factor + 0.2 * source_diversity)
        action_presence = 0.0
        if self.action_loop is not None:
            diagnostics = self.action_loop.diagnostics()
            action_presence = diagnostics.get("action_presence", 0.0)
        ownership_self = clamp01(0.72 * action_agency + 0.28 * action_presence)
        self_model_stability = boundary_self
        legacy_agency = clamp01(0.35 * gating_coordination + 0.65 * action_agency) if self.enable_action_loop else gating_coordination
        agency = action_agency
        measurements = {
            "phi_proxy": phi,
            "pci_proxy": pci,
            "self_model_stability": self_model_stability,
            "boundary_self_proxy": boundary_self,
            "temporal_self_proxy": temporal_self,
            "ownership_self_proxy": ownership_self,
            "legacy_self_model_stability": legacy_self_model_stability,
            "temporal_continuity": temporal,
            "agency_proxy": agency,
            "legacy_agency_proxy": legacy_agency,
            "gating_coordination_proxy": gating_coordination,
            "gating_agency_proxy": gating_coordination,
            "action_agency_proxy": action_agency,
            "threshold_stability": threshold_stability,
            "workspace_presence": workspace_presence,
            "workspace_temporal": workspace_temporal,
            "source_diversity": source_diversity,
            "cortical_presence": cortical_presence,
            "instability": clamp01(1.0 - threshold_stability + float(np.std(arousal))),
            "avoidance_rate": 0.0,
            "negative_value": 0.0,
        }
        if self.action_loop is not None:
            measurements.update(self.action_loop.diagnostics())
        return measurements

    def evaluation_profile(self) -> dict[str, Any]:
        m = self.system_measurements()
        history = self.workspace.broadcast_history if self.enable_workspace else self.transient_broadcast_history
        source_count = len({src for b in history[-64:] for src in b.get("sources", [])})
        return {
            "state": clamp01(0.42 * m["pci_proxy"] + 0.35 * m["phi_proxy"] + 0.23 * (1.0 - m["instability"])),
            "content": clamp01(0.6 * min(source_count / 7.0, 1.0) + 0.4 * m["phi_proxy"]),
            "self_model": clamp01(m["self_model_stability"]),
            "agency": clamp01(m["agency_proxy"]),
            "temporal_continuity": clamp01(m["temporal_continuity"]),
            "details": m,
        }

    def __setstate__(self, state: dict[str, Any]) -> None:
        self.__dict__.update(state)
        config = getattr(self, "config", {}) or {}
        if not hasattr(self, "enable_reticular"):
            self.enable_reticular = bool(config.get("enable_reticular", True))
        if not hasattr(self, "enable_workspace"):
            self.enable_workspace = bool(config.get("enable_workspace", True))
        if not hasattr(self, "enable_core"):
            self.enable_core = bool(config.get("enable_core", True))
        if not hasattr(self, "enable_matrix"):
            self.enable_matrix = bool(config.get("enable_matrix", True))
        if not hasattr(self, "enable_cortical_feedback"):
            self.enable_cortical_feedback = bool(config.get("enable_cortical_feedback", True))
        if not hasattr(self, "action_loop_variant"):
            self.action_loop_variant = str(config.get("action_loop_variant", "minimal"))
        if not hasattr(self, "enable_action_loop"):
            self.enable_action_loop = bool(config.get("enable_action_loop", False)) and self.action_loop_variant != "none"
        if not hasattr(self, "measurement_window"):
            self.measurement_window = int(config.get("measurement_window", 256))
        if not hasattr(self, "action_loop"):
            self.action_loop = None
        if not hasattr(self, "transient_broadcast_history"):
            self.transient_broadcast_history = []
