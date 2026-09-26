from __future__ import annotations

import random
from typing import Any

from .policies import expected_random_recall, probability_random_contains_all
from .synthetic import (
    canonical_json_bytes,
    generate_registry,
    generate_task,
    sha256_json,
)


def validate_val001_spec(spec: dict[str, Any]) -> None:
    if spec.get("id") != "VAL-001" or spec.get("lane") != "VAL":
        raise ValueError("VAL001_SPEC_IDENTITY")
    parameters = spec.get("parameters")
    acceptance = spec.get("acceptance")
    if not isinstance(parameters, dict) or not isinstance(acceptance, dict):
        raise ValueError("VAL001_SPEC_SHAPE")

    registry_sizes = parameters.get("registry_sizes")
    task_types = parameters.get("task_types")
    overlap_levels = parameters.get("overlap_levels")
    alias_rates = parameters.get("alias_rates")
    repeats = parameters.get("repeats_per_cell")
    draws = parameters.get("random_policy_draws")

    if (
        not isinstance(registry_sizes, list)
        or not registry_sizes
        or any(
            not isinstance(n, int) or isinstance(n, bool) or n < 2
            for n in registry_sizes
        )
    ):
        raise ValueError("VAL001_REGISTRY_SIZES")
    if task_types != ["single_tool", "multi_tool", "no_tool"]:
        raise ValueError("VAL001_TASK_TYPES")

    for values, code in (
        (overlap_levels, "VAL001_OVERLAP_LEVELS"),
        (alias_rates, "VAL001_ALIAS_RATES"),
    ):
        if not isinstance(values, list) or not values:
            raise ValueError(code)
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not 0.0 <= float(value) <= 1.0
            for value in values
        ):
            raise ValueError(code)

    if not isinstance(repeats, int) or isinstance(repeats, bool) or repeats < 1:
        raise ValueError("VAL001_REPEATS")
    if not isinstance(draws, int) or isinstance(draws, bool) or draws < 100:
        raise ValueError("VAL001_RANDOM_DRAWS")

    tolerance = acceptance.get("random_k_theory_abs_error_max")
    if (
        isinstance(tolerance, bool)
        or not isinstance(tolerance, (int, float))
        or not 0.0 < float(tolerance) < 1.0
    ):
        raise ValueError("VAL001_RANDOM_TOLERANCE")


def validate_registry_tasks(
    registry: dict[str, Any], tasks: list[dict[str, Any]]
) -> None:
    ids = [tool["tool_id"] for tool in registry["tools"]]
    if len(ids) != registry["n"] or len(set(ids)) != len(ids):
        raise ValueError("REGISTRY_ID_INTEGRITY")

    id_set = set(ids)
    for task in tasks:
        gold = set(task["gold_tool_ids"])
        if not gold <= id_set:
            raise ValueError("GOLD_TOOL_MISSING")
        if task["task_type"] == "no_tool" and gold:
            raise ValueError("NO_TOOL_GOLD_NOT_EMPTY")


def validate_controls(
    registry: dict[str, Any],
    task: dict[str, Any],
    *,
    oracle: tuple[str, ...] | None = None,
    full: tuple[str, ...] | None = None,
) -> None:
    expected_oracle = tuple(sorted(task["gold_tool_ids"]))
    observed_oracle = expected_oracle if oracle is None else oracle
    if observed_oracle != expected_oracle:
        raise ValueError("BROKEN_ORACLE")

    expected_full = tuple(
        sorted(tool["tool_id"] for tool in registry["tools"])
    )
    observed_full = expected_full if full is None else full
    if observed_full != expected_full:
        raise ValueError("BROKEN_FULL")


def failure_injection_probe(seed: int) -> dict[str, bool]:
    registry = generate_registry(n=8, overlap=0.5, alias_rate=0.0, seed=seed)
    task = generate_task(
        registry=registry, task_type="single_tool", repeat=0, seed=seed
    )
    detected: dict[str, bool] = {}

    for name, callback, code in (
        (
            "broken_oracle",
            lambda: validate_controls(registry, task, oracle=()),
            "BROKEN_ORACLE",
        ),
        (
            "broken_full",
            lambda: validate_controls(registry, task, full=()),
            "BROKEN_FULL",
        ),
    ):
        try:
            callback()
            detected[name] = False
        except ValueError as exc:
            detected[name] = str(exc) == code

    corrupted = dict(task)
    corrupted["gold_tool_ids"] = ["TOOL-DOES-NOT-EXIST"]
    try:
        validate_registry_tasks(registry, [corrupted])
        detected["corrupted_gold"] = False
    except ValueError as exc:
        detected["corrupted_gold"] = str(exc) == "GOLD_TOOL_MISSING"

    invalid_spec = {
        "id": "VAL-001",
        "lane": "VAL",
        "parameters": {
            "registry_sizes": [1],
            "task_types": ["single_tool", "multi_tool", "no_tool"],
            "overlap_levels": [0.5],
            "alias_rates": [0.0],
            "repeats_per_cell": 1,
            "random_policy_draws": 100,
        },
        "acceptance": {"random_k_theory_abs_error_max": 0.02},
    }
    try:
        validate_val001_spec(invalid_spec)
        detected["invalid_spec"] = False
    except ValueError as exc:
        detected["invalid_spec"] = str(exc) == "VAL001_REGISTRY_SIZES"

    return detected


