from __future__ import annotations
import unittest

from finite_tool_surface_lab.atomic_hillclimb import EvalPoint, evaluate_atomic_patch


class AtomicHillclimbTests(unittest.TestCase):
    def test_train_only_gain_reverts(self):
        row=evaluate_atomic_patch(
            mutation_id="prompt-rule-1",
            baseline=EvalPoint(.70,.70,.02),
            candidate=EvalPoint(.80,.71,.02),
        )
        self.assertEqual(row["status"],"REVERT")
        self.assertEqual(row["reason"],"train_only_gain_overfit_suspected")

    def test_heldout_gain_above_noise_keeps(self):
        row=evaluate_atomic_patch(
            mutation_id="skill-trigger-1",
            baseline=EvalPoint(.70,.70,.02),
            candidate=EvalPoint(.76,.75,.02),
        )
        self.assertEqual(row["status"],"KEEP")
        self.assertEqual(row["reason"],"heldout_gain_exceeds_noise")

    def test_gain_inside_noise_does_not_merge(self):
        row=evaluate_atomic_patch(
            mutation_id="tiny-change",
            baseline=EvalPoint(.70,.70,.03),
            candidate=EvalPoint(.72,.72,.03),
        )
        self.assertEqual(row["status"],"HOLD")

    def test_cost_reduction_can_keep_when_quality_holds(self):
        row=evaluate_atomic_patch(
            mutation_id="context-shield",
            baseline=EvalPoint(.70,.70,.02,cost=4.0),
            candidate=EvalPoint(.71,.70,.02,cost=1.0),
            objective="COST_WITH_QUALITY_FLOOR",
            minimum_test_score=.68,
        )
        self.assertEqual(row["status"],"KEEP")
        self.assertEqual(row["reason"],"cost_reduced_quality_preserved")

    def test_authority_remains_none(self):
        row=evaluate_atomic_patch(
            mutation_id="x",
            baseline=EvalPoint(.5,.5,.01),
            candidate=EvalPoint(.6,.6,.01),
        )
        self.assertEqual(row["authority_effect"],"NONE")


if __name__=="__main__":
    unittest.main()
