from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from finite_tool_surface_lab.admission_synthetic import (
    generate_admission_case,
    retrieval_fingerprint,
    validate_case,
)
from finite_tool_surface_lab.bench004 import (
    ADMIT,
    DEFER,
    NO_TOOL,
    linear_need_score,
    rule_gate,
    run_benchmark,
    write_evidence,
)
from finite_tool_surface_lab.retrieval import token_jaccard_rank
from finite_tool_surface_lab.spec import load_spec


ROOT = Path(__file__).resolve().parents[1]


class Bench004Tests(unittest.TestCase):
    def test_retrieval_isomorphic_pair(self) -> None:
        a_reg, a_task = generate_admission_case(
            n=32,
            family="EXTERNAL_STATE_REQUIRED",
            ambiguity=0.5,
            plausibility="HIGH",
            repeat=1,
            seed=20260927,
        )
        b_reg, b_task = generate_admission_case(
            n=32,
            family="LOCAL_CONTEXT_SUFFICIENT",
            ambiguity=0.5,
            plausibility="HIGH",
            repeat=1,
            seed=20260927,
        )
        self.assertEqual(
            retrieval_fingerprint(a_reg, a_task),
            retrieval_fingerprint(b_reg, b_task),
        )
        self.assertEqual(
            token_jaccard_rank(a_reg, a_task),
            token_jaccard_rank(b_reg, b_task),
        )
        self.assertNotEqual(a_task["truth"], b_task["truth"])

    def test_truth_hidden_and_authority_absent(self) -> None:
        registry, task = generate_admission_case(
            n=32,
            family="USER_FORBIDS_TOOL",
            ambiguity=0.25,
            plausibility="HIGH",
            repeat=0,
            seed=20260927,
        )
        checks = validate_case(registry, task)
        self.assertTrue(all(checks.values()))

    def test_rule_gate_easy_cases(self) -> None:
        _, admit = generate_admission_case(
            n=32,
            family="EXTERNAL_STATE_REQUIRED",
            ambiguity=0.0,
            plausibility="HIGH",
            repeat=0,
            seed=20260927,
        )
        _, no_tool = generate_admission_case(
            n=32,
            family="USER_FORBIDS_TOOL",
            ambiguity=0.0,
            plausibility="HIGH",
            repeat=0,
            seed=20260927,
        )
        _, defer = generate_admission_case(
            n=32,
            family="AMBIGUOUS_INTENT",
            ambiguity=0.0,
            plausibility="HIGH",
            repeat=0,
            seed=20260927,
        )
        self.assertEqual(rule_gate(admit["gate_input"]), ADMIT)
        self.assertEqual(rule_gate(no_tool["gate_input"]), NO_TOOL)
        self.assertEqual(rule_gate(defer["gate_input"]), DEFER)

    def test_linear_score_is_bounded(self) -> None:
        _, task = generate_admission_case(
            n=32,
            family="SPECIALIZED_COMPUTE_REQUIRED",
            ambiguity=0.75,
            plausibility="LOW",
            repeat=0,
            seed=20260927,
        )
        score = linear_need_score(task["gate_input"])
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_smoke_contract(self) -> None:
        spec = load_spec(ROOT / "specs" / "BENCH-004.json")
        aggregates, digest, count, checks = run_benchmark(
            spec, quick=True
        )
        with tempfile.TemporaryDirectory() as directory:
            summary = write_evidence(
                out_dir=Path(directory),
                spec=spec,
                aggregates=aggregates,
                digest=digest,
                count=count,
                checks=checks,
                quick=True,
            )
        self.assertEqual(summary["state"], "PASS")
        self.assertGreater(count, 0)
        self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main()
