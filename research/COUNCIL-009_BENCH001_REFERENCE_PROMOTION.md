# COUNCIL-009 — BENCH-001 Reference Promotion

## Question

How should the successful BENCH-001 full artifact become a durable canonical reference?

## Evidence already available

- frozen BENCH-001 spec;
- design Monte Carlo PASS;
- full public GitHub-hosted benchmark PASS;
- information-ambiguity audit PASS;
- exact candidate artifact digest;
- deterministic generator and retrieval implementation.

## Candidates

A. Promote now with compact digest binding only.  
B. Cross-Python 3.12/3.13 FULL replay, exact stable-output digest comparison, then commit a compact reference bundle.  
C. Cross-OS full matrix before promotion.  
D. Commit the complete ~56 MB raw JSONL output directly into Git history.

## Council

**B — selected.**

It materially increases independent reproducibility while preserving repository efficiency.

**A — weaker.**
The candidate run is strong, but BENCH-001 is large enough that an independent replay is valuable before canonicalization.

**C — HOLD.**
Cross-OS replay can be added if portability becomes a research question or a contradiction appears.

**D — rejected.**
Raw rows are deterministic and regenerable from exact source/spec. Committing all raw JSONL permanently would add repository weight without proportional evidentiary value.

## Canonical-reference shape

Commit compact files:

- README.md;
- candidate manifest;
- candidate summary;
- aggregate rows;
- retrieval frontier;
- reference_verification.json;
- information-audit summary/binding.

Do not commit the full `per_task.jsonl` or `invalid_cells.jsonl`.

Instead record their exact SHA-256 values and the source/spec required to regenerate them.

```text
Raw Data Not In Git
!= Raw Data Unbound
```

## Replay equality boundary

Byte-compare stable research outputs:

- summary.json;
- per_task.jsonl;
- invalid_cells.jsonl;
- aggregates.jsonl;
- retrieval_frontier.json.

Exclude `manifest.json` from byte equality because Python/runtime/platform are intentionally different.

## 250k synthetic planning sensitivity

Seed: 2026092605.

Criteria:
- independence gain;
- reproducibility;
- Actions/storage efficiency;
- public inspectability;
- claim safety;
- maintenance cost.

Result:

```text
B cross-Python compact reference   100.0000%
A promote now compact                0.0000%
C cross-OS full matrix               0.0000%
D commit all raw to Git              0.0000%
```

Mean utility:

```text
B 0.9674
A 0.9172
C 0.8838
D 0.7924
```

Planning robustness only.

## Promotion gate

Promote BENCH-001 only if:

1. Python 3.12 full replay PASS;
2. Python 3.13 full replay PASS;
3. all five stable output files have byte-identical SHA-256 values;
4. information audit remains PASS;
5. candidate artifact/source/spec identities are bound;
6. the canonical README carries the synthetic-ambiguity and pre-Worker claim ceilings.

## Decision

```text
CROSS_PYTHON_EXACT_REPLAY
+
COMPACT_CANONICAL_REFERENCE
```
