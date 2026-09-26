# COUNCIL-004 — VAL-001 Method

## Question

What should qualify the Tool Surface research apparatus before Worker/model experiments begin?

## Candidates

A. Deterministic structured synthetic registry with exact known-answer controls.  
B. Public external benchmark first.  
C. LLM-generated synthetic registry.  
D. Live MCP/tool environment first.

## Council

A provides the strongest causal control, exact gold labels, byte-repeatability, and analytic RANDOM-k reference.

B has better immediate external validity but mixes in benchmark/task/environment confounds before the apparatus is qualified.

C adds generator-model uncertainty where deterministic generation is sufficient.

D maximizes realism but is inappropriate for harness qualification because live Tool state is volatile.

## Post-finite-ram intake planning sensitivity

250,000 synthetic draws, seed 2026092601.

```text
A deterministic known-answer first   99.9948%
B public benchmark first              0.0052%
C LLM synthetic                       0.0000%
D live MCP first                       0.0000%
```

Planning robustness only.

## Known answers

For a registry of N tools with G relevant tools and a uniformly random subset of size k:

```text
E[Recall] = k / N
```

for G > 0.

Probability that the random surface contains all G relevant tools:

```text
P(all gold) = C(N-G, k-G) / C(N, k)
```

for k >= G, otherwise zero.

These equations are independent oracles for the RANDOM-k Monte Carlo calibration.

## Decision

Implement VAL-001 with no provider/model calls and no paid dependency.
