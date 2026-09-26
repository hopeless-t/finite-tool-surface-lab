from __future__ import annotations

import hashlib
import random
from typing import Any

GENERATOR_VERSION = "ftsl-distractor-v0.1"
TASK_REQUIRED = {"single_tool": 1, "multi_tool": 2, "no_tool": 0}

STRESS_FAMILIES = {
    "RANDOM_IRRELEVANT",
    "SEMANTIC_NEAR",
    "SCHEMA_COMPATIBLE",
    "PREMATURE_STATE",
    "RISKY_RELEVANT",
    "CROSS_DOMAIN_HOMONYM",
    "VALID_EQUIVALENT",
    "MIXED",
}

_MIXED = (
    "SEMANTIC_NEAR",
    "SCHEMA_COMPATIBLE",
    "PREMATURE_STATE",
    "RISKY_RELEVANT",
    "CROSS_DOMAIN_HOMONYM",
    "VALID_EQUIVALENT",
)


def _stable_int(*parts: object) -> int:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def _profile(case_key: str, slot: int) -> dict[str, Any]:
    base = _stable_int(case_key, slot, "profile") % 10_000_000
    domain = f"domain_{base}"
    operation = f"operation_{base}"
    semantic = [f"semantic_{base}_{i}" for i in range(4)]
    schema = [f"schema_{base}_{i}" for i in range(3)]
    state = f"state_ready_{base}"
    intent = f"intent_{base}"
    signature = f"cap_signature_{base}"
    query_tokens = [
        domain,
        operation,
        *semantic,
        *schema,
        state,
        intent,
        signature,
    ]
    return {
        "capability_id": f"CAP-{base}",
        "domain": domain,
        "operation": operation,
        "semantic": semantic,
        "schema": schema,
        "state": state,
        "intent": intent,
        "signature": signature,
        "query_tokens": query_tokens,
    }


def _tool(
    *,
    tool_id: str,
    tokens: list[str],
    role: str,
    capability_id: str | None,
    family: str,
    targeted: bool,
    semantic_proximity: str,
    schema_overlap: str,
    state_validity: str,
    risk_level: str,
    domain_relation: str,
    operation: str,
    domain: str,
) -> dict[str, Any]:
    return {
        "tool_id": tool_id,
        "description_tokens": list(tokens),
        "aliases": [],
        "role": role,
        "capability_id": capability_id,
        "distractor_family": family,
        "targeted": targeted,
        "semantic_proximity": semantic_proximity,
        "schema_overlap": schema_overlap,
        "state_validity": state_validity,
        "risk_level": risk_level,
        "domain_relation": domain_relation,
        "operation": operation,
        "domain": domain,
        "serialized_stub": {
            "name": tool_id,
            "description": " ".join(tokens),
            "operation": operation,
            "domain": domain,
            "risk": risk_level,
            "state_validity": state_validity,
        },
    }


def _wrong_tokens(
    profile: dict[str, Any],
    family: str,
    serial: int,
) -> tuple[list[str], dict[str, str]]:
    q = list(profile["query_tokens"])
    if family == "RANDOM_IRRELEVANT":
        tokens = [f"background_{serial}_{i}" for i in range(6)]
        labels = {
            "semantic_proximity": "far",
            "schema_overlap": "low",
            "state_validity": "valid_now",
            "risk_level": "low",
            "domain_relation": "cross_domain",
        }
    elif family == "SEMANTIC_NEAR":
        tokens = [
            profile["domain"],
            profile["operation"],
            *profile["semantic"],
            profile["schema"][0],
            profile["state"],
            profile["intent"],
        ]
        labels = {
            "semantic_proximity": "near",
            "schema_overlap": "low",
            "state_validity": "valid_now",
            "risk_level": "low",
            "domain_relation": "same_domain",
        }
    elif family == "SCHEMA_COMPATIBLE":
        tokens = [
            *profile["schema"],
            profile["state"],
            profile["intent"],
        ]
        labels = {
            "semantic_proximity": "far",
            "schema_overlap": "high",
            "state_validity": "valid_now",
            "risk_level": "low",
            "domain_relation": "same_domain",
        }
    elif family == "PREMATURE_STATE":
        tokens = [
            token
            for token in q
            if token not in {profile["signature"], profile["state"]}
        ] + [f"state_future_{serial}"]
        labels = {
            "semantic_proximity": "near",
            "schema_overlap": "high",
            "state_validity": "premature",
            "risk_level": "low",
            "domain_relation": "same_domain",
        }
    elif family == "RISKY_RELEVANT":
        tokens = [token for token in q if token != profile["signature"]]
        labels = {
            "semantic_proximity": "near",
            "schema_overlap": "high",
            "state_validity": "valid_now",
            "risk_level": "high",
            "domain_relation": "same_domain",
        }
    elif family == "CROSS_DOMAIN_HOMONYM":
        tokens = [
            profile["operation"],
            *profile["schema"],
            profile["intent"],
            profile["semantic"][0],
            f"other_domain_{serial}",
        ]
        labels = {
            "semantic_proximity": "near",
            "schema_overlap": "high",
            "state_validity": "valid_now",
            "risk_level": "low",
            "domain_relation": "cross_domain",
        }
    else:
        raise ValueError("UNSUPPORTED_WRONG_FAMILY")
    return tokens, labels


