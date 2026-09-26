from __future__ import annotations

import hashlib
import json
import math
import random
from typing import Any

GENERATOR_VERSION = "ftsl-synthetic-v0.1"
_TASK_CODE = {"single_tool": 1, "multi_tool": 2, "no_tool": 3}


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _tool_id(index: int) -> str:
    return f"TOOL-{index:05d}"


def _cell_seed(seed: int, *, n: int, overlap: float, alias_rate: float) -> int:
    return (
        seed * 1_000_003
        + n * 101
        + int(round(overlap * 1000)) * 17
        + int(round(alias_rate * 1000)) * 19
    ) & ((1 << 63) - 1)


def generate_registry(
    *, n: int, overlap: float, alias_rate: float, seed: int
) -> dict[str, Any]:
    if n < 2:
        raise ValueError("REGISTRY_TOO_SMALL")
    if not 0.0 <= overlap <= 1.0:
        raise ValueError("OVERLAP_OUT_OF_RANGE")
    if not 0.0 <= alias_rate <= 1.0:
        raise ValueError("ALIAS_RATE_OUT_OF_RANGE")

    rng = random.Random(
        _cell_seed(seed, n=n, overlap=overlap, alias_rate=alias_rate)
    )
    family_count = max(2, int(round(math.sqrt(n))))
    shared_count = int(round(overlap * 8))
    unique_count = 8 - shared_count

    alias_target = min(n, int(round(alias_rate * n)))
    alias_indices = (
        set(rng.sample(range(n), alias_target)) if alias_target else set()
    )

    tools: list[dict[str, Any]] = []
    for index in range(n):
        family = index % family_count
        shared = [f"fam{family}_s{j}" for j in range(shared_count)]
        unique = [f"u{index}_{j}" for j in range(unique_count)]
        tokens = shared + unique + [f"family_{family}", "synthetic_tool"]

        aliases: list[str] = []
        if index in alias_indices:
            peers = [
                peer
                for peer in range(n)
                if peer != index and peer % family_count == family
            ]
            if peers:
                aliases = [f"alias_{_tool_id(rng.choice(peers))}"]

        tools.append(
            {
                "tool_id": _tool_id(index),
                "family": family,
                "description_tokens": tokens,
                "aliases": aliases,
                "serialized_stub": {
                    "name": _tool_id(index),
                    "description": " ".join(tokens + aliases),
                },
            }
        )

    return {
        "schema_version": "ftsl-synthetic-registry-v0.1",
        "generator_version": GENERATOR_VERSION,
        "n": n,
        "overlap": overlap,
        "alias_rate": alias_rate,
        "tools": tools,
    }


def generate_task(
    *,
    registry: dict[str, Any],
    task_type: str,
    repeat: int,
    seed: int,
) -> dict[str, Any]:
    if task_type not in _TASK_CODE:
        raise ValueError("UNSUPPORTED_TASK_TYPE")

    n = int(registry["n"])
    local_seed = (
        _cell_seed(
            seed,
            n=n,
            overlap=float(registry["overlap"]),
            alias_rate=float(registry["alias_rate"]),
        )
        + repeat * 23
        + _TASK_CODE[task_type]
    ) & ((1 << 63) - 1)
    rng = random.Random(local_seed)
    tools = registry["tools"]

    if task_type == "no_tool":
        gold: list[str] = []
        query_tokens = ["unmatched_concept", f"case_{repeat}"]
    elif task_type == "single_tool":
        selected = rng.choice(tools)
        gold = [selected["tool_id"]]
        query_tokens = list(selected["description_tokens"])
        rng.shuffle(query_tokens)
        query_tokens = query_tokens[: max(2, len(query_tokens) // 2)]
    else:
        selected = rng.sample(tools, 2)
        gold = sorted(tool["tool_id"] for tool in selected)
        query_tokens = (
            list(selected[0]["description_tokens"][:4])
            + list(selected[1]["description_tokens"][:4])
        )
        rng.shuffle(query_tokens)

    return {
        "task_id": (
            f"N{n}-O{float(registry['overlap']):.2f}"
            f"-A{float(registry['alias_rate']):.2f}-{task_type}-{repeat:03d}"
        ),
        "task_type": task_type,
        "query_tokens": query_tokens,
        "gold_tool_ids": gold,
    }
