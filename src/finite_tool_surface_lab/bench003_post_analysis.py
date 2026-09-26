from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any

import numpy as np

SOURCE_RUN_ID = 36242144911
SOURCE_ARTIFACT_ID = 10906331126
SOURCE_ARTIFACT_DIGEST = (
    "sha256:96015668c446af1d7ed561aa8bed76ada532a9c38e0cfdd6ba584e171e02685f"
)
SOURCE_OBSERVATION_DIGEST = (
    "019d4ec58cce84fd2e3c0b92e47fa0ec04bf312aa6bb8e1e421b812bf83db22c"
)
SEED = 2026092617
ALPHAS = [0.25, 1.0, 4.0]
MIXTURES_PER_ALPHA = 20000
NO_TOOL_THRESHOLDS = [0.05, 0.10, 0.25, 0.50]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def selected_findings(rows: list[dict[str, Any]]) -> dict[str, Any]:
    tool = [row for row in rows if row["task_type"] != "no_tool"]
    no_tool = [row for row in rows if row["task_type"] == "no_tool"]

    non_oracle = [row for row in tool if row["policy_family"] != "ORACLE"]
    coverage_failures = sorted(
        {
            row["policy_id"]
            for row in non_oracle
            if row["all_required_rate"] < 1.0
        }
    )

    adaptive_families = {
        "POSITIVE_SUPPORT",
        "RELATIVE_TOP",
        "CUMULATIVE_SCORE_MASS",
        "LARGEST_SCORE_DROP",
    }
    adaptive_no = [
        row for row in no_tool
        if row["policy_family"] in adaptive_families
    ]

    no_tool_by_policy: dict[str, list[float]] = defaultdict(list)
    for row in adaptive_no:
        no_tool_by_policy[row["policy_id"]].append(
            float(row["no_tool_nonempty_surface_rate"])
        )

    risky_detail: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in tool:
        if (
            row["stress_family"] == "RISKY_RELEVANT"
            and row["policy_id"] in {
                "RELATIVE_TOP:0.9",
                "LARGEST_SCORE_DROP",
                "FIXED_K:2",
            }
        ):
            risky_detail[row["policy_id"]].append(row)

    risky_summary: dict[str, dict[str, Any]] = {}
    for policy, prows in risky_detail.items():
        by_density: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for row in prows:
            by_density[int(row["density"])].append(row)
        risky_summary[policy] = {
            str(density): {
                "all_required_rate": mean([
                    float(r["all_required_rate"]) for r in drows
                ]),
                "mean_selected_k": mean([
                    float(r["mean_selected_k"]) for r in drows
                ]),
                "risky_wrong_exposure_rate": (
                    mean([
                        float(r["risky_wrong_exposure_rate"])
                        for r in drows
                        if r["risky_wrong_exposure_rate"] is not None
                    ])
                    if any(
                        r["risky_wrong_exposure_rate"] is not None
                        for r in drows
                    )
                    else None
                ),
                "mean_surface_bytes": mean([
                    float(r["mean_surface_bytes"]) for r in drows
                ]),
            }
            for density, drows in sorted(by_density.items())
        }

    valid_equiv: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in tool:
        if (
            row["stress_family"] == "VALID_EQUIVALENT"
            and row["policy_id"] in {
                "RELATIVE_TOP:0.9",
                "LARGEST_SCORE_DROP",
                "FIXED_K:2",
            }
        ):
            valid_equiv[row["policy_id"]].append(row)

    valid_equiv_summary: dict[str, dict[str, Any]] = {}
    for policy, prows in valid_equiv.items():
        by_density: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for row in prows:
            by_density[int(row["density"])].append(row)
        valid_equiv_summary[policy] = {
            str(density): {
                "all_required_rate": mean([
                    float(r["all_required_rate"]) for r in drows
                ]),
                "mean_selected_k": mean([
                    float(r["mean_selected_k"]) for r in drows
                ]),
                "mean_surface_bytes": mean([
                    float(r["mean_surface_bytes"]) for r in drows
                ]),
                "valid_alternative_recovery_rate": (
                    mean([
                        float(r["valid_alternative_recovery_rate"])
                        for r in drows
                        if r["valid_alternative_recovery_rate"] is not None
                    ])
                    if any(
                        r["valid_alternative_recovery_rate"] is not None
                        for r in drows
                    )
                    else None
                ),
            }
            for density, drows in sorted(by_density.items())
        }

    return {
        "coverage_failure_policy_ids": coverage_failures,
        "coverage_saturation_note": (
            "All non-oracle policies except FIXED_K:0 and FIXED_K:1 "
            "retain exact all-required coverage across every tool-required "
            "aggregate condition. BENCH-003 therefore primarily informs "
            "surface exposure / distractor burden, not hard retrieval recall."
        ),
        "adaptive_no_tool_nonempty_mean_by_policy": {
            policy: mean(values)
            for policy, values in sorted(no_tool_by_policy.items())
        },
        "no_tool_structural_observation": (
            "For nonzero targeted-distractor density, synthetic no-tool "
            "queries contain evidence overlapping plausible wrong tools in "
            "six stress families. Positive-score depth policies therefore "
            "cannot by themselves decide whether any tool should be exposed."
        ),
        "risky_relevant": risky_summary,
        "valid_equivalent": valid_equiv_summary,
    }


