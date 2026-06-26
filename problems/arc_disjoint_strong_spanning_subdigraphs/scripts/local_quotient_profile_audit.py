"""Audit the quotient form behind the D68 local normal form.

D70 rewrites the remaining local proof obligations as two quotient
expansion statements:

  * small in-cuts of the head block Q0;
  * small out-cuts of the outside quotient O=C\\Q0.

This script checks that formulation on the D42/D63/D66 variants and
records the singleton terms used to exclude single-exchange cuts.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chain_kernel_witness import dbullet_arcs  # noqa: E402
from local_normal_form_audit import (  # noqa: E402
    D63_REVERSE_HEAD,
    D66_RHO_ENTRY,
    Q0,
    V2_HOST,
    all_subsets,
    host_from_db,
    out_edges,
    relabel_core_arcs,
)


OUTSIDE = frozenset(V2_HOST) - Q0


def core_edges(extras):
    db = tuple(dbullet_arcs()) + tuple(extras)
    host = tuple(host_from_db(db))
    core_arcs = relabel_core_arcs(host, V2_HOST)
    return tuple((V2_HOST[u], V2_HOST[v]) for u, v in core_arcs)


def arcs_between(edges, left, right):
    left = set(left)
    right = set(right)
    return sorted((u, v) for u, v in edges if u in left and v in right)


def quotient_profile(name, extras):
    edges = core_edges(extras)

    q0_out = out_edges(edges, Q0)
    assert q0_out == [], (name, q0_out)

    low_head_complements = []
    for T in all_subsets(Q0):
        incoming = arcs_between(edges, Q0 - T, T)
        if len(incoming) <= 1:
            low_head_complements.append((tuple(sorted(T)), tuple(incoming)))

    low_outside_cuts = []
    for B in all_subsets(OUTSIDE):
        outgoing = out_edges(edges, B, OUTSIDE)
        if len(outgoing) <= 1:
            low_outside_cuts.append((tuple(sorted(B)), tuple(outgoing)))

    singleton_rows = []
    zero_zero = []
    for h in sorted(Q0):
        in_to_h = arcs_between(edges, Q0 - {h}, {h})
        for w in sorted(OUTSIDE):
            out_of_w = out_edges(edges, {w}, OUTSIDE)
            back = arcs_between(edges, {w}, {h})
            total = len(in_to_h) + len(out_of_w) + len(back)
            row = (total, h, w, tuple(in_to_h), tuple(out_of_w), tuple(back))
            singleton_rows.append(row)
            if not in_to_h and not out_of_w:
                zero_zero.append(row)

    min_singleton = min(singleton_rows)

    reverse_head = D63_REVERSE_HEAD in extras
    expected_head = [] if reverse_head else [((6,), ((2, 6),))]
    expected_outside = [((10,), ((10, 23),))]

    assert low_head_complements == expected_head, (name, low_head_complements)
    assert low_outside_cuts == expected_outside, (name, low_outside_cuts)
    assert not zero_zero, (name, zero_zero)
    assert min_singleton[0] >= 2, (name, min_singleton)

    print(f"\n{name}")
    print(f"  extras={extras}")
    print(f"  low_head_complements={low_head_complements}")
    print(f"  low_outside_cuts={low_outside_cuts}")
    print(f"  min_singleton_terms={min_singleton}")


def main():
    print("Local quotient profile audit")
    quotient_profile("D42 original", ())
    quotient_profile("D63 reverse-head", (D63_REVERSE_HEAD,))
    quotient_profile("D66 rho-entry", (D66_RHO_ENTRY,))
    quotient_profile("D63+D66 combined", (D63_REVERSE_HEAD, D66_RHO_ENTRY))
    print("\nALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
