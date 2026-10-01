from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import prod
from typing import Iterable

from finite_tool_surface_lab.ozaki2_crt_gemm import crt_centered


@dataclass(frozen=True)
class VoteResult:
    true_votes: int
    false_votes: int
    decision: bool | None
    status: str


def majority_vote(votes: Iterable[bool]) -> VoteResult:
    rows=tuple(votes)
    if not rows:
        raise ValueError("votes_empty")
    if any(type(v) is not bool for v in rows):
        raise ValueError("vote_non_boolean")
    yes=sum(rows)
    no=len(rows)-yes
    if yes==no:
        return VoteResult(yes,no,None,"HOLD_TIE")
    return VoteResult(yes,no,yes>no,"DECIDED")


def encode_coordinates(x:int, moduli:Iterable[int])->tuple[int,...]:
    mods=tuple(moduli)
    if not mods:
        raise ValueError("moduli_empty")
    return tuple(x % p for p in mods)


def exact_coordinate_decode(residues:Iterable[int],moduli:Iterable[int])->int:
    return crt_centered(tuple(residues),tuple(moduli))


@dataclass(frozen=True)
class RedundantDecode:
    value:int | None
    support:int
    total_coordinates:int
    status:str
    candidate_count:int


def redundant_coordinate_decode(
    residues:Iterable[int],
    moduli:Iterable[int],
    *,
    legitimate_bound:int,
    subset_size:int,
    minimum_support:int | None=None,
)->RedundantDecode:
    """Toy RRNS-style consistency decoder.

    It enumerates sufficiently wide coordinate subsets, reconstructs a candidate
    by CRT, then scores each candidate by how many *all* residue coordinates it
    satisfies. This is deliberately small and deterministic; it is not claimed
    to reproduce a production RRNS decoder.
    """
    rem=tuple(residues)
    mods=tuple(moduli)
    if len(rem)!=len(mods) or not rem:
        raise ValueError("coordinate_shape_invalid")
    if type(legitimate_bound) is not int or legitimate_bound<0:
        raise ValueError("legitimate_bound_invalid")
    if type(subset_size) is not int or not 1<=subset_size<=len(mods):
        raise ValueError("subset_size_invalid")
    if minimum_support is None:
        minimum_support=len(mods)-1
    if type(minimum_support) is not int or not 1<=minimum_support<=len(mods):
        raise ValueError("minimum_support_invalid")

    candidates:set[int]=set()
    for idxs in combinations(range(len(mods)),subset_size):
        submods=tuple(mods[i] for i in idxs)
        # A centered reconstruction is unique in [-bound, bound] only when
        # the subset dynamic range exceeds twice the legitimate magnitude.
        if prod(submods) <= 2*legitimate_bound:
            continue
        subrem=tuple(rem[i] for i in idxs)
        x=crt_centered(subrem,submods)
        if abs(x)<=legitimate_bound:
            candidates.add(x)

    if not candidates:
        return RedundantDecode(None,0,len(mods),"HOLD_NO_LEGITIMATE_CANDIDATE",0)

    scored=[]
    for x in sorted(candidates):
        support=sum((x % p)==(r % p) for r,p in zip(rem,mods))
        scored.append((support,x))
    best_support=max(s for s,_ in scored)
    best=[x for s,x in scored if s==best_support]

    if best_support<minimum_support:
        return RedundantDecode(None,best_support,len(mods),"HOLD_INSUFFICIENT_SUPPORT",len(candidates))
    if len(best)!=1:
        return RedundantDecode(None,best_support,len(mods),"HOLD_AMBIGUOUS",len(candidates))
    return RedundantDecode(best[0],best_support,len(mods),"CORRECTED_OR_VERIFIED",len(candidates))


@dataclass(frozen=True)
class CircuitComparison:
    vote_status:str
    vote_value:bool | None
    coordinate_exact_value:int
    coordinate_corrupt_value:int
    redundant_value:int | None
    redundant_status:str


def demo_two_circuits()->CircuitComparison:
    # Circuit A: five weak agents all answer the same binary question.
    vote=majority_vote((True,True,True,False,False))

    # Circuit B: four agents/channels each return a different exact coordinate
    # of one latent integer. One coordinate is then deliberately corrupted.
    x=321
    mods=(127,125,121,119)
    good=encode_coordinates(x,mods)
    corrupt=list(good)
    corrupt[1]=(corrupt[1]+1)%mods[1]

    exact=exact_coordinate_decode(good[:3],mods[:3])
    bad=exact_coordinate_decode(corrupt[:3],mods[:3])
    repaired=redundant_coordinate_decode(
        corrupt,mods,legitimate_bound=1000,subset_size=3,minimum_support=3
    )
    return CircuitComparison(
        vote_status=vote.status,
        vote_value=vote.decision,
        coordinate_exact_value=exact,
        coordinate_corrupt_value=bad,
        redundant_value=repaired.value,
        redundant_status=repaired.status,
    )
