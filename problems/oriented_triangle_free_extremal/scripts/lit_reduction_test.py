"""Ground-plan for the literature-reduction proposal.

Build G ~ G(n, c/sqrt n), make it triangle-free (remove an edge from each
triangle), take independent uniform random orientations, compute EXACT
core.acyclic_number, record a* = min over orientations and samples, then min
over c (best construction). Report a*, a*/sqrt(n log n), a*/(sqrt n * log n).

CONFIRM iff a*/sqrt(n log n) stays bounded (sub-sqrt(log n) growth).
KILL iff a*/sqrt(n log n) keeps rising at rate ~sqrt(log n).
"""
from __future__ import annotations

import math
import random
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core


def gnp_triangle_free(n, p, seed):
    """G(n,p) with one edge removed from each triangle -> triangle-free graph."""
    rng = random.Random(seed)
    adj = [set() for _ in range(n)]
    edges = set()
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                edges.add((i, j))
                adj[i].add(j)
                adj[j].add(i)
    # remove triangles: scan edges, if u,v have common neighbour, drop edge (u,v)
    changed = True
    while changed:
        changed = False
        for (u, v) in list(edges):
            if (u, v) not in edges:
                continue
            if adj[u] & adj[v]:
                edges.discard((u, v))
                adj[u].discard(v)
                adj[v].discard(u)
                changed = True
    return n, sorted(edges)


def triangle_free_process(n, m_cap, seed):
    """Triangle-free process: add random edges in random order, skipping any
    edge that would create a triangle, until m_cap edges or exhaustion.

    With m_cap ~ c/sqrt(n) * C(n,2) this realises the dense near-extremal
    triangle-free graph the paper's H1/G2 route targets (Bohman-Keevash).
    """
    rng = random.Random(seed)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    adj = [set() for _ in range(n)]
    edges = []
    for (u, v) in pairs:
        if len(edges) >= m_cap:
            break
        if adj[u] & adj[v]:
            continue
        edges.append((u, v))
        adj[u].add(v)
        adj[v].add(u)
    return n, sorted(edges)


def random_orientation(edges, seed):
    rng = random.Random(seed)
    arcs = []
    for (u, v) in edges:
        arcs.append((u, v) if rng.random() < 0.5 else (v, u))
    return arcs


def main():
    ns = [40, 60, 80, 120, 160]
    cs = [1.0, 1.5, 2.0, 2.5, 3.0]
    n_samples = 8          # orientations/graphs per (n,c)
    per_call_timeout = 90  # seconds soft budget per n via wall clock

    results = {}
    for n in ns:
        t_n_start = time.time()
        best_overall = None
        per_c = {}
        for c in cs:
            p = c / math.sqrt(n)
            # target edge count: density p = c/sqrt(n) on the n*(n-1)/2 pairs.
            m_cap = int(p * n * (n - 1) / 2)
            best_c = None
            for s in range(n_samples):
                # triangle-free PROCESS graph (dense, near-extremal) — the H1/G2 target
                n2, edges = triangle_free_process(n, m_cap, seed=1000 * int(c * 10) + s + n)
                assert core.is_triangle_free(n2, edges)
                arcs = random_orientation(edges, seed=7 * s + 3)
                assert core.is_oriented(arcs)
                a = core.acyclic_number(n2, arcs)
                if best_c is None or a < best_c:
                    best_c = a
                if best_overall is None or a < best_overall:
                    best_overall = a
            per_c[c] = best_c
            print(f"  n={n} c={c} best_a={best_c} (elapsed {time.time()-t_n_start:.1f}s)",
                  flush=True)
            if time.time() - t_n_start > per_call_timeout * len(cs):
                print(f"  n={n}: time budget hit, stopping c-loop", flush=True)
                break
        snl = math.sqrt(n * math.log(n))
        snln = math.sqrt(n) * math.log(n)
        results[n] = (best_overall, best_overall / snl, best_overall / snln, per_c)
        print(f"==> n={n}  a*={best_overall}  "
              f"a*/sqrt(n logn)={best_overall/snl:.4f}  "
              f"a*/(sqrt n logn)={best_overall/snln:.4f}  "
              f"(n total {time.time()-t_n_start:.1f}s)", flush=True)

    print("\n=== SUMMARY ===", flush=True)
    print(f"{'n':>4} {'a*':>4} {'a*/sqrt(n logn)':>16} {'a*/(sqrt n logn)':>17}",
          flush=True)
    xs_sqrt, xs_loglog, ys = [], [], []
    for n in sorted(results):
        a, r1, r2, _ = results[n]
        print(f"{n:>4} {a:>4} {r1:>16.4f} {r2:>17.4f}", flush=True)
        xs_sqrt.append(math.log(math.sqrt(n)))
        xs_loglog.append(math.log(math.log(n)))
        ys.append(math.log(a))

    # Least squares: log a = A + B*log(sqrt n) + C*log log n
    # CONFIRM if C ~ 0.5 (sqrt(n log n)); KILL if C ~ 1.0 (sqrt n log n).
    import numpy as np
    M = np.column_stack([np.ones(len(ys)), xs_sqrt, xs_loglog])
    coef, *_ = np.linalg.lstsq(M, np.array(ys), rcond=None)
    A, B, C = coef
    print(f"\nFIT  log a* = {A:.4f} + {B:.4f}*log(sqrt n) + {C:.4f}*log log n",
          flush=True)
    print(f"  B (sqrt-n exponent, expect ~1.0): {B:.4f}", flush=True)
    print(f"  C (loglog exponent): {C:.4f}  "
          f"[CONFIRM~0.5 => sqrt(n logn); KILL~1.0 => sqrt n logn]", flush=True)

    # ratio rise check between n=40 and n=160
    if 40 in results and 160 in results:
        r40 = results[40][1]
        r160 = results[160][1]
        rise = r160 / r40
        pred_kill = math.sqrt(math.log(160) / math.log(40))
        print(f"\nratio a*/sqrt(n logn): n=40 -> {r40:.4f}, n=160 -> {r160:.4f}, "
              f"rise factor {rise:.4f}", flush=True)
        print(f"  CONFIRM if rise <= ~1.10; KILL if rise ~ {pred_kill:.4f} "
              f"(sqrt(log160/log40))", flush=True)


if __name__ == "__main__":
    main()
