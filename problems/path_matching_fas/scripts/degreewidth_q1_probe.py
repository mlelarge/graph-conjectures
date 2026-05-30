"""Q1 probe: candidate polynomial characterizations of "Δ*(T) ≤ 2".

Q1 (open for tournaments): is degreewidth ≤ 2 poly-decidable?  We test
cheap candidate certificates against the exact Held-Karp solver
(scripts/degreewidth_exact) over exhaustive small n, random larger n, and
the certified hard minimal-NO catalogues.

Key identity (used throughout).  For an order with position i(v) and
b(v) = #in-neighbours of v placed before v,
    bd(v) = i(v) + d⁻(v) − 2·b(v).
Corollaries (necessary conditions for Δ*≤2):
  * the FIRST vertex has back-degree d⁻ (needs d⁻ ≤ 2),
  * the LAST  vertex has back-degree d⁺ (needs d⁺ ≤ 2).

Candidates tested:
  (A) in-degree-sorted order attains max-back-degree ≤ 2
      (Bessy et al.'s 3-approx order; test if it is *exact* for k=2).
  (B) Hall-feasibility of the radius-2 score windows ⟺ Δ*≤2
      (Hall is necessary by the score-window lemma; is it sufficient?).
"""
from __future__ import annotations

import itertools
import random
from typing import Sequence

from degreewidth_exact import degreewidth, is_degreewidth_le2, _masks


def indegrees(T):
    n = len(T)
    return [sum(1 for u in range(n) if T[u][v]) for v in range(n)]


def max_backdeg_order(T, order):
    n = len(T)
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i
    deg = [0] * n
    for u in range(n):
        for v in range(n):
            if T[u][v] and pos[u] > pos[v]:
                deg[u] += 1
                deg[v] += 1
    return max(deg) if n else 0


def indegree_sort_backdeg(T):
    """max-back-degree of the (ascending in-degree) order, ties by index."""
    n = len(T)
    di = indegrees(T)
    order = sorted(range(n), key=lambda v: (di[v], v))
    return max_backdeg_order(T, order)


def hall_feasible_windows(T, radius=2):
    """Is the radius-`radius` window system [d⁻-r, d⁻+r] schedulable into
    distinct positions 0..n-1?  Greedy earliest-deadline assignment."""
    n = len(T)
    di = indegrees(T)
    windows = [(max(0, di[v] - radius), min(n - 1, di[v] + radius)) for v in range(n)]
    # assign positions: sort vertices by right endpoint, give smallest free
    # position >= left endpoint.
    used = [False] * n
    for lo, hi in sorted(windows, key=lambda w: (w[1], w[0])):
        p = lo
        while p <= hi and used[p]:
            p += 1
        if p > hi:
            return False
        used[p] = True
    return True


def all_tournaments(n):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for bits in itertools.product((0, 1), repeat=len(pairs)):
        T = [[0] * n for _ in range(n)]
        for (i, j), b in zip(pairs, bits):
            if b:
                T[i][j] = 1
            else:
                T[j][i] = 1
        yield T


def random_tournament(n, rng):
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < 0.5:
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


def run(T, agg):
    dw2 = is_degreewidth_le2(T)
    agg["n"] += 1
    # (A) in-degree sort exactness
    a_ok = indegree_sort_backdeg(T) <= 2
    if a_ok and not dw2:
        agg["A_false_pos"] += 1  # impossible (order is a real witness) -> sanity
    if dw2 and not a_ok:
        agg["A_misses"] += 1  # Δ*≤2 but in-degree sort fails -> A not exact
    # (B) Hall ⟺ Δ*≤2
    hall = hall_feasible_windows(T)
    if dw2 and not hall:
        agg["B_dw2_not_hall"] += 1  # would refute necessity (should be 0)
    if hall and not dw2:
        agg["B_hall_not_dw2"] += 1  # Hall insufficient (the interesting count)


def main():
    rng = random.Random(20260530)
    print("=== Q1 candidate-characterization probe ===")
    # exhaustive small n
    for n in range(2, 8):
        agg = dict(n=0, A_misses=0, A_false_pos=0, B_dw2_not_hall=0, B_hall_not_dw2=0)
        src = all_tournaments(n) if n <= 6 else (random_tournament(n, rng) for _ in range(20000))
        tag = "exhaustive" if n <= 6 else "random 20000"
        for T in src:
            run(T, agg)
        print(f" n={n} ({tag}): {agg['n']} | "
              f"(A) in-deg-sort misses Δ*≤2: {agg['A_misses']} | "
              f"(B) Hall-but-Δ*>2: {agg['B_hall_not_dw2']} | "
              f"Δ*≤2-but-not-Hall: {agg['B_dw2_not_hall']} (must be 0)")
    # larger random
    for n in (8, 9, 10, 12):
        agg = dict(n=0, A_misses=0, A_false_pos=0, B_dw2_not_hall=0, B_hall_not_dw2=0)
        for _ in range(3000):
            run(random_tournament(n, rng), agg)
        print(f" n={n} (random 3000): {agg['n']} | "
              f"(A) misses: {agg['A_misses']} | (B) Hall-but-Δ*>2: {agg['B_hall_not_dw2']} | "
              f"Δ*≤2-but-not-Hall: {agg['B_dw2_not_hall']}")


if __name__ == "__main__":
    main()
