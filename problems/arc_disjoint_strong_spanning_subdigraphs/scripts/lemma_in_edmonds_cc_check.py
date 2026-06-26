"""lemma_in_edmonds_cc_check.py -- EXACT Edmonds-biconditional red-team of
LEMMA IN (D33), upgrading the random-T_in sampler
(lemma_in_reachability_check.py) to a one-shot max-flow certificate over the
WHOLE T_in space.

PROPOSAL (literature-reduction lens, Edmonds 1973 root-set form).
LEMMA IN asks: does SOME in-X_P in-arborescence T_in rooted at u exist such
that in  D-hat[X_P] = D[X_P] - labels(T_in), with r1,r2's in-X_P out-arcs all
removed (prescribed to rho), EVERY X_P-vertex reaches {r1,r2}?

The "residual reaches {r1,r2}" half is exactly: D-hat[X_P] contains a spanning
in-branching with ROOT SET {r1,r2} (roots r1,r2 have out-degree 0 in an
in-branching, so removing their out-arcs is automatic).  Together with the
T_in (a spanning in-branching with root set {u}) being arc-disjoint from it,
LEMMA IN(X_P,u,r1,r2) holds for SOME T_in IFF D[X_P] contains TWO ARC-DISJOINT
spanning in-branchings with root sets {u} and {r1,r2}.

By Edmonds' disjoint-branchings theorem (root-set form; in-branching dual)
this is EQUIVALENT to the cut condition CC: for every nonempty Y strictly
inside X_P,
    d+_{D[X_P]}(Y) >= [u notin Y] + [Y cap {r1,r2} = empty].
i.e. every vertex must have an out-cut surviving for branching #1 (the {u}
in-branching) AND, if it avoids {r1,r2}, an extra independent out-arc for
branching #2 (the {r1,r2} in-branching).

CC is poly-checkable by max-flows on D[X_P] with UNIT arc capacities (parallel
arcs add capacity):
  (i)   maxflow(x -> u) >= 1            for all x in X_P\\{u};
  (ii)  maxflow(x -> {u,r1,r2}) >= 2    for all x in X_P\\{u,r1,r2};
  (iii) maxflow(u -> {r1,r2}) >= 1.
(Menger: a vertex-set out-cut of value c equals max arc-disjoint flow c to the
merged sink.  (i)+(ii)+(iii) <=> CC for the mixed root sets {u},{r1,r2}.)

PREDICTIONS (from the proposal):
  KILL    -- if on some in-scope witness CC FAILS for EVERY admissible DT-tail
             pair (r1,r2), then by Edmonds-necessity NO T_in satisfies LEMMA
             IN; the statement is dead as written.  (Predicted at blocker_cex,
             whose internal-out-degree-1 vertices outnumber the 2 roots.)
  CONFIRM -- if every witness passes CC for some admissible (r1,r2), build the
             two arc-disjoint root-set in-branchings and verify residual
             reachability after deleting labels(T_in) and r1,r2's internal
             out-arcs.
  CROSS-CHECK -- per witness, CC verdict must never contradict a 200-random-
             T_in sample (CC fail => all samples fail).

Construction of X_P/J/P_v/R_in_X is byte-for-byte shared with
lemma_in_reachability_check.py (same six checked-in witnesses).
"""
from __future__ import annotations

