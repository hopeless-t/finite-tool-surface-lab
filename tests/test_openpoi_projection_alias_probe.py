from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class OpenPoiProjectionAliasProbeTests(unittest.TestCase):
    def test_minimal_union_aliases_distinct_record_provenance(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "research" / "openpoi_projection_alias_probe.py")],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OPENPOI_PROVENANCE_ALIAS=PASS", result.stdout)
        self.assertIn('"minimal_projection_aliases":true', result.stdout)
        self.assertIn('"full_projection_distinguishes":true', result.stdout)


if __name__ == "__main__":
    unittest.main()
