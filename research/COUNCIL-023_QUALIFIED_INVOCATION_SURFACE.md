# COUNCIL-023 — Qualified Invocation Surface

## Trigger

The Dynamic Tool Surface intake established that production-facing systems already separate:

```text
Available
!= Visible
!= Loaded
!= Selected
!= Authorized
!= Invoked
!= Verified
```

BENCH-004 further established an architectural separation between:

```text
Which Tool Looks Relevant?
!=
Should Any Tool Surface Exist?
```

A cross-repository MVCA incident now motivates a third separation:

```text
Which Logical Tool Is Selected?
!=
Which Provider Invocation Is Qualified?
```

The incident itself is private/project-specific operational evidence and is recorded separately in:

`research/FAILURE-003_MVCA_INVOCATION_QUALIFICATION.md`

It is **not** sufficient public canonical evidence for the lab.

## Decision question

Should future Tool Surface experiments model a tool only as one stable schema/identifier, or as a logical tool with one or more independently qualified provider/invocation bindings?

## Candidate models

### A — Logical-tool-only surface

```text
Task
  ->
Logical Tool
  ->
Call
```

Provider/runtime details are treated as hidden implementation.

### B — Provider-aware tool surface

```text
Task
  ->
Logical Tool
  ->
Provider Binding
  ->
Call
```

Provider identity is visible to the surface policy but no explicit qualification state is modeled.

### C — Qualified Invocation Surface

```text
Task
  ->
Logical Tool
  ->
Candidate Provider Binding
  ->
Qualified Invocation Profile
  ->
Call / DEFER
```

Qualification state is independent from tool relevance and surface membership.

### D — Collapse provider qualification into execution authorization

A provider becomes executable merely by being selected/qualified.

### E — Always expose all provider metadata

Every model task receives all logical tools plus all provider/runtime detail.

## Pseudo-Council

### Tool-surface seat -> C

The existing Tool Surface Frontier optimizes the surface visible to a Worker.

If provider/runtime identity can change while a logical tool name/schema remains stable, logical-tool count alone under-describes the effective surface.

The relevant object becomes at least two-layered:

```text
Logical Surface
+
Invocation Binding Surface
```

### Experimental-design seat -> C

C permits controlled synthetic counterfactuals:

- same logical tool;
- same query;
- same relevance;
- different provider qualification state.

That isolates invocation qualification from retrieval quality.

### Safety / authority seat -> C, reject D

Qualification is evidence, not permission.

```text
Qualified Invocation
!=
Execution Authority
```

This preserves the repository's existing boundary:

```text
Tool Qualified != Tool Authorized
```

### Token-economics seat -> C over E

Always exposing provider detail may destroy the finite-surface benefit.

A qualified-binding layer can be searched, cached, or projected just like logical tools.

The experiment should measure whether provider qualification information belongs:

- in resident model context;
- behind deferred lookup;
- at a gateway only;
- in a deterministic admission layer.

### Dynamic-surface seat -> C

The 2026-09-29 Dynamic Tool Surface intake already models runtime mutation and cache invalidation.

Provider qualification introduces another mutable state dimension:

```text
REGISTERED
-> SEARCHABLE
-> LOADED
-> SELECTED
-> PROVIDER_BOUND
-> QUALIFIED
-> CALLABLE
-> STALE
-> INVALIDATED
-> REQUALIFIED
```

These transitions must not be collapsed.

### Provider-portability seat -> C

External gateway/framework prior art already separates client-visible logical tools from downstream execution routing.

Useful mechanism examples include:

- Microsoft MCP Gateway:
  https://github.com/microsoft/mcp-gateway
- Moor:
  https://github.com/varandrew/moor
- Ship:
  https://github.com/cloudshipai/ship
- Openship permission-filtered MCP projection:
  https://openship.io/docs/mcp

The lab should borrow the indirection mechanism, not infer any authority semantics from those systems.

### Claim-safety seat -> C with public validation required

The motivating MVCA incident is useful hypothesis generation only.

The lab's public-repository rule requires a deterministic/public experiment before any canonical claim is promoted.

## Candidate atomic vocabulary

### Logical Tool

Stable task-facing capability identity and schema.

### Provider Candidate

One implementation endpoint or adapter that claims to implement a Logical Tool.

### Qualified Invocation Profile

A bounded evidence object describing the exact invocation context that has been qualified for a Provider Candidate.

Candidate fields may include:

- provider identity/version;
- adapter identity;
- executable artifact identity;
- supported launcher identity;
- fixed argv/environment digest;
- runtime/confinement semantics;
- target identity;
- parser/result contract identity;
- timeout/output ceilings;
- qualification evidence references.

This is a research object, not an authority grant.

### Qualified Invocation Surface

