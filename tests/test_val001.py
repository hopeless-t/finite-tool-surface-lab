from __future__ import annotations

import unittest
from pathlib import Path

from finite_tool_surface_lab.policies import (
    expected_random_recall,
    probability_random_contains_all,
)
from finite_tool_surface_lab.spec import load_spec
from finite_tool_surface_lab.synthetic import (
    canonical_json_bytes,
    generate_registry,
)
from finite_tool_surface_lab.validation import (
    failure_injection_probe,
    run_validation,
)


ROOT = Path(__file__).resolve().parents[1]


class Val001Tests(unittest.TestCase):
    def test_registry_is_byte_deterministic(self) -> None:
        kwargs = dict(n=128, overlap=0.5, alias_rate=0.15, seed=20260926)
        self.assertEqual(
            canonical_json_bytes(generate_registry(**kwargs)),
            canonical_json_bytes(generate_registry(**kwargs)),
        )

    def test_random_known_answers(self) -> None:
        self.assertAlmostEqual(
            expected_random_recall(n=100, k=7, gold_count=2),
            0.07,
        )
        self.assertAlmostEqual(
            probability_random_contains_all(
                n=10, k=3, gold_count=2
            ),
            3 / 10 * 2 / 9,
        )

    def test_failure_injection_is_detected(self) -> None:
        self.assertTrue(all(failure_injection_probe(20260926).values()))

    def test_smoke_validation_passes(self) -> None:
        spec = load_spec(ROOT / "specs" / "VAL-001.json")
        result = run_validation(spec, quick=True)
        self.assertEqual(result["state"], "PASS")
        self.assertLessEqual(
            result["max_random_theory_abs_error"],
            spec["acceptance"]["random_k_theory_abs_error_max"],
        )


if __name__ == "__main__":
    unittest.main()
