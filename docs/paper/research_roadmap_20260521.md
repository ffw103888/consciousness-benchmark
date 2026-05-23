# Research Roadmap: From Current Results to Publication

Last updated: 2026-05-21

## Current Stance

The current paper draft and figures are preserved, but publication is not urgent. The priority is to strengthen measurement validity before making stronger mechanistic or consciousness-related claims.

Mechanistic results are retained as operational proxy evidence. Claims should be upgraded only after independent measurements converge with the relevant proxies.

## Current Evidence Status

### Ready for Strong Claims

- Action agency validation:
  - Corrected action-agency proxy vs independent tests: r approximately 0.87.
  - The earlier negative correlation was explained by a gating-agency confusion.
  - Action-outcome loops can be treated as a validated mechanism for operational action agency.

- Boundary/core self validation:
  - Boundary self proxy vs independent boundary/core tests: r approximately 0.94.
  - Workspace mechanisms can be treated as a validated mechanism for operational boundary self.

- Double dissociation:
  - Workspace mechanisms primarily affect boundary/core self.
  - Action-outcome loops primarily affect action agency.
  - This is currently the strongest publishable substantive result.

### Needs Strengthening Before Strong Claims

- Temporal self:
  - Current validation is moderate, r approximately 0.52.
  - Needs diagnostic decomposition and improved tests.

- Ownership self:
  - Current validation is weak, r approximately 0.41.
  - Needs decomposition into action attribution and body ownership style probes.

- Distributed self:
  - Current general tests are insensitive, r approximately 0.17 in expanded distributed validation.
  - Needs architecture-specific probes rather than generic self tests.

### Optional / Contextual

- ALife long run:
  - Current target is 10% QD coverage.
  - This is useful as context and future discovery material, but not required for the core measurement-validation paper.

- Additional architectures and neuroscience comparisons:
  - Useful for later scope expansion.
  - Not required before the next measurement-validity milestone.

## Phase 1: Consolidate Core Measurement Validity

Estimated duration: 2-3 weeks.

Goal: bring all constructs that will receive strong claims to proxy-test convergence above r = 0.7, or explicitly mark them as exploratory.

### Week 1: Temporal Self

Questions:

- Is the current temporal proxy measuring state stability, trajectory consistency, memory coherence, or identity persistence?
- Is the current mirror-style test too dependent on explicit time perception?
- Do different architectures instantiate temporal self differently?

Tasks:

- Run temporal self diagnostics with intermediate variables:
  - state stability
  - trajectory consistency
  - memory coherence
  - identity persistence
  - temporal binding

- Implement improved temporal proxies:
  - trajectory consistency proxy
  - identity persistence proxy

- Implement improved independent tests:
  - transformed-behavior mirror test
  - temporal binding / event ordering test

Acceptance criteria:

- At least one temporal self subconstruct reaches r > 0.7 against an independent test.
- If no subconstruct reaches r > 0.7, temporal self remains exploratory and should not carry a strong mechanistic claim.

Expected outputs:

- `runs/measurement_validation/temporal_self_*`
- Updated diagnostic report.
- One figure or supplementary panel for temporal self refinement.

### Week 2: Ownership Self

Questions:

- Is ownership self only meaningful in systems with action loops?
- Does the current proxy measure internal attribution rather than behavioral attribution?
- Should ownership be split into action attribution and body ownership?

Tasks:

- Run ownership diagnostics separately for systems with and without action loops.
- Implement improved ownership proxies:
  - action attribution proxy
  - body ownership proxy

- Implement improved independent tests:
  - forced-choice ownership test
  - ownership illusion resistance test

Acceptance criteria:

- At least one ownership subconstruct reaches r > 0.7 in the appropriate system class.
- If validation only works in action-loop systems, write ownership as dependent on action-outcome mechanisms.

Expected outputs:

- `runs/measurement_validation/ownership_self_*`
- Updated diagnostic report.
- Ownership refinement figure or supplementary panel.

### Week 3: Distributed Self Probes

Question:

- Are generic self tests insensitive to distributed architectures, and can architecture-specific tests recover valid measurement?

Tasks:

- Implement and run:
  - meta-monitor lesion and recovery
  - hidden-agent perturbation
  - delayed body-schema update

- Test distributed variants:
  - 4, 8, and 16 agents
  - coordination on/off
  - feedback on/off

