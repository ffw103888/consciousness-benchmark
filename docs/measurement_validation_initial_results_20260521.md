# Measurement Validation Initial Results - 2026-05-21

## What Was Added

Executable measurement-validation infrastructure was added:

- `mind_lab/validation.py`
  - boundary perturbation test,
  - computational mirror test,
  - ownership attribution test,
  - intentional binding analogue,
  - error attribution test,
  - controllability preference test.
- `scripts/run_measurement_validation.py`
  - runs independent validation across thalamus/distributed conditions,
  - exports anonymized blind-rating files,
  - writes labels separately for post-rating reveal.
- `scripts/run_validation_controls.py`
  - first executable alternative-explanation controls:
    - workspace dose response,
    - action-loop dose response,
    - lesion/recovery,
    - approximate complexity proxy logging.

## Quick Validation Run

Output directory:

`runs/measurement_validation/validation_20260521_093954`

Configuration:

- quick mode,
- 2 seeds per condition,
- thalamus 2x2 conditions,
- distributed feedback on/off conditions.

Correlation between original proxies and independent tests:

- Overall self-model correlation: `r = -0.057`
- Overall agency correlation: `r = -0.098`
- Distributed self-model correlation: `r = 0.819`
- Distributed agency correlation: `r = 0.205`
- Thalamus self-model correlation: `r = 0.421`
- Thalamus agency correlation: `r = -0.860`

## Interpretation

This is a measurement warning, not a failure of the project.

The quick independent tests do not yet validate the original automated proxies.  In particular, thalamus agency is not supported by the first independent agency-test bundle; it moves in the opposite direction under this quick validation setup.

Therefore the current mechanism results should remain downgraded to:

> operational proxy evidence requiring independent validation.

They should not yet be described as validated evidence of self-model/agency dissociation.

## Control Run

Output directory:

`runs/measurement_validation/controls_20260521_094018`

Early signals:

- Workspace lesion reduced the original thalamus self-model proxy from about `0.668` to `0.342`, as expected.
- Action-loop lesion reduced the original thalamus agency proxy from about `0.532` to `0.120`, as expected.
- However, independent self/agency tests did not show clean matching drops in this quick control.

This reinforces the same conclusion: the original intervention logic is internally coherent, but independent behavioral validation is not yet aligned.

## Next Action

Before writing stronger claims, improve the independent tests themselves:

1. Make intentional binding less dependent on vector-size artifacts and more directly tied to action-result interval estimation.
2. Replace the current generic ownership test with architecture-specific forced-action probes.
3. Add saved behavioral traces/GIFs to blind exports, not only JSON summaries.
4. Increase seeds after test definitions stabilize.
5. Re-run correlations and require convergence before escalating claims.
