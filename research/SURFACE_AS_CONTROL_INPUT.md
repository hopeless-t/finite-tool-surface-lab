# Research Candidate — Active Tool Surface as a Control Input

> Status: OPEN RESEARCH CANDIDATE  
> Production / MVCA authority: NONE

## Question

The current Tool Surface Frontier treats the active surface primarily as an
exposure / selection object.

A stronger worker-in-the-loop question is:

> Does the composition of the visible tool surface change Worker behavior even
> when the required tool is present in every condition?

This separates:

~~~text
gold-tool coverage
!=
surface-induced worker state
~~~

The active surface may be both:

1. a set of available actions; and
2. an input that changes the Worker's next trajectory.

## Candidate model

Let:

~~~text
q   = task
S   = visible tool surface
x_t = Worker / context state
a_t = next observable action / abstention / tool call
~~~

Then:

~~~text
x_{t+1} = F(x_t, q, Encode(S), tool_results_t)
a_t     = pi(x_t, q, S)
~~~

A passive-surface model assumes that once relevant-tool coverage is fixed,
surface composition affects only selection difficulty.

The stronger hypothesis allows:

~~~text
same task
+ same gold tool present
+ different visible distractor / representation surface
->
different observable Worker trajectory
~~~

## Why this matters to TSF

The current Tool Surface Frontier optimizes utility against exposure cost/risk.

Worker-in-the-loop work may need a separate term:

~~~text
C_trajectory(S)
~~~

for surface-induced behavioral distortion or friction.

A candidate extension is:

~~~text
TSF point = (
    end_to_end_utility,
    exposure_cost,
    coverage,
    false_or_wrong_invocation,
    trajectory_cost
)
~~~

where trajectory cost must be defined only from observable harness data.

## Proposed BENCH-007 sub-study

Hold constant:

~~~text
task
gold-tool availability
serialized token budget where possible
provider / model
tool qualification
authority
acceptance criteria
~~~

Vary:

### A — Oracle-relevant surface

Only required / directly relevant tools.

### B — Coverage-matched neutral distractors

Same gold coverage plus unrelated tools.

### C — Coverage-matched semantic distractors

Same gold coverage plus plausible-but-wrong tools.

### D — Representation ablation

Same tools, different tool description / alias representation.

The goal is not to prove smaller is always better.

It is to test whether:

~~~text
Y(q,S)
~~~

depends on surface composition after simple coverage is controlled.

## Observable metrics

Use only externally visible harness data:

~~~text
end_to_end_success
tool_selection
wrong_tool_invocation
no_tool_false_invocation
tool_call_count
retry_count
turn_count
latency
serialized_surface_tokens
serialized_surface_bytes
abstention
~~~

If available from the harness without private reasoning traces:

~~~text
proposal_reversal_count
same_error_recurrence
time_to_first_valid_tool
~~~

## Candidate transition labels

Borrow only the formal language from DCS:

~~~text
SURFACE-EXPAND
    worker sees a larger action surface

SURFACE-PRUNE
    worker sees a smaller sufficient action surface

SURFACE-ROBUSTIFY
    behavior remains stable across representative distractor changes

SURFACE-OVERFIT
    performance is high only for one narrow surface representation

SURFACE-DEPENDENT
    the required capability exists but is accessible only under a specific
    exposed surface
~~~

These labels do not imply a biological mechanism.

## Falsification

The surface-as-control-input hypothesis weakens if, after controlling for gold
coverage and serialized exposure:

1. worker behavior is invariant to distractor composition;
2. representation ablation changes retrieval metrics but not worker behavior;
3. trajectory metrics add no predictive value beyond coverage and tool count;
4. effects fail replication across tasks / seeds / provider runs.

## DCS lineage

This research candidate was prompted by the DCS Human Control Transition work:

~~~text
Capability != Accessibility
More available control != better task control
Observation / exposure can alter the next state when it re-enters the system
~~~

Only the formal research pattern transfers.

~~~text
Human motor control != AI tool selection mechanism
~~~

## Claim ceiling

A positive result would show that, for tested Worker-in-the-loop tasks, active
surface composition is itself an experimentally relevant input.

It would not establish a universal optimal surface size or justify an MVCA
production policy.
