"""Cap-truncated interval-profile quotients.

The full interval profile I_c(i,j) is closed under interleaving but almost
order-level.  For a fixed cap triple h, the natural quotient clips each colour:

    J_c(i,j) = min(I_c(i,j), h_c + 1).

This preserves exactly the information needed to decide whether an interval
height exceeds its cap.  It is also closed: in the interval crossing formula,
any summand already above h_c can be treated as the absorbing value h_c+1.
"""

from __future__ import annotations

from dataclasses import dataclass

from stilde_interval_profiles import interval_closure_profile, interval_profile
from stilde_profile_closure import lattice_path, module_orders


@dataclass(frozen=True)
class ClippedIntervalProfile:
    depth: int
    caps: tuple[int, int, int]
    order: tuple[int, ...]
    interval: tuple[tuple[tuple[int, ...], ...], ...]
    heights: tuple[int, int, int]


def _clip_matrix(matrix, cap):
    limit = cap + 1
    return tuple(
        tuple(min(value, limit) for value in row)
        for row in matrix
    )


def clipped_interval_profile(order, depth, caps):
    caps = tuple(caps)
    full = interval_profile(order, depth)
    clipped = tuple(
        _clip_matrix(full.interval[colour], caps[colour])
        for colour in range(3)
    )
    n = len(full.order)
    return ClippedIntervalProfile(
        depth=depth,
        caps=caps,
        order=full.order,
        interval=clipped,
        heights=tuple(clipped[colour][0][n] for colour in range(3)),
    )


def clipped_interval_closure_profile(order, depth, caps):
    """Compute clipped parent intervals from clipped child intervals only."""

    caps = tuple(caps)
    if depth <= 0:
        raise ValueError("clipped_interval_closure_profile requires depth >= 1")
    n = 3**depth
    child_depth = depth - 1
    modules = module_orders(order, depth)
    children = tuple(
        clipped_interval_profile(module, child_depth, caps)
        for module in modules
    )
    states = lattice_path(order, depth)

    parent = []
    for colour in range(3):
        limit = caps[colour] + 1
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
                best = far
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
                    best = max(best, min(left + right, limit))
                    if best >= limit:
                        break
                matrix[start][end] = min(best, limit)
        parent.append(tuple(tuple(row) for row in matrix))
    interval = tuple(parent)
    return ClippedIntervalProfile(
        depth=depth,
        caps=caps,
        order=tuple(order),
        interval=interval,
        heights=tuple(interval[colour][0][n] for colour in range(3)),
    )


def clip_full_closure(order, depth, caps):
    """Reference: full interval closure, clipped after the fact."""

    caps = tuple(caps)
    full = interval_closure_profile(order, depth)
    clipped = tuple(
        _clip_matrix(full.interval[colour], caps[colour])
        for colour in range(3)
    )
    n = len(full.order)
    return ClippedIntervalProfile(
        depth=depth,
        caps=caps,
        order=full.order,
        interval=clipped,
        heights=tuple(clipped[colour][0][n] for colour in range(3)),
    )


if __name__ == "__main__":
    import argparse
    import random

    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--caps", type=int, nargs=3, default=(2, 2, 2))
    parser.add_argument("--samples", type=int, default=1000)
    args = parser.parse_args()

    rng = random.Random(0)
    n = 3**args.depth
    seen = set()
    for _ in range(args.samples):
        order = list(range(n))
        rng.shuffle(order)
        prof = clipped_interval_profile(order, args.depth, tuple(args.caps))
        seen.add(prof.interval)
    print(
        {
            "depth": args.depth,
            "caps": tuple(args.caps),
            "samples": args.samples,
            "distinct_clipped_interval_profiles": len(seen),
        }
    )
