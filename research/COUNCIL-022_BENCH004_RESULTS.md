# COUNCIL-022 — BENCH-004 Result Interpretation

## Source evidence

~~~text
FULL run = 36252133177
artifact = 10909552716
artifact sha256 =
decfb2f017b7fdea71965538e6ec4c412548f71f720f563bb3ca44a1a193b155

state = PASS
observations = 884,736
aggregate rows = 9,216
macro rows = 32
frontier cells = 48
feasible frontier cells = 36
observation sha256 =
6a1138a8c55e4e6d1fffea79612746c7282908f377ed2a79e18f20cb1a038c2c
~~~

All frozen acceptance checks passed.

## Finding 1 — retrieval isomorphism worked

Matched ADMIT / NO_TOOL pairs use identical registry/query/ranking evidence.

Retrieval-only gates therefore cannot distinguish the admission semantics.

Across the frozen macro evidence:

~~~text
best retrieval-only no-tool false-admit rate = 0.375
best retrieval-only macro tri-state accuracy = 0.444444...
~~~

This is the intended negative control.

~~~text
Which Tool Looks Relevant?
!=
Should Any Tool Surface Exist?
~~~

## Finding 2 — transparent state admission can solve the frozen contract

RULE_GATE_V0:

~~~text
required admit recall = 1.000000
no-tool false-admit rate = 0.00634765625
defer truth recall = 0.96256510417
weighted non-truth defer rate = 0.02369068287
macro tri-state accuracy = 0.97348813657
post-gate no-tool nonempty surface rate = 0.00341796875
~~~

This is a major improvement over retrieval-only gates under the frozen
synthetic semantics.

But the correct interpretation is architectural, not competitive.

RULE_GATE_V0 is deliberately written against the same structured concepts used
by the synthetic truth contract:

- local-context sufficiency;
- external-state dependency;
- side-effect intent;
- readiness;
- user permission;
- intent clarity;
- menu relevance.

Therefore:

~~~text
State Features Can Express Admission Semantics
!= RULE_GATE_V0 Is Universally Correct
~~~

## Finding 3 — DEFER is not a free win

The linear threshold sweep exposes the tradeoff.

Very wide bands achieve zero false admission partly by deferring too much and
losing required Tool recall.

Examples:

~~~text
bands 0.1 / 0.9:
required admit recall = 0.1667
no-tool false admit = 0
defer truth recall = 1
weighted non-truth defer ~= 0.7222

bands 0.3 / 0.7:
required admit recall ~= 0.9625
no-tool false admit ~= 0.2280
defer truth recall ~= 0.6774
weighted non-truth defer ~= 0.4273
~~~

This validates the frozen principle:

~~~text
Abstention
!= Correctness
~~~

## Finding 4 — admission fixes BENCH-003's no-tool surface failure

BENCH-003's adaptive depth family had mean no-tool nonempty-surface rate ~= 0.60
under the frozen balanced distractor design.

BENCH-004 RULE_GATE_V0 + downstream reference policy reduces the frozen
BENCH-004 no-tool nonempty-surface rate to ~= 0.00342.

Cross-benchmark numeric comparison is descriptive because the generators differ.

The architecture-level result is stronger:

~~~text
Admission Before Depth
can suppress Tool Surface construction
before a plausible wrong Tool becomes visible.
~~~

## Workload Monte Carlo

Post-analysis freezes:

~~~text
Dirichlet alpha = 0.25, 1, 4
20,000 mixtures each
60,000 total
288 aggregate workload conditions
15 non-oracle gate policies
~~~

Constraints:

~~~text
required-admit recall >= 0.99
no-tool false-admit <= 0.05
defer-truth recall >= 0.90
non-truth defer <= 0.05
~~~

Local preflight:

~~~text
alpha=.25  RULE_GATE_V0 feasible 18,857 / 20,000
alpha=1    RULE_GATE_V0 feasible 19,990 / 20,000
alpha=4    RULE_GATE_V0 feasible 20,000 / 20,000

all other non-oracle policies:
0 feasible mixtures
~~~

The GitHub post-analysis workflow is the reproducibility path for this result.

This is synthetic workload robustness only.

## Pseudo-Council — next bounded experiment

Candidates:

A. Cross-Python replay + reference closure now.
B. Representation-shift stress before closure.
C. BFCL external-lane audit.
D. Paid Jev/Cua/provider shadow now.
E. Worker-in-loop now.

Council:

- Evidence integrity -> A for the current frozen synthetic claim.
- Claim safety -> A, with explicit warning that the rule baseline is
  generator-aligned.
- External validity -> C immediately after closure.
- Robustness -> B remains queued because synthetic feature representation is
  the largest current threat to validity.
- Jev/Cua -> D only after external/representation validation and separate Human
  approval where paid.
- Worker evaluation -> rejects E for now.

## 250k planning sensitivity

Seed: 2026092722.

Criteria:

- evidence sufficiency;
- reproducibility;
- claim safety;
- external-validity leverage;
- compute cost;
- provider independence;
- next-step information gain.

~~~text
A replay + close synthetic lane    88.7648%   mean utility 0.9178
C BFCL audit next                   9.6956%   mean utility 0.8865
B representation shift stress       1.5396%   mean utility 0.8641
D provider shadow                   0.0000%   mean utility 0.6254
E Worker-in-loop                    0.0000%   mean utility 0.4921
~~~

Planning robustness only.

## Decision candidate

~~~text
FIRST:
finish BENCH-004 synthetic lane replay/reference closure

NEXT RESEARCH:
BFCL relevance/irrelevance corpus audit
+
representation-shift stress

LATER:
Decision Provider shadow
Worker-in-loop
~~~

No provider call or Mainline authority is authorized by this result.
