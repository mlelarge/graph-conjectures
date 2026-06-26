"""Red-team the W2 outside-core two-support lemma.

D73 reduced the outside-core certificate OC to W2:

    lambda(C[O \\ {w1}]) >= 2.

This script checks the nearest semicomplete-preserving perturbation of the
D42 chain kernel.  Reverse the D-bullet support arc 11->18 to 18->11.  The
usual sealed-chain gates, primitive head-block clauses, global lambda=3, and
a hard gateway pair still survive, but the post-first-successor outside core
has the one-arc cut {12} in host labels.

Thus W2 is not a consequence of the currently formalized sealed-block/CL/DT
primitive package.  The local FSQ conclusion may still survive because w1 can
contribute an additional exit to such a cut; W2 itself is the over-strong step.
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

from chain_crossing_selection_check import hard_pair  # noqa: E402
from chain_feed_deletion_stress import (  # noqa: E402
    host_arcs_from_dbullet,
    structural_gates,
)
from chain_kernel_witness import dbullet_arcs, is_in_arb  # noqa: E402
from check_lexist_fixedroot import (  # noqa: E402
    pair_realizable,
    subtree_through,
    tree_arcs,
)
from d42_split_predicate_tester import relabel_core_arcs  # noqa: E402
from digraph import Digraph  # noqa: E402
from local_normal_form_audit import (  # noqa: E402
    Q0,
    V1_HOST,
    V2_HOST,
    all_subsets,
    out_edges,
)


N_DB = 23
N_HOST = 24
ROOT = 0
U_DB = 1
W1_HOST = 10

DELETE_ARC = (11, 18)
ADD_ARC = (18, 11)

U_HOST = 2
RESERVE = frozenset((3, 4, 5))
HEADS = frozenset((6, 7, 8))
CAGE_HOST = frozenset((U_HOST,)) | RESERVE
OUTSIDE = frozenset(V2_HOST) - Q0
OUTSIDE_CORE = OUTSIDE - {W1_HOST}


def reversed_support_arcs():
    arcs = list(dbullet_arcs())
    assert arcs.count(DELETE_ARC) == 1
    assert ADD_ARC not in arcs
    arcs.remove(DELETE_ARC)
    arcs.append(ADD_ARC)
    return tuple(arcs)


def arcs_between(edges, left, right):
    left = set(left)
    right = set(right)
    return sorted((u, v) for u, v in edges if u in left and v in right)


def powerset_nonempty(vertices):
    vertices = tuple(sorted(vertices))
    for mask in range(1, 1 << len(vertices)):
        yield frozenset(
            vertices[i] for i in range(len(vertices)) if (mask >> i) & 1
        )


def core_edges(db_arcs):
    host = tuple(host_arcs_from_dbullet(db_arcs))
    assert len(host) == len(set(host))
    core_arcs = relabel_core_arcs(host, V2_HOST)
    return tuple((V2_HOST[u], V2_HOST[v]) for u, v in core_arcs)


def induced_lambda(edges, vertices):
    vertices = tuple(sorted(vertices))
    rel = {v: i for i, v in enumerate(vertices)}
    arcs = [(rel[u], rel[v]) for u, v in edges if u in rel and v in rel]
    return Digraph.from_arcs(range(len(vertices)), arcs).arc_connectivity()


def low_cuts(edges, vertices):
    rows = []
    for side in all_subsets(vertices):
        outgoing = tuple(out_edges(edges, side, vertices))
        if len(outgoing) <= 1:
            rows.append((tuple(sorted(side)), outgoing))
    return rows


def verify_primitive_head_block(edges):
    edge_set = set(edges)
    reserve_expansion = [
        (tuple(sorted(P)), tuple(arcs_between(edges, P, CAGE_HOST - P)))
        for P in powerset_nonempty(RESERVE)
    ]
    root_fan = [(U_HOST, z) for z in sorted(HEADS)]
    hooks = [(z, r) for z in sorted(HEADS) for r in sorted(RESERVE)]
    head_pairs = [
        (a, b) for a in sorted(HEADS) for b in sorted(HEADS) if a < b
    ]
    head_semicomplete_missing = [
        (a, b)
        for a, b in head_pairs
        if (a, b) not in edge_set and (b, a) not in edge_set
    ]
    head_sources = [
        z for z in sorted(HEADS)
        if not arcs_between(edges, HEADS - {z}, {z})
    ]
    low_head_complements = [
        (tuple(sorted(T)), tuple(arcs_between(edges, Q0 - T, T)))
        for T in all_subsets(Q0)
        if len(arcs_between(edges, Q0 - T, T)) <= 1
    ]

    assert all(len(row[1]) >= 2 for row in reserve_expansion)
    assert all(e in edge_set for e in root_fan)
    assert all(e in edge_set for e in hooks)
    assert not head_semicomplete_missing
    assert len(head_sources) <= 1
    assert low_head_complements == [((6,), ((2, 6),))]
    return {
        "min_reserve_expansion": min(len(row[1]) for row in reserve_expansion),
        "root_fan": root_fan,
        "head_sources": head_sources,
        "low_head_complements": low_head_complements,
    }


def verify_repaired_hard_gateway(db_arcs):
    mult = Counter(db_arcs)
    T, old_U = hard_pair()
    U = dict(old_U)
    U[11] = 22

    old_usage = Counter(tree_arcs(T)) + Counter(tree_arcs(old_U))
    old_missing = tuple(sorted(e for e in old_usage if old_usage[e] > mult[e]))
    assert old_missing == (DELETE_ARC,)

    Tset, Uset = tree_arcs(T), tree_arcs(U)
    usage = Counter(Tset) + Counter(Uset)
    assert all(usage[e] <= mult[e] for e in usage)
    assert is_in_arb(T, N_DB, ROOT)
    assert is_in_arb(U, N_DB, ROOT)
    assert pair_realizable(Tset, Uset, mult)

    X = subtree_through(T, U_DB, ROOT, N_DB)
    exits = tuple(sorted(e for e in Uset if e[0] in X and e[1] not in X))
    strict = tuple(
        e for e in exits
        if (subtree_through(U, e[0], ROOT, N_DB) & X) < X
    )
    free = tuple(
        sorted(
            e for e in mult
            if e[0] in X
            and e[1] not in X
            and mult[e] - (e in Tset) - (e in Uset) >= 1
        )
    )

    assert X == {1, 2, 3, 4}
    assert exits == ((1, 10),)
    assert not strict
    assert free and all(e[0] == U_DB for e in free)
    return {
        "old_missing": old_missing,
        "replacement": (11, 22),
        "X": tuple(sorted(X)),
        "single_exit": exits,
        "free_exits": free,
    }


def verify_variant():
    db = reversed_support_arcs()
    host = tuple(host_arcs_from_dbullet(db))
    gates = structural_gates(db)
    edges = core_edges(db)

    assert set(V1_HOST) == {0, 1, 9, 11, 13}
    assert gates["structural_ok"], gates
    assert Digraph.from_arcs(range(N_DB), db).arc_connectivity() == 3
    assert Digraph.from_arcs(range(N_HOST), host).arc_connectivity() == 3

    primitive = verify_primitive_head_block(edges)
    hard_gateway = verify_repaired_hard_gateway(db)

    w1_exits = tuple(
        sorted((u, v) for u, v in edges if u == W1_HOST and v in OUTSIDE_CORE)
    )
    returns_to_w1 = tuple(
        sorted((u, v) for u, v in edges if u in OUTSIDE_CORE and v == W1_HOST)
    )
    outside_core_lambda = induced_lambda(edges, OUTSIDE_CORE)
    low_outside_core = low_cuts(edges, OUTSIDE_CORE)
    low_outside = low_cuts(edges, OUTSIDE)

    assert w1_exits == ((10, 23),)
    assert len(returns_to_w1) >= 2
    assert outside_core_lambda == 1
    assert low_outside_core == [((12,), ((12, 23),))]
    assert low_outside == [((10,), ((10, 23),))]

    print("W2 reversal red-team")
    print(f"reversed_dbullet_arc={DELETE_ARC}->{ADD_ARC}")
    print("preserved gates:")
    print("  structural_gates=ok")
    print("  lambda(D-bullet)=lambda(host)=3")
    print(f"  primitive_head_block={primitive}")
    print(f"  repaired_hard_gateway={hard_gateway}")
    print("outside quotient:")
    print(f"  w1={W1_HOST} w1_exits={w1_exits}")
    print(f"  returns_to_w1={returns_to_w1}")
    print(f"  lambda(C[O\\{{w1}}])={outside_core_lambda}")
    print(f"  low_outside_core={low_outside_core}")
    print(f"  low_outside={low_outside}")
    print("ALL ASSERTIONS PASS: W2 is false under the current primitives")


if __name__ == "__main__":
    verify_variant()
