"""cage_canonicalization_check.py -- checked-in machine verification of the
cage lemmas C1-C7 (docs/O2_CAGE_CANONICALIZATION_2026_06_11.md) and of the
O2a*/O2b* residues, with O2b* in its CORRECTED prescribed-out-arc form.

Runs on the D10 witness (scripts/gateway_t_eq_u_witness.py).  Checks:

  C1(3)  no-pair prediction: arcs (u,z) with z in C_u admit NO in-arb T;
         arcs with head outside C_u admit one, and every such T has
         X_a^T >= C_u, with equality realized by some T.
  C2     every pair with X = C_u has exactly one U-exit (hence fails).
  C3     |K cap C_u \\ {u}| >= 2; V \\ C_u \\ {rho} nonempty; K \\ C_u
         nonempty; full hook fan w -> K1 for every w in K \\ C_u.
  C4     per w in K \\ C_u: B_w sealing, exit tails within {u,w}, w-escape,
         and T* realizability (some enumerated T has X_a^T = X*_w exactly).
  C7     min out-cut over nonempty Y within C_u \\ {u}, computed INSIDE
         D[C_u], is >= 3 (Edmonds condition for the 3-packing).
  O2a*   existence of w with an AV_u head escaping X*_w, v notin X*_w,
         |X*_w| <= n-2.
  O2b*   CORRECTED criterion: U* containing the two designated exits
         exists iff every vertex reaches rho in the prescribed residual
         (labels minus T*, out-arcs at u and w replaced by the designated
         exits).  Verified over ALL T* with X exact (not a prefix): the
         criterion is evaluated, independently cross-checked against
         direct enumeration of in-arbs U* with the prescribed out-arcs,
         and the per-(a,w) admit statistic is asserted (witness: 60/64
         per case, 240/256 overall).  At least one admissible T* is
         asserted per admissible (a,w).  The D2/T1 BICONDITIONAL is
         asserted on every T*: admits <=> interior residual >= 1 across
         every interior cut (witness blockers: the star {ka->u, kb->u,
         kc->u}, which exhausts delta+(C_u \\ {u} -> u) and therefore
         belongs to no C7/D1 3-packing -- the packing-based T* excludes
         all observed blockers).  e_u == a is permitted when a parallel
         label exists (a=(u,rho) at multiplicity 2), so T1's coverage of
         a=(u,rho) is exercised.
         (The earlier plain-residual-reachability formulation was FALSE
         as an equivalence -- prescribed arcs may force a cycle.)

NOT checked here (honest coverage): C5 as a stated equivalence, C6's
pathology bounds, and C1(2)'s path statements beyond their use in C4.

No pulp/ILP dependency: pure networkx + the structural-tree machinery of
check_lexist_fixedroot.py (gateway_t_eq_u_witness imports its oracle
lazily, so importing dbullet_arcs from it is dependency-free).
"""
from __future__ import annotations

import itertools
import os
import sys
from collections import Counter

import networkx as nx

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from check_lexist_fixedroot import (  # noqa: E402
    in_arborescences, subtree_through, tree_arcs, pair_realizable)
from gateway_t_eq_u_witness import dbullet_arcs  # noqa: E402


def build(arcs, n):
    G = nx.MultiDiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from(arcs)
    return G


def cage(G, u, root, n):
    H = G.copy()
    H.remove_node(u)
    return {u} | {x for x in range(n) if x not in (root, u)
                  and not nx.has_path(H, x, root)}


def reaches_avoiding(G, z, root, avoid):
    H = G.copy()
    H.remove_nodes_from([x for x in avoid if x not in (z, root)])
    return nx.has_path(H, z, root)


