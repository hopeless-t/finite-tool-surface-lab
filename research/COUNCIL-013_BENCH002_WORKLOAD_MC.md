# COUNCIL-013 — BENCH-002 Workload-Mixture Monte Carlo

## Question

A policy can look good under an equal average of benchmark cells. Does that conclusion survive uncertain workload composition?

## Method

Use the completed optimized BENCH-002 aggregate artifact as fixed empirical condition data.

Tool-required conditions:

```text
4 registry sizes
x 4 overlap levels
x 3 alias rates
x 2 task types
= 96 conditions
```

Only policy variants present in every condition are eligible for this global comparison.

ORACLE is excluded.

FIXED_K:50 is excluded because it is invalid at N=32 under the frozen no-clipping rule.

## Workload uncertainty

Draw workload weights over the 96 conditions from symmetric Dirichlet distributions.

```text
alpha = 0.25  highly concentrated / heterogeneous
alpha = 1.0   broad random mixtures
alpha = 4.0   closer to balanced mixtures
```

20,000 mixtures per alpha.

For each mixture and each:

```text
epsilon = 0, .01, .02, .05, .10
```

choose the candidate with minimum weighted serialized surface bytes subject to:

```text
weighted exact all-gold coverage >= 1 - epsilon
```

This gives:

```text
60,000 random workload mixtures
300,000 constrained policy selections
```

## Why NumPy here

The research package remains stdlib-only.

NumPy is installed only inside this analysis workflow because batched Dirichlet sampling and dense matrix multiplication are mature numerical computation that should be borrowed rather than reimplemented.

```text
Research Calculation Tool
!= Runtime Dependency
```

## Claim ceiling

This Monte Carlo measures robustness to synthetic workload composition over observed BENCH-002 aggregate cells.

It does not model real production traffic and does not establish Worker performance.
