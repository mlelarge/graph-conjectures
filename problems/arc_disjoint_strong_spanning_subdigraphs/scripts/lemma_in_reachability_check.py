"""lemma_in_reachability_check.py -- RED-TEAM the LAST open statement of the
branch-2 X_P program: LEMMA IN (D33 / next_action).

CLAIM (existential over T_in, in the Theorem-DT setting):
    Some in-X_P in-arborescence T_in rooted at u exists such that, in
        D-hat[X_P] := D[X_P] - labels(T_in)
    with the DT rho-tails r1, r2 having ALL their in-X_P out-arcs removed
    (their out-arcs are prescribed to their rho-arcs, which leave X_P),
    EVERY X_P-vertex reaches {r1, r2}.

This is the INSIDE half of obligation (b); Lemma OUT already discharged the
outside.  The lemma is EXISTENTIAL over T_in, so:
  * it HOLDS on a witness iff SOME enumerated/random T_in achieves
    all-of-X_P-reaches-{r1,r2} in D-hat[X_P];
  * it would be REFUTED in-class by a witness where EVERY admissible T_in
    strands some X_P-vertex from {r1,r2}.

Construction of X_P, J, P_v, r1, r2 is byte-for-byte the same as
obligation_b_outside_check.py / v_target_check.py (same six witnesses, same
HOST-lambda-gated, checked-in objects).  T_in is a RANDOM-ATTACHMENT in-arb
of D[X_P-{u}] rooted at u (NEVER reverse-BFS -- the D2/D10 star-consumption
lesson; reverse-BFS a load-bearing tree is explicitly forbidden by
next_action).

For each witness we report, over MANY random T_in:
  * how many T_in make LEMMA IN succeed (every X_P-vertex reaches {r1,r2}
    in D-hat[X_P]);
  * if any succeed -> LEMMA IN HOLDS on this witness;
  * if NONE succeed over the trial budget -> CANDIDATE COUNTEREXAMPLE (which
    X_P-vertices get stranded, by how many T_in).

We also record the structural quantity next_action asked for: how many
X_P-internal arcs head into {r1, r2} (the in-arcs that survive unless T_in
uses them) and whether r1, r2 are themselves the only sinks behind the
prescription.
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


def build_xp(name, db, n, u, v, K_set):
    """Exact X_P / J / P_v / r1, r2 construction shared with the other
    branch-2 checkers.  Returns a dict of the structural data."""
    import networkx as nx
    root = 0
    mult = Counter(db)

    Gm = nx.MultiDiGraph(); Gm.add_nodes_from(range(n)); Gm.add_edges_from(db)
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
    assert not (J & K_set), ("K-vertex removed by closure", sorted(J & K_set))
    assert 2 <= len(X) <= n - 2

    # DT rho-tails inside X_P (the two prescribed roots)
    R_in_X = sorted(r for r in {e[0] for e in mult if e[1] == root} if r in X)
    assert len(R_in_X) >= 2, (name, "Theorem DT guarantees >=2 R-tails in X_P",
                              R_in_X)
    r1, r2 = R_in_X[:2]
    return dict(mult=mult, root=root, X=X, J=J, P_v=P_v, r1=r1, r2=r2,
                R_in_X=R_in_X, K_set=K_set)


def random_in_arb_xp(X, u, mult, rng):
    """Random-attachment spanning in-arb of D[X] rooted at u, using ONLY arcs
    internal to X (both endpoints in X).  Grows by attaching a uniformly
    random (not-yet-in-tree -> in-tree) internal arc.  Spares bottlenecks
    that a BFS star would consume."""
    S = {u}
    succ = {}
    internal = [(x, y) for (x, y) in mult if x in X and y in X]
    target = X
    while S != target:
        choices = [(x, y) for (x, y) in internal if x not in S and y in S]
        if not choices:
            return None
        x, y = rng.choice(choices)
        succ[x] = y
        S.add(x)
    return succ


def dhat_xp_edges(X, mult, Ts, r1, r2):
    """Arcs of D-hat[X_P]: internal-to-X residual arcs after removing T_in
    labels, with r1, r2's in-X out-arcs all removed (prescribed to rho)."""
    edges = []
    for e, m in mult.items():
        if not (e[0] in X and e[1] in X):
            continue                       # only internal arcs matter for IN
        res = m - (1 if e in Ts else 0)
        if e[0] == r1 or e[0] == r2:
            res = 0                        # out-arcs prescribed away to rho
        if res >= 1:
            edges.append(e)
    return edges


