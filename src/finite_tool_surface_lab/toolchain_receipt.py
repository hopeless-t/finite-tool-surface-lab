from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class ToolComponent:
    name: str
    version: str


@dataclass(frozen=True)
class ToolchainReceipt:
    surface: str
    components: tuple[ToolComponent, ...]

    def semantic_payload(self) -> dict[str, object]:
        return {
            "surface": self.surface,
            "components": [
                {"name": c.name, "version": c.version}
                for c in sorted(self.components, key=lambda x: x.name)
            ],
        }

    def semantic_sha256(self) -> str:
        raw = json.dumps(
            self.semantic_payload(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        return sha256(raw).hexdigest()


def same_surface_different_toolchain(
    a: ToolchainReceipt, b: ToolchainReceipt
) -> bool:
    return a.surface == b.surface and a.semantic_sha256() != b.semantic_sha256()
