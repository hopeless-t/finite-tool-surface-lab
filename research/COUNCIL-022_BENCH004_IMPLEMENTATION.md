# COUNCIL-022 — BENCH-004 Implementation Architecture

## Question

How should the frozen tri-state admission design be implemented without leaking truth labels or accidentally reintroducing retrieval shortcuts?

## Candidate implementations

A. Task-conditioned paired generator with exact shared registry/query bytes for each retrieval-isomorphic pair, separate noisy admission-state features, provider-free transparent baselines, and downstream surface composition.

B. Reuse BENCH-003 generator and append an admission label.

C. Generate independent ADMIT and NO_TOOL cases that merely have similar score distributions.

D. Train a small classifier immediately.

## Pseudo-Council

### Causal experimentalist -> A

Exact pair identity is stronger than distributional similarity.

### Benchmark-validity seat -> A

Truth must be recomputable by the harness but absent from gate input.

### Jev/Cua seat -> A

Provider-free baselines should establish the seam before any provider comparison.

### Tool-surface seat -> A

Gate decisions must be composed with real downstream BENCH-003 policies, not evaluated in isolation only.

### Authority seat -> A

Every observation carries authority_effect = NONE. Admission never becomes execution permission.

### Compute seat -> A

27,648 deterministic tasks x 16 gate operating points x 2 downstream policies = 884,736 observations. Streaming aggregation keeps memory bounded.

## 250k planning sensitivity

Seed: 2026092621.

Criteria:

- pair exactness;
- truth leakage resistance;
- causal isolation;
- provider portability;
- compute efficiency;
- downstream realism;
- claim safety.

~~~text
A exact paired generator      99.8728%   mean utility 0.9608
C score-distribution pairs     0.1272%   mean utility 0.8756
B patch BENCH-003              0.0000%   mean utility 0.7235
D train classifier now         0.0000%   mean utility 0.6212
~~~

Planning robustness only.

## Frozen implementation choices

- Retrieval-isomorphic pairs share exact registry/query construction keys.
- Admission-state features are noisy but truth labels are never exposed.
- Retrieval-only threshold policies are retained as negative controls.
- RULE_GATE_V0 and LINEAR_NEED_SCORE_BANDS are transparent baselines.
- DEFER remains a distinct outcome and is never counted as successful admission.
- ADMIT composes with RELATIVE_TOP:0.9 and LARGEST_SCORE_DROP.
- NO_TOOL and DEFER force an empty surface.
- Provider calls = 0.
- Authority effect = NONE.

## Decision

~~~text
IMPLEMENT BENCH-004 CANONICAL SYNTHETIC LANE
WITH EXACT RETRIEVAL-ISOMORPHIC PAIRS
AND PROVIDER-FREE BASELINES
~~~

This grants no authority for paid/model-provider execution.
