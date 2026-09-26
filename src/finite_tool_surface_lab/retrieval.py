from __future__ import annotations

import hashlib
import random
from typing import Any

from .synthetic import canonical_json_bytes


def _stable_seed(*parts: object) -> int:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def _tool_tokens(tool: dict[str, Any]) -> set[str]:
    return set(tool["description_tokens"]) | set(tool["aliases"])


def token_jaccard_rank(
    registry: dict[str, Any],
    task: dict[str, Any],
) -> list[tuple[str, float]]:
    query = set(task["query_tokens"])
    scored: list[tuple[str, float]] = []
    for tool in registry["tools"]:
        tokens = _tool_tokens(tool)
        union = query | tokens
        score = len(query & tokens) / len(union) if union else 0.0
        scored.append((tool["tool_id"], score))
    scored.sort(key=lambda item: (-item[1], item[0]))
    return scored


def token_jaccard_surface(
    ranked: list[tuple[str, float]],
    *,
    k: int,
) -> tuple[str, ...]:
    if not 0 <= k <= len(ranked):
        raise ValueError("K_OUT_OF_RANGE")
    return tuple(tool_id for tool_id, _ in ranked[:k])


def deterministic_random_surface(
    registry: dict[str, Any],
    task: dict[str, Any],
    *,
    k: int,
    seed: int,
) -> tuple[str, ...]:
    ids = tuple(tool["tool_id"] for tool in registry["tools"])
    if not 0 <= k <= len(ids):
        raise ValueError("K_OUT_OF_RANGE")
    rng = random.Random(_stable_seed(seed, task["task_id"], k, "RANDOM_K"))
    return tuple(sorted(rng.sample(ids, k)))


def surface_sha256(surface: tuple[str, ...]) -> str:
    return hashlib.sha256(canonical_json_bytes(list(surface))).hexdigest()


def surface_serialized_bytes(
    registry: dict[str, Any],
    surface: tuple[str, ...],
) -> int:
    lookup = {
        tool["tool_id"]: tool["serialized_stub"]
        for tool in registry["tools"]
    }
    payload = [lookup[tool_id] for tool_id in surface]
    return len(canonical_json_bytes(payload))


def serialized_stub_byte_sizes(
    registry: dict[str, Any],
) -> dict[str, int]:
    """Precompute exact compact-JSON byte length for each serialized stub."""
    return {
        tool["tool_id"]: len(canonical_json_bytes(tool["serialized_stub"])) - 1
        for tool in registry["tools"]
    }


def surface_serialized_bytes_from_sizes(
    sizes: dict[str, int],
    surface: tuple[str, ...],
) -> int:
    """Exact byte length of canonical_json_bytes(list_of_serialized_stubs))."""
    if not surface:
        return 3  # [] plus newline
    return 3 + (len(surface) - 1) + sum(sizes[tool_id] for tool_id in surface)
