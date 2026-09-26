# COUNCIL-019 — BENCH-003 Result Interpretation

## Boundary

Status: **STAGING RESEARCH / NOT CANONICAL / NO MAINLINE AUTHORITY**

Source evidence:

~~~text
BENCH-003 FULL run = 36242144911
artifact = 10906331126
artifact digest =
sha256:96015668c446af1d7ed561aa8bed76ada532a9c38e0cfdd6ba584e171e02685f

policy observations = 483,840
aggregate rows = 10,080
frontier points = 2,184
observation sha256 =
019d4ec58cce84fd2e3c0b92e47fa0ec04bf312aa6bb8e1e421b812bf83db22c
state = PASS
~~~

## Finding 1 — coverage saturated

Across tool-required aggregate conditions, every non-oracle policy except
`FIXED_K:0` and `FIXED_K:1` retained exact all-required capability coverage.

This is good evidence that the frozen capability signature was preserved.

It is also a threat to validity:

~~~text
Gold Identity Preserved
!= Retrieval Difficulty Established
~~~

BENCH-003 is therefore more informative about **what wrong Tools remain visible**
than about hard recall failure.

## Finding 2 — no-tool is the architectural break

The adaptive policies abstain when the top score is exactly zero.

But plausible targeted distractors intentionally share query evidence.

For nonzero distractor density, no-tool tasks in six stress families therefore
produce positive scores and a nonempty adaptive surface.

Across the frozen balanced aggregate design, adaptive no-tool nonempty-surface
rate averages approximately **0.60**.

~~~text
Depth Selection
!= Tool-Need Admission
~~~

A selector that only asks "how many positively-scored Tools?" cannot answer the
prior question "should any Tool be exposed at all?"

This is a direct candidate seam for a small Decision Provider / Jev-style gate:

~~~text
Request
  -> NEED_TOOL? admission decision
  -> if YES: rank / depth / surface policy
  -> if NO: empty surface
~~~

The Decision Provider remains a proposal/signal. It does not gain execution
authority.

## Finding 3 — RISKY_RELEVANT defeats RELATIVE_TOP:0.9

For tool-required RISKY_RELEVANT conditions:

- `RELATIVE_TOP:0.9` preserves coverage but exposes every risky wrong
  distractor when density > 0.
- mean selected k grows roughly with distractor density:
  density 1 -> 3,
  3 -> 6,
  7 -> 12,
  15 -> 24.
- `LARGEST_SCORE_DROP` retains exact coverage with zero risky-wrong exposure
  in this frozen synthetic family.

Therefore:

~~~text
High Relative Score
!= Valid Capability
~~~

and:

~~~text
Adaptive Depth
!= Risk-Aware Admission
~~~

Do **not** generalize LARGEST_SCORE_DROP as universally safe. In MIXED conditions
it can retain substantial wrong exposure at higher densities.

## Finding 4 — valid equivalence creates a different surface problem

VALID_EQUIVALENT is not wrong.

However, tie-preserving adaptive policies expose the whole equal-score
equivalence block.

At density 15, `RELATIVE_TOP:0.9` and `LARGEST_SCORE_DROP` average roughly
24 visible Tool IDs while retaining the same required capability coverage.

This is not a correctness failure.

It is a surface-efficiency result:

~~~text
Valid Equivalent
!= Needlessly Co-visible

Equivalence-Aware Coverage
!= Equivalence-Aware Surface Compaction
~~~

A future lane may select at the **capability-equivalence-class** level and only
materialize one or a bounded number of representatives.

## Workload Monte Carlo

Post-analysis freezes 60,000 workload mixtures:

~~~text
Dirichlet alpha = 0.25, 1, 4
20,000 mixtures each
macro conditions = 120
coverage requirement = 0.99
~~~

The key test asks whether any current non-oracle policy can also keep conditional
no-tool nonempty-surface rate below 5% or 10%.

Local preflight found **0 feasible mixtures out of 60,000** at both ceilings.

The GitHub post-analysis workflow is the canonical reproducibility path for
this result.

This is not proof that an admission gate will succeed. It is evidence that the
current family of depth/selection policies does not solve the no-tool admission
problem under the frozen synthetic workload family.

## Pseudo-Council — next bounded experiment

Candidates:

A. **BENCH-004 Tool-Need Admission Gate** before surface-depth selection.
B. Equivalence-class surface compaction first.
C. Harder identity-confusable distractor generator first.
D. Worker-in-loop immediately.

Council:

- Failure Analysis -> A. The strongest structural failure is no-tool admission.
- Jev/Cua -> A. This is exactly a small binary/typed decision seam.
- Tool Surface -> A, then B. First decide whether a surface exists; then compact it.
- Generator Validity -> C remains necessary because BENCH-003 coverage is saturated.
- Worker Evaluation -> rejects D until admission semantics exist.
- Authority -> A is only an exposure proposal gate; execution authority stays downstream.

## 250k planning sensitivity

Seed: `2026092618`.

Criteria:
- observed blocker;
- causal isolation;
- MVCA fit;
- compute efficiency;
- future leverage;
- claim safety;
- external-validity bridge.

~~~text
A Tool-Need Admission Gate         99.5460%  mean utility 0.9416
B Equivalence Compactor             0.4524%  mean utility 0.8713
D Worker-in-loop                    0.0012%  mean utility 0.6427
C Harder Identity Decoys            0.0004%  mean utility 0.8472
~~~

Planning robustness only.

## Decision candidate

~~~text
NEXT RESEARCH =
BENCH-004 TOOL-NEED ADMISSION GATE

KEEP QUEUED =
equivalence compaction
harder identity-confusable distractors

DO NOT YET =
Worker-in-loop
~~~

Candidate invariant:

~~~text
Tool Relevant
!= Tool Needed Now
!= Tool Should Be Visible
!= Tool May Execute
~~~

This result remains research-only and does not alter MVCA Mainline authority.