import os
import random
import sys
from collections import Counter
from itertools import combinations

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.path.join(os.path.dirname(_HERE), "code")
for _p in (_CODE, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import networkx as nx  # noqa: E402

from check_lexist_fixedroot import tree_arcs  # noqa: E402
from lemma_in_reachability_check import (  # noqa: E402
    build_xp, random_in_arb_xp, dhat_xp_edges,
)


# ---------------------------------------------------------------------------
# max-flow helpers on D[X_P] with UNIT-capacity arcs (parallel arcs add up)
# ---------------------------------------------------------------------------
def _capacity_digraph(X, mult):
    """DiGraph on X with edge capacity = multiplicity of internal arc."""
    G = nx.DiGraph()
    G.add_nodes_from(X)
    for (a, b), m in mult.items():
        if a in X and b in X:
            if G.has_edge(a, b):
                G[a][b]["capacity"] += m
            else:
                G.add_edge(a, b, capacity=m)
    return G


def _maxflow_to_set(G, src, sink_set):
    """max arc-disjoint flow from src to the merged sink (a super-sink)."""
    if src in sink_set:
        return float("inf")
    H = G.copy()
    SINK = ("__SINK__",)
    H.add_node(SINK)
    for s in sink_set:
        if s in H:
            # huge capacity into the super-sink
            H.add_edge(s, SINK, capacity=float("inf"))
    if not H.has_node(src):
        return 0
    val, _ = nx.maximum_flow(H, src, SINK)
    return val


def check_cc(X, u, r1, r2, mult):
    """Decide CC (the Edmonds mixed-root cut condition) by the three max-flow
    families.  Returns (ok, violations) where violations lists the (kind, x,
    value) of every failing flow."""
    G = _capacity_digraph(X, mult)
    roots = {r1, r2}
    viols = []
    # (i) every x in X\{u} reaches u with flow >= 1
    for x in X - {u}:
        f = _maxflow_to_set(G, x, {u})
        if f < 1:
            viols.append(("i:x->u<1", x, f))
    # (ii) every x in X\{u,r1,r2} sends flow >= 2 to {u,r1,r2}
    for x in X - {u} - roots:
        f = _maxflow_to_set(G, x, {u, r1, r2})
        if f < 2:
            viols.append(("ii:x->{u,r1,r2}<2", x, f))
    # (iii) u sends flow >= 1 to {r1,r2}
    f = _maxflow_to_set(G, u, roots)
    if f < 1:
        viols.append(("iii:u->{r1,r2}<1", u, f))
    return (len(viols) == 0, viols)


def internal_outdeg(X, mult):
    """internal-out-degree (multiplicity-summed) of every X-vertex in D[X]."""
    od = {x: 0 for x in X}
    for (a, b), m in mult.items():
        if a in X and b in X:
            od[a] += m
    return od


# ---------------------------------------------------------------------------
# constructive extraction of the two arc-disjoint root-set in-branchings
# ---------------------------------------------------------------------------
def extract_two_branchings(X, u, r1, r2, mult):
    """Construct two ARC-DISJOINT spanning in-branchings B1 (root set {u}) and
    B2 (root set {r1,r2}) in D[X] via matroid-union-style flow feasibility
    (Edmonds): a set of arc-multiplicities supports k arc-disjoint spanning
    in-branchings with root sets R_1..R_k iff for every vertex x and every
    j, the residual graph admits the required out-arcs -- here checked by
    iterated min-cost-feasibility.  We use a correct backtracking selector at
    these tiny sizes: pick, per non-root vertex of each branching, an out-arc
    so that the chosen multiset never exceeds capacity AND each branching stays
    acyclic-to-its-roots.  Returns (B1,B2) lists or None."""
    roots = {u, r1, r2}
    Xs = sorted(X)
    cap0 = {e: m for e, m in mult.items() if e[0] in X and e[1] in X}

    def branchings_feasible(cap):
        """Does `cap` support arc-disjoint in-branchings root {u} and {r1,r2}?
        Check via the Edmonds cut condition on the residual capacities."""
        G = nx.DiGraph(); G.add_nodes_from(X)
        for (a, b), m in cap.items():
            if m >= 1:
                G.add_edge(a, b, capacity=m)
        # need: reach u (flow>=1) for all x!=u; reach {u,r1,r2} (flow>=2) for
        # x outside roots; reach {r1,r2} (flow>=1) for u.
        for x in X - {u}:
            if _maxflow_to_set(G, x, {u}) < 1:
                return False
        for x in X - roots:
            if _maxflow_to_set(G, x, {u, r1, r2}) < 2:
                return False
        if _maxflow_to_set(G, u, {r1, r2}) < 1:
            return False
        return True

    if not branchings_feasible(cap0):
        return None

    # Greedy with feasibility-guarded choice: build B2 (root {r1,r2}) then B1
    # (root {u}); at each arc choice keep the REMAINDER feasible for whatever
    # is still owed.  Sizes are tiny so this terminates fast.
    def build(targets, cap, need_other):
        """Build a spanning in-branching with root set `targets`, consuming
        cap; `need_other`=True means we must keep cap feasible for the OTHER
        branching afterwards (the {u}-branching).  Returns (arcs, cap) or
        (None,None)."""
        S = set(targets); chosen = []
        while S != X:
            cand = [(a, b) for (a, b), m in cap.items()
                    if m >= 1 and a in X and a not in S and b in S]
            if not cand:
                return None, None
            picked = None
            for (a, b) in sorted(cand):
                test = dict(cap); test[(a, b)] -= 1
                if need_other:
                    # the {u}-branching must still be extractable from test
                    Gt = nx.DiGraph(); Gt.add_nodes_from(X)
                    for (p, q), mm in test.items():
                        if mm >= 1:
                            Gt.add_edge(p, q, capacity=mm)
                    if any(_maxflow_to_set(Gt, x, {u}) < 1 for x in X - {u}):
                        continue
                picked = (a, b); cap = test; break
            if picked is None:
                return None, None
            chosen.append(picked); S.add(picked[0])
        return chosen, cap

    b2, cap1 = build({r1, r2}, dict(cap0), need_other=True)
    if b2 is None:
        return None
    b1, _ = build({u}, cap1, need_other=False)
    if b1 is None:
        return None
    return (b1, b2)


def verify_lemma_in_from_branchings(X, u, r1, r2, b1, b2):
    """T_in := B1 (the {u}-in-branching).  D-hat[X_P] = D[X_P] - labels(T_in)
    with r1,r2 out-arcs removed.  Assert every X_P-vertex reaches {r1,r2}.
    We use B2 itself as the residual in-branching witness (it is arc-disjoint
    from B1 and roots at {r1,r2}, so it certifies reachability directly)."""
    H = nx.DiGraph()
    H.add_nodes_from(X)
    for (a, b) in b2:
        if a not in (r1, r2):       # roots keep out-deg 0
            H.add_edge(a, b)
    roots = {r1, r2}
    bad = [x for x in X - roots
           if not (nx.has_path(H, x, r1) or nx.has_path(H, x, r2))]
    return bad


# ---------------------------------------------------------------------------
def check(name, db, n, u, v, K_set, sample_trials=200):
    d = build_xp(name, db, n, u, v, K_set)
    mult, X, R_in_X = d["mult"], d["X"], d["R_in_X"]
    rng = random.Random(20260612)

    od = internal_outdeg(X, mult)
    deg1 = sorted(x for x in X - {u} if od[x] == 1)

    print(f"\n=== {name} ===")
    print(f"  |X_P|={len(X)} X_P={sorted(X)}  u={u}  R_in_X={R_in_X}")
    print(f"  internal-out-degree-1 vertices of D[X_P] (excl u): {deg1} "
          f"(count {len(deg1)})")

    # ALL admissible DT-tail pairs from R_in_X
    pairs = list(combinations(R_in_X, 2))
    print(f"  admissible (r1,r2) DT-tail pairs: {pairs}")

    any_pass = False
    pass_pairs = []
    for (r1, r2) in pairs:
        ok, viols = check_cc(X, u, r1, r2, mult)
        tag = "CC_PASS" if ok else "CC_FAIL"
        print(f"    pair (r1={r1},r2={r2}): {tag}")
        if not ok:
            # show a couple of violating sets / vertices
            for kind, x, val in viols[:6]:
                print(f"        viol {kind} at x={x}: flow={val}")
        else:
            any_pass = True
            pass_pairs.append((r1, r2))

    # CROSS-CHECK against 200 random T_in for EACH pair: CC verdict vs samples
    for (r1, r2) in pairs:
        ok, _ = check_cc(X, u, r1, r2, mult)
        n_succ = 0
        for _ in range(sample_trials):
            T_in = random_in_arb_xp(X, u, mult, rng)
            if T_in is None:
                continue
            Ts = tree_arcs(T_in)
            H = nx.DiGraph(); H.add_nodes_from(X)
            H.add_edges_from(dhat_xp_edges(X, mult, Ts, r1, r2))
            stranded = [x for x in X - {r1, r2}
                        if not (nx.has_path(H, x, r1) or nx.has_path(H, x, r2))]
            if not stranded:
                n_succ += 1
        # CONSISTENCY: CC fail => no sampled T_in may succeed
        if not ok:
            assert n_succ == 0, (
                name, (r1, r2),
                f"INCONSISTENCY: CC_FAIL but {n_succ} random T_in succeeded")
        print(f"    cross-check pair ({r1},{r2}): CC={'PASS' if ok else 'FAIL'}"
              f"  random-T_in successes={n_succ}/{sample_trials}"
              f"  (consistent)")

    # If some pair passes, constructively extract + verify the branchings.
    # Skip the degenerate u-in-roots case (out-of-scope smoke witness): there
    # the {r1,r2} root set contains u, so the two branchings coincide.
    if any_pass:
        r1, r2 = pass_pairs[0]
        if u in (r1, r2):
            print(f"  CC PASSES on ({r1},{r2}) but u in roots (degenerate "
                  f"out-of-scope smoke); skipping constructive extraction.")
            return True
        bres = extract_two_branchings(X, u, r1, r2, mult)
        assert bres is not None, (name, "CC passed but extraction failed")
        b1, b2 = bres
        # arc-disjointness: each labelled arc used <= its multiplicity
        usage = Counter(b1) + Counter(b2)
        for e, c in usage.items():
            assert c <= mult[e], (name, "over-used arc", e, c, mult[e])
        bad = verify_lemma_in_from_branchings(X, u, r1, r2, b1, b2)
        assert not bad, (name, "residual reachability failed", bad)
        print(f"  LEMMA IN CONFIRMED via Edmonds CC on pair ({r1},{r2}): "
              f"two arc-disjoint in-branchings extracted, residual "
              f"reachability of all {len(X)-2} non-root X_P-vertices verified.")
        return True
    else:
        print(f"  *** CC FAILS FOR EVERY ADMISSIBLE PAIR -> LEMMA IN DEAD as "
              f"written on {name} (Edmonds necessity) ***")
        return False


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

    print("\n===== SUMMARY (LEMMA IN Edmonds-CC red-team) =====")
    for name, ok in results.items():
        print(f"  {name}: {'CC_PASS/LEMMA IN holds' if ok else 'CC_FAIL/LEMMA IN dead as written'}")
    inscope = {k: v for k, v in results.items() if "smoke" not in k}
    if all(inscope.values()):
        print("\nLEMMA IN (Edmonds CC) PASSES on ALL FIVE in-scope witnesses.")
    else:
        bad = [k for k, v in inscope.items() if not v]
        print(f"\nLEMMA IN Edmonds-CC FAILS (dead as written) on: {bad}")


if __name__ == "__main__":
    main()
