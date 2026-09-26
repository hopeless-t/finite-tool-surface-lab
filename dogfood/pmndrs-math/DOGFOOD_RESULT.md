# DOGFOOD-001 Result — pmndrs/math

## Verdict

```text
EDIBLE_WITH_BONES
```

The package is useful enough to keep as a candidate computational Tool, but it should remain isolated until a concrete experiment needs its JS/TS geometry or data-oriented math surface.

`Dogfood PASS != Adopted Dependency`

## Exact run

```text
branch  = research/dogfood-pmndrs-math-v0
commit  = 1fbf6c52d40c1d691038016c1e87f5fc3bc81e9a
run     = 36231954801
job     = 108376654932
result  = SUCCESS
artifact= 10902529835
artifact sha256 = 06a9fa99880e36826ab5e16a58fd84032d7806af583f5a7d5a928e8bfd7b8f86
```

Runtime:

```text
Node v22.23.2
Linux x64
math@0.1.0
npm integrity:
sha512-hq5KkLblFiR8OO8ZYqPK02mBqrXuxJ6hwvhL3ZM9OFkAR82/20n4H768SWl4yVVrufh8VijEm42D4V9N8hDa2g==
```

Observed upstream main during intake:

`983a607676026c5f1b950f876bc688988de824e5`

The published npm package was tested by exact package version and npm integrity. This dogfood does not prove that the published tarball is byte-derived from that observed upstream commit.

## Taste

### Functional

PASS:

- import;
- caller-owned output identity;
- in-place aliasing;
- deterministic seeded Mulberry32 replay;
- QuickHull2 geometry smoke;
- packaged Agent Skill.

Observed deterministic RNG prefix for seed 123456789:

```text
1107202814
4169434471
3372958138
885470128
1301683845
3208624240
3344635568
1221959552
```

### Footprint

Installed package:

```text
199 files
2,020,664 bytes unpacked
transitive runtime dependencies observed by npm ls: none
```

Packaged Agent Skill:

```text
skills/math/SKILL.md
9,138 bytes
141 lines
```

It explicitly discusses allocation, caller-owned state, and monomorphic hot paths.

### Descriptive vector workload

400,000 `scaleAndAdd`-equivalent operations per block, 9 measured blocks after warmup:

```text
pmndrs/math in-place     median 0.994251 ms
manual in-place         median 0.997387 ms
allocating array        median 1.497542 ms
```

The checksums agree.

On this single GitHub runner:

- the library abstraction was effectively level with the manual in-place kernel;
- the allocating-array baseline took about 1.51x the time of the `math` in-place path.

This is **descriptive only**. It is not a stable performance claim and was not run under the repository's future statistical benchmark contract.

## Bones / friction

1. The lab is Python-first; this Tool requires a Node boundary.
2. It is a web/graphics/data-oriented math kernel, not a SciPy replacement.
3. Geometry/noise/IK/vector work is immediately plausible; MILP, symbolic algebra, scientific integration, sparse linear algebra, etc. remain outside its scope.
4. Current dogfood pins npm package identity, not a proven source-commit-to-package build chain.
5. Skill presence is useful evidence, not Skill qualification.
6. GitHub runner timing is too environment-sensitive for canonical performance claims.

## BORROW / ADAPT / HOLD

### BORROW

- data-oriented APIs;
- caller-owned output/workspace;
- seeded explicit RNG state;
- allocation-free hot-path discipline;
- library + API docs + Agent Skill packaging;
- composite benchmark philosophy.

### ADAPT

- isolated Node computational Tool lane for experiments that benefit from geometry/noise/IK;
- Tool+Skill paired dogfood in future Tool Surface experiments;
- package footprint as a Tool admission/economics observable.

### HOLD

- root dependency;
- MVCA Tool Asset qualification;
- generic Node runtime requirement for the whole lab;
- performance claims;
- source vendoring.

## Pseudo-Council

Given observed correctness, zero transitive runtime dependencies, small package footprint, shipped Skill, useful geometry primitives, and the Python/Node boundary, the result converged on:

```text
EDIBLE_WITH_BONES
```

A 250,000-draw planning sensitivity over correctness, dependency weight, runtime fit, immediate domain utility, Skill value, and evidence strength selected this verdict in the sampled prior space.

This planning sensitivity is not an empirical probability of usefulness.

## Dogfooding lesson for finite-tool-surface-lab

This candidate is itself evidence for a future research dimension:

```text
Tool Available
!= Tool Needed Now
!= Tool Worth Keeping Discoverable
!= Tool Worth Exposing To Worker
```

A Tool can be cheap to keep in the Warehouse while rarely deserving a place in the Active Tool Surface.
