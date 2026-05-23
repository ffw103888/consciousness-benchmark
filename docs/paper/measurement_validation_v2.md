# Measurement Validation Reveals Five Dissociable Operational Constructs Underlying Self-Model and Agency in Artificial Neural Architectures

## Abstract

Operational proxies are common in artificial consciousness research, but their validity is rarely tested against independent behavioral measures. We evaluate such proxies in artificial neural architectures by comparing internal-state measures with behavior-level probes. Initial validation exposed substantial mismatches: a thalamus-inspired agency proxy was negatively correlated with independent agency tests (`r=-0.860`), and generic distributed self tests had poor convergence. Diagnostic experiments showed that the agency proxy primarily measured gating rather than action-outcome control, and that broad self-model scores conflated boundary maintenance, identity persistence, and ownership. After refinement, five operational constructs showed strong proxy-test convergence, including action agency (`r=0.874`) and boundary self (`r=0.940`). Mechanistic manipulations then separated their computational substrates: workspace mechanisms supported boundary and identity-temporal measures, action-outcome loops supported agency and action ownership, and meta-monitoring supported distributed body-schema measures. Subsequent Transformer diagnostics showed that action-loop effects generalize to an attention-based substrate, while boundary-self validation remains measurement-limited. These results support a validation-first approach: theoretically motivated proxies can misidentify constructs, but diagnostic failures can be used to refine the construct space before making mechanistic claims.

## 1. Introduction

Artificial consciousness research depends on operational measurement. Constructs such as global broadcasting, self-model stability, temporal continuity, ownership, and agency cannot be read directly from a system. They must be inferred from proxies. This is unavoidable, but it creates a risk: a proxy can be theoretically motivated and still measure the wrong process.

This risk is especially acute when constructs co-occur in biological systems. Information selection, action control, body ownership, temporal continuity, and boundary maintenance are deeply entangled in living agents. Artificial systems allow cleaner dissociation. A system can have information gating without action-outcome control, or distributed body-schema tracking without subjective ownership. This makes artificial architectures useful not because they are simpler, but because they allow interventions that are difficult or impossible in biological systems.

We studied this problem in three primary research contexts: a thalamus-inspired architecture with reticular gating and a limited workspace, a distributed multi-agent architecture with local agents and a meta-monitor, and an artificial-life quality-diversity archive used as open-ended search context. A subsequent Transformer-inspired follow-up tested whether the main mechanism pattern survived in an attention-based substrate. Early experiments suggested self-agency dissociations, but measurement validation revealed that some proxies were mislabeled. We therefore shifted from mechanism interpretation to measurement validation.

Our central claim is methodological: validation must precede mechanistic interpretation. After an iterative diagnostic-refinement process, we validated five operational constructs and identified several exploratory or measurement-limited constructs that should remain outside strong mechanism claims.

The paper makes three contributions. First, it shows that a theoretically motivated proxy can fail in a structured way: the original agency proxy was strongly anti-correlated with independent tests because it measured gating rather than action-outcome control. Second, it uses this failure to refine the construct set, separating action agency, boundary self, identity-temporal self, action ownership, and distributed body-schema self. Third, it links these validated operational constructs to separable computational substrates--workspace, action-outcome loops, and meta-monitoring--while using subsequent Transformer diagnostics to show that mechanism generalization and construct validation can diverge.

### 1.1 Related Work and Measurement Framing

The computational mechanisms studied here are motivated by several overlapping literatures, but the claims made in this paper are narrower than the theories that inspired them. Global workspace theories argue that conscious access depends on selective broadcast and integration across specialized processors (Baars, 1988; Dehaene and Changeux, 2011). Our workspace manipulations are related to that idea, but we treat them as operational integration mechanisms rather than as sufficient conditions for consciousness.

Predictive-processing and comparator accounts of agency emphasize action-outcome prediction, prediction error, and cue integration in the sense of control (Friston, 2010; Synofzik et al., 2008; Moore and Fletcher, 2012; Haggard et al., 2002). These theories motivate the action-loop manipulation and the decision to separate action agency from information gating.

