"""Q1: count REACHABLE prefixes of the Δ*≤2 forward DP, and test poly growth.

A prefix is a subset S that can be linearly arranged so every vertex of S
has back-degree ≤ 2.  Reachability BFS (process by increasing |S|):
  reach(∅);  S∪{u} reachable from reachable S iff
  bd(u|S) = 2·|N⁺(u)∩S| + d⁻(u) − |S| ≤ 2.
Δ*(T) ≤ 2 iff the full set V is reachable.  The BFS *is* the candidate
polynomial recognizer — its cost is (#reachable prefixes)·n.  So:

    Q1-poly conjecture: #reachable prefixes = poly(n) for every tournament.

This module counts them, tracks per-size width, and stress-tests growth on
constructed YES instances (which need no Δ* verification: the construction
order itself has max back-degree ≤ 2).
"""
from __future__ import annotations

import random
from collections import defaultdict


def masks(T):
    n = len(T)
    outmask = [0] * n
    dminus = [0] * n
    for u in range(n):
        for v in range(n):
            if u != v and T[u][v]:
                outmask[u] |= 1 << v
    for v in range(n):
        dminus[v] = sum(1 for u in range(n) if u != v and T[u][v])
    return outmask, dminus


def reachable_stats(T):
    """Return (total_reachable, max_per_size, full_reachable?)."""
    n = len(T)
    outmask, dminus = masks(T)
    frontier = {0}
    total = 1
    max_per_size = 1
    full = (1 << n) - 1
    full_reached = (n == 0)
    for p in range(n):
        nxt = set()
        for S in frontier:
            for u in range(n):
                bit = 1 << u
                if S & bit:
                    continue
                c = bin(outmask[u] & S).count("1")
                if 2 * c + dminus[u] - p <= 2:
                    nxt.add(S | bit)
        if not nxt:
            break
        total += len(nxt)
        max_per_size = max(max_per_size, len(nxt))
        if full in nxt:
            full_reached = True
        frontier = nxt
    return total, max_per_size, full_reached


def construct_yes(n, rng, pdense):
    """Random order + a max-degree-≤2 back-arc set ⇒ guaranteed Δ*≤2."""
    perm = list(range(n))
    rng.shuffle(perm)
    deg = defaultdict(int)
    back = set()
    pairs = [(perm[i], perm[j]) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    for a, b in pairs:  # a earlier than b in the order
        if deg[a] < 2 and deg[b] < 2 and rng.random() < pdense:
            back.add((b, a))
            deg[a] += 1
            deg[b] += 1
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            a, b = perm[i], perm[j]
            if (b, a) in back:
                T[b][a] = 1
            else:
                T[a][b] = 1
    return T


def main():
    rng = random.Random(20260531)
    print("=== #reachable prefixes of the Δ*≤2 forward DP, constructed YES ===")
    print("(if poly, this BFS is a poly recognizer; 2^Ω(n) would explode)")
    for n in (10, 15, 20, 25, 30, 40, 50, 60):
        best_total = 0
        best_max = 0
        n_full = 0
        samples = 300 if n <= 30 else (120 if n <= 50 else 60)
        for _ in range(samples):
            T = construct_yes(n, rng, pdense=0.97)
            total, mx, full = reachable_stats(T)
            best_total = max(best_total, total)
            best_max = max(best_max, mx)
            n_full += full
        print(f" n={n:3d}: MAX total reachable={best_total:6d} | "
              f"MAX per-size width={best_max:5d} | "
              f"full-reached {n_full}/{samples} | "
              f"total/n²={best_total/n/n:.2f} total/n³={best_total/n**3:.4f}")


if __name__ == "__main__":
    main()