The subset of provider bindings currently carrying valid qualification evidence for the logical tools relevant to a task.

### False Callable

A logical tool/provider binding surfaced as callable even though its invocation profile is stale, unsupported, ambiguous, or otherwise unqualified.

### Qualification Drift

A provider/runtime/adapter change that invalidates a previously qualified binding while the logical tool identity may remain unchanged.

## Proposed invariant extension

Current research invariants:

```text
Available != Visible
Visible != Loaded
Loaded != Selected
Selected != Authorized
Authorized != Invoked
Invoked != Verified
```

Candidate extension:

```text
Selected Logical Tool != Qualified Invocation
Invoked Logical Tool != Qualified Invocation
Logical Tool != Provider Implementation
Provider Replacement != Qualification Continuity
Qualified Invocation != Execution Authority
```

The order is not necessarily one linear state machine. These are distinct dimensions.

## New Tool Surface Frontier dimensions

The existing Tool Surface Frontier should not be replaced.

A provider-aware experiment may add:

- logical tools exposed;
- provider candidates exposed;
- qualified provider bindings exposed;
- qualification metadata bytes/tokens;
- false-callable rate;
- stale-binding rate;
- qualified-provider recall;
- provider requalification latency/cost;
- logical-tool success;
- end-to-end task success;
- wrong-provider selection;
- DEFER / UNKNOWN rate.

## BENCH-QIP-001 candidate — Logical Tool vs Qualified Invocation

### Controlled setup

Generate tasks with:

- fixed logical-tool relevance;
- deterministic logical registry;
- 1..N provider candidates per logical tool;
- provider states:
  - QUALIFIED;
  - STALE;
  - UNSUPPORTED_LAUNCHER;
  - PARSER_AMBIGUOUS;
  - UNAVAILABLE;
- exact gold logical tools;
- exact acceptable provider bindings.

Hold logical retrieval evidence constant while varying provider qualification state.

### Policies

1. `LOGICAL_ONLY`
   - sees only logical relevance.

2. `PROVIDER_VISIBLE`
   - sees provider identities but not qualification evidence.

3. `QUALIFIED_ONLY`
   - surface contains only currently qualified bindings.

4. `DEFERRED_QUALIFICATION`
   - starts with logical surface and resolves provider qualification only after selection.

5. `ORACLE_BINDING`
   - reference control.

### Primary metrics

- logical gold recall;
- qualified binding recall;
- false-callable rate;
- stale binding selection;
- qualification lookup count;
- qualification metadata bytes;
- total surface bytes;
- defer rate;
- end-to-end synthetic task success.

### Negative-control requirement

Construct matched pairs where logical tool relevance is identical but provider qualification differs.

Then:

```text
Logical Retrieval Evidence Isomorphic
!=
Invocation Qualification Semantics Equivalent
```

A logical-only selector should be unable to solve that distinction by construction.

## BENCH-QIP-002 candidate — Dynamic provider drift

Extend BENCH-DYN lifecycle experiments.

During a task stream, mutate:

- provider version;
- adapter identity;
- launcher identity;
- parser schema;
- qualification TTL/state.

Compare:

- no invalidation;
- TTL-only;
- explicit provider-change invalidation;
- requalification-before-call.

Measure:

- stale-qualified calls;
- false-callable duration;
- requalification overhead;
- task success after drift;
- whether logical-tool cache remains valid while provider binding becomes invalid.

## Relation to BENCH-004

BENCH-004 asks:

```text
Should Any Tool Surface Exist?
```

Qualified Invocation research asks, only after a surface is admitted:

```text
Which exact implementation binding is safe/valid to treat as callable?
```

Candidate composition:

```text
Tool-Need Admission
        ->
Logical Surface Selection
        ->
Provider Qualification Resolution
        ->
Execution Authorization
        ->
Invocation
        ->
Verification
```

Every arrow remains experimentally and semantically distinct.

## Council decision

```text
ADOPT C AS RESEARCH MODEL
```

Meaning:

- add Qualified Invocation Surface as a research hypothesis/model;
- preserve the existing Tool Surface Frontier;
- do not promote new invariants to README/charter as canonical empirical findings yet;
- design a deterministic public synthetic benchmark before making a general claim;
- keep provider qualification separate from execution authority.

## Claim ceiling

This council does not establish that:

- all tool ecosystems require provider-visible qualification metadata;
- provider-aware surfaces improve Worker performance;
- one exact Qualified Invocation Profile schema is optimal;
- provider qualification should be model-visible;
- the motivating MVCA incident is public canonical evidence.

It establishes a **bounded next research question**.

## Working hypothesis

```text
A finite tool surface may still be unsafe or ineffective
if it is finite only at the logical-tool layer
while provider invocation state remains unqualified or stale.
```
