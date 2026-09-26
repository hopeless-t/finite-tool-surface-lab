# GitHub Actions Research Tooling

The Actions design borrows operational lessons from `hopeless-t/finite-ram-lab` while keeping this lab smaller.

## Principle

```text
CI != Research Compute
Research Compute != Canonical Evidence Automatically
Artifact != Reviewed Reference
```

## Two lanes

### CI lane

Purpose:
- compile;
- unit tests;
- invalid/failure-path tests;
- cheap known-answer smoke calculations.

Constraints:
- 10-minute timeout;
- stdlib-only initial research core;
- no paid providers;
- no matrix fan-out for cheap calculations.

### Research-compute lane

Purpose:
- frozen full validation/benchmark runs;
- controlled Monte Carlo when experiment design requires it;
- public evidence artifacts.

Pattern:
- path-filtered trigger;
- `workflow_dispatch` for explicit reruns;
- `contents: read` only;
- deterministic seed;
- artifact upload;
- job summary;
- no automatic commit of evidence to main.

## Sharding rule

Use matrix/shards only when:

1. cells are independent;
2. aggregation is deterministic;
3. one-job runtime or memory is material;
4. fan-out buys more than orchestration overhead.

VAL-001 is deliberately **not sharded** because the full stdlib calculation is cheap.

BENCH-001 may earn sharding later by registry-size/overlap cell if measured runtime justifies it.

## Tool-library rule

Do not copy the entire `finite-ram-lab` scientific toolbox into this repository.

Borrow a calculator only after a concrete Tool Surface experiment requires it.

Likely future reusable calculators:
- bootstrap confidence intervals;
- Pareto frontier;
- change-point candidate detection;
- QMC/factorial design;
- PRCC/sensitivity ranking;
- exact finite-population / hypergeometric oracles.

`Reusable Calculation != Universal Dependency`

## Artifact lifecycle

```text
Action run
  ↓
artifact
  ↓
review
  ↓
claim / limitations
  ↓
explicit canonical-reference commit
```

GitHub Actions must not silently turn an unreviewed run into canonical evidence.
