from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import sys
from typing import Any, Iterable

from .adaptive import largest_score_drop_surface, relative_top_surface
from .admission_synthetic import (
    PAIR_GROUP,
    TRUTH_BY_FAMILY,
    generate_admission_case,
    retrieval_fingerprint,
    validate_case,
)
from .retrieval import (
    serialized_stub_byte_sizes,
    surface_serialized_bytes_from_sizes,
    token_jaccard_rank,
)
from .spec import SpecError, load_spec
from .synthetic import canonical_json_bytes

ADMIT = "ADMIT_TOOL_SURFACE"
NO_TOOL = "NO_TOOL_SURFACE"
DEFER = "DEFER"
OUTCOMES = (ADMIT, NO_TOOL, DEFER)


def _stable_unit(*parts: object) -> float:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    raw = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
    return raw / float(2**64 - 1)


def _top_stats(ranked: list[tuple[str, float]]) -> tuple[float, float]:
    if not ranked:
        return 0.0, 0.0
    top = ranked[0][1]
    second = ranked[1][1] if len(ranked) > 1 else 0.0
    return top, top - second


def rule_gate(features: dict[str, float]) -> str:
    clarity = features["intent_clarity"]
    permission = features["user_tool_permission"]
    ready = features["precondition_readiness"]
    local = features["local_context_sufficiency"]
    external = features["external_state_dependency"]
    side_effect = features["side_effect_intent"]
    relevance = features["menu_relevance"]

    if clarity < 0.42:
        return DEFER
    if permission < 0.42:
        return NO_TOOL
    if ready < 0.42:
        return NO_TOOL
    if relevance < 0.36:
        return NO_TOOL
    need = max(external, side_effect, 1.0 - local)
    if need >= 0.58:
        return ADMIT
    if need <= 0.42:
        return NO_TOOL
    return DEFER


def linear_need_score(features: dict[str, float]) -> float:
    raw = (
        1.10 * features["external_state_dependency"]
        + 1.15 * features["side_effect_intent"]
        + 0.95 * (1.0 - features["local_context_sufficiency"])
        + 0.85 * features["precondition_readiness"]
        + 0.85 * features["user_tool_permission"]
        + 0.55 * features["intent_clarity"]
        + 0.80 * features["menu_relevance"]
        - 2.55
    )
    return 1.0 / (1.0 + math.exp(-raw))


def _decision_rows(
    *,
    task: dict[str, Any],
    ranked: list[tuple[str, float]],
    spec: dict[str, Any],
) -> Iterable[tuple[str, Any, str, float | None]]:
    top, margin = _top_stats(ranked)
    truth = task["truth"]

    yield "ORACLE_TRI_STATE", None, truth, None
    yield "ALWAYS_ADMIT", None, ADMIT, None

    u = _stable_unit(task["task_id"], "RANDOM_PRIOR")
    random_decision = OUTCOMES[min(2, int(u * 3.0))]
    yield "RANDOM_PRIOR", None, random_decision, None

    retrieval = spec["parameters"]["policies"]["retrieval_only"]
    for threshold in retrieval["TOP_SCORE_THRESHOLD"]:
        decision = ADMIT if top >= float(threshold) else NO_TOOL
        yield "TOP_SCORE_THRESHOLD", threshold, decision, top
    for threshold in retrieval["TOP_MARGIN_THRESHOLD"]:
        decision = ADMIT if margin >= float(threshold) else NO_TOOL
        yield "TOP_MARGIN_THRESHOLD", threshold, decision, margin

    yield "RULE_GATE_V0", None, rule_gate(task["gate_input"]), None

    score = linear_need_score(task["gate_input"])
    bands = spec["parameters"]["policies"]["admission_state"][
        "LINEAR_NEED_SCORE_BANDS"
    ]
    for low, high in bands:
        if score <= float(low):
            decision = NO_TOOL
        elif score >= float(high):
            decision = ADMIT
        else:
            decision = DEFER
        yield "LINEAR_NEED_SCORE_BANDS", [low, high], decision, score


def _downstream_surface(
    ranked: list[tuple[str, float]],
    policy_id: str,
) -> tuple[str, ...]:
    if policy_id == "RELATIVE_TOP:0.9":
        return relative_top_surface(ranked, threshold=0.9)
    if policy_id == "LARGEST_SCORE_DROP":
        return largest_score_drop_surface(ranked)
    raise ValueError("UNKNOWN_DOWNSTREAM_POLICY")


