from __future__ import annotations

from consciousness_benchmark.core.construct import ColumnConstruct


def reference_constructs() -> list[ColumnConstruct]:
    """Return the five frozen reference constructs from the current project.

    These are intentionally operational constructs, not claims of subjective
    consciousness.
    """

    return [
        ColumnConstruct(
            name="action_agency",
            source_path="docs/paper/statistics/reference_20260521/action_agency_raw.csv",
            proxy_col="proxy_agency",
            independent_col="independent_agency",
            mechanism="action-outcome loop",
            validated_in=("thalamus",),
            measurement_limited_in=("transformer", "transformer_clean"),
            variants={"transformer": "predictive_agency_without_validated_boundary"},
        ),
        ColumnConstruct(
            name="boundary_self",
            source_path="docs/paper/statistics/reference_20260521/boundary_self_raw.csv",
            proxy_col="proxy_boundary_self",
            independent_col="independent_self_core_boundary",
            mechanism="workspace",
            validated_in=("thalamus",),
            measurement_limited_in=("transformer",),
            variants={"distributed": "distributed_body_schema_self"},
        ),
        ColumnConstruct(
            name="identity_temporal_self",
            source_path="docs/paper/statistics/reference_20260521/identity_temporal_self_raw.csv",
            proxy_col="proxy_identity_marker_persistence",
            independent_col="test_delayed_identity_recognition",
            mechanism="workspace",
            status="validated",
            validated_in=("thalamus",),
            variants={"transformer": "attention_substrate_identity_temporal_followup"},
        ),
        ColumnConstruct(
            name="action_ownership",
            source_path="docs/paper/statistics/reference_20260521/action_ownership_raw.csv",
            proxy_col="proxy_action_attribution",
            independent_col="test_forced_choice_ownership",
            mechanism="action-outcome loop",
            status="validated",
            validated_in=("thalamus",),
            measurement_limited_in=("transformer", "transformer_clean"),
        ),
        ColumnConstruct(
            name="distributed_body_schema_self",
            source_path="docs/paper/statistics/reference_20260521/distributed_body_schema_self_raw.csv",
            proxy_col="proxy_self_model",
            independent_col="hard_self_without_lesion",
            mechanism="meta-monitor",
            status="validated with graded controls",
            validated_in=("distributed",),
            measurement_limited_in=("generic_self_tests",),
        ),
    ]