Acceptance criteria:

- Architecture-specific distributed self score correlates with a distributed self proxy at r > 0.7.
- If not, distributed self remains a measurement-limitation case study rather than a validated claim.

Expected outputs:

- `runs/measurement_validation/distributed_hard_probes_*`
- Figure showing why generic probes failed and whether harder probes improved sensitivity.

## Phase 2: Paper and Figure Consolidation

Estimated duration: 2-3 weeks.

Goal: convert validated constructs into a conservative, clear paper. Unvalidated constructs should remain limitations, exploratory analyses, or future work.

### Week 4: Figures

Core figures:

- Figure 1: measurement validation framework.
- Figure 2: agency refinement before/diagnosis/after.
- Figure 3: action agency mechanism validation.
- Figure 4: self-model construct split.
- Figure 5: double dissociation summary.
- Figure 6: distributed self architecture-specific probes.

Supplementary figures:

- ALife evolution trajectory.
- Full correlation matrices.
- Parameter scans and heatmaps.

Current saved figure snapshot:

- `docs/paper/figure_snapshots/20260521_roadmap_snapshot`

### Week 5: Results Rewrite

Preferred structure:

1. Initial validation reveals systematic discrepancies.
2. Diagnostic experiments identify conceptual confusions.
3. Conceptual refinement and re-validation.
4. Mechanistic validation: double dissociation.
5. Architecture-specific measurement limitations and probes.
6. Comprehensive validation summary.

Every result should include:

- mean and uncertainty
- correlation or ANOVA statistic
- effect size
- confidence interval where available
- figure/table reference
- claim strength label:
  - validated
  - partially validated
  - exploratory
  - measurement-limited

### Week 6: Methods and Discussion

Methods additions:

- Diagnostic protocol.
- Intermediate-variable analysis.
- Architecture-specific probe design.
- Bootstrap confidence intervals.
- Multiple-comparison handling.

Discussion additions:

- Why theoretical proxies fail.
- Gating is not agency.
- Boundary self is not ownership self.
- Validation should precede mechanistic claims.
- Artificial systems as tools for conceptual clarification.
- Limits of proxy-behavior convergence.

## Phase 3: Submission Preparation

Estimated duration: 1-2 weeks.

Tasks:

- Complete references.
- Choose target venue.
- Format paper and supplementary materials.
- Freeze all reported numbers with a consistency-check script.
- Archive code, configs, and run manifests.

Candidate references:

- Baars, 1988: Global Workspace Theory.
- Dehaene and Changeux, 2011: Global Neuronal Workspace.
- Friston, 2010: Free Energy Principle.
- Synofzik et al., 2008: comparator model of agency.
- Moore and Fletcher, 2012: sense of agency review.
- Haggard et al., 2002: intentional binding.
- Gallagher, 2000: self and agency distinctions.
- Blanke and Metzinger, 2009: body ownership.
- Cronbach and Meehl, 1955: construct validity.
- Campbell and Fiske, 1959: multitrait-multimethod validation.
- Borsboom et al., 2004: validity in psychology.

Candidate venues:

- NeurIPS or ICML if framed as method/theory for artificial systems.
- CogSci or ALIFE if framed as cognitive-science/artificial-life methodology.
- Consciousness and Cognition, Neural Networks, or Artificial Life for journal treatment.

## Claim Discipline

Allowed strong claims now:

- Corrected action-agency proxy aligns with independent behavioral agency tests.
- Boundary/core self proxy aligns with independent boundary/core tests.
- Action-outcome loops and workspace mechanisms show a validated operational double dissociation for these two constructs.

Claims to avoid for now:

- The systems are conscious.
- The systems have subjective agency.
- Temporal self and ownership self are fully validated.
- Distributed self is validated by generic tests.

Preferred wording:

- "operational action agency"
- "operational boundary self"
- "proxy-behavior convergence"
- "construct refinement"
- "measurement-limited"
- "exploratory evidence"

## Immediate Next Actions

1. Keep the ALife extension running until 10% QD coverage or the fallback deadline.
2. Implement temporal self diagnostics and improved probes.
3. Implement ownership self diagnostics and improved probes.
4. Implement distributed self harder probes.
5. Regenerate paper figures only after Phase 1 results are complete.
