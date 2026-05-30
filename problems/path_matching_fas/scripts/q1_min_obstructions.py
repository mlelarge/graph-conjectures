"""Q1: mine vertex-minimal Δ*=3 obstructions for tournaments.

A tournament T is a *vertex-minimal degreewidth-3 obstruction* if
Δ*(T) >= 3 but Δ*(T - v) <= 2 for every vertex v.  If these are finite (or
of bounded size, or have bounded structure), Δ*<=2 has a finite forbidden
list / poly recognition.
"""
from __future__ import annotations

import itertools
import sys
from collections import Counter

from degreewidth_exact import degreewidth_le


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


def delete_vertex(T, v):
    n = len(T)
    keep = [u for u in range(n) if u != v]
    return [[T[a][b] for b in keep] for a in keep]


def canon_key(T):
    n = len(T)
    best = None
    for p in itertools.permutations(range(n)):
        bits = tuple(T[p[i]][p[j]] for i in range(n) for j in range(n) if i != j)
        if best is None or bits < best:
            best = bits
    return best


def score_seq(T):
    n = len(T)
    return tuple(sorted(sum(T[u][v] for v in range(n)) for u in range(n)))


def main():
    for n in range(4, 8):
        cnt_dw3 = 0
        minimal = []
        seen = set()
        for T in all_tournaments(n):
            if degreewidth_le(T, 2):
                continue
            cnt_dw3 += 1  # Δ* >= 3
            if all(degreewidth_le(delete_vertex(T, v), 2) for v in range(n)):
                k = canon_key(T)
                if k not in seen:
                    seen.add(k)
                    minimal.append(T)
        print(f"n={n}: #labeled Δ*>=3 = {cnt_dw3}; "
              f"#vertex-minimal (up to iso) = {len(minimal)}", flush=True)
        sc = Counter(score_seq(T) for T in minimal)
        for s, c in sorted(sc.items()):
            print(f"    score-seq {s}: {c}", flush=True)


if __name__ == "__main__":
    main()
