# OZAKI2-001 — CRT GEMM Catfood

Primary source inspected: `RIKEN-RCCS/GEMMul8`.

The production code path is explicit:

`A,B -> scaling -> integer extraction -> residue projection -> low-precision GEMMs -> modulo reduction -> CRT reconstruction -> undo scaling`.

The important algorithmic atom is not "INT8 magically becomes FP64". It is:

For pairwise-coprime moduli `p_1,...,p_s`, compute

`C_i = (A mod p_i) @ (B mod p_i) mod p_i`

using a fast low-precision GEMM. CRT reconstructs the unique integer matrix
`C` modulo `P = product(p_i)`. If every true entry lies inside the centered
uniqueness interval `|C_jk| < P/2`, the integer result is recovered exactly.

The floating-point Scheme II surrounds that exact modular core with power-of-two
scaling/extraction and final rescaling. GEMMul8 implements both fast and accurate
scaling paths. The 2026 improved-fast-scaling work derives a scale-invariant
formula from the CRT uniqueness condition.

Catfood conclusion:

- KEEP the "many narrow exact channels + deterministic reconstruction" pattern.
- DO NOT analogize this to majority voting: every residue channel is a necessary
  coordinate of one exact representation.
- Potential finite-ram/tool-surface experiment: compare memory/workspace and
  operation count as the number of moduli grows.
- No GPU or performance claim from this toy.
