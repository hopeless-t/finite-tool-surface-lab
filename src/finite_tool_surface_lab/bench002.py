from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
import os
import platform
from pathlib import Path
import sys
from typing import Any, Iterable

from .adaptive import (
    cumulative_mass_surface,
    largest_score_drop_surface,
    positive_support_surface,
    relative_top_surface,
    tie_blocks_preserved,
)
from .bench_metrics import chance_all_gold, chance_any_gold
from .retrieval import (
    surface_serialized_bytes,
    token_jaccard_rank,
    token_jaccard_surface,
)
from .spec import SpecError, load_spec
from .synthetic import canonical_json_bytes, generate_registry, generate_task


def _policy_id(family: str, parameter: float | int | None) -> str:
    if parameter is None:
        return family
    return f"{family}:{parameter}"


def _canonical_row(
    *,
    seed: int,
    registry: dict[str, Any],
    task: dict[str, Any],
    family: str,
    parameter: float | int | None,
    surface: tuple[str, ...],
    ranked: list[tuple[str, float]],
) -> dict[str, Any]:
    gold = set(task["gold_tool_ids"])
    hits = len(gold & set(surface))
    gold_count = len(gold)
    selected_k = len(surface)
    top_score = ranked[0][1] if ranked else 0.0
    positive_support = sum(score > 0.0 for _, score in ranked)

    return {
        "seed": seed,
        "task_id": task["task_id"],
        "n": registry["n"],
        "overlap": registry["overlap"],
        "alias_rate": registry["alias_rate"],
        "task_type": task["task_type"],
        "policy_family": family,
        "policy_parameter": parameter,
        "policy_id": _policy_id(family, parameter),
        "selected_k": selected_k,
        "surface_bytes": surface_serialized_bytes(registry, surface),
        "gold_count": gold_count,
        "gold_hits": hits,
        "top_score": top_score,
        "positive_support": positive_support,
        "tie_blocks_preserved": tie_blocks_preserved(ranked, surface)
        if family not in {"ORACLE", "FULL", "FIXED_K"}
        else True,
    }


def _surfaces(
    *,
    registry: dict[str, Any],
    task: dict[str, Any],
    ranked: list[tuple[str, float]],
    spec: dict[str, Any],
) -> Iterable[tuple[str, float | int | None, tuple[str, ...]]]:
    ids = tuple(tool["tool_id"] for tool in registry["tools"])
    gold = tuple(sorted(task["gold_tool_ids"]))

    yield "ORACLE", None, gold
    yield "FULL", None, ids

    for k in spec["parameters"]["fixed_k_values"]:
        if k <= registry["n"]:
            yield "FIXED_K", k, token_jaccard_surface(ranked, k=k)

    yield "POSITIVE_SUPPORT", None, positive_support_surface(ranked)

    for threshold in spec["parameters"]["relative_top_thresholds"]:
        yield (
            "RELATIVE_TOP",
            threshold,
            relative_top_surface(ranked, threshold=threshold),
        )

    for threshold in spec["parameters"]["cumulative_mass_thresholds"]:
        yield (
            "CUMULATIVE_SCORE_MASS",
            threshold,
            cumulative_mass_surface(ranked, threshold=threshold),
        )

    yield "LARGEST_SCORE_DROP", None, largest_score_drop_surface(ranked)


def _accumulator() -> dict[str, Any]:
    return {
        "tasks": 0,
        "sum_selected_k": 0,
        "sum_surface_bytes": 0,
        "sum_gold_hits": 0,
        "sum_gold_count": 0,
        "tool_required": 0,
        "any_gold_hits": 0,
        "all_gold_hits": 0,
        "no_tool_nonempty": 0,
        "sum_chance_recall": 0.0,
        "sum_chance_any": 0.0,
        "sum_chance_all": 0.0,
    }


def _aggregate_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["n"],
        row["overlap"],
        row["alias_rate"],
        row["task_type"],
        row["policy_family"],
        row["policy_parameter"],
    )


def _update(acc: dict[str, Any], row: dict[str, Any]) -> None:
    acc["tasks"] += 1
    acc["sum_selected_k"] += row["selected_k"]
    acc["sum_surface_bytes"] += row["surface_bytes"]

    if row["gold_count"] > 0:
        acc["tool_required"] += 1
        acc["sum_gold_hits"] += row["gold_hits"]
        acc["sum_gold_count"] += row["gold_count"]
        acc["any_gold_hits"] += int(row["gold_hits"] > 0)
        acc["all_gold_hits"] += int(
            row["gold_hits"] == row["gold_count"]
        )

        if row["policy_family"] != "ORACLE":
            n = row["n"]
            k = row["selected_k"]
            g = row["gold_count"]
            acc["sum_chance_recall"] += k / n
            acc["sum_chance_any"] += chance_any_gold(
                n=n, k=k, gold_count=g
            )
            acc["sum_chance_all"] += chance_all_gold(
                n=n, k=k, gold_count=g
            )
    else:
        acc["no_tool_nonempty"] += int(row["selected_k"] > 0)