Work on minimal selfhood and body ownership distinguishes bodily boundary, ownership, agency, and temporal continuity as partially separable phenomena (Gallagher, 2000; Blanke and Metzinger, 2009; Tsakiris, 2010; Seth, 2013). This motivates our decision to decompose self-model measures rather than treating selfhood as one score.

The measurement strategy comes from construct-validity research. Psychological measurement has long distinguished theoretical constructs from their indicators, and has emphasized convergent and discriminant validation across methods (Cronbach and Meehl, 1955; Campbell and Fiske, 1959; Borsboom et al., 2004). Artificial consciousness research often uses operational proxies, but proxy validity is rarely cross-validated against independent behavioral probes (Gamez, 2008; Reggia, 2013; Haladjian and Montemayor, 2016). This paper treats artificial architectures as measurement testbeds: if a proxy fails, the failure is informative because mechanisms can be cleanly separated and retested.

## 2. Methods

### 2.1 Architectures

#### Thalamus-Inspired Architecture

The thalamus-inspired architecture contains sensory candidates, a reticular gating layer, a limited-capacity global workspace, cortical modules, and optional action-outcome loops. The workspace admits selected information items and broadcasts a compressed vector to cortical modules. The action loop predicts proprioceptive consequences of pending actions and updates prediction parameters from observed deltas.

The core factorial manipulation crosses workspace availability and action-loop availability:

- `W-A-`: no workspace, no action loop
- `W+A-`: workspace, no action loop
- `W-A+`: no workspace, action loop
- `W+A+`: workspace, action loop

#### Distributed Multi-Agent Architecture

The distributed architecture contains local agents with limited perception, local memory, and local action requests. A coordination layer resolves conflicts. A meta-monitor tracks aggregate properties including active-agent count, centroid, spread, success, controllability, and goal alignment.

Distributed validation included feedback on/off, coordination on/off, agent-count changes, sensor-range changes, shifted goals, world-size changes, and graded meta-monitor controls.

#### Artificial-Life Archive

The artificial-life path uses a quality-diversity archive over a four-dimensional behavior space. It is included as open-ended search context and future candidate-discovery infrastructure. It is not the primary source of the five validated constructs in this manuscript.

#### Transformer-Inspired Follow-Up

A subsequent Transformer-inspired system was used for cross-architecture diagnosis. It contains a small attention block over synthetic tokens, optional workspace-like memory, and optional action-outcome loops. The purpose was not to model production language models or subjective report, but to test whether the same operational manipulations behave similarly in an attention-based substrate.

The Transformer follow-up crossed workspace availability with action-loop availability using the same notation as the thalamus factorial design:

- `W-A-`: no workspace memory, no action loop
- `W+A-`: workspace memory, no action loop
- `W-A+`: no workspace memory, action loop
- `W+A+`: workspace memory and action loop

Additional Transformer diagnostics varied action-effect noise, action-loop learning rate, and workspace strength. These diagnostics were treated as measurement probes rather than part of the primary validation set.

### 2.2 Initial Proxies

Initial evaluation tracked five proxy dimensions:

- state
- content
- self_model
- agency
- temporal_continuity

These dimensions were intentionally separated rather than collapsed into a single "consciousness score." However, validation showed that separation alone is insufficient. A separate proxy can still track the wrong construct.

### 2.3 Independent Tests

Agency-related independent tests included:

- intentional-binding analogue
- error-attribution test
- controllability-preference test
- forced-action probe

Self-related tests included:

- boundary perturbation
- computational mirror test
- ownership attribution
- architecture-specific self probe

Additional measurement-strengthening tests were added after diagnosis:

- delayed identity recognition
- identity marker persistence
- transformed mirror test
- temporal binding test
- forced-choice ownership
- ownership illusion resistance
- meta-monitor lesion
- hidden-agent perturbation
- body-schema update probe
- graded meta-monitor strength/noise/delay controls

### 2.4 Refined Operational Constructs

