from __future__ import annotations
import unittest

from finite_tool_surface_lab.cf_capability_discovery import (
    CommandHit, classify_cli_effect, compact_discovery_projection, validate_anonymous_query
)


HITS=(
    CommandHit("cf zones list","List Zones"),
    CommandHit("cf zones get","Get Zone"),
    CommandHit("cf zones create","Create Zone"),
    CommandHit("cf zones delete","Delete Zone"),
    CommandHit("cf dns records list","List DNS Records"),
    CommandHit("cf accounts list","List Accounts"),
)


class CfDiscoveryTests(unittest.TestCase):
    def test_top_five_projection_is_tiny_vs_frozen_cloudflare_metadata(self):
        row=compact_discovery_projection(
            query="list zones",
            ranked_hits=HITS,
            commands_metadata_bytes=5_261_155,
            schema_metadata_bytes=2_826_987,
        )
        self.assertEqual(row["result_count"],5)
        self.assertLess(row["surface_fraction"],0.001)
        self.assertGreater(row["surface_reduction_ratio"],1000)
        self.assertEqual(set(row["results"][0]),{"command","summary"})
        self.assertEqual(row["next_step"],"EXACT_SCHEMA")
        self.assertEqual(row["execution_authority"],"NONE")

    def test_queries_with_email_domain_url_or_long_id_fail_closed(self):
        for q in (
            "delete zone user@example.com",
            "list example.com zones",
            "inspect https://example.com",
            "delete token 0123456789abcdef0123456789abcdef",
        ):
            with self.subTest(q=q):
                with self.assertRaisesRegex(ValueError,"identity_or_locator"):
                    validate_anonymous_query(q)

    def test_zero_exit_with_abort_is_no_effect(self):
        row=classify_cli_effect(
            returncode=0,mutation_expected=True,semantic_receipt=None,stderr="Aborted.\n"
        )
        self.assertEqual(row["status"],"NO_EFFECT")
        self.assertFalse(row["returncode_is_effect_proof"])

    def test_zero_exit_mutation_without_receipt_is_unknown(self):
        row=classify_cli_effect(
            returncode=0,mutation_expected=True,semantic_receipt=None,stderr=""
        )
        self.assertEqual(row["status"],"UNKNOWN")

    def test_applied_requires_semantic_receipt(self):
        row=classify_cli_effect(
            returncode=0,mutation_expected=True,semantic_receipt="APPLIED"
        )
        self.assertEqual(row["status"],"APPLIED")


if __name__=="__main__":
    unittest.main()
