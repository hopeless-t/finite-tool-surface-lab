from __future__ import annotations

import json
from pathlib import Path

import pytest

from finite_tool_surface_lab import ExperimentState, SpecError, load_spec

ROOT = Path(__file__).resolve().parents[1]


def test_frozen_specs_load() -> None:
    for name in ("VAL-001.json", "BENCH-001.json"):
        spec = load_spec(ROOT / "specs" / name)
        assert spec["status"] == "FROZEN"


def test_unknown_spec_field_fails_closed(tmp_path: Path) -> None:
    source = json.loads((ROOT / "specs" / "VAL-001.json").read_text())
    source["surprise"] = True
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(source), encoding="utf-8")
    with pytest.raises(SpecError, match="UNKNOWN_FIELDS"):
        load_spec(path)


def test_lane_id_mismatch_fails_closed(tmp_path: Path) -> None:
    source = json.loads((ROOT / "specs" / "VAL-001.json").read_text())
    source["lane"] = "BENCH"
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(source), encoding="utf-8")
    with pytest.raises(SpecError, match="LANE_ID_MISMATCH"):
        load_spec(path)


def test_result_state_vocabulary_is_exact() -> None:
    assert {state.value for state in ExperimentState} == {"PASS", "FAIL", "INVALID", "ERROR"}
