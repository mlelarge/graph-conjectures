"""Red-team the residual row-capacity target after D85.

D85 showed that exact D84 source containment is too strong if the goal is
only AOC.  The stronger ER-4/RRSP target asks for every unlisted eta/zeta
row to have value at least three.  This script checks whether that target
survives the same gate-preserving single-reversal neighbourhood.
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
    arcs_between,
    containing_rows,
    core_edges,
    not_containing_rows,
)
from chain_kernel_witness import dbullet_arcs  # noqa: E402
from residual_ladder_separator_audit import (  # noqa: E402
    M,
    TAU,
    assert_er4,
    eta_rows,
    ladder_skeleton,
    zeta_rows,
)
from residual_ladder_skeleton_source_audit import source_categories  # noqa: E402
from source_clause_reversal_redteam import reversal_rows  # noqa: E402


ROBUST_MIDDLE = (12, 19)


def edges_for_reversal(row):
    arcs = list(dbullet_arcs())
    arcs.remove(row["delete_arc"])
    arcs.append(row["add_arc"])
    return tuple(core_edges(tuple(arcs)))


def weak_middle(edges):
    return ROBUST_MIDDLE not in set(edges)


def residual_capacity_failure(edges):
    try:
        assert_er4(
            not_containing_rows(edges),
            containing_rows(edges),
            weak_middle(edges),
        )
    except AssertionError as exc:
        return exc.args[0] if exc.args else "failed"
    return None


def sle_ok(edges):
    return len(arcs_between(edges, {TAU}, OUTSIDE_CORE - {TAU})) >= 2


def active_attachment_ok(edges):
    if arcs_between(edges, {W1}, OUTSIDE_CORE) != ((10, 23),):
        return False
    returns = arcs_between(edges, OUTSIDE_CORE - {TAU}, {W1})
    return len(returns) == len(OUTSIDE_CORE - {TAU})


def skeleton_critical_deletions(weak):
    cats = source_categories(weak_middle=weak)
    cat_by_arc = {
        arc: category
        for category, arcs in cats.items()
        for arc in arcs
    }
    out = []
    skeleton = set(ladder_skeleton(weak_middle=weak))
    for edge in sorted(skeleton):
        reduced = skeleton - {edge}
        try:
            assert_er4(eta_rows(reduced), zeta_rows(reduced), weak)
        except AssertionError as exc:
            out.append((edge, cat_by_arc.get(edge), exc.args[0]))
    return out


def main():
    rows, _cat_by_arc = reversal_rows()
    residual_bad = []
    sle_bad = []
    active_bad = []
    for row in rows:
        edges = edges_for_reversal(row)
        failure = residual_capacity_failure(edges)
        if failure is not None:
            residual_bad.append((row, failure))
        if not sle_ok(edges):
            sle_bad.append(row)
        if not active_attachment_ok(edges):
            active_bad.append(row)

    residual_bad_aoc_ok = [item for item in residual_bad if item[0]["aoc_ok"]]
    residual_bad_aoc_bad = [
        item for item in residual_bad
        if not item[0]["aoc_ok"]
    ]

    category_counts = defaultdict(int)
    for row, _failure in residual_bad:
        category_counts[row["missing_categories"]] += 1

    robust_critical = skeleton_critical_deletions(weak=False)
    weak_critical = skeleton_critical_deletions(weak=True)

    assert len(rows) == 27
    assert len(residual_bad) == 6
    assert len(residual_bad_aoc_ok) == 4
    assert len(residual_bad_aoc_bad) == 2
    assert len(sle_bad) == 2
    assert len(active_bad) == 0
    assert {
        item[0]["missing_categories"] for item in residual_bad_aoc_ok
    } == {("r2_boundary_L_to_P",)}
    assert {
        item[0]["missing_categories"] for item in residual_bad_aoc_bad
    } == {("top_two_fan",)}
    assert len(robust_critical) == 15
    assert len(weak_critical) == 14

    print("Residual row-capacity red-team")
    print(f"structural_survivors={len(rows)}")
    print(f"residual_capacity_bad={len(residual_bad)}")
    print(f"residual_capacity_bad_aoc_ok={len(residual_bad_aoc_ok)}")
    print(f"residual_capacity_bad_aoc_bad={len(residual_bad_aoc_bad)}")
    print(f"sle_bad={len(sle_bad)}")
    print(f"active_attachment_bad={len(active_bad)}")
    print("residual bad category counts:")
    for categories in sorted(category_counts):
        print(f"  {categories}: {category_counts[categories]}")
    print("residual bad rows:")
    for row, failure in residual_bad:
        print(
            f"  {row['delete_arc']}->{row['add_arc']} "
            f"AOC={row['aoc_ok']} categories={row['missing_categories']} "
            f"failure={failure}"
        )
    print("critical single skeleton deletions:")
    print(f"  robust={len(robust_critical)}")
    for edge, category, failure in robust_critical:
        print(f"    {edge} {category} failure={failure}")
    print(f"  weak={len(weak_critical)}")
    for edge, category, failure in weak_critical:
        print(f"    {edge} {category} failure={failure}")
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
