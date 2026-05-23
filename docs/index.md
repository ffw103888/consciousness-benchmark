# Consciousness Benchmark

Operational construct-validation tools for artificial systems.

This project compares internal proxy measurements with independent behavioral
tests. It is designed for measurement validation and diagnostic refinement, not
for declaring that a system has subjective consciousness.

## Start Here

- [Quickstart](quickstart.md)
- [API Reference](api.md)
- [Custom Adapter Tutorial](tutorial_custom_adapter.md)
- [Benchmark MVP Progress](benchmark_mvp_20260521.md)
- [Research Infrastructure Roadmap](research_infrastructure_roadmap_20260521.md)

## Validated Reference Constructs

| Construct | Mechanism |
|---|---|
| `action_agency` | action-outcome loop |
| `boundary_self` | workspace |
| `identity_temporal_self` | workspace |
| `action_ownership` | action-outcome loop |
| `distributed_body_schema_self` | meta-monitor |

## Command Line

```powershell
python -m consciousness_benchmark reference --bootstrap 10000
python -m consciousness_benchmark online --condition-sets thalamus --seeds 1 --warmup 32 --quick
```

## Claim Boundary

The benchmark reports operational proxy-test convergence and mechanism
sensitivity. It does not measure subjective experience.

