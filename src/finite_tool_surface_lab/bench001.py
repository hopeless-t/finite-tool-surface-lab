from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import sys
from typing import Any, Iterable

from .bench_metrics import aggregate_rows, retrieval_frontier
from .retrieval import (
    deterministic_random_surface,
    surface_serialized_bytes,
    surface_sha256,
    token_jaccard_rank,
    token_jaccard_surface,
)
from .spec import SpecError, load_spec
from .synthetic import canonical_json_bytes, generate_registry, generate_task


def _jsonl_write(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(
                json.dumps(row, sort_keys=True, separators=(",", ":"))
                + "\n"
            )


def _evaluate_surface(
    *,
    registry: dict[str, Any],
    task: dict[str, Any],
    policy: str,
    k: int | None,
    surface: tuple[str, ...],
    top_score: float | None = None,
) -> dict[str, Any]:
    gold = set(task["gold_tool_ids"])
    hits = len(gold & set(surface))
    gold_count = len(gold)

    return {
        "task_id": task["task_id"],
        "n": registry["n"],
        "overlap": registry["overlap"],
        "alias_rate": registry["alias_rate"],
        "task_type": task["task_type"],
        "policy": policy,
        "k": k,
        "gold_count": gold_count,
        "gold_hits": hits,
        "surface_count": len(surface),
        "surface_bytes": surface_serialized_bytes(
            registry, surface
        ),
        "surface_sha256": surface_sha256(surface),
        "top_score": top_score,
    }


def _rows_for_task(
    *,
    registry: dict[str, Any],
    task: dict[str, Any],
    k_values: list[int],
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    n = registry["n"]
    gold = tuple(sorted(task["gold_tool_ids"]))
    full = tuple(tool["tool_id"] for tool in registry["tools"])
    ranked = token_jaccard_rank(registry, task)

    rows.append(
        _evaluate_surface(
            registry=registry,
            task=task,
            policy="ORACLE",
            k=None,
            surface=gold,
        )
    )
    rows.append(
        _evaluate_surface(
            registry=registry,
            task=task,
            policy="FULL",
            k=None,
            surface=full,
        )
    )

    for k in k_values:
        if k > n:
            for policy in ("RANDOM_K", "TOKEN_JACCARD"):
                invalid.append(
                    {
                        "task_id": task["task_id"],
                        "n": n,
                        "overlap": registry["overlap"],
                        "alias_rate": registry["alias_rate"],
                        "task_type": task["task_type"],
                        "policy": policy,
                        "k": k,
                        "reason": "K_GT_N",
                    }
                )
            continue

        random_surface = deterministic_random_surface(
            registry, task, k=k, seed=seed
        )
        rows.append(
            _evaluate_surface(
                registry=registry,
                task=task,
                policy="RANDOM_K",
                k=k,
                surface=random_surface,
            )
        )

        lexical_surface = token_jaccard_surface(ranked, k=k)
        rows.append(
            _evaluate_surface(
                registry=registry,
                task=task,
                policy="TOKEN_JACCARD",
                k=k,
                surface=lexical_surface,
                top_score=ranked[0][1] if ranked else None,
            )
        )

    return rows, invalid


def _expected_raw_rows(
    *,
    registry_sizes: list[int],
    k_values: list[int],
    conditions_per_n: int,
    tasks_per_condition: int,
) -> int:
    total = 0
    for n in registry_sizes:
        valid_k = sum(k <= n for k in k_values)
        total += conditions_per_n * tasks_per_condition * (
            2 + 2 * valid_k
        )
    return total


def _validate_rows(
    rows: list[dict[str, Any]],
    invalid: list[dict[str, Any]],
    spec: dict[str, Any],
    *,
    quick: bool,
) -> dict[str, bool]:
    parameters = spec["parameters"]
    registry_sizes = (
        [32] if quick else parameters["registry_sizes"]
    )
    overlap_levels = (
        [0.0, 0.75] if quick else parameters["overlap_levels"]
    )
    alias_rates = (
        [0.0, 0.15] if quick else parameters["alias_rates"]
    )
    repeats = 4 if quick else parameters["repeats_per_cell"]
    k_values = (
        [1, 3, 8, 32, 50]
        if quick
        else parameters["k_values"]
    )

    required_policies = {"ORACLE", "FULL", "RANDOM_K", "TOKEN_JACCARD"}
    observed_policies = {row["policy"] for row in rows}

    conditions_per_n = len(overlap_levels) * len(alias_rates)
    tasks_per_condition = len(parameters["task_types"]) * repeats
    expected_rows = _expected_raw_rows(
        registry_sizes=registry_sizes,
        k_values=k_values,
        conditions_per_n=conditions_per_n,
        tasks_per_condition=tasks_per_condition,
    )

    count_ok = all(
        (
            row["surface_count"] == row["gold_count"]
            if row["policy"] == "ORACLE"
            else row["surface_count"] == row["n"]
            if row["policy"] == "FULL"
            else row["surface_count"] == row["k"]
        )
        for row in rows
    )

    coverage_ok = all(
        row["gold_hits"] <= row["gold_count"]
        and row["gold_hits"] <= row["surface_count"]
        for row in rows
    )

    invalid_expected = sum(
        1
        for n in registry_sizes
        for k in k_values
        if k > n
    ) * conditions_per_n * tasks_per_condition * 2

    return {
        "required_policies_present": observed_policies == required_policies,
        "all_task_records_emitted": len(rows) == expected_rows,
        "surface_count_matches_policy_output": count_ok,
        "gold_coverage_recomputable_from_raw_records": coverage_ok,
        "invalid_k_not_silently_clipped": len(invalid) == invalid_expected,
    }


def run_benchmark(
    spec: dict[str, Any],
    *,
    quick: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    parameters = spec["parameters"]
    seed = spec["seed"]

    registry_sizes = (
        [32] if quick else parameters["registry_sizes"]
    )
    overlap_levels = (
        [0.0, 0.75] if quick else parameters["overlap_levels"]
    )
    alias_rates = (
        [0.0, 0.15] if quick else parameters["alias_rates"]
    )
    repeats = 4 if quick else parameters["repeats_per_cell"]
    k_values = (
        [1, 3, 8, 32, 50]
        if quick
        else parameters["k_values"]
    )

    rows: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []

    for n in registry_sizes:
        for overlap in overlap_levels:
            for alias_rate in alias_rates:
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
                        task_rows, task_invalid = _rows_for_task(
                            registry=registry,
                            task=task,
                            k_values=k_values,
                            seed=seed,
                        )
                        rows.extend(task_rows)
                        invalid.extend(task_invalid)

    return rows, invalid


def write_evidence(
    *,
    out_dir: Path,
    spec: dict[str, Any],
    rows: list[dict[str, Any]],
    invalid: list[dict[str, Any]],
    quick: bool,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_path = out_dir / "per_task.jsonl"
    invalid_path = out_dir / "invalid_cells.jsonl"
    aggregates_path = out_dir / "aggregates.jsonl"
    frontier_path = out_dir / "retrieval_frontier.json"

    _jsonl_write(raw_path, rows)
    _jsonl_write(invalid_path, invalid)

    aggregates = aggregate_rows(rows)
    _jsonl_write(aggregates_path, aggregates)

    frontier = retrieval_frontier(aggregates)
    frontier_path.write_text(
        json.dumps(frontier, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    reread_rows = [
        json.loads(line)
        for line in raw_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    reread_aggregates = aggregate_rows(reread_rows)

    checks = _validate_rows(
        reread_rows,
        invalid,
        spec,
        quick=quick,
    )
    checks["raw_and_aggregate_metrics_agree"] = (
        reread_aggregates == aggregates
    )
    state = "PASS" if all(checks.values()) else "FAIL"

    tool_required_groups = [
        row for row in aggregates
        if row["task_type"] != "no_tool"
    ]
    random_groups = [
        row for row in tool_required_groups
        if row["policy"] == "RANDOM_K"
    ]
    lexical_groups = [
        row for row in tool_required_groups
        if row["policy"] == "TOKEN_JACCARD"
    ]

    max_random_recall_error = max(
        abs(
            row["mean_gold_recall"]
            - row["chance_expected_recall"]
        )
        for row in random_groups
    )

    summary = {
        "study_id": "BENCH-001",
        "mode": "SMOKE" if quick else "FULL",
        "state": state,
        "checks": checks,
        "raw_rows": len(rows),
        "invalid_rows": len(invalid),
        "aggregate_rows": len(aggregates),
        "frontier_points": len(frontier),
        "max_empirical_random_recall_abs_error": (
            max_random_recall_error
        ),
        "lexical_all_gold_rate_range": [
            min(row["all_gold_rate"] for row in lexical_groups),
            max(row["all_gold_rate"] for row in lexical_groups),
        ],
        "claim_ceiling": (
            "Retrieval/surface benchmark only; no end-to-end Worker "
            "performance claim."
        ),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "schema_version": "ftsl-benchmark-manifest-v0.1",
        "study_id": "BENCH-001",
        "source_commit": os.environ.get("GITHUB_SHA", "UNKNOWN"),
        "spec_sha256": hashlib.sha256(
            canonical_json_bytes(spec)
        ).hexdigest(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "seed": spec["seed"],
        "mode": summary["mode"],
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default="specs/BENCH-001.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    try:
        spec = load_spec(args.spec)
        if spec["id"] != "BENCH-001" or spec["lane"] != "BENCH":
            raise SpecError("BENCH001_SPEC_IDENTITY")
        rows, invalid = run_benchmark(spec, quick=args.quick)
        summary = write_evidence(
            out_dir=Path(args.out),
            spec=spec,
            rows=rows,
            invalid=invalid,
            quick=args.quick,
        )
    except (SpecError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {
                    "study_id": "BENCH-001",
                    "state": "INVALID",
                    "reason": str(exc),
                },
                sort_keys=True,
            )
        )
        raise SystemExit(2)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "study_id": "BENCH-001",
                    "state": "ERROR",
                    "reason": repr(exc),
                },
                sort_keys=True,
            )
        )
        raise SystemExit(3)

    print(
        json.dumps(
            {
                key: summary[key]
                for key in (
                    "study_id",
                    "mode",
                    "state",
                    "raw_rows",
                    "invalid_rows",
                    "aggregate_rows",
                    "frontier_points",
                    "max_empirical_random_recall_abs_error",
                )
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if summary["state"] == "PASS" else 1)


if __name__ == "__main__":
    main()
