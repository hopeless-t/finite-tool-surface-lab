# Metrics

## Retrieval / coverage

Single-tool:
- Hit@k;
- MRR;
- first relevant rank.

Multi-tool:
- Recall@k;
- candidate precision;
- exact gold-set coverage;
- nDCG where graded relevance exists.

Secondary:
- Bits-over-Random where applicable.

## Surface exposure

- visible_tool_count;
- serialized_surface_bytes;
- serialized_surface_tokens;
- mean description length;
- pairwise metadata similarity;
- schema overlap;
- alias/duplicate count.

Token counts are tokenizer-dependent, so bytes and candidate count are always reported too.

## Worker behavior

Conditional on gold presence:
- correct tool selection;
- distractor selection;
- abstention;
- malformed call.

Unconditional:
- end-to-end success;
- false invocation on no-tool tasks;
- unnecessary extra calls;
- repeated/retry loops.

## Cost

- retrieval wall time;
- reranking wall time;
- prompt construction time;
- model latency;
- input/output/cache tokens when observable;
- monetary estimate when applicable.

## Reliability

- seed variance;
- provider/model variance;
- registry-order sensitivity;
- description-order sensitivity;
- drift after registry mutation;
- replay agreement.

## Statistical protocol

Default:
- paired evaluation on identical tasks;
- bootstrap confidence intervals;
- effect sizes with raw distributions;
- multiple-comparison correction when appropriate.

Surface sweeps:
- plot success/coverage against candidate count and serialized exposure;
- test monotonic vs non-monotonic response;
- run change-point analysis only as candidate detection;
- never claim a universal threshold from one registry.

Factor studies:
- factorial or fractional-factorial design;
- report interactions, especially registry-size x overlap and k x overlap.

Expensive Worker runs:
- power analysis first;
- predeclare primary metric and stopping rule;
- never expand sample size only because a preferred result did not appear.
