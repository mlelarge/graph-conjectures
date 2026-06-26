"""Refute the D29 v-target internal-reachability obligation.

Extend relay_free_witness by one independent blocker x_(L,R) for each
shortest path

    v -> L -> R -> rho.

The blocker has exactly the three out-arcs x_(L,R) -> {v,L,R}.  Its three
in-arcs come from the rho-tail layer.  The resulting host is still a simple
(1,0)-near-split digraph, and both the host and its chord contraction remain
3-arc-strong.

For every shortest v->rho path P in D^bullet-u, the corresponding blocker is
in X = V - ({rho} union V(P)) but has no path to u inside D^bullet[X].
Consequently no in-arborescence T containing a=(u,v) can realize
X_a^T = X.  The original hard gateway pair extends to all blockers, so the
failure occurs in the intended gateway regime.
"""
from __future__ import annotations

import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from check_lexist_fixedroot import (  # noqa: E402
    pair_realizable,
    subtree_through,
    tree_arcs,
)
from relay_free_witness import host_arcs as base_host_arcs  # noqa: E402


def construction():
    # Original host: V1={0,1,2}; K={3,...,14}.  Its shortest v=6 to
    # contracted-root paths are 6->L->R->rho with L in 9..11, R in 12..14.
    host = list(base_host_arcs())
    K = list(range(3, 15))
    blockers = []
    next_vertex = 15
    for layer in (9, 10, 11):
        for rho_tail in (12, 13, 14):
            x = next_vertex
            next_vertex += 1
            blockers.append((x, layer, rho_tail))
            host.extend([(x, 6), (x, layer), (x, rho_tail)])
            host.extend((r, x) for r in (12, 13, 14))

    relabel = {0: 0, 1: 0, 2: 1}
    relabel.update({z: z - 1 for z in K})
    relabel.update({x: 14 + i for i, (x, _, _) in enumerate(blockers)})

    contraction = []
    for x, y in host:
        if (x, y) == (0, 1):
            continue
        rx, ry = relabel[x], relabel[y]
        if rx != ry:
            contraction.append((rx, ry))
    return host, contraction, blockers


def is_in_arborescence(succ, n, root):
    for start in range(n):
        if start == root:
            continue
        seen = set()
        current = start
        while current != root:
            if current in seen or current not in succ:
                return False
            seen.add(current)
            current = succ[current]
    return True


def main():
    import networkx as nx
    import oracle
    from digraph import Digraph
    from generators.near_split import is_one_zero_near_split

    host, db, blockers = construction()
    host_n = 24
    contraction_n = 23
    K = list(range(3, 15))
    I = [0, 1, 2] + [x for x, _, _ in blockers]

    assert len(host) == len(set(host))
    ok, why = is_one_zero_near_split(
        Digraph.from_arcs(range(host_n), host), I, K
    )
    assert ok, why
    assert oracle.arc_connectivity(host_n, host) == 3
    assert oracle.arc_connectivity(contraction_n, db) == 3

    root, u, v = 0, 1, 5
    graph = nx.DiGraph()
    graph.add_nodes_from(range(contraction_n))
    graph.add_edges_from(db)
    without_u = graph.copy()
    without_u.remove_node(u)
    paths = list(nx.all_shortest_paths(without_u, v, root))
    assert len(paths) == 9
    assert {len(path) - 1 for path in paths} == {3}

    blocked = []
    for path in paths:
        X = set(range(contraction_n)) - {root} - set(path[:-1])
        inside = graph.subgraph(X)
        bad = [x for x in X if not nx.has_path(inside, x, u)]
        assert bad
        blocked.append((path, bad))
    assert len(blocked) == len(paths)

    # Extend the relay-free witness's explicit hard gateway pair.  Every
    # blocker uses x->v in T and x->L in U, so it lies outside X_a^T and the
    # original single U-exit from the cage is unchanged.
    T = {
        2: 3, 3: 1, 4: 1, 1: 5,
        5: 8, 6: 7, 7: 5,
        8: 11, 9: 11, 10: 11,
        11: 0, 12: 0, 13: 0,
    }
    U = {
        2: 1, 3: 2, 4: 2, 1: 6,
        6: 5, 5: 9, 7: 2, 8: 6,
        9: 12, 10: 13,
        11: 0, 12: 11, 13: 0,
    }
    for i, (_, layer, _) in enumerate(blockers):
        x = 14 + i
        T[x] = v
        U[x] = layer - 1

    mult = Counter(db)
    t_arcs, u_arcs = tree_arcs(T), tree_arcs(U)
    assert is_in_arborescence(T, contraction_n, root)
    assert is_in_arborescence(U, contraction_n, root)
    assert pair_realizable(t_arcs, u_arcs, mult)
    X_gateway = subtree_through(T, u, root, contraction_n)
    assert X_gateway == {1, 2, 3, 4}
    exits = sorted(
        e for e in u_arcs if e[0] in X_gateway and e[1] not in X_gateway
    )
    assert exits == [(1, 6)]
    strict = [
        e for e in exits
        if (subtree_through(U, e[0], root, contraction_n) & X_gateway)
        < X_gateway
    ]
    assert not strict

    print("host lambda=3; contraction lambda=3; hard gateway pair verified")
    print(f"all {len(paths)} shortest v->rho paths fail internal reachability")
    for path, bad in blocked:
        print(f"  P={path}: blockers={bad}")
    print("A-double-prime obligation (i) REFUTED IN-CLASS")


if __name__ == "__main__":
    main()
