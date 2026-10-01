from __future__ import annotations

import unittest

from finite_tool_surface_lab.compat_coordinate import (
    CompatibilityItem,
    CompatibilityProfile,
    scalar_alias_risk,
)


class CompatibilityCoordinateTests(unittest.TestCase):
    def test_same_summary_can_hide_different_blockers(self):
        a = CompatibilityProfile(
            (
                CompatibilityItem("imports", "next/link", "supported"),
                CompatibilityItem("config", "images", "partial"),
                CompatibilityItem("libraries", "critical-auth-lib", "unsupported"),
            )
        )
        b = CompatibilityProfile(
            (
                CompatibilityItem("imports", "next/link", "unsupported"),
                CompatibilityItem("config", "images", "partial"),
                CompatibilityItem("libraries", "critical-auth-lib", "supported"),
            )
        )

        self.assertEqual(a.scalar_summary(), b.scalar_summary())
        self.assertNotEqual(a.coordinate_vector(), b.coordinate_vector())
        self.assertTrue(scalar_alias_risk(a, b))

    def test_same_coordinates_are_not_aliases(self):
        a = CompatibilityProfile(
            (CompatibilityItem("config", "images", "partial"),)
        )
        self.assertFalse(scalar_alias_risk(a, a))


if __name__ == "__main__":
    unittest.main()
