# Supplementary Experiments, 2026-05-22

These runs extend the frozen primary manuscript results without replacing them. The primary paper statistics remain the frozen 2026-05-21 tables in `docs/paper/statistics/final_20260521/`. The runs below are intended for supplementary materials and reviewer-facing robustness checks.

## Run Inventory

| Run | Output directory | Purpose |
|---|---|---|
| 16-seed online benchmark | `runs/benchmark_online_supplementary/online_20260522_173251/` | Extended seeds across thalamus, distributed, and distributed meta-monitor controls |
| Transformer 16-seed 2x2 | `runs/supplementary/transformer_validation_20260522_173251/` | Extended Transformer mechanism and validation follow-up |
| Transformer workspace capacity | `runs/supplementary/transformer_workspace_capacity_20260522_173251/` | Capacity sweep for Transformer workspace-boundary diagnostics |
| Thalamus workspace capacity | `runs/supplementary/thalamus_workspace_capacity_20260522_173251/` | Capacity sweep for thalamus boundary and identity-temporal measures |

## Extended Online Benchmark

The 16-seed online benchmark completed `320/320` rows. It combines several condition sets, so it should be treated as a pooled robustness check rather than a direct replacement for Table 1 in the main manuscript.

| Construct | n | r [95% CI] | Status |
|---|---:|---:|---|
| Action agency | 320 | 0.727 [0.662, 0.781] | validated |
| Boundary self | 320 | 0.918 [0.894, 0.935] | validated |
| Identity-temporal self | 320 | 0.749 [0.656, 0.816] | validated |
| Action ownership | 320 | 0.987 [0.981, 0.990] | validated |
| Distributed body-schema self | 256 | 0.902 [0.877, 0.927] | validated |

Mechanism effects remained aligned with the main claims:

| Mechanism | Target | Mean difference [95% CI] |
|---|---|---:|
| workspace | Boundary self | +0.493 [0.482, 0.504] |
| workspace | Identity-temporal self | +0.246 [0.232, 0.260] |
| action loop | Action agency | +0.698 [0.695, 0.700] |
| action loop | Action ownership | +0.968 [0.968, 0.968] |

Distributed meta-monitor controls also remained orderly:

| Control | n | r [95% CI] |
|---|---:|---:|
| meta-monitor strength | 96 | 0.811 [0.766, 0.857] |
| meta-monitor noise | 64 | -0.906 [-0.943, -0.870] |
| meta-monitor delay | 64 | -0.420 [-0.611, -0.283] |

Interpretation: increasing seeds preserves the five-construct validation pattern in a pooled supplementary run. The pooled action-agency and identity-temporal correlations are lower than the frozen primary table because this run mixes additional control conditions and architectures.

## Transformer 16-Seed 2x2 Follow-Up

The Transformer 16-seed follow-up reinforces the main interpretation from the manuscript: action-loop mechanisms replicate, while Transformer self-model measurement remains architecture-limited.

| Construct | n | r [95% CI] | Status |
|---|---:|---:|---|
| Action agency | 64 | 0.999826 [0.999734, 0.999907] | validated, near ceiling |
| Boundary self | 64 | 0.489 [0.286, 0.674] | not validated |
| Identity-temporal self | 64 | 0.610 [0.444, 0.747] | exploratory |
| Action ownership | 64 | 0.999992 [0.999989, 0.999996] | validated, near ceiling |

Mechanism effects replicated:

| Factor | Target | Mean difference [95% CI] |
|---|---|---:|
| action loop | Action agency | +0.8190 [0.8182, 0.8198] |
| action loop | Action ownership | +0.8190 [0.8182, 0.8197] |
| workspace | Boundary self | +0.8357 [0.8287, 0.8426] |
| workspace | Identity-temporal self | +0.0483 [-0.0006, 0.0969] |

Interpretation: the Transformer system shows robust mechanism selectivity but does not support a strong operational boundary-self claim. Identity-temporal self should also remain exploratory in the Transformer substrate.

## Transformer Workspace Capacity Sweep

The Transformer capacity sweep tested capacities `0, 1, 2, 4, 8` with 16 seeds per capacity.

| Diagnostic | n | Pearson r [95% CI] | Spearman rho |
|---|---:|---:|---:|
| capacity vs boundary proxy | 80 | 0.494 [0.371, 0.596] | 0.203 |
| capacity vs generic boundary probe | 80 | -0.257 [-0.463, -0.034] | -0.078 |
| capacity vs hard attention boundary | 80 | 0.184 [-0.039, 0.386] | 0.251 |
| proxy vs generic boundary | 80 | 0.404 [0.208, 0.578] | 0.483 |
| proxy vs hard attention boundary | 80 | 0.252 [0.077, 0.435] | 0.360 |

Interpretation: workspace capacity moderately affects the Transformer internal boundary proxy, but the effect does not transfer to independent boundary probes. This supports the manuscript's measurement-limited interpretation for Transformer boundary self.

## Thalamus Workspace Capacity Sweep

The thalamus capacity sweep tested capacities `0, 1, 2, 4, 8` with 16 seeds per capacity.

| Diagnostic | n | Pearson r [95% CI] | Spearman rho |
|---|---:|---:|---:|
| capacity vs boundary proxy | 80 | 0.668 [0.588, 0.737] | 0.826 |
| capacity vs boundary independent | 80 | 0.391 [0.222, 0.535] | 0.343 |
| capacity vs identity proxy | 80 | 0.417 [0.262, 0.543] | 0.271 |
| capacity vs identity independent | 80 | 0.508 [0.395, 0.608] | 0.442 |
| boundary proxy vs independent | 80 | 0.838 [0.722, 0.910] | 0.325 |
| identity proxy vs independent | 80 | 0.982 [0.965, 0.992] | 0.629 |

Interpretation: thalamus workspace capacity shows graded effects, especially on the boundary proxy, while proxy-independent convergence remains strong for boundary and identity-temporal measures. This provides a useful supplementary dose-response check for the workspace mechanism.

## Recommended Use

Use these results in Supplementary Materials, not in the main manuscript tables. The main paper should continue to cite the frozen 2026-05-21 statistics. The strongest supplementary claims are:

1. Extended seeds preserve the five-construct validation pattern in pooled online benchmarking.
2. Thalamus workspace capacity provides dose-response support for workspace-linked self measures.
3. Transformer workspace capacity does not rescue boundary-self validation, reinforcing the architecture-limited measurement interpretation.
