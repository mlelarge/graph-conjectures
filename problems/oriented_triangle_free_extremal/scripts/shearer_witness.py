"""Ground-plan for the literature-reduction SHEARER proposal.

Reduce the a_vec UPPER bound to Shearer's triangle-free independence theorem
applied to the ACYCLIC WITNESS SET's induced subgraph G[X*] of the EXTREMAL
(min-over-orientations) oriented triangle-free graph.

Chain: a_vec = |X*|; G[X*] triangle-free with induced avg degree d*;
Shearer => alpha(G[X*]) >= |X*|*(d* ln d* - d* + 1)/(d*-1)^2 ~ |X*| ln d*/d*;
trivially alpha(G[X*]) <= alpha(G). => a_vec <= alpha(G)*d*/ln d* (approx).
Closes Conjecture 3 IFF d* = O(1) on the EXTREMAL graph.

CONFIRM: (i) Shearer inequality holds at every n (must, it is a theorem), AND
(ii) d* stays bounded / O(1), NOT tracking log n -- d*/log n DECLINES while d*
itself roughly flat.
KILL: d* GROWS with n (d*/sqrt(log n) flat or rising) -- reduction inherits the
sqrt(log n) gap.

extremal-oracle note: exact `extremal <n>` (full enum of all triangle-free
graphs x all orientations) is infeasible for n>=18; per ground_plan we fall
back to the MIN over many uniform random orientations of the triangle-free
process graph at density c/sqrt(n), c in {1,1.5,2,2.5}, EXACTLY certified by
core.acyclic_number, as the best available proxy for the extremal G.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from lit_reduction_test import triangle_free_process, random_orientation
from lit_reduction_degeneracy import acyclic_number_witness, avg_degree_in_set

import networkx as nx


def independence_number(n, edges):
    """Exact alpha of an undirected simple graph (small n): max independent set
    = max clique of the complement, via networkx."""
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    comp = nx.complement(g)
    return max((len(c) for c in nx.find_cliques(comp)), default=0)


def induced_subgraph_edges(edges, S):
    Sset = set(S)
    relabel = {v: i for i, v in enumerate(sorted(Sset))}
    sub = [(relabel[u], relabel[v]) for (u, v) in edges
           if u in Sset and v in Sset]
    return len(Sset), sub


def shearer_lower(size, d):
    """Shearer 1983 triangle-free independence bound:
       alpha(H) >= |V(H)| * (d ln d - d + 1)/(d-1)^2
    for average degree d (d>1). Handle d->1 limit (-> |V|/2... actually ->
    |V| as d->1 by L'Hopital? the standard form is for d>=1; guard small d)."""
    if size == 0:
        return 0.0
    if d <= 1e-9:
        return float(size)              # no edges -> whole set independent
    if abs(d - 1.0) < 1e-6:
        # limit of f(d)=(d ln d - d + 1)/(d-1)^2 as d->1 is 1/2
        return 0.5 * size
    f = (d * math.log(d) - d + 1.0) / (d - 1.0) ** 2
    return size * f


def main():
    ns = [18, 20, 22, 24, 26]
    cs = [1.0, 1.5, 2.0, 2.5]
    n_orient = 30          # random orientations per (n,c) -> proxy for extremal
    rows = []

    for n in ns:
        best = None  # (a, S, edges)
        for c in cs:
            p = c / math.sqrt(n)
            m_cap = int(p * n * (n - 1) / 2)
            # try several process-graph realizations too
            for gseed in range(4):
                n2, edges = triangle_free_process(
                    n, m_cap, seed=1000 * int(c * 10) + gseed + n)
                assert core.is_triangle_free(n2, edges)
                for oseed in range(n_orient):
                    arcs = random_orientation(edges, seed=7 * oseed + 3 + gseed)
                    assert core.is_oriented(arcs)
                    a, S = acyclic_number_witness(n2, arcs)
                    # certify witness acyclic
                    sub_arcs = [(u, v) for (u, v) in arcs
                                if u in set(S) and v in set(S)]
                    assert core.is_acyclic(n2, sub_arcs), "witness not acyclic"
                    if best is None or a < best[0]:
                        best = (a, S, edges)
        a, S, edges = best
        # G[X*]
        szX, subX = induced_subgraph_edges(edges, S)
        eX = len(subX)
        d_star = 2.0 * eX / szX if szX else 0.0
        alpha_GX = independence_number(szX, subX)
        # alpha(G) on the WHOLE underlying graph
        alpha_G = independence_number(n, edges)
        shearer_lhs = shearer_lower(szX, d_star)
        logn = math.log(n)
        sqrt_logn = math.sqrt(logn)
        rows.append({
            "n": n, "a": a, "X": szX, "eX": eX, "d_star": d_star,
            "alpha_GX": alpha_GX, "alpha_G": alpha_G,
            "shearer_lhs": shearer_lhs,
            "d_over_logn": d_star / logn,
            "d_over_sqrt_logn": d_star / sqrt_logn,
        })
        print(f"n={n:>3} a*={a:>3} |X*|={szX:>3} e(G[X*])={eX:>3} "
              f"d*={d_star:.4f} alpha(G[X*])={alpha_GX:>2} alpha(G)={alpha_G:>2} "
              f"Shearer_LHS={shearer_lhs:.3f} d*/logn={d_star/logn:.4f} "
              f"d*/sqrt(logn)={d_star/sqrt_logn:.4f}", flush=True)

    print("\n=== SHEARER AUDIT (theorem, MUST hold) ===", flush=True)
    all_ok = True
    for r in rows:
        ok1 = r["shearer_lhs"] <= r["alpha_GX"] + 1e-6
        ok2 = r["alpha_GX"] <= r["alpha_G"] + 1e-9
        ok = ok1 and ok2
        all_ok = all_ok and ok
        print(f"n={r['n']:>3}: Shearer_LHS={r['shearer_lhs']:.3f} <= "
              f"alpha(G[X*])={r['alpha_GX']} ? {ok1} ; "
              f"alpha(G[X*])={r['alpha_GX']} <= alpha(G)={r['alpha_G']} ? {ok2}",
              flush=True)
    print(f"Shearer chain holds at every n? {all_ok} "
          f"(a violation would mean mis-measured witness/d*)", flush=True)

    print("\n=== d* TREND (the discriminator) ===", flush=True)
    print(f"{'n':>4} {'d*':>8} {'d*/logn':>9} {'d*/sqrt(logn)':>14}", flush=True)
    ds = [r["d_star"] for r in rows]
    r_logn = [r["d_over_logn"] for r in rows]
    r_sqrt = [r["d_over_sqrt_logn"] for r in rows]
    for r in rows:
        print(f"{r['n']:>4} {r['d_star']:>8.4f} {r['d_over_logn']:>9.4f} "
              f"{r['d_over_sqrt_logn']:>14.4f}", flush=True)

    def flatness(v):
        m = sum(v) / len(v)
        return (max(v) - min(v)) / m if m else 0.0, m

    f_logn, m_logn = flatness(r_logn)
    f_sqrt, m_sqrt = flatness(r_sqrt)
    d_growing = ds[-1] > ds[0] + 1e-9
    d_logn_declining = all(r_logn[i] >= r_logn[i + 1] - 1e-9
                           for i in range(len(r_logn) - 1))
    print(f"\nd* values: {[f'{x:.3f}' for x in ds]}  "
          f"(grows over n? {d_growing})", flush=True)
    print(f"d*/logn:       mean={m_logn:.4f} range/mean={f_logn:.4f} "
          f"declining? {d_logn_declining}", flush=True)
    print(f"d*/sqrt(logn): mean={m_sqrt:.4f} range/mean={f_sqrt:.4f}", flush=True)

    print("\n=== DECISION ===", flush=True)
    print("CONFIRM (promotable): d* roughly flat (O(1)) AND d*/logn declining "
          "=> Conjecture 3 reduces to Shearer.", flush=True)
    print("KILL: d* grows with n (mirrors G12 random d*=3.47->5.69) => the "
          "reduction inherits the sqrt(log n) gap.", flush=True)
    if (not d_growing) and d_logn_declining:
        print("VERDICT-SIGNAL: CONFIRM", flush=True)
    elif d_growing:
        print("VERDICT-SIGNAL: KILL (d* grows on the extremal-proxy graph)",
              flush=True)
    else:
        print("VERDICT-SIGNAL: AMBIGUOUS", flush=True)


if __name__ == "__main__":
    main()
