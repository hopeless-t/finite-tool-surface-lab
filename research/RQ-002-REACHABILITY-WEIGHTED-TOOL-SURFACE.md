# RQ-002 — Reachability-Weighted Tool Surface

Status: **OPEN RESEARCH QUESTION**

Source intake: https://aikido-community.jp/articles/quiet-business-app-database-access

## Question

The current Tool Surface Frontier studies how much capability should be visible to a Worker. This intake adds a second dimension:

> Is visible tool count an inadequate proxy for risk/cost when two equally small tool surfaces expose radically different reachable resource graphs?

Example:

```text
Surface A: 5 tools -> 20 reachable objects
Surface B: 5 tools -> 2,000,000 reachable objects
```

The visible count is identical. The potential blast radius is not.

## Candidate distinction

```text
Tool Surface Size != Reachable Resource Surface
Tool Visible != Resource Reachable
Resource Reachable != Resource Required
Read-Only != Effect-Free
Single Allowed Call != Safe Aggregate Sequence
```

## Extended frontier

The current Tool Surface Frontier can be extended from a mostly visible-surface tradeoff into a multi-objective frontier:

```text
task success
vs
visible tool count
vs
serialized context cost
vs
reachable resource count / scope
vs
aggregate read fan-out
vs
wrong-tool / wrong-scope effects
```

Do not collapse these into one score before the individual observables are understood.

## Candidate metrics

### Visible surface metrics

- active tool count;
- serialized bytes/tokens;
- retrieval latency;
- tool-selection accuracy;
- false invocation.

### Reachability metrics

- direct reachable resource count;
- approximate transitive reachable resource count;
- number of scopes/repositories/services reachable;
- maximum permission depth;
- capability-expansion delta.

### Effect-stream metrics

- unique resources read;
- unique scopes touched;
- cumulative objects/bytes;
- enumeration count;
- graph distance from task anchors;
- slow low-rate fan-out;
- cross-scope transitions.

## New benchmark candidate

### BENCH-008 — Equal-k / Unequal-Reachability

Hold visible tool count `k` constant while varying the resource graph behind those tools.

Synthetic conditions:

```text
NARROW
  same k
  small bounded resource graph

BROAD
  same k
  large resource graph

BROAD-WITH-DISTRACTORS
  same k
  large resource graph
  many task-irrelevant resources

BROAD-SLOW-ENUM
  same k
  large graph
  injected low-rate enumeration behavior
```

Primary question:

> Does equal `k` produce materially different wrong-scope behavior or reachable blast radius?

Secondary question:

> Can a reachability-aware surface policy preserve task success while reducing exposed resource closure?

## Hypotheses

H1:

```text
visible_tool_count alone is insufficient to predict exposed authority/resource surface
```

H2:

```text
for equal visible k,
smaller task-relevant reachable closure can reduce wrong-scope effects
without reducing task success
```

H3:

```text
aggregate read fan-out can distinguish some harmful broad-surface behavior
that per-call success/permission cannot
```

These are hypotheses, not findings.

## Candidate frontier representation

Rather than:

```text
TSF(success, tool_count)
```

investigate:

```text
TSF(success,
    visible_tool_count,
    context_cost,
    reachable_scope,
    observed_effect_fanout)
```

A simpler derived metric may be introduced only after inspecting correlations and failure cases.

## Failure injections

Required adversarial cases should include:

1. tool with narrow declared schema but broad backend access;
2. tool that lists an entire collection before selecting one object;
3. GraphQL-like multi-object read hidden behind one invocation;
4. slow enumeration that stays below a rate threshold;
5. capability expansion mid-task;
6. irrelevant cross-repository traversal;
7. broad reachability that is never exercised, to separate exposed risk from observed behavior.

## Important separation

```text
Exposed Reachability != Observed Read Fan-Out
```

Both matter.

A Worker may have broad latent reachability yet behave perfectly. Conversely, a moderate reachability surface can still be abused exhaustively.

Therefore report both:

- **potential blast radius** from the capability/resource graph;
- **realized effect surface** from the observed sequence.

## Relationship to authority

This lab remains non-authoritative.

```text
Smaller Reachability != Authorization
Low Risk Score != Authorization
High Risk Score != Automatic Revocation
Benchmark PASS != MVCA Mainline Decision
```

The lab measures tradeoffs. MVCA or another qualified authority system decides policy.

## Minimal next step

Extend a synthetic registry fixture so each tool has:

```json
{
  "tool_id": "t1",
  "visible_cost": 1,
  "reachable_scopes": ["repo-a"],
  "reachable_resource_count": 20,
  "gold_for_tasks": ["task-1"]
}
```

Then create equal-`k` policies with deliberately unequal reachable closures and measure task success plus wrong-scope effects.

No claim is promoted by this research question alone.
