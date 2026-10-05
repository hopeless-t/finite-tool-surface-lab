# Commitment-scoped active tool surfaces

Status: research candidate

Source intake: https://note.com/npaka/n/n341b20a052c6

## Crossover hypothesis

A durable Commitment gives tool-surface selection a stable semantic anchor across many short-lived worker sessions.

Instead of exposing the same warehouse to an always-running agent:

```text
Commitment state
  + current trigger
  + next admissible transition
      -> derive bounded Active Tool Surface
      -> wake worker
      -> act / abstain
      -> persist evidence
      -> discard worker surface
```

This separates:

```text
Durable Work State != Durable Tool Exposure
Tool Available != Tool Visible
Tool Visible != Tool Authorized
Commitment Requires Capability != Worker May Invoke Capability Now
```

## Candidate benchmark extension

Add a synthetic multi-wake task family where one durable Commitment advances through stages such as Observe -> Diagnose -> Propose -> Verify.

Compare:

1. full warehouse on every wake;
2. static small surface;
3. Commitment-state-derived surface;
4. oracle stage-specific surface.

Measure existing TSF metrics plus:

- cumulative serialized tool bytes across the whole Commitment;
- wrong-tool exposure per stage;
- stage-transition coverage;
- wake-to-correct-tool latency;
- stale-surface errors after state change;
- false invocation on observation-only wakes.

## Safety boundary

Surface derivation must never act as authority derivation.

A Commitment may explain **why a capability is relevant**. It cannot establish **whether invocation is permitted**.

Candidate principle:

> **Persist the task meaning; reconstruct only the tool surface justified by the current semantic state.**