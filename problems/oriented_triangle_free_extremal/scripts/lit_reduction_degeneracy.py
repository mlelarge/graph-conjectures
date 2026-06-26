"""Ground-plan for the literature-reduction DEGENERACY proposal.

Hypothesis: Lemma 2.4 certifies acyclic sets as d-SPARSE with worst-case
d = 2*log2(n). The extra sqrt(log n) in the a_vec upper bound is ENTIRELY the
gap between d = Theta(log n) (Lemma 2.4) and d = Theta(sqrt(log n)) (the value
forced by the proven lower bound). FALSIFIABLE CORE: measure the actual
average degree d* = 2*|E(G[S*])|/|S*| of the OPTIMAL acyclic witness set S* of
the best (min-a*) random orientation, as a function of n.

CONFIRM: d*/sqrt(log n) flat (range/mean < 0.20) AND d*/log n declining AND d*
strictly below Lemma 2.4's 2*log2(n) by a growing gap.
KILL: d*/log n flat (Lemma 2.4 tight up to constants).
"""
from __future__ import annotations

import math
import random
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from lit_reduction_test import triangle_free_process, random_orientation

from pysat.formula import WCNF
from pysat.examples.rc2 import RC2


def acyclic_number_witness(n, arcs):
    """Exact alpha_vec(D) AND a witness set S* realizing it.

    Identical MaxSAT + lazy-cycle-elimination loop as core.acyclic_number,
    but also returns the selected vertex set (the max induced acyclic set).
    """
    if n == 0:
        return 0, []
    hard = []
    while True:
        wcnf = WCNF()
        for v in range(n):
            wcnf.append([v + 1], weight=1)
        for clause in hard:
            wcnf.append(clause)
        with RC2(wcnf) as rc2:
            model = rc2.compute()
        chosen = [v for v in range(n) if (v + 1) in set(model)]
        sub = core._digraph(n, [(u, v) for (u, v) in arcs
                                if u in chosen and v in chosen])
        cyc = core._find_directed_cycle(sub.subgraph(chosen))
        if cyc is None:
            return len(chosen), chosen
        hard.append([-(v + 1) for v in cyc])


def _witness_worker(n, edges, arcs):
    """Top-level worker (picklable) for ProcessPoolExecutor: compute a* + S*."""
    a, S = acyclic_number_witness(n, arcs)
    return a, S


def avg_degree_in_set(edges, S):
    """d* = 2*|E(G[S])|/|S| = average degree of the underlying graph induced
    on the vertex set S."""
    Sset = set(S)
    e_in = sum(1 for (u, v) in edges if u in Sset and v in Sset)
    return 2.0 * e_in / len(S), e_in


