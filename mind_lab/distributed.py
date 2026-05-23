from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .utils import clamp01, entropy, safe_corr


Action = dict[str, Any]


@dataclass
class LocalMemory:
    capacity: int = 256
    entries: list[dict[str, Any]] = field(default_factory=list)

    def store(self, entry: dict[str, Any]) -> None:
        self.entries.append(entry)
        if len(self.entries) > self.capacity:
            del self.entries[: len(self.entries) - self.capacity]

    def recent_success(self, window: int = 32) -> float:
        if not self.entries:
            return 0.0
        sample = self.entries[-window:]
        return float(np.mean([1.0 if e.get("success") else 0.0 for e in sample]))


@dataclass
class LocalAgent:
    agent_id: int
    position: np.ndarray
    sensor_range: int
    memory: LocalMemory
    energy: float = 1.0
    active: bool = True
    last_request: Action | None = None
    received_signal: np.ndarray = field(default_factory=lambda: np.zeros(4, dtype=float))

    def perceive(self, env: "GridEnvironment") -> dict[str, Any]:
        x, y = self.position.astype(int)
        r = self.sensor_range
        xmin, xmax = max(0, x - r), min(env.size, x + r + 1)
        ymin, ymax = max(0, y - r), min(env.size, y + r + 1)
        patch = env.resources[ymin:ymax, xmin:xmax]
        yy, xx = np.mgrid[ymin:ymax, xmin:xmax]
        if patch.size == 0 or float(patch.sum()) <= 1e-9:
            target = self.position.copy()
            resource_mean = 0.0
        else:
            weights = patch / (float(patch.sum()) + 1e-9)
            target = np.array([float(np.sum(xx * weights)), float(np.sum(yy * weights))])
            resource_mean = float(np.mean(patch))
        neighbors = [a for a in env.agent_positions if np.linalg.norm(a - self.position) <= r and not np.allclose(a, self.position)]
        return {
            "target": target,
            "resource_mean": resource_mean,
            "neighbor_count": len(neighbors),
            "local_entropy": entropy(patch, bins=12),
        }

    def request(self, perception: dict[str, Any], global_goal: np.ndarray) -> Action:
        direction = perception["target"] - self.position
        if np.linalg.norm(direction) < 1e-6:
            direction = global_goal - self.position
        if np.linalg.norm(direction) > 1e-6:
            direction = direction / np.linalg.norm(direction)
        arousal = float(self.received_signal[0]) if self.received_signal.size else 0.5
        priority = clamp01(0.45 * (1.0 - self.energy) + 0.35 * perception["resource_mean"] + 0.2 * arousal)
        target = np.rint(self.position + direction).astype(int)
        self.last_request = {
            "agent_id": self.agent_id,
            "type": "move_eat",
            "target": target,
            "priority": priority,
            "energy": self.energy,
            "local_entropy": perception["local_entropy"],
        }
        return self.last_request

    def apply_result(self, result: dict[str, Any], record_feedback: bool = True) -> None:
        self.position = np.asarray(result.get("position", self.position), dtype=int)
        self.energy = clamp01(self.energy + float(result.get("energy_delta", 0.0)) - 0.0025)
        self.active = self.energy > 0.035
        if record_feedback:
            self.memory.store(result)


