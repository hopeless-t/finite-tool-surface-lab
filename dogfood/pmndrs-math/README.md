# DOGFOOD-001 — pmndrs/math

Isolated taste-test for `pmndrs/math`.

This directory is intentionally **not** part of the Python package dependency graph.

## Questions

- can the published package install/import cleanly?
- do documented caller-owned/out-parameter semantics hold?
- is seeded RNG reproducible?
- does geometry work out of the box?
- is the Agent Skill shipped in the package?
- what is the installed footprint?
- is representative vector math non-pathological on a GitHub runner?
- what operational friction appears in a Python-first research repo?

## Boundaries

```text
Dogfood PASS != Adopted Dependency
Dogfood PASS != Qualified Tool Asset
Runner Timing != Stable Performance Claim
Skill Present != Skill Qualified
```

Run output is descriptive research evidence.
