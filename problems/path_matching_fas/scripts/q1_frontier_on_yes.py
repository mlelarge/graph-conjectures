"""Q1: frontier size measured on YES (Δ*<=2) instances specifically.

Random tournaments are almost all NO at moderate n, so the forward DP dies
fast and the reachable-state count is misleadingly tiny.  The hard regime
is YES instances (especially near-regular ones).  Here we:
  * enumerate ALL Δ*<=2 tournaments at n=7,8 and measure the true max
    reachable-state count and max active-frontier (# unplaced u with c>0);
  * also probe near-regular / quadratic-residue (Paley) YES tournaments.
"""
from __future__ import annotations

import itertools
import random
from collections import defaultdict

from degreewidth_exact import _masks, is_degreewidth_le2


def reachable_states(T, k=2):
    n = len(T)
    outmask, inmask, dminus = _masks(T)
    by_size = defaultdict(set)
    by_size[0].add(0)
    frontier = {0}
    for p in range(n):
        nxt = set()
        for S in frontier:
            for u in range(n):
                if (S >> u) & 1:
                    continue
                c = bin(outmask[u] & S).count("1")
                if 2 * c + dminus[u] - p <= k:
                    nxt.add(S | (1 << u))
        by_size[p + 1] |= nxt
        frontier = nxt
    return by_size, outmask, dminus


def stats(T):
    bs, outmask, dminus = reachable_states(T)
    n = len(T)
    max_states = 0
    max_active = 0
    max_distinct_prof = 0
    for p, Ss in bs.items():
        if not Ss:
            continue
        max_states = max(max_states, len(Ss))
        profs = set()
        for S in Ss:
            prof = []
            for u in range(n):
                if (S >> u) & 1:
                    continue
                c = bin(outmask[u] & S).count("1")
                if c > 0:
                    prof.append(c)
            max_active = max(max_active, len(prof))
            profs.add(tuple(sorted(prof)))
        max_distinct_prof = max(max_distinct_prof, len(profs))
    return max_states, max_active, max_distinct_prof


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


def rotational(n, jumps):
    """Circulant tournament: i->j if (j-i mod n) in jumps."""
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for d in jumps:
            T[i][(i + d) % n] = 1
    return T


def main():
    import sys
    print("=== near-regular circulant (rotational) YES instances ===", flush=True)
    for n in range(7, 30, 2):
        jumps = list(range(1, (n // 2) + 1))
        T = rotational(n, jumps)
        yes = is_degreewidth_le2(T)
        if yes:
            a, b, c = stats(T)
            print(f" n={n} regular circulant: YES | reachable-S/size={a} | "
                  f"active-frontier={b} | distinct profiles={c}", flush=True)
        else:
            print(f" n={n} regular circulant: NO (Δ*>=3)", flush=True)

    print("=== frontier on YES (Δ*<=2) instances, exhaustive n=7 ===", flush=True)
    for n in (7,):
        ms = ma = mp = 0
        cnt = 0
        for T in all_tournaments(n):
            if not is_degreewidth_le2(T):
                continue
            cnt += 1
            a, b, c = stats(T)
            ms = max(ms, a); ma = max(ma, b); mp = max(mp, c)
        print(f" n={n}: {cnt} YES | max reachable-S/size={ms} | "
              f"max active-frontier={ma} | max distinct profiles/size={mp}", flush=True)
    return

    print("=== near-regular circulant (rotational) YES instances ===")
    for n in range(7, 22, 2):
        jumps = list(range(1, (n // 2) + 1))  # i -> i+1..i+n/2 : regular tournament
        T = rotational(n, jumps)
        yes = is_degreewidth_le2(T)
        if yes:
            a, b, c = stats(T)
            print(f" n={n} regular circulant: YES | reachable-S/size={a} | "
                  f"active-frontier={b} | distinct profiles={c}")
        else:
            print(f" n={n} regular circulant: NO (Δ*>=3)")


if __name__ == "__main__":
    main()