All refined scores are normalized to `[0, 1]`, with larger values indicating stronger expression of the operational construct. A construct was treated as validated when its proxy and independent-test scores showed stable positive convergence, using `r >= 0.7` as the working threshold together with inspection of confidence intervals and condition-level behavior. Results in the intermediate range (`0.5 <= r < 0.7`) were treated as exploratory pending additional probes, while weaker or reversed relationships triggered diagnosis. The final five validated constructs are summarized below.

| Construct | Proxy score | Independent tests | Hypothesized mechanism |
|---|---|---|---|
| Action agency | action-outcome prediction/control score after separating gating from control | intentional-binding analogue, error attribution, controllability preference, forced-action probes | action-outcome loop |
| Boundary self | boundary-maintenance proxy derived from workspace-supported self-boundary stability | boundary perturbation and self/other discrimination probes | workspace |
| Identity-temporal self | identity-marker persistence proxy | delayed identity recognition and temporal-binding probes | workspace |
| Action ownership | action-attribution proxy | forced-choice ownership and ownership-illusion resistance probes | action-outcome loop |
| Distributed body-schema self | meta-monitor/body-schema coherence proxy | meta-monitor lesion, hidden-agent perturbation, body-schema update, and graded controls | meta-monitor |

These are operational constructs rather than reports of subjective experience. The proxy column and independent-test column are intentionally kept separate in the benchmark package so that future systems can reproduce the validation rather than inherit a pre-combined score. Hypothesized mechanisms are based on prior theory and architectural design; their effects are tested empirically in Section 3.6.

### 2.5 Diagnostic Protocol

When proxy-test convergence was below the validation threshold, we used a diagnostic-refinement cycle. Reversed relationships (`r < 0`) or weak convergence (`r < 0.5`) were treated as strong evidence of construct mismatch; intermediate results (`0.5 <= r < 0.7`) were retained as exploratory unless additional probes established stable convergence.

1. Inspect condition-level failures.
2. Measure intermediate variables.
3. Identify which variable the proxy actually tracks.
4. Split conflated constructs.
5. Re-validate each refined construct.
6. Upgrade claims only for constructs with stable convergence.

This procedure follows a multitrait-multimethod logic: a construct is strengthened when proxy and behavioral tests converge, but also when nearby constructs remain discriminable. Failure therefore triggers diagnosis rather than ad hoc relabeling.

Figure 1 summarizes this validation-diagnosis-refinement workflow.

### 2.6 Claim Tiers

We use four claim tiers:

- Validated operational construct: strong proxy-test convergence.
- Validated construct after decomposition: strong convergence after a broader construct was split.
- Exploratory construct: interesting but weak or unstable convergence.
- Measurement-limited construct: current tests lack dynamic range or sensitivity.

Only validated constructs are used for strong mechanism claims.

Transformer follow-up analyses are explicitly assigned to the exploratory or measurement-limited tiers. They are used to test generalization and expose architecture-specific measurement failures, not to expand the primary validated construct set.

### 2.7 Statistical Analysis

Proxy-test convergence was quantified with Pearson correlation. Bootstrap 95% confidence intervals were computed from 10,000 paired resamples. Mechanistic effects in the thalamus-inspired factorial design are reported as condition mean differences: workspace effects are the average of `W+A- - W-A-` and `W+A+ - W-A+`; action-loop effects are the average of `W-A+ - W-A-` and `W+A+ - W+A-`. Confidence intervals for these effects were computed by resampling within each condition. Because some refined probes, especially action-ownership probes, are near-deterministic, standardized effect sizes can become very large and three-decimal confidence intervals can become very narrow. Mean differences and confidence intervals are therefore treated as the primary quantities, with Cohen's d retained as an auxiliary statistic and higher-precision bootstrap outputs reported in the machine-readable statistics. For correlations exceeding `0.99`, we report six-decimal precision to distinguish near-ceiling values; for near-zero mean differences, we report four-decimal precision to show the confidence interval. Mean differences smaller than the four-decimal display threshold are reported as `+0.0000` with their confidence intervals.

