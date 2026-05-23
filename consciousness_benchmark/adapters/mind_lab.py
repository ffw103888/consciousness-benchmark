from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from mind_lab.distributed import DistributedArchitecture
from mind_lab.thalamus import ThalamusInspiredArchitecture
from mind_lab.validation import (
    action_attribution_proxy_test,
    architecture_self_probe_test,
    boundary_perturbation_test,
    delayed_identity_recognition_test,
    distributed_body_schema_update_probe,
    distributed_hidden_agent_perturbation_probe,
    distributed_meta_monitor_lesion_probe,
    forced_choice_ownership_test,
    identity_marker_persistence_probe,
    make_system,
    run_independent_validation,
    run_steps,
)


@dataclass(frozen=True)
class MindLabCondition:
    architecture: str
    condition: str
    config: dict[str, Any]


def thalamus_reference_conditions() -> list[MindLabCondition]:
    base = {
        "workspace_capacity": 96,
        "initial_threshold": 0.52,
        "inhibition_strength": 0.45,
        "threshold_adaptation_rate": 0.08,
        "dim": 32,
        "measurement_window": 128,
    }
    return [
        MindLabCondition("thalamus", "W-A-", {**base, "enable_workspace": False, "enable_action_loop": False, "action_loop_variant": "none"}),
        MindLabCondition("thalamus", "W+A-", {**base, "enable_workspace": True, "enable_action_loop": False, "action_loop_variant": "none"}),
        MindLabCondition("thalamus", "W-A+", {**base, "enable_workspace": False, "enable_action_loop": True, "action_loop_variant": "learning"}),
        MindLabCondition("thalamus", "W+A+", {**base, "enable_workspace": True, "enable_action_loop": True, "action_loop_variant": "learning"}),
    ]


def distributed_reference_conditions() -> list[MindLabCondition]:
    base = {"num_agents": 12, "world_size": 52, "sensor_range": 6, "memory_capacity": 512, "measurement_window": 128}
    return [
        MindLabCondition("distributed", "feedback_off", {**base, "enable_action_feedback": False}),
        MindLabCondition("distributed", "feedback_on", {**base, "enable_action_feedback": True}),
    ]


def _distributed_meta_monitor_base() -> dict[str, Any]:
    return {
        "num_agents": 12,
        "world_size": 52,
        "sensor_range": 6,
        "memory_capacity": 512,
        "measurement_window": 128,
        "enable_action_feedback": True,
        "enable_coordination": True,
        "enable_meta_monitor": True,
    }


def distributed_meta_monitor_strength_conditions() -> list[MindLabCondition]:
    base = _distributed_meta_monitor_base()
    return [
        MindLabCondition("distributed", f"meta_strength_{strength:.1f}", {**base, "meta_monitor_strength": strength})
        for strength in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    ]


def distributed_meta_monitor_noise_conditions() -> list[MindLabCondition]:
    base = {**_distributed_meta_monitor_base(), "meta_monitor_strength": 1.0}
    return [
        MindLabCondition("distributed", f"meta_noise_{noise:.1f}", {**base, "meta_monitor_noise": noise})
        for noise in [0.0, 0.2, 0.4, 0.6]
    ]


def distributed_meta_monitor_delay_conditions() -> list[MindLabCondition]:
    base = {**_distributed_meta_monitor_base(), "meta_monitor_strength": 1.0}
    return [
        MindLabCondition("distributed", f"meta_delay_{delay}", {**base, "meta_monitor_delay": delay})
        for delay in [0, 2, 4, 8]
    ]


def all_reference_condition_sets() -> dict[str, list[MindLabCondition]]:
    return {
        "thalamus": thalamus_reference_conditions(),
        "distributed": distributed_reference_conditions(),
        "meta-strength": distributed_meta_monitor_strength_conditions(),
        "meta-noise": distributed_meta_monitor_noise_conditions(),
        "meta-delay": distributed_meta_monitor_delay_conditions(),
    }


def legacy_smoke_meta_monitor_strength_conditions() -> list[MindLabCondition]:
    base = {
        "num_agents": 12,
        "world_size": 52,
        "sensor_range": 6,
        "memory_capacity": 512,
        "measurement_window": 128,
        "enable_action_feedback": True,
        "enable_coordination": True,
        "enable_meta_monitor": True,
    }
    return [
        MindLabCondition("distributed", f"meta_strength_{strength:.1f}", {**base, "meta_monitor_strength": strength})
        for strength in [0.0, 0.5, 1.0]
    ]


