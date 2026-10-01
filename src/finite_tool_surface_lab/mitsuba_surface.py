from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

SIDE_EFFECT_FREE = "READ_ONLY_SPECIALIST"

@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    required_keys: frozenset[str]
    description: str

    def serialized_bytes(self) -> int:
        payload = {
            "tool_id": self.tool_id,
            "required_keys": sorted(self.required_keys),
            "description": self.description,
        }
        return len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())


VISUAL_TOOLS = (
    ToolSpec(
        "mitsuba.visual.describe",
        frozenset({"image_ref", "instruction"}),
        "Describe bounded visual content; no mutation.",
    ),
    ToolSpec(
        "mitsuba.visual.compare",
        frozenset({"left_image_ref", "right_image_ref", "instruction"}),
        "Compare two bounded visual observations; no mutation.",
    ),
    ToolSpec(
        "mitsuba.visual.compile_prompt",
        frozenset({"brief", "constraints"}),
        "Compile a visual-generation prompt under explicit constraints.",
    ),
    ToolSpec(
        "mitsuba.visual.check_constraints",
        frozenset({"candidate", "constraints"}),
        "Check prompt-format constraints; advisory only.",
    ),
)

DISTRACTOR_TOOLS = (
    ToolSpec("shell.exec", frozenset({"command"}), "Execute an arbitrary shell command."),
    ToolSpec("git.push", frozenset({"remote", "ref"}), "Push a Git ref."),
    ToolSpec("github.merge_pr", frozenset({"pr"}), "Merge a pull request."),
    ToolSpec("filesystem.write", frozenset({"path", "content"}), "Write a file."),
    ToolSpec("http.fetch", frozenset({"url"}), "Fetch arbitrary remote content."),
    ToolSpec("code.run", frozenset({"language", "source"}), "Execute arbitrary code."),
)

SURFACES = {
    "VISUAL_NARROW_V0": VISUAL_TOOLS,
    "BROAD_AGENT_MENU_V0": VISUAL_TOOLS + DISTRACTOR_TOOLS,
    "NO_TOOL_V0": (),
}


def surface_bytes(surface_id: str) -> int:
    if surface_id not in SURFACES:
        raise ValueError("surface_unknown")
    return sum(tool.serialized_bytes() for tool in SURFACES[surface_id])


def tool_ids(surface_id: str) -> tuple[str, ...]:
    if surface_id not in SURFACES:
        raise ValueError("surface_unknown")
    return tuple(tool.tool_id for tool in SURFACES[surface_id])


def validate_call(surface_id: str, tool_id: str, arguments: dict[str, Any]) -> None:
    if not isinstance(arguments, dict):
        raise ValueError("arguments_not_object")
    candidates = {tool.tool_id: tool for tool in SURFACES.get(surface_id, ())}
    if tool_id not in candidates:
        raise ValueError("tool_not_exposed")
    expected = candidates[tool_id].required_keys
    if set(arguments) != set(expected):
        raise ValueError("tool_argument_shape_invalid")


def capability_surface_record(surface_id: str) -> dict[str, Any]:
    ids = tool_ids(surface_id)
    side_effecting = [tool for tool in ids if tool in {x.tool_id for x in DISTRACTOR_TOOLS}]
    return {
        "schema": "finite-tool-surface-lab.mitsuba-surface/v0.1",
        "surface_id": surface_id,
        "tool_ids": list(ids),
        "tool_count": len(ids),
        "serialized_bytes": surface_bytes(surface_id),
        "side_effecting_tool_count": len(side_effecting),
        "authority_effect": "NONE",
        "execution_authority_granted": False,
    }