For distributed meta-monitor controls, we report Pearson correlations between graded control variables and hard-probe scores. Meta-monitor strength is expected to correlate positively with hard-probe scores; meta-monitor noise and delay are expected to correlate negatively if probes track functional degradation. Delay was retained as a control even though it did not show a strong monotonic relationship in the primary run.

Transformer follow-up analyses use the same correlation-based reporting but are not included in the primary validation tables. Their role is diagnostic: they test whether mechanism effects and measurement validity behave similarly in an attention-based substrate.

### 2.8 Data, Figures, and Reproducibility

The primary statistical pass was generated by `scripts/finalize_statistics.py` with 10,000 bootstrap resamples and seed `20260521`. Machine-readable outputs are stored in `docs/paper/statistics/final_20260521`, including:

- `final_statistics.json`
- `construct_validation_stats.csv`
- `mechanism_effects.csv`
- `distributed_control_correlations.csv`
- `number_consistency.csv`

The five main figures are generated by `scripts/generate_paper_figures_v2.py` and stored in `docs/paper/figures/paper_v2_20260521`. The Transformer diagnostic figure is generated by `scripts/generate_transformer_figure6.py`. The current figure manifest is `docs/paper/figures/paper_v2_20260521/manifest.json`.

The public benchmark interface mirrors the same data structure. The `consciousness_benchmark` package exposes each construct as a pair of columns (`proxy_col`, `independent_col`) plus architecture metadata (`validated_in`, `measurement_limited_in`, and `variants`). This prevents a construct from being silently applied to an architecture where it is unvalidated or measurement-limited.

## 3. Results

### 3.1 Initial Validation Failures

The first validation pass showed that the original thalamus agency proxy was anti-correlated with independent agency tests (`r=-0.860`). Inspection showed the most problematic case was `W-A-`: a system with no action loop could receive a high agency proxy score because the proxy was actually tracking gating activity.

Self-model validation was mixed. The initial self-model proxy showed moderate overall agreement, but the result concealed construct mismatch. Distributed self validation was especially weak under the original generic tests (`r=0.166`), suggesting either absence of the construct or inadequate measurement sensitivity.

These failures were treated as measurement evidence. If a theoretically motivated proxy reverses against independent tests, then either the tests are inappropriate, the proxy is mislabeled, or the construct is underspecified.

The three diagnostic-refinement cycles are summarized in Figure 2.

### 3.2 Agency Refinement

The original agency proxy conflated information selection with behavioral control. We split it into:

- `gating_coordination_proxy`: information selection and gating
- `action_agency_proxy`: action-outcome prediction and control
- `legacy_agency_proxy`: retained for auditability

After correction, action-agency proxy-test convergence improved from negative correlation in thalamus systems to strong positive convergence overall:

- action agency: `r=0.874`, 95% CI `[0.774, 0.943]`, `p=2.4e-08`

This preserved the mechanism finding while changing its interpretation: action-outcome loops increased operational agency, whereas workspace alone did not. The original high scores in no-action-loop thalamus systems were therefore not evidence for agency; they were evidence that information gating had been misclassified as agency.

### 3.3 Self-Model Decomposition

The initial self-model proxy mixed multiple operational constructs. Boundary/core self validated strongly:

- boundary self: `r=0.940`, 95% CI `[0.847, 0.994]`, `p<1e-9`

Temporal self required further splitting. Generic trajectory consistency did not align with refined temporal tests. The validated temporal component was identity persistence:

- identity marker persistence vs delayed identity recognition: `r=0.850`, 95% CI `[0.755, 0.912]`, `p<1e-9`

Ownership also required splitting. Body ownership remained exploratory, but action ownership validated strongly:

- action ownership: `r=0.996`, 95% CI `[0.994, 0.998]`, `p<1e-9`

Boundary self, identity-temporal self, action ownership, and body ownership are operationally separable. Only the first three refined self-related constructs above were upgraded into strong claims. Body ownership remained exploratory because the available proxy and independent test did not yet converge.

