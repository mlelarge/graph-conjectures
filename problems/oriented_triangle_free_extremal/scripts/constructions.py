"""Explicit oriented-graph families for arXiv:2403.02298.

Each builder returns (n, arcs).  The headline object is D25 (Prop. 4.6), the
5-backward-blowup of the directed 5-cycle: a 3-dicritical oriented triangle-free
graph on 25 vertices, the witness for m(3) <= 25.  The general
`backward_blowup_directed_cycle(ell, m)` is the family the paper generalises
("the ell-backward-blowup of C_ell is not 2-dicolourable for every odd ell"),
so the agent can explore it.  Paley / transitive / directed-cycle builders exist
to validate the exact solvers against the paper's known small values.
"""
from __future__ import annotations

import random


def transitive_tournament(n):
    """TT_n: arc i->j for i<j.  Acyclic, chi_vec=1, alpha_vec=n."""
    return n, [(i, j) for i in range(n) for j in range(i + 1, n)]


def directed_cycle(n):
    """The directed n-cycle 0->1->...->(n-1)->0."""
    return n, [(i, (i + 1) % n) for i in range(n)]


def paley_tournament(q):
    """Paley tournament P_q for prime q == 3 (mod 4): arc i->j iff (i-j) is a
    nonzero quadratic residue mod q.  (Paper: smallest 3-dichromatic = P_7,
    smallest 4-dichromatic = P_11.)"""
    if q % 4 != 3:
        raise ValueError("Paley tournament needs q == 3 (mod 4)")
    qr = {(x * x) % q for x in range(1, q)}
    arcs = [(i, j) for i in range(q) for j in range(q)
            if i != j and ((i - j) % q) in qr]
    return q, arcs


def backward_blowup_directed_cycle(ell, m):
    """The m-backward-blowup of the directed cycle C_ell.

    Vertices u_{i,j}, i in [ell] (cyclic), j in [m], indexed v = i*m + j.
    Forward arcs  u_{i,j} -> u_{i+1,j'}  for j != j'   (between consecutive packs,
    different columns); backward arcs  u_{i+1,j} -> u_{i,j}  (same column).
    Underlying graph = C_ell blown up by independent m-sets -> triangle-free.
    For ell = m = 5 this is exactly D25 of Proposition 4.6.
    """
    def vid(i, j):
        return (i % ell) * m + j

    arcs = []
    for i in range(ell):
        for j in range(m):
            for jp in range(m):
                if j != jp:
                    arcs.append((vid(i, j), vid(i + 1, jp)))   # forward
            arcs.append((vid(i + 1, j), vid(i, j)))            # backward (matched)
    return ell * m, arcs


def D25():
    """D25 = C5 <-5, the headline construction (Proposition 4.6)."""
    return backward_blowup_directed_cycle(5, 5)


def pack_coupled_d25_ring(L, out_pack=0, in_pack=2, forward=True):
    """L copies of D25 (=C5<-5) on a directed L-ring, coupled pack-to-pack.

    Copy k occupies vertices [k*25, k*25+25); inside it, pack p is the
    independent 5-set {k*25 + p*5 + j : j in 0..4} (a pack = fixed i in the
    D25 backward-blowup layout, which is independent).  Between consecutive
    copies G_k and G_{k+1 mod L} we add a COMPLETE BIPARTITE oriented interface
    from pack `out_pack` of G_k to pack `in_pack` of G_{k+1}, oriented per
    `forward` (forward: out->in; else in->out).  Independent-set to
    independent-set join keeps it triangle-free; one direction keeps it oriented.
    """
    base_n, base_arcs = D25()  # 25, arcs
    arcs = []
    for k in range(L):
        off = k * 25
        for (u, v) in base_arcs:
            arcs.append((u + off, v + off))
    for k in range(L):
        off_k = k * 25
        off_k1 = ((k + 1) % L) * 25
        out_verts = [off_k + out_pack * 5 + j for j in range(5)]
        in_verts = [off_k1 + in_pack * 5 + j for j in range(5)]
        for u in out_verts:
            for v in in_verts:
                arcs.append((u, v) if forward else (v, u))
    return L * 25, arcs


def random_orientation(n, edges, seed=0):
    """A uniformly random orientation of the given undirected edge list."""
    rng = random.Random(seed)
    arcs = []
    for (u, v) in edges:
        arcs.append((u, v) if rng.random() < 0.5 else (v, u))
    return n, arcs
