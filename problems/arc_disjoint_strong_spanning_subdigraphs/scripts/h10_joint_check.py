"""h10_joint_check.py -- red-team the H10 JOINT statement (D34/D35): map,
per witness and per prescription pair, whether FULL D-hat reachability
holds (interior routing AND bounce through O combined).

D38 warning: the universal conclusion suggested by this legacy random
sample is false.  scripts/saturation_kernel_witness.py pins an in-class
cage-sparing T with zero completing prescription pairs.  This script is
retained as the six-witness sample map, not as evidence for a theorem.

Background: Lemma IN (interior-only routing to both prescribed DT-roots)
is in-class FALSE (D34, exhaustive-by-monotonicity).  But the D-hat
reachability that the good pairs actually need is over the FULL digraph:
X_P-vertices may bounce through O (Lemma OUT territory) and use surviving
rho-labels there.  This checker measures, for every witness:

  * the rho-access inventory: |R cap X_P|, mult(p_k -> rho) (the path
    tail's spare label), #boundary tails;
  * for EVERY prescription pair (e1, e2) of boundary arcs (tail in X_P,
    head outside, != a) with DISTINCT tails, over `trials` random
    T = T_in + a + T_out: in how many trials does every vertex reach rho
    in D-hat(T, e1, e2)?

Classification per pair: ROBUST (all trials), SENSITIVE (some), DEAD
(none).  Special attention to the CANONICAL pair ((r1,rho),(r2,rho)):
the D34 kill shows interior-only routing fails on 3/6 -- does bounce
rescue it?

The output of this run is the DATA from which H10's precise statement is
to be written (red-team before formulate before prove).
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


def analyse(name, db, n, u, v, trials=8):
    import networkx as nx
    root = 0
    a = (u, v)
    mult = Counter(db)
    rng = random.Random(20260612)

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
    O = set(range(n)) - X - {root}
    R_in_X = sorted(r for r in {e[0] for e in mult if e[1] == root} if r in X)
    p_k = P_v[-2]
    boundary = [e for e in mult if e[0] in X and e[1] not in X and e != a]
    tails = sorted({e[0] for e in boundary})
    print(f"\n{name}: |X_P|={len(X)} |O|={len(O)} R_in_X={R_in_X} "
          f"mult(p_k={p_k}->rho)={mult.get((p_k, root), 0)} "
          f"boundary arcs={len(boundary)} tails={tails}")

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

    # pre-generate the T sample (shared across pairs for comparability)
    Ts_list = []
    while len(Ts_list) < trials:
        T_in = random_in_arb(X - {u}, u)
        T_out = (reverse_bfs_in_arb(O, set(mult), root, rng)
                 if rng.random() < 0.5 else random_in_arb(O, root))
        if T_in is None or T_out is None:
            continue
        T = dict(T_in); T[u] = v; T.update(T_out)
        Ts_list.append(tree_arcs(T))

    canon = ((R_in_X[0], root), (R_in_X[1], root)) if len(R_in_X) >= 2 else None
    results = {}
    per_T = {}
    for i in range(len(boundary)):
        for j in range(len(boundary)):
            if i == j:
                continue
            e1, e2 = boundary[i], boundary[j]
            if e1[0] == e2[0] or (e2, e1) in results:
                continue
            ok = 0
            per_T.setdefault((e1, e2), [False] * len(Ts_list))
            for ti, Ts in enumerate(Ts_list):
                if e1 in Ts or e2 in Ts:        # boundary arcs are T-free
                    continue                     # (only `a`; never happens)
                H = nx.MultiDiGraph(); H.add_nodes_from(range(n))
                for e, m in mult.items():
                    res = m - (1 if e in Ts else 0)
                    if e[0] == e1[0]:
                        res = res if e == e1 else 0
                    if e[0] == e2[0]:
                        res = res if e == e2 else 0
                    if res >= 1:
                        H.add_edge(*e)
                if all(nx.has_path(H, x, root) for x in range(n) if x != root):
                    ok += 1
                    per_T[(e1, e2)][ti] = True
            results[(e1, e2)] = ok

    robust = [p for p, k in results.items() if k == trials]
    sensitive = [p for p, k in results.items() if 0 < k < trials]
    dead = [p for p, k in results.items() if k == 0]
    canon_status = None
    for p, k in results.items():
        if canon and set(p) == set(canon):
            canon_status = f"{k}/{trials}"
    print(f"  pairs: {len(results)} | ROBUST {len(robust)} | "
          f"SENSITIVE {len(sensitive)} | DEAD {len(dead)}")
    print(f"  CANONICAL pair ((r1,rho),(r2,rho)): "
          f"{canon_status if canon_status else 'not a valid pair here'}")
    # quantifier mapping: for every T, does SOME pair complete it?  And is
    # failure explained by CAGE-CHOKING (cage stranded from u in the
    # T_in-residual interior -- cage vertices are gated, have no boundary
    # arcs, and must route via u)?
    cage_set = {x for x in range(n) if x not in (root,)
                and not (x != u and nx.has_path(Gm, x, root))} | {u}
    per_T_ok = 0
    bad_unexplained = 0
    sparing_total = sparing_ok = 0
    for ti, Ts in enumerate(Ts_list):
        completed = any(per_pair[ti] for per_pair in per_T.values())
        per_T_ok += completed
        # cage-sparing: every cage vertex reaches u in residual D[X_P]
        Hin = nx.MultiDiGraph(); Hin.add_nodes_from(X)
        for e, m in mult.items():
            if e[0] in X and e[1] in X:
                r2_ = m - (1 if e in Ts else 0)
                if r2_ >= 1:
                    Hin.add_edge(*e)
        sparing = all(nx.has_path(Hin, c, u) for c in cage_set - {u})
        if sparing:
            sparing_total += 1
            sparing_ok += completed
        elif completed:
            pass                                   # choked but still ok: fine
        if not completed and sparing:
            bad_unexplained += 1
    print(f"  FORALL-T EXISTS-PAIR: {per_T_ok}/{trials}; cage-sparing T: "
          f"{sparing_ok}/{sparing_total} completed; "
          f"UNEXPLAINED failures (sparing but uncompletable): {bad_unexplained}")
    assert bad_unexplained == 0, (name, "cage-sparing T with no pair!")
    assert sparing_total >= 1, (name, "no cage-sparing T sampled")
    return canon_status, len(robust), len(results)


def main():
    from gateway_t_eq_u_witness import dbullet_arcs as g1
    from rho_headless_witness import dbullet_arcs as g2
    from dominated_witness import dbullet_arcs as g3
    from relay_free_witness import dbullet_arcs as g4
    from core_embedding_witness import dbullet_arcs as g5
    from v_target_internal_reachability_counterexample import construction

    specs = [("t_eq_u(D10,smoke)", g1(), 7, 1, 5),
             ("rho_headless(D17)", g2(), 8, 1, 5),
             ("dominated(D18)", g3(), 11, 1, 5),
             ("relay_free(D19)", g4(), 14, 1, 5),
             ("core_embedding(D28)", g5(), 11, 1, 8),
             ("blocker_cex(D30)", construction()[1], 23, 1, 5)]
    for (name, db, n, u, v) in specs:
        analyse(name, db, n, u, v)
    print("\nLEGACY SAMPLE ASSERTIONS PASS")
    print("D38 pins an in-class cage-sparing T with no completing pair")


if __name__ == "__main__":
    main()
