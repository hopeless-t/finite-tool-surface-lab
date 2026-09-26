# COUNCIL-020 — BENCH-003 Reference Promotion

## Question

Should BENCH-003 be promoted from successful experiment evidence to compact canonical reference?

## Deterministic gate readback

~~~text
Original FULL:
PASS
483,840 observations
10,080 aggregate rows
2,184 frontier points

Post-analysis:
PASS
60,000 workload mixtures
source FULL digest bound

Cross-Python replay:
Python 3.12 PASS
Python 3.13 PASS
stable outputs BYTE_IDENTICAL
original observation digest EXACT MATCH

CI at replay commit:
PASS
~~~

No promotion gate is unresolved.

## Candidates

A. Promote compact canonical reference now.
B. Hold despite all frozen gates passing.
C. Run another identical FULL replay before promotion.

## Pseudo-Council

- Evidence Integrity -> A. Original, post-analysis, and independent replay are all bound.
- Reproducibility -> A. Stable outputs are byte-identical across Python 3.12 and 3.13.
- Claim Safety -> A. Reference README explicitly preserves the synthetic-only claim ceiling.
- Storage Discipline -> A. Keep large deterministic outputs artifact-bound; commit only compact hashes/findings.
- Anti-Rework -> rejects C. Another identical replay has low marginal information value after the cross-runtime equality check.
- Conservative Review -> B is defensible only if a frozen gate remains unresolved; none does.

## 250k promotion sensitivity

Seed: `2026092619`.

Criteria:

- evidence sufficiency;
- reproducibility;
- storage efficiency;
- claim safety;
- marginal information value;
- closure readiness.

~~~text
A PROMOTE_REFERENCE      100.0000%   mean utility 0.9750
B HOLD_FOR_MORE_REPLAY     0.0000%   mean utility 0.7249
C RERUN_FULL_AGAIN         0.0000%   mean utility 0.6249
~~~

Planning robustness only.

This is not a technical-success probability.

## Promotion shape

Commit compact reference material only:

- README;
- verification manifest;
- selected findings;
- replay summary;
- stable output SHA-256.

Do not duplicate large derived outputs into Git history.

~~~text
Reference Promotion
!= Mainline Adoption

Research Closure
!= Production Policy
~~~

## Decision

~~~text
BENCH-003 = PASS / REFERENCE / CLOSED

NEXT RESEARCH CANDIDATE =
BENCH-004 TOOL-NEED ADMISSION GATE
~~~

BENCH-004 remains a research candidate and receives no implementation authority from this decision.