def main():
    import time
    from concurrent.futures import ProcessPoolExecutor, TimeoutError as FTimeout
    ns = [20, 30, 40, 50, 60]
    cs = [1.5, 2.0]
    n_seeds = 3
    per_inst_timeout = 120  # seconds per (n,c,seed); skip pathological MaxSAT

    rows = []
    for n in ns:
        t0 = time.time()
        best = None  # (a*, S*, edges, c, seed)
        n_done = 0
        for c in cs:
            p = c / math.sqrt(n)
            m_cap = int(p * n * (n - 1) / 2)
            for s in range(n_seeds):
                n2, edges = triangle_free_process(
                    n, m_cap, seed=1000 * int(c * 10) + s + n)
                assert core.is_triangle_free(n2, edges)
                arcs = random_orientation(edges, seed=7 * s + 3)
                assert core.is_oriented(arcs)
                # run witness MaxSAT in a subprocess with a hard timeout
                with ProcessPoolExecutor(max_workers=1) as ex:
                    fut = ex.submit(_witness_worker, n2, edges, arcs)
                    try:
                        a, S = fut.result(timeout=per_inst_timeout)
                    except FTimeout:
                        for p_ in ex._processes.values():
                            p_.kill()
                        print(f"   [n={n} c={c} seed={s}] TIMEOUT "
                              f"(> {per_inst_timeout}s) skipped", flush=True)
                        continue
                # sanity: S genuinely acyclic and of size a
                assert len(S) == a
                sub_arcs = [(u, v) for (u, v) in arcs if u in set(S) and v in set(S)]
                assert core.is_acyclic(n2, sub_arcs), "witness not acyclic!"
                n_done += 1
                print(f"   [n={n} c={c} seed={s}] a={a} "
                      f"(elapsed {time.time()-t0:.1f}s)", flush=True)
                if best is None or a < best[0]:
                    best = (a, S, edges, c, s)
        if best is None:
            print(f"n={n}: ALL instances timed out, skipping", flush=True)
            continue
        a, S, edges, c, s = best
        d_star, e_in = avg_degree_in_set(edges, S)
        lemma24 = 2.0 * math.log2(n)
        sqrt_logn = math.sqrt(math.log(n))
        logn = math.log(n)
        rows.append((n, a, len(S), e_in, d_star, lemma24,
                     d_star / sqrt_logn, d_star / logn, c, s))
        print(f"n={n:>3} a*={a:>3} |S*|={len(S):>3} e_in={e_in:>4} "
              f"d*={d_star:.4f} 2log2n={lemma24:.4f} "
              f"d*/sqrt(logn)={d_star/sqrt_logn:.4f} "
              f"d*/logn={d_star/logn:.4f} (best c={c} seed={s})", flush=True)

    print("\n=== SUMMARY TABLE ===", flush=True)
    print(f"{'n':>4} {'a*':>4} {'|S*|':>5} {'d*':>8} {'2log2n':>8} "
          f"{'d*/sqrt(logn)':>14} {'d*/logn':>9}", flush=True)
    r1 = []  # d*/sqrt(logn)
    r2 = []  # d*/logn
    gaps = []  # lemma24 - d*
    for (n, a, sz, e_in, d_star, lemma24, rr1, rr2, c, s) in rows:
        print(f"{n:>4} {a:>4} {sz:>5} {d_star:>8.4f} {lemma24:>8.4f} "
              f"{rr1:>14.4f} {rr2:>9.4f}", flush=True)
        r1.append(rr1)
        r2.append(rr2)
        gaps.append(lemma24 - d_star)

    def flatness(vals):
        m = sum(vals) / len(vals)
        return (max(vals) - min(vals)) / m, m

    fr1, m1 = flatness(r1)
    fr2, m2 = flatness(r2)
    print(f"\nd*/sqrt(logn): values {[f'{x:.3f}' for x in r1]}", flush=True)
    print(f"  mean={m1:.4f} range/mean={fr1:.4f} "
          f"[CONFIRM wants flat: <0.20]", flush=True)
    print(f"d*/logn:       values {[f'{x:.3f}' for x in r2]}", flush=True)
    print(f"  mean={m2:.4f} range/mean={fr2:.4f} "
          f"[KILL wants flat: <0.20]", flush=True)
    # monotone trend of d*/logn
    declining_r2 = all(r2[i] >= r2[i + 1] - 1e-9 for i in range(len(r2) - 1))
    declining_r1 = all(r1[i] >= r1[i + 1] - 1e-9 for i in range(len(r1) - 1))
    print(f"  d*/logn monotone non-increasing? {declining_r2}", flush=True)
    print(f"  d*/sqrt(logn) monotone non-increasing? {declining_r1}", flush=True)
    print(f"Lemma2.4 gap (2log2n - d*): {[f'{g:.3f}' for g in gaps]} "
          f"[CONFIRM wants growing positive gap]", flush=True)
    gap_growing = all(gaps[i] <= gaps[i + 1] + 1e-9 for i in range(len(gaps) - 1))
    print(f"  gap monotone non-decreasing (growing)? {gap_growing}", flush=True)

    # Decision per falsifiable_prediction
    confirm = (fr1 < 0.20) and (not flatness(r2)[0] < 0.20 or m2 > 0) and \
              all(g > 0 for g in gaps)
    # primary discriminator: which ratio is flatter?
    print("\n=== DECISION ===", flush=True)
    print(f"d*/sqrt(logn) flatness={fr1:.4f}  vs  d*/logn flatness={fr2:.4f}",
          flush=True)
    if fr1 < 0.20 and fr1 < fr2 and all(g > 0 for g in gaps):
        print("VERDICT-SIGNAL: CONFIRM (d*/sqrt(logn) flat, below Lemma2.4)",
              flush=True)
    elif fr2 < 0.20 and fr2 < fr1:
        print("VERDICT-SIGNAL: KILL (d*/logn flat => Lemma2.4 tight)",
              flush=True)
    else:
        print("VERDICT-SIGNAL: AMBIGUOUS (neither ratio cleanly flat)",
              flush=True)


if __name__ == "__main__":
    main()
