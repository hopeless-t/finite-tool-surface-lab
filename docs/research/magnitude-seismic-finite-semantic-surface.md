# Magnitude / Seismic lessons for finite-tool-surface-lab

## Core fit

Seismic uses a closed, inspectable semantic registry and rejects constructs that cannot be represented before execution. That maps directly to the idea of a finite tool surface.

## Proposed invariant

> Tool availability may vary, but the semantic operation vocabulary should remain finite, typed, and inspectable.

## One semantic registry

Each canonical operation should own:

- input/output types
- effects
- authority requirements
- replay/idempotency class
- resource requirements
- evidence requirements
- failure classes

Adapters must not redefine these semantics.

## Capability-driven lowering

Operations should request capabilities rather than provider names.

```text
repository.read
repository.write.branch
pull_request.create
process.exec
browser.navigate
```

A planner can then choose among GitHub, local git, MCP, browser, or another backend.

## Reject unsupported semantics early

If no available backend can realize a canonical operation while preserving its contract, fail during checking/planning.

Do not allow:

```text
semantic operation accepted
  -> later tool call
  -> surprise capability mismatch
```

Prefer:

```text
semantic operation
  -> capability check
  -> feasible lowerings
  -> selected backend
```

## Finite surface, open implementations

The semantic vocabulary can stay finite even while implementations remain open-ended.

```text
finite semantic surface
  -> N current adapters
  -> future adapters without semantic expansion
```

Only genuinely new meaning should expand the canonical operation set.

## Search state

Distinguish:

- no backend supports an operation;
- a backend exists but current resources are insufficient;
- search is incomplete;
- an execution candidate is feasible;
- a candidate is selected and authorized.

## Experiment

Take one operation such as `repository.create_branch` and implement two adapters. Prove that both consume the same semantic record and produce equivalent completion evidence.

## Working rule

> Keep the tool surface finite by making meaning canonical and implementations replaceable.
