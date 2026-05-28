# Consciousness Benchmark / Mind Lab

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20372255.svg)](https://doi.org/10.5281/zenodo.20372255)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](pyproject.toml)

English | [中文](README.zh-CN.md)

This repository contains the code and release materials for:

> **Measurement Validation Reveals Five Dissociable Operational Constructs Underlying Self-Model and Agency in Artificial Neural Architectures**

The project studies how internal proxy measures can be checked against independent behavioral probes in small, controlled artificial systems. The claims are about measurement validity for operational constructs. They are not claims about subjective experience, sentience, or consciousness in deployed AI systems.

## Paper And Materials

- Zenodo record: [10.5281/zenodo.20372255](https://doi.org/10.5281/zenodo.20372255)
- Main manuscript: [`docs/paper/submission/measurement_validation_submission.pdf`](docs/paper/submission/measurement_validation_submission.pdf)
- Supplementary materials: [`docs/paper/submission/measurement_validation_supplementary.pdf`](docs/paper/submission/measurement_validation_supplementary.pdf)
- Submission package: [`docs/paper/measurement_validation_submission_package.zip`](docs/paper/measurement_validation_submission_package.zip)
- Release audit: [`docs/paper/release_audit_20260522.md`](docs/paper/release_audit_20260522.md)
- Reproducibility audit: [`docs/reproducibility_audit_20260522.md`](docs/reproducibility_audit_20260522.md)
- FAQ: [`docs/FAQ.md`](docs/FAQ.md)

## Scope

The current release includes five reference constructs:

- `action_agency`
- `boundary_self`
- `identity_temporal_self`
- `action_ownership`
- `distributed_body_schema_self`

The architectures in this repository are small custom simulations used as controlled measurement testbeds. They are not production-scale language models or general-purpose AI systems.

## Repository Layout

- `consciousness_benchmark/`: benchmark abstractions, validators, reference constructs, and CLI.
- `mind_lab/`: controlled simulation systems used by the paper.
- `scripts/`: statistics, figure generation, diagnostics, and online benchmark runners.
- `examples/`: minimal examples for reference and online benchmark runs.
- `docs/paper/statistics/final_20260521/`: frozen primary statistics.
- `docs/paper/statistics/reference_20260521/`: compact raw tables used by the reference benchmark.
- `docs/paper/statistics/transformer_20260522/`: minimal attention follow-up diagnostics.
- `docs/paper/statistics/supplementary_20260522/`: supplementary robustness checks.
- `docs/paper/figures/`: paper and supplementary figures.

Large raw run directories are excluded from the public release. The compact statistics tables and figure manifests are kept for traceability.

## Installation

```powershell
python -m pip install -e .
```

Optional online Mind Lab runs use the optional dependency group:

```powershell
python -m pip install -e ".[mind-lab]"
```

## Reproduce The Reference Report

The paper reports frozen statistics. You do not need to rerun the long experiments to reproduce the main table.

```powershell
python -m consciousness_benchmark reference --bootstrap 10000 --seed 20260521
```

This writes:

- [`docs/benchmark_reference_report_20260521.md`](docs/benchmark_reference_report_20260521.md)
- [`docs/benchmark_reference_report_20260521.csv`](docs/benchmark_reference_report_20260521.csv)

## Regenerate Figures And Submission Files

```powershell
python scripts/generate_paper_figures_v2.py
python scripts/generate_transformer_figure6.py
python scripts/generate_supplementary_figures.py
python scripts/build_submission_package.py
```

## Run A Small Online Smoke Test

```powershell
python -m consciousness_benchmark online --condition-sets thalamus --seeds 1 --warmup 32 --quick --bootstrap 500
```

## Frozen Result Locations

Primary paper statistics:

- [`construct_validation_stats.csv`](docs/paper/statistics/final_20260521/construct_validation_stats.csv)
- [`mechanism_effects.csv`](docs/paper/statistics/final_20260521/mechanism_effects.csv)
- [`distributed_control_correlations.csv`](docs/paper/statistics/final_20260521/distributed_control_correlations.csv)
- [`number_consistency.csv`](docs/paper/statistics/final_20260521/number_consistency.csv)

Reference benchmark inputs:

- [`action_agency_raw.csv`](docs/paper/statistics/reference_20260521/action_agency_raw.csv)
- [`boundary_self_raw.csv`](docs/paper/statistics/reference_20260521/boundary_self_raw.csv)
- [`identity_temporal_self_raw.csv`](docs/paper/statistics/reference_20260521/identity_temporal_self_raw.csv)
- [`action_ownership_raw.csv`](docs/paper/statistics/reference_20260521/action_ownership_raw.csv)
- [`distributed_body_schema_self_raw.csv`](docs/paper/statistics/reference_20260521/distributed_body_schema_self_raw.csv)

Supplementary robustness checks:

- [`online_16seed_construct_validation_stats.csv`](docs/paper/statistics/supplementary_20260522/online_16seed_construct_validation_stats.csv)
- [`transformer_16seed_construct_validation_stats.csv`](docs/paper/statistics/supplementary_20260522/transformer_16seed_construct_validation_stats.csv)
- [`transformer_workspace_capacity_stats.csv`](docs/paper/statistics/supplementary_20260522/transformer_workspace_capacity_stats.csv)
- [`thalamus_workspace_capacity_stats.csv`](docs/paper/statistics/supplementary_20260522/thalamus_workspace_capacity_stats.csv)

## Citation

```bibtex
@misc{measurement_validation_constructs_2026,
  title = {Measurement Validation Reveals Five Dissociable Operational Constructs Underlying Self-Model and Agency in Artificial Neural Architectures},
  author = {Feng, Fuwang},
  year = {2026},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.20372255},
  url = {https://doi.org/10.5281/zenodo.20372255}
}
```

## License

Code is licensed under the Apache License 2.0. See [`LICENSE`](LICENSE).

The preprint files on Zenodo are distributed under CC BY 4.0.
