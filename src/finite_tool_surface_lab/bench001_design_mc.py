from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


REGISTRY_SIZES = (32, 128, 512, 2048)
K_VALUES = (1, 2, 3, 5, 8, 13, 20, 32, 50)
GOLD_COUNTS = (1, 2)


def _hit_probabilities(n: int, k: int, gold_count: int) -> np.ndarray:
    denominator = math.comb(n, k)
    probs = []
    for hits in range(gold_count + 1):
        if hits <= k and k - hits <= n - gold_count:
            numerator = (
                math.comb(gold_count, hits)
                * math.comb(n - gold_count, k - hits)
            )
            probs.append(numerator / denominator)
        else:
            probs.append(0.0)
    result = np.asarray(probs, dtype=float)
    return result / result.sum()


def run(
    *,
    simulations: int,
    repeats_per_cell: int,
    seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    pairs = [
        (n, k, gold_count)
        for n in REGISTRY_SIZES
        for k in K_VALUES
        if k <= n
        for gold_count in GOLD_COUNTS
    ]

    max_error = np.zeros(simulations, dtype=np.float32)
    cells: list[dict[str, Any]] = []

    for n, k, gold_count in pairs:
        probabilities = _hit_probabilities(n, k, gold_count)
        counts = rng.multinomial(
            repeats_per_cell,
            probabilities,
            size=simulations,
        )
        hit_values = np.arange(gold_count + 1, dtype=int)
        total_hits = counts @ hit_values

        empirical_recall = total_hits / (
            repeats_per_cell * gold_count
        )
        exact_expected_recall = k / n
        error = np.abs(empirical_recall - exact_expected_recall)
        max_error = np.maximum(
            max_error,
            error.astype(np.float32),
        )

        cells.append(
            {
                "n": n,
                "k": k,
                "gold_count": gold_count,
                "exact_expected_recall": exact_expected_recall,
                "mean_abs_error": float(error.mean()),
                "p95_abs_error": float(np.quantile(error, 0.95)),
                "p99_abs_error": float(np.quantile(error, 0.99)),
            }
        )

    quantiles = {
        str(q): float(np.quantile(max_error, q))
        for q in (0.5, 0.9, 0.95, 0.99, 0.999)
    }

    return {
        "study_id": "BENCH-001-DESIGN-MC",
        "simulations": simulations,
        "repeats_per_cell": repeats_per_cell,
        "seed": seed,
        "random_cells": len(pairs),
        "max_abs_error_across_cells_quantiles": quantiles,
        "mean_max_abs_error_across_cells": float(max_error.mean()),
        "cells": cells,
        "decision_support": {
            "empirical_random_role": "NEGATIVE_CONTROL",
            "primary_random_baseline": "EXACT_HYPERGEOMETRIC_EXPECTATION",
            "reason": (
                "With 64 repeats per exact cell, empirical RANDOM-k is "
                "too noisy to define the chance baseline across the sweep."
            ),
        },
        "claim_boundary": (
            "This Monte Carlo evaluates the sampling variability of the "
            "BENCH-001 random control under declared synthetic assumptions. "
            "It is design decision support, not evidence that any Tool "
            "surface improves a Worker."
        ),
    }


def to_markdown(result: dict[str, Any]) -> str:
    q = result["max_abs_error_across_cells_quantiles"]
    lines = [
        "# BENCH-001 Design Monte Carlo",
        "",
        f"Simulations: **{result['simulations']:,}**",
        f"Repeats per exact cell: **{result['repeats_per_cell']}**",
        f"Random baseline cells: **{result['random_cells']}**",
        "",
        "## Maximum absolute RANDOM-k recall error across all cells",
        "",
        "| Quantile | Max abs error |",
        "| ---: | ---: |",
    ]
    for key in ("0.5", "0.9", "0.95", "0.99", "0.999"):
        lines.append(f"| {key} | {q[key]:.6f} |")
    lines += [
        "",
        "## Decision support",
        "",
        "- Empirical RANDOM-k: **negative control**.",
        "- Primary chance baseline: **exact hypergeometric expectation**.",
        "",
        result["claim_boundary"],
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulations", type=int, default=250_000)
    parser.add_argument("--repeats-per-cell", type=int, default=64)
    parser.add_argument("--seed", type=int, default=2026092601)
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown", required=True)
    args = parser.parse_args()

    if args.simulations < 1:
        raise SystemExit("simulations must be positive")
    if args.repeats_per_cell < 1:
        raise SystemExit("repeats-per-cell must be positive")

    result = run(
        simulations=args.simulations,
        repeats_per_cell=args.repeats_per_cell,
        seed=args.seed,
    )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    markdown = Path(args.markdown)
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text(to_markdown(result), encoding="utf-8")

    print(
        json.dumps(
            {
                "study_id": result["study_id"],
                "simulations": result["simulations"],
                "p50_max_error": result[
                    "max_abs_error_across_cells_quantiles"
                ]["0.5"],
                "p95_max_error": result[
                    "max_abs_error_across_cells_quantiles"
                ]["0.95"],
                "primary_random_baseline": result[
                    "decision_support"
                ]["primary_random_baseline"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
