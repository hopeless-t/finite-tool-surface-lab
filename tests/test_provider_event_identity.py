from __future__ import annotations

import unittest

from finite_tool_surface_lab.provider_event_identity import (
    ProviderEventIdentity,
    RawProviderEvent,
    canonical_projection,
    provider_identity_alias_risk,
)


class ProviderEventIdentityTests(unittest.TestCase):
    def test_provider_namespace_prevents_native_id_collision(self):
        codex = ProviderEventIdentity("mvca-s1", "codex", "42", "evt-7")
        claude = ProviderEventIdentity("mvca-s2", "claude", "42", "evt-7")

        self.assertEqual(codex.naive_native_key(), claude.naive_native_key())
        self.assertNotEqual(codex.canonical_coordinate(), claude.canonical_coordinate())
        self.assertTrue(provider_identity_alias_risk(codex, claude))

    def test_projection_preserves_raw_provider_identity(self):
        ident = ProviderEventIdentity("mvca-s1", "codex", "thread-a", "evt-9")
        raw = RawProviderEvent(ident, "tool_result", {"status": "UNKNOWN"})
        projected = canonical_projection(raw)

        self.assertEqual(projected["canonical_session_id"], "mvca-s1")
        self.assertEqual(projected["provider"], "codex")
        self.assertEqual(projected["provider_session_id"], "thread-a")
        self.assertEqual(projected["provider_event_id"], "evt-9")
        self.assertEqual(projected["payload"], {"status": "UNKNOWN"})


if __name__ == "__main__":
    unittest.main()