### 3.4 Distributed Self Probes

Generic distributed self tests initially had poor dynamic range. We therefore added architecture-specific probes:

- meta-monitor lesion
- hidden-agent perturbation
- body-schema update

With these probes, distributed body-schema/meta-monitor self validated strongly:

- distributed body-schema self: `r=0.924`, 95% CI `[0.881, 0.956]`, `p<1e-9`

To rule out the explanation that hard probes merely detected a binary meta-monitor switch, we introduced graded meta-monitor controls. Hard-probe scores varied continuously with meta-monitor strength:

- meta-monitor strength vs hard probes: `r=0.887`, 95% CI `[0.846, 0.945]`, `p=7.9e-09`

Meta-monitor noise strongly degraded hard-probe scores:

- meta-monitor noise vs hard probes: `r=-0.974`, 95% CI `[-0.992, -0.952]`, `p=9.0e-08`

This supports the interpretation that hard probes track functional meta-monitor quality, not merely module presence (Figure 5).

### 3.5 Validated Operational Constructs

Table 1 summarizes the final validated construct set:

| Construct | n | Proxy-test r (95% CI) | p | Status | Mechanism |
|---|---:|---:|---:|---|---|
| Action agency | 24 | 0.874 [0.774, 0.943] | 2.4e-08 | validated | action-outcome loop |
| Boundary self | 24 | 0.940 [0.847, 0.994] | <1e-9 | validated | workspace |
| Identity-temporal self | 48 | 0.850 [0.755, 0.912] | <1e-9 | validated | workspace |
| Action ownership | 48 | 0.996 [0.994, 0.998] | <1e-9 | validated | action-outcome loop |
| Distributed body-schema self | 52 | 0.924 [0.881, 0.956] | <1e-9 | validated | meta-monitor |

These correlations are visualized in Figure 3. Sample sizes differ because the first two constructs use the thalamus factorial validation set, identity-temporal self and action ownership include the refined extension probes, and distributed body-schema self includes architecture-specific hard probes plus graded meta-monitor controls. For the distributed architecture, graded controls served as the analogue of the factorial mechanism check because the architecture was not organized around the same workspace-by-action-loop design.

Extended 16-seed robustness analyses are reported in Supplementary Section S1.

### 3.6 Mechanistic Dissociation

Mechanistic analysis showed a clear dissociation:

- Workspace availability strongly affected boundary self (`+0.4679`, 95% CI `[0.4347, 0.4963]`) and identity-temporal self (`+0.2535`, 95% CI `[0.2113, 0.2859]`), while having negligible effect on action agency (`-0.0011`, 95% CI `[-0.0062, 0.0049]`) and action ownership (`+0.0001`, 95% CI `[-0.0002, 0.0004]`).
- Action-loop availability strongly affected action agency (`+0.7113`, 95% CI `[0.7064, 0.7173]`) and action ownership (`+0.9680`, 95% CI `[0.9678, 0.9683]`), while having only a small effect on boundary self (`-0.0453`, 95% CI `[-0.0781, -0.0157]`) and little effect on identity-temporal self (`+0.0131`, 95% CI `[-0.0201, 0.0546]`).
- Meta-monitor strength showed a graded relationship with distributed hard-probe scores (`r=0.887`, 95% CI `[0.846, 0.945]`), and meta-monitor noise degraded them (`r=-0.974`, 95% CI `[-0.992, -0.952]`).

This supports an operational triple dissociation among workspace, action-outcome, and meta-monitoring mechanisms (Figure 4).

### 3.7 Transformer Follow-Up

The Transformer-inspired follow-up tested whether the mechanism pattern generalized to an attention-based substrate. The initial 2x2 run showed selective mechanism effects while also exposing architecture-specific measurement limits (Figure 6).

