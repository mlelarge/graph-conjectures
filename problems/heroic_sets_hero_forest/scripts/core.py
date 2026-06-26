r"""Core oracle primitives for the HERO + ORIENTED-FOREST heroic-set conjecture
(arXiv:2009.13319, Aboulker, Charbit, Naserasr -- "Extension of the
Gyarfas-Sumner conjecture to digraphs"), CONJECTURE 4.2 and its concrete
Section-6 sub-cases (Theorem 6.1 and Conjecture 6.2).

THE CONJECTURE (4.2).  Let H be a hero and F an oriented forest.  The set
{ K2_digon , H , F } is *heroic* (i.e. Forb_ind of it has BOUNDED dichromatic
number) if and only if either F is a disjoint union of oriented stars, OR H is a
transitive tournament.  The "only if" direction is proved in the paper; the "if"
direction with both conditions failing is the open content, and the smallest
concrete positive sub-cases are settled / conjectured in Section 6 with H = C3:

  * Theorem 6.1 (PROVED, EXACT):  chi_d( Forb_ind( K2_digon, ->C3, ->K2+K1 ) ) = 2.
  * Conjecture 6.2 (OPEN):        chi_d( Forb_ind( K2_digon, ->C3, S2+ ) )     = 2.

Definitions used by the paper (verified against Refs/heroic_2009.13319.pdf, Sec 6):
  * K2_digon  (the paper's \overleftrightarrow{K_2}): 2 vertices with a digon
    {(0,1),(1,0)}.  Forbidding it as induced subdigraph == being an ORIENTED
    graph (no 2-cycle).
  * ->C3      (\overrightarrow{C_3}): the directed triangle 0->1->2->0.
    Forbidding it (+ digon) over a triangle-free underlying graph == no directed
    triangle.  Combined with K3 (the symmetric/undirected triangle) one gets the
    class of triangle-free oriented graphs.
  * ->K2+K1   (\overrightarrow{K_2}+K_1): the disjoint union of a single ARC and
    an isolated vertex -- 3 vertices, arc set {(0,1)}, vertex 2 isolated.  The
    paper's proof of Thm 6.1 hinges on: an oriented graph with no induced
    ->K2+K1 has the property that the non-neighbours of every vertex form an
    independent set, i.e. it is an orientation of a complete multipartite graph.
  * S2+ : the oriented star with two OUTGOING arcs from the centre -- 3 vertices,
    arcs {(0,1),(0,2)} (centre 0).
  * S2- : the oriented star with two INGOING arcs to the centre -- 3 vertices,
    arcs {(1,0),(2,0)} (centre 0).
  * P+(k): directed path of length k -- k+1 vertices, arcs (i,i+1).

A *hero* is a tournament H such that {K2_digon, K2_indep, H} is heroic; by the
Berger et al. theorem (cited in the paper) the heroes are exactly the tournaments
built from K1 by H1=>H2 (domination join) and the C3(H,TTk,K1)/C3(TTk,H,K1) rules.
An *oriented forest* is an orientation of a forest; a *union of oriented stars*
is an oriented forest each of whose components has at most one vertex of degree>1.

EXACT invariants (dichromatic number, oriented/triangle-free tests, geng
enumeration, all orientations) are delegated to the shared, battle-tested library
engine/lib/digraph_core.py.  This module adds the hero-forest machinery:
named small forbidden digraphs, INDUCED-subdigraph containment, the substitution
composition C_k(...), the hero / oriented-star classifiers, and enumeration of
the relevant Forb_ind classes.

A digraph is (n, arcs) with arcs a list of (u,v) over vertices 0..n-1.  All
values returned here are EXACT (no heuristics).
"""
from __future__ import annotations

import itertools
import os
import sys

# Make the shared exact library importable (path relative to this file so the
# module imports from a fresh clone in any location).
_ENGINE_LIB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine", "lib")
if _ENGINE_LIB not in sys.path:
    sys.path.insert(0, _ENGINE_LIB)

