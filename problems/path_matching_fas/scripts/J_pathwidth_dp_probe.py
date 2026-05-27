"""Direct correctness probe for the J-pathwidth DP.

Compares `path_fas_J_pathwidth_dp` against `decide_path_fas_bruteforce`
across exhaustive small n and random samples at n in {7, 8, 9}.  Prints
progress and any mismatch.
"""
from __future__ import annotations

import itertools
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from J_pathwidth_dp import (  # noqa: E402
    J_graph,
    nice_path_decomposition,
    path_fas_J_pathwidth_dp,
)
from path_fas import decide_path_fas_bruteforce  # noqa: E402


def all_tournaments(n: int):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for bits in itertools.product([0, 1], repeat=len(pairs)):
        T = [[0] * n for _ in range(n)]
        for (i, j), b in zip(pairs, bits):
            if b:
                T[i][j] = 1
            else:
                T[j][i] = 1
        yield T


def random_tournament(n: int, rng: random.Random):
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < 0.5:
                T[i][j] = 1
            else:
                T[j][i] = 1
    return T


def probe(n: int, count: int | None, seed: int = 20260527, exhaustive: bool = False):
    if exhaustive:
        gen = all_tournaments(n)
        label = "exhaustive"
    else:
        rng = random.Random(seed)
        gen = (random_tournament(n, rng) for _ in range(count))
        label = f"{count} random"
    t0 = time.time()
    total = 0
    mismatches = []
    for T in gen:
        total += 1
        dp = path_fas_J_pathwidth_dp(T)
        bf = decide_path_fas_bruteforce(T)["found"]
        if dp != bf:
            mismatches.append((total, T, dp, bf))
            print(f"  MISMATCH at sample {total}: DP={dp} BF={bf}")
            print(f"    T = {T}")
            if len(mismatches) >= 3:
                break
    dt = time.time() - t0
    print(f"n={n} ({label}): total={total} mismatches={len(mismatches)} time={dt:.1f}s")
    return mismatches


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=7)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--exhaustive", action="store_true")
    args = parser.parse_args()
    probe(args.n, args.count, exhaustive=args.exhaustive)
