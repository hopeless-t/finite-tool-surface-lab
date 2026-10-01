from __future__ import annotations

import unittest

from finite_tool_surface_lab.coordinate_identity import (
    CoordinateProfile,
    representation_alias_risk,
)


class CoordinateIdentityTests(unittest.TestCase):
    def test_same_outer_api_can_hide_different_coordinate_representations(self):
        nvidia = CoordinateProfile(
            outer_api="deep_gemm.fp8_gemm",
            value_dtype="FP8",
            backend="nvidia",
            scale_encoding="NVIDIA_NATIVE",
            scale_layout="NVIDIA_NATIVE",
        )
        ascend = CoordinateProfile(
            outer_api="deep_gemm.fp8_gemm",
            value_dtype="FP8",
            backend="ascend",
            scale_encoding="UE8M0_PAIR_PACKED_INT16",
            scale_layout="MN_MAJOR",
        )

        self.assertEqual(nvidia.naive_surface_key(), ascend.naive_surface_key())
        self.assertNotEqual(nvidia.coordinate_signature(), ascend.coordinate_signature())
        self.assertTrue(representation_alias_risk(nvidia, ascend))

    def test_identical_coordinate_profile_does_not_raise_alias_risk(self):
        a = CoordinateProfile(
            outer_api="deep_gemm.bf16_gemm",
            value_dtype="BF16",
            backend="ascend",
            scale_encoding="NONE",
            scale_layout="NONE",
        )
        self.assertFalse(representation_alias_risk(a, a))


if __name__ == "__main__":
    unittest.main()
