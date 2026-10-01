from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Status = Literal["supported", "partial", "unsupported"]


@dataclass(frozen=True)
class CompatibilityItem:
    dimension: str
    name: str
    status: Status


@dataclass(frozen=True)
class CompatibilityProfile:
    items: tuple[CompatibilityItem, ...]

    def scalar_summary(self) -> tuple[int, int, int, int]:
        supported = sum(i.status == "supported" for i in self.items)
        partial = sum(i.status == "partial" for i in self.items)
        unsupported = sum(i.status == "unsupported" for i in self.items)
        return supported, partial, unsupported, len(self.items)

    def coordinate_vector(self) -> tuple[tuple[str, str, Status], ...]:
        return tuple(
            sorted(
                ((i.dimension, i.name, i.status) for i in self.items),
                key=lambda x: (x[0], x[1]),
            )
        )


def scalar_alias_risk(a: CompatibilityProfile, b: CompatibilityProfile) -> bool:
    return (
        a.scalar_summary() == b.scalar_summary()
        and a.coordinate_vector() != b.coordinate_vector()
    )
