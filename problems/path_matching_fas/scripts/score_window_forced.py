"""Forced/flexible decomposition from score windows.

In any LFO order, vertex v must be placed inside its score window
[d^-(v)-2, d^-(v)+2]. If two windows are disjoint, their relative order
is fixed in every score-respecting order. Any backedge forced by such a
fixed pair can be added before doing any search.

The remaining undecided pairs have overlapping windows. Their interval
overlap graph has clique number at most 9 after Hall feasibility, so
this decomposition is the first plausible positive DP formulation after
the naive active-frontier state failed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lfo_score_window import hall_interval_ok, score_windows, window_profile  # noqa: E402
from verify import classify  # noqa: E402


Matrix = Sequence[Sequence[int]]


def forced_order(windows: Sequence[tuple[int, int]], u: int, v: int) -> tuple[int, int] | None:
    """Return the forced earlier/later pair if windows are disjoint."""
    lo_u, hi_u = windows[u]
    lo_v, hi_v = windows[v]
    if hi_u < lo_v:
        return u, v
    if hi_v < lo_u:
        return v, u
    return None


def forced_flexible_decomposition(T: Matrix, radius: int = 2) -> dict:
    """Return forced backedges and flexible overlapping-window pairs."""
    n = len(T)
    windows = score_windows(T, radius)
    forced_backedges: list[tuple[int, int]] = []
    forced_forward: list[tuple[int, int]] = []
    flexible_pairs: list[tuple[int, int]] = []

    for u in range(n):
        for v in range(u + 1, n):
            fixed = forced_order(windows, u, v)
            if fixed is None:
                flexible_pairs.append((u, v))
                continue
            earlier, later = fixed
            if T[later][earlier]:
                forced_backedges.append((later, earlier))
            else:
                forced_forward.append((earlier, later))

    forced_cls = classify(forced_backedges)
    profile = window_profile(T)
    return {
        "n": n,
        "windows": windows,
        "hall_ok": hall_interval_ok((1 << n) - 1, 0, windows, n),
        "max_active_windows": profile["max_active"],
        "forced_backedges": forced_backedges,
        "forced_backedge_count": len(forced_backedges),
        "forced_forward_count": len(forced_forward),
        "flexible_pairs": flexible_pairs,
        "flexible_pair_count": len(flexible_pairs),
        "forced_classification": forced_cls,
        "forced_linear_forest_ok": forced_cls["is_linear_forest"],
    }


def forced_obstruction(T: Matrix, radius: int = 2) -> str | None:
    """Return a necessary-condition failure reason, if one is immediate."""
    out = forced_flexible_decomposition(T, radius)
    if not out["hall_ok"]:
        return "score_window_hall"
    cls = out["forced_classification"]
    if cls["max_degree"] is not None and cls["max_degree"] > 2:
        return "forced_degree"
    if not cls["is_forest"]:
        return "forced_cycle"
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--T", required=True, help="Tournament as a JSON matrix")
    args = parser.parse_args()
    print(json.dumps(forced_flexible_decomposition(json.loads(args.T)), indent=2))


if __name__ == "__main__":
    main()