def check(name, db, n, u, v, K_set, trials=400):
    import networkx as nx
    d = build_xp(name, db, n, u, v, K_set)
    mult, X, r1, r2 = d["mult"], d["X"], d["r1"], d["r2"]
    rng = random.Random(20260612)

    roots = {r1, r2}
    # structural quantity next_action asked for: X_P-internal in-arcs to r1,r2
    in_to_roots = [e for e in mult if e[0] in X and e[1] in roots and e[0] not in roots]
    # vertices that MUST reach {r1,r2}: all of X_P (r1,r2 trivially "reach"
    # themselves -- they are the targets)
    must_reach = X - roots

    n_succeed = 0
    n_arb_fail = 0
    strand_counter = Counter()        # x -> # of T_in that strand x
    a_good_Tin = None
    for _ in range(trials):
        T_in = random_in_arb_xp(X, u, mult, rng)
        if T_in is None:
            n_arb_fail += 1
            continue
        Ts = tree_arcs(T_in)          # tree_arcs on a {child:parent} dict
        H = nx.DiGraph()
        H.add_nodes_from(X)
        H.add_edges_from(dhat_xp_edges(X, mult, Ts, r1, r2))
        stranded = [x for x in must_reach
                    if not (nx.has_path(H, x, r1) or nx.has_path(H, x, r2))]
        if not stranded:
            n_succeed += 1
            if a_good_Tin is None:
                a_good_Tin = dict(T_in)
        else:
            for x in stranded:
                strand_counter[x] += 1

    holds = n_succeed > 0
    print(f"\n=== {name} ===")
    print(f"  |X_P|={len(X)}  X_P={sorted(X)}  r1={r1} r2={r2}  "
          f"R_in_X={d['R_in_X']}")
    print(f"  X_P-internal in-arcs heading into {{r1,r2}}: "
          f"{len(in_to_roots)}  {sorted(in_to_roots)}")
    print(f"  random T_in trials={trials}  built_ok={trials-n_arb_fail}  "
          f"arb_build_fail={n_arb_fail}")
    print(f"  T_in achieving LEMMA IN (all X_P reach {{r1,r2}}): {n_succeed}")
    if holds:
        # hard assertion: a concrete good T_in exists and is re-verified
        Ts = tree_arcs(a_good_Tin)
        H = nx.DiGraph(); H.add_nodes_from(X)
        H.add_edges_from(dhat_xp_edges(X, mult, Ts, r1, r2))
        bad = [x for x in must_reach
               if not (nx.has_path(H, x, r1) or nx.has_path(H, x, r2))]
        assert not bad, (name, "re-verify good T_in failed", bad)
        print(f"  LEMMA IN HOLDS: good T_in re-verified, 0 stranded.")
    else:
        worst = strand_counter.most_common(6)
        print(f"  *** NO T_in succeeded -> CANDIDATE COUNTEREXAMPLE ***")
        print(f"  most-stranded X_P-vertices (x: #T_in stranding): {worst}")
    return holds


def main():
    from gateway_t_eq_u_witness import dbullet_arcs as g1
    from rho_headless_witness import dbullet_arcs as g2
    from dominated_witness import dbullet_arcs as g3
    from relay_free_witness import dbullet_arcs as g4
    from core_embedding_witness import dbullet_arcs as g5
    from v_target_internal_reachability_counterexample import construction

    specs = [
        ("t_eq_u(D10,smoke)", g1(), 7, 1, 5, set(range(1, 7))),
        ("rho_headless(D17)", g2(), 8, 1, 5, set(range(2, 8))),
        ("dominated(D18)", g3(), 11, 1, 5, set(range(2, 11))),
        ("relay_free(D19)", g4(), 14, 1, 5, set(range(2, 14))),
        ("core_embedding(D28)", g5(), 11, 1, 8, set(range(2, 11))),
        ("blocker_cex(D30)", construction()[1], 23, 1, 5, set(range(2, 14))),
    ]
    results = {}
    for (name, db, n, u, v, K_set) in specs:
        results[name] = check(name, db, n, u, v, K_set)

    print("\n===== SUMMARY (LEMMA IN red-team) =====")
    for name, ok in results.items():
        print(f"  {name}: {'HOLDS' if ok else 'COUNTEREXAMPLE CANDIDATE'}")
    # In-scope = the five non-smoke witnesses
    inscope = {k: v for k, v in results.items() if "smoke" not in k}
    if all(inscope.values()):
        print("\nLEMMA IN holds on ALL FIVE in-scope witnesses "
              "(existential over random T_in satisfied).")
    else:
        bad = [k for k, v in inscope.items() if not v]
        print(f"\nLEMMA IN FAILED (candidate in-class counterexample) on: {bad}")


if __name__ == "__main__":
    main()
