from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
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
from .distractor_synthetic import (
    generate_distractor_case,
    validate_distractor_case,
)
from .retrieval import (
    serialized_stub_byte_sizes,
    surface_serialized_bytes_from_sizes,
    token_jaccard_rank,
    token_jaccard_surface,
)
from .spec import SpecError, load_spec
from .synthetic import canonical_json_bytes


def _policy_id(family: str, parameter: float | int | None) -> str:
    return family if parameter is None else f"{family}:{parameter}"


def _surfaces(
    *,
    registry: dict[str, Any],
    task: dict[str, Any],
    ranked: list[tuple[str, float]],
    spec: dict[str, Any],
) -> Iterable[tuple[str, float | int | None, tuple[str, ...]]]:
    ids = tuple(tool["tool_id"] for tool in registry["tools"])
    oracle = tuple(
        task["canonical_tool_ids_by_capability"][cap]
        for cap in task["required_capabilities"]
    )
    yield "ORACLE", None, oracle
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


def evaluate_surface(
    registry: dict[str, Any],
    task: dict[str, Any],
    surface: tuple[str, ...],
) -> dict[str, int | float | bool]:
    selected = set(surface)
    lookup = {tool["tool_id"]: tool for tool in registry["tools"]}
    required = task["required_capabilities"]
    valid_map = task["valid_tool_ids_by_capability"]
    canonical_map = task["canonical_tool_ids_by_capability"]

    covered = 0
    canonical_hits = 0
    fragmented = 0
    equivalent_eligible = 0
    valid_alt_selected = 0
    valid_alt_available = len(task["valid_equivalent_ids"])

    for cap in required:
        valid = set(valid_map[cap])
        hits = valid & selected
        covered += int(bool(hits))
        canonical_hits += int(canonical_map[cap] in selected)
        if len(valid) > 1:
            equivalent_eligible += 1
            fragmented += int(len(hits) > 1)
        canonical = canonical_map[cap]
        valid_alt_selected += len(hits - {canonical})

    wrong_available = set(task["targeted_wrong_ids"])
    wrong_selected = len(selected & wrong_available)
    premature_selected = len(selected & set(task["premature_wrong_ids"]))
    risky_selected = len(selected & set(task["risky_wrong_ids"]))

    required_count = len(required)
    return {
        "required_capability_count": required_count,
        "covered_capability_count": covered,
        "any_valid": bool(covered > 0) if required_count else False,
        "all_required": bool(covered == required_count) if required_count else True,
        "canonical_all": (
            bool(canonical_hits == required_count) if required_count else True
        ),
        "valid_alt_selected": valid_alt_selected,
        "valid_alt_available": valid_alt_available,
        "equivalence_fragmented_capabilities": fragmented,
        "equivalence_eligible_capabilities": equivalent_eligible,
        "wrong_distractor_selected": wrong_selected,
        "wrong_distractor_available": len(wrong_available),
        "premature_wrong_selected": premature_selected,
        "premature_wrong_available": len(task["premature_wrong_ids"]),
        "risky_wrong_selected": risky_selected,
        "risky_wrong_available": len(task["risky_wrong_ids"]),
        "distractor_burden": (
            wrong_selected / len(surface) if surface else 0.0
        ),
    }


def _canonical_row(
    *,
    seed: int,
    registry: dict[str, Any],
    task: dict[str, Any],
    family: str,
    parameter: float | int | None,
    surface: tuple[str, ...],
    ranked: list[tuple[str, float]],
    serialized_sizes: dict[str, int],
) -> dict[str, Any]:
    metrics = evaluate_surface(registry, task, surface)
    return {
        "seed": seed,
        "task_id": task["task_id"],
        "n": registry["n"],
        "task_type": task["task_type"],
        "stress_family": task["stress_family"],
        "density": task["density"],
        "policy_family": family,
        "policy_parameter": parameter,
        "policy_id": _policy_id(family, parameter),
        "selected_k": len(surface),
        "surface_bytes": surface_serialized_bytes_from_sizes(
            serialized_sizes, surface
        ),
        "top_score": ranked[0][1] if ranked else 0.0,
        "tie_blocks_preserved": (
            tie_blocks_preserved(ranked, surface)
            if family not in {"ORACLE", "FULL", "FIXED_K"}
            else True
        ),
        **metrics,
    }


