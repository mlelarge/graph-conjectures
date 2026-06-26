"""GROUND for the Round-8 'asymptotic-argument' proposal (rho_same = a_vec/alpha
on the greedy-maximal / alpha-minimizing triangle-free graph).

The proposal's build_greedy_maximal(n,seed) IS the saturated triangle-free
process (no density cap) = the G20/G21 saturated graph. We:
  - build that exact graph (EXACT, triangle-free verified),
  - alpha(G) = EXACT independence number via core.acyclic_number on bidirected,
  - a_vec(D) = EXACT core.acyclic_number, min over several random orientations
    (worst orientation = the proposal's reported a_vec), os.killpg-capped,
  - report rho_same = a_vec/alpha  AND the decisive scale test
    alpha/sqrt(n log n)  vs  alpha/(sqrt(n)*log n).

LOAD-BEARING distinction (per ledger D7/G17/G20/G21):
  The proposal's CONFIRM (rho_same bounded) is true but VACUOUS unless ALSO
  alpha/sqrt(n log n) is FLAT.  If alpha/sqrt(n log n) RISES while
  alpha/(sqrt n * log n) is FLAT, then alpha ~ sqrt(n) log n and bounded rho
  gives a_vec = O(sqrt(n) log n) = the EXISTING P2 bound, NOT the conjecture.
"""
from __future__ import annotations
import os
import math, sys, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from ramsey_extremal import saturate, alpha_exact_bidirected, run_with_timeout
from lit_reduction_test import random_orientation


def main():
    # proposal's window n=20,25,...,60 ; extend with larger n for alpha (cheap)
    ns_full = [20, 25, 30, 35, 40, 45, 50, 60]
    n_seeds = 3
    n_orient = 3
    AVEC_TIMEOUT = 90
    print(f"{'n':>4} {'dbar':>6} {'d/sqn':>6} {'alpha':>6} {'a_vec':>6} "
          f"{'rho_same':>8} {'al/snln':>8} {'al/snlog':>9} {'av/snln':>8} {'av/snlog':>9}",
          flush=True)
    summary = []
    for n in ns_full:
        snln = math.sqrt(n * math.log(n))      # sqrt(n log n) = conjecture target
        snlogn = math.sqrt(n) * math.log(n)    # sqrt(n) * log n = P2 scale
        best_alpha = None
        d_used = None
        for s in range(n_seeds):
            n2, edges = saturate(n, seed=4242 + 13 * s + n)
            assert core.is_triangle_free(n2, edges), "process produced a triangle!"
            a = alpha_exact_bidirected(n2, edges)
            # alpha-minimizing => take min alpha across seeds, store its graph
            if best_alpha is None or a < best_alpha:
                best_alpha = a
                best_edges = edges
                d_used = 2 * len(edges) / n2
        alpha = best_alpha
        # a_vec on the alpha-minimizing graph: WORST (min) over random orientations
        best_av = None
        for o in range(n_orient):
            arcs = random_orientation(best_edges, seed=999 * o + n)
            assert core.is_oriented(arcs)
            av = run_with_timeout(core.acyclic_number, (n, arcs), AVEC_TIMEOUT)
            if av is None:
                continue
            if best_av is None or av < best_av:
                best_av = av
        rho = (best_av / alpha) if best_av else None
        av_str = f"{best_av}" if best_av is not None else "TIMEOUT"
        rho_str = f"{rho:.3f}" if rho is not None else "--"
        avsnln = f"{best_av/snln:.3f}" if best_av is not None else "--"
        avsnlog = f"{best_av/snlogn:.3f}" if best_av is not None else "--"
        print(f"{n:>4} {d_used:>6.2f} {d_used/math.sqrt(n):>6.3f} {alpha:>6} {av_str:>6} "
              f"{rho_str:>8} {alpha/snln:>8.3f} {alpha/snlogn:>9.3f} "
              f"{avsnln:>8} {avsnlog:>9}", flush=True)
        summary.append((n, d_used, alpha, best_av, snln, snlogn))

    print("\n=== DECISIVE SCALE TEST (which normalization is FLAT?) ===", flush=True)
    al_snln = [(n, al / snln) for (n, d, al, av, snln, snlog) in summary]
    al_snlog = [(n, al / snlog) for (n, d, al, av, snln, snlog) in summary]
    print("alpha/sqrt(n logn): " + ", ".join(f"{n}:{r:.3f}" for n, r in al_snln)
          + f"   rise20->60 {al_snln[-1][1]/al_snln[0][1]:.3f}", flush=True)
    print("alpha/(sqrtn*logn): " + ", ".join(f"{n}:{r:.3f}" for n, r in al_snlog)
          + f"   rise20->60 {al_snlog[-1][1]/al_snlog[0][1]:.3f}", flush=True)
    cv_snln = statistics.pstdev([r for _, r in al_snln]) / statistics.mean([r for _, r in al_snln])
    cv_snlog = statistics.pstdev([r for _, r in al_snlog]) / statistics.mean([r for _, r in al_snlog])
    print(f"CV alpha/sqrt(n logn) = {cv_snln:.4f}", flush=True)
    print(f"CV alpha/(sqrtn*logn) = {cv_snlog:.4f}   (lower CV = TRUE alpha scale)", flush=True)

    print("\n=== PROPOSAL'S falsifiable handles ===", flush=True)
    rhos = [(n, av / al) for (n, d, al, av, snln, snlog) in summary if av is not None]
    print("rho_same          : " + ", ".join(f"{n}:{r:.3f}" for n, r in rhos), flush=True)
    if rhos:
        r20 = dict(rhos).get(20); r60 = dict(rhos).get(60)
        if r20 and r60:
            print(f"rho_same(60)/rho_same(20) = {r60/r20:.4f}   "
                  f"(proposal CONFIRM iff < 1.15)", flush=True)
    av_snln = [(n, av / snln) for (n, d, al, av, snln, snlog) in summary if av is not None]
    av_snlog = [(n, av / snlog) for (n, d, al, av, snln, snlog) in summary if av is not None]
    print("a_vec/sqrt(n logn): " + ", ".join(f"{n}:{r:.3f}" for n, r in av_snln)
          + (f"   rise {av_snln[-1][1]/av_snln[0][1]:.3f}" if len(av_snln) > 1 else ""), flush=True)
    print("a_vec/(sqrtn*logn): " + ", ".join(f"{n}:{r:.3f}" for n, r in av_snlog)
          + (f"   rise {av_snlog[-1][1]/av_snlog[0][1]:.3f}" if len(av_snlog) > 1 else ""), flush=True)


if __name__ == "__main__":
    main()
