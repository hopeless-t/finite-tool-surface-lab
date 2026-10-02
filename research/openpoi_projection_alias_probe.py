#!/usr/bin/env python3
"""Show that response-level provenance union cannot recover record assignment.

Research-only deterministic fixture. No OpenPOI network request is performed.
"""

from __future__ import annotations

import json


def full_projection(records: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "id": record["id"],
            "licenses": sorted(record["licenses"]),
            "attributions": sorted(record["attributions"]),
        }
        for record in sorted(records, key=lambda row: str(row["id"]))
    ]


def minimal_projection(records: list[dict[str, object]]) -> dict[str, list[str]]:
    licenses: set[str] = set()
    attributions: set[str] = set()
    for record in records:
        licenses.update(record["licenses"])
        attributions.update(record["attributions"])
    return {
        "licenses": sorted(licenses),
        "attributions": sorted(attributions),
    }


def main() -> None:
    a = [
        {"id": "poi-1", "licenses": {"L1"}, "attributions": {"A1"}},
        {"id": "poi-2", "licenses": {"L2"}, "attributions": {"A2"}},
    ]
    b = [
        {"id": "poi-1", "licenses": {"L2"}, "attributions": {"A2"}},
        {"id": "poi-2", "licenses": {"L1"}, "attributions": {"A1"}},
    ]

    full_a = full_projection(a)
    full_b = full_projection(b)
    min_a = minimal_projection(a)
    min_b = minimal_projection(b)

    assert full_a != full_b
    assert min_a == min_b

    print(
        json.dumps(
            {
                "schema": "finite-tool-surface-lab.provenance-alias/v0.1",
                "network_calls": 0,
                "full_projection_distinguishes": True,
                "minimal_projection_aliases": True,
                "minimal_projection": min_a,
                "status": "OPENPOI_PROVENANCE_ALIAS=PASS",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
