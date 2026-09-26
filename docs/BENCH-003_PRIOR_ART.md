# BENCH-003 Prior-Art Map

This file separates source observations from Catfood inference.

## ToolChoiceConfusion / CMTF

Source:
- arXiv:2606.06284
- https://arxiv.org/abs/2606.06284

SOURCE OBSERVATION:
The paper argues that semantic relevance is insufficient for Tool exposure: a Tool can be related to the task but unnecessary or premature at the current step. It evaluates wrong-tool calls, premature actions, Tool exposure, task success, and token cost.

CATFOOD INFERENCE:
BENCH-003 should separate semantic proximity from state validity.

~~~text
Semantically Relevant
!= State-Appropriate
~~~

## ToolMenuBench

Sources:
- arXiv:2606.15508
- https://arxiv.org/abs/2606.15508
- https://github.com/R-Suresh/ToolMenuBench

SOURCE OBSERVATION:
The public repository exposes mixed, schema-compatible, risky, cross-domain, semantic, near-duplicate, and premature distractor conditions. Its runner explicitly tags generated distractors and measures visible Tool count, wrong-tool calls, premature actions, risky exposure, task success, and token usage.

CATFOOD INFERENCE:
Distractor type should be a first-class experimental factor rather than one similarity score. BENCH-003 borrows this direction but decomposes it into primitive axes.

## MCPAgentBench

Sources:
- arXiv:2512.24565
- https://arxiv.org/abs/2512.24565
- https://github.com/Brunestuder/MCPAgentBench

SOURCE OBSERVATION:
MCPAgentBench uses real-world MCP definitions, authentic tasks, simulated MCP Tools, and dynamic candidate lists containing distractors. It evaluates completion and efficiency across several Tool-use structures.

CATFOOD INFERENCE:
A later external-validity lane should use real Tool-catalogue structure rather than synthetic distractors alone.

## pmndrs/math DOGFOOD-001

Internal public research observation:
- pinned package math@0.1.0;
- aliases exist;
- repeated operation names across vec2/vec3/vec4 create natural cross-type homonyms;
- near operations create plausible hard negatives.

CATFOOD INFERENCE:
It is a useful candidate external catalogue for equivalence/homonym stress, but must first pass VAL-002 deterministic adapter qualification.

## Distinctive BENCH-003 contribution

~~~text
Wrong Distractor
!= Valid Equivalent Alternative
~~~

BENCH-003 evaluates both while keeping total menu size fixed in matched synthetic interventions.
