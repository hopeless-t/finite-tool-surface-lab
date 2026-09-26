# Threats to Validity

## BENCH-001

### Synthetic grammar

The registry/task grammar is intentionally synthetic and does not represent the full linguistic or schema complexity of real MCP/Tool ecosystems.

### Overlap is not a universal threshold

Generator v0.1 maps overlap to a discrete count of shared description tokens.

For multi-tool tasks, the query takes the first four description tokens from each selected tool. At overlap >= 0.50 those four tokens are all shared, so exact tool-specific identity is absent from that query prefix.

Therefore:

```text
BENCH-001 overlap transition
!= universal semantic-overlap transition
```

It is a controlled information-ambiguity regime.

### Single-tool query visibility

Single-tool queries retain five shuffled tokens from ten. As overlap increases, the probability that no tool-unique token is present rises.

This means part of the observed surface expansion is directly caused by reduced query information, which is useful for stress testing but must not be attributed only to retriever weakness.

### Alias-rate semantics

Aliases are added to candidate metadata, while query generation currently samples `description_tokens` and does not generate alias queries.

Thus BENCH-001 does not measure alias-query resolution.

### Lexical baseline

TOKEN_JACCARD is deliberately transparent, deterministic, and weak. It is a reference baseline, not a claim about modern embedding or reranking systems.

### RANDOM-k sampling noise

The empirical RANDOM-k control uses 64 repeats per exact cell and is noisy. The public 250k design Monte Carlo shows that the maximum absolute error across cells can be materially larger than individual-cell intuition suggests.

The exact hypergeometric expectation is the primary chance baseline.

### Pre-Worker claim ceiling

BENCH-001 measures retrieval/surface behavior.

```text
Gold present in surface
!= Worker selects gold
!= valid Tool call
!= task success
```

No end-to-end Worker conclusion may be drawn from BENCH-001 alone.
