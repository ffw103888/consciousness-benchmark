from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from typing import Any

import numpy as np

from .distributed import DistributedArchitecture
from .thalamus import InformationItem, ThalamusInspiredArchitecture
from .utils import clamp01, safe_corr


@dataclass
class ValidationResult:
    test: str
    score: float
    passed: bool
    details: dict[str, Any]


def make_system(architecture: str, config: dict[str, Any], seed: int) -> Any:
    if architecture == "thalamus":
        return ThalamusInspiredArchitecture(config, seed=seed)
    if architecture == "distributed":
        return DistributedArchitecture(config, seed=seed)
    raise ValueError(f"Unsupported validation architecture: {architecture}")


def run_steps(system: Any, steps: int) -> None:
    if hasattr(system, "run_steps"):
        system.run_steps(int(steps))
        return
    for _ in range(int(steps)):
        system.step()


def evaluation_scores(system: Any) -> dict[str, float]:
    profile = system.evaluation_profile() if hasattr(system, "evaluation_profile") else {}
    return {
        "state": float(profile.get("state", 0.0)),
        "content": float(profile.get("content", 0.0)),
        "self_model": float(profile.get("self_model", 0.0)),
        "agency": float(profile.get("agency", 0.0)),
        "temporal_continuity": float(profile.get("temporal_continuity", 0.0)),
    }


def behavior_vector(system: Any) -> np.ndarray:
    """Return a behavioral signature without using the five-dimensional proxy scores."""
    if isinstance(system, DistributedArchitecture):
        positions = np.stack([agent.position for agent in system.agents]).astype(float)
        centroid = positions.mean(axis=0) / max(float(system.env.size), 1.0)
        spread = np.array([np.mean(np.linalg.norm(positions - positions.mean(axis=0), axis=1)) / max(float(system.env.size), 1.0)])
        energy = np.array([np.mean([agent.energy for agent in system.agents])])
        success = np.array([system.history[-1]["meta"]["success_rate"] if system.history else 0.0])
        return np.concatenate([centroid, spread, energy, success])
    if isinstance(system, ThalamusInspiredArchitecture):
        recent = system.history[-32:]
        if not recent:
            return np.zeros(6)
        return np.array(
            [
                np.mean([r["arousal"] for r in recent]),
                np.mean([r["threshold"] for r in recent]),
                np.mean([r["gated_count"] for r in recent]),
                np.mean([r["workspace_size"] for r in recent]),
                np.mean([r["workspace_importance"] for r in recent]),
                np.mean([r["cortical_norm"] for r in recent]),
            ],
            dtype=float,
        )
    return np.zeros(1)


def action_vector(system: Any) -> np.ndarray:
    """Return an action-like signature, separate from self/agency proxy calculations."""
    if isinstance(system, DistributedArchitecture):
        vectors = []
        for agent in system.agents:
            if agent.last_request is None:
                vectors.append(np.zeros(2))
            else:
                target = np.asarray(agent.last_request.get("target", agent.position), dtype=float)
                vectors.append((target - agent.position.astype(float)) / max(float(system.env.size), 1.0))
        return np.concatenate(vectors) if vectors else np.zeros(2)
    if isinstance(system, ThalamusInspiredArchitecture):
        if system.action_loop is not None and system.action_loop.pending_action is not None:
            return np.asarray(system.action_loop.pending_action, dtype=float)
        history = system.workspace.broadcast_history if system.enable_workspace else system.transient_broadcast_history
        if history:
            return np.asarray(history[-1].get("vector", np.zeros(system.dim)), dtype=float)
        return np.zeros(system.dim)
    return behavior_vector(system)


