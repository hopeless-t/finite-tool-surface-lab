# COUNCIL-005 — VAL-001 Reference Promotion

## Question

What additional evidence is sufficient before promoting the reviewed VAL-001 Action artifact into the repository's canonical reference evidence?

## Fresh intake

GitHub documents that workflow artifacts carry SHA-256 digests and that artifact attestations can establish workflow/repository/commit provenance.

For this research repository, provenance is useful but does not replace independent result replay.

## Candidates

A. Repeat once on the same Python/runtime and compare headline metrics.  
B. Full replay on Python 3.12 and 3.13; compare stable research outputs byte-for-byte.  
C. Cross-OS matrix across Linux/macOS/Windows.  
D. Promote immediately because the original GitHub run passed.  
E. Add GitHub artifact attestation and treat attestation as scientific replication.

## Council

**B — selected.**

It adds a meaningfully independent runtime dimension at small compute cost and preserves exact comparison of deterministic outputs.

**A — weaker.**
Useful for flake detection but less independent.

**C — HOLD.**
Cross-OS evidence may become useful later, but VAL-001 is stdlib-only and the added hosted-runner cost is not justified before a portability failure appears.

**D — rejected.**
Run PASS alone does not satisfy the repository's explicit artifact-to-reference promotion boundary.

**E — HOLD as provenance hardening.**
Cryptographic provenance answers "where/how was this artifact produced?" It does not answer "does the result independently reproduce?"

## Comparison boundary

Byte-compare only stable research outputs:

- metrics.json
- random_calibration.jsonl
- cell_digests.jsonl

Do not byte-compare manifest.json because Python version and platform are intentionally recorded there.

```text
Runtime Metadata Difference
!=
Research Result Difference
```

## Synthetic planning sensitivity

250,000 draws, seed 2026092602.

Criteria:
- independence gain;
- deterministic falsifiability;
- Actions efficiency;
- public inspectability;
- privilege minimization;
- maintenance simplicity.

Result:

```text
B cross-Python exact replay        97.8420%
C cross-OS matrix                   1.5124%
A same-runtime repeat               0.6448%
E attestation-only                  0.0008%
D immediate promotion               0.0000%
```

Planning robustness only; not a replication probability.

## Promotion gate

Promote only if:

1. Python 3.12 full replay PASS;
2. Python 3.13 full replay PASS;
3. stable research outputs are byte-identical;
4. the original candidate artifact digest remains recorded;
5. reviewed reference files are committed explicitly;
6. README states claim ceiling and source/replay provenance.

## Decision

```text
CROSS_PYTHON_EXACT_REPLAY_BEFORE_REFERENCE_PROMOTION
```
