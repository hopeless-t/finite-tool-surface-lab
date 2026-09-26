from __future__ import annotations

from collections import defaultdict
import math
from typing import Any, Iterable


def chance_any_gold(*, n: int, k: int, gold_count: int) -> float:
    if gold_count <= 0:
        raise ValueError("NO_GOLD_FOR_CHANCE")
    if not 0 <= k <= n:
        raise ValueError("K_OUT_OF_RANGE")
    if k == 0:
        return 0.0
    if n - gold_count < k:
        return 1.0
    return 1.0 - math.comb(n - gold_count, k) / math.comb(n, k)


def chance_all_gold(*, n: int, k: int, gold_count: int) -> float:
    if gold_count <= 0:
        raise ValueError("NO_GOLD_FOR_CHANCE")
    if not 0 <= k <= n:
        raise ValueError("K_OUT_OF_RANGE")
    if k < gold_count:
        return 0.0
    return (
        math.comb(n - gold_count, k - gold_count)
        / math.comb(n, k)
    )


def _key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["n"],
        row["overlap"],
        row["alias_rate"],
        row["task_type"],
        row["policy"],
        row["k"],
    )


def aggregate_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    acc: dict[tuple[Any, ...], dict[str, Any]] = defaultdict(
        lambda: {
            "tasks": 0,
            "sum_surface_count": 0,
            "sum_surface_bytes": 0,
            "tool_required": 0,
            "sum_gold_hits": 0,
            "sum_gold_count": 0,
            "any_gold_hits": 0,
            "all_gold_hits": 0,
            "no_tool_nonempty": 0,
        }
    )

    for row in rows:
        item = acc[_key(row)]
        item["tasks"] += 1
        item["sum_surface_count"] += row["surface_count"]
        item["sum_surface_bytes"] += row["surface_bytes"]

        if row["gold_count"] > 0:
            item["tool_required"] += 1
            item["sum_gold_hits"] += row["gold_hits"]
            item["sum_gold_count"] += row["gold_count"]
            item["any_gold_hits"] += int(row["gold_hits"] > 0)
            item["all_gold_hits"] += int(
                row["gold_hits"] == row["gold_count"]
            )
        else:
            item["no_tool_nonempty"] += int(
                row["surface_count"] > 0
            )

    results: list[dict[str, Any]] = []
    for key in sorted(
        acc,
        key=lambda x: (
            x[0], x[1], x[2], x[3], x[4], -1 if x[5] is None else x[5]
        ),
    ):
        n, overlap, alias_rate, task_type, policy, k = key
        item = acc[key]
        tasks = item["tasks"]
        tool_required = item["tool_required"]

        result: dict[str, Any] = {
            "n": n,
            "overlap": overlap,
            "alias_rate": alias_rate,
            "task_type": task_type,
            "policy": policy,
            "k": k,
            "tasks": tasks,
            "mean_surface_count": item["sum_surface_count"] / tasks,
            "mean_surface_bytes": item["sum_surface_bytes"] / tasks,
            "mean_gold_recall": None,
            "any_gold_rate": None,
            "all_gold_rate": None,
            "no_tool_nonempty_surface_rate": None,
            "chance_expected_recall": None,
            "chance_any_gold_rate": None,
            "chance_all_gold_rate": None,
            "bits_over_random_any_gold": None,
        }

        if tool_required:
            result["mean_gold_recall"] = (
                item["sum_gold_hits"] / item["sum_gold_count"]
            )
            result["any_gold_rate"] = (
                item["any_gold_hits"] / tool_required
            )
            result["all_gold_rate"] = (
                item["all_gold_hits"] / tool_required
            )

            if k is not None:
                gold_count = 1 if task_type == "single_tool" else 2
                p_any = chance_any_gold(
                    n=n, k=k, gold_count=gold_count
                )
                p_all = chance_all_gold(
                    n=n, k=k, gold_count=gold_count
                )
                result["chance_expected_recall"] = k / n
                result["chance_any_gold_rate"] = p_any
                result["chance_all_gold_rate"] = p_all

                observed = result["any_gold_rate"]
                if observed is not None and observed > 0 and p_any > 0:
                    result["bits_over_random_any_gold"] = math.log2(
                        observed / p_any
                    )
        else:
            result["no_tool_nonempty_surface_rate"] = (
                item["no_tool_nonempty"] / tasks
            )

        results.append(result)

    return results


def retrieval_frontier(
    aggregates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)

    for row in aggregates:
        if row["task_type"] == "no_tool":
            continue
        if row["policy"] == "ORACLE":
            continue
        grouped[
            (
                row["n"],
                row["overlap"],
                row["alias_rate"],
                row["task_type"],
            )
        ].append(row)

    frontier: list[dict[str, Any]] = []
    for condition, points in grouped.items():
        for point in points:
            dominated = False
            for other in points:
                if other is point:
                    continue
                no_worse = (
                    other["all_gold_rate"] >= point["all_gold_rate"]
                    and other["mean_surface_count"]
                    <= point["mean_surface_count"]
                    and other["mean_surface_bytes"]
                    <= point["mean_surface_bytes"]
                )
                strictly_better = (
                    other["all_gold_rate"] > point["all_gold_rate"]
                    or other["mean_surface_count"]
                    < point["mean_surface_count"]
                    or other["mean_surface_bytes"]
                    < point["mean_surface_bytes"]
                )
                if no_worse and strictly_better:
                    dominated = True
                    break

            if not dominated:
                frontier.append(
                    {
                        "n": condition[0],
                        "overlap": condition[1],
                        "alias_rate": condition[2],
                        "task_type": condition[3],
                        "policy": point["policy"],
                        "k": point["k"],
                        "all_gold_rate": point["all_gold_rate"],
                        "mean_surface_count": point["mean_surface_count"],
                        "mean_surface_bytes": point["mean_surface_bytes"],
                    }
                )

    frontier.sort(
        key=lambda row: (
            row["n"],
            row["overlap"],
            row["alias_rate"],
            row["task_type"],
            row["mean_surface_count"],
            row["policy"],
            -1 if row["k"] is None else row["k"],
        )
    )
    return frontier