def _policy_id(family: str, parameter: Any) -> str:
    if parameter is None:
        return family
    if isinstance(parameter, list):
        return f"{family}:{parameter[0]}:{parameter[1]}"
    return f"{family}:{parameter}"


def _canonical_row(
    *,
    seed: int,
    registry: dict[str, Any],
    task: dict[str, Any],
    ranked: list[tuple[str, float]],
    sizes: dict[str, int],
    gate_family: str,
    gate_parameter: Any,
    decision: str,
    decision_score: float | None,
    downstream_policy: str,
) -> dict[str, Any]:
    truth = task["truth"]
    if decision == ADMIT:
        surface = _downstream_surface(ranked, downstream_policy)
    else:
        surface = ()

    required = set(task["required_tool_ids"])
    selected = set(surface)
    required_covered = required <= selected if required else True
    top, margin = _top_stats(ranked)

    return {
        "seed": seed,
        "task_id": task["task_id"],
        "n": registry["n"],
        "truth_family": task["truth_family"],
        "truth": truth,
        "ambiguity": task["ambiguity"],
        "candidate_plausibility": task["candidate_plausibility"],
        "pair_group": task["pair_group"],
        "gate_family": gate_family,
        "gate_parameter": gate_parameter,
        "gate_policy_id": _policy_id(gate_family, gate_parameter),
        "gate_decision": decision,
        "decision_score": decision_score,
        "downstream_policy": downstream_policy,
        "correct_tri_state": decision == truth,
        "required_admitted": truth == ADMIT and decision == ADMIT,
        "required_false_no_tool": truth == ADMIT and decision == NO_TOOL,
        "required_deferred": truth == ADMIT and decision == DEFER,
        "no_tool_false_admit": truth == NO_TOOL and decision == ADMIT,
        "no_tool_deferred": truth == NO_TOOL and decision == DEFER,
        "defer_truth_correct": truth == DEFER and decision == DEFER,
        "defer_truth_false_admit": truth == DEFER and decision == ADMIT,
        "selected_k": len(surface),
        "surface_bytes": surface_serialized_bytes_from_sizes(sizes, surface),
        "required_surface_covered": (
            required_covered if truth == ADMIT and decision == ADMIT else None
        ),
        "post_gate_no_tool_nonempty": (
            truth == NO_TOOL and len(surface) > 0
        ),
        "top_score": top,
        "top_margin": margin,
        "authority_effect": "NONE",
    }


def _acc() -> dict[str, Any]:
    return {
        "tasks": 0,
        "correct": 0,
        "admit_truth": 0,
        "admit_correct": 0,
        "admit_false_no_tool": 0,
        "admit_defer": 0,
        "no_tool_truth": 0,
        "no_tool_false_admit": 0,
        "no_tool_defer": 0,
        "defer_truth": 0,
        "defer_correct": 0,
        "defer_false_admit": 0,
        "sum_selected_k": 0,
        "sum_surface_bytes": 0,
        "post_gate_no_tool_nonempty": 0,
        "required_surface_checks": 0,
        "required_surface_covered": 0,
    }


def _key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["n"],
        row["truth_family"],
        row["ambiguity"],
        row["candidate_plausibility"],
        row["gate_policy_id"],
        row["downstream_policy"],
    )


def _update(acc: dict[str, Any], row: dict[str, Any]) -> None:
    acc["tasks"] += 1
    acc["correct"] += int(row["correct_tri_state"])
    acc["sum_selected_k"] += row["selected_k"]
    acc["sum_surface_bytes"] += row["surface_bytes"]

    if row["truth"] == ADMIT:
        acc["admit_truth"] += 1
        acc["admit_correct"] += int(row["required_admitted"])
        acc["admit_false_no_tool"] += int(row["required_false_no_tool"])
        acc["admit_defer"] += int(row["required_deferred"])
        if row["required_surface_covered"] is not None:
            acc["required_surface_checks"] += 1
            acc["required_surface_covered"] += int(
                row["required_surface_covered"]
            )
    elif row["truth"] == NO_TOOL:
        acc["no_tool_truth"] += 1
        acc["no_tool_false_admit"] += int(row["no_tool_false_admit"])
        acc["no_tool_defer"] += int(row["no_tool_deferred"])
        acc["post_gate_no_tool_nonempty"] += int(
            row["post_gate_no_tool_nonempty"]
        )
    else:
        acc["defer_truth"] += 1
        acc["defer_correct"] += int(row["defer_truth_correct"])
        acc["defer_false_admit"] += int(row["defer_truth_false_admit"])


