"""cut_sparing_edmonds_check.py -- A''' OBLIGATION (b) red-team via an
EDMONDS-BICONDITIONAL.

CLAIM (structural, to be killed or corroborated on the 6 witnesses):
A cut-sparing in-arborescence-side T with X_a^T = X_P that leaves >= 1
residual unit across EVERY interior cut of D[X_P] exists IFF
  (i)  every nonempty Y subseteq X_P\\{u} has |delta+_{D[X_P]}(Y)| >= 2
       (with arc multiplicity), equivalently lambda_{D[X_P]}(x,u) >= 2
       for all x in X_P\\{u}  (Menger), AND
  (ii) every vertex of V\\X_P reaches rho in D - X_P.

Backward direction = Edmonds' disjoint-branchings theorem (in-branching
form): (i) gives TWO arc-disjoint spanning in-arborescences T1,T2 of
D[X_P] rooted at u; take T = T1 u {a} u (outside in-arb from (ii)); T2
supplies the spared residual unit on every interior cut.  Forward = a
counting + the X_a^T = X_P geometry.

CITATIONS (NEEDS-VERIFICATION per ledger discipline -- not yet routed
through Crossref; do NOT cite in any draft until verified):
  J. Edmonds, "Edge-disjoint branchings", in Combinatorial Algorithms
  (R. Rustin ed.), Algorithmic Press, 1973, pp. 91-96.
  L. Lovasz, constructive proof, JCTB 1976.

This script, per witness hard gateway at a=(u,v), reuses the EXACT X_P
machinery of v_target_check.py and reports/checks:
  (1) enumerate ALL nonempty Y subseteq X_P\\{u}; report
      min |delta+_{D[X_P]}(Y)| with multiplicity; LIST any Y with value
      <= 1 (a KILL of obligation (b) at that witness);
  (2) cross-check via max-flow lambda_{D[X_P]}(x,u) for every
      x in X_P\\{u} (networkx); (1) and (2) must AGREE
      (min_Y |delta+| == min_x lambda(x,u));
  (3) check every vertex of V\\X_P reaches rho in D - X_P (BFS);
  (4) when (1)-(3) pass: CONSTRUCT two arc-disjoint spanning in-arbs
      T1,T2 of D[X_P] at u via ILP feasibility over the small arc set,
      assemble T = T1 u {a} u (outside in-arb), assert X_a^T == X_P, and
      assert >= 1 residual unit across every interior cut of D[X_P]
      (i.e. T2 crosses every nonempty Y), an end-to-end certificate of
      the backward direction on the real instance.

KILL (verdict=fail): some witness has a Y with internal out-degree <= 1,
OR an outside vertex not reaching rho in D - X_P.  Then no cut-sparing T
exists there at all (necessity), and obligation (b) as formulated is dead.
NON-KILL: min internal out-degree >= 2 + outside rho-reachability on all
six -- licenses (does NOT prove) the Edmonds route; the in-class lemma (i)
is UNIVERSAL over strictly rho-headless gateways and 6 engineered
witnesses can only kill it, never support it.
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


def compute_X_P(db, n, u, v, K_set):
    """Exactly the v_target_check.py / xp_distinct_tails_census.py X_P."""
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


def internal_mult(mult, X):
    """D[X_P] arcs with multiplicity: both endpoints in X."""
    im = Counter()
    for (x, y), m in mult.items():
        if x in X and y in X:
            im[(x, y)] += m
    return im


def out_deg_set(im, Y, X):
    """|delta+_{D[X]}(Y)| with multiplicity: arcs from Y to X\\Y."""
    s = 0
    for (x, y), m in im.items():
        if x in Y and y not in Y:
            s += m
    return s


def lambda_to_u(im, X, u):
    """min over x in X\\{u} of max-flow lambda_{D[X]}(x,u) (arc capacities
    = multiplicity).  Menger: = min over Y (x in Y, u notin Y) of out-cut."""
    G = nx.DiGraph()
    G.add_nodes_from(X)
    for (x, y), m in im.items():
        G.add_edge(x, y, capacity=m)
    best = None
    arg = None
    for x in X - {u}:
        if not G.has_node(x):
            val = 0
        else:
            try:
                val = nx.maximum_flow_value(G, x, u)
            except nx.NetworkXError:
                val = 0
        if best is None or val < best:
            best, arg = val, x
    return best, arg


def two_arc_disjoint_in_arbs(im, X, u):
    """ILP feasibility: pick T1,T2 each a spanning in-arb of D[X] rooted u,
    arc-disjoint (each labelled copy used at most once; a (tail,head) arc
    of multiplicity m offers m copies).  Returns (T1,T2) as succ-dicts or
    None.  Small arc set -- exact ILP via pulp if present, else a
    backtracking search."""
    verts = sorted(X)
    nonroot = [x for x in verts if x != u]
    # candidate arcs out of each nonroot vertex (head in X), with capacity
    cand = {x: [(y, im[(x, y)]) for y in verts
                if (x, y) in im] for x in nonroot}
    # quick infeasibility: every nonroot needs >=2 capacity out-degree to
    # supply two arc-disjoint trees (necessary local condition)
    for x in nonroot:
        if sum(m for _, m in cand[x]) < 2:
            return None

    try:
        import pulp
    except Exception:
        pulp = None

    if pulp is not None:
        prob = pulp.LpProblem("two_inarbs", pulp.LpMinimize)
        # x1[(x,y)], x2[(x,y)] in {0,1}: arc (x,y) used as tree edge of T1/T2
        x1 = {}
        x2 = {}
        arcs = list(cand_arcs(cand))
        for (x, y) in arcs:
            x1[(x, y)] = pulp.LpVariable(f"a1_{x}_{y}", cat="Binary")
            x2[(x, y)] = pulp.LpVariable(f"a2_{x}_{y}", cat="Binary")
        # each nonroot has exactly one out-arc in each tree (in-arb to u)
        for x in nonroot:
            prob += pulp.lpSum(x1[(x, y)] for (y, _) in cand[x]) == 1
            prob += pulp.lpSum(x2[(x, y)] for (y, _) in cand[x]) == 1
        # arc-disjoint with multiplicity: used copies <= capacity
        for (x, y) in arcs:
            prob += x1[(x, y)] + x2[(x, y)] <= im[(x, y)]
        prob += 0  # feasibility
        status = prob.solve(pulp.PULP_CBC_CMD(msg=0))
        if pulp.LpStatus[status] != "Optimal":
            return None
        succ1 = {x: y for (x, y) in arcs if pulp.value(x1[(x, y)]) > 0.5}
        succ2 = {x: y for (x, y) in arcs if pulp.value(x2[(x, y)]) > 0.5}
        # verify they are genuine in-arbs (no directed cycle, all reach u)
        if not (is_in_arb_local(succ1, X, u) and is_in_arb_local(succ2, X, u)):
            return None
        return succ1, succ2
    # fallback: backtracking over choices (X small)
    return backtrack_two(cand, nonroot, im, X, u)


def cand_arcs(cand):
    seen = set()
    for x, lst in cand.items():
        for (y, _) in lst:
            if (x, y) not in seen:
                seen.add((x, y))
                yield (x, y)


def is_in_arb_local(succ, X, u):
    for s in X:
        if s == u:
            continue
        seen, cur = set(), s
        while cur != u:
            if cur in seen or cur not in succ:
                return False
            seen.add(cur)
            cur = succ[cur]
    return True


def backtrack_two(cand, nonroot, im, X, u):
    # assign T1 first, then T2 with residual capacities; ensure both in-arbs
    def find_inarb(used, forbid_use):
        # used: Counter of (x,y) copies already consumed; returns succ or None
        succ = {}
        for x in nonroot:
            chosen = None
            for (y, m) in cand[x]:
                avail = im[(x, y)] - used[(x, y)]
                if avail >= 1:
                    chosen = (y, m)
                    break
            if chosen is None:
                return None
        # acyclicity not guaranteed by greedy; do a real DFS search
        return None

    # full backtracking (X small: |nonroot| <= ~12, fanout small)
    arcs_by_v = {x: [y for (y, _) in cand[x]] for x in nonroot}

    def build(used):
        # try to build ONE spanning in-arb consuming residual capacity
        result = {}

        def rec(i):
            if i == len(nonroot):
                if is_in_arb_local(result, X, u):
                    return True
                return False
            x = nonroot[i]
            for y in arcs_by_v[x]:
                if im[(x, y)] - used[(x, y)] >= 1:
                    result[x] = y
                    used[(x, y)] += 1
                    if rec(i + 1):
                        return True
                    used[(x, y)] -= 1
                    del result[x]
            return False
        if rec(0):
            return dict(result)
        return None

    used = Counter()
    t1 = build(used)
    if t1 is None:
        return None
    t2 = build(used)
    if t2 is None:
        return None
    return t1, t2


def check_witness(name, db, n, u, v, K_set):
    mult, X, P_v, J, root = compute_X_P(db, n, u, v, K_set)
    a = (u, v)
    im = internal_mult(mult, X)
    XP = X

    # (1) enumerate all nonempty Y subseteq X_P\{u}, min out-cut
    pool = sorted(XP - {u})
    min_out = None
    arg_Y = None
    bad_Ys = []
    for r in range(1, len(pool) + 1):
        for Y in itertools.combinations(pool, r):
            Ys = set(Y)
            d = out_deg_set(im, Ys, XP)
            if min_out is None or d < min_out:
                min_out, arg_Y = d, Ys
            if d <= 1:
                bad_Ys.append((sorted(Ys), d))

    # (2) max-flow cross-check lambda(x,u)
    lam, arg_x = lambda_to_u(im, XP, u)

    agree = (min_out == lam)

    # (3) outside rho-reachability in D - X_P
    outside = set(range(n)) - XP
    Gout = nx.DiGraph()
    Gout.add_nodes_from(outside)
    for (x, y), m in mult.items():
        if x in outside and y in outside:
            Gout.add_edge(x, y)
    unreached = []
    for w in outside:
        if w == root:
            continue
        if not (Gout.has_node(w) and nx.has_path(Gout, w, root)):
            unreached.append(w)

    cond_i = (min_out >= 2)
    cond_ii = (len(unreached) == 0)

    print(f"=== {name}: |X_P|={len(XP)} a={a} X_P={sorted(XP)} ===")
    print(f"  (i) min_Y |delta+_D[X_P](Y)| (mult) = {min_out} "
          f"at Y={sorted(arg_Y)}")
    print(f"      max-flow min_x lambda(x,u) = {lam} at x={arg_x} "
          f"[agree={agree}]")
    if bad_Ys:
        print(f"      *** KILL: Y with out-cut <=1: {bad_Ys[:5]} "
              f"(total {len(bad_Ys)})")
    print(f"  (ii) outside V\\X_P = {sorted(outside)}; "
          f"rho-unreachable in D-X_P = {unreached} "
          f"[cond_ii={cond_ii}]")

    constructed = None
    cut_spared = None
    if cond_i and cond_ii and agree:
        # (4) construct two arc-disjoint in-arbs of D[X_P] at u
        pair = two_arc_disjoint_in_arbs(im, XP, u)
        if pair is None:
            print("  (iv) *** Edmonds backward FAILED to construct two "
                  "arc-disjoint in-arbs despite (i) -- INCONCLUSIVE")
            constructed = False
        else:
            T1, T2 = pair
            constructed = True
            # assemble T = T1 u {a} u outside-in-arb (rooted rho)
            Tout = nx.DiGraph()
            Tout.add_nodes_from(outside)
            for (x, y), m in mult.items():
                if x in outside and y in outside:
                    Tout.add_edge(x, y)
            succ_out = {}
            # reverse BFS in-arb of outside rooted root
            dist = {root: 0}
            frontier = [root]
            while frontier:
                nxt = []
                for f in frontier:
                    for p in Tout.predecessors(f):
                        if p not in dist:
                            dist[p] = dist[f] + 1
                            succ_out[p] = f
                            nxt.append(p)
                frontier = nxt
            assert set(succ_out) == outside - {root}, "outside in-arb"
            T = dict(T1)
            T[u] = v
            T.update(succ_out)
            # X_a^T : root-avoiding subtree through a = the set of vertices
            # whose T-path to rho passes through u, i.e. tail-side of a = X_P
            Xa = subtree_through_local(T, u, root, n)
            geom_ok = (Xa == XP)
            # T2 spares >= 1 residual unit across every interior cut:
            # T2 is a spanning in-arb of D[X_P], so it crosses every
            # nonempty Y subseteq X_P\{u} at least once (every vertex of Y
            # routes to u, leaving Y).  Verify directly.
            spare_fail = []
            for r in range(1, len(pool) + 1):
                for Y in itertools.combinations(pool, r):
                    Ys = set(Y)
                    crosses = any(x in Ys and (succ2 := T2.get(x)) is not None
                                  and succ2 not in Ys for x in Ys)
                    if not crosses:
                        spare_fail.append(sorted(Ys))
            cut_spared = (len(spare_fail) == 0)
            print(f"  (iv) two arc-disjoint in-arbs T1,T2 of D[X_P] "
                  f"CONSTRUCTED; X_a^T==X_P: {geom_ok}; "
                  f"T2 spares every interior cut: {cut_spared} "
                  f"(fails={spare_fail[:3]})")
            constructed = geom_ok and cut_spared
    print()
    return dict(name=name, cond_i=cond_i, cond_ii=cond_ii, agree=agree,
                min_out=min_out, lam=lam, bad_Ys=bad_Ys,
                unreached=unreached, constructed=constructed,
                cut_spared=cut_spared)


def subtree_through_local(succ, w, root, n):
    """Set of vertices s != root whose T-path to root passes through w."""
    res = set()
    for s in range(n):
        if s == root:
            continue
        cur = s
        seen = set()
        passed = False
        while cur != root:
            if cur == w:
                passed = True
            if cur in seen or cur not in succ:
                passed = False
                break
            seen.add(cur)
            cur = succ[cur]
        if passed:
            res.add(s)
    return res


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

    results = []
    for (name, db, n, u, v, K_set) in specs:
        results.append(check_witness(name, db, n, u, v, K_set))

    print("=" * 60)
    any_kill = False
    for r in results:
        kill = bool(r["bad_Ys"]) or bool(r["unreached"])
        any_kill |= kill
        tag = "KILL" if kill else ("OK" if r["constructed"] else "INCONCLUSIVE")
        print(f"{r['name']}: cond_i(min_out={r['min_out']})={r['cond_i']} "
              f"cond_ii={r['cond_ii']} agree={r['agree']} "
              f"constructed={r['constructed']} -> {tag}")
    print("=" * 60)
    if any_kill:
        print("VERDICT: OBLIGATION (b) BICONDITIONAL NECESSITY -> KILL on "
              ">=1 witness; merged-packing route DEAD as formulated.")
        sys.exit(2)
    elif all(r["constructed"] for r in results):
        print("VERDICT: NON-KILL. min internal out-degree >=2 + outside "
              "rho-reachability on ALL six; backward Edmonds construction "
              "certified end-to-end. The in-class lemma (i) is UNIVERSAL "
              "and remains the single symbolic target (6 witnesses license, "
              "do NOT prove, it).")
        sys.exit(0)
    else:
        print("VERDICT: NO KILL but >=1 backward construction INCONCLUSIVE.")
        sys.exit(1)


if __name__ == "__main__":
    main()
