from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


EPSILONS = (0.0, 0.01, 0.02, 0.05, 0.1)
ALPHAS = (0.25, 1.0, 4.0)


def _load(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def run_mc(
    rows: list[dict[str, Any]],
    *,
    mixtures_per_alpha: int,
    seed: int,
) -> dict[str, Any]:
    required = [row for row in rows if row["task_type"] != "no_tool"]
    conditions = sorted({
        (
            row["n"],
            row["overlap"],
            row["alias_rate"],
            row["task_type"],
        )
        for row in required
    })
    condition_index = {condition: i for i, condition in enumerate(conditions)}

    availability: dict[str, set[tuple[Any, ...]]] = {}
    for row in required:
        availability.setdefault(row["policy_id"], set()).add(
            (
                row["n"],
                row["overlap"],
                row["alias_rate"],
                row["task_type"],
            )
        )

    candidates = sorted(
        policy_id
        for policy_id, seen in availability.items()
        if len(seen) == len(conditions) and policy_id != "ORACLE"
    )
    candidate_index = {
        policy_id: index for index, policy_id in enumerate(candidates)
    }

    coverage = np.full(
        (len(conditions), len(candidates)),
        np.nan,
        dtype=np.float64,
    )
    surface_bytes = np.full_like(coverage, np.nan)

    for row in required:
        policy_id = row["policy_id"]
        if policy_id not in candidate_index:
            continue
        condition = (
            row["n"],
            row["overlap"],
            row["alias_rate"],
            row["task_type"],
        )
        i = condition_index[condition]
        j = candidate_index[policy_id]
        coverage[i, j] = row["all_gold_rate"]
        surface_bytes[i, j] = row["mean_surface_bytes"]

    if np.isnan(coverage).any() or np.isnan(surface_bytes).any():
        raise ValueError("INCOMPLETE_POLICY_MATRIX")

    rng = np.random.default_rng(seed)
    result: dict[str, Any] = {
        "study_id": "BENCH-002-WORKLOAD-MIX-MC",
        "state": "PASS",
        "seed": seed,
        "conditions": len(conditions),
        "candidate_policies": candidates,
        "mixtures_per_alpha": mixtures_per_alpha,
        "alpha_values": list(ALPHAS),
        "epsilons": list(EPSILONS),
        "total_workload_mixtures": mixtures_per_alpha * len(ALPHAS),
        "total_constrained_policy_selections": (
            mixtures_per_alpha * len(ALPHAS) * len(EPSILONS)
        ),
        "results": [],
        "interpretation": (
            "For each random workload mixture, select the policy with the "
            "lowest weighted mean serialized surface bytes among policies "
            "whose weighted exact all-gold coverage is at least 1-epsilon."
        ),
        "claim_ceiling": (
            "Synthetic workload-mixture robustness analysis over BENCH-002 "
            "aggregate conditions; not Worker performance."
        ),
    }

    batch = 2000
    for alpha in ALPHAS:
        counts = {
            epsilon: np.zeros(len(candidates), dtype=np.int64)
            for epsilon in EPSILONS
        }

        for start in range(0, mixtures_per_alpha, batch):
            size = min(batch, mixtures_per_alpha - start)
            weights = rng.dirichlet(
                np.full(len(conditions), alpha, dtype=np.float64),
                size=size,
            )
            weighted_coverage = weights @ coverage
            weighted_bytes = weights @ surface_bytes

            for epsilon in EPSILONS:
                eligible = weighted_coverage >= 1.0 - epsilon - 1e-12
                objective = np.where(eligible, weighted_bytes, np.inf)
                if np.any(np.all(~eligible, axis=1)):
                    raise ValueError("NO_ELIGIBLE_POLICY")
                winners = np.argmin(objective, axis=1)
                np.add.at(counts[epsilon], winners, 1)

        for epsilon in EPSILONS:
            total = int(counts[epsilon].sum())
            selections = [
                {
                    "policy_id": candidates[index],
                    "count": int(count),
                    "frequency": float(count / total),
                }
                for index, count in enumerate(counts[epsilon])
                if count
            ]
            selections.sort(
                key=lambda item: (-item["count"], item["policy_id"])
            )
            result["results"].append(
                {
                    "dirichlet_alpha": alpha,
                    "epsilon": epsilon,
                    "selections": selections,
                }
            )

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregates", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--mixtures-per-alpha", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=2026092609)
    args = parser.parse_args()

    result = run_mc(
        _load(Path(args.aggregates)),
        mixtures_per_alpha=args.mixtures_per_alpha,
        seed=args.seed,
    )
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "study_id": result["study_id"],
        "state": result["state"],
        "total_workload_mixtures": result["total_workload_mixtures"],
        "total_constrained_policy_selections": (
            result["total_constrained_policy_selections"]
        ),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
