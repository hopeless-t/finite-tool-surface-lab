# VAL-001 Canonical Reference

Status: **REFERENCE / REVIEWED**

This directory is the first canonical reference evidence for VAL-001.

## Scientific claim ceiling

This reference establishes only that the current deterministic synthetic-registry / control / evidence harness satisfied its frozen VAL-001 acceptance checks and reproduced its stable research outputs across Python 3.12 and 3.13 on GitHub-hosted Ubuntu runners.

It does **not** establish that smaller Tool surfaces improve an AI Worker.

```text
VAL-001 PASS
!= BENCH-001 result
!= Worker-in-the-loop result
!= MVCA Active Tool Surface policy
```

## Candidate run

- source commit: `89e99a82f0f950e139d5156942c584ce9f499fc3`
- workflow run: `36221794870`
- artifact id: `10898733297`
- artifact SHA-256: `38b15ea425e51d4af336d69ae96aa99f31e6c74f80656fabf4564893a01a1a7b`
- Python: 3.12.14
- state: PASS
- cells: 60
- tasks: 5760
- max random/theory absolute error: 0.0038
- frozen tolerance: 0.02

## Independent replay

Replay run `36222102366` recomputed the full study independently under:

- Python 3.12.14;
- Python 3.13.15.

Both replay jobs passed.

The compare job `108349191466` passed and reported:

```text
BYTE_IDENTICAL_STABLE_OUTPUTS
```

for:

- `metrics.json`
- `random_calibration.jsonl`
- `cell_digests.jsonl`

Runtime-specific `manifest.json` fields are intentionally excluded from byte equality.

## Files

The data files in this directory are the exact reviewed files extracted from the candidate GitHub Actions artifact.

See `replay_verification.json` for artifact IDs, workflow IDs and SHA-256 bindings.

## Promotion rule

```text
Action Artifact
+ Review
+ Independent Replay
+ Exact Digest Binding
= Canonical Reference

Canonical Reference
!= Universal Truth
```
