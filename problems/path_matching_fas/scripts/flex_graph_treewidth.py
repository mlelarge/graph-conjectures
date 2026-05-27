"""Treewidth of the underlying flex graph (potential backedge graph).

The flex graph G_F(T) has an edge {u, v} iff (u, v) is a potential
flex backedge for some LFO; i.e., the windows of u and v overlap and
the tournament arc between them disagrees with the canonical (base)
order.

This is the graph whose components track via union-find through any
LFO.  If its pathwidth is bounded, then the back-arc component
partition at any prefix has at most O(B(k)) refinements per bag with
k = pathwidth, which is still exponential unless we use a connectivity
DP.

We compute treewidth (= pathwidth for chordal completions of interval
graphs) and pathwidth via a greedy heuristic.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ff_signature_probe import valid_prefix_state_ff  # noqa: E402
from lfo_forced_flexible import _iter_bits  # noqa: E402
from quotient_signature_probe import chain_seeded_toggle_tournament  # noqa: E402
from sleeping_block_skew_sweep import SKEW_TEMPLATES  # noqa: E402
from sleeping_bound_refutation import toggle_tournament  # noqa: E402


Matrix = Sequence[Sequence[int]]


def flex_graph_edges(T: Matrix) -> list[tuple[int, int]]:
    """Build the undirected flex graph: edges where flex-backedge possible."""
    init = valid_prefix_state_ff(T, ())
    if init is None:
        return []
    _, _, _, flex_outmask, _ = init
    n = len(T)
    edges: set[tuple[int, int]] = set()
    for x in range(n):
        for p in _iter_bits(flex_outmask[x]):
            edges.add(tuple(sorted((x, p))))
    return sorted(edges)


def min_degree_treewidth_heuristic(n: int, edges: list[tuple[int, int]]) -> int:
    """Greedy elimination by min-degree to upper bound treewidth."""
    adj: dict[int, set[int]] = {i: set() for i in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    tw_ub = 0
    remaining = set(range(n))
    while remaining:
        # Pick min-degree vertex
        u = min(remaining, key=lambda x: len(adj[x] & remaining))
        deg = len(adj[u] & remaining)
        tw_ub = max(tw_ub, deg)
        # Add clique on remaining neighbors
        nbrs = list(adj[u] & remaining)
        for i in range(len(nbrs)):
            for j in range(i + 1, len(nbrs)):
                adj[nbrs[i]].add(nbrs[j])
                adj[nbrs[j]].add(nbrs[i])
        remaining.remove(u)
    return tw_ub


def analyse(name: str, T: Matrix) -> dict:
    n = len(T)
    edges = flex_graph_edges(T)
    tw_ub = min_degree_treewidth_heuristic(n, edges)
    return {
        "name": name,
        "n": n,
        "n_flex_edges": len(edges),
        "min_degree_tw_upper_bound": tw_ub,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-k", type=int, default=4)
    args = parser.parse_args()
    out: list[dict] = []
    for k in range(1, args.max_k + 1):
        out.append(analyse(f"toggle_k={k}", toggle_tournament(k)))
    for k in range(1, args.max_k + 1):
        out.append(analyse(f"chain_seeded_k={k}", chain_seeded_toggle_tournament(k)))
    for name, T in SKEW_TEMPLATES.items():
        out.append(analyse(name, T))
    print(json.dumps(out, indent=2, default=list))


if __name__ == "__main__":
    main()
