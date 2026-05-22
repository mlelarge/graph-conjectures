"""Formal Path-FAS helpers.

The exact connected-path back-arc condition is too strong for Problem 4.4.
If F is a path-shaped FAS and P is a topological order of T-F, then the
back-arc graph B_P(T) is only a subgraph of that path. Conversely, any
linear-forest back-arc graph can be completed to an actual path by adding
extra arcs to the FAS; deleting additional arcs preserves acyclicity.

Thus formal Path-FAS is exactly the existence of an order whose back-arc
graph is a linear forest.
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict, deque
from itertools import permutations
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import classify, verify  # noqa: E402


def _arc_of(T: Sequence[Sequence[int]], a: int, b: int) -> tuple[int, int]:
    if T[a][b]:
        return (a, b)
    return (b, a)


def _path_components(arcs: list[tuple[int, int]]) -> list[list[int]]:
    """Return vertex sequences for the path components of a linear forest."""
    adj: dict[int, list[int]] = defaultdict(list)
    for u, v in arcs:
        adj[u].append(v)
        adj[v].append(u)

    seen: set[int] = set()
    comps: list[list[int]] = []
    for start in sorted(adj):
        if start in seen:
            continue
        vertices: list[int] = []
        q = deque([start])
        seen.add(start)
        while q:
            x = q.popleft()
            vertices.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    q.append(y)

        endpoints = [v for v in vertices if len(adj[v]) <= 1]
        head = min(endpoints) if endpoints else min(vertices)
        seq = [head]
        prev = None
        cur = head
        while True:
            nxts = [x for x in adj[cur] if x != prev]
            if not nxts:
                break
            nxt = min(nxts)
            seq.append(nxt)
            prev, cur = cur, nxt
        comps.append(seq)
    return comps


def complete_backarc_linear_forest_to_path_fas(
    T: Sequence[Sequence[int]],
    order: Sequence[int],
) -> list[tuple[int, int]]:
    """Return a path-shaped FAS extending the back-arcs of `order`.

    Raises ValueError if the order's back-arc graph is not a linear forest.
    The returned arcs include all back-arcs plus enough extra tournament arcs
    to make the underlying undirected graph a single path.
    """
    info = verify(T, order)
    if not info["is_linear_forest"]:
        raise ValueError("order does not have a linear-forest back-arc graph")

    back = list(info["arcs"])
    touched = {v for arc in back for v in arc}
    comps = _path_components(back)
    comps.extend([[v] for v in order if v not in touched])
    if len(comps) <= 1:
        return back

    completed = list(back)
    for left, right in zip(comps, comps[1:]):
        completed.append(_arc_of(T, left[-1], right[0]))
    return completed


def is_acyclic_after_deleting(
    T: Sequence[Sequence[int]],
    arcs_to_delete: Sequence[tuple[int, int]],
) -> bool:
    n = len(T)
    deleted = set(arcs_to_delete)
    indeg = [0] * n
    out: list[list[int]] = [[] for _ in range(n)]
    for u in range(n):
        for v in range(n):
            if T[u][v] and (u, v) not in deleted:
                out[u].append(v)
                indeg[v] += 1

    q = deque([v for v in range(n) if indeg[v] == 0])
    seen = 0
    while q:
        u = q.popleft()
        seen += 1
        for v in out[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return seen == n


def verify_path_fas_certificate(
    T: Sequence[Sequence[int]],
    arcs: Sequence[tuple[int, int]],
) -> bool:
    cls = classify(list(arcs))
    return cls["is_path"] and is_acyclic_after_deleting(T, arcs)


def decide_path_fas_bruteforce(T: Sequence[Sequence[int]]) -> dict:
    """Brute-force formal Path-FAS decider.

    This searches for an order whose back-arc graph is a linear forest and
    returns an explicit path-shaped FAS certificate.
    """
    for order in permutations(range(len(T))):
        info = verify(T, list(order))
        if info["is_linear_forest"]:
            F = complete_backarc_linear_forest_to_path_fas(T, list(order))
            return {
                "found": True,
                "order": list(order),
                "back_arcs": info["arcs"],
                "path_fas": F,
            }
    return {"found": False, "order": None, "back_arcs": None, "path_fas": None}


if __name__ == "__main__":
    import argparse
    import json

    p = argparse.ArgumentParser()
    p.add_argument("--T", required=True, help="Tournament as JSON matrix")
    args = p.parse_args()
    result = decide_path_fas_bruteforce(json.loads(args.T))
    print(json.dumps(result, indent=2))
