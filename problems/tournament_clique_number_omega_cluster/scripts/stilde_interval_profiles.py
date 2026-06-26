"""Interval profiles for the B_k layer-height recursion.

Prefix/suffix staircases are not closed under interleaving: a suffix of a parent
order can cut each child module at two different child positions when viewed
inside a larger parent interval.  The direct closure repair is to record all
contiguous interval heights

    I_c(i,j) = height of the backward colour-c poset on order positions [i,j).

For a fixed interleaving of three child orders this invariant is closed.  If
n_b(p) is the number of module-b vertices before parent position p, then for a
parent interval [p,q)

    I_c(parent; p,q) =
      max( I_c(child c+2; n_{c+2}(p), n_{c+2}(q)),
           max_{p <= r <= q} [
             I_c(child c;   n_c(r),     n_c(q))
           + I_c(child c+1; n_{c+1}(p), n_{c+1}(r)) ] )

This is the exact interval analogue of the crossing recursion.
"""

from __future__ import annotations

from dataclasses import dataclass

from stilde_profile_closure import lattice_path, module_orders, relation_matrix


@dataclass(frozen=True)
class IntervalProfile:
    depth: int
    order: tuple[int, ...]
    interval: tuple[tuple[tuple[int, ...], ...], ...]
    heights: tuple[int, int, int]


def _intervals_for_colour(order, depth, colour):
    n = len(order)
    relation = relation_matrix(depth, colour)
    matrix = [[0] * (n + 1) for _ in range(n + 1)]
    for start in range(n - 1, -1, -1):
        ranks = [0] * n
        height = 0
        for end in range(start + 1, n + 1):
            index = end - 1
            vertex = order[index]
            best = 1
            for previous in range(start, index):
                if relation[vertex][order[previous]]:
                    best = max(best, ranks[previous] + 1)
            ranks[index] = best
            height = max(height, best)
            matrix[start][end] = height
    return tuple(tuple(row) for row in matrix)


def interval_profile(order, depth):
    expected = 3**depth
    order = tuple(order)
    if sorted(order) != list(range(expected)):
        raise ValueError(f"order must be a permutation of range({expected})")
    intervals = tuple(
        _intervals_for_colour(order, depth, colour)
        for colour in range(3)
    )
    heights = tuple(intervals[colour][0][expected] for colour in range(3))
    return IntervalProfile(depth, order, intervals, heights)


def interval_closure_profile(order, depth):
    """Recompute the parent interval profile from child interval profiles."""

    if depth <= 0:
        raise ValueError("interval_closure_profile requires depth >= 1")
    n = 3**depth
    child_depth = depth - 1
    m = 3**child_depth
    modules = module_orders(order, depth)
    children = tuple(interval_profile(module, child_depth) for module in modules)
    states = lattice_path(order, depth)

    parent = []
    for colour in range(3):
        matrix = [[0] * (n + 1) for _ in range(n + 1)]
        for start in range(n):
            for end in range(start + 1, n + 1):
                lo = states[start]
                hi = states[end]
                far = children[(colour + 2) % 3].interval[colour][
                    lo[(colour + 2) % 3]
                ][
                    hi[(colour + 2) % 3]
                ]
                cross = 0
                for split in range(start, end + 1):
                    mid = states[split]
                    left = children[colour].interval[colour][
                        mid[colour]
                    ][
                        hi[colour]
                    ]
                    right = children[(colour + 1) % 3].interval[colour][
                        lo[(colour + 1) % 3]
                    ][
                        mid[(colour + 1) % 3]
                    ]
                    cross = max(cross, left + right)
                matrix[start][end] = max(far, cross)
        parent.append(tuple(tuple(row) for row in matrix))
    intervals = tuple(parent)
    heights = tuple(intervals[colour][0][m * 3] for colour in range(3))
    return IntervalProfile(depth, tuple(order), intervals, heights)


def prefix_suffix_from_interval(profile):
    n = len(profile.order)
    prefix = []
    suffix = []
    for colour in range(3):
        prefix.append(tuple(profile.interval[colour][0][j] for j in range(n + 1)))
        suffix.append(tuple(profile.interval[colour][n - j][n] for j in range(n + 1)))
    return tuple(prefix), tuple(suffix)


if __name__ == "__main__":
    import argparse
    import random

    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--samples", type=int, default=100)
    args = parser.parse_args()

    rng = random.Random(0)
    n = 3**args.depth
    seen = set()
    for _ in range(args.samples):
        order = list(range(n))
        rng.shuffle(order)
        prof = interval_profile(order, args.depth)
        seen.add(prof.interval)
    print(
        {
            "depth": args.depth,
            "samples": args.samples,
            "distinct_interval_profiles": len(seen),
        }
    )
