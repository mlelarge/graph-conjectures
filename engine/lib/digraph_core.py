"""Core oracle for the oriented-triangle-free extremal problem (arXiv:2403.02298).

Definitions (Aboulker, Havet, Pirot, Schabanel 2024):
  * An *oriented graph* is a digraph with no 2-cycle (no pair u->v and v->u).
  * It is *triangle-free* if its underlying simple graph has no triangle.
  * acyclic number  alpha_vec(D)  = max order of an induced acyclic subdigraph.
  * dichromatic number  chi_vec(D) = least k s.t. V(D) partitions into k acyclic sets.
  * a_vec(n) = min  alpha_vec(D)  over oriented triangle-free graphs of order n.
  * t_vec(n) = max  chi_vec(D)    over oriented triangle-free graphs of order n.

Everything here is EXACT (no heuristics): alpha_vec via MaxSAT + lazy cycle
elimination, chi_vec via SAT k-dicolourability + lazy cycle elimination.  These
are the sound ground truth against which every agent-proposed construction is
checked.  A digraph is represented as (n, arcs) with arcs a list of (u, v),
vertices 0..n-1.
"""
from __future__ import annotations

import subprocess
from functools import lru_cache

import networkx as nx
from pysat.solvers import Solver
from pysat.formula import WCNF
from pysat.examples.rc2 import RC2

# --------------------------------------------------------------------------- #
#  Basic structure
# --------------------------------------------------------------------------- #

def underlying_edges(arcs):
    """Undirected edge set {frozenset({u,v})} of the underlying simple graph."""
    return {frozenset((u, v)) for (u, v) in arcs}


def _check(n, arcs):
    """Validate (n, arcs) is a well-formed digraph: n >= 0 and every arc endpoint
    is a vertex in range(n).  Raises ValueError on malformed input so out-of-range
    arcs fail LOUD instead of being silently dropped by the subgraph builds (which
    would yield confident-but-wrong invariants).  This is the soundness spine: the
    oracle must never return a number for a graph it did not actually see."""
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    for (u, v) in arcs:
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(
                f"arc ({u}, {v}) has an endpoint outside 0..{n - 1} (n={n})")


def is_oriented(arcs, n=None):
    """True iff no 2-cycle: never both (u,v) and (v,u).

    If ``n`` is given, also validates that every arc endpoint is in range(n)."""
    if n is not None:
        _check(n, arcs)
    s = set(map(tuple, arcs))
    return all((v, u) not in s for (u, v) in s) and len(s) == len(underlying_edges(arcs))


def is_triangle_free(n, arcs):
    """True iff the underlying simple graph has no triangle."""
    _check(n, arcs)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(tuple(e) for e in underlying_edges(arcs))
    # a triangle = a 3-clique; cheap for the small graphs we handle
    for u, v in g.edges():
        if set(g.neighbors(u)) & set(g.neighbors(v)):
            return False
    return True


def _digraph(n, arcs):
    d = nx.DiGraph()
    d.add_nodes_from(range(n))
    d.add_edges_from(arcs)
    return d


def is_acyclic(n, arcs):
    _check(n, arcs)
    return nx.is_directed_acyclic_graph(_digraph(n, arcs))


def _find_directed_cycle(d):
    """Return a directed cycle as a list of vertices, or None if acyclic."""
    try:
        edges = nx.find_cycle(d, orientation="original")
    except nx.NetworkXNoCycle:
        return None
    return [u for (u, v, _) in edges]


# --------------------------------------------------------------------------- #
#  Exact dichromatic number  (SAT + lazy cycle elimination)
# --------------------------------------------------------------------------- #

