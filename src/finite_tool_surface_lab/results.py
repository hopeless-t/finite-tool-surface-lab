from __future__ import annotations

from enum import Enum


class ExperimentState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INVALID = "INVALID"
    ERROR = "ERROR"
