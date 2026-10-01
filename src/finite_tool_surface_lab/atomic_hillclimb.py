from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EvalPoint:
    train_score: float
    test_score: float
    noise_floor: float
    cost: float | None = None

    def validate(self) -> None:
        for name, value in (
            ("train_score", self.train_score),
            ("test_score", self.test_score),
            ("noise_floor", self.noise_floor),
        ):
            if type(value) not in (int, float):
                raise ValueError(name + "_invalid")
        if not 0.0 <= float(self.train_score) <= 1.0:
            raise ValueError("train_score_invalid")
        if not 0.0 <= float(self.test_score) <= 1.0:
            raise ValueError("test_score_invalid")
        if not 0.0 <= float(self.noise_floor) <= 1.0:
            raise ValueError("noise_floor_invalid")
        if self.cost is not None and (type(self.cost) not in (int, float) or float(self.cost) < 0):
            raise ValueError("cost_invalid")


def evaluate_atomic_patch(
    *,
    mutation_id: str,
    baseline: EvalPoint,
    candidate: EvalPoint,
    objective: str = "QUALITY",
    minimum_test_score: float | None = None,
) -> dict[str, Any]:
    if not isinstance(mutation_id, str) or not mutation_id or len(mutation_id) > 128:
        raise ValueError("mutation_id_invalid")
    baseline.validate()
    candidate.validate()
    if objective not in {"QUALITY", "COST_WITH_QUALITY_FLOOR"}:
        raise ValueError("objective_invalid")

    noise=max(float(baseline.noise_floor), float(candidate.noise_floor))
    train_delta=float(candidate.train_score)-float(baseline.train_score)
    test_delta=float(candidate.test_score)-float(baseline.test_score)

    if minimum_test_score is not None and float(candidate.test_score) < float(minimum_test_score):
        status,reason="REVERT","test_quality_floor_failed"
    elif train_delta > noise and test_delta <= noise:
        status,reason="REVERT","train_only_gain_overfit_suspected"
    elif test_delta < -noise:
        status,reason="REVERT","heldout_regression"
    elif objective=="QUALITY":
        if test_delta > noise:
            status,reason="KEEP","heldout_gain_exceeds_noise"
        else:
            status,reason="HOLD","heldout_gain_within_noise"
    else:
        if baseline.cost is None or candidate.cost is None:
            raise ValueError("cost_required")
        quality_floor = (
            float(minimum_test_score)
            if minimum_test_score is not None
            else float(baseline.test_score)-noise
        )
        if float(candidate.test_score) < quality_floor:
            status,reason="REVERT","quality_not_preserved"
        elif float(candidate.cost) < float(baseline.cost):
            status,reason="KEEP","cost_reduced_quality_preserved"
        elif float(candidate.cost) > float(baseline.cost):
            status,reason="REVERT","cost_regressed"
        else:
            status,reason="HOLD","no_measurable_cost_gain"

    return {
        "schema":"ftsl.atomic-hillclimb-decision/v0.1",
        "mutation_id":mutation_id,
        "objective":objective,
        "status":status,
        "reason":reason,
        "train_delta":train_delta,
        "test_delta":test_delta,
        "noise_floor":noise,
        "single_mutation_required":True,
        "heldout_required":True,
        "authority_effect":"NONE",
    }