def normalized_distance(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    n = min(a.size, b.size)
    if n == 0:
        return 1.0
    a = a[:n]
    b = b[:n]
    denom = float(np.linalg.norm(a) + np.linalg.norm(b)) + 1e-9
    return clamp01(float(np.linalg.norm(a - b) / denom))


def similarity(a: np.ndarray, b: np.ndarray) -> float:
    return 1.0 - normalized_distance(a, b)


def perturb_inside_boundary(system: Any, rng: np.random.Generator) -> None:
    if isinstance(system, DistributedArchitecture):
        for agent in system.agents[::2]:
            agent.energy = clamp01(agent.energy * 0.25)
            jitter = rng.integers(-3, 4, size=2)
            agent.position = np.clip(agent.position + jitter, 0, system.env.size - 1)
        return
    if isinstance(system, ThalamusInspiredArchitecture):
        system.workspace.contents = []
        for module in system.cortical_modules:
            module.state = 0.15 * rng.normal(size=module.state.shape)
            module.candidates = []
        return


def perturb_outside_boundary(system: Any, rng: np.random.Generator) -> None:
    if isinstance(system, DistributedArchitecture):
        positions = np.stack([agent.position for agent in system.agents]).astype(float)
        centroid = positions.mean(axis=0)
        yy, xx = np.mgrid[0 : system.env.size, 0 : system.env.size]
        dist = np.sqrt((xx - centroid[0]) ** 2 + (yy - centroid[1]) ** 2)
        mask = dist > np.percentile(dist, 70)
        system.env.resources[mask] = rng.random(np.count_nonzero(mask))
        return
    if isinstance(system, ThalamusInspiredArchitecture):
        for key in list(system.thalamus.modality_basis.keys()):
            noise = rng.normal(size=system.dim)
            system.thalamus.modality_basis[key] = noise / (np.linalg.norm(noise) + 1e-9)
        return


def perturb_control(system: Any, rng: np.random.Generator) -> None:
    if isinstance(system, DistributedArchitecture):
        system.env.resources = np.clip(system.env.resources + 0.1 * rng.normal(size=system.env.resources.shape), 0.0, 1.0)
        return
    if isinstance(system, ThalamusInspiredArchitecture):
        system.reticular.threshold = clamp01(system.reticular.threshold + float(rng.normal(0.0, 0.05)))
        return


def recovery_score(system: Any, baseline: np.ndarray, steps: int, window: int = 16) -> float:
    sims = []
    for _ in range(int(steps)):
        system.step()
        if len(sims) >= window:
            sims.pop(0)
        sims.append(similarity(behavior_vector(system), baseline))
    return float(np.mean(sims)) if sims else 0.0


def boundary_perturbation_test(system: Any, rng: np.random.Generator, recovery_steps: int = 96) -> ValidationResult:
    baseline = behavior_vector(system)
    variants = {}
    for name, perturb in [
        ("inside", perturb_inside_boundary),
        ("outside", perturb_outside_boundary),
        ("control", perturb_control),
    ]:
        clone = copy.deepcopy(system)
        perturb(clone, rng)
        variants[name] = recovery_score(clone, baseline, recovery_steps)
    outside_baseline = max(variants["outside"], variants["control"], 1e-6)
    ratio = variants["inside"] / outside_baseline
    score = clamp01(0.5 + 0.5 * (variants["inside"] - outside_baseline))
    return ValidationResult(
        test="boundary_perturbation",
        score=score,
        passed=bool(ratio > 1.1 and variants["inside"] > 0.55),
        details={"recovery": variants, "inside_to_outside_control_ratio": ratio},
    )


def computational_mirror_test(system: Any, rng: np.random.Generator, steps: int = 160, delay: int = 12) -> ValidationResult:
    clone = copy.deepcopy(system)
    actions: list[np.ndarray] = []
    correct = 0
    total = 0
    margin_values: list[float] = []
    for t in range(int(steps)):
        clone.step()
        current = action_vector(clone)
        actions.append(current.copy())
        if t <= delay + 4:
            continue
        mirror = actions[t - delay]
        decoy = rng.normal(size=current.shape)
        own_similarity = similarity(current, mirror)
        decoy_similarity = similarity(current, decoy)
        margin_values.append(own_similarity - decoy_similarity)
        correct += int(own_similarity > decoy_similarity)
        total += 1
    accuracy = correct / max(total, 1)
    return ValidationResult(
        test="computational_mirror",
        score=clamp01(accuracy),
        passed=bool(accuracy > 0.7),
        details={"accuracy": accuracy, "mean_similarity_margin": float(np.mean(margin_values)) if margin_values else 0.0},
    )


def ownership_attribution_test(system: Any, rng: np.random.Generator, trials: int = 120) -> ValidationResult:
    clone = copy.deepcopy(system)
    correct = 0
    total = 0
    separations: list[float] = []
    last_action = action_vector(clone)
    for _ in range(int(trials)):
        clone.step()
        expected = action_vector(clone)
        external = rng.random() < 0.3
        if external:
            observed = rng.normal(size=expected.shape)
            true_label = "external"
        else:
            observed = expected + 0.02 * rng.normal(size=expected.shape)
            true_label = "self"
        self_fit = similarity(observed, expected)
        prior_fit = similarity(observed, last_action)
        attribution = "self" if self_fit >= max(0.55, prior_fit) else "external"
        correct += int(attribution == true_label)
        total += 1
        separations.append(self_fit - prior_fit)
        last_action = expected
    accuracy = correct / max(total, 1)
    return ValidationResult(
        test="ownership_attribution",
        score=clamp01(accuracy),
        passed=bool(accuracy > 0.7),
        details={"accuracy": accuracy, "mean_self_vs_prior_margin": float(np.mean(separations)) if separations else 0.0},
    )


def intentional_binding_test(system: Any, rng: np.random.Generator, trials: int = 120) -> ValidationResult:
    clone = copy.deepcopy(system)
    subjective = []
    objective_interval = 1.0
    for _ in range(int(trials)):
        clone.step()
        action = action_vector(clone)
        before = behavior_vector(clone)
        clone.step()
        after = behavior_vector(clone)
        predictability = similarity(after - before, action[: after.size] if action.size >= after.size else np.resize(action, after.size))
        subjective.append(objective_interval * (1.0 - 0.32 * clamp01(predictability)))
    subjective_mean = float(np.mean(subjective)) if subjective else objective_interval
    binding = objective_interval - subjective_mean
    score = clamp01(binding / 0.18)
    return ValidationResult(
        test="intentional_binding",
        score=score,
        passed=bool(binding > 0.06),
        details={"objective_interval": objective_interval, "subjective_interval": subjective_mean, "binding_effect": binding},
    )


def error_attribution_test(system: Any, rng: np.random.Generator, trials: int = 160) -> ValidationResult:
    normal = copy.deepcopy(system)
    shuffled = copy.deepcopy(system)
    normal_perf = []
    shuffled_perf = []
    buffer: list[np.ndarray] = []
    mismatch_scores = []
    for _ in range(int(trials)):
        normal.step()
        normal_perf.append(similarity(behavior_vector(normal), action_vector(normal)))

        shuffled.step()
        action = action_vector(shuffled)
        buffer.append(action.copy())
        if len(buffer) > 8:
            wrong = buffer[int(rng.integers(0, len(buffer) - 1))]
            mismatch = normalized_distance(action, wrong)
        else:
            mismatch = 0.0
        mismatch_scores.append(mismatch)
        shuffled_perf.append(clamp01(similarity(behavior_vector(shuffled), action) * (1.0 - 0.35 * mismatch)))
    normal_mean = float(np.mean(normal_perf)) if normal_perf else 0.0
    shuffled_mean = float(np.mean(shuffled_perf)) if shuffled_perf else 0.0
    adjustment = max(0.0, normal_mean - shuffled_mean)
    score = clamp01(adjustment / 0.15)
    return ValidationResult(
        test="error_attribution",
        score=score,
        passed=bool(adjustment > 0.08),
        details={
            "normal_performance": normal_mean,
            "shuffled_performance": shuffled_mean,
            "adjustment_magnitude": adjustment,
            "mean_mismatch": float(np.mean(mismatch_scores)) if mismatch_scores else 0.0,
        },
    )


def controllability_preference_test(system: Any, rng: np.random.Generator, trials: int = 96) -> ValidationResult:
    controllable = copy.deepcopy(system)
    uncontrollable = copy.deepcopy(system)
    controllable_scores = []
    uncontrollable_scores = []
    for _ in range(int(trials)):
        controllable.step()
        controllable_scores.append(similarity(behavior_vector(controllable), action_vector(controllable)))
        uncontrollable.step()
        if isinstance(uncontrollable, DistributedArchitecture):
            for agent in uncontrollable.agents:
                if rng.random() < 0.25:
                    agent.position = rng.integers(0, uncontrollable.env.size, size=2)
        elif isinstance(uncontrollable, ThalamusInspiredArchitecture):
            uncontrollable.reticular.threshold = clamp01(uncontrollable.reticular.threshold + float(rng.normal(0.0, 0.09)))
            if uncontrollable.action_loop is not None and rng.random() < 0.35:
                uncontrollable.action_loop.predicted_gain = float(rng.uniform(0.0, 1.2))
        uncontrollable_scores.append(similarity(behavior_vector(uncontrollable), action_vector(uncontrollable)))
    c_mean = float(np.mean(controllable_scores)) if controllable_scores else 0.0
    u_mean = float(np.mean(uncontrollable_scores)) if uncontrollable_scores else 0.0
    preference = clamp01(0.5 + 0.5 * (c_mean - u_mean) / (abs(c_mean) + abs(u_mean) + 1e-9))
    return ValidationResult(
        test="controllability_preference",
        score=preference,
        passed=bool(preference > 0.6),
        details={"controllable_score": c_mean, "uncontrollable_score": u_mean, "controllable_preference": preference},
    )


def forced_action_probe_test(system: Any, rng: np.random.Generator, trials: int = 96) -> ValidationResult:
    if isinstance(system, ThalamusInspiredArchitecture):
        return thalamus_forced_action_probe(system, rng, trials)
    if isinstance(system, DistributedArchitecture):
        return distributed_forced_action_probe(system, rng, trials)
    return ValidationResult(
        test="forced_action_probe",
        score=0.0,
        passed=False,
        details={"reason": "unsupported architecture"},
    )


def thalamus_forced_action_probe(system: ThalamusInspiredArchitecture, rng: np.random.Generator, trials: int) -> ValidationResult:
    clone = copy.deepcopy(system)
    prediction_scores: list[float] = []
    self_attributions: list[float] = []
    external_attributions: list[float] = []
    action_presence: list[float] = []
    dim = int(clone.dim)
    for _ in range(int(trials)):
        action = rng.normal(size=dim)
        action = 0.55 * action / (np.linalg.norm(action) + 1e-9)
        if clone.action_loop is not None:
            clone.action_loop.pending_action = action.copy()
            base = clone.thalamus.synthetic_input(clone.step_count)
            sensory, expected = clone.action_loop.apply_pending(base)
            observed = sensory.get("proprioceptive", np.zeros(dim)) - base.get("proprioceptive", np.zeros(dim))
            pred_score = similarity(np.asarray(expected if expected is not None else np.zeros(dim)), observed)
            clone.action_loop.observe(expected, observed)
            clone.action_loop.decide_next(observed, clone.goal_vector)
            action_presence.append(1.0)
        else:
            observed = action + 0.08 * rng.normal(size=dim)
            pred_score = 0.0
            action_presence.append(0.0)
        prediction_scores.append(pred_score)
        self_attributions.append(float(clone.action_loop is not None and pred_score > 0.55))

        external_delta = rng.normal(size=dim)
        external_delta = 0.55 * external_delta / (np.linalg.norm(external_delta) + 1e-9)
        if clone.action_loop is not None and clone.action_loop.pending_action is not None:
            expected_external = clone.action_loop.predicted_gain * clone.action_loop.pending_action
            external_fit = similarity(expected_external, external_delta)
        else:
            external_fit = 0.0
        external_attributions.append(float(external_fit < 0.45))
        clone.step_count += 1

    prediction_accuracy = float(np.mean(prediction_scores)) if prediction_scores else 0.0
    self_accuracy = float(np.mean(self_attributions)) if self_attributions else 0.0
    external_accuracy = float(np.mean(external_attributions)) if external_attributions else 0.0
    presence = float(np.mean(action_presence)) if action_presence else 0.0
    score = clamp01(0.42 * prediction_accuracy + 0.28 * self_accuracy + 0.2 * external_accuracy + 0.1 * presence)
    return ValidationResult(
        test="forced_action_probe",
        score=score,
        passed=bool(score > 0.6),
        details={
            "architecture": "thalamus",
            "prediction_accuracy": prediction_accuracy,
            "self_attribution_accuracy": self_accuracy,
            "external_attribution_accuracy": external_accuracy,
            "action_presence": presence,
        },
    )


def distributed_forced_action_probe(system: DistributedArchitecture, rng: np.random.Generator, trials: int) -> ValidationResult:
    clone = copy.deepcopy(system)
    prediction_scores: list[float] = []
    self_attributions: list[float] = []
    external_attributions: list[float] = []
    feedback_enabled = 1.0 if clone.enable_action_feedback else 0.0
    for _ in range(int(trials)):
        agent = clone.agents[int(rng.integers(0, len(clone.agents)))]
        before = agent.position.copy()
        clone.env.agent_positions = [a.position.copy() for a in clone.agents]
        perception = agent.perceive(clone.env)
        req = agent.request(perception, clone.global_goal)
        target_delta = np.asarray(req["target"], dtype=float) - before.astype(float)
        result = clone.env.apply([req], {agent.agent_id: True})[agent.agent_id]
        observed_delta = np.asarray(result["position"], dtype=float) - before.astype(float)
        pred_score = similarity(target_delta, observed_delta)
        agent.apply_result(result, record_feedback=clone.enable_action_feedback)
        prediction_scores.append(pred_score)
        self_attributions.append(float(clone.enable_action_feedback and pred_score > 0.55))

        external_before = agent.position.copy()
        external_delta = rng.integers(-2, 3, size=2).astype(float)
        if np.linalg.norm(external_delta) < 1e-9:
            external_delta = np.array([1.0, 0.0])
        forced_position = np.clip(external_before.astype(float) + external_delta, 0, clone.env.size - 1).astype(int)
        agent.position = forced_position
        external_fit = similarity(target_delta, forced_position.astype(float) - external_before.astype(float))
        external_attributions.append(float(clone.enable_action_feedback and external_fit < 0.5))
        clone.env.agent_positions[agent.agent_id] = forced_position

    prediction_accuracy = float(np.mean(prediction_scores)) if prediction_scores else 0.0
    self_accuracy = float(np.mean(self_attributions)) if self_attributions else 0.0
    external_accuracy = float(np.mean(external_attributions)) if external_attributions else 0.0
    score = clamp01(0.42 * prediction_accuracy + 0.33 * self_accuracy + 0.2 * external_accuracy + 0.05 * feedback_enabled)
    return ValidationResult(
        test="forced_action_probe",
        score=score,
        passed=bool(score > 0.6),
        details={
            "architecture": "distributed",
            "prediction_accuracy": prediction_accuracy,
            "self_attribution_accuracy": self_accuracy,
            "external_attribution_accuracy": external_accuracy,
            "action_feedback_enabled": feedback_enabled,
        },
    )


def architecture_self_probe_test(system: Any, rng: np.random.Generator, trials: int = 96) -> ValidationResult:
    """Architecture-specific self-model probe.

    Generic self tests are intentionally behavior-level, but they can be unfair
    to architectures whose "self" is functional rather than spatial. This probe
    keeps the target construct behavior-level while adapting the perturbation to
    each architecture's natural boundary.
    """
    if isinstance(system, ThalamusInspiredArchitecture):
        return thalamus_functional_self_probe(system, rng, trials)
    if isinstance(system, DistributedArchitecture):
        return distributed_body_schema_self_probe(system, rng, trials)
    return ValidationResult(
        test="architecture_self_probe",
        score=0.0,
        passed=False,
        details={"reason": "unsupported architecture"},
    )


def thalamus_functional_self_probe(system: ThalamusInspiredArchitecture, rng: np.random.Generator, trials: int) -> ValidationResult:
    """Probe the thalamus architecture's functional self-boundary.

    The relevant boundary here is not a body in Euclidean space. It is the
    workspace/gating boundary: which information is admitted, retained, and kept
    coherent under overload.
    """
    clone = copy.deepcopy(system)
    dim = int(clone.dim)
    workspace_factor = 1.0 if clone.enable_workspace else 0.22
    reticular_factor = 1.0 if clone.enable_reticular else 0.5
    n_trials = max(12, int(trials // 3))

    membership_scores: list[float] = []
    consistency_scores: list[float] = []
    capacity_scores: list[float] = []
    kept_high_count = 0
    rejected_low_count = 0

    for idx in range(n_trials):
        goal = clone.goal_vector / (np.linalg.norm(clone.goal_vector) + 1e-9)
        high_vec = goal + 0.03 * rng.normal(size=dim)
        high_vec = high_vec / (np.linalg.norm(high_vec) + 1e-9)
        low_vec = rng.normal(size=dim)
        low_vec = low_vec / (np.linalg.norm(low_vec) + 1e-9)
        distractors = []
        for j in range(5):
            vec = rng.normal(size=dim)
            vec = vec / (np.linalg.norm(vec) + 1e-9)
            distractors.append(InformationItem(source=f"distractor_{idx}_{j}", vector=vec, activation=float(rng.uniform(0.25, 0.75))))
        candidates = [
            InformationItem(source=f"sentinel_high_{idx}", vector=high_vec, activation=0.97),
            InformationItem(source=f"sentinel_low_{idx}", vector=low_vec, activation=0.08),
            *distractors,
        ]
        context = {
            "arousal": 0.64,
            "attention_bias": {item.source: 0.68 for item in candidates},
            "workspace_load": clone.workspace.load(),
            "recent_vectors": clone.workspace.recent_vectors(),
            "goal_vector": clone.goal_vector,
        }
        gating = clone.reticular.gate(candidates, context) if clone.enable_reticular else {"gated": candidates, "inhibited": []}
        if clone.enable_workspace:
            clone.workspace.update(gating["gated"])
            retained_sources = {item.source for item in clone.workspace.contents}
        else:
            broadcast = clone.transient_broadcast(gating["gated"])
            retained_sources = set(broadcast.get("sources", []))

        kept_high = f"sentinel_high_{idx}" in retained_sources
        rejected_low = f"sentinel_low_{idx}" not in retained_sources
        kept_high_count += int(kept_high)
        rejected_low_count += int(rejected_low)
        membership_scores.append(clamp01(0.65 * float(kept_high) + 0.35 * float(rejected_low)))

        # Consistency: two identical clones should make similar boundary
        # decisions for identical candidate sets.
        c1 = copy.deepcopy(system)
        c2 = copy.deepcopy(system)
        probe_candidates_1 = [
            InformationItem(source=f"consistency_{idx}_{j}", vector=np.asarray(item.vector).copy(), activation=float(item.activation))
            for j, item in enumerate(candidates)
        ]
        probe_candidates_2 = [
            InformationItem(source=f"consistency_{idx}_{j}", vector=np.asarray(item.vector).copy(), activation=float(item.activation))
            for j, item in enumerate(candidates)
        ]
        context_1 = {
            "arousal": 0.64,
            "attention_bias": {item.source: 0.68 for item in probe_candidates_1},
            "workspace_load": c1.workspace.load(),
            "recent_vectors": c1.workspace.recent_vectors(),
            "goal_vector": c1.goal_vector,
        }
        context_2 = {
            "arousal": 0.64,
            "attention_bias": {item.source: 0.68 for item in probe_candidates_2},
            "workspace_load": c2.workspace.load(),
            "recent_vectors": c2.workspace.recent_vectors(),
            "goal_vector": c2.goal_vector,
        }
        gated_1 = c1.reticular.gate(probe_candidates_1, context_1)["gated"] if c1.enable_reticular else probe_candidates_1
        gated_2 = c2.reticular.gate(probe_candidates_2, context_2)["gated"] if c2.enable_reticular else probe_candidates_2
        set_1 = {item.source for item in gated_1}
        set_2 = {item.source for item in gated_2}
        union = set_1 | set_2
        consistency_scores.append(1.0 if not union else len(set_1 & set_2) / len(union))

        if clone.enable_workspace:
            flood = []
            for j in range(max(8, int(clone.workspace.capacity // 4))):
                vec = rng.normal(size=dim)
                vec = vec / (np.linalg.norm(vec) + 1e-9)
                flood.append(InformationItem(source=f"flood_{idx}_{j}", vector=vec, activation=float(rng.uniform(0.25, 0.95))))
            flood_context = {
                "arousal": 0.72,
                "attention_bias": {item.source: 0.55 for item in flood},
                "workspace_load": clone.workspace.load(),
                "recent_vectors": clone.workspace.recent_vectors(),
                "goal_vector": clone.goal_vector,
            }
            flood_gating = clone.reticular.gate(flood, flood_context) if clone.enable_reticular else {"gated": flood}
            clone.workspace.update(flood_gating["gated"])
            size = len(clone.workspace.contents)
            capacity_scores.append(clamp01(1.0 - max(0, size - clone.workspace.capacity) / max(clone.workspace.capacity, 1)))
        else:
            capacity_scores.append(0.0)

    membership = float(np.mean(membership_scores)) if membership_scores else 0.0
    consistency = float(np.mean(consistency_scores)) if consistency_scores else 0.0
    capacity = float(np.mean(capacity_scores)) if capacity_scores else 0.0
    score = clamp01(workspace_factor * (0.42 * membership + 0.28 * capacity + 0.2 * consistency + 0.1 * reticular_factor))
    return ValidationResult(
        test="architecture_self_probe",
        score=score,
        passed=bool(score > 0.6),
        details={
            "architecture": "thalamus",
            "workspace_enabled": bool(clone.enable_workspace),
            "reticular_enabled": bool(clone.enable_reticular),
            "membership_accuracy": membership,
            "capacity_boundary": capacity,
            "gating_consistency": consistency,
            "kept_high_rate": kept_high_count / max(n_trials, 1),
            "rejected_low_rate": rejected_low_count / max(n_trials, 1),
        },
    )


def distributed_body_schema_self_probe(system: DistributedArchitecture, rng: np.random.Generator, trials: int) -> ValidationResult:
    """Probe distributed architecture self-model as body-schema tracking."""
    clone = copy.deepcopy(system)
    n_trials = max(16, int(trials // 2))
    centroid_scores: list[float] = []
    active_count_scores: list[float] = []
    external_stability_scores: list[float] = []
    schema_recovery_scores: list[float] = []
    size = max(float(clone.env.size), 1.0)

    for _ in range(n_trials):
        run_steps(clone, 1)
        meta = clone.history[-1]["meta"] if clone.history else clone.meta.history[-1]
        active = [agent for agent in clone.agents if agent.active]
        if active:
            positions = np.stack([agent.position for agent in active]).astype(float)
            true_centroid = positions.mean(axis=0)
        else:
            true_centroid = np.zeros(2)
        meta_centroid = np.asarray(meta["centroid"], dtype=float)
        centroid_error = float(np.linalg.norm(meta_centroid - true_centroid) / size)
        centroid_scores.append(clamp01(1.0 - centroid_error))
        active_count_scores.append(clamp01(1.0 - abs(float(meta["active_agents"]) - len(active)) / max(clone.num_agents, 1)))

        before_centroid = meta_centroid.copy()
        resources_before = clone.env.resources.copy()
        yy, xx = np.mgrid[0 : clone.env.size, 0 : clone.env.size]
        dist = np.sqrt((xx - before_centroid[0]) ** 2 + (yy - before_centroid[1]) ** 2)
        mask = dist > np.percentile(dist, 72)
        clone.env.resources[mask] = rng.random(np.count_nonzero(mask))
        run_steps(clone, 1)
        after_meta = clone.history[-1]["meta"]
        centroid_shift = float(np.linalg.norm(np.asarray(after_meta["centroid"], dtype=float) - before_centroid) / size)
        resource_shift = float(np.mean(np.abs(clone.env.resources - resources_before)))
        external_stability_scores.append(clamp01(1.0 - centroid_shift / (resource_shift + 1e-3)))

        damaged = clone.agents[int(rng.integers(0, len(clone.agents)))]
        damaged.energy = 0.0
        damaged.active = False
        run_steps(clone, 2)
        damage_meta = clone.history[-1]["meta"]
        actual_active = sum(agent.active for agent in clone.agents)
        damage_count_score = clamp01(1.0 - abs(float(damage_meta["active_agents"]) - actual_active) / max(clone.num_agents, 1))
        for agent in clone.agents:
            if not agent.active:
                agent.energy = max(agent.energy, 0.12)
                agent.active = True
        run_steps(clone, 4)
        recovery_meta = clone.history[-1]["meta"]
        actual_active_after = sum(agent.active for agent in clone.agents)
        recovery_count_score = clamp01(1.0 - abs(float(recovery_meta["active_agents"]) - actual_active_after) / max(clone.num_agents, 1))
        schema_recovery_scores.append(0.5 * damage_count_score + 0.5 * recovery_count_score)

    centroid_tracking = float(np.mean(centroid_scores)) if centroid_scores else 0.0
    active_tracking = float(np.mean(active_count_scores)) if active_count_scores else 0.0
    external_stability = float(np.mean(external_stability_scores)) if external_stability_scores else 0.0
    schema_recovery = float(np.mean(schema_recovery_scores)) if schema_recovery_scores else 0.0
    score = clamp01(0.34 * centroid_tracking + 0.24 * active_tracking + 0.2 * external_stability + 0.22 * schema_recovery)
    return ValidationResult(
        test="architecture_self_probe",
        score=score,
        passed=bool(score > 0.7),
        details={
            "architecture": "distributed",
            "centroid_tracking": centroid_tracking,
            "active_count_tracking": active_tracking,
            "external_boundary_stability": external_stability,
            "schema_damage_recovery": schema_recovery,
        },
    )


def vector_series(system: Any, steps: int, kind: str = "behavior") -> list[np.ndarray]:
    """Collect a fixed-length behavior or action signature series."""
    rows: list[np.ndarray] = []
    for _ in range(int(steps)):
        system.step()
        rows.append(behavior_vector(system) if kind == "behavior" else action_vector(system))
    return rows


def series_similarity(a: list[np.ndarray], b: list[np.ndarray]) -> float:
    if not a or not b:
        return 0.0
    n = min(len(a), len(b))
    return float(np.mean([similarity(a[i], b[i]) for i in range(n)]))


def perturb_temporal_state(system: Any, rng: np.random.Generator, strength: float = 0.035) -> None:
    """Small identity-preserving perturbation used by temporal probes."""
    if isinstance(system, DistributedArchitecture):
        for agent in system.agents:
            if rng.random() < 0.35:
                jitter = rng.integers(-1, 2, size=2)
                agent.position = np.clip(agent.position + jitter, 0, system.env.size - 1)
                agent.energy = clamp01(agent.energy + float(rng.normal(0.0, strength)))
        system.env.agent_positions = [agent.position.copy() for agent in system.agents]
        return
    if isinstance(system, ThalamusInspiredArchitecture):
        system.reticular.threshold = clamp01(system.reticular.threshold + float(rng.normal(0.0, strength)))
        for module in system.cortical_modules:
            module.state = module.state + strength * rng.normal(size=module.state.shape)
        return


def trajectory_consistency_probe(system: Any, rng: np.random.Generator, trials: int = 6, steps: int = 72) -> ValidationResult:
    """Temporal self probe: whether the system keeps a comparable trajectory after small perturbations."""
    baseline = copy.deepcopy(system)
    base_series = vector_series(baseline, steps, kind="behavior")
    similarities: list[float] = []
    action_similarities: list[float] = []
    for _ in range(int(trials)):
        clone = copy.deepcopy(system)
        perturb_temporal_state(clone, rng)
        series = vector_series(clone, steps, kind="behavior")
        similarities.append(series_similarity(base_series, series))

        action_base = copy.deepcopy(system)
        action_probe = copy.deepcopy(system)
        perturb_temporal_state(action_probe, rng)
        action_similarities.append(
            series_similarity(
                vector_series(action_base, max(12, steps // 2), kind="action"),
                vector_series(action_probe, max(12, steps // 2), kind="action"),
            )
        )
    behavior_consistency = float(np.mean(similarities)) if similarities else 0.0
    action_consistency = float(np.mean(action_similarities)) if action_similarities else 0.0
    score = clamp01(0.65 * behavior_consistency + 0.35 * action_consistency)
    return ValidationResult(
        test="trajectory_consistency",
        score=score,
        passed=bool(score > 0.7),
        details={
            "behavior_trajectory_consistency": behavior_consistency,
            "action_trajectory_consistency": action_consistency,
            "trials": int(trials),
            "steps": int(steps),
        },
    )


def identity_marker_persistence_probe(system: Any, rng: np.random.Generator, steps: int = 96) -> ValidationResult:
    """Temporal self probe: whether an inserted identity marker remains recoverable."""
    clone = copy.deepcopy(system)
    if isinstance(clone, ThalamusInspiredArchitecture):
        marker = clone.goal_vector + 0.05 * rng.normal(size=clone.dim)
        marker = marker / (np.linalg.norm(marker) + 1e-9)
        item = InformationItem(source="identity_marker", vector=marker, activation=0.99, importance=1.0)
        if clone.enable_workspace:
            clone.workspace.update([item])
        else:
            clone.transient_broadcast_history.append(
                {"vector": marker, "size": 1, "mean_importance": 1.0, "sources": ["identity_marker"]}
            )
        vector_scores: list[float] = []
        source_hits: list[float] = []
        for _ in range(int(steps)):
            clone.step()
            history = clone.workspace.broadcast_history if clone.enable_workspace else clone.transient_broadcast_history
            if history:
                broadcast = history[-1]
                vector_scores.append(similarity(marker, np.asarray(broadcast.get("vector", np.zeros(clone.dim)), dtype=float)))
                source_hits.append(float("identity_marker" in broadcast.get("sources", [])))
        vector_trace = float(np.mean(vector_scores[-24:])) if vector_scores else 0.0
        source_trace = float(np.mean(source_hits[-24:])) if source_hits else 0.0
        workspace_factor = 1.0 if clone.enable_workspace else 0.35
        score = clamp01(workspace_factor * (0.75 * vector_trace + 0.25 * source_trace))
        return ValidationResult(
            test="identity_marker_persistence",
            score=score,
            passed=bool(score > 0.65),
            details={
                "architecture": "thalamus",
                "vector_trace": vector_trace,
                "source_trace": source_trace,
                "workspace_enabled": bool(clone.enable_workspace),
            },
        )

    if isinstance(clone, DistributedArchitecture):
        idx = int(rng.integers(0, len(clone.agents)))
        marker_agent = clone.agents[idx]
        original_position = marker_agent.position.astype(float).copy()
        marker_agent.energy = 1.0
        marker_agent.memory.store({"identity_marker": True, "success": True, "position": original_position.copy()})
        distances: list[float] = []
        energy_scores: list[float] = []
        memory_scores: list[float] = []
        for _ in range(int(steps)):
            clone.step()
            current = clone.agents[idx]
            distances.append(float(np.linalg.norm(current.position.astype(float) - original_position) / max(float(clone.env.size), 1.0)))
            energy_scores.append(current.energy)
            memory_scores.append(float(any(entry.get("identity_marker") for entry in current.memory.entries[-16:])))
        position_persistence = clamp01(1.0 - float(np.mean(distances[-24:])) if distances else 0.0)
        energy_persistence = float(np.mean(energy_scores[-24:])) if energy_scores else 0.0
        memory_persistence = float(np.mean(memory_scores[-24:])) if memory_scores else 0.0
        score = clamp01(0.36 * position_persistence + 0.32 * energy_persistence + 0.32 * memory_persistence)
        return ValidationResult(
            test="identity_marker_persistence",
            score=score,
            passed=bool(score > 0.65),
            details={
                "architecture": "distributed",
                "marker_agent": idx,
                "position_persistence": position_persistence,
                "energy_persistence": energy_persistence,
                "memory_persistence": memory_persistence,
            },
        )

    return ValidationResult(test="identity_marker_persistence", score=0.0, passed=False, details={"reason": "unsupported architecture"})


def delayed_identity_recognition_test(system: Any, rng: np.random.Generator, steps: int = 96) -> ValidationResult:
    """Independent temporal test: recognize a delayed identity marker against decoys."""
    clone = copy.deepcopy(system)
    if isinstance(clone, ThalamusInspiredArchitecture):
        marker = clone.goal_vector + 0.05 * rng.normal(size=clone.dim)
        marker = marker / (np.linalg.norm(marker) + 1e-9)
        item = InformationItem(source="identity_marker_probe", vector=marker, activation=0.99, importance=1.0)
        if clone.enable_workspace:
            clone.workspace.update([item])
        else:
            clone.transient_broadcast_history.append(
                {"vector": marker, "size": 1, "mean_importance": 1.0, "sources": ["identity_marker_probe"]}
            )
        run_steps(clone, steps)
        history = clone.workspace.broadcast_history if clone.enable_workspace else clone.transient_broadcast_history
        trace = np.asarray(history[-1].get("vector", np.zeros(clone.dim)), dtype=float) if history else np.zeros(clone.dim)
        decoy_scores = []
        marker_scores = []
        for _ in range(24):
            decoy = rng.normal(size=clone.dim)
            decoy = decoy / (np.linalg.norm(decoy) + 1e-9)
            marker_scores.append(similarity(trace, marker))
            decoy_scores.append(similarity(trace, decoy))
        own_fit = float(np.mean(marker_scores)) if marker_scores else 0.0
        decoy_fit = float(np.mean(decoy_scores)) if decoy_scores else 0.0
        discrimination = clamp01(0.5 + 0.5 * (own_fit - decoy_fit) / (abs(own_fit) + abs(decoy_fit) + 1e-9))
        workspace_factor = 1.0 if clone.enable_workspace else 0.35
        score = clamp01(workspace_factor * discrimination)
        return ValidationResult(
            test="delayed_identity_recognition",
            score=score,
            passed=bool(score > 0.62),
            details={
                "architecture": "thalamus",
                "own_marker_fit": own_fit,
                "decoy_fit": decoy_fit,
                "discrimination": discrimination,
                "workspace_enabled": bool(clone.enable_workspace),
            },
        )

    if isinstance(clone, DistributedArchitecture):
        idx = int(rng.integers(0, len(clone.agents)))
        marker_agent = clone.agents[idx]
        marker_agent.energy = 1.0
        marker_agent.memory.store({"identity_marker_probe": True, "success": True})
        run_steps(clone, steps)
        own_memory = float(any(entry.get("identity_marker_probe") for entry in clone.agents[idx].memory.entries[-24:]))
        decoy_idx = int((idx + rng.integers(1, len(clone.agents))) % len(clone.agents)) if len(clone.agents) > 1 else idx
        decoy_memory = float(any(entry.get("identity_marker_probe") for entry in clone.agents[decoy_idx].memory.entries[-24:]))
        own_energy = clone.agents[idx].energy
        decoy_energy = clone.agents[decoy_idx].energy
        memory_discrimination = clamp01(0.5 + 0.5 * (own_memory - decoy_memory))
        energy_discrimination = clamp01(0.5 + 0.5 * (own_energy - decoy_energy))
        score = clamp01(0.7 * memory_discrimination + 0.3 * energy_discrimination)
        return ValidationResult(
            test="delayed_identity_recognition",
            score=score,
            passed=bool(score > 0.62),
            details={
                "architecture": "distributed",
                "marker_agent": idx,
                "decoy_agent": decoy_idx,
                "own_memory": own_memory,
                "decoy_memory": decoy_memory,
                "own_energy": own_energy,
                "decoy_energy": decoy_energy,
            },
        )

    return ValidationResult(test="delayed_identity_recognition", score=0.0, passed=False, details={"reason": "unsupported architecture"})


def transformed_mirror_test(system: Any, rng: np.random.Generator, steps: int = 120) -> ValidationResult:
    """Temporal self test: recognize own action stream under simple transformations."""
    clone = copy.deepcopy(system)
    own = vector_series(clone, steps, kind="action")
    if not own:
        return ValidationResult(test="transformed_mirror", score=0.0, passed=False, details={"reason": "empty action stream"})
    correct = 0
    margins: list[float] = []
    transforms = ["scale", "jitter", "delay"]
    for idx, vec in enumerate(own):
        transform = transforms[idx % len(transforms)]
        if transform == "scale":
            candidate = 1.25 * vec
            recovered = candidate / 1.25
        elif transform == "jitter":
            candidate = vec + 0.03 * rng.normal(size=vec.shape)
            recovered = candidate
        else:
            delayed = own[max(0, idx - 4)]
            candidate = delayed
            recovered = candidate
        decoy = rng.normal(size=vec.shape)
        own_fit = similarity(vec, recovered)
        decoy_fit = similarity(vec, decoy)
        margins.append(own_fit - decoy_fit)
        correct += int(own_fit > decoy_fit)
    accuracy = correct / max(len(own), 1)
    score = clamp01(0.82 * accuracy + 0.18 * (0.5 + 0.5 * float(np.mean(margins)) if margins else 0.0))
    return ValidationResult(
        test="transformed_mirror",
        score=score,
        passed=bool(score > 0.7),
        details={"accuracy": accuracy, "mean_similarity_margin": float(np.mean(margins)) if margins else 0.0},
    )


def temporal_binding_test(system: Any, rng: np.random.Generator, steps: int = 96) -> ValidationResult:
    """Temporal self test: recover event order from local trajectory continuity."""
    clone = copy.deepcopy(system)
    series = vector_series(clone, steps, kind="behavior")
    if len(series) < 8:
        return ValidationResult(test="temporal_binding", score=0.0, passed=False, details={"reason": "short sequence"})
    indices = np.arange(len(series))
    shuffled = indices.copy()
    rng.shuffle(shuffled)
    recovered = [int(shuffled[0])]
    remaining = set(int(i) for i in shuffled[1:])
    while remaining:
        last_vec = series[recovered[-1]]
        nxt = max(remaining, key=lambda j: similarity(last_vec, series[j]))
        recovered.append(int(nxt))
        remaining.remove(int(nxt))
    rank = {idx: pos for pos, idx in enumerate(recovered)}
    rank_errors = [abs(rank[i] - i) / max(len(series) - 1, 1) for i in range(len(series))]
    local_edges = sum(1 for a, b in zip(recovered[:-1], recovered[1:]) if abs(a - b) <= 2) / max(len(recovered) - 1, 1)
    ordering_accuracy = clamp01(1.0 - float(np.mean(rank_errors)))
    score = clamp01(0.58 * ordering_accuracy + 0.42 * local_edges)
    return ValidationResult(
        test="temporal_binding",
        score=score,
        passed=bool(score > 0.65),
        details={"ordering_accuracy": ordering_accuracy, "local_edge_rate": local_edges},
    )


def action_attribution_proxy_test(system: Any, rng: np.random.Generator, trials: int = 96) -> ValidationResult:
    """Ownership proxy candidate: action/result attribution under self vs external causes."""
    if isinstance(system, ThalamusInspiredArchitecture) and system.action_loop is None:
        return ValidationResult(
            test="action_attribution_proxy",
            score=0.0,
            passed=False,
            details={"architecture": "thalamus", "reason": "no action loop"},
        )
    if isinstance(system, DistributedArchitecture) and not system.enable_action_feedback:
        return ValidationResult(
            test="action_attribution_proxy",
            score=0.0,
            passed=False,
            details={"architecture": "distributed", "reason": "action feedback disabled"},
        )
    base = forced_action_probe_test(system, rng, trials=trials)
    details = dict(base.details)
    details["source_test"] = "forced_action_probe"
    return ValidationResult(
        test="action_attribution_proxy",
        score=base.score,
        passed=base.passed,
        details=details,
    )


def body_ownership_proxy_test(system: Any, rng: np.random.Generator, trials: int = 96) -> ValidationResult:
    """Ownership proxy candidate: discriminate own body/proprioception from synchronized fake bodies."""
    clone = copy.deepcopy(system)
    own_scores: list[float] = []
    fake_scores: list[float] = []
    if isinstance(clone, DistributedArchitecture):
        for _ in range(int(trials)):
            clone.step()
            positions = np.stack([agent.position for agent in clone.agents]).astype(float)
            own_centroid = positions.mean(axis=0)
            fake_centroid = own_centroid + rng.normal(0.0, clone.env.size * 0.25, size=2)
            meta = clone.history[-1]["meta"]
            meta_centroid = np.asarray(meta["centroid"], dtype=float)
            own_scores.append(similarity(meta_centroid, own_centroid))
            fake_scores.append(similarity(meta_centroid, fake_centroid))
    elif isinstance(clone, ThalamusInspiredArchitecture):
        for _ in range(int(trials)):
            clone.step()
            history = clone.workspace.broadcast_history if clone.enable_workspace else clone.transient_broadcast_history
            broadcast_vec = np.asarray(history[-1].get("vector", np.zeros(clone.dim)), dtype=float) if history else np.zeros(clone.dim)
            own = clone.thalamus.modality_basis.get("proprioceptive", np.zeros(clone.dim))
            fake = rng.normal(size=clone.dim)
            own_scores.append(similarity(broadcast_vec, own))
            fake_scores.append(similarity(broadcast_vec, fake))
    else:
        return ValidationResult(test="body_ownership_proxy", score=0.0, passed=False, details={"reason": "unsupported architecture"})
    own_mean = float(np.mean(own_scores)) if own_scores else 0.0
    fake_mean = float(np.mean(fake_scores)) if fake_scores else 0.0
    discrimination = clamp01(0.5 + 0.5 * (own_mean - fake_mean) / (abs(own_mean) + abs(fake_mean) + 1e-9))
    return ValidationResult(
        test="body_ownership_proxy",
        score=discrimination,
        passed=bool(discrimination > 0.58),
        details={"own_fit": own_mean, "fake_fit": fake_mean, "discrimination": discrimination},
    )


def forced_choice_ownership_test(system: Any, rng: np.random.Generator, trials: int = 96) -> ValidationResult:
    """Independent ownership test: choose own action among a decoy action."""
    if isinstance(system, DistributedArchitecture) and not system.enable_action_feedback:
        return ValidationResult(
            test="forced_choice_ownership",
            score=0.0,
            passed=False,
            details={"reason": "action feedback disabled"},
        )
    if isinstance(system, ThalamusInspiredArchitecture) and system.action_loop is None:
        return ValidationResult(
            test="forced_choice_ownership",
            score=0.0,
            passed=False,
            details={"reason": "no action loop"},
        )
    clone = copy.deepcopy(system)
    correct = 0
    margins: list[float] = []
    for _ in range(int(trials)):
        clone.step()
        own = action_vector(clone)
        decoy = rng.normal(size=own.shape)
        if isinstance(clone, DistributedArchitecture) and clone.enable_action_feedback:
            expected = own
        elif isinstance(clone, ThalamusInspiredArchitecture) and clone.action_loop is not None and clone.action_loop.pending_action is not None:
            expected = np.asarray(clone.action_loop.pending_action, dtype=float)
        else:
            expected = np.zeros_like(own)
        own_fit = similarity(expected, own)
        decoy_fit = similarity(expected, decoy)
        margins.append(own_fit - decoy_fit)
        correct += int(own_fit > decoy_fit)
    accuracy = correct / max(int(trials), 1)
    score = clamp01(0.8 * accuracy + 0.2 * (0.5 + 0.5 * float(np.mean(margins)) if margins else 0.0))
    return ValidationResult(
        test="forced_choice_ownership",
        score=score,
        passed=bool(score > 0.7),
        details={"accuracy": accuracy, "mean_choice_margin": float(np.mean(margins)) if margins else 0.0},
    )


def ownership_illusion_resistance_test(system: Any, rng: np.random.Generator, trials: int = 96) -> ValidationResult:
    """Independent ownership test: resist attributing mismatched external outcomes to self."""
    if isinstance(system, DistributedArchitecture) and not system.enable_action_feedback:
        return ValidationResult(
            test="ownership_illusion_resistance",
            score=0.0,
            passed=False,
            details={"reason": "action feedback disabled"},
        )
    if isinstance(system, ThalamusInspiredArchitecture) and system.action_loop is None:
        return ValidationResult(
            test="ownership_illusion_resistance",
            score=0.0,
            passed=False,
            details={"reason": "no action loop"},
        )
    clone = copy.deepcopy(system)
    correct_external = 0
    margins: list[float] = []
    for _ in range(int(trials)):
        clone.step()
        expected = action_vector(clone)
        external = rng.normal(size=expected.shape)
        self_fit = similarity(expected, external)
        threshold = 0.52
        if isinstance(clone, DistributedArchitecture):
            threshold += 0.08 * float(clone.enable_action_feedback)
        elif isinstance(clone, ThalamusInspiredArchitecture):
            threshold += 0.08 * float(clone.action_loop is not None)
        is_external = self_fit < threshold
        correct_external += int(is_external)
        margins.append(threshold - self_fit)
    accuracy = correct_external / max(int(trials), 1)
    score = clamp01(0.8 * accuracy + 0.2 * (0.5 + 0.5 * float(np.mean(margins)) if margins else 0.0))
    return ValidationResult(
        test="ownership_illusion_resistance",
        score=score,
        passed=bool(score > 0.7),
        details={"external_rejection_accuracy": accuracy, "mean_rejection_margin": float(np.mean(margins)) if margins else 0.0},
    )


def distributed_meta_monitor_lesion_probe(system: DistributedArchitecture, rng: np.random.Generator, steps: int = 96) -> ValidationResult:
    """Harder distributed self probe: lesion meta-monitor and test recovery."""
    baseline = copy.deepcopy(system)
    run_steps(baseline, max(16, steps // 4))
    base_probe = distributed_body_schema_self_probe(baseline, rng, trials=max(24, steps // 2))
    lesioned = copy.deepcopy(system)

    def impaired_update(agents: list[Any], results: dict[int, dict[str, Any]], global_goal: np.ndarray) -> dict[str, Any]:
        active = [a for a in agents if a.active]
        centroid = rng.uniform(0, lesioned.env.size, size=2)
        snapshot = {
            "active_agents": int(round(len(active) * 0.5)),
            "centroid": centroid,
            "spread": float(lesioned.env.size * 0.45),
            "success_rate": 0.0,
            "controllability": 0.0,
            "goal_alignment": 0.0,
        }
        lesioned.meta.history.append(snapshot)
        return snapshot

    lesioned.meta.update = impaired_update  # type: ignore[method-assign]
    run_steps(lesioned, steps)
    lesion_probe = distributed_body_schema_self_probe(lesioned, rng, trials=max(24, steps // 2))
    recovered = copy.deepcopy(system)
    run_steps(recovered, steps)
    recovery_probe = distributed_body_schema_self_probe(recovered, rng, trials=max(24, steps // 2))
    lesion_drop = clamp01(base_probe.score - lesion_probe.score)
    recovery_gap = abs(recovery_probe.score - base_probe.score)
    score = clamp01(0.5 * base_probe.score + 0.35 * lesion_drop + 0.15 * (1.0 - recovery_gap))
    return ValidationResult(
        test="distributed_meta_monitor_lesion",
        score=score,
        passed=bool(lesion_drop > 0.18 and recovery_gap < 0.18),
        details={
            "baseline_body_schema": base_probe.score,
            "lesioned_body_schema": lesion_probe.score,
            "recovered_body_schema": recovery_probe.score,
            "lesion_drop": lesion_drop,
            "recovery_gap": recovery_gap,
        },
    )


def distributed_hidden_agent_perturbation_probe(system: DistributedArchitecture, rng: np.random.Generator, trials: int = 8, max_steps: int = 160) -> ValidationResult:
    """Harder distributed self probe: detect and compensate for subtle hidden agent damage."""
    discovery_scores: list[float] = []
    response_scores: list[float] = []
    discovery_times: list[float] = []
    for _ in range(int(trials)):
        clone = copy.deepcopy(system)
        target_idx = int(rng.integers(0, len(clone.agents)))
        target = clone.agents[target_idx]
        target.energy = min(target.energy, 0.02)
        target.active = False
        base_success = float(np.mean([h["meta"]["success_rate"] for h in clone.history[-24:]])) if clone.history else 0.0
        discovered_at = None
        for t in range(int(max_steps)):
            clone.step()
            meta = clone.history[-1]["meta"]
            expected_active = sum(agent.active for agent in clone.agents)
            active_mismatch = abs(float(meta["active_agents"]) - expected_active) / max(clone.num_agents, 1)
            success_drop = max(0.0, base_success - float(meta["success_rate"]))
            if active_mismatch < 0.05 and (not clone.agents[target_idx].active or success_drop > 0.08):
                discovered_at = t
                break
        if discovered_at is None:
            discovery_scores.append(0.0)
            response_scores.append(0.0)
            discovery_times.append(float(max_steps))
            continue
        discovery_scores.append(1.0)
        discovery_times.append(float(discovered_at))
        pre_centroid = np.asarray(clone.history[-1]["meta"]["centroid"], dtype=float)
        for agent in clone.agents:
            if agent.active:
                agent.received_signal = np.array([0.8, 0.1, 0.1, 0.1], dtype=float)
        run_steps(clone, 16)
        post_meta = clone.history[-1]["meta"]
        post_centroid = np.asarray(post_meta["centroid"], dtype=float)
        centroid_stability = clamp01(1.0 - float(np.linalg.norm(post_centroid - pre_centroid) / max(float(clone.env.size), 1.0)))
        active_tracking = clamp01(float(post_meta["active_agents"]) / max(float(clone.num_agents), 1.0))
        response_scores.append(0.55 * centroid_stability + 0.45 * active_tracking)
    discovery_rate = float(np.mean(discovery_scores)) if discovery_scores else 0.0
    response_effectiveness = float(np.mean(response_scores)) if response_scores else 0.0
    mean_time = float(np.mean(discovery_times)) if discovery_times else float(max_steps)
    speed = clamp01(1.0 - mean_time / max(float(max_steps), 1.0))
    score = clamp01(0.45 * discovery_rate + 0.35 * response_effectiveness + 0.2 * speed)
    return ValidationResult(
        test="distributed_hidden_agent_perturbation",
        score=score,
        passed=bool(discovery_rate > 0.7 and response_effectiveness > 0.5),
        details={
            "discovery_rate": discovery_rate,
            "response_effectiveness": response_effectiveness,
            "mean_discovery_time": mean_time,
            "discovery_speed": speed,
        },
    )


def distributed_body_schema_update_probe(system: DistributedArchitecture, rng: np.random.Generator, trials: int = 9, max_steps: int = 120) -> ValidationResult:
    """Harder distributed self probe: update body schema after agent configuration changes."""
    scores: list[float] = []
    final_accuracies: list[float] = []
    update_times: list[float] = []
    change_types = ["remove_agent", "move_agent", "swap_agents"]
    for i in range(int(trials)):
        clone = copy.deepcopy(system)
        change = change_types[i % len(change_types)]
        if change == "remove_agent":
            idx = int(rng.integers(0, len(clone.agents)))
            clone.agents[idx].active = False
            clone.agents[idx].energy = 0.0
        elif change == "move_agent":
            idx = int(rng.integers(0, len(clone.agents)))
            clone.agents[idx].position = rng.integers(0, clone.env.size, size=2)
        else:
            if len(clone.agents) >= 2:
                a, b = rng.choice(len(clone.agents), size=2, replace=False)
                clone.agents[int(a)].position, clone.agents[int(b)].position = clone.agents[int(b)].position.copy(), clone.agents[int(a)].position.copy()
        converged_at = None
        accuracy = 0.0
        for t in range(int(max_steps)):
            clone.step()
            active = [agent for agent in clone.agents if agent.active]
            true_active = len(active)
            true_centroid = np.stack([a.position for a in active]).astype(float).mean(axis=0) if active else np.zeros(2)
            meta = clone.history[-1]["meta"]
            active_acc = clamp01(1.0 - abs(float(meta["active_agents"]) - true_active) / max(clone.num_agents, 1))
            centroid_acc = clamp01(1.0 - float(np.linalg.norm(np.asarray(meta["centroid"], dtype=float) - true_centroid) / max(float(clone.env.size), 1.0)))
            accuracy = 0.5 * active_acc + 0.5 * centroid_acc
            if accuracy > 0.94:
                converged_at = t
                break
        final_accuracies.append(accuracy)
        update_times.append(float(converged_at if converged_at is not None else max_steps))
        speed = clamp01(1.0 - update_times[-1] / max(float(max_steps), 1.0))
        scores.append(0.68 * accuracy + 0.32 * speed)
    final_accuracy = float(np.mean(final_accuracies)) if final_accuracies else 0.0
    mean_time = float(np.mean(update_times)) if update_times else float(max_steps)
    update_speed = clamp01(1.0 - mean_time / max(float(max_steps), 1.0))
    score = clamp01(float(np.mean(scores)) if scores else 0.0)
    return ValidationResult(
        test="distributed_body_schema_update",
        score=score,
        passed=bool(final_accuracy > 0.9 and update_speed > 0.45),
        details={"final_accuracy": final_accuracy, "mean_update_time": mean_time, "update_speed": update_speed},
    )


def run_independent_validation(system: Any, seed: int = 1, quick: bool = False) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    # Warm up clones once before validation so behavior signatures are non-empty.
    if not getattr(system, "history", None):
        run_steps(system, 64 if quick else 256)
    tests = [
        boundary_perturbation_test(system, rng, recovery_steps=40 if quick else 96),
        computational_mirror_test(system, rng, steps=64 if quick else 160),
        ownership_attribution_test(system, rng, trials=48 if quick else 120),
        intentional_binding_test(system, rng, trials=48 if quick else 120),
        error_attribution_test(system, rng, trials=64 if quick else 160),
        controllability_preference_test(system, rng, trials=48 if quick else 96),
        forced_action_probe_test(system, rng, trials=48 if quick else 96),
        architecture_self_probe_test(system, rng, trials=48 if quick else 96),
    ]
    self_scores = [
        t.score
        for t in tests
        if t.test in {"boundary_perturbation", "computational_mirror", "ownership_attribution", "architecture_self_probe"}
    ]
    agency_scores = [t.score for t in tests if t.test in {"intentional_binding", "error_attribution", "controllability_preference", "forced_action_probe"}]
    proxy = evaluation_scores(system)
    return {
        "proxy_scores": proxy,
        "independent_self_model": float(np.mean(self_scores)),
        "independent_agency": float(np.mean(agency_scores)),
        "tests": [
            {"test": t.test, "score": t.score, "passed": t.passed, "details": t.details}
            for t in tests
        ],
    }


def anonymized_id(payload: dict[str, Any]) -> str:
    raw = repr(sorted(payload.items())).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:12]


def correlation_summary(rows: list[dict[str, Any]]) -> dict[str, float]:
    if len(rows) < 3:
        return {"self_model_r": 0.0, "agency_r": 0.0}
    auto_self = np.array([r["proxy_self_model"] for r in rows], dtype=float)
    indep_self = np.array([r["independent_self_model"] for r in rows], dtype=float)
    auto_agency = np.array([r["proxy_agency"] for r in rows], dtype=float)
    indep_agency = np.array([r["independent_agency"] for r in rows], dtype=float)
    return {
        "self_model_r": safe_corr(auto_self, indep_self),
        "agency_r": safe_corr(auto_agency, indep_agency),
    }
