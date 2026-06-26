"""Red-team rho-label endpoint-cleanliness.

D62 recorded endpoint-cleanliness as both:

  * no chord endpoint exits from the active prefix, and
  * no chord endpoint entries into the active prefix.

The first condition is structural: a rho-label exit from Q would add a
host out-arc from Q to a chord endpoint and would change the
prefix-plus-pending out-cut formula.  The second condition is not
forced by the sealed-block/CL/DT gates and is not needed for directed
out-cut bookkeeping.

This script adds a single rho-entry label rho -> head in D-bullet labels
(host arc 0 -> 6).  It preserves the sealed-chain gates and the split
core low-cut profile but creates an endpoint entry into Q0 and Q+.
The D62 formula still holds if endpoint entries are ignored, because
they are arcs entering the cut, not leaving it.
"""
from __future__ import annotations

import itertools
import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chain_kernel_witness import dbullet_arcs  # noqa: E402
from d42_split_predicate_tester import (  # noqa: E402
    deficient_core_cuts,
    relabel_core_arcs,
)
from structural_core_prefix_redteam import (  # noqa: E402
    host_from_db,
    verify_hard_gateway,
)
from chain_feed_deletion_stress import structural_gates  # noqa: E402
from digraph import Digraph  # noqa: E402
from generators.near_split import is_one_zero_near_split  # noqa: E402


EXTRA_RHO_ENTRY = (0, 5)  # D-bullet labels; host label is 0 -> 6.
N_HOST = 24
V1_HOST = (0, 1, 9, 11, 13)
V2_HOST = tuple(v for v in range(N_HOST) if v not in V1_HOST)
PENDING = (9, 11, 13)
CHORD_ENDPOINTS = {0, 1}
PREFIXES = (
    ("Q-", frozenset((2, 3, 4, 5, 7, 8)), 1),
    ("Q0", frozenset((2, 3, 4, 5, 6, 7, 8)), 0),
    ("Q+", frozenset((2, 3, 4, 5, 6, 7, 8, 10)), 1),
)


def out_cut(arcs, side):
    side = set(side)
    return sum(1 for u, v in arcs if u in side and v not in side)


def cut_vertices(v2, mask):
    return tuple(v2[i] for i in range(len(v2)) if (mask >> i) & 1)


def main():
    db = tuple(dbullet_arcs()) + (EXTRA_RHO_ENTRY,)
    host = tuple(host_from_db(db))
    host_set = set(host)
    assert len(host) == len(host_set)
    near_ok, near_reason = is_one_zero_near_split(
        Digraph.from_arcs(range(N_HOST), host),
        V1_HOST,
        V2_HOST,
    )
    assert near_ok, near_reason
    gates = structural_gates(db)
    assert gates["structural_ok"], gates
    assert verify_hard_gateway(Counter(db)) == [(1, 10)]

    core_arcs = relabel_core_arcs(host, V2_HOST)
    low_cuts = [
        (core_out, cut_vertices(V2_HOST, mask))
        for mask, core_out in deficient_core_cuts(len(V2_HOST), core_arcs)
    ]
    assert low_cuts == [
        (1, (2, 3, 4, 5, 7, 8)),
        (0, (2, 3, 4, 5, 6, 7, 8)),
        (1, (2, 3, 4, 5, 6, 7, 8, 10)),
    ]

    print("Rho-entry endpoint-cleanliness red-team")
    print(f"extra_dbullet_arc={EXTRA_RHO_ENTRY} extra_host_arc={(0, 6)}")
    print("preserved gates:")
    print("  simple near-split host: yes")
    print("  structural sealed-chain gates: yes")
    print("  hard_gateway_U_exits=[(1, 10)]")
    print(f"  low_cuts={low_cuts}")

    for name, Q, core_out in PREFIXES:
        endpoint_entries = sorted(
            (u, v) for u, v in host if u in CHORD_ENDPOINTS and v in Q
        )
        endpoint_exits = sorted(
            (u, v) for u, v in host if u in Q and v in CHORD_ENDPOINTS
        )
        print(f"\n{name}: core_out={core_out} cut={tuple(sorted(Q))}")
        print(f"  endpoint_entries={endpoint_entries}")
        print(f"  endpoint_exits={endpoint_exits}")
        if name in {"Q0", "Q+"}:
            assert endpoint_entries == [(0, 6)]
        else:
            assert endpoint_entries == []
        assert endpoint_exits == []

        table = []
        for s in PENDING:
            e = sum(1 for u, v in host if u in Q and v == s)
            f = sum(1 for u, v in host if u == s and v in set(V2_HOST) - Q)
            table.append((s, e, f))

        for r in range(len(PENDING) + 1):
            for J_tuple in itertools.combinations(PENDING, r):
                J = set(J_tuple)
                side = set(Q) | J
                actual = out_cut(host, side)
                formula = core_out
                for s, e, f in table:
                    formula += f if s in J else e
                assert actual == formula, (name, J_tuple, actual, formula)
                assert actual >= 3

    print("\nThe endpoint entry violates the old no-entry cleanliness clause,")
    print("but the out-cut formula remains valid because endpoint entries")
    print("do not leave Q union J.")
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
