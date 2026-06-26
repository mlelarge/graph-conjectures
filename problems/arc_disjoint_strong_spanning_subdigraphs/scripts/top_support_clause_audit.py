"""Audit the top-support two-exit clause isolated by D76.

The proposed endpoint primitive says: if w1 has the unique outside exit
w1->tau, then tau has at least two exits inside O'.  On D42 tau is host
vertex 23.  D76 found that the only single-reversal AOC failures are exactly
the variants that reduce tau's outside-core out-degree from two to one.
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

from attached_outside_cut_audit import (  # noqa: E402
    OUTSIDE_CORE,
    W1,
    arcs_between,
    containing_rows,
    core_edges,
    low_outside_rows,
    make_db,
    not_containing_rows,
)
from chain_feed_deletion_stress import structural_gates  # noqa: E402
from chain_kernel_witness import dbullet_arcs  # noqa: E402
from local_normal_form_audit import D63_REVERSE_HEAD, D66_RHO_ENTRY  # noqa: E402


def aoc_ok(edges):
    return (
        arcs_between(edges, {W1}, OUTSIDE_CORE) == ((10, 23),)
        and not_containing_rows(edges)[0][0] >= 2
        and containing_rows(edges)[0][0] >= 2
        and low_outside_rows(edges) == [((10,), ((10, 23),))]
    )


def top_support_profile(edges):
    w1_exits = arcs_between(edges, {W1}, OUTSIDE_CORE)
    assert len(w1_exits) == 1
    tau = w1_exits[0][1]
    tau_exits = arcs_between(edges, {tau}, OUTSIDE_CORE - {tau})
    return tau, tau_exits


def scenario(name, extras=(), reverse_support=False):
    db = make_db(extras=extras, reverse_support=reverse_support)
    edges = core_edges(db)
    tau, tau_exits = top_support_profile(edges)
    ok = aoc_ok(edges)
    assert tau == 23
    assert len(tau_exits) >= 2
    assert ok
    print(f"{name}: tau={tau} tau_exits={tau_exits} AOC=ok")


def single_reversal_neighbourhood():
    base = tuple(dbullet_arcs())
    mult = Counter(base)
    rows = []
    for delete_arc in sorted(set(base)):
        add_arc = (delete_arc[1], delete_arc[0])
        if delete_arc[0] == delete_arc[1] or add_arc in mult:
            continue
        arcs = list(base)
        arcs.remove(delete_arc)
        arcs.append(add_arc)
        try:
            gates = structural_gates(tuple(arcs))
        except Exception:
            continue
        if not gates["structural_ok"]:
            continue
        edges = core_edges(tuple(arcs))
        tau, tau_exits = top_support_profile(edges)
        rows.append(
            {
                "reversal": (delete_arc, add_arc),
                "tau": tau,
                "tau_exits": tau_exits,
                "top_ok": len(tau_exits) >= 2,
                "aoc_ok": aoc_ok(edges),
            }
        )
    top_bad = [row for row in rows if not row["top_ok"]]
    aoc_bad = [row for row in rows if not row["aoc_ok"]]
    assert len(rows) == 27
    assert top_bad == aoc_bad
    assert {
        row["reversal"] for row in top_bad
    } == {
        ((22, 20), (20, 22)),
        ((22, 21), (21, 22)),
    }
    print("single-reversal neighbourhood:")
    print(f"  structural_survivors={len(rows)}")
    print(f"  top_support_bad={len(top_bad)}")
    for row in top_bad:
        print(f"  bad={row['reversal']} tau_exits={row['tau_exits']}")


def main():
    print("Top-support two-exit audit")
    scenario("D42 original")
    scenario("D63 reverse-head", extras=(D63_REVERSE_HEAD,))
    scenario("D66 rho-entry", extras=(D66_RHO_ENTRY,))
    scenario("D63+D66", extras=(D63_REVERSE_HEAD, D66_RHO_ENTRY))
    scenario("D74 support reversal", reverse_support=True)
    scenario("D74+D63", extras=(D63_REVERSE_HEAD,), reverse_support=True)
    scenario("D74+D66", extras=(D66_RHO_ENTRY,), reverse_support=True)
    scenario("D74+D63+D66", extras=(D63_REVERSE_HEAD, D66_RHO_ENTRY), reverse_support=True)
    single_reversal_neighbourhood()
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
