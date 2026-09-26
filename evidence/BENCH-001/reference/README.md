# BENCH-001 Canonical Reference

Status: **REFERENCE / REVIEWED**

This directory is the canonical compact reference for BENCH-001.

## Scientific claim ceiling

BENCH-001 establishes retrieval/surface behavior for the frozen synthetic generator and policies.

It does **not** establish end-to-end AI Worker performance.

```text
Gold Tool Present In Surface
!= Worker Selects Gold Tool
!= Valid Tool Call
!= Task Success
!= MVCA Active Tool Surface Policy
```

The observed overlap transition is also **not** a universal semantic threshold.

Generator v0.1 creates a controlled information-ambiguity transition: for multi-tool tasks at overlap >= 0.50, the fixed four-token prefix taken from each selected tool contains no tool-unique token.

## Candidate run

- source commit: `158f7417aa76342e2cd4f0a75fb1b3328ec3a721`
- workflow run: `36222829153`
- job: `108351174955`
- artifact: `10899985944`
- artifact SHA-256: `eaea203f47a581d51b5d2300ab467ccf1bb7fda1560a734e189d8e8d3ff9aecc`
- state: PASS
- raw rows: 179,712
- invalid-k rows: 4,608
- aggregate rows: 2,808
- retrieval-frontier points: 329

## Independent replay

Run `36232999281` recomputed the entire benchmark independently under Python 3.12 and 3.13.

Both FULL replay jobs passed.

Compare job `108379664821` passed with:

```text
BYTE_IDENTICAL_STABLE_OUTPUTS
```

for:

- `summary.json`
- `per_task.jsonl`
- `invalid_cells.jsonl`
- `aggregates.jsonl`
- `retrieval_frontier.json`

Runtime-specific `manifest.json` is intentionally excluded from byte equality.

## Compact-reference policy

The raw per-task and derived aggregate/frontier files are deterministic and regenerable from the exact source commit and frozen spec.

To keep Git history small, this reference commits the compact scientific summary, information audit, and exact SHA-256 bindings instead of duplicating roughly 57 MB of regenerable JSONL.

```text
Raw Data Not In Git
!= Raw Data Unbound
```

See `stable-digests.sha256` and `reference_verification.json`.

## Selected findings

Under low-ambiguity synthetic conditions (overlap 0 and 0.25), the transparent TOKEN_JACCARD baseline achieved exact gold coverage with:

- k=1 for single-tool tasks;
- k=2 for two-tool tasks.

As registry size grows, those surfaces are a small fraction of FULL exposure. See `selected_findings.json`.

At overlap 0.50 and 0.75, multi-tool exact coverage collapses sharply at k=2. The information audit shows that this is partly construction-induced by tool-identity information being removed from the query prefix.

Therefore:

```text
Observed BENCH-001 Transition
=
Controlled Information-Ambiguity Stress Result

Observed BENCH-001 Transition
!=
Universal Tool-Surface Threshold
```

## RANDOM-k interpretation

The empirical RANDOM-k control has only 64 repeats per exact cell and is intentionally noisy.

A separate 250,000-simulation design study showed substantial maximum-cell sampling error, so exact hypergeometric probability is the primary chance baseline.

The full run's maximum empirical RANDOM-k recall error was `0.171875`, which is consistent with the design study's expected multiple-cell noise regime.

## Promotion rule

```text
Frozen Spec
+ Public Full Run
+ Design Monte Carlo
+ Information Audit
+ Cross-Python Exact Replay
+ Exact Digest Binding
= Canonical BENCH-001 Reference
```

Canonical Reference != Universal Truth.
