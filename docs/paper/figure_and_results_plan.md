# Figure and Results Plan

## Paper Thesis

Measurement validation must precede mechanistic interpretation in artificial consciousness research.

Strong operational claims currently supported:

- Corrected action-agency proxy aligns with independent agency probes.
- Boundary/core self proxy aligns with independent boundary-self probes.

Exploratory or limited claims:

- Temporal self has moderate validation.
- Ownership self is weakly validated.
- Distributed self remains measurement-limited because current independent tests are not sensitive enough.

## Figure 1 - System and Measurement Workflow

Purpose:

Show the validation-first pipeline.

Panels:

A. Three architecture families:

- thalamus-inspired workspace/gating architecture
- distributed multi-agent architecture
- artificial-life QD archive

B. Measurement workflow:

proxy definition -> independent tests -> discrepancy diagnostics -> construct split -> bounded mechanistic claim

C. Claim-tier legend:

- validated
- exploratory
- measurement-limited

Source:

Create manually from architecture diagrams and validation workflow.

## Figure 2 - Agency Proxy Failure and Correction

Purpose:

Show the gating-agency confusion and its correction.

Panels:

A. Before correction:

- old thalamus agency proxy vs independent agency tests
- highlight negative correlation (`r=-0.86`)

B. Diagnostic:

- old proxy tracks gating coordination, not action-outcome causality

C. After correction:

- corrected agency proxy vs independent tests
- overall `r=0.874`
- thalamus `r=0.853`
- distributed `r=0.975`

Existing files:

- `runs/measurement_validation/diagnostics_20260521_094719`
- `runs/measurement_validation/diagnostics_20260521_095239`
- `runs/measurement_validation/validation_20260521_100404/measurement_validation_raw.csv`

Needed:

Generate a before/after two-panel scatter from old and corrected validation runs.

## Figure 3 - Action Agency Mechanism

Purpose:

Show that action-outcome mechanisms drive corrected agency.

Panels:

A. Thalamus 2x2:

- W-A-
- W+A-
- W-A+
- W+A+

B. Cross-architecture action feedback:

- thalamus feedback off/on
- distributed feedback off/on

C. Action-loop variants:

- none
- minimal
- learning
- full

Key numbers:

- action agency overall proxy-independent validation: `r=0.874`
- thalamus agency validation: `r=0.853`
- distributed agency validation: `r=0.975`

Existing files:

- `runs/mind_lab_night_20260520_182514/analysis/thalamus_factorial_timescale_20260520_212831`
- `runs/mind_lab_night_20260520_182514/analysis/thalamus_action_loop_variants_20260520_220912`
- `runs/mind_lab_night_20260520_182514/analysis/cross_architecture_feedback_20260520_222903`
- `runs/measurement_validation/validation_20260521_100404`

## Figure 4 - Self-Model Construct Split

Purpose:

Show that self-model is not a single validated construct.

Panels:

A. Self proxy vs independent overall:

- overall `r=0.701-0.705`

B. Subscale validation:

- boundary/core self `r=0.940`
- temporal proxy vs mirror `r=0.524`
- ownership proxy vs ownership attribution `r=0.411`
- identity/ownership aggregate `r=-0.135`

C. Condition-level bars:

- thalamus W-A-, W+A-, W-A+, W+A+
- distributed feedback off/on
- proxy boundary / independent boundary / ownership test

Existing files:

- `runs/measurement_validation/self_diagnostics_20260521_101259`
- `runs/measurement_validation/self_diagnostics_20260521_101259/self_proxy_independent_by_condition.png`
- `runs/measurement_validation/self_diagnostics_20260521_101259/self_proxy_vs_independent_scatter.png`

## Figure 5 - Distributed Self Measurement Limitation

Purpose:

Show that distributed self validation currently fails because independent tests have low sensitivity.

Panels:

A. Expanded distributed grid:

- agents_4
- agents_8_feedback_on
- agents_8_feedback_off
- agents_16
- no_coordination
- sparse/dense sensors
- shifted goal
- large world

B. Scatter:

- proxy boundary self vs independent core boundary
- temporal proxy vs mirror
- ownership proxy vs ownership attribution

C. Dynamic range plot:

- architecture_self_probe near saturation (`~0.98-1.00`)
- mirror near saturation
- boundary perturbation narrow band (`~0.46-0.50`)

Existing files:

- `runs/measurement_validation/distributed_self_validation_20260521_101511`
- `distributed_self_proxy_scatter.png`
- `distributed_self_conditions.png`

Key interpretation:

Do not claim distributed self absent. Claim current independent tests are insufficiently sensitive.

## Figure 6 - Long-Running ALife Context

Purpose:

Show that the broader research platform is running open-ended search, but do not rely on ALife for main validated claims.

Panels:

A. QD coverage over time

B. Best fitness over time

C. Current archive coverage and best individual

Current run:

- `runs/mind_lab_night_20260520_182514_extended_20260521_093355`
- current coverage around `14783 / 160000 = 9.24%`
- target `16000 / 160000 = 10%`

Use as context / future discovery platform, not as main measurement-validation evidence.

## Tables

### Table 1 - Proxy Validation Summary

Rows:

- corrected action agency
- boundary/core self
- temporal self
- ownership self
- distributed self expanded grid

Columns:

- proxy
- independent test target
- overall r
- architecture-specific r
- claim tier

### Table 2 - Construct Split

Rows:

- gating coordination
- action agency
- boundary/core self
- temporal self
- ownership self

Columns:

- original label
- corrected label
- operational definition
- validation status

### Table 3 - Limitations and Next Probes

Rows:

- distributed self
- temporal self
- ownership self
- ALife agency

Columns:

- current limitation
- observed symptom
- next probe

## Results Writing Order

1. Start with validation failure, not mechanism.
2. Use agency as the clean rescue case.
3. Use self-model as the construct-splitting case.
4. Use distributed self as the sensitivity-limitation case.
5. End with bounded mechanistic dissociation.

## Language Guardrails

Use:

- "operational agency"
- "action-agency proxy"
- "boundary/core self proxy"
- "independent behavior-level tests"
- "validated operational alignment"

Avoid:

- "the system is conscious"
- "the system has a self"
- "the system feels agency"
- "we detected consciousness"

