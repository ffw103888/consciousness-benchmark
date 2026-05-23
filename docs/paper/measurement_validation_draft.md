# Measurement Validation Reveals Dissociable Operational Mechanisms for Boundary Self and Action Agency in Artificial Neural Architectures

## Status

Draft stage: claim-bounded manuscript scaffold.

This draft intentionally uses conservative language:

- Strong claims are limited to constructs with independent validation.
- Partially validated constructs are marked exploratory.
- Unvalidated or low-sensitivity cases are reported as measurement limitations.
- The paper does not claim that any artificial system is conscious, self-aware, or phenomenally agentic.

## Abstract

Operational proxies are widely used in consciousness-adjacent artificial systems research, but they are rarely validated against independent behavioral measures. We investigated proxy validity by comparing theoretically motivated internal-state measures against behavior-level tests in artificial neural architectures. Initial validation revealed systematic discrepancies: an agency proxy showed negative correlation with independent agency tests in thalamus-inspired systems (`r=-0.86`), while self-model validation was uneven across architectures. Detailed diagnostics identified two conceptual confusions. First, information gating was conflated with action-outcome agency. Second, boundary maintenance was conflated with temporal and ownership-like self measures. After separating these constructs, corrected proxies showed strong convergence with independent tests for action agency (`r=0.874` overall; thalamus `r=0.853`; distributed `r=0.975`) and boundary/core self (`r=0.940` overall). Mechanistic manipulations then supported a bounded double dissociation: action-outcome loops selectively increased corrected agency proxies, while workspace and body-boundary mechanisms aligned with boundary/core self proxies. By contrast, temporal self showed only moderate validation (`r=0.524`), ownership self remained weak (`r=0.411`), and distributed self tests showed insufficient sensitivity (`r=0.166` in an expanded condition grid). These findings demonstrate that theoretically motivated proxies can systematically measure the wrong construct, that behavioral validation can reveal and correct such errors, and that artificial architectures provide a useful testbed for conceptual refinement. We propose a validation-first framework for artificial consciousness research. These findings establish measurement validation as a prerequisite for mechanistic claims in artificial consciousness research.

## 1. Introduction

Artificial consciousness research often depends on operational proxies. Integrated information, perturbational complexity, global broadcasting, self-model stability, temporal continuity, and agency-like control scores are used because the target constructs cannot be directly observed. This is unavoidable, but it creates a methodological risk: a proxy can be theoretically motivated and still measure the wrong thing.

This risk is especially acute when constructs co-occur in biological systems. In biological agents, information selection, motor control, body ownership, temporal continuity, and self-boundary maintenance are deeply entangled. A neural correlate that appears to track one construct may in fact track another nearby process. Artificial systems make this problem visible because architectural components can be separated more cleanly than they can in biological organisms.

Artificial neural systems offer unique advantages for measurement validation. Unlike biological systems, where different processes necessarily co-occur, artificial systems allow cleaner dissociation of mechanisms. For example, information gating can be implemented without action-outcome control, and body-boundary tracking can be implemented without ownership attribution. This enables detection of conceptual confusions that remain hidden in biological research, not because artificial systems are simpler, but because they permit controlled manipulations that are difficult or impossible in living organisms.

We studied this problem in a controlled artificial setting. We implemented several architectures intended to instantiate distinct organizational principles: a thalamus-inspired architecture with reticular gating and a limited global workspace, a distributed multi-agent architecture with sparse coordination and local memories, and an artificial-life archive used for open-ended behavioral search. Initial experiments suggested dissociations between self-model and agency proxies. However, rather than treating those proxy patterns as direct evidence, we subjected them to independent behavior-level validation.

The validation process revealed two instructive failures. First, an initial "agency" proxy in the thalamus architecture was strongly anti-correlated with independent agency tests. Diagnostics showed that it was measuring gating coordination, not action-outcome agency. After separating gating from action-outcome prediction, the corrected agency proxy aligned strongly with independent tests. Second, the initial self-model proxy mixed several constructs. Boundary/core self aligned strongly with independent tests, but temporal and ownership-like components did not.

These results motivate the central claim of this paper: measurement validation must precede mechanistic interpretation. We do not claim that our systems possess consciousness, selfhood, or subjective agency. We claim that, within an operational framework, corrected action-agency and boundary-self proxies can be validated against independent behavior-level probes, while other constructs remain under-validated and require further test design.

Our contributions are:

1. We demonstrate a concrete proxy failure: information gating can be mistaken for agency.
2. We show that conceptual refinement can rescue a mechanistic result when the mechanism is real but the proxy is mislabeled.
3. We decompose self-model measurement into boundary/core, temporal, and ownership-like components, showing that only the first is currently strongly validated.
4. We provide a validation-first workflow for artificial consciousness research: proxy definition, independent tests, discrepancy diagnostics, construct splitting, and bounded mechanistic claims.

