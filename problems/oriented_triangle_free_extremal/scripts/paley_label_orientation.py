"""Paley/quadratic-residue LABEL-tournament orientation of the triangle-free
process graph -- offline, globally non-transitive orientation rule engineered
to suppress long transitive sub-tournaments (the G12-identified gap source).

For each vertex v assign a uniform random label L(v) in F_q (q ~ n, prime,
q % 4 == 3).  Orient each underlying edge {u,v} by the Paley rule:
   u -> v  iff (L(v) - L(u)) mod q is a quadratic residue mod q.
Paley tournaments have transitive subsets of size only O(log q), so the claim
is acyclic induced sets cannot grow a transitive spine and stay near-independent
(d* = O(1)), giving a_vec = Theta(alpha) = Theta(sqrt(n log n)).

CONFIRM (Conjecture-3 upper route alive): witness avg-degree d* stays O(1)/flat
(d*/log n declining toward 0) AND a*/sqrt(n log n) flat or declining (<= ~1.6),
strictly below the uniform-random a*/sqrt(n log n) which rises 1.81->2.06.
KILL (route dead): a*/(sqrt n * log n) FLAT ~1.07 (reproducing G4) AND witness
d* keeps growing ~log n, statistically indistinguishable from G12's uniform-
random d* baseline {20:3.47,30:4.70,40:4.64,50:5.69}.
"""
from __future__ import annotations

import math
import random
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FTimeout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from lit_reduction_test import triangle_free_process
from lit_reduction_degeneracy import acyclic_number_witness, avg_degree_in_set


def _is_prime(m):
    if m < 2:
        return False
    if m % 2 == 0:
        return m == 2
    i = 3
    while i * i <= m:
        if m % i == 0:
            return False
        i += 2
    return True


def next_prime_3mod4(lo):
    """Smallest prime q >= lo with q % 4 == 3."""
    q = lo
    while True:
        if q % 4 == 3 and _is_prime(q):
            return q
        q += 1


def qr_set(q):
    """Set of nonzero quadratic residues mod q."""
    return {(x * x) % q for x in range(1, q)}


def paley_label_orientation(edges, n, q, qr, rng):
    """Assign labels in F_q, orient each edge by the Paley/QR rule."""
    L = [rng.randrange(q) for _ in range(n)]
    arcs = []
    for (u, v) in edges:
        d = (L[v] - L[u]) % q
        # d != 0 a.s. for distinct labels; if labels collide, fall back to a
        # coin so the edge is still oriented (rare, keeps is_oriented true).
        if d == 0:
            arcs.append((u, v) if rng.random() < 0.5 else (v, u))
        elif d in qr:
            arcs.append((u, v))
        else:
            arcs.append((v, u))
    return arcs, L


def _witness_worker(n, arcs):
    return acyclic_number_witness(n, arcs)