def generate_distractor_case(
    *,
    n: int,
    task_type: str,
    stress_family: str,
    density: int,
    repeat: int,
    seed: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if n < 4:
        raise ValueError("REGISTRY_TOO_SMALL")
    if task_type not in TASK_REQUIRED:
        raise ValueError("UNSUPPORTED_TASK_TYPE")
    if stress_family not in STRESS_FAMILIES:
        raise ValueError("UNSUPPORTED_STRESS_FAMILY")
    if density < 0:
        raise ValueError("NEGATIVE_DENSITY")

    required_count = TASK_REQUIRED[task_type]
    case_key = (
        f"{seed}|{n}|{task_type}|{stress_family}|{density}|{repeat}"
    )
    reference_count = max(1, required_count)
    profiles = [_profile(case_key, slot) for slot in range(reference_count)]

    required_profiles = profiles[:required_count]
    required_capabilities = [
        profile["capability_id"] for profile in required_profiles
    ]
    query_tokens: list[str] = []
    for profile in (required_profiles or profiles[:1]):
        query_tokens.extend(profile["query_tokens"])

    tools: list[dict[str, Any]] = []
    valid_by_capability: dict[str, list[str]] = {
        cap: [] for cap in required_capabilities
    }
    canonical_by_capability: dict[str, str] = {}
    counter = 0

    def next_id() -> str:
        nonlocal counter
        tool_id = f"TOOL-{counter:05d}"
        counter += 1
        return tool_id

    for profile in required_profiles:
        tool_id = next_id()
        tools.append(
            _tool(
                tool_id=tool_id,
                tokens=profile["query_tokens"],
                role="canonical",
                capability_id=profile["capability_id"],
                family="CANONICAL",
                targeted=False,
                semantic_proximity="near",
                schema_overlap="high",
                state_validity="valid_now",
                risk_level="low",
                domain_relation="same_domain",
                operation=profile["operation"],
                domain=profile["domain"],
            )
        )
        valid_by_capability[profile["capability_id"]].append(tool_id)
        canonical_by_capability[profile["capability_id"]] = tool_id

    targeted_wrong_ids: list[str] = []
    premature_wrong_ids: list[str] = []
    risky_wrong_ids: list[str] = []
    valid_equivalent_ids: list[str] = []

    for slot, profile in enumerate(profiles):
        if required_count == 0 and stress_family == "VALID_EQUIVALENT":
            continue
        for j in range(density):
            family = stress_family
            if family == "MIXED":
                choices = _MIXED if required_count else _MIXED[:-1]
                family = choices[(slot * density + j) % len(choices)]

            if family == "VALID_EQUIVALENT":
                tool_id = next_id()
                tools.append(
                    _tool(
                        tool_id=tool_id,
                        tokens=profile["query_tokens"],
                        role="valid_equivalent",
                        capability_id=profile["capability_id"],
                        family=family,
                        targeted=True,
                        semantic_proximity="near",
                        schema_overlap="high",
                        state_validity="valid_now",
                        risk_level="low",
                        domain_relation="same_domain",
                        operation=profile["operation"],
                        domain=profile["domain"],
                    )
                )
                valid_by_capability[profile["capability_id"]].append(tool_id)
                valid_equivalent_ids.append(tool_id)
                continue

            tool_id = next_id()
            serial = _stable_int(case_key, slot, j, family) % 10_000_000
            tokens, labels = _wrong_tokens(profile, family, serial)
            operation = (
                profile["operation"]
                if family != "RANDOM_IRRELEVANT"
                else f"background_operation_{serial}"
            )
            domain = (
                profile["domain"]
                if labels["domain_relation"] == "same_domain"
                else f"other_domain_{serial}"
            )
            tools.append(
                _tool(
                    tool_id=tool_id,
                    tokens=tokens,
                    role="wrong_distractor",
                    capability_id=None,
                    family=family,
                    targeted=True,
                    operation=operation,
                    domain=domain,
                    **labels,
                )
            )
            targeted_wrong_ids.append(tool_id)
            if labels["state_validity"] == "premature":
                premature_wrong_ids.append(tool_id)
            if labels["risk_level"] == "high":
                risky_wrong_ids.append(tool_id)

    if len(tools) > n:
        raise ValueError("TARGETED_TOOLS_EXCEED_REGISTRY")

    rng = random.Random(_stable_int(case_key, "background"))
    while len(tools) < n:
        serial = rng.randrange(1_000_000_000)
        tool_id = next_id()
        tokens = [f"bg_{serial}_{i}" for i in range(6)]
        tools.append(
            _tool(
                tool_id=tool_id,
                tokens=tokens,
                role="background",
                capability_id=None,
                family="RANDOM_IRRELEVANT",
                targeted=False,
                semantic_proximity="far",
                schema_overlap="low",
                state_validity="valid_now",
                risk_level="low",
                domain_relation="cross_domain",
                operation=f"bg_operation_{serial}",
                domain=f"bg_domain_{serial}",
            )
        )

    registry = {
        "schema_version": "ftsl-distractor-registry-v0.1",
        "generator_version": GENERATOR_VERSION,
        "n": n,
        "stress_family": stress_family,
        "density": density,
        "tools": tools,
    }
    task = {
        "task_id": (
            f"S{seed}-N{n}-{stress_family}-D{density}-"
            f"{task_type}-{repeat:03d}"
        ),
        "task_type": task_type,
        "query_tokens": query_tokens,
        "required_capabilities": required_capabilities,
        "valid_tool_ids_by_capability": {
            cap: sorted(ids) for cap, ids in valid_by_capability.items()
        },
        "canonical_tool_ids_by_capability": canonical_by_capability,
        "targeted_wrong_ids": sorted(targeted_wrong_ids),
        "premature_wrong_ids": sorted(premature_wrong_ids),
        "risky_wrong_ids": sorted(risky_wrong_ids),
        "valid_equivalent_ids": sorted(valid_equivalent_ids),
        "stress_family": stress_family,
        "density": density,
    }
    return registry, task


def validate_distractor_case(
    registry: dict[str, Any],
    task: dict[str, Any],
) -> dict[str, bool]:
    tools = registry["tools"]
    ids = [tool["tool_id"] for tool in tools]
    lookup = {tool["tool_id"]: tool for tool in tools}
    required = task["required_capabilities"]
    valid_map = task["valid_tool_ids_by_capability"]

    registry_size = len(tools) == registry["n"] and len(ids) == len(set(ids))

    identity_ok = True
    for cap in required:
        valid_ids = valid_map[cap]
        if not valid_ids:
            identity_ok = False
            continue
        signatures = {
            token
            for tool_id in valid_ids
            for token in lookup[tool_id]["description_tokens"]
            if token.startswith("cap_signature_")
        }
        if len(signatures) != 1:
            identity_ok = False
            continue
        signature = next(iter(signatures))
        if signature not in task["query_tokens"]:
            identity_ok = False
        for tool_id in task["targeted_wrong_ids"]:
            if signature in lookup[tool_id]["description_tokens"]:
                identity_ok = False

    equivalent_ids = set(task["valid_equivalent_ids"])
    wrong_ids = set(task["targeted_wrong_ids"])
    equivalent_not_wrong = not (equivalent_ids & wrong_ids)

    wrong_recomputed = {
        tool["tool_id"]
        for tool in tools
        if tool["targeted"] and tool["role"] == "wrong_distractor"
    }
    wrong_labels = wrong_recomputed == wrong_ids

    premature_recomputed = {
        tool["tool_id"]
        for tool in tools
        if tool["targeted"]
        and tool["role"] == "wrong_distractor"
        and tool["state_validity"] == "premature"
    }
    state_labels = premature_recomputed == set(task["premature_wrong_ids"])

    risky_recomputed = {
        tool["tool_id"]
        for tool in tools
        if tool["targeted"]
        and tool["role"] == "wrong_distractor"
        and tool["risk_level"] == "high"
    }
    risk_labels = risky_recomputed == set(task["risky_wrong_ids"])

    derived_groups: dict[str, set[str]] = {}
    for tool in tools:
        if tool["role"] in {"canonical", "valid_equivalent"}:
            cap = tool["capability_id"]
            if cap is not None:
                derived_groups.setdefault(cap, set()).add(tool["tool_id"])

    equivalence_ok = set(derived_groups) == set(required)
    if equivalence_ok:
        equivalence_ok = all(
            derived_groups[cap] == set(valid_map[cap]) for cap in required
        )
    seen: set[str] = set()
    for members in derived_groups.values():
        if seen & members:
            equivalence_ok = False
        seen |= members

    return {
        "registry_size_constant_within_matched_condition": registry_size,
        "gold_capability_identity_preserved": identity_ok,
        "valid_equivalent_not_counted_as_wrong": equivalent_not_wrong,
        "wrong_distractor_labels_recomputable": wrong_labels,
        "state_validity_labels_recomputable": state_labels,
        "risk_labels_recomputable": risk_labels,
        "equivalence_classes_symmetric_and_transitive": equivalence_ok,
    }
