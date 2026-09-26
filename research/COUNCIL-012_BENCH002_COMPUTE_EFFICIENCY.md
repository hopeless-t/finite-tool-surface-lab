# COUNCIL-012 — BENCH-002 Compute Efficiency

## Trigger

The first BENCH-002 public full run passed, but runtime observation exposed unnecessary work in the evidence-cost calculation.

`surface_serialized_bytes(registry, surface)` rebuilt a full Tool-ID lookup for every policy observation.

With 314,496 observations, that moved registry-scale work into the hot path.

## Candidates

A. Keep current implementation.  
B. Cache the Tool-ID -> serialized-stub lookup per registry.  
C. Precompute exact serialized-stub byte lengths per registry and calculate list byte length algebraically.

## Exactness

Canonical compact JSON for a surface is:

```text
[
  object_1,
  object_2,
  ...
]
+ newline
```

Under the repository's canonical JSON encoding:

```text
empty:
bytes = 3

non-empty:
bytes =
  3
  + sum(serialized_object_bytes_without_newline)
  + (surface_count - 1)
```

So C can reproduce the old byte count exactly without rebuilding or serializing the object list per observation.

## Council

C hoists an invariant out of the hot loop and reduces both allocations and repeated registry scans.

B is useful but still rebuilds payload objects/JSON for every observation.

A preserves simplicity but wastes compute.

## 250k synthetic planning sensitivity

Seed: 2026092608.

Criteria:
- semantic exactness;
- runtime gain;
- implementation simplicity;
- reproducibility;
- memory behavior;
- maintenance cost.

Result:

```text
C precomputed exact byte sizes  100.0000%
B cached lookup                   0.0000%
A keep current                    0.0000%
```

Mean utility:

```text
C 0.9739
B 0.9108
A 0.8286
```

Planning robustness only.

## Verification gate

The optimized full run must reproduce the first run's exact:

`observation_sha256 = b2070ee08502491498ced1862cf0b586bb79fddbbb1b9ee4faaf2ce395b86aeb`

If it does not, optimization is rejected.

## Decision

```text
HOIST_SERIALIZATION_SIZE_INVARIANT
+
REQUIRE_EXACT_OBSERVATION_DIGEST_IDENTITY
```
