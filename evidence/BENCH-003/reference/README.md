# BENCH-003 Canonical Reference

Status: **REFERENCE / REVIEWED**

BENCH-003 studies how distractor topology, state validity, risk, and valid-equivalent structure change the Tool Surface required to preserve capability under the frozen synthetic generator and TOKEN_JACCARD ranking.

~~~text
Retrieval Coverage
!= Safe Tool Exposure
!= Tool-Need Admission
!= Valid Tool Call
!= Task Success
!= MVCA Mainline Policy
~~~

## Full benchmark

~~~text
source commit = f5328308d7b436becf6097231e6383720f1ba14e
run = 36242144911
artifact = 10906331126
artifact sha256 =
96015668c446af1d7ed561aa8bed76ada532a9c38e0cfdd6ba584e171e02685f

state = PASS
policy observations = 483,840
aggregate rows = 10,080
frontier points = 2,184
observation sha256 =
019d4ec58cce84fd2e3c0b92e47fa0ec04bf312aa6bb8e1e421b812bf83db22c
~~~

All frozen generator acceptance checks passed, including:

- exact registry-size preservation;
- gold capability signature preservation;
- valid-equivalent separation from wrong distractors;
- recomputable wrong/state/risk labels;
- equivalence-class consistency;
- adaptive zero-evidence abstention;
- tie-block preservation.

## Main interpretation

### 1. Coverage saturated

Across tool-required aggregate conditions, every non-oracle policy except
`FIXED_K:0` and `FIXED_K:1` retained exact all-required capability coverage.

Therefore BENCH-003 is stronger evidence about **surface exposure and distractor burden** than about hard retrieval recall.

~~~text
Gold Identity Preserved
!= Retrieval Difficulty Established
~~~

### 2. No-tool admission is a separate problem

The adaptive policy family abstains when top score is exactly zero.

But plausible wrong Tools intentionally share query evidence. Under nonzero targeted-distractor density, synthetic no-tool queries therefore produce positive-score candidates.

Across the frozen balanced aggregate design, every adaptive operating point had mean no-tool nonempty-surface rate **0.60**.

~~~text
Depth Selection
!= Tool-Need Admission
~~~

### 3. Risky relevance can defeat relative-score depth

For the frozen `RISKY_RELEVANT` family, `RELATIVE_TOP:0.9` preserved coverage but exposed every risky wrong distractor at nonzero density.

Its mean selected-k expanded approximately:

~~~text
density 1  -> 3
density 3  -> 6
density 7  -> 12
density 15 -> 24
~~~

In this single family, `LARGEST_SCORE_DROP` retained exact coverage with zero risky-wrong exposure.

This is **not** a universal safety claim; MIXED conditions behave differently.

### 4. Valid equivalence is also a compaction problem

`VALID_EQUIVALENT` Tools are correct alternatives, not wrong distractors.

However, tie-preserving adaptive policies expose the full equal-score equivalence block.

At density 15, `RELATIVE_TOP:0.9` and `LARGEST_SCORE_DROP` averaged about 24 visible Tool IDs with unchanged required-capability coverage.

~~~text
Valid Equivalent
!= Needlessly Co-visible

Equivalence-Aware Coverage
!= Equivalence-Aware Surface Compaction
~~~

## Workload-mixture Monte Carlo

Canonical post-analysis replay:

~~~text
source commit = 8306b62ec46b6815e98ae1b52072decdc16547c6
run = 36250772637
artifact = 10908544527
artifact sha256 =
3f3163f1dccb0b5081dc6b00ff47e60d8a2c68bc875a76156a47f285251bed5d

Dirichlet alpha = 0.25, 1, 4
20,000 mixtures each
total mixtures = 60,000
macro conditions = 120
candidate policies = 20
coverage requirement = 0.99
~~~

Feasibility under a conditional no-tool false-surface ceiling:

~~~text
<= 5%  -> 0 / 60,000 mixtures
<= 10% -> 1 / 60,000 mixtures
          (alpha=.25: 1 / 20,000)
~~~

This is not an impossibility theorem.

It is strong synthetic evidence that the current depth/selection family does not robustly solve the prior decision of whether any Tool surface should exist.

## Independent replay

Run `36251020964`:

- Python 3.12 FULL PASS;
- Python 3.13 FULL PASS;
- stable research outputs byte-identical;
- observation count = 483,840;
- observation SHA-256 exactly matches the original FULL run;
- aggregate rows = 10,080;
- frontier points = 2,184.

## Stable output SHA-256

~~~text
aggregates.jsonl
da1178bef322b0adc3c920378ce73173715c327a6bd6704fa4980a99314bb080

frontier.json
16308400cc3df2ca0f3ffc280d8d3c4164900baa81b748ae4e67aa6f9c6d6e0b

msts.json
11a3a190d681eddc5205551ba46e3fb1c2e6ad76f71081cd2a5e600634a55a79

observation_digest.json
b5edfa727eff30b566c45f6b268ca0c8af711e8fd5f478ac286b6fb09959b61a

summary.json
c80892da933912070006b933b8d1b6f9462da980be2cf379a0c4360e4316a5b2
~~~

Large deterministic derived outputs remain artifact-bound rather than duplicated into Git.

~~~text
Raw Derived Data Not In Git
!= Raw Derived Data Unbound
~~~

## Claim ceiling

~~~text
BENCH-003 PASS
=
under the frozen synthetic generator/ranking conditions,
distractor topology materially changes Tool-surface exposure,
and depth selection alone does not robustly solve no-tool admission.

BENCH-003 PASS
!= end-to-end Worker success
!= production safety
!= universal distractor taxonomy
!= universal admission rule
!= MVCA Mainline decision
~~~

## Next research candidate

**BENCH-004 — Tool-Need Admission Gate**

Candidate separation:

~~~text
Request
  -> Tool-Need Admission
  -> Retrieval / Depth
  -> Tool Surface
  -> downstream authority gate
~~~

BENCH-004 is a research candidate only. This reference grants no implementation or Mainline authority.
