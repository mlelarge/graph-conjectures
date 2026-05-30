"""Q1: frontier analysis & a bounded-state DP attempt for Δ*<=2.

CLEAN PLACEMENT IDENTITY (derived, verified here).  Append vertex u to a
prefix occupying set S (|S| = current position p = |S|).  In a tournament,
among the placed set S the vertex u sees outS(u) out-neighbours and
inS(u) = |S| - outS(u) in-neighbours.  Its FINAL back-degree (fixed at
placement) is

    bd(u | S) = outS(u) + (d^-(u) - inS(u))
              = outS(u) + d^-(u) - (|S| - outS(u))
              = 2*outS(u) + d^-(u) - |S|.

So bd(u|S) <= 2  <=>  outS(u) <= (2 + |S| - d^-(u)) / 2.

outS(u) = number of u's OUT-neighbours already placed = number of back-arcs
u accrues (arcs u->w, w earlier).  It only grows as S grows.

This file:
  (1) verifies bd(u|S) = 2*outS(u)+d^-(u)-|S| against the exact masks DP;
  (2) tests whether the Δ*<=2 reachability DP state can be COMPRESSED:
      does reach[S] depend only on a bounded-size summary of S?
"""
from __future__ import annotations

import itertools
import random

from degreewidth_exact import _masks, is_degreewidth_le2, degreewidth_le


def verify_identity(T):
    n = len(T)
    outmask, inmask, dminus = _masks(T)
    for _ in range(200):
        # random subset S and a vertex u not in S
        verts = list(range(n))
        random.shuffle(verts)
        cut = random.randint(0, n - 1)
        Sset = verts[:cut]
        S = 0
        for w in Sset:
            S |= 1 << w
        rest = [w for w in range(n) if not (S >> w) & 1]
        if not rest:
            continue
        u = random.choice(rest)
        before_in = bin(inmask[u] & S).count("1")
        bd_solver = bin(outmask[u] & S).count("1") + (dminus[u] - before_in)
        outS = bin(outmask[u] & S).count("1")
        bd_formula = 2 * outS + dminus[u] - bin(S).count("1")
        if bd_solver != bd_formula:
            return False
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


def main():
    rng = random.Random(1)
    ok = all(verify_identity(random_tournament(n, rng)) for n in range(2, 12) for _ in range(50))
    print("placement identity bd(u|S)=2*outS(u)+d^-(u)-|S| holds on samples:", ok)


if __name__ == "__main__":
    main()
