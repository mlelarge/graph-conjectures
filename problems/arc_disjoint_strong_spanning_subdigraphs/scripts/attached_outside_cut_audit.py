"""Audit the attachment-aware replacement for W2.

D74 shows that W2, lambda(C[O\\{w1}]) >= 2, is too strong: a weak cut in
O' can be harmless when it exits to the first successor w1.  This script
checks the exact weaker certificate that still implies FSQ.

Let O' = O\\{w1}.  The attached outside-cut certificate is:

  AOC-1: w1 has the single allowed outside exit;
  AOC-2: every nonempty B subseteq O' satisfies
         d^+_{O'}(B) + d(B,{w1}) >= 2;
  AOC-3: every nonempty proper A subset O' satisfies
         d^+_{O'}(A) + d({w1},O'\\A) >= 2.

These are exactly the cut counts for outside cuts not containing w1 and
containing w1, respectively.  The singleton {w1} is the only permitted low
outside cut.
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

from chain_feed_deletion_stress import host_arcs_from_dbullet, structural_gates  # noqa: E402
from chain_kernel_witness import dbullet_arcs  # noqa: E402
from d42_split_predicate_tester import relabel_core_arcs  # noqa: E402
from digraph import Digraph  # noqa: E402
from local_normal_form_audit import (  # noqa: E402
    D63_REVERSE_HEAD,
    D66_RHO_ENTRY,
    Q0,
    V2_HOST,
    all_subsets,
    out_edges,
)


N_DB = 23
N_HOST = 24
W1 = 10
OUTSIDE = frozenset(V2_HOST) - Q0
OUTSIDE_CORE = OUTSIDE - {W1}
D74_DELETE = (11, 18)
D74_ADD = (18, 11)


def nonempty_subsets(vertices):
    vertices = tuple(sorted(vertices))
    for mask in range(1, 1 << len(vertices)):
        yield frozenset(
            vertices[i] for i in range(len(vertices)) if (mask >> i) & 1
        )


def make_db(extras=(), reverse_support=False):
    arcs = list(dbullet_arcs())
    if reverse_support:
        assert arcs.count(D74_DELETE) == 1
        assert D74_ADD not in arcs
        arcs.remove(D74_DELETE)
        arcs.append(D74_ADD)
    arcs.extend(extras)
    return tuple(arcs)


def core_edges(db_arcs):
    host = tuple(host_arcs_from_dbullet(db_arcs))
    assert len(host) == len(set(host))
    core_arcs = relabel_core_arcs(host, V2_HOST)
    return tuple((V2_HOST[u], V2_HOST[v]) for u, v in core_arcs)


def arcs_between(edges, left, right):
    left = set(left)
    right = set(right)
    return tuple(sorted((u, v) for u, v in edges if u in left and v in right))


def not_containing_rows(edges):
    rows = []
    for B in nonempty_subsets(OUTSIDE_CORE):
        internal = arcs_between(edges, B, OUTSIDE_CORE - B)
        to_w1 = arcs_between(edges, B, {W1})
        rows.append((len(internal) + len(to_w1), tuple(sorted(B)), internal, to_w1))
    return sorted(rows)


def containing_rows(edges):
    rows = []
    for A in all_subsets(OUTSIDE_CORE):
        internal = arcs_between(edges, A, OUTSIDE_CORE - A)
        from_w1 = arcs_between(edges, {W1}, OUTSIDE_CORE - A)
        rows.append((len(internal) + len(from_w1), tuple(sorted(A)), internal, from_w1))
    return sorted(rows)


def low_outside_rows(edges):
    rows = []
    for B in all_subsets(OUTSIDE):
        outgoing = tuple(out_edges(edges, B, OUTSIDE))
        if len(outgoing) <= 1:
            rows.append((tuple(sorted(B)), outgoing))
    return rows


def audit(name, extras=(), reverse_support=False):
    db = make_db(extras=extras, reverse_support=reverse_support)
    edges = core_edges(db)
    host = tuple(host_arcs_from_dbullet(db))
    gates = structural_gates(db)

    assert gates["structural_ok"], (name, gates)
    assert Digraph.from_arcs(range(N_DB), db).arc_connectivity() == 3
    assert Digraph.from_arcs(range(N_HOST), host).arc_connectivity() == 3

    w1_exits = arcs_between(edges, {W1}, OUTSIDE_CORE)
    returns_to_w1 = arcs_between(edges, OUTSIDE_CORE, {W1})
    rows_no_w1 = not_containing_rows(edges)
    rows_with_w1 = containing_rows(edges)
    low_outside = low_outside_rows(edges)

    assert w1_exits == ((10, 23),), (name, w1_exits)
    assert rows_no_w1[0][0] >= 2, (name, rows_no_w1[:5])
    assert rows_with_w1[0][0] >= 2, (name, rows_with_w1[:5])
    assert low_outside == [((10,), ((10, 23),))], (name, low_outside)

    print(f"\n{name}")
    print(f"  extras={extras} reverse_support={reverse_support}")
    print(f"  w1_exits={w1_exits}")
    print(f"  returns_to_w1={returns_to_w1}")
    print(f"  min_no_w1={rows_no_w1[0]}")
    print(f"  min_with_w1={rows_with_w1[0]}")
    print(f"  low_outside={low_outside}")
    return {
        "w1_exits": w1_exits,
        "returns_to_w1": returns_to_w1,
        "min_no_w1": rows_no_w1[0],
        "min_with_w1": rows_with_w1[0],
        "low_outside": low_outside,
    }


def main():
    print("Attached outside-cut audit")
    audit("D42 original")
    audit("D63 reverse-head", extras=(D63_REVERSE_HEAD,))
    audit("D66 rho-entry", extras=(D66_RHO_ENTRY,))
    audit("D63+D66 combined", extras=(D63_REVERSE_HEAD, D66_RHO_ENTRY))
    audit("D74 support reversal", reverse_support=True)
    audit("D74+D63", extras=(D63_REVERSE_HEAD,), reverse_support=True)
    audit("D74+D66", extras=(D66_RHO_ENTRY,), reverse_support=True)
    audit(
        "D74+D63+D66",
        extras=(D63_REVERSE_HEAD, D66_RHO_ENTRY),
        reverse_support=True,
    )
    print("\nALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
