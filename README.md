# Consciousness Benchmark / Mind Lab

Official implementation of **"Measurement Validation Reveals Five Dissociable Operational Constructs Underlying Self-Model and Agency in Artificial Neural Architectures."**

This repository contains the benchmark code, reference statistics, paper figures, and reproducibility scripts for an operational measurement-validation study of artificial systems.

Important boundary: this project validates **operational constructs** such as action agency, boundary self, identity-temporal self, action ownership, and distributed body-schema self. It is not a detector of subjective experience and should not be described as proof that a system is conscious.

## Paper

- Manuscript PDF: [`docs/paper/submission/measurement_validation_submission.pdf`](docs/paper/submission/measurement_validation_submission.pdf)
- Supplementary PDF: [`docs/paper/submission/measurement_validation_supplementary.pdf`](docs/paper/submission/measurement_validation_supplementary.pdf)
- Submission package: [`docs/paper/measurement_validation_submission_package.zip`](docs/paper/measurement_validation_submission_package.zip)
- Release audit: [`docs/paper/release_audit_20260522.md`](docs/paper/release_audit_20260522.md)
- Reproducibility audit: [`docs/reproducibility_audit_20260522.md`](docs/reproducibility_audit_20260522.md)
- Release dry-run checklist: [`docs/release_dry_run_checklist.md`](docs/release_dry_run_checklist.md)
- FAQ: [`docs/FAQ.md`](docs/FAQ.md)
- arXiv: forthcoming

## What Is Included

The current benchmark release includes five validated reference constructs:

- `action_agency`
- `boundary_self`
- `identity_temporal_self`
- `action_ownership`
- `distributed_body_schema_self`

The repository also includes:

- `consciousness_benchmark/`: benchmark abstractions, validators, reference constructs, and CLI.
- `mind_lab/`: thalamus-inspired, distributed, artificial-life, and Transformer-inspired experimental systems.
- `scripts/`: paper statistics, figure generation, diagnostics, and online benchmark runners.
- `docs/paper/statistics/final_20260521/`: frozen primary statistics for the paper.
- `docs/paper/statistics/reference_20260521/`: compact frozen raw tables used by the reference benchmark and figure scripts.
- `docs/paper/statistics/transformer_20260522/`: compact Transformer follow-up diagnostic statistics.
- `docs/paper/statistics/supplementary_20260522/`: supplementary 16-seed and workspace-capacity robustness statistics.
- `docs/paper/figures/paper_v2_20260521/`: final paper figures and manifest.
- `docs/paper/figures/supplementary_20260522/`: supplementary robustness figures.

Large raw run directories are intentionally excluded from the public release. The compact frozen statistics and figure manifests are preserved for traceability.

## Installation

```powershell
python -m pip install -e .
```

Optional Mind Lab online runs may require the optional dependencies:

```powershell
python -m pip install -e ".[mind-lab]"
```

## Reproducing the Paper Assets

The paper uses frozen statistics. You do not need to rerun the long experiments to reproduce the reported numbers.

Reproduce the benchmark reference report:

```powershell
python -m consciousness_benchmark reference --bootstrap 10000 --seed 20260521
```

Regenerate the frozen paper statistics:

```powershell
python scripts/finalize_statistics.py --bootstrap 10000 --seed 20260521 --out-dir docs/paper/statistics/final_20260521
```

Regenerate the paper figures and submission package:

```powershell
python scripts/generate_paper_figures_v2.py
python scripts/generate_transformer_figure6.py
python scripts/generate_supplementary_figures.py
python scripts/build_submission_package.py
```

Run a small online smoke benchmark against live Mind Lab systems:

```powershell
python -m consciousness_benchmark online --condition-sets thalamus --seeds 1 --warmup 32 --quick --bootstrap 500
```

## Frozen Result Locations

Primary paper statistics:

- [`construct_validation_stats.csv`](docs/paper/statistics/final_20260521/construct_validation_stats.csv)
- [`mechanism_effects.csv`](docs/paper/statistics/final_20260521/mechanism_effects.csv)
- [`distributed_control_correlations.csv`](docs/paper/statistics/final_20260521/distributed_control_correlations.csv)
- [`number_consistency.csv`](docs/paper/statistics/final_20260521/number_consistency.csv)

Transformer follow-up diagnostics:

- [`transformer_construct_validation_stats.csv`](docs/paper/statistics/transformer_20260522/transformer_construct_validation_stats.csv)
- [`transformer_mechanism_effects.csv`](docs/paper/statistics/transformer_20260522/transformer_mechanism_effects.csv)
- [`transformer_high_corr_stats.csv`](docs/paper/statistics/transformer_20260522/transformer_high_corr_stats.csv)
- [`transformer_specific_boundary_stats.csv`](docs/paper/statistics/transformer_20260522/transformer_specific_boundary_stats.csv)
- [`transformer_construct_variants_stats.csv`](docs/paper/statistics/transformer_20260522/transformer_construct_variants_stats.csv)

Supplementary robustness checks:

- [`online_16seed_construct_validation_stats.csv`](docs/paper/statistics/supplementary_20260522/online_16seed_construct_validation_stats.csv)
- [`online_16seed_mechanism_effects.csv`](docs/paper/statistics/supplementary_20260522/online_16seed_mechanism_effects.csv)
- [`transformer_16seed_construct_validation_stats.csv`](docs/paper/statistics/supplementary_20260522/transformer_16seed_construct_validation_stats.csv)
- [`transformer_workspace_capacity_stats.csv`](docs/paper/statistics/supplementary_20260522/transformer_workspace_capacity_stats.csv)
- [`thalamus_workspace_capacity_stats.csv`](docs/paper/statistics/supplementary_20260522/thalamus_workspace_capacity_stats.csv)

## Citation

Replace the author and arXiv fields after the preprint is public:

```bibtex
@misc{measurement_validation_constructs_2026,
  title = {Measurement Validation Reveals Five Dissociable Operational Constructs Underlying Self-Model and Agency in Artificial Neural Architectures},
  author = {Feng, Fuwang},
  year = {2026},
  eprint = {arXiv:XXXX.XXXXX},
  archivePrefix = {arXiv},
  primaryClass = {cs.AI},
  url = {https://arxiv.org/abs/XXXX.XXXXX}
}
```

## License

Code is released under the MIT License. See [`LICENSE`](LICENSE).
