from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

_SCHEMA = "ftsl-experiment-v0.1"
_ALLOWED_FIELDS = {
    "schema_version", "id", "lane", "status", "question",
    "seed", "parameters", "acceptance", "claim_ceiling",
}
_LANES = {"VAL", "BENCH"}
_STATUSES = {"CANDIDATE", "FROZEN"}
_ID = re.compile(r"^(VAL|BENCH)-[0-9]{3}$")


class SpecError(ValueError):
    pass


def load_spec(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SpecError("SPEC_NOT_OBJECT")

    extra = set(payload) - _ALLOWED_FIELDS
    missing = _ALLOWED_FIELDS - set(payload)
    if extra:
        raise SpecError("UNKNOWN_FIELDS:" + ",".join(sorted(extra)))
    if missing:
        raise SpecError("MISSING_FIELDS:" + ",".join(sorted(missing)))

    if payload["schema_version"] != _SCHEMA:
        raise SpecError("UNSUPPORTED_SCHEMA_VERSION")

    experiment_id = payload["id"]
    match = _ID.fullmatch(experiment_id) if isinstance(experiment_id, str) else None
    if match is None:
        raise SpecError("INVALID_ID")

    lane = payload["lane"]
    if lane not in _LANES:
        raise SpecError("INVALID_LANE")
    if match.group(1) != lane:
        raise SpecError("LANE_ID_MISMATCH")

    if payload["status"] not in _STATUSES:
        raise SpecError("INVALID_STATUS")

    if not isinstance(payload["seed"], int) or isinstance(payload["seed"], bool) or payload["seed"] < 0:
        raise SpecError("INVALID_SEED")

    for key in ("question", "claim_ceiling"):
        if not isinstance(payload[key], str) or not payload[key].strip():
            raise SpecError("INVALID_" + key.upper())

    for key in ("parameters", "acceptance"):
        if not isinstance(payload[key], dict):
            raise SpecError("INVALID_" + key.upper())

    return payload
