from __future__ import annotations

import argparse

import pytest

from consciousness_benchmark.run_profiles import (
    PROFILES,
    apply_profile_to_namespace,
    format_profiles_listing,
    get_profile,
    list_profiles,
)


def test_all_profiles_loadable() -> None:
    for name in PROFILES:
        profile = get_profile(name)
        assert profile.name == name
        assert profile.rounds > 0


def test_profile_validation_stricter_than_exploration() -> None:
    exploration = get_profile("exploration")
    validation = get_profile("validation")

    assert validation.rounds >= exploration.rounds
    assert validation.min_phase2_rows_with_phase2_data is not None
    assert exploration.min_phase2_rows_with_phase2_data is not None
    assert validation.min_phase2_rows_with_phase2_data > exploration.min_phase2_rows_with_phase2_data
    assert validation.min_phase2_temporal_sequence_ratio is not None
    assert exploration.min_phase2_temporal_sequence_ratio is not None
    assert (
        validation.min_phase2_temporal_sequence_ratio
        > exploration.min_phase2_temporal_sequence_ratio
    )


def test_profile_to_dict() -> None:
    profile = get_profile("validation")
    config = profile.to_dict()

    assert config["rounds"] == 5
    assert config["min_phase2_rows_with_phase2_data"] == 3
    assert isinstance(config["stage_ids"], list)


def test_list_profiles() -> None:
    profiles = list_profiles()

    assert "exploration" in profiles
    assert "validation" in profiles
    assert "production" in profiles
    assert "quick_check" in profiles


def test_format_profiles_listing() -> None:
    text = format_profiles_listing()

    assert text.startswith("Available profiles:")
    assert "exploration:" in text
    assert "quick_check:" in text


def test_unknown_profile_raises() -> None:
    with pytest.raises(ValueError, match="Unknown profile"):
        get_profile("nonexistent")


def test_apply_profile_respects_explicit_rounds_override() -> None:
    args = argparse.Namespace(
        profile="exploration",
        rounds=7,
        seed_step=0,
        stage_ids=[],
        run_gatecheck=False,
        require_health_pass=False,
        no_growth_ablation=False,
        no_theory_ablation=False,
        theory_case_id=[],
        min_phase2_rows_with_phase2_data=None,
        min_phase2_temporal_sequence_ratio=None,
        min_phase2_dynamic_ratio=None,
        min_phase2_unique_constructs=None,
        min_phase2_dynamic_construct_count=None,
    )
    apply_profile_to_namespace(args, argv=["--profile", "exploration", "--rounds", "7"])
    assert args.rounds == 7
    assert args.seed_step == 10
