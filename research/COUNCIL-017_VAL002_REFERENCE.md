# COUNCIL-017 — VAL-002 Reference

## Question

What evidence is sufficient to close VAL-002?

## Evidence

- exact npm package version and integrity;
- deterministic adapter;
- candidate Tool itself used for seeded sampling;
- Node 20 extraction PASS;
- Node 22 extraction PASS;
- catalogue byte-identical across runtimes;
- alias equivalence and homonym structure both non-empty;
- exact catalogue SHA-256.

## Decision

The adapter's claim is narrow and fully covered by the observed evidence.

```text
VAL-002 = PASS / REFERENCE / CLOSED
```

The full catalogue remains regenerable from pinned package identity + adapter code.

If npm/source provenance hardening is later required, it may be added without changing the current claim unless it reveals a contradiction.
