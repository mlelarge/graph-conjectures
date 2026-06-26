"""Audit the one-sided prefix-plus-pending formula.

D66 refuted the old two-sided endpoint-cleanliness condition: rho-label
entries into an active prefix are not forced.  They are also unnecessary
for directed out-cut bookkeeping.  This script verifies the corrected
one-sided formula on four variants:

  * D42 original;
  * D63 reverse-head perturbation;
  * D66 rho-entry perturbation;
  * both perturbations at once.

For each candidate prefix Q and each pending subset J, it checks

    d^+(Q union J)
      = b(Q) + sum_{i notin J} e_i(Q) + sum_{i in J} f_i(Q),

requiring no endpoint exits from Q but allowing endpoint entries into Q.
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
from chain_feed_deletion_stress import structural_gates  # noqa: E402
from d42_split_predicate_tester import (  # noqa: E402
    deficient_core_cuts,
    relabel_core_arcs,
)
from digraph import Digraph  # noqa: E402
from generators.near_split import is_one_zero_near_split  # noqa: E402
from structural_core_prefix_redteam import (  # noqa: E402
    host_from_db,
    verify_hard_gateway,
)


N_HOST = 24
N_DB = 23
V1_HOST = (0, 1, 9, 11, 13)
V2_HOST = tuple(v for v in range(N_HOST) if v not in V1_HOST)
PENDING = (9, 11, 13)
CHORD_ENDPOINTS = {0, 1}

D63_REVERSE_HEAD = (6, 5)  # D-bullet labels; host 7 -> 6.
D66_RHO_ENTRY = (0, 5)     # D-bullet labels; host 0 -> 6.

PREFIXES = (
    ("Q-", frozenset((2, 3, 4, 5, 7, 8))),
    ("Q0", frozenset((2, 3, 4, 5, 6, 7, 8))),
    ("Q+", frozenset((2, 3, 4, 5, 6, 7, 8, 10))),
)


def out_cut(arcs, side):
    side = set(side)
    return sum(1 for u, v in arcs if u in side and v not in side)


def cut_vertices(v2, mask):
    return tuple(v2[i] for i in range(len(v2)) if (mask >> i) & 1)


def expected_lows(reverse_head):
    if reverse_head:
        return [
            (0, (2, 3, 4, 5, 6, 7, 8)),
            (1, (2, 3, 4, 5, 6, 7, 8, 10)),
        ]
    return [
        (1, (2, 3, 4, 5, 7, 8)),
        (0, (2, 3, 4, 5, 6, 7, 8)),
        (1, (2, 3, 4, 5, 6, 7, 8, 10)),
    ]


def scenario(name, extras):
    db = tuple(dbullet_arcs()) + tuple(extras)
    host = tuple(host_from_db(db))
    assert len(host) == len(set(host)), name
    near_ok, near_reason = is_one_zero_near_split(
        Digraph.from_arcs(range(N_HOST), host),
        V1_HOST,
        V2_HOST,
    )
    assert near_ok, (name, near_reason)
    assert Digraph.from_arcs(range(N_HOST), host).arc_connectivity() == 3
    assert Digraph.from_arcs(range(N_DB), db).arc_connectivity() == 3
    gates = structural_gates(db)
    assert gates["structural_ok"], (name, gates)
    assert verify_hard_gateway(Counter(db)) == [(1, 10)]

    core_arcs = relabel_core_arcs(host, V2_HOST)
    low_cuts = [
        (core_out, cut_vertices(V2_HOST, mask))
        for mask, core_out in deficient_core_cuts(len(V2_HOST), core_arcs)
    ]
    reverse_head = D63_REVERSE_HEAD in extras
    assert low_cuts == expected_lows(reverse_head), (name, low_cuts)

    print(f"\n{name}")
    print(f"  extras={extras}")
    print(f"  low_cuts={low_cuts}")

    summary = []
    for q_name, Q in PREFIXES:
        core_out = out_cut(
            [(V2_HOST[u], V2_HOST[v]) for u, v in core_arcs],
            Q,
        )
        endpoint_entries = sorted(
            (u, v) for u, v in host if u in CHORD_ENDPOINTS and v in Q
        )
        endpoint_exits = sorted(
            (u, v) for u, v in host if u in Q and v in CHORD_ENDPOINTS
        )
        assert not endpoint_exits, (name, q_name, endpoint_exits)

        table = []
        min_sum = 0
        for s in PENDING:
            noncore_in = sorted(u for u, v in host if v == s and u not in V2_HOST)
            noncore_out = sorted(v for u, v in host if u == s and v not in V2_HOST)
            e = sum(1 for u, v in host if u in Q and v == s)
            f = sum(1 for u, v in host if u == s and v in set(V2_HOST) - Q)
            assert not noncore_in, (name, q_name, s, noncore_in)
            assert not noncore_out, (name, q_name, s, noncore_out)
            table.append((s, e, f))
            min_sum += min(e, f)

        min_actual = None
        for r in range(len(PENDING) + 1):
            for J_tuple in itertools.combinations(PENDING, r):
                J = set(J_tuple)
                side = set(Q) | J
                actual = out_cut(host, side)
                formula = core_out
                for s, e, f in table:
                    formula += f if s in J else e
                assert actual == formula, (name, q_name, J_tuple, actual, formula)
                assert actual >= 3, (name, q_name, J_tuple, actual)
                min_actual = actual if min_actual is None else min(min_actual, actual)

        summary.append((q_name, core_out, endpoint_entries, min_sum, min_actual))

    for q_name, core_out, endpoint_entries, min_sum, min_actual in summary:
        print(
            f"  {q_name}: core_out={core_out} "
            f"endpoint_entries={endpoint_entries} "
            f"sum_min={min_sum} min_Q_union_J={min_actual}"
        )
    return summary


def main():
    print("One-sided prefix-plus-pending audit")
    original = scenario("D42 original", ())
    reverse = scenario("D63 reverse-head", (D63_REVERSE_HEAD,))
    rho_entry = scenario("D66 rho-entry", (D66_RHO_ENTRY,))
    combined = scenario("D63+D66 combined", (D63_REVERSE_HEAD, D66_RHO_ENTRY))

    assert [row[1] for row in original] == [1, 0, 1]
    assert [row[1] for row in reverse] == [2, 0, 1]
    assert [row[1] for row in rho_entry] == [1, 0, 1]
    assert [row[1] for row in combined] == [2, 0, 1]
    assert rho_entry[1][2] == [(0, 6)]
    assert rho_entry[2][2] == [(0, 6)]
    assert combined[1][2] == [(0, 6)]
    assert combined[2][2] == [(0, 6)]

    print("\nALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
