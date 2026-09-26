# North-star — Tool Surface Frontier

## Decision

The North-star is not one scalar accuracy score.

It is the **Tool Surface Frontier (TSF)**: the non-dominated frontier between end-to-end task utility and the cost/risk of the active tool surface.

## Formal objects

Let:

- U = full tool registry;
- q = task/query;
- G(q) = gold relevant tool set;
- pi(q,U) = surface policy returning S(q), a subset of U;
- Y(q,S) = end-to-end task success or utility;
- C_count(S) = number of visible tools;
- C_bytes(S) = serialized surface bytes;
- C_tokens(S,m) = serialized tokens under tokenizer/model m.

Latency, provider cost, wrong-tool invocation, and no-tool false invocation are recorded separately.

## Tool Surface Frontier

For each policy / operating point, report at least:

- end-to-end success;
- candidate count;
- serialized exposure;
- gold coverage;
- wrong-tool invocation;
- no-tool false invocation;
- latency/cost when applicable.

A point is dominated if another point is no worse on all declared dimensions and better on at least one.

## MSTS(epsilon)

For tolerance epsilon, delta, and alpha, find the smallest expected surface satisfying:

```text
end_to_end_success >= oracle_surface_success - epsilon
gold_coverage       >= 1 - delta
no_tool_false_call  <= alpha
```

Report separate variants for candidate-count and serialized-token exposure.

Initial analysis grid:

```text
epsilon = {0, .01, .02, .05, .10}
delta   = {0, .01, .05, .10}
alpha   = {0, .01, .05, .10}
```

These are research coordinates, not product requirements.

## Mandatory baselines

- ORACLE: exactly the gold relevant set;
- FULL: entire registry;
- RANDOM-k: chance control;
- FIXED-k: deterministic top-k;
- ADAPTIVE-k: query-specific shortlist depth.

`FULL != ORACLE`

## Anti-Goodhart rule

No headline claim may rely on candidate count alone.

Any claimed surface improvement must report success, exposure, coverage, and false/wrong invocation behavior together.
