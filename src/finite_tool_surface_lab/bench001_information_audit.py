from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean

from .bench001 import run_benchmark
from .bench_metrics import aggregate_rows
from .spec import load_spec


def _unique_visibility_probability(overlap: float) -> float:
    shared_count = int(round(overlap * 8))
    unique_count = 8 - shared_count
    total_tokens = 10
    query_tokens = 5
    nonunique = total_tokens - unique_count
    if nonunique < query_tokens:
        return 1.0
    return 1.0 - math.comb(nonunique, query_tokens) / math.comb(
        total_tokens, query_tokens
    )


def _stats(values: list[float]) -> dict[str, float]:
    return {
        "mean": mean(values),
        "min": min(values),
        "max": max(values),
    }


def run_audit(spec_path: str | Path) -> dict:
    spec = load_spec(spec_path)
    if spec["id"] != "BENCH-001":
        raise ValueError("BENCH001_SPEC_REQUIRED")

    rows, _ = run_benchmark(spec, quick=False)
    aggregates = aggregate_rows(rows)

    construction = []
    observed = []
    for overlap in spec["parameters"]["overlap_levels"]:
        overlap = float(overlap)
        shared_count = int(round(overlap * 8))
        unique_count = 8 - shared_count
        multi_prefix_unique_per_tool = max(0, 4 - shared_count)

        single = [
            row["all_gold_rate"]
            for row in aggregates
            if row["policy"] == "TOKEN_JACCARD"
            and row["task_type"] == "single_tool"
            and row["k"] == 1
            and float(row["overlap"]) == overlap
        ]
        multi = [
            row["all_gold_rate"]
            for row in aggregates
            if row["policy"] == "TOKEN_JACCARD"
            and row["task_type"] == "multi_tool"
            and row["k"] == 2
            and float(row["overlap"]) == overlap
        ]

        construction.append(
            {
                "overlap": overlap,
                "shared_description_tokens": shared_count,
                "unique_description_tokens": unique_count,
                "single_query_unique_visibility_probability": (
                    _unique_visibility_probability(overlap)
                ),
                "multi_query_prefix_tokens_per_gold": 4,
                "multi_query_unique_tokens_per_gold_in_prefix": (
                    multi_prefix_unique_per_tool
                ),
            }
        )
        observed.append(
            {
                "overlap": overlap,
                "single_tool_token_jaccard_k1_all_gold": _stats(single),
                "multi_tool_token_jaccard_k2_all_gold": _stats(multi),
            }
        )

    checks = {
        "low_overlap_single_k1_perfect": all(
            item["single_tool_token_jaccard_k1_all_gold"]["min"] == 1.0
            for item in observed
            if item["overlap"] <= 0.25
        ),
        "low_overlap_multi_k2_perfect": all(
            item["multi_tool_token_jaccard_k2_all_gold"]["min"] == 1.0
            for item in observed
            if item["overlap"] <= 0.25
        ),
        "high_overlap_multi_prefix_erases_tool_unique_tokens": all(
            item["multi_query_unique_tokens_per_gold_in_prefix"] == 0
            for item in construction
            if item["overlap"] >= 0.50
        ),
        "single_query_unique_visibility_decreases_with_overlap": all(
            a["single_query_unique_visibility_probability"]
            >= b["single_query_unique_visibility_probability"]
            for a, b in zip(construction, construction[1:])
        ),
    }

    return {
        "study_id": "BENCH-001-INFORMATION-AUDIT",
        "state": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "construction": construction,
        "observed": observed,
        "alias_semantics": (
            "In synthetic generator v0.1, aliases are attached to candidate "
            "tool metadata but query_tokens are drawn from description_tokens; "
            "alias_rate therefore does not test alias-query resolution."
        ),
        "interpretation": (
            "The sharp multi-tool degradation beginning at overlap>=0.50 is "
            "partly construction-induced: the first four description tokens "
            "used per selected tool are all shared at those overlap levels, "
            "so exact tool identity is absent from the query prefix. Treat the "
            "regime as a controlled information-ambiguity stress test, not a "
            "universal semantic-overlap threshold."
        ),
        "claim_ceiling": (
            "Generator/benchmark interpretation audit only; no Worker "
            "performance or universal overlap threshold claim."
        ),
    }


def _markdown(result: dict) -> str:
    lines = [
        "# BENCH-001 Information Audit",
        "",
        f"State: **{result['state']}**",
        "",
        "## Construction",
        "",
        "| overlap | shared | unique | P(single query sees >=1 unique) | multi prefix unique/gold |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["construction"]:
        lines.append(
            f"| {row['overlap']:.2f} | "
            f"{row['shared_description_tokens']} | "
            f"{row['unique_description_tokens']} | "
            f"{row['single_query_unique_visibility_probability']:.6f} | "
            f"{row['multi_query_unique_tokens_per_gold_in_prefix']} |"
        )

    lines += [
        "",
        "## Observed lexical exact-gold rates",
        "",
        "| overlap | single k=1 mean | single min | multi k=2 mean | multi min |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["observed"]:
        s = row["single_tool_token_jaccard_k1_all_gold"]
        m = row["multi_tool_token_jaccard_k2_all_gold"]
        lines.append(
            f"| {row['overlap']:.2f} | {s['mean']:.6f} | "
            f"{s['min']:.6f} | {m['mean']:.6f} | {m['min']:.6f} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        result["interpretation"],
        "",
        "## Alias semantics",
        "",
        result["alias_semantics"],
        "",
        "## Claim ceiling",
        "",
        result["claim_ceiling"],
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default="specs/BENCH-001.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown", required=True)
    args = parser.parse_args()

    result = run_audit(args.spec)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(args.markdown).write_text(_markdown(result), encoding="utf-8")
    print(json.dumps({
        "study_id": result["study_id"],
        "state": result["state"],
        "checks": result["checks"],
    }, sort_keys=True))
    raise SystemExit(0 if result["state"] == "PASS" else 1)


if __name__ == "__main__":
    main()
