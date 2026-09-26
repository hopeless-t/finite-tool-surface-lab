# COUNCIL-006 — BENCH-001 Design

## Fresh prior-art intake

The 2026 shortlist-depth literature treats the number of visible tools as an evaluation variable rather than assuming one fixed k is universally correct.

Bits-over-Random (BoR) uses a hypergeometric random baseline to chance-correct success at a given shortlist depth.

Toollery and SkillRouter further support separating large capability-library retrieval from final Worker selection.

## Decision questions

1. What role should empirical RANDOM-k play with only 64 repeats per exact synthetic cell?
2. Should BENCH-001 immediately introduce embeddings/rerankers?
3. Should the benchmark remain pre-Worker?

## Candidate architectures

A. Transparent deterministic lexical baseline + exact random oracle + empirical RANDOM negative control.  
B. Embedding retriever as the first baseline.  
C. LLM reranker as the first baseline.  
D. Public benchmark import before the synthetic fixed-k sweep.

## Pseudo-Council

**Causal-control seat** -> A.  
A transparent baseline makes overlap/alias effects inspectable.

**Statistics seat** -> A.  
RANDOM-k has an exact finite-population oracle. Monte Carlo should validate the control, not define the baseline.

**External-validity seat** -> D later.  
Public workloads matter but should follow VAL-001 and the synthetic baseline.

**Agent seat** -> keep BENCH-001 pre-Worker.  
Candidate coverage and downstream selection are distinct mechanisms.

**Architecture-subtraction seat** -> A.  
Embeddings and LLM rerankers add dependency/model confounds before a reference surface curve exists.

## 250k design Monte Carlo

The dedicated public design study simulates the sampling variability of empirical RANDOM-k across all valid:

```text
N in {32,128,512,2048}
k in {1,2,3,5,8,13,20,32,50} where k <= N
gold_count in {1,2}
```

with 64 repeats per exact cell.

Interpretation rule:

```text
Empirical RANDOM-k = negative-control observation
Exact hypergeometric = primary chance baseline
```

## BoR

For an any-relevant success rule:

```text
BoR = log2(P_observed / P_random)
```

where P_random is the exact hypergeometric chance probability for the same N, k, and number of relevant tools.

BoR is secondary. It does not replace raw coverage, all-gold coverage, candidate count, or serialized-byte exposure.

## Decision

```text
BENCH-001 =
transparent fixed-k surface baseline
+ exact chance oracle
+ empirical random sanity control
+ no Worker/model calls
```