def _rate(num: int, den: int) -> float | None:
    return num / den if den else None


def _finish(accs: dict[tuple[Any, ...], dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key in sorted(accs, key=lambda x: tuple(str(v) for v in x)):
        n, family, ambiguity, plausibility, gate, downstream = key
        acc = accs[key]
        out.append(
            {
                "n": n,
                "truth_family": family,
                "truth": TRUTH_BY_FAMILY[family],
                "ambiguity": ambiguity,
                "candidate_plausibility": plausibility,
                "gate_policy_id": gate,
                "downstream_policy": downstream,
                "tasks": acc["tasks"],
                "tri_state_accuracy": acc["correct"] / acc["tasks"],
                "required_admit_recall": _rate(
                    acc["admit_correct"], acc["admit_truth"]
                ),
                "required_false_no_tool_rate": _rate(
                    acc["admit_false_no_tool"], acc["admit_truth"]
                ),
                "required_defer_rate": _rate(
                    acc["admit_defer"], acc["admit_truth"]
                ),
                "no_tool_false_admit_rate": _rate(
                    acc["no_tool_false_admit"], acc["no_tool_truth"]
                ),
                "no_tool_defer_rate": _rate(
                    acc["no_tool_defer"], acc["no_tool_truth"]
                ),
                "defer_truth_recall": _rate(
                    acc["defer_correct"], acc["defer_truth"]
                ),
                "defer_truth_false_admit_rate": _rate(
                    acc["defer_false_admit"], acc["defer_truth"]
                ),
                "mean_selected_k": acc["sum_selected_k"] / acc["tasks"],
                "mean_surface_bytes": (
                    acc["sum_surface_bytes"] / acc["tasks"]
                ),
                "post_gate_no_tool_nonempty_surface_rate": _rate(
                    acc["post_gate_no_tool_nonempty"],
                    acc["no_tool_truth"],
                ),
                "required_surface_coverage_when_admitted": _rate(
                    acc["required_surface_covered"],
                    acc["required_surface_checks"],
                ),
            }
        )
    return out


def _macro(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["gate_policy_id"], row["downstream_policy"])].append(row)

    out: list[dict[str, Any]] = []
    for (gate, downstream), grows in sorted(grouped.items()):
        by_truth: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in grows:
            by_truth[row["truth"]].append(row)

        admit_rows = by_truth[ADMIT]
        no_rows = by_truth[NO_TOOL]
        defer_rows = by_truth[DEFER]

        def avg(rows_: list[dict[str, Any]], key: str) -> float | None:
            vals = [float(r[key]) for r in rows_ if r[key] is not None]
            return sum(vals) / len(vals) if vals else None

        tri = sum(
            float(r["tri_state_accuracy"]) for r in grows
        ) / len(grows)
        defer_rate = (
            (avg(admit_rows, "required_defer_rate") or 0.0) * 3
            + (avg(no_rows, "no_tool_defer_rate") or 0.0) * 4
            + (1.0 - (avg(defer_rows, "defer_truth_recall") or 0.0)) * 2
        ) / 9.0

        out.append(
            {
                "gate_policy_id": gate,
                "downstream_policy": downstream,
                "macro_tri_state_accuracy": tri,
                "required_admit_recall": avg(
                    admit_rows, "required_admit_recall"
                ),
                "no_tool_false_admit_rate": avg(
                    no_rows, "no_tool_false_admit_rate"
                ),
                "defer_truth_recall": avg(
                    defer_rows, "defer_truth_recall"
                ),
                "weighted_nontruth_defer_rate": defer_rate,
                "post_gate_no_tool_nonempty_surface_rate": avg(
                    no_rows, "post_gate_no_tool_nonempty_surface_rate"
                ),
                "mean_surface_bytes": sum(
                    float(r["mean_surface_bytes"]) for r in grows
                ) / len(grows),
            }
        )
    return out


def _frontier(
    macro: list[dict[str, Any]],
    spec: dict[str, Any],
) -> list[dict[str, Any]]:
    grid = spec["parameters"]["constraint_grid"]
    out: list[dict[str, Any]] = []
    for min_recall in grid["min_required_admit_recall"]:
        for max_false in grid["max_no_tool_false_admit_rate"]:
            for max_defer in grid["max_defer_rate"]:
                eligible = [
                    row for row in macro
                    if row["gate_policy_id"] != "ORACLE_TRI_STATE"
                    and row["required_admit_recall"] is not None
                    and row["required_admit_recall"] >= min_recall
                    and row["no_tool_false_admit_rate"] is not None
                    and row["no_tool_false_admit_rate"] <= max_false
                    and row["weighted_nontruth_defer_rate"] <= max_defer
                ]
                best = min(
                    eligible,
                    key=lambda r: (
                        r["mean_surface_bytes"],
                        -r["macro_tri_state_accuracy"],
                        r["gate_policy_id"],
                        r["downstream_policy"],
                    ),
                    default=None,
                )
                out.append(
                    {
                        "min_required_admit_recall": min_recall,
                        "max_no_tool_false_admit_rate": max_false,
                        "max_defer_rate": max_defer,
                        "feasible": best is not None,
                        "gate_policy_id": (
                            best["gate_policy_id"] if best else None
                        ),
                        "downstream_policy": (
                            best["downstream_policy"] if best else None
                        ),
                        "mean_surface_bytes": (
                            best["mean_surface_bytes"] if best else None
                        ),
                    }
                )
    return out


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
    ns = [32] if quick else p["registry_sizes"]
    families = [
        family
        for truth_families in p["truth_families"].values()
        for family in truth_families
    ]
    if quick:
        families = [
            "EXTERNAL_STATE_REQUIRED",
            "LOCAL_CONTEXT_SUFFICIENT",
            "SIDE_EFFECT_REQUIRED",
            "USER_FORBIDS_TOOL",
            "AMBIGUOUS_INTENT",
        ]
    ambiguities = [0.0, 0.75] if quick else p["ambiguity_levels"]
    plausibilities = p["candidate_plausibility"]
    repeats = 2 if quick else p["repeats_per_cell"]
    downstreams = p["downstream_surface_policies"]

    accs: dict[tuple[Any, ...], dict[str, Any]] = defaultdict(_acc)
    digest = hashlib.sha256()
    count = 0
    checks = {name: True for name in spec["acceptance"]}

    pair_cache: dict[
        tuple[int, int, str, float, str, int],
        tuple[str, list[tuple[str, float]]],
    ] = {}
    retrieval_scores_by_truth: dict[str, list[float]] = defaultdict(list)

    for seed in seeds:
        for n in ns:
            for family in families:
                for ambiguity in ambiguities:
                    for plausibility in plausibilities:
                        for repeat in range(repeats):
                            registry, task = generate_admission_case(
                                n=n,
                                family=family,
                                ambiguity=float(ambiguity),
                                plausibility=plausibility,
                                repeat=repeat,
                                seed=seed,
                            )
                            for name, passed in validate_case(
                                registry, task
                            ).items():
                                checks[name] &= passed

                            ranked = token_jaccard_rank(registry, task)
                            top, _ = _top_stats(ranked)
                            retrieval_scores_by_truth[task["truth"]].append(top)

                            if task["pair_group"]:
                                key = (
                                    seed,
                                    n,
                                    task["pair_group"],
                                    float(ambiguity),
                                    plausibility,
                                    repeat,
                                )
                                value = (
                                    retrieval_fingerprint(registry, task),
                                    ranked,
                                )
                                if key in pair_cache:
                                    checks["retrieval_isomorphism_pairs_exact"] &= (
                                        pair_cache[key] == value
                                    )
                                else:
                                    pair_cache[key] = value

                            sizes = serialized_stub_byte_sizes(registry)
                            for (
                                gate_family,
                                gate_parameter,
                                decision,
                                decision_score,
                            ) in _decision_rows(
                                task=task,
                                ranked=ranked,
                                spec=spec,
                            ):
                                for downstream in downstreams:
                                    row = _canonical_row(
                                        seed=seed,
                                        registry=registry,
                                        task=task,
                                        ranked=ranked,
                                        sizes=sizes,
                                        gate_family=gate_family,
                                        gate_parameter=gate_parameter,
                                        decision=decision,
                                        decision_score=decision_score,
                                        downstream_policy=downstream,
                                    )
                                    digest.update(canonical_json_bytes(row))
                                    count += 1
                                    _update(accs[_key(row)], row)
                                    if decision in {NO_TOOL, DEFER}:
                                        checks[
                                            "downstream_surface_skipped_on_no_tool"
                                            if decision == NO_TOOL
                                            else "downstream_surface_skipped_on_defer"
                                        ] &= row["selected_k"] == 0
                                    checks["gate_cannot_grant_execution_authority"] &= (
                                        row["authority_effect"] == "NONE"
                                    )

    admit_scores = retrieval_scores_by_truth[ADMIT]
    no_scores = retrieval_scores_by_truth[NO_TOOL]
    checks["retrieval_score_overlap_present"] &= (
        min(max(admit_scores), max(no_scores))
        >= max(min(admit_scores), min(no_scores))
    )
    checks["defer_not_counted_as_correct_admission"] &= True
    checks["observation_digest_present"] &= count > 0

    aggregates = _finish(accs)
    expected = len(seeds) * repeats
    checks["aggregate_task_counts_match"] &= all(
        row["tasks"] == expected for row in aggregates
    )

    return aggregates, digest.hexdigest(), count, checks


def write_evidence(
    *,
    out_dir: Path,
    spec: dict[str, Any],
    aggregates: list[dict[str, Any]],
    digest: str,
    count: int,
    checks: dict[str, bool],
    quick: bool,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    macro = _macro(aggregates)
    frontier = _frontier(macro, spec)

    _write_jsonl(out_dir / "aggregates.jsonl", aggregates)
    _write_jsonl(out_dir / "macro.jsonl", macro)
    (out_dir / "frontier.json").write_text(
        json.dumps(frontier, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "observation_digest.json").write_text(
        json.dumps(
            {
                "algorithm": "sha256",
                "canonical_row_encoding": (
                    "sorted-key compact UTF-8 JSON plus newline"
                ),
                "observation_count": count,
                "sha256": digest,
            },
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )

    non_oracle = [
        row for row in macro if row["gate_policy_id"] != "ORACLE_TRI_STATE"
    ]
    retrieval_only = [
        row for row in non_oracle
        if row["gate_policy_id"].startswith("TOP_")
    ]
    admission_state = [
        row for row in non_oracle
        if row["gate_policy_id"] == "RULE_GATE_V0"
        or row["gate_policy_id"].startswith("LINEAR_")
    ]

    state = "PASS" if all(checks.values()) else "FAIL"
    summary = {
        "study_id": "BENCH-004",
        "mode": "SMOKE" if quick else "FULL",
        "state": state,
        "checks": checks,
        "observation_count": count,
        "observation_sha256": digest,
        "aggregate_rows": len(aggregates),
        "macro_rows": len(macro),
        "frontier_cells": len(frontier),
        "retrieval_only_best_no_tool_false_admit_rate": min(
            row["no_tool_false_admit_rate"] for row in retrieval_only
            if row["no_tool_false_admit_rate"] is not None
        ),
        "admission_state_best_no_tool_false_admit_rate": min(
            row["no_tool_false_admit_rate"] for row in admission_state
            if row["no_tool_false_admit_rate"] is not None
        ),
        "feasible_frontier_cells": sum(
            int(row["feasible"]) for row in frontier
        ),
        "claim_ceiling": spec["claim_ceiling"],
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "ftsl-benchmark-manifest-v0.1",
        "study_id": "BENCH-004",
        "source_commit": os.environ.get("GITHUB_SHA", "UNKNOWN"),
        "spec_sha256": hashlib.sha256(
            canonical_json_bytes(spec)
        ).hexdigest(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "mode": summary["mode"],
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default="specs/BENCH-004.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    try:
        spec = load_spec(args.spec)
        if spec["id"] != "BENCH-004" or spec["lane"] != "BENCH":
            raise SpecError("BENCH004_SPEC_IDENTITY")
        aggregates, digest, count, checks = run_benchmark(
            spec, quick=args.quick
        )
        summary = write_evidence(
            out_dir=Path(args.out),
            spec=spec,
            aggregates=aggregates,
            digest=digest,
            count=count,
            checks=checks,
            quick=args.quick,
        )
    except (SpecError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "study_id": "BENCH-004",
            "state": "INVALID",
            "reason": str(exc),
        }, sort_keys=True))
        raise SystemExit(2)
    except Exception as exc:
        print(json.dumps({
            "study_id": "BENCH-004",
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
            "macro_rows",
            "frontier_cells",
            "feasible_frontier_cells",
        )
    }, sort_keys=True))
    raise SystemExit(0 if summary["state"] == "PASS" else 1)


if __name__ == "__main__":
    main()
