# COUNCIL-007 — VAL-001 Closure

## Question

After canonical reference promotion and cross-Python exact replay, should VAL-001 close now or require additional evidence first?

## Fresh readback

Observed on main:

- canonical reference directory exists;
- candidate artifact digest is bound;
- frozen spec digest is bound;
- Python 3.12 FULL replay PASS;
- Python 3.13 FULL replay PASS;
- stable research outputs byte-identical;
- post-promotion CI PASS;
- claim ceiling explicitly excludes BENCH-001 / Worker / MVCA policy claims.

## Candidates

A. Close VAL-001 now and move additional portability/provenance hardening to future lanes.  
B. Require Linux/macOS/Windows cross-OS replay before closure.  
C. Require GitHub artifact attestation before closure.  
D. Hold open for unspecified additional evidence.

## Council

**A — selected.**

The frozen claim is about deterministic public research-apparatus qualification, not universal cross-platform identity. Cross-Python exact replay already tests an independent runtime dimension while the canonical reference records exact provenance and digests.

B can add portability evidence, but it changes the evidence burden without changing the current claim ceiling.

C improves supply-chain provenance but is not scientific replication.

D creates an unbounded evidence requirement.

## 250k synthetic planning sensitivity

Seed: 2026092603.

Criteria:
- evidence sufficiency;
- marginal information gain;
- compute / Actions efficiency;
- public reproducibility;
- scope discipline;
- provenance strength.

Result:

```text
A close now             100.0000%
B require cross-OS        0.0000%
C attestation first       0.0000%
D indefinite hold         0.0000%
```

Mean utility:

```text
A 0.9546
B 0.8535
C 0.8444
D 0.6321
```

Planning robustness only. This is not a probability that the research result is scientifically true.

## Decision

```text
VAL-001 = PASS / REFERENCE / CLOSED
```

Future cross-OS replay or artifact attestation may be added as hardening without reopening VAL-001 unless they reveal a contradiction.

Next bounded research tranche:

```text
BENCH-001 — Fixed-k Surface Sweep
```
