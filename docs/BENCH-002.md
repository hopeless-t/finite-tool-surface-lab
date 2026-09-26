# BENCH-002 — Adaptive-k Surface Policies

## Question

Can transparent query-specific depth policies improve the retrieval/surface frontier over fixed-k when all policies use the same deterministic TOKEN_JACCARD ranking?

## Frozen mechanism

BENCH-002 reuses synthetic generator v0.1 and TOKEN_JACCARD from BENCH-001.

This is deliberate:

```text
BENCH-001 -> fixed depth
BENCH-002 -> adaptive depth

ranking mechanism held constant
```

The BENCH-001 information-ambiguity and alias caveats remain active.

## Policy families

Reference:
- ORACLE;
- FULL;
- FIXED_K.

Adaptive:
- POSITIVE_SUPPORT;
- RELATIVE_TOP(theta);
- CUMULATIVE_SCORE_MASS(tau);
- LARGEST_SCORE_DROP.

### Shared zero-evidence rule

If the best score is zero, adaptive policies return an empty surface.

### Tie safety

An adaptive cutoff must never split an equal-score block.

```text
Adaptive Depth != Arbitrary Tie Break
```

If a threshold lands inside a tied block, include the complete tie block.

## Why a frontier, not one winner

Threshold sweeps are retained as operating points.

No threshold is selected after observing the evaluation set.

This avoids:

```text
Evaluate Many Thresholds
-> Pick Best On Same Data
-> Pretend It Was A Priori
```

The result is a policy frontier, not one universal adaptive-k constant.

## Evaluation

Three deterministic seeds, 32 repeats per exact condition.

Metrics:
- mean selected k;
- serialized surface bytes;
- mean gold recall;
- any-gold rate;
- all-gold rate;
- no-tool nonempty-surface rate;
- exact chance expectation at each selected k;
- Bits-over-Random where defined;
- Pareto frontier;
- retrieval MSTS(epsilon).

## Evidence efficiency

Policy observations are streamed into aggregate statistics.

Every canonical observation row contributes to a SHA-256 stream digest.

The benchmark persists:
- aggregate rows;
- frontier;
- MSTS summaries;
- observation count + digest;
- manifest;
- summary.

It does not persist the full per-policy observation stream by default.

```text
Raw Rows Not Persisted
!= Raw Computation Unbound
```

Independent replay is expected to reproduce both aggregate files and observation digest.

## Claim ceiling

```text
Adaptive Retrieval Surface Result
!= Worker Tool Selection Result
!= Valid Tool Call
!= End-to-End Task Success
```
