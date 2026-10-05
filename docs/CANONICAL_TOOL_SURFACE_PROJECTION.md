# Canonical Tool Surface Projection

Status: research proposal

## Hypothesis

Tool-surface quality depends not only on which tools are visible, but also on how provider-specific tool schemas are represented to the Worker.

Canonical IR suggests testing a semantic projection layer:

```text
Provider tool warehouse
  -> lift to semantic tool objects
  -> evidence-selected active semantic surface
  -> optional provider-specific lowering at invocation
```

This separates three variables that raw provider catalogs often mix:

```text
Capability coverage
Representation cost
Provider schema quirks
```

## Semantic tool object

Candidate fields:

```text
ToolSemanticObject {
  semantic_operation
  resource_types[]
  required_capabilities[]
  possible_effects[]
  constraints[]
  input_contract
  output_contract
  provenance
  provider_adapter
}
```

The semantic object does not grant authority and does not replace qualification.

## New benchmark axis

Add representation as an explicit ablation dimension:

```text
RAW_PROVIDER_SCHEMA
CANONICAL_COMPACT
CANONICAL_RICH
NAME_DESCRIPTION_ONLY
```

Hold task set, provider capability, gold relevance, and Worker constant where possible.

Measure:

- serialized bytes/tokens;
- gold-tool coverage;
- selection accuracy conditional on coverage;
- wrong-tool invocation;
- abstention quality;
- end-to-end success;
- latency/cost;
- semantic-loss failures.

## Key distinction

```text
Smaller Representation != Smaller Capability
Canonical Projection != Authority Projection
Tool Semantic Equivalence != Provider Behavioral Equivalence
```

Two provider tools may map to the same semantic operation while still differing in reliability, latency, cost, side effects, or qualification status. Preserve those as provider metadata/experimental conditions rather than erasing them.

## Progressive disclosure experiment

A useful BENCH candidate:

1. expose only compact semantic objects for all candidate tools;
2. allow the Worker/router to request richer provider detail only for shortlisted tools;
3. compare against full provider schemas shown up front;
4. measure whether semantic compression reduces token/context cost without harming verified task success.

This is distinct from reducing `k`: the same number of tools can be shown with different representation density.

## Failure probes

Include adversarial pairs where:

- names differ but semantics match;
- names look similar but effects differ;
- one provider cannot enforce a required constraint;
- a compact projection accidentally hides a forbidden effect;
- two tools share semantics but differ in authority/qualification.

Any compact representation that hides a safety/authority-relevant distinction is invalid, even if selection accuracy improves.

## Transfer criterion

Promote toward MVCA only if a canonical projection demonstrates reproducible benefit while preserving:

- required capability/effect distinctions;
- qualification boundaries;
- authority separation;
- provider-specific failure evidence.

Working principle:

> Optimize the semantic surface seen by the Worker, not just the raw count of provider tools.
