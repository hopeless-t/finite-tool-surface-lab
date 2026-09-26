# Reproducibility

This repository inherits the reproducibility discipline of topological-spin-lab.

## Canonical path

```text
Intent
  ↓
Strict Spec
  ↓
Execution
  ↓
Structured Observation
  ↓
Acceptance
  ↓
Evidence
```

## Canonical evidence bundle

When a benchmark earns a reference:

```text
manifest.json
metrics.json
per_task.csv or per_task.jsonl
README.md
```

The manifest should identify source commit, spec/digest, fixture/dataset digest, seeds, runtime/platform, and provider/model identity when applicable.

## Reference semantics

Cross-platform reproduction means agreement under declared tolerances.

It does not necessarily mean byte-identical timing, tokenization, or hosted-model output.

Deterministic synthetic fixtures should be byte-identical for identical generator version + seed.

## Public external datasets

Prefer pinned release, license note, download script, expected hash, and deterministic transformation manifest.

## Failure-path requirement

The harness is incomplete until it detects invalid specs, corrupted gold labels, broken ORACLE/FULL controls, intentionally damaged policies, and malformed evidence.
