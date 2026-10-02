# News Intake 2026-10-02 — OpenPOI, Transport Equivalence, and Provenance Residency

Status: RESEARCH INTAKE / LIVE API CALL NOT CLAIMED

## Scope

OpenPOI is useful to this lab because the same public data semantics are exposed through
multiple agent-facing surfaces:

- REST search/suggest,
- OpenAPI 3.1,
- stateless Streamable HTTP MCP.

Primary documentation captured 2026-10-02:

- https://docs.openpoiapi.com/
- machine-readable schema: https://api.openpoiapi.com/openapi.json

The documentation states that the MCP endpoint exposes `search_facilities` and
`dataset_info`, and that `search_facilities` has the same search semantics as
`GET /v1/search`. This creates a rare public fixture for comparing transport/harness
friction while holding the underlying dataset approximately fixed.

The live API host was not reachable from the current research browser execution
environment, so this intake does not claim a fresh live result. Documentation examples
and schema are the current evidence boundary.

## Atomic decomposition

### Atom A — transport is not search semantics

REST, OpenAPI-generated clients, and MCP are transport/binding choices.

A useful equivalence target is:

    normalize(result_REST(q)) == normalize(result_MCP(q))

for the documented shared search operation.

Failure of transport equivalence should be classified separately from a difference in
retrieval semantics.

### Atom B — /search and /suggest are different algorithms

Do not treat them as aliases.

The documentation describes `/v1/suggest` as an autocomplete-oriented path with:
- normalization,
- deduplication,
- ranking,
- vocabulary/completion output,
- local bbox-first behavior with nationwide fallback.

That is not equivalent to the broader retrieval semantics of `/v1/search`.

Therefore:

    transport equivalence test: REST search <-> MCP search_facilities
    semantic comparison test: /search vs /suggest

These are different experiments.

### Atom C — minimal payload is not semantics-preserving compression

With `fields=minimal`, per-candidate fields such as category, business_type, source,
licenses, and attributions are omitted; licenses/attributions are emitted at response
level as a union.

Therefore the lightweight response preserves enough data for some autocomplete use
cases, but loses candidate-level provenance coordinates.

Define record-level provenance:

    P_i = (source_i, licenses_i, attributions_i)

and minimal response provenance:

    P_min = union_i(licenses_i, attributions_i)

In general:

    {P_i} cannot be reconstructed from P_min

So payload reduction is lossy with respect to candidate-level provenance.

### Atom D — provenance is part of the semantic working set

If a downstream consumer must later explain, store, redistribute, or audit an individual
POI, provenance fields are not decorative metadata.

A projection is sufficient only relative to a consumer contract.

    sufficient(fields, task) != sufficient(fields, every_task)

This is directly analogous to tool-surface projection.

### Atom E — category coverage is incomplete

The current generated documentation reports:

    unknown category/business_type = 1,840,570 / 3,372,487 ~= 54.6%

Therefore the known-category fraction is:

    (3,372,487 - 1,840,570) / 3,372,487
    ~= 0.4542396
    ~= 45.42%

This implies that a router that relies only on normalized category coordinates has a
hard coverage ceiling near 45.42% on this snapshot before any model/search error is
considered.

This is a source snapshot, not a permanent dataset property.

### Atom F — surface compression creates recall risk

Cloudflare's current `cf` CLI documentation says the CLI has more than 2,900 commands
and `cf cli search` returns at most five matches.

Candidate-count projection alone therefore has a nominal lower-bound compression ratio:

    2900 / 5 = 580:1

This is not a token or byte compression ratio and says nothing about top-k recall.

The existing BENCH-007 / PR #15 measured a frozen metadata-to-projection byte ratio on
its own upstream snapshot. Keep those two measurements separate.

### Atom G — process success is not effect proof

Current Cloudflare `cf` documentation explicitly notes that a destructive command
aborted in a non-interactive session can print `Aborted.` and exit with status 0.

Therefore:

    returncode == 0
    does not imply
    semantic_effect == APPLIED

The lab's APPLIED / NO_EFFECT / UNKNOWN split remains justified.

## Mathematical model — minimum sufficient surface

Let U be the complete capability/data field universe and S subset U the resident
projection shown to a worker.

Define:

- C(S): context/serialization cost,
- R(S): probability the required field/tool is absent,
- P(S): provenance loss,
- F(S): execution friction.

A candidate objective:

    L(S) = lambda*C(S) + mu*R(S) + nu*P(S) + xi*F(S)