Action-loop availability increased the action-agency proxy (`+0.8189`, 95% CI `[0.8180, 0.8198]`, `p<1e-9`) and the action-ownership proxy (`+0.8189`, 95% CI `[0.8180, 0.8198]`, `p<1e-9`). It had little effect on the boundary-self proxy (`-0.0046`, 95% CI `[-0.3087, 0.2585]`, `p=0.9760`). Workspace availability increased the boundary-self proxy (`+0.8296`, 95% CI `[0.8207, 0.8377]`, `p<1e-9`) but not the action-agency proxy (`+0.0000`, 95% CI `[-0.3066, 0.2564]`, `p=1.0000`).

The low-noise 2x2 run also produced near-ceiling proxy-test correlations for action agency (`n=32`, `r=0.999825`, 95% CI `[0.999677, 0.999947]`) and action ownership (`n=32`, `r=0.999995`, 95% CI `[0.999990, 0.999999]`). A difficulty diagnostic varied action-effect noise and action-loop learning rate. Under these diagnostics, convergence dropped:

- all diagnostic conditions, agency proxy vs independent agency: `n=104`, `r=0.795`, 95% CI `[0.762, 0.836]`
- all diagnostic conditions, ownership proxy vs independent ownership: `n=104`, `r=0.664`, 95% CI `[0.589, 0.739]`
- noise sweep only, agency proxy vs independent agency: `n=48`, `r=0.991`, 95% CI `[0.986, 0.994]`
- learning-rate sweep only, agency proxy vs independent agency: `n=40`, `r=0.266`, 95% CI `[0.030, 0.516]`
- learning-rate sweep only, ownership proxy vs independent ownership: `n=40`, `r=-0.122`, 95% CI `[-0.442, 0.225]`

This indicates that the near-ceiling correlations reflected shared variance from action-outcome prediction accuracy under low-noise conditions. The mechanism effect remains meaningful, but the low-noise validation statistic should not be interpreted as independent construct validation.

Boundary self showed the opposite pattern. Workspace dose tracked the internal boundary proxy (`n=40`, `r=0.728`, 95% CI `[0.564, 0.845]`), but did not converge with independent boundary tests:

- generic boundary probe: `n=40`, `r=0.325`, 95% CI `[-0.023, 0.620]`
- attention-specific hard boundary probe: `n=40`, `r=0.246`, 95% CI `[-0.023, 0.520]`
- workspace dose vs attention-specific hard boundary probe: `n=40`, `r=0.223`, 95% CI `[-0.049, 0.514]`

The Transformer result therefore supports a conservative interpretation: action-loop mechanisms generalize well to an attention-based substrate, but boundary self remains measurement-limited in the current Transformer implementation. Workspace memory changes internal state, yet those changes do not currently translate into behaviorally or attentionally validated boundary maintenance.

An exploratory construct-variant mini-study then asked whether Transformer-specific self might appear as either attention-focus self or context-window self. Neither candidate validated: attention-focus self had proxy-test convergence of `r=0.203`, while context-window self had proxy-test convergence of `r=0.152`. Context-window dose showed only a weak relation to the independent test (`r=0.341`).

The more informative pattern was a high-agency / low-boundary profile. Across the agency-boundary grid, `36/96` rows (`37.5%`) met the criterion of high independent agency (`>=0.70`) and low independent boundary score (`<0.50`). Independent agency and independent boundary scores were largely dissociated (`r=0.129`). This should not be upgraded to a new validated self construct. It is better treated as an architecture-conditioned profile: Transformer-like systems can show strong predictive agency while failing current boundary-self validation.

Within the Transformer follow-up, boundary self, attention-focus self, context-window self, and the high-agency / low-boundary profile remain outside the strong mechanism claims. These items are retained as architecture-conditioned targets for future measurement work rather than reported as validated constructs.

Extended Transformer validation and workspace capacity sweeps are reported in Supplementary Sections S2 and S3.

## 4. Discussion

### 4.1 Proxy Failure Can Be Productive

The initial agency failure was not merely a bug. It exposed a conceptual confusion. In biological systems, gating and action control often co-occur. In artificial systems, they can be separated. This separation revealed that the original proxy measured information selection rather than agency.

