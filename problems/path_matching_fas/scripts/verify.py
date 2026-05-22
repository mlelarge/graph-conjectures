"""Verifier for Problem 4.4 (Aboulker-Aubian-Lopes).

Given a tournament T (as an n x n 0/1 matrix with T[u][v] = 1 iff there is
an arc u -> v) and a permutation P of [0..n-1] (vertex order, smallest
first), compute the back-arc set and classify it.

This module is the trust root: every higher-level claim about a tournament
and an ordering routes through `verify(T, P)`.
"""
from __future__ import annotations
from collections import Counter, deque
from typing import Sequence


def _validate(T: Sequence[Sequence[int]], P: Sequence[int]) -> int:
    n = len(T)
    for row in T:
        if len(row) != n:
            raise ValueError("T must be square")
    for u in range(n):
        if T[u][u] != 0:
            raise ValueError(f"T[{u}][{u}] must be 0 (no self-loop)")
        for v in range(u + 1, n):
            if (T[u][v] == 0) == (T[v][u] == 0):
                raise ValueError(f"T not a tournament at pair ({u},{v})")
            if T[u][v] not in (0, 1) or T[v][u] not in (0, 1):
                raise ValueError(f"T entries must be 0/1 at ({u},{v})")
    if sorted(P) != list(range(n)):
        raise ValueError(f"P must be a permutation of [0..{n-1}]")
    return n


def back_arcs(T: Sequence[Sequence[int]], P: Sequence[int]) -> list[tuple[int, int]]:
    """Return the list of back-arcs (u, v) of T under order P.

    P[i] is the vertex at position i (positions are 0-indexed). An arc
    u -> v is a back-arc iff pos(u) > pos(v).
    """
    n = _validate(T, P)
    pos = [0] * n
    for i, v in enumerate(P):
        pos[v] = i
    out: list[tuple[int, int]] = []
    for u in range(n):
        for v in range(n):
            if T[u][v] and pos[u] > pos[v]:
                out.append((u, v))
    return out


def _components(adj: dict[int, list[int]]) -> list[list[int]]:
    seen: set[int] = set()
    comps: list[list[int]] = []
    for s in adj:
        if s in seen:
            continue
        comp: list[int] = []
        dq = deque([s])
        seen.add(s)
        while dq:
            x = dq.popleft()
            comp.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    dq.append(y)
        comps.append(comp)
    return comps


def classify(arcs: list[tuple[int, int]]) -> dict:
    """Classify the *undirected* simple graph induced by `arcs`.

    Returns a dict with:
      - count: number of arcs
      - max_degree: max undirected degree among incident vertices
      - is_matching: every vertex has degree <= 1 (i.e. graph is a
        disjoint union of edges)
      - is_forest: acyclic
      - is_linear_forest: forest with max degree <= 2
      - is_path: exact connected path back-arc graph, retained as a
        diagnostic target
      - is_path_fas: formal path-FAS feasibility for this order, i.e. the
        back-arc graph is contained in some path; equivalently, it is a
        linear forest
      - touched_vertices: number of vertices incident to at least one arc
    """
    # Build undirected adjacency on touched vertices.
    adj: dict[int, list[int]] = {}
    seen_pairs: set[tuple[int, int]] = set()
    for (u, v) in arcs:
        a, b = (u, v) if u < v else (v, u)
        if (a, b) in seen_pairs:
            # Tournament has at most one arc per unordered pair, so this
            # should never happen for back-arcs derived from a tournament.
            # Treat as a parallel edge: kill simplicity.
            return {
                "count": len(arcs),
                "max_degree": None,
                "is_matching": False,
                "is_forest": False,
                "is_linear_forest": False,
                "is_path": False,
                "is_path_fas": False,
                "touched_vertices": None,
                "error": "parallel edges (multigraph) — input was not a tournament back-arc set",
            }
        seen_pairs.add((a, b))
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)

    deg = Counter({v: len(nb) for v, nb in adj.items()})
    max_deg = max(deg.values()) if deg else 0
    touched = len(adj)
    n_edges = len(seen_pairs)

    # Forest check: for each component, |edges| == |vertices| - 1.
    comps = _components(adj)
    is_forest = True
    is_connected = (len(comps) <= 1)
    for comp in comps:
        comp_vs = set(comp)
        ce = sum(1 for (a, b) in seen_pairs if a in comp_vs and b in comp_vs)
        if ce != len(comp) - 1:
            is_forest = False
            break

    is_linear_forest = is_forest and max_deg <= 2
    is_matching = is_forest and max_deg <= 1
    # Path: connected linear forest with exactly two degree-1 vertices, or
    # the empty graph (0 edges) -- but a "path" of length 0 is a single
    # vertex; the FAS context wants a nonempty graph. We treat the empty
    # FAS as is_matching=True and is_path=False (no arcs to form a path).
    if n_edges == 0:
        is_path = False
    elif n_edges == 1:
        # single edge: trivially a path of length 1
        is_path = is_connected and max_deg == 1
    else:
        deg1 = sum(1 for v in adj if deg[v] == 1)
        is_path = (is_connected and is_linear_forest and deg1 == 2)

    return {
        "count": n_edges,
        "max_degree": max_deg,
        "is_matching": is_matching,
        "is_forest": is_forest,
        "is_linear_forest": is_linear_forest,
        "is_path": is_path,
        "is_path_fas": is_linear_forest,
        "touched_vertices": touched,
    }


def verify(T: Sequence[Sequence[int]], P: Sequence[int]) -> dict:
    """Top-level verifier: return classification dict for back-arcs of T@P.

    Also includes the explicit back-arc list under the key `arcs`.
    """
    arcs = back_arcs(T, P)
    cls = classify(arcs)
    cls["arcs"] = arcs
    cls["order"] = list(P)
    return cls


if __name__ == "__main__":
    # Tiny smoke test: cyclic triangle 0->1->2->0.
    T = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
    for P in [(0, 1, 2), (1, 2, 0), (2, 0, 1), (0, 2, 1), (1, 0, 2), (2, 1, 0)]:
        v = verify(T, P)
        print(P, "->", {k: v[k] for k in ("count", "is_matching", "is_path", "arcs")})
