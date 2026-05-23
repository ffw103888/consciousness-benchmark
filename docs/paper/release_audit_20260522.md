# Release Audit - 2026-05-22

Scope: format and traceability check only. No experiments were rerun.

## Frozen Statistics

Source directory: `docs/paper/statistics/final_20260521/`
Bootstrap: 10,000 paired resamples. Seed: `20260521`.

### Table 1 / Five Construct Validation

| Construct | n | Manuscript display | Source row | Status |
|---|---:|---|---|---|
| Action agency | 24 | r=0.874 [0.774, 0.943], p=2.4e-08 | `construct_validation_stats.csv::action_agency` | traced |
| Boundary self | 24 | r=0.940 [0.847, 0.994], p=<1e-9 | `construct_validation_stats.csv::boundary_self` | traced |
| Identity-temporal self | 48 | r=0.850 [0.755, 0.912], p=<1e-9 | `construct_validation_stats.csv::identity_temporal_self` | traced |
| Action ownership | 48 | r=0.996 [0.994, 0.998], p=<1e-9 | `construct_validation_stats.csv::action_ownership` | traced |
| Distributed body-schema self | 52 | r=0.924 [0.881, 0.956], p=<1e-9 | `construct_validation_stats.csv::distributed_body_schema_self` | traced |

### Mechanism Effects

| Effect | Target | Manuscript display | Source row | Status |
|---|---|---|---|---|
| workspace | Boundary self | mean diff=+0.4679 [+0.4347, +0.4963], p=2.4e-07 | `mechanism_effects.csv::workspace_effect_boundary_self` | traced |
| action_loop | Boundary self | mean diff=-0.0453 [-0.0781, -0.0157], p=0.7266 | `mechanism_effects.csv::action_effect_boundary_self` | traced |
| workspace | Identity-temporal self | mean diff=+0.2535 [+0.2113, +0.2859], p=2.1e-09 | `mechanism_effects.csv::workspace_effect_identity_temporal_self` | traced |
| action_loop | Identity-temporal self | mean diff=+0.0131 [-0.0201, +0.0546], p=0.7971 | `mechanism_effects.csv::action_effect_identity_temporal_self` | traced |
| workspace | Action agency | mean diff=-0.0011 [-0.0062, +0.0049], p=0.9956 | `mechanism_effects.csv::workspace_effect_action_agency` | traced |
| action_loop | Action agency | mean diff=+0.7113 [+0.7064, +0.7173], p=<1e-9 | `mechanism_effects.csv::action_effect_action_agency` | traced |
| workspace | Action ownership | mean diff=+0.0001 [-0.0002, +0.0004], p=0.9997 | `mechanism_effects.csv::workspace_effect_action_ownership` | traced |
| action_loop | Action ownership | mean diff=+0.9680 [+0.9678, +0.9683], p=<1e-9 | `mechanism_effects.csv::action_effect_action_ownership` | traced |

### Distributed Graded Controls

| Control | Manuscript display | Source row | Status |
|---|---|---|---|
| strength | r=0.887 [0.846, 0.945], p=7.9e-09 | `distributed_control_correlations.csv::meta_monitor_strength` | traced |
| noise | r=-0.974 [-0.992, -0.952], p=9.0e-08 | `distributed_control_correlations.csv::meta_monitor_noise` | traced |

### Number Consistency File

`number_consistency.csv`: PASS (15/15 checks true).

## Figure Traceability

| Figure | File | Exists | Bytes | Manifest |
|---|---|---:|---:|---:|
| Figure 1 | `figure1_validation_framework_v2.png` | True | 219403 | yes |
| Figure 2 | `figure2_diagnostic_refinement_cycles.png` | True | 613609 | yes |
| Figure 3 | `figure3_five_construct_validation.png` | True | 393018 | yes |
| Figure 4 | `figure4_triple_dissociation.png` | True | 268117 | yes |
| Figure 5 | `figure5_distributed_graded_controls.png` | True | 161821 | yes |
| Figure 6 | `figure6_transformer_diagnostics.png` | True | 311344 | yes |

Manifest: `docs/paper/figures/paper_v2_20260521/manifest.json`.

## Transformer Diagnostic Traceability

Transformer diagnostics are post-hoc generalization tests and are not part of the primary five-construct frozen table.

