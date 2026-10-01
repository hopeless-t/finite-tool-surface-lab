# COUNCIL-024 — Mitsuba capability-shaped surface

Date: 2026-10-01

## Observation

Mitsuba-ComfyUI-27B is published as a visual/prompt specialist and explicitly warns
against coding use. The published evaluation also reports weaker general tool
selection than rule-following/vision behavior.

## Catfood hypothesis

Do not expose a generic agent tool menu to a specialist merely because the transport
can express it.

The first live arm should expose only four advisory, non-mutating operations:

- visual description;
- pairwise visual comparison;
- visual prompt compilation;
- prompt-constraint checking.

The comparison arm may serialize generic shell/git/GitHub/filesystem/network/code
tools, but those are experimental distractors and grant no execution authority.

## Boundary

Tool exposure is not authority. This experiment measures cognitive/surface friction.
Any future executable adapter remains subject to MVCA admission and execution leases.

## External implementation note

The PrismML runtime is not treated as a black box. Its `prism` branch contains
separate PQ2_0/PTQ1_0 group-128 codecs and backend kernels. Runtime commit identity
therefore belongs in every live Mitsuba cell.