A failed validation can be informative when it reveals which construct a proxy actually measures. The thalamus `W-A-` case made this especially clear: a no-action-loop system looked agentic under the original proxy because it gated information strongly, but independent agency probes remained low. The corrected proxy was applied to the same data, and the mechanism direction did not change.

### 4.2 Self-Model Is Not a Single Operational Kind

Boundary maintenance, identity persistence, action ownership, and body ownership are not interchangeable. Treating them as one score hides both successes and failures.

This decomposition also changes the interpretation of mechanism effects. Workspace mechanisms supported boundary and identity-temporal measures, but they did not automatically support action ownership. Action loops supported agency and action ownership, but they did not automatically support boundary self. A single "self-model score" would obscure this pattern and invite overclaiming.

### 4.3 Architecture-Specific Measurement Is Necessary

The distributed architecture initially appeared measurement-limited. Hard probes with graded meta-monitor controls revealed that the problem was not necessarily absence of a distributed self-like process, but mismatch between generic tests and architecture-specific organization.

The Transformer follow-up adds the complementary lesson. Architecture-specific testing did not rescue boundary self. Instead, it showed that the internal workspace proxy could respond strongly to workspace dose while failing independent boundary probes. This is not merely a negative result. It suggests that some constructs may require architectural prerequisites. A Transformer-like attention substrate can express action-outcome agency and ownership-like operational signals when action loops are added, but it may not implement the kind of boundary-maintenance behavior measured in thalamus-inspired or embodied systems.

### 4.4 Architecture-Conditioned Construct Variations

The Transformer mini-study suggests that construct discovery should be architecture-conditioned rather than universal by default. Two intuitive candidates failed: attention-focus self did not validate (`r=0.203`), and context-window self did not validate (`r=0.152`) despite a weak dose signal. These negative results are useful because they show that architectural vocabulary cannot simply be relabeled as selfhood. Attention is not automatically self, and context retention is not automatically temporal identity.

The strongest Transformer-specific pattern was instead a dissociation profile: predictive agency without validated boundary self. In the agency-boundary grid, `37.5%` of rows showed high independent agency and low independent boundary score, while independent agency and boundary scores were nearly unrelated (`r=0.129`). This profile is not a phenomenological claim that a Transformer "has agency without a self." The safer interpretation is operational: action-outcome prediction can be strong in an attention-based substrate even when boundary-maintenance probes fail.

This should also not be read as evidence that Transformer-like systems lack all possible self-related constructs. The present tests address boundary self as operationalized here. Other self-like constructs may require different tasks, longer temporal structure, or different architectural probes. Comparisons to human flow states, automatic action, or meditative reports are therefore heuristic analogies rather than evidence.

This matters theoretically because it extends the original dissociation. The main experiments showed that workspace-like, action-loop, and meta-monitor mechanisms can be separately manipulated. The Transformer profile suggests a further possibility: some architectures may naturally occupy regions of construct space where one operational component is strong and another is absent or unmeasurable. The construct space therefore needs to be conditioned on architecture, with explicit records of where validation succeeded, where measurement was limited, and where architecture-specific variants emerged.

### 4.5 Mechanistic Claims Must Follow Validation

The corrected data support operational mechanism claims: workspace mechanisms support boundary and identity-temporal self measures, action-outcome loops support agency and action ownership measures, and meta-monitoring supports distributed body-schema self measures. They do not establish subjective consciousness, subjective selfhood, or phenomenological agency.

This distinction is important for computational models of consciousness-related constructs. The validated constructs are suitable for comparing architectures, diagnosing measurement failures, and testing mechanism sensitivity. They are not sufficient for attributing experience. The correct claim is that some systems satisfy validated operational criteria for action agency, boundary maintenance, identity persistence, action ownership, or distributed body-schema tracking.

### 4.6 Limitations and Future Work

The main limitation is conceptual: proxy-test convergence is not evidence of subjective experience. The constructs reported here are operational measures suitable for comparing systems and testing mechanism sensitivity, but they do not establish phenomenological selfhood, agency, or consciousness. The independent tests are also theory-laden. They provide a stronger measurement basis than internal proxies alone, but they may still miss aspects of the target constructs.