A top-k search system primarily reduces C(S), but can increase R(S).
A minimal field projection reduces C(S), but can increase P(S).

These are separate loss channels.

## Falsifiable hypotheses

### FTS-POI-H1 — transport cost is measurable under semantic equivalence

For identical `/search` semantics, REST/OpenAPI/MCP differ in:
- serialized bytes,
- schema/context tokens,
- tool-selection overhead,
- latency,
- failure classification friction.

Falsifier: differences vanish within measurement noise after warm-up and normalization.

### FTS-POI-H2 — minimal mode has a provenance-loss knee

There exist tasks where `fields=minimal` preserves task success and tasks where it
causes an abrupt failure because record-level provenance/category is required.

Falsifier: candidate-level fields never change downstream decisions on the selected corpus.

### FTS-POI-H3 — category-only routing will systematically miss valid candidates

Because ~54.6% of current records have unknown category/business_type, category-only
retrieval/routing should under-cover a query corpus compared with name/address/text
fallback.

Falsifier: observed recall is unchanged across a representative corpus after controlling
for other query features.

### FTS-CF-H4 — top-k capability projection has a pressure knee

As k decreases, token/schema burden falls until command recall drops sharply.
The optimal k is task-distribution-specific.

Falsifier: recall is flat across the tested k range or no stable knee replicates.

### FTS-EFFECT-H5 — exit status aliases semantic states

At least two executions can share returncode=0 while differing in effect state
(APPLIED vs NO_EFFECT/UNKNOWN).

This already has an upstream example in `cf`; future lab work should reproduce it in a
controlled fixture without external mutation.

## Proposed experiments

### FTS-POI-001 — REST vs MCP semantic equivalence

Freeze a query corpus and normalize:
- POI identity coordinates,
- ordering where contractually meaningful,
- source/provenance fields.

Compare REST `/v1/search` with MCP `search_facilities`.

Record transport bytes, model-visible bytes/tokens, wall time, and mismatch class.

### FTS-POI-002 — full vs minimal projection

Reference: `fields=full`.
Treatment: `fields=minimal`.

Task families:
- autocomplete display,
- category-dependent selection,
- provenance/audit,
- persistence/redistribution planning.

Measure task success and payload reduction separately.

### FTS-POI-003 — provenance reconstruction test

Construct two candidate sets with the same response-level license union but different
record-to-license assignment. Verify that minimal projection aliases them.

This is a deterministic representation-loss probe.

### FTS-POI-004 — unknown-category fallback

Compare:
- category-only,
- name/text fallback,
- address/geography fallback,
- mixed router.

Measure recall and query cost.

### FTS-CF-008 — search-k pressure sweep

Extend BENCH-007 without modifying its frozen evidence.

Sweep k across candidate counts and evaluate:
- command recall@k,
- schema tokens,
- exact-command discovery latency,
- false-match rate.

Keep current public command count versioned; do not treat "more than 2,900" as a stable
identity coordinate.

## Plugin Extensions connection

OpenAI Plugin Extensions add sidebar apps, conversation panels, file surfaces, Model-App
Context, rich forms, and other UI/context surfaces.

For this lab the important atom is:

    available UI/context surface != active tool authority

A UI projection can reduce worker friction, but server-side authorization and semantic
effect receipts remain separate responsibilities.

Reference:
https://developers.openai.com/plugins/build/extensions

## Existing work mapping

- BENCH-007 / Draft PR #15: Cloudflare `cf` capability discovery and effect-state atom.
  This intake does not supersede its frozen measurements.
- Dynamic tool-surface lifecycle:
  REGISTERED -> SEARCHABLE -> RESIDENT -> SELECTED -> CALLABLE -> STALE ->
  INVALIDATED -> REDISCOVERED.
- OpenPOI adds a parallel provenance lifecycle:
  SOURCE -> RECORD -> PROJECTION -> CONSUMER -> STORED/REDISTRIBUTED EVIDENCE.

## Cross-repository dispatch

- finite-ram-lab: treat schema/field projection as another finite working-set instance.
- mvca: transport/effect ambiguity and provenance cannot create authority.
- mvca-hq / KITten Circuit: use OpenPOI as a public transport/friction race fixture.
- catfood-jev-cua-lab: test bounded routers that decide when full provenance is required.

## Claim ceiling

    OPENPOI_TOOL_SURFACE_HYPOTHESES_DEFINED
    CLOUDFLARE_CF_EXISTING_EVIDENCE_PRESERVED

No fresh OpenPOI live-call result and no current top-k quality claim is made here.
