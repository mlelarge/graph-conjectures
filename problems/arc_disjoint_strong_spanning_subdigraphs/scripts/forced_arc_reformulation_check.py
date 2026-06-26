"""forced_arc_reformulation_check.py -- ground the FORCED-ARC REFORMULATION of
the branch-2 cut-avoidance lemma (A').

Reuses cut_avoidance_check.analyse()'s gateway scaffolding (same root,u,v,cage,
admissible-w, O, D_O semantics).  For each in-scope strictly-rho-headless
gateway witness we:

  F = { arc e of D_O : deleting e disconnects SOME O-vertex from rho in D_O }
      (the in-branching-forced / bridge arcs of the rooted-to-rho subdigraph).

Then we assert, per (w,h):
  (1) PER-PATH equivalence: for every enumerated h->w O-path P,
        cut-avoiding(P)  ==  F-avoiding(A_O(P))
      where cut-avoiding means every O-vertex still reaches rho in D_O - A_O(P)
      and F-avoiding means A_O(P) cap F == {}.   (0 mismatches expected)
  (2) PER-(w,h) EXISTENCE equivalence:
        (some path passes)  ==  h reaches w in (D_O - F) restricted to O u {w}.
      (14/14 expected; F per witness = {} / {(7,5)} / {(7,5)}).

We also pin the n=8 GENERAL-digraph counterexample from the proposal idea and
confirm the existence converse FAILS outside the gateway class (h reaches w in
D-F yet every path kills a set).
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


def forced_arcs(DO, O, root):
    """F = arcs of D_O whose single-arc deletion strands some O-vertex from root.
    D_O is a simple DiGraph on O u {root}; multiplicity is irrelevant for
    reachability so we operate on the simple structure (matches the O-internal
    simple-deletion semantics of cut_avoidance_check)."""
    import networkx as nx
    # baseline: every O-vertex must reach root (else F undefined / vacuous)
    F = set()
    for (x, y) in list(DO.edges()):
        H = DO.copy()
        H.remove_edge(x, y)
        if any(not nx.has_path(H, z, root) for z in O):
            F.add((x, y))
    return F


def analyse(name, db, n, expect_in_scope, expect_F):
    import networkx as nx
    root, u, a, v = 0, 1, (1, 5), 5
    mult = Counter(db)
    G = nx.MultiDiGraph(); G.add_nodes_from(range(n)); G.add_edges_from(db)
    Gm = G.copy(); Gm.remove_node(u)
    cage = {u} | {x for x in range(n) if x not in (root, u)
                  and not nx.has_path(Gm, x, root)}
    R = sorted({e[0] for e in mult if e[1] == root})
    strictly_rho_headless = (u, root) not in mult
    assert strictly_rho_headless == expect_in_scope, name

    rows = []
    per_path_mismatch = 0
    per_wh_mismatch = 0
    F_union = set()
    for w in R:
        if w in cage or w == v:
            continue
        red = G.copy(); red.remove_nodes_from(cage | {w})
        B = {z for z in range(n) if z not in cage | {w} and z != root
             and not (z in red and nx.has_path(red, z, root))}
        Xst = cage | {w} | B
        if v in Xst or len(Xst) > n - 2:
            continue
        O = set(range(n)) - Xst - {root}
        heads = [z for z in range(n) if (u, z) in mult and z != v and z in O]

        # D_O: O-internal arcs plus arcs into root (simple)
        DO = nx.DiGraph(); DO.add_nodes_from(O | {root})
        for (x, y) in mult:
            if x in O and (y in O or y == root):
                DO.add_edge(x, y)
        # H_w: O-internal arcs plus arcs into w (path enumeration graph)
        Hw = nx.DiGraph(); Hw.add_nodes_from(O | {w})
        for (x, y) in mult:
            if x in O and (y in O or y == w):
                Hw.add_edge(x, y)

        F = forced_arcs(DO, O, root)
        F_union |= F

        # D_O - F restricted to O u {w}: O-internal arcs (minus F) plus arcs into w
        DmF = nx.DiGraph(); DmF.add_nodes_from(O | {w})
        for (x, y) in mult:
            if x in O and (y in O or y == w):
                if (x, y) in F:
                    continue
                DmF.add_edge(x, y)

        for h in heads:
            n_paths = n_pass = 0
            for P in nx.all_simple_paths(Hw, h, w):
                n_paths += 1
                AO = [(P[i], P[i + 1]) for i in range(len(P) - 2)]  # drop final hop into w
                DOr = DO.copy(); DOr.remove_edges_from(AO)
                cut_avoiding = all(nx.has_path(DOr, z, root) for z in O)
                f_avoiding = all(e not in F for e in AO)
                if cut_avoiding != f_avoiding:
                    per_path_mismatch += 1
                if cut_avoiding:
                    n_pass += 1
            exist_path = n_pass > 0
            exist_reach_minusF = nx.has_path(DmF, h, w)
            if exist_path != exist_reach_minusF:
                per_wh_mismatch += 1
            rows.append((w, h, n_paths, n_pass, exist_path, exist_reach_minusF))

    if expect_F is not None:
        assert F_union == expect_F, (name, "F mismatch", F_union, expect_F)
    return rows, per_path_mismatch, per_wh_mismatch, F_union


def tournament_core_counterexample():
    """D27 negative control (replaces the dead n=8 pin, which was in fact
    cut-avoiding -- G34): the reviewer's TOURNAMENT CORE refuting the H9
    CONVERSE generically.  O = {0..4}, internal tournament
    1->0, 0->2, 0->3, 4->0, 2->1, 3->1, 1->4, 3->2, 4->2, 4->3, plus
    3->rho, 4->rho, 4->w.  Then:
      * F = {(2,1)} (the only singleton-stranding D_O-arc);
      * h=0 reaches w in D_O - F, UNIQUELY along P: 0->3->1->4->w;
      * but Y = {0,1,2} has delta+_DO(Y) = {(0,3),(1,4)} subseteq A_O(P):
        joint deletion covers a 2-arc root cut containing NO forced arc --
        the quantifier error (forall T: A(P) cap T != 0  does NOT give
        exists e in A(P) forall T: e in T);
      * lambda_DO(0,rho) = 2, so two arc-disjoint h->rho routes do NOT
        eliminate the joint-deletion obstruction either.
    Asserts: forward implication holds (no cut-avoiding path uses F);
    converse FAILS (reach in D_O - F, yet no cut-avoiding path exists)."""
    import networkx as nx
    O = {0, 1, 2, 3, 4}
    rho, w = "r", "w"
    arcs = [(1, 0), (0, 2), (0, 3), (4, 0), (2, 1), (3, 1), (1, 4),
            (3, 2), (4, 2), (4, 3), (3, rho), (4, rho), (4, w)]
    DO = nx.DiGraph((x, y) for (x, y) in arcs if x in O and (y in O or y == rho))
    F = forced_arcs(DO, O, rho)
    assert F == {(2, 1)}, F
    DmF = DO.copy(); DmF.remove_edges_from(F)
    Hw = nx.DiGraph((x, y) for (x, y) in arcs if x in O and (y in O or y == w))
    HmF = Hw.copy(); HmF.remove_edges_from(F)
    paths_mF = list(nx.all_simple_paths(HmF, 0, w))
    assert paths_mF == [[0, 3, 1, 4, w]], paths_mF      # unique F-avoiding path
    any_pass = False
    for P in nx.all_simple_paths(Hw, 0, w):
        AO = [(P[i], P[i + 1]) for i in range(len(P) - 2)]
        DOr = DO.copy(); DOr.remove_edges_from(AO)
        if all(nx.has_path(DOr, z, rho) for z in O):
            any_pass = True
    assert not any_pass                                  # converse FAILS
    cap = nx.DiGraph(); cap.add_edges_from(DO.edges(), capacity=1)
    assert nx.maximum_flow_value(cap, 0, rho) == 2       # lambda_DO(h)=2
    Y = {0, 1, 2}
    dY = {(x, y) for (x, y) in DO.edges() if x in Y and y not in Y}
    assert dY == {(0, 3), (1, 4)} and not (dY & F)       # 2-cut, F-free
    return True


def main():
    from rho_headless_witness import dbullet_arcs as g2
    from dominated_witness import dbullet_arcs as g3
    from relay_free_witness import dbullet_arcs as g4

    specs = [("rho_headless(D17)", g2(), 8, set()),
             ("dominated(D18)", g3(), 11, {(7, 5)}),
             ("relay_free(D19)", g4(), 14, {(7, 5)})]

    total_wh = 0
    total_path_mismatch = 0
    total_wh_mismatch = 0
    for name, db, n, expF in specs:
        rows, pm, wm, Fu = analyse(name, db, n, True, expF)
        total_wh += len(rows)
        total_path_mismatch += pm
        total_wh_mismatch += wm
        print(f"{name}: F = {sorted(Fu)}")
        for (w, h, np_, ok, ep, er) in rows:
            flag = "OK" if ep == er else "MISMATCH"
            print(f"  w={w} h={h}: {ok}/{np_} cut-avoiding; "
                  f"exist_path={ep} reach(D_O-F)={er} [{flag}]")
        print(f"  per-path mismatches={pm}, per-(w,h) mismatches={wm}")

    print()
    assert tournament_core_counterexample()
    print("tournament-core negative control: H9 converse REFUTED (generic), forward holds")
    print(f"TOTAL (w,h) pairs = {total_wh} "
          f"(expect 14); per-path mismatches = {total_path_mismatch} "
          f"(expect 0); per-(w,h) mismatches = {total_wh_mismatch} (expect 0)")


    # Final verdict assertions
    assert total_wh == 14, ("expected 14 (w,h) pairs", total_wh)
    assert total_path_mismatch == 0, ("per-path equivalence violated",
                                      total_path_mismatch)
    assert total_wh_mismatch == 0, ("per-(w,h) equivalence violated",
                                    total_wh_mismatch)
    print()
    print("IN-CLASS witnesses: forced-arc equivalence holds (F={}/{(7,5)}/{(7,5)}, "
          "14/14 (w,h), 0 mismatches) -- but per D27 review the CONVERSE is "
          "REFUTED GENERICALLY by the tournament core above; the witnesses' "
          "agreement is family-scoped evidence only, and any in-class H9 "
          "theorem needs a gateway invariant excluding that core.")


if __name__ == "__main__":
    main()