def _accumulator() -> dict[str, Any]:
    return {
        "tasks": 0,
        "sum_selected_k": 0,
        "sum_surface_bytes": 0,
        "sum_required_caps": 0,
        "sum_covered_caps": 0,
        "any_valid_tasks": 0,
        "all_required_tasks": 0,
        "canonical_all_tasks": 0,
        "sum_valid_alt_selected": 0,
        "sum_valid_alt_available": 0,
        "sum_fragmented_caps": 0,
        "sum_equiv_eligible_caps": 0,
        "sum_wrong_selected": 0,
        "sum_wrong_available": 0,
        "sum_premature_selected": 0,
        "sum_premature_available": 0,
        "sum_risky_selected": 0,
        "sum_risky_available": 0,
        "sum_distractor_burden": 0.0,
        "no_tool_nonempty": 0,
    }


def _key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["n"],
        row["task_type"],
        row["stress_family"],
        row["density"],
        row["policy_family"],
        row["policy_parameter"],
    )


def _update(acc: dict[str, Any], row: dict[str, Any]) -> None:
    acc["tasks"] += 1
    acc["sum_selected_k"] += row["selected_k"]
    acc["sum_surface_bytes"] += row["surface_bytes"]
    acc["sum_required_caps"] += row["required_capability_count"]
    acc["sum_covered_caps"] += row["covered_capability_count"]
    acc["sum_valid_alt_selected"] += row["valid_alt_selected"]
    acc["sum_valid_alt_available"] += row["valid_alt_available"]
    acc["sum_fragmented_caps"] += row["equivalence_fragmented_capabilities"]
    acc["sum_equiv_eligible_caps"] += row["equivalence_eligible_capabilities"]
    acc["sum_wrong_selected"] += row["wrong_distractor_selected"]
    acc["sum_wrong_available"] += row["wrong_distractor_available"]
    acc["sum_premature_selected"] += row["premature_wrong_selected"]
    acc["sum_premature_available"] += row["premature_wrong_available"]
    acc["sum_risky_selected"] += row["risky_wrong_selected"]
    acc["sum_risky_available"] += row["risky_wrong_available"]
    acc["sum_distractor_burden"] += row["distractor_burden"]

    if row["required_capability_count"]:
        acc["any_valid_tasks"] += int(row["any_valid"])
        acc["all_required_tasks"] += int(row["all_required"])
        acc["canonical_all_tasks"] += int(row["canonical_all"])
    else:
        acc["no_tool_nonempty"] += int(row["selected_k"] > 0)


def _rate(num: float, den: float) -> float | None:
    return num / den if den else None


