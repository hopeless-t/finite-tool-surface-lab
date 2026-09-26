# COUNCIL-011 — BENCH-002 Adaptive-k Design

## Fresh prior-art intake

- Repantis et al., *How Many Tools Should an LLM Agent See? A Chance-Corrected Answer* (arXiv:2605.24660) treats shortlist depth as a per-query decision variable and reports a simple adaptive policy that can approach deep-list coverage with a much smaller average shortlist.
- Toollery (arXiv:2609.22218) reinforces candidate compression before final LLM selection.
- Adaptive retrieval work outside Tool use also treats query-specific depth as preferable to one global k when query difficulty varies.

## Decision question

What is the smallest BENCH-002 that isolates adaptive-depth behavior without introducing learned-policy confounds?

## Candidates

A. Transparent score-distribution policy frontier over the existing deterministic ranking.  
B. Reinforcement-learning depth policy.  
C. Learned depth classifier.  
D. One globally tuned threshold selected on the evaluation set.  
E. Offline query clusters with fixed depth per cluster.

## Council

**A — selected.**

It isolates the depth decision while holding ranking constant and leaves a complete frontier rather than fitting one post-hoc winner.

B/C are important later but add training data, model, optimization, and generalization confounds.

D creates evaluation leakage.

E is useful prior art but moves the question from score evidence to learned/engineered query groups.

## Policy atoms

### POSITIVE_SUPPORT
Expose every candidate with positive retrieval score.

### RELATIVE_TOP(theta)
Expose all positive-score candidates whose score is at least theta times the top score.

### CUMULATIVE_SCORE_MASS(tau)
Normalize positive scores and expose the shallowest prefix reaching tau cumulative mass, expanded to include the entire tie block at the cutoff.

### LARGEST_SCORE_DROP
Cut at the largest positive adjacent score drop. If no positive drop exists, expose the complete positive-score support.

## Mandatory abstention

```text
top_score == 0 -> k = 0
```

This is evidence-based abstention, not authorization.

## Tie rule

```text
Equal Score
!= Permission To Choose Arbitrarily By Tool ID
```

All adaptive policies preserve complete cutoff tie blocks.

## 250k synthetic planning sensitivity

Seed: 2026092607.

Criteria:
- causal transparency;
- anti-overfit behavior;
- adaptive relevance;
- no-tool support;
- public reproducibility;
- future extensibility;
- compute efficiency.

Result:

```text
A transparent score frontier   100.0000%
B RL policy                      0.0000%
C learned classifier             0.0000%
D one tuned threshold            0.0000%
E fixed query clusters           0.0000%
```

Mean utility:

```text
A 0.9660
E 0.8262
D 0.8202
B 0.7778
C 0.7386
```

Planning robustness only.

## Evidence architecture

Three evaluation seeds are used to reduce one-seed dependence.

The implementation should stream policy observations into aggregates and a canonical SHA-256 observation digest rather than retaining a large observation object graph in memory.

This is both efficient and a direct dogfood of finite-resource research discipline.

## Decision

```text
TRAINING_FREE_ADAPTIVE_POLICY_FRONTIER
+
ZERO_EVIDENCE_ABSTENTION
+
TIE_BLOCK_PRESERVATION
+
STREAMING_EVIDENCE_DIGEST
```
