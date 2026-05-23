# Consciousness Benchmark MVP Progress

Date: 2026-05-21

## Scope

This document records the first infrastructure step after the measurement-validation paper materials: a minimal benchmark layer that can reproduce frozen reference statistics and begin online validation against `mind_lab` systems.

## Implemented

New package:

- `consciousness_benchmark`

Core modules:

- `consciousness_benchmark/core/stats.py`
- `consciousness_benchmark/core/construct.py`
- `consciousness_benchmark/core/validator.py`

Reference constructs:

- `action_agency`
- `boundary_self`
- `identity_temporal_self`
- `action_ownership`
- `distributed_body_schema_self`

Adapters:

- `SystemAdapter` protocol
- `MindLabAdapter`
- reference condition builders for thalamus and distributed systems

Scripts:

- `scripts/benchmark_reference_report.py`
- `scripts/benchmark_mind_lab_smoke.py`
- `scripts/benchmark_online_runner.py`

Dependency update:

- Added `pandas` to `requirements.txt` because benchmark reporting now depends on DataFrame output.

Packaging and public entry points:

- `pyproject.toml`
- `LICENSE`
- `consciousness_benchmark/cli.py`
- `consciousness_benchmark/__main__.py`
- console script: `consciousness-benchmark`

Documentation and examples:

- `README.md`
- `docs/index.md`
- `docs/quickstart.md`
- `docs/api.md`
- `docs/tutorial_custom_adapter.md`
- `examples/01_reference_quickstart.py`
- `examples/02_online_mind_lab_minimal.py`

## Offline Reference Report

Command:

```powershell
python scripts\benchmark_reference_report.py --bootstrap 10000
```

Output:

- `docs/benchmark_reference_report_20260521.md`
- `docs/benchmark_reference_report_20260521.csv`

Results:

| Construct | n | r (95% CI) | Status |
|---|---:|---:|---|
| action_agency | 24 | 0.874 [0.774, 0.943] | validated |
| boundary_self | 24 | 0.940 [0.846, 0.994] | validated |
| identity_temporal_self | 48 | 0.850 [0.754, 0.912] | validated subconstruct |
| action_ownership | 48 | 0.996 [0.994, 0.998] | validated subconstruct |
| distributed_body_schema_self | 52 | 0.924 [0.881, 0.955] | validated with graded controls |

## Online MindLab Adapter Smoke Test

Command:

```powershell
python scripts\benchmark_mind_lab_smoke.py --seeds 1 --warmup 48
```

Output:

- `runs/benchmark_mvp/mind_lab_smoke_20260521_134329`

Rows:

- 9 online condition rows

Smoke correlations:

- action_agency: `r = 0.690`
- boundary_self: `r = 0.927`
- identity_temporal_self: `r = 0.936`
- action_ownership: `r = 0.971`
- distributed_body_schema_self: `r = 0.997`

Interpretation:

- This is a plumbing smoke test, not a formal statistical batch.
- It verifies that the benchmark layer can instantiate live `mind_lab` systems, run warmup, execute independent probes, and produce the same column schema used by the frozen reference constructs.
- The lower action-agency smoke correlation is expected with only one seed and quick probes; formal validation remains the frozen reference dataset.

## Formal Online Benchmark Runner

The smoke runner has been upgraded into a formal online runner that supports:

- selectable condition sets: `thalamus`, `distributed`, `meta-strength`, `meta-noise`, `meta-delay`, or `all`
- configurable seeds per condition
- configurable warmup steps and quick/full probe mode
- frozen bootstrap statistics
- per-run `manifest.json`
- incremental `online_benchmark_raw.partial.csv` and `progress.json`
- final raw data, condition summaries, construct validation statistics, mechanism effects, control correlations, and a Markdown report

Example commands:

```powershell
python scripts\benchmark_online_runner.py --condition-sets thalamus --seeds 1 --warmup 32 --quick --bootstrap 500
python scripts\benchmark_online_runner.py --condition-sets meta-strength --seeds 1 --warmup 24 --quick --bootstrap 500
python scripts\benchmark_online_runner.py --condition-sets meta-noise --seeds 1 --warmup 16 --quick --bootstrap 200
python scripts\benchmark_online_runner.py --condition-sets meta-delay --seeds 1 --warmup 16 --quick --bootstrap 200
```

Verified runs:

| Run | Condition sets | Rows | Key check |
|---|---:|---:|---|
| `runs/benchmark_online/online_20260521_135629` | `thalamus` | 4 | workspace/action-loop mechanism effects frozen |
| `runs/benchmark_online/online_20260521_135655` | `meta-strength` | 6 | strength vs hard probes `r = 0.809` |
| `runs/benchmark_online/online_20260521_135829` | `meta-noise` | 4 | noise vs hard probes `r = -0.973` |
| `runs/benchmark_online/online_20260521_135945` | `meta-delay` | 4 | delay vs hard probes `r = -0.776` |

Each run directory contains:

- `manifest.json`
- `progress.json`
- `online_benchmark_raw.csv`
- `online_benchmark_raw.partial.csv`
- `condition_summary.csv`
- `construct_validation_stats.csv`
- `mechanism_effects.csv`
- `control_correlations.csv`
- `report.md`

Interpretation:

- The online runner is now suitable for formal benchmark batches.
- The small runs above are engineering verification runs, not final paper statistics.
- Control correlations are filtered by `condition_set`, so strength/noise/delay statistics do not contaminate each other.

## Install and CLI Verification

Local editable install:

```powershell
python -m pip install -e .
```

Verified commands:

```powershell
python -m consciousness_benchmark reference --bootstrap 200 --out runs\benchmark_mvp\cli_reference_test.md
python -m consciousness_benchmark online --condition-sets thalamus --seeds 1 --warmup 8 --quick --bootstrap 100 --output-root runs\benchmark_online_cli_test
consciousness-benchmark reference --bootstrap 100 --out runs\benchmark_mvp\console_reference_test.md
python examples\01_reference_quickstart.py
```

Outputs:

- `runs/benchmark_mvp/cli_reference_test.md`
- `runs/benchmark_mvp/cli_reference_test.csv`
- `runs/benchmark_mvp/console_reference_test.md`
- `runs/benchmark_mvp/console_reference_test.csv`
- `runs/benchmark_online_cli_test/online_20260521_141912`

## Next Engineering Steps

1. Split smoke tests from formal validation tests in CI.
2. Add `MindLabAdapter` unit tests using very small warmup/quick probes.
3. Move repeated probe-row logic from scripts into reusable benchmark reporting utilities.
4. Add resume support for interrupted online runs.
5. Add a small GitHub Pages or MkDocs site around `docs/index.md`.

## Claim Boundary

The benchmark remains an operational construct-validation toolkit. It is not a consciousness detector and should not be presented as measuring subjective experience.
