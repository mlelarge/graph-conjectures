"""Structural analysis of NO-instances for the linear-forest ordering
problem.

For a given tournament T, this script computes:
  - the minimum FAS size f(T);
  - every minimum FAS (back-arc set of every order that achieves f(T));
  - the multiset of (max_degree_of_back-arc-graph) over all orders;
  - for each order achieving max-degree d, the vertex/vertices that
    realize the maximum.

The goal is to identify the "forced high-degree vertex" obstruction in
tournaments where a forest-ordering exists but no linear-forest-ordering
does.
"""
from __future__ import annotations
import os, sys
from collections import Counter, defaultdict
from itertools import permutations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import verify  # noqa: E402


def analyze(T):
    n = len(T)
    by_size = defaultdict(list)            # size -> list of (order, info)
    by_max_deg = Counter()                 # max_degree -> count
    by_max_deg_forests = Counter()         # max_degree among forest-orderings
    all_orders = list(permutations(range(n)))

    for P in all_orders:
        info = verify(T, list(P))
        size = info["count"]
        max_d = info["max_degree"]
        by_size[size].append((P, info))
        by_max_deg[max_d] += 1
        if info["is_forest"]:
            by_max_deg_forests[max_d] += 1

    min_size = min(by_size)
    return {
        "n": n,
        "min_FAS": min_size,
        "orderings_at_min": len(by_size[min_size]),
        "max_deg_distribution_all": dict(by_max_deg),
        "max_deg_distribution_forests": dict(by_max_deg_forests),
        "min_max_deg_among_forests": (min(by_max_deg_forests)
                                       if by_max_deg_forests else None),
        "min_FAS_orders": [list(P) for (P, _) in by_size[min_size][:6]],
        "min_FAS_arc_sets": [list(info["arcs"])
                              for (_, info) in by_size[min_size][:6]],
        "min_FAS_max_degs": [info["max_degree"]
                              for (_, info) in by_size[min_size]],
    }


def degree_frequency_at_min_max_deg(T):
    """For each forest-ordering achieving the *minimum* max-degree among
    forest-orderings, report which vertex realizes that max degree.
    """
    n = len(T)
    best = None
    high_vertices = Counter()
    forest_orders = 0

    for P in permutations(range(n)):
        info = verify(T, list(P))
        if not info["is_forest"]:
            continue
        forest_orders += 1
        max_d = info["max_degree"]
        if best is None or max_d < best:
            best = max_d
            high_vertices.clear()
        if max_d == best:
            # which vertex/vertices achieve max degree?
            deg = Counter()
            for (u, v) in info["arcs"]:
                deg[u] += 1; deg[v] += 1
            for v, d in deg.items():
                if d == max_d:
                    high_vertices[v] += 1
    return {"forest_orders": forest_orders,
            "min_max_deg_among_forests": best,
            "high_vertex_frequency": dict(high_vertices)}


if __name__ == "__main__":
    # The FOREST_NOT_PATH_FAS example from tests/test_path_fas.py.
    T = [
        [0, 0, 1, 0, 1, 1, 1],
        [1, 0, 0, 0, 1, 1, 1],
        [0, 1, 0, 0, 1, 1, 0],
        [1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 1],
        [0, 0, 1, 1, 1, 0, 0],
    ]
    import json
    a = analyze(T)
    print("=== Full analysis ===")
    print(json.dumps(a, indent=2, default=str))
    print()
    print("=== High-degree vertices among best forest-orderings ===")
    print(json.dumps(degree_frequency_at_min_max_deg(T), indent=2))
