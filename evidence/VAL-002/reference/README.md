# VAL-002 Canonical Reference

Status: **REFERENCE / REVIEWED**

VAL-002 qualifies the deterministic external Tool-catalogue adapter for `math@0.1.0`.

## Source identity

```text
package = math@0.1.0
npm integrity =
sha512-hq5KkLblFiR8OO8ZYqPK02mBqrXuxJ6hwvhL3ZM9OFkAR82/20n4H768SWl4yVVrufh8VijEm42D4V9N8hDa2g==
```

Observed upstream repository:
`pmndrs/math`

DOGFOOD-001 remains separate from this validation.

## Public run

```text
source commit = 92878f14989e12e9801f39b5ba5cbc0f20a07991
workflow run = 36237206047
Node 20 extract = PASS
Node 22 extract = PASS
compare = PASS
comparison = BYTE_IDENTICAL_NODE20_NODE22
```

## Catalogue

```text
tool_count = 384
alias equivalence groups = 35
cross-type homonym groups = 71
sampled alias pairs = 35
sampled homonym pairs = 64

catalog sha256 =
98fdcda9561222de0ed0a074e4572760f007b3471fc5a4241c4ac34e719866ba
```

## Semantics

Valid-equivalent example:

```text
vec3.dist
vec3.distance
```

The adapter derives this relation from JavaScript function identity.

Cross-type homonym example:

```text
vec2.distance
vec3.distance
vec4.distance
```

These names are similar but are not treated as equivalent by default.

```text
Lexical Similarity != Semantic Equivalence
Valid Alternative != Distractor
```

## Dogfooded computation

The adapter uses `mulberry32` from `math/random` for deterministic pair sampling.

Thus pmndrs/math participates both as:
- the external Tool catalogue under study;
- a bounded research calculation Tool.

## Failure history

The first compare workflow failed because the compare job looked for `catalog.json` at artifact root instead of `out/catalog.json`.

Recorded as:
`research/FAILURE-002_VAL002_ARTIFACT_PATH.md`

Extraction itself had passed; no comparison result was claimed from the failed run.

## Storage

The full catalogue is deterministically regenerable from the pinned npm package and adapter code.

The canonical reference stores its exact digest, counts, examples, package identity, and cross-runtime verification.

## Claim ceiling

```text
VAL-002 PASS
=
the pinned package can be deterministically transformed into
a stable external Tool/equivalence/homonym catalogue.

VAL-002 PASS
!= retrieval performance
!= Worker performance
!= pmndrs/math MVCA Tool qualification
```
