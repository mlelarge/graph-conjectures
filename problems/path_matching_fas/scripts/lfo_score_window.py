"""Score-window exact solver for linear-forest orderings.

If an order has backdegree at most 2 at every vertex, then every vertex
v lies within distance 2 of its indegree:

    |pos(v) - d^-(v)| <= 2.

This script turns that necessary condition into an exact branch-and-prune
solver. It is not yet a polynomial algorithm, but it exposes the right
state space for a possible bounded-frontier DP.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


Matrix = Sequence[Sequence[int]]


def indegrees(T: Matrix) -> list[int]:
    n = len(T)
    return [sum(T[u][v] for u in range(n)) for v in range(n)]


def score_windows(T: Matrix, radius: int = 2) -> list[tuple[int, int]]:
    """Return allowed position intervals forced by max backdegree <= radius."""
    n = len(T)
    return [
        (max(0, d - radius), min(n - 1, d + radius))
        for d in indegrees(T)
    ]


def order_respects_windows(order: Sequence[int], windows: Sequence[tuple[int, int]]) -> bool:
    pos = [0] * len(order)
    for i, v in enumerate(order):
        pos[v] = i
    return all(lo <= pos[v] <= hi for v, (lo, hi) in enumerate(windows))


def _find(parent: list[int], x: int) -> int:
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def _union(parent: list[int], a: int, b: int) -> None:
    ra = _find(parent, a)
    rb = _find(parent, b)
    if ra != rb:
        parent[rb] = ra


def _iter_bits(mask: int):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def hall_interval_ok(
    remaining_mask: int,
    next_pos: int,
    windows: Sequence[tuple[int, int]],
    n: int,
) -> bool:
    """Hall check for assigning remaining vertices to remaining positions.

    The domains are intervals, so it is enough to check all intervals of
    positions. Windows are clipped to the still-unfilled suffix.
    """
    if remaining_mask == 0:
        return True
    clipped: list[tuple[int, int]] = []
    for v in _iter_bits(remaining_mask):
        lo, hi = windows[v]
        lo = max(lo, next_pos)
        if lo > hi:
            return False
        clipped.append((lo, hi))

    for left in range(next_pos, n):
        for right in range(left, n):
            forced = sum(1 for lo, hi in clipped if left <= lo and hi <= right)
            if forced > right - left + 1:
                return False
    return True


def _forced_future_ok(
    T: Matrix,
    prefix_mask: int,
    remaining_mask: int,
    degree: tuple[int, ...],
    parent: tuple[int, ...],
) -> tuple[bool, str | None]:
    """Check unavoidable future backedges against degree and cycle constraints."""
    n = len(T)
    par = list(parent)

    for p in _iter_bits(prefix_mask):
        future_load = sum(1 for x in _iter_bits(remaining_mask) if T[x][p])
        if degree[p] + future_load > 2:
            return False, "forced_degree"

    for x in _iter_bits(remaining_mask):
        forced_neighbors = [p for p in _iter_bits(prefix_mask) if T[x][p]]
        if len(forced_neighbors) > 2:
            return False, "forced_degree"
        if len(forced_neighbors) == 2:
            if _find(par, forced_neighbors[0]) == _find(par, forced_neighbors[1]):
                return False, "forced_cycle"
    return True, None


def find_lfo_order_score_window(T: Matrix, radius: int = 2, use_hall: bool = True) -> dict:
    """Return an exact LFO decision result using score-window pruning."""
    n = len(T)
    windows = score_windows(T, radius)
    outmask = [
        sum((1 << v) for v in range(n) if T[u][v])
        for u in range(n)
    ]
    stats = {
        "nodes": 0,
        "pruned_no_window_candidate": 0,
        "pruned_hall": 0,
        "pruned_forced_degree": 0,
        "pruned_forced_cycle": 0,
        "pruned_degree": 0,
        "pruned_cycle": 0,
        "max_frontier": 0,
        "max_candidates": 0,
    }

    if use_hall and not hall_interval_ok((1 << n) - 1, 0, windows, n):
        return {
            "found": False,
            "order": None,
            "windows": windows,
            "initial_hall": False,
            **stats,
        }

    def rec(
        pos: int,
        prefix_mask: int,
        remaining_mask: int,
        degree: tuple[int, ...],
        parent: tuple[int, ...],
        order: tuple[int, ...],
    ) -> tuple[int, ...] | None:
        stats["nodes"] += 1
        if remaining_mask == 0:
            return order

        frontier = [
            v for v in _iter_bits(remaining_mask)
            if windows[v][0] <= pos <= windows[v][1]
        ]
        stats["max_frontier"] = max(stats["max_frontier"], len(frontier))

        if not frontier:
            stats["pruned_no_window_candidate"] += 1
            return None

        if use_hall and not hall_interval_ok(remaining_mask, pos, windows, n):
            stats["pruned_hall"] += 1
            return None

        ok, reason = _forced_future_ok(T, prefix_mask, remaining_mask, degree, parent)
        if not ok:
            if reason == "forced_cycle":
                stats["pruned_forced_cycle"] += 1
            else:
                stats["pruned_forced_degree"] += 1
            return None

        candidates = sorted(
            frontier,
            key=lambda x: (
                (outmask[x] & prefix_mask).bit_count(),
                -windows[x][1],
            ),
            reverse=True,
        )
        stats["max_candidates"] = max(stats["max_candidates"], len(candidates))

        for x in candidates:
            deg = list(degree)
            par = list(parent)
            ok = True
            for p in _iter_bits(outmask[x] & prefix_mask):
                if deg[x] >= 2 or deg[p] >= 2:
                    stats["pruned_degree"] += 1
                    ok = False
                    break
                if _find(par, x) == _find(par, p):
                    stats["pruned_cycle"] += 1
                    ok = False
                    break
                deg[x] += 1
                deg[p] += 1
                _union(par, x, p)
            if not ok:
                continue
            out = rec(
                pos + 1,
                prefix_mask | (1 << x),
                remaining_mask ^ (1 << x),
                tuple(deg),
                tuple(par),
                order + (x,),
            )
            if out is not None:
                return out
        return None

    order = rec(0, 0, (1 << n) - 1, tuple([0] * n), tuple(range(n)), tuple())
    return {
        "found": order is not None,
        "order": list(order) if order is not None else None,
        "windows": windows,
        "initial_hall": True,
        **stats,
    }


def window_profile(T: Matrix) -> dict:
    windows = score_windows(T)
    widths = [hi - lo + 1 for lo, hi in windows]
    n = len(T)
    active_by_pos = [
        sum(1 for lo, hi in windows if lo <= p <= hi)
        for p in range(n)
    ]
    return {
        "n": n,
        "indegrees": indegrees(T),
        "windows": windows,
        "widths": widths,
        "max_width": max(widths) if widths else 0,
        "active_by_pos": active_by_pos,
        "max_active": max(active_by_pos) if active_by_pos else 0,
        "initial_hall": hall_interval_ok((1 << n) - 1, 0, windows, n),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--T", help="Tournament as a JSON matrix")
    parser.add_argument("--profile", action="store_true")
    args = parser.parse_args()

    if not args.T:
        parser.error("--T is required")
    T = json.loads(args.T)
    out = window_profile(T) if args.profile else find_lfo_order_score_window(T)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