class MindLabAdapter:
    """Adapter that exposes a mind_lab system through the benchmark interface."""

    def __init__(self, condition: MindLabCondition, seed: int = 20260521):
        self.condition = condition
        self.seed = int(seed)
        self.system = make_system(condition.architecture, condition.config, seed=self.seed)

    def run(self, steps: int) -> None:
        run_steps(self.system, steps)

    def get_internal_state(self) -> dict[str, Any]:
        profile = self.system.evaluation_profile() if hasattr(self.system, "evaluation_profile") else {}
        measurements = self.system.system_measurements() if hasattr(self.system, "system_measurements") else {}
        return {"profile": profile, "measurements": measurements}

    def act(self, observation: Any = None) -> Any:
        del observation
        self.system.step()
        if hasattr(self.system, "history") and self.system.history:
            return self.system.history[-1]
        return None

    def observe(self, result: Any) -> None:
        # mind_lab systems are closed-loop simulations; observation is retained
        # for protocol compatibility with external adapters.
        del result

    def generic_validation_row(self, *, seed: int | None = None, quick: bool = True) -> dict[str, Any]:
        validation = run_independent_validation(self.system, seed=self.seed + 100_000 if seed is None else seed, quick=quick)
        proxy = validation["proxy_scores"]
        tests = {item["test"]: float(item["score"]) for item in validation["tests"]}
        row: dict[str, Any] = {
            "architecture": self.condition.architecture,
            "condition": self.condition.condition,
            "seed": self.seed,
            "proxy_self_model": proxy["self_model"],
            "proxy_agency": proxy["agency"],
            "independent_self_model": validation["independent_self_model"],
            "independent_agency": validation["independent_agency"],
        }
        for name, score in tests.items():
            row[f"test_{name}"] = score
        return row

    def refined_construct_row(self, *, seed: int | None = None, quick: bool = True) -> dict[str, Any]:
        rng = np.random.default_rng(self.seed + 200_000 if seed is None else seed)
        profile = self.system.evaluation_profile() if hasattr(self.system, "evaluation_profile") else {}
        details = profile.get("details", {})
        generic = self.generic_validation_row(seed=self.seed + 250_000 if seed is None else seed + 50_000, quick=quick)

        boundary = boundary_perturbation_test(self.system, rng, recovery_steps=36 if quick else 96)
        architecture_self = architecture_self_probe_test(self.system, rng, trials=36 if quick else 96)
        identity_proxy = identity_marker_persistence_probe(self.system, rng, steps=48 if quick else 96)
        identity_test = delayed_identity_recognition_test(self.system, rng, steps=48 if quick else 96)
        ownership_proxy = action_attribution_proxy_test(self.system, rng, trials=48 if quick else 96)
        ownership_test = forced_choice_ownership_test(self.system, rng, trials=48 if quick else 96)

        hard_hidden = np.nan
        hard_schema = np.nan
        hard_lesion = np.nan
        hard_without_lesion = np.nan
        if isinstance(self.system, DistributedArchitecture):
            hidden = distributed_hidden_agent_perturbation_probe(self.system, rng, trials=3 if quick else 8, max_steps=60 if quick else 160)
            schema = distributed_body_schema_update_probe(self.system, rng, trials=4 if quick else 9, max_steps=60 if quick else 120)
            lesion = distributed_meta_monitor_lesion_probe(self.system, rng, steps=48 if quick else 96)
            hard_hidden = hidden.score
            hard_schema = schema.score
            hard_lesion = lesion.score
            hard_without_lesion = float(np.mean([hard_hidden, hard_schema]))

        row = {
            **generic,
            "proxy_boundary_self": float(details.get("boundary_self_proxy", profile.get("self_model", np.nan))),
            "independent_self_core_boundary": float(np.mean([boundary.score, architecture_self.score])),
            "proxy_identity_marker_persistence": identity_proxy.score,
            "test_delayed_identity_recognition": identity_test.score,
            "proxy_action_attribution": ownership_proxy.score,
            "test_forced_choice_ownership": ownership_test.score,
            "proxy_distributed_body_schema_self": float(profile.get("self_model", np.nan)),
            "hard_hidden_agent_perturbation": hard_hidden,
            "hard_body_schema_update": hard_schema,
            "hard_meta_monitor_lesion": hard_lesion,
            "hard_self_without_lesion": hard_without_lesion,
        }
        if isinstance(self.system, DistributedArchitecture):
            row.update(
                {
                    "meta_monitor_strength": self.system.meta_monitor_strength,
                    "meta_monitor_noise": self.system.meta_monitor_noise,
                    "meta_monitor_delay": self.system.meta_monitor_delay,
                }
            )
        if isinstance(self.system, ThalamusInspiredArchitecture):
            row.update(
                {
                    "enable_workspace": self.system.enable_workspace,
                    "enable_action_loop": self.system.enable_action_loop,
                }
            )
        return row
