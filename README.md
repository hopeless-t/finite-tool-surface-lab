# finite-tool-surface-lab

**How many tools should an AI Worker see?**

A public research lab for studying the minimum sufficient active tool surface for LLM/agent workers.

The central hypothesis:

> Agent performance is not maximized by exposing the maximum number of available capabilities. It can improve when the Worker sees the smallest sufficient, evidence-selected working set of tools for the current task.

This repository treats tool visibility as a finite computational resource, analogous to a working set in memory systems.

~~~text
Tool Warehouse
      |
      | many available capabilities
      v
Surface Policy / Retriever
      |
      | small active subset
      v
AI Worker
      |
      v
Tool selection / abstention / execution
~~~

## Status

OPEN RESEARCH. No MVCA Mainline authority, implementation authority, or production claim is granted by this repository.

Research Finding != MVCA Mainline Decision.

## North-star

The North-star is the **Tool Surface Frontier (TSF)**: the Pareto frontier between end-to-end task success and the cost/risk of the tool surface exposed to a Worker.

A derived summary is **MSTS(epsilon) — Minimum Sufficient Tool Surface**: the smallest expected surface cost that keeps end-to-end performance within epsilon of an oracle-relevant tool surface while respecting coverage and false-invocation constraints.

We do not optimize "fewest tools" in isolation.

~~~text
Fewer Tools != Better System
More Tools != More Capability in Practice
Tool Available != Tool Visible
Tool Visible != Tool Selected
Tool Selected != Tool Qualified
Tool Qualified != Tool Authorized
~~~

See docs/NORTH_STAR.md.

## Research questions

1. At what point does exposing additional tools stop helping and begin to degrade selection?
2. Should shortlist size be chosen per query rather than fixed globally?
3. How quickly do near-duplicate and semantically overlapping tools degrade Worker selection?
4. Which tool fields are sufficient for routing: name, description, schema, examples, full body, qualification metadata?
5. How should a Worker behave when no available tool is relevant?
6. What changes when a task genuinely needs multiple tools?
7. Does the optimum surface change with Worker/model/provider strength?
8. When does retrieval/reranking cost more than it saves?
9. Can an MVCA Active Tool Surface Governor expose fewer tools without widening authority or hiding required qualified capability?

## Experimental philosophy

We keep four layers separate:

~~~text
Registry Coverage
!= Retrieval Quality
!= Worker Selection Quality
!= End-to-End Task Success
~~~

Primary baselines:

- ORACLE: expose exactly the gold relevant tool set.
- FULL: expose the entire registry.
- RANDOM-k: negative control.
- FIXED-k: deterministic shortlist depth.
- ADAPTIVE-k: select shortlist depth from query/retrieval evidence.

The first experiments are training-free and provider-neutral. Model training is deferred until simpler retrieval/policy experiments stop answering the research question.

## Experiment sequence

| ID | Experiment | Main question |
|---|---|---|
| E00 | Synthetic Registry Calibration | Can controlled registries with known overlap/difficulty be generated reproducibly? |
| E01 | Fixed-k Surface Sweep | How does success change as visible surface grows? |
| E02 | Adaptive-k Policies | Can per-query depth beat fixed-k? |
| E03 | Distractor Stress | Which irrelevant tools are most damaging? |
| E04 | Representation Ablation | Name vs description vs schema vs body vs qualification metadata |
| E05 | No-tool / Abstention | Does a smaller surface reduce false tool invocation? |
| E06 | Multi-tool Surface | What changes for genuine multi-tool tasks? |
| E07 | Public Benchmark Import | Reproduce selected BFCL / ToolBench / SkillRouter-style workloads |
| E08 | Worker-in-the-loop | Measure real model selection on identical candidate surfaces |
| E09 | MVCA Projection | Translate findings into an Active Tool Surface Governor candidate |

## What we calculate

Core measurements:

- gold tool coverage;
- candidate count;
- exposed schema/token volume;
- retrieval latency;
- Worker selection accuracy conditional on gold presence;
- wrong-tool invocation rate;
- no-tool false invocation rate;
- end-to-end task success;
- tool-call count;
- reasoning turns;
- provider/runtime cost.

Analysis methods:

- bootstrap confidence intervals;
- paired comparisons on identical tasks;
- surface-size response curves;
- change-point/degradation-threshold analysis;
- factorial sensitivity analysis;
- Monte Carlo workload mixtures;
- Pareto-frontier construction;
- power analysis before expensive model-in-the-loop runs.

## Public-repository research contract

Every durable claim should be independently inspectable:

~~~text
Claim
 -> exact code commit
 -> exact dataset/registry digest
 -> exact configuration
 -> exact seeds
 -> raw result
 -> analysis
 -> limitations
~~~

Failed replications, negative results, adversarial registries, alternative routing policies and counterexamples are first-class results.

Canonical claims must be reproducible without private Catfood/MVCA data. Proprietary-provider experiments may be supplemental evidence but cannot be the sole support for a canonical claim.

## Planned repository layout

~~~text
.
├── README.md
├── RESEARCH_CHARTER.md
├── docs/
│   ├── NORTH_STAR.md
│   ├── RESEARCH_QUESTIONS.md
│   ├── METRICS.md
│   ├── EXPERIMENT_ROADMAP.md
│   └── THREATS_TO_VALIDITY.md
├── references/
├── claims/
├── schemas/
├── benchmarks/
├── experiments/
│   ├── E00_synthetic_registry/
│   ├── E01_fixed_k_surface/
│   ├── E02_adaptive_k/
│   ├── E03_distractor_stress/
│   ├── E04_representation_ablation/
│   └── E05_no_tool_abstention/
├── src/finite_tool_surface_lab/
├── tests/
└── results/
~~~

Large benchmark data should not be committed blindly to Git. Prefer deterministic generators, small fixtures, content-addressed manifests, and external dataset releases when appropriate.

## Reference work

- Toollery — candidate compression for large skill/tool libraries: https://arxiv.org/abs/2609.22218
- How Many Tools Should an LLM Agent See? A Chance-Corrected Answer: https://arxiv.org/abs/2605.24660
- SkillRouter — retrieve-and-rerank at about 80K skills: https://arxiv.org/abs/2603.22455 and https://github.com/zhengyanzhao1997/SkillRouter
- BFCL — executable function/tool-calling evaluation: https://gorilla.cs.berkeley.edu/leaderboard
- ToolBench: https://github.com/OpenBMB/ToolBench
- StableToolBench: https://github.com/THUNLP-MT/StableToolBench
- RAG-MCP: https://arxiv.org/abs/2505.03275
- Scalable LLM Agent Tool Access in the Cloud: https://arxiv.org/abs/2607.15593

## Relationship to MVCA

The intended transfer target is an eventual research candidate such as:

~~~text
Qualified Tool Warehouse
        |
        v
Active Tool Surface Governor
        |
        | bounded, evidence-selected projection
        v
Task / Worker
~~~

The central MVCA-facing invariant is:

~~~text
Capability Warehouse Size != Active Tool Surface Size
Tool Surface Optimization != Authority Optimization
~~~

A smaller visible surface must never silently widen authority, hide mandatory gates, or convert retrieval confidence into execution permission.

## Current phase

**Phase 0 — research constitution and benchmark design.**

No headline empirical claim is frozen yet.

The first implementation target is **E00: a deterministic synthetic registry generator** with controlled semantic overlap and reproducible ground truth.