| Manuscript item | Display | Source | Status |
|---|---|---|---|
| clean Transformer Action agency convergence | n=32, r=0.999825 [0.999677, 0.999947] | `docs/paper/statistics/transformer_20260522/transformer_construct_validation_stats.csv::action_agency` | traced |
| clean Transformer Action ownership convergence | n=32, r=0.999995 [0.999990, 0.999999] | `docs/paper/statistics/transformer_20260522/transformer_construct_validation_stats.csv::action_ownership` | traced |
| Transformer mechanism effect action_loop_effect_action_agency | mean diff=+0.8189 [+0.8180, +0.8198], p=<1e-9 | `docs/paper/statistics/transformer_20260522/transformer_mechanism_effects.csv::action_loop_effect_action_agency` | traced |
| Transformer mechanism effect action_loop_effect_action_ownership | mean diff=+0.8189 [+0.8180, +0.8198], p=<1e-9 | `docs/paper/statistics/transformer_20260522/transformer_mechanism_effects.csv::action_loop_effect_action_ownership` | traced |
| Transformer mechanism effect action_loop_effect_boundary_self | mean diff=-0.0046 [-0.3087, +0.2585], p=0.9760 | `docs/paper/statistics/transformer_20260522/transformer_mechanism_effects.csv::action_loop_effect_boundary_self` | traced |
| Transformer mechanism effect workspace_effect_boundary_self | mean diff=+0.8296 [+0.8207, +0.8377], p=<1e-9 | `docs/paper/statistics/transformer_20260522/transformer_mechanism_effects.csv::workspace_effect_boundary_self` | traced |
| Transformer mechanism effect workspace_effect_action_agency | mean diff=+0.0000 [-0.3066, +0.2564], p=1.0000 | `docs/paper/statistics/transformer_20260522/transformer_mechanism_effects.csv::workspace_effect_action_agency` | traced |
| Transformer high-correlation diagnostic all/proxy_agency_vs_independent | n=104, r=0.795 [0.762, 0.836] | `docs/paper/statistics/transformer_20260522/transformer_high_corr_stats.csv` | traced |
| Transformer high-correlation diagnostic all/proxy_ownership_vs_independent | n=104, r=0.664 [0.589, 0.739] | `docs/paper/statistics/transformer_20260522/transformer_high_corr_stats.csv` | traced |
| Transformer high-correlation diagnostic noise_sweep/proxy_agency_vs_independent | n=48, r=0.991 [0.986, 0.994] | `docs/paper/statistics/transformer_20260522/transformer_high_corr_stats.csv` | traced |
| Transformer high-correlation diagnostic learning_sweep/proxy_agency_vs_independent | n=40, r=0.266 [0.030, 0.516] | `docs/paper/statistics/transformer_20260522/transformer_high_corr_stats.csv` | traced |
| Transformer high-correlation diagnostic learning_sweep/proxy_ownership_vs_independent | n=40, r=-0.122 [-0.442, 0.225] | `docs/paper/statistics/transformer_20260522/transformer_high_corr_stats.csv` | traced |
| Transformer boundary diagnostic dose_vs_proxy_boundary | n=40, r=0.728 [0.564, 0.845] | `docs/paper/statistics/transformer_20260522/transformer_specific_boundary_stats.csv` | traced |
| Transformer boundary diagnostic proxy_vs_generic_boundary | n=40, r=0.325 [-0.023, 0.620] | `docs/paper/statistics/transformer_20260522/transformer_specific_boundary_stats.csv` | traced |
| Transformer boundary diagnostic proxy_vs_hard_attention_boundary | n=40, r=0.246 [-0.023, 0.520] | `docs/paper/statistics/transformer_20260522/transformer_specific_boundary_stats.csv` | traced |
| Transformer boundary diagnostic dose_vs_hard_attention_boundary | n=40, r=0.223 [-0.049, 0.514] | `docs/paper/statistics/transformer_20260522/transformer_specific_boundary_stats.csv` | traced |
| Transformer variant attention_focus_self | n=40, r=0.203 [-0.172, 0.547] | `docs/paper/statistics/transformer_20260522/transformer_construct_variants_stats.csv` | traced |
| Transformer variant context_window_self | n=40, r=0.152 [-0.172, 0.445] | `docs/paper/statistics/transformer_20260522/transformer_construct_variants_stats.csv` | traced |
| Transformer context-window dose signal | n=40, r=0.341 [0.101, 0.566] | `docs/paper/statistics/transformer_20260522/transformer_construct_variants_stats.csv` | traced |
| High-agency/low-boundary proxy_agency vs independent_agency | n=96, r=0.995 [0.993, 0.996] | `docs/paper/statistics/transformer_20260522/transformer_construct_variants_stats.csv` | traced |
| High-agency/low-boundary proxy_boundary_self vs independent_boundary_self | n=96, r=0.474 [0.329, 0.601] | `docs/paper/statistics/transformer_20260522/transformer_construct_variants_stats.csv` | traced |
| High-agency/low-boundary independent_agency vs independent_boundary_self | n=96, r=0.129 [-0.055, 0.292] | `docs/paper/statistics/transformer_20260522/transformer_construct_variants_stats.csv` | traced |
| High-agency/low-boundary row count | 36/96 = 37.5% | `docs/paper/statistics/transformer_20260522/transformer_construct_variants_summary.csv` and figure manifest | traced |

## Reference and Figure File Checks

- `references.bib` entries: 16.
- Manuscript References entries: 16.
- All BibTeX titles match manuscript References.
- All BibTeX first-author tokens appear in the manuscript body.
- Figure 1-6 files exist and are listed in the manifest.

## Supplementary Materials

Supplementary materials were added after the primary manuscript freeze and do not replace the frozen 2026-05-21 statistics.

| Item | File | Status |
|---|---|---|
| Supplementary manuscript | `docs/paper/submission/measurement_validation_supplementary.pdf` | generated |
| Supplementary source | `docs/paper/supplementary_materials.md` | generated |
| Supplementary Figure S1 | `docs/paper/figures/supplementary_20260522/figureS1_extended_16seed_validation.png` | generated |
| Supplementary Figure S2 | `docs/paper/figures/supplementary_20260522/figureS2_workspace_capacity_sweeps.png` | generated |
| Supplementary statistics | `docs/paper/statistics/supplementary_20260522/` | preserved |

Supplementary highlights:

- 16-seed pooled online benchmark: all five constructs remain above the validation threshold.
- Transformer 16-seed follow-up: action-loop mechanisms replicate; boundary self remains measurement-limited.
- Workspace capacity sweeps: thalamus retains proxy-independent convergence, while Transformer boundary probes remain limited.

## Reproducibility Audit

A clean-copy reproducibility audit was completed after release packaging. The
audit installed the package into a fresh virtual environment and ran the public
quickstart, reference benchmark, online smoke benchmark, paper figure scripts,
supplementary figure script, frozen-statistics script, and submission-package
builder without access to the ignored `runs/` tree.

Audit note: `docs/reproducibility_audit_20260522.md`.