## 2. Methods

### 2.1 Architectures

#### Thalamus-Inspired Architecture

The thalamus-inspired system contains sensory candidates, a reticular gating layer, a limited-capacity global workspace, cortical modules, and optional action-outcome loops. The workspace admits selected information items, decays older contents, and broadcasts a compressed vector to cortical modules. The action-outcome loop, when enabled, predicts proprioceptive consequences of pending actions and updates prediction parameters from observed deltas.

This architecture supports a factorial manipulation:

- Workspace absent or present (`W-` / `W+`)
- Action-outcome loop absent or present (`A-` / `A+`)

This produces four core conditions: `W-A-`, `W+A-`, `W-A+`, and `W+A+`.

#### Distributed Multi-Agent Architecture

The distributed architecture contains local agents with limited perception, local memory, and local action requests. A coordination layer resolves conflicts and broadcasts sparse global signals. A meta-monitor tracks aggregate properties such as active-agent count, centroid, spread, success, controllability, and goal alignment.

The main manipulation enables or disables action feedback. Additional validation runs varied agent count, sensor range, coordination, world size, and global goal location.

#### Artificial-Life Archive

The artificial-life path uses an open-ended quality-diversity archive over a four-dimensional behavior space. The archive is not used as the primary measurement-validation system in this paper; it serves as a long-running exploratory background system and a source of future candidate behaviors.

### 2.2 Initial Operational Proxies

We initially measured five proxy dimensions:

- `state`
- `content`
- `self_model`
- `agency`
- `temporal_continuity`

These proxies were intentionally separated and never collapsed into a single consciousness score. However, early validation showed that separation alone is insufficient: a named proxy can still track the wrong operational construct.

### 2.3 Independent Behavior-Level Tests

We implemented independent tests for self-related and agency-related constructs. These tests were designed not to reuse the same internal equations as the proxies.

Agency tests included:

- intentional-binding analogue
- error-attribution test
- controllability-preference test
- forced-action probe

Self-related tests included:

- boundary perturbation
- computational mirror test
- ownership attribution
- architecture-specific self probe

The architecture-specific self probe adapts to the natural boundary of each architecture. For thalamus systems, it tests functional workspace boundaries: information admission, rejection, capacity maintenance, and gating consistency. For distributed systems, it tests body-schema tracking: active-agent tracking, centroid tracking, external perturbation stability, and damage/recovery updates.

### 2.4 Diagnostic Protocol

When proxy-behavior discrepancies were detected (`|r| < 0.5` or `r < 0`), we did not discard the result or tune the proxy directly. Instead, we ran a diagnostic protocol:

1. Intermediate-variable analysis. We measured variables hypothesized to mediate the proxy-behavior relationship, including gating activity, prediction error, temporal stability, workspace load, body-schema stability, and controllability.
2. Condition-level inspection. We compared proxy and independent scores across architecture and ablation conditions to identify specific cases where the proxy failed.
3. Architecture-specific probes. We designed tests tailored to each architecture's computational structure, such as forced-action probes for thalamus systems and body-schema probes for distributed systems.
4. Conceptual refinement. Based on diagnostic results, we decomposed conflated constructs into separable components and re-validated each component independently.

This produced two major conceptual refinements:

- `agency_proxy` was split into `gating_coordination_proxy` and `action_agency_proxy`.
- `self_model` was split into `boundary_self_proxy`, `temporal_self_proxy`, and `ownership_self_proxy`.

This iterative validation-diagnosis-refinement cycle continued until proxy-behavior convergence was achieved for a construct (`r > 0.7`) or a measurement limitation was identified.

### 2.5 Claim Tiers

We use three claim tiers:

- Validated operational construct: proxy aligns strongly with independent tests.
- Exploratory construct: proxy has moderate or weak validation and requires further work.
- Measurement-limited construct: tests lack sensitivity or show unresolved disagreement.

Only validated constructs are used for strong mechanistic claims.

## 3. Results

### 3.1 Initial Agency Validation Failed

The initial thalamus agency proxy produced a severe discrepancy. In thalamus systems without action-outcome loops, the proxy could report high agency despite low independent agency scores. Across thalamus conditions, the initial proxy was negatively correlated with independent tests (`r=-0.86`).

Diagnostics showed that the proxy was tracking gating coordination. In other words, it measured which information entered the workspace, not whether the system could predict or control the consequences of its own actions.

### 3.2 Correcting the Agency Proxy Restored Agreement

We split the original measure into:

- `gating_coordination_proxy`: information selection and gating dynamics
- `action_agency_proxy`: action-outcome prediction and control
- `legacy_agency_proxy`: old mixed measure retained for diagnostics

After correction, proxy-independent agreement became strong:

- overall agency: `r=0.874`
- thalamus agency: `r=0.853`
- distributed agency: `r=0.975`