def build_macro(rows: list[dict[str, Any]]):
    grouped: dict[tuple[str, str, int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["task_type"],
            row["stress_family"],
            int(row["density"]),
            row["policy_id"],
        )
        grouped[key].append(row)

    policies = sorted({
        row["policy_id"] for row in rows if row["policy_id"] != "ORACLE"
    })
    conditions = sorted({
        (
            row["task_type"],
            row["stress_family"],
            int(row["density"]),
        )
        for row in rows
    })
    pindex = {p: i for i, p in enumerate(policies)}
    cindex = {c: i for i, c in enumerate(conditions)}

    shape = (len(conditions), len(policies))
    cov = np.zeros(shape)
    no_tool = np.zeros(shape)
    bytes_ = np.zeros(shape)

    for (task_type, stress, density, policy), grows in grouped.items():
        if policy == "ORACLE":
            continue
        ci = cindex[(task_type, stress, density)]
        pi = pindex[policy]

        def avg(key: str, default: float = 0.0) -> float:
            vals = [
                float(row[key]) for row in grows
                if row.get(key) is not None
            ]
            return sum(vals) / len(vals) if vals else default

        cov[ci, pi] = avg("all_required_rate")
        no_tool[ci, pi] = avg("no_tool_nonempty_surface_rate")
        bytes_[ci, pi] = avg("mean_surface_bytes")

    task_types = np.array([condition[0] for condition in conditions])
    tool_mask = (task_types != "no_tool").astype(float)
    no_mask = (task_types == "no_tool").astype(float)

    return conditions, policies, cov, no_tool, bytes_, tool_mask, no_mask


def workload_mc(rows: list[dict[str, Any]]) -> dict[str, Any]:
    (
        conditions,
        policies,
        cov,
        no_tool,
        bytes_,
        tool_mask,
        no_mask,
    ) = build_macro(rows)

    results: list[dict[str, Any]] = []

    for alpha_index, alpha in enumerate(ALPHAS):
        rng = np.random.default_rng(SEED + alpha_index)
        weights = rng.dirichlet(
            np.full(len(conditions), alpha),
            size=MIXTURES_PER_ALPHA,
        )
        tool_weight = weights @ tool_mask
        no_weight = weights @ no_mask

        weighted_cov = (
            weights @ (cov * tool_mask[:, None])
        ) / tool_weight[:, None]
        weighted_no = (
            weights @ (no_tool * no_mask[:, None])
        ) / no_weight[:, None]
        weighted_bytes = weights @ bytes_

        eligible_cov = weighted_cov >= 0.99
        best_no = np.min(
            np.where(eligible_cov, weighted_no, np.inf),
            axis=1,
        )

        feasibility = {}
        cheapest_policy_counts = {policy: 0 for policy in policies}

        for threshold in NO_TOOL_THRESHOLDS:
            feasible = eligible_cov & (weighted_no <= threshold)
            any_feasible = feasible.any(axis=1)
            feasibility[str(threshold)] = float(any_feasible.mean())

            if threshold == 0.50 and any_feasible.any():
                cost = np.where(feasible, weighted_bytes, np.inf)
                winners = np.argmin(cost, axis=1)
                for winner in winners[any_feasible]:
                    cheapest_policy_counts[policies[int(winner)]] += 1

        quantiles = {
            str(q): float(np.quantile(best_no, q))
            for q in [0.0, 0.01, 0.05, 0.50, 0.95, 0.99, 1.0]
        }

        results.append({
            "dirichlet_alpha": alpha,
            "mixtures": MIXTURES_PER_ALPHA,
            "coverage_requirement": 0.99,
            "no_tool_false_surface_feasibility": feasibility,
            "best_achievable_no_tool_false_surface_quantiles": quantiles,
            "cheapest_policy_counts_at_no_tool_threshold_0.50": (
                cheapest_policy_counts
            ),
        })

    return {
        "study": "BENCH-003-WORKLOAD-MC",
        "seed": SEED,
        "macro_condition_count": 120,
        "candidate_policy_count": len(policies),
        "mixtures_total": MIXTURES_PER_ALPHA * len(ALPHAS),
        "interpretation": (
            "No current non-oracle depth/selection policy is feasible at "
            "5% or 10% no-tool false-surface ceilings in the frozen 60k "
            "synthetic workload mixtures. This is evidence for separating "
            "tool-need admission from surface-depth selection."
        ),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregates", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    rows = read_jsonl(Path(args.aggregates))
    summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))

    if summary.get("state") != "PASS":
        raise SystemExit("SOURCE_BENCHMARK_NOT_PASS")
    if summary.get("observation_sha256") != SOURCE_OBSERVATION_DIGEST:
        raise SystemExit("SOURCE_OBSERVATION_DIGEST_MISMATCH")
    if summary.get("observation_count") != 483840:
        raise SystemExit("SOURCE_OBSERVATION_COUNT_MISMATCH")

    result = {
        "schema_version": "ftsl-bench003-post-analysis-v0.1",
        "source": {
            "run_id": SOURCE_RUN_ID,
            "artifact_id": SOURCE_ARTIFACT_ID,
            "artifact_digest": SOURCE_ARTIFACT_DIGEST,
            "observation_digest": SOURCE_OBSERVATION_DIGEST,
            "observation_count": summary["observation_count"],
            "aggregate_rows": summary["aggregate_rows"],
        },
        "selected_findings": selected_findings(rows),
        "workload_mc": workload_mc(rows),
        "claim_ceiling": (
            "Synthetic retrieval/surface evidence only. The analysis does "
            "not establish end-to-end Worker behavior, production safety, "
            "or a universal admission policy."
        ),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "study": result["workload_mc"]["study"],
        "mixtures_total": result["workload_mc"]["mixtures_total"],
        "source_observations": result["source"]["observation_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
