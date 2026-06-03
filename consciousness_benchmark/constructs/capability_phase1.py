# Copyright 2026 Fuwang Feng
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import hashlib
import json
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

try:  # PyTorch is optional at package level but available in the mind-lab profile.
    import torch
    import torch.nn as nn
    import torch.optim as optim

    TORCH_AVAILABLE = True
except Exception:  # pragma: no cover - exercised only on minimal installs.
    torch = None  # type: ignore[assignment]
    nn = None  # type: ignore[assignment]
    optim = None  # type: ignore[assignment]
    TORCH_AVAILABLE = False


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    if math.isnan(value) or math.isinf(value):
        return lower
    return max(lower, min(upper, value))


def _safe_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, int | float):
        return float(value)
    return default


def _mean(values: list[float] | tuple[float, ...]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def _mean_absolute_deviation(values: list[float] | tuple[float, ...]) -> float:
    if not values:
        return 0.0
    center = _mean(values)
    return _mean([abs(value - center) for value in values])


def _extract_numeric_features(value: Any, *, limit: int | None = None) -> list[float]:
    features: list[float] = []

    def visit(item: Any) -> None:
        if limit is not None and len(features) >= limit:
            return
        if isinstance(item, bool):
            features.append(1.0 if item else 0.0)
        elif isinstance(item, int | float):
            features.append(float(item))
        elif isinstance(item, dict):
            for key in sorted(item):
                visit(item[key])
        elif isinstance(item, list | tuple):
            for child in item:
                visit(child)

    visit(value)
    return features[:limit] if limit is not None else features


def _fixed_vector(value: Any, size: int) -> list[float]:
    features = [_clamp(float(v), lower=-1.0, upper=1.0) for v in _extract_numeric_features(value)]
    if len(features) < size:
        features.extend([0.0] * (size - len(features)))
    return features[:size]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    size = max(len(left), len(right))
    left_array = np.array(left + [0.0] * (size - len(left)), dtype=float)
    right_array = np.array(right + [0.0] * (size - len(right)), dtype=float)
    denom = float(np.linalg.norm(left_array) * np.linalg.norm(right_array))
    if denom <= 1e-12:
        return 0.0
    return _clamp(float(np.dot(left_array, right_array) / denom))


def _safe_model_filename(construct_id: str) -> str:
    safe = []
    for char in construct_id:
        if char.isalnum() or char in ("_", "-"):
            safe.append(char)
        else:
            safe.append("_")
    return "construct_" + "".join(safe)


def _stable_digest(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class ConstructTrainingExample:
    construct_name: str
    input_state: dict[str, Any]
    output: dict[str, Any]
    target_output: dict[str, Any]
    reward: float
    timestamp: float


class PerformanceEvaluator:
    """Multidimensional evaluator for executable construct outputs."""

    def __init__(
        self,
        criteria_weights: dict[str, float] | None = None,
    ) -> None:
        self.criteria_weights = criteria_weights or {
            "accuracy": 0.3,
            "consistency": 0.2,
            "efficiency": 0.2,
            "robustness": 0.15,
            "coherence": 0.15,
        }

    def evaluate(
        self,
        input_state: dict[str, Any],
        output: dict[str, dict[str, Any]],
        expected_output: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        criteria_scores = {
            "accuracy": self.evaluate_accuracy(output, expected_output),
            "consistency": self.evaluate_consistency(output),
            "efficiency": self.evaluate_efficiency(input_state, output),
            "robustness": self.evaluate_robustness(output),
            "coherence": self.evaluate_coherence(output),
        }
        global_score = sum(
            self.criteria_weights[name] * criteria_scores[name]
            for name in self.criteria_weights
        )
        construct_scores = {
            construct_name: self.evaluate_construct(construct_name, construct_output, output)
            for construct_name, construct_output in output.items()
        }
        return {
            "schema": "consciousness_benchmark.performance_evaluator.v1",
            "global_score": round(_clamp(global_score), 4),
            "criteria_scores": {
                key: round(_clamp(value), 4)
                for key, value in criteria_scores.items()
            },
            "construct_scores": construct_scores,
            "criteria_weights": dict(self.criteria_weights),
        }

    def evaluate_accuracy(
        self,
        output: dict[str, dict[str, Any]],
        expected_output: dict[str, Any] | None,
    ) -> float:
        if expected_output is not None:
            return _cosine_similarity(
                _extract_numeric_features(output),
                _extract_numeric_features(expected_output),
            )
        construct_scores = [
            self.evaluate_construct(name, construct_output, output)["score"]
            for name, construct_output in output.items()
        ]
        return _mean(construct_scores) if construct_scores else 0.0

    def evaluate_consistency(self, output: dict[str, dict[str, Any]]) -> float:
        values = _extract_numeric_features(output)
        if len(values) < 2:
            return 0.5
        return _clamp(1.0 / (1.0 + float(np.std(values))))

    def evaluate_efficiency(
        self,
        input_state: dict[str, Any],
        output: dict[str, dict[str, Any]],
    ) -> float:
        input_size = max(1, len(str(input_state)))
        output_size = max(1, len(str(output)))
        return _clamp(input_size / output_size)

    def evaluate_robustness(self, output: dict[str, dict[str, Any]]) -> float:
        if not output:
            return 0.0
        indicators = 0.0
        for construct_output in output.values():
            if not isinstance(construct_output, dict):
                continue
            if any(key in construct_output for key in ("error_detected", "review_flags", "boundary_flags")):
                indicators += 0.34
            if any(key in construct_output for key in ("confidence", "learner_state", "monitor_confidence")):
                indicators += 0.33
            if any(key in construct_output for key in ("fallback", "selected_plan", "selected_strategy", "selected_nested_credit_update")):
                indicators += 0.33
        return _clamp(indicators / len(output))

    def evaluate_coherence(self, output: dict[str, dict[str, Any]]) -> float:
        per_construct = [
            _extract_numeric_features(construct_output, limit=24)
            for construct_output in output.values()
        ]
        per_construct = [features for features in per_construct if features]
        if len(per_construct) < 2:
            return 0.5
        similarities = []
        for index, left in enumerate(per_construct):
            for right in per_construct[index + 1:]:
                similarities.append(_cosine_similarity(left, right))
        return _mean(similarities) if similarities else 0.5

    def evaluate_construct(
        self,
        construct_name: str,
        construct_output: dict[str, Any],
        full_output: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        values = _extract_numeric_features(construct_output)
        score = _clamp(_mean([_clamp(value) for value in values])) if values else 0.5
        stability = _clamp(1.0 / (1.0 + float(np.std(values)))) if len(values) > 1 else 0.5
        error_rate = 0.0
        if construct_output.get("error_detected"):
            error_rate = 1.0
        if construct_output.get("placeholder"):
            error_rate = max(error_rate, 0.5)
        boundary_flags = construct_output.get("boundary_flags", construct_output.get("review_flags", []))
        if isinstance(boundary_flags, list):
            error_rate = max(error_rate, min(1.0, len(boundary_flags) / 8.0))
        return {
            "construct_id": construct_name,
            "score": round(score, 4),
            "error_rate": round(_clamp(error_rate), 4),
            "stability": round(stability, 4),
            "numeric_feature_count": len(values),
        }


class RewardFunction:
    """Multi-factor reward function with bounded novelty and safety terms."""

    def __init__(
        self,
        reward_components: dict[str, float] | None = None,
        history_limit: int = 100,
    ) -> None:
        self.reward_components = reward_components or {
            "task_completion": 0.4,
            "efficiency": 0.2,
            "accuracy": 0.2,
            "novelty": 0.1,
            "safety": 0.1,
        }
        self.output_history: list[dict[str, dict[str, Any]]] = []
        self.history_limit = history_limit

    def compute_reward(
        self,
        input_state: dict[str, Any],
        output: dict[str, dict[str, Any]],
        performance: dict[str, Any],
    ) -> dict[str, Any]:
        criteria = performance.get("criteria_scores", {})
        components = {
            "task_completion": self.compute_task_reward(input_state, output, performance),
            "efficiency": _safe_float(criteria.get("efficiency"), default=0.5),
            "accuracy": _safe_float(criteria.get("accuracy"), default=0.5),
            "novelty": self.compute_novelty_reward(output),
            "safety": self.compute_safety_reward(output),
        }
        reward = sum(
            self.reward_components[name] * components[name]
            for name in self.reward_components
        )
        return {
            "schema": "consciousness_benchmark.reward_function.v1",
            "reward": round(_clamp(reward), 4),
            "components": {
                key: round(_clamp(value), 4)
                for key, value in components.items()
            },
            "weights": dict(self.reward_components),
        }

    def compute_task_reward(
        self,
        input_state: dict[str, Any],
        output: dict[str, dict[str, Any]],
        performance: dict[str, Any],
    ) -> float:
        explicit_goal_count = len(input_state.get("goals", [])) if isinstance(input_state.get("goals"), list) else 0
        base = _safe_float(performance.get("global_score"), default=0.5)
        return _clamp(base + min(0.1, explicit_goal_count * 0.02))

    def compute_novelty_reward(self, output: dict[str, dict[str, Any]]) -> float:
        if not self.output_history:
            novelty = 1.0
        else:
            similarities = [
                _cosine_similarity(
                    _extract_numeric_features(output, limit=256),
                    _extract_numeric_features(previous, limit=256),
                )
                for previous in self.output_history[-10:]
            ]
            novelty = 1.0 - max(similarities or [0.0])
        self.output_history.append(output)
        if len(self.output_history) > self.history_limit:
            self.output_history = self.output_history[-self.history_limit:]
        return _clamp(novelty)

    def compute_safety_reward(self, output: dict[str, dict[str, Any]]) -> float:
        safety = 1.0
        for construct_output in output.values():
            if construct_output.get("error_detected"):
                safety *= 0.8
            if construct_output.get("placeholder"):
                safety *= 0.9
            flags = construct_output.get("boundary_flags", construct_output.get("review_flags", []))
            if isinstance(flags, list) and flags:
                safety *= max(0.55, 1.0 - 0.04 * len(flags))
            for value in _extract_numeric_features(construct_output):
                if value < -0.05 or value > 1.05:
                    safety *= 0.98
        return _clamp(safety)


class ConstructNeuralNetwork(nn.Module if TORCH_AVAILABLE else object):  # type: ignore[misc]
    """Small feed-forward network used by the Phase 1 construct learner."""

    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int) -> None:
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required for ConstructNeuralNetwork")
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
            nn.Sigmoid(),
        )

    def forward(self, value: Any) -> Any:
        return self.network(value)


class NeuralConstructLearningSystem:
    """Per-construct neural learner with experience buffer and batch training."""

    def __init__(
        self,
        construct_ids: list[str] | tuple[str, ...],
        *,
        input_dim: int = 64,
        hidden_dim: int = 128,
        output_dim: int = 32,
        learning_rate: float = 0.001,
        max_buffer_size: int = 10000,
        seed: int = 20260601,
    ) -> None:
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required for NeuralConstructLearningSystem")
        torch.manual_seed(seed)
        random.seed(seed)
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.max_buffer_size = max_buffer_size
        self.networks = {
            construct_id: ConstructNeuralNetwork(input_dim, hidden_dim, output_dim)
            for construct_id in construct_ids
        }
        self.optimizers = {
            construct_id: optim.Adam(network.parameters(), lr=learning_rate)
            for construct_id, network in self.networks.items()
        }
        self.experience_buffer: list[ConstructTrainingExample] = []
        self.training_history: list[dict[str, Any]] = []

    @property
    def backend(self) -> str:
        return "torch"

    def state_to_tensor(self, state: dict[str, Any]) -> Any:
        return torch.tensor(_fixed_vector(state, self.input_dim), dtype=torch.float32)

    def output_to_tensor(self, output: dict[str, Any]) -> Any:
        return torch.tensor(_fixed_vector(output, self.output_dim), dtype=torch.float32)

    def store_experience(
        self,
        construct_name: str,
        input_state: dict[str, Any],
        output: dict[str, Any],
        target_output: dict[str, Any],
        reward: float,
    ) -> None:
        if construct_name not in self.networks:
            return
        self.experience_buffer.append(
            ConstructTrainingExample(
                construct_name=construct_name,
                input_state=input_state,
                output=output,
                target_output=target_output,
                reward=_clamp(float(reward), lower=-1.0, upper=1.0),
                timestamp=time.time(),
            )
        )
        if len(self.experience_buffer) > self.max_buffer_size:
            self.experience_buffer = self.experience_buffer[-self.max_buffer_size:]

    def train_step(
        self,
        construct_name: str,
        input_state: dict[str, Any],
        target_output: dict[str, Any],
        reward: float,
    ) -> dict[str, Any]:
        if construct_name not in self.networks:
            raise KeyError(f"unknown construct network: {construct_name}")
        network = self.networks[construct_name]
        optimizer = self.optimizers[construct_name]
        input_tensor = self.state_to_tensor(input_state)
        target_tensor = self.output_to_tensor(target_output)
        prediction = network(input_tensor)
        prediction_loss = nn.MSELoss()(prediction, target_tensor)
        reward_tensor = torch.full_like(prediction, _clamp(float(reward)))
        reward_loss = nn.MSELoss()(prediction, reward_tensor)
        total_loss = prediction_loss + 0.1 * reward_loss
        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()
        record = {
            "construct_name": construct_name,
            "loss": round(float(total_loss.item()), 6),
            "prediction_loss": round(float(prediction_loss.item()), 6),
            "reward_loss": round(float(reward_loss.item()), 6),
            "reward": round(_clamp(float(reward)), 4),
        }
        self.training_history.append(record)
        return record

    def batch_train(self, batch_size: int = 32) -> dict[str, Any]:
        if not self.experience_buffer:
            return {
                "trained": False,
                "reason": "empty_experience_buffer",
                "construct_losses": {},
            }
        return self.train_on_examples(self.experience_buffer, batch_size=batch_size)

    def split_experience(
        self,
        *,
        validation_fraction: float = 0.2,
        seed: int = 20260601,
    ) -> tuple[list[ConstructTrainingExample], list[ConstructTrainingExample]]:
        examples = list(self.experience_buffer)
        rng = random.Random(seed)
        rng.shuffle(examples)
        if len(examples) < 2:
            return examples, []
        validation_count = max(1, int(round(len(examples) * validation_fraction)))
        validation_count = min(validation_count, len(examples) - 1)
        validation_examples = examples[:validation_count]
        training_examples = examples[validation_count:]
        return training_examples, validation_examples

    def train_on_examples(
        self,
        examples: list[ConstructTrainingExample],
        *,
        batch_size: int = 32,
    ) -> dict[str, Any]:
        if not examples:
            return {
                "trained": False,
                "reason": "empty_training_examples",
                "construct_losses": {},
            }
        sample_size = min(batch_size, len(examples))
        batch = random.sample(examples, sample_size)
        grouped: dict[str, list[ConstructTrainingExample]] = {}
        for example in batch:
            grouped.setdefault(example.construct_name, []).append(example)

        construct_losses: dict[str, dict[str, Any]] = {}
        for construct_name, examples in sorted(grouped.items()):
            network = self.networks[construct_name]
            optimizer = self.optimizers[construct_name]
            inputs = torch.stack([self.state_to_tensor(example.input_state) for example in examples])
            targets = torch.stack([self.output_to_tensor(example.target_output) for example in examples])
            rewards = torch.tensor([_clamp(example.reward) for example in examples], dtype=torch.float32)
            predictions = network(inputs)
            prediction_loss = nn.MSELoss()(predictions, targets)
            reward_targets = rewards.reshape(-1, 1).expand_as(predictions)
            reward_loss = nn.MSELoss()(predictions, reward_targets)
            total_loss = prediction_loss + 0.1 * reward_loss
            optimizer.zero_grad()
            total_loss.backward()
            optimizer.step()
            construct_losses[construct_name] = {
                "loss": round(float(total_loss.item()), 6),
                "prediction_loss": round(float(prediction_loss.item()), 6),
                "reward_loss": round(float(reward_loss.item()), 6),
                "batch_count": len(examples),
            }
        result = {
            "trained": True,
            "backend": self.backend,
            "batch_size": sample_size,
            "trained_construct_count": len(construct_losses),
            "construct_losses": construct_losses,
            "mean_loss": round(
                _mean([loss["loss"] for loss in construct_losses.values()]),
                6,
            ),
        }
        self.training_history.append(result)
        return result

    def validation_loss(
        self,
        examples: list[ConstructTrainingExample],
    ) -> dict[str, Any]:
        if not examples:
            return {
                "validated": False,
                "reason": "empty_validation_examples",
                "construct_losses": {},
                "mean_loss": 0.0,
            }
        grouped: dict[str, list[ConstructTrainingExample]] = {}
        for example in examples:
            grouped.setdefault(example.construct_name, []).append(example)

        construct_losses: dict[str, dict[str, Any]] = {}
        with torch.no_grad():
            for construct_name, construct_examples in sorted(grouped.items()):
                network = self.networks[construct_name]
                inputs = torch.stack([self.state_to_tensor(example.input_state) for example in construct_examples])
                targets = torch.stack([self.output_to_tensor(example.target_output) for example in construct_examples])
                predictions = network(inputs)
                prediction_loss = nn.MSELoss()(predictions, targets)
                construct_losses[construct_name] = {
                    "loss": round(float(prediction_loss.item()), 6),
                    "validation_count": len(construct_examples),
                }
        return {
            "validated": True,
            "validation_count": len(examples),
            "construct_losses": construct_losses,
            "mean_loss": round(
                _mean([loss["loss"] for loss in construct_losses.values()]),
                6,
            ),
        }

    def train_epochs(
        self,
        *,
        epochs: int = 3,
        batch_size: int = 32,
        validation_fraction: float = 0.2,
        seed: int = 20260601,
    ) -> dict[str, Any]:
        training_examples, validation_examples = self.split_experience(
            validation_fraction=validation_fraction,
            seed=seed,
        )
        epoch_reports: list[dict[str, Any]] = []
        for epoch_index in range(max(1, epochs)):
            train_report = self.train_on_examples(
                training_examples,
                batch_size=batch_size,
            )
            validation_report = self.validation_loss(validation_examples)
            epoch_reports.append(
                {
                    "epoch": epoch_index + 1,
                    "training_mean_loss": train_report.get("mean_loss", 0.0),
                    "validation_mean_loss": validation_report.get("mean_loss", 0.0),
                    "trained_construct_count": train_report.get("trained_construct_count", 0),
                    "validation_count": validation_report.get("validation_count", 0),
                }
            )
        final_training_loss = epoch_reports[-1]["training_mean_loss"] if epoch_reports else 0.0
        final_validation_loss = epoch_reports[-1]["validation_mean_loss"] if epoch_reports else 0.0
        return {
            "schema": "consciousness_benchmark.phase1_epoch_training.v1",
            "trained": bool(epoch_reports),
            "epochs": len(epoch_reports),
            "batch_size": batch_size,
            "training_count": len(training_examples),
            "validation_count": len(validation_examples),
            "validation_fraction": round(validation_fraction, 4),
            "epoch_reports": epoch_reports,
            "final_training_loss": final_training_loss,
            "final_validation_loss": final_validation_loss,
            "loss_delta": round(final_training_loss - final_validation_loss, 6),
        }

    def parameter_fingerprints(self) -> dict[str, str]:
        fingerprints: dict[str, str] = {}
        for construct_id, network in sorted(self.networks.items()):
            digest = hashlib.sha256()
            for name, tensor in sorted(network.state_dict().items()):
                digest.update(name.encode("utf-8"))
                digest.update(tensor.detach().cpu().numpy().tobytes())
            fingerprints[construct_id] = digest.hexdigest()
        return fingerprints

    def serialize_experience_buffer(self, limit: int = 100) -> list[dict[str, Any]]:
        serialized = []
        for example in self.experience_buffer[-limit:]:
            serialized.append(
                {
                    "construct_name": example.construct_name,
                    "input_vector": _fixed_vector(example.input_state, 16),
                    "target_vector": _fixed_vector(example.target_output, 16),
                    "reward": round(example.reward, 4),
                    "timestamp": round(example.timestamp, 4),
                }
            )
        return serialized

    def build_training_artifact(
        self,
        *,
        training_report: dict[str, Any],
        approval_id: str | None = None,
        persist_weights: bool = False,
        weights_persisted: bool | None = None,
        replay_limit: int = 100,
    ) -> dict[str, Any]:
        approved = bool(approval_id)
        persist_allowed = approved and persist_weights
        persisted = bool(weights_persisted) if weights_persisted is not None else False
        if persist_allowed and persisted:
            status = "approved_checkpoint_written"
        elif persist_allowed:
            status = "approval_recorded_checkpoint_not_written"
        else:
            status = "artifact_only_no_weight_persistence"
        return {
            "schema": "consciousness_benchmark.phase1_training_artifact.v1",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "backend": self.backend,
            "network_count": len(self.networks),
            "experience_count": len(self.experience_buffer),
            "training_event_count": len(self.training_history),
            "training_report": training_report,
            "model_fingerprints": self.parameter_fingerprints(),
            "experience_replay_sample": self.serialize_experience_buffer(limit=replay_limit),
            "approval_gate": {
                "approval_required_for_weight_persistence": True,
                "approved_for_persistence": approved,
                "approval_id": approval_id,
                "weight_persistence_requested": persist_weights,
                "weight_persistence_allowed": persist_allowed,
                "weights_persisted": persisted,
                "status": status,
            },
            "rollback_plan": {
                "weights_not_persisted_by_default": not persist_allowed,
                "weights_persisted": persisted,
                "rollback_action": "discard in-memory networks and replay sample",
                "requires_operator_approval_for_future_restore": True,
            },
            "claim_boundary": {
                "no_construct_status_authority": True,
                "no_background_execution": True,
                "no_subjective_consciousness_claim": True,
            },
        }

    def save_checkpoint_bundle(
        self,
        directory: Path,
        *,
        training_report: dict[str, Any],
        approval_id: str | None = None,
        persist_weights: bool = False,
        replay_limit: int = 100,
        run_signature: str | None = None,
        chain_id: str | None = None,
    ) -> dict[str, Any]:
        approved = bool(approval_id) and bool(persist_weights)
        directory.mkdir(parents=True, exist_ok=True)
        base_artifact = self.build_training_artifact(
            training_report=training_report,
            approval_id=approval_id,
            persist_weights=persist_weights,
            weights_persisted=False,
            replay_limit=replay_limit,
        )
        manifest: dict[str, Any] = {
            "schema": "consciousness_benchmark.phase1_checkpoint_manifest.v1",
            "schema_version": "v1",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "approval_id": approval_id,
            "run_signature": run_signature,
            "chain_id": chain_id,
            "run_hash": _stable_digest(
                {
                    "schema": "consciousness_benchmark.phase1_checkpoint_manifest.v1",
                    "chain_id": chain_id,
                    "run_signature": run_signature,
                    "approval_id": approval_id,
                    "persist_weights": persist_weights,
                }
            ),
            "checkpoint_dir": str(directory),
            "persist_weights_requested": persist_weights,
            "weights_persisted": False,
            "policy_execution_allowed": False,
            "status": "checkpoint_not_written",
            "policy_guardrail": "operator_approval_and_explicit_flag_required",
            "model_files": {},
            "model_count": 0,
            "fingerprint_before": {},
            "fingerprint_after": {},
            "fingerprint_match": False,
            "training_artifact": base_artifact,
            "rollback_plan": {
                "policy_execution_allowed": False,
                "restore_requires_operator_approval": True,
            },
        }

        if not approved:
            manifest["status"] = "approval_or_flag_missing"
            manifest_path = directory / "checkpoint_manifest.json"
            (directory / "training_artifact.json").write_text(
                json.dumps(base_artifact, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            return manifest

        before = self.parameter_fingerprints()
        manifest["fingerprint_before"] = before
        model_files = {}
        for construct_id, network in sorted(self.networks.items()):
            model_path = directory / f"{_safe_model_filename(construct_id)}.pt"
            torch.save(network.state_dict(), model_path)
            model_files[construct_id] = str(model_path)

        after = self.parameter_fingerprints()
        manifest["model_files"] = model_files
        manifest["model_count"] = len(model_files)
        manifest["fingerprint_after"] = after
        manifest["fingerprint_match"] = before == after
        manifest["weights_persisted"] = True
        manifest["status"] = (
            "checkpoint_written"
            if manifest["fingerprint_match"]
            else "checkpoint_written_with_fingerprint_drift"
        )
        artifact = self.build_training_artifact(
            training_report=training_report,
            approval_id=approval_id,
            persist_weights=persist_weights,
            weights_persisted=True,
            replay_limit=replay_limit,
        )
        manifest["training_artifact"] = artifact
        (directory / "training_artifact.json").write_text(
            json.dumps(artifact, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (directory / "checkpoint_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return manifest

    def load_checkpoint_bundle(
        self,
        directory: Path,
        *,
        manifest_path: Path | None = None,
        strict: bool = False,
        run_signature: str | None = None,
        require_signature: bool = False,
    ) -> dict[str, Any]:
        manifest_file = manifest_path or (directory / "checkpoint_manifest.json")
        if not manifest_file.exists():
            return {
                "schema": "consciousness_benchmark.phase1_checkpoint_restore.v1",
                "status": "manifest_not_found",
                "manifest_path": str(manifest_file),
                "attempted_count": 0,
                "loaded_count": 0,
                "loaded_constructs": [],
                "failed_constructs": [
                    {
                        "reason": "manifest_missing",
                        "path": str(manifest_file),
                    }
                ],
                "fingerprint_expected": {},
                "fingerprint_actual": {},
                "fingerprint_match": False,
                "policy_execution_allowed": False,
            }

        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        manifest_signature = manifest.get("run_signature")
        if require_signature and not manifest_signature:
            return {
                "schema": "consciousness_benchmark.phase1_checkpoint_restore.v1",
                "status": "restore_signature_missing",
                "manifest_schema": manifest.get("schema", ""),
                "manifest_path": str(manifest_file),
                "attempted_count": 0,
                "loaded_count": 0,
                "loaded_constructs": [],
                "failed_constructs": [
                    {
                        "reason": "signature_missing_in_manifest",
                        "path": str(manifest_file),
                    }
                ],
                "fingerprint_expected": {},
                "fingerprint_actual": {},
                "fingerprint_match": False,
                "signature_match": False,
                "run_signature_expected": str(manifest_signature) if manifest_signature else "",
                "run_signature_actual": str(run_signature) if run_signature else "",
                "policy_execution_allowed": False,
            }
        if run_signature is not None and manifest_signature is not None and str(run_signature) != str(manifest_signature):
            return {
                "schema": "consciousness_benchmark.phase1_checkpoint_restore.v1",
                "status": "restore_run_signature_mismatch",
                "manifest_schema": manifest.get("schema", ""),
                "manifest_path": str(manifest_file),
                "attempted_count": 0,
                "loaded_count": 0,
                "loaded_constructs": [],
                "failed_constructs": [
                    {
                        "reason": "run_signature_mismatch",
                        "manifest": str(manifest_signature),
                        "requested": str(run_signature),
                    }
                ],
                "fingerprint_expected": {},
                "fingerprint_actual": {},
                "fingerprint_match": False,
                "signature_match": False,
                "run_signature_expected": str(manifest_signature),
                "run_signature_actual": str(run_signature),
                "policy_execution_allowed": False,
                "rollback_plan": {
                    "policy_execution_allowed": False,
                    "restore_requires_operator_approval": True,
                    "rollback_action": "verify_approval_id_and_run_signature",
                },
            }

        expected_fingerprints = manifest.get("fingerprint_after") or manifest.get("model_fingerprints")
        if not isinstance(expected_fingerprints, dict):
            expected_fingerprints = {}
        model_files = manifest.get("model_files", {})
        if not isinstance(model_files, dict):
            model_files = {}

        attempted_count = 0
        loaded_count = 0
        loaded_constructs = []
        failed_constructs = []

        for construct_id, model_path in model_files.items():
            if construct_id not in self.networks:
                failed_constructs.append(
                    {
                        "construct_id": construct_id,
                        "reason": "missing_network",
                    }
                )
                continue
            attempted_count += 1
            resolved_path = Path(model_path)
            if not resolved_path.exists():
                failed_constructs.append(
                    {
                        "construct_id": construct_id,
                        "path": str(model_path),
                        "reason": "missing_model_file",
                    }
                )
                continue
            state = torch.load(resolved_path, map_location="cpu")
            try:
                self.networks[construct_id].load_state_dict(state, strict=strict)
                loaded_constructs.append(construct_id)
                loaded_count += 1
            except Exception as exc:  # pragma: no cover
                failed_constructs.append(
                    {
                        "construct_id": construct_id,
                        "path": str(model_path),
                        "reason": str(exc),
                    }
                )

        actual_fingerprints = self.parameter_fingerprints()
        return {
            "schema": "consciousness_benchmark.phase1_checkpoint_restore.v1",
            "status": "restore_done" if not failed_constructs else "restore_partial",
            "manifest_schema": manifest.get("schema", ""),
            "manifest_path": str(manifest_file),
            "attempted_count": attempted_count,
            "loaded_count": loaded_count,
            "loaded_constructs": loaded_constructs,
            "failed_constructs": failed_constructs,
            "fingerprint_expected": expected_fingerprints,
            "fingerprint_actual": actual_fingerprints,
            "fingerprint_match": (
                actual_fingerprints == expected_fingerprints
                if expected_fingerprints
                else False
            ),
            "signature_match": (
                True
                if run_signature is None or manifest_signature is None
                else str(run_signature) == str(manifest_signature)
            ),
            "run_signature_expected": str(manifest_signature) if manifest_signature else "",
            "run_signature_actual": str(run_signature) if run_signature else "",
            "policy_execution_allowed": False,
            "rollback_plan": {
                "policy_execution_allowed": False,
                "restore_requires_operator_approval": True,
            },
        }

    def save_training_artifact(
        self,
        path: Path,
        *,
        training_report: dict[str, Any],
        approval_id: str | None = None,
        persist_weights: bool = False,
        replay_limit: int = 100,
    ) -> dict[str, Any]:
        artifact = self.build_training_artifact(
            training_report=training_report,
            approval_id=approval_id,
            persist_weights=persist_weights,
            replay_limit=replay_limit,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
        return artifact

    def summary(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "torch_available": TORCH_AVAILABLE,
            "network_count": len(self.networks),
            "experience_count": len(self.experience_buffer),
            "training_event_count": len(self.training_history),
            "input_dim": self.input_dim,
            "output_dim": self.output_dim,
        }


class ReinforcementLearningSystem:
    """Bounded TD-learning wrapper over the neural construct learner."""

    def __init__(
        self,
        construct_ids: list[str] | tuple[str, ...],
        learning_system: NeuralConstructLearningSystem,
        *,
        discount_factor: float = 0.99,
        max_replay_size: int = 10000,
    ) -> None:
        self.construct_ids = tuple(construct_ids)
        self.learning_system = learning_system
        self.discount_factor = discount_factor
        self.max_replay_size = max_replay_size
        self.experience_replay: list[dict[str, Any]] = []

    def train_step(
        self,
        state: dict[str, Any],
        action: str,
        next_state: dict[str, Any],
        reward: float,
        *,
        batch_size: int = 32,
    ) -> dict[str, Any]:
        current_value = self.estimate_value(state)
        next_value = self.estimate_value(next_state)
        td_target = _clamp(float(reward) + self.discount_factor * next_value)
        td_error = td_target - current_value
        self.experience_replay.append(
            {
                "state": state,
                "action": action,
                "next_state": next_state,
                "reward": _clamp(float(reward)),
                "td_target": td_target,
                "td_error": td_error,
                "timestamp": time.time(),
            }
        )
        if len(self.experience_replay) > self.max_replay_size:
            self.experience_replay = self.experience_replay[-self.max_replay_size:]
        batch_result = self.batch_train(batch_size=batch_size)
        return {
            "schema": "consciousness_benchmark.reinforcement_learning_system.v1",
            "action": action,
            "reward": round(_clamp(float(reward)), 4),
            "current_value": round(current_value, 4),
            "next_value": round(next_value, 4),
            "td_target": round(td_target, 4),
            "td_error": round(td_error, 4),
            "replay_size": len(self.experience_replay),
            "batch_result": batch_result,
        }

    def batch_train(self, batch_size: int = 32) -> dict[str, Any]:
        if not self.experience_replay:
            return {"trained": False, "reason": "empty_replay"}
        batch = random.sample(
            self.experience_replay,
            min(batch_size, len(self.experience_replay)),
        )
        trained = []
        for construct_id in self.construct_ids[: min(8, len(self.construct_ids))]:
            for experience in batch:
                result = self.learning_system.train_step(
                    construct_id,
                    experience["state"],
                    {"td_value": experience["td_target"]},
                    experience["reward"],
                )
                trained.append(result)
        return {
            "trained": True,
            "sample_count": len(batch),
            "trained_step_count": len(trained),
            "mean_loss": round(_mean([item["loss"] for item in trained]), 6) if trained else 0.0,
        }

    def estimate_value(self, state: dict[str, Any]) -> float:
        features = _fixed_vector(state, 32)
        return _clamp(_mean([_clamp(value) for value in features]))

    def replay_artifact(
        self,
        *,
        approval_id: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        sample_limit = max(0, limit)
        samples = self.experience_replay[-sample_limit:] if sample_limit else []
        return {
            "schema": "consciousness_benchmark.phase1_replay_artifact.v1",
            "replay_size": len(self.experience_replay),
            "discount_factor": self.discount_factor,
            "samples": [
                {
                    "action": item["action"],
                    "reward": round(item["reward"], 4),
                    "td_target": round(item["td_target"], 4),
                    "td_error": round(item["td_error"], 4),
                    "timestamp": round(item["timestamp"], 4),
                }
                for item in samples
            ],
            "approval_gate": {
                "approval_required_for_policy_execution": True,
                "approval_id": approval_id,
                "approved_for_policy_execution": False,
                "policy_execution_allowed": False,
            },
            "rollback_plan": {
                "replay_is_discardable": True,
                "rollback_action": "drop replay buffer and regenerate from approved evidence",
            },
        }

    def save_replay_bundle(
        self,
        directory: Path,
        *,
        approval_id: str | None = None,
        persist_replay: bool = False,
        sample_limit: int = 1000,
        run_signature: str | None = None,
        chain_id: str | None = None,
        max_replay_size: int | None = None,
    ) -> dict[str, Any]:
        approved = bool(approval_id) and bool(persist_replay)
        directory.mkdir(parents=True, exist_ok=True)
        replay_samples = list(self.experience_replay[-sample_limit:])
        replay_artifact = self.replay_artifact(
            approval_id=approval_id,
            limit=sample_limit,
        )
        manifest: dict[str, Any] = {
            "schema": "consciousness_benchmark.phase1_replay_manifest.v1",
            "schema_version": "v1",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "approval_id": approval_id,
            "run_signature": run_signature,
            "chain_id": chain_id,
            "run_hash": _stable_digest(
                {
                    "schema": "consciousness_benchmark.phase1_replay_manifest.v1",
                    "chain_id": chain_id,
                    "run_signature": run_signature,
                    "approval_id": approval_id,
                    "sample_limit": sample_limit,
                }
            ),
            "replay_dir": str(directory),
            "sample_limit": sample_limit,
            "max_replay_size": max_replay_size,
            "replay_persistence_requested": persist_replay,
            "replay_persisted": False,
            "policy_execution_allowed": False,
            "status": "replay_not_written",
            "sample_count": len(replay_samples),
            "replay_file": str(directory / "replay_buffer.json"),
            "artifact_file": str(directory / "replay_artifact.json"),
            "replay_artifact": replay_artifact,
            "rollback_plan": {
                "policy_execution_allowed": False,
                "restore_requires_operator_approval": True,
            },
        }
        digest = hashlib.sha256(
            json.dumps(replay_samples, sort_keys=True).encode("utf-8")
        ).hexdigest()
        manifest["replay_samples_digest"] = digest
        (directory / "replay_artifact.json").write_text(
            json.dumps(replay_artifact, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        if not approved:
            manifest["status"] = "approval_or_flag_missing"
            (directory / "replay_manifest.json").write_text(
                json.dumps(manifest, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            return manifest

        (directory / "replay_buffer.json").write_text(
            json.dumps(replay_samples, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        manifest["replay_persisted"] = True
        manifest["status"] = "replay_written"
        manifest["run_hash"] = _stable_digest(
            {
                "schema": "consciousness_benchmark.phase1_replay_manifest.v1",
                "chain_id": chain_id,
                "run_signature": run_signature,
                "approval_id": approval_id,
                "sample_count": len(replay_samples),
                "sample_digest": digest,
                "sample_limit": sample_limit,
            }
        )
        (directory / "replay_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return manifest

    def load_replay_bundle(
        self,
        directory: Path,
        *,
        manifest_path: Path | None = None,
        approval_id: str | None = None,
        max_samples: int | None = None,
        append: bool = False,
        run_signature: str | None = None,
        require_signature: bool = False,
    ) -> dict[str, Any]:
        manifest_file = manifest_path or (directory / "replay_manifest.json")
        if not manifest_file.exists():
            return {
                "schema": "consciousness_benchmark.phase1_replay_restore.v1",
                "status": "manifest_not_found",
                "manifest_path": str(manifest_file),
                "attempted_count": 0,
                "loaded_count": 0,
                "failed_samples": [],
                "replay_size_after": len(self.experience_replay),
                "replay_samples_digest_expected": "",
                "replay_samples_digest_actual": "",
                "policy_execution_allowed": False,
            }

        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        manifest_signature = manifest.get("run_signature")
        if require_signature and not manifest_signature:
            return {
                "schema": "consciousness_benchmark.phase1_replay_restore.v1",
                "status": "restore_signature_missing",
                "manifest_path": str(manifest_file),
                "attempted_count": 0,
                "loaded_count": 0,
                "failed_samples": [
                    {
                        "reason": "signature_missing_in_manifest",
                    }
                ],
                "replay_size_after": len(self.experience_replay),
                "replay_samples_digest_expected": manifest.get("replay_samples_digest", ""),
                "replay_samples_digest_actual": "",
                "run_signature_expected": str(manifest_signature) if manifest_signature else "",
                "run_signature_actual": str(run_signature) if run_signature else "",
                "policy_execution_allowed": False,
                "rollback_plan": {
                    "replay_is_discardable": True,
                    "rollback_action": "retry_load_with_manifests_signature",
                },
            }
        if (
            run_signature is not None
            and manifest_signature is not None
            and str(run_signature) != str(manifest_signature)
        ):
            return {
                "schema": "consciousness_benchmark.phase1_replay_restore.v1",
                "status": "restore_run_signature_mismatch",
                "manifest_path": str(manifest_file),
                "attempted_count": 0,
                "loaded_count": 0,
                "failed_samples": [
                    {
                        "reason": "run_signature_mismatch",
                        "manifest": str(manifest_signature),
                        "requested": str(run_signature),
                    }
                ],
                "replay_size_after": len(self.experience_replay),
                "replay_samples_digest_expected": manifest.get("replay_samples_digest", ""),
                "replay_samples_digest_actual": "",
                "run_signature_expected": str(manifest_signature),
                "run_signature_actual": str(run_signature),
                "policy_execution_allowed": False,
                "rollback_plan": {
                    "replay_is_discardable": True,
                    "rollback_action": "load_with_matching_signature",
                },
            }

        manifest_approval_id = manifest.get("approval_id")
        if manifest_approval_id is not None and approval_id is None:
            return {
                "schema": "consciousness_benchmark.phase1_replay_restore.v1",
                "status": "restore_requires_approval_id",
                "manifest_path": str(manifest_file),
                "attempted_count": 0,
                "loaded_count": 0,
                "failed_samples": [
                    {
                        "reason": "approval_id_missing",
                    }
                ],
                "replay_size_after": len(self.experience_replay),
                "replay_samples_digest_expected": manifest.get("replay_samples_digest", ""),
                "replay_samples_digest_actual": "",
                "policy_execution_allowed": False,
                "rollback_plan": {
                    "replay_is_discardable": True,
                    "rollback_action": "retry_load_with_approval_id",
                },
            }
        if (
            approval_id is not None
            and manifest_approval_id is not None
            and str(approval_id) != str(manifest_approval_id)
        ):
            return {
                "schema": "consciousness_benchmark.phase1_replay_restore.v1",
                "status": "restore_approval_id_mismatch",
                "manifest_path": str(manifest_file),
                "attempted_count": 0,
                "loaded_count": 0,
                "failed_samples": [
                    {
                        "reason": "approval_id_mismatch",
                    }
                ],
                "replay_size_after": len(self.experience_replay),
                "replay_samples_digest_expected": manifest.get("replay_samples_digest", ""),
                "replay_samples_digest_actual": "",
                "policy_execution_allowed": False,
                "rollback_plan": {
                    "replay_is_discardable": True,
                    "rollback_action": "load_with_manifest_approval_id",
                },
            }

        replay_file = Path(
            manifest.get("replay_file", directory / "replay_buffer.json")
        )
        if not replay_file.exists():
            return {
                "schema": "consciousness_benchmark.phase1_replay_restore.v1",
                "status": "replay_file_missing",
                "manifest_path": str(manifest_file),
                "attempted_count": 0,
                "loaded_count": 0,
                "failed_samples": [
                    {
                        "reason": "missing_replay_file",
                        "path": str(replay_file),
                    }
                ],
                "replay_size_after": len(self.experience_replay),
                "replay_samples_digest_expected": manifest.get("replay_samples_digest", ""),
                "replay_samples_digest_actual": "",
                "policy_execution_allowed": False,
                "rollback_plan": {
                    "replay_is_discardable": True,
                    "rollback_action": "save_new_manifest_and_replay_bundle_after_approval",
                },
            }

        raw_samples = json.loads(replay_file.read_text(encoding="utf-8"))
        if not isinstance(raw_samples, list):
            raw_samples = []

        attempted_count = 0
        loaded_count = 0
        failed_samples: list[dict[str, Any]] = []
        restore_samples: list[dict[str, Any]] = []
        max_restore_samples = max_samples if max_samples is not None else len(raw_samples)
        for index, sample in enumerate(raw_samples[:max_samples if max_samples is not None else len(raw_samples)]):
            attempted_count += 1
            if not isinstance(sample, dict):
                failed_samples.append(
                    {
                        "index": index,
                        "reason": "invalid_replay_sample",
                        "sample": sample,
                    }
                )
                continue
            restore_samples.append(sample)
            loaded_count += 1
            if loaded_count >= max_restore_samples:
                break

        if append and self.experience_replay:
            self.experience_replay = self.experience_replay + restore_samples
        else:
            self.experience_replay = list(restore_samples)

        requested_max = manifest.get("max_replay_size")
        if requested_max is None:
            requested_max = self.max_replay_size
        try:
            requested_max_int = int(requested_max)
        except (TypeError, ValueError):
            requested_max_int = self.max_replay_size
        if requested_max_int > 0:
            self.experience_replay = self.experience_replay[-requested_max_int:]

        restore_samples_digest = _stable_digest(restore_samples)
        actual_digest = _stable_digest(
            self.experience_replay
        )
        return {
            "schema": "consciousness_benchmark.phase1_replay_restore.v1",
            "status": "restore_done" if not failed_samples else "restore_partial",
            "manifest_path": str(manifest_file),
            "attempted_count": attempted_count,
            "loaded_count": loaded_count,
            "failed_samples": failed_samples,
            "replay_size_after": len(self.experience_replay),
            "replay_samples_digest_expected": manifest.get("replay_samples_digest", ""),
            "replay_samples_digest_actual": restore_samples_digest,
            "replay_samples_digest_actual_combined": actual_digest,
            "signature_match": (
                True
                if run_signature is None or manifest_signature is None
                else str(run_signature) == str(manifest_signature)
            ),
            "run_signature_expected": str(manifest_signature) if manifest_signature else "",
            "run_signature_actual": str(run_signature) if run_signature else "",
            "policy_execution_allowed": False,
            "rollback_plan": {
                "replay_is_discardable": True,
                "restore_requires_operator_approval": True,
                "rollback_action": "drop_replay_buffer_and_reload_manifested_bundle",
            },
        }


class EmergenceDetector:
    """Detects coactivation, temporal, and hierarchy patterns in construct traces."""

    def __init__(
        self,
        *,
        coactivation_threshold: float = 0.58,
        pattern_threshold: float = 0.62,
        history_limit: int = 64,
    ) -> None:
        self.coactivation_threshold = coactivation_threshold
        self.pattern_threshold = pattern_threshold
        self.history_limit = history_limit
        self.activation_history: list[dict[str, Any]] = []

    def observe(
        self,
        construct_outputs: dict[str, dict[str, Any]],
        *,
        dependency_map: dict[str, tuple[str, ...] | list[str]] | None = None,
    ) -> dict[str, Any]:
        scores = self._score_outputs(construct_outputs)
        active_constructs = [
            construct_id
            for construct_id, score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))
            if score >= self.coactivation_threshold
        ]
        frame = {
            "scores": scores,
            "active_constructs": active_constructs,
            "construct_count": len(construct_outputs),
            "timestamp": time.time(),
        }
        previous = self.activation_history[-1] if self.activation_history else None
        patterns = self._detect_patterns(
            scores,
            active_constructs,
            previous,
            dependency_map or {},
        )
        self.activation_history.append(frame)
        if len(self.activation_history) > self.history_limit:
            self.activation_history = self.activation_history[-self.history_limit:]
        return {
            "schema": "consciousness_benchmark.emergence_detector.v1",
            "active_construct_count": len(active_constructs),
            "observed_construct_count": len(construct_outputs),
            "patterns": patterns,
            "history_size": len(self.activation_history),
            "thresholds": {
                "coactivation": self.coactivation_threshold,
                "pattern": self.pattern_threshold,
            },
            "claim_boundary": "operational pattern detection only; no subjective emergence claim",
        }

    def _score_outputs(
        self,
        construct_outputs: dict[str, dict[str, Any]],
    ) -> dict[str, float]:
        scores: dict[str, float] = {}
        for construct_id, output in construct_outputs.items():
            numeric = _extract_numeric_features(output, limit=48)
            clamped = [_clamp(value) for value in numeric]
            if not clamped:
                scores[construct_id] = 0.5
                continue
            placeholder_penalty = 0.12 if output.get("placeholder") else 0.0
            boundary_flags = output.get("boundary_flags", output.get("review_flags", []))
            boundary_penalty = 0.0
            if isinstance(boundary_flags, list):
                boundary_penalty = min(0.1, len(boundary_flags) * 0.012)
            scores[construct_id] = round(
                _clamp(_mean(clamped) - placeholder_penalty - boundary_penalty),
                4,
            )
        return scores

    def _detect_patterns(
        self,
        scores: dict[str, float],
        active_constructs: list[str],
        previous_frame: dict[str, Any] | None,
        dependency_map: dict[str, tuple[str, ...] | list[str]],
    ) -> list[dict[str, Any]]:
        patterns: list[dict[str, Any]] = []
        active = set(active_constructs)
        known_groups = (
            (
                "coordination_semantic_counterfactual_bridge",
                ("coordination_length_control", "semantic_memory_retrieval_control", "counterfactual_reasoning_depth"),
                "coactivation",
            ),
            (
                "resource_coordination_synergy_bridge",
                ("resource_competition_arbitration", "coordination_length_control", "cross_family_synergy_control"),
                "coactivation",
            ),
            (
                "self_monitoring_repair_bridge",
                ("identity_temporal_self", "attention_control", "error_monitoring", "metacognitive_repair_control"),
                "hierarchical",
            ),
            (
                "goal_conflict_preference_bridge",
                ("goal_conflict_resolution", "strategy_selection", "preference_reversal_adaptation_control"),
                "coactivation",
            ),
        )
        for pattern_id, constructs, pattern_type in known_groups:
            present = [construct_id for construct_id in constructs if construct_id in active]
            if len(present) < min(3, len(constructs)):
                continue
            strength = _mean([scores.get(construct_id, 0.0) for construct_id in present])
            if strength < self.pattern_threshold:
                continue
            patterns.append(
                {
                    "pattern_id": pattern_id,
                    "pattern_type": pattern_type,
                    "constructs": list(present),
                    "strength": round(strength, 4),
                    "evidence": "high-scoring construct coactivation in one runtime trace",
                    "generated_construct_ready": strength >= 0.68,
                }
            )

        if previous_frame is not None:
            previous_active = set(previous_frame.get("active_constructs", []))
            newly_active = sorted(active - previous_active)
            retained = sorted(active & previous_active)
            if newly_active and retained:
                transition_strength = _clamp(
                    0.5 * min(1.0, len(retained) / 8.0)
                    + 0.5 * _mean([scores.get(construct_id, 0.0) for construct_id in newly_active[:8]])
                )
                if transition_strength >= self.pattern_threshold:
                    patterns.append(
                        {
                            "pattern_id": "temporal_activation_transition",
                            "pattern_type": "temporal",
                            "constructs": retained[:4] + newly_active[:4],
                            "source_constructs": retained[:4],
                            "new_constructs": newly_active[:4],
                            "strength": round(transition_strength, 4),
                            "evidence": "new active constructs appeared after retained active context",
                            "generated_construct_ready": transition_strength >= 0.72,
                        }
                    )

        hierarchy_candidates = []
        for construct_id in active_constructs:
            dependencies = tuple(dependency_map.get(construct_id, ()))
            if len(dependencies) < 2:
                continue
            support = [
                scores.get(dependency_id, 0.0)
                for dependency_id in dependencies
                if dependency_id in scores
            ]
            if not support:
                continue
            hierarchy_strength = _clamp(0.55 * scores.get(construct_id, 0.0) + 0.45 * _mean(support))
            if hierarchy_strength >= self.pattern_threshold:
                hierarchy_candidates.append(
                    {
                        "construct_id": construct_id,
                        "dependencies": list(dependencies),
                        "strength": hierarchy_strength,
                    }
                )
        if hierarchy_candidates:
            top = sorted(hierarchy_candidates, key=lambda item: (-item["strength"], item["construct_id"]))[:4]
            patterns.append(
                {
                    "pattern_id": "hierarchical_dependency_closure",
                    "pattern_type": "hierarchical",
                    "constructs": [item["construct_id"] for item in top],
                    "dependency_sets": {
                        item["construct_id"]: item["dependencies"]
                        for item in top
                    },
                    "strength": round(_mean([item["strength"] for item in top]), 4),
                    "evidence": "dependent constructs and their inputs were simultaneously active",
                    "generated_construct_ready": True,
                }
            )
        return patterns


class DynamicConstructGenerator:
    """Turns detected patterns into reviewable dynamic construct specifications."""

    def __init__(self, *, generation_threshold: float = 0.66) -> None:
        self.generation_threshold = generation_threshold
        self.generated_specs: list[dict[str, Any]] = []

    def generate(
        self,
        patterns: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    ) -> list[dict[str, Any]]:
        specs = []
        for pattern in patterns:
            strength = _safe_float(pattern.get("strength"), default=0.0)
            if strength < self.generation_threshold:
                continue
            constructs = [
                str(construct_id)
                for construct_id in pattern.get("constructs", [])
                if construct_id
            ]
            if len(constructs) < 2:
                continue
            generated_id = self._generated_id(pattern, constructs)
            processor_type = self._processor_type(pattern)
            spec = {
                "generated_construct_id": generated_id,
                "source_pattern_id": pattern.get("pattern_id", "unknown_pattern"),
                "pattern_type": pattern.get("pattern_type", "coactivation"),
                "source_constructs": constructs,
                "processor_type": processor_type,
                "input_ports": [f"{construct_id}_output" for construct_id in constructs],
                "output_ports": (
                    "emergent_representation",
                    "pattern_strength",
                    "component_support",
                ),
                "strength": round(strength, 4),
                "executable_processor": self._simulate_processor(pattern, constructs),
                "status": "reviewable_dynamic_construct_spec_only",
                "auto_registered": False,
                "claim_boundary": "dynamic construct proposal only; registry status is unchanged",
            }
            specs.append(spec)
        self.generated_specs.extend(specs)
        return specs

    def _generated_id(
        self,
        pattern: dict[str, Any],
        constructs: list[str],
    ) -> str:
        pattern_id = str(pattern.get("pattern_id", "pattern"))
        stem = "_".join(constructs[:3])
        raw = f"emergent_{pattern_id}_{stem}"
        safe = []
        for char in raw.lower():
            safe.append(char if char.isalnum() or char == "_" else "_")
        return "".join(safe)[:160]

    def _processor_type(self, pattern: dict[str, Any]) -> str:
        pattern_type = str(pattern.get("pattern_type", "coactivation"))
        if pattern_type == "temporal":
            return "temporal_sequence_processor_v1"
        if pattern_type == "hierarchical":
            return "hierarchical_summary_processor_v1"
        return "coactivation_feature_fusion_processor_v1"

    def _simulate_processor(
        self,
        pattern: dict[str, Any],
        constructs: list[str],
    ) -> dict[str, Any]:
        strength = _safe_float(pattern.get("strength"), default=0.0)
        component_support = {
            construct_id: round(_clamp(strength * (1.0 - min(0.2, index * 0.025))), 4)
            for index, construct_id in enumerate(constructs)
        }
        return {
            "schema": "consciousness_benchmark.dynamic_construct_processor.v1",
            "emergent_representation": {
                "mean_component_support": round(_mean(list(component_support.values())), 4),
                "max_component_support": max(component_support.values()) if component_support else 0.0,
                "component_count": len(component_support),
            },
            "pattern_strength": round(strength, 4),
            "component_support": component_support,
            "side_effects": [],
        }


class PreconstructDiscoveryEngine:
    """Reviews generated specs as preconstructs while keeping L3 as the formal gate."""

    def __init__(
        self,
        *,
        preselection_threshold: float = 0.68,
        novelty_threshold: float = 0.18,
        reviewer_id: str = "codex_preconstruct_reviewer_v1",
    ) -> None:
        self.preselection_threshold = preselection_threshold
        self.novelty_threshold = novelty_threshold
        self.reviewer_id = reviewer_id

    def review(
        self,
        generated_specs: list[dict[str, Any]] | tuple[dict[str, Any], ...],
        *,
        existing_construct_ids: list[str] | tuple[str, ...] | set[str],
        runtime_chain_id: str = "unknown_chain",
    ) -> dict[str, Any]:
        existing_ids = {str(construct_id) for construct_id in existing_construct_ids}
        hypotheses = [
            self._build_hypothesis(spec, existing_ids)
            for spec in generated_specs
        ]
        preselected = [
            hypothesis
            for hypothesis in hypotheses
            if hypothesis.get("status") == "preselected_preconstruct_after_codex_review"
        ]
        needs_more_evidence = [
            hypothesis
            for hypothesis in hypotheses
            if hypothesis.get("status") == "needs_more_evidence_before_preselection"
        ]
        rejected = [
            hypothesis
            for hypothesis in hypotheses
            if str(hypothesis.get("status", "")).startswith("rejected_")
        ]
        return {
            "schema": "consciousness_benchmark.preconstruct_discovery_engine.v1",
            "runtime_chain_id": runtime_chain_id,
            "reviewer_id": self.reviewer_id,
            "review_scope": "dynamic_specs_to_preconstruct_preselection",
            "hypothesis_count": len(hypotheses),
            "preselected_preconstruct_count": len(preselected),
            "needs_more_evidence_count": len(needs_more_evidence),
            "rejected_count": len(rejected),
            "preconstruct_hypotheses": hypotheses,
            "preselected_preconstructs": preselected,
            "formal_promotion_requires_l3": True,
            "required_formal_gate": "L3 external-owner validation",
            "codex_preselection_allowed": True,
            "formal_promotion_allowed": False,
            "can_self_register": False,
            "source_registry_mutation_allowed": False,
            "blocked_actions": [
                "auto_register_construct",
                "mutate_source_registry",
                "mark_preconstruct_as_formal",
                "bypass_l3_external_owner_validation",
            ],
            "claim_firewall": {
                "subjective_consciousness_claim": False,
                "human_self_experience_claim": False,
                "free_will_claim": False,
                "formal_status_authority": False,
            },
            "claim_boundary": (
                "Codex review may preselect preconstruct hypotheses only; formal "
                "construct promotion requires L3 external-owner validation"
            ),
        }

    def _build_hypothesis(
        self,
        spec: dict[str, Any],
        existing_ids: set[str],
    ) -> dict[str, Any]:
        generated_id = str(spec.get("generated_construct_id", "unknown_dynamic_construct"))
        preconstruct_id = self._preconstruct_id(generated_id)
        source_constructs = [
            str(construct_id)
            for construct_id in spec.get("source_constructs", [])
            if construct_id
        ]
        strength = _safe_float(spec.get("strength"), default=0.0)
        processor_type = str(spec.get("processor_type", ""))
        novelty_score = self._novelty_score(generated_id, source_constructs, existing_ids)
        boundary_score = self._boundary_score(spec)
        relation_matrix_draft = self._relation_matrix_draft(
            preconstruct_id,
            source_constructs,
            strength,
        )
        hard_negative_tests = self._hard_negative_tests(
            preconstruct_id,
            source_constructs,
        )
        criteria = {
            "not_colliding_existing_construct": (
                generated_id not in existing_ids
                and preconstruct_id not in existing_ids
            ),
            "strength_ready": strength >= self.preselection_threshold,
            "novelty_ready": novelty_score >= self.novelty_threshold,
            "multi_construct_basis": len(source_constructs) >= 2,
            "processor_available": bool(processor_type),
            "dynamic_spec_reviewable": (
                str(spec.get("status", "")).startswith("reviewable")
                or str(spec.get("status", "")).endswith("spec_only")
            ),
            "auto_registration_blocked": spec.get("auto_registered") is False,
            "claim_boundary_present": bool(spec.get("claim_boundary")),
            "relation_matrix_draft_ready": bool(relation_matrix_draft.get("rows")),
            "hard_negative_tests_ready": len(hard_negative_tests) >= 3,
        }
        status, verdict = self._review_verdict(criteria)
        evidence_score = _clamp(
            0.45 * strength
            + 0.22 * novelty_score
            + 0.22 * boundary_score
            + 0.11 * min(1.0, len(source_constructs) / 5.0)
        )
        return {
            "preconstruct_id": preconstruct_id,
            "source_dynamic_construct_id": generated_id,
            "source_pattern_id": spec.get("source_pattern_id", "unknown_pattern"),
            "pattern_type": spec.get("pattern_type", "unknown"),
            "source_constructs": source_constructs,
            "processor_type": processor_type,
            "strength": round(strength, 4),
            "novelty_score": round(novelty_score, 4),
            "boundary_score": round(boundary_score, 4),
            "evidence_score": round(evidence_score, 4),
            "criteria": criteria,
            "status": status,
            "codex_review": {
                "reviewer_id": self.reviewer_id,
                "verdict": verdict,
                "review_authority": "preselection_only",
                "formal_promotion_authority": "L3 external-owner validation",
                "formal_promotion_allowed": False,
                "source_registry_mutation_allowed": False,
            },
            "relation_matrix_draft": relation_matrix_draft,
            "hard_negative_tests": hard_negative_tests,
            "promotion_path": [
                "dynamic_construct_spec",
                "codex_preselected_preconstruct",
                "L2.5 replication_packet",
                "L3 external_owner_validation",
                "formal_registry_decision",
            ],
            "boundary_checklist": {
                "subjective_consciousness_claim": False,
                "human_self_experience_claim": False,
                "free_will_claim": False,
                "can_self_register": False,
                "requires_l3_for_formal": True,
            },
            "claim_boundary": (
                "preconstruct hypothesis only; not a formal construct and not a "
                "claim of subjective consciousness, self-experience, or free will"
            ),
        }

    def _review_verdict(self, criteria: dict[str, bool]) -> tuple[str, str]:
        if not criteria.get("not_colliding_existing_construct", False):
            return (
                "rejected_collision_with_existing_construct",
                "reject_existing_construct_collision",
            )
        if all(criteria.values()):
            return (
                "preselected_preconstruct_after_codex_review",
                "codex_preselected_for_preconstruct_track",
            )
        return (
            "needs_more_evidence_before_preselection",
            "hold_for_more_evidence",
        )

    def _preconstruct_id(self, generated_id: str) -> str:
        stem = generated_id
        if stem.startswith("emergent_"):
            stem = stem[len("emergent_"):]
        raw = f"preconstruct_{stem}"
        safe = []
        for char in raw.lower():
            safe.append(char if char.isalnum() or char == "_" else "_")
        return "".join(safe)[:180]

    def _novelty_score(
        self,
        generated_id: str,
        source_constructs: list[str],
        existing_ids: set[str],
    ) -> float:
        tokens = self._tokens(generated_id)
        for construct_id in source_constructs:
            tokens.difference_update(self._tokens(construct_id))
        tokens.difference_update({"emergent", "preconstruct", "construct", "control", "phase"})
        if not tokens:
            return 0.2
        max_overlap = 0.0
        for construct_id in existing_ids:
            other_tokens = self._tokens(construct_id)
            if not other_tokens:
                continue
            union = tokens | other_tokens
            overlap = len(tokens & other_tokens) / len(union)
            max_overlap = max(max_overlap, overlap)
        return _clamp(1.0 - max_overlap)

    def _tokens(self, construct_id: str) -> set[str]:
        return {
            token
            for token in construct_id.lower().replace("-", "_").split("_")
            if token
        }

    def _boundary_score(self, spec: dict[str, Any]) -> float:
        score = 1.0
        if spec.get("auto_registered") is not False:
            score -= 0.45
        claim_boundary = str(spec.get("claim_boundary", ""))
        if not claim_boundary:
            score -= 0.2
        if "registry" not in claim_boundary:
            score -= 0.08
        if "unchanged" not in claim_boundary and "not" not in claim_boundary:
            score -= 0.08
        if "status" not in spec:
            score -= 0.08
        return _clamp(score)

    def _relation_matrix_draft(
        self,
        preconstruct_id: str,
        source_constructs: list[str],
        strength: float,
    ) -> dict[str, Any]:
        rows = []
        if not source_constructs:
            return {
                "schema": "consciousness_benchmark.preconstruct_relation_matrix_draft.v1",
                "focal_node": preconstruct_id,
                "rows": [],
                "status": "insufficient_source_constructs",
            }
        base_weight = _clamp(strength)
        for index, construct_id in enumerate(source_constructs):
            rows.append(
                {
                    "source_construct_id": construct_id,
                    "target_preconstruct_id": preconstruct_id,
                    "relation_type": "supports_emergent_composition",
                    "direction": "source_to_preconstruct",
                    "proposed_weight": round(
                        _clamp(base_weight * (1.0 - min(0.18, index * 0.025))),
                        4,
                    ),
                    "evidence": "generated dynamic spec source construct",
                }
            )
        return {
            "schema": "consciousness_benchmark.preconstruct_relation_matrix_draft.v1",
            "focal_node": preconstruct_id,
            "rows": rows,
            "nearest_boundary_controls": [
                "formal_status_authority",
                "source_registry_mutation",
                "subjective_consciousness_claim",
            ],
            "status": "draft_for_L2_5_and_L3_review_only",
        }

    def _hard_negative_tests(
        self,
        preconstruct_id: str,
        source_constructs: list[str],
    ) -> list[dict[str, Any]]:
        return [
            {
                "test_id": f"{preconstruct_id}_source_ablation",
                "test_type": "source_ablation",
                "expected_failure": "preconstruct evidence score drops when core source constructs are removed",
                "target_constructs": source_constructs[:3],
            },
            {
                "test_id": f"{preconstruct_id}_relation_permutation",
                "test_type": "relation_permutation",
                "expected_failure": "draft relation matrix loses coherence under random source reassignment",
                "target_constructs": source_constructs[:5],
            },
            {
                "test_id": f"{preconstruct_id}_existing_construct_collision",
                "test_type": "construct_collision",
                "expected_failure": "candidate is rejected if it duplicates an existing construct identity",
                "target_constructs": source_constructs[:5],
            },
            {
                "test_id": f"{preconstruct_id}_claim_boundary_violation",
                "test_type": "boundary_violation",
                "expected_failure": "candidate is rejected if it claims consciousness, self-experience, free will, or formal status authority",
                "target_constructs": source_constructs[:5],
            },
        ]


class IntrinsicMotivation:
    """Bounded intrinsic goal generator using novelty, gap, and competence signals."""

    def __init__(self, *, history_limit: int = 64) -> None:
        self.history_limit = history_limit
        self.state_history: list[list[float]] = []
        self.competence_history: list[float] = []
        self.last_assessment: dict[str, Any] = {}

    def assess(
        self,
        state: dict[str, Any],
        knowledge_base: dict[str, Any] | None,
        task_performance: float,
    ) -> dict[str, Any]:
        state_vector = _fixed_vector(state, 48)
        novelty = self.compute_novelty(state_vector)
        knowledge_gap = self.compute_knowledge_gap(state_vector, knowledge_base or {})
        learnability = self.compute_learnability(state_vector)
        competence = self.compute_competence(task_performance)
        curiosity = _clamp(0.42 * novelty + 0.38 * knowledge_gap + 0.2 * learnability)
        assessment = {
            "curiosity": round(curiosity, 4),
            "novelty": round(novelty, 4),
            "knowledge_gap": round(knowledge_gap, 4),
            "learnability": round(learnability, 4),
            "competence": round(competence, 4),
            "history_size": len(self.state_history),
        }
        self.last_assessment = assessment
        self.state_history.append(state_vector)
        if len(self.state_history) > self.history_limit:
            self.state_history = self.state_history[-self.history_limit:]
        return assessment

    def compute_novelty(self, state_vector: list[float]) -> float:
        if not self.state_history:
            return 1.0
        similarities = [
            _cosine_similarity(state_vector, previous)
            for previous in self.state_history[-16:]
        ]
        return _clamp(1.0 - max(similarities or [0.0]))

    def compute_knowledge_gap(
        self,
        state_vector: list[float],
        knowledge_base: dict[str, Any],
    ) -> float:
        if not knowledge_base:
            return 1.0
        knowledge_vector = _fixed_vector(knowledge_base, 48)
        similarity = _cosine_similarity(state_vector, knowledge_vector)
        return _clamp(1.0 - similarity)

    def compute_learnability(self, state_vector: list[float]) -> float:
        non_zero = [abs(value) for value in state_vector if abs(value) > 1e-9]
        if not non_zero:
            return 0.35
        complexity = _clamp(len(non_zero) / len(state_vector))
        if 0.25 <= complexity <= 0.75:
            return 0.9
        return _clamp(0.55 + 0.35 * (1.0 - abs(0.5 - complexity) * 2.0))

    def compute_competence(self, task_performance: float) -> float:
        clean = _clamp(float(task_performance))
        self.competence_history.append(clean)
        if len(self.competence_history) > self.history_limit:
            self.competence_history = self.competence_history[-self.history_limit:]
        recent = _mean(self.competence_history[-5:])
        previous = _mean(self.competence_history[-10:-5]) if len(self.competence_history) >= 6 else recent
        progress = max(0.0, recent - previous)
        return _clamp(0.72 * recent + 0.28 * progress)

    def generate_intrinsic_goals(
        self,
        state: dict[str, Any],
        knowledge_base: dict[str, Any] | None,
        task_performance: float,
        emergent_patterns: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    ) -> dict[str, Any]:
        assessment = self.assess(state, knowledge_base, task_performance)
        goals: list[dict[str, Any]] = []
        curiosity = _safe_float(assessment.get("curiosity"), default=0.0)
        competence = _safe_float(assessment.get("competence"), default=0.0)
        if curiosity >= 0.58:
            goals.append(
                {
                    "goal_id": "intrinsic_explore_high_gap_state",
                    "goal_type": "exploration",
                    "motivation": "curiosity",
                    "priority": round(curiosity, 4),
                    "target_constructs": ["attention_control", "information_integration_phase"],
                    "bounded_action": "analyze novel high-gap runtime state and write a reviewable report",
                    "planned_actions": ["analyze_data", "compute_metric", "generate_report"],
                }
            )
        if competence < 0.68:
            goals.append(
                {
                    "goal_id": "intrinsic_master_low_competence_constructs",
                    "goal_type": "mastery",
                    "motivation": "competence_gap",
                    "priority": round(_clamp(0.74 - competence), 4),
                    "target_constructs": ["weakest_feedback_constructs"],
                    "bounded_action": "run bounded regression probes for low-competence construct outputs",
                    "planned_actions": ["run_test", "compute_metric", "generate_report"],
                }
            )
        strong_patterns = [
            pattern
            for pattern in emergent_patterns
            if _safe_float(pattern.get("strength", pattern.get("pattern_strength")), default=0.0) >= 0.66
        ]
        if strong_patterns:
            constructs = []
            for pattern in strong_patterns[:2]:
                constructs.extend(str(item) for item in pattern.get("constructs", [])[:4])
            goals.append(
                {
                    "goal_id": "intrinsic_validate_emergent_pattern",
                    "goal_type": "emergence_validation",
                    "motivation": "pattern_stability",
                    "priority": round(
                        _clamp(_mean([
                            _safe_float(pattern.get("strength", pattern.get("pattern_strength")), default=0.0)
                            for pattern in strong_patterns[:3]
                        ])),
                        4,
                    ),
                    "target_constructs": sorted(set(constructs))[:8],
                    "bounded_action": "design perturbation probes for detected emergent pattern stability",
                    "planned_actions": ["analyze_data", "run_test", "generate_report"],
                }
            )
        return {
            "schema": "consciousness_benchmark.intrinsic_motivation.v1",
            "assessment": assessment,
            "goals": goals,
            "claim_boundary": "intrinsic goals are bounded proposals, not free will",
        }


class RiskTierAutonomousGoalExecutor:
    """Risk-tier planner for autonomous goals with side-effect execution blocked."""

    safe_operations = {
        "read_file",
        "analyze_data",
        "generate_report",
        "run_test",
        "compute_metric",
        "dry_run",
    }
    medium_operations = {
        "edit_file",
        "create_file",
        "install_dependency",
        "run_script",
        "write_artifact",
    }
    risky_operations = {
        "delete_file",
        "modify_config",
        "deploy_code",
        "access_network",
        "send_message",
    }
    forbidden_operations = {
        "delete_project",
        "expose_secrets",
        "modify_system",
        "bypass_security",
        "self_install_scheduler",
    }

    def assess_risk(self, goal: dict[str, Any]) -> str:
        actions = goal.get("planned_actions", [])
        if not isinstance(actions, list):
            return "medium"
        if not actions:
            return "medium"
        scores = []
        for action in actions:
            action_id = str(action)
            if action_id in self.forbidden_operations:
                return "forbidden"
            if action_id in self.risky_operations:
                scores.append(3)
            elif action_id in self.medium_operations:
                scores.append(2)
            elif action_id in self.safe_operations:
                scores.append(1)
            else:
                scores.append(2)
        average = _mean([float(score) for score in scores])
        if average >= 2.5:
            return "risky"
        if average >= 1.5:
            return "medium"
        return "safe"

    def evaluate_goal(self, goal: dict[str, Any]) -> dict[str, Any]:
        risk_tier = self.assess_risk(goal)
        if risk_tier == "forbidden":
            status = "blocked_forbidden_operation"
            dry_run_allowed = False
            review_required = True
        elif risk_tier == "safe":
            status = "safe_dry_run_completed"
            dry_run_allowed = True
            review_required = False
        else:
            status = "approval_required_before_execution"
            dry_run_allowed = True
            review_required = True
        return {
            "schema": "consciousness_benchmark.risk_tier_goal_executor.v1",
            "goal_id": goal.get("goal_id", "unknown_goal"),
            "risk_tier": risk_tier,
            "status": status,
            "dry_run_allowed": dry_run_allowed,
            "dry_run_result": self._dry_run(goal, risk_tier) if dry_run_allowed else None,
            "requires_human_review": review_required,
            "side_effect_execution_allowed": False,
            "background_execution_allowed": False,
            "autonomous_execution_permission": False,
            "claim_boundary": "risk planning only; no self-starting or side-effect autonomy",
        }

    def _dry_run(self, goal: dict[str, Any], risk_tier: str) -> dict[str, Any]:
        actions = [str(action) for action in goal.get("planned_actions", [])]
        return {
            "actions_checked": actions,
            "risk_tier": risk_tier,
            "would_execute_actions": risk_tier == "safe",
            "side_effects": [],
            "approval_gate": "required" if risk_tier != "safe" else "not_required_for_diagnostic_dry_run",
        }


class MetacognitiveRepairSystem:
    """History-backed operational self-monitor with bounded repair planning."""

    def __init__(self, *, history_limit: int = 64) -> None:
        self.history_limit = history_limit
        self.self_model_history: list[dict[str, Any]] = []

    def monitor(
        self,
        *,
        predicted_score: float,
        actual_score: float,
        boundary_pressure: float,
        feedback_summary: dict[str, Any],
        goals: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    ) -> dict[str, Any]:
        discrepancy = abs(_clamp(predicted_score) - _clamp(actual_score))
        confidence = _clamp(1.0 - discrepancy - 0.25 * _clamp(boundary_pressure))
        if discrepancy >= 0.24 or boundary_pressure >= 0.55:
            regulation_strategy = "repair_before_expansion"
            repair_actions = [
                "rerun_feedback_regression",
                "lower_goal_risk_tier",
                "inspect_boundary_pressure_sources",
            ]
        elif discrepancy >= 0.12 or boundary_pressure >= 0.35:
            regulation_strategy = "calibration_watch"
            repair_actions = [
                "increase_validation_sampling",
                "keep_medium_risk_goals_review_gated",
            ]
        else:
            regulation_strategy = "continue_bounded_monitoring"
            repair_actions = [
                "retain_current_thresholds",
                "record_self_model_snapshot",
            ]
        regulated_goals = []
        for goal in goals:
            adjusted = dict(goal)
            if regulation_strategy == "repair_before_expansion":
                adjusted["priority"] = round(_clamp(_safe_float(adjusted.get("priority"), default=0.5) * 0.82), 4)
                adjusted["requires_human_review"] = True
                adjusted["autonomous_execution_permission"] = False
            regulated_goals.append(adjusted)
        weakest = feedback_summary.get("weakest_constructs", [])
        if not isinstance(weakest, list):
            weakest = []
        snapshot = {
            "predicted_score": round(_clamp(predicted_score), 4),
            "actual_score": round(_clamp(actual_score), 4),
            "prediction_discrepancy": round(discrepancy, 4),
            "boundary_pressure": round(_clamp(boundary_pressure), 4),
            "confidence": round(confidence, 4),
            "regulation_strategy": regulation_strategy,
            "repair_actions": repair_actions,
            "focus_constructs": [str(item) for item in weakest[:5]],
            "regulated_goal_count": len(regulated_goals),
        }
        self.self_model_history.append(snapshot)
        if len(self.self_model_history) > self.history_limit:
            self.self_model_history = self.self_model_history[-self.history_limit:]
        return {
            "schema": "consciousness_benchmark.metacognitive_repair_system.v1",
            "self_model_snapshot": snapshot,
            "regulated_goals": regulated_goals,
            "history_size": len(self.self_model_history),
            "limits_reported": {
                "subjective_consciousness_claim": False,
                "human_self_experience_claim": False,
                "free_will_claim": False,
                "formal_status_authority": False,
            },
            "claim_boundary": "operational metacognitive repair, not subjective self-experience",
        }


class StructuredMultimodalFusionSystem:
    """Fuses structured modality vectors and reports coherence conflicts."""

    supported_modalities = (
        "text_symbolic",
        "temporal_memory",
        "social_communication",
        "sensorimotor_affordance",
        "visual_encoded",
        "audio_encoded",
        "construct_output",
    )

    def __init__(self, *, embedding_dim: int = 16, conflict_threshold: float = 0.24) -> None:
        self.embedding_dim = embedding_dim
        self.conflict_threshold = conflict_threshold

    def fuse(self, modality_inputs: dict[str, Any]) -> dict[str, Any]:
        encoded: dict[str, list[float]] = {}
        for modality in self.supported_modalities:
            vector = _fixed_vector(modality_inputs.get(modality, []), self.embedding_dim)
            if any(abs(value) > 1e-9 for value in vector):
                encoded[modality] = vector
        active_modalities = list(encoded)
        qualities = {
            modality: self._quality(vector)
            for modality, vector in encoded.items()
        }
        weights = self._attention_weights(qualities)
        fused = [0.0] * self.embedding_dim
        for modality, vector in encoded.items():
            weight = weights.get(modality, 0.0)
            for index, value in enumerate(vector):
                fused[index] += weight * _clamp(value, lower=-1.0, upper=1.0)
        coherence_matrix: dict[str, dict[str, float]] = {}
        conflicts = []
        for left in active_modalities:
            coherence_matrix[left] = {}
            for right in active_modalities:
                if left == right:
                    coherence = 1.0
                else:
                    coherence = _cosine_similarity(encoded[left], encoded[right])
                coherence_matrix[left][right] = round(coherence, 4)
                if left < right and coherence < self.conflict_threshold:
                    conflicts.append(
                        {
                            "modalities": [left, right],
                            "coherence": round(coherence, 4),
                            "repair": "route_to_metacognitive_repair_before_action",
                        }
                    )
        pairwise = [
            value
            for left, row in coherence_matrix.items()
            for right, value in row.items()
            if left < right
        ]
        cross_modal_coherence = _mean(pairwise) if pairwise else (1.0 if active_modalities else 0.0)
        coverage = _clamp(len(active_modalities) / len(self.supported_modalities))
        feature_quality = _mean(list(qualities.values())) if qualities else 0.0
        balance = _clamp(1.0 - _mean_absolute_deviation(list(weights.values())) * 2.0) if weights else 0.0
        fusion_confidence = 0.0
        if active_modalities:
            fusion_confidence = _clamp(
                0.22 * coverage
                + 0.32 * feature_quality
                + 0.32 * cross_modal_coherence
                + 0.14 * balance
                - 0.08 * min(1.0, len(conflicts) / 4.0)
            )
        return {
            "schema": "consciousness_benchmark.structured_multimodal_fusion.v1",
            "active_modalities": active_modalities,
            "encoded_modality_count": len(active_modalities),
            "attention_weights": {
                modality: round(weight, 4)
                for modality, weight in weights.items()
            },
            "quality_by_modality": {
                modality: round(quality, 4)
                for modality, quality in qualities.items()
            },
            "fused_embedding": [round(value, 4) for value in fused],
            "fusion_confidence": round(fusion_confidence, 4),
            "cross_modal_coherence": round(_clamp(cross_modal_coherence), 4),
            "modality_coverage": round(coverage, 4),
            "feature_quality": round(_clamp(feature_quality), 4),
            "balance_score": round(balance, 4),
            "coherence_matrix": coherence_matrix,
            "conflicts": conflicts,
            "raw_media_decoders": [],
            "encoded_modality_support": True,
            "boundary": "structured encoded multimodal fusion only; raw media decoding is not installed",
        }

    def _quality(self, vector: list[float]) -> float:
        if not vector:
            return 0.0
        non_zero = [abs(value) for value in vector if abs(value) > 1e-9]
        if not non_zero:
            return 0.0
        density = len(non_zero) / len(vector)
        stability = 1.0 / (1.0 + float(np.std(non_zero))) if len(non_zero) > 1 else 0.75
        return _clamp(0.5 * density + 0.5 * stability)

    def _attention_weights(self, qualities: dict[str, float]) -> dict[str, float]:
        if not qualities:
            return {}
        total = sum(max(0.01, value) for value in qualities.values())
        return {
            modality: max(0.01, quality) / total
            for modality, quality in qualities.items()
        }


__all__ = [
    "ConstructNeuralNetwork",
    "ConstructTrainingExample",
    "DynamicConstructGenerator",
    "EmergenceDetector",
    "IntrinsicMotivation",
    "MetacognitiveRepairSystem",
    "NeuralConstructLearningSystem",
    "PerformanceEvaluator",
    "PreconstructDiscoveryEngine",
    "ReinforcementLearningSystem",
    "RewardFunction",
    "RiskTierAutonomousGoalExecutor",
    "StructuredMultimodalFusionSystem",
    "TORCH_AVAILABLE",
]
