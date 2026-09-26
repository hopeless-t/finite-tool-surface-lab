# BENCH-004 — Tool-Need Admission Gate

## Question

Can an explicit Tool-Need Admission Gate decide whether any Tool Surface should exist, reducing no-tool false exposure while preserving tool-required admission under controlled ambiguity?

BENCH-004 begins where BENCH-003 ended.

~~~text
Depth Selection
!= Tool-Need Admission

Tool Relevant
!= Tool Needed Now
!= Tool Should Be Visible
!= Tool May Execute
~~~

## Outcome contract

The gate emits exactly one of:

~~~text
ADMIT_TOOL_SURFACE
NO_TOOL_SURFACE
DEFER
~~~

DEFER is first-class.

It represents: the evidence is insufficient to decide safely; escalate, ask, or use another bounded fallback.

~~~text
DEFER
!= Correct
!= Incorrect Automatically
!= Permission
~~~

Every report must expose defer rate separately so a policy cannot hide mistakes by deferring everything.

## Architectural placement

~~~text
Request / State
      |
      v
Tool-Need Admission Gate
      |
      +-- NO_TOOL --> empty Tool Surface
      |
      +-- DEFER ---> no Tool Surface; bounded escalation/fallback
      |
      +-- ADMIT
             |
             v
      Retrieval / Ranking
             |
             v
        Depth Policy
             |
             v
         Tool Surface
             |
             v
   downstream authority gate
~~~

The admission gate cannot grant execution authority.

## Controlled synthetic truth families

### ADMIT_TOOL_SURFACE

- EXTERNAL_STATE_REQUIRED
- SIDE_EFFECT_REQUIRED
- SPECIALIZED_COMPUTE_REQUIRED

### NO_TOOL_SURFACE

- LOCAL_CONTEXT_SUFFICIENT
- IRRELEVANT_TOOL_MENU
- PREMATURE_TOOL
- USER_FORBIDS_TOOL

### DEFER

- MISSING_REQUIRED_INPUT
- AMBIGUOUS_INTENT

The benchmark contract defines these labels. It does not claim they are a universal ontology.

## The anti-shortcut design: retrieval isomorphism

BENCH-003 preserved an explicit gold capability signature. That was correct for the distractor question, but it makes a naive top-score threshold too powerful for an admission benchmark.

BENCH-004 therefore freezes retrieval-isomorphic pairs.

Example:

~~~text
Case A:
  menu = weather_tool + distractors
  retrieval query = same
  top-score vector = same
  state says current outside weather is required
  truth = ADMIT_TOOL_SURFACE

Case B:
  menu = weather_tool + distractors
  retrieval query = same
  top-score vector = same
  state says the required weather observation is already supplied locally
  truth = NO_TOOL_SURFACE
~~~

Frozen pairs:

- EXTERNAL_STATE_REQUIRED vs LOCAL_CONTEXT_SUFFICIENT
- SIDE_EFFECT_REQUIRED vs USER_FORBIDS_TOOL
- SPECIALIZED_COMPUTE_REQUIRED vs PREMATURE_TOOL

~~~text
Retrieval Evidence Isomorphic
!= Admission Semantics Equivalent
~~~

Any retrieval-score-only gate must therefore fail on at least some matched pairs.

This is intentional.

## Admission-state evidence

The controlled lane exposes structured, noisy evidence fields rather than the truth label:

- external-state dependency;
- side-effect intent;
- local-context sufficiency;
- precondition readiness;
- user Tool permission;
- intent clarity;
- menu relevance.

Ambiguity mixes evidence toward uncertainty without changing the latent truth.

The truth label is never included in the gate input.

## Candidate policies

### References

- ORACLE_TRI_STATE
- ALWAYS_ADMIT
- RANDOM_PRIOR

### Retrieval-only negative controls

- TOP_SCORE_THRESHOLD
- TOP_MARGIN_THRESHOLD

These are expected to expose the architectural limitation created by isomorphic pairs.

### Transparent admission-state baselines

- RULE_GATE_V0
- LINEAR_NEED_SCORE_BANDS

The linear gate returns a probability-like need score. Two thresholds define:

~~~text
p <= low        -> NO_TOOL_SURFACE
low < p < high  -> DEFER
p >= high       -> ADMIT_TOOL_SURFACE
~~~

No threshold is selected post hoc as a universal winner. The complete frozen sweep remains evidence.

## Downstream composition

Admission is evaluated both alone and composed with the two preregistered BENCH-003 surface policies:

- RELATIVE_TOP:0.9
- LARGEST_SCORE_DROP

If the gate outputs NO_TOOL_SURFACE or DEFER, downstream retrieval/depth is not allowed to materialize a Tool Surface.

This lets BENCH-004 measure whether a gate actually repairs the BENCH-003 no-tool exposure failure.

## Metrics

Primary:

- required Tool admission recall;
- no-tool false-admit rate;
- defer rate by truth class;
- tri-state macro accuracy;
- false NO_TOOL rate on required tasks;
- false ADMIT rate on DEFER tasks;
- post-gate no-tool nonempty-surface rate;
- post-gate surface bytes;
- risk-weighted false admission where applicable.

Probability-like gates additionally report:

- Brier score for the binary needs-Tool projection;
- calibration bins;
- threshold sensitivity.

Reports must never collapse DEFER into success.

## Constraint frontier

For every policy operating point, evaluate whether it satisfies combinations of:

- minimum required-admit recall;
- maximum no-tool false-admit rate;
- maximum defer rate.

This forms a Tool Admission Frontier rather than one selected best threshold.

## Planned deterministic workload

~~~text
3 seeds
x 4 registry sizes
x 9 truth families
x 4 ambiguity levels
x 2 candidate-plausibility levels
x 32 repeats
= 27,648 task conditions
~~~

Policy expansion remains small enough for one bounded hosted compute job, but runtime will be measured before any sharding decision.

## External lanes

### BFCL relevance / irrelevance

BFCL explicitly evaluates function relevance and irrelevance, including cases where none of the supplied functions should be called.

This is useful external evidence, but not the canonical basis.

Before import, BENCH-004 requires a corpus-quality audit and a fixed mapping from BFCL outcomes into the BENCH-004 admission contract.

### Decision Provider shadow lane

A future provider may implement:

~~~text
state -> p_need_tool
p_need_tool + frozen thresholds
-> ADMIT / NO_TOOL / DEFER
~~~

Candidates can include Jev, Cua, a local classifier, an LLM judge, or a deterministic rule.

Provider choice and provider qualification remain separate.

Paid/provider calls require separate Human approval.

~~~text
Decision Provider Signal
!= Tool Selection
!= Execution Authority
~~~

## Claim ceiling

BENCH-004 may establish that a frozen admission architecture improves synthetic Tool-surface exposure under controlled ambiguity.

It may not establish:

- end-to-end Worker task success;
- that Jev or any other provider is superior;
- a universal probability threshold;
- production safety;
- authority to execute Tools;
- MVCA Mainline policy.
