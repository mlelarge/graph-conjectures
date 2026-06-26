"""Focused fast confirmation: extend the G2 a*/sqrt(n log n) curve past n=40.

The process graph saturates near m ~ 0.5 n^1.5 sqrt(ln n); c=1.5..2.0 already
realises essentially the densest (= smallest acyclic number) construction, and
MaxSAT stays tractable there. We compute exact a* = min over samples & over
c in {1.5,2.0} for n in {20,30,40,50,60,70} and report the ratio growth.

Discriminator (proposal's own): does a*/sqrt(n log n) PLATEAU (CONFIRM) or keep
RISING at the sqrt(log n) rate (KILL)? KILL also iff a*/(sqrt n log n) stays
bounded away from 0 and roughly flat (degeneracy d is the true order).
"""
from __future__ import annotations

import math
import multiprocessing as mp
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from lit_reduction_test import triangle_free_process, random_orientation


def _worker(n, arcs, q):
    q.put(core.acyclic_number(n, arcs))


def acyclic_timed(n, arcs, timeout):
    q = mp.Queue()
    p = mp.Process(target=_worker, args=(n, arcs, q))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate(); p.join()
        return None
    return q.get() if not q.empty() else None


def main():
    ns = [20, 30, 40, 50, 60, 70]
    cs = [1.5, 2.0]
    n_samples = 6
    timeout = 60

    results = {}
    for n in ns:
        best = None
        got_any = False
        for c in cs:
            p = c / math.sqrt(n)
            m_cap = int(p * n * (n - 1) / 2)
            for s in range(n_samples):
                n2, edges = triangle_free_process(n, m_cap, seed=1000 * int(c * 10) + s + n)
                assert core.is_triangle_free(n2, edges)
                arcs = random_orientation(edges, seed=7 * s + 3)
                assert core.is_oriented(arcs)
                a = acyclic_timed(n2, arcs, timeout)
                if a is None:
                    continue
                got_any = True
                if best is None or a < best:
                    best = a
        snl = math.sqrt(n * math.log(n))
        snln = math.sqrt(n) * math.log(n)
        results[n] = (best, best / snl, best / snln)
        print(f"n={n}  a*={best}  a*/sqrt(n logn)={best/snl:.4f}  a*/(sqrt n logn)={best/snln:.4f}",
              flush=True)

    print("\n=== CURVE ===", flush=True)
    ratios = [results[n][1] for n in ns]
    print("a*/sqrt(n logn):", [round(r, 4) for r in ratios], flush=True)
    print("monotone rising?", all(ratios[i+1] >= ratios[i] - 1e-9 for i in range(len(ratios)-1)),
          flush=True)
    print("a*/(sqrt n logn):", [round(results[n][2], 4) for n in ns], flush=True)

    import numpy as np
    xs_sqrt = [math.log(math.sqrt(n)) for n in ns]
    xs_ll = [math.log(math.log(n)) for n in ns]
    ys = [math.log(results[n][0]) for n in ns]
    M = np.column_stack([np.ones(len(ys)), xs_sqrt, xs_ll])
    A, B, C = np.linalg.lstsq(M, np.array(ys), rcond=None)[0]
    print(f"\nFIT log a* = {A:.4f} + {B:.4f} log(sqrt n) + {C:.4f} loglog n", flush=True)
    print(f"  B~{B:.4f} (expect ~1.0), C~{C:.4f}  "
          f"[CONFIRM C~0.5 (sqrt(n logn)); KILL C~1.0 (sqrt n logn)]", flush=True)

    rise = ratios[-1] / ratios[0]
    pred = math.sqrt(math.log(ns[-1]) / math.log(ns[0]))
    print(f"\nratio rise n={ns[0]}->{ns[-1]}: {ratios[0]:.4f} -> {ratios[-1]:.4f} "
          f"(x{rise:.4f}); sqrt(log)-KILL signature x{pred:.4f}", flush=True)


if __name__ == "__main__":
    main()
