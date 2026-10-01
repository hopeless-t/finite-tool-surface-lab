# KITTEN-DUAL-001 — Vote vs Exact-Coordinate Circuits

## The distinction

These circuits are not two implementations of the same aggregation rule.

### Statistical vote circuit

Every kitten answers the **same question**:

`Is this hunk unsafe?`

The outputs are redundant estimates of one judgment. Majority/consensus improves
reliability when errors are sufficiently independent, but correlated bias can
produce a confident wrong answer.

### Exact-coordinate circuit

Each kitten/channel returns a **different coordinate** of one latent object:

`x mod p1`, `x mod p2`, `x mod p3`, ...

No coordinate is a vote for the final value. The deterministic combiner needs
all required coordinates to reconstruct the latent value. In CRT, exactness
holds only inside the uniqueness interval.

The production GEMMul8/Ozaki-II analogy is mathematical: each residue GEMM
computes one exact modular coordinate and CRT reconstructs the wide integer
product. This is not majority voting.

## The unexpected third circuit

A plain exact-coordinate circuit is brittle to a corrupted coordinate. Redundant
residue number systems add extra moduli so inconsistency can be detected and,
under bounded-error assumptions, corrected.

The toy in this branch demonstrates:

- 3-of-5 weak votes can still decide the intended Boolean;
- 3 correct CRT coordinates reconstruct x=321 exactly;
- one corrupt coordinate breaks plain CRT;
- adding a fourth redundant coordinate allows a small subset-consistency decoder
  to recover x=321 from one corrupted residue;
- two corrupted coordinates with the frozen support threshold HOLD rather than
  inventing a value.

This toy decoder is intentionally not a production RRNS algorithm.

## Catfood architecture hypothesis

```
semantic/fuzzy domain
    kitten A ─┐
    kitten B ─┼─ statistical review ─→ confidence / HOLD
    kitten C ─┘

exact decomposable domain
    coordinate 1 ─┐
    coordinate 2 ─┼─ deterministic reconstruction ─→ exact object
    coordinate 3 ─┘

hybrid
    voters for coordinate 1 ─→ verified coordinate 1 ─┐
    voters for coordinate 2 ─→ verified coordinate 2 ─┼─ reconstruct
    voters for coordinate 3 ─→ verified coordinate 3 ─┘
```

Potential MVCA targets for exact-coordinate treatment are only fields with
machine-checkable composition rules: hashes, typed receipts, state revisions,
capability-set digests, bounded counters, ledger entries, or independently
verifiable evidence coordinates.

Do **not** pretend fuzzy semantic opinions are exact coordinates merely to use
the prettier combiner.
