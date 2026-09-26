# BENCH-001 — Fixed-k Surface Sweep

## Question

How do coverage and exposed Tool-surface cost change as a deterministic candidate surface grows under controlled registry size and semantic overlap?

## Scope

BENCH-001 is intentionally pre-Worker.

```text
BENCH-001 Result
!=
End-to-End Worker Result
```

## Policies

- ORACLE;
- FULL;
- RANDOM-k;
- TOKEN-JACCARD top-k deterministic lexical baseline.

The lexical baseline is intentionally transparent. Embeddings and learned rerankers are deferred until a reference surface curve exists.

## k sweep

```text
1, 2, 3, 5, 8, 13, 20, 32, 50
```

Values above registry size are recorded as invalid cells and are never silently clipped.

## Factors

- registry size;
- overlap level;
- alias rate;
- task type.

## Observables

- mean relevant-tool recall;
- any-gold coverage;
- exact all-gold coverage;
- candidate count;
- serialized surface bytes;
- no-tool non-empty-surface rate;
- empirical RANDOM-k vs exact chance expectation;
- Bits-over-Random for any-gold coverage;
- deterministic retrieval/surface frontier.

## Random baseline

A 250,000-experiment public design Monte Carlo established that 64 empirical RANDOM-k repeats per exact cell are too noisy to define the chance baseline across the entire sweep.

Therefore:

```text
Empirical RANDOM-k = negative control
Exact hypergeometric expectation = chance baseline
```

For an any-gold success rule, the secondary chance-corrected metric is:

```text
BoR = log2(P_observed / P_random)
```

where `P_random` is the exact hypergeometric chance probability at the same N, k, and gold-count.

## Retrieval frontier

The BENCH-001 frontier is a **retrieval/surface frontier**, not the full North-star Tool Surface Frontier.

It maximizes exact all-gold coverage while minimizing:
- mean visible Tool count;
- mean serialized surface bytes.

ORACLE is excluded from dominance calculations because it uses unavailable gold knowledge.

## Claim ceiling

BENCH-001 may establish synthetic retrieval/surface behavior.

It may not establish that a smaller surface improves an actual AI Worker. That requires a later Worker-in-the-loop benchmark.