def _finish(
    accumulators: dict[tuple[Any, ...], dict[str, Any]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in sorted(
        accumulators,
        key=lambda x: (
            x[0], x[1], x[2], x[3], x[4],
            "" if x[5] is None else str(x[5]),
        ),
    ):
        n, task_type, stress, density, family, parameter = key
        acc = accumulators[key]
        tasks = acc["tasks"]
        required_tasks = tasks if acc["sum_required_caps"] else 0
        rows.append(
            {
                "n": n,
                "task_type": task_type,
                "stress_family": stress,
                "density": density,
                "policy_family": family,
                "policy_parameter": parameter,
                "policy_id": _policy_id(family, parameter),
                "tasks": tasks,
                "mean_selected_k": acc["sum_selected_k"] / tasks,
                "mean_surface_bytes": acc["sum_surface_bytes"] / tasks,
                "capability_recall": _rate(
                    acc["sum_covered_caps"], acc["sum_required_caps"]
                ),
                "any_valid_rate": _rate(
                    acc["any_valid_tasks"], required_tasks
                ),
                "all_required_rate": _rate(
                    acc["all_required_tasks"], required_tasks
                ),
                "canonical_all_rate": _rate(
                    acc["canonical_all_tasks"], required_tasks
                ),
                "valid_alternative_recovery_rate": _rate(
                    acc["sum_valid_alt_selected"],
                    acc["sum_valid_alt_available"],
                ),
                "equivalence_fragmentation_rate": _rate(
                    acc["sum_fragmented_caps"],
                    acc["sum_equiv_eligible_caps"],
                ),
                "wrong_distractor_inclusion_rate": _rate(
                    acc["sum_wrong_selected"],
                    acc["sum_wrong_available"],
                ),
                "mean_distractor_burden": (
                    acc["sum_distractor_burden"] / tasks
                ),
                "premature_wrong_exposure_rate": _rate(
                    acc["sum_premature_selected"],
                    acc["sum_premature_available"],
                ),
                "risky_wrong_exposure_rate": _rate(
                    acc["sum_risky_selected"],
                    acc["sum_risky_available"],
                ),
                "no_tool_nonempty_surface_rate": (
                    acc["no_tool_nonempty"] / tasks
                    if not acc["sum_required_caps"]
                    else None
                ),
            }
        )
    return rows


def _frontier(aggregates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in aggregates:
        if row["task_type"] == "no_tool" or row["policy_family"] == "ORACLE":
            continue
        grouped[
            (
                row["n"],
                row["task_type"],
                row["stress_family"],
                row["density"],
            )
        ].append(row)

    result: list[dict[str, Any]] = []
    for condition, points in grouped.items():
        for point in points:
            point_wrong = point["mean_distractor_burden"] or 0.0
            dominated = False
            for other in points:
                if other is point:
                    continue
                other_wrong = other["mean_distractor_burden"] or 0.0
                no_worse = (
                    other["all_required_rate"] >= point["all_required_rate"]
                    and other["mean_selected_k"] <= point["mean_selected_k"]
                    and other["mean_surface_bytes"] <= point["mean_surface_bytes"]
                    and other_wrong <= point_wrong
                )
                strictly = (
                    other["all_required_rate"] > point["all_required_rate"]
                    or other["mean_selected_k"] < point["mean_selected_k"]
                    or other["mean_surface_bytes"] < point["mean_surface_bytes"]
                    or other_wrong < point_wrong
                )
                if no_worse and strictly:
                    dominated = True
                    break
            if not dominated:
                result.append(
                    {
                        "n": condition[0],
                        "task_type": condition[1],
                        "stress_family": condition[2],
                        "density": condition[3],
                        "policy_id": point["policy_id"],
                        "all_required_rate": point["all_required_rate"],
                        "mean_selected_k": point["mean_selected_k"],
                        "mean_surface_bytes": point["mean_surface_bytes"],
                        "mean_distractor_burden": point_wrong,
                    }
                )
    result.sort(
        key=lambda row: (
            row["n"],
            row["task_type"],
            row["stress_family"],
            row["density"],
            row["mean_selected_k"],
            row["policy_id"],
        )
    )
    return result


def _msts(
    aggregates: list[dict[str, Any]],
    epsilons: list[float],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in aggregates:
        if row["task_type"] == "no_tool" or row["policy_family"] == "ORACLE":
            continue
        grouped[
            (
                row["n"],
                row["task_type"],
                row["stress_family"],
                row["density"],
            )
        ].append(row)

    result: list[dict[str, Any]] = []
    for condition, points in grouped.items():
        for epsilon in epsilons:
            eligible = [
                row for row in points
                if row["all_required_rate"] >= 1.0 - epsilon
            ]
            best = (
                min(
                    eligible,
                    key=lambda row: (
                        row["mean_surface_bytes"],
                        row["mean_distractor_burden"],
                        row["mean_selected_k"],
                        row["policy_id"],
                    ),
                )
                if eligible
                else None
            )
            result.append(
                {
                    "n": condition[0],
                    "task_type": condition[1],
                    "stress_family": condition[2],
                    "density": condition[3],
                    "epsilon": epsilon,
                    "policy_id": best["policy_id"] if best else None,
                    "mean_selected_k": (
                        best["mean_selected_k"] if best else None
                    ),
                    "mean_surface_bytes": (
                        best["mean_surface_bytes"] if best else None
                    ),
                    "mean_distractor_burden": (
                        best["mean_distractor_burden"] if best else None
                    ),
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
    p = spec["parameters"]
    seeds = [p["evaluation_seeds"][0]] if quick else p["evaluation_seeds"]
    registry_sizes = [32] if quick else p["registry_sizes"]
    task_types = p["task_types"]
    stresses = (
        ["RANDOM_IRRELEVANT", "RISKY_RELEVANT", "VALID_EQUIVALENT", "MIXED"]
        if quick else p["stress_families"]
    )
    densities = [0, 3] if quick else p["targeted_distractors_per_required_capability"]
    repeats = 2 if quick else p["repeats_per_cell"]

    run_spec = json.loads(json.dumps(spec))
    if quick:
        run_spec["parameters"]["fixed_k_values"] = [0, 1, 2, 8, 32]
        run_spec["parameters"]["relative_top_thresholds"] = [0.5, 0.9]
        run_spec["parameters"]["cumulative_mass_thresholds"] = [0.7, 0.9]

    accumulators: dict[tuple[Any, ...], dict[str, Any]] = defaultdict(
        _accumulator
    )
    digest = hashlib.sha256()
    observation_count = 0

    checks = {
        key: True for key in spec["acceptance"]
    }
    seen_policy_families: set[str] = set()

    for seed in seeds:
        for n in registry_sizes:
            for task_type in task_types:
                for stress in stresses:
                    for density in densities:
                        for repeat in range(repeats):
                            registry, task = generate_distractor_case(
                                n=n,
                                task_type=task_type,
                                stress_family=stress,
                                density=density,
                                repeat=repeat,
                                seed=seed,
                            )
                            case_checks = validate_distractor_case(
                                registry, task
                            )
                            for name, passed in case_checks.items():
                                checks[name] &= passed

                            ranked = token_jaccard_rank(registry, task)
                            sizes = serialized_stub_byte_sizes(registry)
                            for family, parameter, surface in _surfaces(
                                registry=registry,
                                task=task,
                                ranked=ranked,
                                spec=run_spec,
                            ):
                                row = _canonical_row(
                                    seed=seed,
                                    registry=registry,
                                    task=task,
                                    family=family,
                                    parameter=parameter,
                                    surface=surface,
                                    ranked=ranked,
                                    serialized_sizes=sizes,
                                )
                                digest.update(canonical_json_bytes(row))
                                observation_count += 1
                                seen_policy_families.add(family)
                                if family not in {
                                    "ORACLE", "FULL", "FIXED_K"
                                }:
                                    checks["tie_blocks_not_split"] &= bool(
                                        row["tie_blocks_preserved"]
                                    )
                                    if row["top_score"] == 0.0:
                                        checks[
                                            "adaptive_zero_evidence_abstains"
                                        ] &= row["selected_k"] == 0
                                _update(accumulators[_key(row)], row)

    aggregates = _finish(accumulators)
    expected_tasks = len(seeds) * repeats
    checks["aggregate_task_counts_match"] &= all(
        row["tasks"] == expected_tasks for row in aggregates
    )
    checks["observation_digest_present"] &= observation_count > 0

    required_policy_families = {
        "ORACLE",
        "FULL",
        "FIXED_K",
        "POSITIVE_SUPPORT",
        "RELATIVE_TOP",
        "CUMULATIVE_SCORE_MASS",
        "LARGEST_SCORE_DROP",
    }
    if seen_policy_families != required_policy_families:
        checks["aggregate_task_counts_match"] = False

    return aggregates, digest.hexdigest(), observation_count, checks


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
        [float(value) for value in spec["parameters"]["msts_epsilons"]],
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

    tool_rows = [
        row for row in aggregates
        if row["task_type"] != "no_tool"
        and row["policy_family"] != "ORACLE"
    ]
    no_tool_rows = [
        row for row in aggregates
        if row["task_type"] == "no_tool"
        and row["policy_family"]
        not in {"ORACLE", "FULL", "FIXED_K"}
    ]
    wrong_rates = [
        row["wrong_distractor_inclusion_rate"]
        for row in aggregates
        if row["wrong_distractor_inclusion_rate"] is not None
    ]
    state = "PASS" if all(checks.values()) else "FAIL"
    summary = {
        "study_id": "BENCH-003",
        "mode": "SMOKE" if quick else "FULL",
        "state": state,
        "checks": checks,
        "observation_count": observation_count,
        "observation_sha256": observation_digest,
        "aggregate_rows": len(aggregates),
        "frontier_points": len(frontier),
        "all_required_rate_range": [
            min(row["all_required_rate"] for row in tool_rows),
            max(row["all_required_rate"] for row in tool_rows),
        ],
        "wrong_distractor_inclusion_rate_range": [
            min(wrong_rates) if wrong_rates else None,
            max(wrong_rates) if wrong_rates else None,
        ],
        "adaptive_no_tool_nonempty_rate_range": [
            min(row["no_tool_nonempty_surface_rate"] for row in no_tool_rows),
            max(row["no_tool_nonempty_surface_rate"] for row in no_tool_rows),
        ],
        "claim_ceiling": spec["claim_ceiling"],
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "ftsl-benchmark-manifest-v0.1",
        "study_id": "BENCH-003",
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
    parser.add_argument("--spec", default="specs/BENCH-003.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    try:
        spec = load_spec(args.spec)
        if spec["id"] != "BENCH-003" or spec["lane"] != "BENCH":
            raise SpecError("BENCH003_SPEC_IDENTITY")
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
            "study_id": "BENCH-003",
            "state": "INVALID",
            "reason": str(exc),
        }, sort_keys=True))
        raise SystemExit(2)
    except Exception as exc:
        print(json.dumps({
            "study_id": "BENCH-003",
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
        )
    }, sort_keys=True))
    raise SystemExit(0 if summary["state"] == "PASS" else 1)


if __name__ == "__main__":
    main()
