"""Pruned exact solver for linear-forest orderings.

The brute-force solver checks all n! orders and only classifies the
back-arc graph at the end. This solver builds an order from left to right.
When a vertex x is appended after the current prefix P, the newly decided
back-arcs are exactly the arcs x -> p with p in P. Those edges are added
to the undirected back-arc graph.

If a partial graph already has degree > 2 or an undirected cycle, no
completion can repair it. This gives a small but very effective exact
backtracking solver for the n=8/n=9 obstruction work.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Sequence


def _find(parent: list[int], x: int) -> int:
    while parent[x] != x:
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


def find_lfo_order(T: Sequence[Sequence[int]]) -> dict:
    """Return an LFO order if one exists.

    Output:
      - found: bool
      - order: list[int] | None
      - nodes: number of search nodes explored
      - pruned_degree: branches killed by degree > 2
      - pruned_cycle: branches killed by an undirected cycle
    """
    n = len(T)
    outmask = [
        sum((1 << v) for v in range(n) if T[u][v])
        for u in range(n)
    ]
    stats = {"nodes": 0, "pruned_degree": 0, "pruned_cycle": 0}

    def rec(
        prefix_mask: int,
        remaining_mask: int,
        degree: tuple[int, ...],
        parent: tuple[int, ...],
        order: tuple[int, ...],
    ) -> tuple[int, ...] | None:
        stats["nodes"] += 1
        if not remaining_mask:
            return order

        # Fail-fast heuristic: try vertices that add many immediate
        # back-arcs first. They are more likely to violate degree/cycle
        # constraints early.
        candidates = sorted(
            _iter_bits(remaining_mask),
            key=lambda x: (outmask[x] & prefix_mask).bit_count(),
            reverse=True,
        )
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
                prefix_mask | (1 << x),
                remaining_mask ^ (1 << x),
                tuple(deg),
                tuple(par),
                order + (x,),
            )
            if out is not None:
                return out
        return None

    order = rec(0, (1 << n) - 1, tuple([0] * n), tuple(range(n)), tuple())
    return {
        "found": order is not None,
        "order": list(order) if order is not None else None,
        **stats,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--T", required=True, help="Tournament as a JSON matrix")
    args = p.parse_args()
    print(json.dumps(find_lfo_order(json.loads(args.T)), indent=2))


if __name__ == "__main__":
    main()
