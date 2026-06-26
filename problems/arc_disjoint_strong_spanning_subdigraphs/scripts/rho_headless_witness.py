"""rho_headless_witness.py -- in-class existence of RHO-HEADLESS t==u hard
gateways (settles the D14/D16 dichotomy NEGATIVELY for the impossibility
route), plus verification that Theorem T2 (rho-tail absorption,
docs/O2B_PRESCRIBED_BRANCHING_2026_06_11.md) repairs them.

Host, cell (3,6): V1 = {p,q,y} with y =: u an I-VERTEX -- so u can have NO
arc to rho in the contraction (V1 is independent except the chord), forcing
the rho-headless case structurally.  V2 = {ka,kb,kc,k2,k3,k4} semicomplete:
cage triangle {ka,kb,kc} (digons) with ki -> y only; y -> k2,k3,k4; the
outside K dominates the cage; k2,k3,k4 pairwise digons; rho-tails
R = {k2,k3,k4} with rho-multiplicities 2,2,1.

Asserts: host simple, (1,0)-near-split, lambda=3, SAD=SAT; contraction
lambda=3, NO u->rho arc, cage C_u = {u,ka,kb,kc}; an explicit rho-headless
hard gateway pair; fixed-root L-exist GOOD at every u-external arc; and the
T2 prescription (absorb w=k3 in R, e_w=(k3,rho), e_u=(u,k4) with k4 in
R\\{w} having a spare D_O-arc) admits a prescribed-exit U* for a majority
of T* with X = X* exact (the failures being interior-cut consumers
excluded by D2).
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
    in_arborescences, subtree_through, tree_arcs, pair_realizable)


def host_arcs():
    # p=0, q=1, y=u=2 (I-vertex); ka=3, kb=4, kc=5, k2=6, k3=7, k4=8
    return [
        (0, 1),
        (3, 4), (4, 3), (3, 5), (5, 3), (4, 5), (5, 4),
        (3, 2), (4, 2), (5, 2),
        (2, 6), (2, 7), (2, 8),
        (6, 3), (6, 4), (6, 5), (7, 3), (7, 4), (7, 5), (8, 3), (8, 4), (8, 5),
        (6, 7), (7, 6), (6, 8), (8, 6), (7, 8), (8, 7),
        (6, 0), (7, 0), (8, 0),
        (6, 1), (7, 1),
        (0, 6), (0, 7), (1, 6), (1, 7), (1, 8),
    ]


def dbullet_arcs():
    # contraction: rho=0, u=1, ka=2, kb=3, kc=4, k2=5, k3=6, k4=7
    rel = {0: 0, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7}
    out = []
    for (x, y) in host_arcs():
        if (x, y) == (0, 1):
            continue
        rx, ry = rel[x], rel[y]
        if rx != ry:
            out.append((rx, ry))
    return out


def main():
    import networkx as nx
    import oracle
    from digraph import Digraph
    from generators.near_split import is_one_zero_near_split

    H = host_arcs()
    assert len(H) == len(set(H))
    ok, why = is_one_zero_near_split(
        Digraph.from_arcs(range(9), H), [0, 1, 2], [3, 4, 5, 6, 7, 8])
    assert ok, why
    assert oracle.arc_connectivity(9, H) == 3
    sad = oracle.check_construction(9, H, name="rho-headless-host")
    assert sad["sad"] == "SAT", sad
    if sad["cross_check"] is not None:
        assert sad["cross_check"]["agree"], sad

    db = dbullet_arcs()
    n, root = 8, 0
    mult = Counter(db)
    assert oracle.arc_connectivity(n, db) == 3
    assert (1, 0) not in mult, "u in I must have no rho-arc"
    R = sorted({e[0] for e in mult if e[1] == root})
    assert R == [5, 6, 7] and mult[(5, 0)] == 2 and mult[(6, 0)] == 2

    G = nx.MultiDiGraph(); G.add_nodes_from(range(n)); G.add_edges_from(db)
    Gm = G.copy(); Gm.remove_node(1)
    Cu = {1} | {x for x in range(n) if x not in (0, 1)
                and not nx.has_path(Gm, x, root)}
    assert Cu == {1, 2, 3, 4}, Cu

    struct_out = {}
    for (x, y) in mult:
        struct_out.setdefault(x, set()).add(y)
    struct_out = {x: tuple(sorted(v)) for x, v in struct_out.items()}
    arbs = [(s, tree_arcs(s)) for s in in_arborescences(n, struct_out, root)]

    # explicit rho-headless hard gateway at a=(1,5).  T must NOT use all
    # three mult-1 arcs ki->u, else no arc-disjoint U exists (the cage can
    # only exit via u): T spares (2,1), which U uses.
    T = {2: 3, 3: 1, 4: 1, 1: 5, 5: 0, 6: 0, 7: 0}
    U = {2: 1, 3: 2, 4: 2, 1: 6, 5: 6, 6: 0, 7: 5}
    Ts, Us = tree_arcs(T), tree_arcs(U)
    assert pair_realizable(Ts, Us, mult)
    X = subtree_through(T, 1, root, n)
    assert X == Cu
    ex = [(w, z) for (w, z) in Us if w in X and z not in X]
    assert len(ex) == 1, ex
    free = [e for e in mult if e[0] in X and e[1] not in X
            and mult[e] - (e in Ts) - (e in Us) >= 1]
    assert free and all(e[0] == 1 for e in free)
    print("rho-headless HARD gateway at a=(1,5): verified")

    # fixed-root L-exist at every u-external arc
    for a in [(1, 5), (1, 6), (1, 7)]:
        found = False
        for sT, Tset in arbs:
            if sT.get(1) != a[1]:
                continue
            Xa = subtree_through(sT, 1, root, n)
            if not (2 <= len(Xa) <= n - 2):
                continue
            for sU, Uset in arbs:
                if not pair_realizable(Tset, Uset, mult):
                    continue
                if a in Uset and mult[a] < 2:
                    continue
                ex2 = [(w, z) for (w, z) in Uset if w in Xa and z not in Xa]
                if len(ex2) >= 2 and any(
                        (subtree_through(sU, b[0], root, n) & Xa) < Xa
                        for b in ex2):
                    found = True
                    break
            if found:
                break
        assert found, f"L-exist FAIL at {a}"
    print("fixed-root L-exist: GOOD at all u-external arcs")

    # T2 prescription: absorb w=6 (k3, rho-mult 2), e_w=(6,0); e_u=(1,7).
    # Asserted (not just printed): exactly 135/144 admit; the D2/T1
    # biconditional holds on every T* (admits <=> interior residual >= 1
    # across every interior cut); hence every failure exhausts an interior
    # cut and every D2-packed T* (interior residual >= 1) succeeds.
    import itertools
    a, w, e_u, e_w = (1, 5), 6, (1, 7), (6, 0)
    Xst = Cu | {w}          # B_w is empty here (k2,k4 keep rho-paths)
    interior = Xst - {1, w}
    n_admit = n_tot = 0
    for sT, Tset in arbs:
        if sT.get(1) != 5 or subtree_through(sT, 1, root, n) != Xst:
            continue
        n_tot += 1
        Hh = nx.MultiDiGraph(); Hh.add_nodes_from(range(n))
        for e, m in mult.items():
            res = m - (1 if e in Tset else 0)
            if e[0] == 1:
                res = res if e == e_u else 0
            if e[0] == w:
                res = res if e == e_w else 0
            if res >= 1:
                Hh.add_edge(*e)
        admits = all(nx.has_path(Hh, x, root) for x in range(n) if x != root)
        rmin = min(
            sum(m - (1 if e in Tset else 0) for e, m in mult.items()
                if e[0] in Y and e[1] not in Y)
            for r2 in range(1, len(interior) + 1)
            for Y in map(set, itertools.combinations(interior, r2)))
        assert (rmin >= 1) == admits, ("biconditional violated", rmin, admits)
        if admits:
            n_admit += 1
    assert (n_tot, n_admit) == (144, 135), (n_tot, n_admit)
    print(f"T2 prescription admits U*: {n_admit}/{n_tot} T* (asserted); "
          f"biconditional (admits <=> interior residual >= 1) asserted on all")
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
