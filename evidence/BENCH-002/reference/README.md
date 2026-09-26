# BENCH-002 Canonical Reference

Status: **REFERENCE / REVIEWED**

BENCH-002 establishes that, under the frozen synthetic generator and TOKEN_JACCARD ranking, query-specific adaptive depth can improve the retrieval/surface frontier over fixed depth.

```text
Adaptive Retrieval Gain
!= Worker Selection Gain
!= Valid Tool Call
!= Task Success
!= MVCA Mainline Policy
```

## Full benchmark

```text
source commit = 6268d7c6ef51ddbb5d1a25467446fd02c1855096
run = 36233741224
artifact = 10903158359
artifact sha256 =
917008e625e76ec774ecf90828a915b92283ebdb8c10bc944be739ea03a029ae

state = PASS
policy observations = 314,496
aggregate rows = 3,276
frontier points = 835
adaptive frontier points = 542
observation sha256 =
b2070ee08502491498ced1862cf0b586bb79fddbbb1b9ee4faaf2ce395b86aeb
```

## Main synthetic operating point

Across all 96 tool-required aggregate conditions:

```text
RELATIVE_TOP:0.9
all_gold_rate min = 1.0
mean selected k = 11.9730902778
mean surface bytes = 1,521.4484592
```

FULL averaged 680 visible tools and about 85,782.67 serialized bytes at exact coverage 1.0.

FIXED_K:32 averaged exact all-gold coverage about 0.91591 and about 3,795.14 serialized bytes.

This does not establish 0.9 as a universal threshold. Multiple relative thresholds collapse to identical behavioral points because the synthetic Jaccard scores are discrete.

```text
Hyperparameter Distinct
!= Behavioral Operating Point Distinct
```

## Ambiguity adaptation

At N=2048, multi-tool, overlap 0.50 / 0.75, RELATIVE_TOP:0.9 expanded to roughly 89–91 candidates while retaining exact coverage.

The result is therefore:

```text
sharp evidence -> small surface
ambiguous evidence -> larger surface
zero evidence -> empty surface
```

All adaptive no-tool cells had nonempty-surface rate 0.

## Workload-mixture Monte Carlo

Run `36233978830` evaluated 60,000 random workload mixtures and 300,000 constrained policy selections.

For epsilon <= .01, RELATIVE_TOP:0.9 was selected in 100% of mixtures across all three Dirichlet workload regimes.

At larger epsilon, LARGEST_SCORE_DROP became increasingly competitive, exposing a real coverage/cost tradeoff.

## Independent replay

Run `36234093381`:

- Python 3.12 FULL PASS;
- Python 3.13 FULL PASS;
- GitHub compare PASS;
- local artifact readback independently confirmed byte-identical stable SHA-256 values.

## Compute-efficiency dogfood

A hot-path serialized-surface byte calculation was replaced with exact precomputed stub sizes.

The optimized run reproduced the exact observation digest and stable outputs.

Observed benchmark-step time on separate hosted runs fell from roughly 70.14 s to 54.14 s. This is descriptive only.

## Failure history

The first workload-Monte-Carlo workflow attempt failed before calculation because the repository package was not installed. The failure is preserved in `research/FAILURE-001_BENCH002_MC_IMPORT.md`.

## Storage

Large deterministic derived outputs remain bound by exact SHA-256 rather than duplicated into Git history.

```text
Raw Derived Data Not In Git
!= Raw Derived Data Unbound
```

## Claim ceiling

```text
BENCH-002 PASS
=
adaptive score-responsive depth can dominate fixed depth
under the frozen synthetic generator/ranking conditions.

BENCH-002 PASS
!= RELATIVE_TOP:0.9 universally optimal
!= real MCP registry result
!= embedding/reranker result
!= LLM Worker performance result
```

Next planned lane: **BENCH-003 Distractor Stress**.
