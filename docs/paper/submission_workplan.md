# Submission Workplan

Draft v2 was updated after measurement-strengthening runs on 2026-05-21.

## Scope Notes

- The manuscript reports operational constructs, not subjective consciousness.
- Strong claims are limited to proxy-test convergence and controlled mechanism effects.
- Trajectory consistency and body ownership remain exploratory.
- Artificial-life results are retained as open-ended search context, not as primary validation evidence.

## Statistical Freeze

- Final statistics were frozen with 10,000 bootstrap resamples on 2026-05-21.
- Frozen tables and machine-readable outputs are in `docs/paper/statistics/final_20260521`.
- Number consistency against the v2 figure manifest passed for all key validation and mechanism values.
- A post-freeze Transformer follow-up was added on 2026-05-22 as cross-architecture diagnostic evidence. It is reported separately and is not folded into the frozen five-construct validation table.
- A second post-freeze Transformer mini-study tested architecture-conditioned construct variants. It is treated as exploratory Discussion material, not as a new validated construct.
- Current decision: retain the Transformer follow-up in the main text as Section 3.7 and Figure 6 because it directly supports the measurement-validation thesis. It remains explicitly post-freeze diagnostic evidence, not part of the frozen five-construct validation table.

## Figure Plan

- Figure 1: validation-first workflow. Shows the loop from theoretical construct, to operational proxy, to independent tests, to convergence check, and then either validated claim or diagnostic refinement.
- Figure 2: three diagnostic-refinement cycles. Shows the agency correction, the self-model decomposition, and the distributed architecture-specific probe refinement.
- Figure 3: five validated constructs. Shows proxy-test scatterplots for action agency, boundary self, identity-temporal self, action ownership, and distributed body-schema self.
- Figure 4: triple mechanism dissociation. Shows workspace effects, action-loop effects, and meta-monitor effects across validated constructs.
- Figure 5: distributed graded meta-monitor controls. Shows that distributed hard probes track meta-monitor strength and noise rather than a binary module switch.
- Figure 6: post-freeze Transformer diagnostics and high-agency / low-boundary profile. Shows stress-sensitive Transformer validation, boundary-self measurement failure, and the exploratory predictive-agency-without-validated-boundary profile.

Current figure directory: `docs/paper/figures/paper_v2_20260521`

Snapshot: `docs/paper/figure_snapshots/20260521_paper_v2`

## Table Plan

- Table 1: validation status of the five frozen constructs. Source: `docs/paper/statistics/final_20260521/table1_validation_status.md`.
- Table 2: mechanism effects for workspace, action-loop, and meta-monitor manipulations. Source: `docs/paper/statistics/final_20260521/table2_mechanism_effects.md`.
- Table 3: distributed graded controls. Source: `docs/paper/statistics/final_20260521/table3_distributed_controls.md`.
- Supplementary Table S1: raw paths, column names, and construct metadata for benchmark reproduction.
- Supplementary Table S2: post-freeze Transformer diagnostics, clearly labeled as non-frozen diagnostic evidence.

## Polish Checklist

- References have been converted from working notes to formal author-year entries. BibTeX source is in `docs/paper/references.bib`.
- Transformer follow-up is retained in the main text as diagnostic evidence. Keep Section 3.7 and Figure 6 scope-limited.
- Figure 6 remains in the main text for the current version. Current snapshot exists in `docs/paper/figure_snapshots/20260521_paper_v2`.
- Confirm that all main-table values come from `docs/paper/statistics/final_20260521`.
- Keep all post-freeze Transformer values labeled as diagnostic or exploratory unless re-frozen.
