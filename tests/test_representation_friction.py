from __future__ import annotations

import unittest

from finite_tool_surface_lab.representation_friction import (
    Fact, representation_record, render_markdown, parse_markdown, semantic_sha256
)


FACTS=[
    Fact("status","UNKNOWN|HOLD","receipt:a"),
    Fact("authority","NONE","receipt:b"),
    Fact("next_action","readback before retry","receipt:c"),
]


class RepresentationFrictionTests(unittest.TestCase):
    def test_all_formats_preserve_exact_semantics(self):
        rows=representation_record(FACTS)
        digest=semantic_sha256(FACTS)
        for row in rows.values():
            self.assertTrue(row["semantic_preserved"])
            self.assertEqual(row["semantic_sha256"],digest)
            self.assertEqual(row["authority_effect"],"NONE")

    def test_formats_have_different_surface_costs(self):
        rows=representation_record(FACTS)
        sizes={name:int(row["bytes"]) for name,row in rows.items()}
        self.assertGreater(len(set(sizes.values())),1)

    def test_markdown_pipe_escape_roundtrips(self):
        text=render_markdown(FACTS)
        parsed=parse_markdown(text)
        self.assertEqual(parsed,sorted(FACTS))


if __name__=="__main__":
    unittest.main()
