"""An in-class witness realizing the D37 REACH-saturation kernel.

The host is a four-arc modification of relay_free_witness.  The chosen
cage-sparing tree consumes the entire three-arc cut from

    Z = {u} union cage union AV_u-heads union {v}

to the canonical reachable side.  Consequently no distinct-tail pair of
boundary prescriptions completes that tree.  A second tree on the same
digraph avoids the cut and is completed by the canonical root pair; the
witness therefore kills the "every cage-sparing T" statement, not the
underlying existential L-exist target.
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

import networkx as nx  # noqa: E402

from check_lexist_fixedroot import (  # noqa: E402
    pair_realizable,
    subtree_through,
    tree_arcs,
)
from relay_free_witness import (  # noqa: E402
    host_arcs as relay_free_host_arcs,
    is_in_arb,
)


N_HOST = 15
N = 14
ROOT = 0
U = 1
V = 5
CAGE = {1, 2, 3, 4}
HEADS = {6, 7}
ROOTS = {11, 13}
PATH = [5, 8, 12, 0]
X_P = set(range(N)) - {ROOT} - set(PATH[:-1])
O = set(PATH[:-1])
BLOCK = CAGE | HEADS
Z_KERNEL = BLOCK | {V}
REACH_KERNEL = set(range(N)) - Z_KERNEL


def host_arcs():
    arcs = list(relay_free_host_arcs())
    arcs.remove((6, 10))
    arcs.remove((6, 11))
    arcs += [
        (10, 6),
        (11, 6),
        (7, 10),
        (8, 11),
    ]
    return arcs


def dbullet_arcs():
    relabel = {0: 0, 1: 0, 2: 1}
    relabel.update({v: v - 1 for v in range(3, N_HOST)})
    out = []
    for x, y in host_arcs():
        if (x, y) == (0, 1):
            continue
        rx, ry = relabel[x], relabel[y]
        if rx != ry:
            out.append((rx, ry))
    return out


def kernel_tree():
    return {
        2: 3,
        3: 1,
        4: 1,
        1: 5,
        6: 9,
        7: 10,
        9: 2,
        10: 3,
        11: 2,
        13: 3,
        5: 8,
        8: 12,
        12: 0,
    }


def repaired_tree():
    tree = kernel_tree()
    tree[6] = 2
    tree[7] = 3
    return tree


def residual(mult, tree, e1, e2):
    tree_set = tree_arcs(tree)
    graph = nx.MultiDiGraph()
    graph.add_nodes_from(range(N))
    for arc, multiplicity in mult.items():
        remaining = multiplicity - (arc in tree_set)
        if arc[0] == e1[0]:
            remaining = remaining if arc == e1 else 0
        if arc[0] == e2[0]:
            remaining = remaining if arc == e2 else 0
        for _ in range(max(0, remaining)):
            graph.add_edge(*arc)
    return graph


def reachable_vertices(graph):
    return {
        x
        for x in range(N)
        if nx.has_path(graph, x, ROOT)
    }


def reverse_bfs_tree(graph):
    reached = {ROOT}
    successor = {}
    while len(reached) < N:
        choice = next(
            (
                (x, y)
                for x in range(N)
                if x not in reached
                for y in sorted(set(graph.successors(x)))
                if y in reached
            ),
            None,
        )
        assert choice is not None
        x, y = choice
        successor[x] = y
        reached.add(x)
    return successor


def main():
    import oracle
    from digraph import Digraph
    from generators.near_split import is_one_zero_near_split

    host = host_arcs()
    assert len(host) == len(set(host))
    ok, why = is_one_zero_near_split(
        Digraph.from_arcs(range(N_HOST), host),
        [0, 1, 2],
        list(range(3, N_HOST)),
    )
    assert ok, why
    assert oracle.arc_connectivity(N_HOST, host) == 3
    sad = oracle.check_construction(
        N_HOST,
        host,
        name="saturation-kernel-host",
    )
    assert sad["sad"] == "SAT", sad
    if sad["cross_check"] is not None:
        assert sad["cross_check"]["agree"], sad

    arcs = dbullet_arcs()
    mult = Counter(arcs)
    assert oracle.arc_connectivity(N, arcs) == 3
    assert (U, ROOT) not in mult

    graph = nx.MultiDiGraph()
    graph.add_nodes_from(range(N))
    graph.add_edges_from(arcs)
    without_u = graph.copy()
    without_u.remove_node(U)
    cage = {U} | {
        x
        for x in range(N)
        if x not in (ROOT, U)
        and not nx.has_path(without_u, x, ROOT)
    }
    assert cage == CAGE
    assert all((r, h) in mult for r in ROOTS for h in HEADS)

    # The original hard gateway remains explicit after the modification.
    gateway_t = {
        2: 3,
        3: 1,
        4: 1,
        1: 5,
        5: 8,
        6: 7,
        7: 5,
        8: 11,
        9: 11,
        10: 11,
        11: 0,
        12: 0,
        13: 0,
    }
    gateway_u = {
        2: 1,
        3: 2,
        4: 2,
        1: 6,
        6: 9,
        9: 12,
        12: 11,
        11: 0,
        5: 2,
        7: 10,
        10: 13,
        13: 0,
        8: 6,
    }
    gateway_t_arcs = tree_arcs(gateway_t)
    gateway_u_arcs = tree_arcs(gateway_u)
    assert is_in_arb(gateway_t, N, ROOT)
    assert is_in_arb(gateway_u, N, ROOT)
    assert pair_realizable(gateway_t_arcs, gateway_u_arcs, mult)
    gateway_x = subtree_through(gateway_t, U, ROOT, N)
    assert gateway_x == CAGE
    exits = {
        arc
        for arc in gateway_u_arcs
        if arc[0] in gateway_x and arc[1] not in gateway_x
    }
    assert exits == {(U, 6)}
    strict_exits = {
        arc
        for arc in exits
        if (
            subtree_through(gateway_u, arc[0], ROOT, N)
            & gateway_x
        ) < gateway_x
    }
    assert not strict_exits

    # PATH is a shortest v-to-rho path in D-u and gives the intended X_P.
    assert all((x, y) in mult for x, y in zip(PATH, PATH[1:]))
    assert len(PATH) - 1 == nx.shortest_path_length(
        without_u,
        V,
        ROOT,
    )
    assert X_P == {1, 2, 3, 4, 6, 7, 9, 10, 11, 13}
    assert O == {5, 8, 12}

    tree = kernel_tree()
    tree_set = tree_arcs(tree)
    assert is_in_arb(tree, N, ROOT)
    assert all(mult[arc] >= 1 for arc in tree_set)
    assert subtree_through(tree, U, ROOT, N) == X_P

    # The tree is cage-sparing in the exact D35 sense.
    cage_residual = nx.MultiDiGraph()
    cage_residual.add_nodes_from(CAGE)
    for arc, multiplicity in mult.items():
        if arc[0] in CAGE and arc[1] in CAGE:
            for _ in range(multiplicity - (arc in tree_set)):
                cage_residual.add_edge(*arc)
    assert all(
        nx.has_path(cage_residual, c, U)
        for c in CAGE - {U}
    )

    boundary = sorted(
        arc
        for arc in mult
        if arc[0] in X_P
        and arc[1] not in X_P
        and arc != (U, V)
    )
    assert all(arc not in tree_set for arc in boundary)
    canonical = ((11, 0), (13, 0))
    canonical_residual = residual(mult, tree, *canonical)
    canonical_reach = reachable_vertices(canonical_residual)
    assert canonical_reach == REACH_KERNEL
    assert canonical_residual.has_edge(11, 0)
    assert canonical_residual.has_edge(13, 0)
    assert canonical_residual.has_edge(8, 11)
    assert canonical_residual.has_edge(8, 13)

    # This is exactly the D37 kernel: all Z-to-REACH arcs are consumed.
    z_to_reach = {
        arc
        for arc in mult
        if arc[0] in Z_KERNEL and arc[1] in REACH_KERNEL
    }
    assert z_to_reach == {(5, 8), (6, 9), (7, 10)}
    assert z_to_reach <= tree_set
    assert all(mult[arc] == 1 for arc in z_to_reach)
    head_boundary = {
        arc
        for arc in mult
        if arc[0] in HEADS and arc[1] in O
    }
    assert head_boundary == {(6, 5), (7, 5)}
    block_out_except_a = {
        arc
        for arc in mult
        if arc[0] in BLOCK
        and arc[1] not in BLOCK
        and arc != (U, V)
    }
    assert block_out_except_a == {
        (6, 5),
        (6, 9),
        (7, 5),
        (7, 10),
    }
    assert all(
        arc[1] in Z_KERNEL or arc in tree_set
        for arc in block_out_except_a
    )
    assert V not in canonical_reach

    # Exhaust every pair allowed by the D35 completion statement.
    tested_pairs = 0
    completing_pairs = []
    for i, e1 in enumerate(boundary):
        for e2 in boundary[i + 1 :]:
            if e1[0] == e2[0]:
                continue
            tested_pairs += 1
            reach = reachable_vertices(residual(mult, tree, e1, e2))
            if len(reach) == N:
                completing_pairs.append((e1, e2))
    assert tested_pairs == 79
    assert completing_pairs == []

    # The host is not an L-exist counterexample: a block-sparing choice of
    # T leaves the canonical pair fully reachable.
    repaired = repaired_tree()
    assert is_in_arb(repaired, N, ROOT)
    assert subtree_through(repaired, U, ROOT, N) == X_P
    repaired_reach = reachable_vertices(
        residual(mult, repaired, *canonical)
    )
    assert repaired_reach == set(range(N))
    repaired_u = reverse_bfs_tree(
        residual(mult, repaired, *canonical)
    )
    assert is_in_arb(repaired_u, N, ROOT)
    assert pair_realizable(
        tree_arcs(repaired),
        tree_arcs(repaired_u),
        mult,
    )
    repaired_exits = {
        arc
        for arc in tree_arcs(repaired_u)
        if arc[0] in X_P and arc[1] not in X_P
    }
    assert set(canonical) <= repaired_exits
    assert len({arc[0] for arc in repaired_exits}) >= 2

    print("D37 saturation kernel: IN-CLASS WITNESS VERIFIED")
    print("host lambda=3; contraction lambda=3; host SAD=SAT")
    print(f"canonical Z={sorted(Z_KERNEL)}")
    print(
        "Z->REACH cut consumed by T:",
        sorted(z_to_reach),
    )
    print(
        f"distinct-tail boundary pairs tested={tested_pairs}; "
        "completing=0"
    )
    print("block-sparing repaired T: canonical pair reaches all vertices")
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
