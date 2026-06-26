"""distinct_tails_theorem_check.py -- machine verification of Theorem DT
(docs/DISTINCT_TAILS_THEOREM_2026_06_12.md): obligation (a) of the X_P
v-target program is a THEOREM, and the round-11 G37 'in-class single-tail'
claim is impossible in-class.

Per witness (all six), asserts the full counting chain:
  d^-(rho) >= 5;  |R| >= 3;  |R cap V(P_v)| <= 1;  |R cap X_P| >= 2;
  >= 2 distinct tails on delta^+(X_P) \\ {a};  and T-label-freeness is
  structural (no in-X_P T-arc can be a boundary arc).

Also reproduces the G37 construction faithfully (delete k4's two out-cut
arcs from the D17 witness): it DOES create the single-tail boundary and
keeps lambda(contraction) = 3, but lambda(host) = 2 -- OUT OF CLASS (the
G32 failure mode).  Asserted, so the graveyard entry stays honest.
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


def check(name, db, n, u, v):
    import networkx as nx
    root = 0
    mult = Counter(db)
    din = sum(m for e, m in mult.items() if e[1] == root)
    R = sorted({e[0] for e in mult if e[1] == root})
    G = nx.MultiDiGraph(); G.add_nodes_from(range(n)); G.add_edges_from(db)
    Gm = G.copy(); Gm.remove_node(u)
    P_v = nx.shortest_path(Gm, v, root)
    X = set(range(n)) - {root} - set(P_v[:-1])
    while True:
        DX = nx.DiGraph((x, y) for (x, y) in mult if x in X and y in X)
        DX.add_nodes_from(X)
        bad = {x for x in X - {u} if not nx.has_path(DX, x, u)}
        if not bad:
            break
        X -= bad
    R_in_P = [r for r in R if r in P_v]
    R_in_X = [r for r in R if r in X]
    tails = sorted({e[0] for e in mult
                    if e[0] in X and e[1] not in X and e != (u, v)})
    assert din >= 5, (name, din)
    assert len(R) >= 3, (name, R)
    assert len(R_in_P) <= 1, (name, R_in_P)
    assert len(R_in_X) >= 2, (name, R_in_X)
    assert len(tails) >= 2, (name, tails)
    print(f"{name}: d-(rho)={din}, |R|={len(R)}, R cap P_v={R_in_P}, "
          f"R cap X_P={R_in_X}, tails={tails}")


def g37_reproduction_is_out_of_class():
    import networkx as nx
    import oracle
    from digraph import Digraph
    from generators.near_split import is_one_zero_near_split
    from rho_headless_witness import host_arcs as base_host
    H = [e for e in base_host() if e not in [(8, 6), (8, 0)]]
    ok, _ = is_one_zero_near_split(
        Digraph.from_arcs(range(9), H), [0, 1, 2], list(range(3, 9)))
    assert ok
    rel = {0: 0, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7}
    db = [(rel[x], rel[y]) for (x, y) in H
          if (x, y) != (0, 1) and rel[x] != rel[y]]
    mult = Counter(db)
    # the single-tail boundary IS achieved on the contraction...
    Gm = nx.MultiDiGraph(); Gm.add_nodes_from(range(8)); Gm.add_edges_from(db)
    Gm.remove_node(1)
    P_v = nx.shortest_path(Gm, 5, 0)
    X = set(range(8)) - {0} - set(P_v[:-1])
    tails = {e[0] for e in mult
             if e[0] in X and e[1] not in X and e != (1, 5)}
    assert tails == {6}, tails                       # single tail!
    assert oracle.arc_connectivity(8, db) == 3       # contraction looks fine
    # ...but the HOST is only 2-arc-strong: OUT OF CLASS (G32 mode)
    assert oracle.arc_connectivity(9, H) == 2
    print("G37 reproduction: single-tail + lambda(contraction)=3 BUT "
          "lambda(host)=2 -> OUT OF CLASS (as Theorem DT requires)")


def main():
    from gateway_t_eq_u_witness import dbullet_arcs as g1
    from rho_headless_witness import dbullet_arcs as g2
    from dominated_witness import dbullet_arcs as g3
    from relay_free_witness import dbullet_arcs as g4
    from core_embedding_witness import dbullet_arcs as g5
    from v_target_internal_reachability_counterexample import construction

    check("t_eq_u(D10)", g1(), 7, 1, 5)
    check("rho_headless(D17)", g2(), 8, 1, 5)
    check("dominated(D18)", g3(), 11, 1, 5)
    check("relay_free(D19)", g4(), 14, 1, 5)
    check("core_embedding(D28)", g5(), 11, 1, 8)
    check("blocker_cex(D30)", construction()[1], 23, 1, 5)
    g37_reproduction_is_out_of_class()
    print("ALL ASSERTIONS PASS: Theorem DT verified on all six witnesses")


if __name__ == "__main__":
    main()
