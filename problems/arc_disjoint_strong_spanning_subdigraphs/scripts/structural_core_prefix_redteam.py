"""Red-team the exact structural core-prefix profile.

The requested D62 next target was to prove, from sealed-block/CL/DT,
that every non-degenerate chain kernel has deficient core prefixes
Q- subset Q0 subset Q+ with out-sizes 1,0,1.

This script shows that the exact Q- out-size-one clause is not forced by
the currently formalized sealed-chain gates.  Add the reverse head arc
6 -> 5 in D-bullet labels, i.e. host arc 7 -> 6.  This preserves:

  * simple (1,0)-near-split host;
  * lambda(host)=lambda(D-bullet)=3;
  * the cage C_u;
  * the unique v -> rho path in D-u;
  * the same forced D_O chain arcs;
  * the same sealed B* out-cut;
  * the original hard gateway pair at the cage.

But the old Q- cut has split-core out-size 2 instead of 1, so the exact
1,0,1 structural profile cannot be derived from those hypotheses alone.
"""
from __future__ import annotations

import os
import sys
from collections import Counter

import networkx as nx

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
from chain_kernel_witness import dbullet_arcs  # noqa: E402
from d42_split_predicate_tester import (  # noqa: E402
    deficient_core_cuts,
    out_cut_size,
    relabel_core_arcs,
)
from digraph import Digraph  # noqa: E402
from generators.near_split import is_one_zero_near_split  # noqa: E402


EXTRA_HEAD_ARC = (6, 5)  # D-bullet labels; host labels become (7, 6).


def host_from_db(db_arcs):
    host = [(0, 1)]
    rho_in = Counter()
    rho_out = Counter()
    for x, y in db_arcs:
        if y == 0:
            rho_in[x] += 1
        elif x == 0:
            rho_out[y] += 1
        else:
            host.append((x + 1, y + 1))
    for x, mult in rho_in.items():
        host.append((x + 1, 0))
        if mult == 2:
            host.append((x + 1, 1))
    for y, mult in rho_out.items():
        host.append((0, y + 1))
        if mult == 2:
            host.append((1, y + 1))
    return host


def arc_connectivity(n, arcs):
    return Digraph.from_arcs(range(n), arcs).arc_connectivity()


def cut_mask(v2, vertices):
    idx = {v: i for i, v in enumerate(v2)}
    return sum(1 << idx[v] for v in vertices)


def core_out_edges(v2, core_arcs, vertices):
    idx = {v: i for i, v in enumerate(v2)}
    side = {idx[v] for v in vertices}
    return sorted((v2[u], v2[v]) for u, v in core_arcs if u in side and v not in side)


def verify_hard_gateway(mult):
    n, root, u, v = 23, 0, 1, 7
    cage = {1, 2, 3, 4}

    T0 = {
        2: 3, 3: 1, 4: 1, 1: 7, 5: 8, 6: 8, 7: 8, 8: 9,
        9: 22, 10: 5, 12: 5, 11: 12, 13: 0, 14: 0, 15: 0,
        22: 20, 20: 18, 18: 16, 16: 14, 17: 14, 19: 16, 21: 18,
    }
    U0 = {
        2: 1, 3: 2, 4: 2, 1: 10, 10: 11, 11: 18, 18: 17,
        17: 15, 15: 0, 5: 10, 6: 10, 7: 2, 8: 2, 9: 10,
        12: 13, 13: 0, 14: 0, 16: 15, 19: 17, 20: 19,
        21: 19, 22: 21,
    }
    ts0, us0 = tree_arcs(T0), tree_arcs(U0)
    assert pair_realizable(ts0, us0, mult)
    assert subtree_through(T0, u, root, n) == cage
    exits = sorted((p, q) for p, q in us0 if p in cage and q not in cage)
    assert exits == [(1, 10)], exits
    free = [
        e for e in mult
        if e[0] in cage and e[1] not in cage
        and mult[e] - (e in ts0) - (e in us0) >= 1
    ]
    assert free and all(e[0] == u for e in free), free
    return exits


