from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from finite_tool_surface_lab import ExperimentState, SpecError, load_spec


ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def test_frozen_specs_load(self) -> None:
        for name in ("VAL-001.json", "BENCH-001.json"):
            spec = load_spec(ROOT / "specs" / name)
            self.assertEqual(spec["status"], "FROZEN")

    def test_unknown_spec_field_fails_closed(self) -> None:
        source = json.loads(
            (ROOT / "specs" / "VAL-001.json").read_text()
        )
        source["surprise"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps(source), encoding="utf-8")
            with self.assertRaisesRegex(SpecError, "UNKNOWN_FIELDS"):
                load_spec(path)

    def test_lane_id_mismatch_fails_closed(self) -> None:
        source = json.loads(
            (ROOT / "specs" / "VAL-001.json").read_text()
        )
        source["lane"] = "BENCH"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps(source), encoding="utf-8")
            with self.assertRaisesRegex(SpecError, "LANE_ID_MISMATCH"):
                load_spec(path)

    def test_result_state_vocabulary_is_exact(self) -> None:
        self.assertEqual(
            {state.value for state in ExperimentState},
            {"PASS", "FAIL", "INVALID", "ERROR"},
        )


if __name__ == "__main__":
    unittest.main()
