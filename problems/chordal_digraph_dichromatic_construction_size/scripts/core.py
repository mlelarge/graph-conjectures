"""Core oracle for the chordal-digraph dichromatic construction-size problem
(arXiv:2202.01006, Aboulker, Bousquet, de Verclos, "Chordal directed graphs
are not directed chi-bounded", Section 3 "Further works").

The class C_3 (the paper's chordal directed graphs):
  * an *oriented* digraph (no digon: never both u->v and v->u), AND
  * NO transitive triangle TT3  (no a,b,c with a->b, b->c, a->c), AND
  * NO induced directed cycle of length >= 4.
Note C_3 ALLOWS the directed triangle C3 (a->b->c->a): that is the unique
oriented triangle that is neither a TT3 nor a long induced dicycle, and it is
G_2 in the paper (dichromatic number 2).

Invariant under study:
  m(k) = minimum order of a digraph in C_3 with dichromatic number >= k.
The paper builds a C_3 digraph of dichromatic number k+1 with size doubly
exponential and asks (Section 3) whether that size can be reduced.  m(k) is the
exact extremal lower handle: any small C_3 witness with chi_vec >= k beats the
construction.

Exact invariants (dichromatic_number via SAT + lazy cycle elimination, and
acyclic_number via MaxSAT) are reused verbatim from the shared library
engine/lib/digraph_core.py.  The C_3 membership test below is a pure
combinatorial check.  Everything is EXACT (no heuristics).

A digraph is (n, arcs) with arcs a list of (u, v), vertices 0..n-1.
"""
from __future__ import annotations

import os
import sys

# --- pull the exact SAT/MaxSAT oracles + nauty wrappers from the shared lib ---
# (path relative to this file so the module imports from a fresh clone anywhere)
_ENGINE_LIB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine", "lib")
if _ENGINE_LIB not in sys.path:
    sys.path.insert(0, _ENGINE_LIB)

import digraph_core as _dc  # noqa: E402

# re-export the exact, sound primitives unchanged
acyclic_number = _dc.acyclic_number
dichromatic_number = _dc.dichromatic_number
is_k_dicolourable = _dc.is_k_dicolourable
is_acyclic = _dc.is_acyclic
is_oriented = _dc.is_oriented
underlying_edges = _dc.underlying_edges
all_orientations = _dc.all_orientations
triangle_free_graphs = _dc.triangle_free_graphs


# --------------------------------------------------------------------------- #
#  geng: ALL simple graphs on n vertices (not just triangle-free)
# --------------------------------------------------------------------------- #

def all_simple_graphs(n, connected=False):
    """Yield (n, edges) for every simple graph on n vertices (one per
    isomorphism class) via nauty `geng`.  Unlike digraph_core.triangle_free_graphs
    (which passes -t), C_3 allows triangles (the directed C3), so we must
    enumerate the FULL graph slice."""
    import subprocess
    gp = _dc._geng_path()
    flags = [gp, "-q"]
    if connected:
        flags.append("-c")
    flags.append(str(n))
    proc = subprocess.run(flags, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"geng failed: {proc.stderr}")
    for line in proc.stdout.splitlines():
        if line.strip():
            yield _dc._graph6_to_edges(line)


# --------------------------------------------------------------------------- #
#  C_3 membership  (pure combinatorial, exact)
# --------------------------------------------------------------------------- #

def _out_in(n, arcs):
    out = [set() for _ in range(n)]
    inn = [set() for _ in range(n)]
    for (u, v) in arcs:
        out[u].add(v)
        inn[v].add(u)
    return out, inn


def has_transitive_triangle(n, arcs):
    """True iff some a,b,c have a->b, b->c, a->c (a transitive triangle TT3)."""
    out, _ = _out_in(n, arcs)
    for a in range(n):
        oa = out[a]
        for b in oa:
            # b->c and a->c  ==>  c in out[b] AND c in out[a]
            if out[b] & oa:
                return True
    return False


def _is_induced_directed_cycle(S, out):
    """True iff the subdigraph induced on the vertex set S (a list/iterable) is
    exactly one directed cycle spanning all of S (|S| arcs, each vertex
    out-deg 1 / in-deg 1 within S, single strongly-connected cycle)."""
    Sset = set(S)
    k = len(Sset)
    if k < 2:
        return False
    # within-S out-adjacency
    succ = {}
    arc_count = 0
    for v in Sset:
        o = out[v] & Sset
        if len(o) != 1:
            return False
        w = next(iter(o))
        succ[v] = w
        arc_count += 1
    if arc_count != k:
        return False
    # in-degree 1 each is implied if it is a single cycle; verify by walking
    start = next(iter(Sset))
    seen = set()
    cur = start
    for _ in range(k):
        if cur in seen:
            return False
        seen.add(cur)
        cur = succ[cur]
    return cur == start and len(seen) == k


def has_long_induced_dicycle(n, arcs, min_len=4):
    """True iff some induced subdigraph of order >= min_len is a directed cycle.

    Exact: enumerate vertex subsets.  We exploit that an induced directed
    k-cycle has within-set out-degree EXACTLY 1 at every vertex, so we only need
    to test subsets in which the induced out-degrees can all be 1 -- but for
    exactness on the small n the oracle handles we scan candidate subsets via
    cycle enumeration in the underlying digraph (every induced dicycle is a
    chordless directed cycle of the digraph).
    """
    import networkx as nx
    out, _ = _out_in(n, arcs)
    d = nx.DiGraph()
    d.add_nodes_from(range(n))
    d.add_edges_from(arcs)
    # Every induced directed cycle is in particular a directed cycle of d whose
    # vertex set induces exactly that cycle.  Enumerate simple directed cycles
    # of length >= min_len and test inducedness.  simple_cycles is exact and
    # finite; for the small digraphs the oracle handles this is tractable.
    for cyc in nx.simple_cycles(d):
        if len(cyc) >= min_len and _is_induced_directed_cycle(cyc, out):
            return True
    return False


def is_C3(n, arcs):
    """Exact membership test for the class C_3 of the paper:
    oriented (no digon) AND no transitive triangle TT3 AND no induced directed
    cycle of length >= 4."""
    if not is_oriented(arcs):
        return False
    if has_transitive_triangle(n, arcs):
        return False
    if has_long_induced_dicycle(n, arcs, min_len=4):
        return False
    return True


def c3_reason(n, arcs):
    """Diagnostic: why (n,arcs) is / isn't in C_3."""
    return {
        "is_oriented": is_oriented(arcs),
        "has_TT3": has_transitive_triangle(n, arcs),
        "has_long_induced_dicycle_ge4": has_long_induced_dicycle(n, arcs, 4),
        "is_C3": is_C3(n, arcs),
    }
