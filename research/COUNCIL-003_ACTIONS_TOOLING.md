# COUNCIL-003 — GitHub Actions / Research Tooling

## Trigger

Human direction: reuse lessons from `finite-ram-lab` and design GitHub Actions calculation tools efficiently.

## Candidates

A. Minimal dedicated workflows + cheap CI + path filters; add reusable calculators only when earned.  
B. Copy the full finite-ram-lab generic calculator toolbox immediately.  
C. Matrix/shard every experiment from the start.  
D. Keep all research compute local and use Actions only for unit tests.

## Council

**A — selected.**
- preserves public reproducibility;
- keeps Actions invocation count low;
- keeps dependencies small;
- still permits later shard/aggregate workflows;
- avoids prematurely importing calculators unrelated to Tool Surface research.

**B — rejected for now.**
The finite-ram toolbox is valuable prior art, but changepoint/MILP/system-ID/tail fitting are not all required by VAL-001.

**C — rejected for cheap workloads.**
Parallelism itself has orchestration cost. VAL-001 is small enough for one deterministic job.

**D — rejected as sole strategy.**
It saves Actions resources but weakens third-party reproducibility and public readback.

## 250k synthetic planning sensitivity

Seed: 20260926.

Criteria:
- reproducibility;
- compute efficiency;
- Actions-call efficiency;
- public inspectability;
- future scalability;
- maintenance cost.

Result:

```text
A minimal dedicated + earned toolbox   98.9616%
D local-only + CI                       0.5936%
B generic toolbox now                   0.4448%
C matrix everything                     0.0000%
```

Mean utility:

```text
A 0.9251
D 0.8523
B 0.8468
C 0.7227
```

Planning robustness only; not empirical performance probability.

## Imported finite-ram-lab atoms

ABSORB:
- read-only workflow permissions;
- timeout bounds;
- cheap CI smoke;
- `workflow_dispatch` for research calculations;
- path filters;
- deterministic seeds;
- shard -> artifact -> aggregate for genuinely heavy independent work;
- `GITHUB_STEP_SUMMARY`;
- no automatic evidence commit.

ADAPT:
- initial Tool Surface core stays stdlib-only;
- no matrix for VAL-001;
- generic research calculator workflow deferred until two or more Tool Surface studies need the same calculator.

HOLD:
- SciPy/pandas analysis extras;
- deep Monte Carlo fan-out;
- generic calculation catalog.

## Decision

```text
A_MINIMAL_ACTIONS_PLUS_EARNED_TOOLS
```
