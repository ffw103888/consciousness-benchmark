# FAQ

## Is this claiming that an AI system is conscious?

No. The project validates operational constructs such as action agency,
boundary self, identity-temporal self, action ownership, and distributed
body-schema self. These are measurable computational and behavioral constructs,
not reports of subjective experience.

## Why does the paper emphasize measurement validation?

The central claim is methodological: theoretically motivated internal proxies
can measure the wrong process unless they are checked against independent
behavioral probes. The agency proxy initially measured gating activity rather
than action-outcome control. After separating those processes, proxy-test
agreement recovered.

## Why did action agency drop from 0.874 in the frozen analysis to 0.727 in the 16-seed robustness check?

The 16-seed run is a supplementary robustness check with a larger sample. The
drop is consistent with regression toward a less optimistic population estimate.
The important point is that action agency remains above the working validation
threshold (`r >= 0.7`) and the action-loop mechanism effect remains intact.

## Why does Transformer boundary self fail?

Transformer workspace manipulations affect internal boundary-related proxies,
but those changes do not reliably map onto independent boundary behavior. The
paper treats this as measurement-limited evidence, not as proof that
Transformers lack every possible form of self-model.

## What is the high-agency / low-boundary Transformer profile?

Some Transformer conditions show strong predictive action control while lacking
validated boundary-self behavior. This is treated as an exploratory
architecture-specific profile, not as a new validated construct.

## Can I run the benchmark on my own system?

Yes. The benchmark expects an adapter that exposes proxy measurements and
independent test outputs. Start with the quickstart and examples:

```powershell
python examples\01_reference_quickstart.py
python examples\02_online_mind_lab_minimal.py
```

For custom systems, implement the adapter surface used by
`consciousness_benchmark`.

## Do I need to rerun the long experiments to reproduce the paper?

No. The paper uses frozen statistics and compact preserved raw tables under
`docs/paper/statistics/`. The ignored `runs/` directories are not required for
the public reference benchmark or figure scripts.

## How should I cite this work?

Use the repository `CITATION.cff` or the BibTeX entry in the README. The arXiv
identifier should be filled in after the preprint is public.
