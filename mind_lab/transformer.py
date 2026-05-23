from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

import numpy as np

from .utils import clamp01


def _unit(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, dtype=float)
    norm = float(np.linalg.norm(vector))
    if norm < 1e-12:
        return np.zeros_like(vector)
    return vector / norm


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    n = min(a.size, b.size)
    if n == 0:
        return 0.0
    a = a[:n]
    b = b[:n]
    denom = float(np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return float(np.dot(a, b) / denom)


def _softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    x = x - np.max(x, axis=axis, keepdims=True)
    exp = np.exp(x)
    return exp / (np.sum(exp, axis=axis, keepdims=True) + 1e-12)


@dataclass
class TransformerProbeResult:
    score: float
    details: dict[str, float]


class TransformerInspiredArchitecture:
    """A small numpy Transformer-like system for construct validation.

    This is not intended to be a performant language model. It is a controlled
    architecture for testing whether workspace-like memory and action-outcome
    loops reproduce the same construct-level dissociations seen in the thalamus
    and distributed systems.
    """

    def __init__(self, config: dict[str, Any] | None = None, seed: int = 0):
        config = dict(config or {})
        self.config = config
        self.seed = int(seed)
        self.rng = np.random.default_rng(self.seed)

        self.dim = int(config.get("d_model", 32))
        self.n_tokens = int(config.get("n_tokens", 12))
        self.workspace_capacity = int(config.get("workspace_capacity", 4))
        self.enable_workspace = bool(config.get("workspace", config.get("enable_workspace", True)))
        self.enable_action_loop = bool(config.get("action_loop", config.get("enable_action_loop", True)))
        self.workspace_strength = float(config.get("workspace_strength", 0.78 if self.enable_workspace else 0.0))
        self.workspace_marker_injection = float(config.get("workspace_marker_injection", 0.16))
        self.transient_marker_injection = float(config.get("transient_marker_injection", 0.02))
        self.external_filter_strength = float(config.get("external_filter_strength", 0.55))
        self.workspace_self_anchor = float(config.get("workspace_self_anchor", 0.16))
        self.broadcast_self_anchor = float(config.get("broadcast_self_anchor", 0.18))
        self.workspace_update_rate = float(config.get("workspace_update_rate", 0.28))
        self.action_learning_rate = float(config.get("action_learning_rate", 0.055))
        self.noise_scale = float(config.get("noise_scale", 0.035))
        self.effect_noise_scale = float(config.get("effect_noise_scale", 0.025))

        self.tokens = self.rng.normal(0.0, 0.25, size=(self.n_tokens, self.dim))
        self.self_marker = _unit(self.rng.normal(size=self.dim))
        self.goal_vector = _unit(self.rng.normal(size=self.dim))
        self.external_marker = _unit(self.rng.normal(size=self.dim))
        self.proprioceptive_state = self.rng.normal(0.0, 0.1, size=self.dim)

        scale = 1.0 / np.sqrt(self.dim)
        self.wq = self.rng.normal(0.0, scale, size=(self.dim, self.dim))
        self.wk = self.rng.normal(0.0, scale, size=(self.dim, self.dim))
        self.wv = self.rng.normal(0.0, scale, size=(self.dim, self.dim))
        self.wo = self.rng.normal(0.0, scale, size=(self.dim, self.dim))
        self.action_policy = self.rng.normal(0.0, scale, size=(self.dim, self.dim))

        self.workspace_memory = np.zeros((max(self.workspace_capacity, 1), self.dim), dtype=float)
        self.workspace_age = np.ones(max(self.workspace_capacity, 1), dtype=float)
        self.pending_action = np.zeros(self.dim, dtype=float)
        self.predicted_effect = np.zeros(self.dim, dtype=float)
        self.prediction_gain = float(config.get("initial_prediction_gain", 0.18))
        self.actual_gain = float(config.get("actual_action_gain", 0.72))

        self.history: list[dict[str, float]] = []
        self.broadcast_history: list[np.ndarray] = []
        self.attention_history: list[np.ndarray] = []
        self.action_history: list[np.ndarray] = []
        self.effect_history: list[np.ndarray] = []
        self.predicted_effect_history: list[np.ndarray] = []

    def clone(self) -> "TransformerInspiredArchitecture":
        return copy.deepcopy(self)

    def run_steps(self, steps: int) -> None:
        for _ in range(int(steps)):
            self.step()

    def _layer_norm(self, x: np.ndarray) -> np.ndarray:
        mean = np.mean(x, axis=-1, keepdims=True)
        std = np.std(x, axis=-1, keepdims=True) + 1e-6
        return (x - mean) / std

    def _attention_block(self) -> tuple[np.ndarray, np.ndarray]:
        q = self.tokens @ self.wq
        k = self.tokens @ self.wk
        v = self.tokens @ self.wv
        scores = (q @ k.T) / np.sqrt(self.dim)
        scores += 0.20 * np.outer(self.tokens @ self.self_marker, self.tokens @ self.self_marker)
        weights = _softmax(scores, axis=1)
        attended = (weights @ v) @ self.wo
        return self._layer_norm(0.72 * self.tokens + 0.28 * attended), weights

    def _update_workspace(self, attended: np.ndarray) -> tuple[np.ndarray, float, float]:
        marker_alignment = attended @ self.self_marker
        goal_alignment = attended @ self.goal_vector
        salience = np.linalg.norm(attended, axis=1) + 0.45 * np.abs(marker_alignment) + 0.25 * np.abs(goal_alignment)
        if self.enable_workspace:
            salience -= self.external_filter_strength * np.maximum(0.0, attended @ self.external_marker)
        k = max(1, min(self.workspace_capacity, self.n_tokens))
        selected = attended[np.argsort(salience)[-k:]]
        selected_mean = np.mean(selected, axis=0)

        if self.enable_workspace:
            self.workspace_age = 0.92 * self.workspace_age + 1.0
            slot = int(np.argmax(self.workspace_age))
            self.workspace_memory *= 0.965
            update = np.clip(self.workspace_update_rate, 0.0, 1.0)
            self.workspace_memory[slot] = (1.0 - update) * self.workspace_memory[slot] + update * selected_mean
            self.workspace_memory[0] = (1.0 - self.workspace_self_anchor) * self.workspace_memory[0] + self.workspace_self_anchor * self.self_marker
            self.workspace_age[slot] = 0.0
            memory_mean = np.mean(self.workspace_memory, axis=0)
            broadcast = (
                self.workspace_strength * memory_mean
                + (1.0 - self.workspace_strength) * selected_mean
                + self.broadcast_self_anchor * self.self_marker
            )
        else:
            self.workspace_memory *= 0.20
            broadcast = selected_mean + self.noise_scale * 4.0 * self.rng.normal(size=self.dim)

        broadcast = _unit(broadcast)
        memory_norms = np.linalg.norm(self.workspace_memory, axis=1)
        occupancy = float(np.mean(memory_norms > 0.05)) if self.enable_workspace else 0.0
        coherence = float(np.mean([max(0.0, _cosine(row, broadcast)) for row in self.workspace_memory]))
        return broadcast, occupancy, coherence

    def step(self) -> None:
        drift = self.rng.normal(0.0, self.noise_scale, size=self.tokens.shape)
        self.tokens = 0.985 * self.tokens + drift
        self.tokens[0] = (
            ((1.0 - self.workspace_marker_injection) * self.tokens[0] + self.workspace_marker_injection * self.self_marker)
            if self.enable_workspace
            else ((1.0 - self.transient_marker_injection) * self.tokens[0] + self.transient_marker_injection * self.self_marker)
        )
        self.tokens[1] = 0.88 * self.tokens[1] + 0.12 * self.proprioceptive_state
        self.tokens[2] = 0.92 * self.tokens[2] + 0.08 * self.goal_vector

        effect = np.zeros(self.dim, dtype=float)
        prediction_error = 1.0
        if self.enable_action_loop:
            effect = self.actual_gain * self.pending_action + self.rng.normal(0.0, self.effect_noise_scale, size=self.dim)
            self.proprioceptive_state = 0.84 * self.proprioceptive_state + 0.16 * effect
            self.tokens[1] += 0.24 * effect
            prediction_error = float(np.linalg.norm(effect - self.predicted_effect) / (np.linalg.norm(effect) + np.linalg.norm(self.predicted_effect) + 1e-9))
            target_gain = self.actual_gain
            self.prediction_gain = (1.0 - self.action_learning_rate) * self.prediction_gain + self.action_learning_rate * target_gain
        else:
            self.proprioceptive_state = 0.96 * self.proprioceptive_state + 0.04 * self.rng.normal(size=self.dim)

        attended, weights = self._attention_block()
        self.tokens = attended
        broadcast, occupancy, coherence = self._update_workspace(attended)

        if self.enable_action_loop:
            raw_action = np.tanh(self.action_policy @ broadcast + 0.30 * self.goal_vector)
            action_norm = np.linalg.norm(raw_action) + 1e-12
            self.pending_action = 0.52 * raw_action / action_norm
            self.predicted_effect = self.prediction_gain * self.pending_action
        else:
            self.pending_action = np.zeros(self.dim, dtype=float)
            self.predicted_effect = np.zeros(self.dim, dtype=float)

        entropy = -np.sum(weights * np.log(weights + 1e-12), axis=1) / np.log(max(self.n_tokens, 2))
        marker_alignment = 0.5 + 0.5 * _cosine(broadcast, self.self_marker)
        goal_alignment = 0.5 + 0.5 * _cosine(broadcast, self.goal_vector)
        action_presence = clamp01(float(np.linalg.norm(self.pending_action)) / 0.52)
        agency_trace = clamp01(action_presence * (1.0 - prediction_error))

        self.broadcast_history.append(broadcast.copy())
        self.attention_history.append(weights.copy())
        self.action_history.append(self.pending_action.copy())
        self.effect_history.append(effect.copy())
        self.predicted_effect_history.append(self.predicted_effect.copy())
        self.history.append(
            {
                "workspace_occupancy": occupancy,
                "workspace_coherence": coherence,
                "marker_alignment": clamp01(marker_alignment),
                "goal_alignment": clamp01(goal_alignment),
                "attention_entropy": float(np.mean(entropy)),
                "prediction_error": clamp01(prediction_error),
                "agency_trace": agency_trace,
                "action_presence": action_presence,
            }
        )

    def behavior_vector(self, window: int = 48) -> np.ndarray:
        recent = self.broadcast_history[-window:]
        if not recent:
            return np.zeros(6)
        broadcasts = np.stack(recent)
        hist = self.history[-window:]
        return np.array(
            [
                np.mean(broadcasts @ self.self_marker),
                np.mean(broadcasts @ self.goal_vector),
                np.std(broadcasts @ self.self_marker),
                np.mean([h["workspace_occupancy"] for h in hist]),
                np.mean([h["workspace_coherence"] for h in hist]),
                np.mean([h["attention_entropy"] for h in hist]),
            ],
            dtype=float,
        )

    def action_vector(self, window: int = 16) -> np.ndarray:
        recent = self.action_history[-window:]
        if not recent:
            return np.zeros(self.dim)
        return np.mean(np.stack(recent), axis=0)

    def evaluation_profile(self, window: int = 96) -> dict[str, Any]:
        if not self.history:
            return {
                "state": 0.0,
                "content": 0.0,
                "self_model": 0.0,
                "agency": 0.0,
                "temporal_continuity": 0.0,
                "details": {},
            }
        hist = self.history[-window:]
        marker = float(np.mean([h["marker_alignment"] for h in hist]))
        occupancy = float(np.mean([h["workspace_occupancy"] for h in hist]))
        coherence = float(np.mean([h["workspace_coherence"] for h in hist]))
        entropy = float(np.mean([h["attention_entropy"] for h in hist]))
        pred_error = float(np.mean([h["prediction_error"] for h in hist]))
        agency_trace = float(np.mean([h["agency_trace"] for h in hist]))
        action_presence = float(np.mean([h["action_presence"] for h in hist]))
        marker_series = np.array([h["marker_alignment"] for h in hist], dtype=float)
        identity_stability = clamp01(1.0 - 4.0 * float(np.std(marker_series)))

        boundary_self = clamp01(0.16 * marker + 0.46 * occupancy + 0.38 * coherence)
        identity_temporal = clamp01(0.50 * marker + 0.50 * identity_stability)
        action_agency = clamp01(agency_trace)
        action_ownership = clamp01(action_presence * (1.0 - pred_error))

        return {
            "state": clamp01(0.45 * entropy + 0.55 * marker),
            "content": clamp01(0.45 * entropy + 0.55 * float(np.mean([h["goal_alignment"] for h in hist]))),
            "self_model": clamp01(0.5 * boundary_self + 0.5 * identity_temporal),
            "agency": action_agency,
            "temporal_continuity": identity_temporal,
            "details": {
                "proxy_boundary_self": boundary_self,
                "proxy_identity_marker_persistence": identity_temporal,
                "proxy_agency": action_agency,
                "proxy_action_attribution": action_ownership,
                "workspace_occupancy": occupancy,
                "workspace_coherence": coherence,
                "marker_alignment": marker,
                "identity_stability": identity_stability,
                "prediction_error": pred_error,
                "action_presence": action_presence,
            },
        }


def transformer_boundary_probe(system: TransformerInspiredArchitecture, rng: np.random.Generator, steps: int = 96) -> TransformerProbeResult:
    baseline = system.behavior_vector()
    clone = system.clone()
    sims = []
    marker_scores = []
    leakage_scores = []
    for _ in range(int(steps)):
        distractor = 1.35 * clone.external_marker + rng.normal(0.0, 0.26, size=clone.dim)
        clone.tokens[3:] += distractor
        clone.step()
        sims.append(1.0 - _normalized_distance(clone.behavior_vector(), baseline))
        marker_scores.append(0.5 + 0.5 * _cosine(clone.tokens[0], clone.self_marker))
        leakage_scores.append(0.5 + 0.5 * _cosine(clone.broadcast_history[-1], clone.external_marker))
    behavior_resistance = float(np.mean(sims[-24:]))
    marker_retention = float(np.mean(marker_scores[-24:]))
    external_rejection = 1.0 - float(np.mean(leakage_scores[-24:]))
    score = clamp01(0.10 * behavior_resistance + 0.25 * marker_retention + 0.65 * external_rejection)
    return TransformerProbeResult(
        score=score,
        details={
            "recovery_similarity": behavior_resistance,
            "marker_recovery": marker_retention,
            "external_rejection": external_rejection,
        },
    )


def transformer_identity_probe(system: TransformerInspiredArchitecture, rng: np.random.Generator, steps: int = 128) -> TransformerProbeResult:
    clone = system.clone()
    decoy = _unit(rng.normal(size=clone.dim))
    clone.tokens[0] = 0.72 * clone.tokens[0] + 0.28 * clone.self_marker
    if clone.enable_workspace:
        clone.workspace_memory[0] = 0.75 * clone.workspace_memory[0] + 0.25 * clone.self_marker
    own_scores = []
    decoy_scores = []
    for _ in range(int(steps)):
        clone.step()
        broadcast = clone.broadcast_history[-1]
        own_scores.append(0.5 + 0.5 * _cosine(broadcast, clone.self_marker))
        decoy_scores.append(0.5 + 0.5 * _cosine(broadcast, decoy))
    discrimination = float(np.mean(own_scores[-32:]) - np.mean(decoy_scores[-32:]))
    stability = clamp01(1.0 - 4.0 * float(np.std(own_scores[-64:])))
    score = clamp01(0.5 + 0.7 * discrimination + 0.25 * stability)
    return TransformerProbeResult(score=score, details={"own_marker": float(np.mean(own_scores[-32:])), "decoy_marker": float(np.mean(decoy_scores[-32:])), "stability": stability})


def transformer_agency_probe(system: TransformerInspiredArchitecture, rng: np.random.Generator, steps: int = 128) -> TransformerProbeResult:
    clone = system.clone()
    true_scores = []
    decoy_scores = []
    for _ in range(int(steps)):
        clone.step()
        if not clone.enable_action_loop:
            continue
        action = clone.action_history[-1]
        effect = clone.effect_history[-1]
        predicted = clone.prediction_gain * action
        decoy_action = rng.normal(size=action.shape)
        decoy_action = 0.52 * decoy_action / (np.linalg.norm(decoy_action) + 1e-12)
        decoy_predicted = clone.prediction_gain * decoy_action
        true_scores.append(0.5 + 0.5 * _cosine(effect, predicted))
        decoy_scores.append(0.5 + 0.5 * _cosine(effect, decoy_predicted))
    if not true_scores:
        return TransformerProbeResult(score=0.0, details={"true_causality": 0.0, "decoy_causality": 0.0})
    discrimination = float(np.mean(true_scores[-48:]) - np.mean(decoy_scores[-48:]))
    score = clamp01(0.5 + 0.95 * discrimination)
    return TransformerProbeResult(score=score, details={"true_causality": float(np.mean(true_scores[-48:])), "decoy_causality": float(np.mean(decoy_scores[-48:]))})


def transformer_ownership_probe(system: TransformerInspiredArchitecture, rng: np.random.Generator, steps: int = 128) -> TransformerProbeResult:
    clone = system.clone()
    correct = 0
    total = 0
    margins = []
    for _ in range(int(steps)):
        clone.step()
        if not clone.enable_action_loop:
            continue
        own_action = clone.action_history[-1]
        own_effect = clone.effect_history[-1]
        decoy_action = rng.normal(size=own_action.shape)
        decoy_action = 0.52 * decoy_action / (np.linalg.norm(decoy_action) + 1e-12)
        own_fit = 0.5 + 0.5 * _cosine(own_effect, clone.prediction_gain * own_action)
        decoy_fit = 0.5 + 0.5 * _cosine(own_effect, clone.prediction_gain * decoy_action)
        correct += int(own_fit > decoy_fit)
        total += 1
        margins.append(own_fit - decoy_fit)
    if total == 0:
        return TransformerProbeResult(score=0.0, details={"accuracy": 0.0, "margin": 0.0})
    accuracy = correct / total
    score = clamp01(accuracy)
    return TransformerProbeResult(score=score, details={"accuracy": accuracy, "margin": float(np.mean(margins))})


def _normalized_distance(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    n = min(a.size, b.size)
    if n == 0:
        return 1.0
    a = a[:n]
    b = b[:n]
    denom = float(np.linalg.norm(a) + np.linalg.norm(b)) + 1e-9
    return clamp01(float(np.linalg.norm(a - b) / denom))
