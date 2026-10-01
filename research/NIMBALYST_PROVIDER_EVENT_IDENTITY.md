# NIM-001 — Provider-native identity and canonical event projection

Date: 2026-10-02

Primary source inspected:
- Nimbalyst `design/agents/agent-provider-architecture.md`
- source blob: `69c87dee79c02c81ebc0facc0e308ecf1ba64111`
- https://github.com/Nimbalyst/nimbalyst/blob/main/design/agents/agent-provider-architecture.md

## Source atoms

Nimbalyst separates:
- a high-level `AIProvider` from a transport-facing `AgentProtocol`;
- its own durable canonical `sessionId` from the provider-native `provider_session_id`;
- append-only provider-native raw messages from a canonical UI-facing transcript projection.

Its design explicitly says the canonical and provider session identifiers are not interchangeable. Raw messages are preserved as source-of-truth provider payloads and canonical events are derived through provider-specific parsers / a versioned transformer.

## Catfood atom

```
provider-native identity
!=
canonical identity
```

A native pair such as:

```
(provider_session_id="42", provider_event_id="evt-7")
```

is not globally injective. Another provider may emit the same pair.

A safer event coordinate is:

```
(
  canonical_session_id,
  provider,
  provider_session_id,
  provider_event_id,
)
```

This is another concrete KITten-Coordinate / representation-alias case: the basis must carry enough namespace/provenance coordinates to distinguish states that matter.

## Projection rule

Keep provider-native raw evidence immutable/append-only and treat normalized/canonical events as a rebuildable projection.

This gives two useful properties:
1. parser/normalizer fixes do not require replaying the external provider;
2. normalization bugs cannot erase the original provider-native evidence.

## Minimal probe

`provider_event_identity.py` demonstrates:
- a naive native key collision across two providers;
- a representation-aware canonical coordinate that separates them;
- a projection that preserves provider identity and native ids.

## Claim ceiling

This does not copy Nimbalyst runtime code and does not claim MVCA currently needs Nimbalyst as a dependency.

Catfood verdict: **KEEP the identity/projection atoms; do not import the product.**
