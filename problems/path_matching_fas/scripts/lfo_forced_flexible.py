"""Exact LFO solver using the forced/flexible score-window split.

This is still an exact backtracking solver, not the final polynomial DP.
It implements the reformulation:

1. Preload every backedge whose endpoints have disjoint score windows.
2. Search only over the relative order of overlapping-window pairs.

The point is to make the future DP target executable: the fixed forced
linear forest is separated from the bounded-clique interval-choice part.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lfo_score_window import hall_interval_ok, score_windows  # noqa: E402
from score_window_forced import forced_order  # noqa: E402


Matrix = Sequence[Sequence[int]]


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


def _initial_forced_state(
    T: Matrix,
    windows: Sequence[tuple[int, int]],
) -> tuple[tuple[int, ...], tuple[int, ...], list[int], str | None]:
    """Return degree/parent/flexible-outmasks after loading forced backedges."""
    n = len(T)
    degree = [0] * n
    parent = list(range(n))
    flex_outmask = [0] * n

    for u in range(n):
        for v in range(u + 1, n):
            fixed = forced_order(windows, u, v)
            if fixed is None:
                if T[u][v]:
                    flex_outmask[u] |= 1 << v
                else:
                    flex_outmask[v] |= 1 << u
                continue
            earlier, later = fixed
            if not T[later][earlier]:
                continue
            if degree[later] >= 2 or degree[earlier] >= 2:
                return tuple(degree), tuple(parent), flex_outmask, "forced_degree"
            if _find(parent, later) == _find(parent, earlier):
                return tuple(degree), tuple(parent), flex_outmask, "forced_cycle"
            degree[later] += 1
            degree[earlier] += 1
            _union(parent, later, earlier)
    return tuple(degree), tuple(parent), flex_outmask, None


def _forced_future_ok_flexible(
    flex_outmask: Sequence[int],
    prefix_mask: int,
    remaining_mask: int,
    degree: tuple[int, ...],
    parent: tuple[int, ...],
) -> tuple[bool, str | None]:
    par = list(parent)

    for p in _iter_bits(prefix_mask):
        future_load = sum(1 for x in _iter_bits(remaining_mask) if flex_outmask[x] & (1 << p))
        if degree[p] + future_load > 2:
            return False, "forced_degree"

    for x in _iter_bits(remaining_mask):
        forced_neighbors = [p for p in _iter_bits(flex_outmask[x] & prefix_mask)]
        if len(forced_neighbors) + degree[x] > 2:
            return False, "forced_degree"
        for i, a in enumerate(forced_neighbors):
            for b in forced_neighbors[i + 1:]:
                if _find(par, a) == _find(par, b):
                    return False, "forced_cycle"
        for p in forced_neighbors:
            if _find(par, x) == _find(par, p):
                return False, "forced_cycle"
    return True, None


def find_lfo_order_forced_flexible(T: Matrix, radius: int = 2, use_hall: bool = True) -> dict:
    """Return an exact LFO decision result using forced/flexible splitting."""
    n = len(T)
    windows = score_windows(T, radius)
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
        "forced_initial_obstruction": None,
    }

    if use_hall and not hall_interval_ok((1 << n) - 1, 0, windows, n):
        return {
            "found": False,
            "order": None,
            "windows": windows,
            "initial_hall": False,
            **stats,
        }

    degree0, parent0, flex_outmask, obstruction = _initial_forced_state(T, windows)
    if obstruction is not None:
        stats["forced_initial_obstruction"] = obstruction
        return {
            "found": False,
            "order": None,
            "windows": windows,
            "initial_hall": True,
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

        ok, reason = _forced_future_ok_flexible(
            flex_outmask,
            prefix_mask,
            remaining_mask,
            degree,
            parent,
        )
        if not ok:
            if reason == "forced_cycle":
                stats["pruned_forced_cycle"] += 1
            else:
                stats["pruned_forced_degree"] += 1
            return None

        candidates = sorted(
            frontier,
            key=lambda x: (
                (flex_outmask[x] & prefix_mask).bit_count(),
                -windows[x][1],
            ),
            reverse=True,
        )
        stats["max_candidates"] = max(stats["max_candidates"], len(candidates))

        for x in candidates:
            deg = list(degree)
            par = list(parent)
            ok = True
            for p in _iter_bits(flex_outmask[x] & prefix_mask):
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

    order = rec(0, 0, (1 << n) - 1, degree0, parent0, tuple())
    return {
        "found": order is not None,
        "order": list(order) if order is not None else None,
        "windows": windows,
        "initial_hall": True,
        **stats,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--T", required=True, help="Tournament as a JSON matrix")
    args = parser.parse_args()
    print(json.dumps(find_lfo_order_forced_flexible(json.loads(args.T)), indent=2))


if __name__ == "__main__":
    main()