def is_k_dicolourable(n, arcs, k, solver_name="glucose3"):
    """Exact test: can V be partitioned into k acyclic sets?

    Lazy cycle elimination: solve a colouring relaxation, look for a
    monochromatic directed cycle, forbid it, repeat.  Exact and terminating.
    """
    _check(n, arcs)
    if k <= 0:
        return n == 0
    if k == 1:
        return is_acyclic(n, arcs)

    def var(v, c):                       # 1-based SAT variable for "vertex v has colour c"
        return v * k + c + 1

    solver = Solver(name=solver_name)
    for v in range(n):                   # exactly-one colour per vertex
        solver.add_clause([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                solver.add_clause([-var(v, c1), -var(v, c2)])

    while True:
        if not solver.solve():
            solver.delete()
            return False
        model = set(solver.get_model())
        colour = {v: next(c for c in range(k) if var(v, c) in model) for v in range(n)}
        added = False
        for c in range(k):
            verts = [v for v in range(n) if colour[v] == c]
            sub = _digraph(n, [(u, v) for (u, v) in arcs if u in verts and v in verts])
            cyc = _find_directed_cycle(sub.subgraph(verts))
            if cyc is not None:          # forbid this monochromatic cycle in colour c
                solver.add_clause([-var(v, c) for v in cyc])
                added = True
        if not added:
            solver.delete()
            return True


def dichromatic_number(n, arcs, ub=None):
    """Dichromatic number chi_vec(D); EXACT when ``ub`` is None.

    With ``ub=k`` the colour search is capped at k: the return is the exact value
    when chi_vec(D) <= k, otherwise the SENTINEL ``k + 1`` meaning ">k".  The
    sentinel is NOT the true value (it is the same number no matter how far above
    k chi_vec actually is), so a caller that passes ``ub`` must not treat a return
    of ``ub + 1`` as exact -- recompute uncapped when the exact value is needed."""
    _check(n, arcs)
    if n == 0:
        return 0
    k = 1
    cap = ub if ub is not None else n
    while k <= cap:
        if is_k_dicolourable(n, arcs, k):
            return k
        k += 1
    return cap + 1  # sentinel: chi_vec(D) > cap (an underestimate; see docstring)


# --------------------------------------------------------------------------- #
#  Exact acyclic number  (MaxSAT + lazy cycle elimination)
# --------------------------------------------------------------------------- #

def acyclic_number(n, arcs):
    """Exact alpha_vec(D) = largest induced acyclic vertex set.

    MaxSAT: soft-prefer every vertex selected; hard-forbid every directed cycle
    from being fully selected, added lazily until the optimum is acyclic.
    """
    _check(n, arcs)
    if n == 0:
        return 0
    hard = []                            # accumulated cycle-forbidding clauses
    while True:
        wcnf = WCNF()
        for v in range(n):
            wcnf.append([v + 1], weight=1)   # soft: prefer v selected
        for clause in hard:
            wcnf.append(clause)               # hard: not all of this cycle selected
        with RC2(wcnf) as rc2:
            model = rc2.compute()
        chosen = [v for v in range(n) if (v + 1) in set(model)]
        sub = _digraph(n, [(u, v) for (u, v) in arcs if u in chosen and v in chosen])
        cyc = _find_directed_cycle(sub.subgraph(chosen))
        if cyc is None:
            return len(chosen)
        hard.append([-(v + 1) for v in cyc])


# --------------------------------------------------------------------------- #
#  nauty geng: triangle-free simple graphs
# --------------------------------------------------------------------------- #

def _geng_path():
    for cand in ("geng", "nauty-geng"):
        try:
            subprocess.run([cand, "--help"], capture_output=True)
            return cand
        except FileNotFoundError:
            continue
    raise RuntimeError("nauty geng not found on PATH")


def _graph6_to_edges(line):
    """Decode a headerless graph6 line into (n, edges)."""
    b = line.strip().encode("ascii")
    if not b:
        return 0, []
    if b[0] == 126:
        raise NotImplementedError("n>=63 graph6 not needed here")
    n = b[0] - 63
    bits = []
    for ch in b[1:]:
        v = ch - 63
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    edges, idx = [], 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


def triangle_free_graphs(n, connected=False):
    """Yield (n, edges) for every triangle-free simple graph on n vertices
    (one per isomorphism class) via `geng -t`."""
    gp = _geng_path()
    flags = [gp, "-t", "-q"]
    if connected:
        flags.append("-c")
    flags.append(str(n))
    proc = subprocess.run(flags, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"geng failed: {proc.stderr}")
    for line in proc.stdout.splitlines():
        if line.strip():
            yield _graph6_to_edges(line)


def k4_free_graphs(n, connected=False):
    """Yield (n, edges) for every K4-free simple graph on n vertices
    (one per isomorphism class) via `geng -k`."""
    gp = _geng_path()
    flags = [gp, "-k", "-q"]
    if connected:
        flags.append("-c")
    flags.append(str(n))
    proc = subprocess.run(flags, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"geng failed: {proc.stderr}")
    for line in proc.stdout.splitlines():
        if line.strip():
            yield _graph6_to_edges(line)


def all_orientations(edges):
    """Yield every orientation (list of arcs) of an undirected edge list.

    2^|edges| orientations; caller must restrict to small graphs.  Each
    orientation of an oriented graph is automatically 2-cycle-free.
    """
    edges = [tuple(e) for e in edges]
    m = len(edges)
    for mask in range(1 << m):
        yield [(u, v) if (mask >> i) & 1 else (v, u)
               for i, (u, v) in enumerate(edges)]