import digraph_core as dc  # noqa: E402

# Re-export the exact primitives so callers can `import core`.
acyclic_number = dc.acyclic_number
dichromatic_number = dc.dichromatic_number
is_k_dicolourable = dc.is_k_dicolourable
is_oriented = dc.is_oriented
is_triangle_free = dc.is_triangle_free
is_acyclic = dc.is_acyclic
triangle_free_graphs = dc.triangle_free_graphs
all_orientations = dc.all_orientations


# --------------------------------------------------------------------------- #
#  Named small digraphs  (each returned as (n, arcs))
# --------------------------------------------------------------------------- #

def K1():
    """Single vertex."""
    return 1, []


def K2_digon():
    """The paper's \\overleftrightarrow{K_2}: the digon {(0,1),(1,0)}.
    Forbidding it induced == being an oriented graph."""
    return 2, [(0, 1), (1, 0)]


def C3():
    """\\overrightarrow{C_3}: directed triangle 0->1->2->0."""
    return 3, [(0, 1), (1, 2), (2, 0)]


def arrowK2_plus_K1():
    """\\overrightarrow{K_2}+K_1: a single arc (0->1) plus an isolated vertex 2.
    3 vertices, arc set {(0,1)}.  (Third member of Theorem 6.1's heroic set.)"""
    return 3, [(0, 1)]


def S2_plus():
    """S2+: oriented star, two OUTGOING arcs from centre 0 -> {1,2}."""
    return 3, [(0, 1), (0, 2)]


def S2_minus():
    """S2-: oriented star, two INGOING arcs {1,2} -> centre 0."""
    return 3, [(1, 0), (2, 0)]


def P_plus(k):
    """Directed path P+(k): k arcs, k+1 vertices, 0->1->...->k.
    P+(2) = the directed path of length 2 (3 vertices)."""
    return k + 1, [(i, i + 1) for i in range(k)]


def directed_cycle(k):
    """Directed cycle C_k: 0->1->...->(k-1)->0."""
    return k, [(i, (i + 1) % k) for i in range(k)]


def transitive_tournament(k):
    """TT_k: vertices 0..k-1, arc i->j for i<j."""
    return k, [(i, j) for i in range(k) for j in range(i + 1, k)]


# --------------------------------------------------------------------------- #
#  Induced subdigraph containment  (EXACT, by injective embedding search)
# --------------------------------------------------------------------------- #

def contains_induced(D, H):
    """True iff H = (hn, harcs) occurs as an INDUCED subdigraph of D=(n,arcs).

    Induced: there is an injection f: V(H) -> V(D) such that for ALL ordered
    pairs (i,j), i!=j:  (i,j) in A(H)  <=>  (f(i),f(j)) in A(D).
    Exact brute force over injections (the H's of interest have <=4 vertices)."""
    n, arcs = D
    hn, harcs = H
    if hn > n:
        return False
    Aset = set(map(tuple, arcs))
    Hset = set(map(tuple, harcs))
    for perm in itertools.permutations(range(n), hn):
        ok = True
        for a in range(hn):
            for b in range(hn):
                if a == b:
                    continue
                if ((a, b) in Hset) != ((perm[a], perm[b]) in Aset):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return True
    return False


def induced_subdigraph(D, verts):
    """Return (k, arcs) induced by `verts` (a list), relabeled 0..k-1."""
    n, arcs = D
    verts = list(verts)
    relabel = {v: i for i, v in enumerate(verts)}
    vs = set(verts)
    sub = [(relabel[u], relabel[v]) for (u, v) in arcs if u in vs and v in vs]
    return len(verts), sub


def avoids_all(D, F):
    """True iff D contains NO member of family F (list of (n,arcs)) as induced
    subdigraph -- i.e. D is in Forb_ind(F)."""
    return not any(contains_induced(D, H) for H in F)


