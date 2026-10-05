# Strata v0.1.39 cross-pollination for finite-tool-surface-lab — 2026-10-05

## Transferable principle

A tool catalog resembles a memory hierarchy: exposing every tool eagerly spends context/attention just as keeping every expert resident spends VRAM. The useful abstraction is a bounded hot set plus addressable colder tiers.

## Candidate tool tiers

```text
HOT      minimal tools required for the current phase
WARM     likely next tools, cheap to surface
COLD     discoverable registry entries
REMOTE   expensive/specialized capabilities loaded only on demand
```

Budget by serialized bytes/tokens and expected utility, not by raw tool count.

## Candidate measurements

- first-call tool-schema bytes;
- hot-set hit rate;
- tool promotion/demotion churn;
- discovery latency;
- wrong-tool invocation rate;
- verified task success;
- total context + tool-call cost.

## Strata-derived hypotheses

1. Adaptive hot sets outperform static full catalogs when tool surfaces are large.
2. Planning and execution phases need different tool surfaces.
3. Extra parallel workers can create a catalog/context eviction tax.
4. A slower fallback tool path is preferable to a hard failure when capability is still sufficient.

## Boundary

Tool discovery or residency does not grant authority to invoke the tool.
