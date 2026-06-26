"""Red-team whether the D84 source clauses are forced by current gates.

D84 gives a sufficient residual ladder skeleton for ER-4 by naming source
clauses S0--S5.  This script checks the nearby falsifiable question:
among all single D42 arc reversals that preserve the currently formalized
sealed-chain structural gates, which D84 source clauses can disappear,
and does AOC actually fail when they do?
"""
from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict

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
    not_containing_rows,
)
from chain_feed_deletion_stress import structural_gates  # noqa: E402
from chain_kernel_witness import dbullet_arcs  # noqa: E402
from residual_ladder_skeleton_source_audit import (  # noqa: E402
    flatten,
    source_categories,
)


def aoc_ok(edges):
    return (
        arcs_between(edges, {W1}, OUTSIDE_CORE) == ((10, 23),)
        and not_containing_rows(edges)[0][0] >= 2
        and containing_rows(edges)[0][0] >= 2
        and low_outside_rows(edges) == [((10,), ((10, 23),))]
    )


def reversal_rows():
    base = tuple(dbullet_arcs())
    base_mult = Counter(base)
    cats = source_categories(weak_middle=False)
    required = flatten(cats)
    cat_by_arc = {
        arc: category
        for category, arcs in cats.items()
        for arc in arcs
    }

    rows = []
    for delete_arc in sorted(set(base)):
        add_arc = (delete_arc[1], delete_arc[0])
        if delete_arc[0] == delete_arc[1] or add_arc in base_mult:
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

        edges = set(core_edges(tuple(arcs)))
        missing = tuple(sorted(required - edges))
        missing_categories = tuple(sorted({cat_by_arc[e] for e in missing}))
        rows.append(
            {
                "delete_arc": delete_arc,
                "add_arc": add_arc,
                "missing": missing,
                "missing_categories": missing_categories,
                "aoc_ok": aoc_ok(tuple(edges)),
            }
        )
    return rows, cat_by_arc


def main():
    rows, cat_by_arc = reversal_rows()

    by_category = defaultdict(int)
    examples = defaultdict(list)
    for row in rows:
        for edge in row["missing"]:
            category = cat_by_arc[edge]
            by_category[category] += 1
            if len(examples[category]) < 5:
                examples[category].append(
                    (row["delete_arc"], row["add_arc"], edge, row["aoc_ok"])
                )

    missing_aoc_ok = [row for row in rows if row["missing"] and row["aoc_ok"]]
    missing_aoc_bad = [
        row for row in rows
        if row["missing"] and not row["aoc_ok"]
    ]
    intact_aoc_bad = [
        row for row in rows
        if not row["missing"] and not row["aoc_ok"]
    ]

    assert len(rows) == 27
    assert len(missing_aoc_ok) == 18
    assert len(missing_aoc_bad) == 2
    assert len(intact_aoc_bad) == 0
    assert {row["missing_categories"] for row in missing_aoc_bad} == {
        ("top_two_fan",)
    }

    print("Source-clause reversal red-team")
    print(f"structural_survivors={len(rows)}")
    print(f"missing_source_aoc_ok={len(missing_aoc_ok)}")
    print(f"missing_source_aoc_bad={len(missing_aoc_bad)}")
    print(f"source_intact_aoc_bad={len(intact_aoc_bad)}")
    print("missing category counts:")
    for category in sorted(by_category):
        print(
            f"  {category}: {by_category[category]} "
            f"examples={examples[category]}"
        )
    print("bad or source-missing rows:")
    for row in rows:
        if row["missing"] or not row["aoc_ok"]:
            decorated = tuple((edge, cat_by_arc[edge]) for edge in row["missing"])
            print(
                f"  {row['delete_arc']}->{row['add_arc']} "
                f"AOC={row['aoc_ok']} missing={decorated}"
            )
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
