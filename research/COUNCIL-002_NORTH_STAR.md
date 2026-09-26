# COUNCIL-002 — North-star

## Decision question

What should the lab optimize without Goodharting on tool count or retrieval recall?

## Candidates

A. Tool Surface Frontier + MSTS(epsilon)  
B. end-to-end success / exposed-token scalar  
C. minimum k under recall constraint  
D. maximum end-to-end success only  
E. Bits-over-Random as the primary objective

## Council

A preserves multi-objective tradeoffs and can absorb Worker success, coverage, false invocation, and exposure cost.

B creates arbitrary scalar weighting.

C ignores downstream Worker selection once gold is present.

D permits FULL to win even when its exposure is wasteful or destabilizing.

E is useful for chance correction but too narrow as the sole lab objective.

## Synthetic planning sensitivity

250,000 draws, seed 20260926.

Criteria:
- anti-Goodhart behavior;
- end-to-end relevance;
- interpretability;
- benchmark portability;
- MVCA transfer;
- cost sensitivity.

Result:

```text
A TSF + MSTS(epsilon)        99.8756%
E Bits-over-Random primary    0.1100%
C minimum-k recall            0.0140%
B success/token               0.0004%
D success only                0.0000%
```

Planning robustness only.

## Decision

**ADOPT A.**

Use Bits-over-Random as a secondary metric and adaptive-depth reference, not the sole North-star.
