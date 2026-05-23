# Measurement Strengthening Update

Date: 2026-05-21

This note records the first implementation pass after shifting the project from paper drafting back to measurement strengthening. All results below are from quick pilot runs and should be treated as validation-direction evidence, not final paper numbers.

## Implemented

### Reusable Probes

Added to `mind_lab/validation.py`:

- Temporal self:
  - `trajectory_consistency_probe`
  - `identity_marker_persistence_probe`
  - `transformed_mirror_test`
  - `temporal_binding_test`
  - `delayed_identity_recognition_test`

- Ownership self:
  - `action_attribution_proxy_test`
  - `body_ownership_proxy_test`
  - `forced_choice_ownership_test`
  - `ownership_illusion_resistance_test`

- Distributed self hard probes:
  - `distributed_meta_monitor_lesion_probe`
  - `distributed_hidden_agent_perturbation_probe`
  - `distributed_body_schema_update_probe`

### Architecture Support

Added `enable_meta_monitor` to `DistributedArchitecture`.

Default behavior is unchanged (`True`). When disabled, the distributed system records degraded meta-monitor snapshots, allowing hard probes to include a real negative control rather than relying only on feedback/coordination conditions.

### Batch Scripts

Added:

- `scripts/run_temporal_self_validation.py`
- `scripts/run_ownership_self_validation.py`
- `scripts/run_distributed_hard_probes.py`

Each script writes:

- raw CSV
- condition summary CSV
- correlation summary JSON
- Markdown report
- diagnostic figures

## 4-Seed Quick Pilot Results

### Temporal Self

Run:

- `runs/measurement_validation/temporal_self_20260521_104648`

Key correlations:

- existing temporal proxy vs old mirror: `r = 0.526`
- existing temporal proxy vs refined independent: `r = 0.694`
- marker persistence vs delayed identity recognition: `r = 0.971`
- candidate temporal proxy vs refined independent: `r = 0.806`
- candidate temporal proxy vs composite independent: `r = 0.829`

Architecture-specific:

- thalamus marker persistence vs delayed identity: `r = 1.000`
- distributed marker persistence vs delayed identity: `r = 0.999`
- trajectory consistency vs transformed mirror remained weak (`r approximately 0`)

Interpretation:

- The old temporal measure is improved but still borderline.
- The strongest temporal subconstruct is not generic trajectory smoothness. It is identity-marker persistence / delayed identity recognition.
- Temporal binding and transformed mirror are useful diagnostics, but should not be merged blindly into a single temporal-self score.

Claim status:

- Upgrade candidate: `identity persistence temporal self`.
- Keep exploratory: `trajectory consistency temporal self`.

### Ownership Self

Run:

- `runs/measurement_validation/ownership_self_20260521_104649`

Key correlations:

- existing ownership proxy vs old ownership test: `r = 0.298`
- existing ownership proxy vs refined independent: `r = 0.933`
- action-attribution proxy vs forced-choice ownership: `r = 0.990`
- candidate ownership proxy vs refined independent: `r = 0.990`
- body ownership proxy vs illusion resistance: `r = 0.084`

Architecture-specific:

- thalamus action-attribution proxy vs forced-choice: `r = 1.000`
- distributed action-attribution proxy vs forced-choice: `r = 0.997`

Important caveat:

- Within the action-enabled subset, correlations can flip negative because the scores are near-saturated and the dynamic range is tiny. Do not over-interpret within-action subset correlations from the quick pilot.

Interpretation:

- Ownership should be split into at least:
  - action ownership / action attribution
  - body ownership
- Action ownership is strongly validated by the new forced-choice and illusion-resistance tests.
- Body ownership is not validated by this pass and should remain exploratory.

Claim status:

- Upgrade candidate: `action ownership`.
- Keep exploratory: `body ownership`.

### Distributed Self Hard Probes

Run:

- `runs/measurement_validation/distributed_hard_probes_20260521_104649`

Key correlations:

- proxy self vs hard distributed self: `r = 0.941`
- boundary proxy vs hard distributed self: `r = 0.941`
- legacy proxy vs hard distributed self: `r = 0.957`
- generic architecture probe vs hard distributed self: `r = 1.000`
- boundary proxy vs meta-monitor lesion: `r = 0.939`
- boundary proxy vs hidden-agent perturbation: `r = 0.942`
- boundary proxy vs body-schema update: `r = 0.940`

Interpretation:

- Adding `meta_monitor_off` provided the missing negative control.
- Hard probes now recover distributed self sensitivity that generic tests previously missed.
- This is promising but may be partially driven by the strong meta-monitor on/off contrast. The next formal run should include subtler degradations, not only full meta-monitor removal.

Claim status:

- Upgrade candidate after formal replication: `distributed body-schema / meta-monitor self`.
- Guardrail: current hard-probe success is operational and may be contrast-driven.

## Current Measurement Map

Validated or near-validated:

