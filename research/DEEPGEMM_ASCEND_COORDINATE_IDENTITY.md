# DGASC-001 — DeepGEMM-Ascend Coordinate Identity Catfood

Date: 2026-10-02

Primary source:
- deepseek-ai/DeepGEMM-Ascend README, inspected at README blob `168834134584b2b0b0aaf44cd9cc240d1805453e`
- https://github.com/deepseek-ai/DeepGEMM-Ascend/blob/main/README.md

## Source atoms

The project states that DeepGEMM-Ascend is API-compatible with upstream DeepGEMM while targeting Huawei Ascend 950. It supports BF16, FP8 and FP4 GEMM plus MQA logits and MegaMoE.

The same README also states that the scaling-factor representation differs from NVIDIA: on Ascend, each pair of UE8M0 scaling factors along K is packed into an int16 and stored in MN-major order. The library exposes explicit scale-layout transformation helpers.

Therefore:

```
outer API equality
!=
internal coordinate identity
```

A compatibility layer that keys only on logical API + dtype can collapse two physically different representations into one coordinate.

## KITten-Coordinate implication

This is a concrete representation-aliasing case for the Ozaki-derived Coordinate Circuit.

Naive coordinate:

```
(deep_gemm.fp8_gemm, FP8)
```

is insufficient across backends.

Representation-aware coordinate:

```
(
  outer_api,
  dtype,
  backend,
  scale_encoding,
  scale_layout,
)
```

separates the channels before deterministic composition.

This is structurally similar to the CRT uniqueness lesson: if the coordinate basis cannot distinguish states that matter to reconstruction, the representation is not safe merely because every local channel is internally valid.

## Minimal probe

`coordinate_identity.py` encodes:
- a backend-blind `naive_surface_key`;
- a representation-aware `coordinate_signature`;
- `representation_alias_risk(a, b)`.

The test constructs NVIDIA-native and Ascend-specific profiles with the same logical DeepGEMM FP8 outer surface. They collide under the naive key and separate under the coordinate signature.

## Claim ceiling

This is a representation/typing probe only.
It does not benchmark Ascend hardware, reproduce DeepGEMM kernels, or claim numerical equivalence between backends.

Catfood verdict: **KEEP the atom; do not import the hardware library.**
