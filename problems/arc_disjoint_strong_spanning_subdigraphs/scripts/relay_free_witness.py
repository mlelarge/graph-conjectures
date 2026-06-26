"""An in-class K-dominated, T3-relay-free rho-headless gateway.

The outside semicomplete part is layered as

    escaped heads -> v -> L -> R -> rho,

with R -> {escaped heads, v} and L -> escaped heads.  Thus every escaped
head reaches rho, but none of its direct out-neighbours points to a rho-tail.
This refutes the candidate assertion that a two-step T3 relay h -> o -> w
must always exist.
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


def host_arcs():
    # V1: p=0, q=1, u=2.
    # V2: cage=3,4,5; v=6; escaped heads=7,8; L=9,10,11; R=12,13,14.
    cage = (3, 4, 5)
    heads = (6, 7, 8)
    layer = (9, 10, 11)
    rho_tails = (12, 13, 14)

    arcs = [(0, 1)]
    arcs += [(x, y) for x in cage for y in cage if x != y]
    arcs += [(x, 2) for x in cage]
    arcs += [(2, x) for x in heads]

    # Escaped AV_u heads 7,8 point only toward v among the forward layers.
    arcs += [(7, 6), (8, 6), (7, 8)]
    arcs += [(6, x) for x in layer]
    arcs += [(x, h) for x in layer for h in (7, 8)]
    arcs += [(x, y) for x in layer for y in layer if x != y]

    # Full domination by R, followed by the next layer pointing into R.
    arcs += [(r, h) for r in rho_tails for h in heads]
    arcs += [(x, r) for x in layer for r in rho_tails]
    arcs += [(x, y) for x in rho_tails for y in rho_tails if x != y]

    # Rho-tail multiplicities after contraction are 2,1,2.
    arcs += [(12, 0), (12, 1), (13, 0), (14, 0), (14, 1)]
    arcs += [(0, 12), (0, 13), (1, 13), (1, 14)]
    arcs += [(0, 9), (1, 10), (0, 11)]

    # Every outside K-vertex dominates the cage.
    arcs += [
        (x, c)
        for x in heads + layer + rho_tails
        for c in cage
    ]
    return arcs


def dbullet_arcs():
    # rho=0, u=1, cage=2,3,4, v=5, heads=6,7, L=8,9,10, R=11,12,13.
    relabel = {0: 0, 1: 0, 2: 1}
    relabel.update({v: v - 1 for v in range(3, 15)})
    out = []
    for x, y in host_arcs():
        if (x, y) == (0, 1):
            continue
        rx, ry = relabel[x], relabel[y]
        if rx != ry:
            out.append((rx, ry))
    return out


def is_in_arb(succ, n, root):
    for start in range(n):
        if start == root:
            continue
        seen, cur = set(), start
        while cur != root:
            if cur in seen or cur not in succ:
                return False
            seen.add(cur)
            cur = succ[cur]
    return True


def main():
    import networkx as nx
    import oracle
    from digraph import Digraph
    from generators.near_split import is_one_zero_near_split

    host = host_arcs()
    assert len(host) == len(set(host)), "host must be simple"
    ok, why = is_one_zero_near_split(
        Digraph.from_arcs(range(15), host),
        [0, 1, 2],
        list(range(3, 15)),
    )
    assert ok, why
    assert oracle.arc_connectivity(15, host) == 3
    sad = oracle.check_construction(15, host, name="relay-free-host")
    assert sad["sad"] == "SAT", sad
    if sad["cross_check"] is not None:
        assert sad["cross_check"]["agree"], sad

    arcs = dbullet_arcs()
    n, root, u = 14, 0, 1
    mult = Counter(arcs)
    assert oracle.arc_connectivity(n, arcs) == 3
    assert (u, root) not in mult

    graph = nx.MultiDiGraph()
    graph.add_nodes_from(range(n))
    graph.add_edges_from(arcs)
    without_u = graph.copy()
    without_u.remove_node(u)
    cage = {u} | {
        x
        for x in range(n)
        if x not in (root, u) and not nx.has_path(without_u, x, root)
    }
    assert cage == {1, 2, 3, 4}, cage

    a, v = (u, 5), 5
    av_heads = sorted(z for x, z in mult if x == u and z != v)
    rho_tails = sorted(x for x, z in mult if z == root)
    assert av_heads == [6, 7]
    assert rho_tails == [11, 12, 13]

    # Explicit arc-disjoint pair realizing a failing hard gateway at a.
    tree_t = {
        2: 3, 3: 1, 4: 1, 1: 5,
        5: 8, 6: 7, 7: 5,
        8: 11, 9: 11, 10: 11,
        11: 0, 12: 0, 13: 0,
    }
    tree_u = {
        2: 1, 3: 2, 4: 2, 1: 6,
        6: 5, 5: 9, 7: 2, 8: 6,
        9: 12, 10: 13,
        11: 0, 12: 11, 13: 0,
    }
    t_arcs, u_arcs = tree_arcs(tree_t), tree_arcs(tree_u)
    assert is_in_arb(tree_t, n, root)
    assert is_in_arb(tree_u, n, root)
    assert pair_realizable(t_arcs, u_arcs, mult)
    x_set = subtree_through(tree_t, u, root, n)
    assert x_set == cage
    exits = sorted(e for e in u_arcs if e[0] in x_set and e[1] not in x_set)
    assert exits == [(u, 6)], exits
    strict = [
        e
        for e in exits
        if (subtree_through(tree_u, e[0], root, n) & x_set) < x_set
    ]
    assert not strict
    free = [
        e
        for e, multiplicity in mult.items()
        if e[0] in x_set
        and e[1] not in x_set
        and multiplicity - (e in t_arcs) - (e in u_arcs) >= 1
    ]
    assert free and all(e[0] == u for e in free)

    # Every rho-tail is admissible, fully dominates each escaped K-head,
    # defeats both T2 alternatives, and has no structural T3 relay.
    for w in rho_tails:
        reduced = graph.copy()
        reduced.remove_nodes_from(cage | {w})
        trapped = {
            z
            for z in range(n)
            if z not in cage | {w}
            and z != root
            and not nx.has_path(reduced, z, root)
        }
        x_star = cage | {w} | trapped
        outside = set(range(n)) - x_star - {root}
        assert not trapped
        assert v not in x_star and len(x_star) <= n - 2

        for h in av_heads:
            assert h in outside
            assert h not in rho_tails
            assert (w, h) in mult and (h, w) not in mult
            assert nx.shortest_path_length(graph, h, w) == 3
            relays = [
                o for o in outside
                if (h, o) in mult and (o, w) in mult
            ]
            assert not relays, (w, h, relays)

    print("K-dominated relay-free hard gateway: verified")
    print("host lambda=3; contraction lambda=3; all rho-tails admissible")
    print("T2 and T3 are inapplicable for every (w,h)")
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
