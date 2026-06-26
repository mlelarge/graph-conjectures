"""Check the D43 B3+ free-entry absorption on the chain-kernel witness.

This is a narrow, reproducible check for the current CRUX-A target:
given the explicit hard gateway pair in ``chain_kernel_witness.py``,
enumerate all vertices outside ``X union A`` that have a U-free entry
arc into X, perform the B3+ rehang, and test the exact exit-count
criterion with U unchanged.

The output is intended to ground the proposed Chain Crossing Selection
Lemma: on the D42/D43 chain kernel, at least one forced crossing tail
is B3+-absorbable in one shot.
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

from chain_kernel_witness import dbullet_arcs, is_in_arb  # noqa: E402
from check_lexist_fixedroot import (  # noqa: E402
    pair_realizable,
    subtree_through,
    tree_arcs,
)


N = 23
ROOT = 0
A_ARC = (1, 7)
FORCED_CHAIN_TAILS = {8, 10, 12}


def hard_pair():
    """The explicit D42 hard pair from chain_kernel_witness.py."""
    T = {
        2: 3, 3: 1, 4: 1, 1: 7, 5: 8, 6: 8, 7: 8, 8: 9, 9: 22,
        10: 5, 12: 5, 11: 12, 13: 0, 14: 0, 15: 0, 22: 20,
        20: 18, 18: 16, 16: 14, 17: 14, 19: 16, 21: 18,
    }
    U = {
        2: 1, 3: 2, 4: 2, 1: 10, 10: 11, 11: 18, 18: 17, 17: 15,
        15: 0, 5: 10, 6: 10, 7: 2, 8: 2, 9: 10, 12: 13,
        13: 0, 14: 0, 16: 15, 19: 17, 20: 19, 21: 19, 22: 21,
    }
    return T, U


def path_to_root(succ, start, root):
    path = []
    cur = start
    while True:
        path.append(cur)
        if cur == root:
            return path
        cur = succ[cur]


def b3_plus_candidates(
    T,
    U,
    mult,
    n=N,
    root=ROOT,
    a_arc=A_ARC,
    forced_tails=FORCED_CHAIN_TAILS,
):
    Tset, Uset = tree_arcs(T), tree_arcs(U)
    assert is_in_arb(T, n, root)
    assert is_in_arb(U, n, root)
    assert pair_realizable(Tset, Uset, mult)

    a_tail, a_head = a_arc
    X = subtree_through(T, a_tail, root, n)
    exits = sorted(e for e in Uset if e[0] in X and e[1] not in X)
    assert len(exits) == 1, exits
    unique_exit = exits[0]
    exit_head = unique_exit[1]

    ancestor_path = set(path_to_root(T, a_head, root))
    rows = []
    for w in range(n):
        if w == root or w in X or w in ancestor_path:
            continue
        S_w = subtree_through(T, w, root, n)
        X_prime = X | S_w
        entries = sorted(
            e for e in mult
            if e[0] == w
            and e[1] in X
            and mult[e] - (1 if e in Uset else 0) >= 1
        )
        if not entries:
            continue

        for d in entries:
            T_prime = dict(T)
            T_prime[w] = d[1]
            Tprime_set = tree_arcs(T_prime)
            valid_tree = is_in_arb(T_prime, n, root)
            valid_pair = valid_tree and pair_realizable(Tprime_set, Uset, mult)
            X_check = subtree_through(T_prime, a_tail, root, n) if valid_tree else set()
            exit_count = int(exit_head not in X_prime)
            exit_count += sum(1 for s in S_w if U[s] not in X_prime)
            U_exits = sorted(e for e in Uset if e[0] in X_prime and e[1] not in X_prime)
            strict = [
                e for e in U_exits
                if (subtree_through(U, e[0], root, n) & X_prime) < X_prime
            ]
            rows.append({
                "w": w,
                "entry": d,
                "forced_tail": w in forced_tails,
                "S_w": sorted(S_w),
                "X_prime": sorted(X_prime),
                "valid_tree": valid_tree,
                "valid_pair": valid_pair,
                "x_formula_ok": X_check == X_prime,
                "intermediate": len(X_prime) <= n - 2,
                "exit_count": exit_count,
                "U_exits": U_exits,
                "strict": strict,
                "b3_plus_good": (
                    valid_pair
                    and X_check == X_prime
                    and len(X_prime) <= n - 2
                    and exit_count >= 2
                    and bool(strict)
                ),
            })
    return sorted(rows, key=lambda r: (not r["b3_plus_good"], r["w"], r["entry"]))


def main():
    mult = Counter(dbullet_arcs())
    T, U = hard_pair()
    rows = b3_plus_candidates(T, U, mult)
    good = [r for r in rows if r["b3_plus_good"]]
    forced_good = [r for r in good if r["forced_tail"]]

    print(f"B3+ candidates: {len(rows)}")
    print(f"B3+ good candidates: {len(good)}")
    print(f"B3+ good forced-chain candidates: {len(forced_good)}")
    for r in good:
        tag = "forced-chain" if r["forced_tail"] else "ordinary"
        print(
            f"  w={r['w']} ({tag}), entry={r['entry']}, "
            f"S_w={r['S_w']}, exits={r['U_exits']}, "
            f"exit_count={r['exit_count']}"
        )

    assert forced_good, "no forced chain tail satisfies B3+ on the chain kernel"
    assert any(r["w"] == 12 and r["entry"][1] in {2, 3, 4} for r in forced_good)
    print("ALL ASSERTIONS PASS: chain kernel has a one-shot B3+ forced-tail repair")


if __name__ == "__main__":
    main()
