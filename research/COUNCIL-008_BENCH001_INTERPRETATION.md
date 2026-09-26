# COUNCIL-008 — BENCH-001 Interpretation

## Trigger

The full BENCH-001 artifact passed its frozen execution contract, but fresh readback exposed a sharp retrieval transition at overlap 0.50.

## Atomic finding

Synthetic generator v0.1 constructs each tool description as:

```text
shared family tokens
+ tool-unique tokens
+ family token
+ generic synthetic_tool token
```

The shared-token count is `round(overlap * 8)`.

Single-tool queries shuffle all ten description tokens and retain five.

Multi-tool queries take the first four description tokens from each selected tool.

Therefore:

```text
overlap 0.00 -> multi prefix contains 4 tool-unique tokens
overlap 0.25 -> multi prefix contains 2 tool-unique tokens
overlap 0.50 -> multi prefix contains 0 tool-unique tokens
overlap 0.75 -> multi prefix contains 0 tool-unique tokens
```

The transition at 0.50 is therefore partly a deliberate information-availability transition in the synthetic representation, not evidence for a universal semantic-overlap threshold.

## Additional alias finding

In generator v0.1, alias strings are candidate metadata. Query tokens are generated from `description_tokens`, not aliases.

Thus:

```text
alias_rate factor
!= alias-query resolution benchmark
```

It is currently a candidate-metadata / denominator perturbation.

## Decision candidates

A. Preserve BENCH-001 and promote it with an explicit information-ambiguity claim boundary.  
B. Rewrite the generator and rerun BENCH-001 under the same ID.  
C. Discard BENCH-001 and redesign from scratch.  
D. Promote the observed 0.50 transition as a general Tool Surface threshold.

## Pseudo-Council

**Spec-fidelity seat -> A.**  
The frozen benchmark did what its implementation specified; rewriting it after seeing the result would destroy comparability.

**Causal-interpretation seat -> A.**  
The ambiguity mechanism is inspectable and scientifically useful if named correctly.

**External-validity seat -> B later.**  
A smoother query-information generator should be tested in a later benchmark/distractor lane, not retroactively substituted.

**Claim-safety seat -> A.**  
Explicitly prohibit universal threshold claims.

**Reproducibility seat -> A.**  
Keep exact artifact and generator version.

## 250k synthetic planning sensitivity

Seed: 2026092604.

Criteria:
- frozen-spec fidelity;
- causal interpretability;
- reproducibility;
- future comparability;
- claim safety;
- incremental compute cost.

Result:

```text
A promote with ambiguity caveat   100.0000%
B rerun redesigned generator        0.0000%
C discard and redesign              0.0000%
D generalize threshold              0.0000%
```

Mean utility:

```text
A 0.9718
B 0.8448
C 0.6451
D 0.5950
```

Planning robustness only.

## Decision

```text
PRESERVE_BENCH001
+
PROMOTE_ONLY_WITH_GENERATOR_AMBIGUITY_CAVEAT
```

A later BENCH-003 / generator-v0.2 lane should vary distractor overlap without hard-erasing tool identity at a fixed prefix boundary.
