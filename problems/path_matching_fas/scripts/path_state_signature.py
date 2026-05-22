"""Finite signature checks for path-state gadgets.

The AAL forest-FAS reduction uses high-degree stars to encode the two
truth states. For the path/LFO case, a replacement block must keep the
backedge graph a linear forest while exposing ports that can be linked to
other gadgets. This script records the first exact two-state block found
by random search and provides a reusable signature enumerator.
"""
from __future__ import annotations

import argparse
import random
from itertools import permutations
from typing import Sequence


Matrix = list[list[int]]
Order = tuple[int, ...]
Arc = tuple[int, int]


# Labels:
#   0 = x       control vertex
#   1 = l       anchor/comparison vertex
#   2,3 = N     false-state port pair
#   4,5 = Y     true-state port pair
#   6 = q       auxiliary vertex
#
# Exhaustive check: exactly two LFO orders. In the L state (x before l),
# Y={4,5} are endpoints of the unique path component. In the R state
# (l before x), N={2,3} are endpoints of one path component.
TWO_STATE_PORT_BLOCK: Matrix = [
    [0, 1, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 1, 1, 0],
    [1, 0, 0, 1, 0, 0, 1],
    [1, 1, 0, 0, 0, 0, 0],
    [1, 0, 1, 1, 0, 1, 0],
    [0, 0, 1, 1, 0, 0, 1],
    [1, 1, 0, 1, 1, 0, 0],
]

LABELS = ("x", "l", "n1", "n2", "y1", "y2", "q")
N_PORTS = (2, 3)
Y_PORTS = (4, 5)


def _validate_tournament(T: Sequence[Sequence[int]]) -> None:
    n = len(T)
    for row in T:
        if len(row) != n:
            raise ValueError("T must be square")
    for u in range(n):
        if T[u][u] != 0:
            raise ValueError("diagonal entries must be zero")
        for v in range(u + 1, n):
            if T[u][v] not in (0, 1) or T[v][u] not in (0, 1):
                raise ValueError("T entries must be 0/1")
            if T[u][v] + T[v][u] != 1:
                raise ValueError("T must orient every unordered pair once")


def _find(parent: list[int], x: int) -> int:
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def lfo_signature(T: Sequence[Sequence[int]], order: Sequence[int]) -> dict | None:
    """Return the LFO signature for `order`, or None if it is not an LFO."""
    n = len(T)
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i

    arcs: list[Arc] = []
    degree = [0] * n
    adj = [[] for _ in range(n)]
    for u in range(n):
        for v in range(n):
            if T[u][v] and pos[v] < pos[u]:
                arcs.append((u, v))
                degree[u] += 1
                degree[v] += 1
                adj[u].append(v)
                adj[v].append(u)

    if max(degree) > 2:
        return None

    parent = list(range(n))
    for u, v in arcs:
        ru = _find(parent, u)
        rv = _find(parent, v)
        if ru == rv:
            return None
        parent[ru] = rv

    seen: set[int] = set()
    components: list[list[int]] = []
    component_id: dict[int, int] = {}
    for start in range(n):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        comp: list[int] = []
        while stack:
            u = stack.pop()
            component_id[u] = len(components)
            comp.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        components.append(sorted(comp))

    return {
        "order": tuple(order),
        "state": "L" if pos[0] < pos[1] else "R",
        "arcs": tuple(arcs),
        "degree": tuple(degree),
        "components": tuple(tuple(c) for c in components),
        "component_id": component_id,
    }


def enumerate_lfo_signatures(T: Sequence[Sequence[int]]) -> list[dict]:
    _validate_tournament(T)
    out = []
    for order in permutations(range(len(T))):
        sig = lfo_signature(T, order)
        if sig is not None:
            out.append(sig)
    return out


def _iter_bits(mask: int):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def _signature_from_arcs(
    n: int,
    order: tuple[int, ...],
    arcs: tuple[Arc, ...],
    degree: tuple[int, ...],
) -> dict:
    adj = [[] for _ in range(n)]
    for u, v in arcs:
        adj[u].append(v)
        adj[v].append(u)

    seen: set[int] = set()
    components: list[list[int]] = []
    component_id: dict[int, int] = {}
    for start in range(n):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        comp: list[int] = []
        while stack:
            u = stack.pop()
            component_id[u] = len(components)
            comp.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        components.append(sorted(comp))

    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i
    return {
        "order": order,
        "state": "L" if pos[0] < pos[1] else "R",
        "arcs": arcs,
        "degree": degree,
        "components": tuple(tuple(c) for c in components),
        "component_id": component_id,
    }


