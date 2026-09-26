from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from finite_tool_surface_lab.adaptive import positive_support_surface
from finite_tool_surface_lab.bench003 import (
    evaluate_surface,
    run_benchmark,
    write_evidence,
)
from finite_tool_surface_lab.distractor_synthetic import (
    generate_distractor_case,
    validate_distractor_case,
)
from finite_tool_surface_lab.retrieval import token_jaccard_rank
from finite_tool_surface_lab.spec import load_spec


ROOT = Path(__file__).resolve().parents[1]


class Bench003Tests(unittest.TestCase):
    def test_fixed_n_and_gold_identity(self) -> None:
        registry, task = generate_distractor_case(
            n=32,
            task_type="multi_tool",
            stress_family="RISKY_RELEVANT",
            density=15,
            repeat=0,
            seed=20260926,
        )
        self.assertEqual(len(registry["tools"]), 32)
        checks = validate_distractor_case(registry, task)
        self.assertTrue(all(checks.values()))

    def test_valid_equivalent_counts_as_capability_coverage(self) -> None:
        registry, task = generate_distractor_case(
            n=32,
            task_type="single_tool",
            stress_family="VALID_EQUIVALENT",
            density=3,
            repeat=0,
            seed=20260926,
        )
        alt = task["valid_equivalent_ids"][0]
        result = evaluate_surface(registry, task, (alt,))
        self.assertTrue(result["all_required"])
        self.assertFalse(result["canonical_all"])
        self.assertEqual(result["wrong_distractor_selected"], 0)

    def test_random_irrelevant_no_tool_has_zero_evidence(self) -> None:
        registry, task = generate_distractor_case(
            n=32,
            task_type="no_tool",
            stress_family="RANDOM_IRRELEVANT",
            density=15,
            repeat=0,
            seed=20260926,
        )
        ranked = token_jaccard_rank(registry, task)
        self.assertEqual(ranked[0][1], 0.0)
        self.assertEqual(positive_support_surface(ranked), ())

    def test_risky_relevant_is_wrong_not_equivalent(self) -> None:
        registry, task = generate_distractor_case(
            n=32,
            task_type="single_tool",
            stress_family="RISKY_RELEVANT",
            density=3,
            repeat=0,
            seed=20260926,
        )
        self.assertEqual(len(task["risky_wrong_ids"]), 3)
        self.assertFalse(
            set(task["risky_wrong_ids"]) & set(task["valid_equivalent_ids"])
        )

    def test_smoke_contract(self) -> None:
        spec = load_spec(ROOT / "specs" / "BENCH-003.json")
        aggregates, digest, count, checks = run_benchmark(
            spec, quick=True
        )
        with tempfile.TemporaryDirectory() as directory:
            summary = write_evidence(
                out_dir=Path(directory),
                spec=spec,
                aggregates=aggregates,
                observation_digest=digest,
                observation_count=count,
                checks=checks,
                quick=True,
            )
        self.assertEqual(summary["state"], "PASS")
        self.assertGreater(count, 0)
        self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main()
