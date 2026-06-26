"""Explicit tournament families for arXiv:2310.04265, Conjecture 3.12.

The headline objects (Aboulker-Aubian-Charbit-Lopes):

  Delta(A, B, C)  -- substitution of tournaments A, B, C into the directed
                     triangle C3 (the cyclic 3-tournament on parts P_A, P_B, P_C
                     with all arcs P_A -> P_B, P_B -> P_C, P_C -> P_A).
                     Internally each part keeps its own arcs.

  S_1 = single vertex (TT1);   S_k = Delta(1, S_{k-1}, S_{k-1}).
        Paper: chiVec(S_k) = k,  S_k in {TT1, TT2, C3}-substitution closure,
        and (for k>=2) twin-width(S_k) = 1.
        omegaVec known only for k<=4: omegaVec(S_1..S_4) = 1,2,2,3.

  S~_1 = single vertex;   S~_n = Delta(S~_{n-1}, S~_{n-1}, S~_{n-1}).
        Paper: twin-width(S~_n) = 1 and omegaVec(S~_n) >= n.

Each builder returns (n, arcs); vertices 0..n-1, arcs a list of (u,v) meaning u->v.
"""
from __future__ import annotations


def single_vertex():
    return 1, []


def transitive_tournament(n):
    """TT_n: arc i->j for i<j.  Acyclic; chiVec=1, omegaVec=1."""
    return n, [(i, j) for i in range(n) for j in range(i + 1, n)]


def directed_triangle():
    """C3: 0->1->2->0."""
    return 3, [(0, 1), (1, 2), (2, 0)]


def substitute_into_C3(A, B, C):
    """Delta(A, B, C): substitute the three tournaments into the directed
    triangle.  Part order on the cyclic triangle is A -> B -> C -> A, i.e. every
    vertex of A beats every vertex of B, every vertex of B beats every vertex of
    C, every vertex of C beats every vertex of A.  Internal arcs are preserved.
    """
    (na, aa), (nb, ab), (nc, ac) = A, B, C
    offA, offB, offC = 0, na, na + nb
    n = na + nb + nc
    arcs = []
    arcs += [(offA + u, offA + v) for (u, v) in aa]
    arcs += [(offB + u, offB + v) for (u, v) in ab]
    arcs += [(offC + u, offC + v) for (u, v) in ac]
    # A -> B
    for u in range(na):
        for v in range(nb):
            arcs.append((offA + u, offB + v))
    # B -> C
    for u in range(nb):
        for v in range(nc):
            arcs.append((offB + u, offC + v))
    # C -> A
    for u in range(nc):
        for v in range(na):
            arcs.append((offC + u, offA + v))
    return n, arcs


def S(k):
    """S_1 = single vertex;  S_k = Delta(1, S_{k-1}, S_{k-1}).  chiVec(S_k)=k."""
    if k <= 1:
        return single_vertex()
    sub = S(k - 1)
    return substitute_into_C3(single_vertex(), sub, sub)


def D(n):
    """D_1 = single vertex;  D_n = Delta(D_{n-1}, D_{n-1}, D_1).

    The 'D_n' substitution tower of arXiv:2602.09863 (Charbit-Aubian et al.,
    "Characterizing Large Clique Number in Tournaments"), per the recursion
    stated in the proposal under test:  D_n = Delta(D_{n-1}, D_{n-1}, D_1),
    D_1 = single vertex.  The paper (NEEDS-VERIFICATION: PDF absent from Refs/)
    claims omega-arrow(D_n) >= log_9 n.  Sizes: |D_n| = 2|D_{n-1}| + 1, so
    |D_1..|=1,3,7,15,31,63,...  This recursion is exactly the proposal's; the
    arc-direction convention is whatever substitute_into_C3 fixes (provisional).
    """
    if n <= 1:
        return single_vertex()
    sub = D(n - 1)
    return substitute_into_C3(sub, sub, single_vertex())


def R(k):
    """R_1 = single vertex;  R_k = Delta(R_{k-1}, TT_{k-1}, R_{k-1}).

    Proposal under test: a NEW C3-substitution tower whose MIDDLE branch is a
    transitive (acyclic) block TT_{k-1} instead of a recursive copy, keeping two
    recursive branches (to climb chiVec) while trying to SUPPRESS the omegaVec
    lift.  Sizes |R_k| = 2|R_{k-1}| + (k-1), giving 1,3,8,19,42,89,...
    """
    if k <= 1:
        return single_vertex()
    sub = R(k - 1)
    return substitute_into_C3(sub, transitive_tournament(k - 1), sub)


def S_tilde(m):
    """S~_1 = single vertex;  S~_m = Delta(S~_{m-1}, S~_{m-1}, S~_{m-1}).
    twin-width 1; omegaVec(S~_m) >= m."""
    if m <= 1:
        return single_vertex()
    sub = S_tilde(m - 1)
    return substitute_into_C3(sub, sub, sub)
