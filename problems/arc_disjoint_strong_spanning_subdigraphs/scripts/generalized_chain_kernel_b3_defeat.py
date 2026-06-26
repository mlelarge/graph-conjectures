"""D47 generalized chain-kernel core defeating one-shot B3+.

This is a negative witness for the over-broad reading of D45:
"every hard gateway pair in the in-class inventory has a one-shot B3+
repair with U unchanged."  The underlying host is the in-class
rho-headless D17 witness, but the hard pair is not the representative
used by ``b3_selection_suite.py``.

The obstruction is the short-chain / exit-head-in-subtree pattern.  The
unique U-exit from the cage is u -> 6.  Rehanging the exit head 6 into
the cage consumes the old u-exit and leaves only 6 -> rho; rehanging the
other available vertex 7 leaves the old u-exit and gives no second
U-exit.  Thus every valid free-entry B3+ row has exit_count == 1.
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

from b3_selection_suite import classify_no_good  # noqa: E402
from chain_crossing_selection_check import b3_plus_candidates  # noqa: E402
from check_lexist_fixedroot import (  # noqa: E402
    pair_realizable,
    subtree_through,
    tree_arcs,
)
from rho_headless_witness import dbullet_arcs, host_arcs  # noqa: E402


N = 8
ROOT = 0
A_ARC = (1, 5)
CAGE = {1, 2, 3, 4}


def is_in_arb(succ, n=N, root=ROOT):
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


def hard_pair():
    """A rho-headless hard pair outside the D45 selected-pair suite."""
    T = {1: 5, 2: 1, 3: 1, 4: 2, 5: 0, 6: 0, 7: 0}
    U = {1: 6, 2: 3, 3: 4, 4: 1, 5: 0, 6: 0, 7: 2}
    return T, U


def verify_in_class():
    import networkx as nx
    import oracle
    from digraph import Digraph
    from generators.near_split import is_one_zero_near_split

    host = host_arcs()
    assert len(host) == len(set(host)), "host must be simple"
    ok, why = is_one_zero_near_split(
        Digraph.from_arcs(range(9), host), [0, 1, 2], list(range(3, 9))
    )
    assert ok, why
    lam_host = oracle.arc_connectivity(9, host)
    assert lam_host == 3, lam_host
    sad = oracle.check_construction(9, host, name="d47-b3-defeat-host")
    assert sad["sad"] == "SAT", sad
    if sad["cross_check"] is not None:
        assert sad["cross_check"]["agree"], sad

    arcs = dbullet_arcs()
    lam_contract = oracle.arc_connectivity(N, arcs)
    assert lam_contract == 3, lam_contract
    assert (1, 0) not in Counter(arcs), "rho-headless u must have no rho arc"

    g = nx.MultiDiGraph()
    g.add_nodes_from(range(N))
    g.add_edges_from(arcs)
    g_without_u = g.copy()
    g_without_u.remove_node(1)
    cage = {
        1,
        *(
            x for x in range(N)
            if x not in (ROOT, 1) and not nx.has_path(g_without_u, x, ROOT)
        ),
    }
    assert cage == CAGE, sorted(cage)
    return sad


def verify_hard_pair():
    mult = Counter(dbullet_arcs())
    T, U = hard_pair()
    Tset, Uset = tree_arcs(T), tree_arcs(U)
    assert is_in_arb(T), "T invalid"
    assert is_in_arb(U), "U invalid"
    assert pair_realizable(Tset, Uset, mult), "T/U label conflict"

    X = subtree_through(T, A_ARC[0], ROOT, N)
    assert X == CAGE, sorted(X)
    exits = sorted(e for e in Uset if e[0] in X and e[1] not in X)
    assert exits == [(1, 6)], exits
    strict = [
        e for e in exits
        if (subtree_through(U, e[0], ROOT, N) & X) < X
    ]
    assert strict == [], strict

    free = sorted(
        e for e in mult
        if e[0] in X and e[1] not in X
        and mult[e] - (e in Tset) - (e in Uset) >= 1
    )
    assert free == [(1, 7)], free

    rows = b3_plus_candidates(T, U, mult, N, ROOT, A_ARC, forced_tails=set())
    good = [r for r in rows if r["b3_plus_good"]]
    assert len(rows) == 5, len(rows)
    assert not good, good
    assert classify_no_good(rows) == "exit-count"
    assert all(r["valid_tree"] and r["valid_pair"] for r in rows)
    assert all(r["x_formula_ok"] and r["intermediate"] for r in rows)
    assert all(r["exit_count"] == 1 for r in rows)
    assert all(not r["strict"] for r in rows)
    assert sorted((r["w"], tuple(r["entry"]), tuple(r["S_w"])) for r in rows) == [
        (6, (6, 2), (6,)),
        (6, (6, 3), (6,)),
        (6, (6, 4), (6,)),
        (7, (7, 3), (7,)),
        (7, (7, 4), (7,)),
    ]
    return rows


def main():
    sad = verify_in_class()
    T, U = hard_pair()
    rows = verify_hard_pair()

    print("D47 generalized B3+ defeat")
    print("host: simple (1,0)-near-split, lambda=3, SAD=SAT")
    if sad["cross_check"] is not None:
        print("host SAD cross-check: agree")
    print("D-bullet: n=8, lambda=3, strictly rho-headless at u=1")
    print(f"hard pair: a={A_ARC}, X={sorted(CAGE)}, unique U-exit={(1, 6)}")
    print(f"T={T}")
    print(f"U={U}")
    print(f"B3+ candidates={len(rows)}, good=0, class=exit-count")
    for r in rows:
        print(
            f"  w={r['w']} entry={r['entry']} S_w={r['S_w']} "
            f"U_exits={r['U_exits']} exit_count={r['exit_count']}"
        )
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
