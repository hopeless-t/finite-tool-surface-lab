from __future__ import annotations

import unittest

from finite_tool_surface_lab.compatibility_evidence import (
    CompatibilityItem,
    compatibility_profile,
    substitution_gate,
)


class CompatibilityEvidenceTests(unittest.TestCase):
    def profile(self):
        return compatibility_profile(
            source_surface="Next.js 16 public API",
            target_surface="vinext 1.0",
            items=(
                CompatibilityItem("routing","SUPPORTED","test:routing"),
                CompatibilityItem("server-actions","SUPPORTED","test:server-actions"),
                CompatibilityItem("partial-prerender","DEFERRED","tracker:ppr"),
                CompatibilityItem("legacy-edge-runtime","UNSUPPORTED","tracker:edge"),
                CompatibilityItem("third-party-webpack-plugin","NEEDS_EQUIVALENT","tracker:plugin"),
                CompatibilityItem("rare-config","PARTIAL","test:rare-config"),
            ),
        )

    def test_profile_does_not_collapse_deferred_into_unsupported(self):
        row=self.profile()
        self.assertEqual(row["status_counts"]["DEFERRED"],1)
        self.assertEqual(row["status_counts"]["NEEDS_EQUIVALENT"],1)
        self.assertEqual(row["status_counts"]["UNSUPPORTED"],1)
        self.assertTrue(row["compatibility_is_not_identity"])

    def test_supported_fraction_has_explicit_denominator(self):
        row=self.profile()
        self.assertEqual(row["feature_count"],6)
        self.assertAlmostEqual(row["strict_supported_fraction"],2/6)

    def test_required_supported_features_pass_only_with_evidence(self):
        row=substitution_gate(self.profile(),["routing","server-actions"])
        self.assertEqual(row["status"],"COMPATIBLE")

    def test_partial_required_feature_demands_review(self):
        row=substitution_gate(self.profile(),["routing","rare-config"])
        self.assertEqual(row["status"],"REVIEW")
        self.assertEqual(row["reason"],"required_feature_partial")

    def test_deferred_or_unsupported_required_feature_blocks(self):
        row=substitution_gate(self.profile(),["partial-prerender"])
        self.assertEqual(row["status"],"BLOCKED")
        self.assertEqual(row["reason"],"required_feature_not_supported")

    def test_supported_without_evidence_is_not_auto_compatible(self):
        profile=compatibility_profile(
            source_surface="A",
            target_surface="B",
            items=(CompatibilityItem("x","SUPPORTED"),),
        )
        row=substitution_gate(profile,["x"])
        self.assertEqual(row["status"],"REVIEW")
        self.assertEqual(row["reason"],"supported_feature_unevidenced")


if __name__=="__main__":
    unittest.main()
