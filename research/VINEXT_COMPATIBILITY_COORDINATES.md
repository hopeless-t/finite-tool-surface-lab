# VINEXT-001 — Compatibility is a coordinate vector, not a scalar

Date: 2026-10-02

Primary sources:
- Cloudflare Vinext 1.0 announcement, 2026-09-28.
- cloudflare/vinext README and compatibility scanner.
- inspected `packages/vinext/src/check.ts` blob:
  `95aa6e06675388ac81f85639003ae09ed396d19c`

## Source atoms

Vinext reimplements the public Next.js API surface on Vite and can target multiple
deployment platforms. Its own documentation explicitly describes pragmatic
compatibility rather than bug-for-bug parity and lists known gaps.

The `vinext check` scanner does not model compatibility as one boolean. It
classifies concrete items across dimensions including:
- imports;
- config;
- libraries;
- conventions.

Each item is typed as:
- `supported`;
- `partial`;
- `unsupported`.

It also emits aggregate summary counts / a score.

## Catfood atom

The aggregate is useful for orientation but it is not an injective
representation of application compatibility.

```
Compatibility Score
!=
Compatibility Coordinate Vector
```

Two applications can have identical supported/partial/unsupported counts while
the unsupported coordinate is completely different. If one unsupported item is
on a critical execution path, those states are not interchangeable.

For reconstruction and admission decisions, preserve coordinates such as:

```
(dimension, feature_name, status)
```

rather than keeping only a scalar percentage.

## KITten-Coordinate relation

This is direct representation aliasing.

Let `Phi(app)` be the full compatibility coordinate vector and `s(app)` an
aggregate score. It is easy to have:

```
s(A) = s(B)
but
Phi(A) != Phi(B)
```

Therefore a scalar score cannot satisfy a uniqueness condition for
safety-relevant compatibility states.

## Minimal probe

`compat_coordinate.py` constructs two profiles with the same aggregate counts
but different unsupported features and detects the collision.

## Claim ceiling

This does not criticize Vinext's score: Vinext itself retains the detailed
coordinates. The extracted lesson is specifically for downstream systems that
might collapse the report to one number.

Catfood verdict: **KEEP the coordinate-vector atom.**