- action agency: already validated from earlier correction
- boundary/core self: already validated from earlier diagnostics
- identity-persistence temporal self: quick pilot positive
- action ownership: quick pilot positive
- distributed body-schema/meta-monitor self: quick pilot positive with negative control

Still exploratory:

- trajectory consistency temporal self
- temporal binding as a standalone temporal-self measure
- body ownership
- distributed self without strong meta-monitor contrast

## Next Formal Runs

Recommended next commands:

```powershell
python scripts\run_temporal_self_validation.py --seeds 8 --warmup 220
python scripts\run_ownership_self_validation.py --seeds 8 --warmup 220
python scripts\run_distributed_hard_probes.py --seeds 6 --warmup 260
```

Suggested additions before final paper figures:

- Add subtler distributed negative controls:
  - noisy meta-monitor
  - delayed meta-monitor
  - partial agent masking
  - centroid-only meta-monitor

- Add non-saturated ownership tasks within action-enabled systems:
  - harder decoys
  - delayed outcomes
  - partial action-result mismatch

- Keep temporal self split:
  - identity persistence can be validated now
- trajectory smoothness should remain a separate, weaker construct

## Guardrail

These improvements strengthen measurement validity. They still do not justify claims about subjective consciousness, subjective ownership, or phenomenological time. The appropriate language remains:

- operational identity persistence
- operational action ownership
- distributed body-schema tracking
- proxy-test convergence
- construct refinement

## Formal Follow-Up Batch

Run after the 4-seed quick pilot:

```powershell
python scripts\run_temporal_self_validation.py --seeds 8 --warmup 220
python scripts\run_ownership_self_validation.py --seeds 8 --warmup 220
python scripts\run_distributed_hard_probes.py --seeds 6 --warmup 260
```

### Temporal Self Formal Results

Run:

- `runs/measurement_validation/temporal_self_20260521_104909`

Rows:

- 48 total rows.

Key correlations:

- existing proxy vs old mirror: `r = 0.553`
- existing proxy vs refined independent: `r = 0.737`
- trajectory consistency vs transformed mirror: `r = -0.378`
- marker persistence vs temporal binding: `r = -0.707`
- marker persistence vs delayed identity recognition: `r = 0.850`
- candidate proxy vs refined independent: `r = 0.552`
- candidate proxy vs composite independent: `r = 0.567`

Architecture-specific:

- thalamus marker persistence vs delayed identity: `r = 0.938`
- distributed marker persistence vs delayed identity: `r = 0.991`
- thalamus existing proxy vs refined independent: `r = 0.961`
- distributed existing proxy vs refined independent: `r = -0.286`

Interpretation:

- The refined temporal construct should not be an average of trajectory consistency and marker persistence.
- Identity-marker persistence is the validated temporal subconstruct.
- Trajectory consistency is not a valid temporal-self proxy in this batch; it is measuring something else, likely dynamical smoothness or robustness.
- Temporal binding is also not aligned with marker persistence and should remain a separate exploratory diagnostic.

Updated claim status:

- Stronger candidate: `identity-persistence temporal self`.
- Do not upgrade: generic `temporal self` composite.

### Ownership Self Formal Results

Run:

- `runs/measurement_validation/ownership_self_20260521_104909`

Rows:

- 48 total rows.

Key correlations:

- existing ownership proxy vs old ownership test: `r = 0.350`
- existing ownership proxy vs refined independent: `r = 0.824`
- action-attribution proxy vs forced-choice ownership: `r = 0.996`
- candidate ownership proxy vs refined independent: `r = 0.996`
- candidate ownership proxy vs composite independent: `r = 0.977`
- body ownership proxy vs illusion resistance: `r = -0.012`

Architecture-specific:

- thalamus action-attribution proxy vs forced-choice: `r = 1.000`
- distributed action-attribution proxy vs forced-choice: `r = 0.999`
- thalamus existing proxy vs refined independent: `r = 1.000`
- distributed existing proxy vs refined independent: `r = 0.990`

Interpretation:

- Action ownership / action attribution is now strongly validated.
- Body ownership remains unvalidated and should not be folded into ownership self.
- Within-action subset correlations remain unstable or negative because action-enabled systems have narrow, near-saturated ranges. Use full factorial contrast for the main validation claim.

Updated claim status:

- Stronger candidate: `action ownership`.
- Do not upgrade: `body ownership`.

### Distributed Hard-Probe Formal Results

Run:

- `runs/measurement_validation/distributed_hard_probes_20260521_104909`

Rows:

- 66 total rows.

Key correlations:

- proxy self vs hard distributed self: `r = 0.975`
- boundary proxy vs hard distributed self: `r = 0.975`
- legacy proxy vs hard distributed self: `r = 0.960`
- generic architecture probe vs hard distributed self: `r = 1.000`
- boundary proxy vs meta-monitor lesion: `r = 0.975`
- boundary proxy vs hidden-agent perturbation: `r = 0.976`
- boundary proxy vs body-schema update: `r = 0.974`

Interpretation:

- The hard probes recover strong distributed-self measurement sensitivity when a true `meta_monitor_off` negative control is included.
- This supports a distributed body-schema/meta-monitor self construct.
- However, the strongest contrast is still the meta-monitor on/off manipulation, so the next refinement should add partial or noisy meta-monitor degradations.

Updated claim status:

- Upgrade candidate: `distributed body-schema / meta-monitor self`, pending partial-degradation controls.

## Revised Measurement Claims After Formal Batch

Validated or ready for strong operational claims:

- action agency
- boundary/core self
- action ownership
- identity-persistence temporal self
- distributed body-schema/meta-monitor self with explicit meta-monitor controls

Still exploratory or measurement-limited:

- generic temporal self composite
- trajectory consistency
- temporal binding as a self construct
- body ownership
- distributed self without partial meta-monitor degradation controls

## Distributed Meta-Monitor Graded Controls

This batch addresses the main alternative explanation for distributed self validation: the earlier hard-probe result might have measured a binary meta-monitor on/off switch rather than a graded body-schema/meta-monitor construct.

Command:

```powershell
python scripts\run_distributed_meta_monitor_controls.py --seeds 4 --warmup 220
```

Run:

- `runs/measurement_validation/distributed_meta_monitor_controls_20260521_110459`

Rows:

- 52 total rows.

Key correlations:

- proxy self vs hard probes without lesion component: `r = 0.924`
- boundary proxy vs hard probes without lesion component: `r = 0.924`
- generic architecture probe vs hard probes without lesion component: `r = 0.895`
- meta-monitor strength vs proxy self: `r = 0.993`
- meta-monitor strength vs hard probes: `r = 0.887`
- meta-monitor strength vs hidden-agent probe: `r = 0.655`
- meta-monitor strength vs body-schema update: `r = 0.943`
- meta-monitor noise vs hard probes: `r = -0.974`
- meta-monitor delay vs hard probes: `r = -0.229`

Interpretation:

- The distributed self result is not only an on/off artifact. Meta-monitor strength produces a graded response in both proxy and hard-probe scores.
- Noise strongly degrades hard-probe performance, supporting the interpretation that the construct depends on accurate meta-monitoring.
- Delay has a weaker effect in the current setup; future work should use longer or task-dependent delays if temporal accuracy of the distributed body schema becomes a primary claim.

Updated claim status:

- Distributed body-schema/meta-monitor self is now stronger than before because it survives graded-control testing.
- It should still be described operationally: "distributed body-schema/meta-monitor self", not subjective selfhood.

## Updated Figures

Generated construct-validation figures:

- `docs/paper/figures/construct_validation_20260521/figure_construct_validation_grid.png`
- `docs/paper/figures/construct_validation_20260521/figure_distributed_meta_monitor_controls.png`

Snapshot copy:

- `docs/paper/figure_snapshots/20260521_measurement_strengthening`

Figure manifest:

- `docs/paper/figures/construct_validation_20260521/manifest.json`

Manifest correlations:

- Action agency: `r = 0.874`
- Boundary self: `r = 0.940`
- Identity-temporal self: `r = 0.850`
- Action ownership: `r = 0.996`
- Distributed body-schema self: `r = 0.924`
- Meta-monitor strength vs distributed hard probes: `r = 0.887`

## Statistical Freeze

Final v2 paper statistics were frozen with 10,000 bootstrap resamples.

Command:

```powershell
python scripts\finalize_statistics.py --bootstrap 10000
```

Output directory:

- `docs/paper/statistics/final_20260521`

Frozen validation statistics:

- Action agency: `r = 0.874`, 95% CI `[0.774, 0.943]`, `p = 2.4e-08`
- Boundary self: `r = 0.940`, 95% CI `[0.847, 0.994]`, `p < 1e-9`
- Identity-temporal self: `r = 0.850`, 95% CI `[0.755, 0.912]`, `p < 1e-9`
- Action ownership: `r = 0.996`, 95% CI `[0.994, 0.998]`, `p < 1e-9`
- Distributed body-schema self: `r = 0.924`, 95% CI `[0.881, 0.956]`, `p < 1e-9`

Frozen mechanism effects:

- Workspace -> boundary self: `+0.468`, 95% CI `[0.435, 0.496]`
- Workspace -> identity-temporal self: `+0.254`, 95% CI `[0.211, 0.286]`
- Workspace -> action agency: `-0.001`, 95% CI `[-0.006, 0.005]`
- Workspace -> action ownership: `+0.000`, 95% CI `[-0.000, 0.000]`
- Action loop -> action agency: `+0.711`, 95% CI `[0.706, 0.717]`
- Action loop -> action ownership: `+0.968`, 95% CI `[0.968, 0.968]`
- Action loop -> boundary self: `-0.045`, 95% CI `[-0.078, -0.016]`
- Action loop -> identity-temporal self: `+0.013`, 95% CI `[-0.020, 0.055]`

Number consistency:

- All tracked values match the v2 figure manifest within the `0.01` tolerance.
