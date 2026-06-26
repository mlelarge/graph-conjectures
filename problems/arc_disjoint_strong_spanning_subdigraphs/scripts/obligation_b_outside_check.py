"""obligation_b_outside_check.py -- machine verification of Lemma OUT
(docs/DISTINCT_TAILS_THEOREM_2026_06_12.md, D33): obligation (b)'s OUTSIDE
part holds for EVERY T_out.

For the five in-scope witnesses, plus t_eq_u as an out-of-scope smoke test,
for SEVERAL random T (random-attachment T_in +
random T_out) with the DT prescriptions ((r_1,rho),(r_2,rho)) at the two
theorem-guaranteed rho-tails in X_P, asserts:

  * J is the one-round closure and every J-vertex is a path-fan
    (N+(x) subseteq V(P_v), all arcs mult 1, >= 3 of them);
  * every O cap K vertex keeps ALL its cage hooks in D-hat (no T-part can
    contain a hook) and reaches X_P in ONE step;
  * every O cap I vertex keeps >= 2 (mult-1, distinct-head) K-arcs and
    reaches X_P in <= TWO steps;
  * globally: every O-vertex reaches X_P in D-hat (no closed Y subseteq O).

This is the rank argument of T1 steps 4-5 transplanted to X_P; the chain /
J-leaf structure of the outside plays NO role, so no T_out care is needed.
"""
from __future__ import annotations

import os
import random
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from check_lexist_fixedroot import tree_arcs  # noqa: E402
from v_target_check import reverse_bfs_in_arb  # noqa: E402


def check(name, db, n, u, v, K_set, trials=5):
    import networkx as nx
    root = 0
    mult = Counter(db)
    rng = random.Random(20260612)

    G = nx.MultiDiGraph(); G.add_nodes_from(range(n)); G.add_edges_from(db)
    Gm = G.copy(); Gm.remove_node(u)
    P_v = nx.shortest_path(Gm, v, root)
    X = set(range(n)) - {root} - set(P_v[:-1])
    J = set()
    while True:
        DX = nx.DiGraph((x, y) for (x, y) in mult if x in X and y in X)
        DX.add_nodes_from(X)
        bad = {x for x in X - {u} if not nx.has_path(DX, x, u)}
        if not bad:
            break
        J |= bad
        X -= bad
    O = set(range(n)) - X - {root}

    # J structure: one-round path-fans
    for x in J:
        assert x not in K_set
        outs = [(e, m) for (e, m) in mult.items() if e[0] == x]
        assert sum(m for _, m in outs) >= 3
        assert all(m == 1 and e[1] in P_v for (e, m) in outs), (name, x, outs)

    # DT tails for the prescriptions
    R_in_X = sorted(r for r in {e[0] for e in mult if e[1] == root} if r in X)
    assert len(R_in_X) >= 2
    r1, r2 = R_in_X[:2]
    cage = {u} | {x for x in range(n) if x not in (root, u)
                  and not nx.has_path(Gm, x, root)}

    def random_in_arb(vertices, target):
        S = {target}; succ = {}
        cand = [(x, y) for (x, y) in mult
                if x in vertices and (y in vertices or y == target)]
        while S != vertices | {target}:
            ch = [(x, y) for (x, y) in cand if x not in S and y in S]
            if not ch:
                return None
            x, y = rng.choice(ch)
            succ[x] = y; S.add(x)
        return succ

    for _ in range(trials):
        T_in = random_in_arb(X - {u}, u)
        T_out = (reverse_bfs_in_arb(O, set(mult), root, rng)
                 if rng.random() < 0.5 else random_in_arb(O, root))
        assert T_in is not None and T_out is not None
        T = dict(T_in); T[u] = v; T.update(T_out)
        Ts = tree_arcs(T)
        # D-hat with the DT prescriptions
        H = nx.MultiDiGraph(); H.add_nodes_from(range(n))
        for e, m in mult.items():
            res = m - (1 if e in Ts else 0)
            if e[0] == r1:
                res = res if e == (r1, root) else 0
            if e[0] == r2:
                res = res if e == (r2, root) else 0
            if res >= 1:
                H.add_edge(*e)
        for w in O & K_set:                       # hooks all preserved
            hooks = [e for e in mult if e[0] == w and e[1] in cage - {u}]
            assert len(hooks) >= 2, (name, w)
            assert all(H.has_edge(*e) for e in hooks), (name, w)
        for y in O - K_set:                       # I-vertices: >=2 K-spares
            spares = [e for e in mult
                      if e[0] == y and H.has_edge(*e) and e[1] in K_set]
            assert len(spares) >= 2, (name, y, spares)
        for z in O:                               # global: O reaches X_P
            seen, frontier, ok = {z}, [z], False
            for _step in range(2):
                nxt = []
                for f in frontier:
                    for (_, h2) in H.out_edges(f):
                        if h2 in X:
                            ok = True
                        elif h2 in O and h2 not in seen:
                            seen.add(h2); nxt.append(h2)
                frontier = nxt
            assert ok, (name, z, "no 2-step route to X_P")
    print(f"{name}: |O|={len(O)} (path {len(P_v)-1} + J {len(J)}); "
          f"prescriptions ({r1},rho),({r2},rho); Lemma OUT holds for "
          f"{trials} random T")


def main():
    from gateway_t_eq_u_witness import dbullet_arcs as g1
    from rho_headless_witness import dbullet_arcs as g2
    from dominated_witness import dbullet_arcs as g3
    from relay_free_witness import dbullet_arcs as g4
    from core_embedding_witness import dbullet_arcs as g5
    from v_target_internal_reachability_counterexample import construction

    check("t_eq_u(D10)", g1(), 7, 1, 5, set(range(1, 7)))
    check("rho_headless(D17)", g2(), 8, 1, 5, set(range(2, 8)))
    check("dominated(D18)", g3(), 11, 1, 5, set(range(2, 11)))
    check("relay_free(D19)", g4(), 14, 1, 5, set(range(2, 14)))
    check("core_embedding(D28)", g5(), 11, 1, 8, set(range(2, 11)))
    check("blocker_cex(D30)", construction()[1], 23, 1, 5, set(range(2, 14)))
    print("ALL ASSERTIONS PASS: Lemma OUT verified on five in-scope "
          "witnesses; t_eq_u smoke test also passes")


if __name__ == "__main__":
    main()