# --------------------------------------------------------------------------- #
#  Substitution composition  C_k(D_1,...,D_k)  (paper's Thm 2.1)
# --------------------------------------------------------------------------- #

def substitute_into_cycle(parts):
    """C_k(D_1,...,D_k): directed cycle on k super-vertices, super-vertex i
    replaced by a disjoint copy of D_i=(n_i,arcs_i); along cycle arc i->(i+1),
    add EVERY arc from each vertex of copy i to each vertex of copy (i+1)."""
    k = len(parts)
    offsets, off = [], 0
    for (ni, _) in parts:
        offsets.append(off)
        off += ni
    N, arcs = off, []
    for i, (ni, ai) in enumerate(parts):
        base = offsets[i]
        for (u, v) in ai:
            arcs.append((base + u, base + v))
    for i in range(k):
        j = (i + 1) % k
        bi, ni = offsets[i], parts[i][0]
        bj, nj = offsets[j], parts[j][0]
        for u in range(ni):
            for v in range(nj):
                arcs.append((bi + u, bj + v))
    return N, arcs


def C3_compose(D1, D2, D3):
    return substitute_into_cycle([D1, D2, D3])


def tournament_tower(k):
    """Tower D_1=K1, D_m=C3(D_{m-1},D_{m-1},K1).  chi_d(D_k)=k (unbounded
    dichromatic tournaments); used as a finite exact landmark."""
    D = K1()
    for _ in range(2, k + 1):
        D = C3_compose(D, D, K1())
    return D


# --------------------------------------------------------------------------- #
#  Hero / oriented-forest classifiers  (for Conjecture-4.2 dichotomy)
# --------------------------------------------------------------------------- #

def is_tournament(n, arcs):
    """True iff exactly one of (i,j),(j,i) is present for every pair."""
    s = set(map(tuple, arcs))
    for i in range(n):
        for j in range(i + 1, n):
            if ((i, j) in s) == ((j, i) in s):
                return False
    return True


def _underlying(n, arcs):
    import networkx as nx
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from((u, v) for (u, v) in arcs)
    return g


def is_oriented_forest(n, arcs):
    """True iff (n,arcs) is an orientation of a forest (no digon, underlying
    graph acyclic)."""
    if not is_oriented(arcs):
        return False
    import networkx as nx
    g = _underlying(n, arcs)
    return nx.is_forest(g)


def is_disjoint_union_of_oriented_stars(n, arcs):
    """True iff (n,arcs) is an oriented forest whose every connected component is
    a star (<=1 vertex of degree>1).  Equivalent (paper, Sec 6.1) to: an oriented
    forest with no induced P4 in its underlying graph."""
    if not is_oriented_forest(n, arcs):
        return False
    g = _underlying(n, arcs)
    for comp in __import__("networkx").connected_components(g):
        sub = g.subgraph(comp)
        hi = [v for v in comp if sub.degree(v) > 1]
        if len(hi) > 1:
            return False
    return True


# --------------------------------------------------------------------------- #
#  Enumeration of the relevant Forb_ind classes  (small n)
# --------------------------------------------------------------------------- #

def oriented_triangle_free_digraphs(n):
    """Yield every oriented (digon-free) triangle-free digraph on n vertices, as
    (n, arcs): all 2^|E| orientations of every triangle-free simple graph (one
    per ISOMORPHISM class from geng -t).  Small n only.

    NOTE ON COUNTING: this iterates one underlying graph per iso class and ALL of
    its orientations, so the same oriented digraph can appear under different
    underlying-iso reps only if the underlying graph differs (it cannot); but
    distinct labelled orientations of the SAME underlying graph are all yielded
    (orientations are not iso-reduced).  Member COUNTS are therefore
    "iso-classes-of-underlying-graph x orientations", not orientation-iso-classes.
    The dichromatic-number landmarks (max chi_d, first-attained n) are invariant
    under any such convention."""
    for (gn, edges) in triangle_free_graphs(n):
        for arcs in all_orientations(edges):
            yield (n, arcs)
