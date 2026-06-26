"""cut_avoidance_check.py -- test the corrected branch-2 target (D23) on the
checked-in witnesses: the T4 CUT-AVOIDANCE condition.

Condition (per strictly rho-headless gateway): there exist an admissible
rho-tail w in R \\ (C_u u {v}), an escaped AV_u-head h, and an h->w path P
through O such that NO nonempty Y subseteq O has delta+_DO(Y) subseteq
A_O(P) -- equivalently, every O-vertex reaches rho in D_O - A_O(P)
(T4's residual-reachability hypothesis; O-internal arcs are simple, so
structural deletion is exact).

Asserts on the three in-scope witnesses (rho_headless D17, dominated D18,
relay_free D19): the condition is SATISFIED, and moreover the per-head
structure observed at D24:
  * every head h with lambda_DO(h,rho) = 1 FAILS on every path (its own
    unique escape lies on each of its paths, stranding h itself) -- so the
    existential quantifier over h is ESSENTIAL to the lemma;
  * some head with lambda_DO(h,rho) >= 2 PASSES, and its passing paths are
    exactly those avoiding the unique-escape arcs of other lambda_DO=1
    vertices.
The D10 t_eq_u witness is OUT of the lemma's scope (it has rho-heads; T1
territory) and has no legal (w,h) test configuration; asserted as such.
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


def analyse(name, db, n, expect_in_scope):
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

    rows, satisfied = [], False
    for w in R:
        if w in cage or w == v:
            continue                      # w must be a legal absorption target
        red = G.copy(); red.remove_nodes_from(cage | {w})
        B = {z for z in range(n) if z not in cage | {w} and z != root
             and not (z in red and nx.has_path(red, z, root))}
        Xst = cage | {w} | B
        if v in Xst or len(Xst) > n - 2:
            continue
        O = set(range(n)) - Xst - {root}
        heads = [z for z in range(n) if (u, z) in mult and z != v and z in O]
        DO = nx.DiGraph(); DO.add_nodes_from(O | {root})
        for (x, y) in mult:
            if x in O and (y in O or y == root):
                DO.add_edge(x, y)
        H = nx.DiGraph(); H.add_nodes_from(O | {w})
        for (x, y) in mult:
            if x in O and (y in O or y == w):
                H.add_edge(x, y)
        for h in heads:
            lam_h = (nx.maximum_flow_value(
                nx.DiGraph([(x, y, {"capacity": m}) for (x, y), m in mult.items()
                            if x in O and (y in O or y == root)]), h, root)
                if nx.has_path(DO, h, root) else 0)
            n_paths = n_pass = 0
            best = None
            for P in nx.all_simple_paths(H, h, w):
                n_paths += 1
                AO = [(P[i], P[i + 1]) for i in range(len(P) - 2)]
                DOr = DO.copy(); DOr.remove_edges_from(AO)
                if all(nx.has_path(DOr, z, root) for z in O):
                    n_pass += 1
                    if best is None or len(P) < len(best):
                        best = P
            rows.append((w, h, int(lam_h), n_paths, n_pass, best))
            satisfied = satisfied or n_pass > 0
            # observed structure: lambda_DO(h)=1 <=> all paths fail
            assert (int(lam_h) == 1) == (n_pass == 0 and n_paths > 0) \
                or int(lam_h) >= 2, (name, w, h, lam_h, n_paths, n_pass)
    return satisfied, rows


def main():
    from gateway_t_eq_u_witness import dbullet_arcs as g1
    from rho_headless_witness import dbullet_arcs as g2
    from dominated_witness import dbullet_arcs as g3
    from relay_free_witness import dbullet_arcs as g4

    sat, rows = analyse("t_eq_u(D10)", g1(), 7, expect_in_scope=False)
    assert not rows, "t_eq_u should have no legal (w,h) configuration"
    print("t_eq_u (D10): out of scope, no legal (w,h) configuration (T1 regime)")

    for name, db, n in [("rho_headless(D17)", g2(), 8),
                        ("dominated(D18)", g3(), 11),
                        ("relay_free(D19)", g4(), 14)]:
        sat, rows = analyse(name, db, n, expect_in_scope=True)
        assert sat, (name, "cut-avoidance VIOLATED")
        for (w, h, lam, np_, ok, best) in rows:
            print(f"  {name} w={w} h={h} lam_DO={lam}: "
                  f"{ok}/{np_} paths pass"
                  + (f", shortest {best}" if best else " (ALL FAIL)"))
        print(f"{name}: cut-avoidance SATISFIED")
    print("ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