def _finish(
    accumulators: dict[tuple[Any, ...], dict[str, Any]]
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key in sorted(
        accumulators,
        key=lambda x: (
            x[0], x[1], x[2], x[3], x[4],
            "" if x[5] is None else str(x[5]),
        ),
    ):
        n, overlap, alias_rate, task_type, family, parameter = key
        acc = accumulators[key]
        tasks = acc["tasks"]
        required = acc["tool_required"]
        row: dict[str, Any] = {
            "n": n,
            "overlap": overlap,
            "alias_rate": alias_rate,
            "task_type": task_type,
            "policy_family": family,
            "policy_parameter": parameter,
            "policy_id": _policy_id(family, parameter),
            "tasks": tasks,
            "mean_selected_k": acc["sum_selected_k"] / tasks,
            "mean_surface_bytes": acc["sum_surface_bytes"] / tasks,
            "mean_gold_recall": None,
            "any_gold_rate": None,
            "all_gold_rate": None,
            "no_tool_nonempty_surface_rate": None,
            "mean_chance_recall": None,
            "mean_chance_any_gold_rate": None,
            "mean_chance_all_gold_rate": None,
            "bits_over_random_any_gold": None,
        }

        if required:
            row["mean_gold_recall"] = (
                acc["sum_gold_hits"] / acc["sum_gold_count"]
            )
            row["any_gold_rate"] = acc["any_gold_hits"] / required
            row["all_gold_rate"] = acc["all_gold_hits"] / required
            if family != "ORACLE":
                chance_any = acc["sum_chance_any"] / required
                row["mean_chance_recall"] = (
                    acc["sum_chance_recall"] / required
                )
                row["mean_chance_any_gold_rate"] = chance_any
                row["mean_chance_all_gold_rate"] = (
                    acc["sum_chance_all"] / required
                )
                if row["any_gold_rate"] > 0 and chance_any > 0:
                    row["bits_over_random_any_gold"] = math.log2(
                        row["any_gold_rate"] / chance_any
                    )
        else:
            row["no_tool_nonempty_surface_rate"] = (
                acc["no_tool_nonempty"] / tasks
            )

        out.append(row)
    return out


def _frontier(aggregates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in aggregates:
        if row["task_type"] == "no_tool":
            continue
        if row["policy_family"] == "ORACLE":
            continue
        grouped[
            (row["n"], row["overlap"], row["alias_rate"], row["task_type"])
        ].append(row)

    result: list[dict[str, Any]] = []
    for condition, points in grouped.items():
        for point in points:
            dominated = False
            for other in points:
                if other is point:
                    continue
                no_worse = (
                    other["all_gold_rate"] >= point["all_gold_rate"]
                    and other["mean_selected_k"] <= point["mean_selected_k"]
                    and other["mean_surface_bytes"] <= point["mean_surface_bytes"]
                )
                strictly = (
                    other["all_gold_rate"] > point["all_gold_rate"]
                    or other["mean_selected_k"] < point["mean_selected_k"]
                    or other["mean_surface_bytes"] < point["mean_surface_bytes"]
                )
                if no_worse and strictly:
                    dominated = True
                    break
            if not dominated:
                result.append(
                    {
                        "n": condition[0],
                        "overlap": condition[1],
                        "alias_rate": condition[2],
                        "task_type": condition[3],
                        "policy_family": point["policy_family"],
                        "policy_parameter": point["policy_parameter"],
                        "policy_id": point["policy_id"],
                        "all_gold_rate": point["all_gold_rate"],
                        "mean_selected_k": point["mean_selected_k"],
                        "mean_surface_bytes": point["mean_surface_bytes"],
                    }
                )

    result.sort(
        key=lambda row: (
            row["n"], row["overlap"], row["alias_rate"],
            row["task_type"], row["mean_selected_k"], row["policy_id"],
        )
    )
    return result


def _msts(
    aggregates: list[dict[str, Any]],
    epsilons: list[float],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in aggregates:
        if row["task_type"] == "no_tool":
            continue
        if row["policy_family"] == "ORACLE":
            continue
        grouped[
            (row["n"], row["overlap"], row["alias_rate"], row["task_type"])
        ].append(row)

    result: list[dict[str, Any]] = []
    for condition, points in grouped.items():
        for epsilon in epsilons:
            eligible = [
                point for point in points
                if point["all_gold_rate"] >= 1.0 - epsilon
            ]
            if not eligible:
                result.append(
                    {
                        "n": condition[0],
                        "overlap": condition[1],
                        "alias_rate": condition[2],
                        "task_type": condition[3],
                        "epsilon": epsilon,
                        "policy_id": None,
                        "mean_selected_k": None,
                        "mean_surface_bytes": None,
                    }
                )
                continue
            best = min(
                eligible,
                key=lambda row: (
                    row["mean_surface_bytes"],
                    row["mean_selected_k"],
                    row["policy_id"],
                ),
            )
            result.append(
                {
                    "n": condition[0],
                    "overlap": condition[1],
                    "alias_rate": condition[2],
                    "task_type": condition[3],
                    "epsilon": epsilon,
                    "policy_id": best["policy_id"],
                    "mean_selected_k": best["mean_selected_k"],
                    "mean_surface_bytes": best["mean_surface_bytes"],
                }
            )
    return result


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(
                json.dumps(row, sort_keys=True, separators=(",", ":"))
                + "\n"
            )


def run_benchmark(
    spec: dict[str, Any],
    *,
    quick: bool = False,
) -> tuple[list[dict[str, Any]], str, int, dict[str, bool]]:
    parameters = spec["parameters"]
    seeds = (
        [parameters["evaluation_seeds"][0]]
        if quick else parameters["evaluation_seeds"]
    )
    registry_sizes = [32] if quick else parameters["registry_sizes"]
    overlaps = [0.0, 0.75] if quick else parameters["overlap_levels"]
    aliases = [0.0, 0.15] if quick else parameters["alias_rates"]
    repeats = 4 if quick else parameters["repeats_per_cell"]

    if quick:
        spec = json.loads(json.dumps(spec))
        spec["parameters"]["fixed_k_values"] = [0, 1, 3, 8, 32, 50]
        spec["parameters"]["relative_top_thresholds"] = [0.5, 0.9]
        spec["parameters"]["cumulative_mass_thresholds"] = [0.7, 0.9]

    accumulators: dict[tuple[Any, ...], dict[str, Any]] = defaultdict(
        _accumulator
    )
    observation_hash = hashlib.sha256()
    observation_count = 0
    selected_k_ok = True
    zero_abstain_ok = True
    tie_ok = True
    seen_families: set[str] = set()

    for seed in seeds:
        for n in registry_sizes:
            for overlap in overlaps:
                for alias_rate in aliases:
                    registry = generate_registry(
                        n=n,
                        overlap=overlap,
                        alias_rate=alias_rate,
                        seed=seed,
                    )
                    for task_type in parameters["task_types"]:
                        for repeat in range(repeats):
                            task = generate_task(
                                registry=registry,
                                task_type=task_type,
                                repeat=repeat,
                                seed=seed,
                            )
                            ranked = token_jaccard_rank(registry, task)
                            for family, parameter, surface in _surfaces(
                                registry=registry,
                                task=task,
                                ranked=ranked,
                                spec=spec,
                            ):
                                row = _canonical_row(
                                    seed=seed,
                                    registry=registry,
                                    task=task,
                                    family=family,
                                    parameter=parameter,
                                    surface=surface,
                                    ranked=ranked,
                                )
                                observation_hash.update(canonical_json_bytes(row))
                                observation_count += 1
                                seen_families.add(family)
                                selected_k_ok &= 0 <= row["selected_k"] <= n
                                tie_ok &= row["tie_blocks_preserved"]

                                if (
                                    family not in {"ORACLE", "FULL", "FIXED_K"}
                                    and row["top_score"] == 0.0
                                ):
                                    zero_abstain_ok &= row["selected_k"] == 0

                                _update(accumulators[_aggregate_key(row)], row)

    aggregates = _finish(accumulators)
    required = {
        "ORACLE",
        "FULL",
        "FIXED_K",
        "POSITIVE_SUPPORT",
        "RELATIVE_TOP",
        "CUMULATIVE_SCORE_MASS",
        "LARGEST_SCORE_DROP",
    }
    aggregate_task_counts_ok = all(
        row["tasks"] == len(seeds) * repeats for row in aggregates
    )

    checks = {
        "observation_digest_present": observation_count > 0,
        "selected_k_within_registry": bool(selected_k_ok),
        "adaptive_zero_evidence_abstains": bool(zero_abstain_ok),
        "tie_blocks_not_split": bool(tie_ok),
        "all_policy_families_present": seen_families == required,
        "aggregate_task_counts_match": bool(aggregate_task_counts_ok),
    }
    return (
        aggregates,
        observation_hash.hexdigest(),
        observation_count,
        checks,
    )


def write_evidence(
    *,
    out_dir: Path,
    spec: dict[str, Any],
    aggregates: list[dict[str, Any]],
    observation_digest: str,
    observation_count: int,
    checks: dict[str, bool],
    quick: bool,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    frontier = _frontier(aggregates)
    msts = _msts(
        aggregates,
        [float(x) for x in spec["parameters"]["msts_epsilons"]],
    )

    _write_jsonl(out_dir / "aggregates.jsonl", aggregates)
    (out_dir / "frontier.json").write_text(
        json.dumps(frontier, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "msts.json").write_text(
        json.dumps(msts, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "observation_digest.json").write_text(
        json.dumps(
            {
                "algorithm": "sha256",
                "canonical_row_encoding": (
                    "sorted-key compact UTF-8 JSON plus newline"
                ),
                "observation_count": observation_count,
                "sha256": observation_digest,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    adaptive_frontier = sum(
        row["policy_family"]
        not in {"FULL", "FIXED_K"}
        for row in frontier
    )
    fixed_frontier = sum(
        row["policy_family"] in {"FULL", "FIXED_K"}
        for row in frontier
    )
    no_tool_adaptive = [
        row for row in aggregates
        if row["task_type"] == "no_tool"
        and row["policy_family"]
        not in {"ORACLE", "FULL", "FIXED_K"}
    ]
    checks = dict(checks)
    checks["frontier_recomputable"] = len(frontier) > 0
    state = "PASS" if all(checks.values()) else "FAIL"

    summary = {
        "study_id": "BENCH-002",
        "mode": "SMOKE" if quick else "FULL",
        "state": state,
        "checks": checks,
        "observation_count": observation_count,
        "observation_sha256": observation_digest,
        "aggregate_rows": len(aggregates),
        "frontier_points": len(frontier),
        "adaptive_frontier_points": adaptive_frontier,
        "fixed_or_full_frontier_points": fixed_frontier,
        "adaptive_no_tool_nonempty_rate_range": [
            min(
                row["no_tool_nonempty_surface_rate"]
                for row in no_tool_adaptive
            ),
            max(
                row["no_tool_nonempty_surface_rate"]
                for row in no_tool_adaptive
            ),
        ],
        "claim_ceiling": spec["claim_ceiling"],
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "schema_version": "ftsl-benchmark-manifest-v0.1",
        "study_id": "BENCH-002",
        "source_commit": os.environ.get("GITHUB_SHA", "UNKNOWN"),
        "spec_sha256": hashlib.sha256(
            canonical_json_bytes(spec)
        ).hexdigest(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "mode": summary["mode"],
        "evaluation_seeds": (
            [spec["parameters"]["evaluation_seeds"][0]]
            if quick
            else spec["parameters"]["evaluation_seeds"]
        ),
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default="specs/BENCH-002.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    try:
        spec = load_spec(args.spec)
        if spec["id"] != "BENCH-002" or spec["lane"] != "BENCH":
            raise SpecError("BENCH002_SPEC_IDENTITY")
        aggregates, digest, count, checks = run_benchmark(
            spec, quick=args.quick
        )
        summary = write_evidence(
            out_dir=Path(args.out),
            spec=spec,
            aggregates=aggregates,
            observation_digest=digest,
            observation_count=count,
            checks=checks,
            quick=args.quick,
        )
    except (SpecError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "study_id": "BENCH-002",
            "state": "INVALID",
            "reason": str(exc),
        }, sort_keys=True))
        raise SystemExit(2)
    except Exception as exc:
        print(json.dumps({
            "study_id": "BENCH-002",
            "state": "ERROR",
            "reason": repr(exc),
        }, sort_keys=True))
        raise SystemExit(3)

    print(json.dumps({
        key: summary[key]
        for key in (
            "study_id",
            "mode",
            "state",
            "observation_count",
            "aggregate_rows",
            "frontier_points",
            "adaptive_frontier_points",
        )
    }, sort_keys=True))
    raise SystemExit(0 if summary["state"] == "PASS" else 1)


if __name__ == "__main__":
    main()
