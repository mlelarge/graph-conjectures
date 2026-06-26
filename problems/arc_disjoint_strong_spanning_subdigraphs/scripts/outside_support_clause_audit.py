"""Audit the endpoint-reduced outside-support clauses.

D81 proves AOC from ER-0--ER-4.  This audit checks the concrete clauses
that the next symbolic derivation has to explain:

  * active first successor: w1 has the unique outside exit w1->tau;
  * semicomplete attachment: every x in O'\\{tau} returns to w1;
  * optional weak middle support m attaches by m->tau and m->w1;
  * root-complement return: two root-side predecessors enter r0;
  * every unlisted AOC row has slack at least three.
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
    arcs_between,
    containing_rows,
    core_edges,
    make_db,
    not_containing_rows,
)
from local_normal_form_audit import D63_REVERSE_HEAD, D66_RHO_ENTRY  # noqa: E402


TAU = 23
MID = 12
R0 = 14
ROOT_PREDS = frozenset((15, 16))
TAU_LOWER = frozenset((21, 22))
ROOT_COMPLEMENT = tuple(sorted(OUTSIDE_CORE - {R0}))


def row_value(rows, side):
    key = tuple(sorted(side))
    for row in rows:
        if row[1] == key:
            return row
    raise AssertionError(f"missing row {key}")


def residual_min(rows, excluded):
    excluded = {tuple(sorted(x)) for x in excluded}
    return min(row for row in rows if row[1] not in excluded)


def scenario(name, extras=(), reverse_support=False):
    edges = core_edges(make_db(extras=extras, reverse_support=reverse_support))
    edge_set = set(edges)

    w1_exits = arcs_between(edges, {W1}, OUTSIDE_CORE)
    tau_exits = arcs_between(edges, {TAU}, OUTSIDE_CORE - {TAU})
    returns_to_w1 = arcs_between(edges, OUTSIDE_CORE - {TAU}, {W1})
    missing_returns = sorted((x, W1) for x in OUTSIDE_CORE - {TAU} if (x, W1) not in edge_set)
    root_returns = arcs_between(edges, ROOT_PREDS, {R0})
    w1_to_r0 = arcs_between(edges, {W1}, {R0})

    rows_no_w1 = not_containing_rows(edges)
    rows_with_w1 = containing_rows(edges)

    assert w1_exits == ((W1, TAU),), (name, w1_exits)
    assert set(tau_exits) >= {(TAU, x) for x in TAU_LOWER}, (name, tau_exits)
    assert not missing_returns, (name, missing_returns)
    assert len(returns_to_w1) == len(OUTSIDE_CORE - {TAU}), (name, returns_to_w1)
    assert root_returns == tuple((x, R0) for x in sorted(ROOT_PREDS)), (
        name,
        root_returns,
    )
    assert not w1_to_r0, (name, w1_to_r0)

    excluded_no = [{TAU}]
    excluded_with = [{TAU}, set(ROOT_COMPLEMENT)]

    middle = None
    if reverse_support:
        middle_to_core = arcs_between(edges, {MID}, OUTSIDE_CORE - {MID})
        middle_to_w1 = arcs_between(edges, {MID}, {W1})
        assert middle_to_core == ((MID, TAU),), (name, middle_to_core)
        assert middle_to_w1 == ((MID, W1),), (name, middle_to_w1)
        assert set(TAU_LOWER).isdisjoint({MID})
        assert row_value(rows_no_w1, {MID})[0] == 2
        assert row_value(rows_with_w1, {MID})[0] == 2
        assert row_value(rows_with_w1, {MID, TAU})[0] == 2
        excluded_no.append({MID})
        excluded_with.extend([{MID}, {MID, TAU}])
        middle = {
            "m": MID,
            "m_to_core": middle_to_core,
            "m_to_w1": middle_to_w1,
        }
    else:
        assert row_value(rows_no_w1, {MID})[0] >= 3
        assert row_value(rows_with_w1, {MID})[0] >= 3

    root_row = row_value(rows_with_w1, ROOT_COMPLEMENT)
    assert root_row[0] == 2
    assert residual_min(rows_no_w1, excluded_no)[0] >= 3
    assert residual_min(rows_with_w1, excluded_with)[0] >= 3

    print(f"\n{name}")
    print(f"  extras={extras} reverse_support={reverse_support}")
    print(f"  w1_exits={w1_exits}")
    print(f"  tau_exits={tau_exits}")
    print(f"  returns_to_w1_except_tau={returns_to_w1}")
    print(f"  middle={middle}")
    print(f"  root_returns={root_returns} root_row={root_row}")
    print(f"  residual_min_no_w1={residual_min(rows_no_w1, excluded_no)}")
    print(f"  residual_min_with_w1={residual_min(rows_with_w1, excluded_with)}")


def main():
    print("Outside support clause audit")
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