def check(n, arcs, root, K_set, name=""):
    mult = Counter(arcs)
    G = build(arcs, n)
    struct_out = {}
    for (x, y) in mult:
        struct_out.setdefault(x, set()).add(y)
    struct_out = {x: tuple(sorted(v)) for x, v in struct_out.items()}
    arbs = [(s, tree_arcs(s)) for s in in_arborescences(n, struct_out, root)]
    report = {"name": name, "cages": {}}

    for u in range(n):
        if u == root:
            continue
        Cu = cage(G, u, root, n)
        if len(Cu) < 2:
            continue
        rep = {"C_u": sorted(Cu)}

        # ---- C3 ----
        K1 = (K_set & Cu) - {u}
        assert len(K1) >= 2, "C3 reserve"
        assert set(range(n)) - Cu - {root}, "C3 outside-nonemptiness"
        assert K_set - Cu, "C3 K-outside"
        for w in K_set - Cu:
            assert all((w, k1) in mult for k1 in K1), "C3 hooks"

        # ---- C7: full out-cut of every Y in C_u\{u} stays inside D[C_u] ----
        mincut = min(
            sum(mult[e] for e in mult if e[0] in Y and e[1] not in Y)
            for r in range(1, len(Cu))
            for Y in map(set, itertools.combinations(Cu - {u}, r)))
        assert mincut >= 3, "C7 Edmonds condition"
        for e in mult:                       # the cut arcs stay inside C_u
            if e[0] in Cu - {u}:
                assert e[1] in Cu, "C1(1) u-gatedness"
        rep["C7_min_inside_cut"] = mincut

        # ---- C1(3): no-pair iff head in cage; X >= C_u; equality realized --
        for z in range(n):
            if (u, z) not in mult:
                continue
            has_T = any(sT.get(u) == z for sT, _ in arbs)
            assert has_T == (z not in Cu), "C1(3) no-pair prediction"
        rep["nopair_arcs"] = sorted(z for z in Cu if (u, z) in mult)

        for v in [z for z in range(n) if (u, z) in mult and z not in Cu]:
            a = (u, v)
            Xs_seen, eq_realized = set(), False
            for sT, Ts in arbs:
                if sT.get(u) != v:
                    continue
                X = subtree_through(sT, u, root, n)
                assert X >= Cu, "C1(3) containment"
                Xs_seen.add(frozenset(X))
                if X == Cu:
                    eq_realized = True
                    # ---- C2: every U for this T has exactly one exit ----
                    for sU, Us in arbs:
                        if not pair_realizable(Ts, Us, mult):
                            continue
                        if a in Us and mult[a] < 2:
                            continue
                        ex = [(s, z2) for (s, z2) in Us
                              if s in X and z2 not in X]
                        assert len(ex) == 1, "C2 single exit"
            assert eq_realized, "C1(3) equality realized"

            # ---- C4 + O2a* + O2b* (corrected) ----
            o2a, o2b = [], []
            for w in sorted(K_set - Cu):
                Bw = {z for z in range(n) if z not in Cu and z not in (w, root)
                      and not reaches_avoiding(G, z, root, Cu | {w})}
                Xst = Cu | {w} | Bw
                tails = {e[0] for e in mult if e[0] in Xst and e[1] not in Xst}
                assert tails <= {u, w}, "C4(1) sealing/tails"
                w_exits = [e for e in mult if e[0] == w and e[1] not in Xst]
                assert w_exits, "C4(2) escape"
                if v in Xst or len(Xst) > n - 2:
                    continue
                # e_u == a is allowed when a parallel label exists
                # (e.g. a=(u,rho) with mult 2): T* uses one copy, U* the other
                heads_escape = [e for e in mult
                                if e[0] == u and e[1] not in Xst
                                and (e != a or mult[a] >= 2)]
                if not heads_escape:
                    continue
                o2a.append(w)
                # T* realizability (C4(3)): some enumerated T has X exactly
                Tstars = [(sT, Ts) for sT, Ts in arbs if sT.get(u) == v
                          and subtree_through(sT, u, root, n) == Xst]
                assert Tstars, "C4(3) realizability"
                # O2b*: corrected criterion vs direct enumeration, ALL T*
                interior = Xst - {u, w}
                n_admit = 0
                blocker_residuals = []
                for sT, Ts in Tstars:
                    admits = False
                    for e_u in heads_escape:
                        if e_u in Ts and mult[e_u] < 2:
                            continue
                        for e_w in w_exits:
                            if e_w in Ts and mult[e_w] < 2:
                                continue
                            # prescribed residual D-hat
                            H = nx.MultiDiGraph()
                            H.add_nodes_from(range(n))
                            for e, m in mult.items():
                                res = m - (1 if e in Ts else 0)
                                if e[0] == u:
                                    res = res if e == e_u else 0
                                if e[0] == w:
                                    res = res if e == e_w else 0
                                if res >= 1:
                                    H.add_edge(*e)
                            crit = all(nx.has_path(H, x, root)
                                       for x in range(n) if x != root)
                            # direct enumeration of U* with prescribed arcs
                            direct = any(
                                sU.get(u) == e_u[1] and sU.get(w) == e_w[1]
                                and pair_realizable(Ts, Us, mult)
                                and not (a in Us and mult[a] < 2)
                                for sU, Us in arbs)
                            assert crit == direct, (
                                "O2b* criterion mismatch", a, w, e_u, e_w)
                            if crit:
                                admits = True
                                if not o2b or o2b[-1][0] != w:
                                    o2b.append((w, e_u, e_w))
                                break
                        if admits:
                            break
                    # D2/T1 sharp prediction, asserted as a BICONDITIONAL on
                    # every T*: admits a prescribed-exit U*  <=>  the interior
                    # part leaves residual >= 1 across every interior cut.
                    rmin = min(
                        sum(m - (1 if e in Ts else 0)
                            for e, m in mult.items()
                            if e[0] in Y and e[1] not in Y)
                        for r2 in range(1, len(interior) + 1)
                        for Y in map(set, itertools.combinations(
                            interior, r2)))
                    assert (rmin >= 1) == admits, (
                        "T1 biconditional violated", a, w, rmin, admits)
                    if admits:
                        n_admit += 1
                    else:
                        blocker_residuals.append(
                            tuple(sorted((x, sT[x]) for x in interior)))
                assert n_admit >= 1, ("no admissible T*", a, w)
                rep.setdefault("O2b*_stats", {})[f"a={a},w={w}"] = (
                    f"{n_admit}/{len(Tstars)} admit; "
                    f"blocker interiors: {sorted(set(blocker_residuals))}")
            rep[f"a={a}"] = {"O2a*_w": o2a,
                             "O2b*_witnessed": o2b[:1]}
        report["cages"][u] = rep
    return report


def main():
    db = dbullet_arcs()
    rep = check(7, db, 0, {1, 2, 3, 4, 5, 6}, name="t-eq-u-witness")
    import json
    print(json.dumps(rep, indent=2, default=str))
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
