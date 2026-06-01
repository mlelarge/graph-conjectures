"""Efficient exact degreewidth solver for tournaments (D92, Q1 tooling).

Δ*(T) = degreewidth = min over vertex orderings of the maximum back-degree
(number of back-arcs incident to a vertex; a back-arc is an arc u->v with
v placed before u).

KEY OBSERVATION (makes a Held-Karp subset DP work).  Build the order left
to right.  When vertex v is *appended* to a prefix occupying the set S
(v not in S), every other vertex is decided: those in S are *before* v,
those outside S∪{v} are *after* v.  Hence v's back-degree is FULLY known
at placement time:

    bd(v | before = S) = |N+(v) ∩ S|              (out-arcs to earlier vtx)
                       + |N-(v) ∩ (V∖S∖{v})|       (in-arcs from later vtx)

It never changes afterward.  So with f[S] = min over linear arrangements
of S (as a prefix) of the max back-degree among S's vertices,

    f[∅] = 0,
    f[S] = min_{v∈S} max( f[S∖{v}],  bd(v | S∖{v}) ),
    Δ*(T) = f[V].

This is O(2^n · n) time, O(2^n) space (using a rolling/bitmask layout),
versus the O(n!·n^2) permutation scan in degreewidth_decomposition.py.
Practical to ~n=22 exact; the boolean ≤k reachability variant a bit more.

NB the *general* NP-hardness of computing degreewidth (Davot, Isenmann, Roy & Thiebaut,
arXiv:2212.06007) is not contradicted: this is exponential, just a much
better exponential, and is a data-gathering tool — not a poly algorithm
for Q1.
"""
from __future__ import annotations

from typing import Sequence


def _masks(T: Sequence[Sequence[int]]):
    """Return (outmask, inmask, dminus) as bitmask arrays over vertices."""
    n = len(T)
    outmask = [0] * n
    inmask = [0] * n
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            if T[u][v]:
                outmask[u] |= 1 << v
            else:  # tournament: exactly one of T[u][v], T[v][u]
                inmask[u] |= 1 << v
    dminus = [bin(inmask[u]).count("1") for u in range(n)]
    return outmask, inmask, dminus


def degreewidth(T: Sequence[Sequence[int]]) -> int:
    """Exact Δ*(T) by the Held-Karp subset DP.  O(2^n · n)."""
    n = len(T)
    if n <= 1:
        return 0
    outmask, inmask, dminus = _masks(T)
    full = (1 << n) - 1
    NEG = -1
    f = [NEG] * (1 << n)
    f[0] = 0
    for S in range(1, 1 << n):
        best = n  # upper bound on any back-degree
        rem = S
        while rem:
            vb = rem & (-rem)
            v = vb.bit_length() - 1
            rem ^= vb
            prev = S ^ vb  # S without v  (the "before" set)
            fprev = f[prev]
            if fprev == NEG:
                continue
            before_in = bin(inmask[v] & prev).count("1")
            bd = bin(outmask[v] & prev).count("1") + (dminus[v] - before_in)
            cand = bd if bd > fprev else fprev
            if cand < best:
                best = cand
        f[S] = best
    return f[full]


def degreewidth_le(T: Sequence[Sequence[int]], k: int) -> bool:
    """Decide Δ*(T) ≤ k via boolean reachability DP (degree-feasibility).

    reach[S] = some arrangement of S as a prefix gives every vertex of S
    back-degree ≤ k.  Δ*≤k iff reach[V].  Prunes hard at small k.
    """
    n = len(T)
    if n <= 1:
        return True
    outmask, inmask, dminus = _masks(T)
    full = (1 << n) - 1
    reach = bytearray(1 << n)
    reach[0] = 1
    for S in range(1, 1 << n):
        rem = S
        ok = 0
        while rem:
            vb = rem & (-rem)
            v = vb.bit_length() - 1
            rem ^= vb
            prev = S ^ vb
            if not reach[prev]:
                continue
            before_in = bin(inmask[v] & prev).count("1")
            bd = bin(outmask[v] & prev).count("1") + (dminus[v] - before_in)
            if bd <= k:
                ok = 1
                break
        reach[S] = ok
    return bool(reach[full])


def is_degreewidth_le2(T: Sequence[Sequence[int]]) -> bool:
    """Δ*(T) ≤ 2 — the Path-FAS degree-feasibility gate (Q1)."""
    return degreewidth_le(T, 2)


def degreewidth_order(T: Sequence[Sequence[int]]) -> tuple[int, list[int]]:
    """Exact Δ*(T) and a witnessing order achieving it (for inspection)."""
    n = len(T)
    if n <= 1:
        return 0, list(range(n))
    outmask, inmask, dminus = _masks(T)
    full = (1 << n) - 1
    NEG = -1
    f = [NEG] * (1 << n)
    choice = [-1] * (1 << n)
    f[0] = 0
    for S in range(1, 1 << n):
        best = n
        bestv = -1
        rem = S
        while rem:
            vb = rem & (-rem)
            v = vb.bit_length() - 1
            rem ^= vb
            prev = S ^ vb
            fprev = f[prev]
            if fprev == NEG:
                continue
            before_in = bin(inmask[v] & prev).count("1")
            bd = bin(outmask[v] & prev).count("1") + (dminus[v] - before_in)
            cand = bd if bd > fprev else fprev
            if cand < best:
                best = cand
                bestv = v
        f[S] = best
        choice[S] = bestv
    # reconstruct (vertices appended last->first)
    order_rev = []
    S = full
    while S:
        v = choice[S]
        order_rev.append(v)
        S ^= (1 << v)
    return f[full], order_rev[::-1]


if __name__ == "__main__":
    # tiny self-check on the 3-cycle (Δ*=1) and transitive (Δ*=0)
    cyc = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
    trans = [[0, 1, 1], [0, 0, 1], [0, 0, 0]]
    print("3-cycle Δ* =", degreewidth(cyc), "(expect 1)")
    print("transitive Δ* =", degreewidth(trans), "(expect 0)")
    print("3-cycle ≤2:", is_degreewidth_le2(cyc), " ≤1:", degreewidth_le(cyc, 1))
