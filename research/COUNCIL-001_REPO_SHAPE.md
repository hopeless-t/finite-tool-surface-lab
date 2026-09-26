# COUNCIL-001 — Repository Shape

## Decision question

What repository shape best supports public, falsifiable Tool Surface research and later MVCA transfer?

## Candidates

A. topological-spin-lab research pattern adapted to Tool Surface research  
B. benchmark-package-first  
C. notebook-first  
D. production router / MCP gateway first  
E. dataset-first

## Council

**Reproducibility**  
A strongest because intent/spec/evidence remain separately inspectable.

**Falsifiability**  
A strongest because FAIL/INVALID and intentional broken controls are first-class.

**Public inspection**  
A and E strong; A better binds claims to exact calculations.

**Iteration velocity**  
B/C can be faster initially but accumulate research-state ambiguity.

**MVCA transfer**  
A provides typed contracts and explicit authority boundaries without turning the research repository into MVCA Mainline.

**Architecture subtraction**  
A does not require a generic framework; components are added only when an experiment earns them.

## Synthetic planning sensitivity

250,000 draws, seed 20260926.

Criteria weights were perturbed around:

- reproducibility .24
- falsifiability .20
- public inspectability .16
- low premature abstraction .14
- MVCA transfer .16
- iteration velocity .10

Result:

```text
A topological pattern adaptation  93.7912%
B benchmark package                4.8784%
E dataset first                    1.3292%
C notebook first                   0.0012%
D product/router first             0.0000%
```

This is planning robustness under declared engineering priors, not empirical research probability.

## Decision

**ADOPT A.**

Reuse the discipline, not the physics-specific content.
