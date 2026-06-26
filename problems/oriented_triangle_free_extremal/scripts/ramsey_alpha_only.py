"""Phase A of the ground: EXACT alpha(G) on the SATURATED triangle-free process,
across n, to test the proposal's load-bearing claim that at maximal density
alpha tracks sqrt(n log n) (FLAT) rather than sqrt(n)*log n (the G17/G18 finding).

EXACT alpha via core.acyclic_number on the bidirected graph (verified == independence).
This is the cheap, decisive measurement. a_vec (expensive) is Phase B.
"""
from __future__ import annotations
import os
import math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from ramsey_extremal import saturate, alpha_exact_bidirected


def main():
    ns = [40, 60, 80, 100, 140, 200]
    n_seeds = 4
    print(f"{'n':>4} {'dbar':>6} {'alpha_min':>9} {'d/snln':>7} "
          f"{'al/snln':>8} {'al/snlog':>9}", flush=True)
    summary = []
    for n in ns:
        snln = math.sqrt(n * math.log(n))
        snlogn = math.sqrt(n) * math.log(n)
        ds, als = [], []
        for s in range(n_seeds):
            n2, edges = saturate(n, seed=4242 + 13 * s + n)
            assert core.is_triangle_free(n2, edges)
            ds.append(2 * len(edges) / n2)
            als.append(alpha_exact_bidirected(n2, edges))
        dbar = sum(ds) / len(ds)
        almin = min(als)
        print(f"{n:>4} {dbar:>6.2f} {almin:>9} {dbar/snln:>7.3f} "
              f"{almin/snln:>8.3f} {almin/snlogn:>9.3f}", flush=True)
        summary.append((n, dbar, almin, snln, snlogn))

    print("\n=== DIAGNOSTICS ===", flush=True)
    al_snln = [(n, almin / snln) for (n, dbar, almin, snln, snlogn) in summary]
    al_snlog = [(n, almin / snlogn) for (n, dbar, almin, snln, snlogn) in summary]
    d_snln = [(n, dbar / snln) for (n, dbar, almin, snln, snlogn) in summary]
    print("alpha/sqrt(n logn): " + ", ".join(f"{n}:{r:.3f}" for n, r in al_snln)
          + f"   rise {al_snln[-1][1]/al_snln[0][1]:.3f}", flush=True)
    print("alpha/(sqrtn*logn): " + ", ".join(f"{n}:{r:.3f}" for n, r in al_snlog)
          + f"   rise {al_snlog[-1][1]/al_snlog[0][1]:.3f}", flush=True)
    print("dbar/sqrt(n logn) : " + ", ".join(f"{n}:{r:.3f}" for n, r in d_snln)
          + f"   rise {d_snln[-1][1]/d_snln[0][1]:.3f}", flush=True)

    # coefficient of variation: flatter normalization = true scale
    import statistics
    cv_snln = statistics.pstdev([r for _, r in al_snln]) / statistics.mean([r for _, r in al_snln])
    cv_snlog = statistics.pstdev([r for _, r in al_snlog]) / statistics.mean([r for _, r in al_snlog])
    print(f"CV alpha/sqrt(n logn) = {cv_snln:.4f}", flush=True)
    print(f"CV alpha/(sqrtn*logn) = {cv_snlog:.4f}", flush=True)
    print("FLATTER (lower CV) normalization = true alpha scale.", flush=True)


if __name__ == "__main__":
    main()
