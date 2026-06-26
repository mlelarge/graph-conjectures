"""Search all structural hard-gateway pairs for one-shot B3+ failures.

This is a counterexample hunter for the Missing Entry Lemma.  It enumerates
all arc-disjoint fixed-root in-arborescence pairs on small checked-in
contractions, filters to hard gateways, and classifies whether the B3+
one-shot criterion has any repair with U unchanged.
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

from b3_selection_suite import classify_no_good  # noqa: E402
from chain_crossing_selection_check import b3_plus_candidates  # noqa: E402
from check_lexist_fixedroot import (  # noqa: E402
    in_arborescences,
    pair_realizable,
    subtree_through,
    tree_arcs,
)


def hard_gateway_rows(name, arcs, n, root, max_pairs=None):
    mult = Counter(arcs)
    struct_out = {}
    for arc in mult:
        struct_out.setdefault(arc[0], set()).add(arc[1])
    struct_out = {x: tuple(sorted(ys)) for x, ys in struct_out.items()}
    arbs = [(succ, tree_arcs(succ)) for succ in in_arborescences(n, struct_out, root)]
    rows = []
    stats = defaultdict(int)
    for T, Tset in arbs:
        for a in sorted(Tset):
            u, _v = a
            if u == root:
                continue
            X = subtree_through(T, u, root, n)
            if not (2 <= len(X) <= n - 2):
                continue
            for U, Uset in arbs:
                if not pair_realizable(Tset, Uset, mult):
                    continue
                if a in Uset and mult[a] < 2:
                    continue
                exits = sorted(e for e in Uset if e[0] in X and e[1] not in X)
                if len(exits) != 1:
                    continue
                strict = [
                    e for e in exits
                    if (subtree_through(U, e[0], root, n) & X) < X
                ]
                if strict:
                    continue
                free = [
                    e for e in mult
                    if e[0] in X and e[1] not in X
                    and mult[e] - (e in Tset) - (e in Uset) >= 1
                ]
                if not free or any(e[0] != u for e in free):
                    continue
                stats["hard"] += 1
                b3_rows = b3_plus_candidates(T, U, mult, n, root, a)
                good = [r for r in b3_rows if r["b3_plus_good"]]
                if good:
                    stats["b3_good"] += 1
                else:
                    cls = classify_no_good(b3_rows)
                    stats[f"fail_{cls}"] += 1
                    rows.append({
                        "name": name,
                        "a": a,
                        "X": sorted(X),
                        "single_exit": exits[0],
                        "class": cls,
                        "candidates": len(b3_rows),
                        "T": dict(T),
                        "U": dict(U),
                    })
                    if max_pairs and len(rows) >= max_pairs:
                        return arbs, stats, rows
    return arbs, stats, rows


def cases():
    from gateway_t_eq_u_witness import dbullet_arcs as tequ_arcs
    from rho_headless_witness import dbullet_arcs as rho_arcs
    # Larger witnesses are not enumerated by default; the structural
    # arborescence space grows too quickly for this foreground search.
    yield "t_eq_u(D10)", tequ_arcs(), 7, 0
    yield "rho_headless(D17)", rho_arcs(), 8, 0


def main():
    any_fail = False
    for name, arcs, n, root in cases():
        arbs, stats, rows = hard_gateway_rows(name, arcs, n, root)
        print(f"{name}: structural in-arbs={len(arbs)} stats={dict(stats)}")
        if rows:
            any_fail = True
            for r in rows[:10]:
                print(
                    f"  FAIL class={r['class']} a={r['a']} X={r['X']} "
                    f"single_exit={r['single_exit']} candidates={r['candidates']}"
                )
        else:
            print("  no B3+ failures among hard gateway pairs")
    print(f"B3+ failure found: {any_fail}")


if __name__ == "__main__":
    main()
