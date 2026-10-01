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


def evaluate_prompt_candidate_guard(
    *,
    baseline_text: str,
    candidate_text: str,
    safety_check_passed: bool,
    trace_phrases: tuple[str, ...] = (),
    max_growth_ratio: float = 0.20,
) -> dict[str, Any]:
    """Deterministic pre-eval guard inspired by AgentCore prompt optimization.

    This is not a semantic safety evaluator. It only freezes three cheap gates:
    bounded prompt growth, an externally supplied safety result, and exact
    trace-phrase reuse rejection.
    """
    if not isinstance(baseline_text, str) or not baseline_text:
        raise ValueError("baseline_text_invalid")
    if not isinstance(candidate_text, str) or not candidate_text:
        raise ValueError("candidate_text_invalid")
    if type(safety_check_passed) is not bool:
        raise ValueError("safety_check_passed_invalid")
    if type(max_growth_ratio) not in (int, float) or not 0.0 <= float(max_growth_ratio) <= 1.0:
        raise ValueError("max_growth_ratio_invalid")
    if (
        not isinstance(trace_phrases, tuple)
        or any(not isinstance(item, str) or not item for item in trace_phrases)
    ):
        raise ValueError("trace_phrases_invalid")

    growth_ratio=(len(candidate_text)-len(baseline_text))/max(1,len(baseline_text))
    reused=tuple(sorted({phrase for phrase in trace_phrases if phrase in candidate_text}))

    if growth_ratio > float(max_growth_ratio):
        status,reason="REJECT","prompt_growth_ceiling_exceeded"
    elif not safety_check_passed:
        status,reason="REJECT","external_safety_check_failed"
    elif reused:
        status,reason="REJECT","trace_phrase_reuse_detected"
    else:
        status,reason="PASS","cheap_prompt_guards_passed"

    return {
        "schema":"ftsl.prompt-candidate-guard/v0.1",
        "status":status,
        "reason":reason,
        "growth_ratio":growth_ratio,
        "max_growth_ratio":float(max_growth_ratio),
        "reused_trace_phrases":list(reused),
        "semantic_safety_claim":False,
        "authority_effect":"NONE",
    }
