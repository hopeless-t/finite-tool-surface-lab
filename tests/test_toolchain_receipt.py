from __future__ import annotations

import unittest

from finite_tool_surface_lab.toolchain_receipt import (
    ToolComponent,
    ToolchainReceipt,
    same_surface_different_toolchain,
)


class ToolchainReceiptTests(unittest.TestCase):
    def test_single_surface_does_not_imply_single_component_identity(self):
        old = ToolchainReceipt(
            "vp",
            (
                ToolComponent("vite", "x"),
                ToolComponent("vitest", "y"),
                ToolComponent("rolldown", "z"),
            ),
        )
        new = ToolchainReceipt(
            "vp",
            (
                ToolComponent("vite", "x2"),
                ToolComponent("vitest", "y"),
                ToolComponent("rolldown", "z"),
            ),
        )
        self.assertTrue(same_surface_different_toolchain(old, new))

    def test_component_order_does_not_change_semantic_receipt(self):
        a = ToolchainReceipt(
            "vp",
            (ToolComponent("vite", "x"), ToolComponent("vitest", "y")),
        )
        b = ToolchainReceipt(
            "vp",
            (ToolComponent("vitest", "y"), ToolComponent("vite", "x")),
        )
        self.assertEqual(a.semantic_sha256(), b.semantic_sha256())


if __name__ == "__main__":
    unittest.main()
