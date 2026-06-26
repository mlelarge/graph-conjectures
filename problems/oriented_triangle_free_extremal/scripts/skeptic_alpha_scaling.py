"""SKEPTIC probe: is alpha(G) for the triangle-free process graph really
Theta(sqrt(n log n)) (proposal claim (i)), or is it sqrt(n)*log n / something else?

The proposal's whole decomposition a* = alpha * rho rests on alpha being the
sqrt(n log n) 'floor'. But Shearer's bound for a triangle-free graph of average
degree d gives alpha >= (n/d)(ln d - 1+o(1)). Here d ~ c*sqrt(n), so
  alpha >~ (n/(c sqrt n)) * ln(c sqrt n) = (1/c) sqrt(n) * (1/2 ln n + ln c)
       ~ (1/(2c)) sqrt(n) log n,
which is sqrt(n)*log(n), i.e. the SAME P2 upper-bound scale, NOT sqrt(n log n).

So measure alpha against BOTH normalizations across a wider n range, many seeds,
and report which is flatter. Also report the average degree d of the kept graph.
"""
from __future__ import annotations
import os
import math, sys, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core, networkx as nx
from lit_reduction_test import triangle_free_process


def alpha_independence(n, edges):
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges)
    Gc = nx.complement(G)
    return max((len(c) for c in nx.find_cliques(Gc)), default=0)


def main():
    ns = [20, 30, 40, 50, 70, 100, 140, 200, 300]
    cs = [1.5, 2.0, 2.5]
    n_seeds = 6
    print(f"{'n':>4} {'alpha_min':>9} {'alpha_max':>9} {'dbar':>6} "
          f"{'a/sqrt(nlogn)':>13} {'a/(sqrtn*logn)':>14}")
    rows = []
    for n in ns:
        # mimic the proposal: keep, per n, the graph minimizing a*; but a* is
        # expensive so here we report alpha statistics across all kept graphs and
        # the alpha of the SPARSEST-a* proxy is not needed -- the proposal's
        # claim (i) is about alpha SCALE which is orientation-independent.
        best_alpha = None  # graph minimizing a* would tend to be sparsest; but
        alphas = []
        dbars = []
        chosen = None
        for c in cs:
            p = c / math.sqrt(n)
            m_cap = int(p * n * (n - 1) / 2)
            for s in range(n_seeds):
                n2, edges = triangle_free_process(n, m_cap, seed=1000 * int(c * 10) + s + n)
                if not core.is_triangle_free(n2, edges):
                    continue
                a = alpha_independence(n2, edges)
                d = 2 * len(edges) / n2
                alphas.append(a); dbars.append(d)
                # proposal keeps the graph minimizing a*; smaller a* tends to go
                # with smaller alpha. Track the min-alpha graph as a fair proxy
                # for "the kept graph" (lower bound on the kept alpha).
                if chosen is None or a < chosen[0]:
                    chosen = (a, d, c, s)
        amin = min(alphas); amax = max(alphas)
        a_chosen = chosen[0]
        snln = math.sqrt(n * math.log(n))
        snlogn = math.sqrt(n) * math.log(n)
        dbar = statistics.mean(dbars)
        print(f"{n:>4} {amin:>9} {amax:>9} {dbar:>6.2f} "
              f"{a_chosen/snln:>13.4f} {a_chosen/snlogn:>14.4f}")
        rows.append((n, a_chosen, dbar, a_chosen/snln, a_chosen/snlogn))

    # ratio rises across full range
    print("\n=== scaling diagnostics (using min-alpha 'kept' graph) ===")
    n0, a0 = rows[0][0], rows[0][1]
    nL, aL = rows[-1][0], rows[-1][1]
    r1_0, r1_L = rows[0][3], rows[-1][3]
    r2_0, r2_L = rows[0][4], rows[-1][4]
    print(f"alpha/sqrt(n logn): n={n0}->{r1_0:.4f}, n={nL}->{r1_L:.4f}  "
          f"rise={r1_L/r1_0:.4f}")
    print(f"alpha/(sqrtn*logn): n={n0}->{r2_0:.4f}, n={nL}->{r2_L:.4f}  "
          f"rise={r2_L/r2_0:.4f}")
    print("FLAT normalization = the true alpha scale. "
          "If a/(sqrtn*logn) is flatter, alpha ~ sqrt(n)*log n (P2 scale), "
          "NOT sqrt(n log n) -> proposal claim (i) is FALSE.")

    # log-log fit alpha = A * sqrt(n) * (log n)^gamma : recover gamma
    import numpy as np
    xs_sqrtn = [math.log(math.sqrt(r[0])) for r in rows]
    xs_logn = [math.log(math.log(r[0])) for r in rows]
    ys = [math.log(r[1]) for r in rows]
    M = np.column_stack([np.ones(len(ys)), xs_sqrtn, xs_logn])
    coef, *_ = np.linalg.lstsq(M, np.array(ys), rcond=None)
    A, B, C = coef
    print(f"\nFIT log alpha = {A:.3f} + {B:.3f} log(sqrt n) + {C:.3f} log(log n)")
    print(f"  B (expect ~1 for sqrt n): {B:.3f}")
    print(f"  C (loglog exponent): {C:.3f}  "
          f"[0.5 => sqrt(n logn); 1.0 => sqrt(n)*logn]")


if __name__ == "__main__":
    main()
