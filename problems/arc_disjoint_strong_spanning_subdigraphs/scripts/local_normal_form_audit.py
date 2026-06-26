"""Audit the local normal-form obligations left by D65.

D65 reduces global low-cut classification to local facts around the
sealed zero prefix Q0.  D67 fixes the endpoint bookkeeping.  This audit
checks the remaining local normal form on D42 and the D63/D66 variants:

  * low internal cuts of C[Q0];
  * low external-prefix cuts Q0 union B;
  * single-exchange mixed cuts (Q0 - h) union {w};
  * one-sided endpoint exits.

The point is not to re-enumerate all cuts; D65 already does that.  This
prints the local witnesses the symbolic proof must explain.
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

from chain_feed_deletion_stress import structural_gates  # noqa: E402
from chain_kernel_witness import dbullet_arcs  # noqa: E402
from d42_split_predicate_tester import relabel_core_arcs  # noqa: E402
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
CHORD_ENDPOINTS = {0, 1}
Q0 = frozenset((2, 3, 4, 5, 6, 7, 8))
Q_MINUS = frozenset((2, 3, 4, 5, 7, 8))
Q_PLUS = frozenset((2, 3, 4, 5, 6, 7, 8, 10))
D63_REVERSE_HEAD = (6, 5)
D66_RHO_ENTRY = (0, 5)


def out_edges(edges, side, universe=None):
    side = set(side)
    if universe is None:
        return sorted((u, v) for u, v in edges if u in side and v not in side)
    universe = set(universe)
    return sorted((u, v) for u, v in edges if u in side and v in universe - side)


def all_subsets(vertices):
    vertices = tuple(sorted(vertices))
    for mask in range(1, (1 << len(vertices)) - 1):
        yield frozenset(vertices[i] for i in range(len(vertices)) if (mask >> i) & 1)


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
    edges = tuple((V2_HOST[u], V2_HOST[v]) for u, v in core_arcs)
    outside = frozenset(V2_HOST) - Q0

    q0_out = out_edges(edges, Q0)
    assert q0_out == [], (name, q0_out)

    internal_low = []
    for S in all_subsets(Q0):
        outs = out_edges(edges, S, Q0)
        if len(outs) <= 1:
            internal_low.append((tuple(sorted(S)), outs))

    external_low = []
    for B in all_subsets(outside):
        outs = out_edges(edges, B, outside)
        if len(outs) <= 1:
            external_low.append((tuple(sorted(B)), outs))

    single_exchange = []
    for h in sorted(Q0):
        for w in sorted(outside):
            S = (set(Q0) - {h}) | {w}
            outs = out_edges(edges, S)
            internal_term = out_edges(edges, set(Q0) - {h}, Q0)
            external_term = out_edges(edges, {w}, outside)
            back_term = out_edges(edges, {w}, {w, h})
            single_exchange.append(
                (
                    len(outs),
                    h,
                    w,
                    outs,
                    internal_term,
                    external_term,
                    back_term,
                )
            )
    min_exchange = min(single_exchange)
    bad_exchange = [row for row in single_exchange if row[0] <= 1]

    endpoint_summary = []
    for q_name, Q in (("Q-", Q_MINUS), ("Q0", Q0), ("Q+", Q_PLUS)):
        endpoint_exits = sorted(
            (u, v) for u, v in host if u in Q and v in CHORD_ENDPOINTS
        )
        endpoint_entries = sorted(
            (u, v) for u, v in host if u in CHORD_ENDPOINTS and v in Q
        )
        assert not endpoint_exits, (name, q_name, endpoint_exits)
        endpoint_summary.append((q_name, endpoint_entries))

    reverse_head = D63_REVERSE_HEAD in extras
    expected_internal = [] if reverse_head else [(tuple(sorted(Q_MINUS)), [(2, 6)])]
    assert internal_low == expected_internal, (name, internal_low)
    assert external_low == [((10,), [(10, 23)])], (name, external_low)
    assert not bad_exchange, (name, bad_exchange)

    print(f"\n{name}")
    print(f"  extras={extras}")
    print(f"  internal_low={internal_low}")
    print(f"  external_low={external_low}")
    print(f"  min_single_exchange={min_exchange[:4]}")
    print(f"  endpoint_entries={endpoint_summary}")
    return {
        "internal_low": internal_low,
        "external_low": external_low,
        "min_exchange": min_exchange,
    }


def main():
    print("Local normal-form audit")
    scenario("D42 original", ())
    scenario("D63 reverse-head", (D63_REVERSE_HEAD,))
    scenario("D66 rho-entry", (D66_RHO_ENTRY,))
    scenario("D63+D66 combined", (D63_REVERSE_HEAD, D66_RHO_ENTRY))
    print("\nALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
