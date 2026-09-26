from __future__ import annotations

import argparse
import json

from .evidence import write_val001_evidence
from .spec import SpecError, load_spec
from .validation import run_validation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default="specs/VAL-001.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    try:
        spec = load_spec(args.spec)
        result = run_validation(spec, quick=args.quick)
    except (SpecError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {
                    "study_id": "VAL-001",
                    "state": "INVALID",
                    "reason": str(exc),
                },
                sort_keys=True,
            )
        )
        raise SystemExit(2)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "study_id": "VAL-001",
                    "state": "ERROR",
                    "reason": repr(exc),
                },
                sort_keys=True,
            )
        )
        raise SystemExit(3)

    write_val001_evidence(
        out_dir=args.out,
        spec=spec,
        result=result,
    )
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "study_id",
                    "mode",
                    "state",
                    "cells",
                    "tasks",
                    "max_random_theory_abs_error",
                )
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if result["state"] == "PASS" else 1)


if __name__ == "__main__":
    main()
