"""Bounded pricing oracle for basic Hurlbert tree-strategy column generation.

Given:

- a graph ``G`` (here ``L_fpy box L_fpy``);
- a root vertex ``root``;
- a dual vector ``y[v]`` for each non-root vertex (from the master LP);
- bounds: ``max_depth`` (depth of root-child below the root) and
  ``max_root_child_weight`` (the weight at the root-child, which must
  be a power of two).

This module enumerates *primitive* (= one-root-child) basic Hurlbert
tree strategies and finds one that minimises

    reduced_cost(T) = sum_v (1 - y_v) w_T(v).

A tree is *basic* if ``w(parent) = 2 w(child)`` for every non-root
non-root-neighbour vertex. Equivalently, every leaf has weight 1, and
every internal vertex has weight ``2 * max_child_weight``. We restrict
attention to **uniform-leaf-depth** trees (all leaves at the same
depth from the root), which gives ``w(v) = 2^{leaf_depth - depth(v)}``
where ``leaf_depth`` is the tree's depth.

The pricing problem is solved by branch-and-bound DFS over tree
shapes, with the following variables fixed at each node:

- the partial vertex set ``V(T)`` (a set of distinct vertices, all
  L_fpy-box-L_fpy-connected to one of root or another vertex in V(T));
- the parent-pointer ``parent[v]``;
- the depth ``depth[v]`` (1 for root-child, increasing downward);
- the running cost ``sum_v (1 - y_v) * 2^{leaf_depth - depth[v]}``.

We branch by:

1. extending an existing leaf (depth < ``leaf_depth``) with a new
   adjacent vertex at depth+1; or
2. declaring the current set complete and computing the final cost.

Pruning: at each node, a lower bound on the remaining reduction in
cost is the most-negative ``(1 - y_v)`` reachable times the remaining
weight budget; if even with that the running cost cannot improve on
the best-found, prune.

The output is at most ``top_k`` columns whose reduced cost is the
most negative (or all those with negative cost, up to a cap).
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

from sparse_columns import StrategyColumn


@dataclass
class PricingResult:
    columns: list[StrategyColumn]
    reduced_costs: list[Fraction]
    nodes_explored: int
    elapsed_s: float
    notes: str = ""


def _tree_to_column(
    leaf_depth: int,
    vertices: dict[int, int],  # vertex -> depth
    parent: dict[int, int],
    root: int,
    name_prefix: str = "priced",
) -> StrategyColumn:
    """Build a StrategyColumn from a basic uniform-leaf-depth tree."""
    weights: dict[int, Fraction] = {}
    for v, d in vertices.items():
        if v == root:
            continue
        weights[v] = Fraction(2 ** (leaf_depth - d))
    edges: list[tuple[int, int]] = []
    for v, p in parent.items():
        a, b = (v, p) if v < p else (p, v)
        edges.append((a, b))
    return StrategyColumn(
        weights=weights,
        tree_edges=edges,
        name=f"{name_prefix} depth={leaf_depth} |V|={len(vertices)-1}",
        basic=True,
        source="pricing oracle",
    )


def price_basic_trees(
    adj: list[list[int]],
    root: int,
    y: list[float],
    n_vertices: int,
    *,
    max_depth: int = 5,
    top_k: int = 8,
    require_negative_reduced_cost: bool = True,
    time_budget_s: float = 30.0,
    log: bool = False,
) -> PricingResult:
    """Branch-and-bound pricing for basic uniform-leaf-depth trees.

    ``y`` is the LP dual indexed over non-root vertices in increasing
    order. We expand it to ``y_full`` indexed by vertex.
    """
    y_full = [0.0] * n_vertices
    j = 0
    for v in range(n_vertices):
        if v == root:
            continue
        y_full[v] = y[j]
        j += 1

    # Pre-compute "(1 - y_v)" cost coefficients
    cost_coef = [1.0 - y_full[v] for v in range(n_vertices)]

    found: list[tuple[float, dict, dict, int]] = []  # (cost, vertices, parent, leaf_depth)
    nodes_explored = [0]
    start = time.monotonic()

    def add_candidate(cost: float, vertices: dict, parent: dict, leaf_depth: int):
        # Keep top_k by smallest (most negative) cost
        if require_negative_reduced_cost and cost >= 0:
            return
        # store a snapshot
        found.append((cost, dict(vertices), dict(parent), leaf_depth))
        # prune to top_k: keep most negative
        found.sort(key=lambda x: x[0])
        del found[top_k:]

    def dfs(
        leaf_depth: int,
        vertices: dict[int, int],   # vertex -> current depth
        parent: dict[int, int],     # vertex -> parent vertex
        partial_cost: float,        # sum (1 - y_v) * 2^{leaf_depth - depth_v}
        active: set[int],           # vertices that may still be extended
    ) -> None:
        nodes_explored[0] += 1
        if time.monotonic() - start > time_budget_s:
            return

        # Always allow finalizing here (declare current shape as the
        # tree). We require at least one vertex past the root.
        if vertices:
            add_candidate(partial_cost, vertices, parent, leaf_depth)

        # Try extensions: pick an active vertex v at depth d < leaf_depth,
        # add an adjacent vertex c not yet in V(T), c != root.
        for v in list(active):
            d = vertices[v]
            if d >= leaf_depth:
                continue
            new_d = d + 1
            inc_w = 2 ** (leaf_depth - new_d)
            for c in adj[v]:
                if c == root:
                    continue
                if c in vertices:
                    continue
                cost_inc = cost_coef[c] * inc_w
                # branch
                vertices[c] = new_d
                parent[c] = v
                # Even if v was leaf-eligible at depth = leaf_depth, this
                # extension uses depth new_d <= leaf_depth.
                # active set: v stays (could have more children); c added if d+1 < leaf_depth
                if new_d < leaf_depth:
                    active.add(c)
                dfs(
                    leaf_depth,
                    vertices,
                    parent,
                    partial_cost + cost_inc,
                    active,
                )
                # undo
                if new_d < leaf_depth and c in active:
                    active.discard(c)
                del vertices[c]
                del parent[c]

    # Outer loop over leaf_depth in 1..max_depth
    for leaf_depth in range(1, max_depth + 1):
        # Try every root-child (= L_fpy_box neighbour of root).
        for u in adj[root]:
            inc_w = 2 ** (leaf_depth - 1)
            cost_u = cost_coef[u] * inc_w
            vertices = {u: 1}
            parent = {u: root}
            active = {u} if leaf_depth > 1 else set()
            dfs(leaf_depth, vertices, parent, cost_u, active)

    elapsed = time.monotonic() - start
    columns: list[StrategyColumn] = []
    reduced: list[Fraction] = []
    for cost, vertices, par, leaf_depth in found:
        col = _tree_to_column(leaf_depth, vertices, par, root)
        columns.append(col)
        reduced.append(Fraction(int(round(cost * 10**12)), 10**12))
    return PricingResult(
        columns=columns,
        reduced_costs=reduced,
        nodes_explored=nodes_explored[0],
        elapsed_s=elapsed,
        notes=f"max_depth={max_depth}, top_k={top_k}, time_budget_s={time_budget_s}",
    )
