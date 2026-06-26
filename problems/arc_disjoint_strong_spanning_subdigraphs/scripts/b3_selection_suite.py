"""Run the B3+ free-entry selection test on explicit hard-gateway witnesses.

This extends ``chain_crossing_selection_check.py`` from the single D42/D43
chain kernel to the checked-in hard pairs exposed by the witness scripts.
It is still a red-team harness, not a theorem prover: a positive row means
the displayed pair has a one-shot B3+ repair with U unchanged; a negative row
would identify the local obstruction class for that pair.
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

from check_lexist_fixedroot import (  # noqa: E402
    in_arborescences,
    pair_realizable,
    subtree_through,
    tree_arcs,
)
from chain_crossing_selection_check import b3_plus_candidates  # noqa: E402


def is_in_arb(succ, n, root):
    for start in range(n):
        if start == root:
            continue
        seen, cur = set(), start
        while cur != root:
            if cur in seen or cur not in succ:
                return False
            seen.add(cur)
            cur = succ[cur]
    return True


def first_hard_pair(arcs, n, root, a):
    """Find one structural hard gateway pair at arc a."""
    mult = Counter(arcs)
    struct_out = {}
    for arc in mult:
        struct_out.setdefault(arc[0], set()).add(arc[1])
    struct_out = {x: tuple(sorted(ys)) for x, ys in struct_out.items()}
    arbs = [(succ, tree_arcs(succ)) for succ in in_arborescences(n, struct_out, root)]
    u = a[0]
    for T, Tset in arbs:
        if T.get(u) != a[1]:
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
            if free and all(e[0] == u for e in free):
                return T, U
    raise AssertionError(f"no hard pair found at {a}")


def classify_no_good(rows):
    if not rows:
        return "no-free-entry"
    if all(not r["intermediate"] for r in rows):
        return "boundary"
    if all(r["exit_count"] < 2 for r in rows):
        return "exit-count"
    if all(not r["valid_tree"] for r in rows):
        return "all-ancestors-or-cycle"
    if all(not r["valid_pair"] for r in rows):
        return "label-conflict"
    if all(not r["strict"] for r in rows):
        return "no-strict-exit"
    return "mixed"


def summarize_case(name, arcs, n, root, a, T, U, forced_tails=frozenset()):
    mult = Counter(arcs)
    assert is_in_arb(T, n, root), (name, "T invalid")
    assert is_in_arb(U, n, root), (name, "U invalid")
    assert pair_realizable(tree_arcs(T), tree_arcs(U), mult), (name, "label conflict")
    X = subtree_through(T, a[0], root, n)
    exits = sorted(e for e in tree_arcs(U) if e[0] in X and e[1] not in X)
    strict = [
        e for e in exits
        if (subtree_through(U, e[0], root, n) & X) < X
    ]
    assert len(exits) == 1 and not strict, (name, exits, strict)
    rows = b3_plus_candidates(T, U, mult, n, root, a, set(forced_tails))
    good = [r for r in rows if r["b3_plus_good"]]
    forced_good = [r for r in good if r["forced_tail"]]
    best = good[0] if good else None
    return {
        "name": name,
        "n": n,
        "a": a,
        "X_size": len(X),
        "single_exit": exits[0],
        "candidates": len(rows),
        "good": len(good),
        "forced_good": len(forced_good),
        "best": best,
        "class": "good" if good else classify_no_good(rows),
    }


def explicit_cases():
    from chain_kernel_witness import dbullet_arcs as chain_arcs
    from chain_crossing_selection_check import FORCED_CHAIN_TAILS, hard_pair
    from core_embedding_witness import dbullet_arcs as core_arcs
    from dominated_witness import dbullet_arcs as dominated_arcs
    from gateway_t_eq_u_witness import dbullet_arcs as tequ_arcs
    from relay_free_witness import dbullet_arcs as relay_arcs
    from rho_headless_witness import dbullet_arcs as rho_arcs
    from saturation_kernel_witness import dbullet_arcs as sat_arcs
    from v_target_internal_reachability_counterexample import construction

    # D10 t==u witness: find one representative hard pair exhaustively.
    arcs = tequ_arcs()
    T, U = first_hard_pair(arcs, 7, 0, (1, 5))
    yield ("t_eq_u(D10)", arcs, 7, 0, (1, 5), T, U, frozenset())

    # D17 rho-headless witness.
    yield (
        "rho_headless(D17)", rho_arcs(), 8, 0, (1, 5),
        {2: 3, 3: 1, 4: 1, 1: 5, 5: 0, 6: 0, 7: 0},
        {2: 1, 3: 2, 4: 2, 1: 6, 5: 6, 6: 0, 7: 5},
        frozenset(),
    )

    yield (
        "dominated(D18)", dominated_arcs(), 11, 0, (1, 5),
        {2: 3, 3: 1, 4: 1, 1: 5, 5: 8, 6: 7, 7: 5, 8: 0, 9: 0, 10: 0},
        {2: 1, 3: 2, 4: 2, 1: 6, 6: 5, 5: 9, 7: 2, 9: 8, 8: 0, 10: 0},
        frozenset(),
    )

    relay_T = {
        2: 3, 3: 1, 4: 1, 1: 5, 5: 8, 6: 7, 7: 5,
        8: 11, 9: 11, 10: 11, 11: 0, 12: 0, 13: 0,
    }
    relay_U = {
        2: 1, 3: 2, 4: 2, 1: 6, 6: 5, 5: 9, 7: 2, 8: 6,
        9: 12, 10: 13, 11: 0, 12: 11, 13: 0,
    }
    yield ("relay_free(D19)", relay_arcs(), 14, 0, (1, 5), relay_T, relay_U, frozenset())

    yield (
        "core_embedding(D28)", core_arcs(), 11, 0, (1, 8),
        {2: 3, 3: 1, 4: 1, 1: 8, 5: 7, 7: 6, 6: 9, 9: 0, 8: 0, 10: 0},
        {2: 1, 3: 2, 4: 2, 1: 5, 5: 8, 8: 0, 6: 5, 7: 2, 9: 0, 10: 0},
        frozenset(),
    )

    # D30 blocker counterexample extends the relay-free hard pair.
    _host, blocker_arcs, blockers = construction()
    blocker_T = dict(relay_T)
    blocker_U = dict(relay_U)
    for i, (_x, layer, _rho_tail) in enumerate(blockers):
        x = 14 + i
        blocker_T[x] = 5
        blocker_U[x] = layer - 1
    yield (
        "blocker_cex(D30)", blocker_arcs, 23, 0, (1, 5),
        blocker_T, blocker_U, frozenset(),
    )

    yield (
        "saturation_kernel(D38)", sat_arcs(), 14, 0, (1, 5),
        {2: 3, 3: 1, 4: 1, 1: 5, 5: 8, 6: 7, 7: 5, 8: 11,
         9: 11, 10: 11, 11: 0, 12: 0, 13: 0},
        {2: 1, 3: 2, 4: 2, 1: 6, 6: 9, 9: 12, 12: 11, 11: 0,
         5: 2, 7: 10, 10: 13, 13: 0, 8: 6},
        frozenset(),
    )

    chain_T, chain_U = hard_pair()
    yield (
        "chain_kernel(D42)", chain_arcs(), 23, 0, (1, 7),
        chain_T, chain_U, FORCED_CHAIN_TAILS,
    )


def main():
    rows = []
    for args in explicit_cases():
        rows.append(summarize_case(*args))

    failures = [r for r in rows if r["class"] != "good"]
    for r in rows:
        if r["best"] is None:
            print(
                f"{r['name']}: NO one-shot B3+ repair; "
                f"class={r['class']}; candidates={r['candidates']}"
            )
            continue
        b = r["best"]
        tag = " forced-tail" if b["forced_tail"] else ""
        print(
            f"{r['name']}: B3+ GOOD{tag}; candidates={r['candidates']} "
            f"good={r['good']} forced_good={r['forced_good']} "
            f"w={b['w']} entry={b['entry']} S_w={b['S_w']} "
            f"exits={b['U_exits']}"
        )

    print(f"\nB3+ explicit hard-pair suite: {len(rows) - len(failures)}/{len(rows)} good")
    if failures:
        print("Failures:")
        for r in failures:
            print(f"  {r['name']}: {r['class']}")
    assert not failures, "some explicit hard pairs lack one-shot B3+ repairs"
    print("ALL ASSERTIONS PASS: every explicit hard pair has a one-shot B3+ repair")


if __name__ == "__main__":
    main()