A second limitation is scope. Body ownership and trajectory consistency remain exploratory: body ownership lacked convergent proxy-test evidence, and trajectory consistency did not align with the validated identity-temporal construct. Transformer boundary self also remains measurement-limited: workspace manipulations affect an internal boundary proxy, but not the current behavior-level or attention-boundary probes. The high-agency / low-boundary Transformer profile is therefore best treated as an architecture-conditioned diagnostic pattern, not as a new validated construct. The Transformer analyses were conducted as a post-hoc generalization test rather than as part of the primary analyses and should be evaluated separately.

Future work should focus on two directions. One is measurement expansion: stronger multisensory tests for body ownership, separate treatment of trajectory consistency, and biological or phenomenological cross-validation of the operational constructs. The other is architectural generalization: testing whether high-agency / low-boundary profiles persist in larger Transformer-like systems and using the artificial-life archive to search for naturally emerging dissociations. The benchmark package now includes architecture metadata for constructs; extending this metadata as new systems are tested is a practical route toward an architecture-conditioned construct library.

## 5. Conclusion

This work shows that operational proxies in computational models of consciousness-related constructs can fail systematically, even when theoretically motivated. Treating failure diagnostically allowed us to refine constructs, validate five operational measures, and identify dissociable computational substrates. Workspace, action-outcome, and meta-monitoring mechanisms supported different validated constructs, while Transformer follow-ups showed that mechanism generalization and construct validation can diverge. The broader lesson is methodological: measurement validation is not a post-hoc check; it is a prerequisite for mechanistic interpretation.

## References

Baars, B. J. (1988). *A cognitive theory of consciousness*. Cambridge University Press.

Blanke, O., & Metzinger, T. (2009). Full-body illusions and minimal phenomenal selfhood. *Trends in Cognitive Sciences*, 13(1), 7-13.

Borsboom, D., Mellenbergh, G. J., & van Heerden, J. (2004). The concept of validity. *Psychological Review*, 111(4), 1061-1071.

Campbell, D. T., & Fiske, D. W. (1959). Convergent and discriminant validation by the multitrait-multimethod matrix. *Psychological Bulletin*, 56(2), 81-105.

Cronbach, L. J., & Meehl, P. E. (1955). Construct validity in psychological tests. *Psychological Bulletin*, 52(4), 281-302.

Dehaene, S., & Changeux, J.-P. (2011). Experimental and theoretical approaches to conscious processing. *Neuron*, 70(2), 200-227.

Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127-138.

Gallagher, S. (2000). Philosophical conceptions of the self: implications for cognitive science. *Trends in Cognitive Sciences*, 4(1), 14-21.

Gamez, D. (2008). Progress in machine consciousness. *Consciousness and Cognition*, 17(3), 887-910.

Haladjian, H. H., & Montemayor, C. (2016). Artificial consciousness and the consciousness-attention dissociation. *Consciousness and Cognition*, 45, 210-225.

Haggard, P., Clark, S., & Kalogeras, J. (2002). Voluntary action and conscious awareness. *Nature Neuroscience*, 5(4), 382-385.

Moore, J. W., & Fletcher, P. C. (2012). Sense of agency in health and disease: a review of cue integration approaches. *Consciousness and Cognition*, 21(1), 59-68.

Reggia, J. A. (2013). The rise of machine consciousness: Studying consciousness with computational models. *Neural Networks*, 44, 112-131.

Seth, A. K. (2013). Interoceptive inference, emotion, and the embodied self. *Trends in Cognitive Sciences*, 17(11), 565-573.

Synofzik, M., Vosgerau, G., & Newen, A. (2008). Beyond the comparator model: a multifactorial two-step account of agency. *Consciousness and Cognition*, 17(1), 219-239.

Tsakiris, M. (2010). My body in the brain: a neurocognitive model of body-ownership. *Neuropsychologia*, 48(3), 703-712.