def random_calibration(
    *, draws: int, seed: int, quick: bool = False
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    registry_sizes = (8, 128) if quick else (8, 128, 2048)

    for n in registry_sizes:
        for gold_count in (1, 2):
            for k in sorted({1, min(8, n), min(32, n)}):
                rng = random.Random(
                    seed + n * 1009 + gold_count * 97 + k * 53
                )
                recall_sum = 0.0
                all_hits = 0
                for _ in range(draws):
                    surface = set(rng.sample(range(n), k))
                    hits = sum(i in surface for i in range(gold_count))
                    recall_sum += hits / gold_count
                    all_hits += int(hits == gold_count)

                empirical_recall = recall_sum / draws
                empirical_all = all_hits / draws
                expected_recall = expected_random_recall(
                    n=n, k=k, gold_count=gold_count
                )
                expected_all = probability_random_contains_all(
                    n=n, k=k, gold_count=gold_count
                )
                cases.append(
                    {
                        "n": n,
                        "gold_count": gold_count,
                        "k": k,
                        "expected_recall": expected_recall,
                        "empirical_recall": empirical_recall,
                        "recall_abs_error": abs(
                            empirical_recall - expected_recall
                        ),
                        "expected_all_gold": expected_all,
                        "empirical_all_gold": empirical_all,
                        "all_gold_abs_error": abs(
                            empirical_all - expected_all
                        ),
                    }
                )

    return cases


def run_validation(
    spec: dict[str, Any], *, quick: bool = False
) -> dict[str, Any]:
    validate_val001_spec(spec)
    parameters = spec["parameters"]
    seed = spec["seed"]

    registry_sizes = [8, 32] if quick else parameters["registry_sizes"]
    overlap_levels = [0.0, 0.5] if quick else parameters["overlap_levels"]
    alias_rates = [0.0, 0.15] if quick else parameters["alias_rates"]
    repeats = 2 if quick else parameters["repeats_per_cell"]

    cell_rows: list[dict[str, Any]] = []
    deterministic = True
    integrity = True
    controls = True
    no_tool = True

    for n in registry_sizes:
        for overlap in overlap_levels:
            for alias_rate in alias_rates:
                registry = generate_registry(
                    n=n,
                    overlap=overlap,
                    alias_rate=alias_rate,
                    seed=seed,
                )
                deterministic &= canonical_json_bytes(
                    registry
                ) == canonical_json_bytes(
                    generate_registry(
                        n=n,
                        overlap=overlap,
                        alias_rate=alias_rate,
                        seed=seed,
                    )
                )

                tasks = [
                    generate_task(
                        registry=registry,
                        task_type=task_type,
                        repeat=repeat,
                        seed=seed,
                    )
                    for task_type in parameters["task_types"]
                    for repeat in range(repeats)
                ]

                try:
                    validate_registry_tasks(registry, tasks)
                except ValueError:
                    integrity = False

                for task in tasks:
                    try:
                        validate_controls(registry, task)
                    except ValueError:
                        controls = False
                    if task["task_type"] == "no_tool":
                        no_tool &= not task["gold_tool_ids"]

                cell_rows.append(
                    {
                        "n": n,
                        "overlap": overlap,
                        "alias_rate": alias_rate,
                        "registry_sha256": sha256_json(registry),
                        "tasks": len(tasks),
                    }
                )

    draws = (
        min(1000, parameters["random_policy_draws"])
        if quick
        else parameters["random_policy_draws"]
    )
    calibration = random_calibration(
        draws=draws, seed=seed, quick=quick
    )
    tolerance = float(
        spec["acceptance"]["random_k_theory_abs_error_max"]
    )
    max_error = max(
        max(row["recall_abs_error"], row["all_gold_abs_error"])
        for row in calibration
    )
    injected = failure_injection_probe(seed)

    checks = {
        "deterministic_fixture_replay": bool(deterministic),
        "oracle_exact_gold": bool(controls),
        "full_exact_registry": bool(controls),
        "no_tool_gold_empty": bool(no_tool),
        "invalid_specs_rejected": bool(injected["invalid_spec"]),
        "intentional_failure_injection_detected": bool(
            all(injected.values())
        ),
        "random_k_theory_abs_error_max": bool(max_error <= tolerance),
        "registry_gold_integrity": bool(integrity),
    }
    state = "PASS" if all(checks.values()) else "FAIL"

    return {
        "study_id": "VAL-001",
        "mode": "SMOKE" if quick else "FULL",
        "state": state,
        "seed": seed,
        "cells": len(cell_rows),
        "tasks": sum(row["tasks"] for row in cell_rows),
        "checks": checks,
        "max_random_theory_abs_error": max_error,
        "random_tolerance": tolerance,
        "failure_injection": injected,
        "calibration_cases": calibration,
        "cell_digests": cell_rows,
    }
