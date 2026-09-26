from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from finite_tool_surface_lab.adaptive import (
    cumulative_mass_surface,
    largest_score_drop_surface,
    positive_support_surface,
    relative_top_surface,
    tie_blocks_preserved,
)
from finite_tool_surface_lab.bench002 import run_benchmark, write_evidence
from finite_tool_surface_lab.retrieval import (
    serialized_stub_byte_sizes,
    surface_serialized_bytes,
    surface_serialized_bytes_from_sizes,
)
from finite_tool_surface_lab.synthetic import generate_registry
from finite_tool_surface_lab.spec import load_spec


ROOT = Path(__file__).resolve().parents[1]


class Bench002Tests(unittest.TestCase):
    def test_zero_evidence_abstains(self) -> None:
        ranked = [("A", 0.0), ("B", 0.0), ("C", 0.0)]
        self.assertEqual(positive_support_surface(ranked), ())
        self.assertEqual(relative_top_surface(ranked, threshold=0.5), ())
        self.assertEqual(
            cumulative_mass_surface(ranked, threshold=0.8), ()
        )
        self.assertEqual(largest_score_drop_surface(ranked), ())

    def test_cumulative_mass_preserves_tie_block(self) -> None:
        ranked = [
            ("A", 1.0),
            ("B", 0.5),
            ("C", 0.5),
            ("D", 0.1),
        ]
        surface = cumulative_mass_surface(ranked, threshold=0.55)
        self.assertEqual(surface, ("A", "B", "C"))
        self.assertTrue(tie_blocks_preserved(ranked, surface))

    def test_relative_top_preserves_ties(self) -> None:
        ranked = [
            ("A", 1.0),
            ("B", 0.5),
            ("C", 0.5),
            ("D", 0.1),
        ]
        self.assertEqual(
            relative_top_surface(ranked, threshold=0.5),
            ("A", "B", "C"),
        )

    def test_largest_drop(self) -> None:
        ranked = [
            ("A", 1.0),
            ("B", 0.9),
            ("C", 0.2),
            ("D", 0.2),
        ]
        self.assertEqual(
            largest_score_drop_surface(ranked),
            ("A", "B"),
        )

    def test_precomputed_surface_bytes_are_exact(self) -> None:
        registry = generate_registry(
            n=32, overlap=0.5, alias_rate=0.15, seed=20260927
        )
        sizes = serialized_stub_byte_sizes(registry)
        ids = tuple(tool["tool_id"] for tool in registry["tools"])
        for surface in ((), ids[:1], ids[:7], ids):
            self.assertEqual(
                surface_serialized_bytes(registry, surface),
                surface_serialized_bytes_from_sizes(sizes, surface),
            )

    def test_smoke_contract(self) -> None:
        spec = load_spec(ROOT / "specs" / "BENCH-002.json")
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
        self.assertEqual(
            summary["adaptive_no_tool_nonempty_rate_range"],
            [0.0, 0.0],
        )


if __name__ == "__main__":
    unittest.main()
