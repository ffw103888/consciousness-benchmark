# Measurement Validation Plan After First Batch

This plan supersedes the earlier "mechanism first" order.  The next phase should treat the current self-model and agency findings as promising operational signals, not as settled discoveries, until the measurement system survives independent validation.

## Revised Priority

1. Validate the measurement system.
2. Rule out alternative explanations.
3. Test generality across architectures.
4. Only then deepen mechanism dissection and cross-disciplinary interpretation.

## Priority 1: Measurement Hardening

### Self-Model Validation Tests

- Boundary perturbation test: detect an operational self-boundary, perturb inside/outside/control regions, and test whether recovery is selectively prioritized inside the boundary.
- Computational mirror test: present delayed copies of the system's own behavior alongside current behavior and measure self/non-self discrimination.
- Ownership attribution test: interleave self-generated actions with externally imposed actions and measure attribution accuracy.

Validation criterion: these behavior-level tests should correlate strongly with the existing `self_model` proxy.  If they do not, the proxy must be revised before further claims.

### Agency Validation Tests

- Intentional binding analogue: estimate whether action-result intervals are represented as shorter under self-generated action than under passive or externally imposed outcomes.
- Error attribution test: shuffle action-result mappings and measure whether the system detects the mismatch and adjusts behavior.
- Controllability preference test: offer controllable vs uncontrollable environments and measure preference after exploration.

Validation criterion: these independent tests should converge with the existing `agency` proxy and with action-prediction-error diagnostics.

### Blind Analysis Protocol

- Generate anonymized systems across workspace/action-loop/randomized parameter conditions.
- Export behavioral traces and visual summaries without architecture labels.
- Collect human or separate-model ratings for self-model and agency without revealing condition labels.
- Reveal labels only after scoring and compute agreement between blinded ratings, independent tests, and automated proxies.

Key point: this is the strongest response to the critique that "the metrics are self-defined and can measure whatever we want them to measure."

## Priority 2: Alternative Explanations

- Complexity-matched controls: compare workspace vs no-workspace and action-loop vs no-action-loop systems with matched parameter counts, connection counts, and approximate compute.
- Dose-response tests: sweep workspace capacity and prediction accuracy as continuous variables, checking for selective monotonic effects.
- Lesion and recovery tests: damage workspace or action-loop modules after baseline measurement, then restore them and test whether the predicted dimension selectively drops and recovers.

## Priority 3: Transformer Replication

- Implement a small Transformer-like architecture with optional global workspace and optional action-outcome loop.
- Run the same 2x2 design:
  - W-A-
  - W+A-
  - W-A+
  - W+A+
- The core criterion is not identical absolute scores, but the same selective pattern: workspace increases self-model proxies, action loops increase agency proxies.

## Reporting Rule

Any paper draft should frame the current results as:

- operational proxies,
- architecture-specific simulations,
- and candidate mechanisms.

The stronger language should wait until the independent tests and blind validation agree with the current automated metrics.
