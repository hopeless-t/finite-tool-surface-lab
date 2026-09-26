# COUNCIL-014 — BENCH-002 Result Interpretation

## Evidence in hand

### Full benchmark

Optimized full run:

```text
run = 36233741224
source = 6268d7c6ef51ddbb5d1a25467446fd02c1855096
state = PASS
policy observations = 314,496
aggregate rows = 3,276
frontier points = 835
adaptive frontier points = 542
observation sha256 =
b2070ee08502491498ced1862cf0b586bb79fddbbb1b9ee4faaf2ce395b86aeb
```

### Compute-equivalence check

The first full run and optimized full run produced byte-identical stable outputs:

```text
aggregates.jsonl
frontier.json
msts.json
observation_digest.json
summary.json
```

Only runtime-specific manifest identity changed.

The optimized benchmark step fell from about 70.14 s to 54.14 s on separate GitHub-hosted runs, a descriptive reduction of about 22.8%.

This is an implementation observation, not a stable performance benchmark.

## Main synthetic result

Across all 96 tool-required aggregate conditions:

```text
RELATIVE_TOP:0.9
all_gold_rate min = 1.0
mean selected k ~= 11.973
mean surface bytes ~= 1,521
```

Reference FULL:

```text
all_gold_rate = 1.0
mean selected k = 680
mean surface bytes ~= 85,783
```

Reference FIXED_K:32:

```text
mean all_gold_rate ~= 0.9159
mean surface bytes ~= 3,795
```

All adaptive policies returned an empty surface for zero-evidence no-tool tasks.

## High-ambiguity example

For N=2048 multi-tool tasks at overlap 0.50 / 0.75:

`RELATIVE_TOP:0.9` preserved exact coverage by expanding to roughly 90 candidates on average.

This is larger than fixed k=50, but still only about 4.4% of FULL serialized exposure.

Thus the important result is not:

```text
adaptive always means smaller k
```

It is:

```text
adaptive depth can stay tiny when evidence is sharp
and expand when evidence is ambiguous
```

## Threshold identity caveat

All RELATIVE_TOP thresholds in the frozen sweep achieved exact coverage.

Within every tool-required condition, `RELATIVE_TOP:0.9` weakly dominated the looser relative thresholds on coverage/cost.

But many threshold values produced exactly the same operating point because Jaccard scores are discrete.

```text
Hyperparameter Distinct
!= Behavioral Operating Point Distinct
```

Therefore BENCH-002 does not establish 0.9 as a universal threshold.

## Workload-mixture Monte Carlo

Run:

`36233978830`

Artifact:

`10903920371`

Artifact digest:

`sha256:6e12c6f8eb669368ac45b8b0e0ae63e35868e03e1cb954d5a138d7064b98a9ea`

60,000 random workload mixtures and 300,000 constrained policy selections were evaluated over three Dirichlet concentration regimes.

For epsilon <= 0.01:

`RELATIVE_TOP:0.9` was selected in 100% of mixtures in all three regimes.

At epsilon = 0.05, its selection frequency ranged from about 87.8% to 96.6%, with `LARGEST_SCORE_DROP` taking most of the remainder.

At epsilon = 0.10, the tradeoff widened; `LARGEST_SCORE_DROP` became competitive in more concentrated workloads.

## Failure-path observation

The first MC workflow attempt failed before calculation because the repository package had not been installed.

That failure is recorded in:

`research/FAILURE-001_BENCH002_MC_IMPORT.md`

No scientific output was produced by the failed run.

## Decision candidates

A. Promote BENCH-002 as evidence that adaptive evidence-responsive depth can improve the synthetic retrieval/surface frontier, while prohibiting universal threshold claims.  
B. Promote `RELATIVE_TOP:0.9` as the universal policy.  
C. Reject BENCH-002 because the generator is synthetic.  
D. Skip reference promotion and move directly to Worker-in-the-loop.

## Council

**A — selected.**

The benchmark is internally strong, replayable, and directly answers its frozen synthetic question.

B exceeds the evidence.

C throws away a useful controlled result merely because external validity is intentionally bounded.

D would skip the planned distractor/representation research needed before Worker conclusions.

## Claim ceiling

```text
BENCH-002 supports:
adaptive score-responsive depth can dominate fixed depth
under the frozen synthetic ranking/generator conditions.

BENCH-002 does not support:
RELATIVE_TOP:0.9 is universally optimal;
the same result holds for embedding/reranking models;
the same result holds for real MCP registries;
the same result improves LLM Worker task success.
```

## Decision

```text
PROMOTE_AFTER_CROSS_PYTHON_EXACT_REPLAY
```
