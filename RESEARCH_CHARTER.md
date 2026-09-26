# Research Charter

## Mission

Study how a finite active tool surface changes AI Worker capability, cost, reliability, and safety.

The lab does not assume that smaller surfaces are always better. It identifies conditions where smaller, adaptive, or full surfaces are sufficient, insufficient, or harmful.

## Authority boundary

```text
STATUS = OPEN RESEARCH
MVCA MAINLINE AUTHORITY = NONE
TOOL QUALIFICATION AUTHORITY = NONE
EXECUTION AUTHORITY = NONE
PRODUCTION QUALIFICATION = NONE
```

## Core invariants

```text
Tool Available != Tool Visible
Tool Visible != Tool Selected
Tool Selected != Tool Qualified
Tool Qualified != Tool Authorized

Registry Coverage != Retrieval Quality
Retrieval Quality != Worker Selection Quality
Worker Selection Quality != End-to-End Success

Smaller Surface != Safer Surface
Retrieval Confidence != Execution Authority
Research Finding != Mainline Decision
```

## Research method

Each durable tranche follows:

1. prior-art intake;
2. atomic decomposition;
3. competing hypotheses;
4. pseudo-Council to convergence;
5. planning sensitivity / Monte Carlo when useful;
6. strict spec;
7. deterministic fixture construction where possible;
8. experiment or validation;
9. failure injection / Red Team;
10. readback and statistical analysis;
11. public evidence;
12. claim + limitations.

Planning sensitivity is never an empirical success probability.

## Evidence hierarchy

1. deterministic known-answer replay;
2. independent replication on public data;
3. controlled Worker-in-the-loop experiment;
4. provider-specific observation;
5. synthetic planning sensitivity;
6. analogy.

## Public-repository rule

A canonical claim must be reproducible from public inputs or deterministic generators committed here.

Private Catfood/MVCA observations may inspire hypotheses but cannot be the sole evidence for a public canonical claim.

Negative results and failed replications are scientifically useful.
