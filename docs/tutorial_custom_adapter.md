# Tutorial: Adapting a Custom System

This MVP benchmark uses column-based validation: an adapter should produce rows
with proxy scores and independent-test scores. A mature third-party adapter can
wrap any model as long as it can expose comparable measurements.

## Minimal Row Schema

For one or more constructs, produce columns like:

```python
row = {
    "architecture": "my_architecture",
    "condition": "my_condition",
    "seed": 0,
    "proxy_agency": 0.72,
    "independent_agency": 0.69,
    "proxy_boundary_self": 0.81,
    "independent_self_core_boundary": 0.78,
}
```

You can then validate with `ColumnConstruct`:

```python
from consciousness_benchmark.core.construct import ColumnConstruct

construct = ColumnConstruct(
    name="action_agency",
    source_path="my_results.csv",
    proxy_col="proxy_agency",
    independent_col="independent_agency",
    mechanism="action-outcome loop",
)
result = construct.validate(root=".", n_bootstrap=10000)
print(result.r_with_ci)
```

## Design Rules

- Keep proxy measurements independent from behavioral tests.
- Report failures and negative correlations; they are diagnostic signal.
- Split constructs when a composite score fails validation.
- Use architecture-specific probes when generic probes are insensitive.
- Keep the claim boundary operational.
