"""Audit the residual support-ladder separator used for ER-4.

D82 leaves one endpoint-reduced AOC clause: every unlisted eta/zeta row
has value at least three.  This script builds the small directed ladder
skeleton that is enough to force that residual slack, verifies the skeleton
is present in the accepted normal forms, and checks ER-4 on the skeleton
itself.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from attached_outside_cut_audit import (  # noqa: E402
    OUTSIDE_CORE,
    W1,
    containing_rows,
    core_edges,
    make_db,
    nonempty_subsets,
    not_containing_rows,
)
from local_normal_form_audit import D63_REVERSE_HEAD, D66_RHO_ENTRY  # noqa: E402


M = 12
R0 = 14
P = frozenset((15, 16))
L = frozenset((17, 18))
H = frozenset((19, 20))
S = frozenset((21, 22))
TAU = 23
ROOT_COMPLEMENT = frozenset(OUTSIDE_CORE - {R0})


def arcs_between(edges, left, right):
    left = set(left)
    right = set(right)
    return tuple(sorted((u, v) for u, v in edges if u in left and v in right))


def add_complete(arcs, left, right):
    for u in left:
        for v in right:
            arcs.add((u, v))


def ladder_skeleton(weak_middle=False):
    """Return the minimal named ladder skeleton used in the proof."""
    arcs = set()

    arcs.add((W1, TAU))
    for x in OUTSIDE_CORE - {TAU}:
        arcs.add((x, W1))

    arcs.add((M, TAU))
    if not weak_middle:
        arcs.add((M, min(H)))

    add_complete(arcs, {TAU}, S)
    add_complete(arcs, S, H)
    add_complete(arcs, S, {M})
    arcs.add((21, 22))

    add_complete(arcs, H, L)
    add_complete(arcs, H, {TAU})
    arcs.add((20, M))
    arcs.add((19, 20))

    add_complete(arcs, L, P)
    add_complete(arcs, L, {M, TAU} | S)
    arcs.add((17, 18))

    add_complete(arcs, P, {R0, M, TAU} | S | H)
    arcs.add((15, 16))
    arcs.add((16, 15))

    add_complete(arcs, {R0}, {M, TAU} | S | H | L)

    return tuple(sorted(arcs))


def all_proper_subsets(vertices):
    vertices = tuple(sorted(vertices))
    for mask in range(1, (1 << len(vertices)) - 1):
        yield frozenset(vertices[i] for i in range(len(vertices)) if (mask >> i) & 1)


def eta_rows(edges):
    rows = []
    for B in nonempty_subsets(OUTSIDE_CORE):
        internal = arcs_between(edges, B, OUTSIDE_CORE - B)
        to_w1 = arcs_between(edges, B, {W1})
        rows.append((len(internal) + len(to_w1), tuple(sorted(B)), internal, to_w1))
    return sorted(rows)


def zeta_rows(edges):
    rows = []
    for A in all_proper_subsets(OUTSIDE_CORE):
        internal = arcs_between(edges, A, OUTSIDE_CORE - A)
        from_w1 = arcs_between(edges, {W1}, OUTSIDE_CORE - A)
        rows.append((len(internal) + len(from_w1), tuple(sorted(A)), internal, from_w1))
    return sorted(rows)


def assert_er4(rows_eta, rows_zeta, weak_middle):
    excluded_eta = {tuple(sorted({TAU}))}
    excluded_zeta = {tuple(sorted({TAU})), tuple(sorted(ROOT_COMPLEMENT))}
    if weak_middle:
        excluded_eta.add(tuple(sorted({M})))
        excluded_zeta.add(tuple(sorted({M})))
        excluded_zeta.add(tuple(sorted({M, TAU})))

    bad_eta = [
        row for row in rows_eta
        if row[1] not in excluded_eta and row[0] < 3
    ]
    bad_zeta = [
        row for row in rows_zeta
        if row[1] not in excluded_zeta and row[0] < 3
    ]
    assert not bad_eta, bad_eta
    assert not bad_zeta, bad_zeta


def low_rows(rows):
    return tuple(row for row in rows if row[0] <= 3)


def scenario(name, extras=(), reverse_support=False):
    actual = set(core_edges(make_db(extras=extras, reverse_support=reverse_support)))
    skeleton = set(ladder_skeleton(weak_middle=reverse_support))
    missing = sorted(skeleton - actual)
    assert not missing, (name, missing)

    sk_eta = eta_rows(skeleton)
    sk_zeta = zeta_rows(skeleton)
    assert_er4(sk_eta, sk_zeta, reverse_support)

    # The full quotient has all skeleton arcs plus extra arcs, so the same
    # residual lower bounds hold by monotonicity.  Keep the direct check as an
    # audit guard against wrong exclusions.
    actual_eta = not_containing_rows(actual)
    actual_zeta = containing_rows(actual)
    assert_er4(actual_eta, actual_zeta, reverse_support)

    print(f"\n{name}")
    print(f"  reverse_support={reverse_support} extras={extras}")
    print(f"  skeleton_arcs={len(skeleton)}")
    print(f"  skeleton_low_eta={low_rows(sk_eta)}")
    print(f"  skeleton_low_zeta={low_rows(sk_zeta)}")
    print(f"  actual_low_eta={low_rows(actual_eta)}")
    print(f"  actual_low_zeta={low_rows(actual_zeta)}")


def main():
    print("Residual ladder separator audit")
    scenario("D42 original")
    scenario("D63 reverse-head", extras=(D63_REVERSE_HEAD,))
    scenario("D66 rho-entry", extras=(D66_RHO_ENTRY,))
    scenario("D63+D66", extras=(D63_REVERSE_HEAD, D66_RHO_ENTRY))
    scenario("D74 support reversal", reverse_support=True)
    scenario("D74+D63", extras=(D63_REVERSE_HEAD,), reverse_support=True)
    scenario("D74+D66", extras=(D66_RHO_ENTRY,), reverse_support=True)
    scenario(
        "D74+D63+D66",
        extras=(D63_REVERSE_HEAD, D66_RHO_ENTRY),
        reverse_support=True,
    )
    print("\nALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
