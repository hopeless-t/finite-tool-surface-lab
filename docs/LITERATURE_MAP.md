# Literature Map

This file tracks:

```text
SOURCE
OBSERVATION
INFERENCE
EXPERIMENT IMPACT
```

## Toollery — arXiv:2609.22218

**SOURCE**  
Training-free capability compression using intent-augmented retrieval; evaluated on SkillRouter-scale libraries, BFCL, and another tool workload.

**OBSERVATION**  
Full-library prompting is treated as costly and potentially less reliable; compact top-k candidate sets can preserve useful selection behavior.

**INFERENCE**  
Candidate compression is a viable research object, but fixed top-k alone does not answer how much surface is sufficient.

**EXPERIMENT IMPACT**  
BENCH-001 includes fixed-k baselines; later adaptive policies must compare against them.

## How Many Tools Should an LLM Agent See? — arXiv:2605.24660

**SOURCE**  
Explicitly studies shortlist depth and introduces Bits-over-Random.

**OBSERVATION**  
Fixed shortlist depth can miss harder queries; adaptive depth can expose fewer tools while protecting harder cases.

**INFERENCE**  
Shortlist depth should be a decision variable, not a global constant.

**EXPERIMENT IMPACT**  
BoR becomes a secondary metric. BENCH-002 will study adaptive depth.

## SkillRouter — arXiv:2603.22455

**SOURCE**  
Retrieve-and-rerank evaluation over roughly 80K skills and expert-verified queries.

**OBSERVATION**  
Full skill body can carry routing signal that names/descriptions omit.

**INFERENCE**  
Progressive disclosure may remove information needed for routing.

**EXPERIMENT IMPACT**  
BENCH-004 will perform representation ablation rather than assuming metadata is sufficient.

## ToolBench / StableToolBench

**SOURCE**  
Large-scale tool-use tasks plus later work stabilizing changing/unavailable APIs through simulation/caching.

**OBSERVATION**  
Tool evaluation can be confounded by unstable environments and task solvability.

**INFERENCE**  
Surface policies should not be evaluated only against volatile live APIs.

**EXPERIMENT IMPACT**  
VAL-001 begins with deterministic synthetic fixtures. A later VAL lane will qualify public benchmark adapters.

## RAG-MCP — arXiv:2505.03275

**SOURCE**  
Retrieval-based MCP/tool selection intended to reduce prompt bloat.

**OBSERVATION**  
Moving discovery outside the main LLM context can reduce exposed tool text.

**INFERENCE**  
Prompt reduction and selection quality must be measured separately.

**EXPERIMENT IMPACT**  
Surface bytes/tokens and final selection behavior remain separate metrics.

## Scalable LLM Agent Tool Access in the Cloud — arXiv:2607.15593

**SOURCE**  
Gateway architecture for MCP-scale integration, recommendation, access control, and session-aware routing.

**OBSERVATION**  
Tool recommendation can be a gateway/control-plane concern rather than an LLM-only concern.

**INFERENCE**  
A future MVCA surface governor can remain outside the Worker while preserving independent authority controls.

**EXPERIMENT IMPACT**  
RQ-010 evaluates transfer without collapsing retrieval into authorization.
