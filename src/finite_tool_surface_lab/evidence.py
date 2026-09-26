from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from pathlib import Path

from .synthetic import canonical_json_bytes


def write_val001_evidence(
    *,
    out_dir: str | Path,
    spec: dict,
    result: dict,
    source_commit: str | None = None,
) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    spec_bytes = canonical_json_bytes(spec)

    manifest = {
        "schema_version": "ftsl-evidence-manifest-v0.1",
        "study_id": "VAL-001",
        "source_commit": source_commit
        or os.environ.get("GITHUB_SHA", "UNKNOWN"),
        "spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "mode": result["mode"],
        "seed": result["seed"],
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    metrics = {
        key: value
        for key, value in result.items()
        if key not in {"calibration_cases", "cell_digests"}
    }
    (out / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with (out / "random_calibration.jsonl").open(
        "w", encoding="utf-8"
    ) as handle:
        for row in result["calibration_cases"]:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    with (out / "cell_digests.jsonl").open(
        "w", encoding="utf-8"
    ) as handle:
        for row in result["cell_digests"]:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