def main():
    ns = [40, 60, 80]
    cs = [1.5, 2.0, 2.5]
    seeds = [0, 1, 2]
    per_inst_timeout = 120

    # G12 uniform-random witness avg-degree baseline (for the d* discriminator)
    g12_baseline = {20: 3.47, 30: 4.70, 40: 4.64, 50: 5.69}

    rows = []
    for n in ns:
        t0 = time.time()
        best = None  # (a*, S*, edges, arcs, c, seed, q)
        for c in cs:
            p = c / math.sqrt(n)
            m_cap = int(p * n * (n - 1) / 2)
            q = next_prime_3mod4(n)
            qr = qr_set(q)
            for s in seeds:
                n2, edges = triangle_free_process(
                    n, m_cap, seed=1000 * int(c * 10) + s + n)
                assert n2 == n
                assert core.is_triangle_free(n2, edges)
                rng = random.Random(98765 * s + 13 * int(c * 10) + n)
                arcs, L = paley_label_orientation(edges, n, q, qr, rng)
                assert core.is_oriented(arcs), "Paley orientation not oriented!"
                # underlying graph unchanged => still triangle-free
                assert core.is_triangle_free(n, arcs)
                with ProcessPoolExecutor(max_workers=1) as ex:
                    fut = ex.submit(_witness_worker, n2, arcs)
                    try:
                        a, S = fut.result(timeout=per_inst_timeout)
                    except FTimeout:
                        for p_ in ex._processes.values():
                            p_.kill()
                        print(f"   [n={n} c={c} seed={s}] TIMEOUT skipped",
                              flush=True)
                        continue
                assert len(S) == a
                print(f"   [n={n} c={c} seed={s}] q={q} a*={a} "
                      f"(elapsed {time.time()-t0:.1f}s)", flush=True)
                if best is None or a < best[0]:
                    best = (a, S, edges, arcs, c, s, q)
        if best is None:
            print(f"n={n}: ALL instances timed out", flush=True)
            continue
        a, S, edges, arcs, c, s, q = best
        d_star, e_in = avg_degree_in_set(edges, S)
        snl = math.sqrt(n * math.log(n))
        snln = math.sqrt(n) * math.log(n)
        logn = math.log(n)
        rows.append((n, a, len(S), d_star, a / snl, a / snln,
                     d_star / logn, c, s, q))
        print(f"==> n={n} a*={a} |S*|={len(S)} d*={d_star:.4f} "
              f"a*/sqrt(n logn)={a/snl:.4f} a*/(sqrt n logn)={a/snln:.4f} "
              f"d*/logn={d_star/logn:.4f} (best c={c} seed={s} q={q})",
              flush=True)

    print("\n=== SUMMARY TABLE ===", flush=True)
    print(f"{'n':>4} {'a*':>4} {'a*/sqrt(n logn)':>16} {'a*/(sqrt n logn)':>17} "
          f"{'d*':>8} {'d*/logn':>9} {'G12 d*':>8}", flush=True)
    R1 = []  # a*/sqrt(n logn)
    R2 = []  # a*/(sqrt n logn)
    D = []   # d*
    DL = []  # d*/logn
    for (n, a, sz, d_star, r1, r2, dl, c, s, q) in rows:
        g12 = g12_baseline.get(n, float("nan"))
        print(f"{n:>4} {a:>4} {r1:>16.4f} {r2:>17.4f} {d_star:>8.4f} "
              f"{dl:>9.4f} {g12:>8}", flush=True)
        R1.append(r1)
        R2.append(r2)
        D.append(d_star)
        DL.append(dl)

    def flatness(vals):
        m = sum(vals) / len(vals)
        return (max(vals) - min(vals)) / m if m else float("nan"), m

    print("\n=== SIGNATURES ===", flush=True)
    f1, m1 = flatness(R1)
    f2, m2 = flatness(R2)
    fdl, mdl = flatness(DL)
    print(f"a*/sqrt(n logn): {[f'{x:.4f}' for x in R1]} "
          f"mean={m1:.4f} range/mean={f1:.4f}", flush=True)
    print(f"a*/(sqrt n logn): {[f'{x:.4f}' for x in R2]} "
          f"mean={m2:.4f} range/mean={f2:.4f}", flush=True)
    print(f"d*: {[f'{x:.4f}' for x in D]}", flush=True)
    print(f"d*/logn: {[f'{x:.4f}' for x in DL]} "
          f"mean={mdl:.4f} range/mean={fdl:.4f}", flush=True)

    rising_R1 = len(R1) >= 2 and all(R1[i] <= R1[i+1] + 1e-9
                                     for i in range(len(R1)-1))
    declining_DL = len(DL) >= 2 and all(DL[i] >= DL[i+1] - 1e-9
                                        for i in range(len(DL)-1))
    print("\n=== DECISION SIGNAL ===", flush=True)
    print(f"a*/sqrt(n logn) max={max(R1):.4f} (CONFIRM wants <=~1.6 and "
          f"flat/declining)", flush=True)
    print(f"a*/(sqrt n logn) mean={m2:.4f} (KILL wants flat ~1.07)", flush=True)
    print(f"d*/logn declining? {declining_DL}  (CONFIRM wants declining "
          f"toward 0)", flush=True)
    print(f"a*/sqrt(n logn) rising? {rising_R1}  (KILL wants rising at "
          f"sqrt(log) rate like uniform-random 1.81->2.06)", flush=True)

    confirm = (max(R1) <= 1.6) and not rising_R1 and declining_DL
    kill = rising_R1 and (1.0 <= m2 <= 1.15)
    if confirm:
        print("VERDICT-SIGNAL: CONFIRM (Paley orientation near-independent, "
              "route ALIVE)", flush=True)
    elif kill:
        print("VERDICT-SIGNAL: KILL (Paley re-floors at the random barrier)",
              flush=True)
    else:
        print("VERDICT-SIGNAL: AMBIGUOUS", flush=True)


if __name__ == "__main__":
    main()
