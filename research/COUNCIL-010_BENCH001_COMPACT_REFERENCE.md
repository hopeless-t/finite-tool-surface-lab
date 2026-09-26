# COUNCIL-010 — BENCH-001 Compact Reference Shape

## Question

After exact cross-Python replay, should the canonical reference commit large regenerable derived files, bind them by digest, or commit all raw output?

## Candidates

A. Commit aggregates + frontier, bind raw files by digest.  
B. Commit compact summary/audit/reference metadata and bind all large stable outputs by digest.  
C. Commit every stable output including ~56 MB per-task JSONL.

## Council

B preserves scientific identity through exact source/spec/file hashes while minimizing permanent Git-history cost.

A is workable but permanently duplicates >1 MB of deterministic derived data that can be regenerated exactly.

C maximizes local convenience but creates disproportionate repository weight.

## 250k synthetic planning sensitivity

Seed: 2026092606.

Criteria:
- reproducibility;
- inspectability;
- repository efficiency;
- artifact independence;
- maintenance cost;
- offline durability.

Result:

```text
B compact + digest binding    99.9668%
A aggregates in Git            0.0332%
C all raw in Git               0.0000%
```

Mean utility:

```text
B 0.9625
A 0.9020
C 0.7046
```

Planning robustness only.

## Decision

```text
COMPACT_REFERENCE
+
EXACT_STABLE_FILE_DIGESTS
+
DETERMINISTIC_REGENERATION
```

The reference commits summary, manifest, information audit, selected findings, and verification metadata. Larger deterministic outputs remain bound by exact SHA-256 and can be regenerated from the frozen source/spec.
