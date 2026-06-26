"""Core oracle primitives for the HEROIC SETS / dichromatic problem
(arXiv:2009.13319, Aboulker, Charbit, Naserasr — "Extension of the
Gyarfas-Sumner conjecture to digraphs", Problem 1.2).

Definitions used by the paper:
  * A *digraph* D = (V, A) may have digons (both (u,v) and (v,u)).  A *digon*
    is the pair {(u,v),(v,u)}; the symmetric K2 (written K2sym) is the digraph
    on 2 vertices with a digon.  An *oriented graph* is a digon-free digraph.
  * The *dichromatic number* chi_d(D) = least k such that V(D) partitions into
    k sets, each inducing an ACYCLIC (no directed cycle) subdigraph.  A digon
    is a directed 2-cycle, so the two endpoints of a digon must get different
    colours -- chi_d generalises the chromatic number.
  * For a finite set F of digraphs, Forb_ind(F) is the class of digraphs with
    no member of F as an INDUCED subdigraph.  F is *heroic* iff Forb_ind(F) has
    bounded dichromatic number.
  * C_k(D_1,...,D_k): substitute digraph D_i into vertex i of the directed
    cycle C_k.  Thm 2.1: chi_d(C_k(D_1,...,D_k)) computed via the substitution
    identity; the tower D_1 = K1, D_k = C3(D_{k-1}, D_{k-1}, K1) has
    chi_d(D_k) = k  (unbounded dichromatic number certificate).

EXACT invariants are delegated to the shared, battle-tested library
engine/lib/digraph_core.py (dichromatic_number / is_k_dicolourable via SAT +
lazy directed-cycle clauses; is_oriented; is_triangle_free; triangle_free_graphs
via nauty geng; all_orientations).  This module adds the heroic-set machinery:
small named forbidden digraphs, INDUCED-subdigraph containment, the C_k
substitution composition, and the tournament tower.

A digraph is represented as (n, arcs) with arcs a list/iterable of (u, v) over
vertices 0..n-1.  All values returned here are EXACT (no heuristics).
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
k4_free_graphs = dc.k4_free_graphs
all_orientations = dc.all_orientations


# --------------------------------------------------------------------------- #
#  Named small digraphs  (each returned as (n, arcs))
# --------------------------------------------------------------------------- #

def K1():
    """Single vertex."""
    return 1, []


def K2sym():
    """Symmetric K2: the digon {(0,1),(1,0)}."""
    return 2, [(0, 1), (1, 0)]


def K2sym_bar():
    """Complement of K2sym = independent pair (two vertices, no arc)."""
    return 2, []


def C3():
    """Directed triangle (directed 3-cycle) 0->1->2->0."""
    return 3, [(0, 1), (1, 2), (2, 0)]


def P_plus(k):
    """Directed path P+(k): k arcs, k+1 vertices, 0->1->...->k.

    P+(3) (the paper's induced obstruction in Thm 6.5) has 4 vertices and the
    3 arcs (0,1),(1,2),(2,3)."""
    return k + 1, [(i, i + 1) for i in range(k)]


def directed_cycle(k):
    """Directed cycle C_k: 0->1->...->(k-1)->0."""
    return k, [(i, (i + 1) % k) for i in range(k)]


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
    hverts = list(range(hn))
    for perm in itertools.permutations(range(n), hn):
        ok = True
        for a in range(hn):
            for b in range(hn):
                if a == b:
                    continue
                in_h = (a, b) in Hset
                in_d = (perm[a], perm[b]) in Aset
                if in_h != in_d:
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
    """True iff D contains NO member of the family F (list of (n,arcs)) as an
    induced subdigraph -- i.e. D is in Forb_ind(F)."""
    return not any(contains_induced(D, H) for H in F)


# --------------------------------------------------------------------------- #
#  Substitution / composition  C_k(D_1,...,D_k)   (Thm 2.1)
# --------------------------------------------------------------------------- #

def substitute_into_cycle(parts):
    """C_k(D_1,...,D_k): take the directed cycle on k 'super-vertices'; replace
    super-vertex i by a disjoint copy of D_i = (n_i, arcs_i); for the cycle arc
    i -> (i+1 mod k), put ALL arcs from every vertex of copy i to every vertex
    of copy (i+1 mod k).  Returns (N, arcs).

    This is the standard substitution used in arXiv:2009.13319 (and Berger et
    al.).  `parts` is the ordered list [D_1,...,D_k]."""
    k = len(parts)
    offsets = []
    off = 0
    for (ni, _) in parts:
        offsets.append(off)
        off += ni
    N = off
    arcs = []
    # internal arcs of each part
    for i, (ni, ai) in enumerate(parts):
        base = offsets[i]
        for (u, v) in ai:
            arcs.append((base + u, base + v))
    # complete-arc bundles along each cycle arc i -> (i+1)
    for i in range(k):
        j = (i + 1) % k
        bi, ni = offsets[i], parts[i][0]
        bj, nj = offsets[j], parts[j][0]
        for u in range(ni):
            for v in range(nj):
                arcs.append((bi + u, bj + v))
    return N, arcs


def C3_compose(D1, D2, D3):
    """C3(D1,D2,D3) shorthand."""
    return substitute_into_cycle([D1, D2, D3])


def tournament_tower(k):
    """The tower D_1 = K1, D_m = C3(D_{m-1}, D_{m-1}, K1).

    Thm 2.1 corollary: chi_d(D_k) = k, giving an explicit family of tournaments
    with unbounded dichromatic number.  Returns (n, arcs) for D_k."""
    D = K1()
    if k <= 1:
        return D
    for _ in range(2, k + 1):
        D = C3_compose(D, D, K1())
    return D


# --------------------------------------------------------------------------- #
#  Enumeration helpers for sweeping Forb_ind(F)
# --------------------------------------------------------------------------- #

def oriented_triangle_free_digraphs(n):
    """Yield every oriented (digon-free) triangle-free digraph on n vertices,
    as (n, arcs): all orientations of every triangle-free simple graph (one per
    iso class from geng -t).  Small n only (2^|E| per graph)."""
    for (gn, edges) in triangle_free_graphs(n):
        for arcs in all_orientations(edges):
            yield (n, arcs)


def oriented_k4_free_digraphs(n):
    """Yield every oriented (digon-free) K4-free digraph on n vertices,
    as (n, arcs): all orientations of every K4-free simple graph (one per
    iso class from geng -k).  Small n only (2^|E| per graph)."""
    for (gn, edges) in k4_free_graphs(n):
        for arcs in all_orientations(edges):
            yield (n, arcs)
