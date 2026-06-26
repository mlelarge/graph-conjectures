"""xp_distinct_tails_census.py -- A''' OBLIGATION (a) red-team.

next_action (D30) obligation (a) DISTINCT-TAILS: on every strictly
rho-headless hard gateway, delta+(X_P) \\ {a} carries label-free arcs at
>= 2 DISTINCT tails (so the U-side can pick two exits with distinct tails,
the one-out-arc-per-tail requirement of a U in-arborescence).  The
DANGER CASE flagged in next_action is single-tail concentration: every
arc of delta+(X_P)\\{a} sharing one tail (the t_eq_u shape, where it
survives only via mult-2 rho-arcs at u).

This is the concrete un-run finite check.  It re-uses the EXACT X_P
construction of v_target_check.py (shortest P_v in D-u, J(P) closure of
no-path-to-u I-vertices, X_P = V\\({rho} u V(P_v) u J)) and reports, per
witness:
  - |X_P|, P_v, J
  - the multiset of TAILS of delta+(X_P) (cut arcs out of X_P)
  - the multiset of tails of delta+(X_P) \\ {a}
  - #distinct tails, and #distinct tails carrying a LABEL-FREE arc
    (i.e. tails t s.t. some out-cut arc at t has multiplicity >= 1
     -- trivially true for any present arc, but we also report the
     tails reachable AFTER removing a single fixed in-arb T's one arc
     per the obligation's 'label-free of T' clause as a worst case).

PASS for obligation (a) = every witness has >= 2 distinct tails on
delta+(X_P)\\{a}.  A witness with exactly ONE tail would be the danger
case and would need the mult-2 rho-arc escape hatch.
"""
from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict

import networkx as nx

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def compute_X_P(db, n, u, v, K_set):
    """Exactly the v_target_check.py X_P construction."""
    mult = Counter(db)
    root = 0
    Gm = nx.MultiDiGraph()
    Gm.add_nodes_from(range(n))
    Gm.add_edges_from(db)
    Gm.remove_node(u)
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
    if K_set is not None:
        assert not (J & K_set), ("K-vertex removed", sorted(J & K_set))
    assert 2 <= len(X) <= n - 2
    return mult, X, P_v, J, root


def out_cut(mult, X):
    """delta+(X): arcs with tail in X, head outside X, with multiplicity."""
    out = Counter()
    for (x, y), m in mult.items():
        if x in X and y not in X:
            out[(x, y)] += m
    return out


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

    all_pass = True
    for (name, db, n, u, v, K_set) in specs:
        mult, X, P_v, J, root = compute_X_P(db, n, u, v, K_set)
        a = (u, v)
        out = out_cut(mult, X)
        # tails of the full out-cut
        tails_full = Counter()
        for (x, y), m in out.items():
            tails_full[x] += m
        # out-cut minus a (remove the labelled arc a once; if a has mult>1
        # the tail u still carries label-free copies)
        out_minus_a = Counter(out)
        if a in out_minus_a:
            out_minus_a[a] -= 1
            if out_minus_a[a] == 0:
                del out_minus_a[a]
        tails_minus_a = set(x for (x, y) in out_minus_a)
        # WORST CASE label-free-of-T: for EVERY in-arb T of D[X] rooted u,
        # T consumes exactly one out-arc per non-root... but out-cut arcs
        # leave X so T (in-arb of X to u) never uses them as tree arcs
        # unless tail has its tree-arc among them. Conservative worst case:
        # a single arc per tail could be a tree arc. So a tail t survives
        # label-free iff sum of out-cut mult at t >= (#out-cut arcs at t
        # that could be forced as the unique tree arc) -- but tree arc of t
        # in an in-arb to u goes INTO X (head in X), so out-cut arcs (head
        # outside X) are NEVER tree arcs of the inside in-arb. Hence every
        # present out-cut arc is automatically label-free of the inside T.
        # The only T-consumption is the OUTSIDE T_out + a. So 'label-free
        # of T' = present in delta+(X_P)\\{a} minus outside-T_out usage.
        # outside T_out is an in-arb of (V\X\{rho}) rooted rho; its arcs
        # have tail OUTSIDE X, so again never an out-cut-of-X arc.
        # Conclusion: delta+(X_P)\\{a} is ENTIRELY label-free of T.
        distinct_tails = len(tails_minus_a)
        ok = distinct_tails >= 2
        all_pass &= ok
        # report per-tail arc list
        per_tail = defaultdict(list)
        for (x, y), m in out_minus_a.items():
            per_tail[x].append((y, m))
        tail_summary = {t: sorted(per_tail[t]) for t in sorted(per_tail)}
        # is u among the tails, and does u rely solely on mult>=2 rho-arc?
        u_arcs = per_tail.get(u, [])
        flag = "OK(>=2 tails)" if ok else "DANGER(single tail)"
        print(f"{name}: |X_P|={len(X)} P_v={P_v} J={sorted(J)} a={a}")
        print(f"   delta+(X_P)\\{{a}} tails={distinct_tails} -> {flag}")
        print(f"   per-tail arcs (head,mult): {tail_summary}")
        if u in tails_minus_a:
            print(f"   u={u} out-cut arcs: {sorted(u_arcs)}")
        print()

    print("OBLIGATION (a) DISTINCT-TAILS:",
          "ALL >=2 distinct tails" if all_pass else "FAILED on >=1 witness")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
