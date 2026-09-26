# COUNCIL-018 — BENCH-003 Lane A Generator Architecture

## Question

How should the controlled synthetic distractor benchmark construct matched Tool registries without repeating BENCH-001's identity-erasure artifact?

## Candidates

A. Task-conditioned fixed-N registry with explicit capability signatures and targeted replacement.
B. One global registry per N, then perturb metadata around sampled tasks.
C. Patch BENCH-001 generator v0.1 with more distractor labels.
D. Use only the external pmndrs catalogue.

## Council

**A — selected.**

Each task condition gets a deterministic registry of exact size N.

Required capabilities receive explicit query signatures that:
- are present in canonical and valid-equivalent Tools;
- remain present in the query;
- are absent from wrong distractors.

Targeted distractors replace random background Tools, so menu size remains constant.

B has good compute reuse but makes controlled per-capability distractor density harder to isolate.

C risks inheriting the v0.1 prefix-identity artifact.

D cannot replace the canonical controlled lane.

## 250k synthetic planning sensitivity

Seed: 2026092612.

Criteria:
- causal isolation;
- gold identity preservation;
- equivalence correctness;
- compute efficiency;
- reproducibility;
- implementation simplicity.

Result:

~~~text
A task-conditioned fixed-N   99.1208%
B global registry perturb     0.8792%
C patch v0.1                  0.0000%
D external only               0.0000%
~~~

Mean utility:

~~~text
A 0.9368
B 0.8857
C 0.7220
D 0.7386
~~~

Planning robustness only.

## Adversarial score shape

The generator deliberately creates several wrong-distractor score regimes.

For example, RISKY_RELEVANT shares every query token except the capability signature.

Thus the benchmark can make a distractor highly retrieval-relevant while it remains capability-wrong.

~~~text
High Retrieval Score
!= Valid Capability
~~~

## Evidence model

The full frozen design contains exactly:

~~~text
23,040 task conditions
x 21 policy operating points
= 483,840 policy observations
~~~

Observations are streamed into aggregates and one canonical SHA-256 digest.

## Decision

~~~text
TASK_CONDITIONED_FIXED_N
+
CAPABILITY_SIGNATURE_PRESERVATION
+
TARGETED_REPLACEMENT
+
STREAMING_EVIDENCE
~~~
