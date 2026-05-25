# Reproducibility Audit, 2026-05-22

This audit checked whether the public release can be installed and exercised from
a clean directory without access to the ignored `runs/` tree.

## Audit Environment

- Source workspace: repository root
- Clean audit copy: separate temporary clone/copy without `runs/`
- Python environment: fresh `.venv`
- Install command: `python -m pip install -e .`

## Commands Tested

```powershell
python -m pip install -e .
python examples\01_reference_quickstart.py
python -m consciousness_benchmark reference --bootstrap 100 --seed 20260521 --out docs\audit_reference_report.md
python examples\02_online_mind_lab_minimal.py
python scripts\generate_supplementary_figures.py
python scripts\generate_paper_figures_v2.py
python scripts\generate_transformer_figure6.py
python scripts\finalize_statistics.py --bootstrap 100 --seed 20260521 --out-dir docs\audit_final_stats
python scripts\build_submission_package.py
```

All commands passed after the fixes below.

## Issues Found and Fixed

1. The reference benchmark still depended on raw CSV files under ignored
   `runs/measurement_validation/...` directories. The frozen raw tables were
   copied into `docs/paper/statistics/reference_20260521/`, and the reference
   construct definitions now read from that preserved directory.

2. The supplementary figure script read the 16-seed online raw table from the
   ignored supplementary `runs/` directory. The raw table was copied to
   `docs/paper/statistics/supplementary_20260522/online_16seed_raw.csv`, and
   the figure script now uses that path.

3. The paper figure scripts used hidden `runs/` paths for frozen and
   Transformer diagnostic data. The required compact raw/stat tables were
   preserved under `docs/paper/statistics/reference_20260521/` and
   `docs/paper/statistics/transformer_20260522/`, and the public figure scripts
   now read from those locations.

4. The quickstart and online smoke examples needed `pandas.DataFrame.to_markdown`,
   which requires `tabulate`. The package metadata and requirements now include
   `tabulate`.

5. `scripts/finalize_statistics.py` writes LaTeX tables via pandas, which
   requires `jinja2` in recent pandas versions. The package metadata and
   requirements now include `jinja2`.

## Result

The public package can now reproduce the benchmark reference report, run a small
online smoke benchmark, regenerate paper and supplementary figures, regenerate
frozen statistics from preserved raw tables, and rebuild the submission package
without requiring local experimental run directories.
