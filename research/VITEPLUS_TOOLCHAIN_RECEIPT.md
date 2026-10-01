# VITEPLUS-001 — Compressed surface with inspectable toolchain identity

Date: 2026-10-02

Primary source:
- voidzero-dev/vite-plus README
- inspected README blob: `ad4b16bf8a093b5ae40fff68079b2fda860755dd`
- Vite+ toolchain RFC / implementation discovered in the same repository.

## Source atoms

Vite+ intentionally compresses a multi-tool web-development stack behind one `vp`
entry point. The README lists Vite, Vitest, Oxlint, Oxfmt, Rolldown, tsdown and
Vite Task behind that surface.

Crucially, the compressed surface does not erase component identity:
`vp toolchain` reports the versions and relationships of the bundled tools.
The repository's upgrade documentation also distinguishes package-manager
dependency graphs from code/engines bundled directly into Vite+.

## Catfood atom

```
single entry point
!=
single implementation identity
```

Surface compression is safe to reason about only when the hidden component set
can be read back as a semantic receipt.

A useful receipt coordinate is:

```
(surface_id, sorted[(component_name, component_version)])
```

The same `vp` surface can therefore denote two different implementation states
after an upgrade. A surface-only cache key or evidence record would alias them.

## KITten-Coordinate relation

This is representation aliasing at the tool-surface layer.

Two states may have the same visible coordinate:

```
surface = vp
```

while differing in a hidden coordinate such as the bundled Vite or Rolldown
version. Deterministic reconstruction/debugging needs the component-version
basis when behavior depends on those internals.

## Minimal probe

`toolchain_receipt.py`:
- represents a compressed command surface plus component identities;
- canonicalizes component order;
- computes a semantic SHA-256 receipt;
- flags same-surface/different-toolchain states.

## Claim ceiling

This does not adopt Vite+, benchmark it, or assert that all internal components
must always be surfaced. It extracts the provenance pattern only.

Catfood verdict: **KEEP the receipt atom; no product dependency.**
