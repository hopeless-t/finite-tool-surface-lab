# COUNCIL-017 — BENCH-003 Execution Order

## Fresh readback

VAL-002 is already PASS / REFERENCE / CLOSED.

Pinned external catalogue:

~~~text
math@0.1.0
tool_count = 384
alias equivalence groups = 35
cross-type homonym groups = 71
catalog sha256 =
98fdcda9561222de0ed0a074e4572760f007b3471fc5a4241c4ac34e719866ba
Node 20 / Node 22 = BYTE_IDENTICAL
~~~

Therefore BENCH-003 Lane B is no longer blocked.

## Question

Which bounded implementation order gives the strongest next evidence?

A. Implement canonical synthetic Lane A first, then attach external Lane B.
B. Implement external pmndrs Lane B first.
C. Implement both in parallel.
D. Skip to Worker-in-the-loop.

## Council

**A — selected.**

Lane A is the controlled causal experiment frozen by BENCH-003. It isolates distractor topology while total menu size stays constant and capability identity is preserved.

Lane B now has a qualified adapter, but remains external-validity evidence. It is strongest after the metric/evidence contract is exercised on Lane A.

Parallel execution increases orchestration load before the core benchmark contract is proven.

Worker-in-loop remains premature.

## 250k synthetic planning sensitivity

Seed: 2026092611.

Criteria:
- canonical evidence value;
- blocking reduction;
- reproducibility;
- compute efficiency;
- failure isolation;
- external validity.

Result:

~~~text
A Lane A first       99.2476%
B Lane B first        0.5544%
C parallel            0.1980%
D Worker now          0.0000%
~~~

Mean utility:

~~~text
A 0.9143
B 0.8474
C 0.8375
D 0.5010
~~~

Planning robustness only.

## Decision

~~~text
NEXT BOUNCE =
BENCH-003 LANE A IMPLEMENTATION

AFTER LANE A QUALIFICATION =
ATTACH VAL-002-PINNED LANE B
~~~
