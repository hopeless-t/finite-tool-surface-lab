from __future__ import annotations

import hashlib
import random
from typing import Any

from .synthetic import canonical_json_bytes

GENERATOR_VERSION = "ftsl-admission-v0.1"

TRUTH_BY_FAMILY = {
    "EXTERNAL_STATE_REQUIRED": "ADMIT_TOOL_SURFACE",
    "SIDE_EFFECT_REQUIRED": "ADMIT_TOOL_SURFACE",
    "SPECIALIZED_COMPUTE_REQUIRED": "ADMIT_TOOL_SURFACE",
    "LOCAL_CONTEXT_SUFFICIENT": "NO_TOOL_SURFACE",
    "IRRELEVANT_TOOL_MENU": "NO_TOOL_SURFACE",
    "PREMATURE_TOOL": "NO_TOOL_SURFACE",
    "USER_FORBIDS_TOOL": "NO_TOOL_SURFACE",
    "MISSING_REQUIRED_INPUT": "DEFER",
    "AMBIGUOUS_INTENT": "DEFER",
}

PAIR_GROUP = {
    "EXTERNAL_STATE_REQUIRED": "PAIR_EXTERNAL_CONTEXT",
    "LOCAL_CONTEXT_SUFFICIENT": "PAIR_EXTERNAL_CONTEXT",
    "SIDE_EFFECT_REQUIRED": "PAIR_SIDE_EFFECT_PERMISSION",
    "USER_FORBIDS_TOOL": "PAIR_SIDE_EFFECT_PERMISSION",
    "SPECIALIZED_COMPUTE_REQUIRED": "PAIR_COMPUTE_READINESS",
    "PREMATURE_TOOL": "PAIR_COMPUTE_READINESS",
}

FEATURES = (
    "external_state_dependency",
    "side_effect_intent",
    "local_context_sufficiency",
    "precondition_readiness",
    "user_tool_permission",
    "intent_clarity",
    "menu_relevance",
)

BASE_FEATURES: dict[str, dict[str, float]] = {
    "EXTERNAL_STATE_REQUIRED": {
        "external_state_dependency": 1.0,
        "side_effect_intent": 0.0,
        "local_context_sufficiency": 0.0,
        "precondition_readiness": 1.0,
        "user_tool_permission": 1.0,
        "intent_clarity": 1.0,
        "menu_relevance": 1.0,
    },
    "LOCAL_CONTEXT_SUFFICIENT": {
        "external_state_dependency": 0.0,
        "side_effect_intent": 0.0,
        "local_context_sufficiency": 1.0,
        "precondition_readiness": 1.0,
        "user_tool_permission": 1.0,
        "intent_clarity": 1.0,
        "menu_relevance": 1.0,
    },
    "SIDE_EFFECT_REQUIRED": {
        "external_state_dependency": 0.0,
        "side_effect_intent": 1.0,
        "local_context_sufficiency": 0.0,
        "precondition_readiness": 1.0,
        "user_tool_permission": 1.0,
        "intent_clarity": 1.0,
        "menu_relevance": 1.0,
    },
    "USER_FORBIDS_TOOL": {
        "external_state_dependency": 0.0,
        "side_effect_intent": 1.0,
        "local_context_sufficiency": 0.0,
        "precondition_readiness": 1.0,
        "user_tool_permission": 0.0,
        "intent_clarity": 1.0,
        "menu_relevance": 1.0,
    },
    "SPECIALIZED_COMPUTE_REQUIRED": {
        "external_state_dependency": 0.2,
        "side_effect_intent": 0.0,
        "local_context_sufficiency": 0.0,
        "precondition_readiness": 1.0,
        "user_tool_permission": 1.0,
        "intent_clarity": 1.0,
        "menu_relevance": 1.0,
    },
    "PREMATURE_TOOL": {
        "external_state_dependency": 0.2,
        "side_effect_intent": 0.0,
        "local_context_sufficiency": 0.0,
        "precondition_readiness": 0.0,
        "user_tool_permission": 1.0,
        "intent_clarity": 1.0,
        "menu_relevance": 1.0,
    },
    "IRRELEVANT_TOOL_MENU": {
        "external_state_dependency": 0.0,
        "side_effect_intent": 0.0,
        "local_context_sufficiency": 0.3,
        "precondition_readiness": 1.0,
        "user_tool_permission": 1.0,
        "intent_clarity": 1.0,
        "menu_relevance": 0.0,
    },
    "MISSING_REQUIRED_INPUT": {
        "external_state_dependency": 0.5,
        "side_effect_intent": 0.2,
        "local_context_sufficiency": 0.2,
        "precondition_readiness": 0.3,
        "user_tool_permission": 1.0,
        "intent_clarity": 0.2,
        "menu_relevance": 0.8,
    },
    "AMBIGUOUS_INTENT": {
        "external_state_dependency": 0.5,
        "side_effect_intent": 0.5,
        "local_context_sufficiency": 0.5,
        "precondition_readiness": 0.7,
        "user_tool_permission": 1.0,
        "intent_clarity": 0.0,
        "menu_relevance": 0.8,
    },
}


