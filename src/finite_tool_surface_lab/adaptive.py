from __future__ import annotations

from typing import Iterable


Ranked = list[tuple[str, float]]


def _positive_prefix(ranked: Ranked) -> Ranked:
    return [(tool_id, score) for tool_id, score in ranked if score > 0.0]


def _surface_from_count_with_ties(
    ranked: Ranked,
    count: int,
) -> tuple[str, ...]:
    positive = _positive_prefix(ranked)
    if count <= 0 or not positive:
        return ()
    if count >= len(positive):
        return tuple(tool_id for tool_id, _ in positive)

    cutoff = positive[count - 1][1]
    return tuple(
        tool_id for tool_id, score in positive if score >= cutoff
    )


def positive_support_surface(ranked: Ranked) -> tuple[str, ...]:
    return tuple(tool_id for tool_id, _ in _positive_prefix(ranked))


def relative_top_surface(
    ranked: Ranked,
    *,
    threshold: float,
) -> tuple[str, ...]:
    if not 0.0 < threshold <= 1.0:
        raise ValueError("RELATIVE_TOP_THRESHOLD")
    positive = _positive_prefix(ranked)
    if not positive:
        return ()
    cutoff = positive[0][1] * threshold
    return tuple(
        tool_id for tool_id, score in positive if score >= cutoff
    )


def cumulative_mass_surface(
    ranked: Ranked,
    *,
    threshold: float,
) -> tuple[str, ...]:
    if not 0.0 < threshold <= 1.0:
        raise ValueError("CUMULATIVE_MASS_THRESHOLD")
    positive = _positive_prefix(ranked)
    if not positive:
        return ()

    total = sum(score for _, score in positive)
    target = total * threshold
    running = 0.0
    count = 0
    for _, score in positive:
        running += score
        count += 1
        if running >= target:
            break
    return _surface_from_count_with_ties(positive, count)


def largest_score_drop_surface(ranked: Ranked) -> tuple[str, ...]:
    positive = _positive_prefix(ranked)
    if len(positive) <= 1:
        return tuple(tool_id for tool_id, _ in positive)

    drops = [
        positive[index][1] - positive[index + 1][1]
        for index in range(len(positive) - 1)
    ]
    largest = max(drops)
    if largest <= 0.0:
        return tuple(tool_id for tool_id, _ in positive)

    count = drops.index(largest) + 1
    return _surface_from_count_with_ties(positive, count)


def tie_blocks_preserved(
    ranked: Ranked,
    surface: Iterable[str],
) -> bool:
    selected = set(surface)
    by_score: dict[float, set[str]] = {}
    for tool_id, score in ranked:
        if score <= 0.0:
            continue
        by_score.setdefault(score, set()).add(tool_id)

    return all(
        not (selected & block) or block <= selected
        for block in by_score.values()
    )