The corrected proxy also preserved the mechanistic pattern: systems with action-outcome loops or action feedback showed higher action-agency scores than systems without them.

### 3.3 Self-Model Required Construct Splitting

Self-model validation did not fail in the same way as agency. Instead, it revealed mixed constructs.

After adding architecture-specific self probes and splitting the proxy, boundary/core self showed strong agreement:

- boundary/core self: `r=0.940`

By contrast, temporal and ownership-like components were weaker:

- temporal proxy vs mirror: `r=0.524`
- ownership proxy vs ownership attribution: `r=0.411`
- identity/ownership aggregate: `r=-0.135`

These results suggest that boundary maintenance, temporal continuity, and ownership attribution should not be treated as a single self-model construct.

### 3.4 Validation Success After Refinement: Bounded Mechanistic Dissociation

After measurement correction, two mechanistic claims are currently supported:

1. Action-outcome mechanisms align with corrected action-agency proxies.
2. Workspace or body-boundary mechanisms align with boundary/core self proxies.

The stronger claim that "workspace supports self-model in general" is too broad. The evidence supports boundary/core self, not ownership self.

Similarly, the claim that "action loops produce agency" must be read operationally: action loops increase validated action-outcome agency proxies and independent behavior-level agency probes. This is not a claim about subjective agency.

### 3.5 Distributed Self Remains Measurement-Limited

The distributed architecture initially appeared to support high self-model scores. However, expanded validation across agent count, sensor radius, coordination on/off, shifted goals, and world size produced weak correlations:

- distributed self proxy vs independent self: `r=0.166`
- distributed boundary proxy vs core/boundary tests: `r=0.124`
- distributed temporal proxy vs mirror: `r=-0.070`
- distributed ownership proxy vs ownership test: `r=-0.097`

Inspection showed that the distributed independent tests lacked dynamic range. The architecture-specific self probe was nearly saturated around `0.98-1.00`, the computational mirror test was also near saturation, and boundary perturbation remained in a narrow band. Therefore, the distributed result is best interpreted as a measurement-sensitivity limitation, not as evidence against distributed self-organization.

## 4. Discussion

### 4.1 Proxy Failure Is Informative

The initial agency failure was not merely a bug. It revealed a conceptual confusion: information selection and behavioral control can co-occur in biological systems but separate in artificial ones. The artificial architecture exposed a distinction that would be difficult to isolate biologically.

### 4.2 Boundary Self Is Not Ownership Self

Self-model measurement required a different correction. The core boundary construct aligned well with independent tests, but ownership-like measures did not. This suggests that artificial self-model research should distinguish at least three operational dimensions:

- boundary/core self
- temporal self
- ownership self

The current evidence supports strong claims only for boundary/core self.

### 4.3 Validation Should Precede Mechanism Claims

Mechanistic experiments are tempting to interpret directly. However, a manipulation can affect a proxy for the wrong reason. Our results show that a mechanism may be real while the label attached to its proxy is wrong. The correct order is:

1. Define the proxy.
2. Validate it against independent tests.
3. Diagnose discrepancies.
4. Split constructs where needed.
5. Only then interpret mechanisms.

### 4.4 Limitations

The study is limited in several ways:

- The tests are operational and behavior-level; they do not establish subjective experience.
- Proxy-test convergence is only one form of construct validity. Both a proxy and an independent test may miss aspects of the intended construct.
- Independent tests are themselves fallible and can be too easy or too hard for a given architecture.
- The behavioral tests were designed from existing theories, and those theories may contain their own conceptual confusions.
- Distributed self validation remains unresolved because current tests have low sensitivity.
- The proposed harder distributed probes, including meta-monitor lesions, hidden-agent perturbations, and delayed body-schema updates, remain future work.
- The study focused on boundary self and action agency. Other consciousness-related constructs, including attention, metacognition, affective valence, and phenomenal content, require separate validation.
- Literature grounding and external benchmark comparison are not yet complete.
- Statistical estimates in quick validation runs should be replaced by larger seed counts for final submission.

### 4.5 Future Work

Future work should develop harder distributed self tests:

- meta-monitor lesion
- hidden-agent perturbation
- delayed body-schema update
- coordination lesion
- conflict-resolution/body-boundary dissociation

The artificial-life archive should be used to identify naturally emerging cases where boundary self, temporal self, ownership self, and action agency dissociate without being directly engineered.

## 5. Conclusion

This work demonstrates that operational proxies in artificial consciousness research can fail systematically, even when theoretically motivated. The failure is useful when treated diagnostically. By validating proxies against independent tests, we identified and corrected a gating-agency confusion, decomposed self-model measurement into boundary, temporal, and ownership components, and established bounded mechanistic evidence for action-outcome agency and boundary/core self. The broader lesson is methodological: artificial consciousness research needs validation-first measurement before it can make reliable mechanistic or theoretical claims.
