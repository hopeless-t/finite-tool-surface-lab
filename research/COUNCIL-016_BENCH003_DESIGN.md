# COUNCIL-016 — BENCH-003 Design Freeze

## Question

What is the strongest bounded next benchmark after BENCH-001 fixed-k and BENCH-002 adaptive-k?

## Fresh intake

Current public work provides three useful signals:

1. ToolChoiceConfusion / CMTF — semantic relevance alone is insufficient; premature/state-inappropriate Tools matter.
2. ToolMenuBench — public artifacts separate semantic, near-duplicate, schema-compatible, premature, risky, cross-domain, and mixed distractors.
3. MCPAgentBench — real MCP definitions plus dynamic distractor lists provide an external-validity path.

DOGFOOD-001 additionally provides a naturally redundant public catalogue candidate through pmndrs/math.

## Candidate designs

A. Two-lane design: controlled synthetic topology/equivalence study + external pmndrs lane gated by VAL-002.
B. Semantic-similarity-only synthetic benchmark.
C. External benchmark/corpus only.
D. Skip directly to Worker-in-the-loop distractor evaluation.
E. Copy ToolMenuBench taxonomy without equivalence-aware changes.

## Pseudo-Council

Causal experimentalist -> A.
Keep total registry size fixed while replacing random irrelevant Tools with targeted distractors.

Tool semantics -> A.
Ground truth must be capability-equivalence-aware.

Agent safety -> A.
Premature and risky Tools remain separately measurable.

External validity -> A with VAL-002 gate.
Synthetic and real-catalogue evidence must not masquerade as each other.

Compute efficiency -> A.
Keep first full benchmark pre-Worker and deterministic; stream evidence.

Claim safety -> A.
Do not generalize synthetic thresholds into production rules.

## 250k synthetic planning sensitivity

Seed: 2026092610.

Criteria:
- causal isolation;
- external validity;
- equivalence correctness;
- reproducibility;
- compute efficiency;
- claim safety;
- future Worker bridge.

Result:

~~~text
A two-lane + gated external          100.0000%
E imported taxonomy only               0.0000%
B semantic-only synthetic              0.0000%
C external-only                        0.0000%
D Worker-in-loop now                   0.0000%
~~~

Mean utility:

~~~text
A 0.9404
E 0.7598
B 0.7530
C 0.6736
D 0.5546
~~~

Planning robustness only.

## Frozen design decisions

1. Primitive axes before named categories.
2. Total registry size remains constant in matched interventions.
3. Ground truth is capability-equivalence-aware.
4. Gold identity cannot be erased by query construction.
5. pmndrs/math external lane is gated by VAL-002.
6. First implementation remains pre-Worker and requires no paid provider.

## Projected deterministic workload

~~~text
3 seeds
x 4 N
x 3 task types
x 8 stress families
x 5 targeted densities
x 16 repeats
= 23,040 tasks
~~~

Approximately 20 policy operating points imply roughly 460k policy observations.

Measure one-job runtime before deciding whether sharding is justified.

## Decision

~~~text
BENCH-003 DESIGN = FROZEN

LANE A =
CONTROLLED DISTRACTOR TOPOLOGY
+
CAPABILITY EQUIVALENCE
+
CONSTANT MENU SIZE

LANE B =
PINNED EXTERNAL CATALOGUE
+
VAL-002 GATE
~~~
