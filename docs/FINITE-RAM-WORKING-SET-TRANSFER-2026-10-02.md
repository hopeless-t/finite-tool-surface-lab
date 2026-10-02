# Finite RAM Transfer — Tool Surface as a Finite Semantic Working Set

Status: **RESEARCH TRANSFER / NO PRODUCTION ROUTING CLAIM**

Source research:
- `hopeless-t/finite-ram-lab`
- B461-B500 Governor/application line
- PR #46 / B500 one-shot local qualifier
- 2026-10-02 CLM finite-working-set intake

## 1. Transfer boundary

The transferable result is **not** a RAM threshold and not a particular q value.

The transferable principle is:

> **An obligation to make capability available is not an obligation to keep its full representation resident in every Worker context.**

For this repository:

```text
Available Tool Warehouse
!=
Resident Tool Schema Set
!=
Retrieved Tool Candidate Set
!=
Selected Tool
!=
Authorized Tool
```

This extends the existing Tool Surface Frontier model without changing its authority boundary.

A tool may remain available in the registry while its schema is absent from the current Worker prompt.

## 2. Future-sufficient tool state

Let:

- `W` = complete qualified Tool Warehouse,
- `R_t` = tool representations resident in the Worker context at time t,
- `F_t` = tools sufficient for the next bounded decision,
- `A_t` = tools externally authorized for execution.

The research target is not:

`R_t = W`.

Instead test whether:

`F_t subseteq R_t subseteq W`

can preserve task utility while reducing context cost and interference.

Authority remains orthogonal:

`R_t != A_t`.

A hidden tool does not lose authority merely because it is not resident.
A visible tool does not gain authority merely because it is resident.

## 3. B461/B500 methods that transfer

### 3.1 Obligation / residency separation

Finite RAM B461 distinguishes logical obligation from simultaneous representation.

Tool-surface analogue:

`Tool availability obligation != simultaneous schema residency`.

### 3.2 Coverage-aware promotion

A surface policy should not be promoted because one run succeeded.

Use replicated evidence and keep:

`observation != adoption evidence`.

A policy learned from one task/model/runtime population must not be treated as universal.

### 3.3 OBSERVE / OPTIMIZE / PROBE separation

Adopt the three-mode split:

- **OBSERVE** — measure current surface without intervention.
- **OPTIMIZE** — choose a surface expected to reduce cost while satisfying declared task/coverage gates.
- **PROBE** — deliberately expose or hide tools to discriminate competing hypotheses.

Scientific invariant:

`OPTIMIZE data != PROBE data`.

Intervention runs must remain marked as experimental.

### 3.4 Failure-state biopsy

When a reduced surface fails, capture the first decision point where failure becomes attributable.

Candidate classes:

- required tool absent,
- required tool present but not selected,
- distractor interference,
- stale schema/version,
- retrieval failure,
- wrong abstention,
- unrelated Worker error.

Do not collapse all reduced-surface failures into "k too small."

## 4. Proposed experiment — FTS-FR-001

### Question

Can an adaptive finite tool working set reduce resident schema cost without reducing end-to-end task success beyond a declared tolerance?

### Arms

```text
A0 FULL
   all qualified tool schemas resident

A1 STATIC-k
   deterministic fixed-size retrieved surface

A2 ADAPTIVE
   task-conditioned surface policy

A3 ORACLE-RELEVANT
   research-only relevance oracle; not deployable

A4 PROBE
   deliberate one-variable visibility interventions
```

Freeze:

- model/provider revision,
- task corpus,
- registry revision,
- tool semantics,
- authority policy,
- seed schedule where available,
- maximum tool/model calls.

### Sweep

Candidate dimensions:

- visible schema bytes/tokens,
- visible tool count,
- retrieval depth,
- registry size,
- distractor density,
- schema overlap,
- context pressure.

Use:

`coarse sweep -> knee candidate -> local refinement -> replication -> biopsy`.

### Metrics

Keep at least:

- task success,
- gold-tool coverage,
- conditional selection accuracy,
- wrong-tool invocation,
- false invocation on no-tool tasks,
- resident schema bytes/tokens,
- retrieval latency,
- total harness tokens,
- re-retrieval events,
- tool-call count,
- authority violations.

Authority violations must remain a hard constraint, not an optimizable trade-off.

## 5. Candidate Tool Surface Governor

A future evidence-bound policy may use:

```text
task fingerprint
+ registry fingerprint
+ model/harness fingerprint
+ pressure budget
          |
          v
candidate active surfaces
          |
          v
coverage / success / cost frontier
          |
          v
selected resident schema set
```

The Finite RAM B500 pattern suggests binding promoted policies to the environment that generated their evidence.

For tool surfaces the fingerprint should include at least:

- registry revision,
- schema digest,
- model revision,
- harness/prompt revision,
- task-family identifier.

Copying a policy to a materially different registry/model/harness should fail closed or require revalidation.

## 6. What does not transfer

Do **not** transfer:

- hosted RAM peak thresholds,
- q2/q4/q7 choices,
- B500 host fingerprints,
- exact CRT claims,
- physical-memory coverage as if it were tool-selection coverage.

A semantic working set has omission/interference failure modes that physical reclaim does not.

## 7. Suggested receipt delta

Future tool-surface receipts should be able to record:

```text
mode = OBSERVE | OPTIMIZE | PROBE
policy_id
model_revision
harness_revision
registry_revision
schema_digest
task_family
resident_tool_ids
resident_schema_bytes
retrieved_tool_ids
selected_tool_id
authority_result
task_result
intervention_id
hypothesis_id
changed_variables
held_constant_variables
```

## 8. Claim ceiling

`FINITE_RAM_TOOL_SURFACE_TRANSFER_PROTOCOL_DEFINED`

This document defines a research bridge.
It does not prove that smaller or adaptive surfaces improve Worker performance.
