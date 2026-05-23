# Self-Model Diagnostics - 2026-05-21

## What Changed

The validation suite now includes an `architecture_self_probe`:

- Thalamus systems are tested on functional workspace boundaries: admitted vs rejected information, workspace capacity maintenance, and gating consistency.
- Distributed systems are tested on body-schema tracking: centroid tracking, active-agent tracking, external boundary stability, and damage/recovery updates.

This complements the generic tests (`boundary_perturbation`, `computational_mirror`, `ownership_attribution`) without assuming that every architecture has the same kind of self-boundary.

## Latest Validation Run

Output:

- `runs/measurement_validation/validation_20260521_100404`
- `runs/measurement_validation/self_diagnostics_20260521_100306`
- `runs/measurement_validation/self_diagnostics_20260521_101259`
- `runs/measurement_validation/distributed_self_validation_20260521_101511`

Overall proxy-vs-independent correlations after adding the architecture-specific probe:

| Measure | Correlation |
| --- | ---: |
| Self-model overall | 0.705 |
| Agency overall | 0.874 |
| Thalamus self-model | 0.875 |
| Thalamus agency | 0.853 |
| Distributed self-model | 0.429 |
| Distributed agency | 0.975 |

Self-focused decomposition after explicit proxy split:

| Subscale | Overall correlation with self proxy |
| --- | ---: |
| Core/boundary self | 0.940 |
| Temporal proxy vs mirror | 0.524 |
| Ownership proxy vs ownership test | 0.411 |
| Identity/ownership aggregate | -0.135 |

## Interpretation

The self-model problem is not the same as the agency problem.

For agency, the prior proxy was conceptually wrong: it mixed information gating with action-outcome causality. After splitting those constructs, the corrected action-agency proxy aligned strongly with independent tests.

For self-model, the core/boundary construct is now much better aligned. The `core/boundary self` subscale correlates strongly with the proxy (`r=0.919` overall), and thalamus-specific self validation is strong (`r=0.881` to `0.885`, depending on aggregate).

The remaining failure is `identity/ownership`. That subscale does not behave like the current self proxy and should not be averaged into the primary self-model score. It is better treated as a bridge construct between self-model and agency, or as a separate dimension requiring its own validation.

Distributed self-model still needs a richer validation design. In the current quick run, `architecture_self_probe` and `computational_mirror` are nearly saturated for distributed systems, while feedback changes ownership-like behavior. With only `feedback_off` and `feedback_on`, within-architecture correlation is unstable and should not be overinterpreted.

The expanded distributed grid confirmed that this is not only a two-condition artifact. Across `num_agents`, sensor radius, coordination on/off, and shifted goals, distributed self correlations remained weak:

| Distributed validation pair | Correlation |
| --- | ---: |
| self proxy vs independent self | 0.166 |
| boundary proxy vs core/boundary tests | 0.124 |
| temporal proxy vs mirror | -0.070 |
| ownership proxy vs ownership test | -0.097 |
| agency proxy vs independent agency | 0.270 |

Inspection shows that the current distributed independent tests have low discriminative range:

- `architecture_self_probe` is almost saturated around `0.98-1.00`.
- `computational_mirror` is also saturated near `1.00`.
- `boundary_perturbation` stays in a narrow `0.46-0.50` band.

So the next distributed step is not another proxy tweak. The independent tests themselves need harder probes:

- meta-monitor lesion: degrade or delay centroid and active-agent access
- coordination lesion: compare conflict resolution loss against body-schema tracking
- hidden-agent perturbation: move or disable agents without updating the meta layer
- delayed body-schema update: introduce lag and test whether self metrics detect it

## Writing Guardrail

Current mechanism results should be described as:

> operational proxy evidence, validated against independent behavior-level probes where available.

Avoid claims like:

> the system has self-awareness or agency.

Safer claim:

> workspace/body-boundary mechanisms align with core self-model proxies, while action-outcome loops align with corrected agency proxies. Identity/ownership remains a separate unresolved construct.

## Next Experiments

1. Expand distributed self validation beyond the two feedback conditions:
   - vary `num_agents`
   - vary `global_goal`
   - perturb meta-monitor access
   - lesion coordination signals

2. Report self-model as two subscales:
   - `core_boundary_self`
   - `identity_ownership_self`

3. Run dose-response controls on `core_boundary_self`:
   - workspace capacity for thalamus
   - active-agent/body-schema perturbation strength for distributed

4. Keep ownership out of the primary self-model aggregate until it has a clean construct definition.

5. For distributed systems, prioritize harder independent tests over more conditions. The current tests are too easy/saturated to validate or falsify the proxy.
