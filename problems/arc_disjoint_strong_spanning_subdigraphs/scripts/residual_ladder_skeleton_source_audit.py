"""Audit source clauses for the residual ladder skeleton.

D83 proves ER-4 from a small ladder skeleton.  This script assigns every
skeleton arc to a local sealed-chain source clause: active first successor,
semicomplete return, distance-graded R2 boundary, root/spare domination,
or support shortcut.  The point is to make the next symbolic derivation
checkable at the clause level rather than as an unlabelled arc list.
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from attached_outside_cut_audit import (  # noqa: E402
    OUTSIDE_CORE,
    W1,
    core_edges,
    make_db,
)
from local_normal_form_audit import D63_REVERSE_HEAD, D66_RHO_ENTRY  # noqa: E402
from residual_ladder_separator_audit import (  # noqa: E402
    H,
    L,
    M,
    P,
    R0,
    S,
    TAU,
    ladder_skeleton,
)


def add_complete(out, category, left, right):
    out[category].update((u, v) for u in left for v in right)


def source_categories(weak_middle=False):
    cats = defaultdict(set)

    cats["active_first_successor"].add((W1, TAU))
    cats["semicomplete_active_returns"].update(
        (x, W1) for x in OUTSIDE_CORE - {TAU}
    )

    cats["middle_to_top"].add((M, TAU))
    if not weak_middle:
        cats["robust_middle_support"].add((M, min(H)))

    add_complete(cats, "top_two_fan", {TAU}, S)
    add_complete(cats, "r2_boundary_S_to_H", S, H)
    add_complete(cats, "r2_boundary_H_to_L", H, L)
    add_complete(cats, "r2_boundary_L_to_P", L, P)
    add_complete(cats, "root_spare_to_r0", P, {R0})

    add_complete(cats, "shortcut_S_to_M", S, {M})
    cats["internal_S"].add((21, 22))

    add_complete(cats, "shortcut_H_to_T", H, {TAU})
    cats["shortcut_H_to_M"].add((20, M))
    cats["internal_H"].add((19, 20))

    add_complete(cats, "shortcut_L_to_MTS", L, {M, TAU} | set(S))
    cats["internal_L"].add((17, 18))

    add_complete(cats, "root_spare_domination", P, {M, TAU} | set(S) | set(H))
    cats["internal_P"].update(((15, 16), (16, 15)))

    add_complete(cats, "terminal_support_backfan", {R0}, {M, TAU} | set(S) | set(H) | set(L))

    return {k: tuple(sorted(v)) for k, v in sorted(cats.items())}


def flatten(cats):
    arcs = set()
    for values in cats.values():
        arcs.update(values)
    return arcs


def scenario(name, extras=(), reverse_support=False):
    cats = source_categories(weak_middle=reverse_support)
    sourced = flatten(cats)
    skeleton = set(ladder_skeleton(weak_middle=reverse_support))
    actual = set(core_edges(make_db(extras=extras, reverse_support=reverse_support)))

    assert sourced == skeleton, (name, sorted(skeleton - sourced), sorted(sourced - skeleton))
    assert not (skeleton - actual), (name, sorted(skeleton - actual))

    print(f"\n{name}")
    print(f"  reverse_support={reverse_support} extras={extras}")
    print(f"  skeleton_arcs={len(skeleton)} categories={len(cats)}")
    for category, arcs in cats.items():
        print(f"  {category}: {len(arcs)} {arcs}")


def main():
    print("Residual ladder skeleton source audit")
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
