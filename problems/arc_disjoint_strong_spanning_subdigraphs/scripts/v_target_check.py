"""v_target_check.py -- red-team V-TARGET ABSORPTION on all six checked-in
witnesses, in its D30-CORRECTED X_P form.

History: the A-double-prime form (X = V minus ({rho} u V(P_v))) was REFUTED
in-class by v_target_internal_reachability_counterexample.py (D30):
independent I-blockers x with N+(x) subseteq V(P) sit in X with no
D[X]-path to u, for EVERY shortest path P.  Corrected mechanism
(reviewer's repair):

    J(P) := closure of {x in X : no D[X]-path to u}   (only I-vertices --
            K-vertices keep cage hooks; ASSERTED via K_set)
    X_P  := V minus ({rho} u V(P_v) u J(P))

T := (random-attachment in-arb of D[X_P] rooted u -- NEVER reverse-BFS,
whose star consumes the cage cut, the D2/D10 lesson) + a + (reverse-BFS
in-arb of the outside, = P_v chain + blocker leaves, rooted rho).
U := found via the corrected prescribed-residual criterion (D13) over
candidate exit pairs with distinct tails.

Asserts a verified GOOD pair (valid arc-disjoint in-arbs, X exact, >=2
exits, strict exit) on EVERY witness including the D30 blocker
counterexample.  Remaining A-triple-prime proof obligations (NOT settled
here): (a) delta+(X_P) minus {a} carries >= 2 distinct tails; (b) a T
keeping every residual cut nonempty after prescribing those exits.
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

from check_lexist_fixedroot import subtree_through, tree_arcs  # noqa: E402


def is_in_arb(succ, n, root):
    for s in range(n):
        if s == root:
            continue
        seen, cur = set(), s
        while cur != root:
            if cur in seen or cur not in succ:
                return False
            seen.add(cur)
            cur = succ[cur]
    return True


def reverse_bfs_in_arb(vertices, arcs_set, target, rng):
    """In-arborescence on `vertices` rooted at `target` using arcs in
    arcs_set (tail,head both meaningful); randomized tie-breaks."""
    import networkx as nx
    G = nx.DiGraph()
    G.add_nodes_from(vertices | {target})
    G.add_edges_from((x, y) for (x, y) in arcs_set
                     if x in vertices and (y in vertices or y == target))
    succ = {}
    dist = {target: 0}
    frontier = [target]
    while frontier:
        nxt = []
        for f in frontier:
            preds = [p for p in G.predecessors(f) if p not in dist]
            rng.shuffle(preds)
            for p in preds:
                if p not in dist:
                    dist[p] = dist[f] + 1
                    succ[p] = f
                    nxt.append(p)
        frontier = nxt
    if set(succ) != vertices - {target}:
        return None
    return succ


def try_witness(name, db, n, u, v, K_set=None):
    import networkx as nx
    root = 0
    a = (u, v)
    mult = Counter(db)
    rng = random.Random(20260612)

    # v's escape path (avoiding u); shortest keeps X maximal
    Gm = nx.MultiDiGraph(); Gm.add_nodes_from(range(n)); Gm.add_edges_from(db)
    Gm.remove_node(u)
    P_v = nx.shortest_path(Gm, v, root)
    X = set(range(n)) - {root} - set(P_v[:-1])
    v_in_R = (v, root) in mult
    # D30 correction (A'' refutation): iteratively remove X-vertices with no
    # D[X]-path to u (the closure of the reviewer's J(P) -- independent
    # blockers whose whole out-neighbourhood lies on P).  Only I-vertices may
    # ever be removed (K-vertices keep cage hooks); asserted via K_set.
    J = set()
    while True:
        DX = nx.DiGraph((x, y) for (x, y) in mult if x in X and y in X)
        DX.add_nodes_from(X)
        bad = {x for x in X - {u} if not nx.has_path(DX, x, u)}
        if not bad:
            break
        J |= bad
        X -= bad
    if K_set is not None:
        assert not (J & K_set), ("K-vertex removed by closure", sorted(J & K_set))
    assert 2 <= len(X) <= n - 2

    def random_in_arb(vertices, arcs, target):
        """Random spanning in-arb on vertices rooted at target: grow the
        tree by attaching a uniformly random (outside -> tree) arc.  Unlike
        reverse-BFS this can SPARE bottleneck arcs (the D2/D10 lesson: a
        BFS star consumes the cage's whole interior cut)."""
        S = {target}
        succ = {}
        cand = [(x, y) for (x, y) in arcs
                if x in vertices and (y in vertices or y == target)]
        while S != vertices | {target}:
            choices = [(x, y) for (x, y) in cand if x not in S and y in S]
            if not choices:
                return None
            x, y = rng.choice(choices)
            succ[x] = y
            S.add(x)
        return succ

    for attempt in range(200):
        T_in = random_in_arb(X - {u}, set(mult), u)
        if T_in is None:
            return None
        T = dict(T_in); T[u] = v
        outside = set(range(n)) - X - {root}
        T_out = reverse_bfs_in_arb(outside, set(mult), root, rng)
        if T_out is None:
            return None
        T.update(T_out)
        Ts = tree_arcs(T)
        if not is_in_arb(T, n, root):
            continue
        if subtree_through(T, u, root, n) != X:
            continue
        # candidate exits: arcs leaving X with a T-free label
        exits = [e for e in mult
                 if e[0] in X and e[1] not in X
                 and mult[e] - (e in Ts) >= 1]
        rng.shuffle(exits)
        for i in range(len(exits)):
            for j in range(i + 1, len(exits)):
                e1, e2 = exits[i], exits[j]
                if e1[0] == e2[0]:
                    continue                  # one out-arc per tail
                H = nx.MultiDiGraph(); H.add_nodes_from(range(n))
                for e, m in mult.items():
                    res = m - (1 if e in Ts else 0)
                    if e[0] == e1[0]:
                        res = res if e == e1 else 0
                    if e[0] == e2[0]:
                        res = res if e == e2 else 0
                    if res >= 1:
                        H.add_edge(*e)
                if not all(nx.has_path(H, x, root)
                           for x in range(n) if x != root):
                    continue
                # construct U explicitly from the residual (reverse BFS)
                U = reverse_bfs_in_arb(set(range(n)) - {root},
                                       set(H.edges()), root, rng)
                if U is None:
                    continue
                U[e1[0]], U[e2[0]] = e1[1], e2[1]
                Us = tree_arcs(U)
                if not is_in_arb(U, n, root):
                    continue
                if any(mult[e] < 2 for e in Ts & Us):
                    continue
                ex = sorted(e for e in Us if e[0] in X and e[1] not in X)
                if len(ex) < 2:
                    continue
                strict = [e for e in ex
                          if (subtree_through(U, e[0], root, n) & X) < X]
                if not strict:
                    continue
                return dict(name=name, n=n, a=a, v_in_R=v_in_R,
                            P_v=P_v, J=sorted(J), X=sorted(X),
                            exits=ex, strict=strict)
    return None


def main():
    from gateway_t_eq_u_witness import dbullet_arcs as g1
    from rho_headless_witness import dbullet_arcs as g2
    from dominated_witness import dbullet_arcs as g3
    from relay_free_witness import dbullet_arcs as g4
    from core_embedding_witness import dbullet_arcs as g5

    from v_target_internal_reachability_counterexample import construction
    db6 = construction()[1]

    specs = [("t_eq_u(D10)", g1(), 7, 1, 5, set(range(1, 7))),
             ("rho_headless(D17)", g2(), 8, 1, 5, set(range(2, 8))),
             ("dominated(D18)", g3(), 11, 1, 5, set(range(2, 11))),
             ("relay_free(D19)", g4(), 14, 1, 5, set(range(2, 14))),
             ("core_embedding(D28)", g5(), 11, 1, 8, set(range(2, 11))),
             ("blocker_cex(D30)", db6, 23, 1, 5, set(range(2, 14)))]

    for (name, db, n, u, v, K_set) in specs:
        r = try_witness(name, db, n, u, v, K_set)
        assert r is not None, (name, "V-TARGET (X_P form) FAILED")
        minimal = "X = V-{rho,v} (minimal)" if len(r["P_v"]) == 2 and not r["J"] \
            else f"X = V-(rho u P_v u J), P_v={r['P_v']}, J={r['J']}"
        print(f"{name}: GOOD pair via X_P v-target; v in R: {r['v_in_R']}; "
              f"{minimal}; exits={r['exits']}; strict={r['strict']}")
    print("ALL ASSERTIONS PASS: X_P-form v-target repairs all six witnesses")


if __name__ == "__main__":
    main()
