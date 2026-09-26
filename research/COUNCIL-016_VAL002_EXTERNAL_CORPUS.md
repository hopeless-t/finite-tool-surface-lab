# COUNCIL-016 — Advance VAL-002 Before BENCH-003

## Trigger

BENCH-003 needs an external catalogue with natural redundancy, aliases, and near-name negatives.

DOGFOOD-001 showed that pmndrs/math is a manageable external candidate.

## Candidates

A. Advance VAL-002 and qualify the external catalogue adapter first.  
B. Build the adapter inline inside BENCH-003.  
C. Keep BENCH-003 synthetic-only and defer external evidence.  
D. Jump directly to Worker-in-the-loop evaluation.

## Council

A separates adapter correctness from distractor science.

B is faster initially but confounds extraction bugs with benchmark findings.

C preserves causal control but misses the available external-validity dogfood.

D adds too many variables before the retrieval layer is understood.

## 250k synthetic planning sensitivity

Seed: 2026092612.

Criteria:
- causal isolation;
- external validity;
- reproducibility;
- future reuse;
- dogfood value;
- iteration velocity;
- compute cost.

Result:

```text
A qualify VAL-002 first    100.0000%
B inline adapter             0.0000%
C synthetic only             0.0000%
D Worker immediately         0.0000%
```

Mean utility:

```text
A 0.9131
B 0.7994
C 0.7556
D 0.5068
```

Planning robustness only.

## New invariant

```text
Similar Tool != Wrong Tool
Valid Alternative != Distractor
```

The external corpus must preserve function-identity alias equivalence rather than converting every similar name into a negative example.

## Decision

```text
QUALIFY_EXTERNAL_CORPUS_BEFORE_BENCH003
```
