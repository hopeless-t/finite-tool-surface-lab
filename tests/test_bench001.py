from __future__ import annotations

import unittest
from pathlib import Path
import tempfile

from finite_tool_surface_lab.bench001 import (
    run_benchmark,
    write_evidence,
)
from finite_tool_surface_lab.bench_metrics import (
    chance_all_gold,
    chance_any_gold,
)
from finite_tool_surface_lab.retrieval import token_jaccard_rank
from finite_tool_surface_lab.spec import load_spec
from finite_tool_surface_lab.synthetic import generate_registry, generate_task


ROOT = Path(__file__).resolve().parents[1]


class Bench001Tests(unittest.TestCase):
    def test_hypergeometric_known_answers(self) -> None:
        self.assertAlmostEqual(
            chance_any_gold(n=10, k=3, gold_count=2),
            1 - (8 * 7 * 6) / (10 * 9 * 8),
        )
        self.assertAlmostEqual(
            chance_all_gold(n=10, k=3, gold_count=2),
            3 / 10 * 2 / 9,
        )

    def test_token_jaccard_rank_is_deterministic(self) -> None:
        registry = generate_registry(
            n=32,
            overlap=0.75,
            alias_rate=0.15,
            seed=20260926,
        )
        task = generate_task(
            registry=registry,
            task_type="single_tool",
            repeat=0,
            seed=20260926,
        )
        self.assertEqual(
            token_jaccard_rank(registry, task),
            token_jaccard_rank(registry, task),
        )

    def test_quick_benchmark_contract(self) -> None:
        spec = load_spec(ROOT / "specs" / "BENCH-001.json")
        rows, invalid = run_benchmark(spec, quick=True)
        with tempfile.TemporaryDirectory() as directory:
            summary = write_evidence(
                out_dir=Path(directory),
                spec=spec,
                rows=rows,
                invalid=invalid,
                quick=True,
            )
        self.assertEqual(summary["state"], "PASS")
        self.assertGreater(summary["raw_rows"], 0)
        self.assertGreater(summary["invalid_rows"], 0)


if __name__ == "__main__":
    unittest.main()
