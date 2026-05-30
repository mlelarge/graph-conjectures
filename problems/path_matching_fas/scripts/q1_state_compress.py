"""Q1: does the Δ*<=2 reachability DP admit a poly-size state compression?

Forward construction.  Process positions left to right.  After placing a
prefix (set S, size p), the ONLY thing that matters for the future is, for
each UNPLACED vertex u, the count c(u) = |N^+(u) ∩ S| (out-neighbours of u
already placed = back-arcs u has accrued).  Placing u next (at position p)
is legal iff bd(u|S) = 2*c(u) + d^-(u) - p <= 2.

Claim to test: in any REACHABLE legal prefix, the number of unplaced
vertices with c(u) >= 1 is small / bounded, OR more strongly the multiset
of "active obligations" has poly many distinct values.  We instrument the
exact reachability DP and measure the true reachable-state structure.
"""
from __future__ import annotations

import itertools
import random
from collections import defaultdict

from degreewidth_exact import _masks


def reachable_states(T, k=2):
    """Return, per prefix-size p, the set of reachable S (legal so far)."""
    n = len(T)
    outmask, inmask, dminus = _masks(T)
    # reach via BFS over subsets, but record by size
    reach = {0}
    by_size = defaultdict(set)
    by_size[0].add(0)
    # process in increasing popcount
    frontier = {0}
    for p in range(n):
        nxt = set()
        for S in frontier:
            for u in range(n):
                if (S >> u) & 1:
                    continue
                c = bin(outmask[u] & S).count("1")
                bd = 2 * c + dminus[u] - p
                if bd <= k:
                    nxt.add(S | (1 << u))
        by_size[p + 1] |= nxt
        frontier = nxt
    return by_size


def active_profile(T, S):
    """For prefix S, the sorted tuple of c(u) for unplaced u with c(u)>0."""
    n = len(T)
    outmask, _, _ = _masks(T)
    prof = []
    for u in range(n):
        if (S >> u) & 1:
            continue
        c = bin(outmask[u] & S).count("1")
        if c > 0:
            prof.append(c)
    return tuple(sorted(prof))


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


def main():
    rng = random.Random(7)
    print("=== reachable-state structure of the k=2 forward DP ===")
    for n in (8, 10, 12, 13):
        max_states = 0
        max_active = 0  # max #unplaced with c>0 over reachable legal prefixes
        max_distinct_prof_per_size = 0
        samples = 200 if n <= 12 else 60
        for _ in range(samples):
            T = random_tournament(n, rng)
            bs = reachable_states(T)
            for p, Ss in bs.items():
                if not Ss:
                    continue
                max_states = max(max_states, len(Ss))
                profs = set()
                for S in Ss:
                    prof = active_profile(T, S)
                    max_active = max(max_active, len(prof))
                    profs.add(prof)
                max_distinct_prof_per_size = max(max_distinct_prof_per_size, len(profs))
        print(f" n={n}: max reachable-S per size = {max_states}; "
              f"max #active(c>0) unplaced = {max_active}; "
              f"max distinct active-profiles per size = {max_distinct_prof_per_size}")


if __name__ == "__main__":
    main()
