"""Audit the tight AOC rows after isolating the top-support endpoint.

D79 closes the endpoint singleton tau conditionally via SLE.  This script
prints and asserts the remaining tight AOC rows on the accepted variants, so
the next symbolic proof can target concrete cut types.
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
    containing_rows,
    core_edges,
    make_db,
    not_containing_rows,
)
from local_normal_form_audit import D63_REVERSE_HEAD, D66_RHO_ENTRY  # noqa: E402


TAU = 23
MID = 12
ROOT_COMPLEMENT = tuple(sorted(OUTSIDE_CORE - {14}))


def tight_profiles(edges):
    no_w1 = [row for row in not_containing_rows(edges) if row[0] == 2]
    with_w1 = [row for row in containing_rows(edges) if row[0] == 2]
    return no_w1, with_w1


def side_set(row):
    return row[1]


def scenario(name, extras=(), reverse_support=False):
    edges = core_edges(make_db(extras=extras, reverse_support=reverse_support))
    no_w1, with_w1 = tight_profiles(edges)
    no_sides = tuple(side_set(row) for row in no_w1)
    with_sides = tuple(side_set(row) for row in with_w1)

    if reverse_support:
        assert no_sides == ((MID,), (TAU,)), (name, no_w1)
        assert with_sides == (
            (MID,),
            ROOT_COMPLEMENT,
            (MID, TAU),
            (TAU,),
        ), (name, with_w1)
    else:
        assert no_sides == ((TAU,),), (name, no_w1)
        assert with_sides == (ROOT_COMPLEMENT, (TAU,)), (name, with_w1)

    print(f"\n{name}")
    print(f"  reverse_support={reverse_support} extras={extras}")
    print(f"  tight_no_w1={no_w1}")
    print(f"  tight_with_w1={with_w1}")
    return no_w1, with_w1


def main():
    print("Endpoint-reduced AOC profile audit")
    scenario("D42 original")
    scenario("D63 reverse-head", extras=(D63_REVERSE_HEAD,))
    scenario("D66 rho-entry", extras=(D66_RHO_ENTRY,))
    scenario("D63+D66", extras=(D63_REVERSE_HEAD, D66_RHO_ENTRY))
    scenario("D74 support reversal", reverse_support=True)
    scenario("D74+D63", extras=(D63_REVERSE_HEAD,), reverse_support=True)
    scenario("D74+D66", extras=(D66_RHO_ENTRY,), reverse_support=True)
    scenario("D74+D63+D66", extras=(D63_REVERSE_HEAD, D66_RHO_ENTRY), reverse_support=True)
    print("\nALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
