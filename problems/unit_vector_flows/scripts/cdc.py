"""Small CDC/H4-flow utilities for the unit-vector-flow project.

This module is intentionally narrow.  Its first job is negative
calibration: an oriented 4-cycle double cover gives an H4-flow, and on
a cubic graph any H4-flow induces a nowhere-zero Z_2^2-flow.  Therefore
the plain oriented-4-CDC route cannot prove anything about genuine
snarks.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable

import networkx as nx

from witness import orient


Z2_LABELS = (0, 1, 2, 3)


def _edge(u, v) -> tuple:
    return tuple(sorted((u, v)))


def _canonical_cycle(cycle: list) -> tuple:
    """Canonical rotation/reversal of an undirected simple cycle."""
    c = list(cycle)
    n = len(c)
    rots = []
    for seq in (c, list(reversed(c))):
        for i in range(n):
            rots.append(tuple(seq[i:] + seq[:i]))
    return min(rots)


def simple_cycles_undirected(G: nx.Graph, *, max_cycle_length: int | None = None) -> list[list]:
    """Enumerate undirected simple cycles, deduplicated up to rotation/reversal.

    This is intentionally a small-graph helper for CDC experiments, not a
    high-performance cycle enumerator.
    """
    D = nx.DiGraph()
    D.add_nodes_from(G.nodes())
    for u, v in G.edges():
        D.add_edge(u, v)
        D.add_edge(v, u)
    kwargs = {}
    if max_cycle_length is not None:
        # NetworkX 3.x supports length_bound; fall back below if not.
        kwargs["length_bound"] = max_cycle_length
    seen: set[tuple] = set()
    try:
        raw_iter = nx.simple_cycles(D, **kwargs)
    except TypeError:
        raw_iter = nx.simple_cycles(D)
    for cyc in raw_iter:
        if len(cyc) < 3:
            continue
        if max_cycle_length is not None and len(cyc) > max_cycle_length:
            continue
        key = _canonical_cycle(cyc)
        seen.add(key)
    return [list(c) for c in sorted(seen, key=lambda x: (len(x), x))]


def _cycle_edge_indices(cycle: list, edge_index: dict[tuple, int]) -> tuple[int, ...]:
    out = []
    for u, v in zip(cycle, cycle[1:] + cycle[:1]):
        out.append(edge_index[_edge(u, v)])
    return tuple(sorted(out))


def cdc_summary(cdc: list[list], G: nx.Graph) -> dict:
    """Summarise edge coverage of a candidate cycle double cover."""
    edges, _ = orient(G)
    counts = {e: 0 for e in edges}
    bad_edges = []
    for cyc in cdc:
        for u, v in zip(cyc, cyc[1:] + cyc[:1]):
            e = _edge(u, v)
            if e not in counts:
                bad_edges.append(e)
            else:
                counts[e] += 1
    return {
        "n_cycles": len(cdc),
        "edge_counts": {str(k): v for k, v in counts.items()},
        "bad_edges": [str(e) for e in bad_edges],
        "all_edges_covered_twice": (not bad_edges) and all(v == 2 for v in counts.values()),
    }


def iter_cdcs(
    G: nx.Graph,
    *,
    max_cycle_length: int | None = None,
    time_budget_s: float | None = None,
    max_solutions: int | None = None,
):
    """Yield CDCs found by backtracking over simple cycles.

    Designed for Petersen/Blanusa/flower-smoke experiments.  It is not a
    generic high-order CDC engine.
    """
    t0 = time.time()
    edges, _ = orient(G)
    edge_index = {e: i for i, e in enumerate(edges)}
    cycles = simple_cycles_undirected(G, max_cycle_length=max_cycle_length)
    masks = [_cycle_edge_indices(c, edge_index) for c in cycles]
    by_edge: list[list[int]] = [[] for _ in edges]
    for i, mask in enumerate(masks):
        for e in mask:
            by_edge[e].append(i)

    counts = [0] * len(edges)
    chosen: list[int] = []
    used = [False] * len(cycles)
    yielded: set[tuple[int, ...]] = set()
    n_yielded = 0

    def expired() -> bool:
        return time_budget_s is not None and (time.time() - t0) > time_budget_s

    def backtrack():
        nonlocal n_yielded
        if expired():
            return
        if max_solutions is not None and n_yielded >= max_solutions:
            return
        if all(c == 2 for c in counts):
            key = tuple(sorted(chosen))
            if key not in yielded:
                yielded.add(key)
                n_yielded += 1
                yield [cycles[i] for i in key]
            return

        # Pick the most constrained edge whose current coverage is too low.
        targets = [i for i, c in enumerate(counts) if c < 2]
        e = min(targets, key=lambda idx: sum(not used[c] for c in by_edge[idx]))
        for ci in by_edge[e]:
            if used[ci]:
                continue
            mask = masks[ci]
            if any(counts[j] >= 2 for j in mask):
                continue
            used[ci] = True
            chosen.append(ci)
            for j in mask:
                counts[j] += 1
            yield from backtrack()
            for j in mask:
                counts[j] -= 1
            chosen.pop()
            used[ci] = False

    yield from backtrack()


def find_cdc(
    G: nx.Graph,
    *,
    max_cycle_length: int | None = None,
    time_budget_s: float | None = None,
) -> list[list] | None:
    """Return the first CDC found, or ``None``."""
    return next(
        iter_cdcs(G, max_cycle_length=max_cycle_length, time_budget_s=time_budget_s, max_solutions=1),
        None,
    )


def orient_cdc(cdc: list[list], G: nx.Graph) -> list[list] | None:
    """Orient an undirected CDC so the two uses of every edge cancel.

    Returns directed cycles as vertex lists, or ``None`` if no such
    orientation exists.
    """
    edges, _ = orient(G)
    edge_index = {e: i for i, e in enumerate(edges)}
    uses: list[list[tuple[int, int]]] = [[] for _ in edges]
    for i, cyc in enumerate(cdc):
        for u, v in zip(cyc, cyc[1:] + cyc[:1]):
            e = _edge(u, v)
            if e not in edge_index:
                return None
            a, b = edges[edge_index[e]]
            direction = +1 if (u, v) == (a, b) else -1
            uses[edge_index[e]].append((i, direction))
    if any(len(u) != 2 for u in uses):
        return None

    # orient_sign[i] = +1 means keep cycle as listed, -1 reverse it.
    orient_sign: dict[int, int] = {}
    constraints: list[list[tuple[int, int]]] = [[] for _ in cdc]
    for edge_uses in uses:
        (i, di), (j, dj) = edge_uses
        # Need si*di = -sj*dj, hence sj = (-di/dj) si.
        ratio = -di * dj
        constraints[i].append((j, ratio))
        constraints[j].append((i, ratio))

    for start in range(len(cdc)):
        if start in orient_sign:
            continue
        orient_sign[start] = +1
        stack = [start]
        while stack:
            i = stack.pop()
            for j, ratio in constraints[i]:
                want = orient_sign[i] * ratio
                if j in orient_sign:
                    if orient_sign[j] != want:
                        return None
                else:
                    orient_sign[j] = want
                    stack.append(j)

    out = []
    for i, cyc in enumerate(cdc):
        out.append(list(cyc) if orient_sign[i] == +1 else list(reversed(cyc)))
    return out


def find_oriented_cdc(
    G: nx.Graph,
    *,
    max_cycle_length: int | None = None,
    time_budget_s: float | None = None,
    max_cdcs_to_check: int | None = None,
) -> list[list] | None:
    """Search for an orientable CDC and return directed cycles if found."""
    for cdc in iter_cdcs(
        G,
        max_cycle_length=max_cycle_length,
        time_budget_s=time_budget_s,
        max_solutions=max_cdcs_to_check,
    ):
        oriented = orient_cdc(cdc, G)
        if oriented is not None:
            return oriented
    return None


@dataclass(frozen=True)
class H4Certificate:
    """H4-flow values on the canonical edge orientation.

    For edge ``edges[k]``, ``values[k] = (i, j)`` means the H4 value
    ``e_i - e_j`` on that canonical orientation.
    """

    edges: list[tuple]
    values: list[tuple[int, int]]


def _h4_vector(pair: tuple[int, int]) -> tuple[int, int, int, int]:
    i, j = pair
    if i == j or i not in Z2_LABELS or j not in Z2_LABELS:
        raise ValueError(f"not an H4 value: {pair!r}")
    out = [0, 0, 0, 0]
    out[i] += 1
    out[j] -= 1
    return tuple(out)


def verify_h4_flow(G: nx.Graph, cert: H4Certificate) -> dict:
    """Check that ``cert`` is an H4-flow on ``G``.

    The check is over integers: each edge value is one of ``e_i-e_j``
    and the signed sum at each vertex is zero in ``Z^4``.
    """
    edges, sign = orient(G)
    if [tuple(e) for e in cert.edges] != edges:
        return {"ok": False, "reason": "edge order does not match canonical orientation"}
    if len(cert.values) != len(edges):
        return {"ok": False, "reason": "wrong number of H4 values"}

    try:
        vecs = [_h4_vector(tuple(v)) for v in cert.values]
    except ValueError as exc:
        return {"ok": False, "reason": str(exc)}

    max_abs = 0
    for terms in sign.values():
        s = [0, 0, 0, 0]
        for k, sigma in terms:
            sig = int(sigma)
            for i in range(4):
                s[i] += sig * vecs[k][i]
        max_abs = max(max_abs, max(abs(x) for x in s))
        if any(s):
            return {"ok": False, "reason": "Kirchhoff failure", "residual": s}
    return {"ok": True, "max_abs_residual": max_abs}


def h4_flow_to_z2x2_values(cert: H4Certificate) -> list[int]:
    """Map H4 values to nonzero Z_2^2 values.

    Identify the four H4 coordinate labels with the four elements of
    Z_2^2, encoded as ``0,1,2,3`` with xor as addition.  The H4 value
    ``e_i-e_j`` maps to ``i xor j``.  Since ``i != j``, every edge gets
    a nonzero value.
    """
    return [int(i) ^ int(j) for i, j in cert.values]


def verify_z2x2_flow(G: nx.Graph, edges: list[tuple], values: Iterable[int]) -> dict:
    """Verify a nowhere-zero Z_2^2-flow on a graph.

    In characteristic two, edge orientation is irrelevant: Kirchhoff at
    a vertex is xor of incident edge values.
    """
    canonical_edges, sign = orient(G)
    if [tuple(e) for e in edges] != canonical_edges:
        return {"ok": False, "reason": "edge order does not match canonical orientation"}
    vals = [int(v) for v in values]
    if len(vals) != len(canonical_edges):
        return {"ok": False, "reason": "wrong number of Z2x2 values"}
    if any(v not in (1, 2, 3) for v in vals):
        return {"ok": False, "reason": "zero or invalid edge value"}

    for terms in sign.values():
        acc = 0
        for k, _sigma in terms:
            acc ^= vals[k]
        if acc != 0:
            return {"ok": False, "reason": "Kirchhoff failure", "residual": acc}
    return {"ok": True}


def h4_flow_induces_nz4_flow(G: nx.Graph, cert: H4Certificate) -> dict:
    """Verify the implication H4-flow => nowhere-zero 4-flow.

    This is the computational form of the obstruction: if a cubic snark
    had an oriented 4-CDC, it would have an H4-flow and hence this
    induced nowhere-zero 4-flow, contradiction.
    """
    h4 = verify_h4_flow(G, cert)
    if not h4["ok"]:
        return {"ok": False, "reason": "not an H4-flow", "details": h4}
    zvals = h4_flow_to_z2x2_values(cert)
    z2 = verify_z2x2_flow(G, cert.edges, zvals)
    return {"ok": z2["ok"], "h4": h4, "z2x2": z2, "z2x2_values": zvals}


def h4_certificate_from_directed_4cdc(
    G: nx.Graph,
    cycles: list[list],
) -> H4Certificate:
    """Convert four directed cycles into an H4 certificate.

    Each cycle is given as a cyclic list of vertices.  The function
    requires exactly four cycles.  On every edge, exactly two cycles
    must appear and they must traverse the edge in opposite directions.
    """
    if len(cycles) != 4:
        raise ValueError("an oriented 4-CDC must have exactly four directed cycles")
    edges, _sign = orient(G)
    edge_index = {e: k for k, e in enumerate(edges)}
    seen: list[list[tuple[int, int]]] = [[] for _ in edges]

    for c_idx, cyc in enumerate(cycles):
        if len(cyc) < 2:
            raise ValueError(f"cycle {c_idx} is too short")
        for a, b in zip(cyc, cyc[1:] + cyc[:1]):
            e = tuple(sorted((a, b)))
            if e not in edge_index:
                raise ValueError(f"cycle {c_idx} uses non-edge {a!r}-{b!r}")
            k = edge_index[e]
            u, v = edges[k]
            direction = +1 if (a, b) == (u, v) else -1
            seen[k].append((c_idx, direction))

    values: list[tuple[int, int]] = []
    for k, uses in enumerate(seen):
        if len(uses) != 2:
            raise ValueError(f"edge {edges[k]} covered {len(uses)} times, expected 2")
        (i, di), (j, dj) = uses
        if di == dj:
            raise ValueError(f"edge {edges[k]} is not oppositely oriented")
        if di == +1:
            values.append((i, j))
        else:
            values.append((j, i))
    return H4Certificate(edges=edges, values=values)
