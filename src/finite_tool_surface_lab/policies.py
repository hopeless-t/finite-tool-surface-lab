from __future__ import annotations

import math
import random
from typing import Any


def registry_tool_ids(registry: dict[str, Any]) -> tuple[str, ...]:
    return tuple(tool["tool_id"] for tool in registry["tools"])


def oracle_surface(task: dict[str, Any]) -> tuple[str, ...]:
    return tuple(sorted(task["gold_tool_ids"]))


def full_surface(registry: dict[str, Any]) -> tuple[str, ...]:
    return tuple(sorted(registry_tool_ids(registry)))


def random_k_surface(
    registry: dict[str, Any], *, k: int, rng: random.Random
) -> tuple[str, ...]:
    ids = registry_tool_ids(registry)
    if not 0 <= k <= len(ids):
        raise ValueError("K_OUT_OF_RANGE")
    return tuple(sorted(rng.sample(ids, k)))


def expected_random_recall(*, n: int, k: int, gold_count: int) -> float:
    if not 0 <= gold_count <= n:
        raise ValueError("GOLD_COUNT_OUT_OF_RANGE")
    if not 0 <= k <= n:
        raise ValueError("K_OUT_OF_RANGE")
    return 1.0 if gold_count == 0 else k / n


def probability_random_contains_all(
    *, n: int, k: int, gold_count: int
) -> float:
    if not 0 <= gold_count <= n:
        raise ValueError("GOLD_COUNT_OUT_OF_RANGE")
    if not 0 <= k <= n:
        raise ValueError("K_OUT_OF_RANGE")
    if gold_count == 0:
        return 1.0
    if k < gold_count:
        return 0.0
    return math.comb(n - gold_count, k - gold_count) / math.comb(n, k)


def gold_recall(surface: tuple[str, ...], gold: tuple[str, ...]) -> float:
    return 1.0 if not gold else len(set(surface) & set(gold)) / len(gold)


def contains_all_gold(surface: tuple[str, ...], gold: tuple[str, ...]) -> bool:
    return set(gold) <= set(surface)
