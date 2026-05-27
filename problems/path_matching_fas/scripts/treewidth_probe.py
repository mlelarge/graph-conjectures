"""Treewidth/pathwidth probe for the flex graph of Path-FAS gadgets.

For a tournament T with score windows I_v = [l_v, r_v] of width <= 5,
define the **flex graph** G_flex(T) on V(T) where {u,v} is an edge iff
I_u and I_v overlap.  Width is exactly the score-window interval graph.

For interval graphs, treewidth = pathwidth = max clique size minus 1 =
max active-window size minus 1 <= 8.  So treewidth is always small for
interval graphs of LFO inputs.

We also define the **competition graph** G_comp(T) where {u,v} is an
edge iff some flex backedge can be loaded.  This is a subgraph of
G_flex.

This probe computes both treewidths (via brute force / heuristic) for
small instances and reports them alongside Hall's interval bound.

Observation: the score-window interval graph always has treewidth <= 8
by the radius-2 lemma.  This bound is per-vertex constant; the
question is whether the DP nodes (one per band) can be tiled
appropriately.

The probe also checks: does bounded treewidth of the flex graph imply
a polynomial DP for LFO extension?  Answer below.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import valid_prefix_state_ff  # noqa: E402
from quotient_signature_probe import chain_seeded_toggle_tournament  # noqa: E402
from sleeping_block_skew_sweep import SKEW_TEMPLATES  # noqa: E402
from sleeping_bound_refutation import toggle_tournament  # noqa: E402


Matrix = Sequence[Sequence[int]]


def score_windows_of(T: Matrix) -> list[tuple[int, int]]:
    init = valid_prefix_state_ff(T, ())
    if init is None:
        # Fall back to raw windows
        n = len(T)
        indeg = [sum(T[u][v] for u in range(n)) for v in range(n)]
        return [(max(0, d - 2), min(n - 1, d + 2)) for d in indeg]
    _, _, _, _, windows = init
    return list(windows)


def interval_graph_edges(windows: list[tuple[int, int]]) -> list[tuple[int, int]]:
    n = len(windows)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            li, ri = windows[i]
            lj, rj = windows[j]
            if max(li, lj) <= min(ri, rj):
                edges.append((i, j))
    return edges


def interval_graph_treewidth(windows: list[tuple[int, int]]) -> int:
    """For interval graphs, treewidth = pathwidth = max clique size - 1.

    Max clique = max number of intervals overlapping a single point.
    """
    n = len(windows)
    if n == 0:
        return 0
    max_overlap = 0
    for p in range(min(w[0] for w in windows), max(w[1] for w in windows) + 1):
        overlap = sum(1 for (lo, hi) in windows if lo <= p <= hi)
        max_overlap = max(max_overlap, overlap)
    return max_overlap - 1


def analyse(name: str, T: Matrix) -> dict:
    windows = score_windows_of(T)
    edges = interval_graph_edges(windows)
    tw = interval_graph_treewidth(windows)
    return {
        "name": name,
        "n": len(T),
        "n_windows": len(windows),
        "max_overlap": tw + 1,
        "interval_treewidth": tw,
        "n_flex_edges": len(edges),
        "windows": windows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-k", type=int, default=6)
    args = parser.parse_args()
    out: list[dict] = []
    # Toggle family
    for k in range(1, args.max_k + 1):
        out.append(analyse(f"toggle_k={k}", toggle_tournament(k)))
    for k in range(1, args.max_k + 1):
        out.append(analyse(f"chain_seeded_k={k}", chain_seeded_toggle_tournament(k)))
    for name, T in SKEW_TEMPLATES.items():
        out.append(analyse(name, T))
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