def enumerate_lfo_signatures_pruned(
    T: Sequence[Sequence[int]],
    limit: int | None = None,
) -> list[dict]:
    """Enumerate LFO signatures with prefix pruning.

    This uses the same monotonicity as `lfo_backtrack`: once a partial
    order has a degree-3 vertex or an undirected cycle in its decided
    backedge graph, no completion can become an LFO.
    """
    _validate_tournament(T)
    n = len(T)
    outmask = [
        sum((1 << v) for v in range(n) if T[u][v])
        for u in range(n)
    ]
    out: list[dict] = []

    def find(parent: list[int], x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(parent: list[int], a: int, b: int) -> None:
        ra = find(parent, a)
        rb = find(parent, b)
        if ra != rb:
            parent[rb] = ra

    def rec(
        prefix_mask: int,
        remaining_mask: int,
        degree: tuple[int, ...],
        parent: tuple[int, ...],
        order: tuple[int, ...],
        arcs: tuple[Arc, ...],
    ) -> None:
        if limit is not None and len(out) >= limit:
            return
        if not remaining_mask:
            out.append(_signature_from_arcs(n, order, arcs, degree))
            return

        candidates = sorted(
            _iter_bits(remaining_mask),
            key=lambda x: (outmask[x] & prefix_mask).bit_count(),
            reverse=True,
        )
        for x in candidates:
            deg = list(degree)
            par = list(parent)
            new_arcs = list(arcs)
            ok = True
            for p in _iter_bits(outmask[x] & prefix_mask):
                if deg[x] >= 2 or deg[p] >= 2:
                    ok = False
                    break
                if find(par, x) == find(par, p):
                    ok = False
                    break
                deg[x] += 1
                deg[p] += 1
                union(par, x, p)
                new_arcs.append((x, p))
            if not ok:
                continue
            rec(
                prefix_mask | (1 << x),
                remaining_mask ^ (1 << x),
                tuple(deg),
                tuple(par),
                order + (x,),
                tuple(new_arcs),
            )

    rec(0, (1 << n) - 1, tuple([0] * n), tuple(range(n)), tuple(), tuple())
    return out


def pair_is_endpoint_pair(sig: dict, pair: tuple[int, int]) -> bool:
    a, b = pair
    return (
        sig["component_id"][a] == sig["component_id"][b]
        and sig["degree"][a] <= 1
        and sig["degree"][b] <= 1
    )


def pair_has_spare_capacity(sig: dict, pair: tuple[int, int]) -> bool:
    a, b = pair
    return sig["degree"][a] <= 1 and sig["degree"][b] <= 1


def summarize_two_state_port_block() -> dict:
    sigs = enumerate_lfo_signatures_pruned(TWO_STATE_PORT_BLOCK)
    by_state = {sig["state"]: sig for sig in sigs}
    return {
        "lfo_order_count": len(sigs),
        "states": tuple(sig["state"] for sig in sigs),
        "orders": tuple(sig["order"] for sig in sigs),
        "left_y_endpoint_pair": pair_is_endpoint_pair(by_state["L"], Y_PORTS),
        "right_n_endpoint_pair": pair_is_endpoint_pair(by_state["R"], N_PORTS),
        "left_n_spare_capacity": pair_has_spare_capacity(by_state["L"], N_PORTS),
        "right_y_spare_capacity": pair_has_spare_capacity(by_state["R"], Y_PORTS),
        "signatures": sigs,
    }


def random_tournament(n: int, rng: random.Random) -> Matrix:
    T = [[0] * n for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            if rng.randrange(2):
                T[v][u] = 1
            else:
                T[u][v] = 1
    return T


def random_search(
    n: int,
    samples: int,
    seed: int,
    require_inactive_spare: bool,
) -> dict | None:
    """Search for two-state port blocks with the fixed label convention."""
    rng = random.Random(seed)
    best: dict | None = None
    for sample in range(samples):
        T = random_tournament(n, rng)
        sigs = enumerate_lfo_signatures_pruned(T, limit=3)
        if best is None or len(sigs) < best["lfo_order_count"]:
            best = {"sample": sample, "lfo_order_count": len(sigs), "T": T}
        if len(sigs) != 2:
            continue
        states = sorted(sig["state"] for sig in sigs)
        if states != ["L", "R"]:
            continue
        by_state = {sig["state"]: sig for sig in sigs}
        good = (
            pair_is_endpoint_pair(by_state["L"], Y_PORTS)
            and pair_is_endpoint_pair(by_state["R"], N_PORTS)
        )
        if require_inactive_spare:
            good = (
                good
                and pair_has_spare_capacity(by_state["L"], N_PORTS)
                and pair_has_spare_capacity(by_state["R"], Y_PORTS)
            )
        if good:
            return {
                "sample": sample,
                "T": T,
                "signatures": sigs,
                "inactive_spare_required": require_inactive_spare,
            }
    return {
        "sample": None,
        "best": best,
        "inactive_spare_required": require_inactive_spare,
    }


def extend_known_block_search(extra_vertices: int, max_masks: int | None = None) -> dict:
    """Exhaustively extend the recorded 7-vertex block by new auxiliaries.

    The old block remains induced. All orientations involving the new
    vertices are enumerated. `extra_vertices=1` has 2^7 cases; `extra=2`
    has 2^15 cases and is the meaningful local-repair exhaustion recorded
    in `docs/hardness_route.md`.
    """
    old_n = len(TWO_STATE_PORT_BLOCK)
    n = old_n + extra_vertices
    variable_edges: list[tuple[int, int]] = []
    for j in range(old_n, n):
        for i in range(j):
            variable_edges.append((i, j))

    total_masks = 1 << len(variable_edges)
    if max_masks is not None:
        total_masks = min(total_masks, max_masks)

    exact_two = 0
    active_port_candidates = 0
    best: dict | None = None
    for mask in range(total_masks):
        T = [[0] * n for _ in range(n)]
        for i in range(old_n):
            for j in range(old_n):
                T[i][j] = TWO_STATE_PORT_BLOCK[i][j]
        for bit, (i, j) in enumerate(variable_edges):
            if (mask >> bit) & 1:
                T[j][i] = 1
            else:
                T[i][j] = 1

        sigs = enumerate_lfo_signatures_pruned(T, limit=3)
        if best is None or len(sigs) < best["lfo_order_count"]:
            best = {"mask": mask, "lfo_order_count": len(sigs), "T": T}
        if len(sigs) != 2:
            continue
        exact_two += 1
        states = sorted(sig["state"] for sig in sigs)
        if states != ["L", "R"]:
            continue
        by_state = {sig["state"]: sig for sig in sigs}
        if not (
            pair_is_endpoint_pair(by_state["L"], Y_PORTS)
            and pair_is_endpoint_pair(by_state["R"], N_PORTS)
        ):
            continue
        active_port_candidates += 1
        if (
            pair_has_spare_capacity(by_state["L"], N_PORTS)
            and pair_has_spare_capacity(by_state["R"], Y_PORTS)
        ):
            return {
                "found": True,
                "extra_vertices": extra_vertices,
                "mask": mask,
                "T": T,
                "signatures": sigs,
                "checked_masks": mask + 1,
                "total_masks": total_masks,
                "exact_two_state_extensions": exact_two,
                "active_port_candidates": active_port_candidates,
            }

    return {
        "found": False,
        "extra_vertices": extra_vertices,
        "checked_masks": total_masks,
        "total_masks": 1 << len(variable_edges),
        "variable_edges": variable_edges,
        "exact_two_state_extensions": exact_two,
        "active_port_candidates": active_port_candidates,
        "best": best,
    }


def _compact_signature(sig: dict) -> dict:
    return {
        "state": sig["state"],
        "order": tuple(LABELS[v] for v in sig["order"]),
        "arcs": tuple((LABELS[u], LABELS[v]) for u, v in sig["arcs"]),
        "degree": dict(zip(LABELS, sig["degree"])),
        "components": tuple(tuple(LABELS[v] for v in c) for c in sig["components"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search", action="store_true")
    parser.add_argument("--extend-known", action="store_true")
    parser.add_argument("--n", type=int, default=7)
    parser.add_argument("--samples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260522)
    parser.add_argument("--require-inactive-spare", action="store_true")
    parser.add_argument("--extra-vertices", type=int, default=1)
    parser.add_argument("--max-masks", type=int, default=None)
    args = parser.parse_args()

    if args.extend_known:
        print(extend_known_block_search(args.extra_vertices, args.max_masks))
        return

    if args.search:
        print(random_search(
            args.n,
            args.samples,
            args.seed,
            args.require_inactive_spare,
        ))
        return

    summary = summarize_two_state_port_block()
    print({
        k: v for k, v in summary.items()
        if k != "signatures"
    })
    for sig in summary["signatures"]:
        print(_compact_signature(sig))


if __name__ == "__main__":
    main()