def check_variant():
    db = tuple(dbullet_arcs()) + (EXTRA_HEAD_ARC,)
    host = host_from_db(db)
    host_set = set(host)
    n_host = 24
    v1 = (0, 1, 9, 11, 13)
    v2 = tuple(v for v in range(n_host) if v not in v1)

    ok, why = is_one_zero_near_split(Digraph.from_arcs(range(n_host), host), v1, v2)
    assert ok, why
    assert len(host) == len(host_set)
    assert arc_connectivity(n_host, host) == 3
    assert arc_connectivity(23, db) == 3

    mult = Counter(db)
    root, u, v = 0, 1, 7
    graph = nx.MultiDiGraph()
    graph.add_nodes_from(range(23))
    graph.add_edges_from(db)
    graph_minus_u = graph.copy()
    graph_minus_u.remove_node(u)
    cage = {
        u,
        *(
            x for x in range(23)
            if x not in (root, u) and not nx.has_path(graph_minus_u, x, root)
        ),
    }
    assert cage == {1, 2, 3, 4}, cage
    assert list(nx.all_shortest_paths(graph_minus_u, v, root)) == [
        [7, 8, 9, 10, 11, 12, 13, 0]
    ]

    o_vertices = {7, 8, 9, 10, 11, 12, 13}
    for tail, head in ((7, 8), (8, 9), (10, 11), (12, 13)):
        d_o = [
            (x, y) for x, y in mult
            if x == tail and (y in o_vertices or y == root)
        ]
        assert d_o == [(tail, head)], (tail, d_o)

    b_star = {1, 2, 3, 4, 5, 6, 7, 8, 10, 12}
    b_out = sorted((x, y) for x, y in mult if x in b_star and y not in b_star)
    assert b_out == [(8, 9), (10, 11), (12, 13)], b_out
    hard_exits = verify_hard_gateway(mult)

    core_arcs = relabel_core_arcs(host, v2)
    low_cuts = deficient_core_cuts(len(v2), core_arcs)
    low_details = [
        (
            core_out,
            tuple(v2[i] for i in range(len(v2)) if (mask >> i) & 1),
        )
        for mask, core_out in low_cuts
    ]

    q_minus = {2, 3, 4, 5, 7, 8}
    q0 = {2, 3, 4, 5, 6, 7, 8}
    q_plus = {2, 3, 4, 5, 6, 7, 8, 10}
    q_minus_out = out_cut_size(core_arcs, cut_mask(v2, q_minus))
    q0_out = out_cut_size(core_arcs, cut_mask(v2, q0))
    q_plus_out = out_cut_size(core_arcs, cut_mask(v2, q_plus))
    assert (q_minus_out, q0_out, q_plus_out) == (2, 0, 1)
    assert low_details == [
        (0, tuple(sorted(q0))),
        (1, tuple(sorted(q_plus))),
    ], low_details

    print("Structural core-prefix red-team")
    print(f"extra_dbullet_arc={EXTRA_HEAD_ARC} extra_host_arc={(7, 6)}")
    print("preserved gates:")
    print("  simple near-split host: yes")
    print("  lambda(host)=lambda(D-bullet)=3")
    print(f"  cage={sorted(cage)}")
    print("  unique shortest path=7->8->9->10->11->12->13->rho")
    print(f"  B*_out={b_out}")
    print(f"  hard_gateway_U_exits={hard_exits}")
    print("core prefix out-sizes:")
    print(f"  old Q-={tuple(sorted(q_minus))}: out={q_minus_out}, edges={core_out_edges(v2, core_arcs, q_minus)}")
    print(f"  Q0={tuple(sorted(q0))}: out={q0_out}")
    print(f"  Q+={tuple(sorted(q_plus))}: out={q_plus_out}")
    print(f"  low_cuts={low_details}")
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    check_variant()

