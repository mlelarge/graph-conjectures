"""Bounded-reversal-distance hypothesis: when all reversed arcs are
within constant base-order distance, does the active-bag DP suffice?

For each tournament T:
  - max_reversal_distance = max{|u-v| : T[u][v] != base(u,v)}
  - we check whether T has any extendability collision under the
    active-bag signature.

The hypothesis is: max_reversal_distance <= w implies the active-bag
signature is sound for extendability, with state space O(n * (4w)^9).

Empirical test on small tournaments + the toggle/chain-seeded
families + skew templates.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import find_signature_collision  # noqa: E402
from quotient_signature_probe import chain_seeded_toggle_tournament  # noqa: E402
from sleeping_block_skew_sweep import SKEW_TEMPLATES  # noqa: E402
from sleeping_bound_refutation import toggle_tournament  # noqa: E402


Matrix = Sequence[Sequence[int]]


def max_reversal_distance(T: Matrix) -> int:
    """Max |i-j| over arcs whose orientation disagrees with base."""
    n = len(T)
    max_d = 0
    for i in range(n):
        for j in range(i + 1, n):
            # Base: i < j in base, so base arc is i->j (T[i][j]=1).
            if not T[i][j]:
                max_d = max(max_d, j - i)
    return max_d


def random_tournament(n: int, reversal_radius: int, rng: random.Random) -> Matrix:
    """Random tournament whose reversed arcs are within `radius` of base."""
    T = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if j - i > reversal_radius:
                T[i][j] = True
            else:
                if rng.random() < 0.5:
                    T[i][j] = True
                    T[j][i] = False
                else:
                    T[j][i] = True
                    T[i][j] = False
            if j - i > reversal_radius:
                T[j][i] = False
    return T


def collide(T: Matrix, depth: int) -> dict | None:
    return find_signature_collision(T, depth=depth, mode="active")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--n", type=int, default=10)
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20260527)
    args = parser.parse_args()
    rng = random.Random(args.seed)

    out: dict = {"samples": []}
    for radius in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        bad = 0
        total = 0
        for _ in range(args.samples):
            T = random_tournament(args.n, radius, rng)
            actual_d = max_reversal_distance(T)
            if actual_d != radius and actual_d > 0:
                # Best effort; many will be smaller than radius.
                pass
            col = collide(T, depth=args.depth)
            total += 1
            if col is not None:
                bad += 1
        out["samples"].append({
            "reversal_radius": radius,
            "n": args.n,
            "samples": total,
            "collisions": bad,
        })

    # Also tabulate radius of well-known instances
    instances = {
        "toggle_k=4": toggle_tournament(4),
        "toggle_k=5": toggle_tournament(5),
        "chain_seeded_k=3": chain_seeded_toggle_tournament(3),
        "chain_seeded_k=4": chain_seeded_toggle_tournament(4),
    }
    for name, T in SKEW_TEMPLATES.items():
        instances[name] = T
    instance_rows = []
    for name, T in instances.items():
        d = max_reversal_distance(T)
        col = collide(T, depth=args.depth)
        instance_rows.append({
            "name": name, "n": len(T),
            "max_rev_dist": d,
            "active_bag_collision": col is not None,
        })
    out["instances"] = instance_rows
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
