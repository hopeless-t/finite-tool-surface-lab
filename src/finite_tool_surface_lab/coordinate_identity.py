from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CoordinateProfile:
    outer_api: str
    value_dtype: str
    backend: str
    scale_encoding: str
    scale_layout: str

    def naive_surface_key(self) -> tuple[str, str]:
        """What a backend-blind compatibility layer might incorrectly use."""
        return (self.outer_api, self.value_dtype)

    def coordinate_signature(self) -> tuple[str, str, str, str, str]:
        """Representation-aware identity for a computation coordinate."""
        return (
            self.outer_api,
            self.value_dtype,
            self.backend,
            self.scale_encoding,
            self.scale_layout,
        )


def representation_alias_risk(a: CoordinateProfile, b: CoordinateProfile) -> bool:
    """True when two distinct representations collapse under an outer-API-only key."""
    return (
        a.naive_surface_key() == b.naive_surface_key()
        and a.coordinate_signature() != b.coordinate_signature()
    )
