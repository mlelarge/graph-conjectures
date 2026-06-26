"""t4_relay_repair_check.py -- Theorem T4 (multi-step relay) repairs the
D19 relay-free witness: explicit good pair verified, so that witness is NOT
a fixed-root L-exist counterexample at its gateway arc.

T4 (docs/O2B_PRESCRIBED_BRANCHING_2026_06_11.md): strictly rho-headless
gateway; admissible w in R\\{v}; escaped AV_u-head h; a path
P: h = o_0 -> o_1 -> ... -> o_m -> w with all o_i in O, such that every
O-vertex reaches rho in D_O - A_O(P) (the path's D_O-arcs deleted; the
final arc (o_m, w) has head in X*_w and is never a D_O-arc).  Then
T_out := any in-arb of D_O - A_O(P), T* as in D2, prescriptions
e_u=(u,h), e_w=(w,rho) give a good pair.

On the D19 witness (rho=0, u=1, cage 2..4, v=5, heads 6,7, L=8..10,
R=11..13): w=11, P: 6 -> 5 -> 8 -> 11 (the layered route head -> v -> L
-> R), A_O(P) = {(6,5),(5,8)}.  This script verifies the T4 hypothesis
(D_O - A_O(P) reachability), builds the explicit (T*,U*), and asserts the
pair is valid, label-disjoint, X-exact, two-exit, and strict-exit GOOD.
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

from check_lexist_fixedroot import subtree_through, tree_arcs  # noqa: E402
from relay_free_witness import dbullet_arcs, is_in_arb  # noqa: E402


def main():
    import networkx as nx

    arcs = dbullet_arcs()
    n, root, u, v, w = 14, 0, 1, 5, 11
    a = (u, v)
    mult = Counter(arcs)
    cage = {1, 2, 3, 4}
    Xst = cage | {w}                      # B_w = {} (asserted in D19 script)
    O = set(range(n)) - Xst - {root}

    # T4 hypothesis: path P: 6 -> 5 -> 8 -> 11; D_O - A_O(P) reachability
    P_arcs_O = [(6, 5), (5, 8)]           # (8,11) heads into X*: not a D_O arc
    assert all(e in mult for e in P_arcs_O + [(8, 11)])
    DO = nx.MultiDiGraph()
    DO.add_nodes_from(O | {root})
    for (x, y), m in mult.items():
        if x in O and (y in O or y == root) and (x, y) not in P_arcs_O:
            for _ in range(m):
                DO.add_edge(x, y)
    assert all(nx.has_path(DO, z, root) for z in O), "T4 hypothesis fails"
    print("T4 hypothesis verified: every O-vertex reaches rho in D_O - A_O(P)")

    # explicit T* (cage F1 sparing (2,1); hook 11->2; a; T_out avoiding A_O(P))
    Tst = {2: 3, 3: 1, 4: 1, 1: 5, 11: 2,
           5: 9, 6: 7, 7: 5, 8: 9, 9: 12, 10: 13, 12: 0, 13: 0}
    # explicit U*: relay u ->(e_u) 6 -> 5 -> 8 -> 11 ->(e_w) rho
    Ust = {2: 1, 3: 2, 4: 2, 1: 6, 6: 5, 5: 8, 8: 11, 11: 0,
           7: 2, 9: 11, 10: 11, 12: 11, 13: 11}
    Ts, Us = tree_arcs(Tst), tree_arcs(Ust)
    assert is_in_arb(Tst, n, root) and is_in_arb(Ust, n, root)
    assert all(mult[e] >= 2 for e in Ts & Us), "label clash"
    assert all((x, y) not in Ts for (x, y) in P_arcs_O + [(8, 11)])

    Xv = subtree_through(Tst, u, root, n)
    assert Xv == Xst, sorted(Xv)          # X_a^{T*} = X*_w exactly
    ex = sorted(e for e in Us if e[0] in Xst and e[1] not in Xst)
    assert ex == [(1, 6), (11, 0)], ex    # two exits: e_u and e_w
    strict = [e for e in ex
              if (subtree_through(Ust, e[0], root, n) & Xst) < Xst]
    assert strict, "no strict exit"
    print(f"T4 repair on the D19 witness: GOOD pair at a={a}, "
          f"X*={sorted(Xst)}, exits={ex}, strict={strict}")
    print("the relay-free witness is NOT an L-exist counterexample at a")
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
