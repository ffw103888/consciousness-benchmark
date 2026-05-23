# Consciousness Benchmark Quickstart

This benchmark validates operational constructs by comparing internal proxy
measurements with independent behavioral probes. It is not a detector of
subjective consciousness.

## Install Locally

From the workspace root:

```powershell
python -m pip install -e .
```

## Reproduce Frozen Reference Statistics

```powershell
python -m consciousness_benchmark reference --bootstrap 10000
```

Equivalent console script:

```powershell
consciousness-benchmark reference --bootstrap 10000
```

Expected validated constructs:

| Construct | Mechanism |
|---|---|
| `action_agency` | action-outcome loop |
| `boundary_self` | workspace |
| `identity_temporal_self` | workspace |
| `action_ownership` | action-outcome loop |
| `distributed_body_schema_self` | meta-monitor |

## Check Architecture Applicability

Constructs are not assumed to transfer cleanly to every architecture. Reference
constructs include conservative metadata for where they are validated, where
measurement is limited, and where an architecture-specific variant is known.

```python
from consciousness_benchmark import reference_constructs

for construct in reference_constructs():
    print(
        construct.name,
        construct.applicable_to("thalamus"),
        construct.applicable_to("transformer"),
    )
```

For example, `boundary_self` is validated in the thalamus-inspired reference
system, but currently measurement-limited in the Transformer follow-up. The
Transformer mini-study instead found an exploratory
`predictive_agency_without_validated_boundary` profile.

## Run a Minimal Online Benchmark

```powershell
python -m consciousness_benchmark online --condition-sets thalamus --seeds 1 --warmup 32 --quick --bootstrap 500
```

Output is written under `runs/benchmark_online/<run_id>/`:

- `manifest.json`
- `progress.json`
- `online_benchmark_raw.csv`
- `online_benchmark_raw.partial.csv`
- `condition_summary.csv`
- `construct_validation_stats.csv`
- `mechanism_effects.csv`
- `control_correlations.csv`
- `report.md`

## Run Graded Meta-Monitor Controls

```powershell
python -m consciousness_benchmark online --condition-sets meta-strength --seeds 1 --warmup 24 --quick --bootstrap 500
python -m consciousness_benchmark online --condition-sets meta-noise --seeds 1 --warmup 16 --quick --bootstrap 200
python -m consciousness_benchmark online --condition-sets meta-delay --seeds 1 --warmup 16 --quick --bootstrap 200
```

Use larger `--seeds`, longer `--warmup`, and omit `--quick` for formal runs.

## Python API

```python
from pathlib import Path
from consciousness_benchmark import ConstructValidator

project_root = Path(".")
validator = ConstructValidator.from_reference()
report = validator.validate_all(root=project_root, n_bootstrap=10000)
print(report.summary_markdown())
```

## Claim Boundary

All reported constructs are operational measurements. They support claims about
proxy-test convergence and mechanism sensitivity, not claims of subjective
experience.

