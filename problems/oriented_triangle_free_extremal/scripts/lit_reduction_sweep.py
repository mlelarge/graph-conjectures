"""Tractable sweep for the literature-reduction proposal.

Exact core.acyclic_number on triangle-free PROCESS graphs G(n,c/sqrt n),
best (min) over c and over independent samples. Tracks a*/sqrt(n log n).

CONFIRM iff a*/sqrt(n log n) plateaus (sub-sqrt(log n) growth).
KILL iff it keeps rising at the sqrt(log n) rate.

Each acyclic_number call is run with a per-call wall timeout in a worker
process; if it stalls, that (n,c,sample) is skipped (does NOT contribute a
spuriously small a*).
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


def acyclic_number_timed(n, arcs, timeout):
    q = mp.Queue()
    p = mp.Process(target=_worker, args=(n, arcs, q))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        p.join()
        return None
    return q.get() if not q.empty() else None


def main():
    ns = [20, 30, 40, 50, 60, 70]
    cs = [1.0, 1.5, 2.0, 2.5, 3.0]
    n_samples = 6
    per_call_timeout = 45  # seconds per acyclic_number

    results = {}
    for n in ns:
        best_overall = None
        per_c = {}
        for c in cs:
            p = c / math.sqrt(n)
            m_cap = int(p * n * (n - 1) / 2)
            best_c = None
            for s in range(n_samples):
                n2, edges = triangle_free_process(n, m_cap, seed=1000 * int(c * 10) + s + n)
                assert core.is_triangle_free(n2, edges)
                arcs = random_orientation(edges, seed=7 * s + 3)
                assert core.is_oriented(arcs)
                a = acyclic_number_timed(n2, arcs, per_call_timeout)
                if a is None:
                    continue
                if best_c is None or a < best_c:
                    best_c = a
                if best_overall is None or a < best_overall:
                    best_overall = a
            per_c[c] = best_c
            print(f"  n={n} c={c} m_cap={m_cap} best_a={best_c}", flush=True)
        snl = math.sqrt(n * math.log(n))
        snln = math.sqrt(n) * math.log(n)
        results[n] = (best_overall, best_overall / snl, best_overall / snln, per_c)
        print(f"==> n={n}  a*={best_overall}  a*/sqrt(n logn)={best_overall/snl:.4f}  "
              f"a*/(sqrt n logn)={best_overall/snln:.4f}", flush=True)

    print("\n=== SUMMARY ===", flush=True)
    print(f"{'n':>4} {'a*':>4} {'a*/sqrt(n logn)':>16} {'a*/(sqrt n logn)':>17}", flush=True)
    xs_sqrt, xs_loglog, ys = [], [], []
    for n in sorted(results):
        a, r1, r2, _ = results[n]
        print(f"{n:>4} {a:>4} {r1:>16.4f} {r2:>17.4f}", flush=True)
        xs_sqrt.append(math.log(math.sqrt(n)))
        xs_loglog.append(math.log(math.log(n)))
        ys.append(math.log(a))

    import numpy as np
    M = np.column_stack([np.ones(len(ys)), xs_sqrt, xs_loglog])
    coef, *_ = np.linalg.lstsq(M, np.array(ys), rcond=None)
    A, B, C = coef
    print(f"\nFIT  log a* = {A:.4f} + {B:.4f}*log(sqrt n) + {C:.4f}*log log n", flush=True)
    print(f"  C (loglog exponent): {C:.4f}  [CONFIRM~0.5 => sqrt(n logn); KILL~1.0 => sqrt n logn]", flush=True)

    nn = sorted(results)
    r_lo, r_hi = results[nn[0]][1], results[nn[-1]][1]
    rise = r_hi / r_lo
    pred_kill = math.sqrt(math.log(nn[-1]) / math.log(nn[0]))
    print(f"\nratio a*/sqrt(n logn): n={nn[0]} -> {r_lo:.4f}, n={nn[-1]} -> {r_hi:.4f}, rise {rise:.4f}", flush=True)
    print(f"  full-range sqrt(log)-predicted rise (KILL signature) = {pred_kill:.4f}", flush=True)
    # plateau check on a*/(sqrt n logn): under KILL this should be FLAT (bounded away from 0)
    r2vals = [results[n][2] for n in nn]
    print(f"  a*/(sqrt n logn) over n: {[round(x,4) for x in r2vals]}", flush=True)


if __name__ == "__main__":
    main()
