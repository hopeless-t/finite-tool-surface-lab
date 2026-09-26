# COUNCIL-021 — BENCH-004 Design Freeze

## Trigger

BENCH-003 closed with strong synthetic evidence that downstream depth selection does not robustly solve no-tool exposure.

Frozen result:

~~~text
coverage >= 0.99

no-tool false-surface <= 5%
0 / 60,000 workload mixtures feasible

<= 10%
1 / 60,000 feasible
~~~

## Question

What should the next bounded experiment isolate?

## Candidate architectures

A. Binary top-score admission threshold before depth selection.

B. Tri-state Tool-Need Admission Gate with:
- ADMIT_TOOL_SURFACE;
- NO_TOOL_SURFACE;
- DEFER;
- retrieval-isomorphic matched pairs;
- transparent provider-independent baselines;
- downstream surface composition;
- future shadow Decision Provider lane.

C. Add a NO_TOOL sentinel directly to one relative Tool-choice problem.

D. Skip architecture isolation and test a Worker/provider end to end.

E. Import BFCL relevance/irrelevance as the benchmark without a controlled synthetic lane.

## Pseudo-Council

### Causal experimentalist -> B

Retrieval-isomorphic pairs directly test the architectural claim.

The admission state changes while the ranking evidence stays exactly fixed.

### Tool-surface seat -> B

First decide whether a surface should exist. Then optimize its depth.

### Jev/Cua seat -> B

The seam maps cleanly to an absolute bounded decision. Provider choice should remain replaceable.

### Safety / authority seat -> B

Admission may suppress or propose a surface. It cannot grant execution authority.

### Human-factors seat -> B

DEFER prevents forced binary decisions under insufficient evidence and gives future Ringi/Human escalation a typed path.

### Benchmark-validity seat -> B with external audit

BFCL relevance/irrelevance is useful external evidence, but should not become the sole canonical basis. A recent external audit raises enough dataset-quality concern to require an explicit corpus audit.

### Anti-Goodhart seat -> B

Report the full frontier over:
- required-admit recall;
- no-tool false admission;
- defer rate;
- downstream exposure.

Do not select one threshold and label it universal.

## 250k planning sensitivity

Seed: 2026092620.

Criteria:

- causal isolation;
- no-tool safety;
- required-tool recall;
- calibration support;
- provider portability;
- claim safety;
- implementation efficiency;
- Jev/Cua fit.

~~~text
B tri-state admission          98.0196%   mean utility 0.9436
A binary threshold             1.9800%   mean utility 0.8808
C choice + NO_TOOL sentinel    0.0004%   mean utility 0.7565
E BFCL-only                    0.0000%   mean utility 0.6816
D Worker/provider now          0.0000%   mean utility 0.4895
~~~

Planning robustness only.

This is not a technical-success, model-accuracy, or safety probability.

## Frozen anti-shortcut invariant

~~~text
Retrieval Evidence Isomorphic
!= Admission Semantics Equivalent
~~~

Matched ADMIT / NO_TOOL conditions receive identical registry/retrieval-score evidence.

Only the admission state differs.

This prevents a top-score threshold from winning by construction.

## Frozen gate input

The canonical controlled lane exposes noisy structured evidence:

- external-state dependency;
- side-effect intent;
- local-context sufficiency;
- precondition readiness;
- user Tool permission;
- intent clarity;
- menu relevance.

It never exposes the truth label.

## Frozen truth contract

~~~text
ADMIT_TOOL_SURFACE
NO_TOOL_SURFACE
DEFER
~~~

DEFER is separately reported and constrained.

~~~text
Abstention
!= Correctness
~~~

## Provider boundary

The first implementation remains provider-free.

A future shadow lane may plug in:

- Jev;
- Cua;
- local classifier;
- LLM judge;
- deterministic rule.

The provider emits an admission signal only.

~~~text
Provider Qualified
!= Provider Adopted
!= Tool Authorized
~~~

Paid/provider execution requires separate Human approval.

## Decision

~~~text
BENCH-004 DESIGN = FROZEN

CANONICAL LANE =
CONTROLLED TRI-STATE ADMISSION
+
RETRIEVAL-ISOMORPHIC PAIRS
+
PROVIDER-INDEPENDENT BASELINES
+
DOWNSTREAM SURFACE COMPOSITION

EXTERNAL LANES =
BFCL relevance/irrelevance after corpus audit
Decision Provider shadow after provider qualification/approval
~~~

Implementation is deliberately deferred to the next bounce.
