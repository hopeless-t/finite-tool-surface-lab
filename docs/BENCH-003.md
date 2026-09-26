# BENCH-003 — Distractor Topology & Equivalence Stress

## Question

How do different kinds of plausible-but-wrong Tools, state-inappropriate Tools, risky Tools, and valid-equivalent alternatives change the active Tool Surface required to preserve capability?

## Core correction

~~~text
Similar Tool != Wrong Tool
Alternative Tool != Distractor Automatically
Relevant Tool != Appropriate Next Tool
Schema Compatible != Capability Equivalent
~~~

BENCH-003 moves beyond one scalar similarity axis.

## Atomic distractor axes

The synthetic generator models six primitive relations:

1. semantic proximity — far vs near;
2. schema overlap — low vs high;
3. state validity — valid now vs premature;
4. risk — low vs high;
5. domain relation — cross-domain vs same-domain;
6. capability relation — wrong vs valid-equivalent.

Named stress families are constrained combinations of these axes.

## Constant-menu intervention

For matched conditions, total registry size stays fixed.

Targeted distractors replace random irrelevant Tools rather than enlarging the registry.

~~~text
More Targeted Distractors
!= Larger Tool Menu
~~~

This isolates distractor topology from menu-size effects already studied in BENCH-001/002.

## Synthetic stress families

- RANDOM_IRRELEVANT
- SEMANTIC_NEAR
- SCHEMA_COMPATIBLE
- PREMATURE_STATE
- RISKY_RELEVANT
- CROSS_DOMAIN_HOMONYM
- VALID_EQUIVALENT
- MIXED

VALID_EQUIVALENT is not a wrong distractor. Retrieval of a valid equivalent counts as valid capability coverage.

## Ground truth

Tasks declare required capability IDs.

Each capability may map to one or more valid Tool IDs.

~~~text
Canonical ID Miss
+ Valid Equivalent Present
= Capability Covered
~~~

## Gold identity preservation

Every required capability must retain explicit discriminating evidence in the synthetic query representation.

Targeted distractors may approach that evidence but may not erase it.

## Policies

Carry forward FULL, fixed-k, POSITIVE_SUPPORT, RELATIVE_TOP, CUMULATIVE_SCORE_MASS, and LARGEST_SCORE_DROP.

RELATIVE_TOP:0.9 is retained only as a preregistered BENCH-002 reference point, not as a universal winner.

## Metrics

Tool-required:
- equivalence-aware any-valid coverage;
- equivalence-aware all-required-capability coverage;
- wrong-distractor inclusion rate;
- distractor burden;
- premature-tool exposure;
- risky-wrong-tool exposure;
- mean selected k;
- serialized surface bytes.

Equivalent-alternative:
- valid-alternative recovery;
- canonical-ID sensitivity;
- equivalence fragmentation;
- redundant-equivalent burden.

No-tool:
- nonempty-surface rate.

## Planned computation

~~~text
3 seeds
x 4 registry sizes
x 3 task types
x 8 stress families
x 5 targeted-distractor densities
x 16 repeats
= 23,040 task conditions before policy expansion
~~~

With about 20 policy operating points, the full benchmark is expected to produce roughly 460k policy observations.

Observations should be streamed into aggregates plus an exact canonical SHA-256 observation digest.

## External Lane B

Candidate: pmndrs/math@0.1.0.

Lane B is gated by VAL-002. The external catalogue cannot become BENCH-003 evidence until adapter identity, equivalence labels, homonyms, and cross-Node replay are independently qualified.

Synthetic Lane A may proceed independently.

## Claim ceiling

BENCH-003 may characterize retrieval/surface robustness to frozen distractor topology and equivalence structure.

It may not establish Worker task success, safe authorization, a universal distractor taxonomy, a universal adaptive threshold, or production MVCA policy.
