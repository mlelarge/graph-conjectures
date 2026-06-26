"""dominated_witness.py -- the FULLY-DOMINATED rho-headless configuration
(D17 residue) EXISTS in-class -- and is NOT an obstruction: an explicit
relay repair (Theorem T3, docs/O2B_PRESCRIBED_BRANCHING_2026_06_11.md) is
verified on it.

Host, cell (3,9): V1 = {p,q,y}, y =: u an I-vertex (rho-headless forced).
V2 = {ka,kb,kc, h1,h2,h3, r1,r2,r3} semicomplete: cage triangle {ka,kb,kc}
(digons, ki -> y only); u -> h1(=a), h2, h3; rho-tails R = {r1,r2,r3}
(rho-multiplicities 2,1,2); FULL DOMINATION: every r in R dominates every
AV_u head (r -> h2, r -> h3; no reverses), and no head is a rho-tail --
so BOTH T2 hypotheses fail for EVERY admissible (w, z0).  The relay:
v = h1 carries h2->h1, h3->h1 and h1->r1, h1->r2, h1->r3.

Asserts: in-class (simple, near-split, lambda=3 host and contraction,
host SAD=SAT); cage = {u,ka,kb,kc}; explicit rho-headless hard gateway;
the full-domination pattern (T2 inapplicable everywhere); and the explicit
T3 repair pair (T*,U*): absorb w=r2, prescriptions e_w=(r2,rho),
e_u=(u,h2), relay u -> h2 -> h1 -> r2 -> rho, with (h2,h1) spared by
T_out(h2)=(h2,h3) and (h1,r2) auto-safe (head in X*, not a D_O-arc):
a GOOD pair at a (two exits, strict exit verified directly).
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


def host_arcs():
    # p=0 q=1 y=u=2 | ka=3 kb=4 kc=5 | h1=6 h2=7 h3=8 | r1=9 r2=10 r3=11
    arcs = [
        (0, 1),                                            # chord p->q
        (3, 4), (4, 3), (3, 5), (5, 3), (4, 5), (5, 4),    # cage digons
        (3, 2), (4, 2), (5, 2),                            # ki -> u
        (2, 6), (2, 7), (2, 8),                            # u -> h1(a), h2, h3
        (7, 6), (8, 6), (7, 8),                            # h2->h1, h3->h1, h2->h3
        (6, 9), (6, 10), (6, 11),                          # h1 -> r1,r2,r3 (relay)
        (9, 7), (9, 8), (10, 7), (10, 8), (11, 7), (11, 8),  # FULL DOMINATION
        (9, 10), (10, 9), (9, 11), (11, 9), (10, 11), (11, 10),  # r-digons
        (9, 0), (9, 1), (10, 0), (11, 0), (11, 1),         # rho-tails (mult 2,1,2)
        (0, 9), (0, 10), (1, 10), (1, 11), (1, 6),         # rho-side out
    ]
    arcs += [(x, c) for x in (6, 7, 8, 9, 10, 11) for c in (3, 4, 5)]
    return arcs


def dbullet_arcs():
    # rho=0 u=1 ka=2 kb=3 kc=4 h1=5 h2=6 h3=7 r1=8 r2=9 r3=10
    rel = {0: 0, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4,
           6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 11: 10}
    out = []
    for (x, y) in host_arcs():
        if (x, y) == (0, 1):
            continue
        rx, ry = rel[x], rel[y]
        if rx != ry:
            out.append((rx, ry))
    return out


def is_in_arb(succ, n, root):
    for v0 in range(n):
        if v0 == root:
            continue
        seen, cur = set(), v0
        while cur != root:
            if cur in seen or cur not in succ:
                return False
            seen.add(cur)
            cur = succ[cur]
    return True


def main():
    import networkx as nx
    import oracle
    from digraph import Digraph
    from generators.near_split import is_one_zero_near_split

    H = host_arcs()
    assert len(H) == len(set(H))
    ok, why = is_one_zero_near_split(
        Digraph.from_arcs(range(12), H), [0, 1, 2], list(range(3, 12)))
    assert ok, why
    assert oracle.arc_connectivity(12, H) == 3
    sad = oracle.check_construction(12, H, name="dominated-host")
    assert sad["sad"] == "SAT", sad
    if sad["cross_check"] is not None:
        assert sad["cross_check"]["agree"], sad

    db = dbullet_arcs()
    n, root, u = 11, 0, 1
    mult = Counter(db)
    assert oracle.arc_connectivity(n, db) == 3
    assert (u, root) not in mult                       # rho-headless (u in I)

    G = nx.MultiDiGraph(); G.add_nodes_from(range(n)); G.add_edges_from(db)
    Gm = G.copy(); Gm.remove_node(u)
    Cu = {u} | {x for x in range(n) if x not in (root, u)
                and not nx.has_path(Gm, x, root)}
    assert Cu == {1, 2, 3, 4}, Cu

    R = sorted({e[0] for e in mult if e[1] == root})
    heads = [5, 6]  # AV_u heads h2=5? no: AV_u heads are 6(h2),7(h3); a=(1,5)
    a, v = (1, 5), 5
    av_heads = [z for z in range(n) if (1, z) in mult and z != v]
    assert sorted(av_heads) == [6, 7]
    assert R == [8, 9, 10]
    # FULL DOMINATION + heads not rho-tails => T2 fails for every (w, z0)
    for z0 in av_heads:
        assert z0 not in R
        for r in R:
            assert (r, z0) in mult and (z0, r) not in mult
    print("full domination verified: T2 hypotheses (i),(ii) fail everywhere")

    # explicit rho-headless hard gateway at a=(1,5)
    T = {2: 3, 3: 1, 4: 1, 1: 5, 5: 8, 6: 7, 7: 5, 8: 0, 9: 0, 10: 0}
    U = {2: 1, 3: 2, 4: 2, 1: 6, 6: 5, 5: 9, 7: 2, 9: 8, 8: 0, 10: 0}
    Ts, Us = tree_arcs(T), tree_arcs(U)
    assert is_in_arb(T, n, root) and is_in_arb(U, n, root)
    assert all(mult[e] >= 2 for e in Ts & Us)          # label-disjoint
    X = subtree_through(T, u, root, n)
    assert X == Cu
    ex = [(w, z) for (w, z) in Us if w in X and z not in X]
    assert ex == [(1, 6)], ex                          # single U-exit: failing
    free = [e for e in mult if e[0] in X and e[1] not in X
            and mult[e] - (e in Ts) - (e in Us) >= 1]
    assert free and all(e[0] == u for e in free)       # gateway
    print("rho-headless hard gateway at a=(1,5): verified")

    # T3 relay repair: absorb w=r2(=9), e_w=(9,rho), e_u=(1,6),
    # relay 1 -> 6 -> 5 -> 9 -> 0 with (6,5) spared by T_out(6)=(6,7)
    Tst = {2: 3, 3: 1, 4: 1, 1: 5, 9: 2, 5: 8, 6: 7, 7: 5, 8: 0, 10: 0}
    Ust = {2: 1, 3: 2, 4: 2, 1: 6, 6: 5, 5: 9, 9: 0, 7: 2, 8: 0, 10: 0}
    Tss, Uss = tree_arcs(Tst), tree_arcs(Ust)
    assert is_in_arb(Tst, n, root) and is_in_arb(Ust, n, root)
    assert all(mult[e] >= 2 for e in Tss & Uss)
    Xs = subtree_through(Tst, u, root, n)
    assert Xs == Cu | {9}, sorted(Xs)                  # X* = C_u u {r2}, exact
    ex2 = [(w, z) for (w, z) in Uss if w in Xs and z not in Xs]
    assert sorted(ex2) == [(1, 6), (9, 0)], ex2        # TWO exits
    strict = [b for b in ex2
              if (subtree_through(Ust, b[0], root, n) & Xs) < Xs]
    assert strict, "no strict exit"
    print(f"T3 relay repair: GOOD pair at a=(1,5), X*={sorted(Xs)}, "
          f"exits={sorted(ex2)}, strict={strict}")
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
