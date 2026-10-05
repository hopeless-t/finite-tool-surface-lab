# Workflow-Derived Active Tool Surfaces — 2026-10-05

## Source spark

- https://note.com/shi3zblog/n/nf59b8740cd24
- Transferable idea: real work can be decomposed into operations, branches, and loops before it is bound to implementation syntax.

## Research hypothesis

If a task is represented as a typed workflow graph, the graph may provide a stronger prior for the **minimum relevant tool surface** than lexical task-to-tool retrieval alone.

```text
occupation / task workflow DSL
        ↓
Canonical Workflow IR
        ↓
required operation / capability slice
        ↓
candidate Active Tool Surface
        ↓
Worker
```

This does not prove that the derived surface is sufficient. It gives the lab a new surface policy to test.

## Static capability slicing

Suppose a workflow contains nodes such as:

```text
Observe(local_file)
Transform(report_data)
AttachEvidence(photo)
GenerateProjection(pdf)
Wait(human_review)
```

Each semantic node can declare capability requirements:

```text
Observe(local_file)       -> filesystem.read
AttachEvidence(photo)     -> media.import + persistence.write
GenerateProjection(pdf)   -> report.render
Wait(human_review)        -> no external tool required
```

The union of reachable requirements becomes a candidate workflow-derived surface.

A control-flow-aware slice can be narrower than a simple union if some branches are impossible under the current task state.

## Candidate policies

Add future benchmark policies such as:

1. `WORKFLOW-UNION` — expose all capabilities reachable anywhere in the workflow.
2. `WORKFLOW-STATE-SLICE` — expose only capabilities reachable from the current workflow state.
3. `WORKFLOW-NEXT-N` — expose capabilities needed within the next N transitions.
4. `WORKFLOW+RETRIEVAL` — workflow-derived mandatory core plus retrieval-selected semantic extras.
5. `ORACLE-WORKFLOW` — experiment-only exact required surface derived from ground-truth workflow annotations.

These can be compared against `FULL`, `RANDOM-k`, lexical retrieval, and existing oracle controls.

## Why this differs from ordinary retrieval

Lexical retrieval asks:

> Which tools look relevant to this text?

Workflow slicing asks:

> Which capabilities are required by the currently reachable executable semantics?

The two can disagree usefully.

Example:

```text
Task text mentions "PDF" and "email".
Current workflow state is still field capture.
```

A lexical surface may expose PDF/email tools early. A state slice may expose only capture/storage capabilities until the review transition makes reporting reachable.

## Tool surface as a projection

The Canonical Workflow IR can project to a tool-surface demand set:

```text
Workflow IR
  ├─ human checklist
  ├─ UI projection
  ├─ execution proposal graph
  └─ capability demand projection
         ↓
     Active Tool Surface policy
```

This is especially interesting if the semantic source remains stable while tool implementations/providers change.

## Necessary separations

```text
workflow requires capability != a specific tool is qualified
capability relevant != tool should be visible
visible != selected
selected != authorized
workflow state != authority state
```

A workflow-derived surface must never grant new permission. It can only reduce or rank what is visible from an already qualified/allowed warehouse.

## Failure modes to test

- workflow annotation omits a necessary hidden capability;
- one semantic capability maps to many tool implementations;
- branch uncertainty makes an aggressive state slice hide a soon-needed tool;
- recovery paths require tools not present on the happy path;
- semantic macros expand to capability requirements only after lowering;
- capability changes after provider/runtime drift;
- over-broad workflow annotations collapse back toward the full warehouse.

## Candidate benchmark extension

Construct synthetic tasks with frozen workflow graphs and exact capability annotations.

Compare surface policies on:

- gold-tool / gold-capability coverage;
- visible tool count;
- serialized bytes/tokens;
- wrong-tool invocation;
- no-tool abstention;
- number of surface expansions during execution;
- end-to-end task success;
- recovery-path coverage;
- state-slice churn across transitions.

A particularly useful question is whether workflow slicing improves the Tool Surface Frontier or merely shifts errors from distractor exposure to missing-capability failures.

## Link to Semantic Forge

Semantic Forge can act upstream:

```text
industry DSL
→ normalized Canonical Workflow IR
→ capability requirements
→ finite-tool-surface policy
```

If successful, the same workflow meaning could drive both execution planning and the bounded set of tools shown to a Worker.

## Claim ceiling

This research can establish only model/benchmark-relative evidence that workflow semantics help construct smaller sufficient surfaces under declared annotations and workloads.

It cannot by itself prove production optimality, tool qualification, or execution authority.
