"""Robustness re-check of the UMCO verdict for AC_7[C3] (order 21).

The proposal allows the hitting transversal to be "up to the automorphism
orbit". AC_7[C3] is vertex-transitive (rotation on the AC_7 factor + C3
rotation gives a transitive automorphism group on the 21 vertices? actually
the AC_7 rotation is transitive on the 7 outer blocks; within-block C3 is
NOT vertex-transitive as a whole, but each outer block-rotation maps blocks
to blocks). We test the strongest reasonable form of UMCO:

  (a) Is there a SINGLE vertex hitting every collected max clique? (no => the
      basic UMCO already fails)
  (b) Even allowing a whole automorphism-ORBIT as the transversal: is there a
      vertex orbit O such that every max clique meets O AND |O| is a proper
      transversal (so deleting one orbit rep is what does the criticality
      work)? For a vertex-transitive object the single orbit = all 21 vertices,
      which trivially hits everything but is NOT a "unique max-clique orbit"
      (it carries no localization). UMCO is meaningful only if a PROPER subset
      (ideally one vertex up to symmetry) hits all max cliques.

We compute, over a LARGE sample of optimal orders, the minimum hitting-set
size for the collected max cliques, and the per-vertex coverage fraction.
If the min hitting set is large (>> 1) the "unique max-clique orbit" structure
that UMCO needs is absent.
"""
import sys, os, json, time, itertools, random
sys.path.insert(0, os.path.dirname(__file__))
import core
import networkx as nx
from search_4critical_circulant import circ_arcs
from ground_lex_compose_c3 import ac_gen, c3, lex_compose


def collect_maxcliques(n, arcs, ov, tries, seed=1):
    rng = random.Random(seed)
    beats = core.beats_matrix(n, arcs)
    mc = set()
    n_opt = 0
    orders = [list(range(n))]
    for _ in range(tries):
        o = list(range(n)); rng.shuffle(o); orders.append(o)
    for r in range(n):
        orders.append([(i + r) % n for i in range(n)])
    for order in orders:
        g = nx.Graph(); g.add_nodes_from(range(n))
        for i in range(n):
            a = order[i]
            for j in range(i + 1, n):
                b = order[j]
                if beats[b][a]:
                    g.add_edge(a, b)
        if core.clique_number(g) == ov:
            n_opt += 1
            for c in nx.find_cliques(g):
                if len(c) == ov:
                    mc.add(frozenset(c))
    return list(mc), n_opt


def greedy_hitting_set(cliques, n):
    """Greedy upper bound on min hitting set size."""
    remaining = [set(c) for c in cliques]
    chosen = []
    while remaining:
        cnt = [0] * n
        for c in remaining:
            for v in c:
                cnt[v] += 1
        best_v = max(range(n), key=lambda v: cnt[v])
        if cnt[best_v] == 0:
            break
        chosen.append(best_v)
        remaining = [c for c in remaining if best_v not in c]
    return chosen


def main():
    nC, aC = c3()
    nAC7, aAC7 = 7, circ_arcs(7, ac_gen(7))
    N, A = lex_compose(nAC7, aAC7, nC, aC)
    assert core.is_tournament(N, A)
    ov = 4
    t0 = time.time()
    mc, n_opt = collect_maxcliques(N, A, ov, tries=12000, seed=42)
    # common single hitter?
    common = set(mc[0])
    for c in mc[1:]:
        common &= set(c)
    # min hitting set (greedy upper bound)
    hs = greedy_hitting_set(mc, N)
    # per-vertex coverage
    cov = [0] * N
    for c in mc:
        for v in c:
            cov[v] += 1
    out = {
        "object": "AC_7[C3]", "order": N, "omega_vec": ov,
        "n_optimal_orders_sampled": n_opt,
        "n_distinct_max_cliques": len(mc),
        "common_single_hitter": sorted(common),
        "UMCO_single_hitter": bool(common),
        "greedy_hitting_set_size": len(hs),
        "greedy_hitting_set": sorted(hs),
        "max_vertex_coverage_fraction": round(max(cov) / len(mc), 4) if mc else None,
        "min_vertex_coverage_fraction": round(min(cov) / len(mc), 4) if mc else None,
        "elapsed_s": round(time.time() - t0, 2),
    }
    print(json.dumps(out, indent=2), flush=True)
    dp = os.path.join(os.path.dirname(__file__), "..", "data", "umco_robustness.json")
    with open(os.path.abspath(dp), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
