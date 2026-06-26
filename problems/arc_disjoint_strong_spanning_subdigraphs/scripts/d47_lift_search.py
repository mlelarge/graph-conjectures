"""Bounded D47-to-D42 lift search.

D47's one-shot B3+ defeat is a short-chain exit-count core.  This script
tries the obvious lift: keep the realized D42 sealed chain-kernel
contraction and the cage hard-pair T, but sample alternate U
arborescences to see whether an exit-count failure survives when there
are at least two U-used forced crossing tails.

The search is intentionally bounded and deterministic.  A hit would be a
true next counterexample candidate; a miss is not a proof, but it is a
useful sanity check before designing a new larger host.
"""
from __future__ import annotations

import os
import random
import sys
from collections import Counter, defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from chain_crossing_selection_check import (  # noqa: E402
    A_ARC,
    FORCED_CHAIN_TAILS,
    N,
    ROOT,
    hard_pair,
)
from chain_kernel_degeneracy_classifier import analyze_pair  # noqa: E402
from chain_kernel_witness import dbullet_arcs, is_in_arb  # noqa: E402
from check_lexist_fixedroot import pair_realizable, subtree_through, tree_arcs  # noqa: E402


TRIALS = 5000
SEED = 4701
CAGE_U = {2: 1, 3: 2, 4: 2}
EXIT_HEADS = (5, 6, 8, 10, 12)


def random_completion(n, root, allowed, fixed, rng, max_restarts=200):
    vertices = [v for v in range(n) if v != root]
    for _ in range(max_restarts):
        succ = dict(fixed)
        order = vertices[:]
        rng.shuffle(order)
        failed = False
        for start in order:
            if start in succ:
                continue
            path = []
            seen = {}
            cur = start
            while cur != root and cur not in succ:
                if cur in seen:
                    failed = True
                    break
                heads = allowed.get(cur, ())
                if not heads:
                    failed = True
                    break
                seen[cur] = len(path)
                path.append(cur)
                cur = rng.choice(heads)
            if failed:
                break
            for i, node in enumerate(path):
                succ[node] = path[i + 1] if i + 1 < len(path) else cur
        if not failed and is_in_arb(succ, n, root):
            return succ
    return None


def hard_gateway_ok(T, U, mult):
    Tset, Uset = tree_arcs(T), tree_arcs(U)
    if not is_in_arb(U, N, ROOT):
        return False
    if not pair_realizable(Tset, Uset, mult):
        return False
    X = subtree_through(T, A_ARC[0], ROOT, N)
    if X != {1, 2, 3, 4}:
        return False
    exits = sorted(e for e in Uset if e[0] in X and e[1] not in X)
    if len(exits) != 1:
        return False
    strict = [
        e for e in exits
        if (subtree_through(U, e[0], ROOT, N) & X) < X
    ]
    if strict:
        return False
    free = [
        e for e in mult
        if e[0] in X and e[1] not in X
        and mult[e] - (e in Tset) - (e in Uset) >= 1
    ]
    return bool(free) and all(e[0] == A_ARC[0] for e in free)


def main():
    rng = random.Random(SEED)
    arcs = dbullet_arcs()
    mult = Counter(arcs)
    T, _U0 = hard_pair()
    Tset = tree_arcs(T)
    assert is_in_arb(T, N, ROOT)
    assert subtree_through(T, A_ARC[0], ROOT, N) == {1, 2, 3, 4}

    allowed = defaultdict(list)
    for e, m in mult.items():
        if m - (e in Tset) >= 1:
            allowed[e[0]].append(e[1])
    allowed = {k: tuple(v) for k, v in allowed.items()}

    label_counts = Counter()
    hard_seen = 0
    multi_cross_seen = 0
    best = None
    hit = None

    for i in range(TRIALS):
        exit_head = rng.choice(EXIT_HEADS)
        fixed = dict(CAGE_U)
        fixed[1] = exit_head
        U = random_completion(N, ROOT, allowed, fixed, rng)
        if U is None or not hard_gateway_ok(T, U, mult):
            continue

        hard_seen += 1
        row = analyze_pair(
            "d47_lift_on_D42_sample",
            arcs,
            N,
            ROOT,
            A_ARC,
            T,
            U,
            FORCED_CHAIN_TAILS,
        )
        label_counts[row["label"]] += 1
        if len(row["u_used_forced_crossings"]) >= 2:
            multi_cross_seen += 1
        if best is None or (row["good"], row["forced_good"]) < (best["good"], best["forced_good"]):
            best = dict(row, U=dict(U), trial=i)
        if row["label"] == "sealed-multi-crossing-b3-fail":
            hit = dict(row, U=dict(U), trial=i)
            break

    print("D47 lift search on the D42 sealed chain kernel")
    print(f"seed={SEED} trials={TRIALS} hard_pairs_seen={hard_seen}")
    print(f"multi_forced_crossing_seen={multi_cross_seen}")
    print(f"label_counts={dict(label_counts)}")
    if best is not None:
        print(
            "best_sample="
            f"trial {best['trial']} label={best['label']} "
            f"good={best['good']} forced_good={best['forced_good']} "
            f"forced_crossings={best['u_used_forced_crossings']} "
            f"exit_counts={best['exit_counts']}"
        )
        print(f"best_U={best['U']}")
    if hit is None:
        print("sealed-multi-crossing B3+ failure found: False")
    else:
        print("sealed-multi-crossing B3+ failure found: True")
        print(f"hit_trial={hit['trial']}")
        print(f"hit_U={hit['U']}")

    assert hard_seen > 0
    assert multi_cross_seen > 0
    assert hit is None, "bounded search found a sealed multi-crossing B3+ failure"
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
