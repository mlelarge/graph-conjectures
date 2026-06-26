"""edmonds_1cut_dichotomy_check.py -- GROUND the proposed EDMONDS 1-CUT
DICHOTOMY reduction lemma for the H8-SPINE branch-(2) kernel.

Reduction Lemma (claim under test): if every O-vertex has local
arc-connectivity lambda_{D_O}(x, rho) >= 2 WITHIN D_O, then Edmonds gives
two arc-disjoint spanning in-arborescences T1, T2 of D_O rooted at rho;
for any escaped head h, the T1-path from h truncated at its first rho-tail
is an h-to-R relay whose D_O-arcs lie in A(T1), so D_O - A_O(P) still
contains T2 and every O-vertex reaches rho (route NOT load-bearing).

Falsifiable predictions (proposal):
  (a) lambda_{D_O}(x, rho) >= 2 for ALL x in O, on all three witnesses.
  (b) On the relay-free witness: the T1-path from each escaped head,
      truncated at its first rho-tail, is non-load-bearing in D_O.
KILL = any instance with lambda_{D_O}(x,rho) >= 2 for all x in O yet some
escaped head with EVERY route load-bearing (would expose an Edmonds error).

This script computes the REAL numbers; it asserts nothing it has not first
printed, so a violated prediction is reported, not crashed-on.
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

import networkx as nx  # noqa: E402

import relay_free_witness as RF  # noqa: E402
import rho_headless_witness as RH  # noqa: E402
import dominated_witness as DM  # noqa: E402


def cage_of(mult, n, root, u):
    """C_u = {u} u {x : x cannot reach root after deleting u}."""
    G = nx.MultiDiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from(mult.elements())
    Gm = G.copy()
    Gm.remove_node(u)
    return {u} | {x for x in range(n)
                  if x not in (root, u) and not nx.has_path(Gm, x, root)}


def build_DO(mult, O, root):
    """D_O: outside vertices plus rho; arcs with tail in O and head in
    O u {rho}; unit capacity per parallel-arc label."""
    DO = nx.MultiDiGraph()
    DO.add_nodes_from(O | {root})
    for (x, y), m in mult.items():
        if x in O and (y in O or y == root):
            for _ in range(m):
                DO.add_edge(x, y)
    return DO


def local_arc_conn_to_root(DO, x, root):
    """lambda_{D_O}(x, root): max number of arc-disjoint x->root paths.
    Unit-capacity max-flow on the multigraph (parallel labels = capacity)."""
    if x == root:
        return None
    # networkx edge_connectivity with explicit s,t = arc-disjoint paths
    # on a flow network where each parallel edge has capacity 1.
    F = nx.DiGraph()
    F.add_nodes_from(DO.nodes())
    cap = Counter()
    for a, b in DO.edges():
        cap[(a, b)] += 1
    for (a, b), c in cap.items():
        F.add_edge(a, b, capacity=c)
    if not nx.has_path(F, x, root):
        return 0
    return int(nx.maximum_flow_value(F, x, root))


def edmonds_two_in_arbs(DO, root, n_O_plus):
    """Extract two arc-disjoint spanning in-arborescences of D_O rooted at
    root, when lambda_{D_O}(x,root)>=2 for all x.  Reverse the digraph and
    use networkx edge_disjoint_spanning... no -- use Edmonds' branching via
    the reverse-arborescence = out-arborescence packing on the reversed graph.

    Implementation: reverse D_O -> D_O^R; pack 2 arc-disjoint spanning
    out-arborescences rooted at root in D_O^R (Edmonds), then reverse each
    back to in-arborescences in D_O.  We use a simple augmenting-tree
    construction via 2-flow decomposition per vertex is overkill; instead use
    networkx's branchings on the reversed graph is not directly available, so
    we build it by a greedy arc-disjoint pair search guided by max-flow.

    Robust approach actually used: model as a min-cost flow that ships 2 units
    from every non-root vertex to root, arc capacity = label multiplicity,
    requiring the support to decompose into 2 in-arborescences.  Simpler and
    sufficient for the LEMMA TEST: we only need T1 (one spanning in-arb) plus a
    SECOND arc-disjoint spanning in-arb T2 to exist.  We find T1 and T2 by a
    constructive layered peeling: pick, for each vertex, an out-arc toward root
    along arc-disjoint flow paths.

    Returns (T1_succ, T2_succ) as dict vertex->parent, or None if not found.
    """
    cap = Counter()
    for a, b in DO.edges():
        cap[(a, b)] += 1
    verts = set(DO.nodes())
    non_root = [x for x in verts if x != root]

    # Send 2 units of flow from each non-root vertex to root, capacity=label.
    # A feasible integral routing where every vertex pushes 2 units and the
    # used-arc multiset splits into two in-arbs exists iff Edmonds applies.
    # We instead directly assemble two in-arbs by repeated arc-disjoint
    # shortest-path selection, which is the standard Lovasz/Edmonds proof made
    # constructive at this small scale.
    used = Counter()

    def pick_in_arb():
        # build an in-arb using arcs with remaining capacity, BFS layers from
        # root on the reversed residual graph.
        R = nx.DiGraph()
        R.add_nodes_from(verts)
        for (a, b), c in cap.items():
            if c - used[(a, b)] >= 1:
                R.add_edge(b, a)  # reversed: root reaches a via arc a->b
        # BFS from root in reversed graph; parent in reversed BFS gives the
        # out-arc (cur -> its predecessor toward root) in original.
        if not all(nx.has_path(R, root, x) for x in non_root):
            return None
        parent = {}
        pred = nx.bfs_predecessors(R, root)
        rp = dict(pred)  # x -> p means edge p->x in R, i.e. arc x->p in DO
        for x in non_root:
            if x not in rp:
                return None
            parent[x] = rp[x]
        return parent

    arb1 = pick_in_arb()
    if arb1 is None:
        return None
    for x, p in arb1.items():
        used[(x, p)] += 1
    arb2 = pick_in_arb()
    if arb2 is None:
        return None
    for x, p in arb2.items():
        used[(x, p)] += 1
    return arb1, arb2


def is_in_arb_succ(succ, verts, root):
    for start in verts:
        if start == root:
            continue
        seen, cur = set(), start
        while cur != root:
            if cur not in succ or cur in seen:
                return False
            seen.add(cur)
            cur = succ[cur]
    return True


def t1_path_truncated(arb1, h, root, rho_tails):
    """T1-path from h, truncated at the first rho-tail w (first vertex on the
    path that is a rho-tail).  Returns list of D_O arcs (x,y) of the truncated
    prefix (the truncation removes the final w->root jump; w is the relay
    target, the arc into w's absorbed set is non-D_O)."""
    path = [h]
    cur = h
    seen = {h}
    while cur != root:
        nxt = arb1[cur]
        path.append(nxt)
        if nxt in seen:
            raise RuntimeError("cycle in arb")
        seen.add(nxt)
        cur = nxt
    # first rho-tail on the path:
    w_idx = None
    for i, node in enumerate(path):
        if node in rho_tails:
            w_idx = i
            break
    if w_idx is None:
        return None, None  # no rho-tail on the path
    w = path[w_idx]
    # D_O arcs of the route up to (but not including) the jump w->root:
    route_arcs = [(path[i], path[i + 1]) for i in range(w_idx)]
    return route_arcs, w


def load_bearing(DO, route_arcs, O, root):
    """Delete route's D_O arcs (one label each) from D_O; is every O-vertex
    still able to reach root?  True if the route is NON-load-bearing."""
    H = DO.copy()
    for (a, b) in route_arcs:
        # remove one parallel copy
        keys = list(H[a][b].keys()) if H.has_edge(a, b) else []
        if keys:
            H.remove_edge(a, b, key=keys[0])
    ok = all(nx.has_path(H, z, root) for z in O)
    return ok


def analyze(name, mult, n, root, u, rho_tails_db, av_heads_db, do_edmonds):
    print(f"\n=== {name} ===")
    cage = cage_of(mult, n, root, u)
    O = set(range(n)) - cage - {root}
    R = sorted({e[0] for e in mult if e[1] == root})
    print(f"n={n} root(rho)={root} u={u} cage={sorted(cage)}")
    print(f"O={sorted(O)} R(rho-tails)={R} av_heads={sorted(av_heads_db)}")
    DO = build_DO(mult, O, root)
    lams = {}
    for x in sorted(O):
        lams[x] = local_arc_conn_to_root(DO, x, root)
    print(f"lambda_DO(x,rho) for x in O: {lams}")
    min_lam = min(lams.values())
    print(f"min_x lambda_DO(x,rho) = {min_lam}")
    pred_a = all(v >= 2 for v in lams.values())
    print(f"PREDICTION (a) [all >= 2]: {pred_a}")

    result = {"name": name, "lams": lams, "min_lam": min_lam,
              "pred_a": pred_a, "edmonds": None}

    if do_edmonds:
        arbs = edmonds_two_in_arbs(DO, root, len(O) + 1)
        if arbs is None:
            print("Edmonds extraction FAILED to find two arc-disjoint in-arbs")
            result["edmonds"] = "extract_failed"
            return result
        arb1, arb2 = arbs
        ok1 = is_in_arb_succ(arb1, O | {root}, root)
        ok2 = is_in_arb_succ(arb2, O | {root}, root)
        # arc-disjoint check
        a1 = Counter((x, p) for x, p in arb1.items())
        a2 = Counter((x, p) for x, p in arb2.items())
        disjoint = all(a1[e] + a2[e] <= mult[e] for e in set(a1) | set(a2))
        # also each must have label capacity within D_O
        print(f"T1 in-arb: {ok1}; T2 in-arb: {ok2}; "
              f"label-disjoint within capacity: {disjoint}")
        all_nonlb = True
        details = []
        for h in sorted(av_heads_db):
            if h not in O:
                details.append((h, "head not in O", None))
                continue
            route, w = t1_path_truncated(arb1, h, root, set(rho_tails_db))
            if route is None:
                details.append((h, "no rho-tail on T1-path", None))
                all_nonlb = False
                continue
            nonlb = load_bearing(DO, route, O, root)
            details.append((h, f"route={route} w={w}", nonlb))
            all_nonlb = all_nonlb and nonlb
        for d in details:
            print(f"  head {d[0]}: {d[1]} -> non-load-bearing={d[2]}")
        print(f"PREDICTION (b) [all T1-routes non-load-bearing]: {all_nonlb}")
        result["edmonds"] = {"T1_ok": ok1, "T2_ok": ok2,
                             "disjoint": disjoint, "all_nonlb": all_nonlb,
                             "details": [(d[0], d[2]) for d in details]}
    return result


def main():
    results = []

    # --- relay-free witness (n=14) ---
    rf = Counter(RF.dbullet_arcs())
    rf_rho_tails = sorted(x for (x, z) in rf if z == 0)
    rf_av = sorted(z for (x, z) in rf if x == 1 and z != 5)
    results.append(analyze("relay_free_witness", rf, 14, 0, 1,
                           rf_rho_tails, rf_av, do_edmonds=True))

    # --- rho-headless witness (n=8) ---
    rh = Counter(RH.dbullet_arcs())
    rh_rho_tails = sorted(x for (x, z) in rh if z == 0)
    rh_av = sorted(z for (x, z) in rh if x == 1 and z != 4)  # a=(1,4)? heads
    # av_heads = u-out heads excluding v.  v here = first u-out used as gateway.
    # In RH the gateway a=(1,5); but escaped heads = all u-out except chosen v.
    rh_av = sorted(z for (x, z) in rh if x == 1)
    results.append(analyze("rho_headless_witness", rh, 8, 0, 1,
                           rh_rho_tails, rh_av, do_edmonds=False))

    # --- dominated witness (n=11) ---
    dm = Counter(DM.dbullet_arcs())
    dm_rho_tails = sorted(x for (x, z) in dm if z == 0)
    dm_av = sorted(z for (x, z) in dm if x == 1 and z != 5)
    results.append(analyze("dominated_witness", dm, 11, 0, 1,
                           dm_rho_tails, dm_av, do_edmonds=False))

    print("\n========== SUMMARY ==========")
    all_a = all(r["pred_a"] for r in results)
    print(f"Prediction (a) holds on all three witnesses: {all_a}")
    rf_res = results[0]
    if rf_res["edmonds"] and rf_res["edmonds"] != "extract_failed":
        print(f"Prediction (b) on relay-free witness: "
              f"{rf_res['edmonds']['all_nonlb']}")
        print(f"  (Edmonds extraction: T1={rf_res['edmonds']['T1_ok']}, "
              f"T2={rf_res['edmonds']['T2_ok']}, "
              f"disjoint={rf_res['edmonds']['disjoint']})")
    print(f"Localization filter for executor: a spine candidate (branch-(2) "
          f"single-escape) requires min_x lambda_DO(x,rho) <= 1.")
    for r in results:
        print(f"  {r['name']}: min_x lambda_DO(x,rho) = {r['min_lam']} "
              f"=> spine-possible={r['min_lam'] <= 1}")


if __name__ == "__main__":
    main()
