"""Run profile presets for developmental growth batch runs."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GrowthBatchProfile:
    """Preset configuration for growth stability batch runs."""

    name: str
    description: str
    rounds: int
    seed_step: int
    stage_ids: tuple[str, ...]
    min_phase2_rows_with_phase2_data: int | None
    min_phase2_temporal_sequence_ratio: float | None
    min_phase2_dynamic_ratio: float | None
    min_phase2_unique_constructs: int | None
    min_phase2_dynamic_construct_count: int | None
    require_health_pass: bool
    run_gatecheck: bool
    theory_case_ids: tuple[str, ...] | None
    theory_no_ablation: bool
    growth_no_ablation: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "rounds": self.rounds,
            "seed_step": self.seed_step,
            "stage_ids": list(self.stage_ids),
            "min_phase2_rows_with_phase2_data": self.min_phase2_rows_with_phase2_data,
            "min_phase2_temporal_sequence_ratio": self.min_phase2_temporal_sequence_ratio,
            "min_phase2_dynamic_ratio": self.min_phase2_dynamic_ratio,
            "min_phase2_unique_constructs": self.min_phase2_unique_constructs,
            "min_phase2_dynamic_construct_count": self.min_phase2_dynamic_construct_count,
            "require_health_pass": self.require_health_pass,
            "run_gatecheck": self.run_gatecheck,
            "theory_case_ids": (
                list(self.theory_case_ids) if self.theory_case_ids is not None else None
            ),
            "theory_no_ablation": self.theory_no_ablation,
            "growth_no_ablation": self.growth_no_ablation,
        }


PROFILES: dict[str, GrowthBatchProfile] = {
    "exploration": GrowthBatchProfile(
        name="exploration",
        description="探索模式：宽松门禁，快速迭代",
        rounds=3,
        seed_step=10,
        stage_ids=("initial", "early_exploration"),
        min_phase2_rows_with_phase2_data=1,
        min_phase2_temporal_sequence_ratio=0.3,
        min_phase2_dynamic_ratio=0.2,
        min_phase2_unique_constructs=1,
        min_phase2_dynamic_construct_count=1,
        require_health_pass=False,
        run_gatecheck=True,
        theory_case_ids=("global_workspace",),
        theory_no_ablation=True,
        growth_no_ablation=True,
    ),
    "validation": GrowthBatchProfile(
        name="validation",
        description="验证模式：标准门禁，完整测试",
        rounds=5,
        seed_step=10,
        stage_ids=("initial", "early_exploration", "midterm_tasking"),
        min_phase2_rows_with_phase2_data=3,
        min_phase2_temporal_sequence_ratio=0.5,
        min_phase2_dynamic_ratio=0.4,
        min_phase2_unique_constructs=3,
        min_phase2_dynamic_construct_count=2,
        require_health_pass=True,
        run_gatecheck=True,
        theory_case_ids=(
            "global_workspace",
            "higher_order_self_model",
            "recurrent_processing",
        ),
        theory_no_ablation=False,
        growth_no_ablation=False,
    ),
    "production": GrowthBatchProfile(
        name="production",
        description="生产模式：严格门禁，完整验证",
        rounds=10,
        seed_step=5,
        stage_ids=(
            "initial",
            "early_exploration",
            "midterm_tasking",
            "advanced_social",
        ),
        min_phase2_rows_with_phase2_data=5,
        min_phase2_temporal_sequence_ratio=0.6,
        min_phase2_dynamic_ratio=0.5,
        min_phase2_unique_constructs=5,
        min_phase2_dynamic_construct_count=3,
        require_health_pass=True,
        run_gatecheck=True,
        theory_case_ids=None,
        theory_no_ablation=False,
        growth_no_ablation=False,
    ),
    "quick_check": GrowthBatchProfile(
        name="quick_check",
        description="快速检查：最小门禁，用于 CI/PR",
        rounds=2,
        seed_step=20,
        stage_ids=("initial",),
        min_phase2_rows_with_phase2_data=1,
        min_phase2_temporal_sequence_ratio=0.2,
        min_phase2_dynamic_ratio=0.1,
        min_phase2_unique_constructs=1,
        min_phase2_dynamic_construct_count=0,
        require_health_pass=False,
        run_gatecheck=True,
        theory_case_ids=("global_workspace",),
        theory_no_ablation=True,
        growth_no_ablation=True,
    ),
}


def get_profile(name: str) -> GrowthBatchProfile:
    if name not in PROFILES:
        available = ", ".join(sorted(PROFILES))
        raise ValueError(f"Unknown profile: {name}. Available: {available}")
    return PROFILES[name]


def list_profiles() -> dict[str, str]:
    return {name: profile.description for name, profile in PROFILES.items()}


def format_profiles_listing() -> str:
    lines = ["Available profiles:"]
    for name, description in list_profiles().items():
        lines.append(f"  {name}: {description}")
    return "\n".join(lines)


def _argv_contains_flag(flag: str, argv: list[str] | None = None) -> bool:
    tokens = argv if argv is not None else sys.argv[1:]
    for token in tokens:
        if token == flag or token.startswith(f"{flag}="):
            return True
    return False


def apply_profile_to_namespace(args: Any, *, argv: list[str] | None = None) -> list[str]:
    """Apply profile defaults to an argparse namespace; return override log lines."""
    profile_name = getattr(args, "profile", None)
    if not profile_name:
        return []

    profile = get_profile(profile_name)
    overrides: list[str] = []

    if not _argv_contains_flag("--rounds", argv):
        args.rounds = profile.rounds
        overrides.append(f"rounds={profile.rounds}")
    if not _argv_contains_flag("--seed-step", argv):
        args.seed_step = profile.seed_step
        overrides.append(f"seed_step={profile.seed_step}")
    if not _argv_contains_flag("--stage-ids", argv):
        args.stage_ids = list(profile.stage_ids)
        overrides.append(f"stage_ids={','.join(profile.stage_ids)}")
    if not _argv_contains_flag("--run-gatecheck", argv):
        args.run_gatecheck = profile.run_gatecheck
        overrides.append(f"run_gatecheck={profile.run_gatecheck}")
    if not _argv_contains_flag("--require-health-pass", argv):
        args.require_health_pass = profile.require_health_pass
        overrides.append(f"require_health_pass={profile.require_health_pass}")
    if not _argv_contains_flag("--no-growth-ablation", argv):
        args.no_growth_ablation = profile.growth_no_ablation
        overrides.append(f"no_growth_ablation={profile.growth_no_ablation}")
    if not _argv_contains_flag("--no-theory-ablation", argv):
        args.no_theory_ablation = profile.theory_no_ablation
        overrides.append(f"no_theory_ablation={profile.theory_no_ablation}")
    if (
        profile.theory_case_ids is not None
        and not _argv_contains_flag("--theory-case-id", argv)
    ):
        args.theory_case_id = list(profile.theory_case_ids)
        overrides.append(f"theory_case_id={','.join(profile.theory_case_ids)}")

    phase2_fields = (
        ("--min-phase2-rows-with-phase2-data", "min_phase2_rows_with_phase2_data"),
        ("--min-phase2-temporal-sequence-ratio", "min_phase2_temporal_sequence_ratio"),
        ("--min-phase2-dynamic-ratio", "min_phase2_dynamic_ratio"),
        ("--min-phase2-unique-constructs", "min_phase2_unique_constructs"),
        ("--min-phase2-dynamic-construct-count", "min_phase2_dynamic_construct_count"),
    )
    for flag, attr in phase2_fields:
        if not _argv_contains_flag(flag, argv):
            setattr(args, attr, getattr(profile, attr))
            overrides.append(f"{attr}={getattr(profile, attr)}")

    return overrides