class GridEnvironment:
    def __init__(self, size: int, num_agents: int, rng: np.random.Generator):
        self.size = int(size)
        self.rng = rng
        self.resources = self._make_resources()
        self.agent_positions = [
            np.array([rng.integers(size // 4, 3 * size // 4), rng.integers(size // 4, 3 * size // 4)], dtype=int)
            for _ in range(num_agents)
        ]
        self.t = 0

    def _make_resources(self) -> np.ndarray:
        size = self.size
        yy, xx = np.mgrid[0:size, 0:size]
        centers = [
            (size * 0.28, size * 0.33, 0.8),
            (size * 0.72, size * 0.65, 0.65),
            (size * 0.55, size * 0.22, 0.55),
        ]
        resources = np.zeros((size, size), dtype=float)
        for cx, cy, amp in centers:
            resources += amp * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * (size * 0.14) ** 2))
        resources += 0.04 * self.rng.random((size, size))
        return np.clip(resources, 0.0, 1.0)

    def regenerate(self) -> None:
        self.resources *= 0.998
        self.resources += 0.006 * self._make_resources()
        self.resources = np.clip(self.resources, 0.0, 1.0)
        self.t += 1

    def apply(self, requests: list[Action], allocations: dict[int, bool]) -> dict[int, dict[str, Any]]:
        results: dict[int, dict[str, Any]] = {}
        occupied = {tuple(pos.tolist()) for pos in self.agent_positions}
        for req in requests:
            aid = int(req["agent_id"])
            current = self.agent_positions[aid]
            target = np.clip(np.asarray(req["target"], dtype=int), 0, self.size - 1)
            allowed = allocations.get(aid, True)
            if allowed and tuple(target.tolist()) not in occupied:
                new_pos = target
            else:
                new_pos = current
            x, y = new_pos.astype(int)
            eaten = min(float(self.resources[y, x]), 0.12)
            self.resources[y, x] -= eaten
            rest_bonus = 0.006 if not allowed else 0.0
            self.agent_positions[aid] = new_pos
            results[aid] = {
                "agent_id": aid,
                "position": new_pos,
                "energy_delta": eaten * 1.9 + rest_bonus,
                "success": bool(np.any(new_pos != current) or eaten > 0.01),
                "eaten": eaten,
            }
        self.regenerate()
        return results


class CoordinationLayer:
    def __init__(self):
        self.history: list[dict[str, Any]] = []
        self.round_robin = 0

    def coordinate(self, requests: list[Action], global_goal: np.ndarray) -> tuple[dict[int, bool], np.ndarray, dict[str, Any]]:
        target_map: dict[tuple[int, int], list[Action]] = {}
        for req in requests:
            target_map.setdefault(tuple(np.asarray(req["target"], dtype=int).tolist()), []).append(req)

        allocations: dict[int, bool] = {}
        conflicts = 0
        winners: list[int] = []
        for _, contenders in target_map.items():
            if len(contenders) == 1:
                allocations[int(contenders[0]["agent_id"])] = True
                continue
            conflicts += len(contenders) - 1
            contenders = sorted(contenders, key=lambda r: (float(r["priority"]), -int(r["agent_id"])), reverse=True)
            winner = int(contenders[0]["agent_id"])
            winners.append(winner)
            for req in contenders:
                allocations[int(req["agent_id"])] = int(req["agent_id"]) == winner

        priorities = np.array([float(r["priority"]) for r in requests], dtype=float) if requests else np.zeros(1)
        signal = np.array(
            [
                clamp01(float(np.mean(priorities))),
                clamp01(conflicts / max(len(requests), 1)),
                clamp01(np.linalg.norm(global_goal) / 100.0),
                clamp01(len(winners) / max(len(requests), 1)),
            ],
            dtype=float,
        )
        summary = {"conflicts": conflicts, "winners": winners, "mean_priority": float(np.mean(priorities))}
        self.history.append(summary)
        return allocations, signal, summary


class MetaMonitor:
    def __init__(self):
        self.history: list[dict[str, Any]] = []
        self.predicted_centroids: list[np.ndarray] = []
        self.actual_centroids: list[np.ndarray] = []

    def update(self, agents: list[LocalAgent], results: dict[int, dict[str, Any]], global_goal: np.ndarray) -> dict[str, Any]:
        active = [a for a in agents if a.active]
        if active:
            positions = np.stack([a.position for a in active]).astype(float)
            centroid = positions.mean(axis=0)
            spread = float(np.mean(np.linalg.norm(positions - centroid, axis=1)))
        else:
            centroid = np.zeros(2)
            spread = 0.0
        success_rate = float(np.mean([1.0 if r.get("success") else 0.0 for r in results.values()])) if results else 0.0
        controllability = float(np.mean([a.memory.recent_success() for a in agents])) if agents else 0.0
        goal_alignment = 1.0 - min(float(np.linalg.norm(centroid - global_goal)) / 60.0, 1.0)
        snapshot = {
            "active_agents": len(active),
            "centroid": centroid,
            "spread": spread,
            "success_rate": success_rate,
            "controllability": controllability,
            "goal_alignment": clamp01(goal_alignment),
        }
        self.history.append(snapshot)
        return snapshot


class DistributedArchitecture:
    def __init__(self, config: dict[str, Any], seed: int = 2):
        self.config = config
        self.rng = np.random.default_rng(seed)
        self.num_agents = int(config.get("num_agents", 12))
        self.enable_action_feedback = bool(config.get("enable_action_feedback", True))
        self.enable_coordination = bool(config.get("enable_coordination", True))
        self.enable_meta_monitor = bool(config.get("enable_meta_monitor", True))
        self.meta_monitor_strength = clamp01(float(config.get("meta_monitor_strength", 1.0)))
        self.meta_monitor_noise = clamp01(float(config.get("meta_monitor_noise", 0.0)))
        self.meta_monitor_delay = max(0, int(config.get("meta_monitor_delay", 0)))
        self.measurement_window = int(config.get("measurement_window", 256))
        self.env = GridEnvironment(int(config.get("world_size", 48)), self.num_agents, self.rng)
        self.agents = [
            LocalAgent(
                agent_id=i,
                position=self.env.agent_positions[i].copy(),
                sensor_range=int(config.get("sensor_range", 6)),
                memory=LocalMemory(capacity=int(config.get("memory_capacity", 512))),
            )
            for i in range(self.num_agents)
        ]
        self.coordinator = CoordinationLayer()
        self.meta = MetaMonitor()
        goal_xy = config.get("global_goal_xy")
        self.global_goal = (
            np.asarray(goal_xy, dtype=float)
            if goal_xy is not None
            else np.array([self.env.size * 0.52, self.env.size * 0.48], dtype=float)
        )
        self._meta_delay_buffer: list[dict[str, Any]] = []
        self.step_count = 0
        self.history: list[dict[str, Any]] = []

    def _null_meta_snapshot(self) -> dict[str, Any]:
        return {
            "active_agents": 0,
            "centroid": np.zeros(2),
            "spread": 0.0,
            "success_rate": 0.0,
            "controllability": 0.0,
            "goal_alignment": 0.0,
        }

    def _mix_meta_snapshots(self, true_snapshot: dict[str, Any]) -> dict[str, Any]:
        """Apply graded meta-monitor degradation for validation controls."""
        if not self.enable_meta_monitor:
            return self._null_meta_snapshot()
        strength = self.meta_monitor_strength
        self._meta_delay_buffer.append(
            {
                key: (value.copy() if isinstance(value, np.ndarray) else value)
                for key, value in true_snapshot.items()
            }
        )
        if len(self._meta_delay_buffer) > max(self.meta_monitor_delay + 4, 8):
            del self._meta_delay_buffer[: len(self._meta_delay_buffer) - max(self.meta_monitor_delay + 4, 8)]
        if self.meta_monitor_delay > 0 and len(self._meta_delay_buffer) > self.meta_monitor_delay:
            reference = self._meta_delay_buffer[-self.meta_monitor_delay - 1]
        else:
            reference = true_snapshot
        null = self._null_meta_snapshot()
        noisy_centroid = np.asarray(reference["centroid"], dtype=float).copy()
        if self.meta_monitor_noise > 0:
            noisy_centroid = noisy_centroid + self.rng.normal(0.0, self.meta_monitor_noise * self.env.size * 0.2, size=2)
        snapshot = {
            "active_agents": int(round(strength * float(reference["active_agents"]) + (1.0 - strength) * float(null["active_agents"]))),
            "centroid": np.clip(strength * noisy_centroid + (1.0 - strength) * np.asarray(null["centroid"], dtype=float), 0, self.env.size - 1),
            "spread": float(clamp01(strength) * float(reference["spread"]) + (1.0 - strength) * float(null["spread"])),
            "success_rate": clamp01(strength * float(reference["success_rate"]) + (1.0 - strength) * float(null["success_rate"])),
            "controllability": clamp01(strength * float(reference["controllability"]) + (1.0 - strength) * float(null["controllability"])),
            "goal_alignment": clamp01(strength * float(reference["goal_alignment"]) + (1.0 - strength) * float(null["goal_alignment"])),
        }
        return snapshot

    def step(self) -> dict[str, Any]:
        self.env.agent_positions = [a.position.copy() for a in self.agents]
        requests: list[Action] = []
        for agent in self.agents:
            if not agent.active:
                agent.energy = clamp01(agent.energy + 0.012)
                if agent.energy > 0.09:
                    agent.active = True
                else:
                    continue
            if not agent.active:
                continue
            perception = agent.perceive(self.env)
            requests.append(agent.request(perception, self.global_goal))
        if self.enable_coordination:
            allocations, signal, coord_summary = self.coordinator.coordinate(requests, self.global_goal)
            coord_summary["coordination_enabled"] = True
        else:
            target_map: dict[tuple[int, int], int] = {}
            for req in requests:
                target = tuple(np.asarray(req["target"], dtype=int).tolist())
                target_map[target] = target_map.get(target, 0) + 1
            conflicts = sum(max(0, count - 1) for count in target_map.values())
            priorities = np.array([float(r["priority"]) for r in requests], dtype=float) if requests else np.zeros(1)
            allocations = {int(req["agent_id"]): True for req in requests}
            signal = np.zeros(4, dtype=float)
            coord_summary = {
                "conflicts": conflicts,
                "winners": [],
                "mean_priority": float(np.mean(priorities)),
                "coordination_enabled": False,
            }
        for agent in self.agents:
            agent.received_signal = signal.copy()
        results = self.env.apply(requests, allocations)
        for agent in self.agents:
            if agent.agent_id in results:
                agent.apply_result(results[agent.agent_id], record_feedback=self.enable_action_feedback)
        true_meta_snapshot = self.meta.update(self.agents, results, self.global_goal)
        meta_snapshot = self._mix_meta_snapshots(true_meta_snapshot)
        self.meta.history[-1] = meta_snapshot
        self.step_count += 1
        record = {
            "step": self.step_count,
            "coordination": coord_summary,
            "meta": meta_snapshot,
            "mean_energy": float(np.mean([a.energy for a in self.agents])),
            "resource_mean": float(np.mean(self.env.resources)),
        }
        self.history.append(record)
        if len(self.history) > 5000:
            del self.history[:1000]
        return record

    def run_steps(self, steps: int) -> dict[str, Any]:
        records = [self.step() for _ in range(int(steps))]
        return {
            "step": self.step_count,
            "mean_energy": float(np.mean([a.energy for a in self.agents])),
            "active_agents": int(sum(a.active for a in self.agents)),
            "mean_success": float(np.mean([r["meta"]["success_rate"] for r in records])) if records else 0.0,
            "mean_conflicts": float(np.mean([r["coordination"]["conflicts"] for r in records])) if records else 0.0,
            "goal_alignment": records[-1]["meta"]["goal_alignment"] if records else 0.0,
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
        energy = np.array([r["mean_energy"] for r in recent], dtype=float)
        success = np.array([r["meta"]["success_rate"] for r in recent], dtype=float)
        align = np.array([r["meta"]["goal_alignment"] for r in recent], dtype=float)
        conflicts = np.array([r["coordination"]["conflicts"] for r in recent], dtype=float)
        controllability = np.array([r["meta"]["controllability"] for r in recent], dtype=float)
        active = np.array([r["meta"]["active_agents"] for r in recent], dtype=float)
        spread = np.array([r["meta"]["spread"] for r in recent], dtype=float)
        active_ratio = clamp01(float(np.mean(active)) / max(float(self.num_agents), 1.0))
        spread_stability = clamp01(1.0 - float(np.std(spread) / (np.mean(spread) + 1e-6)))
        energy_stability = clamp01(1.0 - float(np.std(energy) / (np.mean(energy) + 1e-6)))
        low_conflict = clamp01(1.0 - float(np.mean(conflicts)) / max(float(self.num_agents), 1.0))
        boundary_self = clamp01(0.38 * active_ratio + 0.25 * spread_stability + 0.22 * energy_stability + 0.15 * low_conflict)
        temporal_self = clamp01(0.58 * (1.0 - float(np.std(align))) + 0.24 * spread_stability + 0.18 * energy_stability)
        ownership_self = clamp01(float(np.mean(controllability)))
        legacy_self_model_stability = clamp01(float(np.mean(align)))
        return {
            "phi_proxy": clamp01(0.5 * abs(safe_corr(energy, success)) + 0.5 * entropy(success, bins=12)),
            "pci_proxy": clamp01(entropy(conflicts, bins=12)),
            "self_model_stability": boundary_self,
            "boundary_self_proxy": boundary_self,
            "temporal_self_proxy": temporal_self,
            "ownership_self_proxy": ownership_self,
            "legacy_self_model_stability": legacy_self_model_stability,
            "temporal_continuity": clamp01(1.0 - float(np.std(align))),
            "agency_proxy": clamp01(float(np.mean(controllability))),
            "actual_success_rate": clamp01(float(np.mean(success))),
            "action_feedback_enabled": 1.0 if self.enable_action_feedback else 0.0,
            "coordination_enabled": 1.0 if self.enable_coordination else 0.0,
            "instability": clamp01(float(np.std(energy)) + float(np.mean(conflicts)) / max(self.num_agents, 1)),
            "avoidance_rate": 0.0,
            "negative_value": clamp01(1.0 - float(np.mean(energy))),
        }

    def evaluation_profile(self) -> dict[str, Any]:
        m = self.system_measurements()
        recent_conflicts = np.mean([h["coordination"]["conflicts"] for h in self.history[-128:]]) if self.history else 0.0
        return {
            "state": clamp01(0.45 * m["pci_proxy"] + 0.35 * (1.0 - m["instability"]) + 0.2 * m["phi_proxy"]),
            "content": clamp01(0.45 * entropy(self.env.resources, bins=24) + 0.35 * m["phi_proxy"] + 0.2 * min(recent_conflicts / 4.0, 1.0)),
            "self_model": clamp01(m["self_model_stability"]),
            "agency": clamp01(m["agency_proxy"]),
            "temporal_continuity": clamp01(m["temporal_continuity"]),
            "details": m,
        }

    def __setstate__(self, state: dict[str, Any]) -> None:
        self.__dict__.update(state)
        config = getattr(self, "config", {}) or {}
        if not hasattr(self, "enable_action_feedback"):
            self.enable_action_feedback = bool(config.get("enable_action_feedback", True))
        if not hasattr(self, "enable_coordination"):
            self.enable_coordination = bool(config.get("enable_coordination", True))
        if not hasattr(self, "enable_meta_monitor"):
            self.enable_meta_monitor = bool(config.get("enable_meta_monitor", True))
        if not hasattr(self, "meta_monitor_strength"):
            self.meta_monitor_strength = clamp01(float(config.get("meta_monitor_strength", 1.0)))
        if not hasattr(self, "meta_monitor_noise"):
            self.meta_monitor_noise = clamp01(float(config.get("meta_monitor_noise", 0.0)))
        if not hasattr(self, "meta_monitor_delay"):
            self.meta_monitor_delay = max(0, int(config.get("meta_monitor_delay", 0)))
        if not hasattr(self, "_meta_delay_buffer"):
            self._meta_delay_buffer = []
        if not hasattr(self, "measurement_window"):
            self.measurement_window = int(config.get("measurement_window", 256))
