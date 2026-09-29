# Dynamic Tool Surface Intake — 2026-09-29

> **Status:** PRIMARY-SOURCE RESEARCH INTAKE
> **Authority:** NONE
> **Purpose:** Add current production evidence for finite, searchable, cacheable, and dynamically changing tool surfaces.

## Primary sources

1. OpenAI — Tool search  
   https://developers.openai.com/api/docs/guides/tools-tool-search
2. OpenAI — MCP servers / deferred MCP tool loading  
   https://developers.openai.com/api/docs/guides/tools-connectors-mcp
3. Cloudflare — *Introducing cf: the agentic CLI for the entire Cloudflare API*  
   https://blog.cloudflare.com/cloudflare-cf-cli-launch/
4. Model Context Protocol — 2026-07-28 specification release  
   https://blog.modelcontextprotocol.io/posts/2026-07-28/
5. MCP TypeScript SDK — 2026-07-28 dynamic list-change support  
   https://ts.sdk.modelcontextprotocol.io/v2/migration/support-2026-07-28
6. AWS — AgentCore Gateway + MCP multi-account architecture  
   https://aws.amazon.com/blogs/machine-learning/build-a-multi-account-ai-agent-with-agentcore-gateway-and-mcp/
7. Openship — MCP security and permission model  
   https://openship.io/docs/mcp

## Source -> Observation -> Inference -> Experiment impact

### OpenAI Tool Search

**SOURCE OBSERVATION**

OpenAI documents deferred function/MCP loading so individual tool definitions enter model context only when needed. The guide explicitly positions this for large catalogs where each task needs only a few tools.

**INFERENCE**

```text
Available Tool Registry
!=
Resident Tool Schema Set
```

The active surface can be a task-dependent working set.

**EXPERIMENT IMPACT**

BENCH-family metrics should distinguish:

- total registry size;
- searchable metadata initially visible;
- loaded schema count;
- loaded schema tokens;
- discovery-step tokens;
- total task tokens.

A schema-token reduction is not automatically an end-to-end token reduction.

### Cloudflare cf CLI

**SOURCE OBSERVATION**

Cloudflare reports that `cf` covers more than 3,000 API operations and adds `cf cli search` so an agent can query a small search index rather than carry the entire command surface in context. Cloudflare also makes JSON the default output because agents can filter structured output more efficiently than human-oriented tables.

**INFERENCE**

Large capability universes can stay available while only a small command description set becomes active.

```text
Registry Size != Active Surface Size
Output Completeness != Output Residency
```

**EXPERIMENT IMPACT**

Add source-side projection as a separate experimental axis:

- full tool output;
- structured output;
- structured + field filtering;
- compact typed receipt.

Measure output tokens separately from schema tokens.

### MCP 2026-07-28

**SOURCE OBSERVATION**

The MCP release makes list results cacheable with `ttlMs` / `cacheScope`. SDK support also exposes tool-list change notifications through subscriptions.

**INFERENCE**

A tool surface is not necessarily a static prompt prefix. It can be:

- cached;
- invalidated;
- refreshed;
- changed at runtime.

Candidate state machine:

```text
AVAILABLE
-> SEARCHABLE
-> LOADED
-> CALLABLE
-> STALE
-> INVALIDATED / EVICTED
```

**EXPERIMENT IMPACT**

Future BENCH work should model:

- catalog-refresh cost;
- stale-tool exposure;
- cache hit rate;
- invalidation delay;
- re-discovery cost.

### AWS AgentCore Gateway

**SOURCE OBSERVATION**

AgentCore Gateway presents one MCP endpoint across multiple line-of-business MCP servers, performs discovery and policy checks at the Gateway, and the downstream MCP Runtime validates inbound credentials again. AWS explicitly recommends restricting downstream invocation to an identity chain that includes the Gateway.

**INFERENCE**

Tool routing and authorization are separable control planes.

```text
Discovered Tool
!=
Authorized Tool Call

Gateway Permit
!=
Downstream Authentication
```

**EXPERIMENT IMPACT**

A future surface governor must not treat shortlist membership as executable authority.

### Openship MCP

**SOURCE OBSERVATION**

Openship filters `tools/list` according to credential capability, then re-runs route validation/auth/per-resource permission checks on every `tools/call`. Its MCP tools map to permission-tagged REST routes, and credential-management modules are explicitly excluded from the tool surface.

**INFERENCE**

Visibility filtering is useful but is not the security boundary.

```text
Visible != Authorized-at-call-time
```

A finite surface can reduce cognitive/token load without becoming an authority grant.

## New atomic vocabulary

### Registry

All capabilities that could in principle be exposed.

### Searchable surface

Minimal metadata available to the discovery mechanism.

### Resident surface

Full schemas currently loaded into model context.

### Authorized surface

Capabilities current policy would permit if invoked correctly.

### Invoked surface

The actual tools called during the task.

### Verified surface

Invocations whose postconditions have been independently checked.

These sets may overlap but must not be collapsed.

## Token-economics decomposition

For task (q):

```text
T_total =
    T_prompt
  + T_searchable_metadata
  + T_discovery
  + T_loaded_schemas
  + T_tool_outputs
  + T_reasoning
  + T_history
```

A successful optimization must state which term fell.

Headline claims based only on `T_loaded_schemas` are incomplete.

## Candidate experiment extensions

### BENCH-DYN-001 — deferred loading

Compare EAGER vs DEFERRED at matched registry and task set.

Report:

- task success;
- gold coverage;
- loaded schema tokens;
- discovery tokens;
- total input tokens;
- latency;
- wrong/no-tool calls.

### BENCH-DYN-002 — cache + invalidation

Introduce catalog mutations and compare:

- no cache;
- TTL cache;
- TTL + explicit list-change invalidation.

Measure stale-surface error and refresh overhead.

### BENCH-DYN-003 — output projection

Compare raw human-oriented output, JSON, and source-filtered JSON.

Measure token cost and downstream answer fidelity separately.

## Research invariants

```text
Available != Visible
Visible != Loaded
Loaded != Selected
Selected != Authorized
Authorized != Invoked
Invoked != Verified
```

and:

```text
Prompt Reduction != End-to-End Token Reduction
```

## Claim ceiling

These primary sources establish that large real tool catalogs are already being searched, deferred, cached, filtered, and gateway-governed in production-facing systems.

They do not establish one universally optimal shortlist depth, cache TTL, or token-saving percentage.

## Intake decision

**ABSORB.**

This strengthens the lab's existing Tool Surface Frontier rather than replacing it.
