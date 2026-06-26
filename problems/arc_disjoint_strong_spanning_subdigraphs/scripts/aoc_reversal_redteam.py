"""Single-reversal red-team for the attached outside-cut certificate.

D75 proves AOC => FSQ, and verifies AOC on D42 plus the D74 support
reversal.  This script asks a sharper question: do the currently checked
sealed-chain gates alone force AOC?

Answer: no.  Among single semicomplete-preserving reversals of D42 that keep
the structural gates, exactly two break AOC:

    22->20 reversed to 20->22,
    22->21 reversed to 21->22.

Both keep lambda 3 and admit a repaired hard gateway pair.  They create the
new outside low cut {23} in host labels.  This isolates the missing primitive:
the top support vertex reached by w1 needs its two downward support exits, or
more generally AOC must be proved using the DT support clause rather than only
the generic sealed-chain gates.
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
    not_containing_rows,
)
from chain_crossing_selection_check import hard_pair  # noqa: E402
from chain_feed_deletion_stress import structural_gates  # noqa: E402
from chain_kernel_witness import dbullet_arcs, is_in_arb  # noqa: E402
from check_lexist_fixedroot import (  # noqa: E402
    pair_realizable,
    subtree_through,
    tree_arcs,
)


N_DB = 23
ROOT = 0
U = 1


def reversed_once(base, delete_arc, add_arc):
    arcs = list(base)
    arcs.remove(delete_arc)
    arcs.append(add_arc)
    return tuple(arcs)


def aoc_profile(arcs):
    edges = core_edges(arcs)
    w1_exits = arcs_between(edges, {W1}, OUTSIDE_CORE)
    rows_no = not_containing_rows(edges)
    rows_with = containing_rows(edges)
    low_outside = low_outside_rows(edges)
    ok = (
        w1_exits == ((10, 23),)
        and rows_no[0][0] >= 2
        and rows_with[0][0] >= 2
        and low_outside == [((10,), ((10, 23),))]
    )
    return {
        "ok": ok,
        "w1_exits": w1_exits,
        "min_no_w1": rows_no[0],
        "min_with_w1": rows_with[0],
        "low_outside": low_outside,
    }


def hard_gateway_candidates(arcs):
    mult = Counter(arcs)
    base_T, base_U = hard_pair()
    outs_22 = sorted(v for x, v in mult if x == 22)
    candidates = []
    for t22 in outs_22:
        for u22 in outs_22:
            T = dict(base_T)
            U_tree = dict(base_U)
            T[22] = t22
            U_tree[22] = u22
            Tset = tree_arcs(T)
            Uset = tree_arcs(U_tree)
            usage = Counter(Tset) + Counter(Uset)
            if not all(usage[e] <= mult[e] for e in usage):
                continue
            if not (is_in_arb(T, N_DB, ROOT) and is_in_arb(U_tree, N_DB, ROOT)):
                continue
            if not pair_realizable(Tset, Uset, mult):
                continue
            X = subtree_through(T, U, ROOT, N_DB)
            exits = tuple(sorted(e for e in Uset if e[0] in X and e[1] not in X))
            strict = tuple(
                e for e in exits
                if (subtree_through(U_tree, e[0], ROOT, N_DB) & X) < X
            )
            free = tuple(
                sorted(
                    e for e in mult
                    if e[0] in X
                    and e[1] not in X
                    and mult[e] - (e in Tset) - (e in Uset) >= 1
                )
            )
            if X == {1, 2, 3, 4} and exits == ((1, 10),) and not strict:
                if free and all(e[0] == U for e in free):
                    candidates.append({"T22": t22, "U22": u22, "free": free})
    return candidates


def main():
    base = tuple(dbullet_arcs())
    mult = Counter(base)
    structural_survivors = []
    aoc_failures = []
    skipped_exceptions = 0

    for delete_arc in sorted(set(base)):
        x, y = delete_arc
        add_arc = (y, x)
        if x == y or add_arc in mult:
            continue
        arcs = reversed_once(base, delete_arc, add_arc)
        try:
            gates = structural_gates(arcs)
        except Exception:
            skipped_exceptions += 1
            continue
        if not gates["structural_ok"]:
            continue
        structural_survivors.append((delete_arc, add_arc))
        profile = aoc_profile(arcs)
        if not profile["ok"]:
            candidates = hard_gateway_candidates(arcs)
            aoc_failures.append((delete_arc, add_arc, profile, candidates))

    expected = {
        ((22, 20), (20, 22)),
        ((22, 21), (21, 22)),
    }
    found = {(delete_arc, add_arc) for delete_arc, add_arc, _p, _c in aoc_failures}
    assert len(structural_survivors) == 27, len(structural_survivors)
    assert found == expected, found
    assert all(candidates for _d, _a, _p, candidates in aoc_failures)

    print("AOC single-reversal red-team")
    print(f"skipped_exceptions={skipped_exceptions}")
    print(f"structural_single_reversal_survivors={len(structural_survivors)}")
    print(f"aoc_failures={len(aoc_failures)}")
    for delete_arc, add_arc, profile, candidates in aoc_failures:
        print(f"  reversal={delete_arc}->{add_arc}")
        print(f"    min_no_w1={profile['min_no_w1']}")
        print(f"    min_with_w1={profile['min_with_w1']}")
        print(f"    low_outside={profile['low_outside']}")
        print(f"    repaired_hard_gateway={candidates[0]}")
    print("ALL ASSERTIONS PASS: AOC needs an explicit top-support primitive")


if __name__ == "__main__":
    main()
