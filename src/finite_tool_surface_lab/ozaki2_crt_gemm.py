from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import Iterable


Matrix = list[list[int]]


@dataclass(frozen=True)
class Ozaki2ToyResult:
    moduli: tuple[int, ...]
    modulus_product: int
    low_precision_gemm_count: int
    exact: Matrix
    reconstructed: Matrix
    uniqueness_condition_holds: bool
    exact_match: bool


def _shape(a: Matrix) -> tuple[int,int]:
    if not isinstance(a,list) or not a or not all(isinstance(r,list) and r for r in a):
        raise ValueError("matrix_invalid")
    n=len(a[0])
    if any(len(r)!=n for r in a):
        raise ValueError("matrix_ragged")
    if any(type(x) is not int for r in a for x in r):
        raise ValueError("matrix_non_integer")
    return len(a),n


def matmul_int(a: Matrix,b: Matrix)->Matrix:
    m,k=_shape(a)
    kb,n=_shape(b)
    if k!=kb:
        raise ValueError("shape_mismatch")
    return [[sum(a[i][t]*b[t][j] for t in range(k)) for j in range(n)] for i in range(m)]


def _validate_moduli(moduli: Iterable[int])->tuple[int,...]:
    mods=tuple(moduli)
    if not mods:
        raise ValueError("moduli_empty")
    for p in mods:
        if type(p) is not int or not 3<=p<=255:
            raise ValueError("modulus_out_of_int8_centered_range")
    for i,p in enumerate(mods):
        for q in mods[i+1:]:
            if gcd(p,q)!=1:
                raise ValueError("moduli_not_pairwise_coprime")
    return mods


def centered_residue(x:int,p:int)->int:
    r=x%p
    if r>p//2:
        r-=p
    if not -128<=r<=127:
        raise ValueError("centered_residue_not_int8")
    return r


def residue_gemm(a:Matrix,b:Matrix,p:int)->Matrix:
    # Simulates INT8 inputs with exact wide accumulation, then reduces mod p.
    ar=[[centered_residue(x,p) for x in row] for row in a]
    br=[[centered_residue(x,p) for x in row] for row in b]
    raw=matmul_int(ar,br)
    return [[x%p for x in row] for row in raw]


def crt_centered(residues:Iterable[int],moduli:Iterable[int])->int:
    mods=_validate_moduli(moduli)
    rem=tuple(residues)
    if len(rem)!=len(mods):
        raise ValueError("residue_count_mismatch")
    P=1
    for p in mods:
        P*=p
    x=0
    for r,p in zip(rem,mods):
        Mi=P//p
        inv=pow(Mi,-1,p)
        x=(x+(r%p)*Mi*inv)%P
    if x>P//2:
        x-=P
    return x


def ozaki2_integer_core(a:Matrix,b:Matrix,moduli:Iterable[int]=(127,125,121))->Ozaki2ToyResult:
    mods=_validate_moduli(moduli)
    exact=matmul_int(a,b)
    residues=[residue_gemm(a,b,p) for p in mods]
    m,n=_shape(exact)
    reconstructed=[
        [crt_centered((residues[t][i][j] for t in range(len(mods))),mods) for j in range(n)]
        for i in range(m)
    ]
    P=1
    for p in mods:
        P*=p
    bound=max(abs(x) for row in exact for x in row)
    unique=2*bound<P
    return Ozaki2ToyResult(
        moduli=mods,
        modulus_product=P,
        low_precision_gemm_count=len(mods),
        exact=exact,
        reconstructed=reconstructed,
        uniqueness_condition_holds=unique,
        exact_match=reconstructed==exact,
    )
