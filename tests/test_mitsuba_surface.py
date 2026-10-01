from __future__ import annotations

import unittest

from finite_tool_surface_lab.mitsuba_surface import (
    capability_surface_record,
    surface_bytes,
    tool_ids,
    validate_call,
)


class MitsubaSurfaceTests(unittest.TestCase):
    def test_narrow_surface_is_visual_only_and_complete(self):
        ids = set(tool_ids("VISUAL_NARROW_V0"))
        self.assertEqual(ids, {
            "mitsuba.visual.describe",
            "mitsuba.visual.compare",
            "mitsuba.visual.compile_prompt",
            "mitsuba.visual.check_constraints",
        })
        self.assertEqual(
            capability_surface_record("VISUAL_NARROW_V0")[
                "side_effecting_tool_count"
            ],
            0,
        )

    def test_broad_surface_has_more_serialized_exposure(self):
        self.assertGreater(
            surface_bytes("BROAD_AGENT_MENU_V0"),
            surface_bytes("VISUAL_NARROW_V0"),
        )
        self.assertGreater(
            capability_surface_record("BROAD_AGENT_MENU_V0")[
                "side_effecting_tool_count"
            ],
            0,
        )

    def test_call_shape_is_exact_and_unknown_tools_are_denied(self):
        validate_call(
            "VISUAL_NARROW_V0",
            "mitsuba.visual.describe",
            {"image_ref": "artifact:abc", "instruction": "describe composition"},
        )
        with self.assertRaisesRegex(ValueError, "shape"):
            validate_call(
                "VISUAL_NARROW_V0",
                "mitsuba.visual.describe",
                {
                    "image_ref": "artifact:abc",
                    "instruction": "describe",
                    "command": "rm -rf /",
                },
            )
        with self.assertRaisesRegex(ValueError, "not_exposed"):
            validate_call(
                "VISUAL_NARROW_V0",
                "shell.exec",
                {"command": "echo nope"},
            )

    def test_surface_records_never_grant_execution_authority(self):
        for surface in (
            "NO_TOOL_V0",
            "VISUAL_NARROW_V0",
            "BROAD_AGENT_MENU_V0",
        ):
            row = capability_surface_record(surface)
            self.assertEqual(row["authority_effect"], "NONE")
            self.assertFalse(row["execution_authority_granted"])


if __name__ == "__main__":
    unittest.main()
