from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any

import numpy as np

SOURCE_RUN_ID = 36252133177
SOURCE_ARTIFACT_ID = 10909552716
SOURCE_ARTIFACT_DIGEST = (
    "sha256:decfb2f017b7fdea71965538e6ec4c412548f71f720f563bb3ca44a1a193b155"
)
SOURCE_OBSERVATION_DIGEST = (
    "6a1138a8c55e4e6d1fffea79612746c7282908f377ed2a79e18f20cb1a038c2c"
)
SEED = 2026092721
ALPHAS = [0.25, 1.0, 4.0]
MIXTURES_PER_ALPHA = 20000

ADMIT = "ADMIT_TOOL_SURFACE"
NO_TOOL = "NO_TOOL_SURFACE"
DEFER = "DEFER"

CONSTRAINTS = {
    "min_required_admit_recall": 0.99,
    "max_no_tool_false_admit_rate": 0.05,
    "min_defer_truth_recall": 0.90,
    "max_nontruth_defer_rate": 0.05,
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def one_downstream(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row for row in rows
        if row["downstream_policy"] == "RELATIVE_TOP:0.9"
    ]


def selected_findings(
    aggregates: list[dict[str, Any]],
    macro: list[dict[str, Any]],
) -> dict[str, Any]:
    macro_one: dict[str, dict[str, Any]] = {}
    for row in macro:
        if row["downstream_policy"] == "RELATIVE_TOP:0.9":
            macro_one[row["gate_policy_id"]] = row

    retrieval = {
        gate: row
        for gate, row in macro_one.items()
        if gate.startswith("TOP_SCORE_THRESHOLD:")
        or gate.startswith("TOP_MARGIN_THRESHOLD:")
    }
    state = {
        gate: row
        for gate, row in macro_one.items()
        if gate == "RULE_GATE_V0"
        or gate.startswith("LINEAR_NEED_SCORE_BANDS:")
    }

    retrieval_best_false = min(
        float(row["no_tool_false_admit_rate"])
        for row in retrieval.values()
    )
    retrieval_best_acc = max(
        float(row["macro_tri_state_accuracy"])
        for row in retrieval.values()
    )

    rule = macro_one["RULE_GATE_V0"]

    pair_families = {
        "PAIR_EXTERNAL_CONTEXT": (
            "EXTERNAL_STATE_REQUIRED",
            "LOCAL_CONTEXT_SUFFICIENT",
        ),
        "PAIR_SIDE_EFFECT_PERMISSION": (
            "SIDE_EFFECT_REQUIRED",
            "USER_FORBIDS_TOOL",
        ),
        "PAIR_COMPUTE_READINESS": (
            "SPECIALIZED_COMPUTE_REQUIRED",
            "PREMATURE_TOOL",
        ),
    }
    retrieval_pair_accuracy: dict[str, dict[str, float]] = {}
    rows = one_downstream(aggregates)
    for gate in sorted(retrieval):
        family_rows = defaultdict(list)
        for row in rows:
            if row["gate_policy_id"] == gate:
                family_rows[row["truth_family"]].append(
                    float(row["tri_state_accuracy"])
                )
        retrieval_pair_accuracy[gate] = {
            pair: sum(
                sum(family_rows[family]) / len(family_rows[family])
                for family in families
            ) / 2.0
            for pair, families in pair_families.items()
        }

    return {
        "retrieval_only": {
            "best_no_tool_false_admit_rate": retrieval_best_false,
            "best_macro_tri_state_accuracy": retrieval_best_acc,
            "paired_condition_accuracy": retrieval_pair_accuracy,
            "interpretation": (
                "Retrieval-only gates cannot distinguish matched pairs with "
                "identical registry/query/ranking evidence but different "
                "admission semantics."
            ),
        },
        "rule_gate_v0": {
            "required_admit_recall": rule["required_admit_recall"],
            "no_tool_false_admit_rate": rule["no_tool_false_admit_rate"],
            "defer_truth_recall": rule["defer_truth_recall"],
            "weighted_nontruth_defer_rate": (
                rule["weighted_nontruth_defer_rate"]
            ),
            "macro_tri_state_accuracy": rule["macro_tri_state_accuracy"],
            "post_gate_no_tool_nonempty_surface_rate": (
                rule["post_gate_no_tool_nonempty_surface_rate"]
            ),
            "mean_surface_bytes": rule["mean_surface_bytes"],
            "interpretation": (
                "Transparent admission-state features can represent the frozen "
                "synthetic truth contract much better than retrieval evidence "
                "alone. This is not evidence that RULE_GATE_V0 is a universal "
                "production rule."
            ),
        },
        "linear_gate_sweep": {
            gate: {
                "required_admit_recall": row["required_admit_recall"],
                "no_tool_false_admit_rate": row[
                    "no_tool_false_admit_rate"
                ],
                "defer_truth_recall": row["defer_truth_recall"],
                "weighted_nontruth_defer_rate": row[
                    "weighted_nontruth_defer_rate"
                ],
                "macro_tri_state_accuracy": row["macro_tri_state_accuracy"],
            }
            for gate, row in sorted(state.items())
            if gate != "RULE_GATE_V0"
        },
    }


def build_workload_arrays(
    aggregates: list[dict[str, Any]],
) -> tuple[
    list[tuple[int, str, float, str]],
    list[str],
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
]:
    rows = one_downstream(aggregates)
    conditions = sorted({
        (
            int(row["n"]),
            row["truth_family"],
            float(row["ambiguity"]),
            row["candidate_plausibility"],
        )
        for row in rows
    })
    policies = sorted({
        row["gate_policy_id"]
        for row in rows
        if row["gate_policy_id"] != "ORACLE_TRI_STATE"
    })
    cindex = {condition: i for i, condition in enumerate(conditions)}
    pindex = {policy: i for i, policy in enumerate(policies)}
    shape = (len(conditions), len(policies))

    req_admit = np.zeros(shape)
    no_false = np.zeros(shape)
    defer_recall = np.zeros(shape)
    nontruth_defer = np.zeros(shape)

    truth_by_condition: dict[
        tuple[int, str, float, str], str
    ] = {}

    for row in rows:
        condition = (
            int(row["n"]),
            row["truth_family"],
            float(row["ambiguity"]),
            row["candidate_plausibility"],
        )
        truth_by_condition[condition] = row["truth"]
        policy = row["gate_policy_id"]
        if policy == "ORACLE_TRI_STATE":
            continue
        ci = cindex[condition]
        pi = pindex[policy]
        truth = row["truth"]

        if truth == ADMIT:
            req_admit[ci, pi] = float(row["required_admit_recall"])
            nontruth_defer[ci, pi] = float(row["required_defer_rate"])
        elif truth == NO_TOOL:
            no_false[ci, pi] = float(row["no_tool_false_admit_rate"])
            nontruth_defer[ci, pi] = float(row["no_tool_defer_rate"])
        else:
            defer_recall[ci, pi] = float(row["defer_truth_recall"])

    truths = np.array([
        truth_by_condition[condition] for condition in conditions
    ])
    req_mask = (truths == ADMIT).astype(float)
    no_mask = (truths == NO_TOOL).astype(float)
    defer_mask = (truths == DEFER).astype(float)

    return (
        conditions,
        policies,
        req_admit,
        no_false,
        defer_recall,
        nontruth_defer,
        np.vstack([req_mask, no_mask, defer_mask]).T,
    )


def workload_mc(aggregates: list[dict[str, Any]]) -> dict[str, Any]:
    (
        conditions,
        policies,
        req_admit,
        no_false,
        defer_recall,
        nontruth_defer,
        masks,
    ) = build_workload_arrays(aggregates)

    req_mask = masks[:, 0]
    no_mask = masks[:, 1]
    defer_mask = masks[:, 2]
    nondefer_mask = 1.0 - defer_mask

    results: list[dict[str, Any]] = []

    for alpha_index, alpha in enumerate(ALPHAS):
        rng = np.random.default_rng(SEED + alpha_index)
        weights = rng.dirichlet(
            np.full(len(conditions), alpha),
            size=MIXTURES_PER_ALPHA,
        )

        req_weight = weights @ req_mask
        no_weight = weights @ no_mask
        defer_weight = weights @ defer_mask
        nondefer_weight = weights @ nondefer_mask

        required_recall = (
            weights @ (req_admit * req_mask[:, None])
        ) / req_weight[:, None]
        no_tool_false = (
            weights @ (no_false * no_mask[:, None])
        ) / no_weight[:, None]
        defer_truth_recall_weighted = (
            weights @ (defer_recall * defer_mask[:, None])
        ) / defer_weight[:, None]
        nontruth_defer_weighted = (
            weights @ (nontruth_defer * nondefer_mask[:, None])
        ) / nondefer_weight[:, None]

        feasible = (
            (required_recall >= CONSTRAINTS["min_required_admit_recall"])
            & (
                no_tool_false
                <= CONSTRAINTS["max_no_tool_false_admit_rate"]
            )
            & (
                defer_truth_recall_weighted
                >= CONSTRAINTS["min_defer_truth_recall"]
            )
            & (
                nontruth_defer_weighted
                <= CONSTRAINTS["max_nontruth_defer_rate"]
            )
        )

        counts = {
            policy: int(feasible[:, index].sum())
            for index, policy in enumerate(policies)
        }
        results.append({
            "dirichlet_alpha": alpha,
            "mixtures": MIXTURES_PER_ALPHA,
            "feasible_count_by_policy": counts,
            "feasible_fraction_by_policy": {
                policy: count / MIXTURES_PER_ALPHA
                for policy, count in counts.items()
            },
        })

    return {
        "study": "BENCH-004-WORKLOAD-MC",
        "seed": SEED,
        "conditions": len(conditions),
        "candidate_policies": len(policies),
        "mixtures_total": MIXTURES_PER_ALPHA * len(ALPHAS),
        "constraints": CONSTRAINTS,
        "results": results,
        "interpretation": (
            "Under the frozen synthetic aggregate evidence and declared "
            "constraints, RULE_GATE_V0 is the only non-oracle policy with "
            "any feasible workload mixtures. This establishes a synthetic "
            "architectural separation, not a universal rule or provider win."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregates", required=True)
    parser.add_argument("--macro", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    aggregates = read_jsonl(Path(args.aggregates))
    macro = read_jsonl(Path(args.macro))
    summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))

    if summary.get("state") != "PASS":
        raise SystemExit("SOURCE_BENCHMARK_NOT_PASS")
    if summary.get("observation_count") != 884736:
        raise SystemExit("SOURCE_OBSERVATION_COUNT_MISMATCH")
    if summary.get("observation_sha256") != SOURCE_OBSERVATION_DIGEST:
        raise SystemExit("SOURCE_OBSERVATION_DIGEST_MISMATCH")

    result = {
        "schema_version": "ftsl-bench004-post-analysis-v0.1",
        "source": {
            "run_id": SOURCE_RUN_ID,
            "artifact_id": SOURCE_ARTIFACT_ID,
            "artifact_digest": SOURCE_ARTIFACT_DIGEST,
            "observation_count": summary["observation_count"],
            "observation_sha256": summary["observation_sha256"],
            "aggregate_rows": summary["aggregate_rows"],
            "macro_rows": summary["macro_rows"],
        },
        "selected_findings": selected_findings(aggregates, macro),
        "workload_mc": workload_mc(aggregates),
        "claim_ceiling": (
            "Synthetic Tool-Need admission evidence only. RULE_GATE_V0 "
            "encodes the frozen structured state semantics and must not be "
            "interpreted as a universal production rule or provider result."
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
        "source_observations": result["source"]["observation_count"],
        "mixtures_total": result["workload_mc"]["mixtures_total"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
