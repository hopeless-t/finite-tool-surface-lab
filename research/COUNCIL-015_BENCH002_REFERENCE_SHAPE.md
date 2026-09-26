# COUNCIL-015 — BENCH-002 Canonical Reference Shape

## Question

What should be persisted after successful cross-Python replay?

## Candidates

A. Commit full aggregate/frontier/MSTS derived data.  
B. Commit compact machine-readable reference + selected findings + MC result + exact stable hashes.  
C. Commit prose only.

## Council

B preserves exact scientific identity and useful public results while keeping deterministic derived data regenerable.

A is acceptable but permanently duplicates derived data already bound by exact hashes.

C removes too much machine-readable provenance.

## 250k synthetic planning sensitivity

Seed: 2026092610.

```text
B compact machine-readable reference   99.9844%
A commit aggregate data                  0.0156%
C prose only                             0.0000%
```

Planning robustness only.

## Decision

```text
COMPACT_REFERENCE
+
SELECTED_FINDINGS
+
MONTE_CARLO_RESULT
+
EXACT_STABLE_DIGESTS
```
