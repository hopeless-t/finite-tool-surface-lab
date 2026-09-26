# BENCH-004 Prior-Art Map

This file separates source observations from Catfood inference.

## BFCL — relevance / irrelevance detection

Sources:

- Berkeley Function Calling Leaderboard
- https://gorilla.cs.berkeley.edu/leaderboard
- https://gorilla.cs.berkeley.edu/blogs/12_bfcl_v2_live.html
- Patil et al., ICML 2025

SOURCE OBSERVATION:

BFCL explicitly evaluates cases where no supplied function is relevant and the model is expected not to emit a function call. It also separates relevance and irrelevance detection.

CATFOOD INFERENCE:

Tool-need / no-tool behavior deserves a first-class benchmark axis rather than being hidden inside ordinary tool selection.

BENCH-004 differs by placing admission before surface construction and by separately tracking DEFER.

## Jev / Noul versus Choice

Sources:

- LangChain, Building a Harness with Jev, 2026-09-17
- Made with Jev, agentic harness guide
- Learn Jev agent-harness guide

SOURCE OBSERVATION:

Jev exposes typed decision primitives. Community/tutorial material around Jev distinguishes relative selection (Choice) from absolute yes/no-style judgment (Noul) and recommends host-owned validation/permissions.

CATFOOD INFERENCE:

A relative chooser can always nominate a winner even when no Tool is needed.

The admission question should therefore be represented independently from downstream ranking.

~~~text
Which Tool?
!=
Any Tool?
~~~

Jev is one possible future Decision Provider, not part of the canonical synthetic lane.

## ToolChoiceConfusion / CMTF

Source:

- arXiv:2606.06284

SOURCE OBSERVATION:

The work argues that semantic relevance is insufficient: a Tool may be related to a task but unnecessary or premature at the current step.

CATFOOD INFERENCE:

BENCH-004 must include state-dependent no-tool conditions such as PREMATURE_TOOL, not only menus containing completely irrelevant Tools.

## ToolMenuBench

Sources:

- arXiv:2606.15508
- https://github.com/R-Suresh/ToolMenuBench

SOURCE OBSERVATION:

The benchmark separates distractor families including semantic, schema-compatible, premature, risky, cross-domain, near-duplicate, and mixed conditions.

CATFOOD INFERENCE:

Admission should be stressed against plausible Tool menus, not only easy irrelevant menus.

## LangChain tool-call middleware

Sources:

- LangChain Jev harness article
- LangChain middleware reference

SOURCE OBSERVATION:

Modern agent middleware can intercept or block Tool calls and can keep deterministic limits/policy in the harness.

CATFOOD INFERENCE:

The admission gate belongs in the host/harness path and must not itself become an authority plane.

## Benchmark-quality caution

A September 2026 Epoch AI audit reported substantial quality defects in its sampled BFCL v4 tasks.

CATFOOD INFERENCE:

BFCL is useful as an external lane, but BENCH-004 should not inherit it uncritically or use it as the sole canonical evidence source.

The external lane therefore requires its own corpus audit before use.
