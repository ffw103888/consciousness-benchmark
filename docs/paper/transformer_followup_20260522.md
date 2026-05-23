# Transformer Follow-Up Diagnostics

Date: 2026-05-22

This note records the post-freeze Transformer-inspired validation run. It is not part of the 2026-05-21 frozen five-construct statistics. It is cross-architecture diagnostic evidence and should be cited conservatively.

## Files

- Main run: `runs/transformer_validation/transformer_validation_20260522_091959`
- High-correlation diagnostic: `runs/transformer_validation/transformer_high_corr_diagnostic_20260522_094603`
- Transformer-specific boundary probes: `runs/transformer_validation/transformer_specific_boundary_20260522_094656`

## Main 2x2 Result

The Transformer-inspired system crossed workspace availability and action-loop availability:

- `W-A-`
- `W+A-`
- `W-A+`
- `W+A+`

The main run used 8 seeds, 512 warmup steps, 128 probe steps, and 2,000 bootstrap resamples.

### Proxy-Test Convergence

| Construct | r | 95% CI | Status |
|---|---:|---:|---|
| Action agency | 0.9998 | [0.9997, 0.9999] | suspiciously high |
| Action ownership | 0.99999 | [0.99999, 0.999998] | suspiciously high |
| Identity-temporal self | 0.802 | [0.667, 0.896] | passes |
| Boundary self | 0.636 | [0.373, 0.842] | below threshold |

### Mechanism Effects

| Effect | Mean difference | p | Interpretation |
|---|---:|---:|---|
| action loop -> action agency | +0.819 | <1e-9 | strong selective effect |
| action loop -> action ownership | +0.819 | <1e-9 | strong selective effect |
| workspace -> boundary proxy | +0.830 | <1e-9 | strong internal-proxy effect |
| workspace -> action agency | ~0 | 1.000 | selective null |
| action loop -> boundary proxy | -0.005 | 0.976 | selective null |

## High-Correlation Diagnostic

The near-perfect agency and ownership correlations were stress-tested by varying action-effect noise and action-loop learning rate.

Key results:

| Subset | Diagnostic | r | Interpretation |
|---|---|---:|---|
| all diagnostic conditions | proxy agency vs independent agency | 0.795 | plausible but lower |
| all diagnostic conditions | proxy ownership vs independent ownership | 0.664 | below validation threshold |
| noise sweep | proxy agency vs independent agency | 0.991 | still dominated by prediction accuracy |
| learning-rate sweep | proxy agency vs independent agency | 0.266 | convergence collapses across learning axis |
| learning-rate sweep | proxy ownership vs independent ownership | -0.122 | not validated |

Interpretation: the clean 2x2 Transformer run inflated proxy-test correlations because both proxy and probe were driven by prediction accuracy under a low-noise task axis. The action-loop mechanism effect remains real, but the near-perfect validation statistic should not be treated as independent construct validation.

## Boundary-Self Diagnostic

The Transformer boundary result was tested with generic and attention-specific probes.

| Diagnostic | r | 95% CI | Status |
|---|---:|---:|---|
| proxy vs generic boundary probe | 0.325 | [-0.023, 0.620] | fails |
| proxy vs hard attention-boundary probe | 0.246 | [-0.023, 0.520] | fails |
| workspace dose vs hard attention-boundary probe | 0.223 | [-0.049, 0.514] | fails |
| workspace dose vs boundary proxy | 0.728 | [0.564, 0.845] | internal proxy responds |

Interpretation: workspace manipulations strongly affect the internal boundary proxy, but current behavior-level and attention-specific probes do not validate boundary self in the Transformer-inspired system. This is a measurement-limited or construct-architecture mismatch result, not a validated boundary-self replication.

## Conservative Claim

The Transformer follow-up supports:

- action-loop mechanisms generalize to an attention-based substrate as selective operational effects on agency/ownership-related processing;
- clean Transformer-like setups can inflate proxy-test convergence;
- boundary-self measurement does not automatically transfer to attention-only architectures.

The Transformer follow-up does not support:

- claiming perfect cross-architecture validation;
- claiming validated Transformer boundary self;
- treating near-perfect agency/ownership correlations as independent validation without diagnostics.
