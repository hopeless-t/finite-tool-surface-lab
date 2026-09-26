# Research Repository Pattern — finite-tool-surface-lab adaptation

**Origin:** `hopeless-t/topological-spin-lab/docs/RESEARCH_REPOSITORY_PATTERN.md`

This repository deliberately inherits that public research shape.

## Inherited discipline

```text
Question
  ↓
Strict Spec
  ↓
Model / Policy
  ↓
Calculation
  ↓
Observable
  ↓
Acceptance
  ↓
Evidence
```

Also inherited:

- functional core + thin imperative shell;
- PASS / FAIL / INVALID / ERROR;
- fail-closed specs;
- known-answer-first validation;
- intentional failure injection;
- canonical reference evidence;
- provenance;
- primary-source lineage;
- Figure != Evidence;
- Plan != Result;
- Proposal != Decision.

## Domain translation

```text
topological-spin-lab:
physical model -> numerical observable

finite-tool-surface-lab:
registry + surface policy + Worker condition -> selection / cost / task observable
```

## Lanes

- RQ-xxx: open question;
- VAL-xxx: generator/harness/adapter validation;
- BENCH-xxx: comparative study;
- REF-xxx: named canonical reference when needed.

## Deliberate deviations

- No analytic/ package until an independent analytic baseline genuinely exists.
- No generic plugin architecture.
- No notebook-first canonical workflow.
- No production MCP gateway as a substitute for research.
- No empty directories merely to match a template.

> Do not template the research. Template the discipline around the research.
