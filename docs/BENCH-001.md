# BENCH-001 — Fixed-k Surface Sweep

## Question

How do coverage and exposure change as a deterministic candidate surface grows under controlled registry size and semantic overlap?

## Scope

BENCH-001 is intentionally pre-Worker.

`BENCH-001 Result != End-to-End Worker Result`

## Policies

- ORACLE;
- FULL;
- RANDOM-k;
- TOKEN-JACCARD top-k deterministic lexical baseline.

The lexical baseline is intentionally simple and transparent.

## k sweep

```text
1, 2, 3, 5, 8, 13, 20, 32, 50
```

Values above registry size are invalid for that cell and are not silently clipped.

## Factors

- registry size;
- overlap level;
- alias rate;
- task type.

## Observables

- Hit/Recall@k;
- exact gold-set coverage;
- candidate count;
- serialized surface bytes;
- random baseline gap;
- retrieval wall time as descriptive data.

## Claim ceiling

BENCH-001 may establish a retrieval/surface frontier.

It may not establish that a smaller surface improves actual Worker tool selection. That requires a later Worker-in-the-loop benchmark.
