# Consciousness Benchmark API

## Core Objects

### `ColumnConstruct`

Reference construct backed by two score columns:

- `proxy_col`: internal operational proxy
- `independent_col`: independent behavioral probe score

```python
from consciousness_benchmark.core.construct import ColumnConstruct

construct = ColumnConstruct(
    name="action_agency",
    source_path="runs/.../measurement_validation_raw.csv",
    proxy_col="proxy_agency",
    independent_col="independent_agency",
    mechanism="action-outcome loop",
    validated_in=("thalamus",),
    measurement_limited_in=("transformer_clean",),
    variants={"transformer": "predictive_agency_without_validated_boundary"},
)
result = construct.validate(root=".", n_bootstrap=10000)
print(construct.applicable_to("transformer"))
```

Architecture metadata is descriptive, not a validation shortcut:

- `validated_in`: architectures where this operational construct has passed the current validation standard.
- `measurement_limited_in`: architectures where current probes should be interpreted cautiously.
- `variants`: named architecture-specific profiles or related constructs.
- `applicable_to(architecture)`: returns `validated`, `measurement_limited`, `measurement_limited_with_variant`, `variant_available`, or `untested`.

### `ConstructResult`

Validation result for one construct. Important fields:

- `name`
- `n`
- `r`
- `p`
- `ci_low`
- `ci_high`
- `validated`
- `mechanism`
- `status`
- `validated_in`
- `measurement_limited_in`
- `variants`

Convenience properties:

- `p_formatted`
- `r_with_ci`

### `ConstructValidator`

Runs validation over a list of constructs.

```python
from consciousness_benchmark import ConstructValidator, reference_constructs

validator = ConstructValidator(reference_constructs())
report = validator.validate_all(root=".", n_bootstrap=10000)
```

Reference shorthand:

```python
validator = ConstructValidator.from_reference()
report = validator.validate_all(root=".", n_bootstrap=10000)
```

### `ValidationReport`

Aggregates construct results.

```python
df = report.to_dataframe()
print(report.summary_markdown())
report.save("docs/my_report.md")
```

## Reference Constructs

```python
from consciousness_benchmark import reference_constructs

constructs = reference_constructs()
```

Included constructs:

- `action_agency`
- `boundary_self`
- `identity_temporal_self`
- `action_ownership`
- `distributed_body_schema_self`

## MindLab Adapter

The MindLab adapter instantiates live systems from this workspace and produces
the same columns as the frozen reference data.

```python
from consciousness_benchmark.adapters import MindLabAdapter, thalamus_reference_conditions

condition = thalamus_reference_conditions()[0]
adapter = MindLabAdapter(condition, seed=20260521)
adapter.run(32)
row = adapter.refined_construct_row(quick=True)
```

## CLI

```powershell
python -m consciousness_benchmark reference --bootstrap 10000
python -m consciousness_benchmark online --condition-sets thalamus --seeds 1 --warmup 32 --quick
```

The `online` command is workspace-aware and uses `scripts/benchmark_online_runner.py`
inside the full research repository.
