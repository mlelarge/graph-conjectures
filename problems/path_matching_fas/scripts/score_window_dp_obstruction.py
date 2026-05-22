"""Obstructions to the naive score-window frontier DP.

The score-window lemma gives every LFO vertex a constant-width position
window. Hall feasibility then bounds the number of simultaneously active
windows. That does not mean a DP can remember only the active vertices:
valid LFOs can have arbitrarily many already-placed vertices with
obligations to far-future vertices.

The basic witness is a transitive tournament with a reversed matching.
In the identity order its back-arc graph is exactly that matching, so it
is an LFO. At the middle cut all matching edges cross the cut.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lfo_score_window import hall_interval_ok, indegrees, score_windows, window_profile  # noqa: E402
from verify import verify  # noqa: E402


Matrix = Sequence[Sequence[int]]


def reversed_matching_tournament(m: int) -> list[list[int]]:
    """Return the 2m-vertex transitive tournament with m reversed pairs.

    Start from the transitive tournament in the identity order:
    i -> j iff i < j. Then reverse the pairs (r, m+r) for
    r = 0, ..., m-1.
    """
    if m < 1:
        raise ValueError("m must be positive")
    n = 2 * m
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = 1
    for r in range(m):
        T[r][m + r] = 0
        T[m + r][r] = 1
    return T


def crossing_backarcs(T: Matrix, order: Sequence[int], cut: int) -> list[tuple[int, int]]:
    """Return back-arcs crossing the cut after ``cut`` placed vertices."""
    pos = [0] * len(order)
    for i, v in enumerate(order):
        pos[v] = i
    return [
        (u, v)
        for (u, v) in verify(T, order)["arcs"]
        if (pos[u] < cut) != (pos[v] < cut)
    ]


def degree_quota_profile(T: Matrix, order: Sequence[int]) -> list[dict]:
    """Return the displacement/quota table for an order.

    For a vertex v at position i with indegree d, let delta=i-d. Let b be
    the number of earlier out-neighbors and f the number of later
    in-neighbors. These are precisely the past and future back-neighbors
    of v, so b+f is its backdegree.
    """
    n = len(T)
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i
    ds = indegrees(T)
    out = []
    for v in range(n):
        earlier = [u for u in range(n) if pos[u] < pos[v]]
        later = [u for u in range(n) if pos[u] > pos[v]]
        earlier_out = sum(1 for u in earlier if T[v][u])
        later_in = sum(1 for u in later if T[u][v])
        out.append({
            "vertex": v,
            "position": pos[v],
            "indegree": ds[v],
            "delta": pos[v] - ds[v],
            "earlier_out": earlier_out,
            "later_in": later_in,
            "backdegree": earlier_out + later_in,
        })
    return out


def hall_active_bound(windows: Sequence[tuple[int, int]], n: int, radius: int = 2) -> dict:
    """Return active-window data and the Hall-implied constant bound.

    If every window has width at most 2r+1 and Hall feasibility holds,
    then all windows active at position p are contained in
    [p-2r, p+2r], an interval of at most 4r+1 positions. Hall therefore
    bounds the active count at p by 4r+1.
    """
    active_by_pos = [
        sum(1 for lo, hi in windows if lo <= p <= hi)
        for p in range(n)
    ]
    return {
        "radius": radius,
        "hall_ok": hall_interval_ok((1 << n) - 1, 0, windows, n),
        "active_by_pos": active_by_pos,
        "max_active": max(active_by_pos) if active_by_pos else 0,
        "hall_bound": 4 * radius + 1,
    }


def analyze_reversed_matching(m: int) -> dict:
    T = reversed_matching_tournament(m)
    order = list(range(2 * m))
    info = verify(T, order)
    windows = score_windows(T)
    middle_crossing = crossing_backarcs(T, order, m)
    quotas = degree_quota_profile(T, order)
    return {
        "m": m,
        "n": 2 * m,
        "is_lfo": info["is_linear_forest"],
        "is_matching": info["is_matching"],
        "backarc_count": info["count"],
        "middle_crossing_backarc_count": len(middle_crossing),
        "middle_crossing_backarcs": middle_crossing,
        "max_abs_score_displacement": max(abs(q["delta"]) for q in quotas),
        "indegrees": indegrees(T),
        "windows": windows,
        "window_profile": window_profile(T),
        "hall_active_bound": hall_active_bound(windows, 2 * m),
        "degree_quota_profile": quotas,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--m", type=int, default=8)
    args = parser.parse_args()
    print(json.dumps(analyze_reversed_matching(args.m), indent=2))


if __name__ == "__main__":
    main()

