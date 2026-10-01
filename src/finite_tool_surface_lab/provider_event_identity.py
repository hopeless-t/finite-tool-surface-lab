from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProviderEventIdentity:
    canonical_session_id: str
    provider: str
    provider_session_id: str
    provider_event_id: str

    def naive_native_key(self) -> tuple[str, str]:
        """A dangerously underspecified identity: provider namespace is absent."""
        return (self.provider_session_id, self.provider_event_id)

    def canonical_coordinate(self) -> tuple[str, str, str, str]:
        return (
            self.canonical_session_id,
            self.provider,
            self.provider_session_id,
            self.provider_event_id,
        )


@dataclass(frozen=True)
class RawProviderEvent:
    identity: ProviderEventIdentity
    kind: str
    payload: Any


def provider_identity_alias_risk(a: ProviderEventIdentity, b: ProviderEventIdentity) -> bool:
    return (
        a.naive_native_key() == b.naive_native_key()
        and a.canonical_coordinate() != b.canonical_coordinate()
    )


def canonical_projection(event: RawProviderEvent) -> dict[str, object]:
    """Project raw provider data without discarding its provenance coordinate."""
    return {
        "canonical_session_id": event.identity.canonical_session_id,
        "provider": event.identity.provider,
        "provider_session_id": event.identity.provider_session_id,
        "provider_event_id": event.identity.provider_event_id,
        "kind": event.kind,
        "payload": event.payload,
    }