def _stable_int(*parts: object) -> int:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def _pair_key(
    *,
    seed: int,
    n: int,
    family: str,
    ambiguity: float,
    plausibility: str,
    repeat: int,
) -> str:
    group = PAIR_GROUP.get(family, family)
    return (
        f"{seed}|{n}|{group}|{ambiguity:.2f}|{plausibility}|{repeat}"
    )


def _make_registry_and_query(
    *,
    key: str,
    n: int,
    plausibility: str,
    family: str,
) -> tuple[dict[str, Any], list[str]]:
    base = _stable_int(key, "registry") % 10_000_000
    operation = f"operation_{base}"
    domain = f"domain_{base}"
    core = [
        operation,
        domain,
        f"semantic_{base}_0",
        f"semantic_{base}_1",
        f"schema_{base}_0",
        f"intent_{base}",
    ]
    query = list(core)

    tools: list[dict[str, Any]] = []
    if family == "IRRELEVANT_TOOL_MENU":
        lead_tokens = [f"irrelevant_{base}_{i}" for i in range(6)]
    else:
        lead_tokens = list(core)
        if plausibility == "LOW":
            lead_tokens = core[:2] + [f"weak_{base}_{i}" for i in range(4)]

    for index in range(n):
        tool_id = f"TOOL-{index:05d}"
        if index == 0:
            tokens = lead_tokens
        elif index < 4 and plausibility == "HIGH":
            tokens = [
                operation,
                domain,
                f"semantic_{base}_{index}",
                f"schema_{base}_{index}",
                f"distractor_{base}_{index}",
            ]
        else:
            serial = _stable_int(key, index, "bg") % 1_000_000_000
            tokens = [f"bg_{serial}_{i}" for i in range(6)]
        tools.append(
            {
                "tool_id": tool_id,
                "description_tokens": tokens,
                "aliases": [],
                "serialized_stub": {
                    "name": tool_id,
                    "description": " ".join(tokens),
                    "operation": operation if index < 4 else f"bgop_{index}",
                    "domain": domain if index < 4 else f"bgdomain_{index}",
                },
            }
        )

    return {
        "schema_version": "ftsl-admission-registry-v0.1",
        "generator_version": GENERATOR_VERSION,
        "n": n,
        "tools": tools,
    }, query


def _noisy_features(
    *,
    family: str,
    ambiguity: float,
    seed_parts: tuple[object, ...],
) -> dict[str, float]:
    base = BASE_FEATURES[family]
    rng = random.Random(_stable_int(*seed_parts, "features"))
    out: dict[str, float] = {}
    for name in FEATURES:
        raw = float(base[name])
        mixed = (1.0 - ambiguity) * raw + ambiguity * 0.5
        jitter = (rng.random() - 0.5) * 0.12 * ambiguity
        out[name] = round(min(1.0, max(0.0, mixed + jitter)), 6)
    return out


def generate_admission_case(
    *,
    n: int,
    family: str,
    ambiguity: float,
    plausibility: str,
    repeat: int,
    seed: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if family not in TRUTH_BY_FAMILY:
        raise ValueError("UNKNOWN_TRUTH_FAMILY")
    if plausibility not in {"LOW", "HIGH"}:
        raise ValueError("UNKNOWN_PLAUSIBILITY")
    if not 0.0 <= ambiguity <= 1.0:
        raise ValueError("AMBIGUITY_RANGE")

    key = _pair_key(
        seed=seed,
        n=n,
        family=family,
        ambiguity=ambiguity,
        plausibility=plausibility,
        repeat=repeat,
    )
    registry, query_tokens = _make_registry_and_query(
        key=key,
        n=n,
        plausibility=plausibility,
        family=family,
    )

    gate_input = _noisy_features(
        family=family,
        ambiguity=ambiguity,
        seed_parts=(seed, n, family, ambiguity, plausibility, repeat),
    )

    task = {
        "task_id": (
            f"S{seed}-N{n}-{family}-A{ambiguity:.2f}-"
            f"{plausibility}-R{repeat:03d}"
        ),
        "truth_family": family,
        "truth": TRUTH_BY_FAMILY[family],
        "query_tokens": query_tokens,
        "gate_input": gate_input,
        "ambiguity": ambiguity,
        "candidate_plausibility": plausibility,
        "pair_group": PAIR_GROUP.get(family),
        "required_tool_ids": ["TOOL-00000"]
        if TRUTH_BY_FAMILY[family] == "ADMIT_TOOL_SURFACE"
        else [],
    }
    return registry, task


def validate_case(
    registry: dict[str, Any],
    task: dict[str, Any],
) -> dict[str, bool]:
    gate_input = task["gate_input"]
    truth_hidden = (
        "truth" not in gate_input
        and "truth_family" not in gate_input
        and set(gate_input) == set(FEATURES)
    )
    return {
        "truth_label_recomputable": (
            TRUTH_BY_FAMILY[task["truth_family"]] == task["truth"]
        ),
        "truth_not_present_in_gate_input": truth_hidden,
        "gate_cannot_grant_execution_authority": (
            "authority" not in gate_input
            and "execute" not in gate_input
            and "permission_grant" not in gate_input
        ),
    }


def retrieval_fingerprint(
    registry: dict[str, Any],
    task: dict[str, Any],
) -> str:
    payload = {
        "registry": registry,
        "query_tokens": task["query_tokens"],
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
