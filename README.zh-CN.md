# Consciousness Benchmark / Mind Lab

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20372255.svg)](https://doi.org/10.5281/zenodo.20372255)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](pyproject.toml)

[English](README.md) | 中文

这个仓库包含论文和 benchmark 的代码与发布材料：

> **Measurement Validation Reveals Five Dissociable Operational Constructs Underlying Self-Model and Agency in Artificial Neural Architectures**

项目关注的是：如何用独立行为测试来验证人工系统中的内部 proxy 指标。论文中的结论只限于可操作化构念的测量效度，不声称系统具有主观体验、感受性或意识。

## 论文与材料

- Zenodo 记录：[10.5281/zenodo.20372255](https://doi.org/10.5281/zenodo.20372255)
- 主论文 PDF：[`docs/paper/submission/measurement_validation_submission.pdf`](docs/paper/submission/measurement_validation_submission.pdf)
- 补充材料 PDF：[`docs/paper/submission/measurement_validation_supplementary.pdf`](docs/paper/submission/measurement_validation_supplementary.pdf)
- 投稿包：[`docs/paper/measurement_validation_submission_package.zip`](docs/paper/measurement_validation_submission_package.zip)
- 发布审计：[`docs/paper/release_audit_20260522.md`](docs/paper/release_audit_20260522.md)
- 复现审计：[`docs/reproducibility_audit_20260522.md`](docs/reproducibility_audit_20260522.md)
- 常见问题：[`docs/FAQ.md`](docs/FAQ.md)

## 范围

当前版本包含五个参考构念：

- `action_agency`
- `boundary_self`
- `identity_temporal_self`
- `action_ownership`
- `distributed_body_schema_self`

仓库中的架构都是小型自定义模拟系统，用作受控测量测试平台。它们不是生产级语言模型，也不是通用 AI 系统。

## 仓库结构

- `consciousness_benchmark/`：benchmark 抽象、验证器、参考构念和 CLI。
- `mind_lab/`：论文使用的受控模拟系统。
- `scripts/`：统计、图表生成、诊断和在线 benchmark runner。
- `examples/`：最小示例。
- `docs/paper/statistics/final_20260521/`：主论文冻结统计。
- `docs/paper/statistics/reference_20260521/`：reference benchmark 使用的紧凑原始表。
- `docs/paper/statistics/transformer_20260522/`：minimal attention follow-up 诊断统计。
- `docs/paper/statistics/supplementary_20260522/`：补充稳健性检查。
- `docs/paper/figures/`：论文和补充材料图表。

大型原始运行目录没有放进公开发布包。公开版本保留了紧凑统计表和图表 manifest，用于追溯论文数字。

## 安装

```powershell
python -m pip install -e .
```

如果要运行 Mind Lab 在线实验，可以安装可选依赖：

```powershell
python -m pip install -e ".[mind-lab]"
```

## 复现参考报告

论文使用冻结统计。复现主表格不需要重新跑长实验。

```powershell
python -m consciousness_benchmark reference --bootstrap 10000 --seed 20260521
```

该命令会写出：

- [`docs/benchmark_reference_report_20260521.md`](docs/benchmark_reference_report_20260521.md)
- [`docs/benchmark_reference_report_20260521.csv`](docs/benchmark_reference_report_20260521.csv)

## 重新生成图表和投稿文件

```powershell
python scripts/generate_paper_figures_v2.py
python scripts/generate_transformer_figure6.py
python scripts/generate_supplementary_figures.py
python scripts/build_submission_package.py
```

## 运行一个小型在线 smoke test

```powershell
python -m consciousness_benchmark online --condition-sets thalamus --seeds 1 --warmup 32 --quick --bootstrap 500
```

## 冻结结果位置

主论文统计：

- [`construct_validation_stats.csv`](docs/paper/statistics/final_20260521/construct_validation_stats.csv)
- [`mechanism_effects.csv`](docs/paper/statistics/final_20260521/mechanism_effects.csv)
- [`distributed_control_correlations.csv`](docs/paper/statistics/final_20260521/distributed_control_correlations.csv)
- [`number_consistency.csv`](docs/paper/statistics/final_20260521/number_consistency.csv)

reference benchmark 输入：

- [`action_agency_raw.csv`](docs/paper/statistics/reference_20260521/action_agency_raw.csv)
- [`boundary_self_raw.csv`](docs/paper/statistics/reference_20260521/boundary_self_raw.csv)
- [`identity_temporal_self_raw.csv`](docs/paper/statistics/reference_20260521/identity_temporal_self_raw.csv)
- [`action_ownership_raw.csv`](docs/paper/statistics/reference_20260521/action_ownership_raw.csv)
- [`distributed_body_schema_self_raw.csv`](docs/paper/statistics/reference_20260521/distributed_body_schema_self_raw.csv)

补充稳健性检查：

- [`online_16seed_construct_validation_stats.csv`](docs/paper/statistics/supplementary_20260522/online_16seed_construct_validation_stats.csv)
- [`transformer_16seed_construct_validation_stats.csv`](docs/paper/statistics/supplementary_20260522/transformer_16seed_construct_validation_stats.csv)
- [`transformer_workspace_capacity_stats.csv`](docs/paper/statistics/supplementary_20260522/transformer_workspace_capacity_stats.csv)
- [`thalamus_workspace_capacity_stats.csv`](docs/paper/statistics/supplementary_20260522/thalamus_workspace_capacity_stats.csv)

## 引用

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

## 许可证

代码使用 Apache License 2.0。见 [`LICENSE`](LICENSE)。

Zenodo 上的预印本文件使用 CC BY 4.0。
